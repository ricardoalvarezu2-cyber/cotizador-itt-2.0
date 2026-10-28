# Página del cotizador (Artifact en Claude)

- **Dirección:** https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ (privada: solo la ve Matías y a quien él la comparta desde el menú Compartir).
- Publicada el 28/10/2026. Capacidades: `db` (base de cotizaciones), `downloads` (descargas), `assets` (imágenes de firma y plano).
- Sin usuarios ni registro de resultados (decisión de Matías). Los firmantes se cargan en la pestaña Firmantes; la imagen de la firma solo va en las ofertas aprobadas.

## Qué hay en esta carpeta
| Archivo | Para qué |
|---|---|
| `src/motor.js` | Cálculo de costo y precio, igual a `herramientas/armar_cotizacion.py` (control: CAPEX = USD 7.620,59). Prueba: `node web/probar_motor.js`. |
| `src/busqueda.js` | Buscador de materiales y servicios (igual / similar), calculadora de soldaduras y avisos de control. Prueba: `node web/probar_busqueda.js`. |
| `src/documentos.js` | Planilla de presupuesto (con fórmulas), lista para Compras, informe PDF, ofertas técnica y económica (Word con la plantilla ITT y PDF). |
| `src/app.js`, `src/pagina.html` | Interfaz. Estética de los informes de ITT. |
| `construir_datos.py` → `datos.json` | Catálogos, índices, tarifas, tablas técnicas, clientes y plantillas de oferta para la página. |
| `armar_pagina.py` → `cotizador.html` | Junta todo en una sola página para publicar. |
| `semilla.py` → `semilla.json` | Carga una cotización de `cotizaciones/` en la base de la página. |
| `indices_para_pagina.py` | Documento `config/indices` de la base (dólar e índices al día) para la tarea semanal. |
| `respaldo_base.py` | Copia las cotizaciones de la base de la página a `cotizaciones_web/` (respaldo en GitHub). |

## Base de datos de la página
- `cotizaciones/<id>`: `{cot, oferta, creado, guardado}`. `cot` tiene el formato de `cotizacion.json` más `firmante_id` y, en cada material, `plano` (diámetro, serie, material, extremos del plano). `oferta` tiene el formato de `oferta.json`.
- `cotizaciones/<id>/versiones/<marca>`: copia cada 10 minutos de trabajo y en cada cambio de estado (se guardan las últimas 20).
- `resumenes/<id>`: lo que muestra la lista (código, título, cliente, estado, unitario, total).
- `firmantes/<id>`: nombre, cargo, teléfono, celular, email, `firma_asset` y `firma_url`.
- `config/indices`: `{generado, indices, dolar}`. Si es más nuevo que `datos.json`, la página lo usa.
- La página guarda sola 1,2 segundos después de cada cambio.

## Tarea semanal (lunes a la mañana)
Tarea programada `trig_01FE1sHFbntc3vsLmKVYvvcD` (lunes 7:37, hora Argentina). Despierta la sesión fija "Cotizador ITT – tarea semanal" (`session_01Y6ZcPeLckws2e9s2DF8RJ3`), que tiene el repositorio adjunto. Una tarea que abre sesiones nuevas no sirve: esas sesiones no tienen acceso al repositorio (probado el 28/10/2026). Si la sesión fija se archiva, hay que crear otra con el repositorio y apuntar la tarea a ella.

1. `python herramientas/actualizar_base.py` (dólar BNA, índices, catálogos). Si falta el IPC o el CPI de un mes nuevo, buscar el dato oficial (INDEC / BLS), sumarlo en `herramientas/indices_inflacion.py` con su fuente y volver a correr. Tiene que terminar en "TODO OK".
2. `python web/indices_para_pagina.py <scratch>/indices.json` y subirlo con ArtifactData: `set`, collection `config`, doc_id `indices`, `file_path` (si ya existe, leerlo antes para pasar `if_version`).
3. Respaldo: ArtifactData `list` de `cotizaciones` con `out_dir` y `python web/respaldo_base.py <out_dir>/cotizaciones`.
4. Si cambiaron los catálogos: `python web/construir_datos.py && python web/armar_pagina.py` y republicar la página (Artifact, `url` de arriba, `files: {"datos.json": "web/datos.json"}`; leerla antes con `action: read`).
5. Commit y push a `main`.

## Cambios en la página
Editar `src/`, correr `python web/armar_pagina.py`, probar (ver `probar_*.js`) y republicar el mismo `web/cotizador.html`.
