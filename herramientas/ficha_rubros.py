"""Ficha por rubro y modo Detallado / Global de la MO y los servicios (pedido de Matías, 28-10-2026).

Uso: python herramientas/ficha_rubros.py cotizaciones/<carpeta>                    → ficha_rubros.md y ficha_rubros.json
     python herramientas/ficha_rubros.py cotizaciones/<carpeta> --global <rubro>   → pasa el rubro a global (cotizacion.json)
     python herramientas/ficha_rubros.py cotizaciones/<carpeta> --detallado <rubro> → vuelve al detalle guardado
     (la ficha la corre también armar_cotizacion.py al final)

Rubros: mo_piping (armado y soldadura del piping), mo_estructura (fabricación de la estructura), pintura, end (RX, LP y
procedimientos) y transporte. Todo POR EQUIPO; la cantidad multiplica al final, como el resto de la cotización.

- Detallado: como hasta ahora (soldadura junta por junta, m² × tarifa, placas de RX…).
- Global: un solo renglón por rubro con el precio del tercero (cantidad 1, unidad "gl", "rubro" y "global": true). Los
  renglones detallados del rubro se guardan en cotizacion.json → "rubros"[rubro]["detalle"] y vuelven si se pasa a
  detallado. El global arranca en 0 ("SIN PRECIO: pedir cotización", regla P4 ter) hasta cargar la cotización.
- La ficha junta los datos para pedir y controlar el global: soldaduras, pulgadas, kg de piping y de estructura, m², placas
  de RX, juntas con LP, procedimientos y, para el transporte, largo × ancho × alto, kg y equipos por camión. Al lado, lo
  que da el cálculo detallado y el precio del global por kg, pulgada, m², junta o viaje.
El motor, la planilla y el informe no cambian: suman los renglones de "items" como siempre.
"""
import csv
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import precotizar  # noqa: E402
from catalogo_materiales import atributos, expandir, familia_de  # noqa: E402
from controles_tablas import TEC, leer, leer_acc, peso_item  # noqa: E402
from indice_proyectos import norm  # noqa: E402
from numeros import a_vista, fmt, fmtg, numero  # noqa: E402

RUBROS = {  # en el orden en que se muestran (pedido de Matías, 29-10-2026: un ítem por rubro de fabricación)
    "mo_estructura": ("Fabricación del skid (estructura)", "mo"),
    "mo_piping": ("Fabricación del piping", "mo"),
    "pintura": ("Granallado y pintura", "servicio"),
    "end": ("Radiografía y END", "servicio"),
    "procedimientos": ("Procedimientos", "servicio"),
    "ph": ("Prueba hidráulica", "servicio"),
    "horas": ("Horas de ITT (ingeniería, calidad y montaje)", "mo"),
    "transporte": ("Transporte", "servicio"),
}
# Semirremolque plano: caja útil 13,5 × 2,5 m, piso a 1,20 m, carga útil 27 t. Límites sin permiso (Ley 24.449): ancho 2,60 m,
# alto total 4,10 m. Más ancho o más alto: carga especial (permiso de Vialidad, escolta o carretón).
CAMION = {"largo": 13.5, "ancho": 2.5, "piso": 1.2, "kg": 27000}
LIMITE_ANCHO, LIMITE_ALTO = 2.60, 4.10
INSTRUMENTOS = r"termometro|manometro|instrumento|transmisor|bloqueo y purga|vaina|termopozo|indicador|presostato|switch|\b[pt][itwe]-\d"
ESTRUCTURA = r"estructura|perfileria|bastidor|\bskid\b|\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|angulo|planchuela"


def rubro_de(it):
    """Rubro de un renglón de MO o servicio, o None (caución, repuestos y otros quedan en "Otros servicios")."""
    if it.get("rubro"):
        return it["rubro"]
    if it["grupo"] == "material":
        return None
    t = norm(f"{it.get('pos', '')} {it['descripcion']}")
    if re.search(r"caucion|seguro|repuesto", t):
        return None
    if str(it.get("pos", "")).upper() == "PH" or re.search(r"^prueba hidraul", norm(it["descripcion"])):
        return "ph"
    if re.search(r"\bhoras?\b|ingenier|calidad", t):
        return "horas"
    if re.search(r"procedimiento|\bwps\b|\bpqr\b|\bwpq\b|calificacion de soldador", t):
        return "procedimientos"
    if re.search(r"granall|pintur|arenad|revestim", t):
        return "pintura"
    if re.search(r"radiograf|\brx\b|\blp\b|tintas|penetrant|ultrason|particulas|\bend\b|ensayo", t):
        return "end"
    if re.search(r"hidraul", t):
        return "ph"
    if re.search(r"flete|transporte|camion", t):
        return "transporte"
    if re.search(r"estructura|bastidor|perfileria|\bmoe\b", t):
        return "mo_estructura"
    if re.search(r"soldadur|armado|prefabricad|spool|ledesma|dimensional|piping", t):
        return "mo_piping"
    return None


