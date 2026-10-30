#!/bin/bash
# Rifa' la villetta del collaudo della 1.7.0 col collettore a sei vie (REL-016, D3), per la strada
# di un agente: la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna -> anteprima.
# Il grafo e' quello del collaudo (../casi-del-collaudo/villetta-grafo.json) col collettore a sei
# vie e sei pannelli al posto del pannello rappresentativo (fai-il-grafo.py); il piano e' il piano
# buono del collaudo col collettore e i pannelli, in A2 (piano.json, le note dicono perche').
# Uso, dalla radice del repository:  bash docs/collaudi/REL-016/d3/rifai.sh
# Scrive in docs/collaudi/REL-016/d3/tavola/; la skill in una cartella temporanea.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
QUI=docs/collaudi/REL-016/d3
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

# Capire: il grafo del collaudo, col collettore a sei vie.
python3 "$QUI/fai-il-grafo.py"
$MEP valida "$QUI/grafo.json" | sed -n 1p
$MEP completa "$QUI/grafo.json" --out "$LAVORO/grafo-completo.json" | sed -n 1p

# Eseguire: la vista dell'idraulica, come nel collaudo.
rm -rf "$QUI/tavola"
$MEP disegna "$LAVORO/grafo-completo.json" --piano "$QUI/piano.json" --out "$QUI/tavola" | tail -1
$MEP anteprima "$QUI/tavola/villetta-pdc-aria-acqua-idraulica-t1.pdf" \
    --out "$QUI/tavola/villetta-pdc-aria-acqua-idraulica-t1.png" --dpi 110
