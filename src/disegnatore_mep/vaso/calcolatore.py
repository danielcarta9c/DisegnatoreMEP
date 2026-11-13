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

## Il vaso sanitario (REL-026, I-300)

Il vaso del bollitore dell'acqua calda sanitaria, sull'acqua fredda in ingresso
(`dimensiona_il_vaso_sanitario`). Il metodo e' quello del focus tecnico Caleffi «Il
dimensionamento degli impianti idrosanitari — Vasi d'espansione e accumuli» (documento
0851415, © 2015), letto il 13 novembre 2026, p. 4:

- **il volume d'espansione** ``Ve = e · VB``: si conta **solo l'acqua del bollitore** — la
  rete di distribuzione e il ricircolo si trascurano, perche' basta un prelievo per far
  scendere la pressione —, ``e`` il coefficiente d'espansione fra la temperatura dell'acqua
  fredda in ingresso e la massima di accumulo, dalla densita' come per il riscaldamento (la
  tabella di Caleffi, riferita a 4 °C, da' gli stessi valori al decimillesimo);
- **la pressione iniziale** ``pa`` e' quella di alimentazione del bollitore: la taratura del
  riduttore di pressione, o la massima della rete;
- **la precarica** ``p0 = pa − 0,2 bar`` (I-301: il PO ha rimesso la scelta alla sessione).
  Caleffi la formula la scrive con la pressione di alimentazione e la precarica non la
  nomina; la dice il catalogo tecnico Reflex «Reflex, Refix — Expansion vessels» (RE1884en,
  letto il 13 novembre 2026), pp. 48, 49 e 53, che richiama la DIN 4807-5: «the supply
  pressure p0 in the expansion vessel must be at least 0.2 bar less than the minimum flow
  pressure», ``p0 = pa − 0.2 bar``, e fino a 1 bar in meno se il vaso e' lontano dal
  riduttore. Sotto la rete, perche' il vaso tenga sempre un po' d'acqua e la membrana non
  batta a ogni prelievo. **La DIN 4807-5 non e' stata letta**: e' citata dal catalogo;
- **la pressione finale**: la taratura della valvola di sicurezza diminuita del 10 % «che ne
  previene l'apertura», sopra i 5 bar (Caleffi, p. 4: ``Pe = 0,9 Pvs + 1`` in pressioni
  assolute). Fino a 5 bar lo scarto e' quello del vaso di riscaldamento, 0,5 bar, che a 5
  bar da' lo stesso numero: Caleffi, nelle pagine lette, il caso sotto i 5 bar non lo scrive;
- **il volume nominale** ``Vn = Ve · (pe + 1) (pa + 1) / [(p0 + 1) (pe − pa)]``, pressioni
  relative: e' la legge del gas col vaso precaricato a ``p0``, che parte da ``pa`` e arriva a
  ``pe``. Con ``p0 = pa`` e' la formula di Caleffi, ``Vv = VB (eB − e0) / (1 − Pa/Pe)``; con
  ``pe = psv − 0,5`` e' quella di Reflex, p. 49, ``Vn = VSp · n · (psv + 0,5)(p0 + 1,2) /
  [100 (p0 + 1)(psv − p0 − 0,7)]``. Il fattore ``(pa + 1)/(p0 + 1)`` e' l'acqua che il vaso
  tiene gia' a freddo: con 0,2 bar di scarto vale circa il 5 % in piu'. **Senza riserva
  d'acqua**: il circuito sanitario si ricarica dalla rete a ogni prelievo;
- **la taglia**: la prima della serie che non sia sotto ``Vn``.

Le prove del metodo (`tests/vaso`): l'esempio di Caleffi, p. 5 — bollitore da 1000 l, acqua
fredda a 10 °C, accumulo a 80 °C, rete a 3 bar, valvola a 7 bar: 63,49 l con la precarica
uguale alla rete, che e' la sua ipotesi — e l'esempio di Reflex, p. 46: 900 l, espansione
1,7 %, riduttore a 4,2 bar, precarica 4,0 bar, valvola a 10 bar: 31,5 l.

**Fonti e limiti.** La temperatura dell'acqua fredda e' 10 °C (Caleffi, p. 2: 10÷12 °C
nell'Italia settentrionale, 12÷15 al centro, 15÷18 al sud; il piu' freddo da' il vaso piu'
grande). La serie delle taglie sanitarie **e' quella d'uso comune, non letta su un
catalogo**: quella vera e' del fornitore (Reflex, p. 46, ha 8, 12, 18, 25, 33, 60, 80, 100 l).
Per la pressione finale Reflex raccomanda ``pe ≤ psv − 0,5 bar`` (p. 45), e nella stessa
pagina riporta dalla norma uno scarto del 20 % della taratura: qui resta il 10 % di Caleffi
sopra i 5 bar e 0,5 bar fino a 5. Nessuna norma e' stata letta per il sanitario.
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

SALTO_MINIMO_BAR = 0.3
"""Sotto questo salto fra precarica e pressione finale il vaso diventa enorme: si avvisa."""

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


