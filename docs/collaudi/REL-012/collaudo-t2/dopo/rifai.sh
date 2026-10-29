#!/bin/bash
# Rifa' le due tavole del collaudo T2 di REL-012 (centrale con pompa di calore, elettrico
# e regolazione su tavola a parte) dopo le correzioni di libreria e motore, per la strada
# di un agente:
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna (idraulica, elettrico) -> anteprima.
# Il piano dell'idraulica e' quello del collaudo; quello dell'elettrico e' ricomposto
# (i circolatori di zona hanno due cavi). Uso, dalla radice del repository:
#   bash docs/collaudi/REL-012/collaudo-t2/dopo/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../../.."
QUI=docs/collaudi/REL-012/collaudo-t2/dopo
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

python3 "$QUI/fai-il-grafo.py"
$MEP valida "$QUI/grafo.json" | sed -n 1p
$MEP completa "$QUI/grafo.json" --out "$QUI/grafo-completo.json" | sed -n 1p

rm -rf "$QUI/tavola"
for vista in idraulica elettrico; do
    $MEP disegna "$QUI/grafo-completo.json" --piano "$QUI/piano-$vista.json" --out "$LAVORO/tavola" | tail -1
done
mkdir -p "$QUI/tavola"
cp "$LAVORO"/tavola/*.pdf "$LAVORO"/tavola/*-rilievi.md "$QUI/tavola/"
for pdf in "$QUI"/tavola/*.pdf; do
    $MEP anteprima "$pdf" --out "${pdf%.pdf}.png" --dpi 110 > /dev/null
done
