"""Il JSON della pianta: la planimetria, i pezzi posati e i tracciati da instradare.

Coordinate **in metri**, con l'origine in alto a sinistra, x verso destra e y
verso il basso — come il foglio del motore e come un'immagine: chi misura su un
PDF o su una scansione legge le coordinate cosi', senza ribaltarle.

Che cosa c'e' dentro, e chi lo decide:

- **muri, aperture, stanze** — la planimetria, dichiarata **in vettoriale**.
  L'instradatore li deve conoscere: anche quando c'e' uno sfondo raster (il
  catastale), i muri principali si dichiarano lo stesso;
- **sfondo** — facoltativo, un JPEG con la sua scala (px/m) e l'origine, che si
  stampa schiarito sotto il disegno;
- **zone esterne** — dove fuori dall'edificio si puo' passare: il terrazzo,
  il balcone, la facciata attrezzata. Il resto dell'esterno non e' una strada
  (collaudo T3 della 1.6.0: il cavo UI-UE faceva il giro dell'edificio, e
  l'alimentazione dell'UE usciva dalla porta di casa);
- **pezzi** — le macchine e i terminali, dove li ha messi il progettista; uno
  puo' stare sopra o sotto un altro (`sovrapposto_a`);
- **tracciati** — da pezzo a pezzo, col fluido (i nomi di `naming/media.json`),
  la tratta come nella tabella dello schema funzionale, la quota e il fascio.
  **La forma della spezzata non si dichiara**: la sceglie l'instradatore sul
  costo, come nel motore dello schema (D-161).
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, cast, get_args

from pydantic import BaseModel, Field, ValidationError, model_validator

from disegnatore_mep.model.base import FiniteFloat, StrictModel

VERSIONE = "1.0.0"

Punto = tuple[FiniteFloat, FiniteFloat]
"""Un punto della pianta, in metri: (x, y)."""

Quota = Literal["controsoffitto", "traccia", "pavimento", "a_vista"]
"""Dove corre un tracciato. `controsoffitto` paga i tratti fuori dal
controsoffitto; le altre quote non hanno preferenze di stanza."""

QUOTE: tuple[Quota, ...] = ("controsoffitto", "traccia", "pavimento", "a_vista")

Fluido = Literal[
    "supply_air",
    "return_air",
    "refrigerant_liquid",
    "refrigerant_gas",
    "condensate",
    "power_supply",
    "interconnection",
    "control_bus",
    "heating_water",
    "domestic_hot_water",
    "cold_water",
    "natural_gas",
    "solar_fluid",
]
"""I fluidi che un tracciato puo' portare: i nomi di `naming/media.json`."""

Lato = Literal["sopra", "sotto", "sinistra", "destra"]
"""Il lato di un pezzo, **sul foglio**: sopra e' verso y piu' piccola."""

PASSA_PER_TIPO: dict[str, tuple[Quota, ...]] = {
    "varco": QUOTE,
    "foro": QUOTE,
    "porta": ("traccia", "pavimento"),
    "finestra": (),
}
"""Quali quote un'apertura lascia passare senza forare, se non lo dice lei.

Una **porta** non e' un passaggio per il controsoffitto: sopra la porta c'e'
l'architrave, e un canale che passa li' fora il muro. E' il caso della M.03
del kit (il rilievo «+0,5 m per l'architrave»). Un **varco** a tutta altezza e
un **foro** dichiarato lasciano passare tutto; una **finestra** niente."""


class Muro(StrictModel):
    """Un muro: l'asse da `da` ad `a` e lo spessore, in metri."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    da: Punto
    a: Punto
    spessore: FiniteFloat = Field(gt=0, le=1.5)
    tipo: Literal["perimetrale", "portante", "tramezza"] = "tramezza"

    @model_validator(mode="after")
    def non_e_un_punto(self) -> Muro:
        if math.dist(self.da, self.a) < 1e-6:
            raise ValueError(f"il muro {self.id} ha i due capi nello stesso punto")
        return self


PORTA_DI_CASA: tuple[Quota, ...] = ()
"""Una porta nel muro **perimetrale** — la porta di casa, una portafinestra —
non lascia passare niente, se non lo dice lei (`passa`): non e' un passaggio
per i cavi, e di la' c'e' il pianerottolo o la facciata."""


