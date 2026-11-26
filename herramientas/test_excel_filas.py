"""Prueba de excel_filas.correr_formula / insertar_filas. Correr: python herramientas/test_excel_filas.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from openpyxl import Workbook
from excel_filas import correr_formula, insertar_filas

C = [
    ("=SUM(F56:F70)", "Cotización", "=SUM(F56:F70)"),          # como Excel: insertar justo debajo del rango no lo agranda
    ("=SUM(F56:F80)", "Cotización", "=SUM(F56:F85)"),          # rango que contiene el punto: crece
    ("=C68*E68", "Cotización", "=C68*E68"),                     # antes del punto: igual
    ("=F71+F77+$F$94", "Cotización", "=F76+F82+$F$99"),
    ("=Cotización!F21", "Pie de Venta", "=Cotización!F21"),
    ("=Cotización!F134", "Pie de Venta", "=Cotización!F139"),
    ("='Cotización'!A80:B90", "Otra", "='Cotización'!A85:B95"),
    ("=F80", "Pie de Venta", "=F80"),                           # otra hoja sin prefijo: no se toca
    ('=IF(A80="F80 texto",LOG10(F80),0)', "Cotización", '=IF(A85="F80 texto",LOG10(F85),0)'),
]
err = 0
for f, hoja, esperado in C:
    r = correr_formula(f, hoja, "Cotización", 71, 5)
    if r != esperado:
        err += 1
        print("ERROR", f, "->", r, "esperado", esperado)
wb = Workbook(); ws = wb.active; ws.title = "Cotización"
ws["A80"] = 1; ws["A90"] = "=A80*2"; ws.merge_cells("B80:D80"); ws.row_dimensions[80].height = 30
insertar_filas(wb, "Cotización", 71, 5)
if ws["A85"].value != 1 or ws["A95"].value != "=A85*2" or "B85:D85" not in [str(m) for m in ws.merged_cells.ranges] or ws.row_dimensions[85].height != 30:
    err += 1; print("ERROR insertar_filas", ws["A95"].value, [str(m) for m in ws.merged_cells.ranges])
print("excel_filas OK" if not err else f"{err} errores")
sys.exit(1 if err else 0)
