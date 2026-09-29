"""Stampa l'ambiente in cui gira una skill: Python, sistema, librerie, rete, cartelle.

Solo libreria standard, nessuna scrittura fuori da una cartella temporanea: si puo'
lanciare ovunque senza installare niente.
"""

import importlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

LIBRERIE = [
    "pydantic", "pydantic_core", "annotated_types", "typing_extensions", "typing_inspection",
    "ezdxf", "numpy", "fontTools", "pyparsing",
    "reportlab", "pypdf", "fitz", "pdfplumber", "pypdfium2", "PIL", "svglib", "cairosvg",
    "cairo", "lxml", "yaml",
]
PROGRAMMI = ["pip", "pip3", "chromium", "chromium-browser", "google-chrome", "wkhtmltopdf",
             "inkscape", "rsvg-convert", "fc-list", "mutool", "qpdf"]
INDIRIZZI = ["https://pypi.org/simple/pydantic/", "https://files.pythonhosted.org/",
             "https://github.com/"]
CARTELLE = ["/mnt/user-data/outputs", "/mnt/user-data/uploads", "/mnt/skills", "/tmp",
            str(Path.cwd()), str(Path.home())]


def riga(chiave: str, valore: object) -> None:
    print(f"{chiave:28} {valore}")


def main() -> None:
    print("== Python e sistema")
    riga("python", sys.version.replace("\n", " "))
    riga("eseguibile", sys.executable)
    riga("piattaforma", platform.platform())
    riga("macchina", platform.machine())
    riga("libc", " ".join(platform.libc_ver()))
    riga("cpu", os.cpu_count())
    riga("questa skill sta in", Path(__file__).resolve().parent.parent)
    riga("cartella corrente", Path.cwd())
    try:
        import sysconfig
        riga("tag delle ruote", sysconfig.get_platform() + " / " + sys.implementation.cache_tag)
    except Exception as errore:  # noqa: BLE001
        riga("tag delle ruote", f"? {errore}")

    print("\n== Librerie")
    for nome in LIBRERIE:
        try:
            modulo = importlib.import_module(nome)
            versione = getattr(modulo, "__version__", None) or getattr(modulo, "VERSION", "?")
            riga(nome, f"SI {versione}")
        except Exception as errore:  # noqa: BLE001
            riga(nome, f"no ({type(errore).__name__})")

    print("\n== Programmi")
    for nome in PROGRAMMI:
        riga(nome, shutil.which(nome) or "no")
    try:
        uscita = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True,
                                text=True, timeout=30)
        riga("python -m pip", (uscita.stdout or uscita.stderr).strip()[:100])
    except Exception as errore:  # noqa: BLE001
        riga("python -m pip", f"no ({errore})")

    print("\n== Rete (5 secondi per indirizzo)")
    for indirizzo in INDIRIZZI:
        try:
            with urllib.request.urlopen(indirizzo, timeout=5) as risposta:
                riga(indirizzo, f"SI {risposta.status}")
        except urllib.error.HTTPError as errore:
            riga(indirizzo, f"SI (raggiunto, risposta {errore.code})")
        except Exception as errore:  # noqa: BLE001
            riga(indirizzo, f"no ({type(errore).__name__}: {str(errore)[:60]})")

    with tempfile.TemporaryDirectory() as cartella:
        try:
            uscita = subprocess.run(
                [sys.executable, "-m", "pip", "download", "--no-deps", "--quiet", "-d", cartella,
                 "pydantic==2.13.4"], capture_output=True, text=True, timeout=90)
            riga("pip download da PyPI", "SI" if uscita.returncode == 0 else
                 f"no ({(uscita.stderr or uscita.stdout).strip().splitlines()[-1][:80]})")
        except Exception as errore:  # noqa: BLE001
            riga("pip download da PyPI", f"no ({type(errore).__name__})")

    print("\n== Cartelle")
    for cartella in CARTELLE:
        percorso = Path(cartella)
        if not percorso.exists():
            riga(cartella, "non esiste")
            continue
        try:
            with tempfile.NamedTemporaryFile(dir=percorso):
                scrivibile = "scrivibile"
        except Exception:  # noqa: BLE001
            scrivibile = "sola lettura"
        riga(cartella, scrivibile)

    print("\n== Caratteri")
    if shutil.which("fc-list"):
        uscita = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, timeout=30)
        famiglie = sorted({r.split(",")[0] for r in uscita.stdout.splitlines() if r})
        riga("famiglie", ", ".join(f for f in famiglie if any(
            p in f.lower() for p in ("arial", "helvet", "liberation", "dejavu", "nimbus")))[:300] or "nessuna")
    else:
        riga("fc-list", "no")


if __name__ == "__main__":
    main()
