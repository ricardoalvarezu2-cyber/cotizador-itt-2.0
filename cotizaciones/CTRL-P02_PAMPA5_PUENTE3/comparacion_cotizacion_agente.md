# Caso de control CTRL-P02: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_agente.json`. Costos por puente, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida API 6A WN RTJ 10K 2 9/16" x 3" sch 40 A | 1 × 312,00 = 312,00 | 1 un × 312,00 = 312,00 | +0% | cot · Francovigh cot. 0001-00093778 rev. 1 · 2026-06-19 | dentro de ±15% |
| 2 | Junta anillo octogonal RTJ-10K BX153 | 1 × 10,00 = 10,00 | 1 un × 6,60 = 6,60 | -34% | cot · Juntas MS cot. 48.445 (RTJ BX153 D) · 2026-06-18 | más barato |
| 3 | Codo 45° RL 3" sch 40 BW A234 WPB | 1 × 12,13 = 12,13 | 1 un × 12,13 = 12,13 | +0% | lista · Renard (cód. 3347) · 2025-12-26 | dentro de ±15% |
| 4 | Sockolet 3" x 3/4" 3000 A105 | 6 × 6,00 = 36,00 | 6 un × 14,00 = 84,00 | +133% | ant · futura/Francovigh (sockolet SW 3000 A105 · 2026-10-10 | más caro (similar) |
| 5 | Caño s/c 3" sch 40 A106 B (tramo 5173 mm) | 1 × 138,97 = 138,97 | 5.173 m × 25,08 + compra extra 5b = 133,95 | -4% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% · real: la planilla compra 7,4 m de caño 3" (0,9 + 5,2 + 1,3 m) a 25,08 = 185,59; aquí van 5,541 m (el tramo de 5,173 m + el sobrante de 0,368 m); los otros tramos van en su posición |
| 6 | Tee reducción 3" sch 40 x 2" sch 80 BW A234 W | 1 × 44,20 = 44,20 | 1 un × 44,20 = 44,20 | +0% | lista · Renard (cód. 3513) · 2025-12-26 | dentro de ±15% |
| 7 | Brida WNRF 2" #300 A105 | 1 × 22,20 = 22,20 | 1 un × 23,95 = 23,95 | +8% | lista · Renard (cód. 12052) · 2025-12-26 | dentro de ±15% · real: la planilla la toma sch 40 ("Considero sch40"); el plano dice sch 80 |
| 8 | Junta espiralada 2" #300 316 + grafito | 2 × 6,00 = 12,00 | 2 un × 2,30 = 4,60 | -62% | cot · Juntas MS cot. 48.445 (ESP SWI AC 316LFG · 2026-06-18 | más barato |
| 9 | Válvula esférica 2" #300 PT RF WCB palanca (f | 1 × 131,13 = 131,13 | 1 un × 136,00 = 136,00 | +4% | lista · Taval lista 30 (BF60503R0104RP): 261,54  · 2025-09-30 | dentro de ±15% · real: va como Válvulas Taval (factor 1) |
| 10 | Brida ciega 2" #300 RF A105 | 1 × 18,50 = 18,50 | 1 un × 18,50 = 18,50 | +0% | lista · Renard (cód. 8252) · 2025-12-26 | dentro de ±15% |
| 11 | Válvula esférica 3/4" NPT WOG 3000 A105 | 9 × 42,04 = 378,38 | 9 un × 43,60 = 392,42 | +4% | lista · Taval lista 30 (forjada A105 3/4" 3000 P · 2025-09-30 | dentro de ±15% · real: va como Válvulas Taval (factor 1); la planilla dice "PR" y anota "P Total" |
| 12 | Niple 3/4" x 100 mm sch 80 PE x NPT | 6 × 10,00 = 60,00 | 6 un × 4,50 = 27,00 | -55% | ant · Niple 3/4" x 100 sch 80 (planilla YPF 28 · 2026-10-10 | más barato |
| 13 | Tapón hexagonal 3/4" NPT 3000 A105 | 3 × 3,50 = 10,50 | 2 un × 2,30 = 4,60 | -56% | lista · Renard (cód. 5980) · 2025-12-26 | más barato · real: la planilla compra 3; el plano pide 2 |
| 14 | Niple 3/4" x 100 mm sch 80 NPT | 3 × 10,00 = 30,00 | 3 un × 4,50 = 13,50 | -55% | ant · Niple 3/4" x 100 sch 80 (planilla YPF 28 · 2026-10-10 | más barato (similar) |
| 15 | Válvula esférica 1" NPT WOG 3000 A105 | 3 × 51,05 = 153,15 | 3 un × 53,22 = 159,67 | +4% | lista · Taval lista 30 (forjada A105 1" 3000 PSI · 2025-09-30 | dentro de ±15% · real: va como Válvulas Taval (factor 1) |
| 16 | Niple 1" x 100 mm sch 80 PE x NPT | 2 × 10,00 = 20,00 | 2 un × 6,00 = 12,00 | -40% | est · Escalado del niple 3/4" x 100 (4,50) por · 2026-10-10 | más barato (similar) |
| 17 | Sockolet 3" x 1" 3000 A105 | 2 × 6,00 = 12,00 | 2 un × 15,00 = 30,00 | +150% | ant · futura/Francovigh (sockolets SW 3000: 12 · 2026-10-10 | más caro (similar) |
| 18 | Tapón hexagonal 1" NPT 3000 A105 | 2 × 3,08 = 6,16 | 2 un × 3,08 = 6,16 | +0% | lista · Renard (cód. 5981) · 2025-12-26 | dentro de ±15% |
| 19 | Thredolet 3" x 3/4" 3000 A105 | 1 × 15,00 = 15,00 | 1 un × 5,00 = 5,00 | -67% | ant · Duralitte threadolet 2" x 1/2" #3000 A10 · 2026-04-22 | más barato (similar) |
| 20 | Buje reducción 3/4" x 1/2" NPT 3000 A105 | 1 × 2,98 = 2,98 | 1 un × 2,98 = 2,98 | +0% | lista · Renard (cód. 5041) · 2025-12-26 | dentro de ±15% |
| 21 | Caño s/c 3" sch 40 A106 B (tramo 258 mm) | 1 × 6,47 = 6,47 | 0,258 m × 25,08 = 6,47 | +0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 22 | Brida WNRF 3" #300 sch 40 A105 | 6 × 40,98 = 245,88 | 8 un × 40,98 = 327,84 | +33% | lista · Renard (cód. 11978) · 2025-12-26 | más caro · real: la planilla compra 6 (1 + 5); el plano pide 8 |
| 23 | Niple 1" x 100 mm sch 80 NPT | 1 × 10,00 = 10,00 | 1 un × 6,00 = 6,00 | -40% | est · Escalado del niple 3/4" x 100 (4,50) por · 2026-10-10 | más barato (similar) |
| 24 | Junta espiralada 3" #300 316 + grafito | 7 × 6,00 = 42,00 | 8 un × 3,98 = 31,84 | -24% | cot · Juntas MS cot. 48.445 (ESP SWI AC 316LFG · 2026-06-18 | más barato · real: la planilla compra 7; el plano pide 8 |
| 25 | Caño s/c 3" sch 40 A106 B (tramo 722 mm) | 1 × 18,11 = 18,11 | 0,722 m × 25,08 = 18,11 | -0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 26 | Válvula esférica 3" #300 PT RF WCB palanca (f | 3 × 246,25 = 738,74 | 3 un × 256,00 = 768,00 | +4% | lista · Taval lista 30 (BF60803R0104RP): 492,31  · 2025-09-30 | dentro de ±15% · real: va como Válvulas Taval (factor 1) |
| 27 | Brida ciega 3" #300 RF A105 | 1 × 36,49 = 36,49 | 1 un × 36,49 = 36,49 | +0% | lista · Renard (cód. 8254) · 2025-12-26 | dentro de ±15% |
| 28 | Caño s/c 3" sch 40 A106 B (tramo 205 mm) | 1 × 5,14 = 5,14 | 0,205 m × 25,08 = 5,14 | +0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 29 | Caño s/c 3" sch 40 A106 B (tramo 215 mm) | 1 × 5,39 = 5,39 | 0,215 m × 25,08 = 5,39 | +0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 30 | Caño s/c 3" sch 40 A106 B (tramo 105 mm) | 1 × 2,63 = 2,63 | 0,105 m × 25,08 = 2,63 | +0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 31 | Tee normal 3" sch 40 BW A234 WPB | 1 × 28,36 = 28,36 | 1 un × 28,36 = 28,36 | +0% | lista · Renard (cód. 3465) · 2025-12-26 | dentro de ±15% |
| 32 | Tuerca hexagonal 5/8" 2H | 32 × 0,00 = 0,00 | 32 un × 0,00 = 0,00 |  | est · Incluida en el espárrago con 2 tuercas ( · 2026-10-28 | SIN PRECIO en el catálogo · real: incluida en el espárrago con 2 tuercas (pos 33) |
| 33 | Espárrago 5/8" x 89 mm B7 con 2 tuercas 2H, z | 16 × 10,00 = 160,00 | 16 un × 3,50 = 56,00 | -65% | est · Escalado por kg desde Ind. Delgado 1 1/8 · 2026-05-28 | más barato (similar) |
| 34 | Tuerca hexagonal 3/4" 2H | 112 × 0,00 = 0,00 | 112 un × 0,00 = 0,00 |  | est · Incluida en el espárrago con 2 tuercas ( · 2026-10-28 | SIN PRECIO en el catálogo · real: incluida en el espárrago con 2 tuercas (pos 37) |
| 35 | Caño s/c 3" sch 40 A106 B (tramo 254 mm) | 1 × 6,37 = 6,37 | 0,254 m × 25,08 = 6,37 | +0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 36 | Caño s/c 3" sch 40 A106 B (tramo 100 mm) | 1 × 2,51 = 2,51 | 0,1 m × 25,08 = 2,51 | -0% | lista · Renard (cód. 1153) · 2025-12-26 | dentro de ±15% |
| 37 | Espárrago 3/4" x 108 mm B7 con 2 tuercas 2H,  | 56 × 10,00 = 560,00 | 56 un × 4,50 = 252,00 | -55% | est · Stock ITT esp. 3/4 x 4 1/4 B7 (3,90) + 2 · 2024-11-01 | más barato (similar) |
| 38 | Transmisor de temperatura ABB (con sensor y v | 1 × 2.205,87 = 2.205,87 | 1 un × 1.492,00 = 1.492,00 | -32% | ant · ABB: TIT integral a sonda 803 + sensor R · 2026-06-25 | más barato (similar) · real: en la planilla va en Instrumentos (factor 1,35); alternativa Rosemount 3.470,06 |
| 39 | Manómetro con manifold | 1 × 0,00 = 0,00 | 1 un × 257,00 = 257,00 |  | ant · Manómetro Weisz 120 (TAVAL/70) + válvula · 2026-06-25 | más barato (similar) · real: la planilla NO lo costea |
| 40 | Transmisor de presión ABB con manifold | 1 × 901,71 = 901,71 | 1 un × 1.001,20 = 1.001,20 | +11% | cot · ABB PGS300 OPP-26-8794766 (864,20) + blo · 2026-07-16 | dentro de ±15% · real: en la planilla va en Instrumentos (factor 1,35); alternativa Rosemount 2.848,53 |

**Materiales: real USD 6.400,97 · cotizador USD 5.732,61 (-10%).** 22 dentro de ±15%, 16 fuera, 2 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 1.300,00 | 1.120,00 | -14% |
| radiografía y END | 841,00 | 1.485,00 | +77% |
| granallado y pintura | 295,00 | 300,00 | +2% |
| ingeniería, calidad y montaje | 0,00 | 246,00 | — |

**MO y servicios: real USD 2.436,00 · cotizador USD 3.151,00 (+29%).**

## Total por puente

Real USD 8.836,97 · cotizador USD 8.883,61 (+1%) antes de completar lo que el cotizador marca para revisar.

