"""Le scritte che in pianta non trovano posto: fuori, nello spazio bianco attorno.

REL-026, C-1 (LEGGIMI M2 di BD.RM.260). Fino alla 2.0 una scritta che non stava ne'
accanto al suo oggetto, ne' con un richiamo corto, ne' come numero cerchiato in legenda
apriva da sola un riquadro di dettaglio: sulla commessa, un A3 con due tubi e le parole
mandata e ritorno. Ora va **fuori dalla pianta**, nei margini del campo del disegno,
collegata al suo oggetto da una linea di richiamo. I numeri cerchiati restano dove
erano: questo e' solo il posto di quello che prima apriva il dettaglio.

- **Incolonnate.** A destra della pianta le scritte stanno allineate a sinistra, a
  sinistra allineate a destra, tutte alla stessa distanza dalla pianta e su una griglia
  a passo fisso (`PASSO_MM`). Sopra e sotto, dove il margine e' basso ma largo — una
  scritta di tratta e' lunga 25-45 mm, e i margini di fianco su un A3 ne hanno 11-27 —,
  stanno su righe a passo fisso, ciascuna sopra (o sotto) il suo oggetto.
- **Il richiamo e' ortogonale, con al piu' un gomito**: dritto quando il punto d'attacco
  puo' scorrere fino all'altezza della scritta (un tratto del tubo, il fianco del pezzo).
  Parte dall'oggetto verso fuori; correre su una linea o un muro, o accanto, costa al
  millimetro (`COSTO_SOPRA`, `COSTO_ACCANTO`): si confonderebbe con loro.
- **I richiami non si incrociano**: ne' fra loro ne' con i richiami corti; e non passano
  su un'altra scritta fuori. E' un vincolo. Sopra le scritte e i pezzi della pianta
  passano solo se non c'e' altro modo: costa molto, e il controllo li conta.
- Fra i posti possibili si sceglie quello col richiamo che costa meno: la lunghezza, un
  gomito, le linee e i pezzi che attraversa (`COSTO_*`). Il lato piu' vicino all'oggetto
  viene da se'; e siccome due richiami dritti sullo stesso lato sono paralleli, l'ordine
  delle scritte di una colonna e' quello dei loro punti d'attacco.

Una scritta che non trova posto nemmeno fuori torna `None`. Allora, e quando un richiamo
passa su una scritta o un pezzo o e' piu' lungo di `LUNGO_MM`, la tavola prova a spostare
la pianta sul foglio; se non basta, passa al formato successivo (`tavola.componi`, la
stessa regola della colonna che non entra); e solo se un formato dopo non c'e' la scritta
resta senza posto, e il controllo la conta.

Tutto in millimetri di carta, come `scritte.py`. Deterministico: a parita' di costo vince
il primo nell'ordine fisso dei lati, dei posti e dei punti.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from .scritte import (
    ARIA_MM,
    Ingombri,
    Rettangolo,
    ScrittaPosata,
    Segmento,
    _riquadro,
    _riquadro_del_segmento,
    _segmento_tocca,
    _sovrapposti,
    misura,
)

Punto = tuple[float, float]
Lato = Literal["destra", "sinistra", "sopra", "sotto"]
LATI: tuple[Lato, ...] = ("destra", "sinistra", "sopra", "sotto")

STACCO_MM = 3.0
"""Il bianco fra la pianta e le scritte fuori."""

PASSO_MM = 4.5
"""Il passo della griglia delle scritte fuori: una riga di testo e il suo bianco, per le
sigle (9 pt) come per le scritte delle tratte (8 pt)."""

SPESSORE_MM = 0.18
"""Il tratto del richiamo, come quello dei richiami corti."""

FINE_MM = 0.6
"""Quanto il punto d'attacco sta lontano dai capi di un tratto, e il primo pezzo del
richiamo si accorcia per non contare l'oggetto da cui parte."""

VICINO_MM = 0.6
"""Un punto d'attacco piu' vicino di cosi' a una linea non sua e' un incrocio: no. Meno
del passo della griglia dell'instradatore sulla carta (5 cm a 1:50, 1 mm): due linee
vicine di un passo non si escludono a vicenda."""

