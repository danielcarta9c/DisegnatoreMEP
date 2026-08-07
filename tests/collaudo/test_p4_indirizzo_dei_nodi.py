"""Collaudo indipendente — Pacchetto A (§3bis-A): l'indirizzo dei nodi (D-105).

Prove scritte da zero dal collaudatore a contesto separato, piu' dure di quelle
di sviluppo: permutazioni combinate su tutti e sei gli impianti confrontando il
dump completo della lettura e il documento intero, verifica strutturale delle
regole della strada su ogni linea di ogni impianto, e i documenti pubblicati
ripetuti dai generatori senza una riga di differenza.

I criteri, dal contratto:
1. la famiglia di una linea si legge SOLO dalla tabella di dati in `naming/`
   (fluido, mestiere della sorgente, verso), mai da un nome;
2. stesso impianto, stessi indirizzi, qualunque ordine del file;
3. innesto: la principale tira dritto, la secondaria muore sul nodo; la
   principale e' quella della prima sorgente (D-098); diramazione: la
   principale tiene il nome nudo, i rami la lettera nell'ordine della
   passeggiata;
4. gli stacchi sono civici del nodo; l'accessorio sull'attacco di servizio di
   una macchina e' un civico della macchina;
5. le sigle dei pezzi restano identiche con e senza la lettura delle linee;
6. il documento: tabella delle linee da→a, lettura per linea coi civici sotto
   il nodo, anelli e innesti dichiarati, italiano senza identificativi interni;
7. i documenti pubblicati sono la rigenerazione corrente.
"""

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest
from helpers import (
    NAMING_DIR,
    PROVE_DIR,
    ROOT,
    catalog,
    graph_dump,
    naming,
    permuted,
    read,
    rules,
)

from disegnatore_mep.graph import (
    LineNaming,
    NamingError,
    PlantGraph,
    PlantLines,
    read_lines,
)
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import RuleGap

CAT = catalog()
NAM = naming()
REG = rules()
REG.cross_check(CAT)
LINEE = LineNaming.from_directory(NAMING_DIR)

COMPLETA = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
ESSENZIALE = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
GENERATORE = ROOT / "examples" / "graph" / "build_plant_graph.py"
GRAFI_DIR = ROOT / "docs" / "prodotto" / "grafi-di-prova"
DOCUMENTO = ROOT / "docs" / "prodotto" / "GRAFO_IMPIANTO.md"

PROVA = sorted(PROVE_DIR.glob("prova-*.json"))
IMPIANTI = [*PROVA, COMPLETA]

OGNI_IMPIANTO = pytest.mark.parametrize(
    "plant", IMPIANTI, ids=[item.stem for item in IMPIANTI]
)

INDIRIZZO = re.compile(r"^[A-Z]{2,4}\.\d{2}[a-z]?\.N\.\d{2}(\.\d+)?$")
NOME_NUDO = re.compile(r"^[A-Z]{2,4}\.\d{2}$")
NOME_RAMO = re.compile(r"^([A-Z]{2,4}\.\d{2})([a-z])$")

SEMI = (11, 23, 37, 59, 71)
"""Semi diversi da quelli delle prove di sviluppo, permutazioni comunque
combinate: tubazioni, pezzi e reti rimescolati insieme."""


# --- gli attrezzi -----------------------------------------------------------------


_COMPLETATI: dict[str, tuple[ProjectModel, tuple[RuleGap, ...]]] = {}


def completato(plant: Path) -> tuple[ProjectModel, tuple[RuleGap, ...]]:
    key = str(plant)
    if key not in _COMPLETATI:
        done, _, gaps = saturate(load_project(plant), CAT, REG)
        _COMPLETATI[key] = (done, tuple(gaps))
    return _COMPLETATI[key]


def lettura(model: ProjectModel, table: LineNaming = LINEE) -> tuple[PlantGraph, PlantLines]:
    graph = read(model, CAT)
    return graph, read_lines(model, CAT, graph, table)


