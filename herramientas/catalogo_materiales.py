"""Catálogo de materiales: todos los precios conocidos, separados por familia de material, con sus características,
el último precio de costo, su fecha y la ruta de dónde salió.

Uso: python herramientas/catalogo_materiales.py

Fuentes (etapa 1, sin IA):
  conocimiento/precios/lista_renar_2025-12.csv     lista de precios Renard (precio de lista)
  conocimiento/precios/stock_2024-11.csv           stock ITT: precio y fecha de la ÚLTIMA COMPRA de cada artículo
  conocimiento/precios/precios_componentes.csv     base de componentes (proveedor y fecha por renglón)
  conocimiento/precios/proveedores_2025/2026.csv   cotizaciones de proveedores (solo las que traen precio unitario)
  cotizaciones/*/cotizacion.json                   fuentes de precio cargadas en cotizaciones (no los estimados)
  cotizaciones_web/*/cotizacion.json               las de la página incorporadas a la base (ver cotizaciones_base.py)

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
from numeros import a_vista, fecha_iso, leer_numero  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
COMPRA_VIGENTE = "2022-01-01"
# Fin del cepo cambiario. Decisión de Matías (28/10/2026): los valores anteriores cuyo documento no dice con qué tipo de
# cambio se pasaron a dólares se DESCARTAN como precio (quedan en el historial como referencia) y vale el último valor
# confiable. Prueba de por qué: el stock pasa sus compras en pesos a dólares con el TC del día del informe (la misma compra
# del 13/06/2023 figura a USD 2,37 en sep-2024 y a 2,25 en nov-2024).
FIN_CEPO = "2025-04-14"
# Decisión de Matías (28/10/2026): en vez de dejar sin precio, los valores del cepo se llevan al valor más verosímil y
# quedan como ESTIMADO (pedir cotización para el definitivo):
#  - precio maestro del stock (nov-2024): × 0,64. Calibrado: llevado a hoy, salía 1,56 veces el costo real 2025–2026 del
#    mismo material (mediana de 14 materiales, rango 1,43–2,02). Solo la brecha del blue (× 0,90) no alcanzaba.
#  - otros valores en USD (planillas, cotizaciones): × oficial ÷ blue del mes (promedios de dolar_mensual.csv). Verificado:
#    las planillas de mar/abr-2025 daban 1,10 veces las de 2025–2026, igual que la brecha de esos meses.
#  - compras del stock: siguen descartadas (el sistema las pasó a USD con el TC de nov-2024, no el de la compra).
FACTOR_MAESTRO_STOCK = 0.64


def _brecha():
    ruta = RAIZ / "conocimiento" / "costos" / "dolar_mensual.csv"
    return {r["mes"]: float(r["oficial_promedio"]) / float(r["blue_promedio"])
            for r in csv.DictReader(open(ruta, encoding="utf-8")) if r["oficial_promedio"] and r["blue_promedio"]}


def factor_cepo(fecha, tipo_precio=""):
    """(factor, explicación) para llevar un valor en USD del cepo a su valor verosímil, o (None, motivo)."""
    if tipo_precio == "compra":
        return None, "compra del stock: el TC usado no es el de la compra"
    if tipo_precio.startswith("stock"):
        return FACTOR_MAESTRO_STOCK, "precio maestro del stock × 0,64 (calibrado con costos reales 2025–2026)"
    b = _brecha().get((fecha or "")[:7])
    if b is None:
        return None, "sin dólar blue para ese mes"
    return b, f"llevado a dólar blue: × {b:.3f} (oficial ÷ blue de {a_vista(fecha[:7])})"
PRECIOS = RAIZ / "conocimiento" / "precios"
TEXTOS = RAIZ / "fuentes_originales" / "ofertas_texto"
Z = "Z:\\VENTAS\\OFERTAS Y LICITACIONES\\"

# ---------------------------------------------------------------- familias y columnas propias
FAMILIAS = {
    "VAL": ("Válvulas", ["tipo", "diametro", "serie", "material", "trim", "extremos", "paso", "norma", "marca", "modelo"],
            ["tipo", "diametro", "serie", "material", "trim", "extremos", "paso", "marca"]),
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
COMUNES = ["codigo", "familia", "descripcion", "unidad", "ultimo_precio_usd", "iva", "alerta", "referencia_descartada_usd", "fecha_referencia_descartada", "fecha_ultimo_precio", "tipo_precio",
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
         (r"\bgda\b", "guiada"), (r"\ba-(?=\d{2,3}\b)", "a"), (r"\bunion doble golpe\b", "union doble a golpe")]


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
    if f == "INS":
        # "media cupla ... conexión manómetro", "chapa soporte manómetro": el instrumento es el destino, no la pieza
        cabeza = re.split(r"\b(?:para|p/|con|c/|conexion|soporte|porta)\b", t, maxsplit=1)[0]
        fc = familia_texto(cabeza) if cabeza.strip() and cabeza.strip() != t.strip() else f
        if fc not in ("OTR", "INS"):
            f = fc
    if f == "OTR" and pista and not re.search(NO_VALVULA, t):
        for rx, fam in PISTAS:
            if re.search(rx, norm(pista)):
                return fam
    return f


def familia_texto(t):
    if re.search(r"rosca con tuerca|union doble|union americana", t):
        return "AFO"
    if re.search(r"cartucho|elemento filtrante|caja porta ?orificio|bomba dosificadora|tapa de cierre rapido|\bllave\b|argon|\bco2\b|\bled\b"
                 r"|u-?bolt|abrazadera|manguera|\bte (en caja|de |x \d)|manzanilla|yerba|\bcafe\b|azucar", t):
        return "OTR"
    if re.search(r"manometr|transmisor|trasmisor|termometr|termovaina|caudalimetr|coriolis|presostato|sensor|indicador de nivel|visor de nivel|v-cone|computador de (?:flujo|caudal)|flow computer", t):
        return "INS"
    if re.search(r"junta|espiralad|ring joint|\bbx-?\d|\br\d{2}\b|esparrago|bulon|tuerca|kit dielectr|arandela", t):
        return "JUN"
    if re.search(r"\bbridas?\b", t):
        return "BRI"
    if re.search(r"\bniple", t):
        return "NIP"
    if re.search(r"valvul|\bvalv\b|esferica|retencion|esclusa|\baguja\b|bloqueo y purga|\bpsv\b|mariposa|\bglobo\b", t):
        return "OTR" if re.search(NO_VALVULA, t) else "VAL"
    if re.search(r"\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|perfil|angulo|planchuela|\bchapa\b|hierro|tubo estructural", t):
        return "PER"
    if re.search(r"\bcano\b|\bcanos\b|tubo s/?c|tubo c/?c|\btubo\b|\bpipe\b", t):
        return "CAN"
    acc = re.search(r"\bcodo|\btees?\b|\bte\b|reduccion|casquete|\bcupla|\btapon|\bbuje|union doble|entrerrosca|\btapa\b|olet\b|\bcurva", t)
    if acc:
        if re.search(r"\bcupla|olet\b", t):
            return "AFO"  # cuplas y olets son forjados aunque tengan un extremo BW (van soldados sobre el caño)
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
                       (r"a ?333", "A333"), (r"a ?694 ?(?:gr\.? ?)?f ?(\d{2})", "A694 F{}"), (r"a ?694", "A694"), (r"\bf ?65\b", "A694 F65"), (r"a ?194 ?(gr\.?|grado)? ?8ma?\b", "A194 8M"), (r"a ?194 ?(gr\.?|grado)? ?2h\b", "A194 2H"), (r"a ?194", "A194"),
                       (r"a ?193 ?(gr\.?|grado)? ?b ?8m", "A193 B8M"), (r"a ?193 ?(gr\.?|grado)? ?b ?7m", "A193 B7M"), (r"a ?320 ?(gr\.?)? ?l7", "A320 L7"),
                       (r"klingerit", "Klingerit"), (r"g-?10\b", "G10"),
                       (r"a ?216 ?(gr\.? ?)?wcb|\bwcb\b", "A216 WCB"), (r"\ba ?216\b", "A216 WCB"), (r"a ?351|cf8m", "A351 CF8M"), (r"a ?182 ?f ?316|f316", "A182 F316"), (r"aisi ?316l?|\b316l?\b", "AISI 316"), (r"aisi ?304|\b304\b", "AISI 304"),
                       (r"duplex", "Dúplex"), (r"a ?312", "A312"), (r"a ?216 ?(gr\.? ?)?wcb|\bwcb\b", "A216 WCB"),
                       (r"a ?105", "A105"), (r"a ?234 ?(gr\.? ?)?wpb|\bwpb\b", "A234 WPB"), (r"a ?106", "A106 B"),
                       (r"api ?5l", "API 5L"), (r"a ?53", "A53"), (r"a ?516", "A516-70"), (r"a ?36\b", "A36"),
                       (r"f-?24\b", "F-24"), (r"a ?193", "A193 B7"), (r"galvaniz", "Galvanizado"), (r"bronce", "Bronce")]:
        m = re.search(rx, t)
        if m:
            return nombre.format(*m.groups()) if "{}" in nombre else nombre
    if "inox" in t:
        return "Inoxidable"
    if "carbono" in t:
        return "Acero al carbono"
    return ""


def extremos_de(t, fam=""):
    t = re.sub(r"\d+ ?d(?:ias)?\.? ?ff\b|\bff ?\d+ ?d", " ", t)  # "60 días FF" = fecha de factura, no cara plana
    ext = [e for e, rx in (("NPT", r"\bnpt"), ("BSPT", r"bspt"), ("SW", r"\bsw\b|socket"), ("BW", r"\bbw\b|biselad|a tope"),
                           ("RTJ", r"\brtj\b|\brj\b|ring joint"), ("RF", r"\brf\b"), ("FF", r"\bff\b"), ("Bridado", r"bridad")) if re.search(rx, t)]
    if fam == "JUN":
        ext = [e for e in ext if e != "SW"]  # en una junta, SW = spiral wound
    return "/".join(ext)


# ASME B36.10: diámetro exterior (mm) de cada NPS y espesores (mm) por schedule
OD_NPS = {21.3: 0.5, 26.7: 0.75, 33.4: 1, 42.2: 1.25, 48.3: 1.5, 60.3: 2, 73.0: 2.5, 88.9: 3, 101.6: 3.5, 114.3: 4, 141.3: 5,
          168.3: 6, 219.1: 8, 273.0: 10, 323.8: 12, 323.9: 12, 355.6: 14, 406.4: 16, 457.0: 18, 457.2: 18, 508.0: 20, 609.6: 24, 610.0: 24}
ESPESORES = {  # NPS: {schedule: espesor}
    0.5: {"40": 2.77, "80": 3.73, "160": 4.78}, 0.75: {"40": 2.87, "80": 3.91, "160": 5.56}, 1: {"40": 3.38, "80": 4.55, "160": 6.35},
    1.25: {"40": 3.56, "80": 4.85, "160": 6.35}, 1.5: {"40": 3.68, "80": 5.08, "160": 7.14}, 2: {"40": 3.91, "80": 5.54, "160": 8.74},
    2.5: {"40": 5.16, "80": 7.01, "160": 9.53}, 3: {"40": 5.49, "80": 7.62, "160": 11.13}, 4: {"40": 6.02, "80": 8.56, "120": 11.13, "160": 13.49},
    6: {"40": 7.11, "80": 10.97, "120": 14.27, "160": 18.26}, 8: {"20": 6.35, "30": 7.04, "40": 8.18, "60": 10.31, "80": 12.70, "160": 23.01},
    10: {"20": 6.35, "30": 7.80, "40": 9.27, "XS": 12.70, "80": 15.09, "160": 28.58}, 12: {"20": 6.35, "30": 8.38, "STD": 9.53, "40": 10.31, "XS": 12.70, "80": 17.48},
    14: {"10": 6.35, "20": 7.92, "STD": 9.53, "40": 11.13, "XS": 12.70, "80": 19.05}, 16: {"10": 6.35, "20": 7.92, "STD": 9.53, "XS": 12.70, "40": 12.70, "80": 21.44},
    18: {"10": 6.35, "20": 7.92, "STD": 9.53, "30": 11.13, "XS": 12.70, "40": 14.27}, 20: {"10": 6.35, "20": 9.53, "30": 12.70, "40": 15.09, "80": 26.19},
    24: {"10": 6.35, "20": 9.53, "30": 14.27, "40": 17.48, "80": 30.96}}
NPS_VALIDOS = {0.125, 0.25, 0.375, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30,
               32, 34, 36, 40, 42, 48, 54, 56, 60}


def nps_de_od(od):
    return next((n for o, n in OD_NPS.items() if abs(o - od) <= 0.3), None)


def schedule_de_espesor(nps, esp):
    """Schedule del espesor en mm, si coincide con la tabla (±0,1 mm). XS/STD de 10" en adelante quedan como XS/STD."""
    for sch, e in ESPESORES.get(nps, {}).items():
        if abs(e - esp) <= 0.1:
            return sch
    return ""


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
        ord_ds = [x for x in ord_ds if x in NPS_VALIDOS] if fam != "INS" else ord_ds  # "45,5"" no existe
        if ord_ds:
            d["diametro"] = f"{ord_ds[0]:g}\""
            if len(ord_ds) > 1 and fam in ("AFO", "ABW") and re.search(r"reduc|buje", t):
                d["diametro2"] = f"{ord_ds[1]:g}\""
    sr = series(t)
    if sr:
        d["serie"] = sr[0]
    elif fam != "PER" and stock:
        d["serie"] = stock.group(2)
    d["schedule"] = schedule_de(t, float(d["diametro"][:-1]) if d.get("diametro", "").endswith('"') else None)
    d["material"] = material_de(t)
    d["extremos"] = extremos_de(t, fam)
    if not d.get("diametro") and fam in ("JUN", "VAL", "BRI", "AFO", "ABW", "NIP"):
        m = re.search(r"(?:junta \w+|esparrago|tuerca\w*(?: pesada)?|bulon|arandela|esferica(?: paso total)?|retencion|esclusa|brida \w+|codo|tee|niple)\s+(\d{1,2} \d/\d|\d/\d|\d{1,2})\b", t)
        if m:
            v = frac(m.group(1))
            if 0.125 <= v <= 60:
                d["diametro"] = f"{v:g}\""
    if fam == "VAL":
        d["tipo"] = primero(r"(bloqueo y purga|esferica|retencion|esclusa|aguja|globo|mariposa|seguridad|alivio|control|contrapresion|reguladora|tapon|solenoide|sdv|3 vias|tres vias|purga|c/actuador)", t)
        if d["tipo"] in ("esferica", "globo", "mariposa", "esclusa", "3 vias", "tres vias") and re.search(r"actuad|motoriz|electroactu|neumatic|c/actuador|con actuador|limitadora de caudal", t):
            d["tipo"] += " actuada"  # una válvula con actuador no se cotiza con una manual (CTRL-P01: globo de control a USD 80)
        d["trim"] = primero(r"(trim ?\d+|asientos? (?:metalic\w*|ptfe|teflon|blando\w*)|ptfe|metal[- ]metal)", t) or \
            (("asiento " + primero(r"\basto (tv|tr|tcc|ptfe|metal\w*)", t).upper()) if re.search(r"\basto (tv|tr|tcc|ptfe|metal)", t) else "")
        d["paso"] = "" if not d["tipo"].startswith("esferica") else \
            "total" if re.search(r"paso total|full bore|\bfb\b", t) else ("reducido" if re.search(r"paso (reducido|nominal)|reduced|\bpr\b|\brb\b", t) else "")
        d["norma"] = primero(r"(api ?6d|api ?602|api ?594|api ?6a|api ?608|b16\.34)", t).upper()
    elif fam == "AFO":
        d["tipo"] = primero(r"(codo 90|codo 45|codo|tees?|te|media cupla|cupla para soldar|cupla|tapon|buje|union doble a golpe extensible|union doble extensible|union extensible|union doble a golpe|union doble rapida|union doble|rosca con tuerca|entrerrosca|tapa|thredolet|threadolet|sockolet)", t)
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
        d["costura"] = "sin costura" if re.search(r"s/ ?c(ostura)?\b|sin costura|seamless", t) else ("con costura" if re.search(r"c/ ?c(ostura)?\b|con costura|erw", t) else "")
        d["revestimiento"] = primero(r"(tricapa\s?\w*|polipropileno|polietileno|galvanizado|epoxi)", t)
        if not d.get("diametro"):
            od = primero(r"(\d{2,3}[.,]\d)\s?x", t)
            if od:
                nps = nps_de_od(float(od.replace(",", ".")))
                d["diametro"] = f"{nps:g}\"" if nps else f"OD {od} mm"
        if d.get("espesor_mm") and not d.get("schedule") and d.get("diametro", "").endswith('"'):
            d["schedule"] = schedule_de_espesor(float(d["diametro"][:-1]), float(d["espesor_mm"]))
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


