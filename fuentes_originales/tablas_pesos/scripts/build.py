#!/usr/bin/env python3
"""Arma los CSV conocimiento/tecnico/estructura_*.csv a partir de las fuentes guardadas en
fuentes_originales/tablas_pesos/. Consultado 28-10-2026 (se guarda 2026-10-28)."""
import sys, os, re, csv, json, html, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdfplumber, openpyxl
from common import *
import build_ar as AR
from build_ar import U_ACI, N_ACI, U_FER, N_FER, U_NOR, N_NOR

SRC = sys.argv[1]            # carpeta de fuentes
OUT = sys.argv[2]            # carpeta de salida
CONS = '2026-10-28'
RHO = 7850.0

U_INTI = 'https://www.inti.gob.ar/assets/uploads/files/cirsoc/EJEMPLOS%202/EJEMPLOS%202.2/tapa_portada.pdf'
N_INTI = 'INTI-CIRSOC: Tablas de perfiles laminados y tubos estructurales para CIRSOC 301-2005 y 302-2005 (Troglia, Troglia, Godoy; ed. julio 2005)'
U_AM = 'https://sections.arcelormittal.com/repo/Sections/Sections%20and%20Merchant%20Bars-ArcelorMittal_V2026-1.xlsx'
N_AM = 'ArcelorMittal Sections and Merchant Bars, catalogo y planilla V2026-1'
U_STW = 'https://stahlwerk-thueringen.de/files/14426C6B9D9'
N_STW = 'Stahlwerk Thuringen (CSN Sections), hoja UPE segun EN 10365:2017'
U_TAR = 'https://ar.ternium.com/media/dqle541j/2996_1_tubos-y-perfiles_ok.pdf'
N_TAR = 'Ternium Argentina, Tubos y Perfiles (version 01, 2018)'
U_WER = 'https://www.wermac.org/steel/{}.html'
N_WER = 'Wermac.org, tabla de dimensiones (EN 10025 / EN 10056)'
U_FDP = 'https://www.fabricadoprojeto.com.br/en/tabelas-de-laminados-trefilados-e-itens-comerciais/{}/'
N_FDP = 'Fabrica do Projeto (Brasil), tabela tecnica'
U_CED = 'https://www.cedinox.es/export/sites/cedinox/.galleries/publicaciones-tecnicas/Tables_TechnicalProperties_EN.pdf'
N_CED = 'Cedinox (Espana), Stainless steel: tables of technical properties'
U_DIS = 'https://www.distriplac.com/media/catalog/product/3/1/{}.pdf'
N_DIS = 'Distriplac (distribuidor Argentina), ficha Mallexpan malla romboidal'

def r3(x): return None if x is None else round(x, 4)
def fmt(v):
    if v is None or v == '': return ''
    if isinstance(v, float):
        s = ('%.4f' % v).rstrip('0').rstrip('.')
        return s
    return str(v)
def flag_monotono(rows, keyf, tf, vf):
    g = {}
    for r in rows:
        v = vf(r)
        if v in (None, ''): continue
        g.setdefault(keyf(r), []).append((float(tf(r)), float(v), r))
    n = 0
    for k, lst in g.items():
        lst.sort(key=lambda x: x[0])
        for i in range(1, len(lst)):
            if lst[i][0] > lst[i - 1][0] and lst[i][1] <= lst[i - 1][1]:
                lst[i][2]['nota'] += ' ATENCION: el peso no crece con el espesor (%s mm: %s kg/m <= %s mm: %s kg/m); posible error de la fuente.' % (fmt(lst[i][0]), fmt(lst[i][1]), fmt(lst[i - 1][0]), fmt(lst[i - 1][1]))
                n += 1
    return n

def write(name, cols, rows):
    p = os.path.join(OUT, name)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\r\n')
        w.writerow(cols)
        for r in rows: w.writerow([fmt(r.get(c, '')) for c in cols])
    print(name, len(rows))
    return rows

def pdfp(n): return os.path.join(SRC, n)
ACI = os.path.join(SRC, 'acindar_tablas_y_equivalencias_2007.pdf')
FER = os.path.join(SRC, 'ferrara_perfiles_com_ar_catalogo_completo.pdf')
INTI = pdfp('inti_cirsoc_tablas_perfiles_tubos_2005.pdf')

# ------------------------------------------------------------------ perfiles laminados
def inti_perfiles():
    out = []
    pages = {7: ('IPN', 'IPN', 'IRAM-IAS U 500-511'),
             8: ('HEB', 'HEB', 'IRAM-IAS U 500-215-2 (IPB)'),
             9: ('HEA', 'HEA', 'IRAM-IAS U 500-215-3 (IPBl)'),
             10: ('HEM', 'HEM', 'IRAM-IAS U 500-215-4 (IPBv)'),
             11: ('IPE', 'IPE', 'IRAM-IAS U 500-215-5'),
             25: ('UPN', 'UPN', 'IRAM-IAS U 500-509-2')}
    with pdfplumber.open(INTI) as pdf:
        for pg, (fam, pre, norma) in pages.items():
            page = pdf.pages[pg - 1]
            kg = [w for w in page.extract_words() if w['text'] == 'Kg/m' and w['top'] < 300][0]
            cx = (kg['x0'] + kg['x1']) / 2
            for r in rows_of(page):
                if r['y'] <= kg['top'] + 15: continue
                nums = [w for w in r['w'] if NUM.match(w['text'])]
                if len(nums) < 8: continue
                lead = ' '.join(w['text'] for w in r['w'] if w['x0'] < min(n['x0'] for n in nums) - 0.1)
                p = near(r, cx, 6)
                if not p: continue
                v = [num(n['text']) for n in nums]
                if lead and re.match(r'^\d+/\d+$', lead): continue     # HEM 320/305: fuera del alcance
                if lead:
                    des = lead; h, b, tf = v[0], v[1], v[2]
                else:
                    des = fmt(v[0]); h, b, tf = v[1], v[2], v[3]
                note = 'pagina PDF %d.' % pg
                if fam == 'UPN': note += ' Las medidas chicas (30x15, 40x20, 50x25, 50, 65) son los perfiles que en planilla ITT figuran como "UL".'
                out.append(dict(familia=fam, designacion=('%s%s' % (pre, des)) if pre in ('HEA', 'HEB', 'HEM') else '%s %s' % (pre, des), h_mm=h, b_mm=b, tf_mm=tf,
                                kg_por_m=num(p['text']), norma=norma, fuente_url=U_INTI, fuente_nombre=N_INTI, nota=note))
    return out

def am_perfiles():
    wb = openpyxl.load_workbook(os.path.join(SRC, 'arcelormittal_sections_merchant_bars_V2026-1.xlsx'), read_only=True, data_only=True)
    out = []
    rows = list(wb['EN sections'].iter_rows(values_only=True))
    ser = None
    for i, r in enumerate(rows):
        if i < 6: continue
        if r[1] and r[2] and r[4] is None and ser is None or (r[2] in ('IPE', 'HE', 'HL', 'HLZ', 'HD', 'HP', 'UBP', 'UB', 'UC') and r[4] is None):
            ser = r[2]; continue
        if ser not in ('IPE', 'HE') or r[4] is None: continue
        d = str(r[2]).strip()
        fam = ser; des = d; norma = 'EN 10365:2017'
        if ser == 'HE':
            m = re.match(r'^HE (\d+) (AA|A|B|M)$', d)
            if m: fam = 'HE' + m.group(2); des = 'HE%s%s' % (m.group(2), m.group(1))
        out.append(dict(familia=fam, designacion=des, h_mm=r[6], b_mm=r[7], tw_mm=r[8], tf_mm=r[9], kg_por_m=r[4], m2_por_m=r[14],
                        norma=norma, fuente_url=U_AM, fuente_nombre=N_AM,
                        nota='hoja "EN sections", fila Excel %d; designacion original "%s". m2/m = columna AL (superficie lateral por metro)%s' % (i + 1, d, '; "Additional section to the standard" en la fuente' if r[1] else '')))
    rows = list(wb['EN Channels'].iter_rows(values_only=True))
    for i, r in enumerate(rows):
        d = r[1]
        if not d or r[3] is None: continue
        d = str(d).strip()
        if d.startswith('UPE'): fam, norma = 'UPE', 'EN 10365:2017'
        elif d.startswith('UPN'): fam, norma = 'UPN', 'EN 10365:2017'
        else: continue
        out.append(dict(familia=fam, designacion=d, h_mm=r[4], b_mm=r[5], tw_mm=r[6], tf_mm=r[7], kg_por_m=r[3], m2_por_m=r[13],
                        norma=norma, fuente_url=U_AM, fuente_nombre=N_AM,
                        nota='hoja "EN Channels", fila Excel %d. m2/m = columna AL' % (i + 1)))
    return out

