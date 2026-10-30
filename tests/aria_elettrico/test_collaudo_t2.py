"""Le correzioni di libreria e motore dopo il secondo collaudo indipendente (REL-012, T2).

Il rapporto e' `docs/collaudi/REL-012/collaudo-t2/RAPPORTO.md`: una centrale con pompa di
calore, volano, bollitore, due zone, e l'elettrico e la regolazione su una tavola a parte.
La tavola dell'elettrico usciva con zero bloccanti e non si leggeva. Qui le correzioni,
una per una, ciascuna con la sua prova:

1. **le sigle dei pezzi che hanno un cavo** (§3.1, il difetto piu' grave): miscelatrice,
   deviatrice e sonde portano la sigla della famiglia sulle due tavole;
2. **il cavo tocca il corpo** (§3.2): il moncone di una porta di comando collegata va
   dalla faccia del riquadro al corpo;
3. **niente monconi d'acqua sulla tavola dell'elettrico** (§3.2);
4. **il circolatore con due attacchi elettrici** (§2.2.10): alimentazione e comando;
5. **i messaggi in italiano**, e il consiglio del formato successivo (§2.1.8);
6. **i rilievi nominano le tratte coi loro pezzi** (§2.1.5), non con gli id;
7. **il titolo della vista non fa da titolo** (§3.8): senza titolo resta «DA DEFINIRE»;
8. **la riga «Vedi» della legenda** e' una frase sola (§3.9);
9. **la consegna non porta il logo** (§1): lo prova `tests/skill/test_comando.py`.

Che le tavole senza elettrico non cambino lo misura il banco di REL-011, non queste prove.
"""

import ast
import contextlib
import io
import json
import math
import re
from functools import cache
from pathlib import Path
from xml.etree import ElementTree

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.geometry import PlacedSymbol, Point, SheetGeometry
from disegnatore_mep.model.types import Domain, IssueSeverity
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.piano.vista import vista_del_grafo
from disegnatore_mep.skill import cartelle_del_repository, main
from disegnatore_mep.validation.regole import rilievi_delle_regole
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
COLLAUDO = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t2"
DOPO = COLLAUDO / "dopo"

COMANDATI_SENZA_TABELLA = {
    "miscelatrice": "VMR-01",
    "deviatrice": "VD-01",
    "sonda-pannelli": "SO-01",
    "sonda-bollitore": "SO-02",
}
"""I pezzi col cavo che sulle tavole del collaudo non avevano sigla, e quella che il
grafo intero da' loro."""


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def tavola(cartella: Path, vista: str) -> EsitoDelPiano:
    """Una delle due tavole del collaudo: il grafo completo e il piano della vista."""
    esito = esegui_piano(
        load_project(cartella / "grafo-completo.json"),
        carica_piano(cartella / f"piano-{vista}.json"),
        catalogo(),
        simboli(),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    return esito


def foglio(cartella: Path, vista: str) -> SheetGeometry:
    return tavola(cartella, vista).disegno.sheets[0]  # type: ignore[union-attr]


def svg(cartella: Path, vista: str) -> str:
    esito = tavola(cartella, vista)
    return render_sheet(foglio(cartella, vista), esito.frame, simboli())


# --- la geometria disegnata di un pezzo, letta dall'SVG della tavola ----------------

Matrice = tuple[float, float, float, float, float, float]
IDENTITA: Matrice = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _per(m: Matrice, n: Matrice) -> Matrice:
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2, a * e2 + c * f2 + e, b * e2 + d * f2 + f)


