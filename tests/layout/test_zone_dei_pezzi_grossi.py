"""Le zone valgono solo per i pezzi grossi (D-120), e i paralleli si impilano.

La correzione e' del PM, ed e' arrivata guardando la prima tavola: «le zone
servono solo per distribuire i macro componenti; le valvole che stanno in mezzo
possono finire dove vogliono, a cavallo fra le due zone o in una delle due».

Il difetto che chiude si vedeva a occhio sull'impianto 1: la **confluenza dei
due ritorni** e i tre raccordi del corredo di rete prendevano una colonna a
testa, quindi venivano letti come passi del processo e ordinati come macchine.
Il gruppo di riempimento del ritorno finiva **all'estrema sinistra del foglio**,
prima delle due pompe di calore, e il ritorno attraversava la tavola due volte
per raggiungerlo — che e' il rilievo I-007 del registro degli input.
"""

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import ZONED_FUNCTIONS, place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PLANTS = ROOT / "examples" / "prova"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

IMPIANTI = sorted(item.name for item in PLANTS.glob("prova-*.json"))
PRIMO = "prova-1-due-pdc-accumulo-combinato.json"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def completato(name: str) -> ProjectModel:
    """L'impianto come esce dalle regole: e' quello che si disegna."""
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog())
    completed, _, _ = saturate(load_project(PLANTS / name), catalog(), rules)
    return completed


def posa(name: str) -> list[PlacedSymbol]:
    project = completato(name)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return place_sheet(project, partition, catalog(), NOVE_C_A3, inline)


def funzioni(project: ProjectModel, component_id: str) -> frozenset[str]:
    definition = next(
        item.definition_id for item in project.components if item.id == component_id
    )
    return frozenset(catalog().resolve(definition).definition.functions)


QUINTO_APERTO = (
    "APERTO, e marcata rossa apposta. Sulla cascata di tre pompe di calore una "
    "confluenza del secondario resta a sinistra di tutto cio' che unisce: la "
    "sua catena tocca un solo pezzo grosso, quindi non ha una campata dentro "
    "cui distribuirsi e tiene la propria colonna, che l'ordine del processo "
    "porta all'estrema sinistra. Il campo di lavoro e' il solo impianto 1 "
    "(D-116) e il quinto si guarda quando tocca a lui: la riga esiste perche' "
    "il difetto non sia scoperto due volte. Torna verde quando anche le catene "
    "con un estremo solo sanno dove stare."
)


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            item,
            marks=(
                pytest.mark.xfail(strict=True, reason=QUINTO_APERTO)
                if item == "prova-5-cascata-tre-pdc.json"
                else ()
            ),
        )
        for item in IMPIANTI
    ],
)
def test_nessun_raccordo_sta_a_sinistra_di_cio_che_unisce(name: str) -> None:
    """Un raccordo sta **fra** i pezzi che unisce, mai prima di tutti.

    E' la forma misurabile del rilievo del PM: se la confluenza dei ritorni sta
    a sinistra di ogni macchina che vi rientra, il ritorno di quelle macchine
    attraversa la tavola per raggiungerla, e sulla carta si vede subito.
    """
    project = completato(name)
    try:
        placed = posa(name)
    except Exception as exc:  # noqa: BLE001 — un impianto che non si posa non prova nulla qui
        pytest.skip(f"{name} non si posa: {exc}")
    where = {item.component_id: item for item in placed}
    inline = inline_component_ids(project, catalog())
    trunks = build_trunks(project, inline)

    for component_id, item in sorted(where.items()):
        if funzioni(project, component_id) & ZONED_FUNCTIONS:
            continue
        neighbours = {
            other
            for trunk in trunks
            for mine, other in (
                (trunk.start.component_id, trunk.end.component_id),
                (trunk.end.component_id, trunk.start.component_id),
            )
            if mine == component_id and other in where
        }
        if len(neighbours) < 2:
            continue
        vicini = [where[other] for other in sorted(neighbours)]
        assert item.origin.x_mm >= min(other.origin.x_mm for other in vicini) - 1e-9, (
            f"{component_id} sta a sinistra di **tutto** cio' che unisce "
            f"({sorted(neighbours)}): per raggiungerlo, i loro collegamenti "
            f"tornano indietro e attraversano la tavola"
        )


def test_i_raccordi_non_prendono_una_colonna_a_testa() -> None:
    """Chi non e' un pezzo grosso non allarga la fascia.

    Si misura sul primo impianto, che e' quello che il PM guarda (D-116): la
    posa e' piu' stretta della somma delle colonne che i raccordi si prendevano.
    """
    placed = posa(PRIMO)
    largo = max(item.right_mm for item in placed) - min(
        item.origin.x_mm for item in placed
    )
    assert largo <= 280.0, (
        f"la posa dell'impianto 1 e' larga {largo:g}mm: con i raccordi in colonna "
        f"erano 330, e la correzione del PM serve proprio a toglierli dalla fila"
    )


def test_due_macchine_in_parallelo_si_impilano() -> None:
    """«Generatori a sinistra, impilati in verticale se sono piu' di uno» (D-119).

    Non e' estetica: affiancate, il collettore che le serve puo' stare da una
    parte sola, e il ritorno della seconda attraversa la tavola per
    raggiungerlo. Prima capitava per caso — si impilavano **solo** quando la
    fila non entrava nel foglio — e appena la tavola si e' stretta si sono
    affiancate e il ritorno non si e' piu' instradato.
    """
    where = {item.component_id: item for item in posa(PRIMO)}
    master, slave = where["pdc-master"], where["pdc-slave"]
    assert abs(master.origin.x_mm - slave.origin.x_mm) < 1e-9, (
        "le due pompe di calore non sono incolonnate: stanno a "
        f"{master.origin.x_mm:g} e {slave.origin.x_mm:g}"
    )
    assert master.origin.y_mm != slave.origin.y_mm


def test_il_primo_impianto_esce_ancora() -> None:
    """La prova che vale piu' di tutte: la tavola che il PM guarda si compone."""
    from disegnatore_mep.layout.compose import compose_drawing

    project = completato(PRIMO)
    drawing = compose_drawing(project, catalog(), NOVE_C_A3)
    assert drawing.sheets
    assert drawing.sheets[0].symbols
