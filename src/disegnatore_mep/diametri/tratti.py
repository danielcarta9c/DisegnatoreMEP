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

**Quale tratto porta il tubo** (D-193, punto 8): solo se il progettista ha chiesto
i diametri e sulla rete che ha detto, e solo se la portata viene dai suoi dati
(`portate.py`). Ogni tratto che lo porta porta **un'etichetta sola**, e chi la posa
e' `layout.diametri`.

**Il tubo e' quello da comprare** (I-279, `tubi.py`): il piu' piccolo del materiale
della rete — multistrato se il grafo non dice altro — in cui la velocita' reale non
supera la massima del suo pollice. **Solo la velocita'** (I-281): l'attacco della
macchina non e' un minimo, e dove il tubo e' piu' piccolo dell'attacco la skill lo dice
come riduzione (`costruttori.riduzioni_all_attacco`).

**Il tubo del progettista vince** (I-279): se una tubazione del tratto porta una
`sezione` che si legge come un tubo — «MS 32×3», «DN 25», «Cu 28×1» —, la tavola
scrive la sua e il calcolo non la tocca; se la velocita' ci supera la massima, la skill
lo dice (`avvisi_dei_tubi`), e non blocca.
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
from disegnatore_mep.model.types import Domain

from .calcolatore import potenza_da_portata
from .portate import (
    FUNZIONI_DI_MISCELAZIONE,
    TOLLERANZA_M3H,
    Portate,
    portate_delle_tratte,
)
from .tubi import (
    MATERIALE_PREDEFINITO,
    Materiale,
    Tubo,
    TuboScelto,
    ordine_del_pollice,
    tubo_dal_testo,
    tubo_per,
    ultimo_tubo,
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
    """Un tratto a portata costante, con il suo tubo se i dati lo danno."""

    chiavi: tuple[TrunkKey, ...]
    """Le tratte del motore che il tratto attraversa, nell'ordine in cui si
    susseguono."""
    reti: tuple[str, ...]
    capi: tuple[PortRef, PortRef]
    """Dove comincia e dove finisce: l'attacco di una macchina o di un raccordo."""
    portata_m3h: float | None
    fonti: tuple[str, ...]
    diametro: TuboScelto | None
    """Il tubo che il calcolo sceglie, nel materiale della rete (I-279)."""
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
    materiale: Materiale = MATERIALE_PREDEFINITO
    ripetuto: bool = False
    """Il tratto fra due raccordi con lo stesso tubo del vicino: la scritta cede
    (`scritte.segna_i_tratti_ripetuti`, I-279)."""
    macchine_ai_capi: frozenset[str] = frozenset()
    """I capi del tratto che non sono raccordi (`scritte.detto_da_un_vicino`, I-279)."""
    tubo_del_progettista: Tubo | None = None
    """Il tubo che il progettista ha scritto nella `sezione` di una tubazione del
    tratto, se si legge (`tubi.tubo_dal_testo`): vince sul calcolo (I-279)."""

    @property
    def connection_ids(self) -> frozenset[str]:
        return frozenset(item for chiave in self.chiavi for item in chiave)

    @property
    def porta_il_dn(self) -> bool:
        return self.richiesto and self.diametro is not None

    @property
    def scritta(self) -> str | None:
        return None if self.diametro is None else self.diametro.scritta

    @property
    def tubo(self) -> Tubo | None:
        """Il tubo che si posa su questo tratto: quello del progettista, se l'ha
        scritto; altrimenti quello del calcolo, dove il tratto lo porta."""
        if self.tubo_del_progettista is not None:
            return self.tubo_del_progettista
        return self.diametro.tubo if self.porta_il_dn and self.diametro is not None else None


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
    tubi_esistenti = frozenset(item.id for item in project.connections if item.esistente)
    legami = _passaggi(project, catalog, tratte)
    # Il tubo del progettista si legge solo sull'acqua (I-279): «Ø12,7 (1/2")» di una
    # linea del gas refrigerante non e' un tubo d'acciaio.
    idrauliche = {item.id for item in project.networks if item.domain is Domain.HYDRONIC}
    sezioni = {
        item.id: item.sezione for item in project.connections if item.sezione and item.network_id in idrauliche
    }
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
        materiale = materiale_della_rete(project, reti[0])
        diametro = (
            tubo_per(portata, materiale) if portata is not None and portata > TOLLERANZA_M3H else None
        )
        del_progettista = next(
            (
                tubo
                for chiave in chiavi
                for tubo_id in chiave
                if (tubo := tubo_dal_testo(sezioni.get(tubo_id))) is not None
            ),
            None,
        )
        perche: str | None = None
        if any(rete in esistenti for rete in reti):
            perche = "rete esistente"
        elif any(tubo in tubi_esistenti for chiave in chiavi for tubo in chiave):
            perche = "tratto esistente"
        elif not richiesto:
            perche = "diametri non chiesti su questa rete"
        elif portata is None:
            perche = "la portata non viene dai dati del progettista"
        elif portata <= TOLLERANZA_M3H:
            perche = "portata nulla"
        elif diametro is None:
            perche = f"oltre {ultimo_tubo(materiale).scritta}, l'ultimo tubo della tabella del {materiale}"

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
                materiale=materiale,
                tubo_del_progettista=del_progettista,
            )
        )
    return tuple(tratti)


