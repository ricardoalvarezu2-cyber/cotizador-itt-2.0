"""Catálogo de materiales: todos los precios conocidos, separados por familia de material, con sus características,
el último precio de costo, su fecha y la ruta de dónde salió.

Uso: python herramientas/catalogo_materiales.py

Fuentes (etapa 1, sin IA):
  conocimiento/precios/lista_renar_2025-12.csv     lista de precios Renard (precio de lista)
  conocimiento/precios/stock_2024-11.csv           stock ITT: precio y fecha de la ÚLTIMA COMPRA de cada artículo
  conocimiento/precios/precios_componentes.csv     base de componentes (proveedor y fecha por renglón)
  conocimiento/precios/proveedores_2025/2026.csv   cotizaciones de proveedores (solo las que traen precio unitario)
  cotizaciones/*/cotizacion.json                   fuentes de precio cargadas en cotizaciones (no los estimados)

Salidas:
  conocimiento/precios/catalogo_materiales_historial.csv   un renglón por precio, con su clave de material
  conocimiento/precios/catalogo_materiales.csv             un renglón por material: último precio + historial
  conocimiento/precios/catalogo_materiales.xlsx            una hoja por familia, con sus columnas propias
Se busca con herramientas/buscar_material.py.

Reglas:
- Dos precios son del MISMO material solo si coinciden todas las características de la clave de su familia
  (p. ej. válvula: tipo, Ø, serie, material de cuerpo, trim, extremos). Si falta alguna, no se juntan.
- Último precio = el de fecha más reciente entre los de COSTO (cotización, compra, planilla interna, lista, stock).
  Los estimados no entran. Los precios en pesos se pasan a USD con el dólar BNA del mes (indices_ajuste.csv).
- Precio ajustado a hoy con el CPI de EE.UU. (mismo criterio que las cotizaciones).
"""
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm, diametros, series  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PRECIOS = RAIZ / "conocimiento" / "precios"
TEXTOS = RAIZ / "fuentes_originales" / "ofertas_texto"
Z = "Z:\\VENTAS\\OFERTAS Y LICITACIONES\\"

# ---------------------------------------------------------------- familias y columnas propias
FAMILIAS = {
    "VAL": ("Válvulas", ["tipo", "diametro", "serie", "material", "trim", "extremos", "paso", "norma", "marca_modelo"],
            ["tipo", "diametro", "serie", "material", "trim", "extremos"]),
    "AFO": ("Accesorios forjados (roscados / SW)", ["tipo", "diametro", "diametro2", "serie", "schedule", "material", "extremos"],
            ["tipo", "diametro", "diametro2", "serie", "schedule", "material", "extremos"]),
    "ABW": ("Accesorios a tope (BW)", ["tipo", "diametro", "diametro2", "schedule", "material", "norma"],
            ["tipo", "diametro", "diametro2", "schedule", "material"]),
    "BRI": ("Bridas", ["tipo", "diametro", "serie", "cara", "schedule", "material", "norma"],
            ["tipo", "diametro", "serie", "cara", "schedule", "material"]),
    "CAN": ("Caños", ["diametro", "schedule", "espesor_mm", "material", "costura", "revestimiento"],
            ["diametro", "schedule", "espesor_mm", "material", "costura", "revestimiento"]),
    "NIP": ("Niples", ["diametro", "schedule", "largo_mm", "extremos", "material"],
            ["diametro", "schedule", "largo_mm", "extremos", "material"]),
    "PER": ("Perfiles, chapas y estructura", ["tipo", "designacion", "espesor_mm", "material"],
            ["tipo", "designacion", "espesor_mm", "material"]),
    "INS": ("Instrumentos", ["tipo", "rango", "diametro", "conexion", "marca_modelo"],
            ["tipo", "rango", "conexion", "marca_modelo"]),
    "JUN": ("Juntas, bulonería y aislación", ["tipo", "diametro", "serie", "material", "medida", "extremos"],
            ["tipo", "diametro", "serie", "material", "medida", "extremos"]),
    "OTR": ("Otros e insumos", ["tipo"], []),
}
COMUNES = ["codigo", "familia", "descripcion", "unidad", "ultimo_precio_usd", "fecha_ultimo_precio", "tipo_precio",
           "proveedor", "ruta_origen", "archivo_origen", "ruta_repo", "precio_ajustado_hoy_usd", "precios_en_historial",
           "precio_min_usd", "precio_max_usd", "primera_fecha", "confianza_clasificacion"]
