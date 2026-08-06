"""Genera `docs/prodotto/ALBERO_IMPIANTO.md`: l'impianto completo, da leggere.

Le regole degli accessori non si collaudano su un disegno (D-096). Il disegno
prova l'instradatore e il validatore; **cosa** le regole abbiano messo, e dove,
si vede meglio su un grafo scritto — e un grafo scritto si puo' leggere,
correggere e bocciare senza aprire un file di codice.

La forma e' quella di una rete stradale (D-097): ogni pezzo e' un **nodo** con la
propria sigla, ogni tubazione fra due pezzi e' un **arco**, e un attacco su cui
convergono piu' tubazioni e' un **incrocio** con i bracci numerati. Non e' un
albero e non lo si forza a esserlo: un circuito idronico e' un **anello**, e un
albero si spezzerebbe al primo ritorno che lo chiude.

Si legge partendo dalle sorgenti — dove il calore entra nell'acqua e dove
l'acqua entra nell'edificio — e seguendo il fluido (D-098). E' lo stesso ordine
con cui le sigle vengono contate: cosi' l'ordine di lettura e l'ordine dei numeri
sono la stessa cosa.

Si esegue senza argomenti per riscrivere il documento pubblicato:

    python examples/rules/build_plant_tree.py
"""

import sys
from collections import defaultdict
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition, ComponentTrait
from disegnatore_mep.catalog.tags import (
    FAMILIES,
    FAMILY_NAME,
    PREFIX_OF,
    assign_tags,
    sources_of,
    visit_order,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.model.types import PortFlow
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import RuleGap
from disegnatore_mep.rules.registry import RuleRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
ESSENTIAL = REPO_ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
COMPLETE = REPO_ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
CATALOG = REPO_ROOT / "examples" / "layout" / "catalog"
SYMBOLS = REPO_ROOT / "assets" / "symbols"
RULES = REPO_ROOT / "rules" / "hydronic"
DOCUMENT = REPO_ROOT / "docs" / "prodotto" / "ALBERO_IMPIANTO.md"

FLUIDS: dict[str, str] = {
    "heating_water": "acqua di riscaldamento",
    "cold_water": "acqua fredda sanitaria",
    "domestic_hot_water": "acqua calda sanitaria",
}
"""Come si chiama in parole cio' che scorre. Un fluido che non e' qui dentro fa
fermare la generazione: meglio un documento che non esce di uno che presenta al
committente un nome tecnico che lui non usa."""

DIRECTIONS: dict[PortFlow, str] = {
    PortFlow.OUT: "uscita",
    PortFlow.IN: "ingresso",
    PortFlow.BIDIRECTIONAL: "passaggio",
}


class TreeError(ValueError):
    """Qualcosa che il documento non sa dire in italiano."""


def fluid(medium: str) -> str:
    try:
        return FLUIDS[medium]
    except KeyError as exc:
        raise TreeError(
            f"non so come chiamare in parole il fluido {medium!r}: aggiungerlo "
            f"invece di lasciarlo comparire cosi' com'e' davanti al committente"
        ) from exc


def family_in_words(function: str) -> str:
    try:
        return FAMILY_NAME[PREFIX_OF[function]]
    except KeyError as exc:
        raise TreeError(
            f"non so come chiamare in parole un pezzo che fa {function!r}"
        ) from exc


class Plant:
    """L'impianto letto come grafo: nodi, bracci, archi, e le file fra un nodo e l'altro."""

    def __init__(self, project: ProjectModel, catalog: ComponentRegistry) -> None:
        self.project = project
        self.catalog = catalog
        self.tags = assign_tags(project, catalog)
        self.order = visit_order(project, catalog)
        self.sources = sources_of(project, catalog)
        self.definitions: dict[str, ComponentDefinition] = {
            item.id: catalog.get(item.definition_id) for item in project.components
        }
        self.inline = frozenset(
            item.id
            for item in project.components
            if catalog.resolve(item.definition_id).is_inline
        )
        self.networks = {item.id: item for item in project.networks}
        self.pipes: dict[tuple[str, str], list[ConnectionModel]] = defaultdict(list)
        for connection in project.connections:
            for ref in (connection.endpoint_a, connection.endpoint_b):
                self.pipes[(ref.component_id, ref.port_id)].append(connection)
        self.arms: dict[str, dict[str, int]] = {}
        for component_id, definition in self.definitions.items():
            numbered: dict[str, int] = {}
            for port in definition.ports:
                if (component_id, port.id) in self.pipes:
                    numbered[port.id] = len(numbered) + 1
            self.arms[component_id] = numbered

    # --- come si nomina ogni cosa -------------------------------------------

    def sigla(self, component_id: str) -> str:
        return self.tags[component_id]

    def what(self, component_id: str) -> str:
        return self.definitions[component_id].name

    def named(self, component_id: str) -> str:
        return f"{self.sigla(component_id)} {self.what(component_id)}"

    def arm(self, component_id: str, port_id: str) -> str:
        number = self.arms[component_id][port_id]
        port = next(
            item
            for item in self.definitions[component_id].ports
            if item.id == port_id
        )
        converging = len(self.pipes[(component_id, port_id)])
        crowd = f", vi convergono {converging} tubazioni" if converging > 1 else ""
        return f"braccio {number} ({DIRECTIONS[port.flow]}{crowd})"

    def fluid_of(self, connection: ConnectionModel) -> str:
        return fluid(self.networks[connection.network_id].medium)

    def hangs_off_the_pipe(self, component_id: str) -> bool:
        return (
            self.definitions[component_id].attachment is ComponentTrait.ATTACHMENT_BRANCH
        )

    # --- le file fra un nodo e l'altro ---------------------------------------

    def is_a_node(self, component_id: str) -> bool:
        """Un incrocio, non un pezzo posato lungo il tubo."""
        return component_id not in self.inline

    def run_from(
        self, start: str, first: ConnectionModel
    ) -> tuple[list[str], str, str, list[str]]:
        """La fila dei pezzi da un nodo fino al nodo successivo.

        Restituisce i pezzi in linea, il nodo di arrivo, il suo braccio e le
        tubazioni percorse. Un anello che si richiude torna al nodo di partenza
        e lo dice, invece di girare all'infinito."""
        pieces: list[str] = []
        used: list[str] = []
        cursor, current = start, first
        seen = {start}
        end, end_port = start, ""
        while True:
            used.append(current.id)
            far = (
                current.endpoint_b
                if current.endpoint_a.component_id == cursor
                else current.endpoint_a
            )
            end, end_port = far.component_id, far.port_id
            if far.component_id in seen or self.is_a_node(far.component_id):
                break
            pieces.append(far.component_id)
            seen.add(far.component_id)
            following = next(
                (
                    item
                    for (owner, _), pipes in self.pipes.items()
                    if owner == far.component_id
                    for item in pipes
                    if item.id not in used
                ),
                None,
            )
            if following is None:
                break
            cursor, current = far.component_id, following
        return pieces, end, end_port, used

    def runs(self) -> list[tuple[str, str, list[str], str, str, ConnectionModel]]:
        """Tutte le file dell'impianto, nell'ordine in cui si incontrano.

        Ogni fila esce orientata come scorre l'acqua — da dove esce a dove
        entra — anche quando la si e' incontrata camminando all'indietro: una
        fila letta al contrario direbbe il falso su monte e valle.
        """
        walked: set[str] = set()
        found: list[tuple[str, str, list[str], str, str, ConnectionModel]] = []
        for component_id in self.order:
            if not self.is_a_node(component_id):
                continue
            for port in self.definitions[component_id].ports:
                for pipe in self.pipes.get((component_id, port.id), []):
                    if pipe.id in walked:
                        continue
                    pieces, end, end_port, used = self.run_from(component_id, pipe)
                    walked.update(used)
                    if pipe.endpoint_a.component_id == component_id:
                        found.append((component_id, port.id, pieces, end, end_port, pipe))
                    else:
                        found.append(
                            (end, end_port, list(reversed(pieces)), component_id, port.id, pipe)
                        )
        return found


def head(plant: Plant) -> list[str]:
    starts = " e ".join(plant.named(item) for item in plant.sources)
    return [
        "# L'albero dell'impianto",
        "",
        "> **Cosa approvi qui.** L'impianto completo — quello che hai descritto piu' tutto",
        "> cio' che le regole degli accessori gli hanno aggiunto — scritto invece che",
        "> disegnato. Serve a vedere **che cosa e' uscito e dove sta**, prima e",
        "> indipendentemente da qualunque tavola.",
        ">",
        "> **Perche' non un disegno.** Un disegno prova l'instradamento e la resa grafica.",
        "> Qui la domanda e' un'altra: il pezzo giusto e' finito nel punto giusto, sul tubo",
        "> giusto? Quella si legge meglio su un elenco che su un segno.",
        "",
        "---",
        "",
        "## Come si legge",
        "",
        "- **Ogni pezzo e' un nodo** con la propria sigla, macchine e accessori allo stesso",
        "  modo. Le sigle gia' scritte da te restano come le hai scritte.",
        "- **Ogni tubazione fra due pezzi e' un arco**, e porta il proprio fluido.",
        "- **Ogni attacco e' un braccio numerato**, come in un incrocio stradale: un volano a",
        "  quattro attacchi e' un nodo solo con quattro bracci. Dove su un braccio convergono",
        "  piu' tubazioni, il braccio lo dice.",
        "- **Non e' un albero, e' un anello.** Un circuito si chiude su se' stesso: dove",
        "  succede, la lettura lo segnala invece di fermarsi.",
        "",
        f"**Da dove si comincia a contare.** Dalle sorgenti — {starts} — seguendo l'acqua.",
        "La prima valvola che si incontra uscendo dal generatore e' la numero uno della sua",
        "famiglia. **Costo di questa scelta, detto subito:** se domani si aggiunge un pezzo",
        "vicino a una sorgente, i numeri della sua famiglia a valle scalano tutti di uno. E'",
        "normale per un documento che si rigenera a ogni revisione; cio' che non cambia mai",
        "e' che lo stesso impianto dia sempre le stesse sigle.",
        "",
    ]


def families_table(plant: Plant) -> list[str]:
    present = {tag.rsplit("-", 1)[0] for tag in plant.tags.values()}
    rows = [
        f"| **{prefix}** | {name} |"
        for _, prefix, name in FAMILIES
        if prefix in present
    ]
    unlisted = sorted(present - {prefix for _, prefix, _ in FAMILIES})
    rows += [f"| **{prefix}** | famiglia nominata da te nel modello |" for prefix in unlisted]
    return [
        "## Le sigle, per famiglia",
        "",
        "| Sigla | Famiglia |",
        "|---|---|",
        *rows,
        "",
    ]


def nodes_table(plant: Plant) -> list[str]:
    rows: list[str] = []
    for component_id in plant.order:
        media: list[str] = []
        for (owner, port_id), pipes in plant.pipes.items():
            if owner != component_id:
                continue
            for pipe in pipes:
                name = plant.fluid_of(pipe)
                if name not in media:
                    media.append(name)
            del port_id
        arms = " · ".join(
            plant.arm(component_id, port_id)
            for port_id in plant.arms[component_id]
        )
        hanging = " · pende dal tubo" if plant.hangs_off_the_pipe(component_id) else ""
        rows.append(
            f"| **{plant.sigla(component_id)}** | {plant.what(component_id)}{hanging} "
            f"| {', '.join(media)} | {arms} |"
        )
    return [
        "## I nodi",
        "",
        "| Sigla | Che cos'e' | Fluidi che tocca | Bracci |",
        "|---|---|---|---|",
        *rows,
        "",
    ]


def arcs_table(plant: Plant) -> list[str]:
    rows: list[str] = []
    for connection in plant.project.connections:
        first, second = connection.endpoint_a, connection.endpoint_b
        rows.append(
            f"| {plant.sigla(first.component_id)}, "
            f"{plant.arm(first.component_id, first.port_id)} "
            f"| {plant.sigla(second.component_id)}, "
            f"{plant.arm(second.component_id, second.port_id)} "
            f"| {plant.fluid_of(connection)} |"
        )
    return [
        "## Gli archi",
        "",
        "Dal pezzo da cui l'acqua esce a quello in cui entra.",
        "",
        "| Da | A | Fluido |",
        "|---|---|---|",
        *rows,
        "",
    ]


def walk_through(plant: Plant, gaps: list[RuleGap]) -> list[str]:
    lines = [
        "## Come si segue l'acqua",
        "",
        "Ogni blocco e' una tubazione fra due pezzi, con in mezzo la fila ordinata di cio'",
        "che ci sta sopra, da monte a valle.",
        "",
    ]
    missing: dict[str, list[RuleGap]] = defaultdict(list)
    for gap in gaps:
        missing[gap.anchor.component_id].append(gap)

    everything = plant.runs()
    # I circuiti si presentano nell'ordine in cui le sorgenti li raggiungono, non
    # nell'ordine in cui il file li elenca: leggere e contare devono essere la
    # stessa passeggiata.
    circuits: list[str] = []
    for item in everything:
        if item[5].network_id not in circuits:
            circuits.append(item[5].network_id)
    for network_id in circuits:
        network = plant.networks[network_id]
        rows = [item for item in everything if item[5].network_id == network_id]
        title = network.name
        if title.strip().lower() != fluid(network.medium):
            title = f"{title} — {fluid(network.medium)}"
        lines += [f"### {title}", ""]
        # Un circuito e' un anello: prima o poi una fila arriva su un pezzo gia'
        # letto. Quello e' il punto in cui il giro si richiude, e va detto — se
        # ci si fermasse li' il lettore penserebbe che manchi un pezzo.
        met: set[str] = set()
        for start, port_id, pieces, end, end_port, _ in rows:
            # Si richiude quando la tubazione unisce due pezzi **gia' letti
            # entrambi**: e' li' che l'anello si chiude. Arrivare su un pezzo
            # gia' visto ma partendo da uno nuovo e' solo un ramo in piu'.
            closes = (
                f" · **qui il giro si richiude su {plant.sigla(end)}**"
                if start in met and end in met
                else ""
            )
            met.update({start, end})
            lines.append(
                f"**{plant.named(start)}**, {plant.arm(start, port_id)} → "
                f"**{plant.named(end)}**, {plant.arm(end, end_port)}{closes}"
            )
            if pieces:
                lines.append(
                    "&nbsp;&nbsp;&nbsp;"
                    + " · ".join(plant.named(piece) for piece in pieces)
                )
                for piece in pieces:
                    if plant.hangs_off_the_pipe(piece):
                        lines.append(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ {plant.sigla(piece)} "
                            f"non e' un organo di passaggio: pende dal tubo con una "
                            f"propria derivazione"
                        )
            else:
                lines.append("&nbsp;&nbsp;&nbsp;*niente in mezzo*")
            for holder in (start, end, *pieces):
                for gap in missing.get(holder, []):
                    lines.append(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⚠ **manca "
                        f"{family_in_words(gap.missing_function).lower()}** su "
                        f"{plant.sigla(holder)}: servirebbe, e in catalogo non c'e' "
                        f"nessun pezzo che lo faccia su {fluid(gap.medium)}. Va deciso "
                        f"dal progettista."
                    )
            lines.append("")
    return lines


def open_points(plant: Plant, gaps: list[RuleGap]) -> list[str]:
    if not gaps:
        return [
            "## Punti aperti",
            "",
            "Nessuno: per ogni accessorio che le regole hanno chiesto, il catalogo aveva il",
            "pezzo adatto al fluido di quella tubazione.",
            "",
        ]
    rows = [
        f"| **{plant.sigla(gap.anchor.component_id)}** "
        f"| {family_in_words(gap.missing_function)} "
        f"| {fluid(gap.medium)} |"
        for gap in gaps
    ]
    return [
        "## Punti aperti",
        "",
        "Qui una regola si applicava — il pezzo la chiedeva davvero — e il catalogo non",
        "aveva niente da offrire su quel fluido. Non e' una dimenticanza del disegno: e'",
        "una scelta che torna al progettista.",
        "",
        "| Su quale pezzo | Che cosa manca | Su quale fluido |",
        "|---|---|---|",
        *rows,
        "",
    ]


def render(plant: Plant, gaps: list[RuleGap]) -> str:
    lines = [
        *head(plant),
        "---",
        "",
        *families_table(plant),
        "---",
        "",
        *nodes_table(plant),
        "---",
        "",
        *arcs_table(plant),
        "---",
        "",
        *walk_through(plant, gaps),
        "---",
        "",
        *open_points(plant, gaps),
        "---",
        "",
        "## Cosa ti stiamo chiedendo",
        "",
        "Di scorrere la lettura dell'acqua e dirci, per ogni pezzo: **e' quello giusto, ed",
        "e' nel punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito",
        "sbagliato si vede da qui, senza aprire nient'altro.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build(project: ProjectModel, catalog: ComponentRegistry, gaps: list[RuleGap]) -> str:
    return render(Plant(project, catalog), gaps)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    target = Path(arguments[0]) if arguments else DOCUMENT
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog)
    _, _, gaps = saturate(load_project(ESSENTIAL), catalog, rules)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build(load_project(COMPLETE), catalog, gaps), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
