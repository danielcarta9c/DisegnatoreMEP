"""I tratti interi nelle confezioni, senza giunte (`calcolo: confezioni`).

Il flessibile si vende in confezioni (10 m nel kit AA-01). Ogni tratto e' un pezzo
intero: le giunte del flessibile perdono aria e fanno rumore. I pezzi si mettono
nelle confezioni dal piu' lungo (first-fit decreasing), lasciando lo sfrido di ogni
confezione; poi si prende il maggiore fra le confezioni che servono e quelle della
riserva (lunghezza × (1 + riserva)). Un tratto piu' lungo della parte utile di una
confezione non ci sta intero: si spezza, e ogni spezzone in piu' e' una giunta che
la distinta conta e dice.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .lunghezze import TOLLERANZA, in_parole


@dataclass(frozen=True)
class Confezioni:
    numero: int
    riempimento: tuple[tuple[float, ...], ...]
    """I pezzi di ogni confezione, nell'ordine in cui ci sono entrati."""
    per_la_riserva: int
    giunte: int
    calcolo: str


def in_confezioni(pezzi: Sequence[float], confezione_m: float, sfrido_m: float, riserva: float) -> Confezioni:
    utile = confezione_m - sfrido_m
    if utile <= 0:
        raise ValueError("la confezione non ha parte utile: lo sfrido e' piu' lungo della confezione")
    spezzoni: list[float] = []
    giunte = 0
    for pezzo in pezzi:
        resto = pezzo
        while resto > utile + TOLLERANZA:
            spezzoni.append(utile)
            resto = round(resto - utile, 6)
            giunte += 1
        spezzoni.append(resto)
    riempimento: list[list[float]] = []
    for pezzo in sorted(spezzoni, reverse=True):
        for confezione in riempimento:
            if sum(confezione) + pezzo <= utile + TOLLERANZA:
                confezione.append(pezzo)
                break
        else:
            riempimento.append([pezzo])
    totale = sum(pezzi)
    per_la_riserva = math.ceil(totale * (1 + riserva) / confezione_m - TOLLERANZA)
    numero = max(len(riempimento), per_la_riserva)
    righe = " ".join("[" + " + ".join(in_parole(p) for p in c) + "]" for c in riempimento)
    calcolo = (
        f"{len(pezzi)} pezzi interi, {in_parole(totale)} m: in confezioni da {in_parole(confezione_m)} m "
        f"(utili {in_parole(utile)}) ne servono {len(riempimento)} {righe}; riserva "
        f"{in_parole(riserva * 100)}%: {in_parole(totale)} × {in_parole(1 + riserva)} = "
        f"{in_parole(totale * (1 + riserva))} m → {per_la_riserva}; si prende il maggiore: {numero}"
    )
    if giunte:
        calcolo += f"; {giunte} giunte: un tratto e' piu' lungo di una confezione"
    return Confezioni(
        numero=numero,
        riempimento=tuple(tuple(c) for c in riempimento),
        per_la_riserva=per_la_riserva,
        giunte=giunte,
        calcolo=calcolo,
    )