def _trasformazione(testo: str) -> Matrice:
    m = IDENTITA
    for nome, argomenti in re.findall(r"(\w+)\(([^)]*)\)", testo):
        v = [float(x) for x in re.split(r"[ ,]+", argomenti.strip()) if x]
        if nome == "translate":
            n = (1.0, 0.0, 0.0, 1.0, v[0], v[1] if len(v) > 1 else 0.0)
        elif nome == "scale":
            n = (v[0], 0.0, 0.0, v[1] if len(v) > 1 else v[0], 0.0, 0.0)
        elif nome == "rotate":
            r = math.radians(v[0])
            cx, cy = (v[1], v[2]) if len(v) == 3 else (0.0, 0.0)
            n = _per(
                _per((1.0, 0.0, 0.0, 1.0, cx, cy), (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0.0, 0.0)),
                (1.0, 0.0, 0.0, 1.0, -cx, -cy),
            )
        else:
            raise AssertionError(nome)
        m = _per(m, n)
    return m


def _punto(m: Matrice, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def primitive_del_pezzo(testo: str, pezzo: str) -> tuple[list[tuple[float, ...]], list[tuple[float, ...]]]:
    """Segmenti e cerchi che la tavola disegna per un pezzo, in millimetri del foglio."""
    radice = ElementTree.fromstring(testo)
    gruppo = next(
        item for item in radice.iter() if item.get("class") == "symbol" and item.get("data-component-id") == pezzo
    )
    segmenti: list[tuple[float, ...]] = []
    cerchi: list[tuple[float, ...]] = []

    def visita(nodo: ElementTree.Element, m: Matrice) -> None:
        m = _per(m, _trasformazione(nodo.get("transform", "")))
        tag, get = nodo.tag.rpartition("}")[2], nodo.get
        if tag == "line":
            segmenti.append((*_punto(m, float(get("x1")), float(get("y1"))), *_punto(m, float(get("x2")), float(get("y2")))))
        elif tag == "rect":
            x, y, w, h = (float(get(k)) for k in ("x", "y", "width", "height"))
            angoli = [_punto(m, *p) for p in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))]
            segmenti.extend((*angoli[i], *angoli[(i + 1) % 4]) for i in range(4))
        elif tag == "circle":
            cx, cy = _punto(m, float(get("cx")), float(get("cy")))
            cerchi.append((cx, cy, float(get("r")) * math.hypot(m[0], m[1])))
        elif tag == "path":
            punti: list[tuple[float, float]] = []
            for comando, argomenti in re.findall(r"([MLQCZ])([^MLQCZ]*)", get("d", "")):
                numeri = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", argomenti)]
                coppie = [_punto(m, x, y) for x, y in zip(numeri[0::2], numeri[1::2], strict=False)]
                if comando == "M":
                    punti = coppie[:1]
                elif comando in "LQC":
                    for p in coppie:
                        segmenti.append((*punti[-1], *p))
                        punti.append(p)
                elif comando == "Z" and punti:
                    segmenti.append((*punti[-1], *punti[0]))
        for figlio in nodo:
            visita(figlio, m)

    visita(gruppo, IDENTITA)
    return segmenti, cerchi


def distanza(punto: tuple[float, float], primitive: tuple[list[tuple[float, ...]], list[tuple[float, ...]]]) -> float:
    """Dal punto alla cosa disegnata piu' vicina: zero se il punto sta su una linea."""
    px, py = punto
    migliore = math.inf
    for x1, y1, x2, y2 in primitive[0]:
        dx, dy = x2 - x1, y2 - y1
        lungo = dx * dx + dy * dy
        t = 0.0 if lungo == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / lungo))
        migliore = min(migliore, math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)))
    for cx, cy, r in primitive[1]:
        migliore = min(migliore, abs(math.hypot(px - cx, py - cy) - r))
    return migliore


def porta_sul_foglio(pezzo: PlacedSymbol, porta: str) -> tuple[float, float]:
    """Dove sta una porta del pezzo sul foglio."""
    manifesto = simboli().get(pezzo.symbol_id).manifest.rotated(pezzo.rotation_deg, pezzo.specchiato)
    fisica = manifesto.port(pezzo.physical_port(porta))
    return pezzo.origin.x_mm + fisica.x_mm, pezzo.origin.y_mm + fisica.y_mm


