"""Dove si posano le scritte: mai sopra a una linea, mai sopra a un'altra scritta.

Tutto in millimetri di carta. Le linee sono segmenti con il loro mezzo
spessore; muri, pezzi e scritte gia' posate sono rettangoli. Una scritta si
prova in una serie di posti, nell'ordine in cui la si vorrebbe — accanto al
tratto piu' lungo del suo tracciato, poi accanto agli altri —, e prende il
primo libero. Se non ce n'e', si allontana con un richiamo **ortogonale** (la
regola dei diagonali vale anche per lui), prima uno che non attraversa niente
e poi uno che passa sopra altre linee, mai sopra altre scritte; se non c'e'
nemmeno quello, si posa nel posto migliore e il controllo la conta.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

from disegnatore_mep.graphics.cartiglio import larghezza_mm
from disegnatore_mep.graphics.standard import PT_MM

Rettangolo = tuple[float, float, float, float]
Segmento = tuple[float, float, float, float, float]
"""x0, y0, x1, y1 e il mezzo spessore."""

SALITA_EM = 0.75
"""Quanto una scritta sale sopra la linea di base, in corpi (le maiuscole e i
tratti ascendenti di Arial)."""

DISCESA_EM = 0.22
"""Quanto scende sotto: le code di g, p, q."""

ARIA_MM = 0.5
"""Il bianco che una scritta tiene intorno a se'."""

DISTACCO_MM = 0.8
"""La distanza fra una scritta e la linea a cui si riferisce."""

RICHIAMO_MASSIMO_MM = 60.0
"""Fin dove si allontana una scritta col suo richiamo."""

CELLA_MM = 10.0
"""Il lato delle celle dell'indice degli ingombri."""


@dataclass(frozen=True)
class ScrittaPosata:
    testo: str
    x: float
    """La x della linea di base, all'inizio del testo."""
    y: float
    corpo_pt: float
    grassetto: bool
    riquadro: Rettangolo
    richiamo: tuple[float, float, float, float] | None = None
    libera: bool = True
    """Falso se nessun posto era libero: il controllo la conta."""


def misura(testo: str, corpo_pt: float, grassetto: bool) -> tuple[float, float, float]:
    """Larghezza, salita e discesa di una scritta, in millimetri."""
    corpo = corpo_pt * PT_MM
    return larghezza_mm(testo, corpo_pt, grassetto), SALITA_EM * corpo, DISCESA_EM * corpo


def _sovrapposti(a: Rettangolo, b: Rettangolo) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _riquadro_del_segmento(s: Segmento) -> Rettangolo:
    x0, y0, x1, y1, mezzo = s
    return (min(x0, x1) - mezzo, min(y0, y1) - mezzo, max(x0, x1) + mezzo, max(y0, y1) + mezzo)


def _segmento_tocca(s: Segmento, r: Rettangolo) -> bool:
    x0, y0, x1, y1, mezzo = s
    if not _sovrapposti(_riquadro_del_segmento(s), r):
        return False
    if x0 == x1 or y0 == y1:
        return True
    # Un segmento obliquo (una corda dell'arco di una porta): si campiona.
    passi = 24
    for indice in range(passi + 1):
        t = indice / passi
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if r[0] - mezzo <= x <= r[2] + mezzo and r[1] - mezzo <= y <= r[3] + mezzo:
            return True
    return False


