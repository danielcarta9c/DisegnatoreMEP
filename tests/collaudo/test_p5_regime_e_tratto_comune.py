"""Collaudo indipendente — Pacchetto E: il regime della centrale e il tratto
comune (D-106), piu' la correzione C2 («la riserva si svuota da dove si riempie»).

Contratto (piano §3bis-E, DECISION_LOG D-106 e D-104, DOVE_VA parte terza):
- il regime e' DICHIARATO dal progettista, mai calcolato: le potenze scritte nel
  modello non spostano niente, e senza dichiarazione vale il corredo minimo;
- i due regimi non si mescolano mai sullo stesso impianto;
- con due o tre macchine in parallelo il corredo di rete — vaso, riempimento,
  manometro, defangatore — sta sul ritorno generale a monte della prima
  ripartizione, UNA volta; con una macchina sola coincide con la posa di sempre;
  dove il tratto comune non esiste esce un punto aperto, mai una scelta silenziosa;
- stesso impianto, stesso grafo: permutando l'ingresso (tubazioni + pezzi + reti)
  e invertendo l'ordine alfabetico dei file delle regole non cambia un pezzo,
  un attacco occupato ne' una fila — anche sugli impianti che le prove di
  sviluppo non usano;
- cio' che una macchina porta a bordo lo dichiara il catalogo, e una regola non
  aggiunge cio' che la macchina dichiara di avere; la dichiarazione
  contraddittoria non si carica;
- C2: il bollitore si svuota dall'ingresso freddo; il corredo sanitario di
  alimentazione va solo a chi si riempie dalla rete; il punto di riempimento
  dichiarato e' validato al caricamento;
- le regole sono dato: nessuna nomina un componente, le diciassette si caricano,
  e «tratto comune ⇒ una per rete» e' un vincolo del caricamento;
- i cinque grafi committati sono la rigenerazione corrente, e i conteggi del
  confronto per il PM sono veri sui documenti.

I quattro difetti trovati dal collaudo (il bordo macchina sordo per le regole
per attacco; il bordo altrui che spegneva la sicurezza del serbatoio; la firma
sbagliata del vaso sanitario; la fonte oltre il riscontro) sono stati corretti
lo stesso giorno: i loro segni `xfail` sono stati tolti e le prove ora devono
passare da verdi, come regressione.
"""

import importlib.util
import json
import re
import shutil
from collections import Counter
from collections.abc import Callable
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest
from helpers import (
    RULES_DIR,
    catalog,
    comp,
    load,
    naming,
    net,
    permuted,
    pipe,
    project,
    rules,
    symbols,
)
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.proposal import GapReason, RuleGap, RuleProposal
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleDefinition
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CAT = catalog()
REG = rules()

PROVE = [
    "prova-1-due-pdc-accumulo-combinato.json",
    "prova-2-pdc-deviatrice-acs.json",
    "prova-3-pdc-diretta-pavimento.json",
    "prova-4-ibrido-pdc-caldaia.json",
    "prova-5-cascata-tre-pdc.json",
]

# Le regole di ciascun regime si leggono DAI DATI, non da un elenco scritto qui:
# se domani una regola cambia regime, il collaudo la segue senza essere riscritto.
LARGE_ONLY = {r.id for r in REG.all() if r.when.plant_regime is PlantRegime.OVER_35_KW}
SMALL_ONLY = {r.id for r in REG.all() if r.when.plant_regime is PlantRegime.UP_TO_35_KW}

KIT_COMUNE = {
    "expansion-on-closed-circuit",
    "filling-unit-on-return",
    "gauge-where-the-plant-is-charged",
    "dirt-separation-before-what-it-would-ruin",
}

Saturo = tuple[ProjectModel, tuple[RuleProposal, ...], tuple[RuleGap, ...]]


def _two_separate_rings() -> ProjectModel:
    """Due generatori, ciascuno col proprio anello, sulla stessa rete.

    E' il caso in cui il tratto comune non esiste **davvero**: nessuna
    tubazione porta l'acqua di ritorno di tutti e due, e nessuna serve
    entrambi. Da non confondere con l'ibrido, dove il ritorno generale c'e'
    e la camminata lo raggiunge aprendosi sui rami."""
    return project(
        networks=[net("rete", "heating_water")],
        components=[
            comp("gen-a", "heat-pump-air-water"),
            comp("term-a", "radiator"),
            comp("gen-b", "heat-pump-air-water"),
            comp("term-b", "radiator"),
        ],
        connections=[
            pipe("ma", "rete", ("gen-a", "water_supply"), ("term-a", "in")),
            pipe("ra", "rete", ("term-a", "out"), ("gen-a", "water_return")),
            pipe("mb", "rete", ("gen-b", "water_supply"), ("term-b", "in")),
            pipe("rb", "rete", ("term-b", "out"), ("gen-b", "water_return")),
        ],
    )


