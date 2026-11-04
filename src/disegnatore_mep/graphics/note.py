"""Le note di posa, in un riquadro in alto a destra della tabella (REL-011).

Il PO, il 4 novembre 2026 (I-263): «magari mettiamo una sezione note in alto a
destra (tanto quello spazio è sempre bianco) a destra della tabella per capirci. e
nelle note mettiamo queste piccole raccomandazioni di posa (senza esagerare solo
cose che obiettivamente non sono state specificate in tavola […])». E lo stesso
giorno (I-264): «si ok solo nel esecutivo-costruttivo». Sono **D-231** e **D-232**.

Questo modulo fa tre cose, come la tabella (`graphics.tabella`), e anche qui il
posto sul foglio lo sgombra l'esecutore del piano (`layout.compose.sgombra_la_tabella`):

- **che cosa dice** (`note_di_posa`): al massimo cinque note, **solo nel progetto
  esecutivo-costruttivo** (`ProjectMetadata.livello`). Ciascuna la genera il suo
  pezzo, ed esce solo se il pezzo e' sulla tavola; il progettista ne aggiunge di sue,
  che vengono prima e prendono il posto di quelle sullo stesso soggetto, o ne toglie
  (REL-017, I-271). Nel definitivo — o senza livello — il riquadro non esiste e la
  tavola resta quella di prima, byte per byte;
- **quanto e' grande e dove sta** (`impagina_le_note`): in cima all'area del
  disegno, a destra della tabella, largo quanto serve fino a un massimo, e mai
  sopra la fascia della legenda;
- **come si disegna** (`tratti_delle_note`): un riquadro al tratto sottile della
  tabella, il titolo «NOTE» in neretto nella riga alta quanto l'intestazione della
  tabella, le note numerate, a capo fra le parole. L'SVG e il DXF scrivono dalle
  stesse linee e dagli stessi testi.

Il testo delle note passa per le sostituzioni dichiarate del PDF
(`pdf.per_winansi`) **prima** di essere misurato e scritto, come le tabelle nelle
zone: «≤» e «λ» WinAnsi non li ha, e SVG, PDF e DXF portano lo stesso testo.

Le parole delle note, la larghezza del riquadro e i suoi stacchi sono **proposte
della sessione**, da giudicare sulla tavola (D-146).
"""

from collections.abc import Iterable

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.diametri.tubi import Tubo
from disegnatore_mep.layout.geometry import (
    STACCO_DALLA_TABELLA_MM,
    RiquadroDelleNote,
    TabellaDelleApparecchiature,
)
from disegnatore_mep.model.project import ProjectModel, SoggettoDellaNota

from .cartiglio import PT_MM, larghezza_mm
from .frame import SheetFrame
from .pdf import per_winansi
from .standard import GraphicStandard
from .tabella import (
    MARGINE_DELLA_RIGA_MM,
    MEZZE_MAIUSCOLE_EM,
    PASSO_DELLE_RIGHE_MM,
    RIENTRO_MM,
    TestoDellaTabella,
    TrattiDellaTabella,
    altezza_della_riga_mm,
    svg_dei_tratti,
)
from .tabelle import ALTEZZA_MAIUSCOLE_EM, INTERLINEA_EM, _a_capo

ESECUTIVO = "esecutivo"
"""Il livello del progetto in cui le note escono (D-232): l'esecutivo-costruttivo."""

ACQUA_DI_RISCALDAMENTO = "heating_water"
"""Il fluido delle tubazioni di cui le note parlano: l'acqua dell'impianto."""

TITOLO = "NOTE"

NOTA_ISOLAMENTO = (
    "Isolamento delle tubazioni a celle chiuse, conduttività massima 0,040 W/mK, con gli spessori minimi "
    "dell'Allegato B del DPR 412/93: 30 mm per diametri esterni da 20 a 39 mm, 40 mm da "
    "40 a 59 mm; all'esterno spessore pieno e protezione anti-UV."
)
"""(1) Lo spessore dell'isolante, che la tavola non dice (specifica Nove C Rev. 01
§5.3). Esce su ogni tavola con tubazioni d'acqua dell'impianto. Questo e' il testo
generico, per le fasce: quando la tavola porta i tubi, la nota dice lo spessore di
ciascuno (`nota_dell_isolamento`, I-279)."""

