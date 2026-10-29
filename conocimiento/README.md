# Base de conocimiento de cotización — ITT S.A.

Todo lo que se necesita para cotizar, en un solo lugar y con una sola versión vigente. Armada el 27/10/2026 con 34 planillas y documentos internos (2019–2026), el seguimiento de proyectos y **159 cotizaciones** analizadas una por una (93 de 2026 y 66 de 2025). El detalle de cada fuente está en [`fuentes.md`](fuentes.md).

**Empezar por [`estado_y_pendientes.md`](estado_y_pendientes.md)** (qué está hecho, decisiones y pendientes) y **[`RESUMEN.md`](RESUMEN.md)** (factores, costos, plazos y condiciones en una página).

## 1. Cómo se cotiza

| Archivo | Contenido |
|---|---|
| [`guia_cotizacion.md`](guia_cotizacion.md) | **Paso a paso para cotizar un pedido**, con archivos y comandos. Caso modelo: `cotizaciones/COT26-1003-001_CAPEX_OQ8209/bitacora.md` |
| [`procedimiento_cotizacion.md`](procedimiento_cotizacion.md) | **Procedimiento obligatorio** (P1–P10), estados de una cotización y lista de control |
| [`errores_y_lecciones.md`](errores_y_lecciones.md) | Errores detectados en cotizaciones, su causa y la regla que se agregó |
| [`RESUMEN.md`](RESUMEN.md) | Parámetros clave y lista de control antes de enviar una oferta |
| [`reglas_de_calculo.md`](reglas_de_calculo.md) | Cómo se calcula cada rubro (soldadura, END, pintura, estructura, bulonería, venta) y errores conocidos de las planillas viejas |
| [`plazos.md`](plazos.md) | Plazos por familia, atrasos, plazos de materiales, duración de las tareas de taller y regla para cotizar el plazo |
| [`aprendizajes_2026.md`](aprendizajes_2026.md) | 329 observaciones de las cotizaciones de 2026, agrupadas por familia |
| [`aprendizajes_2025.md`](aprendizajes_2025.md) | 228 observaciones de las cotizaciones de 2025, agrupadas por familia |

## 2. Costos y precios

| Archivo | Contenido |
|---|---|
| [`costos/tarifas.csv`](costos/tarifas.csv) | MO, END, pintura y acero en USD, con tipo (costo propio, tercero o usado al cotizar), fecha, fuente y vigencia. **Se mantiene a mano** |
| `costos/indices_ajuste.csv` | Índices mensuales para ajustar precios por inflación: costo local en USD (IPC INDEC ÷ dólar BNA) y CPI de EE.UU., con fuente de cada dato. Se arma con `herramientas/indices_inflacion.py` |
| `costos/costo_hora_planta.csv` | Costo de mano de obra propia por centro de costo (oct-2024): personas, sueldos, indirectos y costo hora |
| `costos/sueldos_2024-10.csv` | Sueldos y cargas sociales por centro de costo (oct-2024), base del costo hora |
| `precios/catalogo_materiales.xlsx` (y `.csv`) | **Catálogo de materiales**: 2.310 materiales en 10 familias, cada una con sus columnas. Último precio de costo **sin IVA**, fecha, proveedor, ruta de origen, unidad, columnas `iva` y `alerta`, precio ajustado a hoy; marca y modelo en válvulas e instrumentos (un renglón por marca). Se consulta con `herramientas/buscar_material.py` (`--marca`) |
| `precios/catalogo_materiales_historial.csv` | Todos los precios de cada material, con fecha, origen y nota |
| `precios/catalogo_servicios.xlsx` (y `.csv`, `_historial.csv`, `_codigos.csv`, `_LEEME.md`) | **Catálogo de mano de obra y servicios**: 146 servicios en 8 hojas (MO propia, fabricación de terceros, soldadura, END, pintura, transporte, ingeniería, otros). Último precio sin IVA, tarifa unitaria (USD/kg, USD/pulg, USD/h…) cuando hay magnitud, incluye / no incluye, alertas, ajuste con el índice de costo local. Se consulta con `herramientas/buscar_servicio.py`. Extracción: `precios/servicios_extraidos.csv` (cita literal de cada precio; scripts en `herramientas/extraccion_servicios/`) |
| `precios/planillas_costo_items.csv` | **Costos renglón por renglón de las planillas de costo 2025–2026** (2.492 renglones de 31 proyectos: materiales, MO y servicios), con cita y ubicación en el original. Alimenta los dos catálogos (`herramientas/unir_planillas_costo.py`) |
| `precios/catalogo_codigos.csv` | Registro fijo de códigos del catálogo (un material conserva su código al regenerar) |
| `costos/dolar_mensual.csv` (y `.xlsx`) | Dólar oficial BNA, mayorista, MEP y blue por mes desde ene-2024: pico, mínimo, promedio, cierre y brecha. **Para convertir: promedio mensual del oficial BNA venta** |
| `precios/indice_precios.csv` | **Índice único de 2.746 precios**, del más reciente al más viejo: cotizaciones de proveedores 2026 y 2025, base de componentes 2025, lista Renard dic-2025 y stock 2024 |
| `precios/proveedores_2026.csv` | 359 cotizaciones de 220 proveedores en 2026, con precio y plazo |
| `precios/proveedores_2025.csv` | 72 cotizaciones de proveedores en 2025, con precio y plazo |
| `precios/precios_componentes.csv` | Base de precios por componente (25 rubros), 2025–2026, con columna `moneda` (hay renglones en pesos) |
| `precios/lista_renar_2025-12.csv` | Lista de cañería de Renard |
| `precios/stock_2024-11.csv` | Stock valorizado: lo que está en stock no se compra y no suma plazo |

