"""Pasa las listas de listas_preliminares.py a pedido/lista_materiales_plano.csv (la tabla que lee el cotizador).

Cantidades POR FILTRO (N = 2 en cotizacion.json). El cliente no da lista de materiales (solo la tabla del plano
PL-001, referencial): todo es diseño ITT con el P&ID, la HD y las clases L0200, y así lo dice cantidad_origen.
Uso: python cotizaciones/COT26-0010-002_AESA_C5297_FILTROS_COALESCEDORES/lista_a_cotizador.py
"""
import csv
import importlib.util
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('lp', os.path.join(AQUI, 'listas_preliminares.py'))
L = importlib.util.module_from_spec(sp)
sp.loader.exec_module(L)

COLS = ['pos', 'descripcion', 'diametro', 'serie_sch', 'material', 'extremos', 'modelo_fabricante', 'cantidad', 'unidad',
        'extremos_campo', 'cantidad_origen', 'nota', 'familia', 'tipo', 'diametro2', 'serie', 'schedule', 'espesor_mm', 'cara',
        'norma', 'marca', 'modelo', 'rango', 'trim', 'paso', 'costura', 'revestimiento', 'largo_mm', 'medida']
ORIGEN = 'El cliente no indica cantidad: calculada por ITT según el P&ID 5297-02-0000-IG-PR-PI-005, la HD-001 y el plano PL-001'
filas = []


def fila(desc, cant, un, fam, **k):
    r = {c: '' for c in COLS}
    r.update(descripcion=desc, cantidad=cant, unidad=un, familia=fam, cantidad_origen=ORIGEN)
    r.update(k)
    r['pos'] = str(len(filas) + 1)
    filas.append(r)


def dn(t):
    return t.split(' ')[0] if t else ''


# 1. Recipiente: chapas y piezas soldadas por kg; bridas y cuellos como piezas
for desc, med, mat, cant, un, kg, orig in L.RECIPIENTE:
    d = desc.lower()
    if 'brida' in d:
        continue  # van abajo con su Ø y serie
    fila(desc, round(kg, 2), 'kg', 'PER', material=mat, tipo='chapa', espesor_mm=med, nota=f'Recipiente FC. {orig}')
fila('Brida WN 32" #600 B16.47 Serie A (M1)', 1, 'un', 'BRI', diametro='32"', serie_sch='600', material='SA-105', extremos='RF', tipo='WN', serie='600', cara='RF', norma='ASME B16.47', nota='Recipiente FC (HD)')
fila('Brida ciega 32" #600 B16.47 Serie A (M1) con pescante', 1, 'un', 'BRI', diametro='32"', serie_sch='600', material='SA-105', tipo='ciega', serie='600', cara='RF', norma='ASME B16.47', nota='Recipiente FC (HD nota 22)')
fila('Brida WN 20" #600 (MH)', 1, 'un', 'BRI', diametro='20"', serie_sch='600', material='SA-105', extremos='RF', tipo='WN', serie='600', cara='RF', norma='ASME B16.5', nota='Recipiente FC (HD)')
fila('Brida ciega 20" #600 (MH) con pescante', 1, 'un', 'BRI', diametro='20"', serie_sch='600', material='SA-105', tipo='ciega', serie='600', cara='RF', norma='ASME B16.5', nota='Recipiente FC (HD nota 22)')
fila('Brida WN 10" #600 (A, B1)', 2, 'un', 'BRI', diametro='10"', serie_sch='600', material='SA-105', extremos='RF', tipo='WN', serie='600', cara='RF', schedule='160', norma='ASME B16.5', nota='Recipiente FC (HD)')
fila('Brida WN 4" #600 (R1, R2)', 2, 'un', 'BRI', diametro='4"', serie_sch='600', material='SA-105', extremos='RF', tipo='WN', serie='600', cara='RF', schedule='160', norma='ASME B16.5', nota='Recipiente FC (HD)')
fila('Brida ciega 4" #600 (R1, R2)', 2, 'un', 'BRI', diametro='4"', serie_sch='600', material='SA-105', tipo='ciega', serie='600', cara='RF', norma='ASME B16.5', nota='Recipiente FC (HD)')
fila('Brida WN 2" #600 (boquillas B2, B3, D, J1, J2, L1–L12, P1, P2, S)', 20, 'un', 'BRI', diametro='2"', serie_sch='600', material='SA-105', extremos='RF', tipo='WN', serie='600', cara='RF', schedule='160', norma='ASME B16.5', nota='Recipiente FC (HD nota 19: mín. Sch 160)')
fila('Caño cuello 10" Sch 160 (A, B1)', 0.6, 'm', 'CAN', diametro='10"', serie_sch='160', material='SA-106 Gr. B', schedule='160', costura='sin costura', nota='Recipiente FC')
fila('Caño cuello 4" Sch 160 (R1, R2)', 0.4, 'm', 'CAN', diametro='4"', serie_sch='160', material='SA-106 Gr. B', schedule='160', costura='sin costura', nota='Recipiente FC')
fila('Caño cuello 2" Sch 160 (20 boquillas)', 4, 'm', 'CAN', diametro='2"', serie_sch='160', material='SA-106 Gr. B', schedule='160', costura='sin costura', nota='Recipiente FC')

# 2. Piping
for c, m in zip(L.CANOS, L.CANOS_META):
    if not m:
        fila(f'{c[0]} {c[1]} {c[2]} {c[3]}', c[5], 'un', 'NIP', diametro='1/2"', serie_sch='160', material=c[3], extremos='NPT', schedule='160', nota=c[6])
        continue
    fila(f'{c[0]} {c[1]} {c[2]} {c[3]}', c[5], 'm', 'CAN', diametro=c[1], serie_sch=m[1], material=c[3], extremos='BW', schedule=m[1], costura='sin costura', nota=f'{c[4]}: {c[6]}')
