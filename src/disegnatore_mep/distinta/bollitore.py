"""Il bollitore e la pompa di calore: la superficie del serpentino (REL-028, I-315, I-321, I-323).

Il PO: «il problema non è tanto il volume di accumulo ma la superficie di scambio … un
bollitore non si categorizza solo per volume ma deve essere a serpentino maggiorato per PDC»;
e, sulle offerte di PR.MI.059: «se mi quoti un bollitore con 0.8 mq di serpentino ovvio che
costa meno ma la pdc non funziona».

Per ogni bollitore che una pompa di calore scalda (raggiunto dalla sua acqua di
riscaldamento), qui si dice:

- **la superficie minima** del serpentino: dal manuale del costruttore per le Shenling
  ThermaX R290 (`diametri.costruttori`, §2.3 del manuale), con la serpentina smaltata se il
  grafo non dice inox (`serpentino`: «inox»); oppure quella che il progettista scrive sul
  bollitore (`superficie_minima_scambio_m2`); se no, **una domanda**: per una pompa di calore
  che non e' una Shenling il minimo non si inventa;
- **la superficie del bollitore scelto** (`superficie_scambio_m2`), se il progettista la da':
  sotto il minimo e' un avviso;
- **la lunghezza del tubo** fra l'unita' esterna e il bollitore, se le tubazioni del percorso
  la dicono tutte: oltre i 5 m del manuale Shenling e' un avviso.

La superficie minima va nella voce della lista materiali che va al fornitore, perche' non
possa quotare un bollitore col serpentino piccolo; e nel costo, dove un bollitore del listino
sotto il minimo e' uno scostamento (⚠).
"""

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass

from disegnatore_mep.diametri.costruttori import (
    SHENLING_DISTANZA_MASSIMA_BOLLITORE_M,
    bollitore_shenling,
)

from .grafo import Impianto, Pezzo, Tubazione, numero

BOLLITORI = frozenset({"dhw-cylinder", "dhw-cylinder-twin-coil"})
"""Le voci di catalogo dei bollitori a serpentino."""

ACQUA_DI_RISCALDAMENTO = "heating_water"

SUPERFICIE = "superficie_scambio_m2"
SUPERFICIE_MINIMA = "superficie_minima_scambio_m2"
SERPENTINO = "serpentino"
LUNGHEZZE = ("lunghezza_m", "lunghezza_dalla_pianta_m")


def _e_una_pompa_di_calore(pezzo: Pezzo) -> bool:
    return pezzo.voce.startswith("heat-pump")


@dataclass(frozen=True)
class SerpentinoDelBollitore:
    bollitore: Pezzo
    pompa: Pezzo | None
    """La pompa di calore che lo scalda (la prima, se sono piu': quella col minimo piu' alto)."""
    minima_m2: float | None
    """La superficie minima del serpentino; `None`: non si sa, e c'e' la domanda."""
    perche: str
    """Da dove viene il minimo, in parole."""
    superficie_m2: float | None
    """La superficie del bollitore scelto, se il progettista la da'."""
    distanza_m: float | None
    """I metri di tubo fra la pompa di calore e il bollitore, se le tubazioni li dicono tutti."""
    distanza_massima_m: float | None

    @property
    def domanda(self) -> str:
        if self.minima_m2 is not None or self.pompa is None:
            return ""
        return (
            f"{self.bollitore.sigla}: superficie minima del serpentino per la pompa di calore {self.pompa.sigla} "
            "(dal manuale della pompa di calore: la skill la sa solo per le Shenling ThermaX R290); si scrive sul "
            f"bollitore in «{SUPERFICIE_MINIMA}»."
        )

    @property
    def avvisi(self) -> list[str]:
        avvisi: list[str] = []
        if self.minima_m2 is not None and self.superficie_m2 is not None and self.superficie_m2 < self.minima_m2:
            avvisi.append(
                f"{self.bollitore.sigla}: serpentino {_m2(self.superficie_m2)}, sotto il minimo di {_m2(self.minima_m2)} "
                f"({self.perche}): con la pompa di calore non scambia abbastanza."
            )
        if self.distanza_m is not None and self.distanza_massima_m is not None and self.distanza_m >= self.distanza_massima_m:
            avvisi.append(
                f"{self.bollitore.sigla}: {_metri(self.distanza_m)} di tubo dalla pompa di calore "
                f"{self.pompa.sigla if self.pompa else ''}, il manuale Shenling (§2.3, punto 6) li vuole sotto i "
                f"{_metri(self.distanza_massima_m)}."
            )
        return avvisi

    def prescrizione(self) -> str:
        """Come si scrive nella voce della lista: «a serpentino maggiorato per pompa di calore,
        superficie di scambio non minore di 2,5 m²»."""
        if self.pompa is None:
            return ""
        minimo = _m2(self.minima_m2) if self.minima_m2 is not None else "DA DEFINIRE m²"
        return f"a serpentino maggiorato per pompa di calore, superficie di scambio non minore di {minimo}"


