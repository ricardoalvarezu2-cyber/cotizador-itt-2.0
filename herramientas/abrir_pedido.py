"""Abre todo lo que manda el cliente para un pedido y lo deja leído en el repositorio.

Uso:
  python herramientas/abrir_pedido.py cotizaciones/<carpeta>/pedido ARCHIVO_O_CARPETA [ARCHIVO_O_CARPETA ...]

Qué hace (sin IA, no interpreta nada):
  1. Copia cada archivo a pedido/ (sin el prefijo de subida "xxxxxxxx-") y descomprime los .zip, también los que
     vienen adentro de otros zip o de un mail, cada uno en su carpeta.
  2. Arregla los nombres con "#U00f3" y similares (zip de Windows) a sus letras (ó, á, ñ…).
  3. Abre los mails .msg con herramientas/leer_msg.py (sin librerías externas): guarda el cuerpo y los adjuntos en
     <mail>_adjuntos/ y los procesa igual.
  4. Al lado de cada documento deja su texto: .pdf (pdftotext -layout), .docx, .xlsx/.xlsm (openpyxl), .doc y .xls
     (LibreOffice). Los .7z, .rar y .dwg se listan sin abrir.
  5. Escribe pedido/inventario.md: cada archivo con tipo, páginas, caracteres de texto y aviso de "posible escaneo o
     dibujo" (PDF con menos de 100 caracteres por página: hay que mirarlo como imagen, p. ej. con recortar_plano.py).

Después, la lectura y el informe los hace la IA siguiendo el skill relevar-pedido.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import leer_msg  # noqa: E402

UNICODE = re.compile(r"#U([0-9a-fA-F]{4})")
PREFIJO_SUBIDA = re.compile(r"^[0-9a-f]{8}-")
SIN_ABRIR = {".7z", ".rar", ".dwg", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def nombre_limpio(n):
    return UNICODE.sub(lambda m: chr(int(m.group(1), 16)), n)


def arreglar_nombres(carpeta: Path):
    for p in sorted(carpeta.rglob("*"), key=lambda x: -len(x.parts)):
        nuevo = nombre_limpio(p.name)
        if nuevo != p.name:
            p.rename(p.with_name(nuevo))


def descomprimir(z: Path):
    destino = z.with_suffix("")
    destino.mkdir(exist_ok=True)
    with zipfile.ZipFile(z) as f:
        for m in f.infolist():
            # zip de Windows sin bandera UTF-8: los nombres vienen en cp437; se pasan a cp850/latin-1 si corresponde
            nombre = m.filename
            if not (m.flag_bits & 0x800):
                try:
                    nombre = nombre.encode("cp437").decode("cp850")
                except UnicodeError:
                    pass
            ruta = (destino / nombre_limpio(nombre)).resolve()
            if destino.resolve() not in ruta.parents and ruta != destino.resolve():
                continue  # nombre que sale de la carpeta: se ignora
            if m.is_dir():
                ruta.mkdir(parents=True, exist_ok=True)
                continue
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with f.open(m) as src, open(ruta, "wb") as dst:
                shutil.copyfileobj(src, dst)
    return destino


def abrir_mail(m: Path):
    salida = m.with_name(m.stem + "_adjuntos")
    ents, kids, data = leer_msg.cfb(str(m))
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        leer_msg.guardar(ents, kids, data, 0, str(salida))
    m.with_suffix(".txt").write_text(buf.getvalue(), encoding="utf-8")
    return salida


def texto_pdf(p: Path):
    out = p.with_suffix(".txt")
    subprocess.run(["pdftotext", "-layout", str(p), str(out)], capture_output=True, timeout=300)
    pags = None
    r = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True, timeout=60)
    m = re.search(r"Pages:\s+(\d+)", r.stdout)
    if m:
        pags = int(m.group(1))
    return out, pags


def texto_docx(p: Path):
    x = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8", "replace")
    x = re.sub(r"</w:p>", "\n", x)
    x = re.sub(r"</w:tc>", " | ", x)
    t = re.sub(r"<[^>]+>", "", x)
    out = p.with_suffix(".txt")
    out.write_text(t, encoding="utf-8")
    return out, None


def texto_xlsx(p: Path):
    import warnings
    import openpyxl
    warnings.filterwarnings("ignore")
    out = p.with_suffix(".txt")
    try:
        wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    except Exception:
        return texto_office(p, "csv")
    partes = []
    for ws in wb.worksheets:
        partes.append(f"=== hoja {ws.title}")
        for fila in ws.iter_rows(values_only=True):
            v = [str(c) for c in fila if c is not None and str(c).strip()]
            if v:
                partes.append(" | ".join(v))
    out.write_text("\n".join(partes), encoding="utf-8")
    return out, None


def texto_office(p: Path, formato):
    with tempfile.TemporaryDirectory() as tmp:
        filtro = "txt:Text" if formato == "txt" else "csv"
        subprocess.run(["soffice", "--headless", "--convert-to", filtro, "--outdir", tmp, str(p)],
                       capture_output=True, timeout=180)
        gen = Path(tmp) / (p.stem + (".txt" if formato == "txt" else ".csv"))
        out = p.with_suffix(".txt" if formato == "txt" else ".csv")
        if gen.exists():
            shutil.copyfile(gen, out)
            return out, None
    return None, None


def procesar(carpeta: Path):
    """Descomprime y abre mails hasta que no quede nada nuevo; después extrae el texto de todo."""
    hechos = set()
    cambio = True
    while cambio:
        cambio = False
        arreglar_nombres(carpeta)
        for p in sorted(carpeta.rglob("*")):
            if p in hechos or not p.is_file():
                continue
            if p.suffix.lower() == ".zip":
                descomprimir(p)
                hechos.add(p)
                cambio = True
            elif p.suffix.lower() == ".msg":
                try:
                    abrir_mail(p)
                except Exception as e:  # mail dañado: se anota y se sigue
                    p.with_suffix(".txt").write_text(f"ERROR al abrir el mail: {e}", encoding="utf-8")
                hechos.add(p)
                cambio = True
    filas = []
    for p in sorted(carpeta.rglob("*")):
        if not p.is_file() or p.name == "inventario.md":
            continue
        ext = p.suffix.lower()
        if ext in (".txt", ".csv") and (p.with_suffix(".pdf").exists() or any(p.with_suffix(e).exists() for e in (".docx", ".doc", ".xlsx", ".xlsm", ".xls", ".msg", ".DOC"))):
            continue  # es el texto extraído de otro archivo
        out, pags, nota = None, None, ""
        try:
            if ext == ".pdf":
                out, pags = texto_pdf(p)
            elif ext == ".docx":
                out, pags = texto_docx(p)
            elif ext in (".xlsx", ".xlsm"):
                out, pags = texto_xlsx(p)
            elif ext == ".doc":
                out, pags = texto_office(p, "txt")
            elif ext == ".xls":
                out, pags = texto_office(p, "csv")
            elif ext == ".msg":
                out = p.with_suffix(".txt")
            elif ext == ".zip":
                nota = "descomprimido en " + p.with_suffix("").name + "/"
            elif ext in SIN_ABRIR:
                nota = "sin abrir (" + ext + ")"
        except Exception as e:
            nota = f"ERROR: {type(e).__name__}: {e}"[:150]
        car = len(out.read_text(encoding="utf-8", errors="replace").strip()) if out and out.exists() else 0
        if ext == ".pdf" and pags and car < 100 * pags:
            nota = (nota + " " if nota else "") + "posible escaneo o dibujo: mirarlo como imagen"
        filas.append((str(p.relative_to(carpeta)), ext, p.stat().st_size, pags or "", car, nota))
    return filas


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    pedido = Path(sys.argv[1])
    pedido.mkdir(parents=True, exist_ok=True)
    for a in sys.argv[2:]:
        src = Path(a)
        if src.is_dir():
            shutil.copytree(src, pedido / nombre_limpio(src.name), dirs_exist_ok=True)
        else:
            shutil.copyfile(src, pedido / nombre_limpio(PREFIJO_SUBIDA.sub("", src.name)))
    filas = procesar(pedido)
    lineas = ["# Inventario del pedido", "", "Lo genera `herramientas/abrir_pedido.py`. Cada documento tiene su texto al lado (.txt o .csv).", "",
              "| Archivo | Tipo | Bytes | Páginas | Caracteres de texto | Nota |", "|---|---|---|---|---|---|"]
    for f in filas:
        lineas.append("| " + " | ".join(str(x).replace("|", "/") for x in f) + " |")
    (pedido / "inventario.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Listo: {len(filas)} archivos en {pedido}; ver inventario.md "
          f"({sum(1 for f in filas if 'escaneo' in f[5])} PDF para mirar como imagen, "
          f"{sum(1 for f in filas if 'ERROR' in f[5])} con error)")


if __name__ == "__main__":
    main()
