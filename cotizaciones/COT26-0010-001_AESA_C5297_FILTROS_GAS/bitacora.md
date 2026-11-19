# Bitácora COT26-0010-001 · AESA (YPF) · C5297 PC-02 LANor · 2 filtros de gas de emergencia FCC-707/708

**Estado: borrador, sin revisar.** Empezada el 11-11-2026 con el alcance y la lista de materiales (pedido de Matías). Precios cargados el 18-11-2026, corregidos con la revisión independiente y ajustados con su auditoría (19-11-2026): **pos 1 RDO USD 1.019,88 el lote, pos 2 RCP USD 509,94 el lote, pos 3 FCC USD 7.128,64 por filtro (14.257,28 los 2); total del pedido USD 15.787,10** (`armar_cotizacion.py` y `posiciones_oferta.md`; borrador, sin revisar). Las versiones anteriores (11.238,38 y 18.396,26) quedan superadas.

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

## Lista de materiales (`pedido/lista_materiales_plano.csv`, 33 renglones, por filtro)
El cliente no da lista ni dimensiones: las define el fabricante (HD notas 2, 4, 8, 9 y 10). La lista es **diseño preliminar de ITT**, a reemplazar por el de Ingeniería:
- Cuerpo de caño 6" Sch 80 SA-106 Gr. B (10,97 mm; C0100 5.1.3 pide 3 mm resistente + 3,2 de corrosión = 6,2 mm con el recipiente terminado), casquete semielíptico 6" Sch 80 SA-234 WPB abajo, brida W.N. 6" #150 y brida ciega con pescante arriba. Largo T/T ≈ 600 mm.
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

