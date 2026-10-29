# Números en las tablas: miles, decimales y precios con 2 decimales (29-10-2026)

Aplicación de la decisión de Matías del 29-10-2026: precios y montos con 2 decimales; en lo que se ve, punto de miles y coma decimal (1.234,56); en ninguna tabla tiene que haber duda sobre qué es miles y qué es decimal. Se revisaron todos los CSV y JSON del repositorio (menos `fuentes_originales/`), los Excel que generan las herramientas y la página, y los Markdown e informes generados. Los scripts de revisión quedaron fuera del repo.

## Convención que quedó, por tipo de archivo

| Tipo | Cómo se guardan los números | Quién lo asegura |
|---|---|---|
| CSV y JSON que lee el código (`conocimiento/**/*.csv`, `cotizacion.json`, `computo.csv`, `web/datos.json`) | Formato de máquina: punto decimal, sin separador de miles, sin "USD" ni espacios. **Precios con 2 decimales como máximo** (sin ceros de más: `6.41`, `12`). Técnicos (kg, kg/m, espesores, factores, índices) con los decimales que hagan falta | `numeros.precio_csv` / `redondear_precios` en cada script que escribe una tabla |
| Textos dentro de esas tablas que se muestran (notas, alertas, especificaciones, avisos) | 1.234,56 (`numeros.fmt` / `fmtg`) | scripts generadores; tablas fijas corregidas a mano |
| Descripciones de materiales, claves, citas textuales de documentos | Como vienen: no se tocan (son clave de búsqueda/código o copia literal del original) | — |
| Excel (catálogos, dólar mensual, planillas de cotización, lista para Compras, planilla de la página) | Celdas **numéricas**, nunca texto. Formato `#,##0.00` en precios, `#,##0.0###` en técnicos, `#,##0` en enteros y `0` en año, serie y schedule (2000, no 2.000). Excel en configuración argentina los muestra 1.234,56. Pos, código, ID y OC quedan como texto (son etiquetas: hay "14b", "A") | `numeros.celda_excel`; en la página, `fila`/`zDe` de `Documentos.compras` |
| Markdown, informes HTML, ofertas Word/PDF | 1.234,56 | `numeros.fmt` / `Documentos.num` |

Ojo, sigue vigente lo que avisó la auditoría de estructura (M6): `numeros.leer_numero` es para documentos de terceros. Un CSV interno con un técnico de 3 decimales ("1.633" kg) leído con `numeros.py` da 1633. Los CSV internos se leen con `float()`.

## Qué se corrigió, tabla por tabla

### Precios con más de 2 decimales (corregido en el script que escribe la tabla)

| Tabla | Script | Celdas que cambiaron | Ejemplo |
|---|---|---|---|
| `precios/catalogo_materiales.csv` | `catalogo_materiales.py` (al escribir CSV y Excel; los cálculos siguen sin redondear) | último precio 2.389 · ajustado a hoy 4.344 · mín. 2.495 · máx. 2.492 · referencia descartada 103 | 38.656 → 38.66; 8.751 → 8.75 |
| `precios/catalogo_materiales_historial.csv` | idem | precio 658 con más de 2 decimales, ajustado 6.168 | 190.692 → 190.69 |
| `precios/catalogo_servicios.csv` | `catalogo_servicios.py` (`round(…, 4)` → 2) | ajustado 550 · tarifa ajustada 266 · último 99 · tarifa unitaria 44 | 13.6666 → 13.67; 4411.9055 → 4411.91 |
| `precios/catalogo_servicios_historial.csv` | idem (también `precio_origen`) | valor ajustado 629 · precio de origen 72 · valor 84 · total 80 | 16.333333333333332 → 16.33 |
| `precios/listas_vendedor.csv` | `listas_vendedor.py` | 501 | Cintolo codo 1" 6.408 → 6.41 (verificado en la lista: dice 6,408) |
| `precios/taval_lista30.csv` | `pesos_valvulas.py` | 81 | 114.23076923076923 → 114.23 |
| `precios/acero_por_kg.csv` | `acero_por_kg.py` | 18 (usd_kg y con recortes) | 1.1585 → 1.16 |
| `precios/indice_precios.csv` | `indice_precios.py` | 16 con más de 2 decimales | 73.91742195367573 → 73.92 |
| `precios/planillas_costo_items.csv` y `servicios_desde_planillas.csv` | `unir_planillas_costo.py` | 230 y 61 | 159.28898059103454 → 159.29 |
| `comercial/indice_proyectos.csv` | `indice_proyectos.py` | 1 | 735563.5631796557 → 735563.56 |
| `cotizacion_auto.json` (precotización) | `precotizar.py` (`round(…, 4)` → 2 y redondeo final) | — | — |
| `computo.csv` | `armar_cotizacion.py`: el precio se escribía con `:g` (notación científica desde 1.000.000) | 2 | 1.8953 → 1.9 |
| `comercial/*` desde planillas | `construir_base.py` (redondea al escribir toda columna de precio) | — | — |

