"""Extrae el texto de una carpeta de documentos (PDF, Word, Excel, mails) a archivos .txt, uno por documento.

Uso: python herramientas/extraer_texto.py CARPETA_ORIGEN CARPETA_SALIDA

Genera en CARPETA_SALIDA:
  textos/<misma ruta>.txt   texto de cada documento
  indice.csv                ruta, tipo, tamaño, caracteres extraídos, páginas y si parece escaneado
"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

import docx
import extract_msg
import openpyxl
import pymupdf
import xlrd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from candado import perfil_soffice  # noqa: E402

MAX_CELDAS = 20000  # por hoja, para no generar textos gigantes con planillas de miles de filas vacías


def pdf(ruta: Path):
    with pymupdf.open(ruta) as d:
        texto = "\n".join(f"--- página {i + 1} ---\n{p.get_text()}" for i, p in enumerate(d))
        return texto, d.page_count


def word(ruta: Path):
    d = docx.Document(ruta)
    partes = [p.text for p in d.paragraphs if p.text.strip()]
    for t in d.tables:
        for fila in t.rows:
            celdas = []
            for c in fila.cells:
                if c.text.strip() and (not celdas or celdas[-1] != c.text.strip()):
                    celdas.append(c.text.strip())
            if celdas:
                partes.append(" | ".join(celdas))
    return "\n".join(partes), None


def word_viejo(ruta: Path):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", perfil_soffice(), "--headless", "--convert-to", "txt:Text", "--outdir", tmp, str(ruta)],
                       capture_output=True, timeout=120)
        salida = Path(tmp) / (ruta.stem + ".txt")
        return (salida.read_text(errors="replace") if salida.exists() else ""), None


def excel(ruta: Path):
    partes = []
    if ruta.suffix.lower() == ".xls":
        for hoja in xlrd.open_workbook(ruta).sheets():
            partes.append(f"=== hoja {hoja.name}")
            for r in range(min(hoja.nrows, 2000)):
                valores = [str(v).strip() for v in hoja.row_values(r) if str(v).strip()]
                if valores:
                    partes.append(" | ".join(valores))
    else:
        libro = openpyxl.load_workbook(ruta, data_only=True, read_only=True)
        for hoja in libro.worksheets:
            partes.append(f"=== hoja {hoja.title}")
            celdas = 0
            for fila in hoja.iter_rows(values_only=True):
                valores = [str(v).strip() for v in fila if v is not None and str(v).strip()]
                if valores:
                    partes.append(" | ".join(valores))
                    celdas += len(valores)
                    if celdas > MAX_CELDAS:
                        partes.append("... (hoja cortada)")
                        break
    return "\n".join(partes), None


def mail(ruta: Path):
    m = extract_msg.Message(str(ruta))
    try:
        adjuntos = ", ".join(a.longFilename or a.shortFilename or "" for a in m.attachments)
        texto = (f"Asunto: {m.subject}\nDe: {m.sender}\nFecha: {m.date}\nAdjuntos: {adjuntos}\n\n{m.body or ''}")
    finally:
        m.close()
    return texto, None


LECTORES = {".pdf": pdf, ".docx": word, ".doc": word_viejo, ".xlsx": excel, ".xlsm": excel, ".xls": excel,
            ".msg": mail}


def main():
    origen, salida = Path(sys.argv[1]), Path(sys.argv[2])
    (salida / "textos").mkdir(parents=True, exist_ok=True)
    filas = []
    archivos = sorted(p for p in origen.rglob("*") if p.is_file())
    for n, ruta in enumerate(archivos, 1):
        rel = ruta.relative_to(origen)
        lector = LECTORES.get(ruta.suffix.lower())
        texto, paginas, error = "", None, ""
        if lector:
            try:
                texto, paginas = lector(ruta)
            except Exception as e:  # archivo dañado o protegido: se registra y se sigue
                error = f"{type(e).__name__}: {e}"[:200]
        destino = salida / "textos" / (str(rel) + ".txt")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        escaneado = bool(paginas) and len(texto.strip()) < 100 * paginas
        filas.append([str(rel), ruta.suffix.lower(), ruta.stat().st_size, len(texto), paginas or "",
                      "si" if escaneado else "", error])
        if n % 200 == 0:
            print(f"{n}/{len(archivos)}", flush=True)
    with (salida / "indice.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ruta", "tipo", "bytes", "caracteres", "paginas", "posible_escaneo", "error"])
        w.writerows(filas)
    print(f"Listo: {len(filas)} archivos, {sum(1 for f in filas if f[6])} con error, "
          f"{sum(1 for f in filas if f[5])} PDF posiblemente escaneados")


if __name__ == "__main__":
    main()
