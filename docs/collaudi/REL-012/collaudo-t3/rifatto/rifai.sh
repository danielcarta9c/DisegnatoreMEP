#!/bin/bash
# Rifa' lo schema e la distinta del collaudo T3 di REL-012 dopo le correzioni delle riserve
# (numeri di tratta, ripresa, tabella delle tratte, termostati in tabella, rilievi), per la
# strada di un agente: la skill costruita da scripts/costruisci-skill.py, poi
#   grafo completo del collaudo -> disegna (A3, senza tabelle della distinta: REL-015, I-233)
#   -> anteprima -> distinta, a parte (PDF coi report Nove C se REPORT e' dato, I-232) -> consegna.
# Il grafo e' quello del collaudo, senza ritocchi; il piano e' quello del collaudo portato in A3
# (rifatto/piano.json, le note dicono che cosa e' cambiato). La pianta no: e' di un altro lavoro.
# Uso, dalla radice del repository:
#   [REPORT=<cartella di nove-c-report>] bash docs/collaudi/REL-012/collaudo-t3/rifatto/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../../.."
T3=docs/collaudi/REL-012/collaudo-t3
QUI=$T3/rifatto
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

rm -rf "$QUI/distinta" "$QUI/tavola"
$MEP disegna "$T3/grafo-completo.json" --piano "$QUI/piano.json" --out "$QUI/tavola" | tail -1
$MEP anteprima "$QUI/tavola/canalizzato-appartamento-secondo-piano-t1.pdf" \
    --out "$QUI/tavola/canalizzato-appartamento-secondo-piano-t1.png" --dpi 110
# La distinta esce con 2: restano voci DA DEFINIRE, come nel collaudo.
$MEP distinta "$T3/grafo-completo.json" --out "$QUI/distinta" --regole rules/distinta \
    --fornitura confermata ${REPORT:+--report "$REPORT"} > "$LAVORO/distinta.txt" || [ $? -eq 2 ]
sed -n 1p "$LAVORO/distinta.txt"
# Quello che il progettista riceve, in una cartella temporanea: solo i nomi.
$MEP consegna "$QUI/tavola" "$QUI/distinta" "$LAVORO/consegna" | sed "s|$LAVORO/||"
