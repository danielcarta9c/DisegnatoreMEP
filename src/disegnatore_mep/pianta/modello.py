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
- **pezzi** — le macchine e i terminali, dove li ha messi il progettista;
- **tracciati** — da pezzo a pezzo, col fluido (i nomi di `naming/media.json`),
  la tratta come nella tabella dello schema funzionale, la quota e il fascio.
  **La forma della spezzata non si dichiara**: la sceglie l'instradatore sul
  costo, come nel motore dello schema (D-161).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator

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
    """Un tracciato da instradare: da un pezzo a un altro."""

    tratta: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    """Il numero di tratta, come nella tabella dello schema funzionale: T01…"""
    da: str | Estremo
    a: str | Estremo
    fluido: Fluido
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

    @model_validator(mode="after")
    def corsia_ordinata(self) -> Parametri:
        if not self.corsia_da_m < self.corsia_a_m < self.centro_da_m:
            raise ValueError("vuole corsia_da_m < corsia_a_m < centro_da_m")
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
    sfondo: Sfondo | None = None
    pezzi: list[Pezzo] = Field(default_factory=list)
    tracciati: list[Tracciato] = Field(default_factory=list)
    maggiorazione: Maggiorazione = Field(default_factory=Maggiorazione)
    parametri: Parametri = Field(default_factory=Parametri)
    note: list[str] = Field(default_factory=list)

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
        sigle = {p.sigla for p in self.pezzi}
        for tracciato in self.tracciati:
            for capo in (tracciato.estremo_da, tracciato.estremo_a):
                if capo.pezzo not in sigle:
                    raise ValueError(
                        f"la tratta {tracciato.tratta} va al pezzo {capo.pezzo!r}, che non c'e'"
                    )
            if tracciato.estremo_da.pezzo == tracciato.estremo_a.pezzo:
                raise ValueError(f"la tratta {tracciato.tratta} comincia e finisce sullo stesso pezzo")
        return self


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
        righe = []
        for dettaglio in errore.errors():
            dove = ".".join(str(parte) for parte in dettaglio["loc"]) or "(la pianta)"
            righe.append(f"  {dove}: {dettaglio['msg']}")
        raise ErroreDellaPianta(f"{percorso}: la pianta non regge\n" + "\n".join(righe)) from None


def schema_della_pianta() -> dict[str, object]:
    """Lo schema JSON dichiarato, quello di `schemas/pianta.schema.json`."""
    return Pianta.model_json_schema()
