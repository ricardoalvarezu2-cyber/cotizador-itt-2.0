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

## Ubicación de los originales
- Carpeta de cotizaciones de ITT: `Z:\VENTAS\OFERTAS Y LICITACIONES` (15.601 archivos, 27 GB; solo en la red de ITT).
- **Tanda 1** (oferta comercial, proveedores, propuesta enviada y OC; 2.281 archivos, RAR de 1,67 GB) en Google Drive: https://drive.google.com/file/d/1FeaoYuehghEkgomXvcQqvjecoriK_4Wr/view?usp=drive_link
  - ID: `1FeaoYuehghEkgomXvcQqvjecoriK_4Wr`. Descarga directa (si el archivo está compartido con "cualquier persona con el enlace"): `curl -L -o t1.rar "https://drive.usercontent.google.com/download?id=1FeaoYuehghEkgomXvcQqvjecoriK_4Wr&export=download&confirm=t"` y extraer con `unrar-free -x`.
  - El texto extraído ya está en `fuentes_originales/ofertas_texto/`; el RAR hace falta solo para releer un original (escaneos, adjuntos).

## Procedimiento de cotización (obligatorio)
- Toda cotización sigue `conocimiento/procedimiento_cotizacion.md` (pasos P1–P10). Se escribió después de los errores de la COT26-1003-001, que están registrados en `conocimiento/errores_y_lecciones.md`. **Un error que llega al cliente puede ser catastrófico.**
- **Nunca enviar nada al cliente.** Estados: borrador → revisado → aprobado (Matías o la dirección) → enviado. Mientras no esté revisada, todo número se muestra como "borrador, sin revisar".
- El cómputo copia la tabla del plano renglón por renglón, con la misma cantidad y unidad. Las compras extra van en filas aparte (`14b`).
- Las soldaduras se derivan de la columna de extremos (BW, SW, NPT/BW), junta por junta, separando taller y campo.
- Cada precio se verifica en el documento original (nunca de memoria ni de un resumen), con proveedor, origen, fecha y la misma especificación que el plano. Un valor "aproximado", verbal o por WhatsApp es estimado.
- La MO de terceros se toma de un trabajo con el mismo alcance. Factores: materiales 1,35 y MO y servicios 1,35; el 1,40 solo para MO vendida sola.
- Los totales salen de la planilla o del informe con fórmulas, nunca de cuentas hechas en el chat. Excel e informe tienen que dar igual.
- Antes de pasar a "revisado": `python herramientas/verificar_computo.py cotizaciones/<carpeta>` sin errores, más una revisión independiente (otro agente o persona) del cómputo contra el plano.
- Todo error detectado se anota en `conocimiento/errores_y_lecciones.md`.

## Reglas de cálculo y comerciales
- Moneda USD, sin IVA, entrega EXW planta Quilmes Oeste. El factor de venta lo define la dirección; la herramienta propone 1,35 y muestra escenarios.
- El cálculo de costo y plazo es determinístico (reglas y tarifas de la base); la IA lee documentos y arma el cómputo.
- Antes de lanzar procesamientos con muchos agentes, estimar el costo y pedir confirmación. Usar un modelo más chico (sonnet) para extracción masiva.
