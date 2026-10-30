# Collaudo indipendente — Disegnatore MEP v1.7.0

Base: `S=/tmp/claude-0/-home-user-DisegnatoreMEP/b6516f2f-ca66-5466-8ba2-b80294187e6d/scratchpad/collaudo-170`.
ZIP scompattato in `$S/skill/disegnatore-mep` (134 file). Usata solo la skill del pacchetto, nessun sorgente del repository.

## Le tavole escono: sì, tutte in A3

| caso | tavola | esito finale di `disegna` |
|---|---|---|
| 1 canalizzato (tavola unica) | `$S/consegna/caso1/canalizzato-appartamento-primo-piano-t1.pdf` (anteprima `$S/lavoro/caso1/tavola/canalizzato-appartamento-primo-piano-t1.png`) | `Formato A3 · tratte 17 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 8 · sormonti 0 · avvisi e regole: RETURN_RUNS_ABOVE_ITS_SUPPLY x1` |
| 2 villetta, idraulica | `$S/consegna/caso2/villetta-pdc-aria-acqua-idraulica-t1.pdf` (anteprima `$S/lavoro/caso2/tavola-idraulica/villetta-pdc-aria-acqua-idraulica-t1.png`) | `Formato A3 · tratte 27 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 1 · HIGHWAY_IS_NOT_STRAIGHT x1, PARALLEL_RUNS_WITHOUT_A_FREE_LANE x1, SERVICE_STUB_LONGER_THAN_ITS_MINIMUM x2, SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1` |
| 2 villetta, elettrico (T2-E) | `$S/consegna/caso2/villetta-pdc-aria-acqua-elettrico-t1.pdf` (anteprima `$S/lavoro/caso2/tavola-elettrico/villetta-pdc-aria-acqua-elettrico-t1.png`) | `Formato A3 · tratte 7 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 10 · sormonti 0 · PARALLEL_RUNS_WITHOUT_A_FREE_LANE x1` |
| distinta caso 1 | `$S/consegna/caso1/PROVA-01_Distinta_materiali_Climatizzazione_canalizzata_aria_aria.pdf` | 11 pagine A4, 81 voci, 6 voci DA DEFINIRE (marca e modello, che di proposito non ho dato); controllo dei report: un solo avviso, «Pag. 9: riempita al 69%» |

`pdfinfo`: le tre tavole sono `1190.55 x 841.89 pts (A3)`. Giri fatti: caso 1, tre pose (3 → 1 → 0 bloccanti; per trovare il posto della scritta del comando a filo ho provato 7 posizioni). Caso 2 idraulica, cinque pose (2 che non si instradavano, 1 con un bloccante, 1 aggrovigliata con 0 bloccanti, poi quella finale). Caso 2 elettrico: una posa, al primo colpo.

## Verifiche richieste

- **Sulla tavola solo la tabella delle apparecchiature e la legenda.** `pdftotext <tavola> | grep -ciE "tratt|computo|^ *note|distinta|T0[0-9]"` restituisce `0` su tutte e tre le tavole; a vista c'è solo la tabella CODICE/DESCRIZIONE/CARATTERISTICHE/MARCA/MODELLO, più la legenda. **OK.**
- **Distinta: è in PDF, senza KPI e senza «Chi siamo», senza Excel e senza prezzi.** La copertina (qa-1.png) porta titolo, commessa e il riquadro «A corpo, fisso e invariabile · quantità indicative · Sopralluogo obbligatorio». Non ha le card dei KPI né la pagina «Chi siamo». Nella cartella non c'è nessun file xls/xlsx (`ls *xls*` → No such file). Nel testo nessun simbolo `€` (`grep -c "€"` → 0) e nessun importo. **OK**, salvo i codici interni (D2).
- **Caso 1: le linee dell'aria e quelle frigorifere non sono disturbate dai cavi.** Sormonti 0. Le frigorifere sono rette fra UE e UI, la mandata e i tre rami sono retti. Bus e alimentazioni girano tutti sotto e a destra, e non toccano le linee dell'aria. **OK.** I difetti minori a vista sono in D5–D8.
- **Caso 2: alimentazione della pompa di calore, sonde e uscite sulla tavola dell'elettrico.** GT-01 è alimentata da QE-01 (uscita di sinistra). SO-02 «bollitore» e SO-01 «volano» vanno agli ingressi sonda di GT-01. Dalle uscite di sopra partono VD-01 (la tre vie) e CIR-01, e CIR-01 ha anche la sua alimentazione da QE-01. Il comando a filo CF-01 «Soggiorno» è sotto la macchina. Non c'è nessun regolatore esterno. **OK.** La legenda rimanda in modo incrociato a T2 e T2-E.
- **La skill si carica e si capisce.** `mep.py ambiente` → «Pronto.» (Python 3.13, pydantic 2.13, DXF sì, anteprima con pypdfium2). `SKILL.md` ha 411 righe e la descrizione 199 caratteri. Il flusso si segue. Le lacune che ho trovato sono in D4, D9 e D10.

