"""Il comando `vaso`: dimensiona il vaso d'espansione e lo scrive sul grafo (D-220, D-221, D-224).

Gira sul **grafo completo**, dopo `completa` e prima di `disegna`: il vaso lo aggiunge una
regola, e solo dopo c'e' un pezzo su cui scrivere. Scrive:

- sul vaso, **sempre**: ``volume_l`` (la taglia scelta), e ``contenuto_stimato`` se i litri
  erano una stima;
- **solo nel progetto esecutivo** (``metadata.livello == "esecutivo"``): sul vaso la
  ``precarica_bar``; su ogni valvola di sicurezza del circuito la scritta della taratura
  («3 bar»); sul gruppo di riempimento la pressione di caricamento («carica 2,0 bar»).

Un vaso per circuito: quello d'acqua di riscaldamento. Se nel grafo ce n'e' piu' d'uno, il
comando vuole sapere quale (``--vaso``). Se le macchine del circuito sono Shenling, la
pressione minima (1,5 bar) e quella di riempimento (2,0 bar) sono quelle del manuale, a
meno che il progettista ne dia altre.

**Il vaso sanitario** (REL-026, I-300; ``--sanitario``): quello sull'acqua fredda del
bollitore, che la regola posa fra il non ritorno e il bollitore (D-178, I-272). Si
dimensiona dal volume del bollitore — se il progettista non lo da', quello scritto sul
bollitore del grafo —, dalla massima di accumulo, dalla pressione di rete (o dalla taratura
del riduttore) e dalla taratura della valvola di sicurezza (`calcolatore`,
`dimensiona_il_vaso_sanitario`). Scrive come per il riscaldamento: sul vaso ``volume_l``
sempre, ``precarica_bar`` nell'esecutivo; nell'esecutivo la taratura accanto alla sicurezza
del sanitario. Prima di REL-026 la taglia del vaso sanitario si scriveva a mano nel grafo.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.io.project_json import dump_project, load_project
from disegnatore_mep.model.project import MARCA, ComponentInstance, ProjectModel

from .calcolatore import (
    DatiDelVaso,
    DatiDelVasoSanitario,
    Vaso,
    VasoSanitario,
    dimensiona_il_vaso,
    dimensiona_il_vaso_sanitario,
)

ETICHETTA = "etichetta"

SHENLING_PRESSIONE_MINIMA_BAR = 1.5
"""ThermaX R290, ricerca guasti: «la pressione dell'acqua deve essere ≥ 1,5 bar»."""

SHENLING_RIEMPIMENTO_BAR = 2.0
"""ThermaX R290, § 6.6: «Riempire con una pressione dell'acqua di circa 2,0 bar»."""


def _bar(valore: float) -> str:
    return f"{valore:.1f}".replace(".", ",").replace(",0", "") if float(valore).is_integer() else f"{valore:.1f}".replace(".", ",")


def _funzioni(catalogo: ComponentRegistry, pezzo: ComponentInstance) -> set[str]:
    return set(catalogo.get(pezzo.definition_id).functions) if catalogo.contains(pezzo.definition_id) else set()


def _reti_di(modello: ProjectModel, pezzo_id: str) -> set[str]:
    return {
        c.network_id
        for c in modello.connections
        if pezzo_id in (c.endpoint_a.component_id, c.endpoint_b.component_id)
    }


ACQUA_DI_RISCALDAMENTO = "heating_water"
ACQUA_FREDDA_SANITARIA = "cold_water"
"""Il fluido su cui sta il vaso sanitario: l'acqua fredda in ingresso al bollitore."""


def _circuito(modello: ProjectModel, partenza: str, fluido: str = ACQUA_DI_RISCALDAMENTO) -> set[str]:
    """I pezzi raggiungibili dal vaso senza uscire dal suo fluido: il suo circuito,
    attraverso volani e collettori (un volano a 4 attacchi non separa l'acqua)."""
    reti = {n.id for n in modello.networks if n.medium == fluido}
    vicini: dict[str, set[str]] = {}
    for c in modello.connections:
        if c.network_id not in reti:
            continue
        a, b = c.endpoint_a.component_id, c.endpoint_b.component_id
        vicini.setdefault(a, set()).add(b)
        vicini.setdefault(b, set()).add(a)
    visti, da_fare = {partenza}, [partenza]
    while da_fare:
        for vicino in vicini.get(da_fare.pop(), ()):
            if vicino not in visti:
                visti.add(vicino)
                da_fare.append(vicino)
    return visti


def vasi_di_riscaldamento(modello: ProjectModel, catalogo: ComponentRegistry) -> list[ComponentInstance]:
    reti = {n.id for n in modello.networks if n.medium == "heating_water"}
    return [
        p for p in modello.components
        if "expansion" in _funzioni(catalogo, p) and _reti_di(modello, p.id) & reti
    ]


