"""La portata di ogni tratta (REL-007): dai dati del progettista, per conservazione.

Il PO (I-142, D-191): «un tratto porta la potenza di cio' che alimenta — il
generatore, il collettore la somma dei generatori, un circuito la sua utenza».
Questo modulo lo fa **con le portate**, perche' le reti sanitarie e il solare la
potenza non la danno (I-157, D-193 punto 4), e la conservazione e' la stessa: in
ogni nodo, quanto entra esce.

**Da dove vengono i numeri — e da nessun'altra parte** (D-087):

- un **generatore** o un'**utenza** porta la portata del proprio circuito: quella
  che il progettista ha scritto (`flow_rate_m3h`), oppure potenza e salto termico
  (`power_kw`, `delta_t_k`) quando il fluido e' acqua di riscaldamento o
  refrigerata — il solare e il sanitario solo dalla portata (D-193, punto 4);
- un **circolatore** con la sua portata la da' alla tratta su cui sta;
- un **confine di rete** — l'acquedotto, le utenze sanitarie, il ricircolo — con
  la portata di progetto la da' alla tratta che lo raggiunge.

**Come si propaga.** Ogni tratta porta una portata, col verso che gli attacchi
del catalogo dichiarano (entrata o uscita). Nei nodi vale la conservazione: un
raccordo somma o divide; un collettore di zona ripartisce; un generatore,
un'utenza, un serpentino, il primario di uno scambiatore, un volano a due
attacchi sono **attraversati** — la portata che entra e' quella che esce. Il
**volume** di un accumulo invece no: primario e secondario di un volano hanno
ciascuno la propria pompa, e l'accumulo assorbe la differenza. Non si scrive
niente che la conservazione non costringa.

**Le valvole a tre vie si provano in ogni posizione.** Una deviatrice manda
tutto su un ramo o sull'altro, una commutatrice riceve da uno o dall'altro, una
miscelatrice nelle due posizioni estreme prende tutto dalla mandata o tutto dal
bipasso: il catalogo dichiara gli stati delle prime due, e per le miscelatrici
questo modulo prova ciascun ingresso da solo. Le combinazioni che i dati non
reggono — l'acqua della caldaia mandata allo scambiatore e ripresa dal
collettore — si scartano; di quelle che reggono, **ogni tratta prende la
portata piu' grande**, che e' quella su cui si dimensiona.

**Dove i dati non bastano, la tratta resta senza portata**, e il DN non compare:
non si interpola, non si divide a occhio fra due rami in parallelo.
"""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import product

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.layout.flow import (
    BOUNDARY_FUNCTION,
    GENERATOR_FUNCTIONS,
    TERMINAL_FUNCTIONS,
)
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of, is_a_machine
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PortFlow

from .calcolatore import portata_da_potenza

TrunkKey = tuple[str, ...]
Attacco = tuple[str, str]

MEDI_DALLA_POTENZA = frozenset({"heating_water", "chilled_water"})
"""I fluidi di cui la portata si ricava da potenza e salto termico (D-193, punto 4).

Le costanti del calcolatore sono quelle dell'acqua: per il fluido solare, che e'
una miscela antigelo, e per le reti sanitarie, che si dimensionano sulle utenze,
la portata la da' il progettista (I-157)."""

FUNZIONI_DI_MISCELAZIONE = frozenset({"circuit_mixing", "dhw_mixing"})
"""Le miscelatrici: il catalogo non ne dichiara gli stati, e qui si provano le due
posizioni estreme — tutto da un ingresso, tutto dall'altro."""

FUNZIONE_DI_DISTRIBUZIONE = "distribution"
"""Il collettore di zona: quanto entra si ripartisce fra le uscite."""

FUNZIONE_DI_CIRCOLAZIONE = "circulation"
"""Il circolatore: in linea su una tratta, ne porta la portata se il progettista
l'ha data."""

TOLLERANZA_M3H = 1e-6
"""Quanto due portate possono differire ed essere la stessa: un millesimo di
litro all'ora. E' la tolleranza dei conti in virgola mobile, non una soglia."""

MASSIMO_DI_CONFIGURAZIONI = 4096
"""Quante combinazioni di posizioni delle tre vie si provano, al piu', in un
circuito. Nei sei impianti di prova sono al piu' quattro: il tetto c'e' perche' un
conto che cresce col prodotto delle valvole non deve poter bloccare la tavola;
oltre, le tratte di quel circuito restano senza portata e lo si dice."""


