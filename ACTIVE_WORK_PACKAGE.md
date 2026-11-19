# REL-031 — La lista prezzata, i tappi e il volano standard, i prezzi del caso BD.RM.264 (la 2.3.0)

> **Scritto il 19 novembre 2026**, alla fusione della PR #102 (I-335). La 2.2.2 è su `main` (`REL-030`, PR #101).

**Da svolgere:** l'agente unico (**D-147**), nella sessione.
**Stato:** **DA AVVIARE.** L'input è del PO (I-335): «sono info per la prossima sessione di sviluppo di correzione della
skill». Il pacchetto applica quell'input; non decide contenuti MEP nuovi.
**Base:** `main` dopo la PR #102. Il ramo è quello assegnato alla sessione.
**Approvazione della fusione:** del PO, **dopo aver visto le tavole e la lista prezzata** (D-146).

## La fonte

`docs/input-pm/2026-11-19-handoff-bd-rm-264/`. Si leggono per primi `LEGGIMI.md` e
`SPEC_lista_prezzata_e_disegnatore.md` (i § qui sotto sono i suoi). Il riferimento visivo è
`BD.RM.264_Lista_materiali_prezzata_rev04.pdf`. Il caso si riproduce da `esempio/grafo.json` e `esempio/piano-*.json`.
`esempio/build_lista_prezzata.py` è lo script della sessione del 19/11, con i percorsi di quel container e le
correzioni scritte a mano: si legge, non si esegue e non si copia nella skill.

## Il lavoro, in ordine

1. **La lista prezzata (§1)** è un'uscita a sé della skill, distinta dalla distinta per l'installatore e da
   `costo-minuteria.md`. Si attiva su «lista prezzata», «lista materiali prezzata», «listino prezzato» e «CAPEX materiali».
   È un PDF impaginato con i report Nove C. Contiene la copertina con 4 KPI, il quadro economico nelle 5 sezioni fisse con
   le colonne Netto, IVA 22% e Totale IVA inclusa, un capitolo per sezione con il Rif. P./A./I./E./S., e il recap ordini
   per fornitore in ordine di importo decrescente.
   Le regole del §1 si implementano come sono scritte:
   - il fornitore è quello reale, oppure «Online»; mai «Fornitura Nove C» e nessuna colonna Note;
   - un articolo composto da articoli di fornitori diversi va su più righe;
   - restano fuori F, Z, G, V e H, le domande e le note;
   - della PdC a terra si quotano solo i piedini antivibranti (I71a, 4 pezzi);
   - quantità nette;
   - nessun «DA DEFINIRE» nel PDF: una voce senza prezzo si chiede al PO, oppure si applica il ripiego del punto 3.
   - **Da verificare all'avvio:** come la skill raggiunge l'impaginazione nove-c-report, che è un'altra skill, senza
     percorsi assoluti. Se non c'è una via pulita, si chiede al PO prima di scrivere codice.
2. **Disegno e distinta (§2):**
   - gli attacchi fisici completi del Bolly 1 XL; ogni attacco non collegato diventa un tappo del suo pollice, in distinta,
     in lista prezzata e col segno in tavola; la riduzione all'attacco va contata quando il pollice è diverso;
   - le schede Cordivari dei volani a 4 attacchi da 50 e 80 l, come volano standard di `buffer-four-port`, con raccordi,
     riduzioni e tappi;
   - l'avviso PdC–bollitore oltre 5 m letto anche da `distinta.tubi`;
   - nel catalogo, il «rubinetto di carico manuale con disconnettore», con simbolo, voce di distinta e articolo;
   - ai confini, il pollice del tubo del tratto come default.
3. **Prezzi (§3):**
   - aggancio per famiglia (Evosta 2 → M30a; cronotermostato wifi → E30a); se ci sono più taglie, si chiede;
   - una riga Shenling ThermaX R290 9 kW HPM-V90W/R3, fornitore Shenling, 2.450 € (dato del PO del 19/11/2026);
   - M01c corretta: è una Haier;
   - i ripieghi: guaina con lo spessore disponibile maggiore o uguale; miscelatrice col pollice più vicino. L'avviso va
     solo in chat.

## Domande al PO, prima del punto che le tocca

- Lo scarico O del bollitore: tappo o rubinetto (§2.1).
- Il numero degli attacchi C del Bolly 1 XL e la resistenza (§2.1). Si cercano prima sulla scheda Cordivari 02.2026; si
  chiede solo se non ci sono.
- Il prezzo reale del volano 50 l. I 95 € del caso sono una stima chiesta solo per BD.RM.264, e non entrano nel listino
  (§2.2).

## Criteri di accettazione

1. Sul caso BD.RM.264 la skill produce:
   - la lista prezzata con la stessa struttura della rev04: sezioni, colonne, recap ordini, nessun «Fornitura Nove C» e
     nessun «DA DEFINIRE»;
   - le tavole T1 e T1-E con i tappi del bollitore e del volano disegnati.
   La lista e le tavole si mostrano al PO **per prime**.
2. Le prove misurano: i tappi giusti per pollice sul Bolly 1 XL e sul volano 50 l; l'avviso dei 5 m da `distinta.tubi`
   con 16 m di primario; Evosta 2 e il cronotermostato wifi agganciati; la Shenling 9 kW a 2.450 €.
3. Banco, suite (0 failed, nessuno skip o xfail nuovo), ruff e mypy verdi. La release si costruisce con
   `scripts/costruisci-skill.py`, e `tests/test_le_release.py` deve essere verde. Non si fonde senza il sì del PO.

## Fuori dal pacchetto

L'import della pianta da PDF vettoriale quotato o da DXF (§4) e le cartelle di consegna (§4) restano annotati, e non si
sviluppano qui.
