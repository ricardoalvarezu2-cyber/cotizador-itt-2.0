# Auditoría de automatizaciones (29-10-2026)

Alcance: herramientas encadenadas, scripts de `web/`, tarea semanal, pedidos de la página, botones de la página (Recalcular, Claude ↗, Chat nuevo, guardado y versiones) y configuración de `.claude/`.
Método: todo se corrió sobre una copia (`/tmp/audit_auto`); el repo original no se tocó salvo este informe. Con red disponible. Lo que solo existe en la página publicada (capacidades, ArtifactData, `mcp`) no se pudo ejecutar: se revisó el código.

## Resumen
- `verificar_todo.py` da TODO OK (22 s). `actualizar_base.py` y toda la cadena de Python corren sin error, con y sin `--sin-red`, y los resultados son idempotentes en datos.
- No hay fallas bloqueantes. Hay 2 hallazgos medios que pueden hacer perder o dañar datos (respaldo que se borra solo, guardado que pierde cambios tras un error) y varios menores.
- La tarea semanal nunca corrió sola todavía (primera vez: 02-11-2026). Está bien armada, pero su prompt no coincide con `web/LEEME.md` (le faltan los pasos 5 y 5b).

## Tabla de automatizaciones

| Automatización | Estado | Observación corta |
|---|---|---|
| `verificar_todo.py` | anda | TODO OK. Restaura solo los derivados que cambian por regenerarse (ver M3) |
| `actualizar_base.py` (con y sin `--sin-red`) | anda con observaciones | Sin red corta entero (B1); los .xlsx cambian de bytes en cada corrida (M3) |
| `dolar_mensual.py` | anda con observaciones | Con red baja y rearma bien. Sin red traceback y no escribe nada (correcto), pero no avisa claro |
| `indices_inflacion.py` | anda | Oct-2026 sigue ESTIMADO (IPC y CPI): lo completa la tarea semanal a mano |
| `catalogo_materiales.py`, `catalogo_servicios.py` | anda | Idempotentes (segunda corrida igual). No aceptan `--help`: lo ejecutan entero y escriben |
| `armar_cotizacion.py` | anda con observaciones | CAPEX: 7.366,12 unitario. Sin LibreOffice cae con traceback a mitad de camino (M2) |
| `precotizar.py` | anda | Idempotente (`cotizacion_auto.json` sin cambios). Carpeta inexistente: mensaje claro |
| `ficha_rubros.py` | anda con observaciones | Sin `--help`, carpeta mala da traceback |
| `plazo.py` | anda con observaciones | Igual que ficha_rubros; avisa bien que el plazo ofrecido no tiene margen |
| `comparar_antecedentes.py` | anda con observaciones | Igual; CAPEX: 5 comparados y aviso -51% |
| `verificar_computo.py` | anda con observaciones | Lee `computo.csv`, no `cotizacion.json` (M4) |
| `buscar_antecedentes.py`, `buscar_material.py`, `buscar_servicio.py` | anda | Argumentos ok |
| `estimar_horas.py` | anda | Ok |
| `web/construir_datos.py` | anda | Determinístico salvo las plantillas Word embebidas (zip con fecha) |
| `web/armar_pagina.py` | anda | 256 kB, determinístico |
| `web/semilla.py` | anda | `<carpeta> <id> --salida <dir>` funciona como dice LEEME; sin `--salida` pisa `web/semilla.json` |
| `web/indices_para_pagina.py` | anda con observaciones | Sin argumento: IndexError (B2) |
| `web/respaldo_base.py` | falla en un caso | Con carpeta vacía o mal escrita vacía el README sin avisar (M1); fecha en AAAA-MM-DD (B3) |
| Tarea semanal (`trig_01FE1sHFbntc3vsLmKVYvvcD`) | no probada | Habilitada, próxima corrida 02-11-2026 07:37 ART. Prompt desfasado (M5) |
| Pedidos desde la página (LEEME) | anda con observaciones | Todos los scripts y argumentos que nombra existen y funcionan; falta verificar ArtifactData en la sesión fija |
| Botón Recalcular (`web/src/ficha.js`, `app.js:970`) | anda | `probar_ficha.js` y `probar_rubros.js`: OK, igual a Python en 9 y 15 cotizaciones |
| Botones Claude ↗ y Chat nuevo (`asistente.js`) | anda con observaciones | Código coherente con LEEME; no ejecutable acá (M6, B4) |
| Guardado automático y versiones (`app.js`) | anda con observaciones | M7, B5 |
| `.claude/` | anda con observaciones | Solo `skills/cotizar`; sin `settings.json` ni hooks (B6) |
| Pruebas JS (`probar_motor/busqueda/ficha/rubros`) | anda | Las cuatro dan OK (CAPEX 7.366,12) |

