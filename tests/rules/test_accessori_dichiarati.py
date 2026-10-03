"""Gli accessori che il progettista mette in un posto preciso (REL-009, I-193).

Sul primo caso reale (I-191) il progettista descrive il costruito: lo sfiato con la valvola
a sfera sul ritorno di ogni pompa di calore, il ritegno sull'uscita, gli sfiati sui volani,
manometro e termometro sui montanti delle pompe di macrozona, il riduttore sull'acqua
fredda, le valvole manuali sulle due uscite di ogni collettore d'appartamento. Capire §5 li
scrive dove lui dice, e le regole **non li duplicano**: dove una regola vuole quel mestiere
su quel tratto, lo trova.
"""

# categoria: difende il contenuto — I-193, il costruito dichiarato dal progettista non si raddoppia

import json
from collections import Counter
from functools import cache
from pathlib import Path
from typing import Any

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import Saturation, saturation
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CASO = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-1" / "grafo-prima-stesura.json"
ISTRUZIONI = ROOT / "skill" / "capire" / "ISTRUZIONI.md"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(ROOT / "rules" / "hydronic")
    registry.cross_check(catalog())
    return registry


def _pezzo(grafo: dict[str, Any], ident: str, definizione: str) -> None:
    grafo["components"].append({"id": ident, "definition_id": definizione, "tag": None, "properties": {}})


def _in_linea(grafo: dict[str, Any], tubo: dict[str, Any], ident: str, definizione: str) -> None:
    """Capire §5, «in linea»: la tubazione si spezza, entra in `a` ed esce da `b`."""
    _pezzo(grafo, ident, definizione)
    seconda = {**tubo, "id": f"{tubo['id']}-{ident}", "endpoint_a": {"component_id": ident, "port_id": "b"}}
    tubo["endpoint_b"] = {"component_id": ident, "port_id": "a"}
    grafo["connections"].append(seconda)


def _stacco(grafo: dict[str, Any], rete: str, da: tuple[str, str], catena: list[tuple[str, str]]) -> None:
    """Capire §5, «appeso»: una tubazione corta dal braccio, pezzo dopo pezzo."""
    for ident, definizione in catena:
        _pezzo(grafo, ident, definizione)
        grafo["connections"].append(
            {
                "id": f"stub-{ident}",
                "network_id": rete,
                "endpoint_a": {"component_id": da[0], "port_id": da[1]},
                "endpoint_b": {"component_id": ident, "port_id": "a"},
                "properties": {},
            }
        )
        da = (ident, "b")


def _uscente(grafo: dict[str, Any], pezzo: str, porta: str) -> dict[str, Any]:
    return next(
        item for item in grafo["connections"] if item["endpoint_a"] == {"component_id": pezzo, "port_id": porta}
    )


def _entrante(grafo: dict[str, Any], pezzo: str, porta: str) -> dict[str, Any]:
    return next(
        item for item in grafo["connections"] if item["endpoint_b"] == {"component_id": pezzo, "port_id": porta}
    )


@cache
def _dichiarato() -> ProjectModel:
    grafo = json.loads(CASO.read_text(encoding="utf-8"))
    for zona, quanti in ((1, 3), (2, 5)):
        for n in range(1, quanti + 1):
            for uscita, terminale in (("out_1", "fc"), ("out_2", "rad")):
                _in_linea(grafo, _uscente(grafo, f"coll-mz{zona}-{n}", uscita), f"vi-{terminale}-mz{zona}-{n}", "valve-isolation")
    pompe = [item["id"] for item in grafo["components"] if item["id"].startswith("pdc-")]
    for pompa in pompe:
        _in_linea(grafo, _uscente(grafo, pompa, "water_supply"), f"rit-{pompa}", "valve-check")
        ritorno = _entrante(grafo, pompa, "water_return")
        _in_linea(grafo, ritorno, f"t-sfiato-{pompa}", "tee-branch")
        _stacco(grafo, ritorno["network_id"], (f"t-sfiato-{pompa}", "branch"),
                [(f"vs-sfiato-{pompa}", "valve-isolation"), (f"sfiato-{pompa}", "air-vent")])
    for volano, rete in (("volano-risc", "primario-risc"), ("volano-acs", "primario-acs")):
        _stacco(grafo, rete, (volano, "vent"), [(f"vs-sfiato-{volano}", "valve-isolation"), (f"sfiato-{volano}", "air-vent")])
    for zona in ("mz1", "mz2"):
        mandata = _uscente(grafo, f"pompa-{zona}", "b")
        _in_linea(grafo, mandata, f"t-man-{zona}", "tee-branch")
        _stacco(grafo, mandata["network_id"], (f"t-man-{zona}", "branch"), [(f"man-{zona}", "pressure-gauge")])
    _in_linea(grafo, _uscente(grafo, "acquedotto", "a"), "riduttore", "pressure-reducer")
    return ProjectModel.model_validate(grafo)