DENTRO_MM = 0.2
"""Un punto d'attacco dentro un muro o un pezzo non suo, di piu' di cosi', no; sul bordo
si' (la linea che costeggia il plenum)."""

PASSO_DEI_PUNTI_MM = 1.0
"""Ogni quanto si prova un punto d'attacco lungo un tratto, per un richiamo dritto."""

PASSO_DEI_GOMITI_MM = 2.0
"""Ogni quanto, per un richiamo col gomito: ce ne sono molti di piu', e un millimetro in
piu' o in meno del gomito non cambia la tavola."""

SCOSTAMENTI_MM = (3.0, 6.0, 10.0, 15.0)
"""Per una riga sopra o sotto, raggiunta da un tratto verticale: quanto il gomito si
scosta dal tratto."""

COSTO_GOMITO = 8.0
"""Un gomito vale 8 mm di richiamo dritto: a parita', il richiamo dritto."""
COSTO_LINEA = 15.0
"""Una linea dei tracciati attraversata."""
COSTO_TRATTINO = 2.0
"""Un tratto delle aperture (l'anta, l'arco della porta) o della cornice di un dettaglio."""
COSTO_MURO = 2.0
"""Un muro attraversato: per uscire dall'edificio se ne passa almeno uno."""
COSTO_ACCANTO = 3.0
"""Ogni millimetro di richiamo che corre accanto a una linea (a meno di `ACCANTO_MM`) o
dentro un muro: si confonde con lei."""
ACCANTO_MM = 4.0
COSTO_SOPRA = 20.0
"""Ogni millimetro di richiamo che corre sopra una linea: non si legge piu' nessuno dei due."""
COSTO_OSTACOLO = 1000.0
"""Una scritta o un pezzo della pianta sotto il richiamo: solo se non c'e' altro modo."""


@dataclass(frozen=True)
class Richiesta:
    """Una scritta da portare fuori, e l'oggetto a cui si attacca il suo richiamo."""

    chi: str
    testo: str
    corpo_pt: float
    grassetto: bool
    linee: tuple[tuple[Punto, ...], ...] = ()
    """Le spezzate di un tracciato, sulla carta: il richiamo parte da un loro punto."""
    rettangolo: Rettangolo | None = None
    """Il pezzo (o la foratura): il richiamo parte dal suo bordo, verso fuori."""
    sotto: tuple[Rettangolo, ...] = ()
    """I pezzi sotto cui la linea passa (sovrapposti a un suo capo): il richiamo ci puo'
    partire sopra, come la scritta accanto (`scritte.posa_accanto`)."""


@dataclass(frozen=True)
class _Tratto:
    """Un tratto da cui il richiamo puo' partire, e verso dove: per un tratto orizzontale
    -1 e' su e +1 giu', per uno verticale -1 a sinistra e +1 a destra."""

    a: Punto
    b: Punto
    orizzontale: bool
    versi: tuple[int, ...]

    def punti(self, passo: float = PASSO_DEI_PUNTI_MM) -> Iterator[Punto]:
        """I punti d'attacco lungo il tratto, lontani dai capi, a passo fisso."""
        asse = 0 if self.orizzontale else 1
        lo, hi = sorted((self.a[asse], self.b[asse]))
        lo, hi = lo + FINE_MM, hi - FINE_MM
        if hi < lo:
            return
        # Un tratto corto (il cavo fra due pezzi vicini) si prova fitto: ha pochi punti, e
        # vicino ai capi molti non vanno bene.
        passi = max(1, int((hi - lo) / min(passo, max(0.25, (hi - lo) / 8))))
        for indice in range(passi + 1):
            v = round(lo + (hi - lo) * indice / passi, 3)
            yield (v, self.a[1]) if self.orizzontale else (self.a[0], v)

    def contiene(self, v: float) -> bool:
        """Il tratto passa per la coordinata `v` (y se verticale, x se orizzontale)."""
        asse = 0 if self.orizzontale else 1
        lo, hi = sorted((self.a[asse], self.b[asse]))
        return lo + FINE_MM <= v <= hi - FINE_MM


