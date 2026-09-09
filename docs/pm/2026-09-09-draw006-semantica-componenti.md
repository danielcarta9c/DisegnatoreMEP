# Traduzione PM — DRAW-006

**Data:** 2026-09-09  
**Autorità:** input PO; traduzione e fonti PM

## Decisioni di prodotto tradotte

- La `P` cerchiata è un manometro. Il suo organo di servizio è un rubinetto
  portamanometro a tre vie sulla presa, non una valvola ordinaria.
- Il gruppo di riempimento pubblicato incorpora già la propria intercettazione: una
  valvola esterna automatica è ridondante.
- Dalla release 0.3 la fixture grafica principale è l'impianto 2. La tavola 1 resta una
  regressione automatica; gli altri casi non vengono renderizzati senza necessità.
- Gli esempi sono fixture: le correzioni diventano proprietà di catalogo e regole
  generali, mai eccezioni sulla tavola.

## Verifica PM delle domande dell'impianto 4

La deviatrice non è un raccordo passante. La connettività interna cambia con lo stato:
ingresso verso circuito tecnico oppure ingresso verso scambiatore sanitario. Attraversare
simultaneamente tutte le porte produrrebbe una comunicazione inesistente.

Le domande sulla presenza a bordo delle sicurezze sono dati di catalogo legittimamente
ignoti. Il `NO_COMMON_RUN` globale rivela invece che il motore ragiona ancora per rete
intera: deve essere sostituito dalla valutazione dei domini garantiti in tutti gli stati
ammessi. Una protezione valida per la PDC non va scartata perché non protegge anche la
caldaia; quest'ultima si valuta separatamente nel ramo che la deviatrice può isolare.

## Fonti applicate

- Raccolta R 2009, cap. R.2.C, punto 2.5: manometro su generatore, mandata o ritorno senza
  intercettazioni interposte e presa per lo strumento di controllo.
- Raccolta R 2009, cap. R.3.B, punti 1, 2.4 e 2.5: sicurezza vicina al generatore e
  collegamento non intercettabile.
- Caleffi serie 690: rubinetto manometro-campione INAIL.
- Caleffi serie 335: pressostati distinti dal rubinetto a tre vie del manometro.
- Caleffi serie 553: gruppo di riempimento con dotazioni interne dichiarate.
- Caleffi serie 580, EN 1717, EN 12729 ed EN 806-5: variante con disconnettore e
  intercettazioni di manutenzione integrate.
- UNI EN 12828:2014: progettazione dei sistemi di riscaldamento ad acqua e dispositivi di
  sicurezza.

## Confine dell'incarico DEV

Il PM ha svolto scelta di dominio, fonti e traduzione. Il DEV implementa il contratto,
scrive prove generali e segnala incompatibilità; non ricerca nuovi requisiti, non decide la
dotazione dei prodotti e non modifica la governance.
