"""Collaudo indipendente — Pacchetto 3: l'assemblatore (G4, D-093, D-094).

Contratto (piano §3-G4):
- la fila prodotta e' leggibile sul grafo scritto nodo per nodo;
- gli stacchi hanno la propria fila;
- l'ordine NON dipende dall'ordine alfabetico dei nomi dei file delle regole;
- su due regole incompatibili si ferma e NOMINA le due regole;
- deterministico: stesso grafo, stessa fila, anche su permutazioni;
- riordina SOLO cio' che le regole hanno aggiunto;
- ogni accessorio viaggia col proprio blocco di valvole;
- la sicurezza sta attaccata alla macchina senza nulla di chiudibile in mezzo;
- il defangatore lato impianto rispetto all'intercettazione;
- sul primario il termometro non finisce dopo un organo di chiusura.
"""

import json
from pathlib import Path

import pytest
from helpers import (
    RULES_DIR,
    catalog,
    comp,
    load,
    net,
    permuted,
    pipe,
    project,
    read,
    rules,
    rules_map,
)

from disegnatore_mep.assembly import AssemblyError, runs_of
from disegnatore_mep.assembly.runs import Piece
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleDefinition
from disegnatore_mep.validation.topology import validate_project

CAT = catalog()
REG = rules()
RMAP = rules_map(REG)

CLOSABLE = {"isolation", "isolation_locked_open"}


