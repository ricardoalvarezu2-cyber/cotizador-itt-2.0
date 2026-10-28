# CTRL-P01: errores de la app (puente de inyección y regulación 2" #600, Taval 70)

**Caso de control, no es una cotización.** Costos por puente, en USD, sin IVA y sin ajuste por inflación (fecha de cada fuente).
- **REAL**: planilla de ITT REV 1 del 26-10-2026 (`REV 1- OFERTA MEJORADA/Cot Puente Gas Lift SAP 1000653143 rev. 2 - PC0.xlsx`, hoja "Cotización rev 1"), que es la versión vigente. Se tomó solo el equipo EXW: no entran el transporte (2.400), la caución (244,43) ni la asistencia y los repuestos de puesta en marcha (2.357,50), que la REV 1 suma al costo unitario. Con esos tres conceptos da 73.561,53, igual que la planilla. La REV 0 (14-07-2026) costaba 77.675,38.
- **APP**: `precotizar.py --excluir "TAVAL/70"` sin completar nada a mano (`cotizacion_auto.json`, `precotizacion.md`, `comparacion_historico.md`).
- **AGENTE**: mi recotización con las herramientas y las fuentes abiertas, sin precios de TAVAL/70 (`cotizacion_agente.json`, `comparacion_agente.md`).

## Resultado por rubro (por puente)

| Rubro | REAL | APP | AGENTE | APP vs REAL |
|---|---:|---:|---:|---:|
| Piping: bridas, caños, tees, juntas, espárragos y sockolets | 5.326,24 | 6.650,32 | 6.685,64 | +25% |
| Válvulas Taval: esféricas, retención, filtro Y y válvulas chicas | 5.033,84 | 6.080,32 | 5.879,06 | +21% |
| Instrumentación y control: válvula de control, V-Cone, computador, inyector, temperatura y manómetros | 42.383,52 | 14.433,32 | 38.551,29 | **−66%** |
| Bastidor, soportes y canalizaciones | 2.000,00 | 0,00 | 9.990,07 | −100% |
| **Materiales** | **54.743,60** | **27.163,96** | **61.106,06** | **−50%** |
| Soldadura, prefabricado y skid (Ledesma / soldadura propia) | 7.200,00 | 6.017,29 | 8.600,00 | −16% |
| Montaje, PH, ingeniería y calidad | 1.818,00 | 969,00 | 1.851,50 | −47% |
| Granallado y pintura | 2.370,00 | 283,15 | 1.700,00 | −88% |
| Radiografía y LP | 2.428,00 | 5.150,00 | 2.884,00 | +112% |
| **MO y servicios** | **13.816,00** | **12.419,44** | **15.035,50** | −10% |
| **Total por puente** | **68.559,60** | **39.583,40** | **76.141,56** | **−42%** |

El AGENTE incluye 8.000 de canalizaciones eléctricas (pos 23, "8000 VERDES" en la lista de ingeniería), que la planilla real no costea. Sin ese renglón el AGENTE da **68.141,56 (−0,6% contra el REAL)**. Por renglón, el agente queda dentro de ±15% en 8 posiciones y la app en 5. Entre las dos diferencias más grandes del agente, el V-Cone se tomó de otra tecnología y no hay un precio real fuera del proyecto, y la brida 3" #600 se escaló desde la 2".

## Errores de la app, ordenados por impacto (USD por puente)

