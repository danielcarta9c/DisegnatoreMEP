"""Il cartiglio Nove C: il modello ricavato dal file del PO, i dati, e il disegno.

**Il cartiglio non si inventa: e' un ingresso del progetto** (D-091). Il file e'
`assets/cartigli/Cartiglio_NoveC_A3.pdf`, nella versione che il PO ha dato il 25
settembre 2026 — «questo e' il cartiglio che usiamo per i fogli A3» (I-127) —, e
il **modello** accanto, `Cartiglio_NoveC_A3.json`, e' quel file letto: ogni
tratto, campitura e testo nel suo ordine, con il logo estratto byte per byte.
Lo scrive `examples/cartigli/build_cartiglio.py`, e una prova pretende che
rieseguirlo dia lo stesso modello: **non si corregge a mano, si rigenera**.

Tre cose questo modulo aggiunge al file, e sono le sole:

- **i dati**: da dove viene ciascun valore (`valori_del_cartiglio`). Un dato che
  il progetto non ha **non si inventa** (D-087): nella casella va «DA
  DEFINIRE», e la tavola e' una bozza (D-025);
- **la misura**: un testo che non entra nella sua casella scende di corpo fino
  al piu' piccolo che il cartiglio stesso usa per un valore, e poi va su due
  righe; se non entra nemmeno cosi', la tavola e' una bozza e lo dice;
- **il foglio**: su ogni formato il cartiglio e' quello dell'A3, a misura,
  contro l'angolo in basso a destra, e la testata corre per tutta la
  squadratura (D-184).
"""

import base64
import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from disegnatore_mep.model.base import FiniteFloat, StrictModel
from disegnatore_mep.model.project import ProjectModel

from . import metriche
from .frame import SheetFrame

PT_MM = 25.4 / 72
"""Un punto tipografico in millimetri: i corpi del cartiglio sono in punti."""

DA_DEFINIRE = "DA DEFINIRE"
"""Il valore di un campo obbligatorio che il progetto non ha (D-025)."""

NON_DATO = "ND"
"""Come «Capire» scrive un dato che il progettista non ha dato
(`skill/capire/ISTRUZIONI.md`, §3): per il cartiglio e' un dato che manca."""

SCALA_DELLO_SCHEMA = "—"
"""Lo schema funzionale non e' in scala, e il cartiglio del PO lo scrive cosi'."""

BOZZA = "BOZZA — cartiglio incompleto"
"""Il segno di una tavola con un campo da definire: sta in testata, a destra."""

FAMIGLIA = "Helvetica, Arial, Liberation Sans, sans-serif"
"""Il cartiglio e' in Helvetica; Arial e Liberation Sans hanno le stesse
larghezze (`examples/cartigli/build_metriche.py`)."""

PASSO_DEL_CORPO_PT = 0.5
"""Di quanto scende il corpo di un testo che non entra, a ogni tentativo."""

INTERLINEA = 1.2
"""La distanza fra le due righe di un testo andato a capo, in corpi.

*Scelta della sessione, non del file*: il cartiglio del PO non ha testi su due
righe, e questa e' la misura tipografica ordinaria."""

STACCO_IN_TESTATA_MM = 5.0
"""Lo spazio minimo fra la scritta di sinistra e quella di destra della testata:
e' il rientro che il file da' a tutt'e due dal bordo della squadratura."""

NomeCampo = Literal[
    "intestazione",
    "dicitura",
    "committente",
    "indirizzo",
    "progetto",
    "titolo_tavola",
    "scala",
    "data",
    "revisione",
    "commessa",
    "numero_tavola",
    "approvato",
    "verificato",
    "disegnato",
]

OBBLIGATORI: tuple[NomeCampo, ...] = (
    "committente",
    "indirizzo",
    "progetto",
    "titolo_tavola",
    "data",
    "revisione",
    "commessa",
    "numero_tavola",
)
"""I campi senza i quali la tavola non e' finale (D-025).

Fuori restano le tre firme — righe da firmare, che il file lascia vuote — e la
dicitura in testata. La scala c'e' sempre: e' quella dello schema."""

Allineamento = Literal["sinistra", "centro", "destra"]

