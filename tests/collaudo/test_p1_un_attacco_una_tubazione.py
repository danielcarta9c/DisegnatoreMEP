"""Collaudo indipendente — Pacchetto 1: un attacco, una tubazione (D-100).

Contratto:
- ogni attacco porta una tubazione sola, sempre;
- il modello RIFIUTA la seconda tubazione sullo stesso attacco;
- dove due tubazioni si incontrano c'e' un pezzo che le unisce con la propria
  sigla (confluenza: tre attacchi sul percorso; ripartizione: idem, una si sdoppia);
- lo stesso impianto scritto in ordini diversi da' lo stesso grafo (permutazioni
  di tubazioni, pezzi e reti; confronto sul dump completo).
"""

import itertools

import pytest
from helpers import (
    catalog,
    comp,
    graph_dump,
    load,
    net,
    permuted,
    pipe,
    project,
    read,
    rules,
)
from pydantic import ValidationError

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.validation.topology import validate_project

CAT = catalog()


def _two_pdc_junction_plant() -> ProjectModel:
    """Due pompe di calore in parallelo: le mandate si uniscono in una
    confluenza, il ritorno comune si sdoppia in una ripartizione."""
    return project(
        networks=[net("primario", "heating_water")],
        components=[
            comp("pdc1", "heat-pump-air-water"),
            comp("pdc2", "heat-pump-air-water"),
            comp("conflu", "tee-junction"),
            comp("riparto", "tee-split"),
            comp("volano", "buffer-two-port"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc1", "water_supply"), ("conflu", "a")),
            pipe("m2", "primario", ("pdc2", "water_supply"), ("conflu", "c")),
            pipe("m3", "primario", ("conflu", "b"), ("volano", "a")),
            pipe("r1", "primario", ("volano", "b"), ("riparto", "a")),
            pipe("r2", "primario", ("riparto", "b"), ("pdc1", "water_return")),
            pipe("r3", "primario", ("riparto", "c"), ("pdc2", "water_return")),
        ],
    )


# ---------------------------------------------------------------------------
# 1. La seconda tubazione sullo stesso attacco viene rifiutata
# ---------------------------------------------------------------------------


def test_la_seconda_tubazione_sullo_stesso_attacco_e_un_errore_bloccante() -> None:
    """Due mandate saldate sullo stesso bocchello del volano: il validatore
    deve respingere con un errore bloccante, non lasciar passare."""
    model = project(
        networks=[net("primario", "heating_water")],
        components=[
            comp("pdc1", "heat-pump-air-water"),
            comp("pdc2", "heat-pump-air-water"),
            comp("volano", "buffer-two-port"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc1", "water_supply"), ("volano", "a")),
            pipe("m2", "primario", ("pdc2", "water_supply"), ("volano", "a")),
            pipe("r1", "primario", ("volano", "b"), ("pdc1", "water_return")),
            pipe("r2", "primario", ("volano", "b"), ("pdc2", "water_return")),
        ],
    )
    report = validate_project(model, CAT)
    assert not report.ok
    offended = [i for i in report.issues if i.code == "PORT_CONNECTION_LIMIT"]
    # Due attacchi violati: l'ingresso (due tubazioni) e l'uscita (due).
    assert len(offended) == 2, [i.message for i in report.issues]
    touched = {tuple(i.entity_ids) for i in offended}
    assert ("volano", "a") in touched
    assert ("volano", "b") in touched
    for issue in offended:
        assert issue.severity.value == "blocking"


def test_anche_su_un_attacco_di_servizio_la_seconda_tubazione_e_rifiutata() -> None:
    """Caso limite: lo stacco di servizio (lo scarico del volano) con due
    tubazioni. Anche uno stacco e' un attacco: una sola, sempre."""
    model = project(
        networks=[net("primario", "heating_water")],
        components=[
            comp("pdc1", "heat-pump-air-water"),
            comp("volano", "buffer-four-port"),
            comp("utenza", "fan-coil"),
            comp("scarico1", "drain-connection"),
            comp("scarico2", "drain-connection"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc1", "water_supply"), ("volano", "a")),
            pipe("r1", "primario", ("volano", "b"), ("pdc1", "water_return")),
            pipe("s1", "primario", ("volano", "secondary_out"), ("utenza", "in")),
            pipe("s2", "primario", ("utenza", "out"), ("volano", "secondary_in")),
            pipe("d1", "primario", ("volano", "drain"), ("scarico1", "a")),
            pipe("d2", "primario", ("volano", "drain"), ("scarico2", "a")),
        ],
    )
    report = validate_project(model, CAT)
    assert not report.ok
    offended = [i for i in report.issues if i.code == "PORT_CONNECTION_LIMIT"]
    assert any(tuple(i.entity_ids) == ("volano", "drain") for i in offended)


def test_il_catalogo_non_puo_dichiarare_un_attacco_che_accetti_due_tubazioni() -> None:
    """D-100: «il catalogo non puo' piu' dichiarare attacchi che ne accettino
    due: la cosa non e' configurabile». Un campo di capienza deve essere
    rifiutato al caricamento della voce."""
    for field in ("max_connections", "capacity", "max_pipes"):
        with pytest.raises(ValidationError):
            PortDefinition.model_validate(
                {
                    "id": "a",
                    "domain": "hydronic",
                    "medium": "heating_water",
                    "flow": "in",
                    **{field: 2},
                }
            )


# ---------------------------------------------------------------------------
# 2. Confluenza e ripartizione: pezzi con la propria sigla, attacchi sul percorso
# ---------------------------------------------------------------------------


def test_confluenza_e_ripartizione_hanno_sigla_propria_e_tre_attacchi_sul_percorso() -> None:
    model = _two_pdc_junction_plant()
    assert validate_project(model, CAT).ok

    junction = CAT.get("tee-junction")
    split = CAT.get("tee-split")
    # Tutti e tre gli attacchi sul percorso, per entrambi: nessuno stub.
    assert all(not p.off_the_run for p in junction.ports)
    assert all(not p.off_the_run for p in split.ports)
    # Confluenza: due entrano, una esce. Ripartizione: una entra, due escono.
    assert sorted(p.flow.value for p in junction.ports) == ["in", "in", "out"]
    assert sorted(p.flow.value for p in split.ports) == ["in", "out", "out"]

    graph = read(model, CAT)
    sigle = graph.sigle
    # Ogni pezzo ha una sigla, tutte diverse, comprese confluenza e ripartizione.
    assert len(set(sigle.values())) == len(sigle)
    assert sigle["conflu"]
    assert sigle["riparto"]
    assert sigle["conflu"] != sigle["riparto"]


def test_nel_grafo_nessun_attacco_del_flusso_porta_due_tubazioni() -> None:
    """Sul grafo letto, nessun braccio e' un incrocio: dove due tubazioni si
    incontrano c'e' un pezzo, non un attacco doppio."""
    for name in (
        "prova-1-due-pdc-accumulo-combinato.json",
        "prova-2-pdc-deviatrice-acs.json",
        "prova-3-pdc-diretta-pavimento.json",
        "prova-4-ibrido-pdc-caldaia.json",
        "prova-5-cascata-tre-pdc.json",
    ):
        model = load(name)
        assert validate_project(model, CAT).ok, name
        graph = read(model, CAT)
        assert graph.crossings == (), f"{name}: {graph.crossings}"


# ---------------------------------------------------------------------------
# 3. Lo stesso impianto in ordini diversi da' lo stesso grafo
# ---------------------------------------------------------------------------


def test_tutte_le_permutazioni_delle_tubazioni_danno_lo_stesso_grafo() -> None:
    """Confronto sul dump completo, non sulle sole sigle: 720 riordinamenti
    delle sei tubazioni dell'impianto con confluenza e ripartizione."""
    base = _two_pdc_junction_plant()
    expected = graph_dump(read(base, CAT))
    for order in itertools.permutations(range(len(base.connections))):
        shuffled = base.model_copy(
            update={"connections": [base.connections[i] for i in order]}
        )
        assert graph_dump(read(shuffled, CAT)) == expected, order


def test_permutazioni_combinate_di_pezzi_reti_e_tubazioni() -> None:
    """Permutazioni casuali ma riproducibili di tutti e tre gli elenchi,
    sull'impianto sintetico e su due impianti del committente."""
    for maker in (
        _two_pdc_junction_plant,
        lambda: load("prova-1-due-pdc-accumulo-combinato.json"),
        lambda: load("prova-2-pdc-deviatrice-acs.json"),
    ):
        base = maker()
        expected = graph_dump(read(base, CAT))
        for seed in range(12):
            shuffled = permuted(base, seed)
            assert graph_dump(read(shuffled, CAT)) == expected, seed


def test_anche_il_modello_completato_e_lo_stesso_in_ordini_diversi() -> None:
    """Tutta la catena — regole, assemblatore — su input permutato: la fila
    per tratta e le sigle non devono cambiare."""
    from disegnatore_mep.assembly import runs_of

    reg = rules()
    rmap = {item.id: item for item in reg.all()}
    base = load("prova-2-pdc-deviatrice-acs.json")
    done, _, _ = saturate(base, CAT, reg)

    def fila(model: ProjectModel) -> dict[tuple[str, str, str], tuple[str, ...]]:
        return {
            (r.head.component_id, r.tail.component_id, r.network_id): tuple(
                r.component_ids
            )
            for r in runs_of(model, CAT, rmap)
        }

    expected_fila = fila(done)
    expected_sigle = read(done, CAT).sigle
    for seed in range(6):
        done_p, _, _ = saturate(permuted(base, seed), CAT, reg)
        assert fila(done_p) == expected_fila, seed
        assert read(done_p, CAT).sigle == expected_sigle, seed
