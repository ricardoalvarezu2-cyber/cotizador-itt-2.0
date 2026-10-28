// Comparación con antecedentes (paso P8): misma puntuación que herramientas/buscar_antecedentes.py y misma lectura que
// herramientas/comparar_antecedentes.py (5 más parecidos con precio; diferencia de más del 15% hay que explicarla; más de
// 4 veces es otra escala). Los datos vienen de datos.json → antecedentes (índice de proyectos 2025–2026).
const Antecedentes = (() => {
  const SERIES = [150, 300, 600, 900, 1500, 2000, 2500, 3000, 5000, 6000, 10000];

  function raiz(w) {
    if (w.length > 4 && w.endsWith("s")) w = w.slice(0, -1);
    if (w.length > 4 && /[eo]$/.test(w)) w = w.slice(0, -1);
    return w;
  }
  function palabras(t, A) {
    const vac = new Set(A.vacias), cor = new Set(A.cortas);
    const ws = new Set((t.match(/[a-z][a-z0-9]{2,}/g) || []).filter(w => (w.length > 3 || cor.has(w)) && !vac.has(w)));
    return [...new Set([...ws].map(raiz))];
  }
  function etiquetas(t, A) {
    const tags = [];
    for (const [k, claves] of Object.entries(A.claves)) if (claves.some(c => t.includes(c)) && !tags.includes(k)) tags.push(k);
    if (tags.length > 1 && tags.includes("OT")) tags.splice(tags.indexOf("OT"), 1);
    return tags.length ? tags : ["OT"];
  }
  function vecino(a, b, T) {
    const i = T.indexOf(a), j = T.indexOf(b);
    return i >= 0 && j >= 0 ? Math.abs(i - j) === 1 : Math.abs(a - b) / Math.max(a, b) <= 0.25;
  }
  // Ø del plano en pulgadas: 2" · 2 1/2" · 1/2" · 2.5
  function pulgadas(s) {
    const t = Busqueda.norm(s).replace(/"/g, " ").trim(), m = t.match(/^(\d+)?\s*(?:(\d+)\/(\d+))?/);
    if (!m || (!m[1] && !m[2])) return parseFloat(t.replace(",", ".")) || null;
    return (m[1] ? +m[1] : 0) + (m[2] ? +m[2] / +m[3] : 0);
  }

  function puntuar(p, q, idf, hoy, A) {
    const razones = []; let s = 0;
    const tags = p.tags.split(" ");
    if (q.familia) {
      if (p.fam === q.familia) s += 15;
      else if (tags.includes(q.familia)) { s += 5; razones.push(`familia ${q.familia} secundaria`); }
      else return null;
    }
    if (q.palabras.length) {
      const pw = new Set(p.w.split(" ")), comunes = q.palabras.filter(w => pw.has(w));
      const tot = q.palabras.reduce((a, w) => a + (idf[w] ?? 3), 0);
      s += tot ? 40 * comunes.reduce((a, w) => a + (idf[w] ?? 3), 0) / tot : 0;
      if (comunes.length) razones.push("texto: " + comunes.sort((a, b) => (idf[b] ?? 3) - (idf[a] ?? 3)).slice(0, 5).join(", "));
    }
    const dias = p.dia.split(" ").filter(Boolean).map(Number);
    if (q.diametro) {
      if (dias.includes(q.diametro)) { s += 15; razones.push(`Ø${q.diametro}"`); }
      else if (dias.some(d => vecino(q.diametro, d, A.tamanos))) { s += 7; razones.push("Ø cercano"); }
    }
    if (q.serie && p.ser.split(" ").includes(q.serie)) { s += 12; razones.push("serie " + q.serie); }
    if (q.cliente && Busqueda.norm(p.cl + " " + p.clf + " " + p.id).includes(Busqueda.norm(q.cliente))) { s += 8; razones.push("mismo cliente"); }
    if (p.pl) { s += 8; razones.push("planilla de costo"); }
    if (p.prov && p.prov !== "0") s += 3;
    if (p.oc) { s += 3; razones.push("ganada (OC)"); }
    if (p.conf === "baja") s -= 5;
    const anios = Math.max(0, (hoy - new Date(p.fe)) / (365.25 * 864e5));
    return { s: s * Math.max(0.4, 1 - 0.2 * anios), razones };
  }

  function comparar(cot, datos, precio_unitario) {
    const A = datos.antecedentes; if (!A) return { filas: [], avisos: ["No hay índice de proyectos en esta versión de la página"] };
    const texto = Busqueda.norm((cot.titulo || "") + " " + cot.items.map(i => i.descripcion).join(" "));
    const familia = etiquetas(texto, A)[0];
    const dias = cot.items.filter(i => i.grupo === "material").map(i => pulgadas(i.plano?.diametro || "")).filter(Boolean);
    const series = cot.items.map(i => (String(i.plano?.serie_sch || "").match(/\d+/g) || []).map(Number)).flat().filter(n => SERIES.includes(n));
    const q = { familia, palabras: palabras(Busqueda.norm(cot.titulo || ""), A), diametro: dias.length ? Math.max(...dias) : null,
      serie: series.length ? String(Math.max(...series)) : null, cliente: cot.cliente?.nombre || "" };
    const df = {};
    for (const p of A.proyectos) for (const w of new Set(p.w.split(" "))) df[w] = (df[w] || 0) + 1;
    const N = A.proyectos.length, idf = Object.fromEntries(Object.entries(df).map(([w, n]) => [w, Math.log(N / n)]));
    const hoy = new Date(), codigo = Busqueda.norm(cot.codigo || "");
    const res = [];
    for (const p of A.proyectos) {
      if (!p.pu || (codigo && Busqueda.norm(p.id).includes(codigo))) continue;
      const r = puntuar(p, q, idf, hoy, A);
      if (r) res.push({ ...r, p });
    }
    res.sort((a, b) => (Math.round(b.s * 10) - Math.round(a.s * 10)) || String(b.p.fe).localeCompare(String(a.p.fe)));
    const filas = res.slice(0, 5).map(({ p, razones }) => {
      const dif = precio_unitario / p.pu - 1, otra = dif > 3 || dif < -0.75;
      return { id: p.id, fecha: p.fe, cliente: p.cl, descripcion: p.d, oferta: p.of, pu: p.pu, moneda: p.mon, factor: p.fac, reparto: p.rep, dif, otra, ojo: !otra && Math.abs(dif) > 0.15, razones };
    });
    const avisos = filas.filter(f => f.ojo).slice(0, 2).map(f => `Precio ${(f.dif * 100).toFixed(0)}% contra "${f.id.slice(0, 50)}" (${Math.round(f.pu).toLocaleString("es-AR")} ${f.moneda}, ${f.fecha}): explicar la diferencia rubro por rubro (P8)`);
    if (filas.length && filas.every(f => f.otra)) avisos.push("Ningún antecedente de los 5 primeros es de la misma escala: comparar a mano");
    if (!filas.length) avisos.push(`No hay antecedentes de la familia ${familia} con precio en el índice: comparar a mano`);
    return { familia, nombreFamilia: A.familias[familia] || familia, consulta: q, filas, avisos };
  }
  return { comparar, palabras, etiquetas, pulgadas };
})();
if (typeof module !== "undefined") module.exports = Antecedentes;
