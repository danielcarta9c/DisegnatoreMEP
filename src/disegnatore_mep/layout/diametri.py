"""Il DN sulla tavola: dove si scrive l'etichetta di un tratto (REL-007).

**Il posto l'ha detto il PO** (I-152, I-156; D-193, punto 6): «il tag messo in
linea con la tubazione subito immediatamente sopra o sotto (a destra o sinistra
per i tratti in verticale scritto da giu' verso su)», e **su ciascuna linea: la
mandata col tag sopra, il ritorno col tag sotto**. Da qui le regole di questo
modulo, in quest'ordine:

1. **un'etichetta sola per tratto** (I-143), su uno dei suoi rettilinei, tutta
   dentro il rettilineo — non scavalca una curva ne' un capo;
2. **parallela alla linea e addosso**, a `STACCO_DALLA_LINEA_MM`: sui rettilinei
   orizzontali si legge da sinistra, sui verticali dal basso verso l'alto;
3. **il lato**: sopra la mandata, sotto il ritorno; sui verticali prima a destra
   la mandata, prima a sinistra il ritorno. **Mai fra le due corsie di una
   coppia** — la mandata e il suo ritorno che corrono affiancati (B12): una
   scritta in mezzo non dice di quale delle due e'. Se nessun rettilineo del
   tratto ha un lato esterno libero, si prova quello interno;
4. **senza toccare niente**: simboli, sigle, altre linee, altre etichette, la
   tabella delle apparecchiature (D-191) — con i franchi qui sotto;
5. dove c'e' posto, **il rettilineo orizzontale piu' lungo**, poi i verticali, e
   su ciascuno prima il centro, poi a passi verso i capi.

**Le etichette sono l'ultima cosa che si scrive** e non spostano niente
(DRAW-003): se un tratto non trova posto, l'etichetta manca e il preflight lo
dice (`DIAMETER_TAG_MISSING`).
"""

from collections.abc import Sequence
from dataclasses import dataclass

from disegnatore_mep.diametri.tratti import TrattoDelDiametro
from disegnatore_mep.graphics.cartiglio import PT_MM, larghezza_mm
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.graphics.standard import CORPO_MINIMO_PT, GraphicStandard

from .geometry import DiametroSullaTavola, NotaDellaLegenda, Point, RoutedTrunk, SheetGeometry
from .labels import (
    DIAGONALS,
    LEADER_MAX_STEPS,
    LEADER_MIN_LENGTH_MM,
    _crosses,
    richiamo_verso,
    riquadro_della_scritta,
    segmenti_del_richiamo,
    segments_cross,
)
from .legend import (
    INSET_MM,
    INTERLINEA_EM,
    ROW_HEIGHT_MM,
    SECTION_GAP_MM,
    a_capo,
    larghezza_del_nome_mm,
)

Box = tuple[float, float, float, float]

STACCO_DALLA_LINEA_MM = 1.25
"""Dall'asse della linea al bordo della scritta: «subito sopra o sotto» (I-152).

La linea e' larga mezzo millimetro, quindi fra il suo bordo e il testo resta un
millimetro: si legge attaccata alla linea, e non la tocca. **Taratura** della
sessione, da giudicare sulla tavola."""

FRANCO_MM = 0.5
"""Quanto l'etichetta sta lontana da cio' che non e' la sua linea: simboli,
testi e le altre linee, che per le sigle sono gia' allargate di mezzo millimetro
(`labels.LINE_CLEARANCE_MM`). Un millimetro in tutto da un'altra tubazione:
abbastanza perche' la scritta non si legga come sua."""

RIENTRO_DAI_CAPI_MM = 1.0
"""Quanto l'etichetta resta dentro il rettilineo, dai suoi due capi: non arriva
sulla curva, sull'attacco o sull'organo in linea che lo chiude. Era 1,5 mm con
le scritte a 1,8 mm; a 9 punti (REL-008) con 1,5 mm tredici DN delle sette
tavole di prova non entravano che a 8 punti, con 1,0 mm entrano tutti a 9."""

DISTANZA_DELLA_COPPIA_MM = 10.0
"""Entro questa distanza una linea parallela dello stesso fluido e del verso
opposto e' **la corsia accanto** della stessa coppia: fra le due l'etichetta non
va. Dieci millimetri sono quattro passi di griglia, piu' dello stacco con cui il
motore affianca mandata e ritorno."""

PASSO_LUNGO_LA_LINEA_MM = 1.25
"""Di quanto l'etichetta si sposta lungo il rettilineo cercando posto: mezzo
passo di griglia."""

