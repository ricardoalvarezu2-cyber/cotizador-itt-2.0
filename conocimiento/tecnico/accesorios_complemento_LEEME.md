# Pesos de accesorios: complemento (28-10-2026)

Complementa `accesorios_peso.csv` (que no se tocó) con `accesorios_peso_complemento.csv`: **2.893 renglones**, mismas 10 columnas, `peso_kg` en kg, cada renglón con su `fuente_url` y `fuente_nombre` ("consultado 2026-10-28"). **Estado: borrador, sin revisar por Matías.** Nada está inventado, interpolado ni extrapolado entre schedules. Lo que la fuente da en lb se convirtió × 0,45359 y la nota lo dice con el valor original en lb. Todos son pesos **aproximados** (B16.9, B16.11 y MSS no fijan pesos; cada fabricante publica los suyos).

**447 renglones llevan "ATENCION" en la nota** (incoherencias que se detectaron, ver más abajo). Filtrar por esa palabra antes de usar un valor.

## Cómo leer el archivo

- Tipos que ya existían con el mismo nombre: `codo_90_radio_largo`, `codo_90_radio_corto`, `codo_45`, `tee_recta`, `tee_reduccion`, `reduccion_concentrica_excentrica`, `casquete`.
- Tipos nuevos: `codo_90_3d`, `codo_45_3d`, `codo_90_reductor` (codo 90° de reducción), `codo_180_radio_largo`, `codo_180_radio_corto`, `cruz`, `stub_end_largo` (largo de B16.9), `stub_end_corto` (largo MSS SP-43), `buje_reductor`, `cupla_reductora`, `union_doble`, `codo_90_calle`, `niple`, `swage_nipple`.
- `dn_pulg` y `dn2_pulg` en pulgadas decimales, mayor primero (en tees de reducción: `dn` = corrida, `dn2` = derivación).
- `schedule_o_clase`: `10S`, `40S`... para inoxidable; `40`, `80`, `60`, `120`... para carbono; `2000`, `3000`, `6000`, `9000` para forjados. En los forjados `extremos` es `NPT` o `SW`.
- **Niples**: el archivo no tiene columna de largo, así que el largo va en `extremos`, por ejemplo `NPT L=4in` o `NPT L=close(3/4in)` (L = largo total del niple, roscado en ambos extremos).
- `norma` indica la tabla de origen: `ASME B16.9`, `MSS SP-43` (inoxidable 5S/10S y stub end corto), `ASME B16.11`, `MSS SP-83` (uniones), `MSS SP-79` (insertos socket weld), `MSS SP-95` (swage), `ASTM A733` (niples).

## Fuentes (todas consultadas el 28-10-2026)

Copias en `fuentes_originales/tablas_pesos/` (las páginas de Texas Flange como HTML, que es lo que se leyó; los catálogos en PDF).

