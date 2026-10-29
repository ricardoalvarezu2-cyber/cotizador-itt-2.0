// Antecedentes (P8) en la página: imprime los 5 más parecidos con precio de cada cotización que se le pase, para que
// herramientas/test_antecedentes.py compruebe que la página da lo mismo que Python.
// Uso: node web/probar_antecedentes.js cotizaciones/<carpeta> [...]
const fs = require("fs");
global.Busqueda = require("./src/busqueda.js");
const Antecedentes = require("./src/antecedentes.js");
const datos = JSON.parse(fs.readFileSync(__dirname + "/datos.json", "utf8"));
const out = {};
for (const carpeta of process.argv.slice(2)) {
  const cot = JSON.parse(fs.readFileSync(carpeta + "/cotizacion.json", "utf8"));
  const { q, res } = Antecedentes.buscar(cot, datos);
  out[carpeta] = { familia: q.familia, subtipo: q.subtipo, cuerpo: q.cuerpo, diametro: q.diametro, serie: q.serie,
    top: res.slice(0, 5).map(r => [r.p.id, Math.round(r.s * 10) / 10]) };
}
console.log(JSON.stringify(out));
