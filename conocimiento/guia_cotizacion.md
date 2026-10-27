# Guía para cotizar un pedido, paso a paso

Cómo se cotiza un pedido nuevo con el cotizador, de principio a fin. Las reglas obligatorias están en [`procedimiento_cotizacion.md`](procedimiento_cotizacion.md) (P1–P10). Esta guía dice **qué hacer, con qué archivo y con qué comando** en cada paso. El caso modelo es la [COT26-1003-001 (CAPEX OQ8209)](../cotizaciones/COT26-1003-001_CAPEX_OQ8209/bitacora.md).

## Resumen

```
Pedido del cliente (mail, PDF, DWG)
  │ 1. Abrir la carpeta de la cotización          cotizaciones/COTAA-CCCC-NNN_<CLIENTE>_<PEDIDO>/
  │ 2. Transcribir la tabla del plano             pedido/lista_materiales_plano.csv
  │ 3. Buscar antecedentes y precios              conocimiento/ + fuentes_originales/ofertas_texto/
  │ 4. Cargar los ítems con sus fuentes           cotizacion.json
  │ 5. Armar todo                                 python herramientas/armar_cotizacion.py <carpeta>
  │ 6. Revisar avisos y comparables               salida del comando + informe.html
  │ 7. Revisión independiente                     otro agente o persona
  │ 8. Aprobación (Matías / dirección)            "estado": "aprobado" + volver a armar
  ▼ 9. Enviar y registrar el resultado            cotizaciones/README.md
```

## 1. Abrir la carpeta

- Código: `COT[AA]-[código de cliente de 4 dígitos]-[NNN]`. El código del cliente está en `conocimiento/comercial/clientes.csv` (por ejemplo, CAPEX = 1003).
- Copiar `cotizaciones/_plantilla/` a `cotizaciones/COT26-1003-001_CAPEX_OQ8209/` (código, cliente y pedido).
- Guardar los originales del cliente en `pedido/`: orden o pliego, planos y especificaciones. Si el plano viene en DWG: `python herramientas/leer_dwg.py`.
- Anotar la cotización en [`cotizaciones/README.md`](../cotizaciones/README.md) con estado `borrador`.

## 2. Transcribir la tabla del plano (P1, P2)

- `pedido/lista_materiales_plano.csv`: **una fila por posición del plano, con todas sus columnas** (pos, descripción, Ø, serie o schedule, material, extremos, modelo o fabricante, cantidad, unidad). Se copia tal cual, sin interpretar.
- Leer también las **notas del plano** (pintura, revestimientos, alternativas) y el **dibujo**, para ver qué extremos se sueldan en taller y cuáles quedan para campo.
- Anotar los requisitos del pedido: ensayos, registros, marcas exigidas, fechas y lugar de entrega.

## 3. Buscar antecedentes y precios (P4, P5, P8)

Por orden de prioridad:

| Qué | Dónde |
|---|---|
| Ofertas parecidas (mismo cliente o mismo equipo) | `conocimiento/comercial/cotizaciones_2026.csv`, `cotizaciones_2024-2026.csv`, `fichas_2026/`, y el texto original en `fuentes_originales/ofertas_texto/<CLIENTE>/<carpeta>/` |
| **Planilla de costo de una oferta equivalente** (es el mejor modelo) | `fuentes_originales/ofertas_texto/.../4.Armado de la Oferta Comercial/*.xlsx.txt` o `7.Propuesta.../*.xlsx.txt` |
| Precios de proveedores con fecha | `conocimiento/precios/indice_precios.csv` (2.680 precios) y `proveedores_2026.csv` |
| Accesorios, caños y bridas | `conocimiento/precios/lista_renar_2025-12.csv` (con código) |
| Stock ITT | `conocimiento/precios/stock_2024-11.csv` (lo que hay en stock no suma plazo) |
| Mano de obra de terceros | `indice_precios.csv` (Ledesma, Quesada…) y `costos/tarifas.csv` |
| Costo propio de planta | `costos/costo_hora_planta.csv`, `costos/tarifas.csv` (soldador 19,73 USD/pulg-eq, oct-2024) |
| Soldadura | `tecnico/factores_soldadura.csv` (pulg-eq = DN × factor de espesor) y `tecnico/factores_accesorios.csv` (cupla/olet ×1,75) |
| Plazos | `conocimiento/plazos.md` |
| Errores que ya pasaron | [`errores_y_lecciones.md`](errores_y_lecciones.md) |

