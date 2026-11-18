# REL-028 — Il listino Tecnomat completo, e i punti aperti di REL-027

> **Scritto il 18 novembre 2026**, alla fusione di `REL-027` (la 2.1.1, PR #96). Il PO: «la lista mettila in main
> insieme alle "cose da fare prox sessione"» (I-312). Il pacchetto precedente è in `docs/plans/pacchetti/REL-027.md`,
> il suo rapporto in `docs/collaudi/REL-027/RAPPORTO.md`.

**Da svolgere:** l'agente unico (**D-147**), nella sessione.
**Stato:** **CONSEGNATO** il 18 novembre 2026, punti 1 e 2 (la 2.2.0, rapporto `docs/collaudi/REL-028/RAPPORTO.md`), fuso col sì del PO («al termine dammi la skill aggiornata e fondi su main»). Era: **AVVIATO** dal PO il 18 novembre 2026 («metti tutto su main e lancia direttamente la prossima sessione per
sistemare», I-324). **La sessione lanciata fa il punto 2**; il punto 1 (il rilievo Tecnomat Pro) aspetta il file che il
PO riempie con Claude in Chrome, e si fa quando lo porta.
**Base:** `main` con la 2.1.1 (PR #96).
**Approvazione della fusione:** del PO. Il pacchetto non tocca il disegno: il PO guarda il costo con «Dove comprare»
di PR.MI.059 rifatto col listino completo.

## Le cose da fare

1. **Completare il listino Tecnomat, coi prezzi Tecnomat Pro** (I-304, I-311, I-313). Il file per la sessione Chrome,
   con le istruzioni, è `docs/rilievi/tecnomat-pro-da-rilevare.md`: **parte A**, le 150 righe Tecnomat che abbiamo,
   da verificare col prezzo Pro (Nove C ha l'abbonamento); **parte B**, i **62 codici** della distinta senza un prezzo
   Tecnomat che rispetti la voce, **prima i 30 di PR.MI.059**. Il
   rilievo si fa **come il 2 novembre: il PO e Claude insieme, con Claude in Chrome nel browser del PO** — dalla
   sessione cloud tecnomat.it non si apre (protezione anti-robot), e non si aggira. Il PO riporta il file riempito; la
   sessione mette le righe nel listino (un capitolo col rilievo e la sua data, colonna Fornitore «Tecnomat»), con ⚠
   dove l'articolo non rispetta la voce, e rifà `docs/collaudi/REL-027/pr-mi-059/misura.py`.
2. **Le risposte del PO del 18 novembre** (I-314 … I-320), da fare:
   - **a. Due liste materiali, tutte e due complete** (I-314). **Prezzata**, per l'analisi CAPEX: il costo prezza
     **anche le apparecchiature** (pompa di calore, bollitore, volano, circolatore, termostati, unità del clima), dal
     listino o DA PREZZARE; oggi le tiene fuori (D-235): la regola nuova si scrive come decisione del PO. **Senza
     prezzi**, per la richiesta di fornitura: le voci fornite da Nove C hanno la nota «fornita da Nove C» (il fornitore
     non le quota), oppure, se il PO lo chiede, non ci sono.
   - **b. Il bollitore con la superficie di scambio** (I-315, I-321): un bollitore non si sceglie solo dal volume; per
     la pompa di calore serve il serpentino maggiorato, e la superficie (m²) va nel grafo, nella tabella delle
     apparecchiature, nel listino e **nella voce della lista materiali che va al fornitore** («bollitore 200 l a
     serpentino maggiorato per pompa di calore, superficie di scambio non minore di … m²»), perché il fornitore non
     possa quotarne uno col serpentino piccolo; il confronto fra fornitori vale solo a pari superficie (o maggiore).
     Il PO: «se mi quoti un bollitore con 0.8 mq di serpentino ovvio che costa meno ma la pdc non funziona».
     **La fonte c'è** (I-323): manuale Shenling ThermaX R290 6–15 kW, §2.3 «Serbatoio dell'acqua calda sanitaria», p. 10
     (pagina 15 del PDF; il manuale è del PO, non nel repository) — «L'area di scambio termico del serbatoio dell'acqua
     calda sanitaria non deve essere inferiore al seguente valore consigliato»:

     | Modello | 6 kW | 9 kW | 12/15 kW |
     |---|--:|--:|--:|
     | Volume del serbatoio, l | 100–250 | 150–300 | 200–500 |
     | Area di scambio, serpentina smaltata, m² | 2,0 | 2,0 | 2,5 |
     | Area di scambio, serpentina inox, m² | 1,4 | 1,4 | 1,6 |

     E (punto 6): «La lunghezza del tubo tra l'unità esterna e il serbatoio deve essere inferiore a 5 metri». Su
     PR.MI.059 (12 kW): il Bolly 1 ST WB 200 di Idrosanitaria (0,8 m²) è molto sotto, e anche il Bolly 1 XL WB 200 di
     Abbattista (2 m²) sta sotto i 2,5 m² se la serpentina è smaltata (da verificare sulla scheda Cordivari): va detto al
     PO. Per le pompe di calore che non sono Shenling, la superficie minima si chiede al PO. Sulle due offerte di PR.MI.059: Bolly 1 XL WB 200 di Abbattista 2 m², Bolly 1 ST WB 200 di
     Idrosanitaria 0,8 m² (da confermare sulle schede Cordivari). **La superficie minima per kW della pompa di calore
     è contenuto MEP**: dalla scheda del costruttore della pompa di calore, o dal PO; non si inventa.
   - **c. Il rame «CONDY»** (I-316): nel preventivo Idrosanitaria non c'è isolante per il rame, quindi è il rivestito:
     le righe 50 e 51 del §5 prendono F01b e F03b.
   - **d. I raccordi agli attacchi delle macchine** (I-317, I-322): il raccordo «all'attacco» scrive il pollice
     dell'attacco della macchina (dal grafo o dal catalogo); se non c'è, è una domanda prima della lista, non un
     raccordo del pollice del tubo. Gli attacchi della Shenling ci sono già (I-281: R1" 6–9 kW, R1¼" 12–15 kW) e la
     skill li usa; mancano quelli delle altre macchine (bollitore, volano) e dei capi su reti esistenti: si registrano
     come la Shenling, dalle schede delle macchine che Nove C usa di solito.
   - **e. Le quantità nette** (I-320): regola fissa, senza la maggiorazione del 15%; i fornitori vendono a confezioni
     intere comunque. È anche in `REL-025`.
   - Risposte che non chiedono lavoro: l'imbuto di scarico non si conta (I-318); gli sconti nel repository pubblico
     vanno bene così (I-319).
   - Resta da sapere dal PO **in quale conversazione è stata fatta la lista di PR.MI.059**, per riportare nella skill
     le modifiche di quella copia.
3. **Le offerte nuove** dei fornitori, quando arrivano: un capitolo ciascuna nel listino, ogni riga col fornitore
   (I-304).

## Criteri di accettazione del punto 2

Prima le misure, poi il racconto; ogni criterio col comando e l'output nel rapporto (`docs/collaudi/REL-028/RAPPORTO.md`).

1. **2a.** `distinta --costo` prezza anche le apparecchiature (dal listino, o DA PREZZARE), comprese quelle fornite da
   Nove C; la lista senza prezzi per il fornitore dice «fornita da Nove C» su quelle voci, e un'opzione le toglie
   (prove). La regola nuova è scritta come decisione del PO (D-241), con la sua frase (I-314).
2. **2b.** La superficie di scambio del bollitore sta nel grafo e nel catalogo, nella tabella delle apparecchiature
   della tavola, nella voce della lista materiali («… superficie di scambio non minore di X m²», dal §2.3 del manuale
   per le Shenling) e nel listino; un bollitore con la superficie sotto il minimo è uno scostamento (⚠) nel confronto;
   la tubazione fra unità esterna e bollitore oltre i 5 m è un avviso (prove, e la tavola di un caso del banco col
   bollitore mostrata al PO se cambia).
3. **2c.** Le righe 50 e 51 del §5 del listino prendono F01b e F03b, con la nota della deduzione (I-316).
4. **2d.** Il raccordo «all'attacco» scrive il pollice dell'attacco della macchina quando il grafo o il catalogo lo
   sanno; senza, è una domanda prima della lista (prove sul caso della centrale e su PR.MI.059).
5. **2e.** Le quantità della lista sono nette, senza il 15% (prove; il documento lo dice).
6. **Le tavole al PO per prime** se una cambia; il banco verde con le impronte cambiate registrate e mostrate; suite a 0
   failed senza skip o xfail nuovi; ruff e mypy verdi; la release costruita con `scripts/costruisci-skill.py` e
   `tests/test_le_release.py` verde (il numero lo decide il PO: la proposta è 2.2.0, che assorbe le quantità nette di
   `REL-025`); la misura di PR.MI.059 rifatta; **non si fonde senza il sì del PO**.

## Fuori

Il contenuto di `REL-025` (la 2.2) e le fasi aperte di `REL-024`: l'ordine lo dice il PO.

## Criteri di accettazione

Si scrivono quando il PO avvia il pacchetto, sul lavoro che sceglie; per il punto 1: le righe rilevate nel listino con
fornitore, negozio, codice e data, le prove del listino verdi, la misura su PR.MI.059 rifatta e mostrata al PO, la
suite, ruff, mypy e il banco verdi, la release costruita con `scripts/costruisci-skill.py`.
