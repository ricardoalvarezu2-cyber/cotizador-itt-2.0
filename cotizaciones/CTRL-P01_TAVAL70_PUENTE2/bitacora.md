# CTRL-P01: caso de control del puente de inyección y regulación 2" #600 (Taval 70, YPF Gas Lift)

**No es una cotización para el cliente.** Es un caso de control del cotizador. Se toma un equipo que ITT ya costeó y se comparan tres números por puente:
- el costo real de la planilla de ITT;
- la precotización automática de la app;
- una recotización hecha a mano por un agente con las herramientas.

- Proyecto: `TAVAL/70- PUENTES DE MEDICION 2 PULGADAS`. Son 24 puentes de inyección y regulación 2" RF #600 (SAP 1000653143) para YPF (UP-UTE La Amarga Chica y LL Norte NOC). PRES 25279: rev. A del 14-07-2026 y rev. B, con bonificación, del 27-10-2026.
- Planilla real vigente: `REV 1- OFERTA MEJORADA/Cot Puente Gas Lift SAP 1000653143 rev. 2 - PC0.xlsx`, hoja "Cotización rev 1", del 26-10-2026. Costo 73.561,53 por puente; venta 97.460,67 con factor 1,35.
- La REV 0 (`REV 0/Puente Iny y Reg 2pulg serie600 SAP 1000653143 rev. 1.xlsx`) costaba 77.675,38. Se anota, pero vale la REV 1, que es la más reciente.
- El archivo `REV 0/PUENTES DE MEDICION 2 PULGADAS.xls` no es la planilla de costo: es la hoja de Ariba con el precio.

## Cómo se armó (28-10-2026)

1. **`pedido/lista_materiales_plano.csv`:** las 24 posiciones de la hoja "Lista Mats Ing", que es la lista de ingeniería de ITT; los planos de YPF del texto no traen tabla de materiales.
   - Los extremos salen de la descripción: WNRF → RF/BW, SWRF → RF/SW, tees BW, sockolet BW/SW y válvulas RF.
   - Caños en metros: la planilla dice "24 un" del 2", pero al precio por metro de Renard.
   - `extremos_campo` = 0, porque el puente entra y sale bridado.
   - Marca TAVAL en las esféricas, la retención, el filtro Y y las válvulas de 1": en la planilla van como "Válvulas Taval".
2. **`historico.csv`:** el costo real por puente de la REV 1, mapeado a las posiciones de la lista.
   - Las diferencias de la REV 1 con la lista van en la nota de cada fila: 8 esféricas en lugar de 10, la junta de la pos 11 eliminada, las válvulas chicas cambiadas y el bastidor de 1.200 kg.
   - Lo que la REV 1 compra fuera de la lista va en filas X1–X3: U-bolts, manifold de 5 vías y botellones.
   - Materiales 54.743,60 + MO y servicios 13.816,00 = 68.559,60 de equipo EXW.
   - Con transporte (2.400), caución (244,43) y asistencia y repuestos de puesta en marcha (2.357,50) da 73.561,53, igual que la planilla.
3. **`cotizacion.json`:** parámetros cargados antes de correr.
   - `N` = 24.
   - `rx_pct` = 100: el pliego pide RT1 ("100% Rx, y donde no se pueda Rx se harán LP").
   - `ph_horas` = 36: 2 personas × 2 días × 9 h, según la planilla.
   - `equipo.tipo` = puente, `diametro_pulg` = 2.
4. **APP:**
   - `python herramientas/precotizar.py cotizaciones/CTRL-P01_TAVAL70_PUENTE2 --excluir "TAVAL/70"`.
   - `python herramientas/comparar_historico.py cotizaciones/CTRL-P01_TAVAL70_PUENTE2` → `comparacion_historico.md`.
5. **AGENTE:** `cotizacion_agente.json`, armado a mano con `buscar_material.py`, `buscar_servicio.py`, `buscar_antecedentes.py` y las fuentes abiertas, sin TAVAL/70. Las fuentes clave son:
   - Doma P-06823, del 16-07-2026: válvula de control 667 EZ 3" #300 a 8.206.
   - ABB OPP-26-8794766, del 16-07-2026: XFC6200EX a 7.345,97.
   - Ledesma 200295, del 19-07-2026: 2 skids de regulación y medición a 17.200, que es el mismo alcance.
   - Lista Renard 12-2025.
   - Válvulas Taval de TAVAL/43.
   - Lista DB NDT del 14-08-2026.

   Después se corrió `comparar_historico.py ... --json cotizacion_agente.json`, con la salida renombrada a `comparacion_agente.md`.

## Resultado (por puente, sin IVA)

| | Materiales | MO y servicios | Total |
|---|---:|---:|---:|
| REAL (REV 1, equipo EXW) | 54.743,60 | 13.816,00 | **68.559,60** |
| APP (precotización sin completar) | 27.163,96 | 12.419,44 | **39.583,40 (−42%)** |
| AGENTE | 61.106,06 | 15.035,50 | **76.141,56 (+11%)** |

Sin las canalizaciones (pos 23, 8.000 estimados, que la planilla real no costea), el AGENTE da 68.141,56 (−0,6%).

El detalle por rubro y los 16 errores de la app, ordenados por impacto, están en `errores_app.md`. Los más graves son:
- la válvula de control que no se reconoce (−17.200), y además queda marcada como Taval, con factor 1 (−6.020 en la venta);
- el computador de caudal sin precio por un renglón del catálogo con varios ítems (−8.424);
- la RX con tarifas viejas y servicios por equipo (+2.722);
- la pintura solo de caños (−2.087);
- el V-Cone cotizado con un electromagnético (+2.040).

## Decisiones y criterios del agente

- **Pos 11:** se costea en 0, porque la junta está duplicada con la pos 19 (46 juntas × 8 = 368 espárragos).
- **Pos 15:** en 0, porque la oferta excluye el inyector de químicos.
- **Pos 23:** se interpreta "8000 VERDES" como USD 8.000 por puente para dos canalizaciones. Es un estimado (`est`) que hay que confirmar.
- **V-Cone:** no hay un precio fuera del proyecto. Se tomó el Krohne electromagnético (4.200) solo como orden de magnitud: hay que pedir cotización a Meditecna o McCrometer.
- **Bridas 3" #600 y SW 1 1/2" #600:** escaladas desde la 2" #600 Renard, porque no hay precio real.
- **Montaje:** 128 h (bridas, instrumentos, movimientos, PH y despacho).
- **Ingeniería y calidad:** 12,5 h por puente (300 h repartidas en 24 puentes).
- **Pintura:** 34 m² a 50 USD/m².
- **RX:** 180 placas × 6,50 + 3 servicios × 408, más 1 servicio de LP de 490.

## Pendientes

- Confirmar si la lista de ingeniería es por puente o por par (SK-2104/SK-2105). La HD I-HD-003004 da 1 FE, 1 FQIT y 1 FV por locación.
- Los botellones de purga (nota 8 del P&ID) y los transmisores DP/P para el V-Cone no están en la lista de ingeniería.
