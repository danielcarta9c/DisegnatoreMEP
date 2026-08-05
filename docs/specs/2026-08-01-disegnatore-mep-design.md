# Specifica di design - Disegnatore MEP

**Data:** 1 agosto 2026

**Stato:** approvata dal PM il 1 agosto 2026

**Versione:** 0.1

## 1. Sintesi

Disegnatore MEP è una skill che trasforma un impianto termotecnico già discusso, progettato e dimensionato dall'ingegnere in uno schema tecnico-esecutivo vettoriale.

La skill non è un catalogo di schemi tipo e non sostituisce il progettista. L'intelligenza del modello interpreta il contesto della conversazione e ricostruisce l'impianto; un nucleo software deterministico normalizza la topologia, applica le regole approvate, dispone i componenti, instrada le reti, controlla la geometria e genera SVG/PDF.

Il risultato deve avere la disciplina di un elaborato CAD: simboli con dimensione fisica costante, porte esplicite, accessori realmente inseriti nelle linee, connessioni ortogonali, prossimità funzionale, testi leggibili, cartiglio completo e controlli bloccanti prima dell'emissione finale.

## 2. Obiettivi

La skill deve:

1. leggere il contesto disponibile della conversazione e gli allegati pertinenti;
2. ricostruire la configurazione decisa dall'ingegnere;
3. produrre un modello tecnico strutturato e tracciabile;
4. individuare accessori necessari, raccomandati o condizionati;
5. presentare un unico dossier di approvazione prima del disegno;
6. generare uno o più elaborati vettoriali coordinati;
7. produrre una distinta quantitativa coerente con il modello;
8. impedire l'emissione finale quando restano errori bloccanti.

## 3. Non obiettivi

La prima versione non deve:

- dimensionare generatori, tubazioni, canali, accumuli o circolatori;
- selezionare autonomamente le apparecchiature principali;
- modificare silenziosamente le scelte dell'ingegnere;
- produrre annotazioni dettagliate di posa e montaggio;
- sostituire la verifica e l'approvazione professionale;
- produrre tavole planimetriche o un modello BIM;
- produrre schemi elettrici esecutivi completi;
- dipendere da AutoCAD per generare l'elaborato iniziale.

I collegamenti di regolazione strettamente necessari alla comprensione funzionale possono essere rappresentati come rete logica dedicata.

Tavole planimetriche e schemi elettrici completi sono esclusi dalla skill attuale, ma registrati nella roadmap come possibili estensioni future del progetto generale. Non introducono requisiti anticipati nell'architettura corrente.

## 4. Perimetro dei sistemi

Il nucleo deve poter descrivere combinazioni arbitrarie dei domini seguenti:

- idronico: caldo, freddo, reversibile, ACS e ricircolo;
- aeraulico: mandata, ripresa, espulsione e aria esterna;
- refrigerante: espansione diretta, VRF/VRV e relative diramazioni;
- gas combustibile;
- condensa e scarichi funzionali;
- misura, regolazione e segnali logici pertinenti.

Esempi validi comprendono centrali con caldaie, pompe di calore, sistemi ibridi, scambiatori, accumuli, UTA e reti miste; zone differenti possono usare contemporaneamente radiatori, pavimento radiante e ventilconvettori.

Il primo caso PDC-ACS-volano quattro attacchi-due zone è un caso di accettazione, non una struttura speciale nel codice.

## 5. Flusso utente end-to-end

### 5.1 Attivazione

L'ingegnere definisce l'impianto nella normale conversazione e richiama la skill con una richiesta equivalente a: «Ora disegna l'impianto che abbiamo deciso».

La skill non richiede di ricompilare un modulo. Prima controlla il contesto realmente disponibile e segnala soltanto eventuali lacune che impediscono una ricostruzione affidabile.

### 5.2 Ricostruzione

La skill:

1. identifica decisioni, componenti, valori e relazioni presenti nella conversazione;
2. distingue fatti approvati, ipotesi e dati mancanti;
3. costruisce la topologia tecnica;
4. applica le regole di completezza;
5. prepara una prima interpretazione probabile per ogni ambiguità non bloccante.