@dataclass(frozen=True)
class DatoDiPortata:
    """Il dato del progettista da cui un pezzo da' la sua portata."""

    component_id: str
    portata_m3h: float
    potenza_kw: float | None = None
    salto_termico_k: float | None = None
    """Potenza e salto termico, quando la portata viene da li'; `None` quando il
    progettista ha dato la portata."""


@dataclass(frozen=True)
class PortataDellaTratta:
    """La portata di una tratta, e i pezzi i cui dati l'hanno determinata."""

    chiave: TrunkKey
    portata_m3h: float | None
    """La piu' grande fra le configurazioni coerenti delle tre vie; `None` quando
    in almeno una i dati non la determinano."""
    fonti: tuple[str, ...] = ()
    """I pezzi con un dato che entra nel conto, nella configurazione che da' la
    portata piu' grande: in ordine di identificativo."""


@dataclass(frozen=True)
class Portate:
    """Le portate di tutte le tratte che portano acqua, e che cosa le ha date."""

    tratte: dict[TrunkKey, PortataDellaTratta]
    dati: dict[str, DatoDiPortata]
    discordanze: tuple[str, ...]
    """I punti in cui i dati del progettista non tornano fra loro: si scrivono
    nel foglio dei calcoli, e il conto prende la portata piu' grande."""


@dataclass(frozen=True)
class _Scelta:
    """Una posizione di un pezzo: i gruppi di attacchi che comunicano, e quelli
    chiusi."""

    gruppi: tuple[frozenset[str], ...]
    chiusi: frozenset[str]


def _attacchi_del_percorso(definizione: ComponentDefinition) -> list[str]:
    return [porta.id for porta in definizione.ports if not porta.off_the_run]


def _verso(definizione: ComponentDefinition, port_id: str) -> int:
    """+1 se da questo attacco il fluido entra nel pezzo, -1 se ne esce, 0 se il
    catalogo non lo dice."""
    for porta in definizione.ports:
        if porta.id == port_id:
            if porta.flow is PortFlow.IN:
                return 1
            if porta.flow is PortFlow.OUT:
                return -1
            return 0
    return 0


def _attraversati(definizione: ComponentDefinition) -> tuple[frozenset[str], ...]:
    """Le coppie di attacchi che un pezzo attraversa: entra da uno, esce dall'altro.

    Per fluido: una coppia con un'entrata e un'uscita dello stesso fluido. Il
    fluido che il pezzo **tiene in serbo** non si attraversa — il volume di un
    accumulo assorbe la differenza fra il primario e il secondario —, tranne
    quando il pezzo ha due attacchi soli, come il volano sul ritorno."""
    percorso = [porta for porta in definizione.ports if not porta.off_the_run]
    per_fluido: dict[str, list[tuple[str, PortFlow]]] = defaultdict(list)
    for porta in percorso:
        per_fluido[porta.medium].append((porta.id, porta.flow))
    coppie: list[frozenset[str]] = []
    for fluido, porte in sorted(per_fluido.items()):
        entrate = [pid for pid, flusso in porte if flusso is PortFlow.IN]
        uscite = [pid for pid, flusso in porte if flusso is PortFlow.OUT]
        if len(entrate) != 1 or len(uscite) != 1 or len(porte) != 2:
            continue
        if (
            definizione.stored_medium is not None
            and fluido == definizione.stored_medium
            and len(percorso) != 2
        ):
            continue
        coppie.append(frozenset({entrate[0], uscite[0]}))
    return tuple(coppie)


def _scelte(definizione: ComponentDefinition) -> tuple[_Scelta, ...]:
    """Le posizioni in cui un pezzo si prova. Una sola per chi non commuta."""
    percorso = _attacchi_del_percorso(definizione)
    if definizione.hydraulic_states:
        scelte = []
        for stato in definizione.hydraulic_states:
            gruppi = tuple(frozenset(gruppo) for gruppo in stato.groups)
            nominati = frozenset(item for gruppo in gruppi for item in gruppo)
            scelte.append(_Scelta(gruppi=gruppi, chiusi=frozenset(percorso) - nominati))
        return tuple(scelte)
    funzioni = frozenset(definizione.functions)
    if funzioni & FUNZIONI_DI_MISCELAZIONE:
        uscite = [pid for pid in percorso if _verso(definizione, pid) < 0]
        entrate = [pid for pid in percorso if _verso(definizione, pid) > 0]
        if len(uscite) == 1 and len(entrate) >= 2:
            return tuple(
                _Scelta(
                    gruppi=(frozenset({entrata, uscite[0]}),),
                    chiusi=frozenset(entrate) - {entrata},
                )
                for entrata in sorted(entrate)
            )
    if definizione.is_a_fitting or FUNZIONE_DI_DISTRIBUZIONE in funzioni:
        return (_Scelta(gruppi=(frozenset(percorso),), chiusi=frozenset()),)
    if is_a_machine(definizione):
        return (_Scelta(gruppi=_attraversati(definizione), chiusi=frozenset()),)
    return (_Scelta(gruppi=(), chiusi=frozenset()),)


