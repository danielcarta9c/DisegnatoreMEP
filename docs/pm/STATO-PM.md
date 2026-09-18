# STATO PM — il documento d'ingresso del PM

**Aggiornato:** 2026-09-18
**A chi serve:** alla sessione PM che subentra. Leggi questo e sei operativo: non ti serve
un prompt lungo, e chi te lo dà ti sta raccontando qualcosa che dovrebbe stare qui.
**Regola di questo file:** ogni sessione PM lo aggiorna prima di chiudere. Un file di stato
vecchio è peggio di nessun file di stato.

---

## 1. Chi sei

Il **PM** del progetto, e il PM è **uno solo** (D-130). Scrivi i pacchetti e i criteri,
verifichi le consegne criterio per criterio, fondi su `main`, e in funzione di ciò che la
verifica trova scrivi le correzioni per il pacchetto successivo.

Le regole del mestiere stanno in `docs/governance/OPERATING_MODEL.md` §1.2.1 e §3. Le due
che si dimenticano per prime:

- **Non sei il DEV.** Il DEV è una sessione diversa, esegue il solo pacchetto attivo, apre
  la PR e si ferma. L'indipendenza sta lì, fra chi esegue e chi giudica.
- **Non decidi al posto del PO.** Dominio MEP, requisiti, convenzioni grafiche e «è questo
  che volevo» sono suoi. Tu proponi e aspetti.

**Come parlare col PO.** È un ingegnere MEP senior: giudica il **risultato**, non
l'implementazione. Mostragli la tavola, non i criteri numerati; niente nomi di file, di
funzioni o di prove. Se stai per scrivere «il criterio 8 è raggiunto in parte», fermati e
riscrivilo come lo diresti a un collega guardando il disegno.

**Vale anche per le sigle degli input.** Il 15 settembre gli ho portato le domande del
triage scritte come «`I-002` e `I-059` chiedono allo spessore due cose incompatibili», e me
le ha rimandate indietro: «per me non significano assolutamente nulla. O non le scrivi
proprio, oppure se mi chiedi qualcosa deve essere tradotta in termini che io possa capire».
Le sigle servono a noi per ritrovare la riga e restano di qua. La versione buona — la stessa
domanda detta guardando il disegno — sta in `2026-09-15-triage-input-aperti.md` §11, ed è il
modello da riusare.

## 2. Dove siamo, al 18 settembre 2026

| | |
|---|---|
| `main` | **la testa che leggi adesso.** Non si scrive uno SHA qui: questo file vive su `main` e ogni suo ritocco sposta la testa, quindi il numero nasce vecchio — è già successo due volte. La base si dice per contenuto: l'ultima fusione è la PR #33, che porta il triage degli input, il verdetto sulla PR #32 e DRAW-011 |
| Release dichiarata | **0.3 — generalizzazione, impianto 2** (`docs/plans/2026-09-03-release-plan.md`) |
| Pacchetto attivo | **DRAW-013** (`ACTIVE_WORK_PACKAGE.md`): la tavola si allarga tutta insieme e non tocca il bordo (D-142, D-143). **BOZZA da approvare dal PO.** Parte dal ramo di `DRAW-012`, non da `main` |
| PR #41 (DRAW-012) | **verificata e respinta.** Tredici criteri su sedici, nessuno barato, rapporto onesto — ma il PO ha guardato le tavole e ha detto «era meglio prima». Verdetto in `docs/pm/2026-09-18-review-pr41-draw012.md`. **Il suo lavoro non è su `main`, e non va rifatto**: `DRAW-013` riparte dal ramo `claude/hopeful-ramanujan-9bs0cb` (`17ff425`) |
| PR #32 (DRAW-010) | verificata e respinta il 15 settembre. Verdetto in `docs/pm/2026-09-15-review-pr32-draw010.md`. Il suo lavoro non è su `main` |
| Ultima consegna verificata | **DRAW-012**, PR #41. Torna al DEV con `DRAW-013` |
| Suite su `main` | **10 rosse, 1470 verdi, 24 saltate, 11 xfailed** — rimisurata dal PM il 17 settembre, coincide |
| Suite sul ramo di DRAW-012 | **13 rosse, 1482 verdi, 24 saltate, 11 xfailed.** È il riferimento di `DRAW-013`, non quello di `main` |
| Tavola 1 su `main` | 4 pieghe · 1 incrocio · 470,0 mm · riempimento 29,8 % · copertura 0,625 · ingombro 245 × 100 mm |
| Tavola 2 su `main` | 5 pieghe · 1 incrocio · 600,0 mm · riempimento 50,1 % · copertura 0,625 · ingombro 257,5 × 160 mm |
| Tavole sul ramo di DRAW-012 | 1 · 4/1 · 45,1 % · 0,750 · 322,5 × 115 mm — 2 · 5/1 · 64,1 % · 0,750 · 315 × 167,5 mm. **Bocciate dal PO**: riempimento comprato allungando i tratti, e disegno fino quasi al bordo |
| Impianti 3, 4, 5 | nessuno produce una tavola, né su `main` né sul ramo di `DRAW-012`. La tavola 4 si ferma su un confine di rete posato dieci millimetri fuori dall'area di disegno |
| Registro degli input | **12 righe aperte + 4 regole permanenti**, su 65. I-073 e I-074 del 18 settembre sono chiuse da D-142 e D-143 |
| Prodotto in chat | **mai eseguito nel suo ambiente finale.** È il rischio 1, il più vecchio |

