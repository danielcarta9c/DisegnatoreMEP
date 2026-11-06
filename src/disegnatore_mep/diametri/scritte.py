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
«Ø · L — sezione e lunghezza, dato del progettista»; se la sezione si legge come un
tubo — «MS 32×3», «DN 25», «Cu 28×1» (I-279) —, la spiega la riga del suo materiale,
come il tubo del calcolo.

**Un tratto, una scritta.** Il tratto e' quello del motore: da un pezzo all'altro,
attraverso gli organi in linea (`layout.trunks`). Se una sola tubazione del tratto
porta il dato, la scritta e' del tratto intero, e si posa su qualunque suo
rettilineo; se ne portano piu' d'una — l'alimentazione dal quadro al sezionatore e
dal sezionatore alla macchina, due cavi —, ciascuna ha la sua scritta, sul pezzo di
linea fra i due organi che la chiudono.

**Sulle reti d'acqua il tratto e' quello del calcolo** (I-279, `tratti`): attraversa le
valvole, i T da cui pendono sicurezze e vasi e la via dritta di una tre vie, e si ferma
dove la portata cambia. Il progettista scrive la sezione su ogni tubazione, e la tavola
ne porta **una sola per tratto**, se e' la stessa su tutte; per l'acqua la scritta e' il
tubo, senza la lunghezza, che e' un dato del calcolo delle perdite e della distinta, e
una lunghezza da sola non toglie il posto al tubo del calcolo. **Niente scritta** su
uno stacco di servizio — la sicurezza, il vaso, il riempimento, il manometro — e su un
tratto fra due raccordi dove la portata cambia che porta lo stesso tubo di un tratto
accanto la scritta cede (`segna_i_tratti_ripetuti`): la' il progettista doveva
cancellarle a mano, o la tavola si fermava (`RUN_LABEL_OMITTED`). Una `scritta` libera
resta sempre.
"""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.model.types import Domain

from .tratti import TrattoDelDiametro, tratti_da_etichettare, tratti_del_diametro
from .tubi import Tubo, tubo_dal_testo

CAMPIONE_DELLA_LEGENDA = "Ø · L"
TESTO_DELLA_LEGENDA = "sezione e lunghezza, dato del progettista"
"""La riga della legenda che spiega la scritta di un tratto: la sua, accanto a quelle
dei materiali dei tubi (I-279). **Proposta della sessione**."""

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


def testo_della_tubazione_d_acqua(tubazione: ConnectionModel) -> str | None:
    """Che cosa la tavola scrive sul tratto d'acqua di questa tubazione (I-279): la
    `scritta` libera se c'e', altrimenti la sezione — il tubo —, senza la lunghezza."""
    if tubazione.scritta is not None and tubazione.scritta.strip():
        return tubazione.scritta.strip()
    if tubazione.lunghezza_m == 0:
        return None
    if tubazione.sezione is not None and tubazione.sezione.strip():
        return tubazione.sezione.strip()
    return None


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
    tubo: Tubo | None = None
    """Il tubo, se la scritta si legge come un tubo (I-279): la legenda lo spiega con la
    riga del suo materiale."""
    capi: frozenset[str] = frozenset()
    """I pezzi ai due capi del tratto d'acqua che la scritta nomina, quando e' quello del
    calcolo (`tratti`): per riconoscere il tratto fra due raccordi."""
    ripetuto: bool = False
    """Il tratto fra due raccordi con lo stesso tubo del vicino: la scritta cede
    (`segna_i_tratti_ripetuti`)."""
    macchine_ai_capi: frozenset[str] = frozenset()
    """I capi del tratto che non sono raccordi: le macchine (`detto_da_un_vicino`)."""


def scritte_dei_tratti(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunks: Sequence[Trunk] | None = None,
) -> tuple[ScrittaDelTratto, ...]:
    """Le scritte dei tratti di questo impianto, nell'ordine delle tratte del motore.

    Nessuna, se nessuna tubazione porta sezione, lunghezza o scritta: il conto delle
    tratte non si fa nemmeno, e le tavole di oggi restano quelle di ieri."""
    idrauliche = {item.id for item in project.networks if item.domain is Domain.HYDRONIC}
    d_acqua = {item.id for item in project.connections if item.network_id in idrauliche}
    libere = {item.id for item in project.connections if item.scritta is not None and item.scritta.strip()}
    sezioni = {item.id: item.sezione for item in project.connections}
    testi = {
        item.id: testo
        for item in project.connections
        if (
            testo := testo_della_tubazione_d_acqua(item)
            if item.id in d_acqua
            else testo_della_tubazione(item)
        )
        is not None
    }
    if not testi:
        return ()
    tutte = list(trunks) if trunks is not None else tratte_del_progetto(project, catalog)
    scritte: list[ScrittaDelTratto] = []

    # L'acqua: una scritta per tratto del calcolo, se e' la stessa su tutte le sue
    # tubazioni; niente sugli stacchi di servizio, salvo una scritta libera (I-279).
    catena_di: dict[str, TrattoDelDiametro] = {}
    if testi.keys() & d_acqua:
        for tratto in tratti_del_diametro(project, catalog, tutte):
            if all(rete in idrauliche for rete in tratto.reti):
                for item in tratto.connection_ids:
                    catena_di[item] = tratto
    fatte: set[int] = set()

    def del_tubo(tubazione: str) -> Tubo | None:
        # Solo sull'acqua: «Ø12,7 (1/2")» di una linea del gas refrigerante non e' un tubo
        # d'acciaio da mezzo pollice.
        if tubazione in libere or tubazione not in d_acqua:
            return None
        return tubo_dal_testo(sezioni.get(tubazione))

    for tratta in tutte:
        primo = next(iter(tratta.connection_ids), None)
        catena = catena_di.get(primo) if primo is not None else None
        if catena is not None:
            if id(catena) in fatte:
                continue
            fatte.add(id(catena))
            nella_catena = sorted(item for item in catena.connection_ids if item in testi)
            if not nella_catena:
                continue
            if len({testi[item] for item in nella_catena}) == 1:
                scritte.append(
                    ScrittaDelTratto(
                        scritta=testi[nella_catena[0]],
                        connection_ids=frozenset(catena.connection_ids),
                        tubazione=nella_catena[0],
                        tubo=del_tubo(nella_catena[0]),
                        capi=frozenset(ref.component_id for ref in catena.capi),
                    )
                )
                continue
            # Tubi diversi nello stesso tratto: ciascuna tratta del motore la sua.
            for chiave in catena.chiavi:
                scritte.extend(_della_tratta(chiave, testi, del_tubo, uguali_in_una=True))
            continue
        if primo in d_acqua:
            # Uno stacco di servizio (o una tratta senza acqua che scorre): solo la
            # scritta libera del progettista.
            solo_libere = {chi: testo for chi, testo in testi.items() if chi in libere}
            scritte.extend(_della_tratta(tratta.connection_ids, solo_libere, del_tubo, uguali_in_una=True))
            continue
        scritte.extend(_della_tratta(tratta.connection_ids, testi, del_tubo))
    return tuple(scritte)


def _della_tratta(
    connessioni: Sequence[str],
    testi: dict[str, str],
    del_tubo: Callable[[str], Tubo | None],
    uguali_in_una: bool = False,
) -> list[ScrittaDelTratto]:
    """Le scritte di una tratta del motore: una, se una sola tubazione porta il dato —
    o, per l'acqua (`uguali_in_una`), se tutte portano lo stesso —; altrimenti una per
    tubazione, come i due cavi del quadro e del sezionatore."""
    con_dato = [item for item in connessioni if item in testi]
    if not con_dato:
        return []
    if len(con_dato) == 1 or (uguali_in_una and len({testi[item] for item in con_dato}) == 1):
        return [
            ScrittaDelTratto(
                scritta=testi[con_dato[0]],
                connection_ids=frozenset(connessioni),
                tubazione=con_dato[0],
                tubo=del_tubo(con_dato[0]),
            )
        ]
    return [
        ScrittaDelTratto(
            scritta=testi[tubazione],
            connection_ids=frozenset({tubazione}),
            tubazione=tubazione,
            tubo=del_tubo(tubazione),
        )
        for tubazione in con_dato
    ]


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
    return segna_i_tratti_ripetuti(project, catalog, scritte, calcolati)


def _capi(item: ScrittaDelTratto | TrattoDelDiametro) -> frozenset[str]:
    if isinstance(item, ScrittaDelTratto):
        return item.capi
    return frozenset(ref.component_id for ref in item.capi)


def detto_da_un_vicino(
    item: ScrittaDelTratto | TrattoDelDiametro,
    scritti: Iterable[ScrittaDelTratto | TrattoDelDiametro],
    lato: Callable[[ScrittaDelTratto | TrattoDelDiametro], bool | None],
) -> bool:
    """Vero se uno dei tratti `scritti` — quelli che sulla tavola hanno gia' la scritta —
    tocca questo in un capo, sta **dalla stessa parte** — mandata o ritorno, `lato` — e
    porta **lo stesso tubo** (I-279): la linea continua attraverso una macchina — un
    volano in serie sul ritorno —, e la scritta del vicino lo dice. Attraverso un raccordo
    no: ai due lati di un T possono correre due rami paralleli, e ciascuno ha la sua (il
    tratto fra due raccordi e' `segna_i_tratti_ripetuti`). Allora questo, se accanto alla linea non c'e'
    posto, non va su un'etichetta staccata e il preflight tace: e' il pezzetto fra un T e
    una valvola dove la scritta del tubo non entra, e dove il progettista la cancellava a
    mano. La mandata e il ritorno di una macchina no: sono due linee, e ciascuna ha la
    sua scritta (D-193, punto 6). Solo per l'acqua: i cavi non hanno i capi del calcolo."""
    capi = item.macchine_ai_capi
    suo = lato(item)
    if not capi or suo is None:
        return False
    return any(
        altro is not item
        and altro.scritta == item.scritta
        and altro.macchine_ai_capi & capi
        and lato(altro) is suo
        for altro in scritti
    )


def segna_i_tratti_ripetuti(
    project: ProjectModel,
    catalog: ComponentRegistry,
    scritte: Sequence[ScrittaDelTratto],
    calcolati: Sequence[TrattoDelDiametro],
) -> tuple[tuple[ScrittaDelTratto, ...], tuple[TrattoDelDiametro, ...]]:
    """Segna `ripetuto` sui tratti d'acqua **fra due raccordi** — dove la portata cambia
    ai due capi: il pezzo fra due T di derivazione — che portano **lo stesso tubo** di un
    tratto accanto che non lo e' (I-279). Il tubo continua, e la scritta del vicino lo
    dice: la loro scritta **cede**. Il posatore la scrive solo su un rettilineo lungo, in
    linea, mai staccata (`layout.diametri.LUNGHEZZA_DEL_RIPETUTO_MM`), e se non la scrive
    il preflight tace: sul pezzetto di pochi millimetri fra due T non entrava, e il
    progettista la cancellava a mano per non fermare la tavola. Un tubo diverso si scrive
    sempre."""
    raccordi = {
        item.id
        for item in project.components
        if catalog.contains(item.definition_id) and catalog.get(item.definition_id).is_a_fitting
    }
    tutti: list[ScrittaDelTratto | TrattoDelDiametro] = [*scritte, *calcolati]

    def fra_due_raccordi(item: ScrittaDelTratto | TrattoDelDiametro) -> bool:
        capi = _capi(item)
        return len(capi) == 2 and capi <= raccordi

    via: set[int] = set()
    for item in tutti:
        if not fra_due_raccordi(item):
            continue
        capi = _capi(item)
        if any(
            altro is not item
            and not fra_due_raccordi(altro)
            and altro.scritta == item.scritta
            and _capi(altro) & capi
            for altro in tutti
        ):
            via.add(id(item))
    return (
        tuple(
            replace(item, ripetuto=id(item) in via, macchine_ai_capi=_capi(item) - raccordi) for item in scritte
        ),
        tuple(
            replace(item, ripetuto=id(item) in via, macchine_ai_capi=_capi(item) - raccordi) for item in calcolati
        ),
    )


__all__ = [
    "CAMPIONE_DELLA_LEGENDA",
    "TESTO_DELLA_LEGENDA",
    "ScrittaDelTratto",
    "detto_da_un_vicino",
    "numero_italiano",
    "scritte_dei_tratti",
    "segna_i_tratti_ripetuti",
    "testo_della_tubazione",
    "testo_della_tubazione_d_acqua",
    "tratti_da_scrivere",
]
