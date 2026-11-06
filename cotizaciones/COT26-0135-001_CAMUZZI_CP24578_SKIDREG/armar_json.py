"""Arma cotizacion.json y oferta.json del skid de regulación (CP 24578 ítem 2) desde cotizacion_auto.json (precotizar.py)
+ correcciones revisadas a mano, cada una con su fuente. Correr: python cotizaciones/COT26-0135-001_CAMUZZI_CP24578_SKIDREG/armar_json.py

Este archivo es la ÚNICA fuente de las correcciones: correrlo de nuevo da siempre el mismo cotizacion.json. Hasta el 30-10-2026
las correcciones de las auditorías de compatibilidad se habían hecho directo sobre cotizacion.json y correr este script las
deshacía (error anotado en la bitácora, revisión completa del 30-10-2026): ahora están todas acá."""
import json
import math
from pathlib import Path

C = Path(__file__).resolve().parent
auto = json.load(open(C / "cotizacion_auto.json", encoding="utf-8"))
base = json.load(open(C / "cotizacion.json", encoding="utf-8"))
items = {i["pos"]: i for i in auto["items"]}
HOY = "2026-10-30"  # fecha de las decisiones de precio (la referencia del ajuste va aparte)
TC_OCT = 1543.23  # dólar oficial BNA venta, promedio de 10-2026 (conocimiento/costos/dolar_mensual.csv)
RENARD = "fuentes_originales/renar_lista_2025-12.xlsx"
TORMENE = "fuentes_originales/ofertas_texto/ALONZO RED/2 - ERP B° Pilara/5.Proveedores 3ros/OFERTA TA7785A-ITT-REG TA956-NATURGY.pdf.txt"
CAM14 = ("fuentes_originales/ofertas_texto/CAMUZZI/14_#5067 - (CGP 6910  CGS 6911) - Estaciones de medición y regulación/"
         "4.Armado de la Oferta Comercial/6910/Planilla de Costo- Salto de Regulación_6910 rev 2.xlsx.txt")
LACH = "fuentes_originales/ofertas_texto/TAVAL/69- Lic 64673 COLECT-SKIDS-PUENTE MED - UTE LACH/5.Proveedores 3ros/"
TECHINT12 = "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado"
LISTADO = "listado SCE-IN-501-0015 rev 1 (10-02-2026, pedido/789-2- LISTADO DE MARCAS Y PROVEEDORES CAMUZZI.pdf)"