CAMPIONE_DELLA_LEGENDA = "Øi"
TESTO_DELLA_LEGENDA = "diametro interno netto minimo in mm, materiale a scelta"
"""La riga della legenda che spiega la scritta (I-155): la frase e' quella che il
PO ha scelto con la proposta."""


def larghezza_del_testo_mm(testo: str, corpo_mm: float) -> float:
    """Quanto e' lunga una scritta in Arial, dalle larghezze del cartiglio
    (`graphics.metriche`, Liberation Sans, che ha le larghezze di Arial): la
    scritta del DN dichiara Arial, e la sua misura deve essere quella vera. La
    stima delle sigle (`labels.text_width_mm`) la darebbe un quarto piu' lunga, e
    un tratto fra due valvole resterebbe senza DN per un millimetro."""
    return larghezza_mm(testo, corpo_mm / PT_MM, False)


@dataclass(frozen=True)
class _Rettilineo:
    route: RoutedTrunk
    orizzontale: bool
    fisso: float
    """La y di un rettilineo orizzontale, la x di uno verticale."""
    da: float
    a: float

    @property
    def lunghezza(self) -> float:
        return self.a - self.da


def _overlap(first: Box, second: Box) -> bool:
    return (
        first[0] < second[2] - 1e-6
        and second[0] < first[2] - 1e-6
        and first[1] < second[3] - 1e-6
        and second[1] < first[3] - 1e-6
    )


def _allargato(box: Box, di: float) -> Box:
    return (box[0] - di, box[1] - di, box[2] + di, box[3] + di)


def _rettilinei(route: RoutedTrunk) -> list[_Rettilineo]:
    """I tratti dritti di una spezzata, uniti quando due passi di fila stanno
    sulla stessa retta."""
    trovati: list[_Rettilineo] = []
    for polilinea in route.segments:
        corrente: _Rettilineo | None = None
        for prima, dopo in zip(polilinea, polilinea[1:], strict=False):
            orizzontale = abs(prima.y_mm - dopo.y_mm) <= 1e-6
            verticale = abs(prima.x_mm - dopo.x_mm) <= 1e-6
            if orizzontale == verticale:
                if corrente is not None:
                    trovati.append(corrente)
                corrente = None
                continue
            fisso = prima.y_mm if orizzontale else prima.x_mm
            da = min(prima.x_mm, dopo.x_mm) if orizzontale else min(prima.y_mm, dopo.y_mm)
            a = max(prima.x_mm, dopo.x_mm) if orizzontale else max(prima.y_mm, dopo.y_mm)
            if (
                corrente is not None
                and corrente.orizzontale == orizzontale
                and abs(corrente.fisso - fisso) <= 1e-6
                and (abs(corrente.a - da) <= 1e-6 or abs(corrente.da - a) <= 1e-6)
            ):
                corrente = _Rettilineo(
                    route, orizzontale, fisso, min(corrente.da, da), max(corrente.a, a)
                )
                continue
            if corrente is not None:
                trovati.append(corrente)
            corrente = _Rettilineo(route, orizzontale, fisso, da, a)
        if corrente is not None:
            trovati.append(corrente)
    return trovati


def _riquadro(rettilineo: _Rettilineo, lato: str, inizio: float, larghezza: float, corpo: float) -> Box:
    """Il riquadro della scritta su un lato del rettilineo, da `inizio` a
    `inizio + larghezza` lungo la linea — da sinistra sull'orizzontale, dall'alto
    sul verticale, dove la scritta pero' si legge dal basso."""
    stacco = STACCO_DALLA_LINEA_MM
    fine = inizio + larghezza
    if rettilineo.orizzontale:
        if lato == "sopra":
            return (inizio, rettilineo.fisso - stacco - corpo, fine, rettilineo.fisso - stacco)
        return (inizio, rettilineo.fisso + stacco, fine, rettilineo.fisso + stacco + corpo)
    if lato == "destra":
        return (rettilineo.fisso + stacco, inizio, rettilineo.fisso + stacco + corpo, fine)
    return (rettilineo.fisso - stacco - corpo, inizio, rettilineo.fisso - stacco, fine)


def _ancora(rettilineo: _Rettilineo, lato: str, riquadro: Box) -> Point:
    """La base della scritta: per l'orizzontale l'angolo in basso a sinistra, come
    un `<text>` SVG; per il verticale, girato di 90 gradi e letto dal basso, il
    punto da cui la scritta sale, sul bordo destro del suo riquadro."""
    if rettilineo.orizzontale:
        return Point(x_mm=riquadro[0], y_mm=riquadro[3])
    return Point(x_mm=riquadro[2], y_mm=riquadro[3])


