"""Planilla verificada (método del skill cotizar-skids-equipos, el mismo de la PC0 de la Lic 69343):
parte de la planilla de Ricardo (rev. 1, pedido/) y entrega <nombre>_rev3.xlsx con
- la hoja Cotización corregida contra el plano D2 / P&ID H2 / HD D1 (amarillo claro = cambiado, verde = agregado,
  columna M = Aclaración, N = cantidad anterior);
- hojas nuevas con fórmulas: Precios proveedores (adopta el más barato que cumple), Precios a confirmar (única carga),
  Verificación (para la dirección, con controles en 0), Pintura m2, Soldaduras, END y Verif. espesores.
Uso: python cotizaciones/COT26-0330-004_YPF_GASLIFT_PUENTEINYREG/armar_planilla_verificada.py
Todo por skid (2 puentes), como la planilla original. Rev. 3 porque la rev. 2 (26-10-2026) ya existe en TAVAL/70."""
import os, sys, shutil
from math import pi
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter as L

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "herramientas"))
from excel_filas import insertar_filas

ORIG = os.path.join(AQUI, "pedido", "Cot_Puente_Iny_y_Reg_2pulg_serie600_SAP_1000653143_rev1.xlsx")
SALIDA = os.path.join(AQUI, "Cot_Puente_Iny_y_Reg_2pulg_serie600_SAP_1000653143_rev3.xlsx")
CAMBIO = PatternFill("solid", fgColor="FFF2CC")   # amarillo claro: valor cambiado
NUEVO = PatternFill("solid", fgColor="E2EFDA")    # verde: fila agregada
AMARILLO = PatternFill("solid", fgColor="FFFF00")  # precio a confirmar (formato condicional)
AZUL = PatternFill("solid", fgColor="D9E1F2")     # encabezados / celdas de entrada
B = Font(bold=True)
NUM = '#,##0.00'

# ---------------------------------------------------------------------------------------------------------------
# Precios: un renglón por artículo. q = cotizaciones que CUMPLEN la especificación {proveedor: (USD, "cotización")}.
# conf = motivo si queda a confirmar (va a la hoja Precios a confirmar); None = firme.
PROV = ["Provemet", "Oil Metal", "Delgado", "Miyashiro", "ABB", "Taval", "Meditecna", "Otro"]
P = {}
def precio(k, item, anterior, ant_origen, q=None, obs="", conf=None, provisorio=None):
    P[k] = dict(item=item, anterior=anterior, ant_origen=ant_origen, q=q or {}, obs=obs, conf=conf, provisorio=provisorio)

precio("BR3", 'Brida WNRF 3" #600 Sch 80 A105', 19.78, "Complemet (planilla 06-2026)",
       obs="Sin cotización nueva de 3\" #600 en la carpeta de Drive.", conf="Precio de planilla 06-2026 sin cotización adjunta: confirmar vigencia (parece bajo: la de 2\" cuesta 19,31)")
precio("CA3", 'Caño S/C 3" Sch 80 A106 Gr.B (USD/m)', 33.93, "Renard (lista)",
       q={"Provemet": (27.78, "Provemet 288974 (29-10-2026)")})
precio("TR32", 'Tee reducción 3" x 2" Sch 80 BW A234 WPB', 64.11, "Renard (lista 27-05-2025)",
       conf="Lista Renard 27-05-2025: confirmar vigencia (Oil Metal 37278 no la cotiza)")
precio("BR2", 'Brida WNRF 2" #600 Sch 80 A105', 19.42, "Complemet (planilla 06-2026)",
       q={"Provemet": (19.31, "Provemet 288979 (29-10-2026)")})
precio("TR215", 'Tee reducción 2" x 1 1/2" Sch 80 BW', 33.59, "Renard (lista)", obs="No va: los TE van en tramo de 3\" (HD nota 4).")
precio("BRSW15", 'Brida SWRF 1 1/2" #600 Sch 160 A105', 18.02, "Complemet (planilla 06-2026)",
       conf="Precio de planilla 06-2026 sin cotización adjunta: confirmar")
precio("JU2", 'Junta espiralada 2" #600 316L + grafito, anillo ext. AC zincado', 4, "Estimado MS juntas",
       q={"Miyashiro": (1.29, "Miyashiro 50630 (05-11-2026)")},
       obs="Miyashiro cotiza ESP SW AC 316LFG (anillo exterior). La HD del V-cone pide AISI 316/grafito e=4,5 con anillo ext. AC zincado: cumple. La planilla decía anillo int. y ext.")
precio("VC", 'Caudalímetro V-Cone 2" #600 en carrete', 3180, "Meditecna (hoja Instrumentos)",
       q={"Meditecna": (3180, "Meditecna (hoja Instrumentos), 60 días")},
       obs="Emerson/McCrometer 10.765,67 (105 días). La HD pide INTRA AUTOMATION o similar.")
precio("CA2", 'Caño S/C 2" Sch 80 A106 Gr.B (USD/m)', 16.62, "Renard (lista)",
       q={"Provemet": (13.61, "Provemet 288974 (29-10-2026)")})
precio("FQIT", "FQIT multivariable DP+P+T con totalizador (uno por puente)", 8577.82, "ABB XFC6200EX (hoja Instrumentos)",
       q={"ABB": (4211.76, "ABB 266CSH + manifold M26 (rev. 2 del 26-10-2026, 50 días)")},
       obs="XFC6200EX 8.577,52 (95 días) y Emerson 14.962,64 (84 días) más caros.",
       conf="Confirmar con ABB que el 266CSH tiene totalizador e indicación local que no se apaga (nota ** del P&ID) y el N° de cotización")
precio("IQ", "Inyector de químicos", 2100, "Estimado Yongjia / Mirbla", obs="Excluido por falta de HD (como dice la oferta).")
precio("SO1", 'Sockolet 1" 3000# A105', 6, "Estimado", conf="Estimado sin cotización; confirmar con el run de 2\"")
precio("ES58", 'Espárrago 5/8" x 4 1/4" B7 c/2 tuercas 2H (2" #600)', 8, "Estimado (planilla: 5/8\" x 5\")",
       obs="Delgado 1556 cotizó 5/8\" x 3 3/4\" (más corto: no sirve). Referencia: 0,68 + 2 tuercas 0,22 = 1,12 el juego.",
       conf="Pedir a Delgado 5/8\" x 4 1/4\" (o x 5\") con 2 tuercas 2H: el 8,00 es estimado")
precio("TE2", 'Tee normal 2" Sch 80 BW A234 WPB', 24.06, "Renard (lista)", conf="Lista Renard: confirmar vigencia")
precio("BR1", 'Brida WNRF 1" #600 Sch 160 A105', 25.00, "Oil Metal (07-2025)", conf="Precio de 07-2025: pedir cotización")
precio("JU1", 'Junta espiralada 1" #600 316L + grafito, anillo ext.', 0.90, "Miyashiro (09-2025)", conf="Precio de 09-2025: confirmar")
precio("JU15", 'Junta espiralada 1 1/2" #600 316L + grafito, anillo ext.', 1.29, "Criterio ITT: precio de la de 2\" (Miyashiro 50630)",
       conf="Sin cotización: pedir a Miyashiro")
