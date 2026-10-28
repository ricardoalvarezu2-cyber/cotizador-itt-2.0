// Asistente de la página: chat con Claude (capacidad "sample") y pedidos para Claude Code (capacidad "mcp", conector
// Claude Code Remote → send_message a la sesión fija con el repositorio). Los archivos se suben con "assets"; Excel y Word
// se pasan a texto antes de subir (assets solo guarda imágenes, PDF y texto). Ver web/LEEME.md, "Pedidos desde la página".
const Asistente = (() => {
  const URL_PAGINA = "https://claude.ai/artifact/HfbiaNvhAFkQjYwLe2kaBQ";
  const SERVIDOR = "Claude Code Remote";
  const SESION_FIJA = "session_01Y6ZcPeLckws2e9s2DF8RJ3"; // "Cotizador ITT – tarea semanal"; se puede cambiar en config/claude_code
  const TIPOS_PEDIDO = {
    cotizacion_nueva: "Armar una cotización nueva (plano, P&ID, pliego)",
    actualizar_cotizacion: "Completar o corregir una cotización existente",
    lista_precios: "Incorporar una lista o cotización de precios al catálogo",
    otro: "Otro",
  };
  const ESTADOS_PEDIDO = { pendiente: ["pendiente", "warn"], enviado: ["enviado", "info"], en_proceso: ["en proceso", "info"], listo: ["listo", "ok"], con_dudas: ["con dudas", "warn"], error: ["error", "bad"] };
  const MAX_MB = 20;

  let I = null, sample = null, mcp = null, limites = null, sesion = SESION_FIJA;
  const P = { lista: [], form: { tipo: "cotizacion_nueva", texto: "", cot: "" }, archivos: [], ocupado: false };
  const chat = { turnos: [], adjuntos: [], todosAdjuntos: [], ctl: null, ocupado: false, deshacer: [], abierto: false, propuesta: null };

  // ------------------------------------------------------------------ arranque
  const listo = window.ITT ? Promise.resolve() : new Promise(ok => window.addEventListener("itt-listo", ok, { once: true }));
  listo.then(async () => {
    I = window.ITT;
    const usar = n => (window.claude && window.claude.use ? window.claude.use(n).catch(() => null) : Promise.resolve(null));
    [sample, mcp] = await Promise.all([usar("sample"), usar("mcp")]);
    limites = sample ? await sample.limits().catch(() => null) : null;
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
    armarChat();
  });

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const ahora = () => new Date().toISOString();
  const fechaCorta = iso => iso ? new Date(iso).toLocaleString("es-AR", { dateStyle: "short", timeStyle: "short" }) : "";

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
    const id = "p" + Date.now().toString(36);
    const doc = { tipo, texto: texto.trim(), cotizacion_id: cot || "", archivos, estado: "pendiente", creado: ahora(), historial: [{ fecha: ahora(), estado: "pendiente", nota: "creado en la página" }] };
    await S.db.doc("pedidos/" + id).set(doc);
    if (mandar) await mandarPedido(id, doc, aviso);
    return id;
  }
  async function mandarPedido(id, doc, aviso) {
    const S = I.S;
    if (!mcp) throw new Error("Esta vista no puede comunicarse con Claude Code. Quedó pendiente: se procesa el lunes o cuando lo pidas en un chat.");
    aviso?.("Mandando el pedido a Claude Code…");
    const msg = `Pedido ${id} desde la página del cotizador (${URL_PAGINA}).\n` +
      `Leé el documento pedidos/${id} de esa página con ArtifactData y seguí web/LEEME.md, sección "Pedidos desde la página".\n` +
      `Tipo: ${doc.tipo} (${TIPOS_PEDIDO[doc.tipo] || ""}).${doc.cotizacion_id ? ` Cotización: cotizaciones/${doc.cotizacion_id}.` : ""} Archivos: ${doc.archivos.length}.\n` +
      `Pedido: ${(doc.texto || "(sin texto)").slice(0, 1500)}`;
    let estado = "enviado", nota = "mandado a Claude Code";
    try {
      await mcp.callTool(SERVIDOR, "send_message", { session_id: sesion, message: msg, priority: "later" });
    } catch (e) {
      const c = e.code;
      if (["server_unavailable", "upstream_error", "cancelled"].includes(c)) { estado = "error"; nota = "no se sabe si llegó (" + c + "): mirá la sesión de Claude Code antes de reenviar"; }
      else {
        estado = "pendiente";
        nota = c === "server_not_connected" ? "falta el conector Claude Code Remote (claude.ai → Configuración → Conectores)"
          : c === "not_in_manifest" ? "no se dio permiso a la página para usar Claude Code"
          : c === "approval_required" ? "hace falta aprobar el envío; volvé a intentar"
          : c === "needs_reauth" ? "hay que volver a conectar Claude Code Remote en claude.ai"
          : c === "tool_error" ? "Claude Code respondió con un error: " + (e.message || "").slice(0, 200)
          : "no se pudo mandar (" + (c || e.message) + ")";
      }
    }
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
      </tbody></table></div>` : `<div class="vacio">Todavía no hay pedidos.</div>`}</section>`;
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
        case "prop-mandar": case "prop-guardar": {
          const pr = chat.propuesta; if (!pr) return;
          b.disabled = true; agregarTraza("Subiendo archivos y guardando el pedido…");
          const id = await crearPedido({ tipo: pr.tipo, texto: pr.texto, cot: pr.cot || "", files: chat.todosAdjuntos, mandar: b.dataset.p === "prop-mandar" }, agregarTraza);
          chat.propuesta = null; document.getElementById("ch-prop")?.remove();
          agregarBurbuja("a", b.dataset.p === "prop-mandar" ? `Listo: el pedido ${id} se mandó a Claude Code. Seguilo en **Pedidos**.` : `Listo: el pedido ${id} quedó pendiente en **Pedidos**.`);
          break;
        }
        case "prop-cancelar": chat.propuesta = null; document.getElementById("ch-prop")?.remove(); break;
      }
    } catch (e) { I.toast(e.message || String(e.code || e)); if (b.dataset.p.startsWith("prop")) agregarBurbuja("a", "No se pudo: " + (e.message || e.code)); }
  });

  // ------------------------------------------------------------------ chat: panel
  function armarChat() {
    const btn = document.getElementById("btn-chat"), panel = document.getElementById("chat");
    if (!btn || !panel) return;
    if (!sample) { btn.hidden = true; return; }
    btn.hidden = false;
    btn.addEventListener("click", () => abrirChat(!chat.abierto));
    panel.innerHTML = `<div class="ch-cab"><div class="fila"><b>Claude</b><span class="small muted" id="ch-ctx"></span><button class="chico" id="ch-cerrar" aria-label="Cerrar el chat">×</button></div>
        <div class="fila"><button class="chico" id="ch-nuevo">Nueva conversación</button><button class="chico" id="ch-deshacer" hidden>Deshacer cambios de Claude</button></div></div>
      <div class="ch-msgs" id="ch-msgs" aria-live="polite"></div>
      <div class="ch-pie"><div id="ch-adj" class="small"></div>
        <textarea id="ch-txt" rows="3" placeholder="Ej.: buscame una válvula esférica 2&quot; #600 · cargá la tabla del plano adjunto · ¿por qué hay tantos avisos?"></textarea>
        <div class="fila"><label class="btn chico" style="flex-direction:row" ${limites?.images ? "" : "hidden"}>Adjuntar plano o archivo<input id="ch-arch" type="file" multiple accept="image/png,image/jpeg,image/webp,application/pdf,.xlsx,.xls,.docx,.csv,.txt" hidden></label>
          <span style="flex:1"></span><button class="chico" id="ch-parar" hidden>Parar</button><button class="prim chico" id="ch-enviar">Enviar</button></div>
        <span class="small muted">Usa tu cuenta de Claude. Lo que cambie queda en borrador y se puede deshacer.</span></div>`;
    panel.querySelector("#ch-cerrar").onclick = () => abrirChat(false);
    panel.querySelector("#ch-nuevo").onclick = () => { chat.ctl?.abort(); chat.turnos = []; chat.adjuntos = []; chat.todosAdjuntos = []; chat.propuesta = null; document.getElementById("ch-msgs").innerHTML = ""; bienvenida(); pintarAdjuntos(); };
    panel.querySelector("#ch-enviar").onclick = enviar;
    panel.querySelector("#ch-parar").onclick = () => chat.ctl?.abort();
    panel.querySelector("#ch-deshacer").onclick = deshacer;
    panel.querySelector("#ch-txt").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(); } });
    window.addEventListener("hashchange", () => { pintarContexto(); });
    bienvenida();
    try { if (localStorage.getItem("itt-chat") === "1") abrirChat(true); } catch (e) { /* sin almacenamiento */ }
  }
  function abrirChat(si) {
    chat.abierto = si;
    document.getElementById("chat").hidden = !si;
    document.body.classList.toggle("con-chat", si);
    document.getElementById("btn-chat").setAttribute("aria-pressed", String(si));
    try { localStorage.setItem("itt-chat", si ? "1" : "0"); } catch (e) { /* sin almacenamiento */ }
    if (si) { pintarContexto(); document.getElementById("ch-txt").focus(); }
  }
  function pintarContexto() {
    const S = I.S, el = document.getElementById("ch-ctx"); if (!el) return;
    el.textContent = S.vista === "cot" && S.doc ? "sobre " + S.doc.cot.codigo : "sin cotización abierta";
    const d = document.getElementById("ch-deshacer");
    if (d) d.hidden = !chat.deshacer.some(x => x.id === S.id);
  }
  function bienvenida() {
    agregarBurbuja("a", "Hola. Puedo buscar en los catálogos, cargar y corregir ítems de la cotización abierta, leer un plano (imagen o PDF) y proponer la lista de materiales, o explicarte los avisos.\n\nPara trabajos largos (un pliego completo, una lista de precios para el catálogo, una cotización entera con ofertas) te propongo mandarlo a **Claude Code**.");
    if (!limites?.tools) agregarBurbuja("a", "En esta vista no puedo cambiar la cotización: solo responder.");
  }
  function md(t) {
    return esc(t).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").split("\n").map(l => /^\s*[-•] /.test(l) ? `<li>${l.replace(/^\s*[-•] /, "")}</li>` : l + "<br>").join("")
      .replace(/(<li>.*?<\/li>)+/g, m => `<ul>${m}</ul>`).replace(/(<br>)+$/, "");
  }
  function agregarBurbuja(quien, texto) {
    const box = document.getElementById("ch-msgs"), el = document.createElement("div");
    el.className = "msg " + quien; el.innerHTML = quien === "u" ? esc(texto).replace(/\n/g, "<br>") : md(texto);
    box.append(el); box.scrollTop = box.scrollHeight; return el;
  }
  function agregarTraza(t) {
    const box = document.getElementById("ch-msgs"), el = document.createElement("div");
    el.className = "traza"; el.textContent = t;
    if (chat.respEl?.isConnected) box.insertBefore(el, chat.respEl); else box.append(el); // lo que hizo va antes de la respuesta
    box.scrollTop = box.scrollHeight;
  }
  function pintarAdjuntos() {
    const el = document.getElementById("ch-adj"); if (!el) return;
    el.innerHTML = chat.adjuntos.map((f, i) => `<span class="pill info">${esc(f.name)} <button class="chico" data-quitar-adj="${i}" aria-label="Quitar">×</button></span>`).join(" ");
    el.querySelectorAll("[data-quitar-adj]").forEach(b => (b.onclick = () => { chat.adjuntos.splice(+b.dataset.quitarAdj, 1); pintarAdjuntos(); }));
  }
  function deshacer() {
    const S = I.S, i = chat.deshacer.map(x => x.id).lastIndexOf(S.id);
    if (i < 0) return;
    const [d] = chat.deshacer.splice(i, 1);
    S.doc = d.doc; I.guardarPronto(); I.render(); pintarContexto();
    agregarTraza(`Deshecho: la cotización volvió a como estaba antes del mensaje de las ${d.hora}.`);
  }

  // ------------------------------------------------------------------ chat: imágenes (PDF → páginas como imagen)
  let pdfjs = null;
  function cargarScript(src) { return new Promise((ok, no) => { const s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = () => no(new Error("No se pudo cargar " + src)); document.head.append(s); }); }
  async function paginasPdf(file, max) {
    if (!pdfjs) {
      const base = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/";
      await cargarScript(base + "pdf.min.js"); await cargarScript(base + "pdf.worker.min.js");
      pdfjs = window.pdfjsLib; pdfjs.GlobalWorkerOptions.workerSrc = base + "pdf.worker.min.js";
    }
    const doc = await pdfjs.getDocument({ data: new Uint8Array(await file.arrayBuffer()) }).promise, out = [];
    for (let n = 1; n <= Math.min(doc.numPages, max); n++) {
      const pg = await doc.getPage(n), v1 = pg.getViewport({ scale: 1 }), esc_ = Math.min(3, 2000 / Math.max(v1.width, v1.height));
      const v = pg.getViewport({ scale: esc_ }), c = document.createElement("canvas"); c.width = v.width; c.height = v.height;
      const ctx = c.getContext("2d"); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, c.width, c.height);
      await pg.render({ canvasContext: ctx, viewport: v }).promise;
      out.push(await new Promise(ok => c.toBlob(ok, "image/png")));
    }
    return { imgs: out, total: doc.numPages };
  }
  async function imagenesDe(files, notas) {
    const max = limites?.images?.maxCount || 0, imgs = [];
    for (const f of files) {
      if (imgs.length >= max) { notas.push(`${f.name}: no entra (máximo ${max} imágenes por mensaje)`); continue; }
      if (/^image\//.test(f.type)) imgs.push(f);
      else if (f.type === "application/pdf" || /\.pdf$/i.test(f.name)) {
        const r = await paginasPdf(f, max - imgs.length); imgs.push(...r.imgs);
        if (r.total > r.imgs.length) notas.push(`${f.name}: se mandan ${r.imgs.length} de ${r.total} páginas`);
      } else notas.push(`${f.name}: el chat no lo lee (solo imágenes y PDF); sí va si lo mandás a Claude Code`);
    }
    return imgs;
  }

  // ------------------------------------------------------------------ chat: instrucciones y contexto
  function reglas() {
    const fams = Object.entries(I.S.datos.familias).map(([k, v]) => `${k}=${v.n}`).join(", ");
    return `Sos el asistente del Cotizador ITT, una página para cotizar equipos de ITT S.A. (Quilmes, Argentina; fabricante de calentadores, separadores, filtros, skids, manifolds, colectores, puentes de medición, cañerías, tanques y trampas para oil & gas). Hablás con alguien de Ventas de ITT en español rioplatense. Respuestas cortas.

Reglas obligatorias (un error que llega al cliente puede ser catastrófico):
- Todo en USD y SIN IVA. Si una fuente dice "con IVA", dividí por 1,21 (o 1,105 si es 10,5%).
- Nunca inventes un precio ni lo saques de memoria. Los precios salen del catálogo (herramientas buscar_*) o de un documento que el usuario adjuntó, con proveedor y fecha. Si no hay, cargá el ítem con precio 0 (queda SIN PRECIO para pedir cotización).
- Si la pieza del catálogo no es exactamente la del plano (otra serie, material, extremos, marca, schedule), es "similar" y tenés que decir en qué difiere. "igual" solo si coincide todo.
- Un precio verbal, aproximado o calculado por vos es "est" (estimado).
- Al copiar la tabla de materiales de un plano: renglón por renglón, con la posición, la misma cantidad y la misma unidad del plano. Compras extra (sobrantes, mangas) van en filas aparte (pos "14b"). No juntes renglones.
- Si una parte del plano no se lee bien, decilo y no adivines. Pedí una imagen mejor o mandá el trabajo a Claude Code.
- La cantidad de cada ítem es por equipo; la cantidad de equipos es el parámetro N.
- Las soldaduras, la pintura, la prueba hidráulica y la radiografía se calculan con las calculadoras de la pestaña "MO y servicios": sugerí usarlas en vez de inventar horas.
- Nunca se envía nada al cliente. Todo queda en borrador para que lo revise una persona.
- Para trabajos largos o que necesitan el repositorio (leer un pliego entero, incorporar una lista de precios al catálogo, armar una cotización completa con plazo y ofertas, buscar antecedentes de proyectos) usá proponer_pedido_claude_code: el usuario lo confirma con un botón.
- Antes de cambiar varios ítems, decí en una línea qué vas a hacer y hacelo. Al final, resumí qué cambiaste.

Familias de materiales para buscar_materiales: ${fams}.
Tipos de origen de un precio: lista, cot (cotización de proveedor), stock, ant (antecedente o planilla interna), est (estimado).`;
  }
  function contexto() {
    const S = I.S, hoy = I.hoy();
    if (S.vista === "cot" && S.doc) {
      const cot = S.doc.cot, p = cot.parametros, c = I.calc();
      const filas = cot.items.map(i => { const s = i.fuentes[0]; return `${i.id} | ${i.pos} | ${i.grupo} | ${i.descripcion} | ${i.especificacion || ""} | ${i.cantidad} ${i.unidad} | USD ${s.precio} | ${s.tipo} | ${s.proveedor} ${s.fecha} | ${s.coincide}${s.diferencia ? " (" + s.diferencia + ")" : ""}`; });
      return `Hoy: ${hoy}. Cotización abierta: ${cot.codigo} ${cot.revision || ""} · ${cot.titulo || "(sin título)"} · cliente ${cot.cliente?.nombre || "—"} · estado ${cot.estado}.
Parámetros: N=${p.N} equipos, factor materiales ${p.FM}, factor MO y servicios ${p.FMO}, contingencia ${p.CONT}%, fecha de referencia ${p.fecha_referencia}.
Totales (borrador): costo por equipo USD ${c.costo.toFixed(2)}, precio unitario USD ${c.precio_unitario.toFixed(2)}, total USD ${c.total.toFixed(2)}.
Ítems (id | pos | grupo | descripción | especificación | cantidad | precio unitario | tipo | proveedor y fecha | coincide):
${filas.join("\n") || "(ninguno)"}`.slice(0, 60000);
    }
    return `Hoy: ${hoy}. No hay una cotización abierta (el usuario está en "${S.vista}"). Cotizaciones guardadas: ${S.lista.slice(0, 30).map(r => `${r.codigo} "${r.titulo}" (id ${r.id})`).join("; ") || "ninguna"}.`;
  }

  // ------------------------------------------------------------------ chat: herramientas
  function herramientas(marcar) {
    const S = I.S;
    const cot = () => { if (S.vista !== "cot" || !S.doc) throw new Error("No hay una cotización abierta. Pedile al usuario que la abra, o creá una con nueva_cotizacion."); return S.doc.cot; };
    const cambio = (txt) => { I.guardarPronto(); I.render(); pintarContexto(); agregarTraza(txt); };
    const s = (v, n = 200) => String(v ?? "").slice(0, n);
    const fechaOk = f => /^\d{4}-\d{2}-\d{2}$/.test(f) && f <= I.hoy();
    return [
      { name: "buscar_materiales", description: "Busca en el catálogo de materiales de ITT (precios sin IVA, con fecha y origen). Devuelve hasta 12 resultados con codigo, descripción, atributos, precio USD, fecha, tipo de precio, proveedor y alerta. Usá pocas palabras (ej. 'esferica 2 600').",
        inputSchema: { type: "object", properties: { texto: { type: "string" }, familia: { type: "string", description: "código de familia (VAL, BRI, CAN, ...) o vacío" } }, required: ["texto"] },
        execute: ({ texto, familia }) => {
          agregarTraza(`Busca materiales: "${s(texto, 60)}"${familia ? " en " + familia : ""}`);
          const fam = familia && S.datos.familias[String(familia).toUpperCase()] ? String(familia).toUpperCase() : "";
          const r = Busqueda.materiales(S.datos, { fam, texto: String(texto || "") }, 12);
          return { total: r.total, resultados: r.res.map(x => ({ codigo: x.r.c, familia: x.r.f, descripcion: x.r.d, atributos: x.r.a, unidad: x.r.u, precio_usd: x.r.p, fecha: x.r.fe, tipo_precio: x.r.tp, proveedor: s(x.r.pr, 60), alerta: s(x.r.al, 120), precios_en_historial: x.r.n })) };
        } },
      { name: "buscar_servicios", description: "Busca en el catálogo de mano de obra y servicios (sin IVA). Devuelve hasta 12 con codigo, rubro, servicio, tarifa unitaria (si hay) o precio global, fecha, proveedor, incluye y equipo de referencia. Un global solo sirve si el alcance es el mismo.",
        inputSchema: { type: "object", properties: { texto: { type: "string" }, rubro: { type: "string" } }, required: ["texto"] },
        execute: ({ texto, rubro }) => {
          agregarTraza(`Busca servicios: "${s(texto, 60)}"`);
          const r = Busqueda.servicios(S.datos, { texto: String(texto || ""), hoja: rubro ? String(rubro) : "" }, 12);
          return { total: r.total, resultados: r.res.map(x => ({ codigo: x.c, rubro: x.h, servicio: x.s, tarifa: x.t, unidad_tarifa: x.ut, precio_global: x.p, fecha: x.fe, proveedor: s(x.pr, 60), incluye: s(x.inc, 150), equipo_referencia: s(x.eq, 80), alerta: s(x.al, 100) })) };
        } },
      { name: "ver_avisos", description: "Devuelve los avisos de control de la cotización abierta (para corregir y para revisar).",
        execute: () => { cot(); return Busqueda.avisos(S.doc.cot).slice(0, 60); } },
      { name: "agregar_material", description: "Agrega a la cotización abierta un material del catálogo por su codigo, con su precio, proveedor y fecha. cantidad = por equipo. coincide: igual o similar (si es similar, diferencia es obligatoria). plano: los datos del renglón del plano.",
        inputSchema: { type: "object", properties: { codigo: { type: "string" }, cantidad: { type: "number" }, pos: { type: "string" }, coincide: { type: "string", enum: ["igual", "similar"] }, diferencia: { type: "string" },
          plano: { type: "object", properties: { diametro: { type: "string" }, serie_sch: { type: "string" }, material: { type: "string" }, extremos: { type: "string" }, modelo: { type: "string" } } } }, required: ["codigo", "cantidad", "coincide"] },
        execute: ({ codigo, cantidad, pos, coincide, diferencia, plano }) => {
          const c = cot(), r = S.datos.materiales.find(m => m.c === String(codigo));
          if (!r) throw new Error("No existe el código " + codigo);
          if (coincide === "similar" && !diferencia) throw new Error("Si es similar, decí en qué difiere (diferencia).");
          marcar();
          const it = Busqueda.itemDeMaterial(r, { estado: coincide === "igual" ? "igual" : "similar", difs: diferencia ? [String(diferencia)] : [] }, Number(cantidad) || 1, I.siguienteId("M"));
          it.pos = pos ? String(pos) : String(c.items.filter(i => i.grupo === "material").length + 1);
          it.plano = plano && typeof plano === "object" ? Object.fromEntries(Object.entries(plano).map(([k, v]) => [k, s(v, 80)])) : {};
          c.items.push(it); cambio(`Agregó ${it.id}: ${it.descripcion.slice(0, 60)} × ${it.cantidad}`);
          return { id: it.id, precio: it.fuentes[0].precio, coincide: it.fuentes[0].coincide };
        } },
      { name: "agregar_servicio", description: "Agrega a la cotización abierta un servicio o mano de obra del catálogo por su codigo. cantidad en la unidad de la tarifa (o 1 si es global).",
        inputSchema: { type: "object", properties: { codigo: { type: "string" }, cantidad: { type: "number" } }, required: ["codigo", "cantidad"] },
        execute: ({ codigo, cantidad }) => {
          const c = cot(), r = S.datos.servicios.find(x => x.c === String(codigo));
          if (!r) throw new Error("No existe el código " + codigo);
          if (!r.p) throw new Error("Ese servicio no tiene precio confiable.");
          marcar(); const it = Busqueda.itemDeServicio(r, Number(cantidad) || 1, I.siguienteId("S")); c.items.push(it);
          cambio(`Agregó ${it.id}: ${it.descripcion.slice(0, 60)}`); return { id: it.id };
        } },
      { name: "cargar_item", description: "Carga un ítem a mano en la cotización abierta (por ejemplo, un renglón del plano sin precio en el catálogo, o un precio de un documento adjunto). precio 0 = SIN PRECIO (pedir cotización). fecha AAAA-MM-DD del precio.",
        inputSchema: { type: "object", properties: { grupo: { type: "string", enum: ["material", "mo", "servicio"] }, pos: { type: "string" }, descripcion: { type: "string" }, especificacion: { type: "string" },
          cantidad: { type: "number" }, unidad: { type: "string" }, precio: { type: "number" }, tipo: { type: "string", enum: ["lista", "cot", "stock", "ant", "est"] }, proveedor: { type: "string" }, origen: { type: "string" }, fecha: { type: "string" },
          coincide: { type: "string", enum: ["igual", "similar", "sin_ref"] }, diferencia: { type: "string" },
          plano: { type: "object", properties: { diametro: { type: "string" }, serie_sch: { type: "string" }, material: { type: "string" }, extremos: { type: "string" }, modelo: { type: "string" } } } },
          required: ["grupo", "descripcion", "cantidad", "unidad", "precio"] },
        execute: (a) => {
          const c = cot(), precio = Number(a.precio) || 0;
          const f = precio ? { tipo: a.tipo || "est", precio, proveedor: s(a.proveedor, 120), origen: s(a.origen, 240), fecha: s(a.fecha, 10), coincide: a.coincide || "similar", diferencia: s(a.diferencia, 300) }
            : { tipo: "est", precio: 0, proveedor: "SIN PRECIO: pedir cotización", origen: s(a.origen, 240), fecha: I.hoy(), coincide: "sin_ref", diferencia: "Sin precio en el catálogo" };
          if (precio && !f.proveedor) throw new Error("Falta el proveedor o criterio del precio.");
          if (precio && !fechaOk(f.fecha)) throw new Error("La fecha del precio no es válida (AAAA-MM-DD, no futura).");
          if (f.coincide === "similar" && !f.diferencia) throw new Error("Si es similar, decí en qué difiere.");
          if (!f.diferencia) delete f.diferencia;
          marcar();
          const grupo = ["material", "mo", "servicio"].includes(a.grupo) ? a.grupo : "material";
          const it = { id: I.siguienteId(grupo === "material" ? "M" : "S"), pos: s(a.pos, 12) || (grupo === "material" ? String(c.items.filter(i => i.grupo === "material").length + 1) : "SRV"), grupo,
            descripcion: s(a.descripcion, 120), especificacion: s(a.especificacion, 300), cantidad: Number(a.cantidad) || 1, unidad: s(a.unidad, 12) || "un", fuentes: [f],
            plano: a.plano && typeof a.plano === "object" ? Object.fromEntries(Object.entries(a.plano).map(([k, v]) => [k, s(v, 80)])) : {} };
          c.items.push(it); cambio(`Cargó ${it.id}: ${it.descripcion.slice(0, 60)}${precio ? "" : " (SIN PRECIO)"}`); return { id: it.id };
        } },
      { name: "modificar_item", description: "Cambia campos de un ítem de la cotización abierta por su id: cantidad, unidad, pos, descripcion, especificacion, precio (sin IVA; si cambiás el precio, pasá también proveedor, fecha y tipo).",
        inputSchema: { type: "object", properties: { id: { type: "string" }, cantidad: { type: "number" }, unidad: { type: "string" }, pos: { type: "string" }, descripcion: { type: "string" }, especificacion: { type: "string" },
          precio: { type: "number" }, proveedor: { type: "string" }, fecha: { type: "string" }, tipo: { type: "string", enum: ["lista", "cot", "stock", "ant", "est"] }, coincide: { type: "string", enum: ["igual", "similar", "sin_ref"] }, diferencia: { type: "string" } }, required: ["id"] },
        execute: (a) => {
          const c = cot(), it = c.items.find(i => i.id === String(a.id)); if (!it) throw new Error("No existe el ítem " + a.id);
          if (a.precio !== undefined && (!a.proveedor || !fechaOk(String(a.fecha || "")))) throw new Error("Para cambiar el precio hacen falta proveedor y fecha válida.");
          marcar(); const f = it.fuentes[0];
          for (const k of ["unidad", "pos", "descripcion", "especificacion"]) if (a[k] !== undefined) it[k] = s(a[k], 300);
          if (a.cantidad !== undefined) it.cantidad = Number(a.cantidad) || 0;
          if (a.precio !== undefined) Object.assign(f, { precio: Number(a.precio) || 0, proveedor: s(a.proveedor, 120), fecha: s(a.fecha, 10), tipo: a.tipo || f.tipo });
          if (a.coincide) f.coincide = a.coincide;
          if (a.diferencia !== undefined) f.diferencia = s(a.diferencia, 300);
          if (f.coincide === "similar" && !f.diferencia) throw new Error("Quedó similar sin diferencia: pasá diferencia.");
          cambio(`Modificó ${it.id}: ${it.descripcion.slice(0, 60)}`); return "ok";
        } },
      { name: "quitar_item", description: "Quita un ítem de la cotización abierta por su id.",
        inputSchema: { type: "object", properties: { id: { type: "string" } }, required: ["id"] },
        execute: ({ id }) => {
          const c = cot(), it = c.items.find(i => i.id === String(id)); if (!it) throw new Error("No existe el ítem " + id);
          marcar(); c.items = c.items.filter(i => i !== it); cambio(`Quitó ${it.id}: ${it.descripcion.slice(0, 60)}`); return "ok";
        } },
      { name: "nueva_cotizacion", description: "Crea una cotización nueva vacía en borrador y la abre. Usala solo si el usuario quiere empezar una cotización y no hay ninguna abierta.",
        inputSchema: { type: "object", properties: { titulo: { type: "string" }, cliente: { type: "string" } }, required: ["titulo"] },
        execute: async ({ titulo, cliente }) => {
          const id = await I.crearCotizacion({ titulo: s(titulo, 120), cliente: s(cliente, 80) });
          S.tab = "materiales"; location.hash = "c-" + id;
          for (let i = 0; i < 50 && !(S.id === id && S.doc); i++) await new Promise(r => setTimeout(r, 100));
          agregarTraza(`Creó la cotización "${s(titulo, 60)}"`); pintarContexto(); return { id, abierta: S.id === id && !!S.doc };
        } },
      { name: "proponer_pedido_claude_code", description: "Propone mandar un trabajo a Claude Code (trabaja sobre el repositorio de ITT con el procedimiento completo y deja el resultado en la página). Muestra un botón para que el usuario confirme; los archivos adjuntos en esta conversación van con el pedido. tipo: cotizacion_nueva, actualizar_cotizacion, lista_precios u otro.",
        inputSchema: { type: "object", properties: { tipo: { type: "string", enum: Object.keys(TIPOS_PEDIDO) }, texto: { type: "string", description: "el pedido completo y claro para Claude Code" } }, required: ["tipo", "texto"] },
        execute: ({ tipo, texto }) => {
          chat.propuesta = { tipo: TIPOS_PEDIDO[tipo] ? tipo : "otro", texto: s(texto, 3000), cot: S.vista === "cot" ? S.id : "" };
          mostrarPropuesta(); return "Propuesta mostrada. El usuario tiene que confirmarla con el botón; no la des por enviada.";
        } },
    ];
  }
  function mostrarPropuesta() {
    const pr = chat.propuesta, box = document.getElementById("ch-msgs");
    document.getElementById("ch-prop")?.remove();
    const el = document.createElement("div"); el.className = "msg a prop"; el.id = "ch-prop";
    el.innerHTML = `<b>Pedido para Claude Code</b><div class="small">${esc(TIPOS_PEDIDO[pr.tipo])}${pr.cot ? " · sobre " + esc(I.S.doc?.cot.codigo || pr.cot) : ""}</div>
      <div class="small" style="white-space:pre-wrap">${esc(pr.texto)}</div>
      <div class="small muted">${chat.todosAdjuntos.length ? "Archivos: " + chat.todosAdjuntos.map(f => esc(f.name)).join(", ") : "Sin archivos adjuntos"}</div>
      <div class="fila"><button class="prim chico" data-p="prop-mandar" ${mcp ? "" : "disabled"}>Mandar a Claude Code</button><button class="chico" data-p="prop-guardar">Dejar pendiente</button><button class="chico" data-p="prop-cancelar">Cancelar</button></div>`;
    box.append(el); box.scrollTop = box.scrollHeight;
  }

  // ------------------------------------------------------------------ chat: enviar
  const ERRORES = {
    not_granted: "No diste permiso a la página para usar Claude. Se puede habilitar desde el menú de permisos de la página.",
    sampling_disabled: "Claude no está disponible para esta cuenta.", rate_limited: "Llegaste al límite de uso por ahora. Probá en un rato.",
    session_expired: "Tenés que volver a iniciar sesión en Claude.", image_rejected: "Alguna imagen no se pudo usar (formato o tamaño). Probá con otra.",
    images_unavailable: "En esta vista no se pueden mandar imágenes.", prompt_too_large: "El mensaje es muy largo. Empezá una conversación nueva o mandá menos a la vez.",
    refused: "Claude no respondió a este pedido. Probá formularlo de otra manera.", empty_completion: "No hubo respuesta. Probá de nuevo con un pedido más simple.",
  };
  async function enviar() {
    if (chat.ocupado) return;
    const ta = document.getElementById("ch-txt"), texto = ta.value.trim(), files = chat.adjuntos.slice();
    if (!texto && !files.length) return;
    chat.ocupado = true; ta.value = ""; chat.adjuntos = []; pintarAdjuntos();
    document.getElementById("ch-enviar").disabled = true; document.getElementById("ch-parar").hidden = false;
    chat.todosAdjuntos.push(...files);
    const contenido = texto + (files.length ? `\n\n[Adjuntó: ${files.map(f => f.name).join(", ")}]` : "");
    agregarBurbuja("u", contenido);
    const resp = agregarBurbuja("a", "Pensando…"); resp.classList.add("pensando"); chat.respEl = resp;
    const notas = []; let imgs = [];
    try {
      if (files.length) {
        if (!limites?.images) notas.push("en esta vista no se pueden mandar imágenes al chat");
        else imgs = await imagenesDe(files, notas);
        notas.forEach(n => agregarTraza(n));
      }
      let marcado = false;
      const marcar = () => { if (!marcado && I.S.doc) { chat.deshacer.push({ id: I.S.id, doc: I.clon(I.S.doc), hora: new Date().toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" }) }); marcado = true; } };
      const previos = chat.turnos.slice(-20);
      const ultimo = `${contexto()}\n\n${imgs.length ? `Van ${imgs.length} imagen(es) adjuntas (páginas de: ${files.map(f => f.name).join(", ")}).\n\n` : ""}Mensaje del usuario:\n${contenido}`;
      const input = [{ role: "user", content: reglas() }, ...previos, { role: "user", content: ultimo }];
      chat.turnos.push({ role: "user", content: contenido });
      chat.ctl = new AbortController();
      const ops = { signal: chat.ctl.signal, cache: false, modelTier: imgs.length ? "complex" : "default",
        onText: ({ text }) => { resp.classList.remove("pensando"); resp.innerHTML = md(text); document.getElementById("ch-msgs").scrollTop = 1e9; } };
      if (imgs.length) ops.images = imgs;
      if (limites?.tools) { ops.tools = herramientas(marcar).slice(0, limites.tools.maxCount || 20); delete ops.cache; }
      const r = await sample(input, ops);
      resp.classList.remove("pensando"); resp.innerHTML = md(r.text) + (r.truncated ? '<div class="small muted">(respuesta cortada: pedí menos a la vez)</div>' : "");
      chat.turnos.push({ role: "assistant", content: r.text });
    } catch (e) {
      resp.classList.remove("pensando");
      if (e.code === "cancelled") resp.innerHTML = e.text ? md(e.text) + '<div class="small muted">(detenido)</div>' : '<span class="muted">Detenido.</span>';
      else resp.innerHTML = (e.text ? md(e.text) + "<br>" : "") + `<span class="err">${esc(ERRORES[e.code] || "Hubo un problema de conexión con Claude. Probá de nuevo.")}</span>`;
      if (e.text) chat.turnos.push({ role: "assistant", content: e.text });
    } finally {
      chat.ocupado = false; chat.ctl = null; chat.respEl = null;
      document.getElementById("ch-enviar").disabled = false; document.getElementById("ch-parar").hidden = true; pintarContexto();
    }
  }

  return { renderPedidos, abrirChat, TIPOS_PEDIDO, prepararArchivo };
})();
if (typeof module !== "undefined") module.exports = Asistente;
