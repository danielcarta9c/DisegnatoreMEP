"""Il documento della distinta in PDF, col motore dei report Nove C (REL-015, I-232).

Il motore e' quello della skill `nove-c-report` del PO, **installata accanto**: si importa
dal suo percorso (`--report <cartella della skill>`), **non si copia** in questo
repository, che e' pubblico. Della skill dei report si usano la copertina
(`nove_c_report_cover.build_cover_pdf`, con `KPI_DATA=()`: niente card dei KPI), il motore
del corpo (`chapter`, `std_table`, `kv_table`, `num_items`, `make_doc`, `fill_report`,
`merge_pdf`, senza «Chi siamo») e il controllo finale (`nove_c_report_qa.qa_pdf`), che
rasterizza le pagine perche' qualcuno le guardi.

Il contenuto non si decide qui: e' `documento.Documento`, gia' scritto. Qui si sceglie
solo come stamparlo: il titolo di un capitolo resta col suo primo blocco e comincia solo
dove c'e' posto anche per l'inizio del secondo; un titoletto va in fondo alla pagina solo
se sotto ci stanno l'intestazione e tre righe della sua tabella, e una tabella lunga
continua alla pagina dopo con l'intestazione ripetuta; una colonna e' almeno larga quanto
la sua parola piu' lunga, e le tabelle con le stesse colonne hanno le stesse larghezze.

Se il motore non c'e', o non si carica (manca una libreria che vuole), la distinta lo
dice e scrive lo stesso contenuto in Markdown (`scrivi_il_documento`).
"""

import contextlib
import hashlib
import importlib.util
import io
import re
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any
from xml.sax.saxutils import escape

from .documento import (
    Blocco,
    Capitolo,
    Chiavi,
    Copertina,
    Documento,
    Elenco,
    Paragrafo,
    Tabella,
    documento_in_markdown,
)

FILE_DEL_MOTORE = {
    "copertina": "nove_c_report_cover.py",
    "corpo": "nove_c_report_engine.py",
    "controllo": "nove_c_report_qa.py",
}
"""I tre file della skill dei report che servono, nella sua cartella `references/`."""

PER_IL_CARATTERE = (("→", "-"), ("⌀", "Ø"))
"""Poppins, il carattere dei report, non ha «→» (misurato sul file della skill rev9)."""

IMBOTTITURA_PT = 6.0
"""Il margine sinistro e destro di una cella di `std_table` (rev9)."""


class MotoreAssente(Exception):
    """Il motore dei report non c'e' al percorso dato, o non si carica."""


@dataclass(frozen=True)
class Motore:
    cartella: Path
    copertina: ModuleType
    corpo: ModuleType
    controllo: ModuleType
    avvisi: tuple[str, ...] = ()
    """Quello che il motore ha detto caricandosi (un carattere che non trova)."""


@dataclass
class EsitoDelPdf:
    pdf: Path
    pagine: list[Path] = field(default_factory=list)
    """Le immagini delle pagine che `qa_pdf` ha scritto: da guardare una per una."""
    avvisi: list[str] = field(default_factory=list)
    """Gli avvisi della copertina, di `fill_report` e di `qa_pdf`: da risolvere, o da
    verificare a vista e dire."""


def cartella_del_motore(percorso: Path) -> Path | None:
    """La cartella coi file del motore: `<skill>/references`, o la cartella data."""
    for cartella in (percorso / "references", percorso):
        if all((cartella / nome).is_file() for nome in FILE_DEL_MOTORE.values()):
            return cartella
    return None


_CARICATI: dict[Path, Motore] = {}


def _avvisi_nel_testo(testo: str) -> list[str]:
    return [riga.strip() for riga in testo.splitlines() if "⚠" in riga or "❌" in riga]


