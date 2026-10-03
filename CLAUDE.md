# Istruzioni di ingresso per Claude

Prima di analizzare il codice, proporre un piano o eseguire qualunque modifica:

1. leggi integralmente `ACTIVE_WORK_PACKAGE.md`;
2. leggi il breve `HANDOFF.md`;
3. leggi `docs/ARCHITETTURA-DEL-PIANO.md` — dice **chi decide cosa** nel disegno, ed è
   vigente da **D-151**;
4. leggi in `AGENTS.md` soltanto il modello PO/agente e i documenti che il Work Package
   indica;
5. verifica base, ramo e perimetro prescritti;
6. esegui esclusivamente il Work Package attivo.

`ACTIVE_WORK_PACKAGE.md` è l'unico incarico operativo corrente. La storia si apre soltanto
quando il pacchetto rinvia a una decisione precisa: non è onboarding.

Se il Work Package è assente, già consegnato, ambiguo o incompatibile con lo stato del
repository, fermati e chiedi al PO. Non scegliere autonomamente il lavoro successivo.

## Sei un agente solo

Dal 19 settembre 2026 (**D-147**, `docs/governance/OPERATING_MODEL.md` §1.2.1) **PM e DEV
sono la stessa sessione.** Non c'è un'altra sessione che scrive i pacchetti, e non c'è
un'altra sessione che verifica la consegna. Puoi lanciare **agenti in parallelo dentro la
sessione** (**D-152**, §1.2.2) — perimetro dichiarato prima, e quello che riferiscono non è
una misura finché non l'hai rieseguito. Sopra di te c'è il PO, e il suo controllo è uno:
**guarda le tavole.**

Il ciclo è:

1. scrivi il pacchetto e sviluppalo, nella stessa sessione;
2. **mostra le tavole al PO** — per prime, prima di qualunque numero (**D-146**);
3. il PO approva la fusione, oppure no;
4. fondi su `main` **solo dopo quell'approvazione**, e solo tramite pull request;
5. nella stessa sessione scrivi `HANDOFF.md` e il pacchetto successivo.

**Non fondere mai senza che il PO abbia visto le tavole e detto di sì.** È l'unico controllo
rimasto, e sostituisce tutto quello che è stato abolito.

Se da un impianto di prova **non esce nessuna tavola**, quella è la prima cosa che dici — non
l'ultima, e non una nota in fondo al rapporto.

## Le due regole che il controllo incrociato non tiene più su

Adesso che nessuno verifica al posto tuo, queste valgono di più, non di meno:

- **prima le misure, poi il racconto** — anche verso te stesso: misura, poi scrivi che cosa
  hai ottenuto. Un criterio senza un comando e il suo output è **non raggiunto**;
- **se una tavola ti sembra sbagliata e i numeri dicono che va bene, scrivilo.** È il rilievo
  più utile che puoi portare, ed è due volte su due il modo in cui i difetti veri sono stati
  trovati in questo progetto.

## La skill si carica, o non è una release

Dal 3 ottobre 2026 (**I-189**, **D-200**): una release si costruisce **solo** con
`scripts/costruisci-skill.py`, e va in `releases/` **solo** se `tests/test_le_release.py` passa.
La costruzione e quella prova controllano i limiti del caricamento su claude.ai — **al massimo
200 file nello ZIP**, la skill in una cartella sola, sotto i 30 MB — e le linee guida di
Anthropic sulla skill (frontespizio, descrizione entro 200 caratteri, `SKILL.md` sotto le 500
righe, riferimenti a un livello). L'elenco con le fonti è in `releases/README.md`. Un controllo
non si toglie e non si allenta per far passare una release.

**Il lavoro di una sessione esiste quando è su `main`.** La correzione dei 200 file era stata
fatta il 2 ottobre su un ramo mai fuso, e due release sono uscite senza (I-188). Una sessione
non si chiude con lavoro su un ramo senza PR; e all'avvio si guardano le PR aperte.

## Quello che resta del PO, e non è tuo

Una disposizione del PO si implementa **come è espressa** (`OPERATING_MODEL.md` §1.1.1), anche
adesso che chi la riceve è anche chi la eseguirà. Non ti appartengono, e non ti sono mai
appartenuti: approvare una decisione, chiudere un input del PO, decidere un contenuto MEP,
cambiare una convenzione grafica. Su questi si chiede.
