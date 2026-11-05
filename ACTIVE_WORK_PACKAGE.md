# REL-020 e REL-021 — La distinta idronica, e la distinta prezzata col listino

> **Scritto il 5 novembre 2026**, dopo `REL-019` (il listino della minuteria nella skill). Il PO: «Mentre gli agenti
> completano il listino puoi partire con rel-019 finito questo passa direttamente a rel-020 così correli tutto il
> corredo mep, idronico elettrico areaulico e espansione diretta. Al termine fai più test diversi anche con sub agenti
> freschi e verifica se i prezzi ti tornano realistici (esempio una pdc da 12 kw con sistema a 3 vie completata noi
> abbiamo come capex di minuteria tubi e elettrici sui 1700€, esclusi volani termici bollitori e pdc che li compro a
> parte). Poi fai merge e rilascia skill rev nuova da installare» (I-287).

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **CONSEGNATO** (5 novembre 2026) — la 1.14.0, fusa su disposizione del PO (I-287). **Il pacchetto
successivo non è scelto**: si chiede al PO (le candidate sono in `HANDOFF.md` e in `docs/collaudi/REL-021/RAPPORTO.md`).
**Base:** `main` dopo la PR #87 (la 1.12.1), con `REL-019` (PR #88) sotto.
**Ramo:** `claude/distinta-idronica-prezzata`.

## REL-020 — il corredo idronico della distinta (D-236, proposta della sessione)

- La sezione **I** «Circuito idraulico»: ogni voce idronica del catalogo ha il suo corredo (tutte tranne collettore
  solare, regolatore d'impianto e sonda esterna, che restano in X). Pompa di calore, accumuli e bollitori sono
  apparecchiature (A); gli accessori in linea portano sé stessi del pollice del tubo e i raccordi a pressare; le
  derivazioni un tee; gli stacchi di servizio si avvitano sul tee; i terminali e la rete esistente sono confini.
- Le linee d'acqua (riscaldamento, acqua calda e fredda sanitaria): tubo, gomiti (uno ogni 3 m), collari (uno ogni
  1,5 m), un manicotto di riserva, guaina; nastro e sigillanti una volta.
- Le valvole, i filtri, i giunti e i circolatori sono passanti: la linea da macchina a macchina è un tratto solo. I
  tratti corti in centrale senza lunghezza valgono 1 m (`se_manca_m`), con un avviso; l'acqua non aggiunge il metro
  per tratto della maggiorazione.
- Le domande dei tubi d'acqua si dicono per rete, quando i tratti sono tanti.

## REL-021 — la distinta prezzata (D-236)

- Ogni voce di materiale delle regole (idronico, elettrico, aria, frigorifero, condensa) ha il suo `prezzo`: un codice
  del listino, o la scelta sul valore di un dato (pollice, tubo, sezione del cavo, taglia del vaso, protezione).
- `mep.py distinta … --costo` scrive `interno/costo-minuteria.md` e `.json`: il costo a listino del materiale, escluse
  apparecchiature, opere e attività; le voci DA PREZZARE fuori dal totale, ciascuna col suo perché. `consegna` non
  copia il costo. Il documento per l'installatore resta senza prezzi (D-235).

## Le misure alla consegna

- Suite intera, ruff, costruzione della skill e `tests/test_le_release.py`: in `HANDOFF.md`.
- I collaudi con quattro agenti freschi e il confronto col riferimento del PO: `docs/collaudi/REL-021/RAPPORTO.md`.
- Le tavole non cambiano: il pacchetto non tocca il disegno.
