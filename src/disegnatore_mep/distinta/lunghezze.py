"""La regola delle lunghezze da quotare (`rules/distinta/lunghezze.json`).

    L da quotare = (L + aggiunta) × fattore, per eccesso al passo,
                   mai sotto il minimo del fluido ne' sotto quello scritto sul tratto.

La L e' il dato del progettista. Nel kit AA-01: aggiunta 1 m, fattore 1,15, passo
0,5 m; minimi 12 m per le linee frigorifere, 10 m per la condensa, 5 m per il bus,
2 m per un ramo d'aria. Ogni lunghezza esce con il conto scritto, perche' il
progettista e l'installatore lo possano rifare.
"""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

TOLLERANZA = 1e-9
"""12 / 1,2 fa 10,000000000000002 in virgola mobile: l'eccesso non deve contare il rumore."""


def per_eccesso(valore: float, passo: float) -> float:
    """Il multiplo del passo subito sopra (o uguale)."""
    return round(math.ceil(valore / passo - TOLLERANZA) * passo, 6)


def quante_volte(valore: float, passo: float) -> int:
    """Quanti passi servono a coprire il valore, per eccesso."""
    return max(0, math.ceil(valore / passo - TOLLERANZA))


def in_parole(valore: float, cifre: int = 2) -> str:
    """6 → «6», 3.5 → «3,5», 0.052 → «0,052»: la virgola, senza zeri in coda."""
    testo = f"{valore:.{cifre}f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",") if testo not in ("", "-0") else "0"


@dataclass(frozen=True)
class Minimo:
    metri: float
    perche: str
    """Da dove viene: «minimo frigo», «minimo scritto sul tratto», «segue T07 + 1 m»."""


@dataclass(frozen=True)
class LunghezzaDaQuotare:
    stimata: float
    da_quotare: float
    calcolo: str


def da_quotare(stimata: float, regola: Mapping[str, Any], minimi: Sequence[Minimo] = ()) -> LunghezzaDaQuotare:
    aggiunta = float(regola["aggiunta_m"])
    fattore = float(regola["fattore"])
    passo = float(regola["passo_m"])
    grezza = (stimata + aggiunta) * fattore
    maggiorata = per_eccesso(grezza, passo)
    calcolo = (
        f"({in_parole(stimata)} + {in_parole(aggiunta)}) × {in_parole(fattore)} = {in_parole(grezza)}"
        f" → {in_parole(maggiorata)} m"
    )
    risultato = maggiorata
    for minimo in minimi:
        if minimo.metri > risultato + TOLLERANZA:
            risultato = minimo.metri
            calcolo += f"; {minimo.perche} {in_parole(minimo.metri)} m → {in_parole(risultato)} m"
    return LunghezzaDaQuotare(stimata=stimata, da_quotare=risultato, calcolo=calcolo)
