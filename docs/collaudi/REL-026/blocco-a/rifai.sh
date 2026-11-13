#!/bin/bash
# Rifa' le tavole del blocco A di REL-026 per la strada di un agente:
#   la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> valida -> completa -> disegna -> anteprima; la distinta a parte.
# Uso, dalla radice del repository:  bash docs/collaudi/REL-026/blocco-a/rifai.sh [python]
# Scrive in docs/collaudi/REL-026/blocco-a/<caso>/; la skill in una cartella temporanea.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
PY=${1:-python3}
QUI=docs/collaudi/REL-026/blocco-a
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

$PY scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="$PY $LAVORO/skill/disegnatore-mep/scripts/mep.py"

# Capire: i due grafi di prova, scritti apposta.
$PY "$QUI/fai-i-grafi.py"

# Il foglio dei simboli nuovi, accanto ai plenum di zona che non cambiano: le forme da
# giudicare (A-1, A-2), tutte le taglie.
mkdir -p "$LAVORO/simboli"
for S in fan-coil-ducted-air ducted-indoor-unit supply-plenum-{2,3,4,5,6} zoning-plenum-{2,3,4,5,6}; do
    cp "assets/symbols/$S.json" "assets/symbols/$S.svg" "$LAVORO/simboli/"
done
PYTHONPATH=src $PY -m disegnatore_mep symbols-sheet --symbols "$LAVORO/simboli" "$QUI/simboli-nuovi.svg" > /dev/null
$MEP anteprima "$QUI/simboli-nuovi.svg" --out "$QUI/simboli-nuovi.png" --dpi 200 > /dev/null

# Il vaso sanitario (A-5) sul T1 di REL-023, che e' esecutivo: il comando scrive taglia e
# precarica sul vaso e la taratura accanto al gruppo di sicurezza, e la tavola le porta.
T1=docs/collaudi/REL-023/T1
rm -rf "$QUI/vaso-sanitario" && mkdir -p "$QUI/vaso-sanitario"
$MEP vaso "$T1/grafo-completo.json" --sanitario --tmax 60 --rete 3 --taratura 6 \
    --out "$QUI/vaso-sanitario/grafo-completo.json" | tee "$QUI/vaso-sanitario/vaso.txt"
$MEP disegna "$QUI/vaso-sanitario/grafo-completo.json" --piano "$T1/piano-idraulica.json" \
    --out "$QUI/vaso-sanitario/tavola" > "$QUI/vaso-sanitario/disegna.txt" || true
grep -E "^Formato" "$QUI/vaso-sanitario/disegna.txt" || tail -3 "$QUI/vaso-sanitario/disegna.txt"
for PDF in "$QUI"/vaso-sanitario/tavola/*.pdf; do
    $MEP anteprima "$PDF" --out "${PDF%.pdf}.png" --dpi 110 > /dev/null
done

for CASO in plenum-di-mandata plenum-motorizzato; do
    echo "== $CASO"
    $MEP valida "$QUI/grafo-$CASO.json" | sed -n 1p
    $MEP completa "$QUI/grafo-$CASO.json" --out "$LAVORO/grafo-completo-$CASO.json" > "$LAVORO/completa.txt"
    sed -n 1p "$LAVORO/completa.txt"
    rm -rf "${QUI:?}/$CASO"
    mkdir -p "$QUI/$CASO"
    cp "$LAVORO/grafo-completo-$CASO.json" "$QUI/$CASO/grafo-completo.json"
    # Eseguire: il piano scritto a mano (materiale di collaudo, D-155). Esce 2 se il
    # preflight ha qualcosa da dire: la tavola c'e' lo stesso, e i rilievi sono nel file.
    for PIANO in "$QUI"/piano-"$CASO".json "$QUI"/piano-"$CASO"-elettrico.json; do
        [ -f "$PIANO" ] || continue
        NOME=$(basename "$PIANO" .json)
        $MEP disegna "$QUI/$CASO/grafo-completo.json" --piano "$PIANO" --out "$QUI/$CASO/tavola" \
            > "$QUI/$CASO/disegna-$NOME.txt" || true
        grep -E "^Formato|^Il piano non" "$QUI/$CASO/disegna-$NOME.txt" || tail -3 "$QUI/$CASO/disegna-$NOME.txt"
    done
    for PDF in "$QUI/$CASO"/tavola/*.pdf; do
        $MEP anteprima "$PDF" --out "${PDF%.pdf}.png" --dpi 110 > /dev/null
    done
    # La distinta, a parte: le regole dal repository.
    $MEP distinta "$QUI/$CASO/grafo-completo.json" --out "$QUI/$CASO/distinta" --regole rules/distinta | sed -n 1p || true
done
