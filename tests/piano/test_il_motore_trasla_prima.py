"""Il motore trasla **prima** di instradare: del piano contano le posizioni relative.

Fino al 23 settembre 2026 il motore instradava dove il piano aveva scritto i
pezzi, e traslava il disegno per centrarlo **dopo**. Un pezzo a coordinate
negative — o troppo vicino all'origine — lasciava le sue tratte fuori dalla
griglia dell'area, e il comando rispondeva «every orthogonal path is blocked».
L'ha trovato un agente in camera pulita il 22 settembre, sulla tavola che il PO
ha poi approvato (**I-108**): lo stesso piano, spostato di (−20, −105), non si
instradava piu'. Le istruzioni del pianificatore dicevano che contano solo le
posizioni relative, e non era vero.

E la diagnostica parla nel sistema del piano. Il 23 settembre due agenti hanno
scritto la stessa cosa: la posa stampata aveva le y un millimetro piu' in basso
del piano, e gli errori dell'instradamento dicevano celle di una griglia che chi
compone non vede.
"""

# categoria: difende il motore — il piano dice dove stanno i pezzi gli uni rispetto agli altri, e il motore porta il disegno nell'area prima di instradarlo

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.geometry import DrawingGeometry
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import PianoDiComposizione, carica_piano

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "DRAW-016" / "prova-camera-pulita-2026-09-22"


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(ROOT / "assets" / "symbols")


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=simboli()
    )


def _spostato(piano: PianoDiComposizione, dx: float, dy: float) -> PianoDiComposizione:
    return piano.model_copy(
        update={
            "pezzi": {
                chi: dove.model_copy(update={"x": dove.x + dx, "y": dove.y + dy})
                for chi, dove in piano.pezzi.items()
            }
        }
    )


def _disegno(piano: PianoDiComposizione) -> DrawingGeometry:
    esito = esegui_piano(
        load_project(PROVA / "scheletro-5.json"),
        piano,
        catalogo(),
        simboli(),
        ROOT / "naming",
    )
    assert esito.disegno is not None, esito.errore
    return esito.disegno


def _forma(disegno: DrawingGeometry) -> tuple[object, ...]:
    """Dove stanno simboli e tubi sulla tavola finita, al decimo di millimetro."""
    foglio = disegno.sheets[0]
    return (
        sorted(
            (item.component_id, item.origin.x_mm, item.origin.y_mm, item.rotation_deg)
            for item in foglio.symbols
        ),
        sorted(
            (
                tuple(route.connection_ids),
                tuple(
                    tuple((round(p.x_mm, 1), round(p.y_mm, 1)) for p in segmento)
                    for segmento in route.segments
                ),
            )
            for route in foglio.routes
        ),
    )


def test_lo_stesso_piano_spostato_da_la_stessa_tavola() -> None:
    """**La misura che ha aperto il difetto, e adesso lo chiude.** Il piano della
    tavola approvata, spostato di (−20, −105): meta' dei pezzi a coordinate
    negative. Esce, e la tavola e' la stessa **al decimo di millimetro**."""
    piano = carica_piano(PROVA / "piano-5.json")
    assert _forma(_disegno(_spostato(piano, -20.0, -105.0))) == _forma(_disegno(piano))


def test_un_piano_lontano_dall_origine_da_la_stessa_tavola() -> None:
    """E nell'altro verso: lo stesso piano spostato lontano, dove prima una parte
    del disegno sarebbe uscita dall'area di un A3."""
    piano = carica_piano(PROVA / "piano-5.json")
    assert _forma(_disegno(_spostato(piano, 300.0, 200.0))) == _forma(_disegno(piano))


def test_la_posa_resta_nel_sistema_del_piano() -> None:
    """La diagnostica di chi compone non cambia: `posa` porta i pezzi dove il piano
    li ha scritti — arrotondati alla griglia — e non dove il motore li ha portati
    per instradarli. Chi corregge il piano legge li' senza togliere traslazioni."""
    piano = carica_piano(PROVA / "piano-5.json")
    posa = {}
    for dx, dy in ((0.0, 0.0), (-20.0, -105.0)):
        esito = esegui_piano(
            load_project(PROVA / "scheletro-5.json"),
            _spostato(piano, dx, dy),
            catalogo(),
            simboli(),
            ROOT / "naming",
        )
        posa[(dx, dy)] = {
            item.component_id: (item.origin.x_mm - dx, item.origin.y_mm - dy)
            for item in esito.posa
        }
    assert posa[(-20.0, -105.0)] == posa[(0.0, 0.0)]


def test_la_posa_e_quella_scritta_nel_piano() -> None:
    """**Al decimo di millimetro**, non a meno di un passo. La griglia del motore
    parte dall'angolo dell'area — su un A3 a 16 mm dal bordo — e fino al 23
    settembre 2026 la posa riportava ogni pezzo un millimetro piu' in basso di
    dove il piano l'aveva scritto."""
    piano = carica_piano(PROVA / "piano-5.json")
    esito = esegui_piano(
        load_project(PROVA / "scheletro-5.json"),
        piano,
        catalogo(),
        simboli(),
        ROOT / "naming",
    )
    posa = {item.component_id: (item.origin.x_mm, item.origin.y_mm) for item in esito.posa}
    assert {chi: posa[chi] for chi in piano.pezzi} == {
        chi: (dove.x, dove.y) for chi, dove in piano.pezzi.items()
    }


def test_una_tratta_che_non_passa_si_dice_nel_sistema_del_piano() -> None:
    """L'instradatore dice le celle della propria griglia, contate dall'angolo
    dell'area e dopo la traslazione: chi compone non sa riportarle sul piano.
    L'errore nomina anche i due capi della tratta, e dove il piano li ha messi.

    Il piano e' quello approvato con la presa del ricircolo abbassata di 20 mm:
    il ricircolo non trova piu' strada."""
    piano = carica_piano(PROVA / "piano-5.json")
    presa = piano.pezzi["presa-ricircolo"].model_copy(
        update={"y": piano.pezzi["presa-ricircolo"].y + 20.0}
    )
    esito = esegui_piano(
        load_project(PROVA / "scheletro-5.json"),
        piano.model_copy(update={"pezzi": {**piano.pezzi, "presa-ricircolo": presa}}),
        catalogo(),
        simboli(),
        ROOT / "naming",
    )
    assert esito.disegno is None
    assert esito.errore is not None
    innesto = piano.pezzi["innesto-ricircolo"]
    assert "innesto-ricircolo." in esito.errore and "presa-ricircolo." in esito.errore
    assert f"(il pezzo sta a {innesto.x:g}, {innesto.y:g} nel piano)" in esito.errore
    assert f"(il pezzo sta a {presa.x:g}, {presa.y:g} nel piano)" in esito.errore
