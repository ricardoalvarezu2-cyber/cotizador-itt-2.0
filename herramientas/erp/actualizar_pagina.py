"""Publica la plantilla actual en la página de GitHub Pages sin volver a leer la base.

La página (rama datos-erp) es index.html = plantilla.html + <script src="datos.js">.
Cuando se cambia herramientas/erp/plantilla.html en main, correr:

    python herramientas/erp/actualizar_pagina.py [remoto]   (remoto por defecto: el que apunta al repo de Ricardo)

Baja la rama datos-erp, rearma index.html con la plantilla de este checkout (los datos
quedan como están) y sube un commit a datos-erp. Si la rama todavía no tiene datos.js,
lo saca de la página completa "Cruce SC-OC (sistema).html".
"""
import os, subprocess, sys, tempfile, time

MARCA = '<script>/*DATOS_ERP*/</script>'
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(AQUI))


def git(*a, cwd=REPO, salida=True):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        sys.exit('git ' + ' '.join(a) + ' falló:\n' + r.stderr)
    return r.stdout if salida else None


def remoto_ricardo():
    for linea in git('remote', '-v').splitlines():
        if 'ricardoalvarezu2-cyber/cotizador-itt-2.0' in linea.lower():
            return linea.split()[0]
    sys.exit('No hay remoto del repositorio de Ricardo: pasarlo como argumento.')


def main():
    remoto = sys.argv[1] if len(sys.argv) > 1 else remoto_ricardo()
    plantilla = open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8-sig').read()
    if plantilla.count(MARCA) != 1:
        sys.exit('La plantilla no tiene una sola vez la marca ' + MARCA)
    git('fetch', '-q', remoto, 'datos-erp')
    tmp = tempfile.mkdtemp(prefix='datos-erp-')
    git('worktree', 'add', '-q', '--detach', tmp, 'FETCH_HEAD')
    try:
        js = os.path.join(tmp, 'datos.js')
        if not os.path.exists(js):
            completa = open(os.path.join(tmp, 'Cruce SC-OC (sistema).html'), encoding='utf-8').read()
            i = completa.index('<script>window.DATOS_ERP = ') + len('<script>')
            j = completa.index('</script>', i)
            open(js, 'w', encoding='utf-8', newline='').write(completa[i:j])
        sello = time.strftime('%Y%m%d%H%M%S')
        html = plantilla.replace(MARCA, '<script src="datos.js?v=' + sello + '"></script>')
        open(os.path.join(tmp, 'index.html'), 'w', encoding='utf-8', newline='').write(html)
        open(os.path.join(tmp, '.nojekyll'), 'w').write('\n')
        git('add', 'index.html', 'datos.js', '.nojekyll', cwd=tmp)
        if not git('status', '--porcelain', cwd=tmp).strip():
            print('La página ya estaba al día.')
            return
        git('commit', '-q', '-m', 'Página: plantilla actualizada ' + time.strftime('%d-%m-%Y %H:%M'), cwd=tmp)
        git('-c', 'push.negotiate=true', 'push', '-q', remoto, 'HEAD:refs/heads/datos-erp', cwd=tmp)
        print('Página actualizada en la rama datos-erp de', remoto, '(GitHub Pages la publica en 1 o 2 minutos).')
    finally:
        git('worktree', 'remove', '--force', tmp)


if __name__ == '__main__':
    main()
