# Verbale di collaudo — le due correzioni di fine sessione

**Data:** 7 agosto 2026. **Collaudo:** indipendente, a contesto separato.
**Repository:** `/home/user/DisegnatoreMEP`, HEAD `82b8374`.
**Prove del collaudo:** `tests/collaudo/test_collaudo_correzioni_fine_sessione.py`
(43 verdi, 11 marcate `xfail(strict=True)` — sono i difetti, falliscono apposta).

Nota di metodo: durante il collaudo il ramo si è mosso sotto di me. Due commit
(`fa7b9e4`, `82b8374`) sono arrivati a lavoro iniziato. Il verbale giudica lo
stato a HEAD `82b8374`; dove una cosa è stata chiusa in corsa lo dico.

Le sei prove rosse della suite completa riguardano il documento pubblicato del
quinto impianto, non ancora rigenerato. Non c'entrano con queste due correzioni
e non le ho toccate.

---

## VERDETTI

| | |
|---|---|
| **Correzione 1 — la camminata del ritorno generale** | **RESPINTA** — 2 difetti |
| **Correzione 2 — il regime letto dalle potenze (D-108)** | **RESPINTA** — 3 difetti |

Nessuno dei cinque difetti è grande. Tutti e cinque sono veri, riproducibili, e
riguardano cose che le due correzioni **affermano** di aver sistemato.

---

# Correzione 1 — la camminata del ritorno generale

## I criteri che ho scritto prima di leggere il codice

| | Criterio | Esito |
|---|---|---|
| C1.1 | Nessuno dei cinque impianti ha punti aperti sul corredo di rete | **superato** |
| C1.2 | Il corredo esce una volta sola, tutto sullo stesso attacco | **superato** |
| C1.3 | Rimescolando pezzi, tubazioni e reti nel file, il punto non si sposta | **superato** (8 rimescolamenti × 5 impianti) |
| C1.4 | Rinominando le tubazioni il punto non si sposta | **superato** |
| C1.5 | Con tre macchine (il ritorno si apre due volte) il punto sta a monte di tutte e due le ripartizioni | **superato** |
| C1.6 | La camminata supera la confluenza e arriva alla ripartizione | **superato** |
| C1.7 | Con due tratti comuni in fila si prende quello vicino alle macchine | **superato** |
| C1.8 | Con un anello la camminata termina e dà una risposta | **superato** |
| C1.9 | Dove il tratto comune non esiste davvero resta un punto aperto | **superato** |
| C1.10 | **Il tratto scelto porta davvero l'acqua di tutti i generatori** | **NON superato** (impianto 4) |
| C1.11 | **A topologia identica, il punto non cambia col nome delle macchine** | **NON superato** (con un anello) |

Il nocciolo della correzione regge: la camminata si apre davvero sui rami, i
cinque impianti non hanno più punti aperti, e l'ordine del file non decide
niente — l'ho verificato più a fondo di quanto facesse la prova di casa
(otto rimescolamenti invece di tre, su tutti e cinque gli impianti invece che
su tre, più la rinomina delle tubazioni).

Quello che non regge è **il criterio con cui la camminata sceglie**. La
camminata considera «comune» un tratto da cui si arriva a tutti i generatori
risalendo. Le regole invece dicono un'altra cosa, e la dicono per iscritto: sul
tratto comune *«passa tutta l'acqua che torna, quindi un pezzo solo protegge
ogni generatore»* (motivazione del defangatore). Le due cose non coincidono, e
su due grafi su sette che ho provato danno risposte diverse.

## Difetto 1 — l'impianto 4 non ha il tratto che gli è stato attribuito

**Dove.** `examples/prova/prova-4-ibrido-pdc-caldaia.json` — l'ibrido, cioè
l'impianto per cui la correzione esiste.

**Cosa succede.** Il corredo viene posato sul tratto fra il volume tecnico e la
ripartizione verso le due macchine (la tubazione `p5`). Quel tratto **non porta
l'acqua che la caldaia rimanda dallo scambiatore sanitario**: quando la
deviatrice manda la caldaia sul sanitario, l'acqua fa il giro
caldaia → deviatrice → scambiatore → raccordo di ritorno → caldaia, e non passa
mai per `p5`. Togliendo `p5` dal grafo, il circuito della caldaia si chiude lo
stesso.

