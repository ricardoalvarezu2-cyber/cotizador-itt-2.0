"""Une todas las fuentes de precios de la base en un solo índice ordenado del más reciente al más viejo.

Uso: python herramientas/indice_precios.py
Lee conocimiento/precios/*.csv y escribe conocimiento/precios/indice_precios.csv.
Correrlo después de construir_base.py y consolidar_fichas.py.
"""
import csv
import re
from pathlib import Path

PRECIOS = Path(__file__).resolve().parent.parent / "conocimiento" / "precios"


def fecha_iso(texto: str) -> str:
    """Lleva '25/03/26', 'Cot 25/03/2026' o '2025-06-25' a AAAA-MM-DD; si no reconoce el formato, lo deja igual."""
    m = re.search(r"(\d{3,4})-(\d{2})-(\d{2})", texto or "")
    if m:  # la fuente tiene algún año mal cargado como '025'
        return f"{m.group(1).rjust(4, '2')}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", texto or "")
    if m:
        d, mes, a = m.groups()
        return f"{'20' + a if len(a) == 2 else a}-{int(mes):02d}-{int(d):02d}"
    return texto or ""


def leer(nombre):
    ruta = PRECIOS / nombre
    return list(csv.DictReader(ruta.open(encoding="utf-8"))) if ruta.exists() else []


def main():
    filas = []
    for r in leer("proveedores_2026.csv"):
        if r["precio"]:
            filas.append([r["fecha"], "cotizacion_proveedor_2026", r["proveedor"], "", r["detalle"], r["precio"],
                          r["moneda"], "", r["plazo_entrega"], r["carpeta_cotizacion"]])
    for r in leer("precios_componentes.csv"):
        detalle = " ".join(x for x in (r["descripcion"], r["detalle"], r["dimension"], r["tipo"], r["schedule"],
                                        r["serie"], r["material"], r["norma"]) if x and x != "-")
        filas.append([r["fecha"], "base_componentes_2025", r["proveedor"], r["rubro"], detalle, r["precio_usd"], "USD",
                      r["unidad"], r["plazo_entrega"], r["observacion"]])
    for r in leer("lista_renar_2025-12.csv"):
        filas.append(["2025-12-26", "lista_renard", "Renard", r["categoria"], r["producto"], r["precio_usd"], "USD",
                      r["unidad"], "", f"código {r['codigo']}"])
    for r in leer("stock_2024-11.csv"):
        if r["precio_maestro_usd"] and float(r["precio_maestro_usd"] or 0) > 0:
            filas.append([r["fecha_ultima_compra"] or "2024-11 (sin fecha de compra)", "stock_itt_2024", "stock ITT",
                          r["grupo"], r["descripcion"], r["precio_maestro_usd"], "USD", r["unidad"], "en stock",
                          f"código {r['codigo']}, cantidad {r['cantidad']}"])
    for f in filas:
        f[0] = fecha_iso(f[0])
    filas.sort(key=lambda f: f[0], reverse=True)
    with (PRECIOS / "indice_precios.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fecha", "fuente", "proveedor", "rubro", "descripcion", "precio", "moneda", "unidad",
                    "plazo_entrega", "referencia"])
        w.writerows(filas)
    print(f"indice_precios.csv: {len(filas)} precios")


if __name__ == "__main__":
    main()
