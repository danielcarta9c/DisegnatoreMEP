"""Le zone valgono solo per i pezzi grossi (D-120), e i paralleli si impilano.

La correzione e' del PM, ed e' arrivata guardando la prima tavola: «le zone
servono solo per distribuire i macro componenti; le valvole che stanno in mezzo
possono finire dove vogliono, a cavallo fra le due zone o in una delle due».

Il difetto che chiude si vedeva a occhio sull'impianto 1: la **confluenza dei
due ritorni** e i tre raccordi del corredo di rete prendevano una colonna a
testa, quindi venivano letti come passi del processo e ordinati come macchine.
Il gruppo di riempimento del ritorno finiva **all'estrema sinistra del foglio**,
prima delle due pompe di calore, e il ritorno attraversava la tavola due volte
per raggiungerlo — che e' il rilievo I-007 del registro degli input.
"""
# categoria: difende una regola del piano — A2, chi sta in parallelo si impila e chi non e' un pezzo grosso esce dalla fila

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import ZONED_FUNCTIONS, place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PLANTS = ROOT / "examples" / "prova"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

IMPIANTI = sorted(item.name for item in PLANTS.glob("prova-*.json"))
PRIMO = "prova-1-due-pdc-accumulo-combinato.json"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def completato(name: str) -> ProjectModel:
    """L'impianto come esce dalle regole: e' quello che si disegna."""
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog())
    completed, _, _ = saturate(load_project(PLANTS / name), catalog(), rules)
    return completed


def posa(name: str, registry: ComponentRegistry | None = None) -> list[PlacedSymbol]:
    """La posa iniziale dell'impianto, letta con il catalogo che si passa.

    Il catalogo e' un parametro perche' e' li' che vive la **classificazione**:
    chi merita una colonna e chi e' un raccordo lo dicono i mestieri dichiarati,
    e una prova che voglia mostrare cosa succederebbe se la classificazione
    cambiasse deve poterla cambiare.
    """
    used = registry or catalog()
    project = completato(name)
    inline = inline_component_ids(project, used)
    partition = partition_project(project, build_trunks(project, inline))[0]
    return place_sheet(project, partition, used, NOVE_C_A3, inline)


def funzioni(project: ProjectModel, component_id: str) -> frozenset[str]:
    definition = next(
        item.definition_id for item in project.components if item.id == component_id
    )
    return frozenset(catalog().resolve(definition).definition.functions)


QUINTO_APERTO = (
    "APERTO, e marcata rossa apposta. Sulla cascata di tre pompe di calore una "
    "confluenza del secondario resta a sinistra di tutto cio' che unisce: la "
    "sua catena tocca un solo pezzo grosso, quindi non ha una campata dentro "
    "cui distribuirsi e tiene la propria colonna, che l'ordine del processo "
    "porta all'estrema sinistra. Il campo di lavoro e' il solo impianto 1 "
    "(D-116) e il quinto si guarda quando tocca a lui: la riga esiste perche' "
    "il difetto non sia scoperto due volte. Torna verde quando anche le catene "
    "con un estremo solo sanno dove stare."
)


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            item,
            marks=(
                pytest.mark.xfail(strict=True, reason=QUINTO_APERTO)
                if item == "prova-5-cascata-tre-pdc.json"
                else ()
            ),
        )
        for item in IMPIANTI
    ],
)
def test_nessun_raccordo_sta_a_sinistra_di_cio_che_unisce(name: str) -> None:
    """Un raccordo sta **fra** i pezzi che unisce, mai prima di tutti.

    E' la forma misurabile del rilievo del PM: se la confluenza dei ritorni sta
    a sinistra di ogni macchina che vi rientra, il ritorno di quelle macchine
    attraversa la tavola per raggiungerla, e sulla carta si vede subito.
    """
    project = completato(name)
    # Nessun `try`, nessuno `skip` (I-046): un impianto che non si posa e' una
    # regressione, e una regressione non si parcheggia. La posa e' provata a
    # parte, per tutti e cinque, in `test_posa_dei_cinque_impianti.py`.
    placed = posa(name)
    where = {item.component_id: item for item in placed}
    inline = inline_component_ids(project, catalog())
    trunks = build_trunks(project, inline)

    for component_id, item in sorted(where.items()):
        if funzioni(project, component_id) & ZONED_FUNCTIONS:
            continue
        neighbours = {
            other
            for trunk in trunks
            for mine, other in (
                (trunk.start.component_id, trunk.end.component_id),
                (trunk.end.component_id, trunk.start.component_id),
            )
            if mine == component_id and other in where
        }
        if len(neighbours) < 2:
            continue
        vicini = [where[other] for other in sorted(neighbours)]
        assert item.origin.x_mm >= min(other.origin.x_mm for other in vicini) - 1e-9, (
            f"{component_id} sta a sinistra di **tutto** cio' che unisce "
            f"({sorted(neighbours)}): per raggiungerlo, i loro collegamenti "
            f"tornano indietro e attraversano la tavola"
        )


