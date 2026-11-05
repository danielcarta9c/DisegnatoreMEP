#!/bin/bash
# Rifa' la tavola dell'elettrico del grafo minimo con l'interruttore
# magnetotermico differenziale sulla linea della pompa di calore (REL-018, I-278),
# per la strada di un agente:
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna (elettrico) -> anteprima.
# Uso, dalla radice del repository:
#   bash docs/collaudi/REL-018/protezione/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../.."
QUI=docs/collaudi/REL-018/protezione
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

python3 "$QUI/fai-il-grafo.py"
$MEP valida "$QUI/grafo.json" | sed -n 1p
$MEP completa "$QUI/grafo.json" --out "$QUI/grafo-completo.json" > "$QUI/completa.txt"
sed -n 1p "$QUI/completa.txt"

rm -rf "$QUI/tavola"
$MEP disegna "$QUI/grafo-completo.json" --piano "$QUI/piano-elettrico.json" --out "$LAVORO/tavola" | tail -1
mkdir -p "$QUI/tavola"
cp "$LAVORO"/tavola/*.pdf "$LAVORO"/tavola/*-rilievi.md "$QUI/tavola/"
for pdf in "$QUI"/tavola/*.pdf; do
    $MEP anteprima "$pdf" --out "${pdf%.pdf}.png" --dpi 110 > /dev/null
done
