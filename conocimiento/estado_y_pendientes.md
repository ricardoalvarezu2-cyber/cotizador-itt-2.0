# Estado del cotizador, decisiones y pendientes

**Leer al empezar cada chat.** Es la memoria del proyecto entre sesiones: qué está hecho, qué se decidió, qué falta. Actualizado al 28/10/2026.

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

**Cotizaciones:** `cotizaciones/README.md`. La única en curso es **COT26-1003-001 CAPEX OQ8209**: borrador, USD 7.620,59 por puente (15.241,18 por 2, sin IVA), 75 días, 63% del costo estimado. **Espera precios de Compras y respuestas del cliente. No enviada.**

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

## 3. Pendiente de decisión de Matías

1. **Alerta "dólar sin aclarar, período con cepo"** para valores en USD de ene-2024 a abr-2025 sin tipo de cambio visible (mostrar cuánto daría con blue). Propuesta hecha, sin confirmar. Matías cree que la MO se pensaba en blue; la planilla de costo de planta oct-2024 usó oficial (997–998,5, hoja "Sueldos").
2. **Lista de Renard vs. compras reales:** las listas suelen estar muy por debajo de lo comprado. ¿Mostrar primero una compra o cotización de menos de un año antes que la lista?
3. **Renglones "IVA 21%" y "total con IVA"** de referencia en la planilla de la cotización: ¿se dejan o se sacan?
4. **Tablas que necesitan datos de ITT:** escala salarial UOM por categoría y mes; tasa que usa ITT para el costo financiero del plazo de pago.
5. **Catálogo de servicios etapa 2** (MO de las 50 planillas de costo, ~USD 8–12) y **catálogo de materiales etapa 2/3** (costos ítem por ítem de planillas 2025–2026; reporte de compras 2021–2024 en pesos).
6. Instalar la herramienta en la PC de Matías y carga automática de respuestas de Compras.

## 4. Pendiente de trabajo (sin decisión necesaria)

1. **Catálogo de MO y servicios etapa 1**: si no está en `precios/catalogo_servicios.*`, relanzar con `herramientas/catalogo_servicios_instrucciones.md`; luego revisar una muestra, commit y avisar.
2. **Revisión independiente de los pesos de bridas y accesorios** (unidad del catálogo Bonney Forge supuesta en lb; 58 valores que difieren >10% entre fuentes; 24 incoherentes en la misma fuente).
3. **Vendor lists de PAE (A7XN-RC-85-SP-0027_R1), Pampa y Pluspetrol (AARC-100-ET-X-001)**: no están en los textos; buscarlos en el RAR de la Tanda 1 o pedirlos.
4. **Plazos de pintura y END**: no hay ningún dato; pedirlos a proveedores.
5. **Sospechosos de la auditoría** para Compras: abrazaderas QOC 48" (USD 17.286), brida WN 1" #600 (5,55), codo 10" Cintolo (2.468), brida SW 24", compras del stock 2022–2024 a ~2,5× Renard (ver columna `alerta`).
6. **CAPEX**: cargar precios de Compras cuando lleguen, nueva revisión independiente, comparación P8 cerrada.
7. Integrar en `armar_cotizacion.py` las tablas nuevas (plazos para el camino crítico, pesos para kg/m², marcas para el control del pliego). Hoy se consultan a mano.

## 5. Cómo seguir en un chat nuevo

1. Leer `CLAUDE.md`, este archivo y `conocimiento/RESUMEN.md`.
2. Para cotizar: skill `cotizar` + `guia_cotizacion.md` + `procedimiento_cotizacion.md` + `errores_y_lecciones.md`.
3. Después de tocar el catálogo: `python herramientas/test_catalogo.py`.
4. Al terminar: actualizar este archivo, commit y push (lo que no se sube se pierde).