def materiale_della_rete(project: ProjectModel, rete: str) -> Materiale:
    """Il materiale delle tubazioni di una rete: il suo, o quello del progetto, o il
    multistrato (I-279)."""
    for item in project.networks:
        if item.id == rete and item.materiale_tubazioni is not None:
            return item.materiale_tubazioni
    return project.materiale_tubazioni or MATERIALE_PREDEFINITO


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


def _idraulici(project: ProjectModel, tratti: Sequence[TrattoDelDiametro]) -> list[TrattoDelDiametro]:
    reti = {item.id for item in project.networks if item.domain is Domain.HYDRONIC}
    return [item for item in tratti if all(rete in reti for rete in item.reti)]


def tubi_delle_tubazioni(
    project: ProjectModel,
    catalog: ComponentRegistry,
    tratti: Sequence[TrattoDelDiametro] | None = None,
) -> dict[str, Tubo]:
    """Il tubo di ogni tubazione d'acqua che ne ha uno: quello che il progettista ha
    scritto sulla tubazione; altrimenti quello del suo tratto (del progettista, o del
    calcolo dove il tratto lo porta). Lo leggono la distinta e la nota dell'isolamento,
    che dicono lo stesso tubo della tavola (I-279)."""
    if tratti is None:
        tratti = tratti_del_diametro(project, catalog)
    idrauliche = {item.id for item in project.networks if item.domain is Domain.HYDRONIC}
    propri = {
        item.id: tubo
        for item in project.connections
        if item.network_id in idrauliche and (tubo := tubo_dal_testo(item.sezione)) is not None
    }
    tubi: dict[str, Tubo] = {}
    for tratto in _idraulici(project, tratti):
        for tubo_id in sorted(tratto.connection_ids):
            tubo = propri.get(tubo_id) or tratto.tubo
            if tubo is not None:
                tubi[tubo_id] = tubo
    return tubi


def pollici_dei_pezzi(
    project: ProjectModel,
    catalog: ComponentRegistry,
    tratti: Sequence[TrattoDelDiametro] | None = None,
) -> dict[str, str]:
    """Il pollice degli accessori in linea — valvole, filtri, circolatori, i T di
    servizio, la via dritta di una tre vie —: quello del tubo su cui stanno (MS 32×3 →
    1", I-279). I capi di un tratto — le macchine, i raccordi dove la portata cambia —
    no: stanno fra tubi diversi."""
    if tratti is None:
        tratti = tratti_del_diametro(project, catalog)
    tubi = tubi_delle_tubazioni(project, catalog, tratti)
    capi_di = {item.id: (item.endpoint_a.component_id, item.endpoint_b.component_id) for item in project.connections}
    pollici: dict[str, str] = {}
    for tratto in _idraulici(project, tratti):
        capi = {ref.component_id for ref in tratto.capi}
        for tubo_id in tratto.connection_ids:
            tubo = tubi.get(tubo_id)
            if tubo is None:
                continue
            for pezzo in capi_di.get(tubo_id, ()):
                if pezzo in capi:
                    continue
                gia = pollici.get(pezzo)
                if gia is None or ordine_del_pollice(tubo.pollici) > ordine_del_pollice(gia):
                    pollici[pezzo] = tubo.pollici
    return pollici


