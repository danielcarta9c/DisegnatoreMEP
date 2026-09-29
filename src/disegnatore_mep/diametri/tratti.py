"""Il tratto che porta un DN (REL-007): da dove a dove, e quale DN.

**Il tratto del PO non e' la linea fra due pezzi disegnati** (I-143, I-153):
«serve un solo tag per ogni tratto, anche se ci sono valvole in mezzo o valvole
a tre vie». Qui un tratto e' una successione di tratte che **si attraversano**:

- gli **organi in linea** — valvole, filtri, circolatori, ritegni — stanno gia'
  dentro una tratta del motore (`layout.trunks`), e non la spezzano;
- un **raccordo di servizio** — il T da cui pende una sicurezza, un vaso, un
  manometro — ha due sole tratte d'acqua, e la portata non cambia: si attraversa;
- una **valvola a tre vie** — deviatrice, commutatrice, miscelatrice — si
  attraversa sulla via dritta, dall'attacco alla faccia opposta, e il terzo
  attacco comincia un tratto suo.

**Il tratto si ferma dove la portata cambia** (I-153, D-193 punto 7): sul
raccordo che unisce o divide due linee d'acqua — con piu' generatori in
parallelo, «uno per tratta fino al raccordo e uno dopo il raccordo» — e sulle
macchine.

**Quale tratto porta il DN** (D-193, punto 8): solo se il progettista ha chiesto
i diametri e sulla rete che ha detto, e solo se la portata viene dai suoi dati
(`portate.py`). Ogni tratto che porta il DN porta **un'etichetta sola**, e chi la
posa e' `layout.diametri`.
"""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import PortRef, ProjectModel

from .calcolatore import Diametro, diametro_per, potenza_da_portata
from .portate import (
    FUNZIONI_DI_MISCELAZIONE,
    TOLLERANZA_M3H,
    Portate,
    portate_delle_tratte,
)

TrunkKey = tuple[str, ...]

_OPPOSTA: dict[PortFace, PortFace] = {
    PortFace.LEFT: PortFace.RIGHT,
    PortFace.RIGHT: PortFace.LEFT,
    PortFace.TOP: PortFace.BOTTOM,
    PortFace.BOTTOM: PortFace.TOP,
}


@dataclass(frozen=True)
class TrattoDelDiametro:
    """Un tratto a portata costante, con il suo DN se i dati lo danno."""

    chiavi: tuple[TrunkKey, ...]
    """Le tratte del motore che il tratto attraversa, nell'ordine in cui si
    susseguono."""
    reti: tuple[str, ...]
    capi: tuple[PortRef, PortRef]
    """Dove comincia e dove finisce: l'attacco di una macchina o di un raccordo."""
    portata_m3h: float | None
    fonti: tuple[str, ...]
    diametro: Diametro | None
    richiesto: bool
    """Il progettista ha chiesto i diametri su questa rete (D-193, punto 8)."""
    potenza_kw: float | None = None
    """La potenza che la portata porta, quando viene tutta da potenze date con lo
    stesso salto termico: per il foglio dei calcoli, che il PO controlla."""
    salto_termico_k: float | None = None
    perche_senza_dn: str | None = None
    """Perche' il tratto non porta il DN, detto per il foglio dei calcoli."""
    strada_principale: bool = True
    """Il tratto corre su un'autostrada del motore — dai generatori agli accumuli,
    agli scambiatori e ai collettori, e fra loro. Gli altri sono le «strade
    secondarie» del PO (I-161): acque fredde in ingresso, bipassi, rami alle
    utenze. Il loro DN si sacrifica quando accanto alla linea non c'e' posto; quello
    di una strada principale, come ultima spiaggia, va su un'etichetta staccata
    con freccia (I-162)."""

    @property
    def connection_ids(self) -> frozenset[str]:
        return frozenset(item for chiave in self.chiavi for item in chiave)

    @property
    def porta_il_dn(self) -> bool:
        return self.richiesto and self.diametro is not None

    @property
    def scritta(self) -> str | None:
        return None if self.diametro is None else self.diametro.scritta


