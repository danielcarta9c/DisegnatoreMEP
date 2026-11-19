# Handoff sviluppo — skill disegnatore-mep (v2.2.2) dopo il caso BD.RM.264

Caso di prova: BD.RM.264 Daniele Gianni, Roma, int. 28 — Shenling ThermaX R290 9 kW, volano Cordivari
50 l a 4 attacchi, bollitore Cordivari Bolly 1 XL WB 200 (serpentino 2 m²) su valvola a tre vie,
circolatore DAB Evosta 2 sul secondario, radiatori esistenti con valvole termostatiche, cronotermostato
BPT wifi. Sessione del 19/11/2026.

Contenuto dello zip:

| File | Cosa è |
|---|---|
| `BD.RM.264_Lista_materiali_prezzata_rev04.pdf` | **Il documento di riferimento**: è questo che il PO intende con "lista prezzata" |
| `esempio/build_lista_prezzata.py` | Script che l'ha generato: nove-c-report, a partire da `costo-minuteria.json` più le correzioni manuali (vedi §3) |
| `esempio/dati_lista_prezzata.json` | Righe e totali della lista, già strutturati |
| `esempio/costo-minuteria_skill.json/.md` | Quello che la skill produce oggi con `distinta --costo` |
| `esempio/grafo*.json`, `piano-*.json` | Grafo e piani del caso, per riprodurlo |
| `esempio/T1_idraulica.pdf`, `T1-E_elettrico.pdf` | Le tavole prodotte |
| `esempio/PRIMA_distinta_installatore_NON_e_la_lista_prezzata.pdf` | Quello che è stato consegnato per errore come "lista prezzata" e che il PO ha respinto |

---

## 1. "Lista prezzata": requisito strutturale

