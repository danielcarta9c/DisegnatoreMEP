"""Il ricircolo ACS: una linea col suo colore, che entra dalle utenze e torna nell'accumulo.

**D-176**, il PO il 23 settembre 2026, guardando l'impianto 5:

    «il ricircolo ha proprio un errore.. innanzitutto la linea di ricircolo ha un
    colore a se' (io generalmente uso il verde chiaro) poi il ricircolo preleva
    dalle utenze (quindi in tavola lo avrei disegnato come un AcsR in ingresso
    (un simbolo uguale a quello del prelievo Af) che poi va nel disegno e poi
    fondamentale ACS-ritorno dopo il Circolatore va nell'accumulo ACS (se ho
    accumulo) altrimenti idraulicamente e termicamente non ha senso.»

Il grafo dell'impianto 5 chiudeva l'anello subito dopo il bollitore: una presa
sulla mandata sanitaria, il circolatore, e un innesto sulla stessa mandata a
monte. Era l'assunzione a3 di «Capire», ed era un errore del grafo, non del
disegno. Due prove, come chiede il pacchetto:

- **la topologia**: il ricircolo parte da un confine «ACS-R» — lo stesso simbolo
  dell'ingresso dell'acqua fredda —, passa per il suo circolatore e rientra
  nell'accumulo dal suo attacco; la mandata sanitaria va alle utenze senza
  nessun raccordo;
- **il colore**: il ricircolo e' il **ritorno** dell'acqua calda sanitaria — la
  stessa acqua che torna —, e il ritorno dell'acqua calda si disegna verde
  chiaro, con la sua riga di legenda.
"""

# categoria: difende il contenuto — D-176, il ricircolo sanitario: dall'ACS-R all'accumulo, verde chiaro

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.flow import classify_trunks
from disegnatore_mep.layout.geometry import Point, RoutedTrunk
from disegnatore_mep.layout.legend import (
    MEDIUM_STYLES,
    RECIRCULATION_COLOUR,
    build_legend,
    style_for,
)
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CINQUE = ROOT / "examples" / "prova" / "prova-5-cascata-tre-pdc.json"
DHW = "domestic_hot_water"


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


@cache
def completo() -> ProjectModel:
    fatto, _, _ = saturate(
        load_project(CINQUE),
        catalogo(),
        RuleRegistry.from_directory(ROOT / "rules" / "hydronic"),
    )
    return ProjectModel.model_validate_json(canonical_json(fatto))


def _definizioni(progetto: ProjectModel) -> dict[str, str]:
    return {item.id: item.definition_id for item in progetto.components}


def _funzioni(progetto: ProjectModel, component_id: str) -> frozenset[str]:
    return frozenset(catalogo().get(_definizioni(progetto)[component_id]).functions)


def _tratte(progetto: ProjectModel) -> list[Trunk]:
    return build_trunks(progetto, inline_component_ids(progetto, catalogo()))


def _ricircolo(progetto: ProjectModel) -> Trunk:
    """La tratta che rientra nell'accumulo dall'attacco del ricircolo."""
    trovate = [
        trunk
        for trunk in _tratte(progetto)
        if any(
            ref.port_id == "recirculation_in"
            and "dhw_storage" in _funzioni(progetto, ref.component_id)
            for ref in (trunk.start, trunk.end)
        )
    ]
    assert len(trovate) == 1, [trunk.connection_ids for trunk in trovate]
    return trovate[0]


def test_il_ricircolo_entra_da_un_confine_acs_r_e_rientra_nell_accumulo() -> None:
    """La topologia di D-176, sul grafo del progettista e su quello completo.

    Il confine dell'ACS-R si disegna con lo stesso simbolo dell'ingresso
    dell'acqua fredda; dal confine si arriva all'accumulo attraversando il solo
    corredo in linea, e il circolatore e' fra quello."""
    for progetto in (load_project(CINQUE), completo()):
        definizioni = _definizioni(progetto)
        confini = [
            item
            for item in progetto.components
            if item.definition_id == "dhw-recirculation-inlet"
        ]
        assert len(confini) == 1, [item.id for item in confini]
        confine = confini[0]
        assert confine.tag == "ACS-R"
        assert "boundary" in catalogo().get(confine.definition_id).functions
        assert (
            catalogo().get("dhw-recirculation-inlet").symbol_id
            == catalogo().get("cold-water-inlet").symbol_id
        )

        trunk = _ricircolo(progetto)
        capi = {trunk.start.component_id, trunk.end.component_id}
        assert confine.id in capi, (confine.id, capi)
        in_linea = set(trunk.inline_component_ids)
        assert any(
            "circulation" in catalogo().get(definizioni[item]).functions for item in in_linea
        ), sorted(in_linea)


