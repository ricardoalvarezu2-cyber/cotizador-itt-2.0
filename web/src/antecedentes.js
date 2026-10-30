// Comparación con antecedentes (paso P8): mismo criterio que herramientas/buscar_antecedentes.py (familia o subtipo,
// parecido con los datos que tienen los dos, Ø del cuerpo en recipientes, sinónimos) y misma lectura que
// herramientas/comparar_antecedentes.py (5 más parecidos con precio; diferencia de más del 15% hay que explicarla; más de
// 4 veces es otra escala). Los datos y las tablas (familias, subtipos, sinónimos, pesos) vienen de datos.json →
// antecedentes, armado desde Python: no se copian a mano. Prueba de igualdad con Python: herramientas/test_antecedentes.py.
const Antecedentes = (() => {
  const cache = new WeakMap();
  function tablas(A) {
    if (cache.has(A)) return cache.get(A);
    const T = {
      sin: (A.sinonimos || []).map(([a, b]) => [new RegExp(a, "g"), b]),
      sub: (A.subtipos || []).map(([c, f, n, pats]) => ({ c, f, n, rx: pats.map(x => new RegExp(x)) })),
      rec: new Set(A.recipientes || []),
      pulg: new RegExp(A.pulgadas, "g"), diam: new RegExp(A.diam_texto, "g"),
      ser: (A.series_rx || []).map(x => new RegExp(x, "g")),
      mat: (A.materiales_rx || []).map(([k, x]) => [k, new RegExp(x)]), uni: (A.uniones_rx || []).map(([k, x]) => [k, new RegExp(x)]),
    };
    T.subFam = Object.fromEntries(T.sub.map(s => [s.c, s.f]));
    T.subNom = Object.fromEntries(T.sub.map(s => [s.c, s.n]));
    cache.set(A, T);
    return T;
  }
  // igual que indice_proyectos.norm: fracciones, sin acentos ni otros caracteres no ASCII, minúsculas
  function norm(t, A) {
    let s = String(t ?? "");
    for (const [a, b] of Object.entries(A.fracciones || {})) s = s.split(a).join(b);
    return s.normalize("NFKD").replace(/[^\x00-\x7f]/g, "").toLowerCase().replace(/\s+/g, " ");
  }
  function canon(t, T) { for (const [rx, b] of T.sin) t = t.replace(rx, b); return t; }
  function raiz(w) {
    if (w.length > 4 && w.endsWith("s")) w = w.slice(0, -1);
    if (w.length > 4 && /[eo]$/.test(w)) w = w.slice(0, -1);
    return w;
  }
  function palabras(t, A) {
    const vac = new Set(A.vacias), cor = new Set(A.cortas);
    const ws = new Set((t.match(/[a-z][a-z0-9]{2,}/g) || []).filter(w => (w.length > 3 || cor.has(w)) && !vac.has(w)));
    return [...new Set([...ws].map(raiz))].sort();
  }
  function etiquetas(t, A) {
    const tags = [];
    for (const [k, claves] of Object.entries(A.claves)) if (claves.some(c => t.includes(c)) && !tags.includes(k)) tags.push(k);
    if (tags.length > 1 && tags.includes("OT")) tags.splice(tags.indexOf("OT"), 1);
    return tags.length ? tags : ["OT"];
  }
  function subtipoEn(t, T, fam) {
    for (const s of T.sub) if ((!fam || s.f === fam) && s.rx.some(rx => rx.test(t))) return s.c;
    return "";
  }
  function familiaEn(t, A, T) {
    const pos = [];
    for (const [k, claves] of Object.entries(A.claves)) for (const c of claves) { const i = t.indexOf(c); if (i >= 0) pos.push([i, k]); }
    for (const s of T.sub) for (const rx of s.rx) { const m = t.match(rx); if (m) pos.push([m.index, s.f]); }
    pos.sort((a, b) => a[0] - b[0] || (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));
    return pos.length ? pos[0][1] : "";
  }
  function clasificar(principal, resto, famDada, A, T) {
    const p = canon(norm(principal, A), T), r = canon(norm(resto, A), T);
    let fam = String(famDada || "").trim().split(" ")[0].toUpperCase();
    if (!(fam in A.familias) || fam === "OT") fam = "";
    if (!fam) fam = familiaEn(p, A, T) || familiaEn(r, A, T) || "OT";
    let sub = subtipoEn(p, T, fam) || subtipoEn(p, T);
    if (!sub) sub = subtipoEn(r, T, fam);
    const tags = [fam, ...etiquetas(p + " " + r, A).filter(k => k !== fam)];
    if (tags.length > 1 && tags.includes("OT")) tags.splice(tags.indexOf("OT"), 1);
    return { fam, tags, sub };
  }
  function frac(s) {
    let tot = 0;
    for (const x of s.trim().split(/\s+/)) { if (x.includes("/")) { const [a, b] = x.split("/"); tot += +a / +b; } else tot += +x; }
    return tot;
  }
  function diametros(t, T) {
    const out = new Set();
    for (const m of t.matchAll(T.pulg)) {
      const v = frac(m[1].replace("-", " ").replace(",", "."));
      if (isFinite(v) && v >= 0.125 && v <= 60) out.add(v);
    }
    for (const m of t.matchAll(T.diam)) { const v = +m[1]; if (v >= 1 && v <= 60) out.add(v); }
    return [...out].sort((a, b) => a - b);
  }
  function series(t, T) {
    const out = new Set();
    for (const rx of T.ser) for (const m of t.matchAll(rx)) out.add(m[1]);
    return [...out].sort((a, b) => +a - +b);
  }
  const mm = s => /\d\.\d{3}/.test(s) ? +s.replace(/\./g, "").replace(",", ".") : +s.replace(",", ".");
  // igual que indice_proyectos.diametro_cuerpo
  function diametroCuerpo(texto, A, T) {
    const t = canon(norm(String(texto || "").replace(/[”″“]/g, '"'), A), T);
    const pul = `(\\d{1,3}(?:[.,]\\d{1,3})?)\\s?(?:"|”|''|pulg)`;
    for (const rx of [`(?:cuerpo|virola|envolvente|casco|shell)[^0-9,;:]{0,25}?` + pul, `casquetes?[^,;]{0,30}?diam ?` + pul])
      for (const m of t.matchAll(new RegExp(rx, "g"))) { const v = +m[1].replace(",", "."); if (v >= 6 && v <= 160) return v; }
    for (const m of t.matchAll(/(?:cuerpo|virola|envolvente|casco|shell)?[^0-9,;]{0,20}?(?:diam(?:etro)?\.?|\bd\.?)\s?(?:ext(?:erior)?\.?|int(?:erior)?\.?)?\s?(?:de )?(\d[\d.,]{2,6})\s?(?:mm|x ?\d[\d.,]* ?mm)/g)) {
      const v = mm(m[1]); if (v >= 250 && v <= 4000) return Math.round(v / 25.4 * 10) / 10;
    }
    for (const m of t.matchAll(/(\d[\d.,]{2,6})\s?mm (?:de )?diam/g)) { const v = mm(m[1]); if (v >= 250 && v <= 4000) return Math.round(v / 25.4 * 10) / 10; }
    for (const m of t.matchAll(new RegExp(`(?:separador|coalescente|tanque|recipiente|\\bkod\\b|slugcatcher|scrubber|pulmon|desgasificador)[^,;:"”]{0,40}?(?:diam ?)?` + pul, "g"))) {
      const v = +m[1].replace(",", "."); if (v >= 6 && v <= 160) return v;
    }
    return null;
  }
  // igual que buscar_antecedentes.consulta_de_cotizacion (con indice_proyectos.clasificar_cotizacion)
  function consulta(cot, A, T) {
    const eq = cot.equipo || {}, items = cot.items || [];
    const principal = [eq.singular || "", cot.titulo || ""].join(" ");
    const resto = items.map(i => `${i.descripcion || ""} ${i.especificacion || ""}`).join(" ");
    const famDada = eq.familia || familiaEn(canon(norm(principal, A), T), A, T) || (A.tipo_familia || {})[eq.tipo || ""] || "";
    const c = clasificar(principal, resto, famDada, A, T);
    const sub = eq.subtipo || c.sub;
    let cuerpo = null;
    if (T.rec.has(c.fam)) cuerpo = (+eq.diametro_pulg || 0) || diametroCuerpo(principal + " " + resto, A, T);
    const t = canon(norm([cot.titulo || "", ...items.map(i => `${i.descripcion || ""} ${i.especificacion || ""}`)].join(" "), A), T);
    const dias = diametros(t, T), ser = series(t, T);
    const mat = T.mat.filter(([, rx]) => rx.test(t)).map(([k]) => k), uni = T.uni.filter(([, rx]) => rx.test(t)).map(([k]) => k);
    return { texto: principal, familia: c.fam !== "OT" ? c.fam : null, subtipo: sub || null,
      diametro: cuerpo ? null : ((+eq.diametro_pulg || 0) || (dias.length ? Math.max(...dias) : null)), cuerpo: cuerpo || null,
      serie: ser.length ? ser[ser.length - 1] : null, material: mat.length === 1 ? mat[0] : null, union: uni.length === 1 ? uni[0] : null,
      cliente: cot.cliente?.nombre || null };
  }
  function vecino(a, b, Tm) {
    const i = Tm.indexOf(a), j = Tm.indexOf(b);
    return i >= 0 && j >= 0 ? Math.abs(i - j) === 1 : Math.abs(a - b) / Math.max(a, b) <= 0.25;
  }
  const g = n => String(Math.round(n * 100) / 100).replace(".", ",");

  // igual que buscar_antecedentes.puntuar
  function puntuar(p, q, idf, hoy, A, T) {
    const P = A.pesos, razones = [], falta = [], tags = p.tags.split(" "), psub = p.sub || "", psubs = (p.subs || psub).split(" ").filter(Boolean);
    let ff = 1;
    if (q.familia) {
      if (p.fam === q.familia || (q.subtipo && psubs.includes(q.subtipo))) { /* entra */ }
      else if (tags.includes(q.familia)) { ff = 0.85; razones.push(`familia ${q.familia} secundaria`); }
      else return null;
    }
    let got = 0, posible = 0, maximo = 0;
    const crit = (n, tp, pts, et) => { maximo += P[n]; if (!tp) { falta.push(et || n); return; } posible += P[n]; got += pts; };
    if (q.subtipo) {
      const igual = psub === q.subtipo, tambien = !igual && psubs.includes(q.subtipo);
      crit("subtipo", !!psub, igual ? P.subtipo : tambien ? 20 : 0);
      if (psub) razones.push(igual ? `mismo subtipo (${T.subNom[q.subtipo] || q.subtipo})` : tambien ? `incluye ${T.subNom[q.subtipo] || q.subtipo}` : `otro subtipo: ${T.subNom[psub] || psub}`);
    }
    const qw = q.texto ? palabras(canon(norm(q.texto, A), T), A) : [];
    if (qw.length) {
      const pw = new Set(p.w.split(" ")), comunes = qw.filter(w => pw.has(w));
      const tot = qw.reduce((a, w) => a + (idf[w] ?? 3), 0);
      crit("texto", true, tot ? P.texto * comunes.reduce((a, w) => a + (idf[w] ?? 3), 0) / tot : 0);
      if (comunes.length) razones.push("texto: " + comunes.sort((a, b) => (idf[b] ?? 3) - (idf[a] ?? 3)).slice(0, 5).join(", "));
    }
    const dias = p.dia.split(" ").filter(Boolean).map(Number), pc = p.cue || null, qc = q.cuerpo;
    const recip = (q.familia && T.rec.has(q.familia)) || T.rec.has(T.subFam[q.subtipo]);
    if (recip && qc) {
      if (pc) {
        const r = Math.abs(qc - pc) / Math.max(qc, pc), pts = r <= 0.10 ? P.tamano : r <= 0.30 ? 7 : 0;
        crit("tamano", true, pts); razones.push(`Ø cuerpo ${g(pc)}"` + (pts === P.tamano ? "" : pts ? " (cercano)" : " (otro tamaño)"));
      } else if (q.diametro && dias.length) {
        crit("tamano", true, dias.includes(q.diametro) ? 7.5 : dias.some(d => vecino(q.diametro, d, A.tamanos)) ? 3.5 : 0); falta.push("Ø cuerpo");
      } else crit("tamano", false, 0, "Ø cuerpo");
    } else if (q.diametro) {
      if (dias.includes(q.diametro)) { crit("tamano", true, P.tamano); razones.push(`Ø${g(q.diametro)}"`); }
      else if (dias.some(d => vecino(q.diametro, d, A.tamanos))) { crit("tamano", true, 7); razones.push("Ø cercano"); }
      else crit("tamano", dias.length > 0, 0, "Ø");
    }
    if (q.serie) { const ps = p.ser.split(" ").filter(Boolean); crit("serie", ps.length > 0, ps.includes(q.serie) ? P.serie : 0); if (ps.includes(q.serie)) razones.push("serie " + q.serie); }
    if (q.material) { const pm = (p.mat || "").split(" ").filter(Boolean); crit("material", pm.length > 0, pm.includes(q.material) ? P.material : 0); if (pm.includes(q.material)) razones.push(q.material); }
    if (q.union) { const pu = (p.un || "").split(" ").filter(Boolean); crit("union", pu.length > 0, pu.includes(q.union) ? P.union : 0); if (pu.includes(q.union)) razones.push(q.union); }
    if (q.cliente) {
      const mismo = norm(p.cl + " " + (p.clf || "") + " " + p.id, A).includes(norm(q.cliente, A));
      crit("cliente", true, mismo ? P.cliente : 0); if (mismo) razones.push("mismo cliente");
    }
    let s = posible ? 100 * got / posible * (0.7 + 0.3 * posible / maximo) : 0;
    if (p.pl) { s += 5; razones.push("planilla de costo"); }
    if (p.prov && p.prov !== "0") s += 2;
    if (p.oc) { s += 2; razones.push("ganada (OC)"); }
    if (p.conf === "baja") s -= 5;
    if (falta.length) razones.push("sin dato: " + falta.join(", "));
    const [y, m, d] = String(p.fe).split("-").map(Number);
    const dias365 = Math.floor((hoy - Date.UTC(y, m - 1, d)) / 864e5);  // días enteros, como Python
    return { s: s * ff * Math.max(0.4, 1 - 0.2 * Math.max(0, dias365 / 365.25)), razones };
  }

  function buscar(cot, datos) {
    const A = datos.antecedentes, T = tablas(A), q = consulta(cot, A, T);
    const df = {};
    for (const p of A.proyectos) for (const w of new Set(p.w.split(" "))) df[w] = (df[w] || 0) + 1;
    const N = A.proyectos.length, idf = Object.fromEntries(Object.entries(df).map(([w, n]) => [w, Math.log(N / n)]));
    const h = new Date(), hoy = Date.UTC(h.getFullYear(), h.getMonth(), h.getDate()), codigo = Busqueda.norm(cot.codigo || "");
    const res = [];
    for (const p of A.proyectos) {
      if (!p.pu || (codigo && Busqueda.norm(p.id).includes(codigo))) continue;
      const r = puntuar(p, q, idf, hoy, A, T);
      if (r) res.push({ ...r, p });
    }
    // como Python: round(puntaje, 1) y, ante empate, el más nuevo
    res.sort((a, b) => (Math.round(b.s * 10) - Math.round(a.s * 10)) || String(b.p.fe).localeCompare(String(a.p.fe)));
    return { q, res, T };
  }

  // igual que comparar_antecedentes.py: costo contra costo (Matías, 30-10-2026); el precio de venta queda como referencia
  function comparar(cot, datos, precio_unitario, costo) {
    const A = datos.antecedentes; if (!A) return { filas: [], avisos: ["No hay índice de proyectos en esta versión de la página"] };
    const { q, res, T } = buscar(cot, datos), familia = q.familia || "OT";
    let mat = 0, tot = 0;
    for (const it of cot.items || []) { const v = (+it.cantidad || 0) * (+it.fuentes?.[0]?.precio || 0); tot += v; if (it.grupo === "material") mat += v; }
    const matN = tot ? mat / tot : 0, moN = tot ? 1 - matN : 0, avisos = [];
    const filas = res.slice(0, 5).map(({ p, razones }) => {
      const difV = p.pu ? precio_unitario / p.pu - 1 : 0, otraV = difV > 3 || difV < -0.75;
      const dif = p.cu && costo ? costo / p.cu - 1 : null, otra = dif != null && (dif > 3 || dif < -0.75);
      if (dif != null && !otra && Math.abs(dif) > 0.15 && avisos.length < 2)
        avisos.push(`Costo ${(dif * 100).toFixed(0)}% contra "${p.id.slice(0, 50)}" (${Math.round(p.cu).toLocaleString("es-AR")} ${p.mon}, ${p.fe.split("-").reverse().join("-")}): explicar la diferencia rubro por rubro (P8)`);
      return { id: p.id, fecha: p.fe, cliente: p.cl, descripcion: p.d, oferta: p.of, pu: p.pu, cu: p.cu, cnota: p.cno, moneda: p.mon, factor: p.fac, reparto: p.rep,
        dif, otra, ojo: dif != null && !otra && Math.abs(dif) > 0.15, difV, otraV, razones, subtipo: T.subNom[p.sub] || "" };
    });
    if (filas.length && !filas.some(f => f.cu)) avisos.push("Ninguno de los 5 tiene costo por equipo en su ficha: la comparación es solo de precio de venta");
    if (!filas.length) avisos.push(`No hay antecedentes de la familia ${familia} con precio en el índice: comparar a mano`);
    if (q.subtipo && !res.slice(0, 5).some(r => r.p.sub === q.subtipo)) avisos.push(`Ninguno de los 5 es del mismo subtipo (${T.subNom[q.subtipo] || q.subtipo}): pedir a Claude que busque más antecedentes`);
    return { familia, nombreFamilia: A.familias[familia] || familia, subtipo: q.subtipo, nombreSubtipo: T.subNom[q.subtipo] || "", consulta: q, filas, avisos, matN, moN };
  }
  return { comparar, buscar, palabras, etiquetas, clasificar: (pr, re, f, A) => clasificar(pr, re, f, A, tablas(A)) };
})();
if (typeof module !== "undefined") module.exports = Antecedentes;
