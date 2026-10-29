"""Arma el índice de proyectos (antecedentes) para buscar cotizaciones parecidas: conocimiento/comercial/indice_proyectos.csv

Uso: python herramientas/indice_proyectos.py

Fuentes:
  conocimiento/fichas_2025/ y fichas_2026/   cotizaciones analizadas de la carpeta Z:\\VENTAS\\OFERTAS Y LICITACIONES
  cotizaciones/*/cotizacion.json             cotizaciones armadas con el cotizador
Por decisión de Ventas (27/10/2026) el índice cubre solo 2025 y 2026; 2021–2024 no se incluye. Aparte, las carpetas
sin ficha (2021–2024 y las de 2025–2026 que faltan fichar) van a conocimiento/comercial/indice_historico.csv, sin
precios: el buscador las muestra solo si hay menos de 5 antecedentes del mismo subtipo (Matías, 29-10-2026).

Por cada proyecto: familia, etiquetas (un proyecto puede ser "skid" y "filtro") y subtipo (coalescente, canasto,
bifásico, puente de medición…: ver SUBTIPOS), Ø del cuerpo en recipientes, datos técnicos normalizados
(diámetros, series, material, roscado/bridado, ensayos), datos comerciales y qué tiene la carpeta (planilla de
costo, cotizaciones de proveedores, oferta enviada, OC). Se busca con herramientas/buscar_antecedentes.py.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "conocimiento" / "comercial" / "indice_proyectos.csv"
TEXTOS = RAIZ / "fuentes_originales" / "ofertas_texto"

FAMILIAS = {"C": "Calentadores e intercambiadores", "SEP": "Separadores", "F": "Filtros", "SK": "Skids", "M": "Manifolds",
            "CO": "Colectores", "P": "Puentes y tramos de medición", "CA": "Cañería / piping / spools", "T": "Tanques",
            "TS": "Trampas scraper", "V": "Válvulas", "EST": "Estructuras y soportes", "S": "Servicios / mano de obra", "OT": "Otros"}
# Palabras clave por familia (sin acentos, en minúscula)
CLAVES = {
    "P": ["puente", "tramo de medicion", "tramo medicion", "cuadro cbm", "puente de inyeccion"],
    "CO": ["colector"],
    "M": ["manifold"],
    "SK": ["skid"],
    "F": ["filtro", "coalescent", "canasto"],
    "SEP": ["separador", "slug catcher", "kod", "knock out", "scrubber"],
    "C": ["calentador", "intercambiador", "mazo", "haz tubular"],
    "TS": ["trampa", "scraper"],
    "T": ["tanque"],
    "CA": ["caneria", "piping", "spool", "carretel", "prefabricado"],
    "EST": ["estructura", "soporte", "plataforma", "mojon"],
    "S": ["mano de obra", "solo mo", "servicio de"],
}
# Sinónimos: se llevan a una sola palabra antes de clasificar y de armar las palabras del buscador (en el índice y en el
# pedido), así "coalescedor" y "coalescente" o "tramo de medición" y "puente de medición" cuentan igual (29-10-2026).
SINONIMOS = [
    (r"\bcoalesce(?:dor|dores|nte|ntes|r|rs)\b|\bcoalescing\b", "coalescente"),
    (r"\bknock[ -]?out(?: drums?)?\b|\bk\.o\.d\b|\bkods\b", "kod"),
    (r"\bslug c[ua]tchers?\b", "slugcatcher"),
    (r"\bdegasser\b|\bdesgasificador(?:es)?\b", "desgasificador"),
    (r"\bbaskets?\b|\bcestas?\b|\bcestos?\b", "canasto"),
    (r"\bstrainers?\b|\btemporar(?:y|ly|io|ios)\b", "temporal"),
    (r"\btramos? de medicion\b", "puente de medicion"),
    (r"\bscrapp?ers?\b|\bpig(?:s|ging)?\b", "scraper"),
    (r"\blanzadoras?\b|\breceptoras?\b", "trampa"),
    (r"\bhaz tubular\b|\bmazos? de tubos\b|\bmazos?\b", "intercambiador"),
    (r"\bcarretel(?:es)?\b|\bspools?\b", "spool"),
    (r"\berps?\b|\bestacion(?:es)? (?:reguladoras?|de regulacion)(?: de presion)?\b|\bsaltos? de regulacion\b", "regulacion"),
    (r"\bfuel gas\b", "gas combustible"),
    (r"\bbbo\.? ?mec\.?(?=\s|$)|\bb\. ?mec\.?(?=\s|$)", "bombeo mecanico"),
    (r"\bseparador(?:es)? de gotas\b", "scrubber"),
    (r"\bflare\b", "antorcha"),
    (r"\bfm[ -]?0?(\d{1,2})\b", r"fm\1"),  # FM06, FM-6, FM 6 -> fm6
]
_SIN = [(re.compile(a), b) for a, b in SINONIMOS]


def canon(t):
    """Texto normalizado (norm) con los sinónimos llevados a una sola forma."""
    for rx, b in _SIN:
        t = rx.sub(b, t)
    return t


# Subtipos de equipo, para todas las familias: lo que más pesa al buscar antecedentes (un filtro canasto y un filtro
# coalescente son la misma familia pero no se comparan). Van del más específico al más general; cada uno con su familia.
# Se buscan en el texto ya pasado por canon(). Agregar acá los que falten (y correr test_antecedentes.py).
SUBTIPOS = [
    # código, familia, nombre, patrones
    ("coalescente", "F", "filtro / separador coalescente", [r"coalescente"]),
    ("polvo_liquido", "SEP", "separador de polvo y líquido", [r"polvo y liquido", r"separador(?:es)? de polvo", r"\bdust\b"]),
    ("trifasico", "SEP", "separador trifásico", [r"trifasic"]),
    ("bifasico", "SEP", "separador bifásico", [r"bifasic"]),
    ("slugcatcher", "SEP", "slug catcher", [r"slugcatcher"]),
    ("kod", "SEP", "KOD / knock out drum", [r"\bkod\b"]),
    ("desgasificador", "SEP", "desgasificador", [r"desgasificador"]),
    ("scrubber", "SEP", "scrubber", [r"scrubber", r"depurador"]),
    ("separador_arena", "SEP", "separador de arena / desarenador", [r"desarenad", r"desanding", r"separador(?:es)? de arena"]),
    ("filtro_fm", "F", "filtro FM (cartucho modular)", [r"\bfm\d{1,2}\b", r"\bfm\b", r"(?:simple|doble) modulo"]),
    ("filtro_temporal", "F", "filtro temporal / cónico", [r"\btemporal", r"filtros? conicos?"]),
    ("filtro_canasto", "F", "filtro canasto / tipo T o Y", [r"canasto", r"filtros? (?:tipo )?[ty]\b"]),
    ("filtro_cartucho", "F", "filtro de cartucho o bolsa", [r"filtros? (?:de )?(?:cartucho|bolsa)", r"\bbolsa\b"]),
    ("calentador_electrico", "C", "calentador eléctrico", [r"calentador(?:es)? electric"]),
    ("calentador_indirecto", "C", "calentador indirecto / baño", [r"calentador(?:es)? (?:de gas |de petroleo )?indirect", r"\bbtu ?/ ?h", r"\bktbu\b", r"bano (?:de agua|maria)"]),
    ("intercambiador", "C", "intercambiador / mazo de tubos", [r"intercambiador"]),
    ("trampa_scraper", "TS", "trampa scraper", [r"scraper", r"\btrampa"]),
    ("skid_regulacion", "SK", "skid / estación de regulación y medición", [r"regulacion"]),
    ("skid_concentrador", "SK", "skid concentrador / colector", [r"concentrador", r"skids? colector"]),
    ("skid_gas_combustible", "SK", "skid de gas combustible", [r"gas combustible", r"acondicionamiento de gas"]),
    ("skid_quimicos", "SK", "skid de inyección de químicos", [r"quimico", r"metanol", r"inhibidor"]),
    ("skid_medicion", "SK", "skid de medición / LACT", [r"skids? de medicion", r"\blact\b", r"custody", r"medicion de (?:gas|liquido)"]),
    ("skid_bombas", "SK", "skid de bombas / cuadro de válvulas", [r"cuadro de valvulas", r"booster", r"skids? de (?:bombas|distribucion)"]),
    ("skid_carga", "SK", "skid cargadero / descargadero", [r"cargadero", r"descargadero", r"skids? de carga"]),
    ("puente_medicion", "P", "puente / tramo de medición", [r"puentes? de medicion", r"\bufm\b", r"fiscal", r"v-?cone"]),
    ("puente_inyeccion", "P", "puente de inyección", [r"puentes? de inyeccion"]),
    ("puente_produccion", "P", "puente de producción", [r"puentes? (?:armados? )?de produccion", r"\baib\b", r"bombeo mecanico", r"\bcbm\b"]),
    ("manifold_pad", "M", "manifold / skid de PAD", [r"\bpad\b"]),
    ("manifold_agua", "M", "manifold de pozo de agua / salmuera", [r"pozos? de agua", r"salmuera"]),
    ("colector_inyeccion", "CO", "colector de inyección", [r"colector(?:es)? de inyeccion"]),
    ("colector_campo", "CO", "colector de campo / producción", [r"colector(?:es)? de (?:campo|produccion)", r"colector(?:es)? manual"]),
    ("antorcha", "CA", "antorcha / venteo", [r"antorcha", r"\bstack\b", r"venteo"]),
    ("bypass", "CA", "bypass de instrumentos", [r"by ?pass"]),
    ("prefabricado", "CA", "prefabricado de piping / spools", [r"prefabricad", r"\bspool"]),
    ("red_gas", "CA", "red de gas", [r"red(?:es)? de gas"]),
    ("tanque_choque", "T", "tanque de choque / pulmón", [r"tanques? de choque", r"\bpulmon\b", r"\btk de choque"]),
    ("pileta", "T", "pileta / tanque de fractura", [r"pileta", r"fractura", r"frac tank"]),
    ("acumulador", "T", "acumulador / botellón", [r"acumulador", r"botellon"]),
    ("tanque_atmosferico", "T", "tanque atmosférico (glicol, cónico)", [r"glicol", r"conico", r"atmosferic"]),
    ("plataforma", "EST", "estructura / plataforma", [r"plataforma", r"estructura"]),
    ("soporte", "EST", "soportes / mojones / postes", [r"soporte", r"mojon", r"poste"]),
    ("valvula_instrumento", "V", "válvulas de aguja, bloqueo y purga", [r"aguja", r"bloqueo y purga"]),
]
_SUB = [(c, f, n, [re.compile(x) for x in pats]) for c, f, n, pats in SUBTIPOS]
SUBTIPO_FAMILIA = {c: f for c, f, _, _ in SUBTIPOS}
SUBTIPO_NOMBRE = {c: n for c, _, n, _ in SUBTIPOS}
# Familias de recipientes: ahí el diámetro que importa es el del cuerpo, no el de las conexiones
RECIPIENTES = {"SEP", "F", "T", "C"}


def subtipo_en(t, familia=None):
    """Primer subtipo (del más específico al más general) cuyo patrón aparece en t; con familia, solo los de esa familia."""
    for c, f, _, rxs in _SUB:
        if (familia is None or f == familia) and any(rx.search(t) for rx in rxs):
            return c
    return ""


def subtipos_en(principal, sub=""):
    """Todos los subtipos que nombra el texto (el nombre de la carpeta o el título), con el principal primero: un
    proyecto puede traer varios equipos ("filtro FM y skid salto de regulación"). No se usa la descripción entera:
    "separador ... para ERP" no es un skid de regulación."""
    t = canon(norm(principal))
    out = [sub] if sub else []
    for c, _, _, rxs in _SUB:
        if c not in out and any(rx.search(t) for rx in rxs):
            out.append(c)
    return " ".join(out)


def familia_en(t):
    """Familia por la palabra clave que aparece primero en el texto (no por el orden de la tabla): en "skid calentador"
    manda skid, en "filtro FM y skid" manda filtro."""
    pos = []
    for k, claves in CLAVES.items():
        for c in claves:
            i = t.find(c)
            if i >= 0:
                pos.append((i, k))
    for _, f, _, rxs in _SUB:  # los subtipos también cuentan como palabra de su familia ("antorcha" → CA)
        for rx in rxs:
            m = rx.search(t)
            if m:
                pos.append((m.start(), f))
    return min(pos)[1] if pos else ""


def clasificar(principal, resto="", fam_dada=""):
    """Familia, etiquetas y subtipo de un proyecto o de un pedido, para todas las familias.

    principal: lo que dice qué es (título, carpeta, descripción corta, equipo); resto: ítems y datos técnicos.
    Familia: la dada (ficha o cotización) → la de la palabra clave que aparece primero en el principal → en el resto.
    Subtipo: del principal (primero los de su familia, después los de otra) → del resto, pero solo entre los de su familia (un "manifold de 2 vías" del manómetro no vuelve manifold a un separador)."""
    p, r = canon(norm(principal)), canon(norm(resto))
    fam = (fam_dada or "").strip().split(" ")[0].upper()
    fam = fam if fam in FAMILIAS and fam != "OT" else ""
    if not fam:
        fam = familia_en(p) or familia_en(r) or "OT"
    # primero un subtipo de su familia; si no, uno de otra ("separador coalescente": SEP con subtipo coalescente)
    sub = subtipo_en(p, fam) or subtipo_en(p)
    if not sub:
        sub = subtipo_en(r, fam)
    tags = [fam] + [k for k in etiquetas("", p + " " + r) if k != fam]
    if len(tags) > 1 and "OT" in tags:
        tags.remove("OT")
    return fam, tags, sub


def diametro_cuerpo(t):
    """Ø del cuerpo de un recipiente en pulgadas (cuerpo, virola, envolvente, casquete, Ø ext en mm, o "separador 28""),
    o None. Las conexiones no cuentan: en recipientes el tamaño es el cuerpo. Recibe el texto original."""
    t = canon(norm(re.sub(r"[”″“]", '"', str(t or ""))))
    pul = r'(\d{1,3}(?:[.,]\d{1,3})?)\s?(?:"|”|\'\'|pulg)'
    for rx in (r"(?:cuerpo|virola|envolvente|casco|shell)[^0-9,;:]{0,25}?" + pul,
               r"casquetes?[^,;]{0,30}?diam ?" + pul):
        for m in re.finditer(rx, t):
            v = float(m.group(1).replace(",", "."))
            if 6 <= v <= 160:
                return v
    for m in re.finditer(r"(?:cuerpo|virola|envolvente|casco|shell)?[^0-9,;]{0,20}?(?:diam(?:etro)?\.?|\bd\.?)\s?(?:ext(?:erior)?\.?|int(?:erior)?\.?)?\s?(?:de )?(\d[\d.,]{2,6})\s?(?:mm|x ?\d[\d.,]* ?mm)", t):
        v = float(m.group(1).replace(".", "").replace(",", ".")) if re.search(r"\d\.\d{3}", m.group(1)) else float(m.group(1).replace(",", "."))
        if 250 <= v <= 4000:
            return round(v / 25.4, 1)
    for m in re.finditer(r"(\d[\d.,]{2,6})\s?mm (?:de )?diam", t):  # "2.286 mm diam. x 8.100 mm"
        v = float(m.group(1).replace(".", "").replace(",", ".")) if re.search(r"\d\.\d{3}", m.group(1)) else float(m.group(1).replace(",", "."))
        if 250 <= v <= 4000:
            return round(v / 25.4, 1)
    for m in re.finditer(r"(?:separador|coalescente|tanque|recipiente|\bkod\b|slugcatcher|scrubber|pulmon|desgasificador)[^,;:\"”]{0,40}?(?:diam ?)?" + pul, t):
        v = float(m.group(1).replace(",", "."))
        if 6 <= v <= 160:
            return v
    return None
VACIAS = set("""para con sin por los las del de la el en y o a un una que se al su sus como mas segun desde hasta entre sobre
tipo incluye incluido incluida item items unidad unidades cotizacion cotizar oferta pedido precio precios total usd pesos
cliente proyecto equipo equipos provision fabricacion construccion suministro segun detalle rev revision doc nro numero
diseno preliminar concurso concursos grados""".split())


FRACCIONES = {"½": " 1/2", "¼": " 1/4", "¾": " 3/4", "⅛": " 1/8", "⅜": " 3/8", "⅝": " 5/8", "⅞": " 7/8", "\u2044": "/", "ø": " diam ", "Ø": " diam ", "⌀": " diam ", "°": " grados ", "º": " grados "}  # "codo 45° 1/2"" no es 45,5"


def norm(t):
    t = str(t or "")
    for a, b in FRACCIONES.items():  # antes de NFKD: si no, "½" queda "12"
        t = t.replace(a, b)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def frac(s):
    s = s.strip()
    tot = 0.0
    for p in s.split():
        if "/" in p:
            a, b = p.split("/")
            tot += float(a) / float(b)
        else:
            tot += float(p)
    return tot


PULGADAS = r'(?<![\d/.,])(\d{1,2}[.,]\d{1,2}|\d{1,2}(?:[ -]\d{1,2}/\d{1,2})?|\d{1,2}/\d{1,2})\s?(?:"|”|\'\'|pulgadas|pulg(?![\w-]*eq)|in\b)'


def pulgadas(t):
    """Diámetros en pulgadas en el orden en que aparecen: 2", 1 1/2", 1-1/2", 3/4", 2.5" o 2,5"."""
    out = []
    for m in re.finditer(PULGADAS, t):
        try:
            v = frac(m.group(1).replace("-", " ").replace(",", "."))
        except (ValueError, ZeroDivisionError):
            continue
        if 0.125 <= v <= 60 and v not in out:
            out.append(v)
    return out


DIAM_TEXTO = r"(?:\bo(?=\d)|\bdiam\.?|\bdiametro)\s?(\d{1,2})(?![\d.,/])"
_SER = r"(150|300|600|900|1500|2000|2500|3000|5000|6000|10000)"
SERIES_RX = [r"#\s?" + _SER + r"(?!\d)", r"\b" + _SER + r"\s?#", r"\b(?:cl|clase|class|serie|s|ansi|wog)[\s.\-]?" + _SER + r"(?!\d)",
             r"\b" + _SER + r"\s?(?:lbs?|psi)\b"]
# material y unión (también los usa la página: web/src/antecedentes.js los recibe en datos.json)
MATERIALES_RX = [("inoxidable", r"inox|aisi ?3(04|16)|\b316l?\b|\b304\b|duplex|a312"),
                 ("carbono", r"a ?106|a ?53\b|carbono|a ?105|a ?234|a ?516|api 5l|wcb")]
UNIONES_RX = [("roscado", r"\bnpt\b|roscad"), ("bridado", r"brida|\brtj\b|\brf\b|\bwn\b|welding neck")]


def diametros(t):
    out = set(pulgadas(t))
    for m in re.finditer(DIAM_TEXTO, t):
        v = float(m.group(1))
        if 1 <= v <= 60:
            out.add(v)
    return sorted(out)


def series(t):
    out = set()
    for rx in SERIES_RX:
        out.update(re.findall(rx, t))
    return sorted(out, key=int)


def atributos(t):
    mat = [k for k, rx in MATERIALES_RX if re.search(rx, t)]
    union = [k for k, rx in UNIONES_RX if re.search(rx, t)]
    ens = [e for e, rx in (("RX", r"\brx\b|radiograf"), ("PH", r"\bph\b|prueba hidr"), ("ultrasonido", r"ultrason|\but\b"),
                           ("pintura", r"pintura|granallad")) if re.search(rx, t)]
    return mat, union, ens


def etiquetas(fam_ficha, t):
    tags = []
    f = (fam_ficha or "").strip().split(" ")[0].upper()
    if f in FAMILIAS:
        tags.append(f)
    for k, claves in CLAVES.items():
        if any(c in t for c in claves) and k not in tags:
            tags.append(k)
    if len(tags) > 1 and "OT" in tags:
        tags.remove("OT")
    return tags or ["OT"]


CORTAS = {"aib", "noc", "kod", "rtj", "npt", "bdp", "psv", "sdv", "bpr", "gas", "rdo", "ypf", "pae"}


def raiz(w):
    """Raíz simple: saca plural y vocal final (puentes/puente -> puent, colectores -> colector)."""
    if len(w) > 4 and w.endswith("s"):
        w = w[:-1]
    if len(w) > 4 and w[-1] in "eo":
        w = w[:-1]
    return w


def palabras(t):
    ws = {w for w in re.findall(r"[a-z][a-z0-9]{2,}", t) if (len(w) > 3 or w in CORTAS) and w not in VACIAS}
    return sorted({raiz(w) for w in ws})


def contenido_carpeta(carpeta):
    d = TEXTOS / carpeta
    archivos = [p for p in d.rglob("*") if p.is_file()] if d.is_dir() else []
    nombres = [str(p.relative_to(d)) for p in archivos]
    planilla = any(("4.Armado" in n or "costo" in norm(n) or "planilla" in norm(n)) and ".xls" in n.lower() for n in nombres)
    if not planilla:
        for p in archivos:
            if ".xls" in p.name.lower():
                try:
                    tx = norm(p.read_text(encoding="utf-8", errors="ignore")[:200000])
                except OSError:
                    continue
                if "factor de rentabilidad" in tx or "costo unit" in tx or "costo nacional" in tx:
                    planilla = True
                    break
    enviada = any(n.startswith("7.") or n.startswith("6.") for n in nombres)
    return planilla, enviada


def cuerpo_de(fam, texto):
    """Ø del cuerpo solo para recipientes (separadores, filtros, tanques, calentadores); en el resto, vacío."""
    v = diametro_cuerpo(texto) if fam in RECIPIENTES else None
    return f"{v:g}" if v else ""


# equipo.tipo de cotizacion.json (el tipo de MO del motor) → familia, cuando no hay equipo.familia ni texto que alcance
TIPO_FAMILIA = {"skid": "SK", "puente": "P", "filtro": "F", "manifold": "M", "prefabricado": "CA", "tanque": "T",
                "trampa": "TS", "separador": "SEP", "calentador": "C", "colector": "CO"}


def clasificar_cotizacion(c):
    """Familia, etiquetas, subtipo y Ø del cuerpo de una cotización del cotizador (cotizacion.json o la de la página).

    Manda lo que diga equipo.familia / equipo.subtipo; si no, el título y el nombre del equipo (no los ítems: un
    "manifold de 2 vías" del manómetro no vuelve manifold a un separador). Ø del cuerpo: equipo.diametro_pulg en
    recipientes."""
    eq = c.get("equipo") or {}
    principal = " ".join([eq.get("singular", ""), c.get("titulo", "")])
    resto = " ".join(f"{i.get('descripcion', '')} {i.get('especificacion', '')}" for i in c.get("items", []))
    fam_dada = eq.get("familia") or ""
    if not fam_dada:
        fam_dada = familia_en(canon(norm(principal))) or TIPO_FAMILIA.get(eq.get("tipo", ""), "")
    fam, tags, sub = clasificar(principal, resto, fam_dada)
    sub = eq.get("subtipo") or sub
    cuerpo = None
    if fam in RECIPIENTES:
        cuerpo = num(eq.get("diametro_pulg")) or diametro_cuerpo(principal + " " + resto)
    return fam, tags, sub, cuerpo


def de_ficha(d, anio):
    carpeta = d["carpeta"]
    items = d.get("items") or []
    texto = " ".join([carpeta, d.get("descripcion_corta") or "", d.get("referencia_cliente") or ""] +
                     [f"{i.get('descripcion', '')} {i.get('datos_tecnicos', '')}" for i in items] +
                     [str(pr.get("que") or "") for pr in (d.get("proveedores") or [])])
    t = canon(norm(texto))
    mat, union, ens = atributos(t)
    principal = " ".join([carpeta.split("/")[-1], d.get("descripcion_corta") or ""])
    fam, tags, sub = clasificar(principal, texto, d.get("familia"))
    planilla, enviada = contenido_carpeta(carpeta)
    planilla = planilla or bool(num(d.get("costo_total")) or num(d.get("factor_venta")))
    precios = [(num(i.get("precio_unitario")) or 0, i) for i in items if num(i.get("precio_unitario"))]
    principal = max(precios, key=lambda x: x[0])[1] if precios else None
    fecha = d.get("fecha_oferta") or d.get("fecha_ultima_modificacion") or f"{anio}-01-01"
    oc = d.get("orden_compra") or {}
    return {
        "id": f"{carpeta}", "origen": f"fichas_{anio}", "fecha": fecha[:10], "cliente": d.get("cliente") or "",
        "cliente_final": d.get("cliente_final") or "", "familia": fam, "etiquetas": " ".join(tags), "subtipo": sub,
        "subtipos": subtipos_en(carpeta.split("/")[-1], sub), "descripcion": d.get("descripcion_corta") or "", "numero_oferta": d.get("numero_oferta") or "",
        "diametros": " ".join(f"{x:g}" for x in diametros(t)), "diametro_cuerpo": cuerpo_de(fam, texto),
        "series": " ".join(series(t)), "material": " ".join(mat), "union": " ".join(union), "ensayos": " ".join(ens),
        "cantidad_principal": num(principal.get("cantidad")) if principal else "",
        "precio_unitario_principal": r2(num(principal.get("precio_unitario"))) if principal else "",
        "monto": r2(num(d.get("monto_total_ofertado"))) or "", "moneda": d.get("moneda") or "", "costo": r2(num(d.get("costo_total"))) or "",
        "factor": num(d.get("factor_venta")) or "", "plazo_dias": num(d.get("plazo_dias")) or "",
        "resultado": d.get("resultado") or "", "tiene_planilla_costo": "si" if planilla else "",
        "proveedores": len(d.get("proveedores") or []), "tiene_oferta_enviada": "si" if enviada else "",
        "tiene_oc": "si" if (oc and oc.get("numero")) or str(d.get("resultado", "")).startswith("ganada") else "",
        "confianza": d.get("confianza") or "", "palabras": " ".join(palabras(t)),
        "ficha": f"conocimiento/fichas_{anio}/", "carpeta_textos": f"fuentes_originales/ofertas_texto/{carpeta}",
    }


def r2(v):
    """Montos y precios con 2 decimales (decisión de Matías, 29-10-2026)."""
    return round(v, 2) if isinstance(v, (int, float)) and not isinstance(v, bool) else v


def de_cotizador(ruta):
    c = json.load(open(ruta, encoding="utf-8"))
    texto = " ".join([c.get("titulo", ""), c.get("subtitulo_planilla", "")] +
                     [f"{i['descripcion']} {i.get('especificacion', '')}" for i in c.get("items", [])])
    t = canon(norm(texto))
    mat, union, ens = atributos(t)
    fam, tags, sub, cuerpo = clasificar_cotizacion(c)
    return {
        "id": ruta.parent.name, "origen": "cotizador" if ruta.parent.parent.name == "cotizaciones" else "pagina", "fecha": c.get("fecha", ""), "cliente": c["cliente"]["nombre"], "cliente_final": "",
        "familia": fam, "etiquetas": " ".join(tags), "subtipo": sub,
        "subtipos": subtipos_en(" ".join([(c.get("equipo") or {}).get("singular", ""), c.get("titulo", "")]), sub), "descripcion": c.get("titulo", ""),
        "numero_oferta": c.get("codigo", ""), "diametros": " ".join(f"{x:g}" for x in diametros(t)),
        "diametro_cuerpo": cuerpo or "", "series": " ".join(series(t)),
        "material": " ".join(mat), "union": " ".join(union), "ensayos": " ".join(ens), "cantidad_principal": c["parametros"]["N"],
        "precio_unitario_principal": "", "monto": "", "moneda": "USD", "costo": "", "factor": c["parametros"]["FM"],
        "plazo_dias": c.get("plazo", {}).get("dias", ""), "resultado": c.get("estado", ""), "tiene_planilla_costo": "si",
        "proveedores": "", "tiene_oferta_enviada": "", "tiene_oc": "", "confianza": "", "palabras": " ".join(palabras(t)),
        "ficha": str(ruta.relative_to(RAIZ)), "carpeta_textos": str(ruta.parent.relative_to(RAIZ)),
    }


HISTORICO = RAIZ / "conocimiento" / "comercial" / "indice_historico.csv"
ETAPA = re.compile(r"(?i)^\s*\d\s*\.\s*(documentaci|armado|proveedores|propuesta|orden de compra)")


def anio_carpeta(d):
    """Año más frecuente en las fechas de los textos de la carpeta (dd/mm/aaaa, aaaa-mm-dd y números de oferta
    "OE 201-22"). Es estimado: estas carpetas no tienen ficha."""
    from collections import Counter
    ys = Counter()
    for f in d.rglob("*.txt"):
        try:
            t = f.read_text(encoding="utf-8", errors="ignore")[:100000]
        except OSError:
            continue
        ys.update(int(m.group(1)) for m in re.finditer(r"\b\d{1,2}[/.-]\d{1,2}[/.-](20(?:1[89]|2\d))\b", t))
        ys.update(int(m.group(1)) for m in re.finditer(r"\b(20(?:1[89]|2\d))-\d\d-\d\d", t))
        ys.update(2000 + int(m.group(1)) for m in re.finditer(r"(?i)\b(?:OE|OT|PRES)\s*0?\s*\d{2,3}\s*[- ]\s*(\d{2})\b", t + " " + f.name))
    ys = Counter({y: n for y, n in ys.items() if 2018 <= y <= 2026})
    return ys.most_common(1)[0][0] if ys else None


def texto_oferta(d, limite=60000):
    """Texto de la oferta enviada (7.*) o, si no hay, del armado (4.*), sin planillas: para clasificar y medir."""
    for etapa in ("7.", "6.", "4."):
        arch = [f for e in d.iterdir() if e.is_dir() and e.name.strip().startswith(etapa) for f in e.rglob("*.txt")
                if not re.search(r"\.xlsx?\.txt$", f.name, re.I)]
        if arch:
            return " ".join(f.read_text(encoding="utf-8", errors="ignore")[:limite // len(arch) + 1] for f in sorted(arch))[:limite]
    return ""


def historico(con_ficha):
    """Carpetas de ofertas sin ficha (2021–2024 y las de 2025–2026 que todavía no tienen): familia, subtipo, Ø y año
    estimados desde el nombre y los textos. No tienen precios: sirven para comparar diseño y alcance, y avisar qué
    carpetas de 2025–2026 falta fichar."""
    filas = []
    carpetas = sorted({d.parent for d in TEXTOS.rglob("*") if d.is_dir() and ETAPA.match(d.name)})
    vistas = set()
    for d in carpetas:
        rel = str(d.relative_to(TEXTOS))
        if (rel in con_ficha or any(c.startswith(rel + "/") for c in con_ficha)  # ficha hecha sobre una subcarpeta
                or rel in vistas or any(rel.startswith(v + "/") for v in vistas)):
            continue  # una carpeta por proyecto (las etapas anidadas no son otro proyecto)
        vistas.add(rel)
        y = anio_carpeta(d)
        nombre = " ".join(rel.split("/")[1:]) or rel
        of = texto_oferta(d)
        fam, tags, sub = clasificar(nombre, of)
        t = canon(norm(nombre + " " + of))
        mat, union, ens = atributos(t)
        planilla, enviada = contenido_carpeta(rel)
        filas.append({
            "id": rel, "origen": "carpeta sin ficha", "fecha": f"{y}-07-01" if y else "", "fecha_estimada": "si",
            "cliente": rel.split("/")[0], "familia": fam, "etiquetas": " ".join(tags), "subtipo": sub,
            "subtipos": subtipos_en(nombre, sub),
            "descripcion": nombre, "diametros": " ".join(f"{x:g}" for x in diametros(canon(norm(nombre + " " + of[:5000])))),
            "diametro_cuerpo": cuerpo_de(fam, nombre + " " + of[:20000]), "series": " ".join(series(canon(norm(nombre + " " + of[:5000])))),
            "material": " ".join(mat), "union": " ".join(union), "tiene_planilla_costo": "si" if planilla else "",
            "tiene_oferta_enviada": "si" if enviada else "", "tiene_oc": "si" if any(e.name.strip().startswith("8.") for e in d.iterdir()) else "",
            "palabras": " ".join(palabras(canon(norm(nombre)))), "carpeta_textos": f"fuentes_originales/ofertas_texto/{rel}",
        })
    filas.sort(key=lambda r: (r["fecha"], r["id"]), reverse=True)
    with open(HISTORICO, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    nuevas = [r["id"] for r in filas if r["fecha"] >= "2025-01-01"]
    print(f"{HISTORICO.relative_to(RAIZ)}: {len(filas)} carpetas sin ficha ({len(nuevas)} de 2025–2026: falta su ficha)")
    return filas


def main():
    filas = []
    con_ficha = set()
    for anio in ("2026", "2025"):
        for f in sorted((RAIZ / "conocimiento" / f"fichas_{anio}").glob("*.json")):
            d = json.load(open(f, encoding="utf-8"))
            con_ficha.add(d["carpeta"])
            fila = de_ficha(d, anio)
            fila["ficha"] = str(f.relative_to(RAIZ))
            filas.append(fila)
    from cotizaciones_base import cotizaciones  # la biblioteca: las incorporadas con el botón de la página
    for f, _ in cotizaciones():
        filas.append(de_cotizador(f))
    filas = [r for r in filas if r["fecha"] >= "2025-01-01"]  # solo 2025-2026 (decisión de Ventas)
    filas.sort(key=lambda r: r["fecha"], reverse=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    from collections import Counter
    c = Counter(t for r in filas for t in r["etiquetas"].split())
    print(f"{SALIDA.relative_to(RAIZ)}: {len(filas)} proyectos")
    print("por familia (un proyecto puede tener varias):", ", ".join(f"{k} {v}" for k, v in c.most_common()))
    print("con planilla de costo:", sum(1 for r in filas if r["tiene_planilla_costo"]))
    print("con subtipo:", sum(1 for r in filas if r["subtipo"]), "· con Ø de cuerpo:", sum(1 for r in filas if r["diametro_cuerpo"]))
    historico(con_ficha)


if __name__ == "__main__":
    main()
