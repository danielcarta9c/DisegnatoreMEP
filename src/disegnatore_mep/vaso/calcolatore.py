"""Il calcolatore del vaso d'espansione a membrana (REL-011, **D-220**).

Il PO: «la skill dimensiona … quindi mi va bene che dimensioni il vaso» (I-247). I dati li
raccoglie l'agente in sessione — dal progettista, o stimati dai terminali dicendo che sono
una stima —; **il conto lo fa questo modulo**, cosi' che gli stessi dati diano sempre lo
stesso vaso.

Il metodo e' quello della UNI EN 12828 per i vasi a membrana:

- **il volume d'espansione** ``Ve = e · C``: ``C`` e' il contenuto d'acqua di tutto cio'
  che il vaso vede senza uno scambiatore in mezzo (D-220, punto 1), ``e`` il coefficiente
  d'espansione dell'acqua fra la temperatura di riempimento (10 °C) e la massima di
  esercizio, dalla densita' (formula di Kell, 0–150 °C);
- **la riserva d'acqua** ``Vwr``: lo 0,5 % del contenuto, almeno 3 litri;
- **la precarica** ``p0``: la pressione statica sopra il vaso (il dislivello fino al punto
  piu' alto, 0,0981 bar al metro) piu' 0,3 bar perche' in alto non entri aria; mai sotto la
  pressione minima di esercizio che chiede il generatore (la Shenling ThermaX vuole almeno
  1,5 bar per la portata, ricerca guasti del manuale);
- **la pressione finale** ``pe``: la taratura della valvola di sicurezza meno 0,5 bar, lo
  scarto di chiusura delle valvole fino a 5 bar;
- **il volume nominale** ``Vn = (Ve + Vwr) · (pe + 1) / (pe − p0)``, in pressioni relative
  (bar) con l'atmosfera aggiunta;
- **la taglia**: la prima della serie commerciale che non sia sotto ``Vn``;
- **la pressione di caricamento a freddo**: la precarica piu' 0,3 bar (la riserva d'acqua
  entra nel vaso), mai sotto quella che il costruttore del generatore indica per il
  riempimento (la Shenling dice «circa 2,0 bar», § 6.6).

Con il glicole il coefficiente d'espansione non e' quello dell'acqua: lo da' la scheda
della miscela, e il calcolatore lo prende cosi' com'e' (specifica Nove C § 2.4: «con
glicole la capacita' si aumenta in proporzione»).

**Fonti e limiti.** La UNI EN 12828 qui e' riassunta, non letta riga per riga nella sua
edizione vigente (la ricerca SRC-028 dice che l'edizione 2014 non e' stata letta): margini
(0,3 bar, 0,5 bar) e riserva (0,5 %, 3 l) sono quelli d'uso comune del metodo, e restano
costanti con un nome, da correggere in un punto solo se la norma letta dice altro. La serie
delle taglie e' quella tipica dei vasi da riscaldamento; quella vera e' del catalogo del
fornitore.
"""

from dataclasses import dataclass
from math import ceil

TEMPERATURA_DI_RIEMPIMENTO_C = 10.0
"""L'acqua entra fredda: il coefficiente d'espansione si misura da qui."""

BAR_AL_METRO = 0.0981
"""Un metro di colonna d'acqua, in bar."""

MARGINE_SULLA_STATICA_BAR = 0.3
"""Quanto la precarica sta sopra la pressione statica, perche' nel punto piu' alto la
pressione resti positiva e non entri aria."""

SCARTO_DI_CHIUSURA_BAR = 0.5
"""La pressione finale sta sotto la taratura della valvola di sicurezza di questo tanto:
lo scarto fra apertura e chiusura delle valvole fino a 5 bar."""

RISERVA_D_ACQUA_FRAZIONE = 0.005
RISERVA_D_ACQUA_MINIMA_L = 3.0

RISERVA_DI_CARICAMENTO_BAR = 0.3
"""A freddo l'impianto si carica sopra la precarica di questo tanto: e' la riserva d'acqua
che entra nel vaso."""

SERIE_DEI_VASI_L: tuple[int, ...] = (
    8, 12, 18, 24, 35, 50, 80, 100, 150, 200, 250, 300, 400, 500, 600, 750, 1000,
)
"""Le taglie tipiche dei vasi a membrana da riscaldamento, in litri. Oltre 1000 l il
calcolatore non sceglie: lo dice."""


def densita_dell_acqua(temperatura_c: float) -> float:
    """La densita' dell'acqua in kg/m³ (formula di Kell, 1975, valida da 0 a 150 °C):
    999,70 a 10 °C, 977,77 a 70 °C."""
    t = temperatura_c
    if not 0.0 <= t <= 150.0:
        raise ValueError(f"la formula della densita' vale fra 0 e 150 °C: {t} °C")
    numeratore = (
        999.83952 + 16.945176 * t - 7.9870401e-3 * t**2 - 46.170461e-6 * t**3
        + 105.56302e-9 * t**4 - 280.54253e-12 * t**5
    )
    return numeratore / (1.0 + 16.879850e-3 * t)


def coefficiente_di_espansione(temperatura_massima_c: float) -> float:
    """Di quanto cresce il volume dell'acqua da 10 °C alla temperatura massima: 0,0142 a
    55 °C, 0,0224 a 70 °C."""
    return densita_dell_acqua(TEMPERATURA_DI_RIEMPIMENTO_C) / densita_dell_acqua(temperatura_massima_c) - 1.0


