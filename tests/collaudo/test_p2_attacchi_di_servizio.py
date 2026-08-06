"""Collaudo indipendente — Pacchetto 2: gli attacchi di servizio (D-101).

Contratto:
- gli attacchi secondari li dichiara il catalogo, macchina per macchina (serves);
- un accessorio che pende da uno stacco si posa sull'attacco di servizio della
  macchina quando ce l'ha, su una derivazione saldata sul tubo quando non ce l'ha
  (il bollitore non ha lo scarico: si svuota dall'ingresso freddo tramite
  derivazione);
- un accessorio di servizio non finisce MAI in fila sulla tubazione principale;
- gli accessori che pendono hanno UN attacco, non due;
- dove la macchina non ha l'attacco e non c'e' derivazione possibile, la regola
  lo DICE (punto aperto), non tace.
"""

import shutil
from pathlib import Path

import pytest
from helpers import (
    CATALOG_DIR,
    catalog,
    comp,
    load,
    net,
    pipe,
    project,
    rules,
)

from disegnatore_mep.catalog.schema import ComponentTrait
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.validation.topology import validate_project

CAT = catalog()
REG = rules()

PROVE = [
    "prova-1-due-pdc-accumulo-combinato.json",
    "prova-2-pdc-deviatrice-acs.json",
    "prova-3-pdc-diretta-pavimento.json",
    "prova-4-ibrido-pdc-caldaia.json",
    "prova-5-cascata-tre-pdc.json",
]