## Hallazgos

### Medios

**M1. `respaldo_base.py` borra la lista del README y no falla si la carpeta no existe o está vacía** (`web/respaldo_base.py:17-36`)
- Reproducir: `python web/respaldo_base.py /tmp/noexiste` termina con código 0, imprime "0 cotizaciones respaldadas" y deja el README sin filas (las carpetas de `cotizaciones_web/` no se borran, pero el registro y el aviso "ya no están en la página" se pierden o se arman mal).
- Riesgo: si el `list` de ArtifactData falla o `out_dir` sale mal, el lunes parece que el respaldo anduvo.
- Corrección: si no hay ningún `.json` con `cot`, salir con error (`sys.exit`) sin tocar el README.
- Relacionado: `cotizaciones_web/` tiene hoy solo `capex-oq8209`. Las otras 5 cotizaciones de la página existen en `cotizaciones/` pero lo que se editó en la página desde la carga (por ejemplo lo que completó Recalcular) está solo en la base hasta el primer lunes (02-11-2026). Con la regla de "no perder información", conviene correr un respaldo manual antes.

**M2. `armar_cotizacion.py` sin LibreOffice falla a mitad de camino** (`herramientas/armar_cotizacion.py:279-283`, `leer_planilla`)
- Reproducir: correr con un PATH sin `soffice`. Traceback `FileNotFoundError: 'soffice'`; la planilla ya quedó escrita, pero no se generan informe ni ofertas, y quedan los viejos de la corrida anterior (Excel e informe distintos).
- Corrección: chequear `shutil.which("soffice")` al principio y cortar con un mensaje claro antes de escribir nada; lo mismo en `generar_oferta.py:52` y `:338`.

**M3. Los binarios generados cambian de bytes en cada corrida, aunque los datos sean los mismos**
- Afecta: los .xlsx de catálogos y dólar, la planilla/compras/ofertas (.docx/.pdf) y `informe.html` (que lleva el Excel en base64) de cada cotización, y las plantillas Word dentro de `web/datos.json`.
- Reproducir: `python herramientas/actualizar_base.py --sin-red` dos veces y `git status`: 3 .xlsx modificados. `armar_cotizacion.py` sobre la CAPEX deja 7 archivos modificados sin cambio de datos.
- Efecto: ensucia el árbol de trabajo y los commits; `verificar_todo.py` lo compensa (`git checkout --` de los derivados) pero solo para sus propias corridas y solo si todo lo nuevo es "derivado".
- Corrección: fijar fechas del zip/xlsx (propiedades `created/modified` de openpyxl y `ZipInfo.date_time`), o no commitear los derivados que no cambian de contenido.

**M4. `verificar_computo.py` no detecta un `computo.csv` desactualizado** (`herramientas/verificar_computo.py:38-39`)
- Reproducir: cambiar una `cantidad` en `cotizacion.json` y correr `verificar_computo.py` solo: 0 errores. Compara el plano con `computo.csv`, que solo se regenera con `armar_cotizacion.py`.
- Efecto: en el flujo normal no pasa (armar lo corre después de generar), pero el paso "antes de pasar a revisado" de CLAUDE.md puede dar un OK falso si alguien editó el JSON y no rearmó.
- Corrección: comparar fecha de modificación de `cotizacion.json` contra `computo.csv` y fallar si el JSON es más nuevo, o regenerar el cómputo en memoria.