def fuente(tipo, precio, prov, origen, fecha, coincide="similar", dif="", **extra):
    f = {"tipo": tipo, "precio": precio, "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        f["diferencia"] = dif
    f.update(extra)
    return f


def SIN(motivo, fecha=HOY):
    """Sin referencia válida: no se adivina (P4 ter, Matías 28-10-2026). Va a la lista de Compras."""
    return fuente("est", 0, "SIN PRECIO: pedir cotización", "—", fecha, "sin_ref", motivo)


def descartada(f, motivo):
    f = dict(f)
    f["coincide"] = "descartada"
    f["diferencia"] = f"descartada ({motivo})" + (" · antes: " + f["diferencia"] if f.get("diferencia") else "")
    return f


def poner(pos, fuentes, **extra):
    items[pos]["fuentes"] = fuentes
    items[pos].update(extra)


for i in items.values():
    i.pop("taval", None)  # Taval no está en el listado SCE-IN-501-0015: nada lleva el factor de válvulas Taval (Matías, 29-10-2026)

# ---------------------------------------------------------------- materiales del plano
F_TOR1 = fuente("cot", 9545.0, "Tormene Americana · oferta TA7785A pos. 1 (TA956-FC+SSV monitor)", TORMENE, "2026-06-16", "similar",
                "DN3\" #300 (pedido #150), con bloqueo OPSO e indicador de posición; condiciones P1 25/7 bar, P2 1,5 bar, Q 8.000 Sm3/h")
F_TOR2 = fuente("cot", 6073.0, "Tormene Americana · oferta TA7785A pos. 2 (TA956-DFO activo silenciado)", TORMENE, "2026-06-16", "similar",
                "DN3\" #300 (pedido #150); silenciador interno")
poner("1", [SIN("la única oferta de reguladoras de la base (Tormene TA956 #300 con OPSO, ERP Pilará 16-06-2026) es de otra serie: pedir cotización "
                "#150 sin OPSO de un modelo homologado en el listado SCE-IN-501-0015 (Tormene TA956 FC, Fiorentini, Fisher…)"),
            descartada(F_TOR1, "tercera auditoría 30-10-2026: otra serie (#300 por #150)")])
poner("2", [SIN("la única oferta de reguladoras de la base (Tormene TA956 DFO #300, ERP Pilará 16-06-2026) es de otra serie: pedir cotización #150 "
                "de un modelo homologado en el listado SCE-IN-501-0015"),
            descartada(F_TOR2, "tercera auditoría 30-10-2026: otra serie (#300 por #150)"),
            fuente("ant", 4060.0, "Planilla Sacde/15 (VAL-03275: válvula reguladora 3\" RF set 0,03 kg/cm2)",
                   "fuentes_originales/ofertas_texto/Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL", "2026-02-20", "descartada",
                   "descartada: otra aplicación (baja presión, sin serie) · solo referencia de orden de magnitud")])
# Esféricas: precio de referencia Taval de la misma especificación; se compra marca del listado (Matías, 29-10-2026)
for p in ("3", "4"):
    f = items[p]["fuentes"][0]
    f["tipo"] = "est"  # auditoría 30-10-2026: marca fuera del listado y sin el ensayo que pide la ET: es estimado, no lista de la marca comprable
    f["coincide"] = "similar"
    f["diferencia"] = ("precio de referencia Taval (marca fuera del listado; lista de precios, sin el ensayo SCE-RE-308-0001 con certificado firmado "
                       "por la inspección que pide la ET 5.6.2): comprar Esferomatic, Worcester, Valvtronic, Pentair, Indave, Wenlen, Beta o Valmec")
# Accesorios para soldar: el listado SCE-IN-501-0015 (hoja 2) admite solo CURVO SOLD (Cintolo); auditoría 30-10-2026: se toma la lista de
# Cintolo 29.1 (vigencia 17-02-2025) donde tiene la pieza, y Renard (otra marca) queda como alternativa o, sin Cintolo, como estimado
CIN = "fuentes_originales/listas_vendedor/2026-10-28/cintolo_lista_29-1_2025-02-17.xlsx"
poner("9", [fuente("lista", 129.55, "Cintolo Hnos. (Curvo Sold) lista 29.1 art. 6046: TE NORMAL 6\" STANDARD ASME B16.9 A234-WPB", CIN + " · art. 6046",
                   "2025-02-17", "similar", "A234 WPB (el plano pide ASTM A-105, que no es material de te a tope B16.9): consulta R83"),
            fuente("lista", 104.61, "Renard (cód. 3468) · ABW-00418", RENARD + " · código 3468", "2025-12-26", "similar", "marca fuera del listado; A234 WPB", codigo="ABW-00418")])
poner("10", [fuente("lista", 351.5, "Cintolo Hnos. (Curvo Sold) lista 29.1 art. 7086: TE RED. 8\" X 6\" STANDARD ASME B16.9 A234-WPB", CIN + " · art. 7086",
                    "2025-02-17", "igual"),
             fuente("lista", 283.84, "Renard (cód. 3533) · ABW-00423", RENARD + " · código 3533", "2025-12-26", "similar", "marca fuera del listado", codigo="ABW-00423")])
poner("11", [fuente("lista", 69.19, "Cintolo Hnos. (Curvo Sold) lista 29.1 art. 8161: RED. CON. 6\" X 3\" STANDARD ASME B16.9 A234-WPB", CIN + " · art. 8161",
                    "2025-02-17", "similar", "A234 WPB (el plano dice S/ Esp. CAMUZZI)"),
             fuente("lista", 55.88, "Renard (cód. 3064) · ABW-00232", RENARD + " · código 3064", "2025-12-26", "similar", "marca fuera del listado", codigo="ABW-00232")])
for p in ("12", "13"):  # Cintolo no lista casquetes: el de Renard es de marca no identificada → estimado
    f = items[p]["fuentes"][0]
    f["tipo"] = "est"
    f["coincide"] = "similar"
    f["diferencia"] = "marca no identificada (el listado admite solo Curvo Sold y la lista 29.1 de Cintolo no tiene casquetes): pedir a Cintolo"
# Pos 14: el plano pide la cupla en ASTM A-106 (norma de caño, no de cupla forjada): consulta al cliente (requisito R78)
poner("14", [SIN("el plano pide la cupla en ASTM A-106 (norma de caño; las cuplas B16.11 son forjadas A-105): consulta al cliente R78. "
                 "Compras: cupla 1/2\" NPT S3000 + esférica 1/2\" NPT S3000 de marca del listado"),
             descartada(items["14"]["fuentes"][0], "revisión de compatibilidades 30-10-2026: válvula A105, el plano pide A-106")])
# Pos 15 y 16: misma pieza en la planilla de costo del salto de regulación de Camuzzi ERP Caseros (CAMUZZI/14, 15-03-2022)
poner("15", [fuente("est", 312.0, "Planilla de costo ITT, salto de regulación Camuzzi ERP Caseros (CAMUZZI/14, CGP 6910, rev 2, renglón 18: "
                    "TOMA MULTIPORT Ø 1/2\" - 3000 LB, 312 USD)", CAM14, "2022-03-15", "similar",
                    "misma pieza (toma multiport 1/2\" serie 3000; la planilla no dice el material) en un salto de Camuzzi; precio de 2022 (período con cepo): pedir cotización a ABAC"),
             descartada(fuente("ant", 170.0, "Manifold ABAC de 3 vías M1-C-T AISI 304/316 (OTR-02980, planilla TAVAL/40)",
                               "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt",
                               "2026-01-15", "similar", "manifold de 3 vías"), "auditoría 30-10-2026: manifold serie 2000, el plano pide 3000")])
poner("16", [fuente("est", 465.0, "Planilla de costo ITT, salto de regulación Camuzzi ERP Caseros (CAMUZZI/14, CGP 6910, rev 2, renglón 48: "
                    "VÁLVULA DE ALIVIO (TIPO S70 / H200) Ø 1/2\" - 3000 LB, 465 USD)", CAM14, "2022-03-15", "similar",
                    "tipo S70/H200 (pedido S-71), mismo Ø y serie; precio de 2022 (período con cepo): pedir cotización a Farinola, Favra o Aerre (listado)")])
# Pos 17: la cupla con tapón lleva el tapón (antes solo la cupla) y el código de Renard era el de la BSPT (5281); la NPT es 5292
poner("17", [fuente("lista", round(2.71 + 1.90, 2), "Renard · cupla 1/2\" NPT S3000 ASTM A105 (cód. 5292) USD 2,71 + tapón 1/2\" NPT S3000 ASTM A105 "
                    "(cód. 5979) USD 1,90 · AFO-00715", RENARD + " · códigos 5292 y 5979", "2025-12-26", "similar",
                    "cupla + tapón NPT S3000 A105; el plano pide SW/NPT (revisión 30-10-2026: faltaba el tapón y el código citado era el de la BSPT)",
                    codigo="AFO-00715")])
# Pos 18: la única termovaina 3/4" NPT de la base es la del stock de ITT en AISI 316L, que la norma no admite por 316 (compatibilidad.py): SIN PRECIO
poner("18", [SIN("termovaina 3/4\" NPT AISI 316: la base solo tiene la del stock de ITT en 316L (2 un, cód. TC6020N5NA2T1DO), que no reemplaza a 316; "
                 "pedir cotización a Weisz, Wika, ABAC o Casucci (listado)"),
             descartada(fuente("est", 70.4, "Stock ITT (cód. TC6020N5NA2T1DO, 2 un): TERMOVAINA ¾ NPT L: 6\" CONEX ½ NPT INS 6mm EXT 1\" AISI 316L · INS-01587",
                               "fuentes_originales/stock_valorizado_2024-11.xlsx · código TC6020N5NA2T1DO", "2024-11-01", "similar", "AISI 316L (pedido AISI 316)",
                               codigo="INS-01587"), "revisión 30-10-2026: 316L no reemplaza a 316 según compatibilidad.py")])
poner("19", [fuente("est", 316.4, "Weisz presupuesto 30.0.10.027.203 ítem 01 (16-07-2026): manómetro 4100N 4\" clase 1, caja AISI 304 IP65, bourdon AISI 316 + limitador 080M + "
                    "bloqueo y purga 070 AISI 316 + certificado de calibración", LACH + "Oferta Weisz de ventas_30.0.10.027.203.pdf.txt", "2026-07-16", "similar",
                    "estimado (auditoría 30-10-2026): sin glicerina, con limitador que no se pide, y bloqueo y purga Weisz AISI 316 en lugar del manifold de 3 vías "
                    "A-105 zincado serie 3000 (ET 5.8; Weisz no figura para bloqueo y purga): pedir manómetro Weisz/Wika con glicerina + manifold ABAC VA 350 o Casucci"),
             fuente("est", 136.0 + 65.0, "Planilla de costo ITT, salto Camuzzi ERP Caseros (CAMUZZI/14, renglones 51 manifold 3 vías zincado 136 y 49 manómetro según la ET, 65)",
                    CAM14, "2022-03-15", "igual", "misma especificación, precio de 2022"),
             fuente("ant", 230.0, "Bloqueo y purga ABAC 80 (VAL-03162, planilla TAVAL/55) + manómetro Ø100 150 (INS-02671, Weisz o similar, TAVAL/43)",
                    "fuentes_originales/ofertas_texto/TAVAL/43- YPF- CM PUENTES DE PRODUCCION", "2026-04-22", "similar",
                    "manómetro según ET 5.7.1 (glicerina, clase 1, certificado de calibración) montado con manifold de 3 vías A-105 zincado serie 3000 (ET 5.8): "
                    "VAL-03162 es un manifold de transmisor (PIT) de Tecpetrol y INS-02671 no demuestra la ET 5.7.1: solo referencia")])
poner("20", [fuente("cot", round(330 * 17.4 / 13.4 * 1.10, 2), "Grupo Provemet cot. 236623: UPN 120 a USD 17,40/m (13,40 kg/m) = 1,30 USD/kg +10% recortes, "
                    "× 330 kg estimados (medidos del plano: 3.700 × 1.630 mm, perimetral, 4 travesaños, soportes y cáncamos)",
                    "fuentes_originales/listas_vendedor/2026-10-28/provemet_cotizacion_236623_perfiles_2025-07-01.pdf", "2025-07-01", "similar",
                    "kilos estimados del plano; confirmar con el típico SCE-RE-110-0006 (consulta R33)")],
     especificacion="Skid 3.700 × 1.630 mm, UPN 120 perimetral y travesaños, soportes de cañería, 4 cáncamos y oreja de PAT (330 kg estimados)")
# Caños: Renard sin costura A53/A106/API 5L B (auditorías 30-10-2026: la lista de Renard dice A53A o A53/135 sin grado en los con costura)
CAN = {"21": (25.08, "1153", "CAN-01484", "Tubo s/costura 88,9 x 5,49 mm A53/A106/API 5L B", "10,50 a 12,50 m",
              (18.99, "1007", "CAN-01485", "la lista de Renard dice A53A (grado A), el plano pide A-53 Gr B", "auditoría 30-10-2026")),
       "22": (60.51, "1173", "CAN-01510", "Tubo s/costura 168,3 x 7,11 mm A53/A106/API 5L B", "10,50 a 14,50 m",
              (50.6, "1056", "CAN-01511", "la lista de Renard dice A53/135 sin grado; el plano pide A-53 Gr B", "segunda auditoría 30-10-2026")),
       "24": (91.01, "1181", "CAN-01521", "Tubo s/costura 219,1 x 8,18 mm A53/A106/API 5L B", "10,50 a 14,50 m",
              (72.64, "1062", "CAN-01522", "la lista de Renard dice A53/135 sin grado; el plano pide A-53 Gr B", "segunda auditoría 30-10-2026"))}
for p, (pr, cod, cc, txt, largo, (pr2, cod2, cc2, mot, quien)) in CAN.items():
    f1 = fuente("lista", pr, f"Renard (cód. {cod}) · {cc}", f"{RENARD} · código {cod}", "2025-12-26", "similar",
                f"{txt} (sin costura, triple certificación: cumple A53 Gr B); largo {largo}", codigo=cc)
    f2 = descartada(fuente("lista", pr2, f"Renard (cód. {cod2}) · {cc2}", f"{RENARD} · código {cod2}", "2025-12-26", "similar",
                           "costura: con costura (no pedido)", codigo=cc2), f"{quien}: {mot}")
    items[p]["fuentes"] = [f1, f2]
    items[p + "b"]["fuentes"] = [dict(f1), dict(f2)]
F23 = fuente("lista", 90.7, "Renard (cód. 1174) · Tubo s/costura 168,3 x 10,97 mm A53/A106/API 5L B · CAN-01512", RENARD + " · código 1174", "2025-12-26", "similar",
             "caño A106 Gr B sch XS (el plano pide A-53 Gr B sch 80: A106 lo reemplaza, mismo espesor en 6\")", codigo="CAN-01512")
items["23"]["fuentes"] = [F23]
items["23b"]["fuentes"] = [dict(F23)]  # segunda auditoría 30-10-2026: la 23b tenía otra pieza (CAN-02603, sin material)
# Precios Provemet del 29-10-2026 (revisión del 05-11-2026): mismo caño sin costura triple certificación; Renard queda de alternativa
PROVEMET_C = "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf"
PV = {"22": (49.48, 1, "TUBO S/C ASTM A53/A106/API5L B 6'' SCH 40 Ø 168,3 X 7,11 mm x 12 / 13,7 mts BW", "CAN-01510"),
      "23": (74.52, 10, "TUBO S/C ASTM A53/A106/API5L B 6'' SCH 80 Ø 168,3 X 10,97 mm x 12 / 13,7 mts BW", "CAN-01512"),
      "24": (74.51, 2, "TUBO S/C ASTM A53/A106/API5L B 8'' SCH 40 Ø 219,1 X 8,18 mm x 12 / 13,7 mts BW", "CAN-01521")}
for p_, (pr, it, txt, cc) in PV.items():
    fp = fuente("cot", pr, f"Grupo Provemet cot. 288974 ítem {it} · {cc}", f"{PROVEMET_C} · ítem {it}", "2026-10-29", "similar",
                f"{txt} (sin costura, triple certificación: cumple A53 Gr B, que pide el plano); Provemet cot. 288974 (29-10-2026), precio neto con bonificación 4% (vale comprando toda la cotización), validez 15 días", codigo=cc)
    for q in (p_, p_ + "b"):
        items[q]["fuentes"] = [dict(fp)] + items[q]["fuentes"]
# Sensores A, B y C (incluidos: la planilla dice "Incluye la provisión de todos los equipos y materiales"); marcas del listado
poner("A", [fuente("cot", 1478.0 + 80.0, "Induquip (Emerson) cot. 26-523-RSDGVM-RSMT ítem PIT-011: Rosemount 2051TG2A2B21AS1B4E7M5P1Q4Q8, USD 1.478 + "
                   "bloqueo y purga ABAC USD 80 (VAL-03162, planilla TAVAL/55, 22-04-2026)", LACH + "Oferta Induquip 26-333-RSDGVM-USM.pdf.txt", "2026-07-17",
                   "similar", "rango 0-10,3 bar (pedido 0-25 bar: pedir rango 3) y opción de sello remoto S1 que no hace falta; bloqueo y purga 1/2\" (sensor 3/4\": pedir 3/4\"); Rosemount y ABAC están en el listado",
                   validez_hasta="2026-08-16"),
            fuente("cot", 934.0 + 150.0, "CV Control PE51913-R0 (presupuesto estimativo): Yokogawa EJA530E USD 934 + bloqueo y purga AISI 316 USD 150",
                   LACH + "Cotización - S51913 CV Control Yokogawa.pdf.txt", "2026-07-16", "similar",
                   "Yokogawa (listado), rango a confirmar; plazo 140 días (por eso no es la base)")])
poner("B", [fuente("cot", round(829.04 + 309.936, 2), "Induquip (Emerson) cot. 26-523-RSDGVM-RSMT: transmisor Rosemount 644HAE7J6M5Q4 USD 829,04 + "
                   "sensor RTD 214C PT100 USD 309,94 (la termovaina es la pos 18)", LACH + "Oferta Induquip 26-333-RSDGVM-USM.pdf.txt", "2026-07-17",
                   "similar", "rango 0-100 °C a configurar; el sensor 214C cotizado se cotizó armado a la termovaina de C-276 de esa misma oferta (opción XW, otra conexión a proceso): pedirlo para la termovaina 3/4\" NPT de la pos 18; Rosemount está en el listado", validez_hasta="2026-08-16")])
poner("C", [SIN("switch de fin de carrera de la monitora (0-24 V): pedir con las reguladoras (Tormene ofrece indicador de posición; confirmar si trae contacto)")])

# ---------------------------------------------------------------- filas que agrega ITT (no están en la tabla del plano)
ext = {
    "2": [("2b", "Tubing de acero inoxidable y accesorios de doble virola para las señales de las reguladoras y monitoras (ET 5.8)", 1, "gl",
           SIN("tubing inoxidable 3/8\" y conectores de doble virola: no hay precio en la base; pedir a Swagelok, Parker, Casucci, Fittinox, ABAC, Famiq o Hoke (listado)"),
           "ET SCE-RE-515-0032 §5.8: \"Para el montaje de las señales de las válvulas reguladoras se utilizarán tubings y accesorios en acero inoxidable del tipo doble virola\"")],
    "5": [("5b", "Junta espiralada 3\" #150 AISI 316/grafito con anillo ext. zincado (juntas de las válvulas, nota del plano)", 12, "un",
           fuente("ant", 6.0, "Planilla Techint/12 (JUN-01698)", TECHINT12, "2025-12-23", "igual", "comprar Klinger, Teadit, Flexseal, Miyashiro Schonborn o Garlock (listado)"),
           "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)"),
          ("5c", "Espárrago 5/8\" × 3 1/2\" A193 B7 con 2 tuercas 2H zincado (4 por junta de 3\")", 48, "un",
           fuente("est", 10.0, "Bules o Versailles (planilla TAVAL/43, hoja 3\" x 442u ítem 9) · JUN-04173",
                  "fuentes_originales/ofertas_texto/TAVAL/43- YPF- CM PUENTES DE PRODUCCION/4.Armado de la Oferta Comercial/TAVAL- LM - Puentes de Producción YPF.xlsx.txt · línea 147",
                  "2026-02-19", "similar", "largo 110 mm (pedido 3 1/2\" ≈ 89 mm, más largo: sirve); la planilla pone USD 10 también al de 7/8\" x 230 mm: "
                  "parece valor global, pedir cotización (Delgado, Petrobul, Versailles o Fornis)", codigo="JUN-04173"),
           "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)")],
    "6": [("6b", "Junta espiralada 6\" #150 AISI 316/grafito con anillo ext. zincado", 4, "un",
           fuente("est", 12.99, "JUN-01702 JUNTA ESPIRALADA C/ANILLO INT. 6\" 150# AISI 316/GRAFITO/AC CAB. ZINCADO (planilla de compras TAVAL/3)",
                  "fuentes_originales/ofertas_texto/TAVAL/3-YPF Separador Bifasicos - Separadores para satelites", "2025-03-27", "igual",
                  "misma junta; valor del período con cepo llevado a dólar blue: pedir cotización", codigo="JUN-01702"),
           "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)"),
          ("6c", "Espárrago 3/4\" × 4\" A193 B7 con 2 tuercas 2H zincado (8 por junta de 6\")", 32, "un",
           fuente("est", 10.0, "Planilla Techint/12 (JUN-02733: 3/4\" L 120 mm con 2 tuercas zincado)", TECHINT12, "2025-12-23", "similar",
                  "L 120 mm · estimado: la planilla Techint/12 tiene columnas ambiguas (tercera auditoría 30-10-2026)"),
           "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)")],
    "7": [("7b", "Junta espiralada 8\" #150 AISI 316/grafito (brida ciega)", 1, "un",
           SIN("sin junta 8\" #150 con precio en la base (la de MS Juntas es #300 y MS Juntas no está en el listado): pedir cotización"),
           "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)"),
          ("7c", "Espárrago 3/4\" × 4 1/4\" A193 B7 con 2 tuercas 2H zincado (8 por la brida ciega 8\")", 8, "un",
           fuente("est", 10.0, "Planilla Techint/12 (JUN-02733)", TECHINT12, "2025-12-23", "similar",
                  "L 120 mm · estimado: la planilla Techint/12 tiene columnas ambiguas (tercera auditoría 30-10-2026)"),
           "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)")],
    # Conexiones que el dibujo muestra soldadas al caño y la tabla no lista (revisión 30-10-2026): 15 ×2, 16 ×2 y 19 ×4 son roscados
    # NPT sobre el caño; 18 ×2 y A ×1 son 3/4" NPT. Sin cupla no se pueden montar.
    "17": [("17b", "Cupla para soldar 1/2\" NPT S3000 ASTM A-105 para las tomas multiport, válvulas de alivio y manómetros (8 conexiones)", 8, "un",
            fuente("lista", 2.71, "Renard (cód. 5292) · AFO-00715", RENARD + " · código 5292", "2025-12-26", "igual", codigo="AFO-00715"),
            "Agregado de ITT: el dibujo muestra estas conexiones roscadas sobre el caño y la tabla no lista sus cuplas")],
    "18": [("18b", "Cupla para soldar 3/4\" NPT S3000 ASTM A-105 para las 2 termovainas y el transmisor de presión (3 conexiones)", 3, "un",
            fuente("lista", 3.51, "Renard (cód. 5293) · AFO-00721", RENARD + " · código 5293", "2025-12-26", "igual", codigo="AFO-00721"),
            "Agregado de ITT: el dibujo muestra estas conexiones roscadas sobre el caño y la tabla no lista sus cuplas")],
    "20": [("20b", "Placa de identificación del equipo AISI 304 (ET §7)", 1, "un",
            fuente("est", 10.0, "Planilla de costo ITT, salto de regulación Camuzzi ERP Caseros (CAMUZZI/14, renglón 40: PLACA DE IDENTIFICACIÓN AISI 304, 10 USD)",
                   CAM14, "2022-03-15", "igual", "precio de 2022"),
            "ET SCE-RE-515-0032 §7: el data book incluye la placa de identificación del equipo")],
}
lista = []
for it in auto["items"]:
    lista.append(items.get(it["pos"], it))
    for pos, desc, q, u, f, esp in ext.get(it["pos"], []):
        lista.append({"id": "M" + pos.upper(), "pos": pos, "grupo": "material", "descripcion": desc, "especificacion": esp,
                      "cantidad": q, "unidad": u, "fuentes": [f]})
# compra extra de caño: media tira (6 m), no 12 m: con 1-2 m usados una tira de 12 m deja más del 80% de sobrante
for p, usado in (("21", 1.8), ("22", 2.0), ("23", 2.25), ("24", 1.0)):
    b = items[p + "b"]
    b["cantidad"] = round(6 - usado, 3)
    b["descripcion"] = f"Completar media tira de 6 m de la pos {p} (compra mínima; sobrante a stock)"
    b["especificacion"] = f"1 tramo de 6 m para {usado:g} m (con tira de 12 m el sobrante superaba 80%)"

# ---------------------------------------------------------------- MO y servicios
# Soldaduras junta por junta, contadas del dibujo (planta y corte A-A del plano SCE-RE-315-0048), revisión del 30-10-2026
BW = {3: 12, 6: 19, 8: 6}
SW = {0.5: 2 + 2 + 8, 0.75: 3}
pulg = sum(d * n for d, n in BW.items()) + sum(d * n * 1.75 for d, n in SW.items())
s01 = items["MO"]
s01["descripcion"] = f"Soldaduras: {sum(BW.values())} a tope + {sum(SW.values())} cuplas SW (contadas del dibujo)"
s01["cantidad"] = round(pulg, 2)
s01["especificacion"] = (
    "Junta por junta (dibujo del plano, todas de taller): "
    "ramas 3\" (×2): reducción 11–brida 5 de la esférica 3, brida 5–caño 21 (200 mm)–brida 5 de la monitora, brida 5–caño 21 (150 mm)–brida 5 de la reguladora, "
    "brida 5 de la reguladora–reducción 11 = 6 juntas 3\" por rama (12); "
    "ramas 6\" (×2): te 9–reducción 11, reducción 11–caño 23 (1.000 mm), caño 23–brida 6 de la esférica 4, brida 6–caño 22–ramal de la te 10 = 5 juntas 6\" por rama (10); "
    "colector de entrada 6\": casquete 12–te 9 (×2), te 9–caño 22 (×2), caño 22–te 9 central (×2), te 9 central–brida 6 de entrada = 7; "
    "salida 6\": ramal de la te 10 central–caño 23 (250 mm)–brida 6 = 2; "
    "colector de salida 8\": brida 7–te 10, te 10–caño 24–te 10 (×2 tramos = 4), te 10–casquete 13 = 6. "
    "Total 12 × 3\" + 19 × 6\" + 6 × 8\" = 198 pulg-diam (factor de espesor 1: bridas y accesorios STD; las 6 juntas con el caño 23 sch 80 se "
    "sueldan al espesor STD de la brida/reducción, ver consulta R77). "
    "Cuplas SW: 1/2\" × 12 (pos 14 ×2, 17 ×2, 17b ×8) × 0,5 × 1,75 = 10,5 y 3/4\" × 3 (18b) × 0,75 × 1,75 = 3,94 (factores_accesorios.csv). "
    f"Total {pulg:.2f} pulg-eq (antes 195,5: la precotización contaba los extremos × 0,75 y no tenía las cuplas de 15, 16, 18, 19 y A).")
# RX: tarifa confirmada por Matías el 30-10-2026 (precios_usuario.csv); placas por junta de factores_soldadura.csv (3" 3, 6" 4, 8" 4)
placas = BW[3] * 3 + BW[6] * 4 + BW[8] * 4
visitas = math.ceil(placas / 45)
rx_ars = visitas * 850000 + placas * 15000
poner("RX", [fuente("cot", round(rx_ars / TC_OCT, 2),
                    f"Proveedor de RX (sin nombre), precio confirmado por Matías el 30-10-2026: {visitas} visitas × ARS 850.000 + {placas} placas × ARS 15.000, "
                    f"sin IVA, a BNA venta promedio 10-2026 (1.543,23) · END-00572 / END-00571", "conocimiento/precios/precios_usuario.csv", HOY, "igual",
                    "placas contadas por junta (37 juntas a tope); confirmar con el mapa de soldaduras"),
             fuente("ant", 2803.5, "Servicio de radiografía DB NDT (2026-08; tarifas.csv): 135 placas + 4 servicios + 1 LP", "PAMPA ENERGIA/5 y /7, hoja ENOD (Lista DB NDT)",
                    "2026-08-31", "similar", "tarifa anterior (incluía LP)")],
     descripcion="Radiografía 100% de las juntas a tope (ET 5.3.1)",
     especificacion=f"37 juntas a tope → {placas} placas chicas → {visitas} visitas de hasta 45 placas")
s_lp = {"id": "S04L", "pos": "LP", "grupo": "servicio", "descripcion": "Líquidos penetrantes en cuplas SW y filetes, 2ª y última pasada (ET 5.3.1)",
        "especificacion": "15 cuplas SW + filetes de soportes: 1 servicio", "cantidad": 1, "unidad": "servicio",
        "fuentes": [fuente("ant", 294.0, "Servicio de líquidos penetrantes DB NDT (tarifas.csv)", "conocimiento/costos/tarifas.csv · PAMPA ENERGIA/5 y /7, hoja ENOD (Lista DB NDT)",
                           "2026-08-31", "igual")]}
s_pro = {"id": "S07", "pos": "PRO", "grupo": "servicio", "descripcion": "Procedimientos de radiografía y de líquidos penetrantes firmados por nivel 3 (ET 3.1.3)",
         "especificacion": "2 procedimientos (RX y LP) para aprobación de Camuzzi; los de soldadura, PH, fugas y pintura van en las horas de ingeniería y calidad",
         "cantidad": 2, "unidad": "procedimiento",
         "fuentes": [fuente("cot", 250.0, "NDT Antonelli (JCA & Asociados) · ING-00086 Procedimiento escrito END nivel 3", "fuentes_originales/antonelli_end_2025-11.pdf",
                            "2025-11-03", "igual")]}
s05 = {"id": "S05", "pos": "EST", "grupo": "mo", "descripcion": "Fabricación del skid y soportes (330 kg estimados)", "especificacion": "kg × tarifa por kg de estructura de skid",
       "cantidad": 330, "unidad": "kg", "fuentes": [fuente("ant", 3.0, "Fabricación de estructura de skid por kg (tercero Ledesma): tarifas.csv",
                                                           "YPF/28 Lic 69343 planilla PC0 (850 kg × 3 = 2.550)", "2026-10-10", "similar", "kilos estimados")]}
# Prueba de fugas: aire seco o N2 a 5,5 bar (ET 5.4.3) con el equipo terminado; 2 operarios × 4 h de planta, con aire de planta
s06 = {"id": "S06", "pos": "PF", "grupo": "servicio", "descripcion": "Prueba de fugas con aire seco o nitrógeno a 5,5 bar con el equipo terminado (ET 5.4.3)",
       "especificacion": "2 operarios × 4 h (presurizar por sectores, solución jabonosa y espejo, registro); con aire de planta",
       "cantidad": 8, "unidad": "h", "fuentes": [fuente("est", 13.0, "Horas de planta para movimientos internos y PH (END-00563, planilla ITT YPF/28)",
                                                        "fuentes_originales/ofertas_texto/YPF/28- Lic 69343 - SKIDS CONCENTRADORES VCD26217 - BLOQUE LAN/4.Armado de la Oferta Comercial/Cotización Lic 69343 Skid concentradores VCD26217 PC0.xlsx.txt",
                                                        "2026-10-10", "similar", "8 h estimadas por ITT para la prueba (tarifa por hora de planta)")]}
lista += [s_lp, s_pro, s05, s06]
for it in lista:  # pintura: sumar el skid (≈ 25 m de UPN 120 ≈ 10,7 m²), que precotizar no cuenta cuando el skid va por unidad
    if it["pos"] == "PIN":
        it["cantidad"] = round((it["cantidad"] + 10.7) * 1.2, 3)
        it["especificacion"] += " + skid ≈ 10,7 m² (25 m de UPN 120), × 1,2 de overspray como la planilla del precio · esquema SCE-PC-511-0003 a confirmar (consulta R33)"
        it["fuentes"] = [fuente("ant", 37.98, "Pintor (sin nombre) · PIN-00579 (precio confirmado por Matías)", "conocimiento/precios/precios_usuario.csv", "2026-10-30", "similar", "Granallado y pintura de piping y skid, incluye materiales: USD 37,98/m² confirmado por Matías Russo el 30-10-2026 (precio firme, PIN-00579); la planilla de origen (YPF Lic 66944 colectores) lo aplica sobre los m² + 20 % de overspray, por eso la cantidad va × 1,2; esquema SCE-PC-511-0003 a confirmar", codigo="PIN-00579"),
                         fuente("ant", 50.0, "criterio ITT · PIN-00569 (YPF/28)", "conocimiento/precios/catalogo_servicios.csv", "2026-10-10", "similar", "referencia anterior (hasta el 05-11-2026)", codigo="PIN-00569")]
base["items"] = lista

# ---------------------------------------------------------------- parámetros, plazo, textos del informe
base["meta"] = ["Concurso de precios N° 24578 · ítem 2", "Plano SCE-RE-315-0048 rev A · Especificación SCE-RE-515-0032", "Comprador: Camuzzi (portal de compras)",
                "Preparó: Matías Russo · 28-10-2026"]
base["parametros"].update({"TRANS": 1, "TC": TC_OCT, "TR_ARS": 700000, "TR_EMB": 150, "TR_F": 1.0, "fecha_referencia": "2026-10-31"})  # último mes con índices (05-11-2026)
base["fecha"] = "2026-10-28"
base["plazo"] = {"dias": 175, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Ingeniería y aprobación por Camuzzi de marca y modelo de las reguladoras (ET 5.6.1)", 0, 20, ""],
                            ["Reguladoras y monitoras (Tormene: 45/60 días de OC y anticipo, pedidas con el modelo aprobado)", 20, 80, ""],
                            ["Transmisores A y B (Rosemount, Induquip: 12 semanas)", 0, 84, "crit"],
                            ["Esféricas 3\" y 6\" con ensayo SCE-RE-308-0001 (Esferomatic: 60/70 días, nota de TAVAL/49)", 0, 70, ""],
                            ["Bridas, accesorios y caño (Renard, stock)", 0, 30, ""],
                            ["Prefabricado, soldadura, RX 100% y PH (sin válvulas)", 84, 114, "tal"],
                            ["Montaje de válvulas, conexionado de pilotos, pintura y prueba de fugas", 114, 134, "tal"],
                            ["Inspección Camuzzi, data book y despacho", 134, 149, "tal"]],
                 "nota": ("Plazo calculado 149 días (último material: transmisores, 84 días + taller 65 días, sin superponer); con el margen de 15% de la "
                          "regla (plazos.md §4) son 171-179 días: se ofrecen 175 (mediana real de la familia SK: 162). Las multas son automáticas (0,30% "
                          "diario). Con Yokogawa (140 días) el plazo pasaría a ~205 días.")}
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)",
                 "referencia_html": "<b>Estimado:</b> un camión con hidrogrúa Quilmes → Mercado Central nave D3 (≈ 30 km), ARS 700.000 + USD 150 de embalaje. No hay cotización de flete local en la base: pedir a Compras.",
                 "criterio_html": "La planilla del concurso dice \"Flete a cargo del proveedor hasta Transporte Cruz del Sur, Mercado Central nave D3\": el flete va incluido en el precio."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · Cláusulas particulares del 01-10-2026 · especificación del 19-10-2026",
                  "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"],
                                 ["Ítem", "2 · Skid de regulación / medición · <b>1 un</b>"],
                                 ["Documentos", "Plano SCE-RE-315-0048 rev A · Especificación SCE-RE-515-0032 (ERP Parque Industrial Tres Arroyos) · Listado de marcas SCE-IN-501-0015 rev 1"],
                                 ["Condiciones de proceso", "Pe 15-10 bar · Pr 4 bar · Qmáx 6.000 Sm3/h · Qmín 1.000 Sm3/h"],
                                 ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (flete a cargo del proveedor)"],
                                 ["Condiciones", "Pago 30 días f.p.f. por transferencia, dólar BNA divisa vendedor del día de factura · validez 30 días · multas automáticas por demora (0,30% a 0,60% diario, tope 25%)"]],
                  "requisitos_html": ["Matriz completa en pedido/requisitos.csv (84 requisitos con destino) y consultas en consultas_cliente.md",
                                      "RX 100% de las soldaduras a tope (filetes y media V con tintas penetrantes)", "PH de los prefabricados sin válvulas: 1,5 × presión máxima de la serie, 6 h (NAG-124); secado y prueba de fugas con aire o N2 a 5,5 bar",
                                      "Protección anticorrosiva SCE-PC-511-0003", "Esféricas según SCE-IN-501-0008 y ensayo SCE-RE-308-0001, con certificados firmados", "Marcas del listado SCE-IN-501-0015",
                                      "Tubing inoxidable de doble virola para las señales de las reguladoras; manifold de 3 vías A-105 zincado serie 3000; espárragos B7/2H zincados",
                                      "Documentación para aprobación (planos, mapa de soldaduras, procedimientos, calificaciones) y data book", "Inspección de Camuzzi en etapas (aviso 5 días hábiles)", "DDJJ de ética firmada con la oferta"]}
