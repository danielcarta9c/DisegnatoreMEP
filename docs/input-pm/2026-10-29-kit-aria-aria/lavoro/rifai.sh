#!/bin/bash
# Ricostruisce tutto, dalla cartella "lavoro": skill estesa (da skill-orig, v1.4.1), numeri, grafo,
# completa, tavola M.02 (PDF/SVG/DXF + tabelle), tavola M.03, computo Excel.
set -e
cd "$(dirname "$0")"
L="$(pwd)"
rm -rf skill && cp -r skill-orig skill && python3 estendi.py
python3 dimensionamento.py > /dev/null
python3 grafo.py
cd skill
python3 scripts/mep.py valida "$L/grafo.json" | head -1
python3 scripts/mep.py completa "$L/grafo.json" --out "$L/grafo-completo.json" > /dev/null
rm -rf "$L/tavola"
python3 scripts/mep.py disegna "$L/grafo-completo.json" --piano "$L/piano.json" --out "$L/tavola" | tail -2
cd "$L"
python3 tabelle.py tavola
python3 pianta.py tavola
python3 excel.py
