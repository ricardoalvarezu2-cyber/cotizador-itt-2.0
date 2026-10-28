# CTRL-F01 — Caso de control: filtro FM2 #300 (INARTECO, lic. 9333)

**No es una cotización para el cliente.** Es un caso de control del cotizador: se toma un equipo que ya se costeó (planilla
`TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx`, 15-01-2026, hoja "Filtro FM2 300")
y se compara lo que da la precotización automática (sin IA) contra el costo real, renglón por renglón.

## Cómo se arma (28-10-2026)
1. `pedido/lista_materiales_plano.csv`: las 27 posiciones de la hoja de la planilla (diámetros de mm a pulgadas; extremos definidos
   con el armado que muestra la planilla: cuerpo de 4" con brida slip-on y casquete; dos picos de 2" con brida slip-on, uno con codo,
   soldados al cuerpo con refuerzo tipo poncho).
2. `historico.csv`: el costo real por filtro (materiales 1.504,15 = 1.424,30 + válvula 44,85 + repuesto 35; MO y servicios 2.979,82;
   total 4.483,97, igual a la planilla).
3. `python herramientas/precotizar.py cotizaciones/CTRL-F01_INARTECO_FM2_S300 --excluir "TAVAL/40" --excluir "INARTECO"`
   (el propio proyecto no puede ser su referencia: sus precios ya están en el catálogo).
4. `python herramientas/comparar_historico.py cotizaciones/CTRL-F01_INARTECO_FM2_S300` → `comparacion_historico.md`.

## Resultado
Precotización automática sin completar: USD 1.126,55 contra USD 4.483,97 reales por filtro (−75%).
- Soldadura: −13% (bien). Bridas: −1% a +16% (bien). Espárragos: igual.
- Radiografía y tinta penetrante: real USD 1.804,20 (40% del costo); el cotizador pone 0 porque `rx_pct` está en 0. Sale del pliego.
- Ingeniería, calidad y montaje: real USD 720 (16%); el cotizador lo deja "a completar".
- Caño: la planilla compra la barra entera de 6 m por filtro. Desde este caso `precotizar.py` agrega la fila de compra extra (4b, 5b).
- 9 piezas sin precio en el catálogo: elemento filtrante, chapas SAE 1010 por kg, refuerzo tipo poncho, chapa de identificación,
  varilla, asas. 12 similares lejos del real (arandelas a USD 0,17, junta espiral 4" #300 a USD 72,50 contra 15, manómetro común
  contra diferencial).

## Correcciones que salieron de este caso
- `catalogo_materiales.familia_de`: "media cupla … conexión manómetro" y "chapa soporte manómetro" se clasificaban como instrumento.
  Ahora manda la pieza (el catálogo actual no cambió).
- `precotizar.py`: opción `--excluir`; fila de compra extra para completar la barra de caño; avisos en rojo de radiografía en 0% y
  de horas de ingeniería, calidad y montaje.
