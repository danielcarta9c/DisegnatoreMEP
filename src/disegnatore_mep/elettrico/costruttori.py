"""La linea della pompa di calore secondo il manuale Shenling e la specifica Nove C (REL-018,
I-278).

Le fonti stanno sul OneDrive del PO, non nel repository, e si citano con la pagina:

- **Manuale d'installazione e d'uso ThermaX R290 6-15 kW, §7.4 p. 55**: la corrente massima
  e il cablaggio per taglia — 6 kW 16 A e 4 mm²; 9 kW 20,5 A e 4 mm²; 12 e 15 kW monofase
  30 A e 6 mm²; 12 e 15 kW trifase 14 A e 2,5 mm². **Pp. 5 e 51**: l'alimentazione dedicata,
  il sezionamento onnipolare, il differenziale da 30 mA ad alta velocita' compatibile con
  l'inverter.
- **Specifica tecnica di installazione PdC Shenling Nove C Rev. 01, §3.2–3.4**: nel quadro un
  magnetotermico differenziale bipolare, curva C, Idn 30 mA, tipo B, ad alta velocita', con la
  sua targhetta; il sezionatore locale **non** e' la regola (§3.2); la tabella del §3.3 — 9 kW
  C25/B25 e 3G4; 12 kW C25/B25 e 3G4; 15 kW C32/B40 e 3G6 —, con la regola: **se la targa o
  il manuale chiedono valori maggiori, vale il maggiore**.

**Vale il maggiore** (§3.3): il 12 kW monofase, che la specifica protegge C25 con un 3G4, ne
assorbe 30 secondo il manuale e vuole 6 mm²: va a **C32 e 3G6**, come il 15 kW (assunzione
detta al PO in REL-018 e non corretta). **Il 6 kW non e' nella specifica**: i suoi valori sono
**proposti dal manuale** — 16 A e 4 mm², quindi C16 e 3G4 —, e cosi' le taglie trifase — 14 A
e 2,5 mm², quindi 4P C16 e 5G2,5 —, che si usano solo se il progettista scrive
un'alimentazione a 400 V. Senza alimentazione dichiarata la macchina e' **monofase**, ed e'
un'assunzione che `completa` dice.

Che cosa ne fa la skill (`completa`):

1. **sulla macchina** Shenling senza `alimentazione`, `corrente_max_a` o `cavo_minimo`
   scrive i valori del manuale, e la tabella della tavola dell'elettrico porta «230 V 1~ ·
   30 A · 3G6»;
2. **sull'interruttore** della linea che alimenta una Shenling scrive i dati che mancano —
   poli, curva, In, Idn, tipo, alta velocita' —;
3. **avvisa** — non corregge — quando l'In dichiarata sta sotto la corrente massima della
   macchina, quando la sezione del cavo dichiarata sulla linea sta sotto quella del manuale,
   e quando la linea dal quadro alla macchina non ha l'interruttore.

**Un dato del progettista non si sovrascrive mai**: si scrive solo dove manca, e si dice
quello che si e' scritto.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import MARCA, ComponentInstance, ProjectModel
from disegnatore_mep.model.types import JsonPrimitive

from .protezione import (
    ALTA_VELOCITA,
    CURVA,
    FUNZIONE_DI_PROTEZIONE,
    IDN_MA,
    IN_A,
    POLI,
    TIPO_DIFFERENZIALE,
    sezione_in_mm2,
)

ALIMENTAZIONE = "alimentazione"
CORRENTE_MAX_A = "corrente_max_a"
CAVO_MINIMO = "cavo_minimo"

MONOFASE = "230 V 1~"
"""L'alimentazione che `completa` scrive quando il progettista non la da': la ThermaX
R290 e' monofase in tutte le taglie, e trifase solo a 12 e 15 kW."""


@dataclass(frozen=True)
class LineaDelManuale:
    """La linea di una taglia: quello che la macchina chiede e la protezione proposta."""

    alimentazione: str
    corrente_max_a: float
    """La corrente massima del manuale (§7.4 p. 55), in A."""
    sezione_mm2: float
    """La sezione del cablaggio del manuale (§7.4 p. 55), in mm²."""
    cavo_minimo: str
    """Il cavo come si scrive sulla tavola: «3G6»."""
    poli: str
    curva: str
    in_a: float
    idn_ma: float
    tipo_differenziale: str
    alta_velocita: bool
    fonte: str
    """Da dove viene la protezione: la tabella della specifica, «vale il maggiore», o il
    manuale per le taglie che la specifica non ha."""

    def dati_della_macchina(self) -> dict[str, JsonPrimitive]:
        return {ALIMENTAZIONE: self.alimentazione, CORRENTE_MAX_A: self.corrente_max_a, CAVO_MINIMO: self.cavo_minimo}

    def dati_della_protezione(self) -> dict[str, JsonPrimitive]:
        return {
            POLI: self.poli,
            CURVA: self.curva,
            IN_A: self.in_a,
            IDN_MA: self.idn_ma,
            TIPO_DIFFERENZIALE: self.tipo_differenziale,
            ALTA_VELOCITA: self.alta_velocita,
        }


