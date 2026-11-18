# REL-028 — Il listino Tecnomat completo, e i punti aperti di REL-027

> **Scritto il 18 novembre 2026**, alla fusione di `REL-027` (la 2.1.1, PR #96). Il PO: «la lista mettila in main
> insieme alle "cose da fare prox sessione"» (I-312). Il pacchetto precedente è in `docs/plans/pacchetti/REL-027.md`,
> il suo rapporto in `docs/collaudi/REL-027/RAPPORTO.md`.

**Da svolgere:** l'agente unico (**D-147**), nella sessione.
**Stato:** **DA AVVIARE** — il primo punto lo ha indicato il PO (la lista Tecnomat); chi apre la sessione nuova
comincia da lì, e sui punti aperti chiede al PO.
**Base:** `main` con la 2.1.1 (PR #96).
**Approvazione della fusione:** del PO. Il pacchetto non tocca il disegno: il PO guarda il costo con «Dove comprare»
di PR.MI.059 rifatto col listino completo.

## Le cose da fare

1. **Completare il listino Tecnomat, coi prezzi Tecnomat Pro** (I-304, I-311, I-313). Il file per la sessione Chrome,
   con le istruzioni, è `docs/rilievi/tecnomat-pro-da-rilevare.md`: **parte A**, le 150 righe Tecnomat che abbiamo,
   da verificare col prezzo Pro (Nove C ha l'abbonamento); **parte B**, i **62 codici** della distinta senza un prezzo
   Tecnomat che rispetti la voce, **prima i 30 di PR.MI.059**. Il
   rilievo si fa **come il 2 novembre: il PO e Claude insieme, con Claude in Chrome nel browser del PO** — dalla
   sessione cloud tecnomat.it non si apre (protezione anti-robot), e non si aggira. Il PO riporta il file riempito; la
   sessione mette le righe nel listino (un capitolo col rilievo e la sua data, colonna Fornitore «Tecnomat»), con ⚠
   dove l'articolo non rispetta la voce, e rifà `docs/collaudi/REL-027/pr-mi-059/misura.py`.
2. **Le domande aperte di `REL-027`**, da fare al PO (rapporto, §7), una alla volta:
   - le **apparecchiature** (volano, circolatore, bollitore) nel consiglio d'acquisto: oggi fuori, la sezione A non
     si prezza (D-235); il PO le compra da Abbattista, e Idrosanitaria le ha meno care;
   - il **rame «CONDY»** di Idrosanitaria: è il rivestito? Se sì, le due righe prendono F01b e F03b;
   - il **pollice nei raccordi «all'attacco»** della distinta: senza, Idrosanitaria ha offerto manicotti;
   - l'**imbuto di scarico** della valvola di sicurezza «con scarico convogliato»: si conta?
   - gli **sconti di Abbattista** nel repository pubblico;
   - la **lista di PR.MI.059 fatta con una copia della skill che non è `main`** (quantità nette, testi diversi): le
     modifiche, se servono, si riportano nel repository (sono in parte `REL-025`).
3. **Le offerte nuove** dei fornitori, quando arrivano: un capitolo ciascuna nel listino, ogni riga col fornitore
   (I-304).

## Fuori

Il contenuto di `REL-025` (la 2.2) e le fasi aperte di `REL-024`: l'ordine lo dice il PO.

## Criteri di accettazione

Si scrivono quando il PO avvia il pacchetto, sul lavoro che sceglie; per il punto 1: le righe rilevate nel listino con
fornitore, negozio, codice e data, le prove del listino verdi, la misura su PR.MI.059 rifatta e mostrata al PO, la
suite, ruff, mypy e il banco verdi, la release costruita con `scripts/costruisci-skill.py`.
