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
- Siempre SIN IVA: un precio con IVA se divide por la alícuota (21% o 10,5%); si la fuente no dice nada, se toma sin IVA.
  La columna "iva" dice qué se hizo con cada precio.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import frac, norm, diametros, pulgadas, series  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
COMPRA_VIGENTE = "2022-01-01"
PRECIOS = RAIZ / "conocimiento" / "precios"
TEXTOS = RAIZ / "fuentes_originales" / "ofertas_texto"
Z = "Z:\\VENTAS\\OFERTAS Y LICITACIONES\\"

# ---------------------------------------------------------------- familias y columnas propias
FAMILIAS = {
    "VAL": ("Válvulas", ["tipo", "diametro", "serie", "material", "trim", "extremos", "paso", "norma", "marca", "modelo"],
            ["tipo", "diametro", "serie", "material", "trim", "extremos", "marca"]),
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
    "INS": ("Instrumentos", ["tipo", "rango", "diametro", "conexion", "marca", "modelo"],
            ["tipo", "rango", "conexion", "marca"]),
    "JUN": ("Juntas, bulonería y aislación", ["tipo", "diametro", "serie", "material", "medida", "extremos"],
            ["tipo", "diametro", "serie", "material", "medida", "extremos"]),
    "OTR": ("Otros e insumos", ["tipo"], []),
}
COMUNES = ["codigo", "familia", "descripcion", "unidad", "ultimo_precio_usd", "iva", "fecha_ultimo_precio", "tipo_precio",
           "proveedor", "ruta_origen", "archivo_origen", "ruta_repo", "precio_ajustado_hoy_usd", "precios_en_historial",
           "precio_min_usd", "precio_max_usd", "primera_fecha", "confianza_clasificacion"]
PRIORIDAD = {"cotización": 4, "compra": 4, "planilla interna": 3, "lista": 2, "stock (precio maestro)": 1}


def primero(rx, t, grupo=1):
    m = re.search(rx, t)
    return m.group(grupo) if m else ""


ABREV = [(r"\besf\b", "valvula esferica"), (r"\bpt\b", "paso total"), (r"\bred conc\b", "reduccion concentrica"),
         (r"\bred exc\b", "reduccion excentrica"), (r"\btrans presion\b", "transmisor de presion"), (r"\btrasmisor", "transmisor"), (r"\bret\b", "valvula retencion"),
         (r"\bescl\b", "valvula esclusa"), (r"\bbloq\.? y (pga|purga)\b", "bloqueo y purga"), (r"\bvalv byp\b|\bbyp\b", "valvula bloqueo y purga"),
         (r"\bept\b", "valvula esferica paso total"), (r"\bvalv reg\b", "valvula reguladora"), (r"a/fuego|a/fgo|\ba/f\b|\baf\b", "antifuego"),
         (r"\bgda\b", "guiada")]


def expandir(t):
    for rx, rep_ in ABREV:
        t = re.sub(rx, rep_, t)
    return t


NO_VALVULA = r"repuesto|kit de reparac|reparacion de|pistola|arrestallama|oxigeno|acetileno|soplete|regulador de gas|manguera|filtro|visor|cartucho"
PISTAS = [(r"valvul", "VAL"), (r"brida|figura 8", "BRI"), (r"esparrago|tuerca|junta|anillo de drenaje|anillo de purga", "JUN"),
          (r"cano", "CAN"), (r"niple", "NIP"), (r"chapa|semielaborado", "PER"), (r"casquete|codo|tee|reduccion", "ABW"),
          (r"cupla|tapon|buje|union doble|e\.? ?rosca", "AFO")]


def familia_de(t, pista=""):
    """Familia por la descripción; si no alcanza, por el grupo del stock o el rubro de la base de componentes."""
    f = familia_texto(t)
    if f == "OTR" and pista and not re.search(NO_VALVULA, t):
        for rx, fam in PISTAS:
            if re.search(rx, norm(pista)):
                return fam
    return f


