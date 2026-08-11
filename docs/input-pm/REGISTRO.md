# Registro degli input del PM

> **Questo file esiste perché un suo input si è perso, e non era la prima volta.**
>
> Il 5 agosto 2026 il PM ha indicato le tavole della simbologia italiana come «la
> simbologia giusta». Da quella fonte sono state ricavate tre osservazioni; una sola è
> stata chiusa. La valvola di ritegno è rimasta sbagliata per quattro giorni, è arrivata
> fino alla prima tavola che lui ha visto, e quando gliel'ha fatto notare la sua frase è
> stata: **«mi avevi detto in una sessione che avevi capito l'errore ed è morto lì. Si
> continuano a perdere i miei input.»**
>
> Aveva ragione, e la causa non è la memoria: è che **non c'era nessun posto in cui un
> suo input restasse scritto finché non veniva chiuso.** Le decisioni avevano il loro
> registro, i difetti avevano le loro prove marcate rosse, le fonti avevano il proprio
> elenco — ma ciò che il PM chiede viveva nella conversazione, e la conversazione finisce.

---

## La regola, che è vincolante

1. **Ogni cosa che il PM porta prende una riga qui, il giorno stesso.** Vale per un
   documento, un link, una correzione su una tavola, una frase in chat. Anche se sembra
   piccola. Anche se si pensa di chiuderla in cinque minuti.
2. **Una riga esce solo in due modi:** *chiusa* — e allora dice **cosa** l'ha chiusa, in
   modo che lui possa verificarlo — oppure *ritirata da lui*. Non esiste «superata dai
   fatti» senza che lui lo sappia.
3. **Un input che genera più cose da fare si spezza in più righe.** È l'errore del
   5 agosto: una fonte sola conteneva tre osservazioni, se n'è chiusa una, e le altre due
   sono sparite insieme alla prima perché sembravano la stessa cosa.
4. **I documenti che consegna si copiano qui accanto**, non restano allegati di una
   conversazione. In questa cartella, con la data nel nome.
5. **Chi apre una sessione legge questo file** subito dopo l'handoff. Le righe aperte
   sono lavoro, non archivio.

---

## Righe aperte

| # | Data | Cosa ha chiesto o dato | Dove vive | Stato |
|---|---|---|---|---|
| I-002 | 2026-08-05 | **Gli spessori di tratto sono normati**: tubazione di progetto 0,50 mm, tubazione esistente 0,25 mm, e tutti i segni grafici tracciati a 0,50 mm salvo diversa descrizione. Ricavato dalla tavola delle tubazioni della fonte che ha indicato lui | Oggi la tavola usa 0,18 / 0,35 / 0,50 scelti internamente, e disegna tubazioni e simboli a 0,35 | **APERTO da 4 giorni.** Nessuno l'ha mai preso in carico |
| I-005 | 2026-08-08 | **La composizione della tavola**: la centrale non si spezza mai in automatico, prima si ottimizza il foglio che c'è, la seconda tavola solo se la distribuzione la merita, il formato maggiore per ultimo e con motivazione verificabile | `2026-08-08-composizione-della-tavola.md`, registrato in **D-112** | **IN CORSO.** Tre impianti su cinque compongono; il quarto e il quinto no — ma **dal 10 agosto si guarda il solo impianto 1** (I-012), quindi il quarto e il quinto non sono più il metro di questa riga |
| I-006 | 2026-08-09 | **Architettura Drawing Director**: il validatore AI diventa supervisore attivo del disegnatore, in anello chiuso, con funzione di costo numerica scomposta in termini nominati | `2026-08-09-drawing-director.pdf`, registrato in **D-114** | **IN CORSO.** Ordine deciso da lui: prima le metriche dentro il motore deterministico, poi il direttore |
| I-007 | 2026-08-09 | **I tubi tornano indietro e fanno i giri** sulla prima tavola | Causa trovata: il collettore di ritorno è posato a sinistra delle macchine che alimenta, quindi il ritorno attraversa la tavola due volte. L'ordine dentro una fascia, sul ritorno, è deciso dall'ordine alfabetico del nome del pezzo | **QUASI CHIUSA (10 agosto).** La causa è stata tolta con D-118: sull'impianto 1 la confluenza dei ritorni non sta più a sinistra delle pompe, e le tratte con troppe pieghe passano da otto a due. Resta aperta perché **due tratte ne fanno ancora quattro** e gli incroci sono saliti da 11 a 13. Una prova marcata rossa presidia il caso del quinto impianto |
| I-009 | 2026-08-09 | **«Dal ramo freddo si stacca un ramo caldo. È un errore nel grafo o del disegnatore?»** e «anche gli altri disegni sono senza senso» | **Risposta: il grafo è pulito, l'errore era del disegnatore.** Nel modello solo il bollitore tocca più di un fluido, ed è giusto. Il disegnatore però prendeva come **sorgente della rete di acqua fredda il bollitore** invece dell'acquedotto — perché pesava il mestiere («tiene una riserva») più del fatto che un confine di rete immette e basta — e disegnava **tutta l'adduzione come un ritorno**, con colore e tratteggio del ritorno. Sui cinque impianti non esisteva **una sola** tratta di acqua fredda in andata | **CHIUSO nel merito, APERTO nel prezzo.** La sorgente ora è chi immette e non riceve. Ma correggere il verso cambia l'ordine con cui il collocatore legge il processo, e due impianti su tre hanno smesso di entrare nel foglio: il terzo chiede 420 mm contro 335. Prova marcata rossa apposta |
| I-010 | 2026-08-09 | Conseguenza dello stesso controllo, **non segnalata da lui**: su un terzo delle tratte il verso mandata/ritorno resta **indeciso** e lo decide la geometria del disegno — cioè il colore dipende da dove il pezzo è finito sul foglio | È il difetto che il modulo del verso esiste per togliere, e non è chiuso: la camminata si ferma sugli utilizzatori e non riattacca il ritorno che ne esce | **APERTO** |
| I-008 | 2026-08-09 | **Distanza senza senso fra i gruppi**, «lì in mezzo ci entrava tutto senza fatica» | Causa trovata: quando avanza larghezza il collocatore la distribuisce fra i gruppi invece di compattarli. Riempimento misurato 35 % contro il 60 % richiesto | **APERTO** |
| I-011 | 2026-08-08 | **Le colonne valgono solo per le macchine principali.** Aveva notato che il disegnatore metteva gli accessori di una macchina nella stessa colonna della macchina; la sua correzione è che le colonne servono **solo a disporre i pezzi grossi**, per usare bene anche l'altezza, e che gli accessori in mezzo possono stare dove capita. Registrato in ritardo, il 10 agosto: ⚠ **è la riga che dimostra che il registro serve** — l'input esisteva, era stato registrato e implementato sulla linea di lavoro dell'8 agosto, e da qui non si vedeva | Riportata sul tronco e attuata il 10 agosto, registrata in **D-118** | **CHIUSA.** I raccordi non prendono più una colonna a testa e si posano sulla tratta che unisce i pezzi grossi; ciò che sta in parallelo si impila sempre. Sull'impianto 1: larghezza da 330 a 253 mm, rilievi da 12 a 6, tratte con troppe pieghe da 8 a 2, e **la confluenza dei ritorni non sta più a sinistra delle pompe** — che era la causa di I-007. Prezzo misurato: incroci da 11 a 13, riempimento da 35 % a 27 % |
| I-012 | 2026-08-10 | **Si lavora su una tavola sola: l'impianto 1.** Le altre quattro si fanno solo dopo che lui ha approvato la prima, e servono a scoprire errori **nuovi**. Motivo suo: «non ha senso sprecare token per vedere 5 tavole dove verosimilmente gli stessi errori si ripetono» | Restringe il campo di ogni giro di lavoro e di ogni consegna. Registrato in **D-116** | **APERTO** — vale da adesso |
| I-014 | 2026-08-10 | **Ogni sessione finisce su `main`**: si spinge su GitHub e si fa merge, sempre, risolvendo i conflitti. «Non deve più accadere che ci siano più rami con pezzi di sviluppo» | Registrato in **D-117** e scritto fra le regole operative, che è il file che una sessione nuova legge per forza. **Vale da subito**: questa sessione si è chiusa su `main` | **APERTO come regola permanente.** L'unico debito che resta fuori è la linea dell'8 agosto, nominata nello stato: va riportata e fusa, non lasciata dov'è |
| I-013 | 2026-08-10 | **Le tavole prodotte finora sono da buttare** — «facevano schifo, erano quelle con i tubi che tornano indietro» — e la priorità è **portare avanti lo sviluppo sui suoi input**, non rifinire quelle tavole | Non apre un difetto nuovo: conferma che I-007, I-008 e I-010 sono la strada, e dice di non spendere tempo altrove finché non sono chiusi | **APERTO** — è il criterio con cui si sceglie cosa fare |

