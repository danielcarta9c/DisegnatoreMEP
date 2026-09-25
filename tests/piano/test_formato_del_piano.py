"""Un piano malformato dice **che cosa manca**, non una traccia di stack.

E' il criterio 10 di DRAW-015, ed e' un criterio di accettazione. Chi compone
lavora a mano sul file del piano: un `KeyError: 'x'` in mezzo a una traccia non
gli dice ne' quale pezzo ne' che cosa ci voleva, e cinquanta pezzi dopo non e'
un messaggio, e' una caccia.

Qui c'e' un caso per ogni forma di malformazione, e ciascuno controlla che nel
messaggio ci siano **il pezzo, il campo e cio' che ci si aspettava**. In testa,
il verso positivo che conta piu' di tutti: i due piani della prova — i documenti
che hanno deciso D-151 — si leggono **senza modifiche**.
"""
# categoria: difende il motore

import json
from pathlib import Path

import pytest

from disegnatore_mep.piano.formato import (
    ErroreDelPiano,
    PezzoNelPiano,
    PianoDiComposizione,
    carica_piano,
)

ROOT = Path(__file__).resolve().parents[2]
PIANI = ROOT / "docs" / "collaudi" / "PROVA-PIANO"


def _scrivi(cartella: Path, testo: str) -> Path:
    percorso = cartella / "piano.json"
    percorso.write_text(testo, encoding="utf-8")
    return percorso


def test_i_due_piani_della_prova_si_leggono_senza_modifiche() -> None:
    """I documenti agli atti entrano nel formato nuovo come sono.

    Sono le due tavole del 19/20 settembre: se il formato dichiarato non le
    leggesse, la prova che ha deciso D-151 non sarebbe piu' riproducibile.
    """
    uno = carica_piano(PIANI / "impianto-1.json")
    cinque = carica_piano(PIANI / "impianto-5.json")

    assert uno.formato == "A2"
    assert cinque.formato == "A1"
    assert len(uno.pezzi) == 19
    assert len(cinque.pezzi) == 46
    # Le note sono parte del piano: dicono quale regola ha messo il pezzo li'.
    assert uno.note and cinque.note
    assert any("D-041 + D-118" in riga for riga in uno.note)
    # Il buco noto: il gruppo di riempimento ha due attacchi e non e' una
    # macchina, quindi la sua rotazione sta scritta a mano nel piano (§4).
    assert uno.pezzi["filling-unit-collettore-ritorno-a"].rotazione == 180
    assert uno.pezzi["pdc-master"].rotazione is None


def test_il_campo_delle_note_si_legge_da_tutti_e_due_i_nomi(tmp_path: Path) -> None:
    """`nota` e' il nome storico, `note` quello dichiarato: valgono uguale.

    I due piani della prova scrivono `nota`, al singolare, e si leggono senza
    modifiche; un piano nuovo scrive `note` e si legge allo stesso modo.
    """
    storico = json.loads((PIANI / "impianto-1.json").read_text(encoding="utf-8"))
    assert "nota" in storico and "note" not in storico
    assert carica_piano(PIANI / "impianto-1.json").note == storico["nota"]

    nuovo = _scrivi(
        tmp_path,
        '{"note": ["B3 — collettore verticale"], "pezzi": {"volano": {"x": 1, "y": 2}}}',
    )
    assert carica_piano(nuovo).note == ["B3 — collettore verticale"]


def test_un_piano_minimo_prende_l_a3_e_nessuna_nota(tmp_path: Path) -> None:
    """Il formato ha un valore di partenza; le note e la regola no: sono scelte."""
    piano = carica_piano(_scrivi(tmp_path, '{"pezzi": {"volano": {"x": 1, "y": 2}}}'))
    assert piano.formato == "A3"
    assert piano.note == []
    assert piano.pezzi["volano"].regola is None


def test_la_regola_si_scrive_sul_pezzo(tmp_path: Path) -> None:
    """`regola` e' la forma per-pezzo delle note: chi ha messo il pezzo li'."""
    piano = carica_piano(
        _scrivi(
            tmp_path,
            '{"pezzi": {"pdc-2": {"x": 35, "y": 110, "regola": "A2"}}}',
        )
    )
    assert piano.pezzi["pdc-2"].regola == "A2"


def test_un_json_non_valido_dice_dove_si_e_rotto(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, '{"pezzi": {"volano": {"x": 1, "y": 2},}}')
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "non e' un JSON valido" in detto
    assert "riga 1 colonna 39" in detto


def test_senza_pezzi_dice_che_manca_il_campo_e_che_forma_ha(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, '{"formato": "A3"}')
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "manca il campo obbligatorio «pezzi»" in detto
    assert '{"id": {"x": …, "y": …}}' in detto


