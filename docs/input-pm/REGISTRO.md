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
| I-005 | 2026-08-08 | **La composizione della tavola**: la centrale non si spezza mai in automatico, prima si ottimizza il foglio che c'è, la seconda tavola solo se la distribuzione la merita, il formato maggiore per ultimo e con motivazione verificabile | `2026-08-08-composizione-della-tavola.md`, registrato in **D-112** | **IN CORSO.** Tre impianti su cinque compongono; il quarto e il quinto no |
| I-006 | 2026-08-09 | **Architettura Drawing Director**: il validatore AI diventa supervisore attivo del disegnatore, in anello chiuso, con funzione di costo numerica scomposta in termini nominati | `2026-08-09-drawing-director.pdf`, registrato in **D-114** | **IN CORSO.** Ordine deciso da lui: prima le metriche dentro il motore deterministico, poi il direttore |
| I-007 | 2026-08-09 | **I tubi tornano indietro e fanno i giri** sulla prima tavola | Causa trovata: il collettore di ritorno è posato a sinistra delle macchine che alimenta, quindi il ritorno attraversa la tavola due volte. L'ordine dentro una fascia, sul ritorno, è deciso dall'ordine alfabetico del nome del pezzo | **APERTO** |
| I-008 | 2026-08-09 | **Distanza senza senso fra i gruppi**, «lì in mezzo ci entrava tutto senza fatica» | Causa trovata: quando avanza larghezza il collocatore la distribuisce fra i gruppi invece di compattarli. Riempimento misurato 35 % contro il 60 % richiesto | **APERTO** |

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
