# Collaudo della skill disegnatore-mep 1.6.0 — centrale termica villetta (T2)

Cartella di lavoro: `/tmp/claude-0/-home-user-DisegnatoreMEP/b6516f2f-ca66-5466-8ba2-b80294187e6d/scratchpad/collaudo2/t2/lavoro/`
(sotto: `$L`). Durata, dal primo comando alla consegna: circa 13 minuti. Ogni comando della skill
ha risposto in meno di un secondo.

## 1. File prodotti e numeri finali

**Due tavole, tutte e due escono.** Due perché la regola di comporre.md §«L'elettrico e il comando»
(righe 556-559) vuole la tavola a parte per l'elettrico su ogni centrale, e questa ha generatore
e accumuli. Il progettista aveva lasciato libera la scelta («sullo stesso disegno o su un altro»).

| tavola | formato | tratte | cedute | bloccanti | pieghe | sormonti | regole del piano che restano |
|---|---|---|---|---|---|---|---|
| idraulica | A2 | 36 | 0 | 0 | 9 | 2 | B9 ×1 (sonda di mandata pannelli), B11 ×1 (collettore-volano, interassi 10/15) |
| elettrico e comando | A3 | 11 | 0 | 0 | 10 | 1 | B9 ×1 (bus e alimentazione del regolatore a 2,5 mm) |

Tutte e due in **bozza**: committente, indirizzo, commessa e numero di tavola «DA DEFINIRE».
Il DXF supera `audit()` di ezdxf senza errori (339 e 115 entità).

