---
name: relevar-pedido
description: Leer TODA la información de un pedido de cotización (zips, mails .msg, requisición, hoja de datos, P&ID, planos, especificaciones, condiciones) y armar el informe previo a la cotización con resumen del pedido, listas de materiales del skid y del recipiente con pesos, válvulas, instrumentos y señales, piping (caños, accesorios, bridas), juntas y bulonería, elementos filtrantes e internos, otros artículos, trabajo eléctrico, pesos y pulgadas de soldadura (nominales y equivalentes, por tipo), faltantes y decisiones de ITT. Usar cuando Matías pase un pedido nuevo y pida "leer", "recopilar", "relevar" o "hacer el informe" antes de cotizar, o cuando el cliente no da lista de materiales y hay que sacarla del P&ID.
---

# Relevar un pedido e informar antes de cotizar

Es el paso previo al skill `cotizar`: deja todo leído, guardado en el repositorio y resumido, con las listas que después se pasan a `pedido/lista_materiales_plano.csv`. Caso modelo: `cotizaciones/COT26-0010-002_AESA_C5297_FILTROS_COALESCEDORES/` (bitácora, `resumen_pedido.md`, `listas_preliminares.py`). Respuestas al usuario cortas, en español rioplatense; números 1.234,56 y fechas DD-MM-AAAA (CLAUDE.md).

Al empezar, leé `conocimiento/estado_y_pendientes.md` y `conocimiento/errores_y_lecciones.md`.

## 1. Guardar y abrir todo (sin IA)

1. Carpeta de la cotización como en el skill `cotizar` paso 1 (`COT[AA]-[código cliente]-[NNN]_<CLIENTE>_<PEDIDO>`; código en `conocimiento/comercial/clientes.csv`; si ya hay otra cotización del mismo proyecto, mirá su bitácora y su `pedido/`). Anotala en `cotizaciones/README.md` con estado "recopilación de información".
2. `python herramientas/abrir_pedido.py cotizaciones/<carpeta>/pedido <archivos subidos…>`: copia los originales, descomprime los zip (también los anidados y los adjuntos de los mails), arregla los nombres `#U00f3`, abre los `.msg` sin librerías externas, deja el texto de cada documento al lado (.txt / .csv) y escribe `pedido/inventario.md`.
3. Documentación general del cliente que sirve para otros pedidos (condiciones de compra, seguridad, instructivos): a `fuentes_originales/<cliente>_<tema>_<AAAA-MM>/`, no a la cotización.
4. Todo va al repositorio en la misma sesión (el entorno es temporal).

## 2. Leer todo (IA)

Leé **cada** documento del inventario; no alcanza con el índice. Orden sugerido:
- **Requisición (RI):** objeto e ítems, alcance (incluye / no incluye), orden de prelación, lista de documentos mandatorios, excepciones, inspecciones, garantía, repuestos (§ repuestos: cantidades mínimas), requisitos de cañerías y procesos, envío, transporte e izaje, documentos con la oferta (columna A).
- **Planilla de cotización del cliente:** posiciones, códigos, cantidades y unidades (precio unitario por posición).
- **Hoja de datos (HD):** datos de diseño y proceso, materiales, conexiones, notas (todas), pesos. Si una tabla viene vacía (lista de válvulas o instrumentos), sale del P&ID.
- **P&ID:** `python herramientas/recortar_plano.py <pdf> <página> <scratchpad>/pid` (grilla 3x3 a 200 dpi) y mirá cada recorte con Read. Relevá todo lo que está dentro del límite de skid: tags de válvulas (Ø, serie, LO/LC, FB), actuadas (LV, SDV, BDV con SV, ZSO/ZSC, posicionadores), PSV (set, orificio), RO, instrumentos y su sistema (SIS / SCP / SCADA / local), juntas dieléctricas (JD), líneas con su Ø, servicio y clase, tie-ins, traceado y aislación (E30, E60, H60), notas. Lo que queda fuera del límite o es de sala de control se lista como "no incluido".
- **Plano de conjunto:** tabla de materiales y lista de conexiones **texto literal** (regla crítica de CLAUDE.md), pesos, medidas, notas.
- **Especificaciones:** las clases de cañería de cada línea del P&ID (schedule por Ø, materiales, juntas, espárragos: ojo con las de baja temperatura aguas abajo de PSV y BDV), recipientes (espesor mínimo, cuellos, PH), pintura y aislación, instrumentación, eléctrica, repuestos.
- **Calidad (RC/PIE), condiciones de obra, BIM.** Los PDF marcados "posible escaneo o dibujo" en el inventario se miran como imagen.

## 3. Verificar qué falta y qué no cierra

