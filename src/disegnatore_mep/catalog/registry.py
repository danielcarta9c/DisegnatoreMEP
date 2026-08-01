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