def _numero(valore: object) -> float | None:
    if isinstance(valore, bool) or not isinstance(valore, int | float) or valore <= 0:
        return None
    return float(valore)


def dato_di_portata(
    component_id: str,
    proprieta: dict[str, object],
    fluido: str | None,
) -> DatoDiPortata | None:
    """La portata che il progettista ha dato per un pezzo, se l'ha data.

    Prima la portata scritta, poi — solo per l'acqua di riscaldamento e
    refrigerata — potenza e salto termico (D-193, punto 4)."""
    portata = _numero(proprieta.get("flow_rate_m3h"))
    if portata is not None:
        return DatoDiPortata(component_id=component_id, portata_m3h=portata)
    potenza = _numero(proprieta.get("power_kw"))
    salto = _numero(proprieta.get("delta_t_k"))
    if potenza is not None and salto is not None and fluido in MEDI_DALLA_POTENZA:
        return DatoDiPortata(
            component_id=component_id,
            portata_m3h=portata_da_potenza(potenza, salto),
            potenza_kw=potenza,
            salto_termico_k=salto,
        )
    return None


class _Radici:
    """Unione di insiemi, per sapere quali tratte si parlano attraverso i nodi."""

    def __init__(self, quanti: int) -> None:
        self.padre = list(range(quanti))

    def radice(self, indice: int) -> int:
        while self.padre[indice] != indice:
            self.padre[indice] = self.padre[self.padre[indice]]
            indice = self.padre[indice]
        return indice

    def unisci(self, primo: int, secondo: int) -> None:
        a, b = self.radice(primo), self.radice(secondo)
        if a != b:
            self.padre[max(a, b)] = min(a, b)


def tratte_che_portano_acqua(
    project: ProjectModel, catalog: ComponentRegistry, trunks: Sequence[Trunk]
) -> list[Trunk]:
    """Le tratte in cui scorre acqua: tutte, tranne i rami di servizio.

    Uno stacco che finisce su una sicurezza, un vaso, un manometro, un gruppo di
    riempimento o uno scarico non porta portata in esercizio, e non porta il DN
    (D-193, punto 7): e' la gerarchia del motore a riconoscerlo
    (`hierarchy.Level.SERVIZIO`: da un lato non c'e' nessuna macchina)."""
    livelli = hierarchy_of(project, catalog, list(trunks))
    return [item for item in trunks if livelli[item.connection_ids] is not Level.SERVIZIO]


