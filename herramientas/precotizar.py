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
import csv
import json
import math
import re
import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar_material import buscar  # noqa: E402
from catalogo_materiales import unidad_norm  # noqa: E402
from indice_proyectos import frac, norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TEC = RAIZ / "conocimiento" / "tecnico"
TIPO = {"lista": "lista", "compra": "stock", "stock (precio maestro)": "stock", "cotización": "cot", "planilla interna": "ant",
        "estimado (cepo)": "est"}
SERIES = {"150", "300", "600", "900", "1500", "2500", "2000", "3000", "6000", "9000"}
SCHEDULES = {"5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160", "STD", "XS", "XXS"}
OLETS = r"cupla|sockolet|threadolet|weldolet|elbowlet|latrolet|\bolet"


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def dn_de(txt):
    m = re.findall(r"(\d+\s\d/\d|\d+/\d+|\d+(?:[.,]\d+)?)", str(txt).replace('"', " "))
    try:
        return frac(m[0].replace(",", ".")) if m else None
    except (ValueError, ZeroDivisionError):
        return None


def sch_de(v):
    for p in re.split(r"[xX/ ]", str(v).upper()):
        if p in SCHEDULES:
            return p
    return ""


def serie_de(v):
    return next((p for p in re.split(r"[x/ ]", str(v)) if p in SERIES), "")


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
    if sc:
        partes.append(f"sch {sc}")
    partes += [r["material"], r["extremos"].replace("-M", "").replace("-H", ""), r.get("modelo_fabricante", "")]
    return " ".join(p for p in partes if p)


AJUSTE_DIRECTAS = 0.75
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
        otros = sorted((h for h in HISTORIAL.get(c["codigo"], []) if not excluido(h) and h["precio_usd"]), key=lambda h: h["fecha"])
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
                  + (f", la más cercana a {esp:g} mm" if esp else "") + ") +10% por recortes; no incluye corte, plegado ni rolado" + nota)


def kg_de(r):
    """Kilos por unidad de una pieza de chapa o perfil: escritos ("590 kg c/u"), perfil por metro, o virola π·D·L·e·7850."""
    t = norm(r["descripcion"])
    m = re.search(r"(\d+(?:[.,]\d+)?)\s?kg\s?(?:c/u|cada)", t)
    if m:
        return float(m.group(1).replace(",", ".")), "kg escritos en la descripción"
    if re.search(r"\bvirola", t) and dn_de(r["diametro"]) and largo_m(r["descripcion"]) and espesor_mm(r):
        D, L, e = dn_de(r["diametro"]) * 0.0254, largo_m(r["descripcion"]), espesor_mm(r) / 1000
        return round(math.pi * D * L * e * 7850, 1), f"π × {D:.3f} m × {L:g} m × {e * 1000:.2f} mm × 7.850 kg/m³"
    return None, ""


BARRA_M = 6.0  # largo de compra mínima de caño (barra); ver caso de control CTRL-F01


def rechazo(x, r):
    """Motivo por el que un similar no sirve como precio, o None. Diámetro hasta 1,6 veces contra alguno de los del plano
    (12"x3/4" → 12 o 3/4); serie hasta 2,6 veces (#3000 roscada no se cotiza con #300 bridada, CTRL-P01)."""
    difs = x[6]
    md = next((re.match(r'diametro: ([\d.]+)"', d) for d in difs if re.match(r'diametro: [\d.]+"', d)), None)
    pedidos = [dn_de(v) for v in re.split(r"\s*x\s*", str(r["diametro"]).lower()) if dn_de(v)]
    if md and pedidos and min(max(float(md.group(1)), d) / max(min(float(md.group(1)), d), 1e-9) for d in pedidos) > 1.6:
        return f"de otro diámetro ({md.group(1)}\")"
    ms = next((re.match(r"serie: (\d+) \(pedido (\d+)\)", d) for d in difs if re.match(r"serie: \d+ \(pedido \d+\)", d)), None)
    if ms and max(int(ms.group(1)), int(ms.group(2))) / max(min(int(ms.group(1)), int(ms.group(2))), 1) > 2.6:
        return f"de otra serie ({ms.group(1)} contra {ms.group(2)})"
    return None


