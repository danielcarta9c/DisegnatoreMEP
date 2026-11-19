# Handoff di sviluppo dal caso BD.RM.264 — 19 novembre 2026 (I-335)

Il PO ha consegnato in chat uno zip (`BD.RM.264_handoff_sviluppo_disegnatore-mep.zip`) con questa richiesta:

> «analizza solo il contenuto dello zip, sono info per la prossima sessione di sviluppo di correzione della skill.
> Non sviluppare codice […] carica solo sulla repo le cose che servono per lo sviluppo che facciamo prox settimana».

Il contenuto è qui **com'era nello zip**, senza modifiche. Il documento da leggere per primo è `SPEC_lista_prezzata_e_disegnatore.md`.

## Cosa chiede, in breve

1. **«Lista prezzata» è un documento a sé** (§1): il PDF del modello `BD.RM.264_Lista_materiali_prezzata_rev04.pdf`,
   impaginato con nove-c-report. Copertina con 4 KPI, quadro economico in 5 sezioni fisse (Pompa di calore ·
   Apparecchiature · Circuito idraulico · Elettrico · Staffaggi) con Netto / IVA 22% / Totale IVA inclusa, un capitolo
   per sezione, recap ordini per fornitore. Non sono la distinta per l'installatore e non è `costo-minuteria.md`:
   quello che era stato consegnato per errore è in `esempio/PRIMA_distinta_installatore_NON_e_la_lista_prezzata.pdf`.
2. **Disegno e distinta** (§2): tappi sugli attacchi non usati del bollitore, con il segno in tavola; scheda del volano
   Cordivari standard a 4 attacchi da 50 e 80 l per `buffer-four-port`; avviso PdC–bollitore oltre 5 m letto anche da
   `distinta.tubi`; voce di catalogo «rubinetto di carico manuale con disconnettore»; pollice di default ai confini.
3. **Prezzi** (§3): matching per famiglia (Evosta 2, cronotermostato wifi); Shenling ThermaX R290 9 kW a 2.450 €
   (dato del PO); M01c da correggere (è una Haier); ripieghi su guaina e miscelatrice; fornitore «Online».
4. **Note** (§4): DWG 2007 non leggibile nel container; cartelle di consegna.

## I file

- `SPEC_lista_prezzata_e_disegnatore.md`: la specifica.
- `BD.RM.264_Lista_materiali_prezzata_rev04.pdf`: il riferimento della lista prezzata.
- `esempio/`: grafo e piani del caso per riprodurlo, le tavole T1 e T1-E, l'output attuale della skill
  (`costo-minuteria_skill.*`), le righe della lista (`dati_lista_prezzata.json`) e lo script che ha generato il PDF.

## Da sapere prima di usarli

- `esempio/build_lista_prezzata.py` **non è codice della skill**: è lo script della sessione, con percorsi del container
  di allora scritti a mano (`/root/.claude/skills/synced/…/nove-c-report`, `/tmp/mep/bd-rm-264/…`) e le correzioni
  manuali del §3 incise nel codice. Serve a capire come si è arrivati al PDF, non va eseguito così com'è.
- Alcuni dati nella specifica sono **del PO e da non generalizzare**: il volano 50 l a 95 € è una stima proporzionale
  chiesta solo per questo caso (§2.2); lo scarico O del bollitore (tappo o rubinetto) è da decidere col PO (§2.1).
- Le regole del §1 (sezioni, colonne, «mai Fornitura Nove C», niente colonna Note, quantità nette) sono disposizioni
  del PO: si implementano come sono scritte (`OPERATING_MODEL.md` §1.1.1).
