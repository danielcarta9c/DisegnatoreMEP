"""Le lunghezze dalla pianta al grafo, in un passaggio solo (REL-026, B-4; LEGGIMI A1 di BD.RM.260).

Fino alla 2.0.0 `pianta --grafo` confrontava soltanto: le lunghezze misurate in pianta si
ricopiavano a mano nel grafo, da cui le leggono lo schema e la distinta, e se la pianta
cambiava restavano i numeri vecchi. Ora, con `--grafo`, dopo aver disegnato la pianta
**scrive nel file del grafo** le lunghezze che ha misurato, e dice che cosa e' cambiato.

**Da dove viene una lunghezza.** Il grafo lo dice con un dato solo, sulla tubazione:
`properties.lunghezza_dalla_pianta_m`, il numero che la pianta ci ha scritto. La
`lunghezza_m` di una tubazione **e' della pianta** se quel dato c'e' ed e' uguale a lei;
in ogni altro caso — nessun dato (un grafo di prima, o una lunghezza scritta dal
progettista) o un dato diverso (la lunghezza corretta a mano dopo) — **e' del
progettista**, e non si sovrascrive. Cosi' un grafo senza il dato si legge com'era, e
una correzione a mano resta anche se si dimentica di togliere il dato.

**Che cosa si scrive.** Solo le lunghezze — e gli `attraversamenti`, se la pianta ha le
forature accese (B-3) —, mai la connettivita' ne' altri campi (`docs/ARCHITETTURA-DEL-
PIANO.md` §2). L'unita' e' la **tratta**: se il progettista ha dato la lunghezza di una
tratta — nella pianta o su una qualunque delle sue tubazioni del grafo —, la tratta e'
sua, e la pianta non scrive niente sulle sue tubazioni (la segnala, se misura altro); se
no, la misura della tratta intera va sulla **prima** delle sue tubazioni, e le altre
restano senza lunghezza: una tratta, una lunghezza, come la scrive il progettista e come
`completa` la tiene quando spezza una tubazione (la prima meta' la tiene). Con una misura
per tronco lo schema scriveva due lunghezze sulla stessa tratta — «3G4 · L 10,19 m» e
«3G4 · L 0,44 m» fra quadro, sezionatore e unita' esterna: visto sulla tavola del
collaudo. Una tratta non instradata, o che il grafo non ha, non si scrive.

**Il file** si riscrive solo se qualcosa cambia, e nello stile in cui era: rientro,
separatori, caratteri accentati, ordine delle chiavi; un campo nuovo va al suo posto
alfabetico se le chiavi dell'oggetto sono in ordine alfabetico, se no in fondo.
Rilanciata senza cambi, la pianta non scrive niente e lo dice.

Il numero scritto e' la misura della pianta come la quota la tavola (`Lunghezza.misurata_m`,
al millimetro): la distinta, rifatta sul grafo, quota lo stesso numero della pianta.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LUNGHEZZA_DALLA_PIANTA = "lunghezza_dalla_pianta_m"
"""Il dato della tubazione che dice che la sua `lunghezza_m` l'ha scritta la pianta."""

ATTRAVERSAMENTI = "attraversamenti"
ATTRAVERSAMENTI_DALLA_PIANTA = "attraversamenti_dalla_pianta"
"""Lo stesso, per gli `attraversamenti` (le pareti forate), a forature accese."""

TOLLERANZA_M = 0.0005
"""Due lunghezze piu' vicine di mezzo millimetro sono la stessa.

Il modulo non importa il resto della pianta: la distinta ne legge la regola della
provenienza (`dalla_pianta`) senza tirarsi dietro l'instradatore."""


def _metri(valore: float) -> str:
    """2.365 → «2,365 m», 3.0 → «3 m»."""
    testo = f"{valore:.3f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",") + " m"


