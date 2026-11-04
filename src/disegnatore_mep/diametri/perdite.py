"""La verifica della prevalenza della pompa a bordo (I-270): le perdite del giro primario.

Il PO, su una commessa reale (villetta, Shenling 12 kW): il calcolo dei diametri «non
verifica le perdite di carico contro la prevalenza utile della pompa a bordo». Qui si
**verifica**, e non si dimensiona: il tubo resta quello della tavola, e se il giro
costa piu' di quanto la pompa da' la skill lo dice — un avviso, come quelli del manuale
del costruttore (`costruttori.py`). Le scelte restano del progettista.

**Quando si fa.** Solo con i dati del progettista, e mai con numeri inventati (D-087):

- la **prevalenza utile** della macchina, `prevalenza_utile_kpa` sul generatore: quella
  che la pompa a bordo lascia all'impianto, fuori dalla macchina, alla portata di
  progetto. **Per una Shenling ThermaX senza il dato** (I-281) la verifica si fa con
  8 m di colonna d'acqua, il valore basso degli «8/9 metri» del PO, e l'avviso lo
  dice: e' indicativo, e piu' vicino alla prevalenza massima della pompa che a quella
  utile alla portata, che e' minore — il valore vero e' la curva del manuale alla
  portata (`costruttori.DatiDelModello.prevalenza_indicativa_m`). E' questa verifica
  che dice la «troppa distanza» del PO per la 12 kW in MS 32×3;
- la **lunghezza** di ogni tratto del giro, `lunghezza_m` sulle tubazioni;
- il **tubo** e la **portata** di ogni tratto: il tubo del progettista o quello del
  calcolo (I-279), quindi i diametri chiesti su quella rete e la potenza col salto
  termico (§4.7 di Capire).

Se manca anche uno solo di questi su un giro, la verifica non si fa e non si dice niente.

**Il giro.** Dalla mandata della macchina al suo ritorno, sulla rete della macchina,
seguendo il verso dell'acqua che il catalogo dichiara: attraverso i raccordi, le
valvole a tre vie nelle loro posizioni (la deviatrice manda o sul volano o sul
serpentino, e i giri sono due), e attraverso il volano, che chiude il primario. Si
verifica il **giro piu' costoso**: e' quello che la pompa deve vincere.

**Il conto.** Per ogni tratto la perdita distribuita di Darcy-Weisbach,
Δp = f · L/D · ρ·v²/2, col fattore d'attrito di Swamee-Jain (moto turbolento) o 64/Re
(laminare); il diametro e' quello interno reale del tubo, con la scabrezza del suo
materiale (I-279). Alle distribuite si aggiunge una **maggiorazione dichiarata** per le
perdite concentrate di curve, valvole e raccordi. **Non entrano** le perdite proprie dei
pezzi che il calcolo non conosce — il serpentino del bollitore, uno scambiatore, il
defangatore —: il foglio lo dice.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import log10

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.layout.flow import GENERATOR_FUNCTIONS
from disegnatore_mep.layout.hierarchy import is_a_machine
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import ComponentInstance, ProjectModel

from .calcolatore import DENSITA_KG_M3, SECONDI_ALL_ORA
from .costruttori import dati_del_modello
from .portate import (
    FUNZIONI_DI_MISCELAZIONE,
    TOLLERANZA_M3H,
    _attacchi_del_percorso,
    _attraversati,
    _scelte,
    _verso,
    portate_delle_tratte,
)
from .tratti import TrattoDelDiametro, tratti_del_diametro
from .tubi import Materiale, Tubo

PREVALENZA_UTILE = "prevalenza_utile_kpa"
"""La prevalenza utile della pompa a bordo, in kPa: il dato del progettista (I-270)."""

PREVALENZA_UTILE_IN_METRI = "prevalenza_utile_m"
"""La stessa in metri di colonna d'acqua, quando il progettista la da' cosi': si scrive
nell'unita' del testo, e il conto la porta in kPa."""

GRAVITA_M_S2 = 9.80665
"""L'accelerazione di gravita' normale: 1 m di colonna d'acqua sono ρ·g = 9,807 kPa."""


