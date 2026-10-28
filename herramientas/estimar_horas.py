"""Estima las horas de ingeniería, calidad y montaje de un equipo desde el antecedente más parecido (sin IA).

Uso: python herramientas/estimar_horas.py <tipo> <diámetro_pulg> [--unidades N] [--materiales USD] [--excluir texto]
     ej.: python herramientas/estimar_horas.py filtro 4 --unidades 2 --materiales 1400

Base: conocimiento/costos/horas_por_equipo.csv (34 equipos vigentes de 18 planillas 2025–2026; criterios en
horas_por_equipo_LEEME.md). Lo usa precotizar.py.

Regla (de las planillas de ITT, ver el LEEME):
- Parecido = mismo tipo, diámetro principal más cercano y costo de materiales más cercano (el tamaño real del equipo:
  el peso casi nunca está). Puntaje = |ln(d/d0)| + 0,5·|ln(mat/mat0)| + 0,5 si es otro tipo del mismo grupo (armados de
  cañería: puente, manifold, skid; recipientes: filtro, tanque, trampa) o + 3 si es de otro grupo. Menor es mejor.
- Si se conocen las pulgadas de soldadura del equipo (las calcula precotizar.py), el parecido y el tamaño se miden con
  ellas: es el trabajo de taller, y el costo de materiales se distorsiona con válvulas o instrumentos caros. Las horas del
  antecedente se multiplican por la raíz del cociente (entre 0,15 y 2,5): un equipo con el doble de trabajo no lleva el
  doble de horas (controles CTRL-T01, CTRL-M01 y CTRL-P01, 28-10-2026).
- Si hay antecedentes del mismo tipo, se usan solo esos (subtipo de skid o trampa como desempate); si no, los del mismo grupo
  con aviso; si tampoco, precotizar no suma horas (CTRL-P02, TS01, SK01, CA01).
- Ingeniería y calidad son un monto fijo por trabajo, casi independiente del tamaño (no se escalan): si el antecedente es de pocas
  unidades (≤ 4), sus horas se reparten entre las unidades de la cotización nueva (horas por unidad × unidades del
  antecedente ÷ N). En series largas (> 4) ya vienen prorrateadas y se toman por unidad.
- Montaje: horas por unidad del antecedente (días × hombres × 9 h por actividad). No incluye soldadura (va por
  pulgada) ni granallado y pintura (por m²); casi siempre incluye la prueba hidráulica.
- Tarifas: las del antecedente (15 USD/h ingeniería y calidad; 13 USD/h montaje, 16 en coalescedores y tanques).
Siempre es un ESTIMADO: se muestra el antecedente y el rango del mismo tipo para revisar.
"""
import argparse
import csv
import math
import statistics
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "conocimiento" / "costos" / "horas_por_equipo.csv"
SERIE_LARGA = 4
K = 3  # antecedentes que se promedian (mediana)
TIPOS = [("prefabricado", r"prefabricad|\bspools?\b(?! y skid)|piping de|\bpiping\b(?! y skid)"), ("puente", r"puente"), ("filtro", r"filtro|coalesc"), ("trampa", r"trampa|scraper"), ("manifold", r"manifold|colector"),
         ("tanque", r"tanque|separador|calentador|recipiente|tacho"), ("skid", r"skid|tramo|cuadro")]


def tipo_de(texto):
    t = (texto or "").lower()
    return next((n for n, rx in TIPOS if re.search(rx, t)), "skid")


# subtipos: "skid" junta desarenadores, skids de bomba, de medición y concentradores (CTRL-SK01: horas de un skid de bomba 4"
# para un concentrador 16"); las trampas, lanzadora y receptora
SUBTIPOS = [("concentrador", r"concentrador|colector|manifold"), ("bomba", r"bomba|booster"), ("medicion", r"medici|uflo|tramo"),
            ("desarenador", r"desarenad|sand"), ("receptora", r"receptora"), ("lanzadora", r"lanzadora"), ("coalescedor", r"coalesc")]


def subtipo_de(texto):
    t = (texto or "").lower()
    return next((n for n, rx in SUBTIPOS if re.search(rx, t)), "")


