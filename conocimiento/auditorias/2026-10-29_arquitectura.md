# Auditoría de estructura, arquitectura e ingeniería (29-10-2026)

Alcance: organización del repo, acoplamiento, duplicación Python ↔ JS, pruebas, manejo de errores, reproducibilidad, tamaño y documentación. No cubre los datos de cada tabla ni el diseño visual (hay otras auditorías del mismo día: `2026-10-29_automatizaciones.md`, `2026-10-29_diseno_ux.md`; donde coincide, se cita en lugar de repetir).
Base: commit `78ac8c8`. Para no pisar a otros agentes, las corridas largas se hicieron en un clon descartable del repo, fuera de `/home/user/cotizador-itt`. No se modificó código ni datos.

## Resumen

1. El núcleo Python es determinístico y en un clon limpio `verificar_todo.py` da **TODO OK** (13 controles, 23 s). `actualizar_base.py --sin-red` también termina bien. Las 6 cotizaciones COT se rearman con 0 errores.
2. **Crítico:** las herramientas escriben los catálogos en el lugar, sin escritura atómica ni bloqueo, y LibreOffice comparte el perfil. Con dos corridas a la vez en el mismo árbol (pasó hoy con agentes en paralelo), los CSV del catálogo quedaron **corruptos** y el control falló. Además, el propio script indica "quedan 16 archivos modificados para revisar y subir".
3. Rearmar desde las fuentes **no reproduce lo que está en el repo**: hay derivados corregidos a mano o sin regenerar, y los 9 casos de control cambiaron de resultado sin que nadie lo notara, porque no están en `verificar_todo.py`.
4. El cálculo sigue repetido en Python, en el motor JS, en el Excel de la página, en el informe HTML y en una segunda calculadora de soldadura. La paridad cubre motor, ficha y rubros, pero no el Excel de la página, el informe, `busqueda.js` ni `antecedentes.js`.
5. La extracción de servicios (`herramientas/extraccion_servicios/`) no se puede volver a correr: depende de módulos de un scratchpad que ya no existe, y `run_all.sh` borra el CSV de producción. La documentación general (README, `web/LEEME.md`) quedó atrás del código.

---

## Hallazgos

### CRÍTICO

#### C1. Corridas simultáneas corrompen los catálogos, y el control invita a subir el resultado
- **Dónde:** `herramientas/verificar_todo.py:52-59` (regenera `catalogo_materiales.*` y `catalogo_servicios.*` en el lugar, dos veces). `herramientas/catalogo_materiales.py` y `catalogo_servicios.py` escriben directo sobre `conocimiento/precios/*.csv/xlsx` (en `herramientas/` no aparece `os.replace`, `rename`, `lock` ni `fcntl`). `herramientas/armar_cotizacion.py:281`, `generar_oferta.py:52,338` y `extraer_texto.py:46` llaman a `soffice --headless` sin `-env:UserInstallation` propio.
- **Qué pasó (verificado hoy):** `python herramientas/verificar_todo.py` corrió en `/home/user/cotizador-itt` mientras otros agentes corrían `actualizar_base.py`, `catalogo_materiales.py` y `verificar_todo.py` en el mismo container. Resultados:
  - Primera corrida: "catalogo_materiales.py no es determinístico", lo mismo con servicios, y `FileNotFoundError: /tmp/tmp…/COT26-1003-001_CAPEX_OQ8209.xlsx`. Con otro `soffice` abierto, LibreOffice devuelve 0 y no genera el archivo.
  - Segunda corrida: `UnicodeDecodeError ... byte 0xc3` al leer `catalogo_materiales_historial.csv` (`precotizar.py:117`) y `ValueError: invalid literal for int() ... '09.xlsx|código '` al leer `catalogo_codigos.csv` (`catalogo_materiales.py:788`). Es decir, escrituras intercaladas.
  - Al final: "Cambiaron datos: quedan 16 archivos modificados para revisar y subir" (`verificar_todo.py:84`). Los 16 eran catálogos y entregables de la CAPEX, corruptos o a medio escribir.
  - En un clon aislado, con el mismo commit, todo da OK. El problema es la concurrencia, no el código del cálculo.
