# Cotizador ITT — reglas del proyecto

## Contexto
- Herramienta de cotización para ITT S.A. (Quilmes, Argentina), fabricante de equipos para oil & gas: calentadores, separadores, filtros, skids, manifolds, colectores, puentes de medición, cañerías, tanques y trampas. Empresa del grupo Taval (válvulas).
- Usuario: Matías Russo, de ventas de ITT. Idioma: **español rioplatense**.
- La base de conocimiento está en `conocimiento/` y empieza por `conocimiento/RESUMEN.md`. Las fuentes están en `fuentes_originales/`.

## Reglas de datos
- **El repositorio es privado. No omitir ni filtrar información por privacidad.** Se guardan completos los contactos de clientes y proveedores, los sueldos, los costos internos y los precios, porque sirven para costear (por ejemplo, la mano de obra). Pedido explícito del usuario el 27/10/2026.
- La prioridad es que el cotizador **no falle por falta o pérdida de información**: todo lo que se procese se guarda en el repositorio. El entorno de trabajo es temporal y lo que no se sube a GitHub se pierde.
- Una sola versión vigente de cada dato, con fecha y fuente. Ante dos versiones, vale la más reciente y se anota la decisión en `conocimiento/fuentes.md`.
- No hay a quién consultar las planillas viejas (Javier Elejondo ya no está en la empresa): ante dudas, tomar el criterio con más sentido técnico y dejarlo documentado.

## Reglas de cálculo y comerciales
- Moneda USD, sin IVA, entrega EXW planta Quilmes Oeste. El factor de venta lo define la dirección; la herramienta propone 1,35 y muestra escenarios.
- El cálculo de costo y plazo es determinístico (reglas y tarifas de la base); la IA lee documentos y arma el cómputo.
- Antes de lanzar procesamientos con muchos agentes, estimar el costo y pedir confirmación. Usar un modelo más chico (sonnet) para extracción masiva.
