"""Precotización automática (sin IA) desde la tabla del plano.

Uso: python herramientas/precotizar.py cotizaciones/<carpeta> [--comparar]

Lee <carpeta>/pedido/lista_materiales_plano.csv y arma <carpeta>/cotizacion_auto.json + <carpeta>/precotizacion.md:
1. Materiales: cada renglón del plano se busca en el catálogo (misma lógica que buscar_material.py). Se toma el IGUAL con
   precio; si no hay, el SIMILAR más parecido con precio, con su diferencia; si no hay ninguno, el renglón queda en 0 con
   "SIN PRECIO: pedir cotización". Fuente, fecha y origen salen del catálogo. Precios sin IVA.
2. Soldaduras: de la columna de extremos, junta por junta. Los extremos BW se juntan de a dos (una junta = dos extremos);
   cada extremo SW es una junta; la cupla, media cupla u olet BW/SW es una junta sobre el caño con el factor de
   factores_accesorios.csv (1,75; weldolet 2,5). Pulgadas equivalentes = DN × factor de espesor (factores_soldadura.csv).
   La columna opcional `extremos_campo` (por unidad) dice cuántos extremos BW quedan abiertos para soldar en campo o con
   la línea del cliente: no suman soldadura de taller. Sin esa columna se avisa que hay que confirmarlo en el dibujo.
   Tarifa: costo propio de planta vigente de costos/tarifas.csv.
3. Servicios calculados: pintura (m² exteriores de caños y niples × última tarifa USD/m² del catálogo de servicios),
   prueba hidráulica (volumen; precio del último global del catálogo, como similar) y radiografía si `parametros.rx_pct` > 0
   (placas por junta de factores_soldadura.csv × tarifas de Antonelli).
Lo que no se puede calcular (armado, ingeniería y calidad, embalaje, flete) queda listado "a completar".

La IA o una persona solo revisa lo que el informe marca: similares, sin precio, estimados y extremos de campo.
Para usarla: revisar precotizacion.md y copiar cotizacion_auto.json a cotizacion.json (o pasar los ítems a mano).
"""
import argparse
import calendar
import csv
import json
import math
import re
import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fmt, fmtg, cantidad_plano  # noqa: E402
from buscar_material import buscar  # noqa: E402
from catalogo_materiales import unidad_norm  # noqa: E402
from indice_proyectos import frac, norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TEC = RAIZ / "conocimiento" / "tecnico"
TIPO = {"lista": "lista", "compra": "stock", "stock (precio maestro)": "stock", "cotización": "cot", "planilla interna": "ant",
        "estimado (cepo)": "est", "estimado (fecha supuesta)": "est"}
SERIES = {"150", "300", "600", "800", "900", "1500", "2500", "2000", "3000", "6000", "9000"}
SCHEDULES = {"5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160", "STD", "XS", "XXS"}
OLETS = r"cupla|sockolet|threadolet|thredolet|weldolet|elbowlet|latrolet|nipolet|\bolet"


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def dn_de(txt):
    m = re.findall(r"(\d+\s\d/\d|\d+/\d+|\d+(?:[.,]\d+)?)", str(txt).replace('"', " "))
    try:
        return frac(m[0].replace(",", ".")) if m else None
    except (ValueError, ZeroDivisionError):
        return None


def partes_sch(v):
    """Partes de una columna serie/schedule: "#300 x sch 80", "STD x XS", "XS", "300/40" (no parte "XS" en la X; CTRL-SK01)."""
    return [p.strip("#").replace("SCH", "") for p in re.split(r"\s+X\s+|[/ ]|(?<=\d)X(?=\d)", str(v).upper()) if p.strip("#")]


def sch_de(v):
    return next((p for p in partes_sch(v) if p in SCHEDULES), "")


def serie_de(v):
    return next((p for p in partes_sch(v) if p in SERIES), "")


def largo_virola(desc):
    """Largo de una virola: "× 3,2 m" o "L 3200 mm"; nunca el diámetro ("DI 1.280 mm" se tomaba como largo, Camuzzi 003)."""
    t = norm(desc)
    m = re.search(r"(?<![\d.,])(\d+(?:,\d+)?)\s?m\b", t)
    if m:
        return float(m.group(1).replace(",", "."))
    t = re.sub(r"\b(?:di|de|od|id|diam)\s?\d[\d.]*\s?mm", " ", t)
    return largo_m(t)


def largo_m(desc):
    m = re.search(r"(\d[\d.]*)\s?mm", norm(desc))
    return float(m.group(1).replace(".", "")) / 1000 if m else None


def texto_busqueda(r):
    d = r["diametro"]
    # el diámetro va entre comas para que no se pegue a una medida de la descripción ("espárrago 3/4 x 6" + "3/4"" se leía
    # "3/4 x 6 3/4"; CTRL-C01/P01)
    partes = [r["descripcion"], f", Ø {d}," if d else ""]
    sr, sc = serie_de(r["serie_sch"]), sch_de(r["serie_sch"])
    if sr:
        partes.append(f"#{sr}")
    from compatibilidad import SCH_DOBLE
    dob = re.search(SCH_DOBLE, norm(r["serie_sch"]))
    if dob:  # "80x40": schedule de cada extremo, para que el control lo vea (tercera auditoría 30-10-2026)
        partes.append(f"sch {dob.group(1)}x{dob.group(2)}")
    elif sc:
        partes.append(f"sch {sc}")
    partes += [r["material"], r["extremos"].replace("-M", "").replace("-H", ""), r.get("modelo_fabricante", "")]
    return " ".join(p for p in partes if p)


AJUSTE_DIRECTAS = 0.75
FECHA_REF = ""  # parametros.fecha_referencia de la cotización: no se usan tarifas posteriores (casos de control)
EXCLUIR = []  # textos de la ruta de origen a no usar (casos de control: el propio proyecto no puede ser su referencia)


def excluido(fila):
    origen = " ".join(str(fila.get(k, "")) for k in ("ruta_origen", "archivo_origen", "ruta_repo", "proveedor")).lower()
    return any(x.lower() in origen for x in EXCLUIR)


HISTORIAL = None


def historial_de(codigo):
    """Precios del historial de una pieza (sin los excluidos), del más viejo al más nuevo."""
    sin_excluidos([])  # carga el historial
    return [float(h["precio_usd"]) for h in sorted(HISTORIAL.get(codigo, []), key=lambda h: h["fecha"]) if h["precio_usd"] and not excluido(h)]


def sin_excluidos(res):
    """Saca de los resultados los precios de los proyectos excluidos. Si la pieza tiene otros precios en el historial,
    usa el más reciente de esos en lugar de borrar la pieza entera (CTRL-C01 y CTRL-M01)."""
    global HISTORIAL
    if HISTORIAL is None:
        HISTORIAL = {}
        for h in leer(RAIZ / "conocimiento" / "precios" / "catalogo_materiales_historial.csv"):
            HISTORIAL.setdefault(h["codigo"], []).append(h)
    if not EXCLUIR:
        return res
    out = []
    for x in res:
        c = x[7]
        if not excluido(c):
            out.append(x)
            continue
        # la fila del historial tiene que ser la misma pieza (CTRL-SK01: NIP-01780, niple 1/2", tenía un niple 2" en el historial)
        misma = lambda h: all(json.loads(h["atributos"] or "{}").get(k, c.get(k, "")) == c.get(k, "") for k in ("diametro", "serie", "schedule") if c.get(k))
        otros = sorted((h for h in HISTORIAL.get(c["codigo"], []) if not excluido(h) and h["precio_usd"] and misma(h)), key=lambda h: h["fecha"])
        if otros:
            h = otros[-1]
            c2 = {**c, "ultimo_precio_usd": h["precio_usd"], "fecha_ultimo_precio": h["fecha"], "tipo_precio": h["tipo_precio"], "proveedor": h["proveedor"],
                  "ruta_origen": h["ruta_origen"], "archivo_origen": h["archivo_origen"], "ruta_repo": h["ruta_repo"], "alerta": c.get("alerta", "")}
            out.append(tuple(list(x[:7]) + [c2] + list(x[8:])))
    return out


ACERO = RAIZ / "conocimiento" / "precios" / "acero_por_kg.csv"


def acero_kg(r):
    """Pieza de acero al carbono pedida por kg (chapa, placa, tapa, asa, planchuela, ángulo): precio de materia prima por kg
    de acero_por_kg.csv (+10% por recortes). Devuelve (fila, motivo) o (None, "")."""
    t = norm(f"{r['descripcion']} {r['material']} {r['diametro']}")
    if not re.search(r"sae ?10\d\d|\b(?:s?a)[- ]?(?:36|283|516)\b|f-? ?24|acero al carbono|\bhierro\b|\bchapa|planchuela|angulo|\bplaca\b|"
                     r"\b(?:upn|ipn|heb|hea|ipe)\b|perfil|bastidor|virola|\bpatas?\b|\bcunas?\b|cancamo", t) or re.search(r"inox|aisi|aluminio|bronce", t):
        return None, ""
    filas = leer(ACERO)
    if not filas:
        return None, ""
    forma = ("hierro ángulo" if re.search(r"angulo|\b(?:upn|ipn|heb|hea|ipe)\b|perfil", t) else "planchuela" if "planchuela" in t else "caño estructural" if re.search(r"tubo|cano estructural", t)
             else "chapa semilla de melón" if "semilla" in t else "chapa negra lisa")
    cand = [f for f in filas if f["forma"] == forma] or [f for f in filas if f["forma"] == "chapa negra lisa"]
    m = re.search(r"(?:esp\.?|espesor|e=)\s?(\d+(?:[.,]\d+)?)\s?mm", t) or re.search(r"(\d+(?:[.,]\d+)?)\s?mm", t)
    esp = float(m.group(1).replace(",", ".")) if m else None
    fila = min(cand, key=lambda f: abs(float(f["espesor_mm"]) - esp)) if esp else cand[0]
    nota = " (A-516: se toma el precio de chapa A-36 de la lista; el A-516 suele costar más)" if re.search(r"\b(?:s?a)[- ]?516\b", t) else ""
    return fila, (f"precio por kg de materia prima ({fila['forma']} {fila['medida']}"
                  + (f", la más cercana a {fmtg(esp)} mm" if esp else "") + ") +10% por recortes; no incluye corte, plegado ni rolado" + nota)