SPESSORI_DPR_412: tuple[tuple[float, int], ...] = (
    (20.0, 20),
    (40.0, 30),
    (60.0, 40),
    (80.0, 50),
    (100.0, 55),
)
"""Gli spessori minimi dell'isolante dell'Allegato B del DPR 412/93, tabella 1, per una
conduttivita' di 0,040 W/mK, per **diametro esterno** del tubo: sotto 20 mm 20 mm; da 20
a 39 mm 30; da 40 a 59 mm 40; da 60 a 79 mm 50; da 80 a 99 mm 55; da 100 mm in su 60.
Ogni coppia e' (diametro esterno fino a cui vale, spessore); oltre l'ultima, 60 mm.
Riscontrata sulla riga 0,040 della tabella riportata da una fonte secondaria (SRC-057),
non sul testo della Gazzetta Ufficiale."""

SPESSORE_OLTRE_MM = 60


def spessore_dell_isolante_mm(esterno_mm: float) -> int:
    """Lo spessore minimo dell'isolante per un tubo di questo diametro esterno (DPR
    412/93, Allegato B, λ 0,040 W/mK)."""
    for fino_a, spessore in SPESSORI_DPR_412:
        if esterno_mm < fino_a:
            return spessore
    return SPESSORE_OLTRE_MM


def nota_dell_isolamento(tubi: Iterable[Tubo], anche_altri: bool = False) -> str:
    """La nota (1) sui tubi veri della tavola (I-279): «MS 32×3: 30 mm», lo spessore di
    ciascuno dal suo diametro esterno. Senza tubi noti, il testo generico. Con
    `anche_altri` — tubazioni d'acqua della tavola senza un tubo noto: una rete dove i
    diametri non sono chiesti — anche le due fasce del testo generico, per quelle."""
    visti = {tubo.scritta: tubo for tubo in tubi}
    if not visti:
        return NOTA_ISOLAMENTO
    ordinati = sorted(visti.values(), key=lambda tubo: (tubo.materiale, tubo.esterno_mm))
    elenco = "; ".join(f"{tubo.scritta}: {spessore_dell_isolante_mm(tubo.esterno_mm)} mm" for tubo in ordinati)
    if anche_altri:
        elenco += "; le altre: 30 mm da 20 a 39 mm, 40 mm da 40 a 59 mm"
    return (
        "Isolamento delle tubazioni a celle chiuse, conduttività massima 0,040 W/mK, con gli spessori minimi "
        f"dell'Allegato B del DPR 412/93 sul diametro esterno ({elenco}); all'esterno spessore pieno e "
        "protezione anti-UV."
    )

NOTA_ANTIGELO = (
    "Valvole antigelo nel punto più basso del tratto esterno, con lo scarico libero dove "
    "l'acqua non fa danni."
)
"""(2) Dove va davvero la valvola antigelo (D-230): esce se sulla tavola c'e' un pezzo
che fa la protezione antigelo."""

NOTA_SFIATI_E_SCARICHI = (
    "Valvole di sfogo aria automatiche in tutti i punti alti e rubinetti di scarico in "
    "tutti i punti bassi del circuito."
)
"""(3) Sfiati e scarichi nei punti alti e bassi, che lo schema funzionale non mostra
(manuale Shenling §6.1, specifica §2.4): esce con un generatore sull'acqua
dell'impianto."""

NOTA_VASO = "La valvola sotto il vaso d'espansione si blocca aperta (maniglia tolta o lucchetto)."
"""(4) Al posto di un segno nuovo per la valvola bloccata aperta (I-220): esce con un
vaso d'espansione sull'acqua dell'impianto."""