def material(r, n):
    """Ítem de cotizacion.json para un renglón del plano, más el renglón del informe."""
    fam, at, _, faltan, res = buscar(texto_busqueda(r))
    res = sin_excluidos(res)
    cant, unidad = float(r["cantidad"] or 0), (r["unidad"] or "un").strip()
    l = largo_m(r["descripcion"])
    if fam == "CAN" and unidad_norm(unidad) == "un" and l:
        cant, unidad = round(cant * l, 3), "m"  # "caño longitud 1900 mm × 1" se compra por metro
    con_precio = [x for x in res if x[7]["ultimo_precio_usd"]]
    # orden: igual con precio real > similar con precio real > igual estimado (cepo) > similar estimado
    real = [x for x in con_precio if x[7]["tipo_precio"] != "estimado (cepo)"]
    est = [x for x in con_precio if x[7]["tipo_precio"] == "estimado (cepo)"]
    orden = [x for x in real if x[0]] + [x for x in real if not x[0]] + [x for x in est if x[0]] + [x for x in est if not x[0]]
    # se descartan los similares de otro diámetro o de otra clase de serie y se prueba el siguiente (CTRL-M01: una
    # esférica 4" PR sirve de referencia para una 4" PT; una 2" PT no)
    validos = [x for x in orden if x[0] or not rechazo(x, r)]
    rechazado = orden[0] if orden and not validos else None
    elegido = validos[0] if validos else None
    item = {"id": f"M{n:02d}", "pos": r["pos"], "grupo": "material",
            "descripcion": f"{r['descripcion'][:60]} {r['diametro']}".strip(), "cantidad": cant, "unidad": unidad,
            "especificacion": f"Plano: {r['diametro']} · {r['serie_sch']} · {r['material']} · {r['extremos']}" + (f" · {r['modelo_fabricante']}" if r.get("modelo_fabricante") else "")}
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
                precio, det = pf[0] * usd_kg, f"{pf[0]:g} kg/m (perfiles.csv) × USD {usd_kg:.2f}/kg; {motivo}"
            else:   # virola o pieza con kilos escritos: kg × (chapa + rolado si es virola)
                rol, f_rol = tarifa("fabricacion", "rolado de chapa", ("tercero",)) if re.search(r"\bvirola", norm(r["descripcion"])) else (None, None)
                precio = kgu * (usd_kg + (rol or 0))
                txt_rol = f" + rolado {rol:g}/kg ({f_rol['fuente'][:60]})" if rol else ""
                det = f"{kgu:g} kg ({como}) × (USD {usd_kg:.2f}/kg{txt_rol}); {motivo}"
            item["fuentes"] = [{"tipo": "est", "precio": round(precio, 2), "proveedor": "Precios de acero por kg (J. Elejondo)" + (" + rolado" if kgu and re.search(r"\bvirola", norm(r["descripcion"])) else ""),
                                "origen": fila["fuente"], "fecha": fila["fecha"], "coincide": "similar", "diferencia": det[:300]}]
            return item, (f"| {r['pos']} | {item['descripcion'][:45]} | ESTIMADO (por kg) | USD {precio:,.2f}/{unidad} | {fila['fecha']} | {det[:110]} |")
    if unidad_norm(unidad) == "kg" and not (elegido and elegido[0] and unidad_norm(elegido[7]["unidad"]) == "kg"):
        fila, motivo = acero_kg(r)
        if fila:
            item["fuentes"] = [{"tipo": "cot", "precio": float(fila["usd_kg_con_recortes"]), "proveedor": "Precios de acero (J. Elejondo)",
                                "origen": fila["fuente"], "fecha": fila["fecha"], "coincide": "similar", "diferencia": motivo}]
            return item, (f"| {r['pos']} | {item['descripcion'][:45]} | SIMILAR (acero por kg) | USD {float(fila['usd_kg_con_recortes']):,.2f}/kg | "
                          f"{fila['fecha']} cot | {motivo} |")
    if rechazado:
        c = rechazado[7]
        item["fuentes"] = [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO EN EL CATÁLOGO: pedir cotización", "origen": "—",
                            "fecha": date.today().isoformat(), "coincide": "sin_ref",
                            "diferencia": f"El más parecido es {rechazo(rechazado, r)} ({c['codigo']} {c['descripcion'][:50]}, USD {float(c['ultimo_precio_usd']):,.2f}): no sirve como precio"}]
        return item, f"| {r['pos']} | {item['descripcion'][:45]} | **SIN PRECIO** | — | — | el más parecido es {rechazo(rechazado, r)} ({c['codigo']}, USD {float(c['ultimo_precio_usd']):,.2f}): pedir cotización |"
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
            nota_u = f"el último precio ({precio:,.2f}) se aparta más de 40% de la mediana de sus últimos precios: se usa la mediana {med:,.2f}"
            precio = med
    if any(re.match(r"paso: reducido \(pedido total\)", d) for d in difs):
        precio *= 1.30
        nota_u = "; ".join(x for x in [nota_u, "esférica de paso reducido: se estima la de paso total × 1,30"] if x)
    uc, up = unidad_norm(c["unidad"]), unidad_norm(unidad)
    m = re.fullmatch(r"tira de (\d+) m", uc)
    if m and up == "m":
        precio, nota_u = precio / float(m.group(1)), f"precio de tira de {m.group(1)} m pasado a metro"
    elif uc and up and uc != up:
        nota_u = "; ".join(x for x in [nota_u, f"unidad distinta: catálogo por {uc}, plano por {up}"] if x)
    coincide = "igual" if igual and "unidad distinta" not in nota_u and "mediana" not in nota_u else "similar"
    dif = "; ".join(difs + ([nota_u] if nota_u else []))
    tipo = TIPO.get(c["tipo_precio"], "ant")
    item["fuentes"] = [{"tipo": tipo, "precio": round(precio, 4), "proveedor": f"{c['proveedor'][:70]} · {c['codigo']}",
                        "origen": (c["ruta_origen"] + (" · " + c["archivo_origen"] if c["archivo_origen"] else ""))[:200],
                        "fecha": c["fecha_ultimo_precio"], "coincide": coincide, **({"diferencia": dif} if coincide == "similar" else {})}]
    if fam == "VAL" and "taval" in norm(c.get("marca", "") + " " + c["proveedor"]):
        item["taval"] = True  # válvula Taval: va con el factor de válvulas Taval (parametros.FTV)
    estado = "IGUAL" if coincide == "igual" else "SIMILAR"
    if tipo == "est":
        estado += " (estimado cepo)"
    if c.get("alerta"):
        estado += " ⚠"
    fila = (f"| {r['pos']} | {item['descripcion'][:45]} | {estado} | {precio:,.2f} / {unidad} | {c['fecha_ultimo_precio']} · {c['tipo_precio']} | "
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
FACTOR_ACCESORIOS = 3.0  # m² del piping completo (bridas, accesorios, válvulas) ≈ 3 × m² de caños y niples (CTRL-M01/P01/C01: 1,0 a 6,2)
M2_POR_KG_ESTRUCTURA = 0.030  # 30 m²/t: perfiles livianos (UPN 140 = 32,5 m²/t) y chapas de apoyo
INTERNOS = r"bafle|deflector|separador de niebla|interno|elemento filtrante|placa apoyo|viruta|refuerzo"


def perfil(r):
    """(kg/m, m²/m) de un perfil nombrado en la descripción (UPN 140, IPN 120, HEB 200…), de tecnico/perfiles.csv."""
    global PERFILES
    if PERFILES is None:
        PERFILES = {norm(x["designacion"]).replace(" ", ""): (float(x["kg_por_m"]), float(x["m2_por_m"] or 0)) for x in leer(TEC / "perfiles.csv")}
    m = re.search(r"\b(upn|ipn|heb|hea|ipe|upe)\s*(\d+)", norm(r["descripcion"]))
    return PERFILES.get(f"{m.group(1)}{m.group(2)}") if m else None


def superficie_pintura(filas, m2_canos):
    """m² exteriores a pintar: caños y niples (tabla) × FACTOR_ACCESORIOS si hay bridas o accesorios; envolvente de
    virolas (π·D·L) y casquetes (≈1,09·D²); estructura por kg o por metro de perfil. Antes solo se contaban los caños
    (CTRL-T01, C01, P01, M01: −73% a −94%)."""
    hay_acc = any(re.search(r"brida|tee|codo|reduc|valvula|cupla", norm(r["descripcion"])) for r in filas)
    piping = m2_canos * (FACTOR_ACCESORIOS if hay_acc else 1)
    env = est = 0.0
    for r in filas:
        d, q, u = norm(r["descripcion"]), float(r["cantidad"] or 0), norm(r["unidad"])
        D = (dn_de(r["diametro"]) or 0) * 0.0254
        if re.search(r"\bvirola", d) and D and largo_m(r["descripcion"]):
            env += math.pi * D * largo_m(r["descripcion"]) * q
        elif re.search(r"casquete|cabezal", d) and D:
            env += 1.09 * D * D * q
        elif re.search(INTERNOS, d):
            continue
        elif perfil(r) and u.startswith("m") and not u.startswith("m2"):
            est += perfil(r)[1] * q
        elif u == "kg" and re.search(r"perfil|upn|ipn|heb|bastidor|estructura|pata|cuna|soporte|skid|chapa|cancamo|angulo|planchuela", d):
            est += q * M2_POR_KG_ESTRUCTURA
    return [("caños y niples" + (f" × {FACTOR_ACCESORIOS:g} por bridas, accesorios y válvulas" if hay_acc else ""), piping),
            ("envolvente", env), ("estructura", est)]


def soldaduras(filas):
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
    for r in filas:
        if r in por_metro:
            continue
        ext = r["extremos"].upper().replace("-M", "").replace("-H", "")
        toks = [t.strip() for t in re.split(r"[/]", ext) if t.strip()]
        d = norm(r["descripcion"])
        if len(toks) == 1:
            n_ext = 3 if re.search(r"\btee\b|\bte\b", d) else (1 if re.search(r"casquete|\bcap\b|brida|" + OLETS, d) else 2)
            toks = toks * n_ext
        n_bw, n_sw = toks.count("BW"), toks.count("SW")
        if not (n_bw or n_sw):
            continue
        q = float(r["cantidad"] or 0)
        dn, sch = dn_de(r["diametro"]), sch_de(r["serie_sch"])
        f, pch, pgr = factor_espesor(dn, sch, tabla, espesor_mm(r))
        if re.search(OLETS, d):
            fa = 2.5 if "weldolet" in d else fac_acc.get("sockolets", 1.75)
            ds = [dn_de(x) for x in re.split(r"\s*x\s*", r["diametro"].lower()) if dn_de(x)]
            dn = min(ds) if ds else dn  # el olet se mide por la salida (12"x3/4" → 3/4"), no por el caño donde se suelda
            juntas_olet += (n_bw + n_sw) * q * (dn or 0) * fa
            n_sw_olet += (n_bw + n_sw) * q
            detalle.append(f"pos {r['pos']}: {int((n_bw + n_sw) * q)} junta(s) de {r['descripcion'][:25]} sobre caño × {dn:g}\" × {fa} = {(n_bw + n_sw) * q * dn * fa:.2f}")
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
        if re.search(r"\bvirola", d) and largo_m(r["descripcion"]):
            # costura longitudinal de la virola rolada: largo / (π · 25,4) pulgadas de diámetro equivalente (CTRL-T01)
            lon = q * largo_m(r["descripcion"]) * 1000 / (math.pi * 25.4)
            bw_eq += 2 * lon * f  # bw_eq se divide por 2 al final (cuenta extremos)
            detalle.append(f"pos {r['pos']}: costura longitudinal de {q:g} virola(s) de {largo_m(r['descripcion']) * 1000:g} mm = {lon:.1f} pulg-eq × {f:.4f}")
        if n_bw:
            detalle.append(f"pos {r['pos']}: {bw_taller:g} extremo(s) BW de taller ({n_bw:g} por unidad × {q:g}{f' − {campo:g} de campo por unidad' if campo else ''}{f' × {m_r:g} por el caño' if m_r != 1 else ''}) × {dn:g}\" × {f:.4f}")
        if n_sw:
            detalle.append(f"pos {r['pos']}: {n_sw * q:g} junta(s) SW × {dn:g}\" × {f:.4f}")
    juntas_bw = extremos_bw / 2
    total = bw_eq / 2 + juntas_sw + juntas_olet
    avisos = []
    if extremos_bw % 2 and not por_metro:
        avisos.append(f"Quedan {extremos_bw:g} extremos BW de taller (número impar): falta marcar algún extremo de campo o una pieza")
    if not hay_campo and extremos_bw:
        avisos.append("La tabla no tiene la columna extremos_campo: se supuso que TODOS los extremos BW se sueldan en taller. Confirmar en el dibujo cuáles quedan para campo")
    return {"juntas_bw": juntas_bw, "pulg_eq": round(total, 3), "detalle": detalle, "avisos": avisos, "placas": placas, "juntas_sw_olet": n_sw_olet}


def tarifa(rubro, texto, tipos=("costo_propio",)):
    """La tarifa vigente más reciente del rubro (tipos en orden de preferencia)."""
    filas = [r for r in leer(RAIZ / "conocimiento" / "costos" / "tarifas.csv")
             if r["rubro"] == rubro and texto in norm(r["concepto"]) and r["tipo"] in tipos and r["vigente"] == "si"]
    if not filas:
        return None, None
    r = max(filas, key=lambda r: (-tipos.index(r["tipo"]), r["fecha"]))
    return float(r["valor_usd"]), r


def servicio_catalogo(hoja, unidad, palabras):
    mejor = None
    for r in leer(RAIZ / "conocimiento" / "precios" / "catalogo_servicios.csv"):
        if r["hoja"].startswith(hoja) and r["ultimo_precio_usd"] and "ESTIMADO" not in r["alerta"] and not excluido(r) and \
                (unidad is None or r["unidad_tarifa"] == unidad) and all(p in norm(r["servicio"] + " " + r["descripcion"]) for p in palabras):
            if mejor is None or r["fecha_ultimo_precio"] > mejor["fecha_ultimo_precio"]:
                mejor = r
    return mejor


def main(carpeta, comparar=False):
    carpeta = Path(carpeta)
    filas = leer(carpeta / "pedido" / "lista_materiales_plano.csv")
    if not filas:
        sys.exit(f"No está {carpeta}/pedido/lista_materiales_plano.csv")
    base_ruta = carpeta / "cotizacion.json" if (carpeta / "cotizacion.json").exists() else RAIZ / "cotizaciones" / "_plantilla" / "cotizacion.json"
    base = json.load(open(base_ruta, encoding="utf-8"))
    hoy = base.get("parametros", {}).get("fecha_referencia", "")
    items, informe = [], [f"# Precotización automática — {base.get('codigo', carpeta.name)}", "",
                          "Generada por `herramientas/precotizar.py`, sin IA. **Borrador: revisar los SIMILAR, SIN PRECIO, estimados y ⚠ antes de usarla.**", "",
                          "## 1. Materiales", "", "| Pos | Ítem | Resultado | Precio | Fecha y tipo | Diferencias / faltantes |", "|---|---|---|---|---|---|"]
    N = float(base.get("parametros", {}).get("N", 1) or 1)
    for n, r in enumerate(filas, 1):
        it, fila = material(r, n)
        items.append(it)
        informe.append(fila)
        # el caño se compra por barra entera (6 m): lo que sobra va en una fila aparte de compra extra (como la 14b de la CAPEX)
        s = it["fuentes"][0]
        if it["unidad"] == "m" and s["precio"] and re.search(r"\bcano\b|\bcanos\b|\btubo\b", norm(it["descripcion"])) and 0 < it["cantidad"] * N < BARRA_M * math.ceil(it["cantidad"] * N / BARRA_M):
            barras = math.ceil(it["cantidad"] * N / BARRA_M)
            extra = round((barras * BARRA_M - it["cantidad"] * N) / N, 3)
            items.append({**json.loads(json.dumps(it)), "id": it["id"] + "B", "pos": f"{it['pos']}b", "cantidad": extra,
                          "descripcion": f"Completar barra de {BARRA_M:g} m de la pos {it['pos']} (compra mínima; sobrante, no va en el equipo)",
                          "especificacion": f"{barras} barra(s) de {BARRA_M:g} m para {it['cantidad'] * N:g} m en {N:g} equipo(s); por equipo {extra:g} m"})
            informe.append(f"| {it['pos']}b | Completar barra de {BARRA_M:g} m (compra mínima) | compra extra | USD {s['precio']:,.2f}/m × {extra:g} m | | "
                           f"Se usan {it['cantidad'] * N:g} m en {N:g} equipo(s) y se compran {barras * BARRA_M:g} m. Borrar si hay sobrante en stock |")
    # 2. soldaduras
    s = soldaduras(filas)
    tar, fila_t = tarifa("soldadura", "soldadura piping", ("usado_en_cotizacion", "costo_propio"))
    informe += ["", "## 2. Soldaduras (de la columna de extremos)", "",
                f"**{s['juntas_bw']:g} juntas a tope de taller + juntas SW y olets = {s['pulg_eq']:.2f} pulgadas equivalentes**"
                + (f" × USD {tar:.2f} ({fila_t['concepto']}, {fila_t['fecha']}) = USD {s['pulg_eq'] * tar:,.2f}" if tar else ""), ""]
    informe += [f"- {d}" for d in s["detalle"]] + [f"- ⚠ {a}" for a in s["avisos"]]
    if s["pulg_eq"] and tar:
        items.append({"id": "S01", "pos": "MO", "grupo": "mo", "descripcion": f"Soldaduras: {s['juntas_bw']:g} a tope + SW y olets (calculado)",
                      "especificacion": "; ".join(s["detalle"])[:400], "cantidad": s["pulg_eq"], "unidad": "pulg",
                      "fuentes": [{"tipo": "ant", "precio": tar, "proveedor": f"{fila_t['concepto']}: {fila_t['nota']}"[:200], "origen": fila_t["fuente"],
                                   "fecha": fila_t["fecha"] if len(fila_t["fecha"]) > 7 else fila_t["fecha"] + "-31", "coincide": "igual" if not s["avisos"] else "similar",
                                   **({"diferencia": " · ".join(s["avisos"])} if s["avisos"] else {})}]})
    # 3. servicios calculados
    canos = leer(TEC / "canos_peso_superficie.csv")
    m2, litros = 0.0, 0.0
    for r in filas:
        if not re.search(r"\bcano\b|\bniple|\btubo\b", norm(r["descripcion"])):
            continue
        dn, sch = dn_de(r["diametro"]), sch_de(r["serie_sch"]) or "40"
        fila = next((c for c in canos if abs(float(c["dn_pulg"]) - (dn or -1)) < 1e-6 and (c["schedule"] == sch or c["clase"] == sch)), None)
        l = largo_m(r["descripcion"]) or (float(r["cantidad"]) if norm(r["unidad"]).startswith("m") else None)
        if fila and l:
            q = float(r["cantidad"]) if not norm(r["unidad"]).startswith("m") else 1
            m2 += float(fila["m2_m_exterior"]) * l * q
            litros += float(fila["litros_m_interior"]) * l * q
    informe += ["", "## 3. Servicios calculados", ""]
    m2p = superficie_pintura(filas, m2)
    m2t = sum(v for _, v in m2p)
    pin = servicio_catalogo("Pintura", "USD/m2", ["granallado", "pintura"])
    if pin and m2t:
        t = float(pin["tarifa_unitaria_usd"])
        det = " + ".join(f"{n} {v:.1f}" for n, v in m2p if v)
        informe.append(f"- **Pintura:** {m2t:.2f} m² ({det}) × USD {t:.2f}/m² ({pin['servicio'][:50]}, {pin['proveedor'][:30]}, {pin['fecha_ultimo_precio']}) = USD {m2t * t:,.2f}.")
        items.append({"id": "S02", "pos": "PIN", "grupo": "servicio", "descripcion": "Granallado y pintura (m² calculados)",
                      "especificacion": f"{m2t:.2f} m² exteriores: {det}", "cantidad": round(max(m2t, 0.01), 3), "unidad": "m2",
                      "fuentes": [{"tipo": "ant", "precio": round(t, 4), "proveedor": f"{pin['proveedor'][:60]} · {pin['codigo']}", "origen": pin["ruta_origen"][:200],
                                   "fecha": pin["fecha_ultimo_precio"], "coincide": "similar", "diferencia": "m² calculados (caños, accesorios por regla, envolvente y estructura); esquema de pintura a confirmar con el pliego"}]})
    # fabricación de la estructura (bastidor, patas, cunas): kg × tarifa por kg; antes no se calculaba (CTRL-M01, P01, C01)
    kg_est = 0.0
    for r in filas:
        d, q, u = norm(r["descripcion"]), float(r["cantidad"] or 0), norm(r["unidad"])
        if re.search(INTERNOS, d):
            continue
        if perfil(r) and u.startswith("m") and not u.startswith("m2"):
            kg_est += perfil(r)[0] * q
        elif u == "kg" and re.search(r"perfil|upn|ipn|heb|bastidor|estructura|pata|cuna|soporte|skid|cancamo|angulo|planchuela", d):
            kg_est += q
    t_est, f_est = tarifa("estructura", "estructura", ("tercero", "costo_propio"))
    if kg_est and t_est:
        informe.append(f"- **Fabricación de la estructura:** {kg_est:,.0f} kg × USD {t_est:g}/kg ({f_est['concepto']}, {f_est['fecha']}) = USD {kg_est * t_est:,.2f}.")
        items.append({"id": "S05", "pos": "EST", "grupo": "mo", "descripcion": "Fabricación de la estructura (bastidor, patas, cunas y soportes)",
                      "especificacion": f"{kg_est:,.0f} kg por equipo × tarifa por kg", "cantidad": round(kg_est, 1), "unidad": "kg",
                      "fuentes": [{"tipo": "ant", "precio": t_est, "proveedor": f"{f_est['concepto']}: {f_est['nota']}"[:200], "origen": f_est["fuente"],
                                   "fecha": f_est["fecha"] + ("-15" if len(f_est["fecha"]) == 7 else ""), "coincide": "similar",
                                   "diferencia": "kg de la tabla del plano; tarifa de un trabajo de estructura de skid"}]})
    # prueba hidráulica: las planillas 2025–2026 la cobran por hora de planta; horas = parametros.ph_horas (supuesto 6 h)
    ph = servicio_catalogo("Ensayos", "USD/hora", ["hidr"])
    horas = float(base.get("parametros", {}).get("ph_horas", 0) or 0)
    supuesto = not horas
    horas = horas or 6
    if ph:
        t = float(ph["tarifa_unitaria_usd"] or ph["ultimo_precio_usd"])
        informe.append(f"- **Prueba hidráulica:** {horas:g} h × USD {t:.2f}/h ({ph['servicio'][:40]}, {ph['fecha_ultimo_precio']}) = USD {horas * t:,.2f}"
                       + (" · ⚠ horas supuestas: cargar `parametros.ph_horas`" if supuesto else "") + f" · volumen interior de caños y niples {litros:.1f} l.")
        items.append({"id": "S03", "pos": "PH", "grupo": "servicio", "descripcion": "Prueba hidráulica (horas de planta)",
                      "especificacion": f"{horas:g} h · volumen interior {litros:.1f} l", "cantidad": horas, "unidad": "h",
                      "fuentes": [{"tipo": "ant", "precio": t, "proveedor": f"{ph['proveedor'][:60]} · {ph['codigo']}", "origen": ph["ruta_origen"][:200],
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
        informe.append(f"- **Radiografía {rx:g}% y tintas:** {pch} placas chicas + {pgr} grandes + {servs:.2f} servicio(s) de RX + {n_lp:.2f} de LP por equipo = USD {costo:,.2f} ({prov}).")
        items.append({"id": "S04", "pos": "RX", "grupo": "servicio", "descripcion": f"Radiografía {rx:g}% de las juntas a tope y tintas penetrantes en SW y olets",
                      "especificacion": f"{pch} placas chicas, {pgr} grandes, {servs:.2f} servicio(s) de RX y {n_lp:.2f} de LP por equipo (servicios repartidos en {N:g} equipos)",
                      "cantidad": 1, "unidad": "gl",
                      "fuentes": [{"tipo": "cot", "precio": round(costo, 2), "proveedor": prov[:200], "origen": f_sv["fuente"] if f_sv else "conocimiento/costos/tarifas.csv",
                                   "fecha": (f_sv["fecha"] + "-14") if f_sv and len(f_sv["fecha"]) == 7 else (f_sv["fecha"] if f_sv else date.today().isoformat()), "coincide": "igual"}]
                      + ([{"tipo": "cot", "precio": round(alt, 2), "proveedor": "NDT Antonelli (tarifas 11-2025), mismas placas y servicios", "origen": "fuentes_originales/antonelli_end_2025-11.pdf",
                           "fecha": "2025-11-03", "coincide": "igual"}] if alt and f_asv else [])})
        if alt:
            informe.append(f"  Con las tarifas de Antonelli (11-2025) serían USD {alt:,.2f}: confirmar el proveedor de END con el cliente o la zona.")
    else:
        informe.append("- **Radiografía:** no se calculó (`parametros.rx_pct` = 0). Si el pliego la pide, cargar el porcentaje y volver a correr.")
    # horas de ingeniería, calidad y montaje: del antecedente más parecido (estimar_horas.py)
    import estimar_horas
    eq = base.get("equipo", {}) or {}
    tipo_eq = eq.get("tipo") or estimar_horas.tipo_de(f"{eq.get('singular', '')} {base.get('titulo', '')}")
    d_eq = eq.get("diametro_pulg") or max([dn_de(r["diametro"]) or 0 for r in filas] or [0]) or None
    mat_u = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] == "material")
    hh = estimar_horas.estimar(tipo_eq, d_eq, N, mat_u or None, EXCLUIR, s["pulg_eq"] or None)
    informe += ["", f"### Horas de ingeniería, calidad y montaje (estimadas: {tipo_eq}, {d_eq or '?'}\", {N:g} u, materiales USD {mat_u:,.0f} por unidad)", ""]
    if hh:
        for k, pos, n in (("ing", "HH", "Ingeniería"), ("cal", "CAL", "Calidad y dossier"), ("mont", "ARM", "Montaje en planta (armado, movimientos" + (", prueba hidráulica" if hh["incluye_ph"] else "") + ")")):
            x = hh[k]
            if not x or not x["horas_u"]:
                continue
            informe.append(f"- **{n}:** {x['horas_u']:g} h × USD {x['usd_h']:g}/h = USD {x['horas_u'] * x['usd_h']:,.2f} · {x['criterio']} · antecedente: {x['antecedente']}"
                           + (f" · rango del mismo tipo {hh['rango'][k][0]:g}–{hh['rango'][k][1]:g} h" if hh["rango"][k] else ""))
            items.append({"id": f"S1{len(pos)}{pos[0]}", "pos": pos, "grupo": "mo", "descripcion": f"Horas de {n.lower()} (estimadas del antecedente)",
                          "especificacion": f"{x['horas_u']:g} h por {eq.get('singular', 'equipo')} · {x['criterio']}", "cantidad": x["horas_u"], "unidad": "h",
                          "fuentes": [{"tipo": "est", "precio": x["usd_h"], "proveedor": "Horas propias ITT (tarifa del antecedente)",
                                       "origen": f"conocimiento/costos/horas_por_equipo.csv · {x['fila']['proyecto']} · {x['fila']['archivo']} · hoja {x['fila']['hoja']}"[:250],
                                       "fecha": x["fila"]["fecha"], "coincide": "similar",
                                       "diferencia": f"ESTIMADO del antecedente {x['antecedente']}"[:300]}]})
        if not hh["mismo_tipo"]:
            informe.append("- ⚠ No hay antecedente del mismo tipo y tamaño: se usó el más parecido de otro tipo. Revisar las horas.")
        if hh["incluye_ph"] and any(i["pos"] == "PH" for i in items):
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
                "- Plazo (camino crítico con `comercial/plazos_proveedores.csv`)."]
    total_mat = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] == "material")
    total_srv = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] != "material")
    sin = [i["pos"] for i in items if i["fuentes"][0]["precio"] == 0]
    sim = [i["pos"] for i in items if i["grupo"] == "material" and i["fuentes"][0]["coincide"] == "similar"]
    informe[3:3] = [f"**Resumen:** materiales USD {total_mat:,.2f} por equipo · soldadura y servicios calculados USD {total_srv:,.2f} · "
                    f"{len(sim)} similares ({', '.join(sim) or '—'}) · {len(sin)} sin precio ({', '.join(sin) or '—'}).", ""]
    if comparar and (carpeta / "cotizacion.json").exists():
        man = {i["pos"]: i for i in json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))["items"]}
        informe += ["", "## 5. Comparación con cotizacion.json (armada a mano)", "", "| Pos | Automático | A mano | Diferencia |", "|---|---|---|---|"]
        for i in items:
            m = man.get(i["pos"])
            if m:
                a, b = i["cantidad"] * i["fuentes"][0]["precio"], m["cantidad"] * m["fuentes"][0]["precio"]
                informe.append(f"| {i['pos']} | {a:,.2f} | {b:,.2f} | {a - b:+,.2f} |")
        tm = sum(m["cantidad"] * m["fuentes"][0]["precio"] for m in man.values() if m["grupo"] == "material")
        informe.append(f"| **Materiales** | **{total_mat:,.2f}** | **{tm:,.2f}** | **{total_mat - tm:+,.2f}** |")
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