Il verdetto completo su DRAW-009, con tutte le misure e i comandi, sta in
`docs/pm/2026-09-14-review-pr27-draw009.md`. È anche il modello di come si scrive un
verdetto.

## 3. Che cosa aspetti dal DEV, e come lo verifichi

`DRAW-013` chiede undici criteri. Quando arriva la PR:

0. **Prima guardi la tavola, poi conti.** È la regola nata il 15 settembre, sulla consegna di
   DRAW-010 (`I-064`): il PM aveva portato al PO pieghe, incroci e lunghezza senza aver letto
   il disegno, e i quattro difetti veri — il prelievo tornato al centro del foglio, lo stretch
   mai avvenuto, lo scarico che attraversa la mandata, la tavola 4 illeggibile — li ha visti
   il PO. Una misura dice se un numero peggiora; non dice se il disegno ha senso. Si apre
   guardando, si chiude misurando.
1. **Prima le tue misure, poi il suo rapporto.** Il rapporto del DEV, il corpo della PR e i
   messaggi dei commit ti sono preclusi finché non hai formato i tuoi numeri. Poi li leggi e
   segnali ogni differenza.
2. **Misura base e ramo nella stessa cartella**, passando con `git checkout`. Il pacchetto è
   installato *editable* e il `.pth` contiene il percorso assoluto di UNA cartella: un
   `git worktree` che riusa l'ambiente esegue le prove di prima **col codice di adesso**,
   senza nessun errore che te lo dica.
3. **La suite si riesegue per intero, sui due lati.** Mezz'ora l'una: avviale presto.
4. **Ogni criterio si chiude con un comando e il suo output.** Senza prova eseguibile è NON
   raggiunto, non «probabilmente».
5. **Misura anche ciò che il pacchetto dichiara fuori perimetro**, quando è una capacità che
   il prodotto aveva. È la regola nata dall'impianto 4, che si è perso proprio così.
6. **Il verdetto è scritto** in `docs/pm/`, criterio per criterio, e si pubblica anche come
   commento sulla PR.

Gli strumenti di misura esistono e non vanno riscritti: `docs/collaudi/DRAW-008/metriche.py`
(misure per livello di gerarchia), `docs/collaudi/DRAW-009/criteri.py`,
`le-due-sovrapposizioni.py`, `due-prove-senza-caso.py`,
`perche-la-strada-bassa-non-c-era.py`.

## 4. I fili che il PM porta

In ordine di quanto pesano, dopo le sei disposizioni del PO del 15 settembre. I rischi
numerati stanno in `PROJECT_STATE.md`.