NOTA_SONDA_DEL_VOLANO = "Sonda del volano (T_BT) nel pozzetto a metà altezza."
"""(5) Dove sta la sonda dell'accumulo: esce con un generatore e un accumulo."""

IN_CASCATA = " In cascata sonde e comando solo sulla macchina principale."
"""Quello che la nota (5) aggiunge con due generatori o piu'."""

SOGGETTI: tuple[SoggettoDellaNota, ...] = ("isolamento", "antigelo", "sfiati", "vaso", "sonda")
"""Il soggetto di ciascuna delle cinque note, nell'ordine (REL-017, I-271): una nota del
progettista che **comincia con questa parola** — «Isolamento: tratto interrato…» — prende il
posto della nota generata, e `metadata.note_tolte` la toglie senza sostituirla."""

MASSIMO_DELLE_NOTE = 5
"""Al massimo cinque (D-232): «non esageriamo ovviamente altrimenti diventa una tavola
di tutte note» (I-263)."""

LARGHEZZA_MINIMA_MM = 60.0
"""Sotto questa larghezza, a destra della tabella, le note andrebbero a capo a ogni
due parole: il riquadro passa **sotto** la tabella, contro la squadratura."""

STACCO_DALLA_LEGENDA_MM = 2.5
"""Fra il riquadro e la fascia della legenda: un passo di griglia."""

STACCO_FRA_LE_NOTE_EM = 0.45
"""Lo spazio in piu' fra due note, in corpi: separa le note senza una linea."""


def _sull_acqua_dell_impianto(voce: ComponentDefinition) -> bool:
    return any(porta.medium == ACQUA_DI_RISCALDAMENTO for porta in voce.ports)


def note_di_posa(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    sul_foglio: Iterable[str],
    reti_sul_foglio: Iterable[str],
    tubi: Iterable[Tubo] = (),
    anche_altri: bool = False,
) -> list[str]:
    """Le note di posa di una tavola, nell'ordine in cui si numerano.

    `sul_foglio` sono i pezzi disegnati sulla tavola, `reti_sul_foglio` le reti
    delle sue tubazioni. **Vuote nel definitivo**, o senza livello (D-232), e vuote
    su una tavola senza tubazioni d'acqua dell'impianto — la tavola dell'elettrico
    e del comando, una tavola dell'aria: le cinque note parlano tutte del circuito
    dell'acqua. Ciascuna esce solo se il suo pezzo e' sulla tavola. `tubi` sono i
    tubi d'acqua della tavola, del calcolo o del progettista: la nota dell'isolamento
    dice lo spessore di ciascuno (I-279), e con `anche_altri` le fasce per le tubazioni
    d'acqua della tavola che un tubo noto non l'hanno.

    **Le note del progettista** (`metadata.note_di_posa`, REL-017, I-271) vengono prima,
    nel suo ordine, sulle stesse tavole e solo nell'esecutivo; una sua nota che comincia
    con il soggetto di una generata (`SOGGETTI`) ne prende il posto, e
    `metadata.note_tolte` toglie una generata senza sostituirla. Il tetto resta cinque."""
    if modello.metadata.livello != ESECUTIVO:
        return []
    fluido = {rete.id: rete.medium for rete in modello.networks}
    if not any(fluido.get(rete) == ACQUA_DI_RISCALDAMENTO for rete in reti_sul_foglio):
        return []
    disegnati = set(sul_foglio)
    voci = [
        catalogo.get(pezzo.definition_id)
        for pezzo in modello.components
        if pezzo.id in disegnati
    ]

    def sull_acqua(mestiere: str) -> list[ComponentDefinition]:
        return [
            voce for voce in voci if mestiere in voce.functions and _sull_acqua_dell_impianto(voce)
        ]

    generatori = sull_acqua("heat_generation")
    generate: list[tuple[SoggettoDellaNota, str]] = [("isolamento", nota_dell_isolamento(tubi, anche_altri))]
    if any("frost_protection" in voce.functions for voce in voci):
        generate.append(("antigelo", NOTA_ANTIGELO))
    if generatori:
        generate.append(("sfiati", NOTA_SFIATI_E_SCARICHI))
    if sull_acqua("expansion"):
        generate.append(("vaso", NOTA_VASO))
    if generatori and any("thermal_storage" in voce.functions for voce in voci):
        generate.append(
            ("sonda", NOTA_SONDA_DEL_VOLANO + (IN_CASCATA if len(generatori) >= 2 else ""))
        )
    # Prima le note del progettista, nel suo ordine (I-271); poi le generate di cui non ha
    # gia' scritto il soggetto, e che non ha tolto.
    sue = list(modello.metadata.note_di_posa)
    coperti = {soggetto_della_nota(item) for item in sue} | set(modello.metadata.note_tolte)
    note = [*sue, *(testo for soggetto, testo in generate if soggetto not in coperti)]
    return note[:MASSIMO_DELLE_NOTE]