def carica_il_motore(percorso: Path) -> Motore:
    """Il motore dei report dal percorso della skill (o della sua cartella `references`).
    I moduli si caricano sotto un nome proprio, una volta per cartella."""
    cartella = cartella_del_motore(percorso)
    if cartella is None:
        raise MotoreAssente(
            f"in {percorso} non c'e' il motore dei report Nove C (references/ con "
            f"{', '.join(FILE_DEL_MOTORE.values())})"
        )
    cartella = cartella.resolve()
    if cartella in _CARICATI:
        return _CARICATI[cartella]
    impronta = hashlib.sha256(str(cartella).encode("utf-8")).hexdigest()[:12]
    moduli: dict[str, ModuleType] = {}
    detto = io.StringIO()
    for ruolo, nome in FILE_DEL_MOTORE.items():
        nome_del_modulo = f"_disegnatore_mep_report_{impronta}_{Path(nome).stem}"
        spec = importlib.util.spec_from_file_location(nome_del_modulo, cartella / nome)
        if spec is None or spec.loader is None:
            raise MotoreAssente(f"{cartella / nome} non si carica")
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[nome_del_modulo] = modulo
        try:
            with contextlib.redirect_stdout(detto), contextlib.redirect_stderr(detto):
                spec.loader.exec_module(modulo)
        except ImportError as errore:
            sys.modules.pop(nome_del_modulo, None)
            manca = f"manca la libreria {errore.name}" if errore.name else str(errore)
            raise MotoreAssente(f"il motore dei report in {cartella} non si carica: {manca}") from errore
        except Exception as errore:  # il motore e' codice d'altri: qualunque guasto e' «non c'e'»
            sys.modules.pop(nome_del_modulo, None)
            raise MotoreAssente(f"il motore dei report in {cartella} non si carica: {errore}") from errore
        moduli[ruolo] = modulo
    motore = Motore(cartella, moduli["copertina"], moduli["corpo"], moduli["controllo"], tuple(_avvisi_nel_testo(detto.getvalue())))
    _CARICATI[cartella] = motore
    return motore


# --- dal documento ai blocchi del motore ------------------------------------------------


def per_il_motore(testo: str) -> str:
    """Il testo come lo vuole un Paragraph del motore: i caratteri che Poppins non ha
    sostituiti, e «&», «<», «>» protetti (il Paragraph legge un markup)."""
    for prima, dopo in PER_IL_CARATTERE:
        testo = testo.replace(prima, dopo)
    return escape(testo)


def _parola_piu_larga(testo: str, carattere: str, misura: Callable[[str, str, float], float]) -> float:
    return max((misura(parola, carattere, 8.5) for parola in testo.split()), default=0.0)


def larghezze_delle_colonne(tabella: Tabella, totale: float, misura: Callable[[str, str, float], float],
                            normale: str, grassetto: str) -> list[float]:
    """Le larghezze in punti: in proporzione ai pesi, ma ogni colonna almeno quanto la
    sua parola piu' lunga (intestazione in grassetto, celle in tondo) piu' le imbottiture;
    quel che si aggiunge alle strette si toglie alle larghe, in proporzione."""
    somma = sum(tabella.pesi)
    larghe = [p * totale / somma for p in tabella.pesi]
    minime = []
    for indice, intestazione in enumerate(tabella.intestazioni):
        parole = [_parola_piu_larga(intestazione, grassetto, misura)]
        parole += [_parola_piu_larga(per_il_motore(riga[indice]).replace("&amp;", "&"), normale, misura) for riga in tabella.righe]
        minime.append(max(parole) + 2 * IMBOTTITURA_PT + 1.0)
    for _ in range(len(larghe)):
        corte = [i for i, (larga, minima) in enumerate(zip(larghe, minime, strict=True)) if larga < minima - 1e-6]
        if not corte:
            break
        manca = sum(minime[i] - larghe[i] for i in corte)
        for i in corte:
            larghe[i] = minime[i]
        cedono = [i for i in range(len(larghe)) if i not in corte and larghe[i] > minime[i]]
        margine = sum(larghe[i] - minime[i] for i in cedono)
        if margine <= 0:
            break
        for i in cedono:
            larghe[i] -= manca * (larghe[i] - minime[i]) / margine
    larghe[-1] += totale - sum(larghe)
    return larghe


TESTA_DEL_CAPITOLO_PT = 28 + 2 * 3 * 72 / 25.4
"""L'altezza del titolo di un capitolo (`sec()` del motore: 3 mm, la fascia di 28 pt, 3 mm)."""

SPAZIO_FRA_I_BLOCCHI_PT = 4 * 72 / 25.4
"""`sp(4)`, lo spazio fra due blocchi (rev9)."""

