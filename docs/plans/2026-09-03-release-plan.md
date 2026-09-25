# Piano di release — Disegnatore MEP

**Scritto il 3 settembre 2026. Annotato il 20 settembre 2026** (`DRAW-015`).

**La release in corso è la 0.3 — generalizzazione**, e dal 24 settembre 2026 il lavoro va verso **la
prima release**, col perimetro che il PO ha dato (D-183, sezione qui sotto). Il numero di versione
Python resta `0.1.0`: non ha mai seguito le release dichiarate, ed è un asse diverso.

> ⚠ **Due punti di questo piano sono storia, e lo dicono qui in testa.**
>
> - **La 0.2 è eseguita**: è il racconto di come è andata, non lavoro aperto.
> - **Il motore «costo-peso» che la 0.2 descrive non decide più la posa.** Dal 20 settembre
>   2026 (**D-151**) il disegno lo **compone un agente** — pianificatore → motore →
>   revisore — e la catena vigente sta in `docs/ARCHITETTURA-DEL-PIANO.md`. Dove qui sotto
>   si legge «costo globale», «costo-peso» o «Drawing Director», si legga quel documento.
>
> Le righe superate portano la loro nota, con la decisione che le ha superate. Il piano non
> è stato riscritto oltre a questo: **che cosa viene dopo la 0.3 è una scelta del PO**, e
> non si decide in una passata di riallineamento documentale.

## ▶ La prima release — il perimetro del PO, 24 settembre 2026 (D-183)

**Come si usa** (I-121): in una sessione di Claude il progettista spiega l'impianto e lancia la
skill; mentre «Capire» lavora, la skill può fare **domande chiarificatrici**; poi il corredo,
l'approvazione del grafo da parte del progettista, la composizione e la tavola.

**Che cosa ci deve essere**, in cinque pacchetti. L'elenco è del PO; **l'ordine è una proposta
della sessione** (D-183, punto 3), e il PO lo può cambiare:

> **E il PO l'ha cambiato, il 25 settembre 2026** (I-126): «in questa sessione ci dedichiamo
> esclusivamente al cartiglio». `REL-002` è venuto prima di `REL-001`, che è rinviato e non
> consegnato (`docs/pm/2026-09-24-rel001-pacchetto.md`). Il cartiglio non aspetta le domande della
> skill: «Capire» sa già dichiarare quello che manca, e le sue istruzioni dicono che cosa chiedere.

| pacchetto | che cosa | perché in quest'ordine |
|---|---|---|
| **`REL-001`** | **la skill vera e propria** — l'ingresso che cuce i cinque pezzi, la cartella installabile — **e il PDF fatto dalla skill** (I-121, I-122) | è il rischio più vecchio del progetto: la skill non è mai girata nel suo ambiente. E senza il PDF la skill non consegna niente |
| **`REL-002`** | **il cartiglio Nove C compilato** (I-123) | i dati del cartiglio li raccoglie «Capire»: si aggiungono alle domande della skill che `REL-001` ha messo in piedi |
| **`REL-003`** | **i simboli nuovi**: pompa di calore di alta potenza, caldaia modulare a condensazione, solare termico, fan-coil canalizzato (I-124) | forme dalle fonti, approvate dal PO guardandole; per ciascuna la voce di catalogo, e le regole solo dove il PO le dà |
| **`REL-004`** | **il DXF** (I-125) | prima si definisce con il PO **come** si esporta — livelli, blocchi, testi, scala —, poi si scrive |
| **`REL-005`** | **il pacchetto della release** | il numero di versione, `releases/latest/` e lo ZIP numerato (D-009), la guida d'installazione, la suite verde e il collaudo sui casi di accettazione |

**Restano da decidere con il PO**, e non fermano `REL-001`: il collaudo su impianti veri (la
proposta del 24 settembre chiedeva due o tre testi di Nove C); il via libera a togliere dal
pacchetto il percorso del solutore e le sue prove rosse, che D-151 teneva agli atti. L'analisi da cui
nasce questo elenco sta in `docs/plans/2026-09-24-verso-la-prima-release.md`.

## 0.2 — Prima tavola approvata — **eseguita**

Obiettivo: portare l'impianto 1 a una tavola **impiantisticamente corretta secondo il
grafo approvato dal PO**, deterministica e graficamente approvata dal PM/PO.

- `DRAW-002`: motore di posa costo-peso e routing compatto;
- `DRAW-003`: rimozione definitiva della linea continua di terra e fase terminale delle
  etichette, indipendente da posa e routing;
- `DRAW-004`: candidati di allineamento fra porte, dorsali principali rettilinee e T che
  può assorbire una curva, sempre scelti dal costo globale e mai come regole assolute;
- `DRAW-005`: correttezza del grafo dell'impianto 1 e simboli/porte che influenzano la
  posa; etichette di nodo opzionali, sigle principali sempre presenti;
- `DRAW-005-R1`: rifiniture PO su flussi dei rami di servizio, sicurezza dei generatori,
  coerenza locale degli accessori e leggibilità dei simboli;
- uscita: PDF, PNG, SVG e metriche riproducibili della tavola 1.

Gate: il PO riconosce un disegno ordinato e tecnicamente leggibile. Finché questo gate
non passa, non si estende il lavoro agli altri impianti.

