"""Aviso de precio no encontrado en su documento de origen (solo avisa, nunca confirma; Matías, 30-10-2026).

Uso: python herramientas/verificar_origen.py cotizaciones/<carpeta>     (lo corre armar_cotizacion.py → verificacion_origen.md)

Por cada renglón con precio (no estimado), busca el archivo de texto del documento de origen en el repositorio (la ruta del
renglón, o la del catálogo según su código) y se fija si el precio figura ahí (también con IVA del 21% o 10,5%). Si no
figura, AVISA para que alguien lo mire en el original. Que figure no prueba que sea de ese renglón: por eso no se marca
nada como "verificado" y el control de P4 sigue siendo de una persona o de la IA.
No se controlan (y se dice cuántos): estimados, precios convertidos de pesos, y renglones cuyo documento no está en el
repositorio como texto (escaneos, Z:\\ sin texto extraído).
"""
import csv
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TEXTOS = RAIZ / "fuentes_originales" / "ofertas_texto"
HIST = RAIZ / "conocimiento" / "precios" / "catalogo_materiales_historial.csv"
HIST_SRV = RAIZ / "conocimiento" / "precios" / "catalogo_servicios_historial.csv"
CODIGO = re.compile(r"\b[A-Z]{3}-\d{5}\b")
PESOS = re.compile(r"(?i)\bars\b|\bpesos\b|\$ ?\d|tipo de cambio|\btc\b|convertid|cepo|blue")


def numeros_en_texto(texto):
    """Todos los números del texto como valores (con las dos lecturas posibles cuando el separador es ambiguo)."""
    vals = set()
    for tok in re.findall(r"\d[\d.,]*\d|\d", texto):
        cands = []
        if "," in tok and "." in tok:
            dec = "," if tok.rfind(",") > tok.rfind(".") else "."
            mil = "." if dec == "," else ","
            cands.append(tok.replace(mil, "").replace(dec, "."))
        elif "," in tok or "." in tok:
            sep = "," if "," in tok else "."
            cands.append(tok.replace(sep, ""))                       # separador de miles
            if tok.count(sep) == 1:
                cands.append(tok.replace(sep, "."))                  # separador decimal
        else:
            cands.append(tok)
        for c in cands:
            try:
                vals.add(round(float(c), 2))
            except ValueError:
                pass
    return vals


def figura(precio, valores):
    for p in (precio, precio * 1.21, precio * 1.105):
        tol = max(0.011, abs(p) * 0.0005)
        if any(abs(v - p) <= tol for v in valores):
            return True
    return False


_HIST = None


def historial():
    global _HIST
    if _HIST is None:
        _HIST = {}
        for ruta in (HIST, HIST_SRV):
            if ruta.exists():
                for r in csv.DictReader(open(ruta, encoding="utf-8")):
                    _HIST.setdefault(r["codigo"], []).append(r)
    return _HIST


def textos_de(origen):
    """Archivos de texto del repositorio que corresponden a un origen ("Z:\\...\\carpeta · sub/archivo", "fuentes_originales/x.xlsx · …")."""
    o = str(origen or "").strip()
    if not o:
        return []
    out = []
    if o.lower().startswith("z:\\ventas\\ofertas y licitaciones\\"):
        resto = o[len("z:\\ventas\\ofertas y licitaciones\\"):].replace("\\", "/")
        carpeta, _, archivo = resto.partition(" · ")
        base = TEXTOS / carpeta.strip()
        if archivo:
            out += [base / (archivo.strip() + ".txt"), base / archivo.strip()]
        elif base.is_dir():
            out += [p for p in base.rglob("*.txt")]
    elif re.match(r"^[A-Za-zÁÉÍÓÚÑ&+ .]+/\d+\b", o.split(" · ")[0]):  # "APSA/15 · …": carpeta abreviada del cliente
        cli, num = o.split(" · ")[0].split("/")[:2]
        num = re.match(r"\d+", num).group(0)
        base = TEXTOS / cli.strip()
        if base.is_dir():
            for d in base.iterdir():
                if d.is_dir() and re.match(rf"0*{num}\b|0*{num}\s*[-._]", d.name):
                    out += list(d.rglob("*.txt"))
    else:
        ruta = o.split(" · ")[0].strip()
        p = RAIZ / ruta
        out += [p, Path(str(p) + ".txt")]
        if p.is_dir():
            out += list(p.rglob("*.txt"))
        if p.suffix.lower() in (".xlsx", ".xls", ".docx", ".pdf"):
            out += list((RAIZ / "fuentes_originales").rglob(p.name + ".txt"))
    return [p for p in out if p.is_file() and p.suffix.lower() in (".txt", ".csv", ".md", ".json")]