Ancora = Literal["sinistra", "destra", "entrambe"]
"""A quale bordo della squadratura si tiene un elemento della **testata** su un
foglio piu' largo dell'A3 (D-184). Nella fascia del cartiglio non serve: la
fascia si sposta tutta insieme, contro l'angolo in basso a destra."""

Colore = Annotated[str, Field(pattern=r"^#[0-9a-f]{6}$")]


class Tratto(StrictModel):
    """Una linea o il contorno di un rettangolo, come il file li disegna."""

    tipo: Literal["tratto"] = "tratto"
    forma: Literal["linea", "rettangolo"]
    x1_mm: FiniteFloat
    y1_mm: FiniteFloat
    x2_mm: FiniteFloat
    y2_mm: FiniteFloat
    colore: Colore
    spessore_mm: FiniteFloat = Field(gt=0)
    ancora: Ancora = "sinistra"


class Campitura(StrictModel):
    """Un rettangolo pieno: le fasce blu e la riga turchese."""

    tipo: Literal["campitura"] = "campitura"
    x_mm: FiniteFloat
    y_mm: FiniteFloat
    larghezza_mm: FiniteFloat = Field(gt=0)
    altezza_mm: FiniteFloat = Field(gt=0)
    colore: Colore
    opacita: FiniteFloat = Field(default=1.0, gt=0, le=1)


class Testo(StrictModel):
    """Un testo fisso: le etichette delle caselle.

    `x_mm` e' il punto d'aggancio secondo l'allineamento — l'inizio, il centro o
    la fine della riga —, `y_mm` la linea di base."""

    tipo: Literal["testo"] = "testo"
    testo: str = Field(min_length=1)
    x_mm: FiniteFloat
    y_mm: FiniteFloat
    corpo_pt: FiniteFloat = Field(gt=0)
    grassetto: bool
    colore: Colore
    opacita: FiniteFloat = Field(default=1.0, gt=0, le=1)
    allineamento: Allineamento = "sinistra"
    ancora: Ancora = "sinistra"


class Campo(StrictModel):
    """Il posto di un valore: dove il file ha il segnaposto, con la sua casella."""

    tipo: Literal["campo"] = "campo"
    campo: NomeCampo
    x_mm: FiniteFloat
    y_mm: FiniteFloat
    corpo_pt: FiniteFloat = Field(gt=0)
    corpo_minimo_pt: FiniteFloat = Field(gt=0)
    grassetto: bool
    colore: Colore
    opacita: FiniteFloat = Field(default=1.0, gt=0, le=1)
    allineamento: Allineamento = "sinistra"
    ancora: Ancora = "sinistra"
    larghezza_mm: FiniteFloat | None = None
    """Quanto e' larga la casella per il valore, al netto del rientro. `None`
    per i due campi della testata, che si misurano l'uno contro l'altro."""
    a_capo: bool = False
    etichetta_y_mm: FiniteFloat | None = None
    """La linea di base dell'etichetta sopra il valore: la prima di due righe
    non la raggiunge."""
    segnaposto: str
    """Il testo che il file ha in quel posto; vuoto se il posto e' della sessione."""
    origine: Literal["file", "sessione"]
    """Da dove viene il posto: misurato sul file, o aggiunto dalla sessione —
    i nomi sulle righe delle firme, che il file lascia vuote."""
    modello: str | None = None
    """Per l'intestazione: la scritta del file, con `{commessa}` al posto della
    commessa."""


class Logo(StrictModel):
    """Il logo, estratto dal file byte per byte: un JPEG, su fondo bianco."""

    tipo: Literal["logo"] = "logo"
    file: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    x_mm: FiniteFloat
    y_mm: FiniteFloat
    larghezza_mm: FiniteFloat = Field(gt=0)
    altezza_mm: FiniteFloat = Field(gt=0)
    pixel_larghezza: int = Field(gt=0)
    pixel_altezza: int = Field(gt=0)


Elemento = Annotated[Tratto | Campitura | Testo | Campo | Logo, Field(discriminator="tipo")]