def _tratti(richiesta: Richiesta) -> list[_Tratto]:
    out: list[_Tratto] = []
    for punti in richiesta.linee:
        for a, b in zip(punti, punti[1:], strict=False):
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 2 * FINE_MM:
                continue
            out.append(_Tratto(a, b, abs(a[1] - b[1]) < 1e-9, (-1, 1)))
    if richiesta.rettangolo is not None:
        x0, y0, x1, y1 = richiesta.rettangolo
        out += [
            _Tratto((x0, y0), (x1, y0), True, (-1,)), _Tratto((x0, y1), (x1, y1), True, (1,)),
            _Tratto((x0, y0), (x0, y1), False, (-1,)), _Tratto((x1, y0), (x1, y1), False, (1,)),
        ]
    return out


@dataclass(frozen=True)
class _Posto:
    """Un posto per la scritta fuori: la linea di base, e il punto del suo bordo dove
    arriva il richiamo."""

    lato: Lato
    indice: int
    x: float
    y: float
    riquadro: Rettangolo
    arrivo: Punto


def _posti_in_colonna(
    lato: Lato, pianta: Rettangolo, area: Rettangolo, larghezza: float, salita: float, discesa: float,
) -> list[_Posto]:
    """La colonna a destra o a sinistra della pianta: per ogni passo della griglia, il
    posto della scritta e il punto del suo bordo dove arriva il richiamo, all'altezza
    del mezzo del testo. La griglia parte dal bordo alto dell'area: e' la stessa per
    tutte le scritte del lato, che restano a passo regolare."""
    out: list[_Posto] = []
    if lato == "destra":
        x = pianta[2] + STACCO_MM
        arrivo_x = x - ARIA_MM
    else:
        x = pianta[0] - STACCO_MM - larghezza
        arrivo_x = x + larghezza + ARIA_MM
    mezzo = (salita - discesa) / 2
    indice = 0
    while True:
        y_mezzo = area[1] + PASSO_MM * (indice + 0.5)
        base = y_mezzo + mezzo
        r = _riquadro(x, base, larghezza, salita, discesa)
        if r[0] < area[0] or r[2] > area[2]:
            return []  # la scritta e' piu' larga del margine
        if r[3] > area[3]:
            break
        out.append(_Posto(lato, indice, round(x, 3), round(base, 3), r, (round(arrivo_x, 3), round(y_mezzo, 3))))
        indice += 1
    return out


def _righe(lato: Lato, pianta: Rettangolo, area: Rettangolo, salita: float, discesa: float) -> list[tuple[int, float, float]]:
    """Le righe sopra o sotto la pianta: (indice, linea di base, y del bordo dove arriva
    il richiamo), dalla piu' vicina alla pianta in fuori."""
    out: list[tuple[int, float, float]] = []
    indice = 0
    while True:
        if lato == "sopra":
            bordo = pianta[1] - STACCO_MM - indice * PASSO_MM
            base = bordo - discesa - ARIA_MM
            if base - salita - ARIA_MM < area[1]:
                break
        else:
            bordo = pianta[3] + STACCO_MM + indice * PASSO_MM
            base = bordo + ARIA_MM + salita
            if base + discesa + ARIA_MM > area[3]:
                break
        out.append((indice, round(base, 3), round(bordo, 3)))
        indice += 1
    return out


def _posti_in_riga(
    lato: Lato, indice: int, base: float, bordo: float, x_arrivo: float, area: Rettangolo, larghezza: float,
    salita: float, discesa: float,
) -> list[_Posto]:
    """In una riga, i posti della scritta il cui bordo prende il richiamo verticale in
    `x_arrivo`: centrata sul richiamo, poi col richiamo all'inizio, poi alla fine."""
    out: list[_Posto] = []
    for x in (x_arrivo - larghezza / 2, x_arrivo - 1.0, x_arrivo - larghezza + 1.0):
        if x - ARIA_MM < area[0] or x + larghezza + ARIA_MM > area[2]:
            continue
        r = _riquadro(x, base, larghezza, salita, discesa)
        out.append(_Posto(lato, indice, round(x, 3), base, r, (round(x_arrivo, 3), bordo)))
    return out