precio("ES34", 'Espárrago 3/4" x 4 1/4" B7 c/2 tuercas 2H (1 1/2" #600)', None, "—",
       q={"Delgado": (1.90, "Delgado 1556 (05-11-2026): 3/4\" x 4 1/2\" 1,18 + 2 tuercas 0,36")},
       obs="Se adopta el de 4 1/2\" (más largo: sirve).")
precio("ES5838", 'Espárrago 5/8" x 3 3/4" B7 c/2 tuercas 2H (1" #600)', None, "—",
       q={"Delgado": (1.12, "Delgado 1556 (05-11-2026): 0,68 + 2 tuercas 0,22")})
precio("ESP", 'Espaciador 2" #600 para orificio de restricción', 19.31, "Criterio ITT: precio de una brida WN 2\" #600",
       conf="Sin cotización: pedir espaciador 2\" #600 (nota 3 del P&ID)")
precio("SO34", 'Sockolet 3/4" 3000# A105', None, "—", q={"Provemet": (3.45, "Provemet 289897 (05-11-2026), run 3\"")},
       conf="Cotizado para run 3\": confirmar para run 2\"")
precio("SO12", 'Sockolet 1/2" 3000# A105', None, "—", q={"Provemet": (2.75, "Provemet 289897 (05-11-2026)")},
       conf="Confirmar para run 2\"")
precio("RC32", 'Reducción concéntrica 3" x 2" Sch 80 BW A234 WPB', 70, "Planilla Sacde 01-2026 (sin proveedor)",
       conf="Sin cotización de proveedor: pedir (Oil Metal / Renard)")
precio("TR315", 'Tee reducción 3" x 1 1/2" Sch 80 BW A234 WPB', 38.72, "Criterio ITT: tee normal 3\" Oil Metal 37278 (30-10-2026)",
       conf="Sin cotización de la tee de reducción: pedir")
precio("NI34", 'Niple 3/4" Sch 160 A106 B NPT/PE', 9.53, "Planilla 03-2025 (NIP-02873)", conf="Precio de 03-2025 sin proveedor: pedir cotización")
precio("NI12", 'Niple 1/2" Sch 160 A106 B NPT/PE L 100', 10, "Planilla de costo ITT 06-2026 (NIP-05009)", conf="Sin proveedor: pedir cotización")
precio("NI1", 'Niple 1" Sch 160 A106 B NPT/PE', 10.74, "Criterio ITT: niple 3/4\" Sch 160 del stock ITT 11-2024 (NIP-01783)", conf="Sin cotización: pedir")
# Válvulas Taval (factor 1)
precio("V2", 'Válvula esférica 2" #600 RF', 400.40, "Taval R Alvarez (rev. 1)", q={"Taval": (400.40, "Taval R Alvarez (rev. 1)"), "Otro": (416, "Stock Devlon (rev. 2)")},
       conf="Confirmar con la lista Taval (skill cotizar-valvulas-taval) y stock")
precio("VR", 'Válvula de retención 2" #600', 133.67, "Taval (rev. 1)", q={"Taval": (133.67, "Taval (rev. 1)"), "Otro": (254, "Stock 37138 (rev. 2)")},
       conf="Confirmar con la lista Taval y stock")
precio("V1_3000", 'Válvula esférica 1" #3000', 27.49, "Taval (rev. 1)", obs="No va: el plano pide 3/4\", 1/2\" y 1\" de 2000#.")
precio("FY", 'Filtro Y 2" #600', 195.93, "Taval (rev. 1)", q={"Taval": (195.93, "Taval (rev. 1)"), "Otro": (378, "rev. 2")},
       conf="Confirmar con la lista Taval y stock")
precio("V34", 'Válvula esférica 3/4" 2000#', 39, "rev. 2", q={"Taval": (39, "rev. 2 (26-10-2026)")}, conf="Confirmar con la lista Taval")
precio("V12", 'Válvula esférica 1/2" 2000#', 36, "rev. 2", q={"Taval": (36, "rev. 2 (26-10-2026)")}, conf="Confirmar con la lista Taval")
precio("V1", 'Válvula esférica 1" 2000# NPT (IQ)', None, "—", q={"Taval": (44.64, "Taval Lista 30 × 0,52 (09-2025)")}, conf="Lista de 09-2025: confirmar")
precio("V1_600", 'Válvula esférica 1" #600 (bypass)', 53.22, "rev. 2", q={"Taval": (53.22, "rev. 2 (26-10-2026)")})
precio("G1_600", 'Válvula globo 1" #600 (bypass)', 56.70, "rev. 2", q={"Taval": (56.70, "rev. 2, G000254R05008V")})
# Instrumentos
precio("FV", 'Válvula globo 2" #600 limitadora con actuador eléctrico (FV)', 8600, "Doma, estimado por Sergio",
       conf="Estimado: pedir mejor oferta (la rev. 2 dice lo mismo)")
precio("PI", "Manómetro (PI) con válvula integral de bloqueo y purga", 120, "Weisz (sin cotización adjunta)", conf="Sin cotización adjunta")
precio("M5", "Manifold de 5 vías", 349, "Abac",
       conf="El precio ABB del FQIT ya incluye un manifold M26 de 5 vías: confirmar si este renglón sobra")
precio("TWTE", "Termovaina + termoelemento (FQIT)", 689, "248 + 425 + 16 (planilla)", conf="Sin cotización adjunta")
precio("TIT", "Transmisor de temperatura completo (TE + TW + TIT)", 1176.57, "ABB TSP331 + TE y TW (hoja Instrumentos)")
precio("M2", 'Manifold 2 vías 1/2" (M2 del PI)', None, "—", q={"ABB": (143.65, "ABB OPP-26-9039842 (05-11-2026), M26 2 vías")})
precio("BOT", "Botellones de purga de tomas de presión (notas 8 y 10)", 450, "rev. 2 (sin proveedor)", conf="Sin cotización")
precio("UB", "U bolts y tornillería", 200, "Estimado", conf="Estimado")
# perfiles: USD/kg de Provemet 288977 (29-10-2026)
PERF = [("UPN 100", 13.41, 10.60, 235.6), ("UPN 160", 24.95, 18.80, 812.2), ("UPN 200", 36.72, 25.30, 1156.0)]
CHAPAS_KG, CHAPA_USD_KG = 88.4 + 72.8 + 1.0, 2.0   # C-PL-003004: chapas 12,7 / 15,88 / AISI 304 6,35