RIGHE_SOTTO_IL_TITOLO = 3
"""Un titoletto non resta in fondo alla pagina: ci va solo se sotto ci stanno
l'intestazione della tabella e almeno tre righe; se no passa alla pagina dopo, e la
tabella lunga continua nelle pagine seguenti con l'intestazione ripetuta."""


def _salto_se_manca(corpo: ModuleType, alto: float) -> Any:
    """Un salto di pagina condizionato (`CondPageBreak` di reportlab, che il motore usa):
    si prende dal modulo dei blocchi del motore, perche' qui reportlab non si importa —
    la distinta deve girare anche dove non c'e'."""
    blocchi = sys.modules[corpo.KeepTogether.__module__]
    return blocchi.CondPageBreak(alto)


Larghezze = dict[tuple[tuple[str, ...], tuple[float, ...]], list[float]]


def larghezze_del_documento(documento: Documento, corpo: ModuleType) -> Larghezze:
    """Le larghezze delle colonne di ogni tabella. Le tabelle con le stesse colonne — le
    sezioni del computo — hanno le stesse larghezze, misurate su tutte le loro righe: i
    bordi cadono sulle stesse verticali da una sezione all'altra (la griglia, rev9)."""
    gruppi: dict[tuple[tuple[str, ...], tuple[float, ...]], list[tuple[str, ...]]] = {}
    for capitolo in documento.capitoli:
        for blocco in capitolo.blocchi:
            if isinstance(blocco, Tabella):
                gruppi.setdefault((blocco.intestazioni, blocco.pesi), []).extend(blocco.righe)
    return {
        (intestazioni, pesi): larghezze_delle_colonne(
            Tabella(intestazioni, tuple(righe), pesi), corpo.CONTENT_W, corpo.pdfmetrics.stringWidth, corpo.BF, corpo.BFB
        )
        for (intestazioni, pesi), righe in gruppi.items()
    }


def _tabella(tabella: Tabella, corpo: ModuleType, larghezze: Larghezze) -> list[Any]:
    larghe = larghezze[(tabella.intestazioni, tabella.pesi)]
    stili = ["table_cell_r" if i in tabella.a_destra else "table_cell" for i in range(len(tabella.intestazioni))]
    righe = [[corpo.P(per_il_motore(cella), stili[i]) for i, cella in enumerate(riga)] for riga in tabella.righe]
    intestazioni = [per_il_motore(i) for i in tabella.intestazioni]
    disegnata = corpo.std_table(intestazioni, righe, larghe)
    testa = corpo.std_table(intestazioni, righe[:RIGHE_SOTTO_IL_TITOLO], larghe)
    blocchi: list[Any] = []
    if tabella.titolo:
        blocchi = [corpo.P(per_il_motore(tabella.titolo), "h3"), corpo.sp(2)]
    alto = sum(altezza(b, corpo.CONTENT_W) for b in [*blocchi, testa])
    return [_salto_se_manca(corpo, alto), *blocchi, disegnata]


def _blocco(blocco: Blocco, corpo: ModuleType, larghezze: Larghezze) -> list[Any]:
    if isinstance(blocco, Paragrafo):
        return [corpo.P(per_il_motore(blocco.testo), "note" if blocco.nota else "body")]
    if isinstance(blocco, Chiavi):
        return [corpo.kv_table([(per_il_motore(k), per_il_motore(v)) for k, v in blocco.righe])]
    if isinstance(blocco, Elenco):
        voci = list(corpo.num_items([per_il_motore(v) for v in blocco.voci]))
        if not blocco.titolo:
            return voci
        # Il titoletto e le prime voci non si separano; le altre voci vanno dove capita.
        testa = [corpo.P(per_il_motore(blocco.titolo), "h3"), corpo.sp(2), *voci[:4]]
        return [corpo.KeepTogether(testa), *voci[4:]]
    return _tabella(blocco, corpo, larghezze)


def altezza(flowable: Any, larghezza: float) -> float:
    """L'altezza di un blocco del motore; un KeepTogether come la somma dei suoi."""
    contenuto = getattr(flowable, "_content", None)
    if contenuto is not None:
        return sum(altezza(f, larghezza) for f in contenuto)
    return float(flowable.wrap(larghezza, 1e6)[1])


