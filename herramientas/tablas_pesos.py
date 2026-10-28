"""Peso y superficie de caños por diámetro y espesor: conocimiento/tecnico/canos_peso_superficie.csv

Uso: python herramientas/tablas_pesos.py

Sale de conocimiento/tecnico/factores_soldadura.csv (diámetro exterior y espesor de ASME B36.10 para cada NPS y
schedule) con las fórmulas de la norma, sin datos de afuera:
  peso acero al carbono (kg/m) = 0,0246615 × (OD − e) × e        (OD y e en mm; densidad 7,85 kg/dm³; ASME B36.10)
  peso inoxidable (kg/m)       = peso carbono × 1,0141            (densidad 7,96 kg/dm³ de los austeníticos 304/316)
  superficie exterior (m²/m)   = π × OD / 1000                    (para pintura exterior)
  superficie interior (m²/m)   = π × (OD − 2e) / 1000             (para revestimiento interior)
  volumen interior (litros/m)  = π/4 × (OD − 2e)² / 1000          (para prueba hidráulica)
Sirve para calcular los kg de un equipo (flete, galvanizado, fabricación por kg) y los m² a pintar.
"""
import csv
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "conocimiento" / "tecnico" / "factores_soldadura.csv"
SALIDA = RAIZ / "conocimiento" / "tecnico" / "canos_peso_superficie.csv"


def main():
    filas = []
    for r in csv.DictReader(open(ORIGEN, encoding="utf-8")):
        od, e = float(r["diam_ext_mm"]), float(r["espesor_mm"])
        kg = 0.0246615 * (od - e) * e
        di = od - 2 * e
        filas.append({"dn_pulg": r["dn_pulg"], "diam_ext_mm": od, "schedule": r["schedule"], "clase": r["clase"], "espesor_mm": e,
                      "diam_int_mm": round(di, 2), "kg_m_carbono": round(kg, 3), "kg_m_inoxidable": round(kg * 1.0141, 3),
                      "m2_m_exterior": round(math.pi * od / 1000, 4), "m2_m_interior": round(math.pi * di / 1000, 4),
                      "litros_m_interior": round(math.pi / 4 * di ** 2 / 1000, 3)})
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"{SALIDA.relative_to(RAIZ)}: {len(filas)} combinaciones de diámetro y espesor")


if __name__ == "__main__":
    main()
