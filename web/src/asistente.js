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
  const MAX_MB = 20;

  let I = null, mcp = null, sesion = SESION_FIJA;
  const P = { nuevos: [] };
  
  // ------------------------------------------------------------------ arranque
  const listo = window.ITT ? Promise.resolve() : new Promise(ok => window.addEventListener("itt-listo", ok, { once: true }));
  listo.then(async () => {
    I = window.ITT;
    const usar = n => (window.claude && window.claude.use ? window.claude.use(n).catch(() => null) : Promise.resolve(null));
    mcp = await usar("mcp");
    const S = I.S;
    if (S.db) {
      S.db.doc("config/claude_code").get().then(d => { if (d.exists && d.data().session_id) sesion = d.data().session_id; }).catch(() => {});
    }
    if (S.db) S.db.collection("catalogo_nuevo").onSnapshot(sn => { P.nuevos = sn.docs.map(d => ({ id: d.id, ...d.data() })); mezclarNuevos(); }, () => {});
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

  // ------------------------------------------------------------------ botones Claude y Chat nuevo
  // "Claude ↗" abre la sesión fija (la de la tarea semanal y los pedidos, con el repositorio) en una ventana chica aparte,
  // como un chat flotante; claude.ai no se puede mostrar dentro de la página. "Chat nuevo" crea una sesión limpia con el
  // repositorio (create_session) y la abre en la misma ventana. Las sesiones que crea la página quedan en la colección
  // "chats" y se archivan solas tras unos días sin uso (config/claude_code.dias_chat, por defecto 3); se pueden recuperar.
  const ENTORNO = "env_01XxXedU9fMy5bmisDSk6jJm", REPO = "https://github.com/tvmaty2186/cotizador-itt", ETIQUETA = "cotizador-itt-chat";
  let diasChat = 3;
  function armarChat() {
    const btn = document.getElementById("btn-chat"), nuevo = document.getElementById("btn-chat-nuevo");
    if (btn) { btn.hidden = false; btn.title = "Abre Claude Code (la sesión de siempre, con el repositorio) en una ventana aparte"; btn.addEventListener("click", abrirClaude); }
    if (nuevo && mcp) { nuevo.hidden = false; nuevo.title = "Abre una sesión nueva de Claude Code con el repositorio"; nuevo.addEventListener("click", chatNuevo); }
    I.S.db?.doc("config/claude_code").get().then(d => { if (d.exists && +d.data().dias_chat > 0) diasChat = +d.data().dias_chat; }).catch(() => {});
  }
  function ventana(url) {
    const an = 480, al = Math.min(820, screen.availHeight - 80);
    const izq = (screen.availLeft || 0) + screen.availWidth - an - 24, arr = (screen.availTop || 0) + 40;
    return window.open(url, "claude-code-itt", `popup=yes,width=${an},height=${al},left=${izq},top=${arr}`);
  }
  function irA(w, url) {
    if (w && !w.closed) { try { w.location.href = url; w.focus(); return; } catch (e) { /* otra ventana */ } }
    const a = document.createElement("a"); a.href = url; a.target = "_blank"; a.rel = "noopener"; document.body.append(a); a.click(); a.remove();
  }
  function abrirClaude() {
    const url = "https://claude.ai/code/" + sesion, w = ventana(url);
    if (w) { try { w.focus(); } catch (e) { /* otra ventana */ } } else irA(null, url);
    limpiarChats().catch(() => {});
  }
  const datoDe = r => { const p = r && (r.payload ?? r); return (p && p.ccr) || p || {}; };
  async function chatNuevo(ev) {
    const b = ev.currentTarget, w = ventana("about:blank"); // la ventana se abre ya, con el clic; después se le pone la sesión
    b.disabled = true; I.toast("Creando un chat nuevo con el repositorio…");
    try {
      const f = Documentos.fechaHora(ahora());
      const r = await mcp.callTool(SERVIDOR, "create_session", { environment_id: ENTORNO, source_url: REPO, title: "Cotizador ITT - chat " + f, tags: [ETIQUETA], permission_mode: "auto" });
      const id = datoDe(r).id || (JSON.stringify(r).match(/session_[A-Za-z0-9]+/) || [])[0];
      if (!id) throw new Error("Claude Code no devolvió la sesión nueva");
      irA(w, "https://claude.ai/code/" + id);
      await I.S.db?.doc("chats/" + id).set({ creado: ahora(), titulo: "Cotizador ITT - chat " + f });
      limpiarChats(id).catch(() => {});
    } catch (e) {
      const [, nota] = motivoError(e);
      I.toast("No se pudo crear el chat nuevo: " + nota + ". Se abre Claude Code para empezarlo a mano.");
      irA(w, "https://claude.ai/code");
    } finally { b.disabled = false; }
  }
  // Limpieza en dos pasos de las sesiones creadas por la página (la sesión fija nunca): 1) con más de diasChat días sin
  // uso se le pide que consolide lo aprendido en el repositorio (web/LEEME.md, "Consolidar antes de archivar"), y la
  // sesión marca chats/<id>.consolidado; 2) recién con eso, y sin estar trabajando, se archiva. Sin consolidar no se archiva.
  async function limpiarChats(menos) {
    const db = I.S.db; if (!db || !mcp) return;
    const sn = await db.collection("chats").get(), limite = Date.now() - diasChat * 864e5;
    for (const d of sn.docs) {
      const c = d.data(); if (d.id === menos || d.id === sesion || c.archivado) continue;
      if (!c.consolidado && Date.parse(c.creado) > limite) continue;
      try {
        const x = datoDe(await mcp.callTool(SERVIDOR, "get_session", { session_id: d.id }));
        if (/RUNNING/.test(x.session_status || "")) continue;
        if (c.consolidado) {
          await mcp.callTool(SERVIDOR, "archive_session", { session_id: d.id });
          await db.doc("chats/" + d.id).update({ archivado: ahora() });
        } else if (!c.consolidar_pedido && Date.parse(x.updated_at || c.creado) <= limite) {
          await mcp.callTool(SERVIDOR, "send_message", { session_id: d.id, priority: "later", message:
            `Consolidación antes de archivar esta sesión (pedido automático de la página del cotizador, ${URL_PAGINA}).\n` +
            `Seguí web/LEEME.md, sección "Consolidar antes de archivar": git pull origin main; anotá en conocimiento/ lo aprendido en esta sesión ` +
            `(estado_y_pendientes.md, errores_y_lecciones.md y lo que corresponda), verificar_todo, commit y pasar a main. ` +
            `Al terminar, ArtifactData update de chats/${d.id} con consolidado = fecha y hora y resumen = una línea. Si no hubo nada nuevo, marcalo igual.` });
          await db.doc("chats/" + d.id).update({ consolidar_pedido: ahora() });
        }
      } catch (e) { if (/not.?found|archiv/i.test(e.message || "")) await db.doc("chats/" + d.id).update({ archivado: ahora() }).catch(() => {}); }
    }
  }


  return { abrirClaude, chatNuevo, TIPOS_PEDIDO, prepararArchivo, crearPedido };
})();
if (typeof module !== "undefined") module.exports = Asistente;