PRIORIDAD = {"cotización": 4, "compra": 4, "planilla interna": 3, "lista": 2, "stock (precio maestro)": 1}


def primero(rx, t, grupo=1):
    m = re.search(rx, t)
    return m.group(grupo) if m else ""


ABREV = [(r"\besf\b", "valvula esferica"), (r"\bpt\b", "paso total"), (r"\bred conc\b", "reduccion concentrica"),
         (r"\bred exc\b", "reduccion excentrica"), (r"\btrans presion\b", "transmisor de presion"), (r"\bret\b", "valvula retencion"),
         (r"\bescl\b", "valvula esclusa")]


def expandir(t):
    for rx, rep_ in ABREV:
        t = re.sub(rx, rep_, t)
    return t


def familia_de(t):
    if re.search(r"rosca con tuerca|union doble|union americana", t):
        return "AFO"
    if re.search(r"manometr|transmisor|termometr|termovaina|caudalimetr|coriolis|presostato|sensor|indicador de nivel|v-cone", t):
        return "INS"
    if re.search(r"junta|espiralad|ring joint|\bbx-?\d|\br\d{2}\b|esparrago|bulon|tuerca|kit dielectr|arandela", t):
        return "JUN"
    if re.search(r"\bbrida", t):
        return "BRI"
    if re.search(r"\bniple", t):
        return "NIP"
    if re.search(r"valvul|\bvalv\b|esferica|retencion|esclusa|\baguja\b|bloqueo y purga|\bpsv\b|mariposa|\bglobo\b", t):
        return "VAL"
    if re.search(r"\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|perfil|angulo|planchuela|\bchapa\b|hierro|tubo estructural", t):
        return "PER"
    if re.search(r"\bcano\b|\bcanos\b|tubo s/?c|tubo c/?c|\btubo\b|\bpipe\b", t):
        return "CAN"
    acc = re.search(r"\bcodo|\btee\b|\bte\b|reduccion|casquete|\bcupla|\btapon|\bbuje|union doble|entrerrosca|\btapa\b|olet\b|\bcurva", t)
    if acc:
        if re.search(r"\bbw\b|\bsch\b|\bxs\b|\bstd\b|a ?234|wpb|radio (largo|corto)|casquete|\bcurva", t):
            return "ABW"
        return "AFO"
    return "OTR"


def material_de(t):
    for rx, nombre in [(r"a ?860|wphy", "A860 WPHY"), (r"a ?403|wp ?304|wp ?316", "A403 (inox)"), (r"a ?350|lf2", "A350 LF2"),
                       (r"a ?333", "A333"), (r"a ?694|f ?65", "A694 F65"), (r"a ?194", "A194"),
                       (r"a ?216 ?(gr\.? ?)?wcb|\bwcb\b", "A216 WCB"), (r"a ?351|cf8m", "A351 CF8M"), (r"a ?182 ?f ?316|f316", "A182 F316"), (r"aisi ?316l?|\b316l?\b", "AISI 316"), (r"aisi ?304|\b304\b", "AISI 304"),
                       (r"duplex", "Dúplex"), (r"a ?312", "A312"), (r"a ?216 ?(gr\.? ?)?wcb|\bwcb\b", "A216 WCB"),
                       (r"a ?105", "A105"), (r"a ?234 ?(gr\.? ?)?wpb|\bwpb\b", "A234 WPB"), (r"a ?106", "A106 B"),
                       (r"api ?5l", "API 5L"), (r"a ?53", "A53"), (r"a ?516", "A516-70"), (r"a ?36\b", "A36"),
                       (r"f-?24\b", "F-24"), (r"a ?193", "A193 B7"), (r"galvaniz", "Galvanizado"), (r"bronce", "Bronce")]:
        if re.search(rx, t):
            return nombre
    if "inox" in t:
        return "Inoxidable"
    if "carbono" in t:
        return "Acero al carbono"
    return ""


def extremos_de(t):
    ext = [e for e, rx in (("NPT", r"\bnpt"), ("BSPT", r"bspt"), ("SW", r"\bsw\b|socket"), ("BW", r"\bbw\b|biselad|a tope"),
                           ("RTJ", r"\brtj\b|ring joint"), ("RF", r"\brf\b"), ("FF", r"\bff\b"), ("Bridado", r"bridad")) if re.search(rx, t)]
    return "/".join(ext)


