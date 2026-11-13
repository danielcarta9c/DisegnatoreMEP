"""La base architettonica della tavola MEP: una sola, qualunque fosse l'ingresso (REL-026, C-3).

Il progettista riceve planimetrie diversissime — il vettoriale dell'architetto pieno di
arredi, il catastale, il disegno a mano quotato, la foto di un catastale stampato. Leggerle
e' un lavoro da agente (`skill/base/ISTRUZIONI.md`); quello che esce e' **la base in dati**,
nel JSON della pianta: muri, aperture, stanze, balconi. Da qui in poi tutto e'
deterministico, e la grafica e' una sola, come si fa con gli xref architettonici in una
tavola impiantistica: **l'architettonico e' contesto, in mezzatinta; il contenuto e'
l'impianto**. Il PO, il 13 novembre 2026 (I-300): «colore appena sbiadito della planimetria
come si fa con gli xref architettonici in ambito mep, muri grigiolini, finestre celestine,
rimuovere arredi e lasciare solo i nomi delle stanze con i loro mq».

- **i muri** in grigio chiaro pieno, con un contorno sottile appena piu' scuro. Dai
  `muri` asse-spessore il motore ricava le sagome: ogni capo che arriva su un altro muro si
  allunga fino alla sua faccia lontana — l'angolo si chiude, niente rettangoli che sporgono —,
  un capo libero (una spalletta) finisce dov'e'; i muri dritti si uniscono in un contorno
  solo, senza le linee dei rettangoli sovrapposti. Le `sagome_muri`, se ci sono, prendono il
  posto dei muri nel disegno, come in B-2;
- **le finestre** celesti: il vano campito di celeste chiaro, il telaio e il vetro a tratto
  fine;
- **le porte** a tratto fine grigio, con l'anta e l'arco (o due ante, o la scorrevole);
- **i balconi** col contorno, **le stanze e i balconi** col nome e i mq — che il motore
  calcola dal poligono —, in grigio.

I colori sono costanti con un nome, qui e in nessun altro posto: sono **proposte**, che il
PO giudica sulla tavola.
"""

from __future__ import annotations

import math
from bisect import bisect_left
from collections.abc import Callable, Sequence

from .modello import Apertura, Muro, Pianta
from .tavola import (
    LAYER_APERTURE,
    LAYER_BALCONI,
    LAYER_FINESTRE,
    LAYER_MURI,
    Arco,
    Area,
    Linea,
    Primitiva,
)

Punto = tuple[float, float]
Anello = list[Punto]
Segmento = tuple[float, float, float, float, float]

# --- i colori della base: proposte, da giudicare sulla tavola ------------------------

GRIGIO_DEI_MURI = "#dcdcdc"
"""Il pieno dei muri: un grigio chiaro, sotto qualunque linea dell'impianto."""
CONTORNO_DEI_MURI = "#a8a8a8"
"""Il contorno dei muri: appena piu' scuro del pieno, perche' il muro si legga sul bianco."""
CELESTE_DELLE_FINESTRE = "#d6ecfa"
"""Il vano della finestra."""
LINEA_DELLE_FINESTRE = "#74b3e0"
"""Telaio e vetro della finestra."""
LINEA_DELLE_PORTE = "#a0a0a0"
"""Anta, arco e foro."""
LINEA_DEI_BALCONI = "#a8a8a8"
"""Il contorno dei balconi e dei terrazzi."""
GRIGIO_DEI_LOCALI = "#8a8a8a"
"""Il nome dei locali con i mq."""

TRATTO_FINE_MM = 0.13
"""Lo spessore delle linee della base: il piu' fine della tavola, sotto quelli dei
tracciati (0,30 – 0,70 mm)."""
TRATTO_DEI_FORI = "1 0.6"

SPESSORE_DELL_ANTA_SCORREVOLE_M = 0.03
"""L'anta scorrevole si disegna come un listello sottile lungo il muro."""

TOLLERANZA_DEL_RACCORDO_M = 0.05
"""Un capo di muro a meno di 5 cm da un altro muro si raccorda con lui: chi trascrive una
planimetria a mano o da una scansione non mette i capi al millimetro."""