def dump_lettura(lines: PlantLines) -> dict[str, object]:
    """Il dump completo della lettura per linea: ogni campo di ogni linea.

    Le tubazioni del percorso si confrontano come insieme per rete: il loro
    ordine nella tupla segue l'ordine del file e nessuna lettura lo usa
    (osservazione non bloccante del collaudo).
    """
    return {
        "linee": [
            (
                item.name,
                item.family_prefix,
                item.family_name,
                item.network_id,
                item.direction,
                item.branch_of,
                item.node_ids,
            )
            for item in lines.lines
        ],
        "owner": dict(lines.owner),
        "indirizzi": dict(lines.addresses),
        "appesi": dict(lines.hanging),
        "percorso": {net: frozenset(pipes) for net, pipes in lines.run_pipes.items()},
    }


def sigla(graph: PlantGraph, component_id: str) -> str:
    return graph.node(component_id).sigla


_GENERATORE: list[ModuleType] = []


def generatore() -> ModuleType:
    """Lo script pubblicato dei grafi, caricato dal suo file: si collauda lui."""
    if not _GENERATORE:
        spec = importlib.util.spec_from_file_location("build_plant_graph", GENERATORE)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _GENERATORE.append(module)
    return _GENERATORE[0]


def documento(model: ProjectModel, gaps: tuple[RuleGap, ...]) -> str:
    made = generatore().build(model, CAT, NAM, gaps)
    assert isinstance(made, str)
    return made


def documento_pubblicato(plant: Path) -> str:
    path = DOCUMENTO if plant == COMPLETA else GRAFI_DIR / f"{plant.stem}.md"
    return path.read_text(encoding="utf-8")


def modello_del_documento(plant: Path) -> tuple[ProjectModel, tuple[RuleGap, ...]]:
    """Il modello da cui il documento pubblicato nasce, come i generatori lo
    leggono: i cinque impianti di prova passano dalle regole, l'impianto di
    accettazione e' gia' completo e i suoi punti aperti si leggono facendo
    lavorare le regole sull'impianto essenziale."""
    if plant == COMPLETA:
        return load_project(COMPLETA), completato(ESSENZIALE)[1]
    return completato(plant)


def sezioni(text: str) -> dict[str, str]:
    """Il corpo di ogni sezione «### LINEA — famiglia», per nome di linea."""
    found: dict[str, str] = {}
    for part in text.split("\n### ")[1:]:
        title, _, body = part.partition("\n")
        found[title.split(" — ")[0]] = body.split("\n### ")[0].split("\n---")[0]
    return found


def chiude_il_giro(graph: PlantGraph, lines: PlantLines, name: str) -> bool:
    """Dal nodo finale riparte una tubazione della stessa rete: e' un anello."""
    line = lines.line(name)
    tail = line.node_ids[-1]
    return any(
        graph.pipe(connection_id).leaves.component_id == tail
        for connection_id in lines.run_pipes.get(line.network_id, ())
    )


# --- 1. la famiglia e' un dato: si legge dalla tabella, mai da un nome ------------


@pytest.mark.parametrize("plant", [PROVA[0], PROVA[4]], ids=["prova-1", "prova-5"])
def test_ribattezzare_una_famiglia_nei_dati_trascina_gli_indirizzi(
    plant: Path, tmp_path: Path
) -> None:
    """La sigla CP vive in `naming/lines.json`: cambiata la' — e solo la' — ogni
    indirizzo della famiglia segue, rami compresi, e nient'altro si muove."""
    table = json.loads((NAMING_DIR / "lines.json").read_text(encoding="utf-8"))
    for row in table["families"]:
        if row["prefix"] == "CP":
            row["prefix"] = "MC"
            row["name"] = "mandata calda ribattezzata"
    (tmp_path / "lines.json").write_text(json.dumps(table), encoding="utf-8")

    done, _ = completato(plant)
    _, base = lettura(done)
    _, renamed = lettura(done, LineNaming.from_directory(tmp_path))

    def segue(value: str) -> str:
        return "MC" + value[2:] if value.startswith("CP.") else value

    assert [
        (item.name, item.family_prefix, item.family_name, item.branch_of)
        for item in renamed.lines
    ] == [
        (
            segue(item.name),
            "MC" if item.family_prefix == "CP" else item.family_prefix,
            "mandata calda ribattezzata" if item.family_prefix == "CP" else item.family_name,
            segue(item.branch_of) if item.branch_of else None,
        )
        for item in base.lines
    ]
    assert renamed.addresses == {key: segue(value) for key, value in base.addresses.items()}
    assert renamed.owner == {key: segue(value) for key, value in base.owner.items()}
    assert renamed.hanging == base.hanging
    assert [item.node_ids for item in renamed.lines] == [item.node_ids for item in base.lines]