def numero(valore: object) -> float | None:
    if isinstance(valore, bool):
        return None
    if isinstance(valore, int | float):
        return float(valore) if math.isfinite(valore) else None
    if isinstance(valore, str):
        try:
            return float(valore.strip().replace(",", "."))
        except ValueError:
            return None
    return None


def dalla_pianta(valore: object, segno: object) -> bool:
    """Il valore l'ha scritto la pianta: c'e' il suo segno, ed e' lo stesso numero."""
    v, s = numero(valore), numero(segno)
    return v is not None and s is not None and abs(v - s) <= TOLLERANZA_M


def lunghezza_della_tubazione(tubazione: Mapping[str, Any]) -> object:
    """La `lunghezza_m` della tubazione: in testa, o fra le `properties` (i grafi di prima
    di REL-012)."""
    if tubazione.get("lunghezza_m") is not None:
        return tubazione["lunghezza_m"]
    return (tubazione.get("properties") or {}).get("lunghezza_m")


def provenienza(tubazione: Mapping[str, Any]) -> str | None:
    """Di chi e' la lunghezza della tubazione: «pianta», «progettista», o `None` se non c'e'."""
    lunghezza = lunghezza_della_tubazione(tubazione)
    if lunghezza is None or lunghezza == "":
        return None
    segno = (tubazione.get("properties") or {}).get(LUNGHEZZA_DALLA_PIANTA)
    return "pianta" if dalla_pianta(lunghezza, segno) else "progettista"


def provenienza_della_tratta(tubazioni: Sequence[Mapping[str, Any]]) -> str | None:
    """Di chi e' la lunghezza di una tratta: del progettista se lo e' quella di una
    qualunque delle sue tubazioni; se no della pianta, se ce n'e' una; se no di nessuno."""
    di = {provenienza(t) for t in tubazioni}
    if "progettista" in di:
        return "progettista"
    return "pianta" if "pianta" in di else None


# --- l'aggiornamento ----------------------------------------------------------------------


@dataclass(frozen=True)
class Cambio:
    """Una tratta il cui dato nel grafo cambia: le tubazioni, il prima e il dopo."""

    tratta: str
    tubazioni: tuple[str, ...]
    prima: float | None
    dopo: float


@dataclass(frozen=True)
class Lasciata:
    """Una tratta con la lunghezza del progettista: resta, e si dice se la pianta misura altro."""

    tratta: str
    data_m: float | None
    """La lunghezza del progettista; `None` se e' nella pianta e il grafo non ce l'ha."""
    misurata_m: float
    dove: str
    """«grafo» o «pianta»: dove il progettista l'ha scritta."""


