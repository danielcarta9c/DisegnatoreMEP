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