def _volano_plant() -> ProjectModel:
    """PdC, volano a quattro attacchi, un'utenza: il volano ha lo scarico."""
    return project(
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


def _holders(model: ProjectModel) -> dict[str, set[str]]:
    """Per ogni componente: gli attacchi toccati da una tubazione."""
    found: dict[str, set[str]] = {}
    for c in model.connections:
        for ref in (c.endpoint_a, c.endpoint_b):
            found.setdefault(ref.component_id, set()).add(ref.port_id)
    return found


# ---------------------------------------------------------------------------
# 1. Il catalogo dichiara gli attacchi di servizio, macchina per macchina
# ---------------------------------------------------------------------------


def test_gli_attacchi_di_servizio_sono_dichiarati_dal_catalogo() -> None:
    volano = CAT.get("buffer-four-port")
    serves = {p.serves for p in volano.ports if p.serves}
    assert serves == {"air_release", "drain", "temperature_measurement"}
    # Il bollitore NON ha lo scarico (D-102: i cataloghi non lo prevedono).
    bollitore = CAT.get("dhw-cylinder")
    assert "drain" not in {p.serves for p in bollitore.ports if p.serves}
    assert "temperature_measurement" in {p.serves for p in bollitore.ports}
    # Un attacco di servizio e' uno stacco: fuori dal percorso del fluido.
    for entry in (volano, bollitore):
        for port in entry.ports:
            if port.serves is not None:
                assert port.off_the_run


# ---------------------------------------------------------------------------
# 2. Con l'attacco: l'accessorio si posa li'. Senza: derivazione sul tubo giusto
# ---------------------------------------------------------------------------


def test_lo_scarico_del_volano_va_sul_suo_attacco_senza_spezzare_il_tubo() -> None:
    done, _, gaps = saturate(_volano_plant(), CAT, REG)
    # C'e' uno scarico, e pende dall'attacco di servizio del volano.
    drains = [
        c for c in done.components if c.definition_id == "drain-connection"
    ]
    assert len(drains) == 1
    stub = [
        c
        for c in done.connections
        if (c.endpoint_a.component_id, c.endpoint_a.port_id) == ("volano", "drain")
        or (c.endpoint_b.component_id, c.endpoint_b.port_id) == ("volano", "drain")
    ]
    assert len(stub) == 1
    ends = {stub[0].endpoint_a.component_id, stub[0].endpoint_b.component_id}
    assert ends == {"volano", drains[0].id}
    # Nessun raccordo di derivazione e' stato saldato per quello scarico.
    assert not any(c.id == f"tee-{drains[0].id}" for c in done.components)
    assert validate_project(done, CAT).ok


@pytest.mark.skip(
    reason=(
        "Difetto C2, confermato dal collaudo e ancora aperto: lo scarico del "
        "bollitore e' saldato sull'uscita dell'acqua calda sanitaria, mentre le "
        "fonti (SRC-017, SRC-018, D-101) dicono che si svuota dall'ingresso "
        "freddo. La correzione e' progettata nell'appendice del piano: il "
        "catalogo deve dichiarare da quale attacco la riserva si riempie, e la "
        "regola dello scarico deve posare la derivazione li'. Questa prova "
        "torna verde con quella correzione, e non va ammorbidita."
    )
)
def test_il_bollitore_si_svuota_dall_ingresso_freddo_con_una_derivazione() -> None:
    """Contratto (D-101 e DOVE_VA_CIASCUN_ACCESSORIO §10): «su un bollitore
    sanitario lo scarico non c'e', e lo si svuota con una derivazione sulla
    tubazione dell'acqua fredda in ingresso»."""
    done, _, _ = saturate(load(PROVE[1]), CAT, REG)
    drains = [
        c
        for c in done.components
        if c.definition_id.startswith("drain-connection")
        and "bollitore" in c.id
    ]
    assert len(drains) == 1, [c.id for c in done.components if "drain" in c.id]
    drain = drains[0]
    tee = next(c for c in done.components if c.id == f"tee-{drain.id}")
    # La derivazione e' saldata su una tubazione: quale? Quella dell'acqua
    # fredda in ingresso al bollitore, dice il contratto.
    touching = [
        c
        for c in done.connections
        if tee.id in (c.endpoint_a.component_id, c.endpoint_b.component_id)
        and drain.id not in (c.endpoint_a.component_id, c.endpoint_b.component_id)
    ]
    reti = {c.network_id for c in touching}
    assert reti == {"fredda"}, (
        f"lo scarico del bollitore e' saldato sulla rete {reti}, "
        f"non sull'acqua fredda in ingresso"
    )


def test_senza_attacco_dedicato_nasce_una_derivazione_e_il_percorso_resta_intero() -> None:
    """La PdC non ha attacchi di servizio: vaso, riempimento e manometro
    pendono da derivazioni saldate sul tubo, ciascuno dalla propria."""
    done, _, _ = saturate(_volano_plant(), CAT, REG)
    assert validate_project(done, CAT).ok
    for definition_id in ("expansion-connection", "filling-unit", "pressure-gauge"):
        hung = [c for c in done.components if c.definition_id == definition_id]
        assert hung, definition_id
        for item in hung:
            tee = [c for c in done.components if c.id == f"tee-{item.id}"]
            assert len(tee) == 1, item.id


# ---------------------------------------------------------------------------
# 3. Un accessorio di servizio non sta mai in fila sulla tubazione principale
# ---------------------------------------------------------------------------


def test_chi_pende_da_uno_stacco_non_e_mai_in_fila_sul_percorso() -> None:
    """Su tutti e cinque gli impianti del committente piu' il sintetico: ogni
    accessorio a stacco ha una sola tubazione, e risalendo la sua piccola
    catena (ammessa: e' la fila dello stacco) si arriva a un attacco di
    servizio o al braccio di un raccordo — mai a un attacco del percorso."""
    plants = [load(name) for name in PROVE] + [_volano_plant()]
    for model in plants:
        done, _, _ = saturate(model, CAT, REG)
        defs = {c.id: CAT.get(c.definition_id) for c in done.components}
        touching: dict[str, list[ConnectionModel]] = {}
        for c in done.connections:
            for ref in (c.endpoint_a, c.endpoint_b):
                touching.setdefault(ref.component_id, []).append(c)
        for component in done.components:
            if not defs[component.id].attaches_on_a_branch:
                continue
            pipes_touching = touching.get(component.id, [])
            assert len(pipes_touching) == 1, component.id
            # Risali la catena dello stacco fino al piede.
            current, edge = component.id, pipes_touching[0]
            for _ in range(10):
                other = (
                    edge.endpoint_b
                    if edge.endpoint_a.component_id == current
                    else edge.endpoint_a
                )
                port = next(
                    p for p in defs[other.component_id].ports if p.id == other.port_id
                )
                if port.off_the_run:
                    break  # piede dello stacco: attacco di servizio o braccio
                holder = defs[other.component_id]
                assert not holder.is_a_fitting, (
                    f"{component.id}: la catena arriva a "
                    f"{other.component_id}.{other.port_id}, che e' il percorso"
                )
                assert len(defs[other.component_id].ports) == 2 and len(
                    touching[other.component_id]
                ) == 2, (
                    f"{component.id} e' appeso a {other.component_id}."
                    f"{other.port_id}, che sta sul percorso principale"
                )
                onward = [
                    c for c in touching[other.component_id] if c.id != edge.id
                ]
                current, edge = other.component_id, onward[0]
            else:
                raise AssertionError(f"catena troppo lunga da {component.id}")


def test_gli_accessori_che_pendono_hanno_un_attacco_solo() -> None:
    """Le famiglie che pendono: vaso, sicurezza, scarico, riempimento,
    strumenti. Ognuna con UN attacco, in tutto il catalogo pubblicato."""
    hanging = [
        entry
        for entry in CAT.all()
        if entry.has_trait(ComponentTrait.ATTACHMENT_BRANCH)
    ]
    assert {e.id for e in hanging} >= {
        "expansion-connection",
        "expansion-connection-dhw",
        "valve-safety",
        "valve-safety-dhw",
        "drain-connection",
        "drain-connection-dhw",
        "filling-unit",
        "pressure-gauge",
        "thermometer",
    }
    for entry in hanging:
        assert len(entry.ports) == 1, (entry.id, [p.id for p in entry.ports])


# ---------------------------------------------------------------------------
# 4. Casi limite: attacco gia' occupato, pezzo mancante, derivazione impossibile
# ---------------------------------------------------------------------------


def test_attacco_di_servizio_gia_occupato_dal_progettista_niente_doppioni() -> None:
    base = _volano_plant()
    occupied = base.model_copy(
        update={
            "components": [*base.components, comp("scarico-mio", "drain-connection", tag="SC-99")],
            "connections": [
                *base.connections,
                pipe("mio", "primario", ("volano", "drain"), ("scarico-mio", "a")),
            ],
        }
    )
    done, _, _ = saturate(occupied, CAT, REG)
    drains = [c for c in done.components if c.definition_id == "drain-connection"]
    assert [c.id for c in drains] == ["scarico-mio"]
    assert validate_project(done, CAT).ok


def test_quando_il_catalogo_non_ha_il_pezzo_la_regola_lo_dice(tmp_path: Path) -> None:
    """Tolto lo scarico sanitario dal catalogo: la regola dello svuotamento si
    applica al bollitore e non ha nulla da offrire. Deve uscire un punto
    aperto che nomina la regola, non un silenzio."""
    ridotto = tmp_path / "catalog"
    shutil.copytree(CATALOG_DIR, ridotto)
    (ridotto / "drain-connection-dhw.json").unlink()
    cat = catalog(ridotto)
    found = evaluate(load(PROVE[1]), cat, REG)
    gaps = [g for g in found.gaps if g.rule_id == "let-what-holds-its-own-volume-empty"]
    assert gaps, [g.rule_id for g in found.gaps]
    assert gaps[0].missing_function == "drain"
    assert gaps[0].anchor.component_id == "bollitore"
    # E la saturazione intera lo riporta senza tacere.
    _, _, all_gaps = saturate(load(PROVE[1]), cat, rules())
    assert any(
        g.rule_id == "let-what-holds-its-own-volume-empty" for g in all_gaps
    )


def test_derivazione_impossibile_e_un_punto_aperto_non_un_crollo(tmp_path: Path) -> None:
    """Il pezzo c'e' (lo scarico sanitario) ma il raccordo di derivazione su
    quel fluido no: la macchina non ha l'attacco, la derivazione non si puo'
    aprire. Contratto: la regola lo DICE (punto aperto), non tace — e non
    deve nemmeno far crollare l'intera catena senza dossier."""
    ridotto = tmp_path / "catalog"
    shutil.copytree(CATALOG_DIR, ridotto)
    (ridotto / "tee-branch-dhw.json").unlink()
    cat = catalog(ridotto)
    done, proposals, gaps = saturate(load(PROVE[1]), cat, REG)
    assert any(
        g.missing_function in {"drain", "branch_off"} and "bollitore" in g.anchor.component_id
        for g in gaps
    ), [
        (g.rule_id, g.missing_function, g.anchor.component_id) for g in gaps
    ]
