# Caso de control CTRL-M01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_agente.json`. Costos por manifold, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida WN 4" S600 Sch.80 A-105 | 30 × 106.00 = 3,180.00 | 30 un × 126.00 = 3,780.00 | +19% | cot · Renard (BRI-01304, historial) · 2025-07-11 | más caro · real: en REV D/E subió a 120,74 |
| 2 | Brida WN 8" S600 Sch.80 A-105 | 2 × 305.43 = 610.86 | 2 un × 176.58 = 353.16 | -42% | cot · Provemet cot. 242356 (BRI-01334) · 2025-08-27 | más barato · real: en REV D/E bajó a 176,80 |
| 3 | Caño SC 4" Sch.80 A-106 | 4 × 57.80 = 231.20 | 4 m × 47.60 + compra extra 3b = 193.78 | -16% | ant · Lista Renar en planilla TAVAL/43 (CAN-01 · 2026-02-19 | más barato · real: LM: tramos 8 × 0,25 + 3,4 + 4 × 0,1; se costean 4 m |
| 4 | Caño SC 8" Sch.80 A-106 | 2 × 165.98 = 331.96 | 2 m × 137.79 + compra extra 4b = 295.28 | -11% | lista · Renard cód. 1183 (CAN-01524) · 2025-12-26 | dentro de ±15% · real: LM: tramo de 2,2 m; se costean 2 m |
| 5 | Drip ring 4" S600 A-516 | 4 × 350.00 = 1,400.00 | 4 un × 180.00 = 720.00 | -49% | est · Estimado del agente (sin antecedente fue · 2026-01-13 | más barato (sin_ref) |
| 6 | Espárragos 7/8" x 100 mm | 160 × 10.00 = 1,600.00 | 160 un × 8.00 = 1,280.00 | -20% | ant · Repuestos, planilla TECPETROL/13 (JUN-02 · 2026-06-26 | más barato (similar) |
| 7 | Espárragos 7/8" x 140 mm | 32 × 10.00 = 320.00 | 32 un × 8.00 = 256.00 | -20% | ant · Repuestos, planilla TECPETROL/13 (JUN-02 · 2026-06-26 | más barato (similar) |
| 8 | Junta espiralada 4" S600 AISI | 28 × 11.00 = 308.00 | 28 un × 5.56 = 155.68 | -49% | ant · MS o Fseal, planilla TAVAL/43 (JUN-02780 · 2026-02-19 | más barato · real: en REV A: 6,35 |
| 9 | Niple 1/2" 100 mm Sch.160 A-106 | 8 × 5.00 = 40.00 | 8 un × 5.00 = 40.00 | +0% | ant · Planilla YPF/28 (NIP-03365) · 2026-10-10 | dentro de ±15% |
| 10 | Sockolet 1/2" S3000 A-105 | 4 × 10.00 = 40.00 | 4 un × 14.00 = 56.00 | +40% | ant · Futura / Francovigh, planilla YPF/28 (AF · 2026-10-10 | más caro (similar) |
| 11 | Tapón 1/2" NPT S3000 A-105 | 8 × 5.00 = 40.00 | 8 un × 1.90 = 15.20 | -62% | lista · Renard cód. 5979 (AFO-00847) · 2025-12-26 | más barato |
| 12 | Te normal 4" Sch.80 A-234 | 8 × 98.00 = 784.00 | 8 un × 85.18 = 681.44 | -13% | lista · Renard cód. 3803 (ABW-00408) · 2025-12-26 | dentro de ±15% |
| 13 | Te red. 8" x 4" Sch.80 A-234 | 4 × 576.00 = 2,304.00 | 4 un × 465.34 = 1,861.36 | -19% | lista · Renard cód. 3848 (ABW-00422) · 2025-12-26 | más barato |
| 14 | UPN 140 | 24 × 23.00 = 552.00 | 24 m × 23.20 = 556.80 | +1% | est · Precio de acero por kg (J. Elejondo) · 2026-02-10 | dentro de ±15% |
| 15 | Válvula esférica 1/2" NPT S3000 A-105 (Taval) | 8 × 65.20 = 521.60 | 8 un × 44.85 = 358.80 | -31% | ant · Válvulas Taval s/listado, planilla TECPE · 2025-12-10 | más barato (similar) · real: lista 97,80 con descuentos (en REV A: 35,88) |
| 16 | Válvula esférica 4" S600 RF PT A-216 (Taval) | 8 × 1,646.30 = 13,170.40 | 8 un × 1,256.00 = 10,048.00 | -24% | est · Taval: 4" #600 RF PR cód. SCJ6R USD 966, · 2026-02-19 | más barato (similar) · real: lista 2.469,45 con descuentos (en REV A: 1.049,88) |
| 17 | Válvula retención 4" S600 RF A-216 (Taval) | 4 × 479.90 = 1,919.60 | 4 un × 690.04 = 2,760.16 | +44% | ant · Válvulas TAVAL −35% −20% sobre lista, pl · 2026-02-19 | más caro · real: lista 719,85 con descuentos (en REV A: 690,04) |

**Materiales: real USD 27,353.62 · cotizador USD 23,411.66 (-14%).** 4 dentro de ±15%, 13 fuera, 0 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 5,321.58 | 5,920.61 | +11% |
| radiografía y END | 5,502.50 | 5,180.00 | -6% |
| granallado y pintura | 523.86 | 1,068.50 | +104% |
| ingeniería, calidad y montaje | 3,711.64 | 3,311.43 | -11% |
| otros | 2,049.02 | 1,770.43 | -14% |

**MO y servicios: real USD 17,108.60 · cotizador USD 17,250.97 (+1%).**

## Total por manifold

Real USD 44,462.22 · cotizador USD 40,662.64 (-9%) antes de completar lo que el cotizador marca para revisar.