def _via_dritta(
    definizione: ComponentDefinition, catalog: ComponentRegistry, attacchi: Sequence[str]
) -> frozenset[str] | None:
    """La via dritta di una valvola a tre vie: i due attacchi su facce opposte.

    La dice il simbolo, non il nome: ruotare il simbolo ruota tutt'e due le
    facce, e la relazione resta (`layout.highways`). `None` se non c'e' una
    coppia sola cosi'."""
    manifesto = catalog.resolve(definizione.id).symbol.manifest
    facce = {pid: manifesto.port(pid).face for pid in attacchi}
    coppie = [
        frozenset({primo, secondo})
        for indice, primo in enumerate(sorted(attacchi))
        for secondo in sorted(attacchi)[indice + 1 :]
        if _OPPOSTA.get(facce[primo]) is facce[secondo]
    ]
    return coppie[0] if len(coppie) == 1 else None


def _passaggi(
    project: ProjectModel,
    catalog: ComponentRegistry,
    tratte: Sequence[Trunk],
) -> dict[int, list[int]]:
    """Quali tratte d'acqua si attraversano l'una nell'altra, e dove."""
    definizioni = {item.id: catalog.get(item.definition_id) for item in project.components}
    alla_porta: dict[tuple[str, str], int] = {}
    per_pezzo: dict[str, list[str]] = defaultdict(list)
    for indice, tratta in enumerate(tratte):
        for ref in (tratta.start, tratta.end):
            alla_porta[(ref.component_id, ref.port_id)] = indice
            per_pezzo[ref.component_id].append(ref.port_id)

    legami: dict[int, list[int]] = defaultdict(list)

    def lega(primo: int, secondo: int) -> None:
        if primo != secondo:
            legami[primo].append(secondo)
            legami[secondo].append(primo)

    for component_id in sorted(per_pezzo):
        definizione = definizioni[component_id]
        attacchi = sorted(
            pid
            for pid in per_pezzo[component_id]
            if not next(p for p in definizione.ports if p.id == pid).off_the_run
        )
        commuta = bool(definizione.hydraulic_states) or bool(
            frozenset(definizione.functions) & FUNZIONI_DI_MISCELAZIONE
        )
        if definizione.is_a_fitting and not commuta:
            # Un raccordo con due sole tratte d'acqua: la portata non cambia.
            if len(attacchi) == 2:
                lega(alla_porta[(component_id, attacchi[0])], alla_porta[(component_id, attacchi[1])])
            continue
        if commuta:
            dritta = _via_dritta(definizione, catalog, attacchi)
            if dritta is not None and all((component_id, pid) in alla_porta for pid in dritta):
                primo, secondo = sorted(dritta)
                lega(alla_porta[(component_id, primo)], alla_porta[(component_id, secondo)])
    return legami


def _catene(numero: int, legami: dict[int, list[int]]) -> list[list[int]]:
    """Le catene di tratte legate, dall'uno all'altro capo, nell'ordine delle tratte."""
    viste: set[int] = set()
    catene: list[list[int]] = []
    capi = [indice for indice in range(numero) if len(legami.get(indice, [])) < 2]
    for inizio in [*capi, *range(numero)]:
        if inizio in viste:
            continue
        catena = [inizio]
        viste.add(inizio)
        precedente, corrente = None, inizio
        while True:
            avanti = [item for item in legami.get(corrente, []) if item != precedente and item not in viste]
            if not avanti:
                break
            precedente, corrente = corrente, min(avanti)
            catena.append(corrente)
            viste.add(corrente)
        catene.append(catena)
    return sorted(catene, key=min)


def _capi_della_catena(catena: list[int], tratte: Sequence[Trunk]) -> tuple[PortRef, PortRef]:
    """I due attacchi da cui la catena entra ed esce: quelli che non stanno su un
    pezzo attraversato da un'altra tratta della stessa catena."""
    if len(catena) == 1:
        return tratte[catena[0]].start, tratte[catena[0]].end
    pezzi_di: dict[str, int] = defaultdict(int)
    for indice in catena:
        for ref in (tratte[indice].start, tratte[indice].end):
            pezzi_di[ref.component_id] += 1
    liberi = [
        ref
        for indice in catena
        for ref in (tratte[indice].start, tratte[indice].end)
        if pezzi_di[ref.component_id] == 1
    ]
    if len(liberi) >= 2:
        return liberi[0], liberi[-1]
    return tratte[catena[0]].start, tratte[catena[-1]].end


