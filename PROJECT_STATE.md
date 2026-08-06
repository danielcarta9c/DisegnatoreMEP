# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Interprete | Python 3.12, minimo 3.11 | |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv` |
| Test | **714 verdi, 23 parcheggiate** | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 39 pubblicati | 22 prove parcheggiate riguardano il **disegno**; la ventitreesima e' il difetto C2 (scarico del bollitore), aperto con correzione progettata |
| Catalogo | 51 voci, 14 regole | |
| Release | Non disponibile | |

## Now — in corso

Il progetto costruisce la skill **un pezzo alla volta**, sulla logica del grafo (D-099).
Piano corrente: `docs/plans/2026-08-06-piano-costruzione-skill.md`.

- [x] **Il grafo e le sue sigle** — nodi, archi, sigle assegnate camminando dalle sorgenti.
- [x] **Il vocabolario delle proprietà** — approvato.
- [x] **Le regole degli accessori** — quattordici regole generali, collaudate.
- [x] **Un attacco, una tubazione** (D-100) — il modello rifiuta due tubazioni sullo stesso
      attacco. Dove due si incontrano c'è un pezzo che le unisce, con la propria sigla:
      **confluenza** se due diventano una, **ripartizione** se una si sdoppia.
- [x] **Gli attacchi di servizio** (D-101) — le macchine dichiarano scarico, sfiato e sede
      sonda come i cataloghi dei costruttori li dichiarano. Un accessorio a stacco va lì, o
      su una derivazione saldata sul tubo quando la macchina non ce l'ha. Chiuso il debito
      che D-094 aveva congelato.