0. **Il motore non ragiona nell'ordine del disegnatore** (`I-069`, D-138, 16 settembre). Il
   PO: «stiamo ottimizzando la punta di una lancia storta». Cinque differenze misurate fra
   l'ordine che ha dettato e quello che il motore esegue, **quattro a monte di qualunque
   taratura**: le strade secondarie sono in ultima fase, il circolatore non fa nemmeno tratta,
   con due generatori uno perde la classificazione, l'autostrada è una catena di frammenti
   senza invariante sulla catena, e quando l'invariante non si può tenere il motore butta via
   la fase invece di cedere una curva. **È DRAW-012**, ed è la voce che rende le altre
   misurabili. Analisi in `2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`.
1. **«Un passo avanti e uno indietro»** (`I-067`, 16 settembre). Il PO l'ha detto e ha
   ragione: `DRAW-009` migliora la tavola 1 e perde l'impianto 4, `DRAW-010` riprende
   l'impianto 4 e perde due budget e quattro prove. **La causa è del PM**: i pacchetti
   chiedono «non peggiora» e nessuno chiede «migliora», quindi il miglior esito possibile è
   pari. Da `DRAW-011` §F ogni pacchetto chiede **almeno un budget che migliora**, e i
   criteri di non-regressione si misurano **prima** di aprire la PR: se uno peggiora, il DEV
   non consegna, si ferma e riferisce. È la voce che pesa di più, perché non è un difetto del
   prodotto ma del modo in cui lo chiediamo.
2. **L'attuazione di D-126 sul prelievo è la causa unica di quasi tutto ciò che la PR #32
   rompe**: i tre incroci e i 45 mm della tavola 2, le otto prove nuove rosse, l'impianto 5
   che non arriva più alla posa. Il DEV e il PO ci sono arrivati per strade indipendenti. È
   la prima voce del pacchetto di correzione, e con essa rientra quasi tutto il resto.
3. **L'autostrada non esiste come oggetto** (`I-068`, misurato il 16 settembre). Con due
   generatori la pompa di calore non viene classificata autostrada — sull'impianto 4 lo è la
   caldaia e lei no — e in ogni caso un'autostrada è una catena di frammenti da 5-10 mm, uno
   per accessorio, con la rettilineità verificata su ciascun frammento e nessun invariante
   sulla catena intera. Diagnosi in `ACTIVE_WORK_PACKAGE.md` §E.1, cura da assegnare: è il
   candidato naturale del pacchetto dopo `DRAW-011`, insieme a D-136.
4. **L'anello della fase del tronco** (rischio 16). È la causa a monte di quasi tutto:
   tiene la tavola 2 sul ripiego, ha costretto ad allargare `is_valid` (rischio 19) e con
   ogni probabilità è ciò che blocca gli impianti 3, 4 e 5. **È §A di DRAW-010**, in corso.
5. **Il verso di mandata e ritorno lo decide la geometria** (`I-010`, aperto dal 9 agosto).
   Su circa un terzo delle tratte il colore di quel tubo è giusto per caso. **Il PO l'ha
   dichiarato fondamentale** — D-136 — ed è la voce principale del pacchetto dopo DRAW-010.
   Nessuno strumento lo misura ancora: `supply` è un booleano già deciso quando arriva alla
   geometria esportata, quindi l'indecisione va misurata dentro la camminata sul grafo.
6. **Il prodotto non gira in una chat vera** (rischio 1). Il più vecchio e il meno toccato.
   La 0.3 non si può dichiarare finita senza una prova verticale in una chat pulita.
7. **Lo spessore del tratto dice la gerarchia** (D-132): 0,50 mm autostrade, 0,25 mm
   servizio, due livelli e non tre. Oggi la tavola usa 0,18 / 0,35 / 0,50. Da assegnare, e
   porta con sé un nodo che D-132 lascia aperto — con due spessori in un nodo, il pallino di
   derivazione a quattro volte lo spessore va agganciato a uno dei due; il PM propone il più
   grosso.