def leer(excluir=()):
    filas = []
    for r in csv.DictReader(open(BASE, encoding="utf-8")):
        if r["vigente"] != "si" or not r["fecha"] or any(x.lower() in (r["proyecto"] + r["archivo"]).lower() for x in excluir):
            continue
        filas.append(r)
    return filas


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# Tipos afines: armados de cañería (se parecen en armado y prueba) y recipientes. Entre grupos el antecedente casi no sirve.
GRUPO = {"prefabricado": "prefabricado", "puente": "piping", "manifold": "piping", "skid": "piping", "filtro": "recipiente", "tanque": "recipiente", "trampa": "recipiente"}
ESCALA = (0.15, 2.5)


def puntaje(r, tipo, d0, mat0, pulg0=None, sub0=""):
    sub = subtipo_de(r["equipo"])
    extra = 0.4 if sub0 and sub and sub != sub0 else 0
    d, m, pu = f(r["diametro_pulg"]), f(r["costo_materiales_usd"]), f(r["pulgadas_soldadura"])
    if pulg0 and pu:  # el trabajo de taller (pulgadas de soldadura) mide mejor el tamaño que el costo de materiales
        p = abs(math.log(pu / pulg0)) + 0.3 * (abs(math.log(d / d0)) if d and d0 else 0.5)
    else:
        p = (abs(math.log(d / d0)) if d and d0 else 1.5) + 0.5 * (abs(math.log(m / mat0)) if m and mat0 else 0.5) + (0.5 if pulg0 else 0)
    return p + extra + (0 if r["tipo"] == tipo else 0.5 if GRUPO.get(r["tipo"]) == GRUPO.get(tipo) else 3)


def escala(r, mat0, pulg0=None):
    """Corrección por tamaño: raíz del cociente de pulgadas de soldadura (o de materiales si no hay pulgadas). Un equipo
    con el doble de trabajo no lleva el doble de horas."""
    pu, m = f(r["pulgadas_soldadura"]), f(r["costo_materiales_usd"])
    k = pulg0 / pu if pulg0 and pu else mat0 / m if m and mat0 else None
    return 1.0 if not k else round(min(max(math.sqrt(k), ESCALA[0]), ESCALA[1]), 3)


