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
    ("22", "Elemento filtrante: 1 cartucho de 2 3/4\" × 10\" (a definir con el fabricante)", 0.5, EST),
    ("23 y 24", 'Internos AISI 316 L: tubo de salida 1" Sch 160 con codo, asiento, platillo, resorte, varilla y bulonería', 4.0, EST),
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
o.append("| Conexión F (3/4\" NPT #3000) | en la tapa, corrida 65 mm del centro (el centro lo ocupa el cáncamo del pescante) |")
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
# ================================================================ DISEÑO: proceso, arreglo interno, soportes, izaje (11-11-2026)
# ---------------------------------------------------------------- proceso (hoja de datos pág. 2 y P&ID hoja 3)
Q_HD = 0.28 * 1000 / 24          # 0,28 MSCMD = 280 Sm3/d → Sm3/h (hoja de datos)
Q_PID = 6.15                     # Sm3/h (P&ID)
P_OP_MIN, T_OP_MAX = 4.5, 65.0   # kg/cm2 g y °C: la combinación que da más volumen real
Z_GAS = 0.98
Q_REAL = max(Q_HD, Q_PID) * 1.0332 / (P_OP_MIN + 1.0332) * (273.15 + T_OP_MAX) / 288.15 * Z_GAS   # m3/h reales
RHO = 6.95                       # kg/m3 (mínima de la hoja de datos)
d_boca = (c1["diam_ext_mm"] - 2 * c1["espesor_mm"]) / 1000
v_boca = Q_REAL / 3600 / (math.pi / 4 * d_boca ** 2)
CART_DE, CART_DI, CART_L = 70.0, 28.0, 254.0    # cartucho plisado estándar 2 3/4" × 10" (doble extremo abierto), mm
A_MEDIO = 0.45                   # m2 de medio plisado de un cartucho de 10" (típico 0,4–0,6 m2)
v_medio = Q_REAL / 3600 / A_MEDIO
v_anular = Q_REAL / 3600 / (math.pi / 4 * ((cuerpo["diam_int_mm"] / 1000) ** 2 - (CART_DE / 1000) ** 2))
rv2 = RHO * v_boca ** 2          # momento en la boca de entrada, kg/m·s2

# ---------------------------------------------------------------- elevaciones sobre el piso (mm)
Z_SOLD = H_PATA                                  # soldadura casquete–caño
Z_FONDO = Z_SOLD - H_CASQ                        # punto más bajo del casquete
Z_D = 150.0                                      # eje de la brida de drenaje
Z_AB = Z_SOLD + 250.0                            # eje de A y B (250 mm de cámara inferior)
Z_ASIENTO = Z_AB + 80.0                          # asiento del cartucho (codo interno 1" + tramo)
Z_CART = Z_ASIENTO + CART_L                      # extremo superior del cartucho
LIBRE_TAPA = z_brida - Z_CART                    # para el platillo, el resorte y sacar el cartucho

# ---------------------------------------------------------------- viento y sismo sobre las patas (CIRSOC 102 y 103, simplificado)
V_VIENTO, I_IMP = 48.0, 1.15
q_v = 0.613 * V_VIENTO ** 2                      # N/m2
A_VIENTO = (OD_BRIDA / 1000) * (z_total / 1000)  # ancho de la brida × altura total (conservador)
F_V = q_v * 0.85 * 1.2 * I_IMP * A_VIENTO        # ráfaga 0,85; coeficiente de fuerza 1,2 (cilindro con accesorios); Kz = 1
H_F = z_total / 2000                             # altura de la resultante, m
M_V = F_V * H_F
W_PH = p_ph * 9.80665
F_S = 0.15 * W_PH                                # zona sísmica 1: coeficiente adoptado 0,15 (conservador)
M_S = F_S * (Z_AB + 150) / 1000
M_BASE, F_BASE = max(M_V, M_S), max(F_V, F_S)
N_PATAS, D_BC = 3, 0.33
A_L, Z_L, R_L = 605.0, 4050.0, 9.9               # ángulo L 2" × 2" × 1/4": área mm2, módulo resistente mm3, radio de giro mínimo mm
L_LIBRE = Z_SOLD                                 # largo libre de la pata, mm
N_PATA = W_PH / N_PATAS + 4 * M_BASE / (N_PATAS * D_BC)
s_axial = N_PATA / A_L
s_flex = (F_BASE / N_PATAS) * L_LIBRE / 2 / Z_L  # empotrada–guiada
S_A36 = 114.0                                    # SA-36, tensión admisible ASME (de memoria)
esbeltez = L_LIBRE / R_L
T_ANCLA = 4 * M_BASE / (N_PATAS * D_BC) - vacio * 9.80665 / N_PATAS
A_M16 = 157.0
s_ancla = max(T_ANCLA, 0) / A_M16

