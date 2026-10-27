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
IPC = [
    ((2024, 7), 100 / (1.042 * 1.035 * 1.027), "INDEC: ago-24 4,2%, sep-24 3,5%, oct-24 2,7% mensual"),
    ((2024, 10), 100.0, "Base"),
    ((2025, 10), 131.3, "INDEC: 31,3% interanual a oct-2025 (12/11/2025)"),
    ((2025, 12), 171.2 / 1.236, "Derivado: acumulado ene-sep 2026 23,6% (INDEC 13/10/2026)"),
    ((2026, 9), 131.3 / 1.023 * 1.334, "INDEC: 33,4% interanual a sep-2026; oct-25 2,3% mensual"),
    ((2026, 10), 131.3 / 1.023 * 1.334 * 1.019, "ESTIMADO: oct-2026 igual a sep-2026 (1,9%), sin dato publicado"),
]
# Dólar BNA vendedor, fin de mes o último dato del mes
TC = [
    ((2024, 7), 965.0, "APROXIMADO: BNA vendedor fin de jul-2024"),
    ((2024, 10), 1011.5, "BNA 31/10/2024 (dolarhistorico.com)"),
    ((2025, 10), 1475.0, "BNA 31/10/2025 (dolarhistorico.com)"),
    ((2025, 12), 1480.0, "BNA 30/12/2025 (mdzol.com)"),
    ((2026, 3), 1480.0 * 0.964, "Derivado: -3,6% nominal en el 1er trimestre 2026 (Sistémica / iProfesional)"),
    ((2026, 10), 1550.0, "BNA 23/10/2026 (dolarhistorico.com)"),
]
# CPI EE.UU. (BLS), base oct-2024 = 100
CPI = [
    ((2024, 7), 100 / 1.003 / 1.002 / 1.002, "BLS: ~0,2%-0,3% mensual ago-oct 2024"),
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
    ini, fin = (2024, 7), (2026, 10)
    ipc, tc, cpi = serie(IPC, ini, fin), serie(TC, ini, fin), serie(CPI, ini, fin)
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