# --- la geometria dei muri ---------------------------------------------------------------


def _asse(muro: Muro) -> tuple[float, float, float]:
    lunghezza = math.dist(muro.da, muro.a)
    return (muro.a[0] - muro.da[0]) / lunghezza, (muro.a[1] - muro.da[1]) / lunghezza, lunghezza


def _sull_asse(muro: Muro, s: float, d: float) -> Punto:
    ux, uy, _ = _asse(muro)
    return (muro.da[0] + ux * s - uy * d, muro.da[1] + uy * s + ux * d)


def _fino_alla_faccia(capo: Punto, verso: Punto, altro: Muro) -> float | None:
    """Di quanto un muro che finisce in `capo`, andando verso `verso`, si allunga per
    arrivare alla faccia lontana di `altro`; `None` se il capo non arriva su `altro`."""
    ux, uy, lunghezza = _asse(altro)
    nx, ny = -uy, ux
    h = altro.spessore / 2
    rx, ry = capo[0] - altro.da[0], capo[1] - altro.da[1]
    s, d = rx * ux + ry * uy, rx * nx + ry * ny
    t = TOLLERANZA_DEL_RACCORDO_M
    if not (-h - t <= s <= lunghezza + h + t) or abs(d) > h + t:
        return None
    coseno = verso[0] * nx + verso[1] * ny
    if abs(coseno) < 0.2:
        return None  # muri in fila: si toccano di testa, non si raccordano
    return max(0.0, (math.copysign(h, coseno) - d) / coseno)


def allungamenti(pianta: Pianta) -> dict[str, tuple[float, float]]:
    """Per muro, di quanto il disegno va oltre il capo `da` e il capo `a`: fino alla faccia
    lontana del muro su cui il capo arriva — l'angolo e la T si chiudono, con spessori anche
    diversi, e niente sporge —; zero per un capo libero."""
    out: dict[str, tuple[float, float]] = {}
    for muro in pianta.muri:
        ux, uy, _ = _asse(muro)
        coppia: list[float] = []
        for capo, verso in ((muro.da, (-ux, -uy)), (muro.a, (ux, uy))):
            fino = [
                v for altro in pianta.muri if altro is not muro
                if (v := _fino_alla_faccia(capo, verso, altro)) is not None
            ]
            coppia.append(max(fino, default=0.0))
        out[muro.id] = (coppia[0], coppia[1])
    return out


def tratti_pieni(pianta: Pianta) -> list[tuple[Muro, float, float]]:
    """I tratti pieni di ogni muro da disegnare: l'asse da s0 a s1 con i raccordi, le
    aperture tolte."""
    oltre = allungamenti(pianta)
    out: list[tuple[Muro, float, float]] = []
    for muro in pianta.muri:
        ux, uy, lunghezza = _asse(muro)
        prima, dopo = oltre[muro.id]
        tratti = [(-prima, lunghezza + dopo)]
        for apertura in sorted((a for a in pianta.aperture if a.muro == muro.id), key=lambda a: a.id):
            centro = (apertura.centro[0] - muro.da[0]) * ux + (apertura.centro[1] - muro.da[1]) * uy
            t0, t1 = centro - apertura.larghezza / 2, centro + apertura.larghezza / 2
            nuovi = []
            for s0, s1 in tratti:
                if t1 <= s0 or t0 >= s1:
                    nuovi.append((s0, s1))
                    continue
                if t0 > s0:
                    nuovi.append((s0, t0))
                if t1 < s1:
                    nuovi.append((t1, s1))
            tratti = nuovi
        out += [(muro, s0, s1) for s0, s1 in tratti if s1 - s0 > 1e-6]
    return out


def _rettangolo_del_tratto(muro: Muro, s0: float, s1: float) -> Anello:
    h = muro.spessore / 2
    return [_sull_asse(muro, s, d) for s, d in ((s0, -h), (s1, -h), (s1, h), (s0, h))]


def _rettilineo(poligono: Sequence[Punto]) -> bool:
    """Ogni lato orizzontale o verticale."""
    return all(
        abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6
        for a, b in zip(poligono, [*poligono[1:], poligono[0]], strict=True)
    )