def procedimientos(filas, esp, juntas_bw, juntas_sw, rx, m2):
    """Procedimientos que lleva el equipo, según materiales, juntas, END y pintura (misma regla en web/src/ficha.js)."""
    grupos = sorted({"inoxidable" if re.search(r"304|316|inox|cf8m", norm(f["material"])) else "acero al carbono"
                     for f in filas if f.get("material") and re.search(r"BW|SW", str(f.get("extremos", "")).upper())})
    esp_txt = f" hasta {n(esp)} mm de espesor" if esp else ""
    lista = []
    for g in grupos:
        if juntas_bw:
            lista.append({"codigo": "WPS-BW", "nombre": f"WPS/PQR de soldadura a tope, {g}", "alcance": esp_txt.strip(), "cantidad": 1, "tipo": "soldadura"})
        if juntas_sw:
            lista.append({"codigo": "WPS-SW", "nombre": f"WPS/PQR de soldadura socket y filete, {g}", "alcance": "", "cantidad": 1, "tipo": "soldadura"})
    if lista:
        lista.append({"codigo": "WPQ", "nombre": "Calificación de soldadores (WPQ)", "alcance": "una por WPS y soldador asignado", "cantidad": len(lista), "tipo": "soldadura"})
    if rx and juntas_bw:
        lista.append({"codigo": "END-RX", "nombre": "Procedimiento de radiografía (nivel 3, ISO 9712)", "alcance": "", "cantidad": 1, "tipo": "end"})
    if juntas_sw:
        lista.append({"codigo": "END-LP", "nombre": "Procedimiento de líquidos penetrantes (nivel 3, ISO 9712)", "alcance": "", "cantidad": 1, "tipo": "end"})
    if juntas_bw or juntas_sw:
        lista.append({"codigo": "PH", "nombre": "Procedimiento de prueba hidráulica", "alcance": "", "cantidad": 1, "tipo": "calidad"})
    if m2:
        lista.append({"codigo": "PIN", "nombre": "Procedimiento de granallado y pintura", "alcance": "esquema del pliego", "cantidad": 1, "tipo": "calidad"})
    return lista


def litros(cfg):
    """Volumen interior de los caños (litros por equipo), para la prueba hidráulica."""
    canos = leer(TEC / "canos_peso_superficie.csv")
    tot = 0.0
    for it in cfg["items"]:
        if it["grupo"] != "material" or norm(it["unidad"]) != "m":
            continue
        fam, at = fam_at(it)
        if fam != "CAN":
            continue
        dn, sch = precotizar.dn_de(at.get("diametro", "")), at.get("schedule", "")
        r = next((r for r in canos if dn and abs(float(r["dn_pulg"]) - dn) < 1e-6 and sch and (r["schedule"] == sch or r["clase"] == sch.upper())), None)
        if r:
            tot += float(r["litros_m_interior"]) * it["cantidad"]
    return round(tot, 1)


def modo(cfg, r):
    return (cfg.get("rubros") or {}).get(r, {}).get("modo", "detallado")


# ---------------------------------------------------------------- cambio de modo (lo mismo hace la página)
def pasar_a_global(cfg, r, hoy=None):
    if r not in RUBROS:
        raise SystemExit(f"Rubro desconocido: {r} (válidos: {', '.join(RUBROS)})")
    if modo(cfg, r) == "global":
        return None
    det = [it for it in cfg["items"] if rubro_de(it) == r and not it.get("global")]
    cfg["items"] = [it for it in cfg["items"] if it not in det]
    nombre, grupo = RUBROS[r]
    it = {"id": f"G-{r}", "pos": "GL", "grupo": grupo, "rubro": r, "global": True, "descripcion": f"{nombre} (global por equipo)",
          "especificacion": "Precio global del tercero: ver ficha_rubros.md", "cantidad": 1, "unidad": "gl",
          "fuentes": [{"tipo": "est", "precio": 0, "proveedor": "A cotizar: global del tercero", "origen": "ficha_rubros.md (pedir con la ficha)", "fecha": hoy or date.today().isoformat(), "coincide": "igual",
                       "diferencia": "SIN PRECIO: pedir cotización global con la ficha del rubro"}]}
    cfg["items"].append(it)
    cfg.setdefault("rubros", {})[r] = {**cfg.get("rubros", {}).get(r, {}), "modo": "global", "detalle": det}
    return it


