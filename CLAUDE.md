# Cotizador ITT — reglas del proyecto

## Contexto
- Herramienta de cotización para ITT S.A. (Quilmes, Argentina), fabricante de equipos para oil & gas: calentadores, separadores, filtros, skids, manifolds, colectores, puentes de medición, cañerías, tanques y trampas. Empresa del grupo Taval (válvulas).
- Usuario: Matías Russo, de ventas de ITT. Idioma: **español rioplatense**. **Respuestas cortas** (pedido de Matías, 28/10/2026).
- La base de conocimiento está en `conocimiento/` y empieza por **`conocimiento/estado_y_pendientes.md`** (estado, decisiones y pendientes: leerlo al empezar cada chat y actualizarlo al terminar) y `conocimiento/RESUMEN.md`. Las fuentes están en `fuentes_originales/`.

## Objetivo
- **Construir el cotizador automático.** Las cotizaciones que se hacen ahora (CAPEX) son casos de prueba para armar el proceso; los pendientes del proyecto son los del cotizador, no los de cada presupuesto.

## Reglas de datos
- **El repositorio es privado. No omitir ni filtrar información por privacidad.** Se guardan completos los contactos de clientes y proveedores, los sueldos, los costos internos y los precios, porque sirven para costear (por ejemplo, la mano de obra). Pedido explícito del usuario el 27/10/2026.
- La prioridad es que el cotizador **no falle por falta o pérdida de información**: todo lo que se procese se guarda en el repositorio. El entorno de trabajo es temporal y lo que no se sube a GitHub se pierde.
- Una sola versión vigente de cada dato, con fecha y fuente. Ante dos versiones, vale la más reciente y se anota la decisión en `conocimiento/fuentes.md`.
- **Todo costo y precio se trabaja SIN IVA.** Con IVA se divide por la alícuota (21% o 10,5%); si no dice, se toma sin IVA (decisión de Matías, 27/10/2026).
- **Pesos a dólares: promedio mensual del dólar oficial BNA venta** (`conocimiento/costos/dolar_mensual.csv`), salvo que el documento diga su tipo de cambio (decisión de Matías, 27/10/2026). Nunca mezclar cotizaciones del dólar (oficial, divisa, MEP, blue) en una misma serie.
- Números y fechas de documentos se leen siempre con `herramientas/numeros.py` (4.500 / 4,500 / 4500; nunca una fecha por defecto). Después de cualquier cambio en herramientas o datos, correr `python herramientas/verificar_todo.py` (tiene que dar "TODO OK").
- No hay a quién consultar las planillas viejas (Javier Elejondo ya no está en la empresa): ante dudas, tomar el criterio con más sentido técnico y dejarlo documentado.

## Ubicación de los originales
- Carpeta de cotizaciones de ITT: `Z:\VENTAS\OFERTAS Y LICITACIONES` (15.601 archivos, 27 GB; solo en la red de ITT).
- **Tanda 1** (oferta comercial, proveedores, propuesta enviada y OC; 2.281 archivos, RAR de 1,67 GB) en Google Drive: https://drive.google.com/file/d/1FeaoYuehghEkgomXvcQqvjecoriK_4Wr/view?usp=drive_link
  - ID: `1FeaoYuehghEkgomXvcQqvjecoriK_4Wr`. Descarga directa (si el archivo está compartido con "cualquier persona con el enlace"): `curl -L -o t1.rar "https://drive.usercontent.google.com/download?id=1FeaoYuehghEkgomXvcQqvjecoriK_4Wr&export=download&confirm=t"` y extraer con `unrar-free -x`.
  - El texto extraído ya está en `fuentes_originales/ofertas_texto/`; el RAR hace falta solo para releer un original (escaneos, adjuntos).

## Procedimiento de cotización (obligatorio)
- **Para cotizar, usar el skill `cotizar` (`.claude/skills/cotizar/SKILL.md`) y la guía `conocimiento/guia_cotizacion.md`.** Cada cotización es una carpeta en `cotizaciones/` (modelo: `cotizaciones/_plantilla/`; caso completo: `COT26-1003-001_CAPEX_OQ8209/` con su `bitacora.md`). La única fuente de datos es `cotizacion.json`. Todo lo demás (cómputo, planilla, informe, ofertas) lo genera `python herramientas/armar_cotizacion.py cotizaciones/<carpeta>`. Registro de cotizaciones: `cotizaciones/README.md`.
- Los antecedentes se buscan primero con `python herramientas/buscar_antecedentes.py` (índice de proyectos 2025–2026: misma familia, más parecido y más nuevo primero). Por decisión de Matías, 2021–2024 no se indexa.
- La MO y los servicios se buscan con `python herramientas/buscar_servicio.py "<texto>"` (un global solo se usa si el alcance es el mismo).
- **Antes de buscar precios a mano, correr `python herramientas/precotizar.py cotizaciones/<carpeta>`** (sin IA): arma la precotización desde la tabla del plano y marca solo lo que hay que revisar.
- Los precios de materiales sueltos se buscan con `python herramientas/buscar_material.py "<descripción>"` (catálogo por familia; igual antes que similar; último precio con fecha y ruta de origen).
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
- El cálculo de costo y plazo es determinístico (reglas y tarifas de la base); la IA lee documentos y arma el cómputo. Lo que varía entre cotizaciones (planos, pliegos, cotizaciones de proveedores en cualquier formato) lo lee la IA; desde los formatos internos (`lista_materiales_plano.csv`, `cotizacion.json`) todo es automático y se revisa.
- Antes de lanzar procesamientos con muchos agentes, estimar el costo y pedir confirmación. Usar un modelo más chico (sonnet) para extracción masiva.