# ---------------------------------------------------------------- izaje (C0100 5.1.13: factor de impacto 1,5) y pescante
F_OREJA = p_ph * 9.80665 * 1.5                   # cada oreja se verifica con todo el peso
A_CORTE = 2 * 20.0 * 9.5                         # dos planos de corte de 20 mm en chapa de 9,5 mm
s_oreja = F_OREJA / A_CORTE
W_TAPA = (brida("ciega", 6) + 3.0) * 9.80665 * 1.5   # tapa + cupla, niple y válvula de venteo, con impacto
BRAZO = 0.20                                     # del eje del pescante al centro de la tapa, m
Z_PESC = 6700.0                                  # módulo resistente del caño 1 1/2" Sch 80, mm3
s_pesc = W_TAPA * BRAZO * 1000 / Z_PESC

o.append("## 5. Proceso y elemento filtrante\n")
o.append("| Dato | Valor |\n|---|---|")
o.append(f"| Caudal de diseño adoptado | {n(max(Q_HD, Q_PID))} Sm3/h (hoja de datos: 0,28 MSCMD; el P&ID dice {n(Q_PID)} Sm3/h: consulta C1) |")
o.append(f"| Caudal real a {n(P_OP_MIN, 1)} kg/cm2 g y {n(T_OP_MAX, 0)} °C | {n(Q_REAL)} m3/h |")
o.append(f"| Velocidad en las conexiones de 1\" Sch 160 (Ø int. {n(d_boca * 1000, 1)} mm) | {n(v_boca)} m/s (ρ·v² = {n(rv2, 0)} kg/m·s²: muy por debajo de los límites usuales de erosión y ruido) |")
o.append(f"| Elemento adoptado | 1 cartucho plisado estándar de 2 3/4\" × 10\" (Ø {n(CART_DE, 0)} × {n(CART_L, 0)} mm, doble extremo abierto), celulósico, 99,9 % > 10 μm, flujo de afuera hacia adentro |")
o.append(f"| Velocidad en el medio filtrante (≈ {n(A_MEDIO)} m2) | {n(v_medio * 1000, 2)} mm/s |")
o.append(f"| Velocidad en el espacio anular cuerpo–cartucho | {n(v_anular, 3)} m/s |")
o.append("| Pérdida de carga | Elemento limpio: despreciable a este caudal (criterio usual de la industria: hasta 0,14 kg/cm2 limpio; recambio a 0,8–1,0 kg/cm2). El valor garantizado lo da el fabricante del elemento |\n")
o.append("- El caudal es tan chico que un solo cartucho de 10\" trabaja muy holgado; el Ø 6\" del cuerpo sale del mínimo razonable para una tapa bridada con pescante, no del proceso.")
o.append("- El antecedente AESA/47 (PC-01) usó cartuchos Gora de Ø 42 × 86 mm (mínimo 2 por recipiente): entran en este cuerpo apilados sobre el mismo asiento. La medida final la define el fabricante del elemento; el asiento se adapta sin cambiar el recipiente.")
o.append("- La eficiencia 99,9 % > 10 μm es de grado absoluto: hay que pedirla garantizada por escrito al fabricante (el celulósico plisado común es nominal).\n")
o.append("## 6. Arreglo interno y elevaciones\n")
o.append("| Nivel sobre el piso | mm |\n|---|---|")
o.append(f"| Eje del drenaje D | {n(Z_D, 0)} |")
o.append(f"| Fondo del casquete | {n(Z_FONDO, 0)} |")
o.append(f"| Soldadura casquete–caño | {n(Z_SOLD, 0)} |")
o.append(f"| Eje de A (entrada) y B (salida) | {n(Z_AB, 0)} |")
o.append(f"| Asiento del cartucho | {n(Z_ASIENTO, 0)} |")
o.append(f"| Extremo superior del cartucho | {n(Z_CART, 0)} |")
o.append(f"| Cara de la brida de cuerpo | {n(z_brida, 0)} (quedan {n(LIBRE_TAPA, 0)} mm para el platillo de cierre y el resorte) |")
o.append(f"| Tope de la tapa | {n(z_tapa, 0)} |\n")
o.append("- **Recorrido del gas:** entra por A a la cámara del cuerpo, atraviesa el cartucho de afuera hacia adentro y sale por el tubo central hacia B. El polvo queda en el cartucho y lo que decanta va a la cámara inferior (250 mm) y al drenaje D.")
o.append("- **Tubo de salida interno:** caño 1\" Sch 160 con codo, desde el cuello de B hasta el centro, con el asiento del cartucho arriba. El tubo también hace de deflector frente a la entrada A.")
o.append("- **Material de los internos: AISI 316 L.** La C0100 5.1.4 pide para internos soldados de acero al carbono corrosión de los dos lados (3,2 + 3,2 mm) y 10 mm de espesor mínimo: un caño de 1\" no lo cumple en ningún schedule. En inoxidable el mínimo es 6 mm (Sch 160 = 6,35 mm) y la corrosión es 0. La hoja de datos no fija el material de internos y pide bulonería AISI 316 L. Requiere procedimiento de soldadura acero al carbono–inoxidable (consultas C6 y C11).")
o.append("- **Cierre del cartucho:** platillo superior con resorte y varilla roscada de 3/8\" AISI 316 L al asiento; se saca por arriba abriendo la tapa.")
o.append("- **Rompevórtice** sobre el drenaje D (C0100 5.1.9), en cruz de planchuela AISI 316 L.\n")
o.append("## 7. Soportes, anclaje, izaje y pescante\n")
o.append("| Verificación | Carga | Resultado | Admisible |\n|---|---|---|---|")
o.append(f"| Viento (CIRSOC 102: {n(V_VIENTO, 0)} m/s, I = {n(I_IMP)}) | {n(F_V, 0)} N; momento en la base {n(M_V, 0)} N·m | manda sobre el sismo | — |")
o.append(f"| Sismo (CIRSOC 103, zona 1; coeficiente adoptado 0,15) | {n(F_S, 0)} N; momento {n(M_S, 0)} N·m | no actúa junto con el viento (C0100 5.1.1) | — |")
o.append(f"| Pata L 2\" × 2\" × 1/4\" SA-36, compresión (lleno de agua + momento) | {n(N_PATA, 0)} N | {n(s_axial, 1)} MPa | {n(S_A36, 0)} MPa |")
o.append(f"| Pata, flexión por el corte | {n(F_BASE / N_PATAS, 0)} N | {n(s_flex, 1)} MPa | {n(S_A36, 0)} MPa |")
o.append(f"| Pata, esbeltez (largo libre {n(L_LIBRE, 0)} mm) | — | {n(esbeltez, 0)} | 120 |")
o.append(f"| Perno de anclaje M16 (3, uno por pata), tracción con el equipo vacío | {n(max(T_ANCLA, 0), 0)} N | {n(s_ancla, 1)} MPa | ≈ 100 MPa |")
o.append(f"| Oreja de izaje 80 × 60 × 9,5 con agujero Ø 22 (todo el peso × 1,5 en una oreja) | {n(F_OREJA, 0)} N | {n(s_oreja, 1)} MPa de corte | ≈ 55 MPa |")
o.append(f"| Pescante, caño 1 1/2\" Sch 80, brazo {n(BRAZO * 1000, 0)} mm (tapa y venteo × 1,5) | {n(W_TAPA, 0)} N | {n(s_pesc, 1)} MPa | {n(S_106B, 0)} MPa |\n")
o.append("- Todo trabaja muy por debajo de lo admisible: en un equipo de 100 kg las secciones salen de mínimos constructivos, no del cálculo.")
o.append("- **Patas:** 3 a 120°, ángulo de 2\" × 2\" × 1/4\" SA-36, soldadas con cordón continuo a placas de refuerzo de 150 × 80 mm cortadas del mismo caño del cuerpo (C0100 5.1.12: del material de la envolvente), con cantos redondeados y agujero testigo 1/8\" NPT. Placas base de 120 × 120 × 9,5 mm con agujero Ø 22. El sistema de patas necesita aprobación de YPF.")
o.append("- **Anclaje:** 3 pernos M16 en círculo de Ø 330 mm. ITT entrega el diseño y la plantilla; los pernos no se proveen.")
o.append("- **Orejas de izaje:** 2 a 180°, a 90° de A y B, debajo de la brida de cuerpo; penetración total y líquidos penetrantes (C0100 5.1.13).")
o.append("- **Pescante:** columna de caño 1 1/2\" Sch 80 que gira dentro de un buje de 2\" Sch 80 soldado al cuerpo con placa de refuerzo; brazo de planchuela y bulón de ojo de 1/2\" con tuerca de maniobra, tomado a un cáncamo en el centro de la tapa. Por eso el venteo F va corrido 65 mm del centro (el esquema de la hoja de datos lo dibuja centrado: se aclara en la oferta).")
o.append("- **Puesta a tierra:** 2 orejas AISI 316 de 50 × 40 × 6 mm con agujero Ø 14, en dos patas.")
o.append("- **Placa de identificación:** AISI 304 sobre soporte de chapa de 6 mm, al frente, entre A y B (como en el esquema de la hoja de datos).")
o.append("- **Sin calcular:** cargas de cañería en A y B (WRC 107 / UG-44 b): AESA tiene que informar las cargas.\n")
o.append("## 8. Soldadura, ensayos y terminación\n")
o.append("- Juntas circunferenciales (casquete–caño y caño–brida): a tope con penetración total, raíz GTAW y relleno SMAW (ED(EP)-B-05.00: sin GMAW en partes a presión). Cuellos de A, B y D pasantes con penetración total (UW-16).")
o.append("- Radiografiado por puntos (RT3): 2 placas por filtro. Líquidos penetrantes 100 % en las soldaduras de las 4 conexiones y en las orejas de izaje. Dureza e identificación positiva según ED(EP)-B-02.00.")
o.append(f"- Prueba hidráulica a {n(PH, 1)} kg/cm2 g, 1 hora, con registro, antes de pintar y sin el cartucho.")
o.append("- Junta de la tapa: espiralada AISI 316 / grafito con anillos interior y exterior, ASME B16.20 (supuesto hasta recibir la clase CA11).")
o.append("- Pintura exterior sistema 201 de la B0600: arenado SSPC-SP10, cinc silicato, mist coat, epoxi y poliuretano; RAL 9006 el cuerpo y RAL 9011 las patas. Interior sin revestimiento.\n")
o.append("## 9. Normas usadas\n")
o.append("| Tema | Norma |\n|---|---|")
for a, b in [("Diseño y fabricación del recipiente", "ASME VIII Div.1 última edición (UG-16, UG-20, UG-27, UG-32, UG-34, UG-36, UG-39, UG-44, UG-45, UG-99, UW-11, UW-12, UW-16, UCS-66, Apéndice 2)"),
             ("Materiales y tensiones admisibles", "ASME II partes A y D"), ("Soldadura y ensayos no destructivos", "ASME IX y ASME V"),
             ("Caños", "ASME B36.10"), ("Bridas", "ASME B16.5"), ("Casquete y codo a tope", "ASME B16.9"), ("Cupla y tapones roscados", "ASME B16.11 y ASME B1.20.1 (NPT)"),
             ("Junta espiralada", "ASME B16.20"), ("Espárragos y tuercas", "ASME B18.2.1 / B18.2.2; recubrimiento ISO 4042"),
             ("Venteo y drenaje aguas abajo de la primera rosca o brida", "ASME B31.3 y clase CA11 de la L0200 de YPF"),
             ("Requisitos del cliente", "YPF C0100 (recipientes), B0600 (pintura), ED(EP)-B-01.00, B-02.00 y B-05.00"),
             ("Viento, sismo y nieve", "CIRSOC 102 (2015), INPRES-CIRSOC 103 (2018), CIRSOC 104 (2005)"),
             ("Cargas en conexiones", "WRC 107 / 537 (pendiente)"),
             ("Patas, orejas y pescante", "Práctica habitual de recipientes (D. Moss, Pressure Vessel Design Manual; detalles tipo PIP VEFV1100), citada de memoria"),
             ("Pérdida de carga del elemento", "Criterios publicados por fabricantes de filtros de gas (Pall, Parker/Peco): ≈ 2 psi limpio, recambio a 12–15 psi")]:
    o.append(f"| {a} | {b} |")
