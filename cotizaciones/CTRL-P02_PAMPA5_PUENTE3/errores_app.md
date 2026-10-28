# CTRL-P02: errores de la app (puente de producción 3" #300, Pampa 5, Rincón de Aranda)

**Caso de control, no es una cotización.** Costos por puente, en USD, sin IVA y sin ajuste por inflación (fecha de cada fuente).
- **REAL**: planilla de ITT `PAMPA ENERGIA/5 .../4.Armado de la Oferta Comercial/Cot Skid Manifolds Colectores RDA Rev2.xlsx`, hoja "Puentes" (PRES 163 rev. C del 16-07-2026; la Rev 3 de `ADICIONAL/` tiene la hoja de puentes idéntica). Solo el equipo EXW: materiales, MO y servicios 4.327,99 + instrumentos ABB 3.107,58 + válvulas Taval 1.401,40 = **8.836,97**. No entran la caución (381,24) ni el transporte del Resumen (215,83).
- **APP**: `precotizar.py` sin completar nada a mano (`cotizacion_auto.json`, `precotizacion.md`, `comparacion_historico.md`). Comando exacto:
  `python herramientas/precotizar.py cotizaciones/CTRL-P02_PAMPA5_PUENTE3 --excluir "PAMPA ENERGIA/5" --excluir "PAMPA ENERGIA/7"`
  y después `python herramientas/comparar_historico.py cotizaciones/CTRL-P02_PAMPA5_PUENTE3`.
- **AGENTE**: recotización a mano con las herramientas y las fuentes abiertas, sin precios de Pampa 5 ni Pampa 7 (`cotizacion_agente.json`, `comparacion_cotizacion_agente.md`).
- Parámetros: N = 10, `rx_pct` = 100 (oferta técnica: 100% RX y LP donde no se pueda), `ph_horas` = 4 (supuesto: la planilla no costea la PH), `equipo.tipo` = puente, `diametro_pulg` = 3.

## Resultado por rubro (por puente)

| Rubro | REAL | APP | AGENTE | APP vs REAL |
|---|---:|---:|---:|---:|
| Piping: bridas, caños, accesorios, olets, niples, juntas, espárragos y tuercas | 1.891,99 | 2.543,18 | 1.526,33 | +34% |
| Válvulas Taval (esféricas 2", 3", 1" y 3/4") | 1.401,40 | 1.775,63 | 1.456,09 | +27% |
| Instrumentos (TT, PT y manómetro) | 3.107,58 | 2.023,00 | 2.750,20 | −35% |
| **Materiales** | **6.400,97** | **6.341,81** | **5.732,61** | **−1%** |
| Soldadura y armado (Ledesma / soldadura por pulgada) | 1.300,00 | 1.183,34 | 1.120,00 | −9% |
| Radiografía y LP | 841,00 | 1.038,30 | 1.485,00 | +23% |
| Granallado y pintura | 295,00 | 310,65 | 300,00 | +5% |
| PH, ingeniería, calidad y montaje ITT | 0,00 | 1.281,40 | 246,00 | — |
| **MO y servicios** | **2.436,00** | **3.813,69** | **3.151,00** | **+57%** |
| **Total por puente** | **8.836,97** | **10.155,50** | **8.883,61** | **+15%** (AGENTE +0,5%) |

- La app deja **un solo renglón SIN PRECIO** (pos 2, anillo BX153: 10,00 en el real). Sin ese renglón, REAL 8.826,97 contra APP 10.155,50 (**+15,0%**).
- El total de materiales de la app "da bien" (−1%) por **compensación**: tuercas cobradas aparte y caras (+631), Taval con otro descuento (+374) contra instrumentos incompletos (−1.085).
- El AGENTE da +0,5%, pero también compensa:
  - suma 246 de horas ITT y 257 del manómetro con bloqueo y purga (la planilla no los costea);
  - usa la RX con la tarifa de TAVAL/43 (+644), porque la lista DB NDT solo está en Pampa 5 y 7;
  - pone el transmisor de temperatura ABB 714 más barato y los espárragos 412 más baratos.
- Por renglón, el AGENTE queda dentro de ±15% en 22 posiciones y la APP en 12.

## Errores de la app, ordenados por impacto (USD por puente)

