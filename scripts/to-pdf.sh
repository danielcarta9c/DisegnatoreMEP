#!/usr/bin/env bash
# Converte una tavola SVG in PDF a misura reale.
#
# Non fa parte del nucleo deterministico: e' uno strumento di sessione, come
# `rasterize.sh`, e usa il browser preinstallato nell'ambiente.
#
# La misura e' il punto: l'SVG dichiara larghezza e altezza in millimetri, e la
# pagina PDF viene dichiarata **della stessa misura**, senza margini. Cosi' un
# simbolo stampato misura quello che il modello dice, e la scala di stampa resta
# invariante come ADR 0003 pretende.
#
# Uso: scripts/to-pdf.sh tavola.svg tavola.pdf
set -euo pipefail

SVG="${1:?uso: to-pdf.sh input.svg output.pdf}"
PDF="${2:?uso: to-pdf.sh input.svg output.pdf}"
CHROME="${CHROME:-/opt/pw-browsers/chromium}"

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

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cat >"$WORK/page.html" <<HTML
<!doctype html><meta charset="utf-8">
<style>
  @page { size: ${W_MM}mm ${H_MM}mm; margin: 0 }
  html, body { margin: 0; padding: 0 }
  img { display: block; width: ${W_MM}mm; height: ${H_MM}mm }
</style>
<img src="tavola.svg">
HTML
cp "$SVG" "$WORK/tavola.svg"

"$CHROME" --headless --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf="$PDF" \
  "file://$WORK/page.html" 2>/dev/null

echo "$PDF (${W_MM}x${H_MM} mm)"
