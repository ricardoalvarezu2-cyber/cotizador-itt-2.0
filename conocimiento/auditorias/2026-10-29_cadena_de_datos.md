# Auditoría de la cadena de datos — 29-10-2026

Qué se revisó: por dónde pasa cada dato, desde que llega el pedido (plano, pliego, listas de proveedores) hasta el cómputo, la planilla, el informe, las ofertas y la página. Se siguieron dos casos de punta a punta: la CAPEX (`COT26-1003-001`) y el skid YPF 713 (`COT26-0330-001`). Las pruebas se hicieron sobre una copia del repositorio en `/tmp/aud/repo`. No se tocó código ni datos.

**Control de la CAPEX:** hoy da **USD 7.366,12 por puente** (Python = planilla = `verificar_todo.py`). El valor 7.620,59 que figura en el pedido de esta auditoría, en `web/LEEME.md:10`, en `web/src/motor.js:2` y en `estado_y_pendientes.md` (filas de la página y "Sumar a otra persona") quedó viejo. Cambió el 28-10-2026 con la regla P4 ter, que sacó 3 valores supuestos (commit 4198546).

---

## 1. Mapa de la cadena

```
ENTRADA (lo lee la IA, no hay herramienta)
  pedido / pliego / plano (PDF, DWG)  ──IA──►  pedido/lista_materiales_plano.csv   [clave: pos]
                                      ──IA──►  pedido/transcripcion.json (literal; opcional)
  listas y cotizaciones de proveedores ─IA─►  conocimiento/precios/listas_nuevas.csv · servicios_extraidos.csv
                                              planillas_costo_items_parte*.csv (etapa 2; YPF: pc0_a_planillas.py)
  página (pedidos_web) ── Artifact read ──►  fuentes_originales/pedidos_web/<id>/  (Excel/Word convertidos a .md)

BASE (determinística; la arma actualizar_base.py)
  fuentes_originales/ofertas_texto + listas + cotizaciones/COT*/cotizacion.json + cotizaciones_web/*/ (incorporables)
     └─ catalogo_materiales.py ─► catalogo_materiales(.csv/.xlsx/_historial) + catalogo_codigos.csv (registro clave→código)
     └─ catalogo_servicios.py  ─► catalogo_servicios(.csv/.xlsx/_historial) + catalogo_servicios_codigos.csv
     └─ indices_inflacion.py / dolar_mensual.py ─► costos/indices_ajuste.csv (dolar_bna = oficial_promedio de dolar_mensual.csv; verificado: 0 diferencias)
     └─ indice_proyectos.py ─► comercial/indice_proyectos.csv (fichas 2025-2026 + cotizaciones del cotizador y de la página)
  [claves: código de catálogo FAM-NNNNN, que sale de una "clave" = familia|atributos|unidad; id de proyecto]

COTIZACIÓN (carpeta cotizaciones/<código>/)
  lista_materiales_plano.csv + catálogos + tecnico/*.csv
     └─ precotizar.py ─► cotizacion_auto.json + precotizacion.md     [clave: pos; el código de catálogo queda solo como TEXTO en fuentes[].proveedor]
  cotizacion_auto.json ──COPIA MANUAL (IA)──► cotizacion.json (única fuente)   [YPF: lo escribe armar_json.py de la carpeta]
  oferta.json (textos, plazo, desvíos) ──MANUAL──
  cotizacion.json ─ armar_cotizacion.py ─►
     computo.csv ─► verificar_computo.py (compara con lista_materiales_plano.csv por pos + cantidad)
     <código>.xlsx (fórmulas; índices congelados o indices_ajuste.csv) ─ soffice ─► recálculo == calcular() en Python
     compras/*.xlsx (lista_compras.py: transcripcion.json o lista del plano + compras{})
     informe.html (editable, guarda en localStorage)
     controles_tablas.md · plazo_calculado.md · ficha_rubros.json/.md · comparacion_antecedentes.md
     oferta/*.docx/.pdf (generar_oferta.py: precio de la planilla; plazo y desvíos de oferta.json; tabla de materiales = lista del plano)
     indice_proyectos.csv (efecto global: cada armado reindexa)

PÁGINA (Artifact + base db)
  construir_datos.py ─► web/datos.json (catálogos, índices, tarifas, tablas, plantillas) ─ armar_pagina.py ─► cotizador.html
  semilla.py <carpeta> [id] ─► set cotizaciones/<id> + resumenes/<id> (agrega item.plano, fam/at, kg_compras, ficha)
  página: motor.js (= calcular), ficha.js (= ficha_rubros.py), rubros.js, busqueda.js, documentos.js (planilla/ofertas propias)
  base db ─ ArtifactData list ─► respaldo_base.py ─► cotizaciones_web/<id>/cotizacion.json ─► (si es incorporable) vuelve a la BASE
  indices_para_pagina.py ─► config/indices (pisa a datos.json si es más nuevo)
```