def kg_de(r):
    """Kilos por unidad de una pieza de chapa o perfil: escritos ("590 kg c/u"), perfil por metro, o virola π·D·L·e·7850."""
    t = norm(r["descripcion"])
    m = re.search(r"(\d+(?:[.,]\d+)?)\s?kg\s?(?:c/u|cada)", t)
    if m:
        return float(m.group(1).replace(",", ".")), "kg escritos en la descripción"
    if re.search(r"\bvirola", t) and dn_de(r["diametro"]) and largo_virola(r["descripcion"]) and espesor_mm(r):
        D, L, e = dn_de(r["diametro"]) * 0.0254, largo_virola(r["descripcion"]), espesor_mm(r) / 1000
        return round(math.pi * D * L * e * 7850, 1), f"π × {fmt(D, 3)} m × {fmtg(L)} m × {fmt(e * 1000, 2)} mm × 7.850 kg/m³"
    return None, ""


def rechazo(x, r, fam=""):
    """Motivo por el que un similar no sirve como precio, o None.
    - Diámetro: hasta 1,6 veces contra alguno de los del plano (12"x3/4" → 12 o 3/4); desde 8", hasta 1,25 veces (el costo
      crece con Ø²; CTRL-SK01: brida 16" con una de 10"). Un candidato SIN diámetro no sirve si el plano lo da (CTRL-SK01:
      retención 12" con una wafer 3" no leída).
    - Serie: en válvulas tiene que ser la misma (CTRL-TS01: Taval #900 con #300); en el resto, hasta 2,1 veces (#300 con
      #600 sí; #900 con #300 o #3000 con #300 no; CTRL-P01).
    - Válvulas: extremos roscados contra bridados, o acero al carbono contra inoxidable, no son similares (CTRL-SK01, P02)."""
    difs = x[6]
    pedidos = [dn_de(v) for v in re.split(r"\s*x\s*", str(r["diametro"]).lower()) if dn_de(v)]
    if pedidos and any(re.match(r"diametro: sin dato", d) for d in difs) and fam in ("VAL", "BRI", "ABW", "AFO", "CAN", "NIP"):
        return "sin diámetro conocido"
    md = next((re.match(r'diametro: ([\d.]+)"', d) for d in difs if re.match(r'diametro: [\d.]+"', d)), None)
    if md and pedidos:
        dc = float(md.group(1))
        rel = min(max(dc, d) / max(min(dc, d), 1e-9) for d in pedidos)
        if rel > 1.6 or (max(dc, *pedidos) >= 8 and rel > 1.25):
            return f"de otro diámetro ({md.group(1)}\")"
    ms = next((re.match(r"serie: (\d+) \(pedido (\d+)\)", d) for d in difs if re.match(r"serie: \d+ \(pedido \d+\)", d)), None)
    if ms:
        a, b = int(ms.group(1)), int(ms.group(2))
        if fam == "VAL" or max(a, b) / max(min(a, b), 1) > 2.1:
            return f"de otra serie ({a} contra {b})"
    if fam == "VAL":
        me = next((re.match(r"extremos: (.*) \(pedido (.*)\)", d) for d in difs if re.match(r"extremos: .* \(pedido .*\)", d)), None)
        rosca = lambda e: bool(re.search(r"npt|bsp|sw|rosc", e.lower()))
        if me and rosca(me.group(1)) != rosca(me.group(2)):
            return f"de otros extremos ({me.group(1)} contra {me.group(2)})"
        mm = next((re.match(r"material: (.*) \(pedido (.*)\)", d) for d in difs if re.match(r"material: .* \(pedido .*\)", d)), None)
        inox = lambda m: bool(re.search(r"inox|aisi|316|304|cf8|galv", m.lower()))
        if mm and inox(mm.group(1)) != inox(mm.group(2)):
            return f"de otro material ({mm.group(1)} contra {mm.group(2)})"
    return None


def ajuste_similar(x, r, fam):
    """(factor, nota) para llevar el precio de un similar al tamaño pedido: por diámetro (Ø pedido ÷ Ø similar)^1,5 y,
    en caños, accesorios y bridas, por espesor de pared (schedule pedido ÷ schedule del similar; CTRL-SK01: tee 12" XS con
    una STD, CTRL-TS01: tee sch 160 con una sch 80). Antes se usaban sin escalar."""
    from catalogo_materiales import ESPESORES
    f, notas = 1.0, []
    pedidos = [dn_de(v) for v in re.split(r"\s*x\s*", str(r["diametro"]).lower()) if dn_de(v)]
    md = next((re.match(r'diametro: ([\d.]+)"', d) for d in x[6] if re.match(r'diametro: [\d.]+" \(pedido', d)), None)
    if md and pedidos and fam not in ("JUN", "INS"):
        # olets: la pieza es la salida (12"x3/4" → 3/4"); el resto, el diámetro principal
        dc, dp = float(md.group(1)), (min(pedidos) if re.search(OLETS, norm(r["descripcion"])) else pedidos[0])
        k = (dp / dc) ** 1.5
        f *= k
        notas.append(f"precio escalado por diámetro ({fmtg(dp)}\" ÷ {fmtg(dc)}\")^1,5 = × {fmt(k, 2)}")
    ms = next((re.match(r"schedule: (\w+) \(pedido (\w+)\)", d) for d in x[6] if re.match(r"schedule: \w+ \(pedido \w+\)", d)), None)
    if ms and pedidos and fam in ("ABW", "CAN", "NIP"):  # en bridas el schedule es solo el bisel del cuello: no cambia el precio
        tabla = ESPESORES.get(pedidos[0], {})
        alias = lambda s: s if s in tabla else {"STD": "40", "XS": "80", "40": "STD", "80": "XS"}.get(s, s)
        ec, ep = tabla.get(alias(ms.group(1).upper())), tabla.get(alias(ms.group(2).upper()))
        if ec and ep and abs(ep / ec - 1) > 0.05:
            f *= ep / ec
            notas.append(f"escalado por espesor (sch {ms.group(2)} {fmtg(ep)} mm ÷ sch {ms.group(1)} {fmtg(ec)} mm = × {fmt(ep / ec, 2)})")
    return f, "; ".join(notas)


BARRA_CHICA, BARRA_GRANDE = 6.0, 12.0  # caños de menos de 3" en barras de 6 m; de 3" en adelante, de 12 m (Renard 10,5–12,5 m)


def barra_m(diametro):
    d = dn_de(diametro) or 0
    return BARRA_GRANDE if d >= 3 else BARRA_CHICA


def provee_cliente(r):
    """Material que provee el cliente: columna `provee` = cliente, o el texto lo dice (CTRL-CA01, prefabricado de Sacde)."""
    if norm(r.get("provee", "")).startswith("cliente"):
        return True
    t = norm(f"{r.get('modelo_fabricante', '')} {r['descripcion']}")
    return bool(re.search(r"provist[oa]s? por (?:el )?cliente|suministr\w* (?:por|del) (?:el )?cliente|material(?:es)? del cliente|\bsum\.? por (?:el )?cliente", t))


VIEJOS, ELEGIDO = {}, {}  # pos → nota de precio viejo reemplazado; id → descripción del catálogo elegida


