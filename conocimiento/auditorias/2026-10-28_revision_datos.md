# Auditoría de cálculos y datos del cotizador ITT — 28-10-2026

Auditor: agente independiente (no armó la base). Repositorio en el commit `44bcd30` (durante la auditoría otra sesión subió `5bd3756`, con el caso CTRL-F01 y un cambio en `catalogo_materiales.py`; los catálogos se auditaron sobre la copia de `44bcd30`). **No se modificó ningún archivo del repo** y `git status` quedó limpio.
Scripts y salidas de la auditoría: `/tmp/claude-0/-home-user-cotizador-itt/82ad64dc-b6db-5ba7-866e-adf8ec6ac548/scratchpad/agentes/datos/` (`recalc.py`, `variantes.py`, `verif_muestra.py`, `mono.py`, `ant.js`, `inf.js`, `njs/web.js`).

## 1. Resumen

- **El caso de control da bien en los cinco caminos:** recálculo independiente con `Decimal`, Python (`calcular`), motor de la página (`motor.js`), planilla de Python y planilla de la página, las dos recalculadas con LibreOffice. Unitario **USD 7.620,59**, total **15.241,18** y costo 5.644,88. `verificar_todo.py` da "TODO OK". `probar_motor.js` y `probar_busqueda.js` dan OK.
- Hice 400 combinaciones al azar de N, factores, contingencia, ajuste, flete, precios y cantidades: Python, JS y el recálculo independiente dan igual al centavo. En 15 variantes recalculadas con LibreOffice, las dos planillas coinciden con el motor en 12. **Hay 3 casos borde en que no coinciden** (E1, E2 y E3).
- Índices y dólar: la serie es una sola (oficial BNA venta, promedio mensual), coincide con los datos diarios y IPC/dólar/CPI son coherentes entre sí. Los defectos son menores: el IPC interpolado se aparta hasta un 2,3% del INDEC mensual, el mayorista de enero de 2024 está viejo y los promedios incluyen fines de semana.
- Catálogos: verifiqué contra el original **44 materiales** (Renard 18/18, stock ×0,64 12/12 y planillas 14/14 en precio) y **22 servicios** (22/22). No encontré ningún precio mal leído por formato. Sí encontré **errores de la fuente que pasan sin alerta** (Renard: tee 1 1/2" NPT a USD 235,85; brida SW 16" a 11,49; brida SW 6" a 112,86), un control de atípicos demasiado laxo (solo avisa desde 50 veces la mediana), duplicados con precios hasta 6,4 veces distintos y servicios metidos en el catálogo de materiales.
- Tablas técnicas: caños 168/168 cumplen la fórmula B36.10 y válvulas 35/35 coinciden celda por celda con la Lista 30. Hay **una válvula con la serie mal asignada** (globo 14" #600 cargada como #300) y desarrollos mal copiados en `factores_soldadura.csv`.
- Documentos: el informe, la planilla, las ofertas y la página muestran los mismos números y todos sin IVA. Las ofertas no muestran costos ni factores. **Problemas:** (a) con flete incluido, la oferta muestra un subtotal y un total distintos sin ningún renglón de flete; (b) la lista para Compras de Python muestra fechas AAAA-MM-DD; (c) el formato de los números está mezclado: las ofertas y el P8 usan 7,620.59 y el informe y la página, 7.620,59.
- Antecedentes (P8): Python y la página dan lo mismo **solo si los ítems traen los datos del plano**. Sin ellos, la página elige otros 5 antecedentes y da avisos distintos. Además, 4 de los 5 antecedentes de la CAPEX "no son comparables" y el único aviso (−50%) es contra un precio que no es por puente.
- CAPEX: la pos. 20 (manómetro) usa el valor del stock del cepo **sin el ×0,64** que aplica el catálogo. Eso suma **USD 90,74 por puente** (181,48 en total) al precio de venta. Es un borrador y está avisado, pero va contra la regla del cepo.

## 2. Tabla de verificaciones

| # | Qué | Cómo | Resultado |
|---|---|---|---|
| 1.1 | CAPEX unitario 7.620,59 / total 15.241,18 / costo 5.644,88 | `recalc.py` (implementación propia con Decimal), `armar_cotizacion.calcular`, `motor.js` | OK (los tres iguales) |
| 1.2 | Planilla de Python (fórmulas) | `escribir_planilla` + LibreOffice headless + openpyxl `data_only` | OK: D27 = 7.620,59 y E28 = 15.241,18 |
| 1.3 | Planilla de la página (`Documentos.planilla`) | node + xlsx-js-style@1.2.0 + LibreOffice | OK: 7.620,59 / 15.241,18 |
| 1.4 | Informe HTML (su propio motor JS) | Playwright: `tPrecio`, `#tRes tfoot` | OK: 5.644,88 · 7.620,59 · 15.241,18; costo sin ajuste 5.482,11 |
| 1.5 | 400 variantes al azar (N 1–40, FM/FMO 1–1,6, CONT, AJ, TRANS, TC, precios, cantidades) | Python vs JS vs recálculo independiente | OK: 0 diferencias |
| 1.6 | N=5, FM 1,30, FMO 1,40, CONT 10% | 5 caminos | OK: 7.727,76 / 38.638,80 |
| 1.7 | Sin ajuste (AJ=0) | 5 caminos | OK: 7.400,85 |
| 1.8 | Con flete (TRANS=1; y TR_F 1,2 con N=3) | 5 caminos | OK: 17.694,97 y 25.806,32 (la planilla no redondea E28: 17.694,9731) |
| 1.9 | Material con fecha futura (2027-03) | 5 caminos | OK (los cinco usan el último índice) |
| 1.10 | Fecha muy vieja (2019, 2020), anterior al primer índice | 5 caminos | Coinciden, pero **ajuste subestimado sin aviso** (E4) |
| 1.11 | Fecha solo con año ("2025") | 5 caminos | **ERROR E3**: 8.064,50 / 8.056,77 / 8.063,39 |
| 1.12 | Fecha de referencia anterior a la de los ítems (2026-05) | 5 caminos | **ERROR E1**: motor 7.496,43 contra planillas 7.483,45 |
| 1.13 | Fecha de referencia anterior al primer índice (2023-06) | 5 caminos | **ERROR E2**: planillas en #N/A; motores, sin aviso |
| 1.14 | Fecha de referencia posterior al último índice (2027-02) | 5 caminos | Coinciden; usan oct-2026 sin aviso (M) |
| 2.1 | `dolar_bna` = promedio de `dolar_diario.csv` (oficial) = `dolar_mensual.oficial_promedio` | script | OK (34/34 meses) |
| 2.2 | `indice_local_usd` = IPC ÷ dólar (base oct-24 = 100) | script | OK (diferencias < 0,001) |
| 2.3 | No se mezclan series del dólar | `indices` usa solo el oficial; cepo = oficial ÷ blue del mismo mes | OK |
| 2.4 | IPC contra el INDEC mensual (ene-24 a oct-25) | variaciones mensuales publicadas | Ene–oct 2024 OK (1,7164 contra 1,7164). Nov-24 a oct-25 interpolado, **hasta −2,3% en abr-25** (M1) |
| 2.5 | CPI EE.UU. | interanual sep-25 (3,0%), sep-26 (3,7%) | OK en los anclajes; meses intermedios interpolados aunque el origen lista el dato mensual |
| 2.6 | Índices de la página = CSV | `datos.json` contra `indices_ajuste.csv` | OK |
| 2.7 | Calidad del diario | duplicados, huecos, relleno | Sin huecos. **Mayorista 1–10 ene-2024 = 366,45** (dato viejo de antes de la devaluación). Promedios con fines de semana repetidos (M) |
| 3.1 | 18 materiales Renard | código contra `renar_lista_2025-12.xlsx` | OK 18/18 (precio, unidad, fecha 26-12-2025) |
| 3.2 | 12 materiales del stock (cepo) | precio maestro × 0,64 contra `stock_valorizado_2024-11.xlsx` hoja General | OK 12/12 |
| 3.3 | 14 materiales de planillas, cotizaciones y cepo×blue | grep en `ofertas_texto` | Precio OK 14/14. Cepo × 0,8661 (oficial 1.088,38 ÷ blue 1.256,61, mar-25) OK. Unidad "m" de caños por metro OK. Hallazgos de clasificación en E9 |
| 3.4 | IVA | fuentes con "con IVA" contra el historial del catálogo | No entra ninguna fuente con IVA incluido. La detección es por renglón: Francovigh dice "MÁS IMPUESTOS" y quedó como "no dice" (sin efecto en el precio) |
| 3.5 | 22 servicios | grep en el original | OK 22/22 (Suan ARS 850.000 ÷ 1.284,03 = 661,98 ✓; Finder 3.900 + IVA ✓; END 18/29/590 ✓; ARSOL 10.874 ✓; seguro 106,66 ✓; RX 490 ✓; pintura propia 15,0241 ✓) |
| 3.6 | Atípicos por serie de diámetros (Renard) | `mono.py`: picos y pozos | **3 errores de la fuente sin alerta** (E6) |
| 3.7 | Atípicos por grupo (familia, tipo, Ø, serie, sch, unidad) | > 4 veces o < 1/4 de la mediana | 7 casos, 4 sin alerta (E6, E7) |
| 3.8 | Duplicados | descripción normalizada + unidad | 89 grupos (188 renglones); 23 con precios > 1,5 veces distintos (E7) |
| 3.9 | Página = CSV | `datos.json` contra los CSV | Materiales 3.298 = 3.298 y precios iguales. Servicios 553 contra 562: faltan solo los 9 de sueldos por centro (intencional) |
| 3.10 | Conteos documentados | `estado_y_pendientes.md` contra el CSV | Desactualizado: dice 3.319 / 1.005 / 132 y hay 3.298 / 1.003 / 131 (M) |
| 4.1 | Caños B36.10 | kg/m = 0,02466·e·(OD−e); m²/m; litros | OK 168/168 y 18 valores de referencia |
| 4.2 | Válvulas (Lista 30) | 35 al azar, celda por celda; las 383 con el código en la misma fila | OK 35/35 y 383/383. **Serie mal asignada en 1** (E8) |
| 4.3 | Factores de soldadura | factor = e/e STD; desarrollo = π·OD | Factor OK. **Desarrollo mal en 1/2" 160/XXS, 3" y 3 1/2"** (E10) |
| 5.1 | Oferta económica de la CAPEX | pdftotext + render | OK: 7,620.59 × 2 = 15,241.18, "sin IVA", fechas DD-MM-AAAA, sin costos ni factores |
| 5.2 | Oferta con flete incluido | copia de la CAPEX con TRANS=1 + `generar_oferta.py` | **ERROR E5**: subtotal 15,241.18 y total 17,694.97 sin renglón de flete |
| 5.3 | Fechas a la vista | regex en xlsx, md e informe | Informe y planilla OK. **Lista para Compras (Python): 25 fechas AAAA-MM-DD** (E11). Hoja Índices: textos con fechas ISO |
| 5.4 | Datos que no van al cliente | lectura de las ofertas | Sin costos, factores ni márgenes. La técnica nombra a un proveedor ("proveedor Morken") (M) |
| 6.1 | P8 Python contra página, CAPEX desde el repo | `comparar_antecedentes.py` contra `Antecedentes.comparar` | **ERROR E12**: sin `plano` en los ítems, la página da otros 5 y otros avisos |
| 6.2 | P8 con la semilla de la página (con plano) | ídem | OK: los mismos 5 y el mismo aviso |

## 3. Errores encontrados (con evidencia)

Severidad: **A** = puede llegar al cliente con un número o un dato equivocado · **M** = da un número distinto en algún camino o rompe una regla · **B** = calidad o prolijidad.

**E1 (M). Ítem con fecha posterior a la fecha de referencia: el motor y las planillas no coinciden.**
`armar_cotizacion.factor` y `motor.js factorAjuste` hacen `min(fecha, fref)`, y la fórmula de la columna N de las planillas (Python y página) es `VLOOKUP(MAX(K, Índices!A2))`, sin el mínimo con H7. Con `fecha_referencia = 2026-05-10`, la CAPEX da **7.496,43 en el motor y 7.483,45 en las dos planillas (−12,98 por puente)**. En Python, `armar_cotizacion` lo frena porque compara los dos. **En la página no hay ese control:** la planilla descargada no coincide con el número de la pantalla. Corrección: `VLOOKUP(MIN(MAX(K,Índices!$A$2),Cotización!$H$7),…)` en las dos planillas.

**E2 (M). Fecha de referencia anterior al primer índice (ene-2024): las planillas dan #N/A y los motores no avisan.** Con 2023-06, el motor da 7.400,85 (factor 1 de hecho) y las planillas, #N/A. Corrección: validar `fecha_referencia ≥ 2024-01` en la página y en Python.

**E3 (B/M). Fecha solo con año ("2025"): tres resultados distintos.** Python y JS comparan strings ("2025" < "2025-01"), así que toman dic-2024: 8.064,50. La planilla de Python usa 01-07-2025: 8.056,77. La de la página usa 01-01-2025: 8.063,39. `verificar_computo.py` y el campo de fecha de la página lo impiden, pero el chat (`asistente.js`) o un JSON cargado a mano podrían meterlo. Corrección: normalizar o rechazar en `calcular` y en `motor.js`.

**E4 (M). Fechas anteriores a ene-2024: el ajuste se recorta sin avisar.** `max(…, idx[0])` toma como base ene-2024. Un precio de 2019 ajustado por CPI sube solo 8,9% (106,871/98,121), cuando 2019→2024 faltan más de 20%. En MO, el índice local arranca en 69,64. El aviso de antigüedad no dice que el ajuste está incompleto. Corrección: un aviso específico, o extender los índices hacia atrás.

**E5 (A). Oferta económica con flete incluido: el total no cierra a la vista del cliente.** Lo reproduje con una copia de la CAPEX con TRANS=1 y `generar_oferta.py`: la tabla dice "USD SUBTOTAL 15,241.18" y "TOTAL (SIN IVA) 17,694.97", con **2.453,79 sin renglón que lo explique**. `Documentos.cuerpoOferta` y `ofertaHtml` de la página hacen lo mismo (subtotal = unitario × N y total = `calc.total`). Corrección: un renglón "Flete y embalaje" cuando TRANS=1 (`generar_oferta.py` l. 270-276; `documentos.js`, `cuerpoOferta` y `ofertaHtml`).

**E6 (A). Errores de la lista Renard que entran como "lista" sin alerta** (la fuente coincide con el CSV, así que el error viene del proveedor; el catálogo no lo detecta):
| Código | Descripción | Precio | Vecinos de la misma serie |
|---|---|---|---|
| AFO-00907 (Renard 6047) | Tee 1 1/2" NPT S3000 A105 | **235,85** | 1 1/4" = 26,20 · 2" = 49,24 (6,45 veces la mediana del grupo) |
| BRI-01162 (Renard 9934) | Brida SW 16" S150 | **11,49** | 6" = 112,86 (además, la SW 16" no existe en B16.5) |
| BRI-01184 (Renard 9929) | Brida SW 6" Sch40 S150 | **112,86** | 5" = 32,85 · 6" Sch80 = 118,83 (posible) |
| AFO-00963 (Renard 13005) | Cupla para soldar 1 1/2" | **1,79** | 1 1/4" = 4,98 · 2" = 12,12 |
Impacto: una tee 1 1/2" NPT cotizada con el catálogo sale **~USD 200 más cara por unidad** (×1,35 = ~270 de venta). La causa es el umbral de la alerta: `catalogo_materiales.py` (l. 680-686) solo avisa desde **50 veces** la mediana.
Del mismo tipo: BRI-01354 "Brida SW 24" #150" a **USD 6,83** (en el original, la misma fila está dos veces, a 6,83 y a 868; se elige 6,83 porque tienen la misma fecha) y JUN-02771 (junta espiralada 2" #600) a **2,30** con historial 2–11. Estas dos tienen la alerta de "historial con precios muy distintos", pero el precio que queda es el más bajo.

**E7 (M). Duplicados sin clave que esconden precios muy distintos.** Hay 89 grupos con la misma descripción y la misma unidad, y 23 con precios más de 1,5 veces distintos. Ejemplos: ABW-00435 codo 90 RC 10" Sch80 **2.468,27** (Cintolo, 31-07-2025) contra ABW-00436 el mismo codo **385,35** (Simat, 11-03-2026), 6,4 veces; OTR-01889 cartucho FM-10 #600 **1.659,49** contra OTR-01890 **335**; ABW-00567 contra 00568 (tee red. 2"×1" sch80) **131,2** contra 30,4. Como no tienen `clave`, no se aplica "el último precio manda" y el buscador puede devolver el viejo o el caro.

**E8 (B). `valvulas_peso.csv`: globo 14" #600 cargada como #300.** En la Lista 30, hoja Globo, filas 94–97, el bloque #600 (dice "600" en A96) repite los códigos del bloque #300 (`G003503…`). Quedaron dos renglones "GLOBO 14" 300 RF" (1.120 kg en E87 y 1.400 kg en E94), con el mismo código, y falta el de 14" #600. `pesos_valvulas.py` toma la serie del código y no del rótulo de la columna. Impacto: solo en los kg (flete y controles). Del mismo tipo: retención 20" #300, trim 1 = 1.220 kg y trim 12 = 1.120 kg (AC95/AC99; la fuente es inconsistente).

**E9 (B). Clasificación del catálogo de materiales.**
- Servicios en materiales: OTR-03013…03016 "Serv de ROLADO" (USD 3,7/kg; contra la lección 33), con el peso pegado en la descripción ("1531.1999999999998").
- CAN-02667 WELDOLET quedó en la familia "Caños".
- AFO-02375 "Tapón lubricado inv. 2" 900" es una **válvula macho** (USD 920) clasificada como accesorio forjado; por eso la alerta "109 veces la mediana" es un falso positivo.
- Texto de la alerta cortado en 1.003 renglones: "(recio maestro…" y "(levado a dólar blue…". En `catalogo_materiales.py` l. 673, `[11:]` tendría que ser `[10:]`.

**E10 (B). `factores_soldadura.csv`: desarrollo (π·OD) mal copiado** en 1/2" Sch160 y XXS (53,7 en vez de 66,9), en 3" (239,4 en vez de 279,3) y en 3 1/2" (279,3 en vez de 319,2). También `factor_original_itt` de 1/2" 160/XXS (2,069 y 3,234 contra 1,726 y 2,697). Hoy no lo usa ningún cálculo (solo `construir_base.py`), pero sería un error si se usa para placas de RX o consumibles.

**E11 (M, regla de fechas). Lista para Compras de Python con fechas AAAA-MM-DD.** `COT26-1003-001_pedido_materiales_compras.xlsx`, hoja Materiales, columna O "Fecha del precio" (O18 = "2025-12-26", 25 celdas). Viene de `lista_compras.py` l. 80/85, que copia `base["fecha"]` sin `a_vista`. También la hoja Índices de la planilla ("último 2024-01-31") y `computo.csv`/`precotizacion.md`, que son internos.

**E12 (M). P8: Python y la página no comparan contra lo mismo.**
- Python toma Ø y serie del renglón de la cotización en `indice_proyectos.csv` (`yo`). Si la cotización todavía no está indexada, quedan en `None`. Además toma la serie con `split()[-1]`.
- La página los toma de `item.plano`. El `cotizacion.json` del repo no tiene `plano`; lo agrega `web/semilla.py`.
- Resultado con el JSON del repo: la página da PAMPA/5, TAVAL/70, **APSA/9 (5.220, aviso +46%)**, PAMPA/7 y TAVAL/55, y Python da TAVAL/55, APSA/12, PAMPA/5, TAVAL/70 y PAMPA/7. Con la semilla dan lo mismo.
- Los dos usan "hoy" para el factor de edad, así que el orden cambia con el paso de los días.
- Además, 4 de los 5 quedan como "otra escala". El único aviso (−50% contra TAVAL/55, 15.096) usa un `precio_unitario_principal` que no es el de un puente comparable: la bitácora habla de ~6.200 (2024) y ~6.700 (2026). **El P8 automático no está comparando contra los antecedentes correctos.**

**E13 (M). CAPEX pos. 20 (manómetro): no se aplicó el ajuste del cepo.** El `cotizacion.json` usa USD 83,40 (precio maestro del stock, 01-11-2024). El catálogo, por la regla del 28-10-2026, lo lleva a 53,376 (INS-01576, ×0,64). Diferencia: 2 × (83,40 − 53,376) × 1,06608 = **64,02 de costo por puente → +90,74 de precio por puente (+181,48 en el total)**. `verificar_computo` lo avisa como "cepo sin TC". La alternativa "stock 86,01" tiene el mismo problema.

**E14 (B). Informe HTML: guarda los parámetros en el navegador con una clave que solo depende de los ítems.** `KEY = codigo:sha1(items)`. Si se cambian FM, FMO, N o CONT en `cotizacion.json` sin tocar los ítems, `load()` mezcla `{...ORIG_PARAMS, ...guardado}` y **el informe muestra los parámetros viejos** en el navegador de quien ya lo abrió. Corrección: incluir los parámetros en la huella.

**E15 (B). Página: un renglón del catálogo sin fecha entra con la fecha de hoy.** `busqueda.js` l. 99 y 111: `fecha: r.fe || hoy()`. El precio sin fecha (p. ej. CAN-01383) queda como de hoy, sin ajuste y sin el aviso "sin fecha". Además, `avisos()` compara las fechas con hoy y no con `fecha_referencia`, así que no detecta el caso E1.

## 4. Mejoras priorizadas

1. **(A) Corregir la oferta con flete** (E5) en `generar_oferta.py` y `documentos.js`: un renglón "Flete y embalaje" y que subtotal + flete = total.
2. **(A) Control de atípicos más estricto en el catálogo** (E6/E7): alerta desde 3–4 veces la mediana de (familia, tipo, Ø, serie/sch, unidad); control de monotonía por diámetro dentro de cada serie de la lista de un proveedor (`mono.py` sirve de modelo); ante dos precios con la misma fecha y la misma fuente, elegir la mediana o dejar el renglón sin precio y con alerta. Confirmar con Compras los 4 de Renard y los 6 casos de E6/E7.
3. **(M) Un solo criterio de fecha en motor y planillas** (E1–E4): `MIN(MAX(K, primer mes), H7)` en las dos planillas; rechazar fechas que no sean AAAA-MM-DD en `calcular`/`motor.js`; aviso cuando la fecha del precio es anterior a ene-2024 o la de referencia queda fuera de la tabla. Sumar a `probar_motor.js` las variantes de `variantes.py`.
4. **(M) En la página, comparar el motor con la planilla** antes de descargar, como hace `armar_cotizacion.py` con LibreOffice (al menos con una evaluación JS de las mismas fórmulas).
5. **(M) P8** (E12): que Python y la página saquen Ø y serie de la misma fuente (`lista_materiales_plano.csv` / `item.plano`); fijar la fecha de cálculo en `fecha_referencia`, no en hoy; revisar `precio_unitario_principal` del índice para que sea por equipo; agregar a la prueba de la página una comparación con Python.
6. **(M) CAPEX pos. 20** (E13): aplicar ×0,64 o reemplazar por una cotización. Hacer que `verificar_computo` trate como **error** (y no como aviso) un precio del cepo sin TC explícito ni el factor aplicado.
7. **(M) Fechas a la vista** (E11): `a_vista` en `lista_compras.py`; revisar los textos de la hoja Índices.
8. **(M) Formato de números único:** las ofertas y el P8 de Python usan `f"{v:,.2f}"` (7,620.59) y el informe y la página, es-AR (7.620,59). Para el cliente argentino, conviene 7.620,59 en todo (la regla de lectura del propio repo trata "4,500" como ambiguo).
9. **(B) Índices** (M1): cargar el IPC mensual publicado de nov-24 a oct-25 (hoy interpolado al 2,30% fijo; con abr-25 un 2,3% más bajo, el ajuste de MO de mar–may-25 queda hasta 2,4% alto), y los meses de 2025–2026 a medida que salgan; CPI mensual de feb–jul 2024 (el dato está en el texto de origen y no en la serie); mayorista de ene-2024 (366,45 → dato real); promedio solo sobre días hábiles; corregir el texto "oct-2026 igual a sep-2026 (1,9%)" (la serie usa 2,38% en sep).
10. **(B) Tablas técnicas** (E8, E10): en `pesos_valvulas.py`, tomar la serie del rótulo del bloque y avisar si no coincide con el código; corregir los desarrollos.
11. **(B) Limpieza del catálogo** (E9): sacar los servicios de rolado, reclasificar el weldolet y el tapón lubricado, arreglar el `[11:]`, detectar el IVA a nivel de documento ("MÁS IMPUESTOS", "No incluye IVA") y no solo en el renglón.
12. **(B) Informe** (E14): huella con parámetros. **Página** (E15): un ítem sin fecha queda sin fecha y con aviso, no con la fecha de hoy.
13. **(B) Documentación:** actualizar los conteos de `estado_y_pendientes.md` (3.298 / 1.003 / 131). En la oferta técnica, evaluar si conviene nombrar proveedores ("Morken").

## 5. Cuentas reproducibles de la CAPEX (por puente, fecha de referencia oct-2026)

Factor = índice de oct-26 / índice del mes del precio. CPI oct-26 = 106,871; local oct-26 = 113,342.

- Materiales ajustados = 4.377,0764. Contingencia 5% = 218,8538. MO = 711,2183 (S01 400 × 1,04624 + S02 13,09 × 19,73 × 1,13342). Servicios = 337,7363.
- Costo = 4.377,0764 + 218,8538 + 711,2183 + 337,7363 = **5.644,8848**.
- Precio = (4.377,0764 + 218,8538) × 1,35 + (711,2183 + 337,7363) × 1,35 = 6.204,5058 + 1.416,0887 = **7.620,59** (redondeado). Total = 7.620,59 × 2 = **15.241,18** (sin flete, EXW).
- Peso del costo por tipo de fuente: estimado 62,9% · cotización 15,1% · antecedente 14,5% · lista 7,5%. Coincide con el "63% estimado" de la bitácora.
