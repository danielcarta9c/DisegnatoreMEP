# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Interprete | Python 3.12, minimo 3.11 | |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv` |
| Test | **844 verdi, 22 parcheggiate** | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 39 pubblicati | Le 22 prove parcheggiate riguardano il **disegno** (composizione da rifare) |
| Catalogo | 53 voci, 17 regole | |
| Release | Non disponibile | |

## Now — in corso

Il progetto costruisce la skill **un pezzo alla volta**, sulla logica del grafo (D-099).
Piano corrente: `docs/plans/2026-08-06-piano-costruzione-skill.md`.

- [x] **Il grafo, le sigle e l'indirizzo dei nodi (D-105)** — sigle collaudate; l'indirizzo
      per linea (`CP.01`, `CP.01.N.02`, civici degli stacchi) **collaudato e APPROVATO**
      il 7 agosto, con le 91 prove del collaudo adottate come regressione.
- [x] **Il regime della centrale e il tratto comune (D-106, pacchetto E)** — costruito,
      **collaudato a contesto separato**: respinto su quattro difetti veri, tutti corretti
      lo stesso giorno e verdi sulle prove del collaudo, adottate come regressione. Il
      regime (sotto/sopra i 35 kW) si **legge dalle potenze dichiarate dal progettista**
      (D-108); se le potenze non sono disponibili, vale il corredo minimo e la mancanza
      viene dichiarata. Il corredo di rete sta sul **ritorno generale, a monte della prima
      ripartizione**; dove il tratto comune non esiste esce un punto aperto. Il catalogo
      dichiara **cosa la macchina porta a bordo** e **da quale attacco la riserva si riempie**.
- [x] **La correzione C2** — lo scarico del bollitore sta sull'ingresso freddo, con la
      derivazione sulla rete fredda; la prova del collaudo è tornata verde senza essere
      ammorbidita.
- [x] **Le correzioni chieste dal PM a fine sessione** (7 agosto, sera):
      la camminata del ritorno generale **si apre sui rami**, e l'ibrido riceve il
      corredo sul tratto che ha davvero — nessuno dei cinque impianti ha più punti
      aperti; e il **regime si legge dalle potenze** che il progettista ha dichiarato
      (D-108), scritto nel modello dove lui lo vede: quattro impianti sotto i 35 kW, la
      cascata di tre macchine sopra.
- [x] **Il quinto impianto conserva tutti e tre i circuiti secondari** — il testo non
      nomina un collettore, quindi la lettura manuale usa la regola generale dei raccordi
      a N vie già introdotta nelle istruzioni di «Capire»: per tre rami, due ripartizioni
      sulla mandata e due confluenze sul ritorno. Rimossa la falsa domanda «il collettore
      ne serve due».
- [ ] **Il pezzo 1, «Capire»** — il collaudo indipendente lo ha **RESPINTO** il 7 agosto;
      le **tredici correzioni sono applicate** lo stesso giorno: sciolta la contraddizione
      sui tre circuiti con la regola generale dei raccordi a N vie, sostituiti gli esempi
      che ricalcavano le soluzioni dei testi di prova, aggiunto il regime ricavato dalle
      potenze e il criterio per cui una cosa non decisa si **chiede** invece di
      dichiararla. **Resta dovuta la prova nuova in camera pulita** — agenti nuovi,
      consegne conservate agli atti — e il collaudo che la giudica: le istruzioni sono
      cambiate, quindi la prova va rifatta da capo. È il primo lavoro della prossima
      sessione.

**Il prossimo lavoro:** la prova nuova del pezzo 1 in camera pulita — le istruzioni sono
già corrette — e il collaudo che la giudica; poi la traduzione in regole delle posizioni
§14-18. Dettagli in `HANDOFF.md` §7.

## Il confine del prodotto, che vale su tutto (D-104)

La skill emula un **disegnatore MEP**, non un progettista. L'ingegnere consegna uno schema a
livello di definitivo; la skill lo porta a livello esecutivo aggiungendo la ferramenta che
su una tavola esecutiva c'è sempre. **Non decide quanti pezzi ci vanno, non cambia lo schema
ricevuto, non dimensiona.** Il regime della centrale è un **dato del progettista**, e la
skill lo **legge** dalle potenze che lui ha dichiarato (D-108): sommarle e confrontarle
con la soglia non è dimensionare. Se le potenze non ci sono, il regime resta non
dichiarato, vale il corredo minimo, e quella è una domanda — non un'invenzione.

