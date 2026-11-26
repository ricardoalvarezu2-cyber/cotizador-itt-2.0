# Verificación contra el plano: puente de inyección y regulación 2" #600 (YPF Gas Lift, SAP 1000653143)

**Borrador, sin revisar. No se manda nada al cliente.** Hecha el 26-11-2026 a pedido de Ricardo Álvarez. No tiene auditoría independiente: por la regla de ahorro de tokens del 25-11-2026 no se lanzó el agente.

## Qué se comparó
- **Documentos del cliente** (en `pedido/`):
  - plano conjunto YPF-GASLIFTPTE-VCD24299-P-PL-003003 D2 con redmarks de YPF del 05-11-2025 (SK-111, 2 puentes por skid);
  - P&ID YPF-GASLIFTLOC1-VCD24299-R-PI-003012 D2 (H2) con redmarks;
  - plano de estructura YPF-GASLIFTPTE-VCD24299-C-PL-003004 D1 con redmarks;
  - HD de instrumentos YPF-GASLIFTPTE-VCD24299-I-HD-003004 D1.
- **Cotizaciones de ITT:**
  - **rev. 1**: el archivo que pasó Ricardo, `Cot_Puente_Iny_y_Reg_2pulg_serie600_SAP_1000653143_rev1.xlsx`, con costo de 72.236,73 por skid;
  - **rev. 2**: la vigente del repositorio, `fuentes_originales/ofertas_texto/TAVAL/70- PUENTES DE MEDICION 2 PULGADAS/…/REV 1- OFERTA MEJORADA/Cot Puente Gas Lift SAP 1000653143 rev. 2 - PC0.xlsx`, hoja "Cotización rev 1" del 26-10-2026, con costo de 73.561,53 por skid. Es el caso de control `CTRL-P01`.
- Las cantidades van **por skid**, que lleva **2 puentes**, como en las dos planillas.

## Cómo queda el puente con los redmarks (por puente)
El gas entra del colector de 3" y sale por la brida de 2". En el plano, de derecha a izquierda:
1. VF 2" #600, la que queda.
2. VF 2" eliminada (nota 3).
3. Filtro Y FY 2" #600, con purga de ¾".
4. Venteo de ¾".
5. V-cone FE 2" #600 con manifold M5 de 5 vías, FQIT y botellones de purga (notas 8 y 10).
6. TW XXXA, que queda en la línea.
7. PIT eliminado (nota 9).
8. Inyección de químicos IQ 1" NPT con VF.
9. Bypass en dos niveles (nota 5), según el esquema del P&ID: TE/TIT XXXA, 2 VE 2" #600, la FV 2" arriba, el bypass de abajo con VE 1" #600 + VG 1" #600 y TE/TIT XXXC.
10. Una sola brida con dos juntas y un espaciador para el orificio de restricción (nota 3 del P&ID).
11. VR 2" #600.
12. PI XXXD con M2 de ½".
13. Venteo y purga de ¾".
14. VF de salida eliminada (notas 1 y 7).
15. Brida de salida de 2".

## Diferencias, por skid (2 puentes)

