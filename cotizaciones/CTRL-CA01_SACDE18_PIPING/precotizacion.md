# Precotización automática — CTRL-CA01

Generada por `herramientas/precotizar.py`, sin IA. **Borrador: revisar los SIMILAR, SIN PRECIO, estimados y ⚠ antes de usarla.**
**Resumen:** materiales USD 0,00 por equipo · soldadura y servicios calculados USD 59.498,78 · 0 similares (—) · 0 sin precio (—).


## 1. Materiales

| Pos | Ítem | Resultado | Precio | Fecha y tipo | Diferencias / faltantes |
|---|---|---|---|---|---|
| 1 | Caño con costura biselado (nota 14) 36" | PROVISTO POR EL CLIENTE | 0 | — | cuenta para soldadura, pintura y PH; no se compra |
| 2 | Caño sin costura biselado 36" | PROVISTO POR EL CLIENTE | 0 | — | cuenta para soldadura, pintura y PH; no se compra |
| 3 | Brida WN RF ASME B16.5 36" | PROVISTO POR EL CLIENTE | 0 | — | cuenta para soldadura, pintura y PH; no se compra |
| 4 | Codo 90° MSS-SP-75 36" | PROVISTO POR EL CLIENTE | 0 | — | cuenta para soldadura, pintura y PH; no se compra |
| 5 | Caño sin costura biselado 12" | PROVISTO POR EL CLIENTE | 0 | — | cuenta para soldadura, pintura y PH; no se compra |

## 2. Soldaduras (de la columna de extremos)

**72 juntas a tope de taller + juntas SW y olets = 2.017,41 pulgadas equivalentes** × USD 21,76 (prefabricado por pulgada diametral (tercero) SOL-00143, 2026-04-07) = USD 43.898,78

- pos 1, 2, 5: caño por metro; sus juntas se cuentan en los extremos BW de accesorios y bridas (una junta cada uno)
- pos 1: 27 junta(s) de empalme entre barras de 12 m (325 m) × 36" × 1,0000
- pos 2: 15 junta(s) de empalme entre barras de 12 m (181 m) × 36" × 0,5003
- pos 5: 15 junta(s) de empalme entre barras de 12 m (190 m) × 12" × 0,9234
- pos 3: 10,5 extremo(s) BW de taller (1 por unidad × 7 × 1,5 por el caño) × 36" × 1,0000
- pos 4: 18 extremo(s) BW de taller (2 por unidad × 6 × 1,5 por el caño) × 36" × 1,0000
- +5% por rechazos y reparaciones con RX 100% (parametros.rechazo_pct)

## 3. Servicios calculados

- **Pintura aparte (no va en el total):** 1.711,68 m² × USD 40,00/m² (Granallado y pintura, 2026-03-03) = USD 68.467,16. Cotizarla como ítem aparte por m² (`parametros.pintura_aparte`).
- **Prueba hidráulica:** en el prefabricado va dentro de la pulgada (no se suma aparte).
- **Radiografía 100% y tintas:** 90 placas chicas + 394 grandes + 13,00 servicio(s) de RX + 0,00 de LP por equipo = USD 15.600,00 (Servicio de radiografía (Antonelli) (2025-11; antonelli_end_2025-11)).
  Con las tarifas de Antonelli (11-2025) serían USD 15.600,00: confirmar el proveedor de END con el cliente o la zona.

### Horas de ingeniería, calidad y montaje (estimadas: prefabricado, 36", 1 u, materiales USD 0 por unidad)

- Prefabricado: sin horas de ingeniería (los isométricos los da el cliente) ni de montaje; calidad, data book, movimientos y PH van dentro de la pulgada. Si el pliego pide ingeniería o dossier aparte, cargarlos a mano.

## 4. A completar (no se puede calcular)

**Lo que más mueve el número:** en el caso de control CTRL-F01 (filtro FM2 #300) la radiografía y tinta penetrante fueron el 40% del costo y las horas de ingeniería, calidad y montaje el 16%. No presentar un precio sin completarlas.
- ⚠ **Horas de ingeniería, calidad y montaje:** son estimadas del antecedente más parecido (punto 3): confirmarlas con el detalle de actividades del equipo.
- Armado y montaje (mano de obra de armado roscado o de terceros con el mismo alcance: `buscar_servicio.py`).
- Ingeniería, calidad y dossier · embalaje · flete (kilos en `controles_tablas.md` al armar) · insumos.
- Plazo (camino crítico con `comercial/plazos_proveedores.csv`).
- ⚠ **Repuestos** (puesta en marcha y 2 años, si el pliego los pide), **transporte a destino** y **póliza de caución** (YPF y la mayoría de las licitaciones la piden): no se calculan; en CTRL-TS01 sumaron USD 1.915 por equipo y en CTRL-SK01 la caución USD 459.