def portate_delle_tratte(
    project: ProjectModel, catalog: ComponentRegistry, trunks: Sequence[Trunk]
) -> Portate:
    """La portata di ogni tratta che porta acqua, dai soli dati del progettista.

    Deterministico: le tratte, i pezzi e le loro posizioni si percorrono sempre
    nello stesso ordine."""
    tratte = tratte_che_portano_acqua(project, catalog, trunks)
    definizioni = {item.id: catalog.get(item.definition_id) for item in project.components}
    pezzi = {item.id: item for item in project.components}

    alla_porta: dict[Attacco, int] = {}
    for indice, tratta in enumerate(tratte):
        for ref in (tratta.start, tratta.end):
            alla_porta[(ref.component_id, ref.port_id)] = indice

    # I dati del progettista.
    dati: dict[str, DatoDiPortata] = {}
    fissi: dict[int, list[tuple[float, str]]] = defaultdict(list)
    for indice, tratta in enumerate(tratte):
        for component_id in tratta.inline_component_ids:
            definizione = definizioni[component_id]
            if FUNZIONE_DI_CIRCOLAZIONE not in definizione.functions:
                continue
            fluido = definizione.ports[0].medium if definizione.ports else None
            dato = dato_di_portata(component_id, dict(pezzi[component_id].properties), fluido)
            if dato is not None and dato.potenza_kw is None:
                dati[component_id] = dato
                fissi[indice].append((dato.portata_m3h, component_id))
    for component_id in sorted(definizioni):
        definizione = definizioni[component_id]
        funzioni = frozenset(definizione.functions)
        percorso = _attacchi_del_percorso(definizione)
        if BOUNDARY_FUNCTION in funzioni and len(percorso) == 1:
            fluido = next(p.medium for p in definizione.ports if p.id == percorso[0])
            al_confine = alla_porta.get((component_id, percorso[0]))
            dato = dato_di_portata(component_id, dict(pezzi[component_id].properties), fluido)
            if al_confine is not None and dato is not None and dato.potenza_kw is None:
                dati[component_id] = dato
                fissi[al_confine].append((dato.portata_m3h, component_id))
            continue
        if not funzioni & (GENERATOR_FUNCTIONS | TERMINAL_FUNCTIONS) or not is_a_machine(definizione):
            continue
        coppie = _attraversati(definizione)
        if len(coppie) != 1:
            continue
        (coppia,) = coppie
        fluido = next(p.medium for p in definizione.ports if p.id in coppia)
        dato = dato_di_portata(component_id, dict(pezzi[component_id].properties), fluido)
        if dato is None:
            continue
        dati[component_id] = dato
        for port_id in sorted(coppia):
            alla_macchina = alla_porta.get((component_id, port_id))
            if alla_macchina is not None:
                fissi[alla_macchina].append((dato.portata_m3h, component_id))

    discordanze: list[str] = []
    for indice in sorted(fissi):
        diversi = sorted({round(valore, 9) for valore, _ in fissi[indice]})
        if len(diversi) > 1 and diversi[-1] - diversi[0] > TOLLERANZA_M3H:
            chi = ", ".join(sorted({component_id for _, component_id in fissi[indice]}))
            discordanze.append(
                f"{chi}: portate diverse sulla stessa tratta "
                f"({' / '.join(f'{v:.3f}' for v in diversi)} m³/h) — si prende la piu' grande"
            )

    # Chi commuta, e chi si attraversa: le posizioni di ogni pezzo.
    scelte: dict[str, tuple[_Scelta, ...]] = {}
    for component_id in sorted(definizioni):
        tocca = any((component_id, pid) in alla_porta for pid in _attacchi_del_percorso(definizioni[component_id]))
        if tocca:
            scelte[component_id] = _scelte(definizioni[component_id])

    radici = _Radici(len(tratte))
    for component_id, posizioni in scelte.items():
        for scelta in posizioni:
            for gruppo in scelta.gruppi:
                dentro = sorted(
                    alla_porta[(component_id, pid)] for pid in gruppo if (component_id, pid) in alla_porta
                )
                for altro in dentro[1:]:
                    radici.unisci(dentro[0], altro)

    circuiti: dict[int, list[int]] = defaultdict(list)
    for indice in range(len(tratte)):
        circuiti[radici.radice(indice)].append(indice)

    esito: dict[TrunkKey, PortataDellaTratta] = {}
    for radice in sorted(circuiti):
        membri = circuiti[radice]
        insieme = set(membri)
        coinvolti = sorted(
            component_id
            for component_id, posizioni in scelte.items()
            if any(
                (component_id, pid) in alla_porta and alla_porta[(component_id, pid)] in insieme
                for scelta in posizioni
                for gruppo in scelta.gruppi
                for pid in gruppo
            )
            or any(
                (component_id, pid) in alla_porta and alla_porta[(component_id, pid)] in insieme
                for scelta in posizioni
                for pid in scelta.chiusi
            )
        )
        commutano = [component_id for component_id in coinvolti if len(scelte[component_id]) > 1]
        combinazioni = 1
        for component_id in commutano:
            combinazioni *= len(scelte[component_id])
        risultati: list[tuple[dict[int, float], dict[int, frozenset[str]]]] = []
        if combinazioni <= MASSIMO_DI_CONFIGURAZIONI:
            for posizione in product(*(range(len(scelte[c])) for c in commutano)):
                scelta_di = dict(zip(commutano, posizione, strict=True))
                risultato = _prova(
                    membri,
                    coinvolti,
                    scelte,
                    scelta_di,
                    alla_porta,
                    definizioni,
                    fissi,
                    discordanze,
                )
                if risultato is not None:
                    risultati.append(risultato)
        else:
            discordanze.append(
                f"circuito con {combinazioni} posizioni delle valvole a tre vie: troppe da "
                f"provare, le sue tratte restano senza portata"
            )
        if not risultati and combinazioni <= MASSIMO_DI_CONFIGURAZIONI:
            discordanze.append(
                "nessuna posizione delle valvole a tre vie tiene insieme i dati del circuito "
                f"che passa per {', '.join(coinvolti[:4])}: le sue tratte restano senza portata"
            )
        for indice in membri:
            chiave = tratte[indice].connection_ids
            if not risultati or any(indice not in valori for valori, _ in risultati):
                esito[chiave] = PortataDellaTratta(chiave=chiave, portata_m3h=None)
                continue
            migliore = max(range(len(risultati)), key=lambda posizione: risultati[posizione][0][indice])
            portate_della_prova, fonti_della_prova = risultati[migliore]
            esito[chiave] = PortataDellaTratta(
                chiave=chiave,
                portata_m3h=portate_della_prova[indice],
                fonti=tuple(sorted(fonti_della_prova[indice])),
            )

    return Portate(tratte=esito, dati=dati, discordanze=tuple(dict.fromkeys(discordanze)))