@dataclass(frozen=True)
class DatiDelVaso:
    """I dati che l'agente raccoglie in sessione (D-220, punto 3)."""

    contenuto_l: float
    """Tutta l'acqua che il vaso vede: macchine, tubi, volano, distribuzione, terminali."""
    temperatura_massima_c: float
    """La massima di mandata: quella di progetto o, se manca, la massima della macchina."""
    dislivello_m: float
    """Dal vaso al punto piu' alto dell'impianto (il radiatore o lo sfiato piu' in alto)."""
    taratura_sicurezza_bar: float = 3.0
    """La valvola di sicurezza del circuito: 3 bar sulla Shenling ThermaX."""
    pressione_minima_bar: float = 0.0
    """La pressione minima di esercizio che il generatore chiede (Shenling: 1,5 bar)."""
    pressione_di_riempimento_bar: float = 0.0
    """La pressione a cui il costruttore dice di riempire (Shenling: circa 2,0 bar)."""
    coefficiente_di_espansione: float | None = None
    """Con il glicole, quello della miscela dalla sua scheda; senza, quello dell'acqua."""
    contenuto_stimato: bool = False
    """Il contenuto e' una stima dai terminali, non un dato del progettista."""


@dataclass(frozen=True)
class Vaso:
    """Il risultato: quanto serve, che taglia, a che pressioni."""

    coefficiente: float
    volume_di_espansione_l: float
    riserva_l: float
    precarica_bar: float
    pressione_finale_bar: float
    volume_nominale_l: float
    taglia_l: int | None
    caricamento_bar: float
    avvisi: tuple[str, ...]

    def caratteristiche(self, esecutivo: bool, contenuto_stimato: bool = False) -> str:
        """La cella «caratteristiche» della tabella (D-221, D-224): il volume sempre, la
        precarica solo nell'esecutivo."""
        taglia = f"{self.taglia_l} l" if self.taglia_l else f"oltre {SERIE_DEI_VASI_L[-1]} l"
        parti = [taglia]
        if esecutivo:
            parti.append(f"precarica {_bar(self.precarica_bar)} bar")
        if contenuto_stimato:
            parti.append("contenuto stimato")
        return " · ".join(parti)

    @property
    def scritta_di_caricamento(self) -> str:
        """La scritta accanto al gruppo di riempimento, nell'esecutivo (D-221)."""
        return f"carica {_bar(self.caricamento_bar)} bar"


def _bar(valore: float) -> str:
    return f"{valore:.1f}".replace(".", ",")


def _per_eccesso(valore: float, passo: float = 0.1) -> float:
    return round(ceil(round(valore / passo, 6)) * passo, 6)


def dimensiona_il_vaso(dati: DatiDelVaso) -> Vaso:
    """Il vaso per questi dati. Non inventa: se i dati non bastano, solleva."""
    if dati.contenuto_l <= 0:
        raise ValueError(f"il contenuto d'acqua deve essere positivo: {dati.contenuto_l} l")
    if dati.dislivello_m < 0:
        raise ValueError(f"il dislivello non puo' essere negativo: {dati.dislivello_m} m")
    if dati.taratura_sicurezza_bar <= SCARTO_DI_CHIUSURA_BAR:
        raise ValueError(f"taratura della valvola di sicurezza troppo bassa: {dati.taratura_sicurezza_bar} bar")
    coefficiente = (
        dati.coefficiente_di_espansione
        if dati.coefficiente_di_espansione is not None
        else coefficiente_di_espansione(dati.temperatura_massima_c)
    )
    volume_di_espansione = coefficiente * dati.contenuto_l
    riserva = max(RISERVA_D_ACQUA_FRAZIONE * dati.contenuto_l, RISERVA_D_ACQUA_MINIMA_L)
    statica = dati.dislivello_m * BAR_AL_METRO
    precarica = _per_eccesso(max(statica + MARGINE_SULLA_STATICA_BAR, dati.pressione_minima_bar))
    finale = dati.taratura_sicurezza_bar - SCARTO_DI_CHIUSURA_BAR
    avvisi: list[str] = []
    if finale - precarica < 0.3:
        avvisi.append(
            f"fra precarica ({_bar(precarica)} bar) e pressione finale ({_bar(finale)} bar) resta meno di 0,3 bar: "
            "l'edificio e' troppo alto per questa valvola di sicurezza, il vaso diventa enorme. Va rivisto col "
            "progettista (vaso in alto, o un'altra taratura)."
        )
    if finale <= precarica:
        raise ValueError(
            f"la precarica ({_bar(precarica)} bar) non sta sotto la pressione finale ({_bar(finale)} bar): "
            "nessun vaso basta"
        )
    nominale = (volume_di_espansione + riserva) * (finale + 1.0) / (finale - precarica)
    taglia = next((t for t in SERIE_DEI_VASI_L if t >= nominale - 1e-9), None)
    if taglia is None:
        avvisi.append(f"servono {nominale:.0f} l: oltre la serie tipica, si sceglie sul catalogo del fornitore")
    caricamento = _per_eccesso(max(precarica + RISERVA_DI_CARICAMENTO_BAR, dati.pressione_di_riempimento_bar))
    if caricamento >= finale:
        avvisi.append(
            f"la pressione di caricamento ({_bar(caricamento)} bar) arriva alla pressione finale: verificare col "
            "progettista"
        )
    return Vaso(
        coefficiente=coefficiente,
        volume_di_espansione_l=volume_di_espansione,
        riserva_l=riserva,
        precarica_bar=precarica,
        pressione_finale_bar=finale,
        volume_nominale_l=nominale,
        taglia_l=taglia,
        caricamento_bar=caricamento,
        avvisi=tuple(avvisi),
    )


__all__ = [
    "SERIE_DEI_VASI_L",
    "DatiDelVaso",
    "Vaso",
    "coefficiente_di_espansione",
    "densita_dell_acqua",
    "dimensiona_il_vaso",
]
