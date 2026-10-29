# Pesos y superficies de materiales de estructura

Tablas de **kg/m** (o kg/m²) y **m²/m** de perfiles, ángulos, planchuelas, barras, tubos y chapas para calcular kg de un equipo (flete, galvanizado, fabricación por kg) y m² a pintar. Armadas el 28-10-2026 desde catálogos públicos, priorizando lo que se compra en Argentina (INTI-CIRSOC/IRAM, Acindar, Ferrara, Ternium). **Estado: borrador, sin revisar por Matías.** Cada renglón lleva `fuente_url`, `fuente_nombre` y `consultado` (2026-10-28). Nada está inventado ni extrapolado: lo calculado dice la fórmula en `nota`.

## Archivos

| Archivo | Renglones | Contenido |
|---|---|---|
| `estructura_perfiles_laminados.csv` | 515 | IPN, IPE (y variantes A/O/AA), HEA, HEB, HEM, HEAA, HE (otras), UPN (con los "U chicos"), UPE |
| `estructura_angulos.csv` | 394 | Ángulos de alas iguales (310) y desiguales (84) |
| `estructura_planchuelas.csv` | 657 | Planchuelas ancho × espesor (pulgada y mm) |
| `estructura_barras.csv` | 202 | Redondos (126) y cuadrados (76) macizos |
| `estructura_perfiles_chapa.csv` | 108 | Perfiles C (67) y U (41) de chapa plegada, laminados en caliente (LAC) y galvanizados |
| `estructura_tubos.csv` | 1.154 | Tubos redondos (311), cuadrados (296) y rectangulares (547) |
| `estructura_chapas.csv` | 163 | Chapa lisa (60), semilla de melón (14), estampada (8), xadrez (5), metal desplegado (76) |
| `estructura_inox_densidad.csv` | 85 | Densidad de aceros inoxidables por grado |

Los CSV usan coma, punto decimal y fin de línea CRLF (igual que el resto de `conocimiento/tecnico/`). `perfiles.csv` **no se tocó** salvo las cuatro filas UL (ver más abajo).

## Cómo leer las columnas

- `kg_por_m` / `kg_por_m2`: valor a usar. En angulos, perfiles y tubos es **el valor publicado por la fuente**. En **planchuelas y barras es calculado** (`tipo_dato = calculado`): sección × 7.850 kg/m³, porque así sale exacto con las medidas comerciales; el valor que publica la fuente queda en `kg_por_m_fuente` para comparar. En chapa lisa también: `kg_por_m2 = espesor_mm × 7,85`.
- `kg_por_m_calc` (angulos, tubos, perfiles de chapa): control con fórmula (ángulo `(a+b−e)·e·7,85/1000`; tubo redondo `π(D−e)e·7,85/1000`; cuadrado/rectangular con radio exterior 2e; perfil de chapa `sección·7,85/1000`). Sirve para detectar errores de la fuente, **no** para reemplazarla.
- `m2_por_m` con `m2_origen`: `fuente` (la tabla lo da) o `calculado` (la nota dice cómo: perímetro del ángulo `2(a+b)/1000`, redondo `π·D/1000`, cuadrado `4a/1000`, planchuela `2(ancho+espesor)/1000`, perfil de chapa `2·sección/espesor`, tubo = perímetro exterior). Es la **superficie exterior por metro**; si se pinta adentro del tubo o por las dos caras del perfil de chapa, hay que contarlo aparte (el de chapa ya viene por las dos caras).
- `ATENCION` al principio de una frase de `nota` = el renglón tiene un problema detectado (error de la fuente, valor que no crece con el espesor, etc.). Hay 26 renglones así; no usarlos sin mirar la nota.
- Fechas internas AAAA-MM-DD (se muestran DD-MM-AAAA con `numeros.a_vista`).

## Fuentes (todas guardadas en `fuentes_originales/tablas_pesos/`)

