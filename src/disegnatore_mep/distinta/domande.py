"""Le domande della distinta **prima** del primo lancio (REL-016, D4).

Il collaudo indipendente della 1.7.0 ha chiesto la distinta su un canalizzato: al passo 2
la skill aveva fatto le domande del disegno, e la prima distinta e' uscita con dodici voci
DA DEFINIRE — refrigerante, precarica, bocchette, attacco della condensa, protezioni —, e
si e' dovuto rifare il giro di domande al progettista.

`mep.py distinta <grafo-completo.json> --domande` compone la distinta in memoria, non
scrive niente, e dice **in parole** che cosa chiedere: un dato per riga, con i pezzi o i
tratti a cui manca e il campo del grafo dove si scrive la risposta. I dati vengono dai
`Mancante` della distinta, che nascono nello stesso punto delle voci DA DEFINIRE: le
domande non si possono scostare dal documento. Qui c'e' soltanto il modo di dirle.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .calcolo import MARCA_E_MODELLO, PEZZO, REGOLE, TRATTO, Distinta, Mancante


@dataclass(frozen=True)
class DatoInParole:
    """Come si chiede un dato al progettista, e in che campo del grafo va la risposta."""

    domanda: str
    campi: str
    poi: str = ""
    """Una riga in piu', quando serve dire che cosa succede se resta senza risposta."""


DATI: dict[str, DatoInParole] = {
    MARCA_E_MODELLO: DatoInParole(
        "Marca e modello",
        "«marca» e «modello»",
        "se il progettista li lascia aperti di proposito, nel documento restano da definire",
    ),
    "refrigerante": DatoInParole("Il refrigerante della macchina (es. «R32»)", "«refrigerante»"),
    "precarica_fino_a_m": DatoInParole(
        "Dalla scheda della macchina: fino a quanti metri di linea basta la precarica", "«precarica_fino_a_m»"
    ),
    "carica_aggiuntiva_g_m": DatoInParole(
        "Dalla scheda della macchina: la carica aggiuntiva oltre la precarica, in grammi per metro di linea",
        "«carica_aggiuntiva_g_m»",
    ),
    "attacco_condensa": DatoInParole(
        "L'attacco dello scarico della condensa sull'unità (es. «VP20 (Øe 26)»)", "«attacco_condensa»"
    ),
    "dimensione": DatoInParole("La dimensione della bocchetta (es. «400×200»)", "«dimensione»"),
    "locale": DatoInParole(
        "Il locale che la bocchetta serve (es. «Soggiorno»): le griglie di transito si contano per locale",
        "«locale»",
    ),
    "protezione": DatoInParole(
        "La protezione della linea nel quadro, dalla targa della macchina (es. «Magnetotermico-differenziale "
        "1P+N C16, Idn 30 mA, tipo A, 6 kA»)",
        "«protezione»",
    ),
    "sezione": DatoInParole("La sezione: diametro, lati del canale o cavo (es. «Ø200», «3G2,5»)", "«sezione»"),
    "materiale": DatoInParole("Il materiale della tubazione", "«materiale»"),
    "lunghezza_m": DatoInParole(
        "La lunghezza stimata del tratto, in metri (0 se è un raccordo diretto)", "«lunghezza_m»"
    ),
    "portata_m3h": DatoInParole("La portata d'aria, in m³/h", "«portata_m3h»"),
    "lunghezza_max_m": DatoInParole(
        "Dalla scheda della macchina: la lunghezza massima della linea frigorifera, in metri", "«lunghezza_max_m»"
    ),
}
"""Ogni dato che la distinta legge dal grafo, detto in parole. Un dato che non c'e' si dice
col suo nome: lo vede la prova delle regole, che ogni dato dei testi qui abbia le sue parole."""

DOVE = {PEZZO: "sul pezzo", TRATTO: "su una tubazione del tratto"}


def _chi(mancanti: Sequence[Mancante]) -> str:
    """I pezzi o i tratti di un dato, con il loro nome una volta sola: «TA-01, TA-02
    (Bocchetta di mandata)», «T08 (Alimentazione centrale di zona: QE-01 - CZ-01)»."""
    gruppi: list[tuple[str, list[str]]] = []
    for mancante in mancanti:
        if mancante.su == TRATTO:
            gruppi.append((mancante.di, [mancante.chi]))
            continue
        for di, sigle in gruppi:
            if di == mancante.di and mancante.chi not in sigle:
                sigle.append(mancante.chi)
                break
        else:
            gruppi.append((mancante.di, [mancante.chi]))
    return "; ".join(f"{', '.join(s for s in sigle if s)} ({di})" if any(sigle) else di for di, sigle in gruppi)


