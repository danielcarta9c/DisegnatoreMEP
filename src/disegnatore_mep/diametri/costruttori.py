"""Quello che il manuale del costruttore chiede, per le macchine che Nove C usa (REL-011).

Il PO: «Le regole del manuale Shenling sicuramente comandano (almeno nelle piccole centrali
domestiche dove di fatto installiamo sempre Shenling … serve per la garanzia)» (I-243). Qui
stanno i **numeri** del manuale che la skill controlla — non le regole degli accessori, che
stanno in `rules/hydronic/`:

- **l'attacco** della macchina, in pollici: dove il tubo scelto dalla velocita' e' piu'
  piccolo, all'attacco c'e' una riduzione (`riduzioni_all_attacco`, I-281);
- **il campo della portata** d'acqua del modello (D-223);
- **il tampone minimo** per unita' (D-226);
- **la prevalenza indicativa** della pompa a bordo, quando il progettista non la da'
  (I-281).

**L'attacco non e' piu' un minimo del tubo** (I-281, che supera D-223 punto 1). Fino a
REL-017 il tratto fra la macchina e il collettore non scendeva sotto l'attacco: 1" per le
ThermaX 6–9 kW, 1¼" per le 12–15 kW. Due commesse realizzate in multistrato 32×3, con
gli accessori da 1", su macchine da 15 e da 12 kW funzionano, e il PO: «decidiamo con la
velocità. Tendenzialmente pero' sulla 12 mettiamo il 32 (a meno che non ci sia troppa
distanza) mentre sulla 15 mettiamo il 40». La velocita' da' proprio questo — 12 kW con
5 K: MS 32×3 a 1,08 m/s; 15 kW: 1,35 m/s nel 32×3, oltre 1,3, quindi MS 40×3,5 —, e la
«troppa distanza» la decide la verifica della prevalenza (`perdite`).

La macchina si riconosce dalla marca («Shenling») e dalla potenza nominale che il
progettista scrive (6, 9, 12, 15 kW, la serie ThermaX R290): il catalogo e' generico e non
sa il modello. Fonte: Manuale d'installazione e d'uso ThermaX R290 6-15 kW (OneDrive del PO,
non nel repository), letto il 3 e 4 novembre 2026: attacchi nella tabella delle specifiche
tecniche, portata nel campo di funzionamento, tampone al par. 4.4.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import MARCA, ComponentInstance, ProjectModel

from .calcolatore import portata_da_potenza
from .tubi import Tubo, ordine_del_pollice


@dataclass(frozen=True)
class DatiDelModello:
    """I numeri del manuale per una taglia."""

    attacco: str
    """L'attacco d'acqua della macchina, in pollici: «1"», «1¼"»."""
    portata_minima_m3h: float
    portata_massima_m3h: float
    tampone_minimo_l: float
    prevalenza_indicativa_m: float = 8.0
    """La prevalenza della pompa a bordo con cui si verifica il giro quando il
    progettista non da' la sua (`perdite`, I-281). Il PO: «dovrebbe stare sui 8/9 metri»;
    si prende il valore basso. **E' indicativa**: probabilmente e' piu' vicina alla
    prevalenza massima della pompa (a portata nulla) che a quella utile alla portata di
    progetto, che e' minore; il valore vero e' la curva del manuale alla portata, che la
    skill non ha letto (D-223)."""


SHENLING_THERMAX_R290: dict[float, DatiDelModello] = {
    6.0: DatiDelModello('1"', 0.50, 1.25, 25.0),
    9.0: DatiDelModello('1"', 0.50, 2.10, 25.0),
    12.0: DatiDelModello('1¼"', 0.90, 2.50, 40.0),
    15.0: DatiDelModello('1¼"', 0.90, 3.00, 40.0),
}
"""ThermaX R290 6-15 kW: attacchi R1" (6, 9 kW) e R1-1/4" (12, 15 kW); portata d'acqua
6 kW 0,50-1,25, 9 kW 0,50-2,10, 12 kW 0,90-2,50, 15 kW 0,90-3,00 m³/h; tampone almeno 25 l
(6-9 kW) e 40 l (12-15 kW), 40 l per unita' in cascata (D-226: i minimi Shenling, che il
progettista puo' variare)."""


