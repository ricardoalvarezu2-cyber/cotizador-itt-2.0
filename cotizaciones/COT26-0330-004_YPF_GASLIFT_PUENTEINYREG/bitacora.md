# Bitácora — COT26-0330-004 · YPF Gas Lift · Puente de inyección y regulación 2" #600 (SAP 1000653143)

## 26-11-2026 — Verificación contra el plano (borrador)
- **Pedido de Ricardo Álvarez:** verificar el equipo contra el plano adjunto con los precios de su carpeta de proveedores. Esa carpeta está en su OneDrive y no hay una PC conectada a la sesión, así que no se usó.
- **Documentos en `pedido/`:**
  - P-PL-003003 D2, C-PL-003004 D1 y R-PI-003012 D2 (H2), los tres con redmarks;
  - HD I-HD-003004 D1;
  - la planilla rev. 1 de ITT.
- **Es el mismo equipo de TAVAL/70** (caso de control `CTRL-P01`). En el repositorio ya está la rev. 2 del 26-10-2026, con un costo de 73.561,53 por skid, y la planilla que se pasó es la rev. 1 (72.236,73).
- **Resultado en `verificacion_plano.md`:**
  - sobran 2 a 4 esféricas de 2", 14 bridas de 2", entre 14 y 62 juntas (la rev. 1 repite el renglón) y 128 espárragos;
  - faltan las válvulas chicas, el espaciador del orificio, la bulonería de 1" y de 1½", 4 termovainas con sus conexiones y el tramo de 3" de los TE (HD nota 4);
  - en la rev. 2 faltan 2 TIT;
  - la rev. 1 tiene un solo FQIT y el P&ID pide uno por puente;
  - el inyector de químicos se cobra y a la vez se excluye;
  - la estructura del plano pesa 907 kg por skid, contra 1.200 kg cotizados.
- **Pendiente:**
  - los precios de la carpeta de Ricardo;
  - pasar el conteo a `lista_materiales_plano.csv` y armar con `armar_cotizacion.py`;
  - las consultas del final de `verificacion_plano.md`;
  - la revisión independiente.

## 26-11-2026 — Precios de la carpeta de Drive de Ricardo
- **Fuente:** carpeta "Precios proveedores" del Drive de Ricardo (folder `1gCEHg1TNIoa5UVKoa4x7AM8buw3Yjyck`).
  - Ya estaban cargadas en el catálogo Provemet 288974/77/78/79, 289894/97/909 y 236623; Oil Metal 37278; Miyashiro 50594 y 50627–30; Delgado 1542 y 1556; ABB OPP-26-9039842; Bripetrol; IMB S03485; Renard 27-5-25 y Cintolo 29-2.
  - Lo único nuevo es la cotización de END del 16-11-2026, sin IVA: Rx $670.000, LP $420.000, placa corta $10.000, placa larga $12.000. Se pasó a dólares con el oficial BNA de noviembre de 2026, 1.574,35.
- **`recotizacion_por_skid.xlsx`** (la arma `armar_recotizacion.py`, con fórmulas): solo los renglones que cambian contra la rev. 2, con las cantidades del plano y los precios nuevos. Diferencia de costo por skid: **−3.612,06 USD**, antes de factores.
  - Lo que más baja: espárragos (Delgado a 1,12 el juego contra 8 estimados), inyector de químicos sacado, juntas (Miyashiro a 1,29 contra 8), esféricas de 2" y bridas.
  - Lo que sube: termovainas, TIT, M2 y el tramo de 3" de la HD nota 4 (a confirmar).
- **SIN PRECIO** (pedir cotización): la junta de 1½" #600 y el espaciador de 2" #600.
- **Estimados:** espárragos de 4 1/4" (Delgado cotizó 3 3/4" y 4 1/2"), bridas de 1" #600 (Oil Metal 07-2025), reducciones de 3"×2".
- **ABB 266HSH** de la OPP-26-9039842 es un transmisor de presión, no el multivariable: el FQIT sigue con el precio de la rev. 2 (4.211,76).
