# Distinta materiali per l'installatore — istruzioni per l'agente

> **Proposta** (D-213, `REL-013`): il PO non ha ancora deciso se la distinta resta nella skill. Finché non decide,
> la distinta esiste **solo come comando esplicito**, che lanci quando il progettista la chiede.

## Quando la accendi

**Solo se il progettista la chiede**: «distinta materiali», «bill of quantities», «materiali per l'installatore»,
«computo per la quotazione». Mai di tua iniziativa, e mai per completare una tavola: la tavola si consegna senza.
Lo schema è lo stesso dei diametri (D-191): spenta di default, accesa su richiesta, ogni numero con la sua regola.

```
python3 scripts/mep.py distinta <grafo-completo.json> --out <cartella> [--regole <cartella o fascio>]
                                [--sul-foglio tratte,computo,attivita,note] [--fornitura <scelte>|confermata]
```

Esce con `0` se è completa, con `2` se ci sono voci **DA DEFINIRE** (con le domande stampate), con `1` se non si è
potuta fare. Scrive `distinta.xlsx` (o `distinta.csv` se manca openpyxl), `distinta.json`, `tabelle-del-foglio.json`
e `distinta-calcoli.md`, il foglio dei calcoli.

## Quando la lanci: **prima** di `disegna`

Le tabelle del foglio — tratte, computo, attività, note — le scrive la distinta, in `tabelle-del-foglio.json`, e la
tavola le posa con `disegna --tabelle <cartella>/tabelle-del-foglio.json`. Se il progettista vuole le tabelle sulla
tavola, la distinta si lancia **prima** di `disegna` (dopo `completa`): lanciata dopo, la tavola esce senza.

**Il computo intero sul foglio porta di solito al formato A1**: ottanta righe di computo non stanno accanto a uno
schema che da solo starebbe in un A3. Se il progettista vuole un foglio più piccolo, sul foglio vanno solo tratte e
note, e il computo resta nell'Excel:

```
python3 scripts/mep.py distinta <grafo-completo.json> --out <cartella> --sul-foglio tratte,note
```

Senza `--sul-foglio` il file porta tutte e quattro le tabelle. Chiedilo al progettista quando chiede le tabelle
sulla tavola, con la tua proposta: «solo tratte e note sul foglio, il computo nell'Excel?».

## Che dati chiedi al progettista

La distinta **non progetta**: conta e maggiora i dati che il progettista scrive nel grafo. Chiedi quelli che
mancano; non li stimi tu.

| dove | dato | che cos'è |
|---|---|---|
| ogni tratto | `lunghezza_m` | la lunghezza **stimata** del tratto (pianta, sopralluogo); `0` se è un raccordo diretto (plenum sulla macchina, cablaggio di fabbrica) |
| ogni tubazione | `sezione` | «Ø200», «Ø6,35 (1/4")», «Ø32», «3G2,5», «2×0,75 (P1-P2)»: diametro, lati o cavo |
| mandata e ripresa | `portata_m3h` | per la verifica della velocità e delle griglie di transito |
| ogni tubazione | `attraversamenti` | quante pareti interne passa; se manca, la distinta ne assume uno per l'aria, la condensa e la linea del gas, e lo dice |
| linee di alimentazione | `protezione` | il dispositivo nel quadro, dalla targa della macchina: «Magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA» |
| un tratto incerto | `lunghezza_minima_m` | un minimo del progettista (il quadro da trovare in sopralluogo) |
| macchine | `marca`, `modello` | come per la tabella delle apparecchiature (D-190) |
| unità esterna | `refrigerante`, `precarica_fino_a_m`, `carica_aggiuntiva_g_m`, `lunghezza_max_m` | dalla scheda della macchina |
| unità interna | `attacco_condensa` | «VP20 (Øe 26)» |
| bocchette | `dimensione` | «400×200» |
| bocchette | `locale` | il locale che la bocchetta serve: «Soggiorno». Le griglie di transito si contano **per locale**, non per bocchetta: due bocchette nello stesso locale ne vogliono una. Se manca, la distinta legge il locale dall'`etichetta` (senza le parentesi); se manca anche quella, è una domanda |
| bocchette | `varco` | il locale ha un varco aperto verso la ripresa (un arco, una porta senza battente): «varco 1,5 m». Quel locale non vuole la griglia di transito; la verifica scrive l'area minima che il varco deve avere |
| un pezzo nel kit di un altro | `compreso_in` | l'id del pezzo che lo comprende (la centrale nel kit del plenum) |

I campi del tratto (`sezione`, `lunghezza_m`, `scritta`) si scrivono sulla tubazione o nelle sue `properties`: la
distinta li legge in tutti e due i posti.

**La lunghezza di un tratto spezzato basta su una tubazione.** Un tratto è la linea che l'installatore posa in un
pezzo, da macchina a macchina: il sezionatore sulla linea dell'unità esterna e il sifone sullo scarico della condensa
non lo spezzano. Quando il grafo lo scrive in due tubazioni (quadro – sezionatore e sezionatore – unità esterna;
unità interna – sifone e sifone – scarico), la lunghezza stimata del tratto intero si scrive in `lunghezza_m` e
basta su **una** tubazione del tratto: l'altra resta senza, e la distinta la considera compresa (lo dice fra gli
avvisi). Non dividere la lunghezza fra le due, e non scrivere `0` sull'altra se non è un raccordo diretto.

