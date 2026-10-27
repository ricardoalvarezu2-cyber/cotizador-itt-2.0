# Codificación de materiales (Taval / ITT)

Fuente: *HD Instructivo de codificacion.xlsx* (2007–2023). Es la misma lógica que usan los códigos de artículo del stock, de la lista Taval y de los remitos.

## Código de válvula

```
E00  050  1  R  01  1  01  V
│    │    │  │  │   │  │   └─ Mando           mandos.csv              (V = volante)
│    │    │  │  │   │  └──── Trim / internos  (según tipo de válvula)
│    │    │  │  │   └─────── 3ª boca y empaquetadura
│    │    │  │  └─────────── Material          materiales.csv          (01 = ASTM A216 WCB)
│    │    │  └────────────── Extremos          extremos.csv            (R = RF)
│    │    └───────────────── Serie             series.csv              (1 = 150)
│    └────────────────────── Diámetro          diametros.csv           (050 = 2")
└─────────────────────────── Tipo de válvula   valvula_tipos.csv       (E00 = esclusa cuña sólida)
```

Ejemplo del instructivo: `E000501R01101V` = Esclusa Ø2" #150 RF ASTM A216 WCB.

Las esféricas, API 6A, filtros Y y mariposas tienen variantes del esquema (asiento, vástago y esfera, malla). El detalle está en las hojas `ESF`, `API 6A`, `FIL` y `MARIPOSA` del instructivo original.

## Tablas

| Archivo | Contenido |
|---|---|
| `valvula_tipos.csv` | Unos 300 tipos de válvula y accesorio (esclusa, globo, retención, esférica, aguja, API 6A…) |
| `diametros.csv` | Código de 3 dígitos y pulgadas |
| `series.csv` | Código de 1 carácter y serie: clases 125 a 15000, PN y schedules. ⚠️ La letra `H` aparece dos veces (125 y SCH 10) en el original |
| `extremos.csv` | RF, RJ, BW, SW, NPT, combinaciones |
| `materiales.csv` | Unos 250 materiales (ASTM, AISI, aleaciones) |
| `mandos.csv` | Volante, palanca, reductor, actuadores |
| `componentes.csv` | Unos 500 componentes de válvula (para repuestos y mecanizado) |
| `filtros_mesh.csv` | Filtros Y por malla |
| `familias_producto.csv` | Familias de producto de ITT para el registro de cotizaciones (V, C, CA, CO, F, M, SK…) |

El maestro de clientes del instructivo está en [`../comercial/clientes.csv`](../comercial/clientes.csv), con el código oficial de 4 dígitos (por ejemplo, 0007 = Almacenes Petroleros).
