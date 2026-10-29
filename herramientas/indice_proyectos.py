"""Arma el índice de proyectos (antecedentes) para buscar cotizaciones parecidas: conocimiento/comercial/indice_proyectos.csv

Uso: python herramientas/indice_proyectos.py

Fuentes:
  conocimiento/fichas_2025/ y fichas_2026/   cotizaciones analizadas de la carpeta Z:\\VENTAS\\OFERTAS Y LICITACIONES
  cotizaciones/*/cotizacion.json             cotizaciones armadas con el cotizador
Por decisión de Ventas (27/10/2026) el índice cubre solo 2025 y 2026; 2021–2024 no se incluye.

Por cada proyecto: familia y etiquetas (un proyecto puede ser "skid" y "filtro"), datos técnicos normalizados
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
VACIAS = set("""para con sin por los las del de la el en y o a un una que se al su sus como mas segun desde hasta entre sobre
tipo incluye incluido incluida item items unidad unidades cotizacion cotizar oferta pedido precio precios total usd pesos
cliente proyecto equipo equipos provision fabricacion construccion suministro segun detalle rev revision doc nro numero""".split())


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


def diametros(t):
    out = set(pulgadas(t))
    for m in re.finditer(r"(?:\bo(?=\d)|\bdiam\.?|\bdiametro)\s?(\d{1,2})(?![\d.,/])", t):
        v = float(m.group(1))
        if 1 <= v <= 60:
            out.add(v)
    return sorted(out)


def series(t):
    out = set()
    pat = r"(150|300|600|900|1500|2000|2500|3000|5000|6000|10000)"
    for rx in (r"#\s?" + pat + r"(?!\d)", r"\b" + pat + r"\s?#", r"\b(?:cl|clase|class|serie|s|ansi|wog)[\s.\-]?" + pat + r"(?!\d)",
               r"\b" + pat + r"\s?(?:lbs?|psi)\b"):
        out.update(re.findall(rx, t))
    return sorted(out, key=int)


def atributos(t):
    mat = []
    if re.search(r"inox|aisi ?3(04|16)|\b316l?\b|\b304\b|duplex|a312", t):
        mat.append("inoxidable")
    if re.search(r"a ?106|a ?53\b|carbono|a ?105|a ?234|a ?516|api 5l|wcb", t):
        mat.append("carbono")
    union = []
    if re.search(r"\bnpt\b|roscad", t):
        union.append("roscado")
    if re.search(r"brida|\brtj\b|\brf\b|\bwn\b|welding neck", t):
        union.append("bridado")
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


def de_ficha(d, anio):
    carpeta = d["carpeta"]
    items = d.get("items") or []
    texto = " ".join([carpeta, d.get("descripcion_corta") or "", d.get("referencia_cliente") or ""] +
                     [f"{i.get('descripcion', '')} {i.get('datos_tecnicos', '')}" for i in items] +
                     [str(pr.get("que") or "") for pr in (d.get("proveedores") or [])])
    t = norm(texto)
    mat, union, ens = atributos(t)
    planilla, enviada = contenido_carpeta(carpeta)
    planilla = planilla or bool(num(d.get("costo_total")) or num(d.get("factor_venta")))
    precios = [(num(i.get("precio_unitario")) or 0, i) for i in items if num(i.get("precio_unitario"))]
    principal = max(precios, key=lambda x: x[0])[1] if precios else None
    fecha = d.get("fecha_oferta") or d.get("fecha_ultima_modificacion") or f"{anio}-01-01"
    oc = d.get("orden_compra") or {}
    return {
        "id": f"{carpeta}", "origen": f"fichas_{anio}", "fecha": fecha[:10], "cliente": d.get("cliente") or "",
        "cliente_final": d.get("cliente_final") or "", "familia": etiquetas(d.get("familia"), t)[0],
        "etiquetas": " ".join(etiquetas(d.get("familia"), t)), "descripcion": d.get("descripcion_corta") or "",
        "numero_oferta": d.get("numero_oferta") or "", "diametros": " ".join(f"{x:g}" for x in diametros(t)),
        "series": " ".join(series(t)), "material": " ".join(mat), "union": " ".join(union), "ensayos": " ".join(ens),
        "cantidad_principal": num(principal.get("cantidad")) if principal else "",
        "precio_unitario_principal": num(principal.get("precio_unitario")) if principal else "",
        "monto": num(d.get("monto_total_ofertado")) or "", "moneda": d.get("moneda") or "", "costo": num(d.get("costo_total")) or "",
        "factor": num(d.get("factor_venta")) or "", "plazo_dias": num(d.get("plazo_dias")) or "",
        "resultado": d.get("resultado") or "", "tiene_planilla_costo": "si" if planilla else "",
        "proveedores": len(d.get("proveedores") or []), "tiene_oferta_enviada": "si" if enviada else "",
        "tiene_oc": "si" if (oc and oc.get("numero")) or str(d.get("resultado", "")).startswith("ganada") else "",
        "confianza": d.get("confianza") or "", "palabras": " ".join(palabras(t)),
        "ficha": f"conocimiento/fichas_{anio}/", "carpeta_textos": f"fuentes_originales/ofertas_texto/{carpeta}",
    }


def de_cotizador(ruta):
    c = json.load(open(ruta, encoding="utf-8"))
    texto = " ".join([c.get("titulo", ""), c.get("subtitulo_planilla", "")] +
                     [f"{i['descripcion']} {i.get('especificacion', '')}" for i in c.get("items", [])])
    t = norm(texto)
    mat, union, ens = atributos(t)
    return {
        "id": ruta.parent.name, "origen": "cotizador" if ruta.parent.parent.name == "cotizaciones" else "pagina", "fecha": c.get("fecha", ""), "cliente": c["cliente"]["nombre"], "cliente_final": "",
        "familia": etiquetas("", t)[0], "etiquetas": " ".join(etiquetas("", t)), "descripcion": c.get("titulo", ""),
        "numero_oferta": c.get("codigo", ""), "diametros": " ".join(f"{x:g}" for x in diametros(t)), "series": " ".join(series(t)),
        "material": " ".join(mat), "union": " ".join(union), "ensayos": " ".join(ens), "cantidad_principal": c["parametros"]["N"],
        "precio_unitario_principal": "", "monto": "", "moneda": "USD", "costo": "", "factor": c["parametros"]["FM"],
        "plazo_dias": c.get("plazo", {}).get("dias", ""), "resultado": c.get("estado", ""), "tiene_planilla_costo": "si",
        "proveedores": "", "tiene_oferta_enviada": "", "tiene_oc": "", "confianza": "", "palabras": " ".join(palabras(t)),
        "ficha": str(ruta.relative_to(RAIZ)), "carpeta_textos": str(ruta.parent.relative_to(RAIZ)),
    }


def main():
    filas = []
    for anio in ("2026", "2025"):
        for f in sorted((RAIZ / "conocimiento" / f"fichas_{anio}").glob("*.json")):
            fila = de_ficha(json.load(open(f, encoding="utf-8")), anio)
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


if __name__ == "__main__":
    main()
