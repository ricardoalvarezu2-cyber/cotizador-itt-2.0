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

## Costo y precio (Rev 0, recalculado el 27/10/2026)
El detalle interactivo, con el origen de cada precio, valores editables y exportación a CSV, está en `informe.html` (artifact https://claude.ai/artifact/Bi6jpUG36k1nQVmGJWTA7C). El cómputo ítem por ítem está en `computo.csv`.

| Rubro por puente | USD |
|---|---|
| Materiales | 4.224 |
| Contingencia 5% | 211 |
| Mano de obra (armado Ledesma 400 + soldaduras 224) | 624 |
| Procesos e insumos (PH, pintura, calidad, sellador) | 315 |
| **Costo** | **5.374** |
| **Precio** (1,35 sobre materiales y servicios, 1,40 sobre MO) | **7.275** |
| Total por 2 puentes | 14.551 + IVA |

Modelo de costo: PRES 24879 rev A (TAVAL/55, Tecpetrol, 22/04/2026), puente de producción convencional para bombeo mecánico.

**Correcciones al borrador anterior:** el armado de Ledesma pasa de 1.800 (sep-2025) a 400 (abr-2026). El bloqueo y purga de 197,71 (modelo de 3/4" y 6000 psi) pasa a 137. La junta monolítica sube de 280 a 315. Los accesorios ahora salen de la lista Renard.

**Sensibilidad:**
- Con la retención de Danco a 240 (sin confirmar), el precio baja a unos 6.445.
- Con el armado de Ledesma a 1.800, sube a unos 9.235.

## Comparables
| Antecedente | Precio c/u |
|---|---|
| OE 332-24 (APSA/8, 05/11/2024): puente para bomba electrosumergible serie 1500 | 6.200 |
| APSA/15 OR 33661 (jun-2026): puente de producción con AIB, incluye BOP 1.195 | ~6.729 |
| OE 150-22 (APSA/3, 25/08/2022): puente de producción 1500, costo 3.957 × 1,5 | 5.935 |
| Danco (APSA/9, feb-2026): puente AIB llave en mano | 3.665 de costo |

## Transporte
La base es EXW. Referencia: Sprinter de BAI a CRD por ARS 3.500.000 (1.200 kg, jun-2026, `antecedentes/flete_BAI-CRD_whatsapp_2026-06.png`). Se ofrece como ítem aparte.

## Plazo
**60 días desde la OC.** Las esféricas 2" de Indave tardan 60 días. Si Taval las tiene en stock, baja a 45. La fecha de necesidad del 09/11 no se puede cumplir.

## Antes de enviar
Ver la sección "Pendientes" en `informe.html`.
