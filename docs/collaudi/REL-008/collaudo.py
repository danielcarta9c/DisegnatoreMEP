"""Le sei tavole approvate e la variante retrofit con le scritte a 9 punti (REL-008).

Per ciascuna tavola di `REL-007` — gli stessi grafi, piani e dati di prova, presi dal
suo collaudo —:

1. `esegui_piano` sul suo piano: la tavola in SVG, DXF e PDF, in `tavole/` qui accanto;
2. le misure:
   - **il corpo di ogni scritta**, letto dall'SVG (`font-size`, in mm di carta) e dal
     DXF (l'altezza delle maiuscole diviso 0,688), in punti: il disegno e la tabella da
     una parte, il cartiglio — che il pacchetto non tocca — dall'altra;
   - **il carattere**: quali scritte dell'SVG non ereditano l'Arial della radice;
   - **le sigle e i DN** contro quelli della stessa tavola su `main`: quanti, quali
     mancano;
   - **il disegno non si muove**: simboli e tratte uguali a quelli di `main`;
   - **niente si tocca**: i DN contro simboli, linee, sigle e tabella, come in
     `REL-007`; il preflight per le sigle;
   - **deterministico**: due esecuzioni danno lo stesso SVG e lo stesso DXF.

La geometria di `main` si scrive prima, **con il codice di `main`**, da un albero di
lavoro a parte:

    git worktree add --detach <albero> origin/main
    PYTHONPATH=<albero>/src python3 docs/collaudi/REL-008/collaudo.py --base <cartella>

e poi il collaudo, dalla radice, con il codice del ramo:

    PYTHONPATH=src python3 docs/collaudi/REL-008/collaudo.py <cartella-di-lavoro> <cartella>

E' uno strumento di sessione: vuole ezdxf e il browser.
"""

import importlib.util
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QUI = Path(__file__).resolve().parent
USCITA = QUI / "tavole"
PT_MM = 25.4 / 72
ALTEZZA_MAIUSCOLE_EM = 0.688


