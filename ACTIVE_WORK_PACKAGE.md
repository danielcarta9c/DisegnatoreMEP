# ACTIVE WORK PACKAGE — DRAW-006

- **Release:** 0.3 — generalizzazione, prima tavola nuova
- **Stato:** APPROVATO DAL PM, PRONTO PER IL DEV
- **Data:** 2026-09-09
- **Base:** ultima `main`, contenente il merge approvato di DRAW-005-R1
- **Ramo:** `claude/draw-006-tavola2-semantica-componenti`
- **Fixture grafica principale:** impianto 2

## Obiettivo

Applicare il motore a un impianto nuovo e correggere tre difetti generali della semantica
dei componenti:

1. il manometro richiede un rubinetto portamanometro a tre vie, non una valvola di
   intercettazione ordinaria;
2. il gruppo di riempimento pubblicato incorpora già la propria intercettazione e non
   deve riceverne una esterna;
3. una valvola multivia possiede configurazioni idrauliche alternative: i domini di
   protezione devono essere validi in ogni configurazione ammessa.

La tavola 2 è il nuovo caso di collaudo visivo perché contiene PDC, deviatrice e produzione
ACS. Gli esempi sono fixture, non il prodotto: nessuna soluzione può dipendere da ID,
nomi, coordinate, quantità di macchine o nomi dei file di prova.

## A. Manometro e rubinetto a tre vie

1. Introdurre un componente e un simbolo specifici per il **rubinetto portamanometro a
   tre vie**, distinti dalla valvola di intercettazione ordinaria.
2. Il gruppo funzionale è: presa sulla tubazione → stacco statico minimo → rubinetto a tre
   vie → manometro. Il rubinetto vive sullo stacco, non interrompe la condotta principale.
3. La regola vale indipendentemente dal diametro della condotta: la presa strumentale è
   una derivazione propria e corta.
4. Il rubinetto non è un organo ordinario capace di dividere un dominio idraulico.
5. Scrivere prima prove generali che distinguano manometro e pressostato: un pressostato
   di sicurezza/minima non riceve automaticamente questo rubinetto né una valvola
   ordinaria.

Riferimento PM: Raccolta R 2009, cap. R.2.C, punto 2.5; Caleffi serie 690 e 335.

## B. Gruppi compositi e riempimento

1. Correggere `filling-unit`: il simbolo pubblicato rappresenta un gruppo che incorpora
   la propria intercettazione. Non aggiungere una valvola esterna per la sola proprietà
   `maintainable`.
2. Rendere esplicito nel catalogo quali funzioni sono interne a un composito. Una funzione
   integrata dichiarata non viene duplicata; una funzione non dichiarata continua a essere
   applicata dalle regole normali.
3. Non dedurre dotazioni dal nome, dal disegno o dal solo `composite: true`.
4. Non attribuire automaticamente al gruppo generico disconnettore BA, filtro, ritegno o
   riduzione di pressione se la variante di catalogo non li dichiara.
5. Un riempimento eventualmente presente sulla tavola 2 deve essere unico sul circuito
   tecnico, orientato verso l'impianto e privo di valvola esterna ridondante.

Riferimento PM: Caleffi serie 553; per la variante con disconnettore, serie 580, EN 1717,
EN 12729 ed EN 806-5.

## C. Connettività interna delle valvole multivia

1. Il catalogo dichiara gli **stati idraulici ammessi** di un componente multivia. Per una
   deviatrice a tre vie: `in ↔ out_a` oppure `in ↔ out_b`; i due rami non sono
   contemporaneamente comunicanti e `out_a ↔ out_b` non è un passaggio autonomo.
2. Nomenclatura delle linee e analisi della sicurezza devono leggere lo stesso dato di
   catalogo, senza elenchi di funzioni duplicati nei moduli.
3. Un generatore è protetto soltanto se raggiunge una sicurezza in ogni stato ammesso nel
   quale può funzionare, senza attraversare un organo che possa separarlo.
4. La cardinalità della sicurezza è per dominio di protezione effettivo, non per intera
   rete né per numero dei generatori.