**Claves que unen las tablas**
| Vínculo | Clave | Control automático |
|---|---|---|
| plano ↔ cómputo ↔ compras ↔ oferta técnica | `pos` (string) | `verificar_computo.py`: solo posición y cantidad |
| ítem ↔ planilla ↔ informe (export/import CSV) | `id` (M01, S01) | sí (planilla = Python) |
| ítem ↔ catálogo | **ninguna estructurada**: el código va dentro del texto `proveedor` ("Renard · cód. 5979", "… · PIN-00569") | no |
| catálogo ↔ historial ↔ registro de códigos | `clave` → `codigo` | registro persistente (`catalogo_codigos.csv`) |
| repo ↔ página | `codigo` (COT26-…) y el id del documento (`capex-oq8209`; la convención dice `c26-1003-001`) | no |
| cotización ↔ antecedente | `id` de proyecto / carpeta | no se excluye la misma licitación |

---

## 2. Hallazgos por gravedad

### CRÍTICO

**C1. Los precios de la planilla PC0 de YPF entran al catálogo con una fecha supuesta y quedan como último precio de 45 materiales.**
- Dónde: `cotizaciones/COT26-0330-001_YPF_LIC69343_SKID713/pc0_a_planillas.py:19` (`FECHA = "2026-10-10"`, la recepción del pedido) → `conocimiento/precios/planillas_costo_items_parte4.csv` (79 renglones) → `catalogo_materiales.py`. En `armar_json.py:7` pasa lo mismo (`FPC0 = "2026-10-10"`).
- Qué pasa: la planilla PC0 no tiene fecha por renglón ni documento del proveedor. En la cotización YPF esos precios están bien marcados como `est`, pero al catálogo entran como "planilla interna" con fecha 10-10-2026, la más nueva de todas. Verificado: **45 materiales** del catálogo tienen hoy su precio vigente sacado de la PC0 (todos con fecha 2026-10-10, sin alerta). Por ejemplo ABW-00358, tee de reducción 16" (USD 2.802,34, "CINTOLO"), y AFO-02373, tapón 3/4" (USD 2,30, "sin proveedor en planilla").
- Impacto: va contra la regla "nunca una fecha por defecto" de `numeros.py`. El próximo `precotizar.py` o `buscar_material.py` va a proponer esos valores como el precio más reciente y la cotización siguiente los toma como `ant`/igual. Un estimado se convierte en precio de base sin que nadie lo vea.
- Corrección: cargar la PC0 con `fecha_planilla` vacía o con la fecha real del archivo, y con `tipo` estimado (o marcar `confiable=False`) para que el catálogo la deje en el historial y no como último precio. Agregar una alerta en `catalogo_materiales.py` cuando la nota diga "sin fecha por renglón". Volver a armar el catálogo.

