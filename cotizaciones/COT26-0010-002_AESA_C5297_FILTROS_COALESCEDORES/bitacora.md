# Bitácora COT26-0010-002 · AESA (YPF) · C5297 PC-02 LANor · 2 filtros coalescedores FC-301/302 en skid (SKID-006/007)

**Estado: recopilación de información (25-11-2026). Sin cómputo ni precios.** Matías pidió por ahora solo leer y juntar la información.

## Pedido recibido (25-11-2026, de Matías)
- `pedido/5297-02-0100-IG-EM-RI-001.pdf` (+ .txt): requisición de ingeniería VCD26288-E-002, E0 30/10/2026 "emisión para información". Código YPF LANor-PCLANOR02-VCD26288-M-RI-003003.
- `pedido/Planilla_de_cotizacion_REV_01.xlsx`: proyecto C5297, solped 23583841, 6 posiciones (orden invertido respecto de la RI):
  pos 10 RDO FC-302 (C529702IGEMFIL_015) · 20 RCP FC-302 (_014) · 30 FC-302 (_013) · 40 RDO FC-301 (_012) · 50 RCP FC-301 (_011) · 60 FC-301 (_010). Cantidad 1 UNI cada una; textos "VER RI".
- `pedido/ANEXO 1 - Documentos del proyecto/`: hoja de datos HD-001, P&ID 5297-02-0000-IG-PR-PI-005 (4 hojas: SB-306/307 y FC-301/302), plano de conjunto general 5297-02-0100-IG-EM-PL-001 (E0 22-10-2026, referencial), típicos de soportes 5165-02-0000-IG-PI-TM-001, ET estructuras metálicas 5297-01-0000-IG-ES-ET-001, formularios FPI-IG-002 (lista de documentos), FPI-IG-012 (consultas técnicas), FPI-IG-013 (excepciones y desvíos).
- `pedido/ANEXO 2 - Especificaciones de YPF/`: C0100, C0107, ED(EP)-C-01.08 Filtros, L0200 (con Anexo I clases de cañerías y Anexo II válvulas), M0100, B0600 (+ anexos), J0100/J0300/J0304/J0400/J0401/J0600/J0602/J1000/J1300/J1301/J1303/J1700, P0100/P0103/P1000/P1104, IG.AR 40.00.140 repuestos, típicos L0100 (.dwg), hojas de datos de instrumentos y válvulas.
- `pedido/ANEXO 3 - Requerimientos de Calidad/`: RC 5297-02-0100-IG-EM-RI-001.
- `pedido/ANEXO 4 - …Condiciones de Obra/`: un .msg (sin abrir todavía).
- `pedido/ANEXO 5- Requerimientos BIM/`: PTC y PC LAN – Requerimientos BIM mínimos.
- Documentación general de AESA (condiciones de compra y subcontratación, SHyMA/MASS, logística, gestión de documentos, lista de excepciones): `fuentes_originales/aesa_documentacion_LAN_2026-11/` (sirve también para COT26-0010-001).
- Los PDF tienen su texto extraído al lado (.txt). Varios PDF de típicos (TI-J1700, PE(EP)-L/M) son escaneos o dibujos sin texto.

## Alcance (RI §1, §2, §8, HD notas 1 y 23)
- 2 skids paquetizados (SKID-006 con FC-301, SKID-007 con FC-302) con todo lo que está dentro del recuadro azul del P&ID: recipiente, internos (caja de chicanas 316L + 9 cartuchos coalescentes), cañerías, válvulas (incl. BDV, SDV, LV, PSV por fuego), instrumentos, JB, cableado, traceado eléctrico, aislación, estructura, escaleras, plataformas, batea de contención, puesta a tierra, placas, pintura, FAT.
- Por cada filtro: RCP (repuestos de precomisionado, comisionado y PEM) y RDO (repuestos 2 años), con precios unitarios. Repuestos incluidos en el alcance según RI §8 (15%/10% de espárragos, juntas 3+2 por medida, kits de PSV y válvulas de control, 1 instrumento de cada tipo, cartuchos: 1 juego PEM + 2 juegos 2 años).
- Opcionales (no están en la planilla): modelo 3D CADWorx con atributos BIM, asistencia técnica en sitio (valor diario), viaje al sitio, herramientas especiales.
- No incluye: cálculo y especificación del sistema de despresurización (BDV, RO), sí su fabricación e instalación (RI §10).

