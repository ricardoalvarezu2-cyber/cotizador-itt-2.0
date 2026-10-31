import json, math
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
d = json.load(open('/tmp/itt_ej/datos.json'))
wb = Workbook(); ws = wb.active; ws.title = "Pedido de cotización"
AZ = PatternFill("solid", fgColor="1F4E79"); GR = PatternFill("solid", fgColor="E7EEF5"); AM = PatternFill("solid", fgColor="FFF2CC")
B = Side(style="thin", color="9AA9B8"); BOX = Border(left=B, right=B, top=B, bottom=B)
W = Font(bold=True, color="FFFFFF"); NEG = Font(bold=True)
for i, w in enumerate([34, 10, 14, 13, 12, 14, 16, 30], 1): ws.column_dimensions[get_column_letter(i)].width = w
f = 1
def t(txt, size=11, bold=True):
    global f
    ws.cell(f, 1, txt).font = Font(bold=bold, size=size); f += 1
def cab(cols):
    global f
    for i, c in enumerate(cols, 1):
        x = ws.cell(f, i, c); x.font = W; x.fill = AZ; x.alignment = Alignment(wrap_text=True, vertical="center"); x.border = BOX
    ws.row_dimensions[f].height = 46; f += 1
def fila(vals, fmts=None, fill=None):
    global f
    for i, v in enumerate(vals, 1):
        x = ws.cell(f, i, v); x.border = BOX; x.alignment = Alignment(wrap_text=True, vertical="top")
        if fmts and fmts[i-1]: x.number_format = fmts[i-1]
        if fill: x.fill = fill
    f += 1
t("ITT S.A. — Pedido de cotización de mano de obra: soldadura y roscado", 14)
t("EJEMPLO (borrador): caso de control CTRL-C01, skid colector para PAD de 6 pozos 6\"/3\" #300", 10, False)
t("Fecha: 31-10-2026 · Precios en USD sin IVA · Cantidades por equipo", 10, False)
f += 1
t("1. Alcance")
for a, b in [("Equipo", "Skid colector 6\"/3\" serie 300 (1 equipo)"), ("Material", "Acero al carbono: caño ASTM A-106 Gr B, accesorios ASTM A-234 WPB, bridas ASTM A-105"),
             ("Materiales", "Los provee ITT (caños, accesorios, bridas, válvulas). El tercero aporta consumibles de soldadura y gases"),
             ("Lugar", "Taller del tercero o planta ITT (a definir). Todas las juntas de este equipo son de taller"),
             ("Ensayos", "Radiografía y prueba hidráulica: a cargo de ITT (indicar si se requiere otra cosa)"),
             ("Estructura", "Bastidor del skid: 800 kg de perfiles y chapa ASTM A-36 (cotizar aparte si corresponde)")]:
    ws.cell(f, 1, a).font = NEG; ws.cell(f, 2, b); ws.merge_cells(start_row=f, start_column=2, end_row=f, end_column=8); f += 1
f += 1
t("2. Soldaduras")
cab(["Tipo de junta", "Ø (pulg)", "Schedule / clase", "Espesor (mm)", "Juntas", "Pulgadas equivalentes", "Posiciones del plano", "Comentario"])
i0 = f
for tipo, dn, sch, esp, nj, pe, pos in d["sold"]:
    com = "1 soldadura al caño + 1 a la pieza que recibe" if "Derivación" in tipo else ""
    dtxt = {0.75: '3/4"', 0.5: '1/2"', 1.5: '1 1/2"'}.get(dn, f'{dn:g}"')
    fila([tipo, dtxt, sch, esp, math.ceil(nj - 1e-9), pe, pos, com], [None, None, None, "#,##0.00", "0", "#,##0.00", None, None])
ws.cell(f, 1, "Total").font = NEG
ws.cell(f, 5, f"=SUM(E{i0}:E{f-1})").number_format = "0"; ws.cell(f, 6, f"=SUM(F{i0}:F{f-1})").number_format = "#,##0.00"
for c in (1, 5, 6): ws.cell(f, c).font = NEG; ws.cell(f, c).border = BOX
f += 1
ws.cell(f, 1, "Pulgada equivalente = Ø × (espesor del schedule ÷ espesor estándar del mismo Ø, mínimo 1). Derivaciones: × 1,75 (sockolet). Juntas contadas desde la lista de materiales: confirmar con el plano.").font = Font(italic=True, size=9)
ws.merge_cells(start_row=f, start_column=1, end_row=f, end_column=8); f += 2
t("3. Roscado y armado roscado")
cab(["Pieza", "Ø", "Schedule / clase", "Extremos", "Cantidad", "Roscas a hacer (si la pieza se fabrica)", "Posición del plano", "Comentario"])
for pos, desc, dia, sch, ext, q, un, ro in d["rosc"]:
    com = "Si se compra hecho, solo se arma" if ro else "Se arma (rosca de fábrica)"
    fila([desc, dia, sch, ext, q, ro, pos, com], [None, None, None, None, "0", "0", None, None])
ws.cell(f, 1, "NPT = rosca cónica americana. -M macho, -H hembra. PE = extremo plano.").font = Font(italic=True, size=9)
ws.merge_cells(start_row=f, start_column=1, end_row=f, end_column=8); f += 2
t("4. Cotización del tercero (completar)")
cab(["Concepto", "", "", "", "Cantidad", "Precio unitario USD", "Total USD", "Comentario"])
filas_p = [("Soldadura (por pulgada equivalente)", f"=F{i0+len(d['sold'])}"), ("Roscado (por rosca)", f"=SUM(F{i0+len(d['sold'])+5}:F{i0+len(d['sold'])+4+len(d['rosc'])})"),
           ("Armado de piping y montaje", 1), ("O bien: precio global por equipo (todo lo anterior)", 1)]
p0 = f
for c, q in filas_p:
    ws.merge_cells(start_row=f, start_column=1, end_row=f, end_column=4)
    fila([c, None, None, None, q, None, f"=IF(F{f}=\"\",\"\",E{f}*F{f})", None], [None]*4 + ["#,##0.00", "#,##0.00", "#,##0.00", None])
    ws.cell(f-1, 6).fill = AM; ws.cell(f-1, 8).fill = AM
for a in ("Plazo de entrega (días)", "Validez de la oferta", "Proveedor / contacto"):
    ws.cell(f, 1, a).font = NEG; ws.cell(f, 2).fill = AM; ws.merge_cells(start_row=f, start_column=2, end_row=f, end_column=8); f += 1
f += 1
ws.cell(f, 1, "Celdas amarillas: las completa el proveedor. Si cotiza global, dejar vacíos los precios unitarios.").font = Font(italic=True, size=9)
ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_options.horizontalCentered = True
wb.save('/home/user/cotizador-itt/ejemplos/ejemplo_pedido_soldadura_roscado_tercero.xlsx')
print("ok")
