# Evaluación de arquitectura e ingeniería — Cotizador ITT

Revisión hecha el 28-10-2026 sobre `/home/user/cotizador-itt` (commit `44bcd30`). Solo lectura: no se tocó el repo.
Corrí: `python herramientas/verificar_todo.py` → **TODO OK** (17,7 s; restauró 9 derivados), `node web/probar_motor.js` → **OK, unitario 7.620,59**, `node web/probar_busqueda.js` → **OK**. Pruebas extra (borde) con scripts en `scratchpad/agentes/arquitectura/`.

## Resumen ejecutivo

1. La base Python es sólida: tiene un cálculo determinístico, una planilla con fórmulas que se contrasta con LibreOffice, controles contra el plano y un caso de control. La página web, en cambio, **no tiene esas defensas**: con un clic se pasa una cotización a "aprobado", la oferta sale sin la leyenda de borrador y con la firma, y no hubo control contra el plano ni revisión.
2. El precio **no queda congelado**: depende de índices que todavía se van a corregir (el mes de referencia tiene IPC y CPI estimados y el dólar a mitad de mes). El control de la CAPEX (7.620,59) **va a fallar en la próxima tarea semanal** y las cotizaciones de la página cambian de precio solas.
3. El cálculo está **escrito 5 veces**: Python, Excel de Python, motor JS, Excel de la página e informe HTML. Además hay 2 algoritmos de soldadura y 2 buscadores. Solo hay una prueba de paridad, con un único caso (la CAPEX). Las pruebas JS no corren en `verificar_todo.py`. Ya encontré divergencias reales con fechas incompletas, grupos mal escritos y soldaduras.
4. En la base de la página **gana el último que escribe** (`set` sin versión): los cambios de Claude Code se pisan si el usuario tiene algo sin guardar. El respaldo es semanal y solo cubre las cotizaciones.
5. Seguridad: pdf.js 3.11.174 tiene una vulnerabilidad conocida (CVE-2024-4367) y abre PDFs de proveedores dentro de una página con permisos de base y de envío a una sesión con push al repo, que procesa pedidos "sin pedir autorización". Además, `datos.json` publica costos propios aunque su comentario dice que no.

---

## Hallazgos por gravedad

### CRÍTICO

#### C1. La página permite aprobar una cotización sin ningún control, y la oferta "aprobada" sale con la firma
- **Evidencia:**
  - `web/src/app.js:247`: botones de estado `borrador/revisado/aprobado/enviado`, todos habilitados.
  - `app.js:689`: `case "estado": cot.estado = b.dataset.v; …` no valida nada (ni avisos, ni revisión, ni quién aprueba).
  - `app.js:775`: con `aprobado` o `enviado` la oferta sale sin leyenda (`documentos.js:381-385`, `:411`) y con la imagen de la firma (`documentos.js:232`).
  - El chat solo puede proponer "revisado" si no hay avisos `bad` (`asistente.js:574`), pero el botón manual saltea incluso eso.
  - La página no tiene el control P2 contra el plano: `verificar_computo.py` necesita `pedido/lista_materiales_plano.csv`, y las cotizaciones creadas en la página no lo tienen. `Busqueda.avisos` (`busqueda.js:143-165`) no compara contra el plano, ni la cantidad, ni el grupo.
  - Una cotización aprobada **sigue editable** y su oferta se regenera con los precios del momento.
- **Impacto:** un borrador con errores puede salir como oferta firmada con un clic. Es justo el escenario que el procedimiento (P9/P10, estados borrador → revisado → aprobado) quiere evitar, y "un error que llega al cliente puede ser catastrófico".
- **Propuesta:**
  1. "revisado" exige 0 avisos `bad` y un campo `revisado_por` con fecha.
  2. "aprobado" exige "revisado", `aprobado_por` distinto de `revisado_por` y una confirmación explícita.
  3. Al aprobar se **congela una instantánea** (`cot`, `oferta`, índices usados, `calc` completo y un hash) en `cotizaciones/<id>/emitidas/<rev>`, y las descargas de una aprobada salen de esa instantánea, nunca de un recálculo.
  4. Editar una aprobada la devuelve a borrador y sube la revisión.
  5. Mostrar en la página un control "plano vs cómputo" cuando el ítem tiene `plano` (o exigir la tabla del plano para pasar a revisado).