def material(r, n):
    """Ítem de cotizacion.json para un renglón del plano, más el renglón del informe."""
    from atributos_plano import fijos
    fam, at, _, faltan, res = buscar(texto_busqueda(r), fijos=fijos(r))  # los datos en columnas mandan (03-11-2026)
    res = sin_excluidos(res)
    cant, unidad = cantidad_plano(r["cantidad"]), (r["unidad"] or "un").strip()
    l = largo_m(r["descripcion"])
    if fam == "CAN" and unidad_norm(unidad) == "un" and l:
        cant, unidad = round(cant * l, 3), "m"  # "caño longitud 1900 mm × 1" se compra por metro
    con_precio = [x for x in res if x[7]["ultimo_precio_usd"]]
    # orden: igual con precio real > similar con precio real > igual estimado (cepo) > similar estimado
    real = [x for x in con_precio if not x[7]["tipo_precio"].startswith("estimado")]
    est = [x for x in con_precio if x[7]["tipo_precio"].startswith("estimado")]
    orden = [x for x in real if x[0]] + [x for x in real if not x[0]] + [x for x in est if x[0]] + [x for x in est if not x[0]]
    # se descartan los similares de otro diámetro o de otra clase de serie y se prueba el siguiente (CTRL-M01: una
    # esférica 4" PR sirve de referencia para una 4" PT; una 2" PT no)
    validos = [x for x in orden if x[0] or not rechazo(x, r, fam)]
    rechazado = orden[0] if orden and not validos else None
    elegido = validos[0] if validos else None
    # un precio de stock o compra viejo (más de 18 meses antes de la fecha de referencia) no le gana a una cotización
    # reciente que solo difiere en la cara o los extremos (CTRL-TS01: bridas #900 del stock 2022–2024 contra Provemet 2025)
    if elegido and elegido[7]["tipo_precio"] in ("compra", "stock (precio maestro)"):
        ref = FECHA_REF or date.today().isoformat()
        limite = f"{int(ref[:4]) - 1}-{int(ref[5:7]) - 6:02d}" if int(ref[5:7]) > 6 else f"{int(ref[:4]) - 2}-{int(ref[5:7]) + 6:02d}"
        if elegido[7]["fecha_ultimo_precio"][:7] < limite:
            nuevo = next((x for x in validos if x[7]["fecha_ultimo_precio"][:7] >= limite and x[7]["tipo_precio"] not in ("compra", "stock (precio maestro)", "estimado (cepo)", "estimado (fecha supuesta)")
                          and all(d.split(":")[0] in ("cara", "extremos", "norma", "marca") for d in x[6])), None)
            if nuevo:
                VIEJOS[r["pos"]] = f"se prefirió un precio reciente a {elegido[7]['tipo_precio']} del {elegido[7]['fecha_ultimo_precio']} ({elegido[7]['codigo']}, USD {fmt(float(elegido[7]['ultimo_precio_usd']), 2)})"
                elegido = nuevo
    item = {"id": f"M{n:02d}", "pos": r["pos"], "grupo": "material",
            # descripción del cliente tal cual (regla crítica, Matías 29-10-2026); el Ø es otra columna del plano y va aparte
            "descripcion": f"{r['descripcion']} · Ø {r['diametro']}" if r["diametro"] and norm(r["diametro"]) != "n/a" else r["descripcion"],
            "cantidad": cant, "unidad": unidad,
            "especificacion": f"Plano: {r['diametro']} · {r['serie_sch']} · {r['material']} · {r['extremos']}" + (f" · {r['modelo_fabricante']}" if r.get("modelo_fabricante") else "")
            + (f" · {r['cantidad_origen']}" if r.get("cantidad_origen") else "") + (f" · Nota ITT: {r['nota']}" if r.get("nota") else "")}
    # datos del pedido en columnas (familia, Ø, serie, schedule, material, marca, norma, rango…) y los que faltan: los usan
    # la planilla y la página para comparar con el antecedente dato por dato (Matías, 03-11-2026)
    from buscar_material import faltan_datos
    item["atributos"] = {"familia": fam, **{k: v for k, v in at.items() if v}}
    item["faltan_datos"] = faltan_datos(fam, at)
    if provee_cliente(r):
        item["provee"] = "cliente"
        item["fuentes"] = [{"tipo": "cot", "precio": 0, "proveedor": "PROVISTO POR EL CLIENTE (no se cotiza)", "origen": "tabla del plano / pliego",
                            "fecha": FECHA_REF or date.today().isoformat(), "coincide": "igual"}]
        return item, f"| {r['pos']} | {item['descripcion'][:45]} | PROVISTO POR EL CLIENTE | 0 | — | cuenta para soldadura, pintura y PH; no se compra |"
    # válvula Taval (empresa del grupo): va con el factor de válvulas Taval de la cotización (parametros.FTV, por defecto 1)
    if fam == "VAL" and "taval" in norm(r.get("modelo_fabricante", "")):
        item["taval"] = True  # el plano pide Taval; si no, se marca solo cuando el precio elegido es de Taval (al final)
    pf = perfil(r) if unidad_norm(unidad) == "m" else None
    kgu, como = kg_de(r) if unidad_norm(unidad) == "un" else (None, "")
    if (pf or kgu) and not (elegido and elegido[0]):
        fila, motivo = acero_kg(r)
        if fila:
            usd_kg = float(fila["usd_kg_con_recortes"])
            if pf:  # perfil pedido por metro: kg/m de tecnico/perfiles.csv × precio por kg
                precio, det = pf[0] * usd_kg, f"{fmtg(pf[0])} kg/m (perfiles.csv) × USD {fmt(usd_kg, 2)}/kg; {motivo}"
            else:   # virola o pieza con kilos escritos: kg × (chapa + rolado si es virola)
                rol, f_rol = tarifa("fabricacion", "rolado de chapa", ("tercero",)) if re.search(r"\bvirola", norm(r["descripcion"])) else (None, None)
                precio = kgu * (usd_kg + (rol or 0))
                txt_rol = f" + rolado {fmtg(rol)}/kg ({f_rol['fuente'][:60]})" if rol else ""
                det = f"{fmtg(kgu)} kg ({como}) × (USD {fmt(usd_kg, 2)}/kg{txt_rol}); {motivo}"
            item["fuentes"] = [{"tipo": "est", "precio": round(precio, 2), "proveedor": "Precios de acero por kg (J. Elejondo)" + (" + rolado" if kgu and re.search(r"\bvirola", norm(r["descripcion"])) else ""),
                                "origen": fila["fuente"], "fecha": fila["fecha"], "coincide": "similar", "diferencia": det[:300]}]
            return item, (f"| {r['pos']} | {item['descripcion'][:45]} | ESTIMADO (por kg) | USD {fmt(precio, 2)}/{unidad} | {fila['fecha']} | {det[:110]} |")
    if unidad_norm(unidad) == "kg" and not (elegido and elegido[0] and unidad_norm(elegido[7]["unidad"]) == "kg"):
        fila, motivo = acero_kg(r)
        if fila:
            item["fuentes"] = [{"tipo": "cot", "precio": float(fila["usd_kg_con_recortes"]), "proveedor": "Precios de acero (J. Elejondo)",
                                "origen": fila["fuente"], "fecha": fila["fecha"], "coincide": "similar", "diferencia": motivo}]
            return item, (f"| {r['pos']} | {item['descripcion'][:45]} | SIMILAR (acero por kg) | USD {fmt(float(fila['usd_kg_con_recortes']), 2)}/kg | "
                          f"{fila['fecha']} cot | {motivo} |")
    if rechazado:
        c = rechazado[7]
        item["fuentes"] = [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO EN EL CATÁLOGO: pedir cotización", "origen": "—",
                            "fecha": date.today().isoformat(), "coincide": "sin_ref",
                            "diferencia": f"El más parecido es {rechazo(rechazado, r, fam)} ({c['codigo']} {c['descripcion'][:50]}, USD {fmt(float(c['ultimo_precio_usd']), 2)}): no sirve como precio"}]
        return item, f"| {r['pos']} | {item['descripcion'][:45]} | **SIN PRECIO** | — | — | el más parecido es {rechazo(rechazado, r, fam)} ({c['codigo']}, USD {fmt(float(c['ultimo_precio_usd']), 2)}): pedir cotización |"
    if not elegido:
        item["fuentes"] = [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO EN EL CATÁLOGO: pedir cotización", "origen": "—",
                            "fecha": date.today().isoformat(), "coincide": "sin_ref", "diferencia": "No hay pieza de esa familia y tipo con precio"}]
        return item, f"| {r['pos']} | {item['descripcion'][:45]} | **SIN PRECIO** | — | — | pedir cotización |"
    igual, _, _, _, _, _, difs, c = elegido
    precio = float(c["ultimo_precio_usd"])
    nota_u = ""
    # último precio fuera de lo normal: si se aparta más de 40% de la mediana de los últimos precios de la pieza, va la
    # mediana (CTRL-M01: brida WN 4" a 55,77 de Provemet contra 87 a 106 de las otras cotizaciones)
    hist = historial_de(c["codigo"])
    if len(hist) >= 3:
        med = statistics.median(hist[-4:])
        if abs(precio / med - 1) > 0.40:
            nota_u = f"el último precio ({fmt(precio, 2)}) se aparta más de 40% de la mediana de sus últimos precios: se usa la mediana {fmt(med, 2)}"
            precio = med
    if not igual:
        k, nota_k = ajuste_similar(elegido, r, fam)
        if k != 1:
            precio *= k
            nota_u = "; ".join(x for x in [nota_u, nota_k] if x)
    if any(re.match(r"paso: reducido \(pedido total\)", d) for d in difs):
        precio *= 1.30
        nota_u = "; ".join(x for x in [nota_u, "esférica de paso reducido: se estima la de paso total × 1,30"] if x)
    uc, up = unidad_norm(c["unidad"]), unidad_norm(unidad)
    m = re.fullmatch(r"tira de (\d+) m", uc)
    if m and up == "m":
        precio, nota_u = precio / float(m.group(1)), f"precio de tira de {m.group(1)} m pasado a metro"
    elif uc and up and uc != up:
        nota_u = "; ".join(x for x in [nota_u, f"unidad distinta: catálogo por {uc}, plano por {up}"] if x)
    if r["pos"] in VIEJOS:
        nota_u = "; ".join(x for x in [nota_u, VIEJOS[r["pos"]]] if x)
    coincide = "igual" if igual and "unidad distinta" not in nota_u and "mediana" not in nota_u and r["pos"] not in VIEJOS else "similar"
    ELEGIDO[item["id"]] = c["descripcion"]
    dif = "; ".join(difs + ([nota_u] if nota_u else []))
    tipo = TIPO.get(c["tipo_precio"], "ant")
    item["fuentes"] = [{"tipo": tipo, "precio": round(precio, 2), "proveedor": f"{c['proveedor'][:70]} · {c['codigo']}", "codigo": c["codigo"],
                        "origen": (c["ruta_origen"] + (" · " + c["archivo_origen"] if c["archivo_origen"] else ""))[:200],
                        "fecha": c["fecha_ultimo_precio"], "coincide": coincide, **({"diferencia": dif} if coincide == "similar" else {})}]
    if fam == "VAL" and "taval" in norm(c.get("marca", "") + " " + c["proveedor"]):
        item["taval"] = True  # válvula Taval: va con el factor de válvulas Taval (parametros.FTV)
    estado = "IGUAL" if coincide == "igual" else "SIMILAR"
    if tipo == "est":
        estado += " (estimado cepo)"
    if c.get("alerta"):
        estado += " ⚠"
    fila = (f"| {r['pos']} | {item['descripcion'][:45]} | {estado} | {fmt(precio, 2)} / {unidad} | {c['fecha_ultimo_precio']} · {c['tipo_precio']} | "
            f"{(dif or '—')[:110]}{' · faltan: ' + ', '.join(faltan) if faltan else ''} |")
    return item, fila


