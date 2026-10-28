# Marcas aprobadas y vendor lists por cliente (resumen)

Fuente de detalle: `conocimiento/comercial/marcas_aprobadas.csv` (217 renglones, un renglón por cliente + rubro + documento). Todos los textos salen de `fuentes_originales/ofertas_texto/` (ruta en las columnas `carpeta_origen` y `archivo_origen`). Estado: **borrador, sin revisar**. Generado el 2026-10-28.

Cómo leerlo:
- "Dato firme" = texto escrito en un documento del cliente (pliego, hoja de datos, OC, lista anexa).
- "Dato dudoso" = texto de una oferta o mail de ITT, de un proveedor, o atribución al cliente inferida. Está marcado en la columna `nota` del CSV.
- La lista de marcas en sí **no está extraída** para PAE (A7XN-RC-85-SP-0027_R1), Pampa Energía ("Vendor List Pampa"), Pluspetrol (AARC-100-ET-X-001) ni para las marcas "homologadas por la Distribuidora". Solo se sabe que existen. Para verlas hay que abrir el RAR de la Tanda 1 (ver CLAUDE.md).

## Resumen rápido: qué cliente exige qué

| Cliente | Lo que dice el documento | Fuerza | Marcas con texto en el repo |
|---|---|---|---|
| YPF | Listas "de proveedores sugeridos" (Anexo 3): NOC, Instrumentación, Electricidad | Preferida (no dice si es cerrada; el aprendizaje de la ficha TAVAL_39 la trata como obligatoria) | Sí, completas (176 renglones) |
| Pampa Energía | "Vendor list" por hoja de datos y OC; "Marcas recomendadas" en transmisores | Exclusiva en válvulas, instrumentos, cañerías, eléctricos y controlador (RM-1056); preferida en transmisores | Parcial: manómetros, transmisores, actuadores y cables |
| PAE | "Listado de Marcas Aprobadas" A7XN-RC-85-SP-0027_R1 (anexo de la ET) y marcas por renglón de la ET | Exclusiva (por nombre del documento) | Solo marcas por renglón copiadas en cómputos de ITT (dudoso: origen inferido) |
| Pluspetrol | Vendor List AARC-100-ET-X-001; campo "MARCAS/FABRICANTES" en pedidos | Indicada en el renglón | Solo repuestos y conjuntos por pedido |
| Tecpetrol (vía Techint y A&A Fluid Control) | La lista de subproveedores que propone ITT queda sujeta a aprobación del Comprador y/o Cliente | Procedimiento de aprobación, sin lista | Ninguna |
| AESA | Marcas de las HD "solo de referencia", vendor list "abierto" (mail de ITT) | "O similar" | Ninguna |
| Albanesi, Camuzzi | Texto de plantilla de ITT ("homologados por la Distribuidora") y ofertas de ITT | Dudoso | Ninguna firme |
| Vista, CGC, TGS, Metrogas, Enarsa, Pecom y otros | No se encontró nada | n/d | Ninguna |

## YPF (listas de la carpeta TAVAL; mismas listas en YPF/11)

Origen: carpetas TAVAL 39, 75, 82, 089 y 092 (Anexo 3 de licitaciones; la más nueva, 092, es del 2026-10-27) y carpeta `YPF/11.Doc3723489492 - 08-0667 Filtros Coalesc UP NOC(TAVAL)` (2022-06-14 a 2022-12-07). Los archivos son idénticos entre carpetas TAVAL (mismo md5): NOC, Electricidad e Instrumentación v1.0. Electricidad también es idéntica a la de YPF/11 (2022). Instrumentación **cambió**: la de 2022 es regional (hojas Oeste y Sur, con modelos); la v1.0 de las carpetas TAVAL es consolidada, sin modelos, con los comentarios "Medición agua inyección", etc.

La atribución a YPF es inferida (las carpetas TAVAL no nombran al cliente en el texto; la carpeta YPF/11 sí tiene las mismas listas con título "Listas de proveedores sugeridos"). La carátula dice "Listado de subproveedores sugeridos". El Anexo 3A obliga a declarar subproveedores y forma parte de la adjudicación (ficha TAVAL_75).