def _q(v: float) -> float:
    """Al decimo di millimetro: due capi che a mano differiscono di un nonnulla coincidono."""
    return round(v, 4) + 0.0


def unione_rettilinea(poligoni: Sequence[Sequence[Punto]]) -> list[Anello]:
    """Il contorno dell'unione di poligoni con i lati orizzontali e verticali: gli anelli,
    in senso orario sul foglio quelli di fuori e antiorario i buchi.

    Si compone una griglia sulle ascisse e le ordinate dei vertici, si riempiono le celle
    che stanno dentro un poligono (pari e dispari), e il contorno sono i lati fra una cella
    piena e una vuota, concatenati: dove due celle piene si toccano solo d'angolo, l'anello
    gira verso il pieno, e ne escono due anelli che non si toccano."""
    if not poligoni:
        return []
    pronti = [[(_q(x), _q(y)) for x, y in p] for p in poligoni]
    xs = sorted({x for p in pronti for x, _ in p})
    ys = sorted({y for p in pronti for _, y in p})
    nx, ny = len(xs) - 1, len(ys) - 1
    if nx < 1 or ny < 1:
        return []
    pieno = bytearray(nx * ny)
    for poligono in pronti:
        j0, j1 = bisect_left(ys, min(y for _, y in poligono)), bisect_left(ys, max(y for _, y in poligono))
        lati = list(zip(poligono, [*poligono[1:], poligono[0]], strict=True))
        for j in range(j0, j1):
            cy = (ys[j] + ys[j + 1]) / 2
            tagli = sorted(a[0] for a, b in lati if abs(a[0] - b[0]) < 1e-9 and min(a[1], b[1]) < cy < max(a[1], b[1]))
            for xa, xb in zip(tagli[0::2], tagli[1::2], strict=False):
                for i in range(bisect_left(xs, xa), bisect_left(xs, xb)):
                    pieno[j * nx + i] = 1

    def e_pieno(i: int, j: int) -> bool:
        return 0 <= i < nx and 0 <= j < ny and bool(pieno[j * nx + i])

    # I lati di contorno, orientati col pieno a destra (sul foglio, y in basso).
    uscenti: dict[Punto, list[Punto]] = {}
    for j in range(ny):
        for i in range(nx):
            if not pieno[j * nx + i]:
                continue
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
            if not e_pieno(i, j - 1):
                uscenti.setdefault((x0, y0), []).append((x1, y0))
            if not e_pieno(i + 1, j):
                uscenti.setdefault((x1, y0), []).append((x1, y1))
            if not e_pieno(i, j + 1):
                uscenti.setdefault((x1, y1), []).append((x0, y1))
            if not e_pieno(i - 1, j):
                uscenti.setdefault((x0, y1), []).append((x0, y0))

    def svolta(arrivo: Punto, da: Punto, verso: Punto) -> int:
        """Ordine di preferenza: prima a destra (verso il pieno), poi dritto, poi a sinistra."""
        dx, dy = arrivo[0] - da[0], arrivo[1] - da[1]
        vx, vy = verso[0] - arrivo[0], verso[1] - arrivo[1]
        vettoriale = dx * vy - dy * vx
        return 0 if vettoriale > 0 else (1 if vettoriale == 0 else 2)

    anelli: list[Anello] = []
    for inizio in sorted(uscenti):
        while uscenti.get(inizio):
            anello = [inizio]
            precedente, corrente = inizio, uscenti[inizio].pop(0)
            while corrente != inizio:
                anello.append(corrente)
                scelte = uscenti[corrente]
                prossimo = min(scelte, key=lambda v: (svolta(corrente, precedente, v), v))  # noqa: B023
                scelte.remove(prossimo)
                precedente, corrente = corrente, prossimo
            anelli.append(_senza_vertici_in_linea(anello))
    return [a for a in anelli if len(a) >= 4]


def _senza_vertici_in_linea(anello: Anello) -> Anello:
    out: Anello = []
    n = len(anello)
    for k, b in enumerate(anello):
        a, c = anello[k - 1], anello[(k + 1) % n]
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-12:
            out.append(b)
    return out


