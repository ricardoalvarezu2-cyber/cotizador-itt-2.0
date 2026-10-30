# Consultas al cliente — COT26-0135-002 (Camuzzi, CP 24578 ítem 3, puente de medición)

**BORRADOR — no se envía nada al cliente desde el cotizador.** Las manda Matías por el portal (PDC), hasta 2 días hábiles antes del cierre (CGP art. 7). Mientras no tengan respuesta quedan como `consulta` en `pedido/requisitos.csv` y frenan las ofertas.

Redactadas el 30-10-2026.

---

**Ref.: Concurso de precios N° 24578 – ítem 3: Skid puente de medición, plano SCE-ME-315-039 y especificación técnica SCE-ME-515-0030 (ERP Parque Industrial Tres Arroyos)**

**C1. Manómetros de presión estática (ET §5.7 y §5.8).** La especificación describe manómetros de presión estática de 4" con manifold de tres vías y sus accesorios en acero inoxidable doble virola, y el plano los nombra en los documentos de referencia (SCE-PR-506-1000 y SCE-PR-106-1000), pero la tabla del plano no los lista. ¿Hay que proveerlos en el puente? En ese caso, ¿cuántos, con qué rango y en qué tomas (por ejemplo, las cuplas con válvula esférica de 1/2" de la pos. 16)?

**C2. Pos. A – "TEMPERATURA PARA CORRECTORA DE CAUDAL" (3/4", 0-100 °C / 4-20 mA).** ¿Se trata de un transmisor de temperatura 4-20 mA o de la sonda que acompaña a la unidad correctora? ¿Lo provee Camuzzi junto con la correctora? Si lo provee ITT, ¿hay marca o modelo preferido (la correctora a utilizar es Itron, Dresser, Instromet u otra)?

**C3. Pos. 16 – "CUPLA DE AC SOLD. 1/2" NPT C/ VLV. ESF 1/2" S3000", material ASTM A-106.** ASTM A-106 es una especificación de caño. ¿Se acepta la cupla forjada en ASTM A-105 serie 3000 (ASME B16.11), como la pos. 12, o se requiere un niple/cupla fabricado de caño A-106 Gr B?

**C4. Pos. 7 y 8 – "TE NORMAL" 6" y 4" STD, material ASTM A-105.** Las tes para soldar a tope (ASME B16.9) se fabrican en ASTM A-234 WPB, como el codo de la pos. 10. ¿Se aceptan tes A-234 WPB, o se requieren tes forjadas en A-105?

---

Respuestas: anotarlas acá con la fecha y el número de circular, pasar el destino del requisito en `pedido/requisitos.csv` a `cumple`, `renglon`, `desvio` o `exclusion`, y ajustar `armar_json.py`.
