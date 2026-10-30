"""La parte idronica e aeraulica di una tavola, letta sull'SVG (REL-015, I-231).

**Il PO, il 30 ottobre 2026**: «Non vorrei che le linee elettriche facciano spostare
le linee idrauliche. [...] Ricordiamoci che prima si disegna idronico - areaulico e
poi si aggiunge elettrico e comando.»

La regola, resa misurabile: **sulla tavola unica (`vista: tutto`) la parte
dell'acqua e dell'aria e' la stessa della vista `idraulica`** dello stesso grafo —
tubazioni, pezzi, e le loro sigle, etichette e scritte, ciascuna al suo posto. Questo
modulo estrae quella parte da un SVG; il confronto fra le due viste e' un'uguaglianza.

Che cosa **non** e' della parte dell'acqua, e si toglie:

- le linee dei fluidi del comando — alimentazione, collegamento fra le unita', bus —,
  riconosciute dal loro colore (`layout.legend.MEDIUM_STYLES`);
- i simboli dei pezzi che stanno **solo** sul comando (`piano.vista.solo_comando`):
  quadro, regolatore, sonda esterna, termostati;
- dentro i simboli dei pezzi d'acqua, i monconi degli attacchi di comando: un tratto
  del corpo che tocca una porta di comando del simbolo (`control_port_ids`). Sulla
  tavola unica il moncone c'e' perche' ci arriva il cavo, sull'idraulica no;
- le scritte del comando: sigle e dati dei pezzi del comando, scritte dei cavi; e i
  richiami che le portano (il renderer scrive un richiamo subito prima del suo testo).

La legenda, la tabella, il cartiglio e le tabelle nelle zone non sono il disegno:
non entrano.

**Il confronto e' a meno di una traslazione.** Il motore porta il disegno al centro
dell'area, e sulla tavola unica il blocco disegnato comprende il regolatore e il
quadro: tutto il disegno si sposta di qualche passo, senza che cambi una distanza fra
due pezzi. Le coordinate si leggono percio' dall'angolo in alto a sinistra dei
simboli d'acqua, e si arrotondano al decimo di millimetro.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import Domain

SVG = "{http://www.w3.org/2000/svg}"

_NUMERO = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")


@dataclass(frozen=True)
class IlComando:
    """Quello che sulla tavola e' del comando, letto sul grafo intero."""

    colori: frozenset[str]
    """Il colore delle linee del comando."""
    pezzi: frozenset[str]
    """I pezzi che stanno solo sul comando."""
    testi: frozenset[str]
    """Sigle, dati e scritte del comando."""
    porte: dict[str, tuple[tuple[float, float], ...]] = field(default_factory=dict)
    """Per simbolo, dove stanno le sue porte di comando nel corpo non girato."""
    nomi_delle_porte: dict[str, frozenset[str]] = field(default_factory=dict)
    """Per simbolo, i nomi delle sue porte di comando: i gruppi `data-port` del corpo."""


def il_comando_del_grafo(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
    naming: Path | None = None,
) -> IlComando:
    """Che cosa e' del comando nel grafo **intero**: le stesse risposte valgono per la
    tavola unica e per la vista idraulica."""
    from disegnatore_mep.diametri.scritte import tratti_da_scrivere
    from disegnatore_mep.layout.labels import format_value
    from disegnatore_mep.layout.legend import style_for
    from disegnatore_mep.piano.vista import sigle_del_grafo_intero, solo_comando

    del_progetto = catalogo.per_il_progetto(modello)
    reti = {item.id: item for item in modello.networks}
    colori = frozenset(
        style_for(item.medium, verso)[0]
        for item in modello.networks
        if item.domain is Domain.CONTROL
        for verso in (True, False)
    )
    pezzi = solo_comando(modello, del_progetto)
    sigle = sigle_del_grafo_intero(modello, del_progetto, naming) if naming is not None else {}
    testi: set[str] = set()
    for pezzo in modello.components:
        if pezzo.id not in pezzi:
            continue
        for sigla in (pezzo.tag, sigle.get(pezzo.id)):
            if sigla:
                testi.add(sigla)
        for chiave, valore in pezzo.properties.items():
            scritto = format_value(chiave, valore)
            if scritto is not None:
                testi.add(scritto)
    del_comando = {
        item.id
        for item in modello.connections
        if (rete := reti.get(item.network_id)) is not None and rete.domain is Domain.CONTROL
    }
    scritte, _ = tratti_da_scrivere(modello, del_progetto)
    testi.update(item.scritta for item in scritte if set(item.connection_ids) <= del_comando)
    porte: dict[str, tuple[tuple[float, float], ...]] = {}
    nomi: dict[str, frozenset[str]] = {}
    for pezzo in modello.components:
        voce = del_progetto.get(pezzo.definition_id)
        if not simboli.contains(voce.symbol_id):
            continue
        manifesto = simboli.get(voce.symbol_id).manifest
        # Le porte di comando: quelle che la voce dice del comando, e quelle che il
        # simbolo tiene da parte come facoltative (`control_ports`).
        del_comando_qui = {porta.id for porta in voce.ports if porta.domain is Domain.CONTROL}
        del_comando_qui |= manifesto.control_port_ids
        nomi[voce.symbol_id] = nomi.get(voce.symbol_id, frozenset()) | del_comando_qui
        porte[voce.symbol_id] = tuple(
            sorted(
                set(porte.get(voce.symbol_id, ()))
                | {
                    (porta.x_mm, porta.y_mm)
                    for porta in (*manifesto.ports, *manifesto.control_ports)
                    if porta.id in del_comando_qui
                }
            )
        )
    return IlComando(
        colori=colori, pezzi=pezzi, testi=frozenset(testi), porte=porte, nomi_delle_porte=nomi
    )


