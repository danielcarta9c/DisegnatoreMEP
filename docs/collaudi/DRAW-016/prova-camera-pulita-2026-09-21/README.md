# La prova in camera pulita del pianificatore — 21 settembre 2026

**Che cos'è.** La prima volta che `skill/comporre/` ha composto da solo. Agenti avviati da
zero, che hanno ricevuto **soltanto** `skill/comporre/ISTRUZIONI.md`, il **grafo scheletro** e
i manifesti dei simboli, e a cui era **vietato leggere qualunque piano già esistente** — i
cinque scritti a mano compresi. Hanno composto, provato il proprio piano col comando, e
corretto fino a farne uscire la tavola.

**Che cosa NON è.** Non è prodotto, e **non si corregge a mano**: è la **misura** di che cosa
sa fare il pianificatore il 21 settembre 2026. Chi la ritocca cancella la misura. Se il
pianificatore migliora, si **rifà la prova** e si scrive la misura nuova accanto a questa.

> ⚠ **`scheletro-N.json` non è un impianto vero** e non deve diventarlo: è il grafo ridotto a
> **sole macchine e collettori**, senza una valvola, prodotto da `../riduci-a-scheletro.py`.
> Serve a **guardare le autostrade**, che è la prova che il PO ha chiesto:
> «disegnare le tavole senza le valvole in mezzo, per vedere se gli agenti riescono a disegnare
> queste autostrade come farebbe un disegnatore umano».

## Le misure, rieseguite dalla sessione

Non sono i numeri che gli agenti hanno riferito: sono quelli **rimisurati** rieseguendo i loro
piani (**D-152** — quello che un agente riferisce non è una misura finché non lo si è
rieseguito).

| impianto | | piano **a mano** | agente, 1° giro | agente **con B12** |
|---|---|---|---|---|
| **1** | formato | A2 | **A4** | — |
| | spezzate piegate | 4 | **3** | |
| | pieghe | 6 | **4** | |
| | incroci | 1 | 1 | |
| **4** | formato | A2 | A3 | **A4** |
| | spezzate piegate | 7 | 5 | **4** |
| | pieghe | 12 | 7 | **5** |
| | incroci | 3 | 5 | **3** |
| **5** | formato | A1 | A2 | **A3** |
| | spezzate piegate | 13 | 13 | **12** |
| | pieghe | 23 | 16 | **16** |
| | incroci | 12 | 6 | **5** |

**Zero tratte cedute e zero rilievi bloccanti su tutti.**

**Il salto è il formato.** L'impianto 5 passa da **A1 ad A3** — un quarto di foglio — e il 4 da
**A2 ad A4**. Non è una misura di stile: il foglio più piccolo in cui un impianto ci sta è il
modo più diretto che abbiamo per dire che **il disegno non spreca**.

**B12 si vede dove è stata applicata.** Sull'impianto 5 le tre pompe sono impilate strette, i
due collettori stanno **addosso a loro** su due verticali corte a 15 mm, e le tre utenze sono
servite da **due colonne adiacenti con una coppia di orizzontali ciascuna** — mandata sopra,
ritorno sotto, affiancate fino al terminale, che entra **da sinistra**. Sull'impianto 4 la
tratta caldaia → scambiatore corre come **due orizzontali affiancate a interasse 15**, che è
esattamente quello che il PO aveva ridisegnato a mano.

## Quello che non è venuto, e che non è colpa della posa

Tre cose, riferite **indipendentemente** da più agenti e verificate:

1. **Il bilancio di B1 è irraggiungibile dove il simbolo impone la piega.**
   `HIGHWAY_IS_NOT_STRAIGHT` dà **zero** pieghe ammesse a ogni catena fra due pezzi di spina,
   ma una catena che passa per un **collettore verticale** ne ha due agli estremi per forza, e
   una che attraversa una **valvola a tre vie sulla terza via** ne ha una imposta dal simbolo.
   Due agenti su due l'hanno detto con le stesse parole: *«il numero è irraggiungibile, non il
   disegno è sbagliato»*. **È la stessa famiglia di B7 e della contraddizione B1 contro B3**,
   già aperte al PO.
2. **B12 presuppone una ramificazione simmetrica.** Sull'impianto 5 l'ultimo nodo prima del
   volano raccoglie l'utenza **più lontana**: con due sole colonne viene o un sali-scendi o
   una sovrapposizione, e l'agente ha usato una **terza verticale** per il ritorno del
   radiante, dichiarandolo. **O la topologia è quella e la terza colonna è vera, o il grafo va
   guardato**: è contenuto MEP, e va al PO.
3. **L'interasse cambia 15 → 10 sui terminali** (D-167 li ha lasciati a 10 perché dentro un
   simbolo alto 15 due porte a 15 non ci stanno), e `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` lo
   nomina. **Si chiude alzando il simbolo**, che è materia del PO.

## Che cosa gli agenti hanno insegnato alle istruzioni

Le mancanze riferite sono già entrate in `skill/comporre/ISTRUZIONI.md`: quali pezzi vanno nel
piano, che le coordinate **non** sono sul foglio, la rotazione obbligatoria sulle tre vie e i
simboli che non si ruotano, e i quattro numeri che **tutti** hanno dovuto leggere dai messaggi
d'errore.

**Restano fuori, e sono il lavoro del prossimo giro:** l'algebra delle valvole a tre vie (la
terza via è perpendicolare alla via dritta, e questo decide la posa intera), il fatto che il
motore **rifà la mappa delle porte dei raccordi** — che è l'unico motivo per cui un T può
stare in una giacitura che il manifesto dichiara impossibile — e un margine di servizio: a
comporre sotto `x≈15, y≈25` le tratte non si instradano.
