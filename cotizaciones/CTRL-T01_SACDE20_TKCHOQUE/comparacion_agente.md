# Caso de control CTRL-T01: precotización automática contra el costo real

Generado por `herramientas/comparar_historico.py` con `cotizacion_agente.json`. Costos por tanque, sin IVA y sin ajuste por inflación. Diferencia = cotizador ÷ real − 1.

## Materiales (por posición del plano)

| Pos | Pieza | Real (cant × unit = total) | Cotizador (cant × unit = total) | Dif. | Fuente del cotizador | Lectura |
|---|---|---|---|---|---|---|
| 1 | Virola 36" x 2500 x 3/8" A-516 Gr.70 rolada y | 2 × 1,888.00 = 3,776.00 | 2 un × 923.36 + compra extra 1c = 4,412.24 | +17% | cot · Chapaferro (presupuesto 00189032, 23-03- · 2026-03-23 | más caro (similar) · real: 590 kg c/u × USD 3,20/kg (chapa 1,58 + corte y biselado 0,90 + rolado 0,62) |
| 2 | Casquete SE 36" x 3/8" | 2 × 531.44 = 1,062.88 | 2 un × 828.35 = 1,656.70 | +56% | cot · Cintolo (mail 20-11-2025, art. 12723) · 2025-11-20 | más caro (similar) · real: cot 24-02-2026 (mail sin precio legible en el texto) |
| 3 | Patas A-36 | 170 × 1.50 = 255.00 | 170 kg × 1.27 = 216.65 | -15% | cot · Precios de acero (feb-2026) · 2026-02-10 | más barato (similar) · real: 2 un × 85 kg |
| 4 | Codo 90° 2" RL Sch 40 | 1 × 13.30 = 13.30 | 1 un × 6.08 = 6.08 | -54% | lista · Renard (cód. 3397) · 2025-12-26 | más barato · real: la planilla multiplica 6,65 por los 2 kg (error de la planilla: debía ser 6,65) |
| 5 | Bafle 400 x 200 x 1/4" | 5 × 1.50 = 7.50 | 5 kg × 1.25 = 6.25 | -17% | cot · Precios de acero (feb-2026) · 2026-02-10 | más barato |
| 6 | Brida SORF 2" #150 | 1 × 10.87 = 10.87 | 1 un × 12.18 = 12.18 | +12% | ant · Planilla Sacde/15 TK glicol (BRI-01112) · 2026-02-20 | dentro de ±15% |
| 7 | Brida SORF 6" #150 | 2 × 38.19 = 76.38 | 2 un × 38.19 = 76.38 | +0% | lista · Renard (cód. 9397) · 2025-12-26 | dentro de ±15% |
| 8 | Caño S/C 6" Sch 40 | 6 × 60.51 = 363.06 | 6 m × 60.51 = 363.06 | +0% | lista · Renard (cód. 1173) · 2025-12-26 | dentro de ±15% · real: se compra la tira entera de 6 m por no haber stock |
| 9 | Caño S/C 2" Sch 80 | 0.25 × 16.62 = 4.16 | 0.25 m × 16.62 = 4.16 | +0% | lista · Renard (cód. 1143) · 2025-12-26 | dentro de ±15% |
| 10 | Sombrerete 10" Sch 20 x 300 mm | 1 × 194.71 = 194.71 | 1 un × 99.02 = 99.02 | -49% | est · Renard 10" 6,35 mm (cód. 1188) + chapa A · 2025-12-26 | más barato (sin_ref) · real: la planilla dice 0,3 × 26,709 = 194,709 (la cuenta no cierra; se toma el subtotal) |
| 11 | Placa de identificación | 1 × 15.00 = 15.00 | 1 un × 25.00 = 25.00 | +67% | ant · Planilla INARTECO (PER-03081) · 2026-01-15 | más caro (similar) |
| 12 | Deflectores 900 x 200 x 1/4" | 90 × 1.50 = 135.00 | 90 kg × 1.25 = 112.44 | -17% | cot · Precios de acero (feb-2026) · 2026-02-10 | más barato · real: 9 un × 10 kg |
| 13 | Espárragos 3/4" x 130 mm c/2 tuercas | 8 × 10.00 = 80.00 | 8 un × 10.00 = 80.00 | +0% | ant · Bules o Versailles (JUN-03363) · 2026-02-19 | dentro de ±15% |
| 14 | Cáncamo y respaldo | 6 × 0.75 = 4.50 | 6 kg × 1.27 = 7.65 | +70% | cot · Precios de acero (feb-2026) · 2026-02-10 | más caro (similar) · real: la planilla toma 3 kg × 1,5 (error: 2 un × 3 kg = 6 kg) |
| 15 | Separador de niebla 6" (con viruta) | 5 × 1.50 = 7.50 | 5 kg × 3.00 = 15.00 | +100% | est · Estimado: chapa/caño + viruta de acero · 2026-02-10 | más caro (sin_ref) |
| 16 | Brida WNRF 2" #600 Sch 80 | 1 × 28.42 = 28.42 | 1 un × 28.42 = 28.42 | +0% | cot · RENARD (BRI-01259) · 2025-07-11 | dentro de ±15% |
| 17 | Refuerzo 355 mm x 3/8" | 8 × 1.50 = 12.00 | 8 kg × 1.65 = 13.17 | +10% | cot · Chapaferro (23-03-2026) · 2026-03-23 | dentro de ±15% |
| 18 | Media cupla 2" #6000 | 1 × 18.38 = 18.38 | 1 un × 18.38 = 18.38 | +0% | est · Renard media cupla 2" S3000 (cód. 7046)  · 2025-12-26 | dentro de ±15% · real: estimado base S3000 × 2 |
| 19 | Junta plana 6" #150 | 1 × 10.00 = 10.00 | 1 un × 8.00 = 8.00 | -20% | est · Junta plana 10" #150 Sacde/13 (JUN-02784 · 2026-03-06 | más barato (similar) |
| 20 | Cunas de apoyo | 40 × 0.75 = 30.00 | 40 kg × 1.27 = 50.98 | +70% | cot · Precios de acero (feb-2026) · 2026-02-10 | más caro (similar) · real: la planilla toma 20 kg × 1,5 (error: 2 un × 20 kg = 40 kg); incluye MO ITT p/estructura pesada |

**Materiales: real USD 6,104.65 · cotizador USD 7,211.75 (+18%).** 8 dentro de ±15%, 12 fuera, 0 sin precio.

## Mano de obra y servicios (por rubro)

| Rubro | Real | Cotizador | Dif. |
|---|---|---|---|
| soldadura | 10,700.00 | 4,292.84 | -60% |
| radiografía y END | 2,720.00 | 2,260.00 | -17% |
| granallado y pintura | 1,000.00 | 889.46 | -11% |
| ingeniería, calidad y montaje | 2,100.00 | 6,300.00 | +200% |

**MO y servicios: real USD 16,520.00 · cotizador USD 13,742.30 (-17%).**

## Total por tanque

Real USD 22,624.65 · cotizador USD 20,954.05 (-7%) antes de completar lo que el cotizador marca para revisar.

