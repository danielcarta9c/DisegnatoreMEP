"""Chi pende da uno stacco, e la soglia di un attacco (D-111, D-112, D-113).

Tre fatti che la tavola dei cinque impianti ha insegnato, e che erano costati
al progetto la convinzione sbagliata che «l'impianto non entra in larghezza»:

- un accessorio appeso a uno stacco sta **accanto al pezzo da cui pende**, non
  in una colonna propria ordinata per profondita';
- davanti a ogni attacco in uso c'e' una **cella sola**, ed e' sua: chi ci si
  siede lo mura, e nessun formato piu' grande lo salva;
- le fasce si leggono **da sinistra a destra per processo** — chi genera, chi
  accumula, chi utilizza — e non nell'ordine in cui il file elenca i
  sottosistemi.
"""
# categoria: difende il motore

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol, SheetGeometry
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import port_aprons
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

COMPONIBILI = ("prova-1-due-pdc-accumulo-combinato.json",)
"""L'impianto su cui si misura: l'1, eseguito **dal piano** approvato (`dal_piano`).

Fino al 2 ottobre 2026 qui si componeva senza piano, e il file teneva il conto
degli impianti che quella via non componeva piu' (`NON_COMPONGONO`,
`TORNATO_A_COMPORRE`, due `xfail` che aspettavano «che la composizione
compatti»). La composizione e' del piano da D-151, e il solutore che l'avrebbe
compattata e' stato tolto (I-180): quelle attese non avevano piu' chi le
soddisfacesse, e sono uscite con lui."""




APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
"""I grafi completi e i piani che il pianificatore ha composto in camera pulita."""


def dal_piano(name: str) -> tuple[ProjectModel, SheetGeometry]:
    """La tavola **dal piano**, come la compone la skill (D-151): il grafo completo
    e il piano approvati dell'impianto (`DRAW-018`). Fino al 2 ottobre 2026 qui si
    componeva senza piano, e da D-167 quella via non instradava piu' l'impianto 1;
    il solutore che le dava le sue qualita' e' stato tolto (I-180)."""
    numero = name.split("-")[1]
    model = load_project(APPROVATI / f"grafo-completo-{numero}.json")
    esito = esegui_piano(
        model,
        carica_piano(APPROVATI / f"piano-completo-{numero}.json"),
        catalog(),
        SymbolRegistry.from_directory(SYMBOLS),
        ROOT / "naming",
    )
    assert esito.disegno is not None, esito.errore
    return model, esito.disegno.sheets[0]


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def completato(name: str) -> ProjectModel:
    registry = catalog()
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(registry)
    done, _, _ = saturate(load_project(PROVA / name), registry, rules)
    return done


def posa(model: ProjectModel) -> tuple[list[PlacedSymbol], SheetPartition]:
    registry = catalog()
    inline = inline_component_ids(model, registry)
    partition = partition_project(model, build_trunks(model, inline))[0]
    return place_sheet(model, partition, registry, NOVE_C_A3, inline), partition


def box(item: PlacedSymbol) -> tuple[float, float, float, float]:
    return (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)


# ---------------------------------------------------------------------------
# La tavola esce
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", COMPONIBILI)
def test_l_impianto_si_compone_su_una_a3(name: str) -> None:
    """La catena arriva in fondo e produce la geometria.

    E' la prova che riassume tutte le altre: prima che gli accessori appesi
    stessero accanto al proprio pezzo, questi tre impianti non si componevano
    **su nessun formato**, A0 compresa.
    """
    _, sheet = dal_piano(name)
    assert sheet.symbols
    assert sheet.routes


@pytest.mark.parametrize("name", COMPONIBILI)
def test_nessun_simbolo_si_sovrappone_a_un_altro(name: str) -> None:
    """Nemmeno cio' che pende: uno sfogo sta fuori dal riquadro del proprio
    serbatoio, e chi gli sale sopra deve saperlo."""
    _, sheet = dal_piano(name)
    boxes = [(item.component_id, box(item)) for item in sheet.symbols]
    for index, (first_id, first) in enumerate(boxes):
        for second_id, second in boxes[index + 1 :]:
            overlap = (
                first[0] < second[2] - 1e-6
                and second[0] < first[2] - 1e-6
                and first[1] < second[3] - 1e-6
                and second[1] < first[3] - 1e-6
            )
            assert not overlap, f"{first_id} e {second_id} si sovrappongono"


# ---------------------------------------------------------------------------
# Chi pende sta accanto al proprio pezzo
# ---------------------------------------------------------------------------


