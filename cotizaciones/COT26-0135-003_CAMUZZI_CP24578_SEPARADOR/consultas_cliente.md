# Consultas a Camuzzi — COT26-0135-003 (separador vertical coalescente)

**Borrador, no enviar.** Las redacta el cotizador; las manda Matías por el portal de compras de Camuzzi (Consultas del Concurso). Cada consulta abierta es un requisito en `pedido/requisitos.csv` con destino `consulta`: mientras no tenga respuesta, las ofertas no salen (`herramientas/frenos.py`). Al recibir la respuesta, anotarla acá con fecha y cambiar el destino del requisito.

Preparadas el 30-10-2026.

## Para enviar al cliente

**C1 — Concurso y fecha de apertura** (requisito R027)
> El Concurso de precios N° 24527 (Filtro Coalescente) tenía apertura el 20-10-2026 y su planilla describe el mismo equipo que el ítem 1 del Concurso N° 24578 (2 separadores verticales coalescentes). ¿Ambos concursos siguen abiertos? ¿Debemos cotizar los 2 equipos en uno solo de ellos? ¿Cuál es la nueva fecha de apertura?

**C2 — Tipo de elemento filtrante** (requisito R049)
> La planilla de cotización pide un separador de líquido coalescente con cartuchos de 914 × 140 mm y filtrado de 0,3 µm, y la especificación técnica (punto 9) indica elementos de "material celulósico, malla reforzada y armadura de refuerzo zincada, con junta de goma", con 98% de eficiencia para partículas de polvo de 0,3 µm o más (9.1). ¿Los elementos deben ser coalescentes (microfibra de vidrio, para separar líquido en neblina) o filtrantes de papel celulósico? Si son coalescentes, ¿hay un caudal de líquido o un contenido de líquido de diseño en el gas?

**C3 — Lugar de entrega** (requisitos R031 y R111)
> La planilla del Concurso N° 24578 indica flete a cargo del proveedor hasta Transporte Cruz del Sur (Mercado Central, nave D3); las cláusulas particulares del Concurso N° 24527 indican "Destino Final a determinar" y la especificación técnica (punto 13), el transporte hasta el destino final indicado en la Nota de Pedido. ¿Cuál es el lugar de entrega a cotizar? Si es el destino final, ¿en qué localidad?

**C4 — Temperatura de diseño y plano tipo** (requisito R052)
> La especificación técnica no indica temperatura de diseño (mínima y máxima) ni la temperatura mínima de metal de diseño (MDMT). ¿Cuáles son? Con el espesor que resulta del diseño (≈ 57 mm) ese dato define si la chapa debe ser normalizada o llevar ensayos de impacto (ASME VIII Div.1 UCS-66). La especificación menciona además "el plano tipo correspondiente": ¿nos pueden enviar el plano tipo, o el Esquema General Filtro Coalescente Camuzzi 2026 es el único documento de referencia?

**C5 — Especificaciones de Camuzzi citadas** (requisitos R042, R090 y R091)
> No recibimos las especificaciones citadas en la ET: SCE-PC-511-0003 (protección anticorrosiva), SCE-IN-501-0008 y SCE-RE-308-0001 (válvulas esféricas y su ensayo), SCE-IN-301-0005 (procedimiento general de soldadura), SCE-IN-501-0003 (juntas), SCE-IN-501-0013 (espárragos), SCE-IN-301-0001, SCE-IN-101-0003/0004/0005, SCE-IN-107-0004, SCE-PR-506-1000 y SCE-PR-106-1000. ¿Nos las pueden enviar, o confirmar que las vigentes son las publicadas en camuzzigas.com/info-contratistas.php?
>
> *Nota interna:* si se pueden descargar de la página de Camuzzi, alcanza con bajarlas, guardarlas en `pedido/` y revisar la pintura y las válvulas contra la cotización; ahí se cierra C5 sin preguntar.

## Consultas sugeridas (no frenan: se cotizó la opción que cumple; decide Matías si se mandan)

- **Presión de diseño.** La ET 9.16.1 pide la prueba de resistencia a 1,3 × la presión máxima de la serie ANSI (≈ 133 bar). Se cotizó el recipiente diseñado a la presión de la serie #600 (102,1 bar, 2 1/4"). Hay otra opción sin preguntar nada: diseñar a 77 bar (1 5/8") y verificar en la memoria que la PH a 133 bar no supere las tensiones admisibles en la prueba (1,3 × MAWP es el mínimo de ASME, no un máximo). Lo decide Matías o la dirección (ver bitácora). También se puede preguntar si la prueba puede hacerse a 1,3 × la presión de diseño del recipiente.
- **Moneda y plazo.** Cotizamos en dólares y con 230 días (desvíos declarados en la oferta). El pliego general (8.7) desestima las ofertas que modifiquen sus condiciones: conviene preguntar si aceptan la cotización en USD y el plazo, como en el Concurso N° 22737 (CAMUZZI/30, cotizado en USD a 120 días).
- **Vicios ocultos sin límite de tiempo** (ET 14): confirmar con la dirección de ITT si se acepta tal cual.

## Pendientes de ITT que también frenan (no se mandan al cliente)

**P1 — Memoria de cálculo** (requisito R017) y **P2 — Esquema con dimensiones generales** (requisito R018): la planilla exige entregarlos con la cotización y todavía no existen. Están cargados con destino `pendiente_itt` (frenan la oferta); se cierran (destino `renglon`, referencia `HH`) cuando estén hechos y adjuntos.
