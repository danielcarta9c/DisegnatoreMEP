"""Genera `docs/prodotto/GRAFO_IMPIANTO.md`: l'impianto scritto, da leggere.

Il contenuto di un impianto non si giudica su un disegno (D-096): il disegno
prova l'instradatore, i validatori e la skill finita. Qui la domanda e' un'altra
— quali pezzi ci sono, come si chiamano, dove stanno, su che fluido, e dove il
giro si richiude — e a quella si risponde meglio su un elenco che su un segno.

La forma e' quella di una rete stradale (D-097): ogni pezzo e' un **nodo** con la
propria sigla, ogni tubazione fra due pezzi e' un **arco**, ogni attacco e' un
**braccio** numerato, e un braccio su cui convergono piu' tubazioni e' un
**incrocio**. La lettura parte dalle sorgenti dichiarate e segue il fluido
(D-098), che e' anche l'ordine con cui le sigle vengono contate: leggere e
numerare sono la stessa passeggiata.

**I punti aperti sono parte del grafo, non un secondo documento.** Dove una
regola degli accessori si applica davvero e il catalogo non ha niente da offrire
su quel fluido, il pezzo manca — e la cosa si dice **sul nodo in cui manca**,
nella sezione di cio' che il grafo non tace. Un documento a parte per la stessa
domanda si sarebbe messo a dire cose diverse.

**Il documento non si scrive a mano.** Si esegue questo file, senza argomenti,
e si ottiene la versione pubblicata:

    python examples/graph/build_plant_graph.py

Il documento e' severo dove il programma e' indulgente: un fluido o una famiglia
che non si sappia dire in italiano fermano la generazione invece di far comparire
un'etichetta interna davanti a chi legge.
"""

