#!/usr/bin/env bash
# Le tavole di un impianto di prova, da una sorgente scelta a una cartella
# scelta — **e in PDF**, che da D-146 e' il prodotto che il PO giudica.
#
# Discende da `docs/collaudi/DRAW-012/tavole.sh` e ne ripete la catena:
# completamento con le regole, disegno in modalita' verifica (D-110), misure
# con il metro di DRAW-002. In piu' fa l'ultimo passo che mancava: da ogni SVG
# escono il **PDF** a misura reale e il PNG per l'occhio terzo, cosi' che la
# consegna porti le tavole invece dei soli file intermedi.
#
# Non fa parte del nucleo deterministico: e' lo strumento di sessione con cui
# il DEV chiude il rapporto e il PM lo rilegge.
#
# Uso:
#   docs/collaudi/DRAW-013/tavole.sh SORGENTE USCITA nome-impianto [nome-impianto...]
#
# SORGENTE e' la radice di un albero del repository (questo, o un worktree sul
# ramo di partenza); USCITA e' dove finiscono i file. L'interprete si passa in
# PY, e per difetto e' il `.venv` della SORGENTE.
set -euo pipefail

SRC="${1:?uso: tavole.sh SORGENTE USCITA nome-impianto...}"
OUT="${2:?uso: tavole.sh SORGENTE USCITA nome-impianto...}"
shift 2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PY="${PY:-$SRC/.venv/bin/python}"

# Il codice e' quello della SORGENTE, non quello installato: e' l'unico modo
# perche' la colonna «prima» sia davvero prima.
export PYTHONPATH="$SRC/src"
mkdir -p "$OUT"

for name in "$@"; do
  echo "== $name"
  "$PY" -m disegnatore_mep rules "$SRC/examples/prova/$name.json" \
    --catalog "$SRC/examples/layout/catalog" --symbols "$SRC/assets/symbols" \
    --rules "$SRC/rules/hydronic" --naming "$SRC/naming" \
    --apply-all --out "$OUT/$name-completo.json" >"$OUT/$name-integrazioni.txt"

  "$PY" -m disegnatore_mep draw "$OUT/$name-completo.json" \
    --catalog "$SRC/examples/layout/catalog" --symbols "$SRC/assets/symbols" \
    --naming "$SRC/naming" --verifica --geometry "$OUT/$name-geometria.json" \
    --out "$OUT" >"$OUT/$name-preflight.txt" 2>&1 || {
      echo "   la tavola NON esce: $(tail -1 "$OUT/$name-preflight.txt")"
      continue
    }

  "$PY" "$SRC/docs/collaudi/DRAW-002/metriche.py" \
    "$OUT/$name-completo.json" "$OUT/$name-geometria.json" >"$OUT/$name-metriche.json"

  # **Le tavole, per prime** (D-146): il PDF e' il prodotto, il PNG e' per
  # l'occhio. Senza questo passo la consegna lascia al PO dei file intermedi.
  for svg in "$OUT/$name"-t*.svg; do
    [ -e "$svg" ] || continue
    sheet="$(basename "$svg" .svg)"
    "$ROOT/scripts/to-pdf.sh" "$svg" "$OUT/$sheet.pdf" >/dev/null
    "$ROOT/scripts/rasterize.sh" "$svg" "$OUT/$sheet.png" >/dev/null
    echo "   tavola: $OUT/$sheet.pdf"
  done
done

echo
echo "Tavole in $OUT"
