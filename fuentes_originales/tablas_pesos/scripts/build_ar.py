"""Parsers de las fuentes argentinas: Acindar (Tablas y Equivalencias, ene-2007), Ferrara S.A. (perfiles.com.ar, catalogo completo) y Aceros Norte."""
import re, subprocess, math, os
import pdfplumber
from common import *

U_ACI = 'https://www.arquitectogustavo.com.ar/Archs/ACINDAR-libroamarillo.pdf'
N_ACI = 'Acindar, Tablas y Equivalencias (Productos, Sistemas y Servicios para la Construccion), edicion enero 2007 (copia en arquitectogustavo.com.ar)'
U_FER = 'https://www.perfiles.com.ar/wp-content/uploads/2020/09/LP-COMPLETO.pdf'
N_FER = 'Ferrara S.A. (perfiles.com.ar, Argentina), Catalogo de productos'
U_NOR = 'https://acerosnorte.com.ar/wp-content/uploads/2026/03/PESOS-Y-MEDIDA-CHAPA-SEMILLA-DE-MELON.pdf'
N_NOR = 'Aceros Norte (Argentina), Pesos y medida chapa semilla de melon'

def txt(f, p, x=None, W=None):
    cmd = ['pdftotext', '-layout', '-f', str(p), '-l', str(p)]
    if x is not None: cmd += ['-x', str(int(x)), '-y', '0', '-W', str(int(W)), '-H', '600']
    return subprocess.run(cmd + [f, '-'], capture_output=True, text=True).stdout

def numtoks(line):
    """tokens numericos iniciales de una linea (coma decimal, punto de miles)"""
    out = []
    for t in line.split():
        if re.match(r'^\d{1,3}(\.\d{3})+$', t) or NUM.match(t): out.append(num(t))
        else: break
    return out

# ----------------------------------------------------------------------------- Acindar
def aci_angulos(f):
    t = txt(f, 9)
    rows = []
    for m in re.finditer(r'(\d+ \d/\d|\d/\d|\d)[”"]\s*x\s*(\d/\d+)[”"]\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', t):
        a, e, F, g = num(m.group(3)), num(m.group(4)), num(m.group(6)), num(m.group(7))
        rows.append((m.group(1) + '" x ' + m.group(2) + '"', a, e, g, F))
    return rows

def aci_perfiles(f):
    """UPN (p10 izq), IPN (p10 der), HEB (p11 izq), IPE (p11 der): (familia, denom, h, b, s, t, kg/m)"""
    out = []
    W = 283.5
    spec = [(10, 0, 'UPN', 7), (10, W, 'IPN', 6), (11, 0, 'HEB', 6), (11, W, 'IPE', 6)]
    for pg, x, fam, idx in spec:
        t = txt(f, pg, x, W)
        for ln in t.split('\n'):
            v = numtoks(ln.strip())
            if len(v) >= idx + 2 and v[0] == v[1] and v[0] >= 80:
                den, h, b, s, tt = v[0], v[1], v[2], v[3], v[4]
                out.append((fam, den, h, b, s, tt, v[idx], v[idx - 1]))
    return out

def aci_u_chicos(f):
    out = []
    with pdfplumber.open(f) as pdf:
        p = pdf.pages[11]
        ws = [w for w in p.extract_words() if w['x0'] < 283]
        rows = rows_of_words(ws)
        for r in rows:
            if re.match(r'^\d+x\d+x[\d,]+$', r[0]['text']) and len(r) >= 3:
                h, b = [int(x) for x in r[0]['text'].split('x')[:2]]
                out.append((h, b, num(r[0]['text'].split('x')[2]), num(r[-1]['text'])))
    return out

def rows_of_words(ws, tol=2.5):
    ws = sorted(ws, key=lambda w: (round(w['top']), w['x0']))
    rows = []
    for w in ws:
        if rows and abs(rows[-1][0]['top'] - w['top']) <= tol: rows[-1].append(w)
        else: rows.append([w])
    for r in rows: r.sort(key=lambda w: w['x0'])
    return rows