@pytest.mark.parametrize(
    ("prefix", "culprit"),
    [
        ("RP", ("heating_water", "generator", "return")),
        ("ACS", ("domestic_hot_water", "store", "supply")),
    ],
    ids=["senza-ritorno-primario", "senza-acqua-calda-sanitaria"],
)
def test_una_voce_tolta_dalla_tabella_ferma_nominando_il_colpevole(
    prefix: str, culprit: tuple[str, str, str], tmp_path: Path
) -> None:
    table = json.loads((NAMING_DIR / "lines.json").read_text(encoding="utf-8"))
    table["families"] = [row for row in table["families"] if row["prefix"] != prefix]
    (tmp_path / "lines.json").write_text(json.dumps(table), encoding="utf-8")

    done, _ = completato(PROVA[0])
    with pytest.raises(NamingError) as caught:
        lettura(done, LineNaming.from_directory(tmp_path))
    for word in culprit:
        assert word in str(caught.value), word


@OGNI_IMPIANTO
def test_il_nome_di_fantasia_di_un_pezzo_non_cambia_nulla(plant: Path) -> None:
    """Sigle riscritte dal progettista e reti ribattezzate: la lettura delle
    linee e' identica byte per byte, perche' niente si legge dai nomi."""
    done, _ = completato(plant)
    _, base = lettura(done)
    fancy = done.model_copy(
        update={
            "components": [
                item.model_copy(update={"tag": f"ZZ-{index + 1:02d}" if item.tag else None})
                for index, item in enumerate(done.components)
            ],
            "networks": [
                item.model_copy(update={"name": f"Rete di fantasia {index + 1}"})
                for index, item in enumerate(done.networks)
            ],
        }
    )
    _, renamed = lettura(fancy)
    assert dump_lettura(renamed) == dump_lettura(base)


# --- 2. stesso impianto, stessi indirizzi, qualunque ordine del file --------------


@OGNI_IMPIANTO
def test_la_lettura_intera_non_dipende_dall_ordine_del_file(plant: Path) -> None:
    """Permutazioni combinate — tubazioni, pezzi e reti insieme — su piu' semi,
    confrontando il dump completo della lettura, non le sole sigle."""
    done, _ = completato(plant)
    _, lines = lettura(done)
    base = dump_lettura(lines)
    for seed in SEMI:
        _, other = lettura(permuted(done, seed))
        assert dump_lettura(other) == base, seed


@OGNI_IMPIANTO
def test_il_documento_intero_non_dipende_dall_ordine_del_file(plant: Path) -> None:
    """Dal file rimescolato, per tutta la catena — regole comprese — fino al
    documento: lo stesso testo, riga per riga."""
    raw = load_project(plant)
    done, _, gaps = saturate(raw, CAT, REG)
    base = documento(done, tuple(gaps))
    for seed in (7, 13):
        shuffled = permuted(raw, seed)
        done_again, _, gaps_again = saturate(shuffled, CAT, REG)
        assert documento(done_again, tuple(gaps_again)) == base, seed


# --- 3. le regole della strada, su ogni linea di ogni impianto --------------------


@OGNI_IMPIANTO
def test_la_principale_tira_dritto_e_i_forestieri_stanno_solo_ai_capi(plant: Path) -> None:
    """I nodi di una linea si numerano di seguito, senza salti, nell'ordine
    della passeggiata; un nodo che ha l'indirizzo di un'altra linea puo' stare
    solo al capo o alla fine — mai in mezzo, perche' la principale non si
    spezza dove qualcuno le muore addosso."""
    done, _ = completato(plant)
    _, lines = lettura(done)
    for line in lines.lines:
        owned = [
            item for item in dict.fromkeys(line.node_ids) if lines.owner.get(item) == line.name
        ]
        assert [lines.addresses[item] for item in owned] == [
            f"{line.name}.N.{index:02d}" for index in range(1, len(owned) + 1)
        ], line.name
        foreign = {
            item
            for item in line.node_ids
            if lines.owner.get(item) != line.name
        }
        assert foreign <= {line.node_ids[0], line.node_ids[-1]}, line.name


