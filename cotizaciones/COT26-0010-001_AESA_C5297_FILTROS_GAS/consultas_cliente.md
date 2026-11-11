# Consultas a AESA — COT26-0010-001 (2 filtros de gas de emergencia FCC-707/708, PC-02 LANor, C5297)

**Borrador, no enviar.** Las redacta el cotizador; las manda Matías. Cada consulta es un requisito en `pedido/requisitos.csv` con destino `consulta`. Al recibir la respuesta, anotarla acá con fecha y cambiar el destino del requisito.

Preparadas el 11-11-2026.

## Para enviar al cliente

**C1 — Caudal y presión de operación** (requisitos R027 y R041)
> La hoja de datos 5297-02-0600-IG-EM-HD-001 E0 indica caudal de gas 0,28 MSCMD y presión de operación 5 kg/cm2g; el P&ID 5297-02-0000-IG-PR-PI-014 (hoja 3) indica para FCC-707/708 caudal de diseño 6,15 Sm3/h y presión de operación 4,5 kg/cm2g. ¿Cuáles son el caudal y la presión para dimensionar el elemento filtrante?

**C2 — Documentos de referencia** (requisito R040)
> La hoja de datos cita el P&ID LANor-PCLANOR01-VCD25176-R-PI-003014 y las bases de diseño LANor-PCLANOR01-VCD25176-R-BD-003001 (PC-01); la requisición cita LANor-PCLANOR02-VCD26288-R-PI-003014. ¿Confirman que vale el P&ID 5297-02-0000-IG-PR-PI-014 recibido? No recibimos las bases de diseño.

**C3 — Clase de cañerías CA11: válvulas, tapones y juntas** (requisito R036)
> La nota 11 de la hoja de datos pide las válvulas de venteo y drenaje según la clase CA11 del Anexo I de ES__-0001998 L0200. El documento recibido (versión 1.1) no trae el Anexo I ("está en un archivo distinto"). ¿Nos lo pueden enviar, o indicar para 3/4" clase CA11 el tipo de válvula (esférica, aguja, globo), extremos, material y trim, el tapón y la junta de la tapa de cierre? El drenaje D es bridado W.N. 3/4" #150: ¿la válvula es bridada con brida ciega, o bridada × roscada con tapón?

**C4 — Marca E30 del P&ID** (requisito R042)
> En el P&ID los filtros FCC-707/708 y sus líneas llevan la marca E30; la hoja de datos indica "Aislación / Traceado: NO / NO". ¿Los filtros llevan aislación o traceado? Si llevan, ¿quién los provee y hay que prever soportes de aislación y el esquema de pintura N° 202?

**C5 — Ítems opcionales fuera de la planilla** (requisitos R004, R005, R006, R047 y R048)
> La requisición pide valores opcionales de asistencia técnica (valor diario), viaje al sitio y modelo 3D con atributos; la planilla de cotización solo tiene 3 posiciones (RDO, RCP y FCC). ¿Los opcionales se cotizan en la misma planilla o en nota aparte? ¿El modelo 3D en CADWorx es obligatorio para estos filtros (recipiente sin skid ni cañerías) o alcanza con un 3D en formato STEP/DWG?

**C6 — Elemento filtrante e internos** (requisito R028)
> La hoja de datos pide cartucho celulósico con eficiencia 99,9 % > 10 μm y no indica ΔP máximo limpio, dispositivo de cierre ni material de los internos. ¿Hay un ΔP admisible con elemento limpio y sucio? ¿Se acepta tapa de cierre con brida ciega abulonada y pescante (como indica la tabla de conexiones) e internos de acero al carbono con bulonería AISI 316 L?

**C7 — Especificación ED(EP)-C-01.08 Filtros** (requisito R043)
> La ED(EP)-C-01.08 trata filtros de líquido (granate-antracita, cáscara de nuez, arena, cartucho) y pide manómetros, transmisor de presión diferencial y doble válvula de drenaje, que no figuran en la hoja de datos ni en el P&ID de los FCC-707/708. Entendemos que para estos filtros de gas vale la hoja de datos y el P&ID (una válvula y tapón en venteo y drenaje, sin instrumentos). ¿Lo confirman?

**C8 — Placa de identificación** (requisito R038)
> La nota 15 de la hoja de datos pide la placa según PE(EP)-C-01.00.01 y la requisición lista "C0100 - Anexo I - Plano de placa característica"; ninguno de los dos vino en el paquete. ¿Nos los pueden enviar?

**C9 — Lugar de entrega** (requisito R008)
> La requisición incluye el transporte "según sea definido con EL COMPRADOR". ¿La entrega es en nuestra planta de Quilmes (EXW) o puesto en obra en La Angostura Norte? Cotizamos EXW y el flete como ítem separado.

**C10 — Recubrimiento interior** (requisito R045)
> La requisición lista la B0609 (selección de materiales y recubrimiento interior) y la hoja de datos no pide revestimiento interior. Entendemos que los filtros no llevan revestimiento interior (gas, 3,2 mm de sobreespesor de corrosión). ¿Lo confirman?

## Para resolver adentro (Matías)

- **Fecha de cierre y contacto de AESA:** el mail del pedido no vino en el zip (solo los adjuntos). Falta la fecha límite de la oferta y el nombre del comprador.
- **Documentos que hay que entregar con la oferta** (RI punto 8, columna A): hoja de datos completada, **plano de arreglo general**, **memoria de cálculo mecánico**, procedimiento de pintura, PIE, certificado ISO 9001, listas de desvíos, antecedentes, repuestos y proveedores. Los hace Ingeniería: avisar ya. La RI dice que sin esa documentación la oferta puede ser rechazada.
- **Antecedente AESA/47 (25-03-2026, mismos tags para la PC-01, C5165):** se cotizó USD 5.963,65 c/u (presupuesto 142), sin planilla de costo ni resultado cargado. ¿Se ganó? ¿Hay plano o planilla de ese diseño (Ø del cuerpo, cartucho)? Con eso se reemplaza el diseño preliminar de la lista de materiales.
