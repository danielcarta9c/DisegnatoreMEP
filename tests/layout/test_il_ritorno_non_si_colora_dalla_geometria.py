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


def _impianto_della_prova_del_po() -> ProjectModel:
    """L'impianto della prima prova del PO su claude.ai, il 2 ottobre 2026 (I-171),
    senza i dati del cliente: pompa di calore, deviatrice fra pavimento radiante e
    serpentina del bollitore, i due ritorni riuniti da un raccordo e un **volano a
    due attacchi in serie sul ritorno**."""

    def pezzo(ident: str, definizione: str) -> dict[str, object]:
        return {"id": ident, "definition_id": definizione, "properties": {}}

    def tubo(ident: str, rete: str, da: tuple[str, str], a: tuple[str, str]) -> dict[str, object]:
        return {
            "id": ident,
            "network_id": rete,
            "endpoint_a": {"component_id": da[0], "port_id": da[1]},
            "endpoint_b": {"component_id": a[0], "port_id": a[1]},
            "properties": {},
        }

    documento = {
        "schema_version": "1.1.0",
        "metadata": {
            "project_id": "prova-po-volano-in-serie",
            "client": "Nove C",
            "project_name": "PdC, deviatrice, pavimento e bollitore, volano a due attacchi sul ritorno",
            "commission_code": "PROVA",
            "revision": "00",
            "issue_date": "2026-10-02",
        },
        "plant_regime": "up_to_35_kw",
        "networks": [
            {"id": "primario", "name": "Primario", "domain": "hydronic", "medium": "heating_water"},
            {"id": "fredda", "name": "Fredda", "domain": "hydronic", "medium": "cold_water"},
            {"id": "sanitaria", "name": "ACS", "domain": "hydronic", "medium": "domestic_hot_water"},
        ],
        "components": [
            pezzo("pdc", "heat-pump-air-water"),
            pezzo("deviatrice", "diverting-valve-3way"),
            pezzo("pavimento", "underfloor-panel"),
            pezzo("bollitore", "dhw-cylinder"),
            pezzo("ritorno", "tee-junction"),
            pezzo("volano", "buffer-two-port"),
            pezzo("acquedotto", "cold-water-inlet"),
            pezzo("utenze", "dhw-draw-off"),
        ],
        "connections": [
            tubo("p1", "primario", ("pdc", "water_supply"), ("deviatrice", "in")),
            tubo("p2", "primario", ("deviatrice", "out_a"), ("bollitore", "coil_in")),
            tubo("p3", "primario", ("deviatrice", "out_b"), ("pavimento", "in")),
            tubo("p4", "primario", ("bollitore", "coil_out"), ("ritorno", "c")),
            tubo("p5", "primario", ("pavimento", "out"), ("ritorno", "a")),
            tubo("p6", "primario", ("ritorno", "b"), ("volano", "a")),
            tubo("p7", "primario", ("volano", "b"), ("pdc", "water_return")),
            tubo("w1", "fredda", ("acquedotto", "a"), ("bollitore", "cold_in")),
            tubo("w2", "sanitaria", ("bollitore", "dhw_out"), ("utenze", "a")),
        ],
        "assumptions": [],
        "rule_applications": [],
        "subsystems": [],
        "sheets": [],
    }
    fatto, _, _ = saturate(
        ProjectModel.model_validate(documento),
        catalogo(),
        RuleRegistry.from_directory(ROOT / "rules" / "hydronic"),
    )
    return ProjectModel.model_validate_json(canonical_json(fatto))


def test_il_ritorno_della_serpentina_e_ritorno_anche_col_volano_in_serie() -> None:
    """**La prima tavola del PO uscita da claude.ai** (I-171): «mi pare abbia anche
    sbagliato il colore del ritorno dal serpentino». Il volano a due attacchi in serie
    sul ritorno ferma la camminata che risale dalla pompa di calore, e il ritorno della
    serpentina restava a `_eredita_da_monte`, che cambiava ruolo solo ai terminali: il
    bollitore non lo e', e la tratta ereditava la mandata che gli entra — rossa.

    Una serpentina scambia calore con un fluido che non e' quello della rete: chi ne
    esce e' ritorno. E tutto il ritorno, fino alla pompa di calore, resta ritorno."""
    progetto = _impianto_della_prova_del_po()
    primario = [trunk for trunk in tratte(progetto) if trunk.network_id == "primario"]
    classificate = classify_trunks(progetto, catalogo(), tratte(progetto))

    def ruolo_della(capo: tuple[str, str]) -> bool | None:
        (trunk,) = [
            trunk
            for trunk in primario
            if capo in {(ref.component_id, ref.port_id) for ref in (trunk.start, trunk.end)}
        ]
        return classificate[trunk.connection_ids].supply

    assert ruolo_della(("bollitore", "coil_out")) is False
    assert ruolo_della(("pavimento", "out")) is False
    assert ruolo_della(("bollitore", "coil_in")) is True
    assert ruolo_della(("pavimento", "in")) is True
    assert [key for key, flusso in classificate.items() if flusso.supply is None] == []