File consegnati (`mep.py consegna`; `/mnt/user-data/outputs` non c'è, quindi cartella locale):
- `$L/consegna/centrale-termica-villetta-pdc-idraulica-t1.pdf` / `.dxf` / `.svg` / `-rilievi.md`
- `$L/consegna/centrale-termica-villetta-pdc-elettrico-t1.pdf` / `.dxf` / `.svg` / `-rilievi.md`
- (più `Cartiglio_NoveC_A3-logo.jpg`, copiato fra i consegnati senza motivo)

File di lavoro: `$L/grafo.json` (23 pezzi, 36 tubazioni, 15 reti, 19 assunzioni),
`$L/grafo-completo.json` (67 pezzi, +37 accessori), `$L/piano-idraulica.json`,
`$L/piano-elettrico.json`, `$L/vincoli.md` (tre giri), `$L/domande.md`, anteprime PNG e zoom in `$L/tavola/`.

Giri: idraulica 3 (A2 380 mm → posa stretta a 340 mm; il terzo giro non ha cambiato i numeri ed è
stato scartato, si tiene il secondo); elettrico 2 (il primo aveva 1 bloccante, la scritta «3G6» senza posto).

## 2. Dove la skill mi ha fatto inciampare

### 2.1 Istruzioni contraddittorie o ambigue

1. **L'elettrico, letto alla lettera, è tutto «tipo B».** In `capire.md` §5, righe 622-627 e 653-659,
   ci sono le due liste di mestieri (entra / non entra), e alle righe 706-707 c'è scritto: «Se il testo
   nomina un mestiere che non sta in nessuna delle due liste … trattalo come voce di catalogo mancante».
   `power_source` (quadro), `power_isolation` (sezionatore), `plant_control` (regolatore),
   `temperature_sensing` (sonde a immersione) e `outdoor_temperature_sensing` non stanno in nessuna
   delle due liste. Lo stesso file, §4.8 righe 585-587, dice invece che sonde e regolatore si
   trascrivono. Ho seguito §4.8. Un agente meno indulgente toglie l'elettrico intero. **Vanno aggiunti
   alla lista «entra» i mestieri dell'elettrico e del comando**, o almeno un rimando a §4.8.
2. **Come si collega una sonda a immersione non lo dice nessuno.** §5 righe 690-699 parla di pezzi
   «appesi» (sfiato, manometro, termometro) con `tee-branch` e di «attacco di servizio … `probe` di un
   volano». Che la sonda di mandata vada su un `tee-branch` con la tubazione dal braccio, e la sonda del
   bollitore su `bollitore.probe` (un attacco `stub`, che §4.3 riga 355 dice «Tu non ci colleghi
   niente»), l'ho dedotto io. La validazione l'ha accettato. Serve un esempio di una riga.
3. **«Collettore di distribuzione» → quale voce?** L'unico collettore con mandata e ritorno,
   `zone-manifold-pair`, è presentato fra le «voci per il costruito» come «collettore d'appartamento»
   (`capire.md` righe 634-640). L'ho usato per il collettore di centrale perché non c'è altro. Va detto
   che vale anche per il collettore di centrale.
4. **Gli attacchi del grafo decidono il disegno, e si scelgono prima di vedere la geometria.** Al
   passo 1 scegli quale uscita del quadro (`out_1`…`out_6`) e quale ingresso del regolatore
   (`probe_1`…`probe_3`) usa ciascun cavo. Dopo l'approvazione «il grafo non si tocca». Ma dove stanno
   quelle porte sul simbolo (out_1/out_2 sopra, out_3 a destra, out_4/out_5 sotto; regolatore con
   l'alimentazione sopra il bus) si scopre solo al passo 5, con `mep.py pezzi --vista elettrico`.
   La tabella delle porte di `comporre.md` §2.1 (righe 66-85) non ha né quadro, né regolatore, né le
   porte elettriche della PdC. Risultato: un incrocio bus/alimentazione del regolatore e la B9 che
   resta, che con un'altra scelta di uscite sparivano. **O `capire.md` dice come si scelgono le uscite,
   o le uscite di quadro e regolatore diventano intercambiabili per il motore.**
5. **I rilievi nominano «le tratte t11 e t12»**, e non c'è modo di trovarle sul foglio: `--verifica`
   stampa gli indirizzi dei pezzi (CS.03.N.06…), non gli id delle tratte. Le mie tubazioni si chiamavano
   anch'esse `t1`…`t36`, e all'inizio ho cercato t11/t12 fra le mie (era la coincidenza giusta solo per
   caso: ho sbagliato la prima ipotesi e ho perso un giro). Il rilievo deve nominare i due pezzi.
6. **«Elettrico: una tavola o due»: fra SKILL.md riga 231-235 e comporre.md righe 556-566 il criterio
   coincide**, ma SKILL.md dice «disposizione del PO» e comporre.md «proposta D-213». Una delle due è
   vecchia.
7. **`rivedere.md` riga 16 parla solo di «tavola di schema funzionale idronico».** Per la tavola
   dell'elettrico non c'è una riga su che cosa guardare (sigle dei pezzi comandati, cavi che arrivano
   alle porte, scritte dei cavi). È proprio dove la tavola ha i difetti peggiori (vedi §3).
8. **Il messaggio della legenda contraddice comporre.md.** Su A3:
   `Errore: the legend needs 237.5mm but its band is 235mm tall: 25 symbols and 5 networks (text is never shrunk to fit; split the plant across more sheets)`
   (uscita 1). Inglese, contro la promessa di SKILL.md riga 409-410 («il messaggio dice…»), e
   consiglia di dividere l'impianto su più fogli, mentre comporre.md D3 righe 521-523 dice di prendere il
   formato successivo. Per **2,5 mm** di legenda la tavola idraulica passa ad A2 con più di metà foglio
   vuoto. Anche il messaggio d'instradamento è in inglese («run t14-a on network secondario cannot be
   routed…»).
9. **B11 sul collettore.** `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` fra collettore e volano nasce dal
   simbolo (`zone-manifold-pair` ha `in`/`out` a 10 mm, il volano a 15). comporre.md B11 righe 444-452
   elenca i casi noti incurabili, cioè serpentina e terminale, e non il collettore. Chi non lo sa lo
   insegue.

### 2.2 Il catalogo e i simboli

10. **Il circolatore ha un solo attacco elettrico** (`power`). Il testo dice «alimentazione dei tre
    circolatori dal quadro» e «il regolatore comanda i due circolatori di zona»: le due cose non si
    possono scrivere insieme. Ho disegnato l'alimentazione dal quadro e dichiarato il comando come non
    rappresentabile. È il caso normale di una villetta (circolatore alimentato dal quadro e
    abilitato da un relè del regolatore). **Manca un attacco di comando sul circolatore**, o una
    regola che dica che l'alimentazione passa per l'uscita del regolatore.
11. **Il bus Modbus non ha scritta.** Il protocollo non ha un campo. Rimangono due strade: `scritta`,
    che è riservata al testo voluto dal progettista, oppure niente. L'ho messo in `properties.protocollo`,
    e sulla tavola non compare.
12. Non mancava nessuna voce principale: PdC monoblocco, volano a 4 attacchi, bollitore a serpentino,
    deviatrice, miscelatrice motorizzata, collettore, ricircolo, quadro, sezionatore, regolatore, sonde:
    c'erano tutte, e `valida` è passato al primo colpo.

### 2.3 Comandi

Nessun comando ha dato errore inatteso. Uscite non zero, tutte attese:
- `disegna` idraulica su A3, primo giro → 2, «Il piano non si instrada … Probabile causa: la posa
  (380 x 167.5 mm) non sta nell'area dell'A3 (350 x 235)». Diagnosi giusta.
- `disegna` idraulica su A3 con la posa stretta a 340 mm → 1, la legenda (punto 8).
- `disegna` elettrico, primo giro → 2, `RUN_LABEL_OMITTED` su «3G6» (cavo quadro-PdC troppo corto). Si
  è curato allungando il cavo.

### 2.4 Dati che non sapevo dove mettere nel grafo

- «all'esterno», «monoblocco», «motorizzata», «circolatore diretto»: sono finiti in `properties` come
  parole, e sulla tavola non compare niente. Sulla PdC la scritta «esterno» sarebbe utile.
- La **lunghezza 15 m** e la sezione 3G6 di una linea spezzata dal sezionatore. capire.md righe 596-598
  dice che la lunghezza va su una sola delle due tubazioni. Della **sezione** non dice niente. L'ho
  messa su tutte e due, e la tavola scrive «3G6» due volte (vedi §3).
- La logica (curva climatica, priorità ACS, Modbus) va in un'assunzione, come vuole capire.md §4.5.
  Sulla tavola non c'è una nota che la porti.

## 3. Quello che ho visto sulle tavole e che i numeri non dicono

Per primi, i difetti con zero rilievi:

1. **Elettrico: miscelatrice, deviatrice e le due sonde a immersione non hanno sigla.** Sulla tavola
   dell'elettrico ci sono due valvole a tre vie quasi identiche e due sonde identiche, senza nome.
   Non si capisce quale cavo comanda la miscelatrice e quale la deviatrice, né quale sonda è la mandata
   pannelli e quale il bollitore. Hanno la sigla solo GT, QE, RG, SE, SZ, CIR. La tavola dell'elettrico
   così **non si legge**, e il rimando «Vedi la tavola idraulica» non aiuta: sulla tavola idraulica le
   stesse quattro sono senza sigla anche lì. I numeri sono puliti (0 bloccanti), e il difetto è il più grave.
2. **Elettrico: i cavi non toccano la PdC.** Fra il fondo del simbolo della pompa di calore e l'inizio del
   cavo di alimentazione c'è un vuoto di circa 4 mm (zoom a 600 dpi, `$L/tavola/z-el3.png`), e lo stesso
   per il bus. Sui lati destri del simbolo restano invece disegnati i due mozziconi degli attacchi
   dell'acqua, che sulla tavola dell'elettrico non servono.
3. **Idraulica: i confini di rete non hanno scritta.** Acquedotto, utenze ACS, ricircolo «ACS-R»,
   ingresso acqua fredda del riempimento e della miscelatrice termostatica sono cinque frecce nere senza
   testo. Si distinguono solo per il colore della linea. capire.md riga 369 dice che il ricircolo «si
   legge ACS-R»: sulla tavola non c'è.
4. **Tabella delle apparecchiature: «Pompa di circolazione nr 1» e «nr 2».** Non dice quale zona
   servono (pannelli, radiatori). Anche il collettore non ha sigla.
5. **Elettrico: le scritte della linea della PdC.** La linea porta «3G6 · L 15 m» lungo il cavo e un
   secondo «3G6» con richiamo. Il richiamo del secondo «3G6» converge sullo stesso punto del richiamo di
   «SZ-01»: due frecce sullo stesso sezionatore, ed è facile leggere «3G6» come sigla del sezionatore.
6. **Idraulica: il collettore di ritorno è disegnato come tre barrette staccate** (una per `out`, una
   per `ret_1`, una per `ret_2`): sembrano tre pezzi distinti, non un collettore.
7. **Idraulica: l'attacco sonda libero del volano** (lato sinistro, in basso) esce come un mozzicone di
   tubo aperto.
8. **Cartiglio: «TITOLO TAVOLA: Idraulica» / «Elettrico e comando».** Con il titolo mancante il cartiglio
   non scrive «DA DEFINIRE» ma il solo suffisso, e senza numero di tavola il «-E» del rimando non esce.
   Fra le caselle da definire risulta solo «TAVOLA».
9. **Legenda: la riga «Vedi»** ha «Vedi» nella colonna dei simboli e il testo nella colonna delle
   descrizioni: si legge male.
10. **Formato:** l'A2 idraulico è pieno per meno di metà, per 2,5 mm di legenda (punto 8 di §2.1).
11. **Rilievi consegnati al progettista** (`*-rilievi.md`): sono pieni di codici, id interni e numeri di
    decisione (`t11`, `D-062`, `B9`). SKILL.md righe 388-390 dice di non dare codici, poi riga 371 li fa
    consegnare.

Il resto si legge bene. Primario dritto dalla PdC al volano (mandata e ritorno alla stessa quota). Il
corredo del ritorno è appeso in basso e ordinato. La deviatrice sta sulla mandata con la terza via che
scende al serpentino, e scavalca il ritorno con un salto imposto. Il ricircolo è verde e rientra dal suo
attacco. La miscelatrice dei pannelli ha il bypass dal ritorno. Ci sono le frecce di flusso e i colori
per rete.

## 4. Le domande che avrei fatto al progettista

(per intero in `$L/domande.md`)
1. Circolatori di zona: alimentati dal quadro (com'è disegnato, e allora il comando del regolatore non si
   vede) o attraverso le uscite del regolatore?
2. Un quadro solo («di centrale») o due («dal quadro» per la PdC)?
3. Zona pannelli: miscelatrice → circolatore → sonda di mandata, con il bypass dal ritorno. Va bene?
4. Il regolatore si alimenta dal quadro di centrale?
5. Ritorni volano e serpentino uniti con un T prima della PdC?
6. Circolatore del primario a bordo della monoblocco?
7. Vaso di espansione sanitario: il bollitore lo ha a bordo? (punto aperto di `completa`)
8. Il corredo che le regole posano: miscelatrice termostatica sull'uscita ACS, filtro a Y sul ritorno
   della PdC (la monoblocco lo ha già?). Mancano intercettazioni direttamente sugli attacchi della PdC
   esterna e giunti antivibranti: li vuole?
9. Dati: committente, commessa, indirizzo, titolo e numero tavola; marca/modello di volano, bollitore e
   circolatori; portata e prevalenza dei circolatori; sezioni e lunghezze delle altre linee e del bus.
10. Pianta dei tracciati: no (prima interpretazione).

## 5. Giudizio

**Per l'idraulica sì, per l'elettrico no.** La tavola idraulica di questo tipo di impianto esce in
13 minuti, pulita, in bozza, e un ingegnere la può mettere in un'offerta dopo un'occhiata. Le
correzioni sono scritte sui confini e sulle sigle dei circolatori.

La tavola dell'elettrico e comando, che il progettista ha chiesto esplicitamente, **non è consegnabile
come lettura autonoma**. La fermano:
1. le sigle mancanti su valvole a tre vie e sonde a immersione (§3.1), su tutte e due le tavole. È il
   correttivo più urgente, ed è nel motore, non nel piano;
2. i cavi che non toccano la pompa di calore (§3.2);
3. il circolatore senza un attacco di comando (§2.2.10): il caso più comune di regolazione di una
   villetta non si può disegnare come il progettista lo descrive;
4. la contraddizione `capire.md` §5 / §4.8 (§2.1.1): un agente che la legge alla lettera toglie tutto
   l'elettrico.

Da sistemare subito dopo: messaggi in inglese con consigli contrari a comporre.md, la legenda che
forza l'A2 per 2,5 mm, i rilievi che nominano tratte introvabili, le porte di quadro e regolatore
assenti dalla tabella di comporre.md.
