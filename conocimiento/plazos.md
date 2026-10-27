# Plazos de entrega

Fuente: *Seguimiento de presupuestos / Proyecto / facturación Rev1* (2023 → ago-2026), con datos de 2019 en adelante. Las tablas completas están en:
- [`comercial/plazos_proyectos.csv`](comercial/plazos_proyectos.csv): 57 ítems de 2022 a 2026, con fecha de OC, entrega comprometida, entrega real y atraso.
- [`comercial/plazos_historicos_2019-2024.csv`](comercial/plazos_historicos_2019-2024.csv): 191 proyectos con el plazo pedido en la OC y algunas entregas reales.

Los días son corridos.

## 1. Plazos de referencia por familia

| Familia | Plazo pedido en la OC (mediana, 2019–2024) | Plazo real (OC → entrega) | Comentario |
|---|---|---|---|
| Colectores / acometidas (CO) | **51 días** (45–83) | — | Producto repetitivo |
| Manifolds (M) | **49 días** (0–149) | 58 días (29–155) en 2023–2026 | Desde 2024 se cumplen o se entregan antes |
| Mojones, mazos de tubos y otros (OT) | 70–120 días | 120–160 días | |
| Puentes de medición (P) | 121 días (94–148) | — | Atrasos de 101–118 días en 2025 |
| Skids (SK) | **122 días** (27–211) | 162 días (88–350) | |
| Filtros (F) | 42–126 días | — | |
| Tanques (T) | 124 días (100–245) | 108–441 días | |
| Calentadores indirectos (C) | **176 días** (92–193) | **431 días** (173–656) | Atraso típico de 270 días en 2023 |
| Separadores (SEP) | **224 días** (123–321) | **370 días** (319–421) | Atraso típico de 290 días en 2023 |
| Trampas scraper (TS) | 204 días | 222 días | 2025–2026 |

## 2. Atraso respecto de lo comprometido: mejoró mucho

| Año de entrega comprometida | Ítems | Atraso mediano |
|---|---|---|
| 2022 | 2 | 348 días |
| 2023 | 27 | **232 días** |
| 2024 | 6 | 68 días |
| 2025 | 3 | 38 días |
| 2026 | 6 | **9 días** |

Lo que muestra: en 2022–2023 se comprometían plazos de calentadores y separadores **la mitad de lo que realmente tomaban**. Desde 2025 los atrasos son chicos. Para cotizar conviene usar el **plazo real reciente**, no el que se prometía antes.

## 3. De qué se compone el plazo

```
plazo = acopio de materiales (camino crítico) + fabricación + ensayos y terminación + despacho
```

En los proyectos atrasados de 2023 el cuello de botella fue el **acopio de materiales**. Los separadores de AESA arrancaron con 0–60% del material, y faltaban bridas de 20" y válvulas de control y de seguridad.

### Plazos de materiales observados

| Material | Plazo | Fuente |
|---|---|---|
| Accesorios de cañería nacionales (codos, reducciones, bridas comunes) | Días a 2–3 semanas | OP 1155 / 1162 (Complemet, Cintolo) |
| Válvulas esféricas Taval de stock | ~30 días | OP 1155 |
| Válvulas de seguridad y alivio (AERRE ARBROS) | 2–3 meses (pedidas en abril, entregadas en junio) | OP 1155 |
| Válvulas de control (EPTA) | Más de 3 meses, sin fecha por demoras de material importado | OP 1155 |
| Válvulas API grandes (8"–12" #900) y tapas de cierre rápido importadas de China | 40 días de fabricación + flete e importación | OP 1176 / 1179 |
| Bridas especiales (20" #150 XS) | Sin OC a tiempo: fue el ítem crítico | OP 1155 |

Regla práctica: **los materiales importados y la instrumentación definen el plazo**. La herramienta tiene que identificarlos en el cómputo y pedir cotización con plazo de entrega desde el primer día. En el stock (`precios/stock_2024-11.csv`) se ve qué se puede tomar sin comprar.

### Duración de las tareas de fabricación (cronogramas AESA 2023)

| Equipo | Tareas y duración |
|---|---|
| **Separador de gas combustible** | Cañerías 11–26 d · cuerpo y casquetes 15–25 d · tapas 7–16 d (en paralelo) · vinculación cuerpo + tapa · dimensional 1 d · PH envolvente 1 d · pintura 2–3 d · aislamiento 2 d |
| **Separador trifásico** | Armado y soldadura de cuerpo, brazo y pasarela 17 d · vinculación 1–2 d · colocación de cañería 4 d · pruebas + dimensional 3 d · PH general 3 d · pintura 6 d · aislamiento y control de calidad 4 d → **unos 38 días de taller** con el material completo |
| **Filtro separador FS-214** | Cuerpo superior 20 d · cuerpo inferior 15 d · skid 10 d · END 4 d · vinculaciones 4 + 10 d · END 2 d · PH 1 d · dimensional 1 d · granallado y pintura 4 d · aislación 3 d · armado final con instrumentos 4 d · inspección y despacho 1 d |
| **Puente de medición 12"** | Cañería, armado y soldadura 12 d · skid 5 d · END 2 d · derivaciones 4 d · END 2 d · PH 2 d · dimensional 1 d · granallado y pintura 8 d · armado final 2 d · despacho 1 d → **unos 40 días** |
| **Tramo de medición** | PH 1 d · bruñido 15 d · rugosidad 1 d · pintura 2 d |

Con el material en planta, los equipos de proceso medianos llevan **entre 6 y 10 semanas de taller**. El resto del plazo real fue espera de materiales.

## 4. Regla para cotizar el plazo

1. Del cómputo, identificar los **ítems de plazo largo**: importados, válvulas de control y de seguridad, instrumentos, bridas y accesorios especiales, chapa especial o inoxidable/dúplex.
2. Plazo de acopio = el mayor plazo de proveedor entre esos ítems, o 0 si están en stock.
3. Plazo de fabricación = suma de tareas de la tabla anterior para el tipo de equipo, o la mediana real de la familia.
4. Sumar ensayos, PH, pintura y despacho si no están incluidos, y un **margen de 15–20%**.
5. Comparar contra la mediana real de la familia (sección 1). Si el plazo calculado es mucho menor, revisar antes de comprometerlo.

## 5. Datos de seguimiento comercial (2024–2026)

[`comercial/cotizaciones_2024-2026.csv`](comercial/cotizaciones_2024-2026.csv) tiene 284 cotizaciones. **232 figuran como "Enviado" y no tienen resultado cargado**, y solo 12 figuran como ganadas. Sin el resultado no se puede saber con qué precio y plazo se gana. Es lo primero que el bibliotecario tiene que resolver: registrar siempre el cierre (ganada, perdida y por qué).

El factor de venta (`Fx`) registrado en esas cotizaciones va de **1,2 a 1,8**, con 1,4–1,5 lo más habitual.