### 5.3 Dossier di approvazione

Prima di disegnare, la skill presenta in un solo riepilogo:

- impianto interpretato;
- integrazioni necessarie, raccomandate e condizionate;
- quantità e posizione funzionale di ogni integrazione;
- motivazione e regola applicata;
- assunzioni adottate;
- domande residue con una soluzione proposta;
- suddivisione in tavole, solo se necessaria;
- campi documentali ancora mancanti.

La risposta «sì, procedi» approva l'intero dossier. Le correzioni dell'ingegnere modificano il modello prima del rendering.

### 5.4 Bozza e finale

Una bozza può contenere campi `DA DEFINIRE` ed è marcata chiaramente come bozza. Una tavola finale richiede:

- dati tecnici obbligatori completi;
- cartiglio completo;
- dossier approvato;
- controlli tecnici, geometrici e documentali superati;
- preflight grafico senza esiti bloccanti (§12.4);
- cold eye review non più in stato di rifiuto (§12.5).

La verifica avviene **prima della consegna**, dentro la skill. Chi la usa riceve un
elaborato già controllato: non è il collaudatore del prodotto.

## 6. Architettura logica

### 6.1 Separazione delle responsabilità

Il sistema è diviso in livelli indipendenti:

1. **orchestrazione della skill:** guida il flusso e legge il contesto;
2. **interpretazione AI:** ricostruisce l'impianto e propone integrazioni;
3. **modello tecnico canonico:** rappresenta la topologia approvata;
4. **pacchetti di dominio:** applicano vocabolario e regole specifiche;
5. **libreria dei simboli:** fornisce geometria vettoriale e metadati;
6. **motore di layout:** partiziona, dispone e instrada;
7. **renderer:** produce SVG e PDF;
8. **validatori:** bloccano errori tecnici, geometrici e documentali, e misurano la
   qualità grafica col preflight di §12.4;
9. **cold eye review:** un agente terzo giudica ciò che non si misura e può
   respingere l'elaborato, rimandandolo in ciclo (§12.5, §12.6).

I livelli 1 e 2 e il 9 sono non deterministici; dal 3 all'8 il comportamento è
deterministico. Il confine è netto per costruzione: la parte non deterministica
sceglie **gli ingressi**, la parte deterministica produce **l'elaborato**.

### 6.2 Nucleo universale e pacchetti di dominio

Il nucleo conosce concetti generali: componente, porta, connessione, rete, diramazione, sottosistema, attributo, tag e tavola.

Il nucleo non presume che tutte le reti si comportino nello stesso modo. Ogni pacchetto di dominio definisce:

- tipi di porta e compatibilità;
- attributi rilevanti;
- regole tecniche;
- simbologia e stile delle connessioni;
- controlli specifici;
- convenzioni di direzione e diramazione.

Questa separazione evita sia gli schemi rigidi sia un motore monolitico in cui acqua, aria, refrigerante e gas vengono trattati indistintamente.

## 7. Modelli e fonte di verità

### 7.1 Modello tecnico canonico

Il progetto è rappresentato da un documento strutturato validato formalmente. Deve contenere almeno:

- metadati del progetto e della revisione;
- sottosistemi e reti;
- componenti e proprietà;
- porte tipizzate;
- connessioni fra porte;
- accessori inseriti nelle connessioni;
- dati mancanti, assunzioni e provenienza;
- regole applicate e relativo esito;
- stato di approvazione;
- struttura delle tavole.

Ogni entità ha un identificativo stabile. Questo consente confronti fra revisioni, conteggi affidabili e rigenerazione deterministica.

### 7.2 Modello geometrico derivato

Coordinate, segmenti, ingombri, label e rimandi di tavola sono salvati in un modello geometrico separato e derivato dal modello tecnico.

