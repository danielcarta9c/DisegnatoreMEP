"""Dove si posano le scritte: mai sopra a una linea, mai sopra a un'altra scritta.

Tutto in millimetri di carta. Le linee sono segmenti con il loro mezzo
spessore; muri, pezzi e scritte gia' posate sono rettangoli. Una scritta si
prova in una serie di posti, nell'ordine in cui la si vorrebbe — accanto al
tratto piu' lungo del suo tracciato, poi accanto agli altri —, e prende il
primo libero.

Se non ce n'e', si allontana con un **richiamo**, e il richiamo ha le sue
regole, misurate anche sulla tavola finita (`controlli.py`):

- e' **ortogonale** (la regola dei diagonali vale anche per lui);
- e' **corto**: al piu' `RICHIAMO_MASSIMO_MM` di carta;
- **non attraversa** muri, pezzi (salvo il suo), scritte; e al piu' **una**
  linea, se non c'e' altro modo, e allora si conta. Un muro attraversato
  indica la stanza sbagliata, un pezzo attraversato il pezzo sbagliato.

Se nemmeno il richiamo corto trova posto, la scritta va **in legenda**: accanto
alla linea (o al pezzo) un numero cerchiato, e il testo nella colonna, sotto
lo stesso numero. Un richiamo lungo che attraversa mezza stanza non si legge
(collaudo REL-012, t1): un numero si'.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field

from disegnatore_mep.graphics.cartiglio import larghezza_mm
from disegnatore_mep.graphics.standard import CORPO_MINIMO_PT, PT_MM

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

RICHIAMO_MASSIMO_MM = 12.0
"""Fin dove si allontana una scritta col suo richiamo: 12 mm di carta, 60 cm
a 1:50. Oltre, la scritta va in legenda con un numero. Era 60 mm, e nel
collaudo t1 un richiamo correva per 3 m lungo un muro."""

LINEE_PER_RICHIAMO = 1
"""Quante linee un richiamo puo' attraversare, se non c'e' altro modo: una, e
si conta."""

RAGGIO_DEL_NUMERO_MM = 1.6
"""Il cerchio del numero di una scritta in legenda."""

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
    numero: int | None = None
    """Una scritta in legenda: sulla tavola c'e' il numero cerchiato (`testo` e'
    il numero, `x` il bordo sinistro del cerchio), il testo intero sta nella
    colonna (`in_legenda`)."""
    in_legenda: str | None = None


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
    legenda: list[str] = field(default_factory=list)
    """I testi andati in legenda, nell'ordine dei numeri."""
    muri: set[int] = field(default_factory=set)
    """Quali rettangoli sono muri: un richiamo ne puo' uscire di traverso."""
    ammessi: tuple[Rettangolo, ...] = ()
    """Durante la posa di una scritta, i rettangoli su cui puo' stare: il muro
    di una foratura, su cui il suo numero si scrive."""
    _indice: dict[tuple[int, int], list[tuple[str, int]]] = field(default_factory=dict)

    def _indicizza(self, tipo: str, numero: int, r: Rettangolo) -> None:
        for cella in _celle(r):
            self._indice.setdefault(cella, []).append((tipo, numero))

    def metti_segmento(self, s: Segmento) -> None:
        self.segmenti.append(s)
        self._indicizza("s", len(self.segmenti) - 1, _riquadro_del_segmento(s))

    def metti_rettangolo(self, r: Rettangolo, muro: bool = False) -> None:
        self.rettangoli.append(r)
        if muro:
            self.muri.add(len(self.rettangoli) - 1)
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

    def libero(self, r: Rettangolo, proprio: Rettangolo | None = None) -> bool:
        """Libero da scritte, rettangoli e linee; `proprio` e' il rettangolo del
        pezzo dentro cui la scritta sta, e non conta."""
        if not self.dentro_l_area(r):
            return False
        for tipo, numero in self._vicini(r):
            if tipo == "t" and _sovrapposti(r, self.scritte[numero]):
                return False
            if (
                tipo == "r" and self.rettangoli[numero] != proprio and self.rettangoli[numero] not in self.ammessi
                and _sovrapposti(r, self.rettangoli[numero])
            ):
                return False
            if tipo == "s" and _segmento_tocca(self.segmenti[numero], r):
                return False
        return True

    def attraversamenti(
        self, s: Segmento, salvo: Iterable[Segmento] = (), proprio: Rettangolo | None = None,
    ) -> int | None:
        """Quante linee il richiamo attraversa; None se attraversa una scritta,
        un muro o un pezzo che non e' il suo. Il richiamo di un oggetto che sta
        dentro un muro (una bocchetta a parete, una foratura) ne esce di
        traverso: quel muro non conta."""
        esclusi = set(salvo)
        riquadro = _riquadro_del_segmento(s)
        linee = 0
        for tipo, numero in sorted(self._vicini(riquadro)):
            if tipo == "t" and _sovrapposti(riquadro, self.scritte[numero]):
                return None
            if tipo == "r":
                rettangolo = self.rettangoli[numero]
                if rettangolo == proprio or rettangolo in self.ammessi or not _sovrapposti(riquadro, rettangolo):
                    continue
                if numero in self.muri and esce_di_traverso(s, rettangolo):
                    continue
                return None
            if tipo == "s" and self.segmenti[numero] not in esclusi and _segmento_tocca(
                self.segmenti[numero], riquadro
            ):
                linee += 1
        return linee


