# Distinta materiali per l'installatore — istruzioni per l'agente

> **Proposta** (D-213, `REL-013`): il PO non ha ancora deciso se la distinta resta nella skill. Finché non decide,
> la distinta esiste **solo come comando esplicito**, che lanci quando il progettista la chiede.

## Quando la accendi

**Solo se il progettista la chiede**: «distinta materiali», «bill of quantities», «materiali per l'installatore»,
«computo per la quotazione». Mai di tua iniziativa, e mai per completare una tavola: la tavola si consegna senza.
Lo schema è lo stesso dei diametri (D-191): spenta di default, accesa su richiesta, ogni numero con la sua regola.

La distinta è **un documento a parte**, in PDF, con la copertina e l'impaginazione dei report Nove C — niente Excel,
e **niente tabelle della distinta sulla tavola**: sulla tavola restano la tabella delle apparecchiature e la legenda
(I-232, I-233). Si lancia dopo `completa`, prima o dopo `disegna`: la tavola non cambia.

## Le domande: al passo 2, prima del primo lancio

Le domande della distinta si fanno **nello stesso giro** di quelle del disegno, non dopo che la
distinta è uscita con le voci «DA DEFINIRE». Subito dopo `completa`:

```
python3 scripts/mep.py distinta <grafo-completo.json> --domande
```

Non scrive niente e non serve `--out`. Compone la distinta in memoria e stampa, in parole, un dato
per riga: che cosa chiedere, a quali pezzi o tratti manca (con le sigle della tavola) e in che campo
del grafo va la risposta. Le domande vengono dagli stessi punti del calcolo che fanno le voci «DA
DEFINIRE»: se `--domande` non chiede un dato, il documento non lo lascerà da definire. Stampa anche:

- **per la verifica**: i dati senza i quali la verifica non si fa (le portate dell'aria, la lunghezza
  massima della linea frigorifera); non fanno voci da definire, ma chiedili nello stesso giro;
- **senza regole nella distinta**: i pezzi e i fluidi che la distinta non sa contare (sezione X);
  una risposta del progettista non basta, e glielo dici;
- **da confermare**: la fornitura dell'offerta (vedi sotto).

Esce con `2` se ci sono domande, `0` se non ce n'è nessuna. Porta le domande al progettista nel
messaggio del passo 2 — se non sai ancora se vuole la distinta, sotto «se vuoi la distinta, mi
servono anche:» —, trascrivi le risposte nel grafo, rilancia `completa`, e solo allora `distinta`.
Marca e modello il progettista può lasciarli aperti di proposito: restano «DA DEFINIRE», e va bene.

## La skill dei report Nove C, accanto

Il PDF lo fa il motore della skill **`nove-c-report`**, che deve essere installata accanto a questa. Non è dentro
questa skill: la si trova e se ne passa la cartella con `--report`. Su claude.ai le skill stanno sotto `/mnt/skills/`;
cercala così, e usa la cartella che contiene `references/nove_c_report_engine.py`:

```
find /mnt/skills ~/.claude/skills -type d -name nove-c-report 2>/dev/null
```

Se non esce niente, cercala in tutto il disco (`find / -type d -name nove-c-report 2>/dev/null`).

```
python3 scripts/mep.py distinta <grafo-completo.json> --out <cartella> --report <cartella di nove-c-report>
                                [--fornitura <scelte>|confermata] [--regole <cartella o fascio>]
```

Esce con `0` se è completa, con `2` se ci sono voci **DA DEFINIRE** (con le domande stampate), con `1` se non si è
potuta fare. Scrive nella cartella:

- **il documento per l'installatore**, `<commessa>_Distinta_materiali_<impianto>.pdf` (il nome viene dal
  cartiglio; senza commessa e senza titolo, `distinta.pdf`), e accanto le sue pagine in PNG
  (`<nome>-pagine/`);
- `distinta.json` (lo legge la pianta, `pianta --distinta`) e `distinta-calcoli.md`, il foglio dei calcoli con il
  conto e la regola di ogni numero, per chi controlla;
- `tabelle-del-foglio.json`: le tabelle che il motore saprebbe posare sulla tavola. **Non passarle a `disegna`**:
  il flusso della skill non le usa più.

**Se la skill dei report non c'è** — non la trovi, oppure il comando dice che il motore non si carica (una libreria
che manca) — la distinta lo dice e scrive lo stesso contenuto in **Markdown**, `<nome>.md`. Dillo al progettista:
il PDF si fa dove la skill `nove-c-report` è installata.

## Il controllo del PDF: lo fai tu, sempre

