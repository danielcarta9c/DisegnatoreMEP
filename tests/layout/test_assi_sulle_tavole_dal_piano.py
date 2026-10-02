"""Le prove di DRAW-008: la posa a fasi, prima le autostrade.

> **Dal 2 ottobre 2026 (I-180) il solutore non c'e' piu'**, e con lui le prove che lo
> difendevano. Restano qui due misure sulle tavole approvate dal piano: la macchina principale e l'accumulo in asse, e quante tratte minori attraversano ancora il tronco. Il resto di questa intestazione e' la storia del
> file, e si legge come tale.


Il PO, l'11 settembre 2026:

    «Il sistema di instradatura deve prima disegnare le autostrade e farle piu'
    dritte possibile. Poi si mettono dentro tutte le altre valvole e pezzi, e se
    non ci stanno le autostrade le puoi allungare, stretchare, spostando le
    macchine principali — sempre pero' mantenendo le autostrade dritte. Poi ci
    attacchiamo le reti stradali di servizio, e quelle si', accettiamo qualche
    curva in piu'.»

Le tre fasi hanno tre invarianti, e ciascuno e' provato qui:

- **il tronco** e' una fase a se': posa le sole macchine di spina, instrada la
  sola autostrada, e il resto dell'impianto non vi partecipa;
- **il corredo** entra dentro il tronco, e dove non ci sta il tronco **si
  allunga** invece di piegarsi;
- **le strade di servizio** si attaccano a un tronco che non si piega piu',
  qualunque cosa ci guadagnerebbero.

E una cosa che non e' un invariante ma un **limite dichiarato**: una tratta e'
un rettilineo solo se le sue due porte si guardano, e ci sono coppie che
nessuna rotazione ammessa mette una di fronte all'altra. La prova che le conta
sta qui sotto, e le nomina: distinguere «non e' dritta» da «non puo' esserlo»
e' il modo di non ammorbidire il criterio fingendo di rispettarlo.

Gli impianti sono costruiti qui, con il catalogo di prova; le due tavole vere
si guardano dove il pacchetto le nomina, cioe' sulle fixture di `examples`.
"""
# categoria: difende una regola del piano — B1 e gli attraversamenti del tronco, misurati sulle tavole approvate dal piano

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import (
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import (
    ProjectModel,
)
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
PROVE = ROOT / "examples" / "prova"

TAVOLA_1 = PROVE / "prova-1-due-pdc-accumulo-combinato.json"
TAVOLA_2 = PROVE / "prova-2-pdc-deviatrice-acs.json"



@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
















APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
"""I grafi completi e i piani che il pianificatore ha composto in camera pulita."""


def _numero(path: Path) -> str:
    return path.name.split("-")[1]


@cache
def _fixture(path: Path) -> ProjectModel:
    """Il grafo completo **su cui il piano approvato e' stato composto** (`DRAW-018`)."""
    return load_project(APPROVATI / f"grafo-completo-{_numero(path)}.json")


def _partizione(project: ProjectModel) -> SheetPartition:
    inline = inline_component_ids(project, catalog())
    return partition_project(project, build_trunks(project, inline))[0]






def _autostrade_del_foglio(
    project: ProjectModel, sheet: SheetGeometry
) -> list[tuple[Trunk, RoutedTrunk]]:
    """Le autostrade della tavola consegnata, con la spezzata che le disegna."""
    partition = _partizione(project)
    levels = hierarchy_of(project, catalog(), list(partition.trunks))
    routes = {tuple(item.connection_ids): item for item in sheet.routes}
    return [
        (trunk, routes[tuple(trunk.connection_ids)])
        for trunk in partition.trunks
        if levels[trunk.connection_ids] is Level.AUTOSTRADA
        and tuple(trunk.connection_ids) in routes
    ]


@cache
def _tavola(path: Path) -> SheetGeometry:
    """La tavola **dal piano** approvato, come la compone la skill (D-151). Fino al
    2 ottobre 2026 queste prove componevano senza piano, con la fase del tronco e
    il ciclo di miglioramento: tolti tutti e due (I-180), quello che resta da
    misurare e' la tavola che esce dal piano."""
    esito = esegui_piano(
        _fixture(path),
        carica_piano(APPROVATI / f"piano-completo-{_numero(path)}.json"),
        catalog(),
        SymbolRegistry.from_directory(SYMBOLS),
        ROOT / "naming",
    )
    assert esito.disegno is not None, esito.errore
    return esito.disegno.sheets[0]


# ---------------------------------------------------------------------------
# Criterio 1 — la fase del tronco esiste ed e' separata
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Criterio 2 — il tronco e' dritto
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# Criterio 3 — la rettilineita' e' un vincolo, non un costo
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Criterio 4 — il tronco si allunga invece di piegarsi
# ---------------------------------------------------------------------------












# ---------------------------------------------------------------------------
# Criterio 5 — le strade di servizio non piegano il tronco
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# Criteri 7 e 8 — le due tavole
# ---------------------------------------------------------------------------


def _porte_di_autostrada(
    project: ProjectModel, sheet: SheetGeometry, component_id: str
) -> dict[str, float]:
    """Dove stanno, sull'asse trasversale, le porte di autostrada di un pezzo."""
    registry = catalog()
    placed = next(item for item in sheet.symbols if item.component_id == component_id)
    manifest = registry.resolve(
        next(
            item.definition_id
            for item in project.components
            if item.id == component_id
        )
    ).symbol.manifest.rotated(placed.rotation_deg)
    found: dict[str, float] = {}
    for trunk, _route in _autostrade_del_foglio(project, sheet):
        for ref in (trunk.start, trunk.end):
            if ref.component_id != component_id:
                continue
            port = manifest.port(placed.physical_port(ref.port_id))
            found[ref.port_id] = placed.origin.y_mm + port.y_mm
    return found


def test_sulla_tavola_2_la_macchina_principale_e_l_accumulo_maggiore_sono_in_asse() -> None:
    """Il §4 dell'architettura, letto sulla tavola consegnata.

    «Allineando ingressi e uscite della macchina principale con quelli del
    serbatoio principale automaticamente abbiamo gia' due linee macro
    parallele»: la mandata della pompa di calore e l'ingresso del volano su una
    retta, il ritorno e l'uscita sull'altra. Non si giudica sull'intenzione ma
    sulle coordinate delle porte nella geometria che esce.
    """
    project = _fixture(TAVOLA_2)
    sheet = _tavola(TAVOLA_2)
    macchina = _porte_di_autostrada(project, sheet, "pdc")
    accumulo = _porte_di_autostrada(project, sheet, "volano")
    assert set(macchina) == {"water_supply", "water_return"}
    # Da `DRAW-012` §B anche il **secondario** del volano e' autostrada — e'
    # la strada che dagli accumuli va ai circolatori e da li' ai terminali —
    # quindi le porte di autostrada dell'accumulo sono quattro. Cio' che questa
    # prova guarda resta il **primario**, che e' l'asse di cui parla
    # l'architettura §4: le altre due si nominano per dire che ci sono.
    assert set(accumulo) == {
        "primary_in",
        "primary_out",
        "secondary_in",
        "secondary_out",
    }
    accumulo = {
        name: value
        for name, value in accumulo.items()
        if name in {"primary_in", "primary_out"}
    }
    assert macchina["water_supply"] == pytest.approx(accumulo["primary_in"])
    assert macchina["water_return"] == pytest.approx(accumulo["primary_out"])
    assert macchina["water_supply"] != macchina["water_return"]


def _nodi_condivisi_col_tronco(project: ProjectModel, sheet: SheetGeometry) -> int:
    """Quanti nodi di griglia una tratta di rango inferiore divide con un'autostrada."""
    partition = _partizione(project)
    levels = hierarchy_of(project, catalog(), list(partition.trunks))
    livello = {
        tuple(trunk.connection_ids): levels[trunk.connection_ids]
        for trunk in partition.trunks
    }
    passaggi: dict[tuple[float, float], set[Level]] = {}
    for route in sheet.routes:
        rank = livello.get(tuple(route.connection_ids))
        if rank is None:
            continue
        for segment in route.segments:
            for before, after in zip(segment, segment[1:], strict=False):
                passi = int(
                    round(
                        (
                            abs(after.x_mm - before.x_mm)
                            + abs(after.y_mm - before.y_mm)
                        )
                        / 2.5
                    )
                )
                for step in range(passi + 1):
                    ratio = 0.0 if passi == 0 else step / passi
                    cell = (
                        round(before.x_mm + (after.x_mm - before.x_mm) * ratio, 3),
                        round(before.y_mm + (after.y_mm - before.y_mm) * ratio, 3),
                    )
                    passaggi.setdefault(cell, set()).add(rank)
    return sum(
        1
        for ranghi in passaggi.values()
        if Level.AUTOSTRADA in ranghi and len(ranghi) > 1
    )


def test_quante_tratte_di_rango_inferiore_attraversano_ancora_il_tronco() -> None:
    """**Questa non e' la seconda meta' del criterio 7: e' la misura del suo scarto.**

    Il criterio chiede che nessuna tratta di rango inferiore attraversi
    un'autostrada. Sulla tavola 2 ne restano, e la causa e' quella che
    l'architettura ha gia' messo fuori perimetro (§6, I-061): l'acqua fredda
    attraversa il foglio con una linea sola, e il bollitore che la riceve sta
    dall'altra parte del tronco. Finche' l'ingresso dell'AF non si ripete, un
    tronco che passa in mezzo lo si incrocia per forza.

    La riga sta qui, misurata e non ammorbidita, perche' il numero non cresca
    di nascosto: **scende** quando I-061 sara' chiuso, e non deve risalire nel
    frattempo.
    """
    uno = _nodi_condivisi_col_tronco(_fixture(TAVOLA_1), _tavola(TAVOLA_1))
    due = _nodi_condivisi_col_tronco(_fixture(TAVOLA_2), _tavola(TAVOLA_2))
    assert uno <= 1, uno
    assert due <= 8, due




# ---------------------------------------------------------------------------
# Criterio 11 — tutti e cinque gli impianti arrivano alla posa
# ---------------------------------------------------------------------------