def _capitolo(capitolo: Capitolo, corpo: ModuleType, larghezze: Larghezze) -> list[Any]:
    """Un capitolo: il titolo legato al suo primo blocco (`chapter(..., keep='lead')`),
    il resto che scorre. Un distinta e' fatta di tabelle lunghe: tenere ogni capitolo
    intero lascerebbe mezze pagine bianche (misurato: nove pagine su quindici sotto
    l'80% sul caso AA-01); cosi' le pagine si riempiono e nessun titolo resta orfano."""
    parti = [_blocco(blocco, corpo, larghezze) for blocco in capitolo.blocchi]
    if not parti:
        return list(corpo.chapter(capitolo.numero, per_il_motore(capitolo.titolo), []))
    # Il titolo si lega al primo blocco: se il primo e' gia' un gruppo indivisibile, se ne
    # prende il contenuto (un KeepTogether dentro un altro misura «infinito», e manderebbe
    # il capitolo alla pagina dopo comunque).
    primo = parti[0]
    if len(primo) >= 1 and getattr(primo[0], "_content", None) is not None:
        primo = [*primo[0]._content, *primo[1:]]
        legati = len(primo) - len(parti[0]) + 1
    else:
        legati = 1
    blocchi = list(primo)
    for parte in parti[1:]:
        blocchi += [corpo.sp(4), *parte]
    # E il capitolo comincia solo dove, dopo il titolo e il primo blocco, c'e' posto anche
    # per l'inizio del secondo: niente titolo con due righe in fondo alla pagina.
    alto = TESTA_DEL_CAPITOLO_PT + sum(altezza(b, corpo.CONTENT_W) for b in blocchi[:legati])
    if len(parti) > 1:
        secondo = parti[1][0]
        alto += SPAZIO_FRA_I_BLOCCHI_PT + float(getattr(secondo, "height", 0) or altezza(secondo, corpo.CONTENT_W))
    capitolo_disegnato = corpo.chapter(capitolo.numero, per_il_motore(capitolo.titolo), blocchi, keep="lead", lead=legati)
    return [_salto_se_manca(corpo, alto), *capitolo_disegnato]


def storia(documento: Documento, corpo: ModuleType) -> list[Any]:
    """La «story» del motore: i capitoli, uno dopo l'altro, mai un salto pagina in testa."""
    pezzi: list[Any] = []
    larghezze = larghezze_del_documento(documento, corpo)
    for capitolo in documento.capitoli:
        pezzi += _capitolo(capitolo, corpo, larghezze)
    return pezzi


def _accorcia(riga: str) -> str:
    """Una parola in meno, e niente «in», «con», «-» in coda."""
    parole = riga.split()[:-1]
    while parole and (len(parole[-1]) <= 3 and parole[-1].islower() or parole[-1] in ("-", "—", "·")):
        parole.pop()
    return " ".join(parole)


def testi_della_copertina(motore: Motore, copertina: Copertina) -> tuple[list[str], str, list[str]]:
    """La copertina ha i triangoli, e il controllo della copertina (`check_cover_text`)
    dice se una riga li invade. Se la terza riga del titolo (il nome dell'impianto) non ci
    sta, si usa la riserva: la commessa nel titolo, l'impianto nel sottotitolo. Una riga
    che ancora non ci sta si accorcia di una parola alla volta, e si dice.
    Restituisce le righe del titolo, il sottotitolo e gli avvisi."""
    righe, sottotitolo, riquadro = list(copertina.titolo), copertina.sottotitolo, copertina.riquadro
    controlla = getattr(motore.copertina, "check_cover_text", None)
    avvisi: list[str] = []
    if controlla is None:
        return righe, sottotitolo, avvisi

    def segnalate(etichetta: str) -> bool:
        return any(str(p).startswith(etichetta) for p in controlla(*righe, sottotitolo, *riquadro, ()))

    if segnalate("TITLE_L3") and all(copertina.riserva):
        righe[2], sottotitolo = copertina.riserva
    for indice, etichetta in ((2, "TITLE_L3"), (1, "TITLE_L2"), (0, "TITLE_L1")):
        prima = righe[indice]
        while segnalate(etichetta) and " " in righe[indice]:
            righe[indice] = _accorcia(righe[indice])
        if righe[indice] != prima:
            avvisi.append(f"[copertina] la riga «{prima}» non ci sta: «{righe[indice]}» (per intero nel capitolo 1)")
    prima = sottotitolo
    while segnalate("SUBTITLE") and " " in sottotitolo:
        sottotitolo = _accorcia(sottotitolo.removesuffix(" …")) + " …"
    if sottotitolo != prima:
        avvisi.append(f"[copertina] il sottotitolo «{prima}» non ci sta: «{sottotitolo}» (per intero nel capitolo 1)")
    return righe, sottotitolo, avvisi