def soggetto_della_nota(nota: str) -> str:
    """La prima parola di una nota, in minuscolo e senza la punteggiatura che la segue:
    «Isolamento: tratto interrato…» ha il soggetto «isolamento». E' con questa parola che
    una nota del progettista prende il posto di una nota generata (`SOGGETTI`)."""
    parola = ""
    for carattere in nota.strip():
        if not carattere.isalpha():
            break
        parola += carattere
    return parola.lower()


def _rientro_del_numero(quante: int, corpo_pt: float) -> float:
    """Dove comincia il testo delle note, dopo il numero: il numero piu' largo e uno
    spazio. Le righe che vanno a capo restano allineate al testo, non al numero."""
    return max(larghezza_mm(f"{indice}. ", corpo_pt, False) for indice in range(1, quante + 1))


def _testi_delle_note(
    note: list[str], x_mm: float, alto_mm: float, larghezza_mm_: float, corpo_mm: float
) -> tuple[list[TestoDellaTabella], float]:
    """I testi delle note sotto la riga del titolo, che comincia a `alto_mm`, e il
    fondo del riquadro che li contiene. Lo stesso conto da' l'altezza
    (`impagina_le_note`) e i testi (`tratti_delle_note`)."""
    corpo_pt = corpo_mm / PT_MM
    rientro = _rientro_del_numero(len(note), corpo_pt)
    utile = larghezza_mm_ - 2 * RIENTRO_MM - rientro
    passo = INTERLINEA_EM * corpo_mm
    base = alto_mm + MARGINE_DELLA_RIGA_MM + ALTEZZA_MAIUSCOLE_EM * corpo_mm
    ultima = base
    testi: list[TestoDellaTabella] = []
    for indice, nota in enumerate(note, start=1):
        testi.append(TestoDellaTabella(f"{indice}.", round(x_mm + RIENTRO_MM, 6), round(base, 6), False))
        for numero, riga in enumerate(_a_capo(nota, utile, corpo_pt, False)):
            if numero:
                base += passo
            testi.append(
                TestoDellaTabella(riga, round(x_mm + RIENTRO_MM + rientro, 6), round(base, 6), False)
            )
        ultima = base
        base += passo + STACCO_FRA_LE_NOTE_EM * corpo_mm
    return testi, ultima + MARGINE_DELLA_RIGA_MM


