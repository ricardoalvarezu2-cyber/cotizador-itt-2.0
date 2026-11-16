# Bitácora — COT26-0330-003 · YPF Lic 70243 · Puente de medición (skid SCC-112A)

## 16-11-2026 — Preliminar (borrador, sin revisar)

**Pedido:** Ricardo Álvarez pasó 5 archivos (carpeta de Drive "4. LIC 70243 Puente MED", copia de su OneDrive
`01- COMERCIAL\0330- YPF\090- Lic 70243 PUENTE MED\4. O. Comercial`) y pidió cotizar el puente de medición con la
"Planilla modelo de cotizacion.xlsx", con los precios más actualizados y priorizando las cotizaciones de la carpeta de Drive.

**Documentos (en `pedido/`):** plano conjunto YPF-GASLIFTBAT21-VCD24299-P-PL-003001 D1 (hoja 1 skid de medición SCC-112A,
hoja 2 skid de regulación SCC-112B), P&ID YPF-GASLIFTPTEMED-VCD24299-R-PI-003010 D0, hojas de datos de instrumentos
YPF-GASLIFTBAT21-VCD24299-I-HD-003001 D1 (texto en `pedido/hd_texto.txt`), ET de paquetizados YPF-EQSKIDSXX-VCD16011-G-ET-001005 D2
y la planilla modelo.

**Alcance tomado:** solo el SCC-112A ("puente de medición"). El SCC-112B queda como consulta.

**Cómputo:** el plano no trae tabla de materiales: lo armó ITT desde la planta y las vistas (colector 7.360 mm, bypass 5.450 mm,
6 esféricas 4" #600 + retención 4" #600, Coriolis 3" #600 entre JD, 5 tomas 3/4", termovaina 1 1/2" #600, bastidor 6.960 × 1.535)
y desde la ET (batea con purga 2", JB y cableado, placa, puesta a tierra). `origen_lista` = diseño ITT. Clase CA31 de la L0200
(600# RF, AºCº, CA 1,6 mm, RX 30 %); schedules Sch 80 / Sch 160 tomados por ITT (falta la hoja de la clase).

**Precios:** catálogo (incluye las cotizaciones de la carpeta de Drive ya cargadas: Provemet 288974/288978, Oil Metal 37278,
Miyashiro 50627/50629, Delgado 1542) y Taval confirmadas por Matías el 30-10-2026. Antecedente gemelo: TAVAL/69 Lic 64673
(SCC-113A/B, mismo tag FIT-1800A): Coriolis ABB FCB450 DN100 (35.558,31), PIT ABB, computador de caudal ABB XFC6200EX
(7.345,97), TIT/TE Induquip + termovaina Weisz, MO Ledesma 200295 (17.200 por 2 skids, prorrateado por largo: 6.627).
Correcciones a la precotización automática: brida 3" #600 y tee 4" con el último precio de proveedor (Provemet / Oil Metal) en
lugar de la mediana; juntas en 316L (Miyashiro); estimados sin referencia en 0 (P4 ter); ingeniería 80 h (la ET pide ingeniería
de detalle completa).

**Resultado del repositorio:** costo 79.308,27 · precio 103.852,73 USD por skid (factores 1,35 / 1,35, contingencia 5 %, Taval 1,0).
**Planilla modelo** (`COT26-0330-003_YPF_Lic70243_PuenteMed_planilla_modelo.xlsx`, la arma `llenar_planilla_modelo.py` desde
`computo.csv`): con los factores y las convenciones del modelo (1,5 materiales/instrumentos/MO, 1,1 Taval y transporte, piping y
pintura × 1,2) da costo 75.362,37 · venta 108.773,31. Se le sacaron los vínculos a otro libro ('[4]Man. Conc…') y el transporte
fijo en 2.500 de la hoja RESUMEN.

**Plazo:** 150 días ofrecidos superponiendo taller y compra del Coriolis; sin superponer da 210 (decisión pendiente).

**Pendiente:** revisión independiente del cómputo contra el plano; cotizar Coriolis 3" #600 y demás instrumentos (las de 07-2026
vencieron), MO Ledesma para el SCC-112A, junta 1 1/2" #600, JB/cableado, tracing y placa; consultas al cliente en `cotizacion.json`
(`pendientes`) y `pedido/requisitos.csv`.

## 16-11-2026 — Mark up 1,5
Ricardo Álvarez pidió mark up 1,5. Se aplicó a todo: `FM`, `FMO` y `FTV` = 1,5 en `cotizacion.json`, y en la planilla modelo los
7 renglones del cuadro de rentabilidad (antes 1,5 / 1,1 Taval / 1,1 transporte / 1 caución) toman el mismo valor de `parametros.FM`.
Repositorio: costo 79.308,27 · precio 118.962,40. Planilla modelo: costo 75.362,37 · venta 113.043,55. La diferencia es de método:
el repositorio suma contingencia 5 % y ajuste por inflación; el modelo suma 20 % a piping y pintura.

## 16-11-2026 — Valores de Ricardo, instrumentos por tag y planilla del cliente
- **Planilla Ariba del cliente** (`pedido/Lic - 70243 - PUENTE MED.SAL.BAT.CORR.MED 500KM3D CAU - UTE LACH.xls`): ítem 1, material
  000000001000653168 "PUENTE MED.SAL.BAT.CORR.MED 500KM3D CAU*", 1 unidad, entrega RUTA 17 aprox. 2 km de Añelo (planta 1036 UP-UTE
  La Amarga Chica) el 01-07-2027. Cita la hoja de datos YPF-GASLIFTBAT30-VCD24299-I-HD-003002-D1 (Batería 3.0), que no llegó: se usa la
  HD-003001 (Batería 2.1). Dice "SERVICIO: CORROSIVO MEDIO" y el P&ID marca la línea CA31 (corrosión baja en la L0200): consulta.
- **Ledesma USD 24 por pulgada equivalente** (136,72 pulg-eq, alcance SOL-00143: piping, skid y soportería) y **pintura USD 50/m²**,
  indicados por Ricardo Álvarez: cargados en `conocimiento/precios/precios_usuario.csv` como confirmados por él.
- **Instrumentos según el P&ID PI-003010 D0** (skid 112A): FE/FIT-1800A (Coriolis integral), PIT-1800A, manifold M2 (pos 34),
  TE-1800A sensor y termovaina 1½"-600# (pos 35) por separado, TIT-1800A, FQIT-1800A (nota 2), 2 JD (pos 19). FI/PI/TI/FQI-1800A son
  indicaciones en SCADA/SCP: fuera del suministro (aclarado en la oferta).
- Resultado: repositorio costo 76.048,57 · precio 114.072,85; planilla modelo costo 72.496,29 · venta 108.744,44.
