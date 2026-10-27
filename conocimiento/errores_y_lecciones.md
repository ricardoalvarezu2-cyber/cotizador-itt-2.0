# Errores de cotización y lecciones

Registro de los errores detectados en cotizaciones armadas con el cotizador, con su causa y la regla que se agregó al [procedimiento](procedimiento_cotizacion.md) para que no se repitan. **Una oferta con un error de cómputo o de precio que llega al cliente puede hacer perder plata o la credibilidad de ITT.** Por eso cada error se anota acá, aunque se haya detectado a tiempo.

## COT26-1003-001 · CAPEX OQ8209 · 2 puentes BBO MEC 1500 · 27/10/2026

Se detectaron antes de enviar, gracias a las preguntas de Matías Russo. El primer borrador proponía **USD 7.700 por puente**, después de un cálculo que daba ~9.000. El valor tras la primera revisión fue USD 7.302; después del ajuste por inflación y la revisión independiente, **USD 7.639,86** (con el 63% del costo todavía estimado). Ninguna versión con errores llegó al cliente.

| # | Error | Cómo se detectó | Impacto por puente | Causa | Regla nueva |
|---|---|---|---|---|---|
| 1 | Se tomó la MO de Ledesma a **USD 1.800** (sep-2025), un presupuesto con otro alcance (cuadro CBM con corte de caño). Había uno más reciente para un puente equivalente a **USD 400** (PRES 24879, abr-2026) | Al rastrear la fuente de cada precio para el informe | ~+1.900 en el precio | Se eligió la primera MO encontrada sin comparar alcances | P5 |
| 2 | Bloqueo y purga cotizado a **USD 197,71**: era el precio de un modelo **3/4" 6000 psi**. El plano pide 1/2" 3000 (USD 137) | Al rastrear la fuente | ~+160 | Se buscó el precio por el nombre del artículo, sin comparar la especificación | P4 |
| 3 | Se presentó una retención Danco a **"USD 220"** como opción de ahorro, pero era un **"algo así como 240"** dicho por WhatsApp, sin confirmar y para otro modelo (WOG3000) | Al leer la captura original | Hasta −830 en el precio si se usaba | Se usó un dato de memoria sin volver a la fuente | P4 |
| 4 | Factor **1,40 sobre la MO** de un tercero dentro de un equipo. En la planilla modelo (PRES 24879) la MO de Ledesma dentro del puente iba a 1,35, y el 1,40 era solo para MO vendida sola | Pregunta de Matías: "¿la mano de obra no es un servicio?" | +31 | Se copió la frase del resumen de la ficha sin abrir la planilla original | P6 |
| 5 | Se informó en el chat un precio (**USD 7.275**) calculado aparte, distinto del que mostraban el informe y el Excel (7.287) | Al armar el Excel con fórmulas | 12 | Cuentas hechas a mano fuera de la herramienta de cálculo | P7 |
| 6 | El caño 14 figuraba como **6 m** (media tira de compra) y no como el **1 × 1.900 mm** del plano | Pedido de Matías de comparar la lista con el plano | 0 (era el mismo costo, pero la lista no coincidía con el plano) | Se mezcló la cantidad de compra con la del plano | P2 |
| 7 | Manómetro de stock con conexión **1/4"**. El plano pide **1/2" NPT-H** (en la primera corrección se transcribió mal como NPT-M; lo detectó la revisión independiente) | Comparación columna por columna con el plano | Sin impacto en precio, pero era un incumplimiento | No se comparó la columna de extremos/conexión | P2, P4 |
| 8 | Cupla 23 **NPT/BW** (va soldada sobre los niples): faltaban **2 soldaduras** | Comparación de la columna de extremos | +47 | No se derivaron las soldaduras de los extremos BW | P3 |
| 9 | La retención y la junta monolítica se tomaron de cotizaciones con otra especificación: asiento AISI 410 en lugar de 316, y extremos BW/NPT en lugar de BW/BW | Comparación de la especificación cotizada con la del plano | A confirmar | Igual que el error 2 | P4 |
| 10 | El primer número (~9.000) se mostró antes de compararlo con antecedentes del mismo cliente (6.200 en 2024, ~6.700 en 2026) | Revisión posterior | — | Se presentó el cálculo antes de contrastarlo | P8 |