o.append("")
o.append("Plano de arreglo general: `arreglo_general.svg` y `arreglo_general.png`, en esta carpeta.\n")

# ---------------------------------------------------------------- plano de arreglo general (SVG)
ESC, X0, Y0 = 0.5, 400.0, 800.0                  # px por mm, eje del filtro y nivel de piso
X = lambda x: X0 + x * ESC
Y = lambda z: Y0 - z * ESC
s = []
def linea(x1, z1, x2, z2, cls="c"): s.append(f'<line class="{cls}" x1="{X(x1):.1f}" y1="{Y(z1):.1f}" x2="{X(x2):.1f}" y2="{Y(z2):.1f}"/>')
def rect(x1, z1, x2, z2, cls="c"): s.append(f'<rect class="{cls}" x="{X(min(x1, x2)):.1f}" y="{Y(max(z1, z2)):.1f}" width="{abs(x2 - x1) * ESC:.1f}" height="{abs(z2 - z1) * ESC:.1f}"/>')
def texto(x, z, t, cls="t", anc="middle", dx=0, dy=0): s.append(f'<text class="{cls}" text-anchor="{anc}" x="{X(x) + dx:.1f}" y="{Y(z) + dy:.1f}">{t}</text>')
def cota_v(x, z1, z2, t):
    linea(x, z1, x, z2, "k"); linea(x - 12, z1, x + 12, z1, "k"); linea(x - 12, z2, x + 12, z2, "k")
    s.append(f'<text class="q" text-anchor="middle" transform="translate({X(x) - 5:.1f},{Y((z1 + z2) / 2):.1f}) rotate(-90)">{t}</text>')
