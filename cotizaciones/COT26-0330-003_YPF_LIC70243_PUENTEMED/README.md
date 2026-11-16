# Carpeta modelo de una cotización

Copiar esta carpeta a `cotizaciones/COT[AA]-[CCCC]-[NNN]_<CLIENTE>_<PEDIDO>/` y completarla. El paso a paso está en [`conocimiento/guia_cotizacion.md`](../../conocimiento/guia_cotizacion.md).

| Archivo | Qué es | Quién lo hace |
|---|---|---|
| `pedido/` | Originales del cliente: orden o pliego, planos, especificaciones | Se copian tal cual |
| `pedido/transcripcion.json`, `pedido/transcripcion_b.json` | Dos lecturas literales de la tabla del cliente, hechas por separado | Dos agentes o personas |
| `pedido/requisitos.csv` | Matriz de requisitos: cada requisito del pedido con su destino (cumple, renglon, desvio, exclusion, consulta) | Se completa al leer el pedido |
| `pedido/lista_materiales_plano.csv` | Tabla de materiales del plano, renglón por renglón, con todas sus columnas | Se copia de la transcripción |
| `cotizacion.json` | **Única fuente de datos**: ítems con todas sus fuentes de precio, parámetros y textos del informe | Se completa |
| `oferta.json` | Textos de la oferta técnica y económica (objeto, desvíos, exclusiones, condiciones, firma). Opcional | Se completa |
| `computo.csv`, `*.xlsx`, `informe.html`, `oferta/` | Salidas | Las genera `herramientas/armar_cotizacion.py`. **No editar a mano** |
| `bitacora.md` | Qué se hizo, qué se decidió y por qué, en orden | Se escribe durante la cotización |

## Campos de `cotizacion.json`

| Campo | Contenido |
|---|---|
| `codigo`, `revision`, `estado`, `fecha`, `preparo` | `estado`: `borrador` → `revisado` → `aprobado` → `enviado` |
| `cliente` | nombre, código ITT de 4 dígitos, comprador |
| `titulo`, `titulo_pagina`, `archivo_planilla`, `subtitulo_planilla`, `meta` | Textos del encabezado del informe y nombre de la planilla |
| `equipo` | `singular` / `plural` ("puente" / "puentes") |
| `parametros` | `N` cantidad · `FM` factor de materiales · `FMO` factor de MO y servicios · `CONT` contingencia % · `AJ` ajuste por inflación (1/0) · `TRANS` flete incluido (1/0) · `TC` dólar · `TR_ARS` flete en pesos · `TR_EMB` embalaje USD · `TR_F` factor flete · `fecha_referencia` (hoy) |
| `plazo` | `dias`, `texto`, `tareas` (`[nombre, día inicio, día fin, "crit"/"tal"/""]`) y `nota` |
| `flete` | etiqueta, referencia de precio y criterio |
| `historial_html` | Correcciones hechas a la cotización (se muestran arriba del informe) |
| `pedido` | `eyebrow`, `datos_html` (pares dato–valor) y `requisitos_html` |
| `nota_mo_html` | Alcance de la MO, soldaduras de taller junta por junta, extremos para campo |
| `desvios` | `tag` (posiciones), `titulo`, `texto` |
| `antecedentes` | Ofertas usadas: carpeta, fecha, qué es, precio, qué se tomó |
| `pendientes` | Bloques de confirmaciones pendientes (proveedores, cliente) |
| `compras` | Para la lista que va a Compras (`compras/*.xlsx`): `fecha_respuesta`, `material_en_planta_dias`, `lugar_entrega`, `requisitos_generales`, `notas` y `proveedores` por posición del plano, `cantidad_compra` (si se compra distinto de cantidad × equipos, p. ej. tira de caño) y `servicios` (armado, pintura, flete) |
| `justificaciones` | Levantan frenos de la oferta (`herramientas/frenos.py`): `estimado` (más del 15% estimado), `vencidas` (cotizaciones de proveedor vencidas), `antecedentes` (sin antecedente comparable o más del 15% de diferencia, explicado rubro por rubro). El plazo se justifica en `plazo.justificacion` |
| `origen_lista` | Solo si no hay tabla del cliente: `{"tipo": "diseno_itt", "motivo": "..."}`. Si hay tabla, van `pedido/transcripcion.json` y `pedido/transcripcion_b.json` (doble lectura) |
| `pie`, `planilla_notas` | Pie del informe y notas de la hoja Resumen |
| `items` | Ver abajo |

Cada ítem:

```json
{"id": "M07", "pos": "7", "grupo": "material", "descripcion": "Válvula de retención 2\" #600 a clapeta",
 "especificacion": "Cuerpo A216 · trim AISI 316 · NPT-H", "cantidad": 2, "unidad": "un",
 "fuentes": [
   {"tipo": "cot", "precio": 533, "proveedor": "Ingeniería en Fluidos (S600, stock)", "origen": "APSA/15 · Capsa Capex puentes AIB", "fecha": "2026-06-11"},
   {"tipo": "cot", "precio": 240, "proveedor": "Danco, aprox. sin confirmar", "origen": "APSA/15", "fecha": "2026-06-11"}]}
```

En una fuente `cot` (cotización de proveedor) se carga `validez_hasta` (AAAA-MM-DD, la que dice el documento) y, si se reconfirmó, `reconfirmado` (AAAA-MM-DD). Sin validez escrita se toma 30 días desde `fecha`; vencida, frena la oferta.

- `id`: `M01…` para materiales y `S01…` para MO y servicios. No se cambia después: identifica la fila al exportar e importar el CSV desde el informe.
- `pos`: la posición del plano; `14b` para compras extra; `MO`, `PH`, `PIN`, `CAL`, `INS` para MO y servicios.
- `grupo`: `material`, `mo` o `servicio`.
- `coincide` (obligatorio en la fuente de base): `igual`, `similar` o `sin_ref`; y `diferencia`: en qué difiere del plano (obligatorio si es `similar`).
- `fuentes`: **la primera es la de base**. `tipo`: `cot`, `lista`, `stock`, `ant` o `est`. `fecha`: la del precio (AAAA-MM-DD, AAAA-MM o AAAA), que se usa para el ajuste por inflación.

El `cotizacion.json` de esta carpeta es un ejemplo mínimo que funciona. Para probarlo, copiar la carpeta a otro lugar, sacar `oferta.json` y correr `python herramientas/armar_cotizacion.py <copia>`; no se corre sobre la plantilla. `oferta.json` tiene los textos de la oferta a CAPEX como ejemplo: hay que reemplazarlos. El caso completo es `cotizaciones/COT26-1003-001_CAPEX_OQ8209/`.