Candidato = tuple[float, tuple[object, ...], tuple[Punto, ...], _Posto]
"""(lunghezza minima, chiave dell'ordine, richiamo, posto)."""


def _lunghezza(punti: Sequence[Punto]) -> float:
    return sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(punti, punti[1:], strict=False))


def _candidati(
    richiesta: Richiesta, tratti: list[_Tratto], pianta: Rettangolo, area: Rettangolo,
) -> list[Candidato]:
    """Tutti i richiami possibili, coi loro posti: dritti e con un gomito, su ogni lato."""
    larghezza, salita, discesa = misura(richiesta.testo, richiesta.corpo_pt, richiesta.grassetto)
    out: list[Candidato] = []

    def aggiungi(punti: tuple[Punto, ...], posto: _Posto, ordine: tuple[object, ...]) -> None:
        punti = tuple((round(x, 3), round(y, 3)) for x, y in punti)
        lunghezza = _lunghezza(punti) + (COSTO_GOMITO if len(punti) == 3 else 0.0)
        out.append((lunghezza, (LATI.index(posto.lato), posto.indice, *ordine), punti, posto))

    for lato in LATI[:2]:
        verso = 1 if lato == "destra" else -1
        for posto in _posti_in_colonna(lato, pianta, area, larghezza, salita, discesa):
            ax, ay = posto.arrivo
            for n, tratto in enumerate(tratti):
                if not tratto.orizzontale and verso in tratto.versi and tratto.contiene(ay):
                    px = tratto.a[0]
                    if (ax - px) * verso > FINE_MM:
                        aggiungi(((px, ay), (ax, ay)), posto, (n, 0.0))
                elif tratto.orizzontale:
                    py = tratto.a[1]
                    giu = 1 if ay > py else -1
                    if abs(ay - py) < VICINO_MM or giu not in tratto.versi:
                        continue
                    for px, _ in tratto.punti(PASSO_DEI_GOMITI_MM):
                        if (ax - px) * verso > FINE_MM:
                            aggiungi(((px, py), (px, ay), (ax, ay)), posto, (n, px))
    for lato in LATI[2:]:
        verso = -1 if lato == "sopra" else 1
        for indice, base, bordo in _righe(lato, pianta, area, salita, discesa):
            for n, tratto in enumerate(tratti):
                if tratto.orizzontale and verso in tratto.versi:
                    py = tratto.a[1]
                    if (bordo - py) * verso <= FINE_MM:
                        continue
                    for px, _ in tratto.punti():
                        for posto in _posti_in_riga(lato, indice, base, bordo, px, area, larghezza, salita, discesa):
                            aggiungi(((px, py), (px, bordo)), posto, (n, px, posto.x))
                elif not tratto.orizzontale:
                    px = tratto.a[0]
                    for _, py in tratto.punti(PASSO_DEI_GOMITI_MM):
                        if (bordo - py) * verso <= VICINO_MM:
                            continue
                        for fianco in tratto.versi:
                            for scosto in SCOSTAMENTI_MM:
                                gx = round(px + fianco * scosto, 3)
                                if not pianta[0] < gx < pianta[2]:
                                    # Il richiamo di una riga non corre nei margini di fianco:
                                    # li' sbarrerebbe la colonna.
                                    continue
                                for posto in _posti_in_riga(lato, indice, base, bordo, gx, area, larghezza, salita,
                                                            discesa):
                                    aggiungi(((px, py), (gx, py), (gx, bordo)), posto, (n, py, fianco, scosto, posto.x))
    out.sort(key=lambda c: (round(c[0], 3), c[1]))
    return out


