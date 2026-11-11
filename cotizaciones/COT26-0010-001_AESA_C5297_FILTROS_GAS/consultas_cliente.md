# Consultas a AESA — COT26-0010-001 (2 filtros de gas de emergencia FCC-707/708, PC-02 LANor, C5297)

**Borrador, no enviar.** Las redacta el cotizador; las manda Matías. Cada consulta es un requisito en `pedido/requisitos.csv` con destino `consulta` (los que dicen "Interna" en la referencia se resuelven adentro de ITT, al final de este archivo). Al recibir la respuesta, anotarla acá con fecha y cambiar el destino del requisito.

Preparadas el 11-11-2026 y corregidas el mismo día con la revisión independiente (C2 reenfocada, C1, C3, C4, C5, C7 y C8 ampliadas, C11 y C12 nuevas).

## Para enviar al cliente

**C1 — Caudal y presión de operación** (requisitos R027 y R041)
> La hoja de datos 5297-02-0600-IG-EM-HD-001 E0 indica caudal de gas 0,28 MSCMD y presión de operación 5 kg/cm2g; el P&ID 5297-02-0000-IG-PR-PI-014 (hoja 3) indica para FCC-707/708 caudal de diseño 6,15 Sm3/h y presión de operación 4,5 kg/cm2g. (0,28 MSCMD son 280 Sm3/d, unos 11,7 Sm3/h: casi el doble.) La hoja de datos da además la densidad del gas a 5,6 y 8,0 kg/cm2g, que no coincide con ninguna de las dos presiones, y su nota 18 dice "valores a confirmar con la provisión de la antorcha". ¿Cuáles son el caudal y la presión para dimensionar el elemento filtrante?

**C2 — Documentos de referencia de la hoja de datos** (requisito R040)
> La hoja de datos cita el P&ID LANor-PCLANOR01-VCD25176-R-PI-003014 y las bases de diseño LANor-PCLANOR01-VCD25176-R-BD-003001 (renglón 5 y notas 1 y 17), que son de la PC-01. El P&ID recibido es LANor-PCLANOR02-VCD26288-R-PI-003014 hoja 3, E0 del 16/10/2026, el que cita la requisición. ¿La referencia de la hoja de datos es un error y vale el de la PC-02? ¿Nos pueden enviar las bases de diseño LANor-PCLANOR02-VCD26288-R-BD-003001?

**C3 — Clase de cañerías CA11: válvulas, tapones y juntas** (requisito R036)
> La nota 11 de la hoja de datos pide las válvulas de venteo y drenaje según la clase CA11 del Anexo I de ES__-0001998 L0200. El documento recibido (versión 1.1) no trae el Anexo I ("está en un archivo distinto") ni el Anexo II (códigos y descripciones de válvulas). ¿Nos lo pueden enviar, o indicar para 3/4" clase CA11 el tipo de válvula (esférica, aguja, globo), extremos, material y trim, el tapón y la junta de la tapa de cierre? El drenaje D es bridado W.N. 3/4" #150: ¿la válvula es bridada con brida ciega, o bridada × roscada con tapón?