### ALTO

#### A1. El precio cambia solo, y el control de la CAPEX va a fallar el lunes 02-11-2026
- **Evidencia:**
  - La CAPEX tiene `fecha_referencia` `2026-10-27`.
  - En `conocimiento/costos/indices_ajuste.csv`, el renglón `2026-10` tiene IPC y CPI **ESTIMADOS** (`herramientas/indices_inflacion.py:34,57`) y el dólar con "27 días, último 2026-10-27".
  - Los últimos datos diarios (`fuentes_originales/indices/dolar_diario.csv`) están en 1.560, contra un promedio de 1.540,74. El promedio de octubre va a subir alrededor de 0,2–0,3%.
  - Sensibilidad medida con el motor: dólar de octubre +0,3% → **7.616,82**; con CPI +0,1% → **7.622,93**.
  - `verificar_todo.py:24` compara contra `"7,620.59"` fijo, así que `actualizar_base.py` en la tarea semanal va a terminar en FALLA.
  - En la página, `resumenDe` (`app.js:47`) guarda un unitario que después no coincide con el recálculo, y una oferta "enviada" que se vuelve a descargar sale con otro precio.
  - La decisión del 28-10 ("una cotización calculada no cambia sola de precio", `estado_y_pendientes.md:54`) **no se cumple** cuando el mes de referencia está abierto o estimado.
- **Impacto:** falsas alarmas en la tarea semanal, o la tentación de "actualizar CONTROL" sin entender por qué cambió. Precios que se mueven después de enviados.
- **Propuesta:**
  - Guardar en cada cotización los **índices congelados** (los renglones usados, o al menos `idx[fref]`) y calcular con esos. Recalcular con índices nuevos solo de forma explícita ("actualizar índices"), mostrando la diferencia.
  - El caso de control usa su propia tabla de índices fija (por ejemplo `cotizaciones/<CAPEX>/indices_congelados.csv`).
  - Como alternativa mínima: no permitir una `fecha_referencia` en un mes sin cerrar (usar el último mes con dato completo).

#### A2. Cinco implementaciones del cálculo y lógica duplicada Python ↔ JS con divergencias reales
- **Dónde está cada copia:**
  - `herramientas/armar_cotizacion.py:64-89` (Python).
  - Las fórmulas de la planilla, en `armar_cotizacion.py:152-199`.
  - `web/src/motor.js:5-36`.
  - Las fórmulas del Excel de la página, en `web/src/documentos.js:63-103`.
  - `plantillas/informe_cotizacion.html:283-338` (`fac` y `calc`).
  - Además, soldaduras en `precotizar.py:138-175` y `busqueda.js:124-136`; búsqueda en `buscar_material.py` y `busqueda.js`; antecedentes en `buscar_antecedentes.py`/`comparar_antecedentes.py` y `antecedentes.js`; avisos en `verificar_computo.py` y `busqueda.js:143`.
- **Divergencias encontradas:**
  - **Fecha solo con año (`"2025"`):** Python y JS toman el índice de **dic-2024** (comparan textos: `"2025" < "2025-01"`). El Excel de Python usa **jul-2025** (`armar_cotizacion.py:58-60`). El Excel de la página usa **ene-2025** (`documentos.js:27`, `m || 1`). Son tres resultados distintos. Python lo detectaría al comparar con LibreOffice (`armar_cotizacion.py:361`); la página **no lo detecta nunca**.
  - **Fecha vacía o en formato DD-MM-AAAA:** el motor JS no avisa y toma el **primer mes de la tabla** (factor 1,089, es decir +9% en materiales). Python lanza una excepción.
  - **Grupo mal escrito** (`"materiales"`): el ítem queda **fuera del precio** en JS sin avisar (CAPEX 7.620,59 → 7.612,27). Python lanza `KeyError`. `avisos` no lo detecta.
  - **Precio escrito como texto** (`"1.234,5"`): el JS da `NaN`. La cantidad negativa se acepta.
  - **Soldadura:** `precotizar.py` da **13,37** pulgadas en la CAPEX y la página y la cotización revisada usan **13,09** (`test_precotizar.py:28` y `probar_busqueda.js:14` fijan los dos valores). Python promedia los diámetros de los dos extremos (reducción); JS multiplica juntas por un solo DN.
  - **Redondeo:** Python `round(2.675,2)=2.67`, JS y Excel dan `2.68`. La diferencia máxima es de 0,01 y entra dentro de la tolerancia de 0,011.
  - **Leyenda:** Python pone la leyenda de borrador también en "enviado" (`generar_oferta.py:309`), y la página no (`app.js:775`).