def _lati(rettilineo: _Rettilineo) -> tuple[str, str]:
    if rettilineo.orizzontale:
        return ("sopra", "sotto") if rettilineo.route.supply else ("sotto", "sopra")
    return ("destra", "sinistra") if rettilineo.route.supply else ("sinistra", "destra")


def _verso_il_lato(rettilineo: _Rettilineo, lato: str) -> int:
    return -1 if lato in ("sopra", "sinistra") else 1


def _fra_le_corsie(
    rettilineo: _Rettilineo, lato: str, da: float, a: float, tutti: Sequence[_Rettilineo]
) -> bool:
    """Vero se su questo lato, entro `DISTANZA_DELLA_COPPIA_MM`, corre la corsia
    accanto della stessa coppia: lo stesso fluido, il verso opposto."""
    verso = _verso_il_lato(rettilineo, lato)
    for altro in tutti:
        if altro.route is rettilineo.route or altro.orizzontale != rettilineo.orizzontale:
            continue
        if altro.route.medium != rettilineo.route.medium or altro.route.supply == rettilineo.route.supply:
            continue
        distanza = (altro.fisso - rettilineo.fisso) * verso
        if not 0 < distanza <= DISTANZA_DELLA_COPPIA_MM:
            continue
        if altro.da < a and da < altro.a:
            return True
    return False


def _posizioni(rettilineo: _Rettilineo, larghezza: float) -> list[float]:
    """Dove comincia la scritta lungo il rettilineo: prima centrata, poi a passi
    verso i capi, alternando."""
    primo = rettilineo.da + RIENTRO_DAI_CAPI_MM
    ultimo = rettilineo.a - RIENTRO_DAI_CAPI_MM - larghezza
    if ultimo < primo - 1e-6:
        return []
    centro = (rettilineo.da + rettilineo.a - larghezza) / 2
    trovate = [centro]
    passo = 1
    while True:
        aggiunte = 0
        for candidato in (centro + passo * PASSO_LUNGO_LA_LINEA_MM, centro - passo * PASSO_LUNGO_LA_LINEA_MM):
            if primo - 1e-6 <= candidato <= ultimo + 1e-6:
                trovate.append(candidato)
                aggiunte += 1
        if not aggiunte:
            break
        passo += 1
    return trovate


def _riquadro_della_linea(rettilineo: _Rettilineo) -> Box:
    if rettilineo.orizzontale:
        return (rettilineo.da, rettilineo.fisso, rettilineo.a, rettilineo.fisso)
    return (rettilineo.fisso, rettilineo.da, rettilineo.fisso, rettilineo.a)


def _punte(rettilineo: _Rettilineo) -> list[float]:
    """Dove la freccia di un'etichetta staccata tocca il rettilineo: al centro,
    poi a passi verso i capi, alternando, restando dentro di `RIENTRO_DAI_CAPI_MM`."""
    primo = rettilineo.da + RIENTRO_DAI_CAPI_MM
    ultimo = rettilineo.a - RIENTRO_DAI_CAPI_MM
    if ultimo < primo - 1e-6:
        return []
    centro = (rettilineo.da + rettilineo.a) / 2
    trovate = [centro]
    passo = 1
    while True:
        aggiunte = 0
        for candidato in (centro + passo * PASSO_LUNGO_LA_LINEA_MM, centro - passo * PASSO_LUNGO_LA_LINEA_MM):
            if primo - 1e-6 <= candidato <= ultimo + 1e-6:
                trovate.append(candidato)
                aggiunte += 1
        if not aggiunte:
            break
        passo += 1
    return trovate


