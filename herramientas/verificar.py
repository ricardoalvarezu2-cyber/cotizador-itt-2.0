"""Verifica que las herramientas de lectura del Cotizador ITT estén instaladas y funcionen."""
import importlib.metadata as md

for paquete in ["pymupdf", "ezdxf", "ezdwg", "docling", "openpyxl"]:
    try:
        print(f"OK  {paquete} {md.version(paquete)}")
    except md.PackageNotFoundError:
        print(f"FALTA  {paquete}")

# Docling necesita descargar sus modelos desde huggingface.co la primera vez
try:
    from huggingface_hub import model_info
    model_info("docling-project/docling-layout-heron")
    print("OK  acceso a modelos de Docling")
except Exception as e:
    print(f"SIN ACCESO a modelos de Docling ({type(e).__name__}): habilitar huggingface.co en la red")
