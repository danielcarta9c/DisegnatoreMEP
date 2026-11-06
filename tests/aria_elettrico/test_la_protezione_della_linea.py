"""L'interruttore magnetotermico differenziale sulla linea della pompa di calore (REL-018, I-278).

Il PO, sulla tavola dell'elettrico uscita in sessione per una commessa: «è uscita senza le
protezioni elettriche (che interruttori ecc... )». Il catalogo non le aveva mai avute.

Cinque cose:

1. **la voce** `circuit-breaker-rcbo` — passante sull'alimentazione come il sezionatore, sigla
   QF, in tabella e in legenda solo sulla tavola dell'elettrico, coi suoi dati («2P C32 · Idn
   30 mA tipo B»), numeri positivi;
2. **il grafo minimo** (`docs/collaudi/REL-018/protezione/`) — quadro, QF-01, Shenling 12 kW,
   cavo 3G6 · L 15 m — si valida, si completa coi dati del manuale scritti e detti, e si
   disegna a 0 bloccanti con l'interruttore stretto all'uscita del quadro;
3. **i dati del manuale** (`elettrico.costruttori`): scritti dove mancano, mai sopra quelli del
   progettista; la monofase assunta e detta; il trifase solo se dichiarato;
4. **gli avvisi**: C25 su una 15 kW, 3G4 su una 12 kW, la linea dal quadro senza interruttore;
5. **la distinta, Capire e Comporre**.
"""
# categoria: difende il motore