**C2. El plazo ofrecido es un número cargado a mano, y el control de plazo avisa pero no frena. En YPF 713 y 708 la oferta dice 120 días y el cálculo da 180.**
- Dónde: `oferta.json → item.plazo_dias` (lo usa `generar_oferta.py:277` y `:294`) y `cotizacion.json → plazo.dias`, dos campos iguales cargados a mano. `plazo.py` solo escribe `plazo_calculado.md` ("Propone y controla; no cambia el plazo ofrecido").
- Qué pasa (verificado en los `plazo_calculado.md`): YPF 713 y 708 ofrecen **120 d** y el cálculo da **180 d** sin superponer (207–216 con margen; el histórico de la familia SK da 162 d). Camuzzi 001 ofrece 120 d y el cálculo da 125. La bitácora de YPF no justifica la diferencia. `armar_cotizacion.py` termina igual con "Listo".
- Impacto: la oferta le promete al cliente un plazo que el propio cotizador calcula como imposible (multas, incumplimiento). Es un error que llega al cliente sin ningún bloqueo.
- Corrección: que `generar_oferta.py` lea el plazo de `cotizacion.json` (un solo campo) y que `armar_cotizacion.py` dé ERROR si el plazo ofrecido es menor que el calculado sin superponer, salvo que haya una `plazo.justificacion` escrita.

### ALTO

**A1. `verificar_todo.py` y los tests reescriben archivos versionados del catálogo y de la CAPEX, sin escritura atómica. Si dos sesiones lo corren en paralelo en el mismo repositorio, se rompen los datos.**
- Dónde: `herramientas/verificar_todo.py:48-57` (corre `test_catalogo*.py`, `catalogo_materiales.py` y `catalogo_servicios.py`, que escriben `conocimiento/precios/*.csv` y `*_codigos.csv`); `test_precotizar.py` reescribe `cotizaciones/COT26-1003-001…/cotizacion_auto.json` y `precotizacion.md`; `catalogo_materiales.py:786-793` y `catalogo_servicios.py:227-235` reescriben el registro de códigos con `open(…, "w")`.
- Evidencia: una corrida en el repo real, con otras auditorías corriendo al mismo tiempo, dio `UnicodeDecodeError` al leer `catalogo_servicios_historial.csv` (un archivo leído a medio escribir). También dio "catalogo_materiales.py / catalogo_servicios.py no es determinístico", dejó 16 archivos modificados y la precotización de la CAPEX tomó **otro servicio de pintura** (PIN-00479, global de un tanque de Sacde, en lugar de PIN-00569, USD/m² de piping) y otro de PH (END-00083 en lugar de END-00215). En la copia aislada, las dos corridas dan idéntico y los tests pasan. Se restauraron los archivos del repo real.
- Impacto: un catálogo o un registro de códigos corrompido puede subirse a `main` (la regla dice commit después de verificar). Los códigos cambian de dueño y la precotización elige servicios equivocados sin avisar.
- Corrección: escribir a un archivo temporal y renombrar (`os.replace`); poner un candado (`.lock`) en `actualizar_base.py`/`verificar_todo.py`; que los tests escriban en un directorio temporal y no en el repo; y que `verificar_todo.py` restaure también los CSV derivados que no cambiaron de datos.

**A2. Entre el ítem de la cotización y el catálogo no hay una clave estructurada. El precio se copia a mano y se desvincula.**
- Dónde: los ítems de `cotizacion.json` solo tienen `id, pos, grupo, descripcion, especificacion, cantidad, unidad, fuentes[]` (verificado en CAPEX, YPF y la plantilla). El código de catálogo queda escrito dentro de `fuentes[].proveedor`. `catalogo_materiales.py:744` detecta "precio que salió del catálogo" con una regex sobre ese texto (`[A-Z]{3}-\d{5}`).
- Evidencia: CAPEX pos 20 (manómetro) usa USD 83,40 (stock nov-2024), mientras que el catálogo ya lo lleva a 53,376 (INS-01576, ajuste del cepo). Ningún control lo detecta (ya estaba como E13 en la auditoría del 28-10 y sigue igual). Si al pasar de `cotizacion_auto.json` a `cotizacion.json` se reescribe el texto del proveedor sin el código, ese precio vuelve a entrar al catálogo como si fuera una cotización nueva (duplicado).
- Impacto: correcciones del catálogo (cepo, IVA, errores de lista) que no llegan a las cotizaciones abiertas, y precios que se realimentan.
- Corrección: agregar `fuentes[].codigo` (código de catálogo) y `fuentes[].moneda`/`iva_origen`; que `precotizar.py` lo complete y `verificar_computo.py` avise si el precio difiere del vigente en el catálogo para ese código.

