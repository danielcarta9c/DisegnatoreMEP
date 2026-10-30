#!/bin/bash
# Rifa' i PDF della distinta di REL-015 (I-232) con la skill dei report Nove C, per la strada
# di un agente: la skill costruita da scripts/costruisci-skill.py, poi completa -> distinta
# --report. Due casi: la M.02 del kit (AA-01) e il canalizzato del collaudo T3. Le pagine in
# PNG per guardarle.
# Uso, dalla radice del repository:
#   REPORT=<cartella della skill nove-c-report> bash docs/collaudi/REL-015/distinta/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../.."
: "${REPORT:?serve REPORT, la cartella della skill nove-c-report}"
QUI=docs/collaudi/REL-015/distinta
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

python3 docs/collaudi/REL-012/fase-2/fai-il-grafo.py > /dev/null
$MEP completa docs/collaudi/REL-012/fase-2/grafo.json --out "$LAVORO/aa01.json" > /dev/null
# La distinta esce con 2: restano voci DA DEFINIRE.
for caso in "AA-01:$LAVORO/aa01.json" "collaudo-t3:docs/collaudi/REL-012/collaudo-t3/grafo-completo.json"; do
    nome=${caso%%:*}; grafo=${caso#*:}
    rm -rf "${QUI:?}/$nome"
    $MEP distinta "$grafo" --out "$QUI/$nome" --regole rules/distinta --fornitura confermata \
        --report "$REPORT" > "$LAVORO/$nome.txt" || [ $? -eq 2 ]
    sed -n 1p "$LAVORO/$nome.txt"
    pdf=$(ls "$QUI/$nome"/*.pdf)
    pagine="${pdf%.pdf}-pagine"
    mkdir -p "$pagine"
    pdftoppm -r 80 -png "$pdf" "$pagine/qa"
    for f in "$pagine"/qa-*.png; do n=${f##*qa-}; nuovo="$pagine/qa-$((10#${n%.png})).png"; [ "$f" = "$nuovo" ] || mv "$f" "$nuovo"; done
done