def _monofase(corrente: float, sezione: float, cavo: str, in_a: float, fonte: str) -> LineaDelManuale:
    return LineaDelManuale(MONOFASE, corrente, sezione, cavo, "2P", "C", in_a, 30, "B", True, fonte)


def _trifase(fonte: str) -> LineaDelManuale:
    return LineaDelManuale("400 V 3N~", 14, 2.5, "5G2,5", "4P", "C", 16, 30, "B", True, fonte)


SHENLING_THERMAX_R290_LINEA: dict[tuple[float, int], LineaDelManuale] = {
    (6.0, 1): _monofase(16, 4, "3G4", 16, "proposta dal manuale (§7.4 p. 55): la specifica non ha il 6 kW"),
    (9.0, 1): _monofase(20.5, 4, "3G4", 25, "specifica §3.3 (C25/B25, 3G4)"),
    (12.0, 1): _monofase(
        30, 6, "3G6", 32, "specifica §3.3 (C25/B25, 3G4) col manuale (30 A, 6 mm²): vale il maggiore"
    ),
    (15.0, 1): _monofase(30, 6, "3G6", 32, "specifica §3.3 (C32/B40, 3G6)"),
    (12.0, 3): _trifase("proposta dal manuale (§7.4 p. 55, 14 A, 2,5 mm²): la specifica non ha il trifase"),
    (15.0, 3): _trifase("proposta dal manuale (§7.4 p. 55, 14 A, 2,5 mm²): la specifica non ha il trifase"),
}
"""**La tabella sola dei dati elettrici Shenling ThermaX R290**, per (potenza nominale in
kW, fasi). La corrente massima e la sezione sono quelle del manuale (§7.4 p. 55); la
protezione e' il magnetotermico differenziale della specifica Nove C (§3.2–3.4: bipolare,
curva C, Idn 30 mA, tipo B, ad alta velocita'), con la taglia della tabella §3.3 e la
regola «vale il maggiore»: il 12 kW sale da C25 e 3G4 a **C32 e 3G6**. Il 6 kW e le taglie
trifase non sono nella specifica, e sono **proposte dal manuale**: la protezione e' la
prima taglia commerciale non sotto la corrente massima (C16 per 16 A e per 14 A), quattro
poli sul trifase."""


def _e_shenling(pezzo: ComponentInstance) -> bool:
    return "shenling" in str(pezzo.properties.get(MARCA, "")).lower()


def _trifase_dichiarata(pezzo: ComponentInstance) -> bool:
    return "400" in str(pezzo.properties.get(ALIMENTAZIONE, ""))


def linea_del_manuale(pezzo: ComponentInstance) -> tuple[LineaDelManuale | None, bool]:
    """La linea del manuale per questa macchina, e se la monofase e' un'assunzione.

    `None` se non e' una Shenling di una taglia nota, o se e' dichiarata trifase in una
    taglia che il manuale non ha trifase (6 e 9 kW)."""
    if not _e_shenling(pezzo):
        return None, False
    potenza = pezzo.properties.get("power_kw")
    if not isinstance(potenza, int | float) or isinstance(potenza, bool):
        return None, False
    fasi = 3 if _trifase_dichiarata(pezzo) else 1
    assunta = ALIMENTAZIONE not in pezzo.properties
    return SHENLING_THERMAX_R290_LINEA.get((float(potenza), fasi)), assunta


# --- la linea, dal quadro alla macchina -----------------------------------------------------


@dataclass(frozen=True)
class LineaDellaMacchina:
    """La linea che alimenta una macchina: i pezzi passanti, le tubazioni, e chi la origina."""

    macchina: str
    passanti: tuple[str, ...]
    """I pezzi in mezzo, dalla macchina verso il quadro."""
    tubazioni: tuple[str, ...]
    origine: str | None
    """Il pezzo da cui la linea parte (il quadro), o `None` se la linea non arriva a nessuno."""


def _funzioni(catalog: ComponentRegistry, pezzo: ComponentInstance) -> set[str]:
    return set(catalog.get(pezzo.definition_id).functions) if catalog.contains(pezzo.definition_id) else set()