base["nota_mo_html"] = ("Soldadura propia por pulgada (16 USD/pulg-eq): 37 juntas a tope y 15 cuplas SW contadas una por una del dibujo (planta y corte A-A). "
                        "Montaje, ingeniería y calidad estimados del antecedente de skid más parecido (Sacde/15). RX con la tarifa confirmada por Matías el 30-10-2026; "
                        "LP, procedimientos de END, PH (en el montaje), prueba de fugas, pintura y fabricación del skid (330 kg estimados) en renglones propios. "
                        "Juntas y espárragos según la nota del plano (solo uniones internas; las de conexión a la planta no).")
base["desvios"] = [
    {"tag": "Pos 1-2 y C", "titulo": "Reguladoras sin precio", "texto": "No hay cotización #150 en la base (la de Tormene es #300 con OPSO): quedan en 0 hasta que Compras traiga el precio. El total no es comparable hasta entonces."},
    {"tag": "Pos 17b, 18b, 2b", "titulo": "Agregados de ITT", "texto": "Cuplas de las conexiones 15, 16, 18, 19 y A (el dibujo las muestra, la tabla no) y tubing inoxidable de doble virola de la ET 5.8."},
    {"tag": "Consultas", "titulo": "5 consultas al cliente", "texto": "Pos 14 (cantidad y material A-106), pos 9 (te A-105 o A234 WPB), pos 23 sch 80 contra bridas y reducciones STD, y documentos técnicos de Camuzzi que no están en el pliego (ver consultas_cliente.md)."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>CAMUZZI/14</b> · CGP 6910, salto de regulación ERP Caseros (planilla de costo rev 2)", "fecha": "15-03-2022",
     "que": "Salto de regulación 4\" #150 con 2 monitoras + 2 reguladoras 4\", esféricas, mariposas 10\" y skid", "precio": "costo 71.833,70 (reguladoras 34.326)",
     "tomado_html": "Precio de la toma multiport (pos 15), la válvula de alivio (pos 16) y la placa de identificación; reparto del costo por rubro (sin ajustar)"},
    {"carpeta_html": "<b>CAMUZZI/23</b> · Concurso 17584, ítem 5 (OC 4500150421)", "fecha": "06-03-2025", "que": "Skid de regulación / medición SCE-RE-315-0047 (ERP Ascensión), ganado", "precio": "venta 24.454",
     "tomado_html": "Orden de magnitud (no hay planilla de costo ni plano en la carpeta)"},
    {"carpeta_html": "<b>ALONZO RED/2</b> · ERP B° Pilará (Naturgy)", "fecha": "16-06-2026", "que": "Reguladoras Tormene TA956 3\" #300 monitor + activo", "precio": "9.545 / 6.073",
     "tomado_html": "Solo referencia (otra serie): no se usa como precio"},
    {"carpeta_html": "<b>TAVAL/69</b> · YPF UTE LACH", "fecha": "19-07-2026", "que": "Transmisores Rosemount/Yokogawa y manómetros Weisz; 2 skids de regulación y medición (MO Ledesma 200295)", "precio": "17.200 (MO de 2 skids)",
     "tomado_html": "Precio de los sensores A y B; control de la MO (tercero ≈ 8.600 por skid)"}]
