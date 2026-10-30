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
