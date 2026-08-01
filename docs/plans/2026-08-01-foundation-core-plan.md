# Foundation Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** costruire la fondazione installabile e testata che rappresenta, valida e serializza impianti termici multi-dominio senza contenere schemi tipo o logica di rendering.

**Architecture:** un modello Pydantic canonico descrive progetto, reti, componenti e connessioni. Un catalogo carica definizioni di componenti con porte tipizzate; pacchetti di dominio verificano la compatibilità; un validatore topologico produce diagnostiche strutturate. Una CLI carica JSON, valida il progetto, esporta lo schema e calcola un fingerprint riproducibile.

**Tech Stack:** Python 3.12.13 di riferimento; Python minimo 3.11; setuptools 83.0.0; Pydantic 2.13.4; pytest 9.1.1; Ruff 0.15.22; mypy 2.3.0; libreria standard `json`, `hashlib`, `argparse`, `pathlib`.

## Global Constraints

- Sistema operativo di sviluppo: Windows; tutti i comandi sono PowerShell.
- Il modello tecnico canonico è la fonte di verità; nessun SVG o PDF viene creato in questo piano.
- Il nucleo espone primitive universali; la compatibilità specifica vive nei pacchetti di dominio.
- Nessun file contiene una funzione dedicata a uno schema PDC, radiatori, VRV o caldaia.
- Le definizioni di componente usano millimetri per la geometria del simbolo, anche se il renderer verrà costruito in un piano successivo.
- Ogni identificativo segue `^[a-z][a-z0-9_-]*$`; le versioni seguono SemVer.
- Tutti i modelli rifiutano campi sconosciuti.
- La serializzazione canonica ordina le collezioni per identificativo e produce UTF-8 stabile.
- Il comando `validate` restituisce `0` per progetto valido, `2` per errori di validazione e `1` per errori di caricamento.
- `releases/latest/` e `releases/archive/` non vengono modificati.
- Ogni task segue red-green-refactor e termina con un commit autonomo.

---

## Struttura dei file

```text
pyproject.toml
src/disegnatore_mep/
  __init__.py
  __main__.py
  cli.py
  model/
    __init__.py
    base.py
    types.py
    project.py
  catalog/
    __init__.py
    schema.py
    registry.py
  domains/
    __init__.py
    base.py
    builtin.py
    registry.py
  validation/
    __init__.py
    issues.py
    topology.py
  io/
    __init__.py
    canonical.py
    project_json.py
schemas/
  project.schema.json
examples/foundation/
  catalog/*.json
  valid-mixed-project.json
  invalid-cross-medium.json
tests/
  test_package.py
  model/test_project.py
  catalog/test_registry.py
  domains/test_builtin.py
  validation/test_topology.py
  io/test_canonical.py
  test_cli.py
  acceptance/test_foundation_cli.py
docs/ARCHITECTURE.md
```

## Contratti pubblici prodotti dal piano

- Modelli: `ProjectModel`, `ComponentDefinition`, `ValidationIssue`, `ValidationReport`.
- Registry: `ComponentRegistry`, `DomainRegistry` e protocollo `DomainPack`.
- Validazione: `validate_project(project, catalog, domains=None) -> ValidationReport`.
- I/O: `load_project(path) -> ProjectModel` e `dump_project(project, path) -> None`.
- Riproducibilità: `canonical_json(project) -> str` e `project_fingerprint(project) -> str`.
- CLI: `main(argv=None) -> int`.

Le firme sono vincolanti per tutti i task e vengono definite integralmente nelle sezioni successive.

---

### Task 1: Bootstrap del pacchetto e toolchain

**Files:**
- Create: `pyproject.toml`
- Create: `src/disegnatore_mep/__init__.py`
- Create: `tests/test_package.py`

**Interfaces:**
- Consumes: nessuna interfaccia precedente.
- Produces: `disegnatore_mep.__version__: str` uguale a `0.1.0`.

- [ ] **Step 1: creare l'ambiente virtuale**

Run:

```powershell
$python = 'C:\Users\DanielCarta\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Expected: `.venv\Scripts\python.exe --version` stampa Python 3.12.x.

- [ ] **Step 2: scrivere il test che fallisce**

Create `tests/test_package.py`:

```python
from disegnatore_mep import __version__


def test_package_version() -> None:
    assert __version__ == "0.1.0"
```

- [ ] **Step 3: verificare il fallimento iniziale**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/test_package.py -v
```

Expected: FAIL con `No module named 'disegnatore_mep'` oppure `No module named 'pytest'`.

- [ ] **Step 4: creare configurazione e pacchetto minimo**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools==83.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "disegnatore-mep"
version = "0.1.0"
description = "Deterministic foundation for technical MEP schematics"
requires-python = ">=3.11"
dependencies = [
  "pydantic==2.13.4",
]

[project.optional-dependencies]
dev = [
  "mypy==2.3.0",
  "pytest==9.1.1",
  "ruff==0.15.22",
]

[project.scripts]
disegnatore-mep = "disegnatore_mep.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]
packages = ["disegnatore_mep"]
```

Create `src/disegnatore_mep/__init__.py`:

```python
"""Disegnatore MEP deterministic core."""

__version__ = "0.1.0"
```

- [ ] **Step 5: installare il progetto e verificare il test**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
& .\.venv\Scripts\python.exe -m pytest tests/test_package.py -v
```

Expected: `1 passed`.

- [ ] **Step 6: verificare lint e tipi**

Run:

```powershell
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src
```

Expected: entrambi exit code `0`.

- [ ] **Step 7: commit**

```powershell
git add pyproject.toml src/disegnatore_mep/__init__.py tests/test_package.py
git commit -m "chore: bootstrap deterministic core package"
```

---

### Task 2: Modello canonico del progetto

**Files:**
- Create: `src/disegnatore_mep/model/__init__.py`
- Create: `src/disegnatore_mep/model/base.py`
- Create: `src/disegnatore_mep/model/types.py`
- Create: `src/disegnatore_mep/model/project.py`
- Create: `tests/model/test_project.py`

**Interfaces:**
- Consumes: Pydantic 2.13.4.
- Produces: `StrictModel`, enum di dominio, `ProjectModel` e relativi modelli.

- [ ] **Step 1: scrivere test di validazione e unicità**

Create `tests/model/test_project.py`:

```python
from datetime import date

import pytest
from pydantic import ValidationError

from disegnatore_mep.model.project import (
    ComponentInstance,
    ProjectMetadata,
    ProjectModel,
)


def metadata() -> ProjectMetadata:
    return ProjectMetadata(
        project_id="demo",
        client="Nove C",
        project_name="Impianto dimostrativo",
        commission_code="MI-001",
        revision="00",
        issue_date=date(2026, 8, 1),
    )


def test_project_rejects_duplicate_component_ids() -> None:
    component = ComponentInstance(
        id="boiler-1",
        definition_id="gas-boiler",
        tag="CAL-01",
    )
    with pytest.raises(ValidationError, match="duplicate component id: boiler-1"):
        ProjectModel(metadata=metadata(), components=[component, component])


def test_project_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProjectMetadata(
            project_id="demo",
            client="Nove C",
            project_name="Impianto dimostrativo",
            commission_code="MI-001",
            revision="00",
            issue_date=date(2026, 8, 1),
            unsupported="value",
        )


def test_project_schema_version_is_fixed() -> None:
    project = ProjectModel(metadata=metadata())
    assert project.schema_version == "1.0.0"
```