8. **L'audit della libreria dei simboli** (rischio 2), che il PO deve approvare prima della
   0.3.
9. **La tavola 1 è sotto la finestra del riempimento**: 29,8 % contro un minimo di 45
   (D-140). È l'impianto su cui il tenersi larghi si vedrà di più, ed è dentro DRAW-012.
10. **L'export DXF** (`I-072`, 17 settembre). Fattibile e indipendente da tutto il resto: legge
    la geometria già esportata, non tocca posa né instradamento, e la libreria dei simboli è
    fatta quasi solo di rette, rettangoli e cerchi — sei archi e tre curve in tutto. **È il
    filo che cambia l'asticella**: se il disegnatore umano rifinisce in CAD, il motore non
    deve più essere perfetto al primo colpo. Pacchetto a sé, da aprire quando il PO lo vuole.
11. **L'ordine degli stacchi non ha un padrone** (rischio 17). Oggi vale per topologia sulle
   due tavole; diventa esigibile su un impianto che lo violi.
12. **Gli attacchi pari di un collettore**: la scambiabilità va dichiarata nel catalogo, non
   dedotta. Pacchetto a sé, da aprire se il PO lo vuole.

Non è più un filo: **lo squilibrio fra quadranti della tavola 2**. Il riempimento invece è
tornato, ma come finestra e non come traguardo (D-139), e la lunghezza è uscita del tutto.

## 5. Cold eye review del 15 settembre — che cosa non tornava, e com'è finita

Lettura dei registri del 15 settembre, non memoria. **Tutte chiuse in giornata**: quelle del
PM da sé, le altre con le sei disposizioni del PO della stessa sera.

| Che cosa non tornava | Come si è chiusa |
|---|---|
| Tre numeri di release in tre file (0.2, 0.3, `0.1.0`) | `HANDOFF.md` allineato a **0.3**. Resta noto e non allineato il numero di versione Python, che non ha mai seguito le release: è un asse diverso e cambiarlo è codice |
| `I-060` chiedeva il PM sdoppiato che D-130 ha abolito | Ritirata, superata da **D-130** |
| `I-014` chiedeva la regola che D-123 ha superato | Ritirata, superata da **D-123** |
| «Aperto» non distingueva più il lavoro dall'archivio: 60 righe su 63 | Triage in `2026-09-15-triage-input-aperti.md`, poi **D-131 … D-136**. Da 60 righe a **12 aperte più 4 regole** |
| La tavola 1 non risultava approvata da nessun atto, e D-116 ci poggiava sopra | **D-133**: le cinque tavole sono casi di prova, non elaborati da approvare. D-116 superata. La domanda era mal posta, e il PO l'ha corretta |
| `I-002` e `I-059` chiedevano allo spessore due cose incompatibili | **D-132**: lo spessore dice la gerarchia. Scostamento voluto dalla norma, dichiarato |
| `I-017` era soddisfatta da mesi senza che nessuno se ne fosse accorto | Chiusa con la misura sulla tavola 2: il prelievo sta 70 mm a destra e 85 mm sopra l'acquedotto |
| `DRAW-007` non ha cartella di collaudo | **Aperta.** Unico buco nella catena: `docs/collaudi/` porta DRAW-001…006-R1, 008 e 009. Va sistemata in un pacchetto |

### La correzione che il PO ha fatto al PM, e che vale più delle otto righe sopra

Gli ho portato queste stesse cose scritte con le sigle degli input, e me le ha rimandate
indietro: «per me non significano assolutamente nulla». Poi ha corretto la domanda sulla
tavola 1, che era mal posta alla radice: **non approviamo tavole, costruiamo un tool**; le
cinque tavole sono prove, un test passato può tornare a fallire, e non si generano tutte a
ogni giro perché lo stesso errore si paga cinque volte. È D-133, ed è la cosa che più cambia
il modo di lavorare da qui in avanti.

## 6. Igiene di git

**Stato al 15 settembre: 35 rami remoti oltre `main`.** Di questi **22 sono completamente
fusi** in `main` — il loro contenuto è tutto lì, cancellarli non perde niente — e **13
divergono**, cioè portano commit che su `main` non ci sono.

