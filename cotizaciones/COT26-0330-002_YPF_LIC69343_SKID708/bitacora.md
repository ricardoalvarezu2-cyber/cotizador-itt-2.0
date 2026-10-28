# Bitácora COT26-0330-002 — YPF · Lic 69343 — 6 skids concentradores 1000623708

Pedido `pmvrzbrh616ftx` desde la página (28-10-2026): revisar y recotizar la planilla PC0. Estado: **borrador, sin revisar**.

## Inconsistencias de la planilla PC0 (Excel del pedido)
1. **Pie de venta:** en los ítems 3 a 9 el USD unidad y el subtotal están cruzados (cada uno trae el precio del otro skid). El total sí cierra: USD 1.437.889,65.
2. **Número de licitación:** el archivo dice 69343 y las hojas 69434.
3. **Vencimiento:** 27-10-2026 (recepción 10-10-2026): ya venció.
4. **Entrega:** las hojas de cada skid dicen EXW Quilmes Oeste; la hoja Resumen dice Rincón de Aranda y suma transporte (USD 2.500 en el Resumen, USD 2.800 en la hoja, USD 3.000 por camión completo).
5. **Instrumental:** el alcance dice «Instrumental: NO», pero lo cotiza (USD 1.780 y 1.110 por skid).
6. **Skid 1000623713:** los tags TI-011 dicen «Manómetro» y los PI-011 «Termómetro 0-200 °C»: rótulos cruzados.
7. **MO de terceros:** en el 713 el Resumen toma USD 34.000 (Ledesma 28.000 + montaje y dimensional 6.000); en el 708 toma 13.250 y deja afuera los 3.000 de montaje y dimensional.
8. **Overspray contado dos veces:** los m² ya dicen «overspray 20%» y el subtotal suma otro 20% (skid 713: 7.200 → 8.640; piping 713: 2.500 → 3.000; skid 708: 2.960 → 3.552; piping 708: 1.100 → 1.320).
9. **Repuestos:** el Resumen suma USD 3.520,04 (713) y 2.305,40 (708), pero las listas dan 2 × 176,81 = 353,62. La lista del 708 es la del 713 (espárragos 7/8" y juntas 8" que el 708 no tiene). «ASTM A133» debería ser A193.
10. **Factores:** la PC0 usa 1,5 y deja en 1 las válvulas Taval, el transporte (713) y la caución. El cotizador aplica 1,35 a todo: definir con la dirección.
11. **Radiografía:** la PC0 pone USD 5.000 por skid; el cálculo junta por junta da 15.140 (713, 124 juntas de 8" y 12") y 5.540 (708, 38 juntas).
12. **Sin plano:** la tabla de materiales se tomó de la PC0; no se pudo ver qué soldaduras quedan para campo ni el detalle de la estructura (kg de la PC0).

## Criterio de esta recotización (borrador)
- Precio del catálogo cuando la pieza es **igual** (con fecha y origen); si no, el precio de la PC0 como **estimado** (sin fecha ni documento del proveedor) con el similar del catálogo como alternativa. Las válvulas de 8" y 12" no están en el catálogo: precio Taval de la PC0.
- Soldadura propia de planta, junta por junta (la PC0 la terceriza en Ledesma: queda como alternativa). Estructura: USD 3/kg de Ledesma (dato de la PC0). Horas de ingeniería, calidad y montaje estimadas del antecedente más parecido (`estimar_horas.py`).
- Pintura con los m² de la PC0 (sin el 20% repetido) a USD 50/m². EXW Quilmes Oeste, USD sin IVA, factores 1,35.
- Script: `cotizaciones/COT26-0330-001_YPF_LIC69343_SKID713/armar_json.py` (lee `pc0.py`).

## Diferencias por posición (USD por unidad)

