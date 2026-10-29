"""Le tabelle nelle zone del foglio: il motore le posa e le disegna (REL-012).

Il piano puo' lasciare alle tabelle una zona a destra del disegno e una sotto
(`PianoDiComposizione.zone_tabelle`, `SheetFrame.zona_destra_mm`, `zona_basso_mm`).
Un altro modulo — la distinta dei materiali, la tabella delle tratte (REL-013) —
passa al motore **che cosa** scrivere (`TabellaNelleZone`: titolo, colonne con la
loro larghezza, righe e righe di sezione), e il motore decide **dove**:

- le tabelle di una zona si posano **una sotto l'altra**, nell'ordine in cui
  arrivano, dall'angolo in alto a sinistra della zona;
- una tabella che non entra in quel che resta della colonna **continua nella colonna
  accanto**, con l'intestazione ripetuta; una riga di sezione non resta mai ultima
  in fondo a una colonna, staccata dalle sue righe;
- il testo di una cella **va a capo** fra le parole sulla larghezza della colonna,
  misurato con le larghezze di Arial, come la legenda (REL-008);
- se una tabella non entra nella zona, o una parola sola non entra nella sua
  colonna, **e' un errore che lo dice** (`LayoutError`): il testo non si
  rimpicciolisce, e una tabella non si disegna sopra il disegno.

Il kit aria-aria le scriveva **dopo**, nell'SVG gia' fatto, e poi nel DXF a mano
(`docs/input-pm/2026-10-29-kit-aria-aria/lavoro/tabelle.py`): qui sono parte della
tavola, e SVG, PDF e DXF le scrivono dalle stesse linee e dagli stessi testi
(`tratti_della_tabella_posata`).

**Il PDF e' WinAnsi**: «≥», «≤», «→» non ci sono. Il testo delle tabelle passa per
le sostituzioni dichiarate del PDF (`pdf.per_winansi`) **prima** di essere misurato
e scritto: SVG, PDF e DXF portano «>=», e la colonna e' larga quanto quel testo.

Le misure — corpo, righe, rientri — sono quelle della tabella delle apparecchiature
(`graphics.tabella`), che il PO ha approvato (D-192, D-194): una tavola, un modo di
fare le tabelle. **Proposta della sessione** per il resto: lo stacco fra le tabelle,
il titolo in neretto sopra la tabella, la riga di sezione in neretto senza le
divisioni delle colonne.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    ColonnaDellaTabella,
    RigaDellaTabellaLibera,
    SheetGeometry,
    TabellaNelleZone,
    TabellaPosata,
)

from .cartiglio import FAMIGLIA, PT_MM, larghezza_mm
from .frame import Rect, SheetFrame
from .pdf import per_winansi
from .standard import GraphicStandard
from .tabella import MARGINE_DELLA_RIGA_MM, RIENTRO_MM, altezza_della_riga_mm

MARGINE_DALLA_ZONA_MM = 2.5
"""Quanto le tabelle stanno lontane dai bordi della zona: dal disegno, dalla legenda,
dal cartiglio. Un passo di griglia."""

STACCO_FRA_LE_TABELLE_MM = 5.0
"""Lo spazio fra due tabelle una sotto l'altra, e fra due colonne di zona."""

INTERLINEA_EM = 1.15
"""Il passo fra due righe dello stesso testo, in corpi: quello della legenda."""

ALTEZZA_MAIUSCOLE_EM = 0.7
"""Le maiuscole di Arial sono alte 0,716 corpi (`dxf.ALTEZZA_MAIUSCOLE_EM`)."""

STACCO_DEL_TITOLO_MM = 1.5
"""Fra la base del titolo e la linea alta della tabella."""


def _a_capo(testo: str, larghezza: float, corpo_pt: float, grassetto: bool) -> list[str]:
    """Le righe di un testo che va a capo fra le parole: riempie ogni riga fin dove
    entra. Una parola da sola piu' larga della colonna e' un errore di chi ha dato le
    larghezze, e lo dice chi chiama."""
    righe: list[str] = []
    corrente = ""
    for parola in testo.split():
        prova = f"{corrente} {parola}" if corrente else parola
        if corrente and larghezza_mm(prova, corpo_pt, grassetto) > larghezza + 1e-9:
            righe.append(corrente)
            corrente = parola
        else:
            corrente = prova
    if corrente:
        righe.append(corrente)
    return righe or [""]