## 3. Datos técnicos

| Archivo | Contenido |
|---|---|
| `tecnico/factores_soldadura.csv` | Por DN y schedule: diámetro exterior, espesor, factor, pulgadas equivalentes, desarrollo y placas de RX |
| `tecnico/factores_accesorios.csv` | Factores de olets, injertos y refuerzos |
| `tecnico/esparragos_por_brida.csv` | Medida y cantidad de espárragos por DN y serie |
| `tecnico/perfiles.csv` | kg/m y m²/m de UPN, IPN, IPE, HEA, HEB, UL y W |
| `tecnico/canos_peso_superficie.csv` | Caños por NPS y schedule: kg/m (carbono e inoxidable), m²/m exterior e interior, litros/m (ASME B36.10) |
| `tecnico/bridas_peso.csv`, `accesorios_peso.csv` | Peso por pieza de bridas B16.5 y accesorios B16.9/B16.11, con URL de origen. **Borrador** (ver `pesos_LEEME.md`) |
| [`codificacion/`](codificacion/README.md) | Codificador Taval/ITT (válvulas, materiales, series, extremos, mandos, componentes) y familias de producto |

## 4. Historial comercial

| Archivo | Contenido |
|---|---|
| `comercial/indice_historico.csv` | Carpetas de ofertas **sin ficha** (2021–2024 y las de 2025–2026 que faltan fichar): familia, subtipo, Ø y año estimados, sin precios. El buscador las muestra aparte cuando hay menos de 5 del mismo subtipo |
| `comercial/indice_proyectos.csv` | **Índice de proyectos para buscar antecedentes** (2025–2026 + cotizador): familia, etiquetas, subtipo, Ø del cuerpo en recipientes, diámetros, series, material, unión, ensayos, precio, factor, plazo, resultado y si tiene planilla de costo. Se consulta con `herramientas/buscar_antecedentes.py` |
| `comercial/carpetas_ofertas.csv` | **Índice de las 532 carpetas de cotización** de `Z:\VENTAS\OFERTAS Y LICITACIONES`: cliente, fechas, etapas presentes, si tiene OC y si ya está analizada |
| `comercial/cotizaciones_2026.csv` | 93 cotizaciones de 2026: oferta, monto, costo, factor, plazo, condiciones y resultado |
| `comercial/cotizaciones_2026_items.csv` | 153 ítems ofertados con precio y datos técnicos |
| `fichas_2026/` | Ficha completa de cada cotización de 2026 |
| `comercial/cotizaciones_2025.csv`, `cotizaciones_2025_items.csv`, `fichas_2025/` | 66 cotizaciones de 2025 (277 ítems): misma estructura que las de 2026 |
| `comercial/cotizaciones_2024-2026.csv` | Seguimiento comercial de 284 cotizaciones (monto, estado, probabilidad, factor) |
| `comercial/registro_cotizaciones_2020-2022.csv` | 200 cotizaciones con resultado y motivo de pérdida |
| `comercial/ventas_2022-2023.csv` | Remitos de venta con precio por equipo |
| `comercial/plazos_proyectos.csv` | 57 ítems 2022–2026: OC, entrega comprometida y real, atraso |
| `comercial/plazos_historicos_2019-2024.csv` | 191 proyectos con plazo pedido y entregas reales |
| `comercial/clientes.csv` | Maestro de clientes con código oficial de 4 dígitos |
| `comercial/marcas_aprobadas.csv` (+ `_resumen.md`) | Marcas exigidas o sugeridas por cliente y rubro, con cita. **Borrador**: YPF completo; PAE, Pampa y Pluspetrol parciales |
| `comercial/plazos_proveedores.csv` (+ `_resumen.md`) | Plazo de entrega por rubro y proveedor en días corridos, con cita (154 de 213 verificados). **Borrador** |
| [`auditorias/`](auditorias/) | Informes de auditorías independientes (catálogo de materiales, 27/10/2026) |