@cache
def _completo() -> Saturation:
    return saturation(_dichiarato(), catalog(), rules())


def test_il_grafo_con_il_costruito_dichiarato_regge() -> None:
    assert validate_project(_dichiarato(), catalog()).ok


def test_le_valvole_dichiarate_sulle_uscite_del_collettore_bastano_all_ingresso_dei_terminali() -> None:
    """T1, la meta' che il costruito risolve da solo: la valvola sull'uscita del
    collettore sta sul tratto che entra nel terminale, e la regola la trova. Quelle
    sull'uscita dei terminali restano, e si tolgono (I-192)."""
    posati = {item.id for item in _completo().model.components}
    assert not [item for item in posati if item.startswith(("valve-isolation-fc-", "valve-isolation-rad-")) and item.endswith("-in")]
    assert len([item for item in posati if item.startswith(("valve-isolation-fc-", "valve-isolation-rad-"))]) == 16


def test_nessun_pezzo_dichiarato_si_raddoppia() -> None:
    """Le regole non aggiungono un altro ritegno, sfiato o riduttore: dei pezzi
    dichiarati aggiungono solo il corredo di chi li porta — il rubinetto del manometro."""
    dichiarati = {item.id for item in _dichiarato().components} - {
        item["id"] for item in json.loads(CASO.read_text(encoding="utf-8"))["components"]
    }
    aggiunti = Counter(
        item.definition_id
        for item in _completo().model.components
        if item.id not in {c.id for c in _dichiarato().components}
    )
    for voce in ("valve-check", "air-vent", "pressure-reducer"):
        assert aggiunti[voce] == 0, voce
    appesi_ai_dichiarati = sorted(
        item.id for item in _completo().model.components if any(d in item.id for d in dichiarati) and item.id not in dichiarati
    )
    assert appesi_ai_dichiarati == ["valve-gauge-cock-3way-man-mz1-a", "valve-gauge-cock-3way-man-mz2-a"]


def test_lo_sfiato_sta_prima_del_filtro_come_sul_costruito() -> None:
    """Sul ritorno di ogni pompa: lo sfiato nel punto alto, prima dell'intercettazione
    e del filtro che le regole posano sull'attacco della macchina."""
    modello = _completo().model
    fila: list[str] = []
    pezzo = "ts-pr-3"
    for _ in range(6):
        pezzo = next(
            c.endpoint_b.component_id
            for c in modello.connections
            if c.endpoint_a.component_id == pezzo and (pezzo != "ts-pr-3" or c.endpoint_a.port_id == "c")
        )
        fila.append(pezzo)
        if pezzo == "pdc-r1":
            break
    assert fila == [
        "t-sfiato-pdc-r1",
        "valve-isolation-strainer-pdc-r1-water-return-a",
        "strainer-pdc-r1-water-return",
        "pdc-r1",
    ]


def test_le_istruzioni_dicono_quando_la_ferramenta_entra_nel_grafo() -> None:
    testo = ISTRUZIONI.read_text(encoding="utf-8")
    assert "**Entra, se il progettista la mette in un posto preciso** (I-193)" in testo
    assert "Le regole **non lo duplicano**" in testo
    assert "`\"altrove\": \"pezzo.attacco\"`" in testo