def avvisi_dei_tubi(
    project: ProjectModel,
    catalog: ComponentRegistry,
    sigle: dict[str, str] | None = None,
    tratti: Sequence[TrattoDelDiametro] | None = None,
) -> list[str]:
    """Dove il tubo del progettista e' piu' piccolo di quello del calcolo: la
    velocita' reale supera la massima del suo pollice (I-279). Un avviso, non un
    blocco: la tavola scrive il suo tubo. E dove la portata va oltre l'ultimo tubo del
    materiale, e il tratto resta senza. Solo sulle reti dove ha chiesto i diametri, e
    solo dove la portata viene dai suoi dati; un testo che non si legge come un tubo non
    si controlla."""
    if project.diametri is None:
        return []
    if tratti is None:
        tratti = tratti_del_diametro(project, catalog)
    nomi = {item.id: item.tag or item.id for item in project.components}
    nomi.update(sigle or {})
    avvisi: list[str] = []
    for tratto in _idraulici(project, tratti):
        tubo, portata = tratto.tubo_del_progettista, tratto.portata_m3h
        if portata is None or not tratto.richiesto or portata <= TOLLERANZA_M3H:
            continue
        capo, fine = tratto.capi
        if tubo is None and tratto.diametro is None and tratto.perche_senza_dn is not None:
            # Oltre l'ultimo tubo del materiale: il tratto resta senza, e lo si dice.
            if tratto.perche_senza_dn.startswith("oltre "):
                avvisi.append(
                    f"{nomi.get(capo.component_id, capo.component_id)} -> "
                    f"{nomi.get(fine.component_id, fine.component_id)}: {_n(portata, 2)} m³/h, "
                    f"{tratto.perche_senza_dn}. Il tratto resta senza tubo: serve un altro materiale "
                    "(`materiale_tubazioni`) o il tubo del progettista (I-279)."
                )
            continue
        if tubo is None:
            continue
        velocita = tubo.velocita_m_s(portata)
        if velocita <= tubo.velocita_massima_m_s * (1 + 1e-9):
            continue
        calcolo = tubo_per(portata, tubo.materiale)
        sceglierebbe = (
            f"il calcolo sceglierebbe {calcolo.scritta}"
            if calcolo is not None
            else "nemmeno l'ultimo tubo della tabella basta"
        )
        avvisi.append(
            f"{nomi.get(capo.component_id, capo.component_id)} -> {nomi.get(fine.component_id, fine.component_id)}: "
            f"{tubo.scritta} del progettista (Øi {_n(tubo.interno_mm)} mm), {_n(portata, 2)} m³/h a "
            f"{_n(velocita, 2)} m/s, oltre la massima di {_n(tubo.velocita_massima_m_s)} m/s del suo pollice "
            f"({tubo.pollici}, Quaderno Caleffi n. 5, D-193): {sceglierebbe}. Sulla tavola resta il tubo del "
            "progettista (I-279)."
        )
    return avvisi


def _n(valore: float, cifre: int = 1) -> str:
    testo = f"{valore:.{cifre}f}"
    if cifre == 1:
        testo = testo.removesuffix(".0")
    return testo.replace(".", ",")


__all__ = [
    "TrattoDelDiametro",
    "avvisi_dei_tubi",
    "materiale_della_rete",
    "pollici_dei_pezzi",
    "tubi_delle_tubazioni",
    "tratti_da_etichettare",
    "tratti_del_diametro",
]
