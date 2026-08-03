# Sistema grafico A3 e libreria dei simboli — piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** costruire lo standard grafico in millimetri di carta e la libreria dei simboli, fino a produrre una tavola A3 stampabile e misurabile con il righello che dimostri l'invarianza di scala.

**Architecture:** un modulo di standard grafico definisce, in un solo posto, tutte le grandezze in millimetri. Un manifesto di simbolo descrive la **geometria** — riquadro, porte sul perimetro, area di rispetto, ancoraggi delle etichette — mentre la definizione di componente del catalogo conserva la **semantica** — dominio, fluido, verso, obbligatorietà, molteplicità. Le due si uniscono per identificativo di porta e vengono verificate reciprocamente al caricamento. Un emettitore SVG minimale disegna un simbolo a misura reale e compone un foglio di riscontro A3.

**Tech Stack:** Python 3.12.13, Pydantic 2.13.4, SVG 1.1/2 senza dipendenze esterne, pytest 9.1.1, Ruff 0.15.22, mypy 2.3.0.

---

## Vincoli globali

- I comandi sono Bash e l'interprete e' `.venv/bin/python`, la forma valida in una sessione cloud su Linux. Su Windows in locale il percorso e' invece `.venv/Scripts/python.exe`: `scripts/setup-env.sh` rileva automaticamente quale dei due esiste.
- **Tutte** le grandezze grafiche sono in millimetri di carta e vivono in un unico modulo. Nessun numero magico sparso nel codice.
- Nessun simbolo, nessun testo e nessuno spessore viene ridotto in funzione della complessità dell'impianto.
- Il modello tecnico canonico resta la fonte di verità. Questo piano non produce PDF e non fa layout d'impianto: disegna simboli, non schemi.
- Nessun file contiene una funzione dedicata a uno schema tipo.
- Ogni identificativo segue `^[a-z][a-z0-9_-]*$`; le versioni seguono SemVer.
- Tutti i modelli rifiutano campi sconosciuti.
- `releases/` non viene modificata.
- Ogni task segue red-green-refactor e termina con un commit autonomo.
- **Eseguire sempre la suite completa** e `mypy src tests`, mai il solo file di test del task in corso.

## Decisione strutturale di questo piano

**La geometria si sposta dal catalogo al simbolo.**

In P0 `ComponentDefinition` portava sia la geometria sia la semantica delle porte, e `symbol_id` puntava a una libreria inesistente. Due definizioni che condividessero lo stesso `symbol_id` potevano dichiarare geometrie contraddittorie senza che nulla se ne accorgesse.

Da qui in avanti:

| Vive nel **simbolo** | Vive nella **definizione di componente** |
|---|---|
| larghezza e altezza in mm | dominio della porta |
| posizione delle porte sul perimetro e loro faccia | fluido della porta |
| area di rispetto per lato | verso del flusso |
| ancoraggi di tag e descrizioni | porta obbligatoria si'/no |
| rotazioni ammesse | numero massimo di connessioni |
| interruzione di linea per i componenti in linea | funzioni, versione, fonti |

Si uniscono per identificativo di porta, e il registry verifica al caricamento che gli insiemi coincidano.

**Conseguenza sul vincolo P0 «le porte possono stare ovunque dentro il riquadro».** Quel vincolo riguardava le coordinate su `PortDefinition`, che qui vengono rimosse. Le porte del simbolo stanno **sul perimetro**, con la faccia coerente con il lato su cui si trovano: una porta al centro di un simbolo non è un punto a cui si possa attaccare una tubazione. Il vincolo non viene violato in silenzio, viene ritirato per costruzione e questa è la sua motivazione.

---

## Struttura dei file

```text
src/disegnatore_mep/graphics/
  __init__.py
  standard.py        # tutte le grandezze in mm di carta
  symbol.py          # SymbolManifest, SymbolPort, KeepOut, LabelAnchor, PortFace
  registry.py        # SymbolRegistry, risoluzione simbolo+definizione, verifiche incrociate
  composite.py       # compositi assemblati da primitive e pubblicati come simbolo unico
  svg.py             # emettitore SVG: simbolo singolo e foglio di riscontro A3
assets/symbols/
  <symbol-id>.json   # manifesto
  <symbol-id>.svg    # corpo grafico
tests/graphics/
  test_standard.py
  test_symbol.py
  test_registry.py
  test_composite.py
  test_svg.py
tests/acceptance/
  test_symbol_sheet.py
```

Modificati: `src/disegnatore_mep/catalog/schema.py`, `src/disegnatore_mep/catalog/registry.py`, `src/disegnatore_mep/cli.py`, `examples/foundation/build_fixtures.py`, i test P0 che costruiscono definizioni.

## Contratti pubblici prodotti dal piano

- `GraphicStandard` — grandezze in mm, istanza unica `A3_LANDSCAPE`.
- `PortFace`, `SymbolPort`, `KeepOut`, `LabelAnchor`, `SymbolManifest`.
- `SymbolRegistry.from_directory(path) -> SymbolRegistry`, `.get(symbol_id)`, `.all()`.
- `ResolvedComponent` con `.ports` semantiche e `.symbol` geometrico.
- `ComponentRegistry.from_directory(catalog_dir, symbols) -> ComponentRegistry`.
- `render_symbol(manifest, svg_body) -> str` e `render_symbol_sheet(manifests) -> str`.
- CLI: comando `symbols-sheet`.

---

### Task 1: Standard grafico in millimetri

**Files:**
- Create: `src/disegnatore_mep/graphics/__init__.py`
- Create: `src/disegnatore_mep/graphics/standard.py`
- Create: `tests/graphics/test_standard.py`

**Interfaces:** produce `GraphicStandard` e `A3_LANDSCAPE`.

- [ ] **Step 1: scrivere il test che fallisce**

Create `tests/graphics/test_standard.py`:

```python
import pytest
from pydantic import ValidationError

from disegnatore_mep.graphics.standard import A3_LANDSCAPE, GraphicStandard


def test_a3_landscape_has_iso_dimensions() -> None:
    assert (A3_LANDSCAPE.sheet_width_mm, A3_LANDSCAPE.sheet_height_mm) == (420.0, 297.0)


def test_usable_area_is_derived_from_margins() -> None:
    expected_width = 420.0 - A3_LANDSCAPE.margin_left_mm - A3_LANDSCAPE.margin_right_mm
    expected_height = 297.0 - A3_LANDSCAPE.margin_top_mm - A3_LANDSCAPE.margin_bottom_mm
    assert A3_LANDSCAPE.usable_width_mm == expected_width
    assert A3_LANDSCAPE.usable_height_mm == expected_height


def test_usable_area_is_a_whole_number_of_grid_steps() -> None:
    steps = A3_LANDSCAPE.usable_width_mm / A3_LANDSCAPE.grid_mm
    assert steps == int(steps)


def test_margins_cannot_exceed_the_sheet() -> None:
    with pytest.raises(ValidationError, match="margins leave no usable area"):
        GraphicStandard(
            sheet_width_mm=420,
            sheet_height_mm=297,
            margin_left_mm=250,
            margin_right_mm=250,
            margin_top_mm=10,
            margin_bottom_mm=10,
            grid_mm=2.5,
            line_thin_mm=0.18,
            line_medium_mm=0.35,
            line_thick_mm=0.5,
            text_small_mm=1.8,
            text_normal_mm=2.5,
            text_title_mm=3.5,
            min_clearance_mm=2.0,
        )


def test_line_weights_are_ordered() -> None:
    assert A3_LANDSCAPE.line_thin_mm < A3_LANDSCAPE.line_medium_mm < A3_LANDSCAPE.line_thick_mm


def test_text_heights_are_ordered() -> None:
    assert A3_LANDSCAPE.text_small_mm < A3_LANDSCAPE.text_normal_mm < A3_LANDSCAPE.text_title_mm
```

