"""Gli invarianti rotti che fermano i cinque impianti (D-113, D-115).

Nessuno di questi e' un difetto di **spazio**: misurato l'8 agosto, i cinque
impianti falliscono su A0 e su un foglio 3000 x 2000 negli stessi punti e alle
stesse coordinate che su A3, usando il 21-23 % dell'altezza. La domanda che
HANDOFF poneva per la prima ora — «piccoli difetti del tracciatore oppure
disposizione stretta?» — ha risposta: difetti del tracciatore.

Le prove marcate `xfail(strict)` dicono cosa dovrebbe valere e oggi non vale:
il segno si toglie quando il difetto si chiude, e la prova resta come
regressione. E' quel che e' successo al difetto 7 lo stesso giorno.

**Difetto 7 — CHIUSO.** L'attacco di scarico dei serbatoi era murato dal
pavimento; il PM ha deciso che esce di fianco, in basso (D-115). Le due prove
restano come regressione e guardano la classe, non il caso.

**Difetto 8 — DISSOLTO, non corretto.** Diceva «un pezzo finisce sotto la linea
di terra»: quella linea e' stata ritirata (D-116) e non c'e' piu' un pavimento
da sfondare. Resta il vincolo vero, che e' il bordo del foglio.

**Difetti 9 e 10 — aperti.** Il rettilineo per gli accessori prenotato solo fra
colonne contigue; la ricerca dell'instradatore che esaurisce il proprio budget.
Il 10 era **coperto** dal 7: finche' la catena si fermava prima, non si vedeva.

Ogni prova che afferma un difetto ne ha accanto **una che ne dice il confine**
— dove il difetto non e' — cosi' chi lo chiude non lo cerca dove non sta.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.composition import levels_of
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import route_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PROVE_DIR = ROOT / "examples" / "prova"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

PROVE = [
    "prova-1-due-pdc-accumulo-combinato.json",
    "prova-2-pdc-deviatrice-acs.json",
    "prova-3-pdc-diretta-pavimento.json",
    "prova-4-ibrido-pdc-caldaia.json",
    "prova-5-cascata-tre-pdc.json",
]

# Un foglio molto piu' grande di qualunque formato ordinario: cosi' nessuno puo'
# leggere questi difetti come «non ci sta».
FOGLIO_ABBONDANTE = SheetFrame(
    standard=A3_LANDSCAPE.model_copy(
        update={"sheet_width_mm": 1189.0, "sheet_height_mm": 841.0}
    )
)


def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def completato(nome: str) -> ProjectModel:
    finito, _, _ = saturate(
        load_project(PROVE_DIR / nome), catalogo(), RuleRegistry.from_directory(RULES)
    )
    return finito


def disposto(nome: str) -> tuple[ProjectModel, list[PlacedSymbol], GridSpace, object]:
    progetto = completato(nome)
    registro = catalogo()
    inline = inline_component_ids(progetto, registro)
    partizione = partition_project(progetto, build_trunks(progetto, inline))[0]
    griglia = GridSpace(
        origin=FOGLIO_ABBONDANTE.drawing_rect_mm, standard=FOGLIO_ABBONDANTE.standard
    )
    posati = place_sheet(
        progetto, partizione, registro, FOGLIO_ABBONDANTE, inline
    )
    return progetto, posati, griglia, partizione


def quota_del_pavimento(griglia: GridSpace) -> float:
    area = FOGLIO_ABBONDANTE.drawing_rect_mm
    return levels_of(area.y_mm, area.height_mm, griglia.step_mm).ground_mm


# ---------------------------------------------------------------------------
# Difetto 7 — CHIUSO l'8 agosto (D-115). L'attacco di scarico dei serbatoi era
# murato dal pavimento; ora esce di fianco, in basso, come ha deciso il PM.
# Le due prove restano come regressione, e difendono la **classe** invece del
# caso: non «il volano ha il drain a destra», ma «nessun attacco di un pezzo
# appoggiato a terra scarica dentro il pavimento». Cosi' il prossimo simbolo
# alto che entrasse in libreria col drain sotto verrebbe fermato qui.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("nome", PROVE)
def test_nessun_pezzo_esce_dall_area_di_disegno(nome: str) -> None:
    """Cio' che resta dei difetti 7 e 8, dopo che la linea di terra e' caduta.

    **Il difetto 8 si e' dissolto con D-116**, non e' stato corretto: diceva
    «un pezzo finisce sotto la linea di terra, dove nessuna linea puo'
    raggiungerlo», e quella linea non esiste piu'. Non c'e' nessun pavimento da
    sfondare. Il vincolo vero — e l'unico che il PM ha mai dato — e' che un
    pezzo stia dentro il foglio.

    Del difetto 7 resta la lezione: tre cose ciascuna giusta per conto propria
    possono chiudere un attacco. La prova guarda **l'esito** e non le cause.
    """
    _, posati, _, _ = disposto(nome)
    area = FOGLIO_ABBONDANTE.drawing_rect_mm
    fuori = [
        p.component_id
        for p in posati
        if p.origin.y_mm < area.y_mm - 1e-9
        or p.bottom_mm > area.bottom_mm + 1e-9
        or p.origin.x_mm < area.x_mm - 1e-9
        or p.right_mm > area.right_mm + 1e-9
    ]
    assert fuori == [], f"{nome}: pezzi fuori dall'area {fuori}"


def test_lo_scarico_di_un_serbatoio_si_riesce_a_instradare() -> None:
    """Il difetto 7 preso dal lato che conta: la tratta si disegna.

    Prima non si disegnava da nessuna posizione — cinquantaquattro provate,
    zero riuscite — e non era un problema di spazio: e' cosi' che si e' capito
    che la prima diagnosi, «e' la disposizione», era sbagliata.
    """
    progetto, posati, griglia, partizione = disposto(PROVE[0])
    registro = catalogo()
    scarico = next(
        t
        for t in partizione.trunks  # type: ignore[attr-defined]
        if t.connection_ids and "stub-drain-connection" in t.connection_ids[0]
    )
    route_sheet(progetto, [scarico], posati, registro, griglia)


# ---------------------------------------------------------------------------
# Difetto 9 — il rettilineo si prenota solo fra colonne contigue
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 9 (D-113). Il rettilineo che gli accessori in linea pretendono si "
        "prenota solo fra colonne CONTIGUE della stessa fascia, e fra l'ultima "
        "colonna di una fascia e la prima della successiva. Una tratta fra colonne "
        "non contigue non ne riceve, e i suoi accessori non trovano i 10 mm dritti "
        "su cui sedersi: e' cio' che ferma gli impianti 2 e 5, su un foglio "
        "abbondante e con il 78 % dell'altezza libera."
    ),
)
@pytest.mark.parametrize("nome", [PROVE[1], PROVE[4]])
def test_ogni_tratta_ha_il_rettilineo_che_i_suoi_accessori_pretendono(
    nome: str,
) -> None:
    from disegnatore_mep.layout.inline import settle_sheet

    progetto, posati, griglia, partizione = disposto(nome)
    settle_sheet(progetto, list(partizione.trunks), posati, catalogo(), griglia)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Difetto 10 — la ricerca dell'instradatore non converge
#
# Non e' nuovo: era **coperto** dal difetto 7. Finche' lo scarico del serbatoio
# era murato la catena si fermava prima, e questo non si vedeva. Chiuso quello,
# gli impianti 1 e 4 arrivano piu' avanti e si fermano qui, su un foglio dove
# il disegno occupa un quinto della carta: non e' congestione, e' la ricerca
# che esplode.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 10 (D-115). L'instradatore esaurisce il proprio budget di ricerca "
        "— 400.000 espansioni — su una tratta sola, e si arrende dicendo «prova una "
        "partizione diversa». Su un foglio 1189x841 in cui i simboli occupano un "
        "quinto della carta, la partizione non c'entra: e' la ricerca che esplode su "
        "una griglia grande e quasi vuota, dove ogni cella libera e' un'espansione. "
        "**Si vede solo dopo il ciclo di miglioramento**: sulla prima posa la stessa "
        "tratta si instrada, e sono le pose che il ciclo prova a farla esplodere. "
        "Emerso l'8 agosto chiudendo il difetto 7, che prima fermava la catena piu' "
        "a monte e lo teneva coperto. Ferma gli impianti 1 e 4."
    ),
)
@pytest.mark.parametrize("nome", [PROVE[0]])
def test_la_tavola_arriva_in_fondo_senza_esaurire_la_ricerca(nome: str) -> None:
    from disegnatore_mep.layout.compose import compose_drawing

    compose_drawing(completato(nome), catalogo(), FOGLIO_ABBONDANTE)


def test_l_ibrido_si_compone(  ) -> None:
    """**La prima delle cinque tavole che esce.**

    L'impianto 4 era fermo sul budget di ricerca dell'instradatore. Ritirato il
    divieto di disegnare sotto la linea di terra (D-116), la stessa tratta
    trova strada e la tavola si compone. Non e' stato aggiunto niente: e' stata
    tolta una regola che nessuno aveva chiesto.
    """
    from disegnatore_mep.layout.compose import compose_drawing

    disegno = compose_drawing(completato(PROVE[3]), catalogo(), FOGLIO_ABBONDANTE)
    assert len(disegno.sheets) == 1
    assert disegno.sheets[0].symbols
    assert disegno.sheets[0].routes


def test_sulla_prima_posa_le_tratte_dei_due_impianti_si_instradano() -> None:
    """Il confine del difetto 10, misurato: **non** e' la posa di partenza.

    Serve a non far cercare il difetto dove non e'. Se un giorno anche questa
    diventasse rossa, il difetto sarebbe un altro e piu' grave.
    """
    for nome in (PROVE[0], PROVE[3]):
        progetto, posati, griglia, partizione = disposto(nome)
        route_sheet(progetto, list(partizione.trunks), posati, catalogo(), griglia)  # type: ignore[attr-defined]