- **Por qué importa:** el proyecto lanza agentes en paralelo de forma habitual (controles con 4 agentes, auditorías, "Chat nuevo"), y la regla es que todo termina en `main`. Un agente que siga el mensaje del control puede subir a `main` un catálogo corrupto, del que leen la precotización, la página (`datos.json`) y todas las cotizaciones. Es justo el tipo de falla por pérdida de información que CLAUDE.md pide evitar.
- **Corrección propuesta:**
  1. Bloqueo exclusivo en `verificar_todo.py`, `actualizar_base.py` y `armar_cotizacion.py`: un archivo `.lock` en la raíz con `fcntl.flock`. Si está tomado, salir con "otra corrida en curso".
  2. Escritura atómica: helper `escribir_atomico(ruta, contenido)` que escriba en `ruta.tmp` y haga `os.replace`. Usarlo en todos los CSV, XLSX y JSON de la base.
  3. `soffice` con perfil propio (`-env:UserInstallation=file:///tmp/lo_<pid>`), y control explícito de que el archivo convertido existe, con un mensaje claro.
  4. Que `verificar_todo.py` nunca diga "para revisar y subir" si hubo fallas: en ese caso, "NO SUBIR: restaurar con git".
  5. Mejor todavía: que `verificar_todo.py` regenere en un directorio temporal (o en un `git worktree` descartable) y compare contra el repo, sin tocar el árbol de trabajo.
  6. Para agentes en paralelo, documentar en `web/LEEME.md` y en CLAUDE.md que cada uno trabaja en su propio worktree.

### ALTO

#### A1. Rearmar desde las fuentes no da lo que está en el repo (derivados editados a mano o sin regenerar)
- **Verificado en un clon limpio:**
  - `python herramientas/indice_precios.py` (dentro de `actualizar_base.py`) cambia 14 líneas de `conocimiento/precios/indice_precios.csv`. Por ejemplo, MS Juntas pasa de un renglón de 728,96 a tres renglones (314,16 + 37,24 + 377,56). Coincide con B8 de `2026-10-29_automatizaciones.md`.
  - `python herramientas/construir_base.py` cambia `conocimiento/comercial/cotizaciones_2024-2026.csv`: en la oferta PAMPA Doc5757155642, `probabilidad_pct` vuelve a **2026.0**. En el repo alguien lo corrigió a mano en el CSV derivado, pero el arreglo no está en la fuente ni en `construir_base.py:512`, así que se pierde en el próximo rearmado.
  - `armar_cotizacion.py` sobre las 5 cotizaciones COT que no son la CAPEX reescribe sus `controles_tablas.md`. En `COT26-0330-001_YPF_LIC69343_SKID713/controles_tablas.md`, el peso pasa de **6.981,3 kg a 8.732,7 kg** y los ítems sin peso de 20 a 8: el informe del repo es anterior a las tablas nuevas de pesos.
- **Por qué importa:** viola "una sola versión vigente de cada dato". Quien lea el repo ve números que ya no salen del código, y una corrección manual se pierde sin aviso.
- **Corrección propuesta:**
  1. Las correcciones van en la fuente o en una tabla de correcciones que lea el constructor, con fecha y motivo en `fuentes.md`. Nunca en el CSV generado.
  2. Agregar a `verificar_todo.py` un control de "rearmado limpio": en un worktree temporal, correr `actualizar_base.py --sin-red`, `construir_base.py` y `armar_cotizacion.py` sobre cada COT, y comparar los CSV, JSON y MD contra HEAD. Ignorar los binarios (ver B6).
  3. Regenerar y subir ahora los derivados desactualizados.