**A3. Las cotizaciones en borrador alimentan el catálogo y el índice de antecedentes. Con la misma licitación, P8 se compara contra sí misma.**
- Dónde: `herramientas/cotizaciones_base.py:21-24` toma **todas** las `cotizaciones/COT*/cotizacion.json`, sin mirar el estado (a las de la página sí les exige `incorporable`, l. 27). `armar_cotizacion.py` (llama a `indice_proyectos.main()`) reindexa en cada armado.
- Evidencia: las 6 cotizaciones del repo están en `borrador` y 2 precios vigentes del catálogo vienen de ellas (AFO-01002 unión Adita de la CAPEX, con cotización vencida según la revisión; INS-04928 visor de Camuzzi). En YPF 713, el antecedente nº 1 de `comparacion_antecedentes.md` es **"YPF/28 – Lic 69343"**, que es la misma licitación (la planilla PC0 de la que salieron los precios). Da −7%, "sin aviso": el control P8 queda en verde de manera circular.
- Impacto: precios sin revisar pasan a ser referencia, y el contraste con antecedentes da confianza falsa.
- Corrección: aplicar `incorporable()` también a las del repo (revisado/aprobado/enviado o `base`), y que `comparar_antecedentes.py`/`buscar_antecedentes.py` excluyan el antecedente con la misma carpeta o el mismo número de licitación.

**A4. Repo y página tienen dos versiones distintas de la misma cotización, y `semilla.py` pisa la de la página entera.**
- Dónde: `web/semilla.py:20` (id por defecto `capex-oq8209`; `web/LEEME.md:55` dice `c26-1003-001`), `:63-66` (`set` del documento completo armado desde el repo: se pierden `rubros`, `transporte`, `aprobacion`, `base`, `indices_congelados` puestos en la página, y `firmante_id` vuelve a `matias-russo`). `cotizaciones_base.py:6` ("si el mismo código está en el repositorio, vale la del repositorio").
- Evidencia: el respaldo `cotizaciones_web/capex-oq8209/cotizacion.json` (28-10 02:31) todavía tiene los 3 valores sin referencia (M14C = 35, S03 = 15, S06 = 100) que P4 ter sacó en el repo: con `motor.js` da **7.620,03** contra **7.366,12** del repo. Lo que se corrija o apruebe en la página nunca entra a la base mientras exista la carpeta del repo, y lo que se resiembre desde el repo borra el trabajo hecho en la página. `if_version` solo evita escrituras cruzadas: no combina.
- Impacto: dos precios para la misma oferta, según dónde se mire. Pérdida silenciosa de cambios. Ya estaba como M1/A3 en la auditoría de arquitectura del 28-10 y sigue abierto.
- Corrección: un dueño por cotización (`origen: repo|pagina`); `semilla.py` con `update`/merge que conserve los campos propios de la página; ids según la convención; al respaldar, comparar con el repo y avisar si hay diferencia.

**A5. Las cantidades de la lista del plano no se leen con `numeros.py`: "1.200" se lee como 1,2.**
- Dónde: `herramientas/verificar_computo.py:29-33` (`num()` propio), `precotizar.py:257` (`float(r["cantidad"])`, y en otros 40 lugares), `generar_oferta.py:308` (copia el texto tal cual).
- Evidencia: `verificar_computo.num("1.200") = 1.2` y `numeros.leer_numero("1.200") = 1200`. `float("1,5")` corta `precotizar.py` con un error, mientras que `verificar_computo` lo lee 1,5. La guía (`guia_cotizacion.md:38`) dice "se copia tal cual, sin interpretar" y no fija el formato numérico de la lista.
- Impacto: un plano argentino con "1.200 m" o "4.500 kg" copiado tal cual queda 1.000 veces más chico en la precotización. Como `cotizacion.json` se arma desde `cotizacion_auto.json`, el cómputo y el control coinciden y el error no aparece.
- Corrección: leer `cantidad` con `numeros.leer_numero` en todas las herramientas (y frenar si viene marcado como ambiguo); fijar en la plantilla que la lista use punto decimal y no lleve separador de miles.

