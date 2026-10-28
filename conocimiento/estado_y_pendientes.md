# Estado del cotizador, decisiones y pendientes

**Leer al empezar cada chat.** Es la memoria del proyecto entre sesiones: qué está hecho, qué se decidió, qué falta.

**Objetivo: construir el cotizador automático.** Las cotizaciones (por ahora la CAPEX) son casos de prueba para armar y validar el proceso; sus pendientes no son pendientes del proyecto. Actualizado al 28/10/2026.

## 1. Qué hay hoy

| Pieza | Estado | Dónde |
|---|---|---|
| Procedimiento de cotización (P1–P10) y guía paso a paso | Vigente | `procedimiento_cotizacion.md`, `guia_cotizacion.md`, skill `.claude/skills/cotizar/` |
| Motor determinístico: cómputo, planilla con fórmulas, informe HTML con descargas, lista para Compras, ofertas técnica y económica | Vigente | `herramientas/armar_cotizacion.py`, `generar_oferta.py`, `lista_compras.py`, `verificar_computo.py` |
| Índice de proyectos 2025–2026 y buscador de antecedentes | Vigente (158 proyectos) | `comercial/indice_proyectos.csv`, `herramientas/buscar_antecedentes.py` |
| Catálogo de materiales con marca, unidad, IVA y alertas | Vigente: 3.319 materiales (1.005 con precio ESTIMADO del cepo; 132 sin precio) | `precios/catalogo_materiales.*`, `herramientas/catalogo_materiales.py`, `buscar_material.py`, `test_catalogo.py` |
| Lector único de números y fechas | Vigente | `herramientas/numeros.py` |
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
| **Página web del cotizador** (Artifact en Claude, privada): lista de cotizaciones, buscador de materiales y servicios, calculadoras (soldadura, pintura, PH, RX), plazo, ofertas, firmantes, guardado automático con versiones, descarga en .zip o de a un archivo | Publicada el 28/10/2026; probada con la CAPEX (USD 7.620,59 en la página y en la planilla que arma) | https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ · `web/` (ver `web/LEEME.md`) |
| Chat con Claude en la página y Pedidos para Claude Code (subir plano, P&ID, pliego o lista; la sesión fija los procesa con `web/LEEME.md` y deja el resultado en la página) | Publicado el 28/10/2026 | `web/src/asistente.js`, `web/LEEME.md` (Pedidos desde la página) |
| Mejoras de la página (28/10/2026): buscador general por texto y selección múltiple en los catálogos; sección Catálogos sin cotización abierta; avisos en cada renglón; filtro y orden de los ítems; deshacer y rehacer (Ctrl+Z / Ctrl+Y); vista previa de informe y ofertas; antecedentes parecidos (P8) en Resumen; versión para celular | Publicado | `web/src/` |
| Listas de precios nuevas que llegan por pedidos | Vigente (vacío) | `precios/listas_nuevas.csv` (lo lee `catalogo_materiales.py`) |
| Tarea semanal (lunes 7:37, hora Argentina): dólar e índices a la página, pedidos pendientes y respaldo de sus cotizaciones en `cotizaciones_web/` | Creada el 28/10/2026 | `web/LEEME.md` (sección Tarea semanal) |

**Caso de prueba:** COT26-1003-001 CAPEX OQ8209 (borrador, no enviada; su estado está en su `bitacora.md` y en `cotizaciones/README.md`).

## 2. Decisiones tomadas (vigentes)

| Fecha | Decisión | Quién | Detalle |
|---|---|---|---|
| 27/10/2026 | No omitir información por privacidad: el repo es privado | Matías | `CLAUDE.md` |
| 27/10/2026 | Nunca enviar nada al cliente. Estados borrador → revisado → aprobado → enviado | Matías | `procedimiento_cotizacion.md` |
| 27/10/2026 | Factores: materiales 1,35; MO y servicios 1,35; 1,40 solo para MO vendida sola. El factor final lo define la dirección | Matías | `guia_cotizacion.md` |
| 27/10/2026 | Ajuste por inflación con índices mensuales: CPI EE.UU. para materiales, IPC ÷ dólar para MO y servicios | Matías | `indices_ajuste.csv` |
| 27/10/2026 | Dos etapas: preliminar (antecedentes y similares) → Compras → definitivo. Matías no compra | Matías | `guia_cotizacion.md` |
| 27/10/2026 | Antecedentes: solo 2025–2026 en el índice (2021–2024 no se indexa) | Matías | `buscar_antecedentes.py` |
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
| 28/10/2026 | **Control total del chat de la página**: crea, abre, duplica y modifica cotizaciones (datos, ítems, plazo, oferta), usa las calculadoras, carga artículos y MO nuevos (con documento, proveedor y fecha; ARS al BNA del mes; IVA descontado) en `catalogo_nuevo` y descarga. Excepciones: no aprueba ni marca enviada; borrar y pasar a revisado los confirma el usuario con un botón; sin documento no carga precios | Matías ("control total") | `web/src/asistente.js`, `web/LEEME.md` |
| 28/10/2026 | No hay más información de precios que la ya entregada: el último precio se sigue eligiendo por fecha (no hay otras compras para preferir sobre la lista de Renard) | Matías | — |

