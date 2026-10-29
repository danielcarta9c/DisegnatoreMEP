#!/bin/bash
# Rifa' lo schema e la distinta del collaudo T3 di REL-012 dopo le correzioni delle riserve
# (numeri di tratta, ripresa, tabella delle tratte, termostati in tabella, rilievi), per la
# strada di un agente: la skill costruita da scripts/costruisci-skill.py, poi
#   grafo completo del collaudo -> distinta (tratte e note sul foglio) -> disegna --tabelle
#   -> anteprima -> consegna.
# Il grafo e il piano sono quelli del collaudo, senza ritocchi. La pianta no: e' di un altro lavoro.
# Uso, dalla radice del repository:  bash docs/collaudi/REL-012/collaudo-t3/rifatto/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../../.."
T3=docs/collaudi/REL-012/collaudo-t3
QUI=$T3/rifatto
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

rm -rf "$QUI/distinta" "$QUI/tavola"
# La distinta esce con 2: restano voci DA DEFINIRE, come nel collaudo.
$MEP distinta "$T3/grafo-completo.json" --out "$QUI/distinta" --regole rules/distinta \
    --fornitura confermata --sul-foglio tratte,note > "$LAVORO/distinta.txt" || [ $? -eq 2 ]
sed -n 1p "$LAVORO/distinta.txt"
$MEP disegna "$T3/grafo-completo.json" --piano "$T3/piano.json" --out "$QUI/tavola" \
    --tabelle "$QUI/distinta/tabelle-del-foglio.json" | tail -1
$MEP anteprima "$QUI/tavola/canalizzato-appartamento-secondo-piano-t1.pdf" \
    --out "$QUI/tavola/canalizzato-appartamento-secondo-piano-t1.png" --dpi 110
# Quello che il progettista riceve, in una cartella temporanea: solo i nomi.
$MEP consegna "$QUI/tavola" "$QUI/distinta" "$LAVORO/consegna" | sed "s|$LAVORO/||"