def volver_a_detallado(cfg, r):
    if modo(cfg, r) != "global":
        return
    det = cfg["rubros"][r].get("detalle", [])
    cfg["items"] = [it for it in cfg["items"] if not (it.get("global") and it.get("rubro") == r)] + det
    cfg["rubros"][r] = {"modo": "detallado", **({"tarifa": cfg["rubros"][r]["tarifa"]} if cfg["rubros"][r].get("tarifa") else {})}


# ---------------------------------------------------------------- ficha
def filas_plano(carpeta, cfg):
    """Tabla del plano (pedido/lista_materiales_plano.csv) o, si no está, los datos del plano guardados en cada renglón."""
    p = carpeta / "pedido" / "lista_materiales_plano.csv"
    if p.exists():
        return list(csv.DictReader(open(p, encoding="utf-8")))
    filas = []
    for it in cfg["items"]:
        if it["grupo"] == "material":
            pl = it.get("plano") or {}
            if not (pl.get("extremos") or pl.get("diametro")):
                continue
            f = {"pos": str(it.get("pos", "")), "descripcion": pl.get("descripcion") or it["descripcion"], "diametro": pl.get("diametro", ""),
                 "serie_sch": pl.get("serie_sch", ""), "material": pl.get("material", ""), "extremos": pl.get("extremos", ""),
                 "cantidad": pl.get("cantidad", it["cantidad"]), "unidad": pl.get("unidad", it["unidad"])}
            if "extremos_campo" in pl:
                f["extremos_campo"] = pl["extremos_campo"]
            filas.append(f)
    return filas


def es_estructura(it):
    return it["grupo"] == "material" and bool(re.search(ESTRUCTURA, norm(it["descripcion"])))


def fam_at(it):
    """Familia y atributos de un renglón de material, como los lee controles_tablas.peso_item."""
    d = expandir(norm(it["descripcion"]))
    t = expandir(norm(f"{it['descripcion']} {it.get('especificacion', '')}"))
    fam = familia_de(d)
    fam = familia_de(t) if fam == "OTR" else fam
    return fam, {**atributos(t, fam), **atributos(d, fam)}


def pesos(cfg):
    """kg de piping (caños, bridas, accesorios y válvulas con tabla), m² de caños y niples, kg de estructura y lo que no tiene tabla."""
    canos, bridas, valv = (leer(TEC / f) for f in ("canos_peso_superficie.csv", "bridas_peso.csv", "valvulas_peso.csv"))
    acc = leer_acc()
    kg_p = m2_c = kg_e = 0.0
    sin, aprox = [], []
    for it in cfg["items"]:
        if it["grupo"] != "material":
            continue
        if es_estructura(it):
            u = norm(it["unidad"])
            if u == "kg":
                kg_e += it["cantidad"]
            else:
                pf = precotizar.perfil({"descripcion": it["descripcion"]})
                if pf and u.startswith("m"):
                    kg_e += pf[0] * it["cantidad"]
                else:
                    sin.append(f"{it['pos']} {it['descripcion'][:40]}")
            continue
        d = expandir(norm(it["descripcion"]))
        if str(it.get("pos", "")).upper() == "INS" or re.search(INSTRUMENTOS, d):
            continue  # instrumentos: peso despreciable, no se pesan (Matías, 29-10-2026)
        fam, at = fam_at(it)
        kg, m2, fuente = peso_item(it, at, fam, canos, bridas, acc, valv)
        if kg is not None and str(fuente).startswith("APROXIMADO"):
            aprox.append(f"{it['pos']} {it['descripcion'][:40]}")
        if kg is None:
            if not re.search(r"junta|termometro|manometro|instrumento|transmisor|bloqueo y purga|repuesto|completar barra", d):
                sin.append(f"{it['pos']} {it['descripcion'][:40]}")
            continue
        kg_p += kg * it["cantidad"]
        m2_c += (m2 or 0) * it["cantidad"]
    return kg_p, m2_c, kg_e, sin, aprox


