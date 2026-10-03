"""Le release pubblicate in `releases/` dicono tutte lo stesso numero (D-198).

La 1.2.0 e' la prima, ed e' lo ZIP che il PO ha distribuito ai collaboratori il 2 ottobre
2026, cosi' come e' stato consegnato; la 1.2.1 e' la prima consegna della beta (I-187).
Questa prova tiene insieme le tre cose che portano il numero — il pacchetto Python, la
riga in testa a `SKILL.md` dentro lo ZIP, il nome dello ZIP — e la copia in `latest/` con
quella numerata in `archive/`: alla prossima versione, chi alza il numero e non pubblica lo
ZIP lo vede qui.
"""

# categoria: difende la consegna — il numero della release e' uno solo (D-198), e ogni ZIP
# pubblicato si carica su claude.ai (I-189, D-200)

import importlib.util
import re
import tomllib
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT / "releases"
CONVENZIONE = re.compile(r"DisegnatoreMEP-v(\d+)\.(\d+)\.(\d+)\.zip")

NON_SI_CARICAVANO = {"DisegnatoreMEP-v1.2.0.zip", "DisegnatoreMEP-v1.2.1.zip"}
"""Le due release uscite con 287 e 284 file, oltre i 200 che claude.ai accetta: la
correzione stava su un ramo mai fuso (I-188, I-189). Restano nell'archivio come sono state
pubblicate; l'elenco e' chiuso, e una release nuova che non si carica fa cadere la prova."""


@pytest.fixture(scope="module")
def costruttore() -> ModuleType:
    spec = importlib.util.spec_from_file_location("costruisci_skill", ROOT / "scripts" / "costruisci-skill.py")
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _versione() -> str:
    return str(tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]["version"])


def test_latest_porta_lo_zip_della_versione_del_pacchetto() -> None:
    zip_ = sorted((RELEASES / "latest").glob("*.zip"))
    assert [item.name for item in zip_] == [f"DisegnatoreMEP-v{_versione()}.zip"]


def test_la_copia_in_latest_e_quella_numerata_dell_archivio() -> None:
    nome = f"DisegnatoreMEP-v{_versione()}.zip"
    assert (RELEASES / "latest" / nome).read_bytes() == (RELEASES / "archive" / nome).read_bytes()


def test_ogni_zip_dell_archivio_segue_la_convenzione() -> None:
    nomi = [item.name for item in (RELEASES / "archive").glob("*.zip")]
    assert nomi
    assert all(CONVENZIONE.fullmatch(nome) for nome in nomi), nomi


def test_la_skill_nello_zip_dice_il_proprio_numero() -> None:
    with zipfile.ZipFile(RELEASES / "latest" / f"DisegnatoreMEP-v{_versione()}.zip") as archivio:
        skill = archivio.read("disegnatore-mep/SKILL.md").decode("utf-8")
    assert f"**Versione {_versione()}**" in skill


def test_lo_zip_in_latest_si_carica_su_claude_ai(costruttore: ModuleType) -> None:
    """I-189: «non possiamo ad ogni release fare lo stesso errore». Lo ZIP che si
    distribuisce passa gli stessi controlli della costruzione: al massimo 200 file, tutto in
    una cartella, sotto i 30 MB, e la skill dentro con le linee guida di Anthropic."""
    zip_ = RELEASES / "latest" / f"DisegnatoreMEP-v{_versione()}.zip"
    assert costruttore.controlla_lo_zip(zip_) == []


def test_nell_archivio_non_si_caricano_solo_le_due_gia_note(costruttore: ModuleType) -> None:
    non_si_caricano = {
        item.name for item in (RELEASES / "archive").glob("*.zip") if costruttore.controlla_lo_zip(item)
    }
    assert non_si_caricano == NON_SI_CARICAVANO
