# COT26-1003-001 Rev 0 — CAPEX S.A. — PDC OQ 8209 / OR 53081

Estado: **borrador, sin enviar** (27/10/2026). Preparó: Matías Russo, con el cotizador.

## Pedido
| Dato | Valor |
|---|---|
| Cliente | CAPEX S.A. (código 1003). Comprador: Carlos Russ |
| Ítem | 1.000, artículo C01A930098080, "PUENTE ARMADO BBO MEC 1500", **2 unidades**. Código SAP anterior: 5049792 |
| Documento | 17009-PDC-YAC-PC-P-001 rev 1. El plano que vino es el 23001-PDC-YAC-PC-P-001 rev 1, "para construcción", del 12/06/2024 |
| Entrega pedida | Depósito Pampa del Castillo, RN 26 km 42 (Comodoro Rivadavia) |
| Fecha de la orden / límite de respuesta / necesidad | 19/10/2026 / **22/10/2026 (vencida)** / 09/11/2026 |
| Requisitos | PH a 15 kg/cm² verificando las uniones, con registro adjunto. Unión doble a golpe extensible con sello metal-metal. Esféricas de cuerpo enterizo, sin bulones de unión. Pintura: esmalte sintético color cedro; las válvulas van en el color original del proveedor. Alternativa: revestir el niple N°14 con cinta Canusa Wax Tape HT 3000 6"x9" (proveedor Workene) |

Originales en `pedido/`.

## Costo por puente (USD, sin IVA, EXW Quilmes)
| Rubro | Base | Optimizado | Criterio |
|---|---|---|---|
| Materiales (`computo.csv`) | 3.812 | 3.186 | En el optimizado, retención Danco a ~220 en lugar de 533 (a confirmar) |
| Contingencia de materiales 5% | 191 | 159 | El 37% del material es estimado |
| Armado roscado (Ledesma) | 1.800 | 1.800 | Cuadro de puente CBM roscado, sep-2025 |
| 4 soldaduras BW (11,4 pulg-eq × 19,7) | 224 | 224 | Costo propio de planta |
| PH 15 kg/cm² con registro | 100 | 100 | |
| Pintura | 110 | 110 | |
| Ingeniería, calidad y dossier | 100 | 100 | |
| **Costo** | **6.337** | **5.679** | |

## Precio por puente
| Factor | Base | Optimizado |
|---|---|---|
| 1,28 | 8.111 | 7.269 |
| **1,35** | **8.555** | **7.667** |
| 1,45 | 9.189 | 8.235 |

**Propuesta: USD 7.700 c/u (USD 15.400 los 2)** si se confirma la retención barata y el precio de las esféricas con asiento metálico. Si no se confirman, USD 8.550 c/u.

## Comparables
| Antecedente | Precio c/u | Comentario |
|---|---|---|
| OE 332-24 (nov-2024, APSA/CAPEX) | 6.200 | Puente de bomba electrosumergible serie 1500 (doc …-P-002). Es otro equipo, con menos válvulas |
| APSA/15 OR 33661 (jun-2026, CAPEX) | ~6.729 | Puente de producción con AIB, incluye BOP compacto (1.195). Sin resultado |
| OE 408-25 (oct-2025, Taval/CAPSA) | 2.307 | Solo mano de obra (Ledesma 1.800 × 1,28) |
| Danco, APSA/9 (feb-2026) | 3.665 costo | Puente de producción AIB llave en mano, 45 días. Alternativa: tercerizar todo en Danco |

Este puente cuesta más que los antecedentes por las 2 retenciones serie 600, las 2 extensibles metal-metal, los 2 bloqueo y purga AISI316, la junta monolítica y las esféricas con asiento metálico (unos USD 2.500 en esos ítems).

## Plazo
**60 días desde la OC.** Las esféricas 2" tardan 60 días en Indave (con asiento metálico, a confirmar), las extensibles de Adita 30–45 días y el taller 2–3 semanas. Si Taval tiene las esféricas en stock, se llega a 45 días. La fecha de necesidad del 09/11 no se puede cumplir.

## Antes de enviar
1. Confirmar precio y plazo de la retención 2" S600 (Danco o Ingeniería en Fluidos) y de las esféricas con asiento metálico (Taval o Indave).
2. Preguntar a CAPEX: si acepta la oferta fuera de término; si la compra es directa o vía Almacenes Petroleros; revestimiento PP o cinta Canusa; EXW o entregado en Pampa del Castillo (el flete BAI–CRD lo cotizó ETFA en jun-2026); si exige marcas de válvulas.
3. Condiciones (como OE 332-24): USD, sin IVA, contado contra entrega, validez 15 días por la validez corta de los proveedores.