def controlar(it):
    """('aviso'|'figura'|'sin_control', detalle) de un renglón."""
    s = it["fuentes"][0]
    precio = float(s.get("precio") or 0)
    if not precio or s.get("tipo") == "est":
        return "sin_control", "estimado o sin precio"
    if PESOS.search(" ".join(str(s.get(k) or "") for k in ("proveedor", "diferencia", "origen", "nota"))):
        return "sin_control", "convertido de pesos"
    archivos = textos_de(s.get("origen"))
    cod = s.get("codigo") or (CODIGO.search(str(s.get("proveedor") or "")) or [None])[0] if not s.get("codigo") else s.get("codigo")
    if cod:
        for h in historial().get(cod, []):
            try:
                ph = float(h.get("precio_usd") or h.get("precio") or 0)
            except ValueError:
                continue
            if abs(ph - precio) <= max(0.011, precio * 0.0005):
                if PESOS.search(f"{h.get('nota', '')} {h.get('iva', '')}"):
                    return "sin_control", "convertido de pesos (catálogo)"
                archivos += textos_de(h.get("ruta_repo")) + textos_de(f"{h.get('ruta_origen', '')} · {h.get('archivo_origen', '')}")
    m = re.search(r"c[óo]d\.? ?(\w+)", str(s.get("proveedor") or ""))  # "Renard · cód. 5979": el código del proveedor en el historial
    if m:
        for hs in historial().values():
            for h in hs:
                if h.get("archivo_origen") == f"código {m.group(1)}":
                    archivos += textos_de(h.get("ruta_repo"))
    if re.search(r"(?i)lista 30 ?× ?0[.,]52|× ?\d", str(s.get("proveedor") or "")):
        return "sin_control", "precio calculado (lista × factor)"
    archivos = list(dict.fromkeys(archivos))
    if not archivos:
        return "sin_control", "el documento no está como texto en el repositorio"
    ml = re.search(r"l[íi]nea (\d+)", str(s.get("origen") or ""))
    if ml:  # "· línea 147": el precio tiene que estar en esa línea (segunda auditoría 30-10-2026)
        n = int(ml.group(1))
        # (límite conocido: alcanza con que el precio sea UN número de esa línea; puede coincidir con otra columna)
        malos = []
        for a in archivos:
            try:
                ls = a.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            if len(ls) >= n:
                if figura(precio, numeros_en_texto(ls[n - 1])):
                    return "figura", f"{a.relative_to(RAIZ)} (línea {n})"
                malos.append(a)
        if malos:  # se miran todos los archivos candidatos, no solo el primero (cuarta auditoría)
            return "aviso", f"en la línea {n} de {malos[0].relative_to(RAIZ)} no figura USD {precio}"
        # la línea citada no existe en ningún archivo: no se busca en todo el archivo (tercera auditoría 30-10-2026)
        return "aviso", f"la línea {n} citada no existe en {archivos[0].relative_to(RAIZ)}"
    if m:  # lista con código del proveedor (auditoría 30-10-2026): el precio tiene que estar en la línea de ese código, no en
        # cualquier lugar de la lista (en una lista de miles de precios casi cualquier número "figura")
        rx = re.compile(rf"(?:^|[\s,|;(]){re.escape(m.group(1))}(?=[\s,|;)]|$)")
        lineas = []
        for a in archivos:
            try:
                lineas += [(a, l) for l in a.read_text(encoding="utf-8", errors="ignore").splitlines() if rx.search(l)]
            except OSError:
                continue
        if lineas:
            for a, l in lineas:
                if figura(precio, numeros_en_texto(l)):
                    return "figura", f"{a.relative_to(RAIZ)} (línea del código {m.group(1)})"
            return "aviso", f"en la línea del código {m.group(1)} no figura USD {precio} ({lineas[0][0].relative_to(RAIZ)})"
    for a in archivos:
        try:
            if figura(precio, numeros_en_texto(a.read_text(encoding="utf-8", errors="ignore"))):
                return "figura", str(a.relative_to(RAIZ))
        except OSError:
            continue
    return "aviso", ", ".join(str(a.relative_to(RAIZ)) for a in archivos[:2])


def main(carpeta):
    carpeta = Path(carpeta)
    c = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    avisos, sin, n = [], {}, 0
    for it in c["items"]:
        estado, det = controlar(it)
        n += 1
        if estado == "aviso":
            avisos.append(f"- ⚠ {it.get('pos') or it['id']} {it['descripcion'][:60]}: USD {it['fuentes'][0]['precio']} no figura tal cual en {det} (si es un valor calculado o escalado, que lo diga la fuente). Mirarlo en el original.")
        elif estado == "sin_control":
            sin[det] = sin.get(det, 0) + 1
    lineas = [f"# Precio en el documento de origen — {c['codigo']}", "",
              "Generado por `herramientas/verificar_origen.py`. Solo avisa cuando el precio NO aparece en el documento de origen; "
              "que aparezca no prueba que sea de ese renglón (el control P4 sigue siendo de una persona o de la IA).", "",
              "## Avisos", ""] + (avisos or ["- Ninguno."]) + ["", "## No controlados", ""] + \
             ([f"- {k}: {v}" for k, v in sin.items()] or ["- Ninguno."])
    (carpeta / "verificacion_origen.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Origen de precios: {n} renglones, {len(avisos)} avisos, {sum(sin.values())} sin controlar → {carpeta / 'verificacion_origen.md'}")
    return avisos


if __name__ == "__main__":
    main(sys.argv[1])
