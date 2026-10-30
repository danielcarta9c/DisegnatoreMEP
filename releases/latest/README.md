# L'ultima release: 1.6.0

`DisegnatoreMEP-v1.6.0.zip` — sha256 `5b5c6865adc77d11…`, 131 file — è **l'aria-aria, l'elettrico e il comando**
(`REL-012`), con **la distinta materiali** (`REL-013`) e **la pianta dei tracciati** (`REL-014`) su richiesta, dal
kit del PO del 29 ottobre 2026 (I-224 … I-229, D-213 proposta). Si carica come ogni skill personale, dallo ZIP così
com'è.

Rispetto alla 1.5.0:
- **l'aria-aria**: unità esterna, unità interna canalizzata, plenum di zona da 2 a 6 uscite, centrale di zona,
  bocchette, ripresa, sifone e scarico della condensa, termostati, comando a filo; linee frigorifere, aria, condensa;
- **l'elettrico e il comando**: quadro (fino a 6 uscite), sezionatore, regolatore d'impianto, sonde, e gli attacchi
  elettrici facoltativi sulle macchine idroniche (pompe di calore, caldaie, circolatori, valvole motorizzate,
  ventilconvettori); sulle centrali e sulle tavole dense **una tavola a parte**, sulle piccole la tavola unica (I-227);
- **sezione e lunghezza di ogni tratto** («Ø200 · L 6 m», «3G2,5 · L 20 m») come dato del progettista, con la sua
  riga di legenda; niente frecce di flusso su refrigerante, cavi e bus (proposta);
- **le tabelle sul foglio**: il piano riserva le zone, `disegna --tabelle` le posa;
- **la distinta materiali** (`mep.py distinta`), solo se il progettista la chiede: Excel per l'installatore a corpo,
  solo valori, ogni quantità con la sua regola; le scelte di fornitura dichiarate da confermare;
- **la pianta dei posizionamenti e dei tracciati** (`mep.py pianta`), solo se la chiede: instradamento ortogonale
  lungo i muri, curve e sormonti pagati, mai diagonali (I-229), fuori dall'edificio solo nelle zone esterne
  dichiarate, pezzi sovrapposti a quote diverse, dettaglio 1:20 dove serve; con `--distinta` e `--grafo` controlla che
  sigle, numeri di tratta e lunghezze siano quelli dello schema e della distinta;
- **i tre comportamenti del motore** trovati dal kit (sigle, etichetta in tabella, lato del sezionatore) corretti.

Le tavole idroniche della 1.5.0 non cambiano: il banco di regressione di `REL-011` (24 tavole) esce identico byte per
byte. Le prove e i tre collaudi indipendenti sono in `docs/collaudi/REL-012/`, `REL-013/`, `REL-014/`.

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
