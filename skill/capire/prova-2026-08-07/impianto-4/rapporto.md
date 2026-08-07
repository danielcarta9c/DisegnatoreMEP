# Rapporto di lavorazione — Esempio 4, sistema ibrido pompa di calore + caldaia combinata

Committente: Nove C · Codice di commessa: PROVA · Revisione 00 · Data 2026-08-07
Consegna: `consegna/grafo.json` (validato), `consegna/rilettura.md`, questo rapporto.

---

## 1. Che impianto ho capito

Un impianto ibrido con **due generatori in parallelo** — una pompa di calore aria-acqua
da 10 kW e una caldaia a condensazione da 24 kW — che alimentano insieme un **volume
tecnico da 150 litri a quattro attacchi**. Dal volume parte un **circuito secondario**
con circolatore dedicato che serve l'impianto esistente **a radiatori**. Il volume, con
i suoi quattro attacchi, tiene separati i due circuiti: il primario dei generatori e il
secondario di riscaldamento.

L'**acqua calda sanitaria** è prodotta dalla sola caldaia, in modo istantaneo e senza
accumulo: quando c'è richiesta, una **valvola deviatrice a tre vie** sul ramo della
caldaia manda l'acqua di caldaia al **primario di uno scambiatore a piastre** invece che
al volume; sul secondario dello scambiatore passa l'acqua fredda di acquedotto, che esce
calda verso le utenze. Il sanitario è quindi un circuito **aperto** (acquedotto →
scambiatore → utenze), mentre riscaldamento e primario sono **chiusi**.

Il resto del testo è **regolazione**, non topologia: la pompa di calore come generatore
principale, la caldaia che interviene al freddo o quando serve più potenza o una mandata
più calda, la priorità sanitaria della caldaia mentre la pompa di calore continua a
caricare il volume.

**Quattro cose in chiaro** (il controllo finale delle istruzioni, §9):

- **Che macchina è ciascun pezzo.** Pompa di calore e caldaia producono solo calore
  (`heat_generation`); nessuna delle due produce il sanitario **da sola** nel grafo,
  perché il testo descrive come lo produce: valvola deviatrice + scambiatore esterno. Il
  volume tecnico separa e accumula acqua di riscaldamento (`hydraulic_separation` +
  `thermal_storage`, `stored_medium: heating_water`); **nessun serbatoio di acqua
  sanitaria** esiste in questo impianto, ed è il testo a escluderlo.
- **Che acqua porta ogni circuito.** `primario` e `secondario` acqua di riscaldamento;
  `acqua-fredda` acqua fredda sanitaria dall'acquedotto allo scambiatore; `acs` acqua
  calda sanitaria dallo scambiatore alle utenze. **Il sanitario c'è**, ed è istantaneo.
- **Il regime della centrale.** Ricavato: 10 + 24 = **34 kW ≤ 35** → `up_to_35_kw`.
- **Come i circuiti toccano il serbatoio.** Il volume tecnico non ha serpentini e non ha
  riserva sanitaria: primario e secondario **attraversano** lo stesso volume d'acqua di
  riscaldamento attraverso due coppie di attacchi (`primary_in`/`primary_out`,
  `secondary_out`/`secondary_in`). Nessun circuito «riempie una riserva»: l'unico
  riempimento nominato dal testo è il carico automatico da acquedotto, che è ferramenta
  e non entra qui.

Numeri della consegna: 4 reti, 12 componenti, 15 tubazioni, 11 assunzioni.
`subsystems`, `rule_applications`, `sheets` sono liste vuote. Nessun `tag`: l'ingegnere
non ne ha scritti.

---

## 2. Elenco in chiaro delle domande e delle assunzioni

Tutte sono nel JSON con `status: "proposed"`. Qui in ordine, con l'id corrispondente.

1. **a1 — Con che pezzo si fa il parallelo?** Il testo dice «collegate in parallelo» e
   che i due generatori alimentano il volume, ma non dice con quale pezzo i flussi si
   uniscono e si dividono. *Assunto:* un raccordo a T sulla mandata (le due mandate
   confluiscono) e una ripartizione a T sul ritorno (il ritorno si divide fra i due
   generatori). *Domanda:* va bene così, o c'è un collettore/separatore che il testo non
   ha nominato?
