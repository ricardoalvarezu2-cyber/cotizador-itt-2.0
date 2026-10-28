"""Textos comunes de las 3 cotizaciones del Concurso de precios N° 24578 de Camuzzi (COT26-0135-001/002/003): oferta.json."""
import json


def oferta(carpeta, codigo, equipo, item_n, descripcion, cantidad, plazo, documentos, caracteristicas, desvios, alcance):
    o = {
        "estado": "borrador",
        "archivo_base": f"{codigo} - CAMUZZI CP24578 - {equipo.upper()}",
        "oferta": {"numero": "PRES [a asignar]", "revision": "A", "fecha": "28-10-2026", "descripcion_revision": "Emisión original"},
        "cliente": {"nombre": "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A.", "contacto": "Gerencia de Abastecimiento Obras y Almacenes",
                    "referencia": "Concurso de precios N° 24578 – Adquisición de SKID DE REGULACIÓN – MEDICIÓN",
                    "proyecto": "Renovación ERP Parque Industrial Tres Arroyos"},
        "objeto": ("El presente documento tiene por objeto establecer el alcance de nuestra Oferta {tipo} según los requerimientos solicitados por el cliente en el "
                   f"Concurso de precios N° 24578, ítem {item_n}: {cantidad} {descripcion}, en un todo de acuerdo con la documentación del concurso y con las aclaraciones y desvíos indicados en nuestra Oferta Técnica."),
        "item": {"item": str(item_n), "codigo": "", "descripcion": descripcion, "observacion": "Ver aclaraciones y desvíos", "plazo_dias": str(plazo)},
        "nota_flete": "Precio entregado en Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (flete a cargo de ITT, según la planilla del concurso). No incluye descarga.",
        "condiciones": {
            "CONDICIONES COMERCIALES": "Precios en dólares estadounidenses, sin IVA (21%). Facturación al tipo de cambio BNA divisa vendedor del día de la facturación, según las cláusulas particulares del concurso.",
            "PLAZO DE ENTREGA": f"{plazo} días corridos desde la orden de compra, sujeto a la aprobación de la documentación por Camuzzi en los plazos previstos.",
            "CONDICIONES DE PAGO": "Transferencia bancaria a 30 días de la fecha de presentación de la factura.",
            "LUGAR DE ENTREGA": "Transporte Cruz del Sur, Au. Riccheri y Boulogne Sur Mer, Mercado Central de Buenos Aires, nave D3, Tapiales.",
            "VALIDEZ DE OFERTA": "30 días corridos."},
        "embalaje": "Los equipos se acondicionarán para su transporte con tapas en las bridas y protección de equipos e instrumentos; preparados para izaje con grúa e identificados.",
        "documentos_cliente": documentos,
        "caracteristicas": caracteristicas,
        "imagen_plano": "",
        "aclaraciones_y_desvios": {"titulo": "ACLARACIONES Y DESVÍOS", "items": desvios},
        "exclusiones": {"titulo": "EXCLUSIONES GENERALES", "items": [
            "Materiales y/o trabajos no indicados en nuestro alcance.", "Descarga en destino, montaje e interconexión en campo.",
            "Juntas y espárragos de las conexiones del equipo con la planta.", "Pólizas de caución o garantía, si se requieren, se cotizan por separado."]},
        "alcance_general": {"titulo": "ALCANCE GENERAL", "items": alcance},
        "garantia": "Garantía general de 2 años desde la entrega o 1 año desde la instalación, lo que ocurra primero (especificación de Camuzzi), más las garantías particulares de materiales e instrumentos.",
        "firma": {"nombre": "Matías Russo", "cargo": "Representante Comercial", "telefono": "[teléfono ITT / interno]", "celular": "[celular]"},
    }
    json.dump(o, open(carpeta / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
