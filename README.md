# Cotizador ITT

Herramienta de cotización asistida por IA para ITT S.A.: lee pedidos de clientes (mails, planos PDF/DWG, especificaciones), arma el cómputo de materiales y calcula costo y plazo.

## Estado

| Parte | Estado |
|---|---|
| Base de conocimiento ([`conocimiento/`](conocimiento/README.md)) | ✅ Reglas de cálculo, tarifas, plazos, precios, codificación, historial comercial y 93 cotizaciones de 2026 analizadas |
| Lectura de documentos (PDF, DWG/DXF, Excel, Word, mails) | ✅ Herramientas instaladas y probadas |
| Proceso de cotización completo: carpeta por cotización, `cotizacion.json`, motor de costo con ajuste por inflación, planilla, informe interactivo, oferta técnica y económica con formato ITT y controles automáticos | ✅ Probado con la COT26-1003-001 (CAPEX OQ8209). Guía: [`conocimiento/guia_cotizacion.md`](conocimiento/guia_cotizacion.md) |
| Registro de cotizaciones y resultados | ✅ [`cotizaciones/README.md`](cotizaciones/README.md) |
| Agentes de extracción automática de planos (lectura de la tabla del plano y del P&ID) | ⏳ Próximo paso. Hoy la tabla se transcribe con ayuda de Claude |

## Cómo se cotiza

Paso a paso en [`conocimiento/guia_cotizacion.md`](conocimiento/guia_cotizacion.md). Las reglas obligatorias están en [`conocimiento/procedimiento_cotizacion.md`](conocimiento/procedimiento_cotizacion.md) y Claude las sigue con el skill `cotizar`.

```
cotizaciones/COTAA-CCCC-NNN_<CLIENTE>_<PEDIDO>/
  pedido/                          originales del cliente + lista_materiales_plano.csv
  cotizacion.json                  ÚNICA fuente: ítems con todas sus fuentes de precio, parámetros y textos
  oferta.json                      textos de la oferta técnica y económica
  bitacora.md                      qué se hizo y por qué
  ── generado por herramientas/armar_cotizacion.py ──
  computo.csv · <codigo>.xlsx · informe.html · oferta/*.docx|pdf
```

Correspondencia con la estructura prevista:
- **Bibliotecario:** carpeta por cotización y registro en `cotizaciones/README.md`.
- **Extracción:** hoy Claude transcribe la tabla del plano. Queda pendiente automatizarla con subagentes.
- **Motor de costo y plazo:** `armar_cotizacion.py`, determinístico, con ajuste por inflación.
- **Herramienta comercial:** factores, contingencia, flete y escenarios en la planilla y en el informe.

## Herramientas

| Script | Uso |
|---|---|
| `herramientas/construir_base.py` | Regenera la base de conocimiento desde las planillas fuente (`fuentes_originales/`, que no se sube al repositorio) |
| `herramientas/extraer_texto.py` | Extrae el texto de una carpeta de documentos (PDF, Word, Excel, mails) |
| `herramientas/ficha_cotizacion_instrucciones.md` | Instrucciones para que un agente analice una carpeta de cotización y arme su ficha |
| `herramientas/consolidar_fichas.py` | Une las fichas en tablas de la base de conocimiento |
| `herramientas/indice_precios.py` | Arma el índice único de precios |
| `herramientas/leer_dwg.py` | Lee un plano DWG/DXF: textos por capa e imágenes por zona |
| `herramientas/armar_cotizacion.py` | **Arma una cotización completa** desde `cotizacion.json`: cómputo, planilla con fórmulas, informe interactivo y ofertas. Compara el cálculo en Python con la planilla y corre los controles |
| `herramientas/indices_inflacion.py` | Arma la tabla mensual de índices para el ajuste por inflación (`conocimiento/costos/indices_ajuste.csv`) |
| `herramientas/generar_oferta.py` | Genera la oferta técnica y la económica (Word y PDF) con el formato de ITT, desde `oferta.json` de la cotización y los precios de su planilla. Lleva la marca "BORRADOR – NO ENVIAR" hasta que la cotización esté aprobada |
| `herramientas/verificar_computo.py` | Control obligatorio de una cotización: cómputo contra la tabla del plano (posiciones, cantidades, extremos y soldaduras, fuentes y antigüedad de precios, estimados) |
| `herramientas/verificar.py` | Comprueba que las herramientas de lectura estén instaladas |

Librerías de lectura: PyMuPDF (PDF y OCR), Docling (pliegos y tablas; descarga modelos de huggingface.co), ezdxf y ezdwg (CAD), openpyxl y xlrd (Excel), python-docx y extract-msg (Word y mails).

## Instalación

```bash
./setup.sh
source .venv/bin/activate
python herramientas/verificar.py
```