def scrivi_il_pdf(documento: Documento, motore: Motore, cartella: Path) -> EsitoDelPdf:
    """Il PDF del documento nella cartella, col nome del documento; le pagine in PNG in
    `<cartella>/<nome>-pagine/`. Quello che il motore stampa non si ripete: si
    raccolgono i suoi avvisi."""
    cartella.mkdir(parents=True, exist_ok=True)
    pdf = cartella / f"{documento.nome}.pdf"
    esito = EsitoDelPdf(pdf=pdf)
    corpo, copertina = motore.corpo, motore.copertina
    riquadro = documento.copertina.riquadro
    righe, sottotitolo, accorciate = testi_della_copertina(motore, documento.copertina)
    detto = io.StringIO()
    with tempfile.TemporaryDirectory(prefix="distinta-report-") as lavoro:
        file_della_copertina = str(Path(lavoro) / "copertina.pdf")
        file_del_corpo = str(Path(lavoro) / "corpo.pdf")
        with contextlib.redirect_stdout(detto), contextlib.redirect_stderr(detto):
            copertina.build_cover_pdf(
                file_della_copertina,
                TITLE_L1=righe[0],
                TITLE_L2=righe[1],
                TITLE_L3=righe[2],
                SUBTITLE=sottotitolo,
                BOX_HEAD=riquadro[0],
                BOX_TXT1=riquadro[1],
                BOX_TXT2=riquadro[2],
                KPI_DATA=(),
                FTR_RIGHT=documento.copertina.piede,
            )
            corpo._DOC_HEADER_RIGHT[:] = list(documento.intestazione)
            pezzi = storia(documento, corpo)
            corpo.story_plan(pezzi, include_chi_siamo=False)
            corpo.validate_story(pezzi, label=documento.nome)
            doc = corpo.make_doc(file_del_corpo, include_chi_siamo=False)
            doc.build(pezzi)
            fatti_dal_corpo = corpo.fill_report(doc)
            corpo.merge_pdf(str(pdf), file_della_copertina, file_del_corpo, include_chi_siamo=False, title=documento.titolo)
            controllo = motore.controllo.qa_pdf(
                str(pdf), offer=False, forbid=list(documento.vietate), out_dir=str(cartella / f"{documento.nome}-pagine")
            )
    detti = [r for r in _avvisi_nel_testo(detto.getvalue()) if re.search(r"\[(cover|font)\]", r)]
    fatti = [str(a) for a in fatti_dal_corpo]
    esito.avvisi = list(dict.fromkeys([*motore.avvisi, *accorciate, *detti, *fatti, *(str(p) for p in controllo.get("issues", []))]))
    esito.pagine = [Path(p) for p in controllo.get("pngs", [])]
    return esito


def scrivi_il_documento(documento: Documento, cartella: Path, report: Path | None) -> tuple[Path, EsitoDelPdf | None, str]:
    """Il documento della distinta: in PDF se `report` porta al motore dei report Nove C,
    altrimenti in Markdown. Restituisce il file scritto, l'esito del PDF (o niente) e,
    se il PDF non si e' fatto, il perche'."""
    perche = ""
    if report is None:
        perche = "non e' stata data la skill dei report Nove C (--report <cartella della skill nove-c-report>)"
    else:
        try:
            motore = carica_il_motore(report)
        except MotoreAssente as errore:
            perche = str(errore)
        else:
            esito = scrivi_il_pdf(documento, motore, cartella)
            return esito.pdf, esito, ""
    cartella.mkdir(parents=True, exist_ok=True)
    markdown = cartella / f"{documento.nome}.md"
    markdown.write_text(documento_in_markdown(documento), encoding="utf-8")
    return markdown, None, perche
