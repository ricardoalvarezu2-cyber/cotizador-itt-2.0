# Bitácora COT26-0010-001 · AESA (YPF) · C5297 PC-02 LANor · 2 filtros de gas de emergencia FCC-707/708

**Estado: borrador, sin revisar. Sin precio todavía.** Empezada el 11-11-2026 con el alcance y la lista de materiales (pedido de Matías).

## Pedido
- Zip "RV: Pedido de Cotización - FILTROS DE GAS - PC LAN2 C5297" (sin el mail): requisición 5297-02-0600-IG-EM-RI-001 E0 (30-10-2026), hoja de datos 5297-02-0600-IG-EM-HD-001 E0, P&ID 5297-02-0000-IG-PR-PI-014, planilla de cotización (cesta 23585543), requisición de calidad RC, especificaciones de YPF (C0100, L0200 sin Anexo I, B0600 anexos, B0606, B0609, ED(EP)-B-01.00 / B-02.00 / B-05.00 / C-01.08, IG.AR 40.00.140), condiciones de obra (.msg) y requerimientos BIM. Todo en `pedido/`.
- Cliente: A - Evangelista S.A. (AESA, código ITT 0010); cliente final YPF, Planta Compresora PC-02 La Angostura Norte, Neuquén.

## Alcance (RI puntos 1 y 2; detalle en `pedido/requisitos.csv`)
- **Planilla:** pos 3 = 2 filtros FCC-707/708; pos 2 = repuestos de precomisionado, comisionado y puesta en marcha (RCP); pos 1 = repuestos para 2 años (RDO). Precios unitarios, no globales.
- **Opcionales de la RI que no están en la planilla:** asistencia técnica (valor diario), viaje al sitio, modelo 3D con atributos (CADWorx).
- **Equipo:** filtro vertical de cartucho, ASME VIII Div.1 sin estampa, diseño 10 kg/cm2g y −10/90 °C, corrosión 3,2 mm, RT3, PH, UT/PT según tabla 2 de ED(EP)-B-02.00, sin NACE, sin aislación. Conexiones: A y B 1" #150 WNRF, D 3/4" #150 WNRF con válvula y tapón, F 3/4" NPT #3000 con válvula y tapón, M tapa de cierre con brida ciega y pescante. Cuellos Sch 160.
- **Incluye:** patas, elementos filtrantes e internos, pescante, junta y bulonería de la tapa, orejas de izaje (2) y de puesta a tierra (AISI 316), válvulas de drenaje y venteo (clase CA11), diseño de pernos de anclaje y plantilla, placa de identificación con soporte, pintura B0600 sistema 201 (RAL 9006 cuerpo, RAL 9011 soportes), ingeniería y data book.
- **Con la oferta hay que entregar:** HD completada, plano de arreglo general, memoria de cálculo, procedimiento de pintura, PIE, ISO 9001, listas de desvíos, antecedentes, repuestos y proveedores.
- **No incluye:** pernos de anclaje (solo diseño y plantilla), contrabridas, juntas y espárragos de A, B y D hacia la cañería, válvulas de bloqueo de 1" del P&ID, instrumentos, montaje.

## Lista de materiales (`pedido/lista_materiales_plano.csv`, 30 renglones, por filtro)
El cliente no da lista ni dimensiones: las define el fabricante (HD notas 2, 4, 8, 9 y 10). La lista es **diseño preliminar de ITT**, a reemplazar por el de Ingeniería:
- Cuerpo de caño 6" Sch 40 SA-106 Gr. B (7,11 mm; C0100 5.1.3 pide 5 mm mínimo total), casquete semielíptico 6" SA-234 WPB abajo, brida W.N. 6" #150 y brida ciega con pescante arriba. Largo T/T ≈ 600 mm.
- Criterio del Ø: el caudal es mínimo (6,15 Sm3/h según el P&ID) y el cartucho del antecedente AESA/47 era de Ø 42 × 86 mm; 6" es el menor Ø con brida ciega manejable y lugar para el asiento del cartucho. Si Ingeniería o el fabricante del cartucho piden otro Ø, cambian las pos 1 a 7.
- Descripción y material de cada renglón: texto literal de la HD; lo que agrega ITT, en `nota`. Cantidades calculadas por ITT salvo las conexiones (tabla de la HD) y las orejas de izaje (nota 14).
- Sin definir: válvulas de drenaje y venteo, tapón del drenaje y junta de la tapa (falta el Anexo I de L0200, clase CA11: consulta C3); cantidad y medida del cartucho (pedir a Gora: celulósico, 99,9 % > 10 μm).

## Diferencias encontradas en los documentos (van en `consultas_cliente.md`)
1. Caudal y presión de operación distintos entre HD (0,28 MSCMD; 5 kg/cm2g) y P&ID (6,15 Sm3/h; 4,5 kg/cm2g).
2. La HD cita documentos de la PC-01 (VCD25176); la RI, de la PC-02 (VCD26288). La HD tiene revisión E0 del 27-02-2026 "para aprobación" y fecha de emisión 30-10-2026.
3. Falta el Anexo I de L0200 (clase CA11), la PE(EP)-C-01.00.01 y el Anexo I de C0100 (placa), y las bases de diseño.
4. El P&ID marca E30 sobre los filtros; la HD dice sin aislación ni traceado.
5. La ED(EP)-C-01.08 es de filtros de líquido y pide instrumentos y doble válvula de drenaje que la HD y el P&ID no tienen.
6. La planilla no tiene posiciones para los opcionales.
7. La planilla cruza las referencias (RDO y RCP citan la HD; FCC cita la RI): sin efecto.

## Antecedentes
- **AESA/47 - Filtros La Angostura Norte C5165** (25-03-2026): los mismos tags FCC-707/708 para la PC-01 (HD-003019 / RI-003017 de VCD25176). Presupuesto 142: USD 5.963,65 c/u, 75 días, sin planilla de costo ni resultado. Gora OF-X-0001-00027549 (23-03-2026): cartucho microfibra de vidrio doble malla 25 μm, Ø ext. 42 × 86 mm, USD 32 c/u, 6 unidades, mínimo 2 por recipiente. **Diferencia:** hoy la HD pide celulósico 99,9 % > 10 μm.
- Otros del buscador: Camuzzi 26 (FM2 #600), Camuzzi 24 (FM3 #600): otra serie y otro tipo.

## Pendientes
- Respuestas a las consultas C1–C10; fecha de cierre y comprador.
- Segunda lectura (`transcripcion_b.json`) y revisión independiente de la lista.
- Diseño de Ingeniería (Ø, largo, internos, patas) y cotización del cartucho.
- Precotización, `cotizacion.json`, repuestos RCP y RDO, opcionales, plazo.
