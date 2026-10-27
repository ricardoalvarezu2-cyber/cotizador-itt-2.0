"""Lectura única de números y fechas para todas las herramientas (auditoría del 27/10/2026, controles C2 y C6).

Números:
  4,413.92 · 4.413,92  -> 4413.92   (si están los dos separadores, el último es el decimal)
  28.500 · 1.250.000    -> miles     (punto seguido de grupos de 3 cifras)
  1.096.71              -> 1096.71   (varios puntos y el último grupo no tiene 3 cifras: el último es decimal)
  12,5 · 0,904 · 6,010  -> decimal   (coma sola = decimal: los proveedores argentinos escriben así;
                                      MS Juntas cotiza con 3 decimales)
  4,500                 -> 4.5, pero se marca AMBIGUO: puede ser 4500 en una cotización en inglés.
Fechas:
  datetime, 2026-03-25, 25/03/26, 25/03/2026, "Cot 25/03/26" -> ISO. Mes > 12, día > 31 o fecha futura -> "" (inválida).
  Nunca se inventa una fecha por defecto.
"""
import re
from datetime import date, datetime


def leer_numero(v):
    """Devuelve (valor, ambiguo). valor None si no hay número."""
    if isinstance(v, bool) or v is None:
        return None, False
    if isinstance(v, (int, float)):
        return float(v), False
    s = re.sub(r"(?i)u\$s|usd|ars|\$", "", str(v)).strip()
    m = re.search(r"-?\d[\d.,]*", s)
    if not m:
        return None, False
    x = m.group(0).strip(".,")
    ambiguo = False
    if "," in x and "." in x:
        dec = "," if x.rfind(",") > x.rfind(".") else "."
        x = x.replace("." if dec == "," else ",", "").replace(dec, ".")
    elif x.count(".") > 1 or x.count(",") > 1:
        sep = "." if "." in x else ","
        partes = x.split(sep)
        if len(partes[-1]) == 3:
            x = "".join(partes)
        else:
            x = "".join(partes[:-1]) + "." + partes[-1]
    elif "." in x:
        if re.fullmatch(r"-?[1-9]\d{0,2}\.\d{3}", x):
            x = x.replace(".", "")  # '4.550 + IVA' son 4550
    elif "," in x:
        ambiguo = bool(re.fullmatch(r"-?[1-9]\d{0,2},\d{3}", x))
        x = x.replace(",", ".")
    try:
        return float(x), ambiguo
    except ValueError:
        return None, False


def numero(v):
    return leer_numero(v)[0]


def fecha_iso(v, hoy=None):
    """Fecha en ISO o "" si no hay una fecha válida."""
    hoy = hoy or date.today()
    if isinstance(v, datetime):
        d = v.date()
    elif isinstance(v, date):
        d = v
    else:
        s = str(v or "").strip()
        m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})", s)
        if m:
            a, me, di = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", s)
            if not m:
                return ""
            di, me, a = int(m.group(1)), int(m.group(2)), m.group(3)
            if len(a) == 3:
                return ""  # "02/07/025": año mal escrito
            a = int(a) + (2000 if len(a) == 2 else 0)
        try:
            d = date(a, me, di)
        except ValueError:
            return ""  # "16/19/2025"
    if d > hoy or d.year < 2000:
        return ""
    return d.isoformat()