def aci_barras(f):
    t = txt(f, 12, 283.5, 284)
    cu, re_ = [], []
    mode = None
    for ln in t.split('\n'):
        if 'Barras cuadradas' in ln: mode = 'cu'
        if 'Barras redondas' in ln: mode = 're'
        m = re.match(r'^\s*(\d+ \d/\d+|\d+/\d+|\d)["”\']\s+([\d,]+)\s+(?:\d+ \d/\d+|\d+/\d+|\d)["”\']\s+([\d,]+)\s+([\d,]+)', ln)
        if m and mode: (cu if mode == 'cu' else re_).append((m.group(1), num(m.group(2)), num(m.group(3)), num(m.group(4))))
    return cu, re_

def aci_planchuelas(f):
    t = txt(f, 13, 0, 283.5)
    ths = [3.2, 4.8, 6.4, 7.9, 9.5, 12.7, 15.9, 19.1, 25.4]
    ths_in = ['1/8', '3/16', '1/4', '5/16', '3/8', '1/2', '5/8', '3/4', '1']
    out = []
    for ln in t.split('\n'):
        m = re.match(r'^\s*(\d+ \d/\d|\d/\d|\d)\s+([\d,]+)\s+((?:[\d,]+\s*)+)$', ln.strip() + '')
        if m:
            vals = [num(x) for x in m.group(3).split()]
            ancho = num(m.group(2))
            if ancho < 12 or ancho > 160: continue
            for k, v in enumerate(vals): out.append((m.group(1), ancho, ths_in[k], ths[k], v))
    return out

# ----------------------------------------------------------------------------- Ferrara
def fer_tubos(f):
    """tubos estructurales cuadrados y rectangulares (p7) y uso mecanico tipo agua (p8): (familia, a, b, e, kg/m)"""
    out = []
    with pdfplumber.open(f) as pdf:
        for pn, kind in ((6, 'sq'), (7, 'agua')):
            page = pdf.pages[pn]; ws = page.extract_words()
            rows = rows_of_words(ws, 3)
            hdrs = []   # (y, [(x, e)])
            for r in rows:
                toks = [w for w in r if re.match(r'^\d,\d\d$', w['text'])]
                if len(toks) >= 5 and all(w['x0'] > 90 for w in toks) and len(toks) == len([w for w in r if w['x0'] > 90 and re.match(r'^[\d,]+$', w['text'])]):
                    hdrs.append((r[0]['top'], [((w['x0'] + w['x1']) / 2, num(w['text'])) for w in toks]))
            hdrs.sort()
            # tablas: cuadrados (hdr0), rectangulares (hdr1/hdr2 segun repeticion de cabecera)
            for r in rows:
                y = r[0]['top']
                wt = [w for w in r if re.match(r'^\d{1,2},\d{3}$', w['text'])]
                if not wt: continue
                lab = [w for w in r if (kind == 'sq' and re.match(r'^\d+x\d+$', w['text'])) or (kind == 'agua' and re.match(r'^\d+,\d{2}$', w['text']) and w['x0'] < 130)]
                if not lab: continue
                hd = [h for h in hdrs if h[0] < y]
                if not hd: continue
                cols = hd[-1][1]
                lbl = lab[0]['text']
                for w in wt:
                    cx = (w['x0'] + w['x1']) / 2
                    c = min(cols, key=lambda c: abs(c[0] - cx))
                    if abs(c[0] - cx) > 9: continue
                    if kind == 'agua':
                        out.append(('tubo_redondo', num(lbl), None, c[1], num(w['text']), 'agua'))
                    else:
                        a, b = [float(x) for x in lbl.split('x')]
                        out.append(('tubo_cuadrado' if a == b else 'tubo_rectangular', a, b, c[1], num(w['text']), 'sq'))
    return out

def fer_angulos(f):
    t = txt(f, 9) + txt(f, 10)
    i = t.find('Barras Redondas y Cuadradas')
    rows = []
    for ln in t[:i if i > 0 else None].split('\n'):
        m = re.search(r'(?:(\d+ \d/\d|\d/\d|\d)\s+)?x\s+(\d/\d+)\s+(\d+,\d{2})\s+(\d,\d{2})\s+(\d{1,2},\d{3})', ln)
        if m: rows.append((num(m.group(3)), num(m.group(4)), num(m.group(5))))
    return rows

