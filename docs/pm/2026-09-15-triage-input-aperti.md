# Triage degli input del PO — il dossier che il PM porta, le chiusure che restano al PO

**Data:** 2026-09-15
**Chi lo ha scritto:** il PM, leggendo i registri e misurando, non a memoria
**A che cosa serve:** «aperto» nel registro degli input ha smesso di distinguere il lavoro
dall'archivio. Questo dossier propone una disposizione per ogni riga e porta accanto la
prova. **La chiusura di un input resta del PO** (`OPERATING_MODEL.md` §1.1): qui non se ne
chiude nessuno.

---

## 1. I numeri esatti

Contati sul file, non stimati.

| | |
|---|---|
| Righe totali | **63** (`I-001` … `I-063`, nessun buco, nessun doppione) |
| Archiviate nella tabella «Righe chiuse» | **3** — `I-001`, `I-003`, `I-004` |
| Righe nella tabella «Righe aperte» | **60** |
| …di cui già **dichiarate chiuse** nella propria casella di stato | **4** — `I-011`, `I-015`, `I-016`, `I-019` |
| …di cui una chiusa a metà | **1** — `I-009`, «chiuso nel merito, aperto nel prezzo» |
| …di cui con una proposta di chiusura già scritta e mai raccolta | **8** — `I-007`, `I-018`, `I-021`, `I-022`, `I-024`, `I-025`, `I-026`, `I-027`, `I-029` |

> Rettifica di un numero che avevo scritto io. `STATO-PM.md` §5 diceva «54 aperti su 63, 5
> chiusi» e «quattro input senza stato leggibile». Il conto giusto è quello qui sopra: gli
> input effettivamente chiusi sono **7** (3 archiviati + 4 dichiarati chiusi ma rimasti fra
> gli aperti), e le righe senza stato leggibile sono le **3** della tabella delle chiuse, che
> non ha la colonna — non quattro, e `I-005` ce l'ha eccome («IN CORSO»).

## 2. Come ho classificato

Quattro fonti, in quest'ordine: la casella di stato della riga; il rapporto di collaudo del
pacchetto che la riga cita; il decision log; una misura fatta oggi, dove serviva e dove
costava poco. Dove nessuna delle quattro dice qualcosa, la riga resta aperta e lo dico.

**Un limite dichiarato.** Per le 33 righe del gruppo A la prova è quella **della consegna**:
non ho rimisurato ciascuna sulla testa di oggi. Fra la consegna e oggi sono passati
`DRAW-007`, `DRAW-008` e `DRAW-009`, che hanno riscritto posa e instradamento. Ciò che le
presidia adesso è la regressione automatica sulla tavola 1 — ferma a 4 pieghe, 1 incrocio,
470,0 mm, organi D-120 15 su 15 — e la tavola 2 misurata il 14 settembre. Una rimisura
integrale è mezza giornata: si fa se il PO la vuole prima di chiudere.

---

## 3. A — Chiusura proposta, prova agli atti (33 righe)

La riga ha ottenuto ciò che chiedeva, la consegna è fusa, e il rapporto porta la misura.