class Ingombro(StrictModel):
    x_mm: FiniteFloat
    y_mm: FiniteFloat
    larghezza_mm: FiniteFloat = Field(gt=0)
    altezza_mm: FiniteFloat = Field(gt=0)

    @property
    def destra_mm(self) -> float:
        return self.x_mm + self.larghezza_mm

    @property
    def fondo_mm(self) -> float:
        return self.y_mm + self.altezza_mm


class Zona(StrictModel):
    """Una parte del cartiglio, con gli elementi **nell'ordine in cui il file li
    dipinge**: la riga turchese copre mezzo filetto della fascia, e l'ordine e'
    parte del disegno."""

    ingombro: Ingombro
    elementi: list[Elemento]


class Fonte(StrictModel):
    file: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    input: str = Field(min_length=1)
    generatore: str = Field(min_length=1)


class ModelloDelCartiglio(StrictModel):
    fonte: Fonte
    foglio_larghezza_mm: FiniteFloat = Field(gt=0)
    foglio_altezza_mm: FiniteFloat = Field(gt=0)
    squadratura: Tratto
    testata: Zona
    fascia: Zona
    altezza_maiuscole_em: FiniteFloat = Field(gt=0, lt=1)
    """L'altezza delle maiuscole in em, dai caratteri incorporati nel file:
    serve a sapere dove arriva in alto la prima di due righe."""
    larghezze_nel_file: dict[str, dict[str, int]]
    """Le larghezze dei caratteri Arial incorporati nel file, per ogni carattere
    che il file usa: il riscontro di `metriche`."""

    def campi(self) -> list[Campo]:
        return [
            item
            for zona in (self.testata, self.fascia)
            for item in zona.elementi
            if isinstance(item, Campo)
        ]

    def logo(self) -> Logo:
        loghi = [item for item in self.fascia.elementi if isinstance(item, Logo)]
        if len(loghi) != 1:
            raise ValueError(f"il cartiglio deve avere un logo, e ne ha {len(loghi)}")
        return loghi[0]


@dataclass(frozen=True)
class Cartiglio:
    """Il modello con il suo logo, letti e controllati."""

    modello: ModelloDelCartiglio
    logo_jpeg: bytes

    @classmethod
    def da_file(cls, path: Path) -> "Cartiglio":
        modello = ModelloDelCartiglio.model_validate_json(path.read_text(encoding="utf-8"))
        logo = modello.logo()
        dati = (path.parent / logo.file).read_bytes()
        if hashlib.sha256(dati).hexdigest() != logo.sha256:
            raise ValueError(
                f"{logo.file} non e' il logo che il modello dichiara: si rigenera "
                f"con examples/cartigli/build_cartiglio.py, non si sostituisce a mano"
            )
        return cls(modello=modello, logo_jpeg=dati)


def _dato(valore: str | None) -> str | None:
    if valore is None or valore.strip().upper() == NON_DATO:
        return None
    return valore


def valori_del_cartiglio(project: ProjectModel, sheet_id: str) -> dict[NomeCampo, str | None]:
    """Il valore di ogni campo per una tavola; `None` dove il progetto non l'ha.

    Il titolo e il numero sono della tavola: se il progetto dichiara le proprie
    tavole valgono i suoi, altrimenti quelli dei metadati."""
    meta = project.metadata
    dichiarata = next((item for item in project.sheets if item.id == sheet_id), None)
    titolo = dichiarata.title if dichiarata is not None else meta.sheet_title
    numero = dichiarata.number if dichiarata is not None else meta.sheet_number
    revisione = _dato(meta.revision)
    return {
        "intestazione": None,
        "dicitura": _dato(meta.header_note),
        "committente": _dato(meta.client),
        "indirizzo": _dato(meta.address),
        "progetto": _dato(meta.project_name),
        "titolo_tavola": _dato(titolo),
        "scala": SCALA_DELLO_SCHEMA,
        "data": meta.issue_date.strftime("%d.%m.%Y"),
        "revisione": None if revisione is None else f"Rev. {revisione}",
        "commessa": _dato(meta.commission_code),
        "numero_tavola": _dato(numero),
        "approvato": _dato(meta.approved_by),
        "verificato": _dato(meta.checked_by),
        "disegnato": _dato(meta.drawn_by),
    }


