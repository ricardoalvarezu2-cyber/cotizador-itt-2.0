"""Genera la lista de materiales y servicios para el área de Compras (pedido de cotización a proveedores).

Uso: python herramientas/lista_compras.py cotizaciones/<carpeta>

Toma la tabla del plano (pedido/lista_materiales_plano.csv) y cotizacion.json (cantidad de equipos,
fuentes de precio y la sección "compras": notas por posición, cantidades de compra, servicios y requisitos).
Salida: <carpeta>/compras/<codigo>_pedido_materiales_compras.xlsx

La especificación sale del plano, tal cual. Los precios son solo de referencia (último precio conocido, sin
ajuste) para que Compras sepa contra qué comparar; no se mandan al proveedor.
"""
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

AZUL = "1D5F86"


def main(carpeta):
    carpeta = Path(carpeta)
    cfg = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    plano = list(csv.DictReader(open(carpeta / "pedido" / "lista_materiales_plano.csv", encoding="utf-8")))
    comp = cfg.get("compras", {})
    n = cfg["parametros"]["N"]
    eq = cfg["equipo"]
    por_pos = {}
    for it in cfg["items"]:
        if it["grupo"] == "material":
            por_pos.setdefault(it["pos"], it)

    H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor=AZUL)
    B = Border(*(Side(style="thin", color="B7C4CC"),) * 4)
    W = Alignment(wrap_text=True, vertical="top")
    wb = Workbook(); ws = wb.active; ws.title = "Materiales"

    ws["A1"] = f"PEDIDO DE COTIZACIÓN DE MATERIALES · {cfg['codigo']}"; ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    ws["A2"] = f"{cfg['titulo']}  ·  {n} {eq['plural']}"; ws["A2"].font = Font(bold=True)
    hoy = date.fromisoformat(cfg["fecha"])
    datos = [("Preparó (Ventas)", cfg["preparo"]),
             ("Fecha", hoy.strftime("%d/%m/%Y")),
             ("Respuesta de proveedores", date.fromisoformat(comp["fecha_respuesta"]).strftime("%d/%m/%Y") if comp.get("fecha_respuesta") else "a definir"),
             ("Plazo de entrega requerido", f"Material en planta a los {comp.get('material_en_planta_dias', '—')} días de la OC del cliente"),
             ("Lugar de entrega", comp.get("lugar_entrega", "Planta ITT, Quilmes Oeste")),
             ("Plano / documento", next((v for k, v in cfg["pedido"]["datos_html"] if k.startswith("Documento")), ""))]
    for r, (k, v) in enumerate(datos, 4):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        ws.cell(r, 1, k).font = Font(bold=True); ws.cell(r, 4, v)
    r = 4 + len(datos) + 1
    ws.cell(r, 1, "Requisitos generales").font = Font(bold=True)
    for t in comp.get("requisitos_generales", []):
        r += 1; ws.cell(r, 1, "• " + t)
    r += 2
    cols = ["Ítem", "Pos. plano", "Descripción (según plano)", "Ø", "Serie / SCH", "Material", "Extremos", "Marca / modelo exigido",
            f"Cant. por {eq['singular']}", "Cant. a comprar", "Unidad", "Requisitos y aclaraciones para el proveedor",
            "Proveedores sugeridos", "Último precio de referencia USD (uso interno)", "Fecha del precio", "Respuesta: proveedor", "Respuesta: precio unit. USD", "Respuesta: plazo (días)", "Observaciones"]
    anchos = [5, 7, 42, 9, 9, 18, 10, 16, 9, 12, 7, 55, 30, 14, 11, 16, 13, 12, 25]
    for j, (c, w) in enumerate(zip(cols, anchos), 1):
        x = ws.cell(r, j, c); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[x.column_letter].width = w
    ws.row_dimensions[r].height = 45
    ws.freeze_panes = ws.cell(r + 1, 4)
    cab = r
    RESP = PatternFill("solid", fgColor="FBEFD6")
    for i, p in enumerate(plano, 1):
        it = por_pos.get(p["pos"])
        provs, ref, fecha_ref = "", "", ""
        if it:
            vistos = []
            for f in it["fuentes"]:
                nombre = f["proveedor"].split(":")[0].split("(")[0].split("·")[0].replace("Valor usado en PRES 24879", "").strip()
                if f["tipo"] in ("cot", "lista", "stock") and nombre and nombre not in vistos:
                    vistos.append(nombre)
            provs = " / ".join(vistos)
            base = it["fuentes"][0]
            ref, fecha_ref = base["precio"], base["fecha"]
        provs = comp.get("proveedores", {}).get(p["pos"], provs)  # si Ventas los cargó explícitos, mandan esos
        cant = float(p["cantidad"])
        compra = comp.get("cantidad_compra", {}).get(p["pos"], cant * n)
        fila = [i, p["pos"], p["descripcion"], p["diametro"], p["serie_sch"], p["material"], p["extremos"], p["modelo_fabricante"],
                cant, compra, p.get("unidad", "un"), comp.get("notas", {}).get(p["pos"], ""), provs, ref, fecha_ref, "", "", "", ""]
        r += 1
        for j, v in enumerate(fila, 1):
            c = ws.cell(r, j, v); c.border = B; c.alignment = W
            if j in (9, 10):
                c.number_format = "0.##"
            if j == 14 and v != "":
                c.number_format = "#,##0.00"; c.font = Font(color="5D6B75")
            if j >= 16:
                c.fill = RESP
    ws.auto_filter.ref = f"A{cab}:S{r}"
    r += 2
    ws.cell(r, 1, "Columnas amarillas: para que Compras cargue la respuesta de cada proveedor y se actualice la cotización (cotizacion.json).").font = Font(italic=True, color="5D6B75")
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True

    s = wb.create_sheet("Servicios")
    cols = ["Servicio", "Proveedores sugeridos", "Referencia (uso interno)", "Aclaraciones", "Respuesta: precio USD", "Respuesta: plazo", "Observaciones"]
    for j, (c, w) in enumerate(zip(cols, [55, 28, 50, 45, 14, 12, 25]), 1):
        x = s.cell(1, j, c); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical="center")
        s.column_dimensions[x.column_letter].width = w
    for i, sv in enumerate(comp.get("servicios", []), 2):
        for j, v in enumerate([sv["servicio"], sv["proveedores"], sv["referencia"], sv.get("nota", ""), "", "", ""], 1):
            c = s.cell(i, j, v); c.border = B; c.alignment = W
            if j >= 5:
                c.fill = RESP

    salida = carpeta / "compras"
    salida.mkdir(exist_ok=True)
    ruta = salida / f"{cfg['codigo']}_pedido_materiales_compras.xlsx"
    wb.save(ruta)
    print(ruta)
    return ruta


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