- [ ] **Step 2: verificare il fallimento**

Run:

```bash
.venv/bin/python -m pytest tests/graphics/test_standard.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.graphics'`.

- [ ] **Step 3: implementare lo standard**

Create `src/disegnatore_mep/graphics/standard.py`:

```python
"""Grandezze grafiche in millimetri di carta.

Unico punto in cui vivono dimensioni, spessori, altezze di testo e distanze.
Nessun altro modulo deve contenere una costante metrica.
"""

from pydantic import Field, model_validator

from disegnatore_mep.model.base import StrictModel


class GraphicStandard(StrictModel):
    sheet_width_mm: float = Field(gt=0)
    sheet_height_mm: float = Field(gt=0)
    margin_left_mm: float = Field(ge=0)
    margin_right_mm: float = Field(ge=0)
    margin_top_mm: float = Field(ge=0)
    margin_bottom_mm: float = Field(ge=0)
    grid_mm: float = Field(gt=0)
    line_thin_mm: float = Field(gt=0)
    line_medium_mm: float = Field(gt=0)
    line_thick_mm: float = Field(gt=0)
    text_small_mm: float = Field(gt=0)
    text_normal_mm: float = Field(gt=0)
    text_title_mm: float = Field(gt=0)
    min_clearance_mm: float = Field(gt=0)

    @property
    def usable_width_mm(self) -> float:
        return self.sheet_width_mm - self.margin_left_mm - self.margin_right_mm

    @property
    def usable_height_mm(self) -> float:
        return self.sheet_height_mm - self.margin_top_mm - self.margin_bottom_mm

    @model_validator(mode="after")
    def geometry_is_coherent(self) -> "GraphicStandard":
        if self.usable_width_mm <= 0 or self.usable_height_mm <= 0:
            raise ValueError("margins leave no usable area")
        if not self.line_thin_mm < self.line_medium_mm < self.line_thick_mm:
            raise ValueError("line weights must increase from thin to thick")
        if not self.text_small_mm < self.text_normal_mm < self.text_title_mm:
            raise ValueError("text heights must increase from small to title")
        return self


A3_LANDSCAPE = GraphicStandard(
    sheet_width_mm=420.0,
    sheet_height_mm=297.0,
    margin_left_mm=20.0,
    margin_right_mm=10.0,
    margin_top_mm=10.0,
    margin_bottom_mm=10.0,
    grid_mm=2.5,
    line_thin_mm=0.18,
    line_medium_mm=0.35,
    line_thick_mm=0.50,
    text_small_mm=1.8,
    text_normal_mm=2.5,
    text_title_mm=3.5,
    min_clearance_mm=2.0,
)
```

Create `src/disegnatore_mep/graphics/__init__.py`:

```python
from .standard import A3_LANDSCAPE, GraphicStandard

__all__ = ["A3_LANDSCAPE", "GraphicStandard"]
```

Nota sul margine sinistro maggiore: è lo spazio di rilegatura previsto da ISO 5457.

- [ ] **Step 4: verificare**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src tests
```

Expected: tutti exit `0`; il totale sale da 59 a 65.

- [ ] **Step 5: commit**

```bash
git add src/disegnatore_mep/graphics tests/graphics/test_standard.py
git commit -m "feat: add the millimetre graphic standard"
```

---

### Task 2: Manifesto del simbolo

**Files:**
- Create: `src/disegnatore_mep/graphics/symbol.py`
- Create: `tests/graphics/test_symbol.py`
- Modify: `src/disegnatore_mep/graphics/__init__.py`

**Interfaces:** produce `PortFace`, `SymbolPort`, `KeepOut`, `LabelAnchor`, `SymbolManifest`.

- [ ] **Step 1: scrivere i test che falliscono**

Create `tests/graphics/test_symbol.py`:

```python
import pytest
from pydantic import ValidationError

from disegnatore_mep.graphics.symbol import (
    KeepOut,
    LabelAnchor,
    PortFace,
    SymbolManifest,
    SymbolPort,
)


def manifest(**overrides: object) -> SymbolManifest:
    payload: dict[str, object] = {
        "id": "valve-isolation",
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "width_mm": 6.0,
        "height_mm": 6.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "inline_gap_mm": 6.0,
        "ports": [
            {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
            {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
        ],
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 1.0, "bottom_mm": 1.0},
        "label_anchors": [{"id": "tag", "role": "tag", "x_mm": 3.0, "y_mm": -1.0}],
        "source": "CONV-GRAFICA-001",
    }
    payload.update(overrides)
    return SymbolManifest.model_validate(payload)


def test_manifest_accepts_ports_on_the_perimeter() -> None:
    assert manifest().port("a").outward_angle_deg == 180


def test_outward_angle_is_derived_from_the_face() -> None:
    assert PortFace.RIGHT.outward_angle_deg == 0
    assert PortFace.BOTTOM.outward_angle_deg == 90
    assert PortFace.LEFT.outward_angle_deg == 180
    assert PortFace.TOP.outward_angle_deg == 270


def test_port_off_its_declared_face_is_rejected() -> None:
    with pytest.raises(ValidationError, match="port a is not on its left face"):
        manifest(ports=[{"id": "a", "face": "left", "x_mm": 3.0, "y_mm": 3.0}])


def test_port_in_the_interior_is_rejected() -> None:
    with pytest.raises(ValidationError, match="port a is not on its top face"):
        manifest(ports=[{"id": "a", "face": "top", "x_mm": 3.0, "y_mm": 3.0}])


def test_port_outside_the_box_is_rejected() -> None:
    with pytest.raises(ValidationError, match="port a falls outside the symbol box"):
        manifest(ports=[{"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 99.0}])


def test_duplicate_port_ids_are_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate port id: a"):
        manifest(
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "a", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
            ]
        )


def test_inline_symbol_needs_two_opposed_ports() -> None:
    with pytest.raises(ValidationError, match="an inline symbol needs two opposed ports"):
        manifest(
            inline_gap_mm=6.0,
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "top", "x_mm": 3.0, "y_mm": 0.0},
            ],
        )


def test_non_inline_symbol_may_have_any_arrangement() -> None:
    assert (
        manifest(
            inline_gap_mm=None,
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "top", "x_mm": 3.0, "y_mm": 0.0},
            ],
        ).inline_gap_mm
        is None
    )


def test_inline_gap_cannot_exceed_the_symbol_width() -> None:
    with pytest.raises(ValidationError, match="inline gap cannot exceed the symbol width"):
        manifest(inline_gap_mm=99.0)


def test_duplicate_label_anchor_ids_are_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate label anchor id: tag"):
        manifest(
            label_anchors=[
                {"id": "tag", "role": "tag", "x_mm": 3.0, "y_mm": -1.0},
                {"id": "tag", "role": "description", "x_mm": 3.0, "y_mm": 8.0},
            ]
        )


def test_keep_out_defaults_to_zero() -> None:
    assert KeepOut().left_mm == 0.0


def test_label_anchor_may_sit_outside_the_box() -> None:
    anchor = LabelAnchor(id="tag", role="tag", x_mm=3.0, y_mm=-1.0)
    assert anchor.y_mm == -1.0