## Ensayos, pintura y embalaje que pesan en el costo (de las especificaciones de YPF)
- Líquidos penetrantes 100% en las 4 conexiones (2" y menores) y en las orejas de izaje; no hay ultrasonido. RX por puntos: 2 placas por filtro. Dureza (5 por procedimiento) e identificación positiva del 10 % de los componentes.
- PH con YPF presente, registro gráfico y 1 hora. Raíz GTAW (el cuerpo de 6" no se suelda de adentro); GMAW no admitido.
- Pintura sistema 201: SSPC-SP10, cinc silicato + mist coat + epoxi + poliuretano (200–320 μm), marcas Carboline, Hempel, International, PPG o Sherwin Williams; se pinta después de las pruebas.
- Embalaje para 12 meses a la intemperie; repuestos en bulto aparte.
- Plazo: no se fabrica hasta aprobar la ingeniería; el cliente tiene 10 días hábiles por revisión.

## Revisión independiente (11-11-2026, agente que no armó la lista)
Sin críticos; transcripción, columna A de documentos de la oferta, espárragos y Sch 160 comprobados. Corregido:
- **Error mío:** leí mal el espesor mínimo de C0100 5.1.3 ("5 mm total"); es el mayor entre 5 mm y resistente + corrosión = 6,2 mm. El Sch 40 pasaba por 0,02 mm: cuerpo, casquete y brida pasan a Sch 80.
- **Error mío:** 1 oreja de puesta a tierra; C0100 5.1.13 pide 2.
- **Regla de descripción literal:** espárragos y tuercas separados como en la HD (pos 7/31 y 17/32); materiales que la HD no da (pescante, cupla, tapón, niple) pasados a `nota`; válvulas y tapones con el texto de la RI y la HD.
- Agregados: 2ª junta de tapa (prueba y servicio), rompevórtice (pos 33, a consultar), conducto interno de B al asiento, 20 requisitos (plazo, END, pintura, embalaje, condiciones de sitio), consultas C11 y C12, y C2 reenfocada.
- Impacto a −10 °C: el revisor entiende que no se exige (UCS-66), pero lo dijo de memoria: lo tiene que justificar la memoria de cálculo.
- No revisado: BIM, B0609.
- **Condiciones de obra (recibidas de Matías el 11-11-2026):** pliego de subcontratación de obras de la PC-01 con 14 anexos; leído el documento principal y las Condiciones Generales de Compras (Anexo 13). Para los filtros: pago a 30 días, precios fijos, multa 2% por semana (tope 10%), garantía de 1 año desde la entrega, excepciones en el Anexo 15; requisitos de ingreso a obra para la asistencia técnica. Los demás anexos (movimiento de suelos, división de responsabilidades, planilla de cotización de obra) no aplican. Sin leer en detalle: Anexos 06, 07, 12 y 14 (seguridad e ingreso), que hacen falta solo si se vende la asistencia en obra.

## Predimensionamiento ASME VIII Div.1 (11-11-2026, pedido de Matías) — `dimensionamiento.md`
- Lo genera `dimensionamiento.py` (fórmulas UG-27, UG-32, UG-45, UG-34, UG-44, UG-99 y pesos de las tablas de `conocimiento/tecnico/`). **No es la memoria de cálculo.** Tensiones admisibles, junta y rating de B16.5 cargados de memoria (ASME no está en el repositorio): los verifica Ingeniería.
- Resultado: Sch 80 en cuerpo y casquete y Sch 160 en cuellos cumplen; manda el mínimo de C0100 (6,2 mm), no la presión. Brida ciega estándar con 3,2 mm de corrosión: en el límite, depende de la junta (a verificar). PH 13,0 kg/cm2g declarando MAWP = presión de diseño.
- Peso vacío ≈ 102 kg por filtro; ≈ 114 kg en prueba hidráulica; volumen 12,9 litros.
- Revisión independiente del cálculo hecha: números reproducidos; corregido el casquete (102 mm para Sch 80, no 89), el "no cumple" de la brida ciega (no contaba el resalte y dependía de supuestos), la opción de mover el venteo (no resolvía nada), la superficie a pintar y pesos menores.
- Supuestos míos sin respaldo del cliente: largo del caño 600 mm, altura de A y B, patas de ángulo 2". Dependen del cartucho.
- B31.3: aplica solo al venteo y drenaje aguas abajo de la primera rosca o brida (confirmado por Matías, 11-11-2026); aclaración en la oferta.

## Diseño preliminar completo (11-11-2026, pedido de Matías: "diseñalo con los estándares que conozcas o puedas investigar")
- `dimensionamiento.md` §5 a §9 y plano `arreglo_general.svg` / `.png` (los genera `dimensionamiento.py`).
- **Proceso:** caudal real 2,51 m3/h (con el caudal mayor, el de la HD); 2,07 m/s en las conexiones de 1". Un cartucho plisado estándar de 2 3/4" × 10" trabaja muy holgado; el Ø 6" sale de la tapa con pescante, no del proceso.
- **Arreglo interno:** entrada A a la cámara, flujo de afuera hacia adentro, salida por tubo central a B; cámara inferior de 250 mm y drenaje. Internos en AISI 316 L (decisión mía): la C0100 5.1.4 hace inviable un tubo interno de 1" en acero al carbono (10 mm mínimo y corrosión de los dos lados). Agrega un procedimiento de soldadura carbono–inoxidable.
- **Venteo F corrido 65 mm del centro de la tapa**, porque el pescante toma la tapa del centro; la HD lo dibuja centrado.
- **Patas, anclaje, izaje y pescante** verificados con cuentas simples (viento CIRSOC 102 simplificado, sismo con coeficiente 0,15 adoptado): todo muy por debajo de lo admisible. 3 pernos M16.
- Investigado en la web: criterio de pérdida de carga de fabricantes de filtros de gas (≈ 2 psi limpio, recambio 12–15 psi) y medidas de cartuchos; no encontré una hoja técnica de cartucho celulósico de 10 μm para gas con caudal garantizado: lo tiene que dar Gora u otro fabricante.
- Lista de materiales actualizada: 1 cartucho, internos 316 L, placas de refuerzo del caño del cuerpo, pescante detallado.

## Revisión independiente del diseño (11-11-2026, agente que no lo armó)
Sin críticos; las cuentas de proceso y de soportes se reprodujeron. Corregido:
- **Orejas de izaje:** como las había puesto (80 × 60 debajo de la brida) el grillete chocaba con la brida de Ø 280. Pasan a 120 × 80 con el agujero a 170 mm del eje.
- **Placas de refuerzo de las patas:** arrancaban sobre la soldadura casquete–caño (C0100 5.3.2 no lo permite); suben 50 mm y la pata pasa a 550 mm. "Cortadas del mismo caño" no asentaba ni coincidía con el peso: quedan en SA-516 Gr. 70 de 6,35 mm roladas.
- **Venteo F:** a 65 mm del centro el agujero caía sobre la cara de la brida; queda a 50 mm.
- **Cartucho:** el plisado estándar trae núcleo de polipropileno (no sirve a 65–90 °C): se pide con núcleo y tapas metálicos. Ø 63 a 70 mm.
- **Condensado:** yo había tratado el gas como seco con polvo; con 7,6 % de C5+ puede condensar. Sumado a la consulta C1.
- **Fórmulas de las patas:** compresión en el círculo de patas (no el de anclaje), flexión en ménsula sobre el eje débil y K = 2: 30,9 MPa y esbeltez 81, siguen cumpliendo.
- Contradicciones entre secciones (altura de A y B 770 contra 600, agujero Ø 18 contra 22, internos de 10 mm contra 316 L) y cita 5.1.1 por 5.1.7.
- Plano: vista en planta con la orientación, cota de altura total al pescante (1.407 mm), oreja y placas de refuerzo dibujadas.
- Queda dicho de memoria por el revisor y por mí: medidas de B16.x, factores de CIRSOC, propiedades del ángulo, límite de temperatura del cartucho y presiones de vapor.

## PDF para Matías (11-11-2026)
`FCC-707-708_diseno_preliminar.pdf` (4 hojas A4 apaisadas): plano de arreglo general con planta, pesos por filtro y lista de materiales. Se rehace con `python dimensionamiento.py && python pdf_resumen.py` y se imprime `resumen_diseno.html` a PDF con Chromium (Playwright, A4 apaisado). No calcula nada: lee el plano, la sección 4 de `dimensionamiento.md` y `pedido/lista_materiales_plano.csv`.

## Antecedentes
- **AESA/47 - Filtros La Angostura Norte C5165** (25-03-2026): los mismos tags FCC-707/708 para la PC-01 (HD-003019 / RI-003017 de VCD25176). Presupuesto 142: USD 5.963,65 c/u, 75 días, sin planilla de costo ni resultado. Gora OF-X-0001-00027549 (23-03-2026): cartucho microfibra de vidrio doble malla 25 μm, Ø ext. 42 × 86 mm, USD 32 c/u, 6 unidades, mínimo 2 por recipiente. **Diferencia:** hoy la HD pide celulósico 99,9 % > 10 μm.
- Otros del buscador: Camuzzi 26 (FM2 #600), Camuzzi 24 (FM3 #600): otra serie y otro tipo.

## Pendientes
- Respuestas a las consultas C1–C12; fecha de cierre y comprador.
- Segunda lectura (`transcripcion_b.json`).
- Diseño de Ingeniería (Ø, largo, internos, patas) y cotización del cartucho.
- Precotización, `cotizacion.json`, repuestos RCP y RDO, opcionales, plazo.

## Aislación y traceado (18-11-2026)
- Matías confirmó con la hoja de datos (HD-001 E0, renglón 26: "Aislación / Traceado: NO / NO") que los filtros **no llevan aislación ni traceado**. La consulta C4 (marca E30 del P&ID) queda resuelta y no se envía; se cotiza con pintura sistema 201 (sin aislación).
- El antecedente AESA/47 (presupuesto 142, 25-03-2026, USD 5.963,65 c/u) no detalla el alcance ("según documentación recibida": HD-003019 y RI-003017 del PC-01, que no están en el repositorio): no se puede saber si incluía aislación o traceado.

## Precios y armado (18-11-2026, pedido de Matías)

**Resultado (`armar_cotizacion.py`, borrador sin revisar):** costo USD 4.223,32 por filtro, precio USD 5.619,19 por filtro (factores 1,35 / 1,35, contingencia 5 %), total USD 11.238,38 los 2, EXW Quilmes, plazo 95 días. Python y planilla iguales; `verificar_computo.py` sin errores (117 avisos, revisados por tipo: similares, estimados y listas de más de 6 meses).

### Doble lectura
- Lectura B hecha por otro agente en una sesión aparte (`session_01Y6ZcPhKAHdv6wZJ9ojKCW6`, rama `claude/aesa-c5297-lectura-b`), con la instrucción de no abrir `transcripcion.json` ni la lista; se le dieron los títulos y columnas de las tablas, no su contenido.
- `frenos.py --comparar`: 13 diferencias. Resueltas mirando el original (anotadas en `diferencias_resueltas`):
  - Planilla: diferencia aparente, el comparador emparejaba por Cesta (igual en las 3 filas). Se pasó Posición a la primera columna en A y B; coinciden.
  - **RI punto 2: la lectura A había omitido 4 viñetas** (Diseño ASME…, Documentos del punto 8, Repuestos según IG.AR 40.00.140, Lista de desviaciones). Vale B. Los 4 ya estaban en `requisitos.csv` (R007, R019, R024, R022).
  - **C0100 5.1.9: A lo había copiado en dos fragmentos**; vale la frase completa de B.
- Después de resolver, las dos lecturas quedan iguales (el aviso "idénticas" es por eso).

### Antecedentes (`buscar_antecedentes.py`)
- YPF/22 y TAVAL/4 (filtros de agua FCC936/937, otra escala), **AESA/47** (mismos tags PC-01, USD 5.963,65 c/u, sin planilla), TECPETROL/11, Sacde/9, CAMUZZI/28, **YPF/26** (FCC707708 PC C5064, 18-06-2025, OE 376-25: USD 6.890,14 c/u + RDO 30 + RCP 87,60 por equipo, sin planilla), CAMUZZI/26 (FM2).
- Modelo de costo: **TAVAL/40 Inarteco** (planilla de costo de filtros FM2/FM3 de taller, 15-01-2026; caso de control CTRL-F01): USD 16 por pulgada, 45 h de montaje × 13 USD/h para el FM3 de 6" (incluye PH con armado y desarme), horas de ingeniería y calidad (4,5 h/u, para un FM estándar).

### Criterios adoptados (a revisar)
- Soldaduras a presión junta por junta: 39,52 pulg-eq por filtro × USD 16 (2 a tope 6" Sch 80, 2 a tope y 2 injertos 1" Sch 160, 3 a tope y 1 injerto 3/4" Sch 160, media cupla en la brida ciega, 2 de internos 316 L). Los filetes de patas, orejas y pescante van en las horas de montaje.
- Ingeniería 30 h y calidad 20 h por filtro (USD 15/h): **criterio mío**, entre el FM estándar (4,5 h/u) y los coalescedores YPF (250 h/u). Lo tiene que confirmar Matías.
- RX: 1 visita (ARS 850.000) y 2 placas por filtro, del proveedor confirmado por Matías el 30-10-2026; LP y dureza: 1 servicio de NDT Antonelli para el lote (0,5 por filtro). PMI y procedimiento carbono–inoxidable SIN PRECIO.
- Pintura: 1,40 m² (1,17 + 20 %) × USD 50 (Ricardo Álvarez, 16-11-2026). Puede haber un mínimo del pintor.
- Bridas WN 1" y 3/4" Sch 160: no hay precio; estimadas con la Sch 40 de Renard × 1,32 (relación Sch 160/Sch 40 de la misma lista en 3").
- Válvula de drenaje (pos 14): esférica 1" #150 bridada RF antifuego (código L0200 TCH1R, clase CE12) de Taval en TAVAL/5 (USD 170,63, 05-06-2025) como referencia conservadora; venteo (pos 20): esférica 3/4" NPT #3000 Taval lista 30 (USD 43,60). Las dos dependen de la clase CA11 (C3). En TAVAL/5 se ve que las esféricas CA11 de YPF son #150 bridadas RF paso total, antiestáticas y antifuego (código TCJ1R).
- Cartucho (pos 22): USD 32 estimado con la cotización Gora del antecedente AESA/47 (microfibra 25 μm Ø 42 × 86); el pedido es celulósico 10 μm Ø 63–70 × 254 con núcleo metálico. Pedir a Gora.
- Repuestos (por filtro, renglones RCP y RDO): RCP = 1 cartucho + 1 junta de tapa; RDO = 4 cartuchos + 2 juntas + 1 juego de espárragos y tuercas de la tapa. Propuesta mía (IG.AR 40.00.140 no fija cantidades).
- **El precio por filtro incluye RCP y RDO**: `generar_oferta.py` arma un solo ítem; la separación en las posiciones 1 y 2 de la planilla queda entre corchetes en la oferta económica.
- Opcionales de la RI (asistencia diaria, viaje, 3D): fuera del precio; en la oferta económica con el valor entre corchetes. Referencias de costo: asistencia de puesta en marcha USD 975/día (Tapigar, 06-2026, OTR-00111).
- Plazo 95 días: 21 de ingeniería + 28 de revisión de YPF (1 ciclo) + 31 de taller y despacho = 80, más margen.
- Envolvente y patas: la HD da dos materiales ("SA 516 Gr.70 / SA-106 Gr. B", "SA 516 Gr.70 / SA 36"); se toma caño SA-106 B y ángulo SA 36, declarado como desvío estructurado y en la oferta porque el control de compatibilidad lee solo el primero.
- `fecha_referencia` 31-10-2026: con 18-11-2026 el armado se corta (no hay índice de noviembre; error ya anotado el 16-11-2026).

### Contraste con antecedentes
- AESA/47 (5.963,65 c/u): esta queda un 6 % abajo, dentro del 15 %.
- YPF/26 (6.890,14 c/u, 06-2025): esta queda más de 15 % abajo. Sin planilla ni plano de esa oferta no se puede explicar rubro por rubro; diferencias conocidas: 17 meses, diseño desconocido, y esta incluye RCP y RDO en el precio. Anotado en `justificaciones.antecedentes`.
- Reparto del costo: 24 % materiales, 76 % MO y servicios (soldadura, montaje, ingeniería, calidad y END pesan más que el material en un filtro de 6").

### Frenos abiertos (`frenos.py`)
- requisitos: 22 consultas sin respuesta (C1–C3, C5–C12 e internas de garantía, pago y cauciones).
- sin_precio: M24 bulonería 316 L, S09 PMI, S10 procedimiento carbono–inoxidable.
- vencidas: 8 precios de lista de más de 180 días (Renard 12-2025, Taval lista 30).
- pendientes_oferta: 11 datos entre corchetes (PRES, contacto, condición de pago, multas, opcionales, separación RCP/RDO, garantía de proceso).
- Estimado sin fuente: 30 % del costo directo (justificado en `justificaciones.estimado`).

### Errores y cambios de herramientas en esta sesión (anotados en `conocimiento/errores_y_lecciones.md`)
- `lista_compras.py` se cortaba (variable usada antes de asignarla) con una fila de la transcripción sin ítem: corregido.
- `verificar_computo.py` suponía que la posición de la lista es la primera columna de la transcripción; con una lista de diseño ITT se cortaba. Nuevo control para `origen_lista.tipo = diseno_itt` (descripción y material tal cual en el documento) y 2 casos en `test_errores_sembrados.py`.
- `ficha_rubros.peso_equipo` lee "0,60 kg" como 60 kg (coma decimal): el peso daba 697 kg por filtro. Saqué los kg de las especificaciones; queda pendiente corregir la herramienta (y `web/src/ficha.js`).
- Reescribí `requisitos.csv` con `csv.writer` y cambió las comillas de todo el archivo (lección del 29-10-2026): rehecho campo por campo.

### Pendiente
- **Revisión independiente** del cómputo contra la HD y del cambio en `verificar_computo.py` (no hecha en esta sesión).
- Lista para Compras (`compras/COT26-0010-001_pedido_materiales_compras.xlsx`): cartucho Gora, bridas y caño Sch 160, válvulas CA11, PMI/LP/dureza, bulonería 316 L.

## Correcciones de la revisión independiente (18-11-2026)

La revisión (otro agente) encontró 2 errores graves y varios medios. Corregido y vuelto a armar:
1. **GRAVE: RCP y RDO estaban dentro del precio por filtro.** La planilla del cliente tiene 3 posiciones y la RI pide listado detallado con precios unitarios (R021: no se admiten precios globales). Ahora la oferta económica tiene 3 ítems (3 FCC × 2, 2 RCP lote, 1 RDO lote) y un listado por repuesto con cantidad y unitario. Herramienta nueva `herramientas/posiciones_oferta.py` (la llama `generar_oferta.py`): vende cada renglón con el mismo cálculo que la planilla y controla que la suma dé el total de la planilla (dio igual: 18.396,26). Siembra nueva en `test_errores_sembrados.py` (un renglón en dos posiciones frena). R021 pasa a `renglon` RDO;RCP;MO. **Ojo:** la planilla y el informe muestran el "precio unitario por filtro" con los repuestos adentro (9.198,13); el de la pos 3 sale de `posiciones_oferta.md`. La página todavía no arma ofertas con varias posiciones.
2. **GRAVE: la oferta prometía PMI, procedimientos y bulonería 316 L en 0.** Costeados: PMI 1 visita para el lote (estimado a la tarifa de servicio de END de NDT Antonelli, USD 490; su lista no trae PMI); 4 procedimientos firmados por Nivel III a USD 250 (Antonelli 1788-JCA-1125 ítem 14); PQR carbono–inoxidable estimado (8 h de soldador a 61,16 + ensayos a 490, sin referencia de laboratorio); bulonería 316 L ≈ 0,4 kg a 10 USD/kg. (Una primera referencia B8M para la bulonería la rechazó el control de compatibilidad: 316 no reemplaza a 316 L.)
3. Cartucho: a USD 160,70 (Gora, celulosa 5 μm, la referencia más alta de la misma fuente), estimado, con la nota "pedir cotización a Gora con la HD: celulósico 10 μm absoluto Ø 63–70 × 254 con núcleo metálico". Arrastra RCP y RDO.
4. Provemet: validez real 13-11-2026 (15 días desde el 29-10), ya vencida: el freno de vencidas queda abierto. El caño 6" va a USD 77,63/m sin bonificar (el 4 % vale solo por compra total) y Provemet lo cotiza por tira de 12 m: **decidir** si se pide tramo cortado o se compra la tira con sobrante a stock (no agregué la compra extra).
5. Testigo de producción (ED(EP)-B-02.00 9.1.1): **no costeado**; aclaración en la oferta "no incluido, sujeto a la consulta C12".
6. Drenaje: la válvula se supone bridada RF; pos 15 pasa a brida ciega 3/4" #150 y se suman junta (15b), 4 espárragos (15c) y 8 tuercas (15d). Texto de la oferta alineado.
7. Revisión de la oferta unificada en "0"; "Clips SA-516 Gr. 70" de la HD declarado como no aplica (sin aislación ni plataformas).
8. LP en 2 servicios para el lote (pasadas finales interior y exterior, Tabla 2 nota 1); tercera junta de internos (codo – tubo vertical): 41,40 pulg-eq.

**Decisión de Matías pendiente — ingeniería y calidad:** 30 h + 20 h por filtro (USD 750 de costo por filtro) son criterio mío, sin antecedente con el mismo alcance. Riesgo: cada 30 h por filtro de más o de menos mueven ≈ USD 600 el precio por filtro (30 × 15 × 1,35).

**Contraste (pos 3 sin repuestos):** 33 % arriba de AESA/47 y 15 % arriba de YPF/26. Ninguno tiene planilla; lo que esta carga y no se sabe si ellos cargaban está en `justificaciones.antecedentes` (PMI, procedimientos Nivel III, PQR, 2 LP, dureza, horas de ingeniería y calidad, cartucho a la referencia alta).

**Frenos abiertos:** requisitos (22 consultas sin respuesta), vencidas (12: Provemet vencida el 13-11, listas Renard y Taval de más de 180 días), pendientes de la oferta (10 corchetes). El estimado sube al 43 % del costo directo (justificado).

## Ajustes de la auditoría de las correcciones (19-11-2026)

La auditoría confirmó que no hay doble conteo y que las posiciones suman el total. Ajustes hechos:
1. **Planilla e informe ya no dicen que 7.893,55 "va a la oferta":** con posiciones en `oferta.json`, el Resumen y la Planilla ITT rotulan "precio unitario por filtro con repuestos" y la Planilla ITT lista los ítems 1 RDO · 2 RCP · 3 FCC; el informe agrega la sección "Oferta por posiciones" con los 3 ítems. Mismo cambio en la página (`web/src/documentos.js`): `node web/probar_planilla.js` sigue OK en las 8 cotizaciones. Python y planilla siguen iguales (15.787,10).
2. `posiciones_oferta.py` frena si una posición declarada queda sin renglones o en 0 (siembra nueva: "RPC" mal tipeado) y cierra el unitario del ítem principal con el total de la planilla, así la oferta suma exactamente lo mismo (antes difería 0,04 por redondeo).
3. Textos: antecedente AESA/47 sin el cartucho de USD 32; la oferta técnica remite el listado a la económica; posiciones en el orden de la planilla del cliente (1 RDO, 2 RCP, 3 FCC); listados sin "por filtro" ni "(pos 22)"; R064 → PQR;PROC y R046 → CAL;PROC;PQR;PMI; la lista para Compras dice que la PMI la hace ITT.
4. **Criterio (Matías: "arreglá con criterio"), propuesta de ITT:** RDO = 2 cartuchos + 2 juntas de tapa por filtro (un recambio por año, es un filtro de emergencia) y RCP = 1 cartucho + 1 junta por filtro; la oferta aclara que las cantidades se ajustan a la frecuencia de uso que indique el cliente. (YPF/26 vendió RDO 30 y RCP 87,60 por equipo.)
5. LP: 1 servicio para el lote (las pasadas interior y exterior se revisan en la misma visita).
6. Procedimientos Nivel III: 2 de END (RT y PT) a USD 250 (Antonelli ítem 14 es de END); la WPS/PQR la hace ITT (renglón PQR). Supuesto: la WPS que pide la RC firmada por inspector de soldadura Nivel III la firma personal de ITT o se agrega cuando se confirme.
7. PQR: incluye la soldadura de la probeta (8 h); no incluye el material de la probeta ni la calificación de soldadores (WPQ): supuesto, ITT tiene soldadores calificados ASME IX vigentes.
- Se mantienen: cartucho a USD 160,70 como estimado (la referencia es Gora PPTO 27131: papel celulósico 5 μm Ø 115 × 158 mm para FM-3 S-600, otra pieza); PMI 1 visita (podrían ser 2: al recibir el material y en el equipo terminado); bulonería 316 L a 10 USD/kg.

**Contraste (pos 3 sin repuestos, 7.128,64):** 20 % arriba de AESA/47 y 3 % arriba de YPF/26.
