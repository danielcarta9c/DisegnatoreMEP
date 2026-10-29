# Rapporto di collaudo della skill disegnatore-mep 1.6.0 — caso t1 (canalizzato Mitsubishi + Airzone)

Data: 29/10/2026. Sessione dalle 18:10 alle ~18:25 UTC (circa 15 minuti di orologio). Ogni comando
ha risposto in meno di 4 s. Ho usato solo la cartella della skill e `lavoro/`.

**In breve: le tavole escono, ma il catalogo non sa disegnare un plenum a 4 uscite.** La
validazione si ferma (`REQUIRED_PORT_UNCONNECTED · plenum, out_5`) e `completa` rifiuta il grafo.
Sono andato avanti solo con un ripiego, che è visibile sulla tavola e nella distinta: una quinta
«bocchetta» con la scritta «tappo».

---

## 1. File prodotti e numeri finali

Cartella di lavoro: `/tmp/claude-0/-home-user-DisegnatoreMEP/b6516f2f-ca66-5466-8ba2-b80294187e6d/scratchpad/collaudo/t1/lavoro/`

| elaborato | percorso |
|---|---|
| Schema funzionale PDF (A1) | `lavoro/consegna/canalizzato-appartamento-secondo-piano-t1.pdf` (+ `.dxf`, `.svg`, `-rilievi.md`) |
| Distinta Excel | `lavoro/consegna/distinta.xlsx` (+ `lavoro/distinta/distinta.json`, `distinta-calcoli.md`, `tabelle-del-foglio.json`) |
| Pianta PDF (A3 1:50) | `lavoro/consegna/pianta.pdf` (+ `.dxf`, `.svg`; `lavoro/pianta/pianta.tracciati.json`, `pianta.png`) |
| Grafo, piano, pianta | `lavoro/grafo.json` (dallo script `lavoro/gen_grafo.py`), `lavoro/grafo-completo.json`, `lavoro/piano.json`, `lavoro/pianta.json` |
| Domande, vincoli | `lavoro/domande.md`, `lavoro/vincoli.md` |
| Anteprime guardate | `lavoro/tavola/zoom-1..3.png`, `lavoro/tavola/finale.png`, `lavoro/pianta/zoom-corridoio.png` |

`/mnt/user-data/outputs` non c'è, quindi la consegna è andata in `lavoro/consegna` con `mep.py consegna`.

