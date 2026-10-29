"""Prepara la carga inicial de la base de la página (web/semilla.json): el firmante y una cotización de la carpeta
cotizaciones/, con los datos del plano (diámetro, serie, material, extremos) en cada renglón de material para la
tabla de la oferta técnica. Claude la carga con ArtifactData (batch de "set").

Uso: python web/semilla.py cotizaciones/<carpeta> [id] [--salida <carpeta>]
  Sin --salida: deja web/semilla.json (firmante + cotización + resumen) para la carga inicial.
  Con --salida: deja un JSON por documento (cotizaciones__<id>.json y resumenes__<id>.json) para subir con ArtifactData
  (batch de "set" con file_path); es lo que usa Claude Code al terminar un pedido de la página (web/LEEME.md).
  Con --previo <archivo>: el documento que la página tiene hoy (ArtifactData "get" con out_dir). Manda el repositorio,
  pero lo que solo se carga en la página y el repositorio no tiene (rubros, transporte, firmante, aprobación, base,
  índices congelados, imagen del plano) se conserva, y se avisa qué se conservó y si la página tenía cambios más
  nuevos que el repositorio (auditoría 29-10-2026: antes se borraban).
"""
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


SOLO_PAGINA = ("rubros", "transporte", "firmante_id", "aprobacion", "base", "indices_congelados")


def conservar(cot, of, previo):
    """Copia a la versión del repositorio lo que solo existe en la página. Devuelve los avisos."""
    d = json.loads(Path(previo).read_text(encoding="utf-8"))
    d = d.get("data", d)
    pc, po, avisos = d.get("cot", {}), d.get("oferta", {}), []
    guardado = d.get("guardado", "")
    for k in SOLO_PAGINA:
        if k in pc and k not in cot:
            cot[k] = pc[k]
            avisos.append(f"se conserva de la página: {k}")
    globales = [i for i in pc.get("items", []) if i.get("global") and not any(j.get("id") == i["id"] for j in cot["items"])]
    if globales:  # precios globales por rubro cargados en la página (G-<rubro>)
        sys.path.insert(0, str(RAIZ / "herramientas"))
        import ficha_rubros
        for g in globales:  # los renglones del repositorio de ese rubro pasan al detalle guardado (si no, se sumarían dos veces)
            r = g.get("rubro")
            det = [i for i in cot["items"] if not i.get("global") and ficha_rubros.rubro_de(i) == r]
            if det:
                cot["items"] = [i for i in cot["items"] if i not in det]
                cot.setdefault("rubros", {}).setdefault(r, {"modo": "global"})["detalle"] = det
        cot["items"] += globales
        avisos.append("se conservan de la página los precios globales de: " + ", ".join(i.get("rubro", i["id"]) for i in globales))
    if po.get("imagen_plano_url") and not of.get("imagen_plano_url"):
        of["imagen_plano_url"] = po["imagen_plano_url"]
    if guardado and d.get("editor") != "claude-code":
        avisos.append(f"ATENCIÓN: la página tenía cambios propios guardados el {guardado[:16].replace('T', ' ')}; los ítems, precios y datos se "
                      "reemplazan por los del repositorio (si había que conservarlos, primero pasar la página al repositorio con el botón)")
    return avisos


