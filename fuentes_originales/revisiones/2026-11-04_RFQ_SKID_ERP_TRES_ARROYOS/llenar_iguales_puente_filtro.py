"""Completa con productos IGUALES las RFQ del puente de medición y del filtro coalescente (ERP Tres Arroyos, 04-11-2026)."""
import openpyxl, copy, sys
sys.path.insert(0, 'herramientas')
from numeros import fmt
from openpyxl.styles import Font, Alignment
S = sys.argv[1]
NUM = '#,##0.00'
NOTA = "Precios: solo productos IGUALES del catálogo de ITT (sin similares ni sugeridos). USD sin IVA, ajustados al 04-11-2026. Borrador, sin revisar."
PL = "plano SCE-ME-315-039 (cómputo COT26-0135-002)"
LBR = "Marca: el listado del cliente (SCE-IN-501-0015) admite para bridas solo Futura y Francovigh; %s no figura."
LAC = "Marca: el listado del cliente (SCE-IN-501-0015) admite para accesorios a soldar solo Curvo Sold; Renard no figura."

def estilo(c, ref, wrap=False, fmt=None):
    if ref.has_style:
        c.font = copy.copy(ref.font); c.border = copy.copy(ref.border); c.fill = copy.copy(ref.fill)
    c.alignment = Alignment(wrap_text=wrap, vertical="top")
    if fmt: c.number_format = fmt

# ---------- Puente de medición ----------
wb = openpyxl.load_workbook(f"{S}/pm/rfq.xlsx"); ws = wb.worksheets[0]
ig = {  # id: (antecedente, fecha, original, ajustado, observación)
 "PM05": ("Grupo Provemet cot. 288979 ítem 5 · catálogo BRI-01295", "29-10-2026", 23.42, 23.42,
          "IGUAL: Brida Welding Neck Sch 40 Raised Face Serie 150 ASTM A 105 ANSI B16.5 4\" (Sch STD/40 según %s). %s" % (PL, LBR % "Provemet")),
 "PM05B": ("Planilla de costo ITT: TECHINT Proyecto Los Toldos, Skid Sand Jetting Desarenado (LM costo Desarenador rev ventas REV.1) · catálogo JUN-02778", "23-12-2025", 15.00, 15.46,
          "IGUAL: junta espiralada 4\" 150# AISI 316/grafito c/anillo ext. ac. zinc. e int. Proveedor y marca no figuran en la planilla: comprar Klinger/Teadit/Garlock (marca homologada)."),
 "PM06": ("Lista Renard 12-2025, cód. 11297 · catálogo BRI-01313", "26-12-2025", 58.91, 60.72,
          "IGUAL: Bridas WN 6\" Sch40 S150 RF ASTM A105/ANSI B16.5 (Sch STD/40 según %s). %s" % (PL, LBR % "Renard")),
 "PM10": ("Lista Renard 12-2025, cód. 3400 · catálogo ABW-00111", "26-12-2025", 26.20, 27.01,
          "IGUAL: Codo Radio Largo 90° 4\" Std ASTM A234 WPB. " + LAC),
 "PM11B": ("Lista Renard 12-2025, cód. 5293 · catálogo AFO-00721", "26-12-2025", 3.51, 3.62,
          "IGUAL: Cupla 3/4\" NPT S3000 ASTM A105."),
}
V = "Sin igual: el material es 'S/ Esp. CAMUZZI' (%s) y no hay precio de esférica paso total #150 RF con ese material definido y marca del listado." % PL
ESP = "Sin igual: falta la medida del espárrago (Ø x largo) y no hay precio A193 B7/A194 2H de esa medida."
CAN = "Sin igual: no hay caño ASTM A53 Gr B %s\" Sch40 con precio en el catálogo (solo triple certificación A53/A106/API 5L, que el buscador no toma como igual)."
sin = {
 "PM01": "Sin igual: equipo fabricado (filtro FM-06), no es material de catálogo.",
 "PM02": "Sin igual: pieza fabricada (carretel según la turbina que provee el cliente).",
 "PM03": V, "PM04": V, "PM05C": ESP, "PM06C": ESP,
 "PM06B": "Sin igual: el único precio de junta espiralada 6\" 150# AISI 316/grafito es del período con cepo (estimado, c/anillo interior solo).",
 "PM07": "Sin igual: el plano pide la tee a tope en ASTM A-105 (material de forjados) y el catálogo solo tiene tees STD en A234 WPB.",
 "PM08": "Sin igual: el plano pide la tee a tope en ASTM A-105 (material de forjados) y el catálogo solo tiene tees STD en A234 WPB.",
 "PM09": "Sin igual: el plano dice material 'S/ Esp. CAMUZZI', sin definir.",
 "PM11": "Sin igual en el catálogo: no hay termovaina 3/4\" NPT AISI 316 con precio.",
 "PM12": "Sin igual en el catálogo: conjunto cupla con válvula y tapón, material 'Segun fabricante'.",
 "PM16": "Sin igual: el plano pide la cupla en ASTM A-106 (norma de caño; las cuplas B16.11 son A-105) y no hay precio del conjunto con válvula.",
 "PM17": "Sin igual en el catálogo: no hay sensor de temperatura 0-100 °C 4-20 mA 3/4\" de las marcas homologadas con ese rango.",
 "PM18": "Sin igual: renglón global sin largo de tubing.",
 "PM19": "Sin igual: renglón global sin medidas ni cantidades de fittings.",
 "PM20": "Sin igual en el catálogo: no hay precio de manifold 3 vías inoxidable sin medida ni conexión.",
 "PM13": "Fabricación ITT según SCE-RE-110-0006: no es material de catálogo.",
 "PM13B": "Sin igual en el catálogo: la única placa AISI 304 con precio es de 2022 (período con cepo).",
 "PM21": CAN % 4, "PM21B": CAN % 4, "PM22": CAN % 6, "PM22B": CAN % 6,
}
ws["L5"] = "Antecedente (fecha · precio original USD)"; estilo(ws["L5"], ws["K5"], wrap=True); ws["L5"].font = copy.copy(ws["K5"].font)
for row in range(6, 34):
    i = ws[f"B{row}"].value; ref = ws[f"H{row}"]
    if i in ig:
        a, f, n, o, q = ig[i]
        ws[f"L{row}"] = f"{a} · {f} · USD {fmt(n, 2)}"; estilo(ws[f"L{row}"], ref, wrap=True)
        ws[f"M{row}"] = o; estilo(ws[f"M{row}"], ref, fmt=NUM)
        ws[f"N{row}"] = f"=F{row}*M{row}"; estilo(ws[f"N{row}"], ref, fmt=NUM)
        ws[f"O{row}"] = q; estilo(ws[f"O{row}"], ref, wrap=True)
    else:
        ws[f"O{row}"] = sin[i]; estilo(ws[f"O{row}"], ref, wrap=True)
