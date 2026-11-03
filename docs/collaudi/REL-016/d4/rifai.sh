#!/usr/bin/env bash
# REL-016, D4 — le domande della distinta prima del primo lancio, sul trilocale del collaudo.
#
# Rifà i file di questa cartella dalla skill costruita (`scripts/costruisci-skill.py`), come
# la usa un agente su claude.ai:
#   1. `trilocale-al-passo-2.json`: il trilocale del collaudo come lo scrive il passo 2 senza
#      le domande della distinta (lunghezze e sezioni sì; refrigerante, precarica, bocchette,
#      attacco della condensa, protezioni e portate no). `completa`, poi
#      `distinta --domande` → `domande-prima.txt`; `distinta` → `distinta-prima.md`.
#   2. Le risposte di `risposte.json`, nei campi che le domande dicono; `completa`, poi
#      `distinta --domande` → `domande-dopo.txt`; `distinta` → `distinta-dopo.md`.
# Le uscite del comando `distinta` sono in `uscita-distinta-prima.txt` e `uscita-distinta-dopo.txt`.
set -euo pipefail

QUI="$(cd "$(dirname "$0")" && pwd)"
RADICE="$(cd "$QUI/../../../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 "$RADICE/scripts/costruisci-skill.py" --out "$TMP/skill" > /dev/null
MEP="$TMP/skill/disegnatore-mep/scripts/mep.py"

# Esce con 2 quando ci sono domande o voci DA DEFINIRE: e' il caso che si misura.
due_va_bene() { "$@" || [ $? -eq 2 ]; }

# Le uscite si scrivono senza la cartella temporanea, perche' si possano confrontare.
senza_tmp() { sed "s|$TMP/||g"; }

python3 "$MEP" completa "$QUI/trilocale-al-passo-2.json" --out "$TMP/prima.json" > /dev/null
due_va_bene python3 "$MEP" distinta "$TMP/prima.json" --domande > "$QUI/domande-prima.txt"
due_va_bene python3 "$MEP" distinta "$TMP/prima.json" --out "$TMP/distinta-prima" > "$TMP/uscita.txt" 2>&1
senza_tmp < "$TMP/uscita.txt" > "$QUI/uscita-distinta-prima.txt"
cp "$TMP"/distinta-prima/*_Distinta_materiali_*.md "$QUI/distinta-prima.md"

python3 - "$QUI/trilocale-al-passo-2.json" "$QUI/risposte.json" "$TMP/con-le-risposte.json" <<'PY'
import json
import sys

grafo = json.load(open(sys.argv[1], encoding="utf-8"))
risposte = json.load(open(sys.argv[2], encoding="utf-8"))
for chiave in ("components", "connections"):
    for elemento in grafo[chiave]:
        elemento.setdefault("properties", {}).update(risposte[chiave].get(elemento["id"], {}))
json.dump(grafo, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
PY

python3 "$MEP" completa "$TMP/con-le-risposte.json" --out "$TMP/dopo.json" > /dev/null
due_va_bene python3 "$MEP" distinta "$TMP/dopo.json" --domande > "$QUI/domande-dopo.txt"
due_va_bene python3 "$MEP" distinta "$TMP/dopo.json" --out "$TMP/distinta-dopo" > "$TMP/uscita.txt" 2>&1
senza_tmp < "$TMP/uscita.txt" > "$QUI/uscita-distinta-dopo.txt"
cp "$TMP"/distinta-dopo/*_Distinta_materiali_*.md "$QUI/distinta-dopo.md"

echo "Prima: $(grep -m1 '^DA DEFINIRE' "$QUI/uscita-distinta-prima.txt")"
echo "Dopo:  $(grep -m1 '^DA DEFINIRE' "$QUI/uscita-distinta-dopo.txt")"