def _incrociano(s: Segmento, t: Segmento) -> bool:
    """Due segmenti ortogonali (con il loro mezzo spessore) si toccano."""
    return _sovrapposti(_riquadro_del_segmento(s), _riquadro_del_segmento(t))


def _sopra(s: Segmento, t: Segmento) -> float:
    """Per quanti millimetri il richiamo `s` corre sulla linea `t` (paralleli, uno
    sull'altro): li' non si legge."""
    sx0, sy0, sx1, sy1, _ = s
    tx0, ty0, tx1, ty1, mezzo = t
    if abs(sy0 - sy1) < 1e-9 and abs(ty0 - ty1) < 1e-9 and abs(sy0 - ty0) < mezzo + 0.4:
        return max(0.0, min(max(sx0, sx1), max(tx0, tx1)) - max(min(sx0, sx1), min(tx0, tx1)))
    if abs(sx0 - sx1) < 1e-9 and abs(tx0 - tx1) < 1e-9 and abs(sx0 - tx0) < mezzo + 0.4:
        return max(0.0, min(max(sy0, sy1), max(ty0, ty1)) - max(min(sy0, sy1), min(ty0, ty1)))
    return 0.0


@dataclass
class _Stato:
    """Quello che le scritte fuori gia' posate impongono alle altre."""

    ingombri: Ingombri
    tubi: frozenset[Segmento]
    richiami: list[Segmento]
    """I richiami corti della pianta e quelli delle scritte fuori gia' posate: non si
    incrociano."""
    scritte_fuori: list[Rettangolo]


def _accorcia(a: Punto, b: Punto, quanto: float) -> Punto:
    """Il punto `a` spostato di `quanto` verso `b`."""
    if abs(a[0] - b[0]) < 1e-9:
        return (a[0], a[1] + quanto * (1 if b[1] > a[1] else -1))
    return (a[0] + quanto * (1 if b[0] > a[0] else -1), a[1])


def _accanto(s: Segmento, t: Segmento) -> float:
    """Per quanti millimetri il richiamo `s` corre parallelo alla linea `t`, a meno di
    `ACCANTO_MM`: un richiamo che costeggia un tubo si confonde con lui."""
    sx0, sy0, sx1, sy1, _ = s
    tx0, ty0, tx1, ty1, mezzo = t
    vicino = ACCANTO_MM + mezzo
    if abs(sy0 - sy1) < 1e-9 and abs(ty0 - ty1) < 1e-9 and abs(sy0 - ty0) < vicino:
        return max(0.0, min(max(sx0, sx1), max(tx0, tx1)) - max(min(sx0, sx1), min(tx0, tx1)))
    if abs(sx0 - sx1) < 1e-9 and abs(tx0 - tx1) < 1e-9 and abs(sx0 - tx0) < vicino:
        return max(0.0, min(max(sy0, sy1), max(ty0, ty1)) - max(min(sy0, sy1), min(ty0, ty1)))
    return 0.0


def _dentro_per(r: Rettangolo, q: Rettangolo) -> float:
    """Per quanti millimetri il richiamo (il suo riquadro `r`, sottile) sta dentro `q`."""
    larghezza = min(r[2], q[2]) - max(r[0], q[0])
    altezza = min(r[3], q[3]) - max(r[1], q[1])
    return max(0.0, max(larghezza, altezza))