#### A2. Los 9 casos de control de la precotización no están en `verificar_todo.py` y ya cambiaron sin aviso
- **Dónde:** `herramientas/correr_controles.py`; `cotizaciones/controles_resultado.md` (último commit 28-10-2026 15:48); `herramientas/verificar_todo.py` no lo llama.
- **Qué pasa (verificado):** al correr `correr_controles.py` en el clon cambian `controles_resultado.md` y los 9 `cotizacion_auto.json`, `precotizacion.md` y `comparacion_historico.md`. Por ejemplo, SK01 pasa de −14% a **−17%**, F01 de −43% a −35% (sin precio: de 6 a 3) y P02 de 1 sin precio a 0. `conocimiento/estado_y_pendientes.md:37` todavía dice "SK01 −14%".
- **Por qué importa:** son la única medida de exactitud del cotizador automático contra costos reales, que es el objetivo del proyecto. Hoy un cambio en el catálogo o en las reglas puede empeorar la precotización sin que lo detecte ningún control.
- **Corrección propuesta:** sumar `correr_controles.py` a `verificar_todo.py` con valores esperados por caso (diferencia y cantidad sin precio) y tolerancia, como `CONTROL` de la CAPEX. Si un caso se aleja más de N puntos, que falle con el detalle. Actualizar el esperado solo a propósito, anotando el porqué.

#### A3. Cálculo repetido sin paridad completa: Excel de la página, informe HTML y una segunda calculadora de soldadura
- **Dónde y estado:**
  - Con paridad automática: `web/src/motor.js` ↔ `armar_cotizacion.calcular` (`probar_motor.js`, CAPEX y un caso Taval), `web/src/ficha.js` ↔ `ficha_rubros.py` (`probar_ficha.js`, todas las cotizaciones con plano) y `web/src/rubros.js` ↔ `ficha_rubros.py` (`probar_rubros.js`).
  - **Sin paridad automática:**
    - `web/src/documentos.js:82-120` arma el Excel de la página con fórmulas propias (`VLOOKUP`/`EDATE` por renglón, `SUM(...)*(1+B8)`), con otra estructura que la planilla de Python (`armar_cotizacion.py:181-191`, `B24`/`D27`/`E28`). Nadie la recalcula con LibreOffice contra `Motor.calcular`.
    - `plantillas/informe_cotizacion.html:284-343` (`fac`, `calc`) es otra copia del cálculo, que corre en el navegador del informe. No se ejecuta en ninguna prueba.
    - `web/src/busqueda.js:130` (`soldadura`) es un algoritmo distinto de `precotizar.soldaduras`: en la CAPEX da **13,085** pulgadas contra **13,37** de Python (`probar_busqueda.js` frente a `test_precotizar.py:29`). Lo usan `rubros.js:75` (ficha aproximada) y las calculadoras de `app.js` (ver M4).
    - `web/probar_busqueda.js` existe y pasa, pero **no está en `verificar_todo.py`**.
    - `web/src/antecedentes.js` ↔ `buscar_antecedentes.py`/`comparar_antecedentes.py`: lo verifiqué a mano con la CAPEX de `web/semilla.json` y dio los mismos 5 y el mismo aviso. No hay prueba automática, y el resultado depende de que los ítems tengan `plano` (con `cotizacion.json` sin `plano`, el JS da otros 5).
- **Por qué importa:** un cambio de regla hecho en Python (por ejemplo, la contingencia o los factores) puede no llegar al Excel ni al informe que se descargan y se mandan a revisar, y con la cobertura actual no se nota.
- **Corrección propuesta:**
  1. Sumar `node web/probar_busqueda.js` a `verificar_todo.py`.
  2. Prueba nueva: generar el Excel de la página en node (con `xlsx-js-style` local), recalcularlo con LibreOffice y compararlo con `Motor.calcular` en todas las COT.
  3. Prueba nueva: ejecutar `calc()` del `informe.html` generado (con jsdom o extrayendo la función) y compararlo con Python.
  4. Que `rubros.js` use `Ficha.soldaduras` y borrar `Busqueda.soldadura`.
  5. Paridad de antecedentes con todas las COT de `semilla.py`.