- **Cómo se detecta hoy:** solo con `probar_motor.js` (1 caso, 3 números) y `probar_busqueda.js`. **Ninguno corre en `verificar_todo.py`.** Tampoco se controla que `web/datos.json` esté al día con los CSV, ni que `cotizador.html` coincida con `src/` (hoy sí coincide; lo verifiqué).
- **Propuesta:**
  1. Que `verificar_todo.py` corra `node web/probar_*.js` y una **prueba de paridad con varios casos**: generar 50–100 cotizaciones sintéticas (fechas límite, AJ=0/1, TRANS, N, grupos, ítems sin MO) y comparar Python, JS y el informe al centavo.
  2. Validar el **esquema** de `cotizacion.json` (JSON Schema compartido por Python y JS: grupo ∈ {material, mo, servicio}, precio y cantidad numéricos ≥ 0, fecha `AAAA-MM-DD`) antes de calcular, en los dos lados.
  3. Tener un solo algoritmo de soldadura, que JS reciba los extremos como Python, más un test con la CAPEX que dé el mismo número.
  4. El Excel generado en la página: probarlo en CI con LibreOffice (node + `xlsx-js-style` → `soffice --convert-to` → comparar D27/E28).

#### A3. Concurrencia en la base de la página: gana el último que escribe
- **Evidencia:**
  - `app.js:65-66`: `set(doc)` y después `set(resumen)`, sin `if_version` y sin atomicidad.
  - `app.js:136`: si llega un cambio de Claude Code u otra persona mientras hay cambios locales sin guardar, **se pisa** y solo aparece un toast ("se guardan tus cambios encima").
  - `web/LEEME.md:212` le pide a Claude Code usar `if_version`, pero la página no lo usa, así que la protección es de un solo lado.
  - `app.js:106`: `beforeunload` llama a un `guardar()` asíncrono que no llega a terminar.
  - El deshacer del chat (`asistente.js:643`) restaura una copia entera del documento, y puede pisar cambios manuales posteriores.
  - `versionar` (`app.js:74-79`) borra las versiones viejas una por una sin control de errores.
- **Impacto:** se pierden en silencio correcciones de Claude Code o de otra persona, justo en el flujo de pedidos que se promociona.
- **Propuesta:**
  - Guardar con `if_version` (o un campo `rev` incremental). Ante un conflicto, no pisar: guardar lo local como versión `conflicto-<hora>` y mostrar un aviso bloqueante con la diferencia.
  - Escribir cotización y resumen en un `batch`.
  - En `beforeunload`, avisar al usuario (`e.preventDefault()`) si hay cambios pendientes.

#### A4. Superficie de ataque: PDFs de proveedores, librerías viejas y pedidos con permisos de escritura
- **Evidencia:**
  - `asistente.js:314`: carga **pdf.js 3.11.174** sin `isEvalSupported: false` (`:318`). La CVE-2024-4367 permite ejecutar JS con un PDF armado, y se corrigió en 4.2.67. Ese JS correría en una página con capacidades `db`, `assets`, `mcp` (send_message a la sesión con push) y `sample`.
  - `pagina.html:186`: `xlsx-js-style@1.2.0` (basada en una SheetJS vieja; CVE-2023-30533, contaminación de prototipos al **leer** un archivo) y `XLSX.read` sobre archivos subidos (`asistente.js:66`).
  - Ningún `<script>` tiene SRI.
  - `CLAUDE.md:45`: "Los pedidos de la página se procesan sin pedir autorización". `asistente.js:126-130` pone el texto del pedido tal cual en el mensaje a la sesión, y el tipo `otro` es "lo que pida" (`LEEME.md:214`).
  - El destino sale de `config/claude_code` en la base (`asistente.js:28`): cualquiera con edición puede redirigir los pedidos o mandar instrucciones.