def globo(x, z, t):
    s.append(f'<circle class="g" cx="{X(x):.1f}" cy="{Y(z):.1f}" r="11"/>'); texto(x, z, t, "b", dy=4)
R = De / 2
linea(-520, 0, 520, 0, "p")
for xp in (-R - 8, R + 8):                       # patas y placas base
    rect(xp - 25, 0, xp + 25, 10); rect(xp - 12, 10, xp + 12, Z_SOLD + 150, "c")
s.append(f'<path class="c f" d="M {X(-R):.1f} {Y(Z_SOLD):.1f} L {X(-R):.1f} {Y(Z_SOLD - RECTO_CASQ):.1f} A {R * ESC:.1f} {(H_CASQ - RECTO_CASQ) * ESC:.1f} 0 0 0 {X(R):.1f} {Y(Z_SOLD - RECTO_CASQ):.1f} L {X(R):.1f} {Y(Z_SOLD):.1f}"/>')
rect(-R, Z_SOLD, R, Z_SOLD + L_CANO, "c f")
s.append(f'<path class="c f" d="M {X(-R):.1f} {Y(Z_SOLD + L_CANO):.1f} L {X(-R - 12):.1f} {Y(z_brida - T_BRIDA):.1f} L {X(R + 12):.1f} {Y(z_brida - T_BRIDA):.1f} L {X(R):.1f} {Y(Z_SOLD + L_CANO):.1f} Z"/>')
rect(-OD_BRIDA / 2, z_brida - T_BRIDA, OD_BRIDA / 2, z_brida, "c f")
rect(-OD_BRIDA / 2, z_brida + 4.5, OD_BRIDA / 2, z_tapa, "c f")
for xe in (-BC / 2, BC / 2):                     # espárragos
    rect(xe - 9.5, z_brida - T_BRIDA - 22, xe + 9.5, z_tapa + 22, "c")