def area_con_segno(anello: Sequence[Punto]) -> float:
    """Positiva per un anello in senso orario sul foglio (y in basso)."""
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(anello, [*anello[1:], anello[0]], strict=True)) / 2


def dentro(p: Punto, poligono: Sequence[Punto]) -> bool:
    x, y = p
    risposta = False
    for a, b in zip(poligono, [*poligono[1:], poligono[0]], strict=True):
        if (a[1] > y) != (b[1] > y):
            xi = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < xi:
                risposta = not risposta
    return risposta


def _con_i_buchi(anelli: list[Anello]) -> list[tuple[Anello, list[Anello]]]:
    """Ogni anello di fuori con i suoi buchi: il buco va all'anello di fuori piu' piccolo
    che lo contiene."""
    fuori = sorted((a for a in anelli if area_con_segno(a) > 0), key=area_con_segno)
    gruppi: list[tuple[Anello, list[Anello]]] = [(a, []) for a in fuori]
    for buco in (a for a in anelli if area_con_segno(a) <= 0):
        prova = ((buco[0][0] + buco[1][0]) / 2, (buco[0][1] + buco[1][1]) / 2)
        # un punto appena dentro il buco: il lato da 0 a 1, spostato a sinistra (verso il vuoto)
        dx, dy = buco[1][0] - buco[0][0], buco[1][1] - buco[0][1]
        lungo = math.hypot(dx, dy) or 1.0
        prova = (prova[0] + dy / lungo * 1e-5, prova[1] - dx / lungo * 1e-5)
        for anello, buchi in gruppi:
            if dentro(prova, anello):
                buchi.append(buco)
                break
    return gruppi


def sagome_dei_muri(pianta: Pianta) -> tuple[list[tuple[Anello, list[Anello]]], list[Anello]]:
    """Le sagome da disegnare: i gruppi di muri dritti uniti (l'anello di fuori e i buchi), e
    a parte i pezzi che non hanno i lati dritti (un muro obliquo, una sagoma storta), uno per
    uno. Dalle `sagome_muri` se la pianta le da' (B-2), se no dai `muri` con i raccordi."""
    if pianta.sagome_muri:
        pezzi: list[Anello] = [[(float(x), float(y)) for x, y in s] for s in pianta.sagome_muri]
    else:
        pezzi = [_rettangolo_del_tratto(muro, s0, s1) for muro, s0, s1 in tratti_pieni(pianta)]
    dritti = [p for p in pezzi if _rettilineo(p)]
    storti = [p for p in pezzi if not _rettilineo(p)]
    return _con_i_buchi(unione_rettilinea(dritti)), storti


# --- il disegno ------------------------------------------------------------------------------


def _chiusa(punti: Sequence[Punto]) -> tuple[Punto, ...]:
    return (*punti, punti[0])


def muri_della_base(pianta: Pianta, P: Callable[[float, float], Punto], velo: float = 1.0) -> list[Primitiva]:
    """I muri della base: il pieno grigio chiaro e il contorno sottile, sull'unione delle
    sagome."""
    gruppi, storti = sagome_dei_muri(pianta)
    out: list[Primitiva] = []
    for anello, buchi in gruppi:
        out.append(Area(tuple(P(*q) for q in anello), GRIGIO_DEI_MURI, LAYER_MURI, velo,
                        tuple(tuple(P(*q) for q in b) for b in buchi)))
    for pezzo in storti:
        out.append(Area(tuple(P(*q) for q in pezzo), GRIGIO_DEI_MURI, LAYER_MURI, velo))
    for anello in [*(a for a, buchi in gruppi for a in (a, *buchi)), *storti]:
        out.append(Linea(_chiusa([P(*q) for q in anello]), CONTORNO_DEI_MURI, TRATTO_FINE_MM, LAYER_MURI))
    return out


def _segmenti(punti: Sequence[Punto], di: str, mezzo: float) -> list[tuple[str, Segmento]]:
    return [(di, (a[0], a[1], b[0], b[1], mezzo)) for a, b in zip(punti, punti[1:], strict=False)]


