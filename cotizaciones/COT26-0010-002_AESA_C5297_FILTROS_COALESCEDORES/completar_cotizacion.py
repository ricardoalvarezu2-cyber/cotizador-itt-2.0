"""Arma cotizacion.json desde cotizacion_auto.json (precotizar.py): encabezado, precios que faltan y MO por rubro.

Criterio (Matías, 26-11-2026: cotizar con la app y ahorrar tokens, sin auditorías):
- Lo que el catálogo no tiene se toma de la planilla de costo de TAVAL/37 (FC-231 YPF, 32" #600 con skids, 17-12-2025),
  el antecedente con el mismo alcance; si no está ahí, ESTIMADO marcado (pedir cotización).
- Baja temperatura (A333-6, A350 LF2, A420 WPL6, A320 L7): precio de acero al carbono × 1,3 (criterio ITT, estimado).
- MO y servicios por rubro: los de TAVAL/37 (mismo tipo y tamaño de equipo); las pulgadas equivalentes del
  informe quedan como dato.
Uso: python cotizaciones/COT26-0010-002_AESA_C5297_FILTROS_COALESCEDORES/completar_cotizacion.py
"""
import copy
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
TAVAL37 = ('fuentes_originales/ofertas_texto/TAVAL/37- Doc5449458609 - RFP 1 Sobre - Filtro Coales (COMPRA)/'
           '4.Armado de la Oferta Comercial/LM costos Coalescedor FC-231 YPF - PC0-C (REV. 0).xlsx.txt')
F37 = '2025-12-17'


def ant(precio, que, dif):
    return {'tipo': 'ant', 'precio': precio, 'proveedor': f'Planilla de costo TAVAL/37 FC-231 YPF (PC0-C rev. 0): {que}',
            'origen': TAVAL37, 'fecha': F37, 'coincide': 'similar', 'diferencia': dif}


SIN_REF = {'10', '49', '63', '103', '116', '136',
           '26', '27', '28', '29', '30', '33', '40', '41', '42', '43', '44', '45', '51', '62', '64', '65', '66', '67',  # baja temperatura
           '55', '57', '121', '123', '127'}  # thredolets 6000# y espárragos L7: sin referencia compatible  # sin pieza parecida: precio 0 y pedir cotización (P4 ter)


def est(precio, que):
    """Estimado sobre una pieza parecida (acero al carbono equivalente o pieza de TAVAL/37): similar con su diferencia."""
    return {'tipo': 'est', 'precio': precio, 'proveedor': f'ESTIMADO ITT: {que}. Pedir cotización', 'origen': 'criterio ITT (COT26-0010-002, 26-11-2026)',
            'fecha': '2026-11-26', 'coincide': 'similar', 'diferencia': que}


