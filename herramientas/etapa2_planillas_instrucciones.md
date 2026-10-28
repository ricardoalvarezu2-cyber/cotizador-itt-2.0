# Etapa 2 de los catálogos: costos renglón por renglón de las planillas de costo 2025–2026

Aprobado por Matías el 28/10/2026 (estimado USD 10–12 con 3 subagentes sonnet). Si `conocimiento/precios/planillas_costo_items.csv` no existe o está incompleto, relanzar con este texto.

## Qué proyectos
Los del índice `conocimiento/comercial/indice_proyectos.csv` con `tiene_planilla_costo` = "si" y `origen` distinto de "cotizador" (49 al 28/10/2026), ordenados por `id` y repartidos en 3 partes: la parte N toma los proyectos en las posiciones N, N+3, N+6… (empezando en 1). Texto de cada proyecto en la columna `carpeta_textos` (`fuentes_originales/ofertas_texto/...`). Las planillas de costo suelen estar en `4.Armado de la Oferta Comercial/*.xls*.txt` o `7.Propuesta.../*.xls*.txt`.

## Qué extraer
Cada renglón de COSTO de la planilla (no el precio de venta, no subtotales ni totales), a `conocimiento/precios/planillas_costo_items_parteN.csv`, con columnas:
`proyecto, fecha_planilla, carpeta, archivo, ubicacion (hoja y fila o renglón), tipo (material / mo / servicio / otro), rubro (válvula, brida, caño, accesorio, junta, bulonería, instrumento, chapa/perfil, soldadura, armado, END, prueba hidráulica, pintura, galvanizado, transporte, ingeniería, calidad/dossier, embalaje, otro), descripcion (literal), cantidad, unidad, costo_unitario, moneda, iva_origen ("+ IVA", "con IVA", "no dice"), proveedor_o_criterio (literal: proveedor, "stock", "estimado", referencia a cotización), tc_explicito (valor si la planilla dice el tipo de cambio usado; si no, vacío), factor_venta (si el renglón lo trae), cita (texto literal corto del renglón), confianza (alta/media/baja), nota`.

## Reglas
- No inventar: lo que no está, vacío. Si el costo unitario no está pero sí el total y la cantidad, calcularlo y decirlo en `nota`.
- Números con el criterio de `herramientas/numeros.py` (4.500 / 4,500 / 4500); si es ambiguo, `confianza` baja y nota.
- Fechas en ISO; la de la planilla (o de la carpeta si la planilla no tiene) — nunca inventada.
- Mano de obra: anotar unidad real (hora, pulg-eq, kg, global por equipo) y lo que dice que incluye.
- Guardar avances seguido (después de cada proyecto) para no perder lo leído si se corta.
- No modificar archivos existentes. No hacer commit.

## Después (lo hace la sesión principal)
Unir las 3 partes en `planillas_costo_items.csv`, sumar los materiales al catálogo de materiales como fuente "planilla interna" y la MO y los servicios al catálogo de servicios; aplicar las reglas vigentes (sin IVA, dólar oficial BNA promedio, descarte de valores del período con cepo sin TC explícito, alertas); revisar una muestra contra los originales; commit.
