"""Separador vertical coalescente (CP 24578 ítem 1 y Concurso 24527, 2 un). Diseño preliminar de ITT (bitacora.md) corregido el
29-10-2026 con la ET "Separador Vertical Coalescente" y el esquema general de Camuzzi (pedido/CP24527_mail_2026-10-14/), y revisado
renglón por renglón el 30-10-2026 (bitacora.md, "Revisión completa del 30-10-2026").
Escribe pedido/lista_materiales_plano.csv (cómputo de diseño, no es un plano del cliente), cotizacion.json y oferta.json.
Es la ÚNICA fuente de esos archivos: toda corrección va acá (con su fuente), nunca a mano en cotizacion.json (error del 30-10-2026:
las decisiones de Matías del 30-10 —RX, ingeniería y calidad 250 h, compatibilidades— estaban solo en cotizacion.json y este programa
las deshacía).
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
from numeros import fmt, fmtg  # noqa: E402

BIT = "cotizaciones/COT26-0135-003_CAMUZZI_CP24578_SEPARADOR/bitacora.md"
# ---- dimensionamiento preliminar (bitacora.md) ----
N_ELEM = 37            # hacen falta ≈ 34 (3.660 m3/h reales a 25 bar ÷ 108 m3/h por elemento, Sacde/12); en arreglo triangular de 180 mm el anillo completo es 1+6+12+18 = 37 (revisión 28-10-2026)
DI = 1.28              # m: centros hasta 0,54 m de radio + 70 mm de medio elemento + 30 mm de huelgo
# Diseño a la presión de la serie #600 (102,1 bar a 38 °C), opción elegida el 29-10-2026 para la PH de la ET 9.16.1 (1,3 × la presión
# máxima de la serie ANSI ≈ 133 bar). Fundamento corregido el 30-10-2026 (auditoría): 1,3 × MAWP es el MÍNIMO de la PH en ASME VIII
# (UG-99), no un máximo; con MAWP 77 bar (1 5/8") la PH a 133 bar también es posible si la memoria verifica las tensiones en la prueba
# (≈ 214 MPa de membrana con 41,3 mm, menos del 90% de la fluencia de SA-516-70). Decisión pendiente de Matías / dirección (bitácora).
# t = P·R/(S·E − 0,6·P) = 10,21 × 640 / (138 − 6,13) = 49,6 + 1,6 de corrosión (ET 9) = 51,2 mm → chapa 2 1/4" (57,15 mm)
T_CUERPO = 57.15       # mm (2 1/4")
T_PLACA = 41.3         # mm (1 5/8"): la placa portaelementos solo soporta la diferencial entre cámaras; se mantiene, a verificar en la memoria
D_EXT = round(DI + 2 * 0.05715, 3)  # m (≈ 55"): DI 1,28 m + 2 × 2 1/4" (con 44" no entraban: revisión 28-10-2026)
D_EXT_PULG = D_EXT / 0.0254  # 54,9": las tapas de cierre rápido se designan por el diámetro nominal exterior (Futura 16" = 406 mm; auditoría 30-10-2026)
L_CUERPO = 3.2         # m: cámara inferior de separación 1,3 m + placa + cámara de coalescencia (914 mm + 200 mm a la salida + 0,8 m)
DM = DI + T_CUERPO / 1000  # diámetro medio de la virola
kg_cuerpo = round(math.pi * DM * L_CUERPO * T_CUERPO / 1000 * 7850)  # con el diámetro medio (antes el exterior: 6.287 kg; auditoría 30-10-2026)
kg_placa = round(math.pi * DI ** 2 / 4 * T_PLACA / 1000 * 7850)
# Fondo 2:1: superficie ≈ 1,084·Dm² + pestaña recta de 50 mm (Dm = diámetro medio)
kg_fondo = round((1.084 * DM ** 2 + math.pi * DM * 0.05) * T_CUERPO / 1000 * 7850)
KG_SKID, KG_POLLERA, KG_CONEX = 1300, 450, 430   # skid y plataforma (pos 23), pollera (pos 24), conexiones (bridas y caños con tabla: controles_tablas.md)
kg_fabricado = kg_cuerpo + kg_fondo + kg_placa + KG_SKID + KG_POLLERA + KG_CONEX  # lo que suelda el tercero (sin la tapa ni las chicanas, que se compran hechas)
# UCS-56 (ASME VIII Div.1): P-No.1 con espesor nominal > 38 mm (1 1/2") exige tratamiento térmico post soldadura → con 2 1/4" corresponde.
# Sin la temperatura mínima de diseño (la ET no la da: consulta C4) no se puede eximir de Charpy (UCS-66): se cotiza SA-516-70 y se avisa.

# Tapa de cierre rápido: exponente ajustado con las dos tapas Futura #600 cotizadas (16": 8.432, TAVAL/40, 15-01-2026; 36": 24.288,60,
# Sacde/12, 18-12-2025): ln(24.288,60 / 8.432) / ln(36 / 16) = 1,305 (antes 1,5 sin fuente). Se escala por el diámetro nominal exterior
# (54,9"), igual que las referencias; el 30-10 se escaló por el DI (50,4") y eso era un error (auditoría).

# Soldadura del recipiente de pared gruesa (auditoría 30-10-2026): los presupuestos de Ledesma de AESA/44 son de recipientes de pared fina
# (2,5 m × 17 a 22 m, 6 a 16 t según el pedido de flete a Suan → ≈ 10 mm de pared). Se suma la soldadura extra por espesor con la regla de
# ITT de pulgadas equivalentes (factores_soldadura.csv: factor = espesor ÷ 9,53 sobre STD) y la tarifa de soldadura por pulgada de Quesada
# (12 USD/pulg-eq, incluye consumibles; JQ-020-2026). Juntas a tope del cuerpo: 3 circunferenciales Ø ext. + 2 longitudinales de 1,6 m
# (pulgadas = largo ÷ π); placa portaelementos; toberas que atraviesan la pared (2 × 10", 6", 4 × 2" y 8 × 1").
F_CUERPO, F_PLACA = T_CUERPO / 9.53, T_PLACA / 9.53
PULG_CUERPO = 3 * D_EXT_PULG + 2 * 1600 / math.pi / 25.4
PULG_TOBERAS = 2 * 10 + 6 + 4 * 2 + 8 * 1
pulg_extra = round(PULG_CUERPO * (F_CUERPO - 1) + DI / 0.0254 * (F_PLACA - 1) + PULG_TOBERAS * (F_CUERPO - 1), 1)
EXP_TAPA = math.log(24288.6 / 8432) / math.log(36 / 16)
TC_OCT = 1543.23       # BNA venta, promedio 10-2026 (conocimiento/costos/dolar_mensual.csv), el mismo de parametros.TC


def fuente(tipo, precio, prov, origen, fecha, coincide="similar", dif=""):
    f = {"tipo": tipo, "precio": round(precio, 2), "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        f["diferencia"] = dif
    return f


def sin_precio(prov, fecha, dif):
    return {"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: " + prov, "origen": "—", "fecha": fecha, "coincide": "sin_ref", "diferencia": dif}


EST = lambda precio, criterio, dif="": fuente("est", precio, "Estimado: " + criterio, BIT, "2026-10-28", "sin_ref", dif)
S12 = "fuentes_originales/ofertas_texto/Sacde/12-2970-SE-PTG-008 - FILTRO COALESCENTE - Pedido de precios/4.Armado de la Oferta Comercial/LM costos Filtro Coalecedor FC 301 y 302 #600 PC0-C.xlsx.txt"
T37 = "fuentes_originales/ofertas_texto/TAVAL/37- Doc5449458609 - RFP 1 Sobre - Filtro Coales (COMPRA)/4.Armado de la Oferta Comercial/LM costos Coalescedor FC-231 YPF - PC0-C (REV. 0).xlsx.txt"
T40 = "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt"
C30 = "fuentes_originales/ofertas_texto/CAMUZZI/30 - Separador Polvo y Líquido (2 unid) - Lic 22737/5.Proveedores 3ros/"
A44 = "fuentes_originales/ofertas_texto/AESA/44-Doc5319481557 - AESA - SRV FABRICACION EQUIPOS - F5064/"
L30 = "fuentes_originales/taval_lista30_2025-09.xlsx"
CAT = "conocimiento/precios/catalogo_materiales.csv"
CANT_ITT = "El cliente no indica cantidad: calculada por ITT según la ET y el esquema de Camuzzi"
# pos, descripción, Ø, serie/sch, material, extremos, cantidad, unidad, fuentes, [sin_precio_motivo]
M = [
    ("1", f"Chapa para virola Ø55\" (DI 1.280 mm) × {fmtg(L_CUERPO)} m × 2 1/4\" ({fmt(kg_cuerpo, 0)} kg + 10% recortes)", '55"', "e = 2 1/4\"", "SA-516 Gr. 70", "BW", round(kg_cuerpo * 1.1), "kg",
     [fuente("ant", 1.80, "Planilla Sacde/12 coalescedor FC-301/302: chapa SA-516-70 1 1/2\" a 1,80 USD/kg", S12, "2025-12-18", "similar", "espesor 1 1/2\" (acá 2 1/4\"); si la temperatura mínima de diseño lo exige (UCS-66, consulta C4) va normalizada (70N)")]),
    ("2", "Cabezal semielíptico 2:1 Ø55\" × 2 1/4\" (fondo inferior)", '55"', "e = 2 1/4\"", "SA-516 Gr. 70", "BW", 1, "un",
     [fuente("ant", 3000 * (55 / 36) ** 2 * 2.25 / 1.5, "Planilla Sacde/12: cabezal 36\" × 1 1/2\" SA-516-70 a 3.000, escalado por superficie (55/36)² y espesor (2 1/4 ÷ 1 1/2)", S12, "2025-12-18", "similar", f"Ø36\" (escalado × 3,50 por peso: ≈ {fmt(kg_fondo, 0)} kg); fondo 2:1 a 102 bar: 47,7 + 1,6 + afinamiento de conformado")]),
    ("3", "Tapa de cierre rápido no roscada para DI 1.280 mm #600 con pescante, A105N, o-rings de repuesto (marca del listado Camuzzi: Futura, Peco, Gora o EKA)", '55"', "600", "A105N", "BW", 1, "un",
     [fuente("ant", 24288.6 * (D_EXT_PULG / 36) ** EXP_TAPA, f"Planilla Sacde/12: tapa Futura 36\" #600 con pescante 24.288,60, escalada al diámetro nominal exterior {fmt(D_EXT_PULG, 1)}\" × ({fmt(D_EXT_PULG, 1)}/36)^{fmt(EXP_TAPA, 3)} (exponente de las tapas Futura #600 de 16\" y 36\", designadas por el diámetro exterior)", S12, "2025-12-18", "similar", "Ø36\", extrapolada fuera del rango cotizado; pedir cotización a Futura (Megatap no está en el listado de Camuzzi)"),
      fuente("ant", 8432, "Futura FV16 #600 A-105 (cotización Futura S00356, planilla TAVAL/40): 16\" a 8.432 (punto bajo del exponente)", T40, "2026-01-15", "similar", "16\": solo para el exponente de escala")]),
    ("4", f"Placa portaelementos Ø1,28 m × 1 5/8\" con {N_ELEM} agujeros mecanizados ({fmt(kg_placa, 0)} kg)", "", "e = 1 5/8\"", "SA-516 Gr. 70", "—", 1, "un",
     [fuente("ant", kg_placa * 1.8, f"{fmt(kg_placa, 0)} kg × 1,80 USD/kg (chapa SA-516-70, planilla Sacde/12)", S12, "2025-12-18", "similar", "solo la chapa: el corte y el mecanizado de los agujeros van en la fabricación (S02)")]),
    ("5", "Elemento filtrante 0,3 µm, cartucho L = 914 mm (36\") × Ø 140 mm (5 1/2\"): planilla «coalescente»; ET 9: «material celulósico, malla reforzada y armadura de refuerzo zincada, con junta de goma» (consulta C2)", "", "", "a definir (consulta C2)", "—", N_ELEM, "un",
     [fuente("ant", 854, "Planilla Sacde/12 FC-301/302: elemento filtrante coalescedor (16 u a 854)", S12, "2025-12-18", "similar", "elemento coalescedor de otro tamaño (no informado); pedir el de 0,3 µm 140 × 914 a Gora / Filtron / De Nichilo / Panden / SP (listado Camuzzi), con caudal por elemento a 25 bar y pérdida de carga; si Camuzzi confirma celulósico (ET 9) el precio baja mucho (Gora 46600 de fibra de vidrio: 113,83, PPTO 27131)"),
      fuente("ant", 854, "Planilla TAVAL/37 FC-231 (YPF): elemento filtrante coalescedor (16 u a 854)", T37, "2025-12-17", "similar", "misma plantilla de costos que Sacde/12 (16 u a 854, sin tamaño ni modelo): NO es una fuente independiente. Es el renglón más caro del equipo con una base débil: cotización a Compras")]),
    ("5b", "Elemento filtrante 0,3 µm, 140 × 914 mm: juego adicional de repuesto (ET 13.1)", "", "", "a definir (consulta C2)", "—", N_ELEM, "un",
     [fuente("ant", 854, "Planilla Sacde/12 FC-301/302: elemento filtrante coalescedor (16 u a 854)", S12, "2025-12-18", "similar", "mismo elemento que la pos. 5; compra extra por el juego de repuesto")]),
    ("6", "Brida WN RF entrada y salida 10\" #600 sch 80", '10"', "600 x 80", "ASTM A-105", "RF/BW", 2, "un",
     [fuente("cot", 301.86, "Grupo Provemet cot. 288978 ítem 12 · BRI-04996", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288978_bridas_2026-10-29.pdf · ítem 12", "2026-10-29", "igual", "Brida Welding Neck Sch 80 Raised Face Serie 600 ASTM A 105 ANSI B16.5 10\"; validez 15 días"), fuente("cot", 338.45, "Provemet · BRI-01227", CAT, "2025-07-29", "igual")]),
    ("7", "Caño 10\" sch 80 (toberas de entrada y salida)", '10"', "80", "ASTM A-106 Gr. B", "BW", 0.8, "m",
     [fuente("cot", 168.01, "Grupo Provemet cot. 288974 ítem 12 · CAN-01420", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf · ítem 12", "2026-10-29", "igual", "TUBO S/C PSL2 ASTM A53/A106/API5L B 10'' SCH 80 Ø 273 X 15,09 mm (PSL2 de API 5L: igual o superior al A-106 Gr B que pide el plano); Provemet cot. 288974 (29-10-2026), precio neto con bonificación 4% (vale comprando toda la cotización), validez 15 días"), fuente("lista", 204.43, "Renard (cód. 1193) · CAN-01420 (273 × 15,09 mm)", "fuentes_originales/renar_lista_2025-12.xlsx", "2025-12-26", "igual")]),
    ("8", "Brida WN RF 6\" #600 sch 80 (boca de inspección a 90° de la entrada)", '6"', "600 x 80", "ASTM A-105", "RF/BW", 1, "un",
     [fuente("cot", 112.28, "Grupo Provemet cot. 288978 ítem 8 · BRI-01321", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288978_bridas_2026-10-29.pdf · ítem 8", "2026-10-29", "igual", "Brida Welding Neck Sch 80 Raised Face Serie 600 ASTM A 105 ANSI B16.5 6\"; validez 15 días"), fuente("cot", 226.14, "Renard · BRI-01320", CAT, "2025-07-11", "igual")]),
    ("9", "Brida ciega RF 6\" #600 (boca de inspección)", '6"', "600", "ASTM A-105", "RF", 1, "un",
     [fuente("cot", 172.28, "Provemet cot. 242356: brida ciega 8\" RF #600 ASTM A105 B16.5 · BRI-01064", CAT, "2025-08-27", "similar", "8\" (pedido 6\"): no hay ciega de 6\" #600 en el catálogo; se toma la medida mayor (antes WN 6\" + 10% sin fuente)")]),
    ("10", "Caño 6\" sch 80 (boca de inspección)", '6"', "80", "ASTM A-106 Gr. B", "BW", 0.3, "m",
     [fuente("cot", 74.52, "Grupo Provemet cot. 288974 ítem 10 · CAN-01512", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf · ítem 10", "2026-10-29", "igual", "TUBO S/C ASTM A53/A106/API5L B 6'' SCH 80 Ø 168,3 X 10,97 mm; Provemet cot. 288974 (29-10-2026), precio neto con bonificación 4% (vale comprando toda la cotización), validez 15 días"), fuente("ant", 90.70, "Renard · CAN-01512 (planilla de costo ITT)", CAT, "2026-06-26", "igual")]),
    ("11", "Brida WN RF 2\" #600 sch 160 (stand-pipes de los switches de las 2 cámaras)", '2"', "600 x 160", "ASTM A-105", "RF/BW", 4, "un",
     [fuente("cot", 25.60, "Oil Metal · BRI-01255", CAT, "2025-07-03", "igual")]),
    ("12", "Caño 2\" sch 160 (conexiones y stand-pipes)", '2"', "160", "ASTM A-106 Gr. B", "BW", 4, "m",
     [fuente("ant", 24.67, "CAN-01454 (planilla de costo ITT)", CAT, "2026-06-26", "igual")]),
    ("13", "Brida WN RF 1\" #600 sch 160 (conexiones de visores, tomas de presión y las 2 purgas automáticas con sus bloqueos y by-pass)", '1"', "600 x 160", "ASTM A-105", "RF/BW", 15, "un",
     [fuente("cot", 25.00, "Oil Metal · BRI-01201", CAT, "2025-07-03", "igual")]),
    ("14", "Válvula esférica 2\" #600 PT RF (bloqueos de stand-pipes), marca del listado Camuzzi (Esferomatic, Worcester, Valvtronic, Pentair, Indave, Wenlen, Beta o Valmec)", '2"', "600", "A216 WCB", "RF", 4, "un",
     [fuente("lista", 220, "Precio de referencia: Taval 2\" #600 RF PT (Lista 30 × 0.52) · VAL-04447", L30, "2025-09-01", "similar", "misma especificación, otra marca: Taval no está en el listado de Camuzzi; pedir cotización a una marca del listado")]),
    ("14b", "Válvula esférica 1\" #600 RF (ET 9.2: 2 bloqueos de cada purga automática, by-pass de cada una y bloqueo del drenaje inferior), marca del listado Camuzzi", '1"', "600", "A216 WCB", "RF", 7, "un",
     [sin_precio("pedir cotización", "2026-10-30", "la referencia (Taval 1\" #600 RF, 162, Sacde/12, VAL-03169) no dice el material y se pide A216 WCB"),
      fuente("ant", 162, "Precio de referencia: Taval 1\" #600 RF PT (planilla Sacde/12) · VAL-03169", S12, "2025-12-18", "similar", "orden de magnitud: 7 × 162 = 1.134 por equipo")],
     "Sin referencia compatible (la Taval 1\" #600 de Sacde/12, 162, no dice el material); verificar_computo.py da ERROR con un estimado sobre una referencia sin material (P4 compatibilidad, regla de Matías del 30-10-2026): queda en 0 y frena hasta cotizar (auditoría 30-10-2026 pedía cargarla como estimado: rechazado)"),
    ("14c", "Válvula tapón lubricado 1\" #600 de sacrificio (drenaje inferior, ET 9.2), marca del listado Camuzzi (Xomox-Tufline, Nordstrom, Favra)", '1"', "600", "A216 WCB", "RF", 1, "un",
     [sin_precio("pedir cotización", "2026-10-29", "solo hay tapón 1\" NPT S-3000 (VAL-03596): otra serie no es referencia; buscar_material.py (30-10-2026): sin tapón lubricado #600 en el catálogo")],
     "Sin referencia de la misma serie (solo hay tapón NPT S-3000): pedir cotización a Xomox-Tufline / Nordstrom / Favra (lista para Compras)"),
    ("15", "Válvula esférica 1/2\" roscada (bloqueo y purga de visores; ET 9.9)", '1/2"', "2000", "A105", "NPT", 8, "un",
     [fuente("lista", 36.06, "Precio de referencia: Taval 1/2\" #2000 NPT A105 paso total API 608 forjada (Lista 30 × 0.52) · VAL-04865", L30, "2025-09-01", "similar", "misma especificación, otra marca: Taval no está en el listado de Camuzzi; pedir cotización a una marca del listado (la revisión del 30-10 la había dejado sin precio diciendo que no había 1/2\" S-2000 NPT en el catálogo: sí está)")]),
    ("16", "Purga automática 1\" #600 bridada: válvula de accionamiento neumático normal cerrada, internos inox con cierres de stellite 6 (ET 9.2), una por cámara; actuador Bettis / Bray / Flow / Wenlen", '1"', "600", "", "RF", 2, "un",
     [sin_precio("pedir cotización (actuador Bettis / Bray / Flow / Wenlen)", "2026-10-30", "la única referencia (válvula de control 1\" #600 RF a 2.000, Sacde/12 = TAVAL/37, misma plantilla) no dice el material ni los internos"),
      fuente("ant", 2000, "Planilla Sacde/12 FC-301/302: válvula de control 1\" #600 RF (purga del coalescedor) · VAL-03210", S12, "2025-12-18", "similar", "orden de magnitud: 2 × 2.000 = 4.000 por equipo")],
     "La referencia de Sacde/12 (2.000) no dice el material; verificar_computo.py da ERROR con un estimado sobre una referencia sin material (P4 compatibilidad, regla de Matías del 30-10-2026): queda en 0 y frena hasta cotizar (auditoría 30-10-2026 pedía cargarla como estimado: rechazado)"),
    ("16b", "Interruptor de nivel a flotante (accionamiento on-off) que comanda cada purga automática (ET 9.2), una por cámara; Epta / Fisher (control de nivel) o Magnetrol / Kimray", "", "", "", "—", 2, "un",
     [fuente("ant", 2500, "Planilla Sacde/12 FC-301/302: switch de nivel 2\" NPT 3000# (4 u a 2.500)", S12, "2025-12-18", "similar", "switch de nivel del coalescedor de Sacde/12, sin datos de modelo; pedir cotización del control de nivel a flotante para purga neumática")]),
    ("16c", "Regulador y filtro de gas de instrumentos para el accionamiento neumático de las 2 purgas automáticas", "", "", "", "—", 1, "un",
     [sin_precio("pedir cotización", "2026-10-30", "no hay regulador de gas de instrumentos en el catálogo (buscar_material.py, 30-10-2026)")],
     "Faltaba en el cómputo (las purgas neumáticas necesitan el gas de accionamiento) y no hay referencia en el catálogo: pedir cotización (lista para Compras)"),
    ("17", "Switch de nivel alto sobre stand-pipe, Ex-d, una por cámara (Magnetrol, Murphy, Kimray, Jefferson o Farinola)", "", "", "", "—", 2, "un",
     [fuente("ant", 2500, "Planilla Sacde/12 FC-301/302: switch de nivel 2\" NPT 3000# (4 u a 2.500)", S12, "2025-12-18", "similar", "no dice Ex-d ni marca; pedir cotización a Magnetrol / Murphy con protección Ex-d")]),
    ("18", "Visor de nivel óptico reflex 500 mm apto para la presión de diseño (#600), con válvulas de bloqueo y purga, uno por cámara (ET 9.9)", "", "", "", "—", 2, "un",
     [sin_precio("pedir cotización a Riva para #600", "2026-10-29", "la cotización de Riva (685, CAMUZZI/30) es para 70 bar: otra presión no es referencia")],
     "La única referencia (Riva 685) es para 70 bar de trabajo, no para la presión de diseño de 102 bar: pedir cotización a Riva (lista para Compras)"),
    ("19", "Manómetro diferencial a diafragma 0-2 bar, Ø3\", aguja de arrastre y contacto seco (ET 9.19.2 y planilla); Wika (homologado por Camuzzi con aguja de arrastre)", "", "", "", "—", 1, "un",
     [fuente("ant", 500, "Weisz: manómetro diferencial 0-2 bar (planilla TAVAL/40) · INS-02695", T40, "2026-01-15", "similar", "sin aguja de arrastre ni contacto seco: pedir cotización a Wika")]),
    ("19b", "Manifold de 3 vías para el manómetro diferencial (ET 9.19.2), ABAC o Casucci", "", "", "", "NPT", 1, "un",
     [fuente("ant", 170, "ABAC manifold de 3 vías M1-C-T 1/2\" S-2000 AISI 304/316 (planilla TAVAL/40)", T40, "2026-01-15", "similar", "AISI 304/316 (la ET pide acero zincado; el listado de Camuzzi pide inoxidable para el del diferencial). Antes estaba sumado al manómetro estático")]),
    ("20", "Manómetro de presión estática Ø100 con glicerina, clase 1, caja AISI 304, conexión 1/2\" NPT AISI 316 (ET 9.19.1)", "", "", "", "—", 1, "un",
     [sin_precio("pedir cotización a Weisz / Wika con la ET 9.19.1", "2026-10-30", "la referencia (Weisz 120, PAMPA/7, INS-02702) no dice el material de caja ni de bourdon"),
      fuente("ant", 120, "Weisz: manómetro (planilla PAMPA/7) · INS-02702", "fuentes_originales/ofertas_texto/PAMPA ENERGIA/7- Licitacion contrato Marco Skid PAD Rincon de Aranda/4.Armado de la Oferta Comercial/Cot Skid Manifolds Colectores RDA Contrato Marco (2da RDA).xlsx.txt", "2026-08-14", "similar", "orden de magnitud")],
     "La referencia (Weisz 120) no dice los materiales que pide la ET (caja AISI 304, bourdon AISI 316); verificar_computo.py da ERROR con un estimado sobre una referencia sin material (P4 compatibilidad, regla de Matías del 30-10-2026): queda en 0 y frena hasta cotizar (auditoría 30-10-2026 pedía cargarla como estimado: rechazado)"),
    ("20b", "Bloqueo y purga de 2 vías para el manómetro estático, 1/2\" NPT serie 3000 (ET 9.19.1 y 9.20), ABAC (modelo homologado por Camuzzi) o Casucci", '1/2"', "3000", "ASTM A105 zincado o superior", "NPT", 1, "un",
     [sin_precio("pedir cotización a ABAC / Casucci", "2026-10-30", "la referencia (ABAC bloqueo y purga 1/2\" NPT AISI 316, 137, TAVAL/55, VAL-03198) es inoxidable y la ET pide A105 zincado: compatibilidad.py no admite el reemplazo; no hay A105 en el catálogo"),
      fuente("ant", 137, "ABAC válvula de bloqueo y purga 1/2\" NPT M-H AISI 316 (planilla TAVAL/55) · VAL-03198", "fuentes_originales/ofertas_texto/TAVAL/55- Tecpetrol Puentes de Producción PPar Valvula y Puente PR 54942/7.Propuesta Comercial (envío al Cliente)/Puente de producción Tec Conv y NOC versión 3.xlsx.txt", "2026-04-22", "similar", "AISI 316: otro material, solo orden de magnitud")],
     "Sin referencia en A105 (la ABAC de 137 es AISI 316 y la regla de compatibilidad no la admite por A105): pedir cotización (lista para Compras)"),
("21", "Internos: caja de chicanas de doble bolsillo en AISI 304 (ET 9.8), soporte superior y fijaciones de elementos", "", "", "AISI 304", "—", 1, "gl",
     [fuente("ant", 6000, "Planilla TAVAL/37 FC-231: caja de chicana 800 × 400 × 400 mm AISI 304 («caja de vanes - a calcular»)", T37, "2025-12-17", "similar", "valor de planilla ITT, no cotización; Gora cotizó una caja de chicanas doble bolsillo AISI 316 250 × 250 × 150 a 615 (PPTO 27131, 11-02-2026, CAMUZZI/30): pedir a Gora con el tamaño del diseño")]),
    ("21b", "Conector recto doble virola OD × NPT 1/2\" AISI 304/316 (ET 9.20), ABAC / Swagelok / Parker / Fittinox / Casucci", '1/2"', "", "AISI 316", "NPT", 4, "un",
     [fuente("ant", 28, "ABAC conector recto c/tuerca y doble virola OD×NPT 1/2\" S-2000 AISI 304/316 (planilla TAVAL/40)", T40, "2026-01-15", "igual")]),
    ("21c", "Conector recto doble virola OD × NPT 1/4\" AISI 304/316 (ET 9.20)", '1/4"', "", "AISI 316", "NPT", 12, "un",
     [fuente("ant", 15, "ABAC conector recto c/tuerca y doble virola OD×NPT 1/4\" S-2000 AISI 304/316 (planilla TAVAL/40)", T40, "2026-01-15", "igual")]),
    ("21d", "Tubing de acero inoxidable 1/4\" × 0,89 mm (diferencial, purgas y controladores de nivel; ET 9.20)", '1/4"', "", "AISI 316", "—", 12, "m",
     [fuente("ant", 7, "ABAC tubing inoxidable 1/4\" esp. 0,89 mm AISI 304/316 a 7 USD/m (planilla TAVAL/40; mínimo 6 m)", T40, "2026-01-15", "igual")]),
    ("22", "Juntas espiraladas #600 de las conexiones internas: 1 de 6\", 6 de 2\" y 7 de 1\"", "", "600", "AISI 316 / grafito", "—", 1, "gl",
     [fuente("ant", 1 * 7 + 6 * 5 + 7 * 5, "Planilla TAVAL/37 FC-231: junta espiralada e = 4,5 mm c/anillo ext. #600 (6\": 7; 2\": 5; 1\": 5): 1 × 7 + 6 × 5 + 7 × 5", T37, "2025-12-17", "similar", "valores de planilla ITT; antes se usaba la cotización MS Juntas 48.729, que es de juntas #300 (otra serie: error de la revisión del 30-10-2026)")]),
    ("22b", "Segundo juego de juntas espiraladas #600 (ET 9.16.3: después de la PH se reemplazan las juntas antes de la prueba de fugas)", "", "600", "AISI 316 / grafito", "—", 1, "gl",
     [fuente("ant", 1 * 7 + 6 * 5 + 7 * 5, "Planilla TAVAL/37 FC-231: mismas juntas que la pos. 22", T37, "2025-12-17", "similar", "compra extra por el reemplazo de juntas que pide la ET 9.16.3 (auditoría 30-10-2026)")]),
    ("22c", "Espárragos totalmente roscados ASTM A193 B7 con 2 tuercas A194 2H, zincado bicromatizado (ET 9.13): 12 de 1\" (6\") y 76 de 5/8\" (48 para 2\" y 28 para 1\", ASME B16.5 #600)", "", "", "ASTM A193 B7 / A194 2H", "—", 88, "un",
     [fuente("ant", 10, "Espárragos con 2 tuercas 3/4\" × 125 mm A-193 B7 / A-194 2H zincados (Bules o Versailles, planilla TAVAL/43) · JUN-04181", CAT, "2026-02-19", "similar", "otra medida (3/4\"); las planillas ponen 10 a todas las medidas: pedir cotización a Petrobul / Versailles / Fornis")]),
    ("23", "Skid y plataforma de acceso con escalera, guarda hombre, baranda y zócalo de metal desplegado, cáncamos y orejas de PAT AISI 304 (1.300 kg estimados; ET 9.11)", "", "", "ASTM A-36", "—", KG_SKID, "kg",
     [fuente("cot", 17.4 / 13.4 * 1.10, "Grupo Provemet cot. 236623: UPN 120 a 17,40/m (1,30 USD/kg +10% recortes) como precio por kg de perfiles", "fuentes_originales/listas_vendedor/2026-10-28/provemet_cotizacion_236623_perfiles_2025-07-01.pdf", "2025-07-01", "similar", "kilos estimados")]),
    ("23b", "Piso de rejilla antideslizante tipo Techno de la tarima (para 2 personas, ET 9.11); se galvaniza en caliente con la plataforma (S05b)", "", "", "ASTM A36", "—", 3, "m2",
     [fuente("ant", 265, "Planilla TAVAL/37 FC-231: rejilla tipo TDL T3010040 SA-36 a 265 USD/m²", T37, "2025-12-17", "similar", "rejilla SA-36 sin galvanizar: el galvanizado va en S05b (+120 kg); antes SIN PRECIO porque la Avila galvanizada (OTR-02141) no dice el material")]),
    ("24", "Pollera / patas de apoyo (450 kg)", "", "e = 1\"", "ASTM A-36", "—", KG_POLLERA, "kg",
     [fuente("ant", 1.2744, "Chapa negra A36 (precios de acero por kg, J. Elejondo) +10% recortes", "conocimiento/precios/acero_por_kg.csv", "2026-02-10", "similar", "chapa 1/2\" de la lista (acá 1\")")]),
    ("25", "Placa de identificación de acero inoxidable remachada sobre soporte de chapa soldado al cuerpo (ET 9.12)", "", "", "AISI 316", "—", 1, "un",
     [fuente("ant", 15, "Planilla Sacde/12: chapa de identificación 100 × 200 × 3 mm AISI 316 · PER-03051", S12, "2025-12-18", "similar", "chapa de tag de instrumentos; la placa del equipo es más grande y grabada con los datos ASME")]),
]
with open(C / "pedido" / "lista_materiales_plano.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["pos", "descripcion", "diametro", "serie_sch", "material", "extremos", "modelo_fabricante", "cantidad", "unidad", "extremos_campo", "cantidad_origen", "nota"])
    for pos, desc, d, s, mat, ext, q, u, *_ in M:  # Camuzzi no entrega lista: toda la tabla es de ITT (lo dice el título en la oferta)
        w.writerow([pos, desc, d, s, mat, ext, "", q, u, 0, CANT_ITT, "diseño preliminar ITT (sin lista del cliente)"])
import atributos_plano  # noqa: E402
atributos_plano.completar(C)  # datos en columnas (Ø, serie, schedule, norma, marca…), 03-11-2026
CS = "SA-516 Gr. 70"  # lista de ITT: los datos de las piezas del recipiente se cargan a mano (el lector no los saca del texto)
atributos_plano.fijar(C, {
    "1": {"familia": "PER", "tipo": "chapa", "espesor_mm": "57.15", "medida": "virola DI 1.280 mm × 3,2 m", "norma": "ASME VIII Div.1"},
    "2": {"familia": "ABW", "tipo": "casquete semielíptico 2:1", "espesor_mm": "57.15", "norma": "ASME VIII Div.1"},
    "3": {"familia": "OTR", "tipo": "tapa de cierre rápido", "serie": "600", "medida": "para DI 1.280 mm", "marca": "Futura / Peco / Gora / EKA"},
    "4": {"familia": "PER", "tipo": "chapa", "espesor_mm": "41.3", "medida": "Ø 1,28 m, 37 agujeros"},
    "5": {"familia": "OTR", "tipo": "elemento coalescente", "medida": "140 × 914 mm", "rango": "0,3 µm", "marca": "Gora / Filtron / Peco"},
    "5b": {"familia": "OTR", "tipo": "elemento coalescente", "medida": "140 × 914 mm", "rango": "0,3 µm", "marca": "Gora / Filtron / Peco"},
})
items = []
for p, desc, d, s, mat, ext, q, u, f, *motivo in M:
    it = {"id": f"M{int(p.rstrip('abcd')):02d}{p.lstrip('0123456789')}", "pos": p, "grupo": "material", "descripcion": desc, "especificacion": f"{d} {s} {mat}".strip(), "cantidad": q, "unidad": u, "fuentes": f}
    if motivo:
        it["sin_precio_motivo"] = motivo[0]
    items.append(it)
ROL = C30 + "Sandri rolado de chapa esp 1.docx.txt"
items += [
    {"id": "S01", "pos": "ROL", "grupo": "servicio", "descripcion": f"Rolado y punteado de la virola ({fmt(kg_cuerpo, 0)} kg, 2 1/4\")", "especificacion": "taller con capacidad para 57,15 mm (Sandri cilindra hasta 50 mm: no sirve)",
     "cantidad": kg_cuerpo, "unidad": "kg", "fuentes": [fuente("est", 3.7, "Estimado: tarifa interna de ITT de rolado 3,70 USD/kg (tarifas.csv; en la planilla AESA/44 se aplica sobre el peso total de cada equipo), nunca cotizada para 57,15 mm", "conocimiento/costos/tarifas.csv", "2025-09-30", "similar", "criterio interno, no cotización (auditoría 30-10-2026); pedir cotización a un taller que cilindre 57,15 mm en DI 1.280 mm"),
                                                         fuente("cot", 2550000 / 1416.29 / 1033, "Juan y Víctor Sandri S.A.: cilindrado y punteado ARS 2.550.000 + IVA por virola de 1.033 kg (1,74 USD/kg)", ROL, "2026-03-25", "similar", "NO SIRVE para 2 1/4\": el membrete dice «cilindramos hasta 50 mm en 2500 mm de largo» (sí serviría con la opción de diseño de 1 5/8\")")]},
    {"id": "S02", "pos": "MO", "grupo": "mo", "descripcion": f"Fabricación del separador y del skid por tercero (armado, soldadura de un recipiente de pared normal, conexiones, internos, pollera, cáncamos, plataforma y montaje sobre skid; ≈ {fmt(kg_fabricado, 0)} kg)",
     "especificacion": f"Ledesma, recipientes a presión AESA/44: 4,15 USD/kg (desgasificador de 8.967 kg, pared ≈ 10 mm) × {fmt(kg_fabricado, 0)} kg (virola {fmt(kg_cuerpo, 0)} + fondo {fmt(kg_fondo, 0)} + placa {fmt(kg_placa, 0)} + skid {fmt(KG_SKID, 0)} + pollera {fmt(KG_POLLERA, 0)} + conexiones {fmt(KG_CONEX, 0)}); la soldadura extra por espesor va en S02b",
     "cantidad": kg_fabricado, "unidad": "kg",
     "fuentes": [fuente("cot", 37200 / 8967, "Edgardo Ledesma, presupuesto 20079 (desgasificador, USD 37.200 + IVA; 8.967 kg según la planilla «LC servicio de mano de obra»): virolas, soldaduras, casquetes, conexiones, refuerzos, internos, paso de hombre, escalera y plataforma", A44 + "5.Proveedores 3ros/Presupuesto ITT N° 20079 Desgasificador SB - 211 27-08-25.docx.txt", "2025-08-27", "similar",
                         "NO es el mismo alcance en soldadura: los recipientes de AESA/44 son de pared fina (2,5 m × 17 a 22 m, 6 a 16 t según el pedido de flete a Suan → ≈ 10 mm); acá 57,15 mm (la diferencia va en S02b). No incluye consumibles (S02c), rolado ni PH. Pedir a Ledesma la cotización con el diseño"),
                 fuente("cot", 13000 * 2.2 * math.sqrt(57.15 / 41.3), "Edgardo Ledesma: separador de polvo y líquido 28\" #600 + skid, USD 13.000 (no incluye plegado de cunas, PH ni END), × 2,2 por tamaño y × 1,18 por espesor", C30 + "E Ledesma - Cotización de Separador de polvo y líquido 28_ #600.pdf.txt", "2026-05-10", "similar", "28\" horizontal; el factor 2,2 por tamaño no tiene fuente y el 1,18 por espesor tampoco (era la base hasta el 30-10-2026)")]},
    {"id": "S02b", "pos": "MOE", "grupo": "mo", "descripcion": f"Soldadura extra del recipiente por espesor (2 1/4\" en lugar de la pared ≈ 10 mm de la referencia de Ledesma): {fmt(pulg_extra, 1)} pulgadas equivalentes",
     "especificacion": f"cuerpo: 3 circunferenciales Ø{fmt(D_EXT_PULG, 1)}\" + 2 longitudinales de 1,6 m = {fmt(PULG_CUERPO, 1)} pulg × (factor {fmt(F_CUERPO, 2)} − 1); placa portaelementos {fmt(DI / 0.0254, 1)}\" × (factor {fmt(F_PLACA, 2)} − 1); toberas que atraviesan la pared {fmt(PULG_TOBERAS, 0)}\" × (factor {fmt(F_CUERPO, 2)} − 1)",
     "cantidad": pulg_extra, "unidad": "pulg-eq",
     "fuentes": [fuente("est", 12, "Estimado: soldadura por pulgada equivalente de J. C. Quesada, USD 12 (presupuesto JQ-020-2026; incluye consumibles, herramental y calificación ASME IX) × pulgadas extra por espesor con la regla de factores_soldadura.csv (espesor ÷ 9,53)", "fuentes_originales/ofertas_texto/TAVAL/58 - Inarteco - ERPs tipo 1ra etapa - Litoral Gas/5.Proveedores 3ros/Cotizacion JQ-020-2026.pdf.txt", "2026-05-06", "similar",
                         "tarifa de piping aplicada a costuras de recipiente: estimado hasta la cotización de Ledesma con el diseño (auditoría 30-10-2026). La regla lineal en espesor subestima el metal depositado (crece con el cuadrado)")]},
    {"id": "S02c", "pos": "CONS", "grupo": "mo", "descripcion": "Consumibles de soldadura de la fabricación de Ledesma (su presupuesto de AESA/44 no los incluye)", "especificacion": "", "cantidad": 1, "unidad": "gl",
     "fuentes": [sin_precio("pedir a Ledesma la cotización con consumibles", "2026-10-30", "no hay precios de electrodos ni alambre en el catálogo (buscar_material.py, 30-10-2026); los de la soldadura extra van en S02b (Quesada los incluye)")],
     "sin_precio_motivo": "Faltaban (el presupuesto 20079 de Ledesma dice «No incluye … Consumibles», auditoría 30-10-2026) y no hay precio de consumibles en el catálogo: queda en 0 y frena hasta la cotización de Ledesma"},
    {"id": "S03", "pos": "RX", "grupo": "servicio", "descripcion": "Radiografía 100% de costuras y toberas", "especificacion": "43 placas grandes (16,3 m de costura del cuerpo ÷ 0,38 m por placa) + 46 chicas (soldaduras de bridas WN: 2 × 10\" a 3, 6\" a 2, 4 × 2\" a 2, 15 × 1\" a 2) = 89 placas → 2 visitas de hasta 45 placas", "cantidad": 1, "unidad": "gl",
     "fuentes": [fuente("cot", 2 * round(850000 / TC_OCT, 2) + 89 * round(15000 / TC_OCT, 2), f"Proveedor de RX (sin nombre), precio confirmado por Matías el 30-10-2026: 2 visitas × ARS 850.000 + 89 placas × ARS 15.000, sin IVA, a BNA oct-2026 ({fmt(TC_OCT)}) · END-00572 / END-00571", "conocimiento/precios/precios_usuario.csv", "2026-10-30", "similar", "la tarifa es la vigente; las placas se contaron por costura (antes 80 por criterio): confirmar con el mapa de soldaduras. TAVAL/37 cuenta 816 placas para el cuerpo (27.314), con una plantilla de «separador bifásico» de 50 soldaduras equivalentes de 22\": no es un conteo de su recipiente"),
                 fuente("ant", 43 * 8 + 46 * 6.5 + 2 * 408, "Tarifas DB NDT (tarifas.csv): 43 placas grandes × 8 + 46 chicas × 6,50 + 2 servicios × 408", "conocimiento/costos/tarifas.csv", "2026-08-31", "similar", "placas contadas por costura; confirmar con el mapa de soldaduras")]},
    {"id": "S03b", "pos": "LP", "grupo": "servicio", "descripcion": "Tintas penetrantes en 2ª y última pasada de las soldaduras que no se radiografían: toberas que atraviesan la pared, placa portaelementos, pollera, filetes (ET 9.15)", "especificacion": "2 servicios (2ª pasada y última pasada)", "cantidad": 2, "unidad": "servicio",
     "fuentes": [fuente("cot", 490, "NDT Antonelli (JCA & Asociados): líquidos penetrantes, USD 490 por servicio · END-00002", "fuentes_originales/antonelli_end_2025-11.pdf", "2025-11-03", "similar", "faltaba en el cómputo (la RX no lo cubre); cantidad de servicios por criterio")]},
    {"id": "S04", "pos": "PH", "grupo": "servicio", "descripcion": "Prueba hidráulica a 1,3 × la presión de la serie #600 (≈ 133 bar) durante 6 h, con registro y secado (ET 9.16)", "especificacion": "", "cantidad": 16, "unidad": "h", "fuentes": [fuente("ant", 13, "Prueba hidráulica por hora de planta (END-00215, MO ITT)", "conocimiento/precios/catalogo_servicios.csv", "2026-03-10", "similar", "16 h para un recipiente de ≈ 5 m³ (llenado, 6 h de prueba, vaciado y secado)")]},
    {"id": "S05", "pos": "PIN", "grupo": "servicio", "descripcion": "Granallado y pintura (≈ 58 m² + 20 % de overspray)", "especificacion": "recipiente 25,5 m² (ficha_rubros.md: cuerpo, fondo, pollera, tapa y toberas) + skid sin la plataforma galvanizada ≈ 800 kg × 40 m²/t (ficha: 52,5 m² por 1.300 kg) ≈ 32 m² (antes 38 m² por criterio); × 1,2 de overspray como la planilla del precio", "cantidad": round(58 * 1.2, 1), "unidad": "m2",
     "fuentes": [fuente("ant", 37.98, "Pintor (sin nombre) · PIN-00579 (precio confirmado por Matías)", "conocimiento/precios/precios_usuario.csv", "2026-10-30", "similar", "Granallado y pintura de piping y skid, incluye materiales: USD 37,98/m² confirmado por Matías Russo el 30-10-2026 (precio firme, PIN-00579); la planilla de origen (YPF Lic 66944 colectores) lo aplica sobre los m² + 20 % de overspray, por eso la cantidad va × 1,2; esquema SCE-PC-511-0003 a confirmar"),
                 fuente("ant", 50, "Granallado y pintura piping (incluye materiales), criterio ITT · PIN-00569", "conocimiento/precios/catalogo_servicios.csv", "2026-10-10", "similar", "esquema SCE-PC-511-0003 sin el documento (consulta C5); pinturas del listado: Sherwin Williams / Hempel")]},
    {"id": "S05b", "pos": "GALV", "grupo": "servicio", "descripcion": "Galvanizado en caliente de plataforma, escalera, baranda y rejilla (≈ 620 kg, ET 9.11)", "especificacion": "500 kg de plataforma + 120 kg de rejilla (3 m² × ≈ 40 kg/m²)", "cantidad": 620, "unidad": "kg",
     "fuentes": [fuente("ant", 2.0, "Galvanizado de terceros 2,00 USD/kg (TAVAL/49) · PIN-00465", "conocimiento/precios/catalogo_servicios.csv", "2026-03-10", "similar", "kilos estimados de la plataforma y la rejilla")]},
    {"id": "S05c", "pos": "FUG", "grupo": "servicio", "descripcion": "Prueba de fugas con aire seco o nitrógeno a 5,5 bar con solución jabonosa, después de pintar (ET 9.16.3)", "especificacion": "8 h de planta + nitrógeno", "cantidad": 8, "unidad": "h",
     "fuentes": [fuente("ant", 13, "Horas de planta para movimientos internos y PH · END-00563", "conocimiento/precios/catalogo_servicios.csv", "2026-10-10", "similar", "8 h por criterio; el nitrógeno va incluido como estimado")]},
    {"id": "S05d", "pos": "API", "grupo": "servicio", "descripcion": "Calificación de procedimientos y soldadores según API 1104 con registro IRAM-IAS U500-138 (ET 9.14)", "especificacion": "", "cantidad": 1, "unidad": "gl",
     "fuentes": [sin_precio("pedir cotización a un ente habilitado (o confirmar si Ledesma o ITT ya tienen procedimientos API 1104 vigentes)", "2026-10-29", "no hay precio de calificación API 1104; Ledesma incluyó «procedimiento de soldadura y calificación de soldadores» en CAMUZZI/30, sin decir la norma")],
     "sin_precio_motivo": "Sin referencia de calificación API 1104 con registro IRAM-IAS: pedir a Ledesma si su calificación cumple, o cotización a un ente habilitado (lista para Compras)"},
    {"id": "S05e", "pos": "PWHT", "grupo": "servicio", "descripcion": "Tratamiento térmico post soldadura del recipiente (ASME VIII Div.1 UCS-56: acero P-No.1 de más de 38 mm; acá 57,15 mm)", "especificacion": f"recipiente de ≈ {fmt(kg_cuerpo + kg_fondo + kg_placa + KG_CONEX, 0)} kg (sin skid), en horno o localizado, con registro", "cantidad": 1, "unidad": "gl",
     "fuentes": [sin_precio("pedir cotización de tratamiento térmico", "2026-10-30", "no hay tratamiento térmico en el catálogo de servicios (buscar_servicio.py, 30-10-2026)")],
     "sin_precio_motivo": "Faltaba en el cómputo (con 2 1/4\" el código lo exige) y no hay referencia en el catálogo: pedir cotización de tratamiento térmico en horno (lista para Compras)"},
    {"id": "S06", "pos": "HH", "grupo": "mo", "descripcion": "Ingeniería: memoria de cálculo ASME VIII Div.1, planos y documentación", "especificacion": "250 h (antes 150 h; Sacde/12 y TAVAL/37: 250 h)", "cantidad": 250, "unidad": "h",
     "fuentes": [fuente("ant", 15, "Horas propias ITT (15 USD/h): 250 h, como los coalescedores Sacde/12 y TAVAL/37 (250 h cada uno); decisión de Matías 30-10-2026", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "horas de coalescedores más chicos (Ø32\"–36\"); la ET pide memoria de cálculo")]},
    {"id": "S07", "pos": "CAL", "grupo": "mo", "descripcion": "Calidad, inspecciones y data book", "especificacion": "250 h (antes 120 h; Sacde/12 y TAVAL/37: 250 h)", "cantidad": 250, "unidad": "h",
     "fuentes": [fuente("ant", 15, "Horas propias ITT (15 USD/h): 250 h, como los coalescedores Sacde/12 y TAVAL/37 (250 h cada uno); decisión de Matías 30-10-2026", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "horas de coalescedores más chicos (Ø32\"–36\"); la ET pide memoria de cálculo")]},
    {"id": "S08", "pos": "ARM", "grupo": "mo", "descripcion": "Montaje propio: instrumentos, purgas, stand-pipes, tubing, movimientos y PH", "especificacion": "160 h", "cantidad": 160, "unidad": "h",
     "fuentes": [fuente("est", 16, "Horas propias ITT (16 USD/h en recipientes); criterio (Sacde/12: movimientos internos 72 h, desarme 54 h y armado final 675 h con la cañería del skid)", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "estimado")]},
]
base = json.load(open(C.parent / "_plantilla" / "cotizacion.json", encoding="utf-8"))
base.update({"codigo": "COT26-0135-003", "fecha": "2026-10-29", "cliente": {"nombre": "CAMUZZI GAS PAMPEANA S.A. / CAMUZZI GAS DEL SUR S.A.", "codigo_itt": "0135", "comprador": "Gerencia de Abastecimiento Obras y Almacenes (Juan Filas)"},
             "titulo": "Camuzzi · Concurso de precios N° 24578 ítem 1 / Concurso N° 24527 — 2 separadores verticales coalescentes (diseño preliminar ITT según ET)",
             "titulo_pagina": "Cotización Camuzzi CP 24578 · Separador coalescente", "archivo_planilla": "CAMUZZI_CP24578_SEPARADOR_COALESCENTE",
             "subtitulo_planilla": f"2 separadores verticales coalescentes Ø55\" #600, {N_ELEM} elementos + juego de repuesto · diseño preliminar ITT según ET · USD sin IVA",
             "meta": ["Concurso de precios N° 24578 · ítem 1 / Concurso N° 24527", "ET Separador Vertical Coalescente y esquema general de Camuzzi; diseño preliminar ITT", "Comprador: Camuzzi (portal de compras)", "Preparó: Matías Russo · 29-10-2026 · revisado renglón por renglón el 30-10-2026"],
             "equipo": {"singular": "separador", "plural": "separadores", "tipo": "filtro", "diametro_pulg": 55}, "items": items})
# Flete: planilla ITT de AESA/44, hoja «Transporte» (09-2025): recipiente SB-003 (17 t) 1.750 + 780 de adicional; acá 2 equipos de ≈ 10 t
# (antes ARS 1.400.000 por un camión con hidrogrúa para los dos: estimado sin fuente, poco para ≈ 20 t). Destino a confirmar (consulta C3).
base["parametros"].update({"N": 2, "fecha_referencia": "2026-10-31", "rx_pct": 0, "ph_horas": 0, "TRANS": 1, "TC": TC_OCT, "TR_ARS": round(2 * 2530 * TC_OCT, -3), "TR_EMB": 300, "TR_F": 1.0})
# Plazo rehecho con la auditoría del 30-10-2026: la tapa la cotiza Futura a 120 días (Sacde/12, "Oferta de Futura … plazo 120 dias"; Megatap
# 90/110 no está en el listado) y se pide recién con el plano aprobado por Camuzzi (ET 7.1 y 10: no se avanza sin plano mecánico aprobado).
# La ET no fija el plazo de revisión de Camuzzi: se suponen 15 días corridos y la oferta lo dice. Margen de 15% de plazos.md §4: 200 × 1,15 = 230.
base["plazo"] = {"dias": 230, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Memoria de cálculo, plano mecánico y procedimientos para calificación de Camuzzi", 0, 25, ""],
                            ["Revisión y aprobación de la documentación por Camuzzi (supuesto: 15 días corridos; la ET no lo fija)", 25, 40, ""],
                            ["Tapas de cierre rápido #600 (Futura, 120 días desde la orden con los datos de diseño aprobados; Sacde/12)", 40, 160, "crit"],
                            ["Chapa, rolado, bridas, elementos y fabricación del cuerpo y el skid (Ledesma)", 40, 150, ""],
                            ["Soldadura del cuello de la tapa, RX, tratamiento térmico y PH", 160, 182, "tal"],
                            ["Instrumentos, pintura, prueba de fugas, inspección de Camuzzi (aviso 5 días hábiles) y despacho", 182, 200, "tal"]],
                 "nota": "Calculado 200 días (tapa Futura de 120 días pedida con el plano aprobado + taller); se ofrecen 230 con el margen de 15% de plazos.md §4. El histórico de separadores es 370 días.",
                 }
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)", "referencia_html": "<b>Estimado:</b> 2 viajes de semirremolque (un separador de ≈ 10 t por viaje) a 1.750 + 780 USD por equipo: costo de transporte que ITT cargó para el recipiente SB-003 (17 t, 11 × 3,7 × 3,7 m, Quilmes → Canning) en la hoja «Transporte» de su planilla «LC servicio de mano de obra» de AESA/44 (09-2025), no una cotización de transportista; + USD 300 de embalaje.",
                 "criterio_html": "La planilla del concurso pone el flete a cargo del proveedor hasta Transporte Cruz del Sur; el Concurso 24527 y la ET dicen destino final (consulta C3)."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · ítem 1 / Concurso N° 24527", "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"],
                  ["Ítem", "1 · Separador vertical coalescente sobre skid con plataforma · <b>2 un</b>"], ["Condiciones", "Pe máx 70 bar · Pe mín 25 bar · Qmáx 100.000 Sm3/h · filtrado 0,3 µm · cartuchos 140 × 914 mm"],
                  ["Documentos", "Planilla del concurso; ET Separador Vertical Coalescente (22 hojas); Esquema General Filtro Coalescente Camuzzi 2026; listado de marcas SCE-IN-501-0015 (mail de B. Raminger, Taval, 14-10-2026)"],
                  ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (CP 24578); destino final a determinar (Concurso 24527)"]],
                  "requisitos_html": ["Entrada y salida a 180°, preferentemente 10\" #600", "Purga automática; switch de nivel alto Ex-d sobre stand-pipe en ambas cámaras; visor de nivel en ambas cámaras",
                                      "Manómetro diferencial con aguja de arrastre y contacto seco; manómetro estático", "Boca de inspección 6\" #600 a 90° de la entrada",
                                      "Salida a 200 mm del límite superior de los cartuchos; 40 mm entre elementos", "Un juego de elementos instalado y un juego adicional de repuesto por equipo (ET 13.1)",
                                      "ASME VIII Div.1, corrosión 1,6 mm; PH a 1,3 × presión de la serie #600 durante 6 h; prueba de fugas a 5,5 bar; RX 100%; soldadura API 1104; tratamiento térmico por espesor (UCS-56)",
                                      "2 purgas automáticas neumáticas 1\" bridadas con drenajes manuales; caja de chicanas AISI 304; tapa de apertura rápida no roscada con pescante",
                                      "Plataforma galvanizada en caliente con rejilla, guarda hombre y zócalo; skid UPN con cáncamos; materiales del listado de marcas de Camuzzi",
                                      "<b>Con la oferta:</b> memoria de cálculo (cantidad de elementos, diámetros, espesores) y esquema con dimensiones generales",
                                      "Matriz completa de requisitos con su destino: <code>pedido/requisitos.csv</code>; consultas al cliente: <code>consultas_cliente.md</code>"]}
base["nota_mo_html"] = (f"Diseño preliminar: {N_ELEM} elementos, cuerpo DI 1.280 mm × {fmtg(L_CUERPO)} m × 2 1/4\" SA-516-70 ({fmt(kg_cuerpo, 0)} kg) a la presión de la serie #600, fondo 2:1, tapa de cierre rápido superior, 2 cámaras. "
                        f"Fabricación por tercero (Ledesma, a 4,15 USD/kg de sus presupuestos de recipientes de AESA/44 × {fmt(kg_fabricado, 0)} kg); ITT pone ingeniería, calidad, montaje de instrumentos, rolado, RX, tratamiento térmico, PH y pintura.")
base["desvios"] = [{"tag": "Todo", "titulo": "Diseño preliminar", "texto": "La cantidad de elementos y el diámetro salen de un dimensionamiento preliminar (108 m³/h por elemento de Sacde/12); hay que confirmar con la ficha del elemento y la pérdida de carga máxima de 100 mbar (ET 9.1) en la memoria de cálculo antes de presentar."},
                   {"tag": "Flete", "titulo": "Lugar de entrega", "texto": "La ET y el Concurso 24527 dicen destino final; la planilla del CP 24578, Transporte Cruz del Sur. Se cotiza según la planilla (consulta C3)."},
                   {"tag": "Plazo", "titulo": "Plazo de entrega", "texto": "El Concurso 24527 pide 30 días corridos: imposible con una tapa de cierre rápido de 90/110 días. Se ofrece el plazo calculado (desvío declarado en la oferta)."},
                   {"tag": "Moneda", "titulo": "Moneda", "texto": "El Concurso 24527 y el pliego general piden cotizar en pesos (USD solo para importados): se cotiza en USD como en CAMUZZI/30 (desvío declarado en la oferta)."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>CAMUZZI/30</b> · Concurso 22737", "fecha": "14-05-2026", "que": "2 separadores horizontales de polvo y líquido 28\" #600, 11 elementos 140 × 914", "precio": "venta 93.033 c/u", "tomado_html": "Solo de control: Ledesma 13.000 (fuente alternativa de S02), Sandri (descartado: hasta 50 mm), Gora 46600 y caja de chicanas (comparación del elemento y de las chicanas)"},
    {"carpeta_html": "<b>Sacde/12</b> · Filtro coalescente FC-301/302", "fecha": "18-12-2025", "que": "Coalescedor 36\" #600, 16 elementos, planilla de costo", "precio": "costo con planilla", "tomado_html": "Caudal por elemento, chapa por kg, cabezal, tapa Futura, válvula de purga y switch de nivel"},
    {"carpeta_html": "<b>TAVAL/37</b> · Filtro coalescedor FC-231 YPF", "fecha": "17-12-2025", "que": "Coalescedor 32\" #600, 16 elementos, con 2 skids de cañería 10\"/16\", válvulas 10\" e instrumentación cableada", "precio": "costo 407.845", "tomado_html": "Elemento (misma plantilla que Sacde/12), caja de chicanas AISI 304, rejilla, juntas #600; comparación P8 rubro por rubro"},
    {"carpeta_html": "<b>AESA/44</b> · Fabricación de recipientes (Ledesma)", "fecha": "27-08-2025", "que": "Presupuestos de Ledesma por recipiente a presión (2,2 a 11,9 t)", "precio": "3,14 a 5,15 USD/kg", "tomado_html": "MO de fabricación por kg (recipientes de pared fina), rolado (tarifa interna) y flete (planilla ITT)"}]
base["pendientes"] = [{"titulo": "Ingeniería", "items": ["<b>CRÍTICO para presentar:</b> el concurso exige entregar con la cotización la memoria de cálculo y el esquema con dimensiones generales; sin eso la oferta incumple el ítem 1 (requisitos R017 y R018, frenan)", "Memoria de cálculo ASME VIII (espesores, refuerzos de toberas, placa portaelementos, temperatura mínima y Charpy) y dimensionamiento con el fabricante de elementos: caudal por elemento a 25 bar y pérdida de carga ≤ 100 mbar", "Esquema con dimensiones generales (lo pide el concurso con la oferta)"]},
                      {"titulo": "Consultas al cliente (frenan la oferta)", "items": ["Ver <code>consultas_cliente.md</code>: C1 concurso y fecha de apertura del 24527; C2 elemento celulósico (ET) o coalescente (planilla); C3 destino final; C4 temperatura de diseño; C5 especificaciones SCE (pintura, válvulas, soldadura, manómetros)"]},
                      {"titulo": "Proveedores (marcas del listado de Camuzzi)", "items": ["Tapa de cierre rápido #600 vertical DI 1.280 mm (Futura, Peco, Gora o EKA)", "Elementos 0,3 µm 140 × 914 (Gora, Filtron, De Nichilo, Panden, SP): 74 por equipo con el repuesto", "Purgas automáticas neumáticas 1\" #600, control de nivel a flotante (Epta, Fisher) y regulador de gas de instrumentos; switches de nivel Ex-d (Magnetrol, Murphy)", "Válvulas esféricas 1/2\", 1\" y 2\" y tapón lubricado 1\" de marcas del listado", "Visores reflex Riva para 102 bar; manómetro diferencial Wika con aguja de arrastre y contacto", "Caja de chicanas AISI 304 (Gora) con el tamaño del diseño", "Tratamiento térmico post soldadura; calificación API 1104 (o confirmar la de Ledesma)", "Fabricación (Ledesma) con el diseño y rolado de 57,15 mm (Sandri no llega: hasta 50 mm)", "Reconfirmar bridas, caños, perfiles y listas de Taval (vencidos)"]}]
base["planilla_notas"] = ["Plazo: 230 días desde OC (calculado 200: documentación 25 + revisión de Camuzzi 15 supuestos + tapa Futura 120 + taller 40; margen 15%).", "Precio preliminar ±30%: diseño ITT según la ET, sin memoria de cálculo ni cotizaciones de tapa, elementos, visores, válvulas 1\", tapón, regulador, tratamiento térmico ni API 1104."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar; diseño preliminar."
PROV_BRIDA = "Francovigh / CH / Thorsa / Forja Atlas (listado Camuzzi)"
PROV_ESF = "Esferomatic / Worcester / Valvtronic / Pentair / Indave / Wenlen / Beta / Valmec"
PROV_INOX = "ABAC / Swagelok / Parker / Fittinox / Casucci"
base["compras"] = {"fecha_respuesta": "2026-11-06", "material_en_planta_dias": 110, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo y validez.", "Certificados 3.1 de chapas, bridas y caños.", "Las cantidades son por separador × 2.", "Solo marcas del listado SCE-IN-501-0015 de Camuzzi (indicado por renglón)."],
                   "notas": {"1": "SA-516 Gr. 70 (70N si la memoria lo pide por temperatura mínima), 2 1/4\", certificado 3.1", "3": "Vertical, DI 1.280 mm #600, diseño a la presión de la serie (102 bar), con pescante y o-rings de repuesto", "5": "0,3 µm, 140 × 914 mm; indicar material (celulósico o coalescente), caudal por elemento a 25 bar y pérdida de carga limpio", "5b": "Repuesto: mismo elemento",
                             "14b": "A216 WCB, con certificados de fabricación y prueba (ET 9.18)", "14c": "Tapón lubricado de sacrificio 1\" #600 RF", "15": "1/2\" NPT serie 2000 A105, paso total", "16": "Neumática NC, internos inox, cierres stellite 6, bridada 1\" #600 RF", "16b": "Interruptor a flotante on-off para comandar la purga neumática", "16c": "Gas de instrumentos desde la línea (102 bar de diseño)",
                             "17": "Ex-d, para stand-pipe 2\"", "18": "Reflex 500 mm, apto para 102 bar de diseño (#600), con válvulas de bloqueo y purga", "19": "Diafragma 0-2 bar Ø3\", aguja de arrastre y contacto seco, estática máx. 100 bar", "21": "Doble bolsillo AISI 304 para entrada 10\" en DI 1.280 mm", "22": "Espárragos ASTM A193 B7 totalmente roscados con tuercas A194 2H, zincado electrolítico bicromatizado (ET 9.13)", "20": "Ø100, clase 1, caja AISI 304, bourdon AISI 316, glicerina, 1/2\" NPT, IP65, certificado de calibración (ET 9.19.1)"},
                   "proveedores": {"3": "Futura / Peco / Gora / EKA", "5": "Gora / Filtron / De Nichilo / Panden / SP", "5b": "Gora / Filtron / De Nichilo / Panden / SP", "6": PROV_BRIDA, "8": PROV_BRIDA, "9": PROV_BRIDA, "11": PROV_BRIDA, "13": PROV_BRIDA,
                                   "14": PROV_ESF, "14b": PROV_ESF, "14c": "Xomox-Tufline / Nordstrom / Favra", "15": PROV_ESF, "16": "Bettis / Bray / Flow / Wenlen (actuador)", "16b": "Epta / Fisher / Magnetrol / Kimray", "16c": "Fisher / Epta",
                                   "17": "Magnetrol / Murphy / Kimray / Jefferson / Farinola", "18": "Riva Hnos", "19": "Wika", "19b": "ABAC / Casucci", "20": "Weisz / Wika / ABAC / Casucci", "20b": "ABAC / Casucci", "21": "Gora", "21b": PROV_INOX, "21c": PROV_INOX, "21d": PROV_INOX,
                                   "22": "Juntas Klinger / Teadit / Flexseal / Garlock; espárragos Petrobul / Versailles / Fornis"},
                   "cantidad_compra": {}, "servicios": [{"servicio": "Rolado de virola DI 1.280 mm × 2 1/4\" (57,15 mm)", "proveedores": "taller con capacidad (Sandri llega a 50 mm)", "referencia": "3,70 USD/kg (AESA/44, 2025)", "nota": "pedir con el desarrollo de la memoria"},
                                                        {"servicio": "Fabricación del separador y skid", "proveedores": "Ledesma", "referencia": "4,15 USD/kg (AESA/44, 08-2025); 13.000 el 28\" de CAMUZZI/30 (05-2026)", "nota": "con el diseño; aclarar consumibles y calificación API 1104"},
                                                        {"servicio": "Tratamiento térmico post soldadura (UCS-56)", "proveedores": "a definir", "referencia": "sin referencia", "nota": "recipiente de ≈ 8 t, DI 1.280 mm × ≈ 4 m"},
                                                        {"servicio": "Calificación API 1104 con registro IRAM-IAS U500-138", "proveedores": "ente habilitado / Ledesma", "referencia": "sin referencia", "nota": "ET 9.14"},
                                                        {"servicio": "Flete de 2 separadores de ≈ 10 t", "proveedores": "Suan / otros", "referencia": "1.750 + 780 USD por equipo (planilla ITT de AESA/44, hoja Transporte, 09-2025; no es cotización)", "nota": "destino a confirmar con Camuzzi (consulta C3)"}]}
base["origen_lista"] = {"tipo": "diseno_itt", "motivo": "Camuzzi no da tabla de materiales: la ET pide que el oferente diseñe el separador; la lista es el cómputo del diseño preliminar de ITT (bitacora.md)"}
# Reescrita el 30-10-2026 con la hoja «Mano de Obra de ITT» de TAVAL/37 (la versión anterior decía que su MO era toda de cañería: falso).
TAV37 = ("TAVAL/37 (FC-231 YPF, 17-12-2025, planilla LM costos Coalescedor FC-231 REV. 0) costó 407.845 por equipo; acá 249.210 a precios de origen "
         "(278.697 ajustado). Rubro por rubro, por equipo: (1) materiales del recipiente: TAVAL/37 54.951 (hoja PC0-C, bloque Cuerpo: acceso con brida ciega "
         "32\" de 5.400, sin tapa de cierre rápido, y 16 elementos a 854 = 13.664); acá 137.376, de los que la tapa de cierre rápido (42.103) y los 74 elementos "
         "con el juego de repuesto (63.196) suman 105.299. (2) MO del recipiente: TAVAL/37 soldadura del cuerpo principal y cunas 36.858 + RX del cuerpo 27.314 "
         "(hoja Mano de Obra de ITT) + ≈ 1.125 h de montaje del tacho (corte, soldaduras, armado, internos, trazado, conexionado y pollera, hoja Costura + HH, "
         "≈ 18.000) ≈ 82.200; acá rolado 22.315 + Ledesma 39.807 + soldadura extra por espesor 16.812 + RX 1.969 + LP 980 = 81.882 (sin consumibles ni "
         "tratamiento térmico, que siguen en 0). (3) Lo que TAVAL/37 tiene y este no: cañería y skids 67.658, instrumentación y válvulas 82.861 (3 esféricas "
         "10\" #600 de 7.052 a 7.552, BDV, SDV, PSV, transmisores, cables y cajas Ex), MO de la cañería de los skids A y B (soldadura 34.584, RX 24.882), "
         "≈ 860 h de montaje de cañería, PH y armado final (≈ 13.800) y estructura 10.841: ≈ 235.000. Acá instrumentos y válvulas 12.214 (con 7 renglones "
         "en 0) y skid 3.226. La diferencia total sale del alcance (3), compensada en parte por la tapa y los elementos (1); la MO del recipiente da parecida. "
         "Nota: el conteo de RX del cuerpo de TAVAL/37 (816 placas) viene de una plantilla de «separador bifásico» con 50 soldaduras equivalentes de 22\", "
         "no de su recipiente.")
base["justificaciones"] = {"antecedentes": TAV37}
base["historial_html"] = ["30-10-2026: revisión completa renglón por renglón (bitacora.md): armar_json.py sincronizado con las decisiones del 30-10, tapa por DI, rolado y fabricación con fuentes de recipientes, tratamiento térmico, purgas, switches, chicanas, accesorios inox, matriz de requisitos y consultas."]
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

PLAZO = base["plazo"]["dias"]
DESV_MONEDA = ("Moneda: cotizamos en dólares estadounidenses, sin IVA, a facturar en pesos al tipo de cambio BNA divisa vendedor del día de la facturación (cláusulas particulares). "
               "Las cláusulas particulares del Concurso N° 24527 y el pliego general piden cotizar en pesos (en dólares solo materiales importados o con componentes extranjeros): "
               "el equipo lleva componentes importados y precios de proveedores en dólares.")
DESV_PLAZO = (f"Plazo de entrega: {PLAZO} días corridos desde la orden de compra. El plazo de 30 días corridos de las cláusulas particulares del Concurso N° 24527 "
              "no es posible por el plazo de fabricación de la tapa de cierre rápido (90 a 110 días desde la certificación de los datos de diseño) y el tratamiento térmico del recipiente.")
DESV_ELEMENTO = ("Elementos filtrantes: ofrecemos elementos coalescentes de 0,3 µm, cartucho de 914 × 140 mm, según la planilla de cotización. "
                 "La especificación técnica (punto 9) indica elementos de material celulósico con malla reforzada y armadura zincada; "
                 "si Camuzzi requiere elementos celulósicos, se ajustará la oferta.")
DESV_MANIFOLD = ("Manifold de 3 vías del manómetro diferencial en acero inoxidable, homologado en el Listado de Marcas y Proveedores SCE-IN-501-0015, "
                 "en lugar de acero zincado (especificación técnica 9.19.2).")
camuzzi_comun.oferta(C, "COT26-0135-003", "Separador coalescente", 1, "separador vertical coalescente sobre skid con plataforma de acceso (filtrado 0,3 µm, Pe 25-70 bar, Qmáx 100.000 Sm3/h)", "2", PLAZO,
                     ["Concurso de precios N° 24578 / Concurso N° 24527: planilla de cotización, cláusulas particulares y condiciones generales", "Especificación técnica Separador Vertical Coalescente (rev. 0) y Esquema General Filtro Coalescente Camuzzi 2026", "Listado de Marcas y Proveedores SCE-IN-501-0015"],
                     f"Separador vertical coalescente de dos cámaras con caja de chicanas AISI 304, cuerpo DI 1.280 mm en SA-516-70 de 2 1/4\", diseño ASME VIII Div.1 a la presión de la serie #600 con 1,6 mm de corrosión y tratamiento térmico post soldadura, conexiones 10\" #600 a 180°, {N_ELEM} elementos filtrantes 0,3 µm de 140 × 914 mm, tapa de apertura rápida no roscada con pescante, boca de inspección 6\" #600, 2 purgas automáticas neumáticas 1\" con drenajes manuales, switch de nivel Ex-d y visor en cada cámara, manómetros diferencial y estático, sobre skid con plataforma de acceso galvanizada.",
                     ["Diseño preliminar según la especificación de Camuzzi: el recipiente se diseña a la presión máxima de la serie ANSI #600 (102,1 bar) para cumplir la prueba de resistencia a 1,3 veces esa presión (ET 9.16.1). Se entregará la memoria de cálculo y el esquema con dimensiones generales.",
                      "Un juego de elementos instalado y un juego adicional de repuesto por equipo.",
                      DESV_ELEMENTO, DESV_MANIFOLD, DESV_MONEDA, DESV_PLAZO,
                      "Entrega en Transporte Cruz del Sur según la planilla del concurso (la especificación indica destino final)."],
                     ["Memoria de cálculo y planos para aprobación.", "Suministro de materiales, elementos e instrumentos.", "Fabricación, RX, tratamiento térmico, PH, prueba de fugas, pintura y montaje sobre skid con plataforma.", "Data book.", "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
of = json.load(open(C / "oferta.json", encoding="utf-8"))
of["titulo_materiales"] = "LISTA DE MATERIALES ELABORADA POR ITT SEGÚN LA ESPECIFICACIÓN TÉCNICA Y EL ESQUEMA DE CAMUZZI (EL CLIENTE NO ENTREGA LISTA; POR SEPARADOR)"
of["condiciones"]["PLAZO DE ENTREGA"] = (f"{PLAZO} días corridos desde la orden de compra. Considera 15 días corridos de revisión de Camuzzi en cada entrega de "
                                         "documentación para calificación; demoras mayores en la aprobación corren el plazo en igual medida.")
of["cliente"]["referencia"] = "Concurso de precios N° 24578 (ítem 1) / Concurso de precios N° 24527 – Filtro Coalescente"
of["objeto"] = ("El presente documento tiene por objeto establecer el alcance de nuestra Oferta {tipo} según los requerimientos solicitados por el cliente en el Concurso de precios "
                "N° 24578, ítem 1, y en el Concurso de precios N° 24527: 2 separadores verticales coalescentes sobre skid con plataforma de acceso (filtrado 0,3 µm, Pe 25-70 bar, "
                "Qmáx 100.000 Sm3/h), en un todo de acuerdo con la documentación del concurso y con las aclaraciones y desvíos indicados en nuestra Oferta Técnica.")
json.dump(of, open(C / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "ítems · cuerpo", kg_cuerpo, "kg · fondo", kg_fondo, "kg · placa", kg_placa, "kg · fabricado", kg_fabricado, "kg · exponente tapa", round(EXP_TAPA, 3))
