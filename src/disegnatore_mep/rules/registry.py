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

from disegnatore_mep.catalog.errors import CatalogError
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition

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
        """Cio' che una regola propone deve esistere in catalogo, e una sola volta.

        Verificarlo al caricamento, e non a meta' valutazione, e' la differenza
        fra una diagnostica che nomina la regola e un errore che compare a
        seconda dell'impianto: da quando una regola dichiara una **funzione**
        invece di un pezzo, «quale pezzo» e' una domanda al catalogo, e su un
        fluido su cui la risposta e' doppia il programma sceglierebbe da solo.
        """
        known_functions = {
            function
            for definition in catalog.all()
            for function in definition.functions
        }
        for rule in self.rules:
            if rule.then.bridges_from_medium is not None:
                self._bridges(rule, catalog)
                continue
            for proposed in rule.then.functions():
                self._resolves_everywhere(rule.id, proposed, catalog)
            for label, awaited in (
                ("when.anchor_has_function", rule.when.anchor_has_function),
                ("when.network_has_function", rule.when.network_has_function),
                ("when.network_lacks_function", rule.when.network_lacks_function),
            ):
                if awaited is not None and awaited not in known_functions:
                    raise RuleError(
                        f"rule {rule.id} names the function {awaited!r} in {label}, "
                        f"which no catalogue definition declares: a rule that waits "
                        f"for a function nobody has never fires"
                    )

    @staticmethod
    def _bridges(rule: RuleDefinition, catalog: ComponentRegistry) -> None:
        """Un ponte si risolve fra due fluidi, e uno solo lo deve portare.

        `serving` non lo troverebbe, e non lo deve trovare: le porte di un ponte
        non stanno tutte sullo stesso fluido perche' il pezzo non si cala dentro
        una tubazione (DRAW-006-R1, blocco D).
        """
        source = rule.then.bridges_from_medium
        assert source is not None
        media = {
            port.medium
            for definition in catalog.all()
            for port in definition.ports
        }
        resolved = 0
        for medium in sorted(media - {source}):
            if not catalog.bridging(rule.then.provides_function, source, medium):
                continue
            try:
                definition = catalog.bridge(rule.then.provides_function, source, medium)
            except CatalogError as exc:
                raise RuleError(f"rule {rule.id} proposes a bridge: {exc}") from exc
            RuleRegistry._bridge_ports(rule, definition, source, medium)
            resolved += 1
        if resolved == 0:
            raise RuleError(
                f"rule {rule.id} proposes a bridge that carries "
                f"{rule.then.provides_function!r} from {source!r}, and no "
                f"catalogue definition does"
            )

    @staticmethod
    def _bridge_ports(
        rule: RuleDefinition, definition: ComponentDefinition, source: str, target: str
    ) -> None:
        """Gli attacchi che la regola nomina esistono, e ciascuno sul suo fluido.

        Il ponte ordinario pesca da `inlet_port` e rende su `outlet_port`; quello
        **in linea** (D-175) sta dentro la tubazione della rete della regola, fra
        `inlet_port` e `outlet_port`, e prende l'altro fluido da `bridge_port`.
        Un nome sbagliato qui produrrebbe una tubazione su un attacco che il
        pezzo non ha, e lo si scoprirebbe solo a meta' catena.
        """
        if rule.then.bridge_port is None:
            wanted = {rule.then.inlet_port: source, rule.then.outlet_port: target}
        else:
            wanted = {
                rule.then.inlet_port: target,
                rule.then.outlet_port: target,
                rule.then.bridge_port: source,
            }
        media_of = {port.id: port.medium for port in definition.ports}
        for port_id, medium in wanted.items():
            if media_of.get(port_id) != medium:
                raise RuleError(
                    f"rule {rule.id} connects {definition.id}.{port_id} on "
                    f"{medium!r}, and the catalogue declares "
                    f"{media_of.get(port_id, 'no such port')!r} there"
                )

    @staticmethod
    def _resolves_everywhere(
        rule_id: str, function: str, catalog: ComponentRegistry
    ) -> None:
        """Su ogni fluido su cui esiste, quella funzione deve dare un pezzo solo."""
        media = {
            port.medium
            for definition in catalog.all()
            if function in definition.functions
            for port in definition.ports
        }
        resolved = 0
        for medium in sorted(media):
            if not catalog.serving(function, medium):
                continue
            try:
                catalog.providing(function, medium)
            except CatalogError as exc:
                raise RuleError(f"rule {rule_id} proposes {function!r}: {exc}") from exc
            resolved += 1
        if resolved == 0:
            raise RuleError(
                f"rule {rule_id} proposes {function!r}, which no catalogue "
                f"definition provides on any medium"
            )


__all__ = ["RuleRegistry"]
