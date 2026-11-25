"""Pesos y pulgadas de soldadura de listas de materiales (para el informe previo a la cotización).

Lo usa cada cotizaciones/<carpeta>/listas_preliminares.py (modelo: COT26-0010-002). Sin IA: solo tablas del repo.
- Pesos: tablas de conocimiento/tecnico (B36.10, B16.5, B16.9, B16.11, B16.47, B16.36, MSS SP-97, Taval Lista 30,
  espárragos). Lo que no está en tabla devuelve None y el script de la cotización pone un aproximado marcado.
- Soldadura: mismas reglas que herramientas/precotizar.py: pulg-eq = Ø × factor de espesor (factores_soldadura.csv);
  olets por el Ø de salida × 1,75 (weldolet × 2,5); caño por metro: cada extremo BW de accesorio o brida es una
  junta con caño × 0,75 (AJUSTE_DIRECTAS) + empalmes entre barras de 6 m.
"""
import csv
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numeros  # noqa: E402

TEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'conocimiento', 'tecnico')
AJUSTE_DIRECTAS = 0.75  # el mismo de precotizar.py
BARRA_M = 6.0


def _csv(n):
    with open(os.path.join(TEC, n), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


_T = {}


def tabla(n):
    if n not in _T:
        _T[n] = _csv(n)
    return _T[n]


def _eq(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return False


def fila_cano(dn, sch):
    return next((r for r in tabla('canos_peso_superficie.csv') if _eq(r['dn_pulg'], dn) and (r['schedule'] == sch or r['clase'] == sch)), None)


def espesor(dn, sch):
    r = fila_cano(dn, sch)
    return float(r['espesor_mm']) if r else None


def factor_esp(dn, sch=None, esp=None):
    """Factor de espesor de factores_soldadura.csv (espesor / espesor STD); con espesor dado, el de la fila más parecida
    o, si el Ø no tiene ese espesor (32"), espesor / 9,53 (STD)."""
    filas = [r for r in tabla('factores_soldadura.csv') if _eq(r['dn_pulg'], dn)]
    if esp is None and sch:
        r = next((r for r in filas if r['schedule'] == sch or r['clase'] == sch), None)
        if r:
            return float(r['factor_espesor'])
        esp = espesor(dn, sch)
    if esp is not None:
        cand = [r for r in filas if r['espesor_mm'] and abs(float(r['espesor_mm']) - esp) < 0.6]
        if cand:
            return float(min(cand, key=lambda r: abs(float(r['espesor_mm']) - esp))['factor_espesor'])
        return max(1.0, esp / 9.53)
    return 1.0


def kg_cano(dn, sch):
    r = fila_cano(dn, sch)
    return (float(r['kg_m_carbono']), 'B36.10') if r else (None, 'sin tabla')


def kg_brida(tipo, dn, serie):
    if tipo == 'orificio':
        r = next((r for r in tabla('bridas_orificio_b1636_peso.csv') if _eq(r['dn_pulg'], dn) and r['clase'] == serie), None)
        return (2 * float(r['peso_kg']), 'B16.36 (par)') if r else (None, 'sin tabla')
    if dn >= 26:
        r = next((r for r in tabla('bridas_b1647_peso.csv') if r['tipo'] == tipo and r['serie_b1647'] == 'A' and r['clase'] == serie and _eq(r['dn_pulg'], dn)), None)
        return (float(r['peso_kg']), 'B16.47 A') if r else (None, 'sin tabla')
    r = next((r for r in tabla('bridas_peso.csv') if r['tipo'] == tipo and _eq(r['dn_pulg'], dn) and r['serie'] == serie and 'no usar' not in r['nota']), None)
    return (float(r['peso_kg']), 'B16.5') if r else (None, 'sin tabla')


def kg_acc(tipo, dn, clase, ext='BW', dn2=None, sch_real=None):
    """Peso de B16.9 / B16.11. Si el schedule real no está (10" Sch 80), toma XS y lo escala por el espesor."""
    def busca(c):
        cand = [r for r in tabla('accesorios_peso.csv') if r['tipo'] == tipo and _eq(r['dn_pulg'], dn) and r['extremos'] == ext
                and r['schedule_o_clase'] == c and 'no sirve' not in r['nota'] and (dn2 is None or _eq(r['dn2_pulg'], dn2))]
        cand.sort(key=lambda r: r['nota'].startswith('ATENCION'))
        return cand[0] if cand else None
    r = busca(clase)
    if r:
        f = 1.0
        if sch_real and ext == 'BW':
            e_real, e_tab = espesor(dn, sch_real), espesor(dn, clase)
            f = e_real / e_tab if e_real and e_tab else 1.0
        return float(r['peso_kg']) * f, (r['norma'] + (f' × {numeros.fmt(f)} por espesor' if abs(f - 1) > 0.01 else ''))
    return None, 'sin tabla'


def kg_olet(tipo, dn, clase):
    r = next((r for r in tabla('olets_peso.csv') if r['tipo'] == tipo and _eq(r['dn_salida_pulg'], dn) and r['schedule_o_clase'] == clase and r['configuracion'] == 'reducing'), None)
    return (float(r['peso_kg']), 'MSS SP-97') if r else (None, 'sin tabla')


def kg_valvula(tipos, dn, serie, ext='RF'):
    for t in tipos:
        r = next((r for r in tabla('valvulas_peso.csv') if r['tipo'] == t and _eq(r['dn_pulg'], dn) and r['serie'] == serie and r['extremos'] == ext), None)
        if r:
            return float(r['kg']), 'Taval Lista 30'
    return None, 'sin tabla'


def kg_esparrago(d, largo):
    r = [x for x in tabla('esparragos_peso.csv') if x['tipo'] == 'esparrago_2_tuercas' and _eq(x['diametro_pulg'], d)]
    if not r:
        return None, 'sin tabla'
    x = min(r, key=lambda x: abs(float(x['largo_pulg']) - largo))
    return float(x['peso_unidad_kg']), 'B16.5 / B18.2.2 (calculado)'


def medida_esparrago(t):
    """'5/8" × 4 1/4"' → (0,625, 4,25)."""
    m = re.match(r'\s*([\d ]+(?:/\d+)?)"\s*×\s*([\d ]+(?:/\d+)?)"', t)
    if not m:
        return None, None

    def frac(x):
        tot = 0.0
        for p in x.strip().split():
            if '/' in p:
                a, b = p.split('/')
                tot += float(a) / float(b)
            else:
                tot += float(p)
        return tot
    return frac(m.group(1)), frac(m.group(2))


def soldaduras_piping(canos, canos_meta, accesorios, acc_meta, bridas, bri_meta, i_metros=5, i_cant_acc=5, i_cant_bri=6):
    """Filas (tipo, Ø, sch, juntas, pulg. nominales, factor, pulg-eq) agrupadas por tipo y Ø.
    canos_meta: (Ø, sch) o None; acc_meta: (tipo tabla, Ø, Ø2, clase tabla, extremos, sch real, extremos BW, extremos SW,
    factor olet); bri_meta: (tipo, Ø, serie, sch del cuello, extremos BW, extremos SW)."""
    g = {}

    def suma(tipo, dn, sch, juntas, factor):
        k = (tipo, dn, sch)
        j0, _ = g.get(k, (0.0, factor))
        g[k] = (j0 + juntas, factor)
    for c, m in zip(canos, canos_meta):  # empalmes entre barras de 6 m
        if m and 'BE' in c[0]:
            emp = max(0, math.ceil(c[i_metros] / BARRA_M - 1e-9) - 1)
            if emp:
                suma('BW a tope (taller)', m[0], m[1], emp, factor_esp(m[0], m[1]))
    for a, m in zip(accesorios, acc_meta):
        tipo, dn, dn2, cl, ext, schr, n_bw, n_sw, f_olet = m
        q = a[i_cant_acc]
        if f_olet:
            suma('Olet (' + ('weldolet' if tipo == 'weldolet' else 'thredolet/sockolet') + ')', dn, cl, q, f_olet)
            continue
        if n_bw:
            if dn2:  # reducción: un extremo de cada Ø; te de reducción: dos del Ø mayor y uno del menor (mismo schedule)
                n_may = n_bw - 1
                suma('BW a tope (taller)', dn, schr, q * n_may * AJUSTE_DIRECTAS, factor_esp(dn, schr))
                suma('BW a tope (taller)', dn2, schr, q * AJUSTE_DIRECTAS, factor_esp(dn2, schr))
            else:
                suma('BW a tope (taller)', dn, schr, q * n_bw * AJUSTE_DIRECTAS, factor_esp(dn, schr))
        if n_sw:
            suma('SW (enchufe)', dn, schr, q * n_sw, factor_esp(dn, schr))
    for b, m in zip(bridas, bri_meta):
        tipo, dn, serie, sch, n_bw, n_sw = m
        q = b[i_cant_bri]
        if n_bw:
            suma('BW a tope (taller)', dn, sch, q * n_bw * AJUSTE_DIRECTAS, factor_esp(dn, sch))
        if n_sw:
            suma('SW (enchufe)', dn, sch, q * n_sw, factor_esp(dn, sch))
    filas = []
    for (tipo, dn, sch), (j, f) in sorted(g.items(), key=lambda x: (x[0][0], -x[0][1])):
        j = math.ceil(j - 1e-9)  # juntas enteras
        filas.append((tipo, dn, sch, j, j * dn, f, j * dn * f))
    return filas
