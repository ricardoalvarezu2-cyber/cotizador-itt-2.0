"""Pasa la planilla PC0 (YPF Lic 69343) a conocimiento/precios/planillas_costo_items_parte4.csv, con el formato de la etapa 2.

Uso: python cotizaciones/COT26-0330-001_YPF_LIC69343_SKID713/pc0_a_planillas.py
Después: python herramientas/unir_planillas_costo.py y python herramientas/actualizar_base.py.
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pc0  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "conocimiento" / "precios" / "planillas_costo_items_parte4.csv"
PROY = "YPF/28- Lic 69343 - SKIDS CONCENTRADORES VCD26217 - BLOQUE LAN"
CARP = "fuentes_originales/ofertas_texto/" + PROY
ARCH = "4.Armado de la Oferta Comercial/Cotización Lic 69343 Skid concentradores VCD26217 PC0.xlsx.txt"
FECHA = "2026-10-10"
CAMPOS = ["proyecto", "fecha_planilla", "carpeta", "archivo", "ubicacion", "tipo", "rubro", "descripcion", "cantidad", "unidad", "costo_unitario",
          "moneda", "iva_origen", "proveedor_o_criterio", "tc_explicito", "factor_venta", "cita", "confianza", "nota"]


def rubro(d):
    d = d.lower()
    for k, v in (("caño", "caño"), ("tee", "accesorio"), ("sockolet", "accesorio"), ("niple", "accesorio"), ("tapón", "accesorio"), ("brida", "brida"),
                 ("junta", "junta"), ("espárrago", "bulonería"), ("válvula", "válvula"), ("esferica", "válvula"), ("retencion", "válvula"), ("globo", "válvula")):
        if k in d:
            return v
    return "otro"


def fila(hoja, tipo, rub, desc, cant, un, precio, prov, cita, nota="", conf="media"):
    return {"proyecto": PROY, "fecha_planilla": FECHA, "carpeta": CARP, "archivo": ARCH, "ubicacion": f"hoja {hoja}", "tipo": tipo, "rubro": rub,
            "descripcion": desc, "cantidad": cant, "unidad": un, "costo_unitario": precio, "moneda": "USD", "iva_origen": "no dice",
            "proveedor_o_criterio": prov, "tc_explicito": "", "factor_venta": "1.5", "cita": cita, "confianza": conf,
            "nota": ("Planilla PC0 sin fecha por renglón: se toma la recepción del pedido (10-10-2026). " + nota).strip()}


def main():
    H = pc0.hojas()
    filas = []
    for hoja in ("1000623713", "1000623708"):
        for p, v in pc0.precios(H[hoja]).items():
            desc = f"{v['desc']} {v['medida']}".strip()
            if v["nota"]:
                desc = re.split(r"\.\s+(?=[A-ZÁÉÍÓÚ])", v["nota"].split(":", 1)[1])[0].strip() if ":" in v["nota"] else desc
            filas.append(fila(hoja, "material", rubro(desc), desc, v["cant"], v["unidad"] or "un", v["precio"], v["prov"].strip() or "sin proveedor en planilla",
                              f"{p} | {v['desc'][:60]} | {v['medida']} | {v['cant']:g} | {v['precio']:g}"))
    kg = {"1000623713": 2100, "1000623708": 850}
    srv = {"1000623713": [("mo", "armado", "Mano de obra de terceros (Ledesma): soldadura y armado de piping y skid concentrador 8 entradas 8\" + colector 12\"", 1, "global por equipo", 28000, "Ledesma (tercero)"),
                          ("mo", "armado", "Montaje + dimensional + desmontaje (piping y skid)", 1, "global por equipo", 6000, "tercero")],
           "1000623708": [("mo", "armado", "Mano de obra de terceros (Ledesma): soldadura y armado de piping y skid concentrador 3 entradas 12\" + colector 16\"", 1, "global por equipo", 13250, "Ledesma (tercero)"),
                          ("mo", "armado", "Montaje + dimensional + desmontaje (piping y skid)", 1, "global por equipo", 3000, "tercero"),
                          ("mo", "armado", "Fabricación de estructura de skid por kg (Ledesma)", 850, "kg", 3, "Ledesma (tercero): 850 kg × 3 = 2.550")]}
    comunes = [("mo", "ingeniería", "Horas de ingeniería", "hora", 15), ("mo", "calidad/dossier", "Horas de calidad", "hora", 15),
               ("mo", "prueba hidráulica", "Horas de planta para movimientos internos y PH", "hora", 13),
               ("servicio", "pintura", "Granallado y pintura piping (incluye materiales)", "m2", 50), ("servicio", "END", "Radiografía y LP según hoja END", "global por equipo", 5000),
               ("servicio", "transporte", "Transporte a Neuquén (Rincón de Aranda), un camión", "viaje", 2800)]
    horas = {"1000623713": {"Horas de ingeniería": 58.67, "Horas de calidad": 21, "Horas de planta para movimientos internos y PH": 40},
             "1000623708": {"Horas de ingeniería": 29.33, "Horas de calidad": 10.5, "Horas de planta para movimientos internos y PH": 40}}
    m2 = {"1000623713": 50, "1000623708": 22}
    for hoja in ("1000623713", "1000623708"):
        filas.append(fila(hoja, "material", "chapa/perfil", "Perfilería para skid (estructura)", kg[hoja], "kg", 2, "criterio de la planilla", f"Skid | Perfilería | {kg[hoja]} | kg | 2", conf="baja"))
        for t, r, d, c, u, pr, pv in srv[hoja]:
            filas.append(fila(hoja, t, r, d, c, u, pr, pv, f"{d[:40]} | {c} | {pr}"))
        for t, r, d, u, pr in comunes:
            c = horas[hoja].get(d, m2[hoja] if u == "m2" else 1)
            filas.append(fila(hoja, t, r, d, c, u, pr, "planilla ITT" if t == "mo" else "criterio ITT", f"{d[:40]} | {c} | {pr}",
                              "la planilla suma 20% más sobre los m² que ya dicen overspray 20%" if u == "m2" else ""))
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)
    print(f"{SALIDA.relative_to(RAIZ)}: {len(filas)} renglones")


if __name__ == "__main__":
    main()