**C4 — Marca E30 del P&ID** (requisito R042)
> En el P&ID los filtros FCC-707/708 y sus líneas llevan la marca E30; la hoja de datos indica "Aislación / Traceado: NO / NO". Además, las líneas de los filtros terminan en "-BE" (1"-FG-0706-CA11-BE, 1154 a 1157) y el resto en "-BB", y el P&ID no trae la leyenda de E30. ¿Los filtros llevan aislación o traceado? Si llevan, ¿quién los provee y hay que prever soportes de aislación y el esquema de pintura N° 202?

**C5 — Ítems opcionales fuera de la planilla** (requisitos R004, R005, R006, R047, R048 y R052)
> La requisición pide valores opcionales de asistencia técnica (valor diario), viaje al sitio y modelo 3D con atributos; la planilla de cotización solo tiene 3 posiciones (RDO, RCP y FCC). ¿Los opcionales se cotizan en la misma planilla o en nota aparte? ¿El modelo 3D en CADWorx es obligatorio para estos filtros (recipiente sin skid ni cañerías) o alcanza con un 3D en formato STEP/DWG? En la tabla del punto 8 el modelo 3D (ítem 1.8) figura con "Req. CAF = SI" a 6 semanas, y el punto 2 lo llama costo opcional: ¿es opcional u obligatorio, y qué significa "Req. CAF"?

**C6 — Elemento filtrante e internos** (requisito R028)
> La hoja de datos pide cartucho celulósico con eficiencia 99,9 % > 10 μm y no indica ΔP máximo limpio, dispositivo de cierre ni material de los internos. ¿Hay un ΔP admisible con elemento limpio y sucio? ¿Se acepta tapa de cierre con brida ciega abulonada y pescante (como indica la tabla de conexiones) e internos de acero al carbono con bulonería AISI 316 L?

**C7 — Especificación ED(EP)-C-01.08 Filtros** (requisito R043)
> La ED(EP)-C-01.08 trata filtros de líquido (granate-antracita, cáscara de nuez, arena, cartucho) y pide manómetros, transmisor de presión diferencial y doble válvula de drenaje, que no figuran en la hoja de datos ni en el P&ID de los FCC-707/708. Para cartucho descartable pide también 2 válvulas de alivio, válvula de venteo automática y prueba de funcionamiento con asistencia en sitio. Entendemos que para estos filtros de gas vale la hoja de datos y el P&ID (una válvula y tapón en venteo y drenaje, sin instrumentos ni alivios) y lo declaramos en la lista de desvíos. ¿Lo confirman?

**C8 — Placa de identificación** (requisito R038)
> La nota 15 de la hoja de datos pide la placa según PE(EP)-C-01.00.01 y la requisición lista "C0100 - Anexo I - Plano de placa característica"; ninguno de los dos vino en el paquete (la ED(EP)-C-01.08 cita además el plano PE(EP)-F-0100.01). ¿Nos pueden enviar el que corresponde?

**C9 — Lugar de entrega** (requisito R008)
> La requisición incluye el transporte "según sea definido con EL COMPRADOR". ¿La entrega es en nuestra planta de Quilmes (EXW) o puesto en obra en La Angostura Norte? Cotizamos EXW y el flete como ítem separado.

**C10 — Recubrimiento interior** (requisito R045)
> La requisición lista la B0609 (selección de materiales y recubrimiento interior) y la hoja de datos no pide revestimiento interior. Entendemos que los filtros no llevan revestimiento interior (gas, 3,2 mm de sobreespesor de corrosión). ¿Lo confirman?

**C11 — Especificaciones que faltan e internos** (requisitos R055, R056 y R068)
> No recibimos el cuerpo de la ES__-0002657 B0600 (solo los anexos I, II y V) ni la C0200 Elementos Internos, que la C0100 (5.3.4) declara aplicable; y la requisición lista la AB-IYO-ED-09-180-01 pero recibimos la ES__-0001032 (B0606). ¿Nos las pueden enviar o confirmar cuál vale? Para un filtro de Ø 6" con un cartucho: ¿aplican a los internos el sobreespesor de corrosión de los dos lados y el espesor mínimo de 10 mm de la C0100 5.1.4? ¿Se requiere rompevórtice (C0100 5.1.9) en el drenaje de 3/4"?

**C12 — Ensayos y soldadura** (requisitos R057, R062 y R064)
> La ED(EP)-B-02.00 (9.1.1) pide un testigo de producción por cada procedimiento de soldadura; tal como está redactado alcanza a un recipiente de acero al carbono de 11 mm. ¿Se requiere para estos filtros? La ED(EP)-B-05.00 pide recalificar los procedimientos con registros de más de 5 años: ¿se aceptan nuestros PQR vigentes según ASME IX? La "prueba inicial en el lugar de instalación" de la C0100 5.1.6 b) entendemos que no es alcance del fabricante. ¿Lo confirman?

## Para resolver adentro (Matías)

- **Fecha de cierre y contacto de AESA:** el mail del pedido no vino en el zip (solo los adjuntos). Falta la fecha límite de la oferta y el nombre del comprador.
- **Documentos que hay que entregar con la oferta** (RI punto 8, columna A): hoja de datos completada, **plano de arreglo general**, **memoria de cálculo mecánico**, procedimiento de pintura, PIE, certificado ISO 9001, listas de desvíos, antecedentes, repuestos y proveedores. Los hace Ingeniería: avisar ya. La RI dice que sin esa documentación la oferta puede ser rechazada.
- **Antecedente AESA/47 (25-03-2026, mismos tags para la PC-01, C5165):** se cotizó USD 5.963,65 c/u (presupuesto 142), sin planilla de costo ni resultado cargado. ¿Se ganó? ¿Hay plano o planilla de ese diseño (Ø del cuerpo, cartucho)? Con eso se reemplaza el diseño preliminar de la lista de materiales.
- **Garantía** (R023): los plazos son los de ITT, pero la requisición agrega la reparación a cargo del oferente durante la garantía (el equipo va a Neuquén) y una garantía de proceso (eficiencia y ΔP), que depende del fabricante del cartucho. Lo decide la dirección.
- **Calidad** (RC punto 4): WPS firmados por inspector de soldadura Nivel III y procedimientos de END por Nivel III. Si ITT no los tiene propios, es un costo de terceros.
- **Condiciones de obra** (Anexo 4, recibidas el 11-11-2026 y leídas): son el pliego de subcontratación de obras de la PC-01 (movimiento de suelos). A los filtros les toca solo en la asistencia técnica en obra (ingreso por SRC, exámenes, ART, seguro de vida, programa de seguridad) y, por las Condiciones Generales de Compras de AESA (Anexo 13): pago a 30 días de la factura, precios fijos, multa del 2% por semana de atraso con tope del 10%, y desvíos comerciales en el formulario del Anexo 15. A decidir por la dirección: condición de pago y si se declaran como excepción la multa y las cauciones del 10% (R069 a R075).
