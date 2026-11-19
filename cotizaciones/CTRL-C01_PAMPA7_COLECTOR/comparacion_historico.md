# Caso de control CTRL-C01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_auto.json`. Costos por colector, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida WNRF 6" #300 sch 40 A105 | 4 × 114,39 = 457,56 | 4 un × 114,39 = 457,56 | 0% | lista · Renard (cód. 11981) · BRI-01317 · 2025-12-26 | dentro de ±15% |
| 2 | Brida WNRF 3" #300 sch 40 A105 | 40 × 40,98 = 1.639,20 | 40 un × 40,98 = 1.639,20 | 0% | lista · Renard (cód. 11978) · BRI-01282 · 2025-12-26 | dentro de ±15% |
| 3 | Brida WNRF 2" #300 sch 80 A105 | 6 × 23,95 = 143,70 | 6 un × 12,47 = 74,82 | -48% | cot · Oil Metal (cód. AC0200BWN2R505) · BRI-01 · 2026-10-30 | más barato |
| 4 | Brida SWRF 1" #300 sch 80 A105 | 4 × 17,96 = 71,84 | 4 un × 17,96 = 71,84 | 0% | lista · Renard (cód. 10681) · BRI-01153 · 2025-12-26 | dentro de ±15% |
| 5 | Brida ciega RF 1" #300 A105 | 2 × 16,46 = 32,92 | 2 un × 16,46 = 32,92 | 0% | lista · Renard (cód. 8249) · BRI-01010 · 2025-12-26 | dentro de ±15% |
| 6 | Brida ciega RF 2" #300 A105 | 6 × 18,50 = 111,00 | 6 un × 18,50 = 111,00 | 0% | ant · Renard · BRI-01031 · 2026-06-26 | dentro de ±15% |
| 7 | Caño s/c 3" sch 40 A106 B | 6,4 × 25,08 = 160,51 | 6,4 m × 25,08 + compra extra 7b = 167,21 | +4% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% · real: media tira de 12,8 m por colector |
| 8 | Caño s/c 6" sch 40 A106 B | 6,4 × 60,51 = 387,26 | 6,4 m × 49,48 + compra extra 8b = 329,88 | -15% | cot · Grupo Provemet · CAN-01510 · 2026-10-29 | dentro de ±15% · real: media tira de 12,8 m por colector |
| 9 | Niple 3/4" x 150 mm sch 160 A106 B | 17 × 10,00 = 170,00 | 17 un × 7,42 = 126,14 | -26% | cot · Grupo Provemet · NIP-01782 · 2026-11-05 | más barato (similar) |
| 10 | Niple 1" x 150 mm sch 160 A106 B | 1 × 10,00 = 10,00 | 1 un × 11,42 = 11,42 | +14% | cot · Grupo Provemet · NIP-01782 · 2026-11-05 | dentro de ±15% |
| 11 | Junta espiralada 6" #300 316+grafito | 1 × 10,00 = 10,00 | 1 un × 15,00 = 15,00 | +50% | ant · no dice · JUN-01703 · 2025-12-10 | más caro (similar) |
| 12 | Junta espiralada 3" #300 316+grafito | 21 × 8,00 = 168,00 | 21 un × 4,32 = 90,72 | -46% | cot · Oil Metal (cód. JUE0300CWI3060) · JUN-02 · 2026-10-30 | más barato (similar) |
| 13 | Junta espiralada 2" #300 316+grafito | 12 × 6,00 = 72,00 | 12 un × 4,32 = 51,84 | -28% | cot · Oil Metal (cód. JUE0300CWI3060) · JUN-02 · 2026-10-30 | más barato (similar) |
| 14 | Junta espiralada 1" #300 316+grafito | 4 × 5,00 = 20,00 | 4 un × 3,00 = 12,00 | -40% | ant · no dice · JUN-02761 · 2025-12-10 | más barato (similar) |
| 15 | Espárrago 3/4 x 6" B7/2H con tuercas | 12 × 8,00 = 96,00 | 12 un × 1,91 = 22,92 | -76% | cot · Oil Metal (cód. ESP0190ZC120193) · JUN-0 · 2026-10-30 | más barato (similar) |
| 16 | Espárrago 3/4 x 5" B7/2H con tuercas | 168 × 8,00 = 1.344,00 | 168 un × 1,91 = 320,88 | -76% | cot · Oil Metal (cód. ESP0190ZC120193) · JUN-0 · 2026-10-30 | más barato (similar) |
| 17 | Espárrago 5/8 x 4" B7/2H con tuercas | 96 × 8,00 = 768,00 | 96 un × 1,04 = 99,84 | -87% | cot · Oil Metal (cód. ESP0158ZC090193) · JUN-0 · 2026-10-30 | más barato (similar) |
| 18 | Espárrago 5/8 x 3.5" B7/2H con tuercas | 16 × 8,00 = 128,00 | 16 un × 1,04 = 16,64 | -87% | cot · Oil Metal (cód. ESP0158ZC090193) · JUN-0 · 2026-10-30 | más barato (similar) |
| 19 | Tee reducción 3"x2" sch 80 BW WPB | 6 × 64,11 = 384,66 | 6 un × 64,11 = 384,66 | 0% | ant · Renard · ABW-00390 · 2026-06-26 | dentro de ±15% |
| 20 | Tee normal 3" sch 80 BW WPB | 6 × 60,36 = 362,16 | 6 un × 38,72 = 232,32 | -36% | cot · Oil Metal (cód. AC0300-4K280527) · ABW-0 · 2026-10-30 | más barato |
| 21 | Tee reducción 6"x3" sch 40 BW WPB | 6 × 164,91 = 989,46 | 6 un × 164,91 = 989,46 | 0% | ant · Renard · ABW-00413 · 2026-06-26 | dentro de ±15% |
| 22 | Entrerosca 3/4" NPT A105 | 3 × 2,50 = 7,50 | 3 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-19 | SIN PRECIO en el catálogo |
| 23 | Sockolet 3/4" 3000 A105 | 17 × 6,00 = 102,00 | 17 un × 2,33 = 39,61 | -61% | cot · Oil Metal (cód. SOC007508030105) · AFO-0 · 2026-10-30 | más barato (similar) |
| 24 | Sockolet 1" 3000 A105 | 2 × 7,00 = 14,00 | 2 un × 3,59 = 7,18 | -49% | cot · Oil Metal (cód. SOC007508030105) · AFO-0 · 2026-10-30 | más barato (similar) |
| 25 | Tapón hexagonal 3/4" NPT A105 | 17 × 2,50 = 42,50 | 17 un × 2,30 = 39,10 | -8% | ant · Renard · AFO-00850 · 2026-06-26 | dentro de ±15% |
| 26 | Válvula bloqueo y purga 1/2" AISI 316 | 15 × 180,00 = 2.700,00 | 15 un × 137,00 = 2.055,00 | -24% | ant · Abac · VAL-03198 · 2026-04-22 | más barato (similar) |
| 27 | Válvula esférica 3/4" #3000 A105 (Taval stock | 4 × 42,04 = 168,17 | 4 un × 42,04 = 168,16 | 0% | ant · Taval · VAL-03530 · 2026-06-26 | dentro de ±15% · real: Válvulas Taval, factor 1 |
| 28 | Válvula esférica 1" #300 PR BF60253R0144RP | 2 × 67,50 = 135,00 | 2 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-19 | SIN PRECIO en el catálogo · real: Válvulas Taval, factor 1 |
| 29 | Válvula esférica 2" #300 PR BG10503R0104RP | 6 × 131,13 = 786,79 | 6 un × 130,00 = 780,00 | -1% | lista · Taval (Lista 30 × 0.52) · VAL-04444 · 2025-09-01 | dentro de ±15% · real: Válvulas Taval, factor 1 |
| 30 | Válvula retención wafer 3" #300 | 6 × 200,00 = 1.200,00 | 6 un × 301,88 = 1.811,28 | +51% | cot · Taval · VAL-04757 · 2026-10-30 | más caro · real: Válvulas Taval, factor 1 |
| 31 | Válvula esférica 3" #300 3 vías motorizada | 6 × 3.406,00 = 20.436,00 | 6 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-19 | SIN PRECIO en el catálogo · real: las cotizaciones del proyecto dan 3.586,58 (Valvtronic) y 4.378 (Valbol); la OC real fue 4.215,21 |
| 32 | Manómetro | 2 × 120,00 = 240,00 | 2 un × 115,00 = 230,00 | -4% | ant · sin proveedor en planilla (columna PROVE · 2026-02-20 | dentro de ±15% |
| 33 | Transmisor de presión | 1 × 856,63 = 856,63 | 1 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-19 | SIN PRECIO en el catálogo |
| 34 | Bastidor skid (300 + 500 kg con 20% de desper | 960 × 1,50 = 1.440,00 | 800 kg × 1,90 = 1.520,00 | +6% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | dentro de ±15% · real: 800 kg × 1,2 de desperdicio × USD 1,5/kg |
| 35 | Tablero y materiales eléctricos | 1 × 12.000,00 = 12.000,00 | 1 gl × 12.000,00 = 12.000,00 | 0% | ant · planilla de costo ITT · OTR-03018 · 2026-06-26 | dentro de ±15% |

**Materiales: real USD 47.654,86 · cotizador USD 23.908,60 (-50%).** 16 dentro de ±15%, 15 fuera, 4 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 8.350,00 | 5.559,25 | -33% |
| radiografía y END | 4.594,50 | 4.497,50 | -2% |
| granallado y pintura | 4.410,00 | 1.463,20 | -67% |
| ingeniería, calidad y montaje | 1.227,00 | 3.660,40 | +198% |
| otros | 253,66 | 2.400,00 | +846% |

**MO y servicios: real USD 18.835,16 · cotizador USD 17.580,35 (-7%).**

## Total por colector

Real USD 66.490,02 · cotizador USD 41.488,95 (-38%) antes de completar lo que el cotizador marca para revisar.

