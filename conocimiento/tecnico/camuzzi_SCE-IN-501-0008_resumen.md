# Camuzzi — válvulas esféricas (SCE-IN-501-0008 Rev. 0)

- **Fuente:** "Informe técnico de válvulas – Listados Camuzzi", 06-11-2026, de Matías Russo (PDF de 10 páginas). Original y texto completo en `fuentes_originales/camuzzi_ET/2026-11-06_Informe_tecnico_valvulas_listados_Camuzzi.*`.
- El informe se basa en la especificación Camuzzi **SCE-IN-501-0008 Rev. 0** (vigente desde 10-11-2014), tomada de una copia de Scribd (no oficial: el sitio de Camuzzi ya no la publica, ver `camuzzi_ET_LEEME.md`), y en los tres listados de materiales del concurso CP 24578.
- **Estado:** fuente secundaria. La especificación original no está en el repositorio: hay que bajarla de la web de Camuzzi (lo pide la ET SCE-ME-515-0030, requisito R56 de la COT26-0135-002) y verificar cada punto contra ella antes de usarlo en una oferta.
- **Alcance:** solo las válvulas **esféricas**. Las reguladoras, monitoras, alivios, bloqueos y válvulas de instrumentación se rigen por otras especificaciones de Camuzzi o por el fabricante.

## A qué cotización corresponde cada listado

| Listado del informe | Cotización | Válvulas |
|---|---|---|
| 1 — planta de regulación | COT26-0135-001 (skid de regulación) | ítems 1, 2, 3, 4, 14, 16, 19 y sensor A (coinciden con `lista_materiales_plano.csv`) |
| 2 — estación con filtro FM-06 y carretel de turbina | COT26-0135-002 (puente de medición) | ítems 3, 4, 12 y 16 (coinciden) |
| 3 — válvulas del filtro (ítems 20, 21, 22, 26/27, 30, 31, 33) | Filtro FM-06 #150 del puente (ítem 1 de la 002), a confirmar | No coincide con la lista del separador COT26-0135-003 (que es de ITT): no aplicarle estos ítems |

## Normas base de las esféricas
Diseño ASME B16.34; fabricación API 6D (última edición); bridas ASME B16.5 (MSS SP44 en 22" y desde 26"); biseles ASME B16.25; fuego API 607; soldadura ASME IX; cálculo ASME VIII Div. 1. Ante conflicto, prevalece la especificación de Camuzzi. Servicio: gas natural (densidad relativa 0,6) o propano-butano líquido; temperatura según API 6D.

## Requisitos por tipo (punto de la especificación entre paréntesis)

| Requisito | Esfera flotante | Trunnion |
|---|---|---|
| Cuándo (6.3.1) | Hasta 4" inclusive en serie 150; por debajo de 2" en 150, 300 y 600 | Obligatoria más de 4" en serie 150 |
| Asientos (6.3.2 a 6.3.5) | Teflón (PTFE) | Inoxidable, más blandos que la esfera, inserto PTFE o Vitón fijado, resortes inox; sellan aun con el inserto gastado |
| Doble bloqueo y purga (6.3.4) | No exigido | Obligatorio |
| Ejes y bujes (6.3.1) | — | Eje inferior ≥ superior; bujes autolubricados tipo DU dimensionados al empuje a máxima ΔP |
| Pasaje (6.3.1) | Paso total (PT): pasaje constante en esfera y cuerpo (scraper y hot tap); no se exige constante por debajo de 3" | Ídem |

Comunes a todas:
- **Esfera (6.2):** inoxidable, o AC / fundición con cromo duro (≥ 35 µm, ≥ 600 HV) o níquel químico (≥ 35 µm, 450–540 HV). **Hasta 2": solo inoxidable.**
- **Vástago (6.2):** inoxidable, o AC con cromo duro o níquel químico (mismos valores).
- **Cuerpo (6.2):** AC totalmente calmado, API 6D punto 8, CE ≤ 0,50 %. Fundido: WCB.
- **Bulonería (6.2):** espárragos A193 B7, tuercas A194 2H, rosca B1.1.
- **Espesores (6.3.6, 6.3.11):** ≥ tabla 3 de B16.34; cuerpo abulonado: bridas intermedias ≥ 80 % de B16.5.
- **Largo entre caras (6.3.12):** según API 6D (verificar con el plano del skid).
- **Extremos (5, 6.3.13):** bridados B16.5; cara igual a la de las bridas WN de la línea.
- **Venteo, drenaje y sellador (6.3.8):** solo en serie 300 de más de 8" y en 600 desde 4".
- **Accionamiento (6.4.1, 6.4.2):** palanca incluida hasta 6" inclusive, cierre horario; fuerza ≤ 345 N a máxima ΔP (si no cumple, reductor con aceptación de Camuzzi).
- **Fuego y antiestático (6.3.17, 6.3.18):** API 607 y dispositivo antiestático. **Topes e indicador** abierto/cerrado (6.3.15).
- **Cáncamos y soportes (6.3.21, 6.3.22):** desde 8".

