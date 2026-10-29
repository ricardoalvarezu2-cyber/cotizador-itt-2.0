# Caso de control CTRL-P01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_auto.json`. Costos por puente, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida WNRF 3" #600 sch 80 SA-105 | 2 × 19,78 = 39,56 | 2 un × 52,21 = 104,42 | +164% | ant · Cot Elem Equip · BRI-02568 · 2026-03-03 | más caro (similar) |
| 2 | Caño S/C 3" sch 80 SA-106 Gr.B | 4 × 33,93 = 135,72 | 4 m × 30,30 = 121,20 | -11% | ant · no dice · CAN-02638 · 2025-12-10 | dentro de ±15% |
| 3 | Tee reducción 3" x 2" sch 80 BW SA-234 WPB | 2 × 64,11 = 128,22 | 2 un × 64,11 = 128,22 | +0% | ant · Renard · ABW-00390 · 2026-08-14 | dentro de ±15% |
| 4 | Brida WNRF 2" #600 sch 80 SA-105 | 48 × 19,42 = 932,16 | 48 un × 28,42 = 1.364,16 | +46% | ant · Cot Elem Equip · BRI-02568 · 2026-03-03 | más caro (similar) |
| 5 | Tee reducción 2" x 1 1/2" sch 80 BW SA-234 WP | 2 × 33,59 = 67,18 | 2 un × 33,59 = 67,18 | +0% | lista · Renard (cód. 3819) · ABW-00367 · 2025-12-26 | dentro de ±15% |
| 6 | Brida SWRF 1 1/2" #600 sch 160 A105 | 2 × 18,02 = 36,04 | 2 un × 23,36 = 46,72 | +30% | lista · Renard (cód. 10531) · BRI-01159 · 2025-12-26 | más caro (similar) |
| 7 | Válvula esférica 2" #600 WCB (PT flotante) | 8 × 416,00 = 3.328,00 | 10 un × 434,00 = 4.340,00 | +30% | lista · Taval (Lista 30 × 0,52) · VAL-04446 · 2025-09-01 | más caro (similar) · real: REV 1: 8 (la lista de ingeniería dice 10; REV 0: 10 × 400,40); va como Válvulas Taval, factor 1 |
| 8 | Válvula globo 2" #600 limitadora de caudal co | 2 × 8.600,00 = 17.200,00 | 2 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo · real: en la planilla va en Instrumentación; "PEDIR MEJOR OFERTA" |
| 9 | Válvula retención 2" #600 WCB | 2 × 254,00 = 508,00 | 2 un × 120,00 = 240,00 | -53% | lista · Taval (Lista 30 × 0,52) · VAL-04709 · 2025-09-01 | más barato · real: REV 0: 133,67; va como Válvulas Taval |
| 10 | Filtro Y 2" #600 WCB | 2 × 378,00 = 756,00 | 2 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo · real: REV 0: 195,93; va como Válvulas Taval |
| 11 | Junta espiralada 2" #600 316+grafito (48) | 48 × 0,00 = 0,00 | 48 un × 2,30 = 110,40 |  | ant · MS o Fseal · JUN-02771 · 2026-02-19 | más barato (similar) · real: REV 1 la sacó (duplicada con la pos 19); REV 0: 48 × 4 = 192 |
| 12 | Caudalímetro V-Cone en carrete 2" S600 | 2 × 3.180,00 = 6.360,00 | 2 un × 4.200,00 = 8.400,00 | +32% | ant · Krohne (cotización en 5.Proveedores 3ros · 2026-03-10 | más caro (similar) · real: 60 días |
| 13 | Caño S/C 2" sch 80 SA-106 Gr.B | 24 × 16,62 = 398,88 | 24 m × 16,62 = 398,88 | +0% | ant · Renard · CAN-02598 · 2026-08-14 | dentro de ±15% · real: la planilla dice 24 "un" a precio por metro de Renard |
| 14 | Transmisor multivariable DP+P+T 266CSH + mani | 2 × 4.211,76 = 8.423,52 | 1 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo · real: la lista pide 1 computador; REV 0: 1 × 8.577,82 (XFC6200EX) |
| 15 | Inyector de químicos | 2 × 2.100,00 = 4.200,00 | 2 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo · real: la oferta lo EXCLUYE pero la planilla lo costea |
| 16 | Manómetro | 2 × 120,00 = 240,00 | 2 un × 120,00 = 240,00 | +0% | ant · Weisz o similar · INS-02702 · 2026-08-14 | dentro de ±15% · real: REV 1 sin la válvula de bloqueo y purga (REV 0: 2 × 150 Abac) |
| 17 | Sensor RTD + termovaina (4) y transmisor de t | 4 × 1.090,50 = 4.362,00 | 4 un × 1.448,33 = 5.793,32 | +33% | ant · ABB · INS-02714 · 2026-08-14 | más caro (similar) · real: 2 × 689 (FQIT) + 2 × 689 (bypass) + 2 × 803 (TIT); REV 0: 4 × 1.176,57 |
| 18 | Sockolet 1" 3000# SA-105 | 14 × 6,00 = 84,00 | 14 un × 24,00 = 336,04 | +300% | est · no dice · AFO-02394 · 2025-03-27 | más caro (similar) |
| 19 | Junta espiralada 2" #600 316+grafito anillo i | 46 × 8,00 = 368,00 | 46 un × 2,30 = 105,80 | -71% | ant · MS o Fseal · JUN-02771 · 2026-02-19 | más barato (similar) |
| 20 | Espárrago 5/8" x 5" con tuercas | 368 × 8,00 = 2.944,00 | 368 un × 2,50 = 920,00 | -69% | ant · sin proveedor en planilla (columna PROVE · 2026-02-20 | más barato (similar) |
| 21 | Tee normal 2" sch 80 BW SA-234 WPB | 8 × 24,06 = 192,48 | 8 un × 25,00 = 200,00 | +4% | ant · no dice · ABW-00373 · 2026-01-22 | dentro de ±15% |
| 22 | Válvulas chicas (REV 1: esf. 1" #600 ×2, glob | 10 × 44,18 = 441,84 | 16 un × 113,88 = 1.822,08 | +312% | ant · Taval (cotización Comex Taval en 5.Prove · 2026-03-10 | más caro (similar) · real: la lista pide 16 esféricas 1" #3000 (REV 0: 16 × 27,49 = 439,84); va como Válvulas Taval |
| 23 | Materiales de canalizaciones (8000 verdes) | 2 × 0,00 = 0,00 | 2 un × 0,00 = 0,00 |  | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo · real: la planilla no lo costea |
| 24 | Bastidor y soportes SA-36 | 1200 × 1,50 = 1.800,00 | 1050 kg × 1,27 = 1.338,12 | -26% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más barato (similar) · real: REV 1: 1.200 kg (lista 1.050 kg + 20% desperdicio; REV 0: 6.000 kg = 9.000) |
| X1 | U-bolts y tornillería del skid | 200,00 | — | — | — | falta en el cotizador |
| X2 | Manifold de 5 vías | 698,00 | — | — | — | falta en el cotizador |
| X3 | Botellones de purga tomas de presión | 900,00 | — | — | — | falta en el cotizador |

**Materiales: real USD 54.743,60 · cotizador USD 26.076,54 (-52%).** 6 dentro de ±15%, 13 fuera, 5 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 7.200,00 | 4.015,09 | -44% |
| radiografía y END | 2.428,00 | 2.655,50 | +9% |
| granallado y pintura | 2.370,00 | 1.993,45 | -16% |
| prueba hidráulica | 0,00 | 468,00 | — |
| ingeniería, calidad y montaje | 1.818,00 | 810,40 | -55% |
| otros | 0,00 | 3.150,00 | — |

**MO y servicios: real USD 13.816,00 · cotizador USD 13.092,44 (-5%).**

## Total por puente

Real USD 68.559,60 · cotizador USD 39.168,98 (-43%) antes de completar lo que el cotizador marca para revisar.