@cache
def saturo(name: str, regime: PlantRegime | None = None) -> Saturo:
    """Una saturazione per impianto e regime, calcolata una volta sola."""
    model = load(name)
    if regime is not None:
        model = model.model_copy(update={"plant_regime": regime})
    done, applied, gaps = saturate(model, CAT, REG)
    return done, tuple(applied), tuple(gaps)


def shape(model: ProjectModel) -> tuple[frozenset[tuple[str, str]], frozenset[tuple[str, ...]]]:
    """Cio' che deve restare identico permutando l'ingresso: i pezzi e gli
    attacchi che ogni tubazione occupa. I nomi dei tronconi portano l'ordine
    del file e restano fuori; le adiacenze fra attacchi codificano le file."""
    pieces = frozenset((c.id, c.definition_id) for c in model.components)
    ends = frozenset(
        (
            c.endpoint_a.component_id,
            c.endpoint_a.port_id,
            c.endpoint_b.component_id,
            c.endpoint_b.port_id,
            c.network_id,
        )
        for c in model.connections
    )
    return pieces, ends


def doctored(definition_id: str, **updates: object) -> ComponentRegistry:
    """Il catalogo vero con UNA voce alterata: la prova cambia i dati, mai i file."""
    definitions = [
        item.model_copy(update=dict(updates)) if item.id == definition_id else item
        for item in CAT.all()
    ]
    return ComponentRegistry(definitions, symbols=symbols())


def fila(model: ProjectModel, start: str, port: str, stop: str) -> list[str]:
    """I pezzi sul percorso da un attacco fino a un pezzo fermo, in ordine.

    Cammina lungo i soli attacchi del flusso: gli stacchi (attacchi di servizio
    e bracci dei raccordi) restano fuori, come per chi legge il grafo. E' il
    modo del collaudo di leggere una fila senza fidarsi dell'assemblatore."""
    defs = {c.id: CAT.get(c.definition_id) for c in model.components}
    run_conns: dict[str, list[ConnectionModel]] = {}
    by_port: dict[tuple[str, str], ConnectionModel] = {}
    for c in model.connections:
        for ref in (c.endpoint_a, c.endpoint_b):
            port_def = next(p for p in defs[ref.component_id].ports if p.id == ref.port_id)
            if not port_def.off_the_run:
                run_conns.setdefault(ref.component_id, []).append(c)
                by_port[(ref.component_id, ref.port_id)] = c
    edge = by_port[(start, port)]
    current = start
    found: list[str] = []
    for _ in range(100):
        a, b = edge.endpoint_a, edge.endpoint_b
        other = b if a.component_id == current else a
        if other.component_id == stop:
            return found
        found.append(other.component_id)
        onward = [c for c in run_conns[other.component_id] if c is not edge]
        assert len(onward) == 1, (
            f"la fila da {start} si biforca su {other.component_id} prima di {stop}"
        )
        current, edge = other.component_id, onward[0]
    raise AssertionError(f"fila troppo lunga da {start}.{port}")


def functions_of(model: ProjectModel, component_id: str) -> frozenset[str]:
    definition_id = next(c.definition_id for c in model.components if c.id == component_id)
    return frozenset(CAT.get(definition_id).functions)


def hanging_functions(model: ProjectModel, holder_id: str) -> frozenset[str]:
    """Le funzioni dell'INTERA catena appesa allo stacco di un pezzo.

    Uno stacco ha la propria fila (D-094): dal braccio del raccordo puo' venire
    prima la valvola e poi il vaso. Guardare il solo primo pezzo direbbe che il
    vaso non c'e'."""
    touching: dict[str, list[ConnectionModel]] = {}
    for c in model.connections:
        for ref in (c.endpoint_a, c.endpoint_b):
            touching.setdefault(ref.component_id, []).append(c)
    edge = next(
        (
            c
            for c in model.connections
            if c.id.startswith("stub-")
            and holder_id in (c.endpoint_a.component_id, c.endpoint_b.component_id)
        ),
        None,
    )
    if edge is None:
        return frozenset()
    found: set[str] = set()
    current = holder_id
    for _ in range(20):
        a, b = edge.endpoint_a, edge.endpoint_b
        other = b if a.component_id == current else a
        found |= functions_of(model, other.component_id)
        onward = [c for c in touching[other.component_id] if c is not edge]
        if len(onward) != 1:
            return frozenset(found)
        current, edge = other.component_id, onward[0]
    raise AssertionError(f"catena dello stacco troppo lunga da {holder_id}")


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# 1. Il regime: dichiarato, mai calcolato; i due regimi non si mescolano
# ---------------------------------------------------------------------------