base["pendientes"] = [
    {"titulo": "Compras (lista en compras/)", "items": [
        "Reguladoras y monitoras 3\" #150, Pe 15-10 / Pr 4 bar, Qmáx 6.000 Sm3/h, modelo homologado (Tormene TA956 FC/DFO, Fiorentini Reflux/Aperflux, Fisher), con switch de posición (pos 1, 2, C)",
        "Esféricas 3\" y 6\" #150 con ensayo SCE-RE-308-0001 (Esferomatic, Worcester, Valvtronic…)", "Junta 8\" #150 (7b) y espárragos B7/2H (5c, 6c, 7c)",
        "Toma multiport ABAC (15), alivio S-71 (16), cupla con esférica (14, según la respuesta R78), tubing de doble virola (2b)",
        "Reconfirmar: lista Renard (12-2025), Taval (09-2025), Induquip y Weisz (07-2026), Provemet (07-2025), Antonelli (11-2025); flete local a Tapiales"]},
    {"titulo": "Camuzzi (consultas_cliente.md, borrador: las manda Matías)", "items": [
        "R76: pos 14, 2 en la tabla y 4 en el dibujo", "R83: pos 9, te A-105 (¿se acepta A234 WPB?)", "R78: pos 14 en ASTM A-106", "R77: pos 23 sch 80 contra bridas y reducciones STD",
        "R33 (pendiente de ITT: descargarlos; si no están, consulta 4): documentos técnicos citados (SCE-RE-110-0006, SCE-PC-511-0003, SCE-IN-501-0008, SCE-RE-308-0001, SCE-IN-301-0005, SCE-IN-501-0003)"]}]