# ---------------------------------------------------------------------------------------------------------------
# Correcciones de la hoja Cotización (filas de la rev. 1). cant=None no cambia la cantidad.
COR = {  # fila: (clave precio, nueva cant, cant plano, aclaración)
    56: ("BR3", None, 2, "Colector 3\": entrada y extremo."),
    57: ("CA3", 5.8, 5.8, "4 m de colector + 6 tramos de 0,3 m para los TE (HD nota 4: ampliar a 3\" en cada TE a 90°)."),
    58: ("TR32", None, 2, ""),
    59: ("BR2", 34, 34, "Plano D2 con redmarks: 17 por puente (VF 2, FY 2, V-cone 2, VE 4, FV 2, orificio 2, VR 2, salida 1). Eran 48."),
    60: ("TR215", 0, 0, "No va: los TE se instalan en tramo de 3\" (HD nota 4); ver tee 3\" x 1 1/2\"."),
    61: ("BRSW15", 6, 6, "6 termovainas por skid (TW de la FQIT + TE XXXA y XXXC de cada puente). Eran 2."),
    62: ("JU2", 32, 32, "16 por puente (la brida de salida va con la junta del cliente). HD V-cone: anillo exterior."),
    63: ("VC", None, 2, ""),
    64: ("CA2", None, 24, "Unidad: metros (el precio es por metro)."),
    65: ("FQIT", 2, 2, "El P&ID tiene un FQIT por puente; la rev. 1 tenía uno solo."),
    66: ("IQ", 0, 0, "Excluido por falta de HD, como dice la oferta: estaba cobrado y excluido a la vez."),
    67: ("SO1", 2, 2, "Solo la inyección de químicos (1\" NPT). Los venteos, purgas y tomas van en 3/4\" y 1/2\" (filas nuevas)."),
    68: ("JU2", 0, 0, "Renglón repetido de la junta 2\" (doble conteo)."),
    69: ("ES58", 240, 240, "30 uniones × 8. Medida 5/8\" x 4 1/4\" (tabla esparragos_por_brida); antes =8×fila de juntas repetida."),
    70: ("TE2", None, 8, ""),
    81: ("V2", 6, 6, "1 VF + 2 VE por puente (redmarks: se eliminan 2 VF por puente). Eran 10."),
    82: ("VR", None, 2, ""),
    83: ("V1_3000", 0, 0, "No va: el plano pide 3/4\", 1/2\" y 1\" de 2000# (filas nuevas)."),
    84: ("FY", None, 2, ""),
    89: ("FV", None, 2, ""),
    90: ("PI", None, 2, ""),
    91: ("M5", None, 2, ""),
    92: ("TWTE", None, 2, "TW de la FQIT (una por puente)."),
    93: ("TIT", None, 4, "TE/TIT XXXA y XXXC por puente (esquema del P&ID); la nota **** dice 3 por skid: consultar."),
    76: ("UB", None, 1, ""),
}
NUEVAS_PIPING = [  # (clave, descripción, material, cant, unid, aclaración)
    ("BR1", 'BRIDA WNRF Ø1" 600# Sch 160', "SA-105", 4, "un", "Bypass 1\" #600 (VE + VG por puente). ITT supone válvulas bridadas RF: a confirmar."),
    ("JU1", 'JUNTA ESPIRALADA Ø1" 600# RF', "AISI 316L + Grafito, anillo ext.", 6, "un", "3 uniones por puente en el bypass."),
    ("JU15", 'JUNTA ESPIRALADA Ø1.1/2" 600# RF', "AISI 316L + Grafito, anillo ext.", 6, "un", "Una por termovaina."),
    ("ES34", 'ESPÁRRAGOS 3/4" X 4 1/4". Con tuercas', "A193 B7 / A194 2H", 24, "un", "4 por brida 1 1/2\" #600."),
    ("ES5838", 'ESPÁRRAGOS 5/8" X 3 3/4". Con tuercas', "A193 B7 / A194 2H", 24, "un", "4 por unión 1\" #600 (6 uniones)."),
    ("ESP", 'ESPACIADOR Ø2" 600# (orificio de restricción)', "A105", 2, "un", "Nota 3 del P&ID: una brida con dos juntas y un espaciador."),
    ("SO34", 'SOCKOLET Ø3/4" 3000#', "SA-105", 8, "un", "4 por puente: venteos y purgas."),
    ("SO12", 'SOCKOLET Ø1/2" 3000#', "SA-105", 2, "un", "Toma del PI (las del V-cone vienen en el instrumento)."),
    ("RC32", 'REDUCCIÓN CONC. Ø3" x 2" Sch 80 BW', "SA-234 Gr.WPB", 12, "un", "HD nota 4: tramo de 3\" en cada TE (2 por termovaina)."),
    ("TR315", 'TEE REDUCCIÓN Ø3" x 1.1/2" Sch 80 BW', "SA-234 Gr.WPB", 6, "un", "HD nota 4: una por termovaina."),
    ("NI34", 'NIPLE Ø3/4" Sch 160 NPT/PE', "SA-106 Gr.B", 8, "un", "Sockolet - válvula NPT. Sch 80 no cumple por espesor (hoja Verif. espesores)."),
    ("NI12", 'NIPLE Ø1/2" Sch 160 NPT/PE', "SA-106 Gr.B", 2, "un", "Sockolet - válvula NPT del PI. Sch 80 no cumple (Verif. espesores)."),
    ("NI1", 'NIPLE Ø1" Sch 160 NPT/PE', "SA-106 Gr.B", 2, "un", "Sockolet - válvula NPT de la IQ. Sch 80 no cumple (Verif. espesores)."),
]
NUEVAS_VALV = [
    ("V34", 'VÁLVULA ESFÉRICA 3/4" 2000#', 8, "Venteos y purgas (4 por puente)."),
    ("V12", 'VÁLVULA ESFÉRICA 1/2" 2000#', 6, "PI + 2 tomas del V-cone por puente."),
    ("V1", 'VÁLVULA ESFÉRICA 1" 2000# NPT', 2, "Inyección de químicos (VF 1\" NPT)."),
    ("V1_600", 'VÁLVULA ESFÉRICA 1" #600 (VE bypass)', 2, "Esquema de bypass del P&ID."),
    ("G1_600", 'VÁLVULA GLOBO 1" #600 (VG bypass)', 2, "Esquema de bypass del P&ID."),
]
NUEVAS_INST = [
    ("M2", 'Manifold 2 vías 1/2" (M2)', 2, "M2 del PI XXXD (P&ID)."),
    ("BOT", "Botellones de purga tomas de presión", 2, "Notas 8 y 10 del P&ID."),
]

wb = openpyxl.load_workbook(ORIG)
ws = wb["Cotización"]
ws.column_dimensions["M"].width = 70; ws.column_dimensions["N"].width = 12

def marcar(c, fill=CAMBIO):
    c.fill = fill

# 1) correcciones en filas existentes (antes de insertar)
for r, (k, cant, plano, acl) in COR.items():
    if cant is not None and ws.cell(r, 3).value != cant:
        ws.cell(r, 14).value = ws.cell(r, 3).value  # N = cantidad anterior
        ws.cell(r, 3).value = cant; marcar(ws.cell(r, 3))
    if acl:
        ws.cell(r, 13).value = acl
    P[k].setdefault("filas", []).append(r)