## 3. Pendientes del proyecto

**Hace Claude** (aprobado el 28/10/2026: "el resto, dale para adelante")
1. ~~Catálogo de MO y servicios etapa 1~~ **Hecho (28/10/2026).**
2. ~~Etapa 2 de los catálogos~~ **Hecho (28/10/2026):** 2.492 renglones de 31 planillas de costo (`precios/planillas_costo_items.csv`, `herramientas/unir_planillas_costo.py`); 18 de los 49 proyectos marcados con planilla en el índice solo tienen precios de venta.
3. ~~Revisión independiente de los pesos~~ **Hecho (28/10/2026):** `auditorias/2026-10-28_pesos_bridas_accesorios.md`; errores corregidos.
4. ~~Vendor lists en el RAR de la Tanda 1~~ **No están** (revisado el 28/10/2026: la Tanda 1 solo trae las listas de YPF, ya cargadas; de PAE, Pampa y Pluspetrol solo hay referencias). Quedan en la carpeta completa `Z:\VENTAS\OFERTAS Y LICITACIONES` (1.Documentación de la licitación) o hay que pedirlas al cliente cuando se cotice para ellos.
5. ~~Integrar las tablas nuevas~~ **Hecho (28/10/2026):** `armar_cotizacion.py` corre `controles_tablas.py` y deja `controles_tablas.md` en cada cotización (kilos y m², plazo típico por rubro con aviso si supera el ofrecido, marcas del cliente). Falta: pesos de válvulas, uniones dobles y bujes reductores (no hay tabla).

**Qué hace la IA y qué es automático (decisión de Matías, 28/10/2026).** Lo que varía entre cotizaciones, clientes y proveedores lo sigue leyendo la IA: planos, pliegos, especificaciones y las cotizaciones que mande Compras (en el formato que vengan; no se usa un formato fijo de respuesta). Lo automático empieza cuando esos datos ya están en los formatos internos (`lista_materiales_plano.csv` y `cotizacion.json`): búsqueda en el catálogo, soldaduras, m², plazo, comparación con antecedentes, sumas y controles. El programa propone y marca; siempre revisa una persona o la IA.

Hecho (28/10/2026): `precotizar.py` (materiales, soldaduras, pintura, PH, RX) · `plazo.py` (acopio + taller sin superponer, margen 15–20%, plazo real de la familia) · `comparar_antecedentes.py` (P8 contra los 5 más parecidos) · control de carga en `verificar_computo.py` (fecha válida, "con IVA", sin precio) · `verificar_todo.py` y `actualizar_base.py`. Descartado: lectura automática de planos y pliegos, y formato fijo para las respuestas de Compras.

**Página web: plan por etapas** (propuesto el 28/10/2026; cada etapa se usa antes de pasar a la siguiente)
1. **Probar la página como está:** Matías arma 2 o 3 cotizaciones reales y completa su firmante (teléfono, celular, email, imagen de la firma). Revisar la primera tarea semanal (lunes 2/11).
2. ~~Subir archivos desde la página~~ **Hecho (28/10/2026):** sección Pedidos. Detalle original: → quedan "pendientes de procesar" en la base (`assets` + colección de pedidos); se procesan en un chat o el lunes, y en la página pasan a "incorporado" o "con dudas".
3. ~~Chat en la página~~ **Hecho (28/10/2026), falta que Matías lo pruebe con su cuenta** (en la prueba local se simuló Claude):: ve la cotización abierta, busca en los catálogos, carga y corrige ítems, explica avisos, propone la lista de materiales desde la imagen de un plano. No toca GitHub. Usa la cuenta de quien la usa.
4. ~~"Mandar a Claude Code"~~ **Hecho y probado de punta a punta (28/10/2026, pedido `prueba-circuito`):**: la página manda el pedido y el archivo a una sesión de Claude Code con el repositorio (capacidad `mcp`, conector Claude Code Remote); la sesión arma la cotización o actualiza el catálogo según el procedimiento, deja el resultado en borrador en la página y lo sube a GitHub. Estado del pedido en la página: en proceso / listo / con dudas.
5. **Sumar a otra persona:** colaboradora en GitHub + edición en la página; probar su agente con una cotización de control (CAPEX = 7.620,59). Ojo: ve todos los costos; la imagen de firma hoy solo la sube quien tiene edición.
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