def stw_upe():
    import subprocess
    t = subprocess.run(['pdftotext', '-layout', pdfp('stahlwerk_thueringen_upe.pdf'), '-'], capture_output=True, text=True).stdout
    out = []
    for ln in t.split('\n'):
        m = re.match(r'^\s*(UPE \d+)\s+([\d,]+)\s+(\d+)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+(\d+)\s+([\d,]+)\s+(\d+)\s+(\d+)\s+M\s*\d+\s+\d+\s+\d+\s+([\d,]+)\s+([\d,]+)', ln)
        if m:
            g = m.groups()
            out.append(dict(familia='UPE', designacion=g[0], h_mm=num(g[2]), b_mm=num(g[3]), tw_mm=num(g[4]), tf_mm=num(g[5]),
                            kg_por_m=num(g[1]), m2_por_m=num(g[10]), norma='EN 10365:2017',
                            fuente_url=U_STW, fuente_nombre=N_STW, nota='segunda fuente (fabricante) para UPE 120-400; m2/m = AL'))
    return out

UCH = {(40, 20): 'UPN 40x20', (50, 25): 'UPN 50x25', (50, 38): 'UPN 50', (60, 30): 'UPN 60', (65, 42): 'UPN 65'}
UL = {'UPN 40x20': 'UL 40x20', 'UPN 50x25': 'UL 50x25', 'UPN 50': 'UL 50x38', 'UPN 65': 'UL 65x42'}
def ar_perfiles():
    rows = []
    for fam, den, h, b, sw, tf, kg, F in AR.aci_perfiles(ACI):
        d = ('%s%d' % (fam, den)) if fam == 'HEB' else '%s %d' % (fam, den)
        rows.append(dict(familia=fam, designacion=d, h_mm=h, b_mm=b, tw_mm=sw, tf_mm=tf, kg_por_m=kg, norma={'UPN': 'IRAM-IAS U 500-509', 'IPN': 'IRAM-IAS U 500-511', 'HEB': 'IRAM-IAS U 500-215-2', 'IPE': 'IRAM-IAS U 500-215-5'}[fam],
                         fuente_url=U_ACI, fuente_nombre=N_ACI, nota='Acindar (fabricante argentino); seccion F=%s cm2.' % fmt(F)))
    for h, b, e, kg in AR.aci_u_chicos(ACI):
        d = UCH[(h, b)]
        nota = 'Acindar, "Perfiles U chicos" (designado %dx%dx%s, largo 6 m).' % (h, b, fmt(e))
        if (h, b) in ((60, 30), (50, 38)):
            nota += ' ATENCION: la tabla de Acindar asigna %s kg/m a %dx%d, al reves que INTI-CIRSOC (UPN 60 = 5,07; UPN 50 = 5,59) y Ferrara (60x30 = 5,1; 50x38 = 5,6): los dos valores parecen estar cruzados en el catalogo. NO usar este renglon.' % (fmt(kg), h, b)
        rows.append(dict(familia='UPN', designacion=d, h_mm=h, b_mm=b, tw_mm=None, tf_mm=None, kg_por_m=kg, norma='IRAM-IAS U 500-509', fuente_url=U_ACI, fuente_nombre=N_ACI, nota=nota))
    for fam, den, h, b, sw, tf, kg in AR.fer_u_upn_ipn_heb(FER):
        if fam == 'UCH':
            d = UCH[(den, h)]; hh, bb = den, h
            nota = 'Ferrara, "U chicos" (peso nominal con 1 decimal, largo 6 m).'
        else:
            d = ('%s%d' % (fam, den)) if fam == 'HEB' else '%s %d' % (fam, den); hh, bb = h, b
            nota = 'Ferrara S.A. (distribuidor argentino)' + ('; "GREY (Heb Med)" = IPB' if fam == 'HEB' else '') + '.'
        rows.append(dict(familia=fam if fam != 'UCH' else 'UPN', designacion=d, h_mm=hh, b_mm=bb, tw_mm=sw, tf_mm=tf, kg_por_m=kg,
                         norma={'UPN': 'IRAM-IAS U 500-509', 'IPN': 'IRAM-IAS U 500-511', 'HEB': 'IRAM-IAS U 500-215-2', 'UCH': 'IRAM-IAS U 500-509'}[fam], fuente_url=U_FER, fuente_nombre=N_FER, nota=nota))
    for r in rows:
        if r['designacion'] in UL: r['nota'] += ' En la planilla ITT figura como "%s".' % UL[r['designacion']]
    return rows

