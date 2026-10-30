"""Pendientes de la oferta (antes "frenos"; proceso unificado, Matías, 30-10-2026).

CAMBIO (Matías, 30-10-2026, tarde): ya no frenan. Son avisos de lo que conviene revisar antes de enviar al cliente: las
ofertas se generan igual (en borrador) y la aprobación la hace el usuario desde la página sin restricción. El texto de
abajo describe cada control; donde dice "frena" o "impide", leer "avisa".

Uso: python herramientas/frenos.py cotizaciones/<carpeta>          lista los frenos de una cotización
     python herramientas/frenos.py --comparar A.json B.json          compara dos lecturas del documento del cliente

Un freno no impide armar el cómputo, la planilla ni el informe (siguen saliendo como borrador): impide generar las ofertas
técnica y económica, que son lo que llega al cliente. No es un candado de estados (Matías no los quiso): cada freno se
levanta corrigiendo el dato o escribiendo la justificación que pide, y la justificación queda en cotizacion.json.

Frenos:
  transcripcion   falta pedido/transcripcion.json (copia literal del documento del cliente), salvo que la lista sea un
                  diseño de ITT declarado en cotizacion.json → "origen_lista": {"tipo": "diseno_itt", "motivo": "..."}
  doble_lectura   falta pedido/transcripcion_b.json (segunda lectura hecha por otro, sin ver la primera), o las dos
                  lecturas difieren en alguna celda sin resolver (se resuelve en transcripcion.json → "diferencias_resueltas")
  requisitos      falta pedido/requisitos.csv o algún requisito no tiene destino válido (cumple, renglon, desvio,
                  exclusion) o sigue en "consulta" sin respuesta o en "pendiente_itt" (algo que hace ITT: memoria, esquema); renglon = posición o rubro del cómputo; desvío y exclusión
                  = fragmento literal de oferta.json
  estimado        lo estimado pesa más del 15% del costo directo → justificaciones.estimado
  antecedentes    no hay antecedente con costo comparable, o el costo difiere más del 15% del más parecido →
                  justificaciones.antecedentes (explicación rubro por rubro)
  vencidas        cotización de proveedor (tipo "cot") vencida: validez_hasta anterior a hoy o, sin validez escrita, de
                  más de 30 días; lista de precios (tipo "lista") de más de 180 días; fuente sin fecha o con fecha futura; se levanta con "reconfirmado": "AAAA-MM-DD" (de los últimos 30 días) en la fuente o con
                  justificaciones.vencidas
  plazo           plazo ofrecido menor que el calculado sin plazo.justificacion (plazo.py)
  computo         verificar_computo.py da errores (también si generar_oferta.py se corre sola)
  sin_precio      renglón en 0 sin sin_precio_motivo en el ítem, o con un motivo que solo dice que falta el precio
                  ("pedir cotización", "a Compras"); valen "lo provee el cliente", "incluido en el renglón X"
  pendientes_oferta  oferta.json con datos entre [corchetes] sin completar
Las justificaciones tienen que tener al menos 20 letras. Las dos lecturas llevan "lector" (distinto en A y B).
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import a_vista, fmt  # noqa: E402

DESTINOS = ("cumple", "renglon", "desvio", "exclusion", "consulta", "pendiente_itt")
COLUMNAS_REQUISITOS = ("id", "documento", "pagina", "texto", "tema", "destino", "referencia")
LIMITE_ESTIMADO = 0.15
LIMITE_ANTECEDENTE = 0.15
DIAS_LISTA = 180  # una lista de precios de más de 6 meses se actualiza (P4)
DIAS_VALIDEZ = 30  # sin validez escrita en la cotización del proveedor se toma 30 días (criterio de ITT, no un dato)


def _norm(t):
    return " ".join(str(t if t is not None else "").split())


def _celda(t):
    """Valor de una celda para comparar lecturas: una celda de relleno hecha solo de guiones ("----", "-----------") vale lo
    mismo con cualquier cantidad de guiones (no es un dato y el largo no se puede leer con certeza). "_" no es relleno: es
    "el cliente no indica cantidad" y se compara tal cual."""
    t = _norm(t)
    return "--" if re.fullmatch(r"-{2,}", t) else t


def _clave_col(t):
    return re.sub(r"[^A-Z0-9]", "", _norm(t).upper().translate(str.maketrans("ÁÉÍÓÚÜÑ", "AEIOUUN")))


def comparar_lecturas(a, b):
    """Diferencias celda por celda entre dos lecturas: [(tabla, pos, columna, valor_a, valor_b)].
    Las tablas se emparejan por título y las filas por la primera columna (posición). Se ignoran solo los espacios de más
    (la lectura de espacios en un plano no es confiable); mayúsculas, acentos y signos cuentan."""
    out = []
    tb = {_clave_col(t["titulo"]): t for t in b["tablas"]}
    for ta in a["tablas"]:
        t = tb.pop(_clave_col(ta["titulo"]), None)
        if t is None:
            out.append((ta["titulo"], "", "", "tabla presente", "tabla ausente"))
            continue
        cols_b = {_clave_col(c): i for i, c in enumerate(t["columnas"])}
        filas_b = {_norm(f[0]): f for f in t["filas"]}
        for f in ta["filas"]:
            pos = _norm(f[0])
            fb = filas_b.pop(pos, None)
            if fb is None:
                out.append((ta["titulo"], pos, "", "fila presente", "fila ausente"))
                continue
            for i, col in enumerate(ta["columnas"]):
                j = cols_b.get(_clave_col(col))
                va = _celda(f[i]) if i < len(f) else ""
                if j is None:
                    if va:
                        out.append((ta["titulo"], pos, col, va, "columna ausente"))
                    continue
                vb = _celda(fb[j]) if j < len(fb) else ""
                if va != vb:
                    out.append((ta["titulo"], pos, col, va, vb))
        cols_a = {_clave_col(c) for c in ta["columnas"]}
        for col in t["columnas"]:  # columnas que solo leyó B (auditoría 30-10-2026)
            if _clave_col(col) not in cols_a:
                j = t["columnas"].index(col)
                for fb in t["filas"]:
                    if _norm(fb[0]) not in filas_b and j < len(fb) and _celda(fb[j]):
                        out.append((ta["titulo"], _norm(fb[0]), col, "columna ausente", _celda(fb[j])))
        for pos in filas_b:
            out.append((ta["titulo"], pos, "", "fila ausente", "fila presente"))
    for t in tb.values():
        out.append((t["titulo"], "", "", "tabla ausente", "tabla presente"))
    return out


def _resuelta(dif, resueltas):
    tabla, pos, col, va, _ = dif
    for r in resueltas:
        if (_clave_col(r.get("tabla")) == _clave_col(tabla) and _norm(r.get("pos")) == pos
                and _clave_col(r.get("columna")) == _clave_col(col) and _norm(r.get("vale")) == va and _norm(r.get("motivo"))):
            return True
    return False


def frenos_transcripcion(carpeta, cfg):
    ped = carpeta / "pedido"
    ra, rb = ped / "transcripcion.json", ped / "transcripcion_b.json"
    origen = cfg.get("origen_lista") or {}
    if not ra.exists():
        if origen.get("tipo") == "diseno_itt" and _norm(origen.get("motivo")):
            return []
        return [("transcripcion", "falta pedido/transcripcion.json: la lista de materiales tiene que salir de la copia literal del "
                 "documento del cliente (plano, planilla o pliego). Si no hay tabla del cliente porque la lista es un diseño de ITT, "
                 "declararlo en cotizacion.json → origen_lista {tipo: diseno_itt, motivo}")]
    if not rb.exists():
        return [("doble_lectura", "falta pedido/transcripcion_b.json: segunda lectura del documento hecha por otro agente o persona, "
                 "sin ver la primera")]
    a, b = (json.load(open(r, encoding="utf-8")) for r in (ra, rb))
    la, lb = _norm(a.get("lector")), _norm(b.get("lector"))
    if not la or not lb or la == lb:
        return [("doble_lectura", f"las dos lecturas tienen que decir quién las hizo y ser de lectores distintos (lector A «{la}», "
                 f"B «{lb}»)")]
    if a["tablas"] == b["tablas"]:
        print("  ! las dos lecturas son idénticas celda por celda: confirmar que B se hizo sin ver A")
    difs = [d for d in comparar_lecturas(a, b) if not _resuelta(d, a.get("diferencias_resueltas") or [])]
    if not difs:
        return []
    ej = "; ".join(f"{d[0][:20]} pos {d[1]} {d[2]}: A «{d[3]}» / B «{d[4]}»" for d in difs[:4])
    return [("doble_lectura", f"las dos lecturas del documento del cliente difieren en {len(difs)} celda(s) sin resolver ({ej}"
             + ("…" if len(difs) > 4 else "") + "). Mirar el original, dejar el valor correcto en transcripcion.json y anotarlo en "
             "diferencias_resueltas [{tabla, pos, columna, vale, motivo}]")]


def _textos(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _textos(v)
    elif isinstance(x, list):
        for v in x:
            yield from _textos(v)


def frenos_requisitos(carpeta, plano_pos):
    ruta = carpeta / "pedido" / "requisitos.csv"
    if not ruta.exists():
        return [("requisitos", "falta pedido/requisitos.csv: cada requisito del pedido (pliego, ET, notas del plano, condiciones "
                 "comerciales) con su destino: cumple, renglon, desvio, exclusion o consulta")]
    filas = list(csv.DictReader(open(ruta, encoding="utf-8")))
    faltan_cols = [c for c in COLUMNAS_REQUISITOS if filas and c not in filas[0]]
    if not filas or faltan_cols:
        return [("requisitos", "pedido/requisitos.csv vacío o sin las columnas " + ", ".join(faltan_cols or COLUMNAS_REQUISITOS))]
    ro = carpeta / "oferta.json"
    textos_oferta = _clave_col(" | ".join(_textos(json.load(open(ro, encoding="utf-8"))))) if ro.exists() else ""
    malos = []
    for r in filas:
        d, ref = _norm(r["destino"]).lower(), _norm(r["referencia"])
        if d not in DESTINOS:
            malos.append(f"{r['id']}: destino «{r['destino']}» no válido")
        elif d == "consulta":
            malos.append(f"{r['id']}: consulta al cliente sin respuesta")
        elif d == "pendiente_itt":  # lo tiene que hacer ITT antes de ofertar (memoria de cálculo, esquema, planos): frena igual
            malos.append(f"{r['id']}: pendiente de ITT ({ref[:60] or 'sin detalle'})")
        elif not _norm(r["texto"]) or not _norm(r["documento"]):
            malos.append(f"{r['id']}: falta el texto literal o el documento de origen")
        elif d != "cumple" and not ref:
            malos.append(f"{r['id']}: destino {d} sin referencia (posición, desvío o exclusión de la oferta)")
        elif d == "renglon" and not all(p.strip() in plano_pos for p in ref.split(";")):
            malos.append(f"{r['id']}: la referencia «{ref}» no es una posición ni un rubro del cómputo")
        elif d in ("desvio", "exclusion") and _clave_col(ref) not in textos_oferta:
            malos.append(f"{r['id']}: la referencia «{ref[:50]}» no está en la oferta (copiar un fragmento literal de la aclaración, "
                         "desvío o exclusión de oferta.json)")
    if not malos:
        return []
    return [("requisitos", f"{len(malos)} requisito(s) sin destino cerrado: " + "; ".join(malos[:5]) + ("…" if len(malos) > 5 else ""))]


# un motivo que dice que falta el precio ("pedir cotización", "a Compras") no explica por qué va en 0: el precio falta y frena
# (auditoría del 30-10-2026, Camuzzi 003: 9 renglones en 0 con "pedir cotización" levantaban el freno). Valen motivos como
# "lo provee el cliente" o "incluido en el renglón M05".
PENDIENTE_PRECIO = r"pedir|cotiza|compras|sin referencia|sin precio|a definir|pendiente|confirmar|averiguar|consultar"


def _justificada(t):
    """Una justificación tiene que decir algo: al menos 20 letras (auditoría 30-10-2026: "." o "ok" levantaban el freno)."""
    return len(_norm(t)) >= 20


def frenos_sin_precio(cfg):
    """Lo que falta frena (principio 4): un renglón en 0 baja el costo y además levantaba el freno de lo estimado."""
    malos = [it["id"] for it in cfg["items"] if not (it["fuentes"][0].get("precio") or 0)
             and (not _justificada(it.get("sin_precio_motivo")) or re.search(PENDIENTE_PRECIO, str(it.get("sin_precio_motivo")).lower()))]
    if not malos:
        return []
    return [("sin_precio", f"{len(malos)} renglón(es) en 0 ({', '.join(malos[:8])}{'…' if len(malos) > 8 else ''}): pedir el precio o "
             "escribir en el ítem sin_precio_motivo (por qué va en 0: lo provee el cliente, está incluido en otro renglón…)")]


def frenos_pendientes_oferta(carpeta):
    ro = carpeta / "oferta.json"
    if not ro.exists():
        return []
    marcas = [t for x in _textos(json.load(open(ro, encoding="utf-8"))) for t in re.findall(r"\[[^\]]+\]", x)]
    if not marcas:
        return []
    return [("pendientes_oferta", f"la oferta tiene {len(marcas)} dato(s) entre corchetes sin completar ({'; '.join(m[:40] for m in marcas[:3])}"
             f"{'…' if len(marcas) > 3 else ''}): completarlos en oferta.json")]


def frenos_computo(carpeta):
    import contextlib
    import io
    import verificar_computo
    if not (carpeta / "computo.csv").exists():
        return [("computo", "falta computo.csv: armar la cotización con armar_cotizacion.py")]
    with contextlib.redirect_stdout(io.StringIO()):
        rc = verificar_computo.main(carpeta)
    return [("computo", "verificar_computo.py da errores: corregirlos antes de generar ofertas")] if rc else []


def frenos_estimado(cfg, just):
    tot = est = 0.0
    for it in cfg["items"]:
        f = it["fuentes"][0]
        v = (it.get("cantidad") or 0) * (f.get("precio") or 0)
        tot += v
        if f.get("tipo") == "est":
            est += v
    if tot and est / tot > LIMITE_ESTIMADO and not _justificada(just.get("estimado")):
        return [("estimado", f"lo estimado es el {est / tot:.0%} del costo directo (USD {fmt(est, 2)} de {fmt(tot, 2)}), más del "
                 f"{LIMITE_ESTIMADO:.0%}: pedir cotizaciones o escribir justificaciones.estimado")]
    return []


def frenos_vencidas(cfg, just, hoy):
    if _justificada(just.get("vencidas")):
        return []
    malos = []
    for it in cfg["items"]:
        f = it["fuentes"][0]
        if f.get("tipo") not in ("cot", "lista") or not f.get("precio"):
            continue
        fecha = str(f.get("fecha") or "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha) or date.fromisoformat(fecha) > hoy:
            malos.append(f"{it['id']} (sin fecha válida)")
            continue
        if f["tipo"] == "lista":  # una lista de precios no tiene validez escrita: vale hasta DIAS_LISTA
            if (hoy - date.fromisoformat(fecha)).days > DIAS_LISTA:
                malos.append(f"{it['id']} (lista del {a_vista(fecha)}, más de {DIAS_LISTA} días)")
            continue
        rec = str(f.get("reconfirmado") or "")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", rec) and 0 <= (hoy - date.fromisoformat(rec)).days <= DIAS_VALIDEZ:
            continue
        val = str(f.get("validez_hasta") or "")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
            if date.fromisoformat(val) < hoy:
                malos.append(f"{it['id']} (válida hasta {a_vista(val)})")
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f.get("fecha") or "")):
            dias = (hoy - date.fromisoformat(f["fecha"])).days
            if dias > DIAS_VALIDEZ:
                malos.append(f"{it['id']} (del {a_vista(f['fecha'])}, {dias} días, sin validez escrita)")
    if not malos:
        return []
    return [("vencidas", f"{len(malos)} cotización(es) de proveedor vencida(s): " + ", ".join(malos[:6]) + ("…" if len(malos) > 6 else "")
             + ". Reconfirmarlas (fuente → reconfirmado: AAAA-MM-DD) o escribir justificaciones.vencidas")]


def frenos_antecedentes(carpeta, just, recalcular=True):
    if _justificada(just.get("antecedentes")):
        return []
    import comparar_antecedentes
    if recalcular or not comparar_antecedentes.ultimo:
        comparar_antecedentes.main(carpeta)
    u = comparar_antecedentes.ultimo
    if u.get("dif") is None:
        return [("antecedentes", "ningún antecedente tiene costo por equipo comparable (control de doble método): comparar a mano "
                 "y escribir justificaciones.antecedentes con el antecedente usado y la diferencia rubro por rubro")]
    if abs(u["dif"]) > LIMITE_ANTECEDENTE:
        return [("antecedentes", f"el costo difiere {u['dif']:+.0%} del antecedente más parecido con costo ({u['id'][:60]}): "
                 "explicarlo rubro por rubro en justificaciones.antecedentes")]
    return []


def frenos_plazo(carpeta, recalcular=True):
    import plazo
    if recalcular or not plazo.ultimo:
        plazo.main(carpeta)
    b = plazo.bloquea_oferta()
    return [("plazo", b)] if b else []


def frenos_repo(carpeta):
    """Los frenos que dependen de archivos del repositorio, para la página (web/semilla.py → cot.frenos_repo). El de
    antecedentes va sin mirar la justificación: la página lo levanta si se escribe justificaciones.antecedentes."""
    carpeta = Path(carpeta)
    cfg = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    rp = carpeta / "pedido" / "lista_materiales_plano.csv"
    plano_pos = {r["pos"].strip() for r in csv.DictReader(open(rp, encoding="utf-8"))} if rp.exists() else set()
    plano_pos |= {str(it.get("pos", "")).strip() for it in cfg["items"]}
    return frenos_computo(carpeta) + frenos_transcripcion(carpeta, cfg) + frenos_requisitos(carpeta, plano_pos) + frenos_antecedentes(carpeta, {})


def frenos(carpeta, hoy=None, recalcular=True):
    """Lista de (clave, texto). Vacía = la oferta puede generarse (sigue en borrador hasta la aprobación).
    recalcular=False usa la última corrida de comparar_antecedentes y plazo (armar_cotizacion.py ya los corrió)."""
    carpeta = Path(carpeta)
    hoy = hoy or date.today()
    cfg = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    just = cfg.get("justificaciones") or {}
    rp = carpeta / "pedido" / "lista_materiales_plano.csv"
    plano_pos = {r["pos"].strip() for r in csv.DictReader(open(rp, encoding="utf-8"))} if rp.exists() else set()
    plano_pos |= {str(it.get("pos", "")).strip() for it in cfg["items"]}
    out = (frenos_computo(carpeta) if recalcular else []) + frenos_transcripcion(carpeta, cfg) + frenos_requisitos(carpeta, plano_pos)
    out += frenos_sin_precio(cfg) + frenos_estimado(cfg, just) + frenos_vencidas(cfg, just, hoy) + frenos_pendientes_oferta(carpeta)
    return out + frenos_antecedentes(carpeta, just, recalcular) + frenos_plazo(carpeta, recalcular)


def main(argv):
    if len(argv) == 4 and argv[1] == "--comparar":
        a, b = (json.load(open(r, encoding="utf-8")) for r in argv[2:4])
        difs = comparar_lecturas(a, b)
        for d in difs:
            print(f"  ≠ {d[0]} · pos {d[1]} · {d[2]}: A «{d[3]}» / B «{d[4]}»")
        print(f"{len(difs)} diferencia(s)")
        return 1 if difs else 0
    if len(argv) != 2:
        sys.exit(__doc__)
    fr = frenos(argv[1])
    print(f"FRENOS DE LA OFERTA ({len(fr)})")
    for k, t in fr:
        print(f"  ■ [{k}] {t}")
    return 1 if fr else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
