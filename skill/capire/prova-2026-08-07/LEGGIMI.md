# Le consegne della prova in camera pulita — 7 agosto 2026

> **Cosa c'è qui.** Quello che cinque agenti freschi hanno prodotto leggendo i cinque
> testi del committente con le sole istruzioni del pezzo «Capire». Sono gli **allegati
> del verbale**: servono perché chiunque, dopo, possa rifare il confronto invece di
> fidarsi delle conclusioni.
>
> La prova del 6 agosto era stata respinta proprio per questo — di quel confronto
> restavano solo le conclusioni. Da allora il contratto di consegna impone di
> conservare le consegne (`../CONSEGNA.md` §3).

## Come è stata condotta

Cinque cartelle di lavoro separate, una per impianto, ciascuna con **solo** il kit
previsto: le istruzioni, il testo del proprio impianto, il catalogo (53 voci), le
tabelle dei nomi e lo schema del modello. Nessun agente ha visto le letture manuali,
i grafi pubblicati, la documentazione del progetto o le prove automatiche. L'unica
cosa eseguibile fuori dalla propria cartella era il comando di validazione.

I cinque testi sono quelli originali del committente, **non modificati**: ogni
cartella ha ricevuto la propria sezione byte per byte, e le cinque sezioni rimesse
insieme ricompongono il file di partenza.

Ogni agente ha salvato **prima** il grafo, poi la tabella di rilettura, poi il
rapporto: se il lavoro si fosse interrotto a metà — è già successo in questo progetto
— il grafo sarebbe stato comunque agli atti.

Nessuno dei cinque ha dichiarato infrazioni all'isolamento.

## Cosa contiene ogni cartella

| File | Cosa |
|---|---|
| `grafo.json` | il grafo di prima stesura, come l'agente l'ha consegnato |
| `rilettura.md` | la tabella che lega ogni frase del testo agli elementi del grafo |
| `rapporto.md` | cosa l'agente ha capito, le domande e le assunzioni, e i punti in cui le istruzioni non gli hanno dato un criterio |

I file non sono stati toccati dopo la consegna.

## I tre giri, e perché sono tre

| Cartella | Cos'è | Esito |
|---|---|---|
| `giro-interrotto/` | due impianti soli | fermato: **il kit si contraddiceva** sul regime, e due agenti che non si vedevano l'hanno trovato |
| `giro-2-respinto/` | cinque impianti | **RESPINTO** su un difetto solo, e non sulla fedeltà: §4.2 non diceva **dove una rete può cominciare**, e il quinto grafo rompeva la catena |
| `impianto-1..5/` | cinque impianti | **APPROVATO** |

Ogni volta che le istruzioni sono cambiate, la prova è stata rifatta **da capo con agenti
nuovi**: un agente che ha già visto il confronto non è più in camera pulita
(`../CONSEGNA.md` §3). I giri precedenti restano perché i verbali dei loro collaudi si
leggono su di essi.

## Il verdetto

**APPROVATO**, dal collaudo a contesto separato che non ha scritto le istruzioni né
prodotto questi grafi. Su cinque impianti, 67 componenti e 82 tubazioni: **zero detto dal
testo e perso, zero inventato**. Il quinto coincide con la lettura manuale arco per arco.

Verbali in `../../../docs/collaudi/`, verdetti registrati nell'appendice del piano di
costruzione (`../../../docs/plans/2026-08-06-piano-costruzione-skill.md`). Le prove che
lo sostengono sono in `tests/collaudo/test_collaudo_interprete.py`.

**Resta un difetto aperto minore**, inchiodato da una prova marcata: una voce dichiarata
del primo grafo cita due identificativi interni del JSON in una frase destinata
all'ingegnere. Non si corregge a mano il grafo di un agente — è un allegato del verbale:
si chiude alle istruzioni, al prossimo giro.