SINONIMOS = {"tees": "tee", "welding neck": "wn", "blind": "ciega", "bl": "ciega", "slip on": "so", "slipon": "so", "lap joint": "lj",
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
    """Lector único: herramientas/numeros.py."""
    return leer_numero(x)[0]


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


SERVICIO = (r"mano de obra|\bm\.?o\.? |rolado|cilindrado|\barmado\b|fabricacion|servicio|montaje|granallad|transporte|flete"
            r"|ensayo|radiograf|inspeccion|mecanizad|soldadura de|pintura de")
PRECIO_EN_TRAMO = r"\(\s?\$?\s?\d[\d.,]*\s?\)|\d[\d.,]*\s?(?:usd|u\$s)\b|(?:usd|u\$s)\s?\d"


def tramo(original):
    """Solo el pedazo del renglón que corresponde al precio "c/u" (auditoría: "tapón 2" (6,66) y 2 tees 2" #6000
    (126,36 c/u)" se clasificaba como tapón). Va desde el último tramo que tenía otro precio hasta el final del c/u."""
    low = original.lower()
    m = re.search(r"(?<![\d.,])\d[\d.,]*\s?(?:usd|u\$s|\$)?\s?c/u", low)
    if not m:
        return original
    fin = low.find(")", m.end())
    fin = fin + 1 if 0 <= fin - m.end() <= 3 else m.end()
    ini = 0
    for sep in re.finditer(r", | y |; ", low[:m.start()]):
        if re.search(PRECIO_EN_TRAMO, low[ini:sep.start()]):
            ini = sep.end()
    cabeza = original[:original.find(":") + 1] if 0 < original.find(":") < ini else ""
    return (cabeza + " " + original[ini:fin]).strip()


PRECIO_TXT = r"(?<![\w.,])(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+,\d{1,2})(?![\d])"


def separar_renglon(original):
    """Renglones con varios productos y un precio cada uno ("Coriolis DN150 59.539,72; computador XFC6200EX 7.345,97;
    3 transmisores a 864,20 c/u"; "válvula de control (8.206) + 2 PSV (1.380 c/u)"): una pieza por tramo, con el precio
    que dice el tramo (en estos renglones es el unitario). Antes la fila entera quedaba con el único precio "c/u" y el computador de caudal salía a USD 864,20
    (error 28 repetido en CTRL-P01). Devuelve [(texto, precio)] si hay 2 o más tramos con precio; si no, None."""
    tramos = []
    segs = []
    for parte in re.split(r";|\.\s(?=suma|total|subtotal)|,\s(?=\d+\s[a-záéíóú])", original, flags=re.I):
        # " + " separa productos solo si lo de la izquierda ya tiene su precio ("válvula (8.206) + 2 PSV (1.380)");
        # en "esférica 16\" + actuador (50.707,15)" el precio es del conjunto
        trozos = re.split(r"\s\+\s", parte)
        acum = trozos[0]
        for t in trozos[1:]:
            if re.search(PRECIO_TXT, acum) or re.search(r"\(\d{2,6}\)", acum):
                segs.append(acum); acum = t
            else:
                acum += " + " + t
        segs.append(acum)
    for seg in segs:
        low = seg.lower()
        if re.search(r"suma|subtotal|total|desc\.|dto|descuento", low):
            continue
        if re.search(r"\d+\s+a\s+\d+|%|\benv[ií]o\b|\bflete\b", low):
            return None  # rangos ("USD 45 a 271"), descuentos o fletes: el renglón no se separa
        nums = (list(re.finditer(r"(?:usd|u\$s)\s?(\d[\d.]*(?:,\d{1,2})?)", seg, re.I))  # "USD 420/m": el precio es el que dice USD
                or list(re.finditer(PRECIO_TXT, seg)) or list(re.finditer(r"\((?:usd\s*)?(\d{2,6})(?:\s*c/u)?\)", seg, re.I)))
        if len(nums) != 1:
            continue
        n = nums[0].group(1)
        v = float(n) if re.fullmatch(r"\d+\.\d{2}", n) else float(n.replace(".", "").replace(",", "."))  # "USD 26.04" es 26,04
        texto = re.sub(r"\(?\s*(?:usd\s*)?" + re.escape(nums[0].group(1)) + r"(?:\s*c/u)?\s*\)?", "", seg, flags=re.I)
        texto = re.sub(r"^\W*(\d{1,3}\s+(?!\d+/))?|\s+a\s*$", "", texto).strip(" :,.-")  # "2 7/8\"" es diámetro, no cantidad
        if tramos and (texto.lower().startswith("de ") or re.match(r"\d", texto)):
            texto = ("de " + texto) if not texto.lower().startswith("de ") else texto
        if texto.lower().startswith("de ") and tramos:  # "+ 7 de 1/2"": el sustantivo es el del tramo anterior
            sust = re.match(r"[^\d\"]+", re.sub(r"^\d+\s+", "", tramos[-1][0].split(":")[-1].strip()))
            texto = (sust.group(0).strip() + " " + texto[3:]) if sust else texto
        if len(texto) >= 6 and v >= 1:
            tramos.append((texto, v))
    # si algún tramo quedó sin producto ("actuador") o mezcla dos ("... y SDV-012: 3\""), el renglón no se separa
    if any(len(t.split()) < 2 or re.search(r"\sy\s+[A-Z]{2,}-?\d", t) or re.match(r"x\s", t)
           or re.search(r"mano de obra|armado|soldadura|por trampa|asistencia|\bdias\b|\bdías\b|\bkg\b", t, re.I) for t, _ in tramos):
        return None
    return tramos if len(tramos) >= 2 else None


def desambiguar(valor, texto, total):
    """"26,338 c/u" puede ser 26,34 o 26.338. Se elige el que da una cantidad entera con el total del renglón
    (2 × 26.338 = 52.676). Si no se puede decidir, queda como ambiguo y con alerta."""
    cant = re.match(r"\D{0,25}?(\d{1,4}) ", texto)
    cant = int(cant.group(1)) if cant else None
    for c in (valor, valor * 1000):
        if total:
            n = total / c
            if abs(n - round(n)) < 0.01 * n and 1 <= round(n) <= 10000 and (cant is None or round(n) == cant):
                return c, False
    return valor, True


def unidad_de_texto(t):
    if re.search(r"c/ ?2 tuercas|con 2 tuercas|con dos tuercas|\bjuegos?\b|\bjgo", t):
        return "juego"
    if re.search(r"(?:usd|u\$s)?\s?\d[\d.,]*\s?(?:usd|u\$s)?\s?(?:/|por) ?(?:m|mt|metro)\b", t):
        return "m"
    return "un"


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
        hoja = re.search(r"(\d{3,4}) ?x ?(\d{3,4})", r["descripcion"])
        if unidad_norm(r["unidad"]) == "m2" and hoja and re.search(r"chapa", r["descripcion"], re.I):
            # el stock dice "Mts²" pero el precio es de la hoja entera (USD/kg igual al de las chapas hermanas; auditoría 27/10/2026)
            r = {**r, "unidad": f"hoja {hoja.group(1)}x{hoja.group(2)}"}
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
        if num(r["precio"]):
            desc = " ".join(x for x in [r["descripcion"], r["dimension"], r["tipo"], r["schedule"] and f"SCH {r['schedule']}", r["serie"],
                                        r["material"], r["norma"]] if x)
            add(desc, num(r["precio"]), r["moneda"], r["fecha"][:10], "cotización", r["proveedor"],
                "fuentes_originales/cotizacion_elementos_equipos_2026-03.xlsx", f"rubro {r['rubro']}" + (f" · cotización {r['cotizacion_proveedor']}" if r["cotizacion_proveedor"] not in ("", "-") else ""),
                "conocimiento/precios/precios_componentes.csv", r["unidad"], pista=r["rubro"])
    for anio in ("2026", "2025"):
        for r in csv.DictReader(open(PRECIOS / f"proveedores_{anio}.csv", encoding="utf-8")):
            det = norm(r["detalle"])
            partes = separar_renglon(r["detalle"]) if not re.search(SERVICIO, det) else None
            if partes:
                car = r["carpeta_cotizacion"]
                pre = r["detalle"].split(":")[0] if ":" in r["detalle"][:80] else ""
                for texto, v in partes:
                    add(texto, v, r["moneda"], fecha_iso(r["fecha"]), "cotización", r["proveedor"], Z + car.replace("/", "\\"),
                        archivo_de(car, r["proveedor"]), f"fuentes_originales/ofertas_texto/{car}" if car else "", unidad_de_texto(norm(texto)),
                        extra=f"renglón con varios productos, separado por tramo{(' (' + pre[:60] + ')') if pre else ''}: {r['detalle'][:160]}",
                        iva=iva_de(det))
                continue
            cu = list(re.finditer(r"(?<![\d.,])(\d[\d.,]*)\s?(?:usd|u\$s|\$)?\s?c/u", det)) or \
                list(re.finditer(r"\b(?:un|unidades)\s+a\s+(?:usd|u\$s)\s?(\d[\d.,]*)", det))  # "12 un a USD 3.586,58" (CTRL-C01)
            if len(cu) != 1 or re.search(SERVICIO, det):
                continue  # varios precios unitarios, ninguno, o es un servicio (va al catálogo de MO y servicios)
            valor, ambiguo = leer_numero(cu[0].group(1))
            if ambiguo:
                valor, ambiguo = desambiguar(valor, r["detalle"], num(r["precio"]))
            car = r["carpeta_cotizacion"]
            add(tramo(r["detalle"]), valor, r["moneda"], fecha_iso(r["fecha"]), "cotización", r["proveedor"], Z + car.replace("/", "\\"),
                archivo_de(car, r["proveedor"]), f"fuentes_originales/ofertas_texto/{car}" if car else "", unidad_de_texto(det),
                extra="; ".join(x for x in [f"número ambiguo '{cu[0].group(1)}' leído como {valor:g}: verificar" if ambiguo else "",
                                            f"renglón completo: {r['detalle'][:180]}" if len(r["detalle"]) > len(tramo(r["detalle"])) + 5 else ""] if x),
                iva=iva_de(det, cu[0].end()))
    # acero al carbono por kg (chapa, ángulo, planchuela, caño estructural): herramientas/acero_por_kg.py
    ruta_ac = PRECIOS / "acero_por_kg.csv"
    if ruta_ac.exists():
        for r in csv.DictReader(open(ruta_ac, encoding="utf-8")):
            forma = "Tubo estructural (caño estructural)" if r["forma"] == "caño estructural" else r["forma"].capitalize()
            add(f"{forma} {r['medida']} {r['material']} (precio por kg, {r['unidad_compra']})", float(r["usd_kg"]), "USD", r["fecha"],
                "cotización", "Precios de acero (J. Elejondo)", r["fuente"], "", "conocimiento/precios/acero_por_kg.csv", "kg",
                extra=f"pesos con IVA ÷ 1,21 ÷ TC del documento {r['tc_documento']}; +10% por recortes: {float(r['usd_kg_con_recortes']):.2f}; no incluye corte, plegado ni rolado",
                iva=("con IVA en el documento: ya dividido por 1,21", 1.0))
    # listas y cotizaciones nuevas que llegan por los pedidos de la página (web/LEEME.md, "Pedidos desde la página")
    ruta_ln = PRECIOS / "listas_nuevas.csv"
    if ruta_ln.exists():
        for r in csv.DictReader(open(ruta_ln, encoding="utf-8")):
            add(r["descripcion"], num(r["precio"]), r["moneda"], fecha_iso(r["fecha"]), r["tipo_precio"] or "cotización", r["proveedor"],
                r["archivo_origen"], r["pedido"] and f"pedido de la página {r['pedido']}", r["ruta_repo"], r["unidad"], extra=r["nota"],
                iva=iva_de(r["iva"]) if r["iva"] else None)
    # etapa 2: costos de materiales de las planillas de costo 2025–2026 (herramientas/unir_planillas_costo.py)
    ruta_pl = PRECIOS / "planillas_costo_items.csv"
    if ruta_pl.exists():
        for r in csv.DictReader(open(ruta_pl, encoding="utf-8")):
            if r["usable_catalogo"] != "si" or r["tipo"] != "material":
                continue
            u = norm(r["unidad"])
            unidad = "m" if "costo por m" in u else ("kg" if u.startswith("kg") else r["unidad"])
            car = r["carpeta_proyecto"]
            # costo_unitario viene del texto de un Excel: formato de máquina, el punto es decimal ("131.131" = 131,13)
            add(r["descripcion"], float(r["costo_unitario"]), r["moneda"], fecha_iso(r["fecha_planilla"]), "planilla interna",
                (r["proveedor_o_criterio"] or "planilla de costo ITT")[:80], Z + car.replace("/", "\\"), f"{r['carpeta']}/{Path(r['archivo']).name}"[:200],
                f"fuentes_originales/ofertas_texto/{car}", unidad, extra=f"planilla de costo {r['proyecto']} ({r['ubicacion']})"[:200],
                pista=r["rubro"], iva=iva_de(r["iva_origen"]) if r["iva_origen"] else None)
    from cotizaciones_base import cotizaciones  # repositorio + las de la página incorporadas a la base
    for f, c in cotizaciones():
        for it in c["items"]:
            if it["grupo"] != "material" or re.fullmatch(r"\d+[a-z]", str(it["pos"])):
                continue  # las compras extra (14b) son sobrante de otra posición, no una pieza
            for s in it["fuentes"]:
                if s["tipo"] in ("est", "lista", "stock") or not s.get("precio") or s.get("coincide") != "igual" \
                        or re.search(r"\b[A-Z]{3}-\d{5}\b", s.get("proveedor", "")):
                    # lista y stock ya entran por su archivo; los similares describen lo pedido y no lo cotizado;
                    # un precio con código del catálogo (CAN-01435) salió del catálogo: volver a cargarlo lo duplicaría
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
                     "nota": "; ".join(x for x in [nota, "ajuste parcial: fecha anterior a ene-2024" if viejo else "", r["extra"]] if x),
                     "confianza_clasificacion": "alta" if k and len(at) >= 4 else ("media" if k else "baja")})
    grupos = defaultdict(list)
    for h in hist:
        grupos[h["clave"] or "SOLO|" + "|".join([h["familia"], norm(h["descripcion"])[:150], h["proveedor"], h["ruta_repo"], h["archivo_origen"]])].append(h)
    # códigos estables (control C10): un material conserva su código aunque se regenere el catálogo
    reg_ruta = PRECIOS / "catalogo_codigos.csv"
    registro = {r["clave"]: r["codigo"] for r in csv.DictReader(open(reg_ruta, encoding="utf-8"))} if reg_ruta.exists() else {}
    ultimo = max([int(c.split("-")[1]) for c in registro.values()] or [0])
    for k in sorted(grupos, key=lambda k: (grupos[k][0]["familia"], k)):
        if k not in registro:
            ultimo += 1
            registro[k] = f"{grupos[k][0]['familia']}-{ultimo:05d}"
    with open(reg_ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "clave"])
        for k, c in sorted(registro.items(), key=lambda kv: kv[1]):
            w.writerow([c, k])
    # mediana por familia, tipo, Ø y unidad para detectar pesos tomados como dólares (control C3)
    pares = defaultdict(list)
    for h in hist:
        pares[(h["familia"], h["atributos"].get("tipo", ""), h["atributos"].get("diametro", ""), h["unidad"])].append(h["precio_usd"])
    filas = []
    for k, hs in sorted(grupos.items(), key=lambda kv: registro[kv[0]]):
        hs.sort(key=lambda h: (h["fecha"], PRIORIDAD.get(h["tipo_precio"], 0)), reverse=True)
        for h in hs:
            h["confiable"] = not (h["fecha"] and h["fecha"] < FIN_CEPO and "tc_explicito" not in h["nota"])
            if not h["confiable"]:
                h["nota"] = "; ".join(x for x in ["descartado: período con cepo, dólar sin aclarar", h["nota"]] if x)
        buenos = [h for h in hs if h["confiable"]]
        alertas = []
        if not buenos:
            for h in hs:  # valor verosímil para los del cepo (ESTIMADO)
                f, txt = factor_cepo(h["fecha"], h["tipo_precio"])
                if f:
                    e = {**h, "precio_usd": round(h["precio_usd"] * f, 4), "precio_ajustado_hoy_usd": round(h["precio_ajustado_hoy_usd"] * f, 4),
                         "tipo_precio": "estimado (cepo)", "nota": f"ESTIMADO: {txt}; valor original USD {h['precio_usd']:,.2f}; " + h["nota"]}
                    buenos.append(e)
            if buenos:
                alertas.append(f"ESTIMADO: valor del período con cepo llevado a su valor verosímil ({buenos[0]['nota'].split(';')[0][11:]}); pedir cotización para el definitivo")
        u = buenos[0] if buenos else hs[0]
        precios = [h["precio_usd"] for h in (buenos or hs)]
        if not buenos:
            alertas.append(f"sin precio confiable (solo valores del período con cepo; referencia descartada USD {hs[0]['precio_usd']:,.2f} del {a_vista(hs[0]['fecha'])}): pedir cotización")
        if max(precios) > 3 * min(precios):
            alertas.append(f"historial con precios muy distintos ({min(precios):,.2f} a {max(precios):,.2f}): revisar")
        par = sorted(pares[(u["familia"], u["atributos"].get("tipo", ""), u["atributos"].get("diametro", ""), u["unidad"])])
        if len(par) >= 3 and u["atributos"].get("tipo"):
            med = par[len(par) // 2]
            if u["precio_usd"] > 50 * med:
                alertas.append(f"{u['precio_usd'] / med:,.0f} veces la mediana de piezas parecidas: ¿pesos tomados como dólares?")
            elif u["precio_usd"] < med / 50:
                alertas.append(f"1/{med / u['precio_usd']:,.0f} de la mediana de piezas parecidas: ¿precio mal leído?")
        if not u["fecha"]:
            alertas.append("sin fecha válida en el origen")
        if "ambiguo" in u["nota"]:
            alertas.append("número ambiguo en el origen")
        fila = {"codigo": registro[k], "alerta": "; ".join(alertas), "familia": FAMILIAS[u["familia"]][0], "descripcion": u["descripcion"][:200],
                "unidad": u["unidad"], "ultimo_precio_usd": u["precio_usd"] if buenos else "", "iva": u["iva"],
                "fecha_ultimo_precio": u["fecha"] if buenos else "", "tipo_precio": u["tipo_precio"],
                "referencia_descartada_usd": "" if buenos else u["precio_usd"], "fecha_referencia_descartada": "" if buenos else u["fecha"],
                "proveedor": u["proveedor"], "ruta_origen": u["ruta_origen"], "archivo_origen": u["archivo_origen"], "ruta_repo": u["ruta_repo"],
                "precio_ajustado_hoy_usd": u["precio_ajustado_hoy_usd"] if buenos else "", "precios_en_historial": len(hs), "precio_min_usd": min(precios),
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
            "confianza_clasificacion", "alerta", "referencia_descartada_usd", "fecha_referencia_descartada"]
    hoja("Todos", ["familia"] + base, [[fl["familia"]] + [fl[c] for c in base] for fl in filas])
    for k, (nombre, cols, _) in FAMILIAS.items():
        fs = [fl for fl in filas if fl["_fam"] == k]
        hoja(nombre, base[:2] + cols + base[2:], [[fl[c] for c in base[:2]] + [fl["_at"].get(c, "") for c in cols] + [fl[c] for c in base[2:]] for fl in fs])
    wb.save(PRECIOS / "catalogo_materiales.xlsx")


if __name__ == "__main__":
    main()