## Datos técnicos principales (HD-001, plano PL-001, P&ID)
- Vertical, ASME VIII Div.1 + C0100, diseño 99 kg/cm2g y −10/65 °C, operación 70–90 kg/cm2g y 45–55 °C, CA 3,2 mm, RT1 (E=1), PWHT s/ código y ED(EP)-B-05.00, MDMT −10 °C.
- Ø ext. 812,8 mm (32"), espesor 31,8 mm (orientativo), materiales SA-516 Gr70 / SA-234 WPB / SA-106 B / SA-105, bulonería B7/2H zincada bicromatizada.
- Conexiones #600 WNRF: A y B1 10", MH 20", M1 32" (con brida ciega y pescante), R1/2 4" ciegas, resto 2" (B2, B3, D, J, L1–L12, P1, P2, S); cuellos < 3" mínimo Sch 160.
- Caudal 2.000.000 Sm3/d (plano); casos A, 26 y turndown en HD nota 24. Eficiencia 99,99% > 0,3 µm; cartuchos Ø 141 × 915 mm, 9 unidades (a confirmar por fabricante).
- Aislación lana mineral 60 mm con chapa de aluminio, traceado hasta HHLL; pintura B0600 sistema 202 (aislado) / 201; RAL 9006, 9011 y 1016. Área Clase I Zona 2 IIA T3.
- Pesos: recipiente ~7.200 kg vacío (HD); skid completo 22.320 kg (plano: chasis 5.642, plataformas y escalera 2.690, cañerías de entrada/salida 10" Sch 80 #600, válvula esférica 10" #600 SA-216 WCB, etc.). Skid ~7.000 × 5.000 mm, altura 6.326 mm.
- P&ID nota 8: "Los filtros corresponden al equipo estándar de YPF, Nro. SAP 1000566431, con modificaciones menores."

## Diferencias ya vistas entre documentos (para consultas)
1. Altura del recipiente: HD 4.064 mm LT/LT; plano 4.663 mm (LT-LRF); P&ID 4.184 mm T-T.
2. Fechas: RI E0 30/10/2026; HD E0 30/10/2025.
3. Planilla con las posiciones en orden inverso a la RI y sin renglones para los opcionales.
4. RI cita para filtros también la C0107 Separadores y la ED(EP)-C-01.08 (filtros).

## Antecedentes encontrados (sin analizar todavía)
- YPF/27 (OE 381-25 Rev 2, 18-08-2025): 2 filtros coalescedores **FC301/FC302 C5064 PC LAS**, USD 322.081,64 c/u, RDO 10.718,10, RCP 3.559,20, PEM opcional 4.000; 175 días. Mismos tags en la planta hermana: probable gemelo.
- TAVAL/37 (PRES 24148, 17-12-2025): filtro coalescedor FC-231 YPF, cuerpo 32" #600, 16 elementos, con skids; USD 529.204,77; factor 1,31; 210 días; **con planilla de costo** (LM costos Coalescedor FC-231 YPF - PC0-C REV. 0).
- Sacde/12 (18-12-2025): coalescedores SK-0301/02, con planilla de costo.
- 2022 (sin ficha): AESA/12 "Filtros coalescedor" (OT 201-22) y AESA/20 "Filtro coalescedor FC-231 FC-431" (OT 226-22), ambos citan el SAP 1000566431.
- Cotización hermana del mismo proyecto: COT26-0010-001 (filtros de gas FCC-707/708).

## Revisión de toda la información (25-11-2026, 2ª pasada)
Abiertos todos los anexos; cada PDF, docx, xlsx, doc y xls tiene su texto al lado (.txt o .csv). El .msg del Anexo 4 se abrió con un lector propio (sin librerías) y sus adjuntos están en `pedido/ANEXO 4 …/adjuntos/`.
- **P&ID (4 hojas, E0 16-10-2026):** completo y legible; alcanza para sacar válvulas, instrumentos, líneas y clases (CE32, CK11, CK31, CA11, todas en L0200 Anexo I). Dentro del límite del SKID-006 entran, entre otras cosas: PSV-301A/B (1" #600 × 2" #150, set 99 kg/cm2, caso fuego), BDV-301E 4" #600 con RO-301, SDV-301C y SDV-301 (2" #600), LV-301D y LV-301B (2" #600, con bypass VG-204/VG-353 y bloqueos VF), VR-354, unos 35 VF y VG, LIT-301A/B/C/D, LG, PDIT/PDI-301, PIT-301B, PI-301A, CC-301 (cupón de corrosión), aire de instrumentos IA1–IA5, colectores de venteo 8" #150 y drenajes, y la batea del skid. La HD p. 4 (listas de válvulas e instrumentos) viene vacía: sale del P&ID.
- **RC (Anexo 3):** PIE con puntos de espera, FAT si hay instrumentos y válvulas actuadas, PQR presenciados y certificados por entidad independiente aprobada por YPF, END por IRAM-ISO 9712, certificados 3.1 EN 10204, Data Book.
- **Anexo 4 (Condiciones de obra):** mail de AESA (G. Falco) con "5165 - Condiciones de obra para las RI 2025.12.05" y 14 anexos. Es un paquete genérico del proyecto C5165 (PTC LAN, movimiento de suelos): aplica solo a trabajos en obra (asistencia, montaje, PEM). Pago a 30 días de la factura; jornada lunes a viernes de 8 a 17 y sábados de 8 a 15. El Anexo 8 es la planilla de movimiento de suelos (no aplica).
- **Anexo 5 (BIM):** requerimientos del modelo 3D (opcional).

## Lo que falta (verificado contra la lista de la RI §4)
**No vino, pero lo tenemos de la COT26-0010-001 (mismo proyecto, en `../COT26-0010-001_AESA_C5297_FILTROS_GAS/pedido/ANEXO 2- Especificaciones de YPF/`):** ED(EP)-B-01.00, B-02.00 y B-05.00, B0606, B0609, N0100.

**No vino y no lo tenemos:**
1. ED(EP)-C-02.00 Elementos internos de recipientes (AB-IYO-ED-09-190-01): define los internos (caja de chicanas, soportes de cartuchos).
2. J1800 Válvulas de seguridad (la HD-J1800-01 sí vino), J0301 Manómetros, J0402 Transmisores DP para nivel.
3. Eléctricas e instrumentación de campo: J1302 Cajas de conexionado (vino solo la HD), J1304 Alimentación eléctrica, J1400 Instalación en áreas clasificadas, P1100 Cañería de acero, P1102 Bandejas, P1103 Prensacables, P1105 Puesta a tierra.
4. L0100 Diseño de cañerías (texto principal; vinieron solo los típicos .dwg) y A0400 Maquetas virtuales (vinieron solo los anexos I y II).
5. B0608 Protección catódica interior: no aplica (HD: sin protección catódica).
6. Bases de diseño LANor-PCLANOR02-VCD26288-G-BD-003001 (HD nota 8, P&ID): no hacen falta para cotizar, porque la HD nota 24 trae los casos de proceso.

**Datos de proceso y diseño que el cliente deja al fabricante:** cantidad y modelo de cartuchos (9 × Ø 141 × 915 mm, a confirmar), caja de chicanas, niveles, altura T/T (HD 4.064 / plano 4.663 / P&ID 4.184) y espesores. Hay que pedir cotización de los internos a un fabricante de elementos (Pall, Gora u otro).

## Resumen del pedido y listas preliminares (25-11-2026, pedido de Matías)
- `resumen_pedido.md` y `listas_preliminares.xlsx`, generados por `listas_preliminares.py` (los datos están en el script; para corregir, editar el script y volver a correrlo). Cantidades por filtro y total ×2.
- Fuente: P&ID hoja 2 (FC-301; FC-302 igual con sus tags), HD, plano PL-001 (tabla de LDM y lista de conexiones transcriptas literal) y clases L0200 CE32, CK11, CK31, CA11. Lo que falta lo decidió ITT (pedido de Matías: "si falta info, decidimos nosotros con el mejor criterio o por antecedentes"), con TAVAL/37 (FC-231) como modelo; la lista de decisiones está en la §10 del resumen.
- Hallazgos: CK11/CK31 (aguas abajo de PSV y BDV) son de baja temperatura (A333-6, LF2, WPL6, espárragos L7). La tabla del plano no cierra: suma 22.845 kg contra 22.320 kg del total. La caja de chicanas de 800 × 650 mm no pasa por MH 20" ni por M1 32": va en módulos. El plano lista 1 válvula de 10" y el P&ID tiene 3; 3 JB de instrumentos en el plano contra 4 que pide la RI.
- Largos de cañería, accesorios y juntas: estimación ITT sin isométricos. **Falta la revisión independiente del relevamiento del P&ID** (no se hizo).

## Pesos y soldaduras (25-11-2026, pedido de Matías)
- Secciones 11 y 12 del resumen: pesos por renglón (tablas del repo; ≈ 24.954 kg por skid contra 22.320 del plano sin instrumental) y soldaduras por tipo y Ø con pulgadas nominales y equivalentes (piping ≈ 1.240 pulg-eq y recipiente ≈ 1.214 pulg-eq por filtro). Calculado con `herramientas/pesos_soldadura.py` (mismas reglas que `precotizar.py`); el criterio del recipiente está en `soldaduras_recipiente()`.
- De este caso salió el skill `relevar-pedido`.

## Cotización con el cotizador (26-11-2026, pedido de Matías: usar la app y ahorrar tokens, sin auditorías)
- `lista_a_cotizador.py` pasa las listas a `pedido/lista_materiales_plano.csv` (148 renglones por filtro); `precotizar.py` puso precios de catálogo; `completar_cotizacion.py` arma `cotizacion.json`: lo que falta, de la planilla de costo de TAVAL/37 (FC-231, mismo alcance) o en 0 para pedir cotización (29 renglones: baja temperatura A333/LF2/WPL6/L7, thredolets 6000#, orejas PAT, casquete 2", portaplaca y RO, junta 20", O-rings); MO y servicios por rubro de TAVAL/37 (USD 187.388,15 por filtro).
- **Resultado (borrador, sin revisar ni auditar):** costo USD 381.120,66 por filtro, precio USD 502.737,81 por filtro, total USD 1.005.475,62 los 2 (factores 1,35/1,35, contingencia 5 %). Antecedentes: TAVAL/37 USD 529.204,77 (1 filtro, 16 elementos); YPF/27 USD 322.081,64 c/u.
- Plazo 210 días desde OC con la ingeniería aprobada en 1 ciclo.
- Falta: precios de los 29 renglones en 0, posiciones RCP y RDO (repuestos, RI §8) y opcionales, ofertas técnica y económica.

## Pendiente (siguiente paso, cuando Matías lo pida)
- Pedir a AESA lo que falta (punto 1 a 4) o cotizar con criterio propio y aclararlo en la oferta.
- Comparar con YPF/27, TAVAL/37 y AESA/20 y decidir la base del cómputo.
- Armar la transcripción y la lista de materiales desde el P&ID y el plano, y las consultas en el formulario FPI-IG-012.
