import sys; sys.path.insert(0,'py')
import pdfplumber
from common import *
def angulos_inti(path='inti.pdf'):
    out=[]
    with pdfplumber.open(path) as pdf:
        for pn in (28,29):
            pg=pdf.pages[pn]; ws=pg.extract_words()
            kg=[w for w in ws if w['text']=='Kg/m' and w['top']<300][0]
            mm=sorted([w for w in ws if w['text']=='mm' and abs(w['top']-kg['top'])<4],key=lambda w:w['x0'])
            cx=lambda w:(w['x0']+w['x1'])/2
            bx,tx,px=cx(mm[0]),cx(mm[1]),cx(kg)
            for r in rows_of(pg):
                if r['y']<=kg['top']+5: continue
                b=near(r,bx,9); t=near(r,tx,9); p=near(r,px,9)
                if b and t and p: out.append((pn+1,num(b['text']),num(t['text']),num(p['text'])))
    return out
if __name__=='__main__':
    o=angulos_inti(); 
    for x in o: print(x)
    print(len(o))