def espesor_mm(r):
    """Espesor de pared escrito en la descripción ("esp. 3/8\"", "e = 9,52 mm"): virolas, casquetes y chapas."""
    m = re.search(r"\b(?:esp|e)\s*[.=:]?\s*(\d+(?:[.,]\d+)?(?:\s*\d+/\d+|/\d+)?)\s*(\"|mm|pulg)", str(r.get("descripcion", "")) + " " + str(r.get("serie_sch", "")), re.I)
    if not m:
        return None
    v = frac(m.group(1).replace(",", ".")) if "/" in m.group(1) else float(m.group(1).replace(",", "."))
    return v * 25.4 if m.group(2) != "mm" else v


def factor_espesor(dn, sch, tabla, esp=None):
    if esp and dn is not None:  # espesor escrito: la fila de ese diámetro con el espesor más parecido
        filas = [r for r in tabla if abs(float(r["dn_pulg"]) - dn) < 1e-6 and r["espesor_mm"]]
        if filas:
            r = min(filas, key=lambda r: abs(float(r["espesor_mm"]) - esp))
            return float(r["factor_espesor"]), float(r["placas_rx_chicas"] or 0), float(r["placas_rx_grandes"] or 0)
    sch = sch or "40"
    for r in tabla:
        if dn is not None and abs(float(r["dn_pulg"]) - dn) < 1e-6 and (r["schedule"] == sch or r["clase"] == sch):
            return float(r["factor_espesor"]), float(r["placas_rx_chicas"] or 0), float(r["placas_rx_grandes"] or 0)
    return 1.0, 0.0, 0.0


PERFILES = None
def no_son_piezas(unidad):
    """Cantidad en kg, m² o toneladas (no son piezas: no cuentan juntas). Acepta Kg, KG., kgs, kilos, m², M2, mts2, tn, ton."""
    u = re.sub(r"[\s.]", "", norm(unidad))
    return bool(re.fullmatch(r"kgs?|kilos?|kilogramos?|m2|mts?2|metros?cuadrados?|tn|t|tons?|toneladas?", u))


M2_POR_KG_ESTRUCTURA = 0.030  # 30 m²/t: perfiles livianos (UPN 140 = 32,5 m²/t) y chapas de apoyo
INTERNOS = r"bafle|deflector|separador de niebla|interno|elemento filtrante|placa apoyo|viruta|refuerzo"


def perfil(r):
    """(kg/m, m²/m) de un perfil nombrado en la descripción (UPN 140, IPN 120, HEB 200…), de tecnico/perfiles.csv."""
    global PERFILES
    if PERFILES is None:
        PERFILES = {norm(x["designacion"]).replace(" ", ""): (float(x["kg_por_m"]), float(x["m2_por_m"] or 0)) for x in leer(TEC / "perfiles.csv")}
    m = re.search(r"\b(upn|ipn|heb|hea|ipe|upe)\s*(\d+)", norm(r["descripcion"]))
    return PERFILES.get(f"{m.group(1)}{m.group(2)}") if m else None


# m² de pintura de cada pieza = largo equivalente de caño de su diámetro, en diámetros (D): brida 1,5 D, codo 90 2,4 D,
# codo 45 1,2 D, tee 3 D, reducción 1,5 D, válvula 6 D, casquete 1 D. Reemplaza el × 3 fijo sobre los caños, que se
# quedaba corto con válvulas grandes (CTRL-SK01: 13,8 m² contra ~31) y triplicaba el caño recto (CTRL-CA01: 4.939 contra 1.688)
LARGO_EQ_D = [(r"valvula|\bvalv\b", 6.0), (r"\btee\b|\bte\b", 3.0), (r"codo 45|curva 45", 1.2), (r"\bcodo|\bcurva", 2.4),
              (r"reduc", 1.5), (r"brida", 1.5), (r"casquete|\bcap\b|tapa", 1.0)]


def od_m(dn):
    from catalogo_materiales import OD_NPS
    od = next((o for o, n in OD_NPS.items() if abs(n - dn) < 1e-6), None)
    return (od / 1000) if od else dn * 0.0254


def superficie_pintura(filas, m2_canos):
    """m² exteriores a pintar: caños y niples (tabla) + cada brida, accesorio y válvula por su largo equivalente (LARGO_EQ_D);
    envolvente de virolas (π·D·L) y casquetes (≈1,09·D²); estructura por kg o por metro de perfil."""
    piezas = 0.0
    env = est = 0.0
    for r in filas:
        d, q, u = norm(r["descripcion"]), cantidad_plano(r["cantidad"]), norm(r["unidad"])
        D = (dn_de(r["diametro"]) or 0) * 0.0254
        # una virola o un casquete cargado en kg es UNA pieza con sus medidas en la descripción: la cantidad son kilos, no
        # piezas (Camuzzi 003, 30-10-2026: 6.916 kg de chapa daban 38.852 m² de pintura)
        n_pz = 1 if u == "kg" else q
        if re.search(r"\bvirola", d) and D and largo_virola(r["descripcion"]) and not u.startswith("m"):  # por metro ya está en caños
            env += math.pi * D * largo_virola(r["descripcion"]) * n_pz
        elif re.search(r"casquete|cabezal", d) and D:
            env += 1.09 * D * D * n_pz
        elif re.search(INTERNOS, d):
            continue
        elif perfil(r) and u.startswith("m") and not u.startswith("m2"):
            est += perfil(r)[1] * q
        elif u == "kg" and re.search(r"perfil|upn|ipn|heb|bastidor|estructura|pata|cuna|soporte|skid|chapa|cancamo|angulo|planchuela", d):
            est += q * M2_POR_KG_ESTRUCTURA
        elif not u.startswith("m") and not re.search(r"\bcano\b|\bniple|\btubo\b|" + OLETS, d):
            k = next((v for rx, v in LARGO_EQ_D if re.search(rx, d)), None)
            dn = dn_de(r["diametro"])
            if k and dn:
                piezas += q * k * od_m(dn) * math.pi * od_m(dn)  # largo equivalente (k·D) × π·D
    return [("caños y niples", m2_canos), ("bridas, accesorios y válvulas (largo equivalente)", piezas), ("envolvente", env), ("estructura", est)]