def fer_barras(f):
    t = txt(f, 10)
    out = []
    for ln in t.split('\n'):
        m = re.match(r'^\s*(\d+,\d{2})\s+(\d+ \d/\d|\d/\d+|\d)\s+(\d+,\d{3})\s+(\d+,\d{3})', ln)
        if m: out.append((num(m.group(1)), m.group(2), num(m.group(3)), num(m.group(4))))
    return out

def fer_matriz(f, pn, hdr_pat, lab_pat, wt_pat, maxy=None, miny=0):
    """matriz con cabecera numerica en x: devuelve (etiqueta, columna, valor)"""
    out = []
    with pdfplumber.open(f) as pdf:
        page = pdf.pages[pn]
        rows = rows_of_words(page.extract_words(), 3)
        hdr = None
        for r in rows:
            if r[0]['top'] < miny: continue
            toks = [w for w in r if re.match(hdr_pat, w['text'])]
            if len(toks) >= 3 and hdr is None:
                hdr = [((w['x0'] + w['x1']) / 2, num(w['text'])) for w in toks]; continue
            if hdr is None: continue
            if maxy and r[0]['top'] > maxy: break
            lab = [w for w in r if re.match(lab_pat, w['text'])]
            wt = [w for w in r if re.match(wt_pat, w['text']) and w not in lab]
            if not lab or not wt: continue
            for w in wt:
                cx = (w['x0'] + w['x1']) / 2
                c = min(hdr, key=lambda c: abs(c[0] - cx))
                if abs(c[0] - cx) <= 12: out.append((num(lab[0]['text']), c[1], num(w['text'])))
    return out

def fer_planchuelas(f):
    return fer_matriz(f, 10, r'^\d{1,2},\d{2}$', r'^\d{1,3},\d{2}$', r'^\d,\d{3}$|^\d{2},\d{3}$', miny=100)

def fer_u_upn_ipn_heb(f):
    out = []
    # U chicos (p15), UPN (p16), IPN (p17), GREY/HEB (p18)
    for pg, fam in ((15, 'UCH'), (16, 'UPN'), (17, 'IPN'), (18, 'HEB')):
        t = txt(f, pg)
        for ln in t.split('\n'):
            s = ln.strip()
            if fam == 'UCH':
                m = re.match(r'^(\d+)\s+x\s+(\d+)\s+6\s+(\d,\d)\s*$', s)
                if m: out.append((fam, int(m.group(1)), int(m.group(2)), None, None, None, num(m.group(3))))
                continue
            v = numtoks(s)
            if fam == 'UPN' and len(v) >= 8 and v[0] == v[1] and v[0] >= 80: out.append((fam, v[0], v[1], v[2], v[3], v[4], v[7]))
            elif fam == 'IPN' and len(v) >= 7 and v[0] == v[1] and v[0] >= 80: out.append((fam, v[0], v[1], v[2], v[3], v[4], v[6]))
            elif fam == 'HEB' and len(v) >= 7 and v[0] == v[1] and v[0] >= 100: out.append((fam, v[0], v[1], v[2], v[3], v[4], v[6]))
    return out

def fer_perfiles_chapa(f):
    out = []
    for pg, fam in ((24, 'C'), (25, 'U')):
        t = txt(f, pg)
        for ln in t.split('\n'):
            if fam == 'C':
                m = re.match(r'^\s*C (\d+)x(\d+)x(\d+)x([\d,]+)\s+\d+\s+\d+\s+\d+\s+[\d,]+\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$', ln)
                if m: out.append((fam, int(m.group(1)), int(m.group(2)), int(m.group(3)), num(m.group(4)), num(m.group(5)), num(m.group(7)), num(m.group(8))))
            else:
                m = re.match(r'^\s*U (\d+)x(\d+)x([\d,]+)\s+\d+\s+\d+\s+[\d,]+\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$', ln)
                if m: out.append((fam, int(m.group(1)), int(m.group(2)), None, num(m.group(3)), num(m.group(4)), num(m.group(6)), num(m.group(7))))
    return out

