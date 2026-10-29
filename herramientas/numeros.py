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


def a_vista(v):
    """Fecha para mostrar: siempre DD-MM-AAAA (decisión de Matías, 28/10/2026). Adentro se guarda AAAA-MM-DD.
    Acepta AAAA-MM-DD (o con hora), AAAA-MM (→ MM-AAAA) y DD/MM/AAAA; cualquier otra cosa vuelve como está."""
    s = str(v or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        return f"{m.group(2)}-{m.group(1)}"
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}-{m.group(3)}"
    return s


def fmt(v, d=2, signo=False):
    """Número para mostrar: punto de miles, coma decimal y d decimales (2 por defecto: precios y cantidades,
    decisión de Matías, 29-10-2026). fmt(1234.5) = '1.234,50'. Solo para textos a la vista; los CSV y JSON
    internos siguen con punto decimal y sin separador de miles."""
    if v is None or v == "":
        return ""
    v = float(v)
    s = f"{abs(v):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 and float(s.replace(".", "").replace(",", ".")) else "+" if signo and v > 0 else "") + s


def fmtg(v):
    """Como fmt pero sin ceros de más: 0.5 → '0,5', 12 → '12', 1234.567 → '1.234,57' (máximo 2 decimales)."""
    s = fmt(v, 2)
    return s.rstrip("0").rstrip(",") if "," in s else s


def precio_csv(v):
    """Precio para guardar en un CSV o JSON interno: 2 decimales, punto decimal, sin separador de miles y sin ceros
    de más (6.408 → '6.41', 12.0 → '12'). Vacío o texto no numérico vuelve como está (decisión de Matías, 29-10-2026:
    los precios y montos llevan 2 decimales; precios por kg o por pulgada también)."""
    if v is None or isinstance(v, bool):
        return v
    try:
        x = round(float(v), 2)
    except (TypeError, ValueError):
        return v
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def redondear_precios(filas, columnas):
    """Aplica precio_csv a las columnas de precio de una lista de filas (dicts) antes de escribir el CSV."""
    for f in filas:
        for c in columnas:
            if c in f and f[c] not in (None, ""):
                f[c] = precio_csv(f[c])
    return filas


# ---------------------------------------------------------------- Excel
# En los xlsx los números van como celdas NUMÉRICAS (nunca texto) con formato: Excel en configuración argentina los
# muestra con punto de miles y coma decimal (decisión de Matías, 29-10-2026).
FMT_PRECIO = "#,##0.00"      # precios y montos: 2 decimales
FMT_TECNICO = "#,##0.0###"   # pesos, espesores, factores: los decimales que hagan falta
FMT_ENTERO = "#,##0"
_RX_PRECIO = re.compile(r"(precio|costo|monto|importe|valor|total|subtotal|tarifa|_usd$|_ars$|_eur$)", re.I)
_RX_NO_PRECIO = re.compile(r"(cantidad|cant_|peso|_kg|factor|porc|pct|horas|_hs|indice|coef|dias|filas|historial|ratio)", re.I)
_RX_SIN_MILES = re.compile(r"(año|anio|serie|schedule|sch|clase|rating|ansi|mes)", re.I)
_RX_CLAVE = re.compile(r"^(codigo|cod|clave|id|pos|op|numero|nro|n°|oc|oc_numero|orden_compra|cuit|telefono|tel|isis|articulo|art)(_|$)", re.I)


def es_columna_precio(nombre):
    n = str(nombre or "").strip().lower().replace(" ", "_")
    return bool(_RX_PRECIO.search(n)) and not _RX_NO_PRECIO.search(n)


def celda_excel(celda, valor, columna="", formato=None, documento=False):
    """Escribe valor en una celda de openpyxl. Un número (o un texto que es un número entero, sin nada más) queda
    numérico con formato de precio (2 decimales) o técnico según la columna. Las claves (código, pos, OC) quedan como
    texto. formato fuerza un formato de número.
    documento=False: el texto viene de un CSV/JSON interno (punto decimal, '6.41').
    documento=True: el texto viene de un documento de terceros y se lee con leer_numero ('1.500' = 1500, '12,5' = 12,5);
    si es ambiguo ('4,500') queda como texto, tal cual."""
    n = str(columna or "").strip().lower().replace(" ", "_")
    v = valor
    if isinstance(v, str) and v.strip() and not _RX_CLAVE.search(n):
        t = v.strip()
        if documento:
            if re.fullmatch(r"-?\d[\d.,]*", t) and not re.search(r"[.,]$", t):
                x, amb = leer_numero(t)
                if x is not None and not amb:
                    v = int(x) if x.is_integer() and not re.search(r"[.,]\d*[1-9]", t) else x
        elif re.fullmatch(r"-?(0|[1-9]\d*)(\.\d+)?", t):
            v = float(t) if "." in t else int(t)
    celda.value = v
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if formato:
            celda.number_format = formato
        elif es_columna_precio(n):
            celda.number_format = FMT_PRECIO
        elif _RX_SIN_MILES.search(n) and float(v).is_integer():
            celda.number_format = "0"  # año, serie, schedule: 2025 y 2500 sin punto de miles
        elif isinstance(v, int) or float(v).is_integer():
            celda.number_format = FMT_ENTERO
        else:
            celda.number_format = FMT_TECNICO
    return celda
