# Il giro interrotto del 7 agosto — perché è agli atti

> **Cosa c'è qui.** Le consegne dei primi due agenti della prova in camera pulita del
> pezzo «Capire», fermata dopo due impianti. Non sono la prova: sono la **prova del
> perché la prova è stata rifatta**.

## Cosa è successo

Due agenti, in due camere pulite separate, senza vedersi, hanno segnalato la stessa
cosa: **due documenti del kit dicevano l'opposto** su una delle quattro cose che
l'interprete deve capire, il regime della centrale.

- Le istruzioni, §4.6: il regime **si ricava** sommando le potenze che il testo dà —
  «si ricava, non si chiede».
- Lo schema del modello, descrizione di `PlantRegime`: il regime è un dato d'ingresso
  «mai calcolato… **nemmeno sommando le potenze che il testo nomina**».

Era il testo di D-106, rimasto in piedi dopo che D-108 lo aveva precisato. D-108 dice
che il regime è del progettista e che chi legge il testo lo **ricava dalle potenze che
lui ha già dichiarato**; le regole, invece, quel campo lo leggono e basta. La frase
vecchia era sopravvissuta in tre posti: lo schema, il sorgente da cui lo schema si
genera, e il documento delle regole che legge il PM.

## Perché la prova si è fermata

Una prova in camera pulita misura **se le istruzioni bastano da sole**. Con due
documenti del kit che si contraddicono, non misura più quello: misura quale dei due
l'agente ha letto per ultimo. Entrambi gli agenti hanno seguito le istruzioni e hanno
dichiarato la contraddizione — si sono comportati bene — ma il risultato non era più
interpretabile.

Corretti i tre punti (lo schema **rigenerato** dal sorgente, non modificato a mano), la
prova è ripartita da zero con agenti nuovi, come impone il protocollo di
`../../CONSEGNA.md` §3: un agente che ha già visto il confronto non è più in camera
pulita, e un kit cambiato è una prova da rifare.

## Cosa vale e cosa non vale, di questi file

**Vale** come riscontro che la contraddizione era reale e che due letture indipendenti
l'hanno trovata senza suggerimenti.

**Non vale** come consegna della prova: i grafi qui dentro sono stati prodotti con un
kit che si contraddiceva, e non sono stati confrontati con le letture manuali né
sottoposti al collaudo. La prova vera, e il suo verdetto, stanno nella cartella
accanto.

## I file

| Cartella | Cosa contiene |
|---|---|
| `impianto-1/` | grafo, tabella di rilettura e rapporto del primo agente |
| `impianto-2/` | grafo, tabella di rilettura e rapporto del secondo agente |

Nessuno dei due ha dichiarato infrazioni all'isolamento.
