# Cotizador ITT — reglas del proyecto

## Contexto
- Herramienta de cotización para ITT S.A. (Quilmes, Argentina), fabricante de equipos para oil & gas: calentadores, separadores, filtros, skids, manifolds, colectores, puentes de medición, cañerías, tanques y trampas. Empresa del grupo Taval (válvulas).
- Usuario: Matías Russo, de ventas de ITT. Idioma: **español rioplatense**. **Respuestas cortas** (pedido de Matías, 28/10/2026): qué se hizo en 2-3 líneas, los errores encontrados y lo que necesita decidir; sin listas de detalle ni cifras de cobertura (29-10-2026).
- La base de conocimiento está en `conocimiento/` y empieza por **`conocimiento/estado_y_pendientes.md`** (estado, decisiones y pendientes: leerlo al empezar cada chat y actualizarlo al terminar) y `conocimiento/RESUMEN.md`. Las fuentes están en `fuentes_originales/`.

## Objetivo
- **Construir el cotizador automático.** Las cotizaciones que se hacen ahora (CAPEX, Camuzzi, YPF, etc.) son casos de prueba para armar el proceso, todas con el mismo peso; ninguna es prioritaria ni tiene página propia. Los pendientes del proyecto son los del cotizador, no los de cada presupuesto (Matías, 28/10/2026).

## Reglas de datos
- **El repositorio es privado. No omitir ni filtrar información por privacidad.** Se guardan completos los contactos de clientes y proveedores, los sueldos, los costos internos y los precios, porque sirven para costear (por ejemplo, la mano de obra). Pedido explícito del usuario el 27/10/2026.
- La prioridad es que el cotizador **no falle por falta o pérdida de información**: todo lo que se procese se guarda en el repositorio. El entorno de trabajo es temporal y lo que no se sube a GitHub se pierde.
- Una sola versión vigente de cada dato, con fecha y fuente. Ante dos versiones, vale la más reciente y se anota la decisión en `conocimiento/fuentes.md`.
- **Todo costo y precio se trabaja SIN IVA.** Con IVA se divide por la alícuota (21% o 10,5%); si no dice, se toma sin IVA (decisión de Matías, 27/10/2026).
- **Pesos a dólares: promedio mensual del dólar oficial BNA venta** (`conocimiento/costos/dolar_mensual.csv`), salvo que el documento diga su tipo de cambio (decisión de Matías, 27/10/2026). Nunca mezclar cotizaciones del dólar (oficial, divisa, MEP, blue) en una misma serie.
- **Fechas a la vista: siempre DD-MM-AAAA** (página, informes, planillas, ofertas, textos y respuestas). Adentro se guardan AAAA-MM-DD para ordenar y comparar; para mostrarlas, `numeros.a_vista` en Python y `Documentos.fecha` en la página (decisión de Matías, 28/10/2026).
- **Números a la vista y en los campos: punto de miles, coma decimal y 2 decimales** (1.234,56; decisión de Matías, 29-10-2026), en página, informes, planillas, ofertas, textos y respuestas. Para mostrar: `numeros.fmt`/`fmtg` en Python y `Documentos.num` en la página. Los campos de la página rechazan lo que no cumple ("1,500", "1.5", más de 2 decimales) y dicen por qué. Adentro (CSV, JSON) se sigue guardando con punto decimal y sin miles; los coeficientes técnicos (factores de soldadura, kg/m) pueden mostrar más decimales, siempre con coma.
- Números y fechas de documentos se leen siempre con `herramientas/numeros.py` (4.500 / 4,500 / 4500; nunca una fecha por defecto). Después de cualquier cambio en herramientas o datos, correr `python herramientas/verificar_todo.py` (tiene que dar "TODO OK").
- **Antes de cerrar o archivar un chat, consolidar** (Matías, 29-10-2026): anotar en `conocimiento/` lo aprendido, las decisiones y los errores de la sesión, y pasarlo a `main` (procedimiento en `web/LEEME.md`, "Consolidar antes de archivar"). La página no archiva un chat sin eso.
- **Todo trabajo en el repo termina en `main`** (pedido de Matías, 29-10-2026): commit y push de la rama de trabajo y después pasarla directo a `main` sin PR (`git fetch origin main && git checkout main && git merge --ff-only <rama>` o, si no se puede, `git merge <rama>`; `git push origin main`; volver a la rama). Las sesiones de pedidos y la tarea semanal trabajan sobre `main`. Si hay conflicto, resolverlo con las reglas de siempre; nunca force-push a `main`.
- **Manda el repositorio. La biblioteca (catálogo y antecedentes) se alimenta solo con el botón "Pasar al repositorio y a la biblioteca"** de la página (Matías, 29-10-2026): pasa esa versión al repositorio y la suma a `biblioteca_cotizaciones/`; si no está revisada o aprobada, la página avisa y pide confirmación; si se vuelve a incorporar, la última versión reemplaza a la anterior. Ninguna cotización entra sola (ni borradores ni las del repositorio).
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

## Página web
- Página del cotizador: https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ (fuente en `web/`, instructivo en `web/LEEME.md`, incluida la sección "Pedidos desde la página").
- **Los pedidos de la página se procesan sin pedir autorización**, siguiendo `web/LEEME.md` (pedido de Matías, 28/10/2026). Nunca se envía nada al cliente: todo queda en borrador.

## Reglas de cálculo y comerciales
- Moneda USD, sin IVA, entrega EXW planta Quilmes Oeste. El factor de venta lo define la dirección; la herramienta propone 1,35 y muestra escenarios.
- El cálculo de costo y plazo es determinístico (reglas y tarifas de la base); la IA lee documentos y arma el cómputo. Lo que varía entre cotizaciones (planos, pliegos, cotizaciones de proveedores en cualquier formato) lo lee la IA; desde los formatos internos (`lista_materiales_plano.csv`, `cotizacion.json`) todo es automático y se revisa.
- Antes de lanzar procesamientos con muchos agentes, estimar el costo y pedir confirmación. Usar un modelo más chico (sonnet) para extracción masiva.
