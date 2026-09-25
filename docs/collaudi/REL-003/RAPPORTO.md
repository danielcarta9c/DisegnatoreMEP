# REL-003 — i simboli nuovi: rapporto della prima parte

**Pacchetto:** `REL-003` (`ACTIVE_WORK_PACKAGE.md`) · **Ramo:** `claude/missing-symbols-uuzbhb` ·
**SHA iniziale:** `130be28` · **Base:** `main` dopo la fusione di `DRAW-018` (PR #57)

> **Le tavole, per prime** — il foglio dei simboli, `REL-003-simboli-nuovi.pdf`, in questa cartella:
> A3 a misura reale, due pagine. La prima mette ogni simbolo nuovo accanto a quello di oggi che gli
> somiglia, a scala di stampa; la seconda li ingrandisce due volte con il nome di ogni attacco. Lo
> scrive `foglio-simboli.py`, dalla libreria pubblicata.
>
> ✅ **Approvato dal PO il 25 settembre 2026** (I-128, D-185): «si i simboli che hai fatto vanno bene.
> fai i test e se va tutto bene al termine push su main».
>
> **Tavola di prova: non ancora.** Il PO ha chiesto di portare i simboli su `main` subito; le voci di
> catalogo e l'impianto di prova che li usa sono il resto del pacchetto, e lo dice il §4.

## 1. Che cosa c'è

Cinque simboli nuovi nella libreria, scritti dal generatore (`examples/graphics/build_symbols.py`) e
mai a mano, ciascuno con la sua fonte nel manifesto:

| simbolo | misura | attacchi | fonte |
|---|---|---|---|
| `heat-pump-air-water-large` — pompa di calore aria-acqua di alta potenza | 60 × 30 | mandata destra +5, ritorno destra +20 | SRC-030, SRC-031, SRC-032 |
| `gas-boiler-modular` — caldaia modulare a condensazione | 60 × 25 | mandata destra +5, ritorno destra +20 | SRC-033, SRC-009 |
| `solar-collector` — collettore solare | 40 × 25 | mandata destra +5, ritorno destra +20 | SRC-034, SRC-035 |
| `dhw-cylinder-twin-coil` — bollitore ACS a due serpentini | 25 × 55 | integrazione sinistra +7,5 e +17,5, solare sinistra +27,5 e +37,5, fredda sinistra +47,5, calda sopra, ricircolo destra +12,5, sonda destra +20 | SRC-036, SRC-037 |
| `fan-coil-ducted` — ventilconvettore canalizzato | 20 × 15 | ingresso e uscita sinistra +2,5 e +12,5 (D-167) | SRC-039, SRC-040 |

Le macchine hanno mandata e ritorno alle **quote di tutte le altre** (+5 e +20), il bollitore il
serpentino di integrazione **dove lo ha il bollitore a un serpentino**, il canalizzato le porte **dove le
hanno gli altri terminali**: nessuna convenzione in vigore è cambiata, e i 42 simboli di prima si
rigenerano identici. **UNI 9511 non ha nessuno dei cinque segni**; le forme vengono dagli schemi dei
costruttori e dei progetti pubblici, e il perché di ogni tratto sta nel rapporto della ricerca
(`docs/fonti/ricerche/reports/Simboli nuovi della prima release.md`, SRC-041).

**L'unico scostamento dalle fonti**, detto al PO prima del suo sì: nella caldaia modulare le fonti
mettono i due collettori sotto i moduli; qui la mandata corre sopra, per tenere le quote +5 e +20.

## 2. Come si è lavorato

- **Le fonti prima delle forme.** Quattro agenti di ricerca in parallelo, uno per famiglia, ciascuno in
  una cartella fuori dal repository (D-152). La sessione ha aperto i ritagli delle fonti da cui vengono
  le forme e ha **riscaricato ogni fonte registrata** dall'indirizzo citato, controllando la pagina: 13
  documenti, tutti `200`, e ogni pagina citata contiene quello che le note dicono.
- **Il foglio lo ha guardato la sessione prima del PO**, a misura di stampa: due ritocchi ne sono usciti
  — le lamelle della batteria della pompa di calore grande più fitte, perché rade si leggevano come una
  scaffalatura, e i collari del canalizzato più larghi e sporgenti, perché a 1:1 non si vedevano.
- **Il repository è pubblico**: dei documenti protetti ci sono solo i ritagli dei singoli segni, e delle
  due tavole che vietano la riproduzione (Division Energia, Comune di Parma) nessun ritaglio.

## 3. Verifiche

- **Le prove della libreria e del catalogo** (`tests/graphics`, `tests/catalog`): 343 passate. Valgono
  per ogni simbolo e quindi per i cinque nuovi: il corpo sta nel proprio riquadro e tocca ogni attacco
  che dichiara, il manifesto è coerente, e **rieseguire il generatore riproduce la libreria committata**.
  Il conto dei simboli pubblicati passa da 50 a 55, e la prova lo dice.
- **La suite completa**, due volte: vedi §3.1.
- `python -m ruff check src tests examples scripts` — `All checks passed!`
- `python -m mypy` — `Success: no issues found in 77 source files`

### 3.1 La suite

**Due giri, e il primo ha trovato una cosa.**

1. **Sul commit `247e932`**, subito dopo i simboli: `47 failed, 1699 passed, 24 skipped, 12 xfailed`
   in 851 s. Delle 47 rosse, 46 sono le stesse di `main` e **una era nuova**:
   `tests/acceptance/test_symbol_sheet.py::test_every_other_shipped_symbol_admits_all_four_rotations`.
   La prova elenca per nome i simboli che si disegnano solo diritti — macchine e accumuli — e le
   quattro macchine nuove non c'erano. Corretto nel commit `a7cb395`: aggiunte a quell'elenco e alla
   prova che pretende che restino diritte. Il ventilconvettore canalizzato gira come il
   ventilconvettore, e non ci sta.
2. **Sul commit `a7cb395`**, il codice finale — dopo, solo documenti —, in tre parti parallele, ciascuna
   in una copia del repository allo stesso commit perché i generatori che riscrivono la libreria non
   si pestassero:

```
gruppo A  tests/layout                                    41 failed, 368 passed, 15 skipped,  3 xfailed
gruppo B  rules, collaudo, piano, graph, model, io, ...    1 failed, 821 passed,              9 xfailed
gruppo C  graphics, catalog, acceptance, validation, cli   4 failed, 511 passed,  9 skipped
totale                                                    46 failed, 1700 passed, 24 skipped, 12 xfailed
```

   **Le 46 rosse sono le stesse di `main` (`130be28`), nome per nome**; nessuna nuova, nessuna tornata
   verde. `skip` e `xfail` sono **identici** a `main`, voce per voce. Le 10 passate in più sono le prove
   del corpo dei cinque simboli nuovi. Nelle due copie la libreria rigenerata dalla prova dei
   generatori è rimasta identica (`git status` pulito).
3. **Dopo i documenti** si è rieseguita la sola prova che legge la cartella `docs/`
   (`test_nessun_documento_dice_piu_che_il_regime_non_si_ricava_dalle_potenze`): passata.

## 4. Criteri di accettazione

Dal pacchetto, uno per uno, senza riscriverli.

- [x] **0. Le tavole, per prime** — **in parte**: il foglio dei simboli è andato al PO per primo, ed è
  approvato (I-128). La tavola di prova non c'è ancora: è il punto 5.
- [x] **1. Le fonti** — ogni simbolo nuovo dichiara la sua fonte nel campo `source` del manifesto; le
  fonti sono nel registro (SRC-030 … SRC-041), con i ritagli dei segni nelle note della ricerca.
- [x] **2. Le forme le ha approvate il PO**, guardando il foglio: I-128, D-185.
- [x] **3. La libreria si rigenera identica** — `tests/catalog/test_generated_fixtures.py` passa, e i
  cinque simboli passano le prove che valgono per tutti. *Il catalogo* non è ancora toccato: è il punto
  4 del pacchetto.
- [ ] **4. Capire sceglie la variante giusta** — **non fatto**: il resto del pacchetto.
- [ ] **5. La tavola di prova** — **non fatta**: il resto del pacchetto.
- [x] **6. La suite** — nessuna rossa nuova rispetto alle 46 di `130be28`, zero `skip` e zero `xfail` nuovi, `ruff` e `mypy` verdi (§3, §3.1).

## 5. Che cosa resta, ed è il resto di `REL-003`

1. **Le voci di catalogo** dei cinque simboli, e **il dato che distingue le varianti** perché Capire le
   possa scegliere: oggi Capire sceglie per mestiere e per attacchi, e tre simboli nuovi hanno mestiere e
   attacchi uguali a quelli del fratello (il pacchetto, *Dove siamo*).
2. **Il circuito solare**: fluido, colore della linea e corredo li decide il PO (D-184, punto 5). La
   ricerca porta quello che le legende fanno: un colore suo solo in una legenda pubblica (arancio,
   Parma) e in due costruttori (magenta); gli altri usano i colori del riscaldamento.
3. **La tavola di prova**, su un impianto che non è fra i cinque, con i cinque simboli.

## 6. Difetti noti e cose trovate fuori perimetro

- **Il foglio della libreria intera non si stampa**: `disegnatore-mep symbols-sheet` rifiuta più di 32
  simboli su un A3, e adesso sono 47. Il foglio di questo pacchetto si stampa sui soli simboli che
  servono. Non toccato.
- **`scripts/rasterize.sh` taglia il fondo del foglio**, come già detto in `DRAW-018`: le immagini si
  guardano dai PDF.
- **Il ricircolo del bollitore a due serpentini** sta a destra come in ogni accumulo sanitario della
  libreria (D-176); Vaillant e Cordivari lo mettono dal lato dei serpentini. Annotato, non cambiato.
- **Rami censiti**: `main` e `claude/missing-symbols-uuzbhb`, nessun altro sul remoto.
