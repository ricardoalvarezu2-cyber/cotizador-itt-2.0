"""Estima las horas de ingeniería, calidad y montaje de un equipo desde el antecedente más parecido (sin IA).

Uso: python herramientas/estimar_horas.py <tipo> <diámetro_pulg> [--unidades N] [--materiales USD] [--excluir texto]
     ej.: python herramientas/estimar_horas.py filtro 4 --unidades 2 --materiales 1400

Base: conocimiento/costos/horas_por_equipo.csv (34 equipos vigentes de 18 planillas 2025–2026; criterios en
horas_por_equipo_LEEME.md). Lo usa precotizar.py.

Regla (de las planillas de ITT, ver el LEEME):
- Parecido = mismo tipo, diámetro principal más cercano y costo de materiales más cercano (el tamaño real del equipo:
  el peso casi nunca está). Puntaje = |ln(d/d0)| + 0,5·|ln(mat/mat0)| + 1 si el tipo es otro. Menor es mejor.
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
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "conocimiento" / "costos" / "horas_por_equipo.csv"
SERIE_LARGA = 4
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


def puntaje(r, tipo, d0, mat0):
    d, m = f(r["diametro_pulg"]), f(r["costo_materiales_usd"])
    p = abs(math.log(d / d0)) if d and d0 else 1.5
    p += 0.5 * abs(math.log(m / mat0)) if m and mat0 else 0.5
    return p + (0 if r["tipo"] == tipo else 1)


def estimar(tipo, diametro, unidades=1, materiales=None, excluir=()):
    """Devuelve {ing, cal, mont: {horas_u, usd_h, antecedente, ...}, rango, incluye_ph} o None si no hay base."""
    filas = leer(excluir)
    if not filas:
        return None
    ord_ = sorted(filas, key=lambda r: (puntaje(r, tipo, diametro, materiales), r["fecha"][::-1]))
    a = next(r for r in ord_ if f(r["horas_ingenieria_u"]) is not None)
    m = next((r for r in ord_ if r["usar_montaje"] == "si"), None)
    ua = f(a["unidades"]) or 1
    rep = (ua <= SERIE_LARGA)

    def fijo(col):
        h = f(a[col]) or 0
        return round(h * ua / unidades, 2) if rep else h
    mismos = [r for r in filas if r["tipo"] == tipo]

    def rango(col):
        v = [f(r[col]) for r in mismos if f(r[col])]
        return (min(v), max(v)) if v else None
    desc = lambda r: f"{r['proyecto']} · {r['equipo'][:60]} ({r['diametro_texto'] or 's/d'}, {r['unidades']} u, {r['fecha']})"
    return {
        "ing": {"horas_u": fijo("horas_ingenieria_u"), "usd_h": f(a["usd_h_ing"]) or 15, "antecedente": desc(a), "fila": a,
                "criterio": (f"{f(a['horas_ingenieria_u']):g} h × {ua:g} u ÷ {unidades:g} u" if rep else f"{f(a['horas_ingenieria_u']):g} h por unidad (serie de {ua:g})")},
        "cal": {"horas_u": fijo("horas_calidad_u"), "usd_h": f(a["usd_h_cal"]) or 15, "antecedente": desc(a), "fila": a,
                "criterio": (f"{f(a['horas_calidad_u']):g} h × {ua:g} u ÷ {unidades:g} u" if rep else f"{f(a['horas_calidad_u']):g} h por unidad (serie de {ua:g})")},
        "mont": None if not m else {"horas_u": f(m["horas_montaje_u"]), "usd_h": f(m["usd_h_mont"]) or 13, "antecedente": desc(m), "fila": m,
                                    "criterio": "horas por unidad del antecedente", "detalle": m["detalle_montaje"]},
        "incluye_ph": bool(m and re.search(r"\bPH\b|hidr", m["detalle_montaje"] + m["cita"], re.I)),
        "mismo_tipo": a["tipo"] == tipo,
        "rango": {k: rango(c) for k, c in (("ing", "horas_ingenieria_u"), ("cal", "horas_calidad_u"), ("mont", "horas_montaje_u"))},
        "candidatos": [desc(r) for r in ord_[:3]],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tipo")
    ap.add_argument("diametro", type=float)
    ap.add_argument("--unidades", type=float, default=1)
    ap.add_argument("--materiales", type=float, help="costo de materiales por unidad, USD")
    ap.add_argument("--excluir", action="append", default=[])
    q = ap.parse_args()
    e = estimar(tipo_de(q.tipo), q.diametro, q.unidades, q.materiales, q.excluir)
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
