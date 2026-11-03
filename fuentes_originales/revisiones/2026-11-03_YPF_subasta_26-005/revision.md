# Revisión — Cotización Subasta 26-005 YPF Skids concentrador rev.0 (03-11-2026)

Archivo: `Cotizacion_Subasta_26-005_YPF_Skids_concentrador_rev.0.xlsx` (7 hojas). Valores recalculados con LibreOffice. Sin errores de fórmula (#REF!, #DIV/0!). Total actual del Pie de Venta: USD 1.074.752,06 sin IVA (710 × 5 + 713 × 4).

## Errores que cambian el precio
1. **Válvulas Taval contadas dos veces (hoja 1000623713).** D15 "Materiales, MO y SVC" = G80+G86+**G96**+G109+G114+G119 y D16 "Válvulas Taval" = **G96**. Las válvulas (31.058,16 por skid) están en las dos filas; la de materiales además lleva markup 1,5. Sobreprecio ≈ 46.587 por skid 713.
2. **Mano de obra de terceros contada dos veces (hoja SAP 1000623710).** C15 incluye **F109** (MO Silvio 8.100) y C18 = **F109**. Sobreprecio ≈ 12.150 por skid 710 (× 5).
3. **Fila "Instrumentos" de la 710 apunta al transporte.** C17 = F138 (transporte 1.200), igual que C19. Los instrumentos reales (F103 = 1.260) ya están dentro de C15. Resultado: el transporte se suma dos veces y la fila "Instrumentos" muestra un número que no es de instrumentos.
4. **Cantidad del 713: 3 o 4.** El pedido es "del 10 al 80" (8 ítems: 710 en 10, 20, 30, 50, 60 y 713 en 40, 70, 80 = 3 equipos), Resumen B7 dice "3 equipos colectores 4x8", la hoja 713 usa 3 (C15:C20) y la Revisión pide a proveedores para 3. Pero el Resumen (B15:B20) usa **4** y el Pie de Venta tiene un **ítem 90** con el mismo REF ID que el 80 (24360). Si son 3, sobran 180.404,83 en el total. En el Pie de Venta rev 1 aparece además un REF **24854** (ítem 60 del lote 3) que no está en el Pie de Venta original, con fecha de necesidad **01-03-2026** (anterior a la cotización), e ítems 50 y 60 repetidos en lotes distintos.
5. **Markups distintos entre hojas.** Resumen: transporte 1,2 e instrumentos 1,5. Hoja 713: transporte 1,0. Hoja 710: instrumentos 1,2 y transporte 1,1. El Pie de Venta toma el Resumen; las hojas por equipo dan otros totales (713: 179.904,83 vs 180.404,83; 710: 350.732,75 vs 353.132,75).
6. **Resumen G28 y G30 (margen) copian el margen de la hoja 710** (17 % y 9 %, calculados con otros factores) en vez de calcularse con el factor del Resumen (33 % y 17 %).

## Precios por debajo de la especificación (riesgo de perder plata o de entregar otra cosa)
7. **Brida WN 8" #300 SCH 60:** se usa Provemet 102,35 que es **SCH 80** (otro bore). Bripetrol cotiza el SCH 60 exacto a 132,00. Una WN de otro schedule no suelda bien con caño SCH 60 (regla de compatibilidad: igual schedule). Diferencia ≈ 1.423 por skid 713 (48 bridas) y 534 por skid 710.
8. **Caño 12" SCH XS:** 170,37 estimado por kg desde un caño 10" SCH 80 de Provemet, habiendo cotización firme de Renard del caño exacto (cód. 1201, 297,75). Diferencia ≈ 1.465 por skid 713 (11,5 m) y 191 por skid 710.
9. **Tes 8" SCH 60 y 12"x8" XS x SCH 60:** precio Cintolo de la versión XS (extra pesado). Precio conservador, pero es otra pieza: hay que comprar la SCH 60 (bore igual al caño).
10. **Junta dieléctrica 8":** precio 36,95 de Miyashiro que según la propia Revisión "cotizó Ø6" – confirmar 8"".
11. **Bridas ciegas 8" y 12", brida SW 1 1/2":** estimadas por USD/kg; Bripetrol cotizó 116,00 / 268,00 / 22,07 (ciega 8", ciega 12", SW). La ciega 12" estimada (338,23) está por encima de Bripetrol; la 8" (134,70) también.
12. **END sin respaldo:** 713 Rx y LP 5.000 por skid "según hoja ENOD" y 710 1.845,50; el archivo no tiene hoja ENOD (la 710 nombra una hoja "Man. Conc. Ent. 4x8- Materiales" que tampoco está).

## Criterios distintos entre los dos skids
13. **Repuestos:** 713 usa 10 % de bulonería y juntas (L60) + el doble para precom/com/PEM (L61) = 887,08; la 710 toma solo el bloque "2 años" (F160 = 165,20) y deja afuera el de PEM (F149 = 165,20) aunque el renglón dice "2 años + precom + com + pem". Los bloques detallados de repuestos de la 713 (filas 137–157) no se usan.
14. **Horas ITT:** 713 ingeniería y calidad 63/3 = 21 h por equipo; 710 calidad 72/5 = 14,4 h pero ingeniería **90 h por equipo** (sin dividir por 5: 450 h en total). La 710 carga 30 h de planta y al lado calcula 126 h (G113).
15. **Granallado 710 (C124:C125):** dos renglones de 10 m² sin descripción, uno con overspray 30 %.

## Detalles
16. Encabezados de las hojas por equipo con datos de otras cotizaciones: 713 "PRESUPUESTO: Javier lejondo" (ya no está en ITT), "CANTIDAD 1 (uno)" con 3 en el cuadro, fechas 11-08 / 22-08 (el Resumen dice 27-08 / 28-08); 710 fechas 25-06 / 16-07 y "1 unidad" con 5 en el cuadro.
17. Plazos distintos: hoja 710 "45 días" vs Pie de Venta 90; hoja 713 "90/120" vs 120. La Revisión avisa que las bridas Bripetrol a 120 días exceden los 90 días de los ítems 710.
18. Transporte 713 cargado a mano (D19 = 2500) en vez de =G124.
19. Celdas sueltas sin rótulo: 713 G27 (=6000/F23), 710 C26, H26, K28, H29.
20. Simulador MU: G47, G56 y G64 tienen 1,3 escrito a mano (no siguen a D5); los tres cuadros de lote dicen "Costo total - LOTE 1". Hereda los errores 1–3, así que los márgenes que muestra (27 %) están calculados sobre un costo inflado.
21. La hoja Revisión cita celdas que ya se corrieron (por ejemplo "E88" para la retención, hoy fila 89).

## Copia marcada
`Cotizacion_Subasta_26-005_REVISADA_errores_marcados.xlsx`: copia del original sin corregir, con cada celda pintada (rojo origen, rosa arrastre, naranja precio, amarillo a revisar), un comentario por celda (qué pasa, de dónde viene, efecto, qué revisar) y la hoja "LEER PRIMERO" con el índice e hipervínculos. Total sin cambios: 1.074.752,06.
