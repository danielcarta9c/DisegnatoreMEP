from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError

from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.types import Domain, PortFlow

from .errors import CatalogError
from .resolved import ResolvedComponent
from .schema import ComponentDefinition, PortDefinition

# CatalogError vive in .errors, ma resta esportato da qui: e' il nome con cui
# il resto del progetto lo importa da quando esisteva un solo modulo a sollevarlo.
if TYPE_CHECKING:
    from disegnatore_mep.model.project import ProjectModel

__all__ = ["CatalogError", "ComponentRegistry", "ResolvedComponent"]


class ComponentRegistry:
    """Il catalogo, con la geometria di ogni voce quando ha i simboli.

    **Le porte di comando stanno da parte** (REL-012, fase 3, I-226). Una pompa
    di calore, una caldaia, un circolatore, una valvola motorizzata, un
    ventilconvettore hanno nel catalogo anche l'alimentazione e il comando, e il
    loro simbolo li dichiara fra le `control_ports`. Questo registro **non le
    mostra**: `get`, `all` e `resolve` danno ogni voce com'era prima che quelle
    porte esistessero, e cosi' nessuna riga del motore — la posa, le regole, i
    diametri, le misure — vede un attacco che il grafo non usa. Le rimette
    soltanto `per_il_progetto`, e soltanto quelle che il grafo collega.

    Senza la libreria dei simboli il registro mostra le voci intere: lo usa il
    validatore topologico, che lavora sulla sola semantica e deve poter
    riconoscere un cavo che arriva sull'alimentazione di una pompa.
    """

    def __init__(
        self,
        definitions: list[ComponentDefinition],
        symbols: SymbolRegistry | None = None,
        porte_di_comando_in_uso: Mapping[str, frozenset[str]] | None = None,
        senza_linea: frozenset[str] = frozenset(),
    ) -> None:
        self._symbols = symbols
        self._intere: dict[str, ComponentDefinition] = {}
        for definition in definitions:
            if definition.id in self._intere:
                raise CatalogError(f"duplicate component definition: {definition.id}")
            if symbols is not None:
                self._check_symbol(definition, symbols)
            self._intere[definition.id] = definition
        for definition in self._intere.values():
            self._check_variant(definition)
        self._in_uso = dict(porte_di_comando_in_uso or {})
        self._senza_linea = senza_linea
        self._definitions: dict[str, ComponentDefinition] = {
            ident: self._senza_le_porte_da_parte(definition)
            for ident, definition in self._intere.items()
        }
        self._risolti: dict[str, ResolvedComponent] = {}

    def porte_di_comando(self, definition_id: str) -> frozenset[str]:
        """Le porte di comando della voce, collegate o no: quelle che il suo
        simbolo dichiara fra le `control_ports`. Vuoto senza simboli."""
        if self._symbols is None:
            return frozenset()
        definition = self._intere.get(definition_id)
        if definition is None or not self._symbols.contains(definition.symbol_id):
            return frozenset()
        return (
            self._symbols.get(definition.symbol_id).manifest.control_port_ids
            & definition.port_ids
        )

    def porte_del_fluido(self, definition: ComponentDefinition) -> tuple[PortDefinition, ...]:
        """Le porte della voce **senza quelle di comando**, anche quando il grafo
        le collega: un circolatore alimentato resta un pezzo che si cala in una
        tubazione d'acqua, e chi cerca un pezzo per fluido lo deve trovare."""
        comando = self.porte_di_comando(definition.id)
        return tuple(item for item in definition.ports if item.id not in comando)

    def _senza_le_porte_da_parte(self, definition: ComponentDefinition) -> ComponentDefinition:
        da_parte = self.porte_di_comando(definition.id) - self._in_uso.get(
            definition.id, frozenset()
        )
        if not da_parte:
            return definition
        return definition.model_copy(
            update={"ports": [item for item in definition.ports if item.id not in da_parte]}
        )

    def per_il_progetto(self, project: "ProjectModel") -> "ComponentRegistry":
        """Il catalogo **di questo grafo**: le porte di comando che il grafo
        collega tornano al loro posto, e le altre restano da parte.

        Una voce vale per tutti i suoi pezzi: se un circolatore ha l'alimentazione
        collegata, la porta c'e' anche sugli altri circolatori del grafo, libera.
        E' facoltativa, e libera non e' un difetto.

        **Un pezzo in linea senza la sua linea si posa come un pezzo.** Sulla
        tavola dell'elettrico e del comando (`piano.vista`) un circolatore non ha
        l'acqua, e resta con il suo cavo: non spezza piu' niente, e il piano lo
        posa come la macchina che e'. Vale per le voci i cui pezzi, in questo
        grafo, sono collegati soltanto dalle porte di comando.

        Senza elettrico nel grafo il catalogo che ne esce e' questo, voce per
        voce: e' lo stesso oggetto."""
        if self._symbols is None:
            return self
        definizioni = {item.id: item.definition_id for item in project.components}
        in_uso: dict[str, set[str]] = {}
        dal_fluido: set[str] = set()
        for connection in project.connections:
            for ref in (connection.endpoint_a, connection.endpoint_b):
                voce = definizioni.get(ref.component_id)
                if voce is None or voce not in self._intere:
                    continue
                if ref.port_id in self.porte_di_comando(voce):
                    in_uso.setdefault(voce, set()).add(ref.port_id)
                else:
                    dal_fluido.add(voce)
        if not in_uso:
            return self
        senza_linea = frozenset(
            voce
            for voce in set(in_uso) - dal_fluido
            if self._symbols.get(self._intere[voce].symbol_id).manifest.is_inline
        )
        return ComponentRegistry(
            list(self._intere.values()),
            self._symbols,
            {voce: frozenset(porte) for voce, porte in in_uso.items()},
            senza_linea,
        )

    def _check_variant(self, definition: ComponentDefinition) -> None:
        """Una variante e' la stessa macchina della sua voce base (D-188).

        Stessi mestieri e stessi attacchi — e' quello che rende la scelta una
        questione di parole del testo e non di collegamenti —, un simbolo
        diverso, e una base che non sia a sua volta una variante: altrimenti
        chi sceglie non saprebbe da quale voce partire."""
        variant = definition.variant
        if variant is None:
            return
        base = self._intere.get(variant.of)
        if base is None:
            raise CatalogError(
                f"{definition.id} e' variante di {variant.of}, che non e' nel catalogo"
            )
        if base.variant is not None:
            raise CatalogError(
                f"{definition.id} e' variante di {variant.of}, che e' a sua volta una "
                f"variante: la voce base dev'essere una sola"
            )
        if set(base.functions) != set(definition.functions):
            raise CatalogError(
                f"{definition.id} e' variante di {variant.of} ma non fa gli stessi "
                f"mestieri: {sorted(definition.functions)} contro {sorted(base.functions)}"
            )
        ports = sorted(definition.ports, key=lambda item: item.id)
        if ports != sorted(base.ports, key=lambda item: item.id):
            raise CatalogError(
                f"{definition.id} e' variante di {variant.of} ma non ha gli stessi "
                f"attacchi: una variante si collega come la sua voce base"
            )
        if base.symbol_id == definition.symbol_id:
            raise CatalogError(
                f"{definition.id} e' variante di {variant.of} con lo stesso simbolo: "
                f"una variante esiste per disegnarsi diversa"
            )

    @staticmethod
    def _check_symbol(definition: ComponentDefinition, symbols: SymbolRegistry) -> None:
        if not symbols.contains(definition.symbol_id):
            raise CatalogError(
                f"unknown symbol {definition.symbol_id} for {definition.id}"
            )
        manifest = symbols.get(definition.symbol_id).manifest
        # Le porte di comando sono facoltative anche nella voce: una voce che non
        # le dichiara si collega al simbolo come prima che esistessero, ed e' la
        # forma in cui `get` e `all` la restituiscono.
        if not (
            definition.port_ids <= manifest.port_ids
            and manifest.port_ids - definition.port_ids <= manifest.control_port_ids
        ):
            raise CatalogError(
                f"port ids do not match symbol {definition.symbol_id} "
                f"for {definition.id}: {sorted(definition.port_ids)} "
                f"vs {sorted(manifest.port_ids)}"
            )
        # Una porta che il simbolo tiene da parte e' un cavo facoltativo: nel
        # dominio del comando, e mai obbligatoria. Una porta del fluido messa da
        # parte sparirebbe dal disegno di ogni grafo che non la collega.
        for port in definition.ports:
            if port.id not in manifest.control_port_ids:
                continue
            if port.domain is not Domain.CONTROL or port.required:
                raise CatalogError(
                    f"{definition.id}: la porta {port.id} sta fra le porte di comando "
                    f"del simbolo {definition.symbol_id}, ma e' del dominio "
                    f"{port.domain.value}, obbligatoria={port.required}: una porta di "
                    f"comando e' del dominio control, e facoltativa"
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
            and all(port.medium == medium for port in self.porte_del_fluido(definition))
        )

    def bridging(
        self, function: str, source_medium: str, target_medium: str
    ) -> tuple[ComponentDefinition, ...]:
        """Le voci che portano quella funzione **da** un fluido **a** un altro.

        E' l'altra meta' di `serving`, e le due non si sovrappongono: li' tutte
        le porte stanno sullo stesso fluido, perche' il pezzo si cala dentro una
        tubazione; qui il pezzo e' un ponte, entra da un fluido e esce
        sull'altro, e nessuna tubazione lo contiene. Il verso e' parte
        dell'identita': si entra da una porta che **entra** sul fluido di
        partenza e si esce da una che **esce** su quello di arrivo.
        """
        if source_medium == target_medium:
            return ()
        return tuple(
            definition
            for definition in self.all()
            if function in definition.functions
            and {port.medium for port in self.porte_del_fluido(definition)}
            == {source_medium, target_medium}
            and any(
                port.medium == source_medium and port.flow is PortFlow.IN
                for port in self.porte_del_fluido(definition)
            )
            and any(
                port.medium == target_medium and port.flow is PortFlow.OUT
                for port in self.porte_del_fluido(definition)
            )
        )

    def bridge(
        self, function: str, source_medium: str, target_medium: str
    ) -> ComponentDefinition:
        """L'unica voce che porta quella funzione da un fluido all'altro."""
        found = self.bridging(function, source_medium, target_medium)
        if not found:
            raise CatalogError(
                f"no catalogue definition bridges {function!r} from "
                f"{source_medium!r} to {target_medium!r}"
            )
        if len(found) > 1:
            raise CatalogError(
                f"{len(found)} catalogue definitions bridge {function!r} from "
                f"{source_medium!r} to {target_medium!r} "
                f"({', '.join(item.id for item in found)}): which one a rule "
                f"means would be the programme's choice, not the catalogue's"
            )
        return found[0]

    def providing(self, function: str, medium: str) -> ComponentDefinition:
        """L'unica voce che porta quella funzione su quel fluido.

        E' cio' che tiene **una** regola dove prima ce n'erano tre, una per
        fluido: la regola dice quale funzione deve comparire, il catalogo dice
        con quale pezzo si ottiene sull'acqua di riscaldamento, sulla fredda o
        sulla sanitaria. Se le voci sono zero o piu' d'una la scelta sarebbe
        del programma, e allora si ferma invece di sceglierne una.

        **Una variante non la propone mai una regola** (D-188): si sceglie solo
        quando il testo la nomina. Lo sfiato senza rubinetto fa il mestiere dello
        sfiato con il rubinetto, e la regola che vuole uno sfogo d'aria propone il
        secondo (I-211).
        """
        found = tuple(item for item in self.serving(function, medium) if item.variant is None)
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
        risolto = self._risolti.get(definition_id)
        if risolto is not None:
            return risolto
        definition = self.get(definition_id)
        symbol = self._symbols.get(definition.symbol_id)
        manifest = symbol.manifest.con_le_porte_di_comando(
            self._in_uso.get(definition_id, frozenset())
        )
        if definition_id in self._senza_linea:
            manifest = manifest.model_copy(update={"inline_gap_mm": None})
        if manifest is not symbol.manifest:
            symbol = replace(symbol, manifest=manifest)
        risolto = ResolvedComponent(definition=definition, symbol=symbol)
        self._risolti[definition_id] = risolto
        return risolto