@dataclass
class Aggiornamento:
    """Che cosa la pianta scrive nel grafo, o scriverebbe se il grafo non fosse in sola lettura."""

    file: str
    sola_lettura: bool
    lunghezze: list[Cambio] = field(default_factory=list)
    allineate: list[str] = field(default_factory=list)
    """Le tratte con la misura della pianta gia' nel grafo, uguale a quella di adesso."""
    del_progettista: list[Lasciata] = field(default_factory=list)
    attraversamenti: list[Cambio] = field(default_factory=list)
    attraversamenti_del_progettista: list[str] = field(default_factory=list)
    non_nel_grafo: list[str] = field(default_factory=list)
    non_instradate: list[str] = field(default_factory=list)
    scritto: bool = False
    formato_conservato: bool = True
    """Il file riscritto ha lo stesso stile di prima (rientro, separatori, accenti)."""
    testo_nuovo: str | None = field(default=None, repr=False)
    """Il file come sara' scritto, se qualcosa cambia."""

    @property
    def da_scrivere(self) -> bool:
        return bool(self.lunghezze or self.attraversamenti)

    def scrivi(self, percorso: Path) -> None:
        """Scrive il grafo, se qualcosa cambia e non e' in sola lettura."""
        if self.sola_lettura or not self.da_scrivere or self.testo_nuovo is None:
            return
        percorso.write_text(self.testo_nuovo, encoding="utf-8")
        self.scritto = True

    @property
    def nel_grafo(self) -> set[str]:
        """Le tratte la cui misura e' nel grafo dopo il passaggio (o lo sarebbe)."""
        return {c.tratta for c in self.lunghezze} | set(self.allineate)

    @property
    def misure_segnalate(self) -> list[Lasciata]:
        """Le lunghezze del progettista che la pianta misura diverse."""
        return [
            lasciata for lasciata in self.del_progettista
            if lasciata.data_m is None or abs(lasciata.data_m - lasciata.misurata_m) > TOLLERANZA_M
        ]

    def come_dati(self) -> dict[str, object]:
        return {
            "file": self.file,
            "sola_lettura": self.sola_lettura,
            "scritto": self.scritto,
            "formato_conservato": self.formato_conservato,
            "lunghezze_cambiate": [
                {"tratta": c.tratta, "tubazioni": list(c.tubazioni), "prima_m": c.prima, "dopo_m": c.dopo}
                for c in self.lunghezze
            ],
            "lunghezze_allineate": self.allineate,
            "lunghezze_del_progettista": [
                {"tratta": lasciata.tratta, "data_m": lasciata.data_m, "misurata_m": lasciata.misurata_m,
                 "dove": lasciata.dove}
                for lasciata in self.misure_segnalate
            ],
            "attraversamenti_cambiati": [
                {"tratta": c.tratta, "tubazioni": list(c.tubazioni), "prima": c.prima, "dopo": c.dopo}
                for c in self.attraversamenti
            ],
            "attraversamenti_del_progettista": self.attraversamenti_del_progettista,
            "tratte_che_il_grafo_non_ha": self.non_nel_grafo,
            "tratte_non_instradate": self.non_instradate,
        }

    def righe(self) -> list[str]:
        """Il riassunto per la console: che cosa e' cambiato, tratta per tratta."""
        def m(valore: float | None) -> str:
            return "—" if valore is None else _metri(valore)

        def tratte(n: int) -> str:
            return f"{n} tratt{'a' if n == 1 else 'e'}"

        righe: list[str] = []
        if self.scritto:
            testa = f"Grafo {self.file}: scritte le lunghezze di {tratte(len(self.lunghezze))}"
        elif self.sola_lettura and self.da_scrivere:
            testa = (f"Grafo {self.file} in sola lettura: non scritto; cambierebbero le lunghezze di "
                     f"{tratte(len(self.lunghezze))}")
        elif self.da_scrivere:
            testa = f"Grafo {self.file}: da scrivere le lunghezze di {tratte(len(self.lunghezze))}"
        else:
            testa = f"Grafo {self.file}: nessuna lunghezza cambiata, il file non si riscrive"
        if self.attraversamenti:
            testa += f" e gli attraversamenti di {tratte(len(self.attraversamenti))}"
        righe.append(testa)
        righe += [f"  - {c.tratta}: {m(c.prima)} → {m(c.dopo)} ({', '.join(c.tubazioni)})" for c in self.lunghezze]
        righe += [
            f"  - {c.tratta}: attraversamenti {'—' if c.prima is None else int(c.prima)} → {int(c.dopo)}"
            for c in self.attraversamenti
        ]
        if self.scritto and not self.formato_conservato:
            righe.append("  Il file era in uno stile che non si riproduce identico: riscritto con lo stesso rientro.")
        segnalate = self.misure_segnalate
        if segnalate:
            righe.append(
                "Lunghezze del progettista, lasciate come sono (la pianta misura altro): "
                + "; ".join(
                    f"{lasciata.tratta} {m(lasciata.data_m)}{' nella pianta' if lasciata.dove == 'pianta' else ''}"
                    f" (misura {m(lasciata.misurata_m)})"
                    for lasciata in segnalate
                )
            )
        if self.attraversamenti_del_progettista:
            righe.append("Attraversamenti del progettista, lasciati: " + ", ".join(self.attraversamenti_del_progettista))
        if self.non_nel_grafo:
            righe.append("Tratte che il grafo non ha (non scritte): " + ", ".join(self.non_nel_grafo))
        if self.non_instradate:
            righe.append("Tratte non instradate (non scritte): " + ", ".join(self.non_instradate))
        return righe