ws["M55"] = "Aclaración (verificación 26-11-2026)"; ws["N55"] = "Cant. anterior"
ws["M55"].font = B; ws["N55"].font = B
# filas 62/68: el texto de la junta dice "ANILLO INT. Y EXT." → HD del V-cone: solo exterior
ws["B62"] = "AISI 316L + Grafito. ANILLO EXT. AC ZINCADO"; marcar(ws["B62"])
ws["A69"] = 'ESPÁRRAGOS 5/8" X 4 1/4". Con tuercas'; marcar(ws["A69"])
ws["D64"] = "m"; marcar(ws["D64"])
ws["D18"] = 1; marcar(ws["D18"]); ws["H18"] = "Transporte a costo (factor 1)"
ws["I1"] = ("VERIFICADA 26-11-2026 contra plano P-PL-003003 D2, P&ID PI-003012 D2 (H2) con redmarks, C-PL-003004 D1 y HD I-HD-003004 D1. "
            "Amarillo claro = cambiado; verde = agregado; amarillo fuerte = precio a confirmar (hoja 'Precios a confirmar'). Borrador, sin revisar.")
ws["I1"].font = Font(bold=True, color="C00000")

# 2) filas nuevas (de abajo hacia arriba; cada bloque se inserta ANTES de su última fila para que el SUM crezca solo)
insertar_filas(wb, "Cotización", 93, len(NUEVAS_INST))
insertar_filas(wb, "Cotización", 84, len(NUEVAS_VALV))
insertar_filas(wb, "Cotización", 70, len(NUEVAS_PIPING))
def nueva(r_orig):  # fila nueva de una fila de la rev. 1
    d = 0
    if r_orig >= 70: d += len(NUEVAS_PIPING)
    if r_orig >= 84: d += len(NUEVAS_VALV)
    if r_orig >= 93: d += len(NUEVAS_INST)
    return r_orig + d
for k in P:
    P[k]["filas"] = [nueva(r) for r in P[k].get("filas", [])]
PLANO = {nueva(r): v[2] for r, v in COR.items()}

def escribir(r, k, desc, mat, cant, unid, acl):
    ws.cell(r, 1).value = desc; ws.cell(r, 2).value = mat; ws.cell(r, 3).value = cant; ws.cell(r, 4).value = unid
    ws.cell(r, 6).value = f"=C{r}*E{r}"; ws.cell(r, 13).value = acl
    for c in range(1, 8): ws.cell(r, c).fill = NUEVO
    P[k]["filas"].append(r); PLANO[r] = cant
for i, (k, d, m, c, u, a) in enumerate(NUEVAS_PIPING):
    escribir(70 + i, k, d, m, c, u, a)
for i, (k, d, c, a) in enumerate(NUEVAS_VALV):
    escribir(nueva(84) - len(NUEVAS_VALV) + i, k, d, None, c, "un", a)
for i, (k, d, c, a) in enumerate(NUEVAS_INST):
    escribir(nueva(93) - len(NUEVAS_INST) + i, k, d, None, c, "un", a)

R_SUB_PIP, R_SKID_BAST, R_SUB_VAL, R_SUB_INS = nueva(71), nueva(75), nueva(85), nueva(94)
R_LEDESMA, R_PINT_P, R_PINT_S, R_END = nueva(98), nueva(114), nueva(115), nueva(120)
assert str(ws.cell(R_SUB_PIP, 6).value).startswith("=SUM(F56:F"), ws.cell(R_SUB_PIP, 6).value
assert ws.cell(R_LEDESMA, 1).value == "Edgardo Ledesma" and ws.cell(R_END, 1).value == "Servicios Rx y LP"

# ---------------------------------------------------------------------------------------------------------------
# 3) Hoja Precios a confirmar + Precios proveedores
pc = wb.create_sheet("Precios a confirmar"); pp = wb.create_sheet("Precios proveedores")
conf_keys = [k for k in P if P[k]["conf"] and P[k]["filas"] and any(ws.cell(r, 3).value for r in P[k]["filas"])]
pc["A1"] = "PRECIOS A CONFIRMAR - cargar aquí el precio confirmado (columnas amarillas). Es el único lugar de carga: el resto de la planilla lo toma solo."
pc["A1"].font = Font(bold=True, size=12)
pc["A2"] = "Ítems pendientes"; pc["C2"] = f'=COUNTIF(N6:N{5+len(conf_keys)},"PENDIENTE")'
pc["A3"] = "Total del pedido (Pie de Venta, USD)"; pc["C3"] = "='Pie de Venta'!G16"
hdr = ["N°", "Ítem", "Dónde se usa (Cotización, fila)", "Cant./skid", "Precio provisorio USD/un", "Origen del provisorio", "Motivo",
       "PRECIO CONFIRMADO USD/un", "Proveedor", "N° cotización / fecha", "Precio vigente", "Diferencia por skid", "", "Estado"]
for j, h in enumerate(hdr, 1):
    c = pc.cell(5, j, h); c.font = B; c.fill = AZUL; c.alignment = Alignment(wrap_text=True)
CONF_ROW = {}
for i, k in enumerate(conf_keys):
    r = 6 + i; CONF_ROW[k] = r; d = P[k]
    pc.cell(r, 1, i + 1); pc.cell(r, 2, d["item"])
    pc.cell(r, 3, ", ".join(f"f.{x}" for x in d["filas"]))
    pc.cell(r, 4, "=" + "+".join(f"Cotización!C{x}" for x in d["filas"]))
    pc.cell(r, 7, d["conf"])
    for j in (8, 9, 10): pc.cell(r, j).fill = AMARILLO
    pc.cell(r, 11, f'=IF(H{r}<>"",H{r},E{r})'); pc.cell(r, 12, f"=(K{r}-E{r})*D{r}")
    pc.cell(r, 14, f'=IF(H{r}<>"","CONFIRMADO","PENDIENTE")')
for w, col in zip((5, 45, 22, 10, 12, 40, 60, 14, 16, 22, 12, 12, 2, 13), "ABCDEFGHIJKLMN"):
    pc.column_dimensions[col].width = w

pp["A1"] = "COMPARATIVO DE PRECIOS DE PROVEEDORES (USD/un, sin IVA) - se adopta el más barato que cumple la especificación"
pp["A1"].font = Font(bold=True, size=12)
pp["A2"] = ("Fuentes: carpeta 'Precios proveedores' del Drive de Ricardo (Provemet 288974/77/79, 289897, 289909; Oil Metal 37278; "
            "Delgado 1542/1556; Miyashiro 50594, 50627-50630; ABB OPP-26-9039842; Bripetrol 16310), hoja Instrumentos de la planilla y rev. 2 (26-10-2026).")
pp["A3"] = ("Solo se cargan en las columnas de proveedor las cotizaciones que cumplen (igual o mayor espesor, espárragos iguales o más largos, "
            "misma serie y norma); las que no cumplen van en Observaciones. Precios netos, sin descuentos por adjudicación total.")