Fecha de la lista NOC y de Electricidad: 230929 en el nombre del archivo. Lo leí como 2023-09-29. La ficha TAVAL_39 la cita como 23/09/2025: queda ambiguo. Instrumentación v1.0 no tiene fecha propia.

Lista más reciente por rubro (v1.0 de Instrumentación y NOC_230929):

| Rubro | Marcas / proveedores tal como figuran | Documento |
|---|---|---|
| Válvula esférica (bola) | Esferomatic, Indave, Tyco Flow Control Argentina, Valmec, Valvtronic, Worcester, Wenlen, Cameron (Instrumentación v1.0). En NOC además: Emerson, Esco, Honeywell, HTM, Metso, Petrogreen, RPM Control, Servin Ingeniería, Siclonet (Weir), Spirax Sarco, Taval, Valvulas Worcester de Argentina, Cameron | Instrumentación v1.0; NOC rubro 2310 |
| Válvulas de bloqueo | Tyco Flow Control Argentina, Esferomatic, Wenlen, Valtronic, Valvol, Indave, Rotork, Limitorque-Flowserve, Giron, Valmec | Instrumentación v1.0 |
| Compuerta / globo / retención / tapón / diafragma | MMA, Wenlen, Esferomatic, Favra, Thorsa, Tyco, Valam, Valvtronic, Worcester (v1.0); NOC rubro 2309 suma Taval, LVM, Giron, Valcox, ABAC y más | v1.0; NOC 2309 |
| PSV (seguridad y alivio) | Favra, Farinola, Aerre, Farris, Anderson Greenwood Crosby, Doma, NOV MSW | Instrumentación v1.0 |
| Actuadores | Tyco Flow Control Argentina, Esferomatic, Wenlen, Valvtronic, Valvol, Airtorque, Rotork, Emerson Biffi | Instrumentación v1.0 |
| Manómetro | Ashcroft (Axar), Weisz, Nuova Fima, Wika, Ing. Capino | Instrumentación v1.0 |
| Transmisor de presión / diferencial | ABB, Rosemount (Emerson), Conar, Honeywell, Vega, Smart (Comsert), Kimray (Comsert), Siemens, Yokogawa | Instrumentación v1.0 |
| Caudalímetro | Por principio (electromagnético: Endress+Hauser, Krohne, Rosemount, Sistemas Industriales, Xycon, Siemens, ABB, Conar; Coriolis: Krohne, Micromotion, Honeywell, Endress+Hauser, ABB, Smart; etc.) | Instrumentación v1.0 (28 renglones) |
| Caños | Siderca, Provemet, Klockmetal, Sidemet, Traficaño | NOC |
| Accesorios A105 | Algomec, Duralitte, Fastpack, Forja Atlas, Sidemet Caños, Sumpetrol, Industria Metalúrgica CH Argentina, Simat, Tubos Renard, Farca | NOC rubro 2301 |
| Accesorios A234 | Cintolo Hnos, Sidemet Caños, Sumpetrol, Newtesol, Servin Ingeniería | NOC rubro 2301 |
| Bridas | Francovigh, Futura Hnos, Oil and Gas Suppliers, Cuñado, Galperti, Phoceenne, Sumpetrol, Simat, Tubos Renard, Bripetrol | NOC rubro 2302 |
| Juntas | Ackron, Dinatecnica, Farca, Industrias Montefiore, Juntas Flex Seal, Miyashiro-Schönborn, Rich Klinger, Teadit Argentina | NOC rubro 2305 |
| Bulonería | Almacenes Petroleros, Batsa, Bulonera del Oeste, Dinatecnica, GR Industrial, Industrias Delgado, Iteco, M. Martino, Petrobul, Provisión y Asesoramiento Técnico, Talleres Versailles, Miguel A. J. Fernández | NOC rubro 1706 |
| Cables de baja tensión | Marlew, Felrro, Anixter, Ateco, Nexans Indelqui, Eecol, Cimet, Prysmian, Racklatina, Draka, General Cable, IMSA (Industria Metalúrgica Sudamericana), Soule, Sermatel (NOC); por regional en Electricidad | NOC rubro 1004; Electricidad |
| Pintura | No hay rubro de pintura en ninguna de las tres listas | n/d |

