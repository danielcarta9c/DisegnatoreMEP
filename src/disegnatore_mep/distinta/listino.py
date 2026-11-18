"""Il listino della minuteria (REL-019, D-235), letto dal suo Markdown (REL-021), a piu' fornitori (REL-027).

Il listino e' un documento per chi lo legge e lo aggiorna — `skill/distinta/LISTINO-MINUTERIA.md`,
nella skill `riferimenti/listino-minuteria.md` —, non un file di dati: le sue tabelle si
leggono qui, cosi' il prezzo che la distinta usa e' quello che il PO vede e corregge.

Due tabelle portano i prezzi:

- gli articoli (il rilievo al banco del §1, le fatture del §2ter, le offerte dei fornitori dei §4 e
  seguenti): una riga per articolo, con la colonna `ID` (il codice), `Netto/UM €` e, dalla
  revisione 06, `Fornitore`;
- il riepilogo del riferimento online (§2, §2bis): una riga per voce e misura, con la colonna
  `Codice` e la `Mediana €` dei riscontri.

**Un codice ha un prezzo per fornitore** (REL-027, I-302): lo stesso articolo da Tecnomat, da
Abbattista e da Idrosanitaria sono tre righe con lo stesso ID. Lo stesso codice due volte **dallo
stesso fornitore** ferma la lettura: il prezzo di un fornitore per una voce dev'essere uno. Una
riga con l'ID «—» e' documentata ma nessuna regola la usa, e non si legge.

**La marca non conta, conta la prescrizione** (I-307): una nota che comincia con «⚠» e' uno
scostamento dalla voce (il fondo scala, l'attacco, un organo che manca). Il prezzo che il conto usa
e' il piu' basso fra le righe che rispettano la voce; quella con ⚠ entra solo se nessun'altra c'e'.

La tabella «I fornitori» (colonne `Fornitore` e `Si ordina`) dice da chi Nove C ordina. Gli altri
prezzi — il riferimento online, le fatture di un installatore — sono riferimenti: entrano nel conto
solo dove nessun fornitore da cui si ordina ha l'articolo. Un listino senza quella tabella (prima
della revisione 06) ordina da tutti, tranne che dal riferimento online.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path


class ErroreDelListino(ValueError):
    """Il listino non si legge: il file, una tabella, un codice doppio dello stesso fornitore."""


RIFERIMENTO_ONLINE = "riferimento online"
"""Il «fornitore» delle righe del riepilogo online: un riferimento, da cui non si ordina."""

SENZA_ID = {"—", "-", ""}


@dataclass(frozen=True)
class VoceDelListino:
    codice: str
    descrizione: str
    prezzo: float
    """Euro netti (IVA esclusa) per unita' di misura."""
    um: str
    fonte: str
    """Da dove viene: «rilievo al banco, Tecnomat Segrate (MI), 2 novembre 2026», «riferimento online, mediana di 5»."""
    fornitore: str = ""
    """Chi vende l'articolo a quel prezzo (la colonna `Fornitore`, o il negozio nei listini di prima)."""
    articolo: str = ""
    """Il codice dell'articolo del fornitore (la colonna `Codice`), per l'ordine."""
    confezione: str = ""
    scostamento: str = ""
    """Dove l'articolo non rispetta la prescrizione della voce (la nota con ⚠), o vuoto."""


@dataclass(frozen=True)
class Fornitore:
    nome: str
    si_ordina: bool
    pagamento: str = ""
    fonte: str = ""