def _colonne(
    placed: list[PlacedSymbol], name: str, registry: ComponentRegistry
) -> tuple[frozenset[float], frozenset[float]]:
    """Le ascisse della **fila** e quelle dei raccordi, dalla stessa posa.

    La fila e' fatta dai pezzi che meritano una zona (D-120): la classificazione
    li riconosce dai mestieri dichiarati, e la posa dice a quale ascissa
    ciascuno sia finito. Due pezzi alla stessa ascissa stanno nella stessa
    colonna, come le due macchine impilate.
    """
    definitions = {item.id: item.definition_id for item in completato(name).components}

    def jobs(item: PlacedSymbol) -> frozenset[str]:
        return frozenset(registry.get(definitions[item.component_id]).functions)

    fila = frozenset(
        round(item.origin.x_mm, 3) for item in placed if jobs(item) & ZONED_FUNCTIONS
    )
    raccordi = frozenset(
        round(item.origin.x_mm, 3)
        for item in placed
        if registry.get(definitions[item.component_id]).is_a_fitting
    )
    return fila, raccordi


def test_i_raccordi_non_prendono_una_colonna_a_testa() -> None:
    """Un raccordo non e' un passo del processo e non tiene una colonna.

    **L'attesa viene dalla classificazione**: le colonne della fila sono quelle
    dei pezzi che il catalogo dichiara degni di una zona (D-120) — chi genera,
    accumula, utilizza, spinge, ripartisce, confina. **La misura viene dalla
    posa**: l'ascissa a cui ciascun pezzo e' finito. La proprieta' e' che
    nessun raccordo sta su una di quelle ascisse: o condivide la colonna di un
    pezzo grosso — la ferramenta compressa dentro la zona, un modo gia' provato
    e buttato — oppure ne apre una propria, e in tutti e due i casi il raccordo
    e' entrato nella fila.

    Nessuna soglia della tavola 1 compare qui: l'unica misura assoluta e'
    l'area di disegno del foglio, che e' del formato e non dell'impianto.

    In coda la prova costruisce la **mutazione negativa** che deve farla
    fallire: lo stesso raccordo che dichiara anche un mestiere da colonna. Se
    la misura non se ne accorgesse, non starebbe misurando cio' che nomina.
    """
    placed = posa(PRIMO)
    largo = max(item.right_mm for item in placed) - min(
        item.origin.x_mm for item in placed
    )
    assert largo <= NOVE_C_A3.drawing_rect_mm.width_mm + 1e-9, (
        f"la posa dell'impianto 1 e' larga {largo:g}mm e non entra nell'area di "
        f"disegno: la gola non puo' prendersi piu' dello spazio che avanza"
    )
    fila, raccordi = _colonne(placed, PRIMO, catalog())
    assert fila and raccordi, (
        "la fixture non ha insieme pezzi grossi e raccordi: la prova non "
        "direbbe niente"
    )
    assert not raccordi & fila, (
        f"alle ascisse {sorted(raccordi & fila)} un raccordo sta in una colonna "
        f"della fila: le colonne sono dei soli pezzi grossi, e i raccordi stanno "
        f"nella gola, fra i pezzi che la loro tratta unisce"
    )

    # La mutazione negativa. Il raccordo resta un raccordo — unisce due
    # tubazioni — ma dichiara anche di ripartire, cioe' un mestiere che merita
    # una zona: la posa gli da' una colonna, la fila si allunga, e la misura
    # qui sopra lo vede.
    promosso = "tee-junction"
    mutato = ComponentRegistry(
        [
            item.model_copy(update={"functions": [*item.functions, "distribution"]})
            if item.id == promosso
            else item
            for item in catalog().all()
        ],
        symbols=SymbolRegistry.from_directory(SYMBOLS),
    )
    assert mutato.get(promosso).is_a_fitting, "la mutazione ha smesso di essere un raccordo"
    fila_mutata, raccordi_mutati = _colonne(posa(PRIMO, mutato), PRIMO, mutato)
    assert len(fila_mutata) > len(fila), (
        "promuovere un raccordo non ha aggiunto nessuna colonna: la mutazione "
        "non e' una mutazione, e la prova non starebbe misurando niente"
    )
    assert raccordi_mutati & fila_mutata, (
        "la misura non si accorge di un raccordo promosso a colonna di un pezzo "
        "grosso: non sta provando la proprieta' che nomina"
    )


