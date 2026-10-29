"""Genera la lista de materiales y servicios para el área de Compras (pedido de cotización a proveedores).

Uso: python herramientas/lista_compras.py cotizaciones/<carpeta>

Formato (pedido de Matías, 28-10-2026):
- La lista sale TAL CUAL la transcripción del documento de origen (plano, planilla del cliente o cómputo de diseño):
  mismas columnas, mismo texto y mismo orden. Fuente: pedido/transcripcion.json
  ({"fuente", "tablas": [{"titulo", "columnas", "filas"}], "nota"}); la primera columna de cada tabla es la posición.
  Si no hay transcripción, se usa pedido/lista_materiales_plano.csv.
- A la derecha, lo que calcula ITT: cantidad a comprar en la unidad que corresponde (m de caño con la tira completa,
  kg de chapa o perfil, unidades), kg aproximados (tablas de conocimiento/tecnico) y de dónde salió la cantidad.
- Después, las columnas para Compras: Proveedor, Precio unit. USD, Plazo y Anotaciones (las anotaciones traen
  precargadas las aclaraciones de Ventas; Compras agrega las suyas).
- Lo que se compra y no figura en el documento (juntas y espárragos, completar tira) va en una sección aparte.
- Hoja "Referencias internas": últimos precios conocidos y proveedores sugeridos. No se manda al proveedor.
Salida: <carpeta>/compras/<codigo>_pedido_materiales_compras.xlsx
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import FMT_TECNICO, celda_excel, fmt, fmtg  # noqa: E402
import controles_tablas as ct  # noqa: E402
from catalogo_materiales import atributos, expandir, familia_de  # noqa: E402
from indice_proyectos import norm  # noqa: E402

AZUL, GRIS, AMAR, VERDE = "1D5F86", "EEF3F6", "FBEFD6", "E6F2EA"
H = Font(bold=True, color="FFFFFF")
B = Border(*(Side(style="thin", color="B7C4CC"),) * 4)
W = Alignment(wrap_text=True, vertical="top")


def kg_por_unidad(p, it):
    """kg por unidad (o por metro) de un renglón, con las tablas de conocimiento/tecnico. (kg, fuente) o (None, motivo)."""
    serie = re.findall(r"\b(150|300|600|900|1500|2500|2000|3000|6000)\b", p.get("serie_sch", ""))
    sch = re.findall(r"\b(STD|XS|XXS|\d{2,3})\b", p.get("serie_sch", "").upper().replace("SCH", ""))
    sch = [s for s in sch if s not in serie]
    t = " ".join([p.get("descripcion", ""), p.get("diametro", ""), f"#{serie[0]}" if serie else "", f"sch {sch[0]}" if sch else "",
                  p.get("material", ""), p.get("extremos", "")])
    t = expandir(norm(t))
    fam = familia_de(t)
    at = atributos(t, fam)
    kg, _, fuente = ct.peso_item({"descripcion": p.get("descripcion", ""), "especificacion": "", "unidad": it.get("unidad", "un")}, at, fam,
                                 ct.leer(ct.TEC / "canos_peso_superficie.csv"), ct.leer(ct.TEC / "bridas_peso.csv"),
                                 ct.leer_acc(), ct.leer(ct.TEC / "valvulas_peso.csv"))
    m = re.search(r"(\d[\d.,]*)\s?kg", norm(it.get("especificacion", "") + " " + p.get("descripcion", "")))
    if kg is None and m and it.get("unidad", "un") == "un":  # kilos escritos en el renglón (skid, chapa)
        kg, fuente = float(m.group(1).replace(".", "").replace(",", ".")) / max(float(it.get("cantidad") or 1), 1), "kilos escritos en el renglón"
    return kg, fuente


def es_tira(it):
    """Fila de compra extra para completar la tira de un caño (precotizar.py: "Completar ... tira/barra")."""
    return bool(re.match(r"completar|sobrante", norm(it.get("descripcion", ""))))


def celda(ws, r, j, v, fill=None, fmt=None, bold=False, col=None, documento=False):
    c = ws.cell(r, j)
    if col is None:
        c.value = v
    else:  # números como celdas numéricas, nunca texto (Matías, 29-10-2026)
        celda_excel(c, v, col, fmt, documento)
    c.border, c.alignment = B, W
    if fill:
        c.fill = PatternFill("solid", fgColor=fill)
    if fmt:
        c.number_format = fmt
    if bold:
        c.font = Font(bold=True)
    return c


def main(carpeta):
    carpeta = Path(carpeta)
    cfg = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    plano = {p["pos"].strip(): p for p in csv.DictReader(open(carpeta / "pedido" / "lista_materiales_plano.csv", encoding="utf-8"))}
    ruta_tr = carpeta / "pedido" / "transcripcion.json"
    if ruta_tr.exists():
        tr = json.load(open(ruta_tr, encoding="utf-8"))
    else:  # sin transcripción literal: la tabla del plano de trabajo
        cols = ["Pos", "Descripción", "Ø", "Serie / SCH", "Material", "Marca / modelo", "Cant.", "Unidad"]
        tr = {"fuente": "pedido/lista_materiales_plano.csv (tabla de trabajo; no hay transcripción literal del documento)",
              "tablas": [{"titulo": "LISTA DE MATERIALES", "columnas": cols,
                          "filas": [[p["pos"], p["descripcion"], p["diametro"], p["serie_sch"], p["material"], p.get("modelo_fabricante", ""),
                                     p["cantidad"], p.get("unidad", "")] for p in plano.values()]}]}
    comp = cfg.get("compras", {})
    n = float(cfg["parametros"]["N"])
    eq = cfg["equipo"]
    items = [i for i in cfg["items"] if i["grupo"] == "material"]
    por_pos = {}
    for it in items:
        por_pos.setdefault(str(it["pos"]).strip(), []).append(it)
    en_doc = {str(f[0]).strip() for t in tr["tablas"] for f in t["filas"]}

    wb = Workbook()
    ws = wb.active
    ws.title = "Materiales"
    ws["A1"] = f"PEDIDO DE COTIZACIÓN DE MATERIALES · {cfg['codigo']}"
    ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    ws["A2"] = f"{cfg['titulo']}  ·  {fmtg(n)} {eq['plural'] if n != 1 else eq['singular']}"
    ws["A2"].font = Font(bold=True)
    datos = [("Preparó (Ventas)", cfg["preparo"]), ("Fecha", date.fromisoformat(cfg["fecha"]).strftime("%d-%m-%Y")),
             ("Respuesta de proveedores", date.fromisoformat(comp["fecha_respuesta"]).strftime("%d-%m-%Y") if comp.get("fecha_respuesta") else "a definir"),
             ("Material en planta", f"a los {comp.get('material_en_planta_dias', '—')} días de la OC del cliente"),
             ("Lugar de entrega", comp.get("lugar_entrega", "Planta ITT, Quilmes Oeste")),
             ("Origen de la lista", tr["fuente"])]
    r = 3
    for k, v in datos:
        r += 1
        ws.cell(r, 1, k).font = Font(bold=True)
        ws.cell(r, 3, v)
    if comp.get("requisitos_generales"):
        r += 2
        ws.cell(r, 1, "Requisitos generales").font = Font(bold=True)
        for t in comp["requisitos_generales"]:
            r += 1
            ws.cell(r, 1, "• " + t)

    calc = ["Cant. a comprar", "Unidad", "Kg aprox.", "Origen de la cantidad"]
    resp = ["Proveedor", "Precio unit. USD", "Plazo", "Anotaciones"]
    ancho_calc, ancho_resp = [11, 8, 10, 30], [22, 13, 12, 45]
    kg_total, sin_kg = 0.0, []

    def fila_calculos(pos, ws, r, j0):
        """Escribe las columnas calculadas y de Compras para la posición pos, desde la columna j0."""
        nonlocal kg_total
        its = por_pos.get(pos, [])
        p = plano.get(pos, {})
        extras = [i for i in items if re.fullmatch(re.escape(pos) + r"[b-z]", str(i["pos"]).strip()) and es_tira(i)]  # completar tira
        if its:
            it = its[0]
            q = sum(float(i["cantidad"]) for i in its) * n
            q_ext = sum(float(i["cantidad"]) for i in extras) * n
            unidad = it.get("unidad", "un")
            cant_doc = str(p.get("cantidad", ""))
            if q_ext:
                origen = f"{fmtg(q)} {unidad} para {fmtg(n)} {eq['plural'] if n != 1 else eq['singular']} + {fmtg(q_ext)} {unidad} para completar la tira"
            elif re.search(r"medida del dibujo|no indicada|no indica", norm(p.get("descripcion", ""))):
                origen = "el documento no da cantidad: medida del dibujo (±20%)"
            else:
                origen = f"documento × {fmtg(n)}" if n != 1 else "documento"
            kg, fuente = kg_por_unidad(p or {"descripcion": it["descripcion"]}, it)
            kg_tot = round(kg * (q + q_ext), 1) if kg is not None else None
            if kg_tot is not None:
                kg_total += kg_tot
            else:
                sin_kg.append(pos)
            vals = [round(q + q_ext, 3), unidad, kg_tot if kg_tot is not None else "—", origen]
        else:
            vals = ["—", "", "", "no se cotiza (ver cotización)"]
        nota = "; ".join(x for x in [comp.get("notas", {}).get(pos, ""), comp.get("cantidad_compra", {}).get(pos, "")] if x)
        for k, v in enumerate(vals):
            celda(ws, r, j0 + k, v, GRIS, "#,##0.00" if k in (0, 2) and isinstance(v, (int, float)) else None)
        for k, v in enumerate(["", "", "", nota]):
            celda(ws, r, j0 + 4 + k, v, AMAR, "#,##0.00" if k == 1 else None)

    for tabla in tr["tablas"]:
        r += 2
        ws.cell(r, 1, tabla["titulo"]).font = Font(bold=True, size=12, color=AZUL)
        r += 1
        cols = tabla["columnas"]
        cab = cols + calc + resp
        for j, c in enumerate(cab, 1):
            x = celda(ws, r, j, c)
            x.font = H
            x.fill = PatternFill("solid", fgColor=AZUL if j <= len(cols) else ("5D6B75" if j <= len(cols) + 4 else "B7791F"))
            x.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.row_dimensions[r].height = 32
        for f in tabla["filas"]:
            r += 1
            for j, v in enumerate(f, 1):
                celda(ws, r, j, v, col=cab[j - 1] if j <= len(cab) else "", documento=True)
            fila_calculos(str(f[0]).strip(), ws, r, len(cols) + 1)
    if tr.get("nota"):
        r += 1
        ws.cell(r, 2, "Nota del documento: " + tr["nota"]).font = Font(italic=True)

    # lo que se compra y no figura en el documento
    adic = [i for i in items if str(i["pos"]).strip() not in en_doc and not es_tira(i)]
    if adic:
        r += 2
        ws.cell(r, 1, "ADICIONALES (no figuran en el documento; los agrega ITT)").font = Font(bold=True, size=12, color=AZUL)
        r += 1
        cab = ["Pos", "Descripción", "Especificación", "Cant. a comprar", "Unidad", "Kg aprox.", "Por qué"] + resp
        for j, c in enumerate(cab, 1):
            x = celda(ws, r, j, c)
            x.font = H
            x.fill = PatternFill("solid", fgColor="5D6B75" if j <= 7 else "B7791F")
        for it in adic:
            r += 1
            q = float(it["cantidad"]) * n
            vals = [it["pos"], it["descripcion"], it.get("especificacion", ""), round(q, 3), it.get("unidad", "un"), "—",
                    "compra mínima o nota del documento"]
            for j, v in enumerate(vals, 1):
                celda(ws, r, j, v, GRIS if j > 3 else None, "#,##0.00" if j == 4 else None, col=cab[j - 1])
            for k, v in enumerate(["", "", "", comp.get("notas", {}).get(str(it["pos"]), "")]):
                celda(ws, r, 8 + k, v, AMAR, "#,##0.00" if k == 1 else None)
    r += 2
    ws.cell(r, 1, f"Peso aproximado de lo que tiene tabla: {fmt(kg_total, 0)} kg" + (f" (sin dato: pos {', '.join(sin_kg)})" if sin_kg else "")).font = Font(bold=True)
    r += 1
    ws.cell(r, 1, "Columnas azules: tal cual el documento. Grises: cálculo de ITT. Amarillas: para que Compras complete (proveedor, precio sin IVA, plazo y anotaciones).").font = Font(italic=True, color="5D6B75")
    ncols = max(len(t["columnas"]) for t in tr["tablas"])
    for j, w in enumerate([6, 46, 9, 8, 8, 8, 20][:ncols] + [10] * max(0, ncols - 7) + ancho_calc + ancho_resp, 1):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    s = wb.create_sheet("Servicios")
    cab = ["Servicio", "Aclaraciones"] + resp
    for j, (c, w) in enumerate(zip(cab, [55, 45, 22, 13, 12, 45]), 1):
        x = celda(s, 1, j, c)
        x.font = H
        x.fill = PatternFill("solid", fgColor=AZUL if j <= 2 else "B7791F")
        s.column_dimensions[x.column_letter].width = w
    for i, sv in enumerate(comp.get("servicios", []), 2):
        celda(s, i, 1, sv["servicio"])
        celda(s, i, 2, sv.get("nota", ""))
        for k in range(4):
            celda(s, i, 3 + k, "", AMAR)

    ref = wb.create_sheet("Referencias internas")
    cab = ["Pos", "Descripción (cotización)", "Proveedores sugeridos", "Último precio USD", "Fecha", "Tipo", "Coincide", "Diferencia"]
    for j, (c, w) in enumerate(zip(cab, [7, 45, 30, 13, 11, 8, 10, 50]), 1):
        x = celda(ref, 1, j, c)
        x.font = H
        x.fill = PatternFill("solid", fgColor="5D6B75")
        ref.column_dimensions[x.column_letter].width = w
    for i, it in enumerate(items, 2):
        f = it["fuentes"][0]
        provs = comp.get("proveedores", {}).get(str(it["pos"]), f["proveedor"].split("·")[0].strip())
        for j, v in enumerate([it["pos"], it["descripcion"], provs, f["precio"] or "SIN PRECIO", f["fecha"], f["tipo"], f.get("coincide", ""), f.get("diferencia", "")], 1):
            celda(ref, i, j, v, "F8E1DE" if f.get("coincide") == "sin_ref" else None, "#,##0.00" if j == 4 and f["precio"] else None)
    ref.cell(len(items) + 3, 1, "Uso interno: no mandar al proveedor.").font = Font(italic=True, color="9A3B2E")

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