@dataclass(frozen=True)
class CartiglioDellaTavola:
    """Il cartiglio di una tavola: il modello e i valori di quella tavola.

    Con `come_nel_file` ogni campo porta il segnaposto del file, e la testata la
    scritta del file: e' il cartiglio **com'e' nel PDF del PO**, e serve a
    confrontarli (criterio 1 di `REL-002`)."""

    cartiglio: Cartiglio
    valori: Mapping[NomeCampo, str | None]
    come_nel_file: bool = False

    @classmethod
    def del_file(cls, cartiglio: Cartiglio) -> "CartiglioDellaTavola":
        return cls(cartiglio=cartiglio, valori={}, come_nel_file=True)

    @property
    def mancanti(self) -> tuple[NomeCampo, ...]:
        if self.come_nel_file:
            return ()
        return tuple(nome for nome in OBBLIGATORI if self.valori.get(nome) is None)

    def testo(self, campo: Campo) -> str:
        """Quello che si scrive nel campo: il valore, «DA DEFINIRE», o niente."""
        if self.come_nel_file:
            return campo.segnaposto
        if campo.campo == "intestazione":
            commessa = self.valori.get("commessa") or DA_DEFINIRE
            return (campo.modello or "").replace("{commessa}", commessa)
        valore = self.valori.get(campo.campo)
        if valore is not None:
            return valore
        return DA_DEFINIRE if campo.campo in OBBLIGATORI else ""


def larghezza_mm(testo: str, corpo_pt: float, grassetto: bool) -> float:
    """Quanto e' lungo un testo stampato, dalle larghezze di Helvetica.

    Un carattere fuori tabella conta come il piu' largo: meglio un testo che
    scende di corpo senza bisogno che uno che esce dalla casella."""
    tabella = metriche.GRASSETTO if grassetto else metriche.NORMALE
    ignoto = max(tabella.values())
    return sum(tabella.get(carattere, ignoto) for carattere in testo) / 1000 * corpo_pt * PT_MM


@dataclass(frozen=True)
class Impaginato:
    corpo_pt: float
    righe: tuple[str, ...]


def _due_righe(testo: str, corpo_pt: float, grassetto: bool, larghezza: float) -> tuple[str, ...]:
    parole = testo.split(" ")
    for taglio in range(len(parole) - 1, 0, -1):
        prima, seconda = " ".join(parole[:taglio]), " ".join(parole[taglio:])
        if larghezza_mm(prima, corpo_pt, grassetto) <= larghezza:
            if larghezza_mm(seconda, corpo_pt, grassetto) <= larghezza:
                return (prima, seconda)
            return ()
    return ()


def impagina(
    testo: str, campo: Campo, altezza_maiuscole_em: float, larghezza: float | None = None
) -> Impaginato | None:
    """Come il testo entra nella casella; `None` se non entra.

    Prima scende di corpo, mezzo punto alla volta, fino al corpo minimo del
    campo; poi, se il campo lo ammette, va su due righe a corpo minimo — la
    seconda sulla linea di base del file, la prima sopra, senza toccare
    l'etichetta."""
    spazio = campo.larghezza_mm if larghezza is None else larghezza
    if spazio is None:
        raise ValueError(f"il campo {campo.campo} non ha una larghezza")
    corpo = campo.corpo_pt
    while corpo >= campo.corpo_minimo_pt - 1e-9:
        if larghezza_mm(testo, corpo, campo.grassetto) <= spazio:
            return Impaginato(corpo_pt=corpo, righe=(testo,))
        corpo -= PASSO_DEL_CORPO_PT
    if not campo.a_capo:
        return None
    corpo = campo.corpo_minimo_pt
    altezza = corpo * PT_MM
    cima = campo.y_mm - INTERLINEA * altezza - altezza_maiuscole_em * altezza
    if campo.etichetta_y_mm is not None and cima <= campo.etichetta_y_mm:
        return None
    righe = _due_righe(testo, corpo, campo.grassetto, spazio)
    return Impaginato(corpo_pt=corpo, righe=righe) if righe else None


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _spazi(text: str) -> str:
    """Gli spazi che contano restano spazi su qualunque visualizzatore.

    La testata del file ha **due** spazi attorno a ogni barra, e un SVG compatta
    gli spazi di fila se il visualizzatore non rispetta `xml:space` — MuPDF, per
    esempio. Ogni spazio seguito da un altro diventa uno spazio non separabile,
    che in Helvetica e' largo uguale."""
    return re.sub(r" (?= )", "\u00a0", text)


