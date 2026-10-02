#!/bin/bash
# confronta.sh <prima> <dopo>: hash di tutte le uscite, con il percorso della cartella tolto dai log
for d in "$1" "$2"; do
  (cd $d && find . -type f \( -name "*.svg" -o -name "*.dxf" -o -name "*.json" -o -name "esito.txt" -o -name "*.md" -o -name "*.pdf" \) | sort | while read f; do
     if [[ $f == *esito.txt ]]; then echo "$(sed "s|$d||g" $f | sha256sum | cut -c1-16)  $f"; else echo "$(sha256sum $f | cut -c1-16)  $f"; fi; done) > $d.hash
done
echo "file: $(wc -l < $1.hash) prima, $(wc -l < $2.hash) dopo"; diff $1.hash $2.hash && echo "IDENTICI"