@dataclass(frozen=True)
class Tratta:
    """Quello che la pianta sa di una tratta, per scriverla nel grafo."""

    tratta: str
    tubazioni: tuple[str, ...]
    """Le tubazioni del grafo, nell'ordine dei tronchi (da `da` ad `a`); vuota se il grafo
    non l'ha."""
    misurata_m: float
    data_nella_pianta_m: float | None
    """La lunghezza che la pianta dichiara sul tracciato (del progettista)."""
    instradata: bool
    attraversamenti: int | None = None
    """Le pareti interne forate, se le forature sono accese."""


def aggiorna(percorso: Path, tratte: Sequence[Tratta], sola_lettura: bool) -> Aggiornamento:
    """Che cosa cambia nel grafo: le tratte una per una, e il file nuovo. Non scrive:
    lo fa `Aggiornamento.scrivi`, dopo la tavola."""
    testo = percorso.read_text(encoding="utf-8")
    dati = json.loads(testo)
    esito = Aggiornamento(file=percorso.name, sola_lettura=sola_lettura)
    tubazioni = {
        str(t.get("id")): t for t in dati.get("connections", []) if isinstance(t, dict)
    }
    for tratta in tratte:
        if not tratta.tubazioni or any(i not in tubazioni for i in tratta.tubazioni):
            esito.non_nel_grafo.append(tratta.tratta)
            continue
        if not tratta.instradata:
            esito.non_instradate.append(tratta.tratta)
            continue
        delle = [tubazioni[i] for i in tratta.tubazioni]
        _le_lunghezze(esito, tratta, delle)
        if tratta.attraversamenti is not None:
            _gli_attraversamenti(esito, tratta, delle[0])
    if esito.da_scrivere:
        esito.testo_nuovo, esito.formato_conservato = _nello_stile_di(dati, testo)
    return esito


def _le_lunghezze(esito: Aggiornamento, tratta: Tratta, delle: list[dict[str, Any]]) -> None:
    di_chi = provenienza_della_tratta(delle)
    if tratta.data_nella_pianta_m is not None or di_chi == "progettista":
        if di_chi == "progettista":
            date = [numero(lunghezza_della_tubazione(t)) for t in delle]
            data: float | None = round(sum(v for v in date if v is not None), 3)
            dove = "grafo"
        else:
            data, dove = tratta.data_nella_pianta_m, "pianta"
        esito.del_progettista.append(Lasciata(tratta.tratta, data, tratta.misurata_m, dove))
        return
    # Qui nessuna tubazione ha la lunghezza del progettista: o non ce l'ha, o e' della pianta.
    prima_di = [numero(lunghezza_della_tubazione(t)) for t in delle]
    prima = None if all(v is None for v in prima_di) else round(sum(v or 0.0 for v in prima_di), 3)
    prima_tubazione, altre = delle[0], [t for t in delle[1:] if provenienza(t) == "pianta"]
    cambiata = prima_di[0] is None or abs(prima_di[0] - tratta.misurata_m) > TOLLERANZA_M or bool(altre)
    if not cambiata:
        esito.allineate.append(tratta.tratta)
        return
    nuova = tratta.misurata_m
    if "lunghezza_m" not in prima_tubazione and "lunghezza_m" in (prima_tubazione.get("properties") or {}):
        _metti(prima_tubazione["properties"], "lunghezza_m", nuova)
    else:
        _metti(prima_tubazione, "lunghezza_m", nuova)
    proprieta = prima_tubazione.get("properties")
    if not isinstance(proprieta, dict):
        proprieta = {}
        _metti(prima_tubazione, "properties", proprieta)
    _metti(proprieta, LUNGHEZZA_DALLA_PIANTA, nuova)
    # Una lunghezza della pianta rimasta su un'altra tubazione della tratta si toglie: la
    # tratta ne ha una sola, e la distinta le sommerebbe.
    for altra in altre:
        altra.pop("lunghezza_m", None)
        (altra.get("properties") or {}).pop("lunghezza_m", None)
        (altra.get("properties") or {}).pop(LUNGHEZZA_DALLA_PIANTA, None)
    esito.lunghezze.append(Cambio(tratta.tratta, (str(prima_tubazione.get("id")),), prima, nuova))