def schedule_de(t):
    s = primero(r"\bsch\.? ?(\d{2,3}s?|xxs|xs|std)\b", t) or primero(r"\b(xxs|xs|std|extra pesado)\b", t)
    return {"xs": "80", "extra pesado": "80", "std": "40"}.get(s, s).upper()  # equivalencias hasta 10"


def atributos(t, fam):
    d = {}
    ds = diametros(t)
    if fam == "PER":
        d["tipo"] = primero(r"\b(upn|ipn|heb|hea|ipe|w|angulo|planchuela|chapa|tubo estructural)\b", t).upper()
        d["designacion"] = primero(r"\b(?:upn|ipn|heb|hea|ipe|w)\s?(\d{2,3}(?:x\d+)?)", t) or primero(r"(\d+(?:[.,]\d+)?\s?x\s?\d+(?:[.,]\d+)?(?:\s?x\s?\d+(?:[.,]\d+)?)?)", t)
        d["espesor_mm"] = primero(r"(?:esp\.?|espesor|e=)\s?(\d+(?:[.,]\d+)?)\s?mm", t) or primero(r"(\d+(?:[.,]\d+)?)\s?mm", t)
    else:
        ord_ds = []
        for m in re.finditer(r'(?<![\d/])(\d{1,2}(?: \d/\d)?|\d/\d)\s?(?:"|”|\'\'|pulg)', t):
            try:
                v = sum(float(p.split("/")[0]) / float(p.split("/")[1]) if "/" in p else float(p) for p in m.group(1).split())
            except ZeroDivisionError:
                continue
            if v not in ord_ds:
                ord_ds.append(v)
        ord_ds = ord_ds or ds
        if ord_ds:
            d["diametro"] = f"{ord_ds[0]:g}\""
            if len(ord_ds) > 1 and fam in ("AFO", "ABW") and re.search(r"reduc|buje|x", t):
                d["diametro2"] = f"{ord_ds[1]:g}\""
    sr = series(t)
    if sr:
        d["serie"] = sr[0]
    d["schedule"] = schedule_de(t)
    d["material"] = material_de(t)
    d["extremos"] = extremos_de(t)
    if not d.get("diametro") and fam in ("JUN", "VAL", "BRI", "AFO", "ABW", "NIP"):
        m = re.search(r"(?:junta \w+|esparrago|tuerca\w*(?: pesada)?|bulon|arandela|esferica(?: paso total)?|retencion|esclusa|brida \w+|codo|tee|niple)\s+(\d{1,2} \d/\d|\d/\d|\d{1,2})\b", t)
        if m:
            p_ = m.group(1)
            v = sum(float(a.split("/")[0]) / float(a.split("/")[1]) if "/" in a else float(a) for a in p_.split())
            d["diametro"] = f"{v:g}\""
    if fam == "VAL":
        d["tipo"] = primero(r"(esferica|retencion|esclusa|aguja|bloqueo y purga|globo|mariposa|seguridad|alivio|control|contrapresion|reguladora|tapon)", t)
        d["trim"] = primero(r"(trim ?\d+|asientos? (?:metalic\w*|ptfe|teflon|blando\w*)|ptfe|metal[- ]metal)", t)
        d["paso"] = "total" if re.search(r"paso total|full bore|\bfb\b", t) else ("reducido" if re.search(r"paso (reducido|nominal)|reduced", t) else "")
        d["norma"] = primero(r"(api ?6d|api ?602|api ?594|api ?6a|api ?608|b16\.34)", t).upper()
    elif fam == "AFO":
        d["tipo"] = primero(r"(codo 90|codo 45|codo|tee|te|media cupla|cupla para soldar|cupla|tapon|buje|union doble a golpe extensible|union doble extensible|union extensible|union doble a golpe|union doble rapida|union doble|rosca con tuerca|entrerrosca|tapa|thredolet|threadolet|sockolet)", t)
    elif fam == "ABW":
        d["tipo"] = primero(r"(codo radio largo 90|codo radio largo 45|codo radio corto 90|codo 90|codo 45|curva 45|curva|tee|te|reduccion concentrica|reduccion excentrica|reduccion|casquete|cap)", t)
        d["norma"] = primero(r"(b16\.9|b16\.28)", t).upper()
    elif fam == "BRI":
        d["tipo"] = primero(r"\b(wn|welding neck|slip ?on|so|ciega|blind|bl|lj|sw|roscada|lap joint|adaptadora|porta ?placa|instrumentacion)\b", t)
        d["cara"] = primero(r"\b(rtj|rf|ff)\b", t).upper()
        d["norma"] = primero(r"(b16\.5|b16\.47|api ?6a)", t).upper()
    elif fam == "CAN":
        d["espesor_mm"] = primero(r"x\s?(\d+(?:[.,]\d+)?)\s?mm", t) or primero(r"(\d+[.,]\d+)\s?mm", t) or primero(r"\bx\s?(\d+,\d+)", t)
        d["costura"] = "sin costura" if re.search(r"s/?c\b|sin costura|seamless", t) else ("con costura" if re.search(r"c/?c\b|con costura|erw", t) else "")
        d["revestimiento"] = primero(r"(tricapa\s?\w*|polipropileno|polietileno|galvanizado|epoxi)", t)
        if not d.get("diametro"):
            od = primero(r"(\d{2,3}[.,]\d)\s?x", t)
            if od:
                d["diametro"] = f"OD {od} mm"
    elif fam == "NIP":
        d["largo_mm"] = primero(r"(\d{2,4})\s?mm", t) or primero(r"x\s?(\d{2,4})\b", t)
    elif fam == "INS":
        d["tipo"] = primero(r"(manometro|transmisor de presion|transmisor de temperatura|transmisor|termometro|termovaina|caudalimetro|coriolis|presostato|sensor)", t)
        d["rango"] = primero(r"(\d+\s?[-–a]\s?\d+\s?(?:bar|psi|kg/cm2|kg|°c|c\b))", t)
        d["conexion"] = primero(r"conex\w*\s?(\d/\d|\d)\"?", t)
        d["marca_modelo"] = primero(r"\b(abb|rosemount|yokogawa|krohne|endress|wika|weisz|winters|ashcroft|emerson|siemens)\b", t).upper()
    elif fam == "JUN":
        d["tipo"] = primero(r"(junta monolitica|junta espiralada|espiralada|ring joint|kit dielectrico|junta dielectrica|junta|esparrago|bulon|tuerca|arandela)", t)
        d["medida"] = primero(r"(\d/\d\"?\s?x\s?\d+(?: \d/\d)?\"?)", t)
    else:
        d["tipo"] = " ".join(t.split()[:3])
    if fam == "VAL":
        d["marca_modelo"] = primero(r"\b(taval|abac|indave|danco|ingenieria en fluidos|cameron|velan|worcester|valvtronic|pecom|doma|duralitte|adita)\b", t).upper()
    return normalizar({k: v for k, v in d.items() if v})