| Pos | Pieza | PC0 | Cotizador | Dif. | Base del cotizador |
|---|---|---|---|---|---|
| 1 | Caño s/c extr. SCH XS (323,8 x 12,70) 12" | 297.75 | 217.23 | -27% | Renard · CAN-01435 · 2026-06-26 |
| 2 | Caño c/c extr. STD (406,4 x 9,52) 16" | 341.24 | 341.24 | +0% | PC0 (estimado) |
| 3 | Tee normal 12" | 1,457.38 | 1,457.38 | +0% | PC0 (estimado) |
| 4 | Tee de reducción SCH STD x XS 16"x12" | 2,802.34 | 2,802.34 | +0% | Renard (cód. 3547) · ABW-00358 · 2025-12-26 |
| 5 | Brida WN RF 300 LB SCH XS 12" | 425.09 | 425.09 | +0% | PC0 (estimado) |
| 6 | Brida WN RF 300 LB 16" | 680.00 | 680.00 | +0% | PC0 (estimado) |
| 7 | Brida ciega RF 300 LB 12" | 477.53 | 426.44 | -11% | Renard (cód. 8260) · BRI-01022 · 2025-12-26 |
| 8 | Brida ciega RF 300 LB 16" | 820.00 | 820.00 | +0% | PC0 (estimado) |
| 9 | Brida SW RF 300 LB SCH 80 1 1/2" | 19.91 | 17.96 | -10% | Renard (cód. 10683) · BRI-01161 · 2025-12-26 |
| 10 | Espárrago c/2 tuercas p/brida 300 LB 1.25x207 zinc | 12.95 | 12.95 | +0% | PC0 (estimado) |
| 11 | Espárrago c/2 tuercas p/brida 300 LB 1.125x186 zin | 9.59 | 9.59 | +0% | PC0 (estimado) |
| 12 | Junta espiralada RF esp. 4,5 mm 300 LB 1 1/2" | 7.00 | 7.00 | +0% | PC0 (estimado) |
| 13 | Junta espiralada RF esp. 4,5 mm 300 LB 12" | 45.00 | 45.00 | +0% | PC0 (estimado) |
| 14 | Junta espiralada RF esp. 4,5 mm 300 LB 16" | 80.00 | 80.00 | +0% | PC0 (estimado) |
| 15 | Niple s/c NPT L=100 mm 1 1/2" | 9.00 | 9.00 | +0% | PC0 (estimado) |
| 16 | Niple s/c NPT L=100 mm 1/2" | 4.00 | 20.00 | +400% | Antecedentes puentes Taval/CGC s2000 · NIP-01 · 2026-04-22 |
| 17 | Niple s/c NPT L=100 mm 3/4" | 4.50 | 4.50 | +0% | PC0 (estimado) |
| 18 | Niple s/c NPT L=100 mm 3/4" | 6.00 | 6.00 | +0% | PC0 (estimado) |
| 19 | Tapón NPT cab. hexag. 1/2" | 1.94 | 1.94 | +0% | PC0 (estimado) |
| 20 | Tapón NPT cab. hexag. 3/4" | 2.30 | 2.30 | +0% | PC0 (estimado) |
| 21 | Sockolet SW 3000 LB 12"x1 1/2" | 28.00 | 28.00 | +0% | PC0 (estimado) |
| 22 | Sockolet SW 3000 LB 12"x3/4" | 14.00 | 14.00 | +0% | PC0 (estimado) |
| 23 | Sockolet SW 3000 LB 16"x3/4" | 15.00 | 15.00 | +0% | PC0 (estimado) |
| 24 | Sockolet SW 3000 LB 16"x1/2" | 13.00 | 13.00 | +0% | PC0 (estimado) |
| 25 | Válvula esférica NPT WOG 2000 P.T. op. palanca 1/2 | 36.06 | 36.06 | -0% | PC0 (estimado) |
| 26 | Válvula esférica NPT WOG 2000 P.T. op. palanca 3/4 | 38.80 | 38.80 | -0% | PC0 (estimado) |
| 27 | Válvula de retención a clapeta FLG RF 300 LB 12" | 3,162.00 | 3,162.00 | +0% | PC0 (estimado) |
| 28 | Válvula globo NPT 800 LB op. volante 1/2" | 35.10 | 35.10 | +0% | PC0 (estimado) |
| 29 | Válvula globo NPT 800 LB op. volante 3/4" | 40.50 | 40.50 | +0% | PC0 (estimado) |
| 30 | Válvula esférica FLG RF 300 LB P.T. op. volante y  | 5,750.00 | 5,750.00 | -0% | PC0 (estimado) |

## Pendientes
- Plano de cañerías y de estructura; cliente, comprador y N; EXW o entregado; instrumental sí/no; lista de repuestos del 708.
- Cotizar a Compras accesorios y bridas de 8" a 16" y confirmar con Taval las válvulas.
- Revisión independiente del cómputo antes de pasar a revisado.