- [x] **L'assemblatore** — costruito e **collaudato in modo indipendente** (6 agosto, sera):
      respinto su due difetti veri, entrambi corretti lo stesso giorno (il doppio «attaccato
      alla macchina» ora ferma nominando le regole; la saturazione non dipende più
      dall'ordine del file). Le prove del collaudo sono regressione in `tests/collaudo/`.
- [x] **I cinque impianti di prova del committente** passano per la prima parte della
      catena. I grafi sono in `docs/prodotto/grafi-di-prova/`.
- [x] **L'indirizzo dei nodi (D-105)** — costruito: ogni linea idraulica ha nome e numero
      (`CP.01`, `RP.01a`), ogni pezzo un indirizzo (`CP.01.N.02`), gli stacchi i civici
      (`CP.01.N.02.1`). I cinque grafi sono rigenerati con la convenzione nuova.
      **Da collaudare da contesto separato.**
- [x] **Il pezzo 1, «Capire»** — costruito come istruzioni (`skill/capire/`) e provato in
      camera pulita sui cinque testi originali: quattro letture su cinque identiche a
      quelle manuali, arco per arco; le divergenze del quinto tutte dichiarate. Verbale in
      `skill/capire/PROVA-2026-08-06.md`. **Da collaudare da contesto separato.**

**Il prossimo lavoro:** i collaudi indipendenti dei due pacchetti nuovi (indirizzo dei
nodi; pezzo 1), la correzione C2 progettata nell'appendice del piano (lo scarico del
bollitore sull'ingresso freddo), e il giro di correzioni alle istruzioni del pezzo 1
raccolto dai rapporti di camera pulita. Dettagli in `HANDOFF.md` §7.

## Il confine del prodotto, che vale su tutto (D-104)

La skill emula un **disegnatore MEP**, non un progettista. L'ingegnere consegna uno schema a
livello di definitivo; la skill lo porta a livello esecutivo aggiungendo la ferramenta che
su una tavola esecutiva c'è sempre. **Non decide quanti pezzi ci vanno, non cambia lo schema
ricevuto, non dimensiona.** Una prescrizione normativa dice cosa deve avere l'impianto: non
autorizza la skill ad aggiungerlo.

## Next — i pezzi che restano

1. **I collaudi indipendenti** dell'indirizzo dei nodi (D-105) e del pezzo 1: costruiti e
   provati, ma per D-083 senza verdetto separato non sono «fatti».
2. **La correzione C2** (scarico del bollitore sull'ingresso freddo): progettata
   nell'appendice del piano, con la prova parcheggiata che la aspetta.
3. **Le correzioni alle istruzioni del pezzo 1** raccolte dalla prova in camera pulita,
   con una prova nuova ad agente nuovo dopo ogni correzione.
4. **La traduzione in regole** delle cinque posizioni chiuse con le fonti (bilanciamento,
   disconnettore, miscelatrice, contabilizzatore, ritegno): il materiale è in
   `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md` §14-18, dentro il confine di D-104.
5. **La libreria dei simboli** — contenuto da completare.
6. **Il cartiglio.**
7. **La composizione** — da rifare: con gli accessori al posto giusto l'impianto completo
   non entra in larghezza su un foglio ordinario.
8. **I validatori e il cancello dell'occhio terzo.**

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `2d48411`+ | **Tre dei quattro difetti del collaudo corretti** (C1 determinismo della saturazione, C3 punto aperto invece del crollo, C4 doppio attaccato-alla-macchina) e le 29 prove del collaudo adottate come regressione in `tests/collaudo/`; C2 progettato e parcheggiato col motivo |
| `feee446` | **L'indirizzo dei nodi (D-105)**: linee idrauliche battezzate, nodi numerati, diramazioni con lettera, civici degli stacchi; documento del grafo per linea e cinque grafi rigenerati; 27 prove nuove |
| `a503ee4`, `f8fc476` | **Il pezzo 1 «Capire»** come istruzioni (`skill/capire/`), provato in camera pulita su cinque agenti freschi: 4/5 letture identiche alle manuali, verbale in `PROVA-2026-08-06.md` |
| `3aa31de` | **Le cinque righe mancanti degli accessori** chiuse con le fonti (SRC-020..026): bilanciamento, disconnettore, miscelatrice, contabilizzatore, ritegno — solo posizioni (D-104) |
| `05d302b` | **I cinque impianti del committente**, letti e assemblati. Nove famiglie di pezzi aggiunte come dato senza toccare il motore; due raccordi nuovi — confluenza e ripartizione — che la modellazione chiedeva |
| `8d7796b` | **L'assemblatore**: la fila dei pezzi la decidono i vincoli dichiarati, non l'ordine alfabetico dei nomi dei file. Sul primario il termometro non finisce più dopo un organo di chiusura |
| `8e70438` | **Gli accessori su stacco vanno dove vanno davvero**: attacco di servizio della macchina, o derivazione sul tubo. Chiuso il debito di D-094 |
| `ecac2fa` | **Ritirate tre regole dedotte dalla norma**: la skill disegna, non progetta (D-104) |
| `167b5be` | **Dove va ciascun accessorio**, con la fonte: Raccolta R e manuali dei produttori, accessorio per accessorio (D-103) |
| `48dbeba` | Gli attacchi delle macchine si leggono dai cataloghi, non si chiedono al PM (D-102) |
| `6fc1ca7` | Un attacco, una tubazione (D-100) e l'avvio degli attacchi di servizio |
| `1c75a92` | Le tre correzioni chieste dal collaudo finale della sessione precedente |
| `0f3bb63`…`ef6fc78` | Il grafo dell'impianto, le sue sigle e la passeggiata |
| `c385d7e`…`5bfcbc1` | Il vocabolario delle proprietà dei componenti |
| `da67b9d`…`c3f0a97` | Piano di layout eseguito: dodici task |
| `8e2b664` | Fase grafica integrata in `main` |
| `987aeec` | Prima libreria trasversale di simboli |
| `78838c7` | **Gate G0 superato**: progetto misto a quattro domini validato senza codice specifico per schema |
| `d0d85ba` | Bootstrap del pacchetto e della toolchain |
| `0bb4ef8` | Design concettuale completato e formalizzato |