XF = -65.0                                        # venteo F corrido del centro: el centro de la tapa lo usa el cáncamo del pescante
rect(XF - 14, z_tapa, XF + 14, z_tapa + 130, "c")  # venteo F: cupla y niple
rect(XF - 28, z_tapa + 130, XF + 28, z_tapa + 230, "c f"); linea(XF - 28, z_tapa + 180, XF - 75, z_tapa + 180, "c")   # válvula y palanca
rect(XF - 12, z_tapa + 230, XF + 12, z_tapa + 270, "c")
rect(-8, z_tapa, 8, z_tapa + 45, "c f")           # cáncamo central de la tapa
for sg in (-1, 1):                               # conexiones A y B
    rect(sg * R, Z_AB - 16.7, sg * (PROY - 14), Z_AB + 16.7, "c f"); rect(sg * (PROY - 14), Z_AB - 55, sg * PROY, Z_AB + 55, "c f")
linea(0, Z_FONDO, 0, Z_D, "c"); rect(-13.3, Z_D + 30, 13.3, Z_FONDO, "c f")       # drenaje D
rect(-(PROY - 13), Z_D - 13.3, 0, Z_D + 13.3, "c f"); rect(-PROY, Z_D - 50, -(PROY - 13), Z_D + 50, "c f")
rect(-PROY - 110, Z_D - 28, -PROY, Z_D + 28, "c f"); linea(-PROY - 55, Z_D + 28, -PROY - 55, Z_D + 75, "c")
rect(-PROY - 135, Z_D - 12, -PROY - 110, Z_D + 12, "c")
rect(0, Z_AB - 16.7, R, Z_AB + 16.7, "i"); rect(-16.7, Z_AB - 16.7, 16.7, Z_ASIENTO, "i")           # tubo de salida interno
rect(-45, Z_ASIENTO, 45, Z_ASIENTO + 8, "i"); rect(-CART_DE / 2, Z_ASIENTO + 8, CART_DE / 2, Z_CART, "i h")
rect(-45, Z_CART, 45, Z_CART + 8, "i"); linea(0, Z_CART + 8, 0, Z_CART + 60, "i")
rect(R + 86, Z_SOLD + 380, R + 122, z_tapa + 340, "c")                              # pescante: columna, buje, brazo y bulón de ojo
rect(R + 78, Z_SOLD + 400, R + 130, Z_SOLD + 520, "c f"); rect(R, Z_SOLD + 440, R + 78, Z_SOLD + 480, "c f")
rect(-20, z_tapa + 320, R + 122, z_tapa + 340, "c f"); linea(0, z_tapa + 320, 0, z_tapa + 45, "c")
rect(-R - 30, Z_SOLD + L_CANO - 90, -R, Z_SOLD + L_CANO - 30, "c f")                 # oreja de izaje
rect(-50, Z_AB + 120, 50, Z_AB + 190, "c"); texto(0, Z_AB + 150, "placa", "q")        # placa de identificación
s.append(f'<line class="e" x1="{X(0):.1f}" y1="{Y(-40):.1f}" x2="{X(0):.1f}" y2="{Y(z_total + 60):.1f}"/>')
cota_v(-600, 0, Z_AB, f"{Z_AB:.0f}"); cota_v(-550, 0, Z_SOLD, f"{Z_SOLD:.0f}"); cota_v(-650, 0, z_brida, f"{n(z_brida, 0)}")
cota_v(400, 0, z_tapa, f"{n(z_tapa, 0)}"); cota_v(450, 0, z_total, f"≈ {n(z_total, 0)}"); cota_v(-500, 0, Z_D, f"{Z_D:.0f}")
linea(-PROY, Z_AB - 95, PROY, Z_AB - 95, "k"); linea(-PROY, Z_AB - 110, -PROY, Z_AB - 60, "k"); linea(PROY, Z_AB - 110, PROY, Z_AB - 60, "k")
texto(120, Z_AB - 95, f"{2 * PROY:.0f} entre caras", "q", dy=-4)
globo(-PROY - 40, Z_AB, "A"); globo(PROY + 40, Z_AB, "B"); globo(-PROY - 165, Z_D, "D"); globo(XF - 60, z_tapa + 250, "F"); globo(OD_BRIDA / 2 + 30, z_brida + 45, "M")
texto(0, -60, f"Ø {n(De, 1)} (6\" Sch 80) · 3 patas a 120° en círculo de anclaje Ø 330", "q")
tabla = [("A", "Entrada de gas", '1" #150 WNRF'), ("B", "Salida de gas", '1" #150 WNRF'), ("D", "Drenaje, con válvula y tapón", '3/4" #150 WNRF'),
         ("F", "Venteo, con válvula y tapón", '3/4" NPT #3000'), ("M", "Tapa de cierre con pescante", '6" #150 WNRF + ciega')]