def test_le_potenze_scritte_nel_modello_non_spostano_il_regime() -> None:
    """D-104: la taglia non la decide la skill, nemmeno sommando le potenze.

    Prova dai dati: si scrivono 500 kW su OGNI pezzo dell'impianto 1 e il
    corredo resta quello minimo — se da qualche parte una somma decidesse il
    regime, qui scatterebbe il corredo grande."""
    base = load(PROVE[0]).model_copy(update={"plant_regime": None})
    heavy = base.model_copy(
        update={
            "components": [
                c.model_copy(update={"properties": {"power_kw": 500.0}})
                for c in base.components
            ]
        }
    )
    _, applied, _ = saturate(heavy, CAT, REG)
    fired = {p.rule_id for p in applied}
    assert not fired & LARGE_ONLY
    assert fired & SMALL_ONLY
    _, base_applied, _ = saturate(base, CAT, REG)
    assert fired == {p.rule_id for p in base_applied}


def test_senza_dichiarazione_vale_il_corredo_minimo_su_tutti_e_cinque() -> None:
    """Il default di D-106 e' il corredo minimo, e non e' un terzo regime: un
    impianto **senza** dichiarazione esce IDENTICO a uno dichiarato piccolo.

    Dal 7 agosto i cinque impianti il regime lo dichiarano — si legge dalle
    potenze che il testo da' — quindi il caso «non dichiarato» si costruisce
    qui, togliendo la dichiarazione: e' la proprieta' a contare, non quale
    file oggi la porti."""
    for name in PROVE:
        stripped = load(name).model_copy(update={"plant_regime": None})
        undeclared = saturate(stripped, CAT, REG)
        declared = saturate(
            stripped.model_copy(update={"plant_regime": PlantRegime.UP_TO_35_KW}),
            CAT,
            REG,
        )
        assert not {p.rule_id for p in undeclared[1]} & LARGE_ONLY, name
        assert shape(undeclared[0]) == shape(declared[0]), name
        assert {g.key for g in undeclared[2]} == {g.key for g in declared[2]}, name


def test_i_due_regimi_non_parlano_mai_insieme() -> None:
    """D-106: i due regimi non si mescolano sullo stesso impianto. Su cinque
    impianti e tre dichiarazioni, mai una regola di ciascun regime insieme."""
    assert LARGE_ONLY and SMALL_ONLY
    for name in PROVE:
        for regime in (None, PlantRegime.UP_TO_35_KW, PlantRegime.OVER_35_KW):
            _, applied, _ = saturo(name, regime)
            fired = {p.rule_id for p in applied}
            assert not (fired & LARGE_ONLY and fired & SMALL_ONLY), (name, regime)


def test_un_regime_che_non_esiste_non_si_carica() -> None:
    """Non c'e' un modo di dichiarare un terzo regime o tutti e due: il campo
    accetta le sole due voci di D-106, e il resto muore al confine."""
    payload = load(PROVE[0]).model_dump(mode="json")
    payload["plant_regime"] = "trentaquattro_kw_e_mezzo"
    with pytest.raises(ValidationError):
        ProjectModel.model_validate(payload)


def test_dichiarare_il_regime_grande_scambia_il_corredo_sulla_cascata() -> None:
    """La promessa del confronto al PM, verificata: dichiarata grande, la
    cascata riprende sicurezza e termometro per macchina e il separatore
    d'aria sulla mandata generale, a valle dell'ultima confluenza."""
    _, applied, gaps = saturo(PROVE[4], PlantRegime.OVER_35_KW)
    fired = Counter(p.rule_id for p in applied)
    assert fired["safety-relief-where-heat-enters-the-water"] == 3
    assert fired["flow-temperature-where-heat-enters-the-water"] == 3
    assert fired["air-release-where-the-water-is-hottest"] == 1
    assert not {p.rule_id for p in applied} & SMALL_ONLY
    separator = next(
        p for p in applied if p.rule_id == "air-release-where-the-water-is-hottest"
    )
    assert (separator.anchor.component_id, separator.anchor.port_id) == (
        "cascata-mandata-b",
        "b",
    ), "il separatore deve stare dove le tre mandate sono gia' diventate una"


# ---------------------------------------------------------------------------
# 2. Il tratto comune: una volta, a monte della prima ripartizione
# ---------------------------------------------------------------------------


def test_con_due_macchine_il_corredo_sta_a_monte_della_ripartizione_una_volta() -> None:
    """Impianto 1: vaso, riempimento, manometro e defangatore stanno fra
    l'accumulo e la ripartizione verso le due macchine — mai sul ramo di una
    sola — e ciascuno UNA volta. La fila si rilegge camminando, non fidandosi
    dell'assemblatore."""
    done, applied, _ = saturo(PROVE[0])
    kit = [p for p in applied if p.rule_id in KIT_COMUNE]
    assert Counter(p.rule_id for p in kit) == dict.fromkeys(KIT_COMUNE, 1)
    for p in kit:
        assert (p.anchor.component_id, p.anchor.port_id) == ("collettore-ritorno", "a"), p.rule_id

    corridor = fila(done, "accumulo", "primary_out", "collettore-ritorno")
    on_corridor = {f for cid in corridor for f in functions_of(done, cid)} | {
        f for cid in corridor for f in hanging_functions(done, cid)
    }
    assert {"expansion", "filling", "pressure_measurement", "sludge_separation"} <= on_corridor

    for branch_port, machine in (("b", "pdc-master"), ("c", "pdc-slave")):
        branch = fila(done, "collettore-ritorno", branch_port, machine)
        on_branch = {f for cid in branch for f in functions_of(done, cid)} | {
            f for cid in branch for f in hanging_functions(done, cid)
        }
        assert not on_branch & {"expansion", "filling", "pressure_measurement", "sludge_separation"}, (
            f"il corredo di rete e' finito sul ramo di {machine}"
        )
    assert validate_project(done, CAT).ok