def importe_items(items, cfg):
    """Costo por equipo de unos renglones, con el mismo ajuste por inflación que el motor."""
    import armar_cotizacion as ac
    idx, p = ac.leer_indices(cfg), cfg["parametros"]
    fref = p["fecha_referencia"][:7]
    return sum(it["cantidad"] * it["fuentes"][0]["precio"] * ac.factor(it, idx, fref, p["AJ"]) for it in items)


def transporte(cfg, kg_equipo):
    t = cfg.get("transporte") or {}
    L, A, H = (float(t.get(k) or 0) for k in ("largo_m", "ancho_m", "alto_m"))
    r = {"largo_m": L, "ancho_m": A, "alto_m": H, "kg_equipo": round(kg_equipo, 1), "destino": t.get("destino", ""),
         "por_camion": None, "viajes": None, "avisos": []}
    if not (L and A and H):
        r["avisos"].append("Faltan las medidas del equipo (largo × ancho × alto): cargarlas del plano de conjunto")
        return r
    if A > LIMITE_ANCHO and L > LIMITE_ANCHO:
        r["avisos"].append(f"Ancho {fmtg(A)} m: supera {fmtg(LIMITE_ANCHO)} m → carga especial (permiso de Vialidad y escolta)")
    if H + CAMION["piso"] > LIMITE_ALTO:
        r["avisos"].append(f"Alto cargado {fmt(H + CAMION['piso'], 2)} m (equipo {fmtg(H)} m + piso {fmtg(CAMION['piso'])} m): supera {fmtg(LIMITE_ALTO)} m → carretón o carga especial")
    if max(L, A) > CAMION["largo"]:
        r["avisos"].append(f"Largo {fmtg(max(L, A))} m: más que la caja de un semi ({fmtg(CAMION['largo'])} m) → carretón extensible")
    entra = lambda l, a: (math.floor(CAMION["largo"] / l) * math.floor(CAMION["ancho"] / a)) if l <= CAMION["largo"] and a <= CAMION["ancho"] else 0
    por_medida = max(entra(L, A), entra(A, L), 1)
    por_peso = math.floor(CAMION["kg"] / kg_equipo) if kg_equipo else por_medida
    n = max(1, min(por_medida, por_peso))
    N = cfg["parametros"]["N"]
    r.update(por_camion=n, viajes=math.ceil(N / n), por_medida=por_medida, por_peso=por_peso)
    return r


NO_VA_EN_EL_EQUIPO = r"completar|sobrante|compra minima|repuesto|junta|esparrago"


def peso_equipo(cfg):
    """Peso aproximado de un equipo para la planilla (kg y USD/kg, pedido de Matías 29-10-2026): piping con tabla,
    estructura, renglones cargados por kg y piezas que dicen su peso en la descripción ("(417 kg)"). No suma compras
    extra, repuestos, juntas ni instrumentos. Devuelve kg y la lista de renglones sin peso (el total es un mínimo)."""
    canos, bridas, valv = (leer(TEC / f) for f in ("canos_peso_superficie.csv", "bridas_peso.csv", "valvulas_peso.csv"))
    acc = leer_acc()
    kg, sin = 0.0, []
    for it in cfg["items"]:
        if it["grupo"] != "material":
            continue
        d, u = norm(it["descripcion"]), norm(it["unidad"])  # sin expandir: igual que la página (ficha.js)
        if re.search(NO_VA_EN_EL_EQUIPO, d) or str(it.get("pos", "")).upper() == "INS" or re.search(INSTRUMENTOS, d):
            continue
        if u == "kg":  # sin el recorte que se compra de más ("+ 10% recortes")
            rc = re.search(r"\+\s*(\d+)\s*% recortes", d)
            kg += it["cantidad"] / (1 + int(rc.group(1)) / 100) if rc else it["cantidad"]
            continue
        # con el lector único (numeros.py): "0,60 kg" son 0,6 y "1.250 kg" son 1250 (antes la coma se perdía: 18-11-2026)
        m = re.search(r"(\d[\d.,]*)\s*kg\b", f"{it['descripcion']} {it.get('especificacion', '')}")
        if m and numero(m.group(1)) is not None:
            kg += numero(m.group(1)) * it["cantidad"]
            continue
        if es_estructura(it):
            pf = precotizar.perfil({"descripcion": it["descripcion"]})
            if pf and u.startswith("m"):
                kg += pf[0] * it["cantidad"]
            else:
                sin.append(str(it["pos"]))
            continue
        fam, at = fam_at(it)
        if not at.get("serie"):  # "150 x STD" en la columna serie/sch del plano: la serie es el número de clase
            sp = re.search(r"Plano: [^·]*· ([^·]*)", it.get("especificacion", ""))
            cl = re.search(r"\b(150|300|400|600|900|1500|2500|2000|3000|6000|9000)\b", sp.group(1)) if sp else None
            if cl:
                at = {**at, "serie": cl.group(1)}
        k, _, _ = peso_item(it, at, fam, canos, bridas, acc, valv)
        if k is None:
            sin.append(str(it["pos"]))
        else:
            kg += k * it["cantidad"]
    return {"kg": round(kg, 1), "sin_peso": sin}