def perfiles():
    cols = ['familia', 'designacion', 'h_mm', 'b_mm', 'tw_mm', 'tf_mm', 'kg_por_m', 'm2_por_m', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = inti_perfiles() + am_perfiles() + stw_upe() + ar_perfiles()
    for r in rows: r['consultado'] = CONS
    return write('estructura_perfiles_laminados.csv', cols, rows)

# ------------------------------------------------------------------ angulos
def html_rows(fname):
    h = open(os.path.join(SRC, fname), errors='ignore').read()
    out = []
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', h, flags=re.S):
        cells = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', c))).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, flags=re.S)]
        out.append(cells)
    return out
def wermac_text(f):
    h = open(os.path.join(SRC, 'wermac_%s.html' % f), errors='ignore').read()
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    t = re.sub(r'</t[dh]>', ' | ', t); t = re.sub(r'</tr>|<br\s*/?>|</p>|</h\d>', '\n', t)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    return t
def wermac_rows(f, pat):
    t = wermac_text(f)
    t = re.sub(r'\s*\|\s*\n?', '|', t)
    out = []
    for m in re.finditer(pat, t):
        out.append(m.groups())
    return out

def angulos():
    cols = ['familia', 'designacion', 'lado_a_mm', 'lado_b_mm', 'espesor_mm', 'kg_por_m', 'kg_por_m_calc', 'm2_por_m', 'm2_origen', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = []
    def calc(a, b, t): return (a + b - t) * t * RHO / 1e6
    def add(fam, a, b, t, kg, m2, m2o, norma, url, name, nota):
        rows.append(dict(familia=fam, designacion='L %s x %s x %s' % (fmt(a), fmt(b), fmt(t)), lado_a_mm=a, lado_b_mm=b, espesor_mm=t,
                         kg_por_m=kg, kg_por_m_calc=round(calc(a, b, t), 3), m2_por_m=m2, m2_origen=m2o, norma=norma, fuente_url=url,
                         fuente_nombre=name, consultado=CONS, nota=nota))
    # INTI (alas iguales, medidas en pulgada convertidas)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ang_inti import angulos_inti
    for pg, b, t, kg in angulos_inti(INTI):
        add('L_iguales', b, b, t, kg, round(4 * b / 1000, 4), 'calculado', 'IRAM-IAS U 500-558', U_INTI, N_INTI,
            'pagina PDF %d. Medidas comerciales en pulgada (b=%s mm). m2/m calculado = perimetro 2(a+b)/1000, sin radios. kg_por_m_calc = (a+b-e)*e*7,85/1000 (sin radios).' % (pg, fmt(b)))
    # Fabrica do Projeto (alas iguales, pulgadas)
    for c in html_rows('fabricadoprojeto_tabela-de-cantoneira-de-abas-iguais.html')[1:]:
        if len(c) < 6 or not re.match(r'^[\d./ ]+$', c[0]): continue
        try: b, t, P, M = float(c[2]), float(c[3]), float(c[4]), float(c[5])
        except: continue
        extra = ''
        t_in = inch(c[1]) * 25.4
        if abs(t_in - t) > 0.4:
            extra = ' ATENCION: la columna t(mm) de la fuente dice %s pero la designacion es %s" (= %.2f mm); se uso el espesor de la designacion.' % (fmt(t), c[1], t_in)
            t = round(t_in, 2)
        add('L_iguales', b, b, t, M, round(P / 1000, 4), 'fuente', 'ASTM A6 / medidas en pulgada', U_FDP.format('tabela-de-cantoneira-de-abas-iguais'), N_FDP,
            'designacion comercial %s" x %s". m2/m = P (perimetro, mm) de la fuente / 1000.%s' % (c[0], c[1], extra))
    # Wermac alas iguales y desiguales
    for f, fam in (('dim_angle_eq', 'L_iguales'), ('dim_angle_uneq', 'L_desiguales')):
        t = wermac_text(f)
        t = re.sub(r'\s*\|\s*\n?\s*', '|', t)
        for m in re.finditer(r'(\d+) x (\d+) x ?(\d+(?:\.\d+)?)\|(\d+(?:\.\d+)?)\|(\d\.\d+)\|', t):
            a, b, e, kg, m2 = [float(x) for x in m.groups()]
            add(fam, a, b, e, kg, m2, 'fuente', 'EN 10056-1', U_WER.format(f), N_WER, 'perfil europeo (EN 10056-1), medidas en mm; segunda fuente, ver desvios contra formula en LEEME.')
    # ArcelorMittal angulos
    wb = openpyxl.load_workbook(os.path.join(SRC, 'arcelormittal_sections_merchant_bars_V2026-1.xlsx'), read_only=True, data_only=True)
    rr = list(wb['EN Angles'].iter_rows(values_only=True))
    fam = None
    for i, r in enumerate(rr):
        if r[0] == 'Equal leg angles': fam = 'L_iguales'; continue
        if r[0] == 'Unequal leg angles': fam = 'L_desiguales'; continue
        if fam and r[1] and str(r[1]).startswith('L ') and r[2]:
            add(fam, r[3], r[3] if fam == 'L_iguales' else r[4], r[4] if fam == 'L_iguales' else r[5], r[2], r[8] if fam == 'L_iguales' else r[9], 'fuente', 'EN 10056-1:2017', U_AM, N_AM,
                'hoja "EN Angles", fila Excel %d. m2/m = AL de la fuente.' % (i + 1))
    for d, a, e, g, F in AR.aci_angulos(ACI):
        add('L_iguales', a, a, e, g, round(4 * a / 1000, 4), 'calculado', 'IRAM-IAS U 500-558', U_ACI, N_ACI,
            'Acindar (fabricante argentino), designacion comercial %s; seccion F=%s cm2. m2/m calculado = 4a/1000. Medidas en mm redondeadas a 0,1.' % (d, fmt(F)))
    for b, e, g in AR.fer_angulos(FER):
        add('L_iguales', b, b, e, g, round(4 * b / 1000, 4), 'calculado', 'IRAM-IAS U 500-558', U_FER, N_FER,
            'Ferrara S.A. (distribuidor argentino), peso por metro redondeado a 0,1 kg. m2/m calculado = 4a/1000.')
    for r in rows:
        dv = (r['kg_por_m'] / r['kg_por_m_calc'] - 1) * 100
        if r['fuente_nombre'].startswith('Wermac'):
            r['nota'] += ' Pesa %+.1f %% contra la formula (la serie Wermac da +1,9 a +3,7 %%; ArcelorMittal -0,9 a +1,3 %%): tomarlo como limite superior.' % dv
        elif abs(dv) > 4.5 and abs(r['kg_por_m'] - r['kg_por_m_calc']) > 0.06:
            r['nota'] += ' ATENCION: difiere %+.1f %% de la formula (a+b-e)*e*7,85/1000 (la sin radios da +-1 a 3 %%); probable error de la fuente, revisar contra otra.' % dv
    print('   angulos sin monotonia:', flag_monotono(rows, lambda r: (r['fuente_nombre'], r['familia'], r['lado_a_mm'], r['lado_b_mm']), lambda r: r['espesor_mm'], lambda r: r['kg_por_m']))
    return write('estructura_angulos.csv', cols, rows)

# ------------------------------------------------------------------ planchuelas / barras
def inch(s):
    # '1.1/4' -> 1.25 ; '3/8' -> 0.375 ; '5' -> 5 ; con comillas opcionales
    s = s.replace('"', '').strip()
    tot = 0.0
    for part in re.split(r'[ .](?=\d+/\d+)', s):
        if '/' in part:
            n, d = part.split('/'); tot += float(n) / float(d)
        else: tot += float(part)
    return tot
def frac(s):
    s = s.replace('"', '').replace('.1/', ' 1/').replace('.3/', ' 3/')
    return s
def planchuelas():
    cols = ['familia', 'designacion', 'ancho_mm', 'espesor_mm', 'kg_por_m', 'tipo_dato', 'kg_por_m_fuente', 'm2_por_m', 'm2_origen', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = []
    for c in html_rows('fabricadoprojeto_tabelas-fapro-ferro-chato.html')[1:]:
        if len(c) < 4 or ' x ' not in c[0]: continue
        try: t, w, kg = float(c[1]), float(c[2]), float(c[3])
        except: continue
        extra = ''
        ti, wi = [inch(x) * 25.4 for x in c[0].split(' x ')]
        if abs(wi - w) / wi > 0.02 or abs(ti - t) / ti > 0.02:
            extra = ' ATENCION: las columnas mm de la fuente (espesor %s, ancho %s) no coinciden con la designacion en pulgadas (%.2f x %.2f mm); se uso la designacion.' % (fmt(t), fmt(w), ti, wi)
        t, w = round(ti, 3), round(wi, 3)
        kgc = round(w * t * RHO / 1e6, 3)
        rows.append(dict(familia='planchuela', designacion='Planchuela %s' % c[0].replace('.1/', ' 1/').replace('.3/', ' 3/'), ancho_mm=w, espesor_mm=t, kg_por_m=kgc, tipo_dato='calculado',
                         kg_por_m_fuente=kg, m2_por_m=round(2 * (w + t) / 1000, 4), m2_origen='calculado', norma='medidas comerciales en pulgada',
                         fuente_url=U_FDP.format('tabelas-fapro-ferro-chato'), fuente_nombre=N_FDP, consultado=CONS,
                         nota='medidas comerciales (pulgada, 1" = 25,4 mm) de la fuente. kg_por_m = espesor*ancho*7,85/1000 (calculado, 7.850 kg/m3). kg_por_m_fuente = peso teorico de la tabla (redondeado a 2 decimales). m2/m calculado = 2(ancho+espesor)/1000.' + extra))
    t = wermac_text('dim_flat'); t = re.sub(r'\s*\|\s*\n?\s*', '|', t)
    for m in re.finditer(r'(\d+) x (\d+(?:\.\d+)?)\|(\d+(?:\.\d+)?)\|(\d\.\d+)\|', t):
        w, e, kg, m2 = [float(x) for x in m.groups()]
        rows.append(dict(familia='planchuela', designacion='Planchuela %s x %s mm' % (fmt(w), fmt(e)), ancho_mm=w, espesor_mm=e, kg_por_m=round(w * e * RHO / 1e6, 3), tipo_dato='calculado',
                         kg_por_m_fuente=kg, m2_por_m=m2, m2_origen='fuente', norma='EN 10058 (medidas europeas)',
                         fuente_url=U_WER.format('dim_flat'), fuente_nombre=N_WER, consultado=CONS,
                         nota='medidas ancho x espesor (mm) de la fuente. kg_por_m = ancho*espesor*7,85/1000 (calculado). kg_por_m_fuente es ~1,9 % mayor (la fuente parece usar 8.000 kg/m3), por eso no se usa. m2/m de la fuente.'))
    W_IN = {12.7: '1/2', 15.87: '5/8', 15.9: '5/8', 19.05: '3/4', 19.1: '3/4', 22.22: '7/8', 22.2: '7/8', 25.4: '1', 31.75: '1 1/4', 31.7: '1 1/4', 38.1: '1 1/2', 44.45: '1 3/4', 44.4: '1 3/4', 50.8: '2', 57.15: '2 1/4', 57.2: '2 1/4', 63.5: '2 1/2', 76.2: '3', 88.9: '3 1/2', 101.6: '4', 127.0: '5', 152.4: '6'}
    T_IN = {'1/8': 1 / 8, '3/16': 3 / 16, '1/4': 1 / 4, '5/16': 5 / 16, '3/8': 3 / 8, '1/2': 1 / 2, '5/8': 5 / 8, '3/4': 3 / 4, '1': 1.0}
    for lab, ancho, ein, emm, kg in AR.aci_planchuelas(ACI):
        w = inch(lab) * 25.4; t = T_IN[ein] * 25.4
        rows.append(dict(familia='planchuela', designacion='Planchuela %s x %s"' % (ein, lab), ancho_mm=round(w, 3), espesor_mm=round(t, 3), kg_por_m=round(w * t * RHO / 1e6, 3), tipo_dato='calculado', kg_por_m_fuente=kg,
                         m2_por_m=round(2 * (w + t) / 1000, 4), m2_origen='calculado', norma='IRAM-IAS U 500-657', fuente_url=U_ACI, fuente_nombre=N_ACI, consultado=CONS,
                         nota='Acindar (fabricante argentino), tabla "Planchuelas laminadas" (kg/m). kg_por_m = ancho*espesor*7,85/1000 (calculado, medidas exactas en pulgada); kg_por_m_fuente = valor de la tabla. m2/m calculado = 2(ancho+espesor)/1000.'))
    for ancho, emm, kg in AR.fer_planchuelas(FER):
        lab = W_IN.get(round(ancho, 2)); ein = {3.18: '1/8', 4.76: '3/16', 6.35: '1/4', 7.94: '5/16', 9.52: '3/8', 12.7: '1/2', 15.87: '5/8', 19.05: '3/4', 25.4: '1'}[round(emm, 2)]
        w = inch(lab) * 25.4; t = T_IN[ein] * 25.4
        rows.append(dict(familia='planchuela', designacion='Planchuela %s x %s"' % (ein, lab), ancho_mm=round(w, 3), espesor_mm=round(t, 3), kg_por_m=round(w * t * RHO / 1e6, 3), tipo_dato='calculado', kg_por_m_fuente=kg,
                         m2_por_m=round(2 * (w + t) / 1000, 4), m2_origen='calculado', norma='IRAM-IAS U 500-657', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS,
                         nota='Ferrara S.A. (distribuidor argentino), tabla "Planchuelas" (peso por metro). kg_por_m = ancho*espesor*7,85/1000 (calculado); kg_por_m_fuente = valor de la tabla. m2/m calculado = 2(ancho+espesor)/1000.'))
    for r in rows:
        if r['tipo_dato'] == 'calculado' and r['kg_por_m_fuente'] not in ('', None):
            dv = (float(r['kg_por_m_fuente']) / r['kg_por_m'] - 1) * 100 if r['kg_por_m'] else 0
            if abs(dv) > 3 and abs(float(r['kg_por_m_fuente']) - r['kg_por_m']) > 0.05 and 'ATENCION' not in r['nota']:
                r['nota'] += ' ATENCION: el valor de la fuente difiere %+.1f %% del calculo.' % dv
    return write('estructura_planchuelas.csv', cols, rows)

def barras():
    cols = ['familia', 'designacion', 'medida_mm', 'kg_por_m', 'tipo_dato', 'kg_por_m_fuente', 'm2_por_m', 'm2_origen', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = []
    t = wermac_text('dim_round_square'); t = re.sub(r'\s*\|\s*\n?\s*', '|', t)
    pos = [m.start() for m in re.finditer('SQUARE', t)]
    i = pos[1]
    for part, fam, f in ((t[:i], 'redondo', lambda d: math.pi * d * d / 4 * RHO / 1e6), (t[i:], 'cuadrado', lambda d: d * d * RHO / 1e6)):
        for m in re.finditer(r'(?<![\d.])(\d+)\|(\d+(?:\.\d+)?)\|(\d\.\d+)\|', part):
            d, kg, m2 = [float(x) for x in m.groups()]
            rows.append(dict(familia=fam, designacion=('Redondo D' if fam == 'redondo' else 'Cuadrado ') + fmt(d) + ' mm', medida_mm=d, kg_por_m=round(f(d), 3), tipo_dato='calculado', kg_por_m_fuente=kg,
                             m2_por_m=m2, m2_origen='fuente', norma='EN 10060 / EN 10059 (medidas europeas)', fuente_url=U_WER.format('dim_round_square'), fuente_nombre=N_WER,
                             consultado=CONS, nota='medida de la fuente. kg_por_m = seccion*7,85/1000 (calculado; cuadrado de arista viva). kg_por_m_fuente es ~1,6 a 2,4 % mayor (la fuente parece usar 8.000 kg/m3), por eso no se usa. m2/m de la fuente.'))
    for c in html_rows('fabricadoprojeto_tabela-de-barra-redonda.html')[1:]:
        if len(c) < 3 or not c[0]: continue
        try: d = float(c[1].replace(',', '.')); kg = float(c[2].replace(',', '.'))
        except: continue
        extra = ''
        di = inch(c[0]) * 25.4
        if abs(di - d) / di > 0.02: extra = ' ATENCION: el diametro mm de la fuente (%s) no coincide con la designacion en pulgadas (%.2f mm); se uso la designacion.' % (fmt(d), di)
        d = round(di, 3)
        kgc = round(math.pi * d * d / 4 * RHO / 1e6, 3)
        if abs(kg / kgc - 1) > 0.03: extra += ' ATENCION: kg_por_m_fuente (%s) difiere %+.0f %% del calculo; probable error de tipeo de la fuente.' % (fmt(kg), (kg / kgc - 1) * 100)
        rows.append(dict(familia='redondo', designacion='Redondo %s' % c[0].replace('.1/', ' 1/').replace('.3/', ' 3/'), medida_mm=d, kg_por_m=kgc, tipo_dato='calculado', kg_por_m_fuente=kg,
                         m2_por_m=round(math.pi * d / 1000, 4), m2_origen='calculado', norma='medidas comerciales en pulgada', fuente_url=U_FDP.format('tabela-de-barra-redonda'), fuente_nombre=N_FDP, consultado=CONS,
                         nota='diametro comercial en pulgada (1" = 25,4 mm). kg_por_m = pi*D^2/4*7,85/1000 (calculado). kg_por_m_fuente = peso nominal de la tabla. m2/m calculado = pi*D/1000.' + extra))
    wb = openpyxl.load_workbook(os.path.join(SRC, 'arcelormittal_sections_merchant_bars_V2026-1.xlsx'), read_only=True, data_only=True)
    for i, r in enumerate(wb['Square bars'].iter_rows(values_only=True)):
        if r[0] and re.match(r'^\d+ x \d+$', str(r[0])):
            a = float(str(r[0]).split(' x ')[0]); kg = r[1] if r[1] is not None else r[2]
            arist = 'arista viva' if r[1] is not None else 'aristas redondeadas r=%s mm' % r[3]
            rows.append(dict(familia='cuadrado', designacion='Cuadrado %s mm' % fmt(a), medida_mm=a, kg_por_m=kg, tipo_dato='fuente', kg_por_m_fuente=kg,
                             m2_por_m=round(4 * a / 1000, 4), m2_origen='calculado', norma='EN 10059:2003', fuente_url=U_AM, fuente_nombre=N_AM, consultado=CONS,
                             nota='hoja "Square bars", fila Excel %d; %s; kg/m de la fuente (cuadrados grandes). Calculo 7,85: %s. m2/m calculado = 4a/1000.' % (i + 1, arist, fmt(round(a * a * RHO / 1e6, 2)))))
    cu, rd = AR.aci_barras(ACI)
    for lab, a, F, g in cu:
        ai = inch(lab) * 25.4 if lab != '15/32' else 15 / 32 * 25.4
        rows.append(dict(familia='cuadrado', designacion='Cuadrado %s"' % lab, medida_mm=round(a, 3), kg_por_m=round(a * a * RHO / 1e6, 3), tipo_dato='calculado', kg_por_m_fuente=g, m2_por_m=round(4 * a / 1000, 4), m2_origen='calculado',
                         norma='IRAM-IAS U 500-605', fuente_url=U_ACI, fuente_nombre=N_ACI, consultado=CONS, nota='Acindar (fabricante argentino), "Barras cuadradas" (lado a = %s mm de la tabla; seccion F=%s cm2). kg_por_m = a^2*7,85/1000 (calculado); kg_por_m_fuente = G de la tabla. m2/m calculado = 4a/1000.' % (fmt(a), fmt(F))))
    for lab, d, F, g in rd:
        rows.append(dict(familia='redondo', designacion='Redondo %s"' % lab, medida_mm=round(d, 3), kg_por_m=round(math.pi * d * d / 4 * RHO / 1e6, 3), tipo_dato='calculado', kg_por_m_fuente=g, m2_por_m=round(math.pi * d / 1000, 4), m2_origen='calculado',
                         norma='IRAM-IAS U 500-605', fuente_url=U_ACI, fuente_nombre=N_ACI, consultado=CONS, nota='Acindar (fabricante argentino), "Barras redondas" (d = %s mm; seccion F=%s cm2). kg_por_m = pi*d^2/4*7,85/1000 (calculado); kg_por_m_fuente = G de la tabla. m2/m calculado = pi*d/1000.' % (fmt(d), fmt(F))))
    for mm, lab, cua, red in AR.fer_barras(FER):
        rows.append(dict(familia='cuadrado', designacion='Cuadrado %s mm (%s")' % (fmt(mm), lab), medida_mm=mm, kg_por_m=round(mm * mm * RHO / 1e6, 3), tipo_dato='calculado', kg_por_m_fuente=cua, m2_por_m=round(4 * mm / 1000, 4), m2_origen='calculado',
                         norma='IRAM-IAS U 500-605', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS, nota='Ferrara S.A. (distribuidor argentino), "Hierro cuadrado" (peso por metro). kg_por_m calculado = a^2*7,85/1000; kg_por_m_fuente = valor de la tabla. m2/m calculado = 4a/1000.'))
        rows.append(dict(familia='redondo', designacion='Redondo D%s mm (%s")' % (fmt(mm), lab), medida_mm=mm, kg_por_m=round(math.pi * mm * mm / 4 * RHO / 1e6, 3), tipo_dato='calculado', kg_por_m_fuente=red, m2_por_m=round(math.pi * mm / 1000, 4), m2_origen='calculado',
                         norma='IRAM-IAS U 500-605', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS, nota='Ferrara S.A. (distribuidor argentino), "Hierro redondo" (peso por metro). kg_por_m calculado = pi*d^2/4*7,85/1000; kg_por_m_fuente = valor de la tabla. m2/m calculado = pi*d/1000.'))
    for r in rows:
        if r['tipo_dato'] == 'calculado' and r['kg_por_m_fuente'] not in ('', None) and 'ATENCION' not in r['nota']:
            dv = (float(r['kg_por_m_fuente']) / r['kg_por_m'] - 1) * 100
            if abs(dv) > 3 and abs(float(r['kg_por_m_fuente']) - r['kg_por_m']) > 0.05: r['nota'] += ' ATENCION: el valor de la fuente difiere %+.1f %% del calculo (posible error de la fuente o medida distinta).' % dv
    return write('estructura_barras.csv', cols, rows)

# ------------------------------------------------------------------ perfiles de chapa plegada
def perfiles_chapa():
    import subprocess
    cols = ['familia', 'designacion', 'h_mm', 'b_mm', 'pestana_mm', 'espesor_mm', 'kg_por_m_lac', 'kg_por_m_galv', 'seccion_cm2', 'kg_por_m_calc', 'm2_por_m', 'm2_origen', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    t = subprocess.run(['pdftotext', '-layout', '-f', '12', '-l', '13', pdfp('ternium_argentina_tubos_y_perfiles_2018.pdf'), '-'], capture_output=True, text=True).stdout
    rows = []; sect = None; cur = None
    for ln in t.split('\n'):
        if 'PERFILES C' in ln: sect = 'C'
        if 'PERFILES U' in ln: sect = 'U'
        tok = ln.split()
        if not tok or sect is None: continue
        m = re.match(r'^(\d+)x(\d+)(?:x(\d+))?$', tok[0])
        if m and len(tok) > 3:
            cur = (int(m.group(1)), int(m.group(2)), int(m.group(3)) if m.group(3) else None); tok = tok[1:]
        if cur is None: continue
        if not re.match(r'^\d(\.\d+)?$', tok[0]) if tok else True: continue
        vals = tok
        need = 10 if sect == 'C' else 9      # sin galva
        if len(vals) < need: continue
        e = float(vals[0]); lac = float(vals[1])
        if len(vals) == need + 1:
            galv = None if vals[2] == '-' else float(vals[2]); sec = float(vals[3])
        elif len(vals) == need: galv = None; sec = float(vals[2])
        else: continue
        h, b, c = cur
        # perimetro exterior de la chapa plegada ~ 2*(h+b)-... (envolvente): se usa perimetro desarrollado = (h + 2b + 2c) - sin espesor
        per = (h + 2 * b + 2 * (c or 0))
        calc = sec * 100 * RHO / 1e6      # seccion mm2 * 7,85
        desig = ('C %dx%dx%d' % (h, b, c)) if sect == 'C' else ('U %dx%d' % (h, b))
        # m2/m: superficie por ambas caras del desarrollo = 2 * desarrollo/1000
        rows.append(dict(familia='perfil_%s_chapa' % sect, designacion=desig, h_mm=h, b_mm=b, pestana_mm=c, espesor_mm=e, kg_por_m_lac=lac, kg_por_m_galv=galv, seccion_cm2=sec,
                         kg_por_m_calc=round(calc, 3), m2_por_m=round(2 * sec * 100 / e / 1000, 4), m2_origen='calculado', norma='IRAM-IAS U500-206 (LAC) / U500-205 (galvanizado)',
                         fuente_url=U_TAR, fuente_nombre=N_TAR, consultado=CONS,
                         nota='LAC = laminado en caliente (negro). kg_por_m_calc = seccion*7,85/1000 (sin galvanizado). m2/m calculado = 2*seccion/espesor (desarrollo de la chapa por las dos caras, sin galvanizado); la fuente no da superficie.'))
    for fam, h, b, c, e, sec, galv, lac in AR.fer_perfiles_chapa(FER):
        desig = ('C %dx%dx%dx%s' % (h, b, c, fmt(e))) if fam == 'C' else ('U %dx%dx%s' % (h, b, fmt(e)))
        rows.append(dict(familia='perfil_%s_chapa' % fam, designacion=desig.rsplit('x', 1)[0] if False else (('C %dx%dx%d' % (h, b, c)) if fam == 'C' else ('U %dx%d' % (h, b))), h_mm=h, b_mm=b, pestana_mm=c, espesor_mm=e,
                         kg_por_m_lac=lac, kg_por_m_galv=galv, seccion_cm2=sec, kg_por_m_calc=round(sec * 100 * RHO / 1e6, 3), m2_por_m=round(2 * sec * 100 / e / 1000, 4), m2_origen='calculado',
                         norma='IRAM-IAS U500-206 (LAC) / U500-205 (galvanizado)', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS,
                         nota='Ferrara S.A. (distribuidor argentino), tabla "Perfiles %s" (largo 12 m). LAC = laminado en caliente. kg_por_m_calc = seccion*7,85/1000 (sin galvanizado). m2/m calculado = 2*seccion/espesor (desarrollo por las dos caras).' % fam))
    for r in rows:
        if r['fuente_nombre'] == N_FER and r['kg_por_m_lac'] and r['kg_por_m_calc']:
            dv = (r['kg_por_m_lac'] / r['kg_por_m_calc'] - 1) * 100
            if abs(dv) > 3: r['nota'] += ' ATENCION: kg/m LAC difiere %+.1f %% de seccion*7,85 (posible error en la seccion o en el peso de la tabla).' % dv
    print('   perfiles chapa sin monotonia:', flag_monotono(rows, lambda r: (r['fuente_nombre'], r['designacion']), lambda r: r['espesor_mm'], lambda r: r['kg_por_m_lac']))
    return write('estructura_perfiles_chapa.csv', cols, rows)

# ------------------------------------------------------------------ tubos
def tubo_rect_kg(a, b, t):
    # tubo cuadrado/rectangular con radio exterior 2t e interior t (IRAM-IAS U500-218): 4 lados rectos de largo (lado - 4t) + 4 cuartos de corona
    A = 2 * t * (a + b - 8 * t) + 3 * math.pi * t * t
    return A * RHO / 1e6

def tubos_inti():
    out = []
    with pdfplumber.open(INTI) as pdf:
        for pn in range(31, 47):
            page = pdf.pages[pn]; rows = rows_of(page)
            txt = page.extract_text() or ''
            if '[Kg/m]' not in txt: continue
            hdr = None
            for r in rows:
                tt = [w['text'] for w in r['w']]
                if tt[:3] in (['D', 't', 'p'], ['B', 't', 'p'], ['B', 'H', 't']): hdr = tt; break
            if not hdr: continue
            kind = {'D': 'redondo', 'B': 'cuadrado'}.get(hdr[0])
            if hdr[:2] == ['B', 'H']: kind = 'rectangular'
            nlab = 2 if kind == 'rectangular' else 1
            ncols = {'redondo': 10, 'cuadrado': 10, 'rectangular': 14}[kind]
            labels = []; data = []
            for r in rows:
                toks = [w['text'] for w in r['w'] if NUM.match(w['text'])]
                if len(toks) != len(r['w']): continue
                if len(toks) == ncols + nlab: labels.append((r['y'], toks[:nlab])); data.append((r['y'], toks[nlab:]))
                elif len(toks) == ncols: data.append((r['y'], toks))
                elif len(toks) == nlab: labels.append((r['y'], toks))
            for y, v in data:
                lab = min(labels, key=lambda l: abs(l[0] - y))
                out.append((kind, pn + 1, [num(x) for x in lab[1]], [num(x) for x in v]))
    return out

def tubos():
    cols = ['familia', 'designacion', 'a_mm', 'b_mm', 'espesor_mm', 'kg_por_m', 'kg_por_m_calc', 'm2_por_m', 'm2_origen', 'estado_material', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = []
    for kind, pg, lab, v in tubos_inti():
        if kind == 'redondo':
            D = lab[0]; t, p, Ag, g = v[0], v[1], v[2], v[3]
            des = 'Tubo redondo D%s x %s' % (fmt(D), fmt(t)); a, b = D, None
            calc = math.pi * (D - t) * t * RHO / 1e6
        elif kind == 'cuadrado':
            B = lab[0]; t, p, Ag, g = v[0], v[1], v[2], v[3]
            des = 'Tubo cuadrado %sx%s x %s' % (fmt(B), fmt(B), fmt(t)); a, b = B, B
            calc = None
        else:
            B, H = lab; t, p, Ag, g = v[0], v[1], v[2], v[3]
            des = 'Tubo rectangular %sx%s x %s' % (fmt(B), fmt(H), fmt(t)); a, b = B, H
            calc = None
        if kind in ('cuadrado', 'rectangular'):
            calc = tubo_rect_kg(a, b, t)
        rows.append(dict(familia='tubo_' + kind, designacion=des, a_mm=a, b_mm=b, espesor_mm=t, kg_por_m=g, kg_por_m_calc=round(calc, 3), m2_por_m=p, m2_origen='fuente',
                         estado_material='', norma='IRAM-IAS U 500-218 / U 500-2592', fuente_url=U_INTI, fuente_nombre=N_INTI, consultado=CONS,
                         nota='pagina PDF %d. m2/m = p de la fuente (area exterior por metro). kg_por_m_calc = formula del tubo con radios (redondo pi(D-e)e; cuadrado/rect. con radio exterior 2e segun la fuente), 7,85.' % pg))
    # Ternium Argentina
    with pdfplumber.open(pdfp('ternium_argentina_tubos_y_perfiles_2018.pdf')) as pdf:
        seen = {}
        for pn, uso in ((7, 'general'), (8, 'general'), (9, 'estructural')):
            page = pdf.pages[pn]; ws = page.extract_words()
            hdr = [w for w in ws if re.match(r'^\d,\d\d$', w['text']) and 90 < w['top'] < 106]
            cols_x = [((w['x0'] + w['x1']) / 2, num(w['text'])) for w in hdr]
            hay_liviano = any('Livianos' == w['text'] for w in ws)
            for r in rows_of(page, tol=3):
                if r['y'] < 104: continue
                wt = [w for w in r['w'] if re.match(r'^\d\.\d{3}$', w['text'])]
                if not wt: continue
                lab = [w for w in r['w'] if w not in wt]
                red = [w for w in lab if 60 < (w['x0'] + w['x1']) / 2 < 86 and re.match(r'^\d+\.\d+$', w['text'])]
                sq = [w for w in lab if re.match(r'^\d+(\.\d+)?x\d+(\.\d+)?$', w['text'])]
                kinds = []
                if red: kinds.append(('redondo', float(red[0]['text']), None))
                for s in sq:
                    a, b = [float(x) for x in s['text'].split('x')]
                    kinds.append(('cuadrado' if a == b else 'rectangular', a, b))
                if not kinds: continue
                for k, a, b in kinds:
                    for w in wt:
                        cxw = (w['x0'] + w['x1']) / 2
                        cx_, e = min(cols_x, key=lambda c: abs(c[0] - cxw))
                        if abs(cx_ - cxw) > 8: continue
                        frio = hay_liviano and cx_ < 240
                        key = (k, a, b, e, frio)
                        if key in seen:
                            if uso == 'estructural' and 'estructural' not in seen[key]['nota']:
                                seen[key]['nota'] += ' Ternium lo lista tambien en la tabla "uso estructural".'
                            continue
                        if k == 'redondo':
                            des = 'Tubo redondo D%s x %s' % (fmt(a), fmt(e)); calc = math.pi * (a - e) * e * RHO / 1e6
                        else:
                            des = 'Tubo %s %sx%s x %s' % (k, fmt(a), fmt(b), fmt(e))
                            calc = tubo_rect_kg(a, b, e)
                        kg = float(w['text'])
                        seen[key] = dict(familia='tubo_' + k, designacion=des, a_mm=a, b_mm=b, espesor_mm=e, kg_por_m=kg, kg_por_m_calc=round(calc, 3),
                                         m2_por_m=None, m2_origen='', estado_material='laminado en frio (liviano)' if frio else 'laminado en caliente sin decapar (semipesado)',
                                         norma='IRAM-IAS U500-2592 (Ternium)', fuente_url=U_TAR, fuente_nombre=N_TAR, consultado=CONS,
                                         nota='pagina PDF %d, tabla "tubos para uso %s" (peso por metro). Medidas comerciales de Ternium, largo 6 m.' % (pn + 1, uso))
        rows += list(seen.values())
    for fam, a, b, e, kg, kind in AR.fer_tubos(FER):
        if fam == 'tubo_redondo':
            des = 'Tubo redondo D%s x %s' % (fmt(a), fmt(e)); calc = math.pi * (a - e) * e * RHO / 1e6
        else:
            des = 'Tubo %s %sx%s x %s' % (fam.split('_')[1], fmt(a), fmt(b), fmt(e)); calc = tubo_rect_kg(a, b, e)
        rows.append(dict(familia=fam, designacion=des, a_mm=a, b_mm=b, espesor_mm=e, kg_por_m=kg, kg_por_m_calc=round(calc, 3), m2_por_m=None, m2_origen='',
                         estado_material='uso mecanico tipo agua' if kind == 'agua' else 'ERW conformado en frio (uso general y estructural)',
                         norma='IRAM-IAS U 500-2590 tipo I' if kind == 'agua' else 'IRAM-IAS U 500-228 / U 500-2592', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS,
                         nota='Ferrara S.A. (distribuidor argentino), pesos teoricos kg/m por espesor comercial (6 m; 12 m desde 5 1/2").' ))
    # tubos de uso mecanico (redondos laminados en caliente sin decapar), pagina 11 del PDF Ternium
    mec = [(60.33, 2.9, 4.107), (60.33, 3.2, 4.508), (76.2, 2.9, 5.242), (76.2, 3.2, 5.761), (76.2, 3.6, 6.446), (88.9, 3.2, 6.763), (88.9, 3.6, 7.573), (114.3, 3.6, 9.828), (114.3, 4.0, 10.881)]
    have = {(r['a_mm'], r['espesor_mm'], r['kg_por_m']) for r in rows if r['familia'] == 'tubo_redondo' and r['fuente_nombre'] == N_TAR}
    for D, e, kg in mec:
        if (D, e, kg) in have:
            for r in rows:
                if r['familia'] == 'tubo_redondo' and r['fuente_nombre'] == N_TAR and (r['a_mm'], r['espesor_mm'], r['kg_por_m']) == (D, e, kg):
                    r['nota'] += ' Ternium lo lista tambien en la tabla "tubos de uso mecanico".'
            continue
        rows.append(dict(familia='tubo_redondo', designacion='Tubo redondo D%s x %s' % (fmt(D), fmt(e)), a_mm=D, b_mm=None, espesor_mm=e, kg_por_m=kg,
                         kg_por_m_calc=round(math.pi * (D - e) * e * RHO / 1e6, 3), m2_por_m=None, m2_origen='', estado_material='uso mecanico, laminado en caliente sin decapar',
                         norma='IRAM-IAS U500-2590 Tipo I', fuente_url=U_TAR, fuente_nombre=N_TAR, consultado=CONS,
                         nota='pagina PDF 11, tabla "tubos de uso mecanico". Largo estandar 6.400 mm.'))
    for r in rows:
        if r['fuente_nombre'] in (N_TAR, N_FER) and r['familia'] in ('tubo_cuadrado', 'tubo_rectangular'):
            dv = (r['kg_por_m'] / r['kg_por_m_calc'] - 1) * 100
            r['nota'] += ' El peso de tubos cuadrados/rectangulares comerciales coincide con el del redondo de igual perimetro (no es el area real): %+.1f %% contra el calculo con radios.' % dv
    # m2/m calculado para los de Ternium: perimetro exterior
    for r in rows:
        if r['m2_origen'] == '':
            a, b = r['a_mm'], r['b_mm']
            per = math.pi * a if r['familia'] == 'tubo_redondo' else 2 * (a + b) - (8 - 2 * math.pi) * 2 * r['espesor_mm']
            r['m2_por_m'] = round(per / 1000, 4); r['m2_origen'] = 'calculado'
            r['nota'] += ' m2/m calculado = perimetro exterior (redondo pi*D; cuadrado/rect. 2(a+b) - (8-2pi)*Re con Re=2e).'
    for r in rows:
        if r['fuente_nombre'] in (N_TAR, N_FER) and r['familia'] in ('tubo_cuadrado', 'tubo_rectangular'):
            D = 2 * (r['a_mm'] + r['b_mm']) / math.pi
            eq = math.pi * (D - r['espesor_mm']) * r['espesor_mm'] * RHO / 1e6
            dv = (r['kg_por_m'] / eq - 1) * 100
            if dv < -6 or dv > 6:
                r['nota'] += ' ATENCION: difiere %+.1f %% del redondo de igual perimetro (lo normal en esta serie es -3 a +5 %%); %s.' % (dv, 'Ternium asigna el peso de la familia 1" a esta medida' if r['fuente_nombre'] == N_TAR else 'posible error de tipeo de la fuente')
    print('   tubos sin monotonia:', flag_monotono(rows, lambda r: (r['fuente_nombre'], r['familia'], r['a_mm'], r['b_mm'], r['estado_material'][:12]), lambda r: r['espesor_mm'], lambda r: r['kg_por_m']))
    return write('estructura_tubos.csv', cols, rows)

# ------------------------------------------------------------------ chapas
def norte_semilla():
    out = []
    with pdfplumber.open(pdfp('acerosnorte_chapa_semilla_de_melon_pesos.pdf')) as pdf:
        page = pdf.pages[0]; ws = page.extract_words(); rows = AR.rows_of_words(ws, 3)
        heads = [(( w['x0'] + w['x1']) / 2) for w in ws if w['text'] in ('1220', '1245', '1500') and w['top'] < 135]
        dims = {1220: (1220, 2440), 1245: (1245, 2440), 1500: (1500, 3000)}
        hx = [((w['x0'] + w['x1']) / 2, int(w['text'])) for w in ws if w['text'] in ('1220', '1245', '1500') and w['top'] < 135]
        for r in rows:
            lab = [w for w in r if re.match(r'^\d,\d{1,2}$', w['text']) and 200 < w['x0'] < 240]
            if not lab: continue
            e = num(lab[0]['text'])
            for w in r:
                if w['x0'] > 260 and NUM.match(w['text']):
                    cx = (w['x0'] + w['x1']) / 2
                    c = min(hx, key=lambda c: abs(c[0] - cx))
                    out.append((e, dims[c[1]][0], dims[c[1]][1], num(w['text'])))
    return out

def chapas():
    cols = ['familia', 'designacion', 'espesor_mm', 'hoja_mm', 'kg_por_hoja', 'malla_mm', 'kg_por_m2', 'kg_por_m2_fuente', 'tipo_dato', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = []
    seenE = {}
    # 1) chapa lisa: pesos por hoja del catalogo Ferrara -> kg/m2 de la fuente; kg/m2 = e*7,85 (calculado)
    from collections import defaultdict
    der = defaultdict(list)
    for kgh, a_, l_, e in AR.fer_chapas_lisas(FER):
        der[e].append(kgh / (a_ * l_ / 1e6))
    for e in sorted(der):
        calc = round(e * RHO / 1000, 3)
        med = sorted(der[e])[len(der[e]) // 2]
        rows.append(dict(familia='chapa_lisa', designacion='Chapa lisa e=%s mm' % fmt(e), espesor_mm=e, kg_por_m2=calc, kg_por_m2_fuente=round(med, 3), tipo_dato='calculado',
                         norma='densidad 7.850 kg/m3', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS,
                         nota='kg_por_m2 = espesor_mm*7,85 (calculado). kg_por_m2_fuente = peso por hoja del catalogo Ferrara (hojas laminadas en frio y caliente, %d medidas) dividido el area; coincide con el calculo (desvio maximo %+.2f %%).' % (len(der[e]), max([(x / calc - 1) * 100 for x in der[e]], key=abs))))
        seenE[round(e, 2)] = 1
    # 2) tabla Fabrica do Projeto: espesores que Ferrara no trae
    for c in html_rows('fabricadoprojeto_tabela-de-chapa-lisa-fina-e-grossa.html')[1:]:
        if len(c) < 4 or c[1] not in ('GSC', 'Pol.'): continue
        try: e = float(c[2].replace(',', '.')); kgf = float(c[3].replace(',', '.'))
        except: continue
        if c[1] == 'Pol.' and e > 40: continue
        if round(e, 2) in seenE: continue
        seenE[round(e, 2)] = 1
        calc = round(e * RHO / 1000, 3)
        ds = abs(kgf - calc) / calc * 100
        rows.append(dict(familia='chapa_lisa', designacion='Chapa lisa e=%s mm' % fmt(e), espesor_mm=e, kg_por_m2=calc, kg_por_m2_fuente=kgf, tipo_dato='calculado', norma='densidad 7.850 kg/m3',
                         fuente_url=U_FDP.format('tabela-de-chapa-lisa-fina-e-grossa'), fuente_nombre=N_FDP, consultado=CONS,
                         nota='espesor de la tabla brasilera (%s %s). kg_por_m2 = espesor_mm*7,85 (calculado); kg_por_m2_fuente es la columna de la tabla (usa 8,0 kg/m2 por mm en calibres hasta 4,75 mm y 7,85 en pulgadas)%s.' % ('calibre' if c[1] == 'GSC' else 'pulgada', c[0].replace('.1/', ' 1/').replace('.3/', ' 3/'), ': desvio %+.1f%% contra 7,85' % (kgf / calc * 100 - 100) if ds > 1 else '')))
    # 3) semilla de melon y estampada (Ferrara) + Aceros Norte
    for sec, kgh, a_, l_, e in AR.fer_semilla(FER):
        m2 = round(kgh / (a_ * l_ / 1e6), 3); flat = e * RHO / 1000
        fam = 'chapa_semilla_melon' if sec == 'semilla' else 'chapa_estampada'
        rows.append(dict(familia=fam, designacion=('Chapa semilla de melon' if sec == 'semilla' else 'Chapa estampada antideslizante') + ' e=%s mm hoja %dx%d' % (fmt(e), a_, l_), espesor_mm=e, hoja_mm='%dx%d' % (a_, l_), kg_por_hoja=kgh,
                         kg_por_m2=m2, tipo_dato='calculado', norma='chapa antideslizante laminada', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS,
                         nota='kg_por_m2 calculado = peso por hoja de la tabla / (ancho*largo). Es %+.1f %% contra la chapa lisa del mismo espesor (7,85*e = %s). El peso por hoja es el de la fuente (aproximado).' % ((m2 / flat - 1) * 100, fmt(round(flat, 2)))))
    for e, a_, l_, kgh in norte_semilla():
        m2 = round(kgh / (a_ * l_ / 1e6), 3); flat = e * RHO / 1000
        rows.append(dict(familia='chapa_semilla_melon', designacion='Chapa semilla de melon e=%s mm hoja %dx%d' % (fmt(e), a_, l_), espesor_mm=e, hoja_mm='%dx%d' % (a_, l_), kg_por_hoja=kgh,
                         kg_por_m2=m2, tipo_dato='calculado', norma='chapa antideslizante laminada', fuente_url=U_NOR, fuente_nombre=N_NOR, consultado=CONS,
                         nota='kg_por_m2 calculado = peso aproximado por hoja de la tabla / (ancho*largo); la fuente rotula la ultima medida "1500 X 300" (se leyo 1500x3000 por el peso). Es %+.1f %% contra la chapa lisa del mismo espesor (%s).' % ((m2 / flat - 1) * 100, fmt(round(flat, 2)))))
    xad = []
    for c in html_rows('fabricadoprojeto_tabela-de-chapa-xadrez.html')[1:]:
        if len(c) < 3: continue
        try: e = float(c[1].replace(',', '.')); kg = float(c[2].replace(',', '.'))
        except: continue
        calc = e * RHO / 1000
        rows.append(dict(familia='chapa_xadrez', designacion='Chapa xadrez/lagrimada (Brasil) e=%s mm' % fmt(e), espesor_mm=e, kg_por_m2=kg, kg_por_m2_fuente=kg, tipo_dato='fuente',
                         norma='chapa de piso laminada (Brasil)', fuente_url=U_FDP.format('tabela-de-chapa-xadrez-chapa-piso'), fuente_nombre=N_FDP, consultado=CONS,
                         nota='peso teorico de la fuente brasilera (incluye relieve; %+.1f %% contra la chapa lisa del mismo espesor). Referencia secundaria: para semilla de melon argentina usar las filas chapa_semilla_melon.' % (kg / calc * 100 - 100)))
    # 4) metal desplegado
    seen = set()
    for D, d, E, H, kg in AR.fer_desplegado(FER):
        k = (D, d, E, H)
        if k in seen: continue
        seen.add(k)
        rows.append(dict(familia='metal_desplegado', designacion='Metal desplegado D%s d%s E%s H%s' % (fmt(D), fmt(d), fmt(E), fmt(H)), espesor_mm=E, malla_mm='D=%s x d=%s, nervio H=%s' % (fmt(D), fmt(d), fmt(H)), kg_por_m2=kg, kg_por_m2_fuente=kg, tipo_dato='fuente',
                         norma='fabricante', fuente_url=U_FER, fuente_nombre=N_FER, consultado=CONS,
                         nota='Ferrara S.A. (distribuidor argentino), tabla "Metales desplegables": D = diagonal mayor, d = diagonal menor, E = espesor, H = nervio (mm); peso en kg/m2 de la fuente.'))
    for c in html_rows('fabricadoprojeto_tabela-de-chapa-expandida-exp-gme.html')[1:]:
        if len(c) < 8 or not re.match(r'^(EXP|GME)', c[0]): continue
        try: e = float(c[4].replace(',', '.')); kg = float(c[7].replace(',', '.'))
        except: continue
        nota = 'tabla Fabrica do Projeto (peso aproximado); malla A x B (mm) = %s; cuerda %s mm; area abierta %s%%.' % (c[1], c[5], c[6])
        if kg > 12 and c[0].startswith('EXP-5B'): nota += ' ATENCION: peso 28 incoherente con las mallas vecinas (1,5 a 2); posible error de la fuente.'
        rows.append(dict(familia='metal_desplegado', designacion='Metal desplegado %s %s' % (c[0], c[1]), espesor_mm=e, malla_mm=c[1].replace('Mesh ', '').replace(' mesh', ''), kg_por_m2=kg, kg_por_m2_fuente=kg, tipo_dato='fuente',
                         norma='fabricante brasilero (GME)', fuente_url=U_FDP.format('tabela-de-chapa-expandida-exp-gme'), fuente_nombre=N_FDP, consultado=CONS, nota=nota))
    import subprocess
    for fn, code in (('distriplac_mallexpan_romboidal_3.pdf', '31076894532'), ('distriplac_mallexpan_romboidal_1.pdf', '31076894581'), ('distriplac_mallexpan_romboidal_2.pdf', '31076894611')):
        t = subprocess.run(['pdftotext', '-layout', pdfp(fn), '-'], capture_output=True, text=True).stdout
        mod = re.search(r'EQ\d+', t).group(0)
        dis = re.search(r'Dise.o expandido\s+([\d x,\-]+)\s*\(mm\)', t).group(1).strip()
        kg = num(re.search(r'Peso\s+([\d,]+)\s*\(Kg/m2\)', t).group(1)); e = num(re.search(r'Espesor\s+([\d,]+)\s*\(mm\)', t).group(1))
        tr = num(re.search(r'Transparencia\s+(\d+)', t).group(1))
        rows.append(dict(familia='metal_desplegado', designacion='Metal desplegado romboidal %s' % mod, espesor_mm=e, malla_mm=dis, kg_por_m2=kg, kg_por_m2_fuente=kg, tipo_dato='fuente',
                         norma='Mallexpan', fuente_url=U_DIS.format(code), fuente_nombre=N_DIS, consultado=CONS, nota='disenio expandido %s mm, transparencia %s%%.' % (dis, fmt(tr))))
    return write('estructura_chapas.csv', cols, rows)

# ------------------------------------------------------------------ inox
def inox():
    import subprocess
    t = subprocess.run(['pdftotext', '-layout', pdfp('cedinox_tables_technical_properties.pdf'), '-'], capture_output=True, text=True).stdout
    cols = ['grado_en', 'grado_aisi', 'densidad_kg_dm3', 'densidad_kg_m3', 'norma', 'fuente_url', 'fuente_nombre', 'consultado', 'nota']
    rows = []; seen = set()
    start = t.find('Physical properties of stainless steels')
    for ln in t[start:].split('\n'):
        m = re.match(r'^\s*(1\.\d{4})\s+(?:(\S+?)\s+)?(\d,\d+)\s+(\d{2,3})\s+\d', ln)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            d = num(m.group(3))
            rows.append(dict(grado_en=m.group(1), grado_aisi=m.group(2) or '', densidad_kg_dm3=d, densidad_kg_m3=int(round(d * 1000)), norma='EN 10088', fuente_url=U_CED, fuente_nombre=N_CED,
                             consultado=CONS, nota='tabla "Physical properties of stainless steels", densidad a 20 C. Factor sobre acero al carbono (7,85): %.3f' % (d / 7.85)))
    return write('estructura_inox_densidad.csv', cols, rows)

if __name__ == '__main__':
    perfiles(); angulos(); planchuelas(); barras(); perfiles_chapa(); tubos(); chapas(); inox()
