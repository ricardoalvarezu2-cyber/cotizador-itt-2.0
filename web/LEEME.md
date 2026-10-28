# Página del cotizador (Artifact en Claude)

- **Dirección:** https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ (privada: solo la ve Matías y a quien él la comparta desde el menú Compartir).
- Publicada el 28/10/2026. Capacidades: `db` (base de cotizaciones), `downloads` (descargas), `assets` (archivos: firma, plano, pedidos), `sample` con imágenes (chat con Claude, con la cuenta de quien lo usa) y `mcp` con el conector **Claude Code Remote** (`send_message`, para mandar pedidos a la sesión fija).
- Sin usuarios ni registro de resultados (decisión de Matías). Los firmantes se cargan en la pestaña Firmantes; la imagen de la firma solo va en las ofertas aprobadas.

## Qué hay en esta carpeta
| Archivo | Para qué |
|---|---|
| `src/motor.js` | Cálculo de costo y precio, igual a `herramientas/armar_cotizacion.py` (control: CAPEX = USD 7.620,59). Prueba: `node web/probar_motor.js`. |
| `src/busqueda.js` | Buscador de materiales y servicios (igual / similar), calculadora de soldaduras y avisos de control. Prueba: `node web/probar_busqueda.js`. |
| `src/antecedentes.js` | Comparación con antecedentes (P8) en Resumen: misma puntuación que `buscar_antecedentes.py` y misma lectura que `comparar_antecedentes.py` (CAPEX: mismos 5 y mismo aviso). Datos: `datos.json` → `antecedentes`. |
| `src/documentos.js` | Planilla de presupuesto (con fórmulas), lista para Compras, informe PDF, ofertas técnica y económica (Word con la plantilla ITT y PDF). |
| `src/app.js`, `src/pagina.html` | Interfaz. Estética de los informes de ITT. |
| `src/asistente.js` | Chat con Claude (herramientas: buscar, agregar, cargar, modificar y quitar ítems, ver avisos, nueva cotización, proponer pedido; lee imágenes y PDF como imágenes; deshacer) y sección **Pedidos** (subir archivos y mandarlos a Claude Code). |
| `construir_datos.py` → `datos.json` | Catálogos, índices, tarifas, tablas técnicas, clientes y plantillas de oferta para la página. |
| `armar_pagina.py` → `cotizador.html` | Junta todo en una sola página para publicar. |
| `semilla.py` → `semilla.json` | Carga una cotización de `cotizaciones/` en la base de la página. |
| `indices_para_pagina.py` | Documento `config/indices` de la base (dólar e índices al día) para la tarea semanal. |
| `respaldo_base.py` | Copia las cotizaciones de la base de la página a `cotizaciones_web/` (respaldo en GitHub). |

## Base de datos de la página
- `cotizaciones/<id>`: `{cot, oferta, creado, guardado}`. `cot.transcripcion` (si existe `pedido/transcripcion.json`) es la lista tal cual el documento de origen y `cot.kg_compras` los kg por unidad de cada posición: los usa el Excel para Compras (los pone `semilla.py`). `cot` tiene el formato de `cotizacion.json` más `firmante_id` y, en cada material, `plano` (diámetro, serie, material, extremos del plano). `oferta` tiene el formato de `oferta.json`.
- `cotizaciones/<id>/versiones/<marca>`: copia cada 10 minutos de trabajo y en cada cambio de estado (se guardan las últimas 20).
- `resumenes/<id>`: lo que muestra la lista (código, título, cliente, estado, unitario, total).
- `firmantes/<id>`: nombre, cargo, teléfono, celular, email, `firma_asset` y `firma_url`.
- `config/indices`: `{generado, indices, dolar}`. Si es más nuevo que `datos.json`, la página lo usa.
- `cot.indices_congelados` (en cada cotización): `{fecha, filas}` con el mismo formato que `datos.json.indices`. Se guarda al pasar a revisado y se borra al volver a borrador; si está, el cálculo usa esos índices y no los de la base. `cot.aprobacion`: `{por, fecha}`. `cot.parametros.FTV`: factor de todas las válvulas Taval (por defecto 1); cada válvula Taval lleva `"taval": true`.
- `catalogo_nuevo/<N-MAT-… o N-SRV-…>`: `{clase, registro (mismo formato que datos.json), original: {precio, moneda, iva, documento}, creado, por, incorporado?}`. Lo carga el chat (`nuevo_en_catalogo`); la página lo suma al buscador mientras no esté `incorporado`.
- `config/claude_code`: `{session_id}` de la sesión que recibe los pedidos (si no existe, la página usa la sesión fija de abajo).
- `pedidos/<id>`: `{tipo, texto, cotizacion_id, archivos: [{id, url, nombre, tipo, original?}], estado, nota, respuesta, resultado_cotizacion_id, creado, enviado, historial: [{fecha, estado, nota}]}`. Tipos: `cotizacion_nueva`, `actualizar_cotizacion`, `lista_precios`, `otro`. Estados: `pendiente` → `enviado` → `en_proceso` → `listo` / `con_dudas` (o `error` si no se sabe si el envío llegó).
- Si Claude Code guarda una cotización con `"editor": "claude-code"`, la página abierta la recarga sola y avisa.
- La página guarda sola 1,2 segundos después de cada cambio.

