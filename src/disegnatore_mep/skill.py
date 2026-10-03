"""Il comando della skill: il lavoro deterministico, in un comando solo (REL-001).

La skill che il progettista lancia in Claude ha tre pezzi fatti da un agente —
Capire, Comporre, Rivedere — e il resto e' questo comando
(`docs/ARCHITETTURA-DEL-PIANO.md` §1):

- `valida` il grafo di prima stesura che Capire scrive, e ne elenca le domande;
- `completa` il grafo con le regole degli accessori, e dice che cosa ha aggiunto e
  perche', e che cosa non ha potuto aggiungere: il progettista approva su questo;
- `disegna` la tavola dal piano che Comporre scrive: la esegue, la misura — il
  preflight e le regole del piano —, e la scrive in SVG, **PDF** e DXF, **con i
  rilievi accanto**, per il progettista. I controlli sono della skill, non della
  sessione che la sviluppa (**I-166**);
- `catalogo` stampa le voci fra cui Capire sceglie, una riga per voce, o una voce
  intera; `simbolo` il manifesto di un simbolo; `pezzi` i pezzi che il piano posa;
- `anteprima` fa della tavola un'immagine, per guardarla; `consegna` copia i file
  per il progettista;
- `ambiente` dice che cosa l'ambiente ha e che cosa no.

**Non chiede niente e non decide niente**: dove serve una scelta, la dice. Le
cartelle dei dati — simboli, catalogo, regole, nomi, cartiglio — le riceve da chi
lo lancia: nella skill vengono dalla cartella della skill, dove simboli, catalogo e
regole stanno in un file ciascuno (`FASCI`), nel repository sono quelle del
repository.
"""

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graphics.cartiglio import (
    Cartiglio,
    CartiglioDellaTavola,
    rilievi_del_cartiglio,
    valori_del_cartiglio,
)
from disegnatore_mep.graphics.pdf import scrivi_pdf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet, stati_della_tavola
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import ApprovalStatus, IssueSeverity
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import PianoDiComposizione, carica_piano
from disegnatore_mep.piano.revisore import misura
from disegnatore_mep.rules.apply import saturation
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.proposal import RuleProposal
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.report import CATEGORY_LABELS, build_report
from disegnatore_mep.validation.issues import ValidationIssue
from disegnatore_mep.validation.regole import rilievi_delle_regole
from disegnatore_mep.validation.topology import validate_project

GRAVITA: dict[IssueSeverity, str] = {
    IssueSeverity.BLOCKING: "Bloccanti — la tavola non si consegna",
    IssueSeverity.APPROVAL: "Da approvare — il progettista decide",
    IssueSeverity.WARNING: "Avvisi — la tavola si consegna, e si sa",
}

ESTENSIONI_DA_CONSEGNARE = (".pdf", ".dxf", ".svg", ".jpg", ".md")


@dataclass(frozen=True)
class Cartelle:
    """Dove stanno i dati che il comando legge."""

    simboli: Path
    catalogo: Path
    regole: Path
    naming: Path
    cartiglio: Path
    """Il modello del cartiglio Nove C, con il logo accanto (REL-002)."""


FASCI = ("simboli", "catalogo", "regole")
"""I dati che legge solo il comando. Nella skill ognuno sta **in un file solo**,
`dati/<nome>.json`: il caricamento su claude.ai accetta al massimo 200 file, e questi
tre da soli ne erano 183 (I-188). Il comando li riapre da se' (`apri_i_fasci`)."""


def fascio_della_cartella(cartella: Path, nome: str) -> str:
    """Una cartella di dati in un file solo, leggibile: ogni JSON come il suo oggetto, ogni
    altro file — i disegni dei simboli — come il suo testo, esatto. Lo scrive la
    costruzione della skill (`scripts/costruisci-skill.py`)."""
    file: dict[str, object] = {}
    for percorso in sorted(cartella.iterdir()):
        if not percorso.is_file():
            raise ValueError(f"{percorso}: un fascio raccoglie solo file, non cartelle")
        testo = percorso.read_text(encoding="utf-8")
        file[percorso.name] = json.loads(testo) if percorso.suffix == ".json" else testo
    return json.dumps({"fascio": nome, "file": file}, ensure_ascii=False, indent=1) + "\n"