def test_un_pezzo_senza_x_nomina_il_pezzo(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, '{"pezzi": {"volano": {"y": 2}}}')
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "al pezzo «volano» manca «x»" in detto
    assert "millimetri dal bordo sinistro" in detto


def test_un_pezzo_senza_y_nomina_il_pezzo(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, '{"pezzi": {"volano": {"x": 2}}}')
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "al pezzo «volano» manca «y»" in detto
    assert "millimetri dal bordo alto" in detto


def test_una_x_non_numerica_dice_che_cosa_ci_voleva(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, '{"pezzi": {"volano": {"x": "sinistra", "y": 2}}}')
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "«x» del pezzo «volano» non e' valido" in detto
    assert "'sinistra'" in detto
    assert "era atteso un numero" in detto


def test_un_campo_sconosciuto_sul_pezzo_elenca_quelli_che_ci_sono(
    tmp_path: Path,
) -> None:
    percorso = _scrivi(
        tmp_path, '{"pezzi": {"volano": {"x": 1, "y": 2, "colore": "rosso"}}}'
    )
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "il pezzo «volano» porta il campo sconosciuto «colore»" in detto
    # L'elenco e' quello dei campi veri, letto dal modello: si allunga quando il
    # formato cresce — `specchio` e' entrato con **D-169** — e la prova non deve
    # congelarne uno vecchio. Quello che deve restare vero e' che li **elenchi
    # tutti**, perche' chi sbaglia un campo legga quali esistono.
    for campo in PezzoNelPiano.model_fields:
        assert campo in detto, f"il messaggio non nomina il campo «{campo}»"
    assert "x, y, rotazione" in detto


def test_un_campo_sconosciuto_sul_piano_elenca_quelli_che_ci_sono(
    tmp_path: Path,
) -> None:
    percorso = _scrivi(
        tmp_path, '{"scala": "1:50", "pezzi": {"volano": {"x": 1, "y": 2}}}'
    )
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "il piano porta il campo sconosciuto «scala»" in detto
    assert "formato, note, pezzi" in detto


@pytest.mark.parametrize("formato", ["A5", "A4"])
def test_un_formato_fuori_dai_tre_ordinari_li_elenca(tmp_path: Path, formato: str) -> None:
    """D-148 e D-184: i formati ordinari sono tre, e chi ne chiede un altro li legge.

    Erano quattro fino al 25 settembre 2026: l'A4 e' uscito perche' non contiene
    il cartiglio Nove C, e un piano che lo chiede adesso si ferma qui, con la
    lista davanti. Si chiamava `test_un_formato_fuori_dai_quattro_ordinari_li_elenca`."""
    percorso = _scrivi(
        tmp_path, f'{{"formato": "{formato}", "pezzi": {{"volano": {{"x": 1, "y": 2}}}}}}'
    )
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "il campo «formato» non e' valido" in detto
    assert f"'{formato}'" in detto
    assert "A3, A2, A1" in detto


def test_un_pezzo_che_non_e_un_oggetto_lo_dice(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, '{"pezzi": {"volano": 12}}')
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    assert "il pezzo «volano» non e' un oggetto" in str(errore.value)


def test_un_piano_che_non_e_un_oggetto_lo_dice(tmp_path: Path) -> None:
    percorso = _scrivi(tmp_path, "[1, 2]")
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    assert "il piano non e' un oggetto" in str(errore.value)


def test_due_difetti_si_dicono_tutti_e_due(tmp_path: Path) -> None:
    """Chi corregge un piano li corregge insieme: nessuno dei due si nasconde."""
    percorso = _scrivi(
        tmp_path, '{"pezzi": {"volano": {"y": 2}, "bollitore": {"x": 3}}}'
    )
    with pytest.raises(ErroreDelPiano) as errore:
        carica_piano(percorso)
    detto = str(errore.value)
    assert "al pezzo «volano» manca «x»" in detto
    assert "al pezzo «bollitore» manca «y»" in detto


def test_il_piano_che_non_c_e_resta_un_errore_di_sistema(tmp_path: Path) -> None:
    """Un file assente non e' un difetto del piano: e' un piano che non c'e'."""
    with pytest.raises(OSError):
        carica_piano(tmp_path / "non-esiste.json")


def test_il_modello_rifiuta_un_campo_sconosciuto_anche_senza_file() -> None:
    """Il formato e' `StrictModel` come il resto del progetto: niente extra."""
    with pytest.raises(ValueError):
        PianoDiComposizione.model_validate(
            {"pezzi": {"volano": {"x": 1, "y": 2}}, "scala": "1:50"}
        )
