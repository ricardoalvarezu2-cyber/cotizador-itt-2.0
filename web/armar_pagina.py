"""Arma web/cotizador.html: pagina.html con motor.js, busqueda.js, rubros.js, documentos.js, app.js y asistente.js incrustados en <!--SCRIPTS-->.
La página se publica como Artifact junto con web/datos.json (python web/construir_datos.py).

Uso: python web/armar_pagina.py
"""
from pathlib import Path

W = Path(__file__).resolve().parent
html = (W / "src" / "pagina.html").read_text(encoding="utf-8")
js = "\n".join((W / "src" / n).read_text(encoding="utf-8") for n in ("motor.js", "busqueda.js", "ficha.js", "rubros.js", "antecedentes.js", "documentos.js", "app.js", "asistente.js"))
assert "<!--SCRIPTS-->" in html and "</script>" not in js
(W / "cotizador.html").write_text(html.replace("<!--SCRIPTS-->", "<script>\n" + js + "\n</script>"), encoding="utf-8")
print(f"web/cotizador.html: {(W / 'cotizador.html').stat().st_size / 1e3:.0f} kB")
