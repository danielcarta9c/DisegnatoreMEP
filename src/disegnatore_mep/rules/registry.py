"""Il registro delle regole: un pacchetto caricato da una cartella.

Stesso patto del catalogo dei componenti — file per file, ordine deterministico,
diagnostica che nomina il file colpevole — perche' una regola e' **dato
versionato e non codice** (§3.2 del piano P1). E' il requisito che permette di
correggere una regola, o di aggiungerne una da un manuale nuovo, senza toccare
il motore.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry

from .errors import RuleError
from .schema import RuleDefinition


@dataclass(frozen=True)
class RuleRegistry:
    rules: tuple[RuleDefinition, ...]

    @classmethod
    def from_directory(cls, directory: Path) -> "RuleRegistry":
        loaded: dict[str, tuple[RuleDefinition, Path]] = {}
        for path in sorted(directory.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuleError(f"rule file {path.name} is not valid JSON: {exc}") from exc
            try:
                rule = RuleDefinition.model_validate(payload)
            except Exception as exc:
                raise RuleError(f"rule file {path.name} is not a valid rule: {exc}") from exc
            if rule.id in loaded:
                raise RuleError(
                    f"rule {rule.id} is declared twice, in "
                    f"{loaded[rule.id][1].name} and in {path.name}"
                )
            loaded[rule.id] = (rule, path)
        return cls(rules=tuple(item[0] for item in loaded.values()))

    def all(self) -> tuple[RuleDefinition, ...]:
        return self.rules

    def cross_check(self, catalog: ComponentRegistry) -> None:
        """Cio' che una regola propone deve esistere in catalogo.

        Verificarlo al caricamento, e non a meta' valutazione, e' la differenza
        fra una diagnostica che nomina la regola e un errore che compare a
        seconda dell'impianto.
        """
        known_functions = {
            function
            for definition in catalog.all()
            for function in definition.functions
        }
        for rule in self.rules:
            if not catalog.contains(rule.then.definition_id):
                raise RuleError(
                    f"rule {rule.id} proposes {rule.then.definition_id}, which the "
                    f"catalogue does not define"
                )
            for label, function in (
                ("when.anchor_has_function", rule.when.anchor_has_function),
                ("when.network_has_function", rule.when.network_has_function),
                ("when.network_lacks_function", rule.when.network_lacks_function),
                ("satisfied_by.network_has_function", rule.satisfied_by.network_has_function),
                ("satisfied_by.port_carries_function", rule.satisfied_by.port_carries_function),
            ):
                if function is not None and function not in known_functions:
                    raise RuleError(
                        f"rule {rule.id} names the function {function!r} in {label}, "
                        f"which no catalogue definition declares: a rule that waits "
                        f"for a function nobody has never fires"
                    )


__all__ = ["RuleRegistry"]
