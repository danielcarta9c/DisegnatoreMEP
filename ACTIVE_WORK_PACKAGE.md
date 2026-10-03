# REL-009 — La 1.3: la tavola del costruito

> **▶ Il pacchetto attivo, per l'ordine del PO** — «ho usato la skil su un caso reale. e abbiamo delle modifiche
> importanti da fare. merita una release 1.3» (I-191). Scritto il 3 ottobre 2026, sulla 1.2.2.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CORSO** — i punti 1–4 sono nella **1.3.0** (I-199, D-205); i punti **6 e 7** nella **1.4.0** (I-206, D-206 … D-209): la tavola del caso rifatta, approvata dal PO, e il tempo del disegna. Restano il limite d'intervento facoltativo (I-195) e la tavola di consegna del caso, che fa il PO (I-200).
**Base:** `main` dopo la PR #71 (la 1.2.2).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147). Una PR per punto, o per gruppo
di punti. La 1.3.0 è uscita alla fusione dei punti 1–4, per disposizione del PO (D-205); il caso rifatto è la PR
#74, e con il tempo del disegna è uscito nella **1.4.0**, col numero che il PO ha chiesto (I-206, D-209).

---

## Perché

Il primo caso reale (I-191) è un retrofit condominiale: sei pompe di calore al posto di caldaia e chiller, due
volani, due macrozone con otto collettori d'appartamento, un bollitore esistente in un altro locale. La tavola
**si lascia in centrale e si allega alla dichiarazione di conformità**: deve dire **che cosa è stato installato**
e **dove finisce l'intervento**. La 1.2.2 si è fermata al passo 4, per tre cose che non sa fare:

1. **togliere** un accessorio che una regola aggiunge e che sul costruito non c'è;
2. **disegnare** un accessorio installato che le regole non mettono, anche se il progettista lo nomina;
3. **distinguere** l'esistente dal nuovo, e il limite dell'intervento; e nel catalogo mancano dei pezzi.

Il documento della sessione di disegno porta i dati del cliente e **non entra nel repository**. Il grafo è
ricostruito anonimo: `docs/collaudi/REL-009/caso-reale-1/grafo-prima-stesura.json`.

## Dove siamo — misurato il 3 ottobre 2026, con la 1.2.2

```
$ python3 scripts/mep.py valida   .../caso-reale-1/grafo-prima-stesura.json
Il grafo si legge: 70 pezzi, 91 tubazioni, 6 reti; regime della centrale: over_35_kw.
$ python3 scripts/mep.py completa .../caso-reale-1/grafo-prima-stesura.json --out grafo-completo.json
Le regole hanno aggiunto 114 accessori; ... il grafo passa da 70 a 207 pezzi (+137).
Punti aperti: nessuno.
```

## Le cose da fare, in quest'ordine

### 1. R1 — togliere, spostare, «a bordo» (I-192): fondamentale

- **Togliere.** Il grafo porta l'elenco degli accessori che il progettista toglie, ciascuno con il suo motivo.
  Un accessorio si nomina con l'identificativo che ha nel grafo completo, che è stabile: lo stesso pezzo sullo
  stesso attacco ha sempre lo stesso nome. `completa` non lo posa, a ogni rilancio; non lo riporta come punto
  aperto; e lo elenca a parte, «tolti dal progettista», con il motivo. Una voce che non toglie niente si dice.
- **«A bordo», per singola macchina.** Il grafo dice, sul pezzo, le funzioni che quella macchina porta dentro; le
  regole lo leggono come leggono il catalogo. Dove una regola vuole il pezzo anche col bordo (la sicurezza di
  ogni generatore, D-182) `completa` lo dice, e per toglierlo si usa «togli» con il motivo.
- **Spostare** è togliere da un posto e dichiarare nell'altro (punto 2).
- Capire e `SKILL.md` dicono come si scrive, prima di `completa` e dopo, al passo 4.
- **Prove**: sul caso reale, i casi T1–T5 del documento — le 32 intercettazioni dei terminali, le valvole di
  sicurezza delle sei pompe, i separatori d'aria, i defangatori, il corredo del primario da portare sul
  secondario.

### 2. R2 — gli accessori dichiarati, com'è costruito (I-193)

- Capire §5: un accessorio **che il progettista nomina in un posto preciso** entra nel grafo di prima stesura; la
  lista della ferramenta resta per tutto il resto.
- Le regole **non lo duplicano**: si misura su ciascuno dei casi del documento — sfiato con valvola a sfera sul
  ritorno di ogni pompa, ritegno sull'uscita, sfiati sui volani, manometri e termometri sui montanti, riduttore di
  pressione.

### 3. R3 — le voci di catalogo che mancano (I-194)

Con il simbolo, che il PO approva **sulle tavole**:
1. il contabilizzatore di calore in linea, con le due sonde;
2. l'attacco predisposto, coppia mandata-ritorno tappata con un'etichetta libera («al solare termico»);
3. il confine di rete su acqua di riscaldamento, «da/verso impianto esistente», con etichetta;
4. il collettore d'appartamento con mandata e ritorno;
5. il giunto antivibrante, se il PO lo vuole disegnato;
6. il dosatore di polifosfati, a bassa priorità.

