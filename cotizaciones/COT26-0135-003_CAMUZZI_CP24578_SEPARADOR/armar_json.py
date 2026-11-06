"""Separador vertical coalescente (CP 24578 ítem 1 y Concurso 24527, 2 un) sobre el PLANO TIPO de Camuzzi SCE-RE-112-0001 rev. 1
("Separador vertical coalescente", circular del 05-11-2026: pedido/circulares_2026-11-05/). Reemplaza el diseño propio de ITT
(armar_json_diseno_preliminar_2026-10.py: 55", 37 elementos, 2 1/4", 102 bar), decisión de Matías del 05-11-2026.

Base adoptada (Matías, 05-11-2026): A = serie #600 (Pe máx 70 bar) y B = 20 cartuchos, la última fila de la tabla. Motivo: la planilla
pide entrada y salida "preferentemente 10\" #600" y en la tabla #600 la tobera D1 de 10" aparece solo con B = 17 y 20; se toma 20 por
margen para la pérdida de carga de 100 mbar (ET 9.1). La cantidad se confirma con la ficha del cartucho (consulta al cliente del 05-11-2026).

Fila #600 / B = 20 de la tabla del plano: C1 36" (914 mm), C2 31,75 mm (chapa G° 70), D1 10" (caño sch 80 A-53 G° B), E1 6" (caño sch 80),
G1 480 / G2 25,4 mm, H1 290 / H2 25,4 mm, I1 900, I2 570, J3 570, L1 220, M1 1.515, M2 2.365 mm.
Parámetros de diseño del plano (serie 600): presión de diseño 70 bar, PH 91 bar, corrosión 1,6 mm, RX 100 % tope, LP 100 % filete, ASME VIII Div. 1.

Las descripciones, materiales y medidas de la lista son las del plano, literales (REGLA CRÍTICA); lo que resuelve ITT (valores de la tabla,
cantidades que el plano no da) va en la nota y en cantidad_origen. Es la ÚNICA fuente de cotizacion.json y oferta.json.
Correr: python cotizaciones/COT26-0135-003_CAMUZZI_CP24578_SEPARADOR/armar_json.py"""
import csv
import json
import math
import sys
from pathlib import Path

C = Path(__file__).resolve().parent
sys.path.insert(0, str(C.parent / "COT26-0135-001_CAMUZZI_CP24578_SKIDREG"))
import camuzzi_comun  # noqa: E402
sys.path.insert(0, str(C.parents[1] / "herramientas"))
from numeros import fmt  # noqa: E402

PLANO = "SCE-RE-112-0001 rev. 1"
B = 20
C1_MM, C2_MM = 914, 31.75
G1, G2, H1, H2, I1, I2, J3 = 480, 25.4, 290, 25.4, 900, 570, 570
M1, M2 = 1515, 2365
TABLA = (f"tabla del plano para A = #600 y B = {B}: C1 = 36\" ({C1_MM} mm), C2 = {fmt(C2_MM)} mm (chapa G° 70), D1 = 10\" (caño sch 80 A-53 G° B), "
         f"E1 = 6\" (caño sch 80), G1 = {G1} / G2 = {fmt(G2, 1)} mm, H1 = {H1} / H2 = {fmt(H2, 1)} mm, I1 = {I1}, I2 = {I2}, J3 = {J3}, M1 = {M1}, M2 = {M2} mm")
CANT_ITT = f"El cliente no indica cantidad: calculada por ITT según el plano {PLANO} (dibujo y tabla para #600 / B = {B})"

# ---- pesos (para precios por kg, fabricación por kg y pintura) ----
DM = (C1_MM - C2_MM) / 1000           # diámetro medio de la envolvente (m)
L_ENV = 3.3                           # m: corte A-A, M1 + M2 = 3.880 mm de la base a la brida de la tapa, menos ≈ 470 mm de la base a la tangente del cabezal y el cuello de la tapa (revisión 05-11-2026: antes 3,0 m con 890 mm)
kg_env = round(math.pi * DM * L_ENV * C2_MM / 1000 * 7850)
kg_cab = round((1.084 * DM ** 2 + math.pi * DM * 0.05) * C2_MM / 1000 * 7850)    # cabezal 2:1 + pestaña de 50 mm
T_PLACAS = 19.05                      # placa portacartuchos y placa guía superior (corte A-A; el plano no da el espesor: criterio ITT)
kg_placas = round(2 * math.pi / 4 * 0.85 ** 2 * T_PLACAS / 1000 * 7850)
kg_disco_g = round(math.pi / 4 * ((G1 / 1000) ** 2 - 0.273 ** 2) * G2 / 1000 * 7850, 1)
kg_disco_h = round(math.pi / 4 * ((H1 / 1000) ** 2 - 0.1683 ** 2) * H2 / 1000 * 7850, 1)
H_FALDON = 0.405
kg_faldon = round(math.pi * DM * H_FALDON * 9.53 / 1000 * 7850 + math.pi / 4 * ((C1_MM + 200) ** 2 - (C1_MM - 10) ** 2) / 1e6 * 0.01905 * 7850 + 8)  # esquema faldón: 3/8" × 405 mm + anillo base Ø C1 + 200 de 3/4" + 4 refuerzos
M_UPN120, M_UPN80 = 12, 30                                                        # m: skid (vista superior) y estructura de la tarima (vista lateral)
kg_skid = round(M_UPN120 * 13.4 + M_UPN80 * 8.64)
KG_TARIMA_EXTRA = 150                                                              # escalera protegida y barandas (pos 25), sin la rejilla
M2_REJILLA = 1.35                                                                  # piso de la tarima ≈ 1,5 × 0,9 m (vista superior)
KG_CONEX = 260                                                                     # bridas y niples 10" y 6", toberas 1", cuplas (controles_tablas.md)
kg_fabricado = kg_env + kg_cab + kg_placas + 2 * kg_disco_g + kg_disco_h + kg_faldon + kg_skid + KG_TARIMA_EXTRA + KG_CONEX
# Soldadura extra por espesor (31,75 mm frente a la pared ≈ 10 mm de los presupuestos de Ledesma de AESA/44): regla de factores_soldadura.csv
F_ESP = C2_MM / 9.53
PULG_CUERPO = 3 * 36 + 2 * L_ENV / 2 * 1000 / math.pi / 25.4      # cabezal–envolvente, unión de las 2 virolas, cuello de la tapa + 2 longitudinales
PULG_TOBERAS = 2 * 10 + 6
pulg_extra = round((PULG_CUERPO + PULG_TOBERAS) * (F_ESP - 1), 1)
TC_OCT = 1543.23       # BNA venta, promedio 10-2026 (conocimiento/costos/dolar_mensual.csv)
UPN_KG = 16.95 / 13.4  # Provemet cot. 288977 ítem 2 (29-10-2026): UPN 120 a 16,95 USD/m, 13,40 kg/m