| Fuente | Qué aportó | Confiabilidad |
|---|---|---|
| **Texas Flange**, tablas "all schedules" de butt weld: https://texasflange.com/butt-weld-fittings/ (13 páginas: codos 90 RL/RC/3R, 45 RL/3R, codo reductor, tee, tee de reducción, reducción, casquete, stub end, curvas 180 RL/RC) | Sch STD, XS, 40, 80, 160, XXS en lb: **Sch 40 y 80 de todas las medidas**, 3D (3R), 180°, stub end largo, codo reductor y huecos de los tipos que ya existían | **Es el mismo dato que el catálogo Weldbend 63ª edición** (se comparó: codo RL STD, casquete Sch 80, tees; idéntico, hasta en los errores). Dos páginas, una sola fuente. Ver "Hallazgos". |
| **Weldbend**, catálogo 63ª edición: https://www.weldbend.com/catalog.pdf | Control cruzado de Texas Flange (no se cargaron renglones propios, serían copia) | Fabricante. Sus tablas Sch 40 y 80 de medidas grandes tienen los problemas de abajo |
| **Hackney Ladish**, Catálogo 55 (1955), sección Seamless Welding Fittings: https://www.hackneyladish.com/catalog/B.pdf (escaneo, sin texto; se transcribió a mano y se releyó contra la imagen, más un OCR de control) | **Schedules especiales**: Sch 30 (8" y 10"), 60 (18", 20", 24"), 80 (10"–14"), 100 (12"), 120 (4"–14") en codo 90 RL, codo 45 y curva 180 RL (pág. 40, 50 y 55 del catálogo); stub end STD y XS (pág. 82 y 83) | Muy buena: el peso sigue el espesor de pared (ver verificación). Catálogo viejo; Hackney Ladish lo publica "como referencia de la industria, no refleja la oferta actual" |
| **CCTF**, Stainless Steel Welding Fittings: https://www.cctf.com/catalogues/stainless_welding_fittings.pdf | **Inoxidable 5S/10S/40S/80S** (MSS SP-43 y B16.9): codo 90 RL, 90 RC, 45, tee recta y de reducción, reducción, casquete, stub end corto (MSS) y largo (ANSI) hasta 12" | Buena. Hay tipeos puntuales (marcados) |
| **CCTF**, Seamless Welding Fittings: https://www.cctf.com/catalogues/seamless_welding_fittings.pdf | **Cruces B16.9** STD y XS, 1 1/4" a 24" | **Mala para cruces**: la cruz pesa menos que la tee desde 2 1/2" (marcado) |
| **Smith-Cooper**, Forged Carbon Steel Fittings: https://www.buyfittingsonline.com/content/pipe-fittings-forged-carbon-steel-specifications-sizing-3000-6000-lb.pdf (columna "Weight LB") | Forjados B16.11: buje hexagonal reductor, cupla reductora, unión SP-83 (NPT y SW), cruz, codo de calle, inserto SW | Aceptable (0,1 lb de resolución; hay tipeos, marcados) |
| **Bonney Forge**, FSFU.pdf: https://bonneyforge.com/assets/files/FSFU.pdf (pesos en lb, ver `pesos_LEEME.md`) | Cruz 2000/3000/6000 NPT y 3000/6000/9000 SW, codo de calle 3000/6000, unión SP-83 3000/6000, inserto reductor SW (MSS SP-79) 3000/6000/9000 | Buena |
| **SCI / Smith-Cooper**, hojas "Steel Nipples Schedule 40 / 80 Welded" (Fig. 83NI4 y 83NI8): https://fwwebbimage.fwwebb.com/ProductInfo/SCI_NIP_B_G_S40.pdf y `..._S80.pdf` | Niples soldados NPT por largo, Sch 40 y 80 | Buena (un tipeo marcado) |
| **Sunhy**, https://sunhyings.com/?p=7234 | Swage nipples MSS SP-95 (kg) | **Baja**: un solo peso "Standard & Extra Heavy", sin schedule; todos marcados ATENCION |
| **Aalco**, https://www.aalco.co.uk/literature/files/aalco-stainless-steel-tube-butt-weld-fittings.pdf | **No se cargó.** Tabla de factores por schedule (ver "Cómo estimar lo que falta") | Es un método, no un peso medido |

Consultados sin resultado: Tube Turns (su página de literatura lista solo cierres, bridas y otros productos, sin tablas de pesos de accesorios), Erne (su página de descargas no trae tablas de pesos), Tectubi, Mills Iron Works y Taylor Forge (el sitio no resolvió), Sandvik y Smith-Cooper/ASC (sin tablas de pesos de accesorios a tope), Scribd y blog.projectmaterials (bloqueados). No se leyeron en profundidad todos los PDF de Erne. Weldbend y Texas Flange publican solo STD, XS, 40, 80, 160 y XXS: **no hay Sch 10, 20, 60, 100, 120 ni 140 en ninguno**.

## Cobertura (renglones por tipo y schedule/clase)