def esce_di_traverso(s: Segmento | tuple[float, float, float, float], r: Rettangolo) -> bool:
    """Il segmento parte dentro il rettangolo e ne esce per il lato lungo: e'
    il richiamo di un oggetto che sta nel muro, non un richiamo che lo passa."""
    x0, y0, x1, y1 = s[:4]
    if not (r[0] - 1e-6 <= x0 <= r[2] + 1e-6 and r[1] - 1e-6 <= y0 <= r[3] + 1e-6):
        return False
    larghezza, altezza = r[2] - r[0], r[3] - r[1]
    if abs(y0 - y1) < 1e-9:  # orizzontale: esce da un muro verticale, stretto in x
        return larghezza < altezza
    return altezza < larghezza


def _riquadro(x: float, y: float, larghezza: float, salita: float, discesa: float) -> Rettangolo:
    return (x - ARIA_MM, y - salita - ARIA_MM, x + larghezza + ARIA_MM, y + discesa + ARIA_MM)


def posti_lungo_i_segmenti(
    segmenti: Sequence[tuple[tuple[float, float], tuple[float, float]]], larghezza: float, salita: float,
    discesa: float, scarto: float,
) -> Iterator[tuple[float, float]]:
    """Le linee di base candidate accanto ai tratti di una spezzata: sopra e
    sotto i tratti orizzontali, a destra e a sinistra di quelli verticali, dal
    tratto piu' lungo al piu' corto e dal mezzo verso i capi."""
    tratti = sorted(
        ((abs(b[0] - a[0]) + abs(b[1] - a[1]), indice, a, b) for indice, (a, b) in enumerate(segmenti)),
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
    misure: tuple[float, float, float] | None = None,
) -> tuple[float, float, Rettangolo, tuple[float, float, float, float]] | None:
    """La scritta in fondo a un richiamo dritto e corto, dal punto piu' vicino
    che trova: prima senza attraversare linee, poi attraversandone una."""
    larghezza, salita, discesa = misure or misura(testo, corpo_pt, grassetto)
    distanze = [minimo + d * 1.0 for d in range(int(RICHIAMO_MASSIMO_MM - minimo) + 1)]
    for ammesse in range(LINEE_PER_RICHIAMO + 1):
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
                    linee = ingombri.attraversamenti(segmento, salvo=salvo, proprio=proprio)
                    if linee is not None and linee <= ammesse:
                        ingombri.metti_segmento(segmento)
                        return x, y, r, richiamo
    return None


