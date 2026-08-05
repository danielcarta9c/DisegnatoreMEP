#!/usr/bin/env bash
# Rasterizza una tavola SVG in PNG a misura di stampa, per l'occhio terzo
# (D-077, D-086) e per il controllo visivo di release (§12.7).
#
# Non fa parte del nucleo deterministico: e' uno strumento di sessione, usa il
# browser preinstallato nell'ambiente. Il prodotto resta SVG/PDF.
#
# Uso: scripts/rasterize.sh tavola.svg tavola.png
set -euo pipefail

SVG="${1:?uso: rasterize.sh input.svg output.png}"
PNG="${2:?uso: rasterize.sh input.svg output.png}"
CHROME="${CHROME:-/opt/pw-browsers/chromium}"

# Dimensioni CSS in px a 96 dpi dalle dimensioni in mm dichiarate dall'SVG.
read -r W_MM H_MM < <(python3 - "$SVG" <<'PY'
import re, sys
head = open(sys.argv[1], encoding="utf-8").read(2000)
w = re.search(r'width="([0-9.]+)mm"', head)
h = re.search(r'height="([0-9.]+)mm"', head)
if not (w and h):
    sys.exit("the SVG does not declare width/height in mm")
print(w.group(1), h.group(1))
PY
)
W_PX=$(python3 -c "print(round(float('$W_MM') / 25.4 * 96) + 1)")
H_PX=$(python3 -c "print(round(float('$H_MM') / 25.4 * 96) + 1)")

"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=2 \
  --window-size="${W_PX},${H_PX}" \
  --screenshot="$PNG" \
  "file://$(realpath "$SVG")" 2>/dev/null
echo "$PNG ($((W_PX * 2))x$((H_PX * 2)) px, ${W_MM}x${H_MM} mm)"
