"""La riduzione all'attacco della macchina, un pezzo vero sulla tavola e in distinta (I-281, D-233).

Il PO: «manca un simobolo della riduzione in tavola. se facciamo riduzione fuori dalla PDC
serve il simbolo no ?». La villetta di riferimento (`docs/collaudi/REL-017/diametri/`) ha la
Shenling ThermaX da 12 kW con 5 K e i diametri chiesti sul primario: 12 / (4,18 · 5) =
2,067 m³/h, che la velocita' manda nel multistrato 32×3 (1", 1,08 m/s), sotto l'attacco
da 1¼" della macchina. `completa` posa allora una riduzione da 1¼" a 1" sulla mandata e una
sul ritorno, subito dopo il giunto antivibrante. Sulla 15 kW il tubo e' l'MS 40×3,5, da
1¼" come l'attacco, e la riduzione non c'e'.
"""

import contextlib
import io
import json
import re
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
VILLETTA = ROOT / "docs" / "collaudi" / "REL-017" / "diametri" / "grafo.json"
PIANO = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola" / "piano-idraulica.json"

MANDATA = "pipe-reducer-pdc-water-supply"
RITORNO = "pipe-reducer-pdc-water-return"
GIUNTO_MANDATA = "flexible-joint-pdc-water-supply"
GIUNTO_RITORNO = "flexible-joint-pdc-water-return"


def _villetta(potenza: float = 12, sezione: str | None = None, diametri: bool = True) -> dict[str, Any]:
    testo: dict[str, Any] = json.loads(VILLETTA.read_text(encoding="utf-8"))
    for pezzo in testo["components"]:
        if pezzo["id"] == "pdc":
            pezzo["properties"].update({"delta_t_k": 5, "power_kw": potenza})
    if sezione is not None:
        for tubo in testo["connections"]:
            if tubo["network_id"] == "primario":
                tubo["sezione"] = sezione
    if not diametri:
        testo.pop("diametri", None)
    return testo


def _completa(cartella: Path, testo: dict[str, Any]) -> tuple[dict[str, Any], str, Path]:
    grafo, completo = cartella / "grafo.json", cartella / "grafo-completo.json"
    grafo.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
    uscita = _esegui(["completa", str(grafo), "--out", str(completo)])
    return json.loads(completo.read_text(encoding="utf-8")), uscita, completo


def _esegui(argomenti: list[str], esito: int = 0) -> str:
    testo = io.StringIO()
    with contextlib.redirect_stdout(testo):
        assert main(argomenti, cartelle_del_repository(ROOT)) == esito
    return testo.getvalue()


def _tubo_fra(grafo: dict[str, Any], primo: tuple[str, str], secondo: tuple[str, str]) -> dict[str, Any]:
    """La tubazione da `primo` a `secondo`, nel verso in cui e' scritta."""
    capi = [
        tubo
        for tubo in grafo["connections"]
        if (tubo["endpoint_a"]["component_id"], tubo["endpoint_a"]["port_id"]) == primo
        and (tubo["endpoint_b"]["component_id"], tubo["endpoint_b"]["port_id"]) == secondo
    ]
    assert len(capi) == 1, (primo, secondo)
    return capi[0]


@pytest.fixture(scope="module")
def dodici(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, Any], str, Path]:
    return _completa(tmp_path_factory.mktemp("dodici"), _villetta())


def test_sulla_dodici_due_riduzioni_subito_dopo_i_giunti(dodici: tuple[dict[str, Any], str, Path]) -> None:
    grafo, _, _ = dodici
    pezzi = {p["id"]: p for p in grafo["components"]}
    riduzioni = sorted(p for p, v in pezzi.items() if v["definition_id"] == "pipe-reducer")
    assert riduzioni == [RITORNO, MANDATA]
    for riduzione in riduzioni:
        assert pezzi[riduzione]["properties"] == {"attacco": '1¼"', "tubo": '1"'}
    # Mandata: la macchina, il giunto, la riduzione dal lato largo, poi la sicurezza.
    _tubo_fra(grafo, ("pdc", "water_supply"), (GIUNTO_MANDATA, "a"))
    _tubo_fra(grafo, (GIUNTO_MANDATA, "b"), (MANDATA, "a"))
    _tubo_fra(grafo, (MANDATA, "b"), ("tee-valve-safety-pdc-water-supply", "a"))
    # Ritorno: l'acqua arriva dal tubo sul lato stretto, ed esce dal largo nel giunto.
    _tubo_fra(grafo, (RITORNO, "a"), (GIUNTO_RITORNO, "a"))
    _tubo_fra(grafo, (GIUNTO_RITORNO, "b"), ("pdc", "water_return"))
    oltre = [t for t in grafo["connections"] if t["endpoint_b"] == {"component_id": RITORNO, "port_id": "b"}]
    assert len(oltre) == 1 and oltre[0]["endpoint_a"]["component_id"] == "valve-antifreeze-pdc-water-return"