_ANCHOR = {"sinistra": "start", "centro": "middle", "destra": "end"}


def _testo_svg(
    testo: str,
    x: float,
    y: float,
    corpo_pt: float,
    grassetto: bool,
    colore: str,
    opacita: float,
    allineamento: Allineamento,
) -> str:
    peso = ' font-weight="bold"' if grassetto else ""
    velo = "" if opacita == 1 else f' fill-opacity="{opacita:g}"'
    return (
        f'<text x="{x:g}" y="{y:g}" font-family="{FAMIGLIA}" '
        f'font-size="{round(corpo_pt * PT_MM, 4):g}"{peso} fill="{colore}"{velo} '
        f'text-anchor="{_ANCHOR[allineamento]}">{_escape(_spazi(testo))}</text>'
    )


ETICHETTA: dict[NomeCampo, str] = {
    "intestazione": "testata",
    "dicitura": "dicitura in testata",
    "committente": "COMMITTENTE",
    "indirizzo": "INDIRIZZO",
    "progetto": "PROGETTO",
    "titolo_tavola": "TITOLO TAVOLA",
    "scala": "SCALA",
    "data": "DATA",
    "revisione": "REVISIONE",
    "commessa": "COMMESSA",
    "numero_tavola": "TAVOLA",
    "approvato": "APPROVATO",
    "verificato": "VERIFICATO",
    "disegnato": "DISEGNATO",
}
"""Come si chiama un campo sulla tavola: l'etichetta della sua casella."""


@dataclass(frozen=True)
class CartiglioDisegnato:
    svg: str
    fuori_misura: tuple[NomeCampo, ...]
    """I campi il cui testo non entra nella casella nemmeno su due righe."""
    bozza: bool
    """Vero se la tavola porta il segno di bozza: un campo da definire, o un
    testo che non entra (D-025)."""


