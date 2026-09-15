# DRAW-010 — Il tronco posa senza pezzi addosso, e l'impianto 4 torna a uscire

**Titolo:** Il tronco posa senza pezzi addosso, e l'impianto 4 torna a uscire
**Assegnato da:** PM (Claude — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-14
**Stato:** **ATTIVO.** Il PO ha disposto in sessione il 14 settembre 2026 che il pacchetto
vada su `main`, così che la sessione DEV successiva sappia che cosa fare. I contenuti di §D
sono **disposizioni del PO** date quella sera (D-126, D-127, D-129); §A, §B, §C ed §E sono
mezzi scelti dal PM in funzione di ciò che la verifica di `DRAW-009` ha trovato
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** quello che la piattaforma assegna alla sessione. Il pacchetto **non ne prescrive
uno**
**Commit di partenza:** la testa di `main`, `b825b25` — `DRAW-009` fuso (PR #27) e questo
pacchetto reso attivo (PR #28)
**Fixture grafica principale:** impianto 4 e impianto 2; impianto 1 come regressione automatica

> **Leggere prima:** `docs/pm/2026-09-14-review-pr27-draw009.md` (il verdetto del PM sulla
> consegna precedente, in particolare §3.1 e la postilla sull'impianto 4) e
> `docs/collaudi/DRAW-009/RAPPORTO.md` §6.3, §6.5 e §7.3. Questo pacchetto ne è il seguito
> e non li ripete.

---

## Contesto

`DRAW-009` è stato verificato e fuso. Ha fatto ciò che il suo pacchetto chiedeva: l'acqua
fredda non è più una linea sola, i nodi che un rango inferiore condivideva col tronco sono
passati da 8 a zero, `p4` ha perso il giro, la tavola 1 è migliorata su due budget su tre e
non è peggiorata su nessuno.

**Ma ha lasciato scoperta la posa da cui tutto parte, e si è visto dopo il merge.**

### L'impianto 4 non produce più una tavola

Misurato dal PM sulla testa di `main` appena fusa, con lo stesso comando sui due
lati:

| impianto 4 | esito |
|---|---|
| base `b63e3e6` | **la tavola esce** |
| `main` `2155c22` | **non esce**, in 12 secondi |

```
run s3-a sul secondario: nessun percorso da (147,70) a (116,76):
i 6 passi dritti che la catena chiede oltre l'attacco a (116,76)
finiscono contro un ostacolo a (118,76)
```

Dodici secondi: non è un esaurimento del tempo, è un rifiuto dell'instradatore.

**Il rischio 14 si è avverato.** Diceva che l'impianto 4 usciva **soltanto grazie al
ripiego** di `compose_sheet`, e che il ripiego era «una rete di sicurezza, non una
soluzione». Adesso la rete non regge più.

**Nessuna prova se n'è accorta**, perché la suite pretende che **un impianto solo** sappia
comporsi:

```python
COMPONIBILI = ("prova-1-due-pdc-accumulo-combinato.json",)
```

L'impianto 4 componeva **per capacità, non per contratto**. Quando l'ha perso, la suite è
rimasta verde. Questo è un difetto della copertura, e vale quanto il difetto che ha
nascosto.

### La causa a monte è l'anello, ed è il rischio 16

La fase del tronco consegna una posa in cui dei pezzi stanno addosso l'uno all'altro.
`_relieve` non li separa perché su un circuito chiuso il tronco è un **anello**: qualunque
sottoalbero si sposti contiene anche l'altro pezzo della coppia, e la mossa si scarta.

`DRAW-009` non l'ha risolto: l'ha reso **innocuo**, rendendo `is_valid` monotona — una mossa
risponde delle sovrapposizioni che **crea**, non di quelle che trova. Il ciclo così esce
dall'impasse, ma il cancello che avrebbe intercettato una posa sovrapposta resta allargato,
e una prova di `DRAW-007` è diventata rossa (rischio 19).

E la posa intermedia **è peggiorata**, cosa che il rapporto di consegna dichiara come
invariata. Misura del PM, stesso strumento sui due lati:

| posa consegnata dalla fase del tronco, tavola 2 | base `b63e3e6` | `main` `2155c22` |
|---|---|---|
| coppie che si sovrappongono davvero | **0** | **1** (`bollitore` ↔ `volano`) |
| coppie più vicine dello stacco ammesso | **4** | **8** |

---

## A. La fase del tronco consegna una posa senza pezzi addosso

1. `lay_the_spine` + `carry_the_rest` devono consegnare una posa in cui **nessuna coppia di
   simboli si sovrappone** e nessuna sta più vicina dello stacco che la posa stessa impone
   fra figure diverse.
2. Il difetto non è la mossa che separa: è che **l'anello non le dà un sottoalbero da
   spostare**. La cura sta lì, e il DEV deve stabilire **con la misura** perché oggi ogni
   candidata di `_relieve` si scarti — non con un'ipotesi. È lo stesso metodo che `DRAW-009`
   ha usato per il giro di `p4`, ed è il metodo che funziona.
3. Vale il contratto: **spostare macchine e accessori non costa.** Se la separazione chiede
   più foglio, si prende più foglio.
4. Gli invarianti di fase di `DRAW-008` restano: la separazione non può piegare il tronco né
   rendere storta una tratta che era rettilinea.

## B. L'impianto 4 torna a uscire, e con lui si guarda il 3

1. **L'impianto 4 produce di nuovo una tavola.** È il criterio che misura §A sul campo.
2. **La tavola 2 esce dalla propria posa a fasi e non dal ripiego.** Oggi esce dal terzo
   ripiego di `compose_sheet` (rischio 16); quando §A è fatto, non deve più servire.
3. **L'impianto 3 si misura e si riferisce.** Oggi si ferma su `p6-a`. Se §A lo fa uscire,
   bene; se no, il rapporto dice **perché**, con la misura. Non è un criterio di
   accettazione: è una misura chiesta.
4. Il ripiego di `compose_sheet` **non si toglie** in questo pacchetto. Va però riferito
   quante volte scatta, impianto per impianto, prima e dopo.

## C. La copertura dice quali impianti devono comporsi

1. `COMPONIBILI` si allarga a **tutti gli impianti che sanno comporsi** alla fine di questo
   pacchetto. Un impianto che compone e non è nell'elenco è una capacità che nessuno
   sorveglia, ed è esattamente come si è perso l'impianto 4.
2. L'elenco è **esplicito e dichiarato**: chi non compone sta nell'altro elenco, con la
   ragione scritta accanto.
3. Il **rischio 22** si incassa qui: l'impianto 2 compone su una A3 e la sua prova è un
   `xfail(strict=True)` rosso anche sulla testa di partenza. Va spostato fra i componibili.

## D. Le tre decisioni del PO del 14 settembre 2026

Il PO ha guardato la tavola 2 consegnata e ha deciso tre cose. Sono **disposizioni**, non
proposte: si attuano come sono espresse (§1.1.1).

### D.1 Il prelievo si posa come un ingresso

> «Il primo gomito in uscita non è sbagliato perché il disegnatore ha tentato di tenere il
> flusso di lettura da sinistra a destra. Giusto. Non capisco però perché abbia forzato a
> mettersi ACS.01 verso l'alto, pagando così una curva inutile. Bastava mettere ACS.01 verso
> destra ed era meglio.»

1. Il gomito con cui la linea esce dal bollitore e piega verso destra **resta**: tiene il
   flusso di lettura da sinistra a destra, ed è voluto.
2. Il **prelievo** si posa nelle immediate vicinanze del pezzo che serve e con la propria
   giacitura scelta per non pagare pieghe — come già fanno gli **ingressi** da `DRAW-009`
   §A.2. Oggi `utenze` è posato a rotazione 90, con la bocchetta verso il basso, e la linea
   deve risalirci dentro.
3. La porta `dhw_out` **resta sulla faccia superiore** del bollitore. Su un bollitore quella
   posizione dice dove si preleva l'acqua calda, ed è la stratificazione. **La libreria dei
   simboli non si tocca.**
4. Il PO ha aggiunto la ragione che la rende definitiva: la faccia destra del bollitore
   servirà al **disegno dei comandi** — la sonda del bollitore collegata alla pompa di
   calore — e portarci anche l'uscita ACS le metterebbe l'una addosso all'altra.

### D.2 Niente freccia sotto la lunghezza minima

> «Secondo me possiamo non metterla tanto si capisce bene lo stesso.»

Su una tratta più corta di quanto una freccia di flusso richieda, **la freccia non si
mette**, e la prova che oggi ne pretende una su ogni tratta non statica si corregge su
questa regola.

### D.3 Lo scarico del bollitore sta dal lato del serbatoio

Difetto trovato dal PM rispondendo al PO, e **antecedente**: stesso ordine sulla
base `b63e3e6`. La catena dell'acqua fredda è

```
acquedotto → intercettazione → T dello SCARICO → GRUPPO DI SICUREZZA → bollitore
```

e il gruppo di sicurezza porta **il ritegno a bordo** (`carries_on_board: [isolation,
non_return]`). Il ritegno sta quindi fra lo scarico e il serbatoio: **aprendo quel rubinetto
il bollitore non si svuota**, si svuota solo il tratto a monte.

La regola `let-what-holds-its-own-volume-empty` lo vieta già con parole sue — «sta dal lato
del serbatoio rispetto all'organo che lo chiude» — ma il motore la applica contro
l'intercettazione, che è un pezzo a sé, e **non contro un organo dichiarato a bordo di un
gruppo**. È lì la cura: chi ordina gli accessori deve contare anche ciò che un composito si
porta dentro.

## E. `is_valid` torna stretta, se §A lo permette

1. Fatto §A, la regola monotona di `DRAW-009` non serve più a sbloccare il ciclo. Va
   riportata alla forma stretta — **nessuna candidata lascia due pezzi addosso** — e la
   prova di `DRAW-007` che oggi è rossa torna verde.
2. Se la misura dice che non si può, si dichiara **con la misura**, e la regola monotona
   resta con la sua motivazione aggiornata. Lo strumento per misurarlo esiste già:
   `docs/collaudi/DRAW-009/le-due-sovrapposizioni.py`.

---

## Nota di metodo — come si misura prima e dopo

Tre cose che sono già costate tempo, una volta ciascuna. Non sono criteri: sono avvertenze.

1. **Il pacchetto è installato in modo *editable*, e il `.pth` in
   `.venv/lib/python3.11/site-packages/` contiene il percorso assoluto di UNA cartella.** Un
   `git worktree` che riusa lo stesso ambiente esegue le prove di prima **con il codice di
   adesso**: un confronto privo di senso, e senza nessun errore che lo dica. Due modi buoni:
   misurare base e ramo **nella stessa cartella**, passando con `git checkout`, oppure usare
   un worktree con `PYTHONPATH="$PWD/src"` davanti al comando. `DRAW-009` ha usato il
   secondo, la verifica il primo, e i numeri coincidono.
2. **La suite integrale richiede circa mezz'ora per esecuzione, e ne servono due** — una per
   lato. Si avviano presto e si lavora ad altro mentre girano.
3. **Sul commit di partenza gli impianti 3 e 5 non producono tavola**, e l'impianto 4 nemmeno
   (§B). Il 3 e il 5 non la producevano nemmeno prima di `DRAW-009`: è la linea di partenza,
   non una regressione da inseguire. L'impianto 4 invece la produceva, ed è il criterio 4.

Gli strumenti di misura già scritti, che non vanno riscritti da capo:
`docs/collaudi/DRAW-008/metriche.py` (misure della tavola per livello di gerarchia),
`docs/collaudi/DRAW-009/criteri.py`, `le-due-sovrapposizioni.py` (il conflitto fra la regola
monotona e la prova di `DRAW-007`, §E) e `due-prove-senza-caso.py`.

---

## Perimetro

**Dentro:** la posa consegnata dalla fase del tronco e il meccanismo che separa i pezzi
(§A); gli impianti 4, 3 e 2 come banco (§B); gli elenchi di copertura della suite (§C); la
posa del prelievo (§D.1); la freccia sotto la lunghezza minima (§D.2); l'ordine degli
accessori rispetto agli organi dichiarati a bordo di un composito (§D.3); `is_valid` (§E);
le misure e il rapporto di consegna.

**Fuori:** la libreria dei simboli, e in particolare la posizione di `dhw_out` sul bollitore
— il PO l'ha escluso esplicitamente; l'ordine degli stacchi lungo il tronco (rischio 17,
resta aperto); le due prove che difendono il pavimento invisibile (rischio 21); lo
squilibrio fra quadranti della tavola 2; gli attacchi pari di un collettore; l'impianto 5
oltre la misura; qualunque decisione MEP che il PO non abbia dato.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**. Un criterio
irraggiungibile si dichiara tale con la misura che lo prova, non si ammorbidisce.

1. **La posa consegnata dalla fase del tronco sulla tavola 2 non ha nessuna coppia di
   simboli sovrapposta**, e nessuna coppia più vicina dello stacco ammesso fra figure
   diverse. Misura prima e dopo, con lo stesso strumento: oggi 1 sovrapposta e 8 troppo
   vicine.
2. **Il rapporto dice perché l'anello impediva la separazione**, con la misura — quali
   candidate `_relieve` generava e perché ciascuna si scartava. Non un'ipotesi.
3. **Una prova generale** mostra che su un tronco ad anello la separazione trova una mossa,
   e una prova negativa mostra che una separazione che piega il tronco viene rifiutata.
4. **L'impianto 4 produce una tavola**, dalla CLI, con la stessa riga di comando con cui
   oggi fallisce. Il rapporto porta la tavola.
5. **La tavola 2 esce dalla propria posa a fasi e non dal ripiego**, e il rapporto dice
   quante volte il ripiego scatta su ciascuno dei cinque impianti, prima e dopo.
6. **L'impianto 3 è misurato**: esce, oppure il rapporto dice dove si ferma e perché.
7. **`COMPONIBILI` elenca tutti gli impianti che compongono** alla fine del pacchetto, e
   l'elenco di chi non compone porta accanto la ragione. L'impianto 2 è fra i componibili.
8. **Sulla tavola 2 la tratta del prelievo ACS non ha nessuna piega oltre quella che tiene
   il flusso di lettura da sinistra a destra**, e `utenze` non è più posato con la bocchetta
   verso il basso. `dhw_out` è ancora sulla faccia superiore e la libreria dei simboli è
   identica al commit di partenza.
9. **Nessuna tratta non statica più corta della lunghezza minima di una freccia pretende una
   freccia**, e la prova lo dice nella propria regola invece che nel proprio esito.
10. **Sulla tavola 2 lo scarico del bollitore sta fra il gruppo di sicurezza e il
    serbatoio**, e una prova generale mostra che un organo dichiarato **a bordo** di un
    composito conta come organo che chiude, ai fini dell'ordine degli accessori.
11. **`is_valid` è tornata stretta** e `test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore`
    è verde — oppure il rapporto dichiara con la misura perché non si può, e la regola
    monotona resta.
12. **La tavola 1 non peggiora** su nessuno dei tre budget (pieghe, incroci, lunghezza), e
    nessuna delle sue tratte di autostrada prende una piega. Riferimento: 4 pieghe,
    1 incrocio, 470,0 mm.
13. **La tavola 2 non peggiora** su nessuno dei tre budget. Riferimento: 5 pieghe,
    1 incrocio, 600,0 mm, nodi condivisi col tronco 0, organi D-120 14 su 15.
14. **Determinismo**: doppia generazione dalla CLI con la stessa impronta, e forma
    invariante alla ridenominazione degli identificativi.
15. **Il saldo della suite migliora e non peggiora.** Nessuna prova convertita in `skip` o
    `xfail`, nessuna soglia allentata, nessuna fixture toccata per far passare una prova.
    Riferimento di partenza: 10 rosse, 1470 verdi, 24 saltate, 11 xfailed.
16. **Nessun impianto che compone all'inizio del pacchetto smette di comporre alla fine.**
    Il rapporto lo misura su tutti e cinque, con il comando e l'esito, prima e dopo. È il
    criterio che esiste perché l'impianto 4 non si perda una seconda volta.

---

## Consegna

Una PR sola, non fusa. Rapporto in `docs/collaudi/DRAW-010/RAPPORTO.md` con i sedici criteri
chiusi uno per uno; pacchetto grafico `prima/` e `dopo/` per l'impianto 4 e per la tavola 2,
con l'impianto 1 misurato come regressione. Il DEV apre la PR e si ferma; verifica e merge sono
del PM, che è una sessione diversa dal DEV.

---

## Decisioni che restano al PO

1. **L'ordine degli stacchi lungo il tronco** (rischio 17). La proprietà oggi vale per
   topologia su tutt'e due le tavole, non perché qualcuno la scelga. Diventa esigibile su un
   impianto che la violi: se l'impianto 4 o il 3 la violano, il PO dirà se aprirla.
2. **Lo squilibrio fra quadranti della tavola 2**, da 3,74 a 32,50. Nessun criterio lo copre
   e nessuna voce di costo lo insegue. Il PO ha visto la tavola e non l'ha sollevato: resta
   qui perché non si perda.
3. **Gli attacchi pari di un collettore**, ereditata da `DRAW-009` e non toccata.
