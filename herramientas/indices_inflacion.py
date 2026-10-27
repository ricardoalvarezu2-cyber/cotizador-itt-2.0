"""Arma la tabla mensual de índices para ajustar precios por inflación: conocimiento/costos/indices_ajuste.csv

Uso: python herramientas/indices_inflacion.py

Dos índices, porque los precios de la base están en dólares:
- indice_local_usd = IPC Argentina / dólar BNA vendedor. Mide cuánto cambia en dólares un costo que se paga
  en pesos y sigue la inflación (mano de obra, talleres, servicios locales). Se usa para MO y servicios.
- cpi_eeuu: inflación en dólares de EE.UU. Se usa para materiales cotizados en dólares.

Los meses que no son dato se completan por interpolación geométrica entre datos (columna "origen").
Para agregar un mes nuevo: sumar el dato en ANCLAS con su fuente y volver a correr el script.
"""
import csv
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "conocimiento" / "costos" / "indices_ajuste.csv"

# IPC Argentina (INDEC), base oct-2024 = 100. (mes, valor, fuente)
_JUL24 = 100 / (1.042 * 1.035 * 1.027)
IPC = [
    ((2024, 1), _JUL24 / 1.040 / 1.046 / 1.042 / 1.088 / 1.110 / 1.132, "INDEC mensual 2024: feb 13,2%, mar 11,0%, abr 8,8%, may 4,2%, jun 4,6%, jul 4,0%"),
    ((2024, 2), _JUL24 / 1.040 / 1.046 / 1.042 / 1.088 / 1.110, "INDEC mensual 2024"),
    ((2024, 3), _JUL24 / 1.040 / 1.046 / 1.042 / 1.088, "INDEC mensual 2024"),
    ((2024, 4), _JUL24 / 1.040 / 1.046 / 1.042, "INDEC mensual 2024"),
    ((2024, 5), _JUL24 / 1.040 / 1.046, "INDEC mensual 2024"),
    ((2024, 6), _JUL24 / 1.040, "INDEC mensual 2024"),
    ((2024, 7), _JUL24, "INDEC: ago-24 4,2%, sep-24 3,5%, oct-24 2,7% mensual"),
    ((2024, 10), 100.0, "Base"),
    ((2025, 10), 131.3, "INDEC: 31,3% interanual a oct-2025 (12/11/2025)"),
    ((2025, 12), 171.2 / 1.236, "Derivado: acumulado ene-sep 2026 23,6% (INDEC 13/10/2026)"),
    ((2026, 9), 131.3 / 1.023 * 1.334, "INDEC: 33,4% interanual a sep-2026; oct-25 2,3% mensual"),
    ((2026, 10), 131.3 / 1.023 * 1.334 * 1.019, "ESTIMADO: oct-2026 igual a sep-2026 (1,9%), sin dato publicado"),
]
# Dólar: PROMEDIO MENSUAL del oficial BNA billete, precio de venta (decisión de Matías, 27/10/2026), de
# conocimiento/costos/dolar_mensual.csv (datos diarios; se actualiza con herramientas/dolar_mensual.py).
# Es lo que usan los documentos (BNA vendedor) y, para precios en pesos llevados a hoy, el dólar del pasado se cancela.
DOLAR_MENSUAL = RAIZ / "conocimiento" / "costos" / "dolar_mensual.csv"


def tc_mensual():
    import csv as _csv
    return [((int(r["mes"][:4]), int(r["mes"][5:7])), float(r["oficial_promedio"]),
             f"promedio BNA billete vendedor ({r['dias_con_dato']} días, último {r['ultimo_dato']})")
            for r in _csv.DictReader(open(DOLAR_MENSUAL, encoding="utf-8")) if r["oficial_promedio"]]


# CPI EE.UU. (BLS), base oct-2024 = 100
_JUL24C = 100 / 1.003 / 1.002 / 1.002
CPI = [
    ((2024, 1), _JUL24C / 1.002 / 0.999 / 1.000 / 1.003 / 1.004 / 1.004, "BLS mensual 2024: feb 0,4%, mar 0,4%, abr 0,3%, may 0,0%, jun -0,1%, jul 0,2%"),
    ((2024, 7), _JUL24C, "BLS: ~0,2%-0,3% mensual ago-oct 2024"),
    ((2024, 10), 100.0, "Base"),
    ((2025, 9), 100 * 1.03 ** (11 / 12), "BLS: ~3,0% interanual a sep-2025"),
    ((2026, 9), 100 * 1.03 ** (11 / 12) * 1.037, "BLS: 3,7% interanual a sep-2026 (14/10/2026)"),
    ((2026, 10), 100 * 1.03 ** (11 / 12) * 1.037 * 1.037 ** (1 / 12), "ESTIMADO: oct-2026 al ritmo de 3,7% anual"),
]


def meses(desde, hasta):
    y, m = desde
    while (y, m) <= hasta:
        yield (y, m)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def ordinal(ym):
    return ym[0] * 12 + ym[1]


def serie(anclas, inicio, fin):
    out = {}
    for ym in meses(inicio, fin):
        exacto = [a for a in anclas if a[0] == ym]
        if exacto:
            out[ym] = (exacto[0][1], "dato: " + exacto[0][2])
            continue
        antes = [a for a in anclas if ordinal(a[0]) < ordinal(ym)]
        despues = [a for a in anclas if ordinal(a[0]) > ordinal(ym)]
        if not antes or not despues:
            continue
        (y0, v0, _), (y1, v1, _) = antes[-1], despues[0]
        t = (ordinal(ym) - ordinal(y0)) / (ordinal(y1) - ordinal(y0))
        out[ym] = (v0 * (v1 / v0) ** t, "interpolado")
    return out


def main():
    ini, fin = (2024, 1), (2026, 10)
    ipc, tc, cpi = serie(IPC, ini, fin), serie(tc_mensual(), ini, fin), serie(CPI, ini, fin)
    base_local = ipc[(2024, 10)][0] / tc[(2024, 10)][0]
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mes", "ipc_argentina", "dolar_bna", "indice_local_usd", "cpi_eeuu", "origen_ipc", "origen_dolar", "origen_cpi"])
        for ym in meses(ini, fin):
            local = ipc[ym][0] / tc[ym][0] / base_local * 100
            w.writerow([date(*ym, 1).isoformat(), round(ipc[ym][0], 3), round(tc[ym][0], 2), round(local, 3),
                        round(cpi[ym][0], 3), ipc[ym][1], tc[ym][1], cpi[ym][1]])
    print(SALIDA)


if __name__ == "__main__":
    main()
