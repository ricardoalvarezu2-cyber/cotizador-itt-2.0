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

  return { abrirClaude, TIPOS_PEDIDO, prepararArchivo, crearPedido };
})();
if (typeof module !== "undefined") module.exports = Asistente;