def test_completa_dice_la_riduzione_aggiunta(dodici: tuple[dict[str, Any], str, Path]) -> None:
    _, uscita, _ = dodici
    assert "Riduzioni agli attacchi delle macchine (informazione)" in uscita
    assert 'riduzione 1¼"×1" aggiunta su mandata e ritorno di GT-01' in uscita


def test_rilanciare_completa_non_aggiunge_una_seconda_coppia(
    dodici: tuple[dict[str, Any], str, Path], tmp_path: Path
) -> None:
    _, _, completo = dodici
    di_nuovo = tmp_path / "di-nuovo.json"
    uscita = _esegui(["completa", str(completo), "--out", str(di_nuovo)])
    assert di_nuovo.read_text(encoding="utf-8") == completo.read_text(encoding="utf-8")
    assert 'riduzione 1¼"×1" gia\' posata su mandata e ritorno di GT-01' in uscita


def test_sulla_quindici_il_tubo_e_gia_da_un_pollice_e_un_quarto(tmp_path: Path) -> None:
    """MS 40×3,5 (1¼") sull'attacco da 1¼": nessuna riduzione."""
    grafo, uscita, _ = _completa(tmp_path, _villetta(15))
    assert not [p for p in grafo["components"] if p["definition_id"] == "pipe-reducer"]
    assert "Riduzioni agli attacchi" not in uscita


def test_senza_i_diametri_niente_riduzione(tmp_path: Path) -> None:
    grafo, _, _ = _completa(tmp_path, _villetta(diametri=False))
    assert not [p for p in grafo["components"] if p["definition_id"] == "pipe-reducer"]


def test_decide_il_tubo_del_progettista(tmp_path: Path) -> None:
    """La 15 kW con l'MS 32×3 scritto dal progettista (una commessa realizzata cosi'):
    il tubo e' da 1", e la riduzione c'e'."""
    grafo, _, _ = _completa(tmp_path, _villetta(15, "MS 32×3"))
    riduzioni = {p["id"]: p["properties"] for p in grafo["components"] if p["definition_id"] == "pipe-reducer"}
    assert riduzioni == {MANDATA: {"attacco": '1¼"', "tubo": '1"'}, RITORNO: {"attacco": '1¼"', "tubo": '1"'}}


def test_sulla_tavola_la_riduzione_e_in_legenda_e_non_in_tabella(
    dodici: tuple[dict[str, Any], str, Path], tmp_path: Path
) -> None:
    """Un raccordo: il suo segno in legenda, «Riduzione»; ne' sigla sul disegno ne' riga
    nella tabella delle apparecchiature, come il giunto e i T."""
    _, _, completo = dodici
    tavola = tmp_path / "tavola"
    _esegui(["disegna", str(completo), "--piano", str(PIANO), "--out", str(tavola), "--senza-dxf"])
    (svg,) = tavola.glob("*.svg")
    testo = svg.read_text(encoding="utf-8")
    assert testo.count(">Riduzione<") == 1
    assert "RID-" not in testo
    # Sul disegno sta fra il giunto e il pezzo dopo, senza toccarli: i simboli sono larghi
    # 5 mm, e sulle due linee orizzontali della villetta conta la x.
    x = {
        pezzo: float(valore)
        for pezzo, valore in re.findall(r'data-component-id="([^"]+)"[^>]*transform="translate\(([-\d.]+) ', testo)
    }
    for giunto, riduzione, dopo in (
        (GIUNTO_MANDATA, MANDATA, "tee-valve-safety-pdc-water-supply"),
        (GIUNTO_RITORNO, RITORNO, "valve-antifreeze-pdc-water-return"),
    ):
        assert x[giunto] + 5.0 < x[riduzione] and x[riduzione] + 5.0 < x[dopo], (x[giunto], x[riduzione], x[dopo])


def test_in_distinta_una_riga_per_le_due_riduzioni(dodici: tuple[dict[str, Any], str, Path], tmp_path: Path) -> None:
    """«Riduzione 1¼" M × 1" F», contata per pezzo; e il giunto, fra la macchina e la
    riduzione, e' grande quanto l'attacco."""
    _, _, completo = dodici
    cartella = tmp_path / "distinta"
    # Senza la skill dei report il documento esce in Markdown, e il comando lo dice con 2.
    _esegui(["distinta", str(completo), "--out", str(cartella)], esito=2)
    (documento,) = cartella.glob("Distinta_*.md")
    righe = documento.read_text(encoding="utf-8").splitlines()
    riduzione = [r for r in righe if 'Riduzione 1¼" M × 1" F' in r]
    assert len(riduzione) == 1
    celle = [c.strip() for c in riduzione[0].strip("|").split("|")]
    assert celle[2:5] == ["n", "2", "installatore"]
    assert any('Giunto antivibrante 1¼":' in r for r in righe)
    assert not any('Giunto antivibrante 1":' in r for r in righe)