def linea_della_macchina(project: ProjectModel, catalog: ComponentRegistry, macchina: str) -> LineaDellaMacchina | None:
    """Risale l'alimentazione della macchina, dall'attacco `power` attraverso i passanti (che
    entrano da `a` ed escono da `b`), fino al pezzo da cui parte. `None` se la macchina non ha
    un cavo sull'alimentazione."""
    alimentazione = {n.id for n in project.networks if n.medium == "power_supply"}
    pezzi = {p.id: p for p in project.components}
    arrivi: dict[tuple[str, str], tuple[str, str, str]] = {}
    for tubazione in project.connections:
        if tubazione.network_id not in alimentazione:
            continue
        a, b = tubazione.endpoint_a, tubazione.endpoint_b
        arrivi[(b.component_id, b.port_id)] = (a.component_id, a.port_id, tubazione.id)
        arrivi[(a.component_id, a.port_id)] = (b.component_id, b.port_id, tubazione.id)
    capo = (macchina, "power")
    if capo not in arrivi:
        return None
    passanti: list[str] = []
    tubazioni: list[str] = []
    visti = {macchina}
    while capo in arrivi:
        chi, porta, tubazione = arrivi[capo]
        tubazioni.append(tubazione)
        if chi in visti or chi not in pezzi:
            return LineaDellaMacchina(macchina, tuple(passanti), tuple(tubazioni), None)
        visti.add(chi)
        if porta == "b" and (chi, "a") in arrivi:
            passanti.append(chi)
            capo = (chi, "a")
            continue
        return LineaDellaMacchina(macchina, tuple(passanti), tuple(tubazioni), chi)
    return LineaDellaMacchina(macchina, tuple(passanti), tuple(tubazioni), None)


def _macchine(project: ProjectModel, catalog: ComponentRegistry) -> list[ComponentInstance]:
    return [p for p in project.components if _e_shenling(p) and "heat_generation" in _funzioni(catalog, p)]


def _numero(valore: object) -> float | None:
    if isinstance(valore, bool) or not isinstance(valore, int | float):
        return None
    return float(valore)


def _n(valore: float) -> str:
    return f"{valore:g}".replace(".", ",")


# --- 1 e 2: i dati che mancano ---------------------------------------------------------------


def scrivi_i_dati_del_manuale(
    project: ProjectModel, catalog: ComponentRegistry, sigle: Mapping[str, str] | None = None
) -> tuple[ProjectModel, list[str]]:
    """Il grafo con i dati elettrici del manuale **dove mancano**, e che cosa si e' scritto,
    in parole: sulle Shenling l'alimentazione, la corrente massima e il cavo minimo; sugli
    interruttori della loro linea poli, curva, In, Idn, tipo e alta velocita'. Un dato del
    progettista resta com'e'."""
    sigle = sigle or {}
    nuovi: dict[str, dict[str, JsonPrimitive]] = {}
    detto: list[str] = []
    pezzi = {p.id: p for p in project.components}

    def nome(pezzo_id: str) -> str:
        return sigle.get(pezzo_id) or pezzi[pezzo_id].tag or pezzo_id

    for macchina in _macchine(project, catalog):
        potenza = macchina.properties.get("power_kw")
        linea, assunta = linea_del_manuale(macchina)
        if linea is None:
            if _trifase_dichiarata(macchina) and isinstance(potenza, int | float):
                detto.append(
                    f"{nome(macchina.id)}: alimentazione «{macchina.properties[ALIMENTAZIONE]}» dichiarata, ma il "
                    f"manuale Shenling (§7.4 p. 55) non ha la {_n(float(potenza))} kW trifase: nessun dato "
                    "elettrico scritto, va chiesto al progettista."
                )
            continue
        mancanti = {k: v for k, v in linea.dati_della_macchina().items() if k not in macchina.properties}
        if mancanti:
            nuovi.setdefault(macchina.id, {}).update(mancanti)
            scritti = ", ".join(f"{k} {_valore(v)}" for k, v in mancanti.items())
            detto.append(
                f"{nome(macchina.id)} (Shenling {_n(float(potenza))} kW): scritti {scritti} — manuale §7.4 p. 55"  # type: ignore[arg-type]
                + (
                    f"; alimentazione non data, assunta monofase {MONOFASE} (se e' trifase, scrivi "
                    "«alimentazione»: «400 V 3N~» e rilancia)"
                    if assunta
                    else ""
                )
                + "."
            )
        traccia = linea_della_macchina(project, catalog, macchina.id)
        if traccia is None:
            continue
        for passante in traccia.passanti:
            interruttore = pezzi[passante]
            if FUNZIONE_DI_PROTEZIONE not in _funzioni(catalog, interruttore):
                continue
            mancanti = {k: v for k, v in linea.dati_della_protezione().items() if k not in interruttore.properties}
            if not mancanti:
                continue
            nuovi.setdefault(passante, {}).update(mancanti)
            detto.append(
                f"{nome(passante)} sulla linea di {nome(macchina.id)}: scritti "
                + ", ".join(f"{k} {_valore(v)}" for k, v in mancanti.items())
                + f" — {linea.fonte}; specifica §3.2 (bipolare, curva C, Idn 30 mA, tipo B, alta velocita')."
            )
    if not nuovi:
        return project, detto
    componenti = [
        p.model_copy(update={"properties": {**p.properties, **nuovi[p.id]}}) if p.id in nuovi else p
        for p in project.components
    ]
    return project.model_copy(update={"components": componenti}), detto