def fuente(tipo, precio, prov, origen, fecha, coincide="similar", dif=""):
    f = {"tipo": tipo, "precio": round(precio, 2), "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        f["diferencia"] = dif
    return f


def sin_precio(prov, dif, fecha="2026-11-05"):
    return {"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: " + prov, "origen": "—", "fecha": fecha, "coincide": "sin_ref", "diferencia": dif}


S12 = "fuentes_originales/ofertas_texto/Sacde/12-2970-SE-PTG-008 - FILTRO COALESCENTE - Pedido de precios/4.Armado de la Oferta Comercial/LM costos Filtro Coalecedor FC 301 y 302 #600 PC0-C.xlsx.txt"
T37 = "fuentes_originales/ofertas_texto/TAVAL/37- Doc5449458609 - RFP 1 Sobre - Filtro Coales (COMPRA)/4.Armado de la Oferta Comercial/LM costos Coalescedor FC-231 YPF - PC0-C (REV. 0).xlsx.txt"
T40 = "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt"
C30 = "fuentes_originales/ofertas_texto/CAMUZZI/30 - Separador Polvo y Líquido (2 unid) - Lic 22737/5.Proveedores 3ros/"
A44 = "fuentes_originales/ofertas_texto/AESA/44-Doc5319481557 - AESA - SRV FABRICACION EQUIPOS - F5064/"
C14 = ("fuentes_originales/ofertas_texto/CAMUZZI/14_#5067 - (CGP 6910  CGS 6911) - Estaciones de medición y regulación/4.Armado de la Oferta Comercial/6910/"
       "Planilla de Costo- Salto de Regulación_6910 rev 2.xlsx.txt")
PVC = "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf"
PVB = "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288978_bridas_2026-10-29.pdf"
PVP = "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288977_perfiles_2026-10-29.pdf"
REN = "fuentes_originales/renar_lista_2025-12.xlsx"
CAT = "conocimiento/precios/catalogo_materiales.csv"
NOTA_PV = "Provemet: precio neto con bonificación 4 % por compra total de la cotización, validez 15 días (hasta 13-11-2026)"
CHAPA = fuente("ant", 1.80, "Planilla Sacde/12 coalescedor FC-301/302: chapa SA-516-70 1 1/2\" a 1,80 USD/kg", S12, "2025-12-18", "similar",
               "espesor 1 1/2\" (acá 31,75 mm); temperatura mínima de diseño sin dato (consulta C4): si exige normalizada (70N) cambia el precio")
CHAPA_A36 = fuente("ant", 1.2744, "Chapa negra A36 (precios de acero por kg, J. Elejondo) +10 % recortes", "conocimiento/precios/acero_por_kg.csv", "2026-02-10", "similar", "chapa 1/2\" de la lista")

# REF., descripción literal, MATERIAL, Øn, SERIE / SCH (literales del plano) · cantidad, unidad · nota ITT · fuentes · [motivo sin precio]
M = [
    ("01", "Envolvente", "C2", "C1", "C2", round(kg_env * 1.1), "kg",
     f"C1 = 36\" ({C1_MM} mm), C2 = chapa G° 70 de {fmt(C2_MM)} mm (SA-516 Gr. 70); 2 virolas de {fmt(L_ENV / 2, 2)} m ({fmt(kg_env, 0)} kg + 10 % de recortes)", [CHAPA]),
    ("01b", "Placa portacartuchos y placa guía superior (dibujadas en el corte A-A; el plano no las lista ni da su espesor)", "SA-516 Gr. 70", "", "", round(kg_placas * 1.1), "kg",
     f"Agregado de ITT: 2 placas Ø 850 mm × {fmt(T_PLACAS)} mm (criterio ITT, a verificar en la memoria) con {B} agujeros", [CHAPA]),
    ("02", "Cabezal semielíptico (2:1)", "C2", "C1", "C2", 1, "un", f"Ø 36\" × {fmt(C2_MM)} mm SA-516 Gr. 70 (≈ {fmt(kg_cab, 0)} kg)",
     [fuente("ant", 3000 * C2_MM / 38.1, "Planilla Sacde/12: cabezal 36\" × 1 1/2\" SA-516-70 a 3.000, por el espesor (31,75 ÷ 38,1)", S12, "2025-12-18", "similar", "mismo Ø (36\"), otro espesor: pedir cotización")]),
    ("03", "Tapa de apertura rápida", "--", "C1", "A", 1, "un", "36\" serie #600, no roscada, con pescante (ET 9.7); marcas del listado: Futura, Peco, Gora o EKA",
     [fuente("ant", 24288.60, "Planilla Sacde/12: tapa de cierre rápido Futura 36\" #600 con pescante (oferta Futura, plazo 120 días)", S12, "2025-12-18", "igual", "misma medida y serie; precio de 12-2025: reconfirmar con Futura")]),
    ("04", "Niple de conexión", "D1", "D1", "D1", 0.7, "m", "D1 = 10\" caño sch 80 A-53 G° B (sin costura, triple certificación); 2 toberas de ≈ 350 mm",
     [fuente("cot", 168.01, "Grupo Provemet cot. 288974 ítem 12 · CAN-01420", PVC + " · ítem 12", "2026-10-29", "igual", "TUBO S/C PSL2 ASTM A53/A106/API5L B 10'' SCH 80 Ø 273 X 15,09 mm (cumple A-53 G° B); " + NOTA_PV)]),
    ("05", "Brida Welding-Neck", "ASTM A-105", "D1", "A", 2, "un", "10\" #600 RF sch 80 (entrada y salida a 180°)",
     [fuente("cot", 301.86, "Grupo Provemet cot. 288978 ítem 12 · BRI-04996", PVB + " · ítem 12", "2026-10-29", "igual", "Brida Welding Neck Sch 80 Raised Face Serie 600 ASTM A 105 ANSI B16.5 10\"; validez 15 días; marca del listado (Francovigh / CH / Thorsa / Forja Atlas)")]),
    ("06", "Niple de conexión", "E1", "E1", "E1", 0.3, "m", "E1 = 6\" caño sch 80 A-53 G° B (boca de inspección)",
     [fuente("cot", 74.52, "Grupo Provemet cot. 288974 ítem 10 · CAN-01512", PVC + " · ítem 10", "2026-10-29", "igual", "TUBO S/C ASTM A53/A106/API5L B 6'' SCH 80 Ø 168,3 X 10,97 mm; " + NOTA_PV)]),
    ("07", "Brida Welding-Neck", "ASTM A-105", "E1", "A", 1, "un", "6\" #600 RF sch 80 (boca de inspección)",
     [fuente("cot", 112.28, "Grupo Provemet cot. 288978 ítem 8 · BRI-01321", PVB + " · ítem 8", "2026-10-29", "igual", "Brida Welding Neck Sch 80 Raised Face Serie 600 ASTM A 105 ANSI B16.5 6\"; validez 15 días")]),
    ("08", "Disco de refuerzo", "C2", "G1", "G2", 2, "un", f"G1 = Ø {G1} mm, G2 = {fmt(G2, 1)} mm, SA-516 Gr. 70 ({fmt(kg_disco_g, 1)} kg c/u), toberas D1",
     [fuente("ant", kg_disco_g * 1.80, f"{fmt(kg_disco_g, 1)} kg × 1,80 USD/kg (chapa SA-516-70, planilla Sacde/12)", S12, "2025-12-18", "similar", "solo la chapa; el corte va en la fabricación")]),
    ("09", "Disco de refuerzo", "C2", "H1", "H2", 1, "un", f"H1 = Ø {H1} mm, H2 = {fmt(H2, 1)} mm, SA-516 Gr. 70 ({fmt(kg_disco_h, 1)} kg), tobera E1",
     [fuente("ant", kg_disco_h * 1.80, f"{fmt(kg_disco_h, 1)} kg × 1,80 USD/kg (chapa SA-516-70, planilla Sacde/12)", S12, "2025-12-18", "similar", "solo la chapa")]),
    ("10", "Perfil normalizado de acero al carbono UPN-120", "ASTM A-36", "--", "--", M_UPN120, "m", "skid (vista superior y vista lateral); metros medidos por ITT",
     [fuente("cot", 16.95, "Grupo Provemet cot. 288977 ítem 2: perfil UPN 120 (13,40 kg/m) a 16,95 USD/m", PVP + " · ítem 2", "2026-10-29", "igual", NOTA_PV.replace("4 % ", ""))]),
    ("11", "Perfil normalizado de acero al carbono UPN-80", "ASTM A-36", "--", "--", M_UPN80, "m", "estructura de la tarima (columnas y vigas, vista lateral); metros estimados por ITT",
     [fuente("cot", 8.64 * UPN_KG, "UPN 80 (8,64 kg/m) al precio por kg del UPN 120 de Provemet cot. 288977 (1,26 USD/kg)", PVP + " · ítem 2", "2026-10-29", "similar", "Provemet no cotizó el UPN 80: precio por kg del UPN 120")]),
    ("12", "Media cupla p/soldar", "ASTM A-105 G° B", "2\"", "6000", 2, "un", "interruptores de nivel (pos 16), una por cámara",
     [fuente("cot", 7.26, "Provemet: cupla 1\" NPT 6000# ASTM A-105 (AFO-03328)", CAT, "2025-07-29", "similar", "otra medida (1\") y cupla entera: pedir media cupla 2\" 6000 (CH / Thorsa / Forja Atlas)")]),
    ("13", "Media cupla p/soldar", "ASTM A-105 G° B", "1\"", "6000", 3, "un", "drenaje inferior del cabezal (rotulada en el plano) y salidas a las 2 válvulas automáticas (supuesto ITT: el dibujo no las rotula)",
     [fuente("cot", 7.26, "Provemet: cupla 1\" NPT 6000# ASTM A-105 (AFO-03328)", CAT, "2025-07-29", "similar", "cupla entera en lugar de media cupla (precio de más)")]),
    ("14", "Media cupla p/soldar", "ASTM A-105 G° B", "1/2\"", "6000", 4, "un", "2 por indicador de nivel (pos 23)",
     [fuente("cot", 3.99, "Provemet: cupla 1/2\" NPT 6000# ASTM A-105 (AFO-03327)", CAT, "2025-07-29", "similar", "cupla entera en lugar de media cupla (precio de más)")]),
    ("15", "Faldon de Apoyo (segun detalle)", "ASTM A-36", "C1", "--", kg_faldon, "kg", "esquema faldón: chapa 3/8\" Ø 36\" × 405 mm, anillo base Ø C1 + 200 mm de 3/4\", 4 refuerzos y orificios de 3/4\"", [CHAPA_A36]),
    ("16", "Interruptor neumático de nivel", "--", "2 \"", "B", 2, "un", "uno por cámara; comanda la válvula automática (ET 9.2)",
     [fuente("ant", 2500, "Planilla Sacde/12 FC-301/302: switch de nivel 2\" NPT 3000# (4 u a 2.500)", S12, "2025-12-18", "similar", "sin modelo ni accionamiento neumático: pedir a Epta / Fisher / Magnetrol / Kimray")]),
    ("17", "Niple", "ACERO AL CARBONO", "4 \"", "40", B, "un", f"uno por cartucho (detalle conjunto soporte), largo J3 = {J3} mm",
     [fuente("lista", 34.34 * J3 / 1000, f"Caño 4\" sch 40 sin costura A53/A106/API 5L B, Renard cód. 1160 (34,34 USD/m) × {J3 / 1000} m", REN + " · código 1160", "2025-12-26", "similar", "precio del caño por metro; el corte va en la fabricación")]),
    ("18", "Cartucho filtrante de papel de 5½\" x 36\", cantidad \"B\"", "--", "--", "--", B, "un", f"B = {B} (base adoptada; confirmar con la ficha del cartucho: consulta del 05-11-2026)",
     [fuente("cot", 113.83, "Gora PPTO 27131 (11-02-2026, pedido para el separador de CAMUZZI/30): elemento separador de polvo y líquido para gas natural, fibra de vidrio, código Gora 46600, 113,83 c/u", C30 + "GORA - PPTO 27131 - ITT.pdf.txt", "2026-02-11", "similar",
              "la cotización no dice la medida y es de fibra de vidrio (el plano pide papel): referencia débil, es el renglón que más puede mover el precio; pedir a Gora el cartucho de papel 5½\" × 36\" con su caudal a 25 bar")]),
    ("18b", "Juego adicional de cartuchos filtrantes de repuesto (ET 13.1)", "--", "--", "--", B, "un", "compra extra: un juego de repuesto por equipo",
     [fuente("cot", 113.83, "Gora PPTO 27131: mismo elemento que la pos 18", C30 + "GORA - PPTO 27131 - ITT.pdf.txt", "2026-02-11", "similar", "mismo que la pos 18")]),
    ("19", "Caja de chicana de acero inoxidable de dimensiones \"I1\"x \"I1\" X \"I2\" (según detalle)", "--", "--", "--", 1, "un", f"I1 × I1 × I2 = {I1} × {I1} × {I2} mm, AISI 304 (ET 9.8)",
     [fuente("cot", 615 * (I1 / 250) ** 2, f"Gora PPTO 27131: caja de chicanas doble bolsillo 250 × 250 × 150 AISI 316 a 615, por el área de paso ({I1} × {I1} ÷ 250 × 250 = {fmt((I1 / 250) ** 2, 2)})", C30 + "GORA - PPTO 27131 - ITT.pdf.txt", "2026-02-11", "similar",
              "escalada por tamaño (estimado): pedir a Gora con las medidas del plano")]),
    ("20", "Válvula automática", "ASTM A-216 G° B", "1 \"", "A", 2, "un", "1\" #600 bridada RF, neumática normal cerrada, internos inox, cierres stellite 6 (ET 9.2)",
     [sin_precio("pedir cotización (actuador Bettis / Bray / Flow / Wenlen)", "la única referencia (Sacde/12, 2.000) no dice el material ni los internos", "2026-10-30")],
     "Sin referencia con el material pedido: pedir cotización (lista para Compras)"),
    ("21", "Válvula esférica de pasaje total", "ASTM A-216 G° B", "1 \"", "A", 2, "un", "1\" #600 RF: by-pass de la purga superior y bloqueo del drenaje inferior (ET 9.2)",
     [sin_precio("pedir cotización a una marca del listado", "la referencia (Taval 1\" #600, 162, Sacde/12) no dice el material", "2026-10-30")],
     "Sin referencia en A216 WCB: pedir cotización (lista para Compras)"),
    ("22", "Válvula tapon lubricado", "ASTM A-216 G° B", "1 \"", "A", 1, "un", "1\" #600 RF de sacrificio (drenaje inferior, ET 9.2); Xomox-Tufline / Nordstrom / Favra",
     [sin_precio("pedir cotización", "solo hay tapón 1\" NPT S-3000: otra serie no es referencia", "2026-10-29")],
     "Sin referencia de la misma serie: pedir cotización (lista para Compras)"),
    ("23", "Indicador de nivel de vídrio (tipo Penberthy \" Reflex\" o similar)", "--", "--", "A", 2, "un", "uno por cámara, reflex 500 mm, apto 70 bar (presión de diseño del plano)",
     [fuente("cot", 685, "Riva Hnos (12-02-2026): indicador de nivel reflex 500 mm, conexiones roscadas, presión de trabajo 70 bar", C30 + "Riva Hnos - Cotización de indicadores de nivel.msg.txt", "2026-02-12", "similar", "misma presión (70 bar); sin las válvulas de bloqueo y purga (van en la pos 23b); validez 4 semanas vencida: reconfirmar")]),
    ("23b", "Válvulas de bloqueo y purga de los indicadores de nivel (ET 9.9)", "A105", "1/2\"", "2000", 8, "un", "compra extra: 4 por indicador",
     [fuente("lista", 36.06, "Precio de referencia: Taval 1/2\" #2000 NPT A105 paso total API 608 forjada (Lista 30 × 0.52) · VAL-04865", "fuentes_originales/taval_lista30_2025-09.xlsx", "2025-09-01", "similar", "Taval no está en el listado de Camuzzi: comprar marca del listado")]),
    ("24", "Chapa de identificación (según detalle)", "ASTM A240 - 304", "--", "--", 1, "un", "detalle de chapa de identificación del plano",
     [fuente("ant", 15, "Planilla Sacde/12: chapa de identificación 100 × 200 × 3 mm AISI 316 · PER-03051", S12, "2025-12-18", "similar", "AISI 316 (superior al 304); la del plano es más grande y grabada")]),
    ("25", "Tarima con escalera protegida y barandas de seguridad", "--", "--", "--", 1, "gl", f"rejilla antideslizante galvanizada {fmt(M2_REJILLA, 2)} m² + escalera protegida y barandas ≈ {KG_TARIMA_EXTRA} kg (la estructura es la pos 11)",
     [fuente("ant", M2_REJILLA * 265 + KG_TARIMA_EXTRA * UPN_KG, f"rejilla TDL a 265 USD/m² (planilla TAVAL/37) × {fmt(M2_REJILLA, 2)} m² + {KG_TARIMA_EXTRA} kg de perfiles a 1,26 USD/kg (Provemet 288977)", T37, "2025-12-17", "similar", "kilos y m² estimados del plano; el galvanizado va en S05b")]),
    ("26", "Manómetro de presión estática con mánifold de 2 vías", "--", "--", "--", 1, "un", "ET 9.19.1: Ø100, clase 1, glicerina, caja AISI 304, bourdon AISI 316, certificado de calibración",
     [sin_precio("pedir cotización a Weisz / Wika con la ET 9.19.1", "la referencia (Weisz 120, PAMPA/7) no dice los materiales que pide la ET", "2026-10-30")],
     "La referencia no dice caja ni bourdon: pedir cotización (lista para Compras)"),
    ("27", "Manómetro de presión diferencial con mánifold de 3 vías", "--", "--", "--", 1, "un", "0-2 bar, aguja de arrastre y contacto seco (planilla y ET 9.19.2); Wika + manifold ABAC / Casucci",
     [fuente("ant", 500 + 170, "Weisz: manómetro diferencial 0-2 bar 500 (INS-02695) + manifold de 3 vías ABAC M1-C-T 170 (planilla TAVAL/40)", T40, "2026-01-15", "similar", "sin aguja de arrastre ni contacto seco: pedir a Wika")]),
    ("28", "Brida Ciega (con junta espiralada de acero inoxidable)", "ASTM A-105", "E1", "A", 1, "un", "6\" #600 RF con junta espiralada AISI 316 (boca de inspección)",
     [fuente("cot", 172.28 + 7, "Provemet cot. 242356: brida ciega 8\" RF #600 ASTM A105 (BRI-01064, 172,28) + junta espiralada 6\" #600 (planilla TAVAL/37, 7)", CAT, "2025-08-27", "similar", "8\" (pedido 6\"): no hay ciega de 6\" #600 en el catálogo; se toma la medida mayor")]),
    ("29", "Arandela y guia para apoyo de elementos filtrantes", "ASTM A-36", "--", "--", B, "un", "una por cartucho (detalle conjunto soporte), ≈ 1,5 kg c/u",
     [fuente("ant", 1.5 * 1.2744, "1,5 kg × chapa A36 a 1,27 USD/kg (acero_por_kg.csv)", "conocimiento/precios/acero_por_kg.csv", "2026-02-10", "similar", "kilos estimados")]),
    ("30", "Valvula reguladora de presion 1301F NPT con manometro", "ASTM A-216 G°WCB", "1/4", "3000", 1, "un", "gas de instrumentos para las válvulas automáticas (Fisher 1301F)",
     [sin_precio("pedir cotización (Fisher / Emerson)", "no hay regulador 1301F en el catálogo")], "Sin referencia en el catálogo: pedir cotización (lista para Compras)"),
    ("31", "Valvula de alivio NPT (Tipo S-70)", "ASTM A-216 G°WCB", "1/4", "3000", 2, "un", "alivio de los reguladores de gas de instrumentos",
     [fuente("est", 465, "Planilla de costo ITT, salto Camuzzi ERP Caseros (CAMUZZI/14, renglón 48: válvula de alivio tipo S70 / H200 1/2\" 3000 LB, 465)", C14, "2022-03-15", "similar", "1/2\" (pedido 1/4\") y precio de 2022 (período con cepo): pedir a Farinola / Favra / Aerre")]),
    ("32", "Conector TE NPT", "ASTM A-105", "1/4", "3000", 3, "un", "",
     [fuente("lista", 8.69, "Renard (cód. 6042) · Tee 1/4\" NPT S3000 ASTM A105 · AFO-00866", REN + " · código 6042", "2025-12-26", "igual")]),
    ("33", "Valvula reguladora de presion 67FR NPT con manometro", "--", "1/4", "3000", 1, "un", "segunda etapa del gas de instrumentos (Fisher 67FR)",
     [sin_precio("pedir cotización (Fisher / Emerson)", "no hay regulador 67FR en el catálogo")], "Sin referencia en el catálogo: pedir cotización (lista para Compras)"),
    ("34", "Tubing de acero inoxidable c/ conectores NPT", "AISI 316", "--", "--", 1, "gl", "≈ 12 m de tubing 1/4\" y 12 conectores de doble virola (ET 9.20)",
     [fuente("ant", 12 * 7 + 12 * 15, "ABAC (planilla TAVAL/40): tubing 1/4\" × 0,89 mm a 7 USD/m × 12 m + conector doble virola 1/4\" NPT a 15 × 12", T40, "2026-01-15", "similar", "metros y conectores estimados del dibujo")]),
    ("35", "Caño de acero", "ASTM A-53 G°B", "1", "80", 8, "m", "drenajes y purgas (vista lateral); metros medidos por ITT",
     [fuente("lista", 8.64, "Renard (cód. 1128) · Tubo s/costura 33,4 × 4,55 mm A53/A106/API 5L B · CAN-01395", REN + " · código 1128", "2025-12-26", "similar", "sin costura, triple certificación: cumple A-53 G° B")]),
    ("36", "TE", "ASTM A-234 G°WPB", "1", "80", 4, "un", "",
     [fuente("lista", 18.38, "Renard (cód. 3797) · Tee 1\" XS ASTM A234 WPB · ABW-00334", REN + " · código 3797", "2025-12-26", "igual")]),
    ("37", "Codo de radio largo", "ASTM A-234 G°WPB", "1", "80", 4, "un", "",
     [fuente("lista", 4.49, "Renard (cód. 3769) · Codo Radio Largo 90° 1\" XS ASTM A234 WPB · ABW-00083", REN + " · código 3769", "2025-12-26", "igual")]),
    ("38", "Brida W.N.", "ASTM A-105", "1", "A", 11, "un", "1\" #600 RF sch 80: 2 por válvula bridada (pos 20, 21, 22) y salida del drenaje",
     [fuente("ant", 26.54, "Renard: brida Welding Neck 1\" RF sch 80 600# ASTM A 105 · BRI-01202", CAT, "2025-07-11", "igual", "marca del listado (Francovigh / CH / Thorsa / Forja Atlas)")]),
    ("38b", "Juntas espiraladas 1\" #600 AISI 316 / grafito de las uniones bridadas de purgas y drenajes, más un segundo juego (ET 9.16.3)", "AISI 316 / grafito", "1\"", "600", 22, "un", "compra extra: 11 uniones × 2 juegos",
     [fuente("ant", 5, "Planilla TAVAL/37 FC-231: junta espiralada 1\" #600 c/anillo ext. a 5", T37, "2025-12-17", "similar", "valor de planilla ITT")]),
    ("38c", "Espárragos ASTM A193 B7 con 2 tuercas A194 2H zincados para las uniones bridadas 1\" #600 (ET 9.13)", "A193 B7 / A194 2H", "5/8\"", "", 44, "un", "compra extra: 11 uniones × 4",
     [fuente("cot", 1.04, "Oil Metal cot. 37278: espárrago 5/8\" × 90 mm zinc con 2 tuercas, gr B7 · JUN-05014", "fuentes_originales/listas_vendedor/2026-11-05/oilmetal_cotizacion_37278_2026-10-30.pdf", "2026-10-30", "similar", "1\" #600 lleva 5/8\" × 4 1/4\" (108 mm): pedir el largo")]),
    ("39", "Cancamo de Izaje", "ASTM A-36", "--", "--", 4, "un", "2 en el cuerpo y 2 en el skid (vista lateral)",
     [fuente("ant", 5 * 1.2744, "≈ 5 kg × chapa A36 a 1,27 USD/kg", "conocimiento/precios/acero_por_kg.csv", "2026-02-10", "similar", "kilos estimados")]),
]

# ---- transcripción textual de la tabla del plano (fuente de la regla crítica) y lista de materiales ----
tabla = [[r[0], r[1], r[2], r[3], r[4]] for r in M if not r[0][-1].isalpha()]
json.dump({"fuente": f"Plano tipo {PLANO} «Separador vertical coalescente» (Camuzzi, 29/09/2020), recibido por circular el 05-11-2026: tabla de referencias. "
                     "Transcripción textual (pdftotext controlado contra la imagen y el recorte de Matías).",
           "lector": "A: transcripción del 05-11-2026 (texto del PDF y recorte de la tabla enviado por Matías)",
           "nota": f"Dimensiones C1, C2, D1, E1, G1, G2, H1, H2, I1, I2, J3, L1, M1, M2 según la «Tabla de dimensiones en función de A (serie ANSI) y B (cantidad de cartuchos)»; {TABLA}.",
           "tablas": [{"titulo": "REFERENCIAS", "columnas": ["REF.", "DENOMINACION Y DIMENSIONES", "MATERIAL", "Øn", "SERIE / SCH"], "filas": tabla}]},
          open(C / "pedido" / "transcripcion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(C / "pedido" / "lista_materiales_plano.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["pos", "descripcion", "diametro", "serie_sch", "material", "extremos", "modelo_fabricante", "cantidad", "unidad", "extremos_campo", "cantidad_origen", "nota"])
    for pos, desc, mat, dn, ser, q, u, nota, *_ in M:
        if pos[-1].isalpha():  # compras extra de ITT (01b, 18b…): van solo en el cómputo, no en la lista del plano
            continue
        w.writerow([pos, desc, dn, ser, mat, "", "", q, u, 0, CANT_ITT, nota])
import atributos_plano  # noqa: E402
atributos_plano.completar(C)
atributos_plano.fijar(C, {
    "01": {"familia": "PER", "tipo": "chapa", "espesor_mm": "31.75", "medida": f"envolvente Ø 36\" × {fmt(L_ENV, 1)} m", "norma": "ASME VIII Div.1"},
    "02": {"familia": "ABW", "tipo": "casquete semielíptico 2:1", "espesor_mm": "31.75", "medida": "Ø 36\"", "norma": "ASME VIII Div.1"},
    "03": {"familia": "OTR", "tipo": "tapa de cierre rápido", "serie": "600", "medida": "36\"", "marca": "Futura / Peco / Gora / EKA"},
    "18": {"familia": "OTR", "tipo": "cartucho filtrante", "medida": "5½\" × 36\" (140 × 914 mm)", "marca": "Gora / Filtron / De Nichilo / Panden / SP"},
})
items = []
for p, desc, mat, dn, ser, q, u, nota, f, *motivo in M:
    it = {"id": f"M{p}", "pos": p, "grupo": "material", "descripcion": desc, "especificacion": f"{mat} · {dn} · {ser} · {nota}".replace("-- · ", ""), "cantidad": q, "unidad": u, "fuentes": f}
    if motivo:
        it["sin_precio_motivo"] = motivo[0]
    items.append(it)

ROL = C30 + "Sandri rolado de chapa esp 1.docx.txt"
items += [
    {"id": "S01", "pos": "ROL", "grupo": "servicio", "descripcion": f"Rolado y punteado de la envolvente (2 virolas de {fmt(L_ENV / 2, 2)} m, {fmt(kg_env, 0)} kg, {fmt(C2_MM)} mm)", "especificacion": "Sandri cilindra hasta 50 mm en 2.500 mm de largo: sirve con 2 virolas",
     "cantidad": kg_env, "unidad": "kg",
     "fuentes": [fuente("cot", 2550000 / 1416.29 / 1033, "Juan y Víctor Sandri S.A.: cilindrado y punteado ARS 2.550.000 + IVA por virola de 1.033 kg de chapa de 1\" (1,74 USD/kg al BNA de 03-2026)", ROL, "2026-03-25", "similar", "chapa de 1\" (acá 1 1/4\"): pedir cotización con el espesor del plano"),
                 fuente("est", 3.7, "Tarifa interna de rolado 3,70 USD/kg (tarifas.csv, AESA/44)", "conocimiento/costos/tarifas.csv", "2025-09-30", "similar", "criterio interno, no cotización")]},
    {"id": "S02", "pos": "MO", "grupo": "mo", "descripcion": f"Fabricación del separador y del skid por tercero (armado, soldadura, toberas, internos, faldón, cáncamos, tarima y montaje sobre skid; ≈ {fmt(kg_fabricado, 0)} kg)",
     "especificacion": (f"Ledesma, recipientes a presión AESA/44: 4,15 USD/kg × {fmt(kg_fabricado, 0)} kg (envolvente {fmt(kg_env, 0)} + cabezal {fmt(kg_cab, 0)} + placas {fmt(kg_placas, 0)} + discos "
                        f"{fmt(2 * kg_disco_g + kg_disco_h, 0)} + faldón {fmt(kg_faldon, 0)} + skid y tarima {fmt(kg_skid, 0)} + escalera y barandas {KG_TARIMA_EXTRA} + conexiones {KG_CONEX}); la soldadura extra por espesor va en S02b"),
     "cantidad": kg_fabricado, "unidad": "kg",
     "fuentes": [fuente("cot", 37200 / 8967, "Edgardo Ledesma, presupuesto 20079 (desgasificador, USD 37.200 + IVA, 8.967 kg): virolas, soldaduras, casquetes, conexiones, refuerzos, internos, paso de hombre, escalera y plataforma",
                         A44 + "5.Proveedores 3ros/Presupuesto ITT N° 20079 Desgasificador SB - 211 27-08-25.docx.txt", "2025-08-27", "similar",
                         "recipiente de pared fina (≈ 10 mm): la diferencia por espesor va en S02b; no incluye consumibles (S02c), rolado ni PH. Pedir a Ledesma la cotización con el plano tipo"),
                 fuente("cot", 13000, "Edgardo Ledesma: separador de polvo y líquido 28\" #600 + skid, USD 13.000 (sin plegado de cunas, PH ni END)", C30 + "E Ledesma - Cotización de Separador de polvo y líquido 28_ #600.pdf.txt", "2026-05-10", "similar",
                         "control: equipo de 28\" horizontal de Camuzzi (mismo cliente y serie)")]},
    {"id": "S02b", "pos": "MOE", "grupo": "mo", "descripcion": f"Soldadura extra del recipiente por espesor ({fmt(C2_MM)} mm en lugar de la pared ≈ 10 mm de la referencia de Ledesma): {fmt(pulg_extra, 1)} pulgadas equivalentes",
     "especificacion": f"cuerpo {fmt(PULG_CUERPO, 1)} pulg (3 circunferenciales de 36\" y 2 longitudinales) + toberas {PULG_TOBERAS}\" × (factor {fmt(F_ESP, 2)} − 1)",
     "cantidad": pulg_extra, "unidad": "pulg-eq",
     "fuentes": [fuente("est", 12, "J. C. Quesada, USD 12 por pulgada equivalente (presupuesto JQ-020-2026; incluye consumibles y calificación ASME IX) × pulgadas extra por espesor (factores_soldadura.csv: espesor ÷ 9,53)",
                         "fuentes_originales/ofertas_texto/TAVAL/58 - Inarteco - ERPs tipo 1ra etapa - Litoral Gas/5.Proveedores 3ros/Cotizacion JQ-020-2026.pdf.txt", "2026-05-06", "similar",
                         "tarifa de piping aplicada a costuras de recipiente: estimado hasta la cotización de Ledesma con el plano")]},
    {"id": "S02c", "pos": "CONS", "grupo": "mo", "descripcion": "Consumibles de soldadura de la fabricación de Ledesma (su presupuesto de AESA/44 no los incluye)", "especificacion": "", "cantidad": 1, "unidad": "gl",
     "fuentes": [sin_precio("pedir a Ledesma la cotización con consumibles", "no hay precios de electrodos ni alambre en el catálogo", "2026-10-30")],
     "sin_precio_motivo": "El presupuesto 20079 de Ledesma dice «No incluye … Consumibles» y no hay precio en el catálogo: queda en 0 hasta la cotización de Ledesma"},
]
N_PG = round((3 * math.pi * C1_MM / 1000 + L_ENV) / 0.38)  # placas grandes: costuras del cuerpo ÷ 0,38 m por placa
N_PC = 2 * 3 + 2 + 11 * 2                                   # chicas: 2 × 10" a 3, 6" a 2, 10 bridas 1" a 2
VIS = math.ceil((N_PG + N_PC) / 45)
items += [
    {"id": "S03", "pos": "RX", "grupo": "servicio", "descripcion": "Radiografía 100 % de las soldaduras a tope (plano: RADIOGRAFIADO 100 % TOPE)",
     "especificacion": f"{N_PG} placas grandes (3 circunferenciales de 36\" + 2 longitudinales ÷ 0,38 m por placa) + {N_PC} chicas (bridas WN 10\", 6\" y 1\") = {N_PG + N_PC} placas → {VIS} visitas de hasta 45 placas",
     "cantidad": 1, "unidad": "gl",
     "fuentes": [fuente("cot", VIS * round(850000 / TC_OCT, 2) + (N_PG + N_PC) * round(15000 / TC_OCT, 2), f"Proveedor de RX (sin nombre), precio confirmado por Matías el 30-10-2026: {VIS} visitas × ARS 850.000 + {N_PG + N_PC} placas × ARS 15.000, sin IVA, a BNA oct-2026 ({fmt(TC_OCT)}) · END-00572 / END-00571",
                         "conocimiento/precios/precios_usuario.csv", "2026-10-30", "similar", "placas contadas por costura: confirmar con el mapa de soldaduras")]},
    {"id": "S03b", "pos": "LP", "grupo": "servicio", "descripcion": "Tintas penetrantes 100 % de filetes (plano) y de las soldaduras que no se radiografían", "especificacion": "2 servicios (2ª y última pasada)", "cantidad": 2, "unidad": "servicio",
     "fuentes": [fuente("cot", 490, "NDT Antonelli (JCA & Asociados): líquidos penetrantes, USD 490 por servicio · END-00002", "fuentes_originales/antonelli_end_2025-11.pdf", "2025-11-03", "similar", "cantidad de servicios por criterio")]},
    {"id": "S04", "pos": "PH", "grupo": "servicio", "descripcion": "Prueba hidráulica a 91 bar (plano tipo, serie 600) durante 6 h, con registro y secado", "especificacion": "la ET 9.16.1 pide 1,3 × la presión máxima de la serie ANSI (≈ 133 bar): consulta del 05-11-2026", "cantidad": 12, "unidad": "h",
     "fuentes": [fuente("ant", 13, "Prueba hidráulica por hora de planta (END-00215, MO ITT)", "conocimiento/precios/catalogo_servicios.csv", "2026-03-10", "similar", "12 h para un recipiente de ≈ 2 m³ (llenado, 6 h de prueba, vaciado y secado)")]},
]
M2_REC = round(math.pi * C1_MM / 1000 * L_ENV + 1.0 + math.pi * C1_MM / 1000 * H_FALDON + 1.0, 1)  # envolvente + cabezal + faldón + toberas y tapa
M2_SKID = round(M_UPN120 * 13.4 / 1000 * 40, 1)                                                  # skid (la tarima va galvanizada)
M2_PIN = round(M2_REC + M2_SKID, 1)
KG_GALV = round(M_UPN80 * 8.64 + KG_TARIMA_EXTRA + M2_REJILLA * 40)
items += [
    {"id": "S05", "pos": "PIN", "grupo": "servicio", "descripcion": f"Granallado y pintura (≈ {fmt(M2_PIN, 1)} m² + 20 % de overspray)", "especificacion": f"recipiente {fmt(M2_REC, 1)} m² (envolvente, cabezal, faldón, tapa y toberas) + skid {fmt(M2_SKID, 1)} m²; × 1,2 como la planilla del precio; terminaciones SCE-PC-511-0003",
     "cantidad": round(M2_PIN * 1.2, 1), "unidad": "m2",
     "fuentes": [fuente("ant", 37.98, "Pintor (sin nombre) · PIN-00579 (precio confirmado por Matías)", "conocimiento/precios/precios_usuario.csv", "2026-10-30", "similar",
                         "granallado y pintura de piping y skid con materiales (37,98 USD/m², firme, Matías 30-10-2026), aplicado también al recipiente: a confirmar; la planilla de origen lo aplica sobre m² + 20 %")]},
    {"id": "S05b", "pos": "GALV", "grupo": "servicio", "descripcion": f"Galvanizado en caliente de la tarima, escalera, barandas y rejilla (≈ {KG_GALV} kg; vista superior: rejilla galvanizada en caliente)", "especificacion": f"UPN 80 {fmt(M_UPN80 * 8.64, 0)} kg + escalera y barandas {KG_TARIMA_EXTRA} kg + rejilla {fmt(M2_REJILLA * 40, 0)} kg",
     "cantidad": KG_GALV, "unidad": "kg", "fuentes": [fuente("ant", 2.0, "Galvanizado de terceros 2,00 USD/kg (TAVAL/49) · PIN-00465", "conocimiento/precios/catalogo_servicios.csv", "2026-03-10", "similar", "kilos estimados")]},
    {"id": "S05c", "pos": "FUG", "grupo": "servicio", "descripcion": "Prueba de fugas con aire seco o nitrógeno a 5,5 bar con solución jabonosa, después de pintar (ET 9.16.3)", "especificacion": "8 h de planta", "cantidad": 8, "unidad": "h",
     "fuentes": [fuente("ant", 13, "Horas de planta para movimientos internos y PH · END-00563", "conocimiento/precios/catalogo_servicios.csv", "2026-10-10", "similar", "8 h por criterio")]},
    {"id": "S05d", "pos": "API", "grupo": "servicio", "descripcion": "Calificación de procedimientos y soldadores (plano: ASME IX; ET 9.14: API 1104 con registro IRAM-IAS U500-138)", "especificacion": "", "cantidad": 1, "unidad": "gl",
     "fuentes": [sin_precio("pedir cotización a un ente habilitado (o confirmar si Ledesma o ITT tienen procedimientos vigentes)", "sin precio de calificación en el catálogo", "2026-10-29")],
     "sin_precio_motivo": "Sin referencia de calificación: pedir a Ledesma si su calificación cumple, o cotización a un ente habilitado (lista para Compras)"},
    {"id": "S06", "pos": "HH", "grupo": "mo", "descripcion": "Ingeniería: memoria de cálculo ASME VIII Div.1, planos de fabricación sobre el plano tipo y documentación", "especificacion": "250 h (decisión de Matías del 30-10-2026, con el diseño propio)", "cantidad": 250, "unidad": "h",
     "fuentes": [fuente("ant", 15, "Horas propias ITT (15 USD/h): 250 h, como los coalescedores Sacde/12 y TAVAL/37", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "con plano tipo del cliente las horas pueden bajar: a decidir por Matías")]},
    {"id": "S07", "pos": "CAL", "grupo": "mo", "descripcion": "Calidad, inspecciones y data book", "especificacion": "250 h (decisión de Matías del 30-10-2026)", "cantidad": 250, "unidad": "h",
     "fuentes": [fuente("ant", 15, "Horas propias ITT (15 USD/h): 250 h, como los coalescedores Sacde/12 y TAVAL/37", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "horas de coalescedores de 32\"–36\"")]},
    {"id": "S08", "pos": "ARM", "grupo": "mo", "descripcion": "Montaje propio: cartuchos, instrumentos, purgas, gas de instrumentos, tubing, movimientos y PH", "especificacion": "160 h", "cantidad": 160, "unidad": "h",
     "fuentes": [fuente("est", 16, "Horas propias ITT (16 USD/h en recipientes); criterio", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "estimado")]},
]

base = json.load(open(C.parent / "_plantilla" / "cotizacion.json", encoding="utf-8"))
base.update({"codigo": "COT26-0135-003", "fecha": "2026-11-05", "cliente": {"nombre": "CAMUZZI GAS PAMPEANA S.A. / CAMUZZI GAS DEL SUR S.A.", "codigo_itt": "0135", "comprador": "Gerencia de Abastecimiento Obras y Almacenes (Juan Filas)"},
             "titulo": f"Camuzzi · Concurso de precios N° 24578 ítem 1 / Concurso N° 24527 — 2 separadores verticales coalescentes (plano tipo {PLANO}, #600, {B} cartuchos)",
             "titulo_pagina": "Cotización Camuzzi CP 24578 · Separador coalescente", "archivo_planilla": "CAMUZZI_CP24578_SEPARADOR_COALESCENTE",
             "subtitulo_planilla": f"2 separadores verticales coalescentes según plano tipo {PLANO}: 36\" #600, {B} cartuchos + juego de repuesto · USD sin IVA",
             "meta": ["Concurso de precios N° 24578 · ítem 1 / Concurso N° 24527", f"Plano tipo {PLANO} (circular del 05-11-2026) · ET Separador Vertical Coalescente", "Comprador: Camuzzi (portal de compras)",
                      "Preparó: Matías Russo · rehecha sobre el plano tipo el 05-11-2026"],
             "equipo": {"singular": "separador", "plural": "separadores", "tipo": "filtro", "diametro_pulg": 36}, "items": items})
# Flete: con ≈ 4 t por equipo entran los 2 en un viaje (antes 2 viajes para ≈ 10 t c/u): 1.750 + 780 USD de la hoja Transporte de AESA/44
base["parametros"].update({"N": 2, "fecha_referencia": "2026-10-31", "rx_pct": 0, "ph_horas": 0, "TRANS": 1, "TC": TC_OCT, "TR_ARS": round(2530 * TC_OCT, -3), "TR_EMB": 300, "TR_F": 1.0})
base["plazo"] = {"dias": 230, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Memoria de cálculo, planos de fabricación sobre el plano tipo y procedimientos para calificación de Camuzzi", 0, 25, ""],
                            ["Revisión y aprobación de la documentación por Camuzzi (supuesto: 15 días corridos)", 25, 40, ""],
                            ["Tapas de cierre rápido 36\" #600 (Futura, 120 días desde la orden con los datos de diseño aprobados; Sacde/12)", 40, 160, "crit"],
                            ["Chapa, rolado, bridas, cartuchos y fabricación del cuerpo y el skid (Ledesma)", 40, 140, ""],
                            ["Soldadura del cuello de la tapa, RX y PH", 160, 178, "tal"],
                            ["Instrumentos, pintura, prueba de fugas, inspección de Camuzzi y despacho", 178, 200, "tal"]],
                 "nota": "Calculado 200 días (tapa Futura de 120 días pedida con el plano aprobado + taller); se ofrecen 230 con el margen de 15 % de plazos.md §4. Sin tratamiento térmico: SA-516-70 (P-No.1) de 31,75 mm no lo exige UCS-56 (ni precalentamiento hasta 1 1/4\"); si la memoria engrosa la chapa, revisarlo."}
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)",
                 "referencia_html": "<b>Estimado:</b> un viaje de semirremolque para los 2 separadores (≈ 4 t c/u) a 1.750 + 780 USD (hoja «Transporte» de la planilla ITT de AESA/44, 09-2025; no es cotización de transportista) + USD 300 de embalaje.",
                 "criterio_html": "La planilla del concurso pone el flete a cargo del proveedor hasta Transporte Cruz del Sur; el Concurso 24527 y la ET dicen destino final (consulta C3)."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · ítem 1 / Concurso N° 24527", "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"],
                  ["Ítem", "1 · Separador vertical coalescente sobre skid con plataforma · <b>2 un</b>"], ["Condiciones", "Pe máx 70 bar · Pe mín 25 bar · Qmáx 100.000 Sm3/h · cartuchos 5½\" × 36\""],
                  ["Documentos", f"Plano tipo {PLANO} y esquema general (circular del 05-11-2026); planilla del concurso; ET Separador Vertical Coalescente; listado de marcas SCE-IN-501-0015"],
                  ["Base adoptada", f"Serie #600 y {B} cartuchos (fila máxima de la tabla): {TABLA}"],
                  ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (CP 24578); destino final a determinar (Concurso 24527)"]],
                  "requisitos_html": [f"Construcción según el plano tipo {PLANO}: 39 referencias, dimensiones de la tabla para A = #600 y B = {B}",
                                      "Parámetros del plano (serie 600): diseño 70 bar, PH 91 bar, corrosión 1,6 mm, RX 100 % tope, LP 100 % filete, ASME VIII Div.1 y IX",
                                      "Entrada y salida a 180°, preferentemente 10\" #600; boca de inspección 6\" #600; tapa de apertura rápida no roscada con pescante",
                                      "2 purgas automáticas neumáticas 1\" con drenajes manuales; interruptores de nivel e indicadores reflex en ambas cámaras",
                                      "Manómetro diferencial con aguja de arrastre y contacto seco; manómetro estático; caja de chicanas AISI 304",
                                      "Un juego de cartuchos instalado y uno adicional de repuesto por equipo (ET 13.1); tarima con escalera y barandas, rejilla galvanizada",
                                      "Matriz de requisitos: <code>pedido/requisitos.csv</code>; consultas al cliente: <code>consultas_cliente.md</code> (consulta del 05-11-2026)"]}