@dataclass(frozen=True)
class ParteIdraulica:
    """La parte dell'acqua e dell'aria di una tavola, voce per voce, ordinata."""

    tracciati: tuple[str, ...]
    """Le linee, le frecce di verso, gli scavalli e i pallini dei fluidi d'acqua e d'aria."""
    simboli: tuple[str, ...]
    """I simboli dei pezzi d'acqua e d'aria: pezzo, simbolo, posto e corpo."""
    testi: tuple[str, ...]
    """Sigle, dati, etichette e scritte dei tratti, ciascuno col suo posto e i suoi richiami."""

    def differenze(self, altra: ParteIdraulica) -> list[str]:
        """Quello che sta in una sola delle due, voce per voce: vuoto se sono uguali."""
        righe: list[str] = []
        for nome in ("tracciati", "simboli", "testi"):
            mie, sue = getattr(self, nome), getattr(altra, nome)
            for voce in sorted(set(mie) - set(sue)):
                righe.append(f"{nome}, solo nella prima: {voce}")
            for voce in sorted(set(sue) - set(mie)):
                righe.append(f"{nome}, solo nella seconda: {voce}")
            if not righe and sorted(mie) != sorted(sue):
                righe.append(f"{nome}: stesse voci, ripetute un numero diverso di volte")
        return righe


def _numeri(testo: str) -> list[float]:
    return [float(item) for item in _NUMERO.findall(testo)]


def _mm(valore: float) -> str:
    """Al decimo di millimetro; lo zero senza segno."""
    arrotondato = round(valore + 0.0, 1)
    return f"{arrotondato + 0.0:.1f}"


def _traslato_d(d: str, dx: float, dy: float) -> str:
    """Un attributo `d` di un percorso, spostato: M e L a coppie, A con i suoi sette
    numeri (solo gli ultimi due sono un punto)."""
    parti = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?(?:e-?\d+)?", d)
    uscita: list[str] = []
    comando = ""
    numeri: list[float] = []

    def chiudi() -> None:
        if not comando:
            return
        if comando in "ML":
            for indice in range(0, len(numeri), 2):
                uscita.append(f"{comando}{_mm(numeri[indice] - dx)},{_mm(numeri[indice + 1] - dy)}")
        elif comando == "A":
            for indice in range(0, len(numeri), 7):
                gruppo = numeri[indice : indice + 7]
                uscita.append(
                    "A" + ",".join(_mm(item) for item in gruppo[:5])
                    + f",{_mm(gruppo[5] - dx)},{_mm(gruppo[6] - dy)}"
                )
        else:
            uscita.append(comando + ",".join(_mm(item) for item in numeri))

    for parte in parti:
        if parte.isalpha():
            chiudi()
            comando, numeri = parte, []
        else:
            numeri.append(float(parte))
    chiudi()
    return " ".join(uscita)


def _corpo_del_simbolo(
    gruppo: ET.Element, porte: tuple[tuple[float, float], ...], nomi: frozenset[str]
) -> list[str]:
    """Il corpo di un simbolo come elenco di voci, senza i monconi di comando: un
    `line` con un capo su una porta di comando del simbolo, o il gruppo `data-port`
    di una porta di comando."""
    voci: list[str] = []

    def visita(elemento: ET.Element, profondita: int) -> None:
        for figlio in elemento:
            nome = figlio.tag.removeprefix(SVG)
            attributi = dict(figlio.attrib)
            if nome == "g" and attributi.get("data-port") in nomi:
                continue
            if nome == "line":
                capi = (
                    (float(attributi.get("x1", 0)), float(attributi.get("y1", 0))),
                    (float(attributi.get("x2", 0)), float(attributi.get("y2", 0))),
                )
                if any(
                    abs(capo[0] - porta[0]) < 1e-6 and abs(capo[1] - porta[1]) < 1e-6
                    for capo in capi
                    for porta in porte
                ):
                    continue
            voci.append(f"{profondita}:{nome}:{sorted(attributi.items())}")
            visita(figlio, profondita + 1)

    visita(gruppo, 0)
    return voci