2. **a2 — Dove sta la valvola deviatrice e dove rientra il ritorno dello scambiatore?**
   Il testo dice che la valvola «devia il circuito della caldaia verso lo scambiatore»,
   ma non dice il punto. *Assunto:* valvola sulla **mandata della caldaia**, a valle del
   generatore e **prima** del raccordo con la pompa di calore (così la pompa di calore
   può continuare ad alimentare il volume, come dice l'ultima frase); ritorno del
   primario dello scambiatore che **rientra sul ritorno della caldaia** attraverso una
   confluenza a T, perché un attacco porta una tubazione sola. *Domanda:* è questo il
   punto di rientro?
3. **a3 — Su quale ramo sta il circolatore del secondario?** Il testo lo nomina come
   pezzo a sé ma non dice dove. *Assunto:* sulla **mandata** che parte dal volume, per
   convenzione di disegno. *Domanda:* è così, o sta sul ritorno?
4. **a4 — La caldaia ha il circolatore a bordo?** Sul primario il testo non nomina
   circolatori. La voce di catalogo della pompa di calore dichiara di portarlo a bordo;
   per la caldaia il catalogo non dichiara niente. *Assunto:* nessun circolatore
   disegnato sul primario. *Domanda:* la caldaia ce l'ha a bordo, o ne serve uno esterno
   sul suo ramo?
5. **a5 — Quanti sono i radiatori?** «L'impianto esistente a radiatori» non dice numero
   né ramificazione. *Assunto:* un solo terminale rappresentativo. *Domanda:* quanti
   corpi scaldanti, e su quanti rami?
6. **a6 — Carico automatico e scarico sul volume tecnico.** Il testo li prevede, ma sono
   ferramenta di servizio (gruppo di riempimento, attacco di scarico): li aggiunge il
   pezzo successivo della catena. *Registrato perché non vada perso*, insieme al fatto
   che gli attacchi di servizio del volume (sfiato, scarico, sonda) sono stati lasciati
   liberi apposta.
7. **a7 — La regolazione non si vede sul grafo.** Pompa di calore principale, caldaia in
   intervento al freddo / a maggiore richiesta / a mandata più alta, priorità sanitaria
   della caldaia, pompa di calore che continua sul volume. Sul grafo si vedono la
   valvola deviatrice e i due generatori in parallelo, non la priorità né la logica di
   intervento.
8. **a8 — Esclusioni dichiarate dal testo.** «Senza bollitore di accumulo»: nessun
   accumulo sanitario è disegnato **perché il testo lo esclude**, non perché sia stato
   perso. Il testo non nomina un ricircolo sanitario: non è disegnato.
9. **a9 — «Caldaia combinata»: aggettivo contro descrizione.** L'aggettivo direbbe una
   macchina che fa anche il sanitario da sola; la descrizione dice come lo fa (valvola a
   tre vie + scambiatore a piastre esterno). *Assunto:* comanda la descrizione, quindi
   voce di catalogo della caldaia base e i due pezzi disegnati. *Domanda:* se invece il
   sanitario è prodotto **dentro** la caldaia, quei due pezzi non vanno e il disegno
   cambia.
10. **a10 — Come è stato ricavato il regime.** 10 kW + 24 kW = 34 kW ≤ 35 →
    `up_to_35_kw`. *Nota:* la somma sta a **un solo kW** dalla soglia; se una delle due
    potenze scritte fosse resa o assorbita invece che al focolare, il regime potrebbe
    cambiare.
11. **a11 — Il ramo sanitario del primario resta nella rete del primario.** Porta la
    stessa acqua di riscaldamento e nasce dalla stessa macchina che lo alimenta (la
    caldaia). Il sanitario vero comincia **dopo** lo scambiatore: prima acqua fredda,
    dopo acqua calda sanitaria, due reti distinte.

**Domande da portare all'ingegnere prima del disegno definitivo** (quelle in cui due
letture ragionevoli darebbero **due grafi diversi**): **a9** (la caldaia produce il
sanitario da sola o attraverso lo scambiatore esterno descritto?) e, in seconda battuta,
**a1** e **a2** (il pezzo con cui si fa il parallelo, e il punto di rientro del ritorno
dello scambiatore). Tutte le altre sono chiusure convenzionali dichiarate: cambiano un
dettaglio, non l'impianto.

---

## 3. Dove le istruzioni non mi hanno dato un criterio