def main(carpeta, ident="capex-oq8209", salida=None, previo=None):
    c = Path(carpeta)
    cot = json.load(open(c / "cotizacion.json", encoding="utf-8"))
    of = json.load(open(c / "oferta.json", encoding="utf-8"))
    plano = {r["pos"]: r for r in csv.DictReader(open(c / "pedido" / "lista_materiales_plano.csv", encoding="utf-8"))}
    for it in cot["items"]:
        r = plano.get(str(it.get("pos")))
        if it["grupo"] == "material" and r:
            it["plano"] = {k: r[k] for k in ("descripcion", "diametro", "serie_sch", "material", "extremos", "modelo_fabricante") if r.get(k)}
            if "modelo_fabricante" in it["plano"]:
                it["plano"]["modelo"] = it["plano"].pop("modelo_fabricante")
            if r.get("extremos_campo"):
                it["plano"]["extremos_campo"] = r["extremos_campo"]
            if r.get("cantidad_origen"):  # el cliente no indicó cantidad: la oferta la marca con (*)
                it["plano"]["cantidad_origen"] = r["cantidad_origen"]
            it["plano"]["cantidad"], it["plano"]["unidad"] = r["cantidad"], r["unidad"]  # tal cual el plano (la soldadura se cuenta así)
    # familia y atributos de cada material (los mismos que usa controles_tablas.peso_item): la ficha de la página los usa
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import ficha_rubros
    for it in cot["items"]:
        if it["grupo"] == "material":
            it["fam"], it["at"] = ficha_rubros.fam_at(it)
    # transcripción literal del documento y kilos por unidad, para el Excel de Compras de la página (igual que lista_compras.py)
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import lista_compras
    if (c / "pedido" / "transcripcion.json").exists():
        cot["transcripcion"] = json.load(open(c / "pedido" / "transcripcion.json", encoding="utf-8"))
    kg = {}
    for it in cot["items"]:
        if it["grupo"] == "material" and str(it.get("pos")) not in kg:
            k, _ = lista_compras.kg_por_unidad(plano.get(str(it.get("pos")), {"descripcion": it["descripcion"]}), it)
            if k is not None:
                kg[str(it["pos"])] = round(k, 3)
    cot["kg_compras"] = kg
    if (c / "ficha_rubros.json").exists():  # ficha por rubro (soldaduras, kg, m², placas, medidas) para el modo global
        cot["ficha"] = json.load(open(c / "ficha_rubros.json", encoding="utf-8"))
    avisos = conservar(cot, of, previo) if previo else []
    cot.setdefault("firmante_id", "matias-russo")
    of.pop("firma", None)  # la firma sale del firmante elegido
    ahora = datetime.now().isoformat(timespec="seconds")
    calc = json.loads(subprocess.run(["node", "-e", f"""
const M=require('{RAIZ}/web/src/motor.js'),d=require('{RAIZ}/web/datos.json'),c=JSON.parse(require('fs').readFileSync(0,'utf8'));
const r=M.calcular(c,d.indices);console.log(JSON.stringify({{u:r.precio_unitario,t:r.total}}))"""], input=json.dumps(cot), capture_output=True, text=True, check=True).stdout)
    ops = [
        {"op": "set", "path": "firmantes/matias-russo", "data": {"nombre": "Matías Russo", "cargo": "Representante Comercial", "telefono": "", "celular": "", "email": ""}},
        {"op": "set", "path": f"cotizaciones/{ident}", "data": {"cot": cot, "oferta": of, "creado": ahora, "guardado": ahora}},
        {"op": "set", "path": f"resumenes/{ident}", "data": {"codigo": cot["codigo"], "titulo": cot["titulo"], "cliente": cot["cliente"]["nombre"],
                                                           "estado": cot["estado"], "unitario": calc["u"], "total": calc["t"], "actualizado": ahora}},
    ]
    if salida:
        ops[1]["data"]["editor"] = "claude-code"  # la página avisa que la actualizó Claude Code
        Path(salida).mkdir(parents=True, exist_ok=True)
        for o in ops[1:]:
            f = Path(salida) / (o["path"].replace("/", "__") + ".json")
            f.write_text(json.dumps(o["data"], ensure_ascii=False), encoding="utf-8")
            print(f"{o['path']} → {f}")
        print(f"unitario USD {calc['u']} · total USD {calc['t']}")
        for x in avisos:
            print("  ! " + x)
        return
    archivo = RAIZ / "web" / "semilla.json"
    archivo.write_text(json.dumps(ops, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{archivo.relative_to(RAIZ)}: {len(ops)} documentos · unitario USD {calc['u']} · {len(json.dumps(ops[1]['data'])) / 1024:.0f} KiB la cotización")


if __name__ == "__main__":
    a = sys.argv[1:]
    op = {}
    for k in ("--salida", "--previo"):
        if k in a:
            i = a.index(k)
            op[k[2:]] = a[i + 1]
            del a[i:i + 2]
    main(*a, **op)