def _costo(
    punti: tuple[Punto, ...], stato: _Stato, proprie: frozenset[Segmento], sotto: tuple[Rettangolo, ...] = (),
) -> float | None:
    """Quanto costa il richiamo, o None se non si puo': incrocia un altro richiamo, passa
    su una scritta fuori. Il primo pezzo si accorcia di `FINE_MM`:
    il pezzo o la linea da cui parte non contano; i pezzi `sotto` la linea nemmeno.

    Costano: la lunghezza, il gomito, ogni linea e ogni muro passati, il tratto che
    corre accanto a una linea o dentro un muro (`COSTO_ACCANTO` al millimetro) e sopra
    una linea (`COSTO_SOPRA`), e molto (`COSTO_OSTACOLO`) una scritta o un pezzo della
    pianta."""
    costo = _lunghezza(punti) + (COSTO_GOMITO if len(punti) == 3 else 0.0)
    ingombri = stato.ingombri
    fuori = set(stato.scritte_fuori)
    for indice, (a, b) in enumerate(zip(punti, punti[1:], strict=False)):
        intero: Segmento = (a[0], a[1], b[0], b[1], SPESSORE_MM / 2)
        if any(_incrociano(intero, r) for r in stato.richiami):
            return None
        if any(_sovrapposti(_riquadro_del_segmento(intero), r) for r in stato.scritte_fuori):
            return None
        # Il primo pezzo, accorciato: l'oggetto da cui parte non conta.
        inizio = _accorcia(a, b, FINE_MM) if indice == 0 else a
        corto: Segmento = (inizio[0], inizio[1], b[0], b[1], SPESSORE_MM / 2)
        riquadro = _riquadro_del_segmento(corto)
        largo = (riquadro[0] - ACCANTO_MM, riquadro[1] - ACCANTO_MM, riquadro[2] + ACCANTO_MM, riquadro[3] + ACCANTO_MM)
        for tipo, numero in sorted(ingombri._vicini(largo)):
            if tipo == "t":
                scritta = ingombri.scritte[numero]
                if scritta not in fuori and _sovrapposti(riquadro, scritta):
                    costo += COSTO_OSTACOLO
            elif tipo == "r":
                rettangolo = ingombri.rettangoli[numero]
                if rettangolo in sotto:
                    continue
                if numero in ingombri.muri:
                    # Passato di traverso, un muro costa poco; costeggiato (dentro, o a meno
                    # di `ACCANTO_MM`), il richiamo si confonde col muro.
                    spessore = min(rettangolo[2] - rettangolo[0], rettangolo[3] - rettangolo[1])
                    intorno = (rettangolo[0] - ACCANTO_MM, rettangolo[1] - ACCANTO_MM,
                               rettangolo[2] + ACCANTO_MM, rettangolo[3] + ACCANTO_MM)
                    if _sovrapposti(riquadro, intorno):
                        lungo = _dentro_per(riquadro, intorno) - spessore - 2 * ACCANTO_MM - 0.5
                        costo += COSTO_ACCANTO * max(0.0, lungo)
                    if _sovrapposti(riquadro, rettangolo):
                        dentro = _dentro_per(riquadro, rettangolo) - spessore - 0.5
                        costo += COSTO_MURO + COSTO_SOPRA * max(0.0, dentro)
                elif _sovrapposti(riquadro, rettangolo):
                    costo += COSTO_OSTACOLO
            else:
                linea = ingombri.segmenti[numero]
                if linea in stato.richiami:
                    continue
                costo += COSTO_SOPRA * _sopra(corto, linea) + COSTO_ACCANTO * _accanto(corto, linea)
                if _segmento_tocca(linea, riquadro):
                    costo += COSTO_LINEA if (linea in stato.tubi or linea in proprie) else COSTO_TRATTINO
    return costo


def _punto_buono(
    p: Punto, stato: _Stato, proprie: frozenset[Segmento], proprio: Rettangolo | None,
    sotto: tuple[Rettangolo, ...] = (),
) -> bool:
    """Il punto d'attacco non sta su un incrocio con un'altra linea, ne' dentro un muro o
    un altro pezzo (salvo quelli sotto la linea)."""
    vicino = (p[0] - VICINO_MM, p[1] - VICINO_MM, p[0] + VICINO_MM, p[1] + VICINO_MM)
    ingombri = stato.ingombri
    for tipo, numero in ingombri._vicini(vicino):
        if tipo == "s":
            linea = ingombri.segmenti[numero]
            if linea not in proprie and _segmento_tocca(linea, vicino):
                return False
        elif tipo == "r":
            q = ingombri.rettangoli[numero]
            if (
                q != proprio and q not in sotto
                and q[0] + DENTRO_MM < p[0] < q[2] - DENTRO_MM and q[1] + DENTRO_MM < p[1] < q[3] - DENTRO_MM
            ):
                return False
    return True


