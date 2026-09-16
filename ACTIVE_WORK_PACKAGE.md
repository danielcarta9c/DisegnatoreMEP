# DRAW-011 — Il prelievo torna nella distribuzione, e il caso di prova 4 sta in piedi

**Titolo:** Il prelievo torna nella distribuzione, e il caso di prova 4 sta in piedi
**Assegnato da:** PM (Claude — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-16
**Stato:** **ATTIVO.**
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** quello che la piattaforma assegna alla sessione. Il pacchetto **non ne prescrive uno**
**Commit di partenza:** **la testa di `main`**, qualunque essa sia quando la sessione parte.
Il contenuto della base: `DRAW-010` **non fuso** — la PR #32 è stata verificata e respinta, e
il suo lavoro **non è su `main`**. Si riparte da `main`, non dal ramo della PR.
**Fixture grafica principale:** impianto 2 e impianto 4; impianto 1 come regressione automatica

> **Leggere prima:** `docs/pm/2026-09-15-review-pr32-draw010.md` — il verdetto del PM sulla
> PR #32, in particolare §3 (i rilievi del PO) e §7 (la causa unica). E
> `docs/collaudi/DRAW-010/RAPPORTO.md` §6.2, §6.3 e §6.5 del ramo della PR #32, che restano
> la diagnosi migliore di ciò che è andato storto. Questo pacchetto non li ripete.

---

## Contesto

`DRAW-010` è stato consegnato e **respinto**. Dodici criteri su sedici erano raggiunti, il
lavoro sotto era serio — l'anello è stato capito davvero e l'impianto 4 era tornato a uscire
— ma la tavola 2 peggiorava su due budget e la suite passava da 10 rosse a 14.

**La causa è una sola, e due strade indipendenti ci sono arrivate.** Il DEV, misurando,
attribuisce a `DRAW-010` §D.1 tutte e otto le prove nuove rosse, l'arretramento
dell'impianto 5 e i tre incroci in più della tavola 2. Il PO, guardando la tavola senza aver
letto il rapporto, ha indicato lo stesso punto.

**Non è il criterio a essere sbagliato: è come D-126 è stato attuato.** D-126 dice che il
prelievo «si posa nelle immediate vicinanze del pezzo che serve e con la propria giacitura
scelta per non pagare pieghe». È stato letto come «appendilo al bollitore», e il prelievo si
è spostato di 45 mm **verso il centro del foglio** mentre a destra restavano 92,5 mm liberi.
Il PO intendeva: **nella zona di distribuzione, e se serve spazio si allargano le macchine** —
il contratto §A.3 che dice che spostare le macchine non costa, e che nessuno ha usato.

Questo pacchetto **non riscrive `DRAW-010`**: ne raccoglie il lavoro buono e corregge quella
attuazione. Il DEV che lo prende può ripartire dal ramo della PR #32 come riferimento di
lettura, ma il codice si scrive su `main`.

---

## A. Il prelievo si posa nella distribuzione, e le macchine si allargano per fargli posto

1. Un **prelievo** si posa **nella zona a cui appartiene** — la distribuzione — e non addosso
   al pezzo che lo alimenta. La vicinanza di D-126 è al **circuito**, non al serbatoio.
2. Se per posarlo lì servono più millimetri, **si prendono**: le macchine principali si
   allargano. È il contratto di sempre e va usato, non citato.
3. **Misura di accettazione:** sulla tavola 2 il prelievo ACS sta a destra del volano, come
   sulla base, e la sua tratta non paga pieghe. Riferimenti: base x 257,5; `DRAW-010`
   x 212,5, che è il difetto.
4. **La giacitura di `utenze` è parte del criterio, e la cura non è nella posa.** Il rapporto
   di `DRAW-010` §6.3 dichiara che la posa gliela dà giusta e **il ciclo la disfa**, e che
   tenergliela costa venticinque pieghe. È lì che si interviene.

## B. Lo stacco dello scarico non attraversa quando può non farlo

Sulla tavola 2 lo stacco dello scarico dell'acqua fredda in `DRAW-010` sale di 42,5 mm e
nel salire attraversa la mandata verso il bollitore, mentre sotto il foglio è libero. Uno
stacco sceglie il verso che non attraversa, quando un verso libero c'è.

## C. La tavola 2 e la suite rientrano

1. **La tavola 2 non peggiora su nessuno dei tre budget.** Riferimento, misurato dal PM sulla
   testa di `main` con lo stesso strumento sui due lati: **5 pieghe, 1 incrocio, 600,0 mm**.
   Organi D-120 vicini: **11 su 14** (il pacchetto precedente diceva «14 su 15» e sbagliava:
   quindici è il totale della tavola 1).
2. **Il saldo della suite migliora e non peggiora.** Riferimento su `main`, rimisurato dal
   PM: **10 rosse, 1470 verdi, 24 saltate, 11 xfailed**. Nessuna prova convertita in `skip`
   o `xfail`, nessuna soglia allentata, nessuna fixture toccata.
3. **L'impianto 5 non arretra.** Su `main` arriva alla posa e alla fase del tronco, pur non
   producendo una tavola; in `DRAW-010` si fermava prima, sulle fasce (447,5 mm contro 335).
   Deve tornare almeno dov'era.
4. **L'impianto 4 continua a uscire e l'impianto 1 non peggiora.** Riferimento tavola 1:
   4 pieghe, 1 incrocio, 470,0 mm.

## D. Il caso di prova 4 si riscrive, e il grafo è questo

Il PO ha verificato che l'impianto 4 **non sta in piedi** e ha scelto lo schema nuovo
(**D-137**). Il grafo è scritto qui per esteso perché non ci sia niente da interpretare: è
la lezione di D-126.

**Componenti** — tutti già in catalogo tranne l'ultimo:

| id | definizione |
|---|---|
| `pdc` | `heat-pump-air-water` |
| `caldaia` | `gas-boiler` |
| `ritegno-pdc` | `valve-check` |
| `ritegno-caldaia` | `valve-check` |
| `collettore-mandata` | `tee-junction` |
| `disgiuntore` | `buffer-four-port` |
| `collettore-ritorno` | `tee-split` |
| `deviatrice-caldaia` | `diverting-valve-3way` |
| `commutatrice-ritorno` | **voce nuova**, vedi §D.2 |
| `scambiatore` | `plate-heat-exchanger` |
| `circolatore` | `pump-circulator` |
| `radiatori` | `radiator` |
| `acquedotto` | `cold-water-inlet` |
| `utenze` | `dhw-draw-off` |

**Collegamenti**, in quest'ordine:

```
pdc.water_supply            → ritegno-pdc.a
ritegno-pdc.b               → collettore-mandata.a
caldaia.water_supply        → deviatrice-caldaia.in
deviatrice-caldaia.out_a    → ritegno-caldaia.a
ritegno-caldaia.b           → collettore-mandata.c
collettore-mandata.b        → disgiuntore.primary_in
disgiuntore.primary_out     → collettore-ritorno.a
collettore-ritorno.b        → pdc.water_return
collettore-ritorno.c        → commutatrice-ritorno.<ingresso primario>
deviatrice-caldaia.out_b    → scambiatore.primary_in
scambiatore.primary_out     → commutatrice-ritorno.<ingresso sanitario>
commutatrice-ritorno.out    → caldaia.water_return
disgiuntore.secondary_out   → circolatore.a
circolatore.b               → radiatori.in
radiatori.out               → disgiuntore.secondary_in
acquedotto.a                → scambiatore.secondary_in
scambiatore.secondary_out   → utenze.a
```

### D.1 Che cosa cambia rispetto a oggi, e perché

- **Due ritegni, uno per generatore.** Oggi non ce n'è nessuno in tutto l'impianto: il
  generatore fermo viene attraversato in controflusso.
- **Il volano diventa il disgiuntore** fra generatori e distribuzione, invece di stare in
  serie a valle del collettore. Il catalogo già gli dichiara `hydraulic_separation`.
- **Il sanitario è un circuito chiuso della caldaia**, come nei sistemi ibridi compatti:
  l'acqua calda la fa sempre il gas.
- **Lo scambiatore sta in centrale**, fra i collegamenti principali (`I-066`).

### D.2 La voce di catalogo nuova: la commutatrice a tre vie sul ritorno

Perché il circuito sanitario sia **davvero** dedicato, la caldaia deve poter scegliere da
dove pesca: dal primario quando fa riscaldamento, dallo scambiatore quando fa sanitario.
Senza, mentre fa sanitario pesca da entrambi — ed è il «ritorno che torna ovunque».

Il catalogo non ha il pezzo: `mixing-valve-3way` ha la geometria giusta (due ingressi, una
uscita) ma dichiara `circuit_mixing`, che è un'altra funzione, e **una funzione non si piega
per far tornare un disegno**. Serve una definizione nuova — due ingressi, un'uscita, funzione
di commutazione — con il proprio simbolo. Il simbolo può essere quello della deviatrice: è
la stessa valvola, montata al contrario.

### D.3 Che cosa non si tocca

Gli altri quattro casi di prova. E la potenza dei generatori, il tipo di terminale e ogni
altro dato MEP: il PO ha dettato lo schema, non i dati di dimensionamento.

## E. La tavola 4 si misura solo dopo §D

Finché il caso di prova è quello vecchio, misurare la leggibilità della tavola 4 non ha
senso: si sta disegnando bene un impianto che non sta in piedi. Rifatto il grafo, la tavola 4
si misura e si riferisce: **esce, e i suoi ritorni seguono l'asse invece di girare.** Oggi
otto tratte prendono una piega e tre sono lunghe 197,5, 155,0 e 137,5 mm, mentre pompa di
calore, volano e radiatori stanno sulla stessa quota.

Non è un criterio di accettazione alla prima consegna — il grafo è nuovo e non c'è un
riferimento con cui confrontarlo — ma il rapporto porta la tavola e le misure, e il PO la
guarda.

---

## Nota di metodo

Valgono per intero le tre avvertenze di `DRAW-010` — il `.pth` dell'installazione editable,
la mezz'ora per esecuzione della suite, la linea di partenza degli impianti 3 e 5 — e se ne
aggiunge una quarta, che è costata questa consegna:

4. **Una disposizione del PO si attua come è scritta, e dove è ambigua si chiede.** D-126
   diceva «nelle immediate vicinanze del pezzo che serve»: è stato letto «appeso al
   bollitore», e sono costati tre incroci, 45 mm, otto prove rosse e un impianto arretrato.
   Quando una disposizione ammette due letture, il DEV **si ferma e chiede al PM**, che
   chiede al PO. Costa un giro; l'altra strada è costata un pacchetto.

Gli strumenti di misura non si riscrivono: `docs/collaudi/DRAW-008/metriche.py`,
`docs/collaudi/DRAW-009/criteri.py` e `le-due-sovrapposizioni.py`, e — dal ramo della PR #32,
che restano validi anche se la PR non si fonde — `chi-compone.py`, `il-ripiego.py`,
`la-catena-fredda.py`, `le-coppie-addosso.py`, `il-prelievo-acs.py`,
`perche-l-anello-non-separava.py`.

---

## Perimetro

**Dentro:** la posa del prelievo e la sua giacitura (§A); il verso degli stacchi che possono
non attraversare (§B); i budget della tavola 2, il saldo della suite, l'impianto 5 (§C); il
caso di prova 4 e la voce di catalogo nuova (§D); la misura della tavola 4 (§E); il rapporto
di consegna.

**Fuori:** la libreria dei simboli, salvo il solo simbolo della commutatrice di §D.2;
l'ordine degli stacchi lungo il tronco (rischio 17); le due prove che difendono il pavimento
invisibile (rischio 21); lo spessore del tratto per gerarchia (**D-132**, è del pacchetto
dopo); il verso di mandata e ritorno deciso dalla geometria (**D-136**, è del pacchetto
dopo); qualunque decisione MEP che il PO non abbia dato.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**. Un criterio
irraggiungibile si dichiara tale con la misura che lo prova, non si ammorbidisce.

1. **Sulla tavola 2 il prelievo ACS sta nella zona di distribuzione**, a destra del volano, e
   la sua tratta non paga pieghe. Misura prima e dopo.
2. **`utenze` non è più posato con la bocchetta verso il basso**, e il rapporto dice che cosa
   nel ciclo disfaceva la giacitura e come è stato corretto.
3. **Le macchine principali si sono allargate** dove serviva a fare spazio, e il rapporto lo
   misura: posizioni prima e dopo, e i millimetri di foglio ancora liberi.
4. **Nessuno stacco attraversa una tratta quando il verso opposto è libero**, con una prova
   generale che lo dice nella propria regola.
5. **La tavola 2 non peggiora su nessuno dei tre budget.** Riferimento: 5 pieghe, 1 incrocio,
   600,0 mm; organi D-120 vicini 11 su 14.
6. **La tavola 1 non peggiora.** Riferimento: 4 pieghe, 1 incrocio, 470,0 mm.
7. **Il saldo della suite migliora e non peggiora.** Riferimento: 10 rosse, 1470 verdi,
   24 saltate, 11 xfailed.
8. **L'impianto 5 arriva alla posa e alla fase del tronco**, come su `main`.
9. **Il caso di prova 4 è riscritto** esattamente secondo §D, e il rapporto mostra il grafo
   nuovo accanto a quello vecchio.
10. **La commutatrice a tre vie è una voce di catalogo con la propria funzione dichiarata**,
    non una miscelatrice piegata, e ha il proprio simbolo.
11. **L'impianto 4 produce una tavola** con il grafo nuovo, e il rapporto la porta.
12. **I ritorni della tavola 4 seguono l'asse**: il rapporto misura quante tratte prendono
    una piega e quanto sono lunghe, e le confronta con le otto e i 197,5 / 155,0 / 137,5 mm
    di adesso.
13. **Nessun impianto che compone all'inizio smette di comporre alla fine**, misurato su tutti
    e cinque con il comando e l'esito.
14. **Determinismo**: doppia generazione dalla CLI con la stessa impronta, e forma invariante
    alla ridenominazione degli identificativi.

---

## Consegna

Una PR sola, non fusa. Rapporto in `docs/collaudi/DRAW-011/RAPPORTO.md` con i quattordici
criteri chiusi uno per uno; pacchetto grafico `prima/` e `dopo/` per la tavola 2 e per
l'impianto 4, con l'impianto 1 misurato come regressione. Il DEV apre la PR e si ferma;
verifica e merge sono del PM, che è una sessione diversa dal DEV.

**E una cosa in più, che questa volta conta:** prima di chiudere, **guarda le tavole**. I
quattro difetti che hanno respinto `DRAW-010` li ha visti il PO a occhio, e nessuno dei
sedici criteri li copriva. Se una tavola ti sembra sbagliata e i numeri dicono che va bene,
scrivilo nel rapporto: è il rilievo più utile che puoi portare.

---

## Decisioni che restano al PO

1. **L'ordine degli stacchi lungo il tronco** (rischio 17).
2. **Gli attacchi pari di un collettore**, ereditata da `DRAW-009` e non toccata.
3. **Il pallino di derivazione con due spessori** (D-132): quando in un nodo concorrono un
   tratto da 0,50 e uno da 0,25, il pallino segue il più grosso. È la proposta del PM e
   aspetta il sì del PO.
