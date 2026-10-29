# Reglas de cálculo de ITT

Cómo se calcula cada rubro de una cotización. Reconstruido de las planillas Master de ITT (2023–2026). Los valores en USD están en [`costos/tarifas.csv`](costos/tarifas.csv), con fuente y fecha.

## 1. Mano de obra de soldadura (piping, colectores, manifolds, recipientes)

La unidad es la **pulgada-diámetro equivalente** (pulg-eq):

```
pulg-eq de una junta = DN (pulg) × factor de espesor
pulg-eq totales      = Σ (cantidad de juntas × DN × factor de espesor)
costo MO soldadura   = pulg-eq totales × USD por pulg-eq
```

- El **factor de espesor** sale de [`tecnico/factores_soldadura.csv`](tecnico/factores_soldadura.csv) por DN y schedule: `factor = espesor / espesor STD del mismo DN`, con mínimo 1. Por ejemplo, 3" SCH80 = 1,388 y 3" SCH160 = 2,027. Es la regla del documento fuente original ("factores de diámetros equivalentes … espesores de pared diferentes a los estándar", con referencia al cuadro X2.2 de ASTM A53).
- Desde 12" la planilla de ITT tenía valores inconsistentes, entre 15% y 40% más bajos en paredes gruesas. Se reemplazaron por la regla única, que coincide con el documento fuente (12" SCH160 = 3,5; 16" SCH160 = 4,3). El valor anterior queda en la columna `factor_original_itt` como referencia.
- **Accesorios** ([`tecnico/factores_accesorios.csv`](tecnico/factores_accesorios.csv)): sockolet, threadolet, latrolet y elbowlet ×1,75. Weldolet ×2,5. Injerto a 90° o 45° ×1,5 (desde el diámetro menor). Refuerzo ×1,5 (desde el diámetro mayor).
- **Valor por pulg-eq:** el costo propio de planta es 19,73 USD (oct-2024). En cotizaciones se usó 28–32 USD. Un tercero cotizó 16,31 USD (sep-2024). La cotización debe mostrar cuál se usó.

## 2. Ensayos no destructivos (radiografía y tintas)

```
placas por junta  = según DN (tabla de factores: placas chicas hasta 12", grandes desde 14")
placas totales    = Σ (juntas a radiografiar × placas por junta)
servicios de RX   = ⌈ placas totales / 40 ⌉
costo RX          = placas chicas × USD/placa chica + placas grandes × USD/placa grande + servicios × USD/servicio
```

- Placa chica 9 × 21,5 cm y placa grande 9 × 43 cm.
- **Porcentaje a radiografiar:** lo define el cliente o el código. Si no se indica, la planilla base usó 20% de las juntas y "100% RX y LP donde no se pueda radiografiar".
- Para los diámetros chicos (1" y 3/4" en muchos casos) se usan tintas penetrantes: medio servicio de LP por manifold en la planilla base.
- Tarifa vigente: Antonelli, noviembre 2025.

## 3. Granallado y pintura

```
superficie (m²) = longitud de caño (m) × desarrollo (mm) / 1000     ← desarrollo = π × diámetro exterior
superficie estructura (m²) = longitud (m) × m²/m del perfil          ← tecnico/perfiles.csv
costo = superficie × (USD/m² granallado + USD/m² pintura)
```

- Overspray: +20% en piping y +30% en skids (planilla base).
- No pintar la cara RF de las bridas ni el canal de la junta. Va como nota en el plano y no cambia la superficie.

## 4. Estructura (bastidores, skids, plataformas)

```
kg de estructura = Σ (largo (m) × kg/m del perfil × cantidad)        ← tecnico/perfiles.csv
costo material   = kg × USD/kg (chapa y perfiles ≈ 1,16–1,72 USD/kg + 10% de recortes)
costo MO         = kg × USD/kg de mano de obra de estructura
```

- Desperdicio de material en skids: +20% (planilla base).
- ⚠️ La planilla "Costos MO Master" busca los kg/m de los perfiles W en una columna equivocada: un W 460×52 da 949,8 kg/m en lugar de 52,2. La tabla de esta base está corregida y validada contra la designación.

## 5. Bulonería de bridas

Cantidad y medida de espárragos por DN y serie: [`tecnico/esparragos_por_brida.csv`](tecnico/esparragos_por_brida.csv). Cada espárrago lleva 2 tuercas.

