"""Listas preliminares COT26-0010-002 (AESA C5297, filtros coalescedores FC-301/302).

Genera resumen_pedido.md y listas_preliminares.xlsx en esta carpeta.
Las cantidades son POR FILTRO (un skid); la columna "Total" es por los 2 equipos.
Origen de cada dato: P&ID 5297-02-0000-IG-PR-PI-005 (hoja 2, FC-301), HD 5297-02-0100-IG-EM-HD-001,
plano PL 5297-02-0100-IG-EM-PL-001, clases L0200 Anexo I (CE32, CK11, CK31, CA11) o criterio ITT.
Lo marcado "ITT" es una decisión nuestra (pedido de Matías, 25-11-2026: "si falta info, decidimos con el
mejor criterio o por antecedentes"); se revisa en la ingeniería de detalle.

Uso: python cotizaciones/COT26-0010-002_AESA_C5297_FILTROS_COALESCEDORES/listas_preliminares.py
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', '..', 'herramientas'))
import numeros  # noqa: E402

N_EQUIPOS = 2

# ---------------------------------------------------------------------------
# 1. Plano PL-001: tabla de LDM (texto literal del cliente) y lista de conexiones
# ---------------------------------------------------------------------------
LDM_PLANO_ = [  # pos, cant, descripción literal, peso un. kg, material/línea literal
    ('001', 1, 'RECIPIENTE FC-301 / FC-302 C/INSTRUMENTOS', 7250, ''),
    ('501', 1, 'VALVULA ESFERICA NPS 10 CL.600 ASME B16.5 RF C/REDUCTOR', 732, 'SA-216 WCB + A°I° 316'),
    ('601', 1, 'CAJA JUNCTION BOX - POTENCIA TRACING', 30, ''),
    ('605', 3, 'CAJA JUNCTION BOX - INSTRUMENTOS', 30, ''),
    ('1000', 1, 'CHASIS BASE', 5642, ''),
    ('1500', 1, 'PLATAFORMAS Y ESCALERA', 2690, ''),
    ('1900', 1, 'ESCALON ACCESO MH', 48, ''),
    ('2000', 1, 'CANALIZACIONES INSTRUMENTOS', 77, ''),
    ('2001', 1, 'SALIDA DE GAS NPS 10 SCH80 CL.600', 2116, '10"-GH-0269-CE32-BB'),
    ('2002', 1, 'CAÑERIA DE ENTRADA NPS 10 SCH80 CL.600', 1863, '10"-GH-0176-CE32-BB'),
    ('2003', 1, 'SALIDA DE VAL. PSV NPS 2 SCH160 CL.600', 598, '2"-V-0262-CE32-BB'),
    ('2004', 1, 'SALIDA A VENTEO NPS 8 SCH40 CL.150', 290, '8"-V-0268-CK11-BB'),
    ('2005', 1, 'CAÑERIA BDV NPS4 CL.600 / NPS2 CL.150', 584.7, '4"-GH-0750-CE32-BB'),
    ('2006', 1, 'SALIDA INFERIOR CONDENSADO NPS2 CL.600', 301.6, '2"-LH-0272-CE32-BE'),
    ('2008', 1, 'SALIDA SUPERIOR DE CONDENSADO NPS2 CL.600', 279.0, '2"-LH-0271-CE32-BE'),
    ('2009', 1, 'CAÑERIA AIRE INSTRUMENTOS NPS2 SCH40 CL.150', 31.0, '2"-IA-0601-CA11-BB'),
    ('2010', 1, 'SALIDA DRENAJE ABIERTO NPS2 CL.150', 56, '2"-OD-0276-CA11-BB'),
    ('2011', 1, 'SALIDA DRENAJE CERRADO NPS2 CL.150', 166.7, '2"-PD-0275-CE32-BE'),
]
LDM_PLANO = [(a, b, c, float(d), e) for a, b, c, d, e in LDM_PLANO_]
PESO_TOTAL_PLANO = 22320.0  # "PESO TOTAL (S/INSTRUMENTAL Y CABLEADOS)"

CONEXIONES_PLANO = [  # límites del skid (tie-ins), literal del plano
    ('AI', '2', 'B16.5', 'WN RF', 'Sch 40', '150', 'AIRE INSTRUMENTOS'),
    ('DA', '2', 'B16.5', 'WN RF', 'Sch 40', '150', 'DRENAJE ABIERTO'),
    ('DC', '2', 'B16.5', 'WN RF', 'Sch 160', '150', 'DRENAJE CERRADO'),
    ('SL', '2', 'B16.5', 'WN RF', 'Sch 160', '600', 'SALIDA LIQUIDO'),
    ('EG', '10', 'B16.5', 'WN RF', 'Sch 80', '600', 'ENTRADA GAS'),
    ('SG', '10', 'B16.5', 'WN RF', 'Sch 80', '600', 'SALIDA GAS'),
    ('SV', '8', 'B16.5', 'WN RF', 'Sch 40', '150', 'SALIDA VENTEO'),
]

# Conexiones del recipiente (HD-001 p. 3, literal)
BOQUILLAS_HD = [
    ('A', 1, '10', 'Entrada de gas'), ('B1', 1, '10', 'Salida de gas'),
    ('B2', 1, '2', 'Salida de líquido superior'), ('B3', 1, '2', 'Salida de líquido inferior (proyección interna y rompevórtices)'),
    ('D', 1, '2', 'Drenaje'), ('J1/2', 2, '2', 'Transm. de presión diferencial'),
    ('L1/2', 2, '2', 'Transmisor de nivel'), ('L3/4', 2, '2', 'Transmisor de nivel'),
    ('L5/6', 2, '2', 'Indicador de nivel'), ('L7/8', 2, '2', 'Indicador de nivel'),
    ('L9/10', 2, '2', 'Transmisor de nivel'), ('L11/12', 2, '2', 'Transmisor de nivel'),
    ('MH', 1, '20', 'Boca de hombre (con junta, brida ciega y pescante)'),
    ('M1', 1, '32', 'Boca de inspección superior (con junta, brida ciega y pescante)'),
    ('P1', 1, '2', 'Indicador de presión'), ('P2', 1, '2', 'Transmisor de presión'),
    ('R1/2', 2, '4', 'Reserva c/ brida ciega'), ('S', 1, '2', 'Venteo'),
]

# ---------------------------------------------------------------------------
# 2. Recipiente FC (componentes principales) - criterio ITT sobre HD, como TAVAL/37 (FC-231)
# ---------------------------------------------------------------------------
# (descripción, medida, material, cant, unidad, peso_kg_total_aprox, origen)
RECIPIENTE_ = [
    ('Envolvente (cuerpo) rolado, Ø ext. 812,8 mm, LT/LT 4.064 mm', 'esp. 31,8 mm (1 1/4")', 'SA-516 Gr. 70', 1, 'u', 2490, 'HD (espesor orientativo, nota 2; lo fija la memoria)'),
    ('Casquete semielíptico 2:1 inferior, Ø ext. 812,8 mm', 'esp. 31,8 mm', 'SA-516 Gr. 70 / SA-234 WPB', 1, 'u', 230, 'HD; ITT: cierre superior = M1'),
    ('Brida WN 32" #600 (M1, boca de inspección superior / acceso a cartuchos)', 'ASME B16.47 Serie A', 'SA-105', 1, 'u', 624, 'HD; peso tabla B16.47'),
    ('Brida ciega 32" #600 (M1) con pescante', 'ASME B16.47 Serie A', 'SA-105', 1, 'u', 1295, 'HD nota 22; peso tabla B16.47'),
    ('Brida WN 20" #600 (MH) + cuello de chapa rolada', 'ASME B16.5', 'SA-105 / SA-516 Gr. 70', 1, 'u', 330, 'HD'),
    ('Brida ciega 20" #600 (MH) con pescante', 'ASME B16.5', 'SA-105', 1, 'u', 380, 'HD nota 22'),
    ('Brida WN 10" #600 + cuello 10" Sch 160 (A y B1)', 'ASME B16.5', 'SA-105 / SA-106 Gr. B', 2, 'u', 260, 'HD; Sch del cuello: ITT (TAVAL/37)'),
    ('Brida WN 4" #600 + cuello 4" Sch 160 (R1, R2)', 'ASME B16.5', 'SA-105 / SA-106 Gr. B', 2, 'u', 50, 'HD'),
    ('Brida ciega 4" #600 (R1, R2)', 'ASME B16.5', 'SA-105', 2, 'u', 40, 'HD'),
    ('Brida WN 2" #600 + cuello 2" Sch 160 (B2, B3, D, J1, J2, L1–L12, P1, P2, S)', 'ASME B16.5', 'SA-105 / SA-106 Gr. B', 20, 'u', 200, 'HD nota 19 (mín. Sch 160 < 3")'),
    ('Chapas de refuerzo de aberturas (MH 20", A y B1 10")', 'esp. 31,8 mm', 'SA-516 Gr. 70', 3, 'u', 150, 'ITT (a confirmar por cálculo UG-37)'),
    ('Pollera (faldón) con anillo base y aberturas de acceso', 'esp. 12,7 mm', 'SA-516 Gr. 70 / SA-36', 1, 'u', 450, 'HD "Pollera: Sí"'),
    ('Placa portacartuchos (tubesheet) con tensores de cartuchos', 'esp. 25,4 mm', 'SA-516 Gr. 70', 1, 'u', 110, 'HD nota 23; ITT'),
    ('Soportes internos de la caja de chicanas (vigas y ángulos)', '', 'SA-516 Gr. 70', 1, 'cj', 60, 'HD "Internos sold.: SA 516 Gr 70"'),
    ('Distribuidor de entrada (deflector) en A', '', 'SA-516 Gr. 70', 1, 'u', 40, 'HD "Distribuidor de entrada: Sí"'),
    ('Rompevórtice en B3 con proyección interna', '', 'SA-516 Gr. 70', 1, 'u', 15, 'HD nota 20'),
    ('Orejas de izaje (o trunnions)', '', 'SA-516 Gr. 70', 2, 'u', 60, 'HD nota 12'),
    ('Orejas de puesta a tierra', '', 'AISI 304L', 2, 'u', 2, 'HD nota 11 (dos)'),
    ('Clips para aislación y clips de instrumentos', '', 'SA-36', 1, 'cj', 40, 'HD "Clips aislación / instr.: Sí"'),
    ('Placa de identificación con soporte', 'C0100 Anexo I', 'AISI 316', 1, 'u', 3, 'RI §2 / C0100'),
]

RECIPIENTE = [r[:5] + (float(r[5]),) + r[6:] for r in RECIPIENTE_]

# ---------------------------------------------------------------------------
# 3. Válvulas (por filtro; FC-302 igual con sus tags)
# ---------------------------------------------------------------------------
# (tag, tipo, Ø, serie/extremos, clase, cant, función, origen/decisión)
VALVULAS = [
    ('VF-322', 'Esférica paso total (FB)', '10"', '#600 RF', 'CE32', 1, 'Bloqueo entrada de gas (LO)', 'P&ID; con reductor (plano pos. 501)'),
    ('VF-337', 'Esférica paso total (FB)', '10"', '#600 RF', 'CE32', 1, 'Bloqueo salida de gas (LO)', 'P&ID; con reductor'),
    ('VF-339', 'Esférica', '10"', '#600 RF', 'CE32', 1, 'By-pass del filtro (LC)', 'P&ID; ITT: paso total, con reductor. El plano lista solo 1 válvula de 10": van 3 por P&ID'),
    ('VF-323', 'Esférica', '2"', '#600 RF', 'CE32', 1, 'By-pass de VF-322 para presurizar (LC)', 'P&ID'),
    ('VG-324', 'Globo', '2"', '#600 RF', 'CE32', 1, 'Regulación de la presurización', 'P&ID'),
    ('VF-327/328/329/330/331/332/333/334/335/336/359/360', 'Esférica paso total (FB)', '2"', '#600 RF', 'CE32', 12, 'Bloqueo de instrumentos de nivel (L1 a L12)', 'P&ID'),
    ('VF-340 (LO) / VF-342 (LC)', 'Esférica paso total (FB)', '2"', '#600 RF', 'CE32', 2, 'Bloqueo de entrada a PSV-301A/B', 'P&ID'),
    ('VF-341 / VF-343', 'Esférica paso total (FB)', '6"', '#150 RF', 'CK11 (baja temp.)', 2, 'Bloqueo de salida de PSV-301A/B (LO)', 'P&ID'),
    ('VF-344', 'Esférica', '1"', '#600 RF', 'CE32', 1, 'Venteo manual (LC)', 'P&ID'),
    ('VG-345', 'Globo', '1"', '#600 RF', 'CE32', 1, 'Venteo manual (regulación)', 'P&ID'),
    ('VF-338', 'Esférica paso total (FB)', '6"', '#600 RF', 'CK31 (baja temp.)', 1, 'Bloqueo aguas abajo de BDV/RO (LO)', 'P&ID'),
    ('VF-346 / VF-347', 'Esférica', '2"', '#600 RF', 'CE32', 2, 'Bloqueo de LV-301D', 'P&ID'),
    ('VG-204', 'Globo', '2"', '#600 RF', 'CE32', 1, 'By-pass de LV-301D (P&ID nota 4: Cv ≤ Cv de la LV)', 'P&ID'),
    ('VF-350 / VF-351', 'Esférica', '2"', '#600 RF', 'CE32', 2, 'Bloqueo de LV-301B', 'P&ID'),
    ('VG-353', 'Globo', '2"', '#600 RF', 'CE32', 1, 'By-pass de LV-301B (nota 4)', 'P&ID'),
    ('VR-354', 'Retención', '2"', '#600 RF', 'CE32', 1, 'Salida de condensado', 'P&ID'),
    ('VF-355', 'Esférica', '2"', '#600 RF', 'CE32', 1, 'Bloqueo salida de condensado (límite)', 'P&ID'),
    ('VF-356', 'Esférica', '2"', '#600 RF', 'CE32', 1, 'Drenaje D (LC)', 'P&ID'),
    ('VR-399', 'Retención', '2"', '#600 RF', 'CE32', 1, 'Drenaje cerrado', 'P&ID'),
    ('VG-357', 'Globo', '2"', '#600 RF', 'CE32', 1, 'Drenaje cerrado (regulación)', 'P&ID'),
    ('VF-358', 'Esférica', '2"', '#150 RF', 'CA11', 1, 'Entrada de aire de instrumentos', 'P&ID'),
    ('VF-325 / VF-326', 'Esférica paso total (FB)', '1 1/2"', 'NPT', 'CE32', 2, 'Cupón CC-301 e inyección de químico (nota 3)', 'P&ID'),
    ('(sin tag)', 'Esférica 2000 WOG (TCH2N)', '1/2"', 'NPT', 'CE32 / CA11', 23, 'Venteos de LIT (8), LG (4), PSV (4), CC-301 (1), aire IA1–IA5 + extremo (6). Las 1/2" de PIT y PI son del manifold M2', 'P&ID; cantidad contada por ITT'),
    ('(sin tag)', 'Esférica 2000 WOG (TCH2N)', '3/4"', 'NPT', 'CE32 / CA11', 11, 'Drenajes de LV-301D (2) y LV-301B (2), entre VR-354 y VF-355 (1), PDIT (2), PIT (1), PI (1), colector de aire (1), OD1 (1)', 'P&ID; cantidad contada por ITT'),
]
VALVULAS_ACTUADAS = [
    ('LV-301D (+ LY-301D)', 'Control, globo, actuador neumático, posicionador 4–20 mA HART', '2"', '#600 RF', 'CE32', 1, 'Control de nivel sección superior (falla cierra, FC). RI §10: no debe pasar más de 3.750 kg/h de gas en blow-by', 'P&ID; Cv por ITT con el proveedor'),
    ('LV-301B (+ LY-301B)', 'Control, globo, actuador neumático, posicionador 4–20 mA HART', '2"', '#600 RF', 'CE32', 1, 'Control de nivel sección inferior (FC). Idem RI §10', 'P&ID'),
    ('SDV-301C', 'Esférica de corte, actuador neumático simple efecto, solenoide SV-301C, fines de carrera ZSO/ZSC-301C', '2"', '#600 RF', 'CE32', 1, 'Corte por SIS línea superior (FC)', 'P&ID'),
    ('SDV-301', 'Esférica de corte, actuador neumático simple efecto, solenoide SV-301, fines de carrera ZSO/ZSC-301', '2"', '#600 RF', 'CE32', 1, 'Corte por SIS línea inferior (FC)', 'P&ID'),
    ('BDV-301E', 'Esférica de blowdown, actuador neumático, solenoide SV-301E, fines de carrera ZSO/ZSC-301E', '4"', '#600 RF', 'CE32', 1, 'Despresurización (falla abre, FO); comando HS-003', 'P&ID; P&ID nota 10'),
    ('PSV-301A / PSV-301B', 'Seguridad, API 526, orificio D', '1" × 2"', '#600 RF × #150 RF', 'CE32 / CK11', 2, 'Set 99 kg/cm2g, caso fuego (alcance del proveedor, RI §10)', 'P&ID'),
    ('RO-301', 'Placa orificio de restricción con bridas portaplaca B16.36', '4"', '#600 RF', 'CK31 (baja temp.)', 1, 'Restricción del blowdown (dimensionamiento de AESA, RI §10)', 'P&ID'),
]

# ---------------------------------------------------------------------------
# 4. Instrumentos (por filtro)
# ---------------------------------------------------------------------------
INSTRUMENTOS = [
    ('LIT-301A', 'Transmisor de nivel por presión diferencial con sellos remotos (J0402)', '2" #600 RF ×2', 'SIS (LALL-301A, I-27)', 'Sección inferior; traceado (nota 2); capilares cortos (nota 5); con bridas pancake AC + JD (P&ID nota 9)'),
    ('LIT-301B', 'Transmisor de nivel DP con sellos remotos', '2" #600 RF ×2', 'SCP (LIC-301B → LV-301B)', 'Sección inferior; con bridas pancake + JD (nota 9)'),
    ('LIT-301C', 'Transmisor de nivel DP con sellos remotos', '2" #600 RF ×2', 'SIS (LALL-301C, I-26)', 'Sección superior; con bridas pancake + JD (nota 9)'),
    ('LIT-301D', 'Transmisor de nivel DP con sellos remotos', '2" #600 RF ×2', 'SCP (LIC-301D → LV-301D)', 'Sección superior; con bridas pancake + JD (nota 9)'),
    ('LG-301A', 'Indicador de nivel de vidrio (J0401), tipo reflex, con válvulas de bloqueo con bola de retención', '2" #600 RF ×2', 'Local', 'Sección inferior. ITT: reflex (HD-J0401-01)'),
    ('LG-301B', 'Indicador de nivel de vidrio tipo reflex', '2" #600 RF ×2', 'Local', 'Sección superior'),
    ('PDIT-301', 'Transmisor de presión diferencial (J0304) con manifold de 5 vías (M5)', '1/2" NPT', 'SCP (PDI/PDAH-301)', 'Ensuciamiento de cartuchos; tomas J1/J2'),
    ('PIT-301B', 'Transmisor de presión (J0304) con manifold de 2 vías (M2)', '1/2" NPT', 'SIS (PAHH-301B, I-25)', 'Toma P2'),
    ('PI-301A', 'Manómetro Ø 100 mm con glicerina, 0–160 kg/cm2 (J0301), con manifold M2', '1/2" NPT', 'Local', 'Toma P1. Rango: ITT'),
    ('CC-301', 'Portacupón de corrosión con cupón (típico 1 del P&ID)', '1 1/2" NPT', 'Local', 'Con VF-325'),
]
SENALES = [  # tag, tipo de señal, sistema
    ('LIT-301A', 'Analógica 4–20 mA', 'SIS'), ('LIT-301C', 'Analógica 4–20 mA', 'SIS'), ('PIT-301B', 'Analógica 4–20 mA', 'SIS'),
    ('LIT-301B', 'Analógica 4–20 mA', 'SCP'), ('LIT-301D', 'Analógica 4–20 mA', 'SCP'), ('PDIT-301', 'Analógica 4–20 mA', 'SCP'),
    ('LY-301B', 'Analógica 4–20 mA (salida)', 'SCP'), ('LY-301D', 'Analógica 4–20 mA (salida)', 'SCP'),
    ('SV-301 / SV-301C / SV-301E', 'Digital (salida, 24 Vcc)', 'SIS'),
    ('ZSO/ZSC-301, ZSO/ZSC-301C, ZSO/ZSC-301E', 'Digital (entrada) ×6', 'SIS / SCADA'),
]
FUERA_DE_ALCANCE_INSTR = 'HS-003, HS-301, HS-301C, ESD1/ESD2, enclavamientos I-25/26/27/209/213/214 y las funciones LI/LAL/LAH/PDI/PAH (son de sala de control); AT-006 (detector de gas, fuera del límite del skid).'

# ---------------------------------------------------------------------------
# 5. Piping: caños y accesorios (por filtro). Largos y piezas: estimación ITT con el P&ID y los pesos del plano
# ---------------------------------------------------------------------------
CANOS = [  # descripción, Ø, sch, material, clase, metros, líneas
    ('Caño sin costura BE', '10"', 'Sch 80', 'ASTM A106 Gr. B', 'CE32', 16, 'Entrada 10"-GH-1105/0176, salida 10"-GH-0269 y by-pass 10"-GH-0297 (ajustado a los pesos del plano: pos. 2001 + 2002 = 3.979 kg)'),
    ('Caño sin costura BE', '4"', 'Sch 80', 'ASTM A106 Gr. B', 'CE32', 5, 'BDV 4"-GH-0750'),
    ('Caño sin costura BE', '4"', 'Sch 80', 'ASTM A333 Gr. 6', 'CK31', 1, '4"-V-0752 aguas abajo de RO-301'),
    ('Caño sin costura BE', '6"', 'Sch 80', 'ASTM A333 Gr. 6', 'CK31', 2, 'Tramo de VF-338'),
    ('Caño sin costura BE', '8"', 'Sch 40', 'ASTM A333 Gr. 6', 'CK11', 6, 'Colector de venteo 8"-V-0268 (plano: Sch 40; la clase pide Sch 20: ITT toma Sch 40)'),
    ('Caño sin costura BE', '6"', 'Sch 40', 'ASTM A333 Gr. 6', 'CK11', 6, 'Salidas de PSV 6"-V-0265/0266'),
    ('Caño sin costura BE', '3"', 'Sch 40', 'ASTM A333 Gr. 6', 'CK11', 1, 'Salidas de PSV (tramos 3")'),
    ('Caño sin costura BE', '2"', 'Sch 160', 'ASTM A106 Gr. B', 'CE32', 33, 'PSV 2"-V-0262/0263, condensado LH-0271/0272/0273, drenaje PD-0275, puentes de nivel, by-pass de entrada'),
    ('Caño sin costura PE', '1"', 'Sch 160', 'ASTM A106 Gr. B', 'CE32', 2, 'Entradas de PSV y venteo manual'),
    ('Caño sin costura PE', '1"', 'Sch 80', 'ASTM A333 Gr. 6', 'CK11', 3, 'Venteo 1"-V-0267'),
    ('Caño sin costura BE', '2"', 'Sch 40', 'ASTM A106 Gr. B', 'CA11', 17, 'Drenaje abierto OD-0276, aire IA-0601, drenaje cerrado PD-0274'),
    ('Niples sin costura NPT', '1/2" y 3/4"', 'Sch 160', 'ASTM A106 Gr. B', 'CE32', 40, 'Venteos, drenajes e instrumentos (unidades)'),
]
ACCESORIOS = [  # descripción, Ø, sch/serie, material, clase, cant
    ('Codo 90° RL BW', '10"', 'Sch 80', 'ASTM A234 WPB', 'CE32', 8),
    ('Te normal BW', '10"', 'Sch 80', 'ASTM A234 WPB', 'CE32', 2),
    ('Te de reducción BW (derivación de la BDV; tabla de derivaciones CE32: código 3)', '10" × 4"', 'Sch 80', 'ASTM A234 WPB', 'CE32', 1),
    ('Codo 90° RL BW', '4"', 'Sch 80', 'ASTM A234 WPB', 'CE32', 3),
    ('Reducción concéntrica BW', '6" × 4"', 'Sch 80', 'ASTM A420 WPL6', 'CK31', 1),
    ('Codo 90° RL BW', '8"', 'Sch 40', 'ASTM A420 WPL6', 'CK11', 2),
    ('Te normal BW', '8"', 'Sch 40', 'ASTM A420 WPL6', 'CK11', 2),
    ('Codo 90° RL BW', '6"', 'Sch 40', 'ASTM A420 WPL6', 'CK11', 4),
    ('Reducción concéntrica BW', '6" × 3"', 'Sch 40', 'ASTM A420 WPL6', 'CK11', 2),
    ('Reducción concéntrica BW', '3" × 2"', 'Sch 40', 'ASTM A420 WPL6', 'CK11', 2),
    ('Codo 90° RL BW', '2"', 'Sch 160', 'ASTM A234 WPB', 'CE32', 30),
    ('Te normal BW', '2"', 'Sch 160', 'ASTM A234 WPB', 'CE32', 6),
    ('Reducción concéntrica BW', '2" × 1"', 'Sch 160', 'ASTM A234 WPB', 'CE32', 2),
    ('Casquete BW', '2"', 'Sch 160', 'ASTM A234 WPB', 'CE32', 2),
    ('Codo 90° SW', '1"', '6000#', 'ASTM A105', 'CE32', 4),
    ('Codo 90° SW', '1"', '3000#', 'ASTM A350 LF2', 'CK11', 2),
    ('Codo 90° RL BW', '2"', 'Sch 40', 'ASTM A234 WPB', 'CA11', 10),
    ('Te normal BW', '2"', 'Sch 40', 'ASTM A234 WPB', 'CA11', 6),
    ('Casquete BW', '2"', 'Sch 40', 'ASTM A234 WPB', 'CA11', 2),
    ('Thredolet 6000# (CE32: serie de olets de la clase; a verificar)', '1/2"', 'NPT', 'ASTM A105', 'CE32', 14),
    ('Thredolet 3000#', '1/2"', 'NPT', 'ASTM A105', 'CA11', 6),
    ('Thredolet 6000# (CE32; a verificar)', '3/4"', 'NPT', 'ASTM A105', 'CE32', 8),
    ('Thredolet 3000#', '3/4"', 'NPT', 'ASTM A105', 'CA11', 2),
    ('Tapón hexagonal 3000#', '1/2" y 3/4"', 'NPT', 'ASTM A105', 'CE32 / CA11', 38),
]
BRIDAS = [  # descripción, Ø, serie, sch, material, clase, cant
    ('Brida WN RF (válvulas de 10" y límites EG y SG)', '10"', '#600', 'Sch 80', 'ASTM A105', 'CE32', 8),
    ('Brida WN RF (entrada de BDV-301E)', '4"', '#600', 'Sch 80', 'ASTM A105', 'CE32', 1),
    ('Brida WN RF (salida de BDV-301E)', '4"', '#600', 'Sch 80', 'ASTM A350 LF2', 'CK31', 1),
    ('Brida portaplaca WN RF (par, para RO-301)', '4"', '#600', 'Sch 80', 'ASTM A350 LF2', 'CK31 (B16.36)', 1),
    ('Brida WN RF', '6"', '#600', 'Sch 80', 'ASTM A350 LF2', 'CK31', 2),
    ('Brida WN RF', '6"', '#150', 'Sch 40', 'ASTM A350 LF2', 'CK11', 4),
    ('Brida WN RF (límite SV)', '8"', '#150', 'Sch 40', 'ASTM A350 LF2', 'CK11', 1),
    ('Brida WN RF (salidas de PSV)', '2"', '#150', 'Sch 40', 'ASTM A350 LF2', 'CK11', 2),
    ('Brida WN RF (incluye el límite SL)', '2"', '#600', 'Sch 160', 'ASTM A105', 'CE32', 40),
    ('Brida WN RF (límite DC)', '2"', '#150', 'Sch 160', 'ASTM A105', 'CA11', 1),
    ('Brida WN RF (VF-358 y límites AI y DA)', '2"', '#150', 'Sch 40', 'ASTM A105', 'CA11', 4),
    ('Brida SW RF', '1"', '#600', 'Sch 160', 'ASTM A105', 'CE32', 5),
    ('Brida ciega RF perforada y roscada 3/4" NPT (P1, P2, J1, J2)', '2"', '#600', '', 'ASTM A105', 'CE32', 4),
]

# ---------------------------------------------------------------------------
# 6. Juntas y bulonería (por filtro). Uniones contadas en el P&ID; espárragos de esparragos_por_brida.csv
# ---------------------------------------------------------------------------
# (Ø, serie, uniones, tipo de junta, material espárrago, espárragos por unión, medida, donde)
JUNTAS = [
    ('32"', '#600', 1, 'Espiralada AISI 316/grafito 4,5 mm, anillo ext. AC zincado + int. AISI 316 (B16.20, para B16.47 A)', 'A193 B7 / A194 2H zincado', 28, '2" × 15 1/2" (a verificar)', 'M1'),
    ('20"', '#600', 1, 'Espiralada 316/grafito, anillo ext. + int.', 'A193 B7 / A194 2H zincado', 24, '1 5/8" × 11 1/2"', 'MH'),
    ('10"', '#600', 8, 'Espiralada 316/grafito, anillo ext. + int.', 'A193 B7 / A194 2H zincado', 16, '1 1/4" × 8 1/2"', 'A, B1, VF-322, VF-337, VF-339'),
    ('6"', '#600', 2, 'Espiralada 316/grafito, anillo ext. AC zincado', 'A320 L7 / A194 Gr. 4 (CK31)', 12, '1" × 6 3/4"', 'VF-338'),
    ('6"', '#150', 4, 'Espiralada 316/grafito, anillo ext. AC zincado', 'A320 L7 / A194 Gr. 4 (CK11)', 8, '3/4" × 4"', 'VF-341, VF-343'),
    ('4"', '#600', 3, 'Espiralada 316/grafito, anillo ext. AC zincado', 'A193 B7 / A194 2H zincado', 8, '7/8" × 5 3/4"', 'R1, R2, entrada de BDV-301E'),
    ('4"', '#600', 3, 'Espiralada 316/grafito, anillo ext. AC zincado', 'A320 L7 / A194 Gr. 4 (CK31)', 8, '7/8" × 5 3/4" (RO: más largo, a verificar con el espesor de la placa)', 'Salida de BDV-301E, RO-301 (2 juntas)'),
    ('2"', '#600', 62, 'Espiralada 316/grafito, anillo ext. AC zincado', 'A193 B7 / A194 2H zincado', 8, '5/8" × 4 1/4"', 'Boquillas, válvulas de línea, LG, LV/SDV, drenaje, PSV'),
    ('2"', '#600', 8, 'Junta dieléctrica + brida pancake AC: las provee el instrumentista con el LIT (P&ID nota 9)', 'A193 B7 / A194 2H zincado', 8, '5/8" × 4 1/4" (a verificar con el kit JD)', 'LIT-301A/B/C/D en L1–L4 y L9–L12 (burbujas JD del P&ID)'),
    ('2"', '#150', 4, 'Espiralada 316/grafito, anillo ext. AC zincado', 'B7 (CA11) / L7 (CK11)', 4, '5/8" × 3 1/4"', 'Salidas de PSV, VF-358'),
    ('1"', '#600', 5, 'Espiralada 316/grafito, anillo ext. AC zincado', 'A193 B7 / A194 2H zincado', 4, '5/8" × 3 3/4"', 'Entradas de PSV, venteo manual'),
]

# ---------------------------------------------------------------------------
# 7. Elementos filtrantes (por filtro)
# ---------------------------------------------------------------------------
FILTRANTES = [
    ('Cartucho coalescente Ø ext. 141 × 915 mm, núcleo y tapas de acero inoxidable, medio de fibra de vidrio (SS + FG), flujo interior → exterior, 99,99 % > 0,3 µm, arrastre máx. 1 ppm, ΔP limpio 0,15 bar / colapso 3 bar', 9, 'u', 'Equipo', 'HD línea 31-36 y nota 23 (cantidad y medida "a confirmar por fabricante")'),
    ('Caja de chicanas (separación primaria) rectangular doble bolsillo, flujo horizontal, 800 × 650 × 200 mm, chapa 0,8 mm, AISI 316L, 99 % > 20 µm', 1, 'u', 'Equipo', 'HD nota 23. ITT: en 2 módulos para sacarla por M1 (no pasa entera por MH 20" ni por M1)'),
    ('Juntas / O-rings de asiento de cartuchos', 9, 'u', 'Equipo', 'ITT (las da el fabricante del cartucho)'),
    ('Cartuchos para precomisionado, comisionado y puesta en marcha (1 juego)', 9, 'u', 'RCP', 'RI §8: mínimo 1 juego para PEM'),
    ('Cartuchos para 2 años de operación (2 juegos)', 18, 'u', 'RDO', 'RI §8: 2 juegos para 2 años'),
    ('Juntas de asiento de cartuchos de repuesto', 27, 'u', 'RCP / RDO', 'ITT (una por cartucho de repuesto)'),
]

# ---------------------------------------------------------------------------
# 8. Otros artículos (por filtro)
# ---------------------------------------------------------------------------
OTROS = [
    ('Chasis base (patín) autoportante, sin grout, con cáncamos de izaje verificados ASME BTH-1 (coef. ≥ 4) y ojales de amarre', '1 cj', 'Plano pos. 1000 (5.642 kg); RI §2 y §12'),
    ('Plataformas (2 niveles, +2.480 y +4.720 mm), escalera marinera y barandas, con rejilla', '1 cj', 'Plano pos. 1500 (2.690 kg); HD "Escaleras / plataformas: Sí"'),
    ('Escalón de acceso a MH', '1 u', 'Plano pos. 1900 (48 kg)'),
    ('Batea de contención de drenajes y salpicaduras con descarga a drenaje abierto', '1 u', 'RI §2; P&ID "batea skid". ITT: chapa 4,76 mm A36'),
    ('Soportes de cañería (típicos 5165-02-0000-IG-PI-TM-001)', '1 cj', 'RI §9'),
    ('Embudos de drenaje abierto OD1, OD2, OD3', '3 u', 'P&ID'),
    ('Tubing inox 1/2" con conectores para aire de instrumentos (IA1–IA5 a actuadores)', '30 m', 'P&ID; ITT'),
    ('Tubing inox 1/2" con conectores para impulsos de PDIT/PIT/PI', '15 m', 'ITT'),
    ('Aislación del recipiente completo: lana mineral 70 kg/m3, 60 mm, chapa de aluminio ASTM B209 3003/3105 H14/H24 de 1 mm', '≈ 12 m2', 'HD nota 10'),
    ('Aislación de líneas e instrumentos traceados (B2, B3, D, puentes de nivel)', '≈ 25 m', 'HD notas 10 y 21; P&ID "E30"'),
    ('Pintura B0600: sistema 202 (superficies aisladas) y 201 (resto); RAL 9006 recipiente, 9011 estructura, 1016 escaleras', '1 gl', 'HD nota 9'),
    ('Chapas de identificación de TAG de válvulas e instrumentos, AISI 316', '≈ 60 u', 'RI §2; ITT'),
    ('Protectores de bridas y embalaje para transporte (ED(EP)-B-01.00); repuestos en bultos separados e identificados', '1 gl', 'RI §11'),
    ('Repuestos incluidos (RI §8): espárragos 15 % PEM y 10 % 2 años (mín. 5 por medida); juntas 3 + 2 por medida; kit de PSV (1 por válvula); kit de LV (1 por válvula); 1 instrumento de cada tipo para PEM y 1 para 2 años', '1 lote RCP + 1 lote RDO', 'RI §8'),
    ('Pernos de anclaje: solo diseño (el skid apoya sin grout)', '—', 'RI §2'),
    ('Opcionales (RI §2): modelo 3D CADWorx con atributos BIM; asistencia técnica en sitio por día; viaje al sitio; herramientas especiales', '—', 'Se cotizan aparte'),
]

# ---------------------------------------------------------------------------
# 9. Trabajo eléctrico (por skid)
# ---------------------------------------------------------------------------
ELECTRICO = [
    ('Área clasificada', 'Clase I, Zona 2, Grupo IIA, T3 (HD nota 18): todo el material eléctrico certificado Ex para zona 2 y mínimo IP-65 (RI §2).'),
    ('Cajas de conexionado', '4 JB de instrumentos segregadas por sistema y tipo de señal (analógicas SIS, analógicas SCP, digitales SIS, digitales SCP; RI §2) + 1 JB de potencia del traceado (plano pos. 601). El plano dibuja 3 JB de instrumentos (pos. 605): ITT toma 4 porque la RI manda sobre el plano (orden de prelación). Con borneras, riel DIN y 20 % de reserva.'),
    ('Cableado de instrumentos', 'De cada instrumento, solenoide y fin de carrera a su JB, con cables según J1301 / P1000 y reservas. Señales: 8 analógicas (LIT ×4, PDIT, PIT, LY ×2) y 9 digitales (SV ×3, ZSO/ZSC ×6). El cable de JB a sala de control es de AESA.'),
    ('Canalizaciones', 'Caño conduit galvanizado y accesorios Ex (P1100), bandeja portacables sobre el skid (P1102), prensacables Ex (P1103), soportes de conduit. El plano estima 77 kg de canalizaciones (pos. 2000).'),
    ('Traceado eléctrico (P0103)', 'Cable calefactor autorregulado en el recipiente hasta HHLL (zona inferior, "E60" en el P&ID), líneas de condensado B2/B3, drenaje D y conexiones e instrumentos de nivel ("E30"). ITT: 4 circuitos con termostato, alimentados desde la JB de potencia. Incluye memoria de cálculo, listado de materiales, plano de canalización y diagrama de conexionado (RI §13, 3.1 a 3.4).'),
    ('Puesta a tierra (P1105)', '2 orejas de PAT en el recipiente (AISI 304L) y 3 puntos de PAT en el chasis (plano), con equipotencialización de JB, instrumentos y estructura.'),
    ('Aire de instrumentos', 'Colector 2"-IA-0601 con 5 tomas (IA1–IA5) a los actuadores de LV-301B/D, SDV-301/301C y BDV-301E (tubing inox 1/2").'),
    ('Documentos', 'Listado de cables, plano de PAT, plano de JB, diagramas de conexionado y listado de instrumentos y señales (RI §13, 3.5 a 4.7).'),
    ('Pruebas', 'FAT con prueba de lazos de instrumentos, válvulas actuadas y traceado (RI §2; RC §1).'),
]

FALTA_O_DECIDIDO = [
    'Cantidad y medida de cartuchos (9 × Ø 141 × 915 mm) y caja de chicanas: se toman de la HD; las confirma el fabricante de elementos (pedir cotización a Pall, Gora u otro).',
    'Altura del recipiente: HD 4.064 mm LT/LT, P&ID 4.184 mm T-T y plano 4.663 mm LT-LRF (hasta la cara de la brida M1). Se toma la HD; las tres cotas son compatibles si se miden a puntos distintos.',
    'Válvulas de 10": el plano lista 1 (pos. 501) y el P&ID tiene 3 (VF-322, VF-337, VF-339). Se toman 3.',
    'JB de instrumentos: el plano dibuja 3 y la RI pide segregarlas en 4. Se toman 4 (la RI manda).',
    'Colector de venteo de 8": el plano dice Sch 40 y la clase CK11 da Sch 20. Se toma Sch 40.',
    'Aguas abajo de PSV y de BDV/RO (CK11 y CK31) el material es de baja temperatura (A333 Gr. 6, A350 LF2, A420 WPL6, espárragos A320 L7).',
    'Largos de cañería y cantidad de accesorios: estimados por ITT con el P&ID, las cotas del plano y los pesos de su tabla (no hay isométricos).',
    'Juntas dieléctricas: 8, en las conexiones de los LIT (burbujas JD del P&ID); según la nota 9 del P&ID las bridas pancake y las JD vienen con el instrumento. Las uniones con el exterior (límites del skid) llevan solo nuestra brida; junta y espárragos los pone AESA.',
    'Thredolets en CE32: serie 6000# por la tabla de series de olets de la clase (a verificar si la columna es el ramal o el cabezal); en CA11 y CK11, 3000#.',
    'Caño de 10": 16 m, ajustado para que el piping de 10" dé un peso parecido al de las líneas 2001 y 2002 del plano.',
    'Detector de gas AT-006 y las funciones de sala de control: fuera del alcance (fuera del límite del skid).',
    'Especificaciones que no vinieron (C-02.00, J1800, J0301, J0402, J1302, J1304, J1400, P1100, P1102, P1103, P1105): se cotiza según buena práctica y se aclara en la oferta.',
]


# ---------------------------------------------------------------------------
# 11. PESOS Y SOLDADURAS (pedido de Matías, 25-11-2026)
# Pesos: tablas de conocimiento/tecnico (B36.10, B16.5, B16.9, B16.11, B16.47, B16.36, MSS SP-97, Taval Lista 30, espárragos).
# Soldadura: mismas reglas que herramientas/precotizar.py: pulg-eq = Ø × factor de espesor (factores_soldadura.csv);
# olets × 1,75 (weldolet × 2,5) por el Ø de salida (factores_accesorios.csv); caño por metro: cada extremo BW de
# accesorio o brida es una junta con caño × 0,75 (AJUSTE_DIRECTAS) + empalmes entre barras de 6 m.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(AQUI, '..', '..', 'herramientas'))
from pesos_soldadura import (factor_esp, kg_cano, kg_brida, kg_acc, kg_olet, kg_valvula, kg_esparrago,  # noqa: E402
                             medida_esparrago)
import pesos_soldadura  # noqa: E402
import math  # noqa: E402


ESF_FB = ['ESFERICA PT GUIADA', 'ESFERICA PT FLOTANTE']
ESF_NPT = ['ESFERICA PT FLOTANTE FORJADA NPT (API 608)']

# Metadatos para peso y soldadura, en el mismo orden que CANOS, ACCESORIOS, BRIDAS, VALVULAS y VALVULAS_ACTUADAS
CANOS_META = [(10, '80'), (4, '80'), (4, '80'), (6, '80'), (8, '40'), (6, '40'), (3, '40'), (2, '160'), (1, '160'), (1, '80'), (2, '40'), None]
# (tipo tabla, Ø, Ø2, clase tabla, extremos, sch real, extremos BW, extremos SW, factor olet)
ACC_META = [
    ('codo_90_radio_largo', 10, None, 'XS', 'BW', '80', 2, 0, 0),
    ('tee_recta', 10, None, 'XS', 'BW', '80', 3, 0, 0),
    ('tee_reduccion', 10, 4, 'XS', 'BW', '80', 3, 0, 0),
    ('codo_90_radio_largo', 4, None, 'XS', 'BW', '80', 2, 0, 0),
    ('reduccion_concentrica_excentrica', 6, 4, 'XS', 'BW', '80', 2, 0, 0),
    ('codo_90_radio_largo', 8, None, 'STD', 'BW', '40', 2, 0, 0),
    ('tee_recta', 8, None, 'STD', 'BW', '40', 3, 0, 0),
    ('codo_90_radio_largo', 6, None, 'STD', 'BW', '40', 2, 0, 0),
    ('reduccion_concentrica_excentrica', 6, 3, 'STD', 'BW', '40', 2, 0, 0),
    ('reduccion_concentrica_excentrica', 3, 2, 'STD', 'BW', '40', 2, 0, 0),
    ('codo_90_radio_largo', 2, None, '160', 'BW', '160', 2, 0, 0),
    ('tee_recta', 2, None, '160', 'BW', '160', 3, 0, 0),
    ('reduccion_concentrica_excentrica', 2, 1, '160', 'BW', '160', 2, 0, 0),
    ('casquete', 2, None, '160', 'BW', '160', 1, 0, 0),
    ('codo_90', 1, None, '6000', 'SW', '160', 0, 2, 0),
    ('codo_90', 1, None, '3000', 'SW', '80', 0, 2, 0),
    ('codo_90_radio_largo', 2, None, 'STD', 'BW', '40', 2, 0, 0),
    ('tee_recta', 2, None, 'STD', 'BW', '40', 3, 0, 0),
    ('casquete', 2, None, 'STD', 'BW', '40', 1, 0, 0),
    ('thredolet', 0.5, None, '6000', 'NPT', None, 0, 0, 1.75),
    ('thredolet', 0.5, None, '3000', 'NPT', None, 0, 0, 1.75),
    ('thredolet', 0.75, None, '6000', 'NPT', None, 0, 0, 1.75),
    ('thredolet', 0.75, None, '3000', 'NPT', None, 0, 0, 1.75),
    ('tapon_hexagonal', 0.75, None, '3000/6000', 'NPT', None, 0, 0, 0),
]
# (tipo tabla, Ø, serie, sch del cuello, extremos BW, extremos SW)
BRI_META = [('WN', 10, '600', '80', 1, 0), ('WN', 4, '600', '80', 1, 0), ('WN', 4, '600', '80', 1, 0), ('orificio', 4, '600', '80', 2, 0), ('WN', 6, '600', '80', 1, 0),
            ('WN', 6, '150', '40', 1, 0), ('WN', 8, '150', '40', 1, 0), ('WN', 2, '150', '40', 1, 0), ('WN', 2, '600', '160', 1, 0),
            ('WN', 2, '150', '160', 1, 0), ('WN', 2, '150', '40', 1, 0), ('SW', 1, '600', '160', 0, 1), ('ciega', 2, '600', None, 0, 0)]
# válvulas: (tipos de tabla, Ø, serie, extremos) o kg aproximado por unidad (actuadas, PSV, RO: sin tabla, criterio ITT)
VAL_META = [732.0, 732.0, 732.0, (ESF_FB, 2, '600', 'RF'), (['GLOBO'], 2, '600', 'RF'),
            (ESF_FB, 2, '600', 'RF'), (ESF_FB, 2, '600', 'RF'), (ESF_FB, 6, '150', 'RF'), (ESF_FB, 1, '600', 'RF'), (['GLOBO'], 1, '600', 'RF'),
            (ESF_FB, 6, '600', 'RF'), (ESF_FB, 2, '600', 'RF'), (['GLOBO'], 2, '600', 'RF'), (ESF_FB, 2, '600', 'RF'), (['GLOBO'], 2, '600', 'RF'),
            (['RETENCION A CLAPETA'], 2, '600', 'RF'), (ESF_FB, 2, '600', 'RF'), (ESF_FB, 2, '600', 'RF'), (['RETENCION A CLAPETA'], 2, '600', 'RF'),
            (['GLOBO'], 2, '600', 'RF'), (ESF_FB, 2, '150', 'RF'), (ESF_NPT, 1.5, '2000', 'NPT'), (ESF_NPT, 0.5, '2000', 'NPT'), (ESF_NPT, 0.75, '2000', 'NPT')]
VAL_ACT_KG = [70.0, 70.0, 60.0, 60.0, 180.0, 35.0, 3.0]  # LV, LV, SDV, SDV, BDV, PSV, placa RO: aproximado ITT con actuador
VAL_ACT_NOTA = 'aprox. ITT (con actuador; sin tabla)'
# Respaldo ITT para válvulas sin fila en la tabla (por unidad, kg)
VAL_RESPALDO = {(6, '600'): 250.0, (6, '150'): 75.0, (1, '600'): 12.0}


def pesos():
    """Lista de (rubro, descripción, cant., kg unidad, kg total por filtro, fuente)."""
    out = []
    for c, m in zip(CANOS, CANOS_META):
        if not m:
            out.append(('Caños', c[0] + ' ' + c[1], c[5], 0.5, c[5] * 0.5, 'aprox. ITT (niple 1/2"-3/4" ≈ 0,5 kg)'))
            continue
        kg, f = kg_cano(*m)
        out.append(('Caños', f'{c[0]} {c[1]} {c[2]} {c[3]}', c[5], kg, (kg or 0) * c[5], f + ' (kg/m)'))
    for a, m in zip(ACCESORIOS, ACC_META):
        tipo, dn, dn2, cl, ext, schr, *_ = m
        if tipo in ('weldolet', 'thredolet'):
            kg, f = kg_olet(tipo, dn, cl)
        else:
            kg, f = kg_acc(tipo, dn, cl, ext, dn2, schr)
        out.append(('Accesorios', f'{a[0]} {a[1]} {a[2]}', a[5], kg, (kg or 0) * a[5], f))
    for b, m in zip(BRIDAS, BRI_META):
        kg, f = kg_brida(m[0], m[1], m[2])
        out.append(('Bridas', f'{b[0]} {b[1]} {b[2]}', b[6], kg, (kg or 0) * b[6], f))
    for v, m in zip(VALVULAS, VAL_META):
        if isinstance(m, float):  # peso dado por el documento del cliente
            out.append(('Válvulas', f'{v[0]} {v[1]} {v[2]} {v[3]}', v[5], m, m * v[5], 'plano pos. 501 (con reductor)'))
            continue
        kg, f = kg_valvula(*m)
        if kg is None and (m[1], m[2]) in VAL_RESPALDO:
            kg, f = VAL_RESPALDO[(m[1], m[2])], 'aprox. ITT (sin tabla)'
        out.append(('Válvulas', f'{v[0]} {v[1]} {v[2]} {v[3]}', v[5], kg, (kg or 0) * v[5], f))
    for v, kg in zip(VALVULAS_ACTUADAS, VAL_ACT_KG):
        out.append(('Válvulas', f'{v[0]} {v[2]} {v[3]}', v[5], kg, kg * v[5], VAL_ACT_NOTA))
    for j in JUNTAS:
        d, largo = medida_esparrago(j[6])
        kg, f = kg_esparrago(d, largo) if d else (None, 'sin medida')
        n = j[2] * j[5]
        out.append(('Bulonería', f'Espárragos {j[6]} ({j[0]} {j[1]})', n, kg, (kg or 0) * n, f))
    for r in RECIPIENTE:
        out.append(('Recipiente', r[0], r[3], r[5] / r[3], r[5], 'aprox. ITT / tablas'))
    for pos, cant, desc, kg, _ in LDM_PLANO:
        if pos in ('1000', '1500', '1900'):
            out.append(('Estructura (plano)', desc, cant, kg, kg * cant, f'plano PL-001 pos. {pos}'))
    return out


def soldaduras_piping():
    return pesos_soldadura.soldaduras_piping(CANOS, CANOS_META, ACCESORIOS, ACC_META, BRIDAS, BRI_META)


def soldaduras_recipiente():
    """Soldaduras del recipiente (criterio ITT, convención de precotizar; revisado por auditoría independiente 25-11-2026):
    costura longitudinal = largo / (π·25,4) pulgadas × factor; circunferencial = Ø × factor; boquilla al cuerpo =
    Ø × 1,5 (derivación) × factor del espesor del CUERPO (la soldadura de penetración completa atraviesa el cuerpo);
    refuerzo = Ø × 1,5 × factor del espesor de la chapa de refuerzo; cuello–brida = Ø × factor del cuello."""
    e = 31.8
    f32 = factor_esp(32, esp=e)
    f_cuerpo = f32
    long_mm = 4064
    filas = [
        ('Costuras longitudinales del cuerpo (2 virolas, 2.500 + 1.564 mm = 4.064 mm de costura)', 1, long_mm / (math.pi * 25.4), f32),
        ('Circunferencial virola–virola', 1, 32, f32),
        ('Circunferencial cuerpo–casquete inferior', 1, 32, f32),
        ('Circunferencial cuerpo–brida M1 32"', 1, 32, f32),
        ('Placa portacartuchos al cuerpo (circunferencial, esp. 25,4 mm)', 1, 32, factor_esp(32, esp=25.4)),
        ('Pollera–casquete (esp. 12,7 mm)', 1, 32, factor_esp(32, esp=12.7)),
        ('Costura longitudinal de la pollera (≈ 1.000 mm, esp. 12,7 mm)', 1, 1000 / (math.pi * 25.4), factor_esp(32, esp=12.7)),
        ('Pollera–anillo base (filete)', 1, 32, 1.0),
        ('Costura longitudinal del cuello rolado MH 20" (≈ 300 mm, esp. 31,8 mm)', 1, 300 / (math.pi * 25.4), factor_esp(20, esp=e)),
        ('Cuello–brida MH 20" (esp. 31,8 mm)', 1, 20, factor_esp(20, esp=e)),
        ('Cuello MH 20" al cuerpo (derivación × 1,5; espesor del cuerpo)', 1, 20 * 1.5, f_cuerpo),
        ('Cuello–brida A y B1 10" Sch 160', 2, 10, factor_esp(10, '160')),
        ('Cuellos A y B1 10" al cuerpo (× 1,5; espesor del cuerpo)', 2, 15, f_cuerpo),
        ('Refuerzos de MH, A y B1 (× 1,5 del Ø mayor; chapa 31,8 mm)', 3, (20 + 10 + 10) / 3 * 1.5, f_cuerpo),
        ('Cuello–brida R1, R2 4" Sch 160', 2, 4, factor_esp(4, '160')),
        ('Cuellos R1, R2 4" al cuerpo (× 1,5; espesor del cuerpo)', 2, 6, f_cuerpo),
        ('Cuello–brida 2" Sch 160 (20 boquillas)', 20, 2, factor_esp(2, '160')),
        ('Cuellos 2" al cuerpo (× 1,5; espesor del cuerpo)', 20, 3, f_cuerpo),
    ]
    out = []
    for d, n, pulg, f in filas:
        out.append(('Recipiente', d, n, n * pulg, f, n * pulg * f))
    return out


SOLD_NOTA = ('Internos (soportes, distribuidor, rompevórtice; la placa portacartuchos sí está arriba), clips, orejas y estructura del skid '
             '(chasis, plataformas, escaleras, batea) se cotizan por kg, no por pulgada.')


def _f(v):
    if isinstance(v, float):
        return numeros.fmt(v)
    if isinstance(v, int):
        return numeros.fmt(v, 0)
    return v


def _tabla(cab, filas):
    out = ['| ' + ' | '.join(cab) + ' |', '|' + '---|' * len(cab)]
    for f in filas:
        out.append('| ' + ' | '.join(str(_f(x)).replace('|', '/') for x in f) + ' |')
    return '\n'.join(out)


def resumen_md():
    peso_ldm = sum(c * p for _, c, _, p, _ in LDM_PLANO)
    md = []
    md.append('# COT26-0010-002 · AESA (YPF) C5297 PC-02 LANor · Filtros coalescedores FC-301/302 · Resumen del pedido y listas preliminares\n')
    md.append('**Borrador, sin revisar.** Armado el 25-11-2026 por ITT. Lo que no define el cliente lo decidió ITT con el mejor criterio o por antecedentes (TAVAL/37 FC-231 e YPF/27 FC301/302 PC LAS); está marcado "ITT" y se lista al final. Cantidades **por filtro** (un skid); la columna "Total" es por los 2 equipos. Lo genera `listas_preliminares.py` (también `listas_preliminares.xlsx`).\n')
    md.append('## 1. Resumen de la solicitud\n')
    md.append('- **Cliente:** A-Evangelista S.A. (AESA), para YPF. Proyecto C5297, Planta Compresora PC-02 La Angostura Norte (Neuquén). Solped 23583841.')
    md.append('- **Documento base:** requisición 5297-02-0100-IG-EM-RI-001 E0 (30-10-2026), hoja de datos HD-001, P&ID 5297-02-0000-IG-PR-PI-005, plano de conjunto PL-001 (referencial).')
    md.append('- **Qué se pide:** 2 skids paquetizados (SKID-006 con FC-301 y SKID-007 con FC-302), cada uno con su filtro coalescedor vertical y todo lo que está dentro del límite de skid del P&ID: cañerías, válvulas manuales y actuadas, PSV, instrumentos, JB y cableado, traceado eléctrico, aislación, estructura, plataformas, escaleras, batea, PAT, pintura y FAT. "Equipo estándar de YPF, SAP 1000566431, con modificaciones menores" (P&ID nota 8).')
    md.append('- **Posiciones de la planilla (precio unitario, no global):** por cada filtro, el equipo (FC), los repuestos de precomisionado, comisionado y puesta en marcha (RCP) y los repuestos para 2 años (RDO). Opcionales aparte: modelo 3D, asistencia en sitio por día, viaje y herramientas especiales.')
    md.append('- **Diseño:** ASME VIII Div. 1 + C0100, 99 kg/cm2g, −10/65 °C, corrosión 3,2 mm, RT1 (E = 1), PWHT según código, MDMT −10 °C. Operación 70–90 kg/cm2g, 45–55 °C, 2 MMSCMD de gas. Cañerías ASME B31.3 con clases CE32 (#600), CK11/CK31 (baja temperatura) y CA11 (#150).')
    md.append('- **Calidad:** PIE con puntos de espera, PQR presenciados por entidad independiente aprobada por YPF, END por IRAM-ISO 9712, certificados 3.1, Data Book. Garantía de 18 meses del embarque o 12 de la puesta en marcha.')
    md.append('- **Con la oferta:** lista de desvíos y excepciones (FPI-IG-013), antecedentes de 5 años, documentos de la columna A (lista de documentos, repuestos, subproveedores, HD completada, arreglo general, P&ID, ISO 9001, procedimiento de pintura, herramientas especiales, listado de válvulas e instrumentos).')
    md.append('- **No incluye:** cálculo de la despresurización (BDV/RO; sí su fabricación e instalación), detector de gas, sala de control, pernos de anclaje (solo diseño), juntas y espárragos de las uniones del límite del skid.\n')

    md.append('## 2. Skid: materiales y peso\n')
    md.append('### 2.1 Tabla de materiales del plano PL-001 (texto literal del cliente, por skid)\n')
    md.append(_tabla(['Pos.', 'Cant.', 'Descripción', 'Peso un. (kg)', 'Material / línea'], LDM_PLANO))
    md.append(f'\n**Peso total del plano (sin instrumental y cableados): {numeros.fmt(PESO_TOTAL_PLANO)} kg por skid** (la suma de las filas, con las 3 JB, da {numeros.fmt(peso_ldm)} kg: el plano no cierra por {numeros.fmt(peso_ldm - PESO_TOTAL_PLANO)} kg). Peso en elevación desmontado 8.950,00 kg; recipiente vacío ≈ 7.200,00 kg, en operación ≈ 7.600,00 kg y en prueba hidráulica ≈ 9.700,00 kg (HD). Total de los 2 skids ≈ {numeros.fmt(PESO_TOTAL_PLANO * N_EQUIPOS)} kg.\n')
    md.append('Medidas del skid (plano): ≈ 6.000 × 3.400 mm en planta, altura total 6.326 mm, plataformas a +2.480 y +4.720 mm; centro de gravedad X 3.957, Y 1.596, Z 2.249 mm.\n')
    md.append('### 2.2 Recipiente FC (componentes principales, por filtro; pesos aproximados ITT)\n')
    md.append(_tabla(['Descripción', 'Medida', 'Material', 'Cant.', 'Un.', 'Peso aprox. (kg)', 'Origen'], RECIPIENTE))
    md.append(f"\nPeso aproximado de estos componentes: {numeros.fmt(sum(r[5] for r in RECIPIENTE))} kg; sin internos ni elementos filtrantes (la HD da ≈ 7.200,00 kg vacío).\n")
    md.append('### 2.3 Conexiones del recipiente (HD-001, todas WNRF #600)\n')
    md.append(_tabla(['Tag', 'Cant.', 'DN (in)', 'Servicio'], BOQUILLAS_HD))
    md.append('\n### 2.4 Conexiones del límite del skid (plano)\n')
    md.append(_tabla(['Pos.', 'NPS', 'Norma', 'Brida', 'Espesor', 'Clase', 'Servicio'], CONEXIONES_PLANO))

    md.append('\n## 3. Válvulas (por filtro)\n')
    md.append('### 3.1 Manuales\n')
    md.append(_tabla(['Tag', 'Tipo', 'Ø', 'Serie / extremos', 'Clase', 'Cant.', 'Total', 'Función', 'Origen'],
                     [v[:6] + (v[5] * N_EQUIPOS,) + v[6:] for v in VALVULAS]))
    md.append('\n### 3.2 Actuadas, de seguridad y restricción\n')
    md.append(_tabla(['Tag', 'Tipo', 'Ø', 'Serie', 'Clase', 'Cant.', 'Total', 'Función', 'Origen'],
                     [v[:6] + (v[5] * N_EQUIPOS,) + v[6:] for v in VALVULAS_ACTUADAS]))
    md.append('\nLas válvulas Taval (esféricas, globo y retención) se cotizan con lista 30 × 0,52 si Matías lo aprueba; las de control, PSV y actuadores, a terceros.\n')

    md.append('## 4. Instrumentos (por filtro; total ×2)\n')
    md.append(_tabla(['Tag', 'Descripción', 'Conexión', 'Sistema', 'Nota'], INSTRUMENTOS))
    md.append('\n**Señales por skid:**\n')
    md.append(_tabla(['Tag', 'Señal', 'Sistema'], SENALES))
    md.append(f'\nNo incluidos: {FUERA_DE_ALCANCE_INSTR}\n')

    md.append('## 5. Piping: caños y accesorios (por filtro; estimación ITT)\n')
    md.append('### 5.1 Caños\n')
    md.append(_tabla(['Descripción', 'Ø', 'Sch', 'Material', 'Clase', 'Metros', 'Total (m)', 'Líneas'],
                     [c[:6] + (c[5] * N_EQUIPOS,) + c[6:] for c in CANOS]))
    md.append('\n### 5.2 Accesorios\n')
    md.append(_tabla(['Descripción', 'Ø', 'Sch / serie', 'Material', 'Clase', 'Cant.', 'Total'],
                     [a + (a[5] * N_EQUIPOS,) for a in ACCESORIOS]))
    md.append('\n### 5.3 Bridas de cañería (las de las válvulas, instrumentos y boquillas no van acá)\n')
    md.append(_tabla(['Descripción', 'Ø', 'Serie', 'Sch', 'Material', 'Clase', 'Cant.', 'Total'],
                     [b + (b[6] * N_EQUIPOS,) for b in BRIDAS]))

    md.append('\n## 6. Juntas y bulonería (por filtro)\n')
    filas = []
    for d, s, n, j, m, e, med, donde in JUNTAS:
        filas.append((d, s, j, n, n * N_EQUIPOS, m, med, n * e, n * e * N_EQUIPOS, donde))
    md.append(_tabla(['Ø', 'Serie', 'Junta', 'Juntas', 'Total juntas', 'Espárragos (c/ 2 tuercas)', 'Medida', 'Espárragos', 'Total espárragos', 'Uniones'], filas))
    md.append('\nEspárragos y tuercas zincados y bicromatizados (ISO 4042, HD nota 16). Cantidad por unión según ASME B16.5 (`conocimiento/tecnico/esparragos_por_brida.csv`); el 32" según B16.47 Serie A. Sin repuestos: los de RCP y RDO van en su lote.\n')

    md.append('## 7. Elementos filtrantes (por filtro)\n')
    md.append(_tabla(['Descripción', 'Cant.', 'Un.', 'Va en', 'Origen'], FILTRANTES))
    md.append('\nAntecedente: TAVAL/37 (FC-231, 32" #600) usó 16 elementos y una caja de chicanas AISI 304 de 800 × 400 × 400 mm.\n')

    md.append('## 8. Otros artículos (por filtro)\n')
    md.append(_tabla(['Artículo', 'Cantidad', 'Origen'], OTROS))

    md.append('\n## 9. Trabajo eléctrico (por skid)\n')
    md.append('Sí tiene: instrumentación cableada a JB, traceado eléctrico y puesta a tierra.\n')
    md.append(_tabla(['Tema', 'Alcance'], ELECTRICO))

    md.append('\n## 10. Decisiones de ITT y datos que faltan\n')
    for i, t in enumerate(FALTA_O_DECIDIDO, 1):
        md.append(f'{i}. {t}')
    md.append('')

    # ---- 11. Pesos
    P = pesos()
    md.append('\n## 11. Pesos (por skid; tablas de `conocimiento/tecnico/`)\n')
    rub = {}
    for r in P:
        rub[r[0]] = rub.get(r[0], 0.0) + r[4]
    tot = sum(rub.values())
    md.append(_tabla(['Rubro', 'kg por skid', 'kg 2 skids'], [(k, float(v), float(v * N_EQUIPOS)) for k, v in rub.items()] + [('**Total**', float(tot), float(tot * N_EQUIPOS))]))
    md.append(f'\nContra el plano: {numeros.fmt(PESO_TOTAL_PLANO)} kg por skid sin instrumental ni cableados ({numeros.fmt((tot / PESO_TOTAL_PLANO - 1) * 100)} %). La diferencia viene sobre todo de las válvulas de 10": la tabla del plano lista 1 (pos. 501, 732 kg) y el P&ID tiene 3 (+1.464 kg). Faltan instrumentos, cajas, cables, internos de la caja de chicanas, cartuchos, aislación y pintura; las válvulas actuadas y las PSV van con peso aproximado; los metros de caño son estimados sin isométricos.\n')
    md.append('### 11.1 Detalle\n')
    md.append(_tabla(['Rubro', 'Descripción', 'Cant.', 'kg un.', 'kg por skid', 'Fuente'],
                     [(r[0], r[1], r[2], float(r[3]) if r[3] is not None else 'SIN TABLA', float(r[4]), r[5]) for r in P]))

    # ---- 12. Soldaduras
    SP = soldaduras_piping()
    SR = soldaduras_recipiente()
    md.append('\n## 12. Soldaduras (por filtro): pulgadas nominales y equivalentes\n')
    md.append('Pulgada equivalente = Ø × factor de espesor (`tecnico/factores_soldadura.csv`). Olets: Ø de salida × 1,75 (weldolet × 2,5). Caño por metro: cada extremo BW de accesorio o brida es una junta con caño × 0,75 (uniones directas), más los empalmes entre barras de 6 m. Mismas reglas que `herramientas/precotizar.py`. Todo en taller (el skid sale armado).\n')
    md.append('### 12.1 Piping, por tipo y Ø\n')
    md.append(_tabla(['Tipo', 'Ø (pulg)', 'Sch / clase', 'Juntas', 'Pulg. nominales', 'Factor espesor', 'Pulg. equivalentes', 'Pulg-eq 2 filtros'],
                     [(t, float(dn), sch, j, float(pn), float(f), float(pe), float(pe * N_EQUIPOS)) for t, dn, sch, j, pn, f, pe in SP]))
    tipos = {}
    for t, dn, sch, j, pn, f, pe in SP:
        a = tipos.get(t, [0, 0.0, 0.0])
        tipos[t] = [a[0] + j, a[1] + pn, a[2] + pe]
    md.append('\n**Resumen del piping por tipo:**\n')
    filas = [(t, a[0], float(a[1]), float(a[2]), float(a[2] * N_EQUIPOS)) for t, a in tipos.items()]
    tj, tn, te = sum(a[0] for a in tipos.values()), sum(a[1] for a in tipos.values()), sum(a[2] for a in tipos.values())
    filas.append(('**Total piping**', tj, float(tn), float(te), float(te * N_EQUIPOS)))
    md.append(_tabla(['Tipo', 'Juntas', 'Pulg. nominales', 'Pulg. equivalentes', 'Pulg-eq 2 filtros'], filas))
    md.append('\n### 12.2 Recipiente\n')
    md.append(_tabla(['Parte', 'Soldadura', 'Cant.', 'Pulg. nominales', 'Factor espesor', 'Pulg. equivalentes'],
                     [(r[0], r[1], r[2], float(r[3]), float(r[4]), float(r[5])) for r in SR]))
    rn, re_ = sum(r[3] for r in SR), sum(r[5] for r in SR)
    md.append(f'\n**Total recipiente:** {numeros.fmt(rn)} pulg. nominales y {numeros.fmt(re_)} pulg. equivalentes por filtro ({numeros.fmt(re_ * N_EQUIPOS)} los 2).\n')
    md.append(f'**Total skid (piping + recipiente):** {numeros.fmt(te + re_)} pulg-eq por filtro, {numeros.fmt((te + re_) * N_EQUIPOS)} los 2. {SOLD_NOTA} Estructura (plano): {numeros.fmt(sum(r[4] for r in P if r[0] == "Estructura (plano)"))} kg por skid.\n')
    md.append('Antecedente para comparar: TAVAL/37 (FC-231) cotizó la soldadura de cañería + cuerpo como un monto global (USD 71.441,70) y la estructura aparte (USD 10.841,12).\n')
    return '\n'.join(md)


def planilla(ruta):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    wb = Workbook()
    hojas = [
        ('Plano LDM', ['Pos.', 'Cant.', 'Descripción (literal)', 'Peso un. kg', 'Material / línea'], LDM_PLANO),
        ('Recipiente', ['Descripción', 'Medida', 'Material', 'Cant.', 'Un.', 'Peso aprox. kg', 'Origen'], RECIPIENTE),
        ('Válvulas', ['Tag', 'Tipo', 'Ø', 'Serie / extremos', 'Clase', 'Cant. por filtro', 'Función', 'Origen'], VALVULAS + VALVULAS_ACTUADAS),
        ('Instrumentos', ['Tag', 'Descripción', 'Conexión', 'Sistema', 'Nota'], INSTRUMENTOS),
        ('Caños', ['Descripción', 'Ø', 'Sch', 'Material', 'Clase', 'Metros por filtro', 'Líneas'], CANOS),
        ('Accesorios', ['Descripción', 'Ø', 'Sch / serie', 'Material', 'Clase', 'Cant. por filtro'], ACCESORIOS),
        ('Bridas', ['Descripción', 'Ø', 'Serie', 'Sch', 'Material', 'Clase', 'Cant. por filtro'], BRIDAS),
        ('Juntas y bulonería', ['Ø', 'Serie', 'Uniones por filtro', 'Junta', 'Espárrago', 'Espárragos por unión', 'Medida', 'Uniones'], JUNTAS),
        ('Filtrantes', ['Descripción', 'Cant. por filtro', 'Un.', 'Va en', 'Origen'], FILTRANTES),
        ('Otros', ['Artículo', 'Cantidad', 'Origen'], OTROS),
        ('Eléctrico', ['Tema', 'Alcance'], ELECTRICO),
        ('Pesos', ['Rubro', 'Descripción', 'Cant. por filtro', 'kg un.', 'kg por filtro', 'Fuente'], [tuple(float(x) if isinstance(x, (int, float)) and i in (3, 4) else x for i, x in enumerate(r)) for r in pesos()]),
        ('Soldadura piping', ['Tipo', 'Ø pulg', 'Sch / clase', 'Juntas', 'Pulg. nominales', 'Factor espesor', 'Pulg. equivalentes'], [(t, float(d), s_, j, float(pn), f, float(pe)) for t, d, s_, j, pn, f, pe in soldaduras_piping()]),
        ('Soldadura recipiente', ['Parte', 'Soldadura', 'Cant.', 'Pulg. nominales', 'Factor espesor', 'Pulg. equivalentes'], [(a, b, c, float(d), e, float(f)) for a, b, c, d, e, f in soldaduras_recipiente()]),
    ]
    wb.remove(wb.active)
    cab_fill = PatternFill('solid', fgColor='DDE4EE')
    for nombre, cab, filas in hojas:
        ws = wb.create_sheet(nombre)
        ws.append(['COT26-0010-002 AESA C5297 FC-301/302 · borrador, sin revisar · cantidades por filtro (2 equipos)'])
        ws.append(cab)
        for c in ws[2]:
            c.font = Font(bold=True)
            c.fill = cab_fill
        for f in filas:
            ws.append(list(f))
        for col in ws.columns:
            largo = max(len(str(c.value or '')) for c in col[1:])
            ws.column_dimensions[col[0].column_letter].width = min(max(10, largo + 2), 70)
        for fila in ws.iter_rows(min_row=3):
            for c in fila:
                c.alignment = Alignment(wrap_text=True, vertical='top')
                if isinstance(c.value, float):
                    c.number_format = '#,##0.00'
                elif isinstance(c.value, int):
                    c.number_format = '#,##0'
        ws.freeze_panes = 'A3'
    wb.save(ruta)


if __name__ == '__main__':
    with open(os.path.join(AQUI, 'resumen_pedido.md'), 'w', encoding='utf-8') as fh:
        fh.write(resumen_md())
    planilla(os.path.join(AQUI, 'listas_preliminares.xlsx'))
    print('OK: resumen_pedido.md y listas_preliminares.xlsx')
