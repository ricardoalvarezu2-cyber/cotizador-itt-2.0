"""Completa los datos de cada renglón de pedido/lista_materiales_plano.csv en columnas (Matías, 03-11-2026): tipo, Ø2,
serie, schedule, espesor, cara, norma, marca, modelo, rango, trim, paso, costura, revestimiento, largo y medida, con los
mismos nombres que el catálogo, para que la búsqueda de antecedentes y la planilla comparen dato por dato.

Uso: python herramientas/atributos_plano.py cotizaciones/<carpeta> [--pisar]

Lo lee del texto literal del cliente (descripción, Ø, serie/sch, material, extremos y modelo/fabricante). Nunca toca las
columnas literales ni pisa un dato ya cargado (salvo --pisar). Al final lista, renglón por renglón, los datos que hacen
falta para identificar la pieza y no figuran: esos se completan a mano o se piden al cliente.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_materiales import FAMILIAS, atributos, expandir, familia_de  # noqa: E402
from indice_proyectos import norm  # noqa: E402

# columnas de datos de la lista del plano (además de las literales del cliente: descripcion, diametro, serie_sch,
# material, extremos y modelo_fabricante); mismos nombres que en catalogo_materiales.csv
ATRIBUTOS = ["familia", "tipo", "diametro2", "serie", "schedule", "espesor_mm", "cara", "norma", "marca", "modelo", "rango",
             "trim", "paso", "costura", "revestimiento", "largo_mm", "medida"]
LITERALES = {"diametro": "diametro", "material": "material", "extremos": "extremos"}


# Columnas de datos de la planilla y de la página: lo que pide el cliente y lo que tiene el antecedente, dato por dato
COLS = [("Ø", "diametro"), ("Ø2", "diametro2"), ("Serie", "serie"), ("Sch", "schedule"), ("Espesor mm", "espesor_mm"), ("Material", "material"),
        ("Extremos", "extremos"), ("Cara", "cara"), ("Norma", "norma"), ("Marca", "marca"), ("Modelo", "modelo"), ("Rango", "rango")]
OTROS = ["tipo", "trim", "paso", "costura", "revestimiento", "largo_mm", "medida", "designacion", "conexion"]
NOMBRES = {"diametro": "Ø", "diametro2": "Ø2", "serie": "serie", "schedule": "schedule", "espesor_mm": "espesor", "largo_mm": "largo",
           "designacion": "designación", "conexion": "conexión"}


def otros(at):
    return "; ".join(f"{k}: {at[k]}" for k in OTROS if at.get(k))


def fila_datos(it, cat):
    """Valores de las columnas de datos de un material: pedido (familia, COLS, otros, faltan) y antecedente (código,
    descripción, COLS, otros), en el orden de encabezados()."""
    import re
    at = it.get("atributos") or {}
    s = it["fuentes"][0]
    cod = s.get("codigo") or (re.findall(r"\b[A-Z]{3}-\d{5}\b", str(s.get("proveedor", ""))) or [""])[0]
    r = cat.get(cod, {})
    ped = [at.get("familia", "")] + [at.get(k, "") for _, k in COLS] + [otros(at), ", ".join(NOMBRES.get(k, k) for k in it.get("faltan_datos", []))]
    ant = [cod, r.get("descripcion", "")] + [r.get(k, "") for _, k in COLS] + [otros(r)]
    return ped, ant


def encabezados():
    return (["Pedido: familia"] + [f"Pedido: {n}" for n, _ in COLS] + ["Pedido: otros datos", "Datos que faltan del pedido"],
            ["Antecedente: código", "Antecedente: descripción"] + [f"Antecedente: {n}" for n, _ in COLS] + ["Antecedente: otros datos"])


def leer(r):
    """Familia y datos de un renglón: lo cargado en columnas manda sobre lo leído del texto."""
    import precotizar
    t = expandir(norm(precotizar.texto_busqueda(r)))
    fam = r.get("familia") if r.get("familia") in FAMILIAS else familia_de(t)
    at = atributos(t, fam)
    for k in ATRIBUTOS[1:]:
        if str(r.get(k, "")).strip():
            at[k] = r[k].strip()
    return fam, at


def fijos(r):
    """Datos cargados en columnas de un renglón (para buscar_material.buscar)."""
    return {k: r[k] for k in ATRIBUTOS[1:] if str(r.get(k, "")).strip()}


def completar(carpeta, pisar=False):
    ruta = Path(carpeta) / "pedido" / "lista_materiales_plano.csv"
    filas = list(csv.DictReader(open(ruta, encoding="utf-8")))
    if not filas:
        return []
    campos = list(filas[0].keys()) + [k for k in ATRIBUTOS if k not in filas[0]]
    from buscar_material import faltan_datos
    informe = []
    for r in filas:
        for k in ATRIBUTOS:
            r.setdefault(k, "")
        t = expandir(norm(__import__("precotizar").texto_busqueda(r)))
        fam = familia_de(t)
        at = atributos(t, fam)
        lit = str(r.get("material", ""))
        if lit.lower().startswith("rango:") and (pisar or not r["rango"].strip()):  # sensores: el plano trae el rango
            r["rango"] = lit.split(":", 1)[1].strip()
        if pisar or not r["familia"]:
            r["familia"] = fam
        fam = r["familia"]
        for k in ATRIBUTOS[1:]:
            if at.get(k) and (pisar or not r[k].strip()):
                r[k] = at[k]
        _, todo = leer(r)
        todo.update({k: v for k, v in at.items() if k in LITERALES})
        falta = faltan_datos(fam, todo)
        if falta:
            informe.append((r["pos"], r["descripcion"], falta))
    w = csv.DictWriter(open(ruta, "w", newline="", encoding="utf-8"), fieldnames=campos)
    w.writeheader()
    w.writerows(filas)
    return informe


def fijar(carpeta, datos):
    """Carga a mano datos de renglones de la lista del plano ({pos: {columna: valor}}), pisando lo leído del texto."""
    ruta = Path(carpeta) / "pedido" / "lista_materiales_plano.csv"
    filas = list(csv.DictReader(open(ruta, encoding="utf-8")))
    campos = list(filas[0].keys())
    for r in filas:
        for k, v in datos.get(r["pos"], {}).items():
            assert k in campos and k in ATRIBUTOS, k  # nunca las columnas literales del documento
            r[k] = v
    w = csv.DictWriter(open(ruta, "w", newline="", encoding="utf-8"), fieldnames=campos)
    w.writeheader()
    w.writerows(filas)


def atributos_items(carpeta, cfg):
    """Datos en columnas de cada material de una cotización (para la planilla y la página): los de la precotización si
    los tiene; si no, los de su renglón en la lista del plano; si no, los leídos del texto del ítem. Agrega "faltan_datos"."""
    from buscar_material import faltan_datos
    ruta = Path(carpeta) / "pedido" / "lista_materiales_plano.csv"
    plano = {r["pos"]: r for r in csv.DictReader(open(ruta, encoding="utf-8"))} if ruta.exists() else {}
    for it in cfg["items"]:
        if it["grupo"] != "material" or it.get("atributos"):
            continue
        r = plano.get(str(it.get("pos")))
        if r:
            fam, at = leer(r)
            t = expandir(norm(__import__("precotizar").texto_busqueda(r)))
            at = {**atributos(t, fam), **{k: v for k, v in at.items() if v}}
        else:
            t = expandir(norm(f"{it['descripcion']} {it.get('especificacion', '')}"))
            fam = familia_de(t)
            at = atributos(t, fam)
        it["atributos"] = {"familia": fam, **{k: v for k, v in at.items() if v}}
        it["faltan_datos"] = faltan_datos(fam, at)
    return cfg


def main(carpeta, *op):
    inf = completar(carpeta, "--pisar" in op)
    print(f"{carpeta}: datos completados en pedido/lista_materiales_plano.csv")
    for pos, d, falta in inf:
        print(f"  ! Pos {pos} ({d[:45]}): falta {', '.join(falta)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(*sys.argv[1:])


# Listas por familia de la planilla y de la página (Matías, 03-11-2026): una lista debajo de la otra, cada una con las
# características que corresponden a esa familia y su subtotal. (nombre, familias del catálogo, columnas)
GRUPOS = [
    ("Válvulas", ("VAL",), ["diametro", "tipo", "serie", "paso", "material", "trim", "extremos", "norma", "marca", "modelo"]),
    ("Accesorios de piping (bridas, tes, codos, reducciones, olets, cuplas)", ("BRI", "AFO", "ABW"),
     ["diametro", "diametro2", "tipo", "serie", "schedule", "cara", "material", "extremos", "norma"]),
    ("Caños y niples", ("CAN", "NIP"), ["diametro", "schedule", "espesor_mm", "material", "costura", "revestimiento", "largo_mm", "extremos", "norma"]),
    ("Perfiles y estructura", ("PER",), ["tipo", "designacion", "espesor_mm", "material", "medida", "norma"]),
    ("Chapas, rejillas y mallas", ("PER",), ["tipo", "espesor_mm", "material", "medida", "norma"]),
    ("Instrumentos", ("INS",), ["tipo", "rango", "diametro", "conexion", "material", "marca", "modelo"]),
    ("Juntas, espárragos y bulonería", ("JUN",), ["tipo", "diametro", "serie", "material", "medida", "norma"]),
    ("Otros materiales", (), ["tipo", "diametro", "serie", "material", "medida", "rango", "marca", "modelo"]),
]
ETIQUETAS = {"diametro": "Ø", "diametro2": "Ø2", "tipo": "Tipo", "serie": "Serie", "schedule": "Sch", "paso": "Paso", "material": "Material",
             "trim": "Trim", "extremos": "Extremos", "cara": "Cara", "norma": "Norma", "marca": "Marca", "modelo": "Modelo", "espesor_mm": "Espesor mm",
             "costura": "Costura", "revestimiento": "Revestimiento", "largo_mm": "Largo mm", "designacion": "Designación", "medida": "Medida",
             "rango": "Rango", "conexion": "Conexión"}


def grupo_de(it):
    """Índice en GRUPOS de un material, por la familia de sus datos (chapas, rejillas y mallas aparte de los perfiles)."""
    import re
    at = it.get("atributos") or {}
    fam = at.get("familia", "")
    if fam == "PER":
        return 4 if re.search(r"chapa|rejilla|malla|desplegad", norm(f"{at.get('tipo', '')} {it.get('descripcion', '')}")) else 3
    return next((i for i, (_, fams, _) in enumerate(GRUPOS) if fam in fams), len(GRUPOS) - 1)