## Risposte che ho dato da progettista (inventate)

- **Caso 1.**
  - Rami d'aria Ø160 da 5, 4 e 6 m; ripresa Ø200 da 1,5 m; condensa Ø32 da 3 m.
  - Linee elettriche: quadro–sezionatore–UE 3G2,5 da 12 m; centrale di zona alimentata dal quadro con 3G1,5 da 10 m (assunzione mia, il testo non lo dice); collegamento UE–UI 4G1,5 da 8 m; termostati e comando a filo 2×0,75. P1-P2 e motori delle serrande sono «di fabbrica» (L 0). Il comando a filo è sulla seconda coppia P1-P2 dell'unità interna.
  - Per la distinta: R32, precarica fino a 15 m, 20 g/m, massimo 30 m; attacco condensa Øe 20; bocchette 300×100; protezioni MTD C16 e C10; portate 250/200/350/800 m³/h; fornitura predefinita confermata (`--fornitura confermata`).
  - Marca e modello non dati. Pianta no. Revisione «in questa conversazione».
- **Caso 2.**
  - Volano a 4 attacchi come separatore. Acqua fredda e utenze del bollitore disegnate.
  - Circolatore alimentato dal quadro. Il vaso sanitario (punto aperto di `completa`) non c'è.
  - Collettore a 6 vie: «procedi senza» (vedi D3).
  - Diametri, distinta e pianta: no.

## Difetti, in ordine di gravità

### Bloccanti
Nessuno: tutte le tavole e il PDF sono usciti, e la skill si è caricata.

### Da correggere

- **D1. Una tavola chiaramente sbagliata passa con 0 rilievi bloccanti.** Prova: `$S/lavoro/caso2/tavola-groviglio/villetta-pdc-aria-acqua-idraulica-t1.png` (piano `$S/lavoro/caso2/piano-idraulica-groviglio.json`). Il comando dà `rilievi bloccanti 0 · pieghe 22 · sormonti 3`.
  - A vista il ritorno generale verso GT-01 è un groviglio: sale, torna indietro, scavalca sé stesso due volte, e il defangatore sta su una piega.
  - Il gruppo di riempimento è disegnato di traverso, e la sua acqua fredda sembra un tratteggio staccato.
  - I rilievi lo vedono (`HIGHWAY_IS_NOT_STRAIGHT`: «piegano 11 volte… 7 di troppo», `INLINE_ORGAN_BREAKS_THE_RUN`, `RUN_LEAVES_ITS_QUOTA_AND_COMES_BACK`), ma nessuno di questi blocca.
  - La causa è una mia posa: i raccordi in ordine inverso a quello della catena e il gruppo di riempimento senza rotazione. Una tavola così però non dovrebbe risultare «consegnabile».
  - `pezzi` non dice in che ordine i raccordi stanno sulla tratta. Per saperlo ho dovuto leggere le `connections` del grafo completo, e `comporre.md` non lo chiede.
- **D2. La distinta PDF contiene codici interni, contro quello che la stessa skill garantisce** («Niente prezzi e niente codici interni nel documento», `distinta.md`). Prova: `pdftotext … | grep "D-190"` restituisce 6 righe, a pag. 9, «marca e modello li da' il progettista (D-190)». A pag. 10 c'è «(regole 05a61bb20ef686d8)». C'è anche un refuso, «da'» al posto di «dà».
- **D3. Il catalogo non ha un collettore a più di 2 vie.** `catalogo zone-manifold-pair` dà le porte `out_1, out_2, ret_1, ret_2`, e basta. Il «collettore a 6 vie» del caso 2 non si può disegnare: sulla tavola c'è un pannello rappresentativo con la scritta «impianto a pavimento (collettore a 6 vie)». È un caso di villetta molto comune.
- **D4. Le domande per la distinta arrivano in un secondo giro.** Il passo 2 di `SKILL.md` chiede sezioni e lunghezze, ma non i dati che la distinta vuole: refrigerante, precarica, dimensione delle bocchette, attacco della condensa, protezioni, portate. Al primo lancio `distinta` è uscita con «DA DEFINIRE — 12 voci», e ho dovuto rifare le domande al progettista.