5. Una sicurezza valida per una parte della rete non va scartata perché non protegge un
   altro generatore: ogni dominio viene valutato separatamente.
6. Per un generatore isolabile: dato a bordo ignoto → una domanda specifica; presente →
   nessun pezzo; assente → sicurezza propria non intercettabile.
7. La fixture dell'impianto 4 verifica questa logica senza produrre artefatti grafici: la
   deviatrice non diventa genericamente passante, la PDC conserva la protezione del proprio
   dominio e la caldaia genera al massimo la domanda dovuta al dato realmente ignoto.

Riferimento PM: Raccolta R 2009, cap. R.3.B, punti 1, 2.4 e 2.5; UNI EN 12828:2014.

## D. Integrità dei test

Riscrivere `test_i_raccordi_non_prendono_una_colonna_a_testa`: l'ultima asserzione
attuale è logicamente ridondante. La nuova prova deve fallire se un raccordo viene promosso
a colonna di un pezzo grosso e deve derivare l'attesa dalla classificazione e dalla posa,
senza soglie ricavate dalla tavola 1.

Il DEV non modifica criteri o soglie per far passare il lavoro. Un'incompatibilità si porta
al PM prima di cambiare la prova.

## E. Tavola 2 e regressioni

1. Generare la tavola 2 dalla sua fixture canonica senza modificare il grafo per ottenere
   un disegno più facile.
2. Applicare costo-peso, spostamenti gratuiti, assi, dorsali e T già approvati; nessuna
   regola speciale per questa geometria.
3. Consegnare metriche iniziali e finali della tavola 2, spiegando separatamente variazioni
   del grafo, della posa e del rendering.
4. Conservare la tavola 1 come regressione automatica: non oltre 4 curve, 1 incrocio e
   425 mm di rete ordinaria; stacchi statici non oltre 0 curve, 0 incroci e 45 mm; zero
   backtracking, tubo sotto simboli e tratte oltre tre curve.
5. Gli impianti 3–5 devono arrivare alla posa; non generare i relativi pacchetti completi.

## Criteri di accettazione

1. La tavola 2 è tecnicamente coerente, leggibile e ottenuta senza eccezioni per la fixture.
2. Il manometro, se presente, usa il rubinetto specifico a tre vie; mai una valvola
   ordinaria. La proprietà è comunque coperta da prove generali.
3. Il gruppo di riempimento, se presente, non ha intercettazione esterna ridondante. La
   proprietà è comunque coperta da prove generali sui compositi.
4. Prove generali dimostrano gli stati alternativi della deviatrice e la protezione in ogni
   configurazione ammessa.
5. L'impianto 4 non produce un `NO_COMMON_RUN` globale né protezioni inventate; restano
   soltanto domande puntuali dovute a dati di catalogo ignoti.
6. Il test sulle colonne dei raccordi prova realmente la proprietà e fallisce su una
   mutazione negativa costruita nella prova.
7. La tavola 1 rispetta integralmente le soglie di regressione del §E senza una nuova
   consegna grafica completa.
8. Tutti e cinque gli impianti arrivano alla posa; nessuna regressione viene convertita in
   `skip` o `xfail`.
9. Suite completa, `ruff`, `mypy --strict` e doppia generazione deterministica verdi.
10. PDF, PNG, SVG, geometria, metriche, preflight e confronto della **sola tavola 2** in
    `docs/collaudi/DRAW-006/`.

## Fuori perimetro

- nuovi PDF/PNG/SVG della tavola 1 e degli impianti 3–5;
- ricerca tecnica o reinterpretazione delle fonti da parte del DEV;
- chiusura degli input PO o modifica dei documenti di governance;
- correzioni puramente estetiche non necessarie alla tavola 2;
- audit dei simboli non coinvolti, cartiglio, etichette e Drawing Director;
- ottimizzazione prestazionale generale del ciclo.

## Consegna

Salvare progressivamente sul ramo remoto e aprire una PR verso `main`, senza merge. Il
rapporto deve dichiarare esplicitamente che soltanto la tavola 2 è stata renderizzata come
consegna; gli altri impianti sono stati usati esclusivamente nei test prescritti.
