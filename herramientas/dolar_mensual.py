"""Tabla mensual del dólar desde ene-2024: conocimiento/costos/dolar_mensual.csv y .xlsx

Uso: python herramientas/dolar_mensual.py            (baja los datos diarios y rearma la tabla)
     python herramientas/dolar_mensual.py --sin-red  (rearma desde la copia diaria guardada en el repo)

Cuatro cotizaciones (precio de VENTA, en pesos por dólar), día por día:
- oficial:   dólar billete Banco Nación (BNA), vendedor.
- mayorista: dólar mayorista (referencia BCRA A3500; el "BNA divisa" que citan algunos proveedores es parecido).
- mep:       dólar bolsa / MEP.
- blue:      dólar informal.
Por mes: pico (máximo y su fecha), mínimo, promedio y cierre de cada una, y la brecha del blue contra el oficial.
Hasta el 14/04/2025 hubo cepo cambiario y la brecha fue grande: en esos meses el oficial no refleja el valor real.

Fuente: api.argentinadatos.com (recopila las cotizaciones publicadas por BNA, BCRA y los mercados). La copia diaria
queda en fuentes_originales/indices/dolar_diario.csv para no depender de internet.
"""
import csv
import json
import sys
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import FMT_PRECIO, celda_excel  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DIARIO = RAIZ / "fuentes_originales" / "indices" / "dolar_diario.csv"
SALIDA = RAIZ / "conocimiento" / "costos" / "dolar_mensual.csv"
API = "https://api.argentinadatos.com/v1/cotizaciones/dolares/{}"
SERIES = {"oficial": "oficial", "mayorista": "mayorista", "mep": "bolsa", "blue": "blue"}
DESDE = "2024-01-01"
FIN_CEPO = "2025-04-14"


def bajar():
    datos = defaultdict(dict)
    for nombre, casa in SERIES.items():
        pedido = urllib.request.Request(API.format(casa), headers={"User-Agent": "Mozilla/5.0 (cotizador ITT)"})
        with urllib.request.urlopen(pedido, timeout=60) as r:
            for x in json.load(r):
                if x["fecha"] >= DESDE and x.get("venta"):
                    datos[x["fecha"]][nombre] = float(x["venta"])
    DIARIO.parent.mkdir(parents=True, exist_ok=True)
    with open(DIARIO, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fecha"] + list(SERIES))
        for d in sorted(datos):
            w.writerow([d] + [datos[d].get(s, "") for s in SERIES])


def main():
    if "--sin-red" not in sys.argv:
        bajar()
    filas = list(csv.DictReader(open(DIARIO, encoding="utf-8")))
    por_mes = defaultdict(lambda: defaultdict(list))
    for r in filas:
        for s in SERIES:
            if r[s]:
                por_mes[r["fecha"][:7]][s].append((r["fecha"], float(r[s])))
    cols = ["mes", "cepo"]
    for s in SERIES:
        cols += [f"{s}_pico", f"{s}_fecha_pico", f"{s}_minimo", f"{s}_promedio", f"{s}_cierre"]
    cols += ["brecha_blue_oficial_promedio_pct", "dias_con_dato", "ultimo_dato"]
    out = []
    for mes in sorted(por_mes):
        fila = {"mes": mes, "cepo": "sí" if mes < FIN_CEPO[:7] else ("parcial (hasta el 14/04)" if mes == FIN_CEPO[:7] else "no")}
        for s in SERIES:
            v = por_mes[mes][s]
            if not v:
                continue
            pico = max(v, key=lambda x: (x[1], x[0]))
            fila.update({f"{s}_pico": pico[1], f"{s}_fecha_pico": pico[0], f"{s}_minimo": min(x[1] for x in v),
                         f"{s}_promedio": round(sum(x[1] for x in v) / len(v), 2), f"{s}_cierre": max(v)[1]})
        if fila.get("blue_promedio") and fila.get("oficial_promedio"):
            fila["brecha_blue_oficial_promedio_pct"] = round((fila["blue_promedio"] / fila["oficial_promedio"] - 1) * 100, 1)
        fila["dias_con_dato"] = len(por_mes[mes]["oficial"])
        fila["ultimo_dato"] = max(x[0] for s in SERIES for x in por_mes[mes][s])
        out.append(fila)
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    escribir_excel(out)
    print(f"{SALIDA.relative_to(RAIZ)}: {len(out)} meses ({out[0]['mes']} a {out[-1]['mes']}, último dato {out[-1]['ultimo_dato']})")


def escribir_excel(out):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = "Dólar por mes"
    enc = ["Mes", "Cepo", "Oficial BNA pico", "Fecha pico", "Oficial promedio", "Oficial cierre", "Mayorista pico",
           "Mayorista cierre", "MEP pico", "MEP promedio", "Blue pico", "Fecha pico blue", "Blue promedio", "Blue cierre",
           "Brecha blue/oficial (promedio, %)"]
    campos = ["mes", "cepo", "oficial_pico", "oficial_fecha_pico", "oficial_promedio", "oficial_cierre", "mayorista_pico",
              "mayorista_cierre", "mep_pico", "mep_promedio", "blue_pico", "blue_fecha_pico", "blue_promedio", "blue_cierre",
              "brecha_blue_oficial_promedio_pct"]
    for j, h in enumerate(enc, 1):
        c = ws.cell(1, j, h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1D5F86")
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[c.column_letter].width = 13
    amarillo = PatternFill("solid", fgColor="FFF2CC")
    for i, f in enumerate(out, 2):
        for j, k in enumerate(campos, 1):
            v = f.get(k, "")
            c = ws.cell(i, j)
            if k == "mes" and re.fullmatch(r"\d{4}-\d{2}", str(v)):
                c.value, c.number_format = date(int(v[:4]), int(v[5:7]), 1), "mm-yyyy"
            elif "fecha" in k and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v)):
                c.value, c.number_format = date.fromisoformat(v), "dd-mm-yyyy"
            else:  # números como celdas numéricas: pesos por dólar con 2 decimales, la brecha en % con 1
                celda_excel(c, v, k, "#,##0.0" if k.endswith("_pct") else FMT_PRECIO if k != "cepo" else None)
            if f["cepo"] != "no":
                c.fill = amarillo
    ws.freeze_panes = "B2"
    n = len(out) + 3
    ws.cell(n, 1, "Precio de venta en pesos por dólar. Amarillo: meses con cepo (hasta el 14-04-2025), con brecha grande entre oficial y blue.")
    ws.cell(n + 1, 1, "Fuente: api.argentinadatos.com (BNA, BCRA y mercados). Datos diarios en fuentes_originales/indices/dolar_diario.csv. "
                      "Se rearma con: python herramientas/dolar_mensual.py")
    wb.save(SALIDA.with_suffix(".xlsx"))


if __name__ == "__main__":
    main()