for a, m in zip(L.ACCESORIOS, L.ACC_META):
    tipo, d1, d2, cl, ext, schr, *_ = m
    fam = 'ABW' if ext == 'BW' else 'AFO'
    fila(f'{a[0]} {a[1]} {a[2]} {a[3]}', a[5], 'un', fam, diametro=a[1].split(' × ')[0] if '×' in a[1] else a[1], diametro2=(a[1].split(' × ')[1] if '×' in a[1] else ''),
         serie_sch=(schr or cl), material=a[3], extremos=ext, tipo=tipo.replace('_', ' '), schedule=(schr or ''), serie=(cl if ext != 'BW' else ''), nota=a[4])
for b, m in zip(L.BRIDAS, L.BRI_META):
    tipo, d1, serie, sch, n_bw, n_sw = m
    fila(f'{b[0]} {b[1]} #{serie} {b[4]}', b[6], 'un', 'BRI', diametro=b[1], serie_sch=serie, material=b[4],
         extremos=('BW' if n_bw else ('SW' if n_sw else '')), tipo={'orificio': 'portaplaca'}.get(tipo, tipo), serie=serie, cara='RF', schedule=sch or '', nota=b[5])

# 3. Válvulas
for v in L.VALVULAS:
    fila(f'{v[1]} {v[2]} {v[3]} ({v[0]})', v[5], 'un', 'VAL', diametro=v[2], serie_sch=v[3].replace('#', '').replace(' RF', ''),
         extremos=('NPT' if 'NPT' in v[3] else 'RF'), tipo=v[1].lower(), nota=f'{v[4]}: {v[6]}. {v[7]}')
for v in L.VALVULAS_ACTUADAS:
    fila(f'{v[0]}: {v[1]} {v[2]} {v[3]}', v[5], 'un', 'VAL', diametro=v[2], serie_sch=v[3], tipo=v[1].split(',')[0].lower(), nota=f'{v[4]}: {v[6]}. {v[7]}')

# 4. Instrumentos
for i in L.INSTRUMENTOS:
    fila(f'{i[0]}: {i[1]}', 1, 'un', 'INS', tipo=i[1].split(' (')[0].lower(), nota=f'{i[2]} · {i[3]} · {i[4]}')

# 5. Juntas y bulonería
for d, s, n, junta, esp, por, med, donde in L.JUNTAS:
    if 'provee el instrumentista' in junta:
        continue  # vienen con el LIT (P&ID nota 9)
    fila(f'Junta {junta} {d} #{s}', n, 'un', 'JUN', diametro=d, serie=s, tipo='junta espiralada', nota=donde)
    fila(f'Espárrago con 2 tuercas {esp} {med} ({d} #{s})', n * por, 'un', 'JUN', diametro=med.split(' ×')[0], tipo='esparrago', material=esp, medida=med, nota=donde)

# 6. Elementos filtrantes del equipo (los de repuesto van en las posiciones RCP y RDO)
for desc, cant, un, va, orig in L.FILTRANTES:
    if va == 'Equipo':
        fila(desc, cant, un, 'OTR', tipo='elemento filtrante', nota=orig)

# 7. Estructura del skid (plano) y otros
for pos, cant, desc, kg, _ in L.LDM_PLANO:
    if pos in ('1000', '1500', '1900'):
        fila(f'{desc} (plano PL-001 pos. {pos})', round(kg * cant, 2), 'kg', 'PER', tipo='estructura', material='SA-36 / IRAM F24', nota='Peso del plano PL-001')
fila('Batea de contención chapa 4,76 mm A36 con descarga a OD', 300, 'kg', 'PER', tipo='estructura', material='SA-36', nota='RI §2; ITT')
fila('Soportes de cañería (típicos 5165-02-0000-IG-PI-TM-001)', 250, 'kg', 'PER', tipo='estructura', material='SA-36', nota='RI §9; ITT')
fila('Tubing inox 1/2" con conectores (aire e impulsos)', 45, 'm', 'OTR', tipo='tubing', nota='P&ID; ITT')
fila('Chapas de TAG AISI 316', 60, 'un', 'OTR', tipo='chapa de identificacion', nota='RI §2')
fila('Caja de conexionado Ex de instrumentos (analógicas/digitales, SIS/SCP)', 4, 'un', 'OTR', tipo='caja de conexionado', nota='RI §2 (la RI pide 4; el plano dibuja 3)')
fila('Caja de conexionado Ex de potencia del traceado', 1, 'un', 'OTR', tipo='caja de conexionado', nota='Plano pos. 601')
fila('Cables, conduit, bandeja y prensacables Ex (canalizaciones del skid)', 1, 'gl', 'OTR', tipo='canalizaciones electricas', nota='Plano pos. 2000; P1100/P1102/P1103')
fila('Traceado eléctrico autorregulado (4 circuitos con termostato)', 1, 'gl', 'OTR', tipo='traceado electrico', nota='HD nota 10; P0103')
fila('Aislación lana mineral 60 mm + chapa de aluminio 1 mm (recipiente y líneas traceadas)', 1, 'gl', 'OTR', tipo='aislacion', nota='HD nota 10; N0100')

with open(os.path.join(AQUI, 'pedido', 'lista_materiales_plano.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    w.writerows(filas)
print(f'OK: {len(filas)} renglones en pedido/lista_materiales_plano.csv')
