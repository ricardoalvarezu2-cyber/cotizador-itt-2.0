"""Reglas de compatibilidad para el buscador de materiales: qué pieza del catálogo puede servir de "similar" para lo que
pide el cliente y cuál no, aunque se parezca (Matías, 30-10-2026: "no poner una comparativa entre dos válvulas que la
norma no lo permite").

Uso: from compatibilidad import incompatible
     motivo = incompatible(familia, atributos_pedido, atributos_candidato, texto_pedido, texto_candidato)
     "" si puede ser similar; si no, el motivo (se muestra al descartar).
     python herramientas/compatibilidad.py "A105" "A216 WCB"   (prueba rápida de dos materiales)

Las reglas y sus fuentes están en conocimiento/tecnico/compatibilidades_LEEME.md; los materiales, en
conocimiento/tecnico/compatibilidad_materiales.csv (patrón, clase, grupo de ASME B16.5 tabla 1A, forma). La página usa las
mismas reglas (web/src/busqueda.js, datos.json → compat) y test_compatibilidad.py controla que den lo mismo.

Reglas (todas solo cuando los dos lados tienen el dato; sin dato no se descarta):
1. Material: misma clase (carbono, carbono para baja temperatura, alta resistencia, 316, 316L, 304, dúplex, bulonería B7…).
   Se acepta el reemplazo "hacia arriba" que la norma admite: LF2 por A105, 316L por 316, B7M por B7, A516 por A36; nunca al
   revés. En válvulas y bridas, además, el mismo grupo de presión-temperatura de B16.5 (A105 y A216 WCB son 1.1: sí;
   WCC es 1.2: no). Grados de alta resistencia (API 5L X52, WPHY 52, F52): el grado tiene que coincidir.
2. Cara de brida: RF, FF y RTJ no se reemplazan entre sí.
3. Roscas y socket weld: NPT y BSPT son roscas distintas; roscado y SW no se reemplazan. El extremo para soldar (BW) que el
   catálogo no anota en una brida WN ("RF") o en un olet ("SW") no cuenta como diferencia.
4. Schedule (caños, niples y accesorios a tope): tiene que coincidir; STD = 40 hasta 10", XS = 80 hasta 8" y 40S/80S = 40/80
   hasta 10"/8" (ASME B36.10 y B36.19).
5. Servicio ácido: si el pedido dice NACE / MR0175 / servicio ácido, el candidato tiene que decir NACE.
La serie y la norma de la pieza ya las controla buscar_material.py (regla del 29-10-2026).
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TABLA = RAIZ / "conocimiento" / "tecnico" / "compatibilidad_materiales.csv"
# reemplazos admitidos: clase pedida -> clases que la pueden reemplazar (además de la misma)
REEMPLAZA = {
    "carbono": {"carbono_baja_temp"},
    "carbono_estructural": {"carbono", "carbono_baja_temp"},
    "inox_316": {"inox_316l"},
    "inox_304": {"inox_304l", "inox_316", "inox_316l"},
    "bulon_b7": {"bulon_b7m"},
    "tuerca_2h": {"tuerca_2hm"},
    "inox": {"inox_316", "inox_316l", "inox_304", "inox_304l"},  # inoxidable sin grado: referencia de cualquiera
}
GENERICOS = {"inox"}  # un candidato "inoxidable" sin grado sirve de referencia para cualquier inoxidable
CARAS = {"rf", "ff", "rtj"}
ROSCAS_Y_SOLDADURA = {"npt", "bspt", "sw", "bw"}
NACE = r"\bnace\b|\bmr ?0175\b|\bmr ?0103\b|iso ?15156|servicio acido|sour"
FAMILIAS_SCH = {"CAN", "NIP", "ABW"}

_MAT = None


def materiales():
    global _MAT
    if _MAT is None:
        _MAT = [{**r, "rx": re.compile(r["patron"])} for r in csv.DictReader(open(TABLA, encoding="utf-8"))]
    return _MAT


def clase_material(texto):
    """Fila de compatibilidad_materiales.csv del material (la primera que coincide) o None."""
    t = norm(texto)
    if not t.strip():
        return None
    return next((m for m in materiales() if m["rx"].search(t)), None)


def grado(texto):
    m = re.search(r"\b(?:x|wphy|f) ?(\d{2})\b", norm(texto))
    return m.group(1) if m else ""


def bulones(texto):
    """Clases de bulonería y tuercas que nombra el texto (un espárrago "B7 / 2H" trae las dos)."""
    t = norm(texto)
    return {m["clase"] for m in materiales() if m["clase"].startswith(("bulon", "tuerca")) and m["rx"].search(t)}


def regla_material(fam, pedido, cand):
    ba, bb = bulones(pedido), bulones(cand)
    if ba and bb:  # bulonería: bulón con bulón y tuerca con tuerca
        for tipo in ("bulon", "tuerca"):
            xa, xb = {c for c in ba if c.startswith(tipo)}, {c for c in bb if c.startswith(tipo)}
            if xa and xb and not any(y == x or y in REEMPLAZA.get(x, set()) for x in xa for y in xb):
                return f"bulonería {'/'.join(sorted(xb)).replace('_', ' ')} no reemplaza a {'/'.join(sorted(xa)).replace('_', ' ')}"
        return ""
    a, b = clase_material(pedido), clase_material(cand)
    if not a or not b:
        return ""
    ca, cb = a["clase"], b["clase"]
    generico = cb in GENERICOS and ca.startswith(cb)  # "inoxidable" sin grado sirve solo para otro inoxidable
    if ca != cb and cb not in REEMPLAZA.get(ca, set()) and not generico:
        return f"material {b['material']} no reemplaza a {a['material']} ({cb.replace('_', ' ')} por {ca.replace('_', ' ')})"
    if ca == cb == "carbono_alta_resistencia" and grado(pedido) and grado(cand) and grado(pedido) != grado(cand):
        return f"grado {grado(cand)} distinto del pedido ({grado(pedido)})"
    if fam in ("VAL", "BRI") and a["grupo_b16_5"] and b["grupo_b16_5"] and a["grupo_b16_5"] != b["grupo_b16_5"] and ca == cb:
        return f"otro grupo de presión-temperatura de B16.5 ({b['grupo_b16_5']} por {a['grupo_b16_5']})"
    return ""


def conexiones(*textos):
    """Tipos de conexión: caras de brida (rf, ff, rtj), 'brida' sin cara, npt, bspt, sw, bw."""
    out = set()
    for t in textos:
        t = norm(t)
        for k in CARAS | ROSCAS_Y_SOLDADURA:
            if re.search(rf"\b{k}\b", t):
                out.add(k)
        if re.search(r"\bbridad|\bbrida\b", t) and not out & CARAS:
            out.add("brida")
    return out


def regla_conexion(pedido, cand):
    """Compara cara con cara y rosca con rosca. El catálogo suele guardar solo la cara de una brida WN ("RF") o solo la
    salida de un olet ("SW"): el extremo para soldar que falta de un lado no cuenta como diferencia."""
    if not pedido or not cand:
        return ""
    txt = f"extremos o cara distintos ({'/'.join(sorted(cand)).upper()} por {'/'.join(sorted(pedido)).upper()})"
    ca, cb = pedido & CARAS, cand & CARAS
    if ca and cb and ca != cb:
        return txt
    ra, rb = pedido & {"npt", "bspt"}, cand & {"npt", "bspt"}
    if ra and rb and ra != rb:
        return txt
    # roscado contra socket weld (o al revés), cuando uno no tiene lo del otro
    if (ra and not rb and "sw" in cand and "sw" not in pedido) or (rb and not ra and "sw" in pedido and "sw" not in cand):
        return txt
    return ""


def sch_canonico(sch, dn):
    s = str(sch or "").upper().replace("SCH", "").strip()
    try:
        d = float(dn)
    except (TypeError, ValueError):
        d = None
    if s in ("STD", "40S") and (d is None or d <= 10):
        return "40"
    if s in ("XS", "80S") and (d is None or d <= 8):
        return "80"
    return s


def dn_de(v):
    m = re.match(r"\s*(\d+(?:[.,]\d+)?)", str(v or ""))
    return float(m.group(1).replace(",", ".")) if m else None


def incompatible(fam, at_pedido, at_cand, texto_pedido="", texto_cand=""):
    """Motivo por el que el candidato NO puede ser similar del pedido ("" si puede)."""
    m = regla_material(fam, at_pedido.get("material", ""), at_cand.get("material", ""))
    if m:
        return m
    c = regla_conexion(conexiones(at_pedido.get("extremos", ""), at_pedido.get("cara", "")),
                       conexiones(at_cand.get("extremos", ""), at_cand.get("cara", "")))
    if c:
        return c
    if fam in FAMILIAS_SCH and at_pedido.get("schedule") and at_cand.get("schedule"):
        dn = dn_de(at_pedido.get("diametro"))
        if sch_canonico(at_pedido["schedule"], dn) != sch_canonico(at_cand["schedule"], dn):
            return f"schedule {at_cand['schedule']} por {at_pedido['schedule']} (otro espesor)"
    if re.search(NACE, norm(texto_pedido)) and not re.search(NACE, norm(texto_cand)):
        return "el pedido es para servicio ácido (NACE) y el candidato no lo dice"
    return ""


def para_pagina():
    """Lo que necesita web/src/busqueda.js para aplicar las mismas reglas (va en datos.json → compat)."""
    return {"materiales": [{k: r[k] for k in ("patron", "material", "clase", "grupo_b16_5")} for r in materiales()],
            "reemplaza": {k: sorted(v) for k, v in REEMPLAZA.items()}, "genericos": sorted(GENERICOS), "nace": NACE,
            "familias_sch": sorted(FAMILIAS_SCH)}


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    print(clase_material(a) and clase_material(a)["clase"], "|", clase_material(b) and clase_material(b)["clase"])
    print(regla_material("VAL", a, b) or "compatible")