#### A4. La extracción de servicios no se puede reproducir y su script borra el CSV de producción
- **Dónde:** `herramientas/extraccion_servicios/run_all.sh:1-4`: hace `cd /tmp/claude-0/.../82ad64dc-.../scratchpad`, después `rm -f /home/user/cotizador-itt/conocimiento/precios/servicios_extraidos.csv` y corre `b[0-9][0-9]_*.py`. Todos los `b*.py` hacen `from core import R` o `from agregar import agregar` (`b01_fijas.py:1` agrega al path ese scratchpad), y esos módulos **no están en el repo**.
- **Por qué importa:** `servicios_extraidos.csv` es una entrada de `catalogo_servicios.py:132`, o sea, del catálogo de MO y servicios. Si alguien corre `run_all.sh`, borra el CSV y los scripts fallan: el catálogo queda sin esa fuente. Y si hay que corregir un precio extraído, no se puede volver a generar. Esto contradice "todo lo que se procese se guarda en el repositorio".
- **Corrección propuesta:** recuperar o reescribir `core.py` y `agregar.py` dentro de `herramientas/extraccion_servicios/`, cambiar `run_all.sh` para que use rutas relativas al repo y escriba en un temporal que reemplace al CSV solo si todo terminó bien. Si no se van a volver a correr, mover la carpeta a `herramientas/historico/`, declarar `servicios_extraidos.csv` como **fuente** (no derivado) en `fuentes.md` y borrar `run_all.sh`.

### MEDIO

#### M1. Utilidades compartidas dentro de scripts constructores e imports circulares
- **Dónde:** `indice_proyectos.norm` (el constructor del índice) lo importan 13 módulos (`buscar_material.py:26`, `catalogo_materiales.py:39`, `precotizar.py:37`, `ficha_rubros.py:32`, …). `catalogo_materiales.py`, el constructor de 900 líneas, funciona además como biblioteca de `atributos`, `familia_de`, `expandir`, `iva_de`, `ESPESORES` y `OD_NPS` para `precotizar`, `plazo`, `lista_compras`, `controles_tablas`, `ficha_rubros` y `catalogo_servicios`. Hay ciclos tapados con imports dentro de funciones: `armar_cotizacion.py:389` importa `ficha_rubros`, que importa `armar_cotizacion` (`ficha_rubros.py:226`), y lo mismo pasa con `comparar_antecedentes.py:31`. Además, `armar_cotizacion.py:399` regenera el índice global (`indice_proyectos.main()`) cada vez que se arma una cotización. Hay `sys.path.insert` en 22 scripts.
- **Por qué importa:** un cambio en un constructor (por ejemplo, en `norm`) cambia en silencio la búsqueda, la precotización y los catálogos. Armar una cotización tiene efectos globales.
- **Corrección propuesta:** paquete `herramientas/comun/` con `texto.py` (`norm`, `frac`, `pulgadas`), `materiales.py` (`atributos`, `familia_de`, `expandir`), `iva.py` y `tablas.py` (leer los espesores del CSV). Los constructores y la cotización importan de ahí. Sacar `indice_proyectos.main()` de `armar_cotizacion` y dejarlo en `actualizar_base`, o hacerlo opcional con `--indexar`.