def dati_del_modello(pezzo: ComponentInstance) -> DatiDelModello | None:
    """I numeri del manuale per questa macchina, se e' una Shenling di una taglia nota."""
    if "shenling" not in str(pezzo.properties.get(MARCA, "")).lower():
        return None
    potenza = pezzo.properties.get("power_kw")
    if not isinstance(potenza, int | float) or isinstance(potenza, bool):
        return None
    return SHENLING_THERMAX_R290.get(float(potenza))


def avvisi_del_costruttore(project: ProjectModel, catalog: ComponentRegistry) -> list[str]:
    """Quello che il manuale chiede e il grafo non rispetta, in parole (D-223, D-226).

    Segnala e non corregge: la portata fuori campo e il volano sotto il minimo sono
    scelte del progettista, che la skill gli fa vedere."""
    avvisi: list[str] = []
    pezzi = {p.id: p for p in project.components}

    def funzioni(pezzo: ComponentInstance) -> set[str]:
        return set(catalog.get(pezzo.definition_id).functions) if catalog.contains(pezzo.definition_id) else set()

    macchine = [(p, d) for p in project.components if (d := dati_del_modello(p)) and "heat_generation" in funzioni(p)]
    for pezzo, dati in macchine:
        salto = pezzo.properties.get("delta_t_k")
        potenza = pezzo.properties.get("power_kw")
        if isinstance(salto, int | float) and isinstance(potenza, int | float) and salto > 0:
            portata = portata_da_potenza(float(potenza), float(salto))
            if not dati.portata_minima_m3h <= portata <= dati.portata_massima_m3h:
                avvisi.append(
                    f"{pezzo.tag or pezzo.id}: con {potenza:g} kW e un salto di {salto:g} K la portata e' "
                    f"{_n(portata)} m³/h, fuori dal campo del manuale Shenling "
                    f"({_n(dati.portata_minima_m3h)}–{_n(dati.portata_massima_m3h)} m³/h): la macchina va in errore "
                    "di flusso (E1/E0). Il salto termico va rivisto."
                )
    # Lo schema in serie, per ogni pompa di calore aria-acqua (specifica Nove C, par. 1.7).
    reti_acqua = {n.id for n in project.networks if n.medium == "heating_water"}
    pompe = [p for p in project.components if p.definition_id.startswith("heat-pump-air-water")]
    giro: dict[str, set[str]] = {}
    for c in project.connections:
        if c.network_id in reti_acqua:
            a, b = c.endpoint_a.component_id, c.endpoint_b.component_id
            giro.setdefault(a, set()).add(b)
            giro.setdefault(b, set()).add(a)
    gia: set[str] = set()
    for pompa in pompe:
        if pompa.id in gia:
            continue
        circuito, da_fare = {pompa.id}, [pompa.id]
        while da_fare:
            for vicino in giro.get(da_fare.pop(), ()):
                if vicino not in circuito:
                    circuito.add(vicino)
                    da_fare.append(vicino)
        gia |= circuito
        serbatoi = [pezzi[i] for i in circuito if i in pezzi and "thermal_storage" in funzioni(pezzi[i])]
        if serbatoi and all(_in_serie(s) for s in serbatoi):
            nomi = ", ".join(p.tag or p.id for p in pompe if p.id in circuito)
            avvisi.append(
                f"il circuito di {nomi} ha solo un volano a due attacchi, in serie: la specifica Nove C (par. "
                "1.7) ammette solo lo schema a 4 tubi, con il volano a 4 attacchi che separa le macchine "
                "dall'impianto. Va chiesto al progettista (D-226)."
            )
    if not macchine:
        return avvisi
    # Il tampone: i volani e gli accumuli d'acqua di riscaldamento raggiunti dalle macchine
    # senza uscire dall'acqua di riscaldamento.
    reti = {n.id for n in project.networks if n.medium == "heating_water"}
    vicini: dict[str, set[str]] = {}
    for c in project.connections:
        if c.network_id in reti:
            a, b = c.endpoint_a.component_id, c.endpoint_b.component_id
            vicini.setdefault(a, set()).add(b)
            vicini.setdefault(b, set()).add(a)
    visti: set[str] = set()
    for pezzo, _ in macchine:
        if pezzo.id in visti:
            continue
        circuito, da_fare = {pezzo.id}, [pezzo.id]
        while da_fare:
            for vicino in vicini.get(da_fare.pop(), ()):
                if vicino not in circuito:
                    circuito.add(vicino)
                    da_fare.append(vicino)
        visti |= circuito
        sue = [(p, d) for p, d in macchine if p.id in circuito]
        minimo = sum(d.tampone_minimo_l for _, d in sue)
        serbatoi = [pezzi[i] for i in circuito if i in pezzi and "thermal_storage" in funzioni(pezzi[i])]
        volumi = _volumi(serbatoi)
        if serbatoi and volumi is not None and volumi < minimo:
            avvisi.append(
                f"il volano del circuito di {', '.join(p.tag or p.id for p, _ in sue)} tiene {volumi:g} l: il manuale "
                f"Shenling ne chiede almeno {minimo:g} ({len(sue)} unita'). Se il progettista lo vuole cosi', lo "
                "conferma; altrimenti va un volano piu' grande."
            )
    return avvisi