SINONIMOS = {"welding neck": "wn", "blind": "ciega", "bl": "ciega", "slip on": "so", "slipon": "so", "lap joint": "lj",
             "codo radio largo 45": "codo 45", "curva 45": "codo 45", "codo radio largo 90": "codo 90", "te": "tee",
             "union doble extensible": "union doble a golpe extensible", "union extensible": "union doble a golpe extensible",
             "union doble rapida": "union doble a golpe", "thredolet": "threadolet"}


def normalizar(at):
    if at.get("tipo"):
        at["tipo"] = SINONIMOS.get(at["tipo"], at["tipo"])
    return at


def clave(fam, at):
    campos = FAMILIAS[fam][2]
    if not campos:
        return None
    oblig = {"VAL": ["tipo", "diametro", "serie"], "AFO": ["tipo", "diametro"], "ABW": ["tipo", "diametro"], "BRI": ["diametro", "serie"],
             "CAN": ["diametro"], "NIP": ["diametro", "largo_mm"], "PER": ["tipo", "designacion"], "INS": ["tipo", "rango"], "JUN": ["tipo", "diametro"]}[fam]
    if fam in ("VAL", "AFO", "ABW", "BRI", "CAN", "NIP") and not at.get("material"):
        return None  # sin material reconocido no se junta
    if fam == "CAN" and not (at.get("schedule") or at.get("espesor_mm")):
        return None
    if fam == "BRI" and not at.get("tipo"):
        return None
    if not all(at.get(c) for c in oblig):
        return None  # sin datos suficientes no se junta con otros
    return fam + "|" + "|".join(norm(at.get(c, "")) for c in campos)