@OGNI_IMPIANTO
def test_la_secondaria_muore_su_un_nodo_che_resta_della_principale(plant: Path) -> None:
    done, _ = completato(plant)
    _, lines = lettura(done)
    for line in lines.lines:
        tail = line.node_ids[-1]
        if lines.owner.get(tail) == line.name:
            continue
        principale = lines.line(lines.owner[tail])
        assert tail in principale.node_ids, line.name
        assert lines.addresses[tail].startswith(f"{principale.name}.N."), line.name


@OGNI_IMPIANTO
def test_i_rami_prendono_la_lettera_della_base_nell_ordine_della_passeggiata(
    plant: Path,
) -> None:
    """Il nome di un ramo e' il nome nudo della base piu' una lettera; le
    lettere di ogni base sono consecutive dalla `a`, nell'ordine in cui la
    passeggiata ha incontrato le diramazioni."""
    done, _ = completato(plant)
    _, lines = lettura(done)
    letters: dict[str, list[str]] = {}
    for line in lines.lines:
        if line.branch_of is None:
            assert NOME_NUDO.match(line.name), line.name
            continue
        matched = NOME_RAMO.match(line.name)
        assert matched, line.name
        assert matched.group(1) == line.branch_of, line.name
        assert NOME_NUDO.match(line.branch_of), line.name
        assert any(item.name == line.branch_of for item in lines.lines), line.name
        letters.setdefault(line.branch_of, []).append(matched.group(2))
    for base, found in letters.items():
        assert found == [chr(ord("a") + index) for index in range(len(found))], base


def test_nella_cascata_la_prima_sorgente_vince_e_le_lettere_restano_piatte() -> None:
    """Prova 5, tre macchine in cascata (D-098, D-105): `CP.01` parte dalla
    prima e tira dritto; le mandate delle altre muoiono su nodi suoi; sul
    ritorno comune `RP.01` arriva alla prima, `RP.01a` alla seconda, `RP.01b`
    alla terza — e la `b`, pur staccandosi da un nodo di `RP.01a`, porta la
    lettera della stessa strada, come la bis e la ter di una statale."""
    done, _ = completato(PROVA[4])
    graph, lines = lettura(done)

    assert sigla(graph, lines.line("CP.01").node_ids[0]) == "PDC-01"
    assert lines.addresses[lines.line("CP.01").node_ids[0]] == "CP.01.N.01"
    for name, head in (("CP.02", "PDC-02"), ("CP.03", "PDC-03")):
        line = lines.line(name)
        assert sigla(graph, line.node_ids[0]) == head
        tail = line.node_ids[-1]
        assert lines.owner[tail] == "CP.01", name
        assert tail != lines.line("CP.01").node_ids[-1], name

    principale = lines.line("RP.01")
    assert sigla(graph, principale.node_ids[-1]) == "PDC-01"
    assert lines.line("RP.01a").branch_of == "RP.01"
    assert sigla(graph, lines.line("RP.01a").node_ids[-1]) == "PDC-02"
    assert lines.line("RP.01b").branch_of == "RP.01"
    assert sigla(graph, lines.line("RP.01b").node_ids[-1]) == "PDC-03"
    assert lines.owner[lines.line("RP.01a").node_ids[0]] == "RP.01"
    assert lines.owner[lines.line("RP.01b").node_ids[0]] == "RP.01a"


def test_alla_deviatrice_la_principale_tiene_il_nome_nudo_e_il_ramo_la_lettera() -> None:
    """Impianto di accettazione: la deviatrice e' un nodo di `CP.01`, la linea
    la attraversa e prosegue, e il ramo deviato e' `CP.01a`."""
    done = load_project(COMPLETA)
    graph, lines = lettura(done)
    ramo = lines.line("CP.01a")
    assert ramo.branch_of == "CP.01"
    valvola = ramo.node_ids[0]
    assert sigla(graph, valvola) == "VD-01"
    principale = lines.line("CP.01")
    assert lines.owner[valvola] == "CP.01"
    assert valvola in principale.node_ids
    assert valvola != principale.node_ids[-1]


