# Base de conocimiento de cotización — ITT S.A.

Todo lo que se necesita para cotizar, en un solo lugar y con una sola versión vigente. Armada el 27/10/2026 con 34 planillas y documentos internos (2019–2026), el seguimiento de proyectos y **93 cotizaciones de 2026** analizadas una por una. El detalle de cada fuente está en [`fuentes.md`](fuentes.md).

**Empezar por [`RESUMEN.md`](RESUMEN.md):** factores, costos, plazos y condiciones en una página.

## 1. Cómo se cotiza

| Archivo | Contenido |
|---|---|
| [`procedimiento_cotizacion.md`](procedimiento_cotizacion.md) | **Procedimiento obligatorio** (P1–P10), estados de una cotización y lista de control |
| [`errores_y_lecciones.md`](errores_y_lecciones.md) | Errores detectados en cotizaciones, su causa y la regla que se agregó |
| [`RESUMEN.md`](RESUMEN.md) | Parámetros clave y lista de control antes de enviar una oferta |
| [`reglas_de_calculo.md`](reglas_de_calculo.md) | Cómo se calcula cada rubro (soldadura, END, pintura, estructura, bulonería, venta) y errores conocidos de las planillas viejas |
| [`plazos.md`](plazos.md) | Plazos por familia, atrasos, plazos de materiales, duración de las tareas de taller y regla para cotizar el plazo |
| [`aprendizajes_2026.md`](aprendizajes_2026.md) | 329 observaciones de las cotizaciones de 2026, agrupadas por familia |

## 2. Costos y precios

| Archivo | Contenido |
|---|---|
| [`costos/tarifas.csv`](costos/tarifas.csv) | MO, END, pintura y acero en USD, con tipo (costo propio, tercero o usado al cotizar), fecha, fuente y vigencia. **Se mantiene a mano** |
| `costos/indices_ajuste.csv` | Índices mensuales para ajustar precios por inflación: costo local en USD (IPC INDEC ÷ dólar BNA) y CPI de EE.UU., con fuente de cada dato. Se arma con `herramientas/indices_inflacion.py` |
| `costos/costo_hora_planta.csv` | Costo de mano de obra propia por centro de costo (oct-2024): personas, sueldos, indirectos y costo hora |
| `costos/sueldos_2024-10.csv` | Sueldos y cargas sociales por centro de costo (oct-2024), base del costo hora |
| `precios/indice_precios.csv` | **Índice único de 2.680 precios**, del más reciente al más viejo: cotizaciones de proveedores 2026, base de componentes 2025, lista Renard dic-2025 y stock 2024 |
| `precios/proveedores_2026.csv` | 359 cotizaciones de 220 proveedores en 2026, con precio y plazo |
| `precios/precios_componentes.csv` | Base de precios por componente (25 rubros), 2025 |
| `precios/lista_renar_2025-12.csv` | Lista de cañería de Renard |
| `precios/stock_2024-11.csv` | Stock valorizado: lo que está en stock no se compra y no suma plazo |

## 3. Datos técnicos

| Archivo | Contenido |
|---|---|
| `tecnico/factores_soldadura.csv` | Por DN y schedule: diámetro exterior, espesor, factor, pulgadas equivalentes, desarrollo y placas de RX |
| `tecnico/factores_accesorios.csv` | Factores de olets, injertos y refuerzos |
| `tecnico/esparragos_por_brida.csv` | Medida y cantidad de espárragos por DN y serie |
| `tecnico/perfiles.csv` | kg/m y m²/m de UPN, IPN, IPE, HEA, HEB, UL y W |
| [`codificacion/`](codificacion/README.md) | Codificador Taval/ITT (válvulas, materiales, series, extremos, mandos, componentes) y familias de producto |

## 4. Historial comercial

| Archivo | Contenido |
|---|---|
| `comercial/carpetas_ofertas.csv` | **Índice de las 532 carpetas de cotización** de `Z:\VENTAS\OFERTAS Y LICITACIONES`: cliente, fechas, etapas presentes, si tiene OC y si ya está analizada |
| `comercial/cotizaciones_2026.csv` | 93 cotizaciones de 2026: oferta, monto, costo, factor, plazo, condiciones y resultado |
| `comercial/cotizaciones_2026_items.csv` | 153 ítems ofertados con precio y datos técnicos |
| `fichas_2026/` | Ficha completa de cada cotización de 2026 |
| `comercial/cotizaciones_2024-2026.csv` | Seguimiento comercial de 284 cotizaciones (monto, estado, probabilidad, factor) |
| `comercial/registro_cotizaciones_2020-2022.csv` | 200 cotizaciones con resultado y motivo de pérdida |
| `comercial/ventas_2022-2023.csv` | Remitos de venta con precio por equipo |
| `comercial/plazos_proyectos.csv` | 57 ítems 2022–2026: OC, entrega comprometida y real, atraso |
| `comercial/plazos_historicos_2019-2024.csv` | 191 proyectos con plazo pedido y entregas reales |
| `comercial/clientes.csv` | Maestro de clientes con código oficial de 4 dígitos |

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
| Cambiar una tarifa | Editar `costos/tarifas.csv` a mano, con fecha y fuente, y marcar la anterior como `vigente = no` |

**Reglas:** una sola versión vigente de cada dato · todo valor con fecha y fuente · el factor lo define la dirección · **no se omite información**: el repositorio es privado y se guardan también contactos y sueldos, porque sirven para costear.
