import tomllib
from pathlib import Path

from disegnatore_mep import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_package_version() -> None:
    """La versione del pacchetto e' una sola: quella del `pyproject.toml`, e la skill
    la scrive per intera in testa a `SKILL.md` (I-178, I-187: dalla 1.2.1 il numero ha
    tre cifre, perche' le consegne della beta cambiano solo la terza)."""
    dichiarata = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]["version"]
    assert __version__ == dichiarata == "1.3.0"
    assert f"**Versione {dichiarata}**" in (ROOT / "skill" / "SKILL.md").read_text("utf-8")
