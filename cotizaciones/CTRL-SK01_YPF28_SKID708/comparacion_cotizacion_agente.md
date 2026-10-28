# Caso de control CTRL-SK01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_agente.json`. Costos por skid, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Caño s/c BW SCH XS A106 Gr.B (323,8 x 12,70)  | 2.3 × 297.75 = 684.83 | 2.3 m × 217.23 + compra extra 1b = 797.23 | +16% | lista · Renard cód. 1201 · 2025-12-26 | más caro |
| 2 | Caño c/c BW API 5L Gr.B (406,4 x 9,52 STD) 16 | 1.7 × 341.24 = 580.11 | 1.7 m × 248.98 + compra extra 2b = 455.63 | -21% | lista · Renard cód. 1212 (tubo s/c 406,4 x 9,52) · 2025-12-26 | más barato (similar) |
| 3 | Tee normal BW SCH XS A234 WPB 12" | 3 × 1,457.38 = 4,372.14 | 3 un × 1,761.90 = 5,285.70 | +21% | est · Cintolo cot. 33764: tee 12" SCH 80 USD 2 · 2026-07-16 | más caro (similar) |
| 4 | Tee de reducción BW SCH STD x XS A234 WPB 16" | 3 × 2,802.34 = 8,407.02 | 3 un × 2,802.34 = 8,407.02 | +0% | lista · Renard cód. 3547 tee red. 16x12 STD · 2025-12-26 | dentro de ±15% |
| 5 | Brida WN RF 300 LB SCH XS A105 12" | 18 × 425.09 = 7,651.62 | 18 un × 218.49 = 3,932.82 | -49% | cot · Complemet (Grupo Provemet) cot. 275397 · 2026-07-06 | más barato |
| 6 | Brida WN RF 300 LB A105 16" | 2 × 680.00 = 1,360.00 | 2 un × 669.20 = 1,338.40 | -2% | est · Renard SO 16" S300 560,29 × (WN/SO 12" S · 2025-12-26 | dentro de ±15% |
| 7 | Brida ciega RF 300 LB A105 12" | 6 × 477.53 = 2,865.18 | 6 un × 257.65 = 1,545.90 | -46% | cot · Complemet cot. 275397 · 2026-07-06 | más barato |
| 8 | Brida ciega RF 300 LB A105 16" | 2 × 820.00 = 1,640.00 | 2 un × 735.42 = 1,470.84 | -10% | est · Renard BL 14" S300 565,71 × (BL 16"/14"  · 2025-12-26 | dentro de ±15% |
| 9 | Brida SW RF 300 LB SCH 80 A105 1 1/2" | 3 × 19.91 = 59.73 | 3 un × 14.88 = 44.64 | -25% | cot · Complemet cot. 275397 · 2026-07-06 | más barato |
| 10 | Espárrago c/2 tuercas 1.25x207 B7/2H zincado | 40 × 12.95 = 518.00 | 40 un × 12.40 = 496.00 | -4% | ant · planilla ITT TECPETROL/13 (1 1/8 x 170 c · 2026-06-26 | dentro de ±15% |
| 11 | Espárrago c/2 tuercas 1.125x186 B7/2H zincado | 288 × 9.59 = 2,761.92 | 288 un × 12.00 = 3,456.00 | +25% | ant · planilla ITT TECPETROL/13: 1 1/8 x 170 m · 2026-06-26 | más caro (similar) · real: 288 = 18 bridas 12" × 16 espárragos (16 × 1 1/8" por brida 12" #300: correcto) |
| 12 | Junta espiralada RF 4,5 mm 300 LB 1 1/2" | 3 × 7.00 = 21.00 | 3 un × 6.00 = 18.00 | -14% | ant · MS (planilla Pampa 7, JUN-02769) · 2026-08-14 | dentro de ±15% |
| 13 | Junta espiralada RF 4,5 mm 300 LB 12" | 18 × 45.00 = 810.00 | 18 un × 9.31 = 167.58 | -79% | cot · MS Juntas cot. 49.323 (ESP SW AC 316LFG  · 2026-08-14 | más barato |
| 14 | Junta espiralada RF 4,5 mm 300 LB 16" | 2 × 80.00 = 160.00 | 2 un × 14.00 = 28.00 | -82% | est · MS 49.323: 10" 7,14 y 12" 9,31 → 16" por · 2026-08-14 | más barato (similar) |
| 15 | Niple s/c NPT SCH 80 L=100 mm 1 1/2" | 3 × 9.00 = 27.00 | 3 un × 5.60 = 16.80 | -38% | stock · Stock ITT ACI040FN1ICK100 · 2024-11-01 | más barato |
| 16 | Niple s/c NPT SCH 80 L=100 mm 1/2" | 1 × 4.00 = 4.00 | 1 un × 4.76 = 4.76 | +19% | stock · Stock ITT ACI015FN1ICK100 · 2024-11-01 | más caro |
| 17 | Niple s/c NPT SCH 80 L=100 mm 3/4" | 1 × 4.50 = 4.50 | 1 un × 5.59 = 5.59 | +24% | stock · Stock ITT ACI020KN1ICK100 (sch 160) · 2024-11-01 | más caro (similar) |
| 18 | Niple s/c NPT SCH 160 L=100 mm 3/4" | 3 × 6.00 = 18.00 | 3 un × 5.59 = 16.77 | -7% | stock · Stock ITT ACI020KN1ICK100 · 2024-11-01 | dentro de ±15% |
| 19 | Tapón NPT cab. hexag. A105 1/2" | 1 × 1.94 = 1.94 | 1 un × 1.38 = 1.38 | -29% | cot · Provemet (AFO-00848) · 2025-08-27 | más barato (similar) |
| 20 | Tapón NPT cab. hexag. A105 3/4" | 2 × 2.30 = 4.60 | 2 un × 2.30 = 4.60 | +0% | ant · planilla ITT 2026-02 (catálogo) · 2026-02-20 | dentro de ±15% |
| 21 | Sockolet SW 3000 LB A105 12"x1 1/2" | 3 × 28.00 = 84.00 | 3 un × 20.00 = 60.00 | -29% | est · sockolet 1/2" S3000 USD 10 (TECHINT/12)  · 2025-12-23 | más barato (similar) |
| 22 | Sockolet SW 3000 LB A105 12"x3/4" | 3 × 14.00 = 42.00 | 3 un × 12.00 = 36.00 | -14% | est · sockolet 1/2" S3000 USD 10 escalado · 2025-12-23 | dentro de ±15% |
| 23 | Sockolet SW 3000 LB A105 16"x3/4" | 1 × 15.00 = 15.00 | 1 un × 12.00 = 12.00 | -20% | est · sockolet 1/2" S3000 USD 10 escalado · 2025-12-23 | más barato (similar) |
| 24 | Sockolet SW 3000 LB A105 16"x1/2" | 1 × 13.00 = 13.00 | 1 un × 10.00 = 10.00 | -23% | ant · planilla ITT TECHINT/12 (sockolet 1/2" 3 · 2025-12-23 | más barato |
| 25 | Válvula esférica 1/2" NPT WOG 2000 PT palanca | 1 × 36.06 = 36.06 | 1 un × 35.88 = 35.88 | -0% | ant · Taval lista 69 × 0,52 · 2026-08-19 | dentro de ±15% |
| 26 | Válvula esférica 3/4" NPT WOG 2000 PT palanca | 4 × 38.80 = 155.20 | 4 un × 39.00 = 156.00 | +1% | ant · Taval lista 75 × 0,52 · 2026-08-19 | dentro de ±15% |
| 27 | Válvula retención clapeta 12" FLG RF 300 LB A | 3 × 3,162.00 = 9,486.00 | 3 un × 3,270.00 = 9,810.00 | +3% | est · Taval: 10" #300 lista 4.500 × 0,52 = 2.3 · 2026-08-19 | dentro de ±15% · real: trim 8 a confirmar |
| 28 | Válvula globo 1/2" NPT 800 LB volante (Taval) | 1 × 35.10 = 35.10 | 1 un × 35.10 = 35.10 | +0% | ant · Taval lista 67,5 × 0,52 · 2026-08-19 | dentro de ±15% · real: API 602 A105 trim 5 |
| 29 | Válvula globo 3/4" NPT 800 LB volante (Taval) | 1 × 40.50 = 40.50 | 1 un × 40.56 = 40.56 | +0% | ant · Taval lista 78 × 0,52 · 2026-08-19 | dentro de ±15% · real: API 602 A105 trim 5 |
| 30 | Válvula esférica 12" FLG RF 300 LB PT volante | 3 × 5,750.00 = 17,250.00 | 3 un × 5,640.00 = 16,920.00 | -2% | est · Taval: 10" #300 lista 7.115 × 0,52 = 3.7 · 2026-08-19 | dentro de ±15% |
| 31 | Bastidor del skid (perfilería) | 850 × 2.00 = 1,700.00 | 850 kg × 1.90 = 1,615.00 | -5% | cot · acero por kg (hierro ángulo 3x1/4 1,72 + · 2026-02-10 | dentro de ±15% · real: la PC0 le aplicó un 20% de overspray (error: es acero, no pintura) |

**Materiales: real USD 60,808.45 · cotizador USD 56,224.21 (-8%).** 15 dentro de ±15%, 16 fuera, 0 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 10,700.00 | 7,594.72 | -29% |
| radiografía y END | 5,000.00 | 2,747.00 | -45% |
| granallado y pintura | 2,360.00 | 2,555.00 | +8% |
| ingeniería, calidad y montaje | 4,117.50 | 2,888.00 | -30% |
| otros | 3,009.20 | 3,850.00 | +28% |

**MO y servicios: real USD 25,186.70 · cotizador USD 19,634.72 (-22%).**

## Total por skid

Real USD 85,995.15 · cotizador USD 75,858.93 (-12%) antes de completar lo que el cotizador marca para revisar.

