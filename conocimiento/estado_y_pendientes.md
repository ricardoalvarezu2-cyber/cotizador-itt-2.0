# Estado del cotizador, decisiones y pendientes

**Leer al empezar cada chat.** Es la memoria del proyecto entre sesiones: qué está hecho, qué se decidió, qué falta.

**Objetivo: construir el cotizador automático.** Las cotizaciones (por ahora la CAPEX) son casos de prueba para armar y validar el proceso; sus pendientes no son pendientes del proyecto. Actualizado al 30-10-2026.

## 1. Qué hay hoy

| Pieza | Estado | Dónde |
|---|---|---|
| Procedimiento de cotización (P1–P10) y guía paso a paso | Vigente | `procedimiento_cotizacion.md`, `guia_cotizacion.md`, skill `.claude/skills/cotizar/` |
| Motor determinístico: cómputo, planilla con fórmulas, informe HTML con descargas, lista para Compras, ofertas técnica y económica | Vigente | `herramientas/armar_cotizacion.py`, `generar_oferta.py`, `lista_compras.py`, `verificar_computo.py` |
| Índice de proyectos 2025–2026 y buscador de antecedentes | Vigente (163 proyectos con ficha + 145 carpetas sin ficha en `indice_historico.csv`). **Criterio nuevo 29-10-2026, igual para todas las familias:** subtipo de equipo (42 subtipos), sinónimos, Ø del cuerpo en recipientes, dato faltante sin castigo, carpetas anteriores cuando hay menos de 5 del subtipo; página igual a Python | `comercial/indice_proyectos.csv`, `herramientas/buscar_antecedentes.py`, `test_antecedentes.py` |
| Catálogo de materiales con marca, unidad, IVA y alertas | Vigente: 4.549 materiales (1.385 con precio ESTIMADO del cepo; 130 sin precio); incluye listas de Ventas (Renard 05-2025, Cintolo 29.1, Provemet) y Lista 30 de Taval × 0,52 | `precios/catalogo_materiales.*`, `herramientas/catalogo_materiales.py`, `buscar_material.py`, `test_catalogo.py` |
| Lector único de números y fechas | Vigente | `herramientas/numeros.py` |
| **Compatibilidades de la norma en el buscador de materiales** (material y grupo B16.5, cara, rosca, schedule, NACE) | Vigente desde 30-10-2026, Python y página | `herramientas/compatibilidad.py`, `tecnico/compatibilidades_LEEME.md`, `test_compatibilidad.py` |
| **Flujo unificado y frenos de la oferta** (transcripción doble, matriz de requisitos, estimado > 15%, cotizaciones vencidas, antecedentes, plazo) y **errores sembrados** | Vigente desde 30-10-2026 (aprobado por Matías sin candados de estados) | `procedimiento_cotizacion.md` ("Flujo unificado"), `herramientas/frenos.py`, `test_errores_sembrados.py` |
| **Precios cargados por el usuario** (firmes si los confirma Matías) | Vigente desde 30-10-2026 (RX por visita y por placa) | `precios/precios_usuario.csv` |
| **Controles que solo avisan**: precio que no figura en su documento (`verificacion_origen.md`), validador de fichas, informe de cambios del buscador; `subir_a_main.py` | Vigente desde 30-10-2026 | `herramientas/verificar_origen.py`, `validar_fichas.py`, `revisar_cambio_busqueda.py`, `subir_a_main.py` |
| Comparación con antecedentes (P8) **costo contra costo** por rubro | Vigente desde 30-10-2026 | `comparar_antecedentes.py`, `web/src/antecedentes.js` |
| Estructura de costo de 103 equipos de 2021–2024 (solo proporciones) | Referencia | `costos/estructura_costo_historica.csv` |
| **Precotización automática sin IA** (materiales del catálogo, soldaduras de los extremos, pintura, PH, RX) | Vigente desde 28/10/2026; caso de control CAPEX | `herramientas/precotizar.py`, `test_precotizar.py` |
| Plazo calculado y comparación con antecedentes (los corre `armar_cotizacion.py`) | Vigente desde 28/10/2026 | `herramientas/plazo.py`, `comparar_antecedentes.py` |
| Un comando para rearmar y otro para verificar todo | Vigente | `herramientas/actualizar_base.py`, `verificar_todo.py` (tiene que dar "TODO OK") |
| Dólar mensual 2024–2026 (oficial, mayorista, MEP, blue) | Vigente | `costos/dolar_mensual.csv/.xlsx`, `herramientas/dolar_mensual.py` |
| Índices de inflación (costo local en USD y CPI EE.UU.) desde ene-2024 | Vigente | `costos/indices_ajuste.csv`, `herramientas/indices_inflacion.py` |
| Peso y superficie de caños (ASME B36.10) | Vigente (calculado) | `tecnico/canos_peso_superficie.csv`, `herramientas/tablas_pesos.py` |
| Peso de bridas (B16.5) y accesorios (B16.9, B16.11) | Revisado el 28/10/2026 y corregido (márgenes: bridas ±15%, BW ±10–15%, forjados ±25%) | `tecnico/bridas_peso.csv`, `accesorios_peso.csv`, `pesos_LEEME.md` |
| Marcas aprobadas por cliente | **Borrador** (YPF completo; PAE, Pampa, Pluspetrol parciales) | `comercial/marcas_aprobadas.csv` + `_resumen.md` |
| Plazos de entrega de proveedores | **Borrador** (213 datos, 154 verificados) | `comercial/plazos_proveedores.csv` + `_resumen.md` |
| Catálogo de mano de obra y servicios (etapas 1 y 2) | Vigente: 562 servicios (181 precios de cotizaciones y tarifas + 467 de planillas de costo); 268 con tarifa unitaria; 5 sin precio | `precios/catalogo_servicios.*`, `herramientas/catalogo_servicios.py`, `buscar_servicio.py`, `test_catalogo_servicios.py` |
| Auditoría del catálogo de materiales | Hecha y corregida | `auditorias/2026-10-27_catalogo_materiales.md` |
| **Página web del cotizador** (Artifact en Claude, privada): lista de cotizaciones, buscador de materiales y servicios, calculadoras (soldadura, pintura, PH, RX), plazo, ofertas, firmantes, guardado automático con versiones, descarga en .zip o de a un archivo | Publicada el 28/10/2026; probada con la CAPEX (hoy USD 7.366,12 en el repositorio; la copia de la página del 28-10 tenía 7.620,59 por sus índices congelados) | https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ · `web/` (ver `web/LEEME.md`) |
| **Botones Claude y Chat nuevo** (29-10-2026): "Chat nuevo" crea una sesión limpia con el repositorio y la página limpia sola las suyas con más de 2 días sin uso: primero les pide consolidar lo aprendido en el repo y recién después las archiva; "Claude ↗" abre la sesión fija de Claude Code (con el repositorio y control total sobre la app) en una ventana chica aparte, como chat flotante. El chat dentro de la página y la pestaña Pedidos se sacaron (los planos y listas se le pasan directo a Claude Code) | Vigente | `web/src/asistente.js`, `web/LEEME.md` (Botón Claude) |
| Mejoras de la página (28/10/2026): buscador general por texto y selección múltiple en los catálogos; sección Catálogos sin cotización abierta; avisos en cada renglón; filtro y orden de los ítems; deshacer y rehacer (Ctrl+Z / Ctrl+Y); vista previa de informe y ofertas; antecedentes parecidos (P8) en Resumen; versión para celular | Publicado | `web/src/` |
| **MO y servicios por rubro de fabricación** (página): skid (estructura), piping, granallado y pintura, radiografía y END, procedimientos, prueba hidráulica, horas de ITT, transporte y otros. Cada rubro: ficha (kg, juntas, pulgadas, m², placas, procedimientos, litros, medidas) y costo **por antecedentes** (tarifa del historial o tarifa propia × cantidad de la ficha; piping por pulgada o por kg) o **manual** (precio del tercero con fuente). Todo por equipo | Vigente desde 29-10-2026 (repo y página) | `herramientas/ficha_rubros.py`, `web/src/rubros.js`, `web/src/ficha.js`, `ficha_rubros.md` en cada cotización |
| **Ficha calculada en la página y botón Recalcular**: soldaduras, kg, m², placas y procedimientos con las mismas fórmulas que Python, sin IA; completa familia y atributos con el código de catálogo | Vigente desde 29-10-2026 | `web/src/ficha.js`, prueba `web/probar_ficha.js` (en `verificar_todo.py`) |
| **Tablas de pesos ampliadas** (borrador sin revisar): estructura (laminados, ángulos, planchuelas, barras, perfiles de chapa, tubos, chapas, inox), olets, bridas B16.47 y B16.36, figuras 8, espárragos, caños inox y complemento B36.10, accesorios complementarios. Sin tabla: **peso aproximado** por volumen × densidad, marcado. Instrumentos no se pesan | Integradas al cálculo de kg (29-10-2026) | `conocimiento/tecnico/*_LEEME.md`, `herramientas/peso_aproximado.py` |
| Listas de precios nuevas que llegan por pedidos | Vigente (vacío) | `precios/listas_nuevas.csv` (lo lee `catalogo_materiales.py`) |
| Tarea semanal (lunes 7:37, hora Argentina): dólar e índices a la página, pedidos pendientes y respaldo de sus cotizaciones en `cotizaciones_web/` | Creada el 28/10/2026 | `web/LEEME.md` (sección Tarea semanal) |