def apri_i_fasci(dati: Path) -> Path:
    """I fasci della skill riaperti in una cartella temporanea — una cartella per
    sottocartella del fascio —, una volta sola per contenuto: l'impronta dei fasci e'
    nel nome della cartella. La cartella della skill puo' essere di sola lettura, quella
    temporanea no."""
    fasci = [dati / f"{nome}.json" for nome in FASCI]
    impronta = hashlib.sha256(b"".join(f.read_bytes() for f in fasci)).hexdigest()[:16]
    aperti = Path(tempfile.gettempdir()) / "disegnatore-mep" / f"dati-{impronta}"
    if aperti.is_dir():
        return aperti
    provvisoria = aperti.with_name(f"{aperti.name}.{os.getpid()}")
    shutil.rmtree(provvisoria, ignore_errors=True)
    try:
        for fascio in fasci:
            contenuto = json.loads(fascio.read_text(encoding="utf-8"))
            cartella = provvisoria / contenuto["fascio"]
            cartella.mkdir(parents=True)
            for nome, valore in contenuto["file"].items():
                if Path(nome).name != nome or nome.startswith("."):
                    raise ValueError(f"{fascio}: nome di file non ammesso in un fascio: {nome!r}")
                testo = valore if isinstance(valore, str) else json.dumps(valore, ensure_ascii=False, indent=2) + "\n"
                (cartella / nome).write_text(testo, encoding="utf-8")
    except BaseException:
        shutil.rmtree(provvisoria, ignore_errors=True)
        raise
    try:
        provvisoria.rename(aperti)
    except OSError:
        # Un'altra chiamata l'ha riaperta nello stesso momento: vale la sua, che e' uguale.
        shutil.rmtree(provvisoria, ignore_errors=True)
    return aperti


def cartelle_della_skill(radice: Path) -> Cartelle:
    """Le cartelle dei dati della skill: i fasci riaperti, e i file che stanno da soli."""
    dati = radice / "dati"
    aperti = apri_i_fasci(dati)
    return Cartelle(
        simboli=aperti / "simboli",
        catalogo=aperti / "catalogo",
        regole=aperti / "regole",
        naming=dati / "naming",
        cartiglio=dati / "cartiglio" / "Cartiglio_NoveC_A3.json",
    )


def cartelle_del_repository(radice: Path) -> Cartelle:
    """Le stesse cartelle, dove stanno nel repository."""
    return Cartelle(
        simboli=radice / "assets" / "symbols",
        catalogo=radice / "examples" / "layout" / "catalog",
        regole=radice / "rules" / "hydronic",
        naming=radice / "naming",
        cartiglio=radice / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json",
    )


class _Dati:
    """I dati caricati una volta sola, quando il comando li chiede."""

    def __init__(self, cartelle: Cartelle) -> None:
        self.cartelle = cartelle
        self.simboli = SymbolRegistry.from_directory(cartelle.simboli)
        self.catalogo = ComponentRegistry.from_directory(cartelle.catalogo, symbols=self.simboli)
        self.naming = Naming.from_directory(cartelle.naming)


# --- valida -----------------------------------------------------------------


def _stampa_rilievi(rilievi: Sequence[ValidationIssue]) -> None:
    for gravita, titolo in GRAVITA.items():
        gruppo = [item for item in rilievi if item.severity == gravita]
        if not gruppo:
            continue
        print(f"\n{titolo}")
        for item in gruppo:
            print(f"  - {item.message}")
            print(f"    codice: {item.code} · {', '.join(item.entity_ids)}")


def _domande(modello: ProjectModel) -> list[str]:
    return [
        f"{item.id}: {item.text}"
        for item in modello.assumptions
        if item.status == ApprovalStatus.PROPOSED
    ]


def _valida(args: argparse.Namespace, cartelle: Cartelle) -> int:
    """Il grafo di Capire carica, e regge contro il catalogo? E che cosa chiede?"""
    dati = _Dati(cartelle)
    modello = load_project(args.grafo)
    esito = validate_project(modello, dati.catalogo)
    print(
        f"Il grafo si legge: {len(modello.components)} pezzi, {len(modello.connections)} "
        f"tubazioni, {len(modello.networks)} reti; regime della centrale: "
        f"{modello.plant_regime.value if modello.plant_regime else 'non dichiarato'}."
    )
    if not esito.ok:
        print("\nIl grafo non regge contro il catalogo: si corregge e si rilancia.")
        _stampa_rilievi(esito.issues)
        return 2
    _stampa_rilievi(esito.issues)
    domande = _domande(modello)
    if domande:
        print(f"\nAssunzioni e domande ancora da confermare ({len(domande)}):")
        for domanda in domande:
            print(f"  - {domanda}")
    else:
        print("\nNessuna assunzione da confermare.")
    return 0


# --- completa ---------------------------------------------------------------