def fer_chapas_lisas(f):
    """p29 (lisas, hojas) -> (kg_hoja, ancho_mm, largo_mm, espesor_mm)"""
    out = []
    with pdfplumber.open(f) as pdf:
        page = pdf.pages[28]
        rows = rows_of_words(page.extract_words(), 3)
        anchos = largos = None
        for r in rows:
            txts = [w['text'] for w in r]
            if txts[:2] == ['Ancho', 'mm']:
                anchos = [((w['x0'] + w['x1']) / 2, int(num(w['text']) * 1000)) for w in r if re.match(r'^\d,\d{3}$', w['text'])]
            if 'Largo' in txts and 'mm' in txts and anchos and largos is None:
                largos = [((w['x0'] + w['x1']) / 2, int(num(w['text']) * 1000)) for w in r if re.match(r'^\d,\d{3}$', w['text'])]
                continue
            if anchos and largos:
                lab = [w for w in r if re.match(r'^\d,\d{2}$', w['text']) and 70 < w['x0'] < 200]
                if not lab: continue
                e = num(lab[0]['text'])
                for w in r:
                    if w is lab[0] or not re.match(r'^\d{1,3},\d{2}$', w['text']) or w['x0'] < 200: continue
                    cx = (w['x0'] + w['x1']) / 2
                    a = min(anchos, key=lambda c: abs(c[0] - cx)); l = min(largos, key=lambda c: abs(c[0] - cx))
                    if abs(a[0] - cx) < 14:
                        out.append((num(w['text']), a[1], l[1], e))
    return out

def fer_semilla(f):
    out = []
    with pdfplumber.open(f) as pdf:
        page = pdf.pages[30]
        rows = rows_of_words(page.extract_words(), 3)
        sec = None; anchos = largos = None
        for r in rows:
            txts = [w['text'] for w in r]
            if 'Semilla' in txts and 'Melon' in txts and r[0]['top'] > 100: sec = 'semilla'
            if 'Estampada' in txts: sec = 'estampada'; anchos = largos = None
            if txts[:2] == ['Ancho', 'mm']:
                anchos = [((w['x0'] + w['x1']) / 2, int(num(w['text']) * 1000) if ',' in w['text'] and len(w['text']) == 5 else int(num(w['text']))) for w in r if re.match(r'^\d[,.]?\d{3}$', w['text'])]
                largos = None
            elif 'Largo' in txts and 'mm' in txts and anchos and largos is None:
                largos = [((w['x0'] + w['x1']) / 2, int(num(w['text']) * 1000) if ',' in w['text'] else int(num(w['text']))) for w in r if re.match(r'^\d[,.]?\d{3}$', w['text'])]
            elif anchos and largos and sec:
                lab = [w for w in r if re.match(r'^\d{1,2},\d{2}$', w['text']) and 70 < w['x0'] < 200]
                if not lab: continue
                e = num(lab[0]['text'])
                for w in r:
                    if w is lab[0] or not re.match(r'^\d{1,3},\d{2}$', w['text']) or w['x0'] < 200: continue
                    cx = (w['x0'] + w['x1']) / 2
                    a = min(anchos, key=lambda c: abs(c[0] - cx)); l = min(largos, key=lambda c: abs(c[0] - cx))
                    out.append((sec, num(w['text']), a[1], l[1], e))
    return out

def fer_desplegado(f):
    out = []
    with pdfplumber.open(f) as pdf:
        for pn in (35, 36):
            rows = rows_of_words(pdf.pages[pn].extract_words(), 3)
            for i, r in enumerate(rows):
                nums = [w for w in r if NUM.match(w['text'])]
                if len(nums) == 12 and len(nums) == len(r) - sum(1 for w in r if w['text'] in ('(mm)',)) and r[0]['top'] > 100:
                    for rr in rows[i + 1:]:
                        if any(w['text'] == 'Aplicaciones' for w in rr): break
                        if len(rr) == 3 and all(NUM.match(w['text']) for w in rr):
                            for g in range(3):
                                D, d, E, H = [num(w['text']) for w in nums[g * 4:g * 4 + 4]]
                                out.append((D, d, E, H, num(rr[g]['text'])))
                            break
    return out

def norte_semilla(f):
    out = []
    with pdfplumber.open(f) as pdf:
        page = pdf.pages[0]; ws = page.extract_words(); rows = rows_of_words(ws, 3)
        heads = [(( w['x0'] + w['x1']) / 2, w['text']) for w in ws if re.match(r'^\d{4}$', w['text']) and w['top'] < 120]
        txt_h = page.extract_text()
        return rows, ws
