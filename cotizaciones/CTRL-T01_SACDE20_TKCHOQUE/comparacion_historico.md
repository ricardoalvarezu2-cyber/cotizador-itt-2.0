# Caso de control CTRL-T01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_auto.json`. Costos por tanque, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Virola 36" x 2500 x 3/8" A-516 Gr.70 rolada y | 2 × 1.888,00 = 3.776,00 | 2 un × 2.932,30 = 5.864,60 | +55% | est · Precios de acero por kg (J. Elejondo) +  · 2026-02-10 | más caro (similar) · real: 590 kg c/u × USD 3,20/kg (chapa 1,58 + corte y biselado 0,90 + rolado 0,62) |
| 2 | Casquete SE 36" x 3/8" | 2 × 531,44 = 1.062,88 | 2 un × 828,35 = 1.656,70 | +56% | cot · Cintolo · ABW-00027 · 2025-11-20 | más caro · real: cot 24-02-2026 (mail sin precio legible en el texto) |
| 3 | Patas A-36 | 170 × 1,50 = 255,00 | 170 kg × 1,27 = 215,90 | -15% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más barato (similar) · real: 2 un × 85 kg |
| 4 | Codo 90° 2" RL Sch 40 | 1 × 13,30 = 13,30 | 1 un × 6,08 = 6,08 | -54% | lista · Renard (cód. 3397) · ABW-00100 · 2025-12-26 | más barato · real: la planilla multiplica 6,65 por los 2 kg (error de la planilla: debía ser 6,65) |
| 5 | Bafle 400 x 200 x 1/4" | 5 × 1,50 = 7,50 | 5 kg × 1,25 = 6,25 | -17% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más barato (similar) |
| 6 | Brida SORF 2" #150 | 1 × 10,87 = 10,87 | 1 un × 12,18 = 12,18 | +12% | ant · sin proveedor en planilla (columna PROVE · 2026-02-20 | dentro de ±15% |
| 7 | Brida SORF 6" #150 | 2 × 38,19 = 76,38 | 2 un × 38,19 = 76,38 | 0% | lista · Renard (cód. 9397) · BRI-01139 · 2025-12-26 | dentro de ±15% |
| 8 | Caño S/C 6" Sch 40 | 6 × 60,51 = 363,06 | 6 m × 49,48 + compra extra 8b = 593,76 | +64% | cot · Grupo Provemet · CAN-01510 · 2026-10-29 | más caro · real: se compra la tira entera de 6 m por no haber stock |
| 9 | Caño S/C 2" Sch 80 | 0,25 × 16,62 = 4,16 | 0,25 m × 13,61 = 3,40 | -18% | cot · Grupo Provemet · CAN-01463 · 2026-10-29 | más barato |
| 10 | Sombrerete 10" Sch 20 x 300 mm | 1 × 194,71 = 194,71 | 1 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-23 | SIN PRECIO en el catálogo · real: la planilla dice 0,3 × 26,709 = 194,709 (la cuenta no cierra; se toma el subtotal) |
| 11 | Placa de identificación | 1 × 15,00 = 15,00 | 1 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-23 | SIN PRECIO en el catálogo |
| 12 | Deflectores 900 x 200 x 1/4" | 90 × 1,50 = 135,00 | 90 kg × 1,25 = 112,50 | -17% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más barato (similar) · real: 9 un × 10 kg |
| 13 | Espárragos 3/4" x 130 mm c/2 tuercas | 8 × 10,00 = 80,00 | 8 un × 1,91 = 15,28 | -81% | cot · Oil Metal (cód. ESP0190ZC120193) · JUN-0 · 2026-10-30 | más barato (similar) |
| 14 | Cáncamo y respaldo | 6 × 0,75 = 4,50 | 6 kg × 1,27 = 7,62 | +69% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más caro (similar) · real: la planilla toma 3 kg × 1,5 (error: 2 un × 3 kg = 6 kg) |
| 15 | Separador de niebla 6" (con viruta) | 5 × 1,50 = 7,50 | 5 kg × 1,27 = 6,35 | -15% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más barato (similar) |
| 16 | Brida WNRF 2" #600 Sch 80 | 1 × 28,42 = 28,42 | 1 un × 19,31 = 19,31 | -32% | cot · Grupo Provemet · BRI-01260 · 2026-10-29 | más barato |
| 17 | Refuerzo 355 mm x 3/8" | 8 × 1,50 = 12,00 | 8 kg × 1,27 = 10,16 | -15% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más barato (similar) |
| 18 | Media cupla 2" #6000 | 1 × 18,38 = 18,38 | 1 un × 0,00 = 0,00 | -100% | est · SIN PRECIO EN EL CATÁLOGO: pedir cotizac · 2026-11-23 | SIN PRECIO en el catálogo · real: estimado base S3000 × 2 |
| 19 | Junta plana 6" #150 | 1 × 10,00 = 10,00 | 1 un × 5,76 = 5,76 | -42% | est · Stock ITT (cód. ACS1501X76FL0) · JUN-017 · 2024-11-01 | más barato (similar) |
| 20 | Cunas de apoyo | 40 × 0,75 = 30,00 | 40 kg × 1,27 = 50,80 | +69% | cot · Precios de acero (J. Elejondo) · 2026-02-10 | más caro (similar) · real: la planilla toma 20 kg × 1,5 (error: 2 un × 20 kg = 40 kg); incluye MO ITT p/estructura pesada |

**Materiales: real USD 6.104,66 · cotizador USD 8.663,03 (+42%).** 2 dentro de ±15%, 15 fuera, 3 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 10.700,00 | 3.252,56 | -70% |
| radiografía y END | 2.720,00 | 1.550,00 | -43% |
| granallado y pintura | 1.000,00 | 196,87 | -80% |
| prueba hidráulica | 0,00 | 468,00 | — |
| ingeniería, calidad y montaje | 2.100,00 | 0,00 | -100% |
| otros | 0,00 | 410,40 | — |

**MO y servicios: real USD 16.520,00 · cotizador USD 5.877,83 (-64%).**

## Total por tanque

Real USD 22.624,66 · cotizador USD 14.540,86 (-36%) antes de completar lo que el cotizador marca para revisar.