def parte_idraulica(svg: str, comando: IlComando) -> ParteIdraulica:
    """La parte idronica e aeraulica della tavola `svg`, a meno della traslazione del
    disegno (le coordinate dall'angolo in alto a sinistra dei simboli d'acqua)."""
    radice = ET.fromstring(svg)
    figli = list(radice)

    simboli_d_acqua = [
        item
        for item in figli
        if item.tag == f"{SVG}g"
        and item.get("class") == "symbol"
        and item.get("data-component-id") not in comando.pezzi
    ]
    origini = [_numeri(item.get("transform", ""))[:2] for item in simboli_d_acqua]
    dx = min((item[0] for item in origini), default=0.0)
    dy = min((item[1] for item in origini), default=0.0)

    def punto(x: str | float, y: str | float) -> str:
        return f"{_mm(float(x) - dx)},{_mm(float(y) - dy)}"

    tracciati: list[str] = []
    simboli: list[str] = []
    testi: list[str] = []
    richiami_in_attesa: list[str] = []
    for elemento in figli:
        nome = elemento.tag.removeprefix(SVG)
        classe = elemento.get("class", "")
        if nome == "g" and classe == "symbol":
            if elemento.get("data-component-id") in comando.pezzi:
                continue
            simbolo_id = elemento.get("data-symbol-id", "")
            x, y = _numeri(elemento.get("transform", ""))[:2]
            corpo = _corpo_del_simbolo(
                elemento,
                comando.porte.get(simbolo_id, ()),
                comando.nomi_delle_porte.get(simbolo_id, frozenset()),
            )
            simboli.append(
                f"{elemento.get('data-component-id')} {simbolo_id} @ {punto(x, y)} | " + " ; ".join(corpo)
            )
            continue
        if classe in ("run",):
            colore = elemento.get("stroke", "")
            if colore in comando.colori:
                continue
            punti = " ".join(
                punto(*coppia.split(",")) for coppia in elemento.get("points", "").split()
            )
            tracciati.append(f"linea {colore} {elemento.get('stroke-dasharray', '-')} {punti}")
            continue
        if classe in ("flow-arrow", "crossing-hop"):
            colore = elemento.get("fill") if classe == "flow-arrow" else elemento.get("stroke")
            if colore in comando.colori:
                continue
            tracciati.append(f"{classe} {colore} {_traslato_d(elemento.get('d', ''), dx, dy)}")
            continue
        if classe == "junction":
            if elemento.get("fill") in comando.colori:
                continue
            tracciati.append(
                f"pallino {elemento.get('fill')} {punto(elemento.get('cx', 0), elemento.get('cy', 0))} "
                f"r{elemento.get('r')}"
            )
            continue
        if classe in ("leader", "diameter-leader"):
            punti = " ".join(punto(*coppia.split(",")) for coppia in elemento.get("points", "").split())
            richiami_in_attesa.append(f"{classe} {punti}")
            continue
        if classe in ("leader-arrow", "diameter-leader-arrow"):
            richiami_in_attesa.append(f"{classe} {_traslato_d(elemento.get('d', ''), dx, dy)}")
            continue
        if nome == "text" and classe in ("label", "diameter"):
            testo = "".join(elemento.itertext())
            richiami, richiami_in_attesa = richiami_in_attesa, []
            if testo in comando.testi:
                continue
            giro = elemento.get("transform", "")
            if giro:
                numeri = _numeri(giro)
                giro = f" rotate({_mm(numeri[0])} {punto(numeri[1], numeri[2])})"
            testi.append(
                f"{classe} {elemento.get('data-role', '')} «{testo}» @ "
                f"{punto(elemento.get('x', 0), elemento.get('y', 0))} corpo {elemento.get('font-size')}{giro}"
                + "".join(f" | {item}" for item in richiami)
            )
            continue
    return ParteIdraulica(
        tracciati=tuple(sorted(tracciati)),
        simboli=tuple(sorted(simboli)),
        testi=tuple(sorted(testi)),
    )


def pezzi_da_togliere(modello: ProjectModel, catalogo: ComponentRegistry) -> frozenset[str]:
    """I pezzi che un piano della vista idraulica non posa: quelli del solo comando."""
    from disegnatore_mep.piano.vista import solo_comando

    return solo_comando(modello, catalogo.per_il_progetto(modello))


def piano_della_vista_idraulica(piano: dict, togliere: Iterable[str]) -> dict:
    """Lo stesso piano, nella vista idraulica: senza i pezzi del solo comando."""
    via = set(togliere)
    return {
        **piano,
        "vista": "idraulica",
        "pezzi": {chiave: valore for chiave, valore in piano["pezzi"].items() if chiave not in via},
    }


__all__ = [
    "IlComando",
    "ParteIdraulica",
    "il_comando_del_grafo",
    "parte_idraulica",
    "pezzi_da_togliere",
    "piano_della_vista_idraulica",
]