def armar(carpeta, cfg=None):
    carpeta = Path(carpeta)
    cfg = cfg or json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    filas = filas_plano(carpeta, cfg)
    sol = precotizar.soldaduras(filas) if filas else {"juntas_bw": 0, "pulg_eq": 0, "placas": [0, 0], "juntas_sw_olet": 0, "avisos": []}
    kg_p, m2_c, kg_e, sin, aprox = pesos(cfg)
    sup = dict(precotizar.superficie_pintura(filas, m2_c)) if filas else {}
    m2_est = sup.get("estructura") or kg_e * precotizar.M2_POR_KG_ESTRUCTURA
    m2_pip = m2_c + sup.get("bridas, accesorios y válvulas (largo equivalente)", 0) + sup.get("envolvente", 0)
    rx = cfg["parametros"].get("rx_pct", 0) or 0
    ch, gr = (math.ceil(x * rx / 100) for x in sol["placas"])
    campo = sum(float(f.get("extremos_campo") or 0) * float(f.get("cantidad") or 0) for f in filas)
    bridas = sum(it["cantidad"] for it in cfg["items"] if it["grupo"] == "material" and re.match(r"brida", norm(it["descripcion"])))
    dns = sorted({d for f in filas if "BW" in str(f.get("extremos", "")).upper() for d in [precotizar.dn_de(f["diametro"])] if d}, reverse=True)
    mats = sorted({f["material"] for f in filas if f.get("material") and "BW" in str(f.get("extremos", "")).upper()})
    tabla = leer(TEC / "factores_soldadura.csv")
    esp = max((float(r["espesor_mm"]) for f in filas if "BW" in str(f.get("extremos", "")).upper() for r in tabla
               if precotizar.dn_de(f["diametro"]) and abs(float(r["dn_pulg"]) - precotizar.dn_de(f["diametro"])) < 1e-6
               and precotizar.sch_de(f["serie_sch"]) and precotizar.sch_de(f["serie_sch"]) in (r["schedule"], r["clase"]) and r["espesor_mm"]), default=0)
    ficha = {
        "generada": date.today().isoformat(),
        "mo_piping": {"juntas_bw": sol["juntas_bw"], "pulg_eq": sol["pulg_eq"], "juntas_sw_olet": sol["juntas_sw_olet"], "extremos_campo": campo,
                      "kg_piping": round(kg_p, 1), "bridas": bridas, "diametros": dns, "sin_peso": sin, "aproximados": aprox, "avisos": sol.get("avisos", [])},
        "mo_estructura": {"kg": round(kg_e, 1), "m2": round(m2_est, 2)},
        "pintura": {"m2_canos": round(m2_c, 2), "m2_piping": round(m2_pip, 2), "m2_estructura": round(m2_est, 2), "m2_total": round(m2_pip + m2_est, 2),
                    "esquema": (cfg.get("pintura") or {}).get("esquema", "")},
        "end": {"juntas_bw": sol["juntas_bw"], "rx_pct": rx, "placas_chicas": ch, "placas_grandes": gr, "juntas_lp": sol["juntas_sw_olet"],
                "materiales": mats, "espesor_max_mm": esp,
                "procedimientos": [f"WPS/PQR de soldadura a tope para {', '.join(mats) or 'el material del plano'} hasta {n(esp)} mm de espesor" if esp else "WPS/PQR de soldadura",
                                   "Calificación de soldadores (WPQ) para esos WPS", "Procedimiento de RX y de LP (escrito, nivel 3 ISO 9712)",
                                   "Confirmar con el pliego: si exige procedimientos nuevos o alcanzan los vigentes de ITT"]},
        "transporte": transporte(cfg, kg_p + kg_e),
        "procedimientos": {"lista": procedimientos(filas, esp, sol["juntas_bw"], sol["juntas_sw_olet"], rx, m2_pip + m2_est)},
        "ph": {"litros": litros(cfg)},
        "horas": {},
    }
    ficha["procedimientos"]["cantidad"] = sum(p["cantidad"] for p in ficha["procedimientos"]["lista"])
    ficha["referencias"] = {}
    for r in RUBROS:
        glob = [it for it in cfg["items"] if it.get("global") and it.get("rubro") == r]
        det = (cfg.get("rubros") or {}).get(r, {}).get("detalle") if modo(cfg, r) == "global" else [it for it in cfg["items"] if rubro_de(it) == r]
        ficha["referencias"][r] = {"modo": modo(cfg, r), "detallado_usd": round(importe_items(det or [], cfg), 2), "renglones_detalle": len(det or []),
                                   "global_usd": round(sum(it["fuentes"][0]["precio"] for it in glob), 2) if glob else None}
    return ficha


