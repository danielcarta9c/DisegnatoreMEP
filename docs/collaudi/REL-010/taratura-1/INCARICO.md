Sei il revisore di una tavola di schema funzionale idronico (centrale termica). Non l'hai composta tu, e non sai niente dell'impianto oltre a quello che la tavola mostra.

Lavori **solo** con i file della cartella `{CARTELLA}`. Non aprire, non cercare e non elencare altri file del computer: tutto quello che ti serve è lì.

1. Leggi per intero `{CARTELLA}/rivedere.md`: sono le tue istruzioni, e bastano da sole. Il piano e le tavole di riferimento che nomina al §2 non li ricevi.
2. La tavola è `{CARTELLA}/tavola.png` (il foglio intero) e `{CARTELLA}/tavola.pdf`. Guardala. Per ingrandire una zona usa
   `pdftoppm -png -r 300 -x X -y Y -W L -H A -singlefile {CARTELLA}/tavola.pdf {CARTELLA}/zoom-N`
   dove X, Y, L, A sono in pixel a 300 dpi (1 mm = 11,81 px; il foglio parte in alto a sinistra), e poi guarda `zoom-N.png`. Scegli tu le zone.
3. I rilievi già misurati sono in `{CARTELLA}/rilievi.md`: sono dati, non il tuo lavoro.
4. `{CARTELLA}/regole-del-piano.md` si apre quando un rilievo o un tuo vincolo cita una regola.

Restituisci il rapporto nella forma di `rivedere.md` §6, in italiano. In fondo aggiungi una riga sola, che comincia con «VERDETTO:», con una di queste due frasi: «la tavola si può consegnare così» oppure «la tavola va ricomposta prima di consegnarla», e il perché in una frase.
