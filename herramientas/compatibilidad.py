"""Reglas de compatibilidad para el buscador de materiales: qué pieza del catálogo puede servir de "similar" para lo que
pide el cliente y cuál no, aunque se parezca (Matías, 30-10-2026: "no poner una comparativa entre dos válvulas que la
norma no lo permite"). Criterio: un reemplazo solo vale si el candidato es igual o superior en TODO (resistencia, rating
presión-temperatura, tenacidad, servicio); si no se puede probar, no es similar. Revisado por un revisor independiente el
30-10-2026 (conocimiento/tecnico/compatibilidades_LEEME.md).

Uso: from compatibilidad import incompatible
     motivo = incompatible(familia, atributos_pedido, atributos_candidato, texto_pedido, texto_candidato)
     "" si puede ser similar; si no, el motivo.
     python herramientas/compatibilidad.py "A105" "A216 WCB"   (prueba rápida de dos materiales)

Materiales: conocimiento/tecnico/compatibilidad_materiales.csv (patrón, clase, grupo de ASME B16.5 tabla 1A). La página usa
las mismas reglas (web/src/busqueda.js, datos.json → compat); test_compatibilidad.py controla que den lo mismo.

Reglas:
1. Material. Se juntan todas las clases que nombra el texto (doble certificación "316/316L", "A105/LF2"): el candidato
   tiene que cumplir cada una (misma clase o un reemplazo de REEMPLAZA). Los genéricos ("acero al carbono",
   "inoxidable") valen solo del lado del pedido. Si el pedido dice el material y el candidato no lo tiene (ni en la
   descripción), no es similar. Si el material del pedido no está en la tabla, solo vale el mismo texto.
   Además, si los dos tienen grupo de B16.5, el del candidato tiene que estar entre los admitidos (GRUPOS: un rating igual
   o mayor). Grados de alta resistencia (X52, WPHY 52, F52): el grado tiene que coincidir. Galvanizado y negro no se mezclan.
2. Conexión. Tipos: brida (RF/FF/RTJ), rosca (NPT/BSPT/BSPP), SW, BW. Si los dos tienen dato y no comparten ningún tipo,
   no es similar (una bridada no es referencia de una roscada). Dentro de un tipo: la cara y la rosca tienen que coincidir.
   El extremo que el catálogo no anota (BW de una WN "RF", el olet "SW") no cuenta como diferencia.
3. Schedule (caños, niples y accesorios a tope): tiene que coincidir; 40S = STD y 80S = XS; STD = 40 hasta 10" y XS = 80
   hasta 8" (ASME B36.10/B36.19). Sin diámetro, no se iguala STD con 40.
4. Servicio ácido: pedido con MR0175 / ISO 15156 → el candidato tiene que decir MR0175 o ISO 15156; pedido "NACE", "sour"
   o "H2S" → el candidato tiene que decir NACE (MR0175, MR0103 o ISO 15156).
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
# reemplazos admitidos: clase pedida -> clases que la pueden reemplazar (además de la misma). Solo "igual o superior en todo".
REEMPLAZA = {
    "carbono": {"carbono_baja_temp"},                       # LF2 / LCC por A105 o WCB (el grupo se controla aparte)
    "carbono_estructural": {"carbono"},                    # A516-70 por A36 (no A516-60/65)
    "cano_a106": {"cano_a106c", "carbono_baja_temp"},      # A106 C o A333 Gr 6 por A106 B
    "cano_a53": {"cano_a106", "cano_a106c"},
    "cano_api5l_b": {"cano_a106", "cano_a106c"},
    "a333_gr1": {"carbono_baja_temp"},
    "inox_304": {"inox_316", "inox_304l"},                 # 304L solo si su grupo alcanza (CF3, 2.1; F304L 2.3 no)
    "inox_304l": {"inox_316l"},
    "inox_316": {"inox_316l"},                             # 316L solo si su grupo alcanza (CF3M, 2.2; F316L 2.3 no)
    "duplex": {"superduplex"},
    "bulon_b7": {"bulon_l7"},
    "bulon_inox": {"bulon_b8m_cl2"},
    "tuerca_2h": {"tuerca_4_7"},
}
# genéricos del pedido: aceptan cualquiera de estas clases
GENERICOS = {
    "carbono_generico": {"carbono", "carbono_baja_temp", "cano_a106", "cano_a106c", "cano_a53", "cano_api5l_b", "carbono_estructural"},
    "inox": {"inox_316", "inox_316l", "inox_304", "inox_304l", "inox_347"},
}
# grupo de B16.5 pedido -> grupos admitidos en el candidato (rating igual o mayor)
GRUPOS = {"1.1": {"1.1", "1.2"}, "1.2": {"1.2"}, "1.3": {"1.3", "1.1", "1.2"}, "1.4": {"1.4", "1.3", "1.1", "1.2"},
          "2.1": {"2.1", "2.2"}, "2.2": {"2.2"}, "2.3": {"2.3", "2.1", "2.2"}}
CARAS = {"rf", "ff", "rtj"}
ROSCAS = {"npt", "bspt", "bspp"}
NACE_ESTRICTO = r"\bmr ?0175\b|iso ?15156"
NACE_PEDIDO = r"\bnace\b|\bmr ?0175\b|\bmr ?0103\b|iso ?15156|servicio acido|\bsour\b|\bh2s\b"
NACE_CAND = r"\bnace\b|\bmr ?0175\b|\bmr ?0103\b|iso ?15156"
FAMILIAS_SCH = {"CAN", "NIP", "ABW"}
GALV = r"galvaniz"
DN_NPS = {15: 0.5, 20: 0.75, 25: 1, 32: 1.25, 40: 1.5, 50: 2, 65: 2.5, 80: 3, 90: 3.5, 100: 4, 125: 5, 150: 6, 200: 8, 250: 10,
          300: 12, 350: 14, 400: 16, 450: 18, 500: 20, 600: 24}

_MAT = None


def materiales():
    global _MAT
    if _MAT is None:
        _MAT = [{**r, "rx": re.compile(r["patron"])} for r in csv.DictReader(open(TABLA, encoding="utf-8"))]
    return _MAT


def prep(texto):
    """Texto normalizado para los patrones: "SA-106", "SA 106", "A-105" y "A 105" quedan "a106", "a105"."""
    return re.sub(r"\bs?a[- ]?(\d{2,3})\b", r"a\1", norm(texto))


def clases(texto):
    """{clase: grupo} de todos los materiales que nombra el texto (doble certificación). Si una fila más general coincide
    dentro de lo que ya tomó una más específica ("A516 Gr 60" no es además A516-70), se descarta; los genéricos se
    descartan si hay uno específico."""
    t = prep(texto)
    hits = []
    for m in materiales():
        x = m["rx"].search(t)
        if x and not any(h[1] <= x.start() and x.end() <= h[2] for h in hits):
            hits.append((m, x.start(), x.end()))
    out = {}
    for m, _, _ in hits:
        out.setdefault(m["clase"], m["grupo_b16_5"])
    if len(out) > 1:
        for g in GENERICOS:
            out.pop(g, None)
    return out


def clase_material(texto):
    """Fila de la tabla del primer material que nombra el texto, o None (para mostrar)."""
    t = prep(texto)
    return next((m for m in materiales() if m["rx"].search(t)), None) if t.strip() else None


def grado(texto):
    m = re.search(r"\b(?:x|wphy|f)[- ]?(\d{2})\b", norm(texto))
    return m.group(1) if m else ""


def regla_material(fam, pedido, cand, desc_cand=""):
    if not str(pedido or "").strip():
        return ""
    if bool(re.search(GALV, norm(pedido))) != bool(re.search(GALV, norm(f"{cand} {desc_cand}"))):
        return "galvanizado y negro no se reemplazan"
    a = clases(pedido)
    b = clases(cand) if str(cand or "").strip() else {}
    if not b:
        b = clases(desc_cand)
    if not a:  # material del pedido que no está en la tabla: solo el mismo texto
        limpio = lambda x: re.sub(r"[^a-z0-9]", "", norm(x))
        return "" if limpio(pedido) and limpio(pedido) == limpio(cand) else f"material {pedido} sin regla: solo vale el mismo material"
    if not b:
        return f"el candidato no dice el material (el pedido es {pedido}): no se puede comparar"
    for ca, ga in a.items():
        tipo = ca.split("_")[0] if ca.startswith(("bulon", "tuerca")) else ""
        if tipo and not any(c.startswith(tipo) for c in b):
            continue  # bulonería: el candidato no dice la tuerca (o el bulón): no hay dato para comparar esa parte
        ok = False
        for cb, gb in b.items():
            if not (cb == ca or cb in REEMPLAZA.get(ca, set()) or cb in GENERICOS.get(ca, set())):
                continue
            if ga and gb and gb not in GRUPOS.get(ga, {ga}):
                continue
            if cb == ca == "carbono_alta_resistencia" and grado(pedido) and grado(cand or desc_cand) and grado(pedido) != grado(cand or desc_cand):
                continue
            ok = True
            break
        if not ok:
            nb = ", ".join(sorted(b)).replace("_", " ")
            return f"material {cand or desc_cand[:30]} ({nb}) no reemplaza a {pedido} ({ca.replace('_', ' ')})"
    return ""


def conexiones(*textos):
    """Tipos de conexión del texto: caras (rf, ff, rtj), roscas (npt, bspt, bspp), sw, bw, 'brida' sin cara, 'rosca' sin tipo."""
    out = set()
    for t in textos:
        t = norm(t)
        t = re.sub(r"\br\.?\s?f\.?(?=\s|/|$)|\brfwn\b", " rf ", t)
        t = re.sub(r"\br\.?\s?j\.?(?=\s|/|$)|\brj\b", " rtj ", t)
        t = re.sub(r"\b[fm]npt\b|\bnptf\b|\bnpt-?[hm]\b", " npt ", t)
        t = re.sub(r"\bsocket ?weld\b|\bsocket\b", " sw ", t)
        t = re.sub(r"\bbspp\b|\bbsp\b(?!t)", " bspp ", t)
        t = re.sub(r"\bbe\b|\bbisel", " bw ", t)
        for k in CARAS | ROSCAS | {"sw", "bw"}:
            if re.search(rf"\b{k}\b", t):
                out.add(k)
        if re.search(r"\bbridad|\bbrida\b", t) and not out & CARAS:
            out.add("brida")
        if re.search(r"\brosca|\broscad", t) and not out & ROSCAS:
            out.add("rosca")
    return out


def tipos(c):
    return {("brida" if x in CARAS | {"brida"} else "rosca" if x in ROSCAS | {"rosca"} else x) for x in c}


def regla_conexion(pedido, cand):
    if not pedido or not cand:
        return ""
    txt = f"extremos o cara distintos ({'/'.join(sorted(cand)).upper()} por {'/'.join(sorted(pedido)).upper()})"
    if not tipos(pedido) & tipos(cand):
        return txt
    ca, cb = pedido & CARAS, cand & CARAS
    if ca and cb and ca != cb:
        return txt
    ra, rb = pedido & ROSCAS, cand & ROSCAS
    if ra and rb and ra != rb:
        return txt
    return ""


def sch_canonico(sch, dn):
    s = re.sub(r"[^A-Z0-9]", "", str(sch or "").upper())
    s = re.sub(r"^(SCH|S)(?=\d)", "", s)
    s = {"40S": "STD", "80S": "XS"}.get(s, s)
    if dn is not None:
        if s == "STD" and dn <= 10:
            return "40"
        if s == "XS" and dn <= 8:
            return "80"
    return s


def dn_de(v):
    t = norm(v)
    m = re.search(r"\bdn ?(\d{2,3})\b|(\d{2,3}) ?mm\b", t)
    if m:
        return DN_NPS.get(int(m.group(1) or m.group(2)))
    m = re.match(r"\s*(\d+(?:[.,]\d+)?)", t)
    return float(m.group(1).replace(",", ".")) if m else None


def incompatible(fam, at_pedido, at_cand, texto_pedido="", texto_cand=""):
    """Motivo por el que el candidato NO puede ser similar del pedido ("" si puede)."""
    m = regla_material(fam, at_pedido.get("material", ""), at_cand.get("material", ""), texto_cand)
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
    tp, tc = norm(texto_pedido), norm(texto_cand)
    if re.search(NACE_ESTRICTO, tp) and not re.search(NACE_ESTRICTO, tc):
        return "el pedido es MR0175 / ISO 15156 y el candidato no lo dice"
    if re.search(NACE_PEDIDO, tp) and not re.search(NACE_CAND, tc):
        return "el pedido es para servicio ácido (NACE) y el candidato no lo dice"
    return ""


def para_pagina():
    """Lo que necesita web/src/busqueda.js para aplicar las mismas reglas (va en datos.json → compat)."""
    return {"materiales": [{k: r[k] for k in ("patron", "material", "clase", "grupo_b16_5")} for r in materiales()],
            "reemplaza": {k: sorted(v) for k, v in REEMPLAZA.items()}, "genericos": {k: sorted(v) for k, v in GENERICOS.items()},
            "grupos": {k: sorted(v) for k, v in GRUPOS.items()}, "nace_estricto": NACE_ESTRICTO, "nace_pedido": NACE_PEDIDO,
            "nace_cand": NACE_CAND, "galv": GALV, "prep": r"\bs?a[- ]?(\d{2,3})\b", "familias_sch": sorted(FAMILIAS_SCH), "dn_nps": DN_NPS}


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    print(clases(a), "|", clases(b))
    print(regla_material("VAL", a, b) or "compatible")
