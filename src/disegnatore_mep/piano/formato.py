"""Il formato dichiarato del piano di composizione, e un caricatore che parla.

Il piano e' un file JSON leggibile e correggibile a mano
(`ARCHITETTURA-DEL-PIANO.md` §4). Dice **dove sta ogni pezzo posabile**, e
nient'altro:

    { "formato": "A2",
      "note": ["D-041 + D-118 — i generatori a sinistra, incolonnati."],
      "pezzi": { "pdc-1": {"x": 35, "y": 60},
                 "filling-unit-a": {"x": 195, "y": 165, "rotazione": 180},
                 "commutatrice": {"x": 102.5, "y": 125, "rotazione": 90,
                                  "specchio": true} } }

**Le note sono parte del piano.** Un piano senza di loro dice dove stanno i
pezzi e non dice **perche'**: il revisore (D-153) lavora sulla traccia piano →
rilievi → piano, e una correzione senza il nome della regola che la motiva non
e' una correzione, e' uno spostamento. `note` porta la motivazione del piano
intero; `regola`, su ogni pezzo, e' la stessa cosa detta pezzo per pezzo.

**`nota` si legge come `note`.** I due piani della prova — `impianto-1.json` e
`impianto-5.json`, che sono le due tavole che hanno deciso D-151 — scrivono
quel campo al singolare. Sono documenti agli atti e si leggono **senza
modifiche**: il nome dichiarato e' `note`, e `nota` resta un alias di lettura.

**Che cosa il piano non contiene, perche' si deduce** (C2, C3): la rotazione di
un raccordo e quella di un pezzo con un attacco solo, e la mappa degli
attacchi. `rotazione` si scrive **solo dove la deduzione non arriva** — una
macchina con due o piu' attacchi, che ha una scelta, e il buco noto del gruppo
di riempimento (§4).

**Criterio 10 di DRAW-015:** un piano malformato da' **un errore che dice che
cosa manca**, non una traccia di stack. E' il compito di `carica_piano`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, ValidationError
from pydantic_core import ErrorDetails

from disegnatore_mep.model.base import FiniteFloat, StrictModel

FORMATI_ORDINARI: tuple[str, ...] = ("A4", "A3", "A2", "A1")
"""I formati ordinari, dal piu' piccolo al piu' grande (D-058, esteso da D-148).

Sono gli stessi di `graphics.frame.ORDINARY_FRAMES`, e l'ordine e' quello: qui
servono per **nominarli** quando un piano ne chiede un altro. D-148 e'
dichiarata momentanea dal PO stesso, e il giorno che si riapre questa tupla e
quella si spostano insieme.
"""

FormatoOrdinario = Literal["A4", "A3", "A2", "A1"]
"""Il tipo di `PianoDiComposizione.formato`: uno dei quattro, e basta."""


class ErroreDelPiano(ValueError):
    """Un piano che non si legge, detto in italiano.

    Sottoclasse di `ValueError` come `LayoutError`, `CatalogError` e
    `SymbolError`: la CLI intercetta `ValueError` e stampa il messaggio,
    quindi chi sbaglia un piano legge **che cosa manca** e non una traccia di
    stack (criterio 10).
    """


class PezzoNelPiano(StrictModel):
    """Dove sta un pezzo, e — dove serve — come e' girato e chi ce l'ha messo."""

    x: FiniteFloat
    """Millimetri dal bordo sinistro del foglio. Si arrotonda al passo di griglia."""

    y: FiniteFloat
    """Millimetri dal bordo alto del foglio. Si arrotonda al passo di griglia."""

    rotazione: int | None = None
    """Solo dove la deduzione non arriva (C2).

    `None` vuol dire «decidila tu»: per un raccordo o per un pezzo con un
    attacco solo la rotazione e' una **conseguenza** della posa e si deduce.
    Si scrive a mano per una macchina con due o piu' attacchi — che ha una
    scelta, e la scelta e' del pianificatore — e per il buco noto, il pezzo a
    due attacchi che non e' una macchina.
    """

    specchio: bool = False
    """Se il pezzo va **specchiato** attorno al proprio asse verticale.

    **D-169**, su disposizione del PO del 22 settembre 2026: «lo specchio come
    rotazione, otto orientamenti invece di quattro; tocca il motore, non il
    simbolo». Lo specchio si applica **prima** della rotazione, e insieme a
    `rotazione` da' le **otto** giaciture ortogonali di un segno piano.

    **Perche' serve, misurato.** Una valvola a tre vie ha la terza via
    **perpendicolare** alla via dritta, e ruotando si gira tutto insieme: la
    terza via resta sempre dalla stessa parte. Per una commutatrice che deve
    ricevere dall'alto, mandare in basso e prendere la terza via **a destra**,
    nessuna delle quattro rotazioni basta — a 90 gradi la terza via guarda a
    sinistra, a 270 si invertono le altre due. Sull'impianto 4 la linea che
    arriva dalla parte sbagliata **gira intorno alla valvola** con quattro
    pieghe; con lo specchio entra dritta, e la tavola passa da 3 spezzate
    piegate a 3 con una piega in meno e un sormonto in meno.

    Come `rotazione`, **si scrive dove la deduzione non arriva**: su una
    valvola a tre vie e su un pezzo a due attacchi che non e' una macchina. Per
    un raccordo la deduzione prova adesso tutte e otto le giaciture.
    """

    regola: str | None = None
    """Quale regola ha messo il pezzo li'.

    La forma per-pezzo di `PianoDiComposizione.note`. Il revisore la usa per
    dire, di ogni spostamento, da dove viene (D-153, criterio 2).
    """


class PianoDiComposizione(StrictModel):
    """Il piano intero: il foglio, le ragioni, e dove stanno i pezzi."""

    formato: FormatoOrdinario = "A3"
    """Il formato ordinario su cui il piano e' stato composto (D-148)."""

    note: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("note", "nota"),
    )
    """Le regole che hanno prodotto questo piano, scritte accanto al piano.

    Si legge anche dal nome storico `nota`, che e' quello dei due piani della
    prova: sono documenti agli atti e non si toccano.
    """

    pezzi: dict[str, PezzoNelPiano]
    """Da identificativo del componente a dove sta. Il cuore del piano."""