## Tarea semanal (lunes a la mañana)
Tarea programada `trig_01FE1sHFbntc3vsLmKVYvvcD` (lunes 7:37, hora Argentina). Despierta la sesión fija "Cotizador ITT – tarea semanal" (`session_01Y6ZcPeLckws2e9s2DF8RJ3`), que tiene el repositorio adjunto. Una tarea que abre sesiones nuevas no sirve: esas sesiones no tienen acceso al repositorio (probado el 28/10/2026). Si la sesión fija se archiva, hay que crear otra con el repositorio y apuntar la tarea a ella.

1. `python herramientas/actualizar_base.py` (dólar BNA, índices, catálogos). Si falta el IPC o el CPI de un mes nuevo, buscar el dato oficial (INDEC / BLS), sumarlo en `herramientas/indices_inflacion.py` con su fuente y volver a correr. Tiene que terminar en "TODO OK".
2. `python web/indices_para_pagina.py <scratch>/indices.json` y subirlo con ArtifactData: `set`, collection `config`, doc_id `indices`, `file_path` (si ya existe, leerlo antes para pasar `if_version`).
3. Respaldo: ArtifactData `list` de `cotizaciones` con `out_dir` y `python web/respaldo_base.py <out_dir>/cotizaciones`. Las aprobadas o enviadas (y las que tienen `cot.base`) entran solas a la base al correr `actualizar_base.py` (ver `herramientas/cotizaciones_base.py`).
4. Si cambiaron los catálogos: `python web/construir_datos.py && python web/armar_pagina.py` y republicar la página (Artifact, `url` de arriba, `files: {"datos.json": "web/datos.json"}`; leerla antes con `action: read`).
5. Pedidos `pendiente` de la colección `pedidos`: procesarlos como dice "Pedidos desde la página".
5b. Artículos y servicios nuevos cargados en la página (colección `catalogo_nuevo`, sin `incorporado`): materiales a `conocimiento/precios/listas_nuevas.csv` (precio y moneda de `original`, `iva` de `original.iva`, `tipo_precio` del registro, `archivo_origen` = documento, `pedido` = código N-MAT-…), servicios a `servicios_extraidos.csv`. Volver a correr `actualizar_base.py`, `construir_datos.py`, `armar_pagina.py`, republicar, y recién después marcar cada documento con `incorporado: <fecha>` (ArtifactData `update`).
6. Commit y push a `main`.