def disegna_cartiglio(
    tavola: CartiglioDellaTavola, frame: SheetFrame, stati: Sequence[str] = ()
) -> CartiglioDisegnato:
    """La squadratura, la testata e la fascia del cartiglio, compilate.

    `stati` sono i segni che la tavola porta in testata — la modalita' di
    verifica —; la bozza la aggiunge questa funzione, quando serve. I testi si
    misurano **prima** di disegnare: il segno di bozza sta in testata, e deve
    sapere anche di un valore che non entra nella fascia."""
    modello = tavola.cartiglio.modello
    bordo = frame.border_rect_mm
    riquadro = modello.squadratura
    a_sinistra = bordo.x_mm - min(riquadro.x1_mm, riquadro.x2_mm)
    a_destra = bordo.right_mm - max(riquadro.x1_mm, riquadro.x2_mm)
    in_alto = bordo.y_mm - min(riquadro.y1_mm, riquadro.y2_mm)
    fascia = modello.fascia.ingombro
    dx = bordo.right_mm - fascia.destra_mm
    dy = bordo.bottom_mm - fascia.fondo_mm
    if fascia.x_mm + dx < bordo.x_mm - 1e-6:
        raise ValueError(
            f"il cartiglio e' largo {fascia.larghezza_mm:g} mm e la squadratura di questo "
            f"foglio {bordo.width_mm:g}: non lo contiene, e il cartiglio non si "
            f"rimpicciolisce (D-184)"
        )

    # 1. Si misura.
    fuori: list[NomeCampo] = []
    impaginati: list[tuple[Campo, Impaginato]] = []
    for item in modello.fascia.elementi:
        if not isinstance(item, Campo):
            continue
        testo = tavola.testo(item)
        if not testo:
            continue
        impaginato = impagina(testo, item, modello.altezza_maiuscole_em)
        if impaginato is None:
            # Non entra nemmeno su due righe: si scrive a corpo minimo, e la
            # tavola e' una bozza che lo dice. Tagliarlo sarebbe perdere il dato.
            fuori.append(item.campo)
            impaginato = Impaginato(corpo_pt=item.corpo_minimo_pt, righe=(testo,))
        impaginati.append((item, impaginato))
    marchi = list(stati)
    if tavola.mancanti or fuori:
        marchi.append(BOZZA)
    if not _testata_entra(tavola, modello, a_sinistra, a_destra, marchi):
        fuori.append("dicitura")
        if BOZZA not in marchi:
            marchi.append(BOZZA)

    parti: list[str] = [
        f'<g class="cartiglio" data-fonte="{_escape(modello.fonte.file)}">',
        f'<rect class="squadratura" x="{bordo.x_mm:g}" y="{bordo.y_mm:g}" '
        f'width="{bordo.width_mm:g}" height="{bordo.height_mm:g}" fill="none" '
        f'stroke="{riquadro.colore}" stroke-width="{riquadro.spessore_mm:g}"/>',
        '<g class="testata">',
    ]

    # 2. La testata: ogni elemento si tiene al proprio bordo (D-184).
    def x_in_testata(x: float, ancora: Ancora) -> float:
        return x + (a_destra if ancora == "destra" else a_sinistra)

    for item in modello.testata.elementi:
        if isinstance(item, Tratto):
            destra = a_destra if item.ancora in ("destra", "entrambe") else a_sinistra
            parti.append(
                f'<line x1="{item.x1_mm + a_sinistra:g}" y1="{item.y1_mm + in_alto:g}" '
                f'x2="{item.x2_mm + destra:g}" y2="{item.y2_mm + in_alto:g}" '
                f'stroke="{item.colore}" stroke-width="{item.spessore_mm:g}"/>'
            )
        elif isinstance(item, Testo):
            parti.append(
                _testo_svg(
                    item.testo, x_in_testata(item.x_mm, item.ancora), item.y_mm + in_alto,
                    item.corpo_pt, item.grassetto, item.colore, item.opacita, item.allineamento,
                )
            )
        elif isinstance(item, Campo):
            x = x_in_testata(item.x_mm, item.ancora)
            testo = tavola.testo(item)
            if testo:
                parti.append(
                    _testo_svg(
                        testo, x, item.y_mm + in_alto, item.corpo_pt, item.grassetto,
                        item.colore, item.opacita, item.allineamento,
                    )
                )
            if item.campo == "dicitura" and marchi:
                # I segni di stato stanno accanto alla dicitura, nel suo corpo,
                # in neretto e nel colore dei valori: si devono vedere.
                if testo:
                    x -= larghezza_mm(testo + SEPARATORE, item.corpo_pt, item.grassetto)
                parti.append(
                    _testo_svg(
                        SEPARATORE.join(marchi), x, item.y_mm + in_alto, item.corpo_pt,
                        True, _colore_dei_valori(modello, item.colore), 1.0, item.allineamento,
                    )
                )
    parti.append("</g>")

    # 3. La fascia: tutta insieme, contro l'angolo in basso a destra (D-184).
    parti.append(f'<g class="fascia" transform="translate({dx:g} {dy:g})">')
    scritti = dict((id(item), impaginato) for item, impaginato in impaginati)
    for item in modello.fascia.elementi:
        if isinstance(item, Tratto):
            parti.append(_tratto_svg(item))
        elif isinstance(item, Campitura):
            velo = "" if item.opacita == 1 else f' fill-opacity="{item.opacita:g}"'
            parti.append(
                f'<rect x="{item.x_mm:g}" y="{item.y_mm:g}" width="{item.larghezza_mm:g}" '
                f'height="{item.altezza_mm:g}" fill="{item.colore}"{velo} stroke="none"/>'
            )
        elif isinstance(item, Logo):
            dati = base64.b64encode(tavola.cartiglio.logo_jpeg).decode("ascii")
            parti.append(
                f'<image xmlns:xlink="http://www.w3.org/1999/xlink" x="{item.x_mm:g}" '
                f'y="{item.y_mm:g}" width="{item.larghezza_mm:g}" '
                f'height="{item.altezza_mm:g}" preserveAspectRatio="none" '
                f'xlink:href="data:image/jpeg;base64,{dati}"/>'
            )
        elif isinstance(item, Testo):
            parti.append(
                _testo_svg(
                    item.testo, item.x_mm, item.y_mm, item.corpo_pt, item.grassetto,
                    item.colore, item.opacita, item.allineamento,
                )
            )
        elif id(item) in scritti:
            impaginato = scritti[id(item)]
            passo = INTERLINEA * impaginato.corpo_pt * PT_MM
            for indice, riga in enumerate(impaginato.righe):
                su = (len(impaginato.righe) - 1 - indice) * passo
                parti.append(
                    _testo_svg(
                        riga, item.x_mm, round(item.y_mm - su, 4), impaginato.corpo_pt,
                        item.grassetto, item.colore, item.opacita, item.allineamento,
                    )
                )
    parti.append("</g></g>")
    return CartiglioDisegnato(
        svg="".join(parti), fuori_misura=tuple(fuori), bozza=BOZZA in marchi
    )


