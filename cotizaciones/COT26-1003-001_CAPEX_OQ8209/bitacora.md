# Bitácora · COT26-1003-001 · CAPEX OQ8209 · 2 puentes BBO MEC 1500

Registro de cómo se armó esta cotización, en orden, con las decisiones y los errores. Es el **caso modelo** del cotizador: la [guía](../../conocimiento/guia_cotizacion.md) y el [procedimiento](../../conocimiento/procedimiento_cotizacion.md) salieron de acá.

**Estado al 27/10/2026:** borrador. La revisión independiente se hizo y encontró 3 críticos, así que **no pasa a "revisado"** hasta tener los precios de Compras. Precio provisorio USD 7.620,59 por puente (15.241,18 por 2, sin IVA), con el 63% del costo estimado. 75 días desde la OC, EXW Quilmes. **No enviado.**

## Datos del pedido

- Pedido de Cotización OQ 8209 / OR 53081 de CAPEX S.A. (comprador Carlos Russ), emitido el 19/10/2026.
- Ítem 1.000, artículo C01A930098080: puente armado de bombeo mecánico serie 1500, 2 unidades. Documento 17009-PDC-YAC-PC-P-001 rev 1; plano 23001-PDC-YAC-PC-P-001 rev 1.
- Requisitos:
  - PH a 15 kg/cm² con registro;
  - unión extensible con sello metal-metal;
  - esféricas de cuerpo enterizo;
  - pintura esmalte sintético color cedro.
- Plazo para responder: 22/10/2026 (vencido). Fecha de necesidad: 09/11/2026. Entrega pedida en Pampa del Castillo (Comodoro).
- Originales en `pedido/`. Llegaron por mail como ZIP: la OR en PDF y el plano en PDF.

## Cronología (27/10/2026)

| Hora | Paso | Resultado | Commit |
|---|---|---|---|
| ~16:40 | Lectura del pedido y del plano (PyMuPDF; la tabla y el detalle, en imagen) | Tabla de 25 posiciones y notas del plano | — |
| ~16:50 | Búsqueda de antecedentes en la base | OE 332-24 (APSA/8, 6.200 c/u, 2024), APSA/15 (jun-2026, 6.729 c/u con BOP), OE 408-25, APSA/9 (Danco 3.665) | — |
| 17:13 | **Primer borrador**: costo bottom-up 6.695 → propuesta USD 7.700 c/u | Tenía errores (ver abajo) | `2e8bc17` |
| 17:22 | Rastreo de la fuente de cada precio para el informe. Aparecen la **PRES 24879** (TAVAL/55, puente convencional de bombeo mecánico, planilla completa), la **JQ-016-2026** (Quesada, armado 380) y las capturas de WhatsApp de Danco y del flete (originales del RAR) | MO corregida 1.800 → 400, bloqueo y purga 197,71 → 137, junta 280 → 315. Precio 7.275 (mal calculado en el chat) | `5f9d2bc` |
| 18:12 | Planilla Excel con fórmulas | Detectado que el 7.275 del chat no coincidía con el informe (7.287) | `c1d88e0` |
| 18:26 | Pregunta de Matías: "¿la MO no es un servicio?" | Dos factores: materiales y MO y servicios, los dos en 1,35, como en la PRES 24879 → 7.256 | `92eadb4` |
| 18:41 | Pedido de Matías: comparar la lista contra el plano | Caño 14 en 1,9 m + sobrante aparte; manómetro con conexión 1/2"; 2 soldaduras de cupla → 7.302 | `4b9887c` |
| 18:44 | Pedido de Matías: registrar lo que pasó y corregir el procedimiento | `procedimiento_cotizacion.md`, `errores_y_lecciones.md`, `verificar_computo.py` | `57fb167` |
| 19:03 | Oferta técnica y económica con el formato de ITT | Plantilla: oferta 138 a Flargent (mar-2026); estructura de la técnica según la PRES 24879. Redondeo del unitario en la planilla (14.603,26) | `1762587` |
| 19:38 | Ajuste por inflación | Índice mensual: CPI de EE.UU. para materiales; IPC INDEC ÷ dólar BNA para MO y servicios → **7.540,63** | `f041d94` |
| ~20:00 | Consolidación para poder repetir el proceso | `cotizacion.json` como única fuente; `armar_cotizacion.py`; plantillas; guía | `5028c4b` |
| ~20:20 | Lista de materiales y servicios para Compras (Matías no compra) | `compras/COT26-1003-001_pedido_materiales_compras.xlsx` | `2190b80` |
| ~20:30 | **Revisión independiente** (agente que no armó el cómputo; verificó 8 precios contra el original) | 3 críticos: plazo real 75 días, esféricas sin cotización metal-metal (+30% inventado), retención trim 8 y no 316. Mayores: manómetro NPT-H, extensible sin metal-metal, junta BW/NPT, buje BSPT, revestimiento de juntas sin costear, estimados reales ~33%, cotizaciones vencidas, diferencia sin explicar con antecedentes | — |
| ~20:45 | Correcciones de la revisión | Precios sin respaldo pasan a estimado; plazo 75 días; manga termocontraíble (14c); desvíos y oferta corregidos (fuera de término, [a confirmar]); NPT-H; Morken; plantilla de oferta limpia → **7.639,86** | este commit |
| 27/10 noche | Auditoría del catálogo de materiales: TC BNA reales de 2026 en `indices_ajuste.csv` | El índice de costo local de abr-2026 sube de 106,6 a 109,5: menos ajuste para el armado y la pintura → **7.620,86** | ver git log |
| 27/10 noche | Tabla de dólar mensual 2024–2026 y decisión: promedio mensual BNA billete vendedor | `indices_ajuste.csv` con promedios reales desde ene-2024 → **7.620,59** | ver git log |

