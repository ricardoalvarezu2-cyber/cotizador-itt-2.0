# Cotizador ITT

Herramienta de cotización asistida por IA para ITT S.A.: lee pedidos de clientes (mails, planos PDF/DWG, especificaciones), arma el cómputo de materiales y calcula costo y plazo.

## Estructura prevista

- **Bibliotecario:** registra cada pedido (`COT-[CLIENTE]-[AÑO]-[NÚMERO] Rev X`), clasifica documentos y guarda resultados.
- **Coordinador + subagentes de extracción:** leen planos y especificaciones y devuelven el cómputo en un formato fijo.
- **Motor de costo y plazo:** cálculo determinístico (planilla), sin IA.
- **Herramienta comercial:** factores de rentabilidad, caución, transporte, márgenes.

## Herramientas de lectura

| Herramienta | Uso |
|---|---|
| PyMuPDF | Texto, imágenes y OCR de PDF |
| Docling | Pliegos y especificaciones: texto y tablas (descarga modelos de huggingface.co) |
| ezdxf | Lectura y render de DXF |
| ezdwg | Lectura de DWG sin conversor externo |
| openpyxl | Planillas Excel |

## Instalación

```bash
./setup.sh
source .venv/bin/activate
python herramientas/verificar.py
```
