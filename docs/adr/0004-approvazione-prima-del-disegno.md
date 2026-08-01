# ADR 0004 - Approvazione tecnica prima del disegno

**Stato:** accettato - agosto 2026

## Contesto

La skill deve completare accessori e dettagli grafici senza sostituire le scelte progettuali dell'ingegnere. Fermarsi su ogni dubbio renderebbe però il flusso lento.

## Decisione

La skill legge la conversazione, propone l'interpretazione più probabile e presenta un unico dossier con impianto interpretato, integrazioni, assunzioni, domande e suddivisione in tavole. Il rendering inizia soltanto dopo approvazione esplicita.

## Motivazione

L'ingegnere può approvare rapidamente l'intero insieme o correggere soltanto le eccezioni. Nessuna modifica tecnica viene introdotta silenziosamente.

## Conseguenze

La skill deve tracciare stato e provenienza di fatti, ipotesi e integrazioni. Le correzioni puramente grafiche possono essere automatiche; quelle tecniche richiedono consenso.

## Quando rivedere

Se l'uso reale dimostrerà che servono più livelli di approvazione o workflow multiutente.
