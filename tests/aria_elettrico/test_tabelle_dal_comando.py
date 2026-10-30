"""Le tabelle del foglio dal comando, non solo da codice (REL-012, fase 2, punto 3).

`mep.py disegna --tabelle <file>` legge il file che la distinta scrive
(`tabelle-del-foglio.json`) e posa le tabelle nelle zone che il piano lascia:

- le colonne pesano, non misurano: il comando le allarga quanto la zona, e ciascuna
  almeno quanto la sua parola piu' lunga;
- una tabella con la sua `zona` va li'; le altre a destra se ci stanno, se no in basso,
  e una zona si divide in colonne quando una tabella e' piu' lunga di lei;
- se non entrano, il comando si ferma prima di scrivere e dice che cosa allargare;
- una tabella senza intestazioni — le note — non ha la riga vuota dell'intestazione.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.graphics.frame import NOVE_C_A2
from disegnatore_mep.graphics.tabelle import posa_le_tabelle, tratti_della_tabella_posata
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    ColonnaDellaTabella,
    RigaDellaTabellaLibera,
    SheetGeometry,
    TabellaNelleZone,
)
from disegnatore_mep.piano.formato import PianoDiComposizione
from disegnatore_mep.skill import (
    FORMATO_DELLE_TABELLE,
    Cartelle,
    cartelle_del_repository,
    main,
    tabelle_per_le_zone,
)

ROOT = Path(__file__).resolve().parents[2]
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
GRAFO_6 = IMPIANTO_6 / "grafo-completo-6.json"
PIANO_6 = IMPIANTO_6 / "piano-6-a.json"


@pytest.fixture(scope="module")
def cartelle() -> Cartelle:
    return cartelle_del_repository(ROOT)


def _file(tmp_path: Path, tabelle: list[dict[str, Any]], nome: str = "tabelle.json") -> Path:
    percorso = tmp_path / nome
    percorso.write_text(
        json.dumps({"formato": FORMATO_DELLE_TABELLE, "versione": 1, "tabelle": tabelle}, ensure_ascii=False),
        encoding="utf-8",
    )
    return percorso


def _tabella(ident: str, righe: int, **altro: Any) -> dict[str, Any]:
    return {
        "id": ident,
        "titolo": f"TABELLA {ident.upper()}",
        "colonne": [
            {"id": "n", "titolo": "N.", "allinea": "sinistra", "peso": 0.5},
            {"id": "voce", "titolo": "Voce", "allinea": "sinistra", "peso": 4},
            {"id": "q", "titolo": "Q.tà", "allinea": "destra", "peso": 0.6},
        ],
        "sezioni": [
            {"titolo": "A. Prima sezione", "righe": [[f"A.{n}", f"voce numero {n}", str(n)] for n in range(1, righe + 1)]}
        ],
        **altro,
    }


def _piano(destra: float, basso: float, formato: str = "A2") -> PianoDiComposizione:
    return PianoDiComposizione.model_validate(
        {"formato": formato, "pezzi": {}, "zone_tabelle": {"destra_mm": destra, "basso_mm": basso}}
    )


def test_le_colonne_si_allargano_quanto_la_zona_secondo_i_pesi(tmp_path: Path) -> None:
    tabelle, dove = tabelle_per_le_zone(_piano(175, 0), [_file(tmp_path, [_tabella("prima", 4)])])
    (tabella,) = tabelle
    assert tabella.zona == "destra"
    larghezze = [c.larghezza_mm for c in tabella.colonne]
    assert sum(larghezze) == pytest.approx(175 - 2 * 2.5, abs=0.05), "larga quanto la zona, meno i margini"
    assert larghezze[1] > larghezze[2] >= larghezze[0], "la voce pesa di piu'"
    assert tabella.righe[0].sezione == "A. Prima sezione" and tabella.righe[1].celle == ["A.1", "voce numero 1", "1"]
    assert dove == ["«prima» a destra, larga 170 mm"]


def test_una_colonna_stretta_e_larga_almeno_quanto_la_sua_parola(tmp_path: Path) -> None:
    """Il peso 0,05 darebbe alla colonna «Tratto» meno di un millimetro: il motore non
    spezza le parole, e la colonna prende quello che le serve."""
    tabella = _tabella("stretta", 2)
    tabella["colonne"][0]["peso"] = 0.05
    tabella["colonne"][0]["titolo"] = "Tratto"
    (posata,), _ = tabelle_per_le_zone(_piano(175, 0), [_file(tmp_path, [tabella])])
    assert posata.colonne[0].larghezza_mm > 12
    posa_le_tabelle(SheetGeometry(sheet_id="t", title="t"), NOVE_C_A2.con_le_zone(175, 0), [posata])


def test_senza_zona_a_destra_se_ci_sta_se_no_in_basso(tmp_path: Path) -> None:
    lunga = _tabella("lunga", 60)
    tabelle, dove = tabelle_per_le_zone(
        _piano(175, 135), [_file(tmp_path, [_tabella("corta", 5), lunga, _tabella("dopo", 3)])]
    )
    assert [t.zona for t in tabelle] == ["destra", "destra", "basso"]
    assert [t.titolo for t in tabelle] == ["TABELLA CORTA", "TABELLA DOPO", "TABELLA LUNGA"]
    assert any(riga.startswith("«lunga» in basso") and "colonne" in riga for riga in dove), dove


def test_la_zona_scritta_nel_file_si_rispetta(tmp_path: Path) -> None:
    tabelle, _ = tabelle_per_le_zone(_piano(175, 135), [_file(tmp_path, [_tabella("giu", 3, zona="basso")])])
    assert [t.zona for t in tabelle] == ["basso"]


def test_piu_file_si_sommano_nell_ordine(tmp_path: Path) -> None:
    primo = _file(tmp_path, [_tabella("uno", 2)], "a.json")
    secondo = _file(tmp_path, [_tabella("due", 2)], "b.json")
    tabelle, _ = tabelle_per_le_zone(_piano(175, 0), [primo, secondo])
    assert [t.titolo for t in tabelle] == ["TABELLA UNO", "TABELLA DUE"]


def test_senza_zone_nel_piano_lo_dice(tmp_path: Path) -> None:
    piano = PianoDiComposizione.model_validate({"formato": "A2", "pezzi": {}})
    with pytest.raises(LayoutError, match="zone_tabelle"):
        tabelle_per_le_zone(piano, [_file(tmp_path, [_tabella("x", 2)])])


def test_una_tabella_che_non_entra_dice_che_cosa_allargare(tmp_path: Path) -> None:
    with pytest.raises(LayoutError, match=r"non entra nelle zone del piano .*a destra: .*in basso: .*zone_tabelle"):
        tabelle_per_le_zone(_piano(60, 20), [_file(tmp_path, [_tabella("enorme", 200)])])


@pytest.mark.parametrize(
    ("contenuto", "messaggio"),
    [
        ({"formato": "altro", "versione": 1, "tabelle": []}, "manca \"formato\""),
        ({"formato": FORMATO_DELLE_TABELLE, "versione": 9, "tabelle": []}, "versione 9"),
        ({"formato": FORMATO_DELLE_TABELLE, "versione": 1, "tabelle": [{"id": "x", "colonne": []}]}, "colonne"),
        (
            {"formato": FORMATO_DELLE_TABELLE, "versione": 1,
             "tabelle": [_tabella("x", 1) | {"sezioni": [{"titolo": None, "righe": [["solo una cella"]]}]}]},
            "non ha 3 celle",
        ),
        ({"formato": FORMATO_DELLE_TABELLE, "versione": 1, "tabelle": [_tabella("x", 1, zona="sopra")]}, "zona"),
    ],
)
def test_un_file_che_non_e_nel_formato_dice_dove(tmp_path: Path, contenuto: dict[str, Any], messaggio: str) -> None:
    percorso = tmp_path / "t.json"
    percorso.write_text(json.dumps(contenuto), encoding="utf-8")
    with pytest.raises(ValueError, match=messaggio):
        tabelle_per_le_zone(_piano(175, 135), [percorso])


def test_una_tabella_senza_intestazioni_non_ha_la_riga_vuota() -> None:
    """Le note della distinta sono una tabella con le intestazioni vuote: sulla M.02 la
    riga dell'intestazione restava, vuota, fra il titolo e la prima nota."""
    frame = NOVE_C_A2.con_le_zone(175, 0)

    def note(intestazioni: tuple[str, str]) -> TabellaNelleZone:
        return TabellaNelleZone(
            titolo="NOTE",
            colonne=[
                ColonnaDellaTabella(intestazione=intestazioni[0], larghezza_mm=8, a_destra=True),
                ColonnaDellaTabella(intestazione=intestazioni[1], larghezza_mm=150),
            ],
            righe=[RigaDellaTabellaLibera(celle=["1.", "prima nota"]), RigaDellaTabellaLibera(celle=["2.", "seconda"])],
            zona="destra",
        )

    vuote, piene = (
        posa_le_tabelle(SheetGeometry(sheet_id="t", title="t"), frame, [note(i)]).tabelle[0]
        for i in (("", ""), ("N.", "Nota"))
    )
    orizzontali = [
        sorted({y1 for x1, y1, x2, y2 in tratti_della_tabella_posata(t, frame.standard).linee if y1 == y2})
        for t in (vuote, piene)
    ]
    assert len(orizzontali[0]) == 3, "il bordo alto e due righe: nessuna riga d'intestazione"
    assert len(orizzontali[1]) == 4
    assert orizzontali[0][0] == orizzontali[1][0]


