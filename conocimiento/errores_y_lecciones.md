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
| 38 | Al cargar los tipos de cambio de 2026 de la auditoría se mezcló el dólar **divisa/mayorista** (1.395, 1.411…) con una serie de **BNA billete**; la CAPEX bajó a 7.620,86 por eso | Una sola serie: promedio mensual BNA billete vendedor (`dolar_mensual.csv`), decisión de Matías. Antes de cargar un dato en una serie, verificar que sea la misma cotización |
| 39 | "131.131" de una planilla Excel se leía como USD 131.131 (es 131,13): tres válvulas esféricas 2" quedaron 226 veces por encima de la mediana | En textos sacados de Excel el número está en formato de máquina: se lee con punto decimal. La alerta de "50 veces la mediana" lo detectó |
| 40 | "11/4" (1 1/4") se leía como 11/4 = 2,75": en `factores_soldadura.csv` y `esparragos_por_brida.csv` no existía el 1 1/4" | `construir_base.pulgadas`: entero pegado a una fracción propia ("11/4", "23/4") |
| 41 | Los PDF de la página (informe y ofertas) salían cortados a la derecha: el contenido medía 774 px y el A4 con márgenes de 10 mm deja ~718 px | Ancho del contenido = ancho útil de la hoja (718 px). Después de cambiar un documento, mirar la primera página renderizada |
| 42 | La tarea semanal creada para "abrir una sesión nueva en cada corrida" no tenía acceso al repositorio (403) y no hizo nada | La tarea despierta una sesión fija con el repositorio adjunto ("Cotizador ITT – tarea semanal"). Toda tarea programada se prueba disparándola una vez al crearla |
| 43 | `verificar_todo.py` regeneraba Excel, Word, PDF e informe con fechas internas nuevas y dejaba el repositorio "con cambios"; la sesión de la tarea semanal no tiene permiso para descartarlos y eso le traba el `git pull` | El control restaura los archivos derivados que estaban limpios si no cambió ningún dato (CSV, JSON, MD) |
| 44 | Caso de control CTRL-F01: "media cupla … conexión manómetro" y "chapa soporte manómetro" se buscaban como manómetros (USD 120) | Si el texto da instrumento pero la pieza nombrada antes de "para / con / conexión / soporte" es otra familia, manda la pieza |
| 45 | En un caso de control, el catálogo ya tenía los precios del mismo proyecto: la prueba se "copiaba" a sí misma | `precotizar.py --excluir <proyecto>` |
| 46 | La precotización dejaba la radiografía en 0% y las horas de ingeniería, calidad y montaje en blanco: en un filtro chico son el 56% del costo | Avisos en rojo en la precotización; no presentar un precio sin completarlas |
| 47 | El caño se presupuestaba por los metros usados; en la realidad se compra la barra entera de 6 m | `precotizar.py` agrega la fila de compra extra (Nb) para completar la barra |
| 48 | El precio de una cotización cambiaba solo cuando la base sumaba un mes de índices (el control de la CAPEX iba a fallar el 02-11 al completarse el dólar de octubre) | Al pasar a revisado se congelan los índices en la cotización (`indices_congelados`); al volver a borrador se descongelan |
| 49 | La oferta económica con flete incluido sumaba el flete al total sin mostrarlo en ninguna fila (USD 2.453,79 sin explicar) | Fila "Flete y embalaje hasta destino" en la oferta (Python y página); `generar_oferta.py` verifica unitario × cantidad + flete = total |
| 50 | La plantilla de oferta traía los datos de la CAPEX: una cotización nueva podía salir con otro cliente | Plantilla neutra con [corchetes] |
| 51 | Skid YPF: `precotizar.py` contaba los metros de caño como piezas (11,5 m → 23 extremos BW) | Con caño por metro, cada extremo BW de accesorio o brida es una junta; tee de reducción: 2 extremos del diámetro mayor y 1 del menor |
| 52 | Los olets se medían por el caño donde se sueldan (sockolet 12"x3/4" = 21 pulgadas) | Se miden por la salida (3/4" × 1,75) |
| 53 | Una válvula de 2" se usó como "similar" para una de 8" (USD 131 contra 1.346) | Si el similar difiere más de 1,6 veces en diámetro, queda SIN PRECIO con el similar como referencia |
| 54 | La plantilla de oferta neutra quedó sin `firma` y con `imagen_plano` vacío: `generar_oferta.py` fallaba en la primera cotización nueva; además decía "POR PUENTE" fijo | `firma` en la plantilla; imagen solo si es un archivo; título con `equipo.singular` |
| 55 | Desde el celular el conector "Claude Code Remote" no cargó: el pedido quedó pendiente (y el Excel se subió dos veces) | Los pendientes se procesan desde la sesión de trabajo o el lunes; revisar la doble subida |

| 56 | Al armar una cotización nueva, el catálogo volvía a leer como "precio usado" los precios que la cotización había tomado del propio catálogo, y las filas de compra extra (sobrante de barra) como piezas | `catalogo_materiales.py` ignora las fuentes con código del catálogo y las filas 14b |
| 57 | Controles con 4 agentes (28-10-2026): la app daba entre −42% y +35% y los totales "buenos" eran compensación de errores | `herramientas/correr_controles.py` mide los 5 casos antes y después de cada cambio; resumen en `conocimiento/auditorias/2026-10-28_controles_4_agentes.md` |
| 58 | Horas de otro tipo de equipo (trampa para un manifold, TK glicol para un tanque de choque) | `estimar_horas`: grupos afines, tamaño por pulgadas de soldadura, mediana de 3 antecedentes (uno por proyecto) |
| 59 | Soldaduras: el doble por caño se aplicaba a virolas y casquetes; espesor escrito no se leía; tarifa de 2024 con cepo | Doble solo para piezas del diámetro del caño, ajuste 0,75 por uniones directas, `espesor_mm`, costura de virolas, tarifa 16 USD/pulg de las planillas 2026 |
| 60 | Pintura solo de caños y niples (−73% a −94%) | Caños × 3 por bridas/accesorios/válvulas + envolvente + estructura (30 m²/t, `perfiles.csv`) |
| 61 | Radiografía con tarifa Antonelli y un servicio por equipo en series | Tarifa vigente más reciente (DB NDT 08-2026), servicios repartidos en la serie, LP para SW y olets; Antonelli como alternativa |
| 62 | Catálogo: renglones de cotización con varios productos quedaban con el precio de otro (computador ABB a 864 en vez de 7.346; Doma a 1.380 en vez de 8.206) | `catalogo_materiales.separar_renglon`: una pieza por tramo, con guardas (rangos, descuentos, fletes, tramos sin producto) |
| 63 | Similares inválidos: válvula manual por una actuada, #300 por #3000, paso reducido por total; se descartaba la pieza en vez de probar el siguiente similar | Tipo "actuada", paso solo en esféricas (PT = PR × 1,30), serie hasta 2,6 veces, se prueba el siguiente similar; Taval solo si el precio elegido es Taval |
| 64 | Virolas y perfiles por metro sin precio; bastidores A-36/SA-36 no reconocidos; no se calculaba la fabricación de la estructura | Virola = kg × (chapa + rolado 3,7/kg); perfiles m → kg; regex de aceros; fila EST (kg × 3 USD/kg) |
| 65 | `--excluir` borraba la pieza entera; precios atípicos sin alerta | Se usa el precio más reciente no excluido del historial; si el último se aparta 40% de la mediana, va la mediana |
| 66 | `comparar_historico` ponía el montaje bajo "prueba hidráulica" y pisaba su salida con `--json` | Rubro por código primero y palabras enteras; salida propia por archivo |


### Segunda tanda de controles (TS01, P02, SK01, CA01) · corregido el 28-10-2026

| # | Error | Corrección |
|---|---|---|
| 67 | Válvulas de otra serie como similar (Taval #900 con #300) y la marca ganándole a la serie | Válvulas: serie distinta = SIN PRECIO con referencia; en el resto, hasta 2,1 veces. En `buscar_material` las diferencias de Ø, serie, schedule y medida pesan antes que la marca |
| 68 | Candidato sin diámetro tomado como similar (retención 12" con una wafer 3" no leída) | Válvulas, bridas, accesorios, caños y niples: sin Ø no sirve si el plano lo da. Lectura de Ø en columnas sueltas ("\| 3 \| 150#") y en "CODO 90 10 BW" |
| 69 | Retención rotulada "VALVULA ESFERICA … Ret" (planillas Sacde) cargada como esférica | "Ret", "retención", "check" o "wafer" mandan sobre esférica/esclusa/globo |
| 70 | Similares de otro Ø o schedule usados sin escalar; brida 16" con una de 10" | Desde 8", Ø hasta 1,25 veces; precio × (Ø pedido ÷ Ø similar)^1,5 (olets: por la salida); caños y accesorios × espesor pedido ÷ espesor del similar (no en bridas) |
| 71 | `sch_de("XS")` vacío; "WNRF", "P.T.", "ESP SWI", "BX 153", "scrapper", "1 7/8"", "7/8 x 145 mm", "1.25x207", "L=", "esp. 5/8"" mal leídos | Lectores corregidos con casos de regresión en `test_precotizar.py` |
| 72 | Familia "Otros" (tapas, U-bolts, detectores) sin comparar Ø ni serie; tipo = 3 primeras palabras | Tipos por palabra clave (tapa de cierre rápido, u-bolt, detector de scraper, elemento filtrante) y comparación de Ø y serie |
| 73 | Precio de stock o compra de 2022–2024 como IGUAL contra una cotización 2025–2026 que solo cambia la cara | Si el stock/compra tiene más de 18 meses y hay una cotización reciente que solo difiere en cara/extremos, va la reciente (como similar) |
| 74 | Tuercas cobradas dos veces (el espárrago elegido ya traía 2 tuercas) | Si el precio elegido del espárrago dice "c/2 tuercas" o "juego", las tuercas del plano van en 0 con aviso |
| 75 | `--excluir` no filtraba `tarifas.csv` ni los buscadores; tarifas posteriores a la fecha de referencia; fecha imposible "2026-02-31" | `tarifa()` excluye por fuente y prefiere tarifas hasta 2 meses después de la fecha de referencia; `--excluir` repetible en los tres buscadores; último día real del mes |
| 76 | Barra fija de 6 m, una barra por tramo y barra entera para 0,1 m | Tramos del mismo caño agrupados; 12 m desde 3"; menos de 0,5 m sale de recortes |
| 77 | Horas de otro tipo de equipo o tamaño (puente con skids, trampa con tanques, filtro 4" con coalescedor 36"); ingeniería y calidad escaladas por tamaño | Solo antecedentes del mismo tipo y Ø hasta 2,5 veces; si no hay, afines solo entre armados de cañería; si tampoco, **no se suman horas** y se avisa. Ingeniería y calidad no se escalan. Subtipos (concentrador, bomba, medición, receptora…) |
| 78 | MO de terceros con el mismo alcance no usada (Ledesma trampa 10.800); soldadura y montaje propios sumados | Si el catálogo tiene la fabricación por tercero del mismo tipo (con Ø o subtipo iguales), va como fuente principal y la soldadura propia como alternativa; sin montaje propio |
| 79 | Pintura × 3 fijo (corta con válvulas grandes, triplicaba caño recto) | m² por pieza con largo equivalente (brida 1,5 D, codo 2,4 D, tee 3 D, válvula 6 D) |
| 80 | No había modo prefabricado: materiales del cliente cotizados, 0 juntas en caño recto, factor de espesor por pulg-eq, pintura dentro, horas de skid | `provee`/"provisto por el cliente" → precio 0; juntas de empalme entre barras; `parametros.modo = "prefabricado"`: pulgada diametral base sch 40, tarifa de prefabricado de terceros, +5% de rechazos, pintura aparte, sin horas ni PH |
| 81 | Lista 30 de Taval y cotizaciones de TAVAL/72 y /78 fuera del catálogo; historial con otra pieza (niple 2" en un código de 1/2") | Lista 30 × 0,52 en el catálogo (720 precios, `precios/taval_lista30.csv`); Complemet 275397 y MS 48.729 / 49.323 renglón por renglón; al volver al historial se exige el mismo Ø, serie y schedule |

### Camuzzi CP 24578 (COT26-0135-001/002/003) · revisión independiente del 28-10-2026

| # | Error | Corrección |
|---|---|---|
| 82 | Separador coalescente: el diámetro salió del área de los elementos (34 × paso² + "huelgo") y no entraban en Ø44"; el caudal por elemento se tomó de otro coalescedor sin saber el elemento | Dimensionar con el arreglo real (anillos completos de un paso triangular) y con el caudal por elemento del fabricante; presión de diseño explícita |
| 83 | Precio de un elemento de separador de polvo (Gora 90) usado para un coalescente de 0,3 µm | No usar como similar un elemento de otra función: estimado con aviso hasta cotizar |
| 84 | `precotizar` no encontró la te de reducción "8\"x6\"" (había IGUAL en Renard) y eligió una esférica galvanizada de 3.500 en lugar de la Taval de lista (740) | Revisar a mano los SIMILAR de válvulas; pendiente en la herramienta: el material galvanizado/inoxidable "no pedido" no tiene que ganar a uno sin esa diferencia |
| 85 | Bloqueo y purga "con manómetro" cotizado sin el manómetro; prueba de fugas pedida sin renglón | Leer la descripción completa del plano; cada ensayo del pliego con su renglón |
| 86 | Precios "estimados" sin ninguna referencia (toma multiport, alivio S-71, termovaina, switch, prueba de fugas; en la CAPEX: manga, sellador e ingeniería) | Regla P4 ter de Matías: sin referencia ni pieza parecida, 0 y pedir cotización. `verificar_computo.py` da error; el chat de la página tiene la misma regla |

## Espesores de 28" y 30" mal cargados en la tabla de factores de soldadura (28-10-2026)
- **Error:** la planilla de ITT `factores_soldadura_rev02-2026.xlsx` tenía 28" STD 8,74 / XS 11,91 / "Sch 40" 6,35 y 30" STD 10,31 / XS 14,27 / Sch 30 17,48 mm. ASME B36.10M da 28" STD 9,53 / XS 12,70 (sin Sch 40) y 30" STD 9,53 / XS 12,70 / Sch 30 15,88. Afectaba kg/m, m² y el factor de soldadura de esos diámetros.
- **Cómo se detectó:** control de `canos_peso_superficie.csv` contra Wermac y Project Materials (388 valores, 373 iguales; los otros 9 desvíos eran de las fuentes).
- **Corrección:** `construir_base.CORRIGE_B3610` corrige al leer la planilla; se regeneraron `factores_soldadura.csv` y `canos_peso_superficie.csv`.
- **Lección:** una tabla interna vieja también se controla contra la norma antes de usarla.

## Perfiles HEB y UL con kg/m equivocados en la tabla de perfiles (28-10-2026)
- **Error:** en `perfiles.csv` (de la planilla de ITT) las HEB repetían los kg/m de las HEA (HEB100 16,7 en vez de 20,4; HEB500 155 en vez de 187: entre 17% y 33% menos), y las UL (UPN chicos) tenían el ancho de ala como peso (UL 40x20 = 20 kg/m en vez de 2,87).
- **Cómo se detectó:** al armar las tablas de estructura con fuente (INTI-CIRSOC, Acindar, Ferrara, ArcelorMittal).
- **Corrección:** `construir_base.perfiles()` corrige al leer la planilla (UL fijas; HEB desde `estructura_perfiles_laminados.csv`).

## Juntas a tope con decimales en la ficha (29-10-2026)
- **Error:** la ficha mostraba "28,50 juntas a tope" (el ajuste de uniones directas 0,75 sobre el caño por metro deja medias juntas) y la cabecera "29": dos números distintos para lo mismo.
- **Corrección:** las juntas se redondean hacia arriba en `precotizar.soldaduras` y en `web/src/ficha.js`; las pulgadas equivalentes quedan con decimales.
- **Lección:** una cantidad física que se cuenta (juntas, piezas, viajes) se muestra entera; los equivalentes de cálculo pueden tener decimales.

## 29-10-2026 — "Chat nuevo" falló desde la página (upstream_error)
- Qué pasó: `create_session` llamado desde la página devolvió `upstream_error` y no creó la sesión; la misma llamada desde una sesión de Claude Code funcionó.
- Causa probable: desde la página no hay sesión que llame, así que no hay de dónde heredar el modelo (y el modo auto no se puede comparar con el de una sesión).
- Corrección: el modelo va en `config/claude_code.model` (base de la página) y la página reintenta sin modo auto y sin etiqueta si el servicio rechaza. El aviso muestra el código y el mensaje real del error.
- Lección: una llamada a un conector que en la sesión funciona puede fallar desde la página; probar el camino real (desde la página) antes de darlo por hecho y mostrar el error completo.

## 29-10-2026 — Dos formatos de número a la vista (auditoría)
- Qué pasó: la página mostraba 5.644,46 y el informe y la oferta económica 5,644.46 (`documentos.js` con `en-US`, `generar_oferta.py` con `:,.2f`); los campos aceptaban "0.35" como decimal y "3,500,000.5" en formato inglés, así que "1.5" y "1,500" se podían leer distinto de lo que se quiso escribir.
- Corrección (Matías): punto de miles, coma decimal y 2 decimales en todo lo que se ve (`numeros.fmt`/`fmtg`, `Documentos.num`); los campos aceptan solo ese formato, marcan en rojo y explican el motivo, y al salir se reescriben (1500 → 1.500) para que se vea cómo se entendió. Las planillas usan `#,##0.00` (Excel con configuración argentina muestra 1.234,56). El control de `verificar_todo.py` pasó a "7.366,12".
- Lección: un número que se puede leer de dos maneras es un error esperando pasar; el formato se fija en un solo lugar y lo ambiguo se rechaza, no se adivina.

## 29-10-2026 — Números ambiguos dentro de las tablas (auditoría de números)
- **Qué pasó:** precios guardados con 3 a 16 decimales ("6.408", "735563.5631796557", "6099.9800000000005") en catálogos, listas, planillas de costo, stock e históricos; en formato argentino "6.408" se lee 6.408 (miles). Notas técnicas con dos formatos en la misma celda ("x0,45359 (lb de la fuente: 0.08)", "10,6 lb = 4.808 kg"). Excel con números guardados como texto (cantidades y series de la lista para Compras, antecedentes de la planilla) y el dólar mensual sin formato y con fechas AAAA-MM-DD. El cómputo escribía el precio con `:g` (con números grandes sale notación científica).
- **Corrección:** precios a 2 decimales en el script que escribe cada tabla (`numeros.precio_csv`) y en las tablas fijas; Excel con celdas numéricas y formato (`numeros.celda_excel`: `#,##0.00` precios, `#,##0.0###` técnicos, claves como texto); notas y textos con coma decimal. Informe: `conocimiento/auditorias/2026-10-29_numeros_tablas.md`.
- **Errores de esta misma corrección (atajados por los controles):** (1) convertir "1.900 mm" como si fuera decimal en textos escritos a mano (ya estaban en formato argentino): los números con 3 decimales solo se convierten cuando el contexto asegura que son decimales; (2) reescribir CSV con `csv.writer` cambió las comillas de todo el archivo: se reemplaza campo por campo en el texto crudo; (3) cambiar el `detalle` de `proveedores_2025/2026.csv` y la `unidad_compra` de acero creó códigos nuevos en el catálogo, porque esos textos son parte de la clave y de ellos se leen precios: se dejaron como estaban; (4) redondear `precio_ultima_compra` del stock dejó en 0 compras basura de 0,0001 USD y el catálogo pasó a usar el precio maestro (4 materiales nuevos).
- **Lección:** antes de reformatear un texto, saber si algún programa lo usa como clave o lo vuelve a leer; y un número con 3 decimales después del punto no se puede convertir sin mirar de dónde viene.