KPA_AL_METRO = DENSITA_KG_M3 * GRAVITA_M_S2 / 1000.0
"""Un metro di colonna d'acqua in kPa."""


def prevalenza_della_macchina(proprieta: Mapping[str, object], pezzo: ComponentInstance | None = None) -> float | None:
    """La prevalenza con cui si verifica il giro di una macchina, in kPa: quella del
    progettista; senza, per una Shenling ThermaX, quella indicativa (I-281)."""
    data = prevalenza_utile_kpa(proprieta)
    if data is not None or pezzo is None:
        return data
    dati = dati_del_modello(pezzo)
    return None if dati is None else dati.prevalenza_indicativa_m * KPA_AL_METRO


def prevalenza_utile_kpa(proprieta: Mapping[str, object]) -> float | None:
    """La prevalenza utile in kPa, dall'una o dall'altra chiave; `None` se non c'e'.
    Se ci sono tutt'e due vale quella in kPa."""
    in_kpa = _numero(proprieta.get(PREVALENZA_UTILE))
    if in_kpa is not None:
        return in_kpa
    in_metri = _numero(proprieta.get(PREVALENZA_UTILE_IN_METRI))
    if in_metri is None:
        return None
    return in_metri * DENSITA_KG_M3 * GRAVITA_M_S2 / 1000.0

VISCOSITA_CINEMATICA_M2_S = 0.658e-6
"""La viscosita' cinematica dell'acqua a 40 °C, in m²/s: la temperatura media di un
primario di pompa di calore. A 20 °C e' 1,004·10⁻⁶: le perdite crescono di qualche
punto percentuale, meno della maggiorazione delle concentrate."""

RUGOSITA_ACCIAIO_M = 0.045e-3
"""La scabrezza assoluta del tubo d'acciaio commerciale, in metri (il valore di Moody)."""

RUGOSITA_RAME_M = 0.0015e-3
"""La scabrezza assoluta del tubo di rame trafilato, in metri."""

RUGOSITA_MULTISTRATO_M = 0.007e-3
"""La scabrezza del multistrato PEX/Al/PEX, in metri: 0,007 mm, la «rugosità
superficiale» della scheda tecnica Valsir Mixal."""

RUGOSITA_DEL_MATERIALE: dict[Materiale, float] = {
    "multistrato": RUGOSITA_MULTISTRATO_M,
    "acciaio": RUGOSITA_ACCIAIO_M,
    "rame": RUGOSITA_RAME_M,
}
"""Con il materiale noto (I-279) la verifica usa la scabrezza del tubo vero."""

RUGOSITA_DI_CALCOLO_M = RUGOSITA_ACCIAIO_M
"""Quella con cui si verificava prima di I-279, quando il materiale era a scelta
dell'installatore: l'acciaio, che perde di piu'. Resta il valore predefinito di
`perdita_distribuita_pa_m`."""

MAGGIORAZIONE_CONCENTRATE = 0.30
"""Le perdite concentrate — curve, valvole, raccordi, la deviatrice — come frazione
delle distribuite: il 30 %. E' una stima dichiarata, non un conto pezzo per pezzo, e
la tavola e' uno schema: le curve vere non ci sono."""

RE_DI_TRANSIZIONE = 2300.0
"""Sotto questo numero di Reynolds il moto e' laminare, e f = 64/Re."""

MASSIMO_DI_GIRI = 64
"""Quanti giri si provano al piu' per una macchina: un tetto perche' il conto non
cresca senza fine su un grafo grande; oltre, la verifica non si fa."""