**Una lunghezza che manca non cancella quelle date.** Se un tratto non ha lunghezza, le voci a metro escono con la
somma dei tratti noti, e una riga DA DEFINIRE per il tratto che manca: la domanda è sul tratto, non sulla voce.

## La fornitura: una scelta dell'offerta, da confermare

Chi fornisce che cosa non lo dice il grafo. La distinta usa le scelte predefinite di Nove C — **apparecchiature
fornite da Nove C; bocchette, griglie e opere edili (velette, controsoffitti, botole, chiusure e ripristini) del
Committente; messa in servizio con Nove C** — e le **dichiara** fra le note e nell'uscita del comando come «da
confermare per questa offerta». Non sono DA DEFINIRE (le quantità ci sono) e il comando non esce con `2` per loro,
ma vanno chieste al progettista, con la proposta: «fornitura come al solito, macchine Nove C e bocchette del
Committente?».

Quando risponde, rilanci con `--fornitura`:

- `--fornitura confermata`: le scelte predefinite, confermate;
- `--fornitura apparecchiature=installatore,bocchette_e_griglie=installatore`: le scelte che cambiano (le altre
  restano le predefinite). Le scelte sono `apparecchiature` (Nove C, installatore, committente),
  `bocchette_e_griglie` e `opere_edili` (committente, installatore), `messa_in_servizio` (Nove C, installatore).
  Una voce del Committente che passa all'installatore va nella sezione dell'impianto (bocchette e griglie in B,
  opere edili in F) e si quota.

Le scelte predefinite stanno in `distinta.json`, `fornitura`: si cambiano lì solo se cambia l'offerta tipo di Nove C.

## Che cosa garantisce

- **Ogni quantità ha la sua regola**, con la fonte e il perché, e il conto fatto: nell'Excel (foglio «Regole») e in
  `distinta-calcoli.md`. Le regole sono dati, in `rules/distinta/`.
- **Niente codici interni nell'Excel e nelle tabelle del foglio**: i pezzi si chiamano con le **sigle dello schema**
  — le stesse che la tavola scrive —, o con la loro etichetta dove non hanno sigla; le fonti sono scritte per chi le
  legge («regola Nove C per i canali flessibili», «manuale di installazione del costruttore della macchina»). Gli id
  delle regole restano nel foglio dei calcoli e nel JSON, che sono la traccia del conto.
- **Il cartiglio**: dove committente, commessa o numero della tavola mancano (o sono «ND»), l'Excel e il foglio dei
  calcoli scrivono «DA DEFINIRE», come la tavola.
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

Riporta al progettista, in quest'ordine: le **domande** (le voci DA DEFINIRE), quello che è **da confermare** (la
fornitura), le **segnalazioni** della verifica, poi i file. Non riempire tu una voce DA DEFINIRE e non ritoccare
l'Excel: si corregge il grafo, e si rilancia il comando.
