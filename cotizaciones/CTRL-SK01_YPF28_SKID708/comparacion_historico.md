# Caso de control CTRL-SK01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_auto.json`. Costos por skid, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Caño s/c BW SCH XS A106 Gr.B (323,8 x 12,70)  | 2.3 × 297.75 = 684.83 | 2.3 m × 217.23 + compra extra 1b = 651.69 | -5% | ant · Renard · CAN-01435 · 2026-06-26 | dentro de ±15% |
| 2 | Caño c/c BW API 5L Gr.B (406,4 x 9,52 STD) 16 | 1.7 × 341.24 = 580.11 | 1.7 m × 133.36 + compra extra 2b = 266.72 | -54% | lista · Renard (cód. 1071) · CAN-01434 · 2025-12-26 | más barato (similar) |
| 3 | Tee normal BW SCH XS A234 WPB 12" | 3 × 1,457.38 = 4,372.14 | 3 un × 962.15 = 2,886.45 | -34% | lista · Renard (cód. 3471) · ABW-00356 · 2025-12-26 | más barato (similar) |
| 4 | Tee de reducción BW SCH STD x XS A234 WPB 16" | 3 × 2,802.34 = 8,407.02 | 3 un × 2,802.34 = 8,407.02 | +0% | lista · Renard (cód. 3547) · ABW-00358 · 2025-12-26 | dentro de ±15% |
| 5 | Brida WN RF 300 LB SCH XS A105 12" | 18 × 425.09 = 7,651.62 | 18 un × 355.68 = 6,402.24 | -16% | lista · Renard (cód. 11984) · BRI-01230 · 2025-12-26 | más barato (similar) |
| 6 | Brida WN RF 300 LB A105 16" | 2 × 680.00 = 1,360.00 | 2 un × 257.80 = 515.60 | -62% | lista · Renard (cód. 11983) · BRI-01224 · 2025-12-26 | más barato (similar) |
| 7 | Brida ciega RF 300 LB A105 12" | 6 × 477.53 = 2,865.18 | 6 un × 426.44 = 2,558.64 | -11% | lista · Renard (cód. 8260) · BRI-01022 · 2025-12-26 | dentro de ±15% |
| 8 | Brida ciega RF 300 LB A105 16" | 2 × 820.00 = 1,640.00 | 2 un × 426.44 = 852.88 | -48% | lista · Renard (cód. 8260) · BRI-01022 · 2025-12-26 | más barato (similar) |
| 9 | Brida SW RF 300 LB SCH 80 A105 1 1/2" | 3 × 19.91 = 59.73 | 3 un × 17.96 = 53.88 | -10% | lista · Renard (cód. 10683) · BRI-01161 · 2025-12-26 | dentro de ±15% |
| 10 | Espárrago c/2 tuercas 1.25x207 B7/2H zincado | 40 × 12.95 = 518.00 | 40 un × 10.00 = 400.00 | -23% | ant · Bules o Versailles · JUN-03364 · 2026-02-19 | más barato (similar) |
| 11 | Espárrago c/2 tuercas 1.125x186 B7/2H zincado | 288 × 9.59 = 2,761.92 | 288 un × 5.00 = 1,440.00 | -48% | ant · marca/proveedor: BULES S.R.L. · JUN-0283 · 2026-01-15 | más barato (similar) · real: 288 = 18 bridas 12" × 16 espárragos (16 × 1 1/8" por brida 12" #300: correcto) |
| 12 | Junta espiralada RF 4,5 mm 300 LB 1 1/2" | 3 × 7.00 = 21.00 | 3 un × 6.00 = 18.00 | -14% | ant · MS · JUN-02769 · 2026-08-14 | dentro de ±15% |
| 13 | Junta espiralada RF 4,5 mm 300 LB 12" | 18 × 45.00 = 810.00 | 18 un × 15.00 = 270.00 | -67% | ant · sin proveedor en planilla · JUN-02765 · 2025-12-18 | más barato (similar) |
| 14 | Junta espiralada RF 4,5 mm 300 LB 16" | 2 × 80.00 = 160.00 | 2 un × 15.00 = 30.00 | -81% | ant · sin proveedor en planilla · JUN-02765 · 2025-12-18 | más barato (similar) |
| 15 | Niple s/c NPT SCH 80 L=100 mm 1 1/2" | 3 × 9.00 = 27.00 | 3 un × 5.60 = 16.80 | -38% | stock · Stock ITT (cód. ACI040FN1ICK100) · NIP-0 · 2024-11-01 | más barato |
| 16 | Niple s/c NPT SCH 80 L=100 mm 1/2" | 1 × 4.00 = 4.00 | 1 un × 20.00 = 20.00 | +400% | ant · Antecedentes puentes Taval/CGC s2000 · N · 2026-04-22 | más caro |
| 17 | Niple s/c NPT SCH 80 L=100 mm 3/4" | 1 × 4.50 = 4.50 | 1 un × 20.00 = 20.00 | +344% | ant · Antecedentes puentes Taval/CGC s2000 · N · 2026-04-22 | más caro (similar) |
| 18 | Niple s/c NPT SCH 160 L=100 mm 3/4" | 3 × 6.00 = 18.00 | 3 un × 5.59 = 16.77 | -7% | stock · Stock ITT (cód. ACI020KN1ICK100) · NIP-0 · 2024-11-01 | dentro de ±15% |
| 19 | Tapón NPT cab. hexag. A105 1/2" | 1 × 1.94 = 1.94 | 1 un × 1.38 = 1.38 | -29% | cot · PROVEMET · AFO-00848 · 2025-08-27 | más barato (similar) |
| 20 | Tapón NPT cab. hexag. A105 3/4" | 2 × 2.30 = 4.60 | 2 un × 2.30 = 4.60 | +0% | ant · sin proveedor en planilla (columna PROVE · 2026-02-20 | dentro de ±15% |
| 21 | Sockolet SW 3000 LB A105 12"x1 1/2" | 3 × 28.00 = 84.00 | 3 un × 0.00 = 0.00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo |
| 22 | Sockolet SW 3000 LB A105 12"x3/4" | 3 × 14.00 = 42.00 | 3 un × 10.00 = 30.00 | -29% | ant · sin proveedor en planilla · AFO-03330 · 2025-12-23 | más barato (similar) |
| 23 | Sockolet SW 3000 LB A105 16"x3/4" | 1 × 15.00 = 15.00 | 1 un × 10.00 = 10.00 | -33% | ant · sin proveedor en planilla · AFO-03330 · 2025-12-23 | más barato (similar) |
| 24 | Sockolet SW 3000 LB A105 16"x1/2" | 1 × 13.00 = 13.00 | 1 un × 10.00 = 10.00 | -23% | ant · sin proveedor en planilla · AFO-03330 · 2025-12-23 | más barato (similar) |
| 25 | Válvula esférica 1/2" NPT WOG 2000 PT palanca | 1 × 36.06 = 36.06 | 1 un × 65.20 = 65.20 | +81% | ant · válvulas Taval (el resumen las agrupa co · 2026-01-26 | más caro (similar) |
| 26 | Válvula esférica 3/4" NPT WOG 2000 PT palanca | 4 × 38.80 = 155.20 | 4 un × 42.04 = 168.17 | +8% | ant · Taval · VAL-03530 · 2026-08-14 | dentro de ±15% |
| 27 | Válvula retención clapeta 12" FLG RF 300 LB A | 3 × 3,162.00 = 9,486.00 | 3 un × 114.00 = 342.00 | -96% | ant · sin proveedor en planilla (columna PROVE · 2026-02-20 | más barato (similar) · real: trim 8 a confirmar |
| 28 | Válvula globo 1/2" NPT 800 LB volante (Taval) | 1 × 35.10 = 35.10 | 1 un × 0.00 = 0.00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo · real: API 602 A105 trim 5 |
| 29 | Válvula globo 3/4" NPT 800 LB volante (Taval) | 1 × 40.50 = 40.50 | 1 un × 80.00 = 80.00 | +98% | ant · sin proveedor en planilla · VAL-03176 · 2025-12-18 | más caro (similar) · real: API 602 A105 trim 5 |
| 30 | Válvula esférica 12" FLG RF 300 LB PT volante | 3 × 5,750.00 = 17,250.00 | 3 un × 4,834.00 = 14,502.00 | -16% | ant · ALT 2 -- VALV WAFER Ø12" S-600 RF WCB IN · 2025-12-18 | más barato (similar) |
| 31 | Bastidor del skid (perfilería) | 850 × 2.00 = 1,700.00 | 850 kg × 1.90 = 1,611.00 | -5% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | dentro de ±15% · real: la PC0 le aplicó un 20% de overspray (error: es acero, no pintura) |

**Materiales: real USD 60,808.45 · cotizador USD 41,651.04 (-32%).** 9 dentro de ±15%, 20 fuera, 2 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 10,700.00 | 6,826.96 | -36% |
| radiografía y END | 5,000.00 | 2,753.00 | -45% |
| granallado y pintura | 2,360.00 | 1,964.50 | -17% |
| ingeniería, calidad y montaje | 4,117.50 | 5,501.15 | +34% |
| otros | 3,009.20 | 2,550.00 | -15% |

**MO y servicios: real USD 25,186.70 · cotizador USD 19,595.61 (-22%).**

## Total por skid

Real USD 85,995.15 · cotizador USD 61,246.65 (-29%) antes de completar lo que el cotizador marca para revisar.