def soldaduras(filas, diametral=False):
    """Pulgadas equivalentes de soldadura. diametral=True (prefabricado de volumen): pulgada diametral con base sch 40 = 1;
    el espesor solo ajusta por el cociente contra el sch 40 de ese diámetro (CTRL-CA01: así cotizan ITT y los terceros)."""
    tabla = leer(TEC / "factores_soldadura.csv")
    fac_acc = {norm(r["accesorio"]): float(r["factor"]) for r in leer(TEC / "factores_accesorios.csv")}
    bw_eq, juntas_olet, juntas_sw, detalle, placas = 0.0, 0.0, 0.0, [], [0.0, 0.0]
    extremos_bw = 0
    n_sw_olet = 0.0
    hay_campo = any("extremos_campo" in r for r in filas)
    # Caño por metro: no se sabe en cuántos tramos va, así que sus extremos no se cuentan; cada extremo BW de un
    # accesorio o brida de ese diámetro se toma como una junta con caño (cuenta doble), menos las uniones directas
    # brida–accesorio, que así se contarían dos veces: AJUSTE_DIRECTAS, calibrado con CTRL-M01 (68 → 52 juntas reales) y
    # CTRL-P01 (86 → 64). Las piezas de otro diámetro (virolas, casquetes) se cuentan por sus extremos.
    es_cano_m = lambda r: re.search(r"\bcano\b|\bcanos\b|\btubo\b", norm(r["descripcion"])) and norm(r["unidad"]).startswith("m")
    por_metro = [r for r in filas if es_cano_m(r) and "BW" in r["extremos"].upper()]
    diam_cano = {dn_de(x) for r in por_metro for x in re.split(r"\s*x\s*", r["diametro"].lower()) if dn_de(x)}
    mult = 2 * AJUSTE_DIRECTAS if por_metro else 1
    if por_metro:
        detalle.append(f"pos {', '.join(r['pos'] for r in por_metro)}: caño por metro; sus juntas se cuentan en los extremos BW de accesorios y bridas (una junta cada uno)")
    for r in por_metro:
        # juntas de empalme entre barras: un caño recto largo lleva una junta cada barra (CTRL-CA01: 190 m de 12" daban 0)
        dn, q = dn_de(r["diametro"]), cantidad_plano(r["cantidad"])
        emp = max(0, math.ceil(q / barra_m(r["diametro"]) - 1e-9) - 1)
        if emp and dn:
            f, pch, pgr = factor_espesor(dn, sch_de(r["serie_sch"]), tabla, espesor_mm(r))
            if diametral:
                f = f / (factor_espesor(dn, "40", tabla)[0] or 1)
            bw_eq += 2 * emp * dn * f
            extremos_bw += 2 * emp
            placas[0] += emp * pch
            placas[1] += emp * pgr
            detalle.append(f"pos {r['pos']}: {emp} junta(s) de empalme entre barras de {fmtg(barra_m(r['diametro']))} m ({fmtg(q)} m) × {fmtg(dn)}\" × {fmt(f, 4)}")
    avisos_kg = []
    for r in filas:
        if r in por_metro:
            continue
        # una cantidad en kg o m² no son piezas (chapa de virola, 6.916 kg): no cuenta juntas (COT26-0135-003, 30-10-2026);
        # la virola se cuenta por su largo si la descripción lo dice (regla de abajo), si no, avisa
        if no_son_piezas(r["unidad"]):
            if r["extremos"].strip():
                avisos_kg.append(f"pos {r['pos']}: cantidad en {r['unidad']} con extremos {r['extremos']}: no se cuentan juntas (no son piezas); contar sus soldaduras a mano")
            continue
        ext = r["extremos"].upper().replace("-M", "").replace("-H", "")
        toks = [t.strip() for t in re.split(r"[/]", ext) if t.strip()]
        d = norm(r["descripcion"])
        if len(toks) == 1:
            n_ext = 3 if re.search(r"\btee\b|\bte\b", d) else (1 if re.search(r"casquete|\bcap\b|brida|\btapa\b|cierre rapido|" + OLETS, d) else 2)
            toks = toks * n_ext
        n_bw, n_sw = toks.count("BW"), toks.count("SW")
        if not (n_bw or n_sw):
            continue
        q = cantidad_plano(r["cantidad"])
        if (n_bw + n_sw) * q > 500:  # auditoría 30-10-2026: más de 500 juntas en un renglón es casi seguro una unidad mal leída
            avisos_kg.append(f"pos {r['pos']}: {fmtg((n_bw + n_sw) * q)} extremos soldados en un solo renglón ({fmtg(q)} {r['unidad']}): confirmar la unidad")
        dn, sch = dn_de(r["diametro"]), sch_de(r["serie_sch"])
        f, pch, pgr = factor_espesor(dn, sch, tabla, espesor_mm(r))
        if diametral:
            f = f / (factor_espesor(dn, "40", tabla)[0] or 1)
        if re.search(OLETS, d):
            fa = 2.5 if "weldolet" in d else fac_acc.get("sockolets", 1.75)
            ds = [dn_de(x) for x in re.split(r"\s*x\s*", r["diametro"].lower()) if dn_de(x)]
            dn = min(ds) if ds else dn  # el olet se mide por la salida (12"x3/4" → 3/4"), no por el caño donde se suelda
            juntas_olet += (n_bw + n_sw) * q * (dn or 0) * fa
            n_sw_olet += (n_bw + n_sw) * q
            detalle.append(f"pos {r['pos']}: {int((n_bw + n_sw) * q)} junta(s) de {r['descripcion'][:25]} sobre caño × {fmtg(dn)}\" × {fmtg(fa)} = {fmt((n_bw + n_sw) * q * dn * fa, 2)}")
            continue
        campo = float(r.get("extremos_campo") or 0)
        dims = [dn_de(x) for x in re.split(r"\s*x\s*", r["diametro"].lower()) if dn_de(x)]
        m_r = mult if (not diam_cano or any(x in diam_cano for x in dims)) else 1
        bw_taller = max(0.0, n_bw - campo) * q * m_r
        extremos_bw += bw_taller
        if n_bw and not campo and len(dims) == 2 and dims[0] != dims[1]:
            # reducción: en una tee, 2 extremos del diámetro mayor y 1 del menor; en una reducción, 1 y 1
            schs = [sch_de(x) or sch for x in re.split(r"\s*x\s*", r["serie_sch"])] + [sch]
            f2 = factor_espesor(dims[1], schs[1] if len(schs) > 2 else sch, tabla)[0]
            n_men = 1
            prom = ((n_bw - n_men) * dims[0] * f + n_men * dims[1] * f2) / n_bw
            bw_eq += bw_taller * prom
            dn, f = prom, 1.0
        else:
            bw_eq += bw_taller * (dn or 0) * f
        juntas_sw += n_sw * q * (dn or 0) * f
        n_sw_olet += n_sw * q
        placas[0] += bw_taller / 2 * pch
        placas[1] += bw_taller / 2 * pgr
        if re.search(r"\bvirola", d) and largo_virola(r["descripcion"]) and not norm(r["unidad"]).startswith("m"):
            # costura longitudinal de la virola rolada: largo / (π · 25,4) pulgadas de diámetro equivalente (CTRL-T01)
            lon = q * largo_virola(r["descripcion"]) * 1000 / (math.pi * 25.4)
            bw_eq += 2 * lon * f  # bw_eq se divide por 2 al final (cuenta extremos)
            detalle.append(f"pos {r['pos']}: costura longitudinal de {fmtg(q)} virola(s) de {fmtg(largo_virola(r['descripcion']) * 1000)} mm = {fmt(lon, 1)} pulg-eq × {fmt(f, 4)}")
        if n_bw:
            detalle.append(f"pos {r['pos']}: {fmtg(bw_taller)} extremo(s) BW de taller ({fmtg(n_bw)} por unidad × {fmtg(q)}{f' − {fmtg(campo)} de campo por unidad' if campo else ''}{f' × {fmtg(m_r)} por el caño' if m_r != 1 else ''}) × {fmtg(dn)}\" × {fmt(f, 4)}")
        if n_sw:
            detalle.append(f"pos {r['pos']}: {fmtg(n_sw * q)} junta(s) SW × {fmtg(dn)}\" × {fmt(f, 4)}")
    juntas_bw = math.ceil(extremos_bw / 2 - 1e-9)  # juntas enteras (el ajuste de uniones directas deja fracciones)
    total = bw_eq / 2 + juntas_sw + juntas_olet
    avisos = list(avisos_kg)
    if extremos_bw % 2 and not por_metro:
        avisos.append(f"Quedan {fmtg(extremos_bw)} extremos BW de taller (número impar): falta marcar algún extremo de campo o una pieza")
    if not hay_campo and extremos_bw:
        avisos.append("La tabla no tiene la columna extremos_campo: se supuso que TODOS los extremos BW se sueldan en taller. Confirmar en el dibujo cuáles quedan para campo")
    return {"juntas_bw": juntas_bw, "pulg_eq": round(total, 3), "detalle": detalle, "avisos": avisos, "placas": placas, "juntas_sw_olet": n_sw_olet}


def mes_mas(f, n):
    a, m = int(f[:4]), int(f[5:7]) + n
    return f"{a + (m - 1) // 12}-{(m - 1) % 12 + 1:02d}"


def fin_de_mes(f):
    """AAAA-MM → último día real del mes (antes se pegaba "-31" y salía "2026-02-31"; CTRL-P02)."""
    if len(f) != 7:
        return f
    a, m = int(f[:4]), int(f[5:7])
    return f"{f}-{calendar.monthrange(a, m)[1]:02d}"


def tarifa(rubro, texto, tipos=("costo_propio",)):
    """La tarifa vigente más reciente del rubro (tipos en orden de preferencia), sin las del proyecto excluido (CTRL-P02,
    SK01: la tarifa DB NDT y la de estructura salían del mismo proyecto que se controlaba) ni posteriores a la fecha de
    referencia de la cotización (CTRL-CA01)."""
    filas = [r for r in leer(RAIZ / "conocimiento" / "costos" / "tarifas.csv")
             if r["rubro"] == rubro and texto in norm(r["concepto"]) and r["tipo"] in tipos and r["vigente"] == "si"
             and not any(x.lower() in (r.get("fuente", "") + " " + r.get("nota", "")).lower() for x in EXCLUIR)]
    previas = [r for r in filas if not FECHA_REF or r["fecha"][:7] <= mes_mas(FECHA_REF, 2)]  # hasta 2 meses después
    filas = previas or filas  # si no hay ninguna anterior a la fecha de referencia, la más vieja disponible
    if not filas:
        return None, None
    r = max(filas, key=lambda r: (-tipos.index(r["tipo"]), r["fecha"]))
    return float(r["valor_usd"]), r


def servicio_catalogo(hoja, unidad, palabras):
    mejor = None
    for r in leer(RAIZ / "conocimiento" / "precios" / "catalogo_servicios.csv"):
        if r["hoja"].startswith(hoja) and r["ultimo_precio_usd"] and "ESTIMADO" not in r["alerta"] and not excluido(r) and \
                (unidad is None or r["unidad_tarifa"] == unidad) and all(p in norm(r["servicio"] + " " + r["descripcion"]) for p in palabras):
            previo = lambda x: not FECHA_REF or x["fecha_ultimo_precio"][:10] <= FECHA_REF
            if mejor is None or (previo(r), r["fecha_ultimo_precio"]) > (previo(mejor), mejor["fecha_ultimo_precio"]):
                mejor = r  # la más reciente anterior a la fecha de referencia; si no hay, la más reciente
    return mejor


TERCERO_TIPOS = {"trampa": r"trampa", "tanque": r"tanque", "filtro": r"filtro", "separador": r"separador"}


