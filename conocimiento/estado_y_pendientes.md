# Estado del cotizador, decisiones y pendientes

**Leer al empezar cada chat.** Es la memoria del proyecto entre sesiones: qué está hecho, qué se decidió, qué falta.

**Objetivo: construir el cotizador automático.** Las cotizaciones (por ahora la CAPEX) son casos de prueba para armar y validar el proceso; sus pendientes no son pendientes del proyecto. Actualizado al 28/10/2026.

## 1. Qué hay hoy

| Pieza | Estado | Dónde |
|---|---|---|
| Procedimiento de cotización (P1–P10) y guía paso a paso | Vigente | `procedimiento_cotizacion.md`, `guia_cotizacion.md`, skill `.claude/skills/cotizar/` |
| Motor determinístico: cómputo, planilla con fórmulas, informe HTML con descargas, lista para Compras, ofertas técnica y económica | Vigente | `herramientas/armar_cotizacion.py`, `generar_oferta.py`, `lista_compras.py`, `verificar_computo.py` |
| Índice de proyectos 2025–2026 y buscador de antecedentes | Vigente (158 proyectos) | `comercial/indice_proyectos.csv`, `herramientas/buscar_antecedentes.py` |
| Catálogo de materiales con marca, unidad, IVA y alertas | Vigente, auditado el 27/10/2026 (2.310 materiales) | `precios/catalogo_materiales.*`, `herramientas/catalogo_materiales.py`, `buscar_material.py`, `test_catalogo.py` |
| Lector único de números y fechas | Vigente | `herramientas/numeros.py` |
| Dólar mensual 2024–2026 (oficial, mayorista, MEP, blue) | Vigente | `costos/dolar_mensual.csv/.xlsx`, `herramientas/dolar_mensual.py` |
| Índices de inflación (costo local en USD y CPI EE.UU.) desde ene-2024 | Vigente | `costos/indices_ajuste.csv`, `herramientas/indices_inflacion.py` |
| Peso y superficie de caños (ASME B36.10) | Vigente (calculado) | `tecnico/canos_peso_superficie.csv`, `herramientas/tablas_pesos.py` |
| Peso de bridas (B16.5) y accesorios (B16.9, B16.11) | **Borrador: falta revisión independiente** | `tecnico/bridas_peso.csv`, `accesorios_peso.csv`, `pesos_LEEME.md` |
| Marcas aprobadas por cliente | **Borrador** (YPF completo; PAE, Pampa, Pluspetrol parciales) | `comercial/marcas_aprobadas.csv` + `_resumen.md` |
| Plazos de entrega de proveedores | **Borrador** (213 datos, 154 verificados) | `comercial/plazos_proveedores.csv` + `_resumen.md` |
| Catálogo de mano de obra y servicios | **En curso / pendiente** | Instrucciones: `herramientas/catalogo_servicios_instrucciones.md` |
| Auditoría del catálogo de materiales | Hecha y corregida | `auditorias/2026-10-27_catalogo_materiales.md` |

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
| 28/10/2026 | **Valores anteriores al 14/04/2025 (cepo) sin tipo de cambio explícito: se descartan** y vale el último valor confiable. Si no hay ninguno, el material queda "sin precio confiable: pedir cotización", con el valor descartado como referencia | Matías | `catalogo_materiales.py` (FIN_CEPO), `verificar_computo.py` |
| 28/10/2026 | No hay más información de precios que la ya entregada: el último precio se sigue eligiendo por fecha (no hay otras compras para preferir sobre la lista de Renard) | Matías | — |

## 3. Pendientes del proyecto

**Decide Matías**
1. Renglones "IVA 21%" y "total con IVA" de referencia en la planilla de la cotización: ¿se dejan? (hoy se dejan).

**Hace Claude** (aprobado el 28/10/2026: "el resto, dale para adelante")
1. Catálogo de MO y servicios etapa 1 (en curso; si no está en `precios/catalogo_servicios.*`, relanzar con `herramientas/catalogo_servicios_instrucciones.md`).
2. Etapa 2 de los catálogos: costos renglón por renglón de las planillas de costo 2025–2026 (materiales, MO y servicios).
3. Revisión independiente de los pesos de bridas y accesorios.
4. ~~Vendor lists en el RAR de la Tanda 1~~ **No están** (revisado el 28/10/2026: la Tanda 1 solo trae las listas de YPF, ya cargadas; de PAE, Pampa y Pluspetrol solo hay referencias). Quedan en la carpeta completa `Z:\VENTAS\OFERTAS Y LICITACIONES` (1.Documentación de la licitación) o hay que pedirlas al cliente cuando se cotice para ellos.
5. Integrar en `armar_cotizacion.py` las tablas nuevas: plazos (camino crítico), pesos (kg y m²), marcas (control del pliego).

**Al terminar el proyecto** (decisión de Matías)
1. Confirmar con Compras los precios sospechosos de la auditoría (columna `alerta`).
2. Instalar la herramienta en la PC de Matías, recién cuando esté completa y funcionando al 100%.

**Descartado por ahora** (decisión de Matías, 28/10/2026): escalas UOM, tasa de interés / costo financiero, plazos de pintura y END, reporte de compras 2021–2024 en pesos (además cae en el período con cepo).

## 5. Cómo seguir en un chat nuevo

1. Leer `CLAUDE.md`, este archivo y `conocimiento/RESUMEN.md`.
2. Para cotizar: skill `cotizar` + `guia_cotizacion.md` + `procedimiento_cotizacion.md` + `errores_y_lecciones.md`.
3. Después de tocar el catálogo: `python herramientas/test_catalogo.py`.
4. Al terminar: actualizar este archivo, commit y push (lo que no se sube se pierde).
