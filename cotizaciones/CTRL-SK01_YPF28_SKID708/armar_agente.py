"""Arma cotizacion_agente.json de CTRL-SK01 (recotización a mano del agente)."""
import json
import sys
from pathlib import Path

C = Path(sys.argv[1])
base = json.load(open(C / "cotizacion.json", encoding="utf-8"))
T72 = "TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE"
T78 = "TAVAL/78- LIC66577 SKID CONC. L. CAMP"
REN = "conocimiento/precios/lista_renar_2025-12.csv (fuentes_originales/renar_lista_2025-12.xlsx)"
COMPLEMET = f"{T72}/5.Proveedores 3ros/Cot Complemet para Narambue 07072026.pdf (cotización 275397)"
MS = f"{T78}/5.Proveedores 3ros/MS Juntas COTIZACION_N§_049323.pdf"
VALV78 = f"{T78}/4.Armado de la Oferta Comercial/Valvulas/Valvulas.xlsx (lista Taval × 0,52)"
STOCK = "conocimiento/precios/stock_2024-11.csv (precio maestro)"
TEC13 = "TECPETROL/13- TRAMPAS .../4.Armado de la Oferta Comercial/Cotización Tecpetrol Trampas ... REV 1.xlsx"


def f(tipo, precio, prov, origen, fecha, coincide, dif=""):
    d = {"tipo": tipo, "precio": round(precio, 2), "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        d["diferencia"] = dif
    return d


M = [
    ("1", 'Caño s/c extr. SCH XS (323,8 x 12,70) 12"', 2.3, "m", [f("lista", 217.23, "Renard cód. 1201", REN, "2025-12-26", "igual")]),
    ("1b", "Compra extra pos 1: 2 tubos de ~11 m para 6 equipos (22 − 13,8 m)", 1.37, "m", [f("lista", 217.23, "Renard cód. 1201", REN, "2025-12-26", "igual", "largo comercial 10,5–11,8 m (lista Renard); sobrante a stock")]),
    ("2", 'Caño c/c extr. STD (406,4 x 9,52) 16"', 1.7, "m", [f("lista", 248.98, "Renard cód. 1212 (tubo s/c 406,4 x 9,52)", REN, "2025-12-26", "similar", "sin costura en lugar de con costura (superior)")]),
    ("2b", "Compra extra pos 2: 1 tubo de ~11 m para 6 equipos (11 − 10,2 m)", 0.13, "m", [f("lista", 248.98, "Renard cód. 1212", REN, "2025-12-26", "similar", "s/c en lugar de c/c")]),
    ("3", 'Tee normal 12" SCH XS A234 WPB', 3, "un", [f("est", 1761.9, "Cintolo cot. 33764: tee 12\" SCH 80 USD 2.425,08 × 12,70/17,48 (espesor XS / sch 80)", "TAVAL/69- Lic 64673 .../5.Proveedores 3ros/Cot Cíntolo 33764.pdf", "2026-07-16", "similar", "sch 80 escalado a XS por espesor"), f("lista", 962.15, "Renard cód. 3471 tee 12\" STD", REN, "2025-12-26", "similar", "STD en lugar de XS")]),
    ("4", 'Tee de reducción 16"x12" SCH STD x XS', 3, "un", [f("lista", 2802.34, "Renard cód. 3547 tee red. 16x12 STD", REN, "2025-12-26", "similar", "rama STD en lugar de XS")]),
    ("5", 'Brida WN RF 300 LB SCH XS 12"', 18, "un", [f("cot", 218.49, "Complemet (Grupo Provemet) cot. 275397", COMPLEMET, "2026-07-06", "igual"), f("lista", 355.68, "Renard cód. 11984 (sch 40)", REN, "2025-12-26", "similar", "sch 40")]),
    ("6", 'Brida WN RF 300 LB 16" (STD)', 2, "un", [f("est", 669.2, "Renard SO 16\" S300 560,29 × (WN/SO 12\" S300 = 355,68/297,79)", REN, "2025-12-26", "similar", "estimado de la lista Renard (no hay WN 16\" #300)")]),
    ("7", 'Brida ciega RF 300 LB 12"', 6, "un", [f("cot", 257.65, "Complemet cot. 275397", COMPLEMET, "2026-07-06", "igual"), f("lista", 426.44, "Renard cód. 8260", REN, "2025-12-26", "igual")]),
    ("8", 'Brida ciega RF 300 LB 16"', 2, "un", [f("est", 735.42, "Renard BL 14\" S300 565,71 × (BL 16\"/14\" S150 = 392,34/301,8)", REN, "2025-12-26", "similar", "estimado de la lista Renard")]),
    ("9", 'Brida SW RF 300 LB SCH 80 1 1/2"', 3, "un", [f("cot", 14.88, "Complemet cot. 275397", COMPLEMET, "2026-07-06", "igual")]),
    ("10", 'Espárrago c/2 tuercas 1 1/4" x 207 mm B7/2H zincado', 40, "un", [f("ant", 12.4, "planilla ITT TECPETROL/13 (1 1/8 x 170 c/2 tuercas zinc 12,00; 1 3/8 x 255 13,00), interpolado", TEC13, "2026-06-26", "similar", "interpolado por diámetro y largo")]),
    ("11", 'Espárrago c/2 tuercas 1 1/8" x 186 mm B7/2H zincado', 288, "un", [f("ant", 12.0, "planilla ITT TECPETROL/13: 1 1/8 x 170 mm c/2 tuercas zinc", TEC13, "2026-06-26", "similar", "170 mm en lugar de 186 mm")]),
    ("12", 'Junta espiralada RF 4,5 mm 300 LB 1 1/2"', 3, "un", [f("ant", 6.0, "MS (planilla Pampa 7, JUN-02769)", "PAMPA ENERGIA/7 .../Cot Skid Manifolds Colectores RDA Contrato Marco (2da RDA).xlsx", "2026-08-14", "similar", "2\" en lugar de 1 1/2\"")]),
    ("13", 'Junta espiralada RF 4,5 mm 300 LB 12"', 18, "un", [f("cot", 9.31, "MS Juntas cot. 49.323 (ESP SW AC 316LFG 12\" 300)", MS, "2026-08-14", "igual")]),
    ("14", 'Junta espiralada RF 4,5 mm 300 LB 16"', 2, "un", [f("est", 14.0, "MS 49.323: 10\" 7,14 y 12\" 9,31 → 16\" por diámetro", MS, "2026-08-14", "similar", "extrapolado de 10\" y 12\"")]),
    ("15", 'Niple s/c NPT SCH 80 L=100 mm 1 1/2"', 3, "un", [f("stock", 5.6, "Stock ITT ACI040FN1ICK100", STOCK, "2024-11-01", "igual")]),
    ("16", 'Niple s/c NPT SCH 80 L=100 mm 1/2"', 1, "un", [f("stock", 4.76, "Stock ITT ACI015FN1ICK100", STOCK, "2024-11-01", "igual")]),
    ("17", 'Niple s/c NPT SCH 80 L=100 mm 3/4"', 1, "un", [f("stock", 5.59, "Stock ITT ACI020KN1ICK100 (sch 160)", STOCK, "2024-11-01", "similar", "sch 160 en lugar de 80")]),
    ("18", 'Niple s/c NPT SCH 160 L=100 mm 3/4"', 3, "un", [f("stock", 5.59, "Stock ITT ACI020KN1ICK100", STOCK, "2024-11-01", "igual")]),
    ("19", 'Tapón NPT cab. hexag. A105 1/2"', 1, "un", [f("cot", 1.38, "Provemet (AFO-00848)", "catálogo de materiales AFO-00848", "2025-08-27", "similar", "serie sin dato")]),
    ("20", 'Tapón NPT cab. hexag. A105 3/4"', 2, "un", [f("ant", 2.3, "planilla ITT 2026-02 (catálogo)", "catálogo de materiales", "2026-02-20", "similar", "serie sin dato")]),
    ("21", 'Sockolet SW 3000 LB 12"x1 1/2"', 3, "un", [f("est", 20.0, "sockolet 1/2\" S3000 USD 10 (TECHINT/12) escalado por salida", "catálogo AFO-02393 / AFO-03330", "2025-12-23", "similar", "salida 1/2\" escalada a 1 1/2\"")]),
    ("22", 'Sockolet SW 3000 LB 12"x3/4"', 3, "un", [f("est", 12.0, "sockolet 1/2\" S3000 USD 10 escalado", "catálogo AFO-02393", "2025-12-23", "similar", "salida 1/2\" escalada a 3/4\"")]),
    ("23", 'Sockolet SW 3000 LB 16"x3/4"', 1, "un", [f("est", 12.0, "sockolet 1/2\" S3000 USD 10 escalado", "catálogo AFO-02393", "2025-12-23", "similar", "salida 1/2\" escalada a 3/4\"")]),
    ("24", 'Sockolet SW 3000 LB 16"x1/2"', 1, "un", [f("ant", 10.0, "planilla ITT TECHINT/12 (sockolet 1/2\" 3000 A105)", "catálogo AFO-02393", "2025-12-23", "igual")]),
    ("25", 'Válvula esférica NPT WOG 2000 PT palanca 1/2" (Taval TCH2N)', 1, "un", [f("ant", 35.88, "Taval lista 69 × 0,52", VALV78, "2026-08-19", "igual")]),
    ("26", 'Válvula esférica NPT WOG 2000 PT palanca 3/4" (Taval TCH2N)', 4, "un", [f("ant", 39.0, "Taval lista 75 × 0,52", VALV78, "2026-08-19", "igual")]),
    ("27", 'Válvula retención clapeta 12" FLG RF 300 LB WCB (Taval)', 3, "un", [f("est", 3270.0, "Taval: 10\" #300 lista 4.500 × 0,52 = 2.340 (TAVAL/78) × 1,35 por diámetro = 3.159; 12\" #600 4.834 (Sacde 12, 12-2025) × 0,70 por serie = 3.384; promedio", VALV78, "2026-08-19", "similar", "sin precio Taval 12\" #300 fuera del proyecto: pedir lista")]),
    ("28", 'Válvula globo NPT 800 LB volante 1/2" (Taval GAB8N)', 1, "un", [f("ant", 35.1, "Taval lista 67,5 × 0,52", VALV78, "2026-08-19", "igual")]),
    ("29", 'Válvula globo NPT 800 LB volante 3/4" (Taval GAB8N)', 1, "un", [f("ant", 40.56, "Taval lista 78 × 0,52", VALV78, "2026-08-19", "igual")]),
    ("30", 'Válvula esférica 12" FLG RF 300 LB PT volante y caja reductora (Taval TCC3R)', 3, "un", [f("est", 5640.0, "Taval: 10\" #300 lista 7.115 × 0,52 = 3.700 (TAVAL/78) × 1,50 por diámetro = 5.550; 12\" #600 PT 7.634 (Sacde 12, 12-2025) × 0,75 por serie = 5.725; promedio", VALV78, "2026-08-19", "similar", "sin precio Taval 12\" #300 fuera del proyecto: pedir lista")]),
    ("31", "Bastidor del skid (perfilería UPN, A-36)", 850, "kg", [f("cot", 1.9, "acero por kg (hierro ángulo 3x1/4 1,72 + 10% recortes)", "conocimiento/precios/acero_por_kg.csv (precios_varios_acero_2026-02)", "2026-02-10", "similar", "ángulo en lugar de UPN")]),
]

items = []
for pos, desc, q, u, fu in M:
    it = {"id": f"M{pos}", "pos": pos, "grupo": "material", "descripcion": desc, "especificacion": "", "cantidad": q, "unidad": u, "fuentes": fu}
    if pos in ("25", "26", "27", "28", "29", "30"):
        it["taval"] = True
    items.append(it)

SOLD = ('Juntas como el skid gemelo TAVAL/72 (tabla "Costuras": 21 del Ø de entrada y 7 del colector): 21 × 12" XS × 1,334 = 336,17; '
        '7 × 16" STD × 1,0 = 112,00; sockolets 3 × 1 1/2" × 1,75 = 7,88, 4 × 3/4" × 1,75 = 5,25, 1 × 1/2" × 1,75 = 0,88; '
        'SW 6 × 1 1/2" = 9,00, 4 × 3/4" = 3,00, 1 × 1/2" = 0,50 → 474,67 pulg-eq, todo de taller')
items += [
    {"id": "S01", "pos": "MO", "grupo": "mo", "descripcion": "Soldadura de piping en planta (28 juntas a tope + SW y olets)", "especificacion": SOLD, "cantidad": 474.67, "unidad": "pulg",
     "fuentes": [f("ant", 16.0, "criterio planillas ITT 2026 (TAVAL/43, TAVAL/40, TECPETROL/9 16,5)", "conocimiento/costos/tarifas.csv fila 3", "2026-02-15", "igual"),
                 f("cot", 16.0, "Ledesma 200276 (980\" sch 80 + 1.300 kg de skid = 19.600) ≈ 16/pulg", "ENDRESS HAUSER/33 .../5.Proveedores 3ros/E Ledesma Presupuesto ITT N° 200276", "2026-06-02", "similar", "pulgada nominal")]},
    {"id": "S05", "pos": "EST", "grupo": "mo", "descripcion": "Fabricación de la estructura (850 kg)", "especificacion": "850 kg × USD 4/kg", "cantidad": 850, "unidad": "kg",
     "fuentes": [f("ant", 4.0, "planilla ITT TECPETROL/9 REV C (UPN 140 384 kg × 4 = 1.536)", "TECPETROL/9 .../REV C/ESTRUCTURA DE COSTOS- LM de Manifold S600 CM - PC0-C REV.1 OS.xlsx, fila 239", "2026-01-13", "similar"),
                 f("cot", 4.5, "J. C. Quesada JQ-020-2026", "TAVAL/58 .../Cotizacion JQ-020-2026.pdf", "2026-05-06", "similar")]},
    {"id": "S04", "pos": "RX", "grupo": "servicio", "descripcion": "Radiografía 100% de las juntas a tope y LP en SW y olets",
     "especificacion": "21 juntas 12\" × 6 placas chicas = 126 × 6,50; 7 juntas 16\" × 3 placas grandes = 21 × 8,00; 23 servicios RX para 6 equipos (40 placas c/u) = 3,83 × 408; LP 4 servicios / 6 = 0,67 × 294",
     "cantidad": 1, "unidad": "gl", "fuentes": [f("cot", 2747.0, "DB NDT (lista en planillas Pampa 7, 08-2026)", "conocimiento/costos/tarifas.csv filas 46–49", "2026-08-14", "igual"),
                                                 f("cot", 4514.0, "Antonelli 11-2025 (15/20 por placa, 490 por servicio)", "fuentes_originales/antonelli_end_2025-11.pdf", "2025-11-03", "igual")]},
    {"id": "S02", "pos": "PIN", "grupo": "servicio", "descripcion": "Granallado y pintura", "especificacion": "piping 30,7 m² (válvulas 12\" 9,0; bridas y ciegas 11,4; tees 4,8; caños 4,5; menores 1,0) + bastidor 850 kg × 24 m²/t (UPN 200–240) = 20,4 m² → 51,1 m²",
     "cantidad": 51.1, "unidad": "m2", "fuentes": [f("ant", 50.0, "criterio ITT USD 50/m² con materiales (PIN-00491)", "PAMPA ENERGIA/7 .../4.Armado de la Oferta Comercial", "2026-08-14", "similar", "esquema según pliego YPF a confirmar")]},
    {"id": "S12H", "pos": "HH", "grupo": "mo", "descripcion": "Horas de ingeniería", "especificacion": "150 h para la serie de 6 (isométricos, planos de fabricación, documentación) = 25 h por skid", "cantidad": 25, "unidad": "h",
     "fuentes": [f("est", 15.0, "tarifa hora ITT de las planillas 2026", "conocimiento/costos/horas_por_equipo.csv", "2026-02-10", "sin_ref")]},
    {"id": "S13C", "pos": "CAL", "grupo": "mo", "descripcion": "Horas de calidad y dossier", "especificacion": "15 h por skid (inspección, PH, dossier) + parte fija repartida", "cantidad": 15, "unidad": "h",
     "fuentes": [f("est", 15.0, "tarifa hora ITT de las planillas 2026", "conocimiento/costos/horas_por_equipo.csv", "2026-02-10", "sin_ref")]},
    {"id": "S13A", "pos": "ARM", "grupo": "mo", "descripcion": "Montaje en planta (armado, movimientos, prueba hidráulica)",
     "especificacion": "movimientos 16 h + presentación de spools 48 + válvulas y ciegas 24 + PH 16 + desarme para pintura 16 + armado final 32 + bastidor y nivelación 16 + despacho 8 = 176 h (escala de TECPETROL/9: 256,5 h para 52 juntas)",
     "cantidad": 176, "unidad": "h", "fuentes": [f("est", 13.0, "tarifa hora planta ITT de las planillas 2026", "conocimiento/costos/horas_por_equipo.csv", "2026-02-10", "sin_ref")]},
    {"id": "S20", "pos": "SEG", "grupo": "servicio", "descripcion": "Seguro de caución", "especificacion": "póliza 10% del precio de venta (~USD 150.000) a ~3% anual", "cantidad": 1, "unidad": "gl",
     "fuentes": [f("est", 450.0, "criterio del agente (pliego no disponible)", "—", "2026-10-28", "sin_ref")]},
]
base["items"] = items
base["codigo"] = "CTRL-SK01"
base["nota_precotizacion"] = "Recotización a mano del agente (caso de control), sin precios de YPF/28 ni de COT26-0330."
json.dump(base, open(C / "cotizacion_agente.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(items))
