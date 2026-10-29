import re
NUM=re.compile(r'^-?\d+([.,]\d+)?$')
def num(s):
    s=s.strip().replace('*','')
    if re.match(r'^-?\d{1,3}(\.\d{3})+,\d+$',s): s=s.replace('.','').replace(',','.')
    else: s=s.replace(',','.')
    return float(s)
def rows_of(page,tol=2.5):
    ws=sorted(page.extract_words(),key=lambda w:(round(w['top']),w['x0']))
    rows=[]
    for w in ws:
        if rows and abs(rows[-1]['y']-w['top'])<=tol: rows[-1]['w'].append(w)
        else: rows.append({'y':w['top'],'w':[w]})
    for r in rows: r['w'].sort(key=lambda w:w['x0'])
    return rows
def near(r,x,tol=12):
    c=[w for w in r['w'] if NUM.match(w['text']) and abs((w['x0']+w['x1'])/2-x)<=tol]
    return min(c,key=lambda w:abs((w['x0']+w['x1'])/2-x)) if c else None