def capo_sul_pezzo(sheet: SheetGeometry, pezzo: PlacedSymbol, tubazione: str) -> tuple[float, float]:
    """Il capo della spezzata di una tubazione che sta sul riquadro del pezzo."""
    tratta = next(item for item in sheet.routes if tubazione in item.connection_ids)
    capi = [tratta.segments[0][0], tratta.segments[-1][-1]]

    def sul_riquadro(p: Point) -> bool:
        return (
            pezzo.origin.x_mm - 0.01 <= p.x_mm <= pezzo.right_mm + 0.01
            and pezzo.origin.y_mm - 0.01 <= p.y_mm <= pezzo.bottom_mm + 0.01
        )

    capo = next(p for p in capi if sul_riquadro(p))
    return capo.x_mm, capo.y_mm


# --- 1. le sigle dei pezzi che hanno un cavo ---------------------------------------------


@pytest.mark.parametrize("vista", ["idraulica", "elettrico"])
def test_i_pezzi_col_cavo_portano_la_sigla_sulle_due_tavole(vista: str) -> None:
    """§3.1: due valvole a tre vie quasi uguali e due sonde identiche, senza nome, sulle
    due tavole. La sigla e' quella del grafo intero, la stessa sulle due."""
    sheet = foglio(COLLAUDO, vista)
    per_pezzo = {item.component_id: item for item in sheet.symbols}
    scritte = {item.text for item in sheet.labels}
    for pezzo, sigla in COMANDATI_SENZA_TABELLA.items():
        assert per_pezzo[pezzo].tag == sigla, (vista, pezzo, per_pezzo[pezzo].tag)
        assert sigla in scritte, (vista, sigla)
    # Cedono come le sigle dei pezzi fuori dall'acqua: mai un bloccante.
    assert tavola(COLLAUDO, vista).bloccanti == []


def test_i_circolatori_hanno_la_stessa_sigla_sulle_due_tavole() -> None:
    sigle = [
        {item.component_id: item.tag for item in foglio(COLLAUDO, vista).symbols if item.component_id.startswith("circ-")}
        for vista in ("idraulica", "elettrico")
    ]
    assert sigle[0] == sigle[1] == {"circ-pannelli": "CIR-01", "circ-radiatori": "CIR-02", "circ-ricircolo": "CIR-03"}


# --- 2. il cavo tocca il corpo -----------------------------------------------------------


def _cavi_sulle_porte_di_comando(cartella: Path) -> list[tuple[str, str, str]]:
    """(pezzo, porta, tubazione) per ogni cavo che arriva su una porta di comando di un
    pezzo che sta sull'acqua (le `control_ports` del suo simbolo)."""
    modello = load_project(cartella / "grafo-completo.json")
    voce = {item.id: item.definition_id for item in modello.components}
    trovati = []
    for tubazione in modello.connections:
        for ref in (tubazione.endpoint_a, tubazione.endpoint_b):
            simbolo = simboli().get(catalogo().get(voce[ref.component_id]).symbol_id)
            if ref.port_id in simbolo.manifest.control_port_ids:
                trovati.append((ref.component_id, ref.port_id, tubazione.id))
    return trovati


@pytest.mark.parametrize("cartella", [COLLAUDO, DOPO], ids=["collaudo", "dopo"])
def test_il_cavo_tocca_il_corpo_del_pezzo(cartella: Path) -> None:
    """§3.2: fra il fondo della pompa di calore e l'inizio del cavo c'era un vuoto di
    tre millimetri, e lo stesso per il bus. Si misura sulla tavola disegnata: dal capo
    del cavo alla cosa disegnata piu' vicina del pezzo."""
    sheet, testo = foglio(cartella, "elettrico"), svg(cartella, "elettrico")
    per_pezzo = {item.component_id: item for item in sheet.symbols}
    cavi = _cavi_sulle_porte_di_comando(cartella)
    assert {pezzo for pezzo, _, _ in cavi} >= {"pdc", "miscelatrice", "deviatrice", "circ-pannelli"}
    for pezzo, porta, tubazione in cavi:
        capo = capo_sul_pezzo(sheet, per_pezzo[pezzo], tubazione)
        assert capo == pytest.approx(porta_sul_foglio(per_pezzo[pezzo], porta))
        vuoto = distanza(capo, primitive_del_pezzo(testo, pezzo))
        assert vuoto < 0.01, f"{pezzo}.{porta}: il cavo finisce a {vuoto:.2f} mm dal pezzo"


