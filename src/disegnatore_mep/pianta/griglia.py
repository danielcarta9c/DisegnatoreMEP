"""La pianta su una griglia ortogonale: che cosa c'e' in ogni nodo.

La griglia ha il passo dei parametri (5 cm di regola) e i nodi su multipli
interi del passo, cosi' un muro dichiarato a 3,50 m cade su un nodo. Ogni nodo
sa se e' muro — e di che giacitura, perche' un muro si attraversa solo di
traverso —, se e' in un'apertura, se e' sotto un pezzo, in che stanza sta, se
c'e' il controsoffitto e quanto e' lontano dal muro piu' vicino. Quest'ultima
misura e' quella che fa le **corsie**: le strade lungo i muri.

Gli indici sono piatti — nodo `k = j * colonne + i` — perche' l'instradatore
li legge milioni di volte.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from .modello import Lato, Pianta

EPS = 1e-6

ATTRAVERSO_IN_VERTICALE = 1
"""Muro ad asse orizzontale: lo si passa solo andando su o giu'."""
ATTRAVERSO_IN_ORIZZONTALE = 2
"""Muro ad asse verticale: lo si passa solo andando a destra o a sinistra."""
ATTRAVERSO_QUALSIASI = 3
"""Muro obliquo: lo si passa dritti, in qualunque verso."""
INCROCIO_DI_MURI = 4
"""Un nodo in due muri di giacitura diversa: non si passa."""

MARGINE_M = 1.0
"""Quanto la griglia esce oltre la pianta: le macchine esterne stanno li'."""

DIREZIONI: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))
"""Destra, giu', sinistra, su: l'ordine fisso da cui dipende il determinismo."""

USCITA_DAL_LATO: dict[Lato, int] = {"destra": 0, "sotto": 1, "sinistra": 2, "sopra": 3}