Cambios entre versiones (Instrumentación 2022 contra v1.0): la v1.0 agrega marcas de PSV (Favra, Aerre, Farris, Anderson Greenwood Crosby; en 2022 solo Farinola, Doma y NOV MSW) y trae filas de válvulas manuales (bola, bloqueo, compuerta/globo/retención), que la versión 2022 no tiene; la de 2022 trae "Sistemas de control" (Allen-Bradley, Honeywell Slate, Emerson DeltaV) que la v1.0 no incluye salvo "Allen Bradley / Rockwell" en PLC. Los renglones 2022 están agregados por rubro en el CSV (columna `nota` con subtipos y cantidad de renglones por regional).

## Pampa Energía (carpeta PAMPA ENERGIA 5, RDA; y Sacde como contratista)

| Rubro | Marcas | Condición | Documento y fecha |
|---|---|---|---|
| Manómetro | Wika, Ashcroft, Winters, Weisz, Nuova-Fima | Exclusiva por "Marcas según vendor list" (dudoso si admite otras) | HD 1046-RDA-I-HD-6312-0, carpeta al 2026-10-09 |
| Transmisor de presión | Rosemount, ABB, Yokogawa | Preferida ("Marcas recomendadas") | HD 1046-RDA-I-HD-6310-A, carpeta al 2026-10-09 |
| Actuador eléctrico | Valvtronic o Worcester | Alternativas nombradas en la OC | OC 4500766711, 2026-07-23 |
| Válvulas esféricas, manómetros, transmisor | "Según vendor list" (sin marcas en el texto) | Exclusiva | OC 4500766711, 2026-07-23 |
| Pintura | "Estándares suministrados por Pampa Energía" (sin marcas) | Estándar del cliente | OC 4500766711 |
| Válvulas, instrumentos, cañerías, elementos eléctricos y controlador | "Marcas listadas en el Vendor list de Pampa Energía" | Exclusiva | RM 1046-RDA-M-RM-1056_A, Sacde/6, carpeta al 2026-10-14 |
| Cables con armadura | Prysmian Group, Marlew, IMSA, Felrro ("si o si") | Exclusiva | Mail 2026-01-28, Sacde/14 (dato de segunda mano) |

Pampa distingue entre "vendor list" (cerrada para válvulas e instrumentos) y "marcas recomendadas" (transmisores). La ficha de Sacde/6 registró que válvulas esféricas de marca propia no estaban en el vendor list (USD 4.150 de diferencia).

## PAE (Pan American Energy)

- Documento aprobador: **Listado de Marcas Aprobadas A7XN-RC-85-SP-0027_R1**, citado en el Anexo II "Especificaciones Técnicas" de las carpetas 21 (calentadores CASE CPF) y 29 (skids a pozo, 2022-09-08). Contenido no extraído.
- Marcas por renglón (dudoso: salen de cómputos de ITT que replican la ET GSJ-GA-GEN-ME-113 y anexos; la redacción con TAG y serie sugiere origen en la ET de PAE, pero no está verificado):

| Rubro | Marca | Carpeta más reciente |
|---|---|---|
| Válvula esférica S-2000 acero | Esferomatic | 21 (2024-10-16) |
| Válvula aguja S-1500 y globo S-800 | LVM/Giron | 21 (2024-10-16) |
| PSV (gas combustible) | Farinola | 21 (2024-10-16) |
| Manómetros | Nuova Firma (escrito así; en la carpeta 16: Nuova Fima) | 21 (2024-10-16) |
| Bloqueo y purga (manifold) | ABAC | 21 (2024-10-16) |
| Visor de nivel S-2000 | Penberthy, Jefferson, Rivas (en la carpeta 20: Riva) | 21 (2024-10-16) |
| Sensor de temperatura | Kimray | 21 (2024-10-16) |
| Filtros FM | Gora | 21 (2024-10-16) |
| Reguladoras de presión | Dallas, Kimray, Invalco | 32 (2023-01-18) |
| Quemador | Flargent | 32 |
| Acumulador de aire: alivio, autorreguladora y transmisor | Favra; Doma 95H; Honeywell STG74L | 16 (2022-03-11) |

