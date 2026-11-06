"""Casos de prueba de herramientas/marcas_cliente.py (listado de marcas del cliente por renglón; Matías, 06-11-2026).
Salen de las Camuzzi 001/002/003 revisadas a mano contra el PDF del SCE-IN-501-0015 rev 1."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import marcas_cliente as mc  # noqa: E402

CLI = "CAMUZZI GAS PAMPEANA S.A. / CAMUZZI GAS DEL SUR S.A."
CASOS = [  # (descripción, comienzo esperado)
    ("VALVULA MONITORA PILOTADA OBT. GUIADO - NC", "Doma / Satesa"),
    ("VÁLVULA ESFÉRICA BRIDADA PASO REDUCIDO APF", "Esferomatic"),
    ("VÁLVULA ALIVIO CAP. REDUCIDA ROSCADA TIPO S-71", "Favra / Aerre / Farinola"),  # Doma no está en alivios
    ("Valvula reguladora de presion 1301F NPT con manometro", "Doma / Satesa"),  # la reguladora antes que el manómetro
    ("Válvula tapon lubricado", "Xomox"),
    ("CUPLA DE AC SOLD. 1/2\" NPT C/ VLV. ESF 1/2\" S3000", "Cupla: CH"),
    ("Cupla para soldar 1/2\" NPT S3000 ASTM A-105 para las tomas multiport, válvulas de alivio y manómetros", "CH / Thorsa"),
    ("Espárrago 5/8\" × 3 1/2\" A193 B7 con 2 tuercas 2H zincado (4 por junta de 3\")", "Delgado"),
    ("Junta espiralada 8\" #150 AISI 316/grafito (brida ciega)", "Klinger"),
    ("Brida Ciega (con junta espiralada de acero inoxidable)", "Futura / Francovigh"),
    ("Toberas del filtro FM-06: brida WN 6\" #150 RF sch 40 ASTM A105", "Futura / Francovigh"),
    ("VÁLVULA BLQ. Y PURG. C/ MANÓMETRO 0-6BAR", "Bloqueo y purga: ABAC"),
    ("Manómetro de presión diferencial con mánifold de 3 vías", "Manómetro: Ing. Capino"),
    ("Tapa de apertura rápida", "Tube Turn"),
    ("Indicador de nivel de vídrio (tipo Penberthy \" Reflex\" o similar)", "Jefferson"),
    ("Interruptor neumático de nivel", "Epta / Fisher"),
    ("SWITCH INDICADOR DE VALV MONITORA ABIERTA", "El listado"),
    ("Conector TE NPT", "El listado"),
    ("TE REDUCCIÓN", "Curvo Sold"),
    ("CAÑO 6\"", "El listado"),
    ("PRESIÓN REGULADA, C/ VAL. BLOQ Y PURGA", "Rosemount"),
]
mal = [(d, e, mc.marcas(CLI, d)) for d, e in CASOS if not mc.marcas(CLI, d).startswith(e)]
assert mc.marcas("YPF S.A.", "VÁLVULA ESFÉRICA") == "", "un cliente sin listado cargado no lleva marcas"
for d, e, r in mal:
    print(f"MAL: {d} → {r[:60]} (esperado {e})")
print("OK" if not mal else f"{len(mal)} casos mal")
sys.exit(1 if mal else 0)
