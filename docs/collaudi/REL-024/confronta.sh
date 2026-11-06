#!/bin/bash
# Le stesse uscite da due skill costruite: main e il ramo. Uso: confronta.sh <radice-repo> <uscita>
set -uo pipefail
R=$1; OUT=$2; rm -rf $OUT; mkdir -p $OUT
python3 $R/scripts/costruisci-skill.py --out $OUT/skill > /dev/null
MEP="python3 $OUT/skill/disegnatore-mep/scripts/mep.py"
D="$(cd "$(dirname "$0")/.." && pwd)"
$MEP disegna $D/REL-023/T1/grafo-completo.json --piano $D/REL-023/T1/piano-idraulica.json --out $OUT/t1 > $OUT/t1.log 2>&1
for v in idraulica elettrico; do
  $MEP disegna $D/REL-015/pdc-regola/grafo-completo.json --piano $D/REL-015/pdc-regola/piano-$v.json --out $OUT/villetta > $OUT/villetta-$v.log 2>&1
done
$MEP completa $D/REL-015/pdc-regola/grafo.json --out $OUT/completa-villetta.json > /dev/null 2>&1
$MEP distinta $D/REL-023/T1/grafo-completo.json --out $OUT/distinta-t1 > $OUT/distinta.log 2>&1
$MEP pianta $D/REL-012/collaudo-t3/pianta.json --out $OUT/pianta > $OUT/pianta.log 2>&1
for f in $D/REL-012/fase-2/grafo.json; do $MEP completa $f --out $OUT/completa-aria.json > /dev/null 2>&1; $MEP disegna $OUT/completa-aria.json --piano $D/REL-012/fase-2/piano.json --out $OUT/aria > $OUT/aria.log 2>&1; done
