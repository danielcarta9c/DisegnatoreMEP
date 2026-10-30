#!/bin/bash
# Rifa' la M.02 del kit aria-aria con la skill, per la strada di un agente (REL-012, fase 2;
# REL-015: in A3, sulla tavola solo la tabella delle apparecchiature e la legenda, I-233):
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna -> anteprima; la distinta a parte.
# La distinta e' un documento per l'installatore, non una tabella sul foglio (I-232): col
# percorso della skill dei report Nove C in REPORT esce in PDF, senza in Markdown.
# Uso, dalla radice del repository:  [REPORT=<cartella di nove-c-report>] bash docs/collaudi/REL-012/fase-2/rifai.sh
# Scrive in docs/collaudi/REL-012/fase-2/tavola/ e distinta/; la skill in una cartella temporanea.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
QUI=docs/collaudi/REL-012/fase-2
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

# Capire: il grafo dell'esempio AA-01, coi tre campi del tratto in testa alla tubazione.
python3 "$QUI/fai-il-grafo.py"
$MEP valida "$QUI/grafo.json" | sed -n 1p
$MEP completa "$QUI/grafo.json" --out "$LAVORO/grafo-completo.json" | sed -n 1p

# Eseguire: il piano del kit, in A3, senza zone e senza file di tabelle.
rm -rf "$QUI/distinta" "$QUI/tavola"
$MEP disegna "$LAVORO/grafo-completo.json" --piano "$QUI/piano.json" --out "$QUI/tavola" | tail -1
$MEP anteprima "$QUI/tavola/caso-prova-aria-aria-t1.pdf" --out "$QUI/tavola/caso-prova-aria-aria-t1.png" --dpi 110

# La distinta, a parte: le regole dal repository.
$MEP distinta "$LAVORO/grafo-completo.json" --out "$QUI/distinta" --regole rules/distinta \
    ${REPORT:+--report "$REPORT"} | sed -n 1p

# Il confronto affiancato con la tavola del kit.
python3 "$QUI/confronto.py"
