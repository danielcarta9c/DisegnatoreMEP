import json
from pathlib import Path

from _pytest.capture import CaptureFixture

from disegnatore_mep.cli import main

FIXTURES = Path(__file__).resolve().parents[2] / "examples" / "foundation"


def test_valid_mixed_project_passes() -> None:
    assert (
        main(
            [
                "validate",
                str(FIXTURES / "valid-mixed-project.json"),
                "--catalog",
                str(FIXTURES / "catalog"),
            ]
        )
        == 0
    )


def test_cross_medium_project_fails_with_code_two(
    capsys: CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "validate",
            str(FIXTURES / "invalid-cross-medium.json"),
            "--catalog",
            str(FIXTURES / "catalog"),
        ]
    )
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert exit_code == 2
    assert "PORT_MEDIUM_MISMATCH" in {item["code"] for item in report["issues"]}