# ---------------------------------------------------------------- tipo de cambio para precios en pesos
def tabla_dolar():
    ruta = RAIZ / "conocimiento" / "costos" / "indices_ajuste.csv"
    return {r["mes"][:7]: (float(r["dolar_bna"]), float(r["cpi_eeuu"])) for r in csv.DictReader(open(ruta, encoding="utf-8"))}


def en_mes(tabla, fecha, i):
    meses = sorted(tabla)
    m = (fecha or "")[:7]
    if not m or m < meses[0]:
        return tabla[meses[0]][i], True
    m = min(m, meses[-1])
    while m not in tabla:
        m = meses[[x < m for x in meses].index(False) - 1]
    return tabla[m][i], False


def num(v):
    try:
        return float(str(v).replace(",", ".")) if str(v).strip() not in ("", "-") else None
    except ValueError:
        return None


# ---------------------------------------------------------------- lectura de fuentes
def carpeta_repo(origen):
    """De 'APSA/15 · …' o 'APSA/15 - …' a la carpeta real en ofertas_texto."""
    o = origen.split("·")[0].strip()
    if (TEXTOS / o).is_dir():
        return o
    m = re.match(r"([^/]+)/(\d+)", o)
    if m:
        base = TEXTOS / m.group(1)
        if base.is_dir():
            for d in sorted(base.iterdir()):
                if re.match(rf"{m.group(2)}\s?[-.\s]", d.name):
                    return f"{m.group(1)}/{d.name}"
    return ""


def archivo_de(carpeta, proveedor):
    if not carpeta:
        return ""
    clave_p = norm(re.split(r"[\s(·,]", proveedor.strip())[0])
    if len(clave_p) < 3:
        return ""
    for p in sorted((TEXTOS / carpeta).rglob("*.txt")):
        if clave_p in norm(p.name):
            return str(p.relative_to(TEXTOS / carpeta))[:-4]
    return ""


