#!/usr/bin/env bash
# Le tavole dei cinque impianti di prova, in parallelo, con l'esito di ciascuno
# su una riga sola (D-146: il PO le vuole vedere, e vuole sapere chi non esce).
#
# Differenza da `tavole-di-verifica.sh`: quello fa un impianto per volta e si
# ferma a guardare gli artefatti di ciascuno; questo serve al giro di lavoro —
# cinque processi insieme, e in fondo una tabella che dice chi esce, su che
# formato e con quante tratte cedute.
#
# Uso: scripts/tavole-dei-cinque.sh [cartella-di-uscita]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/outputs/cinque}"
PY="$ROOT/.venv/bin/python"

mkdir -p "$OUT"
: >"$OUT/esito.txt"

uno() {
  local progetto="$1"
  local nome
  nome="$(basename "$progetto" .json)"

  if ! "$PY" -m disegnatore_mep rules "$progetto" \
    --catalog "$ROOT/examples/layout/catalog" \
    --symbols "$ROOT/assets/symbols" \
    --rules "$ROOT/rules/hydronic" \
    --naming "$ROOT/naming" \
    --apply-all --out "$OUT/$nome-completo.json" >"$OUT/$nome-integrazioni.txt" 2>&1; then
    echo "$nome	REGOLE KO	$(tail -1 "$OUT/$nome-integrazioni.txt" | cut -c1-160)" >>"$OUT/esito.txt"
    return
  fi

  "$PY" -m disegnatore_mep draw "$OUT/$nome-completo.json" \
    --catalog "$ROOT/examples/layout/catalog" \
    --symbols "$ROOT/assets/symbols" \
    --naming "$ROOT/naming" \
    --verifica --geometry "$OUT/$nome-geometria.json" \
    --out "$OUT" >"$OUT/$nome-preflight.txt" 2>&1
  local esito=$?

  if [ ! -f "$OUT/$nome-geometria.json" ]; then
    echo "$nome	NON ESCE	$(tail -2 "$OUT/$nome-preflight.txt" | tr '\n' ' ' | cut -c1-200)" >>"$OUT/esito.txt"
    return
  fi

  # Il formato e il numero di tratte cedute si leggono dalla geometria, che e'
  # il documento agli atti: non dal messaggio, che e' prosa.
  local misura
  misura="$("$PY" - "$OUT/$nome-geometria.json" <<'PYEOF'
import json, sys
dati = json.load(open(sys.argv[1]))
tratte = [r for foglio in dati["sheets"] for r in foglio["routes"]]
cedute = [r for r in tratte if r.get("unresolved")]
print(f"{len(tratte)} tratte, {len(cedute)} cedute", end="")
if cedute:
    nomi = ", ".join(sorted({r["connection_ids"][0] for r in cedute if r["connection_ids"]}))
    print(f" ({nomi})", end="")
PYEOF
)"
  echo "$nome	ESCE (uscita $esito)	$misura" >>"$OUT/esito.txt"
}

for progetto in "$ROOT"/examples/prova/prova-*.json; do
  uno "$progetto" &
done
wait

echo
sort "$OUT/esito.txt" | column -t -s $'\t'
