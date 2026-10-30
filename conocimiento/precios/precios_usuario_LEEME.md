# Precios cargados por el usuario (30-10-2026)

`precios_usuario.csv`: precios que pasa Matías (o quien él autorice) sin documento, por ejemplo hablados con el proveedor.
**Si Matías los confirma, son firmes, no estimados** (decisión de Matías, 30-10-2026): reemplaza, para estos casos, la regla
de que un valor verbal va como estimado. Cada renglón dice quién lo confirmó y cómo se obtuvo.

Columnas: fecha (AAAA-MM-DD), clase (servicio o material), rubro (hoja del catálogo de servicios), concepto, descripción,
precio, moneda (ARS o USD), unidad (de la tarifa: placa, visita, hora, kg, m2, global…), iva (sin IVA / con IVA 21% /
con IVA 10,5%), proveedor, confirmado_por, como_se_obtuvo, nota.

- Los servicios entran al catálogo de servicios (`catalogo_servicios.py`) con la regla de siempre: pesos a dólares con el
  promedio mensual del oficial BNA venta del mes del precio; con IVA se divide por la alícuota.
- Los materiales: por ahora se cargan en `listas_nuevas.csv` (tipo_precio "cotización", archivo_origen = este archivo).
- Si después llega el presupuesto escrito, se carga con su documento y vale el más nuevo (`fuentes.md`).
