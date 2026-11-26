"""Arma herramientas/erp/zip/cruce_erp_itt.zip con lo que va a la carpeta de la PC de ITT.

    python herramientas/erp/armar_zip.py

Lleva ACTUALIZAR.bat, cruce_erp.ps1, plantilla.html y zip/LEEME.txt. Nunca los .udl ni github_token.txt
(así extraer el zip no pisa la contraseña ni el token). Correrlo después de cambiar el .bat o el .ps1,
mandarle el zip a Matías y pedirle que lo extraiga encima de lo anterior.
"""
import os, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCHIVOS = [('ACTUALIZAR.bat', 'ACTUALIZAR.bat'), ('cruce_erp.ps1', 'cruce_erp.ps1'),
            ('plantilla.html', 'plantilla.html'), (os.path.join('zip', 'LEEME.txt'), 'LEEME.txt')]


def main():
    ps1 = open(os.path.join(AQUI, 'cruce_erp.ps1'), 'rb').read()
    assert ps1.startswith(b'\xef\xbb\xbf') and b'\r\n' in ps1, 'cruce_erp.ps1 tiene que ir en UTF-8 con BOM y CRLF'
    assert b'\r\n' in open(os.path.join(AQUI, 'ACTUALIZAR.bat'), 'rb').read(), 'ACTUALIZAR.bat tiene que ir con CRLF'
    salida = os.path.join(AQUI, 'zip', 'cruce_erp_itt.zip')
    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as z:
        for origen, nombre in ARCHIVOS:
            z.write(os.path.join(AQUI, origen), nombre)
    print('Zip armado:', salida)


if __name__ == '__main__':
    main()