def fattore_d_attrito(reynolds: float, rugosita_m: float, diametro_m: float) -> float:
    """Il fattore d'attrito di Darcy: 64/Re in laminare, Swamee-Jain in turbolento.

    Swamee-Jain: f = 0,25 / [log₁₀(ε/(3,7·D) + 5,74/Re^0,9)]², l'esplicita della
    Colebrook (scarto sotto l'1 % fra Re 5000 e 10⁸)."""
    if reynolds <= 0 or diametro_m <= 0:
        raise ValueError(f"Reynolds e diametro devono essere positivi: {reynolds}, {diametro_m}")
    if reynolds < RE_DI_TRANSIZIONE:
        return 64.0 / reynolds
    return 0.25 / log10(rugosita_m / (3.7 * diametro_m) + 5.74 / reynolds**0.9) ** 2


def perdita_distribuita_pa_m(
    portata_m3h: float, interno_mm: float, rugosita_m: float = RUGOSITA_DI_CALCOLO_M
) -> float:
    """La perdita distribuita in Pa per metro di tubo: Darcy-Weisbach, sul diametro
    interno `interno_mm`.

    Per 2,067 m³/h (12 kW, 5 K) in 32 mm interni d'acciaio: v = 0,714 m/s, Re = 34 700,
    f = 0,0265, circa 211 Pa/m."""
    diametro = interno_mm / 1000.0
    velocita = portata_m3h / SECONDI_ALL_ORA / (3.141592653589793 * diametro**2 / 4.0)
    reynolds = velocita * diametro / VISCOSITA_CINEMATICA_M2_S
    attrito = fattore_d_attrito(reynolds, rugosita_m, diametro)
    return attrito / diametro * DENSITA_KG_M3 * velocita**2 / 2.0


@dataclass(frozen=True)
class TrattoDelGiro:
    """Un tratto del giro, con la perdita che porta."""

    da: str
    a: str
    """Le estremita' della tratta: gli id dei pezzi."""
    tubo: Tubo
    portata_m3h: float
    velocita_m_s: float
    lunghezza_m: float
    perdita_pa_m: float

    @property
    def perdita_kpa(self) -> float:
        return self.perdita_pa_m * self.lunghezza_m / 1000.0


@dataclass(frozen=True)
class VerificaDellaPrevalenza:
    """Il giro piu' costoso di una macchina, contro la prevalenza utile della sua pompa."""

    macchina: str
    prevalenza_utile_kpa: float
    giro: tuple[TrattoDelGiro, ...]
    giri: int
    """Quanti giri la macchina ha: due con la deviatrice."""
    attraverso: tuple[str, ...] = ()
    """Le macchine che il giro attraversa — il volano, il serpentino del bollitore —:
    dicono quale giro e', a chi legge."""
    assunta: bool = False
    """La prevalenza non e' del progettista: e' quella indicativa della macchina
    (I-281), e l'avviso lo dice."""

    @property
    def distribuite_kpa(self) -> float:
        return sum(item.perdita_kpa for item in self.giro)

    @property
    def concentrate_kpa(self) -> float:
        return self.distribuite_kpa * MAGGIORAZIONE_CONCENTRATE

    @property
    def totale_kpa(self) -> float:
        return self.distribuite_kpa + self.concentrate_kpa

    @property
    def supera(self) -> bool:
        return self.totale_kpa > self.prevalenza_utile_kpa


def _numero(valore: object) -> float | None:
    if isinstance(valore, bool) or not isinstance(valore, int | float) or valore <= 0:
        return None
    return float(valore)


