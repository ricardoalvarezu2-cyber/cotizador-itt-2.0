# Bitácora COT26-0135-001 · Camuzzi CP 24578 ítem 2 · Skid de regulación (ERP Parque Industrial Tres Arroyos)

**Estado: borrador, sin revisar.** Pedido recibido el 28-10-2026 por Matías (RAR del concurso, copia en `fuentes_originales/pedidos_web/2026-10-28_camuzzi_cp24578/`).

## Pedido
- Concurso de precios N° 24578 "Adquisición de SKID DE REGULACIÓN – MEDICIÓN" (Camuzzi Gas Pampeana / del Sur). Tres ítems: 1) 2 separadores coalescentes (COT26-0135-003), 2) este skid de regulación, 3) skid puente de medición (COT26-0135-002).
- Plano SCE-RE-315-0048 rev 0 y especificación SCE-RE-515-0032 (19-10-2026). Pe 15-10 bar, Pr 4 bar, Q 1.000–6.000 Sm3/h.
- Cláusulas: plazo a indicar, validez 30 días, entrega en Transporte Cruz del Sur (Tapiales) con flete a cargo del proveedor, pago 30 días f.p.f., USD al BNA divisa del día de factura, multas automáticas, DDJJ de ética.

## Qué se hizo
1. Tabla del plano transcripta completa (`pedido/lista_materiales_plano.csv`), con los sensores A, B y C. **Los caños no tienen cantidad en el plano ("_")**: se midieron del dibujo con la escala del skid (3.700 mm): 3" 1,8 m, 6" sch 40 2 m, 6" sch 80 2,1 m, 8" 1 m (±20%).
2. `precotizar.py` y correcciones en `armar_json.py` (cada una con su fuente):
   - Pos 1 y 2: Tormene TA956 3" #300 (ALONZO RED/2, ERP Pilará, 16-06-2026): monitor 9.545, activo 6.073. Es la única cotización 2026 de reguladoras pilotadas en la base. Similar: #300 y otras presiones.
   - Pos 3 y 4: Lista 30 Taval × 0,52 (PR flotante 3" 126, 6" 466), con factor de válvulas Taval.
   - Pos 10: te de reducción 8"x6" Renard 283,84 (precotizar no la encontró: el texto "Te de reducción" con Ø "8"x6"").
   - Pos 15, 16, 18 y C: estimados sin referencia (toma multiport ABAC 250, alivio S-71 180, termovaina 120, switch 350).
   - Pos 20: skid 330 kg estimados (UPN 120 Provemet 1,30 USD/kg +10%) + fabricación 330 kg × 3 USD/kg.
   - Compra extra de caño: media tira (6 m) en lugar de 12 m (con 1–2 m usados, el sobrante superaba el 80%).
   - Juntas y espárragos (nota del plano): 12 juntas 3", 4 de 6" y 1 de 8" con sus espárragos; no las de conexión a la planta.
3. MO: soldadura propia 195,5 pulg-eq × 16, RX 100% DB NDT, pintura, horas del antecedente de skid (Sacde/15). Alternativa de tercero: Ledesma 200295 (TAVAL/69, 2 skids de regulación y medición YPF, 17.200 → 8.600 por skid).

## Control contra antecedentes (P8)
- **CAMUZZI/23** (OC 4500150421, 03-2025): skid de regulación/medición SCE-RE-315-0047 vendido a **24.454**. Este sale **78.580**: la diferencia es casi toda las reguladoras (31.236 de costo, ×1,35 = 42.169 de venta). Hay que confirmar qué reguladoras llevaba el de 2025 y pedir cotización #150 para estas condiciones antes de presentar: con reguladoras de ~4.000 c/u (como la de Sacde/15) el precio bajaría a ~45.000.

## Pendientes
Ver `cotizacion.json` → pendientes. Lo crítico: precio de reguladoras y monitoras #150, si los sensores A/B/C los provee Camuzzi, y los largos de caño.

