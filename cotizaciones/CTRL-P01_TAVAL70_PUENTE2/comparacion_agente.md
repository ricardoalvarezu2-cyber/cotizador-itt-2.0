# Caso de control CTRL-P01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_agente.json`. Costos por puente, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida WNRF 3" #600 sch 80 SA-105 | 2 × 19.78 = 39.56 | 2 un × 52.46 = 104.92 | +165% | est · Renard (cot. elementos 2025-07-11, BRI-0 · 2025-12-26 | más caro (similar) |
| 2 | Caño S/C 3" sch 80 SA-106 Gr.B | 4 × 33.93 = 135.72 | 4 m × 33.93 = 135.72 | +0% | lista · Renard (cód. 1154) · CAN-01486 · 2025-12-26 | dentro de ±15% |
| 3 | Tee reducción 3" x 2" sch 80 BW SA-234 WPB | 2 × 64.11 = 128.22 | 2 un × 64.11 = 128.22 | +0% | ant · Renard · ABW-00390 · 2026-08-14 | dentro de ±15% |
| 4 | Brida WNRF 2" #600 sch 80 SA-105 | 48 × 19.42 = 932.16 | 48 un × 28.42 = 1,364.16 | +46% | cot · RENARD · BRI-01259 · 2025-07-11 | más caro |
| 5 | Tee reducción 2" x 1 1/2" sch 80 BW SA-234 WP | 2 × 33.59 = 67.18 | 2 un × 33.59 = 67.18 | +0% | lista · Renard (cód. 3819) · ABW-00367 · 2025-12-26 | dentro de ±15% |
| 6 | Brida SWRF 1 1/2" #600 sch 160 A105 | 2 × 18.02 = 36.04 | 2 un × 27.72 = 55.44 | +54% | est · Renard (cód. 10531) S300 escalada a #600 · 2025-12-26 | más caro (similar) |
| 7 | Válvula esférica 2" #600 WCB (PT flotante) | 8 × 416.00 = 3,328.00 | 10 un × 416.00 = 4,160.00 | +25% | ant · Válvulas TAVAL (cot. -35% -20% sobre lis · 2026-02-19 | más caro (similar) · real: REV 1: 8 (la lista de ingeniería dice 10; REV 0: 10 × 400,40); va como Válvulas Taval, factor 1 |
| 8 | Válvula globo 2" #600 limitadora de caudal co | 2 × 8,600.00 = 17,200.00 | 2 un × 8,206.00 = 16,412.00 | -5% | cot · Estudio Técnico Doma, presupuesto 6823 ( · 2026-07-16 | dentro de ±15% · real: en la planilla va en Instrumentación; "PEDIR MEJOR OFERTA" |
| 9 | Válvula retención 2" #600 WCB | 2 × 254.00 = 508.00 | 2 un × 255.83 = 511.66 | +1% | est · Válvulas TAVAL 3" (420,16) y 4" (690,04) · 2026-02-19 | dentro de ±15% · real: REV 0: 133,67; va como Válvulas Taval |
| 10 | Filtro Y 2" #600 WCB | 2 × 378.00 = 756.00 | 2 un × 195.30 = 390.60 | -48% | est · OTR-02961 filtro Y 2" #150 WCB (106,14)  · 2026-02-20 | más barato (similar) · real: REV 0: 195,93; va como Válvulas Taval |
| 11 | Junta espiralada 2" #600 316+grafito (48) | 48 × 0.00 = 0.00 | 48 un × 0.00 = 0.00 |  | est · Duplicada con la pos 19 · 2026-10-28 | SIN PRECIO en el catálogo · real: REV 1 la sacó (duplicada con la pos 19); REV 0: 48 × 4 = 192 |
| 12 | Caudalímetro V-Cone en carrete 2" S600 | 2 × 3,180.00 = 6,360.00 | 2 un × 4,200.00 = 8,400.00 | +32% | est · Krohne MRT-W150 (electromagnético) · INS · 2026-03-10 | más caro (similar) · real: 60 días |
| 13 | Caño S/C 2" sch 80 SA-106 Gr.B | 24 × 16.62 = 398.88 | 24 m × 16.62 = 398.88 | +0% | lista · Renard (cód. 1143) · CAN-01463 · 2025-12-26 | dentro de ±15% · real: la planilla dice 24 "un" a precio por metro de Renard |
| 14 | Transmisor multivariable DP+P+T 266CSH + mani | 2 × 4,211.76 = 8,423.52 | 1 un × 7,345.97 = 7,345.97 | -13% | cot · ABB Argentina, cot. OPP-26-8794766 ítem  · 2026-07-16 | dentro de ±15% · real: la lista pide 1 computador; REV 0: 1 × 8.577,82 (XFC6200EX) |
| 15 | Inyector de químicos | 2 × 2,100.00 = 4,200.00 | 2 un × 0.00 = 0.00 | -100% | est · Excluido: la oferta dice 'se excluye el  · 2026-07-14 | SIN PRECIO en el catálogo · real: la oferta lo EXCLUYE pero la planilla lo costea |
| 16 | Manómetro | 2 × 120.00 = 240.00 | 2 un × 300.00 = 600.00 | +150% | ant · Weisz (120) + ABAC bloqueo y purga 1/2"  · 2026-08-14 | más caro (similar) · real: REV 1 sin la válvula de bloqueo y purga (REV 0: 2 × 150 Abac) |
| 17 | Sensor RTD + termovaina (4) y transmisor de t | 4 × 1,090.50 = 4,362.00 | 4 un × 1,448.33 = 5,793.32 | +33% | ant · ABB · INS-02714 'Transmisor de temperatu · 2026-08-14 | más caro (similar) · real: 2 × 689 (FQIT) + 2 × 689 (bypass) + 2 × 803 (TIT); REV 0: 4 × 1.176,57 |
| 18 | Sockolet 1" 3000# SA-105 | 14 × 6.00 = 84.00 | 14 un × 18.00 = 252.00 | +200% | est · futura/francovigh: sockolet 3/4" 14,00 y · 2026-10-10 | más caro (similar) |
| 19 | Junta espiralada 2" #600 316+grafito anillo i | 46 × 8.00 = 368.00 | 46 un × 6.00 = 276.00 | -25% | ant · MS · JUN-02769 (2" 300# 316 4,5 mm c/ani · 2026-08-14 | más barato (similar) |
| 20 | Espárrago 5/8" x 5" con tuercas | 368 × 8.00 = 2,944.00 | 368 un × 10.00 = 3,680.00 | +25% | ant · JUN-02753 espárragos 5/8" L 5" B7 c/2 tu · 2025-12-18 | más caro |
| 21 | Tee normal 2" sch 80 BW SA-234 WPB | 8 × 24.06 = 192.48 | 8 un × 27.89 = 223.12 | +16% | cot · PROVEMET cot. 239607 · ABW-00372 · 2025-08-01 | más caro |
| 22 | Válvulas chicas (REV 1: esf. 1" #600 ×2, glob | 10 × 44.18 = 441.84 | 16 un × 51.05 = 816.80 | +85% | ant · Taval · VAL-03291 (1" WOG 3000 NPT A105) · 2026-08-14 | más caro (similar) · real: la lista pide 16 esféricas 1" #3000 (REV 0: 16 × 27,49 = 439,84); va como Válvulas Taval |
| 23 | Materiales de canalizaciones (8000 verdes) | 2 × 0.00 = 0.00 | 2 un × 4,000.00 = 8,000.00 |  | est · Lista de ingeniería: '8000 VERDES' · 2026-07-14 | más barato (sin_ref) · real: la planilla no lo costea |
| 24 | Bastidor y soportes SA-36 | 1200 × 1.50 = 1,800.00 | 1050 kg × 1.90 = 1,990.07 | +11% | est · Precios de acero (J. Elejondo) · hierro  · 2026-02-10 | dentro de ±15% · real: REV 1: 1.200 kg (lista 1.050 kg + 20% desperdicio; REV 0: 6.000 kg = 9.000) |
| X1 | U-bolts y tornillería del skid | 200.00 | — | — | — | falta en el cotizador |
| X2 | Manifold de 5 vías | 698.00 | — | — | — | falta en el cotizador |
| X3 | Botellones de purga tomas de presión | 900.00 | — | — | — | falta en el cotizador |

**Materiales: real USD 54,743.60 · cotizador USD 61,106.06 (+12%).** 8 dentro de ±15%, 14 fuera, 2 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 7,200.00 | 8,600.00 | +19% |
| radiografía y END | 2,428.00 | 2,884.00 | +19% |
| granallado y pintura | 2,370.00 | 1,700.00 | -28% |
| ingeniería, calidad y montaje | 1,818.00 | 1,851.50 | +2% |

**MO y servicios: real USD 13,816.00 · cotizador USD 15,035.50 (+9%).**

## Total por puente

Real USD 68,559.60 · cotizador USD 76,141.56 (+11%) antes de completar lo que el cotizador marca para revisar.