Argentinas (preferir estas):
1. **INTI-CIRSOC, "Tablas de perfiles laminados y tubos estructurales para CIRSOC 301/302"** (Troglia, Troglia, Godoy, julio 2005; normas IRAM-IAS U 500-511, 215-2/3/4/5, 509, 558, 218/2592). IPN, IPB (=HEB), IPBl (=HEA), IPBv (=HEM), IPE, UPN (con los de 30x15 a 65), ángulos de alas iguales en pulgada y **todos** los tubos redondo, cuadrado y rectangular con `g` (kg/m) y `p` (m²/m). https://www.inti.gob.ar/assets/uploads/files/cirsoc/EJEMPLOS%202/EJEMPLOS%202.2/tapa_portada.pdf
2. **Acindar, "Tablas y Equivalencias" (enero 2007)**, fabricante: ángulos, UPN, IPN, HEB, IPE, U chicos, barras cuadradas y redondas, planchuelas. Es la copia del PDF en arquitectogustavo.com.ar (acindar.com.ar es una página que no carga sin navegador). https://www.arquitectogustavo.com.ar/Archs/ACINDAR-libroamarillo.pdf
3. **Ferrara S.A. (perfiles.com.ar), catálogo de productos** (distribuidor/fabricante de San Fernando y Benavidez, con normas IRAM): tubos estructurales cuadrados/rectangulares por espesor comercial (hasta 250x100 y 175x175), ángulos, barras, planchuelas, UPN, IPN, HEB ("Grey"), U chicos, **perfiles C y U de chapa (galvanizado y LAC)**, chapas lisas, **semilla de melón**, estampada y metal desplegado. https://www.perfiles.com.ar/wp-content/uploads/2020/09/LP-COMPLETO.pdf
4. **Ternium Argentina, "Tubos y Perfiles" (2018)**: tubos para uso general y estructural, tubos de uso mecánico y perfiles C y U (LAC y galvanizado). https://ar.ternium.com/media/dqle541j/2996_1_tubos-y-perfiles_ok.pdf
5. **Aceros Norte**, "Pesos y medida chapa semilla de melón" (peso aproximado por hoja). https://acerosnorte.com.ar/wp-content/uploads/2026/03/PESOS-Y-MEDIDA-CHAPA-SEMILLA-DE-MELON.pdf
6. **Distriplac** (distribuidor argentino), 3 fichas Mallexpan de malla romboidal.

Internacionales / de apoyo:
7. **ArcelorMittal Sections and Merchant Bars V2026-1** (planilla `.xlsx` y catálogo `.pdf`): IPE, HE (A/B/M/AA/…), UPN, UPE y ángulos pesados (EN 10365 / EN 10056), con `AL` (m²/m) oficial. https://sections.arcelormittal.com/repo/Sections/Sections%20and%20Merchant%20Bars-ArcelorMittal_V2026-1.xlsx
8. **Stahlwerk Thüringen**, hoja UPE 120-400 (EN 10365:2017), como segunda fuente de UPE: https://stahlwerk-thueringen.de/files/14426C6B9D9
9. **Wermac.org** (tablas EN 10025 / 10056): ángulos métricos chicos, planchuelas y barras métricas. **Secundaria**: sus pesos están ~1,9 % arriba del cálculo con 7.850 (parece usar 8.000 kg/m³), y en ángulos 1,9 a 3,7 % arriba. Por eso en planchuelas/barras se usa el cálculo y en ángulos queda como "límite superior". Solo se usó donde no hay otra fuente.
10. **Fábrica do Projeto** (Brasil): ángulos y barras en pulgada, planchuelas en pulgada, chapa lisa por calibre, xadrez y metal desplegado. Secundaria, con errores de tipeo (marcados).
11. **Cedinox** (España, "Stainless steel: tables of technical properties"): densidad del inoxidable por grado. https://www.cedinox.es/export/sites/cedinox/.galleries/publicaciones-tecnicas/Tables_TechnicalProperties_EN.pdf

Cómo se armó todo: `fuentes_originales/tablas_pesos/scripts/build.py` (más `build_ar.py`, `common.py`, `ang_inti.py`). Se corre con `python -I fuentes_originales/tablas_pesos/scripts/build.py fuentes_originales/tablas_pesos conocimiento/tecnico` y regenera los 8 CSV desde los originales guardados.

## Las filas "UL" de perfiles.csv

