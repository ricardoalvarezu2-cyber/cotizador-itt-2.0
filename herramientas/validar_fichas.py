"""Validador de fichas de cotización (solo avisa; no corrige ni confirma nada — Matías, 30-10-2026).

Uso: python herramientas/validar_fichas.py <ficha.json o carpeta de fichas> [...]
     (lo corre consolidar_fichas.py con las fichas que entran; la revisión contra el original sigue siendo de la IA o una persona)

Avisa si:
- la carpeta de la ficha no está en fuentes_originales/ofertas_texto/;
- falta la fecha de la oferta o no es AAAA-MM-DD; la familia no es un código válido; falta la moneda;
- el monto total no aparece en ningún documento de ITT de la carpeta (ofertas, armado, OC);
- el precio de un ítem aparece SOLO en documentos de proveedores (5.Proveedores…): los ítems son lo que ofertó ITT
  (error de la ficha de ALUAR/1, 29-10-2026), o no aparece en ningún documento.
Que un número aparezca no prueba que sea ese dato: por eso nunca dice "verificado".
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verificar_origen import TEXTOS, figura, numeros_en_texto  # noqa: E402

FAMILIAS = {"C", "SEP", "F", "SK", "M", "CO", "P", "CA", "T", "TS", "V", "S", "EST", "OT"}


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def validar(d):
    """Lista de avisos de una ficha (dict)."""
    av = []
    carpeta = TEXTOS / str(d.get("carpeta") or "")
    if not d.get("carpeta") or not carpeta.is_dir():
        return [f"la carpeta '{d.get('carpeta')}' no está en fuentes_originales/ofertas_texto/"]
    f = str(d.get("fecha_oferta") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f):
        av.append(f"fecha de oferta {'vacía' if not f else 'no es AAAA-MM-DD: ' + f}")
    fam = str(d.get("familia") or "").strip().split(" ")[0].upper()
    if fam not in FAMILIAS:
        av.append(f"familia '{d.get('familia')}' no es un código válido")
    if (num(d.get("monto_total_ofertado")) or any(num(i.get("precio_unitario")) for i in d.get("items") or [])) and not d.get("moneda"):
        av.append("falta la moneda")
    itt, prov = set(), set()
    for p in carpeta.rglob("*.txt"):
        try:
            vals = numeros_en_texto(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        (prov if re.search(r"(?i)/5[ .]*proveedores|proveedor", str(p.relative_to(carpeta))) else itt).update(vals)
    m = num(d.get("monto_total_ofertado"))
    if m and not figura(m, itt):
        av.append(f"el monto total {m} no aparece en ningún documento de ITT de la carpeta")
    for i in d.get("items") or []:
        pu = num(i.get("precio_unitario"))
        if not pu:
            continue
        en_itt, en_prov = figura(pu, itt), figura(pu, prov)
        nombre = str(i.get("descripcion") or "")[:50]
        if en_prov and not en_itt:
            av.append(f"ítem «{nombre}»: el precio {pu} aparece solo en documentos de proveedores (los ítems son lo que ofertó ITT)")
        elif not en_itt and not en_prov:
            av.append(f"ítem «{nombre}»: el precio {pu} no aparece en ningún documento de la carpeta")
    return av


def main(rutas):
    fichas = []
    for r in rutas:
        r = Path(r)
        fichas += sorted(r.glob("*.json")) if r.is_dir() else [r]
    total = 0
    for f in fichas:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"⚠ {f.name}: no se puede leer ({e})")
            total += 1
            continue
        av = validar(d)
        total += len(av)
        for a in av:
            print(f"⚠ {d.get('carpeta') or f.name}: {a}")
    print(f"Validador de fichas: {len(fichas)} fichas, {total} avisos (solo avisos: revisar contra el original)")
    return total


if __name__ == "__main__":
    main(sys.argv[1:] or [str(Path(__file__).resolve().parent.parent / "conocimiento" / "fichas_2026")])
