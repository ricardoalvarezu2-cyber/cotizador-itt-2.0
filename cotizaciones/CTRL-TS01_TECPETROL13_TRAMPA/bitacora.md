# CTRL-TS01: caso de control con la trampa receptora 16" x 12" #900 de Tecpetrol (Evento 12681)

**No es una cotización para el cliente.** Es un caso de control del cotizador. Se tomó una trampa que ITT ya costeó y ganó (PRES 186 rev. B, OC 4520003317 del 02-09-2026, 6 trampas para el gasoducto de exportación de Fortín de Piedra) y se compararon tres números por trampa: el costo **REAL** de la planilla de ITT, la precotización automática (**APP**) y la recotización a mano del **AGENTE**. El detalle está en `errores_app.md`.

## Fuentes (28-10-2026)
- Planilla: `fuentes_originales/ofertas_texto/TECPETROL/13- TRAMPAS TSR TSL de 16- 12 - 8 pGSD Evento 12681/8.Orden de Compra/Cotización Tecpetrol Trampas Lanz y Rec de 20x16 16x12 10x8 REV 1.xlsx.txt`, hoja **Rec 16x12** (pedido 26-06-2026). Es el ítem 1.4 de la oferta ("trampa receptora de 12" Serie 900, clase A9CM"): línea de 12", barril menor 12" y barril mayor 16". Costo USD 83.177,98 por trampa; venta 105.812,92 (factor 1,35; Taval 1,0; caución 3).
- Las otras dos copias del archivo (`4.Armado…/REV 1.xlsx` y `8.Orden…/REV 1-0.xlsx`) tienen la hoja idéntica (`diff` sin diferencias).
- Hoja de datos `ACO-FP-TR3-M-HD-002` (receptora 12"): B31.8, diseño 118 kg/cm², CA 3,2 mm, paso mínimo 298 mm, toberas WNRF #900, detector "por otros". Condiciones de diseño de la planilla: RX 100%.
- El típico `ACO-CNV-GENTIP-M-PL-001 Rev.2` no tiene texto (es un dibujo). La tabla de materiales es la de la planilla.

## Qué se hizo
1. Carpeta copiada de `_plantilla/` (sin su README). `pedido/lista_materiales_plano.csv`: las 50 posiciones de la hoja (piping, skid, válvulas manuales e instrumentos), con la misma cantidad y unidad. Excepciones anotadas: pos 12 (caño 1½" "0,1 u" de la planilla) va en metros; pos 16 repite el codo 2" sch 160. Barriles como "Virola/caño … largo … esp. 5/8"". Extremos: bridas RF/BW, caños y accesorios BW, niple NPT/BW, weldolets BW, válvulas RF o NPT. `extremos_campo` = 0: todas las conexiones al cliente son bridadas.
2. `historico.csv`: costo real por trampa, con los mismos totales que la hoja. El skid va como en la planilla: UPN 590 kg × 1,5 + 20% = 1.062 y la malla en 0 (la lista pero no la suma). MO: Ledesma piping 11.500 (global), skid 590 kg × 2,8; ITT 120 h × 13; calidad 120 h y ingeniería 100 h × 15; pintura 1.990; RX y LP 2.943,98; repuestos 545,40; transporte 1.200; caución 169,81.
3. `cotizacion.json`: N = 1, `rx_pct` = 100 (condiciones de diseño), `ph_horas` = 18 (dos jornadas de 9 h; la app las descarta porque el montaje del antecedente ya incluye la PH), `equipo.tipo` = trampa, `diametro_pulg` = 16. Se cargó antes de correr.
4. APP: `python herramientas/precotizar.py cotizaciones/CTRL-TS01_TECPETROL13_TRAMPA --excluir "TECPETROL/13"`. No hizo falta otro `--excluir`: los textos "SYPRIS TOOLS" y "REDUCCION EXCENTRICA 16X12" solo aparecen en TECPETROL/13 y en la LM de TECPETROL/7 (otro proyecto, 2025). Después, `python herramientas/comparar_historico.py cotizaciones/CTRL-TS01_TECPETROL13_TRAMPA` → `comparacion_historico.md`.
5. AGENTE: `buscar_antecedentes.py --familia TS` (después del propio, TECPETROL/7: trampas 20x16 #900 con tapa Sypris para Fortín de Piedra, con LM de compras y presupuestos Ledesma; y PAMPA ENERGIA/2, trampas 12x16 #900). `buscar_material.py` renglón por renglón (salteando los precios de TECPETROL/13), `buscar_servicio.py` y `estimar_horas.py trampa 16 --excluir TECPETROL/13`. Se abrieron: la LM RECEPTORA de TECPETROL/7, los presupuestos Ledesma 200106 y 200107 (16-10-2025), la cot. FTS 260812 (Sypris 16" CL900, PAMPA ENERGIA/6), Provemet en `precios_componentes.csv`, la lista Renard, `bridas_peso.csv` y el detalle de montaje de TECPETROL/10. Resultado en `cotizacion_agente.json`, comparado con `comparar_historico.py … --json cotizacion_agente.json` → `comparacion_cotizacion_agente.md`.
6. No se corrió `armar_cotizacion.py` ni `verificar_todo.py`. No se modificó nada fuera de esta carpeta. Los scripts auxiliares quedaron en el scratchpad de la sesión.

## Resultado (por trampa, sin IVA)

| | Materiales | MO y servicios | Total | contra REAL |
|---|---:|---:|---:|---:|
| REAL | 58.316,80 | 24.861,19 | **83.177,98** | — |
| APP | 43.871,89 | 23.427,53 | **67.299,42** | −19% |
| AGENTE | 59.747,69 | 24.294,08 | **84.041,76** | +1% |

Sin lo que la app deja SIN PRECIO (malla y detector): REAL 78.968,48 · APP −15% · AGENTE 82.080,54 (+4%).

Errores principales de la app:
- válvulas Taval #900 cotizadas con #600/#300 y la de 12" con una retención: −8.711;
- MO de otro alcance (soldadura y montaje propios de una trampa #300 que ITT armó entera, en lugar del tercero con el mismo alcance que está en el catálogo) e ingeniería y calidad escaladas por tamaño: −6.243 y +6.934;
- reducción 16x12 cotizada con una 10x4 y tee sch 160 con una sch 80: −3.346;
- tapa de cierre rápido #900 con una #600 de un filtro, marcada IGUAL: −2.491;
- bridas #900 con stock 2022–2024 y lista RTJ: +2.841.

## Criterios del agente (estimados, a confirmar en una cotización real)
- Bridas #900: precio por kg de Provemet 06-2025 (10" → 6,41 USD/kg; 16" → 5,30), con +25% para la 12" A694 F65.
- Barril 12" X52 5/8": 590 USD/m (la 16" X65 de TECPETROL/7 a 750/m, llevada por kg/m).
- Reducción excéntrica 16x12 WPHY 52: 3.040 (la 20x16 de TECPETROL/7 × 0,65 × 1,25).
- MO de fabricación: Ledesma 200106 (10.800, receptora 20x16) sin bajar por tamaño, porque el costo local en USD subió desde 10-2025. Skid: Ledesma 200107 (2 USD/kg).
- Horas ITT: ingeniería 120 h, calidad 100 h, montaje 162 h (PH 54, armado final 54, movimientos 36, despacho 18).
- Radiografía: ~150 placas × 6,50 + 4 servicios × 408 + LP 294 (DB NDT 08-2026).
- Transporte: medio semirremolque Suan a Neuquén (2 trampas por camión). Caución 200. Repuestos: 2 lip seals y 4 O-rings de la cot. FTS.
- Detector de scraper: la hoja de datos dice "por otros". Hay que consultarlo con el cliente.