def _per_dato(mancanti: Iterable[Mancante]) -> list[tuple[str, str, list[Mancante]]]:
    """Per dato e per dove si scrive, nell'ordine di `DATI` e poi in quello d'incontro."""
    gruppi: dict[tuple[str, str], list[Mancante]] = {}
    for mancante in mancanti:
        gruppi.setdefault((mancante.dato, mancante.su), []).append(mancante)
    ordine = {dato: indice for indice, dato in enumerate(DATI)}
    chiavi = sorted(gruppi, key=lambda k: ordine.get(k[0], len(ordine)))
    return [(dato, su, gruppi[(dato, su)]) for dato, su in chiavi]


def _riga(dato: str, su: str, mancanti: Sequence[Mancante]) -> str:
    parole = DATI.get(dato, DatoInParole(f"Il dato «{dato}»", f"«{dato}»"))
    riga = f"{parole.domanda} — {_chi(mancanti)}. Nel grafo: {parole.campi} {DOVE.get(su, '')}".rstrip()
    return f"{riga}; {parole.poi}." if parole.poi else f"{riga}."


def _righe_delle_regole(mancanti: Sequence[Mancante]) -> list[str]:
    """Una riga per fluido o per voce di catalogo, con tutti i suoi tratti o pezzi."""
    gruppi: dict[tuple[str, str], list[str]] = {}
    for mancante in mancanti:
        chi = gruppi.setdefault((mancante.dato, mancante.di), [])
        chi.extend(c for c in mancante.chi.split(", ") if c and c not in chi)
    righe = []
    for (dato, di), chi in gruppi.items():
        quali = f" ({', '.join(chi)})" if chi else ""
        if dato == "fluido":
            righe.append(f"Il fluido «{di}»{quali} non ha regole nella distinta.")
        elif dato == "corredo":
            righe.append(f"«{di}»{quali} non ha il corredo di posa nelle regole della distinta.")
        else:
            righe.append(f"«{di}»: manca il dato «{dato}» nelle regole della distinta.")
    return righe


def domande_in_parole(distinta: Distinta) -> tuple[list[str], int]:
    """Le righe che `--domande` stampa, e quante domande evitano voci DA DEFINIRE."""
    per_le_voci = [m for m in distinta.mancanti if m.su != REGOLE]
    delle_regole = [m for m in distinta.mancanti if m.su == REGOLE]
    gia = set(per_le_voci)
    per_la_verifica = []
    for mancante in distinta.mancanti_della_verifica:
        if mancante not in gia and mancante not in per_la_verifica:
            per_la_verifica.append(mancante)
    righe: list[str] = []
    domande = _per_dato(per_le_voci)
    if domande:
        righe.append(
            f"Le domande della distinta — {len(domande)}, da fare al progettista nello stesso giro di quelle del "
            "disegno (senza risposta, le voci escono DA DEFINIRE):"
        )
        righe.extend(f"  {n}. {_riga(*d)}" for n, d in enumerate(domande, start=1))
    else:
        righe.append("Le domande della distinta: nessuna, i dati per le voci ci sono tutti.")
    verifica = _per_dato(per_la_verifica)
    if verifica:
        righe.append("Per la verifica (senza, la verifica non si fa; non fanno voci DA DEFINIRE):")
        righe.extend(f"  - {_riga(*d)}" for d in verifica)
    if delle_regole:
        righe.append(
            "Senza regole nella distinta (escono nella sezione X, DA DEFINIRE: una risposta del progettista "
            "non basta, dillo):"
        )
        righe.extend(f"  - {riga}" for riga in _righe_delle_regole(delle_regole))
    if distinta.da_confermare:
        righe.append("Da confermare nello stesso giro (poi --fornitura confermata, o le scelte sue):")
        righe.extend(f"  - {riga}" for riga in distinta.da_confermare)
    return righe, len(domande) + len(_righe_delle_regole(delle_regole))
