---
name: cotizar
description: Cotizar un pedido de cliente de ITT (puentes, skids, manifolds, colectores, piping, separadores, filtros, tanques, trampas) desde el pedido y el plano hasta la oferta técnica y económica, siguiendo el procedimiento obligatorio de ITT. Usar cuando Matías pase un pedido de cotización, un plano o una lista de materiales, o pida actualizar, revisar o pasar a oferta una cotización existente.
---

# Cotizar un pedido de ITT

Leé primero `conocimiento/estado_y_pendientes.md`. Seguí **en orden** `conocimiento/guia_cotizacion.md`, respetando las reglas de `conocimiento/procedimiento_cotizacion.md` (P1–P10). Antes de empezar, leé `conocimiento/errores_y_lecciones.md`: ahí están los errores que ya se cometieron. El caso modelo es `cotizaciones/COT26-1003-001_CAPEX_OQ8209/` (leé su `bitacora.md` y su `cotizacion.json`).

## Flujo

**Flujo unificado (30-10-2026):** tabla de 13 pasos y frenos en `conocimiento/procedimiento_cotizacion.md` ("Flujo unificado"). Además de lo de abajo: `pedido/requisitos.csv` (matriz de requisitos con destino) y las consultas al cliente el primer día; **doble lectura** del documento del cliente (`transcripcion.json` y `transcripcion_b.json`, dos agentes que no se ven entre sí, comparadas con `python herramientas/frenos.py --comparar`); las ofertas no salen con frenos abiertos (`python herramientas/frenos.py cotizaciones/<carpeta>`).

1. **Carpeta:** copiar `cotizaciones/_plantilla/` a `cotizaciones/COT[AA]-[CCCC]-[NNN]_<CLIENTE>_<PEDIDO>/`. El código del cliente está en `conocimiento/comercial/clientes.csv`. Guardar los originales en `pedido/` y anotar la cotización en `cotizaciones/README.md`.
2. **Plano → `pedido/transcripcion.json` (copia textual) y `pedido/lista_materiales_plano.csv`:** la tabla completa, renglón por renglón, con todas las columnas. **REGLA CRÍTICA — descripción del cliente (Matías, 29-10-2026):** en la descripción va siempre, sin excepción, el texto exacto del documento del cliente (plano, pliego o planilla), tal cual figura: sin corregir, traducir, abreviar ni agregar palabras ("RF", "radio largo", marcas, normas). Lo mismo con el material: se cotiza lo que pide el cliente. Lo que agrega ITT va en la columna `nota` de `lista_materiales_plano.csv`; el Ø va aparte. Si el cliente no indica cantidad y ITT la calcula, se aclara siempre en `cantidad_origen` ("El cliente no indica cantidad: calculada por ITT según el plano / la ET") y la oferta la marca con (*). Se copia de `pedido/transcripcion.json` y `verificar_computo.py` da error si no coincide. Mirar el dibujo para ver qué extremos BW se sueldan en taller y cuáles en campo.
3. **Precotización automática:** `python herramientas/precotizar.py cotizaciones/<carpeta> --comparar` (sin IA). Revisar solo lo que marca `precotizacion.md` y usar `cotizacion_auto.json` como punto de partida. Cargar `extremos_campo` en la tabla del plano y `ph_horas` / `rx_pct` en los parámetros. Las horas de ingeniería, calidad y montaje salen estimadas del antecedente más parecido (`herramientas/estimar_horas.py`; se puede fijar `equipo.tipo` y `equipo.diametro_pulg` en `cotizacion.json`).
3 bis. **Antecedentes y precios:** correr primero `python herramientas/buscar_antecedentes.py --cotizacion cotizaciones/<carpeta>` (o `--texto "..." --cuerpo --diametro --serie --material --union --cliente`; familia y subtipo se deducen del texto) y revisar los 3–5 primeros (si hay pocos del mismo subtipo, mirar también las carpetas anteriores sin ficha que muestra aparte), priorizando los que tienen **planilla de costo** y los más nuevos. Usar como modelo la planilla de costo de la oferta más parecida. Para cada material sin precio en los antecedentes: `python herramientas/buscar_material.py "<descripción con Ø, serie, material, extremos>"` (igual primero; un similar va con `coincide: similar` y su diferencia). Para cada precio, **abrir el documento original**, comparar la especificación con el plano campo por campo y anotar proveedor, carpeta y fecha. Un dato verbal o por WhatsApp va como `est`. Cada fuente de base se marca `coincide`: `igual`, `similar` (con `diferencia`) o `sin_ref`.
4. **`cotizacion.json`:** un ítem por posición del plano, con la misma cantidad y unidad; las compras extra en filas `14b`. Cargar todas las fuentes de cada ítem (la primera es la de base). Las soldaduras van junta por junta. Factores 1,35 / 1,35, contingencia 5%, `AJ: 1`, `fecha_referencia` = hoy.
5. **Armar:** `python herramientas/armar_cotizacion.py cotizaciones/<carpeta>`. Tiene que terminar sin error: Python y planilla iguales, `verificar_computo.py` sin errores.
6. **Revisar los avisos** uno por uno y contrastar con 2 antecedentes. Si la diferencia es mayor al 15%, explicarla antes de mostrar el número.
7. **Revisión independiente:** lanzar un subagente que **no** armó el cómputo para comparar plano contra cómputo, informe y planilla. Corregir o justificar lo que encuentre.
7 bis. **Preliminar → Compras → definitivo:** el preliminar (con piezas similares) se presenta con la lista para Compras. Matías no compra. Cuando llegan las respuestas se cargan como fuente de base `cot` / `igual` y se vuelve a armar.
8. **Presentar a Matías:** siempre como "borrador, sin revisar" hasta que esté revisado. Publicar `informe.html` con la herramienta Artifact y mandar la planilla y las ofertas con SendUserFile.
9. **Registrar:** actualizar `bitacora.md`, `cotizaciones/README.md` y `errores_y_lecciones.md` si hubo errores. Después, commit y push.

