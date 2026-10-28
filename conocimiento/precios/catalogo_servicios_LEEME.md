# Catálogo de mano de obra y servicios de ITT (etapa 1)

Armado el 28/10/2026 siguiendo `herramientas/catalogo_servicios_instrucciones.md`. Es el equivalente del catálogo de materiales, pero para mano de obra propia y de terceros, ensayos, pintura, transporte, ingeniería y otros servicios. **Todo precio está sin IVA, en USD, con fecha, proveedor y ruta de origen.** Estado: borrador, falta que Matías revise una muestra contra los originales.

## Cómo se usa
- Buscar: `python herramientas/buscar_servicio.py "<texto>" [--hoja <rubro>] [--top N]`. Ejemplos: `"soldadura piping por pulgada"`, `"radiografia" --hoja ensayos`, `"flete camion"`.
- Un servicio **con tarifa unitaria** (USD/kg, USD/pulgada, USD/hora, USD/servicio…) se puede aplicar a cualquier equipo. Un **global** (por ejemplo "MO del desgasificador SB-211") vale solo para ese equipo: sirve de referencia para uno parecido, nunca como tarifa.
- Antes de usar un precio en una cotización hay que leer `incluye` / `no incluye`: casi todos los terceros dejan afuera PH, END, pintura, montaje o consumibles, y eso se cotiza aparte.

## Archivos
| Archivo | Qué es |
|---|---|
| `servicios_extraidos.csv` | Paso 1, leído con IA: un renglón por precio, con la cita literal del documento (`texto_original`). Es la única fuente del catálogo. |
| `catalogo_servicios.csv` / `.xlsx` | Paso 2, determinístico: un renglón por servicio, con el último precio confiable. El Excel tiene "Todos" y una hoja por rubro (el nombre de la hoja de ingeniería se acorta a "Ingeniería, calidad, inspección" por el límite de 31 caracteres de Excel). |
| `catalogo_servicios_historial.csv` | Todos los precios, incluidos los descartados, con su estado y nota. |
| `catalogo_servicios_codigos.csv` | Registro de códigos estables (clave → código, p. ej. `SOL-00144`). Un servicio conserva su código aunque se regenere. **No borrar.** |
| `herramientas/catalogo_servicios.py` | Arma el catálogo (`python herramientas/catalogo_servicios.py`; dos corridas dan el mismo CSV). |
| `herramientas/buscar_servicio.py`, `herramientas/test_catalogo_servicios.py` | Buscador y test de regresión. |

## Rubros (hojas)
MO propia · Fabricación y armado (terceros) · Soldadura y piping · Ensayos y END · Pintura y revestimientos · Transporte e izaje · Ingeniería, calidad e inspección · Otros servicios. Ingeniería y Transporte tienen pocos datos (3 y 2 precios): se mantienen como hoja por pedido de las instrucciones, pero todavía no llegan a los 15–20 datos.

## Reglas aplicadas
1. **Sin IVA.** Con IVA se divide por 1,21 o 1,105; "más IVA" y "no dice" se toman como sin IVA (la columna `iva` dice cuál fue).
2. **Pesos a USD** con el promedio mensual del dólar oficial BNA venta (`costos/indices_ajuste.csv`, `dolar_bna`). Si el documento da su propio tipo de cambio, el precio ya viene en USD y ese tipo de cambio queda en `tc_documento`.
3. **Ajuste a hoy** con `indice_local_usd` (costo local en USD), no con el CPI de EE.UU. Un valor con fecha solo de año no se ajusta.
4. **Regla del cepo (decisión de Matías, 28/10/2026):** un valor en USD con fecha anterior al 14/04/2025 cuyo documento **no dice con qué tipo de cambio se calculó** no se usa como precio. Queda en el historial con la nota "descartado: período con cepo, dólar sin aclarar". El último precio es el último valor confiable (posterior al 14/04/2025; o anterior pero con tipo de cambio explícito; o en pesos con fecha). Si no queda ninguno, el renglón queda sin último precio y con la alerta "sin precio confiable: pedir cotización", y el valor descartado se muestra solo como referencia (`referencia_descartada_usd`). Ya no se calcula "cuánto daría con blue".
   - Ejemplo confiable: la planilla de costo de planta oct-2024 (la hoja "Sueldos" muestra TC 997–998,5). Ejemplo descartado: la MO Master (28 USD/pulgada, 28/05/2024), que no dice TC.
   - Un valor sin ninguna fecha no se descarta (no se puede saber), pero lleva la alerta "sin fecha".
