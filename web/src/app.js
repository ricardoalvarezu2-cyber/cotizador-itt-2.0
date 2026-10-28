// Cotizador ITT — página. Usa Motor (cálculo), Busqueda (catálogos y controles) y Documentos (descargas).
// Guardado: colección "cotizaciones" (cotización completa: cot = cotizacion.json, oferta = oferta.json), "resumenes" (lista liviana),
// "cotizaciones/<id>/versiones" (historial), "firmantes", "config/indices" (dólar e índices que actualiza la tarea semanal) y "pedidos"
// (archivos y trabajos para Claude Code; ver asistente.js). window.ITT expone el estado y las funciones que usa el chat (asistente.js).
(async function () {
  const $ = s => document.querySelector(s);
  const E = Documentos.esc, usd = Documentos.usd, num = Documentos.num, F = Documentos.fecha, FH = Documentos.fechaHora;
  const NUM = v => Documentos.numeroDe(v), NI = Documentos.NI; // números en formato argentino (lectura y campo editable)
  const app = $("#app"), capa = $("#capa");
  const ESTADOS = ["borrador", "revisado", "aprobado", "enviado"];
  const TABS = [["datos", "Datos"], ["materiales", "Materiales"], ["servicios", "MO y servicios"], ["plazo", "Plazo"], ["oferta", "Oferta"], ["resumen", "Resumen y descargas"]];
  const S = {
    datos: null, db: null, dl: null, assets: null, lista: [], firmantes: [], id: null, doc: null, tab: "resumen",
    fm: { fam: "" }, fs: { hoja: "" }, selM: new Map(), selS: new Map(), vistaItems: { m: { f: "", o: "" }, s: { f: "", o: "" } }, catTab: "m",
    hist: [], rehacer: [], base: "", sold: [{ dn: "2", sch: "80", bw: "", sw: "", olet: "", tipoOlet: "cupla" }],
    ultVersion: 0, timer: null, guardando: false, pendiente: false, vista: "inicio"
  };
  const hoy = () => new Date().toISOString().slice(0, 10);
  const clon = o => JSON.parse(JSON.stringify(o));
  let toastT;
  const toast = t => { const el = $("#toast"); el.textContent = t; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => (el.hidden = true), 4200); };

  // ------------------------------------------------------------------ carga
  try {
    S.datos = await (await fetch("datos.json")).json();
  } catch (e) {
    app.innerHTML = `<div class="aviso bad"><b>No se pudieron cargar los catálogos.</b><p>Recargá la página. Si sigue, avisale a quien mantiene el cotizador.</p></div>`;
    return;
  }
  const usar = n => (window.claude && window.claude.use ? window.claude.use(n).catch(() => null) : Promise.resolve(null));
  [S.db, S.dl, S.assets] = await Promise.all([usar("db"), usar("downloads"), usar("assets")]);
  if (S.db) {
    try {
      const c = await S.db.doc("config/indices").get();
      if (c.exists && c.data().generado > S.datos.generado) Object.assign(S.datos, { indices: c.data().indices, dolar: c.data().dolar, generado_indices: c.data().generado });
    } catch (e) { /* sigue con los índices publicados */ }
    S.db.collection("resumenes").onSnapshot(sn => { S.lista = sn.docs.map(d => ({ id: d.id, ...d.data() })); if (S.vista === "inicio") render(); },
      e => toast("No se pudo leer la lista de cotizaciones: " + (e.message || e.code)));
    S.db.collection("firmantes").onSnapshot(sn => { S.firmantes = sn.docs.map(d => ({ id: d.id, ...d.data() })); if (S.vista !== "cot" || S.tab === "datos") render(); });
  }
  const ultIdx = S.datos.indices[S.datos.indices.length - 1];
  const fechaDatos = S.datos.generado_indices || S.datos.generado;
  const viejo = (Date.now() - new Date(fechaDatos).getTime()) / 864e5 > 9;
  $("#datos-al").textContent = `Dólar e índices al ${F(fechaDatos)} · BNA ${num(ultIdx.dolar, 2)}` + (viejo ? " · DESACTUALIZADO" : "");
  $("#datos-al").classList.toggle("viejo", viejo);

  // ------------------------------------------------------------------ guardado automático
  function resumenDe(doc) {
    const c = Motor.calcular(doc.cot, S.datos.indices);
    return { codigo: doc.cot.codigo, titulo: doc.cot.titulo, cliente: doc.cot.cliente?.nombre || "", estado: doc.cot.estado, unitario: c.precio_unitario, total: c.total, actualizado: new Date().toISOString() };
  }
  function guardarPronto() {
    S.pendiente = true; marcarGuardado("cambios sin guardar…");
    clearTimeout(S.timer); S.timer = setTimeout(guardar, 1200);
  }
  async function guardar() {
    if (!S.doc || !S.id) return;
    if (!S.db) { marcarGuardado("sin conexión con la base: los cambios no se guardan"); return; }
    if (S.guardando) { S.timer = setTimeout(guardar, 800); return; }
    S.guardando = true; S.pendiente = false;
    const ahora = estadoJSON();
    if (!S.restaurando && S.base && ahora !== S.base) { S.hist.push(S.base); if (S.hist.length > 60) S.hist.shift(); S.rehacer = []; }
    S.base = ahora; S.restaurando = false;
    const doc = clon(S.doc); doc.guardado = new Date().toISOString(); delete doc.editor; S.miGuardado = doc.guardado;
    try {
      await S.db.doc("cotizaciones/" + S.id).set(doc);
      await S.db.doc("resumenes/" + S.id).set(resumenDe(doc));
      if (Date.now() - S.ultVersion > 10 * 60e3) { S.ultVersion = Date.now(); await versionar(doc); }
      marcarGuardado("guardado " + new Date().toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" }));
    } catch (e) {
      marcarGuardado("no se pudo guardar: " + (e.message || e.code) + " · se reintenta");
      S.timer = setTimeout(guardar, 5000);
    } finally { S.guardando = false; }
  }
  async function versionar(doc) {
    const col = S.db.collection(`cotizaciones/${S.id}/versiones`);
    await col.doc(String(Date.now())).set({ cot: doc.cot, oferta: doc.oferta, guardado: doc.guardado, estado: doc.cot.estado });
    const vs = await col.orderBy("guardado", "desc").get();
    for (const d of vs.docs.slice(20)) await col.doc(d.id).delete();
  }
  // Deshacer / rehacer de cualquier cambio (botones y Ctrl+Z / Ctrl+Y fuera de los campos de texto). Cada guardado es un paso.
  const estadoJSON = () => JSON.stringify({ cot: S.doc.cot, oferta: S.doc.oferta });
  function aplicarEstado(json) {
    const d = JSON.parse(json); S.doc.cot = d.cot; S.doc.oferta = d.oferta; S.base = json; S.restaurando = true;
    guardarPronto(); render();
  }
  function deshacer() {
    if (!S.doc) return;
    const ahora = estadoJSON();
    if (ahora !== S.base) { S.rehacer.push(ahora); aplicarEstado(S.base); }
    else if (S.hist.length) { S.rehacer.push(ahora); aplicarEstado(S.hist.pop()); }
    else return toast("No hay más cambios para deshacer");
    toast("Deshecho");
  }
  function rehacer() {
    if (!S.doc || !S.rehacer.length) return toast("No hay nada para rehacer");
    S.hist.push(estadoJSON()); aplicarEstado(S.rehacer.pop()); toast("Rehecho");
  }
  document.addEventListener("keydown", e => {
    if (S.vista !== "cot" || !S.doc || !(e.ctrlKey || e.metaKey)) return;
    if (e.target.closest("input, textarea, select, [contenteditable]")) return; // ahí vale el deshacer del navegador
    const k = e.key.toLowerCase();
    if (k === "z" && !e.shiftKey) { e.preventDefault(); deshacer(); }
    else if (k === "y" || (k === "z" && e.shiftKey)) { e.preventDefault(); rehacer(); }
  });
  function marcarGuardado(t) { const el = $("#guardado"); if (el) el.textContent = t; }
  window.addEventListener("beforeunload", () => { if (S.pendiente) guardar(); });

  // ------------------------------------------------------------------ navegación
  function ruta() {
    const h = location.hash.slice(1);
    if (h.startsWith("c-")) abrir(h.slice(2));
    else { S.vista = ["firmantes", "pedidos", "catalogos"].includes(h) ? h : "inicio"; S.id = null; S.doc = null; S.desuscribir?.(); render(); }
  }
  window.addEventListener("hashchange", ruta);
  async function abrir(id) {
    if (S.id === id && S.doc) { S.vista = "cot"; render(); return; }
    if (S.pendiente) await guardar();
    S.vista = "cot"; S.id = id; S.doc = null; S.ultVersion = 0;
    app.innerHTML = `<div class="vacio">Abriendo la cotización…</div>`;
    if (!S.db) { app.innerHTML = `<div class="aviso bad">No hay conexión con la base de cotizaciones en esta vista.</div>`; return; }
    const d = await S.db.doc("cotizaciones/" + id).get();
    if (!d.exists) { app.innerHTML = `<div class="aviso bad">No existe esa cotización. <a href="#inicio">Volver a la lista</a></div>`; return; }
    S.doc = clon(d.data());
    S.doc.cot.items = S.doc.cot.items || [];
    S.miGuardado = S.doc.guardado; S.hist = []; S.rehacer = []; S.base = estadoJSON();
    escucharCambios(id);
    render();
  }
  // Si Claude Code (u otra persona) guarda esta cotización mientras está abierta, se muestra lo nuevo
  function escucharCambios(id) {
    S.desuscribir?.();
    S.desuscribir = S.db.doc("cotizaciones/" + id).onSnapshot(sn => {
      if (S.id !== id || !sn.exists) return;
      const d = sn.data();
      if (!d.guardado || d.guardado === S.miGuardado) return;
      if (S.pendiente) { toast("Otra persona o Claude Code cambió esta cotización: se guardan tus cambios encima. Revisá las versiones si hace falta."); return; }
      S.doc = clon(d); S.doc.cot.items ??= []; S.miGuardado = d.guardado; S.base = estadoJSON(); render();
      toast(d.editor === "claude-code" ? "Claude Code actualizó esta cotización" : "La cotización se actualizó con cambios de otra persona");
    }, () => {});
  }
  let secuenciaId = 0;
  function nuevoId() { return "c" + Date.now().toString(36) + (++secuenciaId).toString(36) + Math.random().toString(36).slice(2, 5); }
  async function crearCotizacion({ titulo = "", cliente = "", codigo = "COT26-CCCC-NNN" } = {}) {
    const id = nuevoId(), base = clon(S.datos.plantilla_cotizacion), of = clon(S.datos.plantilla_oferta);
    Object.assign(base, { codigo, revision: "Rev 0", estado: "borrador", fecha: hoy(), titulo, items: [], cliente: { nombre: cliente, codigo_itt: "", comprador: "" }, firmante_id: S.firmantes[0]?.id || "" });
    base.parametros.fecha_referencia = hoy(); base.plazo = { dias: 60, texto: "desde OC", tareas: [], nota: "" };
    of.estado = "borrador"; of.oferta = { numero: "PRES [a asignar]", revision: "A", fecha: F(hoy()), descripcion_revision: "Emisión original" };
    of.cliente = { nombre: cliente, contacto: "", referencia: "", proyecto: "" };
    await S.db.doc("cotizaciones/" + id).set({ cot: base, oferta: of, creado: new Date().toISOString() });
    await S.db.doc("resumenes/" + id).set({ codigo, titulo, cliente, estado: "borrador", unitario: 0, total: 0, actualizado: new Date().toISOString() });
    return id;
  }
  async function duplicarCotizacion(origen) {
    const d = await S.db.doc("cotizaciones/" + origen).get(); if (!d.exists) return null;
    const doc = clon(d.data()), id = nuevoId();
    doc.cot.estado = "borrador"; doc.oferta.estado = "borrador"; doc.cot.codigo += " (copia)"; doc.cot.fecha = hoy(); doc.creado = new Date().toISOString(); delete doc.editor; delete doc.cot.aprobacion; delete doc.cot.indices_congelados;
    await S.db.doc("cotizaciones/" + id).set(doc); await S.db.doc("resumenes/" + id).set(resumenDe(doc));
    return id;
  }
  // Cambio de estado (lo usan el diálogo y el chat). Al revisar se congelan los índices: el precio ya no cambia solo
  // cuando la base suma un mes nuevo. Al volver a borrador se descongelan y se borra la aprobación.
  function cambiarEstado(d) {
    const cot = S.doc.cot;
    if (d === "borrador") { delete cot.aprobacion; delete cot.indices_congelados; }
    else if (!cot.indices_congelados) cot.indices_congelados = { fecha: hoy(), filas: clon(S.datos.indices) };
    cot.estado = d; S.doc.oferta.estado = d; S.ultVersion = 0;
  }
  async function borrarCotizacion(id) { await S.db.doc("resumenes/" + id).delete(); await S.db.doc("cotizaciones/" + id).delete(); }

  // ------------------------------------------------------------------ calculadoras (las usan los botones y el chat)
  const tarifaPH = () => S.datos.servicios.filter(x => x.ut === "USD/hora" && /hidr/i.test(x.s) && x.p && !/ESTIMADO/.test(x.al)).sort((a, b) => String(b.fe).localeCompare(String(a.fe)))[0];
  const tarifasPintura = () => S.datos.servicios.filter(s => s.ut === "USD/m2" && s.p && !/ESTIMADO/.test(s.al)).sort((a, b) => String(b.fe).localeCompare(String(a.fe)));
  function agregarSoldaduras(filas) {
    const sol = Busqueda.soldadura(S.datos, filas), t = Busqueda.tarifa(S.datos, "soldadura", "soldadura piping");
    if (!sol.pulg || !t) throw new Error("No hay juntas o falta la tarifa de soldadura");
    const it = { id: siguienteId("S"), pos: "MO", grupo: "mo", descripcion: "Soldaduras (calculadas por diámetro y schedule)", especificacion: sol.detalle.join("; "), cantidad: sol.pulg, unidad: "pulg",
      fuentes: [{ tipo: "ant", precio: +t.valor, proveedor: "Costo propio de planta: " + t.nota, origen: t.fuente, fecha: t.fecha.length > 7 ? t.fecha : t.fecha + "-31", coincide: "igual" }] };
    S.doc.cot.items.push(it); return { it, sol };
  }
  function agregarRx(filas, pct) {
    const sol = Busqueda.soldadura(S.datos, filas);
    const ch = Math.ceil(sol.placas_chicas * pct / 100), gr = Math.ceil(sol.placas_grandes * pct / 100), sv = Math.max(1, Math.ceil((ch + gr) / 40));
    if (!ch && !gr) throw new Error("No hay placas: cargá juntas a tope (BW)");
    const tc = Busqueda.tarifa(S.datos, "end", "placa radiografica chica", ["tercero"]), tg = Busqueda.tarifa(S.datos, "end", "placa radiografica grande", ["tercero"]), ts = Busqueda.tarifa(S.datos, "end", "servicio de radiografia (antonelli)", ["tercero"]);
    const costo = ch * (+tc?.valor || 0) + gr * (+tg?.valor || 0) + sv * (+ts?.valor || 0);
    const it = { id: siguienteId("S"), pos: "RX", grupo: "servicio", descripcion: `Radiografía ${pct}% de las juntas a tope`, especificacion: `${ch} placas chicas, ${gr} grandes, ${sv} servicio(s)`, cantidad: 1, unidad: "gl",
      fuentes: [{ tipo: "cot", precio: Math.round(costo * 100) / 100, proveedor: "NDT Antonelli (tarifas nov-2025)", origen: "fuentes_originales/antonelli_end_2025-11.pdf", fecha: "2025-11-03", coincide: "igual" }] };
    S.doc.cot.items.push(it); return { it };
  }
  function m2Canos() {
    let m2 = 0;
    for (const it of S.doc.cot.items.filter(i => i.grupo === "material")) {
      const d = Busqueda.norm(it.descripcion + " " + (it.especificacion || ""));
      if (!/\bcano\b|\bniple|\btubo\b/.test(d)) continue;
      const dn = parseFloat(String(it.plano?.diametro || "").replace(/"/g, "").replace(" 1/2", ".5")) || null, sch = (String(it.plano?.serie_sch || "").match(/\d+|STD|XS/i) || ["40"])[0].toUpperCase();
      const fila = S.datos.canos.find(c => dn && Math.abs(c.dn - dn) < 1e-6 && (c.sch === sch || c.cl === sch));
      const largo = it.unidad === "m" ? 1 : (parseFloat((d.match(/(\d[\d.]*)\s?mm/) || [])[1]?.replace(".", "")) || 0) / 1000;
      if (fila && largo) m2 += fila.m2 * largo * it.cantidad;
    }
    return m2;
  }
  function agregarPintura(m2, codigo) {
    const s = S.datos.servicios.find(x => x.c === codigo) || tarifasPintura()[0];
    if (!m2 || !s) throw new Error("Faltan los m² o no hay tarifa de pintura");
    const it = { id: siguienteId("S"), pos: "PIN", grupo: "servicio", descripcion: "Granallado y pintura", especificacion: `${m2} m² · ${s.s}`, cantidad: m2, unidad: "m2",
      fuentes: [{ tipo: "ant", precio: s.t, proveedor: `${s.pr.slice(0, 60)} · ${s.c}`, origen: s.o, fecha: s.fe, coincide: "similar", diferencia: "Esquema de pintura a confirmar con el pliego" }] };
    S.doc.cot.items.push(it); return { it, tarifa: s };
  }
  function agregarPH(h) {
    const s = tarifaPH(); if (!s) throw new Error("No hay tarifa de prueba hidráulica");
    const it = { id: siguienteId("S"), pos: "PH", grupo: "servicio", descripcion: "Prueba hidráulica (horas de planta)", especificacion: `${h} h`, cantidad: h, unidad: "h",
      fuentes: [{ tipo: "ant", precio: s.t, proveedor: `${s.pr.slice(0, 60)} · ${s.c}`, origen: s.o, fecha: s.fe, coincide: "igual" }] };
    S.doc.cot.items.push(it); return { it };
  }

  // ------------------------------------------------------------------ utilidades de datos
  const leerRuta = (o, p) => p.split(".").reduce((a, k) => (a == null ? a : a[k]), o);
  const ponerRuta = (o, p, v) => { const ks = p.split("."); let a = o; ks.slice(0, -1).forEach(k => (a = a[k] ??= {})); a[ks.at(-1)] = v; };
  const firmanteActual = () => S.firmantes.find(f => f.id === S.doc?.cot.firmante_id);
  function calc() { return Motor.calcular(S.doc.cot, S.datos.indices); }
  function siguienteId(pref) { const n = S.doc.cot.items.filter(i => String(i.id).startsWith(pref)).map(i => parseInt(String(i.id).slice(pref.length)) || 0); return pref + String(Math.max(0, ...n) + 1).padStart(2, "0"); }

  // ------------------------------------------------------------------ render
  function render() {
    for (const [id, v] of [["nav-inicio", "inicio"], ["nav-catalogos", "catalogos"], ["nav-pedidos", "pedidos"], ["nav-firmantes", "firmantes"]]) $("#" + id).toggleAttribute("aria-current", S.vista === v), S.vista === v && $("#" + id).setAttribute("aria-current", "page");
    if (S.vista === "firmantes") return renderFirmantes();
    if (S.vista === "catalogos") return renderCatalogos();
    if (S.vista === "pedidos") return typeof Asistente !== "undefined" ? Asistente.renderPedidos(app) : (app.innerHTML = "");
    if (S.vista === "cot" && S.doc) return renderCot();
    if (S.vista === "inicio") return renderInicio();
  }

  function renderInicio() {
    const filas = [...S.lista].sort((a, b) => String(b.actualizado).localeCompare(String(a.actualizado)));
    const pill = e => `<span class="pill ${e === "aprobado" || e === "enviado" ? "ok" : e === "revisado" ? "info" : "warn"}">${E(e)}</span>`;
    app.innerHTML = `<section><div class="sec-head"><h1>Cotizaciones</h1><span class="eyebrow">ITT S.A. · USD sin IVA · EXW Quilmes Oeste</span></div>
      <div class="fila"><button class="prim" data-a="nueva">Nueva cotización</button>
      ${S.db ? "" : '<span class="err">Sin conexión con la base: no se puede guardar en esta vista.</span>'}</div>
      ${filas.length ? `<div class="tbl"><table class="tarjetas"><thead><tr><th>Código</th><th>Cotización</th><th>Cliente</th><th>Estado</th><th class="n">Unitario USD</th><th class="n">Total USD</th><th>Actualizada</th><th></th></tr></thead><tbody>
        ${filas.map(r => `<tr><td class="mono">${E(r.codigo)}</td><td><a href="#c-${E(r.id)}"><b>${E(r.titulo || "(sin título)")}</b></a></td><td data-l="Cliente">${E(r.cliente)}</td><td>${pill(r.estado)}</td>
          <td class="n" data-l="Unitario USD">${num(r.unitario)}</td><td class="n" data-l="Total USD">${num(r.total)}</td><td class="small muted" data-l="Actualizada">${FH(r.actualizado)}</td>
          <td class="fila fin"><button class="chico" data-a="duplicar" data-id="${E(r.id)}">Duplicar</button><button class="chico peligro" data-a="borrar" data-id="${E(r.id)}">Borrar</button></td></tr>`).join("")}
      </tbody></table></div>` : `<div class="vacio"><b>Todavía no hay cotizaciones guardadas.</b><span>Creá la primera con "Nueva cotización": cargás los datos, buscás materiales y servicios en los catálogos, y descargás la planilla, el informe y las ofertas.</span></div>`}
      <p class="small muted">Catálogos: ${S.datos.materiales.length.toLocaleString("es-AR")} materiales y ${S.datos.servicios.length} servicios, precios sin IVA, con fecha y origen. Todo se guarda solo y se copia a GitHub una vez por semana.</p></section>`;
  }

  function renderCot() {
    const c = calc(), cot = S.doc.cot, eq = cot.equipo || { singular: "equipo", plural: "equipos" };
    const n = g => cot.items.filter(i => (g === "material") === (i.grupo === "material")).length;
    const avs = Busqueda.avisos(cot);
    app.innerHTML = `
      <header class="cab"><div style="display:flex;flex-direction:column;gap:6px;min-width:0">
        <span class="eyebrow"><a href="#inicio">Cotizaciones</a> / ${E(cot.codigo)}</span>
        <h1>${E(cot.titulo || "Cotización sin título")}</h1>
        <div class="meta"><span>Cliente: <b>${E(cot.cliente?.nombre || "—")}</b></span><span>${E(cot.codigo)} ${E(cot.revision || "")}</span><span>Preparó: ${E(firmanteActual()?.nombre || "—")}</span></div></div>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:stretch"><div class="estados" role="group" aria-label="Estado">${ESTADOS.map(e => `<button class="chico" data-a="estado" data-v="${e}" aria-pressed="${cot.estado === e}">${e}</button>`).join("")}</div>
        <div class="fila fin"><button class="chico" data-a="deshacer" title="Deshacer (Ctrl+Z)">↶ Deshacer</button><button class="chico" data-a="rehacer" title="Rehacer (Ctrl+Y)">↷ Rehacer</button>
        <span class="guardado" id="guardado">${S.pendiente ? "cambios sin guardar…" : "guardado"}</span></div></div></header>
      ${cot.estado === "borrador" ? `<div class="aviso"><b>Borrador, sin revisar.</b><span class="small">Los números se muestran como borrador hasta pasar a "revisado". La herramienta nunca envía nada al cliente.</span></div>` : ""}
      <div class="totales" id="totales">${totalesHtml(c, eq)}</div>
      <div class="tabs" role="tablist">${TABS.map(([k, t], i) => `<button role="tab" aria-selected="${S.tab === k}" data-a="tab" data-v="${k}"><span class="paso">${i + 1}</span>${t}${k === "materiales" ? `<span class="cnt">${n("material")}</span>` : k === "servicios" ? `<span class="cnt">${n("mo")}</span>` : k === "resumen" && avs.length ? `<span class="cnt alerta">${avs.length} avisos</span>` : ""}</button>`).join("")}</div>
      <div id="tab">${{ datos: tabDatos, materiales: tabMateriales, servicios: tabServicios, plazo: tabPlazo, oferta: tabOferta, resumen: tabResumen }[S.tab]()}</div>`;
    if (S.tab === "materiales") pintarResultadosMat();
    if (S.tab === "servicios") pintarResultadosSrv();
  }

  function totalesHtml(c, eq) {
    const p = S.doc.cot.parametros;
    return `<div><span class="s">Costo / ${E(eq.singular)}</span><span class="v">${num(c.costo)}</span><span class="s">ajuste por inflación incluido ${num(c.costo - c.costo0)}</span></div>
      <div class="prim"><span class="s">Precio unitario USD</span><span class="v">${num(c.precio_unitario)}</span><span class="s">factores ${p.FM} / ${p.FMO}${c.tav ? ` · Taval ${c.ftv}` : ""}</span></div>
      <div><span class="s">Cantidad</span><span class="v">${num(p.N, 0)}</span><span class="s">${E(eq.plural)}</span></div>
      <div><span class="s">Total de la oferta USD</span><span class="v">${num(c.total)}</span><span class="s">sin IVA${p.TRANS ? " · con flete" : " · EXW"}</span></div>`;
  }
  function refrescar() {
    if (!S.doc) return;
    const c = calc(), eq = S.doc.cot.equipo || { singular: "equipo", plural: "equipos" };
    const t = $("#totales"); if (t) t.innerHTML = totalesHtml(c, eq);
    for (const f of c.filas) { const el = document.querySelector(`[data-sub="${CSS.escape(f.id)}"]`); if (el) el.textContent = num(f.ajustado); }
    document.querySelectorAll("[data-subtot]").forEach(el => { el.textContent = num(S.doc.cot.items.filter(i => el.dataset.subtot === "material" ? i.grupo === "material" : i.grupo !== "material").reduce((a, i) => a + (c.filas.find(f => f.id === i.id)?.ajustado || 0), 0)); });
  }

  // ------------------------------------------------------------------ pestaña Datos
  const campo = (etq, ruta, tipo = "text", extra = "") => {
    const v = leerRuta(S.doc, ruta) ?? "";
    if (tipo === "date") return `<label><span>${etq}</span><input id="f-${ruta.replace(/\./g, "-")}" type="text" inputmode="numeric" placeholder="DD-MM-AAAA" data-b="${ruta}" data-t="fecha" value="${E(F(v))}" ${extra}></label>`;
    return `<label><span>${etq}</span><input id="f-${ruta.replace(/\./g, "-")}" type="text" ${tipo === "number" ? 'inputmode="decimal" class="num"' : ""} data-b="${ruta}" data-t="${tipo}" value="${E(tipo === "number" ? NI(v) : v)}" ${extra}></label>`;
  };
  function tabDatos() {
    const cot = S.doc.cot;
    return `<div class="grid2"><section class="panel"><h3>Cotización y cliente</h3><div class="campos">
      ${campo("Código", "cot.codigo")}${campo("Revisión", "cot.revision")}
      <label class="ancho"><span>Título (equipo y pedido)</span><input id="f-titulo" data-b="cot.titulo" value="${E(cot.titulo || "")}"></label>
      <label class="ancho"><span>Cliente</span><input id="f-cliente" list="clientes" data-b="cot.cliente.nombre" value="${E(cot.cliente?.nombre || "")}">
        <datalist id="clientes">${S.datos.clientes.map(c => `<option value="${E(c.n)}">${E(c.c)}</option>`).join("")}</datalist></label>
      ${campo("Código de cliente ITT", "cot.cliente.codigo_itt")}${campo("Comprador", "cot.cliente.comprador")}
      ${campo("Equipo (singular)", "cot.equipo.singular")}${campo("Equipo (plural)", "cot.equipo.plural")}
      <label class="ancho"><span>Preparó (firmante)</span><select id="f-firmante" data-b="cot.firmante_id"><option value="">— elegir —</option>${S.firmantes.map(f => `<option value="${E(f.id)}" ${f.id === cot.firmante_id ? "selected" : ""}>${E(f.nombre)} · ${E(f.cargo || "")}</option>`).join("")}</select>
        <span class="small">${S.firmantes.length ? "" : "No hay firmantes cargados: agregalos en la sección Firmantes."}</span></label>
      </div></section>
      <section class="panel"><h3>Parámetros de cálculo</h3><div class="campos">
      ${campo("Cantidad de equipos", "cot.parametros.N", "number")}${campo("Factor de materiales", "cot.parametros.FM", "number")}
      ${campo("Factor de MO y servicios", "cot.parametros.FMO", "number")}${campo("Factor de válvulas Taval (todas)", "cot.parametros.FTV", "number", 'placeholder="1"')}${campo("Contingencia materiales (%)", "cot.parametros.CONT", "number")}
      ${campo("Fecha de referencia (ajuste a hoy)", "cot.parametros.fecha_referencia", "date")}
      <label><span>Ajuste por inflación</span><select id="f-aj" data-b="cot.parametros.AJ" data-t="number"><option value="1" ${cot.parametros.AJ ? "selected" : ""}>Aplicar</option><option value="0" ${cot.parametros.AJ ? "" : "selected"}>No aplicar</option></select></label>
      <label><span>Flete en el precio</span><select id="f-trans" data-b="cot.parametros.TRANS" data-t="number"><option value="0" ${cot.parametros.TRANS ? "" : "selected"}>No (EXW Quilmes Oeste)</option><option value="1" ${cot.parametros.TRANS ? "selected" : ""}>Sí</option></select></label>
      ${campo("Tipo de cambio ARS/USD (flete)", "cot.parametros.TC", "number")}${campo("Flete ARS por envío", "cot.parametros.TR_ARS", "number")}
      ${campo("Embalaje USD por envío", "cot.parametros.TR_EMB", "number")}${campo("Factor flete", "cot.parametros.TR_F", "number")}
      </div><p class="small muted">El factor de venta lo define la dirección; la herramienta propone 1,35 y muestra escenarios en Resumen. Todos los precios sin IVA.</p></section></div>`;
  }

  // ------------------------------------------------------------------ tablas de ítems
  const FILTROS = [["", "Todos"], ["avisos", "Con avisos"], ["bad", "Para corregir"], ["sinprecio", "Sin precio"], ["est", "Estimados"], ["similar", "Similares"]];
  const ORDENES = [["", "Como se cargaron"], ["pos", "Posición"], ["importe", "Mayor importe"], ["desc", "Descripción"], ["fecha", "Precio más viejo"]];
  function tablaItems(grupoMat) {
    const c = calc(), todos = S.doc.cot.items.filter(i => grupoMat ? i.grupo === "material" : i.grupo !== "material");
    const avs = Busqueda.avisos(S.doc.cot), porItem = {};
    for (const a of avs) (porItem[a.id] ??= []).push(a);
    const v = S.vistaItems[grupoMat ? "m" : "s"], imp = id => c.filas.find(f => f.id === id)?.ajustado || 0;
    const pasa = { "": () => true, avisos: i => porItem[i.id], bad: i => porItem[i.id]?.some(a => a.nivel === "bad"), sinprecio: i => !i.fuentes[0].precio,
      est: i => i.fuentes[0].tipo === "est", similar: i => i.fuentes[0].coincide === "similar" }[v.f] || (() => true);
    const natural = (a, b) => (parseFloat(a.pos) || 9e9) - (parseFloat(b.pos) || 9e9) || String(a.pos).localeCompare(String(b.pos));
    const ord = { pos: natural, importe: (a, b) => imp(b.id) - imp(a.id), desc: (a, b) => a.descripcion.localeCompare(b.descripcion), fecha: (a, b) => String(a.fuentes[0].fecha).localeCompare(String(b.fuentes[0].fecha)) }[v.o];
    let items = todos.filter(pasa); if (ord) items = [...items].sort(ord);
    const k = grupoMat ? "m" : "s";
    const controles = todos.length ? `<div class="fila filtros-items"><label><span>Mostrar</span><select id="fi-${k}" data-vi="${k}" data-c="f">${FILTROS.map(([x, n]) => `<option value="${x}" ${v.f === x ? "selected" : ""}>${n}</option>`).join("")}</select></label>
      <label><span>Ordenar</span><select id="oi-${k}" data-vi="${k}" data-c="o">${ORDENES.map(([x, n]) => `<option value="${x}" ${v.o === x ? "selected" : ""}>${n}</option>`).join("")}</select></label>
      <span class="small muted">${items.length} de ${todos.length} ítem(s)</span></div>` : "";
    const celdaAvisos = it => { const a = porItem[it.id]; if (!a) return `<span class="muted small">—</span>`;
      const bad = a.some(x => x.nivel === "bad");
      return `<details class="avs ${bad ? "bad" : "warn"}"><summary title="${E(a.map(x => x.corto).join(" · "))}">${bad ? "✖" : "⚠"} ${a.length}</summary><ul>${a.map(x => `<li>${E(x.corto)}</li>`).join("")}</ul></details>`; };
    if (todos.length && !items.length) return controles + `<div class="vacio">Ningún ítem con ese filtro.</div>`;
    if (!items.length) return `<div class="vacio">${grupoMat ? "Todavía no hay materiales. Buscalos abajo en el catálogo y agregalos, o cargá uno a mano." : "Todavía no hay mano de obra ni servicios. Buscalos en el catálogo o usá las calculadoras."}</div>`;
    const cl = s => s.coincide === "igual" ? "ok" : s.coincide === "similar" ? "warn" : "bad";
    return controles + `<div class="tbl"><table><thead><tr><th>Pos</th><th>Ítem</th><th class="n">Cant.</th><th>Un.</th><th class="n">USD unit.</th><th>Fuente</th><th>Coincide</th><th>Avisos</th><th class="n">USD ajustado</th><th></th></tr></thead><tbody>
      ${items.map(it => { const s = it.fuentes[0]; return `<tr>
        <td class="ed" style="width:60px"><input id="p-${E(it.id)}" data-it="${E(it.id)}" data-c="pos" value="${E(it.pos)}" style="width:52px"></td>
        <td><div class="d">${E(it.descripcion)}</div><div class="sp">${E(it.especificacion || "")}</div></td>
        <td class="ed"><input id="q-${E(it.id)}" type="text" inputmode="decimal" class="num" data-it="${E(it.id)}" data-c="cantidad" value="${NI(it.cantidad)}"></td><td>${E(it.unidad)}</td>
        <td class="ed"><input id="u-${E(it.id)}" type="text" inputmode="decimal" class="num" data-it="${E(it.id)}" data-c="precio" value="${NI(s.precio)}"></td>
        <td class="small"><span class="pill ${s.tipo === "est" ? "bad" : s.tipo === "cot" ? "ok" : "info"}">${E(Documentos.TIPOS[s.tipo] || s.tipo)}</span><br>${E(s.proveedor)}<br><span class="muted">${E(F(s.fecha))}</span></td>
        <td><span class="pill ${cl(s)}">${E(Documentos.COINC[s.coincide] || "—")}</span>${s.diferencia ? `<div class="sp">${E(s.diferencia.slice(0, 140))}</div>` : ""}</td>
        <td>${celdaAvisos(it)}</td>
        <td class="n" data-sub="${E(it.id)}">${num(c.filas.find(f => f.id === it.id)?.ajustado)}</td>
        <td><div class="fila fin"><button class="chico" data-a="editar" data-id="${E(it.id)}">Editar</button><button class="chico peligro" data-a="quitar" data-id="${E(it.id)}">Quitar</button></div></td></tr>`; }).join("")}
      <tr class="total"><td></td><td>Subtotal por ${E(S.doc.cot.equipo?.singular || "equipo")} (con ajuste por inflación${items.length < todos.length ? ", todos los ítems" : ""})</td><td colspan="6"></td><td class="n" data-subtot="${grupoMat ? "material" : "srv"}"></td><td></td></tr></tbody></table></div>`;
  }

  // ------------------------------------------------------------------ selección múltiple en los buscadores
  function barraSel(k) {
    const n = (k === "m" ? S.selM : S.selS).size;
    return `<div class="fila barra-sel" id="sel-${k}" ${n ? "" : "hidden"}><b id="sel-${k}-n">${n} seleccionado(s)</b>
      <button class="prim chico" data-a="agregar-sel" data-k="${k}">Agregar seleccionados</button><button class="chico" data-a="limpiar-sel" data-k="${k}">Quitar selección</button>
      <span class="small muted">La selección se mantiene aunque cambies la búsqueda.</span></div>`;
  }
  function pintarBarraSel(k) {
    const n = (k === "m" ? S.selM : S.selS).size, el = $("#sel-" + k); if (!el) return;
    el.hidden = !n; $("#sel-" + k + "-n").textContent = `${n} seleccionado(s)`;
  }
  function agregarMaterialDe(x, q) {
    const cot = S.doc.cot, it = Busqueda.itemDeMaterial(x.r, x, q, siguienteId("M"));
    it.plano = { diametro: x.r.a.diametro || "", serie_sch: x.r.a.serie ? "#" + x.r.a.serie : x.r.a.schedule ? "sch " + x.r.a.schedule : "", material: x.r.a.material || "", extremos: x.r.a.extremos || "", modelo: [x.r.a.marca, x.r.a.modelo].filter(Boolean).join(" ") };
    it.pos = String(cot.items.filter(i => i.grupo === "material").length + 1);
    cot.items.push(it); return it;
  }

  // ------------------------------------------------------------------ pestaña Materiales
  function tabMateriales() {
    return `<section><div class="sec-head"><h2>Materiales de la cotización</h2><button data-a="manual" data-g="material">Cargar a mano</button></div>${tablaItems(true)}</section>
      ${buscadorMat()}`;
  }
  function buscadorMat() {
    const f = S.fm, fams = S.datos.familias;
    const sel = (campo, etq) => {
      const vs = Busqueda.valores(S.datos, f.fam, campo, f);
      if (!vs.length) return "";
      return `<label><span>${etq}</span><select id="fm-${campo}" data-fm="${campo}"><option value="">— cualquiera —</option>${vs.map(([v, n]) => `<option value="${E(v)}" ${f[campo] === v ? "selected" : ""}>${E(v)} (${n})</option>`).join("")}</select></label>`;
    };
    const cs = f.fam ? Busqueda.campos(S.datos, f.fam) : [];
    const etq = { tipo: "Tipo", diametro: "Ø", diametro2: "Ø 2", serie: "Serie", schedule: "Schedule", material: "Material", trim: "Trim / asiento", extremos: "Extremos", cara: "Cara", medida: "Medida", largo_mm: "Largo mm", espesor_mm: "Espesor mm", costura: "Costura", revestimiento: "Revestimiento", rango: "Rango", conexion: "Conexión", designacion: "Designación" };
    return `<section class="panel" id="bus-mat"><div class="sec-head"><h3>Buscar en el catálogo de materiales</h3><span class="eyebrow">igual primero · después similares con sus diferencias</span></div>
        <label class="bus-gral"><span>Buscar en todo el catálogo (descripción, medidas, material, marca o proveedor)</span><input id="fm-texto" data-fm="texto" type="search" value="${E(f.texto || "")}" placeholder="ej. esférica 2 600 · brida ciega 4 150 · renard · 316L"></label>
        <div class="buscador">
          <label><span>Familia</span><select id="fm-fam" data-fm="fam"><option value="" ${f.fam ? "" : "selected"}>Todas las familias</option>${Object.entries(fams).map(([k, v]) => `<option value="${k}" ${f.fam === k ? "selected" : ""}>${E(v.n)}</option>`).join("")}</select></label>
          ${f.fam ? [...new Set(["tipo", ...cs, ...(["VAL", "INS"].includes(f.fam) ? ["marca"] : [])])].map(c => sel(c, etq[c] || c)).join("") : ""}
        </div>
        <div class="fila"><button class="chico" data-a="limpiar-fm">Limpiar filtros</button><span class="small muted" id="fm-info"></span></div>
        ${S.doc ? barraSel("m") : ""}<div class="lista-res" id="res-mat"></div></section>`;
  }
  function pintarResultadosMat() {
    const box = $("#res-mat"); if (!box) return;
    if (!S.fm.fam && !(S.fm.texto || "").trim()) { $("#fm-info").textContent = ""; box.innerHTML = `<div class="vacio">Escribí arriba para buscar en los ${S.datos.materiales.length.toLocaleString("es-AR")} materiales, o elegí una familia para filtrar por características.</div>`; S.ultMat = []; return; }
    const r = Busqueda.materiales(S.datos, S.fm);
    $("#fm-info").textContent = `${r.total} resultado(s)${r.total > r.res.length ? ` (se muestran ${r.res.length}: agregá palabras para achicar)` : ""}` + (!S.fm.fam ? " · elegí una familia para ver iguales y similares" : r.clasifica ? "" : Busqueda.CON_TIPO.includes(S.fm.fam) ? " · elegí el tipo de pieza para ver iguales y similares" : " · elegí características para comparar") + (r.faltan.length && r.clasifica ? ` · para distinguir igual de similar falta: ${r.faltan.join(", ")}` : "");
    box.innerHTML = r.res.length ? r.res.map((x, i) => {
      const m = x.r, est = x.estado === "igual" ? `<span class="pill ok">igual</span>` : x.estado === "similar" ? `<span class="pill warn">similar</span>` : `<span class="pill info">catálogo</span>`;
      const ch = S.selM.has(m.c);
      return `<div class="resultado ${ch ? "sel" : ""}"><label class="tilde">${S.doc ? `<input type="checkbox" data-selm="${i}" ${ch ? "checked" : ""} ${m.p ? "" : "disabled"} aria-label="Seleccionar">` : ""}${est}</label><div><div class="d">${E(m.d)}</div><div class="small muted">${E(m.c)} · ${E(S.datos.familias[m.f]?.n || "")}${[m.a.marca, m.a.modelo].filter(Boolean).length ? " · " + E([m.a.marca, m.a.modelo].filter(Boolean).join(" ")) : ""}${m.nuevo ? " · nuevo en la página" : ""}</div></div>
        <div class="precio">${m.p ? "USD " + num(m.p) + " / " + E(m.u || "un") : '<span class="err">sin precio confiable</span>'}<div class="small muted">${E(F(m.fe))} · ${E(m.tp)}</div></div>
        <div class="det">${x.difs.length ? "Difiere en: " + E(x.difs.join("; ")) + " · " : ""}${m.al ? "<b>Alerta:</b> " + E(m.al) + " · " : ""}${E(m.pr)} · Origen: ${E(m.o)}${m.n > 1 ? ` · ${m.n} precios en el historial (${num(m.mn)} a ${num(m.mx)})` : ""}</div>
        ${S.doc ? `<div class="acc"><input id="qm-${i}" type="text" inputmode="decimal" class="num" value="${NI(ch ? S.selM.get(m.c).q : 1)}" aria-label="Cantidad"><button class="chico prim" data-a="agregar-mat" data-i="${i}">Agregar</button></div>` : ""}</div>`;
    }).join("") : `<div class="vacio">No hay materiales con esos filtros. Probá quitar alguno o cargalo a mano.</div>`;
    S.ultMat = r.res;
  }

  // ------------------------------------------------------------------ sección Catálogos (consultar precios sin una cotización abierta)
  function renderCatalogos() {
    app.innerHTML = `<section><div class="sec-head"><h1>Catálogos</h1><span class="eyebrow">precios sin IVA, con fecha y origen · para agregar, abrí una cotización</span></div>
      <div class="tabs" role="tablist"><button role="tab" aria-selected="${S.catTab === "m"}" data-a="cat-tab" data-v="m">Materiales<span class="cnt">${S.datos.materiales.length.toLocaleString("es-AR")}</span></button>
        <button role="tab" aria-selected="${S.catTab === "s"}" data-a="cat-tab" data-v="s">MO y servicios<span class="cnt">${S.datos.servicios.length}</span></button></div>
      ${S.catTab === "m" ? buscadorMat() : buscadorSrv()}</section>`;
    if (S.catTab === "m") pintarResultadosMat(); else pintarResultadosSrv();
  }

  // ------------------------------------------------------------------ pestaña MO y servicios
  function tabServicios() {
    const ph = tarifaPH(), pins = tarifasPintura();
    const sol = Busqueda.soldadura(S.datos, S.sold), t = Busqueda.tarifa(S.datos, "soldadura", "soldadura piping");
    const dns = [...new Set(S.datos.soldadura.map(r => r.dn))].sort((a, b) => a - b);
    const schs = ["10", "20", "30", "40", "STD", "60", "80", "XS", "100", "120", "140", "160", "XXS"];
    return `<section><div class="sec-head"><h2>Mano de obra y servicios</h2><button data-a="manual" data-g="servicio">Cargar a mano</button></div>${tablaItems(false)}</section>
      ${panelRubros()}
      <section class="panel"><h3>1. Soldaduras</h3><p class="small muted">Juntas por diámetro y schedule, derivadas de la columna de extremos del plano (BW se suman de a dos extremos; SW, cuplas y olets, una junta cada una).</p>
        <div class="tbl"><table><thead><tr><th>Ø</th><th>Sch</th><th class="n">Juntas BW</th><th class="n">Juntas SW</th><th class="n">Cuplas / olets</th><th>Tipo olet</th><th></th></tr></thead><tbody>
        ${S.sold.map((r, i) => `<tr><td><select id="sd-${i}" data-sold="${i}" data-c="dn">${dns.map(d => `<option ${String(d) === String(r.dn) ? "selected" : ""}>${d}</option>`).join("")}</select></td>
          <td><select id="ss-${i}" data-sold="${i}" data-c="sch">${schs.map(s => `<option ${s === r.sch ? "selected" : ""}>${s}</option>`).join("")}</select></td>
          ${["bw", "sw", "olet"].map(k => `<td class="ed"><input id="s${k}-${i}" type="text" inputmode="decimal" class="num" data-sold="${i}" data-c="${k}" value="${E(r[k])}"></td>`).join("")}
          <td><select id="so-${i}" data-sold="${i}" data-c="tipoOlet"><option value="cupla" ${r.tipoOlet !== "weldolet" ? "selected" : ""}>cupla/sockolet (1,75)</option><option value="weldolet" ${r.tipoOlet === "weldolet" ? "selected" : ""}>weldolet (2,5)</option></select></td>
          <td><button class="chico" data-a="sold-quitar" data-i="${i}" aria-label="Quitar fila">×</button></td></tr>`).join("")}</tbody></table></div>
        <div class="fila"><button class="chico" data-a="sold-fila">Agregar diámetro</button></div>
        <p id="sold-res"><b>${num(sol.pulg, 2)} pulgadas equivalentes</b> × USD ${t ? num(t.valor) : "—"} (costo propio de planta ${E(F(t?.fecha))}) = <b>USD ${num(sol.pulg * (t ? +t.valor : 0))}</b></p>
        <div class="fila"><button class="prim" data-a="sold-agregar" ${sol.pulg && t ? "" : "disabled"}>Agregar soldaduras a la cotización</button></div></section>
      <div class="grid2">
      <section class="panel"><h3>2. Ensayos</h3><p class="small muted">Controles de calidad, antes de pintar.</p>
        <h3>Radiografía</h3><p class="small" id="rx-info">Usa las juntas a tope de Soldaduras: ${sol.placas_chicas} placas chicas y ${sol.placas_grandes} grandes al 100%.</p>
        <div class="fila"><label style="flex-direction:row;align-items:center;gap:6px"><span>Juntas a radiografiar (%)</span><input id="rx-pct" type="text" inputmode="decimal" class="num" value="${NI(S.rxPct ?? 0)}" style="width:70px"></label>
          <button data-a="rx-agregar" ${sol.placas_chicas + sol.placas_grandes ? "" : "disabled"}>Agregar radiografía</button></div>
        <h3>Prueba hidráulica</h3>
        <div class="campos"><label><span>Horas de prueba</span><input id="ph-h" type="text" inputmode="decimal" class="num" value="${NI(S.phH ?? 6)}"></label>
          <label><span>Tarifa</span><input id="ph-t" readonly value="${ph ? "USD " + num(ph.t) + "/h · " + E(F(ph.fe)) : "sin dato"}"></label></div>
        <div class="fila"><button data-a="ph-agregar" ${ph ? "" : "disabled"}>Agregar prueba hidráulica</button></div></section>
      <section class="panel"><h3>3. Pintura</h3><p class="small muted">Tratamiento de superficie de un tercero, al final.</p>
        <div class="campos"><label><span>Superficie a pintar (m²)</span><input id="pin-m2" type="text" inputmode="decimal" class="num" value="${NI(S.pinM2 ?? "")}"></label>
          <label class="ancho"><span>Tarifa de pintura (USD/m², sin IVA)</span><select id="pin-t">${pins.map(s => `<option value="${E(s.c)}">${num(s.t)} · ${E(s.s.slice(0, 60))} · ${E(s.pr.slice(0, 30))} · ${E(F(s.fe))}</option>`).join("")}</select></label></div>
        <div class="fila"><button data-a="pin-agregar">Agregar pintura</button><button class="chico" data-a="pin-calc">Calcular m² de los caños cargados</button></div></section></div>
      ${buscadorSrv()}`;
  }
  // Detallado o global por rubro (Rubros, rubros.js): la ficha junta los datos para pedir el global al tercero y controlarlo
  function panelRubros() {
    const cot = S.doc.cot, f = Rubros.ficha(cot, S.datos, S.sold, Motor), eq = E(cot.equipo?.singular || "equipo");
    const origen = f.aproximada ? "Ficha aproximada de la página (sin la tabla del plano: faltan juntas y placas; la completa la arma Claude Code con el plano)."
      : `Ficha calculada con la tabla del plano el ${E(F(f.generada))}. Si cambiaste materiales después, pedí que la rearmen.`;
    const tarjeta = r => {
      const [nombre] = Rubros.RUBROS[r], glob = Rubros.modo(cot, r) === "global", g = Rubros.globalDe(cot, r), s = g?.fuentes[0], tr = r === "transporte";
      return `<div class="panel rubro"><div class="sec-head"><h3>${E(nombre)}</h3><div class="estados" role="group" aria-label="Modo de ${E(nombre)}">
          <button class="chico" data-a="rubro-modo" data-r="${r}" data-v="detallado" aria-pressed="${!glob}">${tr ? "Sin precio (EXW)" : "Detallado"}</button>
          <button class="chico" data-a="rubro-modo" data-r="${r}" data-v="global" aria-pressed="${glob}">Global</button></div></div>
        ${tr ? `<div class="campos">${campo("Largo (m)", "cot.transporte.largo_m", "number")}${campo("Ancho (m)", "cot.transporte.ancho_m", "number")}${campo("Alto (m)", "cot.transporte.alto_m", "number")}${campo("Destino", "cot.transporte.destino")}</div>` : ""}
        <div id="rd-${r}">${fichaRubro(f, r)}</div>
        ${glob ? `<div class="campos">
          ${tr ? `<label><span>USD por viaje (sin IVA)</span><input id="gv-${r}" type="text" inputmode="decimal" class="num" data-glob="${r}" data-c="viaje" value="${NI(g.viaje_usd ?? "")}"></label>`
               : `<label><span>Precio global USD por ${eq} (sin IVA)</span><input id="gp-${r}" type="text" inputmode="decimal" class="num" data-glob="${r}" data-c="precio" value="${NI(s.precio)}"></label>`}
          <label><span>Proveedor</span><input id="gr-${r}" data-glob="${r}" data-c="proveedor" value="${E(s.proveedor)}"></label>
          <label><span>Fecha de la cotización</span><input id="gf-${r}" data-glob="${r}" data-c="fecha" type="text" inputmode="numeric" placeholder="DD-MM-AAAA" value="${E(F(s.fecha))}"></label>
          <label class="ancho"><span>Documento (cotización, mail, archivo)</span><input id="go-${r}" data-glob="${r}" data-c="origen" value="${E(s.origen)}"></label></div>
          <p class="small" id="rg-${r}">${globalRubro(f, r)}</p>` : ""}
        <div class="fila"><button class="chico" data-a="ficha-copiar" data-r="${r}">Copiar ficha</button><button class="chico" data-a="ficha-bajar" data-r="${r}" ${S.dl ? "" : "disabled"}>Descargar ficha (.txt)</button></div></div>`;
    };
    return `<section><div class="sec-head"><h2>Cotizar por rubro: detallado o global</h2><span class="eyebrow">todo por ${eq} · la cantidad multiplica al final</span></div>
      <p class="small muted">Detallado: como hasta ahora. Global: un solo precio del tercero por rubro; los renglones detallados quedan guardados y vuelven al pasar a detallado. ${origen}</p>
      <div class="grid-rubros">${Object.keys(Rubros.RUBROS).map(tarjeta).join("")}</div></section>`;
  }
  const uniRubro = (f, r, usd) => Rubros.unitarios(f, r, usd).map(([u, x]) => `USD ${num(x)}/${E(u)}`).join(" · ");
  function fichaRubro(f, r) {
    const ref = f.referencias[r], glob = ref.modo === "global", eq = E(S.doc.cot.equipo?.singular || "equipo");
    const v = x => x == null || x === "" ? '<span class="muted">—</span>' : typeof x === "number" ? num(x, Number.isInteger(x) ? 0 : 2) : E(x);
    return `<table class="ficha"><tbody>${Rubros.datosDe(f, r).map(([e, x, u]) => `<tr><td>${E(e)}</td><td${typeof x === "number" ? ' class="n"' : ""}>${v(x)}${u && x != null ? " " + E(u) : ""}</td></tr>`).join("")}</tbody></table>
      ${(f[r].avisos || []).map(a => `<div class="small warn">⚠ ${E(a)}</div>`).join("")}
      ${r === "transporte" ? "" : `<p class="small">Cálculo detallado: <b>USD ${num(ref.detallado_usd)}</b> por ${eq} (${ref.renglones_detalle} renglón/es${glob ? ", guardados" : ""})${ref.detallado_usd ? " · " + uniRubro(f, r, ref.detallado_usd) : ""}</p>`}`;
  }
  function globalRubro(f, r) {
    const ref = f.referencias[r], g = Rubros.globalDe(S.doc.cot, r); if (!g) return "";
    const p = g.fuentes[0].precio, dif = p && ref.detallado_usd ? p / ref.detallado_usd - 1 : 0, eq = E(S.doc.cot.equipo?.singular || "equipo");
    return (p ? `Global: <b>USD ${num(p)}</b> por ${eq} · ${uniRubro(f, r, p)}` : '<span class="err">SIN PRECIO: pedí la cotización con la ficha.</span>')
      + (p && (/^A cotizar/.test(g.fuentes[0].proveedor) || /^ficha_rubros/.test(g.fuentes[0].origen)) ? '<br><span class="warn">⚠ Cargá el proveedor y el documento de la cotización.</span>' : "")
      + (r !== "transporte" && Math.abs(dif) > 0.15 ? `<br><span class="warn">⚠ El global se aparta ${num(dif * 100, 0)}% del cálculo detallado: revisar alcance.</span>` : "");
  }
  // Transporte global: USD por viaje ÷ equipos por camión (se recalcula si cambian las medidas)
  function precioTransporte() {
    const g = Rubros.globalDe(S.doc.cot, "transporte"); if (!g || g.viaje_usd == null) return;
    const t = Rubros.ficha(S.doc.cot, S.datos, S.sold, Motor).transporte, n = t.por_camion || 1;
    g.fuentes[0].precio = Math.round(g.viaje_usd / n * 100) / 100;
    g.especificacion = `USD ${num(g.viaje_usd)} por viaje ÷ ${n} ${S.doc.cot.equipo?.plural || "equipos"} por camión${t.destino ? " · " + t.destino : ""}`;
  }
  // Actualiza fichas y resultados sin redibujar la pestaña (así no se pierde el clic en el botón siguiente)
  function pintarRubros() {
    const f = Rubros.ficha(S.doc.cot, S.datos, S.sold, Motor);
    for (const r of Object.keys(Rubros.RUBROS)) {
      const d = document.getElementById("rd-" + r), g = document.getElementById("rg-" + r);
      if (d) d.innerHTML = fichaRubro(f, r);
      if (g) g.innerHTML = globalRubro(f, r);
    }
  }
  function buscadorSrv() {
    const hojas = [...new Set(S.datos.servicios.map(s => s.h))];
    return `<section class="panel" id="bus-srv"><div class="sec-head"><h3>Buscar en el catálogo de mano de obra y servicios</h3><span class="eyebrow">un global solo sirve si el alcance es el mismo</span></div>
        <label class="bus-gral"><span>Buscar en todo el catálogo de MO y servicios</span><input id="fs-texto" data-fs="texto" type="search" value="${E(S.fs.texto || "")}" placeholder="ej. soldadura pulgada · granallado · ledesma · montaje"></label>
        <div class="buscador"><label><span>Rubro</span><select id="fs-hoja" data-fs="hoja"><option value="">Todos los rubros</option>${hojas.map(h => `<option ${S.fs.hoja === h ? "selected" : ""}>${E(h)}</option>`).join("")}</select></label></div>
        <span class="small muted" id="fs-info"></span>${S.doc ? barraSel("s") : ""}<div class="lista-res" id="res-srv"></div></section>`;
  }
  function pintarResultadosSrv() {
    const box = $("#res-srv"); if (!box) return;
    const r = Busqueda.servicios(S.datos, S.fs);
    $("#fs-info").textContent = `${r.total} resultado(s)`;
    box.innerHTML = r.res.length ? r.res.map((s, i) => `<div class="resultado ${S.selS.has(s.c) ? "sel" : ""}"><label class="tilde">${S.doc ? `<input type="checkbox" data-sels="${i}" ${S.selS.has(s.c) ? "checked" : ""} ${s.p ? "" : "disabled"} aria-label="Seleccionar">` : ""}<span class="pill ${s.t ? "ok" : "info"}">${s.t ? "tarifa" : "global"}</span></label>
      <div><div class="d">${E(s.s)}</div><div class="small muted">${E(s.h)} · ${E(s.c)}${s.eq ? " · " + E(s.eq) : ""}</div></div>
      <div class="precio">${s.p ? (s.t ? "USD " + num(s.t) + " " + E(s.ut.replace("USD", "")) : "USD " + num(s.p)) : '<span class="err">sin precio confiable</span>'}<div class="small muted">${E(F(s.fe))}</div></div>
      <div class="det">${s.inc ? "Incluye: " + E(s.inc) + " · " : ""}${s.ninc ? "No incluye: " + E(s.ninc) + " · " : ""}${s.al ? "<b>Alerta:</b> " + E(s.al) + " · " : ""}${E(s.pr)} · Origen: ${E(s.o)}</div>
      ${S.doc ? `<div class="acc"><input id="qs-${i}" type="text" inputmode="decimal" class="num" value="${NI(S.selS.has(s.c) ? S.selS.get(s.c).q : 1)}" aria-label="Cantidad"><button class="chico prim" data-a="agregar-srv" data-i="${i}" ${s.p ? "" : "disabled"}>Agregar</button></div>` : ""}</div>`).join("")
      : `<div class="vacio">No hay servicios con ese texto.</div>`;
    S.ultSrv = r.res;
  }

  // ------------------------------------------------------------------ pestaña Plazo
  function tabPlazo() {
    const pl = S.doc.cot.plazo ??= { dias: 60, texto: "desde OC", tareas: [], nota: "" };
    pl.tareas ??= [];
    const mat = pl.tareas.filter(t => t[3] !== "tal"), tal = pl.tareas.filter(t => t[3] === "tal");
    const acopio = Math.max(0, ...mat.map(t => +t[2] || 0)), taller = tal.reduce((a, t) => a + ((+t[2] || 0) - (+t[1] || 0)), 0);
    const calcD = acopio + taller, m1 = Math.round(calcD * 1.15), m2 = Math.round(calcD * 1.2);
    const solapa = tal.find(t => +t[1] < acopio);
    let aviso = "";
    if (pl.dias < calcD) aviso = `<div class="aviso bad">El plazo ofrecido (${pl.dias} d) es menor que el calculado (${calcD} d).</div>`;
    else if (pl.dias < m1) aviso = `<div class="aviso">El plazo ofrecido (${pl.dias} d) no tiene el margen de 15–20% (sugerido ${m1}–${m2} d).</div>`;
    if (solapa) aviso += `<div class="aviso bad">Superposición: "${E(solapa[0])}" empieza el día ${solapa[1]}, antes de que llegue el material más largo (día ${acopio}).</div>`;
    return `<div class="grid2"><section class="panel"><h3>Plazo ofrecido</h3><div class="campos">${campo("Días", "cot.plazo.dias", "number")}${campo("Desde", "cot.plazo.texto")}
        <label class="ancho"><span>Nota (aparece en el informe)</span><textarea id="f-plazo-nota" data-b="cot.plazo.nota">${E(pl.nota || "")}</textarea></label></div></section>
      <section class="panel"><h3>Plazo calculado</h3><p>Material más largo: <b>${acopio} días</b> · taller, ensayos y despacho: <b>${taller} días</b>.</p>
        <p>Sin superponer: <b>${calcD} días</b> · con el margen de 15–20%: <b>${m1}–${m2} días</b>.</p>${aviso}
        <p class="small muted">Los plazos típicos de cada rubro están en el catálogo de plazos de proveedores (válvulas esféricas ~90 d, control ~94, PSV ~100, instrumentos ~85–90). Cargá el plazo que cotizó cada proveedor.</p></section></div>
      <section><div class="sec-head"><h3>Tareas</h3><button class="chico" data-a="tarea-nueva">Agregar tarea</button></div>
        ${pl.tareas.length ? `<div class="tbl"><table><thead><tr><th>Tarea</th><th class="n">Día inicio</th><th class="n">Día fin</th><th>Tipo</th><th></th></tr></thead><tbody>
        ${pl.tareas.map((t, i) => `<tr><td><input id="tn-${i}" data-ta="${i}" data-c="0" value="${E(t[0])}"></td><td class="ed"><input id="ti-${i}" type="text" inputmode="decimal" class="num" data-ta="${i}" data-c="1" value="${NI(t[1])}"></td>
          <td class="ed"><input id="tf-${i}" type="text" inputmode="decimal" class="num" data-ta="${i}" data-c="2" value="${NI(t[2])}"></td>
          <td><select id="tt-${i}" data-ta="${i}" data-c="3"><option value="" ${t[3] === "" ? "selected" : ""}>material</option><option value="crit" ${t[3] === "crit" ? "selected" : ""}>material crítico</option><option value="tal" ${t[3] === "tal" ? "selected" : ""}>taller / despacho</option></select></td>
          <td><button class="chico peligro" data-a="tarea-quitar" data-i="${i}">Quitar</button></td></tr>`).join("")}</tbody></table></div>` : `<div class="vacio">Sin tareas. Agregá una por cada material de plazo largo y las etapas de taller.</div>`}</section>`;
  }

  // ------------------------------------------------------------------ pestaña Oferta
  function tabOferta() {
    const of = S.doc.oferta;
    const lineas = (etq, ruta) => `<label class="ancho"><span>${etq} (una por renglón)</span><textarea id="o-${ruta.replace(/\./g, "-")}" data-bl="${ruta}">${E((leerRuta(S.doc, ruta) || []).join("\n"))}</textarea></label>`;
    const area = (etq, ruta) => `<label class="ancho"><span>${etq}</span><textarea id="o-${ruta.replace(/\./g, "-")}" data-b="${ruta}">${E(leerRuta(S.doc, ruta) || "")}</textarea></label>`;
    of.condiciones ??= {};
    return `<p class="small muted">Lo que está entre [corchetes] sale resaltado en amarillo en el Word, para completar antes de enviar. Los precios no se escriben acá: salen del cálculo.</p>
      <div class="grid2"><section class="panel"><h3>Encabezado</h3><div class="campos">${campo("Número de oferta", "oferta.oferta.numero")}${campo("Revisión", "oferta.oferta.revision")}
        ${campo("Fecha", "oferta.oferta.fecha")}${campo("Descripción de la revisión", "oferta.oferta.descripcion_revision")}
        ${campo("Cliente", "oferta.cliente.nombre")}${campo("Contacto", "oferta.cliente.contacto")}${campo("Referencia", "oferta.cliente.referencia")}${campo("Proyecto", "oferta.cliente.proyecto")}
        ${campo("Nombre base de los archivos", "oferta.archivo_base")}</div></section>
      <section class="panel"><h3>Ítem</h3><div class="campos">${campo("Ítem", "oferta.item.item")}${campo("Código", "oferta.item.codigo")}${campo("Plazo de entrega (días)", "oferta.item.plazo_dias")}
        ${area("Descripción", "oferta.item.descripcion")}${area("Observación / desvío", "oferta.item.observacion")}</div>
        <label><span>Imagen del plano (opcional, va en la oferta técnica)</span><input id="o-plano" type="file" accept="image/png,image/jpeg" ${S.assets ? "" : "disabled"}></label>
        ${of.imagen_plano_url ? `<img src="${E(of.imagen_plano_url)}" alt="Plano cargado" style="max-height:120px;align-self:flex-start;border:1px solid var(--line)">` : ""}</section></div>
      <section class="panel"><h3>Textos</h3><div class="campos">${area("Objeto ({tipo} se reemplaza por Técnica o Comercial)", "oferta.objeto")}${area("Nota de flete", "oferta.nota_flete")}
        ${Object.keys(of.condiciones).map(k => area(k, "oferta.condiciones." + k)).join("")}
        ${area("Embalaje", "oferta.embalaje")}${lineas("Documentos del cliente", "oferta.documentos_cliente")}${area("Características generales según plano", "oferta.caracteristicas")}
        ${lineas("Aclaraciones y desvíos", "oferta.aclaraciones_y_desvios.items")}${lineas("Exclusiones", "oferta.exclusiones.items")}${lineas("Alcance general", "oferta.alcance_general.items")}
        ${area("Garantía", "oferta.garantia")}</div></section>`;
  }

  // ------------------------------------------------------------------ pestaña Resumen y descargas
  const ARCHIVOS = [["presupuesto", "1_Presupuesto.xlsx"], ["compras", "2_Lista_para_Compras.xlsx"], ["informe", "3_Informe_del_presupuesto.pdf"],
    ["tec_docx", "4_Oferta_tecnica.docx"], ["tec_pdf", "4_Oferta_tecnica.pdf"], ["eco_docx", "5_Oferta_economica.docx"], ["eco_pdf", "5_Oferta_economica.pdf"], ["json", "6_Respaldo_cotizacion.json"]];
  // Incorporar a la base: Claude Code copia la cotización al repositorio y rearma catálogos, antecedentes y la página.
  // Las aprobadas o enviadas entran solas con la tarea semanal (web/LEEME.md).
  function panelBase() {
    const cot = S.doc.cot, b = cot.base || {};
    const estado = b.incorporada ? `Incorporada a la base el ${F(b.incorporada)}.` : b.pedida ? `Pedida el ${F(b.pedida)}: la procesa Claude Code (ver Pedidos).` : "";
    return `<h3>Base de datos</h3>
      <p class="small muted">Suma esta cotización a los antecedentes y sus precios con documento (cotizaciones, listas y planillas, iguales a lo pedido) al catálogo, para usarlos en las próximas búsquedas. Los estimados no entran. Las aprobadas o enviadas entran solas el lunes.</p>
      ${estado ? `<p class="small"><b>${E(estado)}</b></p>` : ""}
      <div class="fila"><button data-a="incorporar" ${cot.estado === "borrador" ? "disabled" : ""}>${b.incorporada || b.pedida ? "Volver a incorporar" : "Incorporar a la base de datos"}</button>
      ${cot.estado === "borrador" ? `<span class="small muted">Primero pasala a revisado.</span>` : ""}</div>`;
  }
  function tabResumen() {
    const c = calc(), p = S.doc.cot.parametros, avs = Busqueda.avisos(S.doc.cot), esc_ = Motor.escenarios(S.doc.cot, S.datos.indices);
    const bad = avs.filter(a => a.nivel === "bad"), warn = avs.filter(a => a.nivel !== "bad");
    return `<div class="grid2"><section class="panel"><h3>Costo y precio por ${E(S.doc.cot.equipo?.singular || "equipo")} (USD sin IVA)</h3>
        <div class="tbl"><table><tbody>
        <tr><td>Materiales (con ajuste por inflación)</td><td class="n">${num(c.sub.material)}</td><td class="n">× ${p.FM}</td></tr>
        <tr><td>Contingencia ${p.CONT}%</td><td class="n">${num(c.cont)}</td><td class="n">× ${p.FM}</td></tr>
        ${c.tav ? `<tr><td>Válvulas Taval (con contingencia)</td><td class="n">${num(c.tav)}</td><td class="n">× ${c.ftv}</td></tr>` : ""}
        <tr><td>Mano de obra</td><td class="n">${num(c.sub.mo)}</td><td class="n">× ${p.FMO}</td></tr>
        <tr><td>Servicios e insumos</td><td class="n">${num(c.sub.servicio)}</td><td class="n">× ${p.FMO}</td></tr>
        <tr class="total"><td>Costo</td><td class="n">${num(c.costo)}</td><td class="n">${num(c.precio_unitario)}</td></tr>
        <tr><td>Ajuste por inflación incluido</td><td class="n">${num(c.costo - c.costo0)}</td><td class="n">${c.costo0 ? "+" + num((c.costo / c.costo0 - 1) * 100, 1) + "%" : ""}</td></tr>
        <tr><td>Flete + embalaje</td><td class="n">${num(c.flete)}</td><td class="n">${p.TRANS ? "incluido" : "no incluido"}</td></tr></tbody></table></div>
        <h3>Escenarios de factor</h3><div class="tbl"><table><thead><tr><th>Factor</th><th class="n">Unitario</th><th class="n">Total</th><th class="n">Margen</th></tr></thead><tbody>
        ${esc_.map(e => `<tr ${Math.abs(e.F - p.FM) < 1e-9 && Math.abs(e.F - p.FMO) < 1e-9 ? 'class="total"' : ""}><td>${e.F.toFixed(2)}</td><td class="n">${num(e.unitario)}</td><td class="n">${num(e.total)}</td><td class="n">${num(e.margen * 100, 1)}%</td></tr>`).join("")}</tbody></table></div>
        ${panelBase()}</section>
      <section class="panel"><h3>Descargas</h3>
        <p class="small muted">"Descargar todo" arma un .zip con la planilla, la lista para Compras, el informe, las ofertas (Word y PDF) y el respaldo. ${S.doc.cot.estado === "aprobado" ? "Estado aprobado: las ofertas salen sin la leyenda de borrador y con la firma." : "Mientras no esté aprobada, las ofertas llevan la leyenda BORRADOR – SIN REVISAR – NO ENVIAR."}</p>
        <div class="fila"><button class="prim" data-a="zip" ${S.dl ? "" : "disabled"}>Descargar todo (.zip)</button></div>
        <div class="fila"><span class="small">Ver en pantalla:</span><button class="chico" data-a="vista" data-v="informe">Informe</button><button class="chico" data-a="vista" data-v="tecnica">Oferta técnica</button><button class="chico" data-a="vista" data-v="economica">Oferta económica</button></div>
        <div class="fila"><select id="un-archivo" style="max-width:300px">${ARCHIVOS.map(([k, n]) => `<option value="${k}">${n}</option>`).join("")}</select><button data-a="uno" ${S.dl ? "" : "disabled"}>Descargar este archivo</button></div>
        ${S.dl ? "" : '<p class="err">Las descargas no están disponibles en esta vista.</p>'}<p class="small" id="desc-estado"></p>
        <h3>Versiones guardadas</h3><div id="versiones" class="small muted"><button class="chico" data-a="ver-versiones">Ver versiones</button></div></section></div>
      ${panelAntecedentes(c)}
      <section><div class="sec-head"><h3>Avisos de control</h3><span class="eyebrow">${bad.length} para corregir · ${warn.length} para revisar</span></div>
        ${bad.length ? `<div class="aviso bad"><b>Para corregir antes de presentar</b><ul>${bad.map(a => `<li>${E(a.txt)}</li>`).join("")}</ul></div>` : ""}
        ${warn.length ? `<div class="aviso"><b>Para revisar</b><ul>${warn.map(a => `<li>${E(a.txt)}</li>`).join("")}</ul></div>` : ""}
        ${!avs.length ? `<div class="aviso ok">Sin avisos.</div>` : ""}</section>`;
  }

  function panelAntecedentes(c) {
    const r = Antecedentes.comparar(S.doc.cot, S.datos, c.precio_unitario);
    return `<section><div class="sec-head"><h3>Antecedentes parecidos (P8)</h3><span class="eyebrow">familia ${E(r.nombreFamilia || r.familia)} · los 5 más parecidos con precio</span></div>
      <p class="small muted">Una diferencia de más del 15% no es un error: hay que explicarla rubro por rubro (alcance, cantidad, diámetro, serie, fecha) antes de presentar el número. Más de 4 veces es otra escala (el precio del índice es de otra cosa).</p>
      ${r.filas.length ? `<div class="tbl"><table><thead><tr><th>#</th><th>Antecedente</th><th>Fecha</th><th class="n">Precio unitario</th><th class="n">Esta vs. antecedente</th><th>Factor</th><th>Materiales</th><th>Por qué se parece</th></tr></thead><tbody>
        ${r.filas.map((f, i) => `<tr><td>${i + 1}</td><td><div class="d">${E(f.id)}</div><div class="sp">${E(f.cliente)}${f.oferta ? " · " + E(f.oferta) : ""} · ${E(f.descripcion.slice(0, 120))}</div></td><td class="small">${E(F(f.fecha))}</td>
          <td class="n">${num(f.pu, 0)} ${E(f.moneda)}</td><td class="n">${f.otra ? '<span class="muted">otra escala</span>' : `<span class="pill ${f.ojo ? "warn" : "ok"}">${f.dif > 0 ? "+" : ""}${num(f.dif * 100, 0)}%</span>`}</td>
          <td>${E(f.factor || "—")}</td><td class="small">${f.reparto != null ? num(f.reparto * 100, 0) + "%" : "—"}</td><td class="small muted">${E(f.razones.join(" · "))}</td></tr>`).join("")}</tbody></table></div>` : ""}
      ${r.avisos.length ? `<div class="aviso"><ul>${r.avisos.map(a => `<li>${E(a)}</li>`).join("")}</ul></div>` : ""}</section>`;
  }

  // ------------------------------------------------------------------ firmantes
  function renderFirmantes() {
    app.innerHTML = `<section><div class="sec-head"><h1>Firmantes</h1><span class="eyebrow">quien prepara la cotización</span></div>
      <p class="small muted">Los datos aparecen en el informe, la planilla y las ofertas. La imagen de la firma solo se agrega cuando la cotización está aprobada.</p>
      <div class="fila"><button class="prim" data-a="firmante-nuevo" ${S.db ? "" : "disabled"}>Agregar firmante</button></div>
      ${S.firmantes.length ? `<div class="tbl"><table><thead><tr><th>Nombre</th><th>Cargo</th><th>Teléfono</th><th>Celular</th><th>Email</th><th>Firma</th><th></th></tr></thead><tbody>
      ${S.firmantes.map(f => `<tr><td><b>${E(f.nombre)}</b></td><td>${E(f.cargo)}</td><td>${E(f.telefono)}</td><td>${E(f.celular)}</td><td>${E(f.email)}</td>
        <td>${f.firma_url ? `<img class="firma-img" src="${E(f.firma_url)}" alt="Firma de ${E(f.nombre)}">` : '<span class="muted small">sin imagen</span>'}</td>
        <td><button class="chico" data-a="firmante-editar" data-id="${E(f.id)}">Editar</button></td></tr>`).join("")}</tbody></table></div>`
        : `<div class="vacio"><b>No hay firmantes.</b><span>Agregá a quien prepara las cotizaciones: nombre, cargo, teléfono, celular, email y, si querés, la imagen de su firma.</span></div>`}</section>`;
  }
  function editorFirmante(f) {
    f = f || { id: "f" + Date.now().toString(36), nombre: "", cargo: "", telefono: "", celular: "", email: "" };
    S.editF = clon(f);
    capa.hidden = false;
    capa.innerHTML = `<div class="capa"><section class="panel" role="dialog" aria-label="Firmante"><h2>Firmante</h2><div class="campos">
      ${["nombre", "cargo", "telefono", "celular", "email"].map(k => `<label><span>${{ nombre: "Nombre", cargo: "Cargo", telefono: "Teléfono", celular: "Celular", email: "Email" }[k]}</span><input id="ff-${k}" data-ff="${k}" value="${E(f[k] || "")}"></label>`).join("")}
      <label class="ancho"><span>Imagen de la firma (PNG o JPG, fondo blanco)</span><input id="ff-img" type="file" accept="image/png,image/jpeg" ${S.assets ? "" : "disabled"}></label>
      ${f.firma_url ? `<img class="firma-img" src="${E(f.firma_url)}" alt="Firma actual">` : ""}</div>
      <p class="err" id="ff-err"></p><div class="fila fin"><button data-a="cerrar">Cancelar</button><button class="prim" data-a="firmante-guardar">Guardar</button></div></section></div>`;
  }

  // ------------------------------------------------------------------ editor de ítem
  function editorItem(it, grupo) {
    const nuevo = !it;
    it = it ? clon(it) : { id: siguienteId(grupo === "material" ? "M" : "S"), pos: "", grupo, descripcion: "", especificacion: "", cantidad: 1, unidad: grupo === "material" ? "un" : "gl",
      fuentes: [{ tipo: "cot", precio: 0, proveedor: "", origen: "", fecha: hoy(), coincide: "igual" }], plano: {} };
    it.plano ??= {};
    S.editI = { it, nuevo };
    const s = it.fuentes[0];
    const inp = (k, etq, v, tipo = "text") => tipo === "date"
      ? `<label><span>${etq}</span><input id="ei-${k}" data-ei="${k}" data-fecha type="text" inputmode="numeric" placeholder="DD-MM-AAAA" value="${E(F(v))}"></label>`
      : `<label><span>${etq}</span><input id="ei-${k}" data-ei="${k}" type="text" ${tipo === "number" ? 'inputmode="decimal" class="num" data-num' : ""} value="${E(tipo === "number" ? NI(v) : (v ?? ""))}"></label>`;
    capa.hidden = false;
    capa.innerHTML = `<div class="capa"><section class="panel" role="dialog" aria-label="Ítem"><h2>${nuevo ? "Cargar ítem a mano" : "Editar ítem"}</h2>
      <div class="campos">${inp("pos", "Posición del plano", it.pos)}<label><span>Grupo</span><select id="ei-grupo" data-ei="grupo">${[["material", "Material"], ["mo", "Mano de obra"], ["servicio", "Servicio"]].map(([v, n]) => `<option value="${v}" ${it.grupo === v ? "selected" : ""}>${n}</option>`).join("")}</select></label>
        <label class="ancho"><span>Descripción</span><input id="ei-descripcion" data-ei="descripcion" value="${E(it.descripcion)}"></label>
        <label class="ancho"><span>Especificación</span><input id="ei-especificacion" data-ei="especificacion" value="${E(it.especificacion || "")}"></label>
        ${inp("cantidad", "Cantidad por equipo", it.cantidad, "number")}${inp("unidad", "Unidad", it.unidad)}
        ${it.grupo === "material" ? `<label><span>Válvula Taval</span><select id="ei-taval" data-ei="taval"><option value="" ${it.taval ? "" : "selected"}>No</option><option value="1" ${it.taval ? "selected" : ""}>Sí (usa el factor de válvulas Taval)</option></select></label>` : ""}
        ${it.grupo === "material" ? ["diametro", "serie_sch", "material", "extremos", "modelo"].map(k => inp("plano." + k, { diametro: "Ø (plano)", serie_sch: "Serie / sch (plano)", material: "Material (plano)", extremos: "Extremos (plano)", modelo: "Modelo / fabricante (plano)" }[k], it.plano[k])).join("") : ""}
      </div><h3>Precio y fuente (sin IVA)</h3><div class="campos">
        ${inp("f.precio", "Precio unitario USD sin IVA", s.precio, "number")}
        <label><span>Tipo de origen</span><select id="ei-ftipo" data-ei="f.tipo">${Object.entries(Documentos.TIPOS).map(([k, n]) => `<option value="${k}" ${s.tipo === k ? "selected" : ""}>${n}</option>`).join("")}</select></label>
        ${inp("f.proveedor", "Proveedor o criterio", s.proveedor)}${inp("f.fecha", "Fecha del precio", s.fecha, "date")}
        <label class="ancho"><span>Origen (carpeta, archivo o cotización)</span><input id="ei-forigen" data-ei="f.origen" value="${E(s.origen || "")}"></label>
        <label><span>¿Coincide con el plano?</span><select id="ei-fcoincide" data-ei="f.coincide">${Object.entries(Documentos.COINC).map(([k, n]) => `<option value="${k}" ${s.coincide === k ? "selected" : ""}>${n}</option>`).join("")}</select></label>
        <label class="ancho"><span>En qué difiere (obligatorio si es similar)</span><input id="ei-fdiferencia" data-ei="f.diferencia" value="${E(s.diferencia || "")}"></label></div>
      <p class="small muted">Si la cotización del proveedor dice "con IVA", dividí por 1,21 (o 1,105) antes de cargarla. Un valor verbal o "aprox" va como Estimado.</p>
      <p class="err" id="ei-err"></p><div class="fila fin"><button data-a="cerrar">Cancelar</button><button class="prim" data-a="item-guardar">Guardar</button></div></section></div>`;
  }

  // ------------------------------------------------------------------ cambio de estado (con controles; la herramienta nunca envía nada)
  function dialogoEstado(d) {
    const cot = S.doc.cot, malos = Busqueda.avisos(cot).filter(a => a.nivel === "bad"), act = cot.estado;
    let error = "", texto = "", extra = "";
    if (d === act) return;
    if (d === "revisado") {
      if (malos.length) error = `Hay ${malos.length} aviso(s) para corregir. Corregilos antes de pasar a revisado (ver Resumen y descargas).`;
      texto = "Confirmá que una persona revisó el cómputo contra el plano (procedimiento P10) y que los avisos para revisar están explicados.";
    } else if (d === "aprobado") {
      if (act !== "revisado") error = "Primero tiene que estar revisada.";
      else if (malos.length) error = `Hay ${malos.length} aviso(s) para corregir.`;
      texto = "Al aprobar, la oferta sale sin la leyenda de borrador y con la firma, y la cotización queda bloqueada para cambios.";
      extra = `<label><span>¿Quién aprueba? (Matías o la dirección)</span><input id="ap-por" autocomplete="off"></label>`;
    } else if (d === "enviado") {
      if (act !== "aprobado") error = "Solo se marca enviada una cotización aprobada.";
      texto = "La herramienta no envía nada. Marcala como enviada solo si ya la mandaste vos al cliente.";
    } else if (d === "borrador") {
      texto = act === "revisado" ? "Vuelve a borrador para seguir cambiándola." : "Vuelve a borrador: se desbloquea, se borra la aprobación y la oferta vuelve a salir con la leyenda de borrador.";
    }
    capa.hidden = false;
    capa.innerHTML = `<div class="capa"><section class="panel" role="dialog" aria-label="Cambiar estado"><h2>Pasar a "${E(d)}"</h2>
      ${error ? `<div class="aviso bad">${E(error)}</div>` : `<p>${E(texto)}</p>${extra}`}
      <p class="err" id="est-err"></p><div class="fila fin"><button data-a="cerrar">${error ? "Volver" : "Cancelar"}</button>
      ${error ? "" : `<button class="prim" data-a="estado-ok" data-v="${E(d)}">Pasar a ${E(d)}</button>`}</div></section></div>`;
    $("#ap-por")?.focus();
  }

  // ------------------------------------------------------------------ eventos
  app.addEventListener("input", ev => {
    const el = ev.target;
    if (bloqueada() && (el.dataset.b || el.dataset.bl || el.dataset.it || el.dataset.glob || el.dataset.ta !== undefined)) {
      toast(`La cotización está ${S.doc.cot.estado}: para cambiarla, volvé a borrador.`); render(); return;
    }
    if (el.dataset.b && S.doc) {
      let v = el.value;
      if (el.dataset.t === "fecha") { v = Documentos.isoDe(v); el.classList.toggle("mal", !v); if (!v) return; }
      if (el.dataset.t === "number") { v = v.trim() === "" ? (el.dataset.b === "cot.parametros.FTV" ? 1 : 0) : NUM(v); el.classList.toggle("mal", v == null); if (v == null) return; }
      ponerRuta(S.doc, el.dataset.b, v);
      if (el.dataset.b === "cot.estado") S.doc.oferta.estado = v;
      if (el.dataset.b.startsWith("cot.transporte")) { precioTransporte(); pintarRubros(); }
      refrescar(); guardarPronto();
      if (el.tagName === "SELECT" || el.dataset.b.startsWith("cot.plazo")) { if (el.tagName === "SELECT" || ev.type === "change") render(); }
    } else if (el.dataset.bl && S.doc) {
      ponerRuta(S.doc, el.dataset.bl, el.value.split("\n").map(x => x.trim()).filter(Boolean)); guardarPronto();
    } else if (el.dataset.it && S.doc) {
      const it = S.doc.cot.items.find(i => i.id === el.dataset.it);
      if (el.dataset.c === "precio" || el.dataset.c === "cantidad") {
        const v = el.value.trim() === "" ? 0 : NUM(el.value); el.classList.toggle("mal", v == null || v < 0); if (v == null || v < 0) return;
        if (el.dataset.c === "precio") it.fuentes[0].precio = v; else it.cantidad = v;
      }
      else it[el.dataset.c] = el.value;
      refrescar(); guardarPronto();
    } else if (el.dataset.fm !== undefined) {
      const k = el.dataset.fm; S.fm[k] = el.value;
      if (k === "fam") S.fm = { fam: el.value, texto: S.fm.texto };
      if (k === "texto") { clearTimeout(S.tBus); S.tBus = setTimeout(pintarResultadosMat, 200); }
      else { $("#bus-mat").outerHTML = buscadorMat(); pintarResultadosMat(); }
    } else if (el.dataset.vi) {
      S.vistaItems[el.dataset.vi][el.dataset.c] = el.value; render();
    } else if (el.dataset.selm !== undefined || el.dataset.sels !== undefined) {
      const m = el.dataset.selm !== undefined, i = +(m ? el.dataset.selm : el.dataset.sels), x = m ? S.ultMat[i] : S.ultSrv[i], cod = m ? x.r.c : x.c, sel = m ? S.selM : S.selS;
      if (el.checked) sel.set(cod, { x, q: NUM($((m ? "#qm-" : "#qs-") + i).value) || 1 }); else sel.delete(cod);
      el.closest(".resultado").classList.toggle("sel", el.checked); pintarBarraSel(m ? "m" : "s");
    } else if (/^q[ms]-\d+$/.test(el.id)) {
      const m = el.id[1] === "m", i = +el.id.slice(3), x = m ? S.ultMat[i] : S.ultSrv[i], sel = m ? S.selM : S.selS, cod = m ? x?.r.c : x?.c;
      if (sel.has(cod)) sel.get(cod).q = NUM(el.value) || 1;
    } else if (el.dataset.fs !== undefined) {
      S.fs[el.dataset.fs] = el.value; clearTimeout(S.tBus); S.tBus = setTimeout(pintarResultadosSrv, 200);
    } else if (el.dataset.sold !== undefined) {
      S.sold[+el.dataset.sold][el.dataset.c] = ["bw", "sw", "olet"].includes(el.dataset.c) ? String(NUM(el.value) ?? "") : el.value;
      const sol = Busqueda.soldadura(S.datos, S.sold), t = Busqueda.tarifa(S.datos, "soldadura", "soldadura piping");
      $("#sold-res").innerHTML = `<b>${num(sol.pulg, 2)} pulgadas equivalentes</b> × USD ${t ? num(t.valor) : "—"} = <b>USD ${num(sol.pulg * (t ? +t.valor : 0))}</b>`;
      $("#rx-info").textContent = `Usa las juntas a tope de Soldaduras: ${sol.placas_chicas} placas chicas y ${sol.placas_grandes} grandes al 100%.`;
      document.querySelector('[data-a="sold-agregar"]').disabled = !(sol.pulg && t);
      document.querySelector('[data-a="rx-agregar"]').disabled = !(sol.placas_chicas + sol.placas_grandes);
    } else if (el.dataset.glob && S.doc) {
      const r = el.dataset.glob, g = Rubros.globalDe(S.doc.cot, r); if (!g) return;
      const src = g.fuentes[0], c = el.dataset.c;
      if (c === "precio" || c === "viaje") {
        const v = el.value.trim() === "" ? 0 : NUM(el.value); el.classList.toggle("mal", v == null || v < 0); if (v == null || v < 0) return;
        if (c === "viaje") { g.viaje_usd = v; precioTransporte(); } else src.precio = v;
      } else if (c === "fecha") { const v = Documentos.isoDe(el.value); el.classList.toggle("mal", !v); if (!v) return; src.fecha = v; }
      else src[c] = el.value;
      if ((c === "precio" || c === "viaje") && src.precio && src.tipo === "est" && /^SIN PRECIO/.test(src.diferencia || "")) { src.tipo = "cot"; src.diferencia = ""; }
      refrescar(); pintarRubros(); guardarPronto();
    } else if (el.dataset.ta !== undefined) {
      const t = S.doc.cot.plazo.tareas[+el.dataset.ta], c = +el.dataset.c;
      t[c] = c === 1 || c === 2 ? NUM(el.value) || 0 : el.value; guardarPronto();
    } else if (el.id === "rx-pct") S.rxPct = NUM(el.value) || 0;
    else if (el.id === "pin-m2") S.pinM2 = el.value;
    else if (el.id === "ph-h") S.phH = el.value;
  });
  app.addEventListener("change", async ev => {
    const el = ev.target;
    if (el.dataset.ta !== undefined || (el.dataset.b || "").startsWith("cot.plazo") || el.dataset.b === "cot.firmante_id") { guardarPronto(); render(); }
    if (el.id === "o-plano" && el.files[0]) {
      try {
        const r = await S.assets.upload(el.files[0]);
        S.doc.oferta.imagen_plano_asset = r.id; S.doc.oferta.imagen_plano_url = r.url; guardarPronto(); render(); toast("Imagen del plano cargada");
      } catch (e) { toast("No se pudo subir la imagen: " + (e.message || e.code)); }
    }
  });
  capa.addEventListener("input", ev => {
    const el = ev.target;
    if (el.dataset.ff) S.editF[el.dataset.ff] = el.value;
    if (el.dataset.ei) {
      const k = el.dataset.ei, it = S.editI.it, s = it.fuentes[0];
      let v = el.value;
      if (el.dataset.num !== undefined) { v = NUM(el.value); el.classList.toggle("mal", v == null && el.value.trim() !== ""); v = v ?? 0; }
      if (el.dataset.fecha !== undefined) { v = Documentos.isoDe(el.value); el.classList.toggle("mal", !v); }
      if (k === "taval") { if (v) it.taval = true; else delete it.taval; }
      else if (k.startsWith("f.")) s[k.slice(2)] = v; else if (k.startsWith("plano.")) it.plano[k.slice(6)] = v; else it[k] = v;
      if (k === "grupo") editorItem(it, it.grupo);
    }
  });
  capa.addEventListener("change", async ev => {
    if (ev.target.id === "ff-img" && ev.target.files[0]) {
      try { const r = await S.assets.upload(ev.target.files[0]); S.editF.firma_asset = r.id; S.editF.firma_url = r.url; toast("Imagen de la firma cargada"); editorFirmante(S.editF); }
      catch (e) { $("#ff-err").textContent = "No se pudo subir la imagen: " + (e.message || e.code); }
    }
  });
  document.addEventListener("click", async ev => {
    const b = ev.target.closest("[data-a]"); if (!b) return;
    const a = b.dataset.a;
    try { await accion(a, b); } catch (e) { toast("Error: " + (e.message || e.code || e)); console.error(e); }
  });

  // Acciones que cambian la cotización: no se permiten si está aprobada o enviada (hay que volver a borrador)
  const CAMBIAN = new Set(["quitar", "editar", "manual", "item-guardar", "agregar-mat", "agregar-srv", "agregar-sel", "sold-agregar", "rx-agregar", "pin-agregar",
    "ph-agregar", "rubro-modo", "tarea-nueva", "tarea-quitar", "restaurar", "deshacer", "rehacer"]);
  const bloqueada = () => S.doc && ["aprobado", "enviado"].includes(S.doc.cot.estado);
  async function accion(a, b) {
    const cot = S.doc?.cot;
    if (CAMBIAN.has(a) && bloqueada()) { toast(`La cotización está ${cot.estado}: para cambiarla, volvé a borrador.`); return; }
    switch (a) {
      case "tab": S.tab = b.dataset.v; render(); break;
      case "deshacer": deshacer(); break;
      case "cat-tab": S.catTab = b.dataset.v; render(); break;
      case "vista": await vistaPrevia(b.dataset.v); break;
      case "uno-k": await descargarUno(b, b.dataset.k); break;
      case "rehacer": rehacer(); break;
      case "estado": dialogoEstado(b.dataset.v); break;
      case "incorporar": {
        if (b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro? Incorporar"; setTimeout(() => { b.dataset.ok = ""; render(); }, 4000); return; }
        cot.base = { ...(cot.base || {}), pedida: hoy() }; guardarPronto(); render();
        try {
          await Asistente.crearPedido({ tipo: "incorporar_base", texto: `Incorporar ${cot.codigo} (${cot.titulo || ""}) a la base: catálogos, antecedentes y página.`, cot: S.id, files: [], mandar: true });
          toast("Pedido mandado a Claude Code: va a actualizar catálogos y antecedentes");
        } catch (e) { toast(e.message); }
        break;
      }
      case "estado-ok": {
        const d = b.dataset.v;
        if (d === "aprobado") {
          const por = ($("#ap-por")?.value || "").trim();
          if (!por) { $("#est-err").textContent = "Escribí quién aprueba."; return; }
          cot.aprobacion = { por, fecha: hoy() };
        }
        cambiarEstado(d); capa.hidden = true; capa.innerHTML = ""; guardarPronto(); render();
        toast(`Estado: ${d}`); break;
      }
      case "nueva": { const id = await crearCotizacion(); S.tab = "datos"; location.hash = "c-" + id; break; }
      case "duplicar": { const id = await duplicarCotizacion(b.dataset.id); if (!id) return; toast("Cotización duplicada"); location.hash = "c-" + id; break; }
      case "borrar":
        if (b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro? Borrar"; setTimeout(() => { b.dataset.ok = ""; b.textContent = "Borrar"; }, 4000); return; }
        await borrarCotizacion(b.dataset.id); toast("Cotización borrada"); break;
      case "quitar": cot.items = cot.items.filter(i => i.id !== b.dataset.id); guardarPronto(); render(); break;
      case "editar": editorItem(cot.items.find(i => i.id === b.dataset.id)); break;
      case "manual": editorItem(null, b.dataset.g); break;
      case "cerrar": capa.hidden = true; capa.innerHTML = ""; break;
      case "item-guardar": {
        const { it, nuevo } = S.editI, s = it.fuentes[0];
        const err = !it.descripcion ? "Falta la descripción." : !s.proveedor ? "Falta el proveedor o criterio del precio." : !/^\d{4}-\d{2}-\d{2}$/.test(s.fecha) || s.fecha > hoy() ? "La fecha del precio no es válida." :
          s.coincide === "similar" && !s.diferencia ? "Si es similar, escribí en qué difiere." : "";
        if (err) { $("#ei-err").textContent = err; return; }
        if (nuevo) cot.items.push(it); else cot.items[cot.items.findIndex(i => i.id === it.id)] = it;
        capa.hidden = true; capa.innerHTML = ""; guardarPronto(); render(); break;
      }
      case "agregar-mat": {
        const x = S.ultMat[+b.dataset.i], it = agregarMaterialDe(x, NUM($("#qm-" + b.dataset.i).value) || 1);
        S.selM.delete(x.r.c); guardarPronto(); render(); toast(`Agregado: ${it.descripcion.slice(0, 50)}`); break;
      }
      case "agregar-sel": {
        const sel = b.dataset.k === "m" ? S.selM : S.selS, n = sel.size;
        for (const { x, q } of sel.values()) {
          if (b.dataset.k === "m") agregarMaterialDe(x, q); else cot.items.push(Busqueda.itemDeServicio(x, q, siguienteId("S")));
        }
        sel.clear(); guardarPronto(); render(); toast(`Agregados ${n} ítem(s) a la cotización`); break;
      }
      case "limpiar-sel": (b.dataset.k === "m" ? S.selM : S.selS).clear(); render(); break;
      case "agregar-srv": {
        const r = S.ultSrv[+b.dataset.i], q = NUM($("#qs-" + b.dataset.i).value) || 1;
        cot.items.push(Busqueda.itemDeServicio(r, q, siguienteId("S"))); S.selS.delete(r.c); guardarPronto(); render(); toast(`Agregado: ${r.s.slice(0, 50)}`); break;
      }
      case "limpiar-fm": S.fm = { fam: S.fm.fam }; render(); break;
      case "sold-fila": S.sold.push({ dn: "2", sch: "40", bw: "", sw: "", olet: "", tipoOlet: "cupla" }); render(); break;
      case "sold-quitar": S.sold.splice(+b.dataset.i, 1); if (!S.sold.length) S.sold.push({ dn: "2", sch: "40" }); render(); break;
      case "sold-agregar": agregarSoldaduras(S.sold); guardarPronto(); render(); toast("Soldaduras agregadas"); break;
      case "rx-agregar": {
        const pct = (S.rxPct ?? NUM($("#rx-pct").value)) || 0;
        if (!pct) { toast("Cargá el porcentaje de juntas a radiografiar"); return; }
        agregarRx(S.sold, pct); guardarPronto(); render(); toast("Radiografía agregada"); break;
      }
      case "pin-calc": { const m2 = m2Canos(); S.pinM2 = m2.toFixed(2); render(); toast(m2 ? `${num(m2)} m² de caños y niples (sin accesorios ni válvulas)` : "No hay caños con Ø, schedule y largo para calcular"); break; }
      case "pin-agregar": {
        const m2 = NUM($("#pin-m2").value);
        if (!m2 || !$("#pin-t").value) { toast("Cargá los m² y elegí la tarifa"); return; }
        agregarPintura(m2, $("#pin-t").value); guardarPronto(); render(); toast("Pintura agregada"); break;
      }
      case "rubro-modo": {
        const r = b.dataset.r;
        if (b.dataset.v === "global") { if (!Rubros.pasarAGlobal(cot, r, hoy())) return; toast(`${Rubros.RUBROS[r][0]}: global. Cargá el precio del tercero.`); }
        else { Rubros.volverADetallado(cot, r); toast(`${Rubros.RUBROS[r][0]}: detallado`); }
        guardarPronto(); render(); break;
      }
      case "ficha-copiar": case "ficha-bajar": {
        const r = b.dataset.r, t = Rubros.texto(cot, Rubros.ficha(cot, S.datos, S.sold, Motor), r, num);
        if (a === "ficha-copiar") { await navigator.clipboard.writeText(t); toast("Ficha copiada"); }
        else await S.dl.save({ filename: `${base()} - ficha ${r}.txt`, data: new Blob(["\ufeff" + t], { type: "text/plain;charset=utf-8" }) });
        break;
      }
      case "ph-agregar": agregarPH(NUM($("#ph-h").value) || 6); guardarPronto(); render(); toast("Prueba hidráulica agregada"); break;
      case "tarea-nueva": cot.plazo.tareas.push(["Nueva tarea", 0, 30, ""]); guardarPronto(); render(); break;
      case "tarea-quitar": cot.plazo.tareas.splice(+b.dataset.i, 1); guardarPronto(); render(); break;
      case "firmante-nuevo": editorFirmante(); break;
      case "firmante-editar": editorFirmante(S.firmantes.find(f => f.id === b.dataset.id)); break;
      case "firmante-guardar": {
        const f = S.editF;
        if (!f.nombre) { $("#ff-err").textContent = "Falta el nombre."; return; }
        const { id, ...resto } = f;
        await S.db.doc("firmantes/" + id).set(resto); capa.hidden = true; capa.innerHTML = ""; toast("Firmante guardado"); break;
      }
      case "ver-versiones": {
        const vs = await S.db.collection(`cotizaciones/${S.id}/versiones`).orderBy("guardado", "desc").limit(20).get();
        $("#versiones").innerHTML = vs.docs.length ? `<ul>${vs.docs.map(d => `<li>${FH(d.data().guardado)} · ${E(d.data().estado)} <button class="chico" data-a="restaurar" data-id="${E(d.id)}">Restaurar</button></li>`).join("")}</ul>` : "Todavía no hay versiones (se guarda una cada 10 minutos de trabajo y en cada cambio de estado).";
        break;
      }
      case "restaurar": {
        if (b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro? Restaurar"; return; }
        const d = await S.db.doc(`cotizaciones/${S.id}/versiones/${b.dataset.id}`).get();
        S.doc.cot = clon(d.data().cot); S.doc.oferta = clon(d.data().oferta); S.ultVersion = 0; guardarPronto(); render(); toast("Versión restaurada"); break;
      }
      case "zip": await descargarTodo(b); break;
      case "uno": await descargarUno(b, $("#un-archivo").value); break;
    }
  }

  // ------------------------------------------------------------------ descargas
  async function bytesDe(url) {
    if (!url) return null;
    try {
      const blob = await (await fetch(url)).blob();
      const img = await new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = URL.createObjectURL(blob); });
      return { bytes: new Uint8Array(await blob.arrayBuffer()), tipo: blob.type || "image/png", ancho: img.naturalWidth, alto: img.naturalHeight, url: img.src };
    } catch (e) { return null; }
  }
  async function contexto() {
    const cot = S.doc.cot, of = S.doc.oferta, c = calc(), fir = firmanteActual();
    const aprobado = cot.estado === "aprobado" || cot.estado === "enviado";
    const firma = await bytesDe(fir?.firma_url), plano = await bytesDe(of.imagen_plano_url);
    const pl = cot.plazo || {};
    return { cot, of, calc: c, firmante: fir, firma, firmaUrl: firma?.url, planoImg: plano, planoUrl: plano?.url, datos: S.datos, aprobado, logo: S.datos.logo,
      avisos: Busqueda.avisos(cot), plazo: { texto: `${pl.texto || ""}. ${pl.nota || ""}` } };
  }
  const base = () => (S.doc.oferta.archivo_base || S.doc.cot.codigo || "cotizacion").replace(/[\\/:*?"<>|]/g, "-");
  async function generar(k, ctx) {
    const cot = S.doc.cot;
    switch (k) {
      case "presupuesto": return Documentos.planilla(cot, S.datos.indices);
      case "compras": return Documentos.compras(cot);
      case "informe": return Documentos.pdfDeHtml(Documentos.informeHtml(ctx));
      case "tec_docx": return Documentos.ofertaDocx("tecnica", ctx);
      case "eco_docx": return Documentos.ofertaDocx("economica", ctx);
      case "tec_pdf": return Documentos.pdfDeHtml(Documentos.ofertaHtml("tecnica", ctx));
      case "eco_pdf": return Documentos.pdfDeHtml(Documentos.ofertaHtml("economica", ctx));
      case "json": return new Blob([JSON.stringify({ cotizacion: S.doc.cot, oferta: S.doc.oferta, exportado: new Date().toISOString() }, null, 1)], { type: "application/json" });
    }
  }
  async function vistaPrevia(k) {
    capa.hidden = false; capa.innerHTML = `<div class="capa"><section class="panel vista"><div class="vacio">Armando la vista previa…</div></section></div>`;
    const ctx = await contexto();
    const [titulo, html, desc] = k === "informe" ? ["Informe del presupuesto", Documentos.informeHtml(ctx), "informe"]
      : k === "tecnica" ? ["Oferta técnica", Documentos.ofertaHtml("tecnica", ctx), "tec_pdf"] : ["Oferta económica", Documentos.ofertaHtml("economica", ctx), "eco_pdf"];
    capa.innerHTML = `<div class="capa"><section class="panel vista" role="dialog" aria-label="${E(titulo)}"><div class="fila"><h2 style="flex:1">${E(titulo)}</h2>
      <button class="chico" data-a="uno-k" data-k="${desc}" ${S.dl ? "" : "disabled"}>Descargar PDF</button><button class="chico" data-a="cerrar">Cerrar</button></div>
      <div class="hoja">${html}</div></section></div>`;
  }
  const estadoDesc = t => { const el = $("#desc-estado"); if (el) el.textContent = t; };
  async function descargarTodo(b) {
    if (b) b.disabled = true;
    try {
      const ctx = await contexto(), zip = new JSZip(), carpeta = zip.folder(base());
      for (const [k, n] of ARCHIVOS) { estadoDesc(`Generando ${n}…`); carpeta.file(n, await generar(k, ctx)); }
      estadoDesc("Comprimiendo…");
      const blob = await zip.generateAsync({ type: "blob" });
      await S.dl.save({ filename: base() + ".zip", data: blob });
      estadoDesc("Listo: " + base() + ".zip");
    } catch (e) { estadoDesc(e.code === "declined" ? "Descarga cancelada." : "No se pudo descargar: " + (e.message || e.code)); if (!b) throw e; }
    finally { if (b) b.disabled = false; }
  }
  async function descargarUno(b, k) {
    if (b) b.disabled = true;
    try {
      const n = ARCHIVOS.find(x => x[0] === k)[1]; estadoDesc(`Generando ${n}…`);
      const blob = await generar(k, await contexto());
      await S.dl.save({ filename: `${base()} - ${n}`, data: blob }); estadoDesc("Listo: " + n);
    } catch (e) { estadoDesc(e.code === "declined" ? "Descarga cancelada." : "No se pudo descargar: " + (e.message || e.code)); if (!b) throw e; }
    finally { if (b) b.disabled = false; }
  }

  window.ITT = { S, $, E, num, toast, clon, hoy, render, refrescar, guardarPronto, calc, siguienteId, nuevoId, crearCotizacion, duplicarCotizacion, borrarCotizacion, abrir, accion, cambiarEstado, editorItem,
    agregarSoldaduras, agregarRx, m2Canos, agregarPintura, agregarPH, tarifasPintura, tarifaPH, descargarTodo, descargarUno, ARCHIVOS, resumenDe };
  window.dispatchEvent(new Event("itt-listo"));
  ruta();
})();
