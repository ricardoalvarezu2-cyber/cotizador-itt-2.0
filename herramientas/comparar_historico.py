"""Caso de control: compara la precotización automática con el costo real de una planilla histórica, renglón por renglón.

Uso: python herramientas/comparar_historico.py cotizaciones/<carpeta> [--json cotizacion_auto.json]

Lee <carpeta>/historico.csv (pos, grupo, descripcion, cantidad, unidad, precio_unit_usd, total_usd, proveedor, nota: el costo
que se usó en su momento, por equipo) y el JSON de la cotización (por defecto cotizacion_auto.json, la salida de
precotizar.py). Genera <carpeta>/comparacion_historico.md.
Materiales: por posición del plano. MO y servicios: por rubro (soldadura, radiografía, pintura, prueba hidráulica,
horas de ingeniería/calidad/montaje), porque el cotizador y la planilla los agrupan distinto.
Todo sin IVA y sin ajuste por inflación (precio a la fecha de cada fuente), para comparar con la planilla de ese momento.
"""
import argparse
import re
import csv
import json
from pathlib import Path
from numeros import fmt, fmtg

RUBROS = [("soldadura", ("MO",), ("soldadura",)), ("radiografía y END", ("RX",), ("radiograf", "end", "tinta")),
          ("granallado y pintura", ("PIN",), ("pintura", "granallado")), ("prueba hidráulica", ("PH",), ("hidraulica", "hidráulica")),
          ("ingeniería, calidad y montaje", ("HH", "CAL", "ARM"), ("ingenier", "calidad", "montaje", "armado"))]


def rubro_de(pos, desc):
    """Primero el código de posición (HH, ARM, RX...), después las palabras enteras de la descripción: "montaje en planta
    (armado, movimientos, prueba hidráulica)" es montaje, no prueba hidráulica, y "end" no es parte de "recomendado"."""
    for nombre, poss, _ in RUBROS:
        if pos in poss:
            return nombre
    d = desc.lower()
    for nombre, _, palabras in RUBROS:
        if any(re.search(r"\b" + re.escape(p), d) for p in palabras):
            return nombre
    return "otros"


def pct(a, b):
    return (a / b - 1) * 100 if b else None


def fmt_pct(a, b):
    v = pct(a, b)
    return "—" if v is None else f"{fmt(v, 0, signo=True)}%"