Questo è il punto della prova. Elenco i casi in cui ho dovuto decidere senza che le
istruzioni dicessero come, o in cui dicevano due cose che tiravano in direzioni diverse.

1. **Un ramo che nasce da una valvola deviatrice: rete nuova o stessa rete?**
   §4.2 dice che una rete parte da una macchina che la alimenta o da un confine, **mai
   da un raccordo**, e che i rami di una ripartizione restano nella rete in cui nascono.
   Ma una valvola deviatrice **non è un raccordo** (è `diversion`, sta nella lista di ciò
   che entra nel grafo) e **non alimenta** niente. Il ramo caldaia → scambiatore è un
   circuito che il testo distingue («il circuito della caldaia» verso lo scambiatore),
   con lo stesso fluido e la stessa macchina alimentante. Le istruzioni non coprono il
   caso. Ho scelto di tenerlo dentro `primario` e l'ho dichiarato (a11).

2. **Due reti con lo stesso fluido: quando è obbligatorio separarle?**
   §4.2 porta come esempio «il circuito secondario che parte da un accumulo», ma il
   criterio operativo che enuncia subito dopo è quello del fluido («dove il fluido cambia,
   la rete cambia»). Primario e secondario qui hanno **lo stesso fluido**: nulla nelle
   istruzioni *impone* di separarli, e un lettore ragionevole potrebbe fare una sola rete
   di acqua di riscaldamento. Ho seguito l'esempio testuale del §4.2 e ne ho fatte due.
   Il criterio manca: sarebbe utile dire esplicitamente che una macchina con
   `hydraulic_separation` separa anche le reti.

3. **Che potenze si sommano per il regime — e un contrasto con lo schema.**
   §4.6 dice «somma le potenze delle macchine che **generano calore**»: letteralmente,
   10 + 24 = 34 kW. Ma la descrizione del campo `plant_regime` nello schema motiva la
   soglia con la Raccolta R, che si applica «agli impianti con potenza **dei focolari**
   superiore a 35 kW»: letta così, la pompa di calore non ha focolare e conterebbe solo
   la caldaia (24 kW). Qui il risultato **non cambia** (in entrambi i casi `up_to_35_kw`),
   ma il criterio è genuinamente doppio e su un altro impianto cambierebbe il regime, e
   con lui le regole del pezzo successivo. Ho seguito §4.6, che è il testo che mi
   governa, e ho dichiarato il conto (a10). Aggravante: la somma cade a **1 kW** dalla
   soglia, cioè nel punto in cui l'ambiguità pesa di più.

4. **La «derivazione» del §4.4 non è collegabile.**
   §4.4 distingue i raccordi (confluenza / ripartizione) dalle **derivazioni**, «il pezzo
   con un braccio che esce dal percorso», da usare «solo dove il testo descrive qualcosa
   che si stacca da un tubo». Ma nel catalogo le voci `tee-branch*` hanno la porta
   `branch` marcata `stub: true`, e §4.3 vieta di collegare qualsiasi cosa a uno stub:
   quel braccio non può portare una tubazione. In pratica ogni ramo reale deve essere una
   `tee-split`, e la distinzione del §4.4 non è applicabile. Qui non mi ha danneggiato
   (non ne ho usate), ma è una contraddizione fra istruzioni e catalogo.

5. **`carries_on_board` non è spiegato da nessuna parte.**
   La voce della pompa di calore dichiara `carries_on_board: ["circulation"]`. Le
   istruzioni non nominano mai questo campo: l'unico appiglio è l'esempio del §6 tipo A
   («si è seguita la macchina di catalogo, che lo porta a bordo»). Ho dedotto che
   significa «il circolatore è dentro la macchina, non si disegna» e l'ho dichiarato
   (a4). È una deduzione mia sul significato di un campo, non una regola letta.

6. **Manca in catalogo la caldaia combinata, e §4.1 dice due cose in successione.**
   §4.1 prima dice che un aggettivo che aggiunge un mestiere cambia la voce e invita a
   cercare «una voce che dichiari entrambi i mestieri»; poi dice che se il testo descrive
   **come** si produce il sanitario, comanda la descrizione. Nel catalogo una caldaia che
   produce il sanitario da sola **non esiste** (l'unica voce con `heat_generation` +
   sanitario è `dhw-heat-pump`, che è un boiler in pompa di calore, macchina diversa):
   quindi la prima strada era comunque chiusa e avrebbe prodotto un buco di tipo B. La
   seconda regola mi ha salvato, ma solo perché questo testo descrive lo scambiatore. Se
   avesse detto soltanto «caldaia combinata», non avrei avuto niente da scegliere.

