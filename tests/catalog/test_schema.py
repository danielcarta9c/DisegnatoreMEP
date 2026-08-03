import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.schema import ComponentDefinition


def port(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "a",
        "domain": "hydronic",
        "medium": "heating_water",
        "flow": "bidirectional",
        "required": True,
        "max_connections": 1,
    }
    base.update(overrides)
    return base


def definition(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "isolation-valve",
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "symbol_id": "valve-isolation",
        "composite": False,
        "ports": [port(id="a"), port(id="b")],
        "sources": ["CONV-001"],
    }
    base.update(overrides)
    return base


def test_rejects_duplicate_port_id() -> None:
    with pytest.raises(ValidationError, match="duplicate port id"):
        ComponentDefinition.model_validate(
            definition(ports=[port(id="a"), port(id="a")])
        )