**Consolidado al 28-10-2026 (fin del día):**
- **Controles:** 9 casos `cotizaciones/CTRL-*` medidos con `herramientas/correr_controles.py` (`cotizaciones/controles_resultado.md`). Al 29-10-2026: TS01 +2%, P02 +4%, SK01 −17%, CA01 +3%, C01 +10%, M01 −23%, P01 +3% sin lo que queda SIN PRECIO, F01 −35% y T01 −35% (faltan horas de antecedentes de su tipo). Los totales quedan fijos en `cotizaciones/controles_esperado.json` y `verificar_todo.py` avisa si se mueven.
- **Regla P4 ter (Matías):** sin referencia ni pieza parecida, el precio va en 0 y se pide cotización; `verificar_computo.py` lo controla y el chat de la página la cumple. El control de la CAPEX pasó a 7.366,12.
- **Cotizaciones en borrador (en el repo y en la página):** CAPEX OQ8209, YPF Lic 69343 (2), Camuzzi CP 24578 (3: skid de regulación, puente de medición, separador coalescente preliminar). Detalle en `cotizaciones/README.md`.
- **Acceso:** Ricardo Álvarez (`ricardoalvarezu2-cyber`) invitado como colaborador del repo (escritura); falta que acepte y que se le comparta la página con edición.
- Limpieza: se borraron las copias de trabajo de los agentes de control (`.claude/worktrees`, 911 MB, ya volcadas en main).

