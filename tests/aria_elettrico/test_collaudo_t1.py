"""Le correzioni di libreria e motore dopo il primo collaudo indipendente (REL-012, T1).

Il rapporto e' `docs/collaudi/REL-012/collaudo-t1/RAPPORTO.md`: un canalizzato reale con un
plenum a quattro uscite. Qui le correzioni di libreria e del motore dello schema, una per
una, ciascuna con la sua prova:

1. **il plenum di zona a N uscite** (§2.1, bloccante): da due a sei serrande;
2. **le sigle dei pezzi fuori dall'acqua** (§2.2.6, §3): bocchette, termostati, quadro,
   sezionatore, ripresa, sifone, scarico — e le sigle cedono il posto alle scritte dei
   tratti, che sono un dato del progettista;
3. **la scritta di un pezzo lungo una linea scritta** (§3, «Terrazzo» sulla linea del gas):
   la posa la evita, il preflight la vede;
4. **i monconi delle porte libere** (§3): una porta che nessuna linea collega non disegna
   niente — solo sui simboli dell'aria-aria e del comando;
5. **il quadro fino a sei uscite** (fase 3 e collaudo).

Che le tavole idroniche non cambino lo misura il banco di REL-011, non queste prove.
"""

import contextlib
import io
import json
import re
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.errors import SymbolError
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.tabella import fuori_dall_acqua
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.geometry import (
    DiametroSullaTavola,
    DrawingGeometry,
    PlacedLabel,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.layout.labels import riquadro_della_scritta
from disegnatore_mep.model.types import Domain
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.skill import cartelle_del_repository, main
from disegnatore_mep.validation import preflight

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
CORREZIONI = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t1" / "correzioni"

IN_LETTERE = {2: "due", 3: "tre", 4: "quattro", 5: "cinque", 6: "sei"}


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def il_collaudo() -> EsitoDelPiano:
    """Lo schema del collaudo T1 col plenum a quattro serrande, eseguito col suo piano."""
    return esegui_piano(
        load_project(CORREZIONI / "grafo.json"), carica_piano(CORREZIONI / "piano.json"), catalogo(), simboli(), NAMING
    )


def il_foglio() -> SheetGeometry:
    esito = il_collaudo()
    assert esito.disegno is not None, esito.errore
    return esito.disegno.sheets[0]


# --- 1. il plenum di zona a N uscite --------------------------------------------------


@pytest.mark.parametrize("uscite", [2, 3, 4, 5, 6])
def test_il_catalogo_ha_il_plenum_da_due_a_sei_serrande(uscite: int) -> None:
    voce = catalogo().get(f"zoning-plenum-{uscite}")
    assert voce.name == f"Plenum motorizzato di zona a {IN_LETTERE[uscite]} serrande"
    assert voce.functions == ["air_zoning"]
    serrande = [porta for porta in voce.ports if porta.id.startswith("out_")]
    assert [porta.id for porta in serrande] == [f"out_{indice}" for indice in range(1, uscite + 1)]
    # Ogni uscita e' obbligatoria: una serranda che non porta a una bocchetta non c'e'.
    assert all(porta.required for porta in voce.ports)
    manifesto = simboli().get(f"zoning-plenum-{uscite}").manifest
    assert manifesto.width_mm == 40.0
    assert manifesto.height_mm == 7.5 + 12.5 * (uscite - 1)
    quote = [manifesto.port(f"out_{indice}").y_mm for indice in range(1, uscite + 1)]
    assert quote == [5.0 + 12.5 * indice for indice in range(uscite)]
    assert manifesto.port("in").y_mm == 12.5
    assert manifesto.allowed_rotations_deg == [0]


def test_il_plenum_a_cinque_resta_quello_della_m02() -> None:
    """La M.02 lo usa: id, porte e quote sono quelle del kit."""
    manifesto = simboli().get("zoning-plenum-5").manifest
    assert (manifesto.width_mm, manifesto.height_mm) == (40.0, 57.5)
    assert [(porta.id, porta.face.value, porta.x_mm, porta.y_mm) for porta in manifesto.ports] == [
        ("in", "left", 0.0, 12.5),
        ("motori", "bottom", 20.0, 57.5),
        *((f"out_{i + 1}", "right", 40.0, y) for i, y in enumerate((5.0, 17.5, 30.0, 42.5, 55.0))),
    ]


def test_il_canalizzato_a_quattro_uscite_si_valida_e_si_disegna(tmp_path: Path) -> None:
    """Il collaudo si era fermato qui: `REQUIRED_PORT_UNCONNECTED · plenum, out_5`."""
    cartelle = cartelle_del_repository(ROOT)
    grafo = CORREZIONI / "grafo.json"
    assert json.loads(grafo.read_text(encoding="utf-8"))["components"][2]["definition_id"] == "zoning-plenum-4"
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        assert main(["valida", str(grafo)], cartelle) == 0
        assert main(["completa", str(grafo), "--out", str(tmp_path / "gc.json")], cartelle) == 0
        codice = main(
            ["disegna", str(tmp_path / "gc.json"), "--piano", str(CORREZIONI / "piano.json"),
             "--out", str(tmp_path / "tavola"), "--senza-dxf"],
            cartelle,
        )
    assert codice == 0, uscita.getvalue()
    assert "tratte cedute 0 · rilievi bloccanti 0" in uscita.getvalue()
    svg = next((tmp_path / "tavola").glob("*.svg")).read_text(encoding="utf-8")
    # La tabella delle apparecchiature dice quante serrande ha il plenum.
    assert "Plenum motorizzato di zona a quattro serrande" in svg
    assert "cinque serrande" not in svg


# --- 2. le sigle dei pezzi fuori dall'acqua ---------------------------------------------


def test_le_voci_fuori_dall_acqua_sono_quelle_senza_un_attacco_d_acqua() -> None:
    for voce in catalogo().all():
        acqua = any(porta.domain is Domain.HYDRONIC for porta in voce.ports)
        assert fuori_dall_acqua(voce) is not acqua, voce.id
    for voce_id in (
        "air-supply-terminal", "return-air-terminal", "room-thermostat", "electrical-panel",
        "isolator-switch", "condensate-trap", "condensate-outlet",
    ):
        assert fuori_dall_acqua(catalogo().get(voce_id)), voce_id


def test_bocchette_termostati_quadro_sezionatore_ripresa_e_scarico_portano_la_sigla() -> None:
    foglio = il_foglio()
    scritte = {label.id: label.text for label in foglio.labels if label.role == "tag"}
    attese = {
        "bocchetta-matrimoniale": "TA-01", "bocchetta-singola": "TA-02",
        "bocchetta-soggiorno-1": "TA-03", "bocchetta-soggiorno-2": "TA-04",
        "termostato-matrimoniale": "TZ-01", "termostato-singola": "TZ-02", "termostato-soggiorno": "TZ-03",
        "quadro": "QE-01", "sezionatore": "SZ-01", "ripresa": "RA-01", "scarico-cucina": "AL-01",
    }
    for pezzo, sigla in attese.items():
        assert scritte.get(f"{pezzo}-tag") == sigla, pezzo
    # Il sifone la sigla ce l'ha; sul tratto corto fra unita' interna e scarico non trova
    # un posto che non tolga quello della scritta del tratto, e cede: un avviso.
    sifone = next(item for item in foglio.symbols if item.component_id == "sifone")
    assert sifone.tag == "SIF-01"
    # Una sigla sola per pezzo: quelle della tabella non si ripetono.
    assert len(scritte) == len(set(scritte))


def test_le_sigle_cedono_il_posto_alle_scritte_dei_tratti() -> None:
    """Con le sigle posate insieme alle altre, quella del sezionatore e quella del sifone
    toglievano il posto alla scritta del loro tratto: `RUN_LABEL_OMITTED`, bloccante."""
    esito = il_collaudo()
    assert esito.bloccanti == []
    assert not [item for item in esito.rilievi if item.code == "RUN_LABEL_OMITTED"]
    assert {item.code for item in esito.rilievi} <= {"TAG_OMITTED", "SERVICE_STUB_LONGER_THAN_ITS_MINIMUM"}


# --- 3. la scritta di un pezzo lungo una linea scritta ----------------------------------


def _due_linee_frigo(tmp_path: Path) -> EsitoDelPiano:
    """Il piccolo grafo del rilievo: l'unita' esterna con la sua scritta, le due linee
    frigorifere scritte all'altezza dell'unita' interna, e sotto l'unita' esterna il
    collegamento, il sezionatore e il quadro — come sul collaudo, dove sotto non c'era
    posto e la scritta finiva a destra, sulla linea del gas."""

    def porta(pezzo: str, attacco: str) -> dict[str, str]:
        return {"component_id": pezzo, "port_id": attacco}

    def rete(rete_id: str, dominio: str, fluido: str) -> dict[str, str]:
        return {"id": rete_id, "name": rete_id, "domain": dominio, "medium": fluido}

    def tubazione(
        tubazione_id: str, rete_id: str, da: dict[str, str], a: dict[str, str], **dati: object
    ) -> dict[str, object]:
        return {"id": tubazione_id, "network_id": rete_id, "endpoint_a": da, "endpoint_b": a, **dati}

    grafo = {
        "schema_version": "1.1.0",
        "metadata": {
            "project_id": "terrazzo", "client": "prova", "project_name": "prova",
            "commission_code": "PROVA", "revision": "00", "issue_date": "2026-10-29",
        },
        "networks": [
            rete("liquido", "refrigerant", "refrigerant_liquid"),
            rete("gas", "refrigerant", "refrigerant_gas"),
            rete("link", "control", "interconnection"),
            rete("alim", "control", "power_supply"),
        ],
        "components": [
            {"id": "ue", "definition_id": "split-outdoor-unit", "properties": {"etichetta": "Terrazzo"}},
            {"id": "ui", "definition_id": "ducted-indoor-unit", "properties": {}},
            {"id": "quadro", "definition_id": "electrical-panel", "properties": {"etichetta": "Ingresso"}},
            {"id": "sezionatore", "definition_id": "isolator-switch",
             "properties": {"etichetta": "vicino all'unita' esterna"}},
        ],
        "connections": [
            tubazione("c-liquido", "liquido", porta("ue", "liquid"), porta("ui", "liquid"),
                      sezione='1/4"', lunghezza_m=9),
            tubazione("c-gas", "gas", porta("ue", "gas"), porta("ui", "gas"), sezione='5/8"', lunghezza_m=9),
            tubazione("c-link", "link", porta("ue", "link"), porta("ui", "link"), sezione="4G1,5", lunghezza_m=10),
            tubazione("c-alim-1", "alim", porta("quadro", "out_1"), porta("sezionatore", "a"),
                      sezione="3G4", lunghezza_m=18),
            tubazione("c-alim-2", "alim", porta("sezionatore", "b"), porta("ue", "power"), sezione="3G4"),
        ],
    }
    piano = {"formato": "A3", "pezzi": {"ue": {"x": 0, "y": 0}, "ui": {"x": 100, "y": 0},
                                        "quadro": {"x": 2.5, "y": 115}}}
    (tmp_path / "grafo.json").write_text(json.dumps(grafo), encoding="utf-8")
    (tmp_path / "piano.json").write_text(json.dumps(piano), encoding="utf-8")
    return esegui_piano(
        load_project(tmp_path / "grafo.json"), carica_piano(tmp_path / "piano.json"), catalogo(), simboli(), NAMING
    )


def test_la_scritta_dell_unita_esterna_non_sta_sulla_linea_del_gas(tmp_path: Path) -> None:
    esito = _due_linee_frigo(tmp_path)
    assert esito.disegno is not None, esito.errore
    foglio = esito.disegno.sheets[0]
    corpo = esito.frame.standard.text_small_mm
    terrazzo = next(label for label in foglio.labels if label.text == "Terrazzo")
    x0, y0, x1, y1 = riquadro_della_scritta(terrazzo, corpo)
    for route in foglio.routes:
        for tratto in route.segments:
            for prima, dopo in zip(tratto, tratto[1:], strict=False):
                if abs(prima.y_mm - dopo.y_mm) > 1e-6:
                    continue
                lungo = min(x1, max(prima.x_mm, dopo.x_mm)) - max(x0, min(prima.x_mm, dopo.x_mm))
                vicina = y0 - corpo < prima.y_mm < y1 + corpo
                assert not (lungo > 0 and vicina), f"«Terrazzo» sta lungo {route.connection_ids}"
    assert not [item for item in esito.rilievi if item.code == "PIECE_LABEL_ALONG_A_WRITTEN_RUN"]
    assert esito.bloccanti == []


def _foglio_con_una_scritta_lungo_la_linea(del_progettista: bool) -> DrawingGeometry:
    def a(x: float, y: float) -> Point:
        return Point(x_mm=x, y_mm=y)

    linea = RoutedTrunk(network_id="gas", medium="refrigerant_gas", connection_ids=["c-gas"],
                        segments=[[a(100, 103.5), a(160, 103.5)]])
    foglio = SheetGeometry(
        sheet_id="t1", title="prova", routes=[linea],
        labels=[PlacedLabel(id="ue-etichetta", text="Terrazzo", role="data", anchor=a(104, 102.6))],
        diametri=[DiametroSullaTavola(testo='5/8" · L 9 m', ancora=a(124, 102.2), connection_ids=["c-gas"],
                                      del_progettista=del_progettista)],
    )
    return DrawingGeometry(project_id="prova", sheets=[foglio])


def test_il_preflight_vede_una_scritta_di_pezzo_lungo_una_linea_scritta() -> None:
    from disegnatore_mep.graphics.frame import NOVE_C_A3

    trovati = preflight.labels_along_written_runs(_foglio_con_una_scritta_lungo_la_linea(True), NOVE_C_A3)
    assert [item.code for item in trovati] == ["PIECE_LABEL_ALONG_A_WRITTEN_RUN"]
    assert "Terrazzo" in trovati[0].message
    # Il DN calcolato non conta: le tavole idroniche di prima non cambiano.
    assert preflight.labels_along_written_runs(_foglio_con_una_scritta_lungo_la_linea(False), NOVE_C_A3) == []


# --- 4. i monconi delle porte libere ----------------------------------------------------


def test_la_centrale_di_zona_non_disegna_il_bus_che_nessuno_usa() -> None:
    foglio = il_foglio()
    posati = {item.component_id: item for item in foglio.symbols}
    assert posati["centrale-zona"].porte_scollegate == ["bus_4"]
    assert posati["quadro"].porte_scollegate == ["out_3", "out_4", "out_5", "out_6"]
    assert posati["ui"].porte_scollegate == []
    svg = render_sheet(foglio, il_collaudo().frame, simboli())
    centrale = re.search(r'<g class="symbol" data-component-id="centrale-zona".*?</g></g>', svg)
    assert centrale is not None
    assert 'data-port="bus_3"' in centrale.group(0)
    assert 'data-port="bus_4"' not in centrale.group(0)


def test_il_dxf_disegna_la_centrale_senza_il_moncone_libero(tmp_path: Path) -> None:
    ezdxf = pytest.importorskip("ezdxf")
    from disegnatore_mep.graphics.dxf import write_dxf

    write_dxf(il_foglio(), il_collaudo().frame, simboli(), tmp_path / "t.dxf")
    documento = ezdxf.readfile(tmp_path / "t.dxf")
    intero = documento.blocks.get("NoveC_ZoneController")
    ridotto = documento.blocks.get("NoveC_ZoneController_V1")
    assert ridotto is not None
    inseriti = {item.dxf.name for item in documento.modelspace().query("INSERT")}
    assert "NoveC_ZoneController_V1" in inseriti
    assert len(list(ridotto)) < len(list(intero))


def test_i_simboli_idronici_non_hanno_monconi_da_togliere() -> None:
    """Il moncone in un gruppo suo e' dei soli simboli dell'aria-aria e del comando: un
    simbolo usato da una voce con un attacco d'acqua resta quello di prima, byte per byte."""
    con_acqua = {
        voce.symbol_id for voce in catalogo().all() if any(p.domain is Domain.HYDRONIC for p in voce.ports)
    }
    for simbolo_id in con_acqua:
        assert simboli().get(simbolo_id).porte_col_moncone == frozenset(), simbolo_id
    for simbolo_id in ("split-outdoor-unit", "ducted-indoor-unit", "zone-controller", "electrical-panel",
                       "plant-controller", *(f"zoning-plenum-{n}" for n in range(2, 7))):
        manifesto = simboli().get(simbolo_id).manifest
        # La porta dei motori del plenum sta sul bordo: un moncone non ce l'ha.
        attese = manifesto.port_ids - {"motori"} if simbolo_id.startswith("zoning-plenum") else manifesto.port_ids
        assert simboli().get(simbolo_id).porte_col_moncone == attese, simbolo_id


def test_un_gruppo_di_porta_che_non_nomina_una_porta_non_si_carica(tmp_path: Path) -> None:
    sorgente = SYMBOLS / "electrical-panel"
    (tmp_path / "electrical-panel.json").write_text(sorgente.with_suffix(".json").read_text(), encoding="utf-8")
    corpo = sorgente.with_suffix(".svg").read_text().replace('data-port="out_6"', 'data-port="out_9"')
    (tmp_path / "electrical-panel.svg").write_text(corpo, encoding="utf-8")
    with pytest.raises(SymbolError, match="out_9"):
        SymbolRegistry.from_directory(tmp_path)


# --- 5. il quadro fino a sei uscite -----------------------------------------------------


def test_il_quadro_ha_sei_uscite_e_la_prima_sola_e_obbligatoria() -> None:
    voce = catalogo().get("electrical-panel")
    uscite = {porta.id: porta.required for porta in voce.ports}
    assert uscite == {"out_1": True, **{f"out_{i}": False for i in range(2, 7)}}
    manifesto = simboli().get("electrical-panel").manifest
    # Le due del kit dove sono sempre state, sopra.
    assert (manifesto.port("out_1").face.value, manifesto.port("out_1").x_mm) == ("top", 7.5)
    assert (manifesto.port("out_2").face.value, manifesto.port("out_2").x_mm) == ("top", 17.5)


def test_il_quadro_alimenta_tre_utenze(tmp_path: Path) -> None:
    """Fase 3: il circolatore finiva alimentato dal regolatore perche' il quadro aveva due
    uscite. Ora la terza c'e'."""
    grafo = json.loads((CORREZIONI / "grafo.json").read_text(encoding="utf-8"))
    grafo["networks"].append(
        {"id": "alim-regolatore", "name": "Alimentazione", "domain": "control", "medium": "power_supply"}
    )
    grafo["components"].append({"id": "regolatore", "definition_id": "plant-controller", "tag": None,
                                "properties": {}})
    grafo["connections"].append({
        "id": "c-alim-regolatore", "network_id": "alim-regolatore",
        "endpoint_a": {"component_id": "quadro", "port_id": "out_3"},
        "endpoint_b": {"component_id": "regolatore", "port_id": "power"}, "properties": {},
    })
    (tmp_path / "grafo.json").write_text(json.dumps(grafo), encoding="utf-8")
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        codice = main(["valida", str(tmp_path / "grafo.json")], cartelle_del_repository(ROOT))
    assert codice == 0, uscita.getvalue()