def _completa(args: argparse.Namespace, cartelle: Cartelle) -> int:
    """Le regole degli accessori sul grafo: che cosa aggiungono, e perche'."""
    dati = _Dati(cartelle)
    modello = load_project(args.grafo)
    esito = validate_project(modello, dati.catalogo)
    if not esito.ok:
        print("Il grafo non regge contro il catalogo: si corregge prima di completarlo.")
        _stampa_rilievi(esito.issues)
        return 2
    regole = RuleRegistry.from_directory(cartelle.regole)
    regole.cross_check(dati.catalogo)
    risultato = saturation(modello, dati.catalogo, regole)
    completo, proposte, lacune = risultato.model, risultato.applied, risultato.gaps
    rapporto = build_report(proposte, lacune, dati.naming)

    in_piu = len(completo.components) - len(modello.components)
    print(
        f"Le regole hanno aggiunto {len(proposte)} accessori; con i raccordi e i confini che li "
        f"reggono, il grafo passa da {len(modello.components)} a {len(completo.components)} pezzi "
        f"(+{in_piu})."
    )
    for categoria, etichetta in CATEGORY_LABELS.items():
        voci = rapporto.of(categoria)
        if not voci:
            continue
        print(f"\n{etichetta} ({len(voci)})")
        # Una regola che mette dodici valvole ha una ragione sola: si dice una volta,
        # e sotto i dodici posti. Ripeterla dodici volte non la rende piu' vera.
        # Accanto a ogni posto il nome del pezzo nel grafo completo: e' quello con
        # cui il progettista lo toglie (`accessori_tolti`, I-192).
        della_categoria = [item for item in proposte if item.category == categoria]
        gruppi: dict[tuple[str, str], list[str]] = {}
        for voce, proposta in zip(voci, della_categoria, strict=True):
            gruppi.setdefault((voce.name, voce.rule), []).append(
                f"{voce.where} — {proposta.component_id}"
            )
        for (nome, regola), dove in gruppi.items():
            voce = next(v for v in voci if (v.name, v.rule) == (nome, regola))
            print(f"  - {nome} — {len(dove)} {'pezzo' if len(dove) == 1 else 'pezzi'}")
            for posto in dove:
                print(f"      {posto}")
            print(f"    perche': {voce.rationale}")
            print(f"    fonte: {voce.source} · regola: {regola}")
    if not rapporto.open_points:
        print("\nPunti aperti: nessuno.")
    else:
        # Un accessorio che servirebbe e che non si puo' proporre e' una domanda
        # al progettista: si stampa sempre, anche quando il resto e' a posto.
        print("\nPunti aperti — accessori che servirebbero e che non si possono proporre")
        for punto in rapporto.open_points:
            print(f"  - {punto.name} — {punto.where}")
            print(f"    {punto.what_is_missing}")
            print(f"    perche' servirebbe: {punto.rationale}")
            print(f"    fonte: {punto.source} · regola: {punto.rule}")

    _stampa_le_scelte_del_progettista(modello, risultato.withheld, proposte, dati)

    verdetto = validate_project(completo, dati.catalogo)
    if not verdetto.ok:
        print("\nIl grafo completato non regge: e' un difetto delle regole, non del grafo.")
        _stampa_rilievi(verdetto.issues)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(canonical_json(completo), encoding="utf-8")
    # Il grafo da leggere accanto non si scrive piu': il progettista non lo leggeva, e
    # approva sull'elenco qui sopra (I-186).
    print(f"\nGrafo completo: {args.out}")
    domande = _domande(completo)
    if domande:
        print(f"\nAssunzioni ancora da confermare ({len(domande)}):")
        for domanda in domande:
            print(f"  - {domanda}")
    return 0


def _stampa_le_scelte_del_progettista(
    modello: ProjectModel, tolte: Sequence[RuleProposal], applicate: Sequence[RuleProposal], dati: _Dati
) -> None:
    """Quello che il progettista ha tolto o dichiarato a bordo, detto a ogni rilancio
    (REL-009, I-192): per famiglia, con il motivo; e le sue voci che non hanno effetto."""
    motivi = {item.pezzo: item.motivo for item in modello.accessori_tolti}
    if motivi:
        print(f"\nTolti dal progettista ({len(tolte)}) — le regole li metterebbero, il grafo non li porta")
        gruppi: dict[tuple[str, str], list[str]] = {}
        for proposta in tolte:
            gruppi.setdefault((proposta.name, motivi[proposta.component_id]), []).append(
                f"su {proposta.anchor.component_id}.{proposta.anchor.port_id}, rete "
                f"{proposta.network_id} — {proposta.component_id}"
            )
        for (nome, motivo), dove in gruppi.items():
            print(f"  - {nome} — {len(dove)} {'pezzo' if len(dove) == 1 else 'pezzi'}")
            for posto in dove:
                print(f"      {posto}")
            print(f"    motivo: {motivo}")
        trovati = {item.component_id for item in tolte}
        a_vuoto = [voce.pezzo for voce in modello.accessori_tolti if voce.pezzo not in trovati]
        if a_vuoto:
            print(
                f"\nAccessori tolti che non tolgono niente ({len(a_vuoto)}) — nessuna regola posa "
                "un pezzo con questo nome: si correggono con il nome che il pezzo ha nel grafo completo"
            )
            for pezzo in a_vuoto:
                print(f"  - {pezzo}")
    # Dove una regola vuole il pezzo anche se la macchina lo porta dentro — la
    # sicurezza di ogni generatore, D-182 —, il bordo dichiarato non basta: si dice,
    # e il progettista sceglie se toglierlo.
    bordo = {item.id: set(item.a_bordo) for item in modello.components if item.a_bordo}
    comunque = sorted(
        (
            item
            for item in applicate
            if bordo.get(item.anchor.component_id, set())
            & set(dati.catalogo.resolve(item.definition_id).definition.functions)
        ),
        key=lambda item: item.component_id,
    )
    if comunque:
        print(
            f"\nDichiarati a bordo, e posati lo stesso ({len(comunque)}) — la regola li vuole anche "
            "dentro la macchina; se sul costruito non ci sono, si tolgono con il loro nome"
        )
        for item in comunque:
            print(
                f"  - {item.name} su {item.anchor.component_id}.{item.anchor.port_id} — "
                f"{item.component_id} · regola: {item.rule_id}@{item.rule_version}"
            )