## Decisiones y criterios

| Tema | Decisión | Por qué |
|---|---|---|
| Modelo de costo | PRES 24879 rev A (Taval/Tecpetrol, 22/04/2026), puente convencional | Es el puente de bombeo mecánico más parecido y más reciente, con planilla de costo ítem por ítem |
| MO de armado | Ledesma USD 400 (abr-2026). Alternativas: Quesada 380 y Ledesma 1.800 (sep-2025, con corte de caño) | El de 400 es el más reciente con el mismo alcance |
| Soldaduras | 4 a tope 2" sch80 + 2 cuplas 1/2" = 13,09 pulg-eq × 19,73 USD (costo de planta oct-2024) | Se derivan de los extremos BW del plano. Las puntas BW de 22, 25 y 16 quedan para campo |
| Factores | 1,35 materiales y 1,35 MO y servicios | En la PRES 24879 la MO de terceros dentro del puente iba a 1,35. El 1,40 era solo para MO vendida sola |
| Contingencia | 5% sobre materiales | El 7% del costo es estimado (niples por antecedente, PH, calidad) |
| Ajuste por inflación | Índice mensual, no tasa fija | Entre oct-24 y oct-25 el costo local en USD bajó 10% y entre oct-25 y oct-26 subió 26%. Una tasa fija sobreajustaba la soldadura de 2024 en +64% |
| Pago, plazo y entrega | Contado contra entrega, 60 días, EXW, validez 15 días | Igual que la OE 332-24 al mismo cliente. La validez es corta porque las cotizaciones de los proveedores vencen pronto |
| Flete | Aparte, no incluido | Hay una referencia de ARS 3.500.000 (jun-2026), pero tiene más de 4 meses |

## Errores detectados (todos antes de enviar)

Están en [`errores_y_lecciones.md`](../../conocimiento/errores_y_lecciones.md): MO con otro alcance, precio de otro modelo, dato de WhatsApp tomado como precio, factor mal copiado, cuentas hechas fuera de la herramienta, cómputo no comparado contra el plano (caño, manómetro, cuplas), especificaciones de proveedor distintas a las del plano y presentar un número antes de contrastarlo. **Ninguna versión con errores llegó al cliente.**

## Evolución del precio por puente

| Versión | USD c/u | Motivo del cambio |
|---|---|---|
| Primer cálculo | ~9.000 | MO 1.800 + doble conteo; no se presentó |
| Borrador 1 | 7.700 | Propuesta sin rastrear las fuentes |
| Informe v1 | 7.275 / 7.287 | MO 400, bloqueo y purga 137 (7.275 era un error de cuenta) |
| Factores 1,35 / 1,35 | 7.256 | MO de terceros como servicio |
| Revisión contra el plano | 7.302 | + 2 soldaduras de cupla |
| Con ajuste por inflación | 7.540,63 | Precios llevados a oct-2026 |
| Después de la revisión independiente | 7.639,86 | + manga termocontraíble en juntas; 63% del costo estimado hasta que Compras responda |
| Tipo de cambio de la auditoría (error: eran del dólar divisa/mayorista) | 7.620,86 | Se mezclaron dos cotizaciones del dólar en la tabla de inflación |
| **Dólar = promedio mensual BNA billete vendedor (decisión de Matías)** | **7.620,59** | Promedios reales de cada mes en lugar de valores interpolados: el índice de costo local de abr-2026 sube, y el ajuste del armado y la pintura baja |