5. **Solo se juntan** precios del mismo servicio, misma unidad de tarifa y alcance comparable. Los globales de distinto equipo no se juntan: la clave es rubro + servicio + equipo de referencia + carpeta. El mismo equipo cotizado por varios proveedores sí queda en un solo renglón con historial.
6. **Tarifa unitaria** = precio ÷ magnitud (columna `magnitud` de la extracción, p. ej. "770 kg"). Si el precio ya es por unidad (USD/kg), la tarifa es el precio. `alcance comparable` = "sí" solo si hay tarifa unitaria y un último precio confiable.
7. **Alertas:** sin precio confiable; sin fecha; número ambiguo (`27,200` puede ser 27,2 o 27.200); historial disperso (más de 3×); confianza baja; total tomado como unitario / pesos como USD (tope por unidad o más de 20 veces la mediana); IVA dudoso; valores descartados por cepo.

## Convenciones de la extracción (`servicios_extraidos.csv`)
Columnas de las instrucciones más `tc_documento` (tipo de cambio que figura en el documento; vacío si no dice).
- `fecha`: `AAAA-MM-DD`, o `AAAA-MM` / `AAAA` cuando el documento solo da el mes o el año. Nunca se completa un día.
- `unidad`: `USD/kg`, `USD/pulg-eq` (pulgada de diámetro equivalente soldada), `USD/hora`, `USD/m2`, `USD/placa`, `USD/servicio`, `USD/dia`, `USD/visita`, `USD/viaje`, `USD/persona-mes` o `global`. Un precio en pesos lleva `moneda` ARS y la unidad se escribe igual (se convierte al armar).
- `magnitud`: cantidad con su unidad (`770 kg`, `224 pulg-eq`) solo cuando el documento la da; permite calcular la tarifa de un global.
- `texto_original`: cita literal. El test (`test_catalogo_servicios.py`) verifica que cada cita siga estando en el documento original (`fuentes_originales/ofertas_texto/…`, las planillas `.xlsx` y el PDF de Antonelli).
- Nada se completó de memoria. Lo que el documento no dice quedó vacío o con confianza baja y está explicado en `nota`.

## Fuentes de la etapa 1 y qué quedó afuera
Usadas: planilla de costo de planta oct-2024 (`costo_mo_planta_2024-10.xlsx`: tarifas propias, costo hora por centro, sueldos por persona, benchmarking de Ledesma y VARPAT), Costos MO Master, planilla de costo master (calentadores B PAE), PDF de Antonelli (END, 11/2025), los presupuestos de proveedores de servicios de las carpetas de 2025–2026 (Ledesma, Quesada, Finder, Cormet, Sandri, SEHC, Figueroa, GP, ARSOL, Manchinelli, MCD, Amanci, Suan, Angeletti, CIAR, NEO, Tapigar, Zeziola) y, de `tarifas.csv`, solo los renglones cuyo original no está en el repositorio (marcados confianza baja y "NO VERIFICADO").
Afuera, a propósito:
- `cotizaciones/*/cotizacion.json`: el único ítem no material con `coincide: igual` (soldadura 19,73 USD/pulgada) ya está en la planilla de costo de planta, no se duplicó.
- Precios de materiales con servicio incluido (cortes de chapa con material, barras, metal desplegado, mazos con materiales), válvulas y equipos (Tormene, Danco, EQA, Tapigar calentador): son del catálogo de materiales.
- Cotizaciones cuyo PDF no tiene texto o está ilegible (Ledesma PHOENIX 480 USD, ETFA, Pereira, Quesada JQ-006, Galva Auraria, Sandri 36" y 6,35 mm): sin precio verificable.
- La MO de las planillas de costo renglón por renglón (etapa 2), el precio de venta de TGS 2022 (rango en pesos) y Master II salvo los dos valores de `tarifas.csv`.

## Pendientes y dudas
- Pedir a proveedores los precios que no están extraídos: transporte (Pereira, ETFA, Suan para otros destinos), galvanizado (Galva Auraria, escaneado), calificación de soldadores, inspector, WPS/PQR y dossier: hoy no hay dato.
- Confirmar con Matías qué cubre un "servicio" de Antonelli (jornada, visita o informe): el documento no lo dice.
- Quesada JQ-018 (desgasificador, "5700 por pulgada") y JQ-013 (domos, "por cada los 8 domos") tienen redacción ambigua en el original; quedaron como global y sin tarifa.
- Los valores de MO propia por persona (sueldos) son promedios de octubre 2024 sin cargas sociales: sirven para estimar, no para fijar tarifa.
- Antes de usar el catálogo en una cotización: revisión de una muestra contra los originales (commit y push los hace quien lo revise).
