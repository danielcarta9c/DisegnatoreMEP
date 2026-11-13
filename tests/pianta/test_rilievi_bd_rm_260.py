"""I rilievi d'uso della 2.0.0 sulla pianta (REL-026, blocco B; I-300).

La sessione che ha usato la 2.0.0 sulla commessa BD.RM.260 ha lavorato su una copia
della skill e ha annotato che cosa ha dovuto cambiare (`docs/input-pm/2026-11-13-
rilievi-bd-rm-260/`). I file della commessa non entrano nel repository: ogni voce si
prova qui su un caso del repository o su un caso anonimo scritto apposta.

- B-1 il nome corto dei fluidi idronici nella tabella delle tratte;
- B-2 `sagome_muri`, il retino dei muri sulle sagome vere;
- B-3 le forature spente di base;
- B-4 le lunghezze dalla pianta al grafo, in un passaggio solo;
- B-5 il confronto con grafo e distinta non cambia il foglio.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta, riassunto
from disegnatore_mep.pianta.modello import ErroreDellaPianta, Fluido, carica_pianta
from disegnatore_mep.pianta.nel_grafo import (
    misure_dei_tronchi,
    provenienza,
    provenienza_della_tratta,
)
from disegnatore_mep.pianta.scritte import misura
from disegnatore_mep.pianta.tavola import (
    COLONNE_DELLE_TRATTE,
    CORPO_COLONNA_PT,
    LAYER_MURI,
    Area,
    nome_corto_del_fluido,
    pezzi_dei_muri,
)
from disegnatore_mep.skill import cartelle_del_repository
from disegnatore_mep.skill import main as skill

from .conftest import CASI, CATALOGO, CONFRONTI, NOMI, RADICE

SAGOME = CASI["sagome"]


def _variante(sorgente: Path, cartella: Path, cambia: Any, nome: str = "variante.json") -> Path:
    dati = json.loads(sorgente.read_text(encoding="utf-8"))
    cambia(dati)
    cartella.mkdir(parents=True, exist_ok=True)
    percorso = cartella / nome
    percorso.write_text(json.dumps(dati, ensure_ascii=False, indent=2), encoding="utf-8")
    return percorso


def _aree_dei_muri(esito_o_tavola: Any) -> list[Area]:
    tavola = getattr(esito_o_tavola, "tavola", esito_o_tavola)
    return [p for p in tavola.primitive if isinstance(p, Area) and p.layer == LAYER_MURI]

# --- B-1. il nome corto dei fluidi idronici ---------------------------------------------------


@pytest.mark.parametrize("fluido", Fluido.__args__)  # type: ignore[attr-defined]
def test_il_nome_del_fluido_sta_nella_sua_colonna(fluido: str) -> None:
    """BD.RM.260: «Acqua di riscaldamento» finiva sopra la colonna «Da»."""
    x = {titolo: x for titolo, x, _ in COLONNE_DELLE_TRATTE}
    larghezza = misura(nome_corto_del_fluido(fluido), CORPO_COLONNA_PT, False)[0]
    assert larghezza <= x["Da"] - x["Fluido"] - 1.0, (fluido, nome_corto_del_fluido(fluido), larghezza)


def test_i_nomi_corti_degli_idronici() -> None:
    assert nome_corto_del_fluido("heating_water") == "Acqua risc."
    assert nome_corto_del_fluido("domestic_hot_water") == "ACS"
    assert nome_corto_del_fluido("cold_water") == "AFS"
    assert nome_corto_del_fluido("supply_air") == "Aria di mandata"


# --- B-2. il retino dei muri sulle sagome vere ------------------------------------------------


def test_con_le_sagome_il_retino_sta_sulle_sagome(esiti: dict[str, Esito]) -> None:
    """Un'area per sagoma, con i suoi vertici: nessun rettangolo asse-spessore."""
    esito = esiti["sagome"]
    aree = _aree_dei_muri(esito)
    assert len(aree) == len(esito.pianta.sagome_muri) == 17
    ox, oy, xmin, ymin, k = esito.tavola.trasforma
    for area, sagoma in zip(aree, esito.pianta.sagome_muri, strict=True):
        in_metri = [v for x, y in area.punti for v in ((x - ox) / k + xmin, (y - oy) / k + ymin)]
        assert in_metri == pytest.approx([v for q in sagoma for v in q], abs=1e-3)
    # La tramezza a L e' un poligono solo, di sei vertici.
    assert max(len(a.punti) for a in aree) == 6