def _gli_attraversamenti(esito: Aggiornamento, tratta: Tratta, prima_tubazione: dict[str, Any]) -> None:
    assert tratta.attraversamenti is not None
    proprieta = prima_tubazione.get("properties")
    proprieta = proprieta if isinstance(proprieta, dict) else {}
    adesso = proprieta.get(ATTRAVERSAMENTI)
    if adesso not in (None, "") and not dalla_pianta(adesso, proprieta.get(ATTRAVERSAMENTI_DALLA_PIANTA)):
        esito.attraversamenti_del_progettista.append(tratta.tratta)
        return
    if numero(adesso) == tratta.attraversamenti:
        return
    if "properties" not in prima_tubazione or not isinstance(prima_tubazione["properties"], dict):
        _metti(prima_tubazione, "properties", proprieta)
    _metti(proprieta, ATTRAVERSAMENTI, tratta.attraversamenti)
    _metti(proprieta, ATTRAVERSAMENTI_DALLA_PIANTA, tratta.attraversamenti)
    esito.attraversamenti.append(
        Cambio(tratta.tratta, (str(prima_tubazione.get("id")),), numero(adesso), float(tratta.attraversamenti))
    )


# --- lo stile del file ----------------------------------------------------------------------


def _metti(oggetto: dict[str, Any], chiave: str, valore: object) -> None:
    """Scrive la chiave al suo posto: dov'era; se e' nuova, al suo posto alfabetico se
    l'oggetto ha le chiavi in ordine alfabetico, se no in fondo."""
    if chiave in oggetto or list(oggetto) != sorted(oggetto):
        oggetto[chiave] = valore
        return
    vecchio = dict(oggetto)
    oggetto.clear()
    messa = False
    for k, v in vecchio.items():
        if not messa and chiave < k:
            oggetto[chiave] = valore
            messa = True
        oggetto[k] = v
    if not messa:
        oggetto[chiave] = valore


def _stile(testo: str) -> dict[str, Any]:
    """Rientro, separatori e caratteri accentati del file, per riscriverlo uguale."""
    righe = testo.splitlines()
    rientro: str | int | None = None
    for riga in righe[1:]:
        spazi = riga[: len(riga) - len(riga.lstrip())]
        if spazi:
            rientro = len(spazi) if set(spazi) == {" "} else spazi
            break
    if rientro is None:
        separatori = (",", ":") if '":' in testo and '": ' not in testo else (", ", ": ")
    else:
        separatori = (",", ": ")
    accenti_scritti = any(ord(c) > 127 for c in testo)
    return {"indent": rientro, "separators": separatori,
            "ensure_ascii": not accenti_scritti and "\\u" in testo}


def _nello_stile_di(dati: object, testo: str) -> tuple[str, bool]:
    """I dati nel testo del file, nello stile in cui erano; e se lo stile si riproduce
    identico (l'originale riscritto senza cambi torna byte per byte)."""
    stile = _stile(testo)
    a_capo = "\n" if testo.endswith("\n") else ""
    conservato = json.dumps(json.loads(testo), **stile) + a_capo == testo
    return json.dumps(dati, **stile) + a_capo, conservato