**Schema funzionale (ultimo giro):** A1 · 19 tratte · **0 tratte cedute · 0 rilievi bloccanti** ·
5 pieghe · **0 sormonti** · resta 1 regola del piano (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM`: lo
scarico della condensa sta 5 mm più lontano del minimo). La tavola è in **bozza**: 5 campi del
cartiglio sono DA DEFINIRE (committente, indirizzo, titolo, commessa, numero).
Il primo giro aveva dato 7 pieghe, 2 sormonti e 2 regole; un giro intermedio (scarico al minimo)
dava 1 rilievo bloccante (`RUN_LABEL_OMITTED`).

**Distinta:** 82 voci in 9 sezioni, 16 tratte, uscita 2. **9 voci DA DEFINIRE** (B.7, B.12,
C.7, D.9, E.3, E.4, E.8, E.10, Z.2), con 17 domande stampate.

**Pianta:** A3 1:50 · 16 tratte, 0 non instradate · 0 diagonali · **6 sormonti** · 0
sovrapposizioni · 0 scritte su linee · 5 forature fuori dalle aperture (più 4 fori dei pezzi a
parete). Il controsoffitto manca su 7,95 m di T06, T07 e T11 e su 3,25 m di T08. Uscita 0.
Un secondo tentativo (centrale di zona spostata) ha dato 16 sormonti e 1 bloccante: l'ho scartato.

---

## 2. Dove la skill mi ha fatto inciampare

### 2.1 Bloccante: il plenum a 4 uscite non si può disegnare

- Il catalogo ha un solo plenum di zona, `zoning-plenum-5`, e tutte le sue uscite da `out_1` a
  `out_5` sono `required: true`.
- `python3 scripts/mep.py valida lavoro/grafo.json` dà:
  `Bloccanti — required port out_5 is unconnected · codice: REQUIRED_PORT_UNCONNECTED · plenum, out_5`
  (uscita 2).
- `python3 scripts/mep.py completa ...` dà
  `Il grafo non regge contro il catalogo: si corregge prima di completarlo.` (uscita 2).
- Nel catalogo non c'è un tappo per l'aria: `capped-connection` va solo su `heating_water`.
- Le istruzioni dicono di fermarsi:
  - `SKILL.md` r. 44-47: «Non sostituisci un pezzo che il catalogo non ha»;
  - `SKILL.md` r. 116: «un pezzo principale che il catalogo non ha: chiedi se procedere senza, o fermarsi».
- «Procedere senza» il plenum non ha senso: le bocchette restano scollegate.
- Ripiego, dichiarato in `assumptions`: la quinta uscita va su una `air-supply-terminal` con
  etichetta «Uscita 5 tappata, non utilizzata» e L 0. Il ripiego si propaga:
  - sulla tavola c'è una bocchetta in più e la scritta «tappo»;
  - la tabella delle apparecchiature dice «Plenum … a cinque serrande»;
  - nella distinta ci sono B.12 (plenum porta-bocchetta per il tappo), Z.2 con 5 bocchette e
    Z.3 con 5 griglie di transito.
- `capire.md` r. 555-557 presenta `zoning-plenum-5` come «plenum motorizzato» in generale. Non
  dice che ha 5 uscite fisse e tutte obbligatorie.
- **Il catalogo dell'aria-aria è cucito sul solo caso AA-01.** Ogni voce lo cita nelle `sources`:
  «proposta della sessione del 29/10/2026 (caso di prova AA-01) … forma da approvare dal PO».

### 2.2 Istruzioni ambigue o contraddittorie

1. **`SKILL.md` r. 283**: il testo del revisore esterno dice «Sei il revisore di una tavola di
   schema funzionale idronico (centrale termica)». Su un aria-aria è falso, e prepara male il
   revisore.
2. **`riferimenti/distinta.md` r. 3-4**: «queste istruzioni non sono nella skill che si carica su
   claude.ai». Invece sono nella skill, e `SKILL.md` r. 322-334 dice di leggerle.
3. **Ordine dei passi.** `SKILL.md` mette la distinta dopo il passo 7 (r. 322). Ma per le tabelle
   sul foglio `disegna --tabelle` vuole `tabelle-del-foglio.json`, che scrive `distinta`
   (`comporre.md` r. 241-242). La distinta va quindi lanciata **prima** del passo 6, e il flusso
   non lo dice.
4. **Planimetria a parole.** `SKILL.md` r. 126 e r. 338 chiedono «la planimetria (PDF o immagine,
   con la scala)». Il progettista l'ha data a parole, con le misure. Non è detto se va bene, né
   come leggere «11 × 8 m»: misure interne o esterne. Ho scelto le interne.
5. **`pianta.md` r. 110**: le velette sono «rettangoli di controsoffitto», ma il nome del campo non
   c'è e l'esempio non ne ha. Ho scritto `poligono` come per le stanze, e
   `mep.py pianta` ha risposto:
   `velette.0.rettangolo: Field required / velette.0.poligono: Extra inputs are not permitted` (uscita 1).
   Il formato giusto è `{"id":…, "rettangolo":[x0,y0,x1,y1]}`, e si trova solo leggendo lo schema.
6. **`pianta.md` r. 112-113, e la nota 2 stampata sulla pianta**: «le sigle e i numeri di tratta
   sono quelli dello schema funzionale». È falso:
   - lo schema dà la sigla solo a UE-01, UI-01, PLZ-01, CZ-01 e CF-01;
   - bocchette, termostati, quadro, sezionatore, ripresa e scarico restano senza sigla. Le regole
     di `capire.md` §3 vietano di inventarla, e il «battesimo» automatico non la mette;
   - sulla pianta ho dovuto inventare B1-B4, TZ-01..03, QE-01, SZ-01, RA-01 e SC-01;
   - i numeri T01… stanno solo nella tabella dello schema, non sulle linee.
7. **Il tratto con il sezionatore.** Lo schema numera la linea quadro – sezionatore – UE come una
   sola tratta, T10. La pianta vuole un tracciato per ogni coppia di pezzi, e ho dovuto inventare
   «T10b».
8. **`capire.md` r. 591-592**: la sezione si scrive «come il testo li scrive», e subito dopo
   l'esempio è «Ø6,35 (1/4")», cioè una conversione. Ho scritto `1/4"`.
9. **Il cartiglio.** `capire.md` r. 214-215 dice di scrivere `ND` se committente e commessa
   mancano. Il risultato è incoerente:
   - sulla tavola il cartiglio dice «DA DEFINIRE»;
   - l'Excel titola «ND — Canalizzato…» e porta «Allegata alla tavola -»;
   - il foglio dei calcoli porta «(ND rev. 00)».
10. **A4 contro le scritte.** Con lo scarico della condensa al minimo di A4 (25 mm), la scritta
    obbligatoria del tratto sifone–scarico, che ha L 0, non trova posto, e la tavola si blocca:
    `RUN_LABEL_OMITTED · c-condensa-2`. Una regola del piano e un rilievo bloccante si scontrano, e
    le istruzioni non dicono chi cede. Ho tenuto lo scarico a 30 mm.
11. **Dove va la lunghezza nei tratti spezzati da sifone e sezionatore.** Che basti su una sola
    tubazione lo dice solo `distinta.md` r. 27, non `capire.md`.
12. **Dati senza posto nel grafo:**
    - l'asservimento di due serrande a un termostato (2 bocchette, 1 zona): l'ho detto con le
      etichette «Z3»;
    - la pompa di condensa a bordo della UI: non c'è un mestiere per `a_bordo`, l'ho scritta a
      parole;
    - il collegamento fra centrale Airzone e UI: il testo non lo descrive. L'ho messo su
      `p1p2_b`, perché `zone-controller.p1p2` è obbligatorio;
    - la nomenclatura «P1-P2» è Daikin. Lo stesso progettista nel messaggio si corregge: «per
      Mitsubishi è il cavo del comando a filo».

### 2.3 Comandi che hanno dato errore

- `valida` e `completa` sul plenum a 4 uscite: vedi 2.1.
- `pianta` con le velette: vedi 2.2 punto 5.
- Nessun crash. I messaggi sono chiari e dicono il campo.

### 2.4 Distinta: difetti di contenuto, misurati sull'output

1. **Una lunghezza che manca cancella quelle date.** E.8 (cavo bus) ed E.10 (corrugato) mettono
   insieme i tre bus ai termostati (7 + 5 + 9 m, dati) e il collegamento centrale–UI, che non ha
   lunghezza. Tutta la voce diventa DA DEFINIRE e i 28 m noti spariscono. Dovrebbe essere: somma
   nota più una riga DA DEFINIRE.
2. **Z.3 «Griglia di transito» conta per bocchetta, non per locale.** Esce 5: il soggiorno conta
   due volte, e conta anche il «tappo». Il soggiorno ha già un varco di 1,5 m, quindi non ne serve
   nessuna.
3. **C.7 chiede il `refrigerante`** («servono `precarica_fino_a_m`, `carica_aggiuntiva_g_m` e
   `refrigerante`»), che è già nel grafo: la voce stessa scrive «Refrigerante R32».
4. **Scelte commerciali che il progettista non ha fatto:**
   - sezione A «Apparecchiature fornite da Nove C»: tutte le macchine;
   - sezione Z «Opere del Committente (escluse dall'offerta)»: bocchette, griglie, botole,
     controsoffitto;
   - G.7 «Messa in servizio con Nove C».
   Il progettista ha scritto «da far quotare al nostro installatore a corpo» e non ha detto chi
   fornisce le macchine. Sono regole del kit AA-01 applicate come fatti.
5. **L'Excel che va all'installatore mostra codici interni e fonti di sviluppo:**
   - gli id del grafo nelle Note e in «Da - a»: `bocchetta-soggiorno-1`, `uscita-5-tappata`, `ue`,
     `centrale-zona`;
   - le fonti: «kit AA-01: lavoro/dimensionamento.py», «REVISIONE-INDIPENDENTE.md rilievo 17»,
     «RAPPORTO.md §2, proposta 5 approvata dal PO».
   È contro «niente codici interni» (`SKILL.md` r. 380-382).
6. **La stessa cosa sulla tavola.** La tabella delle tratte e il computo scrivono «plenum -
   bocchetta-matrimoniale», «ui - comando-filo», «centrale-zona - ui».

---

## 3. Quello che ho visto guardando le tavole, e che i numeri non dicono

### Schema funzionale (0 bloccanti, 0 cedute: i numeri dicono «si consegna»)

- **Le linee non portano il numero di tratta.** Lo schema scrive «Ø200 · L 5 m» e la tabella
  scrive T01…T16 con «Da - a» in id interni. Per l'installatore che quota tratta per tratta il
  collegamento fra linea e riga della tabella va indovinato.
- **Pezzi senza sigla.** 4 bocchette, 3 termostati, il quadro (solo «Ingresso»), il sezionatore,
  la ripresa (solo «Disimpegno»), il sifone e lo scarico.
- **La scritta «Terrazzo» dell'UE sta sopra la linea del gas 5/8"**, accanto a «5/8" · L 9 m»: si
  legge come scritta della linea. Nessun rilievo lo segnala.
- **La quinta uscita tappata** è disegnata come una bocchetta vera, col simbolo pieno (ripiego del
  §2.1).
- **Il collegamento centrale Airzone – UI** è una linea blu senza scritta. È corretto, perché il
  dato manca, ma chi legge non sa che cosa sia. «DA DEFINIRE» sarebbe più onesto.
- **Port stub che sembrano attacchi liberi:**
  - due trattini sul fianco destro della UI, sopra e sotto la mandata;
  - due sul fianco sinistro del plenum;
  - uno libero sulla centrale (`bus_4`).
  Sembrano attacchi non collegati.
- **Condensa:** la seconda scritta «PVC Ø32», sul tratto di lunghezza zero fra sifone e scarico, è
  obbligatoria (bloccante), ma è rumore. In più ha costretto a spostare lo scarico (§2.2 punto 10).
- **Il formato è A1 per colpa delle tabelle.** Il disegno è 245 × 172 mm, un A3 basterebbe. Il
  computo di 82 righe sul foglio fa un A1 con il disegno in un angolo e tanto vuoto. È coerente con
  `comporre.md` r. 244-245, ma per uno split è sproporzionato.
- Il resto si legge bene:
  - UE e UI allineate, linee frigo rette;
  - bocchette e termostati in colonna, scritte pulite;
  - le regole E1-E3 di `comporre.md` funzionano al primo colpo.

### Pianta (0 scritte su linee: i numeri dicono «si consegna»)

- **I richiami attraversano mezzo corridoio e passano sopra i pezzi.** Il controllo «scritte che
  toccano una linea: 0» non vede i richiami. Nella zoom del corridoio:
  - il richiamo di F5 sale verticale attraverso la UI per tutto il corridoio;
  - il richiamo di PLZ-01 scende attraverso il fascio frigo e la tramezza fin nel soggiorno;
  - il richiamo di TZ-03 attraversa B3;
  - il richiamo di F1 corre per circa 3,5 m lungo il muro.
- **Il nodo UI + plenum + ripresa + centrale è troppo fitto per 1:50.** Linee e richiami si
  sovrappongono ai rettangoli dei pezzi.
- **Le linee frigo fanno il giro del soggiorno**, senza controsoffitto:
  - dal corridoio scendono lungo il muro ovest;
  - forano il perimetro in F2, vicino all'angolo sud-ovest;
  - tornano all'UE all'esterno, lungo la facciata.
  Sono 10,7 m misurati contro i 9 m del progettista. Il comando scrive «7,95 m in controsoffitto
  dove il controsoffitto non c'è» in console, ma sulla tavola non c'è nessun segno.
- **Due serie di lunghezze per le stesse tratte.**
  - La pianta scrive sulle linee la lunghezza **da quotare** ricavata dalla **sua** misura. Per
    esempio T01 «L 4,5 m» (misura 2,9 m); T12 2,4 m misurati contro 7 dati.
  - Lo schema scrive la lunghezza del progettista, T01 «L 5 m», e la distinta quota 7 m.
  - L'installatore riceve due quantità diverse per T01 (4,5 e 7) e nessuno gli dice quale vale.
  - Nessun controllo confronta le misure in pianta con le lunghezze del grafo.
- Il bus T13 va alla camera singola passando dentro il bagno, in traccia, con 2 forature (F4, F5),
  invece di restare nel corridoio.

---

## 4. Domande che avrei fatto al progettista

Sono tutte in `lavoro/domande.md`; ho proceduto con «va bene».

1. Il plenum a 4 uscite manca dal catalogo: va bene il plenum a 5 con la quinta tappata, o ci
   fermiamo?
2. Bus 7 / 5 / 9 m: nell'ordine matrimoniale, singola, soggiorno?
3. Il collegamento fra centrale Airzone e UI (interfaccia Mitsubishi): che cavo è e quanto è lungo?
4. Il tratto sezionatore–UE: quanto è lungo? (Ho messo i 18 m fra quadro e sezionatore.)
5. Condensa: gli 8 m arrivano al sifone, e il sifone sta sullo scarico della cucina? Dove è la
   cucina nella pianta? (Ho assunto il muro est del soggiorno, verso l'ingresso, a y 7,5.)
6. La ripresa 800×300 è sotto la UI (L 0)? I motori delle serrande sono cablati di fabbrica sulla
   centrale?
7. Cartiglio: committente, commessa, indirizzo, titolo e numero delle tavole.
8. Il modello del plenum e della centrale Airzone; la dimensione delle bocchette; la sezione del
   bus Airzone.
9. I dati di scheda dell'UE (precarica, carica aggiuntiva, lunghezza massima); l'attacco della
   condensa della UI; la protezione delle due linee nel quadro.
10. Pianta: i 11 × 8 m sono misure interne? Dove sono centrale di zona, termostati, comando a filo
    e sezionatore? Dimensioni d'ingombro di UI (ho assunto 1,10 × 0,73) e plenum (0,60 × 0,70)?
    Larghezza della porta di casa?
11. Chi fornisce macchine, bocchette e griglie? La distinta assume «Nove C» e «Committente»: va
    bene per questa offerta?
12. Le linee frigo attraversano il soggiorno senza controsoffitto: c'è una canalina o un altro
    passaggio verso il terrazzo?

---

## 5. Giudizio

**Non è pronta per un uso dal vivo domani su un canalizzato qualsiasi.** Lo è solo su un impianto
con un plenum a 5 uscite, cioè il caso AA-01 da cui è nata.

Che cosa la ferma, in ordine:

1. **Il catalogo dell'aria-aria è una voce sola per tipo**, a numero di uscite fisso e
   obbligatorio. Un 4, 3 o 6 uscite si blocca in validazione, e l'unico modo di passare è un
   ripiego che sporca tavola e distinta. Serve:
   - un plenum a N uscite, con le uscite facoltative;
   - oppure un tappo per l'aria.
2. **Lo schema non è collegabile alla pianta e alla distinta:**
   - mancano le sigle di bocchette, termostati e quadro;
   - mancano i numeri di tratta sulle linee;
   - nelle tabelle compaiono gli id interni.
   È proprio l'uso richiesto, la quotazione a corpo tratta per tratta, che si regge su questo
   collegamento.
3. **Le lunghezze della pianta non vengono riconciliate** con quelle del progettista. Escono due
   serie di quantità per la stessa tratta.
4. **La distinta esce con scelte commerciali e fonti interne di Nove C/AA-01** scritte come fatti,
   e il conto per voce ha errori: bus azzerati da un dato mancante, griglie per bocchetta.
5. **La pianta passa i controlli ma a occhio è un groviglio** attorno alla UI: i richiami non sono
   misurati.
6. Difetti minori di testo:
   - il revisore «idronico»;
   - `distinta.md` dice di non essere nella skill;
   - l'ordine distinta/disegna;
   - il campo delle velette.

Cosa funziona bene:

- i comandi sono rapidi e chiari;
- le regole E1-E3 di `comporre.md` danno uno schema pulito in due giri;
- i rilievi sono onesti sui bloccanti;
- `DA DEFINIRE` è usato senza inventare.
