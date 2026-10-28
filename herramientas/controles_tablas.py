"""Controles de una cotización con las tablas de apoyo: kilos y m², plazos de material y marcas del cliente.

Uso: python herramientas/controles_tablas.py cotizaciones/<carpeta>
     (lo corre también armar_cotizacion.py al final)

Genera <carpeta>/controles_tablas.md y avisa en pantalla. No cambia precios: es información para revisar.
1. Kilos y m² (por equipo): caños y niples con conocimiento/tecnico/canos_peso_superficie.csv (calculado, ASME B36.10);
   bridas y accesorios con bridas_peso.csv y accesorios_peso.csv (borrador). Sirve para flete, galvanizado, fabricación
   por kg y m² de pintura. Lo que no tiene tabla (válvulas, instrumentos, juntas) queda "sin dato".
2. Plazos: por cada material, el plazo típico y máximo de su rubro en conocimiento/comercial/plazos_proveedores.csv.
   Avisa si el plazo típico (sin stock) de algún rubro supera el plazo ofrecido.
3. Marcas: si el cliente (o el cliente final) tiene marcas en conocimiento/comercial/marcas_aprobadas.csv, lista las del
   rubro de cada ítem para controlar contra el pliego.
"""
import csv
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_materiales import atributos, expandir, familia_de  # noqa: E402
from indice_proyectos import norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TEC = RAIZ / "conocimiento" / "tecnico"
COM = RAIZ / "conocimiento" / "comercial"


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def pulg(d):
    try:
        return float(str(d).replace('"', ""))
    except ValueError:
        return None


def sch_tabla(sch, dn):
    """Schedule del ítem → columna de las tablas de accesorios (STD/XS/160/XXS)."""
    s = (sch or "").upper()
    if s in ("40", "STD") and (dn or 0) <= 10:
        return "STD"
    if s in ("80", "XS") and (dn or 0) <= 8:
        return "XS"
    return s


def peso_item(it, at, fam, canos, bridas, acc):
    """(kg por unidad o por metro, m² por unidad o por metro, fuente) o (None, None, motivo)."""
    dn = pulg(at.get("diametro", ""))
    sch = at.get("schedule", "")
    if fam in ("CAN", "NIP") and dn:
        fila = next((r for r in canos if pulg(r["dn_pulg"]) == dn and (r["schedule"] == sch or r["clase"] == sch.upper())), None)
        if not fila:
            return None, None, f"caño {dn:g}\" sin schedule reconocido"
        kg, m2 = float(fila["kg_m_carbono"]), float(fila["m2_m_exterior"])
        if "inox" in norm(at.get("material", "")) or "316" in at.get("material", "") or "304" in at.get("material", ""):
            kg = float(fila["kg_m_inoxidable"])
        if fam == "NIP" or it["unidad"] != "m":
            largo = re.search(r"(\d[\d.]*)\s?mm", norm(it["descripcion"] + " " + it.get("especificacion", "")))
            if not largo:
                return None, None, "niple sin largo"
            l = float(largo.group(1).replace(".", "")) / 1000
            return kg * l, m2 * l, f"caño {dn:g}\" sch {sch} × {l:g} m (ASME B36.10, calculado)"
        return kg, m2, f"caño {dn:g}\" sch {sch} por metro (ASME B36.10, calculado)"
    if fam == "BRI" and dn and at.get("serie"):
        tipo = {"wn": "WN", "so": "SO", "ciega": "ciega", "sw": "SW", "roscada": "roscada", "lj": "LJ"}.get(at.get("tipo", ""), "")
        fila = next((r for r in bridas if r["tipo"] == tipo and pulg(r["dn_pulg"]) == dn and r["serie"] == at["serie"]
                     and "no usar" not in r["nota"]), None)
        if fila:
            return float(fila["peso_kg"]), None, f"brida {tipo} {dn:g}\" #{at['serie']} (B16.5, borrador)"
    if fam in ("ABW", "AFO") and dn:
        t = at.get("tipo", "")
        mapa = {"codo 90": "codo_90_radio_largo", "codo radio corto 90": "codo_90_radio_corto", "codo 45": "codo_45", "tee": "tee_recta",
                "reduccion concentrica": "reduccion_concentrica_excentrica", "reduccion excentrica": "reduccion_concentrica_excentrica",
                "reduccion": "reduccion_concentrica_excentrica", "casquete": "casquete", "cupla": "cupla", "media cupla": "media_cupla",
                "tapon": "tapon_hexagonal", "buje": "buje_hexagonal"}
        if fam == "AFO" and t == "codo 90":
            mapa["codo 90"] = "codo_90"
        tipo = mapa.get(t, "")
        if fam == "ABW":
            clase, ext = sch_tabla(sch, dn), "BW"
        else:
            clase = at.get("serie", "") or "3000"
            ext = "SW" if "SW" in at.get("extremos", "") else "NPT"
        d2 = pulg(at.get("diametro2", "")) if at.get("diametro2") else None
        cand = [r for r in acc if r["tipo"] == tipo and pulg(r["dn_pulg"]) == dn and r["extremos"] == ext and "no sirve" not in r["nota"]
                and (r["schedule_o_clase"] == clase or (tipo.startswith(("tapon", "buje")) and r["schedule_o_clase"] == "3000/6000"))
                and (d2 is None or pulg(r["dn2_pulg"]) == d2)]
        if cand:
            return float(cand[0]["peso_kg"]), None, f"{tipo} {dn:g}\" {clase} {ext} ({cand[0]['norma']}, borrador)"
        return None, None, f"sin tabla para {t} {dn:g}\" {clase}"
    return None, None, "sin tabla (válvula, instrumento, junta u otro)"