def applica(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    contenuto_l: float,
    temperatura_massima_c: float,
    dislivello_m: float,
    vaso_id: str | None = None,
    taratura_bar: float = 3.0,
    pressione_minima_bar: float | None = None,
    riempimento_bar: float | None = None,
    coefficiente: float | None = None,
    stimato: bool = False,
) -> tuple[ProjectModel, Vaso, list[str]]:
    """Il grafo con il vaso scritto, il vaso, e che cosa e' stato scritto dove."""
    vasi = vasi_di_riscaldamento(modello, catalogo)
    if vaso_id is not None:
        vasi = [v for v in vasi if v.id == vaso_id]
        if not vasi:
            raise ValueError(f"nessun vaso d'impianto con id {vaso_id!r}")
    if not vasi:
        raise ValueError("il grafo non ha un vaso d'espansione sull'acqua di riscaldamento: prima `completa`")
    if len(vasi) > 1:
        raise ValueError(
            "il grafo ha piu' vasi d'impianto: " + ", ".join(v.id for v in vasi)
            + ". Uno per volta, con --vaso e il contenuto del suo circuito"
        )
    vaso_pezzo = vasi[0]
    circuito = _circuito(modello, vaso_pezzo.id)
    pezzi = {p.id: p for p in modello.components}
    shenling = any(
        "heat_generation" in _funzioni(catalogo, pezzi[i])
        and "shenling" in str(pezzi[i].properties.get(MARCA, "")).lower()
        for i in circuito if i in pezzi
    )
    if pressione_minima_bar is None:
        pressione_minima_bar = SHENLING_PRESSIONE_MINIMA_BAR if shenling else 0.0
    if riempimento_bar is None:
        riempimento_bar = SHENLING_RIEMPIMENTO_BAR if shenling else 0.0
    vaso = dimensiona_il_vaso(
        DatiDelVaso(
            contenuto_l=contenuto_l,
            temperatura_massima_c=temperatura_massima_c,
            dislivello_m=dislivello_m,
            taratura_sicurezza_bar=taratura_bar,
            pressione_minima_bar=pressione_minima_bar,
            pressione_di_riempimento_bar=riempimento_bar,
            coefficiente_di_espansione=coefficiente,
            contenuto_stimato=stimato,
        )
    )
    esecutivo = modello.metadata.livello == "esecutivo"
    scritto: list[str] = []
    nuovi: list[ComponentInstance] = []
    for pezzo in modello.components:
        proprieta = dict(pezzo.properties)
        if pezzo.id == vaso_pezzo.id:
            if vaso.taglia_l is not None:
                proprieta["volume_l"] = vaso.taglia_l
            proprieta.pop("precarica_bar", None)
            proprieta.pop("contenuto_stimato", None)
            if esecutivo:
                proprieta["precarica_bar"] = vaso.precarica_bar
            if stimato:
                proprieta["contenuto_stimato"] = True
            scritto.append(f"{pezzo.id}: {vaso.caratteristiche(esecutivo, stimato)}")
        elif esecutivo and pezzo.id in circuito:
            funzioni = _funzioni(catalogo, pezzo)
            if "safety" in funzioni and not proprieta.get(ETICHETTA):
                proprieta[ETICHETTA] = f"{_bar(taratura_bar)} bar"
                scritto.append(f"{pezzo.id}: «{proprieta[ETICHETTA]}»")
            elif "filling" in funzioni and not proprieta.get(ETICHETTA):
                proprieta[ETICHETTA] = vaso.scritta_di_caricamento
                scritto.append(f"{pezzo.id}: «{proprieta[ETICHETTA]}»")
        nuovi.append(pezzo.model_copy(update={"properties": proprieta}) if proprieta != pezzo.properties else pezzo)
    return modello.model_copy(update={"components": nuovi}), vaso, scritto


def vasi_sanitari(modello: ProjectModel, catalogo: ComponentRegistry) -> list[ComponentInstance]:
    reti = {n.id for n in modello.networks if n.medium == ACQUA_FREDDA_SANITARIA}
    return [
        p for p in modello.components
        if "expansion" in _funzioni(catalogo, p) and _reti_di(modello, p.id) & reti
    ]


