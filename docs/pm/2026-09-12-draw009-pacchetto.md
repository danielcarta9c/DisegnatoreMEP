# DRAW-009 — L'ingresso vicino a chi serve, e il tronco che si sposta tutto intero

**Titolo:** L'ingresso vicino a chi serve, e il tronco che si sposta tutto intero
**Assegnato da:** PM-autore (Claude, in sessione col PO — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-12
**Stato:** BOZZA — sottoposta al PO, non ancora approvata
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** da assegnare
**Commit di partenza:** la testa di `main` **dopo il merge di DRAW-008 (PR #26)**
**Fixture grafica principale:** impianto 2; impianto 1 come regressione automatica

> **Leggere prima:** `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md` (l'ordine delle
> decisioni) e `docs/collaudi/DRAW-008/RAPPORTO.md` §6 e §7 (che cosa è rimasto aperto e
> perché). Questo pacchetto ne è il seguito e non li ripete.

---

## Contesto

DRAW-008 ha dato alla posa tre fasi e un invariante per fase. La tavola 2 esce, senza
rilievi bloccanti, e la tavola 1 migliora su tutti e tre i budget. Ma il PO, guardandola,
ha ridisegnato a mano un'autostrada più in basso e ha chiesto perché il motore non ci
fosse arrivato da solo. La risposta, misurata, è che **non è una questione di pesi**:
alzando `TURN_COST` da 100 a 800 la tavola esce identica, e abbassando `STEP_COST`
peggiora. La strada pulita che il PO vede non è cara: è **murata**.

Murata da due cose, e questo pacchetto le toglie entrambe.

**La prima è l'acqua fredda.** Sulla tavola 2 la rete `fredda` è **una linea sola** che
parte dall'`acquedotto`, attraversa il foglio, raccoglie per strada il gruppo di
riempimento del ritorno PDC e finisce sul `cold_in` del bollitore:

```
acquedotto.a
  → valve-isolation-dhw-acquedotto-a
  → tee-filling-unit-pdc-water-return-a   ← primo utente
  → tee-drain-connection-cold-bollitore-cold-in
  → dhw-safety-group-bollitore-cold-in
  → bollitore.cold_in                      ← secondo utente
```

Questo è esattamente ciò che il PO ha vietato, e l'ha già detto una volta (I-061,
11 settembre): «non si deve fare una rete unica di af, non si fa così; si fanno più
ingressi». Una linea che traversa il foglio per servire due utenti lontani **inchioda i
pezzi che tocca**: il bollitore non si può spostare di cinque millimetri senza che
l'instradamento della fredda fallisca, e sei dei nodi che un rango inferiore condivide con
il tronco sono suoi.

Misura, sulla geometria consegnata da DRAW-008:

| nodi condivisi fra un'autostrada e un rango inferiore | 8 |
|---|---|
| di cui della rete `fredda` | **6** |
| di cui della rete `sanitaria` | 2 |

**La seconda è che il tronco, per il ciclo, è fermo.** Il PO ha corretto la lettura che
avevo adottato: il tronco è un **corpo rigido, non un corpo immobile**. Trasla tutto
intero, si allunga lungo il proprio asse, e porta con sé ciò che gli sta appeso. Se il
corredo dell'ACS non sta sotto, si alzano PDC e puffer.

Misura, sulla tavola 2 consegnata, alzando in blocco i partecipanti al tronco:

```
base:      chiave (0, 0, 0.0, 1, 90, 41, 8182.5)   pieghe autostrada = 3
su di  5:  valida,     instradabile,  pieghe autostrada = 3
su di 10:  valida,     NON instradabile
su di 15:  valida,     NON instradabile
su di 20:  NON valida, instradabile,  pieghe autostrada = 1
su di 25:  NON valida, NON instradabile
```

A 20 mm **le pieghe dell'autostrada scendono da 3 a 1**: la geometria che il PO ha
ridisegnato esiste e il router la trova. È stata rifiutata perché la traslazione era
grezza — ho spostato i soli partecipanti al tronco e ho lasciato giù tutto il resto, e la
chiave complessiva è peggiorata di conseguenza `(1, 1, 17.5, 5, 162, 79, 9802.5)`. La mossa
giusta esiste; **oggi il ciclo non ce l'ha**: `_shift_moves` sposta un gruppo per una
relazione già esistente, `_column_moves` una colonna, `allungo` taglia il foglio e pretende
che qualcuno resti fermo. Nessuna trasla un blocco allineato *insieme a tutto ciò che deve
seguirlo*.

---

## A. Gli ingressi dell'acqua fredda (I-061)

Ha due metà, e sono separabili: la prima è **contenuto**, la seconda è **disegno**.

### A.1 Un ingresso per utente — contenuto

1. Dove più utenti prendono acqua fredda, il grafo porta **più confini di rete distinti**,
   uno per utente, ciascuno con la propria rete. **Mai** una rete unica che si dirama.
2. I due ingressi sono pezzi diversi, con sigle diverse nella serie `AF.01`, `AF.02`, …, e
   stanno **lontani l'uno dall'altro**: ciascuno vicino al proprio utente.
3. Sulla tavola 2 questo significa due ingressi al posto di uno: uno per il gruppo di
   riempimento del ritorno PDC, uno per il `cold_in` del bollitore.
4. **L'unione a T con un ingresso solo esiste**, per risparmiare sui piccoli componenti a
   servizio dell'ingresso — è rara, ed è **un'opzione che chiede il progettista**. Non è
   mai il default, non si deduce dal grafo e non la sceglie il codice. Finché il
   progettista non la dichiara, gli ingressi restano separati.
5. Questa metà tocca il completamento deterministico del grafo, non il disegnatore. Vale il
   contratto di `HANDOFF.md`: nessun requisito MEP nasce dal codice.

### A.2 L'ingresso si posa addosso a chi serve — disegno

1. Un confine di rete non ha una posizione propria: esiste per immettere. Va posato **nelle
   immediate vicinanze dell'utente che serve**, e la posizione si sceglie per azzerare
   attraversamenti e pieghe della sua tratta.
2. Questo vale per ogni confine di rete, non solo per l'acqua fredda, e vale anche se
   A.1 non viene attuata: **un ingresso che traversa il foglio è un difetto anche quando
   l'utente è uno solo.**
3. Un confine di rete non può inchiodare una macchina di spina. Se la tratta di un ingresso
   è l'unica ragione per cui un pezzo non si può spostare, si sposta l'ingresso.

---

## B. Il tronco è un corpo rigido, non un corpo immobile

1. La fase delle strade di servizio (DRAW-008 §C.1) diceva «un tronco fermo». Si corregge:
   il tronco **non si piega e non si deforma**, ma **trasla** lungo i propri assi e **si
   allunga** lungo il proprio asse.
2. Nasce una **mossa nuova**: la **traslazione di blocco**. Un insieme di pezzi allineati
   si sposta tutto intero di una stessa quantità, portando con sé tutto ciò che deve
   seguirlo — accessori in linea, corredo appeso ai suoi membri, figure che pendono da un
   partecipante. Il resto del foglio resta dov'è.
3. Il blocco **non si deforma**: dopo la traslazione ogni distanza interna al blocco è
   quella di prima. Se un pezzo non può seguire, la mossa non si fa; non si fa a metà.
4. Come ogni spostamento di macchina, la traslazione **costa zero**. Si giudica solo sulla
   chiave di costo del **foglio intero** dopo il reinstradamento, mai sul solo tronco.
5. Gli invarianti di fase di DRAW-008 restano: la traslazione non può piegare il tronco né
   rendere storta una tratta che era rettilinea (`Improver.is_valid`).

---

## C. Il gomito solo

1. Dove una tratta di tronco **non può** essere rettilinea — perché il catalogo non lo
   consente, ed è il caso delle due tratte della tavola 2 (`spine.SpineLayout.impossible`)
   — la fase del tronco oggi la posa alla **campata minima**. Sbagliato: alla campata
   minima il gomito si moltiplica.
2. La fase del tronco deve posare quella tratta **dove il gomito esce singolo**: una piega
   e una sola. Fra le pose che danno una piega sola si sceglie la più corta; se nessuna la
   dà, si sceglie quella con meno pieghe e il codice la nomina.
3. Questo è l'anello che mancava in DRAW-008 e che ha prodotto la tavola che il PO ha
   ridisegnato a mano.

---

## D. L'ordine delle due zone è libero

Risposta del PO del 12 settembre al punto §7.4 del rapporto DRAW-008:

> «Ovviamente l'ordine non è importante. Zona 1 e 2 con radiatori o pavimento radiante è
> indifferente, a meno che non sia il progettista a dare una specifica diversa nel suo
> input.»

1. `tests/layout/test_objective.py::test_parallel_branches_are_stacked_not_strung_out` va
   **riscritta su ciò che vuole davvero**: le due zone stanno impilate sulla stessa
   colonna, e non allungate in fila. L'ordine verticale **non si asserisce**.
2. La regressione 3 di DRAW-008 (§6.3) si chiude **per decisione, non per codice**: non era
   un difetto, era una prova che vincolava più del dovuto.
3. La specifica del progettista, se un giorno arriverà, sarà un campo dichiarato del
   modello. **Non è di questo pacchetto** e non si anticipa.

---

## E. Le due regressioni di vicinanza di DRAW-008

`tests/layout/test_vicinanza_valvole.py`, due prove rosse: sulla tavola 2 l'organo
`valve-isolation-dhw-hot-utenze-a` sta a 10,0 mm dalla miscelatrice con cui fa coppia
invece che a 2,5÷5 mm, e gli organi governati da D-120 passano da 14 su 15 a 13 su 15.

La causa dichiarata nel rapporto è geometrica: il bollitore sta sotto il tronco e la sua
uscita sanitaria deve risalirlo, e su quella tratta il rettilineo accanto alla miscelatrice
non basta più. **A e B tolgono proprio quel vincolo**: liberato dall'ingresso dell'acqua
fredda, il bollitore si sposta; con la traslazione di blocco si sposta anche il tronco.
Le due prove tornano verdi senza essere toccate, oppure il DEV riferisce perché no.

---

## Perimetro

**Dentro:** il completamento del grafo per gli ingressi di rete (A.1); la posa dei confini
di rete (A.2); la mossa di traslazione di blocco (B); la scelta di posa delle tratte non
rettilineabili nella fase del tronco (C); la riscrittura della prova sulle due zone (D); le
misure e il rapporto di consegna.

**Fuori:** l'opzione dell'unione a T dichiarata dal progettista (A.1.4 — si scrive la
regola, non il campo del modello); la rotazione del bollitore nella libreria dei simboli;
qualunque raccordo aggiunto al grafo per raddrizzare le due tratte impossibili (§7.1 del
rapporto DRAW-008 — **decisione del PO**, vedi sotto); le permutazioni fra attacchi pari di
un collettore (vedi sotto); I-059, lo spessore del tratto per gerarchia; il riempimento
estetico del foglio, il cartiglio, l'audit dei simboli; gli impianti 3–5 oltre la prova di
posa.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**, come in DRAW-008. Un
criterio irraggiungibile si dichiara tale con la misura che lo prova, non si ammorbidisce.

1. **Sulla tavola 2 la rete fredda non è più una linea sola.** Il grafo completato porta
   due confini di rete distinti, con due reti distinte, e nessuna tratta di acqua fredda
   serve due utenti in serie.
2. **Una prova generale** mostra che, dati due utenti di acqua fredda, il completamento
   produce due ingressi e non una rete che si dirama — e che l'unione a T non compare mai
   se non è dichiarata.
3. **Ogni confine di rete della tavola 2 ha una tratta senza pieghe** e non attraversa
   nessuna tratta di livello autostrada.
4. **I nodi condivisi fra un'autostrada e un rango inferiore sulla tavola 2 scendono da 8 a
   non più di 2**, con la ripartizione per rete prima e dopo.
5. **Esiste la mossa di traslazione di blocco**, e una prova su un impianto costruito a
   mano la mostra vincere là dove nessuna mossa esistente vince.
6. **La traslazione di blocco non deforma il blocco**: prova generale che dopo la mossa
   ogni distanza interna al blocco è invariata, e che se un pezzo non può seguire la mossa
   non si fa.
7. **Una prova negativa**: una traslazione che piega il tronco viene rifiutata da
   `is_valid` anche quando batte la chiave di costo.
8. **Sulla tavola 2 le pieghe di livello autostrada scendono da 3 a 1** — il valore
   misurato sulla mossa che il PO ha indicato. Se non è raggiungibile, si dichiara con la
   misura.
9. **Ogni tratta di tronco non rettilineabile ha una piega sola**, e l'elenco delle
   eccezioni lo calcola il codice.
10. **`test_parallel_branches_are_stacked_not_strung_out` riscritta sull'impilamento**,
    senza ordine, verde, e con una prova negativa che fallisce davvero se le due zone si
    allungano in fila.
11. **Le due prove di vicinanza tornano verdi**: gli organi governati da D-120 tornano 15
    su 15 sulla tavola 2. Se no, il DEV riferisce perché con la misura.
12. **La tavola 1 non peggiora** su nessuno dei tre budget (pieghe, incroci, lunghezza), e
    nessuna delle sue tratte di autostrada prende una piega.
13. **Determinismo**: doppia generazione dalla CLI con la stessa impronta, e impronta
    invariante alla ridenominazione degli identificativi.
14. **Il saldo della suite migliora e non peggiora.** Nessuna prova convertita in `skip` o
    `xfail`, nessuna soglia allentata.

---

## Consegna

Una PR sola, non fusa. Rapporto in `docs/collaudi/DRAW-009/RAPPORTO.md` con i quattordici
criteri chiusi uno per uno; pacchetto grafico `prima/` e `dopo/` per la sola tavola 2, con
l'impianto 1 misurato come regressione. Il DEV apre la PR e si ferma; il PM-revisore è un
agente separato avviato da zero; **il merge su `main` è del PO**.

---

## Decisioni che restano al PO

1. **Le due tratte impossibili della tavola 2** (§7.1 del rapporto DRAW-008). L'uscita
   secondaria della deviatrice guarda in basso, la serpentina del bollitore si imbocca da
   sinistra, il bollitore non ammette rotazioni: nessuna posa le mette una di fronte
   all'altra. Tre strade, nessuna del DEV: accettare il limite (e il criterio 9 diventa la
   forma definitiva della regola), dare una rotazione al bollitore nella libreria, oppure
   mettere un raccordo nel grafo. **Questo pacchetto assume la prima** e la scrive come
   criterio 9; se il PO ne sceglie un'altra, il criterio cambia.
2. **Gli attacchi pari di un collettore.** La risposta al punto D apre una domanda più
   profonda che questo pacchetto non tocca. Oggi `_admitted_permutations` mette il
   collettore di zona nella stessa categoria della valvola miscelatrice: nessuna
   permutazione, perché «ogni porta ha un ruolo». Ma su un collettore `out_1` e `out_2`
   sono due prese identiche sulla stessa barra, e se l'ordine delle zone è libero allora
   sono scambiabili. Il guaio è che **il catalogo oggi non sa dirlo**: su
   `mixing-valve-3way` gli attacchi `hot_in` e `cold_in` dichiarano lo stesso dominio, lo
   stesso fluido e lo stesso verso, e si distinguono solo per il nome. Una regola meccanica
   «stesso dominio, stesso fluido, stesso verso ⇒ scambiabili» scambierebbe la calda con la
   fredda su una miscelatrice, che è un errore d'impianto, non una scelta di disegno.
   Perciò la scambiabilità va **dichiarata nel catalogo**, non dedotta — ed è un pacchetto
   a sé, da aprire se e quando il PO lo vuole.
