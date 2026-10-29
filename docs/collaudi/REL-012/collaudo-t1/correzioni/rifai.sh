#!/bin/bash
# Rifa' lo schema del collaudo T1 di REL-012 (canalizzato a quattro uscite) dopo le
# correzioni di libreria e motore, per la strada di un agente:
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna -> anteprima.
# Senza la distinta e le tabelle sul foglio: sono di un altro lavoro (REL-013).
# Uso, dalla radice del repository:  bash docs/collaudi/REL-012/collaudo-t1/correzioni/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../../.."
QUI=docs/collaudi/REL-012/collaudo-t1/correzioni
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

python3 "$QUI/fai-il-grafo.py"
$MEP valida "$QUI/grafo.json" | sed -n 1p
$MEP completa "$QUI/grafo.json" --out "$LAVORO/grafo-completo.json" | sed -n 1p

rm -rf "$QUI/tavola"
$MEP disegna "$LAVORO/grafo-completo.json" --piano "$QUI/piano.json" --out "$QUI/tavola" | tail -1
for pdf in "$QUI"/tavola/*.pdf; do
    $MEP anteprima "$pdf" --out "${pdf%.pdf}.png" --dpi 110 > /dev/null
done