def familia_texto(t):
    if re.search(r"rosca con tuerca|union doble|union americana", t):
        return "AFO"
    if re.search(r"cartucho|elemento filtrante|caja porta ?orificio|bomba dosificadora|tapa de cierre rapido|\bllave\b|argon|\bco2\b|\bled\b"
                 r"|u-?bolt|abrazadera|\bte (en caja|de |x \d)|manzanilla|yerba|\bcafe\b|azucar", t):
        return "OTR"
    if re.search(r"manometr|transmisor|trasmisor|termometr|termovaina|caudalimetr|coriolis|presostato|sensor|indicador de nivel|visor de nivel|v-cone", t):
        return "INS"
    if re.search(r"junta|espiralad|ring joint|\bbx-?\d|\br\d{2}\b|esparrago|bulon|tuerca|kit dielectr|arandela", t):
        return "JUN"
    if re.search(r"\bbrida", t):
        return "BRI"
    if re.search(r"\bniple", t):
        return "NIP"
    if re.search(r"valvul|\bvalv\b|esferica|retencion|esclusa|\baguja\b|bloqueo y purga|\bpsv\b|mariposa|\bglobo\b", t):
        return "OTR" if re.search(NO_VALVULA, t) else "VAL"
    if re.search(r"\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|perfil|angulo|planchuela|\bchapa\b|hierro|tubo estructural", t):
        return "PER"
    if re.search(r"\bcano\b|\bcanos\b|tubo s/?c|tubo c/?c|\btubo\b|\bpipe\b", t):
        return "CAN"
    acc = re.search(r"\bcodo|\btee\b|\bte\b|reduccion|casquete|\bcupla|\btapon|\bbuje|union doble|entrerrosca|\btapa\b|olet\b|\bcurva", t)
    if acc:
        if re.search(r"\b(2000|3000|6000|9000)\b|\bnpt\b|\bsw\b|socket", t) and not re.search(r"\bbw\b|a ?234|wpb", t):
            return "AFO"  # forjados roscados o SW (A105), aunque digan "radio corto"
        if re.search(r"\bbw\b|\bsch\b|\bxs\b|\bstd\b|a ?234|wpb|radio (largo|corto)|casquete|\bcurva", t):
            return "ABW"
        return "AFO"
    return "OTR"


# Fabricantes (no distribuidores): la marca sale de la descripción o del proveedor cuando el proveedor es el fabricante.
MARCAS = {"taval": "Taval", "abac": "ABAC", "indave": "Indave", "danco": "Danco", "ingenieria en fluidos": "Ingeniería en Fluidos",
          "duralitte": "Duralitte", "adita": "Adita", "pecom": "Pecom", "doma": "DOMA", "eqa": "EQA", "crosby": "Crosby",
          "fisher": "Fisher", "optimux": "Optimux", "bray": "Bray", "worcester": "Worcester", "valvtronic": "Valvtronic",
          "cameron": "Cameron", "velan": "Velan", "keystone": "Keystone", "wika": "WIKA", "weisz": "Weisz", "rosemount": "Rosemount",
          "abb": "ABB", "yokogawa": "Yokogawa", "krohne": "Krohne", "endress": "Endress+Hauser", "siemens": "Siemens",
          "winters": "Winters", "ashcroft": "Ashcroft", "emerson": "Emerson", "micro motion": "Micro Motion", "parker": "Parker",
          "swagelok": "Swagelok", "hoke": "Hoke", "kitz": "Kitz", "apollo": "Apollo", "genebre": "Genebre", "dhv": "DHV",
          "sferaco": "Sferaco", "mcdowell": "McDowell", "nuova giungas": "Nuova Giungas", "bonney": "Bonney Forge", "anderson greenwood": "Anderson Greenwood",
          "leser": "Leser", "farris": "Farris", "consolidated": "Consolidated", "dresser": "Dresser", "mercer": "Mercer"}
RX_MARCA = r"\b(" + "|".join(sorted(MARCAS, key=len, reverse=True)) + r")\b"


def marca_de(t, proveedor=""):
    m = primero(RX_MARCA, t) or primero(RX_MARCA, norm(proveedor))
    return MARCAS.get(m, "")


def modelo_de(t):
    return primero(r"\b(?:mod(?:elo)?|fig(?:ura)?)\.?\s?([a-z]{0,4}-?\d{2,5}[a-z0-9\-/]*)\b", t).upper()