def test_due_macchine_in_parallelo_si_impilano() -> None:
    """«Generatori a sinistra, impilati in verticale se sono piu' di uno»
    (**D-041 + D-118**).

    Fino a `DRAW-015` questa riga citava **D-119**, che e' un'altra cosa —
    l'area di rispetto dei raccordi. I generatori a sinistra sono **D-041**,
    l'impilamento di cio' che sta in parallelo e' **D-118** punto 3.

    Non e' estetica: affiancate, il collettore che le serve puo' stare da una
    parte sola, e il ritorno della seconda attraversa la tavola per
    raggiungerlo. Prima capitava per caso — si impilavano **solo** quando la
    fila non entrava nel foglio — e appena la tavola si e' stretta si sono
    affiancate e il ritorno non si e' piu' instradato.
    """
    where = {item.component_id: item for item in posa(PRIMO)}
    master, slave = where["pdc-master"], where["pdc-slave"]
    assert abs(master.origin.x_mm - slave.origin.x_mm) < 1e-9, (
        "le due pompe di calore non sono incolonnate: stanno a "
        f"{master.origin.x_mm:g} e {slave.origin.x_mm:g}"
    )
    assert master.origin.y_mm != slave.origin.y_mm


def test_il_primo_impianto_esce_dal_proprio_piano() -> None:
    """La prova che vale piu' di tutte, **riscritta il 20 settembre 2026**.

    Che cosa difendeva: che l'impianto 1 si componesse da solo su una A3, con
    `compose_drawing`. Quella proprieta' gliela dava il **solutore**, e
    **D-151** l'ha tolto dalla decisione della posa: senza un piano, su una A3
    sola e senza il ripiego di D-150, l'impianto 1 non si compone piu' — il
    motore dice perche', ed e' un messaggio su cui si agisce («la tratta
    `w2-a-a-a` passa ancora sotto la miscelatrice dopo essersi interrotta per
    lei: dalle un rettilineo piu' lungo»).

    **Non e' una regressione nascosta: e' il prezzo dichiarato di D-151**, e il
    rapporto di `DRAW-015` lo porta con i numeri su tutti e cinque gli impianti.

    Che cosa difende adesso, ed e' la proprieta' che conta: che l'impianto 1
    esca **dal proprio piano di composizione**, quello agli atti, con **zero
    rilievi bloccanti e zero tratte cedute**. Il disegno lo compone un agente;
    il motore esegue e misura.
    """
    from disegnatore_mep.piano.esecutore import esegui_piano
    from disegnatore_mep.piano.formato import carica_piano

    radice = Path(__file__).resolve().parents[2]
    esito = esegui_piano(
        completato(PRIMO),
        carica_piano(radice / "docs/collaudi/PROVA-PIANO/impianto-1.json"),
        catalog(),
        SymbolRegistry.from_directory(radice / "assets/symbols"),
        radice / "naming",
    )
    assert esito.disegno is not None, esito.errore
    assert esito.disegno.sheets[0].symbols
    assert esito.bloccanti == [], [item.code for item in esito.bloccanti]
    assert esito.cedute == ()
