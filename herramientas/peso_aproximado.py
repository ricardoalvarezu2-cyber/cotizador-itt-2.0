"""Peso APROXIMADO de los materiales que no tienen peso en tabla (pedido de Matías, 29-10-2026): volumen × densidad.

Uso: python herramientas/peso_aproximado.py   → recalibra conocimiento/tecnico/factores_peso_aproximado.csv
     (controles_tablas.peso_item lo usa solo cuando ninguna tabla tiene el peso; el resultado dice "APROXIMADO")

Criterios (todos marcados como aproximados, nunca reemplazan un peso de tabla):
- Accesorios a tope (B16.9) de un schedule sin tabla (ej. tee 8" Sch 60): peso = kg/m del caño de ese Ø y schedule (ASME B36.10)
  × diámetro exterior × "largo equivalente en diámetros" del tipo. El largo equivalente se calibra con las mismas tablas de
  accesorios (mediana de peso_tabla ÷ (kg/m × OD) de los renglones sin observaciones): codo 90 RL ≈ 2,24 (la geometría da 2,36),
  codo 45 ≈ 1,18, tee ≈ 3,04, etc. En una tee o reducción se toma el Ø mayor.
- Forjados (B16.11) de una clase sin tabla: el peso del mismo tipo, Ø y extremo en la clase más cercana.
- Válvulas sin peso para su serie: la misma válvula (tipo y Ø) en la serie más cercana de la lista Taval.
- Juntas espiraladas y dieléctricas: anillo de Ø interior = OD del caño, ancho 25 mm, espesor de la descripción (4,5 mm por
  defecto); densidad 7.900 (espiralada, acero inoxidable con grafito) o 1.800 kg/m³ (dieléctrica, fibra).
- Termovaina bridada: el peso de una brida ciega de su Ø y serie.
Instrumentos (manómetros, termómetros, transmisores) siguen sin peso: no tienen una geometría que se pueda estimar.
"""
import csv
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm  # noqa: E402

TEC = Path(__file__).resolve().parent.parent / "conocimiento" / "tecnico"
FACTORES = TEC / "factores_peso_aproximado.csv"
_F = {}


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def kgm_od(canos, dn, clase):
    """(kg/m de acero al carbono, OD en m) del caño de ese Ø y schedule/clase, o None."""
    for r in canos:
        if abs(float(r["dn_pulg"]) - dn) < 1e-6 and clase and (r["schedule"] == clase or r["clase"] == clase):
            return float(r["kg_m_carbono"]), float(r["diam_ext_mm"]) / 1000
    return None