Il comando chiama il controllo finale dei report — il riempimento delle pagine, la griglia, le stringhe vietate
(nessun prezzo, nessun dato interno), la numerazione — e stampa i suoi avvisi e i percorsi delle pagine in PNG.
**Guarda le pagine una per una** (si aprono come immagini): un capitolo spezzato male, un titolo solo in fondo alla
pagina, un testo tagliato in una cella, una pagina mezza vuota. Un avviso che a vista è un falso positivo lo dici al
progettista; uno vero lo riferisci, non lo correggi ritoccando il PDF: si corregge il grafo, e si rilancia.

## Che cosa c'è nel documento

La copertina dei report Nove C **senza le card dei KPI**, **senza la pagina «Chi siamo»**, e sette capitoli:

1. l'impianto e le avvertenze — **a corpo, fisso e invariabile**; **quantità indicative**; **sopralluogo
   obbligatorio**; la fornitura, da confermare o confermata; la distinta non progetta;
2. le tratte — sezione, materiale, portata, L stimata e L da quotare —, e la verifica dell'aria e delle linee;
3. il computo per sezioni (A apparecchiature, B aria, C frigorifero, D condensa, E elettrico, F assistenze murarie,
   X senza regola, Z opere del Committente), una tabella per sezione;
4. le attività a corpo (G);
5. le varianti a prezzo unitario (V) e le righe vuote delle voci che aggiunge l'installatore (H);
6. le voci da definire e le domande, quello che è da confermare, le segnalazioni e le assunzioni;
7. le note e le regole usate, dette in parole.

## Che dati chiedi al progettista

La distinta **non progetta**: conta e maggiora i dati che il progettista scrive nel grafo. Chiedi quelli che
mancano — `--domande` te li elenca —; non li stimi tu.

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
Committente; messa in servizio con Nove C** — e le **dichiara** fra le avvertenze e nell'uscita del comando come
«da confermare per questa offerta». Non sono DA DEFINIRE (le quantità ci sono) e il comando non esce con `2` per
loro, ma vanno chieste al progettista, con la proposta: «fornitura come al solito, macchine Nove C e bocchette del
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

- **Ogni quantità ha la sua regola**, con la fonte e il perché, e il conto fatto: in `distinta-calcoli.md`; nel PDF
  le regole sono dette in parole (capitolo 7). Le regole sono dati, in `rules/distinta/`.
- **Niente prezzi e niente codici interni nel documento**: i pezzi si chiamano con le **sigle dello schema** — le
  stesse che la tavola scrive —, o con la loro etichetta dove non hanno sigla; le fonti sono scritte per chi le legge
  («regola Nove C per i canali flessibili», «manuale di installazione del costruttore della macchina»). Gli id delle
  regole restano nel foglio dei calcoli e nel JSON, che sono la traccia del conto. Il controllo dei report cerca nel
  PDF le stringhe vietate.
- **Il cartiglio**: dove committente, commessa o numero della tavola mancano (o sono «ND»), il documento e il foglio
  dei calcoli scrivono «DA DEFINIRE», come la tavola.
- **I numeri di tratta seguono le sigle**: per fluido, e dentro il fluido nell'ordine delle sigle che la tratta
  collega, come la colonna «Da - a» (PLZ-01 - TA-01 prima di PLZ-01 - TA-02). Con una tratta per bocchetta, T0n
  va a TA-0n. La ripresa montata sulla macchina (lunghezza 0) è il **plenum di ripresa** in tutte le uscite.
- **Le lunghezze** si quotano con `(L + 1 m) × 1,15`, per eccesso al mezzo metro, con i minimi del fluido (12 m frigo,
  10 m condensa, 5 m bus, 2 m ramo d'aria): in dubbio per eccesso, come vuole il PO.
- **Dove manca un dato, DA DEFINIRE e una domanda.** Mai un numero inventato.
- Il documento chiede un prezzo **a corpo, fisso e invariabile**, con il **sopralluogo obbligatorio**; ha le righe
  vuote **H** per le voci che aggiunge l'installatore e le varianti **V** a prezzo unitario. **Nessun prezzo**: li
  mette l'installatore nella sua offerta.
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

Riporta al progettista, in quest'ordine: le **domande** (le voci DA DEFINIRE: se le hai fatte al passo 2,
restano solo quelle che ha lasciato aperte), quello che è **da confermare** (la
fornitura), le **segnalazioni** della verifica, che cosa hai visto guardando le pagine del PDF, poi i file:
`mep.py consegna` copia il PDF della distinta accanto alle tavole se gli dai anche la sua cartella
(`consegna $L/tavola $L/distinta … <destinazione>`). Non riempire tu una voce DA DEFINIRE e non ritoccare il PDF:
si corregge il grafo, e si rilancia il comando.