import sys
from collections.abc import Sequence
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentTrait
from disegnatore_mep.graph import (
    HydraulicLine,
    LineNaming,
    Naming,
    PlantGraph,
    PlantLines,
    read_lines,
    read_plant,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import Domain
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import RuleGap
from disegnatore_mep.rules.registry import RuleRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANT = REPO_ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
ESSENTIAL = REPO_ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
CATALOG = REPO_ROOT / "examples" / "layout" / "catalog"
SYMBOLS = REPO_ROOT / "assets" / "symbols"
NAMING = REPO_ROOT / "naming"
RULES = REPO_ROOT / "rules" / "hydronic"
DOCUMENT = REPO_ROOT / "docs" / "prodotto" / "GRAFO_IMPIANTO.md"


class Pen:
    """Come si dice ogni cosa in parole, e nient'altro.

    Tiene insieme il grafo, i nomi in italiano e i nomi dei circuiti: e' l'unico
    posto da cui il testo attinge, cosi' un'etichetta interna non puo' finire
    nel documento passando da un'altra strada.
    """

    def __init__(
        self,
        project: ProjectModel,
        graph: PlantGraph,
        naming: Naming,
        hangs: dict[str, bool],
        lines: PlantLines,
        gaps: Sequence[RuleGap] = (),
    ) -> None:
        self.project = project
        self.graph = graph
        self.naming = naming
        self.circuits = {item.id: item.name for item in project.networks}
        self.hangs = hangs
        """Chi pende dal tubo con una propria derivazione invece di starci sopra."""

        self.lines = lines
        """Le linee idrauliche e l'indirizzo di ogni pezzo (D-105)."""

        self.gaps = tuple(gaps)
        """Dove una regola si e' applicata e il catalogo non aveva il pezzo."""

    # --- i nomi ---------------------------------------------------------------

    def sigla(self, component_id: str) -> str:
        return self.graph.node(component_id).sigla

    def named(self, component_id: str) -> str:
        node = self.graph.node(component_id)
        return f"**{node.sigla}** {node.name}"

    def fluid(self, medium: str) -> str:
        return self.naming.name_of_medium(medium)

    def family(self, function: str) -> str:
        """Come si chiama in italiano un pezzo che fa quel mestiere."""
        return self.naming.family_of((function,), function).name

    def circuit(self, network_id: str) -> str:
        return self.circuits[network_id]

    def fluids_of(self, component_id: str) -> str:
        node = self.graph.node(component_id)
        return ", ".join(self.fluid(item) for item in node.media) or "nessuno"

    def held_by(self, component_id: str) -> str:
        """Che acqua tiene in serbo un serbatoio, se ne tiene una.

        Va detto sul nodo: e' cio' che rende visibile a occhio uno scarico finito
        sul circuito sbagliato — un bollitore che tiene acqua calda sanitaria e
        ha lo scarico sul riscaldamento si vede leggendo due righe.
        """
        held = self.graph.node(component_id).stored_medium
        return "" if held is None else f" · tiene in serbo {self.fluid(held)}"

    # --- le linee e gli indirizzi (D-105) --------------------------------------

    def address(self, component_id: str) -> str | None:
        return self.lines.addresses.get(component_id)

    def addressed(self, component_id: str) -> str:
        """Indirizzo e sigla insieme: e' cosi' che si cita un punto."""
        found = self.address(component_id)
        node = self.graph.node(component_id)
        if found is None:
            return f"**{node.sigla}** {node.name}"
        return f"**{found} · {node.sigla}** {node.name}"

    def closes_its_ring(self, line: HydraulicLine) -> bool:
        """La linea finisce dove la sua stessa acqua riparte: il giro si richiude.

        Se dal nodo finale esce una tubazione della stessa rete, quel nodo e'
        il punto in cui il circuito torna su se' stesso. Se non ne esce nessuna
        — l'acqua fredda che entra in un accumulo — e' un innesto, non un anello.
        """
        tail = line.node_ids[-1]
        return any(
            self.graph.pipe(connection_id).leaves.component_id == tail
            for connection_id in self.lines.run_pipes.get(line.network_id, ())
        )

    def foreign(self, line: HydraulicLine, component_id: str) -> bool:
        """Il pezzo sta sulla linea ma l'indirizzo glielo ha dato un'altra."""
        return self.lines.owner.get(component_id) != line.name

    def arriving_lines(self, line: HydraulicLine, component_id: str) -> list[HydraulicLine]:
        """Le altre linee che finiscono su questo nodo."""
        return [
            other
            for other in self.lines.lines
            if other.name != line.name
            and other.node_ids[-1] == component_id
            and self.foreign(other, component_id)
        ]

    def departing_branches(self, line: HydraulicLine, component_id: str) -> list[HydraulicLine]:
        """Le diramazioni che si staccano da questo nodo della linea."""
        return [
            other
            for other in self.lines.lines
            if other.branch_of is not None
            and other.name != line.name
            and other.node_ids[0] == component_id
            and self.lines.owner.get(component_id) == line.name
        ]


VOWELS = "aeiouAEIOU"


def on_the(words: str) -> str:
    """«sull'acqua di riscaldamento», «sul gas metano»: si scrive in italiano."""
    return f"sull'{words}" if words[:1] in VOWELS else f"sul {words}"


def the(words: str) -> str:
    """«l'acqua di riscaldamento», «il gas metano»."""
    return f"l'{words}" if words[:1] in VOWELS else f"il {words}"


# --- le parti del documento ---------------------------------------------------


def head(pen: Pen) -> list[str]:
    return [
        "# Il grafo dell'impianto",
        "",
        f"> **Cosa approvi qui.** L'impianto — {pen.project.metadata.project_name} —",
        "> scritto invece che disegnato: ogni pezzo con la propria sigla, ogni tubazione",
        "> fra due pezzi, e la passeggiata che parte dalle sorgenti e segue l'acqua fino a",
        "> dove il giro si richiude.",
        ">",
        "> **Perche' non un disegno.** Un disegno prova come l'impianto e' stato messo sul",
        "> foglio. Qui la domanda e' un'altra: **il pezzo giusto e' nel punto giusto, sul",
        "> tubo giusto?** Quella si legge, non si guarda. E con una sigla per pezzo puoi",
        "> correggere puntando — «questo qui e' nel posto sbagliato» — invece di",
        "> descrivere a parole dove guardare.",
        "",
        "---",
        "",
        "## Come si legge",
        "",
        "- **Ogni linea idraulica ha un nome**, come una strada: la famiglia dice che acqua",
        "  porta e da che parte va — `CP.01` e' la prima mandata primaria — e la tabella",
        "  accanto dice da dove a dove va. Dove una linea si sdoppia, la principale tiene il",
        "  nome nudo e i rami prendono una lettera (`RP.01a`); dove due linee si incontrano,",
        "  la principale tira dritto e la secondaria muore su quel nodo.",
        "- **Ogni pezzo e' un nodo numerato lungo la sua linea**, e quello e' il suo",
        "  indirizzo: `CP.01.N.02` e' il secondo nodo della prima mandata primaria. Cio' che",
        "  pende da uno stacco e' un **civico** del nodo: `CP.01.N.02.1`.",
        "- **La sigla resta** (`VI-02`): dice che cosa e' il pezzo, e serve alla distinta.",
        "  L'indirizzo dice dove sta. Sulla tavola convivono, e per citare un punto basta",
        "  uno dei due. Le sigle che hai gia' scritto tu restano come le hai scritte.",
        "- **Ogni tubazione fra due pezzi e' un arco**, e porta il proprio fluido.",
        "- **Ogni attacco e' un braccio numerato**, come in un incrocio stradale: un volano",
        "  a quattro attacchi e' un nodo solo con quattro bracci, contati nell'ordine in cui",
        "  il pezzo li dichiara.",
        "- **Un braccio su cui convergono piu' tubazioni e' un incrocio**, e le tubazioni che",
        "  ci arrivano si contano.",
        "- **Non e' un albero, e' un anello.** Un circuito si chiude su se' stesso: dove",
        "  succede, la lettura lo dice e non si interrompe.",
        "",
    ]


def where_it_starts(pen: Pen) -> list[str]:
    starts = [
        f"{pen.named(item.start)}, {on_the(pen.fluid(item.medium))}"
        for item in pen.graph.readings
        if item.kind == "source"
    ]
    stores = [
        f"{pen.named(item.start)}, dove nasce {the(pen.fluid(item.medium))}"
        for item in pen.graph.readings
        if item.kind == "store"
    ]
    lines = [
        "## Da dove si comincia a contare",
        "",
        "Non dall'ordine in cui il modello elenca i pezzi, che e' un fatto di come e'",
        "scritto e non dell'impianto: **dalle sorgenti**, seguendo il fluido. La prima",
        "valvola che si incontra uscendo dal generatore e' la numero uno della sua",
        "famiglia. Sono sorgenti chi il calore lo produce e il punto da cui l'acqua entra",
        "nell'edificio; si riconoscono da cio' che ogni pezzo dichiara di saper fare, mai",
        "da un elenco di nomi — un impianto con una caldaia al posto della pompa di calore",
        "comincia esattamente allo stesso modo.",
        "",
        "Qui si parte da:",
        "",
        *[f"- {item}" for item in starts],
        *[f"- {item}" for item in stores],
        "",
        "**Costo di questa scelta, detto subito:** se domani si aggiunge un pezzo vicino a",
        "una sorgente, i numeri della sua famiglia a valle scalano tutti di uno. E' normale",
        "per un documento che si rigenera a ogni revisione; cio' che non cambia mai e' che",
        "lo stesso impianto dia sempre le stesse sigle, comunque sia scritto il modello che",
        "lo descrive.",
        "",
    ]
    return lines


def families(pen: Pen) -> list[str]:
    named = {entry.prefix: entry.name for entry in pen.naming.families}
    used = {node.sigla.rsplit("-", 1)[0] for node in pen.graph.nodes}
    rows: list[str] = []
    for prefix in sorted(used):
        if prefix in named:
            rows.append(f"| **{prefix}** | {named[prefix]} |")
            continue
        what = sorted(
            {
                node.family
                for node in pen.graph.nodes
                if node.sigla.rsplit("-", 1)[0] == prefix
            }
        )
        rows.append(
            f"| **{prefix}** | {', '.join(what)} — sigla che hai scelto tu nel modello |"
        )
    return [
        "## Le famiglie delle sigle",
        "",
        "La sigla di un pezzo dice a quale famiglia appartiene, e la famiglia si legge dal",
        "mestiere che quel pezzo dichiara di fare — mai dal suo nome. Aggiungere una",
        "famiglia vuol dire aggiungere una riga a una tabella, non toccare il programma.",
        "",
        "| Sigla | Famiglia |",
        "|---|---|",
        *rows,
        "",
    ]


def lines_table(pen: Pen) -> list[str]:
    rows: list[str] = []
    for line in pen.lines.lines:
        head = pen.sigla(line.node_ids[0])
        tail = pen.sigla(line.node_ids[-1])
        stem = f" · si stacca da {line.branch_of}" if line.branch_of else ""
        rows.append(
            f"| **{line.name}** | {line.family_name}{stem} | {head} | {tail} |"
        )
    lines = [
        "## Le linee",
        "",
        "Le tubazioni dell'impianto, lette come strade: ogni linea parte da una macchina,",
        "arriva alla prossima, e i pezzi in mezzo sono i suoi nodi numerati. La famiglia",
        "dice che acqua porta e da che parte va.",
        "",
        "| Linea | Che acqua porta | Da | A |",
        "|---|---|---|---|",
        *rows,
        "",
    ]
    outside = sorted(
        {
            pen.circuit(item.id)
            for item in pen.project.networks
            if item.domain is not Domain.HYDRONIC
        }
    )
    if outside:
        lines += [
            "Le reti che non portano acqua — " + ", ".join(outside) + " — non hanno",
            "linee idrauliche: i loro pezzi si citano con la sola sigla.",
            "",
        ]
    return lines


def one_line_heading(pen: Pen, line: HydraulicLine) -> list[str]:
    head_id, tail_id = line.node_ids[0], line.node_ids[-1]
    where = f"Da **{pen.sigla(head_id)}** a **{pen.sigla(tail_id)}**, {pen.circuit(line.network_id).lower()}."
    opening = [f"### {line.name} — {line.family_name}", "", where]
    if line.branch_of is not None:
        opening.append(f"Si stacca da **{line.branch_of}**.")
    return [*opening, ""]


def one_line_nodes(pen: Pen, line: HydraulicLine) -> list[str]:
    lines: list[str] = []
    last = len(line.node_ids) - 1
    for index, component_id in enumerate(line.node_ids):
        if not pen.foreign(line, component_id):
            entry = f"{index + 1}. {pen.addressed(component_id)}{pen.held_by(component_id)}"
        elif index == last:
            node = pen.graph.node(component_id)
            said = pen.address(component_id)
            spot = f" ({said})" if said else ""
            if pen.closes_its_ring(line):
                entry = (
                    f"{index + 1}. **{node.sigla}** {node.name} · "
                    f"**qui il giro si richiude su {node.sigla}**{spot}"
                )
            else:
                entry = (
                    f"{index + 1}. **{node.sigla}** {node.name} · "
                    f"**qui ci si innesta su {node.sigla}**, che si e' gia' letto{spot}"
                )
        else:
            node = pen.graph.node(component_id)
            said = pen.address(component_id)
            spot = f", indirizzo {said}" if said else ""
            entry = f"{index + 1}. **{node.sigla}** {node.name} · gia' numerato{spot}"
        lines.append(entry)
        if not pen.foreign(line, component_id):
            for hung in pen.lines.hanging.get(component_id, ()):
                lines.append(f"    - {pen.addressed(hung)} · pende dallo stacco")
            for branch in pen.departing_branches(line, component_id):
                lines.append(
                    f"    - qui si stacca **{branch.name}**, verso "
                    f"**{pen.sigla(branch.node_ids[-1])}**"
                )
            for arriving in pen.arriving_lines(line, component_id):
                lines.append(
                    f"    - qui arriva **{arriving.name}**, da "
                    f"**{pen.sigla(arriving.node_ids[0])}**"
                )
    return [*lines, ""]


def the_lines(pen: Pen) -> list[str]:
    lines = [
        "## Le linee, una per una",
        "",
        "Ogni linea si legge dal suo capo, un nodo alla volta; i civici stanno sotto il",
        "proprio nodo. Dove la linea finisce su un nodo che ha gia' un indirizzo, la",
        "lettura dice quale delle due cose e' successa — **il giro si richiude**, perche'",
        "un circuito e' un anello, oppure **ci si innesta** su un giro gia' letto — e in",
        "nessuno dei due casi il nome della principale cambia. Ogni tubazione",
        "dell'impianto sta su una linea sola.",
        "",
    ]
    for line in pen.lines.lines:
        lines += one_line_heading(pen, line)
        lines += one_line_nodes(pen, line)
    return lines


def nodes_table(pen: Pen) -> list[str]:
    rows: list[str] = []
    for node in pen.graph.nodes:
        hanging = " · pende dal tubo con una propria derivazione" if pen.hangs[node.component_id] else ""
        said = pen.address(node.component_id) or "—"
        rows.append(
            f"| {said} | **{node.sigla}** | {node.name}{hanging}"
            f"{pen.held_by(node.component_id)} | {pen.fluids_of(node.component_id)} |"
        )
    return [
        "## I nodi",
        "",
        "Nell'ordine in cui la passeggiata li incontra, che e' l'ordine in cui sono stati",
        "numerati. L'indirizzo dice dove sta il pezzo; la sigla che cos'e'.",
        "",
        "| Indirizzo | Sigla | Che cos'e' | Su quale fluido |",
        "|---|---|---|---|",
        *rows,
        "",
    ]


def crossings(pen: Pen) -> list[str]:
    rows: list[str] = []
    for node, arm in pen.graph.crossings:
        arriving = ", ".join(
            pen.named(pen.graph.pipe(item).other_end(node.component_id, arm.port_id).component_id)
            for item in arm.pipes
        )
        rows.append(
            f"| {pen.named(node.component_id)} | braccio {arm.number} "
            f"| {len(arm.pipes)} | {arriving} |"
        )
    if not rows:
        return [
            "## Gli incroci",
            "",
            "Nessuno: su questo impianto ogni attacco porta una sola tubazione.",
            "",
        ]
    return [
        "## Gli incroci",
        "",
        "Un attacco su cui converge piu' di una tubazione. E' il punto in cui due rami si",
        "uniscono, e va guardato: e' li' che si decide se il ritorno di una zona rientra",
        "dove deve.",
        "",
        "| Su quale pezzo | Su quale braccio | Quante tubazioni | Che cosa ci arriva |",
        "|---|---|---|---|",
        *rows,
        "",
    ]


def silences(pen: Pen) -> list[str]:
    lines = [
        "## Quello che il grafo non tace",
        "",
        "Le cose che un elenco muto lascerebbe scoprire in cantiere.",
        "",
    ]
    free = pen.graph.free_arms
    if free:
        lines += [
            "**Attacchi su cui non arriva nessuna tubazione.** Un attacco libero non e' per",
            "forza un errore — un bollitore puo' essere disegnato con l'acqua sanitaria",
            "ancora da collegare — ma non deve poter passare inosservato.",
            "",
            "| Su quale pezzo | Quale braccio | Che cosa ci passerebbe |",
            "|---|---|---|",
            *[
                f"| {pen.named(node.component_id)} | braccio {arm.number} "
                f"| {pen.fluid(arm.medium)} |"
                for node, arm in free
            ],
            "",
        ]
    else:
        lines += [
            "**Attacchi liberi:** nessuno. Ogni attacco di ogni pezzo porta la sua",
            "tubazione.",
            "",
        ]
    if pen.graph.unreached:
        lines += [
            "**Pezzi che nessuna sorgente raggiunge.** Non si arriva fin li' ne' da chi",
            "produce il fluido ne' dal punto in cui entra nell'edificio.",
            "",
            *[f"- {pen.named(item)}" for item in pen.graph.unreached],
            "",
        ]
    else:
        lines += [
            "**Pezzi che nessuna sorgente raggiunge:** nessuno. Partendo dalle sorgenti si",
            "arriva a ogni pezzo dell'impianto.",
            "",
        ]
    if pen.graph.unread_pipes:
        lines += [
            "**Tubazioni che nessuna passeggiata attraversa.** Ce ne sono "
            f"{len(pen.graph.unread_pipes)}: e' un giro che il documento non sa raccontare, "
            "e va guardato.",
            "",
        ]
    else:
        lines += [
            "**Tubazioni non lette:** nessuna. Ogni tubazione compare nella passeggiata.",
            "",
        ]
    return lines + open_points(pen)


def open_points(pen: Pen) -> list[str]:
    """Cio' che serviva e che non si e' potuto proporre, detto sul nodo.

    Una regola si applicava — il pezzo la chiedeva davvero — e il catalogo non
    aveva niente da offrire su quel fluido. Sta qui, e non in un documento a
    parte, per la ragione per cui sta qui anche un attacco senza tubazione:
    e' un silenzio, e si legge sul pezzo a cui manca qualcosa.
    """
    if not pen.gaps:
        return [
            "**Punti aperti:** nessuno. Per ogni accessorio che le regole hanno chiesto, il",
            "catalogo aveva il pezzo adatto al fluido di quella tubazione.",
            "",
        ]
    return [
        "**Punti aperti: qui una regola si applicava e il catalogo non aveva niente da",
        "offrire.** Non e' una dimenticanza del disegno: e' una scelta che torna al",
        "progettista.",
        "",
        *[
            f"- **manca {pen.family(gap.missing_function).lower()}** su "
            f"{pen.named(gap.anchor.component_id)}: servirebbe, e in catalogo non c'e' "
            f"nessun pezzo che lo faccia {on_the(pen.fluid(gap.medium))}. Va deciso dal "
            f"progettista."
            for gap in pen.gaps
        ],
        "",
    ]


def render(pen: Pen) -> str:
    lines = [
        *head(pen),
        "---",
        "",
        *where_it_starts(pen),
        "---",
        "",
        *families(pen),
        "---",
        "",
        *lines_table(pen),
        "---",
        "",
        *nodes_table(pen),
        "---",
        "",
        *crossings(pen),
        "---",
        "",
        *the_lines(pen),
        "---",
        "",
        *silences(pen),
        "---",
        "",
        "## Cosa ti stiamo chiedendo",
        "",
        "Di scorrere le linee e dirci, per ogni pezzo: **e' quello giusto, ed e' nel",
        "punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito sbagliato",
        "si vede da qui, senza aprire nient'altro — e per segnalarcelo bastano",
        "l'indirizzo o la sigla.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build(
    project: ProjectModel,
    catalog: ComponentRegistry,
    naming: Naming,
    gaps: Sequence[RuleGap] = (),
    line_naming: LineNaming | None = None,
) -> str:
    graph = read_plant(project, catalog, naming)
    lines = read_lines(
        project,
        catalog,
        graph,
        line_naming if line_naming is not None else LineNaming.from_directory(NAMING),
    )
    hangs = {
        item.id: catalog.get(item.definition_id).attachment
        is ComponentTrait.ATTACHMENT_BRANCH
        for item in project.components
    }
    return render(Pen(project, graph, naming, hangs, lines, gaps))


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    target = Path(arguments[0]) if arguments else DOCUMENT
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    naming = Naming.from_directory(NAMING)
    # I punti aperti si leggono facendo lavorare le regole sull'impianto
    # essenziale: sono le richieste che il catalogo non ha saputo servire, e
    # restano tali anche sul modello gia' completato.
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog)
    _, _, gaps = saturate(load_project(ESSENTIAL), catalog, rules)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        build(load_project(PLANT), catalog, naming, gaps), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
