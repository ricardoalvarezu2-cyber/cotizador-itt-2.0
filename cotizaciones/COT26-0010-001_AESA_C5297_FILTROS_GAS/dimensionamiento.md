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
- C0100 5.1.4 pide espesor mínimo total de 10 mm para partes de acero al carbono (está en el párrafo de internos): por eso los internos soldados se previeron en AISI 316 L (mínimo 6 mm y sin corrosión; ver 6). Si YPF lo aplicara también a la envolvente, el Sch 80 con tolerancia (9,60 mm) no alcanzaría: está en la consulta C11.
- Sin calcular: cargas de cañería en las conexiones (WRC 107, HD nota 5). Viento, sismo, patas, anclaje, orejas y pescante: ver 7.

## 3. Dimensiones generales (preliminares)

| Dimensión | Valor |
|---|---|
| Diámetro exterior del cuerpo | 168,3 mm (6") |
| Diámetro interior | 146,4 mm |
| Espesor de envolvente y casquete | 10,97 mm (Sch 80) |
| Largo de la tangente del casquete a la cara de la brida de cuerpo | 741 mm (tramo recto del casquete 54 + caño 600 + brida 87; el casquete entero mide 102 mm) |
| Altura del piso a la cara de la brida de cuerpo | 1.037 mm |
| Altura total con tapa | 1.067 mm |
| Altura total con válvula de venteo | ≈ 1.397 mm (el pescante puede sumar ≈ 100 mm) |
| Brida de cuerpo y tapa 6" #150 | Ø 280 mm; 8 espárragos 3/4" en Ø 241,3 mm |
| Conexiones A y B (1" #150 WNRF) | enfrentadas, a 600 mm del piso; 500 mm entre caras |
| Conexión D (3/4" #150 WNRF) | a 150 mm del piso; cara a 250 mm del eje |
| Conexión F (3/4" NPT #3000) | en la tapa, corrida 50 mm del centro (el centro lo ocupa el cáncamo del pescante) |
| Patas | 3 de L 2" × 2" × 1/4", placas base 120 × 120 × 9,5 mm con agujero Ø 22 en círculo de Ø 330 mm |
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
| 22 | Elemento filtrante: 1 cartucho de 2 3/4" × 10" (a definir con el fabricante) | 0,50 | estimado |
| 23 y 24 | Internos AISI 316 L: tubo de salida 1" Sch 160 con codo, asiento, platillo, resorte, varilla y bulonería | 4,00 | estimado |
| 25 | 3 patas L 2" × 2" × 1/4" × 550 mm con placa base 120 × 120 × 9,5 | 11,06 | calculado |
| 26 | 3 placas de refuerzo 150 × 80 × 6,35 SA-516 Gr. 70 roladas | 1,79 | calculado |
| 27 | 2 orejas de izaje 120 × 80 × 9,5 | 1,43 | calculado |
| 28 | 2 orejas de puesta a tierra 50 × 40 × 6 AISI 316 | 0,19 | calculado |
| 29 | Placa de identificación con soporte 150 × 100 × 6 | 0,81 | calculado |
| 33 | Rompevórtice | 0,20 | estimado |
| — | Soldadura y pintura (≈ 2 %) | 2,01 | estimado |
| | **Peso vacío** | **102,38** | |

| Peso | kg |
|---|---|
| Vacío | 102 |
| En operación (gas) | 102 |
| En prueba hidráulica (lleno de agua, sin elementos) | 114 |
| En transporte (con patín y embalaje, estimado) | 114 |

Origen: *tabla* = tablas de pesos de `conocimiento/tecnico/` (bridas ±15 %, accesorios ±10–15 %); *calculado* = volumen × 7,85; *estimado* = pieza sin definir. Con margen, el peso vacío está entre 92 y 118 kg.

## 5. Proceso y elemento filtrante

| Dato | Valor |
|---|---|
| Caudal de diseño adoptado | 11,67 Sm3/h (hoja de datos: 0,28 MSCMD; el P&ID dice 6,15 Sm3/h: consulta C1) |
| Caudal real a 4,5 kg/cm2 g y 65 °C | 2,51 m3/h |
| Velocidad en las conexiones de 1" Sch 160 (Ø int. 20,7 mm) | 2,07 m/s (ρ·v² ≈ 30 kg/m·s² con la densidad mayor de la hoja de datos: muy por debajo de los límites usuales de erosión y ruido) |
| Elemento adoptado | 1 cartucho plisado estándar de 10" (Ø 63 a 70 × 254 mm, doble extremo abierto), celulósico, 99,9 % > 10 μm, flujo de afuera hacia adentro; núcleo y tapas metálicos, adhesivo y juntas aptos para 90 °C e hidrocarburos (el estándar con polipropileno no sirve: la operación llega a 65 °C) |
| Velocidad en el medio filtrante (≈ 0,45 m2) | 1,55 mm/s |
| Velocidad en el espacio anular cuerpo–cartucho | 0,054 m/s |
| Pérdida de carga | Elemento limpio: despreciable a este caudal (criterio usual de la industria: hasta 0,14 kg/cm2 limpio; recambio a 0,8–1,0 kg/cm2). El valor garantizado lo da el fabricante del elemento |

- El caudal es tan chico que un solo cartucho de 10" trabaja muy holgado; el Ø 6" del cuerpo sale del mínimo razonable para una tapa bridada con pescante, no del proceso.
- El antecedente AESA/47 (PC-01) usó cartuchos Gora de Ø 42 × 86 mm (mínimo 2 por recipiente): entran en este cuerpo, pero piden otro asiento (Ø menor). La medida final la define el fabricante del elemento; el asiento se adapta sin cambiar el recipiente.
- **Condensado:** el gas tiene ≈ 7,6 % molar de C5 y más pesados (HD nota 19) y puede condensar a 15 °C y 5 kg/cm2 g, más con −10 °C de ambiente (estimación del revisor, de memoria; coincide con la marca E30 del P&ID, consulta C4). El elemento es de partículas, no coalescente: la cámara inferior y el drenaje D juntan el líquido que decante, y el fabricante del elemento tiene que confirmar que el medio celulósico tolera hidrocarburo líquido. Sumado a las consultas C1 y C4.
- Los valores de superficie de medio y de pérdida de carga son típicos, citados de memoria y de folletos de fabricantes; no son garantía.
- La eficiencia 99,9 % > 10 μm es de grado absoluto: hay que pedirla garantizada por escrito al fabricante (el celulósico plisado común es nominal).

## 6. Arreglo interno y elevaciones

| Nivel sobre el piso | mm |
|---|---|
| Eje del drenaje D | 150 |
| Fondo del casquete | 248 |
| Soldadura casquete–caño | 350 |
| Eje de A (entrada) y B (salida) | 600 |
| Asiento del cartucho | 680 |
| Extremo superior del cartucho | 934 |
| Cara de la brida de cuerpo | 1.037 (quedan 103 mm para el platillo de cierre y el resorte) |
| Tope de la tapa | 1.067 |

- **Recorrido del gas:** entra por A a la cámara del cuerpo, atraviesa el cartucho de afuera hacia adentro y sale por el tubo central hacia B. El polvo queda en el cartucho y lo que decanta va a la cámara inferior (250 mm) y al drenaje D.
- **Tubo de salida interno:** caño 1" Sch 160 con codo, desde el cuello de B hasta el centro, con el asiento del cartucho arriba. El tubo también hace de deflector frente a la entrada A.
- **Material de los internos: AISI 316 L.** La C0100 5.1.4 pide para internos soldados de acero al carbono corrosión de los dos lados (3,2 + 3,2 mm) y 10 mm de espesor mínimo: un caño de 1" no lo cumple en ningún schedule. En inoxidable el mínimo es 6 mm (Sch 160 = 6,35 mm) y la corrosión es 0. La hoja de datos no fija el material de internos y pide bulonería AISI 316 L. Requiere procedimiento de soldadura acero al carbono–inoxidable (consultas C6 y C11).
- Espesores de los internos: el caño 1" Sch 160 tiene 6,35 mm nominales (5,56 con la tolerancia): se declara 6,35 nominal en la consulta C11 y, si YPF exige 6 mm con tolerancia, pasa a 1" XXS (9,09 mm). Asiento, platillo soldado y rompevórtice: planchuela de 6,35 mm como mínimo.
- Soldadura de los internos: el tubo se suelda sobre el cuello de B, que queda a ras del interior (C0100 5.3.3), con penetración total y aporte 309 L (procedimiento calificado acero al carbono–inoxidable; C0100 5.3.4 pide en esas soldaduras el sobreespesor del recipiente). El tubo y el rompevórtice se sueldan antes de cerrar el casquete.
- Variante más simple, a ofrecer si el cliente la acepta: internos desmontables (tubo 316 L enchufado en B), que quedan fuera de la regla de internos soldados.
- **Cierre del cartucho:** platillo superior con resorte y varilla roscada de 3/8" AISI 316 L al asiento; se saca por arriba abriendo la tapa.
- **Rompevórtice** sobre el drenaje D (C0100 5.1.9), en cruz de planchuela AISI 316 L.

**Orientación en planta** (0° = conexión B, sentido horario):

| Elemento | Posición |
|---|---|
| B, salida | 0° |
| A, entrada | 180° |
| D, drenaje | 180° (debajo de A), a 60° de las patas vecinas |
| Patas | 0°, 120° y 240° |
| Orejas de izaje | 90° y 270° |
| Pescante | 45° |
| F, venteo (en la tapa) | 180°, a 50 mm del centro |
| Placa de identificación | 270° |
| Puesta a tierra | en las patas de 120° y 240° |

## 7. Soportes, anclaje, izaje y pescante

| Verificación | Carga | Resultado | Admisible |
|---|---|---|---|
| Viento (CIRSOC 102: 48 m/s, I = 1,15) | 648 N; momento en la base 453 N·m | manda sobre el sismo | — |
| Sismo (CIRSOC 103, zona 1; coeficiente adoptado 0,15) | 168 N; momento 126 N·m | no actúa junto con el viento (C0100 5.1.7) | — |
| Pata L 2" × 2" × 1/4" SA-36, compresión (lleno de agua + momento, en el círculo de patas Ø 250) | 2.789 N | 4,6 MPa | 114 MPa |
| Pata, flexión por el corte (en ménsula, eje débil) | 216 N | 30,9 MPa | 114 MPa |
| Pata, esbeltez (largo libre 400 mm, K = 2) | — | 81 | 120 |
| Perno de anclaje M16 (3, uno por pata), tracción con el equipo vacío | 1.495 N | 9,5 MPa | ≈ 100 MPa |
| Oreja de izaje 120 × 80 × 9,5 con agujero Ø 22 (todo el peso × 1,5 en una oreja) | 1.681 N | 4,7 MPa de corte; 14,2 MPa de flexión | ≈ 55 / 90 MPa |
| Pescante, caño 1 1/2" Sch 80, brazo 190 mm (tapa y venteo × 1,5) | 224 N | columna 6,3 MPa; brazo 50 × 12,7 8,0 MPa | 118 MPa |

- Cuentas conservadoras: viento al 100 % con el peso de prueba hidráulica (la C0100 5.1.1 pide solo 50 % en prueba), coeficiente de fuerza 1,2 y Kz = 1; coeficiente sísmico 0,15 adoptado sin derivarlo (el viento manda hasta ≈ 0,5).
- Todo trabaja muy por debajo de lo admisible: en un equipo de 100 kg las secciones salen de mínimos constructivos, no del cálculo.
- **Patas:** 3 a 120°, ángulo de 2" × 2" × 1/4" SA-36, de 550 mm, soldadas con cordón continuo a placas de refuerzo de 150 × 80 × 6,35 mm de SA-516 Gr. 70 roladas al radio del cuerpo (la hoja de datos admite SA-516 Gr. 70 para envolvente y soportes; C0100 5.1.12), con cantos redondeados y agujero testigo 1/8" NPT. Las placas arrancan 50 mm arriba de la soldadura casquete–caño (C0100 5.3.2: las soldaduras circunferenciales no deben quedar afectadas por otros componentes; la distancia mínima la fija la B0500, no recibida). Placas base de 120 × 120 × 9,5 mm con agujero Ø 22. El sistema de patas necesita aprobación de YPF.
- **Anclaje:** 3 pernos M16 en círculo de Ø 330 mm. ITT entrega el diseño y la plantilla; los pernos no se proveen.
- **Orejas de izaje:** 2 a 180°, a 90° de A y B, de 120 × 80 × 9,5 mm, con el agujero Ø 22 a 170 mm del eje para que el grillete libre la brida de cuerpo (Ø 280) y sus tuercas; a más de 50 mm de la soldadura caño–brida; penetración total y líquidos penetrantes (C0100 5.1.13).
- **Pescante:** columna de caño 1 1/2" Sch 80 que gira dentro de un buje de 2" Sch 80 soldado al cuerpo con placa de refuerzo; brazo de planchuela y bulón de ojo de 1/2" con tuerca de maniobra, tomado a un cáncamo en el centro de la tapa. Por eso el venteo F va corrido 50 mm del centro (el agujero y la cupla quedan sobre el interior del cuerpo, lejos del asentamiento de la junta; Ingeniería confirma la exención de refuerzo con el agujero excéntrico, UG-39) (el esquema de la hoja de datos lo dibuja centrado: se aclara en la oferta).
- **Puesta a tierra:** 2 orejas AISI 316 de 50 × 40 × 6 mm con agujero Ø 14, en dos patas.
- **Placa de identificación:** AISI 304 sobre soporte de chapa de 6 mm, a 270°, entre A y B (como en el esquema de la hoja de datos).
- **Sin calcular:** cargas de cañería en A y B (WRC 107 / UG-44 b): AESA tiene que informar las cargas.

## 8. Soldadura, ensayos y terminación

- Juntas circunferenciales (casquete–caño y caño–brida): a tope con penetración total, raíz GTAW y relleno SMAW (ED(EP)-B-05.00: sin GMAW en partes a presión). Cuellos de A, B y D pasantes con penetración total (UW-16).
- Radiografiado por puntos (RT3): 2 placas por filtro. Líquidos penetrantes 100 % en las soldaduras de las 4 conexiones y en las orejas de izaje. Dureza e identificación positiva según ED(EP)-B-02.00.
- Prueba hidráulica a 13,0 kg/cm2 g, 1 hora, con registro, antes de pintar y sin el cartucho.
- Junta de la tapa: espiralada AISI 316 / grafito con anillos interior y exterior, ASME B16.20 (supuesto hasta recibir la clase CA11).
- Pintura exterior sistema 201 de la B0600: arenado SSPC-SP10, cinc silicato, mist coat, epoxi y poliuretano; RAL 9006 el cuerpo y RAL 9011 las patas. Interior sin revestimiento.

## 9. Normas usadas

| Tema | Norma |
|---|---|
| Diseño y fabricación del recipiente | ASME VIII Div.1 última edición (UG-16, UG-20, UG-27, UG-32, UG-34, UG-36, UG-39, UG-44, UG-45, UG-99, UW-11, UW-12, UW-16, UCS-66, Apéndice 2) |
| Materiales y tensiones admisibles | ASME II partes A y D |
| Soldadura y ensayos no destructivos | ASME IX y ASME V |
| Caños | ASME B36.10 |
| Bridas | ASME B16.5 |
| Casquete y codo a tope | ASME B16.9 |
| Cupla y tapones roscados | ASME B16.11 y ASME B1.20.1 (NPT) |
| Junta espiralada | ASME B16.20 |
| Espárragos y tuercas | ASME B18.2.1 / B18.2.2; recubrimiento ISO 4042 |
| Venteo y drenaje aguas abajo de la primera rosca o brida | ASME B31.3 y clase CA11 de la L0200 de YPF |
| Requisitos del cliente | YPF C0100 (recipientes), B0600 (pintura), ED(EP)-B-01.00, B-02.00 y B-05.00 |
| Viento, sismo y nieve | CIRSOC 102 (2015), INPRES-CIRSOC 103 (2018), CIRSOC 104 (2005) |
| Cargas en conexiones | WRC 107 / 537 (pendiente) |
| Patas, orejas y pescante | Práctica habitual de recipientes (D. Moss, Pressure Vessel Design Manual; detalles tipo PIP VEFV1100), citada de memoria |
| Pérdida de carga del elemento | Criterios publicados por fabricantes de filtros de gas (Pall, Parker/Peco): ≈ 2 psi limpio, recambio a 12–15 psi |

Plano de arreglo general: `arreglo_general.svg` y `arreglo_general.png`, en esta carpeta.

## 10. Listado de materiales

Está en `pedido/lista_materiales_plano.csv` (33 renglones por filtro), con el texto de la hoja de datos, cantidad, material y los datos de cada pieza en columnas.