def _passaggi(definizione: ComponentDefinition, entrata: str) -> list[str]:
    """Gli attacchi da cui l'acqua puo' uscire da un pezzo in cui e' entrata qui.

    Le valvole a tre vie nelle loro posizioni (`portate._scelte`); una macchina fra i
    due attacchi che attraversa; tutto il resto — raccordi, collettori, il volano —
    verso ogni altro attacco del percorso, e il verso dell'acqua sceglie."""
    percorso = _attacchi_del_percorso(definizione)
    commuta = bool(definizione.hydraulic_states) or bool(
        frozenset(definizione.functions) & FUNZIONI_DI_MISCELAZIONE
    )
    coppie = _attraversati(definizione)
    if commuta or coppie:
        gruppi = (
            [gruppo for scelta in _scelte(definizione) for gruppo in scelta.gruppi] if commuta else list(coppie)
        )
        return sorted({pid for gruppo in gruppi if entrata in gruppo for pid in gruppo if pid != entrata})
    return [pid for pid in percorso if pid != entrata]


def verifiche_della_prevalenza(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunks: Sequence[Trunk] | None = None,
    tratti: Sequence[TrattoDelDiametro] | None = None,
) -> tuple[VerificaDellaPrevalenza, ...]:
    """Una verifica per ogni macchina che ha tutti i dati; nessuna per le altre."""
    if project.diametri is None:
        return ()
    definizioni = {item.id: catalog.get(item.definition_id) for item in project.components}
    con_la_prevalenza = [
        item
        for item in project.components
        if prevalenza_della_macchina(item.properties, item) is not None
        and frozenset(definizioni[item.id].functions) & GENERATOR_FUNCTIONS
    ]
    if not con_la_prevalenza:
        return ()
    tutte = list(trunks) if trunks is not None else tratte_del_progetto(project, catalog)
    portate = portate_delle_tratte(project, catalog, tutte)
    if tratti is None:
        tratti = tratti_del_diametro(project, catalog, tutte, portate)
    acqua = [item for item in tutte if item.connection_ids in portate.tratte]
    alla_porta: dict[tuple[str, str], Trunk] = {}
    for tratta in acqua:
        for ref in (tratta.start, tratta.end):
            alla_porta[(ref.component_id, ref.port_id)] = tratta
    tubo_di = {
        chiave: tratto.tubo
        for tratto in tratti
        if tratto.tubo is not None
        for chiave in tratto.chiavi
    }
    lunghezze = {item.id: item.lunghezza_m for item in project.connections}
    attacchi_d_acqua: dict[str, int] = {}
    for component_id, _ in alla_porta:
        attacchi_d_acqua[component_id] = attacchi_d_acqua.get(component_id, 0) + 1

    def di_servizio(component_id: str) -> bool:
        """Il T da cui pende una sicurezza o un vaso: la tubazione del progettista
        ci passa attraverso, e la sua lunghezza sta su uno solo dei due pezzi."""
        definizione = definizioni[component_id]
        return (
            definizione.is_a_fitting
            and not definizione.hydraulic_states
            and attacchi_d_acqua.get(component_id) == 2
        )

    def voce(pezzi: list[tuple[Trunk, str, str]]) -> TrattoDelGiro | None:
        """Un tratto del giro: le tratte del motore fra due nodi veri, attraverso i T
        di servizio. Le regole spezzano la tubazione del progettista e la lunghezza
        resta su un pezzo solo (`rules.apply`): si somma su tutte."""
        chiavi = [tratta.connection_ids for tratta, _, _ in pezzi]
        portate_date = {portate.tratte[chiave].portata_m3h for chiave in chiavi}
        tubi_dati = {tubo_di.get(chiave) for chiave in chiavi}
        date = [lunghezze[c] for chiave in chiavi for c in chiave if lunghezze.get(c) is not None]
        if len(portate_date) != 1 or len(tubi_dati) != 1 or not date:
            return None
        (portata,), (tubo,) = portate_date, tubi_dati
        if portata is None or portata <= TOLLERANZA_M3H or tubo is None:
            return None
        return TrattoDelGiro(
            da=pezzi[0][1],
            a=pezzi[-1][2],
            tubo=tubo,
            portata_m3h=portata,
            velocita_m_s=tubo.velocita_m_s(portata),
            lunghezza_m=float(sum(x for x in date if x is not None)),
            perdita_pa_m=perdita_distribuita_pa_m(
                portata, tubo.interno_mm, RUGOSITA_DEL_MATERIALE[tubo.materiale]
            ),
        )

    def tratti_del_giro(macchina: str, giro: tuple[Trunk, ...]) -> list[TrattoDelGiro | None]:
        voci: list[TrattoDelGiro | None] = []
        corrente: list[tuple[Trunk, str, str]] = []
        qui = macchina
        for tratta in giro:
            la = tratta.end.component_id if tratta.start.component_id == qui else tratta.start.component_id
            corrente.append((tratta, qui, la))
            if not di_servizio(la):
                voci.append(voce(corrente))
                corrente = []
            qui = la
        if corrente:
            voci.append(voce(corrente))
        return voci

    verifiche: list[VerificaDellaPrevalenza] = []
    for macchina in con_la_prevalenza:
        definizione = definizioni[macchina.id]
        coppie = _attraversati(definizione)
        if len(coppie) != 1:
            continue
        (coppia,) = coppie
        mandata = next((pid for pid in coppia if _verso(definizione, pid) < 0), None)
        ritorno = next((pid for pid in coppia if _verso(definizione, pid) > 0), None)
        if mandata is None or ritorno is None:
            continue
        prima = alla_porta.get((macchina.id, mandata))
        ultima = alla_porta.get((macchina.id, ritorno))
        if prima is None or ultima is None:
            continue
        giri = _giri(macchina.id, prima, ultima, alla_porta, definizioni)
        if giri is None or not giri:
            continue
        valutati: list[tuple[TrattoDelGiro, ...]] = []
        for giro in giri:
            voci = tratti_del_giro(macchina.id, giro)
            if any(item is None for item in voci):
                # Un tratto senza lunghezza, senza tubo o senza portata: non si inventa.
                valutati = []
                break
            valutati.append(tuple(item for item in voci if item is not None))
        if not valutati:
            continue
        peggiore = max(valutati, key=lambda giro: sum(item.perdita_kpa for item in giro))
        attraverso = tuple(
            dict.fromkeys(
                pezzo
                for item in peggiore
                for pezzo in (item.da, item.a)
                if pezzo != macchina.id and is_a_machine(definizioni[pezzo])
            )
        )
        verifiche.append(
            VerificaDellaPrevalenza(
                macchina=macchina.id,
                prevalenza_utile_kpa=prevalenza_della_macchina(macchina.properties, macchina) or 0.0,
                giro=peggiore,
                giri=len(valutati),
                attraverso=attraverso,
                assunta=prevalenza_utile_kpa(macchina.properties) is None,
            )
        )
    return tuple(verifiche)


