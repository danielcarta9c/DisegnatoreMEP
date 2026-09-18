#!/usr/bin/env bash
# Le tavole di un impianto di prova, da una sorgente scelta a una cartella
# scelta: e' cosi' che si producono le due colonne di un confronto prima/dopo
# **con lo stesso comando**, una volta puntandolo a un worktree su `main` e una
# volta al ramo di lavoro.
#
# Non fa parte del nucleo deterministico: e' lo strumento di sessione con cui il
# DEV chiude il rapporto e il PM lo rilegge, come `scripts/tavole-di-verifica.sh`
# — da cui discende, e di cui ripete la catena: completamento con le regole,
# disegno in modalita' verifica (D-110), misure con il metro di DRAW-002.
#
# Uso:
#   docs/collaudi/DRAW-012/tavole.sh SORGENTE USCITA nome-impianto [nome-impianto...]
#
# SORGENTE e' la radice di un albero del repository (questo, o un worktree su
# `main`); USCITA e' dove finiscono i file. Il modello di partenza si legge da
# SORGENTE/examples/prova/<nome-impianto>.json.
#
# L'interprete e' quello del proprio ambiente: si passa in PY, e per difetto e'
# il `.venv` accanto a questo file.
set -euo pipefail

SRC="${1:?uso: tavole.sh SORGENTE USCITA nome-impianto...}"
OUT="${2:?uso: tavole.sh SORGENTE USCITA nome-impianto...}"
shift 2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PY="${PY:-$ROOT/.venv/bin/python}"

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
      echo "   la tavola non esce: $(tail -1 "$OUT/$name-preflight.txt")"
      continue
    }

  "$PY" "$SRC/docs/collaudi/DRAW-002/metriche.py" \
    "$OUT/$name-completo.json" "$OUT/$name-geometria.json" >"$OUT/$name-metriche.json"
done

echo
echo "Tavole in $OUT"
