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
1. **Presión de diseño baja.** La ET 9.16.1 pide PH a **1,3 × la presión máxima de la serie ANSI** (#600 ≈ 102 bar → ~133 bar) durante 6 h. Con 77 bar de diseño esa prueba no cumple ASME (1,3 × MAWP): el recipiente se diseña a ~102 bar. Espesor estimado: 10,2 × 640 / (138 − 0,6 × 10,2) = 49,5 + **1,6 de corrosión (ET 9; se había usado 3,2)** ≈ 51 mm → 2" a 2 1/8" (era 1 5/8"). Sube chapa, fondo, placa y rolado ~25–30%. La PH cargada (1,5 × diseño, 16 h) también cambia.
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