def leer_fuentes():
    regs = []

    def add(desc, precio, moneda, fecha, tipo_precio, proveedor, ruta_origen, archivo, ruta_repo, unidad, extra=""):
        regs.append(dict(descripcion=desc.strip(), precio=precio, moneda=moneda or "USD", fecha=fecha, tipo_precio=tipo_precio,
                         proveedor=proveedor, ruta_origen=ruta_origen, archivo_origen=archivo, ruta_repo=ruta_repo, unidad=unidad, extra=extra))

    for r in csv.DictReader(open(PRECIOS / "lista_renar_2025-12.csv", encoding="utf-8")):
        if num(r["precio_usd"]):
            add(r["producto"], num(r["precio_usd"]), "USD", "2025-12-26", "lista", f"Renard (cód. {r['codigo']})",
                "fuentes_originales/renar_lista_2025-12.xlsx", f"código {r['codigo']}", "conocimiento/precios/lista_renar_2025-12.csv", r["unidad"])
    for r in csv.DictReader(open(PRECIOS / "stock_2024-11.csv", encoding="utf-8")):
        uc, fc = num(r["precio_ultima_compra"]), (r["fecha_ultima_compra"] or "")[:10]
        if uc and fc:
            add(r["descripcion"], uc, r["moneda"] or "USD", fc, "compra", f"Stock ITT · última compra (cód. {r['codigo']})",
                "fuentes_originales/stock_valorizado_2024-11.xlsx", f"código {r['codigo']}", "conocimiento/precios/stock_2024-11.csv", r["unidad"])
        elif num(r["precio_maestro_usd"]):
            add(r["descripcion"], num(r["precio_maestro_usd"]), "USD", "2024-11-01", "stock (precio maestro)", f"Stock ITT (cód. {r['codigo']})",
                "fuentes_originales/stock_valorizado_2024-11.xlsx", f"código {r['codigo']}", "conocimiento/precios/stock_2024-11.csv", r["unidad"])
    for r in csv.DictReader(open(PRECIOS / "precios_componentes.csv", encoding="utf-8")):
        if num(r["precio_usd"]):
            desc = " ".join(x for x in [r["descripcion"], r["dimension"], r["tipo"], r["schedule"] and f"SCH {r['schedule']}", r["serie"],
                                        r["material"], r["norma"]] if x)
            add(desc, num(r["precio_usd"]), "USD", (r["fecha"] or "2025-08-01")[:10], "cotización", r["proveedor"],
                "fuentes_originales/cotizacion_elementos_equipos_2026-03.xlsx", f"rubro {r['rubro']}" + (f" · cotización {r['cotizacion_proveedor']}" if r["cotizacion_proveedor"] not in ("", "-") else ""),
                "conocimiento/precios/precios_componentes.csv", r["unidad"])
    for anio in ("2026", "2025"):
        for r in csv.DictReader(open(PRECIOS / f"proveedores_{anio}.csv", encoding="utf-8")):
            cu = re.findall(r"(?:usd|u\$s|\$)?\s?([\d.]+(?:,\d+)?)\s?c/u", norm(r["detalle"]))
            if len(cu) != 1:
                continue  # presupuesto global o varios ítems: no da un precio unitario confiable
            v = cu[0].replace(".", "").replace(",", ".") if "," in cu[0] or cu[0].count(".") > 1 else cu[0]
            car = r["carpeta_cotizacion"]
            add(r["detalle"], num(v), r["moneda"], r["fecha"][:10], "cotización", r["proveedor"], Z + car.replace("/", "\\"),
                archivo_de(car, r["proveedor"]), f"fuentes_originales/ofertas_texto/{car}" if car else "", "un")
    for f in sorted((RAIZ / "cotizaciones").glob("COT*/cotizacion.json")):
        c = json.load(open(f, encoding="utf-8"))
        for it in c["items"]:
            if it["grupo"] != "material":
                continue
            for s in it["fuentes"]:
                if s["tipo"] in ("est", "lista", "stock") or not s.get("precio") or s.get("coincide") != "igual":
                    # lista y stock ya entran por su archivo; los similares describen lo pedido y no lo cotizado
                    continue
                tp = {"cot": "cotización", "lista": "lista", "stock": "compra", "ant": "planilla interna"}[s["tipo"]]
                car = carpeta_repo(s["origen"])
                add(f"{it['descripcion']} {it['especificacion']} · {s['proveedor']}", s["precio"], "USD", s["fecha"][:10], tp,
                    s["proveedor"].split(":")[0][:80], (Z + car.replace("/", "\\")) if car else s["origen"], archivo_de(car, s["proveedor"]),
                    f"fuentes_originales/ofertas_texto/{car}" if car else str(f.relative_to(RAIZ)), it["unidad"],
                    extra=f"usado en {c['codigo']} pos {it['pos']}")
    return regs