def calibrar():
    import controles_tablas as ct
    canos = leer(TEC / "canos_peso_superficie.csv")
    rat = {}
    for r in ct.leer_acc():
        if r["extremos"] != "BW" or r["nota"].startswith("ATENCION") or not r["peso_kg"]:
            continue
        k = kgm_od(canos, float(r["dn_pulg"]), r["schedule_o_clase"])
        if k:
            rat.setdefault(r["tipo"], []).append(float(r["peso_kg"]) / (k[0] * k[1]))
    filas = [[t, round(statistics.median(v), 3), len(v), round(statistics.quantiles(v, n=4)[0], 3), round(statistics.quantiles(v, n=4)[2], 3)]
             for t, v in sorted(rat.items()) if len(v) >= 6]
    with open(FACTORES, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tipo", "largo_eq_diametros", "muestras", "p25", "p75"])
        w.writerows(filas)
    print(f"{FACTORES.relative_to(TEC.parent.parent)}: {len(filas)} tipos")


def factores():
    if not _F:
        _F.update({r["tipo"]: float(r["largo_eq_diametros"]) for r in leer(FACTORES)})
    return _F


def schedule_de(it, at):
    """Schedule del renglón: atributos, datos del plano o la especificación ("Plano: 8\" · 60 · ASTM A234 WPB · BW")."""
    from precotizar import sch_de
    for c in [at.get("schedule", ""), (it.get("plano") or {}).get("serie_sch", ""), *str(it.get("especificacion", "")).split("·")]:
        s = sch_de(str(c).strip())
        if s:
            return s
    return ""


def clase_num(c):
    m = re.search(r"\d+", str(c))
    return int(m.group(0)) if m else 0


def estimar(it, at, fam, tipo, canos, bridas, acc, valv, pulg):
    """(kg, None, 'APROXIMADO: …') o (None, None, motivo). `tipo` es el tipo de accesorio que buscó peso_item ('' si no aplica)."""
    dn = pulg(at.get("diametro", ""))
    d = norm(f"{it['descripcion']} {it.get('especificacion', '')}")
    bw = fam == "ABW" or (fam == "AFO" and "BW" in str(at.get("extremos", "")).upper())
    tipo_bw = {"codo_90": "codo_90_radio_largo"}.get(tipo, tipo)
    if bw and dn and tipo_bw in factores():
        tipo = tipo_bw
        sch = schedule_de(it, at) or "STD"
        k = kgm_od(canos, dn, sch) or (kgm_od(canos, dn, "STD") if sch in ("40",) else None)
        if k:
            L = factores()[tipo]
            return k[0] * k[1] * L, None, f"APROXIMADO: {tipo} {dn:g}\" sch {sch} = caño {k[0]:.2f} kg/m × OD {k[1] * 1000:.1f} mm × {L:g} diámetros"
    if fam == "AFO" and dn and tipo and not bw:
        ext = "SW" if "SW" in at.get("extremos", "") else "NPT"
        cl = clase_num(at.get("serie", "") or "3000")
        cand = [r for r in acc if r["tipo"] == tipo and abs(float(r["dn_pulg"]) - dn) < 1e-6 and r["extremos"] == ext and r["peso_kg"] and not r["dn2_pulg"]
                and "no sirve" not in r["nota"]]
        if cand:
            r = min(cand, key=lambda r: (abs(clase_num(r["schedule_o_clase"]) - cl), r["nota"].startswith("ATENCION")))
            return float(r["peso_kg"]), None, f"APROXIMADO: {tipo} {dn:g}\" {ext} con el peso de la clase {r['schedule_o_clase']} (no hay tabla para {cl})"
    if fam == "VAL" and dn:
        t = d
        tipos = ["ESFERICA" if "esferica" in t else "RETENCION" if "retencion" in t else "GLOBO" if "globo" in t else
                 "ESCLUSA" if re.search(r"esclusa|compuerta", t) else ""]
        if tipos[0]:
            cl = clase_num(at.get("serie", ""))
            cand = [r for r in valv if r["tipo"].startswith(tipos[0]) and abs(float(r["dn_pulg"]) - dn) < 0.01 and not r["nota"].startswith("pesa menos")]
            if cand:
                r = min(cand, key=lambda r: abs(clase_num(r["serie"]) - cl))
                return float(r["kg"]), None, f"APROXIMADO: {r['tipo'].lower()} {dn:g}\" con el peso de la serie {r['serie']} (Taval Lista 30)"
    if fam == "JUN" and dn and re.search(r"junta", d):
        k = kgm_od(canos, dn, "STD") or kgm_od(canos, dn, "40")
        if k:
            m = re.search(r"esp\.?\s*(\d+(?:[.,]\d+)?)\s*mm", d)
            e = float(m.group(1).replace(",", ".")) / 1000 if m else 0.0045
            rho = 1800 if re.search(r"dielectr|aramid|fibra|nbr", d) else 7900
            di, de = k[1], k[1] + 0.05
            kg = 3.14159265 / 4 * (de ** 2 - di ** 2) * e * rho
            return kg, None, f"APROXIMADO: junta anillo Ø {di * 1000:.0f}–{de * 1000:.0f} mm × {e * 1000:g} mm × {rho} kg/m³"
    if re.search(r"termovaina|vaina|termopozo", d) and re.search(r"brid", d):
        m = re.search(r"(\d+(?: \d/\d)?)\"", it["descripcion"] + " " + it.get("especificacion", ""))
        from controles_tablas import frac_pulg
        dnv = frac_pulg(m.group(1)) if m else None
        serie = re.search(r"(150|300|600|900|1500|2500)\s*(?:lb|#)", d)
        serie = serie.group(1) if serie else "300"
        dnv = dnv or 1.5
        r = next((r for r in bridas if r["tipo"] == "ciega" and abs(float(r["dn_pulg"]) - dnv) < 1e-6 and r["serie"] == serie), None)
        if r:
            return float(r["peso_kg"]), None, f"APROXIMADO: termovaina con el peso de una brida ciega {dnv:g}\" #{serie}"
    return None, None, ""


if __name__ == "__main__":
    calibrar()
