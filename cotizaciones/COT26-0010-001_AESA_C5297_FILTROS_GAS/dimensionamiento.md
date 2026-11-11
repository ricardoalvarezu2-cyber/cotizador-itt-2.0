# Predimensionamiento ASME VIII Div.1 — filtro de gas de emergencia FCC-707/708 (COT26-0010-001)

**Borrador, sin revisar. Es un predimensionamiento para cotizar, no la memoria de cálculo que pide la requisición.** Lo genera `dimensionamiento.py`; no editar a mano. El código ASME no está en el repositorio: las tensiones admisibles (II-D), los datos de la junta y el rating de B16.5 están cargados de memoria y los tiene que verificar Ingeniería en la edición vigente.

## 1. Datos de diseño (hoja de datos 5297-02-0600-IG-EM-HD-001 E0)

| Dato | Valor |
|---|---|
| Presión de diseño | 10,00 kg/cm2 g (0,981 MPa) |
| Temperatura de diseño / MDMT | 90 / -10 °C |
| Sobreespesor de corrosión | 3,20 mm |
| Radiografiado | RT3 (por puntos): eficiencia de junta E = 0,85 |
| Código | ASME VIII Div.1 última edición, sin estampa (recipiente hasta la cara de la primera brida o la primera rosca); ASME B31.3 y clase CA11 para el niple, las válvulas de venteo y drenaje y sus tapones; bridas ASME B16.5 |
| Materiales | Envolvente SA-106 Gr. B; casquete SA-234 WPB; bridas SA-105; cuellos SA-106 Gr. B; espárragos SA-193 B7 / tuercas SA-194 2H |
| Tensión admisible a 90 °C | SA-106 B y SA-234 WPB 118 MPa; SA-105 138 MPa; SA-193 B7 172 MPa (a verificar en II-D) |

## 2. Espesores

| Parte | Adoptado | Mínimo disponible | Requerido por presión | Requerido total | Resultado |
|---|---|---|---|---|---|
| Envolvente, caño 6" Sch 80 (UG-27) | 10,97 mm | 9,60 mm (−12,5 %) | 0,76 mm | 6,20 mm (C0100 5.1.3: 3 + 3,20) | cumple |
| Casquete 6" Sch 80 (UG-32) | 10,97 mm | 9,60 mm | 0,76 mm | 6,20 mm | cumple |
| Cuello A y B, 1" Sch 160 (UG-45) | 6,35 mm | 5,56 mm | 0,14 mm | 4,70 mm | cumple |
| Cuello D, 3/4" Sch 160 (UG-45) | 5,56 mm | 4,86 mm | 0,11 mm | 4,70 mm | cumple |
| Brida ciega 6" #150 con corrosión (UG-34) | 25,90 mm (23,90 + resalte 2) | 25,90 mm | 20,72 mm | 23,92 mm | cumple, con poco margen (1,98 mm): a verificar |