- **Impacto:** un PDF o Excel malicioso de un tercero, o alguien con edición en la página, puede inducir cambios en el repositorio, en los catálogos o en las cotizaciones.
- **Propuesta:**
  - Subir pdf.js a ≥ 4.2.67 (o pasar `isEvalSupported:false`) y cambiar `xlsx-js-style` por SheetJS ≥ 0.20.x del CDN oficial (o hacer el parseo en un Worker).
  - Fijar la sesión destino en el código (no en la base) o validarla contra una lista.
  - En la sesión, tratar `texto` y archivos como datos. Para el tipo `otro`, y para todo lo que no sea crear o actualizar borradores, pedir confirmación.
  - Limitar el `git push` de la sesión de pedidos a una rama `pedidos/*` con merge manual.

#### A5. Datos de entrada sin validar en la página y en el chat
- **Evidencia:**
  - `motor.js:24-29` no valida grupo, tipo numérico ni fecha.
  - `busqueda.js:99,111`: un registro del catálogo sin fecha recibe `hoy()`, o sea que un precio sin fecha parece nuevo y no se ajusta. Casos reales en `datos.json`: `CAN-01383`, `FAB-00028`.
  - `app.js:168`: `t.fecha + "-31"` arma fechas inválidas (`2024-09-31`, `2026-31`) si la tarifa es de un mes de 30 días o solo trae el año (hay tarifas con `fecha: "2026"`). Python se rompe (`date(2024,9,31)`) y la página arma un Excel con otra fecha.
  - Soldadura: si el DN o el schedule no están en la tabla, se usa **factor 1,0 sin avisar** (`busqueda.js:128`, `precotizar.py:134`).
  - El chat puede cambiar `FM`, `FMO`, `CONT`, `AJ` y `TRANS` sin confirmación (`asistente.js:478-493`), cuando "el factor lo define la dirección".
- **Propuesta:**
  - Aplicar el esquema de A2.
  - Fecha de tarifa = último día real del mes (o el día 1, como en `fecha()`); sin fecha → aviso `bad`, nunca `hoy()`.
  - Soldadura: aviso `bad` cuando no hay factor.
  - Cambios de factor o ajuste desde el chat: botón de confirmación, como borrar.

### MEDIO

#### M1. Dos fuentes de verdad por cotización (repositorio y página)
- **Evidencia:**
  - La CAPEX vive en `cotizaciones/COT26-1003-001_CAPEX_OQ8209/cotizacion.json` y en la base (`cotizaciones_web/capex-oq8209/`). Ya difieren en textos de fechas (`13-04-2026` vs `13/04/2026` en M21, en `pie` y en otros 7 campos). El precio por ahora coincide.
  - Los ids no siguen la convención de `LEEME.md:211` (`c26-1003-001`), sino `capex-oq8209`.
  - El flujo `actualizar_cotizacion` (`LEEME.md:212`) decide dónde trabajar según "si está en el repositorio con el mismo código".
- **Propuesta:** definir una sola dueña por cotización (campo `origen: repo|pagina`) y, al sembrar o respaldar, comparar el hash y avisar si divergen. Normalizar los ids.

#### M2. Respaldo incompleto y pérdida posible de hasta 7 días
- **Evidencia:**
  - `web/respaldo_base.py` copia solo `cotizaciones`. No copia `versiones`, `firmantes`, `pedidos`, `catalogo_nuevo` (hasta que se incorpora) ni assets (firma, imagen del plano de la oferta).
  - Borrar es inmediato y no tiene papelera (`app.js:159`).
  - El respaldo depende de una sola sesión fija por tarea programada (`LEEME.md:196`), y nada avisa si no corrió.
- **Propuesta:**
  - Borrado lógico (`borrado: fecha`).
  - Respaldo de todas las colecciones y de los assets referenciados.
  - Que la página muestre "último respaldo: DD-MM-AAAA" leyendo un doc `config/respaldo` que escribe la tarea, con alarma si pasan más de 9 días (ya existe para los índices: `app.js:42-45`).

