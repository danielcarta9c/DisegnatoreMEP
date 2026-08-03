#!/usr/bin/env bash
# Ricostruisce l'ambiente di sviluppo da zero.
#
# Serve alle sessioni cloud, che ripartono da un clone pulito e non
# conservano nulla di quanto installato in precedenza. Funziona anche in
# locale su Linux, macOS e Git Bash su Windows.
#
#   bash scripts/setup-env.sh
#
# Le versioni delle dipendenze sono pinnate in pyproject.toml: questo script
# non le duplica, cosi' non possono divergere.

set -euo pipefail

cd "$(dirname "$0")/.."

# Python 3.11 e' il minimo dichiarato in pyproject.toml; 3.12 e' il riferimento
# con cui il progetto e' stato sviluppato e verificato.
# Il candidato deve anche ESEGUIRE: su Windows `python3` risolve allo stub del
# Microsoft Store, che sta nel PATH ma non e' un interprete.
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  for candidate in python3.12 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
       "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "Nessun interprete Python 3.11+ utilizzabile trovato." >&2
  echo "Imposta PYTHON_BIN sul percorso dell'interprete e riprova." >&2
  exit 1
fi

echo "Interprete: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

if [ ! -d .venv ]; then
  echo "Creo .venv..."
  "$PYTHON_BIN" -m venv .venv
fi

# Windows usa Scripts/, tutto il resto bin/.
if [ -x .venv/bin/python ]; then
  VENV_PY=.venv/bin/python
else
  VENV_PY=.venv/Scripts/python.exe
fi

"$VENV_PY" -m pip install --upgrade pip --quiet
"$VENV_PY" -m pip install -e '.[dev]' --quiet

echo
echo "Verifica dell'ambiente:"
"$VENV_PY" --version
"$VENV_PY" -m pytest -q
"$VENV_PY" -m ruff check src tests
"$VENV_PY" -m mypy src tests

echo
echo "Ambiente pronto. Interprete: $VENV_PY"
