"""Completa la hoja Cotizador del archivo de precios Taval (Drive, Cotizador Valvulas STD Taval rev.2) editando el XML, para no perder los desplegables
(skill cotizar-valvulas-taval). Uso: python llenar_cotizador_taval.py <Cotizador Valvulas STD Taval rev.2.xlsx> <salida.xlsx>. Ítems y cantidades por skid al principio."""
import re, sys, shutil, os, zipfile
from xml.sax.saxutils import escape
src, out = sys.argv[1], sys.argv[2]
N = 24  # skids
ITEMS = [  # tipo, diam, serie, mat, trim, cant por skid, aclaración
 ("ESFERICA PT FLOTANTE", 2, 600, "WCB", "N/A", 6, "Cumple especificación (2\" #600 RF WCB, VF y VE)"),
 ("RETENCION", 2, 600, "WCB", 8, 2, "Trim 8 (a confirmar contra la clase CA31)"),
 ("FILTRO Y", 2, 600, "WCB", "N/A", 2, "Cumple especificación"),
 ("ESFERICA PT FLOT-NPT FORJADAS", "3/4", "2000 PSI", "A105", "N/A", 8, "Plano: 3/4\" 2000# → forjada NPT A105 2000 PSI"),
 ("ESFERICA PT FLOT-NPT FORJADAS", "1/2", "2000 PSI", "A105", "N/A", 6, "Plano: 1/2\" 2000# → forjada NPT A105 2000 PSI"),
 ("ESFERICA PT FLOT-NPT FORJADAS", 1, "2000 PSI", "A105", "N/A", 2, "IQ 1\" NPT → forjada NPT A105 2000 PSI"),
 ("ESFERICA PT FLOTANTE", 1, 600, "A105", "N/A", 2, "Precio neto, sin descuento. Se entrega BF60254R0504RC (bypass 1\" #600; si corresponde R50, indicarlo)"),
 ("GLOBO", 1, 600, "A105", 8, 2, "Precio neto, sin descuento (VG bypass 1\" #600)"),
]
import tempfile; d = tempfile.mkdtemp(); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
zipfile.ZipFile(src).extractall(d)
p = f"{d}/xl/worksheets/sheet1.xml"; s = open(p, encoding="utf-8").read()
col = lambda ref: re.match(r"[A-Z]+", ref).group(0)
def cidx(c): 
    n = 0
    for ch in c: n = n * 26 + ord(ch) - 64
    return n
def cell_xml(ref, v, style):
    st = f' s="{style}"' if style else ""
    if isinstance(v, (int, float)): return f'<c r="{ref}"{st}><v>{v}</v></c>'
    return f'<c r="{ref}"{st} t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'
def setc(s, ref, v):
    row = re.search(r"\d+", ref).group(0)
    m = re.search(rf'<c r="{ref}"(?: [^>]*)?(?:/>|>.*?</c>)', s, re.S)
    if m:
        st = re.search(r' s="(\d+)"', m.group(0)); st = st.group(1) if st else None
        return s[:m.start()] + cell_xml(ref, v, st) + s[m.end():]
    rm = re.search(rf'<row r="{row}"[^>]*?(?:/>|>(.*?)</row>)', s, re.S)
    body = rm.group(1) or ""
    cells = list(re.finditer(r'<c r="([A-Z]+)\d+"', body))
    pos = len(body)
    for c in cells:
        if cidx(c.group(1)) > cidx(col(ref)): pos = c.start(); break
    nb = body[:pos] + cell_xml(ref, v, None) + body[pos:]
    head = re.match(r'<row [^>]*?', rm.group(0)).group(0).rstrip("/")
    head = re.match(r'(<row [^>]*?)/?>', rm.group(0)).group(1)
    return s[:rm.start()] + head + ">" + nb + "</row>" + s[rm.end():]
s = setc(s, "I1", "ITT S.A. - YPF Gas Lift: puente de inyección y regulación 2\" #600, SAP 1000653143 (24 skids) - COT26-0330-004")
s = setc(s, "I2", "26-11-2026")
for i, (t, dm, se, ma, tr, q, acl) in enumerate(ITEMS):
    r = 6 + i
    for c, v in zip("ABCDEF", (i + 1, t, dm, se, ma, tr)): s = setc(s, f"{c}{r}", v)
    s = setc(s, f"I{r}", 0.35); s = setc(s, f"K{r}", 0.2); s = setc(s, f"M{r}", q * N)
    s = setc(s, f"O{r}", "A confirmar (sin acceso a DRILL STOCK)"); s = setc(s, f"P{r}", acl)
# limpiar el ejemplo de las filas siguientes que traía la plantilla
for r in range(6 + len(ITEMS), 26):
    for c in "ABCDEFMOP":
        m = re.search(rf'<c r="{c}{r}"(?: [^>]*)?(?:/>|>.*?</c>)', s, re.S)
        if m and c != "A":
            st = re.search(r' s="(\d+)"', m.group(0)); st = f' s="{st.group(1)}"' if st else ""
            s = s[:m.start()] + f'<c r="{c}{r}"{st}/>' + s[m.end():]
open(p, "w", encoding="utf-8").write(s)
w = f"{d}/xl/workbook.xml"; ws = open(w).read()
if "fullCalcOnLoad" not in ws: ws = re.sub(r"<calcPr", '<calcPr fullCalcOnLoad="1"', ws)
open(w, "w").write(ws)
if os.path.exists(f"{d}/xl/calcChain.xml"): os.remove(f"{d}/xl/calcChain.xml")
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        if it.filename == "xl/calcChain.xml" or it.is_dir(): continue
        zout.writestr(it, open(f"{d}/{it.filename}", "rb").read())
print("ok", out)
