# CTRL-P02: caso de control del puente de producción 3" #300 (Pampa 5, Rincón de Aranda)

**No es una cotización para el cliente.** Es un caso de control del cotizador. Se toma un equipo que ITT ya costeó y se comparan tres números por puente:
- el costo real de la planilla de ITT;
- la precotización automática de la app;
- una recotización hecha a mano por un agente con las herramientas.

- Proyecto: `PAMPA ENERGIA/5 - Doc5757155642 - Construc 10 Puentes y 2 Colectores - RDA`. Son 10 puentes de producción 3" #300 (BDP-RDA, ítems 3.6 y 3.7) más 2 colectores. La oferta es la PRES 163 rev. C del 16-07-2026 y la OC es la 4500766711.
- Planilla real: `4.Armado de la Oferta Comercial/Cot Skid Manifolds Colectores RDA Rev2.xlsx`, hoja "Puentes". La Rev 3 (`ADICIONAL/`) tiene la hoja de puentes idéntica.
- Plano: `PUENTE DE PROD/1046-RDA-P-PL-6430 - Plano Constructivo Piping Puente de Produccion.pdf`, rev. A del 22-07-2026, con 40 posiciones. Las hojas de datos están en la misma carpeta (HD-6310 de presión, HD-6311 de temperatura y HD-6312 de manómetros).

## Cómo se armó (28-10-2026)

1. **`pedido/lista_materiales_plano.csv`:** las 40 posiciones del plano, tal cual.
   - Caños por tramo, en "1 un, L = … mm".
   - Tuercas aparte de los espárragos.
   - Extremos: bridas WN RF/BW, brida API RTJ/BW, olets BW/SW o BW/NPT, niples PE/NPT o NPT, válvulas RF o NPT.
   - `extremos_campo` = 0, porque el puente entra por la brida API y sale bridado.
2. **`historico.csv`:** el costo real por puente, mapeado a las posiciones del plano.
   - La planilla compra 7,4 m de caño 3": va por tramo, y el sobrante en la pos 5.
   - Los espárragos son "con 2 tuercas", así que las tuercas van en 0.
   - Materiales 6.400,97 + MO y servicios 2.436,00 = **8.836,97** EXW. No entran la caución (381,24) ni el transporte (215,83).
   - Las diferencias de cantidad con el plano van en la nota de cada fila.
3. **`cotizacion.json`:** N = 10, `rx_pct` = 100, `ph_horas` = 4 (supuesto: la planilla no costea la PH), `equipo.tipo` = puente, `diametro_pulg` = 3.
4. **APP:**
   - `python herramientas/precotizar.py cotizaciones/CTRL-P02_PAMPA5_PUENTE3 --excluir "PAMPA ENERGIA/5" --excluir "PAMPA ENERGIA/7"`.
   - `python herramientas/comparar_historico.py cotizaciones/CTRL-P02_PAMPA5_PUENTE3` → `comparacion_historico.md`.
5. **AGENTE:** `cotizacion_agente.json`, armado con `buscar_antecedentes.py`, `buscar_material.py`, `buscar_servicio.py`, `estimar_horas.py` y las fuentes abiertas, sin Pampa 5 ni Pampa 7. Las bases son:
   - lista Renard 12-2025 (bridas, caño, tees, codo, tapones y buje);
   - **lista 30 de Taval (09-2025) con −35% −20%** (el criterio de TAVAL/43) para las esféricas;
   - Francovigh O00093778 y MS 48.445 (carpeta de Pampa 4) para la brida API, el BX153 y las juntas;
   - ABB OPP-26-8794766 (TAVAL/69) para el PGS300, y la planilla de TAVAL/70 REV 1 para el TIT y el RTD con vaina;
   - Abac (TAVAL/55) para el bloqueo y purga, y YPF/28 para niples y sockolets;
   - TAVAL/43 para la soldadura a 16 USD/pulg, las tarifas de RX y las horas.

   Después se corrió `comparar_historico.py ... --json cotizacion_agente.json` → `comparacion_cotizacion_agente.md`.

## Resultado (por puente, sin IVA)

| | Materiales | MO y servicios | Total |
|---|---:|---:|---:|
| REAL (Rev2, equipo EXW) | 6.400,97 | 2.436,00 | **8.836,97** |
| APP (precotización sin completar) | 6.341,81 | 3.813,69 | **10.155,50 (+15%)** |
| AGENTE | 5.732,61 | 3.151,00 | **8.883,61 (+0,5%)** |

La app deja un solo renglón SIN PRECIO: el anillo BX153 (10,00 en el real). Sin ese renglón, el REAL es 8.826,97 y la app sigue en +15%.

El detalle por rubro y los 13 errores de la app están en `errores_app.md`. Los más graves son:
1. Horas de montaje de skids de medición para un puente chico (+1.281).
2. Instrumentos incompletos o de otra marca (−1.085).
3. Tuercas cobradas dos veces, al precio de una de 1 7/8" (+631).
4. Taval sin la lista 30, con precios de otro descuento y una 1" inoxidable (+374).
5. RX con tarifa del proyecto excluido: `--excluir` no filtra `tarifas.csv` (+197).

Además, la brida WNRF 3" #300 sale como **roscada BSPT #150**: el impacto es −85, pero es un error de especificación grave si llega a Compras.

## Decisiones y criterios del agente

- **Taval:** lista 30 × 0,52, con el criterio documentado en TAVAL/43. Da 136,00 / 256,00 / 53,22 / 43,60, contra 131,13 / 246,25 / 51,05 / 42,04 del real, que usó ×0,50.
- **Tuercas (pos 32 y 34):** en 0, porque se compran espárragos con 2 tuercas.
- **Espárragos:** estimados (`est`). Los de 3/4" van a 4,50, desde el stock más las tuercas; los de 5/8" a 3,50, escalados por kg desde la cotización de Delgado del 28-05-2026. La planilla real pone 10 estimado.
- **TT:** 803 + 689 (transmisor, más RTD con vaina, de TAVAL/70). No hay precio de un TTF200 fuera de Pampa 5.
- **PT:** PGS300 a 864,20 más bloqueo y purga Abac a 137.
- **Manómetro:** 120 más bloqueo y purga a 137, según la nota 4 de la HD-6312.
- **RX:** 50 placas × 15 + 1 servicio de RX a 490 + 0,5 servicio de LP a 490 (TAVAL/43). La lista DB NDT (6,50 / 408 / 294) solo está en Pampa 5 y 7: con ella serían 880.
- **Soldadura:** 70 pulg-eq × 16, contada junta por junta. Son 16 juntas BW de 3", 1 de 2" sch 80, 8 olets SW y 1 thredolet, y 8 SW de niples. Sin la Ledesma de Pampa 5, que está excluida.
- **Horas ITT:** 12 h de montaje (movimientos, PH, armado final y despacho) y 6 h de ingeniería y calidad por puente. TAVAL/43 toma 27 h y 10 h en una serie de 442.
- **Caño:** 70,32 m en la serie, comprados en 6 barras de 12 m (0,168 m extra por puente).

## Pendientes

- Ninguno del cotizador fuera de los errores listados. No se modificó ninguna herramienta ni el catálogo: los arreglos propuestos están en `errores_app.md`.