@dataclass(frozen=True)
class _Misure:
    """Le misure di una tabella al corpo dato."""

    corpo_mm: float
    riga_mm: float
    """L'altezza di una riga di una sola linea di testo."""

    @property
    def corpo_pt(self) -> float:
        return self.corpo_mm / PT_MM

    @property
    def passo_mm(self) -> float:
        return INTERLINEA_EM * self.corpo_mm

    @property
    def titolo_mm(self) -> float:
        return ALTEZZA_MAIUSCOLE_EM * self.corpo_mm + STACCO_DEL_TITOLO_MM


def _misure(standard: GraphicStandard) -> _Misure:
    corpo = standard.text_small_mm
    return _Misure(corpo_mm=corpo, riga_mm=altezza_della_riga_mm(corpo))


def _righe_della_cella(testo: str, colonna: ColonnaDellaTabella, misure: _Misure, grassetto: bool) -> list[str]:
    utile = colonna.larghezza_mm - 2 * RIENTRO_MM
    righe = _a_capo(per_winansi(testo), utile, misure.corpo_pt, grassetto)
    for riga in righe:
        if larghezza_mm(riga, misure.corpo_pt, grassetto) > utile + 1e-9:
            raise LayoutError(
                f"«{riga}» non entra nella colonna «{colonna.intestazione}», larga "
                f"{colonna.larghezza_mm:g} mm: le scritte non si rimpiccioliscono, si "
                f"allarga la colonna"
            )
    return righe


def _altezza(righe: int, misure: _Misure) -> float:
    return round(misure.riga_mm + (righe - 1) * misure.passo_mm, 6)


def _altezza_della_riga(riga: RigaDellaTabellaLibera, colonne: Sequence[ColonnaDellaTabella], misure: _Misure) -> float:
    if riga.sezione is not None:
        return misure.riga_mm
    linee = max(
        len(_righe_della_cella(testo, colonna, misure, False))
        for testo, colonna in zip(riga.celle, colonne, strict=True)
    )
    return _altezza(linee, misure)


def _ha_l_intestazione(colonne: Sequence[ColonnaDellaTabella]) -> bool:
    """Una tabella con le intestazioni tutte vuote — le note della distinta — non ha la
    riga dell'intestazione: sulla M.02 restava vuota fra il titolo e la prima nota."""
    return any(item.intestazione.strip() for item in colonne)


def _altezza_dell_intestazione(colonne: Sequence[ColonnaDellaTabella], misure: _Misure) -> float:
    if not _ha_l_intestazione(colonne):
        return 0.0
    return _altezza(
        max(len(_righe_della_cella(item.intestazione, item, misure, True)) for item in colonne),
        misure,
    )


def _larghezza_del_titolo(titolo: str, misure: _Misure) -> float:
    return larghezza_mm(per_winansi(titolo), misure.corpo_pt, True)


def posa_le_tabelle(
    foglio: SheetGeometry, frame: SheetFrame, tabelle: Sequence[TabellaNelleZone]
) -> SheetGeometry:
    """Il foglio con le tabelle posate nelle loro zone.

    Solleva `LayoutError` se una tabella chiede una zona che il piano non ha
    lasciato, se non entra nella zona, o se una parola non entra nella sua colonna:
    la tavola non esce con una tabella sopra il disegno o tagliata."""
    if not tabelle:
        return foglio
    misure = _misure(frame.standard)
    zone: dict[str, Rect | None] = {"destra": frame.zona_destra_mm, "basso": frame.zona_basso_mm}
    posate: list[TabellaPosata] = []
    for nome, zona in zone.items():
        mie = [item for item in tabelle if item.zona == nome]
        if not mie:
            continue
        if zona is None:
            raise LayoutError(
                f"la tabella «{mie[0].titolo or ''}» va nella zona {nome}, e il piano non la "
                f"lascia: zone_tabelle nel piano"
            )
        posate.extend(_posa_nella_zona(zona, mie, misure, nome))
    return foglio.model_copy(update={"tabelle": [*foglio.tabelle, *posate]})