def applica_sanitario(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    temperatura_massima_c: float,
    pressione_di_rete_bar: float,
    taratura_bar: float,
    volume_bollitore_l: float | None = None,
    vaso_id: str | None = None,
) -> tuple[ProjectModel, VasoSanitario, list[str]]:
    """Il grafo con il vaso sanitario scritto, il vaso, e che cosa e' stato scritto dove."""
    vasi = vasi_sanitari(modello, catalogo)
    if vaso_id is not None:
        vasi = [v for v in vasi if v.id == vaso_id]
        if not vasi:
            raise ValueError(f"nessun vaso sanitario con id {vaso_id!r}")
    if not vasi:
        raise ValueError(
            "il grafo non ha un vaso d'espansione sull'acqua fredda del bollitore: prima `completa` (il vaso "
            "sanitario lo posa la regola, se il bollitore non lo porta a bordo)"
        )
    if len(vasi) > 1:
        raise ValueError(
            "il grafo ha piu' vasi sanitari: " + ", ".join(v.id for v in vasi)
            + ". Uno per volta, con --vaso e il volume del suo bollitore"
        )
    vaso_pezzo = vasi[0]
    circuito = _circuito(modello, vaso_pezzo.id, ACQUA_FREDDA_SANITARIA)
    scritto: list[str] = []
    if volume_bollitore_l is None:
        bollitori = [
            p for p in modello.components
            if p.id in circuito and "dhw_storage" in _funzioni(catalogo, p)
        ]
        volumi = [p.properties.get("volume_l") for p in bollitori]
        if len(bollitori) != 1 or not isinstance(volumi[0], int | float) or isinstance(volumi[0], bool):
            raise ValueError(
                "il volume del bollitore non e' nel grafo (`volume_l` sul bollitore, uno solo sul circuito del "
                "vaso): dallo con --bollitore"
            )
        volume_bollitore_l = float(volumi[0])
        scritto.append(f"volume del bollitore dal grafo: {bollitori[0].id}, {volume_bollitore_l:g} l")
    vaso = dimensiona_il_vaso_sanitario(
        DatiDelVasoSanitario(
            volume_bollitore_l=volume_bollitore_l,
            temperatura_massima_c=temperatura_massima_c,
            pressione_di_rete_bar=pressione_di_rete_bar,
            taratura_sicurezza_bar=taratura_bar,
        )
    )
    esecutivo = modello.metadata.livello == "esecutivo"
    nuovi: list[ComponentInstance] = []
    for pezzo in modello.components:
        proprieta = dict(pezzo.properties)
        if pezzo.id == vaso_pezzo.id:
            if vaso.taglia_l is not None:
                proprieta["volume_l"] = vaso.taglia_l
            proprieta.pop("precarica_bar", None)
            if esecutivo:
                proprieta["precarica_bar"] = vaso.precarica_bar
            scritto.append(f"{pezzo.id}: {vaso.caratteristiche(esecutivo)}")
        elif esecutivo and pezzo.id in circuito:
            if "safety" in _funzioni(catalogo, pezzo) and not proprieta.get(ETICHETTA):
                proprieta[ETICHETTA] = f"{_bar(taratura_bar)} bar"
                scritto.append(f"{pezzo.id}: «{proprieta[ETICHETTA]}»")
        nuovi.append(pezzo.model_copy(update={"properties": proprieta}) if proprieta != pezzo.properties else pezzo)
    return modello.model_copy(update={"components": nuovi}), vaso, scritto


def esegui_sanitario(
    grafo: Path,
    uscita: Path | None,
    catalogo: ComponentRegistry,
    temperatura_massima_c: float,
    pressione_di_rete_bar: float,
    taratura_bar: float,
    volume_bollitore_l: float | None = None,
    vaso_id: str | None = None,
) -> int:
    modello = load_project(grafo)
    completo, vaso, scritto = applica_sanitario(
        modello, catalogo, temperatura_massima_c, pressione_di_rete_bar, taratura_bar, volume_bollitore_l, vaso_id
    )
    print(
        f"Vaso sanitario: coefficiente {vaso.coefficiente:.4f}, espansione {vaso.volume_di_espansione_l:.1f} l; "
        f"precarica {_bar(vaso.precarica_bar)} bar (0,2 bar sotto la rete a {_bar(vaso.pressione_di_rete_bar)} bar), "
        f"finale {_bar(vaso.pressione_finale_bar)} bar; "
        f"nominale {vaso.volume_nominale_l:.1f} l → "
        + (f"{vaso.taglia_l} l" if vaso.taglia_l else "oltre la serie")
        + "."
    )
    livello = completo.metadata.livello or "definitivo (non dichiarato)"
    print(f"Livello del progetto: {livello}. Scritto sul grafo:")
    for riga in scritto:
        print(f"  - {riga}")
    for avviso in vaso.avvisi:
        print(f"Avviso: {avviso}")
    dump_project(completo, uscita or grafo)
    return 2 if vaso.avvisi else 0


def esegui(
    grafo: Path,
    uscita: Path | None,
    catalogo: ComponentRegistry,
    **dati: object,
) -> int:
    modello = load_project(grafo)
    completo, vaso, scritto = applica(modello, catalogo, **dati)  # type: ignore[arg-type]
    print(
        f"Vaso: contenuto {dati['contenuto_l']:g} l, coefficiente {vaso.coefficiente:.4f}, "
        f"espansione {vaso.volume_di_espansione_l:.1f} l, riserva {vaso.riserva_l:.1f} l; "
        f"precarica {_bar(vaso.precarica_bar)} bar, finale {_bar(vaso.pressione_finale_bar)} bar; "
        f"nominale {vaso.volume_nominale_l:.1f} l → "
        + (f"{vaso.taglia_l} l" if vaso.taglia_l else "oltre la serie")
        + f"; carica a freddo {_bar(vaso.caricamento_bar)} bar."
    )
    livello = completo.metadata.livello or "definitivo (non dichiarato)"
    print(f"Livello del progetto: {livello}. Scritto sul grafo:")
    for riga in scritto:
        print(f"  - {riga}")
    for avviso in vaso.avvisi:
        print(f"Avviso: {avviso}")
    dump_project(completo, uscita or grafo)
    return 2 if vaso.avvisi else 0