#### M2. Más de una fuente por cotización
- **Dónde:** `cotizaciones/COT26-0135-001/armar_json.py:138`, `-002/armar_json.py:109`, `-003/armar_json.py:82,146` y `COT26-0330-001/armar_json.py:90,122` **reescriben `cotizacion.json`** (y el 003 también `pedido/lista_materiales_plano.csv`). El de YPF escribe también la carpeta del 708, y el 003 importa código de la carpeta del 001 (`sys.path.insert(... "COT26-0135-001_...")`). A esto se suma la base de la página: `cotizaciones_web/` respalda 1 cotización de las 6 que tiene la página (último respaldo el 28-10-2026). En la página el guardado sigue siendo "gana el último" (`web/src/app.js:141`: "se guardan tus cambios encima"), como ya marcaba A3 de `2026-10-28_revision_arquitectura.md`.
- **Por qué importa:** CLAUDE.md dice "la única fuente de datos es `cotizacion.json`". Hoy esos scripts lo reproducen igual (verificado en el clon), pero cualquier corrección hecha en el JSON, en la página o al consolidar se pierde si alguien vuelve a correr `armar_json.py`.
- **Corrección propuesta:** decidir que `armar_json.py` es solo para el primer armado: renombrarlo a `historico_armado_inicial.py` con un aviso al principio, o hacer que se niegue a escribir si `cotizacion.json` existe y es distinto. Pasar `camuzzi_comun.py` a `herramientas/` si es reutilizable. Respaldo de la página completo y diario.

#### M3. Orden de `actualizar_base.py`: hacen falta dos corridas para un cambio en la Lista 30 de Taval
- **Dónde:** `herramientas/actualizar_base.py:18-19`. `pesos_valvulas.py`, que escribe `conocimiento/precios/taval_lista30.csv`, corre **último**, después de `catalogo_materiales.py`, que lo lee (`catalogo_materiales.py:701`). `construir_base.py` y `consolidar_fichas.py` no están en la cadena.
- **Por qué importa:** con una lista nueva de Taval, el catálogo sigue con la lista anterior hasta la próxima corrida, y `verificar_todo` no lo detecta.
- **Corrección propuesta:** poner `pesos_valvulas.py` antes de `catalogo_materiales.py`. Mejor aún, declarar en cada script qué lee y qué escribe, y ordenar la cadena con eso (un `make` simple o una lista de dependencias). Documentar cuándo corre `construir_base.py`.

#### M4. Código muerto de las calculadoras sueltas en la página
- **Dónde:** `web/src/app.js:176-221` (`tarifaPH`, `tarifasPintura`, `agregarSoldaduras`, `agregarRx`, `m2Canos`, `agregarPintura`, `agregarPH`), los handlers `:805-810`, `:956-968` y `:999`, la lista `CAMBIAN` en `:889` y las exportaciones en `window.ITT` (`:1089`). Ningún template genera `data-a="sold-agregar"`, `rx-agregar`, `pin-calc`, `pin-agregar`, `ph-agregar`, `sold-fila` ni `data-sold` (lo busqué en `app.js`, `rubros.js` y `pagina.html`). Además, `:809` hace `document.querySelector('[data-a="sold-agregar"]').disabled`, que tiraría error si se ejecutara.
- **Por qué importa:** son unas 60 líneas que mantienen viva la segunda calculadora de soldadura (A3), confunden al leer y se exponen en `window.ITT` sin uso (el chat que las usaba ya no existe).
- **Corrección propuesta:** borrarlas junto con `Busqueda.soldadura` y `S.sold`, y ajustar `Rubros.ficha` para que no reciba `S.sold`.

