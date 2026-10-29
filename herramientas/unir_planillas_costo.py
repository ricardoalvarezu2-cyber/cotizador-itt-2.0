"""Une la extracción de las planillas de costo (etapa 2) y la prepara para los catálogos.

Uso: python herramientas/unir_planillas_costo.py
     (después: python herramientas/catalogo_materiales.py y python herramientas/catalogo_servicios.py)

Entrada: conocimiento/precios/planillas_costo_items_parte*.csv (1 a 3: lectura con IA, ver etapa2_planillas_instrucciones.md; 4: PC0 YPF Lic 69343).
Salidas:
  conocimiento/precios/planillas_costo_items.csv     todo junto, sin renglones repetidos, con la ruta completa del original
  conocimiento/precios/servicios_desde_planillas.csv la MO y los servicios con el formato de servicios_extraidos.csv
Criterio para que un renglón entre a un catálogo (los demás quedan solo en planillas_costo_items.csv):
  - tiene costo unitario, no es "otro" (subtotales) y la lectura no es de confianza baja;
  - no es un estimado de la planilla (proveedor_o_criterio sin "estimad");
  - la regla del cepo, el IVA y la conversión de moneda los aplica cada catálogo.
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm  # noqa: E402
from numeros import precio_csv  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PRECIOS = RAIZ / "conocimiento" / "precios"
INDICE = RAIZ / "conocimiento" / "comercial" / "indice_proyectos.csv"
TEXTOS = "fuentes_originales/ofertas_texto/"

HOJA = {"armado": "Fabricación y armado (terceros)", "soldadura": "Soldadura y piping", "END": "Ensayos y END",
        "prueba hidráulica": "Ensayos y END", "pintura": "Pintura y revestimientos", "galvanizado": "Pintura y revestimientos",
        "transporte": "Transporte e izaje", "ingeniería": "Ingeniería, calidad e inspección",
        "calidad/dossier": "Ingeniería, calidad e inspección"}
UNIDAD_TARIFA = {"hora": "USD/hora", "hs": "USD/hora", "hh": "USD/hora", "pulg-eq": "USD/pulg-eq", "pulg": "USD/pulg-eq", "kg": "USD/kg",
                 "m2": "USD/m2", "placa": "USD/placa", "metro": "USD/m", "m": "USD/m", "soldadura": "USD/junta"}


def ubicar(r):
    """(carpeta relativa a ofertas_texto, archivo sin .txt) del original; los subagentes anotaron la ruta de formas distintas."""
    cands = []
    for c in (r["carpeta"], f"{r['carpeta_proyecto']}/{r['carpeta']}", r["carpeta_proyecto"]):
        c = c[len(TEXTOS):] if c.startswith(TEXTOS) else c
        for a in (r["archivo"], Path(r["archivo"]).name):
            a = a[len(TEXTOS):] if a.startswith(TEXTOS) else a
            cands += [(c, a), ("", a)]
    for c, a in cands:
        f = RAIZ / TEXTOS / c / a
        for g in (f, Path(str(f) + ".txt")):
            if g.is_file():
                rel = g.relative_to(RAIZ / TEXTOS)
                return str(rel.parent), rel.name[:-4] if rel.name.endswith(".txt") else rel.name
    return f"{r['carpeta_proyecto']}/{r['carpeta']}".strip("/"), r["archivo"]


def usable(r):
    try:
        if float(r["costo_unitario"]) <= 0:  # formato de máquina (texto de Excel): el punto es decimal
            return False
    except ValueError:
        return False
    return (r["costo_unitario"].strip() and r["tipo"] != "otro" and r["confianza"].strip().lower() != "baja"
            and "estimad" not in norm(r["proveedor_o_criterio"]))


def main():
    carpetas = {r["id"]: r["carpeta_textos"] for r in csv.DictReader(open(INDICE, encoding="utf-8"))}
    filas, vistos = [], set()
    for n in sorted(int(p.stem.rsplit("parte", 1)[1]) for p in PRECIOS.glob("planillas_costo_items_parte*.csv")):
        ruta = PRECIOS / f"planillas_costo_items_parte{n}.csv"
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            k = (r["proyecto"], norm(r["descripcion"]), r["cantidad"], r["unidad"], r["costo_unitario"], r["tipo"])
            if k in vistos:
                continue  # la misma fila en otra revisión o copia del archivo
            vistos.add(k)
            base = carpetas.get(r["proyecto"], "")
            filas.append({**r, "costo_unitario": precio_csv(r["costo_unitario"]), "parte": n, "carpeta_proyecto": base[len(TEXTOS):] if base.startswith(TEXTOS) else base,
                          "usable_catalogo": "si" if usable(r) else "no"})
    cols = list(filas[0].keys())
    with open(PRECIOS / "planillas_costo_items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)
    serv = []
    for r in filas:
        if r["usable_catalogo"] != "si" or r["tipo"] not in ("mo", "servicio"):
            continue
        u = norm(r["unidad"]).strip()
        tarifa = UNIDAD_TARIFA.get(u, "")
        serv.append({"hoja": HOJA.get(r["rubro"], "Otros servicios" if r["tipo"] == "servicio" else "Fabricación y armado (terceros)"),
                     "servicio": r["descripcion"][:120], "descripcion": r["descripcion"], "proveedor": r["proveedor_o_criterio"] or "planilla de costo ITT",
                     "fecha": r["fecha_planilla"], "precio": r["costo_unitario"], "moneda": r["moneda"] or "USD", "iva_origen": r["iva_origen"] or "no dice",
                     "unidad": tarifa or "global", "magnitud": "", "equipo_referencia": r["proyecto"], "lugar": "",
                     "incluye": "", "no_incluye": "", "carpeta_origen": ubicar(r)[0], "archivo_origen": ubicar(r)[1],
                     "texto_original": r["cita"], "confianza": r["confianza"],
                     "nota": "; ".join(x for x in [f"planilla de costo ITT ({r['ubicacion']})", f"unidad original: {r['unidad']}" if not tarifa else "",
                                                   r["nota"]] if x),
                     "tc_documento": r["tc_explicito"]})
    with open(PRECIOS / "servicios_desde_planillas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(serv[0].keys()))
        w.writeheader()
        w.writerows(serv)
    n_mat = sum(1 for r in filas if r["usable_catalogo"] == "si" and r["tipo"] == "material")
    print(f"planillas_costo_items.csv: {len(filas)} renglones sin repetir · para catálogos: {n_mat} materiales, {len(serv)} MO y servicios")


if __name__ == "__main__":
    main()