#### M3. La página publica costos internos aunque el código dice que no
- **Evidencia:**
  - `web/construir_datos.py:5` dice "No incluye sueldos ni costos internos de planta … (la página puede compartirse)".
  - Pero `datos.json.tarifas` trae "Soldador (costo empresa por operario) 61,16 USD/hh", ingeniería 15,40 USD/hh y otros, y 15 servicios con hh o costo propio.
  - También publica 3.298 precios con proveedor, 505 rutas `Z:\…`, 912 clientes y las planillas de costo.
  - Quien recibe la página compartida ve todo y lo puede bajar entero (`datos.json`, 4 MB).
- **Propuesta:** corregir el comentario (no engañar al que comparta). Si se va a compartir con alguien de afuera de ventas, separar `datos.json` en público y costos, o compartir solo con edición controlada. Esto está dentro de la regla "repo privado, no omitir", pero la página no es el repo.

#### M4. La operación depende de un LLM siguiendo texto
- **Evidencia:**
  - La tarea semanal (`LEEME.md:198-204`) son 6 pasos manuales con ArtifactData y publicación, ejecutados por una sesión.
  - La publicación de la página no tiene script ni control previo (prueba de humo).
  - Varias sesiones hacen push a `main` (hay merges, por ejemplo `37bcaf5`) con archivos generados grandes (`datos.json` 4 MB, xlsx, docx, pdf, `informe.html` con xlsx en base64). `.git` pesa 153 MB.
  - Lección 43: el propio control tuvo que aprender a "restaurar derivados".
- **Propuesta:**
  - Un script `web/publicar.py` que haga `construir_datos`, `armar_pagina`, `node probar_*` y la comprobación de que `datos.json` es más nuevo que los CSV. Que la sesión solo ejecute el script y suba el resultado.
  - Dejar de versionar los derivados binarios (o moverlos a releases o LFS) y regenerarlos.
  - Una sola rama de trabajo por sesión, con merge.

#### M5. `armar_cotizacion.py` verifica después de escribir
- **Evidencia:** `armar_cotizacion.py:349-365`. Escribe `computo.csv`, el xlsx y el `informe.html`, y **recién después** compara Python con la planilla y corre `verificar_computo`. Si falla, sale con error, pero los entregables nuevos (posiblemente incorrectos) quedan en la carpeta junto a ofertas viejas.
- **Propuesta:** generar en un directorio temporal y mover a la carpeta solo si todos los controles pasan.

#### M6. El informe HTML es editable y guarda en `localStorage`
- **Evidencia:** `plantillas/informe_cotizacion.html:292-294`. Los cambios de cantidad, precio y parámetros se guardan con la clave `codigo:huella` y reaparecen al reabrir el mismo informe.
- **Impacto:** un informe abierto puede mostrar números distintos a la planilla, en contra de la regla "Excel e informe tienen que dar igual".
- **Propuesta:** banda visible "números modificados localmente: no válidos para la oferta" y botón de reinicio en el encabezado. O bien: que el modo edición sea opcional y no se guarde.

#### M7. Chat: inyección de instrucciones y catálogo sin revisión
- **Evidencia:**
  - Las reglas van como mensaje `user` (`asistente.js:645`), mezcladas con el contexto: ítems, proveedores y textos del catálogo y de los PDF, sin delimitar.
  - `nuevo_en_catalogo` (`asistente.js:528-559`) suma precios al buscador de todos **al instante** (`mezclarNuevos`, `asistente.js:44-52`), sin revisión humana, hasta que la tarea los incorpora.
- **Propuesta:**
  - Si `sample` lo permite, pasar las reglas como system. Si no, delimitar el contexto como datos.
  - Que los "nuevos" aparezcan en el buscador marcados como "sin revisar" y no como "igual". Revisarlos antes de incorporarlos.

### BAJO

- **Legibilidad:**
  - `app.js` tiene 84 líneas de más de 200 caracteres (máx. 504), `asistente.js` 76 (máx. 826) y `documentos.js` 26. HTML en template strings con lógica adentro.
  - `window.ITT` expone todo el estado (`app.js:827`), y asistente y app quedan muy acoplados.
  - Los archivos Python están bien (≤ 750 líneas, docstrings útiles y nombres claros en español).
