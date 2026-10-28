---
name: cotizar
description: Cotizar un pedido de cliente de ITT (puentes, skids, manifolds, colectores, piping, separadores, filtros, tanques, trampas) desde el pedido y el plano hasta la oferta técnica y económica, siguiendo el procedimiento obligatorio de ITT. Usar cuando Matías pase un pedido de cotización, un plano o una lista de materiales, o pida actualizar, revisar o pasar a oferta una cotización existente.
---

# Cotizar un pedido de ITT

Leé primero `conocimiento/estado_y_pendientes.md`. Seguí **en orden** `conocimiento/guia_cotizacion.md`, respetando las reglas de `conocimiento/procedimiento_cotizacion.md` (P1–P10). Antes de empezar, leé `conocimiento/errores_y_lecciones.md`: ahí están los errores que ya se cometieron. El caso modelo es `cotizaciones/COT26-1003-001_CAPEX_OQ8209/` (leé su `bitacora.md` y su `cotizacion.json`).

## Flujo

1. **Carpeta:** copiar `cotizaciones/_plantilla/` a `cotizaciones/COT[AA]-[CCCC]-[NNN]_<CLIENTE>_<PEDIDO>/`. El código del cliente está en `conocimiento/comercial/clientes.csv`. Guardar los originales en `pedido/` y anotar la cotización en `cotizaciones/README.md`.
2. **Plano → `pedido/lista_materiales_plano.csv`:** la tabla completa, renglón por renglón, con todas las columnas. Mirar el dibujo para ver qué extremos BW se sueldan en taller y cuáles en campo.
3. **Antecedentes y precios:** correr primero `python herramientas/buscar_antecedentes.py --familia <F> --texto "..." --diametro --serie --material --union --cliente` y revisar los 3–5 primeros, priorizando los que tienen **planilla de costo** y los más nuevos. Usar como modelo la planilla de costo de la oferta más parecida. Para cada material sin precio en los antecedentes: `python herramientas/buscar_material.py "<descripción con Ø, serie, material, extremos>"` (igual primero; un similar va con `coincide: similar` y su diferencia). Para cada precio, **abrir el documento original**, comparar la especificación con el plano campo por campo y anotar proveedor, carpeta y fecha. Un dato verbal o por WhatsApp va como `est`. Cada fuente de base se marca `coincide`: `igual`, `similar` (con `diferencia`) o `sin_ref`.
4. **`cotizacion.json`:** un ítem por posición del plano, con la misma cantidad y unidad; las compras extra en filas `14b`. Cargar todas las fuentes de cada ítem (la primera es la de base). Las soldaduras van junta por junta. Factores 1,35 / 1,35, contingencia 5%, `AJ: 1`, `fecha_referencia` = hoy.
5. **Armar:** `python herramientas/armar_cotizacion.py cotizaciones/<carpeta>`. Tiene que terminar sin error: Python y planilla iguales, `verificar_computo.py` sin errores.
6. **Revisar los avisos** uno por uno y contrastar con 2 antecedentes. Si la diferencia es mayor al 15%, explicarla antes de mostrar el número.
7. **Revisión independiente:** lanzar un subagente que **no** armó el cómputo para comparar plano contra cómputo, informe y planilla. Corregir o justificar lo que encuentre.
7 bis. **Preliminar → Compras → definitivo:** el preliminar (con piezas similares) se presenta con la lista para Compras. Matías no compra. Cuando llegan las respuestas se cargan como fuente de base `cot` / `igual` y se vuelve a armar.
8. **Presentar a Matías:** siempre como "borrador, sin revisar" hasta que esté revisado. Publicar `informe.html` con la herramienta Artifact y mandar la planilla y las ofertas con SendUserFile.
9. **Registrar:** actualizar `bitacora.md`, `cotizaciones/README.md` y `errores_y_lecciones.md` si hubo errores. Después, commit y push.

## Datos que se usan siempre igual
- Precios **sin IVA**; pesos a dólares con el **promedio mensual del oficial BNA venta** (`conocimiento/costos/dolar_mensual.csv`), salvo que el documento diga su tipo de cambio.
- Materiales: `buscar_material.py` (columna `alerta`: revisar antes de usar). Marcas del cliente: `comercial/marcas_aprobadas.csv`. Plazos de proveedores: `comercial/plazos_proveedores.csv` (para el camino crítico, el máximo del rubro si es "stock salvo venta"). Kg y m²: `tecnico/canos_peso_superficie.csv`, `bridas_peso.csv`, `accesorios_peso.csv` (estos dos, borrador). MO y servicios: `precios/catalogo_servicios.*` cuando exista (si no, `costos/tarifas.csv` y antecedentes con el mismo alcance).
- Al terminar, actualizar `conocimiento/estado_y_pendientes.md`.

## Nunca

- Enviar nada al cliente. Pasar a `"estado": "aprobado"` sin que Matías o la dirección lo digan.
- Informar un número calculado a mano en el chat: los totales salen solo de `armar_cotizacion.py`.
- Usar un precio sin abrir su fuente, ni la MO de un trabajo con otro alcance.
- Ajustar por inflación con una tasa fija: se usa `conocimiento/costos/indices_ajuste.csv`. Si el mes actual no está, actualizar `herramientas/indices_inflacion.py` con datos y fuentes.
- Editar a mano `computo.csv`, la planilla, el informe o las ofertas: se edita `cotizacion.json` / `oferta.json` y se vuelve a armar.