- Lista de documentos mandatorios de la RI contra lo recibido (código por código) y contra lo que ya está en el repo de otro pedido del mismo proyecto.
- Diferencias entre documentos (cantidades, cotas, fechas, revisiones, material del plano contra la clase). Van al informe y, si hace falta, a consultas al cliente.
- Lo que no se puede definir con la información: **por pedido de Matías (25-11-2026), lo decide ITT con el mejor criterio técnico o por antecedentes**, marcado con su origen ("ITT", "antecedente X") y listado al final del informe.

## 4. Antecedentes

`python herramientas/buscar_antecedentes.py --texto "<equipo>" --cuerpo <Ø> --serie <#> --cliente <cliente>`. Abrí la planilla de costo del más parecido y más nuevo (`fuentes_originales/ofertas_texto/<carpeta>/`) y usala como modelo de la lista (qué renglones lleva un equipo así: internos, elementos, aislación, tracing, JB, cables, conduit, repuestos).

## 5. Informe: `resumen_pedido.md` + `listas_preliminares.xlsx`

Copiá `cotizaciones/COT26-0010-002_AESA_C5297_FILTROS_COALESCEDORES/listas_preliminares.py` a la carpeta nueva y reemplazá los datos (las listas del principio del script); el armado del .md y del .xlsx queda igual. Cantidades **por equipo** con columna de total por la cantidad de equipos. Secciones:
1. Resumen de la solicitud (cliente, documentos base, qué se pide, posiciones de la planilla, diseño, calidad, documentos con la oferta, no incluye).
2. Skid: tabla del plano literal y peso total; componentes del recipiente con peso aproximado; conexiones del recipiente y del límite del skid.
3. Válvulas manuales; actuadas, de seguridad y restricción (tag, tipo, Ø, serie, clase, cantidad, función, origen).
4. Instrumentos y lista de señales (analógicas / digitales, SIS / SCP); lo no incluido.
5. Piping: caños (m por Ø, sch, material y clase), accesorios y bridas de cañería.
6. Juntas y bulonería por unión (junta según la clase, espárragos por unión de `conocimiento/tecnico/esparragos_por_brida.csv`; B16.47 para > 24").
7. Elementos filtrantes e internos (si aplica) con los de repuesto.
8. Otros artículos (estructura, plataformas, batea, soportes, aislación, pintura, placas, embalaje, repuestos incluidos, opcionales).
9. Trabajo eléctrico: área clasificada, JB, cableado, canalizaciones, traceado, PAT, aire de instrumentos, documentos y pruebas. Si no tiene, decirlo.
10. Decisiones de ITT y datos que faltan.
11. **Pesos** por renglón y por rubro, con su fuente (`herramientas/pesos_soldadura.py`: kg_cano, kg_brida, kg_acc, kg_olet, kg_valvula, kg_esparrago). Sin tabla: aproximado marcado. Comparar contra el peso del plano o la HD y explicar la diferencia.
12. **Soldaduras** (pedido de Matías, 25-11-2026): por tipo (BW a tope, SW, olets) y por Ø/schedule, con juntas, pulgadas nominales (diametrales), factor de espesor y **pulgadas equivalentes**, por equipo y total. Piping con `pesos_soldadura.soldaduras_piping` (mismas reglas que `precotizar.py`); recipiente con `soldaduras_recipiente()` del modelo (costuras longitudinales y circunferenciales, cuello–brida, boquilla al cuerpo × 1,5, refuerzos); estructura e internos por kg.

Corré `python cotizaciones/<carpeta>/listas_preliminares.py` y revisá el .md completo.

## 6. Revisión independiente

Antes de pasar al skill `cotizar`, un agente que no armó las listas compara el P&ID y el plano contra las listas (tags, cantidades, Ø, series, clases, juntas) y revisa cualquier criterio de cálculo nuevo (CLAUDE.md). Sus hallazgos se corrigen o se justifican; los errores van a `conocimiento/errores_y_lecciones.md`.

## 7. Cerrar

- `bitacora.md` de la cotización: qué se recibió, qué falta, diferencias, decisiones de ITT, antecedentes y estado.
- `conocimiento/estado_y_pendientes.md` (una línea) y `cotizaciones/README.md`.
- `python herramientas/verificar_todo.py` ("TODO OK"), commit, push y pasar a `main` (`python herramientas/subir_a_main.py "mensaje"`). Los cambios que deja `verificar_todo.py` solo por la fecha del día no se suben.
- Mandar `resumen_pedido.md` y `listas_preliminares.xlsx` con SendUserFile. En el chat: 2–3 líneas de qué se hizo, los errores o diferencias encontrados y lo que Matías tiene que decidir.

## Nunca

- Enviar nada al cliente. Todo queda en borrador.
- Corregir, traducir o completar el texto del cliente en las columnas literales: lo de ITT va en origen o nota.
- Inventar un dato de norma de memoria: si no está en el repo ni en los documentos, "a verificar".