#### M5. `armar_cotizacion.py` escribe antes de validar y da errores crudos
- **Dónde:** `herramientas/armar_cotizacion.py:372-386`. Escribe el cómputo, la planilla, la lista de compras y el informe, y **recién después** compara Python con la planilla y corre `verificar_computo`: así quedan entregables con números que no pasaron el control (M5 de la revisión del 28-10, sigue abierto). En las 9 carpetas `CTRL-*` y en `_plantilla`, `cotizacion.json` es la plantilla, con `"fecha_respuesta": "AAAA-MM-DD"`. `armar_cotizacion` las rompe con `ValueError: Invalid isoformat string` (`lista_compras` vía `date.fromisoformat`) y deja un `computo.csv` suelto (verificado).
- **Corrección propuesta:** validar `cotizacion.json` al entrar (fechas con `numeros.fecha_iso`, placeholders `AAAA`/`[CLIENTE]`, campos obligatorios) con un mensaje claro. Generar los entregables en un temporal y moverlos solo si pasan los controles. En las `CTRL-*`, renombrar el JSON a `parametros.json` o hacer que `armar_cotizacion` las rechace con el mensaje "caso de control: usar correr_controles.py".

#### M6. Documentación desactualizada respecto del código
- `README.md:46` dice que `fuentes_originales/` "no se sube al repositorio", pero hay 1.245 archivos versionados (168 MB). `README.md:16` muestra el catálogo de MO "⏳ En curso", aunque está vigente. La tabla de herramientas (`README.md:44-61`) omite 25 de 45 scripts, entre ellos `verificar_todo.py`, `precotizar.py`, `actualizar_base.py`, `ficha_rubros.py` y `plazo.py`.
- `web/LEEME.md:4` declara la capacidad `sample` ("chat con Claude"), pero el código solo usa `db`, `assets`, `downloads` y `mcp` (`app.js:31`, `asistente.js:25`). `:10` dice "control: CAPEX = USD 7.620,59" y el vigente es 7.366,12 (B9 de automatizaciones). `:11` menciona la "calculadora de soldaduras". `:17` describe `asistente.js` como un chat con herramientas que ya no existe.
- `web/src/motor.js:2` también dice 7.620,59. `conocimiento/estado_y_pendientes.md:27` todavía lista "calculadoras (soldadura, pintura, PH, RX)", `:138` usa 7.620,59 como control para el nuevo colaborador y `:37` tiene porcentajes de control viejos (A2).
- **Corrección propuesta:** actualizar esos textos. Que el README remita a `estado_y_pendientes.md` y a un listado de herramientas generado desde los docstrings (`python herramientas/listar_herramientas.py`), así no se vuelve a desactualizar. Sacar `sample` de las capacidades de la página si no se usa (menor privilegio).

### BAJO

- **B1. El valor de control está en 4 lugares:** `verificar_todo.py:22`, `web/probar_motor.js:17`, `web/src/motor.js:2` y `web/LEEME.md:10`; dos ya quedaron viejos. Dejarlo en un solo archivo (`cotizaciones/COT26-1003-001_CAPEX_OQ8209/control.json`) y leerlo desde las pruebas.
- **B2. Lectores de números locales en vez de `numeros.py`:** `verificar_computo.py:29` lee "4.500" como 4,5. `catalogo_materiales.py:490` y `indice_proyectos.py:58` hacen `float` directo. Hoy leen formatos internos, pero CLAUDE.md pide un lector único. Reemplazarlos por `numeros.numero`.
- **B3. Tablas técnicas duplicadas en el código:** `catalogo_materiales.py:237-247` (`OD_NPS`, `ESPESORES`, con 78 combinaciones) frente a `conocimiento/tecnico/factores_soldadura.csv` (162). Los valores coinciden donde están los dos, pero STD y XS de 10" a 18" solo existen en el código. `web/src/ficha.js:19` repite `OD_NPS`. Leer todo del CSV, también en `datos.json`.
- **B4. Dependencias:** `requirements.txt` no fija versiones. `docling` (pesado, trae modelos de huggingface) solo lo usa `verificar.py`; ninguna herramienta lo importa. `setup.sh` no menciona Node 22 ni LibreOffice, que `verificar_todo.py` y `armar_cotizacion.py` necesitan. Las tres librerías de CDN de `web/src/pagina.html:289-291` no tienen `integrity` (SRI).
- **B5. Archivos huérfanos o sin uso:**
  - `top.png` en la raíz (196 kB, sin referencias; entró en `0eb5330`).
  - `herramientas/extraccion_servicios/b01.py`: el glob de `run_all.sh` lo deja afuera.
  - `fuentes_originales/diagrama_proceso_2022-09.docx`: ningún código ni documento lo menciona.
  - Imports sin uso: `re` en `buscar_antecedentes.py` y `unir_planillas_costo.py`, `date` en `catalogo_materiales.py`, `qn` en `web/construir_datos.py`.