base["nota_mo_html"] = (f"Equipo según plano tipo {PLANO}: cuerpo 36\" × {fmt(C2_MM)} mm SA-516-70 ({fmt(kg_env, 0)} kg), cabezal 2:1, tapa de cierre rápido, {B} cartuchos de 5½\" × 36\", 2 cámaras con caja de chicanas. "
                        f"Fabricación por tercero (Ledesma, a 4,15 USD/kg × {fmt(kg_fabricado, 0)} kg, más la soldadura extra por espesor); ITT pone ingeniería, calidad, montaje de instrumentos, rolado, RX, PH y pintura.")
base["desvios"] = [{"tag": "Cartuchos", "titulo": f"Cantidad de cartuchos (B = {B})", "texto": f"Se adopta la fila máxima de la tabla del plano tipo (B = {B}, 36\", toberas 10\"); se confirma con la ficha del cartucho y la pérdida de carga de 100 mbar (consulta del 05-11-2026)."},
                   {"tag": "PH", "titulo": "Presión de prueba", "texto": "El plano tipo fija 70 bar de diseño y PH a 91 bar; la ET 9.16.1 pide 1,3 × la presión máxima de la serie ANSI (≈ 133 bar). Se cotiza según el plano (consulta del 05-11-2026)."},
                   {"tag": "Elemento", "titulo": "Cartucho de papel", "texto": "El plano y la ET piden cartucho de papel / celulósico; la planilla habla de coalescente 0,3 µm. Se cotiza según el plano (consulta)."},
                   {"tag": "Flete", "titulo": "Lugar de entrega", "texto": "La ET y el Concurso 24527 dicen destino final; la planilla del CP 24578, Transporte Cruz del Sur. Se cotiza según la planilla (consulta C3)."},
                   {"tag": "Plazo", "titulo": "Plazo de entrega", "texto": "El Concurso 24527 pide 30 días corridos: imposible con una tapa de cierre rápido de 120 días. Se ofrece el plazo calculado."},
                   {"tag": "Moneda", "titulo": "Moneda", "texto": "El Concurso 24527 y el pliego general piden cotizar en pesos (USD solo para importados): se cotiza en USD como en CAMUZZI/30."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>CAMUZZI/30</b> · Concurso 22737", "fecha": "14-05-2026", "que": "2 separadores horizontales de polvo y líquido 28\" #600 (70 bar), 11 elementos 140 × 914", "precio": "venta 93.033 c/u", "tomado_html": "Gora (cartucho 46600 y caja de chicanas), Riva (indicador reflex 70 bar), Sandri (rolado) y Ledesma 28\" (control de la fabricación)"},
    {"carpeta_html": "<b>Sacde/12</b> · Filtro coalescente FC-301/302", "fecha": "18-12-2025", "que": "Coalescedor 36\" #600, 16 elementos, planilla de costo", "precio": "costo con planilla", "tomado_html": "Tapa Futura 36\" #600, cabezal 36\", chapa por kg, switch de nivel"},
    {"carpeta_html": "<b>TAVAL/37</b> · Filtro coalescedor FC-231 YPF", "fecha": "17-12-2025", "que": "Coalescedor 32\" #600, 16 elementos, con skids de cañería e instrumentación", "precio": "costo 407.845", "tomado_html": "Juntas #600 y rejilla"},
    {"carpeta_html": "<b>AESA/44</b> · Fabricación de recipientes (Ledesma)", "fecha": "27-08-2025", "que": "Presupuestos de Ledesma por recipiente a presión", "precio": "3,14 a 5,15 USD/kg", "tomado_html": "MO de fabricación por kg y flete (planilla ITT)"}]