Il modello tecnico è la fonte di verità. SVG e PDF sono elaborati generati: eventuali correzioni persistenti devono rientrare nel modello o in override espliciti, non essere applicate manualmente al PDF.

### 7.3 Componenti in linea

Una valvola, un filtro o un altro componente in linea non viene sovrapposto a una tubazione continua. Nel modello topologico spezza la connessione in due segmenti collegati alle proprie porte. Il renderer disegna quindi una geometria corretta per costruzione.

## 8. Libreria di simboli

Ogni componente pubblicato comprende:

- SVG vettoriale originale;
- identificativo stabile e denominazione;
- dominio e funzioni;
- dimensioni fisiche nominali in millimetri;
- porte con coordinate, direzione e tipo;
- orientamenti ammessi;
- ingombro e area di rispetto;
- punti preferiti per tag e descrizioni;
- regole per l'interruzione delle connessioni;
- fonte o convenzione grafica;
- versione della definizione.

### 8.1 Simboli compositi

Un prodotto fisico che integra più funzioni è mostrato come un unico simbolo riconoscibile. Per evitare un'esplosione incontrollata di file, le varianti possono essere costruite internamente da primitive riusabili e poi pubblicate come simboli compositi validati. L'utilizzatore vede comunque un unico componente e la distinta lo conta una sola volta.

### 8.2 Immutabilità della scala

Le dimensioni stampate non cambiano in funzione della complessità dell'impianto. Il layout può cambiare spaziatura, disposizione e numero di tavole, ma non ridurre arbitrariamente simboli, testi o spessori.

## 9. Motore delle regole

Ogni regola dichiara:

- identificativo e versione;
- dominio e campo di applicazione;
- condizione di attivazione;
- fatti richiesti;
- proposta o vincolo;
- posizione funzionale;
- categoria: necessaria, raccomandata o condizionata;
- motivazione e fonte;
- vincolo grafico collegato;
- criterio automatico di verifica.

### 9.1 Gerarchia delle fonti

1. prescrizione normativa applicabile;
2. prescrizione pertinente del produttore;
3. buona pratica tecnica documentata;
4. convenzione grafica del progetto.

Le prescrizioni di prodotto vengono considerate soltanto se modificano topologia o accessori rappresentati. Le prescrizioni di posa restano fuori perimetro.

Le fonti protette da diritto d'autore sono citate e sintetizzate; non vengono riprodotte integralmente nella skill.

### 9.2 Limite di autorità

Il motore delle regole non trasforma automaticamente una proposta in progetto approvato. Le integrazioni tecniche passano sempre dal dossier di approvazione. Le sole correzioni grafiche che non cambiano il significato tecnico possono essere applicate automaticamente.

## 10. Layout e impaginazione

### 10.1 Ordine corretto della pipeline

La revisione end-to-end ha corretto l'ordine inizialmente ipotizzato. La pipeline è:

```text
modello tecnico approvato
-> validazione topologica
-> partizione funzionale in tavole, se necessaria
-> assegnazione dei simboli
-> layout per ciascuna tavola
-> instradamento ortogonale
-> posizionamento di testi e tag
-> generazione dei rimandi fra tavole
-> rendering SVG
-> composizione del cartiglio
-> validazione geometrica e documentale
-> esportazione PDF
```

La partizione precede il layout finale: tagliare geometricamente un disegno già disposto spezzerebbe circuiti e associazioni in modo arbitrario.

### 10.2 Layout deterministico

Il motore usa vincoli e priorità esplicite:

- flusso principale leggibile;
- raggruppamento per sottosistema;
- prossimità degli accessori al componente servito;
- allineamento su griglia;
- connessioni ortogonali;
- penalità per incroci, inversioni e sovrapposizioni;
- rispetto degli ingombri e delle aree di servizio grafiche;
- posizioni stabili fra rigenerazioni equivalenti.

Il layout ha limiti di iterazione. Se non trova una soluzione valida, prova una partizione diversa o restituisce una diagnostica; non riduce le dimensioni e non continua indefinitamente.