## Inspección y ensayos (8.1)
- END de extremos: RX si es fundida (150 mm desde cada extremo para soldar, B16.34), partículas magnéticas si es forjada, ultrasonido si es de planchuela.
- Vástagos con tintas penetrantes o partículas; biseles con partículas después del mecanizado.
- Soldaduras a presión radiografiadas (eficiencia 0,8); soldadores y procedimientos ASME IX.
- Hidrostática de cuerpo (API 6D 11.3) sin grasa ni sellador, con drenaje, venteo y líneas de sellado; de asientos (11.4) y neumática (Anexo B, B.3.3 Type II): burbuja cero, sin sellador.
- Torque operacional (API 6D B.6) a máxima ΔP: ≤ 345 N.
- Camuzzi puede pedir sin cargo metalografía de probetas.

## Prototipos (8.2), si el modelo es nuevo para Camuzzi
500 maniobras a temperatura ambiente y 100 a 121 °C y a −29 °C; par de maniobra a 50 °C y −20 °C; flexión del órgano de maniobra con 200 N·m sin fugas; prueba de mantenimiento; planos e ingeniería certificados, o licencia certificada por escribano.

## Fabricante, marcado, pintura, entrega, documentación y garantía
- **Fabricante (9):** aprobado previamente por Camuzzi.
- **Marcado (11):** fabricante, N° de OC de Camuzzi, modelo, lote y serie, presión máxima, diámetro, PT o PR, sentido de flujo; inalterable (placa soldada, troquelado o fundido).
- **Pintura (12):** SCE-PC-511-0003, última revisión.
- **Entrega (13):** extremos protegidos (nunca cartón), válvula abierta, superficies mecanizadas engrasadas, termocontraíble ≥ 500 µm sobre toda la válvula, pallet con sunchos metálicos apto para camión e intemperie.
- **Documentación por lote (14):** certificado de materiales (DIN 50049 2.2 o equivalente) con análisis químico y propiedades; ensayos (hidráulico, neumático y torque); antifuego API 607; niquelado o cromado; aprobación de Camuzzi; seguimiento de calidad; resistencia y hermeticidad; pintura; manual de uso y mantenimiento; plano de despiece con repuestos; manual de montaje; especificación de la grasa.
- **Garantía (15):** 12 meses desde la instalación o 24 desde el despacho, lo primero; se extiende 12 meses desde cada intervención. **Repuestos (16):** la oferta incluye lista valorizada para 1 año.

## Puntos a confirmar con Camuzzi (del informe)
1. Fabricantes cotizados aprobados por Camuzzi (esféricas y reguladores).
2. Esférica 6" PT (002, ítem 3): si con palanca supera 345 N, aceptación de reductor.
3. Cara de brida (RF) de todas las esféricas bridadas.
4. Si las esféricas de 1/2" clase 3000 roscadas (cuplas) deben cumplir la SCE-IN-501-0008.
5. Material de las cuplas de los ítems 14 y 16: el listado dice A-106; lo habitual es A-105.
6. Listado 3: clase del filtro (serie "A"), extremos de la esférica de 1" y cantidades.
7. Especificación de Camuzzi para la monitora y la reguladora de 3", con presiones y caudal.
8. Presiones de apertura de los alivios S-70 y S-71 y rangos de salida de las reguladoras 1301F y 67FR.
9. Si algún modelo es nuevo para Camuzzi (ensayos de prototipo).

Regla de descripción: estos requisitos no cambian el texto del cliente en el cómputo; lo que agrega ITT va en la columna `nota` (regla crítica de CLAUDE.md).