### Precios con más de 2 decimales en tablas fijas (no las regenera ningún script del flujo)

| Tabla | Celdas | Ejemplo |
|---|---|---|
| `comercial/cotizaciones_2024-2026.csv` (monto) | 14 | 773.552 → 773.55 (verificado en `seguimiento_presupuestos_proyectos_2026-08.xlsx`: 773,552 con formato `#,##0.00`, decimal); 2466936.5118635832 → 2466936.51 |
| `comercial/registro_cotizaciones_2020-2022.csv` | 29 | 41748.157449275364 → 41748.16 |
| `comercial/ventas_2022-2023.csv` | 4 | 6099.9800000000005 → 6099.98 |
| `comercial/cotizaciones_2025_items.csv` y la ficha `TECHINT_10_…json` | 1 + 1 | 735563.5631796557 → 735563.56 |
| `costos/horas_por_equipo.csv` (costo_materiales_usd) | 15 | 74322.245 → 74322.24 |
| `costos/sueldos_2024-10.csv` | 1 | 19239665.939999998 → 19239665.94 |
| `precios/planillas_costo_items_parte1..4.csv` | 90 + 128 + 28 + 3 | 8.5023 → 8.5; 5750.000000000002 → 5750 |
| `precios/stock_2024-11.csv` | 299 | 2.2467270896273916 → 2.25 |
| `precios/precios_componentes.csv` | 2 | MS Juntas 0.904 → 0.9 y 9.874 → 9.87 |
| `precios/servicios_extraidos.csv` | 11 | 19.7293 → 19.73 |
| `cotizaciones/CTRL-*/historico.csv` | 26 | 42.042 → 42.04 |
| `cotizacion.json` de YPF 713 y 708 | 2 + 2 | estructura 1.8953 → 1.90 USD/kg; alternativa Taval 42.042 → 42.04 |
| `cotizacion_agente.json` y `cotizacion_auto.json` de los CTRL y de la Camuzzi 001 | 63 | 136.0008 → 136 |

### Celdas numéricas con otro formato
- `precios/catalogo_materiales.csv`, `espesor_mm`: "1,6" y "7,9" (PER-03031 y PER-03071) → "1.6" y "7.9". Se corrige al escribir el CSV y el Excel; la clave del registro de códigos no se toca.
- No había otras celdas con coma decimal, separador de miles, "USD" o espacios en columnas numéricas. Lo que el barrido marca como "no numérico" en columnas mayormente numéricas son claves o textos a propósito (pos "14b", serie "80x40", códigos "M00", OC "4100271688 y 4100271689").

### Textos a la vista
- Generadores corregidos: factor del dólar blue en el catálogo ("× 0,866"), nota de Taval ("lista USD 3.375,00 × 0,52; 128 kg"), factor en `comparar_antecedentes.py`, factor de juntas en `precotizar.py`, cantidades del plano en la oferta técnica (`generar_oferta.py` y página), factor Taval y soldadura en la página (`app.js`, `busqueda.js`, `ficha.js`).
- Notas de tablas fijas pasadas a coma (solo columnas nota/observación/detalle/comentarios; 4.542 + 493 celdas): técnicas (`accesorios_peso*`, `esparragos_peso`, `olets_peso`, `bridas_peso`, `estructura_*`, `canos_*`), `costos/horas_por_equipo.csv`, `costos/tarifas.csv`, planillas de costo, `precios_componentes`, `servicios_extraidos`, `plazos_proveedores`, `marcas_aprobadas`. Ejemplo: "convertido de lb x0,45359 (lb de la fuente: 0.08)" → "(lb de la fuente: 0,08)".
- `cotizacion.json` (especificaciones y notas de las 5 en curso): "1 tramo de 6 m para 1.8 m" → "1,8 m".
- Markdown: precotizaciones y comparaciones viejas de COT26 y CTRL (estaban en formato inglés: "USD 16,421.40" → "16.421,40"), bitácoras de YPF, `aprendizajes_2025.md`, `aprendizajes_2026.md` y `costos/horas_por_equipo_LEEME.md`. `comparacion_antecedentes.md` regenerado.
- Excel: lista para Compras con cantidades y series del documento como números (antes texto: "3", "2000"); planilla con formato en cantidades e índices y antecedentes numéricos; `dolar_mensual.xlsx` con 2 decimales, brecha con 1 y fechas DD-MM-AAAA (antes "General" y AAAA-MM-DD); catálogos con schedule/serie numéricos (antes 98 a 866 celdas de texto por hoja).

## Lo que NO se corrigió y por qué