**Comparación con antecedentes (P8), pendiente de cerrar.** El precio está 23% arriba de la OE 332-24 (6.200, 2024, otro puente: bomba electrosumergible) y bastante más arriba que APSA/15 sin el BOP (~5.100). Por puente, este equipo lleva rubros que esos antecedentes no tenían o que tenían más baratos: 2 retenciones S600 (~1.080), 2 extensibles metal-metal (~510), junta monolítica (~320), 2 bloqueos y purgas de acero inoxidable (~280), 2 manómetros (~180), caño revestido con manga (~225) y el ajuste por inflación (+3%). Con los precios reales de Compras hay que rehacer la comparación rubro por rubro. Si sigue más de 15% arriba, la dirección decide si se ajusta el factor.

## Pendiente para pasar a "revisado" y "aprobado"

Los pendientes actualizados después de la revisión independiente están en `cotizacion.json` → `pendientes` (y en el informe). Lo de abajo es la lista original.


1. Revisión independiente del cómputo contra el plano (P9.2).
2. Confirmar con proveedores:
   - esféricas con asiento metálico y cuerpo enterizo (Taval o Indave);
   - retención S600 con trim 316 (Ingeniería en Fluidos o Danco);
   - junta monolítica BW/BW (Duralitte);
   - extensibles metal-metal (Adita o Duralitte);
   - manómetro 0–40 bar de 1/2";
   - caño revestido PP o PE (Provemet).
3. Consultar a CAPEX:
   - si acepta la oferta fuera de término;
   - si compra directo o vía Almacenes Petroleros;
   - EXW o entregado;
   - PP o cinta Canusa;
   - marcas;
   - formato del registro de PH.
4. Completar el número de PRES y los teléfonos de la firma, y que la dirección apruebe el factor.
5. Cargar el IPC y el dólar de octubre 2026 cuando salgan (`herramientas/indices_inflacion.py`) y volver a armar.

## Cómo regenerar todo

```bash
python herramientas/armar_cotizacion.py cotizaciones/COT26-1003-001_CAPEX_OQ8209
```

Lo único que se edita es `cotizacion.json` (y `oferta.json` para los textos de la oferta). El informe se genera en `informe.html` (ya no se publica como página aparte; la cotización se ve en el Cotizador).

## 30-10-2026 · Segunda auditoría independiente de compatibilidades
- Pos 10 (buje 2"x1/2" NPT serie 2000): la referencia Renard es BSPT → SIN PRECIO, pedir buje NPT.
- Pos 23 (cupla 1/2" A234 WPB 80/2000 NPT/BW): la referencia era A105 NPT/NPT serie 3000, sin documentar → SIN PRECIO, pedir cotización.
- Pos 2, 5 y 7 quedan como ESTIMADOS (ya lo eran) armados sobre piezas que no cumplen el plano (pos 7: trim 13Cr, no AISI 316): pedir cotización con la especificación del plano.
- Unitario USD 7.324,57 (antes 7.366,12). Borrador.

## 30-10-2026 · Tercera auditoría independiente
- Los desvíos de la oferta (serie 3000, reducción 80×80, revestimiento, válvulas) son ahora lo que permite usar una pieza distinta: P9 los muestra como aviso y marca los que siguen "a confirmar" (pos 2, 5, 7, 14, 21). Hay que resolverlos antes de enviar.
- El buscador ya no propone para la pos 14 un caño sin revestimiento ni para la pos 16 una reducción XS×XS (el plano pide 80×40). La cotización no cambia.

## 30-10-2026 · Cuarta auditoría independiente
- El desvío de la oferta vale solo si habla de lo que no cumple y está resuelto: pos 2, 5, 7, 14 y 14b quedan como "DESVÍO A CONFIRMAR" (frenan el paso a revisado).
- Pos 21 (unión doble serie 3000 por 2000): se sumó al desvío de serie 3000 de la oferta ("Accesorios forjados roscados (pos. 1, 8, 10, 11, 17, 18) y unión doble (pos. 21)"). Revisar con Matías.

## 30-10-2026 · Quinta auditoría independiente: desvíos estructurados
- Cada desvío pasa a ser un dato del renglón (`desvio`): serie 3000 por 2000 en pos 1, 8, 11, 17, 18 y 21; schedule 80×80 por 80×40 en pos 16; "a confirmar" en pos 2, 5 (material y, nuevo, serie WOG 3000), 7, 14 y 14b. Los "a confirmar" frenan el paso a revisado.
- Pos 21: la oferta dice "sello metal-metal, marca Duralite o equivalente", pero el precio es de Adita M-H sin mención del sello: revisar con Matías.

## 30-10-2026 · Sexta auditoría independiente
- Pos 13 (junta monolítica): la fuente Duralitte es BW/NPT y el plano pide BW/BW → desvío de extremos a confirmar (la oferta ya lo tenía entre corchetes). Con la regla nueva de extremos sería ERROR sin desvío.
- Las aclaraciones de la oferta entre [corchetes] (pos 2, 5, 7, 13, 14, 19, 20, 21, 23 y niples) frenan el paso a revisado también en Python.