def _pdc_loop() -> ProjectModel:
    return project(
        networks=[net("primario", "heating_water")],
        components=[
            comp("pdc", "heat-pump-air-water"),
            comp("utenza", "fan-coil"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc", "water_supply"), ("utenza", "in")),
            pipe("r1", "primario", ("utenza", "out"), ("pdc", "water_return")),
        ],
    )


def _fila(
    model: ProjectModel, rmap: dict[str, RuleDefinition] = RMAP
) -> dict[tuple[str, str, str], tuple[str, ...]]:
    return {
        (r.head.component_id, r.tail.component_id, r.network_id): tuple(
            r.component_ids
        )
        for r in runs_of(model, CAT, rmap)
    }


def _run_from(
    model: ProjectModel, machine: str, port: str, rmap: dict[str, RuleDefinition] = RMAP
) -> list[Piece]:
    """La fila di una tratta letta a partire dalla macchina indicata."""
    for run in runs_of(model, CAT, rmap):
        if (run.head.component_id, run.head.port_id) == (machine, port):
            return list(run.pieces)
        if (run.tail.component_id, run.tail.port_id) == (machine, port):
            return list(reversed(run.pieces))
    raise AssertionError(f"nessuna tratta tocca {machine}.{port}")


def _rule_json(
    rule_id: str,
    function: str,
    placement: str,
    ordering: dict[str, object],
    when_extra: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "id": rule_id,
        "version": "1.0.0",
        "name": f"Regola di collaudo {rule_id}",
        "category": "recommended",
        "cardinality": "per_component",
        "when": {
            "network_domain": "hydronic",
            "anchor_has_function": "heat_generation",
            **(when_extra or {}),
        },
        "then": {
            "provides_function": function,
            "placement": placement,
            "inlet_port": "a",
            "outlet_port": "b",
        },
        "satisfied_by": {"scope": "on_the_attachment"},
        "ordering": ordering,
        "rationale": "Costruita apposta dal collaudo per verificare i vincoli.",
        "source": "collaudo indipendente",
    }


def _write_rules(directory: Path, payloads: list[dict[str, object]]) -> RuleRegistry:
    directory.mkdir(parents=True, exist_ok=True)
    for payload in payloads:
        (directory / f"{payload['id']}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
    return RuleRegistry.from_directory(directory)


# ---------------------------------------------------------------------------
# 1. La fila e' leggibile sul grafo scritto, e gli stacchi hanno la propria
# ---------------------------------------------------------------------------


def test_la_fila_si_legge_nodo_per_nodo_sul_grafo_scritto() -> None:
    done, _, _ = saturate(_pdc_loop(), CAT, REG)
    assert validate_project(done, CAT).ok
    graph = read(done, CAT)
    assert graph.unreached == ()
    assert graph.unread_pipes == ()
    assert graph.crossings == ()
    fila = _fila(done)
    assert fila, "nessuna tratta scritta"
    # Ogni pezzo mosso dalle regole compare in una e una sola tratta.
    seen = [cid for pieces in fila.values() for cid in pieces]
    assert len(seen) == len(set(seen))


def test_lo_stacco_del_vaso_ha_la_propria_fila_con_la_valvola_bloccabile() -> None:
    """La piccola catena dello stacco: braccio del raccordo → valvola
    bloccabile aperta → vaso. Sul percorso principale la valvola bloccabile
    non c'e'."""
    done, _, _ = saturate(_pdc_loop(), CAT, REG)
    vessel = next(
        c for c in done.components if c.definition_id == "expansion-connection"
    )
    tee = next(c for c in done.components if c.id == f"tee-{vessel.id}")
    # Cammina dal braccio del raccordo.
    chain = []
    current = (tee.id, "branch")
    edge = next(
        c
        for c in done.connections
        if (c.endpoint_a.component_id, c.endpoint_a.port_id) == current
        or (c.endpoint_b.component_id, c.endpoint_b.port_id) == current
    )
    for _ in range(5):
        other = (
            edge.endpoint_b
            if edge.endpoint_a.component_id == current[0]
            else edge.endpoint_a
        )
        chain.append(other.component_id)
        if other.component_id == vessel.id:
            break
        onward = [
            c
            for c in done.connections
            if other.component_id
            in (c.endpoint_a.component_id, c.endpoint_b.component_id)
            and c.id != edge.id
        ]
        assert len(onward) == 1
        current, edge = (other.component_id, other.port_id), onward[0]
    kinds = [
        CAT.get(next(c.definition_id for c in done.components if c.id == cid)).functions
        for cid in chain
    ]
    assert any("isolation_locked_open" in k for k in kinds[:-1]), chain
    assert chain[-1] == vessel.id
    # E nessuna valvola bloccabile e' rimasta in fila sul percorso principale.
    # La fila dello stacco stesso (dal braccio del raccordo al vaso) e' esclusa:
    # che la bloccabile stia li' e' il contratto, non una violazione.
    stub_chain = {tee.id, vessel.id, *chain}
    for (head, tail, _), pieces in _fila(done).items():
        if head in stub_chain or tail in stub_chain:
            continue
        for cid in pieces:
            inst = next(c for c in done.components if c.id == cid)
            definition = CAT.get(inst.definition_id)
            if definition.is_a_fitting:
                continue
            assert "isolation_locked_open" not in definition.functions, cid


# ---------------------------------------------------------------------------
# 2. Sicurezza, defangatore, termometro: i vincoli dichiarati sono rispettati
# ---------------------------------------------------------------------------


def _over_35(model: ProjectModel) -> ProjectModel:
    """Il regime grande, dichiarato: le regole per generatore parlano solo li'.

    Da D-106 sicurezza e termometro per generatore valgono sopra i 35 kW; senza
    dichiarazione vale il corredo minimo e queste regole tacciono. La meccanica
    che questo collaudo verifica — attaccato alla macchina, prima degli organi
    di chiusura — resta quella, e si prova dichiarando il regime che la usa.
    """
    return model.model_copy(update={"plant_regime": PlantRegime.OVER_35_KW})


def test_la_sicurezza_sta_attaccata_alla_macchina_senza_nulla_di_chiudibile() -> None:
    for model in (_over_35(_pdc_loop()), _over_35(load("prova-2-pdc-deviatrice-acs.json"))):
        done, _, _ = saturate(model, CAT, REG)
        machines = [
            c.id
            for c in done.components
            if "heat_generation" in CAT.get(c.definition_id).functions
        ]
        for machine in machines:
            outlet = next(
                p.id
                for p in CAT.get(
                    next(c.definition_id for c in done.components if c.id == machine)
                ).ports
                if p.flow.value == "out" and not p.off_the_run
            )
            pieces = _run_from(done, machine, outlet)
            safety_at = [
                i for i, p in enumerate(pieces) if "safety" in p.functions
            ]
            assert safety_at, f"nessuna sicurezza sulla mandata di {machine}"
            before = pieces[: safety_at[0]]
            assert not any(
                p.functions & CLOSABLE for p in before
            ), f"{machine}: chiudibile fra la macchina e la sicurezza: {before}"
            assert safety_at[0] == 0, (
                f"{machine}: fra la macchina e la sicurezza c'e' {before}"
            )


def test_il_defangatore_sta_lato_impianto_rispetto_all_intercettazione() -> None:
    for model in (_pdc_loop(), load("prova-2-pdc-deviatrice-acs.json")):
        done, _, _ = saturate(model, CAT, REG)
        machines = [
            c.id
            for c in done.components
            if "heat_generation" in CAT.get(c.definition_id).functions
        ]
        for machine in machines:
            inlet = next(
                p.id
                for p in CAT.get(
                    next(c.definition_id for c in done.components if c.id == machine)
                ).ports
                if p.flow.value == "in" and not p.off_the_run
            )
            pieces = _run_from(done, machine, inlet)
            own = [p for p in pieces if p.anchor == machine]
            sludge = [i for i, p in enumerate(own) if "sludge_separation" in p.functions]
            valve = [
                i
                for i, p in enumerate(own)
                if p.functions & CLOSABLE and p.rule == "isolate-what-is-serviced"
            ]
            assert sludge and valve, (machine, [p.component_id for p in own])
            assert min(valve) < min(sludge), (
                f"{machine}: il defangatore non e' lato impianto: "
                f"{[p.component_id for p in own]}"
            )


def test_il_termometro_di_mandata_non_finisce_dopo_un_organo_di_chiusura() -> None:
    for model in (_over_35(_pdc_loop()), _over_35(load("prova-2-pdc-deviatrice-acs.json"))):
        done, _, _ = saturate(model, CAT, REG)
        machines = [
            c.id
            for c in done.components
            if "heat_generation" in CAT.get(c.definition_id).functions
        ]
        for machine in machines:
            outlet = next(
                p.id
                for p in CAT.get(
                    next(c.definition_id for c in done.components if c.id == machine)
                ).ports
                if p.flow.value == "out" and not p.off_the_run
            )
            pieces = _run_from(done, machine, outlet)
            own = [p for p in pieces if p.anchor == machine]
            thermo = [
                i
                for i, p in enumerate(own)
                if "temperature_measurement" in p.functions
            ]
            valve = [i for i, p in enumerate(own) if p.functions & CLOSABLE]
            assert thermo, (machine, [p.component_id for p in own])
            if valve:
                assert min(thermo) < min(valve), (
                    f"{machine}: termometro dopo un organo di chiusura: "
                    f"{[p.component_id for p in own]}"
                )


def test_ogni_accessorio_viaggia_col_proprio_blocco_di_valvole() -> None:
    """Le valvole ancorate a un accessorio gli restano adiacenti dopo il
    riordino: spostarlo lasciandole indietro le renderebbe due valvole che non
    chiudono niente. Il contratto e' l'adiacenza del blocco, non il numero di
    valvole: fra due accessori manutenibili contigui una valvola puo' essere
    condivisa (convenzione approvata in G3)."""
    for model in (_pdc_loop(), load("prova-1-due-pdc-accumulo-combinato.json")):
        done, _, _ = saturate(model, CAT, REG)
        for pieces in _fila(done).values():
            order = {cid: i for i, cid in enumerate(pieces)}
            for cid in pieces:
                mine = sorted(
                    order[other]
                    for other in pieces
                    if other.startswith("valve-isolation-") and cid in other
                )
                for position in mine:
                    assert abs(position - order[cid]) <= len(mine), (cid, pieces)


# ---------------------------------------------------------------------------
# 3. L'ordine non dipende dai nomi dei file delle regole
# ---------------------------------------------------------------------------


def test_rinominare_i_file_delle_regole_non_cambia_la_fila(tmp_path: Path) -> None:
    """Stesse quattordici regole, nomi di file che invertono l'ordine
    alfabetico: fila per tratta, pezzi e sigle non devono cambiare."""
    renamed = tmp_path / "rules"
    renamed.mkdir()
    originals = sorted(RULES_DIR.glob("*.json"))
    for index, path in enumerate(originals):
        (renamed / f"z{90 - index:02d}.json").write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8"
        )
    reg2 = RuleRegistry.from_directory(renamed)
    assert [r.id for r in reg2.all()] == [
        r.id for r in reversed(REG.all())
    ], "la rinomina non ha invertito l'ordine di caricamento"

    for name in ("prova-2-pdc-deviatrice-acs.json", "prova-1-due-pdc-accumulo-combinato.json"):
        base = load(name)
        done_a, _, _ = saturate(base, CAT, REG)
        done_b, _, _ = saturate(base, CAT, reg2)
        assert {c.id for c in done_a.components} == {c.id for c in done_b.components}
        assert _fila(done_a) == _fila(done_b, rules_map(reg2)), name
        assert read(done_a, CAT).sigle == read(done_b, CAT).sigle, name


# ---------------------------------------------------------------------------
# 4. Due regole incompatibili: si ferma e le nomina
# ---------------------------------------------------------------------------


def test_due_regole_incompatibili_fermano_e_vengono_nominate(tmp_path: Path) -> None:
    reg = _write_rules(
        tmp_path / "rules",
        [
            _rule_json(
                "litigio-primo",
                "filtration",
                "on_inlet",
                {"before": ["sludge_separation"]},
            ),
            _rule_json(
                "litigio-secondo",
                "sludge_separation",
                "on_inlet",
                {"before": ["filtration"]},
            ),
        ],
    )
    with pytest.raises(AssemblyError) as raised:
        saturate(_pdc_loop(), CAT, reg)
    message = str(raised.value)
    assert "litigio-primo" in message
    assert "litigio-secondo" in message


def test_tre_regole_in_cerchio_fermano_e_vengono_nominate_tutte(tmp_path: Path) -> None:
    reg = _write_rules(
        tmp_path / "rules",
        [
            _rule_json(
                "cerchio-a", "filtration", "on_inlet", {"before": ["sludge_separation"]}
            ),
            _rule_json(
                "cerchio-b", "sludge_separation", "on_inlet", {"before": ["non_return"]}
            ),
            _rule_json(
                "cerchio-c", "non_return", "on_inlet", {"before": ["filtration"]}
            ),
        ],
    )
    with pytest.raises(AssemblyError) as raised:
        saturate(_pdc_loop(), CAT, reg)
    message = str(raised.value)
    for rule_id in ("cerchio-a", "cerchio-b", "cerchio-c"):
        assert rule_id in message, message


def test_due_regole_che_pretendono_entrambe_il_posto_attaccato_alla_macchina(tmp_path: Path) -> None:
    """Due pezzi che dichiarano «fra me e la macchina non ci va nessun altro
    pezzo» sullo stesso attacco non possono stare insieme: qualunque fila ne
    violerebbe uno. Il contratto D-094 impone di fermarsi e nominarle, non di
    produrre in silenzio una fila in cui uno dei due vincoli e' falso."""
    reg = _write_rules(
        tmp_path / "rules",
        [
            _rule_json(
                "abbraccio-primo",
                "air_release",
                "on_outlet",
                {"against_the_anchor": True},
            ),
            _rule_json(
                "abbraccio-secondo",
                "non_return",
                "on_outlet",
                {"against_the_anchor": True},
            ),
        ],
    )
    with pytest.raises(AssemblyError) as raised:
        saturate(_pdc_loop(), CAT, reg)
    message = str(raised.value)
    assert "abbraccio-primo" in message
    assert "abbraccio-secondo" in message


# ---------------------------------------------------------------------------
# 5. Deterministico, e riordina solo cio' che le regole hanno aggiunto
# ---------------------------------------------------------------------------


def test_stesso_grafo_stessa_fila_a_ripetizione_e_su_permutazioni() -> None:
    base = load("prova-1-due-pdc-accumulo-combinato.json")
    first = canonical_json(saturate(base, CAT, REG)[0])
    for _ in range(4):
        assert canonical_json(saturate(base, CAT, REG)[0]) == first
    expected = _fila(saturate(base, CAT, REG)[0])
    for seed in range(10):
        done_p, _, _ = saturate(permuted(base, seed), CAT, REG)
        assert _fila(done_p) == expected, seed


def test_cio_che_il_progettista_ha_scritto_resta_dove_lo_ha_messo() -> None:
    """Un ritegno scritto a mano in mezzo al ritorno: le regole aggiungono i
    loro pezzi, ma nessun pezzo scavalca il ritegno e il ritegno non entra in
    nessuna fila riordinabile."""
    base = project(
        networks=[net("primario", "heating_water")],
        components=[
            comp("pdc", "heat-pump-air-water"),
            comp("utenza", "fan-coil"),
            comp("ritegno-mio", "valve-check", tag="VR-77"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc", "water_supply"), ("utenza", "in")),
            pipe("r1", "primario", ("utenza", "out"), ("ritegno-mio", "a")),
            pipe("r2", "primario", ("ritegno-mio", "b"), ("pdc", "water_return")),
        ],
    )
    done, _, _ = saturate(base, CAT, REG)
    assert validate_project(done, CAT).ok
    fila = _fila(done)
    for pieces in fila.values():
        assert "ritegno-mio" not in pieces
    # Il ritegno e' ancora fra l'utenza e la pompa di calore, e i pezzi che le
    # regole hanno ancorato alla PdC stanno tutti dal lato della PdC.
    ends = {
        key: pieces
        for key, pieces in fila.items()
        if "ritegno-mio" in (key[0], key[1])
    }
    assert ends, fila
    for (head, tail, _network), pieces in ends.items():
        if tail == "pdc" or head == "pdc":
            anchored = [p for p in pieces if "pdc" in p]
            assert anchored, pieces
        if "utenza" in (head, tail):
            for cid in pieces:
                assert "pdc-water-return" not in cid, (
                    f"un pezzo ancorato alla PdC ha scavalcato il ritegno: {pieces}"
                )
