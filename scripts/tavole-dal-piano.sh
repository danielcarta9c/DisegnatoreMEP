#!/usr/bin/env bash
# Le tavole dei cinque impianti **dal piano di composizione** (D-151), in
# parallelo, con l'esito di ciascuno su una riga sola (D-146: il PO le vuole
# vedere, e vuole sapere chi non esce).
#
# Differenza da `tavole-dei-cinque.sh`: quello passa dal comando `draw`, cioe'
# dalla posa deterministica **senza un piano**; questo passa dal comando
# `piano`, che esegue il piano che un agente ha composto. Dal 20 settembre 2026
# la via del piano e' quella vigente, e le due si confrontano riga per riga.
#
# I piani stanno in `docs/collaudi/PROVA-PIANO/impianto-N.json`, uno per
# impianto, e sono documenti agli atti: chi li cambia cambia una tavola.
#
# Uso: scripts/tavole-dal-piano.sh [cartella-di-uscita]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/outputs/dal-piano}"
PY="$ROOT/.venv/bin/python"
PIANI="$ROOT/docs/collaudi/PROVA-PIANO"

mkdir -p "$OUT"
: >"$OUT/esito.txt"

uno() {
  local numero="$1"
  local progetto
  progetto="$(ls "$ROOT"/examples/prova/prova-"$numero"-*.json)"
  local nome
  nome="$(basename "$progetto" .json)"
  local piano="$PIANI/impianto-$numero.json"

  if [ ! -f "$piano" ]; then
    echo "$nome	NESSUN PIANO	$piano non esiste" >>"$OUT/esito.txt"
    return
  fi

  # Il progetto completo si ricava sempre dalla stessa catena: le integrazioni
  # del motore delle regole, scritte in forma canonica. **Il piano si esegue su
  # quella forma**, non su un modello costruito in memoria: la posa di partenza
  # legge l'ordine del file, e un ordine diverso da' un'altra tavola.
  if ! "$PY" -m disegnatore_mep rules "$progetto" \
    --catalog "$ROOT/examples/layout/catalog" \
    --symbols "$ROOT/assets/symbols" \
    --rules "$ROOT/rules/hydronic" \
    --naming "$ROOT/naming" \
    --apply-all --out "$OUT/$nome-completo.json" >"$OUT/$nome-integrazioni.txt" 2>&1; then
    echo "$nome	REGOLE KO	$(tail -1 "$OUT/$nome-integrazioni.txt" | cut -c1-160)" >>"$OUT/esito.txt"
    return
  fi

  "$PY" -m disegnatore_mep piano "$OUT/$nome-completo.json" \
    --piano "$piano" \
    --catalog "$ROOT/examples/layout/catalog" \
    --symbols "$ROOT/assets/symbols" \
    --naming "$ROOT/naming" \
    --geometry "$OUT/$nome-geometria.json" \
    --out "$OUT" >"$OUT/$nome-preflight.txt" 2>&1
  local esito=$?

  if [ ! -f "$OUT/$nome-geometria.json" ]; then
    echo "$nome	NON ESCE	$(tail -3 "$OUT/$nome-preflight.txt" | tr '\n' ' ' | cut -c1-200)" >>"$OUT/esito.txt"
    return
  fi

  local misura
  misura="$("$PY" - "$OUT/$nome-geometria.json" "$OUT/$nome-preflight.txt" <<'PYEOF'
import json, sys
dati = json.load(open(sys.argv[1]))
testo = open(sys.argv[2], encoding="utf-8").read()
tratte = [r for foglio in dati["sheets"] for r in foglio["routes"]]
cedute = [r for r in tratte if r.get("unresolved")]
bloccanti = testo.count("\n  - ") and sum(
    1 for riga in testo.splitlines() if riga.startswith("    codice: ")
)
print(f"{len(tratte)} tratte, {len(cedute)} cedute", end="")
if cedute:
    nomi = ", ".join(sorted({r["connection_ids"][0] for r in cedute if r["connection_ids"]}))
    print(f" ({nomi})", end="")
PYEOF
)"
  local righe
  righe="$(grep -c 'codice:' "$OUT/$nome-preflight.txt" 2>/dev/null || echo 0)"
  local blocca
  blocca="$(sed -n 's/^Tratte cedute: .*rilievi bloccanti: \(.*\)$/\1/p' "$OUT/$nome-preflight.txt" | tail -1)"
  echo "$nome	ESCE (uscita $esito)	$misura	bloccanti ${blocca:-?}	rilievi $righe" >>"$OUT/esito.txt"
}

for numero in 1 2 3 4 5; do
  uno "$numero" &
done
wait

echo
sort "$OUT/esito.txt"