# --- disegna ----------------------------------------------------------------


def _rilievi_in_parole(
    titolo: str,
    formato: str,
    tratte: int,
    cedute: int,
    preflight: Sequence[ValidationIssue],
    regole: Sequence[ValidationIssue],
    cartiglio: Sequence[str],
    sostituzioni: Sequence[str],
) -> str:
    """I rilievi della tavola, scritti per il progettista: si consegnano col PDF."""
    bloccanti = [item for item in preflight if item.severity == IssueSeverity.BLOCKING]
    righe = [
        f"# Rilievi della tavola — {titolo}",
        "",
        f"Formato **{formato}** · tratte **{tratte}** · tratte cedute **{cedute}** · "
        f"rilievi bloccanti **{len(bloccanti)}**.",
        "",
        "Li misurano i controlli della skill sulla tavola finita: il preflight di qualita' "
        "e le regole del piano. Non sono un giudizio sull'impianto: dicono come e' "
        "disegnato.",
        "",
    ]
    for gravita, nome in GRAVITA.items():
        gruppo = [item for item in preflight if item.severity == gravita]
        righe += [f"## {nome}", ""]
        righe += [f"- {item.message} (`{item.code}` · {', '.join(item.entity_ids)})" for item in gruppo] or [
            "- nessuno"
        ]
        righe.append("")
    righe += ["## Le regole del piano", ""]
    righe += [f"- {item.message} (`{item.code}` · {', '.join(item.entity_ids)})" for item in regole] or [
        "- nessuna violazione"
    ]
    righe += ["", "## Il cartiglio", ""]
    righe += [f"- {riga}" for riga in cartiglio] or ["- compilato per intero"]
    if sostituzioni:
        righe += ["", "## Caratteri che il PDF non ha", ""]
        righe += [f"- {riga}" for riga in sostituzioni]
    return "\n".join(righe) + "\n"


def _ha_ezdxf() -> bool:
    try:
        importlib.import_module("ezdxf")
    except ImportError:
        return False
    return True


def _capi_delle_tratte(errore: str, esito: EsitoDelPiano, piano: PianoDiComposizione) -> list[str]:
    """Per ogni tratta che il messaggio dell'instradamento nomina, i due pezzi che unisce
    e dove il piano li ha messi: il messaggio dice la tratta, chi compone vuole i pezzi."""
    dove = {item.component_id: item.origin for item in esito.posa}
    righe = []
    for tratta in esito.partizione.trunks:
        if not any(re.search(rf"(?<![\w-]){re.escape(c)}(?![\w-])", errore) for c in tratta.connection_ids):
            continue
        capi = []
        for ref in (tratta.start, tratta.end):
            posto = dove.get(ref.component_id)
            nel_piano = "nel piano" if ref.component_id in piano.pezzi else "posato dal motore"
            capi.append(
                f"{ref.component_id}.{ref.port_id}"
                + (f" ({nel_piano} a {posto.x_mm:g}, {posto.y_mm:g})" if posto else "")
            )
        righe.append(f"la tratta {', '.join(tratta.connection_ids)} va da {capi[0]} a {capi[1]}")
    return righe


def _ingombro_della_posa(esito: EsitoDelPiano) -> tuple[float, float]:
    """Larghezza e altezza della posa, in millimetri: dal primo pezzo all'ultimo."""
    if not esito.posa:
        return 0.0, 0.0
    x0 = min(p.origin.x_mm for p in esito.posa)
    y0 = min(p.origin.y_mm for p in esito.posa)
    x1 = max(p.origin.x_mm + p.width_mm for p in esito.posa)
    y1 = max(p.origin.y_mm + p.height_mm for p in esito.posa)
    return x1 - x0, y1 - y0