SEPARATORE = " · "
"""Fra due segni di stato in testata, e fra i segni e la dicitura."""


def rilievi_del_cartiglio(
    tavola: CartiglioDellaTavola, frame: SheetFrame, stati: Sequence[str] = ()
) -> list[str]:
    """Quello che il comando dice del cartiglio di una tavola, in italiano."""
    disegnato = disegna_cartiglio(tavola, frame, stati)
    rilievi: list[str] = []
    if tavola.mancanti:
        rilievi.append(
            "campi da definire: "
            + ", ".join(ETICHETTA[nome] for nome in tavola.mancanti)
            + " — nella casella c'e' «DA DEFINIRE» e la tavola esce in bozza (D-025)"
        )
    for nome in disegnato.fuori_misura:
        rilievi.append(
            f"il testo di {ETICHETTA[nome]} non entra nella sua casella nemmeno su due "
            f"righe: e' scritto intero, a corpo minimo, e la tavola esce in bozza"
        )
    return rilievi


def _tratto_svg(item: Tratto) -> str:
    if item.forma == "linea":
        return (
            f'<line x1="{item.x1_mm:g}" y1="{item.y1_mm:g}" x2="{item.x2_mm:g}" '
            f'y2="{item.y2_mm:g}" stroke="{item.colore}" stroke-width="{item.spessore_mm:g}"/>'
        )
    return (
        f'<rect x="{min(item.x1_mm, item.x2_mm):g}" y="{min(item.y1_mm, item.y2_mm):g}" '
        f'width="{abs(item.x2_mm - item.x1_mm):g}" height="{abs(item.y2_mm - item.y1_mm):g}" '
        f'fill="none" stroke="{item.colore}" stroke-width="{item.spessore_mm:g}"/>'
    )


def _colore_dei_valori(modello: ModelloDelCartiglio, ripiego: str) -> str:
    """Il colore dei valori della fascia: quello del committente nel file."""
    for item in modello.fascia.elementi:
        if isinstance(item, Campo) and item.campo == "committente":
            return item.colore
    return ripiego


def _testata_entra(
    tavola: CartiglioDellaTavola,
    modello: ModelloDelCartiglio,
    a_sinistra: float,
    a_destra: float,
    marchi: Sequence[str],
) -> bool:
    """Vero se la scritta di sinistra e quella di destra della testata non si
    avvicinano piu' del rientro che il file da' a tutt'e due."""
    campi = {item.campo: item for item in modello.testata.elementi if isinstance(item, Campo)}
    sinistra, destra = campi.get("intestazione"), campi.get("dicitura")
    if sinistra is None or destra is None:
        return True
    fine = sinistra.x_mm + a_sinistra + larghezza_mm(
        tavola.testo(sinistra), sinistra.corpo_pt, sinistra.grassetto
    )
    dicitura = tavola.testo(destra)
    lunghezza = larghezza_mm(dicitura, destra.corpo_pt, destra.grassetto) if dicitura else 0.0
    if marchi:
        separatore = SEPARATORE if dicitura else ""
        lunghezza += larghezza_mm(separatore, destra.corpo_pt, destra.grassetto)
        lunghezza += larghezza_mm(SEPARATORE.join(marchi), destra.corpo_pt, True)
    inizio = destra.x_mm + a_destra - lunghezza
    return fine + STACCO_IN_TESTATA_MM <= inizio