LT = 'acero al carbono × 1,3 por baja temperatura'
# pos → fuente de base (las del catálogo quedan después como alternativas)
PRECIOS = {
    '10': est(20.0, 'orejas de PAT AISI 304L, USD/kg'),
    '12': ant(50.0, 'chapa de identificación AISI 316 a USD 15 c/u; placa con soporte 3 kg', 'placa C0100 con soporte'),
    '26': est(97.5, f'caño 4" Sch 80 A333-6: USD 75/m de TAVAL/37 (A106) {LT}'),
    '27': est(127.4, f'caño 6" Sch 80 A333-6: USD 98/m de TAVAL/37 (A106) {LT}'),
    '28': est(195.0, f'caño 8" Sch 40 A333-6: USD 150/m {LT}'),
    '29': est(91.0, f'caño 6" Sch 40 A333-6: USD 70/m {LT}'),
    '30': est(45.5, f'caño 3" Sch 40 A333-6: USD 35/m {LT}'),
    '33': est(19.5, f'caño 1" Sch 80 A333-6: USD 15/m de TAVAL/37 {LT}'),
    '38': ant(750.0, 'te normal 10" Sch 80 WPB USD 750', 'te de reducción 10"×4" en lugar de te normal 10"'),
    '40': est(120.0, f'reducción 6"×4" Sch 80 WPL6 {LT}'),
    '41': est(200.0, f'codo 8" Sch 40 WPL6 {LT}'),
    '42': est(350.0, f'te 8" Sch 40 WPL6 {LT}'),
    '43': est(110.0, f'codo 6" Sch 40 WPL6 {LT}'),
    '44': est(80.0, f'reducción 6"×3" Sch 40 WPL6 {LT}'),
    '45': est(30.0, f'reducción 3"×2" Sch 40 WPL6 {LT}'),
    '49': est(25.0, 'casquete 2" Sch 160 WPB'),
    '51': est(20.0, f'codo SW 1" 3000# LF2 {LT}'),
    '55': ant(25.0, 'threadolet 3/4" 3000# USD 20', 'serie 6000# y 1/2" (a verificar)'),
    '57': ant(25.0, 'threadolet 3/4" 3000# USD 20', 'serie 6000#'),
    '59': ant(6.5, 'tapón hexagonal 1/2" USD 5 y 3/4" USD 8', 'promedio de 1/2" y 3/4"'),
    '62': est(71.5, f'brida WN 4" #600 LF2: USD 55 de TAVAL/37 (A105) {LT}'),
    '63': est(600.0, 'par de bridas portaplaca 4" #600 B16.36 LF2'),
    '64': est(156.0, f'brida WN 6" #600 LF2: USD 120 de TAVAL/37 (A105) {LT}'),
    '65': est(60.0, f'brida WN 6" #150 LF2 {LT}'),
    '66': est(90.0, f'brida WN 8" #150 LF2 {LT}'),
    '67': est(23.4, f'brida WN 2" #150 LF2: USD 18 de TAVAL/37 (A105) {LT}'),
    '84': ant(274.95, 'VALVULA ESFERICA Ø 2 - Esf PT RF 600# USD 274,95', 'igual (esférica paso total 2" #600 RF)'),
    '97': est(4000.0, 'válvula de control 2" #600 con actuador y posicionador (TAVAL/37: 1" #600 USD 2.000)'),
    '98': est(4000.0, 'válvula de control 2" #600 con actuador y posicionador (TAVAL/37: 1" #600 USD 2.000)'),
    '103': est(800.0, 'placa orificio de restricción 4" con cálculo (dimensiona AESA)'),
    '108': ant(2200.0, 'LG 231A USD 2.200', 'reflex 2" #600 (TAVAL: #150)'),
    '109': ant(1900.0, 'LG 231B USD 1.900', 'reflex 2" #600 (TAVAL: #150)'),
    '113': ant(2000.0, 'cupón de corrosión CC 231 USD 2.000', 'mismo servicio'),
    '114': ant(50.0, 'junta espiralada 32" #600 USD 50', 'igual'),
    '116': est(35.0, 'junta espiralada 20" #600 con anillo interior'),
    '118': ant(15.0, 'junta espiralada 10" #600 USD 15', 'con anillo interior'),
    '120': ant(7.0, 'junta espiralada 6" #600 USD 7', 'igual'),
    '121': est(13.0, f'espárrago L7 1" × 6 3/4": USD 10 B7 de TAVAL/37 {LT}'),
    '123': est(13.0, f'espárrago L7 3/4" × 4": USD 10 B7 de TAVAL/37 {LT}'),
    '127': est(13.0, f'espárrago L7 7/8": USD 10 B7 de TAVAL/37 {LT}'),
    '129': ant(3.5, 'espárragos B7 zincados, mismo valor que la planilla de costo ITT', 'B7 5/8" #600'),
    '133': ant(10.0, 'espárragos con 2 tuercas zinc USD 10', 'B7 #600'),
    '131': ant(10.0, 'espárragos con 2 tuercas zinc USD 10', 'B7 (CA11) / L7 (CK11)'),
    '135': ant(6000.0, 'caja de chicanas 800×400×400 AISI 304 USD 6.000', 'la nuestra es 800×650×200 AISI 316L, en 2 módulos'),
    '136': est(15.0, 'junta de asiento de cartucho'),
    '142': ant(10.0, 'tubing 1/2" USD 10/m', 'inox'),
    '143': ant(15.0, 'chapa de identificación AISI 316 USD 15', 'igual'),
    '144': ant(450.0, 'caja junction box aluminio CA-5-17 USD 450', 'Ex zona 2'),
    '145': ant(450.0, 'caja junction box USD 450', 'potencia del traceado'),
    '146': ant(3364.0, 'cables AR-5100/6100, conduit 2" y 1", boquillas, prensacables Ex, bornera, riel DIN, abrazaderas, ángulos = USD 3.364', 'mismo alcance (skid con instrumentos)'),
    '147': ant(3920.0, 'tracing a USD 980 por circuito × 4 circuitos', 'TAVAL/37 tenía 3 circuitos'),
    '148': ant(4080.0, 'aislación del cuerpo USD 1.200 (sin tracing) + aislación de piping USD 2.880', 'recipiente Ø 32" completo y líneas traceadas'),
}
CHAPA_516 = ant(1.8, 'chapa SA-516 Gr. 70 USD 1,8/kg', 'mismo material')
ACERO_36 = ant(1.4, 'chapa SA-36 USD 1,4/kg', 'perfiles y chapas de estructura')
POS_CHAPA = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '11'}
POS_EST = {'137', '138', '139', '140', '141'}
COPIAR_DE = {}  # VF-346/347: misma válvula que las de nivel

