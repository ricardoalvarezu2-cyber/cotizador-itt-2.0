# Tarea diaria: revisar la carpeta de Drive de precios

Pedido de Matías (05-11-2026): todos los días hábiles a la mañana, revisar si hay información nueva en la carpeta de Drive
https://drive.google.com/drive/folders/1gCEHg1TNIoa5UVKoa4x7AM8buw3Yjyck (ID `1gCEHg1TNIoa5UVKoa4x7AM8buw3Yjyck`,
dueño ricardoalvarezu2@gmail.com) y cargarla al cotizador. Nunca se envía nada a nadie: solo se carga al repositorio.

## Pasos
1. Trabajar sobre `main` del repositorio `tvmaty2186/cotizador-itt` (`git pull`). Leer `CLAUDE.md` y `conocimiento/estado_y_pendientes.md`.
2. Listar la carpeta con el conector de Google Drive (`search_files`, query `parentId = '1gCEHg1TNIoa5UVKoa4x7AM8buw3Yjyck'`,
   paginar hasta el final; incluir subcarpetas).
3. Comparar con `fuentes_originales/listas_vendedor/drive_procesados.csv` por `drive_id` y `modificado_drive`.
   Es nuevo un archivo cuyo `drive_id` no está, o que está con otra fecha de modificación (versión nueva).
4. **Si no hay nada nuevo:** no tocar el repositorio y terminar con una línea: "Drive de precios: sin novedades (N archivos)".
5. **Si hay nuevos:** bajarlos (`download_file_content`), leerlos completos y, según lo que sean:
   - Lista o cotización de proveedor: guardarla en `fuentes_originales/listas_vendedor/<fecha de hoy AAAA-MM-DD>/` con el nombre
     `<proveedor>_<lista|cotizacion>_<nro>_<fecha del documento AAAA-MM-DD>.<ext>`, sumar al README de esa carpeta qué es, y
     cargarla con `python herramientas/listas_vendedor.py` (si el formato no es conocido, agregar el lector siguiendo los de
     Miyashiro y Oil Metal, con control cantidad × precio = importe, y casos en `herramientas/test_catalogo.py`).
     Después `python herramientas/actualizar_base.py` (catálogo) y `python herramientas/revisar_cambio_busqueda.py --control`.
   - Si es un archivo que ya está en el repositorio con otro nombre (mismo tamaño o mismo contenido): solo anotarlo.
   - Cualquier otra cosa (plano, pliego, ET, mail): guardarla en `fuentes_originales/` donde corresponda y anotarla; no cotizar.
   Reglas de siempre: precios sin IVA, USD (pesos con el dólar oficial BNA del mes), fecha del documento, números con
   `herramientas/numeros.py`. Un número que no se puede leer con seguridad no se carga: se anota como pendiente.
6. Sumar cada archivo a `drive_procesados.csv` (id, nombre, modificado, archivo en el repo, fecha de proceso y nota).
7. `python herramientas/verificar_todo.py` tiene que dar "TODO OK". Si un control o un resultado del buscador se mueve por los
   precios nuevos, revisar cada cambio; aceptar solo si tiene sentido y anotarlo en `conocimiento/estado_y_pendientes.md`.
   Si algo falla y no se puede resolver con las reglas, **no pasar a `main`**: dejar la rama subida y avisar.
8. Regenerar la página (`python web/construir_datos.py && python web/armar_pagina.py`) y publicarla (ver `web/LEEME.md`).
9. Commit y `python herramientas/subir_a_main.py "Drive de precios: <qué entró>"`.
10. Resumen final corto (para Matías): qué archivos entraron, cuántos precios nuevos o actualizados, errores y lo que necesita decidir.