cols = ["Clave", "Ítem"] + PROV + ["Precio anterior", "Origen del anterior", "Precio sin confirmar", "Precio adoptado", "Ahorro unit.",
                                   "Proveedor elegido", "Cotización utilizada", "Observaciones"]
for j, h in enumerate(cols, 1):
    c = pp.cell(5, j, h); c.font = B; c.fill = AZUL; c.alignment = Alignment(wrap_text=True)
cP0 = 3; cANT = cP0 + len(PROV); cORI = cANT + 1; cSIN = cANT + 2; cADO = cANT + 3; cAHO = cANT + 4; cPRO = cANT + 5; cCOT = cANT + 6; cOBS = cANT + 7
rngq = lambda r: f"{L(cP0)}{r}:{L(cP0 + len(PROV) - 1)}{r}"
PP_ROW = {}
for i, (k, d) in enumerate(P.items()):
    r = 6 + i; PP_ROW[k] = r
    pp.cell(r, 1, k); pp.cell(r, 2, d["item"])
    for j, prov in enumerate(PROV):
        if prov in d["q"]:
            pp.cell(r, cP0 + j, d["q"][prov][0])
    pp.cell(r, cANT, d["anterior"]); pp.cell(r, cORI, d["ant_origen"])
    pp.cell(r, cSIN, f"=IF(COUNT({rngq(r)})=0,{L(cANT)}{r},MIN({rngq(r)}))")
    if k in CONF_ROW:
        cr = CONF_ROW[k]
        pp.cell(r, cADO, f"=IF('Precios a confirmar'!H{cr}<>\"\",'Precios a confirmar'!H{cr},{L(cSIN)}{r})")
    else:
        pp.cell(r, cADO, f"={L(cSIN)}{r}")
    pp.cell(r, cAHO, f'=IF({L(cANT)}{r}="","",{L(cANT)}{r}-{L(cADO)}{r})')
    # proveedor y cotización: el de menor precio (o el anterior si no hay cotización); si se confirmó, lo confirmado
    if d["q"]:
        prov_min, (v, cot) = min(d["q"].items(), key=lambda kv: kv[1][0])
    else:
        prov_min, cot = d["ant_origen"], f"Precio anterior: {d['ant_origen']}"
    if k in CONF_ROW:
        cr = CONF_ROW[k]
        q_ = lambda t: str(t).replace('"', '""')
        pp.cell(r, cPRO, f"=IF('Precios a confirmar'!H{cr}<>\"\",'Precios a confirmar'!I{cr},\"{q_(prov_min)}\")")
        pp.cell(r, cCOT, f"=IF('Precios a confirmar'!H{cr}<>\"\",'Precios a confirmar'!J{cr},\"{q_(cot)}\")")
        pc.cell(cr, 5, f"='Precios proveedores'!{L(cSIN)}{r}"); pc.cell(cr, 6, cot if d["q"] else d["ant_origen"])
    else:
        pp.cell(r, cPRO, prov_min); pp.cell(r, cCOT, cot)
    pp.cell(r, cOBS, d["obs"])
    for f_ in d["filas"]:  # la hoja Cotización toma precio, proveedor y cotización por fórmula
        ws.cell(f_, 5).value = f"='Precios proveedores'!{L(cADO)}{r}"
        ws.cell(f_, 7).value = f"='Precios proveedores'!{L(cPRO)}{r}"
        ws.cell(f_, 8).value = f"='Precios proveedores'!{L(cCOT)}{r}"
        ws.cell(f_, 5).number_format = NUM
r0 = 7 + len(P)
pp.cell(r0, 2, "PERFILERÍA (C-PL-003004 D1, por módulo de 3 skids)").font = B
for j, h in enumerate(["Perfil", "USD/m Provemet 288977", "kg/m", "USD/kg", "kg del plano (módulo)", "USD"], 2):
    pp.cell(r0 + 1, j, h).font = B
for i, (perf, usdm, kgm, kg) in enumerate(PERF):
    r = r0 + 2 + i
    pp.cell(r, 2, perf); pp.cell(r, 3, usdm); pp.cell(r, 4, kgm); pp.cell(r, 5, f"=C{r}/D{r}"); pp.cell(r, 6, kg); pp.cell(r, 7, f"=E{r}*F{r}")
rch = r0 + 2 + len(PERF)
pp.cell(rch, 2, "Chapas 12,7 / 15,88 / AISI 304 (sin cotización: USD 2/kg)"); pp.cell(rch, 5, CHAPA_USD_KG); pp.cell(rch, 6, CHAPAS_KG); pp.cell(rch, 7, f"=E{rch}*F{rch}")
rtot = rch + 1
pp.cell(rtot, 2, "Costo medio USD/kg de la estructura").font = B
pp.cell(rtot, 6, f"=SUM(F{r0+2}:F{rch})"); pp.cell(rtot, 7, f"=SUM(G{r0+2}:G{rch})"); pp.cell(rtot, 5, f"=G{rtot}/F{rtot}")
R_USDKG = f"'Precios proveedores'!E{rtot}"; R_KGMOD = f"'Precios proveedores'!F{rtot}"
for w, col in zip([8, 48] + [11] * len(PROV) + [11, 30, 11, 11, 10, 16, 45, 70], [L(i) for i in range(1, cOBS + 1)]):
    pp.column_dimensions[col].width = w

# bastidor: kg del plano por skid + 20 % desperdicio, al costo medio
rb = R_SKID_BAST
ws.cell(rb, 14).value = ws.cell(rb, 3).value; ws.cell(rb, 15).value = ws.cell(rb, 5).value
ws.cell(rb, 3).value = f"=ROUND({R_KGMOD}/3*1.2,0)"; ws.cell(rb, 5).value = f"={R_USDKG}"
ws.cell(rb, 7).value = "Provemet 288977 (perfiles) + chapas USD 2/kg"
ws.cell(rb, 13).value = "Peso del plano C-PL-003004 D1 (2.366,1 kg el módulo de 3 skids, sin el 15 % de uniones) / 3 + 20 % de desperdicio. Eran 1.200 kg a 1,50 estimado (O = precio anterior)."
marcar(ws.cell(rb, 3)); marcar(ws.cell(rb, 5))

# ---------------------------------------------------------------------------------------------------------------
# 4) Pintura m2 (por skid)
pm = wb.create_sheet("Pintura m2")
pm["A1"] = "CÁLCULO DE SUPERFICIE A GRANALLAR Y PINTAR (m2 por skid)"; pm["A1"].font = Font(bold=True, size=12)
pm["A2"] = "Precio granallado y pintura (USD/m2)"; pm["C2"] = 50; pm["C2"].fill = AZUL
pm["A3"] = "Excluye válvulas (vienen pintadas), bulonería zincada e instrumentos. Sin overspray adicional (skill: USD 50/m2)."
for j, h in enumerate(["Elemento", "Cantidad", "Unid", "m2 / unid", "m2", "Base de cálculo"], 1):
    pm.cell(5, j, h).font = B
OD = {"3": 0.0889, "2": 0.0603}
def fila_c(nombre, r_orig):
    return f"=Cotización!C{nueva(r_orig)}"