def _celle(r: Rettangolo) -> Iterator[tuple[int, int]]:
    for i in range(int(r[0] // CELLA_MM), int(r[2] // CELLA_MM) + 1):
        for j in range(int(r[1] // CELLA_MM), int(r[3] // CELLA_MM) + 1):
            yield i, j


@dataclass
class Ingombri:
    """Quello che una scritta non deve toccare, con un indice a celle."""

    area: Rettangolo | None = None
    """Dove le scritte possono stare: fuori, no."""
    segmenti: list[Segmento] = field(default_factory=list)
    rettangoli: list[Rettangolo] = field(default_factory=list)
    scritte: list[Rettangolo] = field(default_factory=list)
    _indice: dict[tuple[int, int], list[tuple[str, int]]] = field(default_factory=dict)

    def _indicizza(self, tipo: str, numero: int, r: Rettangolo) -> None:
        for cella in _celle(r):
            self._indice.setdefault(cella, []).append((tipo, numero))

    def metti_segmento(self, s: Segmento) -> None:
        self.segmenti.append(s)
        self._indicizza("s", len(self.segmenti) - 1, _riquadro_del_segmento(s))

    def metti_rettangolo(self, r: Rettangolo) -> None:
        self.rettangoli.append(r)
        self._indicizza("r", len(self.rettangoli) - 1, r)

    def metti_scritta(self, r: Rettangolo) -> None:
        self.scritte.append(r)
        self._indicizza("t", len(self.scritte) - 1, r)

    def _vicini(self, r: Rettangolo) -> set[tuple[str, int]]:
        out: set[tuple[str, int]] = set()
        for cella in _celle(r):
            out.update(self._indice.get(cella, ()))
        return out

    def dentro_l_area(self, r: Rettangolo) -> bool:
        return self.area is None or (
            self.area[0] <= r[0] and self.area[1] <= r[1] and r[2] <= self.area[2] and r[3] <= self.area[3]
        )

    def libero(self, r: Rettangolo) -> bool:
        if not self.dentro_l_area(r):
            return False
        for tipo, numero in self._vicini(r):
            if tipo == "t" and _sovrapposti(r, self.scritte[numero]):
                return False
            if tipo == "r" and _sovrapposti(r, self.rettangoli[numero]):
                return False
            if tipo == "s" and _segmento_tocca(self.segmenti[numero], r):
                return False
        return True

    def segmento_libero(
        self, s: Segmento, salvo: Iterable[Segmento] = (), solo_scritte: bool = False,
        muri: bool = False, proprio: Rettangolo | None = None,
    ) -> bool:
        """Un richiamo non attraversa mai una scritta. Con `muri` non attraversa
        nemmeno muri e pezzi — un richiamo che passa un muro indica la stanza
        sbagliata —; senza `solo_scritte` nemmeno le linee."""
        esclusi = set(salvo)
        riquadro = _riquadro_del_segmento(s)
        for tipo, numero in self._vicini(riquadro):
            if tipo == "t" and _sovrapposti(riquadro, self.scritte[numero]):
                return False
            if (
                tipo == "r" and muri and self.rettangoli[numero] != proprio
                and _sovrapposti(riquadro, self.rettangoli[numero])
            ):
                return False
            if (
                tipo == "s" and not solo_scritte and self.segmenti[numero] not in esclusi
                and _segmento_tocca(self.segmenti[numero], riquadro)
            ):
                return False
        return True


def _riquadro(x: float, y: float, larghezza: float, salita: float, discesa: float) -> Rettangolo:
    return (x - ARIA_MM, y - salita - ARIA_MM, x + larghezza + ARIA_MM, y + discesa + ARIA_MM)


def posti_lungo_i_segmenti(
    punti: list[tuple[float, float]], larghezza: float, salita: float, discesa: float, scarto: float,
) -> Iterator[tuple[float, float]]:
    """Le linee di base candidate accanto a una spezzata: sopra e sotto i tratti
    orizzontali, a destra e a sinistra di quelli verticali, dal tratto piu'
    lungo al piu' corto e dal mezzo verso i capi."""
    tratti = sorted(
        ((abs(b[0] - a[0]) + abs(b[1] - a[1]), indice, a, b)
         for indice, (a, b) in enumerate(zip(punti, punti[1:], strict=False))),
        key=lambda t: (-t[0], t[1]),
    )
    for lunghezza, _, a, b in tratti:
        if lunghezza < 1e-6:
            continue
        orizzontale = abs(a[1] - b[1]) < 1e-9
        passi = max(1, int(lunghezza / 1.5))
        posizioni = sorted(
            (indice / passi for indice in range(passi + 1)), key=lambda t: (abs(t - 0.5), t)
        )
        for t in posizioni:
            cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            if orizzontale:
                yield cx - larghezza / 2, cy - scarto - discesa - ARIA_MM
                yield cx - larghezza / 2, cy + scarto + salita + ARIA_MM
            else:
                base = cy + (salita - discesa) / 2
                yield cx + scarto + ARIA_MM, base
                yield cx - scarto - ARIA_MM - larghezza, base


Origine = tuple[float, float, int, int]
"""Da dove parte un richiamo: il punto e la direzione (una delle quattro)."""


def _con_richiamo(
    testo: str, corpo_pt: float, grassetto: bool, origini: list[Origine], ingombri: Ingombri,
    salvo: list[Segmento], minimo: float, proprio: Rettangolo | None = None,
) -> ScrittaPosata | None:
    """La scritta in fondo a un richiamo dritto, dal punto piu' vicino che
    trova; prima senza attraversare linee, poi attraversandole."""
    larghezza, salita, discesa = misura(testo, corpo_pt, grassetto)
    distanze = [minimo + d * 1.5 for d in range(int((RICHIAMO_MASSIMO_MM - minimo) / 1.5) + 1)]
    for attraversa, muri in ((False, True), (True, True), (True, False)):
        for distanza in distanze:
            for px, py, dx, dy in origini:
                ex, ey = px + dx * distanza, py + dy * distanza
                if dy:
                    y = ey - discesa - ARIA_MM if dy < 0 else ey + salita + ARIA_MM
                    posti = [(ex - larghezza / 2, y), (ex - ARIA_MM, y), (ex - larghezza + ARIA_MM, y)]
                else:
                    x = ex + ARIA_MM if dx > 0 else ex - ARIA_MM - larghezza
                    posti = [(x, ey + (salita - discesa) / 2)]
                for x, y in posti:
                    r = _riquadro(x, y, larghezza, salita, discesa)
                    if not ingombri.libero(r):
                        continue
                    richiamo = (round(px, 3), round(py, 3), round(ex, 3), round(ey, 3))
                    segmento = (*richiamo, 0.1)
                    if ingombri.segmento_libero(
                        segmento, salvo=salvo, solo_scritte=attraversa, muri=muri, proprio=proprio
                    ):
                        ingombri.metti_segmento(segmento)
                        return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri, richiamo)
    return None


def posa_accanto(
    testo: str, corpo_pt: float, grassetto: bool, punti: list[tuple[float, float]],
    proprie: list[Segmento], ingombri: Ingombri, mezzo_spessore: float,
) -> ScrittaPosata:
    """La scritta di un tracciato, accanto alla sua spezzata."""
    larghezza, salita, discesa = misura(testo, corpo_pt, grassetto)
    primo: tuple[float, float] | None = None
    for x, y in posti_lungo_i_segmenti(punti, larghezza, salita, discesa, mezzo_spessore + DISTACCO_MM):
        r = _riquadro(x, y, larghezza, salita, discesa)
        if primo is None and ingombri.dentro_l_area(r):
            primo = (x, y)
        if ingombri.libero(r):
            return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri)
    origini: list[Origine] = []
    for a, b in sorted(
        zip(punti, punti[1:], strict=False),
        key=lambda ab: -(abs(ab[1][0] - ab[0][0]) + abs(ab[1][1] - ab[0][1])),
    ):
        lunghezza = abs(b[0] - a[0]) + abs(b[1] - a[1])
        orizzontale = abs(a[1] - b[1]) < 1e-9
        passi = max(1, int(lunghezza / 2.0))
        for t in sorted((i / passi for i in range(passi + 1)), key=lambda t: (abs(t - 0.5), t)):
            cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for verso in (-1, 1):
                origini.append((cx, cy, 0, verso) if orizzontale else (cx, cy, verso, 0))
    posata = _con_richiamo(testo, corpo_pt, grassetto, origini, ingombri, proprie, 3.0)
    if posata is not None:
        return posata
    x, y = primo if primo is not None else punti[0]
    r = _riquadro(x, y, larghezza, salita, discesa)
    ingombri.metti_scritta(r)
    return ScrittaPosata(testo, x, y, corpo_pt, grassetto, r, libera=False)


def posa_intorno(
    testo: str, corpo_pt: float, grassetto: bool, rettangolo: Rettangolo, ingombri: Ingombri,
) -> ScrittaPosata:
    """La sigla di un pezzo, o il numero di una foratura: accanto al suo
    rettangolo, poi via via piu' lontano, con un richiamo se serve."""
    larghezza, salita, discesa = misura(testo, corpo_pt, grassetto)
    x0, y0, x1, y1 = rettangolo
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    base_mezzo = cy + (salita - discesa) / 2
    primo: tuple[float, float] | None = None
    for distanza in (0.6, 1.2, 1.8):
        for x, y in (
            (x1 + distanza + ARIA_MM, base_mezzo),
            (x0 - distanza - ARIA_MM - larghezza, base_mezzo),
            (cx - larghezza / 2, y0 - distanza - discesa - ARIA_MM),
            (cx - larghezza / 2, y1 + distanza + salita + ARIA_MM),
        ):
            r = _riquadro(x, y, larghezza, salita, discesa)
            if primo is None and ingombri.dentro_l_area(r):
                primo = (x, y)
            if ingombri.libero(r):
                return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri)
    origini: list[Origine] = []
    for t in (0.5, 0.25, 0.75):
        origini += [
            (x1, y0 + (y1 - y0) * t, 1, 0), (x0, y0 + (y1 - y0) * t, -1, 0),
            (x0 + (x1 - x0) * t, y0, 0, -1), (x0 + (x1 - x0) * t, y1, 0, 1),
        ]
    posata = _con_richiamo(testo, corpo_pt, grassetto, origini, ingombri, [], 2.5, rettangolo)
    if posata is not None:
        return posata
    x, y = primo if primo is not None else (x1 + ARIA_MM, base_mezzo)
    r = _riquadro(x, y, larghezza, salita, discesa)
    ingombri.metti_scritta(r)
    return ScrittaPosata(testo, x, y, corpo_pt, grassetto, r, libera=False)


def posa_dentro(
    testo: str, corpo_pt: float, grassetto: bool, candidati: Iterable[tuple[float, float]],
    ingombri: Ingombri,
) -> ScrittaPosata | None:
    """Il nome di una stanza: nel primo dei punti candidati (centri della
    scritta) dove sta libero. Se non c'e', niente: meglio una stanza senza nome
    che un nome sopra un tracciato."""
    larghezza, salita, discesa = misura(testo, corpo_pt, grassetto)
    for cx, cy in candidati:
        x, y = cx - larghezza / 2, cy + (salita - discesa) / 2
        r = _riquadro(x, y, larghezza, salita, discesa)
        if ingombri.libero(r):
            return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri)
    return None


def _posata(
    testo: str, x: float, y: float, corpo_pt: float, grassetto: bool, r: Rettangolo,
    ingombri: Ingombri, richiamo: tuple[float, float, float, float] | None = None,
) -> ScrittaPosata:
    ingombri.metti_scritta(r)
    return ScrittaPosata(testo, round(x, 3), round(y, 3), corpo_pt, grassetto, r, richiamo)