MO = [  # id, descripción, especificación, cantidad, unidad, precio, rubro TAVAL/37
    ('S01', 'Soldadura de cañería y cuerpo (armado y soldadura del recipiente y del piping)',
     'TAVAL/37 FC-231 (mismo tipo y tamaño). Nuestro cálculo: ≈ 2.783 pulg-eq por filtro (piping 1.228 + recipiente 1.556; resumen_pedido.md §12)', 1, 'gl', 71441.70, 'SOLDADURA CAÑERIA+CUERPO'),
    ('S02', 'Soldadura y fabricación de la estructura (chasis, plataformas, escaleras, batea)', 'TAVAL/37; estructura 8.380 kg por skid según el plano', 1, 'gl', 10841.12, 'SOLDADURA ESTRUCTURA'),
    ('S03', 'Radiografía RT1 (100 %) y END', 'TAVAL/37 (RT1, PWHT según código)', 1, 'gl', 52196.00, 'RX'),
    ('S04', 'Granallado y pintura B0600 (sistemas 201 y 202)', 'TAVAL/37', 1, 'gl', 7551.63, 'GRANALLA Y PINTURA'),
    ('S05', 'Montaje del skid, PH, cableado, FAT y embalaje', 'TAVAL/37', 1, 'gl', 31824.00, 'MONTAJE'),
    ('S06', 'Ingeniería (memoria ASME VIII, planos, 3D de ingeniería, documentos de la RI §13)', 'TAVAL/37', 1, 'gl', 8735.00, 'INGENIERIA'),
    ('S07', 'Calidad, PIE, PQR con entidad independiente y Data Book', 'TAVAL/37', 1, 'gl', 3750.00, 'CALIDAD'),
    ('S08', 'Seguro de cumplimiento', 'TAVAL/37', 1, 'gl', 1048.32, 'SEGURO - CUMPLIMIENTO'),
]


