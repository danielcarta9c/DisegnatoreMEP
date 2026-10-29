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
distinta, dal grafo), e la tabella lo dice.

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

from .lunghezze import metri
from .modello import Pianta, Tracciato

TOLLERANZA_M = 1e-6


@dataclass
class Confronto:
    avvisi: list[str] = field(default_factory=list)
    bloccanti: list[str] = field(default_factory=list)
    lunghezze: dict[str, tuple[float, str]] = field(default_factory=dict)
    """Per tratta senza lunghezza nella pianta: la lunghezza presa e da dove."""
    fonti: list[str] = field(default_factory=list)
    """Con che cosa si e' confrontata la pianta: «la distinta», «il grafo»."""

    @property
    def nota(self) -> str:
        """Quello che la nota della tavola dice del controllo."""
        if not self.fonti:
            return "Non controllati dal comando."
        con = " e ".join(self.fonti)
        if self.avvisi or self.bloccanti:
            return f"Controllati con {con}: ci sono discordanze (vedi gli avvisi)."
        return f"Controllati con {con}: concordano."


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


def confronta_con_la_distinta(pianta: Pianta, percorso: Path, confronto: Confronto) -> None:
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
            confronto.avvisi.append(
                f"{tracciato.tratta} ({_in_parole(capi)}) non c'e' nella distinta{altrove}."
            )
            continue
        della_distinta = capi_della_distinta(voce)
        if not _stessi_capi(della_distinta, capi):
            stessi_capi_estremi = bool(della_distinta) and {della_distinta[0], della_distinta[-1]} == {capi[0], capi[-1]}
            if stessi_capi_estremi:
                confronto.avvisi.append(
                    f"{tracciato.tratta}: in pianta {_in_parole(capi)}, nella distinta "
                    f"{_in_parole(della_distinta)} (gli organi in linea non coincidono)."
                )
            else:
                stessi = [n for n, v in tratte.items() if _stessi_capi(capi_della_distinta(v), capi)]
                giusto = f"; questi capi nella distinta sono {', '.join(stessi)}" if stessi else ""
                confronto.bloccanti.append(
                    f"{tracciato.tratta} collega pezzi diversi: in pianta {_in_parole(capi)}, nella distinta "
                    f"{_in_parole(della_distinta)}{giusto}"
                )
            continue
        data = _numero(voce.get("lunghezza_stimata_m"))
        if tracciato.lunghezza_m is None:
            if data is not None:
                confronto.lunghezze.setdefault(tracciato.tratta, (data, "distinta"))
        elif data is not None and abs(data - tracciato.lunghezza_m) > TOLLERANZA_M:
            confronto.avvisi.append(
                f"{tracciato.tratta}: L {metri(tracciato.lunghezza_m, 2)} m in pianta, "
                f"{metri(data, 2)} m nella distinta."
            )
    in_pianta = {t.tratta for t in pianta.tracciati}
    for numero, voce in tratte.items():
        if numero in in_pianta or voce.get("raccordo_diretto"):
            continue
        confronto.avvisi.append(
            f"{numero} della distinta ({_in_parole(capi_della_distinta(voce))}) non e' in pianta."
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
                confronto.avvisi.append(f"{pezzo.sigla}: l'id {pezzo.id!r} non c'e' nel grafo.")
                continue
            id_di[pezzo.sigla] = pezzo.id
            dello_schema = sigle_del_grafo.get(pezzo.id)
            if dello_schema is not None and dello_schema != pezzo.sigla:
                confronto.avvisi.append(
                    f"{pezzo.sigla} ({pezzo.id}): lo schema lo chiama {dello_schema}."
                )
        elif pezzo.sigla in per_sigla_del_grafo:
            id_di[pezzo.sigla] = per_sigla_del_grafo[pezzo.sigla]
        else:
            confronto.avvisi.append(
                f"{pezzo.sigla}: non si ritrova nel grafo (ne' l'id ne' la sigla dello schema)."
            )
    sigla_di = {i: s for s, i in id_di.items()}

    tubazioni: list[tuple[frozenset[str], str, float | None, str]] = []
    for tubazione in grafo.get("connections", []):
        if not isinstance(tubazione, Mapping):
            continue
        a = str((tubazione.get("endpoint_a") or {}).get("component_id"))
        b = str((tubazione.get("endpoint_b") or {}).get("component_id"))
        lunghezza = tubazione.get("lunghezza_m")
        if lunghezza is None:
            lunghezza = (tubazione.get("properties") or {}).get("lunghezza_m")
        tubazioni.append((frozenset((a, b)), reti.get(str(tubazione.get("network_id")), ""),
                          _numero(lunghezza), str(tubazione.get("id"))))
    usate: set[str] = set()
    for tracciato in pianta.tracciati:
        capi = _capi(tracciato)
        if any(c not in id_di for c in capi):
            continue
        somma: float | None = 0.0
        manca = False
        for da, a in zip(capi, capi[1:], strict=False):
            coppia = frozenset((id_di[da], id_di[a]))
            trovate = [t for t in tubazioni if t[0] == coppia and t[1] == tracciato.fluido and t[3] not in usate]
            if not trovate:
                confronto.avvisi.append(
                    f"{tracciato.tratta}: {da} – {a} ({tracciato.fluido}) non e' una tubazione del grafo."
                )
                manca = True
                break
            usate.add(trovate[0][3])
            if trovate[0][2] is not None and somma is not None:
                somma += trovate[0][2]
        if manca:
            continue
        if somma is not None and somma > TOLLERANZA_M:
            if tracciato.lunghezza_m is None:
                confronto.lunghezze.setdefault(tracciato.tratta, (somma, "grafo"))
            elif abs(somma - tracciato.lunghezza_m) > TOLLERANZA_M:
                confronto.avvisi.append(
                    f"{tracciato.tratta}: L {metri(tracciato.lunghezza_m, 2)} m in pianta, "
                    f"{metri(somma, 2)} m nel grafo."
                )
    for coppia, fluido, lunghezza, ident in tubazioni:
        if ident in usate or lunghezza == 0:
            continue
        nomi_dei_capi = " – ".join(sorted(sigla_di.get(c, sigle_del_grafo.get(c, c)) for c in coppia))
        confronto.avvisi.append(f"La tubazione {nomi_dei_capi} ({fluido}) del grafo non e' in pianta.")


def confronta(
    pianta: Pianta, distinta: Path | None, grafo: Path | None,
    catalogo: Path | None = None, nomi: Path | None = None,
) -> Confronto:
    confronto = Confronto()
    if distinta is not None:
        confronta_con_la_distinta(pianta, distinta, confronto)
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