def coefficiente_di_espansione(
    temperatura_massima_c: float, temperatura_iniziale_c: float = TEMPERATURA_DI_RIEMPIMENTO_C
) -> float:
    """Di quanto cresce il volume dell'acqua da 10 °C — o dalla temperatura iniziale data,
    l'acqua fredda del sanitario — alla temperatura massima: 0,0142 a 55 °C, 0,0224 a 70 °C."""
    return densita_dell_acqua(temperatura_iniziale_c) / densita_dell_acqua(temperatura_massima_c) - 1.0


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
    if finale - precarica < SALTO_MINIMO_BAR:
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


# --- il vaso sanitario (REL-026, I-300) ------------------------------------------------

TEMPERATURA_DELL_ACQUA_FREDDA_C = 10.0
"""L'acqua fredda che entra nel bollitore. Caleffi, focus tecnico 0851415, p. 2: 10÷12 °C
nell'Italia settentrionale, 12÷15 al centro, 15÷18 al sud; l'esempio di p. 5 usa 10 °C. Il
valore piu' basso da' il vaso piu' grande."""

SCARTO_SANITARIO_FRAZIONE = 0.10
"""Sopra `SOGLIA_DELLO_SCARTO_BAR` la pressione finale sta il 10 % sotto la taratura della
valvola di sicurezza, «che ne previene l'apertura»: Caleffi, focus tecnico 0851415, p. 4
(``Pe = 0,9 Pvs + 1``, assolute)."""

SOGLIA_DELLO_SCARTO_BAR = 5.0
"""Fino a 5 bar di taratura lo scarto e' quello del vaso di riscaldamento
(`SCARTO_DI_CHIUSURA_BAR`, 0,5 bar: per il sanitario e' la raccomandazione di Reflex,
RE1884en p. 45, ``pe ≤ psv − 0,5 bar``); sopra, il 10 % di Caleffi. A 5 bar i due danno la
stessa pressione finale, 4,5 bar."""

SCARTO_DELLA_PRECARICA_SANITARIA_BAR = 0.2
"""Quanto la precarica del vaso sanitario sta sotto la pressione di alimentazione (la
taratura del riduttore): Reflex, «Reflex, Refix — Expansion vessels» (RE1884en), pp. 48, 49
e 53, ``p0 = pa − 0.2 bar``, che richiama la DIN 4807-5 (non letta). Lo stesso catalogo
porta lo scarto fino a 1 bar quando il vaso e' lontano dal riduttore: quello lo decide chi
installa, e qui resta il minimo. Scelta rimessa dal PO alla sessione (I-301)."""

SERIE_DEI_VASI_SANITARI_L: tuple[int, ...] = (
    2, 5, 8, 12, 18, 24, 35, 50, 60, 80, 100, 150, 200, 300, 500,
)
"""Le taglie dei vasi sanitari, in litri: **la serie d'uso comune, non letta su un
catalogo**; quella vera e' del fornitore. Oltre 500 l il calcolatore non sceglie: lo dice."""


@dataclass(frozen=True)
class DatiDelVasoSanitario:
    """I dati del vaso sanitario, che l'agente raccoglie in sessione (REL-026, I-300)."""

    volume_bollitore_l: float
    """L'acqua del bollitore: e' la sola che si conta (Caleffi, p. 4)."""
    temperatura_massima_c: float
    """La massima di accumulo dell'acqua calda (anche quella dei cicli antilegionella)."""
    pressione_di_rete_bar: float
    """La pressione di alimentazione del bollitore: la taratura del riduttore, se c'e', o la
    massima della rete."""
    taratura_sicurezza_bar: float
    """La valvola di sicurezza del bollitore (il gruppo di sicurezza sanitario)."""
    temperatura_acqua_fredda_c: float = TEMPERATURA_DELL_ACQUA_FREDDA_C


@dataclass(frozen=True)
class VasoSanitario:
    """Il risultato: quanto serve, che taglia, a che pressioni."""

    coefficiente: float
    volume_di_espansione_l: float
    precarica_bar: float
    """La pressione del gas a vaso vuoto: la rete meno `SCARTO_DELLA_PRECARICA_SANITARIA_BAR`."""
    pressione_finale_bar: float
    volume_nominale_l: float
    taglia_l: int | None
    avvisi: tuple[str, ...]
    pressione_di_rete_bar: float = 0.0
    """La pressione di alimentazione da cui la precarica e' ricavata."""

    def caratteristiche(self, esecutivo: bool) -> str:
        """La cella «caratteristiche» della tabella, come quella del vaso di riscaldamento:
        il volume sempre, la precarica solo nell'esecutivo (D-221, D-224)."""
        parti = [f"{self.taglia_l} l" if self.taglia_l else f"oltre {SERIE_DEI_VASI_SANITARI_L[-1]} l"]
        if esecutivo:
            parti.append(f"precarica {_bar(self.precarica_bar)} bar")
        return " · ".join(parti)