**Perché è un difetto.** Per il vaso, il manometro e il riempimento la
posizione regge lo stesso: la pressione è la stessa dappertutto. Per il
**defangatore** no: la sua ragione scritta è che lì passa tutta l'acqua che
torna, e per la caldaia in produzione sanitaria non ci passa. Il messaggio di
commit afferma testualmente che quel tratto *«porta tutta l'acqua che torna
dall'impianto»*: non è vero.

E c'è un secondo lato, più scomodo. Prima della correzione questo impianto dava
quattro punti aperti. Adesso dà una posa, in silenzio, senza che niente avverta
il progettista. La correzione dichiara di lasciare il punto aperto «dove il
tratto comune non esiste davvero»: qui, per la caldaia, non esiste, e il punto
aperto non c'è.

**Come si riproduce.**
`.venv/bin/python -m pytest tests/collaudo/test_collaudo_correzioni_fine_sessione.py -k "porta_davvero_l_acqua and prova-4"`

## Difetto 2 — con un anello, il punto lo decide il nome delle macchine

**Dove.** La camminata in `src/disegnatore_mep/rules/context.py` (`run_from`) e
la scelta in `src/disegnatore_mep/rules/engine.py` (`_common_run_anchor`).

**Cosa succede.** Costruisco un ritorno ad anello: due macchine, il collettore
di ritorno si richiude su se stesso. Stessa identica topologia, cambio solo il
nome delle due macchine:

- macchine chiamate `gen-a` / `gen-b` → il corredo va sul tratto **giusto**;
- macchine chiamate `zeta` / `alfa` → il corredo va **a valle della prima
  ripartizione**, su un tratto che porta solo la parte di acqua che la prima
  macchina non ha preso.

**Perché succede.** La scelta parte dal primo generatore in ordine alfabetico e
prende il primo tratto condiviso che incontra risalendo. Con un anello, «il
primo che incontro» dipende da chi parte. Il nome di un pezzo non è struttura.

**Perché è un difetto.** È esattamente il caso che la regola dice di non avere:
il corredo sul ramo di una macchina sola. Ed è la stessa specie di fragilità che
il progetto ha già chiuso due volte altrove (l'ordine del file, l'ordine
alfabetico dei file delle regole) — qui è rientrata dalla porta dei nomi dei
componenti.

**Come si riproduce.**
`.venv/bin/python -m pytest tests/collaudo/test_collaudo_correzioni_fine_sessione.py -k anello`

## Cosa suggerirei di guardare (non è una correzione, è dove guardare)

Il tratto comune andrebbe scelto con la stessa definizione che le regole
scrivono: **il tratto senza il quale il circuito di ogni generatore non si
chiude più**. È una proprietà della struttura sola, non dipende da chi parte né
da come si chiamano i pezzi, e dove nessun tratto la soddisfa dà da sé il punto
aperto. La prova `generatori_che_si_chiudono_senza` nel file del collaudo la
calcola in venti righe.

---

# Correzione 2 — il regime letto dalle potenze (D-108)

## I criteri che ho scritto prima di leggere il codice

| | Criterio | Esito |
|---|---|---|
| C2.1 | I cinque impianti dichiarano il regime: quattro sotto, uno sopra | **superato** |
| C2.2 | Il regime dichiarato corrisponde alla somma delle potenze del testo del committente, rifatta da zero | **superato** |
| C2.3 | Le regole non sommano mai le potenze dei pezzi | **superato** (900 kW su ogni pezzo, in due forme: non si muove niente) |
| C2.4 | Senza dichiarazione vale il corredo minimo, identico a un impianto dichiarato piccolo | **superato** |
| C2.5 | La soglia è inclusiva: 35 kW esatti sono piccola centrale | **superato** |
| C2.6 | Le istruzioni dicono di ricavare il regime e di non chiederlo | **superato** |
| C2.7 | Nessun documento del kit dice più il contrario | **superato** — ma vedi l'osservazione 1 |
| C2.8 | **Le potenze da cui il regime è stato letto stanno nel modello** | **NON superato** |
| C2.9 | **Il conto copre tutte le macchine che generano calore** | **NON superato** (impianto 3) |
| C2.10 | **Il documento che legge il committente non si contraddice** | **NON superato** |