Scelta = tuple[float, tuple[Punto, ...], _Posto]
"""(costo, richiamo, posto): dove va una scritta fuori."""

GIRI_DI_MIGLIORIA = 2
"""Quante volte si ripassano le scritte fuori, ciascuna con le altre ferme."""


LUNGO_MM = 120.0
"""Un richiamo fuori piu' lungo di cosi' attraversa mezza tavola: la tavola prova a
spostare la pianta sul foglio (`tavola.componi`), e tiene la prova se costa meno."""


@dataclass(frozen=True)
class Fuori:
    """Le scritte fuori, una per richiesta (None se non ha trovato posto), e quanto
    costano i loro richiami."""

    posate: list[ScrittaPosata | None]
    costi: list[float | None]

    @property
    def totale(self) -> float:
        return sum(10 * COSTO_OSTACOLO if c is None else c for c in self.costi)

    def da_migliorare(self) -> list[int]:
        """Le scritte senza posto, o col richiamo che passa su una scritta o un pezzo, o
        piu' lungo di `LUNGO_MM`."""
        return [
            indice for indice, (posata, costo) in enumerate(zip(self.posate, self.costi, strict=True))
            if posata is None or costo is None or costo >= COSTO_OSTACOLO
            or _lunghezza(posata.richiamo_fuori or ()) > LUNGO_MM
        ]


def posa_fuori(
    richieste: Sequence[Richiesta], ingombri: Ingombri, pianta: Rettangolo, area: Rettangolo,
    tubi: frozenset[Segmento], richiami: Sequence[Segmento], proprie: dict[str, frozenset[Segmento]],
) -> Fuori:
    """Le scritte fuori, una per richiesta, nell'ordine; None per quelle che non trovano
    posto. `pianta` e' l'ingombro del disegno sulla carta (muri, pezzi, zone esterne,
    tracciati), `area` il campo del disegno; `tubi` le linee dei tracciati, `richiami` i
    richiami corti gia' disegnati, `proprie` per scritta le linee del suo tracciato.

    Si posano una alla volta, ciascuna nel posto che costa meno con quelle gia' posate;
    poi si ripassano (`GIRI_DI_MIGLIORIA`): ognuna si toglie e si riposa con le altre
    ferme, e cambia posto solo se costa meno. La prima posata non prende il posto che
    serviva a un'altra solo perche' e' venuta prima. Se ne resta una da migliorare
    (`Fuori.da_migliorare`), tutto si rifa' nell'ordine inverso (prima le sigle dei pezzi,
    che stanno nei margini stretti, poi le scritte delle tratte), e si tiene il migliore.

    Le scritte e i richiami posati entrano negli `ingombri`: chi viene dopo (i nomi delle
    stanze) non ci va sopra."""
    vecchia_area = ingombri.area
    prova = ingombri.copia()
    prova.area = area
    ordini = [list(range(len(richieste)))]
    migliori: list[Scelta | None] | None = None
    while ordini:
        ordine = ordini.pop(0)
        scelte = _posa_e_migliora(richieste, ordine, prova, pianta, area, tubi, richiami, proprie)
        if migliori is None or _totale(scelte) < _totale(migliori) - 1e-6:
            migliori = scelte
        if len(ordine) > 1 and ordine[0] == 0 and Fuori(
            [None if c is None else _posata(r, c) for r, c in zip(richieste, scelte, strict=True)],
            [None if c is None else c[0] for c in scelte],
        ).da_migliorare():
            ordini.append(ordine[::-1])
    assert migliori is not None
    finale = _con_le_scelte(prova, migliori, tubi, richiami)
    finale.ingombri.area = vecchia_area
    ingombri.prendi(finale.ingombri)
    return Fuori(
        [None if scelta is None else _posata(richiesta, scelta) for richiesta, scelta in zip(richieste, migliori,
                                                                                             strict=True)],
        [None if scelta is None else scelta[0] for scelta in migliori],
    )


def _totale(scelte: Sequence[Scelta | None]) -> float:
    return sum(10 * COSTO_OSTACOLO if s is None else s[0] for s in scelte)


