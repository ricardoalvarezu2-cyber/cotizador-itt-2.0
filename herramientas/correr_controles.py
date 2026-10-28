"""Corre la precotización automática en los casos de control y la compara con el costo real (por equipo).

Uso: python herramientas/correr_controles.py   → tabla en pantalla y cotizaciones/controles_resultado.md

Cada caso: cotizaciones/CTRL-*/ con pedido/lista_materiales_plano.csv, cotizacion.json (parámetros) e historico.csv
(costo real). Se excluyen los precios del propio proyecto (y de sus copias en otras carpetas). Sirve para medir si un
cambio en las herramientas mejora o empeora la app: correrlo antes y después.
"""
import csv
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))
CASOS = {"CTRL-F01_INARTECO_FM2_S300": ["TAVAL/40", "INARTECO"],
         "CTRL-T01_SACDE20_TKCHOQUE": ["Sacde/20"],
         "CTRL-C01_PAMPA7_COLECTOR": ["PAMPA ENERGIA/7", "ADICIONAL DE OC Colectores"],
         "CTRL-P01_TAVAL70_PUENTE2": ["TAVAL/70"],
         "CTRL-M01_TECPETROL9_MANIFOLD": ["TECPETROL/9", "TECHINT/12"],
         "CTRL-TS01_TECPETROL13_TRAMPA": ["TECPETROL/13"],
         "CTRL-P02_PAMPA5_PUENTE3": ["PAMPA ENERGIA/5", "PAMPA ENERGIA/7"],
         "CTRL-SK01_YPF28_SKID708": ["YPF/28", "pedidos_web", "COT26-0330"],
         "CTRL-CA01_SACDE18_PIPING": ["Sacde/18"]}


def totales(carpeta):
    """(real materiales, real MO+serv, app materiales, app MO+serv) de comparacion_historico.md."""
    import json
    hist = list(csv.DictReader(open(carpeta / "historico.csv", encoding="utf-8")))
    rm = sum(float(h["total_usd"]) for h in hist if h["grupo"] == "material") or 1e-9  # prefabricado: materiales del cliente
    rs = sum(float(h["total_usd"]) for h in hist if h["grupo"] != "material")
    cot = json.load(open(carpeta / "cotizacion_auto.json", encoding="utf-8"))
    am = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in cot["items"] if i["grupo"] == "material")
    a_s = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in cot["items"] if i["grupo"] != "material")
    sinp = {str(i["pos"]) for i in cot["items"] if not i["fuentes"][0]["precio"]}
    real_sin = sum(float(h["total_usd"]) for h in hist if h["pos"] in sinp)  # lo que la app deja SIN PRECIO (a cotizar)
    return rm, rs, am, a_s, len(sinp), real_sin


def main():
    import precotizar
    import comparar_historico
    filas = ["| Caso | Real | App | Dif. | Dif. sin lo que queda SIN PRECIO | Materiales real / app | MO y servicios real / app | Sin precio (real de esos renglones) |",
             "|---|---|---|---|---|---|---|---|"]
    for caso, excl in CASOS.items():
        c = RAIZ / "cotizaciones" / caso
        precotizar.EXCLUIR[:] = excl
        with redirect_stdout(io.StringIO()):
            precotizar.main(c)
            comparar_historico.main(c)
        rm, rs, am, a_s, sin, real_sin = totales(c)
        d = (am + a_s) / (rm + rs) - 1
        d2 = (am + a_s) / (rm + rs - real_sin) - 1
        filas.append(f"| {caso} | {rm + rs:,.0f} | {am + a_s:,.0f} | {d:+.0%} | {d2:+.0%} | {rm:,.0f} / {am:,.0f} ({am / rm - 1:+.0%}) | "
                     f"{rs:,.0f} / {a_s:,.0f} ({a_s / rs - 1:+.0%}) | {sin} ({real_sin:,.0f}) |")
    precotizar.EXCLUIR[:] = []
    texto = "\n".join(filas)
    print(texto)
    (RAIZ / "cotizaciones" / "controles_resultado.md").write_text(
        "# Casos de control: precotización automática contra el costo real\n\nGenerado por `herramientas/correr_controles.py` "
        "(costo por equipo, USD sin IVA, antes de completar lo que la app marca para revisar).\n\n" + texto + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