## Next — i pezzi che restano

1. **La prova nuova del pezzo 1 in camera pulita**, con agenti nuovi e **consegne agli
   atti** (il contratto aggiornato lo impone), e il collaudo che la giudica. Le tredici
   correzioni alle istruzioni sono già applicate.
2. **La traduzione in regole** delle posizioni chiuse con le fonti (bilanciamento,
   disconnettore, contabilizzatore — `DOVE_VA_CIASCUN_ACCESSORIO.md` §14-18), dentro il
   confine di D-104. Miscelatrice e ritegno sanitario hanno già le regole.
3. **La libreria dei simboli** — contenuto da completare (segno del rubinetto bloccabile).
4. **Il cartiglio.**
5. **La composizione** — da rifare: l'impianto completo non entra in larghezza su un
   foglio ordinario.
6. **I validatori e il cancello dell'occhio terzo.**

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `a136862` | **Quinto impianto corretto**: tutti e tre i circuiti secondari restano nel grafo di prima stesura; il collettore a due uscite non limita più la lettura del testo |
| `8d5ec99` | **Le tredici correzioni alle istruzioni dell'interprete**: regola generale dei raccordi a N vie, esempi che non contengono più le soluzioni, il regime dalle potenze, il criterio per chiedere. Tre prove nuove le inchiodano |
| `50cb842` | **Le quattro cose che l'interprete deve capire**, contate sulle condizioni delle diciassette regole: materiale per il giro di correzioni del pezzo 1 |
| `a75197b` | **Il regime si legge dalle potenze dichiarate** (D-108): i cinque impianti lo portano scritto, la cascata è l'unico sopra i 35 kW |
| `4433665` | **Il ritorno generale dell'ibrido c'era**: la camminata si apre sui rami e nessuno dei cinque ha più punti aperti; ritirata prima di scriverla la regola del filtro sul sanitario (D-107) |
| `da2c5f2` | **Collaudo del pacchetto E: RESPINTO, corretto lo stesso giorno.** Il bordo macchina soddisfa chi lo porta (mai il bordo altrui: la sicurezza del serbatoio non sparisce più); il vaso sanitario firmato dalla regola giusta; la fonte sul riscontro. 25 prove del collaudo adottate |
| `b7ea439` | **Collaudo dell'indirizzo dei nodi (D-105): APPROVATO.** 91 prove proprie più dure, adottate come regressione |
| `7187437` | Le tre correzioni del collaudo al contratto di consegna del pezzo 1 (campi del confronto, quarta classe, consegne agli atti) |
| `39259bc` | Il punto aperto del tratto comune si dice per quello che è, anche nel documento del grafo |
| `d370bd9` | **C2 corretta**: la riserva si svuota da dove si riempie; il catalogo dichiara il punto di riempimento; la prova del collaudo verde senza ammorbidirla |
| `08a23f0` | **Il pacchetto E (D-106)**: regime dichiarato, tratto comune, 17 regole aggiornate come dato, bordo macchina; due difetti d'ordine chiusi alla radice |
| `65fc7af` | **Collaudo del pezzo 1: RESPINTO**, verdetto registrato |
| `6334c7b` | **Il riscontro di D-106 sugli schemi Caleffi**, riga per riga con le citazioni |
| `2d48411`+ | Tre dei quattro difetti del collaudo corretti (C1, C3, C4) e le 29 prove del collaudo come regressione |
| `feee446` | **L'indirizzo dei nodi (D-105)**: linee, nodi numerati, civici; cinque grafi rigenerati |
| `a503ee4`, `f8fc476` | **Il pezzo 1 «Capire»** come istruzioni, provato in camera pulita |
| `3aa31de` | Le cinque righe mancanti degli accessori chiuse con le fonti (SRC-020..026) |
| `05d302b` | I cinque impianti del committente, letti e assemblati |
| `8d7796b` | **L'assemblatore**: la fila la decidono i vincoli dichiarati |
| `8e70438` | Gli accessori su stacco vanno dove vanno davvero (D-101) |
| `ecac2fa` | Ritirate tre regole dedotte dalla norma: la skill disegna, non progetta (D-104) |
| `167b5be` | Dove va ciascun accessorio, con la fonte (D-103) |
| `0f3bb63`…`ef6fc78` | Il grafo dell'impianto, le sue sigle e la passeggiata |
| `78838c7` | **Gate G0 superato**: progetto misto a quattro domini validato senza codice specifico per schema |
