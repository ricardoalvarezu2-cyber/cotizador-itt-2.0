"""Arma el documento config/indices de la base de la página (dólar BNA e índices de ajuste al día), para que la página
use los valores nuevos sin volver a publicarla. Lo corre la tarea semanal después de herramientas/actualizar_base.py,
y Claude lo sube con ArtifactData (set en la colección "config", documento "indices", con file_path).

Uso: python web/indices_para_pagina.py <archivo_salida.json>
"""
import json
import sys
from datetime import date

from construir_datos import dolar, indices

doc = {"generado": date.today().isoformat(), "indices": indices(), "dolar": dolar()}
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False))
print(f"{sys.argv[1]}: {len(doc['indices'])} meses de índices, último {doc['indices'][-1]['mes']} (dólar {doc['indices'][-1]['dolar']})")
