#!/usr/bin/env bash
# Prepara una «camera pulita» per un agente pianificatore: la cartella in cui
# lavora e da cui non esce. E' il protocollo delle prove del 21, 22 e 23
# settembre 2026 (docs/collaudi/DRAW-016/), scritto una volta sola.
#
# Uso: prepara-camera.sh <grafo-completo.json> <cartella-camera> <cartella-motore>
#
#   <grafo-completo.json>  il grafo come `disegnatore-mep rules --apply-all --out` lo scrive
#   <cartella-camera>      la cartella dell'agente (viene creata)
#   <cartella-motore>      una copia del repository FERMA a un commit — di solito
#                          `git worktree add --detach <cartella> HEAD` — da cui la camera
#                          esegue il motore. Serve perche' l'agente non veda le modifiche
#                          che la sessione fa mentre lui lavora.
#
# La camera riceve: ISTRUZIONI.md e CONSEGNA.md della skill, il grafo, i manifesti dei
# simboli, il catalogo e il naming (servono al comando), e tre strumenti: piano.sh esegue
# un piano e scrive la tavola, rasterize.sh e to-pdf.sh la trasformano per guardarla.
# Il mandato da dare all'agente sta in docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-23/mandato.md.
set -euo pipefail

GRAFO="${1:?uso: prepara-camera.sh grafo.json cartella-camera cartella-motore}"
CAMERA="${2:?uso: prepara-camera.sh grafo.json cartella-camera cartella-motore}"
MOTORE="$(cd "${3:?uso: prepara-camera.sh grafo.json cartella-camera cartella-motore}" && pwd)"
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"

mkdir -p "$CAMERA/strumenti" "$CAMERA/lavoro"
cp "$REPO/skill/comporre/ISTRUZIONI.md" "$REPO/skill/comporre/CONSEGNA.md" "$CAMERA/"
cp "$GRAFO" "$CAMERA/grafo.json"
rm -rf "$CAMERA/simboli" "$CAMERA/catalogo" "$CAMERA/naming"
cp -r "$MOTORE/assets/symbols" "$CAMERA/simboli"
cp -r "$MOTORE/examples/layout/catalog" "$CAMERA/catalogo"
cp -r "$MOTORE/naming" "$CAMERA/naming"
cp "$REPO/scripts/rasterize.sh" "$REPO/scripts/to-pdf.sh" "$CAMERA/strumenti/"

cat > "$CAMERA/strumenti/piano.sh" <<PIANO
#!/usr/bin/env bash
# Esegue il piano e disegna la tavola in tavola/. Uso: bash strumenti/piano.sh [piano.json]
set -uo pipefail
cd "\$(dirname "\$0")/.."
PIANO="\${1:-piano.json}"
rm -rf tavola && mkdir -p tavola
PYTHONPATH=$MOTORE/src python3 -m disegnatore_mep piano grafo.json --piano "\$PIANO" \\
  --catalog catalogo --symbols simboli --naming naming \\
  --geometry tavola/geometria.json --out tavola
PIANO
chmod +x "$CAMERA/strumenti/"*.sh
echo "camera pronta: $CAMERA (motore: $MOTORE)"