def test_con_tre_macchine_il_corredo_sta_sul_ritorno_generale_della_cascata() -> None:
    """Impianto 5: il caso per cui la correzione esiste. Corredo UNA volta sul
    tratto che raccoglie tutta l'acqua, prima della prima ripartizione della
    cascata; un filtro a Y per macchina, sul suo ritorno; niente filtri ai
    circolatori."""
    done, applied, _ = saturo(PROVE[4])
    kit = [p for p in applied if p.rule_id in KIT_COMUNE]
    assert Counter(p.rule_id for p in kit) == dict.fromkeys(KIT_COMUNE, 1)
    for p in kit:
        assert (p.anchor.component_id, p.anchor.port_id) == ("cascata-ritorno-a", "a"), p.rule_id

    filters = [p for p in applied if p.rule_id == "debris-guard-before-what-it-would-ruin"]
    assert sorted((p.anchor.component_id, p.anchor.port_id) for p in filters) == [
        ("pdc-1", "water_return"),
        ("pdc-2", "water_return"),
        ("pdc-3", "water_return"),
    ]
    assert all(p.network_id == "primario" for p in filters), "filtrazione solo sul primario"
    circulators = {c.id for c in done.components if "circulation" in functions_of(done, c.id)}
    assert not any(p.anchor.component_id in circulators for p in applied if p.rule_id in KIT_COMUNE | {"debris-guard-before-what-it-would-ruin"})
    assert validate_project(done, CAT).ok