def _in_legenda(
    testo: str, corpo_pt: float, posti: Iterable[tuple[float, float]], origini: list[Origine],
    ingombri: Ingombri, salvo: list[Segmento], proprio: Rettangolo | None,
) -> ScrittaPosata | None:
    """Il numero cerchiato al posto della scritta: accanto, o con un richiamo
    corto. Il testo va nella colonna, sotto lo stesso numero."""
    numero = len(ingombri.legenda) + 1
    lato = 2 * RAGGIO_DEL_NUMERO_MM
    misure = (lato, RAGGIO_DEL_NUMERO_MM, RAGGIO_DEL_NUMERO_MM)
    for x, y in posti:
        r = _riquadro(x, y, *misure)
        if ingombri.libero(r):
            ingombri.metti_scritta(r)
            ingombri.legenda.append(testo)
            return ScrittaPosata(str(numero), round(x, 3), round(y, 3), corpo_pt, True, r,
                                 numero=numero, in_legenda=testo)
    trovato = _con_richiamo(str(numero), corpo_pt, True, origini, ingombri, salvo, 2.0, proprio, misure)
    if trovato is None:
        return None
    x, y, r, richiamo = trovato
    ingombri.metti_scritta(r)
    ingombri.legenda.append(testo)
    return ScrittaPosata(str(numero), round(x, 3), round(y, 3), corpo_pt, True, r, richiamo,
                         numero=numero, in_legenda=testo)


def posa_accanto(
    testo: str, corpo_pt: float, grassetto: bool, linee: Sequence[Sequence[tuple[float, float]]],
    proprie: list[Segmento], ingombri: Ingombri, mezzo_spessore: float,
) -> ScrittaPosata:
    """La scritta di un tracciato, accanto alle sue spezzate (una, o i tronchi
    di una tratta con organi in linea)."""
    larghezza, salita, discesa = misura(testo, corpo_pt, grassetto)
    tratti = [(a, b) for punti in linee for a, b in zip(punti, punti[1:], strict=False)]
    primo: tuple[float, float] | None = None
    for x, y in posti_lungo_i_segmenti(tratti, larghezza, salita, discesa, mezzo_spessore + DISTACCO_MM):
        r = _riquadro(x, y, larghezza, salita, discesa)
        if primo is None and ingombri.dentro_l_area(r):
            primo = (x, y)
        if ingombri.libero(r):
            return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri)
    origini: list[Origine] = []
    for a, b in sorted(tratti, key=lambda ab: -(abs(ab[1][0] - ab[0][0]) + abs(ab[1][1] - ab[0][1]))):
        lunghezza = abs(b[0] - a[0]) + abs(b[1] - a[1])
        orizzontale = abs(a[1] - b[1]) < 1e-9
        passi = max(1, int(lunghezza / 2.0))
        for t in sorted((i / passi for i in range(passi + 1)), key=lambda t: (abs(t - 0.5), t)):
            cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for verso in (-1, 1):
                origini.append((cx, cy, 0, verso) if orizzontale else (cx, cy, verso, 0))
    trovato = _con_richiamo(testo, corpo_pt, grassetto, origini, ingombri, proprie, 3.0)
    if trovato is not None:
        x, y, r, richiamo = trovato
        return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri, richiamo)
    lato = 2 * RAGGIO_DEL_NUMERO_MM
    numero = _in_legenda(
        testo, corpo_pt,
        posti_lungo_i_segmenti(tratti, lato, RAGGIO_DEL_NUMERO_MM, RAGGIO_DEL_NUMERO_MM,
                               mezzo_spessore + DISTACCO_MM),
        origini, ingombri, proprie, None,
    )
    if numero is not None:
        return numero
    x, y = primo if primo is not None else tratti[0][0]
    r = _riquadro(x, y, larghezza, salita, discesa)
    ingombri.metti_scritta(r)
    return ScrittaPosata(testo, x, y, corpo_pt, grassetto, r, libera=False)


def _dentro_al_pezzo(
    testo: str, corpo_pt: float, grassetto: bool, misure: tuple[float, float, float],
    rettangolo: Rettangolo, ingombri: Ingombri,
) -> tuple[float, float, Rettangolo] | None:
    """La scritta al centro del pezzo, se ci sta tutta con il suo bianco: per un
    pezzo stretto fra linee e muri e' il posto piu' chiaro che c'e'."""
    larghezza, salita, discesa = misure
    x0, y0, x1, y1 = rettangolo
    x = (x0 + x1) / 2 - larghezza / 2
    y = (y0 + y1) / 2 + (salita - discesa) / 2
    r = _riquadro(x, y, larghezza, salita, discesa)
    if r[0] < x0 or r[2] > x1 or r[1] < y0 or r[3] > y1:
        return None
    if not ingombri.libero(r, proprio=rettangolo):
        return None
    return x, y, r


