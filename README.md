# Cotizador ITT

Herramienta de cotización asistida por IA para ITT S.A.: lee pedidos de clientes (mails, planos PDF/DWG, especificaciones), arma el cómputo de materiales y calcula costo y plazo.

## Estado

| Parte | Estado |
|---|---|
| Base de conocimiento ([`conocimiento/`](conocimiento/README.md)) | ✅ Reglas de cálculo, tarifas, plazos, precios, codificación, historial comercial y 93 cotizaciones de 2026 analizadas |
| Lectura de documentos (PDF, DWG/DXF, Excel, Word, mails) | ✅ Herramientas instaladas y probadas |
| Bibliotecario, agentes de cómputo, motor de costo y plazo, herramienta comercial | ⏳ Próximo paso |

## Estructura prevista

- **Bibliotecario:** registra cada pedido (`COT[AA]-[código cliente]-[NNN] Rev X`), clasifica documentos y guarda resultados, incluido el resultado final de cada oferta.
- **Coordinador + subagentes de extracción:** leen planos y especificaciones y devuelven el cómputo en un formato fijo.
- **Motor de costo y plazo:** cálculo determinístico con las reglas y tarifas de la base, sin IA.
- **Herramienta comercial:** factores de rentabilidad, caución, transporte, márgenes y escenarios.

## Herramientas

| Script | Uso |
|---|---|
| `herramientas/construir_base.py` | Regenera la base de conocimiento desde las planillas fuente (`fuentes_originales/`, que no se sube al repositorio) |
| `herramientas/extraer_texto.py` | Extrae el texto de una carpeta de documentos (PDF, Word, Excel, mails) |
| `herramientas/ficha_cotizacion_instrucciones.md` | Instrucciones para que un agente analice una carpeta de cotización y arme su ficha |
| `herramientas/consolidar_fichas.py` | Une las fichas en tablas de la base de conocimiento |
| `herramientas/indice_precios.py` | Arma el índice único de precios |
| `herramientas/leer_dwg.py` | Lee un plano DWG/DXF: textos por capa e imágenes por zona |
| `herramientas/verificar.py` | Comprueba que las herramientas de lectura estén instaladas |

Librerías de lectura: PyMuPDF (PDF y OCR), Docling (pliegos y tablas; descarga modelos de huggingface.co), ezdxf y ezdwg (CAD), openpyxl y xlrd (Excel), python-docx y extract-msg (Word y mails).

## Instalación

```bash
./setup.sh
source .venv/bin/activate
python herramientas/verificar.py
```
