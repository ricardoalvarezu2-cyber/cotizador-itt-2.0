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
fi["peso_equipo"]=f.peso_equipo(cfg)
print(json.dumps({"cot":cfg,"py":fi}))`], { cwd: raiz, maxBuffer: 1 << 26 }).toString());
  // la tabla del plano manda: renglones del cómputo que no están en el plano (compras extra "1b") no llevan plano
  const js = Ficha.calcular(r.cot, datos), py = r.py;
  const cmp = (k, a, b, tol) => { if (Math.abs((a || 0) - (b || 0)) > tol) { ok = false; console.log(`FALLA ${c} ${k}: página ${a} · Python ${b}`); } };
  cmp("juntas_bw", js.mo_piping.juntas_bw, py.mo_piping.juntas_bw, 1e-6);
  cmp("pulg_eq", js.mo_piping.pulg_eq, py.mo_piping.pulg_eq, 0.01);
  cmp("juntas_sw_olet", js.mo_piping.juntas_sw_olet, py.mo_piping.juntas_sw_olet, 1e-6);
  cmp("kg_piping", js.mo_piping.kg_piping, py.mo_piping.kg_piping, Math.max(0.2, 1e-4 * py.mo_piping.kg_piping));  // redondeo de datos.json
  cmp("kg_estructura", js.mo_estructura.kg, py.mo_estructura.kg, 0.2);
  cmp("m2_total", js.pintura.m2_total, py.pintura.m2_total, 0.02);
  cmp("placas_chicas", js.end.placas_chicas, py.end.placas_chicas, 0);
  cmp("placas_grandes", js.end.placas_grandes, py.end.placas_grandes, 0);
  cmp("procedimientos", js.procedimientos.cantidad, py.procedimientos.cantidad, 0);
  cmp("litros", js.ph.litros, py.ph.litros, 0.11);
  const pe = Ficha.pesoEquipo(r.cot, datos);  // peso del equipo de la planilla (kg y USD/kg)
  cmp("peso_equipo", pe.kg, py.peso_equipo.kg, Math.max(0.2, 1e-4 * py.peso_equipo.kg));
  if (pe.sin_peso.join() !== py.peso_equipo.sin_peso.join()) { ok = false; console.log(`FALLA ${c} sin_peso: página ${pe.sin_peso} · Python ${py.peso_equipo.sin_peso}`); }
  cmp("espesor_max", js.end.espesor_max_mm, py.end.espesor_max_mm, 1e-6);
  n++;
}
// lector de números de la página (numeroDoc) igual a numeros.leer_numero, y peso con coma decimal (AESA, 18-11-2026)
const casos = ["0,60", "3,69", "417", "1.250", "24,4", "1.250,5", "4,413.92", "1.096.71", "4,500", "1.250.000", "28.500", "12.5", "0,904", "1,2.3,4", "x"];
const pyNum = JSON.parse(execFileSync("python3", ["-c", `import json,sys; sys.path.insert(0,"herramientas"); from numeros import numero; print(json.dumps([numero(x) for x in json.loads(sys.argv[1])]))`, JSON.stringify(casos)], { cwd: raiz }).toString());
casos.forEach((x, i) => { const a = Ficha.numeroDoc(x); if (a !== pyNum[i]) { ok = false; console.log(`FALLA numeroDoc("${x}"): página ${a} · Python ${pyNum[i]}`); } });
for (const [txt, esp] of [["Tornillo (0,60 kg c/u)", 0.6], ["Brida ciega 3,69 kg", 3.69], ["Cabezal (417 kg)", 417], ["Virola 1.250 kg", 1250]]) {
  const kg = Ficha.pesoEquipo({ items: [{ pos: "1", grupo: "material", descripcion: "Pieza", especificacion: txt, cantidad: 2, unidad: "un" }] }, datos).kg;
  if (kg !== Math.round(20 * esp) / 10) { ok = false; console.log(`FALLA peso "${txt}": página ${kg}, se esperaba ${Math.round(20 * esp) / 10}`); }
}
console.log(ok ? `Ficha JS OK: igual a Python en ${n} cotizaciones (juntas, pulgadas, placas, kg y m²)` : "Ficha JS distinta de Python");
process.exit(ok ? 0 : 1);