## 6. Precio de venta

```
precio de venta por rubro = costo × factor de rentabilidad del rubro
margen sobre venta        = (precio − costo) / precio
```

| Rubro | Factor habitual | Nota |
|---|---|---|
| Materiales, mano de obra y servicios | 1,33 – 1,35 | **Lo define la dirección en cada cotización** |
| Mano de obra de terceros | 1,35 | |
| Válvulas Taval | 1,00 | Empresa del grupo; la lista Taval ya trae coeficiente 1,25 |
| Seguro de caución | 1,00 | A costo |
| Transporte | 1,00 | A costo |

- Un factor de 1,35 da un margen de 25,9% sobre la venta, y uno de 1,33 da 24,8%.
- En el seguimiento de cotizaciones 2024–2026 el factor (`Fx`) va de 1,2 a 1,8, con 1,4–1,5 lo más habitual.
- En las cotizaciones de 2026 con planilla de costo, el factor nominal es casi siempre **1,35** sobre materiales y MO (MO a veces 1,4; instrumentos 1,35–1,5; válvulas Taval y caución 1,0). Las bonificaciones lo bajan a un efectivo de 1,30–1,33. **Las 5 cotizaciones ganadas de 2026 que tienen costo cerraron con factor de 1,28 a 1,35** (mediana de todas las ofertas con costo: 1,34). Factores más bajos (1,15–1,25) aparecen en ofertas grandes y competitivas, como piping y puentes en cantidad.
- IVA: 21%. Se agrega aparte, porque los precios se cotizan sin IVA.
- Moneda: USD. Entrega estándar: EXW en la planta de ITT (Av. 12 de Octubre 4004, Quilmes Oeste).

## 7. Errores conocidos en las planillas originales (no repetir)

| Planilla | Error |
|---|---|
| Planilla base para cotizaciones | El total de venta `F20` no suma el transporte. `H20` multiplica por la cantidad de válvulas Taval (`B16`) en lugar de la cantidad del ítem. Los subtotales no están vinculados al resumen. La cantidad de servicios de RX está escrita a mano. |
| Costos MO Master | Toma de una columna equivocada los kg/m de los perfiles W. La fórmula de servicios de RX tiene referencias relativas (`AY7`, `AZ11`, `AY16`) que dan un resultado incorrecto en algunos rangos. Usa vínculos a otro archivo (`[1]Tabla Principal`), que se rompen al copiarla (#N/A). |
| Costos MO (dic-2023) y Resumen | Llenos de #REF! por vínculos rotos. |
| Lista Taval 30 | Columnas de precio con #REF!. |
| Factores de soldadura (todas) | 3/4" XXS cargado como 27 y 204 en la versión de 2023 (debería ser 2,7 y 2,04). 1/2" SCH160 y XXS cargados como 3/8", heredado del escaneo original. 6" STD escrito "SDT". Desde 12", factores que no siguen la regla (cambiados de un lado a otro entre feb y mar de 2026). Todo corregido en esta base. |


## Juntas, pesos aproximados y procedimientos (29-10-2026)
- **Juntas a tope enteras:** con caño por metro, cada extremo BW de accesorio o brida cuenta como media junta × 2 × 0,75 (uniones directas); el total de juntas se redondea hacia arriba. Las pulgadas equivalentes no se redondean.
- **Peso sin tabla (APROXIMADO):** accesorio a tope = kg/m del caño (mismo Ø y schedule) × OD × largo equivalente en diámetros, calibrado con las tablas (`tecnico/factores_peso_aproximado.csv`: codo 90 RL 2,24; codo 45 1,18; tee 3,04; reducción 0,80; casquete 0,67). Forjados y válvulas: clase o serie más cercana. Juntas: anillo × densidad. Termovaina bridada: brida ciega. Instrumentos: no se pesan.
- **Procedimientos del equipo:** WPS/PQR por grupo de material (carbono o inoxidable) y tipo de junta (a tope; socket y filete), una WPQ por WPS, procedimiento de RX si hay radiografía, de LP si hay juntas SW u olets, de prueba hidráulica y de pintura. Los de END se costean con la tarifa de procedimiento escrito nivel 3 (USD 250 por trabajo, repartido entre los equipos).
