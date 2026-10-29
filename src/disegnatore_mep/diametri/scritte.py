"""La scritta di un tratto, dato del progettista: «Ø200 · L 6 m», «3G2,5 · L 20 m».

**La skill non dimensiona l'aria, l'elettrico e il bus** (REL-012, I-225): la sezione
e la lunghezza di un tratto le da' il progettista, e la tavola le scrive come le ha
date. Sono tre campi della tubazione (`ConnectionModel`), facoltativi:

- `scritta` — un testo libero, e se c'e' **vince**: «di fabbrica», «bus · L 9 m»;
- altrimenti `sezione` e `lunghezza_m`: «{sezione} · L {lunghezza} m», con la virgola
  decimale e senza decimali inutili — 6 fa «6», 3,5 fa «3,5». Con uno solo dei due si
  scrive quello: «Ø200», «L 6 m». Una lunghezza zero e' un raccordo diretto: il tratto
  non porta scritta, salvo una `scritta` data;
- altrimenti niente.

**Chi la posa e' il posatore dei diametri** (`layout.diametri`), con le sue regole: in
linea con la tubazione, sopra la mandata e sotto il ritorno, senza toccare niente, e
per un tratto di strada principale l'etichetta staccata con freccia come ultima
spiaggia. **Un DN calcolato sullo stesso tratto cede il posto**: il dato del
progettista vince sul conto della skill. In legenda la scritta ha **la sua riga**,
«Ø · L — sezione e lunghezza, dato del progettista», e quella del DN calcolato resta
«Øi» (I-155).

**Un tratto, una scritta.** Il tratto e' quello del motore: da un pezzo all'altro,
attraverso gli organi in linea (`layout.trunks`). Se una sola tubazione del tratto
porta il dato, la scritta e' del tratto intero, e si posa su qualunque suo
rettilineo; se ne portano piu' d'una — l'alimentazione dal quadro al sezionatore e
dal sezionatore alla macchina, due cavi —, ciascuna ha la sua scritta, sul pezzo di
linea fra i due organi che la chiudono.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import ConnectionModel, ProjectModel

from .tratti import TrattoDelDiametro, tratti_da_etichettare

CAMPIONE_DELLA_LEGENDA = "Ø · L"
TESTO_DELLA_LEGENDA = "sezione e lunghezza, dato del progettista"
"""La riga della legenda che spiega la scritta di un tratto: la sua, accanto a quella
del DN calcolato («Øi», I-155), che resta com'e'. **Proposta della sessione**."""

SEPARATORE = " · "


def numero_italiano(valore: float) -> str:
    """Un numero come si scrive su una tavola italiana: la virgola decimale, e nessun
    decimale che non serve — 6 fa «6», 3,5 fa «3,5», 12,25 fa «12,25»."""
    testo = f"{valore:.3f}".rstrip("0").rstrip(".")
    return "0" if testo in ("", "-0") else testo.replace(".", ",")


def testo_della_tubazione(tubazione: ConnectionModel) -> str | None:
    """Che cosa la tavola scrive sul tratto di questa tubazione, o `None`."""
    if tubazione.scritta is not None and tubazione.scritta.strip():
        return tubazione.scritta.strip()
    if tubazione.lunghezza_m == 0:
        # Un raccordo diretto non ha un tratto da quotare: la sua sezione sta gia'
        # nell'etichetta del pezzo, e una scritta obbligatoria su un moncone di pochi
        # millimetri fermava la tavola (collaudo T1, §2.2 punto 10).
        return None
    parti: list[str] = []
    if tubazione.sezione is not None and tubazione.sezione.strip():
        parti.append(tubazione.sezione.strip())
    if tubazione.lunghezza_m is not None:
        parti.append(f"L {numero_italiano(tubazione.lunghezza_m)} m")
    return SEPARATORE.join(parti) if parti else None


@dataclass(frozen=True)
class ScrittaDelTratto:
    """Una scritta da posare: il testo e le tubazioni che nomina.

    Ha la stessa forma che il posatore legge da un `TrattoDelDiametro` — `scritta`,
    `connection_ids`, `strada_principale` — e il posatore non le distingue: e' la
    stessa scritta in linea con la tubazione."""

    scritta: str
    connection_ids: frozenset[str]
    tubazione: str
    """La tubazione che porta il dato."""
    strada_principale: bool = True
    """Il dato del progettista non si sacrifica (I-161 vale per il DN calcolato): se
    accanto alla linea non c'e' posto, va su un'etichetta staccata con freccia."""


def scritte_dei_tratti(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunks: Sequence[Trunk] | None = None,
) -> tuple[ScrittaDelTratto, ...]:
    """Le scritte dei tratti di questo impianto, nell'ordine delle tratte del motore.

    Nessuna, se nessuna tubazione porta sezione, lunghezza o scritta: il conto delle
    tratte non si fa nemmeno, e le tavole di oggi restano quelle di ieri."""
    testi = {
        item.id: testo
        for item in project.connections
        if (testo := testo_della_tubazione(item)) is not None
    }
    if not testi:
        return ()
    tutte = list(trunks) if trunks is not None else tratte_del_progetto(project, catalog)
    scritte: list[ScrittaDelTratto] = []
    for tratta in tutte:
        con_dato = [item for item in tratta.connection_ids if item in testi]
        if len(con_dato) == 1:
            (tubazione,) = con_dato
            scritte.append(
                ScrittaDelTratto(
                    scritta=testi[tubazione],
                    connection_ids=frozenset(tratta.connection_ids),
                    tubazione=tubazione,
                )
            )
            continue
        scritte.extend(
            ScrittaDelTratto(
                scritta=testi[tubazione],
                connection_ids=frozenset({tubazione}),
                tubazione=tubazione,
            )
            for tubazione in con_dato
        )
    return tuple(scritte)


def tratti_da_scrivere(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunks: Sequence[Trunk] | None = None,
) -> tuple[tuple[ScrittaDelTratto, ...], tuple[TrattoDelDiametro, ...]]:
    """Le scritte dei tratti e i DN calcolati che la tavola porta, in quest'ordine.

    **Il DN cede il posto** a una scritta del progettista che tocca lo stesso tratto:
    il dato vince sul conto. La leggono l'esecutore del piano, che le posa, e il
    preflight, che conta che ci siano tutte e una sola per tratto."""
    scritte = scritte_dei_tratti(project, catalog, trunks)
    coperte = {item for scritta in scritte for item in scritta.connection_ids}
    calcolati = tuple(
        item
        for item in tratti_da_etichettare(project, catalog, trunks)
        if not item.connection_ids & coperte
    )
    return scritte, calcolati


__all__ = [
    "CAMPIONE_DELLA_LEGENDA",
    "TESTO_DELLA_LEGENDA",
    "ScrittaDelTratto",
    "numero_italiano",
    "scritte_dei_tratti",
    "testo_della_tubazione",
    "tratti_da_scrivere",
]