ws["M34"] = "Total iguales (USD, sin IVA)"; ws["N34"] = "=SUM(N6:N33)"; ws["N34"].number_format = NUM
ws["M34"].font = Font(bold=True); ws["N34"].font = Font(bold=True)
ws["A4"] = NOTA; ws["A4"].font = Font(bold=True, color="C00000")
ws.column_dimensions["L"].width = 45; ws.column_dimensions["O"].width = 60
wb.save(f"{S}/pm/RFQ_REV4_1_PUENTE_MEDICION_precios_iguales.xlsx")

# ---------- Filtro coalescente ----------
wb = openpyxl.load_workbook(f"{S}/fc/rfq.xlsx"); ws = wb["01_MTO_EXPANDIDO"]
BR = "Sin igual: falta el schedule del cuello de la brida WN."
sinf = {
 "CH01": "Sin igual: virola rolada (pieza fabricada); el catálogo no tiene virola Ø2100 x 50 mm ni chapa A516 Gr70 de 50 mm con precio.",
 "CH02": "Sin igual: falta el diámetro y el espesor del casquete; no hay casquete A516 Gr70 Ø2100 con precio.",
 "CH03": "Sin igual: falta el diámetro y el espesor del casquete; no hay casquete A516 Gr70 Ø2100 con precio.",
 "P01": "Sin igual: el renglón va por unidad sin largo; el caño se compra por metro.",
 "P02": "Sin igual: el renglón va por unidad sin largo; el caño se compra por metro.",
 "B01": BR, "B02": BR,
 "E01": "Sin igual: falta la medida del espárrago (Ø x largo).",
 "E02": "Sin igual: falta la medida de la tuerca.",
 "I01": "Sin igual: interno fabricado, no es material de catálogo.",
 "I02": "Sin igual: interno fabricado, no es material de catálogo.",
 "F01": "Sin igual en el catálogo: no hay cartucho coalescente de esa medida con precio.",
 "F02": "Sin igual en el catálogo: no hay cartucho coalescente de esa medida con precio.",
 "T01": "Sin igual: falta el diámetro y el espesor del tubing.",
 "T02": "Sin igual: falta tipo y medida de los fittings.",
 "S01": "Sin igual: falta la medida del perfil UPN.",
 "S02": "Sin igual: falta la medida del ángulo.",
 "S03": "Sin igual: falta el tipo de rejilla (malla, planchuela portante); no hay rejilla con precio por m².",
}
for row in range(2, 20):
    i = ws[f"B{row}"].value
    ws[f"O{row}"] = sinf[i]; estilo(ws[f"O{row}"], ws[f"F{row}"], wrap=True)
ws.column_dimensions["O"].width = 60
ws["A21"] = NOTA + " Ningún renglón tiene un igual en el catálogo."; ws["A21"].font = Font(bold=True, color="C00000")
wb.save(f"{S}/fc/RFQ_REV4_3_FILTRO_COALESCENTE_precios_iguales.xlsx")
print("ok")