**Patrón común:** se armó el precio rápido, desde fichas resumidas y de memoria, y **sin volver al documento original ni comparar campo por campo contra el plano**. El procedimiento ahora obliga a hacer las dos cosas, y suma un control automático (`herramientas/verificar_computo.py`) y una revisión independiente antes de dar una oferta por lista.

### Revisión independiente del 27/10/2026 (P9.2)

Un agente que no había armado el cómputo comparó el plano y el pedido contra el cómputo, la planilla y las ofertas, y verificó 8 precios contra sus documentos originales. Encontró errores que la autorrevisión no había visto.

| # | Error | Impacto | Causa | Regla nueva |
|---|---|---|---|---|
| 11 | Plazo de **60 días** cuando las esféricas llegan el día 60 y el taller se había superpuesto desde el día 45. Plazo real: **75 días**. La oferta no decía que no se llegaba a la fecha ni que estaba fuera de término | Incumplimiento de plazo con el cliente | Gantt con tareas superpuestas sin dependencia del material | Lista de control: plazo = llegada del material más largo + taller + dossier, sin superponer |
| 12 | Esféricas: el precio era de una válvula forjada con asiento **PTFE** más un **+30% inventado**, cargado como "cotización". La oferta decía "según pedido" | Precio y especificación sin respaldo en 6 válvulas por puente | Recargo supuesto cargado con tipo `cot` | P4: un recargo supuesto es `est`, y la oferta no afirma cumplimiento sin cotización con la especificación |
| 13 | Retención: la cotización era **TRIM 8** (13Cr), no AISI 316, y sin resorte. El desvío decía "cumple" y la oferta, "trim AISI 316" | El ítem más caro, con riesgo de suba | No se leyó el código de trim del documento original | P4: leer la especificación completa del documento (códigos de trim, asientos, extremos) |
| 14 | Manómetro pos 20 transcripto **NPT-M**; el plano dice **NPT-H** | Especificación errónea en compras y en la oferta | Error de transcripción | P2: la transcripción del plano la revisa otro |
| 15 | Extensible sin sello metal-metal cotizado y con la cotización vencida; junta BW/NPT en vez de BW/BW; buje BSPT en vez de NPT | Desvíos no declarados | Igual que el 13 | P4 |
| 16 | No se costeó la reposición del revestimiento en las 2 juntas soldadas sobre el caño revestido | Costo omitido | No se pensó el proceso de soldar sobre caño revestido | P3: cada soldadura sobre caño revestido lleva reposición del revestimiento |
| 17 | Niples, armado y bloqueo y purga cargados como "cotización", cuando salen de una **planilla interna** (PRES 24879) sin presupuesto del proveedor. El estimado real era ~33% del costo, no 7% | El control de estimados daba una falsa seguridad | Tipo de fuente mal clasificado | P4: `cot` solo con documento del proveedor; una planilla interna de ITT es `ant` o `est` |
| 18 | Cotizaciones de proveedores vencidas (Indave 10 días, Adita 13/04, Duralitte 15 días), mientras la oferta da 15 días a precio firme | Precio desactualizado | No se controló la validez | Lista de control: reconfirmar precios vencidos antes de emitir |
| 19 | Diferencia mayor al 15% con los antecedentes (6.200 en 2024; APSA/15 sin BOP ~5.100) sin explicar rubro por rubro | No cumple P8 | Se presentó el número sin el análisis | P8 (ya existía): ahora se controla en la revisión |

**Lección:** la autorrevisión no alcanza. La revisión independiente encontró 3 problemas críticos en una cotización que ya se había revisado contra el plano. Hay que hacerla siempre, y antes de mostrar un número como definitivo.


### Revisión del catálogo de materiales (27/10/2026)

Al revisar el catálogo antes de agregar la marca aparecieron errores de lectura de las fuentes. Ninguno llegó a una cotización, pero cualquiera podía dar un precio equivocado.