def test_symbol_port_is_immutable() -> None:
    port = SymbolPort(id="a", face=PortFace.LEFT, x_mm=0.0, y_mm=3.0)
    with pytest.raises(ValidationError):
        port.x_mm = 1.0
```

- [ ] **Step 2: verificare il fallimento**

Run:

```bash
.venv/bin/python -m pytest tests/graphics/test_symbol.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.graphics.symbol'`.

- [ ] **Step 3: implementare il manifesto**

Create `src/disegnatore_mep/graphics/symbol.py`:

```python
"""Manifesto geometrico di un simbolo.

Il simbolo descrive come il componente è disegnato: riquadro, porte sul
perimetro, area di rispetto e ancoraggi delle etichette. La semantica delle
porte — dominio, fluido, verso, obbligatorietà — vive nella definizione di
componente del catalogo e si unisce a questa per identificativo di porta.
"""

from enum import StrEnum
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel

TOLERANCE_MM = 1e-6


class PortFace(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

    @property
    def outward_angle_deg(self) -> int:
        """Direzione uscente in gradi, con y crescente verso il basso come in SVG."""
        return {
            PortFace.RIGHT: 0,
            PortFace.BOTTOM: 90,
            PortFace.LEFT: 180,
            PortFace.TOP: 270,
        }[self]

    @property
    def opposite(self) -> "PortFace":
        return {
            PortFace.LEFT: PortFace.RIGHT,
            PortFace.RIGHT: PortFace.LEFT,
            PortFace.TOP: PortFace.BOTTOM,
            PortFace.BOTTOM: PortFace.TOP,
        }[self]


class SymbolPort(StrictModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    id: str = Field(pattern=ID_PATTERN)
    face: PortFace
    x_mm: float
    y_mm: float

    @property
    def outward_angle_deg(self) -> int:
        return self.face.outward_angle_deg


class KeepOut(StrictModel):
    """Area di rispetto, per lato: nulla puo' essere disposto dentro questi margini."""

    left_mm: float = Field(default=0.0, ge=0)
    right_mm: float = Field(default=0.0, ge=0)
    top_mm: float = Field(default=0.0, ge=0)
    bottom_mm: float = Field(default=0.0, ge=0)


class LabelAnchor(StrictModel):
    """Punto preferito per un tag o una descrizione, anche fuori dal riquadro."""

    id: str = Field(pattern=ID_PATTERN)
    role: Literal["tag", "description", "data"]
    x_mm: float
    y_mm: float


class SymbolManifest(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    allowed_rotations_deg: list[int] = Field(min_length=1)
    inline_gap_mm: float | None = Field(default=None, gt=0)
    ports: list[SymbolPort] = Field(min_length=1)
    keep_out: KeepOut = Field(default_factory=KeepOut)
    label_anchors: list[LabelAnchor] = Field(default_factory=list)
    source: str = Field(min_length=1)

    def port(self, port_id: str) -> SymbolPort:
        for item in self.ports:
            if item.id == port_id:
                return item
        raise KeyError(f"unknown symbol port: {port_id}")

    @property
    def port_ids(self) -> frozenset[str]:
        return frozenset(item.id for item in self.ports)

    @property
    def is_inline(self) -> bool:
        return self.inline_gap_mm is not None

    def _face_coordinate(self, port: SymbolPort) -> tuple[float, float]:
        expected = {
            PortFace.LEFT: (0.0, port.y_mm),
            PortFace.RIGHT: (self.width_mm, port.y_mm),
            PortFace.TOP: (port.x_mm, 0.0),
            PortFace.BOTTOM: (port.x_mm, self.height_mm),
        }[port.face]
        return expected

    @model_validator(mode="after")
    def geometry_is_coherent(self) -> "SymbolManifest":
        allowed = {0, 90, 180, 270}
        if not set(self.allowed_rotations_deg).issubset(allowed):
            raise ValueError("allowed rotations must be 0, 90, 180 or 270")
        if len(self.allowed_rotations_deg) != len(set(self.allowed_rotations_deg)):
            raise ValueError("duplicate allowed rotation")

        seen: set[str] = set()
        for port in self.ports:
            if port.id in seen:
                raise ValueError(f"duplicate port id: {port.id}")
            seen.add(port.id)
            if not (
                -TOLERANCE_MM <= port.x_mm <= self.width_mm + TOLERANCE_MM
                and -TOLERANCE_MM <= port.y_mm <= self.height_mm + TOLERANCE_MM
            ):
                raise ValueError(f"port {port.id} falls outside the symbol box")
            expected_x, expected_y = self._face_coordinate(port)
            if (
                abs(port.x_mm - expected_x) > TOLERANCE_MM
                or abs(port.y_mm - expected_y) > TOLERANCE_MM
            ):
                raise ValueError(f"port {port.id} is not on its {port.face.value} face")

        anchors: set[str] = set()
        for anchor in self.label_anchors:
            if anchor.id in anchors:
                raise ValueError(f"duplicate label anchor id: {anchor.id}")
            anchors.add(anchor.id)

        if self.inline_gap_mm is not None:
            if self.inline_gap_mm > self.width_mm + TOLERANCE_MM:
                raise ValueError("inline gap cannot exceed the symbol width")
            faces = {port.face for port in self.ports}
            opposed = any(face.opposite in faces for face in faces)
            if len(self.ports) != 2 or not opposed:
                raise ValueError("an inline symbol needs two opposed ports")
        return self
```

Nota sull'ordine dei controlli: la verifica del riquadro precede quella della faccia, cosi' una porta palesemente fuori riceve il messaggio piu' utile.

Replace `src/disegnatore_mep/graphics/__init__.py` with:

```python
from .standard import A3_LANDSCAPE, GraphicStandard
from .symbol import KeepOut, LabelAnchor, PortFace, SymbolManifest, SymbolPort

__all__ = [
    "A3_LANDSCAPE",
    "GraphicStandard",
    "KeepOut",
    "LabelAnchor",
    "PortFace",
    "SymbolManifest",
    "SymbolPort",
]
```

- [ ] **Step 4: verificare**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src tests
```

Expected: tutti exit `0`.

- [ ] **Step 5: commit**

```bash
git add src/disegnatore_mep/graphics tests/graphics/test_symbol.py
git commit -m "feat: add the symbol geometry manifest"
```

---

### Task 3: Registro dei simboli e verifica incrociata con il catalogo

**Files:**
- Create: `src/disegnatore_mep/graphics/registry.py`
- Create: `tests/graphics/test_registry.py`
- Modify: `src/disegnatore_mep/catalog/schema.py`
- Modify: `src/disegnatore_mep/catalog/registry.py`
- Modify: `tests/catalog/test_registry.py`, `tests/catalog/test_schema.py`, `tests/validation/test_topology.py`

**Interfaces:** produce `SymbolRegistry`, `SymbolError`, `ResolvedComponent`; `ComponentRegistry.from_directory(catalog_dir, symbols)`.

- [ ] **Step 1: scrivere i test che falliscono**

Create `tests/graphics/test_registry.py`:

```python
import json
from pathlib import Path

import pytest

from disegnatore_mep.graphics.registry import SymbolError, SymbolRegistry