def _lato_della_cerniera(apertura: Apertura, muro: Muro, s0: float, s1: float) -> float:
    """L'ascissa, lungo l'asse, dello stipite con la cerniera."""
    if apertura.cerniera is None:
        return s0
    a, b = _sull_asse(muro, s0, 0.0), _sull_asse(muro, s1, 0.0)
    indice = 0 if apertura.cerniera in ("sinistra", "destra") else 1
    piu_piccolo = s0 if a[indice] <= b[indice] else s1
    return piu_piccolo if apertura.cerniera in ("sinistra", "sopra") else (s1 if piu_piccolo == s0 else s0)


def _anta(muro: Muro, cerniera_s: float, libero_s: float, larghezza: float, segno: float,
          P: Callable[[float, float], Punto], k: float, di: str) -> tuple[list[Primitiva], list[tuple[str, Segmento]]]:
    """Un'anta a battente: la linea dell'anta aperta a 90 gradi e l'arco fino all'altro stipite."""
    h = muro.spessore / 2
    cerniera = _sull_asse(muro, cerniera_s, segno * h)
    anta = _sull_asse(muro, cerniera_s, segno * (h + larghezza))
    stipite = _sull_asse(muro, libero_s, segno * h)
    a_cerniera = math.atan2(anta[1] - cerniera[1], anta[0] - cerniera[0])
    a_stipite = math.atan2(stipite[1] - cerniera[1], stipite[0] - cerniera[0])
    orario = (a_stipite - a_cerniera) % (2 * math.pi) < math.pi
    centro, raggio = P(*cerniera), larghezza * k
    primitive: list[Primitiva] = [
        Linea((P(*cerniera), P(*anta)), LINEA_DELLE_PORTE, TRATTO_FINE_MM, LAYER_APERTURE),
        Arco(centro, raggio, P(*anta), P(*stipite), orario, LINEA_DELLE_PORTE, TRATTO_FINE_MM, LAYER_APERTURE),
    ]
    passo = ((a_stipite - a_cerniera + math.pi) % (2 * math.pi) - math.pi) / 8
    corde = [(centro[0] + raggio * math.cos(a_cerniera + i * passo), centro[1] + raggio * math.sin(a_cerniera + i * passo))
             for i in range(9)]
    return primitive, [*_segmenti((P(*cerniera), P(*anta)), di, 0.09), *_segmenti(corde, di, 0.09)]