## Datos que se usan siempre igual
- Precios **sin IVA**; pesos a dólares con el **promedio mensual del oficial BNA venta** (`conocimiento/costos/dolar_mensual.csv`), salvo que el documento diga su tipo de cambio.
- Materiales: `buscar_material.py` (columna `alerta`: revisar antes de usar). Marcas del cliente: `comercial/marcas_aprobadas.csv`. Plazos de proveedores: `comercial/plazos_proveedores.csv` (para el camino crítico, el máximo del rubro si es "stock salvo venta"). Kg y m²: `controles_tablas.peso_item` (caños, bridas, accesorios base y complemento, olets, espárragos, válvulas; sin tabla, APROXIMADO por `peso_aproximado.py`). Ficha por rubro (MO del skid y del piping, pintura, END, procedimientos, PH, horas, transporte): `ficha_rubros.py`, que corre `armar_cotizacion.py`. MO y servicios: `buscar_servicio.py` (catálogo `precios/catalogo_servicios.*`), siempre con el mismo alcance.
- Al terminar, actualizar `conocimiento/estado_y_pendientes.md`.

## Nunca

- Enviar nada al cliente. Pasar a `"estado": "aprobado"` sin que Matías o la dirección lo digan.
- Informar un número calculado a mano en el chat: los totales salen solo de `armar_cotizacion.py`.
- Usar un precio sin abrir su fuente, ni la MO de un trabajo con otro alcance.
- Ajustar por inflación con una tasa fija: se usa `conocimiento/costos/indices_ajuste.csv`. Si el mes actual no está, actualizar `herramientas/indices_inflacion.py` con datos y fuentes.
- Editar a mano `computo.csv`, la planilla, el informe o las ofertas: se edita `cotizacion.json` / `oferta.json` y se vuelve a armar.