| # | Error | Evidencia | Impacto por puente | Corrección propuesta (herramienta) |
|---|---|---|---|---|
| 1 | **No reconoce la válvula de control.** "Válvula globo limitadora de caudal con actuador eléctrico" se busca como globo manual. El similar más parecido es una globo **manual Taval de 1"** de USD 80, que se descarta por diámetro, y el renglón queda SIN PRECIO. El catálogo sí tiene válvulas de control Doma y Fisher. | `precotizacion.md` pos 8; `buscar_material.py "...globo 2\" #600 ... actuador"` lee tipo=globo | **−17.200** (REAL) / −16.412 (AGENTE) | `catalogo_materiales.familia_de`/tipo: "con actuador", "limitadora", "control", "FV-" → tipo `control`. Una globo manual nunca es similar de una de control |
| 2 | **Marca como Taval (factor 1) una válvula de control de terceros.** La pos 8 sale con `"taval": true` porque el similar *descartado* (globo Taval 1") es Taval. Cuando Compras cargue el precio, la válvula se vende sin margen | `cotizacion_auto.json` pos 8: `taval: true`, precio 0. `precotizar.material()` decide `taval` con `elegido` antes de descartarlo por diámetro | 0 en costo · **−6.020 en precio de venta** (2 × 8.600 × 0,35) | Marcar `taval` solo si la fuente aceptada es Taval o si lo dice `modelo_fabricante`; nunca con un similar descartado |
| 3 | **Computador de caudal SIN PRECIO** aunque el catálogo tiene el ABB XFC6200EX (USD 7.345,97, cot. OPP-26-8794766 del 16-07-2026, TAVAL/69). Esa fila (INS-01575) junta varios ítems y su "último precio" quedó en **864,20** (el PGS300). Además, "computador de caudal" no encuentra "flow computer" | `catalogo_materiales_historial.csv` INS-01575; `Cot ABB OPP-26-8794766-1.pdf.txt` ítem 3 | **−8.424** (REAL) / −7.346 | Separar las filas con varios ítems (es el error 28, que se repite); sinónimos computador de caudal / flow computer / FQIT / multivariable |
| 4 | **RX con tarifas viejas y servicios mal contados.** Toma Antonelli 11-2025 de `tarifas.csv` (placa 15, servicio 490) y no la lista DB NDT del 14-08-2026 del catálogo de servicios (placa 6,50, servicio 408). Cuenta 1 servicio cada 40 placas *por puente* (5 por puente) en una serie de 24. No suma LP para las 30 juntas SW/olet que no se radiografían | `precotizacion.md` §3: 180 placas + 5 servicios = 5.150; END-00211/END-00256 | **+2.722** (5.150 contra 2.428) | Tarifa desde `catalogo_servicios` (la más reciente con el mismo alcance); servicios repartidos en la serie (N); LP para SW y olets cuando `rx_pct` deja juntas sin RX |
| 5 | **Pintura solo de los caños.** Da 5,66 m², contra 38 m² reales (piping 20 y skid 18): faltan bridas, válvulas, accesorios, instrumentos y el bastidor de 1.050 kg | `precotizacion.md` §3 | **−2.087** | Sumar m² de bridas y accesorios (`bridas_peso.csv`, `accesorios_peso.csv`), válvulas por diámetro y bastidor por kg (m²/t de perfil); sobrepintura según criterio ITT |
| 6 | **V-Cone cotizado con un caudalímetro electromagnético Krohne** (USD 4.200), marcado "similar" con solo "faltan: rango, conexión". Es otro principio de medición | `precotizacion.md` pos 12 → INS-02682 | **+2.040** | El tipo de instrumento tiene que incluir el principio (V-Cone, Coriolis, electromagnético, placa orificio). Si el principio es otro, queda SIN PRECIO con referencia |
| 7 | **Bastidor SA-36 por kg SIN PRECIO.** La regex de `acero_kg` no reconoce "SA-36" ni "A-36" (con guion), ni "bastidor", "perfil" o "HEB". Aun reconocido, un perfil HEB se pagaría como chapa negra lisa (no hay precio de perfiles en `acero_por_kg.csv`) | prueba: `acero_kg({'material':'SA-36'})` → None; `'Perfil HEB 200'` → chapa | **−1.800** (bastidor) − 200 (U-bolts) | Regex `s?a-? ?36`, sumar bastidor/perfil/HEB/IPN/UPN/soporte; cargar precio de perfiles laminados |
| 8 | **Horas de montaje, ingeniería y calidad tomadas de un equipo de otra escala.** Usa el puente de producción 3" de TAVAL/43 (serie de 442, materiales USD 3.789) para un skid de medición de USD 55.000 con 46 uniones bridadas e instrumentos: 27 h de montaje contra 126 h reales (con PH) | `precotizacion.md` §3; `estimar_horas.puntaje` | **−849** (969 contra 1.818) | En `estimar_horas` pesar más la escala (materiales, posiciones, uniones bridadas). Si el antecedente es más de 3 veces más chico, avisar en rojo |
| 9 | **No contempla MO de terceros ni la fabricación del bastidor.** Calcula soldadura propia a 19,73 USD/pulg (costo de planta de 10-2024, el más viejo vigente; las planillas 2026 usan 16) sobre 305 pulgadas. El catálogo tiene un presupuesto de Ledesma del mismo alcance (FAB-00052, skids de regulación y medición, 8.600 c/u) | `cotizacion_auto.json` S01; `buscar_servicio.py "skid regulacion y medicion"` | **−1.183** (6.017 contra 7.200) | Ofrecer el presupuesto de terceros del mismo alcance como alternativa a la soldadura por pulgada; actualizar o avisar la tarifa de 2024 |
| 10 | **"WNRF", "SWRF" y "SA-105 / SA-106 / SA-234 / SA-216" no se leen.** Se pierden el tipo, la cara y el material, así que nunca da IGUAL: la brida 3" se cotiza con una **de 2"** (28,42), la 2" con una "similar" en lugar de la cotización Renard igual, y el caño 3" con un similar (30,30) en lugar de la lista Renard igual (33,93) | `buscar("Brida WNRF 2\" #600 SA-105")` → faltan tipo y material; con "WN RF A105" da IGUAL | **+445** (pos 1, 2, 4 y 6) | En `norm`/lector: WNRF→WN RF, SWRF→SW RF, SORF, BLRF; "SA-1xx" → "A1xx" |
| 11 | **Espárrago mal medido.** `texto_busqueda` pega la columna diámetro a la descripción: "5/8 x 5" + "5/8"" = "5/8 x 5 5/8"". Además el lector toma el largo (5") como diámetro. Elige uno de 10 USD | `precotizacion.md` pos 20: "pedido 5/8 x 5 5/8"; `buscar_material "Esparrago 5/8 x 5\""` → diametro=5" | **+736** (368 × 2) | No agregar el diámetro si la descripción ya lo tiene; en espárragos, el primer número es el diámetro y el segundo el largo |
| 12 | **#3000 tomado como "serie 300".** La esférica 1" #3000 (forjada roscada, WOG) se cotiza con una 1" **#300 bridada** (67,50) como simple "diferencia de serie". El catálogo tiene la Taval 1" WOG 3000 NPT A105 a 51,05 | `precotizacion.md` pos 22 → VAL-03219 "1" #300" | **+638** (1.080 contra 441,84) | Las clases 2000/3000/6000 (forjadas) y 150–2500 (bridadas) son tipos distintos: no son similares |
| 13 | **Retención 2" con precio de una de 3"** (420,16). La regla de 1,6 veces deja pasar 3"/2" = 1,5. Con la escala Taval 3"/4" da 255,83 (real 254) | pos 9 → VAL-03316 | **+332** | En válvulas, bajar el límite a ~1,3 o escalar por la relación de precios de la misma línea |
| 14 | **No avisa posiciones duplicadas.** La lista repite la junta 2" #600 (pos 11: 48 y pos 19: 46; los 368 espárragos = 46 × 8). La app cobra las dos; la REV 1 sacó la 11 | pos 11 y 19 | **+288** | Avisar en `precotizar.py` las filas con la misma descripción, diámetro y serie |
| 15 | **Soldaduras sobrecontadas.** "Cada extremo BW de accesorio o brida = una junta con caño" cuenta dos veces las juntas brida–accesorio directas: 86 juntas BW contra 64 de la planilla (6 de 3" y 58 de 2") | `precotizacion.md` §2 | 0 directo (la soldadura real va en el global de Ledesma); +~50 placas de RX | Columna opcional de juntas directas, o pedir el conteo del isométrico cuando el caño va por metro |
| 16 | **Filtro Y y sockolet 1" SIN PRECIO.** Había referencias escalables: filtro Y 2" #150 WCB a 106,14 (OTR-02961) y sockolets 3/4" y 1 1/2" | pos 10 y 18 | −840 | Similar de otra serie o diámetro con escala explícita (`est`), en vez de 0 |

**Cómo se explica la diferencia total (−28.976):**
- Los errores 1, 3, 5, 7, 8, 9 y 16 bajan la app 32.583.
- Los errores 4, 6 y 10 a 14 la suben 7.201.
- El resto (−3.594) no es error de la app:
  - el inyector de químicos (−4.200), que la oferta excluye pero la planilla real cobra;
  - los ítems que no están en la lista de ingeniería (manifold de 5 vías, botellones y U-bolts, −1.798);
  - las 10 esféricas de la lista contra 8 en la REV 1 (+832);
  - el transmisor de temperatura, cotizado con un similar más caro (+1.431).

## Fallas de herramientas (sin impacto directo en el número)

- `buscar_antecedentes.py` y `buscar_servicio.py` no tienen `--excluir`. En un caso de control muestran primero el propio proyecto: TAVAL/70 sale #1 en antecedentes y FAB-00061 es el Ledesma 7.200 del mismo proyecto.
- `comparar_historico.py`:
  - si el real es 0 y la app cobra, la lectura dice "más barato" (pos 11: 288 contra 0);
  - un 0 intencional (ítem excluido) se cuenta como "SIN PRECIO en el catálogo";
  - los ítems del cotizador sin posición en `historico.csv` se ignoran sin aviso;
  - corrido con `--json` pisa `comparacion_historico.md`: no tiene salida propia.
- `precotizar.py`:
  - informa "materiales USD 27.164 por equipo" sin decir que los 7 SIN PRECIO pesan el 55% del material real;
  - no estima transporte: la REV 1 entrega en Neuquén a 2.400 por puente.
- `buscar_material.py`: "Tee 2" sch 80" devuelve como IGUAL una **tee de reducción** 2"x1 1/2". En el catálogo, ABW-00373 junta la tee normal (24,06) y la de reducción (33,59) con un mismo código.

## Errores del catálogo detectados (afectan a otras cotizaciones)

- **VAL-02268:** la válvula de control Doma 667 EZ 3" #300 (8.206) está indexada a **USD 1.380**, que es el c/u de las PSV del mismo renglón (`Oferta Doma P-06823.pdf.txt`).
- **INS-01575:** el renglón ABB OPP-26-8794766 junta Coriolis, XFC6200EX y PGS300. Su último precio es 864,20.
- **TAVAL/70:** conviven la REV 0 y la REV 1 del mismo ítem con códigos distintos (retención 133,67 / 254; filtro Y 195,93 / 378; esférica 400,40 / 416). Todos tienen fecha 25-06-2026, pero los de la REV 1 son del 26-10-2026. Va contra "una sola versión vigente, con fecha".

## Observaciones sobre la planilla real (no son errores de la app)

- La REV 1 suma al costo unitario la asistencia de puesta en marcha y los repuestos (2.357,50). Esos mismos ítems se ofrecen además como **opcionales** (6.365,25): se cobran dos veces.
- El **inyector de químicos** (4.200 por puente, 5.670 de venta, ×24 = 136.080) está costeado, pero la oferta dice que se excluye.
- Las **canalizaciones** de la pos 23 ("8000 VERDES") no se costean, aunque el checklist dice "Instalación eléctrica: SI".
- La REV 0 duplicaba las juntas (48 + 46) y el bastidor (6.000 kg contra 1.050 kg de la lista). La REV 1 lo corrigió.
- La lista tiene 2 V-Cone, 2 FV y 2 FQIT por puente. La hoja de datos (I-HD-003004) lista un solo FE, FQIT y FV por locación tipo 1: **hay que confirmar si la lista es por puente o por par** (SK-2104/SK-2105).