## Righe chiuse

| # | Data | Cosa ha chiesto o dato | Cosa l'ha chiusa |
|---|---|---|---|
| I-001 | 2026-08-05 | **La simbologia giusta è quella delle tavole UNI 9511 pubblicate da Oppo**, scaricabili anche in DWG | Acquisita come SRC-016 e letta il 5 agosto. ⚠ **Da sola questa riga non bastava**: conteneva tre osservazioni, ed è per questo che le righe I-002, I-003 e I-004 esistono separate |
| I-003 | 2026-08-05 | **Incrocio con connessione e derivazione portano un pallino** di diametro pari a quattro volte lo spessore del tratto | D-079: il pallino si disegna, con quel diametro, citando la fonte |
| I-004 | 2026-08-05 | **La valvola di ritegno è sbagliata.** Ribadito il 9 agosto: «basta cercarla su Oppo o Caleffi, vedrai che è una sorta di z di fianco con freccia sopra» | **9 agosto**: tavola del valvolame riletta sull'immagine pubblicata, non a memoria. Il segno è **due barrette verticali unite da una diagonale** dall'alto della prima al basso della seconda — la z coricata — **con la freccia del senso del flusso sopra**, e la norma lo dice testualmente. Il simbolo è stato rifatto. La lettura precedente, registrata come «triangolo vuoto contro la battuta», era **sbagliata**: qualcuno aveva descritto il segno invece di guardarlo |

---

## Cosa insegna il caso della valvola di ritegno

Tre errori distinti, e vale la pena tenerli separati perché si ripetono in modo diverso.

1. **Una fonte è stata letta descrivendola a parole invece di guardarla.** La tavola è
   un'immagine pubblicata: scaricarla e guardarla costa un minuto. La descrizione
   registrata quel giorno — «triangolo vuoto contro la battuta» — non somiglia al segno
   vero.
2. **Un difetto riconosciuto non è un difetto chiuso.** La nota diceva «la nostra ha il
   triangolo pieno e nessuna freccia»: qualcuno l'aveva visto. È stata aggiunta la
   freccia e il triangolo è rimasto. Mezza correzione somiglia moltissimo a una
   correzione fatta.
3. **Il difetto viveva in un file che nessun elenco di lavoro nominava.** Non era una
   prova marcata rossa, non era un punto aperto, non era una riga di stato. Era una frase
   dentro un registro di fonti, e i registri di fonti si leggono quando si cerca una
   fonte.
