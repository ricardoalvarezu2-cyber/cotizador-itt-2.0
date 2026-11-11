import openpyxl, re, sys
from datetime import datetime
from openpyxl.styles import PatternFill
base = sys.argv[1]
NAR = PatternFill("solid", fgColor="FBEFD6")
T = "fuentes_originales/ofertas_texto/ALONZO RED/2 - ERP B° Pilara/5.Proveedores 3ros/OFERTA TA7785A-ITT-REG TA956-NATURGY.pdf"
P = {  # fila de Materiales: (precio, fecha, tipo, proveedor, antecedente, diferencia, documento)
 6: (9545.0, "2026-06-16", "cotización", "Tormene Americana, oferta TA7785A (16-06-2026)", "Regulador pilotado TA956-FC+SSV DN 3\" #300, configuración monitor FTC + bloqueo OPSO, conexionado inox 3/8\", indicador de posición", "Serie 300 con OPSO por serie 150 sin OPSO (más caro: precio conservador); P1 25/7 bar, Q 8.000 Sm3/h", T),
 7: (6073.0, "2026-06-16", "cotización", "Tormene Americana, oferta TA7785A (16-06-2026)", "Regulador pilotado TA956-DFO DN 3\" #300, activo FTO silenciado, conexionado inox 3/8\", indicador de posición", "Serie 300 por serie 150 (precio conservador)", T),
 8: (304.0, "2026-01-15", "planilla interna", "ABAC / Fittinox (planilla TAVAL/40, filtro FM3)", "12 m de tubing inox 1/2\" ABAC a 11 USD/m (CAN-02661) + conectores doble virola 30 + 30 + 112 (TAVAL/40 pos 22, 29 y 30)", "tubing 1/2\" por 3/8\"; cantidad estimada 4 reguladoras × 3 m. El conexionado de los pilotos ya viene en la oferta de Tormene", "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx"),
 11: (67.91, "2025-12-23", "planilla interna", "Renard cód. 5292 (cupla) + planilla interna (esférica)", "Cupla 1/2\" NPT S3000 A105 (AFO-00715, 2,71) + válvula esférica 1/2\" NPT S3000 A105 (VAL-03527, 65,20)", "cupla A105 por A-106 (consulta R78); esfera inox y a prueba de fuego a confirmar", "conocimiento/precios/lista_renar_2025-12.csv; catálogo VAL-03527"),
 47: (70.40, "2024-11-01", "estimado", "Stock ITT (INS-01587)", "Termovaina 3/4\" NPT L 6\" conexión 1/2\" NPT AISI 316L", "precio de stock 2024 llevado a valor actual (× 0,64): pedir cotización", "fuentes_originales/stock_valorizado_2024-11.xlsx"),
 57: (25.0, "2026-10-10", "estimado", "Planilla YPF/28 Lic 69343 (JUN-03422)", "Junta espiralada RF 4,5 mm 300 LB SS316 c/grafito, anillo ext. zincado, 8\"", "Serie 300 por serie 150 (precio conservador)", "fuentes_originales/ofertas_texto/YPF/28- Lic 69343 - SKIDS CONCENTRADORES VCD26217 - BLOQUE LAN"),
}
wb = openpyxl.load_workbook(f"{base}/in/001.xlsx")
m = wb["Materiales"]
for r, (pr, fe, tipo, prov, ant, dif, doc) in P.items():
    vals = {5: "Similar", 6: pr, 7: datetime.fromisoformat(fe), 13: tipo, 14: prov, 16: ant, 17: dif, 18: doc}
    for c, v in vals.items():
        m.cell(r, c).value = v
    for c in (5, 6, 7, 14): m.cell(r, c).fill = NAR
# Planilla ITT: proveedor, equivalencia y fecha de esos renglones
i = wb["Planilla ITT"]
for r in range(25, i.max_row + 1):
    mm = re.match(r"=('?)Materiales\1!J(\d+)$", str(i.cell(r, 6).value or ""))
    if mm and int(mm.group(2)) in P:
        pr, fe, tipo, prov, ant, dif, doc = P[int(mm.group(2))]
        i.cell(r, 8).value = prov; i.cell(r, 9).value = "Similar"; i.cell(r, 10).value = datetime.fromisoformat(fe)
        i.cell(r, 9).fill = PatternFill("solid", fgColor="FBEFD6")
wb.save(f"{base}/out/001.xlsx"); print("ok")