def manifest_payload(symbol_id: str) -> dict[str, object]:
    return {
        "id": symbol_id,
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "width_mm": 6.0,
        "height_mm": 6.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "inline_gap_mm": 6.0,
        "ports": [
            {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
            {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
        ],
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 1.0, "bottom_mm": 1.0},
        "label_anchors": [{"id": "tag", "role": "tag", "x_mm": 3.0, "y_mm": -1.0}],
        "source": "CONV-GRAFICA-001",
    }


SVG_BODY = '<g><line x1="0" y1="3" x2="6" y2="3"/></g>'


def write_symbol(directory: Path, symbol_id: str, body: str = SVG_BODY) -> None:
    (directory / f"{symbol_id}.json").write_text(
        json.dumps(manifest_payload(symbol_id)), encoding="utf-8"
    )
    (directory / f"{symbol_id}.svg").write_text(body, encoding="utf-8")


def test_registry_loads_a_symbol(tmp_path: Path) -> None:
    write_symbol(tmp_path, "valve-isolation")
    registry = SymbolRegistry.from_directory(tmp_path)
    assert registry.get("valve-isolation").manifest.width_mm == 6.0
    assert "line" in registry.get("valve-isolation").body


def test_missing_directory_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SymbolError, match="symbol directory not found"):
        SymbolRegistry.from_directory(tmp_path / "nope")


def test_manifest_without_body_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "valve-isolation.json").write_text(
        json.dumps(manifest_payload("valve-isolation")), encoding="utf-8"
    )
    with pytest.raises(SymbolError, match="missing svg body for valve-isolation"):
        SymbolRegistry.from_directory(tmp_path)


def test_filename_must_match_the_manifest_id(tmp_path: Path) -> None:
    (tmp_path / "wrong-name.json").write_text(
        json.dumps(manifest_payload("valve-isolation")), encoding="utf-8"
    )
    (tmp_path / "wrong-name.svg").write_text(SVG_BODY, encoding="utf-8")
    with pytest.raises(SymbolError, match="file name does not match symbol id"):
        SymbolRegistry.from_directory(tmp_path)


def test_body_carrying_its_own_svg_root_is_rejected(tmp_path: Path) -> None:
    write_symbol(tmp_path, "valve-isolation", body="<svg><g/></svg>")
    with pytest.raises(SymbolError, match="svg body must not contain an <svg> root"):
        SymbolRegistry.from_directory(tmp_path)


def test_unknown_symbol_lookup_is_rejected(tmp_path: Path) -> None:
    write_symbol(tmp_path, "valve-isolation")
    registry = SymbolRegistry.from_directory(tmp_path)
    with pytest.raises(SymbolError, match="unknown symbol: nope"):
        registry.get("nope")


def test_all_is_ordered_by_id(tmp_path: Path) -> None:
    write_symbol(tmp_path, "zzz-valve")
    write_symbol(tmp_path, "aaa-valve")
    registry = SymbolRegistry.from_directory(tmp_path)
    assert [item.manifest.id for item in registry.all()] == ["aaa-valve", "zzz-valve"]
```

Append to `tests/catalog/test_registry.py` a cross-check test. First replace the module's `definition` helper so it no longer carries geometry, and add a symbol fixture:

```python
def definition(component_id: str, ports: list[str] | None = None) -> dict[str, object]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "symbol_id": "valve-isolation",
        "composite": False,
        "ports": [
            {
                "id": port_id,
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "bidirectional",
                "required": True,
                "max_connections": 1,
            }
            for port_id in (ports or ["a", "b"])
        ],
        "sources": ["CONV-001"],
    }
