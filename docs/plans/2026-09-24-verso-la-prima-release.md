# Verso la prima release — proposta del 24 settembre 2026

**Stato: PROPOSTA della sessione** (I-118). **Che cosa viene dopo la 0.3 lo sceglie il PO**; con la
sua scelta si aggiornano `docs/plans/2026-09-03-release-plan.md` e il pacchetto successivo. Qui non
c'è nessuna decisione: c'è quello che manca, misurato, e una strada per chiuderlo.

Il PO, il 24 settembre 2026: «Alla fine parliamo di quali sono i prossimi step per arrivare alla
prima release della skill».

---

## Dove siamo

- **Il disegno regge.** Le cinque tavole di prova escono dal pianificatore in camera pulita e il PO le
  ha approvate due volte (I-109, I-117): «hanno proprio l'aspetto di tavole professionali». Sul lato
  del disegno è il cancello della 0.3 — cinque impianti, senza eccezioni legate agli identificativi
  degli esempi.
- **Quello che manca per chiamarla release** lo dice il piano: la 1.0 è la «pipeline completa dal
  modello approvato alla tavola verificata, documentazione di installazione, pacchetto versionato e
  collaudo sui casi di accettazione». E lo dice il rischio più vecchio del progetto
  (`PROJECT_STATE.md`, rischio 4): **la skill non è mai stata eseguita nella chat di lavoro**.

## I buchi, uno per uno

| | che cosa manca | come lo so |
|---|---|---|
| 1 | **L'ingresso della skill.** Ci sono l'architettura (`docs/SKILL.md`) e le istruzioni di tre pezzi (`skill/capire/`, `skill/comporre/`, `skill/rivedere/`), ma non il file che dice all'agente della chat come cucire i cinque pezzi — dal testo dell'ingegnere al PDF, con le domande e le due approvazioni in mezzo | nel repository non c'è un ingresso per la chat: `docs/SKILL.md` è il documento d'architettura |
| 2 | **Il PDF nel pacchetto.** Il motore scrive l'SVG; il PDF lo fa uno strumento di sessione che usa il browser dell'ambiente di sviluppo (`scripts/to-pdf.sh`). Nell'ambiente della chat va verificato che cosa c'è | `pyproject.toml` dipende solo da `pydantic`; `to-pdf.sh` dice di sé che non fa parte del nucleo |
| 3 | **Un impianto nuovo.** Regole, libreria e istruzioni del pianificatore sono state scritte e collaudate sui cinque di prova. Il collaudo vero è su testi che il progetto non ha mai visto | i cinque sono gli unici impianti in `examples/prova/` |
| 4 | **Il DXF** (I-072). Era la contropartita di due prezzi già pagati: la riproducibilità bit per bit (D-151) e il vincolo dell'A3 (D-148) | in `src/` non c'è codice che scriva un DXF |
| 5 | **Una suite verde.** 45 rosse, tutte del percorso che D-151 ha tolto dalla decisione della posa (il solutore); una release si pubblica «soltanto dopo verifica dei test» | `releases/README.md`; rapporto di `DRAW-017`, criterio 6 |
| 6 | **La libreria dei simboli certificata**: la matrice fonti, forma, porte e ingombri, approvata dal PO | `PROJECT_STATE.md`, rischio 5 |
| 7 | **Il pacchetto versionato**: `releases/latest/` e lo ZIP numerato (D-009), la guida d'installazione, il numero di versione — il pacchetto Python dice ancora `0.1.0` | `releases/latest/` e `releases/archive/` hanno solo il README |

## La strada proposta

1. **R1 — L'ingresso della skill e la prova nella chat.** Si scrive l'ingresso: i cinque pezzi
   cuciti, i due cancelli umani (l'ingegnere approva il grafo; il PO guarda le tavole), il PDF
   prodotto dentro il pacchetto. Si installa in un ambiente pulito e si fa girare **su un impianto
   nuovo**, dal testo al PDF. È il «cancello verticale» del piano, e va fatto per primo: dice che
   cosa si rompe davvero — tempi, strumenti che mancano, passaggi che oggi la sessione fa a mano.
2. **R2 — Il collaudo su impianti veri.** Due o tre testi di impianti di Nove C, scelti dal PO, mai
   visti dalle regole. Ogni rottura diventa una regola, un simbolo o una riga delle istruzioni, e le
   tavole vanno al PO come sempre.
3. **R3 — La pulizia per la release.** Il percorso del solutore e le sue prove escono dal pacchetto
   (restano nella storia di git); la suite torna verde; la libreria certificata (buco 6); il numero
   di versione allineato alla release; `releases/latest/`, lo ZIP numerato e la guida
   d'installazione.
4. **R4 — Il DXF**, se il PO lo vuole nella prima release.

**Dopo la release, come migliorie e non come cancelli**: l'anello (i vincoli dell'occhio come dati
per il pianificatore), `passa-per`, i rilievi di A2, A3 e B5. Le tavole sono già approvate senza, e
torneranno utili se gli impianti nuovi mostrano difetti che il pianificatore da solo non chiude.

## Che cosa serve dal PO

- **la scelta sul DXF**: dentro la prima release, o subito dopo;
- **due o tre testi di impianti veri** per R2 — non i cinque di prova;
- **il via libera a togliere il percorso del solutore** dal pacchetto: D-151 lo teneva «agli atti», e
  agli atti resta nella storia di git.
