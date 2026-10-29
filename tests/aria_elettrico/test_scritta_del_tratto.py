"""La scritta del tratto come dato del grafo (REL-012, fase 1, punto 3).

Il contratto, che la distinta dei materiali (REL-013) legge: la tubazione ha tre campi
facoltativi, `sezione` (testo), `lunghezza_m` (numero positivo, dato del progettista)
e `scritta` (testo libero, che vince). Sulla tavola il tratto porta `scritta`, oppure
«{sezione} · L {lunghezza} m», oppure niente; la posa e' quella dei diametri, un DN
calcolato sullo stesso tratto cede il posto, e la legenda ha **la sua** riga «Ø · L»
accanto a quella del DN, che resta «Øi» (I-155).
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.scritte import (
    CAMPIONE_DELLA_LEGENDA,
    TESTO_DELLA_LEGENDA,
    numero_italiano,
    scritte_dei_tratti,
    tratti_da_scrivere,
)
from disegnatore_mep.diametri.scritte import (
    testo_della_tubazione as scritta_della_tubazione,
)
from disegnatore_mep.layout.diametri import riquadro_del_diametro
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.rules.apply import _derivation, _split

ROOT = Path(__file__).resolve().parents[2]


def _tubo(**campi: Any) -> ConnectionModel:
    return ConnectionModel.model_validate(
        {
            "id": "t",
            "network_id": "rete",
            "endpoint_a": {"component_id": "a", "port_id": "out"},
            "endpoint_b": {"component_id": "b", "port_id": "in"},
            **campi,
        }
    )


@pytest.mark.parametrize(
    ("campi", "atteso"),
    [
        ({"sezione": "Ø200", "lunghezza_m": 6}, "Ø200 · L 6 m"),
        ({"sezione": "Ø200", "lunghezza_m": 6.0}, "Ø200 · L 6 m"),
        ({"sezione": "3G2,5", "lunghezza_m": 3.5}, "3G2,5 · L 3,5 m"),
        ({"sezione": 'Ø6,35 (1/4")', "lunghezza_m": 12.25}, 'Ø6,35 (1/4") · L 12,25 m'),
        ({"sezione": "1000×250"}, "1000×250"),
        ({"lunghezza_m": 2}, "L 2 m"),
        ({"sezione": "Ø200", "lunghezza_m": 6, "scritta": "di fabbrica"}, "di fabbrica"),
        ({}, None),
    ],
)
def test_che_cosa_scrive_un_tratto(campi: dict[str, Any], atteso: str | None) -> None:
    assert scritta_della_tubazione(_tubo(**campi)) == atteso


def test_il_numero_all_italiana() -> None:
    assert [numero_italiano(v) for v in (6, 6.0, 3.5, 0.75, 12.25, 100)] == ["6", "6", "3,5", "0,75", "12,25", "100"]


@pytest.mark.parametrize(
    "campi",
    [{"lunghezza_m": 0}, {"lunghezza_m": -1}, {"lunghezza_m": float("inf")}, {"sezione": ""}, {"scritta": "   "},
     {"lunghezza_m": "6"}],
)
def test_il_modello_rifiuta_un_dato_che_non_si_legge(campi: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _tubo(**campi)


def test_vuoti_non_si_scrivono_e_i_grafi_agli_atti_restano_uguali() -> None:
    assert set(_tubo().model_dump(mode="json")) == {"id", "network_id", "endpoint_a", "endpoint_b", "properties", "evidence"}
    pieno = _tubo(sezione="Ø200", lunghezza_m=6).model_dump(mode="json")
    assert pieno["sezione"] == "Ø200" and pieno["lunghezza_m"] == 6
    agli_atti = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24" / "grafo-completo-1.json"
    testo = json.loads(agli_atti.read_text(encoding="utf-8"))
    assert ProjectModel.model_validate(testo).model_dump(mode="json")["connections"] == testo["connections"]


def test_lo_schema_del_progetto_porta_i_tre_campi() -> None:
    """Lo schema pubblicato e' quello del modello (`export-schema`), e porta i tre
    campi con la loro forma."""
    pubblicato = json.loads((ROOT / "schemas" / "project.schema.json").read_text(encoding="utf-8"))
    assert pubblicato == json.loads(json.dumps(ProjectModel.model_json_schema()))
    campi = pubblicato["$defs"]["ConnectionModel"]["properties"]
    assert {"type": "string", "minLength": 1} in campi["sezione"]["anyOf"]
    assert {"type": "number", "exclusiveMinimum": 0} in campi["lunghezza_m"]["anyOf"]
    assert {"type": "string", "minLength": 1} in campi["scritta"]["anyOf"]


def test_una_tubazione_spezzata_da_completa_tiene_la_scritta_su_una_meta() -> None:
    """Sezione e lunghezza sono del tratto intero: copiate sulle due meta', la tavola le
    scriverebbe due volte e la distinta conterebbe due volte la lunghezza."""

    class Proposta:
        component_id = "valvola"
        inlet_port = "a"
        outlet_port = "b"

    tubo = _tubo(sezione="Ø200", lunghezza_m=6)
    for prima, seconda in (_split(tubo, Proposta()), _derivation(tubo, Proposta(), "tee")):  # type: ignore[arg-type]
        assert (prima.sezione, prima.lunghezza_m) == ("Ø200", 6)
        assert (seconda.sezione, seconda.lunghezza_m, seconda.scritta) == (None, None, None)
        assert "sezione" not in seconda.model_dump(mode="json")


def test_un_tratto_con_un_dato_solo_e_una_scritta_per_tubazione_dove_sono_due(
    tavola: tuple[ProjectModel, Any], catalogo_aria: ComponentRegistry
) -> None:
    modello, _ = tavola
    scritte = {item.tubazione: item for item in scritte_dei_tratti(modello, catalogo_aria)}
    # La condensa: c-1 ha il dato, c-2 no; il sifone sta in mezzo. La scritta e' del
    # tratto intero.
    assert scritte["c-1"].connection_ids == frozenset({"c-1", "c-2"})
    assert "c-2" not in scritte
    # L'alimentazione: due cavi col loro dato, due scritte.
    assert scritte["e-1a"].connection_ids == frozenset({"e-1a"})
    assert scritte["e-1b"].connection_ids == frozenset({"e-1b"})
    assert scritte["e-1a"].scritta == "3G2,5 · L 20 m" and scritte["e-1b"].scritta == "3G2,5 · L 1,5 m"
    assert scritte["a-ripresa"].scritta == "1000×250 · L 2 m"


def test_sulla_tavola_ogni_scritta_sta_sulla_sua_tubazione(tavola: tuple[ProjectModel, Any]) -> None:
    """Ogni scritta c'e', una sola volta, e sta addosso alla **sua** polilinea: quella
    del cavo dal quadro al sezionatore e quella dal sezionatore alla macchina."""
    modello, esito = tavola
    foglio = esito.disegno.sheets[0]
    attese = {item.id: scritta_della_tubazione(item) for item in modello.connections if scritta_della_tubazione(item)}
    posate = {tuple(item.connection_ids): item for item in foglio.diametri}
    assert len(posate) == len(foglio.diametri) == len(attese)
    for tubazione, testo in attese.items():
        chiave = next(chiave for chiave in posate if tubazione in chiave)
        assert posate[chiave].testo == testo
    assert not [item for item in esito.rilievi if item.code.startswith(("DIAMETER_", "RUN_LABEL"))]
    # La scritta di un cavo spezzato dal sezionatore sta sul suo pezzo di linea.
    alimentazione = next(route for route in foglio.routes if "e-1a" in route.connection_ids)
    assert len(alimentazione.segments) == len(alimentazione.connection_ids) == 2
    corpo = esito.frame.standard.text_small_mm
    for indice, tubazione in enumerate(alimentazione.connection_ids):
        etichetta = posate[(tubazione,)]
        punta = etichetta.richiamo.punta if etichetta.richiamo is not None else None
        polilinea = alimentazione.segments[indice]
        xs = [p.x_mm for p in polilinea]
        ys = [p.y_mm for p in polilinea]
        if punta is not None:
            assert min(xs) - 1e-6 <= punta.x_mm <= max(xs) + 1e-6
            assert min(ys) - 1e-6 <= punta.y_mm <= max(ys) + 1e-6
        else:
            box = riquadro_del_diametro(etichetta, corpo)
            assert box[1] < max(ys) and box[3] > min(ys), (tubazione, box, ys)


def test_la_legenda_ha_la_riga_della_scritta_e_non_quella_del_dn(tavola: tuple[ProjectModel, Any]) -> None:
    _, esito = tavola
    note = esito.disegno.sheets[0].note_della_legenda
    assert [item.campione for item in note] == [CAMPIONE_DELLA_LEGENDA] == ["Ø · L"]
    assert " ".join(note[0].righe) == TESTO_DELLA_LEGENDA


def test_il_dn_calcolato_cede_il_posto_alla_scritta_del_progettista(
    catalogo_aria: ComponentRegistry,
) -> None:
    """L'impianto 1 con i diametri chiesti: il DN si calcola su sei tratti. Si da' una
    scritta a una tubazione di uno di loro: quel tratto porta la scritta, gli altri
    il DN, e la legenda ha le due righe, «Øi» e poi «Ø · L»."""
    from disegnatore_mep.diametri.tratti import tratti_da_etichettare

    diametri = json.loads((ROOT / "docs" / "collaudi" / "REL-007" / "dati-di-prova.json").read_text("utf-8"))
    grafo = json.loads(
        (ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24" / "grafo-completo-1.json").read_text(
            "utf-8"
        )
    )
    dati = diametri["impianti"]["1"]
    pezzi = {item["id"]: item for item in grafo["components"]}
    for ident, proprieta in dati["pezzi"].items():
        pezzi[ident]["properties"].update(proprieta)
    reti = [item["id"] for item in grafo["networks"]]
    grafo["diametri"] = {"reti": reti if dati["reti"] == "tutte" else dati["reti"]}
    senza = ProjectModel.model_validate(grafo)
    calcolati = tratti_da_etichettare(senza, catalogo_aria)
    assert calcolati
    bersaglio = sorted(calcolati[0].connection_ids)[0]
    for tubo in grafo["connections"]:
        if tubo["id"] == bersaglio:
            tubo["sezione"], tubo["lunghezza_m"] = "DN 40 esistente", 7
    con = ProjectModel.model_validate(grafo)
    scritte, rimasti = tratti_da_scrivere(con, catalogo_aria)
    assert [item.tubazione for item in scritte] == [bersaglio]
    assert len(rimasti) == len(calcolati) - 1
    assert all(bersaglio not in item.connection_ids for item in rimasti)


def test_un_dn_e_una_scritta_sulla_stessa_tavola_hanno_due_righe_di_legenda(
    progetto: Callable[..., ProjectModel],
) -> None:
    """La legenda in ordine: «Øi» dove stava, «Ø · L» sotto (`note_della_legenda`)."""
    from disegnatore_mep.graphics.frame import NOVE_C_A3
    from disegnatore_mep.layout.diametri import note_della_legenda
    from disegnatore_mep.layout.geometry import NetworkKey, Point, SheetGeometry

    foglio = SheetGeometry(
        sheet_id="t1",
        title="prova",
        network_keys=[
            NetworkKey(medium="supply_air", name="Aria di mandata", colour="#148f77", dash="none",
                       anchor=Point(x_mm=362.5, y_mm=40))
        ],
    )
    note = note_della_legenda(foglio, NOVE_C_A3, [("Øi", "diametro interno"), ("Ø · L", TESTO_DELLA_LEGENDA)])
    assert [item.campione for item in note] == ["Øi", "Ø · L"]
    assert note[0].anchor.y_mm == 47.5
    assert note[1].anchor.y_mm > note[0].anchor.y_mm