```

and add:

```python
def test_registry_rejects_ports_the_symbol_does_not_have(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "catalog"
    symbol_dir = tmp_path / "symbols"
    catalog_dir.mkdir()
    symbol_dir.mkdir()
    write_symbol(symbol_dir, "valve-isolation")
    (catalog_dir / "valve.json").write_text(
        json.dumps(definition("isolation-valve", ports=["a", "c"])), encoding="utf-8"
    )
    with pytest.raises(CatalogError, match="port ids do not match symbol valve-isolation"):
        ComponentRegistry.from_directory(
            catalog_dir, symbols=SymbolRegistry.from_directory(symbol_dir)
        )
```

Import `SymbolRegistry` and reuse `write_symbol` from `tests.graphics.test_registry` by duplicating the two helpers locally — pytest uses importlib import mode and the test packages are not importable from one another.

- [ ] **Step 2: verificare il fallimento**

Run:

```bash
.venv/bin/python -m pytest tests/graphics/test_registry.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.graphics.registry'`.

- [ ] **Step 3: implementare il registro dei simboli**

Create `src/disegnatore_mep/graphics/registry.py`:

```python
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .symbol import SymbolManifest


class SymbolError(ValueError):
    pass


@dataclass(frozen=True)
class Symbol:
    """Un simbolo pubblicato: manifesto geometrico piu' corpo grafico SVG."""

    manifest: SymbolManifest
    body: str


class SymbolRegistry:
    def __init__(self, symbols: list[Symbol]) -> None:
        self._symbols: dict[str, Symbol] = {}
        for symbol in symbols:
            if symbol.manifest.id in self._symbols:
                raise SymbolError(f"duplicate symbol: {symbol.manifest.id}")
            self._symbols[symbol.manifest.id] = symbol

    @classmethod
    def from_directory(cls, directory: Path) -> "SymbolRegistry":
        if not directory.is_dir():
            raise SymbolError(f"symbol directory not found: {directory}")
        symbols: list[Symbol] = []
        for path in sorted(directory.glob("*.json")):
            try:
                manifest = SymbolManifest.model_validate_json(path.read_text("utf-8"))
            except (OSError, ValidationError, ValueError) as exc:
                raise SymbolError(f"invalid symbol manifest {path}: {exc}") from exc
            if manifest.id != path.stem:
                raise SymbolError(f"file name does not match symbol id: {path}")
            body_path = path.with_suffix(".svg")
            if not body_path.is_file():
                raise SymbolError(f"missing svg body for {manifest.id}")
            body = body_path.read_text("utf-8").strip()
            if "<svg" in body:
                raise SymbolError(
                    f"svg body must not contain an <svg> root: {body_path}"
                )
            symbols.append(Symbol(manifest=manifest, body=body))
        return cls(symbols)

    def get(self, symbol_id: str) -> Symbol:
        try:
            return self._symbols[symbol_id]
        except KeyError as exc:
            raise SymbolError(f"unknown symbol: {symbol_id}") from exc

    def contains(self, symbol_id: str) -> bool:
        return symbol_id in self._symbols

    def all(self) -> tuple[Symbol, ...]:
        return tuple(self._symbols[key] for key in sorted(self._symbols))
```

Il corpo SVG non deve contenere una radice `<svg>` perché viene inserito dentro un gruppo del foglio, con la propria trasformazione di posizionamento.

- [ ] **Step 4: alleggerire il catalogo**

In `src/disegnatore_mep/catalog/schema.py` rimuovere `SymbolGeometry` e i campi geometrici di `PortDefinition`, lasciando la sola semantica:

```python
from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel
from disegnatore_mep.model.types import Domain, PortFlow


class PortDefinition(StrictModel):
    """Semantica di una porta. La geometria vive nel manifesto del simbolo."""

    id: str = Field(pattern=ID_PATTERN)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    flow: PortFlow
    required: bool = True
    max_connections: int = Field(default=1, ge=1)


class ComponentDefinition(StrictModel):
    """Voce di catalogo versionata che descrive un componente e le sue porte.

    Gli identificativi di catalogo sono uno spazio di nomi distinto da quelli
    di progetto portati da `IdentifiedModel`, quindi questo modello dichiara
    un proprio `id` invece di ereditare quella base.
    """

    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    functions: list[str] = Field(min_length=1)
    symbol_id: str = Field(pattern=ID_PATTERN)
    composite: bool = False
    ports: list[PortDefinition] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)

    @property
    def port_ids(self) -> frozenset[str]:
        return frozenset(port.id for port in self.ports)

    @model_validator(mode="after")
    def port_ids_are_unique(self) -> "ComponentDefinition":
        ids = [port.id for port in self.ports]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate port id")
        return self
```

In `src/disegnatore_mep/catalog/registry.py` aggiungere la risoluzione e la verifica incrociata:

```python
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.graphics.registry import SymbolRegistry

from .schema import ComponentDefinition


class CatalogError(ValueError):
    pass


class ComponentRegistry:
    def __init__(
        self,
        definitions: list[ComponentDefinition],
        symbols: SymbolRegistry | None = None,
    ) -> None:
        self._definitions: dict[str, ComponentDefinition] = {}
        self._symbols = symbols
        for definition in definitions:
            if definition.id in self._definitions:
                raise CatalogError(f"duplicate component definition: {definition.id}")
            if symbols is not None:
                self._check_symbol(definition, symbols)
            self._definitions[definition.id] = definition

    @staticmethod
    def _check_symbol(definition: ComponentDefinition, symbols: SymbolRegistry) -> None:
        if not symbols.contains(definition.symbol_id):
            raise CatalogError(
                f"unknown symbol {definition.symbol_id} for {definition.id}"
            )
        manifest = symbols.get(definition.symbol_id).manifest
        if definition.port_ids != manifest.port_ids:
            raise CatalogError(
                f"port ids do not match symbol {definition.symbol_id} "
                f"for {definition.id}: {sorted(definition.port_ids)} "
                f"vs {sorted(manifest.port_ids)}"
            )

    @classmethod
    def from_directory(
        cls, directory: Path, symbols: SymbolRegistry | None = None
    ) -> "ComponentRegistry":
        if not directory.is_dir():
            raise CatalogError(f"catalog directory not found: {directory}")
        definitions: list[ComponentDefinition] = []
        for path in sorted(directory.glob("*.json")):
            try:
                definitions.append(
                    ComponentDefinition.model_validate_json(path.read_text("utf-8"))
                )
            except (OSError, ValidationError, ValueError) as exc:
                raise CatalogError(f"invalid catalog file {path}: {exc}") from exc
        # Duplicate detection stays outside the loop: CatalogError subclasses
        # ValueError, so raising it inside would be re-wrapped by the except above.
        return cls(definitions, symbols)

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

`symbols` è opzionale perché il validatore topologico continua a funzionare sulla sola semantica; la verifica incrociata scatta quando la libreria è disponibile.

- [ ] **Step 5: adattare i test P0 che costruivano la geometria**

In `tests/validation/test_topology.py` la funzione `component_definition` non deve piu' costruire `SymbolGeometry`. Sostituirla con:

```python
def component_definition(component_id: str, flow: PortFlow) -> ComponentDefinition:
    return ComponentDefinition(
        id=component_id,
        version="1.0.0",
        name=component_id,
        functions=["boundary"],
        symbol_id=component_id,
        composite=False,
        ports=[
            PortDefinition(
                id="port",
                domain=Domain.HYDRONIC,
                medium="heating_water",
                flow=flow,
            )
        ],
        sources=["CONV-001"],
    )
```

Rimuovere l'import di `SymbolGeometry`. In `tests/catalog/test_schema.py` eliminare i test che riguardavano rotazioni e porte fuori riquadro — quelle verifiche vivono ora in `tests/graphics/test_symbol.py` e sono coperte li' — mantenendo il solo test sugli identificativi di porta duplicati.

- [ ] **Step 6: verificare**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src tests
```

Expected: tutti exit `0`. Il conteggio cala per i test rimossi dal catalogo e sale per quelli nuovi: riportare il totale reale.

- [ ] **Step 7: commit**

```bash
git add src/disegnatore_mep/graphics src/disegnatore_mep/catalog tests
git commit -m "feat: own symbol geometry in the symbol manifest"
```

---

### Task 4: Simboli compositi

**Files:**
- Create: `src/disegnatore_mep/graphics/composite.py`
- Create: `tests/graphics/test_composite.py`

**Interfaces:** produce `CompositeSpec`, `CompositePart`, `compile_composite`.

- [ ] **Step 1: scrivere i test che falliscono**

Create `tests/graphics/test_composite.py`:

```python
import pytest

from disegnatore_mep.graphics.composite import CompositePart, CompositeSpec, compile_composite
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.symbol import SymbolManifest


def primitive(symbol_id: str) -> Symbol:
    manifest = SymbolManifest.model_validate(
        {
            "id": symbol_id,
            "version": "1.0.0",
            "name": symbol_id,
            "width_mm": 6.0,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "inline_gap_mm": 6.0,
            "ports": [
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
            ],
            "source": "CONV-GRAFICA-001",
        }
    )
    return Symbol(manifest=manifest, body=f'<g id="{symbol_id}"/>')


def registry() -> SymbolRegistry:
    return SymbolRegistry([primitive("valve"), primitive("filter")])


def spec(**overrides: object) -> CompositeSpec:
    payload: dict[str, object] = {
        "id": "filling-group",
        "version": "1.0.0",
        "name": "Gruppo di riempimento",
        "width_mm": 16.0,
        "height_mm": 6.0,
        "allowed_rotations_deg": [0, 180],
        "source": "CONV-GRAFICA-002",
        "parts": [
            {"symbol_id": "valve", "offset_x_mm": 0.0, "offset_y_mm": 0.0},
            {"symbol_id": "filter", "offset_x_mm": 10.0, "offset_y_mm": 0.0},
        ],
        "exposed_ports": [
            {"part_index": 0, "port_id": "a", "as_id": "inlet"},
            {"part_index": 1, "port_id": "b", "as_id": "outlet"},
        ],
    }
    payload.update(overrides)
    return CompositeSpec.model_validate(payload)


def test_compiled_composite_is_a_single_symbol() -> None:
    symbol = compile_composite(spec(), registry())
    assert symbol.manifest.id == "filling-group"
    assert sorted(symbol.manifest.port_ids) == ["inlet", "outlet"]


def test_exposed_ports_carry_the_translated_position() -> None:
    symbol = compile_composite(spec(), registry())
    assert symbol.manifest.port("outlet").x_mm == 16.0
    assert symbol.manifest.port("inlet").x_mm == 0.0


def test_body_nests_each_part_with_its_offset() -> None:
    body = compile_composite(spec(), registry()).body
    assert 'translate(10.0 0.0)' in body
    assert body.count("<g") >= 2


def test_part_falling_outside_the_composite_box_is_rejected() -> None:
    with pytest.raises(ValueError, match="part 1 falls outside the composite box"):
        compile_composite(spec(width_mm=8.0), registry())


def test_unknown_primitive_is_rejected() -> None:
    invalid = spec(parts=[{"symbol_id": "nope", "offset_x_mm": 0.0, "offset_y_mm": 0.0}],
                   exposed_ports=[{"part_index": 0, "port_id": "a", "as_id": "inlet"}])
    with pytest.raises(ValueError, match="unknown symbol: nope"):
        compile_composite(invalid, registry())
```

- [ ] **Step 2: verificare il fallimento**

Run:

```bash
.venv/bin/python -m pytest tests/graphics/test_composite.py -v
```

Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: implementare il compilatore**

Create `src/disegnatore_mep/graphics/composite.py`:

```python
"""Compositi assemblati da primitive e pubblicati come simbolo unico.

Un prodotto che integra piu' funzioni viene mostrato come un solo simbolo
riconoscibile e conta una sola volta nella distinta. Internamente puo' essere
costruito da primitive riusabili, ma cio' non è visibile all'utilizzatore.
"""

from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel

from .registry import Symbol, SymbolRegistry
from .symbol import SymbolManifest, SymbolPort


class CompositePart(StrictModel):
    symbol_id: str = Field(pattern=ID_PATTERN)
    offset_x_mm: float = Field(ge=0)
    offset_y_mm: float = Field(ge=0)


class ExposedPort(StrictModel):
    part_index: int = Field(ge=0)
    port_id: str = Field(pattern=ID_PATTERN)
    as_id: str = Field(pattern=ID_PATTERN)


class CompositeSpec(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    allowed_rotations_deg: list[int] = Field(min_length=1)
    source: str = Field(min_length=1)
    parts: list[CompositePart] = Field(min_length=1)
    exposed_ports: list[ExposedPort] = Field(min_length=1)

    @model_validator(mode="after")
    def exposed_ports_are_unique(self) -> "CompositeSpec":
        ids = [item.as_id for item in self.exposed_ports]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate exposed port id")
        for item in self.exposed_ports:
            if item.part_index >= len(self.parts):
                raise ValueError(f"exposed port {item.as_id} refers to a missing part")
        return self


def compile_composite(spec: CompositeSpec, symbols: SymbolRegistry) -> Symbol:
    resolved = [symbols.get(part.symbol_id) for part in spec.parts]

    for index, (part, source) in enumerate(zip(spec.parts, resolved, strict=True)):
        if (
            part.offset_x_mm + source.manifest.width_mm > spec.width_mm
            or part.offset_y_mm + source.manifest.height_mm > spec.height_mm
        ):
            raise ValueError(f"part {index} falls outside the composite box")

    ports: list[SymbolPort] = []
    for exposed in spec.exposed_ports:
        part = spec.parts[exposed.part_index]
        origin = resolved[exposed.part_index].manifest.port(exposed.port_id)
        ports.append(
            SymbolPort(
                id=exposed.as_id,
                face=origin.face,
                x_mm=origin.x_mm + part.offset_x_mm,
                y_mm=origin.y_mm + part.offset_y_mm,
            )
        )

    manifest = SymbolManifest(
        id=spec.id,
        version=spec.version,
        name=spec.name,
        width_mm=spec.width_mm,
        height_mm=spec.height_mm,
        allowed_rotations_deg=spec.allowed_rotations_deg,
        ports=ports,
        source=spec.source,
    )

    fragments = [
        f'<g transform="translate({part.offset_x_mm} {part.offset_y_mm})">{source.body}</g>'
        for part, source in zip(spec.parts, resolved, strict=True)
    ]
    return Symbol(manifest=manifest, body="".join(fragments))
```

Una porta esposta conserva la faccia della primitiva: la traslazione la sposta ma non la ruota. Il costruttore di `SymbolManifest` rivaliderà comunque il vincolo perimetro-faccia, quindi un composito mal costruito viene respinto qui.

- [ ] **Step 4: verificare e committare**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src tests
git add src/disegnatore_mep/graphics/composite.py tests/graphics/test_composite.py
git commit -m "feat: compile composite symbols from primitives"
```

---

### Task 5: Emettitore SVG a misura reale

**Files:**
- Create: `src/disegnatore_mep/graphics/svg.py`
- Create: `tests/graphics/test_svg.py`
- Modify: `src/disegnatore_mep/graphics/__init__.py`

**Interfaces:** produce `render_symbol_sheet(symbols, standard) -> str`.

- [ ] **Step 1: scrivere i test che falliscono**

Create `tests/graphics/test_svg.py`:

```python
import re

from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.svg import render_symbol_sheet
from disegnatore_mep.graphics.symbol import SymbolManifest


def symbol(symbol_id: str) -> Symbol:
    manifest = SymbolManifest.model_validate(
        {
            "id": symbol_id,
            "version": "1.0.0",
            "name": f"Simbolo {symbol_id}",
            "width_mm": 6.0,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "inline_gap_mm": 6.0,
            "ports": [
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
            ],
            "source": "CONV-GRAFICA-001",
        }
    )
    return Symbol(manifest=manifest, body='<line x1="0" y1="3" x2="6" y2="3"/>')


def sheet() -> str:
    return render_symbol_sheet(SymbolRegistry([symbol("valve"), symbol("pump")]))


def test_sheet_declares_physical_millimetres() -> None:
    output = sheet()
    assert 'width="420mm"' in output
    assert 'height="297mm"' in output


def test_viewbox_maps_one_unit_to_one_millimetre() -> None:
    assert 'viewBox="0 0 420 297"' in sheet()


def test_sheet_contains_a_hundred_millimetre_scale_bar() -> None:
    output = sheet()
    assert 'id="scale-bar"' in output
    assert "100 mm" in output


def test_every_symbol_is_placed_once() -> None:
    output = sheet()
    assert output.count('class="symbol"') == 2
    assert 'data-symbol-id="valve"' in output
    assert 'data-symbol-id="pump"' in output


def test_symbol_bodies_are_nested_under_a_translation() -> None:
    assert re.search(r'<g class="symbol"[^>]*transform="translate\([\d.]+ [\d.]+\)"', sheet())


def test_port_markers_are_emitted_at_their_millimetre_position() -> None:
    assert 'class="port"' in sheet()


def test_sheet_is_deterministic() -> None:
    assert sheet() == sheet()


def test_sheet_is_well_formed_xml() -> None:
    from xml.etree import ElementTree

    ElementTree.fromstring(sheet())


def test_nothing_is_drawn_outside_the_usable_area() -> None:
    output = sheet()
    xs = [float(value) for value in re.findall(r'translate\(([\d.]+) [\d.]+\)', output)]
    assert min(xs) >= A3_LANDSCAPE.margin_left_mm
    assert max(xs) <= A3_LANDSCAPE.margin_left_mm + A3_LANDSCAPE.usable_width_mm
```

- [ ] **Step 2: verificare il fallimento**

Run:

```bash
.venv/bin/python -m pytest tests/graphics/test_svg.py -v
```

Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: implementare l'emettitore**

Create `src/disegnatore_mep/graphics/svg.py`:

```python
"""Emettitore SVG a misura reale.

Il foglio dichiara larghezza e altezza in millimetri e un `viewBox` numerico
identico, cosi' che una unita' utente corrisponda esattamente a un millimetro
di carta. Stampando senza adattamento, il righello deve confermare la barra di
scala.
"""

from .registry import SymbolRegistry
from .standard import A3_LANDSCAPE, GraphicStandard

SCALE_BAR_MM = 100.0
COLUMN_GAP_MM = 10.0
ROW_GAP_MM = 14.0


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _scale_bar(standard: GraphicStandard) -> str:
    x = standard.margin_left_mm
    y = standard.sheet_height_mm - standard.margin_bottom_mm
    return (
        f'<g id="scale-bar" stroke="black" stroke-width="{standard.line_medium_mm}">'
        f'<line x1="{x}" y1="{y}" x2="{x + SCALE_BAR_MM}" y2="{y}"/>'
        f'<line x1="{x}" y1="{y - 1.5}" x2="{x}" y2="{y + 1.5}"/>'
        f'<line x1="{x + SCALE_BAR_MM}" y1="{y - 1.5}" '
        f'x2="{x + SCALE_BAR_MM}" y2="{y + 1.5}"/>'
        f'<text x="{x + SCALE_BAR_MM / 2}" y="{y - 2}" '
        f'font-size="{standard.text_small_mm}" text-anchor="middle" '
        f'stroke="none" fill="black">100 mm</text>'
        f"</g>"
    )


def render_symbol_sheet(
    symbols: SymbolRegistry, standard: GraphicStandard = A3_LANDSCAPE
) -> str:
    column_width = max(
        (item.manifest.width_mm for item in symbols.all()), default=COLUMN_GAP_MM
    ) + COLUMN_GAP_MM
    row_height = max(
        (item.manifest.height_mm for item in symbols.all()), default=ROW_GAP_MM
    ) + ROW_GAP_MM
    columns = max(1, int(standard.usable_width_mm // column_width))

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{standard.sheet_width_mm}mm" height="{standard.sheet_height_mm}mm" '
        f'viewBox="0 0 {standard.sheet_width_mm:g} {standard.sheet_height_mm:g}">',
        f'<rect x="{standard.margin_left_mm}" y="{standard.margin_top_mm}" '
        f'width="{standard.usable_width_mm}" height="{standard.usable_height_mm}" '
        f'fill="none" stroke="black" stroke-width="{standard.line_thin_mm}"/>',
    ]

    for index, symbol in enumerate(symbols.all()):
        column, row = index % columns, index // columns
        x = standard.margin_left_mm + column * column_width
        y = standard.margin_top_mm + row * row_height
        markers = "".join(
            f'<circle class="port" cx="{port.x_mm}" cy="{port.y_mm}" r="0.6" '
            f'fill="black"/>'
            for port in symbol.manifest.ports
        )
        parts.append(
            f'<g class="symbol" data-symbol-id="{_escape(symbol.manifest.id)}" '
            f'transform="translate({x} {y})" '
            f'stroke="black" stroke-width="{standard.line_medium_mm}" fill="none">'
            f"{symbol.body}{markers}"
            f'<text x="0" y="{symbol.manifest.height_mm + standard.text_small_mm + 1}" '
            f'font-size="{standard.text_small_mm}" stroke="none" fill="black">'
            f"{_escape(symbol.manifest.id)}</text>"
            f"</g>"
        )

    parts.append(_scale_bar(standard))
    parts.append("</svg>")
    return "".join(parts)
```

Add to `src/disegnatore_mep/graphics/__init__.py`:

```python
from .svg import render_symbol_sheet
```

and extend `__all__` with `"render_symbol_sheet"`.

- [ ] **Step 4: verificare e committare**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src tests
git add src/disegnatore_mep/graphics tests/graphics/test_svg.py
git commit -m "feat: render a true-scale symbol sheet"
```

---

### Task 6: Prima libreria trasversale di simboli

**Files:**
- Create: `assets/symbols/*.json` e `assets/symbols/*.svg` (dodici simboli)
- Create: `examples/graphics/build_symbols.py`

**Interfaces:** consuma `SymbolManifest`; produce la libreria iniziale.

- [ ] **Step 1: scrivere lo script generatore dei manifesti**

Create `examples/graphics/build_symbols.py` che produce dodici simboli, quattro per dominio, tutti con porte sul perimetro e faccia coerente:

| id | dominio | in linea | porte |
|---|---|---|---|
| `valve-isolation` | idronico | si' | `a` sinistra, `b` destra |
| `valve-check` | idronico | si' | `a` sinistra, `b` destra |
| `strainer` | idronico | si' | `a` sinistra, `b` destra |
| `pump-circulator` | idronico | si' | `a` sinistra, `b` destra |
| `expansion-vessel` | idronico | no | `a` in alto |
| `air-vent` | idronico | no | `a` in basso |
| `duct-damper` | aeraulico | si' | `a` sinistra, `b` destra |
| `air-diffuser` | aeraulico | no | `a` sinistra |
| `fan-inline` | aeraulico | si' | `a` sinistra, `b` destra |
| `refrigerant-branch` | refrigerante | no | `a` sinistra, `b` destra, `c` in basso |
| `gas-valve` | gas | si' | `a` sinistra, `b` destra |
| `gas-meter` | gas | si' | `a` sinistra, `b` destra |

**Dimensioni, per rendere i manifesti completamente determinati:** ogni simbolo in linea misura 6×6 mm; ogni simbolo non in linea misura 8×8 mm, eccetto `expansion-vessel` che è 6×10 mm. Ogni porta è centrata sulla propria faccia — quindi su una faccia verticale `y_mm` vale metà altezza, su una orizzontale `x_mm` vale metà larghezza — tranne le tre porte di `refrigerant-branch`, dove `a` e `b` stanno a metà altezza e `c` a metà larghezza sul lato inferiore. `allowed_rotations_deg` vale `[0, 90, 180, 270]` per tutti; `inline_gap_mm` è pari alla larghezza per i simboli in linea e assente per gli altri. `keep_out` vale `min_clearance_mm` sui lati che portano una porta e `0` sugli altri.

Lo script deve, per ciascuno: costruire il dizionario del manifesto, validarlo con `SymbolManifest.model_validate` prima di scriverlo, scrivere `assets/symbols/<id>.json` e `assets/symbols/<id>.svg`. Il corpo SVG di ogni simbolo è un frammento senza radice `<svg>`, disegnato in coordinate locali in millimetri, con l'origine nell'angolo in alto a sinistra del riquadro.

**Sul disegno vero e proprio.** I tracciati dei dodici corpi sono l'unica parte di questo piano che non è pre-scritta riga per riga, perché è lavoro di disegno e non di trascrizione. Il vincolo è che ogni corpo resti dentro il proprio riquadro, che i tratti di attacco raggiungano le porte dichiarate, e che il simbolo sia riconoscibile da un termotecnico. Il giudice è il controllo visivo del Task 7 Step 7, non un test automatico. Esempio per `valve-isolation`, un corpo a farfalla di 6×6 mm:

```python
VALVE_ISOLATION_BODY = (
    '<line x1="0" y1="3" x2="1" y2="3"/>'
    '<line x1="5" y1="3" x2="6" y2="3"/>'
    '<path d="M1 1 L5 5 L5 1 L1 5 Z"/>'
)
```

Ogni simbolo dichiara `source` con il riferimento alla convenzione grafica adottata, e `keep_out` pari almeno a `A3_LANDSCAPE.min_clearance_mm` sui lati che portano porte.

- [ ] **Step 2: eseguire il generatore**

Run:

```bash
mkdir -p assets/symbols
.venv/bin/python examples/graphics/build_symbols.py
```

Expected: ventiquattro file creati, dodici manifesti e dodici corpi.

- [ ] **Step 3: verificare che la libreria carichi**

Run:

```bash
.venv/bin/python -c "from pathlib import Path; from disegnatore_mep.graphics.registry import SymbolRegistry; r = SymbolRegistry.from_directory(Path('assets/symbols')); print(len(r.all()), 'simboli caricati')"
```

Expected: `12 simboli caricati`.

- [ ] **Step 4: verificare la rigenerabilità**

Rieseguire il generatore e controllare che `git status --short assets/symbols` non mostri differenze. La generazione deve essere deterministica.

- [ ] **Step 5: commit**

```bash
git add assets/symbols examples/graphics/build_symbols.py
git commit -m "feat: add the first cross-domain symbol library"
```

---

### Task 7: Comando CLI e gate di accettazione

**Files:**
- Modify: `src/disegnatore_mep/cli.py`
- Create: `tests/acceptance/test_symbol_sheet.py`
- Modify: `examples/foundation/build_fixtures.py`
- Create: `docs/GRAPHIC_STANDARD.md`

**Interfaces:** produce il comando `symbols-sheet`.

- [ ] **Step 1: scrivere il test di accettazione**

Create `tests/acceptance/test_symbol_sheet.py`:

```python
from pathlib import Path
from xml.etree import ElementTree

from disegnatore_mep.cli import main
from disegnatore_mep.graphics.registry import SymbolRegistry

SYMBOLS = Path(__file__).resolve().parents[2] / "assets" / "symbols"


def test_the_shipped_library_loads() -> None:
    assert len(SymbolRegistry.from_directory(SYMBOLS).all()) == 12


def test_symbols_sheet_command_writes_a_true_scale_sheet(tmp_path: Path) -> None:
    output = tmp_path / "symbols.svg"
    assert main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS)]) == 0
    content = output.read_text(encoding="utf-8")
    assert 'width="420mm"' in content
    assert 'viewBox="0 0 420 297"' in content
    ElementTree.fromstring(content)


def test_every_shipped_symbol_appears_on_the_sheet(tmp_path: Path) -> None:
    output = tmp_path / "symbols.svg"
    main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS)])
    content = output.read_text(encoding="utf-8")
    for symbol in SymbolRegistry.from_directory(SYMBOLS).all():
        assert f'data-symbol-id="{symbol.manifest.id}"' in content


def test_missing_symbol_directory_returns_one(tmp_path: Path) -> None:
    assert main(["symbols-sheet", str(tmp_path / "out.svg"), "--symbols", str(tmp_path / "nope")]) == 1
```

- [ ] **Step 2: estendere la CLI**

In `src/disegnatore_mep/cli.py` aggiungere al parser:

```python
    sheet = commands.add_parser("symbols-sheet")
    sheet.add_argument("output", type=Path)
    sheet.add_argument("--symbols", type=Path, required=True)
```

e in `main`, prima del ramo che carica il progetto:

```python
        if args.command == "symbols-sheet":
            registry = SymbolRegistry.from_directory(args.symbols)
            args.output.write_text(render_symbol_sheet(registry), encoding="utf-8")
            return 0
```

Aggiungere gli import `from disegnatore_mep.graphics.registry import SymbolError, SymbolRegistry` e `from disegnatore_mep.graphics.svg import render_symbol_sheet`, e includere `SymbolError` nella tupla dell'`except`.

- [ ] **Step 3: allineare le fixture P0**

`examples/foundation/build_fixtures.py` costruisce definizioni con geometria e porte posizionate. Rimuovere `geometry()` e i campi `x_mm`, `y_mm`, `angle_deg` dalla funzione `port`, e far puntare ogni definizione a un simbolo esistente della libreria. Le otto definizioni di confine e macchina useranno simboli generici della libreria del Task 6 oppure simboli dedicati aggiunti li'; se manca un simbolo adatto, aggiungerlo in `assets/symbols` con lo stesso generatore anziché reintrodurre geometria nel catalogo.

Rigenerare e verificare che il gate G0 regga:

```bash
.venv/bin/python examples/foundation/build_fixtures.py
.venv/bin/python -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog
if [ $? -ne 0 ]; then echo 'Il progetto misto non valida piu' >&2; exit 1; fi
.venv/bin/python -m disegnatore_mep validate examples/foundation/invalid-cross-medium.json --catalog examples/foundation/catalog
if [ $? -ne 2 ]; then echo 'Il progetto incoerente non restituisce piu 2' >&2; exit 1; fi
```

- [ ] **Step 4: rigenerare lo schema JSON**

Run:

```bash
.venv/bin/python -m disegnatore_mep export-schema schemas/project.schema.json
```

- [ ] **Step 5: documentare lo standard grafico**

Create `docs/GRAPHIC_STANDARD.md` con: la tabella delle grandezze di `A3_LANDSCAPE` e la loro motivazione; la regola perimetro-faccia e perché sostituisce il vincolo P0 sulle porte interne; la divisione fra geometria del simbolo e semantica del catalogo, con la tabella della sezione «Decisione strutturale» di questo piano; come si aggiunge un simbolo alla libreria; come si stampa il foglio di riscontro e cosa misurare.

- [ ] **Step 6: eseguire il gate completo**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests examples
.venv/bin/python -m mypy src tests examples
.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols
```

Expected: tutto a `0`; il foglio viene prodotto. `outputs/` è già in `.gitignore`.

- [ ] **Step 7: verifica visiva e di stampa — non automatizzabile**

Aprire `outputs/symbols.svg` in un browser, stamparlo su A3 **senza adattamento alla pagina** e misurare con il righello la barra di scala: deve misurare 100 mm. Verificare a vista che i simboli siano riconoscibili e che le porte cadano sul perimetro. Registrare l'esito nel commit.

Questo passaggio è il vero gate della fase: i controlli automatici dicono che nulla si sovrappone, non che il disegno sia leggibile.

- [ ] **Step 8: commit finale**

```bash
git add src/disegnatore_mep/cli.py tests/acceptance/test_symbol_sheet.py examples schemas docs/GRAPHIC_STANDARD.md
git commit -m "test: qualify the graphic standard and symbol library"
```

---

## Copertura della specifica

| Area della specifica | Copertura |
|---|---|
| §11.1 spazio carta e grandezze in mm | Task 1 |
| §8 manifesto del simbolo, porte, orientamenti, area di rispetto, ancoraggi | Task 2 |
| §8 versione della definizione e fonte | Task 2, Task 6 |
| §8.1 compositi da primitive, pubblicati e contati come uno | Task 4 |
| §8.2 immutabilità della scala | Task 1, Task 5, Task 7 Step 7 |
| §7.3 interruzione di linea per i componenti in linea | Task 2, campo `inline_gap_mm` e vincolo delle due porte opposte |
| §12.4 controllo visivo e prova di stampa | Task 7 Step 7 |
| §17 riferimenti ISO per formato e simbologia | Task 1 margini, Task 6 campo `source` |
| Libreria trasversale iniziale | Task 6 |
| Layout, instradamento, multi-tavola | Piano successivo |
| Cartiglio, PDF, distinta, preflight | Piano successivo |
| Regole tecniche | Rimandate per D-040 |

## Self-review checklist

- [ ] Ogni grandezza grafica vive in `standard.py` e nessun numero magico compare altrove.
- [ ] Nessuna funzione è dedicata a uno schema tipo.
- [ ] Ogni porta di simbolo sta sul perimetro con faccia coerente, verificato da test.
- [ ] Un composito è pubblicato come simbolo unico e le sue porte esposte hanno posizione tradotta.
- [ ] Il foglio dichiara millimetri fisici e `viewBox` numericamente identico.
- [ ] Il foglio è deterministico e ben formato come XML.
- [ ] La libreria si rigenera identica.
- [ ] Il gate G0 di P0 continua a passare dopo la migrazione delle fixture.
- [ ] `pytest`, Ruff e mypy hanno exit code `0` su `src`, `tests` ed `examples`.
- [ ] La prova di stampa è stata eseguita e il righello conferma i 100 mm.
- [ ] `git status --short` è vuoto dopo l'ultimo commit.