`UL 40x20`, `UL 50x25`, `UL 50x38` y `UL 65x42` tenían `kg_por_m` = 20, 25, 38 y 42, que son los **anchos de ala** (b) y no el peso. Son los perfiles **UPN chicos** de la norma IRAM-IAS U 500-509 (en planilla ITT figuraban como "UL"; Ferrara y Acindar los venden como "U chicos"). Se corrigió el peso con fuente (tres fuentes coinciden):

| Fila | kg/m anterior | kg/m corregido | Fuentes |
|---|---|---|---|
| UL 40x20 | 20,0 | **2,87** | INTI-CIRSOC (UPN 40x20) 2,87; Acindar 2,87; Ferrara 2,9 |
| UL 50x25 | 25,0 | **3,86** | INTI-CIRSOC 3,86; Acindar 3,86; Ferrara 3,9 |
| UL 50x38 | 38,0 | **5,59** | INTI-CIRSOC (UPN 50) 5,59; ArcelorMittal 5,6; Ferrara 5,6 |
| UL 65x42 | 42,0 | **7,09** | INTI-CIRSOC (UPN 65) 7,09; ArcelorMittal 7,1; Acindar 7,09; Ferrara 7,1 |

El `m2_por_m` de esas filas (0,16 / 0,2 / 0,252 / 0,298) se dejó: es la misma fórmula simplificada `2h + 4b` que usa el resto de `perfiles.csv` (por ejemplo UPN 80 = 2·80 + 4·45 = 340 mm). Ojo: `perfiles.csv` lo regenera `herramientas/construir_base.py` desde la planilla vieja; si se vuelve a correr, las cuatro filas UL vuelven al error.

## Hallazgos sobre perfiles.csv (para decidir; no se cambió nada más)

1. **Las filas HEB son copia de las HEA** (kg y m² iguales: `HEB100 = 16,7 kg/m`, `HEB500 = 155 kg/m`). Los HEB reales pesan bastante más: HEB100 = **20,4**, HEB200 = **61,3**, HEB300 = **117**, HEB500 = **187** kg/m (INTI-CIRSOC, Acindar, ArcelorMittal y Ferrara coinciden; están en `estructura_perfiles_laminados.csv`). Si un cálculo usó `HEB…` de `perfiles.csv`, subestima entre 17 y 33 % los kg. Corregirlo en `perfiles.csv` queda para la sesión principal.
2. **`m2_por_m` de `perfiles.csv` es una aproximación** (UPN = 2h + 4b; IPE = 2h + 4b; HEA/HEB distinta) y da entre 3 y 9 % más que la superficie oficial `AL` de ArcelorMittal (UPN 80: 0,34 contra 0,312; IPE 100: 0,42 contra 0,400; IPE 500: 1,80 contra 1,744). Para pintura conviene la columna `m2_por_m` de `estructura_perfiles_laminados.csv` (filas ArcelorMittal).
3. IPN 120 figura 11,2 y IPN 360 figura 76,0; todas las fuentes dan 11,1 y 76,1. Diferencia de redondeo, sin importancia.

## Cobertura

