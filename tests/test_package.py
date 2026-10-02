import tomllib
from pathlib import Path

from disegnatore_mep import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_package_version() -> None:
    """La versione del pacchetto e' una sola: quella del `pyproject.toml`, e la skill
    la scrive in testa a `SKILL.md` (I-178: la skill «in Rev 1.2»)."""
    dichiarata = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]["version"]
    assert __version__ == dichiarata == "1.2.0"
    principale, minore, _ = dichiarata.split(".")
    assert f"**Versione {principale}.{minore}**" in (ROOT / "skill" / "SKILL.md").read_text("utf-8")