@dataclass(frozen=True)
class Listino:
    righe: dict[str, tuple[VoceDelListino, ...]]
    """Per codice, i prezzi di tutti i fornitori e dei riferimenti."""
    titolo: str
    revisione: str
    percorso: Path
    fornitori: dict[str, Fornitore] = field(default_factory=dict)
    """La tabella «I fornitori»; vuota nei listini di prima della revisione 06."""

    def si_ordina(self, fornitore: str) -> bool:
        if fornitore == RIFERIMENTO_ONLINE:
            return False
        if not self.fornitori:
            return True
        trovato = self.fornitori.get(fornitore)
        return bool(trovato and trovato.si_ordina)

    def offerte(self, codice: str) -> tuple[VoceDelListino, ...]:
        """Tutti i prezzi del codice, il piu' basso per primo."""
        return tuple(sorted(self.righe.get(codice, ()), key=lambda v: v.prezzo))

    def ordinabili(self, codice: str) -> tuple[VoceDelListino, ...]:
        """I prezzi del codice dei fornitori da cui si ordina, il piu' basso per primo."""
        return tuple(v for v in self.offerte(codice) if self.si_ordina(v.fornitore))

    def validi(self, codice: str) -> tuple[VoceDelListino, ...]:
        """I prezzi dei fornitori da cui si ordina che rispettano la voce; se nessuno la rispetta,
        tutti quelli da cui si ordina (con lo scostamento, che il conto dice)."""
        ordinabili = self.ordinabili(codice)
        conformi = tuple(v for v in ordinabili if not v.scostamento)
        return conformi or ordinabili

    def get(self, codice: str) -> VoceDelListino | None:
        """Il prezzo che il conto usa: il piu' basso fra i fornitori da cui si ordina, fra gli
        articoli che rispettano la voce (`validi`); se nessuno di loro ha il codice, il riferimento
        piu' basso."""
        validi = self.validi(codice)
        if validi:
            return validi[0]
        offerte = self.offerte(codice)
        return offerte[0] if offerte else None

    def con_i_fornitori(self, nomi: Sequence[str]) -> "Listino":
        """Lo stesso listino, da cui si ordina soltanto dai fornitori `nomi` (`distinta --costo
        --fornitori`, I-306): il progettista ha scelto per il cantiere un fornitore, o due. Gli altri
        prezzi restano, come riferimenti. Un nome che il listino non ha ferma."""
        noti = {v.fornitore for vv in self.righe.values() for v in vv} - {RIFERIMENTO_ONLINE}
        noti |= set(self.fornitori)
        ignoti = [n for n in nomi if n not in noti]
        if ignoti or not nomi:
            raise ErroreDelListino(
                f"{self.percorso}: fornitori che il listino non ha: {', '.join(ignoti) or '(nessuno)'}; "
                f"quelli che ha: {', '.join(sorted(noti))}"
            )
        scelti = {
            nome: replace(self.fornitori.get(nome, Fornitore(nome, True)), si_ordina=nome in nomi) for nome in sorted(noti)
        }
        return replace(self, fornitori=scelti)

    @property
    def voci(self) -> dict[str, VoceDelListino]:
        """Per codice, il prezzo che il conto usa (`get`)."""
        return {codice: voce for codice in self.righe if (voce := self.get(codice)) is not None}


def _numero(testo: str) -> float | None:
    pulito = testo.strip().replace(".", "").replace(",", ".") if "," in testo else testo.strip()
    try:
        return float(pulito)
    except ValueError:
        return None


def _celle(riga: str) -> list[str]:
    return [c.strip() for c in riga.strip().strip("|").split("|")]


def _si(testo: str) -> bool:
    return testo.strip().lower().startswith(("sì", "si", "yes"))


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
    voci: dict[str, list[VoceDelListino]] = {}
    fornitori: dict[str, Fornitore] = {}
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
        if "Si ordina" in dati and "Fornitore" in dati:
            nome = dati["Fornitore"]
            fornitori[nome] = Fornitore(nome, _si(dati["Si ordina"]), dati.get("Come si paga", ""),
                                        dati.get("Da dove vengono i prezzi", ""))
            continue
        data = re.search(r"(\d+ \w+ \d{4})", capitolo)
        quando = f", {data.group(1)}" if data else ""
        if "Netto/UM €" in dati and "ID" in dati and "Articolo" in dati:
            codice, prezzo, um = dati["ID"], _numero(dati["Netto/UM €"]), dati.get("UM", "")
            descrizione = dati["Articolo"]
            negozio = dati.get("Negozio", "")
            fornitore = dati.get("Fornitore") or negozio
            dove = " ".join(dict.fromkeys(p for p in (dati.get("Fornitore", ""), negozio) if p))
            if dati.get("Rif."):
                fonte = f"{fornitore}, {dati['Rif.']}"
            else:
                fonte = f"rilievo al banco, {dove}{quando}"
            articolo, confezione = dati.get("Codice", ""), dati.get("Confezione", "")
            nota = dati.get("Note", "").strip()
            scostamento = nota[1:].split(";")[0].strip() if nota.startswith("⚠") else ""
        elif "Mediana €" in dati and "Codice" in dati:
            codice, prezzo, um = dati["Codice"], _numero(dati["Mediana €"]), dati.get("UM", "")
            descrizione = f"{dati.get('Voce', '')}, {dati.get('Misura', '')}".strip(", ")
            fonte = f"riferimento online{quando}, mediana di {dati.get('Riscontri', '?')} riscontri"
            fornitore, articolo, confezione, scostamento = RIFERIMENTO_ONLINE, "", "", ""
        else:
            continue
        if codice in SENZA_ID or prezzo is None:
            continue
        gia = voci.setdefault(codice, [])
        if any(v.fornitore == fornitore for v in gia):
            da = f" da {fornitore}" if fornitore else ""
            raise ErroreDelListino(f"{percorso}: il codice {codice} ha due prezzi{da}")
        gia.append(VoceDelListino(codice, descrizione, prezzo, um, fonte, fornitore, articolo, confezione, scostamento))
    if not voci:
        raise ErroreDelListino(f"{percorso}: nessuna tabella di prezzi (colonne «ID … Netto/UM €» o «Codice … Mediana €»)")
    if fornitori:
        ignoti = sorted({v.fornitore for vv in voci.values() for v in vv} - set(fornitori) - {RIFERIMENTO_ONLINE})
        if ignoti:
            raise ErroreDelListino(f"{percorso}: fornitori che la tabella «I fornitori» non ha: {', '.join(ignoti)}")
    return Listino({c: tuple(v) for c, v in voci.items()}, titolo, revisione, percorso, fornitori)