def impagina_le_note(
    note: list[str],
    tabella: TabellaDelleApparecchiature | None,
    frame: SheetFrame,
) -> RiquadroDelleNote | None:
    """Il riquadro delle note, misurato e messo **in cima all'area del disegno, a
    destra della tabella**, staccato da lei dello stacco del disegno
    (`STACCO_DALLA_TABELLA_MM`). `None` senza note.

    E' largo **quanto resta fino alla fascia della legenda**, al passo di griglia
    (I-265: «non teniamola a larghezza fissa … portiamola fino al limite del bordo
    destro»). Se a destra della tabella resta meno di
    `LARGHEZZA_MINIMA_MM`, il riquadro va **sotto** la tabella; senza tabella sta
    nell'angolo in alto a sinistra, al suo posto."""
    if not note:
        return None
    standard = frame.standard
    passo = standard.grid_mm
    area = frame.drawing_rect_mm
    destra = area.right_mm - STACCO_DALLA_LEGENDA_MM

    def larghezza_da(sinistra: float) -> float:
        # Fino alla fascia della legenda, non a larghezza fissa (I-265): le note vanno a
        # capo solo quando finisce lo spazio, e il riquadro resta basso.
        return ((destra - sinistra + 1e-6) // passo) * passo

    sinistra, alto = area.x_mm, area.y_mm
    if tabella is not None:
        sinistra = tabella.riquadro[2] + STACCO_DALLA_TABELLA_MM
        if larghezza_da(sinistra) < LARGHEZZA_MINIMA_MM:
            sinistra, alto = area.x_mm, tabella.riquadro[3] + STACCO_DALLA_TABELLA_MM
    larghezza = larghezza_da(sinistra)
    scritte = [per_winansi(item) for item in note[:MASSIMO_DELLE_NOTE]]
    corpo = standard.text_small_mm
    riga = altezza_della_riga_mm(corpo)
    _, fondo = _testi_delle_note(scritte, sinistra, alto + riga, larghezza, corpo)
    altezza = -(-round(fondo - alto, 6) // PASSO_DELLE_RIGHE_MM) * PASSO_DELLE_RIGHE_MM
    return RiquadroDelleNote(
        x_mm=round(sinistra, 6),
        y_mm=round(alto, 6),
        larghezza_mm=round(larghezza, 6),
        altezza_mm=altezza,
        riga_mm=riga,
        note=scritte,
    )


def tratti_delle_note(riquadro: RiquadroDelleNote, standard: GraphicStandard) -> TrattiDellaTabella:
    """Le linee — il riquadro e la linea sotto il titolo, al tratto sottile della
    tabella — e i testi: «NOTE» in neretto a meta' della sua riga, come
    l'intestazione della tabella, e sotto le note numerate."""
    sinistra, alto, destra, basso = riquadro.riquadro
    sotto_il_titolo = round(alto + riquadro.riga_mm, 6)
    linee = (
        (sinistra, alto, destra, alto),
        (sinistra, sotto_il_titolo, destra, sotto_il_titolo),
        (sinistra, basso, destra, basso),
        (sinistra, alto, sinistra, basso),
        (destra, alto, destra, basso),
    )
    corpo = standard.text_small_mm
    titolo = TestoDellaTabella(
        TITOLO,
        round(sinistra + RIENTRO_MM, 6),
        round(alto + riquadro.riga_mm / 2 + corpo * MEZZE_MAIUSCOLE_EM, 6),
        True,
    )
    testi, _ = _testi_delle_note(riquadro.note, sinistra, sotto_il_titolo, riquadro.larghezza_mm, corpo)
    return TrattiDellaTabella(
        linee=linee,
        testi=(titolo, *testi),
        corpo_mm=corpo,
        spessore_mm=standard.line_thin_mm,
    )


def svg_delle_note(riquadro: RiquadroDelleNote, standard: GraphicStandard) -> str:
    """Il riquadro delle note nell'SVG della tavola: un gruppo, in nero come la tabella."""
    return svg_dei_tratti(tratti_delle_note(riquadro, standard), "note-di-posa")


__all__ = [
    "IN_CASCATA",
    "MASSIMO_DELLE_NOTE",
    "NOTA_ANTIGELO",
    "NOTA_ISOLAMENTO",
    "nota_dell_isolamento",
    "spessore_dell_isolante_mm",
    "NOTA_SFIATI_E_SCARICHI",
    "NOTA_SONDA_DEL_VOLANO",
    "NOTA_VASO",
    "SOGGETTI",
    "TITOLO",
    "impagina_le_note",
    "note_di_posa",
    "soggetto_della_nota",
    "svg_delle_note",
    "tratti_delle_note",
]
