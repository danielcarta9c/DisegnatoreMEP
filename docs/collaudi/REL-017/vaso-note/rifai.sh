#!/bin/bash
# Rifa' la tavola idraulica della villetta con il vaso sanitario posato dalla regola e le note
# di posa del progettista (REL-017, I-271, I-272), per la strada di un agente:
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna (idraulica) -> anteprima.
# Uso, dalla radice del repository:
#   bash docs/collaudi/REL-017/vaso-note/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../.."
QUI=docs/collaudi/REL-017/vaso-note
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

python3 "$QUI/fai-il-grafo.py"
$MEP valida "$QUI/grafo.json" | sed -n 1p
$MEP completa "$QUI/grafo.json" --out "$QUI/grafo-completo.json" | sed -n 1p

rm -rf "$QUI/tavola"
$MEP disegna "$QUI/grafo-completo.json" --piano "$QUI/piano-idraulica.json" --out "$LAVORO/tavola" | tail -1
mkdir -p "$QUI/tavola"
cp "$LAVORO"/tavola/*.pdf "$LAVORO"/tavola/*-rilievi.md "$QUI/tavola/"
for pdf in "$QUI"/tavola/*.pdf; do
    $MEP anteprima "$pdf" --out "${pdf%.pdf}.png" --dpi 110 > /dev/null
done