def estimar(tipo, diametro, unidades=1, materiales=None, excluir=(), pulgadas=None, texto=""):
    """Devuelve {ing, cal, mont: {horas_u, usd_h, antecedente, ...}, rango, incluye_ph, nivel} o None si no hay base.
    nivel: "mismo_tipo" (solo antecedentes del mismo tipo), "mismo_grupo" (no hay del mismo tipo: se usan los afines, con
    aviso) u "otro" (ni del grupo: precotizar no suma horas y avisa). Antes la mediana mezclaba tipos aunque hubiera del
    mismo (CTRL-P02: un puente con dos skids de medición; CTRL-TS01: una trampa con dos tanques)."""
    filas = leer(excluir)
    if not filas:
        return None
    sub0 = subtipo_de(texto)
    # del mismo tamaño: diámetro hasta 2,5 veces (CTRL-F01: un filtro coalescedor 36" de 250 h no sirve para un FM2 de 4")
    cerca = lambda r: not (f(r["diametro_pulg"]) and diametro) or max(f(r["diametro_pulg"]), diametro) / min(f(r["diametro_pulg"]), diametro) <= 2.5
    mismos = [r for r in filas if r["tipo"] == tipo and cerca(r)]
    # sin antecedente del mismo tipo, solo se usan afines en armados de cañería (puente, manifold, skid); entre recipientes
    # (filtro, tanque, trampa) el trabajo es otro (CTRL-F01: un filtro FM2 4" tomaba las horas de una trampa 8x6)
    grupo = [r for r in filas if GRUPO.get(r["tipo"]) == GRUPO.get(tipo) == "piping" and cerca(r)]
    nivel = "mismo_tipo" if mismos else "mismo_grupo" if grupo else "otro"
    pool = mismos or grupo or filas
    ord_ = sorted(pool, key=lambda r: (puntaje(r, tipo, diametro, materiales, pulgadas, sub0), r["fecha"][::-1]))

    def primeros(filas_):  # uno por proyecto (las filas del mismo proyecto repiten las horas)
        vistos, out = set(), []
        for r in filas_:
            if r["proyecto"] not in vistos:
                vistos.add(r["proyecto"]); out.append(r)
        return out[:K]
    cand_a = primeros(r for r in ord_ if f(r["horas_ingenieria_u"]) is not None)
    cand_m = primeros(r for r in ord_ if r["usar_montaje"] == "si")
    a, m = (cand_a[0] if cand_a else None), (cand_m[0] if cand_m else None)
    if not a:
        return None

    def por_unidad(r, col):
        # ingeniería y calidad: monto fijo por trabajo, no se escalan por tamaño (CTRL-TS01: 251,5 h → 521 h); sí se reparten en la serie
        u = f(r["unidades"]) or 1
        h = f(r[col]) or 0
        return h * u / unidades if u <= SERIE_LARGA else h

    def fijo(col):
        return round(statistics.median(por_unidad(r, col) for r in cand_a), 2)
    mont_h = round(statistics.median(f(r["horas_montaje_u"]) * escala(r, materiales, pulgadas) for r in cand_m), 1) if cand_m else None

    def rango(col):
        v = [f(r[col]) for r in mismos if f(r[col])]
        return (min(v), max(v)) if v else None
    desc = lambda r: f"{r['proyecto']} · {r['equipo'][:60]} ({r['diametro_texto'] or 's/d'}, {r['unidades']} u, {r['fecha']})"
    return {
        "ing": {"horas_u": fijo("horas_ingenieria_u"), "usd_h": f(a["usd_h_ing"]) or 15, "antecedente": desc(a), "fila": a,
                "criterio": "mediana de " + ", ".join(f"{por_unidad(r, 'horas_ingenieria_u'):.1f}" for r in cand_a) + " h por unidad (repartidas en la serie)"},
        "cal": {"horas_u": fijo("horas_calidad_u"), "usd_h": f(a["usd_h_cal"]) or 15, "antecedente": desc(a), "fila": a,
                "criterio": "mediana de " + ", ".join(f"{por_unidad(r, 'horas_calidad_u'):.1f}" for r in cand_a) + " h por unidad (repartidas en la serie)"},
        "mont": None if not m else {"horas_u": mont_h, "usd_h": f(m["usd_h_mont"]) or 13, "antecedente": desc(m), "fila": m,
                                    "criterio": "mediana de " + ", ".join(f"{f(r['horas_montaje_u']):g} h × {escala(r, materiales, pulgadas):g}" for r in cand_m) + " (horas por unidad × tamaño)",
                                    "detalle": m["detalle_montaje"]},
        "incluye_ph": bool(m and re.search(r"\bPH\b|hidr", m["detalle_montaje"] + m["cita"], re.I)),
        "nivel": nivel,
        "mismo_tipo": nivel == "mismo_tipo",
        "mismo_grupo": nivel != "otro",
        "rango": {k: rango(c) for k, c in (("ing", "horas_ingenieria_u"), ("cal", "horas_calidad_u"), ("mont", "horas_montaje_u"))},
        "candidatos": [desc(r) for r in cand_m or cand_a],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tipo")
    ap.add_argument("diametro", type=float)
    ap.add_argument("--unidades", type=float, default=1)
    ap.add_argument("--materiales", type=float, help="costo de materiales por unidad, USD")
    ap.add_argument("--pulgadas", type=float, help="pulgadas equivalentes de soldadura por unidad")
    ap.add_argument("--excluir", action="append", default=[])
    q = ap.parse_args()
    e = estimar(tipo_de(q.tipo), q.diametro, q.unidades, q.materiales, q.excluir, q.pulgadas, q.tipo)
    if not e:
        raise SystemExit("No hay antecedentes")
    for k, n in (("ing", "Ingeniería"), ("cal", "Calidad"), ("mont", "Montaje")):
        x = e[k]
        if x:
            print(f"{n}: {x['horas_u']:g} h/u × USD {x['usd_h']:g} = USD {x['horas_u'] * x['usd_h']:,.2f} · {x['criterio']} · {x['antecedente']}")
        r = e["rango"][k]
        if r:
            print(f"   rango del mismo tipo: {r[0]:g}–{r[1]:g} h/u")
    print(("La prueba hidráulica va dentro del montaje del antecedente. " if e["incluye_ph"] else "") +
          {"mismo_tipo": "", "mismo_grupo": "⚠ No hay antecedente del mismo tipo: se usaron equipos afines.",
           "otro": "⚠ No hay antecedente del mismo tipo ni de uno afín: no usar estas horas."}[e["nivel"]])
    print("Candidatos: " + " | ".join(e["candidatos"]))


if __name__ == "__main__":
    main()
