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
from disegnatore_mep.graph import Naming, PlantGraph, Reading, Step, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
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
        gaps: Sequence[RuleGap] = (),
    ) -> None:
        self.project = project
        self.graph = graph
        self.naming = naming
        self.circuits = {item.id: item.name for item in project.networks}
        self.hangs = hangs
        """Chi pende dal tubo con una propria derivazione invece di starci sopra."""

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


def arms_in_words(numbers: tuple[int, ...]) -> str:
    said = [f"braccio {item}" for item in numbers]
    if len(said) == 1:
        return said[0]
    return ", ".join(said[:-1]) + " e " + said[-1]


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
        "- **Ogni pezzo e' un nodo** con la propria sigla, macchine e accessori allo stesso",
        "  modo. Le sigle che hai gia' scritto tu restano come le hai scritte.",
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


def nodes_table(pen: Pen) -> list[str]:
    rows: list[str] = []
    for node in pen.graph.nodes:
        hanging = " · pende dal tubo con una propria derivazione" if pen.hangs[node.component_id] else ""
        rows.append(
            f"| **{node.sigla}** | {node.name}{hanging}"
            f"{pen.held_by(node.component_id)} | {pen.fluids_of(node.component_id)} |"
        )
    return [
        "## I nodi",
        "",
        "Nell'ordine in cui la passeggiata li incontra, che e' l'ordine in cui sono stati",
        "numerati.",
        "",
        "| Sigla | Che cos'e' | Su quale fluido |",
        "|---|---|---|",
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


def opening(pen: Pen, reading: Reading) -> list[str]:
    node = pen.graph.node(reading.start)
    fluid = pen.fluid(reading.medium) if reading.medium else "nessun fluido"
    if reading.kind == "source":
        title = f"### Si parte da {node.sigla}, {on_the(fluid)}"
        why = (
            f"{pen.named(reading.start)} e' una sorgente: {node.family.lower()}. "
            f"Da qui {the(fluid)} entra nell'impianto."
        )
    elif reading.kind == "store":
        title = f"### Si riparte da {node.sigla}, dove nasce {the(fluid)}"
        why = (
            f"Nessuna sorgente porta {fluid} da fuori: e' {pen.named(reading.start)} a "
            f"tenerne una riserva, e quindi e' li' che il giro comincia."
        )
    elif reading.kind == "onward":
        title = f"### Si riparte da {node.sigla}, {on_the(fluid)}"
        why = (
            f"Attraversando {pen.named(reading.start)} il fluido cambia nome: quello che "
            f"esce di qui e' {fluid}, e il suo giro si legge a parte."
        )
    else:
        title = f"### Staccato dal resto: {node.sigla}"
        why = (
            "**Nessuna sorgente arriva fin qui.** Questi pezzi non sono raggiunti ne' da "
            "chi produce il fluido ne' dal punto in cui entra nell'edificio: o manca una "
            "tubazione, o manca il pezzo da cui il loro fluido dovrebbe partire. Va deciso "
            "dal progettista."
        )
    lines = [title, "", why, ""]
    if len(reading.departing_arms) > 1:
        lines += [
            f"Da {pen.named(reading.start)} la lettura prosegue su "
            f"{len(reading.departing_arms)} bracci: "
            f"{arms_in_words(reading.departing_arms)}.",
            "",
        ]
    if not reading.steps:
        lines += [
            "Da qui non riparte niente che non sia gia' stato letto: il suo giro compare "
            "piu' su.",
            "",
        ]
    return lines


def step_lines(pen: Pen, reading: Reading) -> list[str]:
    lines: list[str] = []
    circuit = ""
    for step in reading.steps:
        if pen.circuit(step.network_id) != circuit:
            circuit = pen.circuit(step.network_id)
            lines += [f"*{circuit}*", ""] if not lines else ["", f"*{circuit}*", ""]
        lines.append(one_step(pen, step))
        lines += notes_under(pen, step)
    return lines


def one_step(pen: Pen, step: Step) -> str:
    if step.closes_the_ring:
        ending = f" · **qui il giro si richiude su {pen.sigla(step.arrives_at)}**"
    elif step.rejoins:
        ending = (
            f" · **qui ci si innesta su {pen.sigla(step.arrives_at)}**, che si e' gia' letto"
        )
    else:
        ending = ""
    return (
        f"{step.number}. {pen.named(step.departs_from)} · braccio {step.departs_arm} "
        f"→ {pen.named(step.arrives_at)} · braccio {step.arrives_arm}{ending}"
    )


def notes_under(pen: Pen, step: Step) -> list[str]:
    notes: list[str] = []
    arm = next(
        item
        for item in pen.graph.node(step.arrives_at).arms
        if item.number == step.arrives_arm
    )
    if arm.is_a_crossing:
        notes.append(
            f"    - sul braccio {arm.number} di {pen.named(step.arrives_at)} convergono "
            f"{len(arm.pipes)} tubazioni: e' un incrocio"
        )
    if len(step.onward_arms) > 1:
        notes.append(
            f"    - da {pen.named(step.arrives_at)} la lettura prosegue su altri "
            f"{len(step.onward_arms)} bracci: {arms_in_words(step.onward_arms)}"
        )
    return notes


def the_walk(pen: Pen) -> list[str]:
    lines = [
        "## La passeggiata",
        "",
        "Si parte da ogni sorgente e si segue il fluido, un pezzo alla volta. Dove",
        "l'impianto si dirama, la lettura dice su quali bracci prosegue. Dove torna su un",
        "pezzo gia' incontrato dice quale delle due cose e' successa — **il giro si",
        "richiude**, perche' un circuito e' un anello, oppure **ci si innesta** un giro che",
        "si era gia' letto — e in nessuno dei due casi si interrompe. Ogni tubazione",
        "dell'impianto compare esattamente una volta.",
        "",
    ]
    for reading in pen.graph.readings:
        lines += opening(pen, reading)
        lines += step_lines(pen, reading)
        lines.append("")
    return lines


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
        *nodes_table(pen),
        "---",
        "",
        *crossings(pen),
        "---",
        "",
        *the_walk(pen),
        "---",
        "",
        *silences(pen),
        "---",
        "",
        "## Cosa ti stiamo chiedendo",
        "",
        "Di scorrere la passeggiata e dirci, per ogni pezzo: **e' quello giusto, ed e' nel",
        "punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito sbagliato",
        "si vede da qui, senza aprire nient'altro — e per segnalarcelo basta la sigla.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build(
    project: ProjectModel,
    catalog: ComponentRegistry,
    naming: Naming,
    gaps: Sequence[RuleGap] = (),
) -> str:
    graph = read_plant(project, catalog, naming)
    hangs = {
        item.id: catalog.get(item.definition_id).attachment
        is ComponentTrait.ATTACHMENT_BRANCH
        for item in project.components
    }
    return render(Pen(project, graph, naming, hangs, gaps))


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
