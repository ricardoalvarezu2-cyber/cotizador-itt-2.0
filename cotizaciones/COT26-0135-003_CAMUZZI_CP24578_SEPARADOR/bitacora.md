# Bitácora COT26-0135-003 · Camuzzi CP 24578 ítem 1 · 2 separadores verticales coalescentes

**Estado: borrador, sin revisar. Precio preliminar (±30%).** Mismo concurso que COT26-0135-001.

## Pedido
Solo la descripción de la planilla de cotización: separador de líquido coalescente vertical sobre skid con plataforma, filtrado 0,3 µm, cartuchos 140 × 914 mm, Pe 70 bar máx / 25 bar mín, Qmáx 100.000 Sm3/h, entrada y salida a 180° preferentemente 10" #600, purga automática, switch de nivel Ex-d en ambas cámaras, manómetro diferencial con aguja de arrastre y contacto seco, manómetro estático, visor de nivel en ambas cámaras, boca de inspección 6" #600 a 90°, salida a 200 mm sobre los cartuchos, 40 mm entre elementos, un juego de elementos por equipo. **Pide memoria de cálculo y esquema con la oferta.** La "especificación técnica adjunta" que menciona **no vino en el RAR**: pedirla.

## Dimensionamiento preliminar (criterio técnico, a reemplazar por la memoria de cálculo)
- Caudal real a la presión mínima (25 barg, 15 °C, Z ≈ 0,94): 100.000 × 1,013 / 26 × 0,94 ≈ **3.660 m³/h**.
- Carga por elemento: la del coalescedor Sacde/12 (ITT, 36" #600, 16 elementos, 3,3 MMSm3/d a ~70 bar ≈ 1.730 m³/h reales → **108 m³/h por elemento**).
- Elementos: 3.660 / 108 ≈ **34**.
- Diámetro: 34 elementos a paso triangular de 180 mm (140 + 40) ≈ 0,96 m² + huelgo → **Ø44" (1.118 mm)**.
- Espesor ASME VIII Div.1 a 70 bar, SA-516-70 (S 138 MPa, E 1, RX 100%): t = P·Ro/(S·E + 0,4·P) = 7,0 × 559 / 140,8 = 27,8 mm + 3,2 de corrosión → **1 1/4"**. Fondo 2:1 de 1 3/8".
- Cuerpo 3,2 m (cámara inferior 1,3 m + placa + cámara de coalescencia): **2.801 kg** de virola.
- **Sensibilidad:** si el fabricante de elementos admite el doble de caudal por elemento, serían ~17 elementos en Ø32"–34" y el costo bajaría ~35% (sobre todo la tapa de cierre rápido y la chapa).

## Costos (por separador)
Tapa de cierre rápido 44" #600 (Megatap 28" escalada: ~29.500) · chapa SA-516 1,80/kg (Sacde/12) · rolado Sandri 1,74/kg · fondo escalado de Sacde/12 · elementos Gora 90 c/u (similar: elemento de separador, no coalescente) · visores Riva 685 · fabricación Ledesma 13.000 (28" + skid, CAMUZZI/30) × 1,6 · RX, PH, pintura, ingeniería 150 h, calidad 120 h y montaje 160 h por criterio. Precio **139.551 c/u** (borrador). Control: CAMUZZI/30 (separador horizontal 28" #600, 11 elementos) se ofertó a 93.033 c/u.

## Pendientes
Especificación del separador (Camuzzi), memoria de cálculo y dimensionamiento con Gora/Pall, cotización de la tapa 44" vertical, purgas automáticas, switches Ex-d, manómetro diferencial con contacto, y fabricación (Ledesma) con el diseño.

## Revisión independiente (28-10-2026, agente que no armó el cómputo)
Transcripción del plano y cantidades: bien. Precios Tormene y Taval verificados contra los originales. Corregido:
- **Error mío de dimensionamiento:** 34 elementos a 180 mm de paso no entraban en Ø44" (calculé el área sin descontar el borde). Con el arreglo triangular real, el anillo completo es 1 + 6 + 12 + 18 = **37 elementos** con centros hasta 0,54 m de radio → DI 1,28 m, **Ø53"**.
- Presión de diseño 77 bar (70 + 10%): espesor 36,7 + 3,2 = 39,9 mm → **1 5/8"** (cuerpo 4.387 kg); fondo 1 3/4".
- Elemento: los 90 de Gora eran de un elemento de separador de polvo, no coalescente: pasa a 400 estimado (Sacde/12 pagó 854).
- Purgas automáticas, switches, manómetro diferencial, internos, RX, PH, pintura, skid y MO de Ledesma: estimados subidos (eran bajos para 70 bar y el tamaño nuevo).
- Precio: **204.970 c/u** (preliminar). Los 108 m³/h por elemento de Sacde/12 no son del mismo elemento: **pedir a Gora o Pall el caudal por elemento de 0,3 µm a 25 bar**. Si admite el doble, alcanza con ~19 elementos en Ø40" y el precio baja mucho.
- **Crítico para presentar:** el concurso exige con la oferta la memoria de cálculo y el esquema con dimensiones; hoy no existen.

## 29-10-2026 · Llegó la especificación (mail de Brian Raminger, Taval, 14-10-2026)
Concurso aparte **Nº 24527** solo para los 2 filtros coalescentes (vencía el 20-10-2026). Adjuntos en `pedido/CP24527_mail_2026-10-14/`: **ET Separador Vertical Coalescente** (22 hojas), **Esquema General Filtro Coalescente Camuzzi 2026** (PDF de imagen, sin texto), listado de marcas y proveedores Camuzzi (789-2), cláusulas particulares, DDJJ ética, PCG CGP/CGS 2023 y la planilla del concurso (misma descripción que el ítem 1 del CP 24578). Matías volvió a pasar la planilla del CP 24578 (idéntica a la de `pedido/`). Pendiente: rehacer el dimensionamiento con la ET y el esquema, y esperar los planos que va a mandar Matías.

## 29-10-2026 · Revisión contra la ET y el esquema de Camuzzi (sin cambiar todavía `cotizacion.json`)
Diferencias encontradas (la cotización se había armado sin la ET):
1. **Presión de diseño baja.** La ET 9.16.1 pide PH a **1,3 × la presión máxima de la serie ANSI** (#600 ≈ 102 bar → ~133 bar) durante 6 h. Con 77 bar de diseño esa prueba no cumple ASME (1,3 × MAWP): el recipiente se diseña a ~102 bar. Espesor estimado: 10,2 × 640 / (138 − 0,6 × 10,2) = 49,5 + **1,6 de corrosión (ET 9; se había usado 3,2)** ≈ 51 mm → 2" a 2 1/8" (era 1 5/8"). Sube chapa, fondo, placa y rolado ~25–30%. La PH cargada (1,5 × diseño, 16 h) también cambia. **[Corregido el 30-10-2026, auditoría: 1,3 × MAWP es el mínimo de la PH en ASME VIII (UG-99), no un máximo; con 77 bar la PH a 133 bar es posible si la memoria verifica las tensiones en la prueba. El diseño a 102 bar es una opción, no una obligación: ver "Auditoría independiente".]**
2. **Repuestos (ET 13.1): un juego adicional de elementos** por equipo, además del instalado. Hoy hay 37 por equipo (≈ 31.600 USD); con el juego extra se duplica. La planilla dice "un juego"; la ET dice "adicional". A decidir.
3. **Tapa de cierre rápido:** Megatap **no está en el listado de marcas de Camuzzi** (SCE-IN-501-0015: Peco, Gora, Futura, EKA). Recotizar con alguna de esas.
4. **Válvulas esféricas Taval:** Taval no figura en el listado (Esferomatic, Worcester, Valvtronic, Pentair, Indave, Wenlen, Spirax, Beta, Valmec). Confirmar con Taval si está homologada (afecta también a COT26-0135-001 y 002).
5. **Purgas (ET 9.2):** 2 automáticas neumáticas NC, internos inox con stellite 6, **1" bridadas**, con interruptor de nivel a flotante; drenaje superior con by-pass esférico e inferior con esférica + **tapón lubricado de sacrificio**. El cómputo tiene esféricas de 2" y no tiene el tapón lubricado. Marcas: control de nivel Epta/Fisher; actuadores Bettis/Bray/Flow/Wenlen; switches Magnetrol/Murphy/Kimray.
6. **Caja de chicanas AISI 304 de doble bolsillo** (ET 9.8 y esquema): hoy "internos" sin precio.
7. **Plataforma galvanizada en caliente**, piso de rejilla tipo Techno, guarda hombre desde 2 m, zócalo de metal desplegado; skid UPN con cáncamos y orejas de PAT AISI 304 (ET 9.11): falta el galvanizado y la rejilla.
8. **Soldadura según API 1104** con procedimientos y soldadores con registro IRAM-IAS U500-138 (ET 9.14): no está la calificación.
9. **Prueba de fugas** con N2 a 5,5 bar después de pintar (ET 9.16.3): no está.
10. Manómetro estático con manifold de 2 vías (no de 3) y accesorios inox doble virola (ET 9.19–9.20). Menor.
11. Transporte: la ET dice hasta destino final; la planilla, hasta Cruz del Sur (E. Echeverría). Se mantiene la planilla, aclarado en la oferta.
12. Esquema: entrada abajo a la caja de chicanas, elementos sobre placa con soporte superior, salida arriba a ≥ 200 mm de los elementos. Coincide con el arreglo cotizado.
Pérdida de carga máxima 100 mbar a Qmáx y Pmín con elementos limpios (ET 9.1): sirve para fijar la cantidad de elementos con la ficha de Gora/Filtron/Peco.

## 29-10-2026 · Corrección contra la ET (decisiones de Matías: incluir el juego de repuesto; usar solo marcas del listado de Camuzzi)
- Diseño a la presión de la serie #600 (102,1 bar), corrosión 1,6 mm: virola y fondo de **2 1/4"** (DI 1.280 mm, ≈ Ø55" exterior, 6.287 kg de virola). La placa portaelementos queda en 1 5/8" (solo soporta la diferencial; a verificar en la memoria).
- **Juego de repuesto** de 37 elementos en fila aparte (5b).
- Tapa: Futura (Sacde/12 escalada) en lugar de Megatap. Válvulas: precio de referencia Taval de la misma especificación, a comprar de una marca del listado (Esferomatic, Worcester, Valvtronic…); 1/2" con Esferomatic (TAVAL/40).
- Purgas según ET 9.2: neumáticas 1" #600 bridadas (sin precio), 7 esféricas 1" #600 de bloqueo y by-pass, tapón lubricado 1" de sacrificio; bridas 2" de 6 a 4, bridas 1" de 7 a 15, esféricas 2" de 6 a 4.
- Nuevos: caja de chicanas AISI 304 y accesorios doble virola (sin precio), rejilla galvanizada 3 m², galvanizado de plataforma 500 kg, prueba de fugas 8 h, calificación API 1104 (sin precio). PH a 1,3 × serie #600 durante 6 h. Visores a pedir para 102 bar. Fabricación Ledesma × 1,18 por espesor.
- Resultado: **USD 284.971,97 c/u, 571.152,19 los 2** (antes 205.839,76 c/u), borrador ±30%. `verificar_computo.py`: 0 errores. Queda en 0 (a cotizar): purgas automáticas, switches Ex-d, chicanas, accesorios doble virola y API 1104.
- Regla nueva de Matías (29-10-2026: similares solo de la misma serie y norma): el tapón lubricado (referencia S-3000 NPT) y los visores Riva (cotizados para 70 bar) pasan a SIN PRECIO. Precio: **USD 282.808,31 c/u, 566.824,87 los 2**.
- Página actualizada desde el repositorio (29-10-2026, `semilla.py --previo`). La página tenía un renglón propio del 29-10 18:10, "Fabricación de la estructura del skid" 1.300 kg × 3 = 3.900 (FAB-00565), que se descartó: la fabricación del skid ya está en S02 (Ledesma, separador + skid) y se contaba dos veces.
- 29-10-2026: la oferta titula la tabla "Lista de materiales elaborada por ITT según la ET y el esquema de Camuzzi (el cliente no entrega lista)" (`oferta.json` → `titulo_materiales`, también en la página) y ya no repite "diseño preliminar ITT" en cada renglón. Números de las descripciones en formato argentino.

## 30-10-2026 · MO contra TAVAL/37 (coalescedor FC-231 YPF, cuerpo Ø32" #600, 16 elementos; planilla LM costos FC-231 REV. 0)
Comparación por equipo, costo (sin factor). TAVAL/37 se fabricaba en ITT; acá el cuerpo y el skid los hace Ledesma.

| Rubro | Este (Ø55", 2 1/4", 37 elementos) | TAVAL/37 (Ø32") |
|---|---|---|
| Ingeniería | 150 h · 2.250 | 250 h + ingeniería Gora · 8.735 |
| Calidad | 120 h · 1.800 | 250 h · 3.750 |
| Montaje propio | 160 h · 2.560 | 1.989 h · 31.824 (incluye armado de tacho, internos, conexionado y armado final: acá van en Ledesma) |
| Soldadura cuerpo y conexiones + rolado | Ledesma 33.643 + rolado 10.939 | 71.442 (propia) |
| RX y LP | 1.426 | 52.196 (1.504 placas) |
| Pintura | 1.900 | 7.552 |
| Total MO y servicios | 55.831 | 186.339 |

Lectura: (1) **RX** es la diferencia más fuerte y no se explica por alcance: el 1.426 sale de 80 placas a tarifa DB NDT (8 USD la grande); para 2 1/4" (gammagrafía) y RX 100% (ET) parece bajo: pedir cotización. Ojo: la tabla de soldaduras de la planilla de TAVAL/37 viene rotulada "SEPARADOR BIFASICO" (resto de plantilla), así que sus 52.196 tampoco son un dato limpio del FC-231. (2) **Ingeniería y calidad**: los dos coalescedores de referencia (Sacde/12 y TAVAL/37) usan 250 h cada una; acá 150 y 120. La ET pide memoria de cálculo. (3) **Ledesma**: los 33.643 salen de escalar un separador horizontal de 28" (×2,2 × 1,18); el TAVAL/37 propio da 71.442 para un equipo más chico: pedir la cotización real con el diseño. (4) Montaje propio: no es comparable (acá lo hace Ledesma).
Además: la ficha contaba 6.931 juntas a tope porque tomaba los 6.916 kg de chapa como piezas (error de `precotizar.soldaduras` / `ficha.js`, corregido: una cantidad en kg o m² no cuenta juntas y avisa). Ahora: 15 juntas.
No se cambió ningún valor de la cotización (decide Matías).

## 30-10-2026 · RX con el precio confirmado por Matías
Proveedor de RX (sin nombre, hablado con el proveedor): ARS 850.000 por visita (hasta 45 placas) + ARS 15.000 por placa, sin IVA, firme (`precios_usuario.csv`). Con las 80 placas estimadas: 2 visitas → USD 1.881,28 (antes 1.426, tarifa DB NDT). Precio: **USD 283.367,32 c/u, 567.942,89 los 2** (borrador). Las placas siguen estimadas: confirmar con el mapa de soldaduras. Ingeniería, calidad y Ledesma sin cambios (pendiente de Matías).

## 30-10-2026 · Ingeniería y calidad a 250 h (decisión de Matías)
Ingeniería 150 → 250 h y calidad 120 → 250 h, como los coalescedores Sacde/12 y TAVAL/37. Precio: **USD 288.966,36 c/u, 579.140,97 los 2** (borrador). Página actualizada (`semilla.py --previo`). Pendiente: cotización real de Ledesma y placas de RX con el mapa de soldaduras.

## 30-10-2026 · Reglas de compatibilidad sobre la cotización
Pos 15 (válvula esférica 1/2" roscada, 8 u): la referencia era una Esferomatic SW-roscada (USD 55,90, TAVAL/40), otro extremo: con la regla nueva no sirve y no hay otra en el catálogo → **SIN PRECIO, pedir cotización**. Precio: **USD 288.314,94 c/u, 577.838,13 los 2** (borrador). Página actualizada.

## 30-10-2026 · Compatibilidades revisadas
Pos 14b (esférica 1" #600 RF, A216 WCB): SIN PRECIO (la Taval de referencia no dice el material). Pos 23b (rejilla galvanizada): SIN PRECIO. Unitario USD 285.832,80, 571.665,60 los 2 (borrador).

## 30-10-2026 · Revisión completa renglón por renglón (pedido de Matías: "revisar por completo los presupuestos de Camuzzi")
Hecha por un agente sobre `armar_json.py` (única fuente: regenera la lista, `cotizacion.json` y `oferta.json`; correrlo de nuevo no deshace nada). **Sin revisión independiente todavía.**

**Resultado (salida de `armar_cotizacion.py`, borrador sin revisar):** antes USD 285.832,80 c/u y 572.873,85 los 2 con flete (costo 211.728,00); ahora **USD 346.355,34 c/u y 698.070,92 los 2** (costo 256.559,51). `verificar_computo.py`: 0 errores. Quedan 9 renglones en 0 (SIN PRECIO, con motivo y en la lista para Compras): 14b, 14c, 16, 16c, 18, 20, 20b, S05d (API 1104) y S05e (tratamiento térmico).

**Diseño y requisitos**
- Matriz de requisitos `pedido/requisitos.csv` (148 renglones con texto literal, documento y hoja: planillas de los dos concursos, cláusulas particulares 24578 y 24527, ET, esquema, listado de marcas y pliego general). 10 quedan en `consulta` y frenan: memoria y esquema (pendientes de ITT, se exigen con la oferta), C1 concurso 24527 con apertura vencida, C2 elemento celulósico (ET 9) o coalescente (planilla), C3 destino final, C4 temperatura de diseño y plano tipo, C5 especificaciones SCE citadas que no vinieron. Redactadas en `consultas_cliente.md` (no se envió nada).
- Tratamiento térmico post soldadura agregado (S05e): ASME VIII UCS-56 lo exige en P-No.1 de más de 38 mm (acá 57,15 mm). Sin la temperatura mínima de diseño no se puede eximir de Charpy (UCS-66): consulta C4; la chapa pasa a 70N si hace falta.
- Purgas (ET 9.2): la purga automática se separa en válvula neumática NC (16), interruptor de nivel a flotante que la comanda (16b) y regulador de gas de instrumentos (16c, faltaba).
- Manómetros: el manifold de 3 vías pasa al diferencial (19b, ET 9.19.2) y el estático lleva bloqueo y purga de 2 vías (20b, ET 9.19.1 y 9.20).
- Accesorios doble virola (ET 9.20) con precio ABAC de TAVAL/40: conectores 1/2" y 1/4" y tubing 1/4" (21b–21d).
- Placa de identificación inoxidable (25, ET 9.12). Orejas de PAT y cáncamos en la descripción del skid (23) y en el alcance de Ledesma.
- Elementos: la descripción dice lo que piden los dos documentos (planilla coalescente, ET celulósico) y se cotiza el coalescente (854, el más caro) hasta la respuesta de C2. Proveedores corregidos al listado de Camuzzi (Gora, Filtron, De Nichilo, Panden, SP; Peco solo está homologado para tapas).
- Desvíos declarados en la oferta: moneda USD (24527 y pliego 18.1 piden pesos salvo importados) y plazo (24527 pide 30 días). Referencia y objeto de la oferta nombran los dos concursos.

**Materiales (fuente en cada renglón)**
- Tapa (3): escalada al DI 50,4" (antes 53") con el exponente de las dos tapas Futura #600 cotizadas (16": 8.432, TAVAL/40; 36": 24.288,60, Sacde/12 → 1,305; antes 1,5 sin fuente): 43.387,29 → 37.668,33. **[Corregido por la auditoría: la Futura 36" se designa por el diámetro exterior; escalada a 54,9" da 42.103,38.]**
- Brida ciega 6" (9): Provemet ciega 8" #600 (172,28, BRI-01064) en lugar de WN 6" + 10% sin fuente.
- Válvula 1/2" S-2000 NPT (15): Taval lista 30 VAL-04865 (36,06) como precio de referencia de una marca del listado (estaba sin precio "porque no había": sí había).
- Switches Ex-d (17) e interruptores de purga (16b): switch de nivel de Sacde/12 (2.500).
- Chicanas AISI 304 (21): planilla TAVAL/37 (6.000, caja 800 × 400 × 400, valor "a calcular" de ITT); Gora cotizó una de 250 × 250 × 150 a 615.
- Rejilla (23b): TAVAL/37 rejilla TDL SA-36 a 265/m², galvanizada con la plataforma (S05b pasa a 620 kg).
- Pasan a SIN PRECIO por la regla "sin material no es similar": válvula neumática (16, la de control de Sacde/12 no dice material), manómetro estático (20, Weisz no dice caja ni bourdon) y bloqueo y purga (20b, la ABAC es AISI 316 y la ET pide A105 zincado: `compatibilidad.py` no admite el reemplazo).

**MO y servicios**
- Rolado (S01): Sandri cilindra hasta 50 mm (membrete de su cotización) y la virola es de 57,15 mm: la base pasa a la tarifa de rolado 3,70 USD/kg (tarifas.csv, AESA/44): 10.939 → 23.262. Pedir cotización a un taller con capacidad.
- Fabricación Ledesma (S02): el factor × 2,2 por tamaño sobre el separador 28" de CAMUZZI/30 no tenía fuente. Base nueva: presupuestos de Ledesma de recipientes a presión de AESA/44 (27-08-2025), 4,15 USD/kg del de 8.967 kg (el de peso más cercano; el de 11.860 kg da 3,14) × 9.848 kg (virola, fondo, placa, skid, pollera y conexiones): 33.643 → 40.869. Alcance igual (virolas, soldaduras, casquetes, conexiones, internos, plataforma); no incluye consumibles ni rolado. **[Corregido por la auditoría: AESA/44 es de pared fina; se suma S02b por espesor y S02c consumibles.]**
- RX (Matías, 30-10), ingeniería y calidad 250 h (Matías, 30-10), PH, pintura, prueba de fugas y montaje propio: sin cambios. API 1104 y tratamiento térmico sin precio (Compras).
- Flete: 2 viajes de semirremolque a 1.750 + 780 USD por equipo (Suan, AESA/44, 09-2025) + 300 de embalaje; antes ARS 1.400.000 por un camión con hidrogrúa para los dos (≈ 20 t), sin fuente. Destino a confirmar (C3).

**Plazo y antecedentes**
- Plazo 165 → 175 días (se suma el tratamiento térmico después de soldar el cuello de la tapa). Con el margen de la regla serían 201–210; el histórico de separadores es 370. Lo decide Matías.
- Antecedentes: el −48% contra TAVAL/37 (ahora −37%) es de alcance, explicado rubro por rubro en `justificaciones.antecedentes` con los números de su planilla (TAVAL/37 suma 2 skids de cañería 10"/16", válvulas 10" e instrumentación cableada por ≈ 150.000 y MO propia de toda la cañería con 1.504 placas de RX; su recipiente solo costó 54.951 sin tapa de cierre rápido).
- Vencidas: 10 renglones (bridas y caños 2025, listas Taval, perfiles Provemet y Ledesma AESA/44) siguen frenando: van a Compras para reconfirmar; no se escribió justificación.

### Errores encontrados en la revisión del 30-10-2026
1. **`armar_json.py` desincronizado de `cotizacion.json`:** las decisiones del 30-10 (RX con el precio de Matías, ingeniería y calidad 250 h, 14b/15/23b sin precio, segunda fuente del elemento) estaban solo en `cotizacion.json`; correr el programa las deshacía. Corregido: todo está en `armar_json.py`.
2. **Rolado imposible:** la base era Sandri, que cilindra hasta 50 mm; la virola es de 57,15 mm.
3. **Factor sin fuente:** la fabricación de Ledesma se escalaba × 2,2 "por tamaño" sin dato.
4. **Tapa mal escalada:** a 53" (no es el DI ni el diámetro exterior) y con un exponente 1,5 supuesto. **[Corrección de la auditoría: el error fue mío al escalar por el DI; las tapas se designan por el diámetro exterior.]**
5. **Faltaba el tratamiento térmico** que el código exige por espesor (UCS-56).
6. **Purga automática incompleta:** sin el interruptor de nivel que la comanda ni el gas de accionamiento (ET 9.2).
7. **Manifold de 3 vías en el manómetro equivocado** (la ET pide 2 vías en el estático y 3 o 5 en el diferencial).
8. **Pos 15 dejada sin precio con un dato falso** ("no hay 1/2" S-2000 NPT en el catálogo": está VAL-04865).
9. **Proveedor fuera del listado sugerido para los elementos** (Peco; homologado solo para tapas) y material "fibra de vidrio" puesto por ITT cuando la ET dice celulósico y la planilla coalescente.
10. **Brida ciega con un recargo supuesto** (WN + 10%).
11. **Faltaba la placa de identificación** (ET 9.12).
12. **No se habían leído las condiciones del Concurso 24527:** moneda en pesos, plazo de 30 días, destino final a determinar y apertura del 20-10-2026 ya vencida.
13. **Flete sin fuente** y corto para dos equipos de ≈ 10 t.
14. Herramientas (no se tocaron; van en el informe): `ficha_rubros.py` da 38.862 m² de pintura de piping (cuenta la chapa en kg como largo equivalente); `compatibilidad.py` leyó "ABAC VA 350" como material A350 LF2; el control de material de instrumentos depende de si la descripción nombra materiales (el manómetro estático pasaba antes porque no los nombraba).

## 30-10-2026 · Auditoría independiente de la revisión: hallazgos verificados contra los originales y correcciones
**Resultado (salida de `armar_cotizacion.py`, borrador sin revisar):** antes de la auditoría USD 346.355,34 c/u y 698.070,92 los 2; ahora **USD 376.240,31 c/u y 757.840,86 los 2** (costo 278.696,52). `verificar_computo.py`: 0 errores.

**Hallazgos verificados y corregidos**
- **2. Ledesma de pared fina:** confirmado. Los recipientes de AESA/44 son de 2,5 m × 17 a 22 m y 6 a 16 t (pedido de flete a Suan, 01-09-2025), es decir ≈ 10 mm de pared; el presupuesto 20079 dice "No incluye … Consumibles". Ledesma queda a 4,15 USD/kg (S02) para el trabajo de pared normal. Se agrega **S02b**, la soldadura extra por espesor: 1.401 pulgadas equivalentes (regla de factores_soldadura.csv, espesor ÷ 9,53, en las costuras del cuerpo, la placa y las toberas) × 12 USD/pulg-eq de Quesada (JQ-020-2026, incluye consumibles) = 16.812. Va como estimado. Se agrega también **S02c**, consumibles de Ledesma: sin precio en el catálogo, queda en 0 y frena.
- **3. Tapa:** confirmado, la Futura 36" se designa por el diámetro exterior (la de 16" es de 406 mm). Escalada a 54,9": 37.668,33 → 42.103,38. Mi "error 4" del 30-10 estaba mal planteado: el error fue mío al escalar por el DI.
- **4. Justificación TAVAL/37:** confirmado que era falsa. La hoja "Mano de Obra de ITT" separa el cuerpo principal y las cunas (soldadura 36.858, RX 27.314) de los skids A (20.196 / 15.485) y B (14.388 / 9.397). Además ≈ 1.125 h de las 1.989 de montaje son del recipiente. Se reescribió con esos números: la MO del recipiente da parecida (≈ 82.200 allá, 81.882 acá) y la diferencia es de alcance. RX: las placas se contaron por costura, 43 grandes + 46 chicas = 89 (antes 80 por criterio): 1.968,85. El conteo de 816 placas de TAVAL/37 sale de una plantilla de "separador bifásico", no de su recipiente. Se agregan las tintas penetrantes **S03b** (2 servicios de Antonelli a 490), que faltaban.
- **5. Elemento:** confirmado, TAVAL/37 y Sacde/12 son la misma plantilla (16 u a 854, sin tamaño). Se sacó "confirma el valor".
- **6. Plazo:** confirmado.
  - Futura cotizó la tapa a 120 días (Sacde/12, "plazo 120 dias"); los 90/110 eran de Megatap, que está fuera del listado.
  - La tapa ahora se pide con el plano aprobado (ET 7.1 y 10). Se suponen 15 días de revisión de Camuzzi, porque la ET no los fija, y la oferta lo dice.
  - Plazo calculado: 200 días; con el margen de 15% de plazos.md §4 se ofrecen **230** (antes 175).
- **7. Fundamento de los 102 bar:** confirmado que estaba mal escrito. No se cambia el diseño; quedan dos opciones para Matías o la dirección:
  - **(a) Actual:** diseño a 102,1 bar, 2 1/4", PH a 133 bar.
  - **(b) Alternativa:** diseño a 77 bar, 1 5/8" (41,3 mm). La PH a 133 bar se verifica en la memoria: membrana ≈ 214 MPa, menos del 90% de la fluencia de SA-516-70 (260 MPa). Efecto:
    - ≈ 2 t menos de chapa por equipo, entre virola y fondo.
    - La virola la puede rolar Sandri (hasta 50 mm).
    - Menos soldadura extra por espesor.
    - El tratamiento térmico sigue, porque 41,3 mm es más de 38 mm.
- **8. Oferta:** se declaran el elemento ofrecido (coalescente, la ET dice celulósico; C2 sigue abierta) y el manifold del diferencial en inoxidable del listado en lugar de zincado (requisito ET 9.19.2 → desvío).
- **9. Kilos de la virola:** confirmado. Con el diámetro medio dan 6.031 kg (antes 6.287 con el exterior); cambian M01, S01 y S02.
- **10. Juntas:** se agrega el segundo juego (**22b**, ET 9.16.3) y los requisitos de reemplazo de juntas y de aviso de llegada con 5 días hábiles (ET 13).
  - Error adicional encontrado: M22 usaba la cotización 48.729 de MS Juntas, que es de juntas **#300** (otra serie).
  - Las juntas pasan a las #600 de la planilla TAVAL/37.
  - Los espárragos B7/2H zincados quedan aparte (**22c**, 88 un a 10, JUN-04181).
- **11. Flete:** confirmado, 1.750 + 780 es el costo que ITT cargó para el SB-003 en la hoja "Transporte" de su planilla de AESA/44, no una cotización de Suan. Fuente corregida.
- **12. CAMUZZI/30:** se corrigió "tomado de".
- **13. Rolado:** pasa a estimado, porque es tarifa interna de ITT y nunca se cotizó para 57 mm.
- **Pintura:** con la superficie corregida de la ficha (recipiente 25,5 m²) y el skid sin la plataforma galvanizada (≈ 32 m²) da 58 m² (antes 38).

**Hallazgo rechazado**
- **1. Cargar como estimado la segunda referencia de los renglones en 0** (M14b Taval 162, M16 válvula de control 2.000, M20 Weisz 120): lo probé y `verificar_computo.py` da ERROR. Las tres referencias no dicen el material, y la regla de compatibilidad (Matías, 30-10-2026; CLAUDE.md) no admite un estimado sobre una referencia sin material. Quedan en 0 con la referencia como orden de magnitud (≈ 5.250 por equipo entre las tres), y frenan.
- M18 (visores) también queda en 0: Matías decidió el 29-10 que la Riva para 70 bar no es referencia.
- M14c, M16c, M20b, S05d y S05e no tienen ninguna referencia.

**Frenos**
- **Requisitos:** R017 y R018 pasan a `pendiente_itt`; quedan las consultas C1 a C5.
- **Sin precio:** 10 renglones (los motivos dicen que falta precio, así que frenan).
- **Estimado:** 17%. No se justificó.
- **Vencidas:** 11. Se agrega la de Antonelli; no se justificó.
- **Datos entre corchetes de la oferta.**

## 05-11-2026 — Actualización con los precios nuevos del catálogo (pedido de Matías: «revisá y rehacé las cotizaciones de Camuzzi»)

- Se cruzó cada renglón con el catálogo actualizado (listas Provemet 29-10-2026, Oil Metal 37278, Miyashiro 50594). Solo cambian los renglones con la **misma pieza** y precio más nuevo; donde la marca se eligió por el listado SCE-IN-501-0015 (Cintolo / Curvo Sold) se mantiene, y las juntas nuevas (#300) no son de la serie pedida.
- Granallado y pintura: USD 37,98/m² (PIN-00579, precio firme confirmado por Matías el 30-10-2026, mismo alcance: granallado y pintura con materiales). La planilla de origen lo aplica sobre los m² + 20 % de overspray, así que la cantidad va × 1,2. Antes: criterio ITT 50 USD/m² (queda de alternativa).
- Fecha de referencia del ajuste: 31-10-2026 (todavía no hay índices de noviembre).
- Provemet 29-10-2026: brida WN 10" #600 sch 80 338,45 → 301,86 (cot. 288978 ítem 12); caño 10" sch 80 204,43 → 168,01 (cot. 288974 ítem 12); brida WN 6" #600 sch 80 226,14 → 112,28 (cot. 288978 ítem 8); caño 6" sch 80 90,70 → 74,52 (cot. 288974 ítem 10).
- Pintura: 58 m² × 1,2 = 69,6 m² a 37,98.
- Precio unitario 376.069,98 → **375.344,72** (total 2 equipos con flete 756.049,68), borrador.
- Revisión independiente (05-11-2026): los 8 precios Provemet coinciden con el PDF y la pieza con el plano; el × 1,2 de la pintura está en la planilla de origen (=D×37,98×1,2, «Overspray 20%»). Corregido después: la fecha de los precios que no cambiaron había pasado a hoy (HOY se usaba también como referencia: vuelve a 30-10-2026); dólar de octubre cerrado 1.543,23 (era 1.541,43); caño 10" PSL2 aclarado (igual o superior al A-106 Gr B); la descripción de la pintura dice el 20 % de overspray. A confirmar por Matías: el precio de pintura es de piping y skid y se aplica también al recipiente (25,5 de los 58 m²).
- Para confirmar: Provemet da el precio con bonificación 4 % por compra total, para las cantidades cotizadas (no las del plano) y con validez hasta el 13-11-2026.
- Precio unitario final: **375.341,76** (total con flete 756.043,69), borrador.

## 05-11-2026 — Rehecha sobre el plano tipo SCE-RE-112-0001 rev. 1 (circular de Camuzzi)

- Camuzzi mandó por circular el plano tipo «Separador vertical coalescente» SCE-RE-112-0001 rev. 1 (archivo «671 1 0», 29/09/2020) y el esquema general. El plano fija la construcción (39 referencias) y una tabla de dimensiones según la serie (A) y la cantidad de cartuchos (B, hasta 20). Parámetros para serie 600: diseño 70 bar, PH 91 bar, corrosión 1,6 mm, RX 100 % tope, LP 100 % filete, ASME VIII Div. 1 y IX.
- Decisión de Matías (05-11-2026): rehacer sobre el plano con A = #600 y B = 20 (fila máxima: la planilla pide 10" #600 y en la tabla D1 = 10" solo con B = 17 y 20). Consulta al cliente en `consultas_cliente.md` (cantidad de cartuchos, PH 91 bar contra la ET 9.16.1, cartucho de papel o coalescente, SCE-RE-512-0001 y SCE-PC-511-0003).
- El diseño propio anterior (55", 37 elementos, 2 1/4", 102 bar, 375.341,76 por equipo) queda en `armar_json_diseno_preliminar_2026-10.py` como historial.
- Nueva base: cuerpo 36" × 31,75 mm SA-516-70 (2 virolas de 1,5 m: Sandri las puede rolar), cabezal 2:1, tapa Futura 36" #600 (igual a la de Sacde/12, 24.288,60), toberas 10", boca 6", 20 cartuchos + 20 de repuesto, caja de chicanas 900 × 900 × 570, sin tratamiento térmico (UCS-56 lo exige desde 38 mm). Las cantidades que el plano no da las contó ITT del dibujo (vistas lateral y corte A-A) y van con la aclaración en `cantidad_origen`.
- Referencia débil a confirmar: cartucho Gora 46600 (113,83, PPTO 27131) no dice la medida y es de fibra de vidrio; el plano pide papel 5½" × 36".
- Resultado (borrador, sin revisar): **140.980,08 por separador**, 284.789,92 los 2 con flete (antes 375.341,76 / 756.043,69).
