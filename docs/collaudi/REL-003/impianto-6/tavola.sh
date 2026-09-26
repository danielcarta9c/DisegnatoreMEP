#!/usr/bin/env bash
# Rifà la tavola dell'impianto 6 da grafo e piano, col cartiglio compilato.
#
# I dati del cartiglio sono quelli di prova di REL-002 (docs/collaudi/REL-002/dati-di-prova.json:
# inventati, il repository è pubblico), più il numero T6; si aggiungono ai metadati del grafo solo
# per compilare il cartiglio, e il disegno non li legge.
#
# Uso, dalla radice del repository:
#   bash docs/collaudi/REL-003/impianto-6/tavola.sh a <cartella-di-lavoro>   # la tavola
#   bash docs/collaudi/REL-003/impianto-6/tavola.sh b <cartella-di-lavoro>   # la seconda composizione
set -euo pipefail

QUALE="${1:?uso: tavola.sh a|b cartella-di-lavoro}"
LAVORO="${2:?uso: tavola.sh a|b cartella-di-lavoro}"
QUI="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$QUI/../../../.." && pwd)"
PYTHON="${PYTHON:-$REPO/.venv/bin/python}"

mkdir -p "$LAVORO"
"$PYTHON" - "$QUI/grafo-completo-6.json" "$LAVORO/grafo-con-i-dati.json" "$REPO" <<'PY'
import json, sys
from pathlib import Path
dati = json.loads(Path(sys.argv[3], "docs/collaudi/REL-002/dati-di-prova.json").read_text("utf-8"))
grafo = json.loads(Path(sys.argv[1]).read_text("utf-8"))
grafo["metadata"].update({**dati["tutti"], "sheet_number": "T6"})
Path(sys.argv[2]).write_text(json.dumps(grafo, ensure_ascii=False, indent=2), "utf-8")
PY
cd "$REPO"
rm -rf "$LAVORO/svg"
"$PYTHON" -m disegnatore_mep piano "$LAVORO/grafo-con-i-dati.json" --piano "$QUI/piano-6-$QUALE.json" \
  --catalog examples/layout/catalog --symbols assets/symbols --naming naming \
  --cartiglio assets/cartigli/Cartiglio_NoveC_A3.json --out "$LAVORO/svg"
bash scripts/to-pdf.sh "$LAVORO"/svg/*-t1.svg "$LAVORO/tavola-impianto-6-$QUALE.pdf"