def test_senza_le_sagome_il_retino_e_quello_di_sempre(tmp_path: Path, esiti: dict[str, Esito]) -> None:
    """Senza `sagome_muri`, un rettangolo per tratto pieno di muro, come prima; e il
    percorso dei tracciati e' lo stesso: l'instradatore conosce i muri, non le sagome."""
    senza = _variante(SAGOME, tmp_path, lambda d: d.pop("sagome_muri"))
    esito = disegna_la_pianta(senza, tmp_path / "out", None, dxf=False, png=False)
    assert len(_aree_dei_muri(esito)) == len(pezzi_dei_muri(esito.pianta))
    con = esiti["sagome"]
    assert [p.punti for p in esito.percorsi] == [p.punti for p in con.percorsi]
    assert [lu.misurata_m for lu in esito.lunghezze] == [lu.misurata_m for lu in con.lunghezze]


def test_con_le_sagome_gli_ingombri_restano_i_muri(esiti: dict[str, Esito]) -> None:
    """Le scritte e i controlli misurano ancora i muri asse-spessore."""
    esito = esiti["sagome"]
    muri = {di for di, _ in esito.tavola.rettangoli if di.startswith("muro ")}
    assert muri == {f"muro {m.id}" for m in esito.pianta.muri}
    assert esito.rilievi.bloccanti == []


def test_nel_dettaglio_le_sagome_si_ritagliano(esiti: dict[str, Esito]) -> None:
    """Il riquadro A prende l'angolo della tramezza a L: le sagome che ci cadono si
    ritagliano sulla zona, e niente esce dalla cornice."""
    esito = esiti["sagome"]
    (dettaglio,) = esito.dettagli or []
    assert esito.pianta.dettagli
    x0, y0, x1, y1 = esito.pianta.dettagli[0].rettangolo
    ox, oy, xmin, ymin, k = dettaglio.trasforma
    aree = _aree_dei_muri(dettaglio)
    assert aree
    for area in aree:
        for x, y in area.punti:
            xm, ym = (x - ox) / k + xmin, (y - oy) / k + ymin
            assert x0 - 1e-3 <= xm <= x1 + 1e-3 and y0 - 1e-3 <= ym <= y1 + 1e-3
    # La L intera sta nel riquadro: si ritrova con i suoi sei vertici.
    assert any(len(a.punti) == 6 for a in aree)


def test_nel_dxf_le_sagome_sono_campiture_sul_layer_dei_muri(esiti: dict[str, Esito]) -> None:
    ezdxf = pytest.importorskip("ezdxf")
    esito = esiti["sagome"]
    dxf = next(p for p in esito.file if p.name == "sagome-muri.dxf")
    documento = ezdxf.readfile(dxf)
    campiture = [h for h in documento.modelspace().query("HATCH") if h.dxf.layer == LAYER_MURI]
    assert len(campiture) == len(esito.pianta.sagome_muri)
    vertici = sorted(len(h.paths[0].vertices) for h in campiture)
    assert vertici == sorted(len(s) for s in esito.pianta.sagome_muri)


def test_una_sagoma_vuole_tre_punti(tmp_path: Path) -> None:
    rotta = _variante(SAGOME, tmp_path, lambda d: d["sagome_muri"].append([[0.0, 0.0], [1.0, 0.0]]))
    with pytest.raises(ErroreDellaPianta, match="sagome_muri"):
        carica_pianta(rotta)


def test_muri_visibili_non_c_e(tmp_path: Path) -> None:
    """Il campo della copia della commessa (`sfondo.muri_visibili`) era un residuo
    della rev02 e non entra (LEGGIMI B4)."""
    rotta = _variante(CASI["corridoio"], tmp_path, lambda d: d["sfondo"].update(muri_visibili=False))
    with pytest.raises(ErroreDellaPianta, match="muri_visibili"):
        carica_pianta(rotta)


# --- B-3. le forature spente di base ----------------------------------------------------------

T3 = CASI["collaudo-t3"]


def _scritte_delle_forature(esito: Esito) -> list[str]:
    """Le sigle F1, F2… sulla tavola intera e nei riquadri di dettaglio."""
    return [
        s.testo for tavola in [esito.tavola, *(esito.dettagli or [])]
        for chi, s in tavola.scritte if chi.startswith("foratura ")
    ]


def _svg(esito: Esito) -> str:
    return next(p for p in esito.file if p.suffix == ".svg" and "dettaglio" not in p.name).read_text(encoding="utf-8")