- Por renglón de OC (campo "MARCAS/FABRICANTES" de SAP, dato firme): monobornes **Payra** (7 OC, 2023 y 2025-09-25). Válvula de retención clapeta 2" serie 3000 en la licitación 3000043859: marca/fabricante **Wenlen EMG 2086-CI, 999.99-99-78**; Wenlen contestó que no es parte de su línea (dudoso).

## Pluspetrol

- Vendor List **AARC-100-ET-X-001** figura en la OT173-22 (manifolds a colectores). No hay marcas en el texto.
- Pedidos con fabricante impuesto (campo "MARCAS/FABRICANTES"): conjunto válvula aguja y manómetro 15000 psi **MMA 55582-1** (2025-02-14; ITT ofreció ABAC VHP 9H más manómetro CENI, sin evidencia de aceptación); repuesto tubo de fuego **Kvaerner D-3353-09-0104**; válvula de bloqueo **ABAC VA150M IG-HS** (solo consta en la oferta de ITT).

## Tecpetrol, AESA, Albanesi, Camuzzi

- Tecpetrol (vía Techint, Los Toldos II Este, y vía A&A Fluid Control): solo exige que la lista de subproveedores quede sujeta a aprobación del Comprador y/o Cliente; no hay lista de marcas en el texto.
- AESA: mail de ITT a proveedores (2022-10-21) con "marcas y modelos indicadas en las HD son meramente de referencia, el vendor list es abierto". Es texto de ITT.
- "Homologados por la Distribuidora": frase de plantilla en 13 OT de AESA, 5 de Albanesi, 1 de PAE y 2 de Tecpetrol; no verificada en un pliego.
- Camuzzi: sin vendor list. Solo la oferta de ITT con ABAC VHP 9H S IT y manómetro CENI 74.

## Diferencias entre clientes

1. **Dónde está la lista.** YPF entrega listas completas y por rubro (la única con texto utilizable para validar marcas). Pampa y PAE la nombran como documento aparte que hay que ir a buscar. Pluspetrol la nombra solo por código.
2. **Fuerza.** Pampa dice "deberán ser de las marcas listadas" (exclusiva) pero recomienda marcas en transmisores. YPF dice "sugeridos". PAE llama al documento "aprobadas".
3. **Rubros que cubren.** YPF cubre desde válvulas e instrumentos hasta caños, bridas, juntas, bulonería, cables y chapas. Pampa nombra válvulas, instrumentos, cañerías, eléctricos y controlador, pero sin marcas de caños. PAE solo se vio en instrumentos, válvulas pequeñas y accesorios de calentador.
4. **Marcas coincidentes** (útiles para ofertar a varios clientes): manómetros Wika, Ashcroft y Weisz, y Nuova-Fima en YPF y Pampa (Winters solo en Pampa); transmisores Rosemount, ABB y Yokogawa en YPF y Pampa; Valvtronic y Worcester en válvulas esféricas y actuadores en YPF y Pampa. Las marcas por renglón de PAE (Esferomatic, LVM/Giron, Farinola, Nuova Firma, ABAC) también están en la lista de YPF.
5. **Taval.** Figura como proveedor aprobado en las listas de YPF (válvula de bola, compuerta/globo/retención, PSV). En Pampa y PAE no hay texto que lo diga (la política de ofrecer Taval salvo vendor list es de ITT, ficha APSA_9).

## Qué no se encontró

- Texto de los listados de PAE (A7XN-RC-85-SP-0027_R1), Pampa ("Vendor List Pampa") y Pluspetrol (AARC-100-ET-X-001).
- Ninguna frase de vendor list, marcas aprobadas o fabricantes aceptados en los textos de Vista, CGC, TGS, Metrogas, Camuzzi (lista propia), Enarsa, Pecom, Shell, Aluar, Bahisa, Chimen Aike, Phoenix, Los Guindos, Contreras, Alcalá, BTU, Gaumer ni Milicic. Vista, CGC y TGS aparecen solo en nombres de carpetas o como clientes finales. La búsqueda fue por frases clave y por nombres de marcas, no leyendo todos los documentos.
- Marcas de pintura exigidas por algún cliente (solo "estándares de Pampa").
- Marcas de juntas, bulonería y caños de Pampa, PAE y Pluspetrol; solo existen para YPF.
- Documentos en escaneos: los PDF que no tienen texto extraíble pueden contener listas que acá no figuran.
