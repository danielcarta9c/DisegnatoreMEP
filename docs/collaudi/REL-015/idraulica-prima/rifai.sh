#!/bin/bash
# Rifa' le immagini «dopo» della prova di REL-015, punto 3 (I-231): prima l'idraulica, poi
# l'elettrico. Le «prima» sono quelle della 1.6.0 e non si toccano.
# Le tavole dell'aria (M.02, collaudo T1, collaudo T3) e la vista idraulica del collaudo T2 si
# rifanno coi loro rifai.sh, che vanno girati prima; qui se ne copia l'anteprima. Le tavole
# della fase 3 di REL-012 e la tavola di prova della fase 1 si disegnano qui.
# Uso, dalla radice del repository:  bash docs/collaudi/REL-015/idraulica-prima/rifai.sh
set -euo pipefail
cd "$(dirname "$0")/../../../.."
QUI=docs/collaudi/REL-015/idraulica-prima
F3=docs/collaudi/REL-012/fase-3
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

disegna() {  # <grafo> <piano> <nome dell'immagine>
    $MEP disegna "$1" --piano "$2" --out "$LAVORO/$3" | tail -1 || true
    $MEP anteprima "$(ls "$LAVORO/$3"/*.pdf | head -1)" --out "$QUI/$3-dopo.png" --dpi 110 > /dev/null
}
disegna "$F3/piccolo/grafo-completo.json" "$F3/piccolo/piano.json" fase-3-piccolo
disegna "$F3/centrale/grafo-completo.json" "$F3/centrale/piano-tutto.json" fase-3-centrale-tavola-unica
disegna "$F3/centrale/grafo-completo.json" "$F3/centrale/piano-idraulica.json" fase-3-centrale-idraulica

PYTHONPATH=src python3 examples/aria_elettrico/tavola_di_prova.py "$LAVORO/fase-1" > /dev/null
$MEP anteprima "$(ls "$LAVORO/fase-1"/*.pdf | head -1)" --out "$QUI/fase-1-dopo.png" --dpi 110 > /dev/null

cp docs/collaudi/REL-012/fase-2/tavola/caso-prova-aria-aria-t1.png "$QUI/fase-2-m02-dopo.png"
cp docs/collaudi/REL-012/collaudo-t1/correzioni/tavola/canalizzato-appartamento-secondo-piano-t1.png \
    "$QUI/collaudo-t1-correzioni-dopo.png"
cp docs/collaudi/REL-012/collaudo-t3/rifatto/tavola/canalizzato-appartamento-secondo-piano-t1.png \
    "$QUI/collaudo-t3-rifatto-dopo.png"
cp "$(ls docs/collaudi/REL-012/collaudo-t2/dopo/tavola/*idraulica*.png | head -1)" "$QUI/collaudo-t2-idraulica-dopo.png"
ls "$QUI"