def unitarios(ficha, r, usd):
    """El precio (global o detallado) expresado por la unidad física del rubro, para comparar con antecedentes y tarifas."""
    f = ficha[r]
    pares = {"mo_piping": [("pulgada eq.", f.get("pulg_eq")), ("kg de piping", f.get("kg_piping")), ("junta a tope", f.get("juntas_bw"))],
             "mo_estructura": [("kg", f.get("kg"))], "pintura": [("m²", f.get("m2_total"))],
             "end": [("junta a tope", f.get("juntas_bw")), ("placa", (f.get("placas_chicas") or 0) + (f.get("placas_grandes") or 0))],
             "transporte": [("viaje", (1 / f["por_camion"]) if f.get("por_camion") else None)],
             "procedimientos": [("procedimiento", f.get("cantidad"))], "ph": [("litro", f.get("litros"))], "horas": []}[r]
    return [(u, usd / q) for u, q in pares if q]


def n(v, d=2):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def escribir(carpeta, ficha, cfg):
    p, eq = ficha, (cfg.get("equipo") or {}).get("singular", "equipo")
    mp, me, pi, en, tr = p["mo_piping"], p["mo_estructura"], p["pintura"], p["end"], p["transporte"]
    L = [f"# Ficha por rubro — {cfg['codigo']}", "",
         f"Generada por `herramientas/ficha_rubros.py` el {a_vista(p['generada'])}. Todo **por {eq}**; la cantidad ({fmtg(cfg['parametros']['N'])}) multiplica al final.",
         "Sirve para pedir un precio global al tercero y para controlarlo contra el cálculo detallado.", ""]

    def ref(r):
        x = p["referencias"][r]
        if r == "transporte" and x["modo"] != "global":
            return ["- Sin precio por equipo: se cotiza EXW (o flete aparte en los parámetros). Para sumarlo por equipo, pasar el rubro a global."]
        modo_txt = "manual" if x["modo"] == "global" else "por antecedentes"
        out = [f"- **Costo {modo_txt}.** Por antecedentes: USD {n(x['detallado_usd'])} ({x['renglones_detalle']} renglón/es, con ajuste por inflación)."]
        if x["detallado_usd"] and unitarios(p, r, x["detallado_usd"]):
            out.append("  - Por unidad: " + " · ".join(f"USD {n(v)}/{u}" for u, v in unitarios(p, r, x["detallado_usd"])))
        if x["global_usd"] is not None:
            out.append(f"- Manual: USD {n(x['global_usd'])}" + (" — **SIN PRECIO: pedir cotización con esta ficha**" if not x["global_usd"] else
                       " (" + " · ".join(f"USD {n(v)}/{u}" for u, v in unitarios(p, r, x["global_usd"])) + ")"))
            if x["global_usd"] and x["detallado_usd"] and abs(x["global_usd"] / x["detallado_usd"] - 1) > 0.15:
                out.append(f"- ⚠ El costo manual se aparta {n((x['global_usd'] / x['detallado_usd'] - 1) * 100, 0)}% del de antecedentes: revisar alcance")
        return out

    L += ["## 1. MO de armado y soldadura del piping", "",
          f"- Juntas a tope (BW) de taller: **{n(mp['juntas_bw'], 0)}** · juntas SW, cuplas y olets: **{n(mp['juntas_sw_olet'], 0)}** · extremos para soldar en campo: {n(mp['extremos_campo'], 0)}",
          f"- Pulgadas equivalentes de soldadura: **{n(mp['pulg_eq'])}**",
          f"- kg de piping (caños, bridas, accesorios y válvulas con tabla): **{n(mp['kg_piping'], 0)} kg** · bridas: {n(mp['bridas'], 0)}",
          f"- Diámetros soldados a tope: {', '.join(f'{fmtg(d)}\"' for d in mp['diametros']) or '—'}"]
    if mp["sin_peso"]:
        L.append(f"- Sin peso (no suman kg): {'; '.join(mp['sin_peso'])}")
    L += [f"- ⚠ {a}" for a in mp["avisos"]] + ref("mo_piping") + ["",
          "## 2. MO de fabricación de la estructura", "", f"- kg de estructura: **{n(me['kg'], 0)} kg** · m²: {n(me['m2'])}"] + ref("mo_estructura") + ["",
          "## 3. Granallado y pintura", "",
          f"- m² de piping: **{n(pi['m2_piping'])}** (caños y niples {n(pi['m2_canos'])}; bridas, accesorios y válvulas por largo equivalente) · m² de estructura: **{n(pi['m2_estructura'])}**",
          f"- m² total: **{n(pi['m2_total'])}** (sin overspray) · esquema: {pi['esquema'] or 'según pliego'}"] + ref("pintura") + ["",
          "## 4. Radiografía y END", "",
          f"- Juntas a tope: **{n(en['juntas_bw'], 0)}** · RX {n(en['rx_pct'], 0)}% → placas chicas **{n(en['placas_chicas'], 0)}**, grandes **{n(en['placas_grandes'], 0)}**",
          f"- Juntas SW, cuplas y olets (LP donde no se puede radiografiar): **{n(en['juntas_lp'], 0)}**",
          ] + ref("end") + ["",
          "## 5. Procedimientos", ""] + [f"- {x['nombre']}" + (f" ({x['alcance']})" if x["alcance"] else "") + (f" × {x['cantidad']}" if x["cantidad"] > 1 else "")
                                         for x in p["procedimientos"]["lista"]] + ["- Confirmar con el pliego si exige procedimientos nuevos o alcanzan los vigentes de ITT"] + ref("procedimientos") + ["",
          "## 6. Prueba hidráulica", "", f"- Volumen interior de los caños: **{n(p['ph']['litros'], 1)} litros**"] + ref("ph") + ["",
          "## 7. Horas de ITT (ingeniería, calidad y montaje)", ""] + ref("horas") + ["",
          "## 8. Transporte", "",
          f"- Medidas del {eq}: {n(tr['largo_m'])} × {n(tr['ancho_m'])} × {n(tr['alto_m'])} m (largo × ancho × alto) · kg: **{n(tr['kg_equipo'], 0)}** (piping + estructura)"
          + (f" · destino: {tr['destino']}" if tr["destino"] else "")]
    if tr["por_camion"]:
        L.append(f"- Entran **{tr['por_camion']}** por semirremolque ({fmtg(CAMION['largo'])} × {fmtg(CAMION['ancho'])} m, {fmtg(CAMION['kg'] / 1000)} t; por medidas {tr['por_medida']}, por peso {tr['por_peso']}) → **{tr['viajes']} viaje(s)** para {fmtg(cfg['parametros']['N'])}")
    L += [f"- ⚠ {a}" for a in tr["avisos"]] + ref("transporte") + [""]
    (carpeta / "ficha_rubros.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (carpeta / "ficha_rubros.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main(carpeta, accion=None, rubro=None):
    carpeta = Path(carpeta)
    cfg = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    if accion:
        (pasar_a_global if accion == "--global" else volver_a_detallado)(cfg, rubro)
        (carpeta / "cotizacion.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{rubro}: modo {modo(cfg, rubro)} (volver a correr armar_cotizacion.py)")
    ficha = armar(carpeta, cfg)
    escribir(carpeta, ficha, cfg)
    print(f"Ficha por rubro → {carpeta / 'ficha_rubros.md'}")
    return ficha


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], *(a[1:3] if len(a) >= 3 else []))
