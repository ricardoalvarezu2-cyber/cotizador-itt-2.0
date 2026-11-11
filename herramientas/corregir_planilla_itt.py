"""Corrige un Excel de presupuesto editado a mano (Planilla ITT): cantidades del detalle enlazadas a las hojas Materiales / MO y servicios y factores como fórmula (un factor escrito en la Planilla ITT pasa a los parámetros del Resumen). Uso: python herramientas/corregir_planilla_itt.py <carpeta con in/ y out/> <nombres sin .xlsx>. Pedido de Matías, 11-11-2026."""
import openpyxl, re, sys
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment
base = sys.argv[1]
GRIS = PatternFill("solid", fgColor="D9D9D9")
FAC = {"Materiales, MO y SVC": "FactorMateriales", "Materiales (con contingencia)": "FactorMateriales", "MO ITT y servicios": "FactorMO",
       "Válvulas Taval": "FactorTaval", "Mano de obra de terceros": "FactorMO", "Seguro de caución": "FactorMO", "Transporte": "FactorMO"}
for n in sys.argv[2:]:
    wb = openpyxl.load_workbook(f"{base}/in/{n}.xlsx")
    ws = wb["Planilla ITT"]; log = []
    # 1) factores: si se escribió uno a mano en la Planilla ITT, pasa a los parámetros del Resumen; la celda queda con la fórmula
    for r in range(15, 21):
        lab = ws.cell(r, 1).value; d = ws.cell(r, 4)
        if lab not in FAC: continue
        nombre = FAC[lab]
        if isinstance(d.value, (int, float)):
            dest = wb.defined_names[nombre].attr_text.replace("$", "")
            sh, cel = dest.split("!"); actual = wb[sh][cel].value
            costo_cero = lab in ("Seguro de caución", "Transporte")
            if not costo_cero and actual != d.value:
                wb[sh][cel].value = d.value
                log.append(f"{nombre} (Resumen {cel}): {actual} → {d.value} (lo que estaba escrito en Planilla ITT D{r})")
            d.value = f"={nombre}"
        d.fill = GRIS
        if r == 15: d.comment = Comment("El factor se cambia en la hoja Resumen (sección 4, celdas amarillas). Acá es fórmula.", "ITT")
    # 2) cantidades del detalle enlazadas a la hoja de origen
    k = 0
    for r in range(25, ws.max_row + 1):
        m = re.match(r"=('?)([^'!]+)\1!J(\d+)$", str(ws.cell(r, 6).value or ""))
        if m and not str(ws.cell(r, 3).value or "").startswith("="):
            ws.cell(r, 3).value = f"='{m.group(2)}'!C{m.group(3)}"; k += 1
    log.append(f"{k} cantidades de la Planilla ITT enlazadas a Materiales / MO y servicios")
    wb.save(f"{base}/out/{n}.xlsx")
    print(n, *log, sep="\n  ")
