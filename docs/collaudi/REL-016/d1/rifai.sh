#!/bin/bash
# Rifa' le due tavole della villetta del collaudo della 1.7.0 (REL-016, D1), per la strada
# di un agente: la skill costruita da scripts/costruisci-skill.py, poi
#   grafo -> completa -> pezzi -> disegna (piano aggrovigliato e piano buono) -> anteprima.
# La tavola aggrovigliata esce coi suoi bloccanti (RUN_CROSSES_ITSELF,
# INLINE_ORGAN_BREAKS_THE_RUN) e il comando la ferma; quella buona si consegna.
# Uso, dalla radice del repository:
#   bash docs/collaudi/REL-016/d1/rifai.sh
# Scrive in docs/collaudi/REL-016/d1/: le anteprime PNG, i rilievi e l'ordine dei pezzi.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
QUI=docs/collaudi/REL-016/d1
CASI=docs/collaudi/REL-016/casi-del-collaudo
LAVORO=$(mktemp -d)
trap 'rm -rf "$LAVORO"' EXIT

python3 scripts/costruisci-skill.py --out "$LAVORO/skill" > /dev/null
MEP="python3 $LAVORO/skill/disegnatore-mep/scripts/mep.py"

$MEP completa "$CASI/villetta-grafo.json" --out "$LAVORO/grafo-completo.json" | sed -n 1p
# L'ordine dei pezzi lungo le tratte, quello che chi compone deve seguire.
$MEP pezzi "$LAVORO/grafo-completo.json" --vista idraulica | sed -n '/^In che ordine/,$p' > "$QUI/ordine-dei-pezzi.txt"

rm -f "$QUI"/*.png "$QUI"/*-rilievi.md
for piano in groviglio buono; do
    # La tavola aggrovigliata non si consegna: il comando esce con 2, e qui si va avanti.
    $MEP disegna "$LAVORO/grafo-completo.json" --piano "$CASI/villetta-piano-$piano.json" \
        --out "$LAVORO/$piano" --senza-dxf | grep -E '^(Formato|La tavola)' || true
    for pdf in "$LAVORO/$piano"/*.pdf; do
        nome=$(basename "${pdf%.pdf}")
        $MEP anteprima "$pdf" --out "$QUI/$piano-$nome.png" --dpi 110 > /dev/null
        cp "$LAVORO/$piano/$nome-rilievi.md" "$QUI/$piano-$nome-rilievi.md"
    done
done
