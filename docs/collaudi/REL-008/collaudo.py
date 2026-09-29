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
        print(
            f"   scritte accanto ai pezzi: main {per_ruolo(prima)} · ora {per_ruolo(foglio)} · "
            f"mancano {sorted(t for _, t in sigle_prima - sigle_ora) or 'nessuna'}"
        )
        a_otto = sum(1 for x in foglio.diametri if getattr(x, "corpo_mm", None))
        print(
            f"   DN: main {len(prima.diametri)} · ora {len(foglio.diametri)} (al minimo di 8 pt: {a_otto})"
            f" · mancano {len(dn_prima - dn_ora)}"
            f"{' ' + str(sorted(x.testo for x in prima.diametri if frozenset(x.connection_ids) in dn_prima - dn_ora)) if dn_prima - dn_ora else ''}"
        )

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