def posa_i_diametri(
    tratti: Sequence[TrattoDelDiametro],
    foglio: SheetGeometry,
    standard: GraphicStandard,
    area: Rect,
    ostacoli: Sequence[Box] = (),
) -> tuple[list[DiametroSullaTavola], list[TrattoDelDiametro]]:
    """Le etichette del DN, una per tratto, e i tratti che non hanno trovato posto.

    Si posano **dopo** simboli, linee, sigle e tabella, e non spostano niente.
    Deterministico: i tratti nell'ordine in cui arrivano, i rettilinei e le
    posizioni sempre nello stesso ordine.

    **Il corpo** (REL-008): prima quello delle scritte della tavola, 9 punti; dove
    non entra, il minimo del PO, 8 punti (I-159) — prima di mettere la scritta fra
    le due corsie di una coppia, che la renderebbe ambigua.

    **Quando accanto alla linea non c'e' posto** (I-161, I-162): il DN di una
    strada secondaria si sacrifica; quello di una strada principale va, per
    ultima spiaggia, su un'etichetta staccata con freccia — la freccia sulla
    linea, un tratto a 45 gradi e la spalla orizzontale fino alla scritta
    (I-163), il richiamo piu' corto che non attraversa niente."""
    corpo = standard.text_small_mm
    minimo = CORPO_MINIMO_PT * PT_MM
    tentativi = [(corpo, False)]
    if minimo < corpo - 1e-9:
        tentativi.append((minimo, False))
    tentativi.append((corpo, True))
    if minimo < corpo - 1e-9:
        tentativi.append((minimo, True))
    limite: Box = (area.x_mm, area.y_mm, area.right_mm, area.bottom_mm)
    simboli: list[Box] = [
        (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm) for item in foglio.symbols
    ]
    simboli.extend(ostacoli)
    testi: list[Box] = []
    testi.extend(riquadro_della_scritta(label, corpo) for label in foglio.labels)
    tutti = [item for route in foglio.routes for item in _rettilinei(route)]
    linee: list[tuple[Point, Point]] = [
        (Point(x_mm=item.da, y_mm=item.fisso), Point(x_mm=item.a, y_mm=item.fisso))
        if item.orizzontale
        else (Point(x_mm=item.fisso, y_mm=item.da), Point(x_mm=item.fisso, y_mm=item.a))
        for item in tutti
    ]
    richiami: list[tuple[Point, Point]] = [
        segmento for label in foglio.labels for segmento in segmenti_del_richiamo(label)
    ]

    def libero(box: Box, proprio: _Rettilineo | None) -> bool:
        if not (
            box[0] >= limite[0] - 1e-6
            and box[1] >= limite[1] - 1e-6
            and box[2] <= limite[2] + 1e-6
            and box[3] <= limite[3] + 1e-6
        ):
            return False
        largo = _allargato(box, FRANCO_MM)
        if any(_overlap(largo, altro) for altro in (*simboli, *testi)):
            return False
        for altro in tutti:
            if altro is proprio:
                continue
            if altro.orizzontale:
                linea: Box = (altro.da, altro.fisso, altro.a, altro.fisso)
            else:
                linea = (altro.fisso, altro.da, altro.fisso, altro.a)
            if _overlap(largo, _allargato(linea, FRANCO_MM)):
                return False
        return True

    def staccata(
        tratto: TrattoDelDiametro, testo: str, propri: list[_Rettilineo]
    ) -> DiametroSullaTavola | None:
        """L'etichetta staccata con freccia (I-162): il richiamo piu' corto — anello
        per anello, dal centro del rettilineo piu' lungo verso i capi — il cui testo
        e' libero e la cui diagonale non attraversa linee, simboli, scritte o altri
        richiami."""
        larghezza = larghezza_del_testo_mm(testo, corpo)
        passo = standard.grid_mm
        primo = -(-LEADER_MIN_LENGTH_MM / 2**0.5 // passo) * passo
        for anello in range(LEADER_MAX_STEPS):
            campata = primo + anello * passo
            for rettilineo in propri:
                for lungo in _punte(rettilineo):
                    punta = (
                        Point(x_mm=lungo, y_mm=rettilineo.fisso)
                        if rettilineo.orizzontale
                        else Point(x_mm=rettilineo.fisso, y_mm=lungo)
                    )
                    for verso in DIAGONALS:
                        richiamo, ancora, box = richiamo_verso(punta, verso, campata, larghezza, corpo)
                        if not libero(box, None):
                            continue
                        segmenti = richiamo.segmenti
                        if any(
                            _crosses(*segmento, altro)
                            for segmento in segmenti
                            for altro in (box, *simboli, *testi)
                        ):
                            continue
                        if any(
                            segments_cross(segmento, altra)
                            for segmento in segmenti
                            for altra in (*linee, *richiami)
                        ):
                            continue
                        # La spalla e' orizzontale: non corre lungo un tubo, dentro il
                        # suo franco (I-163).
                        spalla = segmenti[1]
                        if any(
                            _crosses(*spalla, _allargato(_riquadro_della_linea(altro), FRANCO_MM))
                            for altro in tutti
                        ):
                            continue
                        testi.append(box)
                        richiami.extend(segmenti)
                        return DiametroSullaTavola(
                            testo=testo,
                            ancora=ancora,
                            connection_ids=sorted(tratto.connection_ids),
                            richiamo=richiamo,
                        )
        return None

    posati: list[DiametroSullaTavola] = []
    mancanti: list[TrattoDelDiametro] = []
    for tratto in tratti:
        testo = tratto.scritta
        if testo is None:
            continue
        propri = [
            item
            for item in tutti
            if item.route.connection_ids and set(item.route.connection_ids) <= tratto.connection_ids
        ]
        if not propri:
            continue
        propri.sort(key=lambda item: (not item.orizzontale, -item.lunghezza, item.fisso, item.da))
        trovato: DiametroSullaTavola | None = None
        for corpo_della_scritta, anche_fra_le_corsie in tentativi:
            larghezza = larghezza_del_testo_mm(testo, corpo_della_scritta)
            for rettilineo in propri:
                for inizio in _posizioni(rettilineo, larghezza):
                    for lato in _lati(rettilineo):
                        box = _riquadro(rettilineo, lato, inizio, larghezza, corpo_della_scritta)
                        da, a = (box[0], box[2]) if rettilineo.orizzontale else (box[1], box[3])
                        if not anche_fra_le_corsie and _fra_le_corsie(rettilineo, lato, da, a, tutti):
                            continue
                        if not libero(box, rettilineo):
                            continue
                        trovato = DiametroSullaTavola(
                            testo=testo,
                            ancora=_ancora(rettilineo, lato, box),
                            verticale=not rettilineo.orizzontale,
                            connection_ids=sorted(tratto.connection_ids),
                            corpo_mm=None if corpo_della_scritta == corpo else corpo_della_scritta,
                        )
                        testi.append(box)
                        break
                    if trovato is not None:
                        break
                if trovato is not None:
                    break
            if trovato is not None:
                break
        if trovato is None and tratto.strada_principale:
            trovato = staccata(tratto, testo, propri)
        if trovato is None:
            mancanti.append(tratto)
        else:
            posati.append(trovato)
    return posati, mancanti


def riquadro_del_diametro(etichetta: DiametroSullaTavola, corpo: float) -> Box:
    """Il riquadro che l'etichetta occupa sulla tavola: lo leggono il preflight e
    il collaudo, e deve essere quello della posa. `corpo` e' quello delle scritte
    della tavola; un'etichetta scesa al minimo porta il suo."""
    if etichetta.corpo_mm is not None:
        corpo = etichetta.corpo_mm
    larghezza = larghezza_del_testo_mm(etichetta.testo, corpo)
    if etichetta.verticale:
        return (
            etichetta.ancora.x_mm - corpo,
            etichetta.ancora.y_mm - larghezza,
            etichetta.ancora.x_mm,
            etichetta.ancora.y_mm,
        )
    return (
        etichetta.ancora.x_mm,
        etichetta.ancora.y_mm - corpo,
        etichetta.ancora.x_mm + larghezza,
        etichetta.ancora.y_mm,
    )


def nota_della_legenda(foglio: SheetGeometry, frame: SheetFrame) -> NotaDellaLegenda | None:
    """La riga della legenda che spiega «Øi» (I-155), sotto i fluidi.

    La spiegazione va a capo sulla larghezza della fascia, misurata con le
    larghezze di Arial: le altre righe della legenda sono piu' corte, questa no.
    `None` se la fascia non ha piu' posto in altezza: il testo non si
    rimpicciolisce mai, e la riga manca — il collaudo lo misura."""
    fascia = frame.legend_rect_mm
    corpo = frame.standard.text_small_mm
    righe_occupate = [item.anchor.y_mm for item in foglio.legend] + [
        item.anchor.y_mm for item in foglio.network_keys
    ]
    y = (max(righe_occupate) if righe_occupate else fascia.y_mm) + ROW_HEIGHT_MM
    if not foglio.network_keys:
        y += SECTION_GAP_MM
    righe = list(a_capo(TESTO_DELLA_LEGENDA, larghezza_del_nome_mm(frame), corpo))
    ultima = y + (len(righe) - 1) * INTERLINEA_EM * corpo
    if ultima > fascia.bottom_mm - INSET_MM:
        return None
    return NotaDellaLegenda(
        campione=CAMPIONE_DELLA_LEGENDA,
        righe=righe,
        anchor=Point(x_mm=fascia.x_mm + INSET_MM, y_mm=y),
    )


__all__ = [
    "CAMPIONE_DELLA_LEGENDA",
    "STACCO_DALLA_LINEA_MM",
    "TESTO_DELLA_LEGENDA",
    "nota_della_legenda",
    "posa_i_diametri",
    "riquadro_del_diametro",
]
