# Distinta materiali per l'installatore — istruzioni per l'agente

> **Proposta** (D-213, `REL-013`): il PO non ha ancora deciso se la skill fa la distinta. Finché non decide, la
> distinta esiste **solo come comando esplicito**, e queste istruzioni non sono nella skill che si carica su claude.ai.

## Quando la accendi

**Solo se il progettista la chiede**: «distinta materiali», «bill of quantities», «materiali per l'installatore»,
«computo per la quotazione». Mai di tua iniziativa, e mai per completare una tavola: la tavola si consegna senza.
Lo schema è lo stesso dei diametri (D-191): spenta di default, accesa su richiesta, ogni numero con la sua regola.

```
python3 scripts/mep.py distinta <grafo-completo.json> --out <cartella> [--regole <cartella o fascio>]
```

Esce con `0` se è completa, con `2` se ci sono voci **DA DEFINIRE** (con le domande stampate), con `1` se non si è
potuta fare. Scrive `distinta.xlsx` (o `distinta.csv` se manca openpyxl), `distinta.json`, `tabelle-del-foglio.json`
e `distinta-calcoli.md`, il foglio dei calcoli.

## Che dati chiedi al progettista

La distinta **non progetta**: conta e maggiora i dati che il progettista scrive nel grafo. Chiedi quelli che
mancano; non li stimi tu.

| dove | dato | che cos'è |
|---|---|---|
| ogni tubazione | `lunghezza_m` | la lunghezza **stimata** del tratto (pianta, sopralluogo); `0` se è un raccordo diretto (plenum sulla macchina, cablaggio di fabbrica). Basta su una tubazione del tratto: sezionatore e sifone non lo spezzano |
| ogni tubazione | `sezione` | «Ø200», «Ø6,35 (1/4")», «Ø32», «3G2,5», «2×0,75 (P1-P2)»: diametro, lati o cavo |
| mandata e ripresa | `portata_m3h` | per la verifica della velocità e delle griglie di transito |
| ogni tubazione | `attraversamenti` | quante pareti interne passa; se manca, la distinta ne assume uno per l'aria, la condensa e la linea del gas, e lo dice |
| linee di alimentazione | `protezione` | il dispositivo nel quadro, dalla targa della macchina: «Magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA» |
| un tratto incerto | `lunghezza_minima_m` | un minimo del progettista (il quadro da trovare in sopralluogo) |
| macchine | `marca`, `modello` | come per la tabella delle apparecchiature (D-190) |
| unità esterna | `refrigerante`, `precarica_fino_a_m`, `carica_aggiuntiva_g_m`, `lunghezza_max_m` | dalla scheda della macchina |
| unità interna | `attacco_condensa` | «VP20 (Øe 26)» |
| bocchette | `dimensione` | «400×200» |
| un pezzo nel kit di un altro | `compreso_in` | l'id del pezzo che lo comprende (la centrale nel kit del plenum) |

I campi del tratto (`sezione`, `lunghezza_m`, `scritta`) si scrivono sulla tubazione o nelle sue `properties`: la
distinta li legge in tutti e due i posti.

## Che cosa garantisce

- **Ogni quantità ha la sua regola**, con la fonte e il perché, e il conto fatto: nell'Excel (foglio «Regole») e in
  `distinta-calcoli.md`. Le regole sono dati, in `rules/distinta/`.
- **Le lunghezze** si quotano con `(L + 1 m) × 1,15`, per eccesso al mezzo metro, con i minimi del fluido (12 m frigo,
  10 m condensa, 5 m bus, 2 m ramo d'aria): in dubbio per eccesso, come vuole il PO.
- **Dove manca un dato, DA DEFINIRE e una domanda.** Mai un numero inventato.
- **L'Excel ha solo valori**, nessuna formula; chiede un prezzo **a corpo, fisso e invariabile**, con il **sopralluogo
  obbligatorio**; ha la sezione **H** vuota per le voci che aggiunge l'installatore e le varianti **V** a prezzo
  unitario. **Nessun prezzo**: li mette l'installatore.
- Lo stesso grafo dà sempre la stessa distinta.

## Che cosa non garantisce

- **Non progetta e non corregge.** La verifica dell'aria segnala una velocità oltre soglia, una scritta sulla tavola
  che dice un'altra lunghezza, una linea frigorifera oltre il massimo della macchina: **non cambia niente**. Riferisci,
  e il progettista decide.
- Non sa se le lunghezze sono giuste: sono del progettista. Il sopralluogo dell'installatore resta obbligatorio.
- **Le regole coprono l'aria-aria e l'elettrico del kit AA-01.** Una voce di catalogo senza corredo (oggi tutto
  l'idronico) o un fluido senza regole esce nella sezione **X**, contato e DA DEFINIRE: dillo al progettista, non
  completarlo tu.
- Non calcola perdite di carico né prevalenze.

## Come la consegni

Riporta al progettista, in quest'ordine: le **domande** (le voci DA DEFINIRE), le **segnalazioni** della verifica,
poi i file. Non riempire tu una voce DA DEFINIRE e non ritoccare l'Excel: si corregge il grafo, e si rilancia il
comando.