RUBRO_PLAZO = [("VAL", "esferica", "válvula esférica"), ("VAL", "retencion", "retención"), ("VAL", "aguja", "aguja/bloqueo y purga"),
               ("VAL", "bloqueo", "aguja/bloqueo y purga"), ("VAL", "seguridad", "PSV"), ("VAL", "alivio", "PSV"), ("VAL", "control", "válvula de control"),
               ("INS", "", "instrumento"), ("JUN", "esparrago", "bulonería"), ("JUN", "tuerca", "bulonería"), ("JUN", "", "junta"), ("CAN", "", "caño"),
               ("NIP", "", "caño"), ("BRI", "", "brida"), ("ABW", "", "accesorio BW"), ("AFO", "", "accesorio forjado"), ("PER", "", "chapa/perfil")]
RUBRO_MARCA = [("VAL", "esferica", "válvula esférica"), ("VAL", "retencion", "retención"), ("VAL", "bloqueo", "bloqueo y purga"),
               ("VAL", "seguridad", "PSV"), ("INS", "manometro", "instrumento de presión"), ("INS", "transmisor", "transmisor"),
               ("INS", "caudal", "caudalímetro"), ("CAN", "", "caño"), ("NIP", "", "caño"), ("BRI", "", "brida"), ("ABW", "", "accesorio"),
               ("AFO", "", "accesorio")]


def rubro(tabla, fam, t):
    return next((r for f, clave, r in tabla if f == fam and clave in t), None)


