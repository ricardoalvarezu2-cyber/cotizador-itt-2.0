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