### MEDIO

**M1. `verificar_computo.py` controla solo posición y cantidad, no la especificación.** `computo.csv` no tiene Ø, serie, material ni extremos (`armar_cotizacion.py:114`), y `cotizacion.json` los lleva como texto libre en `especificacion`. El P2 ("se copian del plano") no tiene control automático. Tampoco compara la unidad cuando el plano dice "m" y el cómputo "un" (`verificar_computo.py:53-61` solo cubre plano "un"). Corrección: que `semilla.py`/`precotizar.py` guarden `plano{}` en cada ítem también en el repo, y que `verificar_computo.py` compare campo por campo, con desvío declarado o error.

**M2. Los desvíos de la oferta no están atados a los ítems "similar".** `oferta.json → aclaraciones_y_desvios` se escribe a mano y nada controla que cada ítem con `coincide: similar` tenga su desvío. En la CAPEX coinciden (revisado: los 25 similares están cubiertos o se ofrecen según el plano). Pero la tabla "MATERIALES CONSIDERADOS" de la oferta técnica (`generar_oferta.py:305-310`) copia la lista del **plano** y no lo que se ofrece (p. ej. pos 16 dice 80×40 y se cotiza XS×XS), en contra de "la oferta no afirma 'según pedido'". Corrección: generar la tabla desde `cotizacion.json` (especificación ofrecida) y avisar por cada `similar` sin `pos` mencionada en los desvíos.

**M3. Tipo de cambio del flete cargado a mano y con una regla distinta.** `parametros.TC` es manual: CAPEX 1.450, YPF 1.550, Camuzzi 1.541,43, y el promedio BNA de oct-2026 es 1.541,43 (`dolar_mensual.csv`). La planilla lo rotula "cargar BNA **del día**" (`armar_cotizacion.py:147`; también `documentos.js:75`), en contra de la regla del promedio mensual. Hoy afecta a Camuzzi (TRANS = 1). En la CAPEX está apagado, pero con TRANS = 1 el flete saldría 6% más caro. Corrección: tomar TC de `dolar_mensual.csv` por mes (`fecha_referencia` o la fecha del documento del flete) y corregir el rótulo.

**M4. `armar_cotizacion.py` escribe antes de verificar.** `armar_cotizacion.py:370-388`: escribe el cómputo, la planilla, el informe y Compras, y recién después corre `verificar_computo` y sale con error. Quedan entregables nuevos junto a ofertas viejas (ya estaba como M5 el 28-10; sigue abierto). Corrección: generar en un directorio temporal y mover cuando todo pasa.

**M5. La página convierte mal el Ø en dos cálculos: 1/2" da 1 y 3/4" da 3.** `web/src/app.js:200` (calculadora de m² de pintura, botón `pin-calc`) y `web/src/rubros.js:67` (`fichaBasica`, la ficha aproximada) hacen `parseFloat(…replace(" 1/2", ".5"))`. Verificado con node: `1/2"` → 1, `3/4"` → 3. Un niple de 3/4" se calcula con m² y kg de caño de 3". `ficha.js` y Python lo hacen bien. Corrección: usar el mismo `pulg`/`frac` de `ficha.js`.

**M6. El informe HTML es editable y guarda en el navegador con una clave que depende solo de los ítems.** `armar_cotizacion.py:309,352` (`KEY = codigo:sha1(items)`). Si cambian los factores en `cotizacion.json`, el informe abierto muestra los valores viejos (E14/M6 del 28-10, siguen abiertos). Corrección: que la huella incluya `parametros` y poner una banda "modificado localmente: no válido para oferta".