PIP = [
    ('Caño 3" (OD 88,9 mm)', fila_c("", 57), "m", f"=PI()*{OD['3']}", "π·OD por metro"),
    ('Caño 2" (OD 60,3 mm)', fila_c("", 64), "m", f"=PI()*{OD['2']}", "π·OD por metro"),
    ('Tee 2"', fila_c("", 70), "un", f"=PI()*{OD['2']}*3*0.064", "π·OD·3·C (C = 64 mm, ASME B16.9)"),
    ('Tee reducción 3" x 2"', fila_c("", 58), "un", f"=PI()*{OD['3']}*2*0.086+PI()*{OD['2']}*0.083", "run 2·C = 172 mm + ramal M = 83 mm"),
    ('Tee reducción 3" x 1 1/2"', f"=Cotización!C{P['TR315']['filas'][0]}", "un", f"=PI()*{OD['3']}*2*0.086+PI()*0.0483*0.076", "run 2·C + ramal M = 76 mm"),
    ('Reducción 3" x 2"', f"=Cotización!C{P['RC32']['filas'][0]}", "un", f"=PI()*({OD['3']}+{OD['2']})/2*0.089", "π·OD medio·H (H = 89 mm)"),
    ('Brida WN 3" #600', fila_c("", 56), "un", 0.07, "cara posterior + canto + cuello (sin cara RF), estimado"),
    ('Brida WN 2" #600', fila_c("", 59), "un", 0.046, "cara posterior + canto + cuello (sin cara RF), estimado"),
    ('Brida 1 1/2" #600', fila_c("", 61), "un", 0.04, "idem, estimado"),
    ('Brida WN 1" #600', f"=Cotización!C{P['BR1']['filas'][0]}", "un", 0.03, "idem, estimado"),
    ("Accesorios menores (sockolets, niples, espaciadores)", 1, "gl", 0.3, "Global estimado"),
]
for i, (n, q, u, m2u, base) in enumerate(PIP):
    r = 6 + i
    pm.cell(r, 1, n); pm.cell(r, 2, q); pm.cell(r, 3, u); pm.cell(r, 4, m2u); pm.cell(r, 5, f"=B{r}*D{r}"); pm.cell(r, 6, base)
rpp = 6 + len(PIP); pm.cell(rpp, 1, "Subtotal piping").font = B; pm.cell(rpp, 5, f"=SUM(E6:E{rpp-1})")
rsk = rpp + 2
pm.cell(rsk, 1, "Estructura (skid)").font = B
pm.cell(rsk + 1, 1, "Perfiles: superficie del plano C-PL-003004 D1 (64,0 m2 por módulo de 3 skids, incluye el % de uniones)")
pm.cell(rsk + 1, 2, 64.0); pm.cell(rsk + 1, 3, "m2 / módulo"); pm.cell(rsk + 1, 4, "=1/3"); pm.cell(rsk + 1, 5, f"=B{rsk+1}*D{rsk+1}")
pm.cell(rsk + 2, 1, "Subtotal estructura").font = B; pm.cell(rsk + 2, 5, f"=E{rsk+1}")
pm.cell(rsk + 3, 1, "TOTAL m2").font = B; pm.cell(rsk + 3, 5, f"=E{rpp}+E{rsk+2}")
pm.column_dimensions["A"].width = 60; pm.column_dimensions["F"].width = 55
for r_, ref in ((R_PINT_P, f"E{rpp}"), (R_PINT_S, f"E{rsk+2}")):
    ws.cell(r_, 14).value = ws.cell(r_, 3).value
    ws.cell(r_, 3).value = f"=ROUNDUP('Pintura m2'!{ref},0)"; ws.cell(r_, 5).value = "='Pintura m2'!C2"; ws.cell(r_, 6).value = f"=C{r_}*E{r_}"
    ws.cell(r_, 13).value = "m2 de la hoja 'Pintura m2' × USD 50 (sin el overspray de 20 %/30 % de la rev. 1)."
    marcar(ws.cell(r_, 3)); marcar(ws.cell(r_, 6))

# ---------------------------------------------------------------------------------------------------------------
# 5) Soldaduras (por skid)
so = wb.create_sheet("Soldaduras")
so["A1"] = "CÓMPUTO DE SOLDADURAS Y MO DE TERCEROS (por skid)"; so["A1"].font = Font(bold=True, size=12)
so["A2"] = "Costo soldadura (USD / pulgada-diámetro)"; so["C2"] = 22; so["C2"].fill = AZUL
so["A3"] = "Mano de obra estructura (USD / kg)"; so["C3"] = 2; so["C3"].fill = AZUL
so["A4"] = "Juntas a tope = (extremos BW de accesorios y bridas + 2 × tramos de caño) / 2. Tramos (azul) estimados del plano de conjunto: cada extremo de accesorio suelda contra caño."
for j, h in enumerate(["Tipo de soldadura", "Diám. (pulg)", "Extremos BW", "Tramos caño", "Cant. soldaduras", "Pulg-diám", "USD"], 1):
    so.cell(6, j, h).font = B
c = lambda k: f"Cotización!C{P[k]['filas'][0]}"
c2 = lambda r_orig: f"Cotización!C{nueva(r_orig)}"
SOL = [
    ('A tope (BW) 3"', 3, f"={c2(56)}+2*{c2(58)}+{c('RC32')}+2*{c('TR315')}", 15),
    ('A tope (BW) 2"', 2, f"={c2(59)}+3*{c2(70)}+{c2(58)}+{c('RC32')}+2*{c2(60)}", 36),
    ('A tope (BW) 1 1/2" (ramal de la tee al niple de la brida)', 1.5, f"={c('TR315')}", 3),
    ('A tope (BW) 1" (bridas del bypass)', 1, f"={c('BR1')}", 2),
]
for i, (n, d, ext, tr) in enumerate(SOL):
    r = 7 + i
    so.cell(r, 1, n); so.cell(r, 2, d); so.cell(r, 3, ext); so.cell(r, 4, tr); so.cell(r, 4).fill = AZUL
    so.cell(r, 5, f"=(C{r}+2*D{r})/2"); so.cell(r, 6, f"=E{r}*B{r}"); so.cell(r, 7, f"=F{r}*$C$2")
OL = [('Sockolet a caño (3/4")', 0.75, f"={c('SO34')}"), ('Sockolet a caño (1/2")', 0.5, f"={c('SO12')}"), ('Sockolet a caño (1")', 1, f"={c2(67)}"),
      ('Socket weld 3/4" (sockolet-niple)', 0.75, f"={c('SO34')}"), ('Socket weld 1/2" (sockolet-niple)', 0.5, f"={c('SO12')}"),
      ('Socket weld 1" (sockolet-niple)', 1, f"={c2(67)}"), ('Socket weld 1 1/2" (niple-brida SW)', 1.5, f"={c2(61)}")]
