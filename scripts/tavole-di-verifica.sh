#!/usr/bin/env bash
# Le tavole dei cinque impianti di prova, in modalita' verifica (D-110), da SVG
# a PDF (D-016: il PDF e' l'elaborato, l'SVG e' il passaggio vettoriale).
#
# Non fa parte del nucleo deterministico: e' lo strumento con cui si guarda il
# lavoro durante la sessione, come `rasterize.sh`. La conversione in PDF usa il
# browser preinstallato nell'ambiente, a misura reale — il foglio dichiara i
# propri millimetri e la pagina li rispetta, quindi un simbolo stampato misura
# quello che il modello dice.
#
# Da DRAW-002 scrive anche la geometria, il PNG e le misure di ogni tavola:
# sono gli artefatti con cui il PM confronta prima e dopo, e devono uscire
# dallo stesso comando che produce la tavola.
#
# Uso: scripts/tavole-di-verifica.sh [cartella-di-uscita]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/outputs/verifica}"
CHROME="${CHROME:-/opt/pw-browsers/chromium}"
PY="$ROOT/.venv/bin/python"

mkdir -p "$OUT"

for project in "$ROOT"/examples/prova/prova-*.json; do
  name="$(basename "$project" .json)"
  echo "== $name"
  "$PY" -m disegnatore_mep rules "$project" \
    --catalog "$ROOT/examples/layout/catalog" \
    --symbols "$ROOT/assets/symbols" \
    --rules "$ROOT/rules/hydronic" \
    --naming "$ROOT/naming" \
    --apply-all --out "$OUT/$name-completo.json" >"$OUT/$name-integrazioni.txt"

  "$PY" -m disegnatore_mep draw "$OUT/$name-completo.json" \
    --catalog "$ROOT/examples/layout/catalog" \
    --symbols "$ROOT/assets/symbols" \
    --naming "$ROOT/naming" \
    --verifica --geometry "$OUT/$name-geometria.json" \
    --out "$OUT" >"$OUT/$name-preflight.txt" 2>&1 || {
      echo "   la tavola non esce: $(tail -1 "$OUT/$name-preflight.txt")"
      continue
    }

  for svg in "$OUT/$name"-*.svg; do
    [ -e "$svg" ] || continue
    "$ROOT/scripts/to-pdf.sh" "$svg" "${svg%.svg}.pdf"
    "$ROOT/scripts/rasterize.sh" "$svg" "${svg%.svg}.png"
  done

  # Le misure della tavola, con lo stesso strumento del collaudo DRAW-002:
  # geometria letta dal file appena scritto, cosi' che i numeri descrivano
  # esattamente la tavola consegnata e non una ricomposizione.
  "$PY" "$ROOT/docs/collaudi/DRAW-002/metriche.py" \
    "$OUT/$name-completo.json" "$OUT/$name-geometria.json" >"$OUT/$name-metriche.json"
done

echo
echo "Tavole in $OUT"