base["pendientes"] = [{"titulo": "Consultas al cliente (05-11-2026)", "items": ["Cantidad de cartuchos para 100.000 Sm3/h (fila B de la tabla)", "PH a 91 bar (plano) o 1,3 × la serie (ET)", "Cartucho de papel o coalescente", "Especificaciones SCE-RE-512-0001 y SCE-PC-511-0003"]},
                      {"titulo": "Ingeniería", "items": ["Memoria de cálculo ASME VIII con la fila adoptada; espesor de las placas portacartuchos y guía (el plano no lo da)", "Ficha del cartucho: caudal por elemento a 25 bar y pérdida de carga ≤ 100 mbar"]},
                      {"titulo": "Proveedores (marcas del listado de Camuzzi)", "items": ["Tapa de cierre rápido 36\" #600 (Futura, Peco, Gora o EKA)", f"Cartuchos de papel 5½\" × 36\" (Gora, Filtron, De Nichilo, Panden, SP): {2 * B} por equipo con el repuesto", "Caja de chicanas 900 × 900 × 570 AISI 304 (Gora)", "Válvulas automáticas, esféricas y tapón 1\" #600; reguladores 1301F y 67FR; manómetros", "Fabricación (Ledesma) y rolado (Sandri) con el plano tipo"]}]