- **Dependencias:** `requirements.txt` sin versiones fijas. `setup.sh` no instala LibreOffice (`soffice`, necesario en `armar_cotizacion.py:260`) ni Node. Las librerías del CDN tienen versión fija (bien) pero no SRI.
- **Fechas:** `antecedentes[].fecha` de la CAPEX se guarda en DD-MM-AAAA (y hay una `"10–11-06-2026"`), en contra de la regla "adentro AAAA-MM-DD".
- **Dólar mensual:** promedio por días corridos, con fines de semana que repiten el viernes (`dolar_diario.csv`, 24 y 25-10). Sesgo chico; conviene usar días hábiles.
- **Rendimiento:** `datos.json` pesa 4 MB, de los cuales 1,7 MB son las dos plantillas docx en base64, casi idénticas (`docx_tecnica`, `docx_economica`). Compartir la base o cargarla solo al descargar. La búsqueda sobre 3.300 registros con espera de 200 ms anda bien.
- **`numeros.leer_numero`:** "4.500" siempre se lee como miles, sin marca de ambiguo (`numeros.py:41-43`). La coma sí se marca. `fecha_iso` depende de `date.today()`, así que los tests dependen del reloj.

---

## Tests: qué hay y qué falta

**Hay:**
- `test_catalogo.py`: números, fechas y clasificación.
- `test_catalogo_servicios.py`.
- `test_precotizar.py`: la CAPEX.
- Determinismo de los catálogos.
- El armado de la CAPEX con Python contra LibreOffice y el precio de control (`verificar_todo.py`).
- `probar_motor.js`: 1 caso. `probar_busqueda.js`: 6 controles.

**Faltan (por prioridad):**
1. `node web/probar_*.js` dentro de `verificar_todo.py`.
2. Paridad con varios casos Python ↔ JS ↔ informe (fechas límite, grupos, AJ/TRANS/N, redondeo .005).
3. Validación de esquema de `cotizacion.json` y `oferta.json` (con tests de datos malos: grupo, NaN, fechas).
4. Excel de la página recalculado con LibreOffice contra `Motor.calcular`.
5. Paridad de `antecedentes.js` con `buscar_antecedentes.py`, y de `busqueda.js` con `buscar_material.py`. Hoy es una afirmación manual en `LEEME.md:12`.
6. Soldadura: el mismo resultado en `precotizar.py` y `busqueda.js`.
7. Concurrencia de guardado (simular un cambio externo con cambios pendientes).
8. Transiciones de estado: no se puede aprobar sin revisado ni con avisos `bad`.
9. `datos.json` al día respecto de los CSV, y `cotizador.html` igual a `src/`.
10. `respaldo_base.py` y `semilla.py`: ida y vuelta sin pérdida.
11. Que el caso de control no dependa de índices que cambian (índices congelados).

---

## Mejoras priorizadas

1. **Bloquear la aprobación en la página** con controles, quién revisa y quién aprueba, y **congelar la instantánea emitida** (C1).
2. **Congelar los índices por cotización** y desacoplar el caso de control de los índices vivos. Hacerlo antes del lunes 02-11 o la tarea semanal falla (A1).
3. **Esquema compartido y validación** en Python y JS. Fechas sin `hoy()` por defecto, fecha de tarifa válida y aviso cuando falta el factor de soldadura (A2, A5).
4. **`verificar_todo.py` corre los tests JS** más una paridad con varios casos y el Excel de la página con LibreOffice (A2).
5. **Guardado con `if_version`**, batch y versión de conflicto, sin pisar a Claude Code (A3).
6. **pdf.js ≥ 4.2.67, SheetJS actual y SRI.** Sesión destino fija en código y pedidos `otro` con confirmación. Push de la sesión de pedidos a una rama (A4).
7. **Factores y ajuste desde el chat con confirmación.** Catálogo nuevo marcado "sin revisar" (A5, M7).
8. **Respaldo completo, borrado lógico e indicador de último respaldo** en la página (M2).
9. **Script único de publicación** (`web/publicar.py`) y dejar de versionar los derivados binarios (M4).
10. Una sola dueña por cotización (repo o página), ids normalizados y control de divergencia (M1).
11. Generar los entregables en un temporal y moverlos solo si los controles pasan (M5). Informe sin estado persistente engañoso (M6).
12. Corregir el comentario de `construir_datos.py` sobre costos internos y decidir qué se comparte (M3).
13. Limpieza: separar las plantillas de HTML en `app.js`/`asistente.js`, fijar versiones en `requirements.txt` y documentar LibreOffice y Node en `setup.sh`.
