// Prueba de ficha.js contra herramientas/ficha_rubros.py. Uso: node web/probar_ficha.js
// En cada cotización con tabla del plano, arma los renglones como semilla.py (plano, familia y atributos) y compara, con los mismos
// renglones de entrada,
// juntas, pulgadas, placas, kg y m² de la página con los de Python.
const fs = require("fs");
const { execFileSync } = require("child_process");
const Ficha = require("./src/ficha.js");
const datos = JSON.parse(fs.readFileSync(__dirname + "/datos.json", "utf8"));
const raiz = __dirname + "/..";
let ok = true, n = 0;
const conItems = c => { try { return JSON.parse(fs.readFileSync(`${raiz}/cotizaciones/${c}/cotizacion.json`, "utf8")).items.some(i => i.grupo === "material"); } catch (e) { return false; } };
for (const c of fs.readdirSync(raiz + "/cotizaciones").filter(c => !c.startsWith("_") && fs.existsSync(`${raiz}/cotizaciones/${c}/pedido/lista_materiales_plano.csv`) && conItems(c))) {
  const r = JSON.parse(execFileSync("python3", ["-c", `import json,sys,csv; sys.path.insert(0,"herramientas"); import ficha_rubros as f
from pathlib import Path
d=Path("cotizaciones/${c}"); cfg=json.load(open(d/"cotizacion.json"))
plano={r["pos"]:r for r in csv.DictReader(open(d/"pedido"/"lista_materiales_plano.csv"))}
for it in cfg["items"]:
    if it["grupo"]=="material":
        it["fam"],it["at"]=f.fam_at(it)
        p=plano.get(str(it.get("pos")))
        if p:
            it["plano"]={k:p[k] for k in ("descripcion","diametro","serie_sch","material","extremos") if p.get(k)}
            if p.get("extremos_campo"): it["plano"]["extremos_campo"]=p["extremos_campo"]
            it["plano"]["cantidad"],it["plano"]["unidad"]=p["cantidad"],p["unidad"]
import tempfile, copy
fi=f.armar(Path(tempfile.mkdtemp()), copy.deepcopy(cfg))  # sin la tabla del plano: los mismos renglones que ve la página
print(json.dumps({"cot":cfg,"py":fi}))`], { cwd: raiz, maxBuffer: 1 << 26 }).toString());
  // la tabla del plano manda: renglones del cómputo que no están en el plano (compras extra "1b") no llevan plano
  const js = Ficha.calcular(r.cot, datos), py = r.py;
  const cmp = (k, a, b, tol) => { if (Math.abs((a || 0) - (b || 0)) > tol) { ok = false; console.log(`FALLA ${c} ${k}: página ${a} · Python ${b}`); } };
  cmp("juntas_bw", js.mo_piping.juntas_bw, py.mo_piping.juntas_bw, 1e-6);
  cmp("pulg_eq", js.mo_piping.pulg_eq, py.mo_piping.pulg_eq, 0.01);
  cmp("juntas_sw_olet", js.mo_piping.juntas_sw_olet, py.mo_piping.juntas_sw_olet, 1e-6);
  cmp("kg_piping", js.mo_piping.kg_piping, py.mo_piping.kg_piping, 0.2);
  cmp("kg_estructura", js.mo_estructura.kg, py.mo_estructura.kg, 0.2);
  cmp("m2_total", js.pintura.m2_total, py.pintura.m2_total, 0.02);
  cmp("placas_chicas", js.end.placas_chicas, py.end.placas_chicas, 0);
  cmp("placas_grandes", js.end.placas_grandes, py.end.placas_grandes, 0);
  cmp("espesor_max", js.end.espesor_max_mm, py.end.espesor_max_mm, 1e-6);
  n++;
}
console.log(ok ? `Ficha JS OK: igual a Python en ${n} cotizaciones (juntas, pulgadas, placas, kg y m²)` : "Ficha JS distinta de Python");
process.exit(ok ? 0 : 1);
