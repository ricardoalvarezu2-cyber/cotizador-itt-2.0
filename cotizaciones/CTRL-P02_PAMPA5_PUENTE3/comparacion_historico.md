# Caso de control CTRL-P02: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_auto.json`. Costos por puente, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida API 6A WN RTJ 10K 2 9/16" x 3" sch 40 A | 1 × 312,00 = 312,00 | 1 un × 312,00 = 312,00 | 0% | cot · Francovigh S.A. · BRI-01338 · 2026-06-19 | dentro de ±15% |
| 2 | Junta anillo octogonal RTJ-10K BX153 | 1 × 10,00 = 10,00 | 1 un × 6,60 = 6,60 | -34% | cot · Juntas MS · JUN-03463 · 2026-06-18 | más barato (similar) |
| 3 | Codo 45° RL 3" sch 40 BW A234 WPB | 1 × 12,13 = 12,13 | 1 un × 17,49 = 17,49 | +44% | cot · Cintolo cot 11/02/26 · ABW-00064 · 2026-02-11 | más caro |
| 4 | Sockolet 3" x 3/4" 3000 A105 | 6 × 6,00 = 36,00 | 6 un × 0,73 = 4,38 | -88% | cot · planilla de costo ITT (proveedor sin nom · 2026-10-30 | más barato (similar) |
| 5 | Caño s/c 3" sch 40 A106 B (tramo 5173 mm) | 1 × 138,97 = 138,97 | 5,17 m × 25,08 = 129,74 | -7% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% · real: la planilla compra 7,4 m de caño 3" (0,9 + 5,2 + 1,3 m) a 25,08 = 185,59; aquí van 5,541 m (el tramo de 5,173 m + el sobrante de 0,368 m); los otros tramos van en su posición |
| 6 | Tee reducción 3" sch 40 x 2" sch 80 BW A234 W | 1 × 44,20 = 44,20 | 1 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-25 | SIN PRECIO en el catálogo |
| 7 | Brida WNRF 2" #300 A105 | 1 × 22,20 = 22,20 | 1 un × 12,47 = 12,47 | -44% | cot · Oil Metal (cód. AC0200BWN2R505) · BRI-01 · 2026-10-30 | más barato · real: la planilla la toma sch 40 ("Considero sch40"); el plano dice sch 80 |
| 8 | Junta espiralada 2" #300 316 + grafito | 2 × 6,00 = 12,00 | 2 un × 4,32 = 8,64 | -28% | cot · Oil Metal (cód. JUE0300CWI3060) · JUN-02 · 2026-10-30 | más barato (similar) |
| 9 | Válvula esférica 2" #300 PT RF WCB palanca (f | 1 × 131,13 = 131,13 | 1 un × 170,30 = 170,30 | +30% | ant · Válvulas Taval (s/listado de Valv.) · VA · 2025-12-10 | más caro (similar) · real: va como Válvulas Taval (factor 1) |
| 10 | Brida ciega 2" #300 RF A105 | 1 × 18,50 = 18,50 | 1 un × 18,50 = 18,50 | 0% | lista · Renard (cód. 8252) · BRI-01031 · 2025-12-26 | dentro de ±15% |
| 11 | Válvula esférica 3/4" NPT WOG 3000 A105 | 9 × 42,04 = 378,38 | 9 un × 43,60 = 392,40 | +4% | lista · Taval (Lista 30 × 0.52) · VAL-04878 · 2025-09-01 | dentro de ±15% · real: va como Válvulas Taval (factor 1); la planilla dice "PR" y anota "P Total" |
| 12 | Niple 3/4" x 100 mm sch 80 PE x NPT | 6 × 10,00 = 60,00 | 6 un × 36,74 = 220,44 | +267% | ant · Antecedentes puentes Taval/CGC s2000 · N · 2026-04-22 | más caro (similar) |
| 13 | Tapón hexagonal 3/4" NPT 3000 A105 | 3 × 3,50 = 10,50 | 2 un × 2,30 = 4,60 | -56% | lista · Renard (cód. 5980) · AFO-00850 · 2025-12-26 | más barato · real: la planilla compra 3; el plano pide 2 |
| 14 | Niple 3/4" x 100 mm sch 80 NPT | 3 × 10,00 = 30,00 | 3 un × 36,74 = 110,22 | +267% | ant · Antecedentes puentes Taval/CGC s2000 · N · 2026-04-22 | más caro (similar) |
| 15 | Válvula esférica 1" NPT WOG 3000 A105 | 3 × 51,05 = 153,15 | 3 un × 53,22 = 159,66 | +4% | lista · Taval (Lista 30 × 0.52) · VAL-04887 · 2025-09-01 | dentro de ±15% · real: va como Válvulas Taval (factor 1) |
| 16 | Niple 1" x 100 mm sch 80 PE x NPT | 2 × 10,00 = 20,00 | 2 un × 4,44 = 8,88 | -56% | cot · Oil Metal (cód. NP0150NN0100806) · NIP-0 · 2026-10-30 | más barato (similar) |
| 17 | Sockolet 3" x 1" 3000 A105 | 2 × 6,00 = 12,00 | 2 un × 1,12 = 2,24 | -81% | cot · planilla de costo ITT (proveedor sin nom · 2026-10-30 | más barato (similar) |
| 18 | Tapón hexagonal 1" NPT 3000 A105 | 2 × 3,08 = 6,16 | 2 un × 3,08 = 6,16 | 0% | lista · Renard (cód. 5981) · AFO-00853 · 2025-12-26 | dentro de ±15% |
| 19 | Thredolet 3" x 3/4" 3000 A105 | 1 × 15,00 = 15,00 | 1 un × 0,28 = 0,28 | -98% | cot · planilla de costo ITT (proveedor sin nom · 2026-10-30 | más barato (similar) |
| 20 | Buje reducción 3/4" x 1/2" NPT 3000 A105 | 1 × 2,98 = 2,98 | 1 un × 2,98 = 2,98 | 0% | lista · Renard (cód. 5041) · AFO-00604 · 2025-12-26 | dentro de ±15% |
| 21 | Caño s/c 3" sch 40 A106 B (tramo 258 mm) | 1 × 6,47 = 6,47 | 0,26 m × 25,08 = 6,47 | +0% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% |
| 22 | Brida WNRF 3" #300 sch 40 A105 | 6 × 40,98 = 245,88 | 8 un × 40,98 = 327,84 | +33% | lista · Renard (cód. 11978) · BRI-01282 · 2025-12-26 | más caro · real: la planilla compra 6 (1 + 5); el plano pide 8 |
| 23 | Niple 1" x 100 mm sch 80 NPT | 1 × 10,00 = 10,00 | 1 un × 4,44 = 4,44 | -56% | cot · Oil Metal (cód. NP0150NN0100806) · NIP-0 · 2026-10-30 | más barato (similar) |
| 24 | Junta espiralada 3" #300 316 + grafito | 7 × 6,00 = 42,00 | 8 un × 4,32 = 34,56 | -18% | cot · Oil Metal (cód. JUE0300CWI3060) · JUN-02 · 2026-10-30 | más barato (similar) · real: la planilla compra 7; el plano pide 8 |
| 25 | Caño s/c 3" sch 40 A106 B (tramo 722 mm) | 1 × 18,11 = 18,11 | 0,72 m × 25,08 = 18,11 | 0% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% |
| 26 | Válvula esférica 3" #300 PT RF WCB palanca (f | 3 × 246,25 = 738,74 | 3 un × 256,00 = 768,00 | +4% | lista · Taval (Lista 30 × 0.52) · VAL-04457 · 2025-09-01 | dentro de ±15% · real: va como Válvulas Taval (factor 1) |
| 27 | Brida ciega 3" #300 RF A105 | 1 × 36,49 = 36,49 | 1 un × 24,60 = 24,60 | -33% | cot · Oil Metal (cód. AC0300BCI2R305) · BRI-01 · 2026-10-30 | más barato |
| 28 | Caño s/c 3" sch 40 A106 B (tramo 205 mm) | 1 × 5,14 = 5,14 | 0,2 m × 25,08 = 5,14 | +0% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% |
| 29 | Caño s/c 3" sch 40 A106 B (tramo 215 mm) | 1 × 5,39 = 5,39 | 0,21 m × 25,08 = 5,39 | +0% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% |
| 30 | Caño s/c 3" sch 40 A106 B (tramo 105 mm) | 1 × 2,63 = 2,63 | 0,1 m × 25,08 = 2,63 | +0% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% |
| 31 | Tee normal 3" sch 40 BW A234 WPB | 1 × 28,36 = 28,36 | 1 un × 28,36 = 28,36 | 0% | lista · Renard (cód. 3465) · ABW-00394 · 2025-12-26 | dentro de ±15% |
| 32 | Tuerca hexagonal 5/8" 2H | 32 × 0,00 = 0,00 | 32 un × 0,00 = 0,00 |  | cot · Incluidas en el precio del espárrago · 2026-10-28 | incluido en otra posición · real: incluida en el espárrago con 2 tuercas (pos 33) |
| 33 | Espárrago 5/8" x 89 mm B7 con 2 tuercas 2H, z | 16 × 10,00 = 160,00 | 16 un × 1,04 = 16,64 | -90% | cot · Oil Metal (cód. ESP0158ZC090193) · JUN-0 · 2026-10-30 | más barato (similar) |
| 34 | Tuerca hexagonal 3/4" 2H | 112 × 0,00 = 0,00 | 112 un × 0,00 = 0,00 |  | cot · Incluidas en el precio del espárrago · 2026-10-28 | incluido en otra posición · real: incluida en el espárrago con 2 tuercas (pos 37) |
| 35 | Caño s/c 3" sch 40 A106 B (tramo 254 mm) | 1 × 6,37 = 6,37 | 0,25 m × 25,08 = 6,37 | +0% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% |
| 36 | Caño s/c 3" sch 40 A106 B (tramo 100 mm) | 1 × 2,51 = 2,51 | 0,1 m × 25,08 + compra extra 36b = 6,72 | +168% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 37 | Espárrago 3/4" x 108 mm B7 con 2 tuercas 2H,  | 56 × 10,00 = 560,00 | 56 un × 5,00 = 280,00 | -50% | ant · marca/proveedor: BULES S.R.L. · JUN-0417 · 2026-01-15 | más barato (similar) |
| 38 | Transmisor de temperatura ABB (con sensor y v | 1 × 2.205,87 = 2.205,87 | 1 un × 803,00 = 803,00 | -64% | ant · planilla de costo ITT · INS-02677 · 2026-06-25 | más barato (similar) · real: en la planilla va en Instrumentos (factor 1,35); alternativa Rosemount 3.470,06 |
| 39 | Manómetro con manifold | 1 × 0,00 = 0,00 | 1 un × 120,00 = 120,00 |  | cot · Weisz · INS-04947 · 2026-10-30 | más barato (similar) · real: la planilla NO lo costea |
| 40 | Transmisor de presión ABB con manifold | 1 × 901,71 = 901,71 | 1 un × 856,62 = 856,62 | -5% | cot · ABB · INS-05103 · 2026-11-05 | dentro de ±15% · real: en la planilla va en Instrumentos (factor 1,35); alternativa Rosemount 2.848,53 |

**Materiales: real USD 6.400,97 · cotizador USD 4.902,88 (-23%).** 18 dentro de ±15%, 21 fuera, 1 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 1.300,00 | 1.198,34 | -8% |
| radiografía y END | 841,00 | 1.666,00 | +98% |
| granallado y pintura | 295,00 | 184,50 | -37% |
| prueba hidráulica | 0,00 | 52,00 | — |
| ingeniería, calidad y montaje | 0,00 | 902,10 | — |

**MO y servicios: real USD 2.436,00 · cotizador USD 4.002,94 (+64%).**

## Total por puente

Real USD 8.836,97 · cotizador USD 8.905,81 (+1%) antes de completar lo que el cotizador marca para revisar.

