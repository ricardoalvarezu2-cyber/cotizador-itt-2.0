---
name: "cotizar-skids-equipos"
description: "Armar o revisar la planilla de cotización de skids/equipos de piping (YPF y otros) desde planos, cotizaciones de proveedores y piping class, hasta la planilla final verificada."
---

# Cotizar skids / equipos de piping (planilla completa)

Usar cuando Ricardo pasa una planilla de cotización de skids o equipos (hojas por SAP o por equipo, Resumen, Pie de Venta, DISEÑO) junto con planos (procesos / P&ID, conjunto de cañerías, estructuras) y quiere la planilla final verificada: materiales, precios de proveedores, pintura, soldaduras, END, válvulas TAVAL y control para la dirección.

Responder en castellano rioplatense, conciso. Trabajar siempre sobre una copia y entregar revisiones numeradas (`<nombre>_rev1.xlsx`, `rev2`...). Si Ricardo sube una planilla con cambios suyos, partir de ESA (comparar contra la última rev para ver qué tocó y conservarlo).

## 0. Antes de empezar

- Leer la skill `xlsx` (recalc.py) y, si hay que cotizar válvulas TAVAL, la skill `cotizar-valvulas-taval`.
- Confirmar o tomar estos parámetros (dejarlos como celdas de entrada amarillas/azules, nunca fijos en fórmulas):
  - Soldadura: **USD 22 por pulgada-diámetro** (valor estándar definido por Ricardo).
  - MO estructura: **USD 2/kg**; material perfilería según cotización (Provemet) y chapas/rejilla USD 2/kg si no hay cotización.
  - Granallado y pintura: **USD 50/m2** (valor interno, sin overspray adicional).
  - END: % de RX según la clase de cañería (L0200 punto 5.4; CE22 = 30 %), rendimiento **40 juntas radiografiadas por día**, LP 1 jornada por equipo, tipo de cambio BNA vendedor.
  - Transporte: va a costo (factor 1).
  - Plazo de entrega: el que indique Ricardo (último: 150 días desde aprobación de documentación).
  - Válvulas TAVAL: 1er descuento 35 % (a confirmar) y 2do descuento el que indique Ricardo (último: 20 %).
- Leer todos los archivos con herramientas de archivo; PDFs de planos: `pdftotext -layout` + rasterizar con `pdftoppm -r 220` y recortar el cómputo de materiales (tabla arriba a la derecha) para leerlo como imagen. Los planos de estructura pueden venir rotados 180°.

## 1. Verificar listas de materiales contra planos (por SAP)

Comparar cada fila de la planilla con el cómputo del plano de cañerías y el de estructuras:
- Cantidades, diámetros, schedule, material, rating, descripción. Corregir la descripción al texto del plano y completar lo que el plano deja en blanco (material, SCH, spec de juntas) indicándolo en una columna **Aclaración**.
- Errores típicos encontrados: fórmulas que multiplican por un número fijo en vez de la cantidad; subtotales que no incluyen filas nuevas; instrumentos TI/PI con descripción cruzada; ítems que no figuran en P&ID (poner cant. 0 y aclarar); doble conteo de MO de terceros o repuestos dentro de "Materiales"; montaje no sumado en un SAP y sí en otro; fórmulas de matriz que solo toman una celda; precios de válvulas cruzados entre ítems.
- Faltantes del propio plano: juntas y espárragos de bridas SW 1½" de termovainas (4 espárragos por brida), etc. Agregarlos marcados en verde con su aclaración.
- Repuestos (PEM y 2 años): 10 % de bulonería y juntas de cada SAP, redondeo hacia arriba, con precios vinculados a la lista de piping.
- Estructura: peso total del plano de estructuras (no el estimado). Mantener +20 % de desperdicio sobre perfilería/chapas/rejilla, no sobre pintura.
- Al insertar filas con openpyxl, desplazar a mano todas las referencias de fórmulas (openpyxl no lo hace) y revisar subtotales.

## 2. Hoja "Pintura m2"

Por SAP: piping (caño = π·OD·L; tees = π·OD·(2C) + ramal π·OD_b·M según ASME B16.9; bridas WN/ciegas por unidad: cara posterior + canto + cuello, sin cara RF; global de accesorios menores) y estructura (metros de cada perfil × m2/m de tabla: UPN 100 0,372; 180 0,611; 200 0,661; 240 0,775; chapas ambas caras). Excluir válvulas (vienen pintadas), bulonería zincada y rejilla galvanizada. Las hojas SAP toman ROUNDUP de los m2 × USD 50.

## 3. Hoja "Soldaduras"

Por SAP y por diámetro: juntas a tope = (extremos BW de accesorios y bridas + 2 × tramos de caño) / 2 (tramos estimados del plano de conjunto, celdas azules editables); olets (sockolet a caño, por diámetro de ramal); socket weld (sockolet-niple, niple-brida SW). Pulgadas-diámetro × USD 22/pulg (celda de entrada). Sumar MO estructura (kg × USD/kg). La MO de terceros de cada hoja SAP se vincula a esta hoja.

## 4. Hoja "END"

Con la cotización de ENSAYOS (ITT, en pesos): servicio RX y LP por jornada, placas (2"-6" 3 cortas; 8"-12" 3 largas; 14"-18" 4 largas). Juntas a radiografiar = ROUNDUP(juntas BW × % RX) por diámetro; jornadas RX = ROUNDUP(juntas / 40). Convertir a USD con TC de entrada. Vincular la línea "Rx y LP" de cada SAP. Confirmar con ITT si el servicio es por jornada.

