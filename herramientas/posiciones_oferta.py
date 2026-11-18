"""Precio por posición de la oferta, cuando el cliente pide varias posiciones con precio propio (p. ej. equipo + repuestos de
puesta en marcha + repuestos de 2 años, COT26-0010-001, 18-11-2026: la RI pide precios unitarios, no globales).

Uso: python herramientas/posiciones_oferta.py cotizaciones/<carpeta>   (lo corren armar_cotizacion.py y generar_oferta.py)

En oferta.json, "posiciones": [{"item", "codigo", "descripcion", "pos_cotizacion": ["RCP"], "cantidad": 1, "unidad": "lote",
"detalle": true}]. Los ítems de cotizacion.json cuya "pos" está en pos_cotizacion van a esa posición; el resto es el ítem
principal (oferta.json → item), con la cantidad de equipos. Cada renglón se vende con el mismo cálculo que la planilla
(precio × ajuste por inflación × factor; materiales con contingencia, válvulas Taval con FTV, MO y servicios con FMO). Las
cantidades de cotizacion.json son por equipo: una posición en lote lleva cantidad × N.
Control: la suma de las posiciones tiene que dar el total de la planilla (diferencia solo por redondeo de los unitarios).
Deja posiciones_oferta.md.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fmt, fmtg  # noqa: E402


def venta_unitaria(it, p, idx, fref):
    import armar_cotizacion as ac
    base = it["fuentes"][0]["precio"] * ac.factor(it, idx, fref, p["AJ"])
    if ac.es_taval(it):
        return base * (1 + p["CONT"] / 100) * p.get("FTV", 1.0)
    if it["grupo"] == "material":
        return base * (1 + p["CONT"] / 100) * p["FM"]
    return base * p["FMO"]


def calcular(carpeta):
    """None si oferta.json no tiene posiciones; si no, {"filas": [...], "total": x}."""
    import armar_cotizacion as ac
    carpeta = Path(carpeta)
    ro = carpeta / "oferta.json"
    if not ro.exists():
        return None
    of = json.load(open(ro, encoding="utf-8"))
    if not of.get("posiciones"):
        return None
    cot = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    p = cot["parametros"]
    n, fref, idx = p["N"], p["fecha_referencia"][:7], ac.leer_indices(cot)
    asignados = {}
    for po in of["posiciones"]:
        for x in po["pos_cotizacion"]:
            asignados[str(x).strip()] = po
    principal = [it for it in cot["items"] if str(it["pos"]).strip() not in asignados]
    pu = round(sum(it["cantidad"] * venta_unitaria(it, p, idx, fref) for it in principal), 2)
    it0 = of["item"]
    filas = [{"item": it0["item"], "codigo": it0["codigo"], "descripcion": it0["descripcion"], "cantidad": n, "unidad": "un",
              "unitario": pu, "subtotal": round(pu * n, 2), "plazo": it0.get("plazo_dias", ""), "detalle": []}]
    for po in of["posiciones"]:
        lineas = []
        for it in cot["items"]:
            if str(it["pos"]).strip() in [str(x).strip() for x in po["pos_cotizacion"]]:
                q = it["cantidad"] * n
                u = round(venta_unitaria(it, p, idx, fref), 2)
                lineas.append({"descripcion": it.get("especificacion") or it["descripcion"], "cantidad": q, "unidad": it["unidad"],
                               "unitario": u, "subtotal": round(u * q, 2)})
        tot = round(sum(x["subtotal"] for x in lineas), 2)
        q = po.get("cantidad", 1)
        filas.append({"item": po["item"], "codigo": po["codigo"], "descripcion": po["descripcion"], "cantidad": q,
                      "unidad": po.get("unidad", "lote"), "unitario": round(tot / q, 2), "subtotal": tot,
                      "plazo": po.get("plazo_dias", it0.get("plazo_dias", "")), "detalle": lineas if po.get("detalle") else []})
    return {"filas": filas, "total": round(sum(f["subtotal"] for f in filas), 2), "lineas": len(filas) + sum(len(f["detalle"]) for f in filas)}


def main(carpeta, total_planilla=None):
    r = calcular(carpeta)
    if r is None:
        return None
    out = ["# Precio por posición de la oferta", "", "Generado por `herramientas/posiciones_oferta.py` (mismo cálculo que la planilla, "
           "por renglón). Borrador, sin revisar.", "", "| Ítem | Código | Descripción | Cant. | Unidad | Unitario USD | Subtotal USD |",
           "|---|---|---|---|---|---|---|"]
    for f in r["filas"]:
        out.append(f"| {f['item']} | {f['codigo']} | {f['descripcion']} | {fmtg(f['cantidad'])} | {f['unidad']} | {fmt(f['unitario'], 2)} | {fmt(f['subtotal'], 2)} |")
        for x in f["detalle"]:
            out.append(f"|  |  | · {x['descripcion']} | {fmtg(x['cantidad'])} | {x['unidad']} | {fmt(x['unitario'], 2)} | {fmt(x['subtotal'], 2)} |")
    out.append(f"| | | **TOTAL** | | | | **{fmt(r['total'], 2)}** |")
    ok = True
    if total_planilla is not None:
        dif = r["total"] - total_planilla
        tol = 0.01 * r["lineas"]
        ok = abs(dif) <= tol + 1e-9
        out += ["", f"Total de la planilla: USD {fmt(total_planilla, 2)} · diferencia por redondeo de los unitarios: USD {fmt(dif, 2)} "
                f"(tolerancia {fmt(tol, 2)}): {'OK' if ok else 'NO COINCIDE'}"]
    Path(carpeta, "posiciones_oferta.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Posiciones de la oferta: total USD {fmt(r['total'], 2)}" + ("" if total_planilla is None else f" (planilla {fmt(total_planilla, 2)})"))
    if not ok:
        sys.exit("ERROR: la suma de las posiciones de la oferta no da el total de la planilla.")
    return r


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
