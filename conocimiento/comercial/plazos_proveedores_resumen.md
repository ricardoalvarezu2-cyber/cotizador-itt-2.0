# Plazos de entrega de proveedores por tipo de material o servicio

Generado el 28/10/2026 a partir de `precios/proveedores_2025.csv`, `precios/proveedores_2026.csv` y `precios/precios_componentes.csv`, con cada dato contrastado contra el texto original en `fuentes_originales/ofertas_texto/` cuando el original está en el repositorio. La tabla completa, renglón por renglón y con cita literal, está en [`plazos_proveedores.csv`](plazos_proveedores.csv).

Todos los plazos están en **días corridos**. Los días hábiles se multiplicaron por 1,4 y las semanas por 7; cada conversión está anotada en la columna `nota`. "Stock" o "inmediato" se cargó como 0 a 7 días.

## Cómo leer los números

- **Datos**: renglones de la tabla para ese rubro. Una misma cotización que aparece en varias carpetas de cliente se contó **una sola vez** (la nota dice en qué otras carpetas está).
- **Mediana**: mediana de los puntos medios (mínimo + máximo / 2) de todos los renglones del rubro. Como mezcla stock con fabricación, se informa aparte la **mediana sin stock** (renglones con máximo mayor a 7 días) y cuántos renglones son de stock.
- **Rango**: menor mínimo y mayor máximo del rubro.
- Los datos de **planilla** (59 renglones, casi todos de Provemet, Cintolo, Jorvical y Centriacero, jul–sep 2025) vienen de `COTIZACION ELEMENTOS DE EQUIPOS.xlsx` y **no se pudieron verificar en la cotización original**: la planilla no indica carpeta y el número de cotización del proveedor no aparece en `ofertas_texto`. Son sobre todo "EN STOCK" de caños, accesorios y bridas.

## Resumen por rubro

| Rubro | Datos | Mediana (días) | Rango (días) | Stock | Mediana sin stock | Proveedores más rápidos (mediana sin stock) | Proveedores más lentos (mediana sin stock) |
|---|---|---|---|---|---|---|---|
| válvula esférica | 12 | 90 | 0–140 | 1 | 90 | Indave (38), Esferomatic (90), TAVAL (90) | Valvtronic (133), Valbol (90), TAVAL (90) |
| retención | 2 | 62 | 0–120 | 1 | 120 | TAVAL (120) (único) | — |
| aguja/bloqueo y purga | 3 | 15 | 15–30 | 0 | 15 | ABAC (15) (único) | — |
| PSV | 3 | 100 | 60–112 | 0 | 100 | DOMA (80) < Induquip (105) (orden de menor a mayor) | — |
| válvula de control | 8 | 94 | 60–196 | 0 | 94 | DOMA (75), TAVAL (84), Cv Control (90) | Induquip (133), Cv Control (90), TAVAL (84) |
| instrumento | 31 | 85 | 0–308 | 2 | 90 | RIVA (52), ABB (56), Meditecna (58) | Emerson Argentina (304), Cv Control (108), Induquip (98) |
| junta | 7 | 4 | 0–90 | 4 | 30 | Miyashiro (30) < Ms Juntas (60) (orden de menor a mayor) | — |
| bulonería | 4 | 8 | 7–10 | 2 | 10 | Ind Delgado (10) < Ms Juntas (10) (orden de menor a mayor) | — |
| caño | 15 | 4 | 0–40 | 14 | 38 | Mancul (38) (único) | — |
| brida | 26 | 29 | 0–210 | 6 | 75 | Tubos Renard (11), Pampa Conecta (20), Provemet (74) | Itt S.A. - Compras (165), Francovigh (75), Provemet (74) |
| accesorio BW | 17 | 4 | 0–40 | 13 | 24 | Cintolo (19) < Provemet (29) (orden de menor a mayor) | — |
| accesorio forjado | 14 | 8 | 0–60 | 7 | 35 | Provemet (30), Xiamen Landee Industries (35), ADITA (38) | Duralitte (52), ADITA (38), Xiamen Landee Industries (35) |
| chapa/perfil | 4 | 4 | 2–20 | 3 | 20 | AVILA (20) (único) | — |
| tapa de cierre rápido | 11 | 75 | 30–120 | 0 | 75 | Megatap (68) < Sypris (Fts) (70) < Futura (120) (orden de menor a mayor) | — |
| filtro/cartucho | 7 | 35 | 7–45 | 1 | 36 | GORA (35) < SP (38) (orden de menor a mayor) | — |
| fabricación terceros | 27 | 45 | 3–150 | 3 | 47 | Curvatubos Zeziola (18), Mcd Montajes Industriales (18), Juan Y Victor Sandri (20) | ARSOL (136), Ingeniería Figueroa (120), SEHC (98) |
| pintura | 0 | — | — | — | — | sin datos en las fuentes | sin datos en las fuentes |
| END/ensayos | 0 | — | — | — | — | sin datos en las fuentes | sin datos en las fuentes |
| transporte | 2 | 2 | 2–3 | 2 | — | — | — |
| otro | 20 | 52 | 0–154 | 4 | 62 | Dinatecnica (10), TULSA (10), Establecimientos Gascon (20) | Itt Bornemann-Goulds Pumps S.R.L (154), TAVAL (130), Tapigar (115) |

