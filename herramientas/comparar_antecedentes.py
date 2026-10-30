"""Comparación de una cotización con sus antecedentes más parecidos (paso P8), con datos internos.

Uso: python herramientas/comparar_antecedentes.py cotizaciones/<carpeta>   (lo corre también armar_cotizacion.py)

Busca en el índice de proyectos (buscar_antecedentes.py: misma familia o subtipo, más parecido y más nuevo primero) los 5 mejores
con precio, y compara precio unitario, factor y reparto del costo (materiales / MO y servicios, de la ficha).
Marca diferencias de más del 15%: no dicen que esté mal, dicen que hay que explicarlas rubro por rubro antes de
presentar el número (procedimiento P8). Genera <carpeta>/comparacion_antecedentes.md.
"""
import csv
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar_antecedentes import INDICE, buscar, consulta_de_cotizacion  # noqa: E402
from indice_proyectos import SUBTIPO_NOMBRE  # noqa: E402
from numeros import a_vista, fmt, fmtg  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def costo_antecedente(p):
    """Costo por equipo y reparto del costo de un antecedente, solo con lo que dice su ficha y sin ambigüedad:
    {"cu": costo por unidad o None, "mat": fracción de materiales o None, "nota": por qué no hay costo por unidad}.
    El costo por unidad sale solo si la ficha tiene un único equipo con precio (o el monto es precio × cantidad): si la oferta
    tiene varios ítems, el costo total es de todo y no se reparte (no se inventa un costo por equipo)."""
    out = {"cu": None, "mat": None, "nota": ""}
    ficha = RAIZ / p["ficha"] if str(p.get("ficha", "")).endswith(".json") else None
    if not ficha or not ficha.exists():
        out["nota"] = "sin ficha"
        return out
    d = json.load(open(ficha, encoding="utf-8"))
    dc = d.get("desglose_costo") or {}
    m, mo, te, ot = (dc.get(k) or 0 for k in ("materiales", "mano_obra", "terceros", "otros"))
    if m + mo + te + ot and (mo + te):
        out["mat"] = m / (m + mo + te + ot)
    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    costo = num(d.get("costo_total"))
    if not costo:
        out["nota"] = "la ficha no tiene costo (solo precio de venta)"
        return out
    con_precio = [i for i in d.get("items") or [] if num(i.get("precio_unitario"))]
    pu, cant, monto = num(p.get("precio_unitario_principal")), num(p.get("cantidad_principal")) or 1, num(d.get("monto_total_ofertado"))
    if len(con_precio) == 1 or (pu and monto and abs(pu * cant - monto) <= 0.01 * monto):
        out["cu"] = costo / cant
    else:
        out["nota"] = "costo de toda la oferta (varios ítems): no se reparte por equipo"
    return out


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
    q = consulta_de_cotizacion(c, yo)  # familia y subtipo de la cotización (equipo.familia/subtipo o el título), no de los ítems
    fam = q.familia or "OT"
    res = [(s, p) for s, _, _, p in buscar(q, filas, hoy=date.today(), excluir=[carpeta.name], con_precio=True)[0]]
    lineas = [f"# Comparación con antecedentes (P8) — {c['codigo']}", "",
              f"Generado por `herramientas/comparar_antecedentes.py`. Familia {fam}"
              + (f", subtipo {SUBTIPO_NOMBRE.get(q.subtipo, q.subtipo)}" if q.subtipo else "") + f". Esta cotización: **precio unitario USD {fmt(precio_unitario, 2)}**, "
              f"costo USD {fmt(costo, 2)}, factor {fmtg(c['parametros']['FM'])} · reparto del costo: materiales {reparto.get('material', 0):.0%}, MO y servicios {reparto.get('mo', 0):.0%}.", "",
              "Se compara **costo contra costo** (Matías, 30-10-2026): el precio de venta mezcla factor, flete, caución y alcance de cada oferta. "
              "El costo del antecedente es el de su ficha, a su fecha (sin ajustar), y solo por equipo cuando la ficha lo permite sin ambigüedad; "
              "si no, queda el precio de venta marcado \"solo venta\". Una diferencia de más del 15% no significa error: hay que explicarla rubro por rubro "
              "(alcance, cantidad, diámetro, serie, fecha) antes de presentar el número.", "",
              "| # | Antecedente | Fecha | Costo por equipo | Costo: esta vs. antecedente | Materiales (ant. / esta) | MO y servicios (ant. / esta) | Factor | Precio de venta (solo referencia) | Qué es |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    avisos = []
    mat_n, mo_n = reparto.get("material", 0), reparto.get("mo", 0)
    for n, (s, p) in enumerate(res[:5], 1):
        pu = float(p["precio_unitario_principal"])
        dif_v = precio_unitario / pu - 1 if pu else 0
        ca = costo_antecedente(p)
        if ca["cu"]:
            dif = costo / ca["cu"] - 1
            otra = dif > 3 or dif < -0.75
            cel_c, cel_d = f"{fmt(ca['cu'], 0)} {p['moneda']}", f"{dif:+.0%}" + (" (otra escala: no comparable)" if otra else " ⚠" if abs(dif) > 0.15 else "")
            if not otra and abs(dif) > 0.15 and len(avisos) < 2:
                avisos.append(f"Costo {dif:+.0%} contra '{p['id'][:50]}' ({fmt(ca['cu'], 0)} {p['moneda']}, {a_vista(p['fecha'])}): explicar la diferencia rubro por rubro (P8)")
        else:
            cel_c, cel_d = "—", f"solo venta: {dif_v:+.0%}" + (" (otra escala)" if dif_v > 3 or dif_v < -0.75 else "") + (f" · {ca['nota']}" if ca["nota"] else "")
        rep_m = f"{ca['mat']:.0%} / {mat_n:.0%}" if ca["mat"] is not None else f"— / {mat_n:.0%}"
        rep_o = f"{1 - ca['mat']:.0%} / {mo_n:.0%}" if ca["mat"] is not None else f"— / {mo_n:.0%}"
        lineas.append(f"| {n} | {p['id'][:55]} | {a_vista(p['fecha'])} | {cel_c} | {cel_d} | {rep_m} | {rep_o} | "
                      f"{fmtg(p['factor']) if p['factor'] not in ('', None) else '—'} | {fmt(pu, 0)} {p['moneda']} | {p['descripcion'][:80]} |")
    if res and not any(costo_antecedente(p)["cu"] for _, p in res[:5]):
        avisos.append("Ninguno de los 5 tiene costo por equipo en su ficha: la comparación es solo de precio de venta")
    if res and not any(-0.75 <= precio_unitario / float(p["precio_unitario_principal"]) - 1 <= 3 for _, p in res[:5]):
        avisos.append("Ningún antecedente de los 5 primeros es de la misma escala: comparar a mano")
    if not res:
        avisos.append(f"No hay antecedentes de la familia {fam} con precio en el índice: comparar a mano")
    if q.subtipo and not any(p.get("subtipo") == q.subtipo for _, p in res[:5]):
        avisos.append(f"Ninguno de los 5 es del mismo subtipo ({SUBTIPO_NOMBRE.get(q.subtipo, q.subtipo)}): buscar más con buscar_antecedentes.py --cotizacion")
    lineas += ["", "## Avisos", ""] + ([f"- ⚠ {a}" for a in avisos] or ["- Ninguno."])
    (carpeta / "comparacion_antecedentes.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Antecedentes: {min(len(res), 5)} comparados → {carpeta / 'comparacion_antecedentes.md'}")
    for a in avisos:
        print("  ! " + a)
    return avisos


if __name__ == "__main__":
    main(sys.argv[1])