def test_con_una_macchina_sola_la_posa_coincide_con_quella_di_sempre() -> None:
    """Un impianto sintetico che le prove di sviluppo non usano: una macchina,
    un volano, un'utenza. Il tratto comune di un solo generatore comincia sul
    suo stesso ritorno: il corredo si posa li', come si e' sempre fatto."""
    single = project(
        networks=[net("primario", "heating_water"), net("secondario", "heating_water")],
        components=[
            comp("pdc", "heat-pump-air-water"),
            comp("volano", "buffer-four-port"),
            comp("utenza", "fan-coil"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc", "water_supply"), ("volano", "primary_in")),
            pipe("r1", "primario", ("volano", "primary_out"), ("pdc", "water_return")),
            pipe("s1", "secondario", ("volano", "secondary_out"), ("utenza", "in")),
            pipe("s2", "secondario", ("utenza", "out"), ("volano", "secondary_in")),
        ],
    )
    done, applied, gaps = saturate(single, CAT, REG)
    kit = [p for p in applied if p.rule_id in KIT_COMUNE]
    assert Counter(p.rule_id for p in kit) == dict.fromkeys(KIT_COMUNE, 1)
    for p in kit:
        assert (p.anchor.component_id, p.anchor.port_id) == ("pdc", "water_return"), p.rule_id
    assert not gaps
    assert validate_project(done, CAT).ok


def test_l_ibrido_non_ha_un_ritorno_generale_e_apre_il_punto() -> None:
    """Impianto 4, l'ibrido — e qui il contratto di questo collaudo vince su
    una correzione successiva che gli andava contro.

    La correzione del 7 agosto sera affermava che l'ibrido un ritorno generale
    ce l'ha, e che il corredo va sul tratto fra il volume tecnico e la
    ripartizione. **Non e' vero, ed e' misurabile:** la caldaia manda alla
    deviatrice, che sdoppia; il ramo del sanitario passa per lo scambiatore e
    rientra in `ritorno-caldaia`, **a valle** del collettore di ritorno. Tolto
    quel tratto, il circuito della caldaia si chiude lo stesso — quindi quel
    tratto la sua acqua non la porta, e il defangatore che ci si posava sopra
    non proteggeva la caldaia, che e' la ragione per cui esiste.

    Il collaudo indipendente delle correzioni lo ha inchiodato (DIFETTO 1) e
    aveva gia' osservato che «prima della correzione erano quattro punti
    aperti». La risposta giusta e' quella: nessuna scelta silenziosa, quattro
    punti aperti con la ragione vera, e la decisione torna al progettista."""
    done, applied, gaps = saturo(PROVE[3])
    open_points = {g.rule_id: g for g in gaps if g.rule_id in KIT_COMUNE}
    assert set(open_points) == KIT_COMUNE
    for gap in open_points.values():
        assert gap.reason is GapReason.NO_COMMON_RUN, gap.rule_id
    assert not any(p.rule_id in KIT_COMUNE for p in applied)
    banned = {"expansion", "filling", "pressure_measurement", "sludge_separation"}
    for component in done.components:
        assert not functions_of(done, component.id) & banned, (
            f"{component.id}: il corredo e' stato posato su un ramo scelto in silenzio"
        )


def test_dove_il_tratto_comune_non_esiste_davvero_esce_un_punto_aperto() -> None:
    """Due generatori, due anelli separati sulla stessa rete: nessuna
    tubazione porta tutta l'acqua che torna, e non c'e' nessun tratto che le
    serva entrambe. Qui il corredo non si posa su un anello scelto in
    silenzio — le quattro regole aprono un punto aperto con la ragione
    giusta."""
    done, applied, gaps = saturate(_two_separate_rings(), CAT, REG)
    open_points = {g.rule_id: g for g in gaps}
    assert set(open_points) == KIT_COMUNE
    for gap in open_points.values():
        assert gap.reason is GapReason.NO_COMMON_RUN, gap.rule_id
    assert not any(p.rule_id in KIT_COMUNE for p in applied)
    banned = {"expansion", "filling", "pressure_measurement", "sludge_separation"}
    for component in done.components:
        assert not functions_of(done, component.id) & banned, (
            f"{component.id}: il corredo e' stato posato su un anello scelto in silenzio"
        )


# ---------------------------------------------------------------------------
# 3. Determinismo: ne' l'ordine del file, ne' i nomi dei file delle regole
# ---------------------------------------------------------------------------


def test_permutare_l_ingresso_non_cambia_il_grafo_completato() -> None:
    """Stesso impianto scritto in un altro ordine — tubazioni, pezzi E reti
    insieme — stesso completamento: pezzi, attacchi occupati, file per tratta,
    punti aperti. Sugli impianti che la prova di sviluppo non usa (2, 4, 5),
    compreso quello coi punti aperti."""
    for name in (PROVE[1], PROVE[3], PROVE[4]):
        done, _, gaps = saturo(name)
        reference = shape(done)
        reference_gaps = {g.key for g in gaps}
        base = load(name)
        for seed in (11, 47, 101):
            again, _, gaps_again = saturate(permuted(base, seed), CAT, REG)
            assert shape(again) == reference, (name, seed)
            assert {g.key for g in gaps_again} == reference_gaps, (name, seed)


def test_l_ordine_alfabetico_dei_file_delle_regole_non_decide_niente(tmp_path: Path) -> None:
    """Il difetto c'era (D-093) ed e' dichiarato chiuso: si rinominano TUTTI i
    file delle regole invertendo l'ordine alfabetico e si pretende lo stesso
    esito — anche sull'ibrido coi punti aperti e sulla cascata, che le prove
    esistenti non usano per questa proprieta'."""
    names = sorted(p.name for p in RULES_DIR.glob("*.json"))
    for index, name in enumerate(names):
        shutil.copy(RULES_DIR / name, tmp_path / f"{chr(ord('z') - index)}-{name}")
    reversed_registry = RuleRegistry.from_directory(tmp_path)
    assert [r.id for r in reversed_registry.all()] == [
        r.id for r in reversed(REG.all())
    ], "la rinomina deve davvero invertire l'ordine di caricamento"
    for name in (PROVE[1], PROVE[3], PROVE[4]):
        done, _, gaps = saturo(name)
        again, _, gaps_again = saturate(load(name), CAT, reversed_registry)
        assert shape(again) == shape(done), name
        assert {g.key for g in gaps_again} == {g.key for g in gaps}, name


# ---------------------------------------------------------------------------
# 4. Il bordo macchina: cio' che e' dichiarato a bordo non si disegna
# ---------------------------------------------------------------------------


def test_il_corredo_di_rete_dichiarato_a_bordo_non_si_aggiunge() -> None:
    """Criterio 4, provato dai dati sulle regole di rete: una macchina che
    dichiara a bordo defangazione, riempimento, manometro e vaso non li riceve
    dall'esterno; sul catalogo vero, che dichiara il solo circolatore, escono."""
    doctored_cat = doctored(
        "heat-pump-air-water",
        carries_on_board=["circulation", "sludge_separation", "filling", "pressure_measurement", "expansion"],
    )
    found = evaluate(load(PROVE[1]), doctored_cat, REG)
    fired = {p.rule_id for p in found.proposals if p.network_id == "primario"}
    assert not fired & KIT_COMUNE
    true_found = evaluate(load(PROVE[1]), CAT, REG)
    assert {p.rule_id for p in true_found.proposals if p.network_id == "primario"} >= KIT_COMUNE


def test_la_filtrazione_a_bordo_fa_tacere_il_filtro_a_y() -> None:
    """«Dichiara a bordo una funzione e guarda la regola tacere» (§3bis-E)."""
    doctored_cat = doctored("heat-pump-air-water", carries_on_board=["circulation", "filtration"])
    found = evaluate(load(PROVE[1]), doctored_cat, REG)
    assert not any(
        p.rule_id == "debris-guard-before-what-it-would-ruin" for p in found.proposals
    ), "la macchina dichiara il filtro a bordo e la regola lo aggiunge lo stesso"


def test_termometro_e_sicurezza_a_bordo_fanno_tacere_le_regole_grandi() -> None:
    """La regola generale della Raccolta R letta in DOVE_VA parte prima."""
    doctored_cat = doctored(
        "heat-pump-air-water",
        carries_on_board=["circulation", "temperature_measurement", "safety"],
    )
    model = load(PROVE[1]).model_copy(update={"plant_regime": PlantRegime.OVER_35_KW})
    found = evaluate(model, doctored_cat, REG)
    fired = {p.rule_id for p in found.proposals}
    assert "flow-temperature-where-heat-enters-the-water" not in fired
    assert "safety-relief-where-heat-enters-the-water" not in fired


def test_la_sicurezza_del_serbatoio_resta_anche_se_la_macchina_ha_la_sua() -> None:
    """D-106: «le macchine la portano gia' a bordo, e la sicurezza esterna
    della centrale e' quella del serbatoio» — e' la rationale della regola."""
    doctored_cat = doctored("heat-pump-air-water", carries_on_board=["circulation", "safety"])
    found = evaluate(load(PROVE[1]), doctored_cat, REG)
    assert any(
        p.rule_id == "safety-relief-on-the-stored-volume" for p in found.proposals
    ), "la sicurezza del serbatoio e' sparita perche' la macchina dichiara la propria"


def test_la_dichiarazione_contraddittoria_non_si_carica() -> None:
    """Stessa funzione come mestiere e come bordo: una delle due e' falsa, e il
    caricamento deve fermarla — insieme ai doppioni e ai nomi vuoti."""
    payload = CAT.get("heat-pump-air-water").model_dump(mode="json")
    payload["carries_on_board"] = ["heat_generation"]
    with pytest.raises(ValidationError, match="mestiere"):
        ComponentDefinition.model_validate(payload)
    payload["carries_on_board"] = ["circulation", "circulation"]
    with pytest.raises(ValidationError, match="due volte"):
        ComponentDefinition.model_validate(payload)
    payload["carries_on_board"] = ["   "]
    with pytest.raises(ValidationError, match="senza nome"):
        ComponentDefinition.model_validate(payload)


# ---------------------------------------------------------------------------
# 5. C2: la riserva si svuota da dove si riempie, e il corredo va a chi spetta
# ---------------------------------------------------------------------------


def test_il_corredo_sanitario_va_solo_a_chi_si_riempie_dalla_rete() -> None:
    """L'accumulo combinato scalda l'acqua sanitaria in un serpentino
    istantaneo: tocca la rete fredda ma non se ne riempie la riserva, e il
    corredo di alimentazione — gruppo di sicurezza, ritegno, vaso della
    riserva — NON gli spetta. Al bollitore, che dichiara di riempirsi dal
    freddo, spetta tutto."""
    corredo = {
        "safety-group-on-the-stored-volume",
        "dhw-check-on-cold-inlet",
        "expansion-on-the-stored-volume-feed",
    }
    _, applied_combinato, gaps_combinato = saturo(PROVE[0])
    assert not any(p.rule_id in corredo for p in applied_combinato)
    assert not any(g.rule_id in corredo for g in gaps_combinato), (
        "il corredo che non spetta non deve nemmeno uscire come punto aperto"
    )
    _, applied_bollitore, _ = saturo(PROVE[1])
    on_cold = {p.rule_id for p in applied_bollitore if p.network_id == "fredda"}
    assert corredo <= on_cold


def test_lo_scarico_del_bollitore_sta_sul_freddo_e_dal_lato_del_serbatoio() -> None:
    """Piu' duro della prova gia' esistente: oltre alla rete giusta, si
    verifica che fra la derivazione dello scarico e il bollitore non ci sia
    nulla che chiude — a organo chiuso, uno scarico di la' dalla valvola
    svuoterebbe la tratta sbagliata."""
    done, _, _ = saturo(PROVE[1])
    drains = [
        c for c in done.components
        if c.definition_id.startswith("drain-connection") and "bollitore" in c.id
    ]
    assert len(drains) == 1
    tee_id = f"tee-{drains[0].id}"
    corridoio = fila(done, "bollitore", "cold_in", "acquedotto")
    assert tee_id in corridoio
    before_the_tee = corridoio[: corridoio.index(tee_id)]
    closable = {"isolation", "isolation_locked_open"}
    assert not any(functions_of(done, cid) & closable for cid in before_the_tee), (
        "c'e' un organo di chiusura fra lo scarico e il serbatoio"
    )
    # E lo scarico dell'accumulo tecnico resta sul SUO attacco dedicato: il
    # volano si riempie dal circuito e non dichiara un punto di riempimento.
    volano_drains = [
        c for c in done.components
        if c.definition_id.startswith("drain-connection") and "volano" in c.id
    ]
    assert len(volano_drains) == 1
    stub = next(c for c in done.connections if c.id == f"stub-{volano_drains[0].id}")
    holders = {
        (c.component_id, c.port_id) for c in (stub.endpoint_a, stub.endpoint_b)
    }
    assert ("volano", "drain") in holders


def test_sfogo_e_sicurezza_stanno_sul_serbatoio_e_stop() -> None:
    """D-106 nel regime piccolo: lo sfogo sull'attacco dedicato del serbatoio,
    la sicurezza attaccata al serbatoio senza nulla di chiudibile in mezzo,
    UNA ciascuno anche se il serbatoio sta su due reti; niente separatore
    d'aria e niente termometro aggiunti, su nessuno dei cinque impianti."""
    done, applied, _ = saturo(PROVE[0])
    vents = [p for p in applied if p.rule_id == "air-vent-on-the-stored-volume"]
    assert len(vents) == 1
    assert vents[0].anchor.component_id == "accumulo"
    assert vents[0].service_port == "vent"
    safeties = [p for p in applied if p.rule_id == "safety-relief-on-the-stored-volume"]
    assert len(safeties) == 1
    assert safeties[0].anchor.component_id == "accumulo"
    # La derivazione della sicurezza e' ADIACENTE all'accumulo: nulla in mezzo.
    neighbours = fila(done, "accumulo", "primary_in", "collettore-mandata")
    assert neighbours, "nessun pezzo fra l'accumulo e la confluenza?"
    first = neighbours[0]
    assert "safety" in hanging_functions(done, first), (
        f"fra la sicurezza e il serbatoio c'e' {first}"
    )
    # Su tutti e cinque, **nel regime piccolo**: separatore e termometro non
    # compaiono. L'impianto 5 il regime grande lo dichiara — tre macchine da
    # 35 kW — e li' quei due pezzi ci vanno, quindi lo si guarda nel regime
    # di cui parla questa regola, non in quello che il file dichiara.
    for name in PROVE:
        completed, _, _ = saturo(name, PlantRegime.UP_TO_35_KW)
        for component in completed.components:
            assert "air_separation" not in functions_of(completed, component.id), name
            assert "temperature_measurement" not in functions_of(completed, component.id), name


def test_il_punto_di_riempimento_dichiarato_e_validato_al_caricamento() -> None:
    """C2: un punto di riempimento sbagliato manderebbe lo scarico sulla
    tubazione sbagliata, quindi muore al caricamento: attacco inesistente,
    stacco, uscita, o riserva che non c'e' — tutti respinti."""
    payload = CAT.get("dhw-cylinder").model_dump(mode="json")
    for wrong, why in (
        ("bocchello_fantasma", "non e' un suo attacco"),
        ("probe", "stacco"),
        ("dhw_out", "uscita"),
    ):
        broken = dict(payload)
        broken["fills_from"] = wrong
        with pytest.raises(ValidationError, match=why):
            ComponentDefinition.model_validate(broken)
    without_reserve = dict(payload)
    without_reserve["traits"] = [
        t for t in payload["traits"] if t != "holds_its_own_volume"
    ]
    without_reserve["stored_medium"] = None
    with pytest.raises(ValidationError, match="riserva"):
        ComponentDefinition.model_validate(without_reserve)


def test_il_vaso_sanitario_e_firmato_dalla_regola_dell_alimentazione() -> None:
    """Chi firma il vaso della riserva sanitaria deve essere la regola del
    corredo di alimentazione, non quella del circuito chiuso."""
    found = evaluate(load(PROVE[2]), CAT, REG)
    on_cold = [
        p for p in found.proposals
        if p.network_id == "fredda" and "expansion" in p.definition_id
    ]
    assert len(on_cold) == 1
    assert on_cold[0].rule_id == "expansion-on-the-stored-volume-feed", (
        f"il vaso sanitario e' firmato da {on_cold[0].rule_id}"
    )


# ---------------------------------------------------------------------------
# 6. Le regole come dato
# ---------------------------------------------------------------------------


def test_le_diciassette_regole_si_caricano_e_nessuna_nomina_un_componente() -> None:
    """D-069: le condizioni parlano di proprieta', funzioni, domini e fluidi.
    Nessun valore in when, then, ordering o satisfied_by puo' essere
    l'identificativo di una voce di catalogo."""
    assert len(REG.all()) == 17
    REG.cross_check(CAT)
    catalog_ids = {d.id for d in CAT.all()}

    def strings_in(payload: object) -> set[str]:
        if isinstance(payload, str):
            return {payload}
        if isinstance(payload, dict):
            found: set[str] = set()
            for key, value in payload.items():
                found |= strings_in(key) | strings_in(value)
            return found
        if isinstance(payload, list):
            found = set()
            for item in payload:
                found |= strings_in(item)
            return found
        return set()

    for rule in REG.all():
        dumped = rule.model_dump(mode="json")
        tokens: set[str] = set()
        for field in ("when", "then", "ordering", "satisfied_by", "cardinality", "category"):
            tokens |= strings_in(dumped[field])
        named = tokens & catalog_ids
        assert not named, f"{rule.id} nomina componenti: {sorted(named)}"


def test_tratto_comune_impone_una_per_rete_al_caricamento(tmp_path: Path) -> None:
    """Una regola sul tratto comune con cardinalita' diversa da «una per rete»
    dichiara due cose che non stanno insieme: muore validando, e dal file
    muore nominando il file."""
    payload = next(r for r in REG.all() if r.id == "expansion-on-closed-circuit").model_dump(
        mode="json"
    )
    payload["cardinality"] = "per_component"
    with pytest.raises(ValidationError, match="tratto comune"):
        RuleDefinition.model_validate(payload)
    (tmp_path / "regola-storta.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )
    with pytest.raises(RuleError, match="regola-storta"):
        RuleRegistry.from_directory(tmp_path)


# ---------------------------------------------------------------------------
# 7. I cinque grafi committati e il confronto per il PM
# ---------------------------------------------------------------------------


def test_i_cinque_grafi_committati_sono_la_rigenerazione_corrente() -> None:
    """Il documento pubblicato E' la rigenerazione: si ricostruisce ogni grafo
    in memoria — stessi generatori, senza scrivere niente — e si pretende il
    byte a byte con il file committato. Idem per i cinque impianti JSON."""
    plants_module = load_module(ROOT / "examples" / "prova" / "build_test_plants.py")
    plants = cast(dict[str, dict[str, object]], plants_module.PLANTS)
    for name, payload in plants.items():
        committed = (ROOT / "examples" / "prova" / f"{name}.json").read_text(encoding="utf-8")
        assert json.dumps(payload, ensure_ascii=False, indent=2) + "\n" == committed, name

    graph_module = load_module(ROOT / "examples" / "graph" / "build_plant_graph.py")
    build = cast(Callable[..., str], graph_module.build)
    for name in PROVE:
        done, _, gaps = saturo(name)
        text = build(done, CAT, naming(), list(gaps))
        committed_doc = (
            ROOT / "docs" / "prodotto" / "grafi-di-prova" / f"{Path(name).stem}.md"
        ).read_text(encoding="utf-8")
        assert text == committed_doc, f"{name}: il grafo committato non e' la rigenerazione"


def test_il_confronto_per_il_pm_dice_il_vero_sui_documenti() -> None:
    """Ogni conteggio «a N pezzi» del confronto deve essere vero due volte: sul
    modello completato e sulle righe dei nodi del documento committato. E i
    «quattro punti aperti» dell'ibrido devono essere davvero quattro. (I
    conteggi «da N», che vivono nella storia di ieri, sono stati riscontrati
    dal collaudo sul commit dei grafi vecchi: 59, 58, 55, 68, 105.)"""
    confronto = (
        ROOT / "docs" / "prodotto" / "grafi-di-prova" / "CONFRONTO-2026-08-07.md"
    ).read_text(encoding="utf-8")
    claimed = [int(m) for m in re.findall(r"da \d+ a (\d+) pezzi", confronto)]
    assert len(claimed) == 5
    for name, expected in zip(PROVE, claimed, strict=True):
        done, _, gaps = saturo(name)
        assert len(done.components) == expected, name
        doc = (
            ROOT / "docs" / "prodotto" / "grafi-di-prova" / f"{Path(name).stem}.md"
        ).read_text(encoding="utf-8")
        rows = [
            line for line in doc.splitlines() if re.match(r"^\| [A-Z]+\.[0-9]", line)
        ]
        assert len(rows) == expected, f"{name}: il documento non ha {expected} nodi"
    # La frase sui punti aperti dev'essere vera impianto per impianto. Il
    # 7 agosto diceva «nessuno dei cinque»: il collaudo ha misurato che
    # sull'ibrido era falsa, e il documento e' stato corretto invece che
    # lasciato a raccontare una cosa che il PM non poteva verificare.
    assert "Quattro dei cinque non hanno punti aperti" in confronto
    assert "L'ibrido ne ha quattro" in confronto
    for name in PROVE:
        _, _, found = saturo(name)
        if name == PROVE[3]:
            assert {g.rule_id for g in found} == KIT_COMUNE, name
            continue
        assert not found, (name, [(g.rule_id, g.reason.value) for g in found])
    # Il regime che il confronto dichiara per ciascun impianto dev'essere
    # quello scritto nel modello: la tabella del documento e i cinque file
    # non possono divergere.
    rows = re.findall(r"^\| ([1-5]) \|[^|]+\| ([^|]+)\|", confronto, flags=re.M)
    assert len(rows) == 5, rows
    for row, name in zip(rows, PROVE, strict=True):
        index, spoken = row[0], row[1]
        declared = load(name).plant_regime
        assert declared is not None, name
        wants_large = "sopra" in spoken.lower()
        assert (declared is PlantRegime.OVER_35_KW) is wants_large, (index, spoken)
