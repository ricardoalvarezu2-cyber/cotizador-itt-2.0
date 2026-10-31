import sys, csv, re, math
sys.path.insert(0, '/home/user/cotizador-itt/herramientas')
import precotizar as pc
from numeros import fmt
CAR = '/home/user/cotizador-itt/cotizaciones/CTRL-C01_PAMPA7_COLECTOR'
filas = list(csv.DictReader(open(CAR + '/pedido/lista_materiales_plano.csv', encoding='utf-8')))
tot = pc.soldaduras(filas)
es_cano_m = lambda r: re.search(r"\bcano\b|\bcanos\b|\btubo\b", pc.norm(r["descripcion"])) and pc.norm(r["unidad"]).startswith("m")
pm = [r for r in filas if es_cano_m(r) and "BW" in r["extremos"].upper()]
base = pc.soldaduras(pm)['pulg_eq'] if pm else 0
tabla = pc.leer(pc.TEC / "factores_soldadura.csv")
grupos = {}
for r in filas:
    if r in pm: continue
    ext = r["extremos"].upper()
    if "BW" not in ext and "SW" not in ext: continue
    d = pc.norm(r["descripcion"]); q = pc.cantidad_plano(r["cantidad"])
    toks = [t for t in re.split(r"/", ext.replace("-M","").replace("-H","")) if t]
    if len(toks) == 1:
        n = 3 if re.search(r"\btee\b", d) else (1 if re.search(r"brida|" + pc.OLETS, d) else 2); toks = toks * n
    olet = re.search(pc.OLETS, d)
    dims = [pc.dn_de(x) for x in re.split(r"\s*x\s*", r["diametro"].lower()) if pc.dn_de(x)]
    schs = [pc.sch_de(x) or "" for x in re.split(r"\s*x\s*", r["serie_sch"])]
    sch = pc.sch_de(r["serie_sch"]) or ""
    partes = []
    if olet:
        fa = 2.5 if "weldolet" in d else 1.75
        nj = (toks.count("BW") + toks.count("SW")) * q  # el olet lleva dos soldaduras: al caño (BW) y a la pieza que recibe (SW)
        partes.append(("Derivación soldada sobre caño (sockolet/weldolet)", min(dims), r["serie_sch"].strip() + " (clase)", nj, nj * min(dims) * fa))
    elif "SW" in toks:
        f = pc.factor_espesor(dims[0], sch, tabla)[0]
        partes.append(("Enchufe soldado (SW)", dims[0], sch, toks.count("SW") * q, toks.count("SW") * q * dims[0] * f))
    else:
        diam_cano = {pc.dn_de(x) for c in pm for x in re.split(r"\s*x\s*", c["diametro"].lower()) if pc.dn_de(x)}
        m = (2 * pc.AJUSTE_DIRECTAS if pm and (not diam_cano or any(x in diam_cano for x in dims)) else 1) / 2
        nb = toks.count("BW")
        if len(dims) == 2 and dims[0] != dims[1]:
            reps = [(dims[0], nb - 1), (dims[1], 1)]
        else:
            reps = [(dims[0], nb)]
        for dn, n in reps:
            f = pc.factor_espesor(dn, sch, tabla)[0]
            partes.append(("A tope (BW)", dn, sch, n * q * m, n * q * m * dn * f))
    for tipo, dn, sc, nj, pe in partes:
        g = grupos.setdefault((tipo, dn, sc), {"juntas": 0, "pe": 0, "pos": []})
        g["juntas"] += nj; g["pe"] += pe; g["pos"].append(r["pos"])
filas_s = []
for (tipo, dn, sch), g in sorted(grupos.items(), key=lambda x: (x[0][0], -x[0][1])):
    esp = next((t["espesor_mm"] for t in tabla if float(t["dn_pulg"]) == dn and t["schedule"] == sch), "") if "clase" not in sch else ""
    filas_s.append([tipo, dn, sch, float(esp) if esp else None, round(g["juntas"], 2), round(g["pe"], 2), ", ".join(dict.fromkeys(g["pos"]))])
rosc = []
for r in filas:
    e = r["extremos"].upper()
    if "NPT" in e:
        es_niple = "niple" in pc.norm(r["descripcion"])
        rosc.append([r["pos"], r["descripcion"], r["diametro"], r["serie_sch"], r["extremos"], pc.cantidad_plano(r["cantidad"]), r["unidad"],
                     e.count("NPT") * pc.cantidad_plano(r["cantidad"]) if es_niple else None])
import json; json.dump({"sold": filas_s, "rosc": rosc, "tot_pe": tot["pulg_eq"], "tot_bw": tot["juntas_bw"], "sw": tot["juntas_sw_olet"]}, open('/tmp/itt_ej/datos.json','w'), ensure_ascii=False, indent=1)
print(json.dumps({"sold": filas_s, "tot": tot["pulg_eq"], "bw": tot["juntas_bw"], "sw": tot["juntas_sw_olet"], "suma_pe": round(sum(x[5] for x in filas_s),2)}, ensure_ascii=False, indent=0))
for x in rosc: print(x)