Rubros sin datos: **pintura** y **END/ensayos**. En las cotizaciones de terceros de 2025–2026 esos servicios van incluidos en la mano de obra de taller o excluidos ("sin arenado/pintura/END"), sin plazo propio. La única cotización de granallado y revestimiento (Amanci 147-26, carpeta TAVAL/77) tiene el plazo cortado en el texto ("se estima un plazo de ejecución de 7."), así que no se cargó. Para estos dos rubros hay que pedir plazo aparte.

## Salvedades

### Stock contra fabricación
- Los renglones "en stock" (0–7 días) son **de stock sujeto a venta**: casi todas las cotizaciones dicen "salvo venta" o "no reserva stock". Es una promesa de disponibilidad al día de la cotización, no un plazo garantizado.
- Hay renglones con rango del tipo "en stock a 75 días según ítem" (Francovigh, Cintolo, Provemet): se cargaron como 0–75 y el punto medio (37) **no representa nada**. Para plazos de acopio usar el máximo.
- Los rubros con casi todo stock (caño 14 de 15, accesorios BW 13 de 17, junta, bulonería) tienen una mediana de 3–8 días que no sirve para el camino crítico. Mirar la columna "mediana sin stock" y el rango.
- Los datos de **planilla** (Provemet, Cintolo, Jorvical, Centriacero, Miyashiro, jul–sep 2025) son los que más pesan en esos rubros y no se pudieron verificar en el original.