def _prova(
    membri: list[int],
    coinvolti: list[str],
    scelte: dict[str, tuple[_Scelta, ...]],
    scelta_di: dict[str, int],
    alla_porta: dict[Attacco, int],
    definizioni: dict[str, ComponentDefinition],
    fissi: dict[int, list[tuple[float, str]]],
    discordanze: list[str],
) -> tuple[dict[int, float], dict[int, frozenset[str]]] | None:
    """Una configurazione delle tre vie: le portate che i dati costringono, o
    `None` se la configurazione non regge."""
    insieme = set(membri)
    valori: dict[int, float] = {}
    fonti: dict[int, frozenset[str]] = {}
    for indice in membri:
        if fissi.get(indice):
            valori[indice] = max(valore for valore, _ in fissi[indice])
            fonti[indice] = frozenset(component_id for _, component_id in fissi[indice])

    nodi: list[list[tuple[int, int]]] = []
    for component_id in coinvolti:
        scelta = scelte[component_id][scelta_di.get(component_id, 0)]
        definizione = definizioni[component_id]
        for port_id in sorted(scelta.chiusi):
            chiusa = alla_porta.get((component_id, port_id))
            if chiusa is None or chiusa not in insieme:
                continue
            if valori.get(chiusa, 0.0) > TOLLERANZA_M3H:
                return None
            valori[chiusa] = 0.0
            fonti[chiusa] = frozenset()
        for gruppo in scelta.gruppi:
            nodo = [
                (alla_porta[(component_id, pid)], _verso(definizione, pid))
                for pid in sorted(gruppo)
                if (component_id, pid) in alla_porta and alla_porta[(component_id, pid)] in insieme
            ]
            if nodo and all(verso != 0 for _, verso in nodo):
                nodi.append(nodo)

    cambiato = True
    while cambiato:
        cambiato = False
        for nodo in nodi:
            ignote = [(indice, verso) for indice, verso in nodo if indice not in valori]
            note = [(indice, verso) for indice, verso in nodo if indice in valori]
            somma = sum(verso * valori[indice] for indice, verso in note)
            if len(ignote) == 1:
                indice, verso = ignote[0]
                portata = -somma / verso
                if portata < -TOLLERANZA_M3H:
                    return None
                valori[indice] = max(portata, 0.0)
                fonti[indice] = frozenset().union(*(fonti[i] for i, _ in note))
                cambiato = True
            elif not ignote:
                scala = max(1.0, *(valori[i] for i, _ in nodo))
                if abs(somma) > TOLLERANZA_M3H * scala:
                    # **Uno zero che nessun dato spiega viene da una valvola
                    # chiusa**, direttamente o attraverso una macchina: il nodo
                    # non torna perche' questa posizione delle tre vie non puo'
                    # esistere, e si scarta. Se invece ogni tratta del nodo
                    # porta un dato, sono i dati a non tornare.
                    if any(valori[i] <= TOLLERANZA_M3H and not fonti[i] for i, _ in nodo):
                        return None
                    nomi = ", ".join(sorted(set().union(*(fonti[i] for i, _ in nodo)))) or "dati"
                    discordanze.append(
                        f"{nomi}: le portate non tornano in un nodo ({abs(somma):.3f} m³/h "
                        f"di differenza) — si prende la piu' grande"
                    )
    return valori, fonti


def fonti_leggibili(fonti: Iterable[str], project: ProjectModel) -> str:
    """Le fonti di una portata come le legge chi guarda la tavola: le sigle."""
    sigle = {item.id: item.tag or item.id for item in project.components}
    return ", ".join(sigle.get(item, item) for item in fonti)


__all__ = [
    "DatoDiPortata",
    "MEDI_DALLA_POTENZA",
    "PortataDellaTratta",
    "Portate",
    "dato_di_portata",
    "fonti_leggibili",
    "portate_delle_tratte",
    "tratte_che_portano_acqua",
]
