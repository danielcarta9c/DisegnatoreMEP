#!/bin/bash
# Le uscite che la pulizia del solutore non deve cambiare, byte per byte (I-180).
#
#   docs/collaudi/REL-005/pulizia-del-solutore/uscite.sh <cartella>
#
# Scrive nella cartella: le sette tavole di prova approvate (tavole_di_prova.py), i
# cinque impianti di prova per la via del piano (PROVA-PIANO) e per la via senza piano
# (`draw`), e la tavola D della prova del PO dalla skill costruita. Si lancia prima e
# dopo, e le due cartelle si confrontano con `confronta.sh <prima> <dopo>`.
O=$1; rm -rf "$O"; mkdir -p "$O/tp" "$O/cinque" "$O/D"
R=$(cd "$(dirname "$0")/../../../.." && pwd); cd "$R" || exit 1
python3 docs/collaudi/REL-005/prova-po-1/tavole_di_prova.py "$O/tp" >/dev/null 2>&1 || echo "tavole di prova: errore"
for n in 1 2 3 4 5; do
  g=$(ls examples/prova/prova-$n-*.json); nome=$(basename "$g" .json)
  python3 -m disegnatore_mep rules "$g" --catalog examples/layout/catalog --symbols assets/symbols \
    --rules rules/hydronic --naming naming --apply-all --out "$O/cinque/$nome-completo.json" >/dev/null 2>&1 \
    || echo "$nome rules: $?"
  mkdir -p "$O/cinque/piano-$n" "$O/cinque/draw-$n"
  python3 -m disegnatore_mep piano "$O/cinque/$nome-completo.json" --piano "docs/collaudi/PROVA-PIANO/impianto-$n.json" \
    --catalog examples/layout/catalog --symbols assets/symbols --naming naming \
    --geometry "$O/cinque/piano-$n/geom.json" --dxf --out "$O/cinque/piano-$n" >"$O/cinque/piano-$n/esito.txt" 2>&1
  echo "piano $n -> $?"
  python3 -m disegnatore_mep draw "$g" --catalog examples/layout/catalog --symbols assets/symbols --naming naming \
    --geometry "$O/cinque/draw-$n/geom.json" --dxf --out "$O/cinque/draw-$n" >"$O/cinque/draw-$n/esito.txt" 2>&1
  echo "draw $n -> $?"
done
D=$R/docs/collaudi/REL-005/prova-po-1
python3 scripts/costruisci-skill.py >/dev/null 2>&1
cd "$R/outputs/skill/disegnatore-mep" || exit 1
python3 scripts/mep.py completa "$D/grafo-proposta-po.json" --out "$O/D/gc.json" >/dev/null 2>&1 \
  && python3 scripts/mep.py disegna "$O/D/gc.json" --piano "$D/piano-D-volano-coricato.json" --out "$O/D/t" >"$O/D/esito.txt" 2>&1
echo "D -> $?"
