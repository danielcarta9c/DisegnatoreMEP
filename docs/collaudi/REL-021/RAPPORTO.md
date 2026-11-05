# REL-020 e REL-021 — i collaudi della 1.14.0

Quattro agenti freschi, che conoscono solo lo ZIP della skill (non il repository, e non il numero di riferimento
del PO), hanno fatto da Claude con un progettista: grafo, `completa`, tavola, `distinta --costo`. I casi e i grafi
completi stanno nello scratchpad della sessione del 5 novembre 2026; il grafo completo del T1 è qui accanto.

| | impianto | prezzato (1.14.0 finale) | voci prezzate | DA PREZZARE |
|---|---|--:|--:|--:|
| T1 | Shenling 12 kW, deviatrice a 3 vie, volano 50 l, bollitore 200 l, un circuito al pavimento | 1.799,06 € | 58 | 12 |
| T2 | Shenling 9 kW, volano 100 l, bollitore 300 l, due zone (pannelli miscelati, radiatori), ricircolo | 2.369,29 € | 69 | 18 |
| T3 | canalizzato 7 kW, plenum a 4 serrande, 4 bocchette | 724,17 € | 24 | 23 |
| T4 | Shenling 6 kW su radiatori esistenti, volano 50 l | 674,20 € | 32 | 9 |

I numeri sono quelli della skill dopo le correzioni dei collaudi, ricalcolati sui grafi completi degli agenti
(`distinta --costo`). **Il riferimento del PO** (I-287): una PdC da 12 kW con la 3 vie, finita, costa a Nove C circa
**1.700 €** di minuteria, tubi ed elettrico, esclusi volano, bollitore e PdC. Il T1 prezzato è 1.799 €; le 12 voci
DA PREZZARE (interruttore tipo B, due antigelo, gruppo di sicurezza sanitario, cavi 3G1,5, relè, …) valgono, a stima
degli agenti, altri 500–650 €. **La skill sta quindi sopra il riferimento del PO del 30-40% a listino completo**,
mentre i quattro collaudatori, a mente e a prezzi da banco, la giudicano bassa. Le ragioni scritte:

- le quantità sono quelle della distinta per l'offerta a corpo, maggiorate (+15%, i minimi delle linee);
- i prezzi del listino sono al banco (Tecnomat) o mediane online, non i prezzi d'acquisto di Nove C;
- il rapporto fra il numero dei raccordi, dei gomiti e delle valvole e quello reale va tarato su una distinta vera
  del PO: è la prossima prova da fare.

## Corretto nella 1.14.0, dai collaudi

- T3: le protezioni di tipo A scritte a parole si prezzano col listino; il costo dice che il flessibile si paga a
  confezioni intere e che le apparecchiature escluse sono quelle della sezione A, macchine ad aria comprese.
- T4: il costo si scrive in `interno/`, e `consegna` non lo copia mai; gli stacchi di servizio (sicurezza, manometro,
  sfiato, scarico, sonda) sono avvitati sul tee, senza tubo; la domanda del tubo dice perché manca.
- T1: i raccordi all'attacco della pompa di calore contati tre volte (attacco, giunto, riduzione): ora uno per lato,
  dopo il giunto; un manicotto di riserva per tubo, non due; la taglia del vaso sanitario la dà il progettista.
- T2 e T4: la protezione si chiede solo sulle linee che partono dal quadro, non sui comandi che escono dalla scheda
  della pompa di calore.
- una riga per tubo d'acqua, comunque il progettista lo scriva («MS 26×3» e «multistrato MS 26×3»).

## Aperti, fuori da questi pacchetti (da proporre al PO)

1. **Le risposte della distinta su pezzi e tratti che `completa` crea** (stacchi, giunti, riduzioni, ingressi d'acqua
   fredda) si scrivono solo nel grafo completo, e un nuovo `completa` le cancella; **la lunghezza data resta sul primo
   spezzone** quando `completa` spezza una tubazione (T1, T2, T4). È il difetto che pesa di più sull'uso.
2. Il calcolo dei diametri non dà il tubo del primario in alcune disposizioni (T4: volano a quattro attacchi su
   radiatori esistenti): la tavola e la distinta lo lasciano senza.
3. Il gruppo di riempimento non si posa in un impianto di solo riscaldamento (manca la sorgente d'acqua fredda); il
   ritegno sul ricircolo sanitario non si posa (T2, T4).
4. Le sigle degli accessori (VI-, GR-, DEF-) sono nella distinta ma non sulla tavola (T1).
5. Le staffe a muro sono la regola anche con la pompa di calore a terra; mancano la posa esterna (finitura anti-UV,
   preisolato) e lo scarico della condensa di sbrinamento della monoblocco.
6. Il corrugato è contato per cavo, anche dove i cavi corrono insieme (T1, T2: 2-3 volte il necessario).
7. Testi dell'aria-aria nelle attività di un impianto idronico (tracce al controsoffitto, DiCo solo lettera a);
   testi di un'altra commessa nel canalizzato (T3: «portico», «pompa»).
8. `vaso` non dimensiona il vaso sanitario; `catalogo --cerca pavimento` non trova il pannello radiante; `comporre.md`
   rimanda a un collaudo che nello ZIP non c'è.