## Pedidos desde la página
Llegan a la sesión fija como un mensaje "Pedido <id> desde la página del cotizador…" (botón "Mandar a Claude Code" o el chat), o quedan `pendiente` y se procesan el lunes. Procesar uno por vez:
1. ArtifactData `get` de `pedidos/<id>` (url de la página, arriba). `update` con `if_version`: `estado: "en_proceso"`, `nota`, y una entrada más en `historial`.
2. Bajar cada archivo con Artifact `action: "read"`, `url` de la página y `path` = `archivos[].id`. Guardar la copia en `fuentes_originales/pedidos_web/<id>/<nombre>` (todo queda en el repositorio). Excel y Word llegan convertidos a Markdown (`original` = nombre del archivo original); en el Excel convertido el punto es decimal.
3. Según el `tipo`:
   - `cotizacion_nueva`: skill `cotizar` completo (carpeta nueva en `cotizaciones/`, P1–P10, `precotizar.py`, `armar_cotizacion.py`, `verificar_computo.py`). Después `python web/semilla.py cotizaciones/<carpeta> <id_pagina> --salida <scratch>` (id_pagina: `c` + código en minúsculas, ej. `c26-1003-001`) y ArtifactData `batch` de `set` con esos dos archivos (si ya existen, leerlos y pasar `if_version`).
   - `actualizar_cotizacion`: si está en el repositorio (`cotizaciones/<carpeta>` con el mismo código), trabajar ahí y volver a cargarla con `semilla.py --salida`; si no, bajar `cotizaciones/<cotizacion_id>` con ArtifactData, corregir el JSON con las mismas reglas, poner `"editor": "claude-code"` y `"guardado"` = ahora, y `set` con `if_version` (y `resumenes/<id>` con los totales de `web/src/motor.js`). En `respuesta`, decir qué se cambió.
   - `lista_precios`: materiales a `conocimiento/precios/listas_nuevas.csv` (`fecha,proveedor,descripcion,precio,moneda,unidad,iva,tipo_precio,archivo_origen,ruta_repo,pedido,nota`; precio y moneda tal como dice el documento; `iva` con lo que dice el documento: el catálogo divide si es con IVA; `tipo_precio` lista o cotización; `ruta_repo` = la copia en `fuentes_originales/pedidos_web/`). MO y servicios a `conocimiento/precios/servicios_extraidos.csv` con su formato. Después `python herramientas/actualizar_base.py` (TODO OK), `python web/construir_datos.py && python web/armar_pagina.py` y republicar la página (Artifact `read` primero, después publish con la misma `url` y `files: {"datos.json": "web/datos.json"}`).
   - `incorporar_base` (botón "Incorporar a la base de datos" en Resumen; deja `cot.base.pedida`): ArtifactData `get` de `cotizaciones/<cotizacion_id>` con `out_dir`, y `python web/respaldo_base.py <out_dir>/cotizaciones` (la copia a `cotizaciones_web/<id>/`). Revisar que no tenga precios absurdos ni piezas mal identificadas (si los hay, `con_dudas` y no seguir). Después `python herramientas/actualizar_base.py` (o `--sin-red` si falla la red; TODO OK): `herramientas/cotizaciones_base.py` hace que el catálogo tome sus precios con documento (cot/lista/ant, iguales a lo pedido, sin estimados ni precios sacados del propio catálogo) y que el índice de antecedentes la sume. `python web/construir_datos.py && python web/armar_pagina.py`, republicar con `files: {"datos.json": "web/datos.json"}`, y `update` de la cotización en la página con `cot.base.incorporada` = hoy (leerla antes, `if_version`, `editor: "claude-code"`). En `respuesta`: cuántos precios entraron al catálogo y que ya figura como antecedente.
   - `otro`: lo que pida, con las mismas reglas.
4. Cerrar el pedido: `update` con `estado: "listo"` o `"con_dudas"`, `respuesta` (2 a 4 líneas: qué se hizo, qué revisar, dudas), `resultado_cotizacion_id` si corresponde, y el `historial`.
5. `verificar_todo.py` (TODO OK), commit y push. Errores nuevos a `conocimiento/errores_y_lecciones.md`.
- Reglas: nunca enviar nada al cliente; todo queda en borrador; si algo no se lee bien, `con_dudas` y explicarlo. Un precio sin documento no se carga.

## Cambios en la página
Editar `src/`, correr `python web/armar_pagina.py`, probar (ver `probar_*.js`) y republicar el mismo `web/cotizador.html`.