base["planilla_notas"] = ["Plazo: 175 días desde OC (transmisores 84 días + taller 65 = 149, más 15-20% de margen).",
                          "Condiciones del concurso: pago 30 días f.p.f., USD al BNA divisa vendedor del día de factura, validez 30 días, entregado en Transporte Cruz del Sur (Tapiales)."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar."
base["historial_html"] = ["30-10-2026: revisión completa (matriz de requisitos, precios, compatibilidades, soldaduras junta por junta, RX, plazo); ver bitácora."]
MARCAS = {"1": "Tormene (TA956 FC monitor), Fiorentini, Fisher u otro modelo homologado", "2": "Tormene (TA956 DFO), Fiorentini (Reflux/Aperflux), Fisher (EZR) u otro homologado",
          "3": "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Beta / Valmec", "4": "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Beta / Valmec (Spirax Sarco solo hasta 4\" S150)",
          "5": "Futura / Francovigh (bridas)", "6": "Futura / Francovigh (bridas)", "7": "Futura / Francovigh (bridas)", "8": "Futura / Francovigh (bridas)",
          "9": "Curvo Sold (Cintolo)", "10": "Curvo Sold (Cintolo)", "11": "Curvo Sold (Cintolo)", "12": "Curvo Sold (Cintolo)", "13": "Curvo Sold (Cintolo)",
          "14": "Thorsa / Forja Atlas (cupla); esférica del listado", "15": "ABAC", "16": "Favra / Aerre / Farinola (Doma, fabricante del S-71, no figura en alivios: consultar)", "17": "Thorsa / Forja Atlas", "18": "Weisz / Wika / ABAC / Casucci",
          "19": "ABAC VA 350 / Casucci (bloqueo y purga); Weisz / Wika / ABAC / Casucci (manómetro)", "20": "taller (UPN 120, Provemet)", "A": "Rosemount / Yokogawa / Siemens / Aplisens / SMAR",
          "B": "Rosemount / Yokogawa / Siemens / Aplisens / SMAR", "C": "con las reguladoras", "5b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)",
          "6b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)", "7b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)",
          "5c": "Delgado / Petrobul / Talleres Versailles / Fornis", "6c": "Delgado / Petrobul / Talleres Versailles / Fornis", "7c": "Delgado / Petrobul / Talleres Versailles / Fornis",
          "2b": "Swagelok / Parker / Casucci / Fittinox / ABAC / Famiq / Hoke", "17b": "Thorsa / Forja Atlas", "18b": "Thorsa / Forja Atlas"}
base["compras"] = {"marcas": {"1": "Doma / Satesa / EQA / Epta / Tormene / Fiorentini / Fisher / Francel (solo modelos homologados de la solapa \"Válvulas Reguladoras\"; Ø mayor a 4\" con aprobación de la Gerencia Técnica)", "2": "Doma / Satesa / EQA / Epta / Tormene / Fiorentini / Fisher / Francel (solo modelos homologados de la solapa \"Válvulas Reguladoras\"; Ø mayor a 4\" con aprobación de la Gerencia Técnica)", "2b": "Swagelok / Parker / Casucci / Fittinox / ABAC / Famiq / Hoke-Gyrolok", "3": "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Spirax Sarco (bridadas o roscadas hasta 4\" S150 y 1 1/2\" S300) / Beta / Valmec", "4": "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Spirax Sarco (bridadas o roscadas hasta 4\" S150 y 1 1/2\" S300) / Beta / Valmec", "5": "Futura / Francovigh", "6": "Futura / Francovigh", "7": "Futura / Francovigh", "8": "Futura / Francovigh", "5b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)", "6b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)", "7b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)", "5c": "Delgado / Petrobul / Talleres Versailles / Fornis (terminación zincado / anodizado)", "6c": "Delgado / Petrobul / Talleres Versailles / Fornis (terminación zincado / anodizado)", "7c": "Delgado / Petrobul / Talleres Versailles / Fornis (terminación zincado / anodizado)", "9": "Curvo Sold / TDW", "10": "Curvo Sold / TDW", "11": "Curvo Sold / TDW", "12": "Curvo Sold / TDW", "13": "Curvo Sold / TDW", "14": "Cupla: CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet). Esférica: Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Spirax Sarco (bridadas o roscadas hasta 4\" S150 y 1 1/2\" S300) / Beta / Valmec", "15": "Sin subgrupo propio (el plano pide ABAC, que figura en accesorios para conexiones de acero inoxidable)", "16": "Favra / Aerre / Farinola (con bridas ANSI o roscadas). El tipo S-71 es un modelo Doma y Doma no figura en válvulas de alivio: consultar a Camuzzi", "17": "CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet)", "17b": "CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet)", "18": "El listado no trae marcas para este producto", "18b": "CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet)", "19": "Bloqueo y purga: ABAC (modelo VA 350 y tapón 50 T) / Casucci. Manómetro: Ing. Capino / Weisz / Wika (diferencial con aguja de arrastre) / ABAC / Casucci", "20": "El listado no trae marcas para este producto", "20b": "El listado no trae marcas para este producto", "21": "El listado no trae marcas para este producto", "22": "El listado no trae marcas para este producto", "23": "El listado no trae marcas para este producto", "24": "El listado no trae marcas para este producto", "A": "Transmisor: Rosemount / Yokogawa / Siemens / Aplisens / Bristol / Zürich / Smar. Bloqueo y purga: ABAC (modelo VA 350 y tapón 50 T) / Casucci", "B": "Rosemount / Yokogawa / Siemens / Aplisens / Bristol / Zürich / Smar", "C": "El listado no trae marcas para este producto"}, "material": {"1": "SCE-RE-508-0002 §7: cuerpo de acero fundido ASTM A-216 WCB o superior o ASTM A-350 CF8 o superior, o acero forjado ASTM A-105 (prohibido bronce, latón, aluminio u otra aleación con tensión de ruptura menor a 480 MPa); internos de acero inoxidable; diafragmas de goma nitrílica (Buna N) y tela según IRAM 113001; espárragos ASTM A193 B7 y tuercas ASTM A194 2H", "2": "SCE-RE-508-0002 §7: cuerpo de acero fundido ASTM A-216 WCB o superior o ASTM A-350 CF8 o superior, o acero forjado ASTM A-105 (prohibido bronce, latón, aluminio u otra aleación con tensión de ruptura menor a 480 MPa); internos de acero inoxidable; diafragmas de goma nitrílica (Buna N) y tela según IRAM 113001; espárragos ASTM A193 B7 y tuercas ASTM A194 2H", "3": "SCE-IN-501-0008 §6.2 (resumen no oficial): cuerpo de acero al carbono totalmente calmado (API 6D punto 8), CE ≤ 0,50 %; esfera inox, o AC / fundición con cromo duro (≥ 35 µm, ≥ 600 HV) o níquel químico (≥ 35 µm, 450-540 HV); vástago inox o AC con cromo duro o níquel químico; asientos de teflón (PTFE) (§6.3.5); espárragos ASTM A193 B7, tuercas ASTM A194 2H", "4": "SCE-IN-501-0008 §6.2 (resumen no oficial): cuerpo de acero al carbono totalmente calmado (API 6D punto 8), CE ≤ 0,50 %; esfera inox, o AC / fundición con cromo duro (≥ 35 µm, ≥ 600 HV) o níquel químico (≥ 35 µm, 450-540 HV); vástago inox o AC con cromo duro o níquel químico; asientos inoxidables más blandos que la esfera, con inserto PTFE o Vitón y resortes inox (§6.3.2 a 6.3.5); espárragos ASTM A193 B7, tuercas ASTM A194 2H"}, "fecha_respuesta": "2026-11-04", "material_en_planta_dias": 84, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo de entrega y validez de la oferta.",
                                            f"Solo marcas del {LISTADO}; cualquier otra marca, avisar antes de cotizar.",
                                            "Certificados de material 3.1; válvulas esféricas con certificados de fabricación y prueba según SCE-IN-501-0008 / SCE-RE-308-0001 firmados por la inspección.",
                                            "Espárragos ASTM A193 B7 con tuercas A194 2H zincados; manómetros con certificado de calibración (ET 5.7.1).", "Indicar cualquier diferencia con lo pedido.", "Válvulas esféricas (SCE-IN-501-0008 y ensayo SCE-RE-308-0001; no se aceptan sin certificados de fabricación y prueba firmados por la inspección): diseño ASME B16.34, fabricación API 6D, bridas ASME B16.5, a prueba de fuego API 607 con dispositivo antiestático, topes e indicador abierto/cerrado, fuerza de maniobra máx. 345 N a máxima ΔP (ensayo de torque API 6D B.6), esfera y vástago inox o AC con cromo duro / níquel químico ≥ 35 µm (hasta 2\": esfera solo inox), cuerpo AC calmado CE ≤ 0,50 %, espárragos A193 B7 / tuercas A194 2H, largo entre caras API 6D, prueba hidráulica de cuerpo y asientos y neumática burbuja cero sin sellador, marcado con fabricante, N° de OC, PT o PR, Ø, presión máx. y sentido de flujo, pintura SCE-PC-511-0003 (amarillo), entrega abierta con extremos protegidos (no cartón) y termocontraíble ≥ 500 µm, documentación por lote (certificados de materiales, ensayos hidráulico/neumático/torque, antifuego, cromado o niquelado, manual, despiece con repuestos, grasa recomendada), lista de repuestos valorizada para 1 año, garantía 12 meses desde instalación o 24 desde despacho. Fabricante aprobado por Camuzzi; si el modelo es nuevo para Camuzzi, ensayos de prototipo (8.2).", "Reguladoras, monitoras y alivios (SCE-RE-508-0002): cuerpo A216 WCB / A350 / A105 (prohibido bronce, latón o aluminio), internos inox, obturador blando PTFE, diafragmas de nitrilo IRAM 113001, espárragos B7/2H, placa de identificación con modelo, Ø, serie, internos, piloto, presiones máx. y N° de OC; ensayos de cuerpo a 1,5 × la serie (28,5 bar en #150; 110 bar en #600) 4 h y hermeticidad a 5,5 bar; pintura: cuerpo y actuador amarillo, válvulas de alivio naranja (SCE-PC-511-0003); entrega con extremos obturados, piloto protegido y fijada a bancada; hoja de datos y lista de repuestos recomendados con vida útil. Solo modelos homologados de la solapa \"Válvulas Reguladoras\" del SCE-IN-501-0015 rev 1 (Ø mayor a 4\" requiere aprobación de Camuzzi)."],
                   "notas": {"16": "Alivio de capacidad reducida tipo S-71, 1/2\" NPT S3000, cuerpo de acero (no bronce); presión de apertura y rango de resorte a confirmar con Camuzzi (salida regulada 4 bar); indicar capacidad de descarga. el S-70 es modelo Doma y el S-71 se presume de la misma línea; Doma NO figura en válvulas de alivio del listado (solo Favra, Aerre y Farinola): consultar a Camuzzi. Pintura naranja. Requisitos SCE-RE-508-0002", "4": "Esférica 6\" #150 bridada B16.5 RF (confirmar cara), paso reducido, a prueba de fuego: esfera guiada TRUNNION (obligatoria en más de 4\" #150), DOBLE BLOQUEO Y PURGA, asientos inox con inserto PTFE o Vitón y resortes inox, eje inferior ≥ superior y bujes autolubricados tipo DU; palanca incluida (hasta 6\") con fuerza ≤ 345 N: si no la cumple, ofrecer reductor y aclararlo. Requisitos SCE-IN-501-0008 en requisitos generales", "3": "Esférica 3\" #150 bridada B16.5 RF (confirmar cara), paso reducido, a prueba de fuego: esfera flotante, asientos PTFE, palanca incluida con cierre horario. No exige doble bloqueo y purga ni venteo. Requisitos SCE-IN-501-0008 en requisitos generales", "1": "Monitora pilotada NC, obturador guiado, 3\" #150 RF (cara a confirmar con Camuzzi), Pe 15-10 bar, Pr 4 bar, Q 1.000-6.000 Sm3/h, SIN bloqueo OPSO, con switch de posición 0-24 V (pos C). Modelo homologado (ej. Tormene TA956 FC monitor; Epta VD277 + monitor FC); misma marca y pilotos compatibles con la reguladora (pos 2); el fabricante entrega el diagrama de conexionado de pilotos (ET 5.6.1). Requisitos SCE-RE-508-0002 (ver requisitos generales)",
                             "2": "Reguladora pilotada a diafragma NA, 3\" #150 RF (cara a confirmar), Pe 15-10 bar, Pr 4 bar, Q 1.000-6.000 Sm3/h; misma marca que la monitora (pos 1), pilotos compatibles. Modelo homologado (ej. Tormene TA956 DFO, Fiorentini Reflux / Aperflux, Fisher EZR, Epta VD277). Requisitos SCE-RE-508-0002 (ver requisitos generales)",
                             "14": "Consulta R78 al cliente (material A-106): cotizar cupla 1/2\" NPT S3000 A105 + esférica 1/2\" NPT S3000 paso total, palanca, esfera inox; consultar a Camuzzi si le aplica la SCE-IN-501-0008 (a prueba de fuego y antiestática)",
                             "19": "Bloqueo y purga 1/2\" NPT S3000 ABAC VA 350 con tapón 50 T (modelo del listado) o Casucci, con manómetro 4\" 0-6 bar, glicerina, clase 1, caja AISI 304, bourdon AISI 316, IP65, certificado de calibración, montado con manifold de 3 vías A-105 zincado serie 3000",
                             "A": "Transmisor de presión 0-25 bar, 4-20 mA, 1/2\" NPT, con válvula de bloqueo y purga ABAC VA 350 / Casucci",
                             "B": "Transmisor de temperatura 0-100 °C, 4-20 mA, con sensor PT100 para la termovaina 3/4\" NPT (pos 18)",
                             "2b": "Tubing AISI 316 3/8\" y conectores de doble virola para las señales de 4 reguladoras (≈ 4 × 3 m), confirmar con el diagrama de conexionado del fabricante"},
                   "proveedores": MARCAS,
                   "cantidad_compra": {"21": "media tira de 6 m", "22": "media tira de 6 m", "23": "media tira de 6 m", "24": "media tira de 6 m"},
                   "servicios": [{"servicio": "Radiografía 100% (≈ 136 placas, 4 visitas)", "proveedores": "proveedor de RX (tarifa confirmada por Matías 30-10-2026)", "referencia": "ARS 850.000 por visita + ARS 15.000 por placa", "nota": ""},
                                 {"servicio": "Líquidos penetrantes y procedimientos de END (RX y LP)", "proveedores": "DB NDT / Antonelli", "referencia": "LP 294 (DB NDT 08-2026); procedimiento 250 c/u (Antonelli 11-2025)", "nota": ""},
                                 {"servicio": "Flete a Tapiales con hidrogrúa", "proveedores": "a definir", "referencia": "sin referencia", "nota": ""}]}
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- oferta.json (textos comunes del concurso en camuzzi_comun.py)
import camuzzi_comun  # noqa: E402
camuzzi_comun.oferta(C, "COT26-0135-001", "Skid de regulacion", 2, "skid de regulación / medición según plano SCE-RE-315-0048 y especificación SCE-RE-515-0032", "1",
                     base["plazo"]["dias"],
                     ["Concurso de precios N° 24578: planilla de cotización, cláusulas particulares (01-10-2026) y condiciones generales", "Plano mecánico SCE-RE-315-0048 rev A (rótulo; el archivo se llama SCERE3150048-0)",
                      "Especificación técnica SCE-RE-515-0032 (19-10-2026)", "Listado de marcas y proveedores SCE-IN-501-0015 rev 1 (10-02-2026)"],
                     "Salto de regulación de presión sobre skid: 2 ramas 3\" #150 con monitora y reguladora pilotadas, colector de entrada 6\" y de salida 8\". Pe 15-10 bar, Pr 4 bar, Q 1.000-6.000 Sm3/h. RX 100%, PH según NAG-124, prueba de fugas a 5,5 bar, protección anticorrosiva SCE-PC-511-0003.",
                     ["Largos de caño (pos 21 a 24): el plano no indica cantidad; ITT los midió del dibujo (*).",
                      "Se cotiza sobre el plano SCE-RE-315-0048 revisión A (emitido para calificación según la especificación 3.2) y la especificación SCE-RE-515-0032 del 19-10-2026.",
                      "Reguladoras y monitoras: de un modelo homologado en el listado SCE-IN-501-0015 (solapa Válvulas Reguladoras), sujeto a la aprobación previa de Camuzzi (especificación 5.6.1).",
                      "Se agregan las cuplas para soldar 1/2\" y 3/4\" NPT serie 3000 ASTM A-105 de las conexiones de las pos 15, 16, 18, 19 y A, que la tabla del plano no lista.",
                      "Juntas y espárragos de las uniones internas del equipo según la nota del plano (SCE-IN-301-0001/2).",
                      "Precio entregado en Transporte Cruz del Sur según las cláusulas particulares y la planilla de cotización."],
                     ["Ingeniería de fabricación y documentación para aprobación (cronograma, listado de documentos, planos, hoja de datos de instrumentos, mapa y planilla de soldaduras, procedimientos y calificaciones).",
                      "Suministro de materiales, juntas y espárragos internos.",
                      "Prefabricado, armado y soldadura en taller; montaje de reguladoras y conexionado de pilotos.",
                      "Radiografía 100% y tintas penetrantes; prueba hidráulica de los prefabricados y prueba de fugas.",
                      "Protección anticorrosiva según SCE-PC-511-0003.", "Data book (copia digital, CD y copia en papel) y certificados; placa de identificación.",
                      "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
print(len(base["items"]), "ítems · soldadura", round(pulg, 2), "pulg-eq · RX", placas, "placas,", visitas, "visitas")
# Garantía: CGP 13.1 (18 meses desde la entrega) y ET §9 (2 años desde la entrega o 1 desde la instalación, lo primero; vicios ocultos sin límite).
# La de camuzzi_comun solo cita la ET y puede quedar por debajo de los 18 meses del CGP (auditoría 30-10-2026).
o = json.load(open(C / "oferta.json", encoding="utf-8"))
o["garantia"] = ("Garantía general por el plazo que resulte mayor entre 18 meses desde la entrega (Pliego de Cláusulas Generales, art. 13.1) y 2 años desde la "
                 "entrega o 1 año desde la instalación, lo que ocurra primero (especificación SCE-RE-515-0032, punto 9); responsabilidad por vicios ocultos de "
                 "fabricación sin límite de tiempo (especificación, punto 9); más las garantías particulares de materiales e instrumentos.")
json.dump(o, open(C / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