def posa_nel_pezzo(
    testo: str, corpo_pt: float, grassetto: bool, rettangolo: Rettangolo, ingombri: Ingombri,
) -> ScrittaPosata | None:
    """La sigla dentro il suo pezzo, al corpo delle sigle o al minimo, se ci
    sta: un'unita' grande porta il nome dentro, e il posto fuori resta alle
    scritte delle linee."""
    for corpo in sorted({corpo_pt, min(corpo_pt, CORPO_MINIMO_PT)}, reverse=True):
        trovato = _dentro_al_pezzo(testo, corpo, grassetto, misura(testo, corpo, grassetto), rettangolo, ingombri)
        if trovato is not None:
            x, y, r = trovato
            return _posata(testo, x, y, corpo, grassetto, r, ingombri)
    return None


def posa_intorno(
    testo: str, corpo_pt: float, grassetto: bool, rettangolo: Rettangolo, ingombri: Ingombri,
    dentro: bool = False, sopra: Sequence[Rettangolo] = (),
) -> ScrittaPosata:
    """Come `_posa_intorno`; `sopra` sono i rettangoli su cui la scritta puo'
    stare (il muro della foratura che numera)."""
    ingombri.ammessi = tuple(sopra)
    try:
        return _posa_intorno(testo, corpo_pt, grassetto, rettangolo, ingombri, dentro)
    finally:
        ingombri.ammessi = ()


def _posa_intorno(
    testo: str, corpo_pt: float, grassetto: bool, rettangolo: Rettangolo, ingombri: Ingombri,
    dentro: bool = False,
) -> ScrittaPosata:
    """La sigla di un pezzo, o il numero di una foratura: accanto al suo
    rettangolo, poi (`dentro`, per i pezzi) al centro del pezzo se ci sta, poi
    con un richiamo corto, poi in legenda."""
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
    if dentro:
        # Dentro il pezzo, al corpo delle sigle o, se non ci sta, al minimo.
        for corpo in sorted({corpo_pt, min(corpo_pt, CORPO_MINIMO_PT)}, reverse=True):
            trovato_dentro = _dentro_al_pezzo(testo, corpo, grassetto, misura(testo, corpo, grassetto),
                                              rettangolo, ingombri)
            if trovato_dentro is not None:
                x, y, r = trovato_dentro
                return _posata(testo, x, y, corpo, grassetto, r, ingombri)
    origini: list[Origine] = []
    for t in (0.5, 0.25, 0.75):
        origini += [
            (x1, y0 + (y1 - y0) * t, 1, 0), (x0, y0 + (y1 - y0) * t, -1, 0),
            (x0 + (x1 - x0) * t, y0, 0, -1), (x0 + (x1 - x0) * t, y1, 0, 1),
        ]
    trovato = _con_richiamo(testo, corpo_pt, grassetto, origini, ingombri, [], 2.5, rettangolo)
    if trovato is not None:
        x, y, r, richiamo = trovato
        return _posata(testo, x, y, corpo_pt, grassetto, r, ingombri, richiamo)
    lato, raggio = 2 * RAGGIO_DEL_NUMERO_MM, RAGGIO_DEL_NUMERO_MM
    posti: list[tuple[float, float]] = []
    for distanza in (0.6, 1.2):
        posti += [
            (x1 + distanza + ARIA_MM, cy), (x0 - distanza - ARIA_MM - lato, cy),
            (cx - raggio, y0 - distanza - raggio - ARIA_MM), (cx - raggio, y1 + distanza + raggio + ARIA_MM),
        ]
    numero = _in_legenda(testo, corpo_pt, posti, origini, ingombri, [], rettangolo)
    if numero is not None:
        return numero
    if dentro:
        lato = 2 * RAGGIO_DEL_NUMERO_MM
        trovato_dentro = _dentro_al_pezzo(str(len(ingombri.legenda) + 1), corpo_pt, True,
                                          (lato, RAGGIO_DEL_NUMERO_MM, RAGGIO_DEL_NUMERO_MM), rettangolo, ingombri)
        if trovato_dentro is not None:
            x, y, r = trovato_dentro
            ingombri.metti_scritta(r)
            ingombri.legenda.append(testo)
            numero_scritto = len(ingombri.legenda)
            return ScrittaPosata(str(numero_scritto), round(x, 3), round(y, 3), corpo_pt, True, r,
                                 numero=numero_scritto, in_legenda=testo)
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
