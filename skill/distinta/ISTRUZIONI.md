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
                                [--fornitura <scelte>|confermata] [--regole <cartella o fascio>] [--lista [--senza-nove-c]]
                                [--costo [--fornitori <nomi>]]
```

**Due liste, tutte e due complete** (D-241, I-314). Il progettista chiede o la **lista prezzata** (l'analisi CAPEX:
`--costo`, sotto) o la **lista senza prezzi** da mandare ai fornitori per le quotazioni (`--lista`). Nella lista senza
prezzi le voci fornite da Nove C ci sono, con la nota «fornita da Nove C: non si quota»; se il progettista dice che
quelle cose le fornisce lui da altre parti e non le vuole nella lista, rilancia con `--senza-nove-c`. Chiediglielo
solo se non l'ha detto.

**Con `--lista`** esce la **lista della spesa per l'installatore**, `<commessa>_Lista_materiali_<impianto>.pdf`:
stessi calcoli e stessi numeri, ma solo i materiali da comprare — niente offerta a corpo, niente assistenze
murarie e opere del Committente, niente attività, varianti, domande e regole. È quella da dare quando
l'installatore deve comprare, non quotare; il documento completo resta quello senza `--lista`.

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
3. il computo per sezioni (A apparecchiature, S staffaggi, B aria, C frigorifero, D condensa, I circuito idraulico,
   E elettrico, F assistenze murarie, X senza regola, Z opere del Committente), una tabella per sezione;
4. le attività a corpo (G);
5. le varianti a prezzo unitario (V) e le righe vuote delle voci che aggiunge l'installatore (H);
6. le voci da definire e le domande, quello che è da confermare, le segnalazioni e le assunzioni;
7. le note e le regole usate, dette in parole.

## Che dati chiedi al progettista

La distinta **non progetta**: conta e maggiora i dati che il progettista scrive nel grafo. Chiedi quelli che
mancano — `--domande` te li elenca —; non li stimi tu.

| dove | dato | che cos'è |
|---|---|---|
| ogni tratto (aria, frigorifero, condensa, elettrico) | `lunghezza_m` | la lunghezza **stimata** del tratto (pianta, sopralluogo); `0` se è un raccordo diretto (plenum sulla macchina, cablaggio di fabbrica). **Non per l'acqua**: vedi sotto |
| ogni rete d'acqua | blocco `distinta.tubi` | **i tubi d'acqua li dice il progettista nella chat**: per rete, il tubo, i metri e l'isolamento (sotto) |
| l'impianto | `distinta.gomiti` | i gomiti a corpo: si **chiedono** come i metri; senza risposta la distinta mette l'ipotesi di 20, e la voce resta da confermare |
| pompa di calore | `posa` | «staffe a muro» solo se il progettista le chiede; senza, la distinta la mette **a terra** su supporti antivibranti |
| ogni tubazione | `sezione` | «Ø200», «Ø6,35 (1/4")», «MS 32×3», «3G2,5», «2×0,75 (P1-P2)»: diametro, lati o cavo; sull'acqua il tubo, nella notazione del materiale (I-279), e dove manca vale quello della tavola |
| mandata e ripresa | `portata_m3h` | per la verifica della velocità e delle griglie di transito |
| ogni tubazione | `attraversamenti` | quante pareti interne passa; se manca, la distinta ne assume uno per l'aria, la condensa e la linea del gas, e lo dice |
| linee di alimentazione | `protezione` | il dispositivo nel quadro, dalla targa della macchina: «Magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA»; non serve su una linea che ha il pezzo `circuit-breaker-rcbo`, che ha la sua voce |
| interruttore della linea | `poli`, `curva`, `in_a`, `idn_ma`, `tipo_differenziale` | «Interruttore magnetotermico differenziale 2P C32 Idn 30 mA tipo A» (REL-018, D-237: tipo A in ambito domestico); su una Shenling li scrive `completa` |
| un tratto incerto | `lunghezza_minima_m` | un minimo del progettista (il quadro da trovare in sopralluogo) |
| macchine | `marca`, `modello` | come per la tabella delle apparecchiature (D-190) |
| unità esterna | `refrigerante`, `precarica_fino_a_m`, `carica_aggiuntiva_g_m`, `lunghezza_max_m` | dalla scheda della macchina |
| unità interna | `attacco_condensa` | «VP20 (Øe 26)» |
| bocchette | `dimensione` | «400×200» |
| bocchette | `locale` | il locale che la bocchetta serve: «Soggiorno». Le griglie di transito si contano **per locale**, non per bocchetta: due bocchette nello stesso locale ne vogliono una. Se manca, la distinta legge il locale dall'`etichetta` (senza le parentesi); se manca anche quella, è una domanda |
| bocchette | `varco` | il locale ha un varco aperto verso la ripresa (un arco, una porta senza battente): «varco 1,5 m». Quel locale non vuole la griglia di transito; la verifica scrive l'area minima che il varco deve avere |
| un pezzo nel kit di un altro | `compreso_in` | l'id o la sigla del pezzo che lo comprende (la centrale nel kit del plenum; il filtro a Y o il pozzetto «compreso con la PdC»): non si compra, e la riga della macchina dice «comprende …» |

I campi del tratto (`sezione`, `lunghezza_m`, `scritta`) si scrivono sulla tubazione o nelle sue `properties`: la
distinta li legge in tutti e due i posti.

**Sull'acqua il tubo è quello della tavola** (I-279): la linea si dice come lo schema, «multistrato MS 32×3», e gli
accessori in linea — valvole, filtri, giunti, la deviatrice — portano il pollice del tubo su cui stanno (MS 32×3 →
1"), dalla tabella di equivalenza del produttore.

**L'idronico ha il suo corredo** (REL-020, sezione I). La pompa di calore, gli accumuli, il bollitore e il
circolatore sono apparecchiature (sezione A, Nove C le compra a parte); la pompa di calore va a terra, su staffe solo
se il progettista le chiede.

**Il bollitore della pompa di calore si sceglie col serpentino** (D-243, I-315): la voce dice «a serpentino maggiorato
per pompa di calore, superficie di scambio non minore di X m²», perché il fornitore non possa quotare un serpentino
piccolo. X viene dal manuale della pompa di calore che lo scalda: per le Shenling ThermaX R290 la skill lo sa (§2.3:
2,0 m² per 6–9 kW, 2,5 m² per 15 kW, serpentina smaltata; 1,4 e 1,6 m² inox, se sul bollitore scrivi
`"serpentino": "inox"`; **per la 12 kW 2,0 m²**, disposizione del PO, I-326). Se il bollitore è un Cordivari Bolly 1 XL,
la skill sa i suoi attacchi dalla scheda (primario 1¼" F). Per un'altra pompa di calore è una domanda: il minimo lo dà il progettista, e si scrive sul
bollitore in `superficie_minima_scambio_m2`. Se il progettista dice la superficie del bollitore scelto, scrivila in
`superficie_scambio_m2`: la tabella delle apparecchiature la porta, e sotto il minimo è un avviso. Un avviso anche
per il tubo fra unità esterna e bollitore oltre i 5 m (manuale Shenling §2.3, punto 6), se le tubazioni hanno le
lunghezze.

**Il raccordo all'attacco dice il pollice dell'attacco** (I-317): sul pezzo (bollitore, volano, collettore, terminale,
rete esistente) si scrive `"attacco": "1\""` dalla scheda della macchina; la Shenling lo sa dal manuale (1" per 6–9 kW,
1¼" per 12–15 kW). Senza, il raccordo esce DA DEFINIRE e `--domande` lo chiede: mai il pollice del tubo al posto di
quello dell'attacco. Ogni accessorio in linea porta sé stesso, del pollice del tubo; ogni derivazione un tee.
**Dal grafo si contano solo i pezzi** (valvole, tee, attacchi): sono pezzi veri.

**Le giunzioni si contano sulle tubazioni** (REL-023, I-291), dai due pezzi che ciascuna collega:

- fra **due pezzi filettati che si toccano** (sfera e defangatore, sfera e circolatore, la sfera sull'attacco del
  volano) un **nipplo**, ridotto se i pollici sono diversi;
- fra **un pezzo filettato e il tubo** un **raccordo diritto a pressare**, uno per capo; il **tee a pressare** prende
  il tubo da sé; il tubo che arriva a un attacco (macchina, accumulo, collettore, terminale, rete esistente) finisce
  con un raccordo all'attacco;
- la riduzione M × F si avvita senza nipplo, e il giunto antivibrante sull'attacco della pompa di calore col suo
  bocchettone; sfiati, manometri, sicurezze, scarichi, vasi e sonde si avvitano sul tee o sul loro rubinetto;
- **ogni tratto fra due pezzi che non sono tee ha almeno un tubo** (la deviatrice e la sfera del volano non si
  toccano): se le sue giunzioni sarebbero tutte nippli, la prima fra due accessori diventa un tubo;
- **il tratto esterno**: dalla pompa di calore si passano il giunto, la riduzione e la valvola antigelo, e la
  tubazione dopo è il tubo fino alla centrale.

Dove il **contesto del progetto** dice che fra due accessori c'è un tubo che la regola non vede (un accessorio lontano
dal suo vicino), scrivi `"tubo": true` nelle `properties` di quella tubazione. Se un accumulo ha gli attacchi di un
pollice diverso dalle valvole, scrivi il suo `attacco` (es. `"1¼\""`): la giunzione diventa un nipplo ridotto.

**I tubi d'acqua si chiedono nella chat, non si misurano sul grafo** (I-288). Il grafo è uno spazio di disegno, non
una planimetria: le lunghezze dei suoi tratti e le sue pieghe non sono quelle del cantiere. Chiedi al progettista,
**per ogni rete d'acqua**, il tubo, i metri (dalla pianta o dal sopralluogo) e l'isolamento — multistrato
**preisolato**, o **nudo con guaina** e il suo spessore —, e scrivili nel blocco `distinta` in testa al grafo, che
`completa` conserva:

```json
"distinta": {
  "tubi": [
    {"rete": "primario", "tubo": "MS 32×3", "metri": 30, "isolamento": "preisolato"},
    {"rete": "secondario", "tubo": "MS 26×3", "metri": 12, "isolamento": "guaina 19 mm"}
  ],
  "gomiti": 20
}
```

La distinta conta i metri netti, senza maggiorazione (I-320: il materiale si vende a confezioni intere); i collari (uno ogni 1,5 m) e un manicotto di riserva seguono i metri; i gomiti
sono **a corpo**: chiedili, proponendo l'ipotesi di 20, o stimali dal contesto del progetto (la pianta, il percorso
descritto), mai dalle pieghe dello schema; senza risposta la voce esce con 20 e resta da confermare. I metri vengono
dal contesto del progetto — la pianta quotata, il sopralluogo, le distanze che il progettista dice —, **mai dallo
schema**: se il contesto non li dà, non stimarli, la voce è DA DEFINIRE e `--domande` li chiede. Lo spessore della
guaina lo dice il progettista ogni volta.

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
- **Le quantità sono nette** (I-320): niente maggiorazione percentuale, perché i fornitori vendono a confezioni
  intere. Le lunghezze delle linee si contano con `L + 1 m` per tratto (i tubi d'acqua senza il metro), per eccesso al
  mezzo metro, con i minimi del fluido (12 m frigo, 10 m condensa, 5 m bus, 2 m ramo d'aria).
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
- **Le regole coprono l'aria-aria e l'elettrico del kit AA-01 e l'idronico** (REL-020). Una voce di catalogo senza
  corredo (il collettore solare, il regolatore d'impianto, la sonda esterna) o un fluido senza regole (il gas)
  esce nella sezione **X**, contato e DA DEFINIRE: dillo al progettista, non completarlo tu.
- Non calcola perdite di carico né prevalenze.

## La lista prezzata (CAPEX), se la chiede

Se il progettista chiede **la lista materiali prezzata**, l'analisi CAPEX, **quanto costa la minuteria** o un
riferimento per confrontare i preventivi, lancia la distinta con `--costo`: nella sottocartella `interno/` della distinta escono `costo-minuteria.md` e
`costo-minuteria.json` (`consegna` non li copia), con il prezzo di ogni voce dal **listino della minuteria** di Nove C
(`riferimenti/listino-minuteria.md`; un altro con `--listino <file>`). È un conto **interno**:

- **non va all'installatore** e non si mette nel suo documento, che resta senza prezzi;
- prezza **tutto il materiale**: le apparecchiature (pompa di calore, accumuli, bollitori, circolatori, unità e comandi
  del clima), anche quelle fornite da Nove C (D-241), e la minuteria (sezioni S, B, C, D, I, E e la X); **non** le
  opere, le attività, le voci a corpo e quelle del Committente. Una macchina che il listino non ha è DA PREZZARE;
  una di un'altra marca, o un bollitore col serpentino sotto il minimo, è uno scostamento ⚠: dillo;
- è il **consumo** (quantità × prezzo per unità del listino): le confezioni intere costano di più;
- una voce senza codice, con un codice che il listino non ha, o con la quantità DA DEFINIRE, è **DA PREZZARE**, fuori
  dal totale, col suo perché: **non la stimi tu**. Riporta il totale, quante voci sono da prezzare e le più pesanti;
- i prezzi del listino hanno una data e tre gradi di affidabilità (gli ordini e i preventivi dei fornitori, il
  rilievo al banco, il riferimento online): dillo.

### Dove comprare, e gli ordini

Il listino è **a più fornitori** (dalla revisione 06): la tabella «I fornitori» dice da chi Nove C ordina (oggi
Abbattista, Tecnomat, Idrosanitaria), e lo stesso articolo può avere il prezzo di ciascuno. **La marca non conta,
conta la prescrizione** (I-307): il costo usa, articolo per articolo, **il prezzo più basso fra quelli da cui si
ordina e che rispettano la voce**, e dice di chi è; un articolo che si scosta dalla voce (⚠ nel listino: il fondo
scala, l'attacco, il disconnettore che manca) e costa meno è un **avviso sul prezzo**, col risparmio, non una scelta; dove nessuno ha l'articolo, il
riferimento (online, o le fatture di un installatore). In fondo a `costo-minuteria.md`, **«Dove comprare»**:

- l'**ordine per fornitore**: per ogni articolo il codice e la descrizione del fornitore, la confezione, la quantità
  (la somma sulle voci che lo usano), il prezzo, e i prezzi degli altri fornitori;
- **«Un fornitore solo»**: se compra tutta la minuteria da uno, quale costa meno sul totale — gli articoli che ha ai
  suoi prezzi, quelli che non ha dal più economico degli altri, così i totali sono sullo stesso paniere; e accanto il
  conto sui soli articoli che **tutti** hanno, che dice chi costa meno a parità di articoli quando un listino è
  incompleto. Se le due righe nominano fornitori diversi, diglielo: vuol dire che il listino di qualcuno è incompleto;
- **«Con meno ordini»**: per ogni gruppo di fornitori, quanti articoli non hanno e quanto costano in più gli altri,
  sugli stessi articoli. È lì che il progettista decide se tre ordini valgono la differenza;
- gli articoli **senza un fornitore**, da comprare dove si trovano;
- gli **avvisi sul prezzo**: l'articolo scelto, quello che costa meno e in che cosa si scosta. Se lo scostamento va
  bene lo decide il progettista, non tu.

Quando il progettista chiede **dove comprare** o di **fare gli ordini**, lancia `--costo` e riportagli «Dove
comprare» così com'è: gli ordini, il fornitore più economico se ne sceglie uno solo, le combinazioni, gli articoli
senza fornitore. Se per il cantiere **sceglie lui** il fornitore (o due), rilancia con `--fornitori Idrosanitaria`
(o `--fornitori Abbattista,Tecnomat`): l'ordine va tutto a quelli, e quello che non hanno resta fra gli articoli
senza fornitore, col prezzo più basso degli altri. **Non** spostare tu un articolo da un
fornitore all'altro e non aggiungere trasporto o minimi d'ordine: il conto non li ha, e lo dici. **Non** sostituire
un pezzo con uno che fa un altro mestiere, e **non** aggiungere articoli che la distinta non conta: lo scopo è
risparmiare sulla minuteria, non comprare l'utile che non serve (I-310). Le quantità sono il
consumo: al banco si comprano le confezioni intere (il rotolo, la barra), e la colonna Confezione lo dice.

## Come la consegni

Riporta al progettista, in quest'ordine: le **domande** (le voci DA DEFINIRE: se le hai fatte al passo 2,
restano solo quelle che ha lasciato aperte), quello che è **da confermare** (la
fornitura), le **segnalazioni** della verifica, che cosa hai visto guardando le pagine del PDF, poi i file:
`mep.py consegna` copia il PDF della distinta accanto alle tavole se gli dai anche la sua cartella
(`consegna $L/tavola $L/distinta … <destinazione>`). Non riempire tu una voce DA DEFINIRE e non ritoccare il PDF:
si corregge il grafo, e si rilancia il comando.
