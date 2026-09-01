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

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol, SheetGeometry
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import port_aprons
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

COMPONIBILI = ("prova-1-due-pdc-accumulo-combinato.json",)
"""L'impianto che entra in una A3 oggi.

⛔ **Il 9 agosto erano tre, e sono tornati uno. Non e' un ammorbidimento: e' un
prezzo, ed e' misurato.** Il verso del fluido era sbagliato — sulla rete di
acqua fredda il disegnatore prendeva il bollitore come sorgente invece
dell'acquedotto, e disegnava **tutta l'adduzione come un ritorno**. Correggerlo
cambia l'ordine con cui il collocatore legge il processo, e la disposizione non
regge il cambiamento: il terzo impianto chiede 420 mm contro i 335 di una A3, e
il secondo non trova piu' il rettilineo per una valvola.

Un disegno che sbaglia il verso dell'acqua e' peggio di un disegno che non
esce: il committente non puo' verificarci niente, e infatti se n'e' accorto in
pochi minuti. La correzione resta; a rientrare devono essere gli impianti,
quando la composizione compatta. Il conto e' in `NON_COMPONGONO`."""

NON_COMPONGONO = ("prova-2-pdc-deviatrice-acs.json",)
"""Gli impianti che componevano il 9 agosto e oggi no, con il motivo misurato."""

TORNATO_A_COMPORRE = ("prova-3-pdc-diretta-pavimento.json",)
"""Chi era in `NON_COMPONGONO` e ha ricominciato a comporre (DRAW-001).

Il terzo impianto chiedeva 420 mm contro i 335 di una A3 e non entrava. Da
quando il collocatore **distende** invece di limitarsi a stringere (D-111) —
e la posa che ne esce e' un'altra — la sua fila rientra e la tavola si compone
in un foglio solo.

⚠ **Che componga e' un fatto, che sia bella non lo dice nessuno.** Qui si
verifica solo che la catena arrivi in fondo: la **qualita'** delle altre quattro
tavole non si guarda e non si consegna finche' il PO non ha approvato la prima
(D-116). La riga esiste perche' un guadagno misurato non vada perso, non per
aprire un cantiere sul terzo impianto."""


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
    drawing = compose_drawing(completato(name), catalog(), NOVE_C_A3)
    assert len(drawing.sheets) == 1
    sheet = drawing.sheets[0]
    assert sheet.symbols
    assert sheet.routes


@pytest.mark.parametrize("name", COMPONIBILI)
def test_nessun_simbolo_si_sovrappone_a_un_altro(name: str) -> None:
    """Nemmeno cio' che pende: uno sfogo sta fuori dal riquadro del proprio
    serbatoio, e chi gli sale sopra deve saperlo."""
    sheet = compose_drawing(completato(name), catalog(), NOVE_C_A3).sheets[0]
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
    model = completato(name)
    registry = catalog()
    sheet: SheetGeometry = compose_drawing(model, registry, NOVE_C_A3).sheets[0]
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


@pytest.mark.xfail(
    strict=True,
    reason="APERTO, e misurato. Questi due impianti componevano il 9 agosto e "
    "hanno smesso quando il verso del fluido e' stato corretto: sulla rete di "
    "acqua fredda la sorgente era il bollitore invece dell'acquedotto, e tutta "
    "l'adduzione veniva disegnata come un ritorno. Il verso giusto cambia "
    "l'ordine del processo, e la disposizione non lo regge: il terzo impianto "
    "chiede 420 mm contro i 335 di una A3, il secondo non trova il rettilineo "
    "per una valvola di intercettazione. Torna verde quando la composizione "
    "compatta davvero — non abbassando i minimi grafici.",
)
@pytest.mark.parametrize("name", NON_COMPONGONO)
def test_tornano_a_comporre_quando_la_composizione_compatta(name: str) -> None:
    drawing = compose_drawing(completato(name), catalog(), NOVE_C_A3)
    assert len(drawing.sheets) == 1


@pytest.mark.parametrize("name", TORNATO_A_COMPORRE)
def test_chi_e_tornato_a_comporre_compone_in_un_foglio_solo(name: str) -> None:
    """Il terzo impianto rientra in una A3 da quando il collocatore distende.

    Solo che compone, e nient'altro: le altre quattro tavole non si guardano
    finche' la prima non e' approvata (D-116).
    """
    drawing = compose_drawing(completato(name), catalog(), NOVE_C_A3)
    assert len(drawing.sheets) == 1
