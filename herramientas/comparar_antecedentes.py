"""Comparación de una cotización con sus antecedentes más parecidos (paso P8), con datos internos.

Uso: python herramientas/comparar_antecedentes.py cotizaciones/<carpeta>   (lo corre también armar_cotizacion.py)

Busca en el índice de proyectos (buscar_antecedentes.py: misma familia, más parecido y más nuevo primero) los 5 mejores
con precio, y compara precio unitario, factor y reparto del costo (materiales / MO y servicios, de la ficha).
Marca diferencias de más del 15%: no dicen que esté mal, dicen que hay que explicarlas rubro por rubro antes de
presentar el número (procedimiento P8). Genera <carpeta>/comparacion_antecedentes.md.
"""
import csv
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar_antecedentes import INDICE, puntuar  # noqa: E402
from indice_proyectos import etiquetas, norm  # noqa: E402
from numeros import a_vista  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def main(carpeta, precio_unitario=None, costo=None, reparto=None):
    carpeta = Path(carpeta)
    c = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    if precio_unitario is None:
        import armar_cotizacion as ac
        r = ac.calcular(c, ac.leer_indices(c))
        precio_unitario, costo = r["precio_unitario"], r["costo"]
    if reparto is None:
        sub = Counter()
        for it in c["items"]:
            sub["material" if it["grupo"] == "material" else "mo"] += it["cantidad"] * it["fuentes"][0]["precio"]
        tot = sum(sub.values()) or 1
        reparto = {k: v / tot for k, v in sub.items()}
    filas = list(csv.DictReader(open(INDICE, encoding="utf-8")))
    yo = next((r for r in filas if r["id"] == carpeta.name), None)
    texto = norm(c.get("titulo", "") + " " + " ".join(i["descripcion"] for i in c["items"]))
    fam = (etiquetas("", texto) or ["OT"])[0]
    dias = [float(x) for x in (yo["diametros"].split() if yo else [])]
    q = SimpleNamespace(familia=fam, texto=c.get("titulo", ""), diametro=max(dias) if dias else None,
                        serie=(yo["series"].split() or [None])[-1] if yo else None, material=None, union=None, cliente=c["cliente"].get("nombre"))
    df = Counter(w for r in filas for w in set(r["palabras"].split()))
    idf = {w: math.log(len(filas) / n) for w, n in df.items()}
    res = []
    for p in filas:
        if p["id"] == carpeta.name or not p["precio_unitario_principal"]:
            continue
        r = puntuar(p, q, idf, date.today())
        if r:
            res.append((r[0], p))
    res.sort(key=lambda x: (round(x[0], 1), x[1]["fecha"]), reverse=True)
    lineas = [f"# Comparación con antecedentes (P8) — {c['codigo']}", "",
              f"Generado por `herramientas/comparar_antecedentes.py`. Familia {fam}. Esta cotización: **precio unitario USD {precio_unitario:,.2f}**, "
              f"costo USD {costo:,.2f}, factor {c['parametros']['FM']} · reparto del costo: materiales {reparto.get('material', 0):.0%}, MO y servicios {reparto.get('mo', 0):.0%}.", "",
              "Una diferencia de más del 15% no significa error: hay que explicarla rubro por rubro (alcance, cantidad, diámetro, serie, fecha) antes de presentar el número.", "",
              "| # | Antecedente | Fecha | Precio unitario | Diferencia | Factor | Reparto de la ficha | Qué es |", "|---|---|---|---|---|---|---|---|"]
    avisos = []
    for n, (s, p) in enumerate(res[:5], 1):
        pu = float(p["precio_unitario_principal"])
        dif = precio_unitario / pu - 1 if pu else 0
        rep = ""
        ficha = RAIZ / p["ficha"] if p["ficha"].endswith(".json") else None
        if ficha and ficha.exists():
            d = json.load(open(ficha, encoding="utf-8")).get("desglose_costo") or {}
            m, mo, te = (d.get("materiales") or 0), (d.get("mano_obra") or 0), (d.get("terceros") or 0)
            if m + mo + te:
                rep = f"mat {m / (m + mo + te):.0%} · MO+serv {(mo + te) / (m + mo + te):.0%}"
        otra_escala = dif > 3 or dif < -0.75  # más de 4 veces de diferencia: el "precio principal" del índice es otra cosa
        marca = " (otra escala: no comparable)" if otra_escala else (" ⚠" if abs(dif) > 0.15 else "")
        lineas.append(f"| {n} | {p['id'][:55]} | {a_vista(p['fecha'])} | {pu:,.0f} {p['moneda']} | {dif:+.0%}{marca} | {p['factor'] or '—'} | {rep or '—'} | {p['descripcion'][:90]} |")
        if not otra_escala and abs(dif) > 0.15 and len(avisos) < 2:
            avisos.append(f"Precio {dif:+.0%} contra '{p['id'][:50]}' ({pu:,.0f} {p['moneda']}, {a_vista(p['fecha'])}): explicar la diferencia rubro por rubro (P8)")
    if res and not any(-0.75 <= precio_unitario / float(p["precio_unitario_principal"]) - 1 <= 3 for _, p in res[:5]):
        avisos.append("Ningún antecedente de los 5 primeros es de la misma escala: comparar a mano")
    if not res:
        avisos.append(f"No hay antecedentes de la familia {fam} con precio en el índice: comparar a mano")
    lineas += ["", "## Avisos", ""] + ([f"- ⚠ {a}" for a in avisos] or ["- Ninguno."])
    (carpeta / "comparacion_antecedentes.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Antecedentes: {min(len(res), 5)} comparados → {carpeta / 'comparacion_antecedentes.md'}")
    for a in avisos:
        print("  ! " + a)
    return avisos


if __name__ == "__main__":
    main(sys.argv[1])
