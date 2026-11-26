"""Recotización por skid (2 puentes): cantidades del plano D2/P&ID H2 con redmarks contra la rev. 2 (TAVAL/70).
Solo los renglones que cambian; el resto de la rev. 2 queda igual. Precios: carpeta de Drive de Ricardo
(Precios proveedores, ya cargada en el catálogo) y cotización END del 16-11-2026. Fórmulas en el Excel."""
from openpyxl import Workbook
from openpyxl.styles import Font
DOLAR_NOV26 = 1574.35  # oficial BNA venta promedio 2026-11 (conocimiento/costos/dolar_mensual.csv)
F = [  # renglón, cant plano, cant rev2, precio nuevo, tipo, fuente, precio rev2
 ("Esférica 2\" #600 RF (VF + 2 VE por puente)", 6, 8, 416, "firme", "rev. 2 (stock Devlon)", 416),
 ("Esférica 1\" #600 bloqueo bypass", 2, 2, 53.22, "firme", "rev. 2", 53.22),
 ("Globo 1\" #600 regulación bypass", 2, 2, 56.70, "firme", "rev. 2 (G000254R05008V)", 56.70),
 ("Esférica 3/4\" 2000# venteos y purgas", 8, 2, 39, "firme", "rev. 2", 39),
 ("Esférica 1/2\" 2000# (PI y tomas V-cone)", 6, 4, 36, "firme", "rev. 2", 36),
 ("Esférica 1\" 2000# NPT (IQ)", 2, 0, 44.64, "similar", "Taval Lista 30 x 0,52 (VAL-04883, 09-2025)", 0),
 ("Brida WNRF 2\" #600 Sch 80 A105", 34, 48, 19.31, "firme", "Provemet 288979 (29-10-2026)", 19.42),
 ("Brida WNRF 1\" #600 Sch 160 A105 (bypass, ITT supone bridadas)", 4, 0, 25.00, "estimado", "Oil Metal 07-2025 (BRI-01201)", 0),
 ("Brida WNRF 1 1/2\" #600 (termovainas)", 6, 2, 18.02, "firme", "rev. 2 (Complemet)", 18.02),
 ("Junta espiralada 2\" #600 316L/grafito, anillo ext.", 32, 46, 1.29, "firme", "Miyashiro 50630 (05-11-2026)", 8),
 ("Junta espiralada 1 1/2\" #600", 6, 0, 0, "SIN PRECIO", "pedir a Miyashiro", 0),
 ("Junta espiralada 1\" #600", 6, 0, 0.90, "similar", "Miyashiro 09-2025 (JUN-01690)", 0),
 ("Espárrago 5/8\" x 4 1/4\" B7 c/2 tuercas 2H (2\" #600)", 240, 368, 0.68 + 2 * 0.22, "estimado", "Delgado 1556: 5/8 x 3 3/4 + 2 tuercas; pedir 4 1/4", 8),
 ("Espárrago 3/4\" x 4 1/4\" B7 c/2 tuercas 2H (1 1/2\" #600)", 24, 0, 1.18 + 2 * 0.36, "estimado", "Delgado 1556: 3/4 x 4 1/2 + 2 tuercas", 0),
 ("Espárrago 5/8\" x 3 3/4\" B7 c/2 tuercas 2H (1\" #600)", 24, 0, 0.68 + 2 * 0.22, "firme", "Delgado 1556 (05-11-2026)", 0),
 ("Espaciador / portaorificio 2\" #600 (nota 3 P&ID)", 2, 0, 0, "SIN PRECIO", "pedir cotización", 0),
 ("Sockolet 3/4\" 3000#", 8, 0, 3.45, "firme", "Provemet 289897 (05-11-2026)", 0),
 ("Sockolet 1/2\" 3000#", 2, 0, 2.75, "firme", "Provemet 289897 (05-11-2026)", 0),
 ("Sockolet 1\" 3000#", 2, 14, 6, "estimado", "rev. 2", 6),
 ("Reducción conc. 3\" x 2\" Sch 80 (HD nota 4, a confirmar)", 12, 0, 70, "estimado", "planilla Sacde 01-2026 (ABW-02346)", 0),
 ("Tee 3\" x 1 1/2\" Sch 80 (HD nota 4, a confirmar)", 6, 2, 38.72, "similar", "Oil Metal 37278 tee 3\" (30-10-2026); rev. 2: tee 2\"x1 1/2\" 33,59", 33.59),
 ("Caño S/C 3\" Sch 80 (tramos TE, 0,3 m c/u)", 1.8, 0, 27.78, "firme", "Provemet 288974 (29-10-2026)", 0),
 ("Sensor RTD + termovaina (TE/TW)", 6, 4, 689, "firme", "rev. 2 (ABB)", 689),
 ("Transmisor de temperatura TIT", 4, 2, 803, "firme", "rev. 2", 803),
 ("Manifold 2 vías M2 1/2\" (PI)", 2, 0, 143.65, "firme", "ABB OPP-26-9039842 (05-11-2026)", 0),
 ("Inyector de químicos (excluido por falta de HD)", 0, 2, 0, "excluido", "se saca: estaba cobrado y excluido", 2100),
 ("Bastidor (kg; 789 kg netos del C-PL + 20 % desperdicio)", 946, 1200, 1.5, "firme", "rev. 2 (USD/kg)", 1.5),
 ("Pintura skid (m2; 64 m2 / 3 skids)", 21.3, 18, 50, "firme", "precios_usuario (Ricardo)", 50),
 ("Servicio Rx (por servicio)", 2, 2, round(670000 / DOLAR_NOV26, 2), "firme", "END 16-11-2026: $670.000 / 1.574,35", 408),
 ("Servicio LP (por servicio)", 2, 2, round(420000 / DOLAR_NOV26, 2), "firme", "END 16-11-2026: $420.000 / 1.574,35", 294),
]
wb = Workbook(); ws = wb.active; ws.title = "Recotización por skid"
ws.append(["Borrador, sin revisar. Por skid (2 puentes). Solo renglones que cambian contra la rev. 2; el resto queda igual."])
ws.append(["Renglón", "Cant. plano", "Cant. rev. 2", "USD/un nuevo", "Tipo", "Fuente", "USD/un rev. 2", "Subtotal nuevo", "Subtotal rev. 2", "Diferencia"])
for c in ws[2]: c.font = Font(bold=True)
for i, r in enumerate(F, start=3):
    ws.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], f"=B{i}*D{i}", f"=C{i}*G{i}", f"=H{i}-I{i}"])
n = 2 + len(F)
ws.append(["TOTAL", None, None, None, None, None, None, f"=SUM(H3:H{n})", f"=SUM(I3:I{n})", f"=SUM(J3:J{n})"])
for c in ws[n + 1]: c.font = Font(bold=True)
for row in ws.iter_rows(min_row=3, min_col=2, max_col=10):
    for c in row: c.number_format = '#,##0.00'
ws.column_dimensions["A"].width = 58; ws.column_dimensions["F"].width = 50
wb.save("recotizacion_por_skid.xlsx")