**Caso de control 2 (28-10-2026):** `cotizaciones/CTRL-F01_INARTECO_FM2_S300` (filtro, otra familia): la precotización automática sin completar da −75% contra el costo real; lo que falta es radiografía (40%), horas de ingeniería/calidad/montaje (16%) y piezas sin precio. Herramienta: `comparar_historico.py`. **Chapa y perfiles por kg: hecho (28-10-2026)**, `precios/acero_por_kg.csv` en el catálogo y en la precotización (en CTRL-F01 las piezas de chapa dan −10% contra la planilla). **Horas de ingeniería, calidad y montaje: hecho (28-10-2026)**: `costos/horas_por_equipo.csv` (34 equipos vigentes de 18 planillas 2025–2026, criterios en `horas_por_equipo_LEEME.md`) y `herramientas/estimar_horas.py` (antecedente más parecido por tipo, diámetro y costo de materiales; ingeniería y calidad se reparten entre las unidades; el montaje incluye la PH). `precotizar.py` las carga como estimadas: en CTRL-F01, sin usar el propio proyecto, da USD 592 contra 720 reales (−18%) y el total pasa de −75% a −61% (lo que falta es la radiografía, que depende del pliego, y 4 piezas sin precio). Pendiente: elementos filtrantes y refuerzos tipo poncho; mejorar los atributos de la familia Perfiles (tipo y espesor) sin cambiar los códigos existentes.

**REGLA CRÍTICA — descripción del cliente (Matías, 29-10-2026):** en la descripción va siempre, sin excepción, el texto exacto del documento del cliente (plano, pliego o planilla), tal cual figura: sin corregir, traducir, abreviar ni agregar palabras ("RF", "radio largo", marcas, normas). Lo mismo con el material: se cotiza lo que pide el cliente. Lo que agrega ITT va en la columna `nota` de `lista_materiales_plano.csv`; el Ø va aparte. Si el cliente no indica cantidad y ITT la calcula, se aclara siempre en `cantidad_origen` ("El cliente no indica cantidad: calculada por ITT según el plano / la ET") y la oferta la marca con (*). Se copia de `pedido/transcripcion.json` y `verificar_computo.py` da error si no coincide.

