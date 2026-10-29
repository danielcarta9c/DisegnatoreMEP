"""Le lunghezze dei tracciati: misurate sul percorso, e da quotare con la regola.

La lunghezza **misurata** e' quella della spezzata disegnata, dal bordo di un
pezzo a quello dell'altro. Quella **da quotare** e' la regola del kit
aria-aria (`lavoro/dimensionamento.py`, `da_quotare`), con i numeri che la
pianta dichiara in `maggiorazione`: non e' scritta qui dentro.

Le salite e le discese non si vedono in pianta: stanno nell'aggiunta della
regola, ed e' per questo che c'e'.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .instrada import Percorso
from .modello import Maggiorazione, Tracciato


@dataclass(frozen=True)
class Lunghezza:
    tratta: str
    fluido: str
    misurata_m: float
    da_quotare_m: float
    minimo_m: float | None
    """Il minimo del fluido, se e' lui a decidere la lunghezza da quotare."""


def da_quotare(misurata: float, regola: Maggiorazione, fluido: str) -> tuple[float, float | None]:
    """`(misurata + aggiunta) × fattore`, per eccesso all'arrotondamento, mai
    sotto il minimo del fluido. Torna anche il minimo, se ha deciso lui."""
    passo = regola.arrotondamento_m
    valore = math.ceil((misurata + regola.aggiunta_m) * regola.fattore / passo - 1e-9) * passo
    valore = round(valore, 6)
    minimo = regola.minimi_m.get(fluido)  # type: ignore[call-overload]
    if minimo is not None and minimo > valore:
        return float(minimo), float(minimo)
    return valore, None


def lunghezze(
    tracciati: list[Tracciato], percorsi: list[Percorso], regola: Maggiorazione
) -> list[Lunghezza]:
    out: list[Lunghezza] = []
    for tracciato, percorso in zip(tracciati, percorsi, strict=True):
        misurata = round(percorso.lunghezza_m, 3)
        quotare, minimo = da_quotare(misurata, regola, tracciato.fluido)
        out.append(
            Lunghezza(
                tratta=tracciato.tratta, fluido=tracciato.fluido, misurata_m=misurata,
                da_quotare_m=quotare, minimo_m=minimo,
            )
        )
    return out


def metri(valore: float, decimali: int = 1) -> str:
    """6 → «6», 6.5 → «6,5», 2.35 → «2,4»: la virgola, e niente zeri inutili."""
    testo = f"{valore:.{decimali}f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",")