@pytest.mark.parametrize(
    "simbolo",
    [item for item in SymbolRegistry.from_directory(SYMBOLS).all() if item.manifest.control_ports],
    ids=lambda item: item.manifest.id,
)
def test_il_moncone_di_comando_va_dalla_porta_al_corpo(simbolo: Symbol) -> None:
    """In libreria: col cavo collegato il corpo arriva a ogni porta di comando, e il
    moncone tocca il corpo di sempre — non resta sospeso."""
    corpo = simbolo.body
    di_sempre = primitive_del_pezzo(f'<svg><g class="symbol" data-component-id="x">{corpo}</g></svg>', "x")
    tutti = simbolo.senza_le_porte((), simbolo.manifest.control_port_ids)
    disegnato = primitive_del_pezzo(f'<svg><g class="symbol" data-component-id="x">{tutti.body}</g></svg>', "x")
    for porta in simbolo.manifest.control_ports:
        assert distanza((porta.x_mm, porta.y_mm), disegnato) < 1e-6, porta.id
        verso = {"left": (1, 0), "right": (-1, 0), "top": (0, 1), "bottom": (0, -1)}[porta.face.value]
        # Dalla porta verso l'interno, il primo punto del corpo di sempre e' a una
        # distanza finita, e il moncone la copre tutta.
        passo, fondo = 0.0, None
        while passo < 10:
            punto = (porta.x_mm + verso[0] * passo, porta.y_mm + verso[1] * passo)
            if distanza(punto, di_sempre) < 1e-6:
                fondo = passo
                break
            assert distanza(punto, disegnato) < 1e-6, f"{porta.id}: buco a {passo:.2f} mm dalla porta"
            passo += 0.05
        assert fondo is not None, f"{porta.id}: il corpo non si incontra"


def test_senza_cavi_il_corpo_resta_quello_di_sempre() -> None:
    """Il moncone di comando si disegna solo col cavo: senza, il corpo e' quello di
    prima, e una tavola senza elettrico non cambia."""
    for simbolo in simboli().all():
        assert simbolo.senza_le_porte(()) is simbolo
        assert "data-comando" not in simbolo.body and "data-moncone" not in simbolo.body


# --- 3. niente monconi d'acqua sulla tavola dell'elettrico ------------------------------


ATTACCHI_D_ACQUA = [
    ("pdc", "water_supply"), ("pdc", "water_return"),
    ("miscelatrice", "hot_in"), ("miscelatrice", "cold_in"), ("miscelatrice", "out"),
    ("deviatrice", "in"), ("deviatrice", "out_a"), ("deviatrice", "out_b"),
    ("circ-pannelli", "a"), ("circ-pannelli", "b"), ("circ-radiatori", "a"), ("circ-radiatori", "b"),
    ("circ-ricircolo", "a"), ("circ-ricircolo", "b"),
    ("sonda-pannelli", "a"), ("sonda-bollitore", "a"),
]
"""Gli attacchi d'acqua dei pezzi che stanno sulla tavola dell'elettrico del collaudo."""