**M5. El prompt de la tarea semanal no coincide con `web/LEEME.md`**
- Fuente: `get_trigger` de `trig_01FE1sHFbntc3vsLmKVYvvcD`. El prompt tiene 5 pasos; LEEME tiene 6 y el 5b. Faltan: procesar pedidos `pendiente` (paso 5, incluidos los `incorporar_base`) e incorporar `catalogo_nuevo` (5b). Hoy la página manda `incorporar_base` y los pedidos pueden quedar `pendiente` si el envío falla, y los artículos nuevos de `catalogo_nuevo` no entran nunca al repo.
- También: el prompt dice "Commit y push a main" pero no pide `verificar_todo` al final (lo hace `actualizar_base` en el paso 1, ok), y la sesión fija corre sin conector propio visible (`mcp_connections: []`); el lunes 28-10 mencionó haber revisado pedidos, así que ArtifactData parece disponible, pero no se pudo confirmar.
- Corrección: `update_trigger` con el prompt "seguí la sección Tarea semanal de web/LEEME.md completa (pasos 1 a 6)" en lugar de copiar los pasos; así no se desfasa.

**M6. Chat nuevo: se archiva una sesión consolidada aunque se haya seguido usando** (`web/src/asistente.js:198-200`)
- Reproducir (por lectura): una sesión con `consolidado` ya marcado se archiva en el próximo clic de "Claude ↗" o "Chat nuevo" si no está RUNNING, sin mirar `updated_at`. Si Matías la reabre y la usa después de consolidar, la siguiente limpieza la archiva sin una nueva consolidación.
- Efecto: el trabajo posterior a la consolidación puede quedar sin anotar. La sesión se recupera desde claude.ai/code.
- Corrección: archivar solo si `Date.parse(x.updated_at) <= Date.parse(c.consolidado) + margen`; si la sesión se movió después, volver a pedir consolidar (borrar `consolidado`/`consolidar_pedido`).

**M7. El guardado automático pierde cambios tras un error de red** (`web/src/app.js:60-77`, `111`, `123`)
- `guardar()` pone `S.pendiente = false` antes de guardar. Si el `set` falla, se reprograma a 5 s, pero `S.pendiente` ya es false: `beforeunload` (`:111`) y la navegación (`abrir`, `:122`, `if (S.pendiente) await guardar()`) no intentan guardar.
- Reproducir: cortar la red, editar, volver a la lista antes de los 5 s: los cambios se pierden (el reintento corre contra `S.doc` ya reemplazado).
- Corrección: poner `S.pendiente = true` en el `catch` y limpiarlo solo al terminar bien.

### Bajos

**B1. Sin red, `actualizar_base.py` corta entero** (`herramientas/actualizar_base.py:17-23`, `herramientas/dolar_mensual.py:50`). Con `HTTPS_PROXY` roto: traceback de `urllib` y "se corta la actualización", sin probar `--sin-red`. Es seguro (no escribe nada) pero la tarea semanal queda detenida. Corrección: capturar `URLError` en `dolar_mensual.py`, avisar "sin red: se usa la copia del repo (último dato DD-MM-AAAA)" y seguir con `--sin-red`, dejando el aviso en el resumen de la tarea.

**B2. `indices_para_pagina.py` sin argumento** (`web/indices_para_pagina.py:14`). `IndexError`. Pedir el argumento con mensaje de uso.

**B3. Fechas en AAAA-MM-DD en textos a la vista** (`web/respaldo_base.py:33` y la columna "guardado" `:29`). CLAUDE.md pide DD-MM-AAAA a la vista; usar `numeros.a_vista`.