### 10.3 Multi-tavola semantico

Un impianto semplice usa una sola A3. Quando serve, la divisione segue centrale, distribuzioni, zone o domini funzionali. Le continuità sono rappresentate con connettori di rimando dotati di identificativo, provenienza, destinazione e fluido.

## 11. Sistema grafico e formati

### 11.1 Spazio carta

Il formato ordinario è A3 orizzontale. Tutte le grandezze grafiche sono definite in millimetri di carta:

- dimensioni dei simboli;
- spessori delle linee;
- altezze dei testi;
- distanze minime;
- passo della griglia;
- margini e area utile;
- geometria dei rimandi.

A1 e A0 sono supporti secondari. Un elaborato di grande formato non deve essere stampato ridotto su A3 se ciò viola la leggibilità prevista.

### 11.2 SVG e PDF

SVG è il formato vettoriale intermedio; PDF è il formato finale iniziale. Le unità, le trasformazioni e gli spessori devono essere verificati lungo l'intera catena di esportazione affinché la misura stampata sia invariata.

### 11.3 Cartiglio

Il cartiglio Nove C viene trasformato in un template vettoriale compilabile. I campi obbligatori comprendono almeno committente, progetto, titolo tavola, data, revisione, commessa, numero tavola e responsabilità previste dal modello aziendale.

Il PDF sorgente viene conservato come riferimento. Prima dell'uso in produzione devono essere verificati font, sostituzioni tipografiche e portabilità; l'ispezione iniziale ha rilevato avvisi di font durante il rendering e quindi il template non deve dipendere ciecamente dai font incorporati nel PDF originale.

## 12. Controlli qualità

### 12.1 Controlli tecnici

- compatibilità fra porte;
- reti e componenti privi di collegamenti impossibili;
- completezza degli accessori approvati;
- direzioni e ramificazioni coerenti;
- assenza di modifiche progettuali non approvate;
- quantità della distinta coerenti con il modello.

### 12.2 Controlli geometrici

- nessun componente flottante;
- nessuna linea attraversa un simbolo in linea;
- porte e segmenti coincidono entro tolleranza;
- nessuna sovrapposizione non ammessa;
- testi e tag non collidono;
- distanze minime rispettate;
- rimandi multi-tavola accoppiati;
- oggetti interamente dentro l'area utile.

### 12.3 Controlli documentali

- cartiglio completo;
- revisione coerente;
- tutte le tavole numerate;
- distinta e manifest coerenti;
- nessun `DA DEFINIRE` in una versione finale;
- versione di skill, libreria e regole registrata nel manifest di progetto.

### 12.4 Preflight grafico

I controlli geometrici di §12.2 dimostrano che nulla è rotto, non che la tavola sia
ben disegnata: una tavola può superarli tutti ed essere fatta male. Il preflight
grafico misura la qualità del disegno, non la sua validità (D-063):

- pieghe per tratta;
- attraversamenti fra tratte;
- **sovrapposizioni longitudinali**, che sono un errore e non un costo (D-062);
- distanze di rispetto fra una linea e un simbolo, e fra due linee parallele;
- lunghezza complessiva delle tubazioni rispetto al minimo teorico;
- area di foglio occupata, e vuoti anomali.

Ogni misura produce un esito con la stessa classificazione di §13: bloccante, da
approvare o avviso. Le soglie sono parte del prodotto e vivono con esso: non sono
un test su un caso di esempio.

### 12.5 Cold eye review

Ciò che resta — composizione, ordine di lettura, se la tavola «sembra una tavola» —
non si misura, e lo giudica un **agente terzo** (D-063): contesto proprio, diverso da
quello che ha costruito il modello, perché un agente che rilegge il proprio lavoro lo
approva. Giudica contro lo standard grafico scritto, non contro il gusto, altrimenti
due esecuzioni danno due giudizi diversi.