**M7. La página pone la fecha de hoy a un precio del catálogo sin fecha.** `web/src/busqueda.js:102,117` (`fecha: r.fe || hoy()`): no se ajusta y no avisa (E15 del 28-10, sigue abierto). Corrección: dejar la fecha vacía y que `verificar`/avisos lo marquen.

**M8. El script que escribe `cotizacion.json` en YPF depende de una carpeta temporal y pisa la "única fuente".** `COT26-0330-001…/armar_json.py:3` agrega al path el scratchpad de otra sesión (`/tmp/claude-0/…/82ad64dc…/scratchpad/ypf`), usa rutas absolutas (`R = "/home/user/cotizador-itt/"`) y en `:90` y `:122` **reescribe** `cotizacion.json` de los dos skids. Si alguien corrige el JSON a mano y vuelve a correr el script, pierde la corrección. Corrección: dejar `cotizacion.json` como fuente y mover el script a `antecedentes/` como registro, o hacerlo reproducible y documentado en la bitácora.

### BAJO

- **B1. Valor de control viejo en la documentación:** 7.620,59 en `web/LEEME.md:10`, `web/src/motor.js:2` y `estado_y_pendientes.md`; el vigente es 7.366,12 (`verificar_todo.py:22`, `probar_motor.js:2`).
- **B2. La CAPEX tiene `indices_congelados` estando en borrador,** contra la regla de `web/LEEME.md` ("se borra al volver a borrador"). Sirve para el control, pero hay que documentarlo.
- **B3. Formato de fecha de las fuentes contradictorio:** `_plantilla/README.md` acepta "AAAA-MM o AAAA", y `verificar_computo.py:96-98` exige AAAA-MM-DD (frena bien). La fórmula de la planilla (`armar_cotizacion.py:218`, `MAX(K, Índices!A2)` sin `MIN` con H7) sigue distinta del motor para fechas posteriores a la de referencia (E1 del 28-10).
- **B4. La lista para Compras muestra fechas AAAA-MM-DD:** `lista_compras.py:234` escribe `f["fecha"]` sin `a_vista` (E11 del 28-10, sigue abierto).
- **B5. El IVA no tiene campo en `cotizacion.json`:** solo hay un aviso si el texto dice "con IVA" (`verificar_computo.py:99-100`). El catálogo sí lo registra (columna `iva`). Ver la corrección de A2 (`iva_origen` en cada fuente).
- **B6. Eslabones manuales sin control:** `cotizacion_auto.json` → `cotizacion.json` (solo `precotizar.py --comparar`, informativo); `catalogo_nuevo` de la página → `listas_nuevas.csv` (copia a mano de la tarea semanal); `resumenes/<id>` de la página con totales que se recalculan a mano (`web/LEEME.md:56`).

---

## 3. Lo que funciona bien
- Python, la planilla recalculada con LibreOffice y `motor.js` dan lo mismo (CAPEX 7.366,12; YPF 713 182.148,08), y la oferta toma el precio de la planilla y frena si no cierra (`generar_oferta.py:57`).
- Una sola serie de dólar: `indices_ajuste.dolar_bna` = `dolar_mensual.oficial_promedio` en todos los meses (0 diferencias).
- Registro de códigos persistente en los catálogos, y regeneración determinística cuando se corre sola.
- `verificar_computo.py` frena con fechas inválidas o futuras, con precios `sin_ref` con valor y con posiciones faltantes.

## 4. Orden sugerido
1. C1 (sacar la PC0 como último precio) y C2 (plazo con bloqueo), antes de tocar más YPF.
2. A1 (escritura atómica y candado) antes de que más sesiones corran en paralelo.
3. A2 + A5 + M1: código de catálogo y `plano{}` en cada ítem, y números con `numeros.py`. Con eso `verificar_computo.py` puede controlar especificación y precio.
4. A3 y A4: qué entra a la base y quién es dueño de cada cotización.