def material_de(t):
    for rx, nombre in [(r"a ?860|wphy", "A860 WPHY"), (r"a ?403|wp ?304|wp ?316", "A403 (inox)"), (r"a ?350|lf2", "A350 LF2"),
                       (r"a ?333", "A333"), (r"a ?694|f ?65", "A694 F65"), (r"a ?194 ?(gr\.?|grado)? ?8ma?\b", "A194 8M"), (r"a ?194 ?(gr\.?|grado)? ?2h\b", "A194 2H"), (r"a ?194", "A194"),
                       (r"a ?193 ?(gr\.?|grado)? ?b ?8m", "A193 B8M"), (r"a ?193 ?(gr\.?|grado)? ?b ?7m", "A193 B7M"), (r"a ?320 ?(gr\.?)? ?l7", "A320 L7"),
                       (r"klingerit", "Klingerit"), (r"g-?10\b", "G10"),
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
                           ("RTJ", r"\brtj\b|\brj\b|ring joint"), ("RF", r"\brf\b"), ("FF", r"\bff\b"), ("Bridado", r"bridad")) if re.search(rx, t)]
    return "/".join(ext)


def schedule_de(t, diam=None):
    """XS = Sch 80 solo hasta 8" y STD = Sch 40 solo hasta 10" (ASME B36.10); más grandes son espesores distintos."""
    s = primero(r"\bsch\.? ?(\d{2,3}s?|xxs|xs|std)\b", t) or primero(r"\b(xxs|xs|std|extra pesado)\b", t)
    s = "xs" if s == "extra pesado" else s
    if s == "xs" and (diam is None or diam <= 8):
        return "80"
    if s == "std" and (diam is None or diam <= 10):
        return "40"
    return s.upper()


