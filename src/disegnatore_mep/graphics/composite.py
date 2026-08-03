"""Compositi assemblati da primitive e pubblicati come simbolo unico.

Un prodotto che integra piu' funzioni viene mostrato come un solo simbolo
riconoscibile e conta una sola volta nella distinta. Internamente puo' essere
costruito da primitive riusabili, ma cio' non è visibile all'utilizzatore.
"""

from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, FiniteFloat, StrictModel

from .registry import Symbol, SymbolRegistry
from .symbol import TOLERANCE_MM, KeepOut, LabelAnchor, SymbolManifest, SymbolPort


class CompositePart(StrictModel):
    symbol_id: str = Field(pattern=ID_PATTERN)
    offset_x_mm: FiniteFloat = Field(ge=0)
    offset_y_mm: FiniteFloat = Field(ge=0)


class ExposedPort(StrictModel):
    part_index: int = Field(ge=0)
    port_id: str = Field(pattern=ID_PATTERN)
    as_id: str = Field(pattern=ID_PATTERN)


class CompositeSpec(StrictModel):
    """Come si autora un composito: gli stessi campi di un simbolo scritto a mano.

    `inline_gap_mm`, `keep_out` e `label_anchors` sono dichiarati qui, non
    dedotti dalle primitive. L'area di rispetto di un composito non e' l'unione
    di quelle delle sue parti - una parte interna non contribuisce nulla
    all'involucro esterno - l'interruzione di linea appartiene al composito
    intero e non a una sua parte, e gli ancoraggi di etichetta di un composito
    sono quelli del prodotto unico, non quelli delle primitive che lo compongono.
    I valori di default sono quelli di `SymbolManifest`.
    """

    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    width_mm: FiniteFloat = Field(gt=0)
    height_mm: FiniteFloat = Field(gt=0)
    allowed_rotations_deg: list[int] = Field(min_length=1)
    inline_gap_mm: FiniteFloat | None = Field(default=None, gt=0)
    keep_out: KeepOut = Field(default_factory=KeepOut)
    label_anchors: list[LabelAnchor] = Field(default_factory=list)
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
            part.offset_x_mm + source.manifest.width_mm > spec.width_mm + TOLERANCE_MM
            or part.offset_y_mm + source.manifest.height_mm > spec.height_mm + TOLERANCE_MM
        ):
            raise ValueError(f"part {index} falls outside the composite box")

    ports: list[SymbolPort] = []
    for exposed in spec.exposed_ports:
        part = spec.parts[exposed.part_index]
        try:
            origin = resolved[exposed.part_index].manifest.port(exposed.port_id)
        except KeyError as exc:
            raise ValueError(f"part {exposed.part_index} has no port {exposed.port_id}") from exc
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
        inline_gap_mm=spec.inline_gap_mm,
        ports=ports,
        keep_out=spec.keep_out,
        label_anchors=spec.label_anchors,
        source=spec.source,
    )

    fragments = [
        f'<g transform="translate({part.offset_x_mm} {part.offset_y_mm})">{source.body}</g>'
        for part, source in zip(spec.parts, resolved, strict=True)
    ]
    return Symbol(manifest=manifest, body="".join(fragments))