- **Perfiles laminados**: IPN 80-600, IPE 80-600 (+ variantes A/O/AA y hasta 750), HEA/HEB/HEM 100-1000, UPN 30x15-400, UPE 80-400. Las series coinciden entre fuentes (146 designaciones con 2 o más fuentes: 143 dentro de 1,2 %; las 3 restantes son el IPE 100 de Acindar redondeado a 8,0 y el cruce de UPN 50/60 de Acindar, ver abajo). **UPE** no está en las fuentes argentinas: sale de ArcelorMittal y Stahlwerk Thüringen (coinciden en los 12 comunes).
- **Ángulos**: alas iguales de 12,7 a 300 mm (pulgada de 1/2" a 8" en INTI, Acindar, Ferrara y Fábrica do Projeto; métricos 16-200 en Wermac; pesados 80-300 en ArcelorMittal). **Desiguales**: de 30x20 a 250x100 (Wermac, ArcelorMittal 200x100). No hay desiguales en pulgada.
- **Planchuelas**: pulgada (1/2" a 6" de ancho × 1/8" a 1" de espesor) en Acindar, Ferrara y Fábrica do Projeto; métricas (hasta 500 × 50) en Wermac.
- **Barras**: redondos y cuadrados de 1/4" a 4" (Acindar, Ferrara, Fábrica do Projeto), métricos 6-200 (redondo) y 6-160 (cuadrado) en Wermac/ArcelorMittal. Las trefiladas de Ferrara no se cargaron (están en el PDF).
- **Perfiles C y U de chapa**: Ternium (C 80x40x15 a 240x80x25; U 80x40 a 200x80) y Ferrara (C 50x25x10 a 240x80x25; U 100x50 a 280x80). **Galvanizado y LAC** (`kg_por_m_galv`, `kg_por_m_lac`).
- **Tubos**: INTI-CIRSOC tiene la serie IRAM-IAS U 500-218 **completa** (redondos hasta 1.828,8 mm, cuadrados hasta 400, rectangulares hasta 250x100) con `m2/m` oficial; Ternium y Ferrara dan los espesores comerciales (0,8 a 6,35). Cuando una medida está en dos fuentes están las dos filas.
- **Chapas**: lisa de 0,30 a 12,5 mm calculada con 7,85 y verificada contra los pesos de hoja del catálogo Ferrara (45 espesores, 146 pesos de hoja, desvío máximo 0,0 %); 15 espesores más salen de la tabla brasilera de Fábrica do Projeto. Semilla de melón de 2,5 a 8 mm (Ferrara y Aceros Norte), 14 renglones por medida de hoja.
- **Inoxidable**: densidad por grado, 85 grados (304/304L/321 = 7.900; 316/316L/316Ti = 8.000; dúplex 2205 = 7.800; ferríticos 430 = 7.700 kg/m³). Para pesar inox: **kg = kg del acero al carbono × 1,006 (304) o × 1,019 (316)** (7.900/7.850 y 8.000/7.850).

## Cosas que hay que saber antes de usar

- **Tubos cuadrados y rectangulares comerciales (Ternium y Ferrara)**: el peso publicado es el del **tubo redondo de igual perímetro** ("familia" en pulgadas), no el área real. Da 3 a 18 % más que el cálculo real con radios, sobre todo en tubos chicos y finos (10x10 x 1,25: Ternium 0,353 contra 0,312 teórico). Es el peso por el que los venden. La serie INTI-CIRSOC sí es el área teórica (coincide con la fórmula entre −0,8 y +1,4 %). Para costear la compra de material, conviene Ternium/Ferrara; para la superficie o el peso real del tubo, INTI-CIRSOC.
- **Semilla de melón**: el peso por hoja de los distribuidores da 21 a 28 kg/m² para 2,5 y 3,2 mm, 40 a 41 para 4,75, 53 a 55 para 6,35 y 69 para 8 mm (de 7 % a 12 % más que la chapa lisa por el relieve). Las hojas del mismo espesor difieren hasta 4 % entre medidas (son pesos aproximados). La xadrez brasilera de Fábrica do Projeto (27 / 41 / 54 kg/m² para 3 / 4,75 / 6,3 mm) es otra chapa; no mezclar.
- **Acindar (2007)**: la tabla de U chicos tiene cruzados los pesos de 60x30 y 50x38 (5,59 y 5,07, al revés que INTI-CIRSOC y Ferrara); los dos renglones están marcados `ATENCION` y no hay que usarlos.
- **Errores de tipeo de las fuentes**, todos marcados con `ATENCION` en `nota`: Fábrica do Projeto (ángulo 3x1/2 con espesor 2,7; ángulo 5x7/16 con 23,52 kg/m en vez de ~21,3; redondo 2 1/16" con 116,92 kg/m; planchuelas 1x4" y 1x5" con ancho mal; metal desplegado EXP-5B con 28 kg/m²), Ferrara (tubo 120x120x3,2 con 10,814, que no crece con el espesor; redondo 2 3/8" con 20,7 kg/m; ángulo con dos renglones 38,1x6,35 y 38,1x6,4 con el mismo peso 3,4 (uno parece sobrar); C 50x25x10 y C 80x50x15 con sección que no cierra con el peso).
- **Metal desplegado de Fábrica do Projeto**: valores erráticos entre mallas parecidas; usar solo como orden de magnitud. Las fichas de Distriplac/Mallexpan (3 mallas livianas) y la tabla de Ferrara (15 mallas de 1,6 a 4,75 mm) son más confiables.
- **Largos y normas**: planchuelas y ángulos de 6 m (12 m desde 2 1/2" en ángulos); UPN/IPN 6 o 12 m; perfiles C/U de chapa 12 m; tubos 6 m (12 m desde 5 1/2"). Calidad F-24 (IRAM-IAS U 500-503), similar al ASTM A36.

