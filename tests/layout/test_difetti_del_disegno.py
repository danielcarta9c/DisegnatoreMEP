"""I tre invarianti rotti che fermano i cinque impianti (D-113).

Nessuno di questi e' un difetto di **spazio**: misurato l'8 agosto, i cinque
impianti falliscono su A0 e su un foglio 3000 x 2000 negli stessi punti e alle
stesse coordinate che su A3, usando il 21-23 % dell'altezza. La domanda che
HANDOFF poneva per la prima ora — «piccoli difetti del tracciatore oppure
disposizione stretta?» — ha risposta: difetti del tracciatore.

Le prove qui sono **marcate rosse apposta**: dicono cosa dovrebbe valere, oggi
non vale, e il segno si toglie quando il difetto si chiude. Il difetto 7 porta
dentro una domanda grafica vera — dove va disegnato lo scarico di un serbatoio
che poggia a terra — e quella si decide con una fonte o col PM, non qui: questa
prova si limita a inchiodare il fatto misurabile.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.composition import levels_of
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import PlacedSymbol, Point
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
# Difetto 7 — l'attacco di scarico dei serbatoi e' murato dal pavimento
# ---------------------------------------------------------------------------


def test_su_ogni_impianto_un_serbatoio_ha_lo_scarico_sulla_linea_di_terra() -> None:
    """Il fatto nudo, senza giudizio: e' cosi' su tutti e cinque.

    Tre cose ciascuna giusta per conto propria — il `drain` sul fondo del
    simbolo, il serbatoio appoggiato a terra, il divieto di disegnare sotto il
    pavimento — che insieme chiudono un attacco.
    """
    for nome in PROVE:
        progetto, posati, griglia, _ = disposto(nome)
        registro = catalogo()
        definizioni = {c.id: c.definition_id for c in progetto.components}
        pavimento = quota_del_pavimento(griglia)
        murati = [
            f"{p.component_id}.{porta.id}"
            for p in posati
            for porta in registro.resolve(
                definizioni[p.component_id]
            ).symbol.manifest.rotated(p.rotation_deg).ports
            if porta.face is PortFace.BOTTOM
            and p.origin.y_mm + porta.y_mm >= pavimento - 1e-9
        ]
        assert murati, f"{nome}: nessun attacco murato — il difetto 7 e' chiuso?"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 7 (D-113). L'attacco di scarico di un serbatoio e' irraggiungibile "
        "per costruzione, e non per mancanza di spazio: il simbolo mette il `drain` "
        "sul proprio bordo inferiore rivolto in basso, il collocatore appoggia i "
        "serbatoi sulla linea di terra, e l'instradatore vieta ogni cella sotto "
        "quella linea perche' li' c'e' il pavimento. Misurato: provando 54 posizioni "
        "diverse per l'accessorio di scarico intorno al serbatoio, gli instradamenti "
        "riusciti sono ZERO — quindi spostare qualcosa non serve, e nemmeno un "
        "foglio piu' grande. E' cio' che ferma la catena sugli impianti 1 e 4. La "
        "chiusura ha dentro una domanda grafica vera — il serbatoio si stacca da "
        "terra, l'accessorio esce di fianco, oppure sotto la linea di terra si puo' "
        "disegnare? — che si decide con una fonte o col PM (D-102, D-107), mai qui."
    ),
)
def test_lo_scarico_di_un_serbatoio_si_riesce_a_instradare() -> None:
    progetto, posati, griglia, partizione = disposto(PROVE[0])
    route_sheet(progetto, list(partizione.trunks), posati, catalogo(), griglia)  # type: ignore[attr-defined]


def test_spostare_l_accessorio_di_scarico_non_cambia_niente() -> None:
    """La prova che il difetto 7 **non** e' di disposizione, e va tenuta anche
    dopo: e' il modo in cui si e' scoperto che la prima diagnosi era sbagliata.

    Cinquantaquattro posizioni intorno al serbatoio, su un foglio abbondante:
    se anche una sola funzionasse, il difetto sarebbe di chi dispone.
    """
    progetto, posati, griglia, partizione = disposto(PROVE[0])
    registro = catalogo()
    serbatoio = next(p for p in posati if p.component_id == "accumulo")
    scarico = "drain-connection-accumulo-primary-in"
    riusciti = 0
    for dx in (-40.0, -20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0, 40.0):
        for dy in (-40.0, -20.0, -10.0, 0.0, 10.0, 20.0):
            mosso = [
                item.model_copy(
                    update={
                        "origin": Point(
                            x_mm=serbatoio.origin.x_mm + dx,
                            y_mm=serbatoio.origin.y_mm + dy,
                        )
                    }
                )
                if item.component_id == scarico
                else item
                for item in posati
            ]
            try:
                route_sheet(progetto, list(partizione.trunks), mosso, registro, griglia)  # type: ignore[attr-defined]
            except LayoutError:
                continue
            riusciti += 1
    assert riusciti == 0, (
        f"{riusciti} posizioni instradano: il difetto 7 sarebbe di disposizione, "
        "e la diagnosi di D-113 va riscritta"
    )


# ---------------------------------------------------------------------------
# Difetto 8 — un pezzo puo' finire sotto la linea di terra
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 8 (D-113). Il ripiego del collocatore puo' posare un pezzo sotto la "
        "linea di terra, dove nessuna linea puo' raggiungerlo: il ciclo che lo spinge "
        "in giu' cercando posto si ferma quando sfonderebbe il pavimento e usa lo "
        "stesso l'ultima quota. Sull'impianto 3 `zona-notte` finisce interamente "
        "sotto — ed e' li' che quella catena si ferma; sul 5 `miscelatrice-radiante` "
        "resta a cavallo. Su un foglio abbondante, quindi non e' mancanza di spazio."
    ),
)
@pytest.mark.parametrize("nome", [PROVE[2], PROVE[4]])
def test_nessun_pezzo_finisce_sotto_il_pavimento(nome: str) -> None:
    _, posati, griglia, _ = disposto(nome)
    pavimento = quota_del_pavimento(griglia)
    sotto = [
        item.component_id for item in posati if item.bottom_mm > pavimento + 1e-9
    ]
    assert sotto == [], sotto


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
