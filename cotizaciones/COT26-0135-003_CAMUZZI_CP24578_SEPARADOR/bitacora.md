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