def test_sulla_tavola_dell_elettrico_le_porte_d_acqua_non_hanno_moncone() -> None:
    """§3.2: la pompa di calore mostrava i due attacchi d'acqua come tubi aperti, e cosi'
    circolatori, valvole e sonde. Dal punto dell'attacco, niente di disegnato."""
    sheet, testo = foglio(COLLAUDO, "elettrico"), svg(COLLAUDO, "elettrico")
    per_pezzo = {item.component_id: item for item in sheet.symbols}
    for pezzo, porta in ATTACCHI_D_ACQUA:
        vuoto = distanza(porta_sul_foglio(per_pezzo[pezzo], porta), primitive_del_pezzo(testo, pezzo))
        assert vuoto > 1.0, f"{pezzo}.{porta}: moncone d'acqua a {vuoto:.2f} mm"


def test_sulla_tavola_idraulica_i_monconi_d_acqua_restano() -> None:
    sheet, testo = foglio(COLLAUDO, "idraulica"), svg(COLLAUDO, "idraulica")
    per_pezzo = {item.component_id: item for item in sheet.symbols}
    for porta in ("water_supply", "water_return"):
        assert distanza(porta_sul_foglio(per_pezzo["pdc"], porta), primitive_del_pezzo(testo, "pdc")) < 1e-6


# --- 4. il circolatore con due attacchi elettrici ---------------------------------------


def test_il_circolatore_ha_l_alimentazione_e_il_comando() -> None:
    """§2.2.10: alimentato dal quadro e acceso dal regolatore, due cavi."""
    manifesto = simboli().get("pump-circulator").manifest
    assert {(p.id, p.face.value) for p in manifesto.control_ports} == {("power", "top"), ("comando", "bottom")}
    intere = ComponentRegistry.from_directory(CATALOG)
    for voce in ("pump-circulator", "pump-circulator-dhw", "pump-circulator-solar"):
        porta = next(p for p in intere.get(voce).ports if p.id == "comando")
        assert porta.domain is Domain.CONTROL and porta.required is False and porta.medium == "power_supply"
        # Senza collegamento non c'e': la voce e' quella di prima.
        assert "comando" not in catalogo().get(voce).port_ids


def test_il_grafo_col_comando_dei_circolatori_si_valida_e_si_disegna() -> None:
    modello = load_project(DOPO / "grafo-completo.json")
    esito = validate_project(modello, catalogo().per_il_progetto(modello))
    assert not [item for item in esito.issues if item.severity is IssueSeverity.BLOCKING]
    sheet = foglio(DOPO, "elettrico")
    circolatore = next(item for item in sheet.symbols if item.component_id == "circ-pannelli")
    assert circolatore.porte_col_cavo == ["comando", "power"]
    assert tavola(DOPO, "elettrico").bloccanti == []
    assert tavola(DOPO, "elettrico").cedute == ()


# --- 5. i messaggi in italiano ---------------------------------------------------------


def test_la_legenda_che_sfora_lo_dice_in_italiano_e_consiglia_il_formato_successivo(tmp_path: Path) -> None:
    """§2.1.8: sull'A3 la legenda della tavola idraulica sfora di 2,5 mm. Il messaggio
    era in inglese e consigliava di dividere l'impianto su piu' fogli."""
    piano = json.loads((COLLAUDO / "piano-idraulica.json").read_text(encoding="utf-8"))
    piano["formato"] = "A3"
    (tmp_path / "piano.json").write_text(json.dumps(piano), encoding="utf-8")
    errore = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errore):
        codice = main(
            ["disegna", str(COLLAUDO / "grafo-completo.json"), "--piano", str(tmp_path / "piano.json"),
             "--out", str(tmp_path / "tavola"), "--senza-dxf"],
            cartelle_del_repository(ROOT),
        )
    assert codice == 1
    detto = errore.getvalue()
    assert "la legenda sfora" in detto and "formato successivo" in detto, detto
    assert "the legend" not in detto and "more sheets" not in detto