**Reglas que más se olvidan:**
- Abrir el documento original de cada precio. **Nunca usar un precio de memoria ni de un resumen.**
- Comparar la especificación cotizada con la del plano: Ø, serie, material de cuerpo y trim, extremos, modelo.
- La MO de terceros tiene que salir de un trabajo con el **mismo alcance**.
- Un precio "aproximado", verbal o por WhatsApp es `est` (estimado), nunca precio de base.
- Si el original es una imagen (WhatsApp, escaneo), está en el RAR de Drive (ver `CLAUDE.md`). Hay que extraerlo y leerlo.

## 4. Cargar `cotizacion.json`

Cada ítem lleva todas sus fuentes de precio. **La primera fuente es la de base**; las demás son alternativas que se pueden elegir en el informe. Los campos se explican en [`cotizaciones/_plantilla/README.md`](../cotizaciones/_plantilla/README.md).

- `grupo`: `material`, `mo` (armado, soldadura) o `servicio` (PH, pintura, calidad, insumos).
- `tipo` de cada fuente: `cot` (cotización de proveedor), `lista`, `stock`, `ant` (antecedente de otra oferta ITT), `est` (estimado).
- `fecha` de cada fuente: la fecha del precio. Con esa fecha se hace el ajuste por inflación.
- Una fila por posición del plano, con la cantidad del plano. Lo que se compra de más va en una fila `14b`.
- Soldaduras: una fila de MO con las pulgadas equivalentes, junta por junta en la especificación.
- Parámetros: factores 1,35 / 1,35, contingencia 5%, ajuste por inflación activado y `fecha_referencia` igual a la de hoy.

## 5. Armar todo

```bash
python herramientas/indices_inflacion.py            # solo si se cargaron meses nuevos de IPC, dólar o CPI
python herramientas/armar_cotizacion.py cotizaciones/<carpeta>
```

Genera `computo.csv`, la planilla `.xlsx` con fórmulas, `informe.html` y, si hay `oferta.json`, las ofertas técnica y económica en Word y PDF. También:
- calcula el precio en Python y lo compara con la planilla recalculada con LibreOffice. Si no coinciden, frena;
- corre `verificar_computo.py` contra la tabla del plano. Si hay errores, frena.

Para publicar o actualizar el informe web se usa la herramienta Artifact con `informe.html`.

## 6. Revisar (P8)

- Revisar **uno por uno los avisos** del control: soldaduras de campo o taller, modelos exigidos, estimados, precios viejos.
- Comparar el precio con al menos 2 antecedentes. **Si la diferencia es mayor al 15%, explicarla rubro por rubro.**
- Verificar que el plazo cubra el material más largo.
- Dejar los desvíos y los pendientes escritos en `cotizacion.json`.

## 7. Revisión independiente (P9)

Alguien que no armó el cómputo (otro agente o una persona) compara `pedido/lista_materiales_plano.csv` y el plano con `computo.csv`, el informe y la planilla. Lo que encuentre se corrige o se justifica, y se anota en el historial (`historial_html`) y en [`errores_y_lecciones.md`](errores_y_lecciones.md) si fue un error. Recién ahí `"estado": "revisado"`.

## 8. Aprobación y oferta

- La dirección o Matías definen el factor final y aprueban.
- En `cotizacion.json` y `oferta.json`: `"estado": "aprobado"`. Completar los datos marcados entre [corchetes]: número de PRES, teléfonos, marcas a confirmar.
- Volver a correr `armar_cotizacion.py`. Sin el estado "aprobado", la oferta sale con la marca **"BORRADOR – NO ENVIAR"**.
- **El cotizador nunca envía nada al cliente.** La oferta la manda Matías.

## 9. Registrar

- `cotizaciones/README.md`: estado, precio, fecha de envío y, después, **el resultado** (ganada o perdida y por qué).
- `bitacora.md` de la cotización: qué se hizo, qué se decidió y por qué.
- Todo se sube al repositorio (`git commit` + `git push`). Lo que no se sube se pierde.

## Mantenimiento de la base

| Para… | Se hace |
|---|---|
| Actualizar la inflación | Agregar el IPC, el dólar BNA y el CPI del mes en `herramientas/indices_inflacion.py` (con su fuente) y correrlo |
| Sumar precios de una cotización nueva | Los precios con fuente quedan en `cotizacion.json`. Para sumarlos a la base general: `herramientas/indice_precios.py` |
| Cambiar el formato de la oferta | `plantillas/oferta_itt_2026.docx` (ver `plantillas/README.md`) |
| Cambiar el diseño del informe | `plantillas/informe_cotizacion.html` |