for i, (n, d, q) in enumerate(OL):
    r = 7 + len(SOL) + i
    so.cell(r, 1, n); so.cell(r, 2, d); so.cell(r, 5, q); so.cell(r, 6, f"=E{r}*B{r}"); so.cell(r, 7, f"=F{r}*$C$2")
rts = 7 + len(SOL) + len(OL)
so.cell(rts, 1, "TOTAL SOLDADURAS PIPING").font = B
for j in (5, 6, 7): so.cell(rts, j, f"=SUM({L(j)}7:{L(j)}{rts-1})")
so.cell(rts + 2, 1, "Mano de obra estructura (kg netos del plano por skid × USD/kg)"); so.cell(rts + 2, 5, f"={R_KGMOD}/3"); so.cell(rts + 2, 6, "kg"); so.cell(rts + 2, 7, f"=E{rts+2}*$C$3")
so.cell(rts + 3, 1, "MO de terceros calculada (soldaduras + estructura)").font = B; so.cell(rts + 3, 7, f"=G{rts}+G{rts+2}")
so.cell(rts + 4, 1, "MO de terceros de la rev. 1 (Ledesma, global)"); so.cell(rts + 4, 7, 7200)
so.cell(rts + 5, 1, "Diferencia (rev. 1 - calculada)"); so.cell(rts + 5, 7, f"=G{rts+4}-G{rts+3}")
so.column_dimensions["A"].width = 60
ws.cell(R_LEDESMA, 14).value = ws.cell(R_LEDESMA, 5).value
ws.cell(R_LEDESMA, 5).value = f"=Soldaduras!G{rts+3}"; marcar(ws.cell(R_LEDESMA, 5))
ws.cell(R_LEDESMA, 13).value = "Calculada en la hoja Soldaduras (USD 22/pulg-diám + USD 2/kg de estructura). La rev. 1 tenía 7.200 global (N)."
R_BW = [7, 8]  # filas de soldaduras a tope de 3" y 2" (van a RX)

# ---------------------------------------------------------------------------------------------------------------
# 6) END
en = wb.create_sheet("END")
en["A1"] = "ENSAYOS NO DESTRUCTIVOS (RX + LP) - Presupuesto ITT 16-11-2026 (en pesos, sin IVA)"; en["A1"].font = Font(bold=True, size=12)
PAR = [("Tipo de cambio (ARS por USD)", 1574.35, "Promedio de noviembre 2026 del oficial BNA venta (conocimiento/costos/dolar_mensual.csv), regla del proyecto"),
       ("Servicio de RX (ARS por jornada, sin IVA)", 670000, "Presupuesto ITT 16-11-2026"),
       ("Servicio de LP (ARS por jornada, sin IVA)", 420000, "Presupuesto ITT 16-11-2026"),
       ("Placa radiográfica corta (ARS)", 10000, "Presupuesto ITT: 2\" a 6\" llevan 3 placas cortas"),
       ("Juntas radiografiadas por jornada de RX", 40, "Rendimiento del skill (confirmado por R. Alvarez para la Lic 69343)"),
       ("Jornadas de LP por skid", 1, "Sockolets, socket weld y juntas chicas"),
       ("Porcentaje de juntas a tope radiografiadas", 1, "La planilla dice 100 % Rx (RT1 del pliego); la clase CA31 de la L0200 pide 30 %: confirmar")]
for i, (n, v, nota) in enumerate(PAR):
    r = 3 + i; en.cell(r, 1, n); en.cell(r, 3, v); en.cell(r, 3).fill = AZUL; en.cell(r, 4, nota)
for j, h in enumerate(["Concepto", "", "Cantidad", "Unid", "ARS unit.", "ARS", "USD"], 1):
    en.cell(11, j, h).font = B
en.cell(12, 1, 'Placas cortas soldaduras 2" y 3" (juntas × % RX × 3)')
en.cell(12, 3, f"=(ROUNDUP(Soldaduras!E{R_BW[0]}*$C$9,0)+ROUNDUP(Soldaduras!E{R_BW[1]}*$C$9,0))*3"); en.cell(12, 4, "placas"); en.cell(12, 5, "=$C$6")
en.cell(13, 1, "Jornadas de RX (juntas a radiografiar / rendimiento)")
en.cell(13, 3, f"=ROUNDUP((ROUNDUP(Soldaduras!E{R_BW[0]}*$C$9,0)+ROUNDUP(Soldaduras!E{R_BW[1]}*$C$9,0))/$C$7,0)"); en.cell(13, 4, "jornada"); en.cell(13, 5, "=$C$4")
en.cell(14, 1, "Jornadas de LP"); en.cell(14, 3, "=$C$8"); en.cell(14, 4, "jornada"); en.cell(14, 5, "=$C$5")
for r in (12, 13, 14):
    en.cell(r, 6, f"=C{r}*E{r}"); en.cell(r, 7, f"=F{r}/$C$3")
en.cell(15, 1, "TOTAL END por skid").font = B; en.cell(15, 6, "=SUM(F12:F14)"); en.cell(15, 7, "=SUM(G12:G14)")
en.column_dimensions["A"].width = 55; en.column_dimensions["D"].width = 60
ws.cell(R_END, 14).value = "='Lista Mats Ing'!G35"
ws.cell(R_END, 5).value = "=END!G15"; marcar(ws.cell(R_END, 5))
ws.cell(R_END, 13).value = "Hoja END (presupuesto ITT 16-11-2026, placas y jornadas). La rev. 1 tomaba 'Lista Mats Ing'!G35 (N)."

# ---------------------------------------------------------------------------------------------------------------
# 7) Verif. espesores (ASME B31.3 304.1.2)
ve = wb.create_sheet("Verif. espesores")
ve["A1"] = "VERIFICACIÓN DE ESPESORES POR PRESIÓN INTERNA (ASME B31.3 304.1.2)"; ve["A1"].font = Font(bold=True, size=12)
VP = [("Presión de diseño (kg/cm2g): máxima del material #600 según la HD (nota 5 del V-cone, ASME B16.5)", 101.25),
      ("Presión de diseño (MPa)", "=B3*0.0980665"), ("Tensión admisible S (MPa), A106 B / A234 WPB", 137.9), ("Factor de junta E (sin costura)", 1),
      ("Factor W", 1), ("Coeficiente Y", 0.4), ("Sobreespesor por corrosión c (mm): clase CA31 de la L0200 (1,6 mm, a confirmar con la hoja de la clase)", 1.6),
      ("Tolerancia de fabricación (fracción)", 0.125)]
for i, (n, v) in enumerate(VP):
    ve.cell(3 + i, 1, n); ve.cell(3 + i, 2, v); ve.cell(3 + i, 2).fill = AZUL
for j, h in enumerate(["Componente", "Diám.", "Schedule", "Ext. (D) mm", "Espesor nominal mm", "Extremo", "Prof. rosca mm", "t presión mm", "Nominal mín. mm", "Resultado"], 1):
    ve.cell(12, j, h).font = B