def _disegna(args: argparse.Namespace, cartelle: Cartelle) -> int:
    """Esegue il piano, misura la tavola e la scrive, con i rilievi accanto."""
    dati = _Dati(cartelle)
    modello = load_project(args.grafo)
    piano = carica_piano(args.piano)
    cartiglio = Cartiglio.da_file(cartelle.cartiglio)
    esito = esegui_piano(modello, piano, dati.catalogo, dati.simboli, cartelle.naming, verifica=args.verifica)

    if esito.girati:
        print("Girati dalla deduzione:")
        for riga in esito.girati:
            print(f"  - {riga}")
    area = esito.frame.drawing_rect_mm
    larghezza, altezza = _ingombro_della_posa(esito)
    # Chi compone deve sapere quanto posto prende la tabella, per giudicare se una posa
    # piu' stretta le passa sotto o accanto nello stesso formato: la camera Opus di
    # REL-001 e' salita all'A2, e lo stesso disegno stava nell'A3.
    tabelle = [f.tabella for f in esito.disegno.sheets if f.tabella] if esito.disegno else []
    tabella = (
        f" ({tabelle[0].larghezza_mm:g} x {tabelle[0].altezza_mm:g} mm)" if len(tabelle) == 1 else ""
    )
    print(
        f"Area del disegno dell'{piano.formato}: {area.width_mm:g} x {area.height_mm:g} mm, "
        f"con la tabella delle apparecchiature in alto a sinistra{tabella}; la posa ne occupa "
        f"{larghezza:g} x {altezza:g}."
    )
    if esito.disegno is None:
        print(f"\nIl piano non si instrada: {esito.errore}")
        for riga in _capi_delle_tratte(esito.errore or "", esito, piano):
            print(f"  - {riga}")
        if larghezza > area.width_mm or altezza > area.height_mm:
            # Il motore porta il disegno al centro dell'area: se non ci sta, le tratte che
            # escono non trovano strada, e il messaggio accusa una tratta innocente.
            print(
                f"  - Probabile causa: la posa ({larghezza:g} x {altezza:g} mm) non sta nell'area "
                f"dell'{piano.formato} ({area.width_mm:g} x {area.height_mm:g}). Stringi la posa o prendi "
                "il formato successivo, prima di spostare la tratta."
            )
        print("\nPosa applicata (i pezzi del piano sono marcati con *):")
        for posato in sorted(esito.posa, key=lambda i: (i.origin.x_mm, i.origin.y_mm)):
            segno = "*" if posato.component_id in piano.pezzi else " "
            print(
                f"  {segno} {posato.component_id:46} {posato.width_mm:5.1f}x{posato.height_mm:5.1f} "
                f"@({posato.origin.x_mm:6.1f},{posato.origin.y_mm:6.1f})"
            )
        return 2

    regole = rilievi_delle_regole(esito.disegno, esito.frame, dati.catalogo, modello)
    _stampa_rilievi(esito.rilievi)
    if regole:
        print("\nLe regole del piano")
        for item in regole:
            print(f"  - {item.message}")
            print(f"    codice: {item.code} · {', '.join(item.entity_ids)}")
    else:
        print("\nLe regole del piano: nessuna violazione.")

    args.out.mkdir(parents=True, exist_ok=True)
    dxf = not args.senza_dxf and _ha_ezdxf()
    scritti: list[Path] = []
    for foglio in esito.disegno.sheets:
        nome = f"{modello.metadata.project_id}-{foglio.sheet_id}"
        svg = args.out / f"{nome}.svg"
        tavola = CartiglioDellaTavola(cartiglio=cartiglio, valori=valori_del_cartiglio(modello, foglio.sheet_id))
        svg.write_text(render_sheet(foglio, esito.frame, dati.simboli, tavola), encoding="utf-8")
        pdf = scrivi_pdf(svg, titolo=f"{modello.metadata.project_name} — {foglio.sheet_id}")
        scritti += [svg.with_suffix(".pdf"), svg]
        if dxf:
            from disegnatore_mep.graphics.dxf import write_dxf

            scritti += list(write_dxf(foglio, esito.frame, dati.simboli, svg.with_suffix(".dxf"), tavola))
        sul_cartiglio = rilievi_del_cartiglio(tavola, esito.frame, stati_della_tavola(foglio))
        sostituzioni = [
            f"{s.carattere!r} in «{s.scritta}»: nel PDF e' scritto «?»" for s in pdf.sostituzioni
        ]
        rilievi = args.out / f"{nome}-rilievi.md"
        rilievi.write_text(
            _rilievi_in_parole(
                foglio.title,
                piano.formato,
                len(foglio.routes),
                sum(1 for tratta in foglio.routes if tratta.unresolved),
                esito.rilievi,
                regole,
                sul_cartiglio,
                sostituzioni,
            ),
            encoding="utf-8",
        )
        scritti.append(rilievi)
        for riga in sul_cartiglio:
            print(f"\nCartiglio: {riga}")
        for riga in sostituzioni:
            print(f"\nPDF: {riga}")
    if args.geometria:
        args.geometria.parent.mkdir(parents=True, exist_ok=True)
        args.geometria.write_text(esito.disegno.model_dump_json(indent=2) + "\n", encoding="utf-8")

    print("\nFile scritti:")
    for percorso in scritti:
        print(f"  - {percorso}")
    if not dxf:
        print(
            "  (il DXF non c'e': "
            + ("chiesto senza" if args.senza_dxf else "manca la libreria ezdxf")
            + ")"
        )
    codici = Counter(item.code for item in [*esito.rilievi, *regole])
    punti = misura(esito, [*esito.rilievi, *regole])
    print(
        f"\nFormato {piano.formato} · tratte {sum(len(f.routes) for f in esito.disegno.sheets)} · "
        f"tratte cedute {len(esito.cedute)} · rilievi bloccanti {len(esito.bloccanti)} · "
        f"pieghe {punti.pieghe} · sormonti {punti.incroci} · "
        f"avvisi e regole: {', '.join(f'{c} x{n}' for c, n in sorted(codici.items())) or 'nessuno'}"
    )
    if esito.bloccanti or esito.cedute:
        print("\nLa tavola non si consegna: c'e' un rilievo bloccante o una tratta ceduta (D-063).")
        return 2
    return 0


