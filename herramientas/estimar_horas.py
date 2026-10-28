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
- Ingeniería y calidad son un monto fijo por trabajo, casi independiente del tamaño: si el antecedente es de pocas
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
TIPOS = [("puente", r"puente"), ("filtro", r"filtro|coalesc"), ("trampa", r"trampa|scraper"), ("manifold", r"manifold|colector"),
         ("tanque", r"tanque|separador|calentador|recipiente|tacho"), ("skid", r"skid|tramo|cuadro")]


def tipo_de(texto):
    t = (texto or "").lower()
    return next((n for n, rx in TIPOS if re.search(rx, t)), "skid")


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
GRUPO = {"puente": "piping", "manifold": "piping", "skid": "piping", "filtro": "recipiente", "tanque": "recipiente", "trampa": "recipiente"}
ESCALA = (0.15, 2.5)


def puntaje(r, tipo, d0, mat0, pulg0=None):
    d, m, pu = f(r["diametro_pulg"]), f(r["costo_materiales_usd"]), f(r["pulgadas_soldadura"])
    if pulg0 and pu:  # el trabajo de taller (pulgadas de soldadura) mide mejor el tamaño que el costo de materiales
        p = abs(math.log(pu / pulg0)) + 0.3 * (abs(math.log(d / d0)) if d and d0 else 0.5)
    else:
        p = (abs(math.log(d / d0)) if d and d0 else 1.5) + 0.5 * (abs(math.log(m / mat0)) if m and mat0 else 0.5) + (0.5 if pulg0 else 0)
    return p + (0 if r["tipo"] == tipo else 0.5 if GRUPO.get(r["tipo"]) == GRUPO.get(tipo) else 3)


def escala(r, mat0, pulg0=None):
    """Corrección por tamaño: raíz del cociente de pulgadas de soldadura (o de materiales si no hay pulgadas). Un equipo
    con el doble de trabajo no lleva el doble de horas."""
    pu, m = f(r["pulgadas_soldadura"]), f(r["costo_materiales_usd"])
    k = pulg0 / pu if pulg0 and pu else mat0 / m if m and mat0 else None
    return 1.0 if not k else round(min(max(math.sqrt(k), ESCALA[0]), ESCALA[1]), 3)


def estimar(tipo, diametro, unidades=1, materiales=None, excluir=(), pulgadas=None):
    """Devuelve {ing, cal, mont: {horas_u, usd_h, antecedente, ...}, rango, incluye_ph} o None si no hay base."""
    filas = leer(excluir)
    if not filas:
        return None
    ord_ = sorted(filas, key=lambda r: (puntaje(r, tipo, diametro, materiales, pulgadas), r["fecha"][::-1]))
    # mediana de los K más parecidos (un solo antecedente era frágil: trampas, skids con bombas o tanques con pintura incluida)
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
    ua = f(a["unidades"]) or 1
    rep = (ua <= SERIE_LARGA)
    ka = escala(a, materiales, pulgadas)
    km = escala(m, materiales, pulgadas) if m else 1.0

    def por_unidad(r, col):
        u = f(r["unidades"]) or 1
        h = (f(r[col]) or 0) * escala(r, materiales, pulgadas)
        return h * u / unidades if u <= SERIE_LARGA else h

    def fijo(col):
        return round(statistics.median(por_unidad(r, col) for r in cand_a), 2)
    mont_h = round(statistics.median(f(r["horas_montaje_u"]) * escala(r, materiales, pulgadas) for r in cand_m), 1) if cand_m else None
    mismos = [r for r in filas if r["tipo"] == tipo]

    def rango(col):
        v = [f(r[col]) for r in mismos if f(r[col])]
        return (min(v), max(v)) if v else None
    desc = lambda r: f"{r['proyecto']} · {r['equipo'][:60]} ({r['diametro_texto'] or 's/d'}, {r['unidades']} u, {r['fecha']})"
    return {
        "ing": {"horas_u": fijo("horas_ingenieria_u"), "usd_h": f(a["usd_h_ing"]) or 15, "antecedente": desc(a), "fila": a,
                "criterio": "mediana de " + ", ".join(f"{por_unidad(r, 'horas_ingenieria_u'):.1f}" for r in cand_a) + " h por unidad (repartidas en la serie y por tamaño)"},
        "cal": {"horas_u": fijo("horas_calidad_u"), "usd_h": f(a["usd_h_cal"]) or 15, "antecedente": desc(a), "fila": a,
                "criterio": "mediana de " + ", ".join(f"{por_unidad(r, 'horas_calidad_u'):.1f}" for r in cand_a) + " h por unidad (repartidas en la serie y por tamaño)"},
        "mont": None if not m else {"horas_u": mont_h, "usd_h": f(m["usd_h_mont"]) or 13, "antecedente": desc(m), "fila": m,
                                    "criterio": "mediana de " + ", ".join(f"{f(r['horas_montaje_u']):g} h × {escala(r, materiales, pulgadas):g}" for r in cand_m) + " (horas por unidad × tamaño)",
                                    "detalle": m["detalle_montaje"]},
        "incluye_ph": bool(m and re.search(r"\bPH\b|hidr", m["detalle_montaje"] + m["cita"], re.I)),
        "mismo_tipo": a["tipo"] == tipo and (not m or m["tipo"] == tipo),
        "mismo_grupo": GRUPO.get(a["tipo"]) == GRUPO.get(tipo) and (not m or GRUPO.get(m["tipo"]) == GRUPO.get(tipo)),
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
    e = estimar(tipo_de(q.tipo), q.diametro, q.unidades, q.materiales, q.excluir, q.pulgadas)
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
          ("" if e["mismo_tipo"] else "⚠ No hay antecedente del mismo tipo y tamaño: se usó otro tipo."))
    print("Candidatos: " + " | ".join(e["candidatos"]))


if __name__ == "__main__":
    main()
