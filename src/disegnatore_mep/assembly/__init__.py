"""L'assemblatore: la fila ordinata dei pezzi lungo ogni tubo.

Sta fra «completare» e «disporre» (D-093). Le regole dicono **cosa** manca e a
quale macchina si ancora; qui si decide **in che ordine** i pezzi stanno lungo
la tubazione, prima che esista qualunque disegno — e si legge sul grafo scritto,
non su una tavola (D-096).

**Perche' serve.** Senza, ogni regola infila il proprio accessorio per conto suo
e l'ordine che ne esce non lo ha deciso nessuno: dipende dall'ordine con cui le
regole vengono valutate, cioe' dall'ordine alfabetico dei nomi dei loro file. Un
ordine impiantistico deciso dal nome di un file non e' un ordine.

**Come lo decide, e non con dei numeri** (D-094). Ogni regola dichiara rispetto
a quali **mestieri** il proprio pezzo viene prima o dopo; il programma fa un
ordinamento su quei vincoli. Dare a ogni accessorio un numero di priorita'
sarebbe stato di nuovo un ordine arbitrario. Se due vincoli si contraddicono,
**si ferma e nomina le due regole** invece di produrre in silenzio una fila
sbagliata.

**Cosa non tocca.** I pezzi che il progettista ha scritto restano dove li ha
messi: si riordina soltanto cio' che le regole hanno aggiunto. La skill non
trasforma l'impianto che ha ricevuto.
"""

from .runs import (
    AssemblyError,
    Run,
    assemble,
    runs_of,
)

__all__ = ["AssemblyError", "Run", "assemble", "runs_of"]