def main():
    auto = json.load(open(os.path.join(AQUI, 'cotizacion_auto.json'), encoding='utf-8'))
    base = json.load(open(os.path.join(AQUI, '..', 'COT26-0010-001_AESA_C5297_FILTROS_GAS', 'cotizacion.json'), encoding='utf-8'))
    c = copy.deepcopy(auto)
    c.update({
        'codigo': 'COT26-0010-002', 'revision': 'Rev 0', 'estado': 'borrador', 'fecha': '2026-11-26', 'preparo': 'Matías Russo',
        'cliente': base['cliente'],
        'titulo': 'AESA (YPF) · C5297 PC-02 LANor — 2 filtros coalescedores FC-301/302 en skid',
        'titulo_pagina': 'Cotización AESA C5297 FC-301/302',
        'archivo_planilla': 'AESA_C5297_FILTROS_COALESCEDORES',
        'subtitulo_planilla': '2 skids con filtro coalescedor 32" #600 · RI 5297-02-0100-IG-EM-RI-001 E0 · USD sin IVA · EXW Quilmes Oeste',
        'meta': ['Solped 23583841', 'RI 5297-02-0100-IG-EM-RI-001 E0 (30-10-2026)', 'Comprador: AESA', 'Preparó: Matías Russo · 26-11-2026'],
        'equipo': {'singular': 'filtro coalescedor (skid)', 'plural': 'filtros coalescedores (skids)'},
    })
    for k in ('flete', 'pie', 'pedido', 'desvios', 'antecedentes', 'pendientes', 'planilla_notas', 'nota_mo_html', 'historial_html', 'justificaciones', 'compras'):
        if k in base and k not in c:
            c[k] = copy.deepcopy(base[k])
    c['parametros'].update({'N': 2, 'FM': 1.35, 'FMO': 1.35, 'CONT': 5, 'AJ': 1, 'TC': 1543.23, 'fecha_referencia': '2026-10-31'})
    c['plazo'] = {'dias': 210, 'texto': 'días corridos desde OC, con la ingeniería aprobada en 1 ciclo de revisión · EXW Quilmes Oeste',
                  'tareas': [['Ingeniería y aprobación de AESA/YPF', 0, 60, 'crit'], ['Compra de chapa, bridas B16.47, válvulas de 10" y cartuchos', 30, 150, 'crit'],
                             ['Fabricación del recipiente, PWHT, RX y PH', 90, 170, 'tal'], ['Skid, piping, instrumentos, tracing y aislación', 140, 195, 'tal'],
                             ['FAT, pintura, embalaje y despacho', 195, 210, 'tal']],
                  'nota': 'Antecedentes: YPF/27 FC301/302 PC LAS 175 días; Sacde/12 190 días; TAVAL/37 FC-231 210 días. Criterio ITT: el de TAVAL/37 (mismo alcance).'}
    items = {i['pos']: i for i in c['items'] if i['grupo'] == 'material'}
    for pos, f in PRECIOS.items():
        if pos in SIN_REF:
            f = {'tipo': 'est', 'precio': 0, 'proveedor': 'SIN PRECIO: pedir cotización (sin pieza parecida en el catálogo ni en TAVAL/37)',
                 'origen': 'P4 ter', 'fecha': '2026-11-26', 'coincide': 'sin_ref'}
        it = items[pos]
        it['fuentes'] = [f] + [x for x in it.get('fuentes', []) if (x.get('precio') or 0) > 0]
    for pos in POS_CHAPA:
        items[pos]['fuentes'] = [CHAPA_516] + items[pos].get('fuentes', [])
    for pos in POS_EST:
        if pos in items:
            items[pos]['fuentes'] = [ACERO_36] + items[pos].get('fuentes', [])
    for pos, de in COPIAR_DE.items():
        items[pos]['fuentes'] = copy.deepcopy(items[de]['fuentes'])
        if items[de].get('taval'):
            items[pos]['taval'] = True
    mats = [i for i in c['items'] if i['grupo'] == 'material']
    for i in mats:  # similares del catálogo sin la diferencia anotada
        for f in i.get('fuentes', []):
            if f.get('coincide') == 'similar' and not f.get('diferencia'):
                f['diferencia'] = ('similar elegido por precotizar.py (misma familia, Ø y serie); especificación a confirmar '
                                   'con el pedido (ver precotizacion.md)')
    mo = []
    for id_, d, e, q, u, p, rub in MO:
        mo.append({'id': id_, 'pos': 'MO', 'grupo': 'mo' if id_ in ('S01', 'S02', 'S05') else 'servicio', 'descripcion': d, 'especificacion': e,
                   'cantidad': q, 'unidad': u, 'fuentes': [ant(p, f'{rub} USD {p:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'), 'mismo tipo y tamaño de equipo (32" #600, skid con instrumentos)')]})
    c['items'] = mats + mo
    comp = c.setdefault('compras', {})
    for k, v in list(comp.items()):
        if isinstance(v, str) and 'AAAA' in v:
            comp[k] = '2026-12-04'
    for k in ('material', 'marcas', 'notas', 'material_sin_et'):
        if isinstance(comp.get(k), dict):
            comp[k] = {}
    c['parametros']['rx_pct'] = 0
    c['parametros']['ph_horas'] = 0
    json.dump(c, open(os.path.join(AQUI, 'cotizacion.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'OK: cotizacion.json con {len(mats)} materiales y {len(mo)} rubros de MO y servicios')


if __name__ == '__main__':
    main()