- [ ] **Step 2: eseguire i test e verificare il fallimento**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/model/test_project.py -v
```

Expected: FAIL perché `disegnatore_mep.model` non esiste.

- [ ] **Step 3: implementare base ed enum**

Create `src/disegnatore_mep/model/base.py`:

```python
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
```

Create `src/disegnatore_mep/model/types.py`:

```python
from enum import StrEnum


class Domain(StrEnum):
    HYDRONIC = "hydronic"
    AERAULIC = "aeraulic"
    REFRIGERANT = "refrigerant"
    GAS = "gas"
    CONDENSATE = "condensate"
    CONTROL = "control"


class PortFlow(StrEnum):
    IN = "in"
    OUT = "out"
    BIDIRECTIONAL = "bidirectional"


class IssueSeverity(StrEnum):
    BLOCKING = "blocking"
    APPROVAL = "approval"
    WARNING = "warning"


class ApprovalStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"


class IntegrationCategory(StrEnum):
    NECESSARY = "necessary"
    RECOMMENDED = "recommended"
    CONDITIONAL = "conditional"


JsonPrimitive = str | int | float | bool | None
```

- [ ] **Step 4: implementare il modello progetto**

Create `src/disegnatore_mep/model/project.py`:

```python
from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from .base import StrictModel
from .types import (
    ApprovalStatus,
    Domain,
    IntegrationCategory,
    JsonPrimitive,
)

ID_PATTERN = r"^[a-z][a-z0-9_-]*$"


class ProjectMetadata(StrictModel):
    project_id: str = Field(pattern=ID_PATTERN)
    client: str = Field(min_length=1)
    project_name: str = Field(min_length=1)
    commission_code: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    issue_date: date


class EvidenceRef(StrictModel):
    kind: Literal["conversation", "attachment", "engineer", "rule"]
    reference: str = Field(min_length=1)
    note: str | None = None


class NetworkModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ComponentInstance(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    definition_id: str = Field(pattern=ID_PATTERN)
    tag: str | None = None
    properties: dict[str, JsonPrimitive] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class PortRef(StrictModel):
    component_id: str = Field(pattern=ID_PATTERN)
    port_id: str = Field(pattern=ID_PATTERN)


class ConnectionModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    network_id: str = Field(pattern=ID_PATTERN)
    endpoint_a: PortRef
    endpoint_b: PortRef
    properties: dict[str, JsonPrimitive] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def endpoints_must_differ(self) -> "ConnectionModel":
        if self.endpoint_a == self.endpoint_b:
            raise ValueError("connection endpoints must differ")
        return self


class AssumptionModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    text: str = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    source_message_refs: list[str] = Field(default_factory=list)


class RuleApplicationModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    rule_id: str = Field(pattern=ID_PATTERN)
    rule_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    category: IntegrationCategory
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    entity_ids: list[str] = Field(default_factory=list)


class SubsystemModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    component_ids: list[str] = Field(default_factory=list)
    network_ids: list[str] = Field(default_factory=list)


class SheetIntentModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    title: str = Field(min_length=1)
    subsystem_ids: list[str] = Field(default_factory=list)


class ProjectModel(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    metadata: ProjectMetadata
    subsystems: list[SubsystemModel] = Field(default_factory=list)
    networks: list[NetworkModel] = Field(default_factory=list)
    components: list[ComponentInstance] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)
    assumptions: list[AssumptionModel] = Field(default_factory=list)
    rule_applications: list[RuleApplicationModel] = Field(default_factory=list)
    sheets: list[SheetIntentModel] = Field(default_factory=list)

    @model_validator(mode="after")
    def identifiers_must_be_unique(self) -> "ProjectModel":
        collections = {
            "subsystem": self.subsystems,
            "network": self.networks,
            "component": self.components,
            "connection": self.connections,
            "assumption": self.assumptions,
            "rule application": self.rule_applications,
            "sheet": self.sheets,
        }
        for label, items in collections.items():
            seen: set[str] = set()
            for item in items:
                if item.id in seen:
                    raise ValueError(f"duplicate {label} id: {item.id}")
                seen.add(item.id)
        tags = [item.tag for item in self.components if item.tag is not None]
        if len(tags) != len(set(tags)):
            raise ValueError("duplicate component tag")
        return self
```

Create `src/disegnatore_mep/model/__init__.py`:

```python
from .project import ProjectModel

__all__ = ["ProjectModel"]
```

- [ ] **Step 5: eseguire test, lint e type check**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/model/test_project.py -v
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src
```

Expected: tutti exit code `0`.

- [ ] **Step 6: commit**

```powershell
git add src/disegnatore_mep/model tests/model/test_project.py
git commit -m "feat: add canonical project model"
```

---

### Task 3: Definizioni dei componenti e catalogo

**Files:**
- Create: `src/disegnatore_mep/catalog/__init__.py`
- Create: `src/disegnatore_mep/catalog/schema.py`
- Create: `src/disegnatore_mep/catalog/registry.py`
- Create: `tests/catalog/test_registry.py`

**Interfaces:**
- Consumes: `StrictModel`, `Domain`, `PortFlow`, `ID_PATTERN`.
- Produces: `ComponentDefinition`, `PortDefinition`, `SymbolGeometry`, `ComponentRegistry`.

- [ ] **Step 1: scrivere test per caricamento e duplicati**

Create `tests/catalog/test_registry.py`:

```python
import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry


def definition(component_id: str) -> dict[str, object]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "symbol_id": "valve-isolation",
        "composite": False,
        "geometry": {
            "width_mm": 6.0,
            "height_mm": 6.0,
            "clearance_mm": 2.0,
            "allowed_rotations_deg": [0, 90, 180, 270],
            "inline_gap_mm": 6.0,
        },
        "ports": [
            {
                "id": "a",
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "bidirectional",
                "x_mm": 0.0,
                "y_mm": 3.0,
                "angle_deg": 180,
                "required": True,
                "max_connections": 1,
            },
            {
                "id": "b",
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "bidirectional",
                "x_mm": 6.0,
                "y_mm": 3.0,
                "angle_deg": 0,
                "required": True,
                "max_connections": 1,
            },
        ],
        "sources": ["CONV-001"],
    }


def write_definition(path: Path, component_id: str) -> None:
    path.write_text(json.dumps(definition(component_id)), encoding="utf-8")


def test_registry_loads_definition(tmp_path: Path) -> None:
    write_definition(tmp_path / "valve.json", "isolation-valve")
    registry = ComponentRegistry.from_directory(tmp_path)
    assert registry.get("isolation-valve").geometry.inline_gap_mm == 6.0


def test_registry_rejects_duplicate_ids(tmp_path: Path) -> None:
    write_definition(tmp_path / "a.json", "isolation-valve")
    write_definition(tmp_path / "b.json", "isolation-valve")
    with pytest.raises(CatalogError, match="duplicate component definition"):
        ComponentRegistry.from_directory(tmp_path)
```

- [ ] **Step 2: verificare il fallimento**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/catalog/test_registry.py -v
```

Expected: FAIL perché `disegnatore_mep.catalog` non esiste.

- [ ] **Step 3: implementare lo schema del catalogo**

Create `src/disegnatore_mep/catalog/schema.py`:

```python
from pydantic import Field, model_validator

from disegnatore_mep.model.base import StrictModel
from disegnatore_mep.model.project import ID_PATTERN
from disegnatore_mep.model.types import Domain, PortFlow


class SymbolGeometry(StrictModel):
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    clearance_mm: float = Field(ge=0)
    allowed_rotations_deg: list[int] = Field(min_length=1)
    inline_gap_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def rotations_are_orthogonal(self) -> "SymbolGeometry":
        allowed = {0, 90, 180, 270}
        if not set(self.allowed_rotations_deg).issubset(allowed):
            raise ValueError("allowed rotations must be 0, 90, 180 or 270")
        if len(self.allowed_rotations_deg) != len(set(self.allowed_rotations_deg)):
            raise ValueError("duplicate allowed rotation")
        return self


class PortDefinition(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    flow: PortFlow
    x_mm: float
    y_mm: float
    angle_deg: int
    required: bool = True
    max_connections: int = Field(default=1, ge=1)


class ComponentDefinition(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    functions: list[str] = Field(min_length=1)
    symbol_id: str = Field(pattern=ID_PATTERN)
    composite: bool = False
    geometry: SymbolGeometry
    ports: list[PortDefinition] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def port_ids_are_unique_and_inside_geometry(self) -> "ComponentDefinition":
        ids = [port.id for port in self.ports]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate port id")
        for port in self.ports:
            if not 0 <= port.x_mm <= self.geometry.width_mm:
                raise ValueError(f"port outside symbol width: {port.id}")
            if not 0 <= port.y_mm <= self.geometry.height_mm:
                raise ValueError(f"port outside symbol height: {port.id}")
        return self
```

- [ ] **Step 4: implementare il registry**

Create `src/disegnatore_mep/catalog/registry.py`:

```python
from pathlib import Path

from pydantic import ValidationError

from .schema import ComponentDefinition


class CatalogError(ValueError):
    pass


class ComponentRegistry:
    def __init__(self, definitions: list[ComponentDefinition]) -> None:
        self._definitions: dict[str, ComponentDefinition] = {}
        for definition in definitions:
            if definition.id in self._definitions:
                raise CatalogError(f"duplicate component definition: {definition.id}")
            self._definitions[definition.id] = definition

    @classmethod
    def from_directory(cls, directory: Path) -> "ComponentRegistry":
        definitions: list[ComponentDefinition] = []
        for path in sorted(directory.glob("*.json")):
            try:
                definitions.append(ComponentDefinition.model_validate_json(path.read_text("utf-8")))
            except (OSError, ValidationError, ValueError) as exc:
                raise CatalogError(f"invalid catalog file {path}: {exc}") from exc
        return cls(definitions)

    def get(self, definition_id: str) -> ComponentDefinition:
        try:
            return self._definitions[definition_id]
        except KeyError as exc:
            raise CatalogError(f"unknown component definition: {definition_id}") from exc

    def contains(self, definition_id: str) -> bool:
        return definition_id in self._definitions

    def all(self) -> tuple[ComponentDefinition, ...]:
        return tuple(self._definitions[key] for key in sorted(self._definitions))
```

Create `src/disegnatore_mep/catalog/__init__.py`:

```python
from .registry import ComponentRegistry
from .schema import ComponentDefinition

__all__ = ["ComponentDefinition", "ComponentRegistry"]
```

- [ ] **Step 5: eseguire verifiche**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/catalog/test_registry.py -v
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src
```

Expected: tutti exit code `0`.

- [ ] **Step 6: commit**

```powershell
git add src/disegnatore_mep/catalog tests/catalog/test_registry.py
git commit -m "feat: add versioned component catalog"
```

---

### Task 4: Contratti e registry dei domini

**Files:**
- Create: `src/disegnatore_mep/validation/__init__.py`
- Create: `src/disegnatore_mep/validation/issues.py`
- Create: `src/disegnatore_mep/domains/__init__.py`
- Create: `src/disegnatore_mep/domains/base.py`
- Create: `src/disegnatore_mep/domains/builtin.py`
- Create: `src/disegnatore_mep/domains/registry.py`
- Create: `tests/domains/test_builtin.py`

**Interfaces:**
- Consumes: `PortDefinition`, `NetworkModel`, `Domain`.
- Produces: `ValidationIssue`, `DomainPack`, `DomainRegistry`, `default_domain_registry()`.

- [ ] **Step 1: scrivere test di registrazione e compatibilità**

Create `tests/domains/test_builtin.py`:

```python
from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.domains.registry import default_domain_registry
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain, PortFlow


def port(domain: Domain, medium: str, flow: PortFlow) -> PortDefinition:
    return PortDefinition(
        id="p",
        domain=domain,
        medium=medium,
        flow=flow,
        x_mm=0,
        y_mm=0,
        angle_deg=0,
    )


def test_all_domains_have_a_pack() -> None:
    registry = default_domain_registry()
    assert {pack.domain for pack in registry.all()} == set(Domain)


def test_pack_rejects_cross_medium_connection() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "chilled_water", PortFlow.IN),
        network,
    )
    assert [issue.code for issue in issues] == ["PORT_MEDIUM_MISMATCH"]


def test_pack_accepts_output_to_input() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "heating_water", PortFlow.IN),
        network,
    )
    assert issues == []
```

- [ ] **Step 2: verificare il fallimento**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/domains/test_builtin.py -v
```

Expected: FAIL perché `disegnatore_mep.domains` non esiste.

- [ ] **Step 3: implementare diagnostiche e protocollo**

Create `src/disegnatore_mep/validation/issues.py`:

```python
from pydantic import Field

from disegnatore_mep.model.base import StrictModel
from disegnatore_mep.model.types import IssueSeverity


class ValidationIssue(StrictModel):
    code: str = Field(pattern=r"^[A-Z][A-Z0-9_]*$")
    severity: IssueSeverity
    message: str = Field(min_length=1)
    entity_ids: list[str] = Field(default_factory=list)
```

Create `src/disegnatore_mep/domains/base.py`:

```python
from typing import Protocol

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain
from disegnatore_mep.validation.issues import ValidationIssue


class DomainPack(Protocol):
    domain: Domain

    def validate_pair(
        self,
        port_a: PortDefinition,
        port_b: PortDefinition,
        network: NetworkModel,
    ) -> list[ValidationIssue]:
        raise NotImplementedError
```

- [ ] **Step 4: implementare il pacchetto base e il registry**

Create `src/disegnatore_mep/domains/builtin.py`:

```python
from dataclasses import dataclass

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain, IssueSeverity, PortFlow
from disegnatore_mep.validation.issues import ValidationIssue


@dataclass(frozen=True)
class BasicDomainPack:
    domain: Domain

    def validate_pair(
        self,
        port_a: PortDefinition,
        port_b: PortDefinition,
        network: NetworkModel,
    ) -> list[ValidationIssue]:
        entities = [network.id, port_a.id, port_b.id]
        if network.domain != self.domain or port_a.domain != self.domain or port_b.domain != self.domain:
            return [
                ValidationIssue(
                    code="PORT_DOMAIN_MISMATCH",
                    severity=IssueSeverity.BLOCKING,
                    message=f"ports and network must belong to {self.domain.value}",
                    entity_ids=entities,
                )
            ]
        if port_a.medium != network.medium or port_b.medium != network.medium:
            return [
                ValidationIssue(
                    code="PORT_MEDIUM_MISMATCH",
                    severity=IssueSeverity.BLOCKING,
                    message=f"ports must use network medium {network.medium}",
                    entity_ids=entities,
                )
            ]
        invalid_pair = port_a.flow == port_b.flow and port_a.flow != PortFlow.BIDIRECTIONAL
        if invalid_pair:
            return [
                ValidationIssue(
                    code="PORT_FLOW_MISMATCH",
                    severity=IssueSeverity.BLOCKING,
                    message=f"cannot connect two {port_a.flow.value} ports",
                    entity_ids=entities,
                )
            ]
        return []
```

Create `src/disegnatore_mep/domains/registry.py`:

```python
from disegnatore_mep.model.types import Domain

from .base import DomainPack
from .builtin import BasicDomainPack


class DomainRegistry:
    def __init__(self, packs: list[DomainPack]) -> None:
        self._packs: dict[Domain, DomainPack] = {}
        for pack in packs:
            if pack.domain in self._packs:
                raise ValueError(f"duplicate domain pack: {pack.domain.value}")
            self._packs[pack.domain] = pack

    def get(self, domain: Domain) -> DomainPack:
        try:
            return self._packs[domain]
        except KeyError as exc:
            raise ValueError(f"missing domain pack: {domain.value}") from exc

    def all(self) -> tuple[DomainPack, ...]:
        return tuple(self._packs[key] for key in sorted(self._packs, key=str))


def default_domain_registry() -> DomainRegistry:
    return DomainRegistry([BasicDomainPack(domain) for domain in Domain])
```

Create `src/disegnatore_mep/domains/__init__.py`:

```python
from .registry import DomainRegistry, default_domain_registry

__all__ = ["DomainRegistry", "default_domain_registry"]
```

Create `src/disegnatore_mep/validation/__init__.py`:

```python
from .issues import ValidationIssue

__all__ = ["ValidationIssue"]
```

- [ ] **Step 5: eseguire verifiche**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/domains/test_builtin.py -v
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src
```

Expected: tutti exit code `0`.

- [ ] **Step 6: commit**

```powershell
git add src/disegnatore_mep/domains src/disegnatore_mep/validation tests/domains
git commit -m "feat: add domain compatibility contracts"
```

---

### Task 5: Validatore topologico

**Files:**
- Modify: `src/disegnatore_mep/validation/issues.py`
- Create: `src/disegnatore_mep/validation/topology.py`
- Modify: `src/disegnatore_mep/validation/__init__.py`
- Create: `tests/validation/test_topology.py`

**Interfaces:**
- Consumes: `ProjectModel`, `ComponentRegistry`, `DomainRegistry`.
- Produces: `ValidationReport` e `validate_project(...)`.

- [ ] **Step 1: scrivere test validi e non validi**

Create `tests/validation/test_topology.py`:

```python
from datetime import date

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    ComponentDefinition,
    PortDefinition,
    SymbolGeometry,
)
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import Domain, PortFlow
from disegnatore_mep.validation.topology import validate_project


def component_definition(component_id: str, flow: PortFlow) -> ComponentDefinition:
    return ComponentDefinition(
        id=component_id,
        version="1.0.0",
        name=component_id,
        functions=["boundary"],
        symbol_id=component_id,
        composite=False,
        geometry=SymbolGeometry(
            width_mm=10,
            height_mm=10,
            clearance_mm=2,
            allowed_rotations_deg=[0],
        ),
        ports=[
            PortDefinition(
                id="port",
                domain=Domain.HYDRONIC,
                medium="heating_water",
                flow=flow,
                x_mm=5,
                y_mm=5,
                angle_deg=0,
            )
        ],
        sources=["CONV-001"],
    )


def project() -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="demo",
            client="Nove C",
            project_name="Demo",
            commission_code="MI-001",
            revision="00",
            issue_date=date(2026, 8, 1),
        ),
        networks=[
            NetworkModel(
                id="heating",
                name="Riscaldamento",
                domain=Domain.HYDRONIC,
                medium="heating_water",
            )
        ],
        components=[
            ComponentInstance(id="source", definition_id="source-def"),
            ComponentInstance(id="sink", definition_id="sink-def"),
        ],
        connections=[
            ConnectionModel(
                id="pipe-1",
                network_id="heating",
                endpoint_a=PortRef(component_id="source", port_id="port"),
                endpoint_b=PortRef(component_id="sink", port_id="port"),
            )
        ],
    )


def test_valid_project_has_no_issues() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(project(), catalog)
    assert report.ok is True
    assert report.issues == []


def test_unknown_definition_is_blocking() -> None:
    catalog = ComponentRegistry([component_definition("source-def", PortFlow.OUT)])
    report = validate_project(project(), catalog)
    assert report.ok is False
    assert "UNKNOWN_COMPONENT_DEFINITION" in {issue.code for issue in report.issues}


def test_required_unconnected_port_is_blocking() -> None:
    disconnected = project().model_copy(update={"connections": []})
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(disconnected, catalog)
    assert report.ok is False
    assert [issue.code for issue in report.issues].count("REQUIRED_PORT_UNCONNECTED") == 2


def test_unknown_subsystem_member_is_blocking() -> None:
    invalid = project().model_copy(
        update={
            "subsystems": [
                SubsystemModel(
                    id="plant",
                    name="Centrale",
                    component_ids=["missing-component"],
                )
            ]
        }
    )
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(invalid, catalog)
    assert "UNKNOWN_SUBSYSTEM_COMPONENT" in {issue.code for issue in report.issues}


def test_duplicate_connection_is_blocking() -> None:
    base = project()
    duplicate = base.connections[0].model_copy(update={"id": "pipe-2"})
    invalid = base.model_copy(update={"connections": [base.connections[0], duplicate]})
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(invalid, catalog)
    assert "DUPLICATE_CONNECTION" in {issue.code for issue in report.issues}
```

- [ ] **Step 2: verificare il fallimento**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/validation/test_topology.py -v
```

Expected: FAIL perché `validation.topology` non esiste.

- [ ] **Step 3: aggiungere il report**

Append to `src/disegnatore_mep/validation/issues.py`:

```python


class ValidationReport(StrictModel):
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == IssueSeverity.BLOCKING for issue in self.issues)
```

- [ ] **Step 4: implementare il validatore**

Create `src/disegnatore_mep/validation/topology.py`:

```python
from collections import Counter

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.domains.registry import DomainRegistry, default_domain_registry
from disegnatore_mep.model.project import ComponentInstance, PortRef, ProjectModel
from disegnatore_mep.model.types import IssueSeverity

from .issues import ValidationIssue, ValidationReport


def _issue(code: str, message: str, entity_ids: list[str]) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=IssueSeverity.BLOCKING,
        message=message,
        entity_ids=entity_ids,
    )


def _resolve_port(
    ref: PortRef,
    components: dict[str, ComponentInstance],
    catalog: ComponentRegistry,
) -> tuple[PortDefinition | None, list[ValidationIssue]]:
    component = components.get(ref.component_id)
    if component is None:
        return None, [_issue("UNKNOWN_COMPONENT", "unknown component", [ref.component_id])]
    try:
        definition = catalog.get(component.definition_id)
    except CatalogError:
        return None, [
            _issue(
                "UNKNOWN_COMPONENT_DEFINITION",
                f"unknown definition {component.definition_id}",
                [component.id, component.definition_id],
            )
        ]
    port = next((item for item in definition.ports if item.id == ref.port_id), None)
    if port is None:
        return None, [
            _issue(
                "UNKNOWN_PORT",
                f"unknown port {ref.port_id}",
                [component.id, ref.port_id],
            )
        ]
    return port, []


def validate_project(
    project: ProjectModel,
    catalog: ComponentRegistry,
    domains: DomainRegistry | None = None,
) -> ValidationReport:
    domain_registry = domains or default_domain_registry()
    components = {item.id: item for item in project.components}
    networks = {item.id: item for item in project.networks}
    subsystems = {item.id: item for item in project.subsystems}
    usage: Counter[tuple[str, str]] = Counter()
    seen_edges: set[tuple[str, tuple[str, str], tuple[str, str]]] = set()
    issues: list[ValidationIssue] = []

    for component in project.components:
        if not catalog.contains(component.definition_id):
            issues.append(
                _issue(
                    "UNKNOWN_COMPONENT_DEFINITION",
                    f"unknown definition {component.definition_id}",
                    [component.id, component.definition_id],
                )
            )

    for subsystem in project.subsystems:
        for component_id in subsystem.component_ids:
            if component_id not in components:
                issues.append(
                    _issue(
                        "UNKNOWN_SUBSYSTEM_COMPONENT",
                        f"unknown component {component_id} in subsystem {subsystem.id}",
                        [subsystem.id, component_id],
                    )
                )
        for network_id in subsystem.network_ids:
            if network_id not in networks:
                issues.append(
                    _issue(
                        "UNKNOWN_SUBSYSTEM_NETWORK",
                        f"unknown network {network_id} in subsystem {subsystem.id}",
                        [subsystem.id, network_id],
                    )
                )

    for sheet in project.sheets:
        for subsystem_id in sheet.subsystem_ids:
            if subsystem_id not in subsystems:
                issues.append(
                    _issue(
                        "UNKNOWN_SHEET_SUBSYSTEM",
                        f"unknown subsystem {subsystem_id} in sheet {sheet.id}",
                        [sheet.id, subsystem_id],
                    )
                )

    for connection in project.connections:
        endpoint_a = (connection.endpoint_a.component_id, connection.endpoint_a.port_id)
        endpoint_b = (connection.endpoint_b.component_id, connection.endpoint_b.port_id)
        edge_key = (connection.network_id, *sorted((endpoint_a, endpoint_b)))
        if edge_key in seen_edges:
            issues.append(
                _issue(
                    "DUPLICATE_CONNECTION",
                    f"duplicate connection {connection.id}",
                    [connection.id],
                )
            )
        seen_edges.add(edge_key)
        network = networks.get(connection.network_id)
        if network is None:
            issues.append(
                _issue(
                    "UNKNOWN_NETWORK",
                    f"unknown network {connection.network_id}",
                    [connection.id, connection.network_id],
                )
            )
            continue
        port_a, errors_a = _resolve_port(connection.endpoint_a, components, catalog)
        port_b, errors_b = _resolve_port(connection.endpoint_b, components, catalog)
        issues.extend(errors_a)
        issues.extend(errors_b)
        if port_a is None or port_b is None:
            continue
        usage[(connection.endpoint_a.component_id, connection.endpoint_a.port_id)] += 1
        usage[(connection.endpoint_b.component_id, connection.endpoint_b.port_id)] += 1
        issues.extend(domain_registry.get(network.domain).validate_pair(port_a, port_b, network))

    for component in project.components:
        if not catalog.contains(component.definition_id):
            continue
        definition = catalog.get(component.definition_id)
        for port in definition.ports:
            count = usage[(component.id, port.id)]
            if port.required and count == 0:
                issues.append(
                    _issue(
                        "REQUIRED_PORT_UNCONNECTED",
                        f"required port {port.id} is unconnected",
                        [component.id, port.id],
                    )
                )
            if count > port.max_connections:
                issues.append(
                    _issue(
                        "PORT_CONNECTION_LIMIT",
                        f"port {port.id} has {count} connections; maximum is {port.max_connections}",
                        [component.id, port.id],
                    )
                )

    unique = {
        (item.code, tuple(item.entity_ids), item.message): item
        for item in issues
    }
    ordered = sorted(unique.values(), key=lambda item: (item.code, item.entity_ids, item.message))
    return ValidationReport(issues=ordered)
```

Replace `src/disegnatore_mep/validation/__init__.py` with:

```python
from .issues import ValidationIssue, ValidationReport
from .topology import validate_project

__all__ = ["ValidationIssue", "ValidationReport", "validate_project"]
```

- [ ] **Step 5: eseguire verifiche**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/validation/test_topology.py -v
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src
```

Expected: tutti exit code `0`.

- [ ] **Step 6: commit**

```powershell
git add src/disegnatore_mep/validation tests/validation/test_topology.py
git commit -m "feat: validate multi-domain topology"
```

---

### Task 6: I/O canonico e fingerprint

**Files:**
- Create: `src/disegnatore_mep/io/__init__.py`
- Create: `src/disegnatore_mep/io/project_json.py`
- Create: `src/disegnatore_mep/io/canonical.py`
- Create: `tests/io/test_canonical.py`

**Interfaces:**
- Consumes: `ProjectModel`.
- Produces: `load_project`, `dump_project`, `canonical_json`, `project_fingerprint`.

- [ ] **Step 1: scrivere test di round-trip e stabilità**

Create `tests/io/test_canonical.py`:

```python
from datetime import date
from pathlib import Path

from disegnatore_mep.io.canonical import canonical_json, project_fingerprint
from disegnatore_mep.io.project_json import dump_project, load_project
from disegnatore_mep.model.project import (
    ComponentInstance,
    NetworkModel,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import Domain


def project(component_order: list[str]) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="demo",
            client="Nove C",
            project_name="Demo",
            commission_code="MI-001",
            revision="00",
            issue_date=date(2026, 8, 1),
        ),
        networks=[
            NetworkModel(
                id="heating",
                name="Riscaldamento",
                domain=Domain.HYDRONIC,
                medium="heating_water",
            )
        ],
        components=[
            ComponentInstance(id=item, definition_id="boundary") for item in component_order
        ],
    )


def test_round_trip(tmp_path: Path) -> None:
    source = project(["b", "a"])
    path = tmp_path / "project.json"
    dump_project(source, path)
    assert load_project(path) == source


def test_fingerprint_ignores_collection_order() -> None:
    first = project(["a", "b"])
    second = project(["b", "a"])
    assert canonical_json(first) == canonical_json(second)
    assert project_fingerprint(first) == project_fingerprint(second)
```

- [ ] **Step 2: verificare il fallimento**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/io/test_canonical.py -v
```

Expected: FAIL perché `disegnatore_mep.io` non esiste.

- [ ] **Step 3: implementare I/O e canonicalizzazione**

Create `src/disegnatore_mep/io/project_json.py`:

```python
from pathlib import Path

from disegnatore_mep.model.project import ProjectModel


def load_project(path: Path) -> ProjectModel:
    return ProjectModel.model_validate_json(path.read_text(encoding="utf-8"))


def dump_project(project: ProjectModel, path: Path) -> None:
    path.write_text(project.model_dump_json(indent=2) + "\n", encoding="utf-8")
```

Create `src/disegnatore_mep/io/canonical.py`:

```python
import hashlib
import json
from typing import Any

from disegnatore_mep.model.project import ProjectModel

ORDERED_COLLECTIONS = {
    "subsystems",
    "networks",
    "components",
    "connections",
    "assumptions",
    "rule_applications",
    "sheets",
}


def _normalize(value: Any, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {item_key: _normalize(value[item_key], item_key) for item_key in sorted(value)}
    if isinstance(value, list):
        normalized = [_normalize(item) for item in value]
        if key in ORDERED_COLLECTIONS:
            return sorted(normalized, key=lambda item: item["id"])
        return normalized
    return value


def canonical_json(project: ProjectModel) -> str:
    payload = project.model_dump(mode="json")
    normalized = _normalize(payload)
    return json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def project_fingerprint(project: ProjectModel) -> str:
    return hashlib.sha256(canonical_json(project).encode("utf-8")).hexdigest()
```

Create `src/disegnatore_mep/io/__init__.py`:

```python
from .canonical import canonical_json, project_fingerprint
from .project_json import dump_project, load_project

__all__ = ["canonical_json", "dump_project", "load_project", "project_fingerprint"]
```

- [ ] **Step 4: eseguire verifiche**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/io/test_canonical.py -v
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src
```

Expected: tutti exit code `0`.

- [ ] **Step 5: commit**

```powershell
git add src/disegnatore_mep/io tests/io/test_canonical.py
git commit -m "feat: add canonical project serialization"
```

---

### Task 7: CLI di validazione e schema

**Files:**
- Create: `src/disegnatore_mep/cli.py`
- Create: `src/disegnatore_mep/__main__.py`
- Create: `tests/test_cli.py`

**Interfaces:**
- Consumes: catalogo, I/O, validatore.
- Produces: `main(argv)` e comandi `validate`, `export-schema`, `fingerprint`.

- [ ] **Step 1: scrivere test della CLI**

Create `tests/test_cli.py`:

```python
import json
from pathlib import Path

from disegnatore_mep.cli import main
from disegnatore_mep.model.project import ProjectModel


def test_export_schema(tmp_path: Path) -> None:
    output = tmp_path / "schema.json"
    exit_code = main(["export-schema", str(output)])
    assert exit_code == 0
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["title"] == "ProjectModel"


def test_fingerprint(tmp_path: Path, capsys: object) -> None:
    project = ProjectModel.model_validate(
        {
            "metadata": {
                "project_id": "demo",
                "client": "Nove C",
                "project_name": "Demo",
                "commission_code": "MI-001",
                "revision": "00",
                "issue_date": "2026-08-01",
            }
        }
    )
    path = tmp_path / "project.json"
    path.write_text(project.model_dump_json(), encoding="utf-8")
    exit_code = main(["fingerprint", str(path)])
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert exit_code == 0
    assert len(captured.out.strip()) == 64


def test_validate_load_error_returns_one(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    assert main(["validate", str(missing), "--catalog", str(catalog)]) == 1
```

- [ ] **Step 2: verificare il fallimento**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/test_cli.py -v
```

Expected: FAIL perché `disegnatore_mep.cli` non esiste.

- [ ] **Step 3: implementare la CLI**

Create `src/disegnatore_mep/cli.py`:

```python
import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.io.canonical import project_fingerprint
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.validation.topology import validate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="disegnatore-mep")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("project", type=Path)
    validate.add_argument("--catalog", type=Path, required=True)

    schema = commands.add_parser("export-schema")
    schema.add_argument("output", type=Path)

    fingerprint = commands.add_parser("fingerprint")
    fingerprint.add_argument("project", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "export-schema":
            args.output.write_text(
                json.dumps(ProjectModel.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return 0
        project = load_project(args.project)
        if args.command == "fingerprint":
            print(project_fingerprint(project))
            return 0
        catalog = ComponentRegistry.from_directory(args.catalog)
        report = validate_project(project, catalog)
        print(report.model_dump_json(indent=2))
        return 0 if report.ok else 2
    except (OSError, ValidationError, CatalogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Create `src/disegnatore_mep/__main__.py`:

```python
from .cli import main

raise SystemExit(main())
```

- [ ] **Step 4: tipizzare il fixture `capsys`**

Replace the imports and signature in `tests/test_cli.py` with:

```python
from _pytest.capture import CaptureFixture


def test_fingerprint(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
```

Replace `captured = capsys.readouterr()  # type: ignore[attr-defined]` with:

```python
    captured = capsys.readouterr()
```

- [ ] **Step 5: eseguire verifiche**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/test_cli.py -v
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\python.exe -m mypy src tests
```

Expected: tutti exit code `0`.

- [ ] **Step 6: commit**

```powershell
git add src/disegnatore_mep/cli.py src/disegnatore_mep/__main__.py tests/test_cli.py
git commit -m "feat: add project validation CLI"
```

---

### Task 8: Fixture multi-dominio, schema e gate di accettazione

**Files:**
- Create: `examples/foundation/catalog/boundary-gas-source.json`
- Create: `examples/foundation/catalog/gas-boiler.json`
- Create: `examples/foundation/catalog/boundary-hydronic-return.json`
- Create: `examples/foundation/catalog/boundary-hydronic-supply.json`
- Create: `examples/foundation/catalog/supply-fan.json`
- Create: `examples/foundation/catalog/air-terminal.json`
- Create: `examples/foundation/catalog/vrv-outdoor.json`
- Create: `examples/foundation/catalog/vrv-indoor.json`
- Create: `examples/foundation/valid-mixed-project.json`
- Create: `examples/foundation/invalid-cross-medium.json`
- Create: `examples/foundation/build_fixtures.py`
- Create: `tests/acceptance/test_foundation_cli.py`
- Create: `schemas/project.schema.json`
- Create: `docs/ARCHITECTURE.md`
- Modify: `PROJECT_STATE.md`

**Interfaces:**
- Consumes: CLI e contratti completi di P0.
- Produces: fixture multi-dominio eseguibile, schema JSON versionato e documentazione della fondazione.

- [ ] **Step 1: creare un helper di test che genera il catalogo multi-dominio**

Create `tests/acceptance/test_foundation_cli.py`:

```python
import json
from pathlib import Path

from disegnatore_mep.cli import main


def test_valid_mixed_project_passes() -> None:
    root = Path("examples/foundation")
    assert main(["validate", str(root / "valid-mixed-project.json"), "--catalog", str(root / "catalog")]) == 0


def test_cross_medium_project_fails_with_code_two(capsys: object) -> None:
    root = Path("examples/foundation")
    exit_code = main(
        ["validate", str(root / "invalid-cross-medium.json"), "--catalog", str(root / "catalog")]
    )
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    report = json.loads(captured.out)
    assert exit_code == 2
    assert "PORT_MEDIUM_MISMATCH" in {item["code"] for item in report["issues"]}
```

- [ ] **Step 2: creare catalogo e progetti usando uno script monouso revisionabile**

Create `examples/foundation/build_fixtures.py` with explicit Python dictionaries for the eight component definitions and two projects. The script must:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
CATALOG = ROOT / "catalog"


def geometry() -> dict[str, Any]:
    return {
        "width_mm": 12.0,
        "height_mm": 10.0,
        "clearance_mm": 2.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "inline_gap_mm": None,
    }


def port(
    port_id: str,
    domain: str,
    medium: str,
    flow: str,
    x_mm: float,
    y_mm: float,
) -> dict[str, Any]:
    return {
        "id": port_id,
        "domain": domain,
        "medium": medium,
        "flow": flow,
        "x_mm": x_mm,
        "y_mm": y_mm,
        "angle_deg": 0,
        "required": True,
        "max_connections": 1,
    }


def definition(
    component_id: str,
    name: str,
    functions: list[str],
    ports: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": name,
        "functions": functions,
        "symbol_id": component_id,
        "composite": len(functions) > 1,
        "geometry": geometry(),
        "ports": ports,
        "sources": ["CONV-FOUNDATION"],
    }


DEFINITIONS = [
    definition("boundary-gas-source", "Confine gas", ["boundary"], [port("out", "gas", "natural_gas", "out", 12, 5)]),
    definition(
        "gas-boiler",
        "Caldaia gas",
        ["heat_generation", "gas_combustion"],
        [
            port("gas_in", "gas", "natural_gas", "in", 0, 2),
            port("water_return", "hydronic", "heating_water", "in", 0, 8),
            port("water_supply", "hydronic", "heating_water", "out", 12, 8),
        ],
    ),
    definition("boundary-hydronic-return", "Confine ritorno", ["boundary"], [port("out", "hydronic", "heating_water", "out", 12, 5)]),
    definition("boundary-hydronic-supply", "Confine mandata", ["boundary"], [port("in", "hydronic", "heating_water", "in", 0, 5)]),
    definition("supply-fan", "Ventilatore", ["air_movement"], [port("out", "aeraulic", "supply_air", "out", 12, 5)]),
    definition("air-terminal", "Terminale aria", ["air_terminal"], [port("in", "aeraulic", "supply_air", "in", 0, 5)]),
    definition(
        "vrv-outdoor",
        "Unità esterna VRV",
        ["refrigerant_generation"],
        [
            port("liquid_out", "refrigerant", "refrigerant_liquid", "out", 12, 3),
            port("gas_in", "refrigerant", "refrigerant_gas", "in", 12, 7),
        ],
    ),
    definition(
        "vrv-indoor",
        "Unità interna VRV",
        ["direct_expansion_terminal"],
        [
            port("liquid_in", "refrigerant", "refrigerant_liquid", "in", 0, 3),
            port("gas_out", "refrigerant", "refrigerant_gas", "out", 0, 7),
        ],
    ),
]

COMPONENTS = [
    {"id": "gas-source", "definition_id": "boundary-gas-source", "tag": None, "properties": {}},
    {"id": "boiler", "definition_id": "gas-boiler", "tag": "CAL-01", "properties": {}},
    {"id": "return-boundary", "definition_id": "boundary-hydronic-return", "tag": None, "properties": {}},
    {"id": "supply-boundary", "definition_id": "boundary-hydronic-supply", "tag": None, "properties": {}},
    {"id": "fan", "definition_id": "supply-fan", "tag": "VEN-01", "properties": {}},
    {"id": "terminal", "definition_id": "air-terminal", "tag": "TER-01", "properties": {}},
    {"id": "vrv-outdoor", "definition_id": "vrv-outdoor", "tag": "UE-01", "properties": {}},
    {"id": "vrv-indoor", "definition_id": "vrv-indoor", "tag": "UI-01", "properties": {}},
]

NETWORKS = [
    {"id": "gas", "name": "Gas", "domain": "gas", "medium": "natural_gas"},
    {"id": "heating", "name": "Riscaldamento", "domain": "hydronic", "medium": "heating_water"},
    {"id": "supply-air", "name": "Aria mandata", "domain": "aeraulic", "medium": "supply_air"},
    {"id": "vrv-liquid", "name": "VRV liquido", "domain": "refrigerant", "medium": "refrigerant_liquid"},
    {"id": "vrv-gas", "name": "VRV gas", "domain": "refrigerant", "medium": "refrigerant_gas"},
]

CONNECTIONS = [
    {"id": "gas-1", "network_id": "gas", "endpoint_a": {"component_id": "gas-source", "port_id": "out"}, "endpoint_b": {"component_id": "boiler", "port_id": "gas_in"}, "properties": {}},
    {"id": "heat-return", "network_id": "heating", "endpoint_a": {"component_id": "return-boundary", "port_id": "out"}, "endpoint_b": {"component_id": "boiler", "port_id": "water_return"}, "properties": {}},
    {"id": "heat-supply", "network_id": "heating", "endpoint_a": {"component_id": "boiler", "port_id": "water_supply"}, "endpoint_b": {"component_id": "supply-boundary", "port_id": "in"}, "properties": {}},
    {"id": "air-1", "network_id": "supply-air", "endpoint_a": {"component_id": "fan", "port_id": "out"}, "endpoint_b": {"component_id": "terminal", "port_id": "in"}, "properties": {}},
    {"id": "vrv-liquid-1", "network_id": "vrv-liquid", "endpoint_a": {"component_id": "vrv-outdoor", "port_id": "liquid_out"}, "endpoint_b": {"component_id": "vrv-indoor", "port_id": "liquid_in"}, "properties": {}},
    {"id": "vrv-gas-1", "network_id": "vrv-gas", "endpoint_a": {"component_id": "vrv-indoor", "port_id": "gas_out"}, "endpoint_b": {"component_id": "vrv-outdoor", "port_id": "gas_in"}, "properties": {}},
]


def project(connections: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "project_id": "foundation-mixed",
            "client": "Nove C",
            "project_name": "Foundation mixed-domain fixture",
            "commission_code": "DEV-001",
            "revision": "00",
            "issue_date": "2026-08-01",
        },
        "networks": NETWORKS,
        "components": COMPONENTS,
        "connections": connections,
        "assumptions": [],
        "rule_applications": [],
        "sheets": [],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    CATALOG.mkdir(parents=True, exist_ok=True)
    for item in DEFINITIONS:
        write_json(CATALOG / f"{item['id']}.json", item)
    write_json(ROOT / "valid-mixed-project.json", project(CONNECTIONS))
    invalid_networks = [dict(item) for item in NETWORKS]
    invalid_networks[2] = dict(invalid_networks[2], medium="return_air")
    invalid_project = project(CONNECTIONS)
    invalid_project["networks"] = invalid_networks
    write_json(ROOT / "invalid-cross-medium.json", invalid_project)


if __name__ == "__main__":
    main()
```

Run:

```powershell
& .\.venv\Scripts\python.exe examples/foundation/build_fixtures.py
```

Expected: otto manifesti e due progetti JSON creati.

- [ ] **Step 3: correggere il tipo di `capsys` nel test di accettazione**

Add to the imports in `tests/acceptance/test_foundation_cli.py`:

```python
from _pytest.capture import CaptureFixture
```

Replace the test signature with:

```python
def test_cross_medium_project_fails_with_code_two(
    capsys: CaptureFixture[str],
) -> None:
```

Replace the capture line with:

```python
    captured = capsys.readouterr()
```

- [ ] **Step 4: eseguire il test di accettazione e verificare rosso/verde**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/acceptance/test_foundation_cli.py -v
```

Expected: `2 passed`; il progetto valido restituisce `0`, quello cross-medium restituisce `2`.

- [ ] **Step 5: generare e versionare lo schema JSON**

Run:

```powershell
New-Item -ItemType Directory -Path schemas -Force | Out-Null
& .\.venv\Scripts\python.exe -m disegnatore_mep export-schema schemas/project.schema.json
```

Expected: `schemas/project.schema.json` contiene `"title": "ProjectModel"`.

- [ ] **Step 6: creare l'architettura operativa**

Create `docs/ARCHITECTURE.md` con queste sezioni e contenuti:

````markdown
# Architettura - Disegnatore MEP

## Fonte di verità

Il `ProjectModel` JSON è la fonte tecnica canonica. Elaborati grafici e distinte sono derivati.

## Moduli P0

- `model/`: entità e metadati indipendenti dal dominio.
- `catalog/`: definizioni versionate dei componenti e delle porte.
- `domains/`: compatibilità e validatori specifici per dominio.
- `validation/`: diagnostiche bloccanti e report strutturati.
- `io/`: round-trip JSON, canonicalizzazione e fingerprint.
- `cli.py`: interfaccia stabile per validazione e schema.

## Confini

P0 non interpreta conversazioni, non applica best practice impiantistiche e non disegna. Fornisce i contratti verificati usati dai piani successivi.

## Comandi

```powershell
& .\.venv\Scripts\python.exe -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog
& .\.venv\Scripts\python.exe -m disegnatore_mep fingerprint examples/foundation/valid-mixed-project.json
& .\.venv\Scripts\python.exe -m disegnatore_mep export-schema schemas/project.schema.json
```
````

- [ ] **Step 7: eseguire il gate completo**

Run:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m ruff check src tests examples/foundation/build_fixtures.py
& .\.venv\Scripts\python.exe -m mypy src tests examples/foundation/build_fixtures.py
& .\.venv\Scripts\python.exe -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog
if ($LASTEXITCODE -ne 0) { throw 'Valid mixed project failed' }
& .\.venv\Scripts\python.exe -m disegnatore_mep validate examples/foundation/invalid-cross-medium.json --catalog examples/foundation/catalog
if ($LASTEXITCODE -ne 2) { throw 'Invalid project did not return exit code 2' }
```

Expected: test, lint e type check passano; valido `0`; invalido `2` con `PORT_MEDIUM_MISMATCH`.

- [ ] **Step 8: aggiornare lo stato del progetto**

In `PROJECT_STATE.md`:

- spostare P0 dal `Now` al `Done log` con l'hash del commit;
- impostare `Now` sulla scrittura dei piani P1 e P2;
- lasciare `releases/latest/` non disponibile.

- [ ] **Step 9: commit finale P0**

```powershell
git add examples/foundation schemas/project.schema.json tests/acceptance docs/ARCHITECTURE.md PROJECT_STATE.md
git commit -m "test: qualify multi-domain foundation"
```

## Copertura della specifica

| Area della specifica | Copertura |
|---|---|
| Modello canonico, identificativi stabili e provenienza | Task 2 |
| Catalogo versionato, porte e geometria metrica | Task 3 |
| Nucleo universale e pacchetti di dominio | Task 4 |
| Validazione topologica e diagnostica bloccante | Task 5 |
| Riproducibilità e fingerprint | Task 6 |
| Contratto di automazione per script e skill | Task 7 |
| Composizione idronica-aeraulica-refrigerante-gas | Task 8 |
| Motore delle regole e dossier di approvazione | Piano P1 del master |
| Simboli SVG e sistema grafico A3 | Piano P2 del master |
| Librerie tecniche dei domini | Piani P3A-P3D del master |
| Layout, routing e multi-tavola | Piano P4 del master |
| Cartiglio, SVG, PDF, distinta e preflight | Piano P5 del master |
| Lettura della conversazione e orchestrazione | Piano P6 del master |
| Matrice completa, stampa e release | Piano P7 del master |

## Self-review checklist

- [ ] Ogni requisito di P0 ha almeno un test.
- [ ] Nessuna funzione o fixture contiene un nome di schema tipo come ramo logico.
- [ ] Tutti i modelli rifiutano campi extra.
- [ ] Ogni dominio enumerato possiede un pacchetto registrato.
- [ ] Il progetto misto comprende almeno idronica, aeraulica, refrigerante e gas.
- [ ] L'input valido restituisce `0`; l'errore topologico restituisce `2`; l'errore di caricamento restituisce `1`.
- [ ] Lo schema JSON è rigenerabile senza differenze.
- [ ] Il fingerprint è stabile rispetto all'ordine delle collezioni.
- [ ] `pytest`, Ruff e mypy hanno exit code `0`.
- [ ] `git status --short` è vuoto dopo l'ultimo commit.