def tratti_del_diametro(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunks: Sequence[Trunk] | None = None,
    portate: Portate | None = None,
) -> tuple[TrattoDelDiametro, ...]:
    """Tutti i tratti d'acqua dell'impianto, ciascuno con la sua portata e il suo DN.

    Anche quelli che il DN non lo portano — una rete non chiesta, una portata che
    i dati non danno —, perche' il foglio dei calcoli dica di ciascuno perche'."""
    tutte = list(trunks) if trunks is not None else tratte_del_progetto(project, catalog)
    if portate is None:
        portate = portate_delle_tratte(project, catalog, tutte)
    tratte = [item for item in tutte if item.connection_ids in portate.tratte]
    richieste = frozenset(project.diametri.reti) if project.diametri is not None else frozenset()
    esistenti = frozenset(item.id for item in project.networks if item.esistente)
    legami = _passaggi(project, catalog, tratte)
    livelli = hierarchy_of(project, catalog, tutte)

    tratti: list[TrattoDelDiametro] = []
    for catena in _catene(len(tratte), legami):
        chiavi = tuple(tratte[indice].connection_ids for indice in catena)
        reti = tuple(dict.fromkeys(tratte[indice].network_id for indice in catena))
        valori = [portate.tratte[chiave] for chiave in chiavi]
        noti = [item.portata_m3h for item in valori if item.portata_m3h is not None]
        portata = max(noti) if len(noti) == len(valori) and noti else None
        fonti: tuple[str, ...] = ()
        if portata is not None:
            migliore = max(valori, key=lambda item: item.portata_m3h or 0.0)
            fonti = migliore.fonti
        richiesto = bool(richieste) and all(rete in richieste for rete in reti)
        diametro = diametro_per(portata) if portata is not None and portata > TOLLERANZA_M3H else None
        perche: str | None = None
        if any(rete in esistenti for rete in reti):
            perche = "rete esistente"
        elif not richiesto:
            perche = "diametri non chiesti su questa rete"
        elif portata is None:
            perche = "la portata non viene dai dati del progettista"
        elif portata <= TOLLERANZA_M3H:
            perche = "portata nulla"
        elif diametro is None:
            perche = "oltre DN 300"

        potenza: float | None = None
        salto: float | None = None
        if portata is not None and fonti:
            dati = [portate.dati.get(item) for item in fonti]
            salti = {dato.salto_termico_k for dato in dati if dato is not None}
            if (
                all(dato is not None and dato.potenza_kw is not None for dato in dati)
                and len(salti) == 1
            ):
                (salto,) = salti
                if salto is not None:
                    potenza = potenza_da_portata(portata, salto)

        tratti.append(
            TrattoDelDiametro(
                chiavi=chiavi,
                reti=reti,
                capi=_capi_della_catena(catena, tratte),
                portata_m3h=portata,
                fonti=fonti,
                diametro=diametro,
                richiesto=richiesto,
                potenza_kw=potenza,
                salto_termico_k=salto,
                perche_senza_dn=perche,
                strada_principale=any(
                    livelli.get(tratte[indice].connection_ids) is Level.AUTOSTRADA for indice in catena
                ),
            )
        )
    return tuple(tratti)


def tratti_da_etichettare(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunks: Sequence[Trunk] | None = None,
) -> tuple[TrattoDelDiametro, ...]:
    """I tratti che portano il DN sulla tavola: chiesti, e con la portata dai dati.

    Senza richiesta del progettista non ce n'e' nessuno (D-193, punto 8), e il
    conto non si fa nemmeno."""
    if project.diametri is None:
        return ()
    return tuple(
        item for item in tratti_del_diametro(project, catalog, trunks) if item.porta_il_dn
    )


__all__ = [
    "TrattoDelDiametro",
    "tratti_da_etichettare",
    "tratti_del_diametro",
]