VT = [('Caño / accesorios 3"', '3"', "Sch 80", 88.9, 7.62, "BW", 0), ('Caño / accesorios 2"', '2"', "Sch 80", 60.3, 5.54, "BW", 0),
      ('Ramal 1 1/2"', '1 1/2"', "Sch 160", 48.3, 7.14, "BW/SW", 0), ('Bypass 1"', '1"', "Sch 160", 33.4, 6.35, "BW", 0),
      ('Niple 3/4" (sockolet - válvula NPT)', '3/4"', "Sch 80", 26.7, 3.91, "NPT", 1.45), ('Niple 3/4" (sockolet - válvula NPT)', '3/4"', "Sch 160", 26.7, 5.56, "NPT", 1.45),
      ('Niple 1/2" (sockolet - válvula NPT)', '1/2"', "Sch 80", 21.3, 3.73, "NPT", 1.45), ('Niple 1/2" (sockolet - válvula NPT)', '1/2"', "Sch 160", 21.3, 4.78, "NPT", 1.45),
      ('Niple 1" (IQ, NPT)', '1"', "Sch 80", 33.4, 4.55, "NPT", 1.77), ('Niple 1" (IQ, NPT)', '1"', "Sch 160", 33.4, 6.35, "NPT", 1.77)]
for i, v in enumerate(VT):
    r = 13 + i
    for j, x in enumerate(v, 1): ve.cell(r, j, x)
    ve.cell(r, 8, f"=$B$4*D{r}/(2*($B$5*$B$6*$B$7+$B$4*$B$8))"); ve.cell(r, 9, f"=(H{r}+$B$9+G{r})/(1-$B$10)")
    ve.cell(r, 10, f'=IF(E{r}>=I{r},"CUMPLE","NO CUMPLE")')
ve.cell(24, 1, "Profundidad de rosca NPT (ASME B1.20.1): 1/2\"-3/4\" 1,45 mm; 1\"-1 1/2\" 1,77 mm. Bridas y válvulas #600 A105: cumplen por rating (B16.5).")
ve.cell(25, 1, "Si un niple roscado Sch 80 NO CUMPLE, va Sch 160 (o XXS): pedirlo así en Compras.")
ve.column_dimensions["A"].width = 45

# ---------------------------------------------------------------------------------------------------------------
# 8) Verificación (para la dirección): todo vinculado a Cotización, con cantidad del plano y controles en 0
vf = wb.create_sheet("Verificación")
vf["A1"] = "VERIFICACIÓN DE MATERIALES, PRECIOS Y PROVEEDORES (por skid, vinculado a la hoja Cotización)"; vf["A1"].font = Font(bold=True, size=12)
vf["A2"] = "Cant. plano = conteo ITT sobre el plano D2 / P&ID H2 con redmarks y la HD D1. Dif. distinta de 0 = revisar."
H = ["Fila", "Descripción", "Cant.", "Cant. plano", "Dif.", "Unid", "USD/un", "Subtotal USD", "Proveedor", "Cotización utilizada", "Aclaración"]
BLOQ = [("1. PIPING (caños, bridas, accesorios, juntas, espárragos, instrumentos en línea)", 56, R_SUB_PIP - 1, R_SUB_PIP),
        ("2. SKID", R_SKID_BAST, R_SKID_BAST + 1, R_SKID_BAST + 2),
        ("3. VÁLVULAS MANUALES (Taval, factor 1)", nueva(81), R_SUB_VAL - 1, R_SUB_VAL),
        ("4. INSTRUMENTAL", nueva(89), R_SUB_INS - 1, R_SUB_INS),
        ("5. MANO DE OBRA DE TERCEROS (hoja Soldaduras)", R_LEDESMA, R_LEDESMA, R_LEDESMA + 1),
        ("6. GRANALLADO Y PINTURA (hoja Pintura m2)", R_PINT_P, R_PINT_S, R_PINT_S + 1),
        ("7. END (hoja END)", R_END, R_END, R_END + 1)]
r = 4; CTRL = []
for tit, a, b, rsub in BLOQ:
    vf.cell(r, 1, tit).font = B; r += 1
    for j, h in enumerate(H, 1):
        x = vf.cell(r, j, h); x.font = B; x.fill = AZUL
    r += 1; r_ini = r
    for fr in range(a, b + 1):
        if ws.cell(fr, 1).value in (None, "") and ws.cell(fr, 3).value in (None, ""):
            continue
        vf.cell(r, 1, fr); vf.cell(r, 2, f'=Cotización!A{fr}&""'); vf.cell(r, 3, f"=Cotización!C{fr}")
        if fr in PLANO:
            vf.cell(r, 4, PLANO[fr]); vf.cell(r, 5, f"=C{r}-D{r}")
        vf.cell(r, 6, f'=Cotización!D{fr}&""'); vf.cell(r, 7, f"=Cotización!E{fr}"); vf.cell(r, 8, f"=C{r}*G{r}")
        vf.cell(r, 9, f'=Cotización!G{fr}&""'); vf.cell(r, 10, f'=Cotización!H{fr}&""'); vf.cell(r, 11, f'=Cotización!M{fr}&""')
        for j in (7, 8): vf.cell(r, j).number_format = NUM
        r += 1
    vf.cell(r, 2, "Subtotal").font = B; vf.cell(r, 8, f"=SUM(H{r_ini}:H{r-1})"); vf.cell(r, 8).number_format = NUM
    vf.cell(r, 9, "Control contra Cotización (debe dar 0):"); vf.cell(r, 11, f"=ROUND(H{r}-Cotización!F{rsub},2)")
    CTRL.append(f"K{r}"); r += 2
vf.cell(r, 2, "TOTAL DE CONTROLES (debe dar 0)").font = B; vf.cell(r, 11, "=" + "+".join(f"ABS({x})" for x in CTRL)); R_CTRL_TOT = r
for w, col in zip((6, 50, 8, 10, 7, 6, 11, 12, 18, 45, 70), "ABCDEFGHIJK"):
    vf.column_dimensions[col].width = w

# formato condicional: amarillo fuerte en los precios a confirmar mientras estén PENDIENTES
for k, cr in CONF_ROW.items():
    regla = FormulaRule(formula=[f"'Precios a confirmar'!$H${cr}=\"\""], fill=AMARILLO)
    for f_ in P[k]["filas"]:
        ws.conditional_formatting.add(f"E{f_}", regla)
    pp.conditional_formatting.add(f"{L(cADO)}{PP_ROW[k]}", FormulaRule(formula=[f"'Precios a confirmar'!$H${cr}=\"\""], fill=AMARILLO))

# orden de hojas: las nuevas después de Cotización
orden = ["Pie de Venta", "Cotización", "Verificación", "Precios a confirmar", "Precios proveedores", "Pintura m2", "Soldaduras", "END",
         "Verif. espesores", "Instrumentos", "Lista Mats Ing", "Lista Soportes Ing", "Lista de Skid Ing"]
wb._sheets = [wb[n] for n in orden]
wb.save(SALIDA)
print("Guardado", SALIDA, "| a confirmar:", len(conf_keys), "| control total en Verificación!K%d" % R_CTRL_TOT)