**B4. La limpieza de chats solo corre al tocar los botones** (`web/src/asistente.js:150`, `:157`). LEEME lo dice así ("Al tocar…"), pero "se archivan solas" en otros textos es exagerado: si no se usa la página, no se limpia nada.

**B5. Versiones: guardan el estado posterior al cambio, no el anterior** (`web/src/app.js:72`, `:171`). La versión se toma después del guardado que cruza los 10 minutos o un cambio de estado (`S.ultVersion = 0`). No hay copia del estado previo a la primera edición de la sesión. LEEME dice "en cada cambio de estado": se cumple, pero tras el cambio. Corrección: versionar el documento que se leyó al abrir (primer guardado de la sesión) antes de sobrescribir.

**B6. Sin hooks ni `settings.json` en `.claude/`.** Nada impide por configuración enviar mails o escribir fuera de `main`; las reglas dependen de CLAUDE.md. No hay `SessionStart` que instale dependencias. En este entorno faltan `pymupdf`, `extract_msg`, `ezdxf`, `ezdwg`, `matplotlib`, `huggingface_hub`: fallan `extraer_texto.py`, `leer_dwg.py`, `verificar.py` (no están en la cadena de cotización ni en `verificar_todo`, pero sí en el flujo de pedidos con planos o mails). `setup.sh` arma un `.venv` que ningún comando usa (todos llaman `python`). Corrección: hook `SessionStart` con `pip install -r requirements.txt` (solo lo que falte) o un `setup` para la sesión fija.

**B7. Sin `--help` ni validación de argumentos** en `armar_cotizacion.py`, `ficha_rubros.py`, `plazo.py`, `comparar_antecedentes.py`, `verificar_computo.py` (tratan `--help` como carpeta y dan traceback). Y en `actualizar_base.py`, `dolar_mensual.py`, `indices_inflacion.py`, `catalogo_*.py`, `--help` ejecuta el proceso completo y escribe archivos. Corrección: `argparse` mínimo.

**B8. `indice_precios.csv` del repo estaba desactualizado** respecto de sus fuentes (al rearmar cambian 14 líneas, por ejemplo las juntas de MS Juntas separadas en 3 renglones). Quedó sin regenerar en el último commit. Correr `actualizar_base.py` antes de commitear (ya figura en el procedimiento).

**B9. Texto desactualizado en `web/LEEME.md:10`**: dice "control: CAPEX = USD 7.620,59"; el control vigente es 7.366,12 (así lo da `probar_motor.js`, y `estado_y_pendientes.md` lo registra). Corregir el LEEME.

## Qué se verificó y está bien
- Todos los scripts y argumentos que nombran CLAUDE.md, el skill `cotizar` y `web/LEEME.md` existen (el "web/datos.js" que sale en un grep es `datos.json`).
- `semilla.py` acepta `<carpeta> <id> --salida <dir>` y genera `cotizaciones__<id>.json` y `resumenes__<id>.json` (7.366,12 unitario / 14.732,24 total).
- `precotizar.py` y `armar_cotizacion.py` son idempotentes en datos; `catalogo_*` dan la misma salida en la segunda corrida; `construir_datos.py`/`armar_pagina.py` dan el mismo resultado en dos corridas.
- El botón Recalcular usa `Ficha.completarAtributos` y `Rubros.ficha`, guarda solo si completó algo y su resultado coincide con Python en las pruebas.
- Guardado: 1,2 s después del cambio, versión cada 10 minutos (últimas 20), cola si ya hay un guardado en curso, y recarga si Claude Code guarda con `editor: "claude-code"`.

## No probado
- Ejecución real de la tarea semanal, de ArtifactData y de la capacidad `mcp` (`create_session`, `get_session`, `archive_session`, `send_message`) y el manifiesto de la página publicada.
- Apertura de la ventana emergente de "Claude ↗" dentro del iframe de la página.
- Descarga del RAR de la Tanda 1 desde Google Drive.