## Revisión independiente (28-10-2026, agente que no armó el cómputo)
Transcripción del plano y cantidades: bien. Precios Tormene y Taval verificados contra los originales. Corregido:
- Pos 19: faltaba el manómetro (solo estaba el bloqueo y purga): 80 + 150.
- Pos 23: 6" sch 80 2,25 m (2 × 1.000 + 250 de bajada).
- Pintura: se suma el skid (≈ 10,7 m²). Prueba de fugas con N2: renglón propio (250 estimado).
- Quedaron archivos de plantilla en `oferta/`: borrados.
- **Sigue abierto (crítico):** la monitora Tormene cotizada trae bloqueo OPSO y es #300 (el plano no pide OPSO y es #150), y el switch de posición (pos C) puede estar incluido en la reguladora. Pedir cotización #150 sin OPSO. Explicar contra CAMUZZI/23 (24.454) antes de presentar.

## 29-10-2026 · Lista igual al plano (pedido de Matías)
- `pedido/lista_materiales_plano.csv` corregida para que descripción y MATERIAL/OBS. digan lo mismo que el plano (antes había materiales reinterpretados, "RF" y "radio largo" agregados y textos cortados a 60 caracteres por `precotizar.py`, ya corregido). Lo que agrega ITT (planos tipo, kg estimados, largo medido de los caños) pasó a la columna `modelo_fabricante`.
- Tes en ASTM A-105 y cupla en ASTM A-106 como dice el plano: se sacaron los desvíos "se cotiza A-234 WPB / A-105"; el precio es de la pieza similar y Compras pide la del plano.
- Esféricas: marca del listado de Camuzzi (Taval no figura); precio Taval de la misma especificación como referencia y sin el factor de válvulas Taval (ahora llevan 1,35).