# --- catalogo, anteprima, ambiente ---------------------------------------------


def _pezzi(args: argparse.Namespace, cartelle: Cartelle) -> int:
    """I pezzi del grafo completo, divisi come li divide Comporre: quelli che il piano posa,
    con ingombro, rotazioni ammesse e porte; e quelli in linea, che posa il motore."""
    dati = _Dati(cartelle)
    modello = load_project(args.grafo)
    da_posare: list[str] = []
    in_linea: list[str] = []
    for pezzo in modello.components:
        voce = dati.catalogo.get(pezzo.definition_id)
        simbolo = dati.simboli.get(voce.symbol_id).manifest
        porte = ", ".join(f"{p.id} {p.face} ({p.x_mm:g}, {p.y_mm:g})" for p in simbolo.ports)
        riga = (
            f"{pezzo.id} — {voce.name} · simbolo {simbolo.id} {simbolo.width_mm:g} x "
            f"{simbolo.height_mm:g} · rotazioni {', '.join(str(r) for r in simbolo.allowed_rotations_deg)}"
            f"\n    porte: {porte}"
        )
        (in_linea if simbolo.inline_gap_mm is not None else da_posare).append(riga)
    print(f"Da posare nel piano ({len(da_posare)}):")
    print("\n".join(f"  {r}" for r in da_posare))
    print(f"\nIn linea, li posa il motore sulla loro tratta ({len(in_linea)}): non vanno nel piano.")
    print("\n".join(f"  {r.splitlines()[0]}" for r in in_linea))
    return 0


def _riga_del_catalogo(voce: dict[str, object]) -> str:
    """Una voce del catalogo in una riga e mezza: quello su cui Capire sceglie."""
    mestieri = ", ".join(str(m) for m in voce.get("functions", []))  # type: ignore[attr-defined]
    extra = []
    variante = voce.get("variant")
    if isinstance(variante, dict):
        extra.append(f"variante di {variante.get('of')}, se il testo dice: {', '.join(variante.get('named_as', []))}")
    if voce.get("carries_on_board"):
        extra.append("a bordo: " + ", ".join(str(m) for m in voce["carries_on_board"]))  # type: ignore[attr-defined]
    if voce.get("stored_medium"):
        extra.append(f"tiene in serbo: {voce['stored_medium']}")
    if voce.get("fills_from"):
        extra.append(f"si riempie da: {voce['fills_from']}")
    attacchi = []
    for porta in voce.get("ports", []):  # type: ignore[attr-defined]
        segni = [str(porta.get("flow", "?")), str(porta.get("medium", porta.get("domain", "?")))]
        if porta.get("stub"):
            segni.append("di servizio")
        if porta.get("required") is False:
            segni.append("facoltativo")
        attacchi.append(f"{porta['id']} ({', '.join(segni)})")
    righe = f"{voce['id']} — {voce.get('name', '')} · mestieri: {mestieri}"
    if extra:
        righe += " · " + " · ".join(extra)
    return righe + f"\n    attacchi: {', '.join(attacchi)}"


def _voce_intera(cartella: Path, ident: str, che_cosa: str, come_cercarla: str) -> int:
    """Il file intero di una voce — del catalogo o dei simboli —, come lo legge il motore."""
    percorso = cartella / f"{ident}.json"
    if Path(ident).name != ident or not percorso.is_file():
        print(f"Nessun{che_cosa} «{ident}»: {come_cercarla}.")
        return 1
    print(percorso.read_text(encoding="utf-8"), end="")
    return 0


def _simbolo(args: argparse.Namespace, cartelle: Cartelle) -> int:
    """Il manifesto di un simbolo: ingombro, porte con le loro quote, rotazioni ammesse."""
    return _voce_intera(
        cartelle.simboli, args.simbolo, " simbolo",
        "il simbolo di un pezzo e' il campo symbol_id della sua voce, `mep.py catalogo <id>`",
    )


def _catalogo(args: argparse.Namespace, cartelle: Cartelle) -> int:
    """Le voci del catalogo, una riga ciascuna: id, nome, mestieri, attacchi. Con l'id di
    una voce, la voce intera."""
    if args.voce:
        return _voce_intera(
            cartelle.catalogo, args.voce, "a voce del catalogo",
            "le voci si cercano con `mep.py catalogo --cerca <parola>`",
        )
    trovate = 0
    for percorso in sorted(cartelle.catalogo.glob("*.json")):
        voce = json.loads(percorso.read_text(encoding="utf-8"))
        if args.mestiere and args.mestiere not in voce.get("functions", []):
            continue
        if args.cerca and not any(
            args.cerca.lower() in str(campo).lower() for campo in (voce["id"], voce.get("name", ""))
        ):
            continue
        trovate += 1
        print(_riga_del_catalogo(voce))
    if not trovate:
        # Una voce che manca e' un pezzo che non si disegna (Capire, tipo B): dirlo
        # subito evita di sceglierne una che somiglia.
        cercata = " e ".join(f"«{v}»" for v in (args.cerca, args.mestiere) if v)
        print(f"Nessuna voce del catalogo per {cercata}: quel pezzo il catalogo non ce l'ha.")
    return 0