Lo standard grafico scritto è `docs/QUALITA_GRAFICA.md`, «le regole del colpo
d'occhio» (D-076): una quarantina di regole di buona pratica in sei famiglie, ciascuna con
cosa vuole, come si vede a occhio e uno stato. Non è una norma e non dice cosa mettere
in un impianto: dice come si disegna quello che l'ingegnere ha deciso.

L'agente giudica **l'immagine renderizzata a misura di stampa, non il sorgente**
(D-077), e parte dalla sola composizione guardata da lontano: se non regge, la tavola
torna indietro senza esaminare il resto. Ogni rilievo nomina la regola violata — un
giudizio senza regola nominata non è utilizzabile e non fa crescere la carta.

L'agente può **respingere**. Quando lo fa, il lavoro torna in ciclo (§12.6). Non
approva nulla in senso tecnico: l'approvazione resta dell'ingegnere.

Preflight e cold eye review non sono ridondanti. Una sovrapposizione di due
millimetri e mezzo si trova misurandola, non guardandola; «questa non sembra una
tavola» non si misura. Ciò che il cold eye review respinge due volte per lo stesso
motivo diventa una soglia del preflight (D-065): il giudizio non deterministico è il
modo in cui si scoprono le regole, non il modo in cui si applicano per sempre.

### 12.6 Il ciclo di revisione

    input di progetto
       -> interpretazione AI                        (non deterministica)
    modello tecnico + piano di impaginazione        <- il ciclo cambia QUESTO
       -> regole, layout, instradamento, rendering  (deterministico)
    tavola
       -> controlli tecnici, geometrici, documentali, preflight grafico
       -> cold eye review
            approvata  -> consegna
            respinta   -> nuovo piano di impaginazione, e si ricomincia

Il ciclo cambia gli **ingressi**, mai il disegno prodotto (D-064). Ciò che può
cambiare è il piano di impaginazione — quale sottosistema su quale fascia, in che
ordine, se dividere in più tavole, quale formato — che è fatto di scelte discrete
registrate nel modello proprio perché l'AI potesse sceglierle diversamente (D-042).
Nessun agente tocca la geometria: stesso modello e stesso piano danno lo stesso
identico file, e questa proprietà non è negoziabile.

Il ciclo ha un numero massimo di passate ed è **monotono**: una passata si accetta
solo se le misure del preflight non peggiorano. Senza, un ciclo può oscillare fra due
impaginazioni o «migliorare» all'infinito.

### 12.7 Controllo visivo di release

Ogni release deve renderizzare i PDF in immagini e sottoporli a controllo visivo
umano, oltre a prove di stampa A3 su casi rappresentativi. Non è sostituito né dal
preflight né dal cold eye review.

## 13. Errori e diagnostica

Gli esiti sono classificati in:

- **bloccante:** impedisce la generazione finale;
- **da approvare:** richiede una decisione dell'ingegnere;
- **avviso:** non impedisce l'elaborato ma resta nel report;
- **correzione grafica automatica:** non cambia il significato tecnico.

Ogni messaggio deve indicare elemento coinvolto, problema, regola, conseguenza e azione consigliata. Il sistema non nasconde correzioni tecniche e non produce un PDF apparentemente definitivo quando la validazione è fallita.

## 14. Strategia di collaudo

Il collaudo evita il sovradattamento a uno schema campione mediante più livelli:

1. **test della libreria:** porte, dimensioni, orientamenti e ingombri di ogni simbolo;
2. **test delle regole:** casi positivi, negativi e di confine;
3. **test di composizione:** sottosistemi piccoli combinati in modi differenti;
4. **test misti:** idronica, aria, refrigerante e gas nello stesso progetto;
5. **test di proprietà:** invarianti generali, come nessuna porta obbligatoria aperta e nessuna linea passante sotto un componente;
6. **test di regressione grafica:** confronto geometrico e immagini di riferimento;
7. **test di riproducibilità:** stesso input e stesse versioni producono lo stesso risultato;
8. **revisione dell'ingegnere:** controllo professionale su casi reali.

Il caso iniziale è accompagnato da varianti: terminali misti, componenti rimossi, rami aggiunti, ordine modificato, ambiguità e configurazioni volutamente non valide.

