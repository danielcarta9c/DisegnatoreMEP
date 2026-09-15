# STATO PM — il documento d'ingresso del PM

**Aggiornato:** 2026-09-15
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

## 2. Dove siamo, al 15 settembre 2026

| | |
|---|---|
| `main` | `5ef4f14` (PR #31, 15 settembre) |
| Release dichiarata | **0.3 — generalizzazione, impianto 2** (`docs/plans/2026-09-03-release-plan.md`) |
| Pacchetto attivo | **DRAW-010** (`ACTIVE_WORK_PACKAGE.md`). **Non ancora consegnato al 15 settembre sera:** nessuna PR aperta, nessun ramo DEV spinto |
| Ultima consegna verificata | **DRAW-009**, fusa il 14 settembre, PR #27 |
| Suite su `main` | **10 rosse, 1470 verdi, 24 saltate, 11 xfailed**; `ruff` pulito; `mypy` 2 errori ereditati in `tests/layout/test_posa_a_fasi.py` |
| Tavola 1 | 4 pieghe · 1 incrocio · 470,0 mm · autostrada 0 pieghe · D-120 15 su 15 |
| Tavola 2 | 5 pieghe · 1 incrocio · 600,0 mm · nodi condivisi col tronco 0 · D-120 14 su 15 |
| Impianti 3, 4, 5 | **nessuno produce una tavola.** Il 4 la produceva prima di DRAW-009 |
| Prodotto in chat | **mai eseguito nel suo ambiente finale.** È il rischio 1, il più vecchio |

Il verdetto completo su DRAW-009, con tutte le misure e i comandi, sta in
`docs/pm/2026-09-14-review-pr27-draw009.md`. È anche il modello di come si scrive un
verdetto.

## 3. Che cosa aspetti dal DEV, e come lo verifichi

DRAW-010 chiede sedici criteri. Quando arriva la PR:

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

In ordine di quanto pesano. I rischi numerati stanno in `PROJECT_STATE.md`.

1. **L'anello della fase del tronco** (rischio 16). È la causa a monte di quasi tutto:
   tiene la tavola 2 sul ripiego, ha costretto ad allargare `is_valid` (rischio 19) e con
   ogni probabilità è ciò che blocca gli impianti 3, 4 e 5. **È §A di DRAW-010.**
2. **Il prodotto non gira in una chat vera** (rischio 1). Il più vecchio e il meno toccato.
   La 0.3 non si può dichiarare finita senza una prova verticale in una chat pulita.
3. **L'audit della libreria dei simboli** (rischio 2), che il PO deve approvare prima della
   0.3.
4. **L'ordine degli stacchi non ha un padrone** (rischio 17). Oggi vale per topologia sulle
   due tavole; diventa esigibile su un impianto che lo violi.
5. **Lo squilibrio fra quadranti della tavola 2**, da 3,74 a 32,50. Nessuna voce di costo lo
   insegue. Il PO ha visto la tavola e non l'ha sollevato.
6. **Gli attacchi pari di un collettore**: la scambiabilità va dichiarata nel catalogo, non
   dedotta. Pacchetto a sé, da aprire se il PO lo vuole.

## 5. Cold eye review del 15 settembre — le incoerenze trovate

Fatte da una lettura dei registri, non da memoria. Quelle che il PM può chiudere da sé sono
già chiuse; le altre chiedono il PO.

### Chiuse in questa passata

- **Tre numeri di release diversi in tre file.** `HANDOFF.md` diceva 0.2, `PROJECT_STATE.md`
  0.3, `pyproject.toml` `0.1.0`. `HANDOFF.md` è stato allineato a **0.3**, che è ciò che il
  piano di release e il lavoro effettivo dicono. **Resta noto e non allineato** il numero di
  versione Python, che non ha mai seguito le release dichiarate: è un asse diverso, e
  cambiarlo è una modifica di codice che va in un pacchetto.

### Che chiedono il PO

- **`I-060` chiede il contrario di `D-130`.** L'input del 10 settembre chiede di **sdoppiare**
  il ruolo PM; la decisione del 14 settembre lo **abolisce**. L'input è ancora aperto, quindi
  il registro chiede una cosa e il modello operativo ne fa un'altra. Va chiuso o riscritto
  dal PO.
- **`I-014` chiede il contrario di `D-123`.** «Ogni sessione finisce su `main`, sempre»: è la
  regola **D-117**, che **D-123 ha superato** il 31 agosto. L'input è ancora aperto.
- **Il registro degli input non distingue più il lavoro dall'archivio.** Il dossier di
  triage è pronto e sta in `docs/pm/2026-09-15-triage-input-aperti.md`: ogni riga ha una
  disposizione proposta e la prova accanto. **Aspetta soltanto sei risposte del PO** (§10 del
  dossier). La chiusura di un input è sua (§1.1), quindi il PM non ne ha chiuso nessuno.

  I numeri corretti, contati sul file: **63 righe**, di cui **3** archiviate fra le chiuse,
  **60** nella tabella delle aperte — e di queste **4** dicono già «CHIUSA» nella propria
  casella (`I-011`, `I-015`, `I-016`, `I-019`). Gli input effettivamente chiusi sono quindi
  **7**, non 5. Le righe senza stato leggibile sono **3**, non quattro: sono quelle della
  tabella delle chiuse, che non ha la colonna. `I-005` uno stato ce l'ha.

  Rispondendo alle sei domande, il registro scende ad **al più 17 righe aperte**.

### Trovate nella passata di triage del 15 settembre

- **La tavola 1 non risulta approvata da nessun atto**, e `D-116` — «si lavora su una tavola
  sola finché il PO non approva la prima» — è tuttora «Approvata» e mai superata. Di fatto si
  lavora sulla tavola 2 da `DRAW-006`. Non è una violazione: è un cardine mai registrato, e
  la 0.3 ci si appoggia sopra. Basta una parola del PO.
- **`I-002` e `I-059` chiedono allo spessore del tratto due cose incompatibili**: il calibro
  normato (0,50 / 0,25, dalla fonte che il PO ha indicato) e la gerarchia (stacchi ciechi più
  sottili). Nessuno dei due è assegnabile finché il PO non sceglie il canale.
- **`I-017` è soddisfatta da mesi e nessuno se n'era accorto.** Il prelievo ACS non sta più
  accanto all'acquedotto: sulla tavola 2 sta 70 mm a destra e 85 mm sopra, oltre il
  bollitore, perché `D-098` distingue l'ingresso dal prelievo. Ciò che resta della riga è la
  giacitura, che è già `D-126` e §D.1 di `DRAW-010`.

### Da sistemare in un pacchetto

- **`DRAW-007` non ha cartella di collaudo.** `docs/collaudi/` porta DRAW-001…006-R1, 008 e
  009; il 007 è stato fuso senza rapporto agli atti. È l'unico buco nella catena.

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
2. **Un SHA scritto dentro `ACTIVE_WORK_PACKAGE.md` nasce vecchio**, perché il file vive su
   `main` e ogni suo ritocco sposta la testa. Si definisce la base per contenuto, non per
   numero.
3. **Gli impianti 3 e 5 non producono tavola da prima di DRAW-009.** È la linea di partenza,
   non una regressione da inseguire. Il 4 invece è una regressione vera.

## 8. Che cosa fa il PM appena subentra

1. Legge questo file e `ACTIVE_WORK_PACKAGE.md`.
2. Controlla se il DEV ha aperto la PR di DRAW-010. Se sì, verifica secondo §3.
3. Se il PO è in sessione, gli porta le sei domande del dossier di triage
   (`docs/pm/2026-09-15-triage-input-aperti.md` §10) e la lista dei rami da cancellare (§6):
   sono le due cose che aspettano solo lui.
4. Prima di chiudere la sessione, **aggiorna questo file**.