def _collaudo_di_rel007():  # type: ignore[no-untyped-def]
    """Il collaudo di `REL-007`, come modulo: le sue tavole, i suoi dati, le sue misure."""
    percorso = ROOT / "docs" / "collaudi" / "REL-007" / "collaudo.py"
    spec = importlib.util.spec_from_file_location("collaudo_rel007", percorso)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _strumenti():  # type: ignore[no-untyped-def]
    from disegnatore_mep.catalog.registry import ComponentRegistry
    from disegnatore_mep.graphics.cartiglio import Cartiglio
    from disegnatore_mep.graphics.registry import SymbolRegistry

    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)
    cartiglio = Cartiglio.da_file(ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json")
    return simboli, catalogo, cartiglio


def base(cartella: Path) -> None:
    """La geometria di ogni tavola com'e' con il codice che si sta eseguendo."""
    r7 = _collaudo_di_rel007()
    simboli, catalogo, cartiglio = _strumenti()
    cartella.mkdir(parents=True, exist_ok=True)
    for nome, impianto, grafo, piano, dati in r7.tavole():
        modello = r7.con_i_dati(grafo, impianto, dati)
        esito, foglio, svg, _ = r7.esegui(nome, modello, piano, simboli, catalogo, cartiglio, cartella / "tavole")
        (cartella / f"{nome}.json").write_text(foglio.model_dump_json(indent=1), encoding="utf-8")
        svg.unlink()
        print(nome, "scritta")


def _corpi_dell_svg(svg: Path) -> dict[str, list[float]]:
    """Il corpo in punti di ogni scritta dell'SVG, per gruppo: cartiglio, tabella,
    il resto della tavola. E le scritte che dichiarano un carattere diverso da quello
    della radice."""
    radice = ET.parse(svg).getroot()
    spazio = "{http://www.w3.org/2000/svg}"
    corpi: dict[str, list[float]] = {"disegno": [], "tabella": [], "cartiglio": []}
    famiglie: set[str] = set()

    def giro(elemento: ET.Element, gruppo: str) -> None:
        classe = elemento.get("class", "")
        if classe == "cartiglio":
            gruppo = "cartiglio"
        elif classe == "tabella-apparecchiature":
            gruppo = "tabella"
        if elemento.tag == f"{spazio}text":
            corpi[gruppo].append(float(elemento.get("font-size", "0")) / PT_MM)
            famiglia = elemento.get("font-family")
            if gruppo == "disegno" and famiglia and famiglia != radice.get("font-family"):
                famiglie.add(famiglia)
        for figlio in elemento:
            giro(figlio, gruppo)

    giro(radice, "disegno")
    corpi["famiglie"] = sorted(famiglie)  # type: ignore[assignment]
    corpi["radice"] = [radice.get("font-family", "")]  # type: ignore[list-item]
    return corpi


def _corpi_del_dxf(dxf: Path) -> dict[str, list[float]]:
    import ezdxf

    from disegnatore_mep.graphics.dxf import LAYER_CARTIGLIO, LAYER_TABELLA

    documento = ezdxf.readfile(dxf)
    corpi: dict[str, list[float]] = {"disegno": [], "tabella": [], "cartiglio": []}
    stili: set[str] = set()
    for spazio in documento.layouts:
        for entita in spazio:
            if entita.dxftype() != "TEXT":
                continue
            gruppo = {LAYER_CARTIGLIO: "cartiglio", LAYER_TABELLA: "tabella"}.get(entita.dxf.layer, "disegno")
            corpi[gruppo].append(entita.dxf.height / ALTEZZA_MAIUSCOLE_EM / PT_MM)
            stili.add(documento.styles.get(entita.dxf.style).dxf.font)
    corpi["caratteri"] = sorted(stili)  # type: ignore[assignment]
    return corpi


def _intervallo(valori: list[float]) -> str:
    if not valori:
        return "nessuna"
    return f"{len(valori)} scritte, {min(valori):.1f}–{max(valori):.1f} pt"


def _scritte(foglio, corpo: float):  # type: ignore[no-untyped-def]
    """Sigle, dati e DN della tavola: nome, padrone, riquadro, verticale. Il padrone
    di una sigla o di un dato e' il suo pezzo; quello di un DN, il suo tratto."""
    from disegnatore_mep.layout.diametri import riquadro_del_diametro
    from disegnatore_mep.layout.labels import riquadro_della_scritta

    pezzi = sorted((s.component_id for s in foglio.symbols), key=len, reverse=True)
    scritte = [
        (
            f"{x.role} {x.text}",
            next((c for c in pezzi if x.id.startswith(c + "-")), x.id),
            riquadro_della_scritta(x, corpo),
            False,
        )
        for x in foglio.labels
        if x.role in ("tag", "data")
    ]
    scritte += [
        (f"DN {x.testo}", "DN " + "/".join(x.connection_ids), riquadro_del_diametro(x, corpo), x.verticale)
        for x in foglio.diametri
    ]
    return scritte


def _rispetto(foglio, corpo: float) -> str:  # type: ignore[no-untyped-def]
    """Le coppie di scritte di pezzi diversi piu' vicine di un corpo lungo la riga e
    di mezzo corpo fra le righe: si leggerebbero come una scritta sola («CIR-01 Øi
    40») o come le righe di un blocco solo («4 kW» di PAV-02 su «PAV-01»)."""
    scritte = _scritte(foglio, corpo)
    coppie = []
    for i, (primo, suo, a, verticale) in enumerate(scritte):
        for secondo, altro, b, altro_verso in scritte[i + 1 :]:
            if suo == altro:
                continue
            dx = max(b[0] - a[2], a[0] - b[2], 0.0)
            dy = max(b[1] - a[3], a[1] - b[3], 0.0)
            for verso in {verticale, altro_verso}:
                lungo, attraverso = (dy, dx) if verso else (dx, dy)
                if lungo < corpo - 1e-6 and attraverso < corpo / 2 - 1e-6:
                    coppie.append(f"{primo} / {secondo} ({dx:.2f}, {dy:.2f} mm)")
                    break
    return (
        "scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: "
        f"{len(coppie)} {coppie if coppie else ''}"
    )


def _sigle_vicine_ad_altri(foglio, corpo: float) -> str:  # type: ignore[no-untyped-def]
    """Le sigle accanto al pezzo piu' vicine a un altro pezzo che al loro."""
    pezzi = {s.component_id: (s.origin.x_mm, s.origin.y_mm, s.right_mm, s.bottom_mm) for s in foglio.symbols}
    trovate = []
    for nome, suo, box, _ in _scritte(foglio, corpo):
        if not nome.startswith("tag ") or suo not in pezzi:
            continue
        mio = _distanza_fra(box, pezzi[suo])
        altri = [(_distanza_fra(box, riquadro), c) for c, riquadro in pezzi.items() if c != suo]
        if altri and min(altri)[0] < mio - 1e-6:
            trovate.append(f"{nome}: dal suo {mio:.2f} mm, da {min(altri)[1]} {min(altri)[0]:.2f} mm")
    return f"sigle piu' vicine a un altro pezzo che al loro: {len(trovate)} {trovate if trovate else ''}"


def _distanza_fra(a, b) -> float:  # type: ignore[no-untyped-def]
    return math.hypot(max(b[0] - a[2], a[0] - b[2], 0.0), max(b[1] - a[3], a[1] - b[3], 0.0))


def _staccate(foglio, corpo: float, cose, r7) -> str:  # type: ignore[no-untyped-def]
    """Le etichette staccate: quanto la scritta sta da cio' che non e' il suo tratto
    (scritte, simboli, linee, tabella), e se la punta cade su una freccia di verso."""
    from disegnatore_mep.graphics.sheet import ARROW_HALF_WIDTH_MM, ARROW_LENGTH_MM, flow_arrow_at
    from disegnatore_mep.layout.diametri import riquadro_del_diametro
    from disegnatore_mep.layout.geometry import FlowKind

    staccate = [x for x in foglio.diametri if x.richiamo is not None]
    if not staccate:
        return "staccate: nessuna"
    frecce = []
    for route in foglio.routes:
        if route.flow_kind is FlowKind.STATIC:
            continue
        for segmento in route.segments:
            freccia = flow_arrow_at(segmento, route.flow_from_start)
            if freccia is not None:
                x, y, dx, dy = freccia
                cx, cy = x - dx * ARROW_LENGTH_MM, y - dy * ARROW_LENGTH_MM
                xs = (x, cx - dy * ARROW_HALF_WIDTH_MM, cx + dy * ARROW_HALF_WIDTH_MM)
                ys = (y, cy + dx * ARROW_HALF_WIDTH_MM, cy - dx * ARROW_HALF_WIDTH_MM)
                frecce.append((min(xs), min(ys), max(xs), max(ys)))
    scritte = _scritte(foglio, corpo)
    righe = []
    for etichetta in staccate:
        assert etichetta.richiamo is not None
        box = riquadro_del_diametro(etichetta, corpo)
        proprie = frozenset(etichetta.connection_ids)
        vicine = [
            (r7._distanza(box, riquadro), nome)
            for nome, connessioni, riquadro in cose
            if not nome.startswith("sigla") and not (connessioni and connessioni <= proprie)
        ]
        vicine += [(r7._distanza(box, riquadro), nome) for nome, _, riquadro, _ in scritte if riquadro != box]
        distanza, nome = min(vicine)
        punta = etichetta.richiamo.punta
        dalla_freccia = min(r7._distanza((punta.x_mm, punta.y_mm, punta.x_mm, punta.y_mm), f) for f in frecce)
        righe.append(
            f"{etichetta.testo}: la cosa piu' vicina {nome} a {distanza:.2f} mm, "
            f"la punta a {dalla_freccia:.2f} mm dalla freccia di verso piu' vicina"
        )
    return "staccate (un corpo = " + f"{corpo:.2f} mm): " + " · ".join(righe)


def collaudo(lavoro: Path, cartella_base: Path) -> None:
    from disegnatore_mep.layout.geometry import SheetGeometry

    r7 = _collaudo_di_rel007()
    simboli, catalogo, cartiglio = _strumenti()
    USCITA.mkdir(exist_ok=True)
    for nome, impianto, grafo, piano, dati in r7.tavole():
        modello = r7.con_i_dati(grafo, impianto, dati)
        esito, foglio, svg, dxf = r7.esegui(nome, modello, piano, simboli, catalogo, cartiglio, USCITA)
        _, _, svg2, dxf2 = r7.esegui(nome, modello, piano, simboli, catalogo, cartiglio, lavoro / "seconda")
        prima = SheetGeometry.model_validate_json((cartella_base / f"{nome}.json").read_text(encoding="utf-8"))
        frame = esito.frame
        pdf = USCITA / f"{nome}.pdf"
        subprocess.run(["bash", str(ROOT / "scripts" / "to-pdf.sh"), str(svg), str(pdf)], check=True)
        formato = {420.0: "A3", 594.0: "A2", 841.0: "A1"}[frame.standard.sheet_width_mm]
        print(f"\n== {nome} — {grafo.name}, formato {formato}")

        # Il corpo delle scritte, nell'SVG e nel DXF.
        nell_svg = _corpi_dell_svg(svg)
        nel_dxf = _corpi_del_dxf(dxf)
        print(
            f"   SVG: disegno {_intervallo(nell_svg['disegno'])} · tabella {_intervallo(nell_svg['tabella'])} · "
            f"cartiglio {_intervallo(nell_svg['cartiglio'])}"
        )
        print(
            f"   DXF: disegno {_intervallo(nel_dxf['disegno'])} · tabella {_intervallo(nel_dxf['tabella'])} · "
            f"cartiglio {_intervallo(nel_dxf['cartiglio'])} · caratteri {nel_dxf['caratteri']}"
        )
        print(
            f"   carattere: radice {nell_svg['radice'][0]!r}; scritte del disegno che ne dichiarano un "
            f"altro: {nell_svg['famiglie'] or 'nessuna'}"
        )

        # Sigle e DN, contro main.
        def per_ruolo(geometria: SheetGeometry) -> dict[str, int]:
            conto: dict[str, int] = {}
            for etichetta in geometria.labels:
                conto[etichetta.role] = conto.get(etichetta.role, 0) + 1
            return conto

        sigle_prima = {(x.role, x.text) for x in prima.labels}
        sigle_ora = {(x.role, x.text) for x in foglio.labels}
        dn_prima = {frozenset(x.connection_ids) for x in prima.diametri}
        dn_ora = {frozenset(x.connection_ids) for x in foglio.diametri}
        a_otto_sigle = sorted(x.text for x in foglio.labels if getattr(x, "corpo_mm", None))
        con_richiamo = sorted(x.text for x in foglio.labels if x.leader_from is not None or getattr(x, "richiamo", None))
        print(
            f"   scritte accanto ai pezzi: main {per_ruolo(prima)} · ora {per_ruolo(foglio)} · "
            f"mancano {sorted(t for _, t in sigle_prima - sigle_ora) or 'nessuna'} · "
            f"a 8 pt {a_otto_sigle or 'nessuna'} · con richiamo {con_richiamo or 'nessuna'}"
        )
        from disegnatore_mep.diametri.tratti import tratti_da_etichettare

        a_otto = sum(1 for x in foglio.diametri if getattr(x, "corpo_mm", None))
        staccati = sorted(x.testo for x in foglio.diametri if getattr(x, "richiamo", None))
        tratti = tratti_da_etichettare(modello, catalogo)
        mancanti = [x for x in tratti if x.connection_ids not in dn_ora]
        principali = [x.scritta for x in mancanti if x.strada_principale]
        secondari = [f"{x.scritta} {x.capi[0].component_id}→{x.capi[1].component_id}" for x in mancanti if not x.strada_principale]
        print(
            f"   DN: main {len(prima.diametri)} · ora {len(foglio.diametri)} (a 8 pt {a_otto}, staccati con "
            f"freccia {staccati or 'nessuno'}) · mancano sulle strade principali {principali or 'nessuno'} · "
            f"sacrificati sulle secondarie {len(secondari)} {secondari if secondari else ''}"
        )
        del dn_prima

        # Il disegno non si muove.
        uguali = {
            "simboli": [s.model_dump() for s in foglio.symbols] == [s.model_dump() for s in prima.symbols],
            "tratte": [r.model_dump() for r in foglio.routes] == [r.model_dump() for r in prima.routes],
        }
        tabella = (
            f"{prima.tabella.larghezza_mm:.1f}x{prima.tabella.altezza_mm:.1f} → "
            f"{foglio.tabella.larghezza_mm:.1f}x{foglio.tabella.altezza_mm:.1f} mm"
            if prima.tabella is not None and foglio.tabella is not None
            else "—"
        )
        print(
            "   rispetto a main: "
            + ", ".join(f"{k} {'uguali' if v else 'DIVERSI'}" for k, v in uguali.items())
            + f" · tabella {tabella} · voci della legenda {len(foglio.legend)} + {len(foglio.network_keys)}"
            + f" · riga «Øi»: {'si' if foglio.note_della_legenda else 'no'}"
        )

        # I DN non toccano niente (le misure di REL-007, al corpo nuovo).
        corpo = frame.standard.text_small_mm
        from disegnatore_mep.layout.diametri import riquadro_del_diametro

        cose = r7.ostacoli(foglio, corpo)
        toccate = []
        piu_vicina = (math.inf, "")
        for etichetta in foglio.diametri:
            box = riquadro_del_diametro(etichetta, corpo)
            proprie = frozenset(etichetta.connection_ids)
            for nome_cosa, connessioni, riquadro in cose:
                if connessioni and connessioni <= proprie:
                    continue
                if r7._sovrapposti(box, riquadro):
                    toccate.append(f"{etichetta.testo} su {nome_cosa}")
                d = r7._distanza(box, riquadro)
                if d < piu_vicina[0]:
                    piu_vicina = (d, f"{etichetta.testo} da {nome_cosa}")
        print(
            f"   i DN toccano qualcosa: {len(toccate)} {toccate if toccate else ''}— la cosa piu' vicina: "
            f"{piu_vicina[1]} a {piu_vicina[0]:.2f} mm"
        )
        print(f"   {_rispetto(foglio, corpo)}")
        print(f"   {_sigle_vicine_ad_altri(foglio, corpo)}")
        print(f"   {_staccate(foglio, corpo, cose, r7)}")
        print(
            f"   deterministico: SVG {'uguale' if svg.read_bytes() == svg2.read_bytes() else 'DIVERSO'} "
            f"({r7.impronta(svg)}), DXF {'uguale' if dxf.read_bytes() == dxf2.read_bytes() else 'DIVERSO'} "
            f"({r7.impronta(dxf)})"
        )
        rilievi = [f"{item.code} ({item.severity.value})" for item in esito.rilievi]
        print(f"   preflight: {rilievi or 'nessun rilievo'}")
        svg.unlink()
    print("\n" + json.dumps({"tavole": str(USCITA.relative_to(ROOT))}))


if __name__ == "__main__":
    if sys.argv[1] == "--base":
        base(Path(sys.argv[2]))
    else:
        collaudo(Path(sys.argv[1]), Path(sys.argv[2]))
