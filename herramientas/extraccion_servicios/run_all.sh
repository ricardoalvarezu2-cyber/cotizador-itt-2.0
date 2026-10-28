cd /tmp/claude-0/-home-user-cotizador-itt/82ad64dc-b6db-5ba7-866e-adf8ec6ac548/scratchpad
rm -f /home/user/cotizador-itt/conocimiento/precios/servicios_extraidos.csv
for f in b[0-9][0-9]_*.py; do python3 $f; done
wc -l /home/user/cotizador-itt/conocimiento/precios/servicios_extraidos.csv