def _m2(valore: float) -> str:
    return f"{valore:g}".replace(".", ",") + " m²"


def _metri(valore: float) -> str:
    return f"{valore:g}".replace(".", ",") + " m"


def _lunghezza(tubazione: Tubazione) -> float | None:
    for campo in LUNGHEZZE:
        valore = numero(tubazione.dati.get(campo))
        if valore is not None:
            return valore
    return None


def _percorso(impianto: Impianto, da: str, a: str) -> list[Tubazione] | None:
    """Le tubazioni d'acqua di riscaldamento dal pezzo `da` al pezzo `a`, col minor numero di
    tubazioni; `None` se non si raggiungono."""
    vicini: dict[str, list[tuple[str, Tubazione]]] = {}
    for tubazione in impianto.tubazioni:
        if tubazione.fluido != ACQUA_DI_RISCALDAMENTO:
            continue
        vicini.setdefault(tubazione.capo_a, []).append((tubazione.capo_b, tubazione))
        vicini.setdefault(tubazione.capo_b, []).append((tubazione.capo_a, tubazione))
    venuto: dict[str, tuple[str, Tubazione] | None] = {da: None}
    coda = deque([da])
    while coda:
        qui = coda.popleft()
        if qui == a:
            break
        for la, tubazione in vicini.get(qui, []):
            if la not in venuto:
                venuto[la] = (qui, tubazione)
                coda.append(la)
    if a not in venuto:
        return None
    percorso: list[Tubazione] = []
    qui = a
    while (passo := venuto[qui]) is not None:
        qui, tubazione = passo
        percorso.append(tubazione)
    return list(reversed(percorso))


def _minimo(pompa: Pezzo, bollitore: Pezzo) -> tuple[float | None, str, float | None]:
    dato = numero(bollitore.proprieta.get(SUPERFICIE_MINIMA))
    if dato is not None:
        return dato, f"il minimo scritto sul bollitore {bollitore.sigla}", None
    modello = bollitore_shenling(pompa.proprieta.get("marca"), numero(pompa.proprieta.get("power_kw")))
    if modello is None:
        return None, "", None
    inox = "inox" in str(bollitore.proprieta.get(SERPENTINO) or "").lower()
    potenza = f"{numero(pompa.proprieta.get('power_kw')) or 0:g}".replace(".", ",")
    if inox:
        return modello.superficie_inox_m2, f"Shenling {potenza} kW, serpentina inox, manuale §2.3", (
            SHENLING_DISTANZA_MASSIMA_BOLLITORE_M
        )
    return modello.superficie_smaltata_m2, f"Shenling {potenza} kW, serpentina smaltata, manuale §2.3", (
        SHENLING_DISTANZA_MASSIMA_BOLLITORE_M
    )


def serpentini(impianto: Impianto) -> dict[str, SerpentinoDelBollitore]:
    """Per id di bollitore, il serpentino che serve: solo i bollitori che una pompa di calore
    raggiunge con la sua acqua di riscaldamento."""
    pompe = [p for p in impianto.pezzi.values() if _e_una_pompa_di_calore(p)]
    esito: dict[str, SerpentinoDelBollitore] = {}
    for bollitore in impianto.pezzi.values():
        if bollitore.voce not in BOLLITORI:
            continue
        candidati: list[tuple[float, Pezzo, str, float | None, list[Tubazione]]] = []
        senza_minimo: list[tuple[Pezzo, list[Tubazione]]] = []
        for pompa in pompe:
            percorso = _percorso(impianto, pompa.id, bollitore.id)
            if percorso is None:
                continue
            minima, perche, massima = _minimo(pompa, bollitore)
            if minima is None:
                senza_minimo.append((pompa, percorso))
            else:
                candidati.append((minima, pompa, perche, massima, percorso))
        if senza_minimo:
            pompa, percorso = senza_minimo[0]
            minima_o_niente: float | None = None
            perche, massima = "", None
        elif candidati:
            minima_o_niente, pompa, perche, massima, percorso = max(candidati, key=lambda c: c[0])
        else:
            continue
        lunghezze = [_lunghezza(t) for t in percorso]
        distanza = sum(x for x in lunghezze if x is not None) if lunghezze and None not in lunghezze else None
        esito[bollitore.id] = SerpentinoDelBollitore(
            bollitore=bollitore,
            pompa=pompa,
            minima_m2=minima_o_niente,
            perche=perche,
            superficie_m2=numero(bollitore.proprieta.get(SUPERFICIE)),
            distanza_m=distanza,
            distanza_massima_m=massima,
        )
    return esito


def minima_per_voce(serpentini_: Mapping[str, SerpentinoDelBollitore], ids: list[str]) -> float | None:
    """Il minimo piu' alto fra i bollitori `ids` di una stessa voce della distinta."""
    minimi = [s.minima_m2 for i in ids if (s := serpentini_.get(i)) is not None and s.minima_m2 is not None]
    return max(minimi) if minimi else None
