# Precotización automática — CTRL-M01

Generada por `herramientas/precotizar.py`, sin IA. **Borrador: revisar los SIMILAR, SIN PRECIO, estimados y ⚠ antes de usarla.**
**Resumen:** materiales USD 20.952,40 por equipo · soldadura y servicios calculados USD 13.150,89 · 7 similares (6, 7, 10, 12, 13, 14, 15) · 1 sin precio (5).


## 1. Materiales

| Pos | Ítem | Resultado | Precio | Fecha y tipo | Diferencias / faltantes |
|---|---|---|---|---|---|
| 1 | Brida WN RF 4" | IGUAL | 120,00 / un | 2026-02-19 · planilla interna | — |
| 2 | Brida WN RF 8" | IGUAL | 176,58 / un | 2025-08-27 · cotización | — |
| 3 | Caño sin costura 4" | IGUAL | 47,60 / m | 2026-02-19 · planilla interna | — |
| 4 | Caño sin costura 8" | IGUAL | 137,79 / m | 2025-12-26 · lista | — |
| 5 | Drip ring 4" | **SIN PRECIO** | — | — | pedir cotización |
| 6 | Espárrago con 2 tuercas 7/8 x 100 mm 7/8" | SIMILAR | 8,00 / un | 2026-06-26 · planilla interna | medida: 7/8 x 5 3/4 (pedido 7/8 x 3 7/8) · faltan: material |
| 7 | Espárrago con 2 tuercas 7/8 x 140 mm 7/8" | SIMILAR | 8,00 / un | 2026-06-26 · planilla interna | medida: 7/8 x 5 3/4 (pedido 7/8 x 5 1/2) · faltan: material |
| 8 | Junta espiralada 4" | IGUAL | 5,56 / un | 2026-02-19 · planilla interna | — |
| 9 | Niple longitud 100 mm 1/2" | IGUAL ⚠ | 5,00 / un | 2026-10-10 · planilla interna | — |
| 10 | Sockolet 1/2" | SIMILAR (estimado cepo) ⚠ | 8,49 / un | 2025-03-27 · estimado (cepo) | diametro: 0.75" (pedido 0.5"); material: sin dato (pedido A105); extremos: sin dato (pedido SW/BW); precio esc |
| 11 | Tapón roscado 1/2" | IGUAL | 1,90 / un | 2025-12-26 · lista | — |
| 12 | Tee normal 4" | SIMILAR | 85,18 / un | 2025-12-26 · lista | material: A234 WPB (no pedido) · faltan: material |
| 13 | Tee de reducción 8" x 4" | SIMILAR | 465,34 / un | 2025-12-26 · lista | material: A234 WPB (no pedido) · faltan: material |
| 14 | Perfil UPN 140 (bastidor) | ESTIMADO (por kg) | USD 30.32/m | 2026-02-10 | 16 kg/m (perfiles.csv) × USD 1.90/kg; precio por kg de materia prima (hierro ángulo 3x1/4) +10% por recortes;  |
| 15 | Válvula esférica 1/2" | SIMILAR | 36,06 / un | 2025-09-01 · lista | paso: total (no pedido) · faltan: paso |
| 16 | Válvula esférica paso total 4" | IGUAL | 1.050,00 / un | 2025-09-01 · lista | — |
| 17 | Válvula de retención 4" | IGUAL | 690,04 / un | 2026-02-19 · planilla interna | — |
| 3b | Completar barra de 12 m (pos 3) | compra extra | USD 47.60/m × 0,286 m | | Se usan 112 m en 28 equipo(s) y se compran 120 m. Borrar si hay sobrante en stock |
| 4b | Completar barra de 12 m (pos 4) | compra extra | USD 137.79/m × 0,143 m | | Se usan 56 m en 28 equipo(s) y se compran 60 m. Borrar si hay sobrante en stock |

## 2. Soldaduras (de la columna de extremos)

**51 juntas a tope de taller + juntas SW y olets = 347,57 pulgadas equivalentes** × USD 16,00 (Mano de obra soldadura piping (criterio de las planillas de costo 2026), 2026-02) = USD 5.561,07

- pos 3, 4: caño por metro; sus juntas se cuentan en los extremos BW de accesorios y bridas (una junta cada uno)
- pos 1: 45 extremo(s) BW de taller (1 por unidad × 30 × 1,5 por el caño) × 4" × 1,4219
- pos 2: 3 extremo(s) BW de taller (1 por unidad × 2 × 1,5 por el caño) × 8" × 1,5526
- pos 10: 8 junta(s) de Sockolet sobre caño × 0.5" × 1,75 = 7,00
- pos 12: 36 extremo(s) BW de taller (3 por unidad × 8 × 1,5 por el caño) × 4" × 1,4219
- pos 13: 18 extremo(s) BW de taller (3 por unidad × 4 × 1,5 por el caño) × 10.1764" × 1,0000

## 3. Servicios calculados

- **Pintura:** 23,46 m² (caños y niples 2,9 + bridas, accesorios y válvulas (largo equivalente) 8,1 + estructura 12,5) × USD 7.51/m² (Pintura MO propia (por m2), ITT (costo propio de planta), 2024-10-31) = USD 176,27.
- **Fabricación de la estructura:** 384 kg × USD 1.9/kg (Mano de obra estructura (tercero Ledesma), 2024-09) = USD 729,60.
- **Prueba hidráulica:** 27 h × USD 13.00/h (Prueba hidráulica Desgacificador Alivios, 2025-09-05) = USD 351,00 · volumen interior de caños y niples 88,7 l.
- **Radiografía 100% y tintas:** 164 placas chicas + 0 grandes + 4,11 servicio(s) de RX + 0,29 de LP por equipo = USD 4.612,50 (Servicio de radiografía (Antonelli) (2025-11; antonelli_end_2025-11)).
  Con las tarifas de Antonelli (11-2025) serían USD 4.612,50: confirmar el proveedor de END con el cliente o la zona.

### Horas de ingeniería, calidad y montaje (estimadas: manifold, 8", 28 u, materiales USD 20,952 por unidad)

- **Ingeniería:** 6,29 h × USD 15/h = USD 94,35 · mediana de 1,0, 7,1, 6,3 h por unidad (repartidas en la serie) · antecedente: Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL · Skid para bomba P-111 (SK-2111) (6, 1 u, 2026-02-20)
- **Calidad y dossier:** 2,5 h × USD 15/h = USD 37,50 · mediana de 2,5, 3,2, 2,2 h por unidad (repartidas en la serie) · antecedente: Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL · Skid para bomba P-111 (SK-2111) (6, 1 u, 2026-02-20)
- **Montaje en planta (armado, movimientos, prueba hidráulica):** 149,2 h × USD 13/h = USD 1.939,60 · mediana de 135 h × 1.105, 535,5 h × 0,893, 30 h × 1.994 (horas por unidad × tamaño) · antecedente: Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL · Skid para bomba P-111 (SK-2111) (6, 1 u, 2026-02-20)
- ⚠ No hay antecedente del mismo tipo: se usaron equipos afines del mismo grupo. Revisar las horas.
- La prueba hidráulica va dentro del montaje del antecedente: se sacó la fila PH para no cobrarla dos veces.
- Candidatos: Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL · Skid para bomba P-111 (SK-2111) (6, 1 u, 2026-02-20) | Sacde/14- 3029 RDA - SE-CPF-062_ SKID VALVULA Y BOMBA TK CONICO · Skid valvula y bomba para TK-1839 (TK conico) (4 (sch 40; tambien 3,2), 1 u, 2026-02-10) | TAVAL/43- YPF- CM PUENTES DE PRODUCCION · Puente de produccion 4in #600 (serie de 13 unidades) (4, 13 u, 2026-02-19)

## 4. A completar (no se puede calcular)

**Lo que más mueve el número:** en el caso de control CTRL-F01 (filtro FM2 #300) la radiografía y tinta penetrante fueron el 40% del costo y las horas de ingeniería, calidad y montaje el 16%. No presentar un precio sin completarlas.
- ⚠ **Horas de ingeniería, calidad y montaje:** son estimadas del antecedente más parecido (punto 3): confirmarlas con el detalle de actividades del equipo.
- Armado y montaje (mano de obra de armado roscado o de terceros con el mismo alcance: `buscar_servicio.py`).
- Ingeniería, calidad y dossier · embalaje · flete (kilos en `controles_tablas.md` al armar) · insumos.
- Plazo (camino crítico con `comercial/plazos_proveedores.csv`).
- ⚠ **Repuestos** (puesta en marcha y 2 años, si el pliego los pide), **transporte a destino** y **póliza de caución** (YPF y la mayoría de las licitaciones la piden): no se calculan; en CTRL-TS01 sumaron USD 1.915 por equipo y en CTRL-SK01 la caución USD 459.
