"""I simboli nuovi del primo caso reale, disegnati (REL-009, I-194).

La tavola di prova `docs/collaudi/REL-009/simboli-nuovi/` mette in un impianto piccolo
il contatore di calore, l'attacco predisposto con la sua scritta, il volano a sei
attacchi, il collettore con mandata e ritorno e i confini con l'impianto esistente. Si
disegna dal suo grafo e dal suo piano, col comando della skill, e deve uscire: zero
tratte cedute, zero bloccanti, e le scritte del progettista scritte.
"""

# categoria: difende il prodotto — I-194, le voci nuove si disegnano e le scritte libere non si perdono

from pathlib import Path

import pytest

from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "REL-009" / "simboli-nuovi"


@pytest.fixture(scope="module")
def tavola(tmp_path_factory: pytest.TempPathFactory) -> Path:
    cartelle = cartelle_del_repository(ROOT)
    uscita = tmp_path_factory.mktemp("simboli")
    assert main(["completa", str(PROVA / "grafo.json"), "--out", str(uscita / "completo.json")], cartelle) == 0
    codice = main(
        ["disegna", str(uscita / "completo.json"), "--piano", str(PROVA / "piano.json"), "--out", str(uscita / "t")],
        cartelle,
    )
    assert codice == 0, "la tavola dei simboli nuovi si consegna"
    return uscita / "t"


def test_la_tavola_dei_simboli_nuovi_esce_senza_bloccanti(tavola: Path) -> None:
    rilievi = next(tavola.glob("*-rilievi.md")).read_text(encoding="utf-8")
    assert "tratte cedute **0**" in rilievi and "rilievi bloccanti **0**" in rilievi


def test_i_simboli_nuovi_ci_sono_e_le_scritte_sono_scritte(tavola: Path) -> None:
    svg = next(tavola.glob("*.svg")).read_text(encoding="utf-8")
    for simbolo in (
        "heat-meter", "capped-connection", "buffer-six-port", "zone-manifold-pair",
        "flexible-joint", "polyphosphate-doser",
    ):
        assert simbolo in svg, simbolo
    for scritta in ("al solare termico", "verso impianto esistente", "da impianto esistente"):
        assert scritta in svg, scritta


def test_la_mandata_del_predisposto_entra_dall_alto() -> None:
    """I-197: «la mandata e' sempre sopra il suo ritorno». L'attacco predisposto che
    immette sta per il collettore solare che verra': la sua tubazione e' mandata, ed
    entra nel volano dall'attacco alto; quella che esce dall'attacco basso e' ritorno."""
    from disegnatore_mep.catalog.registry import ComponentRegistry
    from disegnatore_mep.graphics.registry import SymbolRegistry
    from disegnatore_mep.io.project_json import load_project
    from disegnatore_mep.layout.flow import classify_trunks
    from disegnatore_mep.layout.trunks import build_trunks

    catalogo = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )
    modello = load_project(PROVA / "grafo.json")
    in_linea = frozenset(
        item.id for item in modello.components if catalogo.resolve(item.definition_id).is_inline
    )
    tratte = build_trunks(modello, in_linea)
    verso = classify_trunks(modello, catalogo, tratte)
    ruolo = {
        connessione: verso[item.connection_ids].supply
        for item in tratte
        for connessione in item.connection_ids
    }
    assert ruolo["x1"] is True, "dal tappo alto, verso aux_in: mandata"
    assert ruolo["x2"] is False, "da aux_out verso il tappo basso: ritorno"
    porte = {item.id: item for item in catalogo.get("buffer-six-port").ports}
    simbolo = SymbolRegistry.from_directory(ROOT / "assets" / "symbols").get("buffer-six-port").manifest
    quota = {item.id: item.y_mm for item in simbolo.ports}
    assert "aux_in" in porte and quota["aux_in"] < quota["aux_out"], "la mandata sta sopra"


def test_il_giunto_antivibrante_sta_attaccato_alla_macchina(tmp_path: Path) -> None:
    """I-197: il giunto antivibrante e' fra la macchina e il resto, e le regole posano i
    loro organi oltre il giunto, non fra lui e la pompa di calore."""
    import json

    cartelle = cartelle_del_repository(ROOT)
    assert main(["completa", str(PROVA / "grafo.json"), "--out", str(tmp_path / "c.json")], cartelle) == 0
    grafo = json.loads((tmp_path / "c.json").read_text(encoding="utf-8"))
    vicini = {
        (item["endpoint_a"]["component_id"], item["endpoint_b"]["component_id"])
        for item in grafo["connections"]
        if "pdc" in (item["endpoint_a"]["component_id"], item["endpoint_b"]["component_id"])
    }
    assert vicini == {("pdc", "giunto-mandata"), ("giunto-ritorno", "pdc")}
    # Oltre il giunto la fila si conta dalla macchina: il filtro della pompa di calore
    # le sta vicino come senza giunto.
    oltre = {
        ref["component_id"]
        for item in grafo["connections"]
        for ref, altro in ((item["endpoint_a"], item["endpoint_b"]), (item["endpoint_b"], item["endpoint_a"]))
        if altro["component_id"] == "giunto-ritorno" and ref["component_id"] != "pdc"
    }
    assert oltre == {"strainer-pdc-water-return"}
