"""L'ordine strutturale dei pezzi: uno spareggio che non e' un nome.

D-093 lo dice da sempre: **due impianti uguali con nomi diversi devono dare la
stessa tavola**. La posa aveva pero' un solo spareggio a disposizione — la
posizione nel file — e quella posizione sopravvive soltanto finche' il modello
resta in memoria: il JSON canonico riordina i pezzi per identificativo, e la
catena della CLI disegna proprio quel file. Da li' in poi rinominare un pezzo
cambiava la tavola.

Lo stesso vale per il **completamento**: il motore delle regole serve i pezzi di
una rete in un ordine, e chi viene per primo prende l'organo che due attacchi
affacciati sullo stesso tratto si dividono. Per anni quell'ordine e' stato
l'ordine alfabetico — che i nomi decidono — oppure l'ordine del file, che una
permutazione cambia.

Questo modulo sostituisce quello spareggio con uno che si legge **dalla forma
dell'impianto**: due pezzi si distinguono per la voce di catalogo che li
descrive e per come sono attaccati al resto, mai per come si chiamano.

Il conto e' il raffinamento dei colori, fatto sul grafo dei componenti:

1. all'inizio ogni pezzo porta il colore della propria voce di catalogo;
2. a ogni passata il colore diventa «il mio colore, piu' l'elenco ordinato di
   *(mio attacco, colore del vicino, suo attacco)*»;
3. si ripete finche' la partizione non cambia piu'.

Due pezzi che restano dello stesso colore sono **strutturalmente
indistinguibili**: nessun dato dell'impianto li separa, e allora — e soltanto
allora — l'identificativo puo' spareggiare, come DRAW-006-R1 §A.2 ammette.
"""

from collections import defaultdict

from .project import ProjectModel

__all__ = ["structural_order"]


def structural_order(project: ProjectModel) -> dict[str, int]:
    """La posizione di ogni componente in un ordine che i nomi non decidono.

    Restituisce un rango denso, `0` per il primo. I pezzi che il modello
    dichiara ma che nessuna tubazione tocca entrano ugualmente: hanno il colore
    della propria voce e nessun vicino.
    """
    colour: dict[str, str] = {
        item.id: item.definition_id for item in project.components
    }
    links: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for connection in project.connections:
        for mine, other in (
            (connection.endpoint_a, connection.endpoint_b),
            (connection.endpoint_b, connection.endpoint_a),
        ):
            if mine.component_id not in colour or other.component_id not in colour:
                continue
            links[mine.component_id].append(
                (mine.port_id, other.component_id, other.port_id)
            )

    def refined() -> dict[str, str]:
        """Una passata: il colore nuovo di ciascuno, gia' rinumerato.

        La rinumerazione tiene i colori corti — senza, il colore raddoppierebbe
        di lunghezza a ogni passata — e la si fa in ordine di **colore**, non di
        identificativo: e' il colore che deve decidere il numero.
        """
        described = {
            component_id: (
                colour[component_id],
                tuple(
                    sorted(
                        (my_port, colour[peer], peer_port)
                        for my_port, peer, peer_port in links[component_id]
                    )
                ),
            )
            for component_id in colour
        }
        fresh = {
            description: f"{index:06d}"
            for index, description in enumerate(sorted(set(described.values())))
        }
        return {
            component_id: fresh[description]
            for component_id, description in described.items()
        }

    for _ in range(len(colour)):
        fresh = refined()
        if _partition(fresh) == _partition(colour):
            break
        colour = fresh

    return {
        component_id: index
        for index, component_id in enumerate(
            sorted(colour, key=lambda item: (colour[item], item))
        )
    }


def _partition(colour: dict[str, str]) -> frozenset[frozenset[str]]:
    """Chi sta insieme a chi. E' la sola cosa che deve smettere di cambiare:
    i numeri dei colori cambiano a ogni passata, i gruppi no."""
    groups: dict[str, set[str]] = defaultdict(set)
    for component_id, value in colour.items():
        groups[value].add(component_id)
    return frozenset(frozenset(item) for item in groups.values())