| Tipo | Total | Schedule o clase: renglones |
|---|---|---|
| `codo_90_radio_largo` | 129 | 5S 15, 10S 15, 40S 15, 80S 15 (inox); 30: 2, 40: 20, **60: 3**, 80: 23, **100: 1, 120: 6**, STD 2, XS 2, 160: 6, XXS: 4 |
| `codo_90_radio_corto` | 115 | 5S/10S/40S/80S: 10 c/u; 40: 18, 80: 18, STD 4, XS 6, 160: 17, XXS: 12 |
| `codo_90_3d` / `codo_45_3d` | 76 / 76 | STD, XS, 40, 80: 19 c/u (0,75" a 24") |
| `codo_90_reductor` | 132 | STD, XS, 40, 80: 33 c/u |
| `codo_45` | 152 | 5S/10S/40S/80S: 15 c/u; 30: 2, 40: 20, 60: 3, 80: 23, 100: 1, 120: 6, 160: 19, XXS: 14, STD 2, XS 2 |
| `codo_180_radio_largo` | 128 | STD, XS: 20 c/u; 30: 2, 40: 20, 60: 3, 80: 23, 100: 1, 120: 6, 160: 19, XXS: 14 |
| `codo_180_radio_corto` | 101 | STD, XS, 40, 80: 18 c/u; 160: 17, XXS: 12 |
| `tee_recta` | 113 | 5S/10S/40S/80S: 15 c/u; 40: 20, 80: 20, 160: 5, XXS: 4, STD 2, XS 2 |
| `tee_reduccion` | 345 | 5S/10S/40S/80S: 50 c/u; 40: 31, 80: 36, 160: 31, XXS: 13, STD 17, XS 17 |
| `reduccion_concentrica_excentrica` | 369 | 5S 53, 10S 52, 40S 53, 80S 53; 40: 31, 80: 35, 160: 31, XXS: 15, STD 23, XS 23 |
| `casquete` | 121 | 5S/10S/40S/80S: 15 c/u; 40: 20, 80: 20, 160: 7, XXS: 4, STD 5, XS 5 |
| `cruz` (B16.9) | 34 | STD 17, XS 17 |
| `cruz` (B16.11) | 104 | NPT 2000: 20, 3000: 24, 6000: 18; SW 3000: 23, 6000: 13, 9000: 6 |
| `stub_end_largo` | 168 | 40S: 15; STD: 40, XS: 40 (dos fuentes), 40: 20, 80: 20, 160: 19, XXS: 14 |
| `stub_end_corto` (MSS SP-43) | 30 | 10S: 15, 40S: 15 |
| `buje_reductor` | 154 | NPT hexagonal 2000/3000/6000: 54; SW inserto 3000: 60, 6000: 25, 9000: 15 |
| `cupla_reductora` | 96 | NPT 3000: 52, 6000: 6; SW 3000: 38 |
| `union_doble` (MSS SP-83) | 49 | NPT 3000: 22, 6000: 10; SW 3000: 11, 6000: 6 |
| `codo_90_calle` | 26 | NPT 3000: 18, 6000: 8 |
| `niple` | 340 | Sch 40: 188, Sch 80: 152 (1/8" a 4", close a 12") |
| `swage_nipple` | 35 | sin schedule (Sunhy), todos con ATENCION |

Los de 5S/10S/40S/80S son **inoxidable** (CCTF no dice aleación; el catálogo es para inoxidable genérico). Los demás son acero al carbono.

## Hallazgos importantes (leer antes de usar)

1. **Los pesos Sch 40 (de 12" para arriba) y Sch 80 (de 10" para arriba) de Texas Flange / Weldbend no siguen el espesor de pared** en codos, tees, casquetes y curvas 180°. Ejemplo: codo 90 RL Sch 80 de 18": 157,8 kg, y el Sch 60 de Hackney Ladish (pared menor) pesa 224 kg. Con el espesor de pared, el peso de Sch 80 debería ser 1,8 veces el de STD y la tabla da 1,0 (se comparó tabla contra STD y contra el espesor de la propia tabla: la relación observada sobre la esperada baja de 0,84 en 10" a 0,41 en 24" en el codo 90 RL Sch 80). En las reducciones el peso sí crece con el espesor (24"×16" Sch 80 da 2,6 veces el XS de Wermac). **Esos renglones están marcados ATENCION** ("el peso no sigue el espesor de pared"). Es un error del catálogo, no de la carga. Para Sch 80 de codo 90 RL, codo 45 y curva 180° de 10" a 14" valen las filas `80` de Hackney Ladish (están en el mismo archivo, con su fuente).
2. **Tee recta Sch 40 de 3 1/2" a 12"** (Weldbend y Texas Flange): la tabla está **corrida una medida** (la tee de 10" Sch 40 da 56,5 lb, que es la de 8" STD; la de 12" da 90,9 lb contra 136 lb de STD). Marcadas ATENCION: no usar. No se corrigió.
3. **Codos 3D (3R) 45° XS y 80** pesan menos que STD/40 en casi todas las medidas (de la propia fuente). **Curvas 180° RL Sch 160 y XXS** pesan menos que XS. Marcados ATENCION.
4. **Cruces B16.9 de CCTF**: la cruz pesa menos que la tee de la misma tabla desde 2 1/2" (una cruz tiene una boca más). 28 de los 34 renglones llevan ATENCION (los de 1 1/4" a 2" no).
5. **Diferencias entre fuentes** donde hay dos para el mismo renglón (por ejemplo, stub end STD/XS Hackney Ladish contra Texas Flange, o Sch 80 de codos 10"–14"): están las dos filas y la nota de cada una dice el otro valor y la diferencia en %. Los que ya existían en `accesorios_peso.csv` (Wermac/Hackney Ladish) también dicen la diferencia.
6. **Hackney Ladish sí cierra con el espesor**: se calculó el peso por (OD − T)·T relativo al STD del mismo tamaño para sus 45 renglones de codos/curvas, y coincide en promedio **1,1% (codo 90), 1,6% (codo 45) y 3,2% (curva 180°)**. Es la fuente a preferir para Sch 30, 60, 80, 100 y 120 donde existe.
7. Tipeos de la fuente en inoxidable marcados: codo 90 RL 2 1/2" 10S (0,8 lb contra 1,8 lb en la fila en kg), reducciones 3"×2" 10S y 2"×1 1/4" 80S. La reducción 3/4"×1/2" 10S no se cargó (peso ilegible en el catálogo: "/16"; los otros 3 schedules de esa fila sí).
8. Smith-Cooper/Bonney: tipeos puntuales marcados (por ejemplo, hex bushing 1 1/4"×1/8" con 0,8 lb contra 0,3 lb de sus vecinos, unión 6000 SW 1 1/4" 6,5 lb).

## Lo que NO se consiguió

- **Tee 8" Sch 60 y tee de reducción 12"×8" XS×Sch 60 (COT26-0330-001): no existen en ninguna tabla pública consultada.** Ningún fabricante publica Sch 10, 20, 60, 100, 120 ni 140 para tees, reducciones, casquetes ni stub ends; Hackney Ladish da esos schedules solo para codos 90, 45 y curvas 180° (arriba). Para esa cotización hay que pedir el peso a un proveedor (o aceptar una estimación):
  - *Estimación, no es dato de fuente y no está en el CSV*: tee 8" Sch 60 (pared 0,406") ≈ **29 a 32 kg** (64 a 71 lb): interpolando por espesor entre STD y XS (24,95 y 34,02 kg de Wermac; 25,6 y 34,6 kg de Weldbend) da 29 a 30 kg; escalando el STD por (OD − T)·T o con el factor 1,25 de Aalco para Sch 60 a 8" da 32 kg. Margen ±10%.
  - Tee de reducción 12"×8" XS×Sch 60: ≈ **75 a 79 kg** (la tabla XS×XS es 79,4 kg, la rama Sch 60 es un poco más liviana). Margen ±8%.
- **Sch 10, 20 y 30**: solo Sch 30 de codos/curvas de 8" y 10" (Hackney Ladish). **Sch 60**: 18", 20" y 24" (codos/curvas). **Sch 100**: 12". **Sch 120**: 4" a 14". **Sch 140**: nada.
- **Clase 9000 NPT: no existe** en ASME B16.11 (roscados 2000, 3000 y 6000; socket weld 3000, 6000 y 9000). Está cargado el 9000 SW de cruz e insertos.
- **Swage nipples**: solo la tabla de Sunhy (baja confiabilidad). No apareció un catálogo con pesos por schedule (J.B. Smith/ASC y MSS SP-95 no publican los pesos en texto).
- **Stub end corto de carbono**: solo inoxidable (CCTF 10S/40S). Los de carbono de Texas Flange/Weldbend/Hackney Ladish son el largo de B16.9.
- **Cruces de reducción**, uniones SP-83 de 4" y mayores, forjados de inoxidable y niples de Sch 160/XXS: sin dato. Los Rockwood de Bonney (uniones 601/602/604) no se cargaron.
- **Codo 90 reductor (RL)**: solo Sch STD, XS, 40 y 80 (Texas Flange). Sin control de espesor para tees de reducción ni reducciones 40/80 (solo se verificó la coherencia entre schedules; ver abajo).
- Los 1955 de Hackney Ladish (forjados, flanges, etc.) no se cargaron; el catálogo completo está en https://www.hackneyladish.com/Catalog.aspx.

## Cómo estimar lo que falta (para decidir, no cargado)

Aalco publica factores "peso del schedule X = factor × peso de 40S/STD del mismo NPS" (tabla guardada en `fuentes_originales/tablas_pesos/aalco_stainless_buttweld_fittings_factores_por_schedule.pdf`; por ejemplo, 8": Sch 60 1,25, Sch 100 1,78, Sch 120 2,13, Sch 140 2,37). Coincide con el cálculo por espesor (OD − T)·T que reproduce a Hackney Ladish con 1–3% en codos y curvas. En tees el escalado sobrestima (la tee de la tabla XS pesa 0,94 de lo que predice el espesor). Si Matías lo aprueba, se puede agregar como columna "estimado por factor", siempre rotulado como estimado.

## Verificación (28-10-2026)

- **Relectura de 20 valores al azar** (semilla fija, repartidos entre las 8 fuentes) contra la fuente por un camino distinto al de la carga (texto de los PDF de Texas Flange en vez del HTML; texto del PDF de CCTF; imagen del escaneo de Hackney Ladish; coordenadas del PDF de Bonney): **20 de 20 coinciden**. Muestra: reducción 20"×10" Sch 40 = 205 lb; codo 45 1" Sch 160 = 3 lb; casquete 1 1/4" Sch 80 = 0,48 lb; tee de reducción 48"×36" XS = 2.127 lb; tee 18" Sch 80 = 360 lb; reducción 10"×4" XXS = 52 lb; codo 45 1 1/2" 5S = 0,28 lb; tee 6×6×5 10S = 17 lb; stub end 1" 40S ANSI = 0,65 lb; tee 1" 10S = 0,6 lb; stub end 5" STD = 11,75 lb (Ladish); curva 180° 14" Sch 120 = 850 lb; codo 90 24" Sch 60 = 1.188 lb; cruz 4" STD = 9,25 lb; cupla reductora 2 1/2"×1 1/4" 3000 = 4,5 lb; cupla reductora 2"×1 1/2" 3000 = 3,9 lb; cruz 3/4" 9000 SW = 4,12 lb; inserto 2"×1" 6000 = 1,86 lb; niple 2" Sch 40 de 10" = 2,89 lb; swage 1 1/2"×3/4" = 0,70 kg.
- **Hackney Ladish**: los 85 renglones transcriptos (45 de codos y curvas, 40 de stub ends) se cotejaron contra un OCR del escaneo: coinciden todos (los 5 que no matchean por texto son pesos que el escaneo imprime sin el cero, como ".24" o ".34", y se confirmaron en la imagen).
- **Coherencia** (el peso crece con el schedule y con la medida): se controló contra el orden 10, 20, 30, STD, 40, 60, XS, 80, 100, 120, 140, 160, XXS (misma fuente tolerancia 3%; entre fuentes 10%; las equivalencias STD=40 hasta 10" y XS=80 hasta 8" con 5% y 15%), con la medida en cada tabla, con la clase en forjados (2000<3000<6000<9000), con el largo en niples y 5S<10S<40S<80S en inoxidable. Más el control por espesor de pared descripto arriba. Resultado: **447 de 2.893 renglones con ATENCION** (codos 180° RL 76, codos 3D 45° 62, codos 45° 37, cruces 37, swage 35, reducciones 29, codos 180° RC 27, codos 90 RC 26, tees rectas 25, codo 90 RL 21, casquetes 20, resto menos de 16 por tipo).
- Formato: 10 columnas en todos los renglones, `dn2 ≤ dn`, sin renglones repetidos de la misma fuente, ningún peso vacío o cero.

## Uso y márgenes

Estimar siempre como estimado, igual que `pesos_LEEME.md`: carbono B16.9 ±10% en codos, ±15% en tees, reducciones y casquetes; forjados ±25%; **no usar** los renglones con ATENCION sin confirmar, en particular Sch 40 y 80 grandes de codos, tees y casquetes de Texas Flange/Weldbend. Para Sch 40 y 80 de más de 8" y 10" respectivamente, mejor Hackney Ladish (codos y curvas) o el peso por espesor de pared.
