"""La pianta confrontata con la distinta e con il grafo: sigle, numeri di tratta, lunghezze.

Collaudo T3 della 1.6.0: le sigle e i numeri di tratta della pianta **si
ricopiavano a mano** dalla tavola dello schema e dalla tabella delle tratte, e
la nota della tavola («Sigle e numeri di tratta come lo schema funzionale e la
distinta») era vera solo se l'agente non sbagliava a copiare. Il comando
`pianta` accetta ora i due file d'uscita degli altri comandi:

- `--distinta <distinta.json>` — quello che scrive `mep.py distinta`. Ogni
  tracciato deve avere nella distinta una tratta con **lo stesso numero**, **gli
  stessi capi** (le sigle, in un verso o nell'altro, con gli stessi organi in
  linea) e **la stessa lunghezza data**; ogni tratta della distinta, salvo i
  raccordi diretti, deve essere in pianta;
- `--grafo <grafo-completo.json>` — il grafo dello schema. Ogni pezzo della
  pianta con un `id` deve esserci, con la stessa sigla che lo schema gli da';
  ogni coppia di capi di un tracciato deve essere una tubazione del grafo con
  lo stesso fluido, e la lunghezza data quella del grafo; ogni tubazione del
  grafo, salvo i raccordi diretti (lunghezza 0), deve essere in pianta. Il grafo
  non numera le tratte: i numeri li controlla solo la distinta.

Ogni discordanza e' un rilievo: un avviso, sulla tavola e in console; **un
numero di tratta che nella distinta collega pezzi diversi ferma la consegna**,
perche' sulla pianta e sulla distinta lo stesso numero direbbe due cose.

Se un tracciato non da' la lunghezza, la prende dalla distinta (o, senza
distinta, dal grafo), e la tabella lo dice. **Non prende una misura della pianta**
(REL-026, B-4): la lunghezza che la pianta stessa ha scritto nel grafo
(`nel_grafo.py`, il segno `lunghezza_dalla_pianta_m`), e che la distinta fatta da
quel grafo riporta, non e' del progettista, e non si confronta.

Sulla tavola le discordanze si riassumono (`Confronto.per_la_tavola`, B-5): per
esteso stanno in console e in `.tracciati.json`.

**Si legge un file, non si importa la distinta**: `distinta.json` e' l'uscita
del comando, e la distinta resta spenta di default (D-213,
`tests/distinta/test_da_definire.py`).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .instrada import chiave_della_tratta
from .lunghezze import metri
from .modello import Pianta, Tracciato
from .nel_grafo import lunghezza_della_tubazione, provenienza, provenienza_della_tratta

TOLLERANZA_M = 1e-6


TIPI_DI_DISCORDANZA: dict[str, tuple[str, str]] = {
    "fuori_dalla_distinta": ("tratta della pianta che la distinta non ha", "tratte della pianta che la distinta non ha"),
    "organi_in_linea": ("tratta con organi in linea diversi", "tratte con organi in linea diversi"),
    "lunghezza_della_distinta": ("lunghezza diversa dalla distinta", "lunghezze diverse dalla distinta"),
    "tratta_non_in_pianta": ("tratta della distinta non in pianta", "tratte della distinta non in pianta"),
    "id_fuori_dal_grafo": ("id di pezzo che il grafo non ha", "id di pezzi che il grafo non ha"),
    "sigla": ("sigla diversa dallo schema", "sigle diverse dallo schema"),
    "pezzo_fuori_dal_grafo": ("pezzo che il grafo non ha", "pezzi che il grafo non ha"),
    "non_e_una_tubazione": ("tracciato che non e' una tubazione del grafo",
                            "tracciati che non sono tubazioni del grafo"),
    "lunghezza_del_grafo": ("lunghezza diversa dal grafo", "lunghezze diverse dal grafo"),
    "tubazione_non_in_pianta": ("tubazione del grafo non in pianta", "tubazioni del grafo non in pianta"),
}
"""I tipi di discordanza, al singolare e al plurale: la tavola li conta (REL-026, B-5)."""


@dataclass
class Confronto:
    avvisi: list[str] = field(default_factory=list)
    bloccanti: list[str] = field(default_factory=list)
    lunghezze: dict[str, tuple[float, str]] = field(default_factory=dict)
    """Per tratta senza lunghezza nella pianta: la lunghezza presa e da dove."""
    fonti: list[str] = field(default_factory=list)
    """Con che cosa si e' confrontata la pianta: «la distinta», «il grafo»."""
    per_tipo: dict[str, list[str]] = field(default_factory=dict)
    """Gli avvisi per tipo (`TIPI_DI_DISCORDANZA`), nell'ordine in cui escono."""
    tratte_bloccanti: list[str] = field(default_factory=list)
    """I numeri di tratta che nella distinta collegano pezzi diversi."""
    tubazioni: dict[str, list[str]] = field(default_factory=dict)
    """Per tratta, le tubazioni del grafo che le corrispondono, nell'ordine dei tronchi
    (REL-026, B-4: sono quelle su cui la pianta scrive la misura)."""
    misure_della_pianta: list[str] = field(default_factory=list)
    """Le tratte la cui lunghezza nel grafo (o nella distinta) l'ha scritta la pianta:
    e' una misura, non la lunghezza del progettista, e non si prende come L prog."""

    def avviso(self, tipo: str, testo: str) -> None:
        self.avvisi.append(testo)
        self.per_tipo.setdefault(tipo, []).append(testo)

    @property
    def nota(self) -> str:
        """Quello che la nota della tavola dice del controllo."""
        if not self.fonti:
            return "Non controllati dal comando."
        con = " e ".join(self.fonti)
        if self.avvisi or self.bloccanti:
            return f"Controllati con {con}: ci sono discordanze (vedi gli avvisi)."
        return f"Controllati con {con}: concordano."

    def per_la_tavola(self, dati: str) -> list[str]:
        """Le discordanze **riassunte**, per gli avvisi della tavola: quante, di che tipo,
        dove si leggono per esteso (`dati`, il nome del `.tracciati.json`).

        BD.RM.260: `pianta --grafo` dava 72 avvisi, e l'elenco scritto per intero nella
        colonna portava il foglio da A2 ad A1 (anche `--distinta` lo portava in A1). Il
        formato lo decide il disegno: l'elenco sta nei dati e in console."""
        if not self.avvisi and not self.bloccanti:
            return []
        con = " e ".join(self.fonti)
        dove = f"L'elenco per esteso e' in {dati} («confronto») e in console."
        righe: list[str] = []
        if self.bloccanti:
            quali = ", ".join(sorted(self.tratte_bloccanti, key=chiave_della_tratta)) or str(len(self.bloccanti))
            righe.append(
                f"Ferma la consegna: {quali} nella distinta collega{'no' if len(self.bloccanti) > 1 else ''} "
                f"pezzi diversi da quelli della pianta."
            )
        if self.avvisi:
            voci = [
                f"{len(elenco)} {TIPI_DI_DISCORDANZA[tipo][0 if len(elenco) == 1 else 1]}"
                for tipo, elenco in self.per_tipo.items()
            ]
            n = len(self.avvisi)
            righe.append(f"Confronto con {con}: {n} discordanz{'a' if n == 1 else 'e'} ({'; '.join(voci)}).")
        righe[-1] += " " + dove
        return righe


