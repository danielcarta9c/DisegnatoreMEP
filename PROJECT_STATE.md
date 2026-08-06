# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Interprete | Python 3.12, minimo 3.11 | |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv` |
| Test | **659 verdi, 22 parcheggiate** | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 39 pubblicati | Le 22 prove parcheggiate riguardano il **disegno**, non il contenuto, e portano scritto il motivo |
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
- [x] **L'assemblatore** — costruito. La fila dei pezzi la decidono i **vincoli dichiarati**
      da ogni regola rispetto ai mestieri degli altri pezzi, mai numeri di priorità. Se due
      vincoli si contraddicono si ferma e nomina le due regole. **Da collaudare in modo
      indipendente.**
- [x] **I cinque impianti di prova del committente** passano per la prima parte della
      catena. I grafi sono in `docs/prodotto/grafi-di-prova/`.

**Il prossimo lavoro:** le integrazioni che il PM darà dopo aver letto i cinque grafi, e poi
i pezzi da 1 a 3 fino al grafo definitivo. Dettagli in `HANDOFF.md` §7.

## Il confine del prodotto, che vale su tutto (D-104)

La skill emula un **disegnatore MEP**, non un progettista. L'ingegnere consegna uno schema a
livello di definitivo; la skill lo porta a livello esecutivo aggiungendo la ferramenta che
su una tavola esecutiva c'è sempre. **Non decide quanti pezzi ci vanno, non cambia lo schema
ricevuto, non dimensiona.** Una prescrizione normativa dice cosa deve avere l'impianto: non
autorizza la skill ad aggiungerlo.

## Next — i pezzi che restano

1. **Il pezzo «Capire»** — le istruzioni dell'agente che dal testo dell'ingegnere costruisce
   il grafo di prima stesura. Non esiste: oggi quella lettura è fatta a mano.
2. **Il contenuto delle regole**, esteso con il metodo delle fonti (D-103): bilanciamento,
   disconnettore, miscelatrice sanitaria, contabilizzazione, ritegno.
3. **Il collaudo indipendente dell'assemblatore.**
4. **La libreria dei simboli** — contenuto da completare.
5. **Il cartiglio.**
6. **La composizione** — da rifare: con gli accessori al posto giusto l'impianto completo
   non entra in larghezza su un foglio ordinario.
7. **I validatori e il cancello dell'occhio terzo.**

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
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