def _con_le_scelte(
    base: Ingombri, scelte: Sequence[Scelta | None], tubi: frozenset[Segmento], richiami: Sequence[Segmento],
    salvo: int | None = None,
) -> _Stato:
    """Gli ingombri di partenza con le scritte gia' scelte, salvo una."""
    stato = _Stato(base.copia(), tubi, list(richiami), [])
    for indice, scelta in enumerate(scelte):
        if scelta is not None and indice != salvo:
            _registra(stato, scelta)
    return stato


def _posa_e_migliora(
    richieste: Sequence[Richiesta], ordine: Sequence[int], base: Ingombri, pianta: Rettangolo, area: Rettangolo,
    tubi: frozenset[Segmento], richiami: Sequence[Segmento], proprie: dict[str, frozenset[Segmento]],
) -> list[Scelta | None]:
    scelte: list[Scelta | None] = [None] * len(richieste)
    stato = _Stato(base.copia(), tubi, list(richiami), [])
    for indice in ordine:
        richiesta = richieste[indice]
        scelte[indice] = _cerca(richiesta, stato, pianta, area, proprie.get(richiesta.chi, frozenset()))
        if scelte[indice] is not None:
            _registra(stato, scelte[indice])  # type: ignore[arg-type]
    for _ in range(GIRI_DI_MIGLIORIA if len(richieste) > 1 else 0):
        cambiato = False
        for indice in ordine:
            richiesta = richieste[indice]
            senza = _con_le_scelte(base, scelte, tubi, richiami, salvo=indice)
            nuova = _cerca(richiesta, senza, pianta, area, proprie.get(richiesta.chi, frozenset()))
            vecchia = scelte[indice]
            if nuova is not None and (vecchia is None or nuova[0] < vecchia[0] - 1e-6):
                scelte[indice] = nuova
                cambiato = True
        if not cambiato:
            break
    return scelte


def _cerca(
    richiesta: Richiesta, stato: _Stato, pianta: Rettangolo, area: Rettangolo, proprie: frozenset[Segmento],
) -> Scelta | None:
    """Il posto che costa meno per la scritta, con quelle gia' posate: i candidati in ordine
    di lunghezza, finche' la lunghezza da sola supera il costo del migliore."""
    tratti = _tratti(richiesta)
    liberi: dict[Rettangolo, bool] = {}
    buoni: dict[Punto, bool] = {}
    migliore: Scelta | None = None
    for minimo, _, punti, posto in _candidati(richiesta, tratti, pianta, area):
        if migliore is not None and minimo >= migliore[0]:
            break
        if posto.riquadro not in liberi:
            liberi[posto.riquadro] = stato.ingombri.libero(posto.riquadro)
        if not liberi[posto.riquadro]:
            continue
        if punti[0] not in buoni:
            buoni[punti[0]] = _punto_buono(punti[0], stato, proprie, richiesta.rettangolo, richiesta.sotto)
        if not buoni[punti[0]]:
            continue
        costo = _costo(punti, stato, proprie, richiesta.sotto)
        if costo is not None and (migliore is None or costo < migliore[0] - 1e-9):
            migliore = (costo, punti, posto)
    return migliore


def _registra(stato: _Stato, scelta: Scelta) -> None:
    _, punti, posto = scelta
    stato.ingombri.metti_scritta(posto.riquadro)
    stato.scritte_fuori.append(posto.riquadro)
    for a, b in zip(punti, punti[1:], strict=False):
        segmento: Segmento = (a[0], a[1], b[0], b[1], SPESSORE_MM / 2)
        stato.ingombri.metti_segmento(segmento)
        stato.richiami.append(segmento)


def _posata(richiesta: Richiesta, scelta: Scelta) -> ScrittaPosata:
    _, punti, posto = scelta
    return ScrittaPosata(richiesta.testo, posto.x, posto.y, richiesta.corpo_pt, richiesta.grassetto, posto.riquadro,
                         richiamo_fuori=punti)