| # | Error | Evidencia | Impacto | Corrección propuesta (herramienta) |
|---|---|---|---|---|
| 1 | **Horas de montaje de otro tipo y otra escala** (sigue el error 58). Montaje 85,2 h (1.107,60), más 4 h de ingeniería, 4 h de calidad y 4 h de PH: 1.281,40 en total. La mediana mezcla el puente de TAVAL/43 (30 h × 0,92) con dos skids de medición (E+H 121,5 h y TAVAL/70 126 h). El "antecedente" que muestra es el puente **4"** de TAVAL/43, aunque en `horas_por_equipo.csv` está el puente **3"** de la misma planilla (27 h de montaje y 10 h de ingeniería y calidad). Además, el mismo equipo da 85,2 h desde `precotizar` y 128,7 h desde `estimar_horas.py puente 3 --unidades 10 --materiales 6000 --pulgadas 70`: el resultado es inestable | `precotizacion.md` §3; `estimar_horas.py` | **+1.281** (REAL 0; la Ledesma 200284 incluye el armado) · +1.035 contra el AGENTE | `estimar_horas`: si hay antecedentes del mismo tipo, no mezclarlos con otro grupo (skid de medición ≠ puente); preferir el mismo diámetro antes que materiales parecidos; avisar cuando el rango del tipo (27–126 h) es más de 3 veces; no sumar montaje propio cuando el armado es de terceros |
| 2 | **Instrumentos mal identificados.** (a) El TT "ABB TTF200" se cotiza con el TIT de TAVAL/70 (803), que es **solo el transmisor**: la HD-6311 pide RTD Pt100 integral y vaina (en TAVAL/70 van aparte, a 689). (b) El PT "ABB PGS300" se cotiza con un transmisor **Vega** de TAVAL/49 (1.100), cuando el catálogo tiene el **ABB PGS300 a 864,20** (OPP-26-8794766, 16-07-2026, INS-01575): no usa `modelo_fabricante` para elegir y el renglón INS-01575 sigue mezclando ítems (error 62). (c) No suma la válvula de bloqueo y purga que piden la HD-6310 (nota 1) y la HD-6312 (nota 4) | `cotizacion_auto.json` M38, M40; HD en `PUENTE DE PROD/` | **−1.085** contra el REAL (TT −1.403, PT +198, manómetro +120) · −727 contra el AGENTE | Buscar por modelo (`modelo_fabricante`) antes que por descripción; un TT "integral con RTD y vaina" es transmisor + sensor + vaina (sumar las tres piezas o avisar); la marca del plano manda (Vega ≠ ABB es desvío); leer "c/ manifold" como pieza aparte |
| 3 | **Tuercas cobradas dos veces y con el precio de una de 1 7/8".** El plano lista tuercas (pos 32 y 34, 144 un) y espárragos aparte. La app cotiza los espárragos con precios de "espárrago con 2 tuercas" (7,82 por juego y 10) y además las tuercas a 4,38 c/u, que es el precio de una **TUERCA 2H 1 7/8"** (JUN-01778). El catálogo tiene tuercas 5/8" y 3/4" 2H a 0,43–0,53. "1 7/8"" no se lee como diámetro y el similar sin diámetro gana al del mismo diámetro | `precotizacion.md` pos 32 y 34 | **+631** | Leer diámetros mixtos con espacio ("1 7/8"", "1 1/8""); un similar sin dato de diámetro nunca le gana a uno del mismo diámetro; si el espárrago elegido es "con 2 tuercas" o "juego", poner las tuercas del plano en 0 con aviso |
| 4 | **Válvulas Taval sin la lista oficial.** `fuentes_originales/taval_lista30_2025-09.xlsx` (Lista 30) no está en el catálogo. La app toma precios de planillas con otro descuento: TECPETROL/10, Lista 30 −35% (2" 170,30; 3" 319,80), y la 1" #3000 **inoxidable/galvanizada** de TAVAL/49 a 113,88 como similar de una A105. La 3/4" sale con una WOG 2000 de Sacde 15 (33,81) sin proveedor, por eso no la marca Taval y le aplica factor 1,35 | `cotizacion_auto.json` M09, M11, M15, M26 | **+374** contra el REAL (+320 contra el AGENTE: Lista 30 × 0,52 = 136,00 / 256,00 / 53,22 / 43,60) · +106 en la venta por la 3/4" sin marca Taval | Cargar la Lista 30 de Taval al catálogo como `lista` (código, serie, paso, material) con el descuento vigente en un solo parámetro; en válvulas, el material (A105 / inox / galvanizado) es excluyente para "similar" |
| 5 | **RX con tarifa del propio proyecto excluido y servicios de más.** La tarifa DB NDT sale de `costos/tarifas.csv` con fuente "PAMPA ENERGIA/5 y /7": `--excluir` no filtra `tarifas.csv` (solo el catálogo). Con N = 10 cuenta 1,3 servicios de RX por puente (40 placas por servicio), cuando la planilla real hace 1 por puente (44 placas). Pone 51 placas contra 44: cuenta 17,5 juntas con el thredolet como si fuera una junta a tope | `precotizacion.md` §3; `tarifas.csv` filas 46–49 | **+197** (1.038,30 contra 841) · sin la fuga, con Antonelli, daría 1.696 (+855) | Aplicar `EXCLUIR` también a `tarifa()` (`tarifas.csv`) y al catálogo de servicios; avisar cuando la tarifa viene del proyecto excluido; parametrizar placas por servicio (una jornada ≈ 45–50 placas) |
| 6 | **Brida WNRF 3" #300 cotizada con una brida ROSCADA BSPT #150** (Renard 8938, "Bridas RO BSPT 3" S150", 30,33), cuando Renard tiene la WN 3" sch 40 S300 RF (11978, 40,98) igual. Sigue el error 10 de P01: "WNRF" no se lee, se pierde el tipo y el ranking elige otra serie y otro tipo. Lo mismo en la 2" #300 sch 80, que sale con una #600 (28,42) teniendo la Renard 12052 a 23,95 | `precotizacion.md` pos 7 y 22 | **−85** (8 × −10,65) y +4 · si llega así a Compras, se compran bridas roscadas #150 para un puente #300 | En `norm`: WNRF → WN RF, SWRF, SORF, BLRF; el tipo de brida (WN/SO/RO/SW/ciega) y la serie son excluyentes para "similar" |
| 7 | **Compra extra de caño por posición y con barra de 6 m.** El plano da 8 tramos de caño 3" (5.173, 258, 722, 205, 215, 105, 254 y 100 mm). La app completa una barra **por cada tramo**: 8 filas "b", que suman 102 m comprados para 70,3 m usados. Además el caño Renard 1153 se vende en barras de 10,5 a 12,5 m, no de 6 | `precotizacion.md` filas 5b, 21b, 25b, 28b, 29b, 30b, 35b y 36b | **+71** (3,17 m extra por puente contra 0,17 m) | Agrupar los tramos del mismo caño (Ø, sch y material) antes de calcular las barras; largo de barra según la fuente (Renard 12 m) |
| 8 | **Soldadura: el thredolet se cuenta como un extremo BW de 3/4"**, no como un olet sobre el caño. Deja 35 extremos BW (impar) y el aviso "falta marcar algún extremo de campo", que confunde | `precotizacion.md` §2 | +63 contra el AGENTE (73,96 contra 70 pulg) · −117 contra la Ledesma real | Tratar thredolet, sockolet y weldolet igual (olet × 1,75); el aviso de impar tiene que decir qué posición lo produce |
| 9 | **Sockolets "3" x 3/4"" leídos como Ø 3".** Toma una de 1/2" (10,00) y, para la de 3" x 1", un estimado del cepo de 2025 (15,59) | pos 4 y 17 | +43 contra el REAL (−23 contra el AGENTE) | En olets, el Ø de la pieza es la salida (el segundo número), como ya se hace en soldadura (error 52) |
| 10 | **Espárrago "5/8 L=3 1/2 (90 mm)" sin diámetro:** cotiza un espárrago de 1 1/8" x 7" (7,82 por juego). Sigue el error 11 de P01 con otro formato ("L=") | pos 33 | −35 contra el REAL (+69 contra el AGENTE) | Leer "Ø × L=", "L=" y largos en mm; el diámetro es el primer número |
| 11 | **Catálogo: juntas espiraladas leídas como espárragos.** La cotización MS 48.445 dice "ESP SWI AC 316LFG 316L Ø2" 3/4/600" (2,30) y "Ø3"" (3,98): son juntas espiraladas para las series 300, 400 y 600, pero el catálogo las cargó como "espárragos" (JUN-03461 y JUN-03462). La app cotiza las juntas a 5,00 y 7,00 | catálogo JUN-03461/3462 | +12 contra el REAL (+30 contra el AGENTE) | "ESP SWI / ESP SW" = junta espiralada en la extracción de proveedores; "3/4/600" es serie 300-400-600 |
| 12 | **Anillo BX153 SIN PRECIO.** "Anillo octogonal RTJ-10K BX 153" se clasifica en la familia OTR. El catálogo tiene el BX153 en la familia JUN: 6,60 de MS (JUN-03463, Pampa 4) y 6,01 de TAVAL/43 | pos 2; `buscar_material.py "anillo BX 153 RTJ"` → "No hay precios" | −10 | Familia JUN para "anillo", "ring joint", "RTJ", "BX", "RX" |
| 13 | **Fecha imposible en la soldadura:** S01 sale con `"fecha": "2026-02-31"` (concatena "-31" a "2026-02"), y `numeros.a_vista` la muestra como "31-02-2026" sin validar. Al ajustar por inflación o al armar puede fallar o tomar un mes equivocado | `cotizacion_auto.json` S01 | 0 directo · riesgo de falla en `armar_cotizacion` | Último día real del mes (`calendar.monthrange`); `numeros.a_vista` y `fecha_iso` tienen que rechazar fechas inválidas |

