# Revisión de la planilla YPF Lic 66944 · colectores manuales · 2da entrega (30-10-2026)

Planilla "COMPRA 2da ENTREGA AM COLECTORES", armada por Ricardo Álvarez y pasada por Matías para revisar si tenía errores arrastrados o matemáticos.
Original: `fuentes_originales/ypf_lic66944_colectores_2da_entrega_2026-10.xlsx`. Texto: `fuentes_originales/ofertas_texto/YPF/Lic 66944 - Colectores manuales 2da entrega/`. Ficha de antecedente: `conocimiento/fichas_2026/YPF_Lic_66944_-_Colectores_manuales_2da_entrega.json`.

## Qué vale (decisiones de Matías, 30-10-2026)
- **Solo vale la hoja "Pie de Venta rev 2".** La hoja "Pie de Venta" anterior y la tabla "Escenario Base" no se usan.
- **La hoja DISEÑO se ignora.** El radiografiado vale el de cada hoja: 30% en el 2658 y el 3152 (USD 1.500,00 de END por equipo) y 100% en el 7955 y el 7487 (USD 3.000,00).
- La hoja "ENOD" que mencionan los renglones de END no existe y se ignora.
- **Los valores cargados a mano son correctos**: son el último valor negociado o conocido con el proveedor y mandan sobre el detalle de abajo de cada hoja.
  - MO de terceros: Ledesma, **USD 15.000,00 por colector, solo fabricación**. El montaje, dimensional y desmontaje lo hace personal de ITT.
  - Transporte a Neuquén: **USD 1.500,00 por equipo**.
- **Todos los precios de la planilla son precios de hoy (30-10-2026)**, confirmados por Matías.
- **Las válvulas son marca Taval**, con precios Taval actualizados (la planilla no siempre lo dice).

## Totales de la rev 2 (sin IVA)

| TAG | Colector | Cant. | Costo unit. | Precio unit. | Precio total |
|---|---|---|---|---|---|
| SCC-500 | 2658 · 300 LB 4 pozos | 27 | 45.474,77 | 51.899,34 | 1.401.282,16 |
| SCC-100 | 7955 · 300 LB 6 pozos | 4 | 55.534,17 | 63.027,86 | 252.111,45 |
| SCC-700 | 3152 · 300 LB 4 pozos 10" | 2 | 54.645,79 | 62.427,66 | 124.855,32 |
| SCC-101X | 7487 · 600 LB 6 pozos | 2 | 66.588,53 | 75.735,03 | 151.470,07 |
| | **Total** | 35 | 1.692.424,19 | | **1.929.719,00** |

Las fórmulas se recalcularon con LibreOffice y coinciden con los valores guardados. Los subtotales de piping suman todos sus renglones.

## Hallazgos que siguen vigentes
1. **La columna "Margen de ganancia" del Resumen está mal**: trae el margen de cada hoja de colector, calculado con factor 1,5 (1ª entrega), y muestra 25,83% a 27,50%. El margen real de la rev 2, con MU 1,2, válvulas Taval a 1,0 y transporte a 1,1, es **12,30%** (Resumen E64), por debajo del 1,35 de referencia del cotizador. Corregir antes de mostrarla.
2. **No se sabe si las 90 h de planta por colector alcanzan para el montaje, dimensional y desmontaje** (Matías, 30-10-2026: "no sé por ahora"). Si no alcanzan, falta costo.
3. **Precios distintos de la misma pieza entre hojas.** No se cargaron al catálogo hasta que Matías decida cuál vale:

| Pieza | Precios (hoja) |
|---|---|
| Caño S/C BW SCH 60 A106 Gr.B 8" | 146,90 (2658) · 147,11 (7955 = 113,16 × 1,3) |
| Caño S/C BW SCH 80 A106 Gr.B 4" | 39,07 (2658, 3152, 7487) · 50,79 (7955 = × 1,3) |
| Caño S/C BW SCH 80 A106 Gr.B 3" | 27,78 (2658) · 36,11 (7955 = × 1,3) |
| Caño S/C BW SCH 80 A106 Gr.B 2" | 13,61 (2658, 3152) · 17,69 (7955 = × 1,3) |
| Tee normal BW SCH 80 4" | 105,49 (2658, 7955) · 105,00 (3152) · 106,00 (7487) |
| Brida ciega RF 300 LB 4" | 54,87 (2658, 7955) · 54,00 (3152) |
| Niple NPT SCH 80 1 1/2" | 15,00 (2658, 7955) · 13,00 (3152) |
| Niple NPT SCH 160 1/2" | 10,00 (2658, 7955) · 11,00 (3152) |
| Sockolet SW 3000 8"x1 1/2" | 8,00 (2658, 7955) · 9,00 (7487) |
| Sockolet SW 3000 4"x1 1/2" | 6,00 (2658) · 8,00 (7955) · 9,00 (3152) · 4,00 (7487) |
| Sockolet SW 3000 4"x3/4" | 6,00 (2658) · 8,00 (7955) · 9,00 (3152) |
| Sockolet SW 3000 3"x1/2" | 6,00 (2658) · 8,00 (7955) |
| Reducción excéntrica BW SCH 80 4"x2" | 137,81 (7955, mismo precio que la tee de reducción 4"x3": parece copiado) · 68,00 (3152) |
| Cap NPT 3000 2" | 5,00 (7955) · 1,29 (3152, mismo precio que la junta espiralada 2": parece copiado) |
| Tapón NPT cab. hexag. 1/2" | 1,00 (7955) · 2,00 (3152) |
| Caño S/C PL SCH 160 3/4" | 8,00 con unidad "UN." y cantidad 0,2 (7487): unidad dudosa |

## Arrastrados de la 1ª entrega (no cambian el total)
- Hoja 2658: cantidad de equipos 15 en I55 e I102 ("TOTAL DE EQUIPO 1RA ENTREGA") y los montos fijos de H26/H27 (Taval vs. precio válvulas).
- Hoja 7487: "TOTAL DE EQUIPOS 3" en H89.
- Repuestos: el detalle incluye espárragos de 1 1/8" y una junta de 12" que los colectores de 300 LB no llevan; el monto usado es un global cargado a mano (USD 1.000,00 o 1.500,00 por equipo).
- La "TEE DE REDUCCION EXCENT." 4"x2" de la hoja 2658 (USD 137,81) es en realidad una reducción excéntrica (B16.9 no tiene tee excéntrica); se cargó al catálogo tal como figura.
- La brida WN RF 300 LB 4" (USD 34,95) está calculada por proporción con otros precios; se cargó como **estimado**.
- Celdas del Resumen vinculadas a un libro externo ([4]); solo traen textos.

## Qué se cargó en la base (30-10-2026)
- `conocimiento/precios/precios_usuario.csv`: MO Ledesma (fabricación de colector), transporte a Neuquén, granallado y pintura por m², RX y LP por colector (30% y 100%), hora de planta y de ingeniería de ITT.
- `conocimiento/precios/listas_nuevas.csv`: 99 materiales (piping, válvulas Taval, instrumentos Weisz y Abac, perfilería por kg) con fecha 30-10-2026, menos los de la tabla del punto 3.
- Ficha de antecedente en `conocimiento/fichas_2026/` (familia CO, colector de campo).