import contextlib
import io
import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.riduzioni import posa_le_riduzioni
from disegnatore_mep.distinta import carica_regole, componi_la_distinta
from disegnatore_mep.distinta.comando import nomi_dei_fluidi, nomi_del_catalogo
from disegnatore_mep.distinta.grafo import sigle_dello_schema
from disegnatore_mep.elettrico.costruttori import (
    SHENLING_THERMAX_R290_LINEA,
    avvisi_della_linea,
    scrivi_i_dati_del_manuale,
)
from disegnatore_mep.elettrico.protezione import scritta_della_protezione, sezione_in_mm2
from disegnatore_mep.graph import Naming, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.tabella import dati_elettrici
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ComponentInstance, ProjectModel
from disegnatore_mep.model.types import Domain, IssueSeverity
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.piano.vista import vista_del_grafo
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.skill import cartelle_del_repository, main
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
CASO = ROOT / "docs" / "collaudi" / "REL-018" / "protezione"
CAPIRE = ROOT / "skill" / "capire" / "ISTRUZIONI.md"
COMPORRE = ROOT / "skill" / "comporre" / "ISTRUZIONI.md"
CORREDO = ROOT / "rules" / "distinta" / "corredo.json"
VOCE = "circuit-breaker-rcbo"


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def tavola() -> EsitoDelPiano:
    esito = esegui_piano(
        load_project(CASO / "grafo-completo.json"),
        carica_piano(CASO / "piano-elettrico.json"),
        catalogo(),
        simboli(),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    return esito


def _bloccanti(grafo: ProjectModel) -> list[tuple[str, str]]:
    rilievi = validate_project(grafo, catalogo().per_il_progetto(grafo))
    return [(item.code, item.message) for item in rilievi.issues if item.severity is IssueSeverity.BLOCKING]


def _grafo(**ritocchi: Any) -> dict[str, Any]:
    """Il grafo minimo di prima stesura, con i dati della macchina, dell'interruttore e del
    cavo cambiati: `pdc`, `qf` (None toglie l'interruttore), `sezione`."""
    grafo: dict[str, Any] = json.loads((CASO / "grafo.json").read_text(encoding="utf-8"))
    pezzi = {p["id"]: p for p in grafo["components"]}
    pezzi["pdc"]["properties"].update(ritocchi.get("pdc", {}))
    if "qf" in ritocchi and ritocchi["qf"] is None:
        grafo["components"] = [p for p in grafo["components"] if p["id"] != "qf-pdc"]
        grafo["connections"] = [t for t in grafo["connections"] if t["id"] not in {"t4", "t5"}]
        grafo["connections"].append(
            {
                "id": "t4",
                "network_id": "el-pdc",
                "endpoint_a": {"component_id": "quadro", "port_id": "out_1"},
                "endpoint_b": {"component_id": "pdc", "port_id": "power"},
                "properties": {},
                "sezione": "3G6",
                "lunghezza_m": 15,
            }
        )
    else:
        pezzi["qf-pdc"]["properties"].update(ritocchi.get("qf", {}))
    if "sezione" in ritocchi:
        for tubazione in grafo["connections"]:
            if tubazione.get("sezione"):
                tubazione["sezione"] = ritocchi["sezione"]
    return grafo


def _completa(grafo: dict[str, Any], tmp_path: Path) -> tuple[str, ProjectModel]:
    entrata = tmp_path / "grafo.json"
    entrata.write_text(json.dumps(grafo, ensure_ascii=False), encoding="utf-8")
    uscita = tmp_path / "grafo-completo.json"
    stampa = io.StringIO()
    with contextlib.redirect_stdout(stampa):
        codice = main(["completa", str(entrata), "--out", str(uscita)], cartelle_del_repository(ROOT))
    assert codice == 0, stampa.getvalue()
    return stampa.getvalue(), load_project(uscita)


def _proprieta(grafo: ProjectModel, pezzo: str) -> dict[str, Any]:
    return dict(next(p for p in grafo.components if p.id == pezzo).properties)


# --- 1. la voce -----------------------------------------------------------------------------


def test_la_voce_e_un_passante_dell_alimentazione_come_il_sezionatore() -> None:
    voce = ComponentRegistry.from_directory(CATALOG).get(VOCE)
    assert voce.name == "Interruttore magnetotermico differenziale"
    assert voce.functions == ["circuit_protection"]
    porte = {porta.id: porta for porta in voce.ports}
    assert set(porte) == {"a", "b"}
    for nome, verso in (("a", "in"), ("b", "out")):
        assert porte[nome].domain is Domain.CONTROL
        assert (porte[nome].medium, porte[nome].flow.value) == ("power_supply", verso)
        assert porte[nome].required is True
    assert catalogo().resolve(VOCE).is_inline
    manifesto = simboli().get(VOCE).manifest
    assert {(porta.id, porta.face.value) for porta in manifesto.ports} == {("a", "left"), ("b", "right")}
    assert manifesto.allowed_rotations_deg == simboli().get("isolator-switch").manifest.allowed_rotations_deg
    # Largo come il termostato a contatto: tre segni (toroide, lama, «×») in 5 mm non si leggono.
    assert (manifesto.width_mm, manifesto.height_mm) == (10.0, 5.0)


def test_la_sigla_e_qf_e_il_sezionatore_resta_sz() -> None:
    naming = Naming.from_directory(NAMING)
    voci = ComponentRegistry.from_directory(CATALOG)
    assert naming.family_of(tuple(voci.get(VOCE).functions), VOCE).prefix == "QF"
    assert naming.family_of(tuple(voci.get("isolator-switch").functions), "isolator-switch").prefix == "SZ"
    grafo = load_project(CASO / "grafo-completo.json")
    sigle = read_plant(grafo, catalogo().per_il_progetto(grafo), naming).sigle
    assert sigle["qf-pdc"] == "QF-01"


def test_la_caratteristica_si_scrive_poli_curva_in_idn_e_tipo() -> None:
    dati = {"poli": "2P", "curva": "C", "in_a": 32, "idn_ma": 30, "tipo_differenziale": "B", "alta_velocita": True}
    assert scritta_della_protezione(dati) == ["2P C32", "Idn 30 mA tipo B"]
    assert dati_elettrici(("circuit_protection",), dati) == ["2P C32", "Idn 30 mA tipo B"]
    # Un dato che manca non si scrive, e non si indovina.
    assert scritta_della_protezione({"in_a": 25, "tipo_differenziale": "B"}) == ["25 A", "tipo B"]
    assert scritta_della_protezione({}) == []
    # Solo l'interruttore porta questi dati in tabella.
    assert dati_elettrici(("circulation",), dati) == []


@pytest.mark.parametrize("dati", [{"in_a": -32}, {"in_a": 0}, {"idn_ma": "30 mA"}, {"in_a": True}])
def test_in_e_idn_sono_numeri_positivi(dati: dict[str, Any]) -> None:
    with pytest.raises(ValidationError, match=next(iter(dati))):
        ComponentInstance(id="qf", definition_id=VOCE, properties=dati)


def test_la_sezione_del_cavo_si_legge_dal_testo_del_progettista() -> None:
    assert [sezione_in_mm2(t) for t in ("3G6", "3G4", "5G2,5", "6 mm²", "3x1,5", "3×6")] == [6, 4, 2.5, 6, 1.5, 6]
    assert sezione_in_mm2("FG16OR16 3G6") is None
    assert sezione_in_mm2("Ø200") is None
    assert sezione_in_mm2(None) is None


# --- 2. il grafo minimo ---------------------------------------------------------------------


def test_il_grafo_minimo_si_valida_e_il_completo_e_la_rigenerazione() -> None:
    for nome in ("grafo.json", "grafo-completo.json"):
        assert _bloccanti(load_project(CASO / nome)) == [], nome
    grafo = load_project(CASO / "grafo.json")
    cat = catalogo().per_il_progetto(grafo)
    completo, _, _ = saturate(grafo, cat, RuleRegistry.from_directory(ROOT / "rules" / "hydronic"))
    completo, _ = posa_le_riduzioni(completo, cat)
    completo, _ = scrivi_i_dati_del_manuale(completo, cat)
    assert canonical_json(completo) == (CASO / "grafo-completo.json").read_text(encoding="utf-8")
    cavi = {
        frozenset({(t.endpoint_a.component_id, t.endpoint_a.port_id), (t.endpoint_b.component_id, t.endpoint_b.port_id)})
        for t in completo.connections
    }
    assert frozenset({("quadro", "out_1"), ("qf-pdc", "a")}) in cavi
    assert frozenset({("qf-pdc", "b"), ("pdc", "power")}) in cavi
    # Niente sezionatore locale: la specifica (§3.2) non lo chiede come regola.
    assert "isolator-switch" not in {p.definition_id for p in completo.components}


def test_completa_scrive_i_dati_del_manuale_e_lo_dice(tmp_path: Path) -> None:
    stampa, completo = _completa(_grafo(), tmp_path)
    macchina, interruttore = _proprieta(completo, "pdc"), _proprieta(completo, "qf-pdc")
    assert (macchina["alimentazione"], macchina["corrente_max_a"], macchina["cavo_minimo"]) == ("230 V 1~", 30, "3G6")
    assert interruttore == {
        "poli": "2P",
        "curva": "C",
        "in_a": 32,
        "idn_ma": 30,
        "tipo_differenziale": "A",
        "alta_velocita": True,
    }
    assert "Dati elettrici scritti dal manuale Shenling e dalla specifica Nove C (informazione)" in stampa
    assert "GT-01 (Shenling 12 kW): scritti alimentazione «230 V 1~», corrente_max_a 30, cavo_minimo «3G6»" in stampa
    assert "assunta monofase 230 V 1~" in stampa
    assert "QF-01 sulla linea di GT-01: scritti poli «2P», curva «C», in_a 32" in stampa
    assert "vale il maggiore" in stampa
    # Con i dati scritti, nessun avviso sulla linea.
    assert "manca la protezione" not in stampa and "sotto i" not in stampa


def test_la_tavola_dell_elettrico_esce_pulita_con_qf_in_tabella_e_in_legenda() -> None:
    esito = tavola()
    assert [item.message for item in esito.rilievi if item.severity is IssueSeverity.BLOCKING] == []
    assert not esito.cedute
    foglio = esito.disegno.sheets[0]  # type: ignore[union-attr]
    assert foglio.tabella is not None
    righe = {riga.codice: riga for riga in foglio.tabella.righe}
    assert set(righe) == {"GT-01", "QE-01", "QF-01"}
    assert righe["QF-01"].descrizione == "Interruttore magnetotermico differenziale"
    # D-237 (I-289): in ambito domestico il differenziale e' di tipo A.
    assert righe["QF-01"].caratteristiche == "2P C32 · Idn 30 mA tipo A"
    # I dati elettrici della macchina, dal manuale (I-277 riempita da REL-018).
    assert righe["GT-01"].caratteristiche == "230 V 1~ · 30 A · 3G6"
    assert (VOCE, "Interruttore magnetotermico differenziale") in {(v.symbol_id, v.name) for v in foglio.legend}
    assert "QF-01" in {label.text for label in foglio.labels}
    # La scritta del cavo resta sulla linea: una per la linea intera, attraverso QF-01.
    assert [(e.testo, sorted(e.connection_ids)) for e in foglio.diametri] == [("3G6 · L 15 m", ["t4", "t5"])]
    # Stretto all'uscita del quadro, non accanto alla macchina come il sezionatore.
    posati = {item.component_id: item for item in foglio.symbols}
    qf, quadro, pdc = posati["qf-pdc"], posati["quadro"], posati["pdc"]

    def centro(item: Any) -> tuple[float, float]:
        return (item.origin.x_mm + item.right_mm) / 2, (item.origin.y_mm + item.bottom_mm) / 2

    def distanza(a: Any, b: Any) -> float:
        (xa, ya), (xb, yb) = centro(a), centro(b)
        return abs(xa - xb) + abs(ya - yb)

    assert qf.symbol_id == VOCE
    assert distanza(qf, quadro) < distanza(qf, pdc)


def test_sulla_tavola_idraulica_l_interruttore_non_c_e() -> None:
    grafo = load_project(CASO / "grafo-completo.json")
    idraulica, _ = vista_del_grafo(grafo, "idraulica", catalogo(), NAMING)
    assert "qf-pdc" not in {item.id for item in idraulica.components}
    elettrico, _ = vista_del_grafo(grafo, "elettrico", catalogo(), NAMING)
    assert "qf-pdc" in {item.id for item in elettrico.components}


# --- 3. i dati del manuale -------------------------------------------------------------------


def test_i_dati_del_progettista_non_si_sovrascrivono(tmp_path: Path) -> None:
    grafo = _grafo(
        pdc={"alimentazione": "230 V 1~", "corrente_max_a": 28},
        qf={"in_a": 40, "curva": "D", "tipo_differenziale": "F"},
    )
    stampa, completo = _completa(grafo, tmp_path)
    macchina, interruttore = _proprieta(completo, "pdc"), _proprieta(completo, "qf-pdc")
    assert macchina["corrente_max_a"] == 28 and macchina["cavo_minimo"] == "3G6"
    assert (interruttore["in_a"], interruttore["curva"], interruttore["tipo_differenziale"]) == (40, "D", "F")
    assert (interruttore["poli"], interruttore["idn_ma"]) == ("2P", 30)
    # L'alimentazione e' data: niente monofase assunta.
    assert "assunta monofase" not in stampa
    assert "scritti cavo_minimo «3G6»" in stampa


def test_la_tabella_dei_dati_shenling() -> None:
    """La tabella sola (manuale §7.5 p. 55, specifica §3.3, «vale il maggiore»)."""
    attesi = {
        (6.0, 1): (16, 4, "3G4", "2P", 20),  # D-234: C20, non C16, sui 16 A del 6 kW
        (9.0, 1): (20.5, 4, "3G4", "2P", 25),
        (12.0, 1): (30, 6, "3G6", "2P", 32),
        (15.0, 1): (30, 6, "3G6", "2P", 32),
        (12.0, 3): (14, 2.5, "5G2,5", "4P", 16),
        (15.0, 3): (14, 2.5, "5G2,5", "4P", 16),
    }
    assert set(SHENLING_THERMAX_R290_LINEA) == set(attesi)
    for chiave, (corrente, sezione, cavo, poli, nominale) in attesi.items():
        linea = SHENLING_THERMAX_R290_LINEA[chiave]
        assert (linea.corrente_max_a, linea.sezione_mm2, linea.cavo_minimo, linea.poli, linea.in_a) == (
            corrente, sezione, cavo, poli, nominale,
        ), chiave
        assert (linea.curva, linea.idn_ma, linea.tipo_differenziale, linea.alta_velocita) == ("C", 30, "A", True)
        assert linea.in_a >= linea.corrente_max_a, chiave
    assert "vale il maggiore" in SHENLING_THERMAX_R290_LINEA[(12.0, 1)].fonte
    assert "proposta dal manuale" in SHENLING_THERMAX_R290_LINEA[(6.0, 1)].fonte


def test_il_trifase_solo_se_dichiarato(tmp_path: Path) -> None:
    stampa, completo = _completa(_grafo(pdc={"alimentazione": "400 V 3N~"}), tmp_path)
    macchina, interruttore = _proprieta(completo, "pdc"), _proprieta(completo, "qf-pdc")
    assert (macchina["alimentazione"], macchina["corrente_max_a"], macchina["cavo_minimo"]) == ("400 V 3N~", 14, "5G2,5")
    assert (interruttore["poli"], interruttore["curva"], interruttore["in_a"]) == ("4P", "C", 16)
    assert "assunta monofase" not in stampa


def test_una_taglia_che_il_manuale_non_ha_trifase_non_scrive_niente(tmp_path: Path) -> None:
    grafo = _grafo(pdc={"alimentazione": "400 V 3N~", "power_kw": 9})
    stampa, completo = _completa(grafo, tmp_path)
    assert "corrente_max_a" not in _proprieta(completo, "pdc")
    assert "in_a" not in _proprieta(completo, "qf-pdc")
    assert "non ha la 9 kW trifase" in stampa


def test_una_macchina_non_shenling_resta_senza_dati(tmp_path: Path) -> None:
    stampa, completo = _completa(_grafo(pdc={"marca": "Altra"}), tmp_path)
    assert "alimentazione" not in _proprieta(completo, "pdc")
    assert _proprieta(completo, "qf-pdc") == {}
    assert "Dati elettrici scritti" not in stampa


# --- 4. gli avvisi ---------------------------------------------------------------------------


def test_una_15_kw_protetta_c25_e_un_avviso(tmp_path: Path) -> None:
    """Il caso della commessa: la 15 kW protetta C25."""
    stampa, completo = _completa(_grafo(pdc={"power_kw": 15}, qf={"in_a": 25}), tmp_path)
    assert "Avvisi del manuale del costruttore e della specifica Nove C" in stampa
    assert "QF-01: In 25 A sulla linea di GT-01, sotto i 30 A del manuale (§7.5 p. 55)" in stampa
    # Il dato resta quello del progettista: e' un avviso, non una correzione.
    assert _proprieta(completo, "qf-pdc")["in_a"] == 25


def test_un_3g4_sulla_12_kw_e_un_avviso(tmp_path: Path) -> None:
    stampa, _ = _completa(_grafo(sezione="3G4"), tmp_path)
    assert "linea di GT-01: cavo 3G4, 4 mm², sotto i 6 mm² del manuale (§7.5 p. 55)" in stampa
    # Il 3G6 del caso minimo no.
    stampa, _ = _completa(_grafo(), tmp_path)
    assert "mm² del manuale" not in stampa


def test_la_linea_dal_quadro_senza_interruttore_e_un_avviso(tmp_path: Path) -> None:
    stampa, _ = _completa(_grafo(qf=None), tmp_path)
    assert "manca la protezione della linea (specifica §3.2, manuale p. 51)" in stampa


def test_gli_avvisi_si_leggono_anche_senza_completa() -> None:
    grafo = load_project(CASO / "grafo-completo.json")
    assert avvisi_della_linea(grafo, catalogo().per_il_progetto(grafo)) == []


# --- 5. la distinta, Capire e Comporre -------------------------------------------------------


def _distinta(grafo: dict[str, Any]) -> Any:
    return componi_la_distinta(
        grafo,
        carica_regole(ROOT / "rules" / "distinta"),
        nomi_del_catalogo(CATALOG),
        nomi_dei_fluidi(NAMING),
        sigle_dello_schema(grafo, CATALOG, NAMING),
    )


def test_la_distinta_ha_la_voce_dell_interruttore_e_non_la_protezione_della_linea() -> None:
    grafo = json.loads((CASO / "grafo-completo.json").read_text(encoding="utf-8"))
    distinta = _distinta(grafo)
    voce = next(v for v in distinta.voci if v.regola == f"corredo/{VOCE}/interruttore")
    assert voce.testo == "Interruttore magnetotermico differenziale 2P C32 Idn 30 mA tipo A"
    assert (voce.quantita, voce.sezione, voce.da_definire) == (1, "E", False)
    # La linea con l'interruttore non chiede anche la `protezione` del tratto.
    assert not any(v.regola.endswith("/protezione-della-linea") for v in distinta.voci)
    # Il cavo resta: 3G6, una tratta sola dal quadro alla macchina, attraverso QF-01.
    assert any(v.regola.endswith("/cavo-di-alimentazione") and "3G6" in v.testo for v in distinta.voci)


def test_la_distinta_senza_dati_dice_da_definire() -> None:
    grafo = json.loads((CASO / "grafo.json").read_text(encoding="utf-8"))
    voce = next(v for v in _distinta(grafo).voci if v.regola == f"corredo/{VOCE}/interruttore")
    assert voce.da_definire
    assert "DA DEFINIRE (poli)" in voce.testo and "DA DEFINIRE (in_a)" in voce.testo


def test_il_corredo_dice_che_l_interruttore_e_passante() -> None:
    corredo = json.loads(CORREDO.read_text(encoding="utf-8"))
    voce = corredo["voci"][VOCE]
    assert voce["passante"] is True
    assert [item["testo"] for item in voce["voci"]] == [
        "Interruttore magnetotermico differenziale {poli} {curva}{in_a} Idn {idn_ma} mA tipo {tipo_differenziale}"
    ]


def test_capire_mette_l_interruttore_sulla_linea_della_pompa_di_calore_e_non_il_sezionatore() -> None:
    testo = CAPIRE.read_text(encoding="utf-8")
    for parola in (
        VOCE,
        "REL-018",
        "Interruttore magnetotermico differenziale",
        "`quadro.out_n → QF.a`, `QF.b → pdc.power`",
        "**Il sezionatore locale, di regola, no** (specifica §3.2)",
        "**solo se il testo lo chiede**",
        "**lo hanno\nsolo se il progettista lo dichiara**",
        "`in_a`",
        "`idn_ma`",
        "`tipo_differenziale`",
    ):
        assert parola in testo, parola


def test_comporre_dice_dove_sta_l_interruttore_sulla_tavola_dell_elettrico() -> None:
    testo = COMPORRE.read_text(encoding="utf-8")
    assert VOCE in testo
    assert "QF-01" in testo
    assert "**all'uscita del quadro**" in testo
    assert "«3G6 · L 15 m» — resta sulla linea" in testo