| Consegnato da | Righe | Che cosa lo prova |
|---|---|---|
| `DRAW-001` | `I-007` *(per l'impianto 1)*, `I-018` | `docs/collaudi/DRAW-001/COLLAUDO.md`. `I-007`: il ritorno che superava la propria porta non c'è più, andata e ritorno a zero tratte e zero millimetri. `I-018`: 17 valvole su 20 a 2,5÷5 mm dal proprio attacco, contro 6 della base. **Resta fuori l'impianto 5**, presidiato da una prova marcata rossa |
| `DRAW-002-R3` | `I-021`, `I-022` | Tubo da 1177,5 a 597,5 mm; incroci da 12 a 2; pieghe da 27 a 10; nessuna tratta oltre tre pieghe. `docs/collaudi/DRAW-002/` |
| `DRAW-003` / `-R1` | `I-024`, `I-025` | `I-024`: il renderer non disegna più né linea né tratteggio di terra, e `tests/graphics/test_terra.py` fallisce se il segno rientra. `I-025`: sequenza posa → tubazioni → centratura → testi provata invariante |
| `DRAW-004` | `I-026`, `I-027`, `I-029` | Curve da 10 a 6, incroci da 2 a 1, tubo da 597,5 a 577,5 mm; la T che assorbe il gomito ha una prova generale |
| `DRAW-005` (PR #18) | `I-030`, `I-031`, `I-032`, `I-033`, `I-034`, `I-035`, `I-036`, `I-037`, `I-039` | `docs/collaudi/DRAW-005/RAPPORTO.md` nomina una per una queste righe con la propria prova: filtro a Y, confine di rete nel verso del fluido, glifi dritti, ordine e vicinanza delle valvole, tre accumuli distinti, riempimento unico, interasse PDC 15 mm, velo degli indirizzi |
| `DRAW-005-R1` (PR #21) | `I-041`, `I-042`, `I-043`, `I-044`, `I-045`, `I-046` | `docs/collaudi/DRAW-005-R1/RAPPORTO.md` e `metriche.py`, che misura esplicitamente `I-041`÷`I-046`. `I-043` è assorbita da `I-046`: una sola sicurezza di circuito, non tre |
| `DRAW-006` (PR #24) | `I-048`, `I-049`, `I-050` | Manometro con rubinetto a tre vie come componente a sé; funzioni interne dei compositi dichiarate in catalogo; la tavola 2 è diventata il caso visivo, ed è ciò su cui si lavora da allora |
| `DRAW-006-R1` (PR #24) | `I-052`, `I-053`, `I-054`, `I-055`, `I-056` | Ponte AF → ritorno tecnico senza funzioni duplicate; nessuno sfiato ACS per default; porta `drain` preferita; un solo gruppo EN 1487; assi attraverso raccordi e multivia |
| Misura di oggi | `I-017` | Vedi §7.1: sulla tavola 2 il prelievo non sta più accanto all'acquedotto |

**Una nota sulla riga `I-049`**, perché il suo seguito è vivo. `I-049` chiedeva che
l'intercettazione esterna non duplicasse quella che il gruppo di riempimento si porta
dentro, e il catalogo ha preso `carries_on_board` per dirlo. Quella riga è soddisfatta. Ma
`carries_on_board` **lo legge la regola di isolamento e non lo legge chi ordina gli
accessori**: è il difetto che ha messo lo scarico del bollitore dalla parte sbagliata del
ritegno, è D-129 del 14 settembre, ed è §D.3 di `DRAW-010`. Chiudere `I-049` non chiude
quello.

## 4. B — Già chiuse, ma archiviate nella tabella sbagliata (4 righe)

`I-011`, `I-015`, `I-016`, `I-019`. La loro casella di stato dice **CHIUSA** con la data e
ciò che le ha chiuse, e stanno nella tabella «Righe aperte». Non c'è niente da decidere: è
una correzione di archiviazione, e la propongo come tale. È anche la ragione per cui
`I-019` — la linea di terra — risulta chiusa mentre `I-024`, che chiede la stessa cosa,
risulta aperta.

## 5. C — Regole permanenti: non si chiudono, e non devono contare come lavoro (4 righe)

| Riga | Che cosa vincola |
|---|---|
| `I-023` | I quattro schemi del disegnatore sono materiale del collaudo del PM |
| `I-028` | Etichette e richiami non partecipano mai al confronto fra due pose |
| `I-038` | Il collaudo del PM verifica posizione e simboli, non solo l'instradamento |
| `I-047` | Ogni correzione specifica si traduce in una regola generale; gli esempi sono fixture |

Propongo uno **stato a sé — `REGOLA`** — che le tolga dal conteggio degli aperti senza
chiuderle. Sono vincoli da rispettare in ogni pacchetto, non lavoro che qualcuno finirà.

## 6. D — Superate da una decisione successiva (2 righe)

| Riga | Che cosa chiede | Che cosa dice oggi il modello |
|---|---|---|
| `I-014` | «Ogni sessione finisce su `main`, sempre» — **D-117** | **D-123** (31 agosto) l'ha superata: il lavoro entra in `main` solo tramite PR verificata. `OPERATING_MODEL.md` §3.2 lo dichiara per esteso, e il decision log marca D-117 «Superata da D-123» |
| `I-060` | Sdoppiare il PM in autore e revisore | **D-130** (14 settembre) ha abolito lo sdoppiamento: il PM è uno solo |

Vanno **ritirate dal PO**, oppure riscritte per dire ciò che resta vero: di `I-014`
sopravvive il divieto di rami paralleli sovrapposti; di `I-060` sopravvive che il PM è un
agente e non il PO.

## 7. E — Le sei righe che chiedono una parola del PO

Non sono lavoro: sono domande a cui solo lui può rispondere, e cinque su sei aspettano da
più di un mese.

### 7.1 `I-002` contro `I-059` — lo spessore del tratto non può dire due cose

`I-002` (5 agosto, **mai preso in carico da nessuno**; la sua casella dice ancora «aperto
da 4 giorni», scritta il 9 agosto e mai più toccata — oggi sono 41) riporta dalla fonte che lui ha
indicato che gli spessori sono **normati**: tubazione di progetto 0,50 mm, tubazione
esistente 0,25 mm, ogni altro segno grafico 0,50 mm salvo diversa descrizione. Oggi la
tavola usa 0,18 / 0,35 / 0,50 scelti internamente.

`I-059` (10 settembre) chiede di usare lo **spessore** per dire la **gerarchia**: stacchi
ciechi più sottili delle autostrade.

Le due cose usano lo stesso canale. Se lo spessore è normato, non è libero di portare la
gerarchia; se porta la gerarchia, la tavola si allontana dalla norma che lui stesso ha
indicato come «la simbologia giusta». **Domanda al PO:** lo spessore dice il **calibro
normato** o la **gerarchia**? E se la gerarchia, la si dichiara come scostamento voluto
dalla fonte?

*(Terza via che il PM segnala senza sceglierla: la gerarchia ha un canale ancora libero —
il colore dice il fluido, il tratto dice mandata o ritorno, lo spessore sarebbe il terzo. Ma
`I-059` porta con sé anche D-079, perché il pallino di derivazione è definito come quattro
volte lo spessore del tratto, e con spessori diversi va detto quale comanda.)*

### 7.2 `I-012` — la tavola 1 è approvata?

`I-012` e **D-116** dicono: si lavora su una tavola sola, l'impianto 1, e le altre quattro
si fanno **dopo che il PO ha approvato la prima**. D-116 è tuttora «Approvata» e non risulta
superata da nessuna decisione.

Di fatto si lavora sulla tavola 2 da `DRAW-006`, e `DRAW-010` misura gli impianti 2, 3 e 4.
Nel registro non c'è **nessun atto che approvi la tavola 1**: c'è `I-050` (9 settembre), che
dice di usare la tavola 2 come nuovo caso visivo, e che presuppone quell'approvazione senza
scriverla.

Non è una violazione: è un **cardine mai registrato**, e la 0.3 ci si appoggia sopra.
**Domanda al PO:** la tavola 1 è approvata? Se sì, lo registro e D-116 entra nella propria
seconda fase.

### 7.3 `I-008` — il 60 % di riempimento è ancora un obiettivo?

La distanza senza senso fra i gruppi è stata tolta alla radice in `DRAW-002-R3`: il
riempimento non compra più tubo. Il prezzo dichiarato è che il riempimento è sceso dal 41 al
36 %, contro il 60 % di questa riga. Arrivare al 60 % chiede una scelta di composizione —
dove stanno le macchine in altezza — che è sua. **Domanda:** il 60 % resta un obiettivo, o
la riga si chiude prendendo atto che il foglio pieno non è un criterio?

### 7.4 `I-020` — una centrale deve restare almeno su A3?

Da quando la quota di terra non è più un muro, l'impianto 1 entra su una **A4**, e la regola
dice di provare il formato più piccolo (D-058). Se una centrale debba comunque stare almeno
su A3 è una scelta di prodotto che nessuno ha mai fatto. Pesa adesso, perché §C di
`DRAW-010` sposta l'impianto 2 fra i componibili e l'impianto 2 compone **su A3**.

### 7.5 `I-013` — la priorità dell'agosto vale ancora?

«Le tavole prodotte finora sono da buttare, la priorità è portare avanti lo sviluppo sui
suoi input»: la riga indica `I-007`, `I-008` e `I-010` come la strada. `I-007` è in §3,
`I-008` è in §7.3, `I-010` è l'unico rimasto davvero aperto. La riga ha fatto il suo lavoro:
propongo di chiuderla o di riscriverla sulla strada di adesso.

### 7.6 `I-059` — le tre conseguenze da decidere prima

Oltre al conflitto di §7.1, la riga porta con sé un delta minimo leggibile in stampa su A3
dopo l'export PDF, e il rapporto con D-079. Va decisa prima di poter essere assegnata.

## 8. F — Restano aperte e vive (11 righe)

| Riga | Dove sta adesso |
|---|---|
| `I-063`, `I-062` | La posa a fasi e l'autostrada come fase. `DRAW-008` le ha attuate in parte; ciò che manca è §A di `DRAW-010` — la fase del tronco consegna ancora una posa con pezzi addosso |
| `I-061` | Attuata da `DRAW-009` per gli ingressi; resta fuori il prelievo, che è §D.1 di `DRAW-010` |
| `I-057`, `I-058` | Allineamento come primo atto, e peso della gerarchia nel costo. **Non assegnate.** Sono i candidati naturali del pacchetto dopo `DRAW-010` |
| `I-051` | L'ordine funzionale degli accessori. `DRAW-006-R1` l'ha reso un vincolo duro, ma D-129 ha trovato che non conta gli organi a bordo dei compositi: resta aperta finché `DRAW-010` §D.3 non chiude |
| `I-040` | L'audit dei 39 simboli. È **attività del PM**, non delegata al DEV, e il PO deve approvarla prima della 0.3. È il rischio 2 |
| `I-005` | La composizione della tavola. Oggi compongono l'impianto 1 e l'impianto 2; il 4 ha smesso, il 3 e il 5 non l'hanno mai fatto. È §B e §C di `DRAW-010` |
| `I-006` | Drawing Director. Ordine deciso dal PO: prima le metriche nel motore, poi il direttore. Non è ancora il suo turno |
| `I-009` | Chiusa nel merito — la sorgente è chi immette — **aperta nel prezzo**: correggere il verso ha fatto uscire dal foglio due impianti su tre. È lo stesso fronte di `I-005` |
| `I-010` | **Il vero orfano.** Dal 9 agosto: su un terzo delle tratte il verso mandata/ritorno resta indeciso e lo decide la geometria. Nessun pacchetto l'ha mai presa. Ho provato a misurarla oggi sulla geometria esportata e **non si misura da lì**: `supply` è un booleano già deciso, l'indecisione vive dentro la camminata. Serve uno strumento, e va assegnata |

---

## 9. Che cosa ho misurato oggi

### 9.1 `I-017` — il prelievo ACS non sta più accanto all'acquedotto

La riga, del 10 agosto: «quel simbolo si mette in genere nella zona della distribuzione,
perché di fatto anche lui fa parte della rete di distribuzione», e la causa scritta allora
era che il catalogo lo dichiarava confine e nient'altro.

Misurato su `docs/collaudi/DRAW-009/dopo/geometria.json`, la tavola 2 consegnata il 14
settembre:

| pezzo | x (mm) | y (mm) |
|---|---|---|
| `acquedotto` — l'ingresso AF | 187,5 | 208,5 |
| `bollitore` | 217,5 | 151,0 |
| `volano` | 232,5 | 68,5 |
| `utenze` — il prelievo ACS | **257,5** | **123,5** |

Il prelievo sta **70 mm a destra e 85 mm sopra** l'acquedotto, oltre il bollitore, in mezzo
alla distribuzione. La causa è stata tolta senza che nessuno collegasse le due cose:
`place.py` distingue oggi un **ingresso** — confine da cui il fluido entra, che si posa
vicino a chi serve — da un **prelievo** — «è l'ultimo passo della lettura e sta in fondo,
come ogni utilizzatore», D-098.

Ciò che resta della riga non è più la zona: è la **giacitura**. `utenze` è posato a
rotazione 90 con la bocchetta verso il basso, e la linea deve risalirci dentro pagando una
piega. È esattamente D-126 del 14 settembre ed è §D.1 di `DRAW-010`. Propongo quindi di
**chiudere `I-017` sulla zona**, annotando che il seguito vive nel pacchetto attivo.

### 9.2 I rami remoti, ricontati

35 oltre `main`: **22 completamente fusi**, **13 divergenti**. L'elenco di `STATO-PM.md` §6
è ancora esatto dopo il merge della PR #31 — `claude/kind-wozniak-clrksw`, che quella PR ha
portato, era già nell'elenco dei fusi.

---

## 10. Che cosa chiedo al PO

Sei cose, in ordine di quanto costa rispondere.

1. **I 33 di §3 e i 4 di §4**: li chiudo in blocco? Un no su una singola riga la tiene
   aperta e la rimisuro.
2. **Le 4 di §5** prendono lo stato `REGOLA` e smettono di contare come lavoro?
3. **`I-014` e `I-060`**: ritirate o riscritte?
4. **Lo spessore del tratto** (§7.1): calibro normato o gerarchia?
5. **La tavola 1 è approvata?** (§7.2) — è il cardine di D-116 e della 0.3.
6. **Il 60 % di riempimento** (§7.3) e **l'A3 minima** (§7.4): obiettivi o no?

Se rispondi a tutte, il registro passa da 60 righe aperte ad **al più 17** — le 11 vive di
§8 e le 6 di §7, di cui alcune si chiudono invece di diventare lavoro — e «aperto» torna a
voler dire qualcosa.

---

## 11. Le stesse sei domande, come vanno poste al PO

Il PO ha rimandato indietro la prima versione di questo elenco: «se mi parli di
`I-002` e `I-059` non ti seguo, non so nel dettaglio cosa ci sia». Aveva ragione, ed è
già scritto in `STATO-PM.md` §1 — *mostragli la tavola, non i criteri numerati*. Sotto c'è
la traduzione, ed è **questa** la versione che si porta al PO. Le sigle servono al PM per
ritrovare la riga, e restano di qua.

**1. Il quaderno delle tue richieste.** Ho ricontrollato una per una le sessanta richieste
che risultano ancora da fare. **Trentasette sono già fatte**, verificate e misurate quando
sono state consegnate: è il quaderno che non è mai stato aggiornato. Sono cose come il
filtro a Y col ramo inclinato, la linea di terra sparita dal foglio, la valvola di ritegno
disegnata a z, le valvole a un passo dagli attacchi delle macchine, un solo gruppo di
sicurezza sull'acqua fredda del bollitore, puffer bollitore e accumulo combinato come tre
oggetti distinti, le lettere dentro i simboli che restano dritte quando il simbolo ruota.
→ *Le depenno tutte in blocco, o c'è qualcosa che vuoi riguardare sul disegno prima?*

**2. Lo spessore delle linee — mi hai chiesto due cose che non stanno insieme.** Il 5 agosto
mi hai dato le tavole UNI come simbologia giusta, e lì lo spessore è **normato**: 0,50 mm
per la tubazione di progetto, 0,25 mm per l'esistente. Il 10 settembre mi hai chiesto di
fare gli stacchi ciechi **più sottili** delle autostrade, per far vedere a colpo d'occhio
chi è dorsale e chi è servizio. Se lo spessore è quello normato non può anche dire la
gerarchia: è un canale solo.
→ *Lo spessore dice il calibro normato, o la gerarchia? Se scegli la gerarchia, lo mettiamo
agli atti come scostamento voluto dalla norma.*

**3. La tavola 1 la consideri approvata?** Ad agosto avevi detto: si lavora su una tavola
sola, le altre quattro solo dopo che approvi la prima. Da settembre lavoriamo sulla tavola 2
e stiamo misurando la 3 e la 4 — ma da nessuna parte risulta che tu abbia detto «la tavola 1
va bene». Non è un problema di disegno: è che tutto il lavoro da settembre in poi poggia su
un tuo sì che non è mai stato scritto.
→ *Me lo dici adesso e lo registro.*

**4. Il foglio pieno.** Ne volevi il 60 %. Oggi siamo al 36 %, e il motivo è una correzione
che hai chiesto tu: prima il disegnatore comprava riempimento allungando i tubi, adesso non
lo fa più e i gruppi stanno alla distanza minima che gli accessori consentono. Per arrivare
al 60 % bisogna decidere **dove stanno le macchine in altezza**, ed è una scelta di
composizione tua, non una misura.
→ *Il foglio pieno ti interessa ancora, o lo togliamo dagli obiettivi?*

**5. Il formato minimo.** Da quando il pavimento non è più un muro invalicabile, la centrale
della tavola 1 **ci sta su un A4**, e la regola dice di provare sempre il formato più
piccolo che regge. La tavola 2 invece chiede un A3.
→ *Una centrale su A4 te la tieni, o il minimo per una centrale è A3 comunque?*

**6. Il verso di mandata e ritorno.** Ad agosto avevi segnalato tre difetti come priorità.
Due sono chiusi — i tubi che tornavano indietro e la distanza senza senso fra i gruppi. Il
terzo è ancora lì e **nessuno l'ha mai preso in mano**: su circa un terzo delle tratte il
verso mandata/ritorno non lo decide l'acqua, lo decide dove il pezzo è finito sul foglio.
Vuol dire che il colore di quel tubo è giusto per caso.
→ *Questo lo metto nel prossimo lavoro del disegnatore, o hai qualcosa di più urgente?*
