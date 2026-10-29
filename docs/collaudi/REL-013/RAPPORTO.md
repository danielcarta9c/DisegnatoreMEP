# REL-013 in anticipo — la distinta materiali per l'installatore

**Data:** 29 ottobre 2026 · **Stato:** sul ramo, **proposta** (D-213): il PO non ha deciso se la skill fa la distinta.
**Base:** `6e04487` (REL-012, fluidi e famiglie dell'aria-aria).

> **Da questo lavoro non esce nessuna tavola.** La distinta produce i **dati** delle tabelle per il foglio
> (`tabelle-del-foglio.json`); disegnarle sulla tavola è del pacchetto che porta nel motore le zone per le tabelle
> (`REL-012`, fase 1, punto 5). Quello che il PO può guardare oggi è l'Excel per l'installatore
> (`AA-01/distinta.xlsx`), accanto al computo del kit (`docs/input-pm/2026-10-29-kit-aria-aria/tavole/`).

## 1. Che cosa c'è

| dove | che cos'è |
|---|---|
| `rules/distinta/` | le regole come dato, sei file, ogni voce con `fonte` e `perche` (§2) |
| `src/disegnatore_mep/distinta/` | il modulo: grafo → distinta, uscite, comando |
| `src/disegnatore_mep/skill.py`, `skill/scripts/mep.py` | la registrazione del comando `distinta`: un sottocomando, una funzione, openpyxl fra le librerie facoltative |
| `examples/distinta/AA-01/grafo-completo.json` | il canalizzato del kit, con lunghezze, sezioni, portate e protezioni come dati del progettista |
| `tests/distinta/` | 100 prove |
| `skill/distinta/ISTRUZIONI.md` | quando l'agente la accende, che dati chiede, che cosa garantisce e che cosa no |
| `docs/collaudi/REL-013/AA-01/` | le uscite sul caso AA-01 |
| `docs/collaudi/REL-013/AA-01-con-dati-mancanti/` | lo stesso caso senza una lunghezza, una protezione e i dati di carica dell'unità esterna: le voci DA DEFINIRE e le domande |
| `docs/collaudi/REL-013/fai-il-grafo-aa01.py` | come è stato scritto il grafo d'esempio dal `grafo.json` e dal `dim.json` del kit |

**Spenta di default.** La fa solo `mep.py distinta`. Nessun altro modulo del motore importa la distinta (lo controlla
`test_la_distinta_la_fa_solo_il_suo_comando`); gli altri comandi non cambiano (la suite intera è verde come prima).

## 2. Le regole

| file | che cosa dice |
|---|---|
| `distinta.json` | le sezioni A, B, C, D, E, F, X, Z, G, H, V e i loro titoli; l'intestazione «prezzo a corpo, fisso e invariabile; quantità indicative; sopralluogo obbligatorio»; chi fornisce le apparecchiature (Nove C); le sei righe vuote di H |
| `lunghezze.json` | `L da quotare = (L + 1 m) × 1,15`, per eccesso a 0,5 m; i minimi per classe (frigo 12, condensa 10, bus 5, ramo d'aria 2); il cavo di collegamento che segue le linee frigorifere (+1 m) |
| `fluidi.json` | per fluido, che cosa costa a metro e a giunzione: flessibile in confezioni da 10 m senza giunte (0,5 m di sfrido, riserva 25%), curve, fascette, nastro, sostegni ogni 1,2 m, forature; rame pre-isolato, manicotti, collari, carica di refrigerante; PVC, curve, manicotti, collari, isolamento; cavi, protezioni, scatole, corrugati |
| `corredo.json` | per voce di catalogo (le dodici dell'aria-aria), il corredo di posa: sospensioni, giunto, raccordo della condensa, canalina e staffe, carotaggio, plenum porta-bocchetta, botole, controsoffitto, griglie, scatole 503, tracce |
| `attivita.json` | le attività a corpo (G), le opere generali del committente (Z), le varianti (V), con la condizione che le accende |
| `verifica.json` | le soglie: aria di mandata ≤ 3 m/s, ripresa ≤ 2 m/s, griglie di transito a 1,5 m/s; lunghezza massima della linea frigorifera; scritta sulla tavola contro la lunghezza quotata |

Il **corredo idronico non c'è**: pompa di calore, accumulo, circolatore e valvole escono nella sezione **X**, contati e
DA DEFINIRE. Il corredo di quelle voci è contenuto MEP che il PO non ha deciso, e le regole del corredo contro il manuale
Shenling sono `REL-011`: scriverlo qui sarebbe stato inventarlo.

## 3. Le misure

```
$ PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider
FAILED tests/piano/test_formato_del_piano.py::test_un_json_non_valido_dice_dove_si_e_rotto
1 failed, 2149 passed, 15 skipped, 10 xfailed in 63.71s

$ PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider tests/distinta
100 passed in 1.01s

$ ruff check src tests
All checks passed!

$ python3 -m mypy --strict --follow-imports=silent src/disegnatore_mep/distinta
Success: no issues found in 8 source files
```

Sul commit di partenza: `1 failed, 2049 passed, 15 skipped, 10 xfailed` — lo stesso fallimento ambientale, che corregge
un altro agente. Nessuno `skip` e nessuno `xfail` nuovi.

Il comando sul caso AA-01 (dal repository; lo stesso dalla skill costruita con `scripts/costruisci-skill.py`, con
`--regole rules/distinta`):

```
Distinta: 80 voci in 9 sezioni, 18 tratte; regole cfc42a99c0fd0a1a.
Verifica — 1 segnalazioni (la distinta non corregge):
  - T13, scritta sulla tavola: «P1-P2 · L 3 m», contro L 5 m da quotare
Avvisi:
  - T09 (Scarico condensa: UI-01 - SIF-01 - scarico): c-2 senza lunghezza; si considera compresa nei 7,6 m dati sul tratto.
  - T10 (Alimentazione unita' esterna: UE-01 - SZ-01 - QE-01): e-1a senza lunghezza; si considera compresa nei 15 m dati sul tratto.
  - T02, T04, T05 (aria di mandata): attraversamenti di parete non dati, assunti 1 per tratto (…)
  - T09 (condensa): attraversamenti di parete non dati, assunti 1 per tratto (…)
Nessuna voce DA DEFINIRE.
```

## 4. Il confronto col computo del kit

Il computo del kit è `lavoro/dimensionamento.py` (le stesse voci sono sulla M.02, `tavole/AA-01_M.02_anteprima.png`).
La prova è `tests/distinta/test_il_caso_aa01.py`: le 62 voci del kit, una per una, con la voce della distinta che le
fa.

**Coincidono 57 voci su 62**, con la stessa quantità: tutte le apparecchiature (A), le 18 tratte con le loro lunghezze
da quotare tranne una, il flessibile (4 confezioni: i 5 rami stanno interi in 3, la riserva del 25% ne vuole 4), il
rame (12 + 12 m), la riserva di R32 (0,2 kg), la condensa (10 m, 6 curve, 3 manicotti, 10 collari), i cavi (20, 15, 13
e 29 m), i corrugati (40 + 40 m), le assistenze murarie (F, tutte e 7) e le opere del committente (Z, tutte e 7).

**Cinque voci contano di più, e tutte in su:**

| kit | voce | kit | distinta | perché |
|---|---|---|---|---|
| B.5 | curve 90° Ø200 in lamiera | 4 | 5 | una per ramo; il kit le metteva alle sole uscite strette, scelte a mano |
| B.7 | fascette Ø200 | 36 | 40 | 8 per ramo (estremità e curva, anima e mantello): segue la curva in più |
| B.9 | sostegni del flessibile | 25 | 27 | L / 1,2 m per eccesso + 1 per ramo; il 25 del kit era scritto a mano |
| D.8 | isolamento anticondensa | 5 m | 10 m | su tutta la condensa: il tratto in controsoffitto lo sa solo la pianta |
| E.9 | cavo P1-P2 | 8,5 m | 10,5 m | il minimo di 5 m vale per tutto il bus, come dice `RAPPORTO.md` §7; il codice del kit lo dava ai soli termostati. La scritta del kit sulla tratta (L 3 m) e la distinta (5 m) non coincidono più, e la verifica lo segnala |

**Che cosa è diverso nella forma, e perché:**

- **C.3** (manicotti a brasare 1/4" e 1/2", 4): due righe da 2, una per diametro. La distinta ha 63 voci in A-Z, il kit 62.
- **G**: 12 attività invece di 11; le due dichiarazioni di conformità (lettera a e lettera c) sono due righe.
- **I testi sono generali**, non del caso: quello che il kit scriveva sulla commessa — «controsoffitto dei due
  disimpegni», «veletta nel soggiorno per B5», «S4a-S4b su TZ-04, Z4 zona di sfogo», «sifone uscita Ø40» — non viene
  da una regola ma dalla progettazione del caso, e la distinta non lo sa.
- **Le note**: il kit ne aveva 11, la distinta ne scrive 5 (la regola delle lunghezze, il prezzo a corpo, le velocità,
  la frase «la distinta non progetta»). Le altre sei erano note di progetto del caso (dove sta la macchina, la zona di
  sfogo, i due accessi): sono del progettista, e oggi il grafo non ha un posto per scriverle (§6, proposta 4).
- **Le griglie di transito** (Z.6): 5 come nel kit, ma contate una per bocchetta, con l'area efficace minima per
  bocchetta in nota (B1 0,05 m², B2 0,052, B3 0,039, B4 e B5 0,051). Il kit ne contava una per il soggiorno (due
  bocchette) e una per la porta fra i disimpegni: lo stesso numero per una strada diversa.
- **Le note dei pezzi**: il kit scriveva «verificare targa RXM60A (RXM60R: MCA 15,9 A, fus. 16 A)» accanto alla
  protezione. La distinta scrive la protezione che il progettista dà, e basta.
- **L'ordine delle tratte**: per fluido nell'ordine di `fluidi.json` (alimentazioni, poi collegamento); nel kit il
  collegamento UI-UE stava fra le due alimentazioni.

**Dove il kit era cablato a mano e la distinta lo prende come dato del progettista**, nel grafo d'esempio: i minimi delle
due linee di alimentazione (20 m sulla linea dell'unità esterna: `lunghezza_minima_m`, «posizione del quadro da
sopralluogo»), le pareti passate da B1, B3 e dalle linee frigorifere (`attraversamenti`), le protezioni (`protezione`),
i dati di carica dell'unità esterna, l'attacco condensa dell'unità interna, la misura delle bocchette, la centrale nel
kit del plenum (`compreso_in`). La lunghezza stimata di ogni tratto è quella della tabella delle tratte del kit.

**Le regole che riproducono il kit con un passo scelto dalla sessione**, da confermare: nastro (1 rotolo ogni 20 m),
curve della condensa (1 ogni 2 m + 1), manicotti della condensa (barre da 3 m), corrugati (per eccesso a 10 m), tracce
dal quadro (2,5 m per linea). Danno i numeri del kit sul caso AA-01; su un altro caso nessuno li ha provati. Il
`fonte` di ciascuna lo dice.

## 5. Le uscite

| file | per chi |
|---|---|
| `AA-01/distinta.xlsx` | l'installatore: foglio «Computo» (A-F, X, Z, poi G a corpo, H vuota, totale da compilare, V a prezzo unitario), e i fogli «Tratte», «Verifica», «Regole» (rif, regola, conto, fonte, perché), «Note e domande». **Solo valori, nessuna formula**, nessun prezzo |
| `AA-01/distinta.json` | tutto, con la regola e il conto di ogni voce |
| `AA-01/tabelle-del-foglio.json` | i dati per disegnare sulla tavola le tabelle della M.02 del kit (tratte, computo, attività, note): celle di testo già scritte, «≥» e «≤» come «min.» e «max.» perché il writer PDF è WinAnsi |
| `AA-01/distinta-calcoli.md` | il foglio dei calcoli, come per i diametri |

## 6. Limiti, e le decisioni del PO

**Limiti, detti come sono:**

1. **Nessuna tavola.** Le tabelle sul foglio aspettano l'API del motore.
2. **La skill che si carica non porta le regole.** Il modulo entra nella skill con il motore, ma `rules/distinta/` no:
   `scripts/costruisci-skill.py` (fuori dal perimetro di questo lavoro) va toccato con una riga perché scriva il fascio
   `dati/distinta.json`, che il comando cerca da solo. Oggi, dalla skill, serve `--regole`. Lo stesso per
   `skill/distinta/ISTRUZIONI.md`, che non è fra i riferimenti, e per `SKILL.md`, che non nomina il comando.
3. **openpyxl non è fra le dipendenze del progetto.** C'è in questo ambiente (3.1.5); `mep.py` prova a installarlo come
   fa con ezdxf, e se non ci riesce la distinta scrive un CSV e lo dice. Le prove sull'Excel girano solo dove c'è.
4. **Il corredo idronico non c'è** (§2).
5. **La verifica guarda le velocità**, non le perdite di carico né la prevalenza della macchina (il kit le calcolava:
   70 Pa a budget).
6. **Il grafo d'esempio non si valida col catalogo di questa base**: le dodici voci dell'aria-aria le porta un altro
   agente. La distinta legge il grafo dal JSON e non ne ha bisogno, ma `mep.py valida` oggi lo rifiuterebbe.
7. I campi `sezione`, `lunghezza_m`, `scritta` si leggono in testa alla tubazione o nelle `properties`; gli altri dati
   della distinta (`portata_m3h`, `attraversamenti`, `protezione`, `lunghezza_minima_m`, `materiale`) solo nelle
   `properties`. Se il modello li porterà in testa, va aggiunto il nome in `grafo.CAMPI_DEL_TRATTO`.

**Da decidere col PO:**

1. **D-213, il «Non progetti»**: la distinta così — spenta di default, comando esplicito, ogni numero con la sua regola
   — è quella che il PO vuole nella skill?
2. **Le cinque differenze in su** (§4): una curva per ramo, i sostegni per formula, l'isolamento su tutta la condensa,
   il minimo del bus su tutto il bus. O il kit, che sceglieva a mano.
3. **I passi scelti dalla sessione** (§4, ultimo capoverso).
4. **Le note di progetto**: un posto nel grafo per le note del progettista che la distinta riporta (oggi si perdono
   sei note del kit su undici).
5. **Le bocchette e le griglie del committente**: nel kit erano escluse dall'offerta; la regola le mette nella sezione
   Z per tutti i casi. Se cambia da commessa a commessa, serve un dato nel grafo.
6. **Il corredo idronico**, dopo `REL-011`.