base["planilla_notas"] = ["Plazo: 230 días desde OC (calculado 200: documentación 25 + revisión de Camuzzi 15 + tapa Futura 120 + taller 40; margen 15 %).",
                          f"Base: plano tipo {PLANO}, serie #600, B = {B} cartuchos (a confirmar con Camuzzi y con la ficha del cartucho)."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar."
PROV_BRIDA = "Francovigh / CH / Thorsa / Forja Atlas (listado Camuzzi)"
base["compras"] = {"marcas": {"01": "El listado no trae marcas para este producto", "01b": "El listado no trae marcas para este producto", "02": "Curvo Sold / TDW", "03": "Tube Turn / Peco / Gora / Futura / EKA Técnica / T.D. Williamson (con tapa soldada, no roscada)", "04": "El listado no trae marcas para este producto", "05": "Futura / Francovigh", "06": "El listado no trae marcas para este producto", "07": "Futura / Francovigh", "08": "El listado no trae marcas para este producto", "09": "El listado no trae marcas para este producto", "10": "El listado no trae marcas para este producto", "11": "El listado no trae marcas para este producto", "12": "CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet)", "13": "CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet)", "14": "CH / Thorsa / Forja Atlas (accesorios forjados: threadolet, weldolet, socketweld, couplet)", "15": "El listado no trae marcas para este producto", "16": "Epta / Fisher (control de nivel líquido para separadores)", "17": "El listado no trae marcas para este producto", "18": "Gora / De Nichilo / Filtron / Panden / SP / Metpor (para separadores)", "18b": "Gora / De Nichilo / Filtron / Panden / SP / Metpor (para separadores)", "19": "El listado no trae marcas para este producto", "20": "Actuador: Bettis-Biffi-Morin / Bray / Flow / Wenlen (actuadores neumáticos). La válvula automática no tiene subgrupo en el listado", "21": "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Spirax Sarco (bridadas o roscadas hasta 4\" S150 y 1 1/2\" S300) / Beta / Valmec", "22": "Xomox-Tufline (autolubricado) / Nordstrom / Favra", "23": "Jefferson / Farinola / Riva (niveles tipo reflex y americano)", "23b": "Sin subgrupo propio (bloqueo y purga para manómetro: ABAC (modelo VA 350 y tapón 50 T) / Casucci)", "24": "El listado no trae marcas para este producto", "25": "El listado no trae marcas para este producto", "26": "Manómetro: Ing. Capino / Weisz / Wika (diferencial con aguja de arrastre) / ABAC / Casucci. Bloqueo y purga: ABAC (modelo VA 350 y tapón 50 T) / Casucci", "27": "Manómetro: Ing. Capino / Weisz / Wika (diferencial con aguja de arrastre) / ABAC / Casucci. Manifold: ABAC / Casucci / Fittinox (acero inoxidable)", "28": "Futura / Francovigh", "29": "El listado no trae marcas para este producto", "30": "Doma / Satesa / EQA / Epta / Tormene / Fiorentini / Fisher / Francel (solo modelos homologados de la solapa \"Válvulas Reguladoras\"; Ø mayor a 4\" con aprobación de la Gerencia Técnica). El 1301F no está en la solapa de modelos homologados (es para reguladoras de línea): consultar", "31": "Favra / Aerre / Farinola (con bridas ANSI o roscadas). El tipo S-70 es un modelo Doma y Doma no figura en válvulas de alivio: consultar a Camuzzi", "32": "El listado no trae marcas para este producto", "33": "Doma / Satesa / EQA / Epta / Tormene / Fiorentini / Fisher / Francel (solo modelos homologados de la solapa \"Válvulas Reguladoras\"; Ø mayor a 4\" con aprobación de la Gerencia Técnica). El 67FR no está en la solapa de modelos homologados: consultar", "34": "Swagelok / Parker / Casucci / Fittinox / ABAC / Famiq / Hoke-Gyrolok", "35": "El listado no trae marcas para este producto", "36": "Curvo Sold / TDW", "37": "Curvo Sold / TDW", "38": "Futura / Francovigh", "38b": "Klinger / Teadit / Flexseal / Miyashiro Schonborn / Garlock (solo espirometálicas)", "38c": "Delgado / Petrobul / Talleres Versailles / Fornis (terminación zincado / anodizado)", "39": "El listado no trae marcas para este producto"}, "material": {}, "fecha_respuesta": "2026-11-10", "material_en_planta_dias": 110, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo y validez.", "Certificados 3.1 de chapas, bridas y caños.", "Las cantidades son por separador × 2.", f"Plano tipo Camuzzi {PLANO}, serie #600, {B} cartuchos.", "Solo marcas del listado SCE-IN-501-0015 de Camuzzi.", "Válvulas esféricas (SCE-IN-501-0008 y ensayo SCE-RE-308-0001; no se aceptan sin certificados de fabricación y prueba firmados por la inspección): diseño ASME B16.34, fabricación API 6D, bridas ASME B16.5, a prueba de fuego API 607 con dispositivo antiestático, topes e indicador abierto/cerrado, fuerza de maniobra máx. 345 N a máxima ΔP (ensayo de torque API 6D B.6), esfera y vástago inox o AC con cromo duro / níquel químico ≥ 35 µm (hasta 2\": esfera solo inox), cuerpo AC calmado CE ≤ 0,50 %, espárragos A193 B7 / tuercas A194 2H, largo entre caras API 6D, prueba hidráulica de cuerpo y asientos y neumática burbuja cero sin sellador, marcado con fabricante, N° de OC, PT o PR, Ø, presión máx. y sentido de flujo, pintura SCE-PC-511-0003 (amarillo), entrega abierta con extremos protegidos (no cartón) y termocontraíble ≥ 500 µm, documentación por lote (certificados de materiales, ensayos hidráulico/neumático/torque, antifuego, cromado o niquelado, manual, despiece con repuestos, grasa recomendada), lista de repuestos valorizada para 1 año, garantía 12 meses desde instalación o 24 desde despacho. Fabricante aprobado por Camuzzi; si el modelo es nuevo para Camuzzi, ensayos de prototipo (8.2).", "Reguladoras, monitoras y alivios (SCE-RE-508-0002): cuerpo A216 WCB / A350 / A105 (prohibido bronce, latón o aluminio), internos inox, obturador blando PTFE, diafragmas de nitrilo IRAM 113001, espárragos B7/2H, placa de identificación con modelo, Ø, serie, internos, piloto, presiones máx. y N° de OC; ensayos de cuerpo a 1,5 × la serie (28,5 bar en #150; 110 bar en #600) 4 h y hermeticidad a 5,5 bar; pintura: cuerpo y actuador amarillo, válvulas de alivio naranja (SCE-PC-511-0003); entrega con extremos obturados, piloto protegido y fijada a bancada; hoja de datos y lista de repuestos recomendados con vida útil. Solo modelos homologados de la solapa \"Válvulas Reguladoras\" del SCE-IN-501-0015 rev 1 (Ø mayor a 4\" requiere aprobación de Camuzzi)."],
                   "notas": {"23b": "Bloqueo y purga 1/2\" NPT de los indicadores de nivel (ET 9.9): si no vienen con el Reflex, ABAC VA 350 con tapón 50 T o Casucci, clase apta para 70 bar", "27": "Manómetro diferencial a diafragma 0-2 bar, 3\", clase 2, aguja de arrastre, sellos Buna N o Vitón, presión estática máx. 100 bar, 1/4\" NPT, IP65, certificado de calibración (ET 9.19.2), con manifold de 3 vías ABAC / Casucci / Fittinox (inox, listado); accesorios inox doble virola", "26": "Manómetro estático Ø 100 (ET 9.19.1: clase 1, glicerina, caja AISI 304, bourdon AISI 316, 1/2\" NPT, IRAM IAP AS 165, IP65, certificado de calibración) montado con manifold de 2 vías (bloqueo y purga) de acero forjado ASTM A-105 zincado serie 3000 (ET 9.20): ABAC VA 350 con tapón 50 T o Casucci", "33": "Reguladora 67FR 1/4\" NPT con manómetro y filtro incorporado (Fisher o Doma, ambas en el listado), segunda etapa del gas de instrumentos; rango de salida según el actuador de la pos 20; verificar material del cuerpo (sin bronce ni aluminio, SCE-RE-508-0002)", "31": "Alivio 1/4\" NPT tipo S-70 (modelo Doma; Doma NO figura en válvulas de alivio del listado, solo Favra, Aerre y Farinola: consultar a Camuzzi), cuerpo ASTM A216 WCB, protege el gas de instrumentos aguas abajo de las reguladoras; presión de apertura a confirmar según el actuador de la pos 20; pintura naranja", "30": "Reguladora Fisher 1301F 1/4\" NPT con manómetro, alimentación de gas de instrumentos a los actuadores de las purgas automáticas: indicar rangos de entrada (hasta la presión del separador) y salida según el actuador de la pos 20; el plano pide cuerpo ASTM A216 WCB y la SCE-RE-508-0002 prohíbe bronce o latón: verificar el material del cuerpo que ofrece Fisher. Requisitos SCE-RE-508-0002", "22": "Tapón lubricado 1\" #600 bridada RF de sacrificio (drenaje inferior, ET 9.2), SCE-IN-501-0009: cono invertido (series 300/600), cuerpo ASTM A216 WCB, vástago inexpulsable A182 F6 o AISI 410, tapón de acero aleado con dureza ≥ 100 HB sobre el cuerpo, palanca; ensayos API 598 / API 6D (hidráulica 60 min, neumática de asiento a 7 kg/cm2, torque, LP en vástago, obturador y asiento); con grasa sellante compatible con gas, alemite de inyección, repuestos para 2 años y marca y tipo de sellante recomendado; garantía 12 / 24 meses", "21": "Esférica 1\" #600 bridada RF, PASO TOTAL, cuerpo fundido ASTM A216 WCB (by-pass de la purga superior y bloqueo del drenaje inferior, ET 9.2): esfera flotante solo inox, asientos PTFE, palanca con cierre horario ≤ 345 N; RX de extremos si fuera para soldar (B16.34). Requisitos SCE-IN-501-0008 en requisitos generales", "01": f"SA-516 Gr. 70, {fmt(C2_MM)} mm, certificado 3.1 (70N si la memoria lo pide)", "03": "36\" #600 vertical, no roscada, con pescante y o-rings de repuesto",
                             "18": "Papel 5½\" × 36\"; indicar caudal por elemento a 25 bar y pérdida de carga limpio", "19": "900 × 900 × 570 AISI 304 doble bolsillo (detalle de chicanas del plano)",
                             "20": "Purga automática 1\" #600 bridada RF (serie \"A\" del plano = #600), cuerpo ASTM A216 WCB, accionamiento neumático NORMAL CERRADA, internos inox y cierres con aporte stellite N° 6, comandada por interruptor de nivel a flotante on-off (ET 9.2); indicar presión y consumo del aire o gas de instrumentos del actuador; pintura amarillo", "23": "Reflex 500 mm, 70 bar (presión de diseño #600), con sus válvulas de bloqueo y purga (ET 9.9)"},
                   "proveedores": {"03": "Futura / Peco / Gora / EKA", "05": PROV_BRIDA, "07": PROV_BRIDA, "28": PROV_BRIDA, "38": PROV_BRIDA, "18": "Gora / Filtron / De Nichilo / Panden / SP", "18b": "Gora / Filtron / De Nichilo / Panden / SP",
                                   "19": "Gora", "20": "Bettis / Bray / Flow / Wenlen (actuador)", "21": "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Beta / Valmec (Spirax Sarco no: solo hasta 1 1/2\" S300)", "22": "Xomox-Tufline / Nordstrom / Favra",
                                   "23": "Riva Hnos", "27": "Wika + ABAC / Casucci", "30": "Fisher (Emerson)", "33": "Fisher (Emerson) / Doma", "31": "Favra / Aerre / Farinola (Doma, fabricante del S-70, no figura en alivios: consultar)", "26": "Weisz / Wika / Capino / ABAC / Casucci + ABAC VA 350 / Casucci", "34": "ABAC / Swagelok / Parker / Fittinox / Casucci"},
                   "cantidad_compra": {}, "servicios": [{"servicio": f"Rolado de 2 virolas 36\" × {fmt(C2_MM)} mm × {fmt(L_ENV / 2, 2)} m", "proveedores": "Sandri (hasta 50 mm × 2.500 mm)", "referencia": "1,74 USD/kg (03-2026, chapa de 1\")", "nota": "con el plano tipo"},
                                                        {"servicio": "Fabricación del separador y skid", "proveedores": "Ledesma", "referencia": "4,15 USD/kg (AESA/44); 13.000 el 28\" de CAMUZZI/30", "nota": "con el plano tipo; aclarar consumibles y calificación"},
                                                        {"servicio": "Flete de 2 separadores de ≈ 4 t", "proveedores": "a definir", "referencia": "1.750 + 780 USD (planilla ITT de AESA/44)", "nota": "destino a confirmar (consulta C3)"}]}
base["origen_lista"] = {"tipo": "plano_cliente", "motivo": f"Plano tipo de Camuzzi {PLANO} (circular del 05-11-2026): tabla de 39 referencias sin cantidades; las cantidades las calcula ITT con la tabla para #600 / B = {B}"}
base["justificaciones"] = {"antecedentes": "Rehecha el 05-11-2026 sobre el plano tipo de Camuzzi (36\" #600, 20 cartuchos): no se compara con la versión de diseño propio (55\", 37 elementos, 2 1/4\"). Comparar con CAMUZZI/30 (28\" #600, 93.033 de venta c/u) al revisar."}
base["historial_html"] = ["30-10-2026: revisión completa del diseño propio (55\", 37 elementos).", f"05-11-2026: rehecha sobre el plano tipo {PLANO} recibido por circular (serie #600, B = {B})."]
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

PLAZO = base["plazo"]["dias"]
camuzzi_comun.oferta(C, "COT26-0135-003", "Separador coalescente", 1, f"separador vertical coalescente según plano tipo {PLANO}, serie #600, {B} cartuchos de 5½\" × 36\", sobre skid con tarima de acceso", "2", PLAZO,
                     ["Concurso de precios N° 24578 / Concurso N° 24527: planilla de cotización, cláusulas particulares y condiciones generales", f"Plano tipo {PLANO} «Separador vertical coalescente» y Esquema General Filtro Coalescente (circular del 05-11-2026)",
                      "Especificación técnica Separador Vertical Coalescente (rev. 0)", "Listado de Marcas y Proveedores SCE-IN-501-0015"],
                     f"Separador vertical coalescente según plano tipo {PLANO}: cuerpo 36\" en SA-516-70 de {fmt(C2_MM)} mm con cabezal semielíptico 2:1, diseño ASME VIII Div.1 a 70 bar con 1,6 mm de corrosión, toberas 10\" #600 a 180°, "
                     f"{B} cartuchos de papel de 5½\" × 36\", tapa de apertura rápida no roscada con pescante, caja de chicanas AISI 304, boca de inspección 6\" #600, 2 purgas automáticas neumáticas 1\" con drenajes manuales, interruptor de nivel e indicador reflex en cada cámara, manómetros diferencial y estático, sobre skid con tarima de acceso galvanizada.",
                     [f"Construcción según el plano tipo {PLANO}, serie #600, con {B} cartuchos (fila máxima de la tabla). La cantidad definitiva se confirmará con la ficha técnica del cartucho y la pérdida de carga máxima de 100 mbar (ET 9.1).",
                      "Presión de diseño 70 bar y prueba hidráulica a 91 bar según el plano tipo. Si Camuzzi requiere la prueba a 1,3 veces la presión máxima de la serie ANSI (ET 9.16.1), se ajustará el diseño y la oferta.",
                      "Cartuchos de papel / material celulósico según el plano tipo y la especificación (punto 9); un juego instalado y uno adicional de repuesto por equipo.",
                      "Moneda: cotizamos en dólares estadounidenses, sin IVA, a facturar en pesos al tipo de cambio BNA divisa vendedor del día de la facturación. El equipo lleva componentes importados y precios de proveedores en dólares.",
                      f"Plazo de entrega: {PLAZO} días corridos desde la orden de compra (la tapa de cierre rápido tiene 120 días de fabricación desde la aprobación de los datos de diseño).",
                      "Entrega en Transporte Cruz del Sur según la planilla del concurso (la especificación indica destino final)."],
                     ["Memoria de cálculo y planos de fabricación para aprobación.", "Suministro de materiales, cartuchos e instrumentos.", "Fabricación, RX, PH, prueba de fugas, pintura, galvanizado de la tarima y montaje sobre skid.", "Data book.", "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
of = json.load(open(C / "oferta.json", encoding="utf-8"))
of["titulo_materiales"] = f"LISTA DE MATERIALES SEGÚN PLANO TIPO {PLANO} (SERIE #600, {B} CARTUCHOS; CANTIDADES CALCULADAS POR ITT, POR SEPARADOR)"
of["condiciones"]["PLAZO DE ENTREGA"] = f"{PLAZO} días corridos desde la orden de compra. Considera 15 días corridos de revisión de Camuzzi en cada entrega de documentación para calificación."
of["cliente"]["referencia"] = "Concurso de precios N° 24578 (ítem 1) / Concurso de precios N° 24527 – Filtro Coalescente"
json.dump(of, open(C / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "ítems · envolvente", kg_env, "kg · cabezal", kg_cab, "· placas", kg_placas, "· faldón", kg_faldon, "· skid", kg_skid, "· fabricado", kg_fabricado, "kg · pulg extra", pulg_extra, "· RX", N_PG, "+", N_PC)
