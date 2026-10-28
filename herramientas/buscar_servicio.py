"""Busca un servicio o mano de obra en el catálogo de servicios: último precio confiable, tarifa unitaria, alcance (incluye / no incluye),
fecha, proveedor y la ruta de dónde salió.

Uso:
  python herramientas/buscar_servicio.py "soldadura piping por pulgada"
  python herramientas/buscar_servicio.py "radiografia" --hoja ensayos --top 5
  python herramientas/buscar_servicio.py "armado skid por kg" --hoja fabricacion
  python herramientas/buscar_servicio.py "flete camion Neuquen" --hoja transporte
  python herramientas/buscar_servicio.py "hora hombre soldador"

--hoja filtra por rubro (basta un pedazo del nombre: mo, fabricacion, soldadura, ensayos, pintura, transporte, ingenieria, otros).
Los resultados se ordenan por parecido con el texto; con la misma coincidencia salen primero los que tienen tarifa unitaria
(comparable entre equipos) y después los más nuevos. Un servicio "sin precio confiable" (todos sus valores son de la época del
cepo con el dólar sin aclarar) se muestra con el valor descartado solo como referencia: hay que pedir cotización.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm  # noqa: E402

PRECIOS = Path(__file__).resolve().parent.parent / "conocimiento" / "precios"
SINONIMOS = {"rx": "radiografia", "radiografias": "radiografia", "hh": "hora hombre", "pulg": "pulgada", "pulgadas": "pulgada", "pulg-eq": "pulgada",
             "flete": "transporte", "camion": "semirremolque", "ph": "prueba hidraulica", "end": "ensayos", "ensayo": "ensayos", "granallado": "granallado",
             "arenado": "granallado", "mo": "mano de obra", "soldar": "soldadura", "cañeria": "piping", "caneria": "piping", "canerias": "piping",
             "ingenieria": "ingenieria", "planos": "ingenieria", "lp": "liquidos penetrantes", "pm": "particulas magnetizables", "us": "ultrasonido"}
VACIAS = {"de", "del", "la", "el", "los", "las", "por", "para", "con", "y", "en", "a", "un", "una", "tercero", "terceros"}


def tokens(t):
    t = norm(t)
    out = []
    for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", t):
        w = SINONIMOS.get(w, w)
        out += [x for x in w.split() if x not in VACIAS]
    return out


def ficha(r, i, puntaje):
    sin = r["ultimo_precio_usd"] == ""
    print(f"\n{i}. {r['codigo']} · {r['hoja']} · {r['servicio']}")
    if sin:
        print("   SIN PRECIO CONFIABLE: pedir cotización." + (f" Referencia descartada (no usar): USD {float(r['referencia_descartada_usd']):,.2f} ({r['unidad']}) · {r['fecha_referencia_descartada']}"
                                                          if r["referencia_descartada_usd"] else ""))
    else:
        print(f"   Último precio: USD {float(r['ultimo_precio_usd']):,.2f} {('por ' + r['unidad'][4:]) if r['unidad'].startswith('USD/') else '(' + r['unidad'] + ')'} sin IVA · {r['fecha_ultimo_precio'] or 'sin fecha'} · {r['proveedor']}")
        if r["tarifa_unitaria_usd"]:
            print(f"   Tarifa unitaria: USD {float(r['tarifa_unitaria_usd']):,.2f} por {r['unidad_tarifa'][4:]} "
                  f"(ajustada a hoy: USD {float(r['tarifa_ajustada_hoy_usd'] or 0):,.2f}) · alcance comparable: {r['alcance_comparable']}")
        if r["precio_ajustado_hoy_usd"] != "":
            print(f"   Precio ajustado a hoy (costo local en USD): USD {float(r['precio_ajustado_hoy_usd']):,.2f}")
    if r["precios_en_historial"] and int(r["precios_en_historial"]) > 1 and r["precio_min_usd"] != "":
        print(f"   {r['precios_en_historial']} precio(s) en el historial (confiables entre {float(r['precio_min_usd']):,.2f} y {float(r['precio_max_usd']):,.2f})")
    print(f"   {r['descripcion'][:200]}")
    if r["equipo_referencia"]:
        print(f"   Equipo de referencia: {r['equipo_referencia']}" + (f" · lugar: {r['lugar']}" if r["lugar"] else ""))
    if r["incluye"]:
        print(f"   Incluye: {r['incluye'][:200]}")
    if r["no_incluye"]:
        print(f"   No incluye: {r['no_incluye'][:200]}")
    if r["alerta"]:
        print(f"   ALERTA: {r['alerta']}")
    print(f"   Origen: {r['ruta_origen']}" + (f" · {r['archivo_origen']}" if r["archivo_origen"] else ""))
    print(f"   En el repo: {r['ruta_repo']}")


def buscar(texto, hoja="", top=8, excluir=()):
    """Devuelve [(puntaje, fila)] ordenado; usado también por los tests."""
    q = tokens(texto)
    filas = list(csv.DictReader(open(PRECIOS / "catalogo_servicios.csv", encoding="utf-8")))
    if hoja:
        h = norm(hoja)
        filas = [r for r in filas if h in norm(r["hoja"])]
    res = []
    for r in filas:
        if any(x.lower() in (r["ruta_origen"] + " " + r["archivo_origen"] + " " + r["ruta_repo"]).lower() for x in excluir):
            continue  # casos de control: el propio proyecto no puede ser su referencia
        campos = tokens(r["servicio"] + " " + r["descripcion"] + " " + r["equipo_referencia"] + " " + r["hoja"] + " " + r["proveedor"])
        titulo = set(tokens(r["servicio"] + " " + r["unidad_tarifa"]))
        s = 0.0
        for w in q:
            if w in titulo:
                s += 2
            elif w in campos:
                s += 1
        if not q or s == 0:
            continue
        s = s / (2 * len(q))
        res.append((s, r["alcance_comparable"] == "sí", r["fecha_ultimo_precio"] or "", r))
    res.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return [(x[0], x[3]) for x in res[:top]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("texto")
    ap.add_argument("--hoja", default="", help="rubro (pedazo del nombre)")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--excluir", action="append", default=[], help="no mostrar servicios cuyo origen contenga este texto (repetible)")
    q = ap.parse_args()
    res = buscar(q.texto, q.hoja, q.top, q.excluir)
    if not res:
        print("No hay servicios parecidos en el catálogo. Pedir cotización al proveedor.")
        return
    print(f"Lectura: {' '.join(tokens(q.texto))}" + (f" · rubro: {q.hoja}" if q.hoja else ""))
    for i, (p, r) in enumerate(res, 1):
        ficha(r, i, p)


if __name__ == "__main__":
    main()