@dataclass
class Griglia:
    passo: float
    i0: int
    j0: int
    colonne: int
    righe: int
    muro: list[int]
    giacitura: bytearray
    apertura: list[int]
    pezzo: list[int]
    stanza: list[int]
    controsoffitto: bytearray
    distanza: list[int]
    """Passi fino al nodo di muro piu' vicino (4-vicinato), con un tetto."""
    ingombri: list[tuple[int, int, int, int]] = field(default_factory=list)
    """I nodi di ogni pezzo: i_min, j_min, i_max, j_max."""
    esterno: bytearray = field(default_factory=bytearray)
    """1 dove si e' fuori dall'edificio: fuori da ogni stanza dichiarata, e
    raggiungibile dal bordo della griglia senza passare un muro. Li' il
    controsoffitto non si cerca: le linee corrono sulla facciata, in canalina."""

    def x(self, k: int) -> float:
        return round((self.i0 + k % self.colonne) * self.passo, 9)

    def y(self, k: int) -> float:
        return round((self.j0 + k // self.colonne) * self.passo, 9)

    def punto(self, k: int) -> tuple[float, float]:
        return self.x(k), self.y(k)

    def nodo(self, i: int, j: int) -> int:
        return j * self.colonne + i

    def dentro(self, i: int, j: int) -> bool:
        return 0 <= i < self.colonne and 0 <= j < self.righe

    def colonna_di(self, x: float) -> float:
        return x / self.passo - self.i0

    def riga_di(self, y: float) -> float:
        return y / self.passo - self.j0

    def nodi_del_rettangolo(
        self, x0: float, y0: float, x1: float, y1: float
    ) -> tuple[int, int, int, int]:
        """Gli indici dei nodi dentro un rettangolo, bordi compresi; almeno un
        nodo per asse, anche per un pezzo piu' piccolo del passo."""
        i_min = math.ceil(self.colonna_di(x0) - EPS)
        i_max = math.floor(self.colonna_di(x1) + EPS)
        j_min = math.ceil(self.riga_di(y0) - EPS)
        j_max = math.floor(self.riga_di(y1) + EPS)
        if i_min > i_max:
            i_min = i_max = round(self.colonna_di((x0 + x1) / 2))
        if j_min > j_max:
            j_min = j_max = round(self.riga_di((y0 + y1) / 2))
        return i_min, j_min, i_max, j_max

    def bordo_del_pezzo(self, indice: int, lato: Lato | None) -> list[tuple[int, int]]:
        """I nodi appena fuori da un pezzo, con la direzione che esce dal pezzo:
        da li' parte o li' arriva un tracciato. Senza lato, tutti e quattro."""
        i_min, j_min, i_max, j_max = self.ingombri[indice]
        # Gli spigoli no, se il lato ha posto: una linea che arriva sullo
        # spigolo del pezzo si legge come la prosecuzione del suo bordo.
        colonne = range(i_min + 1, i_max) if i_max - i_min >= 2 else range(i_min, i_max + 1)
        righe = range(j_min + 1, j_max) if j_max - j_min >= 2 else range(j_min, j_max + 1)
        lati: list[tuple[Lato, list[tuple[int, int]]]] = [
            ("destra", [(i_max + 1, j) for j in righe]),
            ("sotto", [(i, j_max + 1) for i in colonne]),
            ("sinistra", [(i_min - 1, j) for j in righe]),
            ("sopra", [(i, j_min - 1) for i in colonne]),
        ]
        out: list[tuple[int, int]] = []
        for nome, nodi in lati:
            if lato is not None and nome != lato:
                continue
            for i, j in nodi:
                if not self.dentro(i, j):
                    continue
                k = self.nodo(i, j)
                if self.muro[k] or self.pezzo[k]:
                    continue
                out.append((k, USCITA_DAL_LATO[nome]))
        return out


def costruisci_la_griglia(pianta: Pianta) -> Griglia:
    passo = pianta.parametri.passo_m
    xs: list[float] = []
    ys: list[float] = []
    for muro in pianta.muri:
        for x, y in (muro.da, muro.a):
            xs += [x - muro.spessore, x + muro.spessore]
            ys += [y - muro.spessore, y + muro.spessore]
    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        xs += [x0, x1]
        ys += [y0, y1]
    for stanza in pianta.stanze:
        xs += [p[0] for p in stanza.poligono]
        ys += [p[1] for p in stanza.poligono]
    for veletta in pianta.velette:
        xs += [veletta.rettangolo[0], veletta.rettangolo[2]]
        ys += [veletta.rettangolo[1], veletta.rettangolo[3]]
    if not xs:
        raise ValueError("la pianta e' vuota: niente muri, pezzi o stanze")
    i0 = math.floor((min(xs) - MARGINE_M) / passo)
    j0 = math.floor((min(ys) - MARGINE_M) / passo)
    colonne = math.ceil((max(xs) + MARGINE_M) / passo) - i0 + 1
    righe = math.ceil((max(ys) + MARGINE_M) / passo) - j0 + 1
    n = colonne * righe
    griglia = Griglia(
        passo=passo, i0=i0, j0=j0, colonne=colonne, righe=righe,
        muro=[0] * n, giacitura=bytearray(n), apertura=[0] * n, pezzo=[0] * n,
        stanza=[0] * n, controsoffitto=bytearray(n), distanza=[0] * n,
    )
    _i_muri(griglia, pianta)
    _le_aperture(griglia, pianta)
    _le_stanze(griglia, pianta)
    _i_pezzi(griglia, pianta)
    _la_distanza_dai_muri(griglia, pianta)
    _l_esterno(griglia)
    return griglia


def _l_esterno(griglia: Griglia) -> None:
    """Dal bordo della griglia, senza passare i muri (le aperture sono muro):
    i nodi che si raggiungono, fuori dalle stanze, sono l'esterno."""
    n = griglia.colonne * griglia.righe
    esterno = bytearray(n)
    coda: deque[int] = deque()
    for i in range(griglia.colonne):
        for j in (0, griglia.righe - 1):
            coda.append(griglia.nodo(i, j))
    for j in range(griglia.righe):
        for i in (0, griglia.colonne - 1):
            coda.append(griglia.nodo(i, j))
    colonne = griglia.colonne
    while coda:
        k = coda.popleft()
        if esterno[k] or griglia.muro[k] or griglia.stanza[k]:
            continue
        esterno[k] = 1
        i = k % colonne
        for vicino in (k + 1 if i + 1 < colonne else -1, k - 1 if i > 0 else -1, k + colonne, k - colonne):
            if 0 <= vicino < n and not esterno[vicino]:
                coda.append(vicino)
    griglia.esterno = esterno


def _asse(da: tuple[float, float], a: tuple[float, float]) -> tuple[float, float, float]:
    lunghezza = math.dist(da, a)
    return (a[0] - da[0]) / lunghezza, (a[1] - da[1]) / lunghezza, lunghezza


def _nodi_vicini_al_muro(
    griglia: Griglia, da: tuple[float, float], a: tuple[float, float], mezzo: float,
    s_da: float, s_a: float,
):
    """I nodi del rettangolo del muro fra le ascisse `s_da` e `s_a`, con la loro ascissa."""
    ux, uy, _ = _asse(da, a)
    nx, ny = -uy, ux
    angoli = [
        (da[0] + ux * s + nx * d, da[1] + uy * s + ny * d)
        for s in (s_da, s_a) for d in (-mezzo, mezzo)
    ]
    i_min = max(0, math.floor(griglia.colonna_di(min(p[0] for p in angoli))) - 1)
    i_max = min(griglia.colonne - 1, math.ceil(griglia.colonna_di(max(p[0] for p in angoli))) + 1)
    j_min = max(0, math.floor(griglia.riga_di(min(p[1] for p in angoli))) - 1)
    j_max = min(griglia.righe - 1, math.ceil(griglia.riga_di(max(p[1] for p in angoli))) + 1)
    for j in range(j_min, j_max + 1):
        for i in range(i_min, i_max + 1):
            k = griglia.nodo(i, j)
            vx, vy = griglia.x(k) - da[0], griglia.y(k) - da[1]
            s = vx * ux + vy * uy
            d = vx * nx + vy * ny
            if s_da - EPS <= s <= s_a + EPS and abs(d) <= mezzo + EPS:
                yield k, s


def _i_muri(griglia: Griglia, pianta: Pianta) -> None:
    for indice, muro in enumerate(pianta.muri, start=1):
        ux, uy, lunghezza = _asse(muro.da, muro.a)
        if abs(uy) < EPS:
            giacitura = ATTRAVERSO_IN_VERTICALE
        elif abs(ux) < EPS:
            giacitura = ATTRAVERSO_IN_ORIZZONTALE
        else:
            giacitura = ATTRAVERSO_QUALSIASI
        mezzo = muro.spessore / 2
        for k, _ in _nodi_vicini_al_muro(griglia, muro.da, muro.a, mezzo, -mezzo, lunghezza + mezzo):
            if griglia.muro[k] == 0:
                griglia.muro[k] = indice
                griglia.giacitura[k] = giacitura
            elif griglia.giacitura[k] != giacitura:
                griglia.giacitura[k] = INCROCIO_DI_MURI


def _le_aperture(griglia: Griglia, pianta: Pianta) -> None:
    muri = {muro.id: (indice, muro) for indice, muro in enumerate(pianta.muri, start=1)}
    for numero, apertura in enumerate(pianta.aperture, start=1):
        indice, muro = muri[apertura.muro]
        ux, uy, _ = _asse(muro.da, muro.a)
        centro = (apertura.centro[0] - muro.da[0]) * ux + (apertura.centro[1] - muro.da[1]) * uy
        mezza = apertura.larghezza / 2
        for k, _ in _nodi_vicini_al_muro(
            griglia, muro.da, muro.a, muro.spessore / 2, centro - mezza + EPS * 10, centro + mezza - EPS * 10
        ):
            if griglia.muro[k] == indice and griglia.giacitura[k] != INCROCIO_DI_MURI:
                griglia.apertura[k] = numero


def _spanne(poligono: list[tuple[float, float]], y: float) -> list[tuple[float, float]]:
    """Le porzioni di una riga orizzontale dentro un poligono (pari e dispari)."""
    tagli: list[float] = []
    for (xa, ya), (xb, yb) in zip(poligono, poligono[1:] + poligono[:1], strict=True):
        if (ya <= y < yb) or (yb <= y < ya):
            tagli.append(xa + (y - ya) * (xb - xa) / (yb - ya))
    tagli.sort()
    return list(zip(tagli[0::2], tagli[1::2], strict=False))


def _le_stanze(griglia: Griglia, pianta: Pianta) -> None:
    for indice, stanza in enumerate(pianta.stanze, start=1):
        poligono = [(float(x), float(y)) for x, y in stanza.poligono]
        for j in range(griglia.righe):
            y = griglia.y(griglia.nodo(0, j))
            for xa, xb in _spanne(poligono, y + EPS):
                i_da = max(0, math.ceil(griglia.colonna_di(xa) - EPS))
                i_a = min(griglia.colonne - 1, math.floor(griglia.colonna_di(xb) + EPS))
                for i in range(i_da, i_a + 1):
                    k = griglia.nodo(i, j)
                    griglia.stanza[k] = indice
                    if stanza.controsoffitto:
                        griglia.controsoffitto[k] = 1
    for veletta in pianta.velette:
        x0, y0, x1, y1 = veletta.rettangolo
        i_min, j_min, i_max, j_max = griglia.nodi_del_rettangolo(x0, y0, x1, y1)
        for j in range(max(0, j_min), min(griglia.righe - 1, j_max) + 1):
            for i in range(max(0, i_min), min(griglia.colonne - 1, i_max) + 1):
                griglia.controsoffitto[griglia.nodo(i, j)] = 1


def _i_pezzi(griglia: Griglia, pianta: Pianta) -> None:
    for indice, pezzo in enumerate(pianta.pezzi, start=1):
        ingombro = griglia.nodi_del_rettangolo(*pezzo.rettangolo)
        griglia.ingombri.append(ingombro)
        i_min, j_min, i_max, j_max = ingombro
        for j in range(max(0, j_min), min(griglia.righe - 1, j_max) + 1):
            for i in range(max(0, i_min), min(griglia.colonne - 1, i_max) + 1):
                griglia.pezzo[griglia.nodo(i, j)] = indice


def _la_distanza_dai_muri(griglia: Griglia, pianta: Pianta) -> None:
    tetto = math.ceil(pianta.parametri.centro_da_m / griglia.passo) + 2
    distanza = griglia.distanza
    coda: deque[int] = deque()
    for k in range(len(distanza)):
        if griglia.muro[k]:
            distanza[k] = 0
            coda.append(k)
        else:
            distanza[k] = tetto
    colonne = griglia.colonne
    while coda:
        k = coda.popleft()
        prossima = distanza[k] + 1
        if prossima >= tetto:
            continue
        i = k % colonne
        for vicino in (
            k + 1 if i + 1 < colonne else -1,
            k - 1 if i > 0 else -1,
            k + colonne,
            k - colonne,
        ):
            if 0 <= vicino < len(distanza) and distanza[vicino] > prossima:
                distanza[vicino] = prossima
                coda.append(vicino)