def _posa_nella_zona(
    zona: Rect, tabelle: Sequence[TabellaNelleZone], misure: _Misure, nome: str
) -> list[TabellaPosata]:
    alto = zona.y_mm + MARGINE_DALLA_ZONA_MM
    fondo = zona.bottom_mm - MARGINE_DALLA_ZONA_MM
    destra = zona.right_mm - MARGINE_DALLA_ZONA_MM
    x = zona.x_mm + MARGINE_DALLA_ZONA_MM
    y = alto
    larga = 0.0
    posate: list[TabellaPosata] = []

    def nuova_colonna() -> None:
        nonlocal x, y, larga
        x += larga + STACCO_FRA_LE_TABELLE_MM
        y = alto
        larga = 0.0

    for tabella in tabelle:
        larghezza = sum(item.larghezza_mm for item in tabella.colonne)
        intestazione = _altezza_dell_intestazione(tabella.colonne, misure)
        righe = list(tabella.righe)
        titolo = tabella.titolo
        while True:
            testa = (misure.titolo_mm if titolo is not None else 0.0) + intestazione
            # Quante righe entrano qui: una riga di sezione non resta ultima.
            disponibile = fondo - y - testa
            quante, usato = 0, 0.0
            for riga in righe:
                altezza = _altezza_della_riga(riga, tabella.colonne, misure)
                if usato + altezza > disponibile + 1e-9:
                    break
                usato += altezza
                quante += 1
            while 0 < quante < len(righe) and righe[quante - 1].sezione is not None:
                quante -= 1
            entra_tutta = quante == len(righe)
            if (quante == 0 and righe) or (disponibile < -1e-9):
                if y > alto + 1e-9:
                    nuova_colonna()
                    continue
                raise LayoutError(
                    f"la tabella «{tabella.titolo or ''}» non entra nella zona {nome}: "
                    f"nemmeno una riga sta sotto l'intestazione in {zona.height_mm:g} mm"
                )
            if titolo is not None and x + _larghezza_del_titolo(titolo, misure) > destra + 1e-9:
                raise LayoutError(
                    f"il titolo «{titolo}» non entra in una riga nella zona {nome}: restano "
                    f"{max(0.0, destra - x):g} mm"
                )
            if x + larghezza > destra + 1e-9:
                raise LayoutError(
                    f"la tabella «{tabella.titolo or ''}», larga {larghezza:g} mm, non entra "
                    f"nella zona {nome}: restano {max(0.0, destra - x):g} mm"
                )
            posate.append(
                TabellaPosata(
                    x_mm=round(x, 6),
                    y_mm=round(y, 6),
                    titolo=titolo,
                    colonne=list(tabella.colonne),
                    righe=righe[:quante],
                    corpo_mm=misure.corpo_mm,
                )
            )
            larga = max(larga, larghezza)
            y += testa + usato + STACCO_FRA_LE_TABELLE_MM
            if entra_tutta:
                break
            righe = righe[quante:]
            titolo = None
            nuova_colonna()
    return posate


@dataclass(frozen=True)
class TestoDiTabella:
    testo: str
    x_mm: float
    y_mm: float
    """La linea di base."""
    grassetto: bool
    a_destra: bool


@dataclass(frozen=True)
class TrattiDellaTabellaPosata:
    """Una tabella posata come linee e testi: quello che SVG e DXF scrivono."""

    linee: tuple[tuple[float, float, float, float], ...]
    testi: tuple[TestoDiTabella, ...]
    corpo_mm: float
    spessore_mm: float


