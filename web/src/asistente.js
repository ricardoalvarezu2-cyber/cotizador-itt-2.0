// Asistente de la página: pedidos para Claude Code (capacidad "mcp", conector Claude Code Remote → send_message a la sesión
// fija con el repositorio) y botón Claude, que abre esa sesión en una ventana aparte. Los archivos se suben con "assets"; Excel y Word
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
        case "nuevo-borrar":
          if (b.dataset.ok !== "1") { b.dataset.ok = "1"; b.textContent = "¿Seguro?"; setTimeout(() => { b.dataset.ok = ""; b.textContent = "Borrar"; }, 4000); return; }
          await S.db.doc("catalogo_nuevo/" + b.dataset.id).delete(); I.toast("Borrado del catálogo nuevo"); break;
      }
    } catch (e) { I.toast(e.message || String(e.code || e)); }
  });

  // ------------------------------------------------------------------ botón Claude: abre la sesión de Claude Code
  // La sesión fija (la misma que recibe los pedidos, con el repositorio) se abre en una ventana chica aparte, como un
  // chat flotante. claude.ai no se puede mostrar dentro de la página.
  function armarChat() {
    const btn = document.getElementById("btn-chat");
    if (!btn) return;
    btn.hidden = false; btn.title = "Abre Claude Code (sesión con el repositorio) en una ventana aparte";
    btn.addEventListener("click", abrirClaude);
  }
  function abrirClaude() {
    const url = "https://claude.ai/code/" + sesion, an = 480, al = Math.min(820, screen.availHeight - 80);
    const izq = (screen.availLeft || 0) + screen.availWidth - an - 24, arr = (screen.availTop || 0) + 40;
    const w = window.open(url, "claude-code-itt", `popup=yes,width=${an},height=${al},left=${izq},top=${arr}`);
    if (w) { try { w.focus(); } catch (e) { /* otra ventana */ } return; }
    const a = document.createElement("a"); a.href = url; a.target = "_blank"; a.rel = "noopener"; document.body.append(a); a.click(); a.remove();
  }

  return { renderPedidos, abrirClaude, TIPOS_PEDIDO, prepararArchivo, crearPedido };
})();
if (typeof module !== "undefined") module.exports = Asistente;