def mo_tercero(tipo, d_eq, texto):
    """Mano de obra de fabricación de un tercero con el mismo tipo de equipo (catálogo de servicios, global por unidad), o
    None. Diámetro hasta 1,6 veces si el renglón lo dice; desempata el subtipo (receptora/lanzadora) y la fecha. CTRL-TS01:
    la trampa la fabricaba Ledesma (FAB-00066, 10.800) y la app sumaba soldadura y montaje propios."""
    import estimar_horas
    rx = TERCERO_TIPOS.get(tipo)
    if not rx:
        return None
    sub = estimar_horas.subtipo_de(texto)
    mejor = None
    for r in leer(RAIZ / "conocimiento" / "precios" / "catalogo_servicios.csv"):
        txt = norm(r["servicio"] + " " + r["descripcion"] + " " + r["equipo_referencia"])
        if not (r["hoja"].startswith("Fabric") and "tercero" in norm(r["servicio"]) and re.search(r"fabricacion (?:completa )?de(?:l)? " + rx, norm(r["servicio"]))
                and r["unidad"] == "global" and r["ultimo_precio_usd"] and not excluido(r) and "montaje dimensional" not in norm(r["servicio"])):
            continue
        ds = [float(frac(x)) for x in re.findall(r"(\d+)(?:\"|in\b| ?pulg)", r["descripcion"] + " " + r["equipo_referencia"]) if frac(x)]
        if ds and d_eq and max(max(ds), d_eq) / min(max(ds), d_eq) > 1.6:
            continue
        if not ds and not (sub and estimar_horas.subtipo_de(txt) == sub):
            continue  # sin tamaño ni subtipo no se sabe si es el mismo alcance (CTRL-F01: filtro FM S600 para un FM2 S300)
        clave = (bool(sub) and estimar_horas.subtipo_de(txt) == sub, r["fecha_ultimo_precio"])
        if mejor is None or clave > mejor[0]:
            mejor = (clave, r)
    return mejor[1] if mejor else None


