# Inventario de fuentes

Todos los archivos de ITT revisados para armar esta base, en orden cronológico (por fecha de última modificación). Revisado el 27/10/2026.

**Estados:** ✅ vigente (se usa en la base) · 📚 referencia histórica · ❌ reemplazado · 🗑️ duplicado

## Técnico: factores de soldadura, END, espárragos y perfiles

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2022-10 | Soldadura, factores por diámetro.docx | L. Bustamante | 📚 | Escaneo del documento fuente de los factores. **Respalda la regla `espesor / espesor STD`** |
| 2023-01 | Copia de Factores de Soldadura por diámetro.xlsx | L. Bustamante | ❌ | Placas de RX sobreestimadas (48" = 29 placas) |
| 2023-05 | Tabla_I.xlsx | L. Bustamante | ❌ | Catálogo de nomenclatura. Integrado después como "TABLA GENERAL" |
| 2024-02 | Factores de Soldadura por diámetro.xlsx | L. Bustamante | ❌ | Corrige placas (215/430 mm), agrega perfiles y pintura |
| 2025-05 | Factores_de_Soldadura_p_MOMaster_.xlsx | C. Alfonso | ❌ | Agrega 17 hojas de perfiles y tubos, y espárragos por serie |
| 2025-11 | Factores_de_Soldadura_p_MOMaster.xlsx | C. Alfonso | ❌ | |
| 2025-11 | Factores_de_Soldadura_p_MO.xlsx | C. Alfonso | 🗑️ | Idéntico byte a byte al anterior |
| 2026-02 | Factores de Soldadura p MO - rev 2025.xlsx | J. Elejondo | ❌ | Pone factor 1 a SCH40 de 12" a 20" |
| 2026-03 | **Factores_de_Soldadura_p_MO - rev 02.2026.xlsx** | J. Elejondo | ✅ | Base de `tecnico/*`. Revierte el cambio anterior, 2 placas en 1"–1½", corrige la clave de 2" SCH160 |
| 2023-04 | Planilla de Acero Inox.xlsx | L. Bustamante | 📚 | Pesos de caño inoxidable A312. Pasada por OCR, con errores |
| 2024-02 | PLanilla Caños de Acero Inoxidable.xlsx | L. Bustamante | 📚 | Presiones admisibles B31.1. Pasada por OCR, con errores |

## Mano de obra y costos

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2022-10 | Copia de Anexo 1 4562.xlsx (TGS, spools Joule Thomson) | J. Alfonso / L. Bustamante | 📚 | Precio de venta de MO por pulg-eq en pesos (mar-2022). Cómputo por línea y por clase |
| 2023-12 | Costos_MO.xlsx | L. Bustamante | ❌ | Primera versión del modelo de MO. Llena de #REF! |
| 2024-01 | PLANILLA DE COSTO - TANQUE DE MEZCLA.xlsx | L. Bustamante | ❌ | Antecesora de la Planilla de Costo Master |
| 2024-02 | Costos_MO_Master_II-SEP_TRIFASICO-19-4-24.xlsx | L. Bustamante | 📚 | Caso: separador trifásico AESA (32 USD/pulg, 7,4 USD/kg) |
| 2024-09 | **Costos_MO_Master.xlsx** | L. Bustamante | ✅ | Modelo de estimación de MO (28 USD/pulg, 10 USD/kg). Tiene errores, ver reglas §7 |
| 2024-11 | **PLANILLA DE COSTO -Master.xlsx** | C. Alfonso | ✅ | Planilla de costo y venta (factor 1,33, IVA, hitos de pago) |
| 2024-12 | **Costo MO de ITT Octubre.24.xlsx** | O. Fuentes / C. Alfonso | ✅ | Costo real de planta por hora y por pulgada, más benchmarking de terceros. Incluye la hoja de sueldos por centro de costo (base del costo hora); el reparto queda en `costos/costo_hora_planta.csv` |
| 2024 | Planilla base para cotizaciones.xlsx | — | ❌ | Tarifas de END desactualizadas. Errores de fórmula, ver reglas §7 |

## Precios

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2024-08 | reporte de compras.pdf (453 páginas) | Sistema | 📚 | Órdenes de compra por artículo de dic-2021 a ago-2024, mayormente en pesos. **Pendiente de procesar** |
| 2024-11 | STOCK VALORIZADO ITT.xlsx | O. Fuentes | ✅ | Base de `precios/stock_2024-11.csv`. La hoja oculta "borrador19.09" es una versión previa. 601 artículos sin fecha de compra. **Criterio (27/10/2026):** en el catálogo, una última compra anterior a 2022 (hay de 2009) no representa el precio actual: se usa el precio maestro de nov-2024 y se deja anotada la compra vieja. Los precios en 0,00 se descartan. Las chapas con unidad "Mts²" y medida 1500x6000 tienen el precio de la hoja entera (USD/kg igual al de las hermanas): se cargan como "hoja" |
| 2025-09 | Lista TAVAL 30 vigencia 01-09-2025 - ventas.xlsx | Taval | ✅ | Coeficiente 1,25 y USD/kg. Columnas de precio con #REF!: **pendiente de obtener una versión sana** |
| 2025-11 | 1788-JCA-1125 - ITT SA.pdf (Antonelli) | Antonelli | ✅ | Tarifas de END, en `costos/tarifas.csv` |
| 2025-12 | RENAR ListaPrecios_ittSA_20251226.xlsx | Renard | ✅ | Base de `precios/lista_renar_2025-12.csv` |
| 2026-02 | Precios varios materiales de acero, chapa, angulo, etc.xlsx | J. Elejondo | ✅ | Chapa, perfiles y caño estructural en USD/kg, en `costos/tarifas.csv` |
| 2026-03 | **COTIZACION ELEMENTOS DE EQUIPOS.xlsx** | Lautaro / J. Elejondo | ✅ | Base de `precios/precios_componentes.csv`. 25 rubros con proveedor y fecha. **Corrección 27/10/2026:** en las hojas con dos columnas DESCRIPCION (bombas dosificadoras, caja porta orificio, anillo de purga, válvulas) lo cotizado es la segunda; la primera y la dimensión son un modelo copiado de otra hoja. Se leían al revés (p. ej. "válvula de retención 3"" a USD 5.850 era una caja porta orificio API 6A). Y "4.550 + IVA" se leía 4,55: son USD 4.550. **Auditoría 27/10/2026:** la hoja U BOLT está en **pesos** ("$16.114,07 + IVA", encabezado sin U$S): columna `moneda` nueva; la fecha de la columna proveedor ("Cintolo cot 11/02/26") manda sobre la de la columna fecha; 3 fechas ilegibles en el origen quedan vacías (nunca una fecha por defecto). Informe: `auditorias/2026-10-27_catalogo_materiales.md` |

## Comercial y codificación

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2022-05 | Registro de presupuesto.xlsx | L. Bustamante | ✅ | Base de `comercial/registro_cotizaciones_2020-2022.csv` y `codificacion/familias_producto.csv` |
| 2022-09 | ITTSA-Diagrama de Proceso.docx | L. Bustamante | ✅ | Proceso comercial y de ejecución de ITT (ver README) |
| 2023-02 | especificacion de una valvula Rev A.pdf | C. Sorrentino | 📚 | Explicación escrita del codificador |
| 2023-05 | vta_remitoporcliente.xls | Sistema | ✅ | Base de `comercial/ventas_2022-2023.csv` |
| 2023-05 | vta_remitoporcliente_i.xls | Sistema | 🗑️ | Mismo contenido, con fechas como texto |
| 2023-07 | **HD Instructivo de codificacion.xlsx** | S. Giron / C. Sorrentino | ✅ | Base de `codificacion/*` y `comercial/clientes.csv` |
| 2026-08 | **Seguimiento de presupuestos/Proyecto/facturación Rev1.xlsx** | C. Alfonso / J. Elejondo | ✅ | Base de `plazos.md`, `comercial/plazos_*.csv` y `comercial/cotizaciones_2024-2026.csv`. También tiene facturación y cobranza, clientes activos y potenciales de Taval, cronogramas y faltantes de materiales por OP. Los contactos de cada cotización quedan en `comercial/cotizaciones_2024-2026.csv` |

## Técnicos de ingeniería (para futuros módulos)

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2024-11 | Cálculo calentador.xlsx y Cálculo calentador BAGSA.docx | G. Vicens | 📚 | Dimensionamiento térmico de un calentador indirecto (API 12K). Los dos tienen el mismo cálculo |

## Pedidos y planos de prueba

| Fecha | Archivo | Uso |
|---|---|---|
| 2026-10 | Mail Almacenes Petroleros (carreteles 3" CL900) | Caso piloto de cotización |
| 2026-04 | ACO-CNV-PTIP-M-PL-005 Rev0.dwg (manifold 8×4 S600, Tecpetrol) | Prueba de lectura de DWG. Confidencial de Tecpetrol |

## Carpeta de ofertas y licitaciones (Z:\VENTAS\OFERTAS Y LICITACIONES)

15.601 archivos (27 GB) en 533 carpetas de cotización de 75 clientes, 2017–2026. Se trajo la **tanda 1**: oferta comercial, proveedores, propuesta comercial enviada y OC (2.281 archivos, 1,9 GB, 307 carpetas), con la fecha original de cada archivo. Se analizaron en detalle **las 93 cotizaciones de 2026**: ver `fichas_2026/`, `comercial/cotizaciones_2026*.csv`, `precios/proveedores_2026.csv` y `aprendizajes_2026.md`. También **las 66 cotizaciones de 2025** que tienen documentos comerciales (27/10/2026, 12 agentes; muestra de 7 datos verificada contra los originales, sin diferencias): ver `fichas_2025/`, `comercial/cotizaciones_2025*.csv`, `precios/proveedores_2025.csv` y `aprendizajes_2025.md`. Otras 55 carpetas de 2025 solo tienen documentación del cliente (no está en la tanda 1). Quedan sin analizar las de 2021–2024. La documentación del cliente (22 GB) no se trajo.

## Índices de inflación (para ajustar precios a hoy)

| Fecha | Dato | Fuente | Uso |
|---|---|---|---|
| 13/10/2026 | IPC 12 meses a sep-2026: 33,4%; acumulado ene–sep 2026: 23,6% | INDEC (vía medios: Canal 26, El Economista, Dólar Hoy) | `costos/indices_ajuste.csv` |
| 12/11/2025 | IPC 12 meses a oct-2025: 31,3% | INDEC (vía A24, Calcular Sueldo) | ídem |
| 2024–2026 | Dólar BNA vendedor: promedio mensual de datos diarios (`costos/dolar_mensual.csv`, api.argentinadatos.com). Reemplaza a los valores puntuales 1.011,50 (31/10/2024), 1.475 (31/10/2025), 1.480 (30/12/2025), 1.550 (23/10/2026) | ver "Dólar mensual" | ídem |
| 14/10/2026 | CPI EE.UU. 12 meses a sep-2026: 3,7% | BLS (vía Trading Economics) | ídem |

Los meses intermedios se interpolan. Octubre 2026 es estimado. Hay que actualizar la tabla cuando salgan los datos nuevos (`herramientas/indices_inflacion.py`).

## Dólar mensual (27/10/2026)

`costos/dolar_mensual.csv` y `.xlsx`: por mes desde ene-2024, pico (con fecha), mínimo, promedio y cierre del dólar oficial BNA billete vendedor, mayorista, MEP y blue, y la brecha blue/oficial. Datos diarios de api.argentinadatos.com, guardados en `fuentes_originales/indices/dolar_diario.csv`. Se rearma con `python herramientas/dolar_mensual.py`. Hasta el 14/04/2025 hubo cepo (brecha de 9% a 53%); desde mayo-2025 la brecha es menor al 2%.

**Decisión de Matías (27/10/2026): para pasar pesos a dólares se usa el promedio mensual del dólar oficial BNA billete, precio de venta.** Si el documento dice su tipo de cambio, se usa ese. Fundamento: en todos los textos de cotizaciones, pliegos y OC no hay ninguna mención a MEP, blue ni CCL; cuando se aclara, es siempre BNA vendedor (divisa o billete). Para precios en pesos llevados a hoy con `indice_local_usd`, el dólar del pasado se cancela en la cuenta. `indices_ajuste.csv` toma ese promedio para todos los meses desde ene-2024 (reemplaza a las anclas interpoladas y a las del dólar divisa que se habían cargado por error). Riesgo que queda: datos que alguien pasó a dólares durante el cepo sin decir con qué tipo de cambio (costo hora de planta oct-2024, compras del stock 2022–2024).

## Período con cepo (decisión del 28/10/2026)

Los valores con fecha anterior al 14/04/2025 cuyo documento no dice con qué tipo de cambio se pasaron a dólares se descartan como precio y vale el último valor confiable. Prueba: el stock valorizado pasa las compras en pesos a dólares con el TC del día del informe (la compra del 13/06/2023 del espárrago 5/8 x 3 1/4 figura a USD 2,37 en la hoja de sep-2024 y a 2,25 en la de nov-2024). En el catálogo de materiales esto deja 1.020 de 2.310 materiales "sin precio confiable" (casi todo el stock, incluidas 53 de 58 válvulas): conservan el valor descartado como referencia y la alerta "pedir cotización". Excepción documentada: costo de planta oct-2024 (TC 997–998,5 explícito en la hoja "Sueldos").

## Faltantes conocidos

1. **Plazos:** cubierto en parte con el seguimiento de proyectos (ver `plazos.md`). Faltan plazos de proveedores actualizados por rubro.
2. **Costo real de proyectos terminados** para comparar con lo cotizado.
3. **Resultado de las cotizaciones 2024–2026:** 232 de 284 figuran como "Enviado" sin resultado.
4. **Lista Taval sin #REF!**.
5. **Reporte de compras** (PDF de 453 páginas) sin procesar: es el historial de precios de compra.