## Huecos (no se consiguió)

- **Rejillas / grating (piso electrosoldado) y metal desplegado pesado de fabricante argentino**: no hay tabla pública en kg/m². Se encontraron solo referencias de comercios de EE.UU. (lb/pie²) y no se cargaron. Pedir ficha técnica al fabricante.
- **Ángulos desiguales en pulgada** y alas iguales de más de 8" fuera de ArcelorMittal.
- **UPE 80 y UPE 100**: solo ArcelorMittal (7,9 y 9,8 kg/m); ninguna fuente argentina.
- **Perfiles W / HP / M (norma ASTM)**: INTI-CIRSOC los tiene (páginas PDF 12-24) pero no se cargaron ni se controlaron los `W(H)`/`W(I)` de `perfiles.csv`. Tampoco el `HEM 320/305` especial, ni los perfiles T chicos, ni C/MC americanos.
- **Catálogo Acindar vigente, Gerdau Argentina, ArcelorMittal Brasil e IMCA**: el sitio de Acindar no carga sin navegador, el PDF de ArcelorMittal Brasil dio 404 y de Gerdau Argentina no se encontró un catálogo con tablas; lo de Acindar es del 2007.
- **Tubos redondos estructurales de Ferrara**: la tabla del catálogo no tiene texto extraíble (parece imagen); solo están los de uso mecánico tipo agua.
- **Galvanizado de ángulos, tubos y planchuelas**: ninguna tabla da el peso con zinc (en C/U de chapa sí, comparar `kg_por_m_galv` contra `kg_por_m_lac`).

## Verificación hecha (28-10-2026)

- **20 valores al azar releídos contra la fuente** (extrayendo de nuevo el texto o la celda del original guardado): ángulos (Wermac, Fábrica do Projeto, Acindar, ArcelorMittal), planchuelas (Fábrica do Projeto, Acindar, Ferrara), barras (Wermac, Fábrica do Projeto, Acindar), perfiles (INTI-CIRSOC HEA340 y HEB450, ArcelorMittal HEA900, IPE A 600 y HEM320), perfiles de chapa (Ternium C 100x45x10 y U 200x80, Ferrara C 50x25x10), tubos (INTI-CIRSOC redondo 1066,8x15,87 y cuadrado 40x40x2,5; Ternium 30x40x0,9), chapas (Ferrara lisa 1,6, Fábrica do Projeto EXP-68): **20 de 20 coinciden**.
- **Coherencia con las fórmulas**: tubos INTI-CIRSOC (352 renglones) entre −0,8 y +1,4 % contra el cálculo con radios; tubos redondos Ternium (108) entre −0,3 y 0,0 %; redondos Ferrara 35 entre −0,7 y 0,0 %; perfiles C/U Ternium (55) entre −0,1 y +0,2 % contra `sección × 7,85`; planchuelas Acindar (97) entre −1,1 y +1,1 % contra 7.850; barras Acindar (23) entre −1,0 y +0,4 %; chapa lisa Ferrara (45 espesores) exacta contra `7,85 × e`.
- **Ángulos contra `(2a−e)·e·7,85/1000`**: INTI-CIRSOC (47) −4,1 a +3,3 %; Acindar (33) −1,4 a +3,1 %; ArcelorMittal (76) −0,9 a +1,3 %; Wermac (157) +1,9 a +3,7 % (por eso es secundaria). Los desvíos de hasta 4 % en medidas chicas vienen de que la fórmula no cuenta los radios.
- **El peso crece con el espesor**: controlado para ángulos, tubos y perfiles de chapa (1 incumplimiento: ángulo Ferrara 38,1x6,4 duplicado, marcado).
- Pendiente: revisión independiente por Matías o por otro agente antes de usar en una cotización, y decidir si se corrige `perfiles.csv` (HEB y m²).
