"""Candado y escritura segura para las herramientas que reescriben tablas compartidas (auditoría 29-10-2026).

Dos corridas a la vez (dos sesiones, o agentes en paralelo) corrompían los catálogos: una leía el CSV mientras la otra
lo estaba escribiendo. Ahora:
- `candado()`: una sola corrida por vez en el repositorio. La segunda espera a que termine la primera (avisa).
  Los procesos hijos heredan el permiso (variable COTIZADOR_CANDADO), así verificar_todo.py puede llamar a los demás.
- `escribir(ruta)`: escribe en un archivo temporal y lo reemplaza de una vez (os.replace); nadie ve un archivo a medias.
- `guardar_libro(wb, ruta)`: lo mismo para un Excel de openpyxl.
- `perfil_soffice()`: perfil propio de LibreOffice para cada proceso (dos conversiones a la vez se pisaban).
"""
import contextlib
import fcntl
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / ".cotizador.lock"


@contextlib.contextmanager
def candado(quien=""):
    if os.environ.get("COTIZADOR_CANDADO"):
        yield
        return
    with open(ARCHIVO, "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"Otra corrida está usando el repositorio; espero a que termine{' (' + quien + ')' if quien else ''}…", file=sys.stderr)
            t = time.time()
            fcntl.flock(f, fcntl.LOCK_EX)
            print(f"Listo, sigo (esperé {time.time() - t:.0f} s).", file=sys.stderr)
        os.environ["COTIZADOR_CANDADO"] = str(os.getpid())
        try:
            yield
        finally:
            os.environ.pop("COTIZADOR_CANDADO", None)
            fcntl.flock(f, fcntl.LOCK_UN)


@contextlib.contextmanager
def escribir(ruta, modo="w", **kw):
    ruta = Path(ruta)
    if "b" not in modo:
        kw.setdefault("encoding", "utf-8")
    fd, tmp = tempfile.mkstemp(dir=ruta.parent, prefix="." + ruta.name + ".", suffix=".tmp")
    os.close(fd)
    try:
        with open(tmp, modo, **kw) as f:
            yield f
        os.replace(tmp, ruta)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def guardar_libro(wb, ruta):
    ruta = Path(ruta)
    fd, tmp = tempfile.mkstemp(dir=ruta.parent, prefix="." + ruta.stem + ".", suffix=ruta.suffix)
    os.close(fd)
    try:
        wb.save(tmp)
        os.replace(tmp, ruta)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def perfil_soffice():
    return f"-env:UserInstallation=file://{tempfile.gettempdir()}/soffice-itt-{os.getpid()}"
