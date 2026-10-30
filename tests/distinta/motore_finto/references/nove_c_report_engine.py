"""Un motore del corpo dei report Nove C **finto**, per le prove della distinta (REL-015).

Ha le funzioni di `nove_c_report_engine` (rev9) che la distinta usa, con le stesse firme,
ma non disegna niente e non vuole reportlab: registra le chiamate in `CHIAMATE`, e i
blocchi che restituisce hanno solo un'altezza. Il motore vero e' della skill
`nove-c-report` del PO e non entra nel repository.
"""

from pathlib import Path
from typing import Any

CHIAMATE: list[tuple[str, dict[str, Any]]] = []
AVVISI_DEL_RIEMPIMENTO: list[str] = []
"""Quello che `fill_report` restituisce: una prova lo riempie per vedere che il comando lo dice."""

CONTENT_W = 510.24
FRAME_H = 697.0
BF = "Finto"
BFB = "Finto-Grassetto"
_DOC_HEADER_RIGHT = ["noveC — [INSERIRE titolo documento]", "[INSERIRE mese anno]"]


class _Misure:
    @staticmethod
    def stringWidth(testo: str, carattere: str, corpo: float) -> float:  # noqa: N802 - come reportlab
        return len(testo) * corpo * (0.6 if carattere == BFB else 0.55)


pdfmetrics = _Misure()


class Blocco:
    def __init__(self, tipo: str, alto: float, **dati: Any) -> None:
        self.tipo, self.alto, self.dati = tipo, alto, dati
        self.height = 0.0

    def wrap(self, larghezza: float, altezza: float) -> tuple[float, float]:
        return larghezza, self.alto


class KeepTogether:
    def __init__(self, flowables: list[Any], maxHeight: Any = None) -> None:  # noqa: N803 - come reportlab
        self._content = list(flowables)
        self.height = 0.0


class CondPageBreak(Blocco):
    def __init__(self, height: float) -> None:
        super().__init__("salto", 0.0)
        self.height = height


def _registra(nome: str, **dati: Any) -> None:
    CHIAMATE.append((nome, dati))


def P(text: str, style: str = "body") -> Blocco:  # noqa: N802 - il nome del motore
    return Blocco("P", 14.0, testo=text, stile=style)


def sp(h: float = 4) -> Blocco:
    return Blocco("sp", h * 72 / 25.4)


def chapter(num: int, title: str, flowables: list[Any], keep: str = "all", lead: int = 2) -> list[Any]:
    _registra("chapter", num=num, title=title, keep=keep, lead=lead, blocchi=len(flowables))
    testa = [sp(3), Blocco("titolo", 28.0, numero=num, titolo=title), sp(3)]
    if keep == "all":
        return [KeepTogether(testa + list(flowables))]
    return [KeepTogether(testa + list(flowables)[:lead]), *list(flowables)[lead:]]


def std_table(headers: list[str], rows: list[list[Any]], col_widths: list[float], extra_styles: Any = None) -> Blocco:
    _registra("std_table", intestazioni=list(headers), righe=[[c.dati["testo"] for c in r] for r in rows], larghezze=list(col_widths))
    return Blocco("tabella", 20.0 * (len(rows) + 1), larghezze=list(col_widths))


def kv_table(rows: list[tuple[str, str]], ratio: tuple[float, float] = (0.24, 0.76)) -> Blocco:
    _registra("kv_table", righe=list(rows))
    return Blocco("chiavi", 20.0 * len(rows))


def num_items(items: list[str], color: Any = None, gap_mm: float = 0.3, font_size: float = 8.5) -> list[Any]:
    _registra("num_items", voci=list(items))
    blocchi: list[Any] = []
    for voce in items:
        blocchi += [Blocco("voce", 18.0, testo=voce), sp(gap_mm)]
    return blocchi


def story_plan(story: list[Any], label: str = "corpo", include_chi_siamo: bool = False) -> list[Any]:
    _registra("story_plan", include_chi_siamo=include_chi_siamo, pezzi=len(story))
    return []


def validate_story(story: list[Any], label: str = "document", strict: bool = True) -> bool:
    _registra("validate_story", label=label)
    return True


class _Documento:
    def __init__(self, percorso: str) -> None:
        self.percorso = percorso

    def build(self, story: list[Any]) -> None:
        _registra("build", pezzi=len(story), primo=type(story[0]).__name__ if story else "")
        Path(self.percorso).write_bytes(b"%PDF-corpo finto\n")


def make_doc(output_path: str, include_chi_siamo: bool = False) -> _Documento:
    _registra("make_doc", include_chi_siamo=include_chi_siamo)
    return _Documento(output_path)


def fill_report(doc: Any, min_fill: float = 0.80, min_last: float = 0.30, label: str = "corpo") -> list[str]:
    _registra("fill_report")
    print("  Riempimento pagine (corpo) — finto")
    return list(AVVISI_DEL_RIEMPIMENTO)


def merge_pdf(out_path: str, cover_path: str, body_path: str, include_chi_siamo: bool = False, title: str | None = None) -> str:
    _registra("merge_pdf", include_chi_siamo=include_chi_siamo, title=title, copertina=Path(cover_path).read_bytes())
    Path(out_path).write_bytes(b"%PDF-1.4 finto\n")
    return out_path