def _png(larghezza: int, altezza: int, righe: Sequence[bytes]) -> bytes:
    """Un PNG a colori da righe RGB, con la sola libreria standard."""

    def blocco(tipo: bytes, dati: bytes) -> bytes:
        corpo = tipo + dati
        return len(dati).to_bytes(4, "big") + corpo + zlib.crc32(corpo).to_bytes(4, "big")

    intestazione = larghezza.to_bytes(4, "big") + altezza.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0])
    grezzo = b"".join(b"\x00" + riga for riga in righe)
    return (
        b"\x89PNG\r\n\x1a\n"
        + blocco(b"IHDR", intestazione)
        + blocco(b"IDAT", zlib.compress(grezzo, 6))
        + blocco(b"IEND", b"")
    )


def anteprima(
    sorgente: Path, destinazione: Path, dpi: int, zona: tuple[float, float, float, float] | None = None
) -> str | None:
    """La tavola come immagine PNG, con quello che l'ambiente ha. Dice con che cosa
    l'ha fatta, o `None` se non ha niente con cui farla.

    `zona` e' un riquadro in millimetri del foglio — da sinistra, dall'alto —: un A2 intero
    a 110 dpi non fa leggere una valvola, un suo pezzo a 300 si'."""
    pdf = sorgente if sorgente.suffix == ".pdf" else sorgente.with_suffix(".pdf")
    if not pdf.exists():
        scrivi_pdf(sorgente, pdf)
    punti = None if zona is None else tuple(v * 72 / 25.4 for v in zona)
    try:
        fitz = importlib.import_module("fitz")
        pagina = fitz.open(pdf)[0]
        ritaglio = fitz.Rect(*punti) if punti else None
        pagina.get_pixmap(dpi=dpi, clip=ritaglio).save(destinazione)
        return "PyMuPDF"
    except ImportError:
        pass
    try:
        pdfium = importlib.import_module("pypdfium2")
        pagina = pdfium.PdfDocument(str(pdf))[0]
        taglio = (0.0, 0.0, 0.0, 0.0)
        if punti:
            larghezza, altezza = pagina.get_size()
            # pypdfium2 vuole quanto togliere da sinistra, sotto, destra e sopra.
            taglio = (punti[0], altezza - punti[3], larghezza - punti[2], punti[1])
        immagine = pagina.render(scale=dpi / 72, rev_byteorder=True, crop=taglio)
        dati = bytes(immagine.buffer)
        passo, riga = immagine.stride, immagine.width * immagine.n_channels
        if immagine.n_channels != 3:
            raise ValueError(f"pypdfium2 ha reso {immagine.n_channels} canali invece di 3")
        destinazione.write_bytes(
            _png(immagine.width, immagine.height,
                 [dati[y * passo : y * passo + riga] for y in range(immagine.height)])
        )
        return "pypdfium2"
    except ImportError:
        pass
    programma = shutil.which("pdftoppm")
    if programma:
        radice = destinazione.with_suffix("")
        riquadro: list[str] = []
        if punti:
            px = [round(v * dpi / 72) for v in punti]
            riquadro = ["-x", str(px[0]), "-y", str(px[1]), "-W", str(px[2] - px[0]), "-H", str(px[3] - px[1])]
        subprocess.run(
            [programma, "-png", "-r", str(dpi), "-singlefile", *riquadro, str(pdf), str(radice)],
            check=True,
            capture_output=True,
        )
        return "pdftoppm"
    return None


def _anteprima(args: argparse.Namespace, cartelle: Cartelle) -> int:
    zona = None
    if args.zona:
        valori = [float(v) for v in args.zona.split(",")]
        if len(valori) != 4 or valori[0] >= valori[2] or valori[1] >= valori[3]:
            raise ValueError(f"--zona vuole x0,y0,x1,y1 in millimetri, con x0 < x1 e y0 < y1: {args.zona}")
        zona = (valori[0], valori[1], valori[2], valori[3])
    destinazione = args.out or args.tavola.with_suffix(".png" if zona is None else ".zona.png")
    con = anteprima(args.tavola, destinazione, args.dpi, zona)
    if con is None:
        print(
            "Nessun programma per fare della tavola un'immagine (ne' PyMuPDF, ne' "
            "pypdfium2, ne' pdftoppm): la tavola si guarda nel PDF."
        )
        return 1
    print(f"Anteprima: {destinazione} (con {con}, {args.dpi} dpi)")
    return 0


def _ambiente(args: argparse.Namespace, cartelle: Cartelle) -> int:
    import pydantic

    print(f"Python {sys.version.split()[0]} · pydantic {pydantic.VERSION}")
    print(f"Motore: {Path(__file__).resolve().parent}")
    print(f"DXF: {'si' if _ha_ezdxf() else 'no, manca ezdxf: la tavola esce in PDF e SVG'}")
    rasterizzatori = [
        nome for nome in ("fitz", "pypdfium2") if importlib.util.find_spec(nome) is not None
    ] + (["pdftoppm"] if shutil.which("pdftoppm") else [])
    print(
        "Anteprima PNG: "
        + (", ".join(rasterizzatori) if rasterizzatori else "no — manca un lettore di PDF (pypdfium2 o PyMuPDF)")
    )
    dati = _Dati(cartelle)
    regole = RuleRegistry.from_directory(cartelle.regole)
    print(
        f"Dati: {len(dati.simboli.all())} simboli, "
        f"{len(list(cartelle.catalogo.glob('*.json')))} voci di catalogo, "
        f"{len(regole.all())} regole, cartiglio "
        f"{'si' if cartelle.cartiglio.exists() else 'NO'}"
    )
    print("Pronto.")
    return 0


