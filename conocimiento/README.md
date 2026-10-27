# Base de conocimiento de cotización — ITT S.A.

Todo lo que se necesita para cotizar, en un solo lugar y con una sola versión vigente. La base se armó el 27/10/2026 a partir de 34 archivos de ITT de 2020 a 2026; el detalle de cada uno está en [`fuentes.md`](fuentes.md).

## Estructura

| Carpeta / archivo | Qué contiene | Se usa para |
|---|---|---|
| [`reglas_de_calculo.md`](reglas_de_calculo.md) | Cómo se calcula cada rubro: soldadura, END, pintura, estructura, venta. Errores conocidos | El motor de costo |
| [`costos/tarifas.csv`](costos/tarifas.csv) | Valores en USD de MO, END, pintura y acero, con tipo, fecha, fuente y vigencia | El motor de costo |
| `tecnico/factores_soldadura.csv` | Por DN y schedule: diámetro exterior, espesor, factor, pulg-eq, desarrollo y placas de RX | Pulg-eq, END y pintura |
| `tecnico/factores_accesorios.csv` | Factores de olets, injertos y refuerzos | Pulg-eq |
| `tecnico/esparragos_por_brida.csv` | Medida y cantidad de espárragos por DN y serie | Bulonería |
| `tecnico/perfiles.csv` | kg/m y m²/m de UPN, IPN, IPE, HEA, HEB, UL y W | Estructura y pintura |
| [`codificacion/`](codificacion/README.md) | Codificador Taval/ITT: tipos de válvula, materiales, series, extremos, mandos, componentes; familias de producto | Traducir pedidos a códigos |
| `precios/precios_componentes.csv` | Base de precios por componente (25 rubros) con proveedor, fecha y validez (2025) | Materiales |
| `precios/lista_renar_2025-12.csv` | Lista de cañería de Renard, dic-2025 | Materiales |
| `precios/stock_2024-11.csv` | Stock valorizado: código, cantidad, precio y fecha de última compra | Materiales y plazo (lo que hay en stock no se compra) |
| `comercial/clientes.csv` | Maestro de clientes con código oficial de 4 dígitos | Código de cotización |
| `comercial/registro_cotizaciones_2020-2022.csv` | 200 cotizaciones con familia, precio y resultado (ganada o perdida y por qué) | Histórico y referencia de precios |
| `comercial/ventas_2022-2023.csv` | Remitos de venta con precio unitario por equipo | Control de rango de precios |
| [`plazos.md`](plazos.md) | Plazos de referencia por familia, atrasos, plazos de materiales, duración de tareas de taller y regla para cotizar el plazo | El motor de plazo |
| `comercial/plazos_proyectos.csv` | 57 ítems 2022–2026: fecha de OC, entrega comprometida y real, atraso | El motor de plazo |
| `comercial/plazos_historicos_2019-2024.csv` | 191 proyectos con código ITT, plazo pedido en la OC y entregas reales | El motor de plazo |
| `comercial/cotizaciones_2024-2026.csv` | 284 cotizaciones con monto, estado, probabilidad y factor de venta (sin datos de contacto) | Histórico y seguimiento |

## Reglas de uso

1. **Una sola versión vigente.** Si llega una versión nueva de una fuente, se reemplaza el archivo en `fuentes_originales/`, se corre `python herramientas/construir_base.py` y se anota el cambio en `fuentes.md`. No se editan los CSV generados a mano, salvo `costos/tarifas.csv`, que se mantiene a mano.
2. **Todo valor tiene fecha y fuente.** Si una tarifa tiene más de 6 meses, la cotización tiene que avisarlo.
3. **Tres tipos de valor de MO.** `costo_propio` (lo que le cuesta a ITT), `tercero` (lo que cobra un proveedor) y `usado_en_cotizacion` (lo que se usó históricamente). La cotización tiene que decir cuál usó.
4. **El factor de venta lo define la dirección** en cada cotización. La base solo guarda los valores habituales.
5. **Datos personales fuera.** Los sueldos y los datos de contacto de personas no se cargan en esta base.

## Proceso comercial de ITT

Según el *Diagrama del Proceso* de ITT (2022), la herramienta cubre la gestión comercial y conecta con el cierre a través de la biblioteca:

```
Calificación → Desarrollo → Cotización → Negociación │ Ejecución → Cierre → MRO
   (1) Proyecto   (2) Propuesta   (3) Acuerdo  (4) Aceptación del contrato  (5) Aceptación del cliente  (6) Entrega
└──────────────── Cotizador ITT ────────────────┘                  └── se registra costo y plazo real ──┘
```

## Registro de cotizaciones: códigos

- **Número histórico de presupuesto:** `0-NNNAA` (ej. `0-07420`). **Formato nuevo propuesto:** `COT-[SIGLA]-[AÑO]-[NNN] Rev X`, vinculado al código oficial del cliente.
- **Código de proyecto existente** (cuando llega la OC): `ITT[AA]-[código cliente]-[NV]`. Por ejemplo, `ITT22-0336-0320` = año 2022, cliente 0336 (Pan American Energy), nota de venta 320. Además, cada proyecto tiene una **OP** (orden de producción, ej. 1155) y una **NV** (nota de venta).
- **Familia de producto:** `codificacion/familias_producto.csv` (V válvulas, C calentadores, CA cañería, CO colector, F filtro, M manifold, SK skid, SEP separador, T tanque…).
- **Resultado:** `1` ganada · `0.5` activa · `L1` perdida por precio · `L2` perdida por técnica · `L3` perdida por plazo · `L4` perdida por otros motivos · `C` cancelada.