## 5. Hoja "Precios proveedores" (comparativo)

- Una columna por proveedor (Provemet, Bripetrol, Oil Metal, Delgado, Miyashiro, listas Renard y Cintolo...), precio anterior, precio adoptado = MIN, ahorro, proveedor elegido, cotización utilizada (N° y fecha), observaciones. Las hojas SAP toman precio (F), proveedor (I) y cotización (J) por fórmula.
- Regla: **se toma el precio más bajo**, pero solo si el material cumple la presión de la clase: se aceptan alternativas de **igual o mayor espesor** (p. ej. SCH 80 en lugar de SCH 60, sin costura en lugar de con costura) y **nunca de menor espesor**. Espárragos más largos sí; más cortos no. Actualizar la descripción en la hoja SAP y explicar el cambio en Aclaración.
- Precios netos de bonificación por ítem; no aplicar descuentos por adjudicación total.
- Las listas viejas (Renard, Cintolo) suelen ser el origen de los "precios anteriores": usarlas como respaldo y marcarlas para confirmar vigencia.
- Perfiles: USD/m de la cotización ÷ kg/m; el costo medio USD/kg de la estructura va a la hoja SAP.
- Anotar la vigencia de las cotizaciones que informe Ricardo.

## 6. Hoja "Verif. espesores" (ASME B31.3 304.1.2)

Presión = rating de la clase a 38 °C (hoja DISEÑO / L0200); S = 137,9 MPa (A106 B / API 5L B / A234 WPB); E = 1 sin costura; W = 1; Y = 0,4; c = sobreespesor de la clase (CE22 = 3,2 mm) + profundidad de rosca NPT (½"-¾" 1,45 mm; 1½" 1,77 mm); tolerancia -12,5 %. t = P·D/(2(SEW+PY)); nominal mín = (t + c)/(1-0,125). Verificar cada diámetro/schedule de caños, accesorios y niples, y alternativas baratas. Lo que NO CUMPLE se corrige (p. ej. 16" STD → XS; tee red. 16x12 → XS x XS; niples roscados ½"-¾" → XXS; niples entre sockolet SW y brida SW → extremos planos PE). Bridas/válvulas clase 300 A105 (51,1 bar a 38 °C) se informan como cumplen. Si no hay precio para lo corregido, estimar con criterio explícito (p. ej. Std × 1,20) y marcarlo a confirmar.

## 7. Válvulas TAVAL

Correr la skill `cotizar-valvulas-taval` con las válvulas de cada SAP (cantidades = por skid × cantidad de skids), descuentos indicados, stock en DRILL STOCK (si la variante exacta no tiene stock, ofrecer la equivalente en stock y aclararlo; repartir el stock entre SAPs y dar plazo mixto). Comparar los precios con los de la hoja SAP y avisar diferencias; actualizar la planilla si Ricardo lo pide.

## 8. Hoja "Precios a confirmar"

Único lugar de carga: ítem, dónde se usa (SAP/fila), cantidad, precio provisorio y origen, motivo, columnas amarillas **PRECIO CONFIRMADO / Proveedor / N° cotización**, precio vigente = SI(confirmado; confirmado; provisorio), diferencia y estado PENDIENTE/CONFIRMADO, contador de pendientes y total del pedido. Incluir: precios estimados, ítems sin cotización, listas viejas, sockolets sin run confirmado, instrumentos, chapas, rejilla (por m2). En el comparativo guardar el precio de cotizaciones en columnas ocultas para evitar referencias circulares. Pintar en amarillo con formato condicional (que desaparece al confirmar) las celdas de precio en hojas SAP, Verificación y comparativo. Probar la propagación cargando un precio de prueba en una copia y luego borrarlo.

## 9. Hoja "Verificación" (para la dirección)

Por SAP y por rubro, todo vinculado a las hojas SAP, con precio, subtotal, proveedor y cotización: 1 caños; 2 bridas; 3 accesorios soldables; 4 accesorios roscados; 5 juntas; 6 espárragos y tuercas (+ bulonería de estructura); 7 instrumentación; 8 válvulas; 9 pintura m2; 10 perfilería (metros por perfil, posiciones del plano); 11 chapas; 12 rejillas; desperdicio 20 %; 13 soldadura y MO estructura. Resumen por rubro y **controles contra la hoja SAP que deben dar 0** (piping, estructura + pintura, válvulas, instrumentos, MO de terceros).

## 10. Resumen y Pie de Venta

La hoja Resumen toma todo de las hojas SAP (sin valores fijos): costo, factor, precio de venta por línea = precio × cantidad, totales, costo total = Σ costo unitario × cantidad de cada SAP, margen total y fila de control contra Pie de Venta (= 0). Unificar plazo de entrega en Resumen y hojas SAP. Hoja DISEÑO: datos de la clase de cañería (L0200), % RX, PWHT por espesor (> 19,05 mm), anillo espaciador en SW.

## 11. Cierre (siempre)

- recalc.py: 0 errores. Todos los controles en 0. Total de Resumen = Pie de Venta.
- Entregar el archivo con SendUserFile y responder breve: total del pedido antes → después, qué cambió y por qué, lo que queda a confirmar (cotizaciones faltantes, desvíos a declarar a YPF, supuestos a confirmar con proveedores/ITT).
- Marcar celdas cambiadas (amarillo claro), agregadas (verde) y precios a confirmar (amarillo); explicar desvíos en la columna Aclaración.