| Renglón | Plano / P&ID (conteo ITT) | rev. 1 | rev. 2 | Comentario |
|---|---|---|---|---|
| Esférica 2" #600 | **6** (1 VF + 2 VE por puente) | 10 | 8 | Las dos cuentan de más: la rev. 2 todavía suma 2 VF eliminadas. |
| Esférica 1" #600 + globo 1" #600 (bypass) | 2 + 2 | — | 2 + 2 | Faltan en la rev. 1. |
| Válvulas chicas 2000# | **¾": 8 · ½": 6 · 1": 2** | 16 esféricas 1" #3000 | ½": 4 · ¾": 2 | Rev. 1: medida y serie equivocadas. Rev. 2: faltan 6 de ¾", 2 de ½" y las 2 de 1" de la IQ. Por puente: 4 de ¾" (venteos y purgas), ½" del PI + 2 de las tomas del V-cone, 1" de la IQ. |
| Retención 2" #600 · filtro Y 2" #600 · FV globo 2" con actuador | 2 · 2 · 2 | 2 · 2 · 2 | 2 · 2 · 2 | Bien. |
| Brida WNRF 2" #600 | **34** (17 por puente) | 48 | 48 | Sobran 14. Por puente: VF 2, FY 2, V-cone 2, VE 4, FV 2, orificio 2, VR 2 y salida 1. |
| Junta espiralada 2" #600 | **32** (16 por puente; la brida de salida va con la del cliente) | **94** (48 + 46: renglón repetido) | 46 | Rev. 1 cuenta dos veces las juntas. Rev. 2: sobran 14. |
| Espárragos 2" #600 | **240** (30 uniones × 8) de 5/8" × 4 1/4" | 368 de 5/8" × 5" | 368 de 5/8" × 5" | Sobran 128. La medida sale de `tecnico/esparragos_por_brida.csv`; los de la unión con espaciador van más largos. |
| Espaciador / portaorificio 2" #600 | **2** | — | — | Falta en las dos (nota 3 del P&ID). |
| Bridas, juntas y espárragos de 1" #600 (bypass) | 4 bridas, 6 juntas, 24 espárragos de 5/8" × 3 3/4" | — | — | Faltan. ITT supone válvulas de 1" bridadas RF: el P&ID dice "1" #600" sin extremos. A confirmar. |
| Termovainas 1½" #600 y sus conexiones | **6 TW** (por puente: TW de la FQIT + TE XXXA + TE XXXC) | 2 bridas 1½" + 2 tees 2"×1½" | Ídem | Faltan 4 bridas de 1½", 4 tees o derivaciones, 6 juntas y 24 espárragos de 3/4" × 4 1/4". **HD nota (4): hay que ampliar la línea de 2" a 3" en cada TE a 90°** (reducciones 3"×2" y tee 3"). No está en ninguna de las dos. |
| TE + TIT con indicación local | **4 TE/TW + 4 TIT** (P&ID: XXXA y XXXC por puente) | 4 "transmisor completo" + 2 TW/TE | 2 TE/TW + 2 TIT (bypass) + 2 TE/TW (FQIT) | Rev. 2: faltan 2 TE/TW y 2 TIT. La nota **** del P&ID pide uno para el gas de llegada y uno por tramo aguas abajo, o sea 3 por skid; el esquema dibuja 4. La HD solo tiene la hoja TIT-XXXC. A consultar. |
| FQIT (multivariable con totalizador) | **2** (uno por puente) + manifold M5 + botellones | **1** computador XFC6200EX | 2 × 266CSH + M5 + botellones | Rev. 1 tiene uno solo. La nota ** pide lectura local que no se apague (DP en pulgadas de agua, P en kg/cm² y caudal en m³/d): confirmar que el modelo la tenga. |
| PIT | 0 (eliminado, nota 9) | — | — | La HD todavía trae la hoja del PIT-XXXA: diferencia entre documentos. |
| PI + M2 ½" | 2 + 2 | 2 manómetros | 2 manómetros | Falta el M2 (manifold de 2 vías). La HD pide la válvula integral de bloqueo y purga. |
| Inyector de químicos (IQ) | La conexión de 1" NPT con VF va; el inyector no tiene HD | 2 × 2.100 en el piping **y** excluido en el texto | Ídem | En las dos se cobra el inyector y a la vez se excluye en la oferta. Hay que sacarlo o sacar la exclusión. |
| Estructura | **907 kg por skid**: el C-PL da 2.721,0 kg para el módulo de 3 skids, 15 % de uniones incluido | 1.200 kg | 1.200 kg | El 1.200 cubre de sobra. Los redmarks achican el largo (7.960) y el ancho. |
| Pintura del skid | **21,3 m² por skid** (64,0 m² ÷ 3) | 15 m² | 18 m² | Faltan unos 3 m² en la rev. 2. |

## Qué sigue igual
- El colector de 3" (2 bridas, 4 m y 2 tees 3"×2").
- MO de Ledesma, MO de ITT, calidad, ingeniería y asistencia.
- Los END: hay que bajarlos porque hay 14 bridas menos, o sea 14 soldaduras BW menos. Se recalculan con el cómputo.

## Precios
- No se pudo usar la carpeta de precios de proveedores (`C:\Users\ralvarez\OneDrive - Taval S.A\01- COMERCIAL\00- ACTIVACION\Precios proveedores`): está en la PC de Ricardo y esta sesión no tiene esa computadora conectada.
- Para recotizar con esos precios hay dos caminos: conectar la PC a la sesión (Remote Control en la app de escritorio) o subir los archivos.
- Mientras tanto, los precios de referencia son los de la rev. 2 y el catálogo del repositorio. Por ejemplo, la esférica de 1" #600 está a 53,22 (de la misma rev. 2).

## Decisiones de ITT y consultas
1. **ITT:** las válvulas de 1" #600 del bypass van bridadas RF.
2. **Consulta:** cuántos TIT con indicación local van, 3 o 4 por skid.
3. **Consulta:** el tramo de 3" para los TE (HD nota 4); se cotiza.
4. **Consulta:** el PIT figura en la HD pero el P&ID lo elimina; no se cotiza.
5. El inyector de químicos sigue excluido porque no tiene HD. La conexión de 1" con su válvula sí va.