class Apertura(StrictModel):
    """Una porta, un varco, una finestra o un foro, su un muro dichiarato."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    muro: str
    centro: Punto
    """Il centro dell'apertura, sull'asse del muro."""
    larghezza: FiniteFloat = Field(gt=0, le=10)
    tipo: Literal["porta", "varco", "finestra", "foro"]
    passa: list[Quota] | None = None
    """Le quote che passano senza forare; se manca, quelle del tipo
    (`PASSA_PER_TIPO`)."""
    apre_verso: Lato | None = None
    """Solo per il disegno della porta: da che parte si apre l'anta."""

    @property
    def quote_ammesse(self) -> tuple[Quota, ...]:
        """Le quote che passano senza forare, se il muro e' interno. Per il muro
        perimetrale vale `Pianta.quote_ammesse`."""
        return tuple(self.passa) if self.passa is not None else PASSA_PER_TIPO[self.tipo]


class Stanza(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    nome: str
    zona: str | None = None
    poligono: list[Punto] = Field(min_length=3)
    controsoffitto: bool = False
    disimpegno: bool = False
    """Un disimpegno e' tutto corsia: ci si passa a costo basso anche lontano
    dai muri."""


class Rettangolo(StrictModel):
    """Un rettangolo in metri: [x0, y0, x1, y1]."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    rettangolo: tuple[FiniteFloat, FiniteFloat, FiniteFloat, FiniteFloat]

    @model_validator(mode="after")
    def ordinato(self) -> Rettangolo:
        x0, y0, x1, y1 = self.rettangolo
        if not (x0 < x1 and y0 < y1):
            raise ValueError(f"{self.id}: il rettangolo vuole x0 < x1 e y0 < y1")
        return self


class ZonaEsterna(StrictModel):
    """Una zona fuori dall'edificio dove le linee possono correre: il terrazzo,
    il balcone, la facciata attrezzata. **Fuori da queste zone l'esterno non e'
    una strada**: l'instradatore ci passa solo se non ha altro, a un costo
    altissimo, e la tavola lo dice come rilievo bloccante."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    nome: str | None = None
    """Si scrive sulla tavola: «Terrazzo»."""
    rettangolo: tuple[FiniteFloat, FiniteFloat, FiniteFloat, FiniteFloat]
    """[x0, y0, x1, y1] in metri: la zona praticabile, fuori dal muro."""
    costo: FiniteFloat = Field(default=1.0, ge=1.0, le=20.0)
    """Quanto costa un passo qui, in multipli del passo lungo il muro: 1 come in
    casa; 2 o 3 se il progettista vuole che le linee fuori siano corte."""

    @model_validator(mode="after")
    def ordinato(self) -> ZonaEsterna:
        x0, y0, x1, y1 = self.rettangolo
        if not (x0 < x1 and y0 < y1):
            raise ValueError(f"la zona esterna {self.id}: il rettangolo vuole x0 < x1 e y0 < y1")
        return self


class Sfondo(StrictModel):
    """Una planimetria raster sotto il disegno: un JPEG, la sua scala, l'origine."""

    file: str
    """Il JPEG, relativo alla cartella del JSON."""
    px_per_m: FiniteFloat = Field(gt=0)
    origine_px: Punto
    """Il pixel dove cade il punto (0, 0) della pianta."""
    opacita: FiniteFloat = Field(default=0.35, gt=0, le=1)
    """Quanto si vede: lo sfondo si stampa schiarito, sotto i tracciati."""


class Pezzo(StrictModel):
    """Un pezzo posato: la sigla, che cosa e', dove sta (il centro) e quanto ingombra."""

    sigla: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    """La sigla della tavola dello schema funzionale: UI-01, SZ-01…"""
    id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    """Facoltativo: l'id del pezzo nel grafo dello schema (`sezionatore`). Un
    tracciato puo' nominare il pezzo con la sigla o con l'id."""
    tipo: str
    """Che cosa e': una voce del catalogo, o una parola."""
    nome: str | None = None
    x: FiniteFloat
    y: FiniteFloat
    larghezza: FiniteFloat = Field(gt=0, le=10)
    """Lungo x."""
    profondita: FiniteFloat = Field(gt=0, le=10)
    """Lungo y."""
    quota: Quota | None = None
    sovrapposto_a: str | None = None
    """La sigla (o l'id) del pezzo con cui questo si sovrappone **in pianta**,
    a un'altra altezza: la centrale di zona sopra il plenum, la ripresa sotto
    l'unita' interna. Allora la sovrapposizione e' ammessa e si disegna — il
    pezzo che sta sotto tratteggiato —, e le linee di ciascuno partono dal suo
    ingombro, anche attraverso quello dell'altro. Senza, due pezzi sovrapposti
    sono un rilievo bloccante."""
    sta: Literal["sopra", "sotto"] = "sopra"
    """Con `sovrapposto_a`: questo pezzo sta sopra o sotto l'altro."""
    ingombro_da_confermare: bool = False
    """Larghezza e profondita' non vengono ne' dal progettista ne' dalla scheda
    che ha indicato: sono valori dichiarati, e la tavola lo scrive in nota."""

    @property
    def rettangolo(self) -> tuple[float, float, float, float]:
        return (
            self.x - self.larghezza / 2,
            self.y - self.profondita / 2,
            self.x + self.larghezza / 2,
            self.y + self.profondita / 2,
        )


class Estremo(StrictModel):
    """Un capo di un tracciato: il pezzo e, se conta, il lato da cui si prende."""

    pezzo: str
    lato: Lato | None = None


class Tracciato(StrictModel):
    """Un tracciato da instradare: da un pezzo a un altro, attraverso gli organi
    in linea che lo schema numera nella stessa tratta."""

    tratta: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    """Il numero di tratta, come nella tabella delle tratte della distinta: T01…"""
    da: str | Estremo
    a: str | Estremo
    passa_per: list[str] = Field(default_factory=list)
    """Gli organi in linea, in ordine da `da` ad `a` (sigla o id del pezzo): il
    sezionatore fra il quadro e l'unita' esterna. Lo schema numera quadro –
    sezionatore – UE come **una** tratta: la pianta la instrada a pezzi, con un
    numero solo e una scritta sola."""
    fluido: Fluido
    lunghezza_m: FiniteFloat | None = Field(default=None, ge=0)
    """La lunghezza del progettista, la stessa del grafo dello schema
    (`lunghezza_m` della tubazione). Se c'e', la tavola quota **questa**, con la
    regola della distinta, e la misura in pianta e' un controllo."""
    lunghezza_minima_m: FiniteFloat | None = Field(default=None, ge=0)
    """Il minimo che il progettista scrive sulla tratta, come nel grafo."""
    dimensione: str | None = None
    """Ø200, 1/4", 3G2,5…: un dato del progettista, si scrive com'e'."""
    quota: Quota = "controsoffitto"
    fascio: str | None = None
    """I tracciati con lo stesso fascio corrono paralleli, a passo fisso."""
    etichetta: str | None = None
    """Se c'e', sostituisce la scritta «T03 · Ø200 · L 6 m»."""

    @property
    def estremo_da(self) -> Estremo:
        return self.da if isinstance(self.da, Estremo) else Estremo(pezzo=self.da)

    @property
    def estremo_a(self) -> Estremo:
        return self.a if isinstance(self.a, Estremo) else Estremo(pezzo=self.a)


class Maggiorazione(StrictModel):
    """La regola delle lunghezze da quotare: un parametro, non una costante.

    `L da quotare = (L misurata + aggiunta) × fattore`, per eccesso
    all'arrotondamento, mai sotto il minimo del fluido. I valori predefiniti
    sono quelli del kit aria-aria (AA-01, `lavoro/dimensionamento.py`); i
    minimi del kit erano della commessa, e si dichiarano nella pianta."""

    aggiunta_m: FiniteFloat = Field(default=1.0, ge=0)
    fattore: FiniteFloat = Field(default=1.15, ge=1)
    arrotondamento_m: FiniteFloat = Field(default=0.5, gt=0)
    minimi_m: dict[Fluido, FiniteFloat] = Field(default_factory=dict)


class Parametri(StrictModel):
    """Le misure dell'instradatore. Le lunghezze equivalenti dicono quanto
    tracciato lungo il muro vale una curva, un sormonto, una foratura.

    **Una foratura costa piu' di un sormonto**, apposta: il sormonto e' un
    incrocio sulla carta, la foratura e' lavoro in cantiere. Con i due valori
    al contrario (prima stesura, 3 m contro 2 m) un bus andava dalla centrale
    al comando passando per tre camere e quattro muri pur di non incrociare le
    linee frigo: misurato sul caso di prova, e visto sulla tavola."""

    passo_m: FiniteFloat = Field(default=0.05, ge=0.02, le=0.2)
    corsia_da_m: FiniteFloat = Field(default=0.15, gt=0)
    corsia_a_m: FiniteFloat = Field(default=0.30, gt=0)
    centro_da_m: FiniteFloat = Field(default=0.80, gt=0)
    passo_fascio_m: FiniteFloat = Field(default=0.10, gt=0)
    distacco_m: FiniteFloat = Field(default=0.10, ge=0)
    curva_m: FiniteFloat = Field(default=0.5, ge=0)
    sormonto_m: FiniteFloat = Field(default=1.5, ge=0)
    foratura_m: FiniteFloat = Field(default=4.0, ge=0)
    scarto_della_misura: FiniteFloat = Field(default=0.15, gt=0, le=1)
    """Quanto la lunghezza misurata in pianta puo' superare quella data dal
    progettista prima che la tavola lo segnali: 0,15 e' il 15 %, l'incertezza
    che la regola delle lunghezze gia' copre col suo fattore 1,15."""

    @model_validator(mode="after")
    def corsia_ordinata(self) -> Parametri:
        if not self.corsia_da_m < self.corsia_a_m < self.centro_da_m:
            raise ValueError("vuole corsia_da_m < corsia_a_m < centro_da_m")
        return self


class Dettaglio(StrictModel):
    """Un riquadro di dettaglio: una zona della pianta disegnata a scala
    maggiore su una tavola a parte, quando a 1:50 e' troppo fitta per le sue
    scritte."""

    id: str = Field(pattern=r"^[A-Z0-9]{1,3}$")
    """La lettera del dettaglio: A, B…"""
    rettangolo: tuple[FiniteFloat, FiniteFloat, FiniteFloat, FiniteFloat]
    """La zona, in metri: [x0, y0, x1, y1]."""
    scala: int = Field(default=20, ge=5, le=50)

    @model_validator(mode="after")
    def ordinato(self) -> Dettaglio:
        x0, y0, x1, y1 = self.rettangolo
        if not (x0 < x1 and y0 < y1):
            raise ValueError(f"il dettaglio {self.id}: il rettangolo vuole x0 < x1 e y0 < y1")
        return self


class Foglio(StrictModel):
    formato: Literal["A3", "A2", "A1"] | None = None
    """Se manca, il piu' piccolo che contiene pianta e colonna."""
    scala: int | None = Field(default=None, ge=10, le=500)
    """Il denominatore: 50 per 1:50. Se manca, 1:50 e poi 1:100."""


class Pianta(StrictModel):
    versione: Literal["1.0.0"] = VERSIONE
    titolo: str = "Pianta dei posizionamenti e dei tracciati"
    cartiglio: dict[str, str] = Field(default_factory=dict)
    """I campi del cartiglio Nove C: committente, indirizzo, progetto,
    numero_tavola, revisione, data (gg.mm.aaaa), commessa, disegnato,
    verificato, approvato, dicitura. La scala la scrive la tavola."""
    foglio: Foglio = Field(default_factory=Foglio)
    muri: list[Muro] = Field(default_factory=list)
    aperture: list[Apertura] = Field(default_factory=list)
    stanze: list[Stanza] = Field(default_factory=list)
    velette: list[Rettangolo] = Field(default_factory=list)
    """Tratti di controsoffitto fuori dalle stanze che ce l'hanno."""
    zone_esterne: list[ZonaEsterna] = Field(default_factory=list)
    """Dove fuori dall'edificio le linee possono correre (vedi `ZonaEsterna`)."""
    sfondo: Sfondo | None = None
    pezzi: list[Pezzo] = Field(default_factory=list)
    tracciati: list[Tracciato] = Field(default_factory=list)
    maggiorazione: Maggiorazione | None = None
    """Facoltativo, e di regola **assente**: allora la regola delle lunghezze e'
    quella della distinta (`rules/distinta/lunghezze.json`), e pianta e
    distinta danno lo stesso numero per la stessa tratta. Si dichiara solo se il
    progettista da' un'altra regola, e la tavola lo dice."""
    parametri: Parametri = Field(default_factory=Parametri)
    dettagli: list[Dettaglio] | None = None
    """I riquadri di dettaglio. Se manca, la tavola ne fa uno da se' dove le
    scritte non trovano posto a 1:50, e lo dice; `[]` li spegne."""
    note: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def sigle_al_posto_degli_id(cls, dati: object) -> object:
        """Un tracciato puo' nominare un pezzo con l'id del grafo: qui diventa la
        sigla, cosi' il resto conosce una parola sola per pezzo."""
        if not isinstance(dati, dict):
            return dati
        pezzi, tracciati = dati.get("pezzi"), dati.get("tracciati")
        if not isinstance(pezzi, list) or not isinstance(tracciati, list):
            return dati
        sigle = {p.get("sigla") for p in pezzi if isinstance(p, dict)}
        per_id = {
            p["id"]: p["sigla"] for p in pezzi
            if isinstance(p, dict) and isinstance(p.get("id"), str) and isinstance(p.get("sigla"), str)
        }

        def sigla(nome: object) -> object:
            if isinstance(nome, str) and nome not in sigle and nome in per_id:
                return per_id[nome]
            return nome

        pezzi_nuovi: list[object] = []
        for pezzo in pezzi:
            if isinstance(pezzo, dict) and isinstance(pezzo.get("sovrapposto_a"), str):
                pezzo = {**pezzo, "sovrapposto_a": sigla(pezzo["sovrapposto_a"])}
            pezzi_nuovi.append(pezzo)
        nuovi: list[object] = []
        for tracciato in tracciati:
            if isinstance(tracciato, dict):
                tracciato = dict(tracciato)
                for capo in ("da", "a"):
                    valore = tracciato.get(capo)
                    if isinstance(valore, dict) and "pezzo" in valore:
                        tracciato[capo] = {**valore, "pezzo": sigla(valore["pezzo"])}
                    elif isinstance(valore, str):
                        tracciato[capo] = sigla(valore)
                if isinstance(tracciato.get("passa_per"), list):
                    tracciato["passa_per"] = [sigla(n) for n in tracciato["passa_per"]]
            nuovi.append(tracciato)
        return {**dati, "pezzi": pezzi_nuovi, "tracciati": nuovi}

    @model_validator(mode="after")
    def coerente(self) -> Pianta:
        def unici(nomi: list[str], cosa: str) -> None:
            visti: set[str] = set()
            for nome in nomi:
                if nome in visti:
                    raise ValueError(f"{cosa} {nome!r} dichiarato due volte")
                visti.add(nome)

        unici([m.id for m in self.muri], "il muro")
        unici([a.id for a in self.aperture], "l'apertura")
        unici([s.id for s in self.stanze], "la stanza")
        unici([p.sigla for p in self.pezzi], "il pezzo")
        unici([t.tratta for t in self.tracciati], "la tratta")
        muri = {m.id: m for m in self.muri}
        for apertura in self.aperture:
            muro = muri.get(apertura.muro)
            if muro is None:
                raise ValueError(f"l'apertura {apertura.id} sta sul muro {apertura.muro!r}, che non c'e'")
            distanza, lungo = _sull_asse(muro, apertura.centro)
            if distanza > muro.spessore / 2 + 1e-6 or not (-1e-6 <= lungo <= _lunghezza(muro) + 1e-6):
                raise ValueError(
                    f"il centro dell'apertura {apertura.id} non sta sul muro {muro.id}: "
                    f"e' a {distanza:.3f} m dall'asse"
                )
        unici([p.id for p in self.pezzi if p.id is not None], "l'id di pezzo")
        unici([z.id for z in self.zone_esterne], "la zona esterna")
        sigle = {p.sigla for p in self.pezzi}
        for pezzo in self.pezzi:
            if pezzo.sovrapposto_a is None:
                continue
            if pezzo.sovrapposto_a not in sigle:
                raise ValueError(
                    f"il pezzo {pezzo.sigla} e' sovrapposto_a {pezzo.sovrapposto_a!r}, che non c'e' "
                    "(la sigla, o l'id, di un pezzo dichiarato)"
                )
            if pezzo.sovrapposto_a == pezzo.sigla:
                raise ValueError(f"il pezzo {pezzo.sigla} e' sovrapposto a se stesso")
        for tracciato in self.tracciati:
            for capo in (tracciato.estremo_da, tracciato.estremo_a):
                if capo.pezzo not in sigle:
                    raise ValueError(
                        f"la tratta {tracciato.tratta} va al pezzo {capo.pezzo!r}, che non c'e' "
                        "(un pezzo si nomina con la sigla, o con l'id dichiarato sul pezzo)"
                    )
            if tracciato.estremo_da.pezzo == tracciato.estremo_a.pezzo:
                raise ValueError(f"la tratta {tracciato.tratta} comincia e finisce sullo stesso pezzo")
            for nome in tracciato.passa_per:
                if nome not in sigle:
                    raise ValueError(
                        f"la tratta {tracciato.tratta} passa per il pezzo {nome!r}, che non c'e' "
                        "(passa_per vuole la sigla, o l'id, di pezzi dichiarati)"
                    )
            capi = [tracciato.estremo_da.pezzo, *tracciato.passa_per, tracciato.estremo_a.pezzo]
            if len(set(capi)) != len(capi):
                raise ValueError(
                    f"la tratta {tracciato.tratta} passa due volte per lo stesso pezzo: {' – '.join(capi)}"
                )
            if tracciato.passa_per and tracciato.fascio:
                raise ValueError(
                    f"la tratta {tracciato.tratta} ha sia passa_per sia fascio: un fascio corre fra "
                    "gli stessi due pezzi, senza organi in linea"
                )
        return self

    def quote_ammesse(self, apertura: Apertura) -> tuple[Quota, ...]:
        """Le quote che un'apertura lascia passare senza forare: quelle dichiarate,
        o quelle del tipo; una porta nel muro perimetrale, nessuna."""
        if apertura.passa is not None:
            return tuple(apertura.passa)
        muro = next((m for m in self.muri if m.id == apertura.muro), None)
        if apertura.tipo == "porta" and muro is not None and muro.tipo == "perimetrale":
            return PORTA_DI_CASA
        return PASSA_PER_TIPO[apertura.tipo]

    def sovrapposti(self) -> dict[str, set[str]]:
        """Per sigla, i pezzi con cui la sovrapposizione e' dichiarata (nei due versi)."""
        out: dict[str, set[str]] = {}
        for pezzo in self.pezzi:
            if pezzo.sovrapposto_a is not None:
                out.setdefault(pezzo.sigla, set()).add(pezzo.sovrapposto_a)
                out.setdefault(pezzo.sovrapposto_a, set()).add(pezzo.sigla)
        return out

    def tronchi(self, tracciato: Tracciato) -> list[tuple[Estremo, Estremo]]:
        """I tronchi di una tratta: da un capo al primo organo in linea, da li' al
        successivo, fino all'altro capo. Senza `passa_per`, un tronco solo."""
        if not tracciato.passa_per:
            return [(tracciato.estremo_da, tracciato.estremo_a)]
        tappe = [tracciato.estremo_da, *(Estremo(pezzo=n) for n in tracciato.passa_per), tracciato.estremo_a]
        return list(zip(tappe, tappe[1:], strict=False))


def _lunghezza(muro: Muro) -> float:
    return math.dist(muro.da, muro.a)


def _sull_asse(muro: Muro, punto: tuple[float, float]) -> tuple[float, float]:
    """La distanza di un punto dall'asse del muro e la sua ascissa lungo l'asse."""
    lunghezza = _lunghezza(muro)
    ux, uy = (muro.a[0] - muro.da[0]) / lunghezza, (muro.a[1] - muro.da[1]) / lunghezza
    vx, vy = punto[0] - muro.da[0], punto[1] - muro.da[1]
    return abs(vx * -uy + vy * ux), vx * ux + vy * uy


class ErroreDellaPianta(ValueError):
    """Una pianta che non si legge, detto in italiano e con il posto."""


def carica_pianta(percorso: Path) -> Pianta:
    """Legge il JSON della pianta. Un errore dice **dove** e **che cosa**."""
    try:
        dati = json.loads(percorso.read_text(encoding="utf-8"))
    except json.JSONDecodeError as errore:
        raise ErroreDellaPianta(
            f"{percorso}: non e' un JSON valido (riga {errore.lineno}): {errore.msg}"
        ) from None
    try:
        return Pianta.model_validate(dati)
    except ValidationError as errore:
        raise ErroreDellaPianta(f"{percorso}: la pianta non regge\n" + "\n".join(spiega(errore))) from None


ESEMPI: dict[str, str] = {
    "Muro": '{"id": "m-nord", "da": [0.15, 0.15], "a": [11.45, 0.15], "spessore": 0.30, "tipo": "perimetrale"}',
    "Apertura": '{"id": "porta-1", "muro": "t-corr", "centro": [2.55, 3.70], "larghezza": 0.90, "tipo": "porta"}',
    "Stanza": '{"id": "corridoio", "nome": "Disimpegno", "poligono": [[0.3, 3.75], [11.3, 3.75], '
              '[11.3, 4.85], [0.3, 4.85]], "controsoffitto": true, "disimpegno": true}',
    "Rettangolo": '{"id": "veletta-soggiorno", "rettangolo": [0.30, 4.95, 2.30, 5.45]}',
    "ZonaEsterna": '{"id": "terrazzo", "nome": "Terrazzo", "rettangolo": [0.0, 8.6, 7.4, 10.1], "costo": 1}',
    "Sfondo": '{"file": "catastale.jpg", "px_per_m": 40, "origine_px": [120, 80]}',
    "Pezzo": '{"sigla": "UI-01", "tipo": "ducted-indoor-unit", "x": 6.3, "y": 4.3, '
             '"larghezza": 1.1, "profondita": 0.73}; sopra un altro: {"sigla": "CZ-01", '
             '"tipo": "zone-controller", "x": 5.5, "y": 4.3, "larghezza": 0.25, "profondita": 0.15, '
             '"sovrapposto_a": "PLZ-01", "sta": "sopra"}',
    "Estremo": '{"pezzo": "PLZ-01", "lato": "sinistra"}',
    "Dettaglio": '{"id": "A", "rettangolo": [4.5, 3.6, 8.0, 5.2], "scala": 20}',
    "Tracciato": '{"tratta": "T10", "da": "QE-01", "a": "UE-01", "passa_per": ["SZ-01"], '
                 '"fluido": "power_supply", "dimensione": "3G4", "quota": "traccia", "lunghezza_m": 18}',
}
"""Un esempio per oggetto: l'errore lo mostra, perche' un campo sbagliato si
corregge prima guardando un oggetto giusto che leggendo lo schema."""

ATTESI: dict[str, str] = {
    "rettangolo": "[x0, y0, x1, y1] in metri, con x0 < x1 e y0 < y1",
    "poligono": "[[x, y], [x, y], …] in metri, almeno tre punti",
    "da": "la sigla di un pezzo («UI-01»), o {\"pezzo\": \"UI-01\", \"lato\": \"sotto\"}",
    "a": "la sigla di un pezzo («UE-01»), o {\"pezzo\": \"UE-01\", \"lato\": \"sopra\"}",
    "centro": "[x, y] in metri, sull'asse del muro",
    "lunghezza_m": "un numero di metri, quello del grafo dello schema",
    "passa_per": "un elenco di sigle (o id) di pezzi, in ordine: [\"SZ-01\"]",
}


def _annotazione_del_modello(annotazione: object) -> type[BaseModel] | None:
    if isinstance(annotazione, type) and issubclass(annotazione, BaseModel):
        return annotazione
    for argomento in get_args(annotazione):
        trovato = _annotazione_del_modello(argomento)
        if trovato is not None:
            return trovato
    return None


def _modello_a(percorso: Sequence[int | str]) -> type[BaseModel] | None:
    """Il modello dell'oggetto che sta in quel punto del JSON."""
    modello: type[BaseModel] | None = Pianta
    for parte in percorso:
        if modello is None:
            return None
        if isinstance(parte, int):
            continue
        if parte in modello.model_fields:
            modello = _annotazione_del_modello(modello.model_fields[parte].annotation)
        elif parte in ESEMPI:  # il ramo di un'unione: «Estremo»
            modello = cast(type[BaseModel], globals()[parte])
        elif parte == "str":
            return None
    return modello


def spiega(errore: ValidationError) -> list[str]:
    """Gli errori di pydantic detti come si correggono: il posto, il campo
    atteso, e un esempio dell'oggetto giusto."""
    righe: list[str] = []
    visti: set[str] = set()
    dettagli = errore.errors()
    # Di un'unione «sigla o oggetto» si dice il ramo che l'utente ha scritto:
    # se ha scritto un oggetto, l'errore del ramo «testo» e' rumore.
    rami_oggetto = {tuple(d["loc"][: d["loc"].index(m)]) for d in dettagli for m in ESEMPI if m in d["loc"]}
    for dettaglio in dettagli:
        if dettaglio["loc"] and dettaglio["loc"][-1] == "str" and tuple(dettaglio["loc"][:-1]) in rami_oggetto:
            continue
        loc = [p for p in dettaglio["loc"] if p not in ("str",) and p not in ESEMPI]
        dove = ".".join(str(p) for p in loc) or "(la pianta)"
        tipo = dettaglio["type"]
        campo = str(loc[-1]) if loc else ""
        genitore = loc[:-1]
        if tipo == "extra_forbidden":
            modello = _modello_a(genitore)
            campi = ", ".join(modello.model_fields) if modello else ""
            riga = f"  {dove}: il campo «{campo}» non c'e' in questo oggetto"
            if campi:
                riga += f"; i campi sono: {campi}"
            if modello is not None and modello.__name__ in ESEMPI:
                riga += f". Esempio: {ESEMPI[modello.__name__]}"
        elif tipo == "missing":
            riga = f"  {dove}: manca il campo «{campo}»"
            if campo in ATTESI:
                riga += f" (atteso: {ATTESI[campo]})"
            modello = _modello_a(genitore)
            if modello is not None and modello.__name__ in ESEMPI:
                riga += f". Esempio: {ESEMPI[modello.__name__]}"
        elif tipo == "literal_error":
            ammessi = dettaglio.get("ctx", {}).get("expected", "")
            riga = f"  {dove}: {dettaglio.get('input')!r} non e' ammesso; i valori sono {ammessi}"
        else:
            riga = f"  {dove}: {dettaglio['msg']}"
            if campo in ATTESI:
                riga += f" (atteso: {ATTESI[campo]})"
        if riga not in visti:
            visti.add(riga)
            righe.append(riga)
    return righe


def schema_della_pianta() -> dict[str, object]:
    """Lo schema JSON dichiarato, quello di `schemas/pianta.schema.json`."""
    return Pianta.model_json_schema()
