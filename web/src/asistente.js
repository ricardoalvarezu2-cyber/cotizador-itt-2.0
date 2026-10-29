// Asistente de la página: chat y pedidos para Claude Code (capacidad "mcp", conector Claude Code Remote → send_message a
// la sesión fija con el repositorio; la respuesta vuelve por la base de la página). Los archivos se suben con "assets"; Excel y Word
// se pasan a texto antes de subir (assets solo guarda imágenes, PDF y texto). Ver web/LEEME.md, "Pedidos desde la página".
const Asistente = (() => {
  const URL_PAGINA = "https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ";
  const SERVIDOR = "Claude Code Remote";
  const SESION_FIJA = "session_01Y6ZcPeLckws2e9s2DF8RJ3"; // "Cotizador ITT – tarea semanal"; se puede cambiar en config/claude_code
  const TIPOS_PEDIDO = {
    cotizacion_nueva: "Armar una cotización nueva (plano, P&ID, pliego)",
    actualizar_cotizacion: "Completar o corregir una cotización existente",
    lista_precios: "Incorporar una lista o cotización de precios al catálogo",
    incorporar_base: "Incorporar una cotización terminada a la base (catálogos y antecedentes)",
    otro: "Otro",
  };
  const ESTADOS_PEDIDO = { pendiente: ["pendiente", "warn"], enviado: ["enviado", "info"], en_proceso: ["en proceso", "info"], listo: ["listo", "ok"], con_dudas: ["con dudas", "warn"], error: ["error", "bad"] };
  const MAX_MB = 20;

  let I = null, mcp = null, sesion = SESION_FIJA;
  const P = { lista: [], form: { tipo: "cotizacion_nueva", texto: "", cot: "" }, archivos: [], ocupado: false };
  const chat = { msgs: [], adjuntos: [], conv: "", ocupado: false, abierto: false, recien: false };

  // ------------------------------------------------------------------ arranque
  const listo = window.ITT ? Promise.resolve() : new Promise(ok => window.addEventListener("itt-listo", ok, { once: true }));
  listo.then(async () => {
    I = window.ITT;
    const usar = n => (window.claude && window.claude.use ? window.claude.use(n).catch(() => null) : Promise.resolve(null));
    mcp = await usar("mcp");
    const S = I.S;
    if (S.db) {
      S.db.doc("config/claude_code").get().then(d => { if (d.exists && d.data().session_id) sesion = d.data().session_id; }).catch(() => {});
      S.db.collection("pedidos").onSnapshot(sn => {
        P.lista = sn.docs.map(d => ({ id: d.id, ...d.data() })).sort((a, b) => String(b.creado).localeCompare(String(a.creado)));
        const activos = P.lista.filter(p => ["pendiente", "enviado", "en_proceso"].includes(p.estado)).length;
        const nav = document.getElementById("nav-pedidos");
        if (nav) nav.dataset.cnt = activos || "";
        if (S.vista === "pedidos") renderPedidos(document.getElementById("app"));
      }, () => {});
    }
    if (S.db) S.db.collection("catalogo_nuevo").onSnapshot(sn => { P.nuevos = sn.docs.map(d => ({ id: d.id, ...d.data() })); mezclarNuevos(); if (S.vista === "pedidos") renderPedidos(document.getElementById("app")); }, () => {});
    armarChat();
  });

  // Artículos y servicios nuevos cargados en la página (colección catalogo_nuevo): se suman al buscador al instante y
  // la tarea de los lunes los pasa al catálogo del repositorio (después quedan marcados "incorporado" y no se repiten).
  function mezclarNuevos() {
    const D = I.S.datos;
    D.materiales = D.materiales.filter(m => !m.nuevo); D.servicios = D.servicios.filter(s => !s.nuevo);
    for (const n of P.nuevos || []) {
      if (n.incorporado) continue;
      if (n.clase === "material") D.materiales.unshift({ ...n.registro, c: n.id, nuevo: true });
      else D.servicios.unshift({ ...n.registro, c: n.id, nuevo: true });
    }
  }

  // id único aunque se pidan varios en el mismo milisegundo (contador + azar)
  let secuencia = 0;
  const idUnico = pref => pref + Date.now().toString(36) + (++secuencia).toString(36) + Math.random().toString(36).slice(2, 6);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const ahora = () => new Date().toISOString();
  const fechaCorta = iso => Documentos.fechaHora(iso); // DD-MM-AAAA HH:MM

  // ------------------------------------------------------------------ archivos: conversión y subida
  async function prepararArchivo(file) {
    const ext = (file.name.split(".").pop() || "").toLowerCase();
    if (file.size > MAX_MB * 1048576) throw new Error(`${file.name}: pesa más de ${MAX_MB} MB`);
    const tipos = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp", gif: "image/gif", pdf: "application/pdf",
      csv: "text/csv", txt: "text/plain", md: "text/markdown", json: "application/json" };
    if (tipos[ext]) return { blob: file, nombre: file.name, tipo: tipos[ext] };
    if (["xlsx", "xlsm", "xls", "ods"].includes(ext)) {
      const wb = XLSX.read(await file.arrayBuffer(), { type: "array" });
      const partes = wb.SheetNames.map(n => `## Hoja: ${n}\n\n\`\`\`csv\n${XLSX.utils.sheet_to_csv(wb.Sheets[n], { rawNumbers: true, blankrows: false })}\n\`\`\``);
      const md = `# ${file.name}\n\nConvertido de Excel en la página (${new Date().toLocaleDateString("es-AR")}). Números en formato de máquina: el punto es decimal.\n\n${partes.join("\n\n")}\n`;
      return { blob: new Blob([md], { type: "text/markdown" }), nombre: file.name + ".md", tipo: "text/markdown", original: file.name };
    }
    if (ext === "docx") {
      const z = await JSZip.loadAsync(await file.arrayBuffer());
      const xml = new DOMParser().parseFromString(await z.file("word/document.xml").async("string"), "application/xml");
      const W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
      const txt = el => Array.from(el.getElementsByTagNameNS(W, "t")).map(t => t.textContent).join("");
      const lineas = [];
      for (const el of Array.from(xml.getElementsByTagNameNS(W, "body")[0].children)) {
        if (el.localName === "p") lineas.push(txt(el));
        else if (el.localName === "tbl") for (const tr of Array.from(el.getElementsByTagNameNS(W, "tr"))) lineas.push("| " + Array.from(tr.getElementsByTagNameNS(W, "tc")).map(txt).join(" | ") + " |");
      }
      const md = `# ${file.name}\n\nConvertido de Word en la página (${new Date().toLocaleDateString("es-AR")}).\n\n${lineas.join("\n")}\n`;
      return { blob: new Blob([md], { type: "text/markdown" }), nombre: file.name + ".md", tipo: "text/markdown", original: file.name };
    }
    throw new Error(`${file.name}: formato no admitido (.${ext}). Guardalo como PDF, imagen, Excel o Word.`);
  }
  async function subir(files, aviso) {
    const S = I.S;
    if (!files.length) return [];
    if (!S.assets) throw new Error("Esta vista no puede subir archivos (hace falta permiso de edición en la página).");
    const out = [];
    for (const f of files) {
      aviso?.(`Subiendo ${f.name}…`);
      const a = await prepararArchivo(f);
      const r = await S.assets.upload(a.blob, { type: a.tipo });
      out.push({ id: r.id, url: r.url, nombre: a.nombre, tipo: a.tipo, ...(a.original ? { original: a.original } : {}), bytes: r.sizeBytes });
    }
    return out;
  }

  // ------------------------------------------------------------------ pedidos
  async function crearPedido({ tipo, texto, cot, files, mandar }, aviso) {
    const S = I.S;
    if (!S.db) throw new Error("Sin conexión con la base.");
    if (!texto.trim() && !files.length) throw new Error("Escribí qué necesitás o subí un archivo.");
    if (tipo === "actualizar_cotizacion" && !cot) throw new Error("Elegí la cotización a completar o corregir.");
    const archivos = await subir(files, aviso);
    const id = idUnico("p");
    const doc = { tipo, texto: texto.trim(), cotizacion_id: cot || "", archivos, estado: "pendiente", creado: ahora(), historial: [{ fecha: ahora(), estado: "pendiente", nota: "creado en la página" }] };
    await S.db.doc("pedidos/" + id).set(doc);
    if (mandar) await mandarPedido(id, doc, aviso);
    return id;
  }
  function motivoError(e) {
    const c = e.code;
    if (["server_unavailable", "upstream_error", "cancelled"].includes(c)) return ["error", "no se sabe si llegó (" + c + "): mirá la sesión de Claude Code antes de reenviar"];
    return ["pendiente", c === "server_not_connected" ? "falta el conector Claude Code Remote (claude.ai → Configuración → Conectores)"
      : c === "not_in_manifest" ? "no se dio permiso a la página para usar Claude Code"
      : c === "approval_required" ? "hace falta aprobar el envío; volvé a intentar"
      : c === "needs_reauth" ? "hay que volver a conectar Claude Code Remote en claude.ai"
      : c === "tool_error" ? "Claude Code respondió con un error: " + (e.message || "").slice(0, 200)
      : "no se pudo mandar (" + (c || e.message) + ")"];
  }
  async function mandarPedido(id, doc, aviso) {
    const S = I.S;
    if (!mcp) throw new Error("Esta vista no puede comunicarse con Claude Code. Quedó pendiente: se procesa el lunes o cuando lo pidas en un chat.");
    aviso?.("Mandando el pedido a Claude Code…");
    const msg = `Pedido ${id} desde la página del cotizador (${URL_PAGINA}).\n` +
      `Primero git pull origin main. Después leé el documento pedidos/${id} de esa página con ArtifactData y seguí web/LEEME.md, sección "Pedidos desde la página".\n` +
      `Tipo: ${doc.tipo} (${TIPOS_PEDIDO[doc.tipo] || ""}).${doc.cotizacion_id ? ` Cotización: cotizaciones/${doc.cotizacion_id}.` : ""} Archivos: ${doc.archivos.length}.\n` +
      `Pedido: ${(doc.texto || "(sin texto)").slice(0, 1500)}`;
    let estado = "enviado", nota = "mandado a Claude Code";
    try { await mcp.callTool(SERVIDOR, "send_message", { session_id: sesion, message: msg, priority: "later" }); }
    catch (e) { [estado, nota] = motivoError(e); }
    const d = await S.db.doc("pedidos/" + id).get();
    const h = (d.exists && d.data().historial) || [];
    await S.db.doc("pedidos/" + id).update({ estado, ...(estado === "enviado" ? { enviado: ahora() } : {}), nota, historial: [...h, { fecha: ahora(), estado, nota }] });
    if (estado !== "enviado") throw new Error(nota.charAt(0).toUpperCase() + nota.slice(1) + ". El pedido quedó guardado.");
  }

  function renderPedidos(app) {
    I = I || window.ITT; // puede llegar antes de que termine el arranque del asistente
    const S = I.S, f = P.form;
    const cots = [...S.lista].sort((a, b) => String(b.actualizado).localeCompare(String(a.actualizado)));
    const pill = e => { const [t, c] = ESTADOS_PEDIDO[e] || [e, "info"]; return `<span class="pill ${c}">${esc(t)}</span>`; };
    app.innerHTML = `<section><div class="sec-head"><h1>Pedidos</h1><span class="eyebrow">archivos y trabajos para Claude Code</span></div>
      <p class="small muted">Subí un plano, un P&ID, un pliego o una lista de precios y escribí qué necesitás. Claude Code trabaja sobre el repositorio con el procedimiento de cotización: arma la cotización o actualiza el catálogo, deja el resultado acá en borrador y lo sube a GitHub. Tarda unos minutos y usa tu cuenta de Claude. Nada se envía al cliente.</p>
      <section class="panel"><h3>Nuevo pedido</h3><div class="campos">
        <label><span>Qué es</span><select id="pd-tipo">${Object.entries(TIPOS_PEDIDO).map(([k, v]) => `<option value="${k}" ${f.tipo === k ? "selected" : ""}>${esc(v)}</option>`).join("")}</select></label>
        <label><span>Cotización ${f.tipo === "actualizar_cotizacion" ? "(obligatorio)" : "(opcional)"}</span><select id="pd-cot"><option value="">— ninguna —</option>${cots.map(c => `<option value="${esc(c.id)}" ${f.cot === c.id ? "selected" : ""}>${esc(c.codigo)} · ${esc((c.titulo || "").slice(0, 60))}</option>`).join("")}</select></label>
        <label class="ancho"><span>Qué necesitás</span><textarea id="pd-texto" placeholder="Ej.: Cotizar 2 puentes según el plano adjunto para CAPEX, pedido OQ 8209, entrega en 75 días.">${esc(f.texto)}</textarea></label>
        <label class="ancho"><span>Archivos (PDF, imágenes, Excel, Word, CSV; hasta ${MAX_MB} MB cada uno)</span><input id="pd-arch" type="file" multiple accept=".pdf,.png,.jpg,.jpeg,.webp,.xlsx,.xlsm,.xls,.ods,.docx,.csv,.txt,.md,.json" ${S.assets ? "" : "disabled"}></label>
        ${P.archivos.length ? `<div class="ancho small">${P.archivos.map(x => esc(x.name)).join(" · ")}</div>` : ""}
      </div>
      ${S.assets ? "" : '<p class="err">Esta vista no puede subir archivos: hace falta permiso de edición en la página.</p>'}
      <div class="fila"><button class="prim" data-p="mandar" ${P.ocupado ? "disabled" : ""} ${mcp ? "" : "disabled"}>Guardar y mandar a Claude Code</button>
        <button data-p="guardar" ${P.ocupado ? "disabled" : ""}>Guardar como pendiente</button><span class="small muted" id="pd-estado"></span></div>
      ${mcp ? "" : '<p class="small muted">En esta vista no se puede llamar a Claude Code: el pedido queda pendiente y se procesa el lunes con la tarea semanal, o cuando lo pidas en un chat.</p>'}</section>
      ${P.lista.length ? `<div class="tbl"><table><thead><tr><th>Fecha</th><th>Pedido</th><th>Archivos</th><th>Estado</th><th>Resultado</th><th></th></tr></thead><tbody>
        ${P.lista.map(p => `<tr><td class="small">${fechaCorta(p.creado)}</td>
          <td><div class="d">${esc(TIPOS_PEDIDO[p.tipo] || p.tipo)}</div><div class="sp">${esc((p.texto || "").slice(0, 220))}</div>
            ${p.cotizacion_id ? `<div class="sp">Cotización: <a href="#c-${esc(p.cotizacion_id)}">${esc(S.lista.find(c => c.id === p.cotizacion_id)?.codigo || p.cotizacion_id)}</a></div>` : ""}</td>
          <td class="small">${(p.archivos || []).map(a => `<a href="${esc(a.url || "/_blob/" + a.id)}" target="_blank" rel="noopener">${esc(a.original || a.nombre)}</a>`).join("<br>") || "—"}</td>
          <td>${pill(p.estado)}${p.nota ? `<div class="sp">${esc(p.nota)}</div>` : ""}</td>
          <td class="small">${esc(p.respuesta || "")}${p.resultado_cotizacion_id ? `<div><a href="#c-${esc(p.resultado_cotizacion_id)}">Abrir la cotización</a></div>` : ""}</td>
          <td><div class="fila fin">${["pendiente", "error"].includes(p.estado) && mcp ? `<button class="chico" data-p="reenviar" data-id="${esc(p.id)}">${p.estado === "error" ? "Reenviar" : "Mandar ahora"}</button>` : ""}
            <button class="chico peligro" data-p="borrar" data-id="${esc(p.id)}">Borrar</button></div></td></tr>`).join("")}
      </tbody></table></div>` : `<div class="vacio">Todavía no hay pedidos.</div>`}
      ${nuevosHtml()}</section>`;
  }

  function nuevosHtml() {
    const ns = (P.nuevos || []).filter(n => !n.incorporado).sort((a, b) => String(b.creado).localeCompare(String(a.creado)));
    if (!ns.length) return "";
    return `<section><div class="sec-head"><h2>Artículos y servicios nuevos</h2><span class="eyebrow">ya están en el buscador · el lunes pasan al catálogo del repositorio</span></div>
      <div class="tbl"><table><thead><tr><th>Código</th><th>Descripción</th><th class="n">USD sin IVA</th><th>Proveedor y fecha</th><th>Documento</th><th></th></tr></thead><tbody>
      ${ns.map(n => { const r = n.registro || {}; return `<tr><td class="mono small">${esc(n.id)}</td><td><div class="d">${esc(r.d || r.s)}</div><div class="sp">${esc(n.clase === "material" ? (I.S.datos.familias[r.f]?.n || r.f) : r.h)} · ${esc(r.u || r.ut || "")}${r.al ? " · " + esc(r.al) : ""}</div></td>
        <td class="n">${esc((r.t || r.p)?.toLocaleString("es-AR", { maximumFractionDigits: 4 }))}</td><td class="small">${esc(r.pr)}<br><span class="muted">${esc(Documentos.fecha(r.fe))}</span></td><td class="small">${esc(n.original?.documento || "")}</td>
        <td><button class="chico peligro" data-p="nuevo-borrar" data-id="${esc(n.id)}">Borrar</button></td></tr>`; }).join("")}</tbody></table></div></section>`;
  }

  document.addEventListener("input", ev => {
    const el = ev.target;
    if (el.id === "pd-texto") P.form.texto = el.value;
  });
  document.addEventListener("change", ev => {
    const el = ev.target;
    if (el.id === "pd-tipo") { P.form.tipo = el.value; renderPedidos(document.getElementById("app")); }
    else if (el.id === "pd-cot") P.form.cot = el.value;
    else if (el.id === "pd-arch") { P.archivos = Array.from(el.files); renderPedidos(document.getElementById("app")); }
    else if (el.id === "ch-arch") { chat.adjuntos.push(...Array.from(el.files)); el.value = ""; pintarAdjuntos(); }
  });
  document.addEventListener("click", async ev => {
    const b = ev.target.closest("[data-p]"); if (!b) return;
    const S = I.S, est = t => { const e = document.getElementById("pd-estado"); if (e) e.textContent = t; };
    try {
      switch (b.dataset.p) {
        case "guardar": case "mandar": {
          P.ocupado = true; renderPedidos(document.getElementById("app"));
          try {
            await crearPedido({ ...P.form, files: P.archivos, mandar: b.dataset.p === "mandar" }, est);
            P.form = { tipo: P.form.tipo, texto: "", cot: "" }; P.archivos = [];
            I.toast(b.dataset.p === "mandar" ? "Pedido mandado a Claude Code" : "Pedido guardado como pendiente");
          } finally { P.ocupado = false; renderPedidos(document.getElementById("app")); }
          break;
        }
        case "reenviar": {
          const p = P.lista.find(x => x.id === b.dataset.id);
          if (p.estado === "error" && b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro? Puede haber llegado"; return; }
          b.disabled = true; await mandarPedido(p.id, p); I.toast("Pedido mandado a Claude Code"); break;
        }
        case "borrar":
          if (b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro? Borrar"; setTimeout(() => { b.dataset.ok = ""; b.textContent = "Borrar"; }, 4000); return; }
          await S.db.doc("pedidos/" + b.dataset.id).delete(); I.toast("Pedido borrado (los archivos subidos se conservan)"); break;
        case "ch-reenviar": {
          const m = chat.msgs.find(x => x.id === b.dataset.id); if (!m) return;
          if (m.estado === "error" && b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro? Puede haber llegado"; return; }
          b.disabled = true; await mandarChat(m.id, m); break;
        }
        case "nuevo-borrar":
          if (b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro?"; setTimeout(() => { b.dataset.ok = ""; b.textContent = "Borrar"; }, 4000); return; }
          await S.db.doc("catalogo_nuevo/" + b.dataset.id).delete(); I.toast("Borrado del catálogo nuevo"); break;
      }
    } catch (e) { I.toast(e.message || String(e.code || e)); }
  });

  // ------------------------------------------------------------------ chat: cada mensaje va a la sesión de Claude Code
  // Colección "chat": un documento por mensaje {conversacion, texto, archivos, contexto, estado, creado, nota, avance,
  // respuesta, cambios, respondido}. La sesión fija lo lee con ArtifactData, trabaja sobre el repositorio y la página
  // (control total, ver web/LEEME.md "Chat de la página") y escribe la respuesta en el mismo documento.
  const ESPERA = { enviado: "Esperando a Claude Code…", en_proceso: "Claude Code está trabajando…" };
  function armarChat() {
    const btn = document.getElementById("btn-chat"), panel = document.getElementById("chat");
    if (!btn || !panel || !I.S.db) return;
    btn.hidden = false;
    btn.addEventListener("click", () => abrirChat(!chat.abierto));
    try { chat.conv = localStorage.getItem("itt-conv") || ""; } catch (e) { /* sin almacenamiento */ }
    if (!chat.conv) nuevaConversacion();
    panel.innerHTML = `<div class="ch-cab"><div class="fila"><b>Claude Code</b><span class="small muted" id="ch-ctx"></span><button class="chico" id="ch-cerrar" aria-label="Cerrar el chat">×</button></div>
        <div class="fila"><button class="chico" id="ch-nuevo">Nueva conversación</button></div></div>
      <div class="ch-msgs" id="ch-msgs" aria-live="polite"></div>
      <div class="ch-pie"><div id="ch-adj" class="small"></div>
        <textarea id="ch-txt" rows="3" placeholder="Ej.: armá la cotización del plano adjunto · ¿cuánto se cobró la última trampa 8&quot;? · corregí la pintura de esta cotización"></textarea>
        <div class="fila"><label class="btn chico" style="flex-direction:row">Adjuntar archivo<input id="ch-arch" type="file" multiple accept="image/png,image/jpeg,image/webp,application/pdf,.xlsx,.xls,.xlsm,.ods,.docx,.csv,.txt,.md,.json" hidden></label>
          <span style="flex:1"></span><button class="prim chico" id="ch-enviar" ${mcp ? "" : "disabled"}>Enviar</button></div>
        <span class="small muted" id="ch-estado">${mcp ? "Trabaja sobre el repositorio con tu cuenta de Claude. Cada respuesta tarda de 1 a 3 minutos." : "En esta vista no se puede llamar a Claude Code (falta el conector Claude Code Remote o el permiso de la página)."}</span></div>`;
    panel.querySelector("#ch-cerrar").onclick = () => abrirChat(false);
    panel.querySelector("#ch-nuevo").onclick = () => { nuevaConversacion(); pintarChat(); };
    panel.querySelector("#ch-enviar").onclick = enviar;
    panel.querySelector("#ch-txt").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(); } });
    window.addEventListener("hashchange", pintarContexto);
    I.S.db.collection("chat").onSnapshot(sn => { chat.msgs = sn.docs.map(d => ({ id: d.id, ...d.data() })); pintarChat(); }, () => {});
    setInterval(() => { if (chat.abierto && chat.msgs.some(m => ESPERA[m.estado])) pintarChat(); }, 60e3);
    pintarChat();
    try { if (localStorage.getItem("itt-chat") === "1") abrirChat(true); } catch (e) { /* sin almacenamiento */ }
  }
  function nuevaConversacion() {
    chat.conv = idUnico("v");
    try { localStorage.setItem("itt-conv", chat.conv); } catch (e) { /* sin almacenamiento */ }
  }
  function abrirChat(si) {
    chat.abierto = si;
    document.getElementById("chat").hidden = !si;
    document.body.classList.toggle("con-chat", si);
    document.getElementById("btn-chat").setAttribute("aria-pressed", String(si));
    try { localStorage.setItem("itt-chat", si ? "1" : "0"); } catch (e) { /* sin almacenamiento */ }
    if (si) { pintarContexto(); pintarChat(); document.getElementById("ch-txt").focus(); }
  }
  function pintarContexto() {
    const S = I.S, el = document.getElementById("ch-ctx"); if (!el) return;
    el.textContent = S.vista === "cot" && S.doc ? "sobre " + S.doc.cot.codigo : "";
  }
  function md(t) {
    return esc(t).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").split("\n").map(l => /^\s*[-•] /.test(l) ? `<li>${l.replace(/^\s*[-•] /, "")}</li>` : l + "<br>").join("")
      .replace(/(<li>.*?<\/li>)+/g, m => `<ul>${m}</ul>`).replace(/(<br>)+$/, "");
  }
  const delaConv = () => chat.msgs.filter(m => m.conversacion === chat.conv).sort((a, b) => String(a.creado).localeCompare(String(b.creado)));
  function pintarChat() {
    const box = document.getElementById("ch-msgs"); if (!box) return;
    const abajo = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
    const hora = iso => iso ? fechaCorta(iso).slice(-5) : "";
    const ms = delaConv();
    box.innerHTML = (ms.length ? "" : `<div class="msg a">Hola. Hablás con Claude Code, que trabaja sobre el repositorio y la página: busca en el historial, los catálogos y los antecedentes, arma y corrige cotizaciones, lee planos, pliegos y listas de precios, y puede cambiar la página. Nada se envía al cliente.</div>`)
      + ms.map(m => {
        const arch = (m.archivos || []).length ? `<div class="small muted">Adjuntó: ${m.archivos.map(a => esc(a.original || a.nombre)).join(", ")}</div>` : "";
        const u = `<div class="msg u">${esc(m.texto).replace(/\n/g, "<br>")}${arch}</div>`;
        if (m.respuesta) return u + `<div class="msg a">${md(m.respuesta)}${(m.cambios || []).length ? `<div class="small muted">Cambió: ${m.cambios.map(esc).join(" · ")}</div>` : ""}<div class="small muted">${hora(m.respondido)}</div></div>`;
        if (ESPERA[m.estado]) {
          const min = (Date.now() - Date.parse(m.enviado || m.creado)) / 60e3;
          return u + `<div class="msg a pensando">${ESPERA[m.estado]}${m.avance ? `<div class="small">${esc(m.avance)}</div>` : ""}${min > 15 ? `<div class="small">Tarda más de lo normal: puede estar con un trabajo largo o con otro pedido antes.</div>` : ""}</div>`;
        }
        return u + `<div class="msg a"><span class="err">${esc(m.nota || "No se mandó.")}</span> <button class="chico" data-p="ch-reenviar" data-id="${esc(m.id)}" ${mcp ? "" : "disabled"}>Reenviar</button></div>`;
      }).join("");
    if (abajo || chat.recien) { box.scrollTop = box.scrollHeight; chat.recien = false; }
  }
  function pintarAdjuntos() {
    const el = document.getElementById("ch-adj"); if (!el) return;
    el.innerHTML = chat.adjuntos.map((f, i) => `<span class="pill info">${esc(f.name)} <button class="chico" data-quitar-adj="${i}" aria-label="Quitar">×</button></span>`).join(" ");
    el.querySelectorAll("[data-quitar-adj]").forEach(b => (b.onclick = () => { chat.adjuntos.splice(+b.dataset.quitarAdj, 1); pintarAdjuntos(); }));
  }
  const contextoPagina = () => { const S = I.S, c = S.vista === "cot" && S.doc; return { vista: S.vista || "", cotizacion_id: c ? S.id : "", codigo: c ? S.doc.cot.codigo : "", pestana: c ? S.tab || "" : "" }; };
  async function enviar() {
    if (chat.ocupado || !mcp) return;
    const ta = document.getElementById("ch-txt"), texto = ta.value.trim(), files = chat.adjuntos.slice(), est = document.getElementById("ch-estado");
    if (!texto && !files.length) return;
    chat.ocupado = true; document.getElementById("ch-enviar").disabled = true;
    const aviso = t => (est.textContent = t);
    try {
      const archivos = await subir(files, aviso);
      const id = idUnico("m"), doc = { conversacion: chat.conv, texto, archivos, contexto: contextoPagina(), estado: "pendiente", creado: ahora() };
      await I.S.db.doc("chat/" + id).set(doc);
      ta.value = ""; chat.adjuntos = []; pintarAdjuntos(); chat.recien = true;
      aviso("Mandando a Claude Code…");
      await mandarChat(id, doc);
      aviso("Mandado. La respuesta aparece acá en 1 a 3 minutos; podés seguir trabajando.");
    } catch (e) { aviso(e.message || String(e.code || e)); }
    finally { chat.ocupado = false; document.getElementById("ch-enviar").disabled = false; }
  }
  async function mandarChat(id, doc) {
    const ctx = doc.contexto || {};
    const previos = delaConv().filter(m => m.id !== id && m.creado < doc.creado).slice(-6);
    const msg = `Chat ${id} desde la página del cotizador (${URL_PAGINA}).\n` +
      `Seguí web/LEEME.md, sección "Chat de la página" (primero git pull origin main). Leé el documento chat/${id} con ArtifactData y respondé en ese mismo documento.\n` +
      `Página: ${ctx.vista || "inicio"}${ctx.cotizacion_id ? `, cotización abierta ${ctx.codigo} (documento cotizaciones/${ctx.cotizacion_id}), pestaña ${ctx.pestana}` : ""}. Conversación ${doc.conversacion}. Archivos adjuntos: ${(doc.archivos || []).length}.\n` +
      (previos.length ? `Antes en esta conversación:\n${previos.map(p => `- Matías: ${String(p.texto).slice(0, 400)}\n  Claude Code: ${String(p.respuesta || "(sin respuesta)").slice(0, 600)}`).join("\n")}\n` : "") +
      `Mensaje de Matías:\n${String(doc.texto || "(sin texto, ver archivos)").slice(0, 8000)}`;
    let estado = "enviado", nota = "";
    try { await mcp.callTool(SERVIDOR, "send_message", { session_id: sesion, message: msg, priority: "later" }); }
    catch (e) { [estado, nota] = motivoError(e); }
    await I.S.db.doc("chat/" + id).update({ estado, nota, ...(estado === "enviado" ? { enviado: ahora() } : {}) });
    if (estado !== "enviado") throw new Error(nota.charAt(0).toUpperCase() + nota.slice(1) + ".");
  }

  return { renderPedidos, abrirChat, TIPOS_PEDIDO, prepararArchivo, crearPedido };
})();
if (typeof module !== "undefined") module.exports = Asistente;