- **B6. Tamaño y derivados versionados:** `.git` ocupa 173 MB (pack de 83 MB). Varios derivados cambian de bytes en cada corrida y se suben una y otra vez: `web/cotizador.html` (38 commits), `catalogo_materiales.xlsx` (24) y `web/datos.json` (5 MB, 11 commits). `datos.json` además lleva las plantillas .docx en base64 (1,7 MB) y no es determinístico: al rearmarlo solo cambian `docx_tecnica` y `docx_economica`. `fuentes_originales/codificador_taval_2023-07.xlsx` pesa 46 MB. Con varias sesiones que pasan a `main`, los binarios en conflicto no se pueden unir: hay que regenerarlos. Fijar las fechas internas de los zip (como propone M3 de automatizaciones) y considerar Git LFS para `fuentes_originales/*.pdf|xlsx`.
- **B7. `web/probar_ficha.js:13-28`** tiene incrustada una copia en Python de la lógica de `semilla.py` (plano, `fam_at`). Si cambia `semilla.py`, la prueba deja de representar lo que ve la página. Mejor que llame a `semilla.py` directamente.

---

## Pruebas: qué cubre `verificar_todo.py` y qué queda afuera

**Cubre:** `test_catalogo.py`, `test_catalogo_servicios.py`, `test_precotizar.py` (solo la CAPEX); determinismo del CSV de cada catálogo (no del historial ni de los códigos); armado de la CAPEX (Python = planilla con LibreOffice, `verificar_computo`, `controles_tablas`, `plazo`, `ficha_rubros`, `comparar_antecedentes`, `generar_oferta`, `lista_compras`, `indice_proyectos`) con precio de control; `probar_motor.js`, `probar_rubros.js` y `probar_ficha.js`.

**Queda afuera:**
- Los 9 casos `CTRL-*` (A2).
- Las otras 5 cotizaciones COT: se rearman bien, pero nadie lo controla.
- `probar_busqueda.js`; la paridad de `antecedentes.js`, del Excel de la página (`documentos.js`) y del cálculo del informe (A3).
- Que `web/cotizador.html` sea igual a `src/`, y `datos.json` igual a los CSV. Hoy están al día (verificado), pero nada lo garantiza.
- `semilla.py`, `respaldo_base.py` e `indices_para_pagina.py`.
- Los constructores (`construir_base`, `indice_precios`, `unir_planillas_costo`, `listas_vendedor`, `pesos_valvulas`, `acero_por_kg`, `dolar_mensual`, `indices_inflacion`) y el rearmado limpio contra HEAD (A1).
- `app.js` y `asistente.js` (interfaz).
- La validación de entrada de `cotizacion.json` (M5).
- La concurrencia (C1).

## No verificado
- Que la página publicada (Artifact) sea igual a `web/cotizador.html` local.
- Los flujos de la página con la base real (se cubren en `2026-10-29_diseno_ux.md` y `2026-10-29_automatizaciones.md`).

## Orden sugerido
1. C1: bloqueo, escritura atómica, perfil propio de `soffice`, y que el control no invite a subir si falló.
2. A2 y A3: controles CTRL, `probar_busqueda` y la paridad del Excel de la página en `verificar_todo.py`.
3. A1: control de rearmado limpio y regenerar los derivados viejos.
4. A4: dejar reproducible (o declarar como fuente) la extracción de servicios.
5. M1 a M6, después lo bajo.