### 4. R4 — esistente e nuovo, e il limite d'intervento (I-195, I-196, D-202)

- `esistente` **per pezzo e per tratto**, oltre che per rete: è un dato **per le regole e per i diametri**, non per
  il disegno. **L'esistente si disegna come il nuovo**, e la tabella non cambia (D-202).
- **Le regole non aggiungono corredo sulle parti esistenti**, e `completa` lo dice una volta. *Proposta* — il
  documento dice «non applicare, o chiedere». La valvola di sicurezza di ogni generatore si disegna sempre.
- **Il limite d'intervento**: una linea a tratto e punto con la scritta, **facoltativa**. La tavola del caso non la
  porta: si fa dopo il punto 5.

### 5. Il caso, rifatto — **lo fa il PO**, nella sua sessione di lavoro con la 1.3.0 (I-200)

Il grafo anonimo con le scelte del progettista — quello che toglie, sposta, dichiara, l'esistente —, il piano, la
tavola: **al PO**. Restano aperte con il progettista le voci della §6 del documento (titolo e numero della tavola,
dati della tabella, temperature del secondario ACS, diametri sì o no, pompe di macrozona nuove o esistenti,
posizione del contabilizzatore).

### 6. Quello che il caso ha riportato (I-201 … I-205) — fatto, nella 1.4.0 (PR #74, D-206 … D-208)

Il PO, sulla tavola del caso fatta con la 1.3.0 nella sua sessione di lavoro. La tavola porta i dati del cliente e **non
entra nel repository**; il grafo per le prove si ricostruisce anonimo in `docs/collaudi/REL-009/caso-reale-2/`.

1. **Prima le autostrade, e disegnata l'autostrada non si tocca** (I-201, I-203). Il motore instrada nell'ordine dei nomi
   delle tubazioni: uno stacco che passa prima posa la valvola sulla quota dell'autostrada, e l'autostrada la scavalca.
2. **Le pompe in parallelo con lo stesso verso** (I-204): A2 lo dice per l'incolonnamento, non per il verso, e non ha un
   controllo sulla tavola.
3. **Le dorsali della distribuzione sono autostrade** (I-202, I-205): mandata e ritorno dopo le pompe secondarie corrono
   insieme, a colonne affiancate, fino ai collettori; i colori giusti.
4. **Il collettore con ritorno si raccorda ai terminali senza curve inutili** (I-205): gli attacchi del simbolo.
5. **La tavola del caso rifatta**, al PO.

### 7. Il tempo della skill (I-205) — fatto, nella 1.4.0 (D-209)

«La skill gira in 30 minuti buoni»: si misura dove va il tempo, dopo il punto 6. **Misurato** (`docs/collaudi/REL-009/RAPPORTO.md` §6): la posa d'inventario rileggeva tutte le tratte per ogni attacco; con un
indice, `disegna` sul caso passa da 107 a 3,4 s e sulle tavole agli atti scende sotto i due secondi, con le stesse
tavole. **I 30 minuti non stanno nel motore della 1.3.0** (da 1 a 7 s per tavola): per sapere dove vanno serve il
registro di una sessione vera, che è del PO.

### Note di controllo, dal documento

- I diametri del secondario ACS non si calcolano: c'è il salto termico ma non la potenza né la portata.
- Il grafo completo della 1.2.2 ha 207 pezzi e 228 tubazioni, per una tavola probabilmente in A1: con il punto 1
  se ne tolgono una trentina.

## Quello che resta di `BETA-001`

La copia è in `docs/plans/pacchetti/BETA-001.md`. Restano aperti, e si fanno dentro questo pacchetto quando
toccano: I-182 (le valvole di D-120 a 10 mm sulla tavola 1 dal piano); il modulo della segnalazione per i
collaboratori (`docs/beta/SEGNALAZIONE.md`); le tavole dei collaboratori, con il ciclo della prova del PO.

## Perimetro

**Dentro:** `skill/**`, `src/**`, `schemas/**`, il catalogo (`examples/layout/catalog/`), le regole
(`rules/hydronic/`), la libreria (`examples/graphics/build_symbols.py` → `assets/symbols/`), `tests/**`,
`docs/collaudi/REL-009/`, `releases/`, il registro, il registro delle decisioni (come proposte), `HANDOFF.md`,
questo file.

**Fuori:** i dati del cliente, in qualunque file; un contenuto MEP o una convenzione grafica decisi dalla sessione.

## Criteri di accettazione — per ogni PR

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: quelle che la PR cambia, prima e dopo, al PO.
1. **La suite**: `0 failed`; nessuno `skip` e nessuno `xfail` nuovi; `ruff` e `mypy` verdi.
2. **La regressione**: `confronta.sh` fra `main` e il ramo, ogni file cambiato spiegato.
3. **Ogni correzione ha la sua prova**, rossa sul commit di partenza.
4. **Gli input del PO nel registro** il giorno in cui arrivano.
5. **Nessun dato di cliente nel diff**: il comando di ricerca e il suo output vuoto.
6. **La release**: `tests/test_le_release.py` verde — la skill si carica (D-200).
