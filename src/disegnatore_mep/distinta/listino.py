"""Il listino della minuteria (REL-019, D-235), letto dal suo Markdown (REL-021).

Il listino e' un documento per chi lo legge e lo aggiorna — `skill/distinta/LISTINO-MINUTERIA.md`,
nella skill `riferimenti/listino-minuteria.md` —, non un file di dati: le sue tabelle si
leggono qui, cosi' il prezzo che la distinta usa e' quello che il PO vede e corregge.

Due tabelle portano i prezzi:

- il rilievo al banco (§1): una riga per voce, con la colonna `ID` (il codice) e
  `Netto/UM €`;
- il riepilogo del riferimento online (§2): una riga per voce e misura, con la colonna
  `Codice` e la `Mediana €` dei riscontri.

Il resto (il dettaglio dei riscontri, le note) si legge come testo. Un codice che compare
due volte ferma la lettura: il prezzo di una voce dev'essere uno.
"""

import re
from dataclasses import dataclass
from pathlib import Path


class ErroreDelListino(ValueError):
    """Il listino non si legge: il file, una tabella, un codice doppio."""


@dataclass(frozen=True)
class VoceDelListino:
    codice: str
    descrizione: str
    prezzo: float
    """Euro netti (IVA esclusa) per unita' di misura."""
    um: str
    fonte: str
    """Da dove viene: «rilievo Tecnomat 2 novembre 2026», «riferimento online, mediana di 5»."""


@dataclass(frozen=True)
class Listino:
    voci: dict[str, VoceDelListino]
    titolo: str
    revisione: str
    percorso: Path

    def get(self, codice: str) -> VoceDelListino | None:
        return self.voci.get(codice)


def _numero(testo: str) -> float | None:
    pulito = testo.strip().replace(".", "").replace(",", ".") if "," in testo else testo.strip()
    try:
        return float(pulito)
    except ValueError:
        return None


def _celle(riga: str) -> list[str]:
    return [c.strip() for c in riga.strip().strip("|").split("|")]


def leggi_il_listino(percorso: Path) -> Listino:
    """Le voci con un prezzo del listino in `percorso`."""
    try:
        testo = percorso.read_text(encoding="utf-8")
    except OSError as errore:
        raise ErroreDelListino(f"{percorso}: il listino non si apre ({errore})") from errore
    righe = testo.splitlines()
    titolo = next((r[2:].strip() for r in righe if r.startswith("# ")), percorso.stem)
    trovata = re.search(r"\*\*Revisione ([^*]+)\*\*", testo)
    revisione = trovata.group(1).strip().rstrip(".") if trovata else ""
    capitolo = ""
    voci: dict[str, VoceDelListino] = {}
    intestazione: list[str] | None = None
    for riga in righe:
        if riga.startswith("## "):
            capitolo = riga[3:].strip()
        if not riga.startswith("|"):
            intestazione = None
            continue
        celle = _celle(riga)
        if intestazione is None:
            intestazione = celle
            continue
        if set(riga.replace("|", "").strip()) <= set("-: "):
            continue
        dati = dict(zip(intestazione, celle, strict=False))
        data = re.search(r"(\d+ \w+ \d{4})", capitolo)
        quando = f", {data.group(1)}" if data else ""
        if "Netto/UM €" in dati and "ID" in dati and "Articolo" in dati:
            codice, prezzo, um = dati["ID"], _numero(dati["Netto/UM €"]), dati.get("UM", "")
            descrizione = dati["Articolo"]
            fonte = f"rilievo al banco, {dati.get('Negozio', '')}{quando}"
        elif "Mediana €" in dati and "Codice" in dati:
            codice, prezzo, um = dati["Codice"], _numero(dati["Mediana €"]), dati.get("UM", "")
            descrizione = f"{dati.get('Voce', '')}, {dati.get('Misura', '')}".strip(", ")
            fonte = f"riferimento online{quando}, mediana di {dati.get('Riscontri', '?')} riscontri"
        else:
            continue
        if not codice or prezzo is None:
            continue
        if codice in voci:
            raise ErroreDelListino(f"{percorso}: il codice {codice} ha due prezzi")
        voci[codice] = VoceDelListino(codice, descrizione, prezzo, um, fonte)
    if not voci:
        raise ErroreDelListino(f"{percorso}: nessuna tabella di prezzi (colonne «ID … Netto/UM €» o «Codice … Mediana €»)")
    return Listino(voci, titolo, revisione, percorso)