_ATTESO_PER_CAMPO: dict[str, str] = {
    "x": "un numero, i millimetri dal bordo sinistro del foglio",
    "y": "un numero, i millimetri dal bordo alto del foglio",
    "rotazione": "un numero intero di gradi (0, 90, 180, 270)",
    "specchio": "vero o falso: se il pezzo va specchiato prima di ruotarlo (D-169)",
    "regola": "il nome della regola che ha messo il pezzo li'",
    "formato": f"uno dei formati ordinari: {', '.join(FORMATI_ORDINARI)} (D-148)",
    "note": "un elenco di righe di testo",
    "pezzi": 'l\'elenco dei pezzi con il loro posto: {"id": {"x": …, "y": …}}',
}

_CAMPI_DEL_PEZZO = ", ".join(PezzoNelPiano.model_fields)
_CAMPI_DEL_PIANO = ", ".join(PianoDiComposizione.model_fields)


def _riga(difetto: ErrorDetails) -> str:
    """Un difetto solo, detto nominando il pezzo, il campo e cio' che si attendeva."""
    dove = difetto["loc"]
    tipo = difetto["type"]

    # Un difetto dentro `pezzi` si dice nominando **il pezzo**: in un piano da
    # cinquanta voci «campo mancante» senza il nome del pezzo non e' un
    # messaggio, e' una caccia.
    if dove[:1] == ("pezzi",) and len(dove) >= 2:
        pezzo = str(dove[1])
        if len(dove) == 2:
            return (
                f"il pezzo «{pezzo}» non e' un oggetto: era atteso "
                '{"x": …, "y": …} con i millimetri del suo posto'
            )
        campo = str(dove[2])
        if tipo == "missing":
            return (
                f"al pezzo «{pezzo}» manca «{campo}»: era atteso "
                f"{_ATTESO_PER_CAMPO.get(campo, 'un valore')}"
            )
        if tipo == "extra_forbidden":
            return (
                f"il pezzo «{pezzo}» porta il campo sconosciuto «{campo}»: "
                f"un pezzo del piano dichiara soltanto {_CAMPI_DEL_PEZZO}"
            )
        return (
            f"«{campo}» del pezzo «{pezzo}» non e' valido ({difetto['input']!r}): "
            f"era atteso {_ATTESO_PER_CAMPO.get(campo, 'un valore')}"
        )

    if not dove:
        return (
            "il piano non e' un oggetto: era atteso "
            '{"formato": …, "note": […], "pezzi": {…}}'
        )

    campo = str(dove[0])
    if tipo == "missing":
        return (
            f"manca il campo obbligatorio «{campo}»: era atteso "
            f"{_ATTESO_PER_CAMPO.get(campo, 'un valore')}"
        )
    if tipo == "extra_forbidden":
        return (
            f"il piano porta il campo sconosciuto «{campo}»: "
            f"un piano dichiara soltanto {_CAMPI_DEL_PIANO}"
        )
    return (
        f"il campo «{campo}» non e' valido ({difetto['input']!r}): era atteso "
        f"{_ATTESO_PER_CAMPO.get(campo, 'un valore')}"
    )


def _spiega(percorso: Path, errore: ValidationError) -> str:
    """Tutti i difetti di un piano, uno per riga, nell'ordine in cui stanno."""
    righe = [_riga(difetto) for difetto in errore.errors()]
    # Senza duplicati e nell'ordine d'arrivo: un campo sconosciuto dentro un
    # sotto-modello puo' arrivare due volte, e ripetere la stessa riga non
    # aggiunge niente a chi corregge.
    viste: list[str] = []
    for riga in righe:
        if riga not in viste:
            viste.append(riga)
    testa = f"il piano {percorso} non si legge"
    return testa + ":\n  - " + "\n  - ".join(viste)


def carica_piano(percorso: Path) -> PianoDiComposizione:
    """Legge un piano da file, e se non si legge **dice che cosa manca**.

    Criterio 10 di DRAW-015, ed e' un criterio di accettazione: un piano
    malformato non deve dare una traccia di stack. Chi compone lavora a mano su
    questo file, e un `KeyError: 'x'` in mezzo a una traccia non gli dice ne'
    quale pezzo ne' che cosa ci voleva.

    Le due forme di malformazione arrivano per strade diverse e tornano dalla
    stessa: un JSON rotto e' un `JSONDecodeError`, un piano che non rispetta il
    formato e' un `ValidationError` di pydantic. Entrambi diventano un
    `ErroreDelPiano` che nomina **il pezzo, il campo e che cosa ci si
    aspettava**.

    Il file che non c'e' resta un `OSError`, che e' quello che e': non un
    difetto del piano, ma un piano che non c'e'.
    """
    percorso = Path(percorso)
    testo = percorso.read_text(encoding="utf-8")
    try:
        grezzo = json.loads(testo)
    except json.JSONDecodeError as errore:
        raise ErroreDelPiano(
            f"il piano {percorso} non e' un JSON valido: {errore.msg}, "
            f"riga {errore.lineno} colonna {errore.colno}"
        ) from errore
    try:
        return PianoDiComposizione.model_validate(grezzo)
    except ValidationError as errore:
        raise ErroreDelPiano(_spiega(percorso, errore)) from errore
