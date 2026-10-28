# Caso de control CTRL-P02: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_auto.json`. Costos por puente, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Brida API 6A WN RTJ 10K 2 9/16" x 3" sch 40 A | 1 × 312.00 = 312.00 | 1 un × 312.00 = 312.00 | +0% | cot · Francovigh S.A. · BRI-01338 · 2026-06-19 | dentro de ±15% |
| 2 | Junta anillo octogonal RTJ-10K BX153 | 1 × 10.00 = 10.00 | 1 un × 0.00 = 0.00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-10-28 | SIN PRECIO en el catálogo |
| 3 | Codo 45° RL 3" sch 40 BW A234 WPB | 1 × 12.13 = 12.13 | 1 un × 17.49 = 17.49 | +44% | cot · Cintolo cot 11/02/26 · ABW-00064 · 2026-02-11 | más caro |
| 4 | Sockolet 3" x 3/4" 3000 A105 | 6 × 6.00 = 36.00 | 6 un × 10.00 = 60.00 | +67% | ant · sin proveedor en planilla · AFO-03330 · 2025-12-23 | más caro (similar) |
| 5 | Caño s/c 3" sch 40 A106 B (tramo 5173 mm) | 1 × 138.97 = 138.97 | 5.173 m × 25.08 + compra extra 5b = 135.43 | -3% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | dentro de ±15% · real: la planilla compra 7,4 m de caño 3" (0,9 + 5,2 + 1,3 m) a 25,08 = 185,59; aquí van 5,541 m (el tramo de 5,173 m + el sobrante de 0,368 m); los otros tramos van en su posición |
| 6 | Tee reducción 3" sch 40 x 2" sch 80 BW A234 W | 1 × 44.20 = 44.20 | 1 un × 44.20 = 44.20 | +0% | lista · Renard (cód. 3513) · ABW-00389 · 2025-12-26 | dentro de ±15% |
| 7 | Brida WNRF 2" #300 A105 | 1 × 22.20 = 22.20 | 1 un × 28.42 = 28.42 | +28% | ant · Lista Renar · BRI-02567 · 2026-02-19 | más caro (similar) · real: la planilla la toma sch 40 ("Considero sch40"); el plano dice sch 80 |
| 8 | Junta espiralada 2" #300 316 + grafito | 2 × 6.00 = 12.00 | 2 un × 5.00 = 10.00 | -17% | ant · sin proveedor en planilla · JUN-02769 · 2025-12-23 | más barato |
| 9 | Válvula esférica 2" #300 PT RF WCB palanca (f | 1 × 131.13 = 131.13 | 1 un × 170.30 = 170.30 | +30% | ant · Válvulas Taval (s/listado de Valv.) · VA · 2025-12-10 | más caro (similar) · real: va como Válvulas Taval (factor 1) |
| 10 | Brida ciega 2" #300 RF A105 | 1 × 18.50 = 18.50 | 1 un × 18.50 = 18.50 | +0% | lista · Renard (cód. 8252) · BRI-01031 · 2025-12-26 | dentro de ±15% |
| 11 | Válvula esférica 3/4" NPT WOG 3000 A105 | 9 × 42.04 = 378.38 | 9 un × 33.81 = 304.29 | -20% | ant · sin proveedor en planilla (columna PROVE · 2026-02-20 | más barato (similar) · real: va como Válvulas Taval (factor 1); la planilla dice "PR" y anota "P Total" |
| 12 | Niple 3/4" x 100 mm sch 80 PE x NPT | 6 × 10.00 = 60.00 | 6 un × 4.50 = 27.00 | -55% | ant · sin proveedor en planilla · NIP-03426 · 2026-10-10 | más barato |
| 13 | Tapón hexagonal 3/4" NPT 3000 A105 | 3 × 3.50 = 10.50 | 2 un × 2.30 = 4.60 | -56% | lista · Renard (cód. 5980) · AFO-00850 · 2025-12-26 | más barato · real: la planilla compra 3; el plano pide 2 |
| 14 | Niple 3/4" x 100 mm sch 80 NPT | 3 × 10.00 = 30.00 | 3 un × 4.50 = 13.50 | -55% | ant · sin proveedor en planilla · NIP-03426 · 2026-10-10 | más barato |
| 15 | Válvula esférica 1" NPT WOG 3000 A105 | 3 × 51.05 = 153.15 | 3 un × 113.88 = 341.64 | +123% | ant · Taval (cotización Comex Taval en 5.Prove · 2026-03-10 | más caro (similar) · real: va como Válvulas Taval (factor 1) |
| 16 | Niple 1" x 100 mm sch 80 PE x NPT | 2 × 10.00 = 20.00 | 2 un × 9.00 = 18.00 | -10% | ant · futura/ francovigh · NIP-01794 · 2026-10-10 | dentro de ±15% |
| 17 | Sockolet 3" x 1" 3000 A105 | 2 × 6.00 = 12.00 | 2 un × 15.59 = 31.18 | +160% | est · no dice · AFO-02394 · 2025-03-27 | más caro (similar) |
| 18 | Tapón hexagonal 1" NPT 3000 A105 | 2 × 3.08 = 6.16 | 2 un × 3.08 = 6.16 | +0% | lista · Renard (cód. 5981) · AFO-00853 · 2025-12-26 | dentro de ±15% |
| 19 | Thredolet 3" x 3/4" 3000 A105 | 1 × 15.00 = 15.00 | 1 un × 5.00 = 5.00 | -67% | ant · Duralitte · AFO-03339 · 2026-04-22 | más barato (similar) |
| 20 | Buje reducción 3/4" x 1/2" NPT 3000 A105 | 1 × 2.98 = 2.98 | 1 un × 2.98 = 2.98 | +0% | lista · Renard (cód. 5041) · AFO-00604 · 2025-12-26 | dentro de ±15% |
| 21 | Caño s/c 3" sch 40 A106 B (tramo 258 mm) | 1 × 6.47 = 6.47 | 0.258 m × 25.08 + compra extra 21b = 15.05 | +133% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 22 | Brida WNRF 3" #300 sch 40 A105 | 6 × 40.98 = 245.88 | 8 un × 30.33 = 242.64 | -1% | lista · Renard (cód. 8938) · BRI-01376 · 2025-12-26 | dentro de ±15% · real: la planilla compra 6 (1 + 5); el plano pide 8 |
| 23 | Niple 1" x 100 mm sch 80 NPT | 1 × 10.00 = 10.00 | 1 un × 9.00 = 9.00 | -10% | ant · futura/ francovigh · NIP-01794 · 2026-10-10 | dentro de ±15% |
| 24 | Junta espiralada 3" #300 316 + grafito | 7 × 6.00 = 42.00 | 8 un × 7.00 = 56.00 | +33% | ant · sin proveedor en planilla · JUN-02775 · 2025-12-23 | más caro · real: la planilla compra 7; el plano pide 8 |
| 25 | Caño s/c 3" sch 40 A106 B (tramo 722 mm) | 1 × 18.11 = 18.11 | 0.722 m × 25.08 + compra extra 25b = 30.10 | +66% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 26 | Válvula esférica 3" #300 PT RF WCB palanca (f | 3 × 246.25 = 738.74 | 3 un × 319.80 = 959.40 | +30% | ant · Válvulas Taval (s/listado de Valv.) · VA · 2025-12-10 | más caro (similar) · real: va como Válvulas Taval (factor 1) |
| 27 | Brida ciega 3" #300 RF A105 | 1 × 36.49 = 36.49 | 1 un × 36.49 = 36.49 | +0% | lista · Renard (cód. 8254) · BRI-01044 · 2025-12-26 | dentro de ±15% |
| 28 | Caño s/c 3" sch 40 A106 B (tramo 205 mm) | 1 × 5.14 = 5.14 | 0.205 m × 25.08 + compra extra 28b = 15.05 | +193% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 29 | Caño s/c 3" sch 40 A106 B (tramo 215 mm) | 1 × 5.39 = 5.39 | 0.215 m × 25.08 + compra extra 29b = 15.05 | +179% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 30 | Caño s/c 3" sch 40 A106 B (tramo 105 mm) | 1 × 2.63 = 2.63 | 0.105 m × 25.08 + compra extra 30b = 15.05 | +472% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 31 | Tee normal 3" sch 40 BW A234 WPB | 1 × 28.36 = 28.36 | 1 un × 28.36 = 28.36 | +0% | lista · Renard (cód. 3465) · ABW-00394 · 2025-12-26 | dentro de ±15% |
| 32 | Tuerca hexagonal 5/8" 2H | 32 × 0.00 = 0.00 | 32 un × 4.38 = 140.16 |  | cot · DELGADO · JUN-01778 · 2025-09-04 | más barato (similar) · real: incluida en el espárrago con 2 tuercas (pos 33) |
| 33 | Espárrago 5/8" x 89 mm B7 con 2 tuercas 2H, z | 16 × 10.00 = 160.00 | 16 un × 7.82 = 125.12 | -22% | cot · Ind Delgado · JUN-01744 · 2026-05-28 | más barato (similar) |
| 34 | Tuerca hexagonal 3/4" 2H | 112 × 0.00 = 0.00 | 112 un × 4.38 = 490.56 |  | cot · DELGADO · JUN-01778 · 2025-09-04 | más barato (similar) · real: incluida en el espárrago con 2 tuercas (pos 37) |
| 35 | Caño s/c 3" sch 40 A106 B (tramo 254 mm) | 1 × 6.37 = 6.37 | 0.254 m × 25.08 + compra extra 35b = 15.05 | +136% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 36 | Caño s/c 3" sch 40 A106 B (tramo 100 mm) | 1 × 2.51 = 2.51 | 0.1 m × 25.08 + compra extra 36b = 15.05 | +500% | lista · Renard (cód. 1153) · CAN-01484 · 2025-12-26 | más caro |
| 37 | Espárrago 3/4" x 108 mm B7 con 2 tuercas 2H,  | 56 × 10.00 = 560.00 | 56 un × 10.00 = 560.00 | +0% | ant · no dice · JUN-02733 · 2025-12-10 | dentro de ±15% |
| 38 | Transmisor de temperatura ABB (con sensor y v | 1 × 2,205.87 = 2,205.87 | 1 un × 803.00 = 803.00 | -64% | ant · planilla de costo ITT · INS-02677 · 2026-06-25 | más barato (similar) · real: en la planilla va en Instrumentos (factor 1,35); alternativa Rosemount 3.470,06 |
| 39 | Manómetro con manifold | 1 × 0.00 = 0.00 | 1 un × 120.00 = 120.00 |  | ant · planilla de costo ITT · INS-02694 · 2026-06-26 | más barato (similar) · real: la planilla NO lo costea |
| 40 | Transmisor de presión ABB con manifold | 1 × 901.71 = 901.71 | 1 un × 1,100.00 = 1,100.00 | +22% | ant · Vega (cotización en 5.Proveedores 3ros)  · 2026-03-10 | más caro (similar) · real: en la planilla va en Instrumentos (factor 1,35); alternativa Rosemount 2.848,53 |

**Materiales: real USD 6,400.97 · cotizador USD 6,341.81 (-1%).** 12 dentro de ±15%, 27 fuera, 1 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 1,300.00 | 1,183.34 | -9% |
| radiografía y END | 841.00 | 1,038.30 | +23% |
| granallado y pintura | 295.00 | 310.65 | +5% |
| prueba hidráulica | 0.00 | 52.00 | — |
| ingeniería, calidad y montaje | 0.00 | 1,229.40 | — |

**MO y servicios: real USD 2,436.00 · cotizador USD 3,813.69 (+57%).**

## Total por puente

Real USD 8,836.97 · cotizador USD 10,155.50 (+15%) antes de completar lo que el cotizador marca para revisar.