def aperture_della_base(
    pianta: Pianta, P: Callable[[float, float], Punto], k: float,
) -> tuple[list[Primitiva], list[tuple[str, Segmento]]]:
    """Finestre, porte, fori e balconi; e, per le scritte, i tratti che non devono toccare."""
    primitive: list[Primitiva] = []
    tratti: list[tuple[str, Segmento]] = []
    muri = {m.id: m for m in pianta.muri}
    for apertura in pianta.aperture:
        muro = muri[apertura.muro]
        ux, uy, _ = _asse(muro)
        centro = (apertura.centro[0] - muro.da[0]) * ux + (apertura.centro[1] - muro.da[1]) * uy
        s0, s1 = centro - apertura.larghezza / 2, centro + apertura.larghezza / 2
        h = muro.spessore / 2
        di = f"{apertura.tipo} {apertura.id}"
        if apertura.tipo == "finestra":
            vano = [P(*_sull_asse(muro, s, d)) for s, d in ((s0, -h), (s1, -h), (s1, h), (s0, h))]
            primitive.append(Area(tuple(vano), CELESTE_DELLE_FINESTRE, LAYER_FINESTRE))
            primitive.append(Linea(_chiusa(vano), LINEA_DELLE_FINESTRE, TRATTO_FINE_MM, LAYER_FINESTRE))
            vetro = (P(*_sull_asse(muro, s0, 0.0)), P(*_sull_asse(muro, s1, 0.0)))
            primitive.append(Linea(vetro, LINEA_DELLE_FINESTRE, TRATTO_FINE_MM, LAYER_FINESTRE))
            for linea in ((vano[0], vano[1]), vetro, (vano[3], vano[2])):
                tratti += _segmenti(linea, di, 0.09)
        elif apertura.tipo == "foro":
            vano = [P(*_sull_asse(muro, s, d)) for s, d in ((s0, -h), (s1, -h), (s1, h), (s0, h))]
            primitive.append(Linea(_chiusa(vano), LINEA_DELLE_PORTE, TRATTO_FINE_MM, LAYER_APERTURE, TRATTO_DEI_FORI))
        elif apertura.tipo == "porta":
            verso = {"sopra": (0.0, -1.0), "sotto": (0.0, 1.0), "sinistra": (-1.0, 0.0), "destra": (1.0, 0.0)}
            segno = 1.0
            if apertura.apre_verso is not None:
                v = verso[apertura.apre_verso]
                segno = 1.0 if -uy * v[0] + ux * v[1] >= 0 else -1.0
            if apertura.apre_verso is None and apertura.anta != "scorrevole":
                # Il verso non e' dato (uno schizzo, un catastale che non lo disegna): l'anta si
                # disegna chiusa, nel vano. Un arco da una parte a caso sembrerebbe un dato letto.
                chiusa = (P(*_sull_asse(muro, s0, 0.0)), P(*_sull_asse(muro, s1, 0.0)))
                primitive.append(Linea(chiusa, LINEA_DELLE_PORTE, TRATTO_FINE_MM, LAYER_APERTURE))
                tratti += _segmenti(chiusa, di, 0.09)
            elif apertura.anta == "scorrevole":
                m = SPESSORE_DELL_ANTA_SCORREVOLE_M / 2
                d0 = segno * h / 2
                listello = [P(*_sull_asse(muro, s, d0 + d)) for s, d in ((s0, -m), (s1, -m), (s1, m), (s0, m))]
                primitive.append(Linea(_chiusa(listello), LINEA_DELLE_PORTE, TRATTO_FINE_MM, LAYER_APERTURE))
                tratti += _segmenti(_chiusa(listello), di, 0.09)
            elif apertura.anta == "doppia":
                mezzo_s = (s0 + s1) / 2
                for cerniera_s, libero_s in ((s0, mezzo_s), (s1, mezzo_s)):
                    p, t = _anta(muro, cerniera_s, libero_s, apertura.larghezza / 2, segno, P, k, di)
                    primitive += p
                    tratti += t
            else:
                cerniera_s = _lato_della_cerniera(apertura, muro, s0, s1)
                libero_s = s1 if cerniera_s == s0 else s0
                p, t = _anta(muro, cerniera_s, libero_s, apertura.larghezza, segno, P, k, di)
                primitive += p
                tratti += t
    for balcone in pianta.balconi:
        contorno = _chiusa([P(*q) for q in balcone.poligono])
        primitive.append(Linea(contorno, LINEA_DEI_BALCONI, TRATTO_FINE_MM, LAYER_BALCONI))
        tratti += _segmenti(contorno, f"balcone {balcone.id}", 0.09)
    return primitive, tratti


def superficie(poligono: Sequence[Punto]) -> float:
    """La superficie di un poligono, in m²: quella che si scrive accanto al nome."""
    return abs(area_con_segno(poligono))


def locali_con_nome(pianta: Pianta) -> list[tuple[str, tuple[str, ...], list[Punto]]]:
    """I locali che hanno un nome sulla tavola — le stanze, poi i balconi —: chi sono, le
    parti della scritta (il nome, la zona, i mq dal poligono) e il poligono."""
    from .lunghezze import metri

    out: list[tuple[str, tuple[str, ...], list[Punto]]] = []
    for stanza in pianta.stanze:
        parti = tuple(v for v in (stanza.nome, stanza.zona, f"{metri(superficie(stanza.poligono))} m²") if v)
        out.append((f"stanza {stanza.id}", parti, [(float(x), float(y)) for x, y in stanza.poligono]))
    for balcone in pianta.balconi:
        parti = (balcone.nome, f"{metri(superficie(balcone.poligono))} m²")
        out.append((f"balcone {balcone.id}", parti, [(float(x), float(y)) for x, y in balcone.poligono]))
    return out