def consegna(cartella: Path, destinazione: Path) -> list[Path]:
    """Copia nella cartella di consegna i file per il progettista: PDF, DXF col suo
    logo, SVG e rilievi."""
    destinazione.mkdir(parents=True, exist_ok=True)
    copiati = []
    for percorso in sorted(cartella.iterdir()):
        if percorso.is_file() and percorso.suffix in ESTENSIONI_DA_CONSEGNARE:
            copiati.append(Path(shutil.copy2(percorso, destinazione / percorso.name)))
    return copiati


def _consegna(args: argparse.Namespace, cartelle: Cartelle) -> int:
    for percorso in consegna(args.cartella, args.destinazione):
        print(f"Consegnato: {percorso}")
    return 0


# --- il comando ---------------------------------------------------------------


def costruisci_il_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mep.py", description="Il comando della skill Disegnatore MEP."
    )
    comandi = parser.add_subparsers(dest="comando", required=True)

    comandi.add_parser("ambiente", help="che cosa l'ambiente ha, e se il comando e' pronto")

    catalogo = comandi.add_parser("catalogo", help="le voci del catalogo, una riga ciascuna; con un id, la voce intera")
    catalogo.add_argument("voce", nargs="?", help="l'id di una voce: la stampa intera")
    catalogo.add_argument("--mestiere", help="solo le voci che fanno questo mestiere")
    catalogo.add_argument("--cerca", help="solo le voci con questa parola nell'id o nel nome")

    simbolo = comandi.add_parser("simbolo", help="il manifesto di un simbolo: ingombro, porte, rotazioni")
    simbolo.add_argument("simbolo", help="l'id del simbolo (il symbol_id della voce di catalogo)")

    pezzi = comandi.add_parser("pezzi", help="i pezzi da posare nel piano, e quelli che posa il motore")
    pezzi.add_argument("grafo", type=Path, help="il grafo completo")

    valida = comandi.add_parser("valida", help="il grafo di Capire carica e regge?")
    valida.add_argument("grafo", type=Path)

    completa = comandi.add_parser("completa", help="le regole degli accessori sul grafo")
    completa.add_argument("grafo", type=Path)
    completa.add_argument("--out", type=Path, required=True, help="il grafo completo")

    disegna = comandi.add_parser("disegna", help="esegue il piano: tavola, PDF, DXF e rilievi")
    disegna.add_argument("grafo", type=Path, help="il grafo completo")
    disegna.add_argument("--piano", type=Path, required=True)
    disegna.add_argument("--out", type=Path, required=True, help="la cartella della tavola")
    disegna.add_argument("--geometria", type=Path, help="scrive anche la geometria, per le misure")
    disegna.add_argument(
        "--verifica",
        action="store_true",
        help="stampa accanto a ogni pezzo il suo indirizzo (D-110): per guardare, non per consegnare",
    )
    disegna.add_argument("--senza-dxf", action="store_true", help="non scrive il DXF")

    vista = comandi.add_parser("anteprima", help="la tavola come immagine PNG")
    vista.add_argument("tavola", type=Path, help="il PDF o l'SVG della tavola")
    vista.add_argument("--out", type=Path)
    vista.add_argument("--dpi", type=int, default=110)
    vista.add_argument(
        "--zona", help="solo un riquadro del foglio, x0,y0,x1,y1 in millimetri dall'alto a sinistra"
    )

    finale = comandi.add_parser("consegna", help="copia PDF, DXF, SVG e rilievi nella cartella data")
    finale.add_argument("cartella", type=Path)
    finale.add_argument("destinazione", type=Path)
    return parser


def main(argv: Sequence[str] | None, cartelle: Cartelle) -> int:
    """Codici di uscita: `0` fatto, `2` fatto ma c'e' qualcosa che ferma la consegna,
    `1` non si e' potuto fare — un file che non si legge, un dato che manca."""
    args = costruisci_il_parser().parse_args(argv)
    try:
        comando: dict[str, Callable[[argparse.Namespace, Cartelle], int]] = {
            "ambiente": _ambiente,
            "completa": _completa,
            "catalogo": _catalogo,
            "simbolo": _simbolo,
            "pezzi": _pezzi,
            "valida": _valida,
            "disegna": _disegna,
            "anteprima": _anteprima,
            "consegna": _consegna,
        }
        return comando[args.comando](args, cartelle)
    except (OSError, ValidationError, ValueError, RuleError) as errore:
        print(f"Errore: {errore}", file=sys.stderr)
        return 1
