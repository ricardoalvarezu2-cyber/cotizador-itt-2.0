"""Predimensionamiento del filtro FCC-707/708 (COT26-0010-001) según ASME VIII Div.1: espesores, dimensiones y pesos.

Uso: python cotizaciones/COT26-0010-001_AESA_C5297_FILTROS_GAS/dimensionamiento.py   → escribe dimensionamiento.md

ES UN PREDIMENSIONAMIENTO PARA COTIZAR, NO LA MEMORIA DE CÁLCULO. El código ASME no está en el repositorio: las tensiones
admisibles (II-D), los datos de junta (Apéndice 2) y el rating B16.5 están cargados de memoria y los tiene que verificar
Ingeniería en la edición vigente. Los pesos de caños, bridas, casquete, codo, espárragos y válvulas salen de las tablas de
conocimiento/tecnico/; las piezas de chapa, por volumen × 7,85.
"""
import csv
import math
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TEC = AQUI.parent.parent / "conocimiento" / "tecnico"


def n(x, d=2):
    """Número a la vista: punto de miles, coma decimal."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def filas(nombre):
    return list(csv.DictReader(open(TEC / nombre, encoding="utf-8")))


def cano(dn, sch):
    for r in filas("canos_peso_superficie.csv"):
        if float(r["dn_pulg"]) == dn and r["schedule"] == sch:
            return {k: float(r[k]) for k in ("diam_ext_mm", "espesor_mm", "diam_int_mm", "kg_m_carbono", "m2_m_exterior", "litros_m_interior")}
    raise SystemExit(f"caño {dn} sch {sch} no está en la tabla")


def brida(tipo, dn):
    for r in filas("bridas_peso.csv"):
        if r["tipo"] == tipo and float(r["dn_pulg"]) == dn and r["serie"] == "150":
            return float(r["peso_kg"])
    raise SystemExit(f"brida {tipo} {dn} no está en la tabla")


def accesorio(tipo, dn, sch):
    for nombre in ("accesorios_peso.csv", "accesorios_peso_complemento.csv"):
        for r in filas(nombre):
            if r["norma"] == "ASME B16.9" and r["tipo"] == tipo and float(r["dn_pulg"]) == dn and r["schedule_o_clase"] == sch:
                return float(r["peso_kg"])
    raise SystemExit(f"accesorio {tipo} {dn} {sch} no está en la tabla")


def tuerca(d):
    for r in filas("esparragos_peso.csv"):
        if r["tipo"] == "tuerca_heavy_hex_2H" and float(r["diametro_pulg"]) == d:
            return float(r["peso_unidad_kg"])
    raise SystemExit(f"tuerca {d} no está en la tabla")


def chapa(largo, ancho, esp, cant=1):
    """kg de chapa de acero (mm)."""
    return largo * ancho * esp * 7.85e-6 * cant


# ---------------------------------------------------------------- datos del cliente (hoja de datos HD-001 E0, pág. 3)
P_KG = 10.0                      # presión de diseño, kg/cm2 g
P = P_KG * 0.0980665             # MPa
T_DIS, MDMT = 90, -10            # °C
CA = 3.2                         # sobreespesor de corrosión, mm
E = 0.85                         # RT3: radiografiado por puntos (C0100 5.1.5); caño y casquete sin costura
TOL = 0.125                      # tolerancia de fabricación del caño (ASME B36.10 / SA-106)

# ---------------------------------------------------------------- tensiones admisibles a 90 °C (ASME II-D tabla 1A, DE MEMORIA)
S_106B = 118.0                   # SA-106 Gr. B (17,1 ksi)
S_WPB = 118.0                    # SA-234 WPB
S_105 = 138.0                    # SA-105 (20,0 ksi)
S_B7 = 172.0                     # SA-193 B7 (25,0 ksi)

# ---------------------------------------------------------------- diseño preliminar ITT
cuerpo = cano(6, "80")
c1 = cano(1, "160")
c34 = cano(0.75, "160")
L_CANO = 600.0                   # largo del caño del cuerpo, mm (a confirmar con el cartucho)
H_CASQ = 102.0                   # altura del casquete 6" B16.9 con pared mayor de 10,92 mm (E1); con Sch 40 es 89
RECTO_CASQ = 54.0                # tramo recto del casquete hasta la tangente (aprox.: 102 − profundidad del fondo − espesor)
Y_BRIDA = 87.0                   # largo de la brida W.N. 6" #150 (Y, aprox.)
T_BRIDA = 23.9                   # espesor mínimo de brida y brida ciega 6" #150 (B16.5), sin el resalte
RF = 2.0                         # resalte de la cara (lado mojado de la brida ciega: es el que se corroe)
OD_BRIDA, BC, N_ESP, D_ESP = 280.0, 241.3, 8, 19.05
H_PATA = 350.0                   # del piso a la soldadura casquete-caño
PROY = 250.0                     # del eje del filtro a la cara de las bridas A, B y D

# ---------------------------------------------------------------- 1. envolvente (UG-27 c 1)
De, t_nom = cuerpo["diam_ext_mm"], cuerpo["espesor_mm"]
t_min = t_nom * (1 - TOL)                      # espesor mínimo que puede traer el caño
R_corr = De / 2 - t_min + CA                   # radio interior corroído
t_env = P * R_corr / (S_106B * E - 0.6 * P)    # requerido por presión
T_YPF = max(5.0, 3.0 + CA)                     # C0100 5.1.3 tabla 5.1.3-I nota 1 (Ø ext. < 1000 mm)
sch40 = cano(6, "40")["espesor_mm"] * (1 - TOL)

# ---------------------------------------------------------------- 2. casquete semielíptico 2:1 (UG-32 c)
D_corr = De - 2 * t_min + 2 * CA
t_casq = P * D_corr / (2 * S_WPB * E - 0.2 * P)

# ---------------------------------------------------------------- 3. cuellos (UG-45) y refuerzo (UG-36 c 3)
UG16 = 1.5                                     # espesor mínimo UG-16(b), mm
cuellos = []
for nombre, c, std in (('A y B, 1" Sch 160', c1, cano(1, "40")["espesor_mm"]), ('D, 3/4" Sch 160', c34, cano(0.75, "40")["espesor_mm"])):
    ta = P * (c["diam_ext_mm"] / 2) / (S_106B * 1.0 + 0.4 * P) + CA       # presión interior (UG-27, radio exterior) + corrosión
    tb1 = max(P * R_corr / (S_106B * 1.0 - 0.6 * P), UG16) + CA   # envolvente por presión con E = 1, no menor que UG-16(b), + corrosión
    tb3 = std * (1 - TOL) + CA                 # pared estándar menos tolerancia + corrosión
    req = max(ta, min(tb1, tb3))
    cuellos.append((nombre, c["espesor_mm"], c["espesor_mm"] * (1 - TOL), ta, tb1, tb3, req))

# ---------------------------------------------------------------- 4. bridas (UG-44, ASME B16.5 grupo 1.1 clase 150, DE MEMORIA)
RAT_50, RAT_100 = 19.2, 17.7                   # bar a 50 y 100 °C
rating_bar = RAT_50 + (RAT_100 - RAT_50) * (T_DIS - 50) / 50
rating_kg = rating_bar / 0.980665

# ---------------------------------------------------------------- 5. brida ciega con corrosión (UG-34 c 2, ec. 2; junta espiralada, DE MEMORIA)
J_DE, J_DI, m_j, y_j = 209.6, 182.6, 3.0, 69.0  # junta espiralada 6" #150: Ø del sello, m e y (MPa)
b0 = (J_DE - J_DI) / 2 / 2
b = 2.52 * math.sqrt(b0) if b0 > 6.35 else b0
G = J_DE - 2 * b
hG = (BC - G) / 2
A_ESP = 194.8                                   # área de raíz de un espárrago 3/4"-10 UNC, mm2
Ab = N_ESP * A_ESP
Wm1 = math.pi / 4 * G ** 2 * P + 2 * b * math.pi * G * m_j * P
Wm2 = math.pi * b * G * y_j
Am = max(Wm1 / S_B7, Wm2 / S_B7)
W_as = (Am + Ab) / 2 * S_B7
C_T = 0.3
t_tapa_op = G * math.sqrt(C_T * P / S_105 + 1.9 * Wm1 * hG / (S_105 * G ** 3))
t_tapa_as = G * math.sqrt(1.9 * W_as * hG / (S_105 * G ** 3))
t_tapa = max(t_tapa_op + CA, t_tapa_as + CA)    # corrosión sumada también al asentamiento: la tapa se abre y se vuelve a apretar ya corroída
T_TAPA_DISP = T_BRIDA + RF                      # espesor dentro del círculo de la junta, con el resalte

# ---------------------------------------------------------------- 6. prueba hidráulica (UG-99 b)
PH = 1.3 * P_KG * 1.0                           # relación de tensiones 1 (misma S a temperatura ambiente y a 90 °C)

# ---------------------------------------------------------------- dimensiones generales
z_brida = H_PATA + L_CANO + Y_BRIDA             # cara de la brida de cuerpo sobre el piso
z_tapa = z_brida + 4.5 + T_BRIDA + RF
z_total = z_tapa + 330                          # cupla + niple 100 + válvula + tapón (aprox.)
TT = RECTO_CASQ + L_CANO + Y_BRIDA              # de la tangente del casquete a la cara de la brida
vol = (cuerpo["litros_m_interior"] * TT / 1000) + math.pi / 24 * (cuerpo["diam_int_mm"] / 100) ** 3
m2_ext = cuerpo["m2_m_exterior"] * (L_CANO + Y_BRIDA + H_CASQ) / 1000 + 0.2032 * 1.5 + 0.15 + 0.30   # cuerpo + patas (L 2": 0,2032 m2/m) + pescante + bridas, tapa y conexiones (aprox.)

# ---------------------------------------------------------------- pesos (kg por filtro)
TAB, CALC, EST = "tabla", "calculado", "estimado"
pesos = [
    ("1", 'Envolvente: caño 6" Sch 80 × 600 mm', cuerpo["kg_m_carbono"] * L_CANO / 1000, TAB),
    ("2", 'Casquete semielíptico 6" Sch 80', accesorio("casquete", 6, "80"), TAB),
    ("3", 'Brida W.N. 6" #150', brida("WN", 6), TAB),
    ("4", 'Brida ciega 6" #150', brida("ciega", 6), TAB),
    ("5", 'Pescante: caño 1 1/2" Sch 80 × 1,0 m, buje soporte, brazo y bulón de ojo', cano(1.5, "80")["kg_m_carbono"] * 1.0 + 3.5, EST),
    ("6", "Junta de la tapa (1 colocada)", 0.3, EST),
    ("7 y 31", '8 espárragos 3/4" × 4" con 16 tuercas', 8 * (4 * 0.0254 * math.pi / 4 * 0.01905 ** 2 * 7850) + 16 * tuerca(0.75), CALC),
    ("8 y 9", '2 bridas W.N. 1" #150', 2 * brida("WN", 1), TAB),
    ("10", 'Cuellos A y B: caño 1" Sch 160 × 0,3 m', c1["kg_m_carbono"] * 0.3, TAB),
    ("11", 'Brida W.N. 3/4" #150', brida("WN", 0.75), TAB),
    ("12", 'Cuello D: caño 3/4" Sch 160 × 0,4 m', c34["kg_m_carbono"] * 0.4, TAB),
    ("13", 'Codo 90° 3/4" Sch 160', accesorio("codo_90_radio_largo", 0.75, "160"), TAB),
    ("14 a 17 y 32", 'Válvula de drenaje 3/4" con tapón, junta y bulonería (tipo a definir: CA11; entre 3,5 kg esférica y 8 kg esclusa)', 5.5, EST),
    ("18 a 21", 'Cupla, niple, válvula de venteo 3/4" NPT y tapón (tipo a definir: CA11)', 2.4, EST),
    ("22", "2 elementos filtrantes (a definir con el fabricante)", 1.0, EST),
    ("23 y 24", "Internos: asiento de 10 mm, conducto de salida, varilla y bulonería", 5.0, EST),
    ("25", '3 patas L 2" × 2" × 1/4" × 500 mm con placa base 120 × 120 × 9,5', 3 * (4.75 * 0.50) + chapa(120, 120, 9.5, 3), CALC),
    ("26", "3 placas de refuerzo 150 × 80 × 6,35", chapa(150, 80, 6.35, 3), CALC),
    ("27", "2 orejas de izaje 80 × 60 × 9,5", chapa(80, 60, 9.5, 2), CALC),
    ("28", "2 orejas de puesta a tierra 50 × 40 × 6 AISI 316", chapa(50, 40, 6, 2), CALC),
    ("29", "Placa de identificación con soporte 150 × 100 × 6", chapa(150, 100, 6) + 0.1, CALC),
    ("33", "Rompevórtice", 0.2, EST),
    ("—", "Soldadura y pintura (≈ 2 %)", 0.0, EST),
]
sub = sum(p[2] for p in pesos)
pesos[-1] = (pesos[-1][0], pesos[-1][1], sub * 0.02, EST)
vacio = sum(p[2] for p in pesos)
p_ph = vacio + vol * 1.0 - 1.0                  # lleno de agua, sin los elementos
p_op = vacio                                    # gas: el fluido no pesa
p_tr = vacio + 12.0                             # patín y embalaje (estimado)

# ---------------------------------------------------------------- salida
ok = lambda c: "cumple" if c else "**NO CUMPLE**"
o = []
o.append("# Predimensionamiento ASME VIII Div.1 — filtro de gas de emergencia FCC-707/708 (COT26-0010-001)\n")
o.append("**Borrador, sin revisar. Es un predimensionamiento para cotizar, no la memoria de cálculo que pide la requisición.** "
         "Lo genera `dimensionamiento.py`; no editar a mano. El código ASME no está en el repositorio: las tensiones admisibles (II-D), "
         "los datos de la junta y el rating de B16.5 están cargados de memoria y los tiene que verificar Ingeniería en la edición vigente.\n")
o.append("## 1. Datos de diseño (hoja de datos 5297-02-0600-IG-EM-HD-001 E0)\n")
o.append("| Dato | Valor |\n|---|---|")
o.append(f"| Presión de diseño | {n(P_KG)} kg/cm2 g ({n(P, 3)} MPa) |")
o.append(f"| Temperatura de diseño / MDMT | {T_DIS} / {MDMT} °C |")
o.append(f"| Sobreespesor de corrosión | {n(CA)} mm |")
o.append(f"| Radiografiado | RT3 (por puntos): eficiencia de junta E = {n(E)} |")
o.append("| Código | ASME VIII Div.1 última edición, sin estampa (recipiente hasta la cara de la primera brida o la primera rosca); ASME B31.3 y clase CA11 para el niple, las válvulas de venteo y drenaje y sus tapones; bridas ASME B16.5 |")
o.append("| Materiales | Envolvente SA-106 Gr. B; casquete SA-234 WPB; bridas SA-105; cuellos SA-106 Gr. B; espárragos SA-193 B7 / tuercas SA-194 2H |")
o.append(f"| Tensión admisible a {T_DIS} °C | SA-106 B y SA-234 WPB {n(S_106B, 0)} MPa; SA-105 {n(S_105, 0)} MPa; SA-193 B7 {n(S_B7, 0)} MPa (a verificar en II-D) |\n")
o.append("## 2. Espesores\n")
o.append("| Parte | Adoptado | Mínimo disponible | Requerido por presión | Requerido total | Resultado |\n|---|---|---|---|---|---|")
o.append(f"| Envolvente, caño 6\" Sch 80 (UG-27) | {n(t_nom)} mm | {n(t_min)} mm (−12,5 %) | {n(t_env)} mm | {n(max(t_env + CA, T_YPF))} mm (C0100 5.1.3: 3 + {n(CA)}) | {ok(t_min >= max(t_env + CA, T_YPF))} |")
o.append(f"| Casquete 6\" Sch 80 (UG-32) | {n(t_nom)} mm | {n(t_min)} mm | {n(t_casq)} mm | {n(max(t_casq + CA, T_YPF))} mm | {ok(t_min >= max(t_casq + CA, T_YPF))} |")
for nombre, tn, tm, ta, tb1, tb3, req in cuellos:
    o.append(f"| Cuello {nombre} (UG-45) | {n(tn)} mm | {n(tm)} mm | {n(ta - CA)} mm | {n(req)} mm | {ok(tm >= req)} |")
o.append(f"| Brida ciega 6\" #150 con corrosión (UG-34) | {n(T_TAPA_DISP)} mm ({n(T_BRIDA)} + resalte {n(RF, 0)}) | {n(T_TAPA_DISP)} mm | {n(max(t_tapa_op, t_tapa_as))} mm | {n(t_tapa)} mm | {ok(T_TAPA_DISP >= t_tapa)}, con poco margen ({n(T_TAPA_DISP - t_tapa)} mm): a verificar |\n")
o.append(f"- Con caño Sch 40 el mínimo disponible sería {n(sch40)} mm contra {n(T_YPF)} mm que pide YPF: sin margen. Por eso Sch 80.")
o.append("- Manda el espesor mínimo de la C0100 de YPF, no la presión: por presión alcanza con menos de 1 mm.")
o.append(f"- **Brida ciega: en el límite, a verificar por Ingeniería** (C0100 5.1.11: con corrosión mayor de 3 mm el fabricante verifica las bridas ciegas estándar). "
         f"Manda el asentamiento de la junta ({n(t_tapa_as)} mm; en operación {n(t_tapa_op)} mm), más {n(CA)} mm de corrosión. Contando el resalte cumple por {n(T_TAPA_DISP - t_tapa)} mm; "
         f"sin contarlo ({n(T_BRIDA)} mm) no llega por {n(t_tapa - T_BRIDA)} mm. El resultado depende de la junta, que no está definida (clase CA11, consulta C3): se calculó con espiralada "
         f"(m = {n(m_j, 0)}, y = {n(y_j, 0)} MPa), que es el caso más exigente; con junta plana de fibra sobra. Con esa junta el área de espárragos que pide el Apéndice 2 ({n(Am, 0)} mm2) supera la disponible ({n(Ab, 0)} mm2), "
         "algo conocido en bridas #150 con espiralada: la unión es estándar (UG-44) y el caso de asentamiento es conservador. Si Ingeniería no la acepta, la salida es una tapa de chapa de 1\" a 1 1/8\" con el perforado #150 (≈ 2 kg más). "
         "El agujero roscado de 3/4\" del venteo no necesita refuerzo (UG-39 a / UG-36 c 3).")
o.append(f"- Bridas (UG-44): B16.5 clase 150, grupo 1.1, admite {n(rating_bar, 1)} bar ({n(rating_kg, 1)} kg/cm2) a {T_DIS} °C contra {n(P_KG, 1)} kg/cm2 de diseño: {ok(rating_kg >= P_KG)}.")
o.append("- Refuerzo de aberturas (UG-36 c 3): las conexiones de 1\" y 3/4\" en la envolvente y el casquete no necesitan cálculo de refuerzo (abertura menor de 89 mm con espesor requerido de hasta 10 mm).")
o.append("- Cuellos: Sch 160 por la C0100 5.1.3 (conexiones menores de 3\").")
o.append(f"- Prueba hidráulica (UG-99 b): 1,3 × {n(P_KG, 1)} = **{n(PH, 1)} kg/cm2 g** como mínimo, tomando la presión máxima admisible igual a la de diseño (hay que declararlo en la oferta: la C0100 5.1.6 pide 1,3 × MAWP y, si la MAWP se calculara, la limita la brida #150 en ≈ {n(rating_kg, 1)} kg/cm2 y la prueba subiría a ≈ {n(1.3 * rating_kg, 1)} kg/cm2).")
o.append("- Impacto a −10 °C: el revisor independiente entiende que queda exento (UG-20 f y UCS-66: curva B con 11 mm; bridas B16.5 hasta −29 °C), dicho de memoria; se justifica en la memoria de cálculo.")
o.append("- C0100 5.1.4 pide espesor mínimo total de 10 mm para partes de acero al carbono (está en el párrafo de internos): los internos soldados se previeron de 10 mm. Si YPF lo aplicara también a la envolvente, el Sch 80 con tolerancia (9,60 mm) no alcanzaría: está en la consulta C11.")
o.append("- Sin calcular: cargas en conexiones (WRC 107, HD nota 5), viento, sismo y nieve sobre las patas y los pernos de anclaje, orejas de izaje y pescante.\n")
o.append("## 3. Dimensiones generales (preliminares)\n")
o.append("| Dimensión | Valor |\n|---|---|")
o.append(f"| Diámetro exterior del cuerpo | {n(De, 1)} mm (6\") |")
o.append(f"| Diámetro interior | {n(cuerpo['diam_int_mm'], 1)} mm |")
o.append(f"| Espesor de envolvente y casquete | {n(t_nom)} mm (Sch 80) |")
o.append(f"| Largo de la tangente del casquete a la cara de la brida de cuerpo | {n(TT, 0)} mm (tramo recto del casquete {n(RECTO_CASQ, 0)} + caño {n(L_CANO, 0)} + brida {n(Y_BRIDA, 0)}; el casquete entero mide {n(H_CASQ, 0)} mm) |")
o.append(f"| Altura del piso a la cara de la brida de cuerpo | {n(z_brida, 0)} mm |")
o.append(f"| Altura total con tapa | {n(z_tapa, 0)} mm |")
o.append(f"| Altura total con válvula de venteo | ≈ {n(z_total, 0)} mm (el pescante puede sumar ≈ 100 mm) |")
o.append(f"| Brida de cuerpo y tapa 6\" #150 | Ø {n(OD_BRIDA, 0)} mm; {N_ESP} espárragos 3/4\" en Ø {n(BC, 1)} mm |")
o.append(f"| Conexiones A y B (1\" #150 WNRF) | enfrentadas, a {n(H_PATA + 420, 0)} mm del piso; {n(2 * PROY, 0)} mm entre caras |")
o.append(f"| Conexión D (3/4\" #150 WNRF) | a 150 mm del piso; cara a {n(PROY, 0)} mm del eje |")
o.append("| Conexión F (3/4\" NPT #3000) | en el centro de la tapa |")
o.append("| Patas | 3 de L 2\" × 2\" × 1/4\", placas base 120 × 120 × 9,5 mm con agujero Ø 18 en círculo de Ø 330 mm |")
o.append(f"| Volumen interior | {n(vol, 1)} litros ({n(vol / 1000, 4)} m3) |")
o.append(f"| Superficie exterior a pintar | ≈ {n(m2_ext)} m2 |\n")
o.append("El largo del cuerpo y la posición de A y B dependen del cartucho (cantidad y medida a definir con el fabricante del elemento) y del caudal, que el cliente tiene que aclarar (consulta C1).\n")
o.append("## 4. Peso (por filtro)\n")
o.append("| Pos | Parte | kg | Origen |\n|---|---|---|---|")
for pos, d, kg, org in pesos:
    o.append(f"| {pos} | {d} | {n(kg)} | {org} |")
o.append(f"| | **Peso vacío** | **{n(vacio)}** | |\n")
o.append("| Peso | kg |\n|---|---|")
o.append(f"| Vacío | {n(vacio, 0)} |")
o.append(f"| En operación (gas) | {n(p_op, 0)} |")
o.append(f"| En prueba hidráulica (lleno de agua, sin elementos) | {n(p_ph, 0)} |")
o.append(f"| En transporte (con patín y embalaje, estimado) | {n(p_tr, 0)} |\n")
o.append("Origen: *tabla* = tablas de pesos de `conocimiento/tecnico/` (bridas ±15 %, accesorios ±10–15 %); *calculado* = volumen × 7,85; *estimado* = pieza sin definir. "
         "Con margen, el peso vacío está entre " + f"{n(vacio * 0.9, 0)} y {n(vacio * 1.15, 0)} kg.\n")
o.append("## 5. Listado de materiales\n")
o.append("Está en `pedido/lista_materiales_plano.csv` (33 renglones por filtro), con el texto de la hoja de datos, cantidad, material y los datos de cada pieza en columnas.\n")
(AQUI / "dimensionamiento.md").write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"vacío {n(vacio)} kg · PH {n(p_ph)} kg · volumen {n(vol, 1)} l · tapa req {n(t_tapa)} mm (disp {n(T_BRIDA)})")
