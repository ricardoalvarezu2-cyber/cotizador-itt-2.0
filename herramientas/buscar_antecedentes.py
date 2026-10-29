"""Busca en el índice de proyectos las cotizaciones más parecidas a un pedido nuevo, priorizando las más actuales.

Uso:
  python herramientas/buscar_antecedentes.py --familia CO --texto "colector de campo produccion" --diametro 6 --serie 300 \\
         --material carbono --union bridado --cliente "PAMPA" [--top 8]
  python herramientas/buscar_antecedentes.py --familias      (lista las familias y cuántos proyectos hay de cada una)

Familias: C calentadores · SEP separadores · F filtros · SK skids · M manifolds · CO colectores · P puentes y tramos de
medición · CA cañería/piping · T tanques · TS trampas · V válvulas · EST estructuras · S servicios/MO · OT otros.

Puntaje (0–100), solo entre proyectos de la familia pedida:
  familia principal 15 (si la familia es solo secundaria, 5) · parecido del texto hasta 40 · diámetro 15 (cercano 7)
  · serie 12 · material 8 (distinto −5) · roscado/bridado 5 · mismo cliente 8 · planilla de costo 8 · proveedores 3
  · OC 3 · confianza baja −5. Después se multiplica por la antigüedad: 1,0 este año y −20% por cada año.
Ante dos parecidos, gana el más nuevo. Revisar los 3–5 primeros (abrir la carpeta de textos y la ficha).
"""
import argparse
import csv
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fmt, fmtg  # noqa: E402
from indice_proyectos import FAMILIAS, SALIDA as INDICE, norm, palabras  # noqa: E402

TAMANOS = [0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30, 36, 42, 48]


def vecino(a, b):
    try:
        return abs(TAMANOS.index(a) - TAMANOS.index(b)) == 1
    except ValueError:
        return abs(a - b) / max(a, b) <= 0.25


def puntuar(p, q, idf, hoy):
    razones, s = [], 0.0
    tags = p["etiquetas"].split()
    if q.familia:
        if p["familia"] == q.familia:
            s += 15
        elif q.familia in tags:
            s += 5
            razones.append(f"familia {q.familia} secundaria")
        else:
            return None
    # texto: palabras del pedido presentes en el proyecto, ponderadas por rareza
    qw = set(palabras(norm(q.texto))) if q.texto else set()
    if qw:
        pw = set(p["palabras"].split())
        comunes = qw & pw
        tot = sum(idf.get(w, 3) for w in qw)
        val = 40 * sum(idf.get(w, 3) for w in comunes) / tot if tot else 0
        s += val
        if comunes:
            razones.append("texto: " + ", ".join(sorted(comunes, key=lambda w: -idf.get(w, 3))[:5]))
    dias = [float(x) for x in p["diametros"].split()]
    if q.diametro:
        if q.diametro in dias:
            s += 15; razones.append(f'Ø{fmtg(q.diametro)}"')
        elif any(vecino(q.diametro, d) for d in dias):
            s += 7; razones.append(f'Ø cercano ({", ".join(f"{fmtg(d)}" for d in dias if vecino(q.diametro, d))}")')
    if q.serie and q.serie in p["series"].split():
        s += 12; razones.append(f"serie {q.serie}")
    if q.material:
        if q.material in p["material"].split():
            s += 8; razones.append(q.material)
        elif p["material"]:
            s -= 5
    if q.union and q.union in p["union"].split():
        s += 5; razones.append(q.union)
    if q.cliente and norm(q.cliente) in norm(p["cliente"] + " " + p["cliente_final"] + " " + p["id"]):
        s += 8; razones.append("mismo cliente")
    if p["tiene_planilla_costo"]:
        s += 8; razones.append("PLANILLA DE COSTO")
    if p["proveedores"] not in ("", "0"):
        s += 3
    if p["tiene_oc"]:
        s += 3; razones.append("ganada (OC)")
    if p["confianza"] == "baja":
        s -= 5
    anios = max(0.0, (hoy - date.fromisoformat(p["fecha"])).days / 365.25)
    factor_edad = max(0.4, 1 - 0.2 * anios)
    return s * factor_edad, razones, factor_edad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--familia", help="código de familia (CO, P, SK, F, ...)")
    ap.add_argument("--texto", default="", help="palabras del pedido: tipo de equipo, servicio, cliente, norma…")
    ap.add_argument("--diametro", type=float, help='diámetro principal en pulgadas (ej. 6 o 2.5)')
    ap.add_argument("--serie", help="serie o rating: 150, 300, 600, 900, 1500, 2000, 3000…")
    ap.add_argument("--material", choices=["carbono", "inoxidable"])
    ap.add_argument("--union", choices=["roscado", "bridado"])
    ap.add_argument("--cliente")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--excluir", action="append", default=[], help="texto del id a excluir (ej. la propia cotización); repetible")
    ap.add_argument("--hoy", default=date.today().isoformat())
    ap.add_argument("--familias", action="store_true", help="listar familias")
    q = ap.parse_args()
    filas = list(csv.DictReader(open(INDICE, encoding="utf-8")))
    if q.familias:
        c = Counter(t for r in filas for t in r["etiquetas"].split())
        for k, v in FAMILIAS.items():
            print(f"{k:4} {v:32} {c.get(k, 0):3} proyectos ({sum(1 for r in filas if r['familia'] == k)} como familia principal)")
        return
    q.familia = (q.familia or "").upper() or None
    if q.familia and q.familia not in FAMILIAS:
        sys.exit(f"Familia desconocida: {q.familia}. Opciones: {', '.join(FAMILIAS)}")
    df = Counter(w for r in filas for w in set(r["palabras"].split()))
    idf = {w: math.log(len(filas) / n) for w, n in df.items()}
    hoy = date.fromisoformat(q.hoy)
    res = []
    for p in filas:
        if any(x.lower() in (p["id"] + " " + p.get("origen", "") + " " + p.get("ruta", "")).lower() for x in q.excluir):
            continue
        r = puntuar(p, q, idf, hoy)
        if r:
            res.append((r[0], r[1], r[2], p))
    res.sort(key=lambda x: (round(x[0], 1), x[3]["fecha"]), reverse=True)  # empate: el más nuevo primero
    print(f"{len(res)} proyectos de la familia {q.familia or '(todas)'} en el índice (2025–2026). Los {min(q.top, len(res))} más parecidos:\n")
    for i, (s, razones, fe, p) in enumerate(res[:q.top], 1):
        pu = p["precio_unitario_principal"]
        datos = " · ".join(x for x in [
            f"{fmt(p['monto'] and float(p['monto']), 0)} {p['moneda']}" if p["monto"] else "",
            f"unit. {fmt(float(pu), 0)}" if pu else "", f"factor {fmt(float(p['factor']), 2)}" if p["factor"] else "",
            f"{fmt(float(p['plazo_dias']), 0)} días" if p["plazo_dias"] else "", p["resultado"]] if x)
        print(f"{i}. [{fmt(s, 0)}] {p['fecha']} · {p['id']}")
        print(f"   {p['descripcion'][:160]}")
        print(f"   {datos}")
        print(f"   Por qué: {'; '.join(razones) or '—'} · antigüedad ×{fmt(fe, 2)}")
        print(f"   Abrir: {p['carpeta_textos']}  |  ficha: {p['ficha']}\n")


if __name__ == "__main__":
    main()