Quando il PO chiede **"lista prezzata"** (anche "lista materiali prezzata", "listino prezzato", "CAPEX
materiali"), la skill produce **il PDF del modello rev04**. Non produce la distinta per l'installatore e
non produce `costo-minuteria.md`. È un documento a uso interno Nove C, impaginato con i report Nove C.

### Struttura, in quest'ordine
1. **Copertina** report Nove C con 4 KPI:
   - totale netto;
   - pompa di calore;
   - numero di fornitori;
   - numero di voci.
2. **Capitolo 1 — Quadro economico riepilogativo**:
   - in testa una tabella con commessa, committente, indirizzo e la fonte dei prezzi (listino interno con revisione e data);
   - sotto, la tabella con queste righe fisse, in quest'ordine: **Pompa di calore · Apparecchiature · Circuito idraulico · Elettrico · Staffaggi · Totale**;
   - colonne: **Netto € · IVA 22% € · Totale IVA inclusa €**. La doppia colonna con e senza IVA è una regola del PO.
3. **Un capitolo per categoria**, nello stesso ordine: Pompa di calore, Apparecchiature, Circuito idraulico, Elettrico, Staffaggi.
   - Tabella con le colonne **Rif. · Voce · UM · Q.tà · Fornitore · € unit. · € totale**.
   - Rif. per sezione: P., A., I., E., S.
4. **Ultimo capitolo — Recap ordini**:
   - una riga per fornitore (Shenling, Idrosanitaria, Tecnomat, Abbattista, …, Online), più il totale;
   - colonne: Fornitore · Articoli · Netto € · IVA 22% € · Totale IVA inclusa €.
   - Righe ordinate per importo decrescente.

### Regole
- **Fornitore** = il fornitore reale che vende l'articolo al prezzo scelto: Shenling, Idrosanitaria, Tecnomat, Abbattista. Se il prezzo è solo un riferimento online e nessun fornitore da cui Nove C ordina lo ha, scrivere "Online".
- **Mai "Fornitura Nove C"** e **mai una colonna Note**.
- Un articolo composto da più articoli di fornitori diversi va su **righe separate**, una per fornitore. Esempio: "Canapa e pasta sigillante" diventa "Canapa" (Tecnomat) e "Pasta sigillante" (Idrosanitaria).
- **Escluso dalla lista prezzata:**
  - F assistenze murarie;
  - Z opere del Committente;
  - G attività a corpo;
  - V varianti a prezzo unitario;
  - H voci aggiunte dall'installatore;
  - capitolo domande e voci da definire;
  - capitolo note e regole usate.
- **Staffaggi della pompa di calore a terra:** si quotano solo i **piedini antivibranti**, voce "Piedini antivibranti per l'unità esterna", 4 pezzi, articolo I71a. Mai "basamento a terra": nessuno l'ha chiesto. Le staffe a muro solo se il PO le chiede.
- **Attribuzione delle sezioni:**
  - Pompa di calore: solo il generatore;
  - Apparecchiature: bollitore, volano, circolatori, termostati e comandi;
  - Circuito idraulico: tubi, guaine, raccordi, valvolame, vasi, defangatore, filtro, deviatrice, miscelatrice, prodotti chimici;
  - Elettrico: cavi, corrugati, scatole, interruttore, relè;
  - Staffaggi: piedini antivibranti, staffe.
- **Quantità nette.** Vale la regola del PO: niente riserve.
- Gli importi seguono le regole dei report: centesimi solo se servono, mai ",00".
- **Una voce senza prezzo non deve uscire in silenzio.** Prima della consegna va chiesta al PO, oppure si usa la regola di ripiego del §3. Nel PDF non compaiono "DA DEFINIRE" né "DA PREZZARE".

---

## 2. Disegno e distinta: modifiche attese

### 2.1 Tappi sugli attacchi non usati del bollitore ACS
Il Bolly 1 XL ha più attacchi di quelli che lo schema usa. La scheda è già trascritta in
`diametri/costruttori.py`, `CORDIVARI_BOLLY_1_XL`:

| Attacco | Pollice |
|---|---|
| A uscita ACS | 1¼" |
| B ricircolo | ¾" sul 200 l |
| M acqua fredda | ¾" sul 200 l |
| F e G primario | 1¼" |
| C strumentazione | ½" |
| E anodo | 1¼" |
| O scarico | 1¼" |

Oggi la distinta conta solo gli attacchi collegati, e in tavola gli altri non si vedono.

**Atteso**
- La scheda del bollitore elenca **tutti** gli attacchi fisici, con numero e pollice.
  - Da completare: numero esatto degli attacchi C di strumentazione e attacco della resistenza, se c'è. Fonte: scheda Cordivari BOLLY 1 XL W 02.2026.
- Ogni attacco che il grafo non collega diventa **un tappo filettato del pollice giusto**:
  - in distinta, voce "Tappo M x"";
  - nella lista prezzata, con il prezzo del listino.
- In tavola il segno dell'attacco tappato compare sul bollitore.
- Nel caso BD.RM.264, senza ricircolo:
  - tappo ¾" sul ricircolo B;
  - tappi ½" sugli attacchi C non usati dalla sonda;
  - scarico O 1¼": tappo, oppure rubinetto, da decidere con il PO. Le regole oggi scaricano il bollitore dalla linea dell'acqua fredda.
- **Riduzioni agli attacchi:** l'uscita ACS da 1¼" sul tubo MS 20×2 richiede una riduzione. Va verificato che il conto la faccia sempre, quando il pollice dell'attacco è diverso da quello del tubo e degli accessori.

### 2.2 Volano standard Cordivari a 4 attacchi, 50 l e 80 l
La skill non ha la scheda di nessun volano. Il volano esce con l'attacco "da definire", e quindi senza raccordi, riduzioni e tappi.

**Atteso**
- La sessione di sviluppo **cerca le schede Cordivari** dei volani a 4 attacchi da **50 l e 80 l**.
  - L'80 l è già in listino: "VB 80LT C/4 ATT. C/COPERT." codice 3070160920018, Idrosanitaria 156,49 €, Abbattista 179,29 €.
  - Il 50 l è da trovare.
- Le trascrive come `CORDIVARI_BOLLY_1_XL` (numero e pollice di ogni attacco: primari, secondari, sfiato, scarico, sonde, eventuali attacchi in più) e le usa come **volano standard per `buffer-four-port`**.
  - Il volume (50 o 80) si sceglie dal grafo.
  - Il pollice degli attacchi vale anche se marca e modello non sono scritti.
- Dagli attacchi la distinta conta raccordi all'attacco, nippli ridotti o riduzioni, e **tappi sugli attacchi non usati**. Come per il bollitore, il segno dell'attacco tappato compare in tavola.
- **Listino:** aggiungere il volano Cordivari 50 l a 4 attacchi con il prezzo reale.
  - Nel caso BD.RM.264 il PO ha chiesto una stima proporzionale all'80 l: 95 €, segnata come stima. Non è una regola da rendere strutturale.

### 2.3 Avviso distanza pompa di calore–bollitore oltre 5 m (manuale Shenling §2.3 p.to 6)
Non è scattato. Il PO ha dato 8 m fra macchina e centrale, scritti in `distinta.tubi`: primario 16 m fra andata e ritorno. L'avviso però legge solo `lunghezza_m` sulle tubazioni.

**Atteso:** leggere anche il blocco `distinta.tubi` (metri della rete primario / 2), oppure chiedere la distanza.

### 2.4 Carico impianto manuale
Il PO non vuole il gruppo di riempimento automatico: vuole **rubinetto manuale più disconnettore CA**, secondo UNI EN 1717. Il catalogo ha solo `filling-unit`, il gruppo automatico con disconnettore. Nel caso è stato aggirato:
- `accessori_tolti` sul gruppo automatico;
- `capped-connection` con etichetta su un `tee-branch` del ritorno.

**Atteso:** una voce di catalogo "Rubinetto di carico manuale con disconnettore", con simbolo, voce di distinta e articolo di listino. La si sceglie quando il progettista dice "carico manuale" o "rubinetto".

### 2.5 Attacchi dei confini "da definire"
Gli attacchi di acqua fredda, acqua calda e attacco di carico (AL-01…04) restano da definire.

**Proposta:** come default, il pollice del tubo del tratto; la domanda solo se il progettista lo vuole diverso.

---

## 3. Prezzi: lacune emerse nel caso, da sistemare

| Voce | Cosa è successo | Correzione |
|---|---|---|
| Circolatore DAB Evosta 2 | Il progettista ha scritto "Evosta 2" e non è stato agganciato, anche se il listino ha M30a "EVOSTA2 40-70/130", Idrosanitaria 93,60 € | Matching per famiglia o prefisso del modello; se ci sono più taglie, chiedere quale |
| Cronotermostato "wifi" | "BPT Cronotermostato settimanale wifi" non è stato agganciato a E30a (CRONOTERMOSTATO BPT SETTIMANALE WIFI, Tecnomat 56,56 €) | Matching per famiglia E30 e parole chiave (wifi, a filo) |
| Shenling ThermaX R290 9 kW | Non c'è in listino. Peggio: M01c, "Shenling ThermaX 12 kW", è una Haier GT 12 kW trifase | Aggiungere la riga Shenling 9 kW HPM-V90W/R3, **fornitore Shenling, 2.450 €** (dato del PO, 19/11/2026); sistemare M01c |
| Volano Cordivari 50 l | Non c'è in listino | Vedi §2.2 |
| Guaina 9 e 13 mm per MS 20×2 e MS 26×3 | Non c'è in listino | Ripiego usato: guaina elastomerica da 19 mm del diametro giusto (I56 Ø22 Tecnomat 2,355 €/m; I57 Ø28 2,79 €/m). Regola: spessore disponibile maggiore o uguale; l'avviso va solo in chat |
| Miscelatrice termostatica ½" | Non c'è in listino | Ripiego usato: la ¾" Giacomini DR156 (I52a Tecnomat 46,30 €). Regola: pollice disponibile più vicino; l'avviso va solo in chat |
| Bollitore Bolly 1 XL WB 200 | Corretto nella v2.2.2: Idrosanitaria 546 € | — |
| Pozzetti portasonda, cavo 3G4 | Solo riferimento online | Fornitore "Online", e nel recap ordini una riga "Online" |

**Lezione sul bollitore (già coperta da I-331, da tenere ferma).** In sessione è stato scelto il Bolly 1 ST perché costava meno, ma ha il serpentino da 0,8 m². Il bollitore non si sceglie mai per prezzo senza controllare la superficie del serpentino: per le Shenling 6-9 kW il minimo è 2,0 m².

---

## 4. Altre note della sessione

- **DWG AutoCAD 2007 non leggibile nel container.** Aspose in valutazione restituisce solo la filigrana, e la compilazione di LibreDWG è stata negata. Ripiego: il PO stampa un PDF vettoriale dal CAD con due quote, e la scala si ricava dalle quote. Vale la pena prevedere un import da PDF vettoriale quotato o da DXF per la pianta dei tracciati.
- **Cartelle e consegne:**
  - la lista prezzata va in `C - Progetto Definitivo\2_Computo`;
  - le tavole in `C - Progetto Definitivo\1_Elaborati_dwg\MEP`;
  - quando si inviano, copia in `Z - Consegne\AAAAMMGG - OUT - <nome>`, secondo la procedura PO 002 rev2.
