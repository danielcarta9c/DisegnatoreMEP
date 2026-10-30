"""La copertina dei report Nove C **finta**, per le prove della distinta (REL-015): le
firme di `nove_c_report_cover` (rev9), le chiamate registrate in `CHIAMATE`. Una riga del
titolo «invade i triangoli» oltre 20 caratteri (24 la terza), il sottotitolo oltre 65."""

from pathlib import Path
from typing import Any

CHIAMATE: list[dict[str, Any]] = []


def check_cover_text(TITLE_L1: str, TITLE_L2: str, TITLE_L3: str, SUBTITLE: str, BOX_HEAD: str,  # noqa: N803
                     BOX_TXT1: str, BOX_TXT2: str, KPI_DATA: Any, tol: float = 4) -> list[str]:
    problemi = [
        f"{etichetta} '{testo}' invade il triangolo"
        for etichetta, testo, limite in (("TITLE_L1", TITLE_L1, 20), ("TITLE_L2", TITLE_L2, 20), ("TITLE_L3", TITLE_L3, 24))
        if len(testo) > limite
    ]
    if len(SUBTITLE) > 65:
        problemi.append("SUBTITLE invade il triangolo")
    return problemi


def build_cover_pdf(path: str, **testi: Any) -> str:
    CHIAMATE.append(dict(testi))
    for problema in check_cover_text(
        testi["TITLE_L1"], testi["TITLE_L2"], testi["TITLE_L3"], testi["SUBTITLE"], testi["BOX_HEAD"],
        testi["BOX_TXT1"], testi["BOX_TXT2"], testi["KPI_DATA"],
    ):
        print(f"  [cover] ⚠️  {problema}")
    Path(path).write_bytes(b"%PDF-copertina finta\n")
    return path