def main(carpeta, archivo="cotizacion_auto.json"):
    carpeta = Path(carpeta)
    hist = list(csv.DictReader(open(carpeta / "historico.csv", encoding="utf-8")))
    cot = json.load(open(carpeta / archivo, encoding="utf-8"))
    items = {str(i["pos"]): i for i in cot["items"] if i["grupo"] == "material"}
    extras = {}  # compras extra de una posición (4b, 14c…): se suman a su posición, porque la planilla real las incluye ahí
    for p, i in items.items():
        if p[-1:] in "bcd" and p[:-1] in items:
            extras.setdefault(p[:-1], []).append(i)
    nombre = "precotización automática" if archivo == "cotizacion_auto.json" else f"cotización de `{archivo}`"
    lin = [f"# Caso de control {cot['codigo']}: {nombre} contra el costo real", "",
           f"Generado por `herramientas/comparar_historico.py` con `{archivo}`. Costos por {cot.get('equipo', {}).get('singular', 'equipo')}, "
           "sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.", "",
           "## Materiales (por posición del plano)", "",
           "| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |", "|---|---|---|---|---|---|---|"]
    tot_h = tot_c = 0.0
    cuenta = {"bien": 0, "lejos": 0, "sin precio": 0}
    for h in [x for x in hist if x["grupo"] == "material"]:
        th = float(h["total_usd"])
        it = items.get(h["pos"])
        if not it:
            lin.append(f"| {h['pos']} | {h['descripcion'][:45]} | {fmt(th, 2)} | — | — | — | falta en el cotizador |")
            tot_h += th
            continue
        s = it["fuentes"][0]
        tc = it["cantidad"] * s["precio"] + sum(e["cantidad"] * e["fuentes"][0]["precio"] for e in extras.get(h["pos"], []))
        tot_h += th
        tot_c += tc
        d = pct(tc, th)
        if not s["precio"] and it.get("provee"):
            lectura = "provisto por el cliente" if it["provee"] == "cliente" else "incluido en otra posición"
            cuenta["bien" if not th else "lejos"] += 1
        elif not s["precio"]:
            lectura = "SIN PRECIO en el catálogo"
            cuenta["sin precio"] += 1
        elif d is not None and abs(d) <= 15:
            lectura = "dentro de ±15%"
            cuenta["bien"] += 1
        else:
            lectura = ("más caro" if d and d > 0 else "más barato") + (f" ({s['coincide']})" if s["coincide"] != "igual" else "")
            cuenta["lejos"] += 1
        if h.get("nota"):
            lectura += f" · real: {h['nota']}"
        lin.append(f"| {h['pos']} | {h['descripcion'][:45]} | {fmtg(float(h['cantidad']))} × {fmt(float(h['precio_unit_usd']), 2)} = {fmt(th, 2)} | "
                   f"{fmtg(it['cantidad'])} {it['unidad']} × {fmt(s['precio'], 2)}{' + compra extra ' + ', '.join(e['pos'] for e in extras.get(h['pos'], [])) if extras.get(h['pos']) else ''} = {fmt(tc, 2)} | {'' if d is None else f'{fmt(d, 0, signo=True)}%'} | "
                   f"{s['tipo']} · {s['proveedor'][:40]} · {s['fecha']} | {lectura} |")
    lin += ["", f"**Materiales: real USD {fmt(tot_h, 2)} · cotizador USD {fmt(tot_c, 2)} ({fmt_pct(tot_c, tot_h)}).** "
            f"{cuenta['bien']} dentro de ±15%, {cuenta['lejos']} fuera, {cuenta['sin precio']} sin precio.", ""]
    # MO y servicios por rubro
    real, auto = {}, {}
    for h in [x for x in hist if x["grupo"] != "material"]:
        real[rubro_de(h["pos"], h["descripcion"])] = real.get(rubro_de(h["pos"], h["descripcion"]), 0) + float(h["total_usd"])
    for i in [x for x in cot["items"] if x["grupo"] != "material"]:
        r = rubro_de(str(i["pos"]), i["descripcion"])
        auto[r] = auto.get(r, 0) + i["cantidad"] * i["fuentes"][0]["precio"]
    lin += ["## Mano de obra y servicios (por rubro)", "", "| Rubro | Real | Cotizador | Dif. |", "|---|---|---|---|"]
    for r in [n for n, _, _ in RUBROS] + ["otros"]:
        if r in real or r in auto:
            a, b = auto.get(r, 0), real.get(r, 0)
            lin.append(f"| {r} | {fmt(b, 2)} | {fmt(a, 2)} | {'—' if not b else f'{fmt(pct(a, b), 0, signo=True)}%'} |")
    mo_h, mo_c = sum(real.values()), sum(auto.values())
    lin += ["", f"**MO y servicios: real USD {fmt(mo_h, 2)} · cotizador USD {fmt(mo_c, 2)} ({fmt(pct(mo_c, mo_h), 0, signo=True)}%).**", "",
            f"## Total por {cot.get('equipo', {}).get('singular', 'equipo')}", "",
            f"Real USD {fmt(tot_h + mo_h, 2)} · cotizador USD {fmt(tot_c + mo_c, 2)} ({fmt(pct(tot_c + mo_c, tot_h + mo_h), 0, signo=True)}%) antes de completar lo que el cotizador marca para revisar.", ""]
    salida = carpeta / ("comparacion_historico.md" if archivo == "cotizacion_auto.json" else f"comparacion_{Path(archivo).stem}.md")
    salida.write_text("\n".join(lin) + "\n", encoding="utf-8")
    print(f"Materiales {fmt_pct(tot_c, tot_h)} · MO y servicios {fmt(pct(mo_c, mo_h), 0, signo=True)}% · total {fmt(pct(tot_c + mo_c, tot_h + mo_h), 0, signo=True)}% → {salida}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--json", default="cotizacion_auto.json")
    q = ap.parse_args()
    main(q.carpeta, q.json)