| # | Error | Causa | Corrección |
|---|---|---|---|
| 20 | "½", "¾" y "¼" se leían como 12, 34 y 14 | La normalización a ASCII borraba la barra de fracción | `norm()` pasa las fracciones a "1/2" antes de normalizar; "Ø" pasa a "diam" |
| 21 | 2,5" o 2.5" se leía como 5"; "13,09 pulg-eq" como un diámetro | El patrón no aceptaba decimales ni excluía las pulgadas equivalentes | Diámetros con decimales, "1-1/2", límites 1/8" a 60" y sin "pulg-eq" |
| 22 | Válvulas y accesorios del stock ("ESF PT 4 300 RF", "4#150RF", "TEE ½ 3000 NPT") quedaban sin serie | La serie solo se leía con "#" delante | Se lee el formato del stock |
| 23 | "4,413.92 c/u" se leía 413,92 y "4.550 + IVA" se leía 4,55 | Separadores de miles | Lectura de números en ambos formatos |
| 24 | En 4 hojas de la base de componentes se tomaba como material una descripción copiada de otra hoja (una caja porta orificio quedó como "válvula de retención 3" USD 5.850") | Hojas con dos columnas DESCRIPCION | Se toma la segunda y se corrigió `precios_componentes.csv` |
| 25 | Precios por metro mezclados con precios por unidad; XS juntado con Sch 80 en 10" y 12"; B7 con B8M; 2H con 8M; bridas ciegas con ciegas perforadas; codos forjados 3000 con codos BW | Clave incompleta | La unidad entra en la clave; XS = 80 solo hasta 8"; grado de bulonería; tipos nuevos |
| 26 | Compras del stock de 2009 mostradas como "último precio" | Se tomaba siempre la última compra | Compras anteriores a 2022 no se usan; precios en 0 se descartan |

**Lección:** un catálogo armado por reglas también se revisa: listar los grupos que juntan precios muy distintos (más de 2,5 veces) y mirar cada familia antes de usarlo.

### Auditoría independiente del catálogo (27/10/2026)

Un subagente comparó 2.506 precios contra sus originales (`auditorias/2026-10-27_catalogo_materiales.md`). **Ningún precio mal leído por formato** (×10, ×100, ×1000), pero sí:

| # | Error | Corrección |
|---|---|---|
| 27 | U-bolts en **pesos** cargados como USD 16.114 y 36.907 (eran USD 11 y 26) | Columna `moneda` en la base de componentes; alerta si un precio es 50 veces la mediana de piezas parecidas |
| 28 | Renglones de proveedores con varios ítems: el precio de una tee quedaba como tapón; el de un anillo BX153, como junta 3" #600 | Se toma solo el tramo del renglón que corresponde al "c/u" |
| 29 | "Codo 45° 1/2"" leído como Ø 45,5" (27 accesorios); casquete "36" x 3/8"" con 3/8" como segundo Ø | "°" se lee como grados; Ø solo de la lista de NPS; segundo Ø solo en reducciones y bujes |
| 30 | A694 F60 leído como F65; "60 días FF" (fecha de factura) leído como cara plana; SW de junta espiralada leído como socket weld | Grado capturado; FF de pago ignorado; SW no es extremo en juntas |
| 31 | 88 caños Renard sin "sin costura" y 107 con Ø "OD 48,3 mm" que no se cruzaban con los de pulgadas | "s/costura"; tabla ASME B36.10 de OD → NPS y espesor → schedule |
| 32 | 7 precios de Cintolo de 2026 con fecha por defecto 2025-08-01; fechas como "16/19/2025" o "02/07/025" | Lector único de fechas; nunca una fecha por defecto |
| 33 | Mano de obra (Ledesma, GP, Sandri) cargada como material | Los servicios no entran al catálogo de materiales |
| 34 | Chapas del stock en "USD/m²" que eran USD por hoja de 9 m² | Unidad "hoja" |
| 35 | "26,338 c/u" puede ser 26,34 o 26.338 | Si es ambiguo, se decide con el total del renglón (2 × 26.338 = 52.676); si no se puede, queda con alerta |
| 36 | Los códigos del catálogo cambiaban en cada regeneración | Registro fijo `precios/catalogo_codigos.csv` |
| 37 | Tipo de cambio de 2026 interpolado, 0,5–3,5% distinto del citado en los documentos | Anclas reales en `indices_inflacion.py`; la CAPEX pasa de 7.639,86 a 7.620,86 |

**Controles nuevos:** un solo lector de números y fechas (`herramientas/numeros.py`); columna `alerta` en el catálogo; test de regresión `herramientas/test_catalogo.py`, que hay que correr después de tocar el catálogo.