### Minori

- **D5. Caso 1: falso positivo sul bus.** `RETURN_RUNS_ABOVE_ITS_SUPPLY` (B10) su c19/c14 dice «il ritorno fra UI-01 e CZ-01 corre sopra la mandata fra CF-01 e UI-01 … sulla rete bus»: un bus non ha mandata né ritorno.
- **D6. Caso 1: la scritta del comando a filo è difficile da posare.** `FREE_LABEL_OMITTED` su «Soggiorno» di CF-01 anche quando a vista c'era spazio. Ho dovuto provare 7 posizioni: 3 su 7 danno ancora bloccanti.
- **D7. Caso 1: richiami ambigui.**
  - Al sezionatore SZ-01 la sigla e la scritta «3G2,5» hanno due richiami che finiscono sullo stesso punto del simbolo.
  - La freccia di SIF-01 indica il tubo sotto il sifone, non il sifone.
  - La scritta «Ø32» verticale tocca la freccia del flusso (zoom `$S/lavoro/caso1/zoom5.png`).
- **D8. Caso 1: nomi diversi fra legenda e tabella.** La legenda dice «Unità esterna ad espansione diretta», la tabella «Unità esterna split a pompa di calore».
- **D9. Caso 2 idraulica: confini e legenda.** Prove: `$S/lavoro/caso2/zoom-acs.png` e `$S/lavoro/caso2/zoom-legenda.png`.
  - I confini di rete (ingresso dell'acqua fredda, utenze, acqua fredda della miscelatrice) sono frecce senza sigla né scritta.
  - La sigla SO-02 sta fra la freccia dell'acqua fredda e la sonda.
  - Il bollitore mostra un moncone sull'attacco del ricircolo, che non è usato.
  - Nella legenda le icone alte (sfiato, volano, bollitore) si toccano e scavalcano le righe di testo.
- **D10. Caso 2 elettrico: comandi e alimentazioni uguali.** I comandi delle uscite di GT-01 verso VD-01 e CIR-01 hanno lo stesso tratto e lo stesso colore dell'«Alimentazione elettrica». La legenda non distingue un comando da un'alimentazione.
- **D11. `comporre.md` rinvia a `docs/collaudi/REL-015/pdc-regola/`**, che non è nello ZIP. Le istruzioni sono piene di codici D-/I- che un agente su claude.ai non può aprire. Non bloccano, ma pesano: `capire.md` è di 942 righe e `comporre.md` di 726, entrambi «da leggere per intero».

## Dove sta il resto

- Grafi e piani: `$S/lavoro/caso1/`, `$S/lavoro/caso2/` (`grafo.json`, `grafo-completo.json`, `piano*.json`).
- Rilievi delle tavole: `$S/consegna/caso*/…-rilievi.md`.
- Pagine della distinta in PNG: `$S/lavoro/caso1/distinta/PROVA-01_Distinta_materiali_Climatizzazione_canalizzata_aria_aria-pagine/qa-1..11.png`.
- Script che ho usato per scrivere i grafi (fuori dalla skill): `$S/script/g1.py`, `$S/script/g2.py`.

## Che cosa ne ha fatto la sessione — 30 ottobre 2026

Il collaudo è di un agente che ha usato solo lo ZIP (`DisegnatoreMEP-v1.7.0.zip` della prima costruzione,
sha256 `7d0f9406…`), su due casi inventati. Le tavole del collaudo sono in questa cartella, in PNG.

- **D2 corretto** prima della PR: le domande della distinta non citano più «(D-190)» e le avvertenze non portano
  l'impronta delle regole, che resta in `distinta.json` e `distinta-calcoli.md`; «da'» è «dà». Prova:
  `tests/distinta/test_niente_codici_interni.py`, rossa senza la correzione. Lo ZIP 1.7.0 è stato ricostruito
  (sha256 `39031f6b…`).
- **D1** (una posa sbagliata del piano che esce con 0 bloccanti) e **D4** (le domande per la distinta al passo 2)
  toccano Comporre e Capire: al PO, con la PR.
- **D3** (il collettore a più di due vie): è un simbolo nuovo, convenzione grafica del PO.
- I minori restano registrati qui.