def _valore(valore: JsonPrimitive) -> str:
    if isinstance(valore, bool):
        return "si'" if valore else "no"
    if isinstance(valore, int | float):
        return _n(float(valore))
    return f"«{valore}»"


# --- 3: gli avvisi ---------------------------------------------------------------------------


def avvisi_della_linea(
    project: ProjectModel, catalog: ComponentRegistry, sigle: Mapping[str, str] | None = None
) -> list[str]:
    """Quello che la linea di una Shenling dichiara sotto il manuale, in parole. Segnala e
    non corregge, come gli altri avvisi del manuale (D-223, D-226):

    - l'**In** di un interruttore della linea sotto la corrente massima della macchina (il
      maggiore fra il manuale e quella dichiarata sulla macchina);
    - la **sezione** di un tratto della linea (`sezione`, «3G4», «6 mm²») sotto quella del
      manuale;
    - la linea **dal quadro** alla macchina **senza l'interruttore** (specifica §3.2, manuale
      p. 51)."""
    sigle = sigle or {}
    pezzi = {p.id: p for p in project.components}
    tubazioni = {t.id: t for t in project.connections}
    avvisi: list[str] = []

    def nome(pezzo_id: str) -> str:
        return sigle.get(pezzo_id) or pezzi[pezzo_id].tag or pezzo_id

    for macchina in _macchine(project, catalog):
        linea, _ = linea_del_manuale(macchina)
        traccia = linea_della_macchina(project, catalog, macchina.id)
        if linea is None or traccia is None:
            continue
        potenza = _n(float(macchina.properties["power_kw"]))  # type: ignore[arg-type]
        dichiarata = _numero(macchina.properties.get(CORRENTE_MAX_A))
        soglia, di_chi = linea.corrente_max_a, f"del manuale (§7.4 p. 55) per la Shenling {potenza} kW"
        if dichiarata is not None and dichiarata > soglia:
            soglia, di_chi = dichiarata, f"dichiarati sulla macchina {nome(macchina.id)}"
        interruttori = [
            pezzi[p] for p in traccia.passanti if FUNZIONE_DI_PROTEZIONE in _funzioni(catalog, pezzi[p])
        ]
        for interruttore in interruttori:
            nominale = _numero(interruttore.properties.get(IN_A))
            if nominale is not None and nominale < soglia:
                avvisi.append(
                    f"{nome(interruttore.id)}: In {_n(nominale)} A sulla linea di {nome(macchina.id)}, sotto i "
                    f"{_n(soglia)} A {di_chi}: la protezione proposta e' {linea.poli} {linea.curva}"
                    f"{_n(linea.in_a)} ({linea.fonte}). Va rivista, o confermata dal progettista con la targa."
                )
        for tubazione_id in traccia.tubazioni:
            sezione = tubazioni[tubazione_id].sezione
            mm2 = sezione_in_mm2(sezione)
            if mm2 is not None and mm2 < linea.sezione_mm2:
                avvisi.append(
                    f"linea di {nome(macchina.id)}: cavo {sezione}, {_n(mm2)} mm², sotto i {_n(linea.sezione_mm2)} "
                    f"mm² del manuale (§7.4 p. 55) per la Shenling {potenza} kW: il cavo minimo e' "
                    f"{linea.cavo_minimo}. Va rivisto, o confermato dal progettista."
                )
        dal_quadro = traccia.origine is not None and "power_source" in _funzioni(catalog, pezzi[traccia.origine])
        if dal_quadro and not interruttori:
            avvisi.append(
                f"linea di {nome(macchina.id)} dal quadro {nome(traccia.origine)}: manca la protezione della linea "  # type: ignore[arg-type]
                f"(specifica §3.2, manuale p. 51) — un interruttore magnetotermico differenziale "
                f"`circuit-breaker-rcbo` in serie all'uscita del quadro, {linea.poli} {linea.curva}{_n(linea.in_a)} "
                f"Idn {_n(linea.idn_ma)} mA tipo {linea.tipo_differenziale}."
            )
    return avvisi


__all__ = [
    "ALIMENTAZIONE",
    "CAVO_MINIMO",
    "CORRENTE_MAX_A",
    "MONOFASE",
    "SHENLING_THERMAX_R290_LINEA",
    "LineaDellaMacchina",
    "LineaDelManuale",
    "avvisi_della_linea",
    "linea_del_manuale",
    "linea_della_macchina",
    "scrivi_i_dati_del_manuale",
]