- Con caño Sch 40 el mínimo disponible sería 6,22 mm contra 6,20 mm que pide YPF: sin margen. Por eso Sch 80.
- Manda el espesor mínimo de la C0100 de YPF, no la presión: por presión alcanza con menos de 1 mm.
- **Brida ciega: en el límite, a verificar por Ingeniería** (C0100 5.1.11: con corrosión mayor de 3 mm el fabricante verifica las bridas ciegas estándar). Manda el asentamiento de la junta (20,72 mm; en operación 12,90 mm), más 3,20 mm de corrosión. Contando el resalte cumple por 1,98 mm; sin contarlo (23,90 mm) no llega por 0,02 mm. El resultado depende de la junta, que no está definida (clase CA11, consulta C3): se calculó con espiralada (m = 3, y = 69 MPa), que es el caso más exigente; con junta plana de fibra sobra. Con esa junta el área de espárragos que pide el Apéndice 2 (1.621 mm2) supera la disponible (1.558 mm2), algo conocido en bridas #150 con espiralada: la unión es estándar (UG-44) y el caso de asentamiento es conservador. Si Ingeniería no la acepta, la salida es una tapa de chapa de 1" a 1 1/8" con el perforado #150 (≈ 2 kg más). El agujero roscado de 3/4" del venteo no necesita refuerzo (UG-39 a / UG-36 c 3).
- Bridas (UG-44): B16.5 clase 150, grupo 1.1, admite 18,0 bar (18,4 kg/cm2) a 90 °C contra 10,0 kg/cm2 de diseño: cumple.
- Refuerzo de aberturas (UG-36 c 3): las conexiones de 1" y 3/4" en la envolvente y el casquete no necesitan cálculo de refuerzo (abertura menor de 89 mm con espesor requerido de hasta 10 mm).
- Cuellos: Sch 160 por la C0100 5.1.3 (conexiones menores de 3").
- Prueba hidráulica (UG-99 b): 1,3 × 10,0 = **13,0 kg/cm2 g** como mínimo, tomando la presión máxima admisible igual a la de diseño (hay que declararlo en la oferta: la C0100 5.1.6 pide 1,3 × MAWP y, si la MAWP se calculara, la limita la brida #150 en ≈ 18,4 kg/cm2 y la prueba subiría a ≈ 23,9 kg/cm2).
- Impacto a −10 °C: el revisor independiente entiende que queda exento (UG-20 f y UCS-66: curva B con 11 mm; bridas B16.5 hasta −29 °C), dicho de memoria; se justifica en la memoria de cálculo.
- C0100 5.1.4 pide espesor mínimo total de 10 mm para partes de acero al carbono (está en el párrafo de internos): los internos soldados se previeron de 10 mm. Si YPF lo aplicara también a la envolvente, el Sch 80 con tolerancia (9,60 mm) no alcanzaría: está en la consulta C11.
- Sin calcular: cargas en conexiones (WRC 107, HD nota 5), viento, sismo y nieve sobre las patas y los pernos de anclaje, orejas de izaje y pescante.

## 3. Dimensiones generales (preliminares)

| Dimensión | Valor |
|---|---|
| Diámetro exterior del cuerpo | 168,3 mm (6") |
| Diámetro interior | 146,4 mm |
| Espesor de envolvente y casquete | 10,97 mm (Sch 80) |
| Largo de la tangente del casquete a la cara de la brida de cuerpo | 741 mm (casquete de 102 mm, caño de 600 mm y brida de 87 mm) |
| Altura del piso a la cara de la brida de cuerpo | 1.037 mm |
| Altura total con tapa | 1.067 mm |
| Altura total con válvula de venteo | ≈ 1.397 mm (el pescante puede sumar ≈ 100 mm) |
| Brida de cuerpo y tapa 6" #150 | Ø 280 mm; 8 espárragos 3/4" en Ø 241,3 mm |
| Conexiones A y B (1" #150 WNRF) | enfrentadas, a 770 mm del piso; 500 mm entre caras |
| Conexión D (3/4" #150 WNRF) | a 150 mm del piso; cara a 250 mm del eje |
| Conexión F (3/4" NPT #3000) | en el centro de la tapa |
| Patas | 3 de L 2" × 2" × 1/4", placas base 120 × 120 × 9,5 mm con agujero Ø 18 en círculo de Ø 330 mm |
| Volumen interior | 12,9 litros (0,0129 m3) |
| Superficie exterior a pintar | ≈ 1,17 m2 |

El largo del cuerpo y la posición de A y B dependen del cartucho (cantidad y medida a definir con el fabricante del elemento) y del caudal, que el cliente tiene que aclarar (consulta C1).

## 4. Peso (por filtro)

| Pos | Parte | kg | Origen |
|---|---|---|---|
| 1 | Envolvente: caño 6" Sch 80 × 600 mm | 25,54 | tabla |
| 2 | Casquete semielíptico 6" Sch 80 | 4,22 | tabla |
| 3 | Brida W.N. 6" #150 | 11,70 | tabla |
| 4 | Brida ciega 6" #150 | 12,20 | tabla |
| 5 | Pescante: caño 1 1/2" Sch 80 × 1,0 m, buje soporte, brazo y bulón de ojo | 8,91 | estimado |
| 6 | Junta de la tapa (1 colocada) | 0,30 | estimado |
| 7 y 31 | 8 espárragos 3/4" × 4" con 16 tuercas | 3,22 | calculado |
| 8 y 9 | 2 bridas W.N. 1" #150 | 2,80 | tabla |
| 10 | Cuellos A y B: caño 1" Sch 160 × 0,3 m | 1,27 | tabla |
| 11 | Brida W.N. 3/4" #150 | 0,90 | tabla |
| 12 | Cuello D: caño 3/4" Sch 160 × 0,4 m | 1,16 | tabla |
| 13 | Codo 90° 3/4" Sch 160 | 0,27 | tabla |
| 14 a 17 y 32 | Válvula de drenaje 3/4" con tapón, junta y bulonería (tipo a definir: CA11; entre 3,5 kg esférica y 8 kg esclusa) | 5,50 | estimado |
| 18 a 21 | Cupla, niple, válvula de venteo 3/4" NPT y tapón (tipo a definir: CA11) | 2,40 | estimado |
| 22 | 2 elementos filtrantes (a definir con el fabricante) | 1,00 | estimado |
| 23 y 24 | Internos: asiento de 10 mm, conducto de salida, varilla y bulonería | 5,00 | estimado |
| 25 | 3 patas L 2" × 2" × 1/4" × 500 mm con placa base 120 × 120 × 9,5 | 10,35 | calculado |
| 26 | 3 placas de refuerzo 150 × 80 × 6,35 | 1,79 | calculado |
| 27 | 2 orejas de izaje 80 × 60 × 9,5 | 0,72 | calculado |
| 28 | 2 orejas de puesta a tierra 50 × 40 × 6 AISI 316 | 0,19 | calculado |
| 29 | Placa de identificación con soporte 150 × 100 × 6 | 0,81 | calculado |
| 33 | Rompevórtice | 0,20 | estimado |
| — | Soldadura y pintura (≈ 2 %) | 2,01 | estimado |
| | **Peso vacío** | **102,45** | |

| Peso | kg |
|---|---|
| Vacío | 102 |
| En operación (gas) | 102 |
| En prueba hidráulica (lleno de agua, sin elementos) | 114 |
| En transporte (con patín y embalaje, estimado) | 114 |

Origen: *tabla* = tablas de pesos de `conocimiento/tecnico/` (bridas ±15 %, accesorios ±10–15 %); *calculado* = volumen × 7,85; *estimado* = pieza sin definir. Con margen, el peso vacío está entre 92 y 118 kg.

## 5. Listado de materiales

Está en `pedido/lista_materiales_plano.csv` (33 renglones por filtro), con el texto de la hoja de datos, cantidad, material y los datos de cada pieza en columnas.

