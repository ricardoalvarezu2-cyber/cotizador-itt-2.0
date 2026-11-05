# Listas cargadas el 05-11-2026

Matías Russo pidió cargar "todas estas listas de precios, son precios actualizados" de la carpeta de Google Drive "Precios de
materiales" (de Ricardo Álvarez, https://drive.google.com/drive/folders/1gCEHg1TNIoa5UVKoa4x7AM8buw3Yjyck). De sus 9 archivos,
7 ya estaban en el repositorio (Renard 27-05-2025, Provemet 236623, 288974, 288977, 288978, 288979 y "Cintolo Lista 29-2.xlsx",
que es el mismo archivo que `2026-10-28/cintolo_lista_29-1_2025-02-17.xlsx`: mismo tamaño y adentro dice "Lista 29.1, vigencia
17/02/2025"). Se cargan los 2 nuevos:

| Archivo | Original en Drive | Fecha | Proveedor | Contenido |
|---|---|---|---|---|
| miyashiro_cotizacion_50594_2026-11-03.pdf | MIYASHIRO COTIZACION_N§_050594.pdf | 03-11-2026 | Miyashiro / MS Juntas (Eduardo Quinteros, equinteros@juntasms.com, +54 11 4290-1798) para Taval | 3 renglones: juntas espiraladas SW 316LFG 12" y 8" #300, kit aislante tipo F doble 6" #300. USD sin IVA (el IVA 21% va aparte); TC usado 1.545,50; validez 15 días (vence 18-11-2026); pago echeq 15 días / 60 días FF |
| oilmetal_cotizacion_37278_2026-10-30.pdf | oil metal 37278_TAVAL.pdf | 30-10-2026 | Oil Metal S.A. (Darío Fernando Villafañez, pablo.villafanez@oilmetal.com.ar, 011-3764-1628) para Taval | 34 ítems (28 códigos distintos): tees y reducciones BW Sch 80 WPB, bridas WN/ciegas/SW #300 A105, espárragos B7 zincados con tuercas, juntas espiraladas 316L+grafito, niples NPT, tapa hexagonal, weldolet y sockolets. USD, "no incluyen impuestos"; vigencia 09-11-2026; cta. cte. 30 días. Brida 4" WN #300 con entrega a 90 días; brida 8" WN "alternativa en stock, ver schedule" |

Las lee `herramientas/listas_vendedor.py` (lectores `miyashiro` y `oilmetal`, nuevos el 05-11-2026): cada renglón se controla
contra su importe (cantidad × precio), las abreviaturas del proveedor se pasan a texto que entiende el catálogo y el original
queda entre paréntesis (ESP SW → junta espiralada SW, 316LFG → AISI 316L + grafito, BWN → WN, BCI → ciega, BSW → SW,
GR B7 → ASTM A193 B7, CW/CWI → con anillo exterior / exterior e interior).

**Para revisar:** la tee 3" Sch 80 WPB (ABW-00396) pasa de 74,75 (planilla YPF Lic 66944 confirmada por Matías el 30-10-2026)
a 38,72 de Oil Metal, con la misma fecha; varias juntas espiraladas y niples bajan 60–80 % contra los precios anteriores
(p. ej. junta 2" #300 de 6,00 a 1,41; niple 1/2" Sch 160 de 20,00 a 2,79). Se cargó lo que dice el documento.

**Auditoría independiente (05-11-2026):** los 3 + 28 precios coinciden con los PDF (los códigos repetidos de Oil Metal tienen
el mismo precio). Corregido después: la junta CWI conserva "316/316L"; sockolets y weldolet leen la serie 3000; la nota de
disponibilidad de Oil Metal queda en `listas_vendedor.csv` (brida 8" WN: "alternativa en stock, ver schedule"; brida 4" WN:
entrega en 90 días; niple 1 1/2": 7 días). Quedan pendientes, porque vienen de cómo arma las claves el catálogo:
- Las juntas espiraladas no se distinguen por anillos ni espesor: en JUN-01699 (4" #300), JUN-02764 (12"), JUN-02769 (2") y
  JUN-02775 (3") el precio nuevo (anillo exterior solo o SW) reemplaza históricos con anillo interior a ~1/4 del valor.
- Las juntas "#300-600" se cargan solo en la serie 300.
- Los sockolets nuevos (con Sch 80) quedan con código aparte de los sockolet 3000 sin schedule (AFO-03330 y otros).
- El weldolet queda sin tipo; "SA-193 B7M" y "316LFG" no se leen como material en otros textos (corregirlo cambia claves de
  ~40 espárragos y juntas y deja códigos usados por cotizaciones sin referencia: hay que hacerlo con migración de códigos).
- 16 códigos citados en `cotizaciones/` no existen en el catálogo (anteriores a esta carga; dos en `cotizacion.json`:
  JUN-02839 en COT26-0330-001 y VAL-03290 en COT26-0330-002).

## Juntas YPF (Miyashiro / MS Juntas, 05-11-2026)

Matías pasó el mail «RE: COTIZACION JUNTAS - YPF» con 4 cotizaciones de Miyashiro (MS Juntas, Eduardo Quinteros, equinteros@juntasms.com) para Taval, del 05-11-2026, USD sin IVA (IVA 21 % aparte), TC usado 1.546,00, validez 15 días (vence 20-11-2026), pago echeq 15 días / 60 días FF:

| Archivo | Ref. | Contenido |
|---|---|---|
| miyashiro_cotizacion_50627_2026-11-05.pdf | P-PL-20002 | junta SWI 8" #600 10,96; junta SW 4" #600 3,38; kit aislante tipo D doble micarta 1 1/2" #1500 R-20 17,66 |
| miyashiro_cotizacion_50628_2026-11-05.pdf | P-PL-20015 | junta SW 10" #300 7,14; 4" #300 2,59; 2" #300/400/600 1,29; kit aislante tipo F doble micarta 4" #300 29,77 |
| miyashiro_cotizacion_50629_2026-11-05.pdf | P-PL-020004 | junta SW 8" #300 5,95; 4" #300 2,59; 3" #300/400/600 1,93; 2" 1,29; kit F 3" #300 30,44 |
| miyashiro_cotizacion_50630_2026-11-05.pdf | (sin ref.) | mismos ítems que la 50629 en mayor cantidad (kit 3": 14 un a 7 días, resto 15/20 días) |

Los lee `listas_vendedor.py` (lector `miyashiro`; se sumaron las abreviaturas «ESP SWI» = con anillo interior, «KIT AISL.D» y «MIC.» = micarta). Al catálogo: 7 ítems nuevos y 2 actualizados. Las juntas «3/4/600» (aptas #300/#400/#600) quedan sin serie en el catálogo, que admite una sola; la junta 8" #600 con anillo interior cae en el mismo código que una con anillo exterior (el catálogo no separa los anillos: pendiente ya anotado).

## Juntas separadas por anillos (05-11-2026, aprobado por Matías)

Desde esta carga el catálogo separa las juntas espiraladas por anillos (ext., int., ext. e int.) y por 316 / 316L, y carga las
aptas para varias series en cada una (así deja de valer lo de arriba: "#300-600" ya no queda solo en la 300). Convenciones:
MS «SW AC» = anillo exterior, «SWI AC» = interior y exterior; Oil Metal «CW» / «CWI» igual; acero zincado = anillo exterior.
Códigos que se fusionaron con otro quedan en `conocimiento/precios/catalogo_codigos_fusionados.csv`.