## 30-10-2026 · Reglas de compatibilidad sobre la cotización
Pos 17 (cupla 1/2" SW/NPT): la referencia era una cupla BSPT (otra rosca); pasa a la cupla NPT AFO-00715, mismo precio (USD 2,71). El total no cambia. Página actualizada.

## 30-10-2026 · Compatibilidades revisadas
Pos 14 (cupla c/ válvula esférica, A-106): SIN PRECIO (la referencia A105 es otra clase de material). Pos 23 (caño 6" A-53 sch 80): pasa a CAN-01512 A106 Gr B sch XS, mismo precio (USD 90,70). Unitario USD 76.498,56.

## 30-10-2026 · Auditoría independiente de compatibilidades
- Pos 5c (espárragos 5/8" B7 + 2H): la referencia era B7M (menor resistencia, no reemplaza a B7). Pasa a JUN-04173 "Espárragos con 2 tuercas 5/8" x 110 mm A-193 Gr. B7 / A-194 Gr. 2H. Zincados", USD 10 c/u (Bules o Versailles, planilla TAVAL/43, 19-02-2026, verificado en el texto, línea 147). Más largo que el pedido (sirve). La planilla pone USD 10 también al de 7/8" × 230 mm: parece valor global, **pedir cotización**.
- Pos 21 y 21b (caño 3" sch 40 A-53 Gr B): la lista de Renard dice "A53A" (grado A, con costura; verificado en `renar_lista_2025-12.xlsx`, cód. 1007). Pasa a cód. 1153 "Tubo s/costura 88,9 x 5,49 mm A53/A106/API 5L B", USD 25,08/m (misma lista). Cantidades sin cambio.
- Pos 15 (toma multiport 1/2" 3000): la referencia era un manifold serie 2000: otra serie no es similar → SIN PRECIO, pedir cotización a ABAC.
- Unitario USD 76.572,52 (antes 76.498,56); total USD 77.176,64. Borrador, sin revisar.

## 30-10-2026 · Segunda auditoría independiente
- Pos 22/22b y 24/24b (caños 6" y 8" sch 40 A-53 Gr B): la lista de Renard dice "A53/135" sin grado. Pasan a cód. 1173 "Tubo s/costura 168,3 x 7,11 mm A53/A106/API 5L B" USD 60,51/m y cód. 1181 "219,1 x 8,18 mm" USD 91,01/m (misma lista, verificados en el original).
- Pos 6b y 7b (juntas 6" y 8" #150): la de MS Juntas es #300 (otra medida de junta) → SIN PRECIO, pedir cotización a MS Juntas.
- Pos 23b: tenía otra pieza (CAN-02603, sin material) que la pos 23 → la misma CAN-01512 A106 Gr B XS de la pos 23, USD 90,70.
- Pos 5c: el precio de USD 10 pasa a estimado (la planilla pone el mismo valor a todos los tamaños).
- Unitario USD 76.781,76; total USD 77.385,88. Borrador, sin revisar.

## 30-10-2026 · Tercera auditoría independiente
- Pos 1 y 2 (válvulas monitora y reguladora 3" #150): la oferta de Tormene es **#300** (y la monitora con OPSO). Otra serie no es similar → SIN PRECIO hasta tener la cotización #150. El pendiente crítico ya estaba anotado; el control nuevo de serie lo frena.
- Pos 6c/7c: USD 10 de la planilla Techint/12 (columnas ambiguas) pasa a estimado.
- Unitario USD 31.965,44 (antes 76.781,76: faltan las dos reguladoras). Borrador, sin revisar.

## 30-10-2026 · Revisión completa (pedido de Matías: "revisar por completo los presupuestos de Camuzzi")
Antes: unitario USD 31.965,44, total USD 32.569,56. Después: **unitario USD 37.730,89, total USD 38.335,01** (salida de `armar_cotizacion.py`; borrador, sin revisar; **sin las reguladoras, la junta 8", el tubing, la termovaina, la pos 14 ni el switch**, que siguen en 0 hasta que Compras traiga precio). Costo directo: materiales 9.775,11 → 11.819,10; MO y servicios 12.249,75 → 14.144,48.

**`armar_json.py` reescrito:** ahora tiene todas las correcciones (también las de las tres auditorías de compatibilidad, que estaban solo en `cotizacion.json`) y correrlo dos veces da el mismo archivo (probado).

**Requisitos:** `pedido/requisitos.csv` con 80 requisitos literales (planilla, cláusulas particulares, CGP, ET, plano, DDJJ), cada uno con destino. 4 quedan como consulta (borrador en `consultas_cliente.md`, lo manda Matías): R76 cantidad de la pos 14 (tabla 2, dibujo 4), R78 pos 14 en ASTM A-106, R77 caño 23 sch 80 contra bridas/reducciones STD, R33 documentos técnicos de Camuzzi que no están (SCE-RE-110-0006, SCE-PC-511-0003, SCE-IN-501-0008, SCE-RE-308-0001, SCE-IN-301-0005, SCE-IN-501-0003). Se copió a `pedido/` el listado de marcas SCE-IN-501-0015 rev 1 (10-02-2026) que estaba en la carpeta de la 003.

**Materiales** (fuentes en `armar_json.py`):
- Pos 1, 2 y C: siguen SIN PRECIO (Tormene #300 descartada); a Compras con los modelos homologados del listado (TA956 FC/DFO, Fiorentini Reflux/Aperflux, Fisher EZR).
- Pos 3 y 4: Taval lista 30 como referencia; la diferencia aclara que no incluye el ensayo SCE-RE-308-0001 con certificado firmado (ET 5.6.2) y que se compra marca del listado.
- Pos 14: SIN PRECIO hasta la respuesta R78. Pos 15 (toma multiport) USD 312 y pos 16 (alivio, tipo S70/H200) USD 465 estimados de la planilla de costo de Camuzzi ERP Caseros (CAMUZZI/14, 15-03-2022, renglones 18 y 48). Pos 17: se suma el tapón (Renard cód. 5979, USD 1,90) y se corrige el código (5292 NPT; se citaba 5281, que es la BSPT). Pos 18: la del stock es 316L, que no reemplaza a 316 → SIN PRECIO.
- Sensores: A = Rosemount 2051TG (Induquip 26-523, 17-07-2026, USD 1.478) + bloqueo y purga ABAC USD 80 (antes ABB sin bloqueo y purga; ABB no está en el listado); B = Rosemount 644H + RTD 214C (USD 1.138,98; antes ABB 1.448,33). Alternativa Yokogawa (CV Control) con 140 días de plazo.
- Juntas: 6b → JUN-01702 6" #150 estimada USD 12,99; 7b sigue SIN PRECIO (MS Juntas además no está en el listado).
- Agregados de ITT (aclarados en la oferta): 17b 8 cuplas 1/2" NPT 3000 y 18b 3 cuplas 3/4" para montar 15, 16, 18, 19 y A (el dibujo las muestra soldadas al caño, la tabla no las lista); 2b tubing y accesorios inoxidables de doble virola (ET 5.8, SIN PRECIO); 20b placa de identificación (ET 7, USD 10 de CAMUZZI/14).
- Marca exigida por posición en `compras.proveedores` (listado SCE-IN-501-0015).

**MO y servicios:**
- Soldaduras contadas junta por junta del dibujo (planta y corte A-A): 37 a tope (12 × 3", 19 × 6", 6 × 8") + 15 cuplas SW = 212,44 pulg-eq (antes 195,5: la precotización estimaba juntas = extremos × 0,75 y no tenía las cuplas agregadas). Detalle en la especificación de S01.
- RX: tarifa confirmada por Matías (precios_usuario.csv, 30-10-2026): 136 placas → 4 visitas = USD 3.529,19 (antes DB NDT 2.803,50 con LP). LP aparte (DB NDT 294) y procedimientos de RX y LP (Antonelli 2 × 250, ET 3.1.3).
- Prueba de fugas (ET 5.4.3): 8 h de planta × USD 13 (estimado; antes 0 sin referencia).
- Ingeniería 30 h, calidad 70 h y montaje 215,1 h siguen estimadas de Sacde/15 (sin antecedente de Camuzzi con horas).

**Plazo:** el último material son los transmisores (Rosemount 12 semanas = 84 días); las reguladoras se piden después de que Camuzzi apruebe el modelo (ET 5.6.1): días 20 a 80. Taller sin superponer 65 días → calculado 149; con el margen de 15–20% (plazos.md §4) 171–179 → **se ofrecen 175 días** (antes 120, menor que el calculado). Mediana real de la familia SK: 162.

**Antecedentes (P8):** ninguna ficha tiene costo por equipo. El único antecedente con costo por rubro del mismo cliente y subtipo es CAMUZZI/14 (salto ERP Caseros, 4" #150, 15-03-2022, sin ajustar): piping 17.299 (con una te 12"x10" sch 80 de 9.880), skid 1.142, válvulas e instrumentos 46.363 (de los cuales reguladoras 4" 34.326), pintura 730, MO 5.700 (cañerías 2.780, skid 420, RX 2.500), transporte 600; costo 71.834. No se escribió `justificaciones.antecedentes`: sin el precio de las reguladoras la comparación no se puede cerrar.

### Errores encontrados en la revisión del 30-10-2026
1. **`armar_json.py` deshacía las correcciones de las auditorías**: las de compatibilidad (pos 1, 2, 5c, 6b, 6c, 7b, 7c, 14, 15, 21–24 y 23b) se habían hecho directo en `cotizacion.json`; correr el script volvía a cargar Tormene #300, B7M, MS Juntas #300 y los caños de grado A. Corregido: todo está en el script.
2. **Pos 17 citaba el código de Renard de la cupla BSPT (5281)** aunque la descripción decía NPT (la NPT es 5292, mismo precio) y **no tenía el tapón** que pide el plano.
3. **Sensores A y B de marca ABB, que no está en el listado SCE-IN-501-0015**; el A además no incluía la válvula de bloqueo y purga que pide su descripción.
4. **Faltaban las conexiones soldadas de las pos 15, 16, 18, 19 y A** (11 cuplas) y el tubing de doble virola de la ET 5.8: el cómputo copiaba la tabla, pero la tabla no alcanza para armar el equipo.
5. **Soldaduras estimadas por regla (36) en lugar de contadas del dibujo (37 + 15 SW)**.
6. **Plazo 120 días menor que el calculado** (no consideraba la aprobación previa del modelo de reguladoras ni el plazo de los transmisores).
7. **La oferta decía "a confirmar"** (reguladoras) y el informe tenía el desvío "Reguladoras de referencia en #300" cuando ese precio ya no se usaba.
8. **Prueba de fugas en 0 "sin referencia"** cuando hay tarifa de horas de planta; **RX con la tarifa DB NDT** cuando Matías ya había confirmado otra (30-10-2026).
9. **Faltaba la matriz de requisitos** y no se había usado el listado de marcas de Camuzzi, que estaba en la carpeta de la 003.

### Frenos que quedan (las ofertas no se generan)
requisitos (4 consultas), sin_precio (pos 1, 2, 2b, 7b, 14, 18, C), estimado 27% (horas, espárragos, pos 15/16), vencidas (24: listas Renard 12-2025 y Taval 09-2025, cotizaciones de 07-2026 y Provemet 07-2025: reconfirmar), pendientes de la oferta (número de PRES y teléfonos), antecedentes (sin costo comparable). No se escribió ninguna justificación para levantarlos.
