#!/bin/bash
# Rifa' la M.02 del kit aria-aria con la skill, per la strada di un agente (REL-012, fase 2):
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> distinta -> disegna --tabelle -> anteprima.
# Uso, dalla radice del repository:  bash docs/collaudi/REL-012/fase-2/rifai.sh
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

# La distinta: le regole non sono ancora nella skill costruita (REL-013, RAPPORTO §6.2).
rm -rf "$QUI/distinta" "$QUI/tavola"
$MEP distinta "$LAVORO/grafo-completo.json" --out "$QUI/distinta" --regole rules/distinta | sed -n 1p

# Eseguire: il piano del kit, le tabelle della distinta e le note di progetto.
$MEP disegna "$LAVORO/grafo-completo.json" --piano "$QUI/piano.json" --out "$QUI/tavola" \
    --tabelle "$QUI/distinta/tabelle-del-foglio.json" --tabelle "$QUI/note-di-progetto.json" | tail -1
$MEP anteprima "$QUI/tavola/caso-prova-aria-aria-t1.pdf" --out "$QUI/tavola/caso-prova-aria-aria-t1.png" --dpi 110

# Il confronto affiancato con la tavola del kit.
python3 "$QUI/confronto.py"