ty = 60
s.append(f'<text class="h1" x="750" y="{ty - 22}">Conexiones</text>')
for i, (a, b, c) in enumerate(tabla):
    s.append(f'<text class="q" x="750" y="{ty + i * 18}">{a}</text><text class="q" x="772" y="{ty + i * 18}">{b}</text><text class="q" x="960" y="{ty + i * 18}">{c}</text>')
datos = [f"Diseño: {n(P_KG, 1)} kg/cm2 g · {MDMT}/{T_DIS} °C", f"Corrosión: {n(CA, 1)} mm · RT3 · PH {n(PH, 1)} kg/cm2 g", "ASME VIII Div.1, sin estampa",
         "Envolvente SA-106 Gr. B · casquete SA-234 WPB", "Bridas SA-105 · internos AISI 316 L", f"Volumen {n(vol, 1)} litros",
         f"Peso vacío ≈ {n(vacio, 0)} kg · en PH ≈ {n(p_ph, 0)} kg", "Elemento: 1 cartucho Ø 70 × 254 mm (a confirmar)"]
s.append(f'<text class="h1" x="750" y="{ty + 130}">Datos</text>')
for i, d in enumerate(datos):
    s.append(f'<text class="q" x="750" y="{ty + 152 + i * 18}">{d}</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 900" width="1180" height="900" font-family="Arial, Helvetica, sans-serif">
<style>.c{{fill:none;stroke:#111;stroke-width:1.4}}.f{{fill:#f2f2f2}}.i{{fill:none;stroke:#1565c0;stroke-width:1.1;stroke-dasharray:5 3}}.h{{fill:#e3f0fb}}
.e{{stroke:#b00;stroke-width:.7;stroke-dasharray:14 4 3 4}}.k{{stroke:#555;stroke-width:.7}}.p{{stroke:#111;stroke-width:2}}.g{{fill:#fff;stroke:#111;stroke-width:1}}
.t{{font-size:12px}}.q{{font-size:11.5px;fill:#222}}.b{{font-size:12px;font-weight:bold}}.h1{{font-size:14px;font-weight:bold}}.n{{font-size:11px;fill:#a00}}</style>
<rect width="1180" height="900" fill="#fff"/>
<text class="h1" x="20" y="26">FCC-707/708 · Filtro de gas de emergencia · Arreglo general preliminar (cotas en mm)</text>
<text class="n" x="20" y="44">BORRADOR, SIN REVISAR · COT26-0010-001 · predimensionamiento ITT para cotizar: no es plano de fabricación</text>
<text class="q" x="20" y="880">Línea azul de trazos: internos (tubo de salida, asiento y cartucho). Las orejas de izaje y la placa se muestran giradas al plano del dibujo.</text>
{chr(10).join(s)}
</svg>'''
(AQUI / "arreglo_general.svg").write_text(svg, encoding="utf-8")

o.append("## 10. Listado de materiales\n")
o.append("Está en `pedido/lista_materiales_plano.csv` (33 renglones por filtro), con el texto de la hoja de datos, cantidad, material y los datos de cada pieza en columnas.\n")
(AQUI / "dimensionamiento.md").write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"vacío {n(vacio)} kg · PH {n(p_ph)} kg · volumen {n(vol, 1)} l · tapa req {n(t_tapa)} mm (disp {n(T_BRIDA)})")