class ErroreDelConfronto(ValueError):
    """Un file da confrontare che non si legge: il messaggio dice quale e perche'."""


def _leggi(percorso: Path, cosa: str) -> Any:
    try:
        return json.loads(percorso.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as errore:
        raise ErroreDelConfronto(f"{percorso}: {cosa} non si legge ({errore})") from None


def _numero(valore: object) -> float | None:
    if isinstance(valore, bool):
        return None
    if isinstance(valore, int | float):
        return float(valore)
    if isinstance(valore, str):
        try:
            return float(valore.strip().replace(",", "."))
        except ValueError:
            return None
    return None


def _capi(tracciato: Tracciato) -> list[str]:
    return [tracciato.estremo_da.pezzo, *tracciato.passa_per, tracciato.estremo_a.pezzo]


def _stessi_capi(a: Sequence[str], b: Sequence[str]) -> bool:
    return list(a) == list(b) or list(a) == list(reversed(b))


def _in_parole(capi: Sequence[str]) -> str:
    return " – ".join(capi)


def _della_pianta(voce: Mapping[str, Any], provenienze: Mapping[str, str | None]) -> bool:
    """La lunghezza di una tratta della distinta l'ha scritta la pianta: lo dice la
    distinta, o lo dice il grafo per le sue tubazioni con una lunghezza."""
    if voce.get("lunghezza_dalla_pianta"):
        return True
    di = {provenienze.get(str(i)) for i in voce.get("tubazioni") or []} - {None}
    return di == {"pianta"}


def confronta_con_la_distinta(
    pianta: Pianta, percorso: Path, confronto: Confronto, provenienze: Mapping[str, str | None] | None = None,
) -> None:
    dati = _leggi(percorso, "la distinta")
    if not isinstance(dati, Mapping) or not isinstance(dati.get("tratte"), list):
        raise ErroreDelConfronto(
            f"{percorso}: non e' il distinta.json del comando `distinta` (manca l'elenco «tratte»)"
        )
    confronto.fonti.append("la distinta")
    tratte: dict[str, dict[str, Any]] = {}
    for voce in dati["tratte"]:
        if isinstance(voce, Mapping) and isinstance(voce.get("num"), str) and voce["num"]:
            tratte[voce["num"]] = dict(voce)

    def capi_della_distinta(voce: Mapping[str, Any]) -> list[str]:
        return [c.strip() for c in str(voce.get("da_a", "")).split(" - ") if c.strip()]

    for tracciato in pianta.tracciati:
        capi = _capi(tracciato)
        voce = tratte.get(tracciato.tratta)
        if voce is None:
            stessi = [n for n, v in tratte.items() if _stessi_capi(capi_della_distinta(v), capi)]
            altrove = f"; con questi capi nella distinta c'e' {', '.join(stessi)}" if stessi else ""
            confronto.avviso(
                "fuori_dalla_distinta", f"{tracciato.tratta} ({_in_parole(capi)}) non c'e' nella distinta{altrove}."
            )
            continue
        della_distinta = capi_della_distinta(voce)
        if not _stessi_capi(della_distinta, capi):
            stessi_capi_estremi = bool(della_distinta) and {della_distinta[0], della_distinta[-1]} == {capi[0], capi[-1]}
            if stessi_capi_estremi:
                confronto.avviso(
                    "organi_in_linea",
                    f"{tracciato.tratta}: in pianta {_in_parole(capi)}, nella distinta "
                    f"{_in_parole(della_distinta)} (gli organi in linea non coincidono).",
                )
            else:
                stessi = [n for n, v in tratte.items() if _stessi_capi(capi_della_distinta(v), capi)]
                giusto = f"; questi capi nella distinta sono {', '.join(stessi)}" if stessi else ""
                confronto.bloccanti.append(
                    f"{tracciato.tratta} collega pezzi diversi: in pianta {_in_parole(capi)}, nella distinta "
                    f"{_in_parole(della_distinta)}{giusto}"
                )
                confronto.tratte_bloccanti.append(tracciato.tratta)
            continue
        data = _numero(voce.get("lunghezza_stimata_m"))
        if data is not None and _della_pianta(voce, provenienze or {}):
            # E' la misura che la pianta ha scritto nel grafo (B-4): non e' L prog.
            if tracciato.tratta not in confronto.misure_della_pianta:
                confronto.misure_della_pianta.append(tracciato.tratta)
            data = None
        if tracciato.lunghezza_m is None:
            if data is not None:
                confronto.lunghezze.setdefault(tracciato.tratta, (data, "distinta"))
        elif data is not None and abs(data - tracciato.lunghezza_m) > TOLLERANZA_M:
            confronto.avviso(
                "lunghezza_della_distinta",
                f"{tracciato.tratta}: L {metri(tracciato.lunghezza_m, 2)} m in pianta, "
                f"{metri(data, 2)} m nella distinta.",
            )
    in_pianta = {t.tratta for t in pianta.tracciati}
    for numero, voce in tratte.items():
        if numero in in_pianta or voce.get("raccordo_diretto"):
            continue
        confronto.avviso(
            "tratta_non_in_pianta", f"{numero} della distinta ({_in_parole(capi_della_distinta(voce))}) non e' in pianta."
        )


def sigle_dello_schema(
    grafo: Mapping[str, Any], catalogo: Path | None, nomi: Path | None
) -> dict[str, str]:
    """Le sigle che lo schema scrive, dalla stessa lettura dell'impianto che le da'
    alla tavola (`graph.plant.read_plant`); senza catalogo, o se il grafo non si
    lascia leggere, le sole `tag` scritte dall'ingegnere."""
    sigle = {
        str(c["id"]): str(c["tag"]) for c in grafo.get("components", [])
        if isinstance(c, Mapping) and isinstance(c.get("id"), str) and isinstance(c.get("tag"), str) and c["tag"]
    }
    if catalogo is None or nomi is None:
        return sigle
    from pydantic import ValidationError

    from disegnatore_mep.catalog.errors import CatalogError
    from disegnatore_mep.catalog.registry import ComponentRegistry
    from disegnatore_mep.graph.naming import Naming, NamingError
    from disegnatore_mep.graph.plant import GraphError, read_plant
    from disegnatore_mep.model.project import ProjectModel

    try:
        modello = ProjectModel.model_validate(dict(grafo))
        registro = ComponentRegistry.from_directory(catalogo).per_il_progetto(modello)
        return {**dict(read_plant(modello, registro, Naming.from_directory(nomi)).sigle), **sigle}
    except (ValidationError, CatalogError, GraphError, NamingError, ValueError, OSError):
        return sigle


def confronta_con_il_grafo(
    pianta: Pianta, percorso: Path, confronto: Confronto,
    catalogo: Path | None = None, nomi: Path | None = None,
) -> None:
    grafo = _leggi(percorso, "il grafo")
    if not isinstance(grafo, Mapping) or not isinstance(grafo.get("components"), list):
        raise ErroreDelConfronto(f"{percorso}: non e' un grafo (manca l'elenco «components»)")
    confronto.fonti.append("il grafo")
    sigle_del_grafo = sigle_dello_schema(grafo, catalogo, nomi)
    componenti = [str(c.get("id")) for c in grafo["components"] if isinstance(c, Mapping)]
    reti = {
        str(r.get("id")): str(r.get("medium")) for r in grafo.get("networks", []) if isinstance(r, Mapping)
    }
    # Dal grafo alla pianta: l'id dichiarato sul pezzo, o la sigla dello schema.
    per_sigla_del_grafo = {s: i for i, s in sigle_del_grafo.items()}
    id_di: dict[str, str] = {}
    for pezzo in pianta.pezzi:
        if pezzo.id is not None:
            if pezzo.id not in componenti:
                confronto.avviso("id_fuori_dal_grafo", f"{pezzo.sigla}: l'id {pezzo.id!r} non c'e' nel grafo.")
                continue
            id_di[pezzo.sigla] = pezzo.id
            dello_schema = sigle_del_grafo.get(pezzo.id)
            if dello_schema is not None and dello_schema != pezzo.sigla:
                confronto.avviso("sigla", f"{pezzo.sigla} ({pezzo.id}): lo schema lo chiama {dello_schema}.")
        elif pezzo.sigla in per_sigla_del_grafo:
            id_di[pezzo.sigla] = per_sigla_del_grafo[pezzo.sigla]
        else:
            confronto.avviso(
                "pezzo_fuori_dal_grafo",
                f"{pezzo.sigla}: non si ritrova nel grafo (ne' l'id ne' la sigla dello schema).",
            )
    sigla_di = {i: s for s, i in id_di.items()}

    tubazioni: list[tuple[frozenset[str], str, float | None, str]] = []
    per_id: dict[str, Mapping[str, Any]] = {}
    for tubazione in grafo.get("connections", []):
        if not isinstance(tubazione, Mapping):
            continue
        a = str((tubazione.get("endpoint_a") or {}).get("component_id"))
        b = str((tubazione.get("endpoint_b") or {}).get("component_id"))
        tubazioni.append((frozenset((a, b)), reti.get(str(tubazione.get("network_id")), ""),
                          _numero(lunghezza_della_tubazione(tubazione)), str(tubazione.get("id"))))
        per_id[str(tubazione.get("id"))] = tubazione
    usate: set[str] = set()
    for tracciato in pianta.tracciati:
        capi = _capi(tracciato)
        if any(c not in id_di for c in capi):
            continue
        somma: float | None = 0.0
        manca = False
        accoppiate: list[str] = []
        for da, a in zip(capi, capi[1:], strict=False):
            coppia = frozenset((id_di[da], id_di[a]))
            trovate = [t for t in tubazioni if t[0] == coppia and t[1] == tracciato.fluido and t[3] not in usate]
            if not trovate:
                confronto.avviso(
                    "non_e_una_tubazione",
                    f"{tracciato.tratta}: {da} – {a} ({tracciato.fluido}) non e' una tubazione del grafo.",
                )
                manca = True
                break
            usate.add(trovate[0][3])
            accoppiate.append(trovate[0][3])
            if trovate[0][2] is not None and somma is not None:
                somma += trovate[0][2]
        if manca:
            continue
        confronto.tubazioni[tracciato.tratta] = accoppiate
        if provenienza_della_tratta([per_id[i] for i in accoppiate]) == "pianta":
            # La lunghezza nel grafo e' la misura che la pianta ci ha scritto (B-4): non e'
            # quella del progettista, non si prende come L prog. e non si confronta.
            if tracciato.tratta not in confronto.misure_della_pianta:
                confronto.misure_della_pianta.append(tracciato.tratta)
            continue
        if somma is not None and somma > TOLLERANZA_M:
            if tracciato.lunghezza_m is None:
                confronto.lunghezze.setdefault(tracciato.tratta, (somma, "grafo"))
            elif abs(somma - tracciato.lunghezza_m) > TOLLERANZA_M:
                confronto.avviso(
                    "lunghezza_del_grafo",
                    f"{tracciato.tratta}: L {metri(tracciato.lunghezza_m, 2)} m in pianta, "
                    f"{metri(somma, 2)} m nel grafo.",
                )
    for coppia, fluido, lunghezza, ident in tubazioni:
        if ident in usate or lunghezza == 0:
            continue
        nomi_dei_capi = " – ".join(sorted(sigla_di.get(c, sigle_del_grafo.get(c, c)) for c in coppia))
        confronto.avviso("tubazione_non_in_pianta", f"La tubazione {nomi_dei_capi} ({fluido}) del grafo non e' in pianta.")


def confronta(
    pianta: Pianta, distinta: Path | None, grafo: Path | None,
    catalogo: Path | None = None, nomi: Path | None = None,
) -> Confronto:
    confronto = Confronto()
    if distinta is not None:
        # Il grafo dice quali lunghezze ha scritto la pianta (B-4): la distinta fatta da quel
        # grafo le riporta, e non sono lunghezze del progettista.
        provenienze: dict[str, str | None] = {}
        if grafo is not None:
            dati_del_grafo = _leggi(grafo, "il grafo")
            if isinstance(dati_del_grafo, Mapping):
                provenienze = {
                    str(t.get("id")): provenienza(t)
                    for t in dati_del_grafo.get("connections", []) if isinstance(t, Mapping)
                }
        confronta_con_la_distinta(pianta, distinta, confronto, provenienze)
    if grafo is not None:
        confronta_con_il_grafo(pianta, grafo, confronto, catalogo, nomi)
    return confronto


def con_le_lunghezze(pianta: Pianta, confronto: Confronto) -> Pianta:
    """La pianta con le lunghezze prese dalla distinta (o dal grafo) dove il
    tracciato non le da'."""
    if not confronto.lunghezze:
        return pianta
    tracciati = [
        t.model_copy(update={"lunghezza_m": confronto.lunghezze[t.tratta][0]})
        if t.lunghezza_m is None and t.tratta in confronto.lunghezze else t
        for t in pianta.tracciati
    ]
    return pianta.model_copy(update={"tracciati": tracciati})
