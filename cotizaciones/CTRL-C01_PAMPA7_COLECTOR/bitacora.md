# CTRL-C01 — Caso de control: skid colector para PAD de 6 pozos (Pampa Energía, contrato marco Rincón de Aranda)

**No es una cotización para el cliente.** Es un caso de control del cotizador: se toma un equipo que ya se costeó (planilla
`PAMPA ENERGIA/7- Licitacion contrato Marco Skid PAD Rincon de Aranda/4.Armado de la Oferta Comercial/Cot Skid Manifolds Colectores RDA Contrato Marco (2da RDA).xlsx`,
hoja "Colector RDA"; oferta PRES 169 rev. A del 14-08-2026, ítem 2, 18 colectores a USD 88.267,59 de venta) y se compara el
costo REAL con la precotización automática (APP) y con una recotización a mano (AGENTE).

## Cómo se armó (28-10-2026)
1. `pedido/lista_materiales_plano.csv`: no hay plano del colector en las fuentes (el plano 1046-RDA-P-PL-6430 de Pampa 5 es del puente).
   Se transcribieron las 31 posiciones de la planilla (columna "Posición"), más manómetros (32), transmisor de presión (33),
   bastidor del skid 800 kg (34) y tablero eléctrico (35). Extremos definidos con criterio técnico: bridas WN RF/BW, SW RF/SW,
   tees y caño BW, sockolets BW/SW, niples PE/NPT. `extremos_campo` = 0 en todos (el colector se conecta por bridas).
2. `historico.csv`: el costo real por colector, igual a la planilla: materiales 47.654,86 (incluye Taval 2.289,95), MO y
   servicios 18.835,16 (Ledesma 8.350, horas 525 + 702, pintura 4.410, RX y LP 4.594,50, caución 253,66). **Total 66.490,02.**
3. Parámetros en `cotizacion.json` antes de correr: N = 18, `rx_pct` = 100 (oferta técnica: 100% RX), `ph_horas` = 8 (supuesto:
   la planilla no separa la PH de las 54 h de planta), `equipo.tipo` = manifold, `diametro_pulg` = 6, `FTV` = 1,
   `fecha_referencia` = 14-08-2026 (fecha de la oferta).
4. APP: `python herramientas/precotizar.py cotizaciones/CTRL-C01_PAMPA7_COLECTOR --excluir "PAMPA ENERGIA/7"` y
   `python herramientas/comparar_historico.py cotizaciones/CTRL-C01_PAMPA7_COLECTOR` → `cotizacion_auto.json`, `precotizacion.md`,
   `comparacion_historico.md`.
5. AGENTE: `cotizacion_agente.json`, armado con `buscar_material.py`, `buscar_servicio.py`, `buscar_antecedentes.py` y la estimación
   de horas, abriendo las fuentes. No usa nada de Pampa 7 ni de su copia en Pampa 5 (`ADICIONAL/ADICIONAL DE OC Colectores.xlsx`).
   Bases: lista Renard 12-2025 (bridas, caños, tees, tapones), planilla de Pampa 5 Rev2 del 26-06-2026 (válvulas Taval, bloqueo y
   purga, manómetros, tablero, horas, m² de pintura, ENOD), cotizaciones de proveedores de la carpeta de Pampa 5 (Ledesma 200283
   8.350, Valvtronic 3.586,58, MS Juntas 48.445), YPF/28, Tecpetrol/10 y Sacde/20 para niples, juntas y espárragos.
   `comparar_historico.py ... --json cotizacion_agente.json` → `comparacion_agente.md`. La herramienta escribe siempre
   `comparacion_historico.md`: se renombró la salida y se volvió a correr la de la app.
6. APP sin fuga (diagnóstico): la misma precotización con `--excluir "ADICIONAL DE OC"`, corrida en el scratchpad (no se guardó).

## Resultado (por colector, sin IVA, sin ajuste por inflación)
| | Total | vs REAL |
|---|---|---|
| REAL (planilla) | 66.490,02 | — |
| APP | 66.180,03 | −0,5% |
| APP sin fuga del propio proyecto | 73.918,11 | +11,2% |
| AGENTE | 69.702,46 | +4,8% |

El detalle por rubro y los 13 errores de la app, ordenados por impacto, están en `errores_app.md`. Los más graves:
1. Fuga: `--excluir` no saca el proyecto, porque una copia de su planilla está en la carpeta de Pampa 5 (esconde 7.738).
2. Radiografía con tarifa y servicios de otra empresa (+4.736).
3. Pintura solo de caños (−4.140).
4. Cotizaciones de proveedores fuera del catálogo; transmisor de otra marca (hasta +6.472 en el escenario sin fuga).
5. Soldadura propia + montaje de un antecedente armado por ITT, cuando el armado es de terceros (+3.012).

## Decisiones
- La comparación es contra el costo de la hoja "Colector RDA" (EXW, con caución de la hoja), no contra el Resumen (que suma
  1.500 de transporte y una caución de 354,91).
- Las columnas "Cant | REAL | Ahorro | Gasto de MAS | OC N°" de la planilla son compras posteriores a la adjudicación: no se
  usaron como costo real. Se citan como dato (por ejemplo, la válvula de 3 vías se compró a 4.215,21).
- No se modificó ninguna herramienta ni el catálogo. Los arreglos propuestos están en `errores_app.md`.