def test_la_mandata_sanitaria_va_alle_utenze_senza_innesti() -> None:
    """L'errore del grafo: l'anello si chiudeva subito dopo il bollitore, con
    una presa e un innesto sulla mandata sanitaria. Non c'e' piu' nessun
    raccordo sull'acqua calda sanitaria dell'impianto 5."""
    progetto = completo()
    reti_calde = {item.id for item in progetto.networks if item.medium == DHW}
    raccordi = sorted(
        {
            ref.component_id
            for connection in progetto.connections
            if connection.network_id in reti_calde
            for ref in (connection.endpoint_a, connection.endpoint_b)
            if "junction" in _funzioni(progetto, ref.component_id)
        }
    )
    assert raccordi == [], raccordi


def test_il_ricircolo_e_il_ritorno_dell_acqua_calda_e_si_disegna_verde_chiaro() -> None:
    """Il colore lo decide il modello (I-042): il ricircolo e' l'acqua calda che
    torna all'accumulo, cioe' il **ritorno** della rete sanitaria, e il ritorno
    dell'acqua calda sanitaria ha adesso il colore che il PO usa — verde chiaro
    — e una riga di legenda sua. La mandata sanitaria resta com'era."""
    progetto = completo()
    classificate = classify_trunks(progetto, catalogo(), _tratte(progetto))
    ricircolo = _ricircolo(progetto)
    assert classificate[ricircolo.connection_ids].supply is False

    mandate = [
        trunk
        for trunk in _tratte(progetto)
        if trunk.start.port_id == "dhw_out" or trunk.end.port_id == "dhw_out"
    ]
    assert mandate, "la mandata sanitaria non esce dall'accumulo"
    assert all(classificate[trunk.connection_ids].supply is True for trunk in mandate)

    assert style_for(DHW, supply=False)[0] == RECIRCULATION_COLOUR
    assert style_for(DHW, supply=True) == MEDIUM_STYLES[DHW]
    # Verde chiaro, e non uno dei colori che la tavola usa gia'.
    gia_usati = {colour for colour, _ in MEDIUM_STYLES.values()}
    assert RECIRCULATION_COLOUR not in gia_usati
    rosso, verde, blu = (int(RECIRCULATION_COLOUR[i : i + 2], 16) for i in (1, 3, 5))
    assert verde > rosso and verde > blu and min(rosso, verde, blu) > 60


def test_la_legenda_ha_la_riga_del_ricircolo() -> None:
    """La riga di legenda del ricircolo si chiama ricircolo, e c'e' solo se la
    tavola lo disegna."""
    progetto = completo()
    reti = tuple(item.id for item in progetto.networks)
    sanitaria = next(item.id for item in progetto.networks if item.medium == DHW)
    disegnate = [
        RoutedTrunk(
            network_id=sanitaria,
            medium=DHW,
            supply=supply,
            connection_ids=[f"x-{supply}"],
            segments=[[Point(x_mm=100.0, y_mm=101.0), Point(x_mm=150.0, y_mm=101.0)]],
        )
        for supply in (True, False)
    ]
    _, righe = build_legend(progetto, [], reti, catalogo(), NOVE_C_A3, routes=disegnate)
    per_nome = {item.name: item.colour for item in righe}
    assert per_nome == {
        "Acqua calda sanitaria — andata": MEDIUM_STYLES[DHW][0],
        "Acqua calda sanitaria — ricircolo": RECIRCULATION_COLOUR,
    }
    _, senza = build_legend(
        progetto, [], reti, catalogo(), NOVE_C_A3, routes=disegnate[:1]
    )
    assert [item.name for item in senza] == ["Acqua calda sanitaria — andata"]
