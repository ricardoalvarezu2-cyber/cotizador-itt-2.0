"""Precio de acero al carbono por kilo (chapa, ángulo, planchuela, caño estructural) desde la planilla de J. Elejondo.

Uso: python herramientas/acero_por_kg.py  → conocimiento/precios/acero_por_kg.csv

Fuente: fuentes_originales/precios_varios_acero_2026-02.xlsx (última modificación 10-02-2026). Cada hoja tiene, por renglón,
el precio en pesos CON IVA de una hoja de chapa o una tira de 6 m, dividido por 1,21 y por el tipo de cambio que usa el
propio documento (1.447,5), los kg por m² o por m, y el USD/kg (más un 10% por recortes). Acá se recalcula todo desde la
fórmula de cada celda, para que el número no dependa del valor guardado en el Excel.
Lo usan el catálogo de materiales (un renglón por medida, unidad kg) y precotizar.py (piezas de chapa o perfil por kg).
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "fuentes_originales" / "precios_varios_acero_2026-02.xlsx"
SALIDA = RAIZ / "conocimiento" / "precios" / "acero_por_kg.csv"
FECHA = "2026-02-10"  # última modificación del archivo (propiedades del Excel); el documento no tiene otra fecha
RECORTES = 1.10
FORMA = {"chapa negra A36": ("chapa negra lisa", "ASTM A36", "m2"), "Chapa semilla de melón": ("chapa semilla de melón", "acero al carbono", "m2"),
         "H°A°": ("hierro ángulo", "acero al carbono", "m"), "Planch": ("planchuela", "acero al carbono", "m"),
         "Caño estr": ("caño estructural", "acero al carbono", "m")}


def pulg_mm(t):
    """'1/2"' → 12.7; '3/16"' → 4.76; '1-1/2X3/16' → espesor 3/16 (el último número es el espesor)."""
    partes = re.findall(r"(\d+)(?:-(\d+)/(\d+)|/(\d+))?", t.replace('"', ""))
    if not partes:
        return None
    a, b, c, d = partes[-1]
    v = int(a) / int(d) if d else int(a) + (int(b) / int(c) if b else 0)
    return round(v * 25.4, 2)


def main():
    wb = openpyxl.load_workbook(FUENTE, data_only=False)
    filas = []
    for ws in wb.worksheets:
        forma, material, por = FORMA[ws.title]
        for r in ws.iter_rows(min_row=2):
            a, b, c, f = r[0].value, r[1].value, r[2].value, r[5].value
            if not (isinstance(b, str) and b.startswith("=")):
                continue
            m = re.match(r"=\(([\d.]+)/1\.21\)/([\d.]+)", b.replace(" ", ""))
            if not m:
                sys.exit(f"Fórmula no reconocida en {ws.title}!{r[1].coordinate}: {b}")
            ars_con_iva, tc = float(m.group(1)), float(m.group(2))
            cant = eval(str(a).lstrip("="), {}, {}) if isinstance(a, str) else float(a)  # "=1.245*6" (fórmula simple del documento)
            usd = ars_con_iva / 1.21 / tc
            usd_kg = usd / cant / float(c)
            filas.append({"forma": forma, "material": material, "medida": str(f).strip(), "espesor_mm": pulg_mm(str(f)),
                          "unidad_compra": f"hoja de {cant:g} m²" if por == "m2" else f"tira de {cant:g} m",
                          "kg_por_m2_o_m": float(c), "por": por, "precio_compra_usd": round(usd, 2), "usd_kg": round(usd_kg, 2),
                          "usd_kg_con_recortes": round(usd_kg * RECORTES, 2), "ars_con_iva": ars_con_iva, "tc_documento": tc,
                          "fecha": FECHA, "fuente": f"fuentes_originales/precios_varios_acero_2026-02.xlsx, hoja {ws.title}, {r[1].coordinate}",
                          "nota": "precio de materia prima sin IVA (pesos con IVA ÷ 1,21 ÷ TC del documento); no incluye corte, plegado ni rolado"})
    with open(SALIDA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"{SALIDA.relative_to(RAIZ)}: {len(filas)} precios por kg · " + " · ".join(f"{x['forma']} {x['medida']} {x['usd_kg']:.2f}" for x in filas))


if __name__ == "__main__":
    main()