def main(carpeta):
    carpeta = Path(carpeta)
    c = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    canos, bridas, acc = leer(TEC / "canos_peso_superficie.csv"), leer(TEC / "bridas_peso.csv"), leer(TEC / "accesorios_peso.csv")
    plazos, marcas = leer(COM / "plazos_proveedores.csv"), leer(COM / "marcas_aprobadas.csv")
    cli = norm(" ".join([c["cliente"].get("nombre", ""), c["cliente"].get("cliente_final", ""), c.get("titulo", "")]))
    marcas_cli = [m for m in marcas if norm(re.split(r"[ (]", m["cliente"])[0]) in cli]
    lineas, avisos = [f"# Controles con tablas de apoyo — {c['codigo']}", "",
                      "Generado por `herramientas/controles_tablas.py`. Información para revisar; no cambia precios.", ""], []
    kg_tot, m2_tot, sin_peso = 0.0, 0.0, []
    filas_p, filas_t, filas_m = [], {}, []
    for it in c["items"]:
        if it["grupo"] != "material":
            continue
        d = expandir(norm(it["descripcion"]))
        t = expandir(norm(f"{it['descripcion']} {it.get('especificacion', '')}"))
        fam = familia_de(d)  # la familia sale de la descripción; la especificación puede nombrar otras piezas
        fam = familia_de(t) if fam == "OTR" else fam
        at = {**atributos(t, fam), **atributos(d, fam)}
        kg, m2, fuente = peso_item(it, at, fam, canos, bridas, acc)
        if kg is None:
            sin_peso.append(f"{it['pos']} {it['descripcion'][:50]} ({fuente})")
        else:
            kg_tot += kg * it["cantidad"]
            m2_tot += (m2 or 0) * it["cantidad"]
            filas_p.append(f"| {it['pos']} | {it['descripcion'][:55]} | {it['cantidad']:g} {it['unidad']} | {kg:.2f} | {kg * it['cantidad']:.2f} | {fuente} |")
        rp = rubro(RUBRO_PLAZO, fam, at.get("tipo", "") or t)
        if rp:
            filas_t.setdefault(rp, []).append(it["pos"])
        rm = rubro(RUBRO_MARCA, fam, at.get("tipo", "") or t)
        if rm and marcas_cli:
            ms = [m for m in marcas_cli if m["rubro"].startswith(rm)]
            if ms:
                filas_m.append(f"| {it['pos']} | {it['descripcion'][:50]} | {ms[0]['cliente']} · {ms[0]['rubro']} | {ms[0]['marcas'][:120]} | {ms[0]['condicion']} |")
    lineas += ["## 1. Kilos y m² por equipo", "", f"**Peso estimado de lo que tiene tabla: {kg_tot:,.1f} kg** · m² exteriores de caños y niples: {m2_tot:,.2f} m².",
               f"Ítems sin dato de peso ({len(sin_peso)}): " + ("; ".join(sin_peso) if sin_peso else "ninguno") + ".", "",
               "| Pos | Ítem | Cantidad | kg/u | kg total | Fuente |", "|---|---|---|---|---|---|"] + filas_p + [""]
    dias = c.get("plazo", {}).get("dias")
    lineas += ["## 2. Plazos de material (proveedores 2025–2026)", "", f"Plazo ofrecido: **{dias} días**." if dias else "Sin plazo cargado.", "",
               "| Rubro | Posiciones | Datos | Típico sin stock (días) | Máximo (días) |", "|---|---|---|---|---|"]
    for rp, pos in sorted(filas_t.items()):
        ds = [r for r in plazos if r["rubro"] == rp and r["plazo_dias_max"]]
        sin_stock = [(float(r["plazo_dias_min"] or 0) + float(r["plazo_dias_max"])) / 2 for r in ds if float(r["plazo_dias_max"]) > 7]
        tip = statistics.median(sin_stock) if sin_stock else None
        mx = max((float(r["plazo_dias_max"]) for r in ds), default=None)
        lineas.append(f"| {rp} | {', '.join(pos)} | {len(ds)} | {tip:.0f} | {mx:.0f} |" if tip is not None and mx is not None
                      else f"| {rp} | {', '.join(pos)} | {len(ds)} | sin dato | {mx if mx is not None else 'sin dato'} |")
        if dias and tip and tip > dias:
            avisos.append(f"Plazo: el típico sin stock de '{rp}' ({tip:.0f} días) supera el plazo ofrecido ({dias} días). Confirmar stock o plazo cotizado")
    lineas += ["", "## 3. Marcas del cliente", ""]
    if not marcas_cli:
        lineas.append(f"No hay marcas aprobadas cargadas para este cliente ({c['cliente'].get('nombre', '')}). Si el pliego exige marcas, cargarlas en `conocimiento/comercial/marcas_aprobadas.csv`.")
    else:
        lineas += ["| Pos | Ítem | Lista | Marcas | Condición |", "|---|---|---|---|---|"] + filas_m
        avisos.append(f"Marcas: el cliente tiene listas cargadas ({len(marcas_cli)} renglones). Controlar cada ítem contra controles_tablas.md")
    (carpeta / "controles_tablas.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Controles con tablas: {kg_tot:,.1f} kg con tabla, {len(sin_peso)} ítems sin peso, {m2_tot:,.2f} m² de caño → {carpeta / 'controles_tablas.md'}")
    for a in avisos:
        print("  ! " + a)
    return avisos


if __name__ == "__main__":
    main(sys.argv[1])
