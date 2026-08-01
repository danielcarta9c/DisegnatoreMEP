import json
from pathlib import Path

from _pytest.capture import CaptureFixture

from disegnatore_mep.cli import main


def test_valid_mixed_project_passes() -> None:
    root = Path("examples/foundation")
    assert main(["validate", str(root / "valid-mixed-project.json"), "--catalog", str(root / "catalog")]) == 0


def test_cross_medium_project_fails_with_code_two(
    capsys: CaptureFixture[str],
) -> None:
    root = Path("examples/foundation")
    exit_code = main(
        ["validate", str(root / "invalid-cross-medium.json"), "--catalog", str(root / "catalog")]
    )
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert exit_code == 2
    assert "PORT_MEDIUM_MISMATCH" in {item["code"] for item in report["issues"]}