# ---------------------------------------------------------------- armado
def main():
    tabla = tabla_dolar()
    ref_cpi = tabla[max(tabla)][1]
    regs = leer_fuentes()
    hist = []
    for r in regs:
        t = expandir(norm(r["descripcion"]))
        fam = familia_de(t)
        at = atributos(t, fam)
        precio = r["precio"]
        nota = ""
        if r["moneda"].upper().startswith("ARS") or r["moneda"] == "$":
            tc, viejo = en_mes(tabla, r["fecha"], 0)
            precio = precio / tc
            nota = f"convertido de ARS a USD con dólar BNA {tc:,.0f}" + (" (fecha anterior a la tabla)" if viejo else "")
        cpi, viejo = en_mes(tabla, r["fecha"], 1)
        k = clave(fam, at)
        hist.append({**r, "familia": fam, "atributos": at, "clave": k, "precio_usd": round(precio, 4),
                     "precio_ajustado_hoy_usd": round(precio * ref_cpi / cpi, 4),
                     "nota": "; ".join(x for x in [nota, "ajuste parcial: fecha anterior a jul-2024" if viejo else "", r["extra"]] if x),
                     "confianza_clasificacion": "alta" if k and len(at) >= 4 else ("media" if k else "baja")})
    grupos = defaultdict(list)
    for i, h in enumerate(hist):
        grupos[h["clave"] or f"SOLO-{i}"].append(h)
    filas = []
    for n, (k, hs) in enumerate(sorted(grupos.items(), key=lambda kv: (kv[1][0]["familia"], kv[0])), 1):
        hs.sort(key=lambda h: (h["fecha"], PRIORIDAD.get(h["tipo_precio"], 0)), reverse=True)
        u = hs[0]
        precios = [h["precio_usd"] for h in hs]
        fila = {"codigo": f"{u['familia']}-{n:05d}", "familia": FAMILIAS[u["familia"]][0], "descripcion": u["descripcion"][:200],
                "unidad": u["unidad"], "ultimo_precio_usd": u["precio_usd"], "fecha_ultimo_precio": u["fecha"], "tipo_precio": u["tipo_precio"],
                "proveedor": u["proveedor"], "ruta_origen": u["ruta_origen"], "archivo_origen": u["archivo_origen"], "ruta_repo": u["ruta_repo"],
                "precio_ajustado_hoy_usd": u["precio_ajustado_hoy_usd"], "precios_en_historial": len(hs), "precio_min_usd": min(precios),
                "precio_max_usd": max(precios), "primera_fecha": hs[-1]["fecha"], "confianza_clasificacion": u["confianza_clasificacion"],
                "_fam": u["familia"], "_at": u["atributos"], "_nota": u["nota"]}
        for h in hs:
            h["codigo"] = fila["codigo"]
        filas.append(fila)
    # CSV de historial y de catálogo
    with open(PRECIOS / "catalogo_materiales_historial.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "familia", "clave", "fecha", "precio_usd", "precio_ajustado_hoy_usd", "tipo_precio", "proveedor", "descripcion",
                    "unidad", "ruta_origen", "archivo_origen", "ruta_repo", "atributos", "nota"])
        for h in sorted(hist, key=lambda h: (h["codigo"], h["fecha"]), reverse=False):
            w.writerow([h["codigo"], h["familia"], h["clave"] or "", h["fecha"], h["precio_usd"], h["precio_ajustado_hoy_usd"], h["tipo_precio"],
                        h["proveedor"], h["descripcion"], h["unidad"], h["ruta_origen"], h["archivo_origen"], h["ruta_repo"],
                        json.dumps(h["atributos"], ensure_ascii=False), h["nota"]])
    todos_at = sorted({c for v in FAMILIAS.values() for c in v[1]})
    with open(PRECIOS / "catalogo_materiales.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COMUNES + todos_at + ["nota"])
        for fl in filas:
            w.writerow([fl[c] for c in COMUNES] + [fl["_at"].get(c, "") for c in todos_at] + [fl["_nota"]])
    escribir_excel(filas)
    from collections import Counter
    c = Counter(fl["_fam"] for fl in filas)
    print(f"{len(hist)} precios → {len(filas)} materiales distintos")
    for k, (nombre, _, _) in FAMILIAS.items():
        print(f"  {k} {nombre:40} {c.get(k, 0):5}")
    print(f"con más de un precio en el historial: {sum(1 for fl in filas if fl['precios_en_historial'] > 1)}")


def escribir_excel(filas):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1D5F86")
    wb = Workbook(); wb.remove(wb.active)
    ancho = {"descripcion": 60, "ruta_origen": 50, "archivo_origen": 40, "ruta_repo": 45, "proveedor": 30, "nota": 40}

    def hoja(nombre, cols, rows):
        ws = wb.create_sheet(re.sub(r"[/\\?*\[\]:]", "-", nombre)[:31])
        for j, c in enumerate(cols, 1):
            x = ws.cell(1, j, c.replace("_", " ")); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[x.column_letter].width = ancho.get(c, 14)
        for i, r in enumerate(rows, 2):
            for j, v in enumerate(r, 1):
                ws.cell(i, j, v)
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = ws.dimensions
    base = ["codigo", "descripcion", "unidad", "ultimo_precio_usd", "fecha_ultimo_precio", "tipo_precio", "proveedor",
            "precio_ajustado_hoy_usd", "precios_en_historial", "precio_min_usd", "precio_max_usd", "ruta_origen", "archivo_origen", "ruta_repo",
            "confianza_clasificacion"]
    hoja("Todos", ["familia"] + base, [[fl["familia"]] + [fl[c] for c in base] for fl in filas])
    for k, (nombre, cols, _) in FAMILIAS.items():
        fs = [fl for fl in filas if fl["_fam"] == k]
        hoja(nombre, base[:2] + cols + base[2:], [[fl[c] for c in base[:2]] + [fl["_at"].get(c, "") for c in cols] + [fl[c] for c in base[2:]] for fl in fs])
    wb.save(PRECIOS / "catalogo_materiales.xlsx")


if __name__ == "__main__":
    main()