def _giri(
    macchina: str,
    prima: Trunk,
    ultima: Trunk,
    alla_porta: dict[tuple[str, str], Trunk],
    definizioni: dict[str, ComponentDefinition],
) -> list[tuple[Trunk, ...]] | None:
    """I giri dalla mandata al ritorno della macchina, sulla sua rete e nel verso
    dell'acqua. `None` se sono troppi da provare."""
    rete = prima.network_id
    giri: list[tuple[Trunk, ...]] = []

    def altro_capo(tratta: Trunk, component_id: str, port_id: str) -> tuple[str, str]:
        if (tratta.start.component_id, tratta.start.port_id) == (component_id, port_id):
            return tratta.end.component_id, tratta.end.port_id
        return tratta.start.component_id, tratta.start.port_id

    def avanti(
        tratta: Trunk, da: tuple[str, str], visti: frozenset[str], cammino: tuple[Trunk, ...]
    ) -> bool:
        if len(giri) > MASSIMO_DI_GIRI:
            return False
        pezzo, entrata = altro_capo(tratta, *da)
        if tratta is ultima:
            if pezzo == macchina:
                giri.append(cammino)
            return True
        if pezzo in visti or pezzo == macchina:
            return True
        definizione = definizioni[pezzo]
        if _verso(definizione, entrata) < 0 or frozenset(definizione.functions) & GENERATOR_FUNCTIONS:
            # Contro il verso dell'acqua, o dentro un'altra macchina: non e' il giro di questa.
            return True
        for uscita in _passaggi(definizione, entrata):
            seguente = alla_porta.get((pezzo, uscita))
            if seguente is None or seguente.network_id != rete or seguente in cammino:
                continue
            if _verso(definizione, uscita) > 0:
                continue
            if not avanti(seguente, (pezzo, uscita), visti | {pezzo}, (*cammino, seguente)):
                return False
        return True

    mandata = (prima.start.component_id, prima.start.port_id)
    if mandata[0] != macchina:
        mandata = (prima.end.component_id, prima.end.port_id)
    if not avanti(prima, mandata, frozenset({macchina}), (prima,)):
        return None
    return giri