## 15. Pacchetto prodotto e release

La skill installabile contiene:

- istruzioni di orchestrazione;
- schemi dei dati;
- pacchetti di dominio;
- libreria SVG e manifesti;
- regole e registro delle fonti;
- script di validazione, layout, rendering ed esportazione;
- template del cartiglio;
- casi di prova e riferimenti grafici;
- comando di autoverifica dell'installazione.

Ogni release produce:

- `releases/latest/` pronto da installare;
- `releases/archive/DisegnatoreMEP-vMAJOR.MINOR.PATCH.zip`;
- manifest con versione, data, commit, compatibilità e checksum;
- esito dei test e inventario della libreria.

Una release non viene costruita copiando manualmente file di sviluppo: è generata da uno script ripetibile e verificata in un ambiente pulito.

## 16. Elaborati generati per un progetto

Il pacchetto di consegna di un singolo progetto comprende:

- PDF finale o bozza marcata;
- SVG vettoriale corrispondente;
- modello tecnico approvato;
- distinta quantitativa dei componenti e accessori;
- report di preflight con regole, avvisi e controlli;
- manifest di riproducibilità.

La distinta è generata dal modello, non ricavata contando elementi grafici nel PDF.

## 17. Riferimenti iniziali per il linguaggio grafico

La ricerca formale parte almeno da:

- ISO 5457 per formato e organizzazione delle tavole tecniche;
- ISO 7200 per i dati dei cartigli;
- ISO 14617-1:2025 e ISO 14617-2:2025 per regole e libreria generale dei simboli per diagrammi;
- ANSI/ASHRAE Standard 134 per il linguaggio simbolico HVAC&R;
- SVG 2 del W3C per coordinate, unità e controllo degli spessori.

Questi riferimenti non costituiscono ancora la libreria definitiva. Ogni simbolo o regola deve essere valutato per pertinenza europea/italiana, licenza, chiarezza e coerenza con il livello dell'elaborato.

## 18. Esito della revisione end-to-end

### 18.1 Valutazione da disegnatore CAD esperto

L'impostazione è coerente perché tratta accessori, tubazioni e macchine come elementi topologici collegati e non come forme flottanti. Scala fisica, prossimità funzionale, cartiglio, multi-tavola e controllo di stampa sono correttamente inclusi.

Correzioni recepite:

- inserimento topologico reale dei componenti in linea;
- partizione funzionale prima del layout;
- cartiglio finale obbligatoriamente completo;
- distinta quantitativa derivata dal modello;
- controllo visivo e stampa oltre ai soli test geometrici.

### 18.2 Valutazione da sviluppatore CAD senior

L'architettura è coerente perché separa semantica, geometria e rendering; usa identificativi stabili; mantiene un'unica fonte di verità; isola le regole dei domini; limita gli algoritmi di layout; rende versionabili simboli e regole; prevede output riproducibili e test multilivello.

Correzioni recepite:

- nucleo universale con adattatori, non regole universali indistinte;
- compositi compilati da primitive per contenere la crescita della libreria;
- SVG/PDF trattati come artefatti, non sorgenti modificabili;
- manifest di riproducibilità e versionamento delle regole;
- fallback esplicito quando il layout non converge.

### 18.3 Conclusione

Non restano contraddizioni architetturali bloccanti. Il progetto è ampio ma decomponibile in moduli indipendenti. La specifica è sufficientemente definita per passare, dopo revisione del PM, alla pianificazione dell'implementazione.

## 19. Criteri di accettazione del design

Il design è stato approvato dal PM dopo avere confermato che:

- il flusso conversazione -> approvazione -> disegno rispecchia il lavoro reale;
- il prodotto non è limitato a schemi tipo;
- le tavole mantengono scala e leggibilità professionali;
- l'ingegnere conserva tutte le decisioni progettuali;
- il pacchetto finale contiene quanto serve per controllo, stampa e riproduzione.
