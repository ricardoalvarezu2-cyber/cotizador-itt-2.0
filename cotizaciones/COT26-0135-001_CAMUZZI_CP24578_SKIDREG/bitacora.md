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
- **CAMUZZI/23** (OC 4500150421, 03-2025): skid de regulación/medición SCE-RE-315-0047 vendido a **24.454**. Este sale **76.648**: la diferencia es casi toda las reguladoras (31.236 de costo, ×1,35 = 42.169 de venta). Hay que confirmar qué reguladoras llevaba el de 2025 y pedir cotización #150 para estas condiciones antes de presentar: con reguladoras de ~4.000 c/u (como la de Sacde/15) el precio bajaría a ~45.000.

## Pendientes
Ver `cotizacion.json` → pendientes. Lo crítico: precio de reguladoras y monitoras #150, si los sensores A/B/C los provee Camuzzi, y los largos de caño.