@pytest.mark.parametrize("modulo", ["legend.py", "route.py", "inline.py"])
def test_i_messaggi_del_motore_che_arrivano_a_chi_disegna_sono_in_italiano(modulo: str) -> None:
    """La legenda, l'instradamento e gli organi in linea: i loro `LayoutError` arrivano a
    chi lancia `mep.py disegna`. Nessuna parola inglese nel testo."""
    albero = ast.parse((ROOT / "src" / "disegnatore_mep" / "layout" / modulo).read_text(encoding="utf-8"))
    inglese = re.compile(r"\b(the|cannot|never|needs?|route|routed|run|is|has|no|fit|split|sheets?)\b")
    trovati = []
    for nodo in ast.walk(albero):
        if not (isinstance(nodo, ast.Raise) and isinstance(nodo.exc, ast.Call)):
            continue
        if getattr(nodo.exc.func, "id", None) != "LayoutError" or not nodo.exc.args:
            continue
        testo = "".join(
            parte.value
            for parte in ast.walk(nodo.exc.args[0])
            if isinstance(parte, ast.Constant) and isinstance(parte.value, str)
        )
        if inglese.search(testo):
            trovati.append(testo)
    assert trovati == []


# --- 6. i rilievi nominano le tratte coi loro pezzi --------------------------------------


def test_i_rilievi_nominano_le_tratte_coi_pezzi_che_collegano() -> None:
    """§2.1.5: «le tratte t11 e t12» non si trovano sul foglio. Si dicono coi pezzi."""
    esito = tavola(COLLAUDO, "idraulica")
    rilievi = rilievi_delle_regole(esito.disegno, esito.frame, esito.catalogo, esito.modello)  # type: ignore[arg-type]
    affiancate = [item for item in rilievi if item.code == "PARALLEL_RUNS_WITHOUT_A_FREE_LANE"]
    assert affiancate, [item.code for item in rilievi]
    for item in affiancate:
        testo = item.message.split(":", 1)[1]
        assert not re.search(r"\bt\d+\b", testo), item.message
        assert "fra " in testo, item.message
        # Gli id restano fra i codici, per chi cerca nel grafo.
        assert {"t11", "t12"} <= set(item.entity_ids)


# --- 7. il titolo della vista non fa da titolo -------------------------------------------


def test_senza_titolo_la_vista_lascia_il_titolo_da_definire() -> None:
    """§3.8: senza `sheet_title` il cartiglio scriveva «Idraulica» e la casella non
    risultava da definire. *Proposta della sessione*."""
    modello = load_project(COLLAUDO / "grafo-completo.json")
    assert modello.metadata.sheet_title is None
    for vista in ("idraulica", "elettrico"):
        della_vista, _ = vista_del_grafo(modello, vista, catalogo(), NAMING)
        assert della_vista.metadata.sheet_title is None
    con = modello.model_copy(update={"metadata": modello.metadata.model_copy(update={"sheet_title": "Centrale"})})
    assert vista_del_grafo(con, "elettrico", catalogo(), NAMING)[0].metadata.sheet_title == "Centrale — elettrico e comando"


# --- 8. la riga «Vedi» della legenda ------------------------------------------------------


@pytest.mark.parametrize("vista", ["idraulica", "elettrico"])
def test_il_rimando_e_una_frase_sola_che_comincia_con_vedi(vista: str) -> None:
    """§3.9: «Vedi» nella colonna dei simboli e il resto in quella dei nomi."""
    sheet = foglio(COLLAUDO, vista)
    rimandi = [nota for nota in sheet.note_della_legenda if nota.campione == "Vedi"]
    assert len(rimandi) == 1
    nota = rimandi[0]
    assert nota.frase and nota.righe[0].startswith("Vedi la tavola «")
    testo = svg(COLLAUDO, vista)
    # Nessun campione a parte: la frase comincia dove comincia il campione.
    assert 'class="legend-note-sample"' not in testo or ">Vedi</text>" not in testo
    assert f'x="{nota.anchor.x_mm:g}" y="{nota.anchor.y_mm:g}" font-size' in testo