> **Nota del 20 settembre 2026.** Il «costo globale» di `DRAW-004` e il «motore di posa
> costo-peso» di `DRAW-002` sono **storia da D-151**: una somma pesata non sa esprimere una
> gerarchia di giudizio. `layout/improve.py`, la fase del tronco di `layout/spine.py` e
> `layout/dilate.py` restano agli atti e non decidono più la posa (D-151, D-149).

### Gate verticale — chat di lavoro

Dopo la prima generalizzazione controllata sull'impianto 2 e prima di estendere il ciclo
agli impianti 3–5, installare la skill in un ambiente pulito e collaudare un percorso
reale: input naturale → grafo e domande → approvazione PO → generazione deterministica
→ verifica → link al PDF. Questo gate anticipa il rischio d'integrazione oggi rimandato
impropriamente alla 1.0 senza impedire al primo caso nuovo di verificare il motore.

## 0.3 — Generalizzazione

Applicare senza coordinate speciali lo stesso motore agli impianti 2–5, uno per volta.
Ogni nuovo impianto deve scoprire una classe di difetto nuova; non si ripetono quattro
cicli sullo stesso errore.

- `DRAW-006`: impianto 2 come prima nuova tavola; semantica dei gruppi accessori,
  rubinetto portamanometro a tre vie e stati idraulici delle valvole multivia. La tavola 1
  resta una regressione automatica; gli impianti 3–5 sono soltanto smoke test.
- `DRAW-006-R1`: ordine funzionale indipendente dagli ID, assi attraverso multivia,
  gruppo sanitario EN 1487 composito, riempimento tecnico a due reti e chiusura D-120;
  consegna grafica completa ancora limitata alla sola tavola 2.

Gate: cinque impianti, senza regressioni sulla tavola 1 e senza eccezioni legate agli
identificativi degli esempi.

> **Nota del 20 settembre 2026.** La parola «deterministici» esce dal gate: la
> riproducibilità bit-per-bit di **D-023 è sospesa da D-151** — due composizioni dello
> stesso impianto non danno la stessa tavola — ed è un prezzo dichiarato, accettabile
> perché la tavola esce anche in **DXF** e si rifinisce in AutoCAD (I-072, D-148).
>
> Che cosa il gate misura adesso, e sta già negli atti: i formati ordinari sono **A4, A3,
> A2, A1** (D-148, dichiarata momentanea dal PO); una tratta che non si instrada **non
> uccide più la tavola** ma si marca `unresolved` e il preflight la nomina (D-150); il
> riempimento del foglio è una **misura**, non un obiettivo (D-149).
>
> **Dove siamo, misurato:** gli impianti 1 e 5 sono stati **composti a mano** ed eseguiti
> dal motore con **zero rilievi bloccanti e zero tratte cedute**
> (`docs/collaudi/PROVA-PIANO/`). È la prova che ha deciso D-151. Quello che non dimostra,
> e il PO l'ha detto, è che le tavole siano belle.

## 0.4 — Tavola professionale completa

Completare ciò che non altera la geometria critica già collaudata: simboli secondari,
spessori normati,
cartiglio Nove C, legenda, testi e gestione motivata del formato/paginazione.

Gate: tavola stampabile e utilizzabile come elaborato tecnico, non soltanto come prova
del motore.

## ~~0.5 — Drawing Director~~ — **superata da D-151 e D-153, 20 settembre 2026**

> Questa voce diceva di introdurre il supervisore AI **soltanto dopo** la stabilizzazione
> delle metriche deterministiche, e di farlo agire **sui parametri**. Tutte e due le cose
> sono state ribaltate dal PO:
>
> - **il revisore si costruisce subito** (**D-153**), perché è lo strumento con cui si
>   scrivono le regole, una tavola alla volta — non il premio a valle;
> - **corregge il piano**, non i parametri (**D-151**): legge i rilievi, guarda la tavola, e
>   ogni spostamento porta il nome della regola che lo motiva.
>
> Resta vero l'unico vincolo che questa voce poneva e che nessuna decisione ha tolto: **il
> revisore non altera il grafo** — sposta pezzi, non collega pezzi (`HANDOFF.md`).
>
> Il testo originale: «Introdurre il supervisore AI soltanto dopo la stabilizzazione delle
> metriche deterministiche. Il Director osserva il raster, propone correzioni attraverso
> parametri e candidati ammessi e richiede una nuova generazione; non modifica direttamente
> la tavola e non altera il grafo.» Gate: «miglioramento misurabile su casi non usati per
> costruire le regole, mantenendo riproducibilità e tracciabilità delle correzioni.»
>
> **Dove vive adesso:** `docs/ARCHITETTURA-DEL-PIANO.md` §1 e §5, e il pacchetto attivo
> `DRAW-015`.

## 1.0 — Release utilizzabile

Pipeline completa dal modello approvato alla tavola verificata, documentazione di
installazione, pacchetto versionato e collaudo sui casi di accettazione.

~~Il PM aggiorna `ACTIVE_WORK_PACKAGE.md` dopo ogni merge. Il DEV esegue soltanto il
pacchetto attivo; il PO interviene sui requisiti e sul giudizio del risultato.~~

**Dal 19 settembre 2026 (D-147)** PM e DEV sono **la stessa sessione**: quella sessione
scrive il pacchetto, lo sviluppa, mostra le tavole al PO e — solo dopo il suo sì — fonde;
poi, nella stessa sessione, scrive `HANDOFF.md` e il pacchetto successivo. Il PO decide i
requisiti, giudica il risultato **guardando le tavole** e approva la fusione (D-146).