def _dati(esito: Esito) -> dict[str, Any]:
    testo = next(p for p in esito.file if p.name.endswith(".tracciati.json")).read_text(encoding="utf-8")
    return json.loads(testo)  # type: ignore[no-any-return]


def test_di_base_le_forature_non_si_scrivono(esiti: dict[str, Esito]) -> None:
    """Niente F1/F2 sulla tavola, niente elenco nella colonna, niente voce in legenda,
    niente dato per il grafo: in una tavola MEP non servono (LEGGIMI B1)."""
    esito = esiti["collaudo-t3"]
    assert esito.pianta.forature is False
    assert esito.forature  # il percorso fora lo stesso: il costo vale sempre
    assert _scritte_delle_forature(esito) == []
    svg = _svg(esito)
    assert "FORATURE" not in svg and "Foratura (F1" not in svg and "Fori per i pezzi a parete" not in svg
    assert esito.rilievi.fori_fuori_dalle_aperture == []
    dati = _dati(esito)
    assert dati["forature_accese"] is False and dati["forature"] == [] and dati["fori_dei_pezzi"] == []
    assert "per_il_grafo" not in dati
    assert all("attraversamenti_di_parete" not in t for t in dati["tratte"])


def test_accese_le_forature_tornano_come_prima(tmp_path: Path, esiti: dict[str, Esito]) -> None:
    """`"forature": true`: le sigle, l'elenco e i dati per la distinta tornano; il
    percorso e le lunghezze sono gli stessi di quando sono spente."""
    accese = _variante(T3, tmp_path, lambda d: d.update(forature=True))
    esito = disegna_la_pianta(accese, tmp_path / "out", None, dxf=False, png=False)
    spente = esiti["collaudo-t3"]
    assert [p.punti for p in esito.percorsi] == [p.punti for p in spente.percorsi]
    assert [lu.da_quotare_m for lu in esito.lunghezze] == [lu.da_quotare_m for lu in spente.lunghezze]
    numeri = [f.numero for f in esito.forature]
    # Nel dettaglio si riscrivono anche le sigle di quello che ci sta dentro: si
    # confrontano gli insiemi.
    assert numeri and set(_scritte_delle_forature(esito)) == set(numeri)
    svg = _svg(esito)
    assert "FORATURE" in svg and "Foratura (F1, F2…: elenco sotto)" in svg
    assert len(esito.rilievi.fori_fuori_dalle_aperture) == len(numeri)
    dati = _dati(esito)
    assert dati["forature_accese"] is True and len(dati["forature"]) == len(numeri)
    assert set(dati["per_il_grafo"]["attraversamenti"]) == {t.tratta for t in esito.pianta.tracciati}


def test_il_riassunto_dice_che_le_forature_sono_spente(esiti: dict[str, Esito]) -> None:

    righe = riassunto(esiti["collaudo-t3"])
    assert any(r.startswith("Forature: spente") for r in righe)
    assert not any(r.startswith("Forature fuori dalle aperture") for r in righe)


# --- B-4. le lunghezze dalla pianta al grafo, in un passaggio solo ----------------------------

DISTINTA_T3, GRAFO_T3 = CONFRONTI["collaudo-t3"]

MISURATE = (
    "ramo-matrimoniale", "ramo-singola", "ramo-soggiorno-varco", "ramo-soggiorno-parete",
    "bus-matrimoniale", "bus-singola", "bus-soggiorno", "cavo-comando-filo", "alim-quadro-sezionatore",
)
"""Le tubazioni del grafo del T3 a cui il caso toglie la lunghezza: la pianta le misura.
Le altre restano del progettista (frigo, cavo UI-UE, condensa, centrale)."""