| Qué | Por qué |
|---|---|
| `costos/tarifas.csv`, `valor_usd` con rangos ("17.2-28.8", "1.32-1.72"; 5 filas) | Es un cambio de estructura (`valor_min`/`valor_max`, propuesto en la auditoría de estructura M2). Lo tiene que decidir quien mantenga las tarifas |
| `proveedores_2025.csv` / `proveedores_2026.csv`, columna `detalle` ("USD 4,413.92 c/u", "USD 126.80") | El catálogo arma la descripción y la clave del material con ese texto y además lee precios de ahí (`desambiguar`). Al convertirlo aparecieron 6 códigos nuevos: se volvió atrás |
| Proveedor "Taval (Lista 30 × 0.52)" en el catálogo y en los `cotizacion.json` | Es parte de la clave de 35 materiales SOLO en `catalogo_codigos.csv`; cambiarlo renumera |
| `acero_por_kg.csv`, `unidad_compra` "hoja de 7.47 m²" | Entra en la descripción (clave) del catálogo |
| Descripciones de materiales con pulgadas decimales (`0.5"`, `OD 21,3 mm`) y diámetros del índice de proyectos ("0.5 0.625 0.75") | Son claves de búsqueda o listas que lee el código. `catalogo_codigos.csv` mezcla `0.75"` (clave) con "1,6" (tal cual vino) |
| Citas y textos originales (`cita`, `texto_original`, descripciones de `lista_materiales_plano.csv`, "Chapa Ø53" × 3.2 m") | Copia literal del documento: es la prueba de dónde salió el dato |
| Números con 3 decimales en notas escritas a mano ("1.050", "7.850 kg/m3", "6.000 mm") | En formato argentino ya son miles y en casi todos los casos eso es lo correcto. Solo se convirtieron los que por contexto son decimales sin duda: pesos en kg y espesores en pulgadas de tablas ("4.808 kg" → "4,808 kg", 451 celdas), factor de densidad del inoxidable (42) y dos factores de horas en las Camuzzi ("× 1.648") |
| Auditorías e informe de errores (`auditorias/*.md`, `errores_y_lecciones.md`) | Son registro histórico; varios citan a propósito el formato inglés para explicar el error |
| Fichas de `fichas_2025/2026` (texto extraído por IA) | Fuente de extracción; solo se redondeó el precio con 16 decimales |
| Pos como texto en los Excel | Es una etiqueta ("14b", "A"); un número en esa columna desordena el filtro. Si Matías prefiere los pos numéricos, se cambia en `celda_excel` |
| `precotizacion.md` y `cotizacion_auto.json` de las Camuzzi, YPF y CTRL | No se regeneraron (el catálogo cambió desde que se hicieron y el contenido cambiaría, no solo el formato): se pasaron a coma en el texto y se redondearon los precios |

## Valores que cambiaron de significado

No apareció ningún precio mal leído (miles tomados como decimales). Se verificaron contra el original los casos dudosos: Cintolo 6,408 USD (lista 29.1, celda `PRECIO USD` = 6.408) y Pluspetrol 349-25 773,552 USD (seguimiento de presupuestos). Lo que sí cambió:

1. **YPF 713 y 708: la estructura pasa de 1,8953 a 1,90 USD/kg** (precio de acero de J. Elejondo, redondeado a 2 decimales). Skid 713: precio unitario 182.148,08 → 182.162,41 (+14,33; total +42,99). Skid 708: 110.291,62 → 110.297,42 (+5,80; total +34,80). Siguen en borrador.
2. **4 materiales nuevos en el catálogo** (AFO-04930 media cupla 3/4" #6000, JUN-04931 espárrago 3/4 × 4 3/4, OTR-04932 terminal de cobre, PER-04933 chapa 1/4 1500 × 6000): el stock tenía "última compra" de 0,0001 USD (basura de pesos viejos); al redondear quedó en 0 y el catálogo usa el precio maestro del stock, que es verosímil (5,97 USD la media cupla).
3. **Tarifas de terceros por magnitud** con 2 decimales: Ledesma manifold 3590 ÷ 224 = 16,03 USD/pulg (antes 16,0268); antorcha 81000 ÷ 24500 = 3,31 USD/kg. Se actualizó `test_catalogo_servicios.py`.
4. Precios chicos por kg o por unidad pierden precisión: 0,0861 → 0,09 USD/kg (referencia descartada), MS Juntas 0,904 → 0,90.

La CAPEX de control no cambió: **7.366,12** (`verificar_todo.py`: TODO OK).

## Para decidir (Matías)
- Precios unitarios chicos (juntas a 0,904, USD/kg de chapa): ¿2 decimales también ahí, o 4 para precios por kg y por pieza menor a 1 USD? Hoy quedó 2 en todo, como se pidió.
- Pos en los Excel: ¿texto (como quedó) o número cuando es solo número?
- Tarifas con rango: ¿pasar a `valor_min`/`valor_max`?
- Claves del catálogo con números en formato de máquina ("Taval (Lista 30 × 0.52)", "hoja de 7.47 m²", detalle de proveedores): ¿migrar las claves (renumera códigos) o dejarlas como están?