def main(carpeta, comparar=False):
    carpeta = Path(carpeta)
    filas = leer(carpeta / "pedido" / "lista_materiales_plano.csv")
    if not filas:
        sys.exit(f"No está {carpeta}/pedido/lista_materiales_plano.csv")
    base_ruta = carpeta / "cotizacion.json" if (carpeta / "cotizacion.json").exists() else RAIZ / "cotizaciones" / "_plantilla" / "cotizacion.json"
    base = json.load(open(base_ruta, encoding="utf-8"))
    global FECHA_REF
    hoy = FECHA_REF = base.get("parametros", {}).get("fecha_referencia", "") or ""
    items, informe = [], [f"# Precotización automática — {base.get('codigo', carpeta.name)}", "",
                          "Generada por `herramientas/precotizar.py`, sin IA. **Borrador: revisar los SIMILAR, SIN PRECIO, estimados y ⚠ antes de usarla.**", "",
                          "## 1. Materiales", "", "| Pos | Ítem | Resultado | Precio | Fecha y tipo | Diferencias / faltantes |", "|---|---|---|---|---|---|"]
    N = float(base.get("parametros", {}).get("N", 1) or 1)
    par = base.get("parametros", {}) or {}
    eq0 = base.get("equipo", {}) or {}
    import estimar_horas
    texto_eq = f"{eq0.get('singular', '')} {base.get('titulo', '')}"
    tipo_eq = eq0.get("tipo") or estimar_horas.tipo_de(texto_eq)
    # prefabricado de piping (spools por pulgada, MO vendida sola): pulgada diametral, tarifa de prefabricado de terceros,
    # sin horas de ingeniería ni montaje y pintura aparte por m² (CTRL-CA01)
    prefab = par.get("modo") == "prefabricado" or tipo_eq == "prefabricado"
    pintura_aparte = bool(par.get("pintura_aparte", prefab))
    canos_m = {}
    for n, r in enumerate(filas, 1):
        it, fila = material(r, n)
        items.append(it)
        informe.append(fila)
        if it["unidad"] == "m" and it["fuentes"][0]["precio"] and re.search(r"\bcano\b|\bcanos\b|\btubo\b", norm(it["descripcion"])):
            canos_m.setdefault((dn_de(r["diametro"]), norm(r["serie_sch"]), norm(r["material"]), it["fuentes"][0]["proveedor"]), []).append((it, r))
    # tuercas: si el espárrago elegido ya trae tuercas ("c/2 tuercas", "juego"), las tuercas del plano van en 0 (CTRL-P02)
    con_tuercas = [i for i in items if re.search(r"esparrago|bulon", norm(i["descripcion"])) and re.search(r"c/ ?\d? ?tuercas?|con \d? ?tuercas?|\bjuego\b|\bjgo\b|\+ ?\d? ?tuercas?", norm(ELEGIDO.get(i["id"], "")))]
    if con_tuercas:
        for i in items:
            if re.match(r"tuercas?\b", norm(i["descripcion"])) and i["fuentes"][0]["precio"]:
                i["fuentes"] = [{"tipo": "cot", "precio": 0, "proveedor": "Incluidas en el precio del espárrago", "origen": "—", "fecha": FECHA_REF or date.today().isoformat(),
                                 "coincide": "igual", "diferencia": f"el precio de la pos {', '.join(x['pos'] for x in con_tuercas)} ya trae las tuercas"}]
                i["provee"] = "incluido"
                informe.append(f"| {i['pos']} | {i['descripcion'][:45]} | INCLUIDAS EN EL ESPÁRRAGO | 0 | — | el precio elegido para los espárragos ({', '.join(x['pos'] for x in con_tuercas)}) trae tuercas: confirmar |")
    # el caño se compra por barra entera: los tramos del mismo caño se juntan (CTRL-P02: 8 tramos de 3" compraban 8 barras)
    # y lo que sobra va en una fila aparte de compra extra (como la 14b de la CAPEX). Barras de 12 m desde 3" (CTRL-TS01,
    # SK01, CA01). Menos de 0,5 m en total sale de recortes del stock (CTRL-TS01: 5,9 m de 1½" sch 160 para usar 0,1 m).
    for (d, _, _, _), grupo in canos_m.items():
        it, r = grupo[-1]
        B = barra_m(r["diametro"])
        total = sum(g[0]["cantidad"] for g in grupo) * N
        pos = ", ".join(g[0]["pos"] for g in grupo)
        if total < 0.5:
            informe.append(f"| {it['pos']}b | Caño de la pos {pos}: {fmtg(total)} m en total | sin compra extra | | | menos de 0,5 m: sale de recortes del stock (confirmar) |")
            continue
        barras = math.ceil(total / B - 1e-9)
        extra = round((barras * B - total) / N, 3)
        if extra <= 0:
            continue
        s0 = it["fuentes"][0]
        items.insert(items.index(it) + 1, {**json.loads(json.dumps(it)), "id": it["id"] + "B", "pos": f"{it['pos']}b", "cantidad": extra,
                                           "descripcion": f"Completar barra de {fmtg(B)} m de la pos {pos} (compra mínima; sobrante, no va en el equipo)",
                                           "especificacion": f"{barras} barra(s) de {fmtg(B)} m para {fmtg(total)} m en {fmtg(N)} equipo(s); por equipo {fmtg(extra)} m"})
        informe.append(f"| {it['pos']}b | Completar barra de {fmtg(B)} m (pos {pos}) | compra extra | USD {fmt(s0['precio'], 2)}/m × {fmtg(extra)} m | | "
                       f"Se usan {fmtg(total)} m en {fmtg(N)} equipo(s) y se compran {fmtg(barras * B)} m. Borrar si hay sobrante en stock |")
    # 2. soldaduras
    s = soldaduras(filas, diametral=prefab)
    tar, fila_t = tarifa("soldadura", "soldadura piping", ("usado_en_cotizacion", "costo_propio"))
    if prefab:
        sp = servicio_catalogo("Soldadura", "USD/pulg-eq", ["tercero", "pulgada"])
        if sp:
            tar = float(sp["tarifa_unitaria_usd"] or sp["ultimo_precio_usd"])
            fila_t = {"concepto": f"prefabricado por pulgada diametral (tercero) {sp['codigo']}", "nota": f"{sp['proveedor'][:60]}: {sp['descripcion'][:80]}",
                      "fuente": sp["ruta_origen"][:200], "fecha": sp["fecha_ultimo_precio"]}
        rech = float(par.get("rechazo_pct", 5) or 0)
        if rech:
            s["pulg_eq"] = round(s["pulg_eq"] * (1 + rech / 100), 3)
            s["detalle"].append(f"+{fmtg(rech)}% por rechazos y reparaciones con RX 100% (parametros.rechazo_pct)")
    informe += ["", "## 2. Soldaduras (de la columna de extremos)", "",
                f"**{fmtg(s['juntas_bw'])} juntas a tope de taller + juntas SW y olets = {fmt(s['pulg_eq'], 2)} pulgadas equivalentes**"
                + (f" × USD {fmt(tar, 2)} ({fila_t['concepto']}, {fila_t['fecha']}) = USD {fmt(s['pulg_eq'] * tar, 2)}" if tar else ""), ""]
    informe += [f"- {d}" for d in s["detalle"]] + [f"- ⚠ {a}" for a in s["avisos"]]
    terc = None if prefab else mo_tercero(tipo_eq, eq0.get("diametro_pulg"), texto_eq)
    if terc and s["pulg_eq"] and tar:
        propia = round(s["pulg_eq"] * tar, 2)
        informe.append(f"- **MO de fabricación de un tercero con el mismo tipo de equipo:** {terc['codigo']} {terc['proveedor'][:40]}, USD {fmt(float(terc['ultimo_precio_usd']), 2)} "
                       f"({terc['fecha_ultimo_precio']}; {terc['descripcion'][:90]}). Se propone en lugar de la soldadura propia (USD {fmt(propia, 2)}, segunda fuente) "
                       f"y sin el montaje propio del antecedente. No incluye: {terc['no_incluye'] or 's/d'}.")
        items.append({"id": "S01", "pos": "MO", "grupo": "mo", "descripcion": "Fabricación (soldadura y armado) por tercero, mismo tipo de equipo",
                      "especificacion": f"{terc['descripcion'][:200]} · alternativa propia: {fmt(s['pulg_eq'], 2)} pulg-eq × USD {fmtg(tar)}", "cantidad": 1, "unidad": "gl",
                      "fuentes": [{"tipo": "cot", "precio": float(terc["ultimo_precio_usd"]), "proveedor": f"{terc['proveedor'][:60]} · {terc['codigo']}", "codigo": terc["codigo"],
                                   "origen": terc["ruta_origen"][:200], "fecha": terc["fecha_ultimo_precio"], "coincide": "similar",
                                   "diferencia": f"trabajo del mismo tipo ({terc['equipo_referencia'][:60]}); confirmar alcance y tamaño con el tercero"},
                                  {"tipo": "ant", "precio": propia, "proveedor": f"Soldadura propia {fmt(s['pulg_eq'], 2)} pulg-eq × {fmtg(tar)} ({fila_t['concepto']})"[:200],
                                   "origen": fila_t["fuente"], "fecha": fin_de_mes(fila_t["fecha"]), "coincide": "similar", "diferencia": "alternativa propia"}]})
    elif s["pulg_eq"] and tar:
        items.append({"id": "S01", "pos": "MO", "grupo": "mo", "descripcion": f"Soldaduras: {fmtg(s['juntas_bw'])} a tope + SW y olets (calculado)",
                      "especificacion": "; ".join(s["detalle"])[:400], "cantidad": s["pulg_eq"], "unidad": "pulg",
                      "fuentes": [{"tipo": "ant", "precio": tar, "proveedor": f"{fila_t['concepto']}: {fila_t['nota']}"[:200], "origen": fila_t["fuente"],
                                   "fecha": fin_de_mes(fila_t["fecha"]), "coincide": "igual" if not s["avisos"] else "similar",
                                   **({"diferencia": " · ".join(s["avisos"])} if s["avisos"] else {})}]})
    # 3. servicios calculados
    canos = leer(TEC / "canos_peso_superficie.csv")
    m2, litros = 0.0, 0.0
    for r in filas:
        if not re.search(r"\bcano\b|\bniple|\btubo\b", norm(r["descripcion"])):
            continue
        dn, sch = dn_de(r["diametro"]), sch_de(r["serie_sch"]) or "40"
        fila = next((c for c in canos if abs(float(c["dn_pulg"]) - (dn or -1)) < 1e-6 and (c["schedule"] == sch or c["clase"] == sch)), None)
        l = largo_m(r["descripcion"]) or (cantidad_plano(r["cantidad"]) if norm(r["unidad"]).startswith("m") else None)
        if fila and l:
            q = cantidad_plano(r["cantidad"]) if not norm(r["unidad"]).startswith("m") else 1
            m2 += float(fila["m2_m_exterior"]) * l * q
            litros += float(fila["litros_m_interior"]) * l * q
    informe += ["", "## 3. Servicios calculados", ""]
    m2p = superficie_pintura(filas, m2)
    m2t = sum(v for _, v in m2p)
    pin = servicio_catalogo("Pintura", "USD/m2", ["granallado", "pintura"])
    if pin and m2t and pintura_aparte:
        t = float(pin["tarifa_unitaria_usd"])
        informe.append(f"- **Pintura aparte (no va en el total):** {fmt(m2t, 2)} m² × USD {fmt(t, 2)}/m² ({pin['servicio'][:50]}, {pin['fecha_ultimo_precio']}) = USD {fmt(m2t * t, 2)}. "
                       "Cotizarla como ítem aparte por m² (`parametros.pintura_aparte`).")
    elif pin and m2t:
        t = float(pin["tarifa_unitaria_usd"])
        det = " + ".join(f"{n} {fmt(v, 1)}" for n, v in m2p if v)
        informe.append(f"- **Pintura:** {fmt(m2t, 2)} m² ({det}) × USD {fmt(t, 2)}/m² ({pin['servicio'][:50]}, {pin['proveedor'][:30]}, {pin['fecha_ultimo_precio']}) = USD {fmt(m2t * t, 2)}.")
        items.append({"id": "S02", "pos": "PIN", "grupo": "servicio", "descripcion": "Granallado y pintura (m² calculados)",
                      "especificacion": f"{fmt(m2t, 2)} m² exteriores: {det}", "cantidad": round(max(m2t, 0.01), 3), "unidad": "m2",
                      "fuentes": [{"tipo": "ant", "precio": round(t, 2), "proveedor": f"{pin['proveedor'][:60]} · {pin['codigo']}", "codigo": pin["codigo"], "origen": pin["ruta_origen"][:200],
                                   "fecha": pin["fecha_ultimo_precio"], "coincide": "similar", "diferencia": "m² calculados (caños, accesorios por regla, envolvente y estructura); esquema de pintura a confirmar con el pliego"}]})
    # fabricación de la estructura (bastidor, patas, cunas): kg × tarifa por kg; antes no se calculaba (CTRL-M01, P01, C01)
    kg_est = 0.0
    for r in filas:
        d, q, u = norm(r["descripcion"]), cantidad_plano(r["cantidad"]), norm(r["unidad"])
        if re.search(INTERNOS, d):
            continue
        if perfil(r) and u.startswith("m") and not u.startswith("m2"):
            kg_est += perfil(r)[0] * q
        elif u == "kg" and re.search(r"perfil|upn|ipn|heb|bastidor|estructura|pata|cuna|soporte|skid|cancamo|angulo|planchuela", d):
            kg_est += q
    t_est, f_est = tarifa("estructura", "estructura", ("tercero", "costo_propio"))
    if kg_est and t_est:
        informe.append(f"- **Fabricación de la estructura:** {fmt(kg_est, 0)} kg × USD {fmtg(t_est)}/kg ({f_est['concepto']}, {f_est['fecha']}) = USD {fmt(kg_est * t_est, 2)}.")
        items.append({"id": "S05", "pos": "EST", "grupo": "mo", "descripcion": "Fabricación de la estructura (bastidor, patas, cunas y soportes)",
                      "especificacion": f"{fmt(kg_est, 0)} kg por equipo × tarifa por kg", "cantidad": round(kg_est, 1), "unidad": "kg",
                      "fuentes": [{"tipo": "ant", "precio": t_est, "proveedor": f"{f_est['concepto']}: {f_est['nota']}"[:200], "origen": f_est["fuente"],
                                   "fecha": fin_de_mes(f_est["fecha"]), "coincide": "similar",
                                   "diferencia": "kg de la tabla del plano; tarifa de un trabajo de estructura de skid"}]})
    # prueba hidráulica: las planillas 2025–2026 la cobran por hora de planta; horas = parametros.ph_horas (supuesto 6 h)
    ph = servicio_catalogo("Ensayos", "USD/hora", ["hidr"])
    horas = float(base.get("parametros", {}).get("ph_horas", 0) or 0)
    supuesto = not horas
    horas = horas or 6
    if ph and prefab:
        informe.append("- **Prueba hidráulica:** en el prefabricado va dentro de la pulgada (no se suma aparte).")
    elif ph:
        t = float(ph["tarifa_unitaria_usd"] or ph["ultimo_precio_usd"])
        informe.append(f"- **Prueba hidráulica:** {fmtg(horas)} h × USD {fmt(t, 2)}/h ({ph['servicio'][:40]}, {ph['fecha_ultimo_precio']}) = USD {fmt(horas * t, 2)}"
                       + (" · ⚠ horas supuestas: cargar `parametros.ph_horas`" if supuesto else "") + f" · volumen interior de caños y niples {fmt(litros, 1)} l.")
        items.append({"id": "S03", "pos": "PH", "grupo": "servicio", "descripcion": "Prueba hidráulica (horas de planta)",
                      "especificacion": f"{fmtg(horas)} h · volumen interior {fmt(litros, 1)} l", "cantidad": horas, "unidad": "h",
                      "fuentes": [{"tipo": "ant", "precio": t, "proveedor": f"{ph['proveedor'][:60]} · {ph['codigo']}", "codigo": ph["codigo"], "origen": ph["ruta_origen"][:200],
                                   "fecha": ph["fecha_ultimo_precio"], "coincide": "similar" if supuesto else "igual",
                                   **({"diferencia": "horas supuestas (6 h): confirmar"} if supuesto else {})}]})
    rx = float(base.get("parametros", {}).get("rx_pct", 0) or 0)
    if rx > 0 and s["juntas_bw"]:
        # tarifa vigente más reciente (hoy DB NDT 08-2026); los servicios se reparten entre los equipos de la serie
        # (se hacen juntos) y las juntas SW y los olets llevan tintas penetrantes (CTRL-C01/P01/M01)
        pch, pgr = (math.ceil(p * rx / 100) for p in s["placas"])
        t_ch, f_ch = tarifa("end", "placa radiografica chica", ("tercero",))
        t_gr, _ = tarifa("end", "placa radiografica grande", ("tercero",))
        t_sv, f_sv = tarifa("end", "servicio de radiografia", ("tercero",))
        t_lp, _ = tarifa("end", "servicio de liquidos penetrantes", ("tercero",))
        servs = max(1, math.ceil(N * (pch + pgr) / 40)) / N
        n_lp = (max(1, math.ceil(N * s["juntas_sw_olet"] / 30)) / N) if s.get("juntas_sw_olet") else 0
        costo = pch * (t_ch or 0) + pgr * (t_gr or 0) + servs * (t_sv or 0) + n_lp * (t_lp or 0)
        prov = f"{f_sv['concepto']} ({f_sv['fecha']}; {f_sv['fuente']})" if f_sv else "tarifas.csv"
        a_ch, _ = tarifa("end", "placa radiografica chica 9", ("tercero",))
        a_gr, _ = tarifa("end", "placa radiografica grande 9", ("tercero",))
        a_sv, f_asv = tarifa("end", "servicio de radiografia (antonelli)", ("tercero",))
        a_lp, _ = tarifa("end", "servicio de liquidos penetrantes (antonelli)", ("tercero",))
        alt = pch * (a_ch or 0) + pgr * (a_gr or 0) + servs * (a_sv or 0) + n_lp * (a_lp or 0)
        informe.append(f"- **Radiografía {fmtg(rx)}% y tintas:** {pch} placas chicas + {pgr} grandes + {fmt(servs, 2)} servicio(s) de RX + {fmt(n_lp, 2)} de LP por equipo = USD {fmt(costo, 2)} ({prov}).")
        items.append({"id": "S04", "pos": "RX", "grupo": "servicio", "descripcion": f"Radiografía {fmtg(rx)}% de las juntas a tope y tintas penetrantes en SW y olets",
                      "especificacion": f"{pch} placas chicas, {pgr} grandes, {fmt(servs, 2)} servicio(s) de RX y {fmt(n_lp, 2)} de LP por equipo (servicios repartidos en {fmtg(N)} equipos)",
                      "cantidad": 1, "unidad": "gl",
                      "fuentes": [{"tipo": "cot", "precio": round(costo, 2), "proveedor": prov[:200], "origen": f_sv["fuente"] if f_sv else "conocimiento/costos/tarifas.csv",
                                   "fecha": fin_de_mes(f_sv["fecha"]) if f_sv else date.today().isoformat(), "coincide": "igual"}]
                      + ([{"tipo": "cot", "precio": round(alt, 2), "proveedor": "NDT Antonelli (tarifas 11-2025), mismas placas y servicios", "origen": "fuentes_originales/antonelli_end_2025-11.pdf",
                           "fecha": "2025-11-03", "coincide": "igual"}] if alt and f_asv else [])})
        if alt:
            informe.append(f"  Con las tarifas de Antonelli (11-2025) serían USD {fmt(alt, 2)}: confirmar el proveedor de END con el cliente o la zona.")
    else:
        informe.append("- **Radiografía:** no se calculó (`parametros.rx_pct` = 0). Si el pliego la pide, cargar el porcentaje y volver a correr.")
    # horas de ingeniería, calidad y montaje: del antecedente más parecido (estimar_horas.py)
    eq = eq0
    d_eq = eq.get("diametro_pulg") or max([dn_de(r["diametro"]) or 0 for r in filas] or [0]) or None
    mat_u = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] == "material")
    hh = None if prefab else estimar_horas.estimar(tipo_eq, d_eq, N, mat_u or None, EXCLUIR, s["pulg_eq"] or None, texto_eq)
    informe += ["", f"### Horas de ingeniería, calidad y montaje (estimadas: {tipo_eq}, {d_eq or '?'}\", {fmtg(N)} u, materiales USD {fmt(mat_u, 0)} por unidad)", ""]
    if prefab:
        informe.append("- Prefabricado: sin horas de ingeniería (los isométricos los da el cliente) ni de montaje; calidad, data book, movimientos y PH van "
                       "dentro de la pulgada. Si el pliego pide ingeniería o dossier aparte, cargarlos a mano.")
    elif hh and hh["nivel"] == "otro":
        informe.append(f"- ⚠ **No hay antecedente del mismo tipo ({tipo_eq}) ni de uno afín: no se suman horas.** Cargarlas a mano con el detalle de actividades. "
                       "Candidatos (de otro tipo, no usar sin revisar): " + " | ".join(hh["candidatos"]))
        hh = None
    if hh:
        if terc:
            hh["mont"] = None
            informe.append("- Montaje propio: no se suma porque la fabricación la hace el tercero; la prueba hidráulica va aparte (fila PH).")
        for k, pos, n in (("ing", "HH", "Ingeniería"), ("cal", "CAL", "Calidad y dossier"), ("mont", "ARM", "Montaje en planta (armado, movimientos" + (", prueba hidráulica" if hh["incluye_ph"] else "") + ")")):
            x = hh[k]
            if not x or not x["horas_u"]:
                continue
            informe.append(f"- **{n}:** {fmtg(x['horas_u'])} h × USD {fmtg(x['usd_h'])}/h = USD {fmt(x['horas_u'] * x['usd_h'], 2)} · {x['criterio']} · antecedente: {x['antecedente']}"
                           + (f" · rango del mismo tipo {fmtg(hh['rango'][k][0])}–{fmtg(hh['rango'][k][1])} h" if hh["rango"][k] else ""))
            items.append({"id": f"S1{len(pos)}{pos[0]}", "pos": pos, "grupo": "mo", "descripcion": f"Horas de {n.lower()} (estimadas del antecedente)",
                          "especificacion": f"{fmtg(x['horas_u'])} h por {eq.get('singular', 'equipo')} · {x['criterio']}", "cantidad": x["horas_u"], "unidad": "h",
                          "fuentes": [{"tipo": "est", "precio": x["usd_h"], "proveedor": "Horas propias ITT (tarifa del antecedente)",
                                       "origen": f"conocimiento/costos/horas_por_equipo.csv · {x['fila']['proyecto']} · {x['fila']['archivo']} · hoja {x['fila']['hoja']}"[:250],
                                       "fecha": x["fila"]["fecha"], "coincide": "similar",
                                       "diferencia": f"ESTIMADO del antecedente {x['antecedente']}"[:300]}]})
        if not hh["mismo_tipo"]:
            informe.append("- ⚠ No hay antecedente del mismo tipo: se usaron equipos afines del mismo grupo. Revisar las horas.")
        if hh["incluye_ph"] and hh["mont"] and any(i["pos"] == "PH" for i in items):
            items[:] = [i for i in items if i["pos"] != "PH"]
            informe.append("- La prueba hidráulica va dentro del montaje del antecedente: se sacó la fila PH para no cobrarla dos veces.")
        informe.append("- Candidatos: " + " | ".join(hh["candidatos"]))
    informe += ["", "## 4. A completar (no se puede calcular)", "",
                "**Lo que más mueve el número:** en el caso de control CTRL-F01 (filtro FM2 #300) la radiografía y tinta penetrante fueron "
                "el 40% del costo y las horas de ingeniería, calidad y montaje el 16%. No presentar un precio sin completarlas.",
                *(["- ⚠ **Radiografía en 0%:** confirmar con el pliego (en CTRL-F01 fue 100% + tinta penetrante, USD 1.804 por filtro)."] if not rx else []),
                "- ⚠ **Horas de ingeniería, calidad y montaje:** son estimadas del antecedente más parecido (punto 3): confirmarlas con el detalle de actividades del equipo.",
                "- Armado y montaje (mano de obra de armado roscado o de terceros con el mismo alcance: `buscar_servicio.py`).",
                "- Ingeniería, calidad y dossier · embalaje · flete (kilos en `controles_tablas.md` al armar) · insumos.",
                "- Plazo (camino crítico con `comercial/plazos_proveedores.csv`).",
                "- ⚠ **Repuestos** (puesta en marcha y 2 años, si el pliego los pide), **transporte a destino** y **póliza de caución** "
                "(YPF y la mayoría de las licitaciones la piden): no se calculan; en CTRL-TS01 sumaron USD 1.915 por equipo y en CTRL-SK01 la caución USD 459."]
    for i in items:  # precios con 2 decimales (decisión de Matías, 29-10-2026)
        for f in i["fuentes"]:
            if isinstance(f.get("precio"), float):
                f["precio"] = round(f["precio"], 2)
    total_mat = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] == "material")
    total_srv = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] != "material")
    sin = [i["pos"] for i in items if i["fuentes"][0]["precio"] == 0 and not i.get("provee")]
    sim = [i["pos"] for i in items if i["grupo"] == "material" and i["fuentes"][0]["coincide"] == "similar"]
    informe[3:3] = [f"**Resumen:** materiales USD {fmt(total_mat, 2)} por equipo · soldadura y servicios calculados USD {fmt(total_srv, 2)} · "
                    f"{len(sim)} similares ({', '.join(sim) or '—'}) · {len(sin)} sin precio ({', '.join(sin) or '—'}).", ""]
    if comparar and (carpeta / "cotizacion.json").exists():
        man = {i["pos"]: i for i in json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))["items"]}
        informe += ["", "## 5. Comparación con cotizacion.json (armada a mano)", "", "| Pos | Automático | A mano | Diferencia |", "|---|---|---|---|"]
        for i in items:
            m = man.get(i["pos"])
            if m:
                a, b = i["cantidad"] * i["fuentes"][0]["precio"], m["cantidad"] * m["fuentes"][0]["precio"]
                informe.append(f"| {i['pos']} | {fmt(a, 2)} | {fmt(b, 2)} | {fmt(a - b, 2, signo=True)} |")
        tm = sum(m["cantidad"] * m["fuentes"][0]["precio"] for m in man.values() if m["grupo"] == "material")
        informe.append(f"| **Materiales** | **{fmt(total_mat, 2)}** | **{fmt(tm, 2)}** | **{fmt(total_mat - tm, 2, signo=True)}** |")
    auto = {**{k: v for k, v in base.items() if k not in ("indices_congelados", "aprobacion")}, "items": items, "estado": "borrador",
            "nota_precotizacion": "Generado por precotizar.py: revisar precotizacion.md antes de usarlo como cotizacion.json"}
    json.dump(auto, open(carpeta / "cotizacion_auto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    (carpeta / "precotizacion.md").write_text("\n".join(informe) + "\n", encoding="utf-8")
    print(informe[3])
    print(f"→ {carpeta / 'cotizacion_auto.json'} y {carpeta / 'precotizacion.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--comparar", action="store_true", help="comparar con el cotizacion.json armado a mano")
    ap.add_argument("--excluir", action="append", default=[], help="no usar precios cuyo origen contenga este texto (repetible)")
    q = ap.parse_args()
    EXCLUIR.extend(q.excluir)
    main(q.carpeta, q.comparar)
