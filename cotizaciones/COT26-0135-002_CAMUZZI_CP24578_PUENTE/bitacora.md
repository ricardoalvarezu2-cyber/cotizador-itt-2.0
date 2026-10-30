# Bitácora COT26-0135-002 · Camuzzi CP 24578 ítem 3 · Skid puente de medición (ERP Parque Industrial Tres Arroyos)

**Estado: borrador, sin revisar.** Mismo concurso que COT26-0135-001 (ver su bitácora para el pedido).

## Qué se hizo
1. Tabla del plano SCE-ME-315-039 transcripta (`pedido/lista_materiales_plano.csv`). Caños sin cantidad en el plano: medidos del dibujo, 4" ≈ 8 m (bypass 3.961 + 1.213 + 911 mm y línea 452 + 1.100 + tramos), 6" ≈ 1 m.
2. La turbina la provee Camuzzi (especificación §4): pos 2 es un carretel provisorio de 300 mm (2 bridas WN 4" + 0,3 m de caño, 90 estimado).
3. Correcciones (`armar_json.py`):
   - Pos 1 filtro FM-6 #150 simple módulo: **9.000 estimado** (el FM-6 #300 de CAMUZZI/23 se vendió a 13.543 → ~10.000 de costo; el FM3 S150 de TAVAL/40 costó 5.575 y el FM8 S600 14.375). Pedir cotización de tapa y elemento.
   - Pos 3: esférica 6" PT Taval Lista 30 (740). precotizar había tomado una Esferomatic galvanizada de 3.500 (error de selección: ver lecciones).
   - Pos 11: termovaina estimada 120. Pos 13: skid 200 kg + fabricación por kg. Pos A: transmisor de temperatura ABB 1.448.
   - Ingeniería 20 h y calidad 40 h por criterio: el antecedente que eligió `estimar_horas` (puentes en serie de 442 unidades) da 7,5 y 3,5 h, que no alcanzan para un equipo único con aprobación de Camuzzi.
   - Media tira de 6" (6 m) y juntas/espárragos internos (6 de 4", 4 de 6").
4. Precio: **29.641** (borrador). Los antecedentes que compara la herramienta (puentes con V-Cone e instrumentos, 97.000–101.000) no son del mismo alcance: no llevan filtro FM y sí caudalímetros.

## Revisión independiente (28-10-2026, agente que no armó el cómputo)
Transcripción del plano y cantidades: bien. Precios Tormene y Taval verificados contra los originales. Corregido:
- Juntas internas de 6": 3 (no 4) y 24 espárragos. Prueba de fugas con N2: renglón propio (250 estimado).
- **Sigue abierto:** el filtro FM-6 (9.000 estimado) es el 44% del costo y sale de una venta de 2025 de un FM-6 #300: costearlo por componentes con el plano tipo SCE-RE-112-0004 o pedir cotización.
- Flete: si se adjudican los ítems 2 y 3 juntos, va un solo viaje (hoy cada uno suma su flete).

## 29-10-2026 · Lista igual al plano (pedido de Matías)
- `pedido/lista_materiales_plano.csv` corregida para que descripción y MATERIAL/OBS. digan lo mismo que el plano (antes había materiales reinterpretados, "RF" y "radio largo" agregados y textos cortados a 60 caracteres por `precotizar.py`, ya corregido). Lo que agrega ITT (planos tipo, kg estimados, largo medido de los caños) pasó a la columna `modelo_fabricante`.
- Tes en ASTM A-105 y cupla en ASTM A-106 como dice el plano: se sacaron los desvíos "se cotiza A-234 WPB / A-105"; el precio es de la pieza similar y Compras pide la del plano.
- Esféricas: marca del listado de Camuzzi (Taval no figura); precio Taval de la misma especificación como referencia y sin el factor de válvulas Taval (ahora llevan 1,35).

## 30-10-2026 · Compatibilidades revisadas
Pos 16 (cupla c/ válvula esférica, A-106): SIN PRECIO. Unitario USD 29.395,10.

## 30-10-2026 · Auditoría independiente de compatibilidades
- Pos 5c (espárragos 5/8" B7 + 2H): la referencia era B7M (no reemplaza a B7). Pasa a JUN-04173 (B7/2H zincado con 2 tuercas, 5/8" × 110 mm), USD 10 c/u, planilla TAVAL/43 (19-02-2026, línea 147); valor que parece global: **pedir cotización**.
- Pos 14 y 14b (caño 4" sch 40 A-53 Gr B): la lista de Renard dice "A53A" (grado A, cód. 1008). Pasa a cód. 1160 "Tubo s/costura 114,3 x 6,02 mm A53/A106/API 5L B", USD 34,34/m (misma lista, verificado en el original). Cantidades sin cambio.
- Unitario USD 30.040,50 (antes 29.395,10); total USD 30.644,62. Borrador, sin revisar.

## 30-10-2026 · Segunda auditoría independiente
- Pos 15/15b (caño 6" sch 40 A-53 Gr B): Renard "A53/135" sin grado → cód. 1173 sin costura A53/A106/API 5L B, USD 60,51/m (verificado en la lista).
- Pos 6b (junta 6" #150): la de MS Juntas es 8" #300 → SIN PRECIO, pedir cotización.
- Pos 5c: el precio de USD 10 pasa a estimado.
- Unitario USD 30.102,40; total USD 30.706,52. Borrador, sin revisar.

## 30-10-2026 · Tercera auditoría independiente
- Pos 6c: USD 10 de la planilla Techint/12 pasa a estimado. Total sin cambio: unitario USD 30.102,40.
