"""Lector mínimo de .msg (OLE CFB) con la biblioteca estándar: cuerpo y adjuntos."""
import struct, sys, os

def cfb(path):
    d = open(path, 'rb').read()
    ss = 1 << struct.unpack_from('<H', d, 30)[0]
    mss = 1 << struct.unpack_from('<H', d, 32)[0]
    nfat = struct.unpack_from('<I', d, 44)[0]
    dir0 = struct.unpack_from('<I', d, 48)[0]
    cutoff = struct.unpack_from('<I', d, 56)[0]
    minifat0 = struct.unpack_from('<I', d, 60)[0]
    difat0, ndifat = struct.unpack_from('<II', d, 68)
    sec = lambda n: d[512 + n * ss: 512 + (n + 1) * ss]
    difat = list(struct.unpack_from('<109I', d, 76))
    n = difat0
    for _ in range(ndifat):
        s = sec(n); vals = struct.unpack('<%dI' % (ss // 4), s)
        difat += vals[:-1]; n = vals[-1]
    fat = []
    for f in difat[:nfat]:
        fat += struct.unpack('<%dI' % (ss // 4), sec(f))
    def chain(n):
        out = []
        while n < 0xFFFFFFFA:
            out.append(n); n = fat[n]
        return out
    rd = lambda n: b''.join(sec(x) for x in chain(n))
    dirs = rd(dir0)
    ents = []
    for i in range(len(dirs) // 128):
        e = dirs[i * 128:(i + 1) * 128]
        nl = struct.unpack_from('<H', e, 64)[0]
        name = e[:max(nl - 2, 0)].decode('utf-16le', 'replace')
        typ = e[66]
        l, r, c = struct.unpack_from('<III', e, 68)
        start, size = struct.unpack_from('<IQ', e, 116)
        ents.append(dict(name=name, typ=typ, l=l, r=r, c=c, start=start, size=size & 0xFFFFFFFF))
    root = ents[0]
    ministream = rd(root['start'])
    minifat = []
    if minifat0 < 0xFFFFFFFA:
        mf = rd(minifat0); minifat = list(struct.unpack('<%dI' % (len(mf) // 4), mf))
    def data(e):
        if e['size'] < cutoff:
            out = []; n = e['start']
            while n < 0xFFFFFFFA:
                out.append(ministream[n * mss:(n + 1) * mss]); n = minifat[n]
            return b''.join(out)[:e['size']]
        return rd(e['start'])[:e['size']]
    def kids(i):
        res = []
        def walk(j):
            if j >= 0xFFFFFFFA or j >= len(ents): return
            walk(ents[j]['l']); res.append(j); walk(ents[j]['r'])
        walk(ents[i]['c']); return res
    return ents, kids, data

def props(ents, kids, data, i):
    p = {}
    for k in kids(i):
        n = ents[k]['name']
        if n.startswith('__substg1.0_'):
            p[n[12:]] = data(ents[k])
    return p, [k for k in kids(i) if ents[k]['typ'] == 1]

def txt(p, tag):
    if tag + '001F' in p: return p[tag + '001F'].decode('utf-16le', 'replace')
    if tag + '001E' in p: return p[tag + '001E'].decode('latin-1', 'replace')
    return None

def guardar(ents, kids, data, i, out, nivel=0):
    p, subs = props(ents, kids, data, i)
    pre = '  ' * nivel
    print(pre + 'Asunto:', txt(p, '0037'))
    print(pre + 'De:', txt(p, '0C1A'), txt(p, '0065') or '')
    print(pre + 'Para:', txt(p, '0E04'))
    print(pre + 'CC:', txt(p, '0E03'))
    body = txt(p, '1000')
    if body:
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, 'cuerpo.txt'), 'w').write(body)
        print(pre + '--- cuerpo (%d car.) ---' % len(body)); print(body[:4000])
    for s in subs:
        if ents[s]['name'].startswith('__attach'):
            ap, asubs = props(ents, kids, data, s)
            nombre = txt(ap, '3707') or txt(ap, '3704') or ents[s]['name']
            if '37010102' in ap:
                os.makedirs(out, exist_ok=True)
                open(os.path.join(out, nombre), 'wb').write(ap['37010102'])
                print(pre + 'ADJUNTO', nombre, len(ap['37010102']))
            else:
                emb = [k for k in kids(s) if ents[k]['name'] == '__substg1.0_3701000D']
                if emb:
                    print(pre + 'MENSAJE ADJUNTO', nombre)
                    guardar(ents, kids, data, emb[0], os.path.join(out, nombre.replace('/', '_')), nivel + 1)

if __name__ == '__main__':
    ents, kids, data = cfb(sys.argv[1])
    guardar(ents, kids, data, 0, sys.argv[2])