### Importado contra nacional
- **Válvulas de control**: nacionales (DOMA 60 días, Optimux de CV Control 90, Taval 84) contra importadas por Emerson/Fisher (98–196 días; las de 16" #900 "24–28 semanas a confirmar"). La mediana de las importadas es 140 días y la de las nacionales 90.
- **Válvulas esféricas**: nacionales y de stock de Taval (0–10 días las chicas y de 8"; 60–130 las grandes, esclusas y globos), Indave 15–60; importadas con actuador (Valvtronic 126–140 días, "18–20 semanas"; con flete aéreo 70–80 días).
- **Instrumentos**: los de Emerson/Rosemount (12 semanas = 84 días en casi todas las ofertas) son plazos "estimados, sujetos a disponibilidad de insumos y nacionalización de productos". ABB 50–122 días (Coriolis 122). Yokogawa vía CV Control 90–140. El cromatógrafo 770XA de Emerson llegó a **43–44 semanas (301–308 días)**.
- **Tapas de cierre rápido**: las nacionales (Megatap 30–110 días según diámetro; Futura 90–120) contra las de Sypris Tube Turns, que cotizan **70 días EXW Louisville**: no incluyen flete, ni importación, ni aduana, así que el plazo total es mayor.
- **Bridas**: Shanghai Bozhong ofrece 5–7 días EXW China y Xiamen Landee 35 días desde el anticipo (FOB Tianjin), también sin flete ni importación. Las bridas API 6A (6BX 2 9/16" 10.000 psi) de Francovigh tardan 75 días; las de 20" son críticas ("no consiguen menos de 20 días").
- **Retención 10" #600 de Taval**: 120 días, compra a China, salvo venta.

### Por rubro (casos que cambian el plazo)
- **Tapas de cierre rápido (Megatap)**: 4" S600 30/45 días; 6" S150 60; 16" #900 60/90; 20" vertical S300 75/105; 28" #600 90/110; 32" S600 60/90 (120 si se pide ahora por parada de forja de Francovigh). Se paga con anticipo y certificación de datos de diseño.
- **Filtros y cartuchos**: Gora 30–45 días desde OC y anticipo; Filtron 5 días hábiles (7 corridos) para cartuchos de polipropileno de fabricación estándar; SP 30–45.
- **Fabricación de terceros**: depende de si el plazo corre desde la OC o desde que llegan los materiales. Los talleres (Quesada, Sandri, Cormet, MCD) cotizan 3–45 días **desde que ITT les entrega material**; los que arman skids completos (Figueroa 90–150, SEHC 60–120, ARSOL 136, Galvanotecnia 49–112) son los más lentos. Los mazos de tubos (Termofluidos, Galvanotecnia) 84–112 días desde OC, anticipo y planos aprobados.
- **Mano de obra de Ledesma y de otros talleres**: muchas cotizaciones no traen plazo ("a convenir", "pago a 5 días f.f." que es pago, no entrega); no se cargaron.
- **Transporte**: 2–3 días de tránsito (Quilmes a Neuquén por semirremolque), más la estadía de 850.000 ARS por 24 h.

### Calidad de los datos
- Hay **cotizaciones viejas dentro de los CSV 2025**: dos de agosto de 2023 (bridas de la licitación YPF 08-0740: Francovigh hasta 210 días, compras de ITT 150/180) y cuatro de 2024 (Mancul y Zeziola de agosto; piletas de Milei y Tankor de diciembre). Se cargaron con su fecha real; para plazos recientes conviene ignorarlas.
- **Diferencias con el CSV**: se corrigieron al contrastar con el original. Bombas centrífugas Goulds: el CSV decía "160–180", el original dice 22 semanas (154 días) para las centrífugas y 180 días para las PCP. ARSOL: el CSV decía "7+90 días"; el original dice 7 días hábiles de ingeniería y 90 **hábiles** de fabricación (136 corridos). Taval 23442: el CSV tenía 45 días y es lo que dice el presupuesto de Taval (ITT ofreció 45/60 al cliente). ABAC: la fuente del plazo de 30 días es un mail, no la oferta de ITT.
- Varias "cotizaciones" del CSV son **notas de las planillas de costo de ITT**, no el documento del proveedor: Taval 6" (60/70 días, planilla Alpha Manifolds), Meditecna V-Cone (60 días) y Francovigh 75/90 (planilla de puentes de producción). Están marcadas en `nota`.
- Una misma cotización repetida en varias carpetas se contó una vez: Induquip/Rosemount 12 semanas (PAMPA/4, /5, /7), Valvtronic y Valbol (PAMPA/5 y /7), Riva, Protfund, Gora, EQA, Juntas MS y Francovigh bridas API.
- El rubro **instrumento** reúne transmisores, caudalímetros, manómetros, cromatógrafo y muestreador; el plazo depende de la marca más que del tipo. Las válvulas esclusa/globo y las de retención y esclusa de Ingeniería en Fluidos quedaron en `otro` porque la lista de rubros no tiene válvula esclusa.

## Cómo usarlo al cotizar el plazo

1. Del cómputo, buscar los renglones de **plazo largo** y tomar el máximo de la tabla, no la mediana: instrumentación Emerson/Rosemount (12–16 semanas) y cromatógrafos, válvulas de control Fisher (14–28 semanas), PSV importadas (14–16 semanas), tapas de cierre rápido grandes (90–120 días), bridas API 6A (75 días), válvulas con actuador (18–20 semanas).
2. Para materiales de stock (caños, accesorios BW, bridas estándar, juntas) usar 7 días y confirmar el stock el día de la cotización.
3. En fabricación de terceros aclarar si el plazo corre desde la OC o desde la recepción del material y sumarlo al acopio.
4. Antes de usar un dato, mirar la columna `condicion` (desde OC, desde anticipo, desde aprobación de planos, stock): el plazo puede arrancar semanas después de la OC.