Lo que explica la diferencia total (+1.318,53):
- Los errores 1, 3, 4, 5, 7 y 9 suben la app 2.597.
- Los errores 2, 6, 12 y la soldadura contra la Ledesma la bajan 1.297.
- El resto (+19) son diferencias chicas de precio:
  - el codo 45° de Cintolo a 17,49 contra la lista Renard a 12,13; las dos fuentes son iguales y la app toma la más nueva;
  - juntas, niples y espárragos.

## Fallas de herramientas (sin impacto directo en el número)

- **`buscar_antecedentes.py --excluir` no se puede repetir:** con `--excluir "PAMPA ENERGIA/5" --excluir "PAMPA ENERGIA/7"` vale solo el último, y **Pampa 5 sale primero** (puntaje 86). `precotizar` y `estimar_horas` sí aceptan varios (`action="append"`).
- `buscar_material.py` y `buscar_servicio.py` siguen sin `--excluir` (error 12 de la auditoría): para la RX y la pintura, lo primero que muestran es Pampa 7.
- `buscar_material.py` no lee la serie sin "#": "brida WN RF 3" 300 sch 40" da "Faltan: serie".
- `--excluir` es por carpeta y el mismo documento está copiado en varias. La cotización Francovigh O00093778 está tres veces en el catálogo (BRI-01337 de Pampa 5, BRI-01338 de Pampa 4 y BRI-01339 de Pampa 7), y la de MS 48.445 dos veces (JUN-03463 y JUN-03599). Al excluir Pampa 5 y 7, el precio entra igual por Pampa 4. Acá es legítimo, porque Pampa 4 es otro pedido, pero va contra "una sola versión vigente". Hay que deduplicar por documento (proveedor + número + fecha).
- La copia de Pampa 7 en `PAMPA ENERGIA/5/ADICIONAL/ADICIONAL DE OC Colectores.xlsx` sigue en el catálogo (VAL-03184, INS-02707, INS-02713 y otros; error 8). Acá no afecta, porque se excluyen las dos carpetas.
- **Unidad del caño:** el plano da el caño en "1 un, L = 5.173 mm" y la app lo pasa a 5,173 m. El criterio técnico es correcto, pero no respeta "misma cantidad y unidad que el plano" (P2): `verificar_computo` lo va a marcar, o hay que documentar la conversión.
- `comparar_historico` sigue contando un 0 intencional (las tuercas incluidas en el espárrago del AGENTE) como "SIN PRECIO en el catálogo" (P01).
- `precotizar` no avisa que el plano lista tuercas aparte de los espárragos, ni que el precio elegido para el espárrago ya trae tuercas.