# --- 4. gli stacchi sono civici del nodo ------------------------------------------


@OGNI_IMPIANTO
def test_ogni_pezzo_ha_un_solo_indirizzo_nella_grammatica_della_strada(plant: Path) -> None:
    done, _ = completato(plant)
    _, lines = lettura(done)
    assert set(lines.addresses) == {item.id for item in done.components}
    values = list(lines.addresses.values())
    assert len(values) == len(set(values))
    for value in values:
        assert INDIRIZZO.match(value), value


@OGNI_IMPIANTO
def test_la_catena_appesa_porta_i_civici_del_proprio_nodo(plant: Path) -> None:
    """Chi pende da uno stacco non e' un nodo di nessuna strada: e' un civico,
    numerato lungo la catena a partire dall'indirizzo del nodo."""
    done, _ = completato(plant)
    _, lines = lettura(done)
    hung_everywhere: set[str] = set()
    for node, chain in lines.hanging.items():
        hung_everywhere |= set(chain)
        root = lines.addresses.get(node)
        assert root is not None, node
        for index, hung in enumerate(chain, start=1):
            assert lines.addresses[hung] == f"{root}.{index}", hung
    assert hung_everywhere.isdisjoint(lines.owner)


def test_l_accessorio_sull_attacco_di_servizio_e_un_civico_della_macchina() -> None:
    """Prova 1: sfogo e scarico stanno sugli attacchi di servizio del
    serbatoio, e i loro indirizzi sono i civici del nodo del serbatoio."""
    done, _ = completato(PROVA[0])
    graph, lines = lettura(done)
    machine = next(item.id for item in done.components if item.definition_id == "buffer-combined")
    root = lines.addresses[machine]
    assert INDIRIZZO.match(root) and "." not in root.split(".N.")[1], root
    chain = lines.hanging[machine]
    served: dict[str, str] = {}
    for arm in graph.node(machine).arms:
        if arm.serves is None:
            continue
        for connection_id in arm.pipes:
            pipe = graph.pipe(connection_id)
            other = (
                pipe.enters.component_id
                if pipe.leaves.component_id == machine
                else pipe.leaves.component_id
            )
            served[arm.serves] = other
    assert set(served) == {"air_release", "drain"}
    for accessory in served.values():
        assert accessory in chain
        assert lines.addresses[accessory] == f"{root}.{chain.index(accessory) + 1}"


# --- 5. le sigle restano: l'indirizzo convive, non sostituisce --------------------


@OGNI_IMPIANTO
def test_le_sigle_sono_identiche_con_e_senza_la_lettura_delle_linee(plant: Path) -> None:
    done, _ = completato(plant)
    senza = read(done, CAT)
    sigle_senza = {node.component_id: node.sigla for node in senza.nodes}

    graph = read(done, CAT)
    prima = graph_dump(graph)
    _, lines = lettura(done)
    assert graph_dump(graph) == prima
    sigle_con = {node.component_id: node.sigla for node in graph.nodes}
    assert sigle_con == sigle_senza
    for component_id, value in sigle_con.items():
        assert lines.addresses[component_id] != value


# --- 6. il documento: le linee, i civici, gli anelli, l'italiano ------------------


@OGNI_IMPIANTO
def test_il_documento_racconta_ogni_linea_da_dove_a_dove(plant: Path) -> None:
    model, _ = modello_del_documento(plant)
    graph, lines = lettura(model)
    text = documento_pubblicato(plant)
    assert "| Linea | Che acqua porta | Da | A |" in text
    for line in lines.lines:
        stem = f" · si stacca da {line.branch_of}" if line.branch_of else ""
        row = (
            f"| **{line.name}** | {line.family_name}{stem} "
            f"| {sigla(graph, line.node_ids[0])} | {sigla(graph, line.node_ids[-1])} |"
        )
        assert row in text, row
        assert f"### {line.name} — {line.family_name}" in text, line.name


