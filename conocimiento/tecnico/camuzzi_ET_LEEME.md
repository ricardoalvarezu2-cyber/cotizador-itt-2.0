# Especificaciones técnicas de Camuzzi Gas (ET, planos tipo y procedimientos SCE)

Pedido de Matías (05-11-2026): sumar a la base todas las ET que Camuzzi tiene publicadas.

## Dónde las publica Camuzzi
- Info Contratistas: https://www.camuzzigas.com/info-contratista/ (321 fichas: 45 especificaciones técnicas, 168 planos tipo, 19 procedimientos y el resto de seguridad, ambiente y planillas). Listado completo en `camuzzi_publicaciones_sitio.csv`.
- Listado de ET: https://www.camuzzigas.com/tipo/especificaciones_tecnicas/ · planos tipo: https://www.camuzzigas.com/tipo/planos_tipo/
- **Las fichas del sitio actual no muestran el PDF** (quedó solo el título). Los PDF siguen en el servidor (`/wp-content/uploads/AAAA/MM/…`) y se encontraron con el buscador web; no hay forma de listarlos todos. Probar nombres de archivo a ciegas no se hace (miles de pedidos a un servidor de terceros).

## Qué hay en el repositorio
- `fuentes_originales/camuzzi_ET/`: 34 PDF bajados el 05-11-2026 con su texto (`.txt`, pdftotext -layout).
- `camuzzi_ET_indice.csv`: código, revisión, fecha, título, tipo, para qué le sirve a ITT, archivo y URL.
- `camuzzi_ET_requisitos.md`: requisitos de las ET de equipos que pesan en costo, plazo u oferta (filtro FM, separador, tanque de purga, calentador, reguladoras, juntas, válvulas, pintura, soldadura, prueba neumática, eléctrica).
- Documentos que vinieron en pedidos (más nuevos que la web cuando coinciden): `cotizaciones/COT26-0135-00*/pedido/` — listado de marcas **SCE-IN-501-0015 rev 1 (10-02-2026)** (la web tiene la rev 00 de 11-12-2020: vale la rev 1), ET del proyecto ERP Tres Arroyos (SCE-ME-515-0030, SCE-RE-515-0032), planos SCE-ME-315-0039 y SCE-RE-315-0048 y plano tipo SCE-RE-112-0001 rev 1 (separador vertical coalescente).

## Regla
Vale la revisión vigente al momento del pedido: si el pliego trae otra revisión, manda la del pliego y se anota en `conocimiento/fuentes.md`. Una ET de la web se usa para cotizar solo si el pliego la cita.

## Citadas en el repositorio y que no están (05-11-2026)
Genéricas (pedirlas a Camuzzi con la consulta del concurso cuando el pliego las cite): SCE-IN-101-0003, SCE-IN-101-0005, SCE-IN-107-0004, SCE-IN-301-0001, SCE-IN-501-0008, SCE-IN-501-0013, SCE-ME-106-0003, SCE-PR-106-1000, SCE-PR-506-1000, SCE-RE-102-0016, SCE-RE-103-0011, SCE-RE-104-0037, SCE-RE-104-0038, SCE-RE-105-0003, SCE-RE-110-0001, SCE-RE-110-0006, SCE-RE-112-0002, SCE-RE-112-0005, SCE-RE-113-0001, SCE-RE-308-0001, SCE-RE-508-0001, SCE-RE-512-0001.
Notas: SCE-RE-113-0001 fue un error de este chat (el plano es SCE-RE-112-0001). SCE-IN-301-0001 (ajuste de espárragos en uniones bridadas) solo aparece en una copia no oficial en Scribd: no se usa.

De proyecto (planos y ET propios de cada obra, no se publican; vienen con el pliego): SCE-ME-315-0014, SCE-ME-315-0015, SCE-ME-315-0016, SCE-ME-315-0017, SCE-ME-315-0018, SCE-ME-315-0019, SCE-ME-315-0027, SCE-ME-315-0028, SCE-ME-315-0029, SCE-ME-315-0031, SCE-ME-515-0014, SCE-ME-515-0015, SCE-ME-515-0016, SCE-ME-515-0017, SCE-ME-515-0018, SCE-ME-515-0019, SCE-ME-515-0026, SCE-ME-515-0027, SCE-ME-515-0028, SCE-RE-315-0014, SCE-RE-315-0015, SCE-RE-315-0016, SCE-RE-315-0017, SCE-RE-315-0018, SCE-RE-315-0019, SCE-RE-315-0032, SCE-RE-315-0033, SCE-RE-315-0034, SCE-RE-315-0035, SCE-RE-315-0038, SCE-RE-315-0039, SCE-RE-315-0047, SCE-RE-515-0014, SCE-RE-515-0015, SCE-RE-515-0016, SCE-RE-515-0017, SCE-RE-515-0018, SCE-RE-515-0019, SCE-RE-515-0025, SCE-RE-515-0026, SCE-RE-515-0027, SCE-RE-515-0028, SCE-RE-515-0031.
