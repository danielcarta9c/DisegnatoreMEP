from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.graphics.registry import SymbolRegistry

from .errors import CatalogError
from .resolved import ResolvedComponent
from .schema import ComponentDefinition

# CatalogError vive in .errors, ma resta esportato da qui: e' il nome con cui
# il resto del progetto lo importa da quando esisteva un solo modulo a sollevarlo.
__all__ = ["CatalogError", "ComponentRegistry", "ResolvedComponent"]


class ComponentRegistry:
    def __init__(
        self,
        definitions: list[ComponentDefinition],
        symbols: SymbolRegistry | None = None,
    ) -> None:
        self._symbols = symbols
        self._definitions: dict[str, ComponentDefinition] = {}
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

    def serving(self, function: str, medium: str) -> tuple[ComponentDefinition, ...]:
        """Le voci che portano quella funzione su quel fluido, in ordine.

        «Su quel fluido» vuol dire **tutte** le porte su quel fluido: un
        accessorio si cala dentro una tubazione, e una voce con una porta su
        un altro fluido non ci sta dentro — e' una macchina che li mette in
        comunicazione, non un pezzo da infilare in una tratta.
        """
        return tuple(
            definition
            for definition in self.all()
            if function in definition.functions
            and all(port.medium == medium for port in definition.ports)
        )

    def providing(self, function: str, medium: str) -> ComponentDefinition:
        """L'unica voce che porta quella funzione su quel fluido.

        E' cio' che tiene **una** regola dove prima ce n'erano tre, una per
        fluido: la regola dice quale funzione deve comparire, il catalogo dice
        con quale pezzo si ottiene sull'acqua di riscaldamento, sulla fredda o
        sulla sanitaria. Se le voci sono zero o piu' d'una la scelta sarebbe
        del programma, e allora si ferma invece di sceglierne una.
        """
        found = self.serving(function, medium)
        if not found:
            raise CatalogError(
                f"no catalogue definition provides {function!r} on {medium!r}: a "
                f"rule that asks for it would have nothing to propose"
            )
        if len(found) > 1:
            raise CatalogError(
                f"{len(found)} catalogue definitions provide {function!r} on "
                f"{medium!r} ({', '.join(item.id for item in found)}): which one "
                f"a rule means would be the programme's choice, not the "
                f"catalogue's"
            )
        return found[0]

    def resolve(self, definition_id: str) -> ResolvedComponent:
        """La definizione insieme alla propria geometria.

        Richiede la libreria dei simboli. Resta separato da `get` perche'
        `symbols` e' opzionale per scelta: il validatore topologico lavora sulla
        sola semantica e non deve pretendere la libreria sotto mano.
        """
        if self._symbols is None:
            raise CatalogError(
                f"cannot resolve {definition_id}: the catalog was loaded without a "
                f"symbol library; pass symbols=SymbolRegistry.from_directory(...) "
                f"to ComponentRegistry.from_directory"
            )
        definition = self.get(definition_id)
        return ResolvedComponent(
            definition=definition, symbol=self._symbols.get(definition.symbol_id)
        )