@OGNI_IMPIANTO
def test_il_documento_mette_i_civici_sotto_il_proprio_nodo(plant: Path) -> None:
    model, _ = modello_del_documento(plant)
    graph, lines = lettura(model)
    text = documento_pubblicato(plant)
    parts = sezioni(text)
    for node, chain in lines.hanging.items():
        body = parts[lines.owner[node]]
        root = lines.addresses[node]
        assert f"**{root} · {sigla(graph, node)}**" in body, node
        for index, hung in enumerate(chain, start=1):
            bullet = f"- **{root}.{index} · {sigla(graph, hung)}**"
            assert bullet in body, bullet
            row = next(line for line in body.splitlines() if bullet in line)
            assert "pende dallo stacco" in row, bullet
    for component_id, address in lines.addresses.items():
        assert f"| {address} | **{sigla(graph, component_id)}** |" in text, address


@OGNI_IMPIANTO
def test_il_documento_dichiara_anelli_e_innesti_dove_le_linee_finiscono(plant: Path) -> None:
    model, _ = modello_del_documento(plant)
    graph, lines = lettura(model)
    parts = sezioni(documento_pubblicato(plant))
    for line in lines.lines:
        tail = line.node_ids[-1]
        body = parts[line.name]
        ring = f"qui il giro si richiude su {sigla(graph, tail)}"
        graft = f"qui ci si innesta su {sigla(graph, tail)}"
        if lines.owner.get(tail) == line.name:
            assert ring not in body and graft not in body, line.name
        elif chiude_il_giro(graph, lines, line.name):
            assert ring in body, line.name
        else:
            assert graft in body, line.name
        head = line.node_ids[0]
        if lines.owner.get(head) != line.name:
            assert f"gia' numerato, indirizzo {lines.addresses[head]}" in body, line.name


INGLESE = (
    "the",
    "and",
    "with",
    "from",
    "water",
    "valve",
    "pump",
    "supply",
    "return",
    "node",
    "pipe",
    "port",
    "source",
    "store",
    "buffer",
    "cylinder",
    "radiator",
    "manifold",
    "heat",
    "ring",
    "loop",
    "branch",
    "line",
    "reading",
    "safety",
    "drain",
    "vent",
    "generator",
)
"""Parole che, se comparissero, direbbero che un'etichetta interna e' passata.

«Boiler» non c'e' apposta: e' il nome italiano di mestiere che il catalogo
dichiara per lo scaldacqua («Boiler in pompa di calore»), un dato per il
committente e non un'etichetta interna."""


@OGNI_IMPIANTO
def test_il_documento_parla_italiano_senza_identificativi_interni(plant: Path) -> None:
    """Su tutti e sei i documenti: nessun identificativo di modello o di
    catalogo con la forma di un identificativo, nessun vocabolo tecnico
    interno, nessuna parola d'inglese, nessun nome di file."""
    model, _ = modello_del_documento(plant)
    text = documento_pubblicato(plant)

    def come_parola(needle: str, haystack: str) -> bool:
        return re.search(rf"(?<![\w-]){re.escape(needle)}(?![\w-])", haystack) is not None

    shaped: set[str] = set()
    shaped |= {item.id for item in model.components}
    shaped |= {item.id for item in model.networks}
    shaped |= {item.id for item in model.connections}
    shaped |= {item.id for item in model.subsystems}
    shaped |= {item.definition_id for item in model.components}
    shaped |= {item.id for item in CAT.all()}
    for definition in CAT.all():
        shaped |= set(definition.functions)
        shaped |= {str(trait) for trait in definition.traits}
        shaped |= {port.medium for port in definition.ports}
        shaped |= {port.id for port in definition.ports}
    forbidden = {item for item in shaped if "-" in item or "_" in item}
    leaked = sorted(item for item in forbidden if come_parola(item, text))
    assert not leaked, leaked

    lowered = text.lower()
    english = sorted(item for item in INGLESE if come_parola(item, lowered))
    assert not english, english

    for mark in (".json", ".py", ".md", ".svg", "examples/", "docs/", "src/"):
        assert mark not in text, mark


# --- 7. i documenti pubblicati sono la rigenerazione corrente ---------------------


@OGNI_IMPIANTO
def test_il_documento_pubblicato_e_la_rigenerazione_corrente(plant: Path) -> None:
    """Lo stesso generatore pubblicato, rieseguito ora sul modello corrente,
    riscrive il documento pubblicato senza una riga di differenza."""
    model, gaps = modello_del_documento(plant)
    assert documento(model, gaps) == documento_pubblicato(plant)
