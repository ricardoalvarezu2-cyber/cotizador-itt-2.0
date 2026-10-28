# Instrucciones para armar el catálogo de mano de obra y servicios (etapa 1)

Encargo aprobado por Matías el 27/10/2026 (costo estimado USD 3–6 con un subagente sonnet). Si el catálogo todavía no existe en `conocimiento/precios/catalogo_servicios.*`, relanzar un subagente con este texto.

## Objetivo
Un catálogo como el de materiales (`herramientas/catalogo_materiales.py`, `buscar_material.py`, `numeros.py`, `test_catalogo.py`), con los mismos criterios, reutilizando (importando, sin modificar) `numeros.leer_numero`, `numeros.fecha_iso`, `catalogo_materiales.iva_de`, `catalogo_materiales.unidad_norm`, `catalogo_materiales.tabla_dolar/en_mes` e `indice_proyectos.norm`.

## Dos pasos
1. **Extracción (lectura con IA):** `conocimiento/precios/servicios_extraidos.csv`, un renglón por precio: `hoja, servicio, descripcion, proveedor, fecha, precio, moneda, iva_origen, unidad (USD/hora, USD/pulg-eq, USD/junta, USD/placa, USD/m2, USD/kg, USD/viaje, USD/km, USD/dia, USD/visita, global), magnitud, equipo_referencia, lugar (taller ITT / taller tercero / campo), incluye, no_incluye, carpeta_origen, archivo_origen, texto_original (cita literal), confianza, nota`. Cada precio verificado en el documento original de `fuentes_originales/ofertas_texto/`. Nunca completar un dato que no esté.
2. **Armado determinístico:** `herramientas/catalogo_servicios.py` → `conocimiento/precios/catalogo_servicios.csv`, `_historial.csv` y `.xlsx`, con registro de códigos estables `catalogo_servicios_codigos.csv`.

## Hojas (8 + "Todos")
MO propia · Fabricación y armado (terceros) · Soldadura y piping · Ensayos y END (incluye prueba hidráulica) · Pintura y revestimientos (incluye galvanizado) · Transporte e izaje · Ingeniería, calidad e inspección (planos, cálculo, dossier, WPS/PQR, calificación de soldadores, inspector) · Otros servicios (mecanizado, tratamiento térmico, montaje en campo, rolado/cilindrado). Una categoría pasa a hoja propia cuando junta 15–20 datos.

Columnas comunes: código, descripción, unidad, último precio USD sin IVA, iva, fecha, proveedor, ruta de origen (Z:\VENTAS\OFERTAS Y LICITACIONES\<carpeta>), archivo, ruta en el repo, precio ajustado a hoy, tarifa unitaria (precio ÷ magnitud), alcance comparable (sí solo si hay tarifa unitaria), incluye, no incluye, precios en historial, mín, máx, alerta.

## Reglas
- Siempre sin IVA (con IVA se divide por 1,21 o 1,105; si no dice, sin IVA).
- Números y fechas con `numeros.py`; nunca una fecha por defecto.
- Pesos a USD con el promedio mensual del dólar oficial BNA venta (`indices_ajuste.csv`, columna dolar_bna), salvo que el documento diga su tipo de cambio.
- Ajuste a hoy con `indice_local_usd` (costo local en USD), no con el CPI de EE.UU.
- Solo se juntan precios del mismo servicio, misma unidad y alcance comparable. Los globales de distinto equipo no se juntan.
- Alertas: total tomado como unitario, posible pesos como USD, sin fecha, número ambiguo, historial disperso (>3×), confianza baja, valores en USD de ene-2024 a abr-2025 sin tipo de cambio visible (período con cepo: mostrar cuánto daría si hubiera sido blue).

## Fuentes de la etapa 1
`costos/tarifas.csv`, `costo_hora_planta.csv`, `sueldos_2024-10.csv`; renglones de servicios de `precios/proveedores_2025.csv` y `proveedores_2026.csv` (~130); proveedores y desglose de las fichas 2025–2026 (sin duplicar); ítems no materiales de `cotizaciones/*/cotizacion.json` con fuente cot/ant y `coincide: igual`. La etapa 2 (MO renglón por renglón de las 50 planillas de costo, ~USD 8–12) queda para después.

## Entregables
`herramientas/buscar_servicio.py "<texto>" [--hoja] [--top]`, `herramientas/test_catalogo_servicios.py` (al menos 10 casos reales), `conocimiento/precios/catalogo_servicios_LEEME.md`. Armado determinístico (dos corridas, mismo CSV). Después: revisión de una muestra contra los originales, commit y push.