ADJACENCY_MM = 60.0
"""Quanto lontano puo' stare, al massimo, un accessorio dal pezzo che lo regge.

Non e' una soglia estetica: e' la distanza oltre la quale il difetto vero si
manifestava. Lo scarico dell'accumulo del primo impianto stava a sessanta
millimetri dal proprio accumulo, con due macchine in mezzo, e la sua tratta non
si instradava piu'."""


@pytest.mark.parametrize("name", COMPONIBILI)
def test_chi_pende_da_uno_stacco_sta_accanto_al_proprio_pezzo(name: str) -> None:
    model = completato(name)
    registry = catalog()
    placed, partition = posa(model)
    where = {item.component_id: item for item in placed}
    ports = {
        item.id: registry.resolve(item.definition_id).definition.ports
        for item in model.components
    }

    coppie: list[tuple[str, str]] = []
    for trunk in partition.trunks:
        for parent, child in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
            if child.component_id not in where or parent.component_id not in where:
                continue
            if len(ports.get(child.component_id, [])) != 1:
                continue
            if not any(
                port.id == parent.port_id and port.off_the_run
                for port in ports.get(parent.component_id, [])
            ):
                continue
            coppie.append((parent.component_id, child.component_id))

    assert coppie, "questo impianto non ha accessori appesi: la prova non misura nulla"
    for parent_id, child_id in coppie:
        regge, appeso = where[parent_id], where[child_id]
        gap_x = max(
            0.0, regge.origin.x_mm - appeso.right_mm, appeso.origin.x_mm - regge.right_mm
        )
        gap_y = max(
            0.0,
            regge.origin.y_mm - appeso.bottom_mm,
            appeso.origin.y_mm - regge.bottom_mm,
        )
        assert max(gap_x, gap_y) <= ADJACENCY_MM, (
            f"{child_id} pende da {parent_id} e gli sta a "
            f"{max(gap_x, gap_y):g}mm: non e' accanto, e la sua tratta lo paga"
        )


# ---------------------------------------------------------------------------
# La soglia di un attacco (D-113)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", COMPONIBILI)
def test_nessuno_si_siede_sulla_soglia_di_un_attacco(name: str) -> None:
    """La cella davanti a un attacco in uso resta libera da simboli.

    Un attacco ha una sola uscita: le altre tre celle gli stanno dentro. Chi
    occupa quella cella lo mura, e nessun formato piu' grande lo salva — l'unico
    modo per accorgersene e' guardare la cella, non la larghezza del foglio.
    """
    model, sheet = dal_piano(name)
    registry = catalog()
    inline = inline_component_ids(model, registry)
    partition = partition_project(model, build_trunks(model, inline))[0]
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)

    aprons = port_aprons(
        model, list(partition.trunks), sheet.symbols, registry, grid
    )
    murati = {(component_id, port_id) for (component_id, port_id) in aprons}
    for item in sheet.symbols:
        low = grid.to_cell(item.origin.x_mm, item.origin.y_mm)
        high = grid.to_cell(item.right_mm, item.bottom_mm)
        covered = {
            (col, row)
            for col in range(low[0], high[0] + 1)
            for row in range(low[1], high[1] + 1)
        }
        for key, cell in aprons.items():
            if key[0] == item.component_id or key not in murati:
                continue
            assert cell not in covered, (
                f"{item.component_id} si siede sulla soglia di "
                f"{key[0]}.{key[1]}: quell'attacco resta murato"
            )


# ---------------------------------------------------------------------------
# L'ordine di lettura (D-111)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", COMPONIBILI)
def test_chi_genera_sta_a_sinistra_di_chi_utilizza(name: str) -> None:
    """Le macchine principali a sinistra, come il PM ha chiesto (D-111).

    Prima l'ordine delle fasce veniva da quello in cui il file elenca i
    sottosistemi, cioe' dal loro nome: con `accumulo`, `distribuzione`,
    `generazione` le due pompe di calore finivano all'estrema destra e
    l'impianto si leggeva al contrario.
    """
    model = completato(name)
    registry = catalog()
    placed, _ = posa(model)
    where = {item.component_id: item.origin.x_mm for item in placed}

    generatori = [
        item.id
        for item in model.components
        if "heat_generation" in registry.resolve(item.definition_id).definition.functions
        and item.id in where
    ]
    utilizzatori = [
        item.id
        for item in model.components
        if {"emission", "air_terminal"}
        & set(registry.resolve(item.definition_id).definition.functions)
        and item.id in where
    ]
    assert generatori and utilizzatori, "senza generatori o utenze non si misura nulla"
    assert min(where[item] for item in generatori) < max(
        where[item] for item in utilizzatori
    )


# ---------------------------------------------------------------------------
# Il prezzo del verso corretto (aperto)
# ---------------------------------------------------------------------------




