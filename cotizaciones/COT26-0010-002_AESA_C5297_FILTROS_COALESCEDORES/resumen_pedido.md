# COT26-0010-002 · AESA (YPF) C5297 PC-02 LANor · Filtros coalescedores FC-301/302 · Resumen del pedido y listas preliminares

**Borrador, sin revisar.** Armado el 25-11-2026 por ITT. Lo que no define el cliente lo decidió ITT con el mejor criterio o por antecedentes (TAVAL/37 FC-231 e YPF/27 FC301/302 PC LAS); está marcado "ITT" y se lista al final. Cantidades **por filtro** (un skid); la columna "Total" es por los 2 equipos. Lo genera `listas_preliminares.py` (también `listas_preliminares.xlsx`).

## 1. Resumen de la solicitud

- **Cliente:** A-Evangelista S.A. (AESA), para YPF. Proyecto C5297, Planta Compresora PC-02 La Angostura Norte (Neuquén). Solped 23583841.
- **Documento base:** requisición 5297-02-0100-IG-EM-RI-001 E0 (30-10-2026), hoja de datos HD-001, P&ID 5297-02-0000-IG-PR-PI-005, plano de conjunto PL-001 (referencial).
- **Qué se pide:** 2 skids paquetizados (SKID-006 con FC-301 y SKID-007 con FC-302), cada uno con su filtro coalescedor vertical y todo lo que está dentro del límite de skid del P&ID: cañerías, válvulas manuales y actuadas, PSV, instrumentos, JB y cableado, traceado eléctrico, aislación, estructura, plataformas, escaleras, batea, PAT, pintura y FAT. "Equipo estándar de YPF, SAP 1000566431, con modificaciones menores" (P&ID nota 8).
- **Posiciones de la planilla (precio unitario, no global):** por cada filtro, el equipo (FC), los repuestos de precomisionado, comisionado y puesta en marcha (RCP) y los repuestos para 2 años (RDO). Opcionales aparte: modelo 3D, asistencia en sitio por día, viaje y herramientas especiales.
- **Diseño:** ASME VIII Div. 1 + C0100, 99 kg/cm2g, −10/65 °C, corrosión 3,2 mm, RT1 (E = 1), PWHT según código, MDMT −10 °C. Operación 70–90 kg/cm2g, 45–55 °C, 2 MMSCMD de gas. Cañerías ASME B31.3 con clases CE32 (#600), CK11/CK31 (baja temperatura) y CA11 (#150).
- **Calidad:** PIE con puntos de espera, PQR presenciados por entidad independiente aprobada por YPF, END por IRAM-ISO 9712, certificados 3.1, Data Book. Garantía de 18 meses del embarque o 12 de la puesta en marcha.
- **Con la oferta:** lista de desvíos y excepciones (FPI-IG-013), antecedentes de 5 años, documentos de la columna A (lista de documentos, repuestos, subproveedores, HD completada, arreglo general, P&ID, ISO 9001, procedimiento de pintura, herramientas especiales, listado de válvulas e instrumentos).
- **No incluye:** cálculo de la despresurización (BDV/RO; sí su fabricación e instalación), detector de gas, sala de control, pernos de anclaje (solo diseño), juntas y espárragos de las uniones del límite del skid.

## 2. Skid: materiales y peso

### 2.1 Tabla de materiales del plano PL-001 (texto literal del cliente, por skid)

| Pos. | Cant. | Descripción | Peso un. (kg) | Material / línea |
|---|---|---|---|---|
| 001 | 1 | RECIPIENTE FC-301 / FC-302 C/INSTRUMENTOS | 7.250,00 |  |
| 501 | 1 | VALVULA ESFERICA NPS 10 CL.600 ASME B16.5 RF C/REDUCTOR | 732,00 | SA-216 WCB + A°I° 316 |
| 601 | 1 | CAJA JUNCTION BOX - POTENCIA TRACING | 30,00 |  |
| 605 | 3 | CAJA JUNCTION BOX - INSTRUMENTOS | 30,00 |  |
| 1000 | 1 | CHASIS BASE | 5.642,00 |  |
| 1500 | 1 | PLATAFORMAS Y ESCALERA | 2.690,00 |  |
| 1900 | 1 | ESCALON ACCESO MH | 48,00 |  |
| 2000 | 1 | CANALIZACIONES INSTRUMENTOS | 77,00 |  |
| 2001 | 1 | SALIDA DE GAS NPS 10 SCH80 CL.600 | 2.116,00 | 10"-GH-0269-CE32-BB |
| 2002 | 1 | CAÑERIA DE ENTRADA NPS 10 SCH80 CL.600 | 1.863,00 | 10"-GH-0176-CE32-BB |
| 2003 | 1 | SALIDA DE VAL. PSV NPS 2 SCH160 CL.600 | 598,00 | 2"-V-0262-CE32-BB |
| 2004 | 1 | SALIDA A VENTEO NPS 8 SCH40 CL.150 | 290,00 | 8"-V-0268-CK11-BB |
| 2005 | 1 | CAÑERIA BDV NPS4 CL.600 / NPS2 CL.150 | 584,70 | 4"-GH-0750-CE32-BB |
| 2006 | 1 | SALIDA INFERIOR CONDENSADO NPS2 CL.600 | 301,60 | 2"-LH-0272-CE32-BE |
| 2008 | 1 | SALIDA SUPERIOR DE CONDENSADO NPS2 CL.600 | 279,00 | 2"-LH-0271-CE32-BE |
| 2009 | 1 | CAÑERIA AIRE INSTRUMENTOS NPS2 SCH40 CL.150 | 31,00 | 2"-IA-0601-CA11-BB |
| 2010 | 1 | SALIDA DRENAJE ABIERTO NPS2 CL.150 | 56,00 | 2"-OD-0276-CA11-BB |
| 2011 | 1 | SALIDA DRENAJE CERRADO NPS2 CL.150 | 166,70 | 2"-PD-0275-CE32-BE |

**Peso total del plano (sin instrumental y cableados): 22.320,00 kg por skid** (la suma de las filas, con las 3 JB, da 22.845,00 kg: el plano no cierra por 525,00 kg). Peso en elevación desmontado 8.950,00 kg; recipiente vacío ≈ 7.200,00 kg, en operación ≈ 7.600,00 kg y en prueba hidráulica ≈ 9.700,00 kg (HD). Total de los 2 skids ≈ 44.640,00 kg.

Medidas del skid (plano): ≈ 6.000 × 3.400 mm en planta, altura total 6.326 mm, plataformas a +2.480 y +4.720 mm; centro de gravedad X 3.957, Y 1.596, Z 2.249 mm.

### 2.2 Recipiente FC (componentes principales, por filtro; pesos aproximados ITT)

| Descripción | Medida | Material | Cant. | Un. | Peso aprox. (kg) | Origen |
|---|---|---|---|---|---|---|
| Envolvente (cuerpo) rolado, Ø ext. 812,8 mm, LT/LT 4.064 mm | esp. 31,8 mm (1 1/4") | SA-516 Gr. 70 | 1 | u | 2.490,00 | HD (espesor orientativo, nota 2; lo fija la memoria) |
| Casquete semielíptico 2:1 inferior, Ø ext. 812,8 mm | esp. 31,8 mm | SA-516 Gr. 70 / SA-234 WPB | 1 | u | 230,00 | HD; ITT: cierre superior = M1 |
| Brida WN 32" #600 (M1, boca de inspección superior / acceso a cartuchos) | ASME B16.47 Serie A | SA-105 | 1 | u | 624,00 | HD; peso tabla B16.47 |
| Brida ciega 32" #600 (M1) con pescante | ASME B16.47 Serie A | SA-105 | 1 | u | 1.295,00 | HD nota 22; peso tabla B16.47 |
| Brida WN 20" #600 (MH) + cuello de chapa rolada | ASME B16.5 | SA-105 / SA-516 Gr. 70 | 1 | u | 330,00 | HD |
| Brida ciega 20" #600 (MH) con pescante | ASME B16.5 | SA-105 | 1 | u | 380,00 | HD nota 22 |
| Brida WN 10" #600 + cuello 10" Sch 160 (A y B1) | ASME B16.5 | SA-105 / SA-106 Gr. B | 2 | u | 260,00 | HD; Sch del cuello: ITT (TAVAL/37) |
| Brida WN 4" #600 + cuello 4" Sch 160 (R1, R2) | ASME B16.5 | SA-105 / SA-106 Gr. B | 2 | u | 50,00 | HD |
| Brida ciega 4" #600 (R1, R2) | ASME B16.5 | SA-105 | 2 | u | 40,00 | HD |
| Brida WN 2" #600 + cuello 2" Sch 160 (B2, B3, D, J1, J2, L1–L12, P1, P2, S) | ASME B16.5 | SA-105 / SA-106 Gr. B | 20 | u | 200,00 | HD nota 19 (mín. Sch 160 < 3") |
| Chapas de refuerzo de aberturas (MH 20", A y B1 10") | esp. 31,8 mm | SA-516 Gr. 70 | 3 | u | 150,00 | ITT (a confirmar por cálculo UG-37) |
| Pollera (faldón) con anillo base y aberturas de acceso | esp. 12,7 mm | SA-516 Gr. 70 / SA-36 | 1 | u | 450,00 | HD "Pollera: Sí" |
| Placa portacartuchos (tubesheet) con tensores de cartuchos | esp. 25,4 mm | SA-516 Gr. 70 | 1 | u | 110,00 | HD nota 23; ITT |
| Soportes internos de la caja de chicanas (vigas y ángulos) |  | SA-516 Gr. 70 | 1 | cj | 60,00 | HD "Internos sold.: SA 516 Gr 70" |
| Distribuidor de entrada (deflector) en A |  | SA-516 Gr. 70 | 1 | u | 40,00 | HD "Distribuidor de entrada: Sí" |
| Rompevórtice en B3 con proyección interna |  | SA-516 Gr. 70 | 1 | u | 15,00 | HD nota 20 |
| Orejas de izaje (o trunnions) |  | SA-516 Gr. 70 | 2 | u | 60,00 | HD nota 12 |
| Orejas de puesta a tierra |  | AISI 304L | 2 | u | 2,00 | HD nota 11 (dos) |
| Clips para aislación y clips de instrumentos |  | SA-36 | 1 | cj | 40,00 | HD "Clips aislación / instr.: Sí" |
| Placa de identificación con soporte | C0100 Anexo I | AISI 316 | 1 | u | 3,00 | RI §2 / C0100 |

Peso aproximado de estos componentes: 6.829,00 kg; sin internos ni elementos filtrantes (la HD da ≈ 7.200,00 kg vacío).

### 2.3 Conexiones del recipiente (HD-001, todas WNRF #600)

| Tag | Cant. | DN (in) | Servicio |
|---|---|---|---|
| A | 1 | 10 | Entrada de gas |
| B1 | 1 | 10 | Salida de gas |
| B2 | 1 | 2 | Salida de líquido superior |
| B3 | 1 | 2 | Salida de líquido inferior (proyección interna y rompevórtices) |
| D | 1 | 2 | Drenaje |
| J1/2 | 2 | 2 | Transm. de presión diferencial |
| L1/2 | 2 | 2 | Transmisor de nivel |
| L3/4 | 2 | 2 | Transmisor de nivel |
| L5/6 | 2 | 2 | Indicador de nivel |
| L7/8 | 2 | 2 | Indicador de nivel |
| L9/10 | 2 | 2 | Transmisor de nivel |
| L11/12 | 2 | 2 | Transmisor de nivel |
| MH | 1 | 20 | Boca de hombre (con junta, brida ciega y pescante) |
| M1 | 1 | 32 | Boca de inspección superior (con junta, brida ciega y pescante) |
| P1 | 1 | 2 | Indicador de presión |
| P2 | 1 | 2 | Transmisor de presión |
| R1/2 | 2 | 4 | Reserva c/ brida ciega |
| S | 1 | 2 | Venteo |

### 2.4 Conexiones del límite del skid (plano)

| Pos. | NPS | Norma | Brida | Espesor | Clase | Servicio |
|---|---|---|---|---|---|---|
| AI | 2 | B16.5 | WN RF | Sch 40 | 150 | AIRE INSTRUMENTOS |
| DA | 2 | B16.5 | WN RF | Sch 40 | 150 | DRENAJE ABIERTO |
| DC | 2 | B16.5 | WN RF | Sch 160 | 150 | DRENAJE CERRADO |
| SL | 2 | B16.5 | WN RF | Sch 160 | 600 | SALIDA LIQUIDO |
| EG | 10 | B16.5 | WN RF | Sch 80 | 600 | ENTRADA GAS |
| SG | 10 | B16.5 | WN RF | Sch 80 | 600 | SALIDA GAS |
| SV | 8 | B16.5 | WN RF | Sch 40 | 150 | SALIDA VENTEO |

## 3. Válvulas (por filtro)

### 3.1 Manuales

| Tag | Tipo | Ø | Serie / extremos | Clase | Cant. | Total | Función | Origen |
|---|---|---|---|---|---|---|---|---|
| VF-322 | Esférica paso total (FB) | 10" | #600 RF | CE32 | 1 | 2 | Bloqueo entrada de gas (LO) | P&ID; con reductor (plano pos. 501) |
| VF-337 | Esférica paso total (FB) | 10" | #600 RF | CE32 | 1 | 2 | Bloqueo salida de gas (LO) | P&ID; con reductor |
| VF-339 | Esférica | 10" | #600 RF | CE32 | 1 | 2 | By-pass del filtro (LC) | P&ID; ITT: paso total, con reductor. El plano lista solo 1 válvula de 10": van 3 por P&ID |
| VF-323 | Esférica | 2" | #600 RF | CE32 | 1 | 2 | By-pass de VF-322 para presurizar (LC) | P&ID |
| VG-324 | Globo | 2" | #600 RF | CE32 | 1 | 2 | Regulación de la presurización | P&ID |
| VF-327/328/329/330/331/332/333/334/335/336/359/360 | Esférica paso total (FB) | 2" | #600 RF | CE32 | 12 | 24 | Bloqueo de instrumentos de nivel (L1 a L12) | P&ID |
| VF-340 (LO) / VF-342 (LC) | Esférica paso total (FB) | 2" | #600 RF | CE32 | 2 | 4 | Bloqueo de entrada a PSV-301A/B | P&ID |
| VF-341 / VF-343 | Esférica paso total (FB) | 6" | #150 RF | CK11 (baja temp.) | 2 | 4 | Bloqueo de salida de PSV-301A/B (LO) | P&ID |
| VF-344 | Esférica | 1" | #600 RF | CE32 | 1 | 2 | Venteo manual (LC) | P&ID |
| VG-345 | Globo | 1" | #600 RF | CE32 | 1 | 2 | Venteo manual (regulación) | P&ID |
| VF-338 | Esférica paso total (FB) | 6" | #600 RF | CK31 (baja temp.) | 1 | 2 | Bloqueo aguas abajo de BDV/RO (LO) | P&ID |
| VF-346 / VF-347 | Esférica | 2" | #600 RF | CE32 | 2 | 4 | Bloqueo de LV-301D | P&ID |
| VG-204 | Globo | 2" | #600 RF | CE32 | 1 | 2 | By-pass de LV-301D (P&ID nota 4: Cv ≤ Cv de la LV) | P&ID |
| VF-350 / VF-351 | Esférica | 2" | #600 RF | CE32 | 2 | 4 | Bloqueo de LV-301B | P&ID |
| VG-353 | Globo | 2" | #600 RF | CE32 | 1 | 2 | By-pass de LV-301B (nota 4) | P&ID |
| VR-354 | Retención | 2" | #600 RF | CE32 | 1 | 2 | Salida de condensado | P&ID |
| VF-355 | Esférica | 2" | #600 RF | CE32 | 1 | 2 | Bloqueo salida de condensado (límite) | P&ID |
| VF-356 | Esférica | 2" | #600 RF | CE32 | 1 | 2 | Drenaje D (LC) | P&ID |
| VR-399 | Retención | 2" | #600 RF | CE32 | 1 | 2 | Drenaje cerrado | P&ID |
| VG-357 | Globo | 2" | #600 RF | CE32 | 1 | 2 | Drenaje cerrado (regulación) | P&ID |
| VF-358 | Esférica | 2" | #150 RF | CA11 | 1 | 2 | Entrada de aire de instrumentos | P&ID |
| VF-325 / VF-326 | Esférica paso total (FB) | 1 1/2" | NPT | CE32 | 2 | 4 | Cupón CC-301 e inyección de químico (nota 3) | P&ID |
| (sin tag) | Esférica 2000 WOG (TCH2N) | 1/2" | NPT | CE32 / CA11 | 27 | 54 | Venteos y purgas de instrumentos (12), PSV (4), aire IA1–IA5 + reserva (6), LG (4), CC (1) | P&ID; cantidad contada por ITT |
| (sin tag) | Esférica 2000 WOG (TCH2N) | 3/4" | NPT | CE32 / CA11 | 11 | 22 | Drenajes de LV/SDV (4), VR-354 (1), PDIT (2), PIT (1), PI (1), aire (1), OD1 (1) | P&ID; cantidad contada por ITT |

### 3.2 Actuadas, de seguridad y restricción

| Tag | Tipo | Ø | Serie | Clase | Cant. | Total | Función | Origen |
|---|---|---|---|---|---|---|---|---|
| LV-301D (+ LY-301D) | Control, globo, actuador neumático, posicionador 4–20 mA HART | 2" | #600 RF | CE32 | 1 | 2 | Control de nivel sección superior (falla cierra, FC). RI §10: no debe pasar más de 3.750 kg/h de gas en blow-by | P&ID; Cv por ITT con el proveedor |
| LV-301B (+ LY-301B) | Control, globo, actuador neumático, posicionador 4–20 mA HART | 2" | #600 RF | CE32 | 1 | 2 | Control de nivel sección inferior (FC). Idem RI §10 | P&ID |
| SDV-301C | Esférica de corte, actuador neumático simple efecto, solenoide SV-301C, fines de carrera ZSO/ZSC-301C | 2" | #600 RF | CE32 | 1 | 2 | Corte por SIS línea superior (FC) | P&ID |
| SDV-301 | Esférica de corte, actuador neumático simple efecto, solenoide SV-301, fines de carrera ZSO/ZSC-301 | 2" | #600 RF | CE32 | 1 | 2 | Corte por SIS línea inferior (FC) | P&ID |
| BDV-301E | Esférica de blowdown, actuador neumático, solenoide SV-301E, fines de carrera ZSO/ZSC-301E | 4" | #600 RF | CE32 | 1 | 2 | Despresurización (falla abre, FO); comando HS-003 | P&ID; P&ID nota 10 |
| PSV-301A / PSV-301B | Seguridad, API 526, orificio D | 1" × 2" | #600 RF × #150 RF | CE32 / CK11 | 2 | 4 | Set 99 kg/cm2g, caso fuego (alcance del proveedor, RI §10) | P&ID |
| RO-301 | Placa orificio de restricción con bridas portaplaca B16.36 | 4" | #600 RF | CE32 / CK31 | 1 | 2 | Restricción del blowdown (dimensionamiento de AESA, RI §10) | P&ID |

Las válvulas Taval (esféricas, globo y retención) se cotizan con lista 30 × 0,52 si Matías lo aprueba; las de control, PSV y actuadores, a terceros.

## 4. Instrumentos (por filtro; total ×2)

| Tag | Descripción | Conexión | Sistema | Nota |
|---|---|---|---|---|
| LIT-301A | Transmisor de nivel por presión diferencial con sellos remotos (J0402) | 2" #600 RF ×2 | SIS (LALL-301A, I-27) | Sección inferior; traceado (nota 2); capilares cortos (nota 5) |
| LIT-301B | Transmisor de nivel DP con sellos remotos | 2" #600 RF ×2 | SCP (LIC-301B → LV-301B) | Sección inferior |
| LIT-301C | Transmisor de nivel DP con sellos remotos | 2" #600 RF ×2 | SIS (LALL-301C, I-26) | Sección superior |
| LIT-301D | Transmisor de nivel DP con sellos remotos | 2" #600 RF ×2 | SCP (LIC-301D → LV-301D) | Sección superior |
| LG-301A | Indicador de nivel de vidrio (J0401), tipo reflex, con válvulas de bloqueo con bola de retención | 2" #600 RF ×2 | Local | Sección inferior. ITT: reflex (HD-J0401-01) |
| LG-301B | Indicador de nivel de vidrio tipo reflex | 2" #600 RF ×2 | Local | Sección superior |
| PDIT-301 | Transmisor de presión diferencial (J0304) con manifold de 5 vías (M5) | 1/2" NPT | SCP (PDI/PDAH-301) | Ensuciamiento de cartuchos; tomas J1/J2 |
| PIT-301B | Transmisor de presión (J0304) con manifold de 2 vías (M2) | 1/2" NPT | SIS (PAHH-301B, I-25) | Toma P2 |
| PI-301A | Manómetro Ø 100 mm con glicerina, 0–160 kg/cm2 (J0301), con manifold M2 | 1/2" NPT | Local | Toma P1. Rango: ITT |
| CC-301 | Portacupón de corrosión con cupón (típico 1 del P&ID) | 1 1/2" NPT | Local | Con VF-325 |

**Señales por skid:**

| Tag | Señal | Sistema |
|---|---|---|
| LIT-301A | Analógica 4–20 mA | SIS |
| LIT-301C | Analógica 4–20 mA | SIS |
| PIT-301B | Analógica 4–20 mA | SIS |
| LIT-301B | Analógica 4–20 mA | SCP |
| LIT-301D | Analógica 4–20 mA | SCP |
| PDIT-301 | Analógica 4–20 mA | SCP |
| LY-301B | Analógica 4–20 mA (salida) | SCP |
| LY-301D | Analógica 4–20 mA (salida) | SCP |
| SV-301 / SV-301C / SV-301E | Digital (salida, 24 Vcc) | SIS |
| ZSO/ZSC-301, ZSO/ZSC-301C, ZSO/ZSC-301E | Digital (entrada) ×6 | SIS / SCADA |

No incluidos: HS-003, HS-301, HS-301C, ESD1/ESD2, enclavamientos I-25/26/27/209/213/214 y las funciones LI/LAL/LAH/PDI/PAH (son de sala de control); AT-006 (detector de gas, fuera del límite del skid).

## 5. Piping: caños y accesorios (por filtro; estimación ITT)

### 5.1 Caños

| Descripción | Ø | Sch | Material | Clase | Metros | Total (m) | Líneas |
|---|---|---|---|---|---|---|---|
| Caño sin costura BE | 10" | Sch 80 | ASTM A106 Gr. B | CE32 | 24 | 48 | Entrada 10"-GH-1105/0176, salida 10"-GH-0269 y by-pass 10"-GH-0297 |
| Caño sin costura BE | 4" | Sch 80 | ASTM A106 Gr. B | CE32 | 5 | 10 | BDV 4"-GH-0750 |
| Caño sin costura BE | 4" | Sch 80 | ASTM A333 Gr. 6 | CK31 | 1 | 2 | 4"-V-0752 aguas abajo de RO-301 |
| Caño sin costura BE | 6" | Sch 80 | ASTM A333 Gr. 6 | CK31 | 2 | 4 | Tramo de VF-338 |
| Caño sin costura BE | 8" | Sch 40 | ASTM A333 Gr. 6 | CK11 | 6 | 12 | Colector de venteo 8"-V-0268 (plano: Sch 40; la clase pide Sch 20: ITT toma Sch 40) |
| Caño sin costura BE | 6" | Sch 40 | ASTM A333 Gr. 6 | CK11 | 6 | 12 | Salidas de PSV 6"-V-0265/0266 |
| Caño sin costura BE | 3" | Sch 40 | ASTM A333 Gr. 6 | CK11 | 1 | 2 | Salidas de PSV (tramos 3") |
| Caño sin costura BE | 2" | Sch 160 | ASTM A106 Gr. B | CE32 | 33 | 66 | PSV 2"-V-0262/0263, condensado LH-0271/0272/0273, drenaje PD-0275, puentes de nivel, by-pass de entrada |
| Caño sin costura PE | 1" | Sch 160 | ASTM A106 Gr. B | CE32 | 2 | 4 | Entradas de PSV y venteo manual |
| Caño sin costura PE | 1" | Sch 80 | ASTM A333 Gr. 6 | CK11 | 3 | 6 | Venteo 1"-V-0267 |
| Caño sin costura BE | 2" | Sch 40 | ASTM A106 Gr. B | CA11 | 17 | 34 | Drenaje abierto OD-0276, aire IA-0601, drenaje cerrado PD-0274 |
| Niples sin costura NPT | 1/2" y 3/4" | Sch 160 | ASTM A106 Gr. B | CE32 | 40 | 80 | Venteos, drenajes e instrumentos (unidades) |

### 5.2 Accesorios

| Descripción | Ø | Sch / serie | Material | Clase | Cant. | Total |
|---|---|---|---|---|---|---|
| Codo 90° RL BW | 10" | Sch 80 | ASTM A234 WPB | CE32 | 8 | 16 |
| Te normal BW | 10" | Sch 80 | ASTM A234 WPB | CE32 | 2 | 4 |
| Weldolet 10" × 4" | 10" × 4" | Sch 80 | ASTM A105 | CE32 | 1 | 2 |
| Codo 90° RL BW | 4" | Sch 80 | ASTM A234 WPB | CE32 | 3 | 6 |
| Reducción concéntrica BW | 6" × 4" | Sch 80 | ASTM A420 WPL6 | CK31 | 1 | 2 |
| Codo 90° RL BW | 8" | Sch 40 | ASTM A420 WPL6 | CK11 | 2 | 4 |
| Te normal BW | 8" | Sch 40 | ASTM A420 WPL6 | CK11 | 2 | 4 |
| Codo 90° RL BW | 6" | Sch 40 | ASTM A420 WPL6 | CK11 | 4 | 8 |
| Reducción concéntrica BW | 6" × 3" | Sch 40 | ASTM A420 WPL6 | CK11 | 2 | 4 |
| Reducción concéntrica BW | 3" × 2" | Sch 40 × Sch 80 | ASTM A420 WPL6 | CK11 | 2 | 4 |
| Codo 90° RL BW | 2" | Sch 160 | ASTM A234 WPB | CE32 | 30 | 60 |
| Te normal BW | 2" | Sch 160 | ASTM A234 WPB | CE32 | 6 | 12 |
| Reducción concéntrica BW | 2" × 1" | Sch 160 | ASTM A234 WPB | CE32 | 2 | 4 |
| Casquete BW | 2" | Sch 160 | ASTM A234 WPB | CE32 | 2 | 4 |
| Codo 90° SW | 1" | 6000# | ASTM A105 | CE32 | 4 | 8 |
| Codo 90° SW | 1" | 3000# | ASTM A350 LF2 | CK11 | 2 | 4 |
| Codo 90° RL BW | 2" | Sch 40 | ASTM A234 WPB | CA11 | 10 | 20 |
| Te normal BW | 2" | Sch 40 | ASTM A234 WPB | CA11 | 6 | 12 |
| Casquete BW | 2" | Sch 40 | ASTM A234 WPB | CA11 | 2 | 4 |
| Thredolet 3000# | 1/2" | NPT | ASTM A105 | CE32 / CA11 | 20 | 40 |
| Thredolet 3000# | 3/4" | NPT | ASTM A105 | CE32 / CA11 | 10 | 20 |
| Tapón hexagonal 3000# | 1/2" y 3/4" | NPT | ASTM A105 | CE32 / CA11 | 38 | 76 |

### 5.3 Bridas de cañería (las de las válvulas, instrumentos y boquillas no van acá)

| Descripción | Ø | Serie | Sch | Material | Clase | Cant. | Total |
|---|---|---|---|---|---|---|---|
| Brida WN RF | 10" | #600 | Sch 80 | ASTM A105 | CE32 | 8 | 16 |
| Brida WN RF | 4" | #600 | Sch 80 | ASTM A105 | CE32 | 2 | 4 |
| Brida portaplaca WN RF (par, para RO-301) | 4" | #600 | Sch 80 | ASTM A105 | CE32 (B16.36) | 1 | 2 |
| Brida WN RF | 6" | #600 | Sch 80 | ASTM A350 LF2 | CK31 | 2 | 4 |
| Brida WN RF | 6" | #150 | Sch 40 | ASTM A350 LF2 | CK11 | 4 | 8 |
| Brida WN RF (límite SV) | 8" | #150 | Sch 40 | ASTM A350 LF2 | CK11 | 1 | 2 |
| Brida WN RF | 2" | #150 | Sch 80 | ASTM A350 LF2 | CK11 | 2 | 4 |
| Brida WN RF | 2" | #600 | Sch 160 | ASTM A105 | CE32 | 40 | 80 |
| Brida WN RF (límite DC) | 2" | #150 | Sch 160 | ASTM A105 | CA11 | 1 | 2 |
| Brida WN RF | 2" | #150 | Sch 40 | ASTM A105 | CA11 | 4 | 8 |
| Brida SW RF | 1" | #600 | Sch 160 | ASTM A105 | CE32 | 5 | 10 |
| Brida ciega RF perforada y roscada 3/4" NPT (P1, P2, J1, J2) | 2" | #600 |  | ASTM A105 | CE32 | 4 | 8 |

## 6. Juntas y bulonería (por filtro)

| Ø | Serie | Junta | Juntas | Total juntas | Espárragos (c/ 2 tuercas) | Medida | Espárragos | Total espárragos | Uniones |
|---|---|---|---|---|---|---|---|---|---|
| 32" | #600 | Espiralada AISI 316/grafito 4,5 mm, anillo ext. AC zincado + int. AISI 316 (B16.20, para B16.47 A) | 1 | 2 | A193 B7 / A194 2H zincado | 2" × 15 1/2" (a verificar) | 28 | 56 | M1 |
| 20" | #600 | Espiralada 316/grafito, anillo ext. + int. | 1 | 2 | A193 B7 / A194 2H zincado | 1 5/8" × 11 1/2" | 24 | 48 | MH |
| 10" | #600 | Espiralada 316/grafito, anillo ext. + int. | 8 | 16 | A193 B7 / A194 2H zincado | 1 1/4" × 8 1/2" | 128 | 256 | A, B1, VF-322, VF-337, VF-339 |
| 6" | #600 | Espiralada 316/grafito, anillo ext. AC zincado | 2 | 4 | A320 L7 / A194 Gr. 7 (CK31) | 1" × 6 3/4" | 24 | 48 | VF-338 |
| 6" | #150 | Espiralada 316/grafito, anillo ext. AC zincado | 4 | 8 | A320 L7 / A194 Gr. 7 (CK11) | 3/4" × 4" | 32 | 64 | VF-341, VF-343 |
| 4" | #600 | Espiralada 316/grafito, anillo ext. AC zincado | 5 | 10 | A193 B7 / A194 2H zincado | 7/8" × 5 3/4" (RO: más largo) | 40 | 80 | R1, R2, BDV-301E, RO-301 |
| 2" | #600 | Espiralada 316/grafito, anillo ext. AC zincado | 58 | 116 | A193 B7 / A194 2H zincado | 5/8" × 4 1/4" | 464 | 928 | Boquillas, válvulas de línea, LV/SDV, drenaje, PSV |
| 2" | #600 | Junta dieléctrica VCS epoxi RFG (kit con camisas y arandelas) | 12 | 24 | A193 B7 / A194 2H zincado | 5/8" × 4 3/4" (kit JD) | 96 | 192 | Instrumentos de nivel L1–L12 (P&ID "JD"; nota general 2G) |
| 2" | #150 | Espiralada 316/grafito, anillo ext. AC zincado | 4 | 8 | B7 (CA11) / L7 (CK11) | 5/8" × 3 1/4" | 16 | 32 | Salidas de PSV, VF-358 |
| 1" | #600 | Espiralada 316/grafito, anillo ext. AC zincado | 5 | 10 | A193 B7 / A194 2H zincado | 5/8" × 3 3/4" | 20 | 40 | Entradas de PSV, venteo manual |

Espárragos y tuercas zincados y bicromatizados (ISO 4042, HD nota 16). Cantidad por unión según ASME B16.5 (`conocimiento/tecnico/esparragos_por_brida.csv`); el 32" según B16.47 Serie A. Sin repuestos: los de RCP y RDO van en su lote.

## 7. Elementos filtrantes (por filtro)

| Descripción | Cant. | Un. | Va en | Origen |
|---|---|---|---|---|
| Cartucho coalescente Ø ext. 141 × 915 mm, núcleo y tapas de acero inoxidable, medio de fibra de vidrio (SS + FG), flujo interior → exterior, 99,99 % > 0,3 µm, arrastre máx. 1 ppm, ΔP limpio 0,15 bar / colapso 3 bar | 9 | u | Equipo | HD línea 31-36 y nota 23 (cantidad y medida "a confirmar por fabricante") |
| Caja de chicanas (separación primaria) rectangular doble bolsillo, flujo horizontal, 800 × 650 × 200 mm, chapa 0,8 mm, AISI 316L, 99 % > 20 µm | 1 | u | Equipo | HD nota 23. ITT: en 2 módulos para sacarla por M1 (no pasa entera por MH 20" ni por M1) |
| Juntas / O-rings de asiento de cartuchos | 9 | u | Equipo | ITT (las da el fabricante del cartucho) |
| Cartuchos para precomisionado, comisionado y puesta en marcha (1 juego) | 9 | u | RCP | RI §8: mínimo 1 juego para PEM |
| Cartuchos para 2 años de operación (2 juegos) | 18 | u | RDO | RI §8: 2 juegos para 2 años |
| Juntas de asiento de cartuchos de repuesto | 27 | u | RCP / RDO | ITT (una por cartucho de repuesto) |

Antecedente: TAVAL/37 (FC-231, 32" #600) usó 16 elementos y una caja de chicanas AISI 304 de 800 × 400 × 400 mm.

## 8. Otros artículos (por filtro)

| Artículo | Cantidad | Origen |
|---|---|---|
| Chasis base (patín) autoportante, sin grout, con cáncamos de izaje verificados ASME BTH-1 (coef. ≥ 4) y ojales de amarre | 1 cj | Plano pos. 1000 (5.642 kg); RI §2 y §12 |
| Plataformas (2 niveles, +2.480 y +4.720 mm), escalera marinera y barandas, con rejilla | 1 cj | Plano pos. 1500 (2.690 kg); HD "Escaleras / plataformas: Sí" |
| Escalón de acceso a MH | 1 u | Plano pos. 1900 (48 kg) |
| Batea de contención de drenajes y salpicaduras con descarga a drenaje abierto | 1 u | RI §2; P&ID "batea skid". ITT: chapa 4,76 mm A36 |
| Soportes de cañería (típicos 5165-02-0000-IG-PI-TM-001) | 1 cj | RI §9 |
| Embudos de drenaje abierto OD1, OD2, OD3 | 3 u | P&ID |
| Tubing inox 1/2" con conectores para aire de instrumentos (IA1–IA5 a actuadores) | 30 m | P&ID; ITT |
| Tubing inox 1/2" con conectores para impulsos de PDIT/PIT/PI | 15 m | ITT |
| Aislación del recipiente completo: lana mineral 70 kg/m3, 60 mm, chapa de aluminio ASTM B209 3003/3105 H14/H24 de 1 mm | ≈ 12 m2 | HD nota 10 |
| Aislación de líneas e instrumentos traceados (B2, B3, D, puentes de nivel) | ≈ 25 m | HD notas 10 y 21; P&ID "E30" |
| Pintura B0600: sistema 202 (superficies aisladas) y 201 (resto); RAL 9006 recipiente, 9011 estructura, 1016 escaleras | 1 gl | HD nota 9 |
| Chapas de identificación de TAG de válvulas e instrumentos, AISI 316 | ≈ 60 u | RI §2; ITT |
| Protectores de bridas y embalaje para transporte (ED(EP)-B-01.00); repuestos en bultos separados e identificados | 1 gl | RI §11 |
| Repuestos incluidos (RI §8): espárragos 15 % PEM y 10 % 2 años (mín. 5 por medida); juntas 3 + 2 por medida; kit de PSV (1 por válvula); kit de LV (1 por válvula); 1 instrumento de cada tipo para PEM y 1 para 2 años | 1 lote RCP + 1 lote RDO | RI §8 |
| Pernos de anclaje: solo diseño (el skid apoya sin grout) | — | RI §2 |
| Opcionales (RI §2): modelo 3D CADWorx con atributos BIM; asistencia técnica en sitio por día; viaje al sitio; herramientas especiales | — | Se cotizan aparte |

## 9. Trabajo eléctrico (por skid)

Sí tiene: instrumentación cableada a JB, traceado eléctrico y puesta a tierra.

| Tema | Alcance |
|---|---|
| Área clasificada | Clase I, Zona 2, Grupo IIA, T3 (HD nota 18): todo el material eléctrico certificado Ex para zona 2 y mínimo IP-65 (RI §2). |
| Cajas de conexionado | 4 JB de instrumentos segregadas por sistema y tipo de señal (analógicas SIS, analógicas SCP, digitales SIS, digitales SCP; RI §2) + 1 JB de potencia del traceado (plano pos. 601). El plano dibuja 3 JB de instrumentos (pos. 605): ITT toma 4 porque la RI manda sobre el plano (orden de prelación). Con borneras, riel DIN y 20 % de reserva. |
| Cableado de instrumentos | De cada instrumento, solenoide y fin de carrera a su JB, con cables según J1301 / P1000 y reservas. Señales: 8 analógicas (LIT ×4, PDIT, PIT, LY ×2) y 9 digitales (SV ×3, ZSO/ZSC ×6). El cable de JB a sala de control es de AESA. |
| Canalizaciones | Caño conduit galvanizado y accesorios Ex (P1100), bandeja portacables sobre el skid (P1102), prensacables Ex (P1103), soportes de conduit. El plano estima 77 kg de canalizaciones (pos. 2000). |
| Traceado eléctrico (P0103) | Cable calefactor autorregulado en el recipiente hasta HHLL (zona inferior, "E60" en el P&ID), líneas de condensado B2/B3, drenaje D y conexiones e instrumentos de nivel ("E30"). ITT: 4 circuitos con termostato, alimentados desde la JB de potencia. Incluye memoria de cálculo, listado de materiales, plano de canalización y diagrama de conexionado (RI §13, 3.1 a 3.4). |
| Puesta a tierra (P1105) | 2 orejas de PAT en el recipiente (AISI 304L) y 3 puntos de PAT en el chasis (plano), con equipotencialización de JB, instrumentos y estructura. |
| Aire de instrumentos | Colector 2"-IA-0601 con 5 tomas (IA1–IA5) a los actuadores de LV-301B/D, SDV-301/301C y BDV-301E (tubing inox 1/2"). |
| Documentos | Listado de cables, plano de PAT, plano de JB, diagramas de conexionado y listado de instrumentos y señales (RI §13, 3.5 a 4.7). |
| Pruebas | FAT con prueba de lazos de instrumentos, válvulas actuadas y traceado (RI §2; RC §1). |

## 10. Decisiones de ITT y datos que faltan

1. Cantidad y medida de cartuchos (9 × Ø 141 × 915 mm) y caja de chicanas: se toman de la HD; las confirma el fabricante de elementos (pedir cotización a Pall, Gora u otro).
2. Altura del recipiente: HD 4.064 mm LT/LT, P&ID 4.184 mm T-T y plano 4.663 mm LT-LRF (hasta la cara de la brida M1). Se toma la HD; las tres cotas son compatibles si se miden a puntos distintos.
3. Válvulas de 10": el plano lista 1 (pos. 501) y el P&ID tiene 3 (VF-322, VF-337, VF-339). Se toman 3.
4. JB de instrumentos: el plano dibuja 3 y la RI pide segregarlas en 4. Se toman 4 (la RI manda).
5. Colector de venteo de 8": el plano dice Sch 40 y la clase CK11 da Sch 20. Se toma Sch 40.
6. Aguas abajo de PSV y de BDV/RO (CK11 y CK31) el material es de baja temperatura (A333 Gr. 6, A350 LF2, A420 WPL6, espárragos A320 L7).
7. Largos de cañería y cantidad de accesorios: estimados por ITT con el P&ID, las cotas del plano y los pesos de su tabla (no hay isométricos).
8. Juntas dieléctricas: 12 (una por instrumento de nivel). Las uniones con el exterior (límites del skid) llevan solo nuestra brida; junta y espárragos los pone AESA.
9. Detector de gas AT-006 y las funciones de sala de control: fuera del alcance (fuera del límite del skid).
10. Especificaciones que no vinieron (C-02.00, J1800, J0301, J0402, J1302, J1304, J1400, P1100, P1102, P1103, P1105): se cotiza según buena práctica y se aclara en la oferta.