def atributos(t, fam, proveedor=""):
    d = {}
    ds = diametros(t)
    stock = None
    if fam == "PER":
        d["tipo"] = primero(r"\b(upn|ipn|heb|hea|ipe|w|angulo|planchuela|chapa|tubo estructural)\b", t).upper()
        d["designacion"] = primero(r"\b(?:upn|ipn|heb|hea|ipe|w)\s?(\d{2,3}(?:x\d+)?)", t) or primero(r"(\d+(?:[.,]\d+)?\s?x\s?\d+(?:[.,]\d+)?(?:\s?x\s?\d+(?:[.,]\d+)?)?)", t)
        d["espesor_mm"] = primero(r"(?:esp\.?|espesor|e=)\s?(\d+(?:[.,]\d+)?)\s?mm", t) or primero(r"(\d+(?:[.,]\d+)?)\s?mm", t)
    else:
        # formato del stock "ESF PT 4 300 RF" y formato "4#150RF": Ø y serie sin comillas ni #
        T = r"(?<![\d/.,#])(\d{1,2}(?: \d/\d)?|\d/\d)"
        stock = (re.search(T + r"\"?\s+(150|300|600|900|1500|2500|2000|3000|6000|9000)\s?(rf|rtj|rj|ff|npt|sw|bw)\b", t)
                 or re.search(T + r"\s?#\s?(150|300|600|900|1500|2500)(?!\d)", t)
                 or (fam in ("VAL", "JUN") and re.search(T + r"\s+(150|300|600|900|1500|2500)\b", t)))
        sin_comillas = re.search(r"\bnps ?(\d{1,2}(?: \d/\d)?|\d/\d)\b", t) or (fam in ("VAL", "AFO", "NIP", "JUN") and re.search(T + r"\s?(?:npt|bspt)\b", t))
        ord_ds = pulgadas(t) or ([frac(stock.group(1))] if stock else []) or ([frac(sin_comillas.group(1))] if sin_comillas else []) or ds
        if ord_ds:
            d["diametro"] = f"{ord_ds[0]:g}\""
            if len(ord_ds) > 1 and fam in ("AFO", "ABW") and re.search(r"reduc|buje|x", t):
                d["diametro2"] = f"{ord_ds[1]:g}\""
    sr = series(t)
    if sr:
        d["serie"] = sr[0]
    elif fam != "PER" and stock:
        d["serie"] = stock.group(2)
    d["schedule"] = schedule_de(t, float(d["diametro"][:-1]) if d.get("diametro", "").endswith('"') else None)
    d["material"] = material_de(t)
    d["extremos"] = extremos_de(t)
    if not d.get("diametro") and fam in ("JUN", "VAL", "BRI", "AFO", "ABW", "NIP"):
        m = re.search(r"(?:junta \w+|esparrago|tuerca\w*(?: pesada)?|bulon|arandela|esferica(?: paso total)?|retencion|esclusa|brida \w+|codo|tee|niple)\s+(\d{1,2} \d/\d|\d/\d|\d{1,2})\b", t)
        if m:
            v = frac(m.group(1))
            if 0.125 <= v <= 60:
                d["diametro"] = f"{v:g}\""
    if fam == "VAL":
        d["tipo"] = primero(r"(bloqueo y purga|esferica|retencion|esclusa|aguja|globo|mariposa|seguridad|alivio|control|contrapresion|reguladora|tapon|solenoide|sdv|3 vias|tres vias|purga|c/actuador)", t)
        d["trim"] = primero(r"(trim ?\d+|asientos? (?:metalic\w*|ptfe|teflon|blando\w*)|ptfe|metal[- ]metal)", t) or \
            (("asiento " + primero(r"\basto (tv|tr|tcc|ptfe|metal\w*)", t).upper()) if re.search(r"\basto (tv|tr|tcc|ptfe|metal)", t) else "")
        d["paso"] = "total" if re.search(r"paso total|full bore|\bfb\b", t) else ("reducido" if re.search(r"paso (reducido|nominal)|reduced", t) else "")
        d["norma"] = primero(r"(api ?6d|api ?602|api ?594|api ?6a|api ?608|b16\.34)", t).upper()
    elif fam == "AFO":
        d["tipo"] = primero(r"(codo 90|codo 45|codo|tee|te|media cupla|cupla para soldar|cupla|tapon|buje|union doble a golpe extensible|union doble extensible|union extensible|union doble a golpe|union doble rapida|union doble|rosca con tuerca|entrerrosca|tapa|thredolet|threadolet|sockolet)", t)
    elif fam == "ABW":
        d["tipo"] = primero(r"(codo radio largo 90|codo radio largo 45|codo radio corto 90|codo 90|codo 45|curva 45|curva|tee|te|reduccion concentrica|reduccion excentrica|reduccion|casquete|cap)", t)
        d["norma"] = primero(r"(b16\.9|b16\.28)", t).upper()
    elif fam == "BRI":
        d["tipo"] = primero(r"\b(wn|welding neck|slip ?on|so|ciega|blind|bl|lj|sw|roscada|lap joint|adaptadora|porta ?placa|instrumentacion)\b", t)
        if d["tipo"] in ("ciega", "blind", "bl") and re.search(r"c/ ?aguj|agujer|perforad|roscado", t):
            d["tipo"] = "ciega perforada"
        d["cara"] = primero(r"\b(rtj|rf|ff)\b", t).upper()
        d["norma"] = primero(r"(b16\.5|b16\.47|api ?6a)", t).upper()
    elif fam == "CAN":
        d["espesor_mm"] = (primero(r"sch\.? ?\w+ ?\((\d+[.,]\d+)\s?(?:mm)?\)", t) or primero(r"x\s?(\d+(?:[.,]\d+)?)\s?mm", t)
                           or primero(r"(?:esp\.?|espesor|e=)\s?(\d+(?:[.,]\d+)?)", t) or primero(r"\bx\s?(\d+,\d+)", t)).replace(",", ".")
        d["costura"] = "sin costura" if re.search(r"s/?c\b|sin costura|seamless", t) else ("con costura" if re.search(r"c/?c\b|con costura|erw", t) else "")
        d["revestimiento"] = primero(r"(tricapa\s?\w*|polipropileno|polietileno|galvanizado|epoxi)", t)
        if not d.get("diametro"):
            od = primero(r"(\d{2,3}[.,]\d)\s?x", t)
            if od:
                d["diametro"] = f"OD {od} mm"
    elif fam == "NIP":
        d["largo_mm"] = primero(r"(\d{2,4})\s?mm", t) or primero(r"x\s?(\d{2,4})\b", t)
    elif fam == "INS":
        d["tipo"] = primero(r"(manometro|transmisor de presion|transmisor de temperatura|transmisor de nivel|visor de nivel|transmisor|termometro|termovaina|caudalimetro|coriolis|presostato|sensor)", t)
        d["rango"] = primero(r"(\d+\s?[-–a]\s?\d+\s?(?:bar|psi|kg/cm2|kg|°c|c\b))", t)
        d["conexion"] = primero(r"conex\w*\s?(\d/\d|\d)\"?", t)
    elif fam == "JUN":
        d["tipo"] = primero(r"(junta monolitica|junta espiralada|espiralada|ring joint|kit dielectrico|kit junta aislamiento|kit de aislacion|junta dielectrica|junta plana|junta|esparrago|bulon|tuerca|arandela)", t)
        if d["tipo"] in ("kit junta aislamiento", "kit de aislacion"):
            d["tipo"] = "kit dielectrico"
        m = re.search(r"(?<![\d/])(\d{1,2}(?: \d/\d)?|\d/\d)\"?\s?x\s?(\d{1,2}(?: \d/\d)?)\"?", t) if d["tipo"] in ("esparrago", "bulon") else None
        d["medida"] = f"{m.group(1)} x {m.group(2)}" if m else ""
    else:
        d["tipo"] = " ".join(t.split()[:3])
    if fam in ("VAL", "INS"):
        d["marca"] = marca_de(t, proveedor)
        d["modelo"] = modelo_de(t)
    return normalizar({k: v for k, v in d.items() if v})