def tratti_della_tabella_posata(
    tabella: TabellaPosata, standard: GraphicStandard
) -> TrattiDellaTabellaPosata:
    """Le linee e i testi di una tabella posata: il titolo in neretto sopra, la
    griglia al tratto sottile della legenda, l'intestazione in neretto, le righe di
    sezione in neretto e senza le divisioni delle colonne."""
    misure = _Misure(corpo_mm=tabella.corpo_mm, riga_mm=altezza_della_riga_mm(tabella.corpo_mm))
    larghezza = sum(item.larghezza_mm for item in tabella.colonne)
    sinistra = tabella.x_mm
    destra = round(sinistra + larghezza, 6)
    bordi = [sinistra]
    for colonna in tabella.colonne:
        bordi.append(round(bordi[-1] + colonna.larghezza_mm, 6))
    linee: list[tuple[float, float, float, float]] = []
    testi: list[TestoDiTabella] = []
    y = tabella.y_mm
    if tabella.titolo is not None:
        testi.append(
            TestoDiTabella(
                per_winansi(tabella.titolo),
                sinistra,
                round(y + ALTEZZA_MAIUSCOLE_EM * misure.corpo_mm, 6),
                True,
                False,
            )
        )
        y += misure.titolo_mm
    alto = y

    def scrivi(riga_alta: float, celle: Sequence[list[str]], grassetto: bool) -> None:
        for indice, (righe, colonna) in enumerate(zip(celle, tabella.colonne, strict=True)):
            for numero, testo in enumerate(righe):
                base = round(
                    riga_alta + MARGINE_DELLA_RIGA_MM + ALTEZZA_MAIUSCOLE_EM * misure.corpo_mm
                    + numero * misure.passo_mm,
                    6,
                )
                x = bordi[indice + 1] - RIENTRO_MM if colonna.a_destra else bordi[indice] + RIENTRO_MM
                testi.append(TestoDiTabella(testo, round(x, 6), base, grassetto, colonna.a_destra))

    linee.append((sinistra, y, destra, y))
    divisioni: list[tuple[float, float]] = []
    if _ha_l_intestazione(tabella.colonne):
        intestazione = [_righe_della_cella(item.intestazione, item, misure, True) for item in tabella.colonne]
        altezza = _altezza(max(len(item) for item in intestazione), misure)
        scrivi(y, intestazione, True)
        divisioni.append((y, y + altezza))
        y = round(y + altezza, 6)
        linee.append((sinistra, y, destra, y))
    for riga in tabella.righe:
        if riga.sezione is not None:
            testi.append(
                TestoDiTabella(
                    per_winansi(riga.sezione),
                    round(sinistra + RIENTRO_MM, 6),
                    round(y + MARGINE_DELLA_RIGA_MM + ALTEZZA_MAIUSCOLE_EM * misure.corpo_mm, 6),
                    True,
                    False,
                )
            )
            y = round(y + misure.riga_mm, 6)
        else:
            celle = [
                _righe_della_cella(testo, colonna, misure, False)
                for testo, colonna in zip(riga.celle, tabella.colonne, strict=True)
            ]
            altezza = _altezza(max(len(item) for item in celle), misure)
            scrivi(y, celle, False)
            divisioni.append((y, y + altezza))
            y = round(y + altezza, 6)
        linee.append((sinistra, y, destra, y))
    linee.append((sinistra, alto, sinistra, y))
    linee.append((destra, alto, destra, y))
    # Le divisioni delle colonne corrono solo sulle righe con le celle: una riga di
    # sezione attraversa la tabella da un bordo all'altro. Righe vicine si uniscono.
    tratti: list[tuple[float, float]] = []
    for da, a in divisioni:
        if tratti and abs(tratti[-1][1] - da) <= 1e-6:
            tratti[-1] = (tratti[-1][0], a)
        else:
            tratti.append((da, a))
    for bordo in bordi[1:-1]:
        linee.extend((bordo, round(da, 6), bordo, round(a, 6)) for da, a in tratti)
    return TrattiDellaTabellaPosata(
        linee=tuple(linee),
        testi=tuple(testi),
        corpo_mm=misure.corpo_mm,
        spessore_mm=standard.line_thin_mm,
    )


def riquadro_della_tabella_posata(tabella: TabellaPosata, standard: GraphicStandard) -> tuple[float, float, float, float]:
    """`(sinistra, alto, destra, basso)` di una tabella posata, titolo compreso."""
    tratti = tratti_della_tabella_posata(tabella, standard)
    xs = [x for linea in tratti.linee for x in (linea[0], linea[2])]
    ys = [y for linea in tratti.linee for y in (linea[1], linea[3])]
    if tabella.titolo is not None:
        corpo_pt = tabella.corpo_mm / PT_MM
        xs.append(tabella.x_mm + larghezza_mm(per_winansi(tabella.titolo), corpo_pt, True))
    return (min(xs), tabella.y_mm, max(xs), max(ys))


def _escape(testo: str) -> str:
    return (
        testo.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_delle_tabelle(foglio: SheetGeometry, standard: GraphicStandard) -> str:
    """Le tabelle nelle zone, nell'SVG della tavola: un gruppo, in nero."""
    parti: list[str] = []
    for tabella in foglio.tabelle:
        tratti = tratti_della_tabella_posata(tabella, standard)
        parti.append(
            f'<g class="tabella-nelle-zone" stroke="black" '
            f'stroke-width="{tratti.spessore_mm:g}" fill="none">'
        )
        parti.extend(
            f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"/>' for x1, y1, x2, y2 in tratti.linee
        )
        for item in tratti.testi:
            peso = ' font-weight="bold"' if item.grassetto else ""
            ancora = ' text-anchor="end"' if item.a_destra else ""
            parti.append(
                f'<text x="{item.x_mm:g}" y="{item.y_mm:g}" font-family="{FAMIGLIA}" '
                f'font-size="{tratti.corpo_mm:g}"{peso}{ancora} fill="black" stroke="none">'
                f"{_escape(item.testo)}</text>"
            )
        parti.append("</g>")
    return "".join(parti)


__all__ = [
    "MARGINE_DALLA_ZONA_MM",
    "STACCO_FRA_LE_TABELLE_MM",
    "TestoDiTabella",
    "TrattiDellaTabellaPosata",
    "posa_le_tabelle",
    "riquadro_della_tabella_posata",
    "svg_delle_tabelle",
    "tratti_della_tabella_posata",
]