def avvisi_della_prevalenza(
    project: ProjectModel,
    catalog: ComponentRegistry,
    verifiche: Sequence[VerificaDellaPrevalenza] | None = None,
    sigle: Mapping[str, str] | None = None,
) -> list[str]:
    """Le verifiche che non tornano, in parole. Nessun avviso se i dati mancano.

    I pezzi si nominano con le sigle che la tavola scrive, quando chi chiama le ha
    (`piano.vista.sigle_del_grafo_intero`); altrimenti con quelle dell'ingegnere."""
    if verifiche is None:
        verifiche = verifiche_della_prevalenza(project, catalog)
    sigle = {**{item.id: item.tag or item.id for item in project.components}, **(sigle or {})}
    avvisi: list[str] = []
    for verifica in verifiche:
        if not verifica.supera:
            continue
        lunghezza = sum(item.lunghezza_m for item in verifica.giro)
        dove = ", ".join(sigle.get(item, item) for item in verifica.attraverso)
        avvisi.append(
            f"{sigle.get(verifica.macchina, verifica.macchina)}: il giro primario piu' costoso "
            f"({_n(lunghezza, 1)} m di tubo{', attraverso ' + dove if dove else ''}) "
            f"perde {_n(verifica.totale_kpa, 1)} kPa — {_n(verifica.distribuite_kpa, 1)} distribuite piu' il "
            f"{MAGGIORAZIONE_CONCENTRATE:.0%} di concentrate, serpentini e scambiatori esclusi — e la pompa "
            f"a bordo ne da' {_n(verifica.prevalenza_utile_kpa, 1)} utili"
            + (
                f" ({_n(verifica.prevalenza_utile_kpa / KPA_AL_METRO, 0)} m, indicativo del PO; il valore vero è "
                "la curva del manuale alla portata)"
                if verifica.assunta
                else ""
            )
            + ". La pompa da sola non basta: il giro va rivisto col progettista (i tubi della tavola non "
            "cambiano)."
        )
    return avvisi


def _n(valore: float, cifre: int) -> str:
    return f"{valore:.{cifre}f}".replace(".", ",")


__all__ = [
    "MAGGIORAZIONE_CONCENTRATE",
    "PREVALENZA_UTILE",
    "PREVALENZA_UTILE_IN_METRI",
    "KPA_AL_METRO",
    "RUGOSITA_ACCIAIO_M",
    "RUGOSITA_DEL_MATERIALE",
    "RUGOSITA_DI_CALCOLO_M",
    "RUGOSITA_MULTISTRATO_M",
    "RUGOSITA_RAME_M",
    "TrattoDelGiro",
    "VISCOSITA_CINEMATICA_M2_S",
    "VerificaDellaPrevalenza",
    "avvisi_della_prevalenza",
    "GRAVITA_M_S2",
    "fattore_d_attrito",
    "perdita_distribuita_pa_m",
    "prevalenza_della_macchina",
    "prevalenza_utile_kpa",
    "verifiche_della_prevalenza",
]
