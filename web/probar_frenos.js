// Frenos de la oferta: la página (Busqueda.frenosOferta) da las mismas claves que Python (herramientas/frenos.py) en cada
// cotización del repositorio, con cot.frenos_repo como lo deja web/semilla.py. Uso: node web/probar_frenos.js <json>
// (el json lo arma herramientas/test_errores_sembrados.py / verificar_todo.py: [{nombre, cot, oferta, hoy, claves}]).
const Busqueda = require("./src/busqueda.js");
const casos = JSON.parse(require("fs").readFileSync(process.argv[2], "utf8"));
let mal = 0;
for (const c of casos) {
  const js = Busqueda.frenosOferta(c.cot, c.oferta, c.hoy).map(f => f.clave).sort().join(",");
  const py = [...c.claves].sort().join(",");
  if (js !== py) { mal++; console.log(`FALLA ${c.nombre}: página [${js}] · Python [${py}]`); }
}
console.log(mal ? `FALLAN ${mal} de ${casos.length}` : `OK ${casos.length} cotizaciones: la página frena igual que Python`);
process.exit(mal ? 1 : 0);
