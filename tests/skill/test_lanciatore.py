"""Il lanciatore della skill installa quello che manca (REL-001, seconda parte).

Su claude.ai il Python della macchina puo' essere quello di sistema di un Ubuntu recente,
che protegge i suoi pacchetti (PEP 668): pip rifiuta di installare, e il lanciatore ritenta
dicendo a pip che va bene. Qualunque altro rifiuto si dice com'e', senza ritentare.
"""

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def lanciatore() -> ModuleType:
    spec = importlib.util.spec_from_file_location("mep_lanciatore", ROOT / "skill" / "scripts" / "mep.py")
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _finto_pip(risposte: list[tuple[int, str]], chiamate: list[list[str]]) -> Any:
    def run(comando: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        chiamate.append(comando)
        codice, errore = risposte[len(chiamate) - 1]
        return subprocess.CompletedProcess(comando, codice, "", errore)

    return run


def test_un_python_protetto_si_installa_lo_stesso(
    lanciatore: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    chiamate: list[list[str]] = []
    rifiuto = "error: externally-managed-environment\n"
    monkeypatch.setattr(lanciatore.subprocess, "run", _finto_pip([(1, rifiuto), (0, "")], chiamate))
    assert lanciatore._pip("pydantic==2.13.4") is True
    assert chiamate[0][-1] == "pydantic==2.13.4"
    assert chiamate[1][-1] == "--break-system-packages"


def test_un_altro_rifiuto_si_dice_senza_ritentare(
    lanciatore: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    chiamate: list[list[str]] = []
    rifiuto = "ERROR: Could not find a version that satisfies the requirement pydantic==2.13.4\n"
    monkeypatch.setattr(lanciatore.subprocess, "run", _finto_pip([(1, rifiuto)], chiamate))
    assert lanciatore._pip("pydantic==2.13.4") is False
    assert len(chiamate) == 1
    assert "Could not find a version" in capsys.readouterr().err


# REL-024, la prova senza rete: senza PyPI la skill ritentava l'installazione delle librerie
# facoltative a ogni comando, perdendo ogni volta otto secondi o piu' (pip riprova cinque
# volte). Un tentativo fallito si ricorda per la sessione, e pip ha un limite di attesa.


def test_pip_non_aspetta_minuti_su_una_rete_che_non_risponde(
    lanciatore: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    chiamate: list[list[str]] = []
    monkeypatch.setattr(lanciatore.subprocess, "run", _finto_pip([(0, "")], chiamate))
    lanciatore._pip("ezdxf==1.4.4")
    comando = chiamate[0]
    assert comando[comando.index("--retries") + 1] == "1"
    assert int(comando[comando.index("--timeout") + 1]) <= 15


def test_una_facoltativa_che_non_si_installa_non_si_ritenta_a_ogni_comando(
    lanciatore: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(lanciatore.tempfile, "gettempdir", lambda: str(tmp_path))
    tentativi: list[str] = []
    monkeypatch.setattr(lanciatore, "_pip", lambda pacchetto: tentativi.append(pacchetto) or False)
    for _ in range(3):
        assert lanciatore._installa("ezdxf", "ezdxf==1.4.4", "senza la quale il comando fa meno", ricorda=True) is False
    assert tentativi == ["ezdxf==1.4.4"]
    assert "non riprovo" in capsys.readouterr().err


def test_pydantic_si_ritenta_sempre(
    lanciatore: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Senza pydantic il comando non parte: ogni volta vale la pena di riprovare."""
    monkeypatch.setattr(lanciatore.tempfile, "gettempdir", lambda: str(tmp_path))
    tentativi: list[str] = []
    monkeypatch.setattr(lanciatore, "_pip", lambda pacchetto: tentativi.append(pacchetto) or False)
    for _ in range(2):
        lanciatore._installa("pydantic", "pydantic==2.13.4", "che il motore usa")
    assert tentativi == ["pydantic==2.13.4", "pydantic==2.13.4"]
