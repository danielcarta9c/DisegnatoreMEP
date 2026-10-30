"""Il controllo finale dei report Nove C **finto**, per le prove della distinta (REL-015):
la firma di `nove_c_report_qa.qa_pdf` (rev9); scrive tre PNG vuote e restituisce i
problemi di `PROBLEMI`."""

from pathlib import Path
from typing import Any

CHIAMATE: list[dict[str, Any]] = []
PROBLEMI: list[str] = []


def qa_pdf(pdf: str, offer: bool = False, forbid: Any = (), out_dir: str | None = None, dpi: int = 80) -> dict[str, Any]:
    CHIAMATE.append({"pdf": pdf, "offer": offer, "forbid": list(forbid), "out_dir": out_dir})
    cartella = Path(out_dir or ".")
    cartella.mkdir(parents=True, exist_ok=True)
    pagine = []
    for numero in (1, 2, 3):
        pagina = cartella / f"qa-{numero}.png"
        pagina.write_bytes(b"\x89PNG finta")
        pagine.append(str(pagina))
    print("  CHECKLIST VISIVA (finta)")
    return {"pages": 3, "issues": list(PROBLEMI), "notes": [], "pngs": pagine}