SINONIMOS = {"welding neck": "wn", "blind": "ciega", "bl": "ciega", "slip on": "so", "slipon": "so", "lap joint": "lj",
             "codo radio largo 45": "codo 45", "curva 45": "codo 45", "codo radio largo 90": "codo 90", "te": "tee",
             "union doble extensible": "union doble a golpe extensible", "union extensible": "union doble a golpe extensible",
             "union doble rapida": "union doble a golpe", "thredolet": "threadolet"}


def normalizar(at):
    if at.get("tipo"):
        at["tipo"] = SINONIMOS.get(at["tipo"], at["tipo"])
    return at


UNIDADES = [(r"^(-|)$", ""), (r"^(unid\w*|un|u|c/u|pza|pieza\w*|1)$", "un"), (r"^(m|mt|mts|metro\w*|ml)$", "m"), (r"^(m2|mts2|mtr2|mts²|m²)$", "m2"),
            (r"^(kg|kilo\w*)$", "kg"), (r"^(jgo|juego)$", "juego"), (r"^par$", "par"), (r"^caja$", "caja"), (r"^(paq|paquete)$", "paquete")]


def unidad_norm(u):
    """Unidad de precio normalizada. Un precio por metro nunca se junta con uno por unidad."""
    u = norm(u).strip(" .")
    m = re.fullmatch(r"(\d+) ?(m|mt|mts|metros)", u)
    if m:
        return f"tira de {m.group(1)} m"
    for rx, nombre in UNIDADES:
        if re.match(rx, u):
            return nombre
    return u


def clave(fam, at, unidad="un"):
    campos = FAMILIAS[fam][2]
    if not campos:
        return None
    oblig = {"VAL": ["tipo", "diametro", "serie"], "AFO": ["tipo", "diametro"], "ABW": ["tipo", "diametro"], "BRI": ["diametro", "serie"],
             "CAN": ["diametro"], "NIP": ["diametro", "largo_mm"], "PER": ["tipo", "designacion"], "INS": ["tipo", "rango"], "JUN": ["tipo", "diametro"]}[fam]
    if fam in ("VAL", "AFO", "ABW", "BRI", "CAN", "NIP") and not at.get("material"):
        return None  # sin material reconocido no se junta
    if fam == "CAN" and not (at.get("schedule") or at.get("espesor_mm")):
        return None
    if fam == "CAN" and at.get("schedule"):
        at = {**at, "espesor_mm": ""}  # con schedule, el espesor es el de la tabla: no separa
    if fam == "BRI" and not at.get("tipo"):
        return None
    if not all(at.get(c) for c in oblig):
        return None  # sin datos suficientes no se junta con otros
    return fam + "|" + "|".join(norm(at.get(c, "")) for c in campos) + "|" + unidad


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


def numero(x):
    """Número escrito en cualquier formato: 4,413.92 · 4.413,92 · 28.500 · 12,5 · 1250."""
    x = x.strip(".,")
    if "," in x and "." in x:
        dec = "," if x.rfind(",") > x.rfind(".") else "."
        x = x.replace("." if dec == "," else ",", "").replace(dec, ".")
    elif x.count(",") > 1 or x.count(".") > 1 or re.fullmatch(r"[1-9]\d{0,2}[.,]\d{3}", x):
        x = x.replace(",", "").replace(".", "")  # separador de miles
    else:
        x = x.replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