def pressione_finale_sanitaria(taratura_bar: float) -> float:
    """La pressione finale del vaso sanitario per la taratura della valvola di sicurezza: il
    10 % sotto la taratura sopra i 5 bar, 0,5 bar sotto fino a 5 bar."""
    if taratura_bar > SOGLIA_DELLO_SCARTO_BAR:
        return round(taratura_bar * (1.0 - SCARTO_SANITARIO_FRAZIONE), 6)
    return taratura_bar - SCARTO_DI_CHIUSURA_BAR


def volume_nominale_sanitario(
    volume_di_espansione_l: float, rete_bar: float, precarica_bar: float, finale_bar: float,
) -> float:
    """Il volume nominale del vaso sanitario, pressioni relative: il gas precaricato a
    `precarica_bar` parte da `rete_bar` e arriva a `finale_bar`. Con la precarica uguale alla
    rete e' la formula di Caleffi; con la finale 0,5 bar sotto la valvola e' quella di Reflex."""
    return (
        volume_di_espansione_l * (finale_bar + 1.0) * (rete_bar + 1.0)
        / ((precarica_bar + 1.0) * (finale_bar - rete_bar))
    )


def dimensiona_il_vaso_sanitario(dati: DatiDelVasoSanitario) -> VasoSanitario:
    """Il vaso sanitario per questi dati. Non inventa: se i dati non bastano, solleva."""
    if dati.volume_bollitore_l <= 0:
        raise ValueError(f"il volume del bollitore deve essere positivo: {dati.volume_bollitore_l} l")
    if dati.temperatura_massima_c <= dati.temperatura_acqua_fredda_c:
        raise ValueError(
            f"la temperatura di accumulo ({dati.temperatura_massima_c:g} °C) non sta sopra quella "
            f"dell'acqua fredda ({dati.temperatura_acqua_fredda_c:g} °C)"
        )
    if dati.pressione_di_rete_bar <= 0:
        raise ValueError(f"la pressione di rete deve essere positiva: {dati.pressione_di_rete_bar} bar")
    if dati.taratura_sicurezza_bar <= SCARTO_DI_CHIUSURA_BAR:
        raise ValueError(f"taratura della valvola di sicurezza troppo bassa: {dati.taratura_sicurezza_bar} bar")
    coefficiente = coefficiente_di_espansione(dati.temperatura_massima_c, dati.temperatura_acqua_fredda_c)
    volume_di_espansione = coefficiente * dati.volume_bollitore_l
    rete = _per_eccesso(dati.pressione_di_rete_bar)
    if rete <= SCARTO_DELLA_PRECARICA_SANITARIA_BAR:
        raise ValueError(
            f"la pressione di rete ({_bar(rete)} bar) e' troppo bassa per precaricare il vaso "
            f"{_bar(SCARTO_DELLA_PRECARICA_SANITARIA_BAR)} bar sotto"
        )
    precarica = round(rete - SCARTO_DELLA_PRECARICA_SANITARIA_BAR, 6)
    finale = pressione_finale_sanitaria(dati.taratura_sicurezza_bar)
    if finale <= rete:
        raise ValueError(
            f"la pressione di rete ({_bar(rete)} bar) non sta sotto la pressione finale ({_bar(finale)} bar, "
            f"dalla valvola a {_bar(dati.taratura_sicurezza_bar)} bar): nessun vaso basta, serve un riduttore di "
            "pressione sull'acqua fredda"
        )
    avvisi: list[str] = []
    if finale - rete < SALTO_MINIMO_BAR:
        avvisi.append(
            f"fra la pressione di rete ({_bar(rete)} bar) e la pressione finale ({_bar(finale)} bar) resta meno "
            "di 0,3 bar: il vaso diventa enorme. Va rivisto col progettista (un riduttore di pressione, o un'altra "
            "taratura della valvola)."
        )
    nominale = volume_nominale_sanitario(volume_di_espansione, rete, precarica, finale)
    taglia = next((t for t in SERIE_DEI_VASI_SANITARI_L if t >= nominale - 1e-9), None)
    if taglia is None:
        avvisi.append(f"servono {nominale:.0f} l: oltre la serie d'uso comune, si sceglie sul catalogo del fornitore")
    return VasoSanitario(
        coefficiente=coefficiente,
        volume_di_espansione_l=volume_di_espansione,
        precarica_bar=precarica,
        pressione_finale_bar=finale,
        volume_nominale_l=nominale,
        taglia_l=taglia,
        avvisi=tuple(avvisi),
        pressione_di_rete_bar=rete,
    )


__all__ = [
    "SERIE_DEI_VASI_L",
    "SCARTO_DELLA_PRECARICA_SANITARIA_BAR",
    "SERIE_DEI_VASI_SANITARI_L",
    "DatiDelVaso",
    "DatiDelVasoSanitario",
    "Vaso",
    "VasoSanitario",
    "coefficiente_di_espansione",
    "densita_dell_acqua",
    "dimensiona_il_vaso",
    "dimensiona_il_vaso_sanitario",
    "volume_nominale_sanitario",
    "pressione_finale_sanitaria",
]