def _compatto(dati: object) -> str:
    """Lo stile del grafo del T3: una riga sola, chiavi in ordine, accenti scritti."""
    return json.dumps(dati, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _caso_b4(cartella: Path) -> tuple[Path, Path]:
    """Il T3 anonimo con le lunghezze da misurare: la pianta senza `lunghezza_m` sui
    tracciati, il grafo senza la lunghezza di nove tubazioni."""
    cartella.mkdir(parents=True, exist_ok=True)
    grafo = json.loads(GRAFO_T3.read_text(encoding="utf-8"))
    for tubazione in grafo["connections"]:
        if tubazione["id"] in MISURATE:
            tubazione.pop("lunghezza_m")
    percorso_del_grafo = cartella / "grafo-completo.json"
    percorso_del_grafo.write_text(_compatto(grafo), encoding="utf-8")
    pianta = _variante(T3, cartella, lambda d: [t.pop("lunghezza_m", None) for t in d["tracciati"]], "pianta.json")
    return pianta, percorso_del_grafo


def _pianta(pianta: Path, grafo: Path, uscita: Path, *altro: str) -> tuple[int, str]:
    """`mep.py pianta` con --grafo, come lo lancia la skill: l'uscita e la console."""

    testo = io.StringIO()
    with contextlib.redirect_stdout(testo):
        codice = skill(["pianta", str(pianta), "--out", str(uscita), "--senza-dxf", "--grafo", str(grafo), *altro],
                       cartelle_del_repository(RADICE))
    return codice, testo.getvalue()


def _tubazioni(grafo: Path) -> dict[str, dict[str, Any]]:
    return {t["id"]: t for t in json.loads(grafo.read_text(encoding="utf-8"))["connections"]}


@pytest.fixture(scope="module")
def primo_giro(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Il giro 1 della prova di accettazione: la pianta con --grafo, e il grafo prima e dopo."""
    cartella = tmp_path_factory.mktemp("b4")
    pianta, grafo = _caso_b4(cartella)
    prima = grafo.read_text(encoding="utf-8")
    codice, console = _pianta(pianta, grafo, cartella / "giro-1")
    dati = json.loads((cartella / "giro-1" / "pianta.tracciati.json").read_text(encoding="utf-8"))
    return {"cartella": cartella, "pianta": pianta, "grafo": grafo, "prima": prima, "dopo": grafo.read_text(encoding="utf-8"),
            "codice": codice, "console": console, "dati": dati}


def test_1_la_pianta_scrive_nel_grafo_le_lunghezze_misurate(primo_giro: dict[str, Any]) -> None:
    """Le nove tubazioni senza lunghezza ricevono la misura della pianta, col segno della
    provenienza; la tratta con un organo in linea (T10) riceve una misura per tronco."""
    assert primo_giro["codice"] == 0
    per_tratta = {t["tratta"]: t for t in primo_giro["dati"]["tratte"]}
    tubazioni = _tubazioni(primo_giro["grafo"])
    for tratta, tubazione in (("T01", "ramo-matrimoniale"), ("T12", "bus-matrimoniale"), ("T16", "cavo-comando-filo")):
        misura = per_tratta[tratta]["lunghezza_misurata_m"]
        assert tubazioni[tubazione]["lunghezza_m"] == misura
        assert tubazioni[tubazione]["properties"]["lunghezza_dalla_pianta_m"] == misura
    t10 = tubazioni["alim-quadro-sezionatore"]["lunghezza_m"] + tubazioni["alim-sezionatore-ue"]["lunghezza_m"]
    assert t10 == pytest.approx(per_tratta["T10"]["lunghezza_misurata_m"], abs=1e-9)
    assert tubazioni["alim-sezionatore-ue"]["properties"]["lunghezza_dalla_pianta_m"] > 0
    cambiate = {c["tratta"]: c for c in primo_giro["dati"]["grafo"]["lunghezze_cambiate"]}
    assert set(cambiate) == {"T01", "T02", "T03", "T04", "T10", "T12", "T13", "T14", "T16"}
    assert cambiate["T01"]["prima_m"] is None and cambiate["T01"]["dopo_m"] == per_tratta["T01"]["lunghezza_misurata_m"]
    assert cambiate["T10"]["tubazioni"] == ["alim-quadro-sezionatore", "alim-sezionatore-ue"]
    assert primo_giro["dati"]["grafo"]["scritto"] is True
    assert "scritte le lunghezze di 9 tratte" in primo_giro["console"]
    assert "  - T01: — → " in primo_giro["console"]


def test_1_solo_le_lunghezze_mai_la_connettivita(primo_giro: dict[str, Any]) -> None:
    """Tolti i due campi della lunghezza, il grafo e' quello di prima, campo per campo;
    il file resta nel suo stile (una riga, chiavi in ordine) e il modello lo legge."""

    prima, dopo = json.loads(primo_giro["prima"]), json.loads(primo_giro["dopo"])
    for tubazione in dopo["connections"]:
        if tubazione["id"] in MISURATE or tubazione["id"] == "alim-sezionatore-ue":
            tubazione.pop("lunghezza_m")
            tubazione["properties"].pop("lunghezza_dalla_pianta_m")
    assert dopo == prima
    assert "\n" not in primo_giro["dopo"] and primo_giro["dopo"] == _compatto(json.loads(primo_giro["dopo"]))
    ProjectModel.model_validate(json.loads(primo_giro["dopo"]))


def test_1_le_lunghezze_del_progettista_restano_e_si_segnalano(primo_giro: dict[str, Any]) -> None:
    """Le tubazioni con la lunghezza del progettista non si toccano — nemmeno la tubazione
    senza lunghezza di una tratta che il progettista ha dato (la condensa, 8 m sul primo
    tronco) — e la console e i dati dicono che la pianta misura altro."""
    prima, dopo = _tubazioni_da(primo_giro["prima"]), _tubazioni(primo_giro["grafo"])
    for ident in ("frigo-gas", "frigo-liquido", "cavo-ui-ue", "condensa-ui-sifone", "condensa-sifone-scarico"):
        assert dopo[ident] == prima[ident]
    lasciate = {voce["tratta"]: voce for voce in primo_giro["dati"]["grafo"]["lunghezze_del_progettista"]}
    assert lasciate["T07"]["data_m"] == 9 and lasciate["T07"]["dove"] == "grafo"
    assert lasciate["T08"]["data_m"] == 8
    assert "Lunghezze del progettista, lasciate come sono (la pianta misura altro): " in primo_giro["console"]


def _tubazioni_da(testo: str) -> dict[str, dict[str, Any]]:
    return {t["id"]: t for t in json.loads(testo)["connections"]}


def test_1_rilanciata_senza_cambi_non_scrive_niente(primo_giro: dict[str, Any]) -> None:
    grafo: Path = primo_giro["grafo"]
    codice, console = _pianta(primo_giro["pianta"], grafo, primo_giro["cartella"] / "giro-1b")
    assert codice == 0
    assert grafo.read_text(encoding="utf-8") == primo_giro["dopo"]
    assert "nessuna lunghezza cambiata, il file non si riscrive" in console
    dati = json.loads((primo_giro["cartella"] / "giro-1b" / "pianta.tracciati.json").read_text(encoding="utf-8"))
    assert dati["grafo"]["scritto"] is False and dati["grafo"]["lunghezze_cambiate"] == []
    assert "T01" in dati["grafo"]["lunghezze_allineate"]


def test_la_misura_scritta_non_diventa_la_lunghezza_del_progettista(primo_giro: dict[str, Any]) -> None:
    """Al giro dopo, la lunghezza che la pianta ha scritto e' ancora una misura: non si
    prende come L prog. (la scritta resta col «°»), e l'avviso non chiede di riportarla."""
    cartella: Path = primo_giro["cartella"]
    esito = disegna_la_pianta(primo_giro["pianta"], cartella / "giro-lettura", None, dxf=False, png=False,
                              grafo=primo_giro["grafo"], catalogo=CATALOGO, nomi=NOMI)
    per_tratta = {t["tratta"]: t for t in _dati(esito)["tratte"]}
    assert per_tratta["T01"]["lunghezza_data_m"] is None and per_tratta["T01"]["lunghezza_usata_da"] == "misura"
    assert per_tratta["T07"]["lunghezza_data_da"] == "grafo"
    (senza,) = [a for a in esito.avvisi or [] if a.startswith("Senza L prog.")]
    assert "Le misure sono nel grafo" in senza and "Da riportare" not in senza
    assert esito.confronto is not None and "T01" in esito.confronto.misure_della_pianta


def test_2_spostato_un_pezzo_l_elenco_dice_che_cosa_e_cambiato(tmp_path: Path) -> None:
    pianta, grafo = _caso_b4(tmp_path)
    _pianta(pianta, grafo, tmp_path / "giro-1")
    prima = _tubazioni(grafo)["ramo-matrimoniale"]["lunghezza_m"]
    dati = json.loads(pianta.read_text(encoding="utf-8"))
    next(p for p in dati["pezzi"] if p["sigla"] == "TA-01")["x"] -= 1.0
    pianta.write_text(json.dumps(dati, ensure_ascii=False), encoding="utf-8")
    codice, console = _pianta(pianta, grafo, tmp_path / "giro-2")
    assert codice == 0
    dopo = _tubazioni(grafo)["ramo-matrimoniale"]["lunghezza_m"]
    assert dopo == pytest.approx(prima + 1.0, abs=1e-9)
    uscita = json.loads((tmp_path / "giro-2" / "pianta.tracciati.json").read_text(encoding="utf-8"))
    assert uscita["grafo"]["lunghezze_cambiate"] == [
        {"tratta": "T01", "tubazioni": ["ramo-matrimoniale"], "prima_m": prima, "dopo_m": dopo}
    ]
    assert "scritte le lunghezze di 1 tratta" in console and "  - T01: " in console


def test_3_schema_e_distinta_rifatti_portano_i_numeri_nuovi(primo_giro: dict[str, Any], tmp_path: Path) -> None:
    """La distinta rifatta dal grafo aggiornato quota, tratta per tratta, lo stesso numero
    della pianta, e segna le lunghezze che vengono dalla pianta; lo schema scrive la misura."""

    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(primo_giro["dopo"], encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        skill(["distinta", str(grafo), "--out", str(tmp_path / "distinta")], cartelle_del_repository(RADICE))
        assert skill(["disegna", str(grafo), "--piano", str(RADICE / "docs/collaudi/REL-012/collaudo-t3/piano.json"),
                      "--out", str(tmp_path / "tavola")], cartelle_del_repository(RADICE)) == 0
    distinta = {t["num"]: t for t in json.loads((tmp_path / "distinta" / "distinta.json").read_text(encoding="utf-8"))["tratte"]}
    pianta = {t["tratta"]: t for t in primo_giro["dati"]["tratte"]}
    for tratta in ("T01", "T02", "T03", "T04", "T10", "T12", "T13", "T14", "T16"):
        assert distinta[tratta]["lunghezza_stimata_m"] == pytest.approx(pianta[tratta]["lunghezza_misurata_m"]), tratta
        assert distinta[tratta]["lunghezza_da_quotare_m"] == pianta[tratta]["lunghezza_da_quotare_m"], tratta
        assert distinta[tratta]["lunghezza_dalla_pianta"] is True
    assert "lunghezza_dalla_pianta" not in distinta["T07"]
    svg = next((tmp_path / "tavola").glob("*.svg")).read_text(encoding="utf-8")
    misura = str(pianta["T01"]["lunghezza_misurata_m"]).rstrip("0").rstrip(".").replace(".", ",")
    assert f"L {misura} m" in svg


def test_3_con_la_sola_distinta_la_misura_non_e_l_prog(primo_giro: dict[str, Any], tmp_path: Path) -> None:
    """La distinta fatta dal grafo aggiornato riporta le misure della pianta col loro segno:
    la pianta, letta solo la distinta, non le prende per lunghezze del progettista."""

    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(primo_giro["dopo"], encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        skill(["distinta", str(grafo), "--out", str(tmp_path / "distinta")], cartelle_del_repository(RADICE))
    esito = disegna_la_pianta(primo_giro["pianta"], tmp_path / "pianta", None, dxf=False, png=False,
                              distinta=tmp_path / "distinta" / "distinta.json")
    per_tratta = {t["tratta"]: t for t in _dati(esito)["tratte"]}
    assert per_tratta["T01"]["lunghezza_data_m"] is None
    assert per_tratta["T07"]["lunghezza_data_da"] == "distinta"


def test_4_una_lunghezza_corretta_a_mano_resta(primo_giro: dict[str, Any], tmp_path: Path) -> None:
    """Il progettista corregge a mano la lunghezza che la pianta aveva scritto (e lascia il
    segno): la correzione resta, e la pianta la segnala. Lo stesso per una lunghezza data
    nella pianta: non si scrive una misura nel grafo."""
    grafo = tmp_path / "grafo-completo.json"
    dati = json.loads(primo_giro["dopo"])
    next(t for t in dati["connections"] if t["id"] == "ramo-singola")["lunghezza_m"] = 5.0
    grafo.write_text(_compatto(dati), encoding="utf-8")
    pianta = _variante(primo_giro["pianta"], tmp_path,
                       lambda d: next(t for t in d["tracciati"] if t["tratta"] == "T13").update(lunghezza_m=6.0),
                       "pianta.json")
    prima = grafo.read_text(encoding="utf-8")
    _, console = _pianta(pianta, grafo, tmp_path / "giro")
    assert grafo.read_text(encoding="utf-8") == prima
    uscita = json.loads((tmp_path / "giro" / "pianta.tracciati.json").read_text(encoding="utf-8"))
    lasciate = {voce["tratta"]: voce for voce in uscita["grafo"]["lunghezze_del_progettista"]}
    assert lasciate["T02"]["data_m"] == 5.0 and lasciate["T02"]["dove"] == "grafo"
    assert lasciate["T13"]["data_m"] == 6.0 and lasciate["T13"]["dove"] == "pianta"
    assert "T02 5 m (misura " in console and "T13 6 m nella pianta (misura " in console


def test_in_sola_lettura_il_grafo_non_si_scrive(tmp_path: Path) -> None:
    pianta, grafo = _caso_b4(tmp_path)
    prima = grafo.read_text(encoding="utf-8")
    codice, console = _pianta(pianta, grafo, tmp_path / "giro", "--grafo-in-sola-lettura")
    assert codice == 0
    assert grafo.read_text(encoding="utf-8") == prima
    uscita = json.loads((tmp_path / "giro" / "pianta.tracciati.json").read_text(encoding="utf-8"))
    assert uscita["grafo"]["sola_lettura"] is True and uscita["grafo"]["scritto"] is False
    assert len(uscita["grafo"]["lunghezze_cambiate"]) == 9
    assert "in sola lettura: non scritto; cambierebbero le lunghezze di 9 tratte" in console
    (senza,) = [a for a in uscita["avvisi"] if a.startswith("Senza L prog.")]
    assert "Da riportare nel grafo" in senza


def test_un_grafo_senza_provenienza_non_si_sovrascrive(esiti: dict[str, Esito]) -> None:
    """Il grafo del T3, com'e': ogni lunghezza e' del progettista. La pianta non scrive
    niente (e la libreria, senza `aggiorna_il_grafo`, non scrive comunque)."""
    nel_grafo = esiti["collaudo-t3"].nel_grafo
    assert nel_grafo is not None
    assert nel_grafo.lunghezze == [] and nel_grafo.sola_lettura and not nel_grafo.scritto
    assert len(nel_grafo.del_progettista) == len(esiti["collaudo-t3"].pianta.tracciati)


def test_a_forature_accese_si_scrivono_anche_gli_attraversamenti(tmp_path: Path) -> None:
    pianta, grafo = _caso_b4(tmp_path)
    accese = _variante(pianta, tmp_path, lambda d: d.update(forature=True), "accese.json")
    _pianta(accese, grafo, tmp_path / "giro")
    uscita = json.loads((tmp_path / "giro" / "accese.tracciati.json").read_text(encoding="utf-8"))
    per_tratta = {t["tratta"]: t for t in uscita["tratte"]}
    tubazioni = _tubazioni(grafo)
    assert tubazioni["ramo-matrimoniale"]["properties"]["attraversamenti"] == per_tratta["T01"]["attraversamenti_di_parete"]
    assert tubazioni["frigo-gas"]["properties"]["attraversamenti_dalla_pianta"] == per_tratta["T07"]["attraversamenti_di_parete"]
    assert uscita["grafo"]["attraversamenti_cambiati"]


def test_a_forature_spente_gli_attraversamenti_non_si_scrivono(primo_giro: dict[str, Any]) -> None:
    assert all("attraversamenti" not in t["properties"] for t in _tubazioni(primo_giro["grafo"]).values())


def test_le_misure_dei_tronchi_sommano_la_misura() -> None:

    linee = (((0.0, 0.0), (1.2345, 0.0)), ((1.2345, 0.0), (1.2345, 2.0004)))
    parti = misure_dei_tronchi(linee, 3.235)
    assert parti == [1.234, 2.001] and sum(parti) == pytest.approx(3.235)


def test_la_provenienza_di_una_lunghezza() -> None:

    assert provenienza({"lunghezza_m": 5.0}) == "progettista"
    assert provenienza({"lunghezza_m": 2.8, "properties": {"lunghezza_dalla_pianta_m": 2.8}}) == "pianta"
    assert provenienza({"lunghezza_m": 3.0, "properties": {"lunghezza_dalla_pianta_m": 2.8}}) == "progettista"
    assert provenienza({"properties": {"lunghezza_m": 2.8, "lunghezza_dalla_pianta_m": 2.8}}) == "pianta"
    assert provenienza({"properties": {}}) is None
    assert provenienza_della_tratta([{"lunghezza_m": 2.0}, {"properties": {}}]) == "progettista"


# --- B-5. il confronto con grafo e distinta non cambia il foglio ------------------------------


def _discordante(dati: dict[str, Any]) -> None:
    """Il T3 con molte discordanze, come la commessa: numeri di tratta che la distinta
    non ha (e tratte della distinta che la pianta non ha), lunghezze diverse da quelle
    del grafo, sigle diverse da quelle dello schema."""
    nuove = {p["sigla"]: p["sigla"].replace("TA-", "BOC-") for p in dati["pezzi"] if p["sigla"].startswith("TA-")}
    for pezzo in dati["pezzi"]:
        pezzo["sigla"] = nuove.get(pezzo["sigla"], pezzo["sigla"])
    for tracciato in dati["tracciati"]:
        tracciato["tratta"] = f"T{int(tracciato['tratta'][1:]) + 40:02d}"
        if tracciato.get("lunghezza_m") is not None:
            tracciato["lunghezza_m"] += 1
        for capo in ("da", "a"):
            valore = tracciato[capo]
            if isinstance(valore, dict):
                valore["pezzo"] = nuove.get(valore["pezzo"], valore["pezzo"])
            else:
                tracciato[capo] = nuove.get(valore, valore)


@pytest.fixture(scope="module")
def discordanti(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Esito]:
    cartella = tmp_path_factory.mktemp("discordanze")
    sorgente = _variante(T3, cartella, _discordante, "discordanze.json")
    out: dict[str, Esito] = {}
    for nome, distinta, grafo in (
        ("senza", None, None), ("grafo", None, GRAFO_T3), ("distinta", DISTINTA_T3, None),
        ("entrambi", DISTINTA_T3, GRAFO_T3),
    ):
        out[nome] = disegna_la_pianta(
            sorgente, cartella / nome, None, dxf=False, png=False, distinta=distinta, grafo=grafo,
            catalogo=CATALOGO, nomi=NOMI,
        )
    return out


def test_con_o_senza_il_confronto_il_foglio_e_lo_stesso(discordanti: dict[str, Esito]) -> None:
    """BD.RM.260: 72 avvisi con `--grafo` portavano il foglio da A2 ad A1, e
    `--distinta` lo portava in A1. Sulla 2.0.0 questo caso usciva in A3 senza
    confronto, in A2 con uno dei due file e in A1 con tutti e due (49 avvisi)."""
    entrambi = discordanti["entrambi"]
    assert entrambi.confronto is not None and len(entrambi.confronto.avvisi) >= 40
    formati = {nome: (e.tavola.formato, e.tavola.scala) for nome, e in discordanti.items()}
    assert len(set(formati.values())) == 1, formati


def test_sulla_tavola_le_discordanze_sono_riassunte(discordanti: dict[str, Esito]) -> None:
    """Quante, di che tipo, dove leggere il resto: una riga, non quarantanove."""
    senza, entrambi = discordanti["senza"], discordanti["entrambi"]
    assert entrambi.confronto is not None
    assert len(entrambi.avvisi or []) == len(senza.avvisi or []) + 1
    (riassunto_del_confronto,) = [a for a in entrambi.avvisi or [] if a.startswith("Confronto con")]
    n = len(entrambi.confronto.avvisi)
    assert f"{n} discordanze" in riassunto_del_confronto
    assert "15 tratte della pianta che la distinta non ha" in riassunto_del_confronto
    assert "lunghezze diverse dal grafo" in riassunto_del_confronto
    assert "discordanze.tracciati.json" in riassunto_del_confronto
    assert sum(len(v) for v in entrambi.confronto.per_tipo.values()) == n


def test_per_esteso_nei_dati_e_in_console(discordanti: dict[str, Esito]) -> None:

    entrambi = discordanti["entrambi"]
    assert entrambi.confronto is not None
    dati = _dati(entrambi)
    assert dati["confronto"]["avvisi"] == entrambi.confronto.avvisi
    assert sum(dati["confronto"]["avvisi_per_tipo"].values()) == len(entrambi.confronto.avvisi)
    righe = riassunto(entrambi)
    for voce in entrambi.confronto.avvisi:
        assert f"  - {voce}" in righe


def test_i_bloccanti_si_riassumono_coi_numeri_di_tratta(tmp_path: Path) -> None:
    def scambia(dati: dict[str, Any]) -> None:
        t03 = next(t for t in dati["tracciati"] if t["tratta"] == "T03")
        t04 = next(t for t in dati["tracciati"] if t["tratta"] == "T04")
        t03["a"], t04["a"] = t04["a"], t03["a"]

    esito = disegna_la_pianta(_variante(T3, tmp_path, scambia), tmp_path / "out", None, dxf=False, png=False,
                              distinta=DISTINTA_T3)
    (riga,) = [a for a in esito.avvisi or [] if a.startswith("Ferma la consegna")]
    assert "T03, T04 nella distinta collegano pezzi diversi" in riga
    assert len(esito.rilievi.confronto_bloccante) == 2