Il principio è giusto e applicato: il regime si legge, non si chiede, e le
regole quel campo lo leggono e basta. Ho rifatto il conto da zero rileggendo il
testo originale del committente, impianto per impianto, e i cinque regimi
scritti sono quelli giusti (24 · 15 · 8 · 34 sotto, 105 sopra). Ho anche
verificato che nessuna somma avvenga dentro le regole: 900 kW scritti su ogni
pezzo non muovono un accessorio.

Quello che manca è la **tracciabilità** e la **copertura dei casi di mezzo**.

## Difetto 3 — il conto non è nel modello, e il metro contraddice le istruzioni

**Dove.** I cinque grafi `examples/prova/prova-*.json`.

**Cosa succede.** Ogni impianto dichiara `plant_regime`, ma **nessun componente
porta la potenza**: tutti hanno `properties` vuote. Il conto che giustifica il
regime (`# Due macchine da 12 kW: 24 kW, sotto la soglia`) vive in un commento
Python del generatore delle fixture.

**Perché è un difetto.** Le istruzioni dell'interprete ordinano il contrario, e
lo dicono a parole nel loro esempio: *«la potenza detta dal testo compare in due
posti: trascritta in `properties`, e usata per ricavare `plant_regime`»*. I
cinque grafi la mettono in uno solo. E quei cinque grafi non sono grafi
qualunque: il loro README dice che sono il **metro congelato** con cui si
giudicherà l'interprete quando esisterà. Un interprete che segue le istruzioni
produrrà un grafo diverso dal metro che lo misura.

È la stessa specie di contraddizione dentro il kit che il 7 agosto ha fatto
fermare la prova in camera pulita. Lì era fra due documenti; qui è fra le
istruzioni e le fixture.

**Effetto pratico.** Chi apre il modello vede la conclusione e non vede il dato
da cui è stata tratta. Può cambiare il regime, non può verificarlo.

**Come si riproduce.**
`.venv/bin/python -m pytest tests/collaudo/test_collaudo_correzioni_fine_sessione.py -k potenze_da_cui`

## Difetto 4 — la somma su alcune macchine sole, in silenzio

**Dove.** `skill/capire/ISTRUZIONI.md` §4.6, e l'impianto 3.

**Cosa succede.** La regola ha due soli rami: «somma le potenze» e «il testo non
dà le potenze → ometti il campo e chiedi». Manca il caso di mezzo: il testo dà
la potenza di una macchina e non quella di un'altra.

**Non è teorico, è già successo.** L'impianto 3 ha **due** macchine che il
catalogo classifica come generatrici di calore: la pompa di calore aria-acqua e
lo scaldacqua in pompa di calore, che dichiara anche lui `heat_generation`. Il
testo dà la potenza solo della prima (8 kW); dello scaldacqua dà il volume, 200
litri, non la potenza. La somma è stata fatta su una macchina sola, il regime è
stato scritto lo stesso, e la mancanza non è stata detta da nessuna parte.

**Perché è un difetto.** Qui l'esito è giusto lo stesso, perché il margine è
larghissimo. Ma la regola tace proprio dove serve parlare: su un impianto vicino
alla soglia lo stesso silenzio ribalta il corredo. L'impianto 4 sta a 34 kW su
35 — un solo dato mancante e il conto non significa più niente. La stessa lacuna
copre il caso senza generatori, dove la somma vale zero e cade sotto la soglia
senza che nessuno se ne accorga.

**Come si riproduce.**
`.venv/bin/python -m pytest tests/collaudo/test_collaudo_correzioni_fine_sessione.py -k "solo_alcune or porta_una_potenza"`

## Difetto 5 — il documento del committente si contraddice sul regime

**Dove.** `docs/prodotto/grafi-di-prova/CONFRONTO-2026-08-07.md`, il documento
scritto per il committente.

**Cosa succede.** Nella stessa pagina:

- al punto 1: *«Nessuno dei cinque testi dichiara il regime, e senza
  dichiarazione vale il corredo minimo — quello della piccola centrale»*;
- più sotto, la sezione *«Il regime: letto dai testi, non chiesto a te»* con la
  tabella delle potenze, e il quinto impianto dichiarato **sopra** i 35 kW, con
  il corredo da grande centrale.

La correzione ha scritto la sezione nuova e ha lasciato in piedi la frase
vecchia. Le due si contraddicono, e la prima è quella che il committente legge
per prima.

**Come si riproduce.**
`.venv/bin/python -m pytest tests/collaudo/test_collaudo_correzioni_fine_sessione.py -k confronto_per_il_committente`

---

# Osservazioni non bloccanti

**1 · La contraddizione dello schema, chiusa in corsa.** All'apertura del
collaudo, la descrizione di `PlantRegime` nel sorgente e il documento delle
regole del committente dicevano ancora *«mai calcolato… nemmeno sommando le
potenze che il testo nomina»*, cioè l'opposto di D-108. L'avevo registrata come
difetto. È stata chiusa dal commit `fa7b9e4` mentre lavoravo, su segnalazione di
due camere pulite indipendenti. La registro lo stesso, perché faceva parte dello
stato in cui la correzione era stata consegnata: la correzione del 7 agosto
aveva cambiato il comportamento e lasciato indietro tre documenti su cinque. La
prova che lo inchioda è nel file del collaudo, e oggi passa: resta come
regressione.

**2 · La radice normativa della soglia, sulle pompe di calore.** D-108 giustifica
il conto dicendo che la soglia dei 35 kW «ha radice normativa (SRC-012,
R.1.A.1)». Quel capitolo parla di **potenza dei focolari**, cioè di macchine a
combustione; e il registro delle fonti, alla riga SRC-013, dice testualmente che
«la Raccolta R esclude» il caso a pompa di calore. Il quinto impianto — tre
pompe di calore da 35 kW, nessun focolare — è dichiarato sopra soglia su una
radice che per quelle macchine non c'è. La scelta di avere due regimi anche per
le pompe di calore è di D-106 e non la discuto qui; discuto che la si motivi con
una norma che quelle macchine le esclude. Va detto in una riga, non va corretto
di corsa.

**3 · Nessuno avverte a valle quando il regime non è dichiarato.** «La mancanza
va detta» è affidato interamente alle istruzioni dell'interprete, che ordinano di
scriverlo in `assumptions`. Il resto della catena — regole, relazione, controlli
— non nomina mai il regime mancante. È coerente con il disegno, ma se un modello
arriva senza `plant_regime` da una strada diversa dall'interprete, prende il
corredo minimo in silenzio.

---

# Come far girare le prove del collaudo

```
cd /home/user/DisegnatoreMEP
.venv/bin/python -m pytest tests/collaudo/test_collaudo_correzioni_fine_sessione.py
```

Atteso oggi: **43 verdi, 11 xfail**. Le undici xfail sono i cinque difetti: sono
marcate `strict=True`, quindi il giorno in cui un difetto viene chiuso la prova
diventa rossa e obbliga a togliere il segno. Ogni `xfail` porta scritto per
esteso il difetto che documenta.

Suite completa con le prove del collaudo dentro: **881 verdi, 22 saltate,
11 xfail, 6 rosse** — le sei rosse sono quelle già note del documento pubblicato
del quinto impianto, identiche a prima che aggiungessi qualcosa.

Non ho modificato niente in `src/`, nella documentazione o negli artefatti
pubblicati.

Due avvertenze pratiche per chi raccoglie questo lavoro:

- il file delle prove è stato committato da un'altra sessione (`7325928`) mentre
  lavoravo; nell'albero di lavoro c'è una mia modifica non committata che
  **corregge la motivazione del difetto 3** (una frase di D-108 ammette una
  lettura diversa da quella che le avevo dato, e l'ho tolta). Va tenuta la
  versione dell'albero di lavoro;
- `ruff check` è pulito sul file. `ruff format` no, ma non lo è su 75 file del
  repository: il progetto non lo usa.