CON_IVA = r"c/ ?iva|con iva|iva incluido|incluye iva|iva inc\w*|precio final"
SIN_IVA = r"sin iva|s/ ?iva|\+ ?iva|mas iva|neto de iva|no incluye iva|iva aparte|iva no incluido"


def iva_de(texto, fin=None):
    """Regla de Ventas (27/10/2026): el catálogo guarda siempre el precio SIN IVA. Si el precio es con IVA se divide por
    la alícuota que corresponda (21% o 10,5%); si no dice nada, se toma como sin IVA.
    `fin` = posición donde termina el número en el texto: se mira primero lo que viene inmediatamente después."""
    t = norm(texto)
    cerca = t[fin:fin + 30] if fin is not None else ""
    alicuota = 1.105 if re.search(r"10[.,]5 ?%", t) else 1.21
    if re.search(SIN_IVA, cerca):
        return "sin IVA (lo dice)", 1.0
    if re.search(CON_IVA, cerca) or (re.search(CON_IVA, t) and not re.search(SIN_IVA, t)):
        return f"con IVA: dividido por {alicuota:.3f}".replace(".", ","), alicuota
    if re.search(SIN_IVA, t):
        return "sin IVA (lo dice)", 1.0
    return "no dice: se toma sin IVA", 1.0


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

    def add(desc, precio, moneda, fecha, tipo_precio, proveedor, ruta_origen, archivo, ruta_repo, unidad, extra="", pista="", iva=None):
        if not precio or precio < 0.05:
            return  # precio cero o simbólico (hay compras del stock en 0,00): no es un precio
        iva, div = iva or iva_de(desc)
        if div != 1:
            extra = "; ".join(x for x in [extra, f"precio original con IVA {precio:,.2f}"] if x)
        regs.append(dict(descripcion=desc.strip(), precio=precio / div, iva=iva, moneda=moneda or "USD", fecha=fecha, tipo_precio=tipo_precio,
                         proveedor=proveedor, ruta_origen=ruta_origen, archivo_origen=archivo, ruta_repo=ruta_repo,
                         unidad=unidad_norm(unidad), extra=extra, pista=pista))

    for r in csv.DictReader(open(PRECIOS / "lista_renar_2025-12.csv", encoding="utf-8")):
        if num(r["precio_usd"]):
            add(r["producto"], num(r["precio_usd"]), "USD", "2025-12-26", "lista", f"Renard (cód. {r['codigo']})",
                "fuentes_originales/renar_lista_2025-12.xlsx", f"código {r['codigo']}", "conocimiento/precios/lista_renar_2025-12.csv", r["unidad"])
    for r in csv.DictReader(open(PRECIOS / "stock_2024-11.csv", encoding="utf-8")):
        uc, fc = num(r["precio_ultima_compra"]), (r["fecha_ultima_compra"] or "")[:10]
        # una compra anterior a 2022 no representa el precio actual (hay compras de 2009): se usa el precio maestro de nov-2024
        if uc and fc and (fc >= COMPRA_VIGENTE or not num(r["precio_maestro_usd"])):
            add(r["descripcion"], uc, r["moneda"] or "USD", fc, "compra", f"Stock ITT · última compra (cód. {r['codigo']})",
                "fuentes_originales/stock_valorizado_2024-11.xlsx", f"código {r['codigo']}", "conocimiento/precios/stock_2024-11.csv", r["unidad"],
                extra="" if fc >= COMPRA_VIGENTE else f"compra vieja ({fc}): precio poco representativo", pista=r["grupo"])
        elif num(r["precio_maestro_usd"]):
            add(r["descripcion"], num(r["precio_maestro_usd"]), "USD", "2024-11-01", "stock (precio maestro)", f"Stock ITT (cód. {r['codigo']})",
                "fuentes_originales/stock_valorizado_2024-11.xlsx", f"código {r['codigo']}", "conocimiento/precios/stock_2024-11.csv", r["unidad"],
                extra=f"última compra {fc} a USD {uc:,.2f}, anterior a 2022: no se usa" if uc and fc else "", pista=r["grupo"])
    for r in csv.DictReader(open(PRECIOS / "precios_componentes.csv", encoding="utf-8")):
        if num(r["precio_usd"]):
            desc = " ".join(x for x in [r["descripcion"], r["dimension"], r["tipo"], r["schedule"] and f"SCH {r['schedule']}", r["serie"],
                                        r["material"], r["norma"]] if x)
            add(desc, num(r["precio_usd"]), "USD", (r["fecha"] or "2025-08-01")[:10], "cotización", r["proveedor"],
                "fuentes_originales/cotizacion_elementos_equipos_2026-03.xlsx", f"rubro {r['rubro']}" + (f" · cotización {r['cotizacion_proveedor']}" if r["cotizacion_proveedor"] not in ("", "-") else ""),
                "conocimiento/precios/precios_componentes.csv", r["unidad"], pista=r["rubro"])
    for anio in ("2026", "2025"):
        for r in csv.DictReader(open(PRECIOS / f"proveedores_{anio}.csv", encoding="utf-8")):
            det = norm(r["detalle"])
            cu = list(re.finditer(r"(?<![\d.,])(\d[\d.,]*)\s?(?:usd|u\$s|\$)?\s?c/u", det))
            if len(cu) != 1 or re.search(r";| \+ (?!iva)", det):
                continue  # presupuesto global o varios ítems: no da un precio unitario confiable ("+ IVA" no cuenta)
            car = r["carpeta_cotizacion"]
            add(r["detalle"], numero(cu[0].group(1)), r["moneda"], r["fecha"][:10], "cotización", r["proveedor"], Z + car.replace("/", "\\"),
                archivo_de(car, r["proveedor"]), f"fuentes_originales/ofertas_texto/{car}" if car else "", "un", iva=iva_de(det, cu[0].end()))
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
        fam = familia_de(t, r["pista"])
        at = atributos(t, fam, r["proveedor"])
        precio = r["precio"]
        nota = ""
        if r["moneda"].upper().startswith("ARS") or r["moneda"] == "$":
            tc, viejo = en_mes(tabla, r["fecha"], 0)
            precio = precio / tc
            nota = f"convertido de ARS a USD con dólar BNA {tc:,.0f}" + (" (fecha anterior a la tabla)" if viejo else "")
        cpi, viejo = en_mes(tabla, r["fecha"], 1)
        if fam in ("AFO", "ABW", "BRI", "NIP", "VAL", "INS") and r["unidad"] not in ("un", ""):
            r["extra"] = "; ".join(x for x in [r["extra"], f"unidad del origen '{r['unidad']}' corregida a 'un' (es una pieza)"] if x)
            r["unidad"] = "un"
        k = clave(fam, at, r["unidad"])
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
                "unidad": u["unidad"], "ultimo_precio_usd": u["precio_usd"], "iva": u["iva"], "fecha_ultimo_precio": u["fecha"], "tipo_precio": u["tipo_precio"],
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
        w.writerow(["codigo", "familia", "clave", "fecha", "precio_usd", "iva", "precio_ajustado_hoy_usd", "tipo_precio", "proveedor", "descripcion",
                    "unidad", "ruta_origen", "archivo_origen", "ruta_repo", "atributos", "nota"])
        for h in sorted(hist, key=lambda h: (h["codigo"], h["fecha"]), reverse=False):
            w.writerow([h["codigo"], h["familia"], h["clave"] or "", h["fecha"], h["precio_usd"], h["iva"], h["precio_ajustado_hoy_usd"], h["tipo_precio"],
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
    base = ["codigo", "descripcion", "unidad", "ultimo_precio_usd", "iva", "fecha_ultimo_precio", "tipo_precio", "proveedor",
            "precio_ajustado_hoy_usd", "precios_en_historial", "precio_min_usd", "precio_max_usd", "ruta_origen", "archivo_origen", "ruta_repo",
            "confianza_clasificacion"]
    hoja("Todos", ["familia"] + base, [[fl["familia"]] + [fl[c] for c in base] for fl in filas])
    for k, (nombre, cols, _) in FAMILIAS.items():
        fs = [fl for fl in filas if fl["_fam"] == k]
        hoja(nombre, base[:2] + cols + base[2:], [[fl[c] for c in base[:2]] + [fl["_at"].get(c, "") for c in cols] + [fl[c] for c in base[2:]] for fl in fs])
    wb.save(PRECIOS / "catalogo_materiales.xlsx")


if __name__ == "__main__":
    main()