## 5. Códigos

- **Oferta:** ITT usa varios formatos: `0-232 22 rev.0` (histórico), `PRES 141 rev. A` y `Presupuesto ITT 0135-000000000152`. **Propuesta para la herramienta:** `COT[AA]-[código cliente]-[NNN] Rev X` (ej. `COT26-0007-001` para Almacenes Petroleros), alineado con el código de proyecto.
- **Proyecto** (cuando llega la OC): `ITT[AA]-[código cliente]-[NV]`, ej. `ITT22-0336-0320` (2022, cliente 0336 = PAE, nota de venta 320). Cada proyecto tiene además una **OP** (orden de producción) y una **NV** (nota de venta).
- **Familia de producto:** `codificacion/familias_producto.csv` (C calentadores, SEP separadores, F filtros, SK skids, M manifolds, CO colectores, P puentes, CA cañería, T tanques, TS trampas, V válvulas…).
- **Resultado:** ganada · perdida por precio · por técnica · por plazo · por otros motivos · cancelada · sin resultado.

## 6. Proceso comercial de ITT

Según el *Diagrama del Proceso* de ITT (2022):

```
Calificación → Desarrollo → Cotización → Negociación │ Ejecución → Cierre → MRO
└──────────────── Cotizador ITT ────────────────┘    └── se registra costo y plazo real ──┘
```

## 7. Mantenimiento

| Para… | Se hace |
|---|---|
| Actualizar una planilla fuente | Reemplazarla en `fuentes_originales/` (no se sube al repositorio), correr `python herramientas/construir_base.py` y anotar el cambio en `fuentes.md` |
| Analizar un lote nuevo de cotizaciones | `herramientas/extraer_texto.py` (texto de los documentos) → un agente por carpeta con `herramientas/ficha_cotizacion_instrucciones.md` → `herramientas/consolidar_fichas.py` |
| Rehacer el índice de precios | `python herramientas/indice_precios.py` |
| Rearmar toda la base y verificarla | `python herramientas/actualizar_base.py` (dólar, índices, catálogos, índice de proyectos y al final `verificar_todo.py`) |
| Verificar después de cualquier cambio | `python herramientas/verificar_todo.py` → tiene que decir "TODO OK" |
| Rehacer el catálogo de materiales | `python herramientas/catalogo_materiales.py` y después `python herramientas/test_catalogo.py` (tiene que pasar) |
| Actualizar el dólar y los índices de inflación | `python herramientas/dolar_mensual.py` y `python herramientas/indices_inflacion.py` (sumar los datos nuevos de IPC y CPI con su fuente) |
| Leer números o fechas de un documento nuevo | Usar siempre `herramientas/numeros.py` (un solo lector para todo) |
| Cambiar una tarifa | Editar `costos/tarifas.csv` a mano, con fecha y fuente, y marcar la anterior como `vigente = no` |

**Reglas:** una sola versión vigente de cada dato · todo valor con fecha y fuente · el factor lo define la dirección · **no se omite información**: el repositorio es privado y se guardan también contactos y sueldos, porque sirven para costear.