7. **Dove sta una valvola deviatrice, quando il testo non lo dice.**
   Le istruzioni danno la convenzione per il **circolatore** (§7: sulla mandata) ma non
   ne danno nessuna per la valvola deviatrice né per il punto in cui il ritorno di un
   ramo deviato rientra. Ho scelto mandata + confluenza sul ritorno della caldaia,
   appoggiandomi all'ultima frase del testo (la pompa di calore continua ad alimentare il
   volume: quindi la deviazione è sul solo ramo caldaia) e l'ho dichiarato (a2). Il
   criterio l'ho costruito io dal testo, non l'ho trovato nelle istruzioni.

8. **`metadata.project_name` non è definito.**
   Le istruzioni spiegano `project_id`, `client`, `commission_code`, `revision`,
   `issue_date`, ma non dicono che cosa scrivere in `project_name`. Ho usato il titolo
   che il testo si dà.

9. **Nessun criterio sulla granularità delle assunzioni.**
   Le istruzioni chiedono di dichiarare tutto, ma non dicono se una nomina di ferramenta
   e una domanda di topologia vadano in voci separate o accorpate. Ne ho fatte 11,
   una per argomento. È una scelta mia.

10. **Nessuna istruzione su cosa fare quando un dato del catalogo aggiunge un fatto che
    il testo non dice.** Il testo dice «volume tecnico a quattro tubi»; la voce di
    catalogo `buffer-four-port` dichiara anche `hydraulic_separation`. Il grafo, così,
    afferma una separazione idraulica che il testo non nomina in modo esplicito. Non era
    evitabile (era l'unica voce con quattro attacchi di flusso) e non l'ho considerata
    un'invenzione, ma è un caso in cui **la scelta di catalogo aggiunge informazione**, e
    le istruzioni non dicono se vada dichiarato. Lo dico qui.

---

## 4. Controllo finale (§9) e verifiche eseguite

- Il JSON **carica** con lo strumento di validazione: comando eseguito dalla radice del
  repository, nessun output, ripetuto dopo l'ultima modifica. ✔
- Ogni `definition_id` esiste nel catalogo; **nessuno** ha un mestiere della lista
  ferramenta. ✔ (verificato con uno script sul catalogo della cartella di lavoro)
- Ogni attacco usato esiste; **nessun attacco porta due tubazioni**; **nessuna tubazione
  tocca uno stub** (gli stub di sfiato/scarico/sonda del volume restano liberi). ✔
- Ogni tubazione va da una porta `out` a una porta `in`, con fluido e dominio uguali a
  quelli della rete a cui appartiene. ✔
- Tutti gli attacchi `required: true` risultano collegati: nessun collegamento descritto
  è andato perso. ✔
- Tutti i `tag` sono `null` (l'ingegnere non ha scritto sigle). ✔
- Ogni componente e ogni tubazione compare nella tabella di rilettura, agganciato a una
  frase. ✔
- `subsystems`, `rule_applications`, `sheets` sono liste vuote. ✔

---

## 5. Isolamento

Non ho aperto, letto, cercato, elencato né ispezionato alcun file fuori dalla cartella di
lavoro. Ho letto soltanto: `ISTRUZIONI.md`, `testo-del-committente.txt`, i 53 file di
`examples/layout/catalog/`, `naming/families.json`, `naming/media.json`,
`schemas/project.schema.json`, tutti dentro la cartella.

Due precisazioni, per trasparenza:

- Ho **eseguito** il comando di validazione dalla radice del repository, come l'eccezione
  prevede. Non ho letto nulla del repository: il comando ha stampato solo la riga di
  conferma che ho aggiunto io (`OK-CARICA`).
- Il dump del catalogo era troppo grande per la finestra e l'ambiente lo ha salvato
  automaticamente in un file di appoggio, che ho poi riletto. Quel file conteneva
  **esclusivamente** l'output del mio stesso comando sui 53 file della mia cartella:
  nessun contenuto del repository. Ho scritto anche uno script di verifica nella
  scratchpad di sessione, che legge solo la mia cartella di lavoro.

Nessuna infrazione da dichiarare.