def test_disegna_posa_le_tabelle_del_file_e_lo_dice(
    cartelle: Cartelle, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    piano = json.loads(PIANO_6.read_text(encoding="utf-8"))
    piano["formato"] = "A1"
    piano["zone_tabelle"] = {"destra_mm": 180, "basso_mm": 60}
    (tmp_path / "piano.json").write_text(json.dumps(piano), encoding="utf-8")
    tabelle = _file(tmp_path, [_tabella("prima", 6)])
    codice = main(
        ["disegna", str(GRAFO_6), "--piano", str(tmp_path / "piano.json"), "--out", str(tmp_path / "tavola"),
         "--tabelle", str(tabelle), "--senza-dxf"],
        cartelle,
    )
    uscita = capsys.readouterr().out
    assert "Tabelle del foglio:\n  - «prima» a destra, larga 175 mm" in uscita
    svg = next((tmp_path / "tavola").glob("*.svg")).read_text(encoding="utf-8")
    assert 'class="tabella-nelle-zone"' in svg and "TABELLA PRIMA" in svg and "voce numero 6" in svg
    assert codice in (0, 2)


def test_disegna_con_una_tabella_che_non_entra_si_ferma_prima_di_scrivere(
    cartelle: Cartelle, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    piano = json.loads(PIANO_6.read_text(encoding="utf-8"))
    (tmp_path / "piano.json").write_text(json.dumps(piano), encoding="utf-8")
    codice = main(
        ["disegna", str(GRAFO_6), "--piano", str(tmp_path / "piano.json"), "--out", str(tmp_path / "tavola"),
         "--tabelle", str(_file(tmp_path, [_tabella("x", 3)]))],
        cartelle,
    )
    assert codice == 1
    assert "zone_tabelle" in capsys.readouterr().err
    assert not (tmp_path / "tavola").exists(), "nessuna tavola scritta senza le sue tabelle"
