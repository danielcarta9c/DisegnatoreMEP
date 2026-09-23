"""Mandata o ritorno lo dice il fluido, anche dove le camminate si fermano.

Il colore di una tratta viene dal modello (I-042, D-059): si cammina dai
generatori in avanti — mandata — e all'indietro — ritorno — fermandosi a ogni
utilizzatore. Le tratte che nessuna camminata raggiunge restavano indecise, e
per loro decideva la geometria: **mandata se la tratta va verso destra**.

Il 23 settembre 2026 un agente in camera pulita ha visto il ritorno delle zone
dipinto da mandata sull'impianto 3, dove il volano sta **in serie sul
ritorno** e ferma la camminata che risale dalla pompa di calore: una posa
migliore, scartata perche' la tavola non si leggeva. Lo stesso accadeva sul
by-pass della miscelatrice dell'impianto 5.
"""

# categoria: difende il motore — il colore di una tratta lo decide il modello, non il verso in cui e' disegnata (I-042)

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.flow import classify_trunks
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PROVE = ROOT / "examples" / "prova"
IMPIANTI = (
    "prova-1-due-pdc-accumulo-combinato.json",
    "prova-2-pdc-deviatrice-acs.json",
    "prova-3-pdc-diretta-pavimento.json",
    "prova-4-ibrido-pdc-caldaia.json",
    "prova-5-cascata-tre-pdc.json",
)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


@cache
def completo(nome: str) -> ProjectModel:
    """L'impianto con il corredo che le regole aggiungono: e' il grafo che il
    pianificatore riceve."""
    fatto, _, _ = saturate(
        load_project(PROVE / nome),
        catalogo(),
        RuleRegistry.from_directory(ROOT / "rules" / "hydronic"),
    )
    return ProjectModel.model_validate_json(canonical_json(fatto))


def tratte(progetto: ProjectModel) -> list[Trunk]:
    return build_trunks(progetto, inline_component_ids(progetto, catalogo()))


def ruolo(progetto: ProjectModel, trunk: Trunk) -> bool | None:
    return classify_trunks(progetto, catalogo(), tratte(progetto))[trunk.connection_ids].supply


def funzioni(progetto: ProjectModel, component_id: str) -> frozenset[str]:
    definizione = next(
        item.definition_id for item in progetto.components if item.id == component_id
    )
    return frozenset(catalogo().get(definizione).functions)


@pytest.mark.parametrize("nome", IMPIANTI)
def test_nessuna_tratta_resta_al_ripiego_geometrico(nome: str) -> None:
    """Sui cinque impianti, completi del corredo, **ogni** tratta ha il suo
    ruolo dal modello. Prima del 23 settembre 2026 ne restavano indecise tre
    sull'impianto 3 e una sul 5."""
    progetto = completo(nome)
    classificate = classify_trunks(progetto, catalogo(), tratte(progetto))
    indecise = [key for key, flusso in classificate.items() if flusso.supply is None]
    assert indecise == []


def test_il_ritorno_delle_zone_verso_il_volano_in_serie_e_ritorno() -> None:
    """**Il caso dell'agente.** Sull'impianto 3 il volano sta in serie sul
    ritorno: dalle zone al raccordo che le riunisce, e dal raccordo al volano,
    il fluido e' ritorno — e' uscito da un terminale e non ha attraversato
    nient'altro che un raccordo."""
    progetto = completo("prova-3-pdc-diretta-pavimento.json")
    dal_volano = [
        trunk
        for trunk in tratte(progetto)
        if "thermal_storage" in funzioni(progetto, trunk.end.component_id)
        and "junction" in funzioni(progetto, trunk.start.component_id)
    ]
    dalle_zone = [
        trunk
        for trunk in tratte(progetto)
        if "emission" in funzioni(progetto, trunk.start.component_id)
    ]
    assert len(dal_volano) == 1 and len(dalle_zone) == 2
    assert [ruolo(progetto, trunk) for trunk in (*dal_volano, *dalle_zone)] == [
        False,
        False,
        False,
    ]


def test_il_by_pass_della_miscelatrice_e_ritorno() -> None:
    """Sull'impianto 5 il by-pass entra nella miscelatrice dal ritorno del
    pavimento radiante: e' acqua di ritorno. Il ruolo lo porta chi arriva, non
    chi riparte — dalla miscelatrice esce mandata, e non per questo il by-pass
    lo e'."""
    progetto = completo("prova-5-cascata-tre-pdc.json")
    by_pass = [
        trunk
        for trunk in tratte(progetto)
        if "circuit_mixing" in funzioni(progetto, trunk.end.component_id)
        and trunk.end.port_id == "cold_in"
    ]
    assert len(by_pass) == 1
    assert ruolo(progetto, by_pass[0]) is False
