# Cantidades y estructura de costo de planillas de ITT — instrucciones para el agente

Sos analista de costos de ITT S.A. (fabricante de equipos para oil & gas). Vas a leer las **planillas de costo** de unas
carpetas de cotización y sacar, por cada equipo, las **cantidades** (horas, pulgadas de soldadura, kg, placas) y la
**estructura del costo** (cuánto es materiales, MO propia, terceros). Los precios de 2021–2024 son del período con cepo y
no se usan como costo: lo que importa son las cantidades y las proporciones (Matías, 29-10-2026).

## Dónde están los datos
- Textos de cada carpeta: `fuentes_originales/ofertas_texto/<carpeta>/` (cada archivo original tiene su `.txt`; las
  planillas son `*.xlsx.txt` / `*.xls.txt`, con `=== hoja <nombre>` por hoja y celdas separadas por ` | `).
- Modelo y criterios ya usados (leelos primero): `conocimiento/costos/horas_por_equipo.csv` (formato de salida, con
  ejemplos) y `conocimiento/costos/horas_por_equipo_LEEME.md` (criterios: revisión más nueva, horas por unidad, montaje =
  días × hombres × 9 h, qué es resto de plantilla, etc.).
- Las planillas suelen tener hojas "Mano de Obra de ITT" / "Soldadura + HH" / "HH" con "Horas de ingeniería", "Hora de
  calidad", "Hora de montaje" (cantidad | USD/h | total), una lista de materiales con COSTO UNIT y un RESUMEN con
  materiales, MO, terceros, factor y precio. Buscá con grep: `horas de ingenier`, `hora de calidad`, `hora de montaje`,
  `HH`, `pulgada`, `soldadura`, `RESUMEN`, `TOTAL`, `FACTOR`, `UTILIDAD`, `COSTO`.

## Salida 1 — horas (una fila por equipo, mismas columnas que horas_por_equipo.csv)
`proyecto,fecha,archivo,hoja,equipo,tipo,unidades,diametro_pulg,diametro_texto,serie,horas_ingenieria_u,horas_calidad_u,horas_montaje_u,usd_h_ing,usd_h_cal,usd_h_mont,vigente,usar_montaje,pulgadas_soldadura,pulgadas_tipo,peso_kg,posiciones,costo_materiales_usd,detalle_montaje,nota,cita`
- `proyecto` = la carpeta tal cual te la pasan. `fecha` AAAA-MM-DD (la de la planilla o la oferta; si solo hay año, AAAA-07-01 y decilo en `nota`).
- `archivo` relativo a la carpeta. `tipo`: puente, filtro, trampa, manifold, tanque (también separadores, calentadores, recipientes, KOD), skid, prefabricado.
- `diametro_pulg`: en recipientes (separador, filtro, tanque, calentador, KOD) el Ø del **cuerpo**; en el resto, el Ø principal de línea. `diametro_texto` como figura.
- Horas **por unidad** (ver LEEME: si la planilla prorratea entre unidades, decilo en `nota`). Sin dato: vacío, no 0 (salvo que la planilla diga 0 y lo aclares).
- `usd_h_*`: la tarifa que usa la planilla; si está en ARS, ponela en ARS y aclará moneda y tipo de cambio del documento en `nota`.
- `vigente` si/no (la revisión vigente es la más nueva). `usar_montaje` no si el montaje está incompleto o es 0 sin sentido.
- `pulgadas_soldadura` y `pulgadas_tipo` como en el LEEME (equivalente = costo soldadura / precio por pulgada, o DN × cantidad).
- `costo_materiales_usd`: el de la planilla tal cual (es del cepo: en `nota` poné "cepo: solo como tamaño relativo" si es anterior a 2025-04-14).
- `detalle_montaje`: actividades con días × hombres × 9 h. `cita`: el texto de las celdas de donde salen las horas (copiado).

## Salida 2 — estructura del costo (una fila por equipo)
`proyecto,fecha,archivo,equipo,tipo,unidades,moneda,tc_documento,costo_materiales,costo_mo_propia,costo_terceros,costo_otros,costo_total,factor_venta,precio_venta,pct_materiales,pct_mo_propia,pct_terceros,pct_otros,que_es_terceros,nota`
- Montos por unidad, en la moneda de la planilla. `tc_documento`: el tipo de cambio que dice el documento (vacío si no dice).
- `pct_*` = cada rubro / costo_total (0 a 1, punto decimal). `que_es_terceros`: qué se tercerizó (soldadura Ledesma, RX, pintura, rolado…).
- `factor_venta` solo si figura (FR, factor, utilidad); si lo derivás (precio / costo), decilo en `nota`.

## Reglas
- No inventes: si no está, vacío. Números con punto decimal y sin miles (formato de máquina). Fechas AAAA-MM-DD.
- Si una carpeta no tiene horas ni estructura de costo (solo precios de venta o una planilla vacía), no escribas filas y
  anotalo en el informe final.
- Restos de plantilla (rótulos de otro equipo, "Total de Pulgadas 53,97", tablas de referencia de otras cotizaciones):
  no los tomes como datos del equipo (ver LEEME).
- No modifiques ningún archivo del repositorio: escribí solo los CSV que te indiquen (UTF-8, con encabezado).
- Respondé al final con una línea por carpeta: carpeta | equipos con horas | equipos con estructura | problemas.
