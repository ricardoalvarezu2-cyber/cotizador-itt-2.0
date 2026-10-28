"""Control automático de una cotización contra la tabla de materiales del plano.

Uso: python herramientas/verificar_computo.py cotizaciones/<carpeta>

Necesita en la carpeta:
  pedido/lista_materiales_plano.csv  (pos, descripcion, diametro, serie_sch, material, extremos, modelo_fabricante, cantidad, unidad)
  computo.csv                        (id, pos, descripcion, cant_por_puente, unidad, precio_unit_usd, subtotal_usd,
                                      tipo_origen, proveedor_o_criterio, carpeta_origen, fecha_precio)

ERRORES (impiden pasar a "revisado"):
  - posición del plano que falta en el cómputo, o con otra cantidad
  - posición del cómputo que no está en el plano (salvo filas de compra extra con sufijo, ej. 14b)
  - precio sin proveedor, origen o fecha
  - subtotal distinto de cantidad × precio
AVISOS (revisar uno por uno):
  - extremos BW/SW: soldaduras que tienen que estar contadas en la MO
  - modelo o fabricante exigido por el plano
  - precios estimados y su peso en el costo
  - precios con más de 6 meses
Ver conocimiento/procedimiento_cotizacion.md.
"""
import csv
import re
import sys
from datetime import date
from pathlib import Path


def num(v):
    v = str(v or "").strip().replace(" ", "")
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    return float(v.replace(",", ".")) if v else None


def main(carpeta):
    c = Path(carpeta)
    plano = list(csv.DictReader(open(c / "pedido" / "lista_materiales_plano.csv", encoding="utf-8")))
    comp = list(csv.DictReader(open(c / "computo.csv", encoding="utf-8")))
    errores, avisos = [], []

    por_pos = {}
    for r in comp:
        por_pos.setdefault(r["pos"].strip(), []).append(r)
    pos_plano = {p["pos"].strip() for p in plano}

    for p in plano:
        filas = por_pos.get(p["pos"].strip())
        if not filas:
            errores.append(f"Pos {p['pos']} ({p['descripcion'][:40]}) no está en el cómputo")
            continue
        cant = sum(num(f["cant_por_puente"]) or 0 for f in filas)
        largo = re.search(r"(\d+)\s*mm", p["descripcion"])
        if p.get("unidad", "un") == "un" and filas[0]["unidad"] == "m" and largo:
            esperado = int(largo.group(1)) / 1000 * num(p["cantidad"])
            if abs(cant - esperado) > 1e-6:
                errores.append(f"Pos {p['pos']}: el plano pide {p['cantidad']} × {largo.group(1)} mm = {esperado:g} m y el cómputo tiene {cant:g} m")
        elif p.get("unidad", "un") == "un" and filas[0]["unidad"] != "un":
            errores.append(f"Pos {p['pos']}: el plano pide {p['cantidad']} un y el cómputo usa '{filas[0]['unidad']}'. "
                           "Si se compra por metro, la cantidad tiene que dar el largo del plano y el sobrante va en fila aparte")
        elif abs(cant - num(p["cantidad"])) > 1e-6:
            errores.append(f"Pos {p['pos']}: plano {p['cantidad']} / cómputo {cant:g}")
        ext = p.get("extremos", "").upper()
        if "BW" in ext or "SW" in ext:
            avisos.append(f"Pos {p['pos']} extremos {ext} × {p['cantidad']}: confirmar que la soldadura está contada (taller o campo)")
        if p.get("modelo_fabricante", "").strip():
            avisos.append(f"Pos {p['pos']}: el plano exige {p['modelo_fabricante']}. Confirmar que el precio es de ese modelo o declarar desvío")

    for pos, filas in por_pos.items():
        if pos in pos_plano:
            continue
        base = re.match(r"^(\d+)[a-z]$", pos)
        if base and base.group(1) in pos_plano:
            avisos.append(f"Pos {pos}: fila de compra extra (sobrante) de la pos {base.group(1)}")
        elif not re.match(r"^[A-Z]{2,4}$", pos):  # MO, PH, PIN, CAL, INS
            errores.append(f"Pos {pos} del cómputo no está en el plano")

    total = estimado = 0.0
    hoy = date.today()
    for r in comp:
        cant, precio, sub = num(r["cant_por_puente"]), num(r["precio_unit_usd"]), num(r["subtotal_usd"])
        if cant is None or precio is None:
            errores.append(f"{r['id']}: falta cantidad o precio")
            continue
        if sub is not None and abs(sub - cant * precio) > 0.05:
            errores.append(f"{r['id']}: subtotal {sub} distinto de {cant:g} × {precio}")
        total += cant * precio
        if not r.get("proveedor_o_criterio", "").strip() or not r.get("fecha_precio", "").strip():
            errores.append(f"{r['id']}: precio sin fuente o sin fecha")
        if r.get("coincidencia") == "similar":
            avisos.append(f"{r['id']}: precio de una pieza SIMILAR, no igual: {r.get('diferencia', '')}")
        if r.get("tipo_origen", "").strip().lower() == "estimado":
            estimado += cant * precio
            avisos.append(f"{r['id']}: precio ESTIMADO ({r['descripcion'][:45]}) USD {cant * precio:,.2f}")
        m = re.match(r"(\d{4})-(\d{2})", r.get("fecha_precio", ""))
        if m:
            meses = (hoy.year - int(m.group(1))) * 12 + hoy.month - int(m.group(2))
            if meses > 6 and r.get("tipo_origen", "").lower() != "estimado":
                avisos.append(f"{r['id']}: precio de hace {meses} meses ({r['fecha_precio']}), actualizar")
            # decisión de Matías (28/10/2026): valores de antes del fin del cepo sin tipo de cambio explícito no son confiables
            if r.get("fecha_precio", "") < "2025-04-14" and not re.search(r"tc |tipo de cambio|tc explícito|tc explicito", (r.get("proveedor_o_criterio", "") + " " + r.get("nota", "")).lower()):
                avisos.append(f"{r['id']}: precio del período con cepo ({r['fecha_precio']}) sin tipo de cambio explícito: reemplazar por un valor confiable o justificar (por ejemplo, costo de planta oct-2024: TC 997 en la hoja Sueldos)")

    print(f"Plano: {len(plano)} posiciones · Cómputo: {len(comp)} filas · Costo directo por unidad USD {total:,.2f}")
    if total:
        print(f"Estimado sin fuente: USD {estimado:,.2f} ({estimado / total:.0%} del costo directo)"
              + ("  ← más del 15%, justificar" if estimado / total > 0.15 else ""))
    print(f"\nERRORES ({len(errores)})")
    for e in errores:
        print("  ✗", e)
    print(f"\nAVISOS ({len(avisos)})")
    for a in avisos:
        print("  !", a)
    return 1 if errores else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