**Similares solo de la misma serie y la misma norma (Matías, 29-10-2026):** `buscar_material.py` (y con él `precotizar.py`) ya no ofrece como similar una pieza de otra serie (#3000 por #2000, #600 por #900) ni de otra norma; si el renglón no dice la serie, tampoco (salvo bulonería, donde manda la medida). Sin similar válido queda SIN PRECIO y se pide cotización. Controles movidos a propósito: F01 2.907 → 2.892, TS01 85.243 → 84.055, SK01 71.487 → 71.864.

**Caso de prueba:** COT26-1003-001 CAPEX OQ8209 (borrador, no enviada; su estado está en su `bitacora.md` y en `cotizaciones/README.md`).

**Índices congelados (28-10-2026):** al pasar una cotización a revisado, la página guarda en `cot.indices_congelados` los índices de ese día; desde ahí el precio no cambia cuando la base suma un mes. Al volver a borrador se descongelan. `armar_cotizacion.py`, el motor JS, la planilla y el informe usan los congelados si están. La CAPEX (caso de control) tiene los del 28-10-2026, así el control de la página no se mueve (en el repositorio, desde la regla P4 ter, el control es 7.366,12). La oferta económica muestra una fila de flete cuando se incluye.

**Revisión con agentes (28-10-2026):** informes en `conocimiento/auditorias/2026-10-28_revision_*.md` (arquitectura, usuario, chat, datos). Hechos: plantilla de oferta neutra, números en formato argentino en los campos, estados con control (aprobar pide quién), ids únicos en el chat, índices congelados, flete en la oferta. Siguen: endurecer el chat, avisos y UX, y los datos (manómetro CAPEX, pesos globo 14" #600, factores de soldadura, alertas de precios fuera de rango, pdf.js).

## 2. Decisiones tomadas (vigentes)

| Fecha | Decisión | Quién | Detalle |
|---|---|---|---|
| 28-10-2026 | Las válvulas Taval (empresa del grupo) llevan un factor de venta propio, igual para todas las de la cotización, por defecto 1 | Matías | `parametros.FTV`; cada válvula con `"taval": true`. En la planilla, fila "Válvulas Taval" con su contingencia y parámetro en B14. Como en la PC0 de YPF Lic 69343 |
| 27/10/2026 | No omitir información por privacidad: el repo es privado | Matías | `CLAUDE.md` |
| 27/10/2026 | Nunca enviar nada al cliente. Estados borrador → revisado → aprobado → enviado | Matías | `procedimiento_cotizacion.md` |
| 27/10/2026 | Factores: materiales 1,35; MO y servicios 1,35; 1,40 solo para MO vendida sola. El factor final lo define la dirección | Matías | `guia_cotizacion.md` |
| 27/10/2026 | Ajuste por inflación con índices mensuales: CPI EE.UU. para materiales, IPC ÷ dólar para MO y servicios | Matías | `indices_ajuste.csv` |
| 27/10/2026 | Dos etapas: preliminar (antecedentes y similares) → Compras → definitivo. Matías no compra | Matías | `guia_cotizacion.md` |
| 27/10/2026 | Antecedentes: solo 2025–2026 en el índice (2021–2024 no se indexa) | Matías | `buscar_antecedentes.py` |
| 30-10-2026 | **Automatizaciones sin riesgo (solo avisan o arreglan herramientas):** `verificar_origen.py` (aviso de precio que no figura en su documento; lo corre `armar_cotizacion.py`), `validar_fichas.py` (lo corre `consolidar_fichas.py`), `consolidar_fichas.py` ya no pisa los aprendizajes escritos a mano, `revisar_cambio_busqueda.py` (cambios del buscador contra una versión anterior) y `subir_a_main.py` | Matías ("automatizá todo eso") | `conocimiento/README.md` |
| 30-10-2026 | **Ciclo ante errores:** anotar → corregir → repensar el proceso → auditoría independiente automática (sin esperar a que Matías la pida). Controles nuevos: error por referencia incompatible en `verificar_computo.py` y resultados aceptados del buscador en `verificar_todo.py` | Matías | `CLAUDE.md` |
| 30-10-2026 | **Compatibilidades revisadas:** un similar vale solo si es igual o superior en todo (resistencia, rating, tenacidad, servicio); sin material en el catálogo no es similar; bridada no es referencia de roscada. Revisión independiente aplicada | Matías ("revisar las compatibilidades") | `tecnico/compatibilidades_LEEME.md` |
| 30-10-2026 | **Precios cargados por el usuario:** un precio que confirma Matías (aunque sea hablado con el proveedor, sin documento) es firme, no estimado. Va en `precios/precios_usuario.csv` (quién lo confirmó y cómo se obtuvo); los servicios entran al catálogo de servicios. Primer caso: RX ARS 850.000 por visita (hasta 45 placas) + ARS 15.000 por placa, sin IVA | Matías | `precios/precios_usuario_LEEME.md` |
| 30-10-2026 | **P8 costo contra costo:** la comparación con antecedentes usa el costo por equipo y el reparto materiales / MO y servicios de la ficha (solo si la ficha lo permite sin ambigüedad: un único equipo con precio); el precio de venta queda como referencia "solo venta". El costo del antecedente va a su fecha, sin ajustar | Matías | `comparar_antecedentes.py`, `web/src/antecedentes.js` |
| 30-10-2026 | **Aclaración:** lo que se prohíbe es programar algo que pueda generar datos falsos o erróneos. El análisis y la corrección con IA (revisada) sí están permitidos | Matías | — |
| 30-10-2026 | **No se automatiza nada que tenga riesgo, aunque sea mínimo, de generar información errónea, imprecisa o irrelevante.** Siguen con IA y revisión: transcripción de planos y pliegos, textos de oferta, fichas de carpetas, explicación de diferencias con antecedentes, verificación de precios contra el original y la tarea semanal de índices. La MO de recipientes por kg no se incorpora | Matías | — |
| 30-10-2026 | **Compatibilidades de la norma en el buscador de materiales:** no es similar lo que la norma no permite reemplazar (material de otra clase o de otro grupo B16.5, otra cara RF/FF/RTJ, otra rosca NPT/BSPT o roscado por SW, otro schedule en caños y accesorios a tope, sin NACE si el pedido es para servicio ácido). Se aceptan los reemplazos hacia arriba que la norma admite (LF2 por A105, 316L por 316, B7M por B7). Sin normas compradas: reglas de datos públicos y criterio técnico, documentadas | Matías | `tecnico/compatibilidades_LEEME.md`, `herramientas/compatibilidad.py`, `web/src/busqueda.js` |
| 29-10-2026 | **Criterio de antecedentes igual para todas las familias y todo el catálogo:** subtipo (30) > texto con sinónimos (25) > tamaño (15; Ø del cuerpo en recipientes) > serie (12) > material (8) > unión (5) > cliente (4); un dato que falta no resta; con menos de 5 del mismo subtipo se muestran aparte las carpetas sin ficha 2021–2024 (sin precios, solo diseño). Familia y subtipo de una cotización: `equipo.familia`/`equipo.subtipo` o el título, nunca los ítems | Matías ("ok" a la propuesta, pidiendo que sirva para todas las familias); umbral de 5 confirmado por Matías el 29-10-2026 | `guia_cotizacion.md` §3, `buscar_antecedentes.py` |
| 27/10/2026 | Catálogo de materiales separado por familia, último precio con fecha y ruta de origen | Matías | `catalogo_materiales.py` |
| 27/10/2026 | La marca es un renglón aparte en válvulas e instrumentos; se puede elegir con `--marca` | Matías | `buscar_material.py` |
| 27/10/2026 | **Todo precio sin IVA**: con IVA se divide por la alícuota; si no dice, sin IVA | Matías | `catalogo_materiales.iva_de` |
| 27/10/2026 | **Dólar para convertir: promedio mensual del oficial BNA, venta**; si el documento dice su tipo de cambio, ese | Matías | `fuentes.md`, `dolar_mensual.csv` |
| 28/10/2026 | 2025 y 2026 con dólar oficial (desde el 14/04/2025 la brecha es menor al 2%) | Propuesta aceptada en la conversación | — |
| 27/10/2026 | Compras del stock anteriores a 2022 no se usan (precio maestro nov-2024) | Criterio técnico (documentado) | `fuentes.md` |
| 28/10/2026 | **Valores en USD anteriores al 14/04/2025 (cepo) sin tipo de cambio explícito: se llevan a su valor más verosímil y quedan como ESTIMADO** (pedir cotización para el definitivo): precio maestro del stock × 0,64 (calibrado con 14 materiales contra costos reales 2025–2026); otros valores × oficial ÷ blue del mes; compras del stock siguen descartadas. Si hay un valor confiable más nuevo, manda ese | Matías ("ajustalo al valor más verosímil") | `catalogo_materiales.factor_cepo`, `catalogo_servicios.py` |
| 28/10/2026 | Sin renglones de IVA en la planilla ni en el informe: solo precios sin IVA | Matías | `armar_cotizacion.py`, `plantillas/informe_cotizacion.html` |
| 28/10/2026 | Página web en Claude, sin usuarios ni registro de resultados; dólar e índices una vez por semana (lunes) por tarea programada; guardado automático y respaldo semanal en GitHub; descarga en .zip y de a un archivo; firma del cotizador (la imagen solo en ofertas aprobadas) | Matías | `web/LEEME.md` |
| 28/10/2026 | El ajuste por inflación lleva cada precio a la **fecha de referencia de la cotización** (no a "hoy" automático): una cotización calculada no cambia sola de precio. Los meses sin dato oficial (INDEC/BLS) quedan estimados y la tarea semanal los reemplaza | Criterio explicado a Matías (sin objeción) | `web/src/motor.js`, `indices_ajuste.csv` |
| 28/10/2026 | Respuestas cortas | Matías | `CLAUDE.md` |
| 28/10/2026 | El repositorio sigue **privado** (tiene sueldos, costos, márgenes y contactos). Para que otra persona trabaje con su agente: sumarla como colaboradora en GitHub y darle edición en la página | Recomendación aceptada | — |
| 28/10/2026 | Integrar un chat con Claude en la página y un "Mandar a Claude Code" (desde el chat o con un botón) que procese planos, P&ID, pliegos y listas de precios sobre el repositorio y deje el resultado en borrador | Matías (idea), plan por etapas abajo | — |
| 28/10/2026 | ~~Control total del chat de la página~~ (reemplazado el 29-10-2026 por el chat con Claude Code): crea, abre, duplica y modifica cotizaciones (datos, ítems, plazo, oferta), usa las calculadoras, carga artículos y MO nuevos (con documento, proveedor y fecha; ARS al BNA del mes; IVA descontado) en `catalogo_nuevo` y descarga. Excepciones: no aprueba ni marca enviada; borrar y pasar a revisado los confirma el usuario con un botón; sin documento no carga precios | Matías ("control total") | `web/src/asistente.js`, `web/LEEME.md` |
| 28/10/2026 | **Fechas a la vista siempre DD-MM-AAAA**; adentro AAAA-MM-DD. Aplicado en la página (también los campos de fecha se escriben DD-MM-AAAA), informe, planilla, lista para Compras, ofertas, avisos del catálogo y comparación con antecedentes | Matías | `numeros.a_vista`, `Documentos.fecha` |
| 28-10-2026 | **Sin referencia ni producto parecido no se adivina el precio:** va en 0 y se pide cotización | Matías | `procedimiento_cotizacion.md` P4 ter, `verificar_computo.py` |
| 28-10-2026 | Listas que pasa Ventas: se guardan en `fuentes_originales/listas_vendedor/<fecha de carga>/` como cargadas por el vendedor; cada precio conserva la fecha del documento | Matías | `herramientas/listas_vendedor.py`, `fuentes.md` |
| 28-10-2026 | Válvulas Taval: costo = Lista 30 × 0,52 (factor de las planillas TAVAL/72 y /78) | Criterio de las planillas (documentado) | `pesos_valvulas.py`, `precios/taval_lista30.csv` |
| 28-10-2026 | Sin antecedente de horas del mismo tipo y tamaño, la precotización **no suma horas** y avisa (antes tomaba otro tipo de equipo) | Criterio técnico (controles) | `estimar_horas.py` |
| 28-10-2026 | Prefabricado de piping: `parametros.modo = "prefabricado"` (pulgada diametral base sch 40, tarifa de terceros, +5% rechazos, pintura aparte, sin horas); materiales del cliente con la columna `provee` = cliente | Criterio técnico (CTRL-CA01) | `precotizar.py`, `guia_cotizacion.md` |
| 28-10-2026 | MO, pintura, END y transporte: opción global por rubro, siempre **por equipo** (la cantidad multiplica al final); MO del piping y de la estructura **por separado**, con ficha de cada uno | Matías | `guia_cotizacion.md`, `ficha_rubros.py` |
| 29-10-2026 | **Manda el repositorio; la biblioteca se alimenta solo con el botón** "Pasar al repositorio y a la biblioteca" (Resumen): sin revisar o sin aprobar avisa y pide confirmación; volver a incorporar reemplaza la versión anterior. Las 6 cotizaciones del repo salieron del catálogo y de los antecedentes hasta que se incorporen | Matías | `web/incorporar_base.py`, `herramientas/cotizaciones_base.py`, `biblioteca_cotizaciones/` |
| 29-10-2026 | **Números: punto de miles, coma decimal, 2 decimales** en todo lo que se ve y en los campos (los campos rechazan formatos ambiguos y explican por qué; al salir del campo se reescribe en el formato de la página) | Matías | `CLAUDE.md`, `numeros.fmt`, `Documentos.num`/`numeroDe` |
| 29-10-2026 | El botón Claude abre Claude Code (repositorio, control total sobre la app) en ventana aparte; enviado y envíos al cliente, nunca | Matías | `web/LEEME.md` |
| 29-10-2026 | MO y servicios: un ítem por rubro de fabricación con ficha y costo por antecedentes o manual; se sacaron la tabla general y las calculadoras sueltas | Matías | `guia_cotizacion.md` |
| 29-10-2026 | Piping por pulgada de soldadura o por kg; en cualquier rubro, tarifa propia con valor, fecha y proveedor | Matías | `web/src/rubros.js` |
| 29-10-2026 | Lo que no tiene peso en tabla se estima por volumen × densidad y queda marcado APROXIMADO; los instrumentos no se pesan (despreciable) | Matías | `peso_aproximado.py` |
| 29-10-2026 | Juntas a tope siempre enteras (redondeo hacia arriba); las pulgadas equivalentes pueden tener decimales | Criterio técnico (observación de Matías) | `precotizar.soldaduras` |
| 29-10-2026 | Respuestas más cortas: qué se hizo, errores y decisiones | Matías | `CLAUDE.md` |
| 29-10-2026 | **Números en las tablas:** precios con 2 decimales; CSV/JSON con punto decimal y sin miles (formato de máquina); Excel con celdas numéricas (`#,##0.00` precios, `#,##0.0###` técnicos); textos y notas con 1.234,56. Pos, códigos y claves quedan como texto | Matías | `numeros.precio_csv`, `numeros.celda_excel`, `auditorias/2026-10-29_numeros_tablas.md` |
| 28/10/2026 | No hay más información de precios que la ya entregada: el último precio se sigue eligiendo por fecha (no hay otras compras para preferir sobre la lista de Renard) | Matías | — |

## 3. Pendientes del proyecto

**Hace Claude** (aprobado el 28/10/2026: "el resto, dale para adelante")
1. ~~Catálogo de MO y servicios etapa 1~~ **Hecho (28/10/2026).**
2. ~~Etapa 2 de los catálogos~~ **Hecho (28/10/2026):** 2.492 renglones de 31 planillas de costo (`precios/planillas_costo_items.csv`, `herramientas/unir_planillas_costo.py`); 18 de los 49 proyectos marcados con planilla en el índice solo tienen precios de venta.
3. ~~Revisión independiente de los pesos~~ **Hecho (28/10/2026):** `auditorias/2026-10-28_pesos_bridas_accesorios.md`; errores corregidos.
4. ~~Vendor lists en el RAR de la Tanda 1~~ **No están** (revisado el 28/10/2026: la Tanda 1 solo trae las listas de YPF, ya cargadas; de PAE, Pampa y Pluspetrol solo hay referencias). Quedan en la carpeta completa `Z:\VENTAS\OFERTAS Y LICITACIONES` (1.Documentación de la licitación) o hay que pedirlas al cliente cuando se cotice para ellos.
5. ~~Integrar las tablas nuevas~~ **Hecho (28/10/2026):** `armar_cotizacion.py` corre `controles_tablas.py` y deja `controles_tablas.md` en cada cotización (kilos y m², plazo típico por rubro con aviso si supera el ofrecido, marcas del cliente). **Pesos de válvulas: hecho (28-10-2026)**, 383 pesos de la Lista 30 de Taval (`tecnico/valvulas_peso.csv`). Falta: uniones dobles y bujes reductores (no hay tabla).

**Qué hace la IA y qué es automático (decisión de Matías, 28/10/2026).** Lo que varía entre cotizaciones, clientes y proveedores lo sigue leyendo la IA: planos, pliegos, especificaciones y las cotizaciones que mande Compras (en el formato que vengan; no se usa un formato fijo de respuesta). Lo automático empieza cuando esos datos ya están en los formatos internos (`lista_materiales_plano.csv` y `cotizacion.json`): búsqueda en el catálogo, soldaduras, m², plazo, comparación con antecedentes, sumas y controles. El programa propone y marca; siempre revisa una persona o la IA.

Hecho (28/10/2026): `precotizar.py` (materiales, soldaduras, pintura, PH, RX) · `plazo.py` (acopio + taller sin superponer, margen 15–20%, plazo real de la familia) · `comparar_antecedentes.py` (P8 contra los 5 más parecidos) · control de carga en `verificar_computo.py` (fecha válida, "con IVA", sin precio) · `verificar_todo.py` y `actualizar_base.py`. Descartado: lectura automática de planos y pliegos, y formato fijo para las respuestas de Compras.

**Auditoría completa (29-10-2026)** — informes en `conocimiento/auditorias/2026-10-29_*.md` (arquitectura, cadena de datos, automatizaciones, diseño y UX, estructura de tablas, prueba de usuario con dislexia: 5/10). Pendiente corregir; lo más grave:
1. ~~Transporte con precio sin reflejar en resumen y oferta~~ Hecho (29-10-2026).
2. ~~Plazo menor que el calculado sin bloqueo; oferta sin los datos cargados~~ Hecho (29-10-2026): sin justificación no salen ofertas (YPF 713/708 y Camuzzi 001 quedaron sin ofertas hasta corregir o justificar el plazo).
3. Precios de la PC0 YPF con fecha supuesta (10-10-2026) entraron al catálogo como último precio de 45 materiales (hecho 29-10-2026: ahora son "estimado (fecha supuesta)"). ~~Los borradores alimentan la base~~ Hecho: solo entra lo incorporado con el botón.
4. ~~Corridas simultáneas corrompen los catálogos~~ Hecho (29-10-2026): candado y escritura atómica (`herramientas/candado.py`).
5. ~~Formato de números distinto entre página e informe~~ Hecho (29-10-2026): todo 1.234,56.
6. ~~Ítems sin código de catálogo; `semilla.py` pisaba lo cargado en la página~~ Hecho (29-10-2026): `codigo` en cada fuente con aviso de precio más nuevo; `semilla.py --previo`.
7. ~~Página: subtotal vacío, diálogos, avisos, MO sin costo, celular~~ Hecho (29-10-2026).
8. Tablas: pesos argentinos en columnas de USD sin moneda (índice de proyectos), 129 materiales sin unidad, claves de peso repetidas sin `vigente`, IVA/unidad/moneda en texto libre.
9. ~~Control de la CAPEX en la documentación y controles CTRL fuera de `verificar_todo.py`~~ Hecho (29-10-2026): CAPEX 7.366,12 en todos lados; los 9 casos CTRL se controlan contra `cotizaciones/controles_esperado.json` (tolerancia 0,5%) y `probar_busqueda.js` entró al control.
Decidido (Matías, 29-10-2026): manda el repositorio; la biblioteca se alimenta solo con el botón; números 1.234,56.

**Camuzzi CP 24578** (28-10-2026; COT26-0135-001/002/003 en borrador y cargadas en la página)
1. Reguladoras y monitoras 3" #150 sin OPSO (hoy Tormene #300 con OPSO de referencia) y explicar contra CAMUZZI/23 (24.454 en 2025).
2. Filtro FM-6 #150: costearlo por componentes o cotizarlo.
3. Separador: pedir a Camuzzi la especificación; caudal por elemento de 0,3 µm a Gora/Pall; memoria de cálculo y esquema (se entregan con la oferta).

**Comparación con la planilla del vendedor (YPF Lic 69343 PC0, 28-10-2026)** — conceptos que la app todavía no tiene:
**Por ahora no (Matías, 29-10-2026):** puntos 1 a 3.
1. Montaje + control dimensional + desmontaje como renglón propio.
2. Repuestos de precomisionado, comisionado y puesta en marcha (aparte de los de 2 años).
3. Hoja de alcance SI/NO (recipiente, plataforma, eléctrico, aislación, tracing, embalaje).
4. Factor de transporte y caución: se ajusta en Datos (Matías, 29-10-2026).
5. ~~Soldaduras de los skids YPF~~ Recalculadas el 29-10-2026 (713: 988,83 pulg; 708: 456,03 pulg) en el repo y en la página.

**Antecedentes (29-10-2026)**
0. Página republicada con el criterio nuevo el 29-10-2026; `test_antecedentes.py` controla que dé lo mismo que Python.
1. ~~Fichas que faltaban de 2025–2026~~ Hechas el 29-10-2026 (Matías: "armalas"): TAVAL/37 (coalescente FC-231 YPF, cuerpo 32" #600, USD 529.204,77, factor 1,31), ENDRESS HAUSER/17 (ganada, OC 1007502798) y /28, ALUAR/1 (solo cotización de instrumentos, sin oferta ITT) y AESA/43 (ganada). FILTRON y Los Guindos ya tenían ficha: el índice histórico ahora reconoce fichas hechas sobre una subcarpeta. `indice_proyectos.py` avisa si vuelve a faltar alguna.
2. 17 proyectos sin subtipo (manifolds y skids genéricos, servicios): sumar subtipos en `SUBTIPOS` cuando aparezca un caso.
3. El "precio unitario principal" del índice es el renglón más caro de la oferta; en ofertas con varios equipos puede no ser el equipo comparado (por eso tantos "otra escala"). Falta guardar el precio por equipo en las fichas.
6. **Horas de recipientes 2025–2026 (30-10-2026):** las planillas de 2025–2026 con horas ya estaban todas en `horas_por_equipo.csv` salvo AESA/44 (10 recipientes, servicio de MO): no trae horas propias de fabricación (la columna "QTY HH" son kg) pero sí MO de Ledesma por equipo, kg, calidad 160 h y PH 108 h. Se sumó a `costos/tarifas.csv` como MO de recipiente por kg (3,1 a 8,0 USD/kg según tamaño, tercero) y horas de calidad y PH por recipiente. **No se conecta a la precotización (Matías, 30-10-2026):** la MO por kg varía demasiado (3,1 a 8,0 USD/kg; con curva por tamaño, −25% a +40%) y sale de una sola fuente. Queda solo como referencia en `tarifas.csv`.
7. ~~Fichas con precios de proveedor cargados como ítems de ITT~~ **Corregidas el 30-10-2026** (revisión con IA contra los originales, permitida por Matías): eran 20 ítems en 8 fichas (CAMUZZI/27, APSA/9, /12 y /16, PHOENIX/2, PLUSPETROL/8, TAVAL/74, TECPETROL/12), todas carpetas con solo cotizaciones de proveedores y sin oferta de ITT: `items` vacío, monto null, los precios quedan en `proveedores`. Quedan avisos menores (fichas sin fecha de oferta, 4 sin moneda) en `auditorias/2026-10-30_validacion_fichas.md`.
5. **Planillas 2021–2024 (29-10-2026, pedido de Matías):** se leyeron las 59 carpetas con planilla de costo buscando horas y estructura. **No traen horas** (la MO es un monto global): `horas_por_equipo.csv` no cambió y los controles F01/T01 siguen en −35%. Quedó la estructura de costo de 103 equipos en `costos/estructura_costo_historica.csv` (solo proporciones, del cepo; ver su LEEME). Para las horas de recipientes, la fuente posible son planillas 2025–2026 que todavía no están en `horas_por_equipo.csv` o el detalle de montaje de cada cotización nueva.
4. El Ø del cuerpo está en 13 de 158 fichas: completarlo al hacer o revisar fichas de recipientes.

**Cotizaciones cargadas revisadas con las reglas de compatibilidad (30-10-2026):** solo 2 renglones usaban un similar que la norma no admite: COT26-0135-001 pos 17 (cupla BSPT → NPT, mismo precio) y COT26-0135-003 pos 15 (válvula SW-roscada → SIN PRECIO). El resto no cambia; no hace falta rehacer las cotizaciones. Para revisar otras: comparar cada renglón con `compatibilidad.incompatible` (como en este chat) o volver a correr `precotizar.py` y comparar.

**Catálogo sin material (30-10-2026):** 1.407 renglones del catálogo de materiales no tienen el material cargado y, con las reglas revisadas, no sirven como similar (quedan SIN PRECIO). Completar el material leyendo la descripción o el original (tarea de IA con revisión) bajaría los SIN PRECIO.

**Flujo unificado (30-10-2026)** — hecho: frenos de la oferta, doble lectura (CAPEX y Camuzzi 001/002), matriz de requisitos (CAPEX), cantidad del cliente en `verificar_computo.py`, 18 errores sembrados. Pendiente:
1. Matriz de requisitos de Camuzzi 001, 002 y 003 e YPF 713/708; transcripción del plano del cliente de YPF (en el repositorio solo está la planilla PC0 del vendedor).
2. Notas del plano de la CAPEX en la matriz (solo se cargó la OR) y las 3 consultas abiertas: documento 17009 contra plano 23001, condición de pago "Habitual", esféricas de cuerpo enterizo.
3. Cargar `validez_hasta` en las fuentes `cot`; S02 de la CAPEX (costo propio de planta) está como `cot` y frena por "vencida".
4. La página todavía no tiene los frenos nuevos (solo el de plazo): sus ofertas pueden salir sin ellos.
5. Doble método por USD/kg: las fichas de antecedentes no tienen kg; hoy el contraste es costo contra costo del antecedente.
6. Medir contra el costo real (los casos CTRL siguen congelados contra lo que da la app) y sumar siembras para los errores que no cubre (factor 1,40, alcance de MO, tablas técnicas).

**Para decidir con Matías (30-10-2026)**
1. Separador Camuzzi (COT26-0135-003): ~~ingeniería y calidad a 250 h~~ hecho (Matías, 30-10-2026). Falta pedir a Ledesma la cotización real con el diseño, confirmar las placas de RX con el mapa de soldaduras y cotizar la válvula esférica 1/2" roscada S-2000 (pos 15, sin precio por la regla de compatibilidad).

**Abiertos al 29-10-2026 (para decidir con Matías)**
1. Costos de procedimientos sin antecedente: WPS/PQR, calificación de soldadores, prueba hidráulica y pintura (hoy solo RX y LP, USD 250 cada uno).
2. Sacar de Datos los campos viejos de flete (flete en el precio, flete ARS, embalaje, factor flete): el transporte ya está en MO y servicios.
3. ~~Llevar la rama de trabajo a `main`~~ Resuelto: todo trabajo termina en `main` sin PR (Matías, 29-10-2026). Transporte: la ficha quedó con precio, destino y transportista (29-10-2026).

**Tablas de pesos y botón Recalcular (29-10-2026)**
1. ~~Integrar las tablas nuevas al cálculo de kg~~ **Hecho (29-10-2026):** accesorios complementarios, tees de reducción, olets y espárragos.
2. ~~Botón "Recalcular"~~ **Hecho (29-10-2026):** `web/src/ficha.js` calcula la ficha en la página igual que Python (`web/probar_ficha.js`); completa familia y atributos con el código de catálogo. Las 6 cotizaciones de la página quedaron con atributos y datos del plano; skids YPF con la soldadura nueva.
3. ~~Pedir el peso de tees Sch 60~~ Descartado (Matías, 29-10-2026).
4. En Sch 40 de 12"+ y Sch 80 de 10"+ preferir Hackney Ladish sobre Texas Flange/Weldbend (pesos que no siguen el espesor).

**Controles de la precotización** (28-10-2026, segunda tanda corregida: ver `auditorias/2026-10-28_controles_4_agentes.md`)
1. ~~Cargar horas de antecedentes que faltan~~ Descartado por ahora (Matías, 29-10-2026).
2. Instrumentos: sumar accesorios de la hoja de datos (RTD y vaina del TT, manifolds, bloqueo y purga).
3. RX por jornada (placas por servicio) y propuesta de caución, repuestos y transporte (hoy solo aviso).

**Página web: plan por etapas** (propuesto el 28/10/2026; cada etapa se usa antes de pasar a la siguiente)
1. **Probar la página como está:** Matías arma 2 o 3 cotizaciones reales y completa su firmante (teléfono, celular, email, imagen de la firma). Revisar la primera tarea semanal (lunes 2/11).
2. ~~Subir archivos desde la página~~ **Hecho (28/10/2026):** sección Pedidos. Detalle original: → quedan "pendientes de procesar" en la base (`assets` + colección de pedidos); se procesan en un chat o el lunes, y en la página pasan a "incorporado" o "con dudas".
3. ~~Chat en la página~~ **Hecho (28/10/2026), falta que Matías lo pruebe con su cuenta** (en la prueba local se simuló Claude):: ve la cotización abierta, busca en los catálogos, carga y corrige ítems, explica avisos, propone la lista de materiales desde la imagen de un plano. No toca GitHub. Usa la cuenta de quien la usa.
4. ~~"Mandar a Claude Code"~~ **Hecho y probado de punta a punta (28/10/2026, pedido `prueba-circuito`):**: la página manda el pedido y el archivo a una sesión de Claude Code con el repositorio (capacidad `mcp`, conector Claude Code Remote); la sesión arma la cotización o actualiza el catálogo según el procedimiento, deja el resultado en borrador en la página y lo sube a GitHub. Estado del pedido en la página: en proceso / listo / con dudas.
5. **Sumar a otra persona:** colaboradora en GitHub + edición en la página; probar su agente con una cotización de control (CAPEX = 7.366,12). Ojo: ve todos los costos; la imagen de firma hoy solo la sube quien tiene edición.
6. **Cierre:** ver "Al terminar el proyecto".

**Al terminar el proyecto** (decisión de Matías)
1. Confirmar con Compras los precios sospechosos de la auditoría (columna `alerta`).
2. Instalar la herramienta en la PC de Matías, recién cuando esté completa y funcionando al 100%.

**Descartado por ahora** (decisión de Matías, 28/10/2026): escalas UOM, tasa de interés / costo financiero, plazos de pintura y END, reporte de compras 2021–2024 en pesos (además cae en el período con cepo).

## 5. Cómo seguir en un chat nuevo

1. Leer `CLAUDE.md`, este archivo y `conocimiento/RESUMEN.md`.
2. Para cotizar: skill `cotizar` + `guia_cotizacion.md` + `procedimiento_cotizacion.md` + `errores_y_lecciones.md`.
3. Después de cualquier cambio en herramientas o datos: `python herramientas/verificar_todo.py` (tiene que dar "TODO OK"). Para rearmar toda la base: `python herramientas/actualizar_base.py`.
4. Al terminar: actualizar este archivo, commit y push (lo que no se sube se pierde).