def _in_serie(serbatoio: ComponentInstance) -> bool:
    """Un volano a due attacchi: sta in serie sul circuito, non separa (D-226)."""
    return serbatoio.definition_id.startswith("buffer-two-port")


def _n(valore: float) -> str:
    return f"{valore:.2f}".replace(".", ",")


def _volumi(serbatoi: Iterable[ComponentInstance]) -> float | None:
    totale = 0.0
    for serbatoio in serbatoi:
        volume = serbatoio.properties.get("volume_l")
        if not isinstance(volume, int | float) or isinstance(volume, bool):
            return None
        totale += float(volume)
    return totale


@dataclass(frozen=True)
class RiduzioneAllAttacco:
    """Un attacco della macchina piu' grande del tubo che ci arriva (I-281)."""

    macchina: str
    """L'id del pezzo."""
    porta: str
    attacco: str
    """L'attacco della macchina in pollici: «1¼"»."""
    tubo: Tubo
    """Il tubo che ci arriva: il pollice dei suoi raccordi e' piu' piccolo."""

    @property
    def in_parole(self) -> str:
        tubo = self.tubo.scritta if self.tubo.materiale == "acciaio" else f"{self.tubo.scritta} ({self.tubo.pollici})"
        return f"attacco {self.attacco}, tubo {tubo}: riduzione all'attacco"


def riduzioni_all_attacco(project: ProjectModel, catalog: ComponentRegistry) -> list[RiduzioneAllAttacco]:
    """Gli attacchi d'acqua delle macchine dove il tubo che ci arriva ha il pollice piu'
    piccolo dell'attacco: li' va una riduzione (I-281). **Una funzione sola**, che
    `riduzioni.posa_le_riduzioni` legge per posare il pezzo della riduzione (D-233).

    Il tubo e' quello che la tavola scrive (`tratti.tubi_delle_tubazioni`): del
    progettista, o del calcolo. Senza un tubo noto sull'attacco, niente."""
    from .tratti import tubi_delle_tubazioni

    pezzi = {p.id: p for p in project.components}
    macchine = {pid: dati for pid, p in pezzi.items() if (dati := dati_del_modello(p)) is not None}
    if not macchine:
        return []
    tubi = tubi_delle_tubazioni(project, catalog)
    riduzioni: list[RiduzioneAllAttacco] = []
    for tubazione in project.connections:
        tubo = tubi.get(tubazione.id)
        if tubo is None:
            continue
        for capo in (tubazione.endpoint_a, tubazione.endpoint_b):
            dati = macchine.get(capo.component_id)
            if dati is None or ordine_del_pollice(tubo.pollici) >= ordine_del_pollice(dati.attacco):
                continue
            riduzioni.append(RiduzioneAllAttacco(capo.component_id, capo.port_id, dati.attacco, tubo))
    return sorted(riduzioni, key=lambda item: (item.macchina, item.porta))