**La cancellazione non è eseguibile da una sessione Claude Code in questo ambiente:** il
proxy risponde **403** a `git push origin :ramo`, e il server GitHub MCP non espone un tool
che cancelli un ref. Va fatta dal PO, dall'interfaccia web di GitHub o da una copia locale.

I 22 fusi, sicuri da cancellare:

```
claude/disegnatoremep-interpreter-validation-6j9vk8   claude/draw-001-tavola1-qualita
claude/draw-004-assi-dorsali-tee                      claude/draw-005-contenuto-simboli-tavola1-r20hmg
claude/draw-005-r1-rifiniture-tavola1-3aad42          claude/draw-006-tavola2-semantica-v4n8o5
claude/draw-009-work-package-171cly                   claude/kind-wozniak-clrksw
claude/project-docs-first-pdf-obh471                  claude/ripresa-progetto-tavole-353zsb
claude/work-package-attivo-eijiol                     pm/close-draw005
pm/correct-draw005-r1                                 pm/draw-002-r1-costo-peso
pm/draw-002-routing-qualita                           pm/draw-003-terra-etichette
pm/draw-004-port-topology                             pm/generalize-draw005-r1
pm/register-pdc-port-spacing                          pm/register-po-input-draw004
pm/retro-roadmap-draw005                              pm/spec-draw005-r1
```

I 13 divergenti **non si cancellano senza deciderlo**, perché portano commit unici:
`archivio/fase-grafica-2026-08-03` (+72, è un archivio dichiarato: **si tiene**),
`claude/mep-pacchetto-e-collaudi-42itzv` (+214), `claude/disegnatoremep-main-resume-890881`
(+10), `claude/draw-002-routing-qualita-rhy6yu` (+4), `claude/gov-001-baseline-m6b0mn` (+3),
`claude/draw-003-terra-etichette` (+2), `pm/draw-001-active-work-package` (+2),
`pm/draw-006-component-semantics` (+5), `pm/draw-006-r1-revisione` (+5),
`pm/claude-entrypoint` (+1), `pm/draw-002-r2-riferimenti-visivi` (+1),
`pm/draw-002-r3-specifica-tecnica` (+1), `pm/draw-003-r1-priorita` (+1, l'unico il cui
titolo compare già su `main`).

Nota di governance: §3, obbligo 7, vuole un pacchetto esplicito per cancellare rami. Il PO
ha autorizzato la pulizia in sessione il 15 settembre; l'autorizzazione copre i 22 fusi.

## 7. Le trappole che costano tempo

Tre, ciascuna già pagata almeno una volta.

1. **Il `.pth` dell'installazione editable** (vedi §3.2). Ha già falsato un confronto.
2. **Uno SHA scritto dentro un file che vive su `main` nasce vecchio**, perché ogni ritocco
   al file sposta la testa. Vale per `ACTIVE_WORK_PACKAGE.md` — dove è già stato corretto — e
   **vale per questo file**: la riga `main` di §2 è stata trovata vecchia dal PM che è
   subentrato il 15 settembre, ed è stata trovata vecchia di nuovo un'ora dopo. Ora non porta
   più un numero. La base si dice per contenuto.
3. **Gli impianti 3 e 5 non producono tavola da prima di DRAW-009.** È la linea di partenza,
   non una regressione da inseguire. Il 4 invece è una regressione vera.

## 8. Che cosa fa il PM appena subentra

1. Legge questo file e `ACTIVE_WORK_PACKAGE.md`.
2. Controlla se il DEV ha aperto la PR di DRAW-010. Se sì, verifica secondo §3.
3. Se il PO è in sessione, l'unica cosa che aspetta ancora solo lui è la lista dei rami da
   cancellare (§6). Il triage degli input è **fatto**: dossier in
   `docs/pm/2026-09-15-triage-input-aperti.md`, esito in D-131 … D-136.
4. Prima di chiudere la sessione, **aggiorna questo file**.
