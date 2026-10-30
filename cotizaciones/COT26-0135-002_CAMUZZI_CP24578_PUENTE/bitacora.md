# Bitácora COT26-0135-002 · Camuzzi CP 24578 ítem 3 · Skid puente de medición (ERP Parque Industrial Tres Arroyos)

**Estado: borrador, sin revisar.** Mismo concurso que COT26-0135-001 (ver su bitácora para el pedido).

## Qué se hizo
1. Tabla del plano SCE-ME-315-039 transcripta (`pedido/lista_materiales_plano.csv`). Caños sin cantidad en el plano: medidos del dibujo, 4" ≈ 8 m (bypass 3.961 + 1.213 + 911 mm y línea 452 + 1.100 + tramos), 6" ≈ 1 m.
2. La turbina la provee Camuzzi (especificación §4): pos 2 es un carretel provisorio de 300 mm (2 bridas WN 4" + 0,3 m de caño, 90 estimado).
3. Correcciones (`armar_json.py`):
   - Pos 1 filtro FM-6 #150 simple módulo: **9.000 estimado** (el FM-6 #300 de CAMUZZI/23 se vendió a 13.543 → ~10.000 de costo; el FM3 S150 de TAVAL/40 costó 5.575 y el FM8 S600 14.375). Pedir cotización de tapa y elemento.
   - Pos 3: esférica 6" PT Taval Lista 30 (740). precotizar había tomado una Esferomatic galvanizada de 3.500 (error de selección: ver lecciones).
   - Pos 11: termovaina estimada 120. Pos 13: skid 200 kg + fabricación por kg. Pos A: transmisor de temperatura ABB 1.448.
   - Ingeniería 20 h y calidad 40 h por criterio: el antecedente que eligió `estimar_horas` (puentes en serie de 442 unidades) da 7,5 y 3,5 h, que no alcanzan para un equipo único con aprobación de Camuzzi.
   - Media tira de 6" (6 m) y juntas/espárragos internos (6 de 4", 4 de 6").
4. Precio: **29.641** (borrador). Los antecedentes que compara la herramienta (puentes con V-Cone e instrumentos, 97.000–101.000) no son del mismo alcance: no llevan filtro FM y sí caudalímetros.

## Revisión independiente (28-10-2026, agente que no armó el cómputo)
Transcripción del plano y cantidades: bien. Precios Tormene y Taval verificados contra los originales. Corregido:
- Juntas internas de 6": 3 (no 4) y 24 espárragos. Prueba de fugas con N2: renglón propio (250 estimado).
- **Sigue abierto:** el filtro FM-6 (9.000 estimado) es el 44% del costo y sale de una venta de 2025 de un FM-6 #300: costearlo por componentes con el plano tipo SCE-RE-112-0004 o pedir cotización.
- Flete: si se adjudican los ítems 2 y 3 juntos, va un solo viaje (hoy cada uno suma su flete).

## 29-10-2026 · Lista igual al plano (pedido de Matías)
- `pedido/lista_materiales_plano.csv` corregida para que descripción y MATERIAL/OBS. digan lo mismo que el plano (antes había materiales reinterpretados, "RF" y "radio largo" agregados y textos cortados a 60 caracteres por `precotizar.py`, ya corregido). Lo que agrega ITT (planos tipo, kg estimados, largo medido de los caños) pasó a la columna `modelo_fabricante`.
- Tes en ASTM A-105 y cupla en ASTM A-106 como dice el plano: se sacaron los desvíos "se cotiza A-234 WPB / A-105"; el precio es de la pieza similar y Compras pide la del plano.
- Esféricas: marca del listado de Camuzzi (Taval no figura); precio Taval de la misma especificación como referencia y sin el factor de válvulas Taval (ahora llevan 1,35).

## 30-10-2026 · Compatibilidades revisadas
Pos 16 (cupla c/ válvula esférica, A-106): SIN PRECIO. Unitario USD 29.395,10.

## 30-10-2026 · Auditoría independiente de compatibilidades
- Pos 5c (espárragos 5/8" B7 + 2H): la referencia era B7M (no reemplaza a B7). Pasa a JUN-04173 (B7/2H zincado con 2 tuercas, 5/8" × 110 mm), USD 10 c/u, planilla TAVAL/43 (19-02-2026, línea 147); valor que parece global: **pedir cotización**.
- Pos 14 y 14b (caño 4" sch 40 A-53 Gr B): la lista de Renard dice "A53A" (grado A, cód. 1008). Pasa a cód. 1160 "Tubo s/costura 114,3 x 6,02 mm A53/A106/API 5L B", USD 34,34/m (misma lista, verificado en el original). Cantidades sin cambio.
- Unitario USD 30.040,50 (antes 29.395,10); total USD 30.644,62. Borrador, sin revisar.

## 30-10-2026 · Segunda auditoría independiente
- Pos 15/15b (caño 6" sch 40 A-53 Gr B): Renard "A53/135" sin grado → cód. 1173 sin costura A53/A106/API 5L B, USD 60,51/m (verificado en la lista).
- Pos 6b (junta 6" #150): la de MS Juntas es 8" #300 → SIN PRECIO, pedir cotización.
- Pos 5c: el precio de USD 10 pasa a estimado.
- Unitario USD 30.102,40; total USD 30.706,52. Borrador, sin revisar.

## 30-10-2026 · Tercera auditoría independiente
- Pos 6c: USD 10 de la planilla Techint/12 pasa a estimado. Total sin cambio: unitario USD 30.102,40.

## 30-10-2026 · Revisión completa (pedido de Matías: "revisar por completo los presupuestos de Camuzzi")
Borrador, sin revisar. Antes: unitario USD 30.102,40, total USD 30.706,52 (con flete). Después (`armar_cotizacion.py`): **unitario USD 31.122,70, total USD 31.726,82**. Lo estimado bajó del 56% al 16% del costo directo.

**`armar_json.py` reescrito:** ahora fija todas las fuentes, filas agregadas, MO, servicios, plazo y textos (antes las correcciones de las tres auditorías del 30-10-2026 estaban solo en `cotizacion.json` y correrlo de nuevo las deshacía; ver errores). También completa `oferta.json` (exclusiones de la turbina y de los manómetros, garantía con vicios ocultos) después de `camuzzi_comun.oferta`, sin tocar `camuzzi_comun.py`.

**Requisitos:** `pedido/requisitos.csv` con 114 requisitos literales (planilla, cláusulas particulares, DDJJ, CGP, ET SCE-ME-515-0030 y plano), cada uno con destino. Quedan 4 consultas (7 renglones) redactadas en `consultas_cliente.md`: C1 manómetros de la ET §5.7 (el plano no los lista), C2 sensor A, C3 cupla A-106 (pos 16), C4 tes A-105 (pos 7 y 8).

**Materiales:**
- Pos 1 filtro FM-06: el estimado de USD 9.000 salía de una **venta** de 2025 con cepo (CAMUZZI/23, 06-03-2025) de un FM-6 #300. Ahora se costea por componentes con la planilla TAVAL/40 (15-01-2026) como modelo y la configuración del FM6 S150 de la OE 260-23 (cuerpo 12", toberas 6", tapa de cierre rápido): 1b caño 12" sch 40 (Renard 1200, 177,72/m × 1,5 m estimados), 1c casquete 12" (Renard 3438), **1d tapa de cierre rápido 12" #150: Megatap 2026-143 (19-05-2026) USD 2.480** como referencia de precio (Megatap no está en el listado: comprar Futura/Gora/Peco/EKA), 1e elemento (Metpor del FM8, TAVAL/40), 1f/1g toberas, 1h manómetro diferencial + manifold + conexiones (TAVAL/40 FM3, 950), 1i internos y refuerzos (TAVAL/40 FM3, 427,50). La fila 1 queda en 0 con `sin_precio_motivo` (se suma por componentes). El plano tipo SCE-RE-112-0004 no está: largos y refuerzos a confirmar.
- Pos A: la referencia era un transmisor **ABB, que no está en el listado SCE-IN-501-0015**. Pasa a Rosemount (INS-02716, planilla PAMPA ENERGIA/5, 26-06-2026, USD 3.470,06; consulta C2: si alcanza una sonda o la provee Camuzzi, baja).
- Pos 2 carretel: el estimado usaba el caño Renard A53 **grado A** (26,95/m) que la auditoría ya había descartado: ahora 2 bridas + 0,3 m de caño cód. 1160 = 81,60. Extremos en la lista: RF (es bridado entre las bridas 5), no BW/BW.
- Pos 12: fuente con la fecha real de VAL-03526 (planilla Tecpetrol/9, 26-01-2026), no la de la lista Taval.
- Fila nueva 11b: 2 cuplas 3/4" NPT S3000 para montar las termovainas (no están en la tabla del plano; aclarado en la oferta).
- 15b: 4,7 m (0,3 m de la media tira van a las toberas del filtro).
- Marcas: en cada renglón y en Compras, las del listado de Camuzzi (rev. 1, 10-02-2026, copia en la carpeta del 003). Taval, Renard y Megatap quedan solo como referencias de precio.
- Siguen SIN PRECIO (a Compras, con motivo): 6b junta 6" #150, 11 termovainas, 16 cupla A-106.

**MO y servicios:**
- Soldaduras del puente contadas junta por junta del dibujo: 21 a tope (5 de 6", 16 de 4") + 5 cuplas = **99,25 pulg** (antes 98,625 de la regla × 1,5 por caño). Filtro: **70,75 pulg** (fila MOF), a 16 USD/pulg como la planilla TAVAL/40. Alternativa: Quesada JQ-020-2026, 12 USD/pulg.
- Skid: Quesada JQ-020-2026 (06-05-2026) 4,50 USD/kg × 200 kg (antes Ledesma 3 USD/kg de la PC0 de YPF con fecha supuesta).
- RX con la tarifa confirmada por Matías (30-10-2026): 88 placas (puente 68 + filtro 20), 2 visitas, ARS 3.020.000 a 1.541,43 = USD 1.959,22. LP aparte: 10 juntas × 30 (END-00209).
- Pintura: 14,80 m² (antes 6,21: faltaban el filtro y el skid), PIN-00494 (50 USD/m², PAMPA/7); la PIN-00569 era de la PC0 con fecha supuesta.
- PH del puente 6 h (ET: 1,5 × serie, 6 h); la del filtro va en ARMF (45 h del FM3, TAVAL/40). Prueba de fugas con aire seco: 8 h × 13 (estimado; antes en 0).
- Horas: ingeniería 29 h y calidad 49 h (20/40 del puente por criterio + 9/9 del filtro de TAVAL/40); montaje 65,1 h (antecedente TAVAL/43).

**Plazo:** lo fija la tapa de cierre rápido de marca del listado (Futura cotizó 90 días la FV16 en TAVAL/40): calculado 130 días, **ofrecido 150** (antes 105, con la tapa supuesta a 45 días).

**Antecedentes:** ninguno con costo por equipo comparable; no se escribió justificación. Comparación parcial del filtro con TAVAL/40 FM3 S150 (5.575 de costo total): materiales del FM-06 4.404,81 contra 1.720 del FM3 (diferencia: tapa de cierre rápido 2.480 contra tapa bridada; cuerpo 12" contra 6"), MO de soldadura 1.132 contra 694,72 (70,75 contra 43,42 pulg).

## Errores encontrados en la revisión del 30-10-2026
1. **`armar_json.py` no reproducía `cotizacion.json`:** las correcciones de las tres auditorías (5c B7/2H, 6b, 6c, 14/15 sin costura, 16 SIN PRECIO) estaban solo en el json; correr el script las deshacía (volvía el B7M a 2,60). Corregido: todo está en el script.
2. **Filtro FM-06 estimado desde un precio de venta del período con cepo** (CAMUZZI/23, 06-03-2025) y de otra serie (#300): el 44% del costo sin fuente válida. Corregido por componentes.
3. **Transmisor ABB fuera del listado de marcas** de Camuzzi (pos A). Corregido.
4. **Carretel (pos 2) con caño A53 grado A** ya descartado. Corregido.
5. **Pintura sin el filtro ni el skid** (6,21 m² en vez de 14,80). Corregido.
6. **Precios de la PC0 de YPF con fecha supuesta** (pintura PIN-00569 y skid 3 USD/kg) usados como antecedente. Reemplazados.
7. **Plazo de 105 días con la tapa supuesta a 45 días**, sin cotización. Corregido a 150 con la referencia de Futura.
8. **Termovainas sin la conexión al caño** (faltaban 2 cuplas 3/4"). Agregadas (11b).
9. **Manómetros de la ET §5.7 y PH, prueba de fugas y LP sin destino**: no había matriz de requisitos. Hecha; los manómetros van como consulta C1.
10. Error mío durante la revisión: el directorio temporal es compartido con los agentes del 001 y el 003; un script de requisitos del 001 con el mismo nombre escribió sus requisitos en esta carpeta. Se detectó al instante y se rehizo el archivo desde un script propio. Usar nombres únicos en el temporal.

**Frenos que quedan:** consultas C1–C4; lo estimado 16% (horas de ingeniería, calidad y montaje por criterio, espárragos, carretel, prueba de fugas); 20 precios vencidos (lista Renard 12-2025, lista Taval 09-2025, Megatap, Provemet, Quesada): pedir a Compras; datos entre corchetes de la oferta (número de PRES, teléfonos); antecedentes sin costo comparable. Falta la revisión independiente (P9).

## 30-10-2026 · Hallazgos de la auditoría independiente de esta revisión
Cada hallazgo se verificó contra el plano (imagen ampliada del dibujo) y los originales. Antes: unitario USD 31.122,70, total USD 31.726,82. Después (`armar_cotizacion.py`): **unitario USD 32.269,12, total USD 32.873,24**. Borrador, sin revisar.

Errores reales, corregidos (se suman a los de la revisión):
11. **Faltaba una junta de 6"**: entre el ramal de la te 7 y la brida de la válvula 3 hay un tramo de caño (dibujo de elevación), así que son 2 juntas y no 1. S01 pasa a 105,25 pulgadas (22 a tope). RX: 92 placas, 3 visitas = ARS 3.930.000 = USD 2.549,58.
12. **El filtro dibuja un manómetro de presión estática con su válvula**, además del diferencial, y la exclusión decía que no figuraban en el plano. Se agrega la fila 1j: manómetro Ø 100, 1/2" NPT, AISI 316 (INS-02698, planilla Sacde/15, 115) + manifold de 3 vías ABAC (TAVAL/40, 170). La exclusión y la consulta C1 quedan solo para manómetros adicionales en el puente.
13. **La válvula 3 (6") está dibujada con volante (caja reductora)**: la referencia Taval es a palanca. Queda la diferencia en el renglón, en los desvíos del informe y en Compras. No hay precio con reductor en la base, así que no se agregó un monto.
14. **PH del puente en 6 h**: era solo el tiempo de mantenimiento. Pasa a 18 h por armado, cegado de bridas, llenado, desarme y secado (TAVAL/40, «PH con armado y desarme» 1 día × 2 × 9 h).
15. **`sin_precio_motivo` mal usado** en 6b, 11 y 16: decía "pedida a Compras", que no es un motivo para ir en 0, y tapaba el freno de sin precio. Se sacó; ahora frenan. Solo la fila 1 lo conserva, porque su precio está en los componentes.
16. **Refuerzos tipo poncho del filtro** con el valor de 6"x3" de TAVAL/40 (150 c/u, que la propia planilla marcaba como estimado). Pasan a una fila 1k SIN PRECIO, para pedir a Cintolo.
17. En la lista para Compras faltaban las marcas de accesorios para soldar del listado (Cintolo/Curvo Sold, TDW) en las pos 8, 9, 10, 1c y 1k. Agregadas.
18. Faltaba en la matriz de requisitos la ET §5.8 sobre los manifolds (A-105 o superior, zincado, serie 3000): va a 1h y 1j. Se agregan como `pendiente_itt` la descarga de los documentos de Camuzzi y el plano tipo del filtro (largos, internos y refuerzos estimados). Se agrega la consulta C5: el dibujo muestra la pos 12 dos veces, la 16 una y la 11 una, contra 1, 2 y 2 en la tabla; se cotiza la tabla. La C2 ahora pregunta si el sensor A trae termovaina propia.

Hallazgo no aceptado, con su evidencia:
- **Tapa de cierre rápido 1d (USD 2.480, Megatap).** Se mantiene como referencia de precio. Es la misma medida y la misma serie (12" #150, ASME VIII). Según la guía (§ "Similares: misma serie y misma norma", Matías 29-10-2026), otra marca se anota como diferencia y no invalida la referencia. Las referencias de Futura que propone el auditor son de otra medida y otra serie (8" #300 USD 3.424; 16" #600 USD 8.432), así que no sirven como referencia. La Futura 8" #300 queda cargada como fuente descartada, porque muestra que una marca del listado puede cotizar más. La cotización de Megatap está vencida, ya frena por eso y está pedida a Compras.

Siguen abiertos: ARMF (45 h del FM3) y los internos del filtro, que salen de un FM3 con tapa bridada, hasta tener el plano tipo (pendiente_itt).