## Lo que se corrigió desde los controles anteriores (verificado en este caso)

- **Pintura:** da 6,21 m², contra 5,9 de la planilla (+5%). Antes, en P01, daba −88%.
- **RX:** usa la tarifa vigente DB NDT y reparte los servicios en la serie. Queda la fuga del error 5.
- **Soldadura:** la tarifa es 16 USD/pulg y el conteo queda cerca del real (73,96 contra unas 70 pulg; 17,5 juntas contra 15 de la planilla). Ya no hay doble conteo grave.
- **`comparar_historico`:** ahora escribe una salida propia con `--json`.
- **Similares por diámetro:** la regla de 1,6 veces funciona. Siguen los similares de otro tipo o material (errores 4 y 6).

## Observaciones sobre la planilla real (no son errores de la app)

- La planilla es del 26-06/16-07-2026 sobre los isométricos IS-6310. El plano constructivo PL-6430 rev. A es del 22-07-2026 y trae diferencias: 8 bridas WN 3" (la planilla compra 6), 8 juntas 3" (compra 7) y 2 tapones 3/4" (compra 3). La brida WN 2" la toma sch 40 ("Considero sch40"), pero el plano dice sch 80.
- **No costea la PH** (78 kg/cm²), ni horas de ingeniería, calidad y dossier, ni movimientos. La Ledesma 200284 (1.300) dice "NO INCLUYE PH, END, pintura ni montaje".
- **No costea** el manómetro (pos 39) ni las válvulas de bloqueo y purga que piden las HD-6310 y HD-6312.
- Los 72 espárragos son "Estimado" a 10 c/u (720 por puente). Con una cotización real (Delgado, escala por kg) serían unos 330.
- Los instrumentos se cotizaron "Rosemount" en la oferta (Resumen con factor 1,5, plazo 90/110 días) y ABB en la hoja de puentes (factor 1,35). La OC final pide Rosemount 3051S2TG.
- "131.131" (válvula esférica 2") es 131,13 en formato de máquina de Excel (error 39). Se verificó con el subtotal 1.401,40.
