# ADR 0003 - Scala fisica invariabile e impaginazione semantica

**Stato:** accettato - agosto 2026

## Contesto

Rimpicciolire automaticamente un impianto complesso rende simboli e testi illeggibili. Tagliare geometricamente un disegno già composto spezza circuiti e associazioni funzionali.

## Decisione

Definire simboli, testi, spessori e distanze in millimetri di carta invarianti. Usare A3 orizzontale come formato ordinario e suddividere, soltanto quando necessario, il modello per sottosistemi prima del layout. A1/A0 restano alternative secondarie.

## Motivazione

La scelta garantisce leggibilità di stampa e coerenza grafica. La partizione semantica mantiene la continuità dell'impianto mediante rimandi controllabili.

## Conseguenze

Il motore deve gestire connettori fra tavole e non può risolvere la complessità riducendo la scala. Le prove di stampa diventano parte del collaudo.

## Quando rivedere

Se cambierà il formato ordinario di stampa o se nascerà un requisito prioritario di consultazione esclusivamente digitale.
