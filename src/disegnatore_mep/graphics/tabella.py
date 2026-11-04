"""La tabella delle apparecchiature, in alto a sinistra del foglio (REL-006).

Il PO, il 28 settembre 2026 (I-141): «Inserire una tabella in alto a sinistra del
foglio con codice, descrizione, caratteristiche, marca, modello. Esempio pdc.01
pompa di calore aria acqua nr 1 - 15 kw - Shenling - HPM150WR3. Mettiamo dentro
solo le apparecchiature principali, e vaso espansione, no valvole». E lo stesso
giorno (I-144): «marca e modello non deve essere nella skill, è qualcosa che
definisce il progettista […] quindi è un dato in ingresso».

Questo modulo fa tre cose, e il posto sul foglio non e' fra queste — lo decide
l'esecutore del piano, che fa spazio alla tabella (`layout/compose.py`):

- **che cosa dice** (`righe_della_tabella`): i pezzi che fanno un mestiere da
  apparecchiatura principale, la loro sigla, il nome della voce di catalogo, i
  dati tecnici **che il progettista ha dato**, con chiavi fisse. **Un dato che
  manca resta una cella vuota, con un trattino** (D-087): la tabella non ne
  inventa, e la skill non ha un elenco di marche e modelli;
- **quanto e' grande** (`impagina_la_tabella`): le colonne larghe quanto il
  loro testo piu' lungo, misurato con le larghezze di Helvetica del cartiglio;
- **come si disegna** (`tratti_della_tabella`): linee e testi, che l'SVG e il
  DXF scrivono **dalle stesse misure** — la tabella e' la stessa nei due.

Le scelte di contenuto e di grafica sono **proposte della sessione**, da
giudicare sulla tavola (D-146): quali mestieri entrano, le caratteristiche per
mestiere, il codice uguale alla sigla del disegno, «nr» quando le voci sono piu'
d'una, il trattino, il corpo e le righe della legenda.
"""

import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graph.naming import Naming, NamingError
from disegnatore_mep.graph.plant import GraphError, read_plant
from disegnatore_mep.layout.geometry import (
    RigaDellaTabella,
    SheetGeometry,
    TabellaDelleApparecchiature,
)
from disegnatore_mep.model.project import (
    CHIAVI_DEI_DATI_NUMERICI,
    MARCA,
    MODELLO,
    ProjectModel,
)
from disegnatore_mep.model.types import Domain, JsonPrimitive

from .cartiglio import FAMIGLIA, PT_MM, SEPARATORE, larghezza_mm
from .frame import SheetFrame
from .standard import GraphicStandard

FUNZIONI_DELLA_TABELLA: tuple[str, ...] = (
    "heat_generation",
    "refrigerant_generation",
    "thermal_storage",
    "dhw_storage",
    "hydraulic_separation",
    "heat_exchange",
    "circulation",
    "expansion",
    "direct_expansion_terminal",
    "air_zoning",
    "zone_control",
    "unit_control",
    "room_contact_control",
)
"""I mestieri delle apparecchiature principali, e il vaso di espansione (I-141).

**Con l'aria-aria** (REL-012, dal kit del PO): l'unita' interna ad espansione
diretta, il plenum motorizzato di zona, la centrale di zona e il comando a filo.
Sono le macchine che il progettista sceglie con marca e modello, come la pompa di
calore. Fuori le bocchette e le riprese, che sono terminali, e i termostati, che
sono tanti uguali e portano la loro scritta di zona accanto — se non hanno marca o
modello dichiarati (`FUNZIONI_CON_MARCA_O_MODELLO`). *Proposta della sessione*, da
giudicare sulla tavola.

**Il termostato ambiente a contatto** (I-269) entra sempre: sta solo sulla tavola
dell'elettrico, sulla linea del circolatore che accende, e va in tabella e in
legenda con la sua sigla.

Generatori, accumuli e bollitori, separatori idraulici, scambiatori,
circolatori — e i vasi. **Fuori** le valvole, come il PO ha detto, e con loro
filtri, strumenti, raccordi e attacchi. Fuori anche i **terminali** (radiatori,
ventilconvettori, pannelli): nello schema di centrale sono le utenze, non
macchine della centrale. *Proposta della sessione*, da giudicare sulla tavola.
Un pezzo entra se **uno qualunque** dei suoi mestieri e' in elenco."""

FUNZIONI_CON_MARCA_O_MODELLO: tuple[str, ...] = ("room_control",)
"""I mestieri che entrano nella tabella **solo se il pezzo ha marca o modello
dichiarati** (collaudo T3 di REL-012, §2: il progettista aveva dato «Airzone Think a
filo» per i termostati, e sulla tavola non comparivano). Un termostato senza marca ne'
modello resta fuori, come prima: una riga col solo nome non dice niente che il simbolo
non dica. Il preflight vuole sul disegno la sigla di ogni pezzo in tabella (I-160), e
il motore la scrive per i pezzi fuori dall'acqua (`sigle_sul_disegno`). *Proposta
della sessione*, da giudicare sulla tavola."""

CARATTERISTICHE_PER_MESTIERE: dict[str, tuple[str, ...]] = {
    "heat_generation": ("power_kw",),
    "refrigerant_generation": ("power_kw",),
    "heat_exchange": ("power_kw",),
    "thermal_storage": ("volume_l",),
    "dhw_storage": ("volume_l",),
    "expansion": ("volume_l",),
    "circulation": ("flow_rate_m3h", "head_kpa", "head_m"),
    "direct_expansion_terminal": ("power_kw", "flow_rate_m3h"),
}
"""Che cosa si scrive fra le caratteristiche, secondo il mestiere del pezzo.

La **potenza** dei generatori e degli scambiatori, il **volume** di accumuli,
bollitori e vasi, **portata e prevalenza** dei circolatori, **potenza e portata
d'aria** dell'unita' interna (REL-012). Un pezzo che fa
piu' mestieri — il boiler in pompa di calore genera e accumula — le porta
tutte, nell'ordine delle chiavi di `CHIAVI_DEI_DATI_NUMERICI`. Il separatore
idraulico non ha una sua caratteristica: quando e' anche un accumulo, porta il
volume da accumulo."""

CONTATTO = "contatto"
"""La portata del contatto di un termostato a contatto o di un relè, come il progettista
l'ha data: «5(2) A 250 V» (I-269). Un testo."""

CARATTERISTICHE_DI_TESTO: dict[str, tuple[str, ...]] = {
    "room_contact_control": (CONTATTO,),
}
"""Le caratteristiche che il progettista da' **come testo**, scritte come le ha date
dopo quelle numeriche: la portata del contatto del termostato ambiente (I-269), per
esempio «5(2) A 250 V». Una chiave che manca non scrive niente, come un dato numerico
che manca. *Proposta della sessione*, da giudicare sulla tavola."""

CARATTERISTICHE_ELETTRICHE: tuple[str, ...] = (
    "alimentazione",
    "potenza_elettrica_kw",
    "corrente_max_a",
    "cavo_minimo",
)
"""Le caratteristiche di ogni riga **sulla tavola dell'elettrico** (I-277), in
quest'ordine: l'alimentazione («230 V 1~», un testo), la potenza elettrica assorbita
(kW) e la corrente massima (A), numeri come quelli della tabella idraulica, e il cavo
minimo richiesto («3G6», un testo). Poi, sul relè e sul termostato a contatto, la
portata del contatto (`CONTATTO`). Il PO, il 4 novembre 2026: «che senso ha mettere le
caratteristiche idroniche della pdc e del circolatore in una tabella nella tavola
elettrica ci dovrebbero andare le info elettriche. pdc Assorbimento ampere max? cavo
minimo richiesto di sezione? alimentazione 230 o 400 ecc.». I dati idronici — potenza
termica, volume, portata, prevalenza — su quella tavola non si scrivono. Sono dati del
progettista, dalla targa o dal manuale: se mancano, la cella ha il trattino."""

FUNZIONI_COL_CONTATTO: tuple[str, ...] = ("room_contact_control", "power_switching")
"""Chi ha un contatto la cui portata la tabella dell'elettrico scrive (I-277)."""

INTESTAZIONE: tuple[str, ...] = (
    "CODICE",
    "DESCRIZIONE",
    "CARATTERISTICHE",
    "MARCA",
    "MODELLO",
)
"""Le cinque colonne, nell'ordine in cui il PO le ha dette (I-141)."""

CELLA_VUOTA = "–"
"""Il segno di una cella senza dato: il progettista non l'ha dato, e sulla
tavola non compare (D-087). Un trattino e non il vuoto, perche' il vuoto si
legge come una dimenticanza del disegno."""

MARGINE_DELLA_RIGA_MM = 1.85
"""Lo spazio sopra e sotto le maiuscole di una riga: quello che la riga di 5 mm
di `REL-006` lasciava al testo di 1,8 mm (D-192, punto 8)."""

PASSO_DELLE_RIGHE_MM = 1.25
"""L'altezza di una riga si arrotonda a mezzo passo di griglia."""

RIENTRO_MM = 1.5
"""Lo spazio fra il testo e le linee della cella, a sinistra e a destra: lo
stesso stacco che un testo prende dal proprio pezzo (`labels.TAG_GAP_MM`)."""

MEZZE_MAIUSCOLE_EM = 0.35
"""Mezza altezza delle maiuscole, in corpi: serve a mettere il testo a meta'
della riga. Le maiuscole di Arial e di Helvetica sono alte 0,688–0,716 em
(`dxf.ALTEZZA_MAIUSCOLE_EM`, il cartiglio)."""


def altezza_della_riga_mm(corpo_mm: float) -> float:
    """L'altezza di una riga della tabella per il corpo dei suoi testi (REL-008): le
    maiuscole, alte 0,7 corpi, piu' lo stesso margine sopra e sotto, arrotondate a
    mezzo passo di griglia. A 1,8 mm fa i 5 mm di `REL-006`; a 9 punti 6,25."""
    grezza = 2 * MEZZE_MAIUSCOLE_EM * corpo_mm + 2 * MARGINE_DELLA_RIGA_MM
    return -(-round(grezza, 6) // PASSO_DELLE_RIGHE_MM) * PASSO_DELLE_RIGHE_MM


def formatta_il_dato(chiave: str, valore: JsonPrimitive) -> str | None:
    """Un dato numerico come si legge sulla tavola: «15 kW», «2,5 m³/h».

    La virgola e' quella decimale italiana. Un valore che non e' un numero non
    si scrive: e' il modello a rifiutarlo (`ComponentInstance`), e qui non si
    indovina che cosa volesse dire."""
    unita = CHIAVI_DEI_DATI_NUMERICI.get(chiave)
    if unita is None or isinstance(valore, bool) or not isinstance(valore, int | float):
        return None
    testo = str(valore) if isinstance(valore, int) else f"{valore:.3f}".rstrip("0").rstrip(".")
    return f"{testo.replace('.', ',')} {unita}"


PRECARICA = "precarica_bar"
"""La precarica del vaso d'espansione, in bar: la scrive il comando `vaso`, e solo nel
progetto esecutivo-costruttivo (D-221, D-224)."""

CONTENUTO_STIMATO = "contenuto_stimato"
"""Il vaso e' dimensionato su un contenuto d'acqua stimato, non dato (D-220)."""


def dati_del_vaso(proprieta: Mapping[str, JsonPrimitive]) -> list[str]:
    """Quello che la riga del vaso porta dopo il volume: la precarica, se c'e', e
    «contenuto stimato» (D-221)."""
    dati: list[str] = []
    precarica = proprieta.get(PRECARICA)
    if isinstance(precarica, int | float) and not isinstance(precarica, bool) and precarica > 0:
        dati.append(f"precarica {precarica:.1f} bar".replace(".", ","))
    if proprieta.get(CONTENUTO_STIMATO) is True:
        dati.append("contenuto stimato")
    return dati


def dati_idronici(mestieri: Iterable[str], proprieta: Mapping[str, JsonPrimitive]) -> list[str]:
    """Le caratteristiche di una riga sulla tavola idraulica e sulla tavola unica: i dati
    numerici del mestiere (`CARATTERISTICHE_PER_MESTIERE`), quelli del vaso, e i testi
    del mestiere (`CARATTERISTICHE_DI_TESTO`)."""
    fa = tuple(mestieri)
    chiavi = [
        chiave
        for chiave in CHIAVI_DEI_DATI_NUMERICI
        if any(chiave in CARATTERISTICHE_PER_MESTIERE.get(item, ()) for item in fa)
    ]
    dati = [
        scritto
        for chiave in chiavi
        if (scritto := formatta_il_dato(chiave, proprieta.get(chiave))) is not None
    ]
    if "expansion" in fa:
        dati.extend(dati_del_vaso(proprieta))
    dati.extend(
        scritto
        for item in fa
        for chiave in CARATTERISTICHE_DI_TESTO.get(item, ())
        if (scritto := _testo(proprieta.get(chiave))) is not None
    )
    return dati


def dati_elettrici(mestieri: Iterable[str], proprieta: Mapping[str, JsonPrimitive]) -> list[str]:
    """Le caratteristiche di una riga sulla tavola dell'elettrico (I-277): alimentazione,
    potenza elettrica, corrente massima, cavo minimo (`CARATTERISTICHE_ELETTRICHE`), e la
    portata del contatto di chi ne ha uno. I numeri si scrivono come nella tabella
    idraulica, con la virgola e l'unita'; i testi come il progettista li ha dati."""
    dati: list[str] = []
    for chiave in CARATTERISTICHE_ELETTRICHE:
        valore = proprieta.get(chiave)
        scritto = (
            formatta_il_dato(chiave, valore) if chiave in CHIAVI_DEI_DATI_NUMERICI else _testo(valore)
        )
        if scritto is not None:
            dati.append(scritto)
    if set(mestieri) & set(FUNZIONI_COL_CONTATTO) and (contatto := _testo(proprieta.get(CONTATTO))):
        dati.append(contatto)
    return dati


def _testo(valore: JsonPrimitive) -> str | None:
    """Un dato di testo — marca, modello —, o `None` se non c'e'.

    «ND» e' come «Capire» scrive un dato non dato (`cartiglio.NON_DATO`): per la
    tabella e' una cella vuota come un dato che manca."""
    if not isinstance(valore, str) or not valore.strip() or valore.strip().upper() == "ND":
        return None
    return valore.strip()


def _in_ordine_di_sigla(codice: str | None) -> tuple[str, int, str]:
    """`PDC-02` prima di `PDC-10`: la famiglia, poi il numero come numero."""
    if codice is None:
        return ("~", 0, "")
    forma = re.fullmatch(r"([A-Za-z]+)[-.]?(\d+)", codice)
    if forma is None:
        return (codice, 0, codice)
    return (forma.group(1), int(forma.group(2)), codice)


FUORI_DALLA_TABELLA_DELL_ELETTRICO: tuple[str, ...] = ("power_isolation",)
"""I mestieri che restano fuori dalla tabella **anche sulla tavola dell'elettrico**
(I-276): il sezionatore, un organo in linea sul cavo della macchina come la valvola
sul tubo — e la tabella dell'idraulica le valvole non le elenca (I-141). La sua sigla
sta sul disegno e cede il posto alla scritta del cavo che lo attraversa («3G6 · L 15
m»): in tabella diventerebbe una sigla che non cede, e la scritta del progettista non
troverebbe piu' posto (RUN_LABEL_OMITTED, sul collaudo T2 di REL-012). *Proposta della
sessione*, da giudicare sulla tavola."""


def entra_in_tabella(
    mestieri: Iterable[str], proprieta: Mapping[str, JsonPrimitive], ogni_pezzo: bool = False
) -> bool:
    """Se un pezzo disegnato ha una riga nella tabella: per mestiere, per marca o modello
    dichiarati, o — sulla tavola dell'elettrico, `ogni_pezzo` — perche' ha un cavo e non
    e' un organo di linea."""
    fa = set(mestieri)
    if fa & set(FUNZIONI_DELLA_TABELLA):
        return True
    if ogni_pezzo:
        return not fa & set(FUORI_DALLA_TABELLA_DELL_ELETTRICO)
    return bool(
        fa & set(FUNZIONI_CON_MARCA_O_MODELLO)
        and (_testo(proprieta.get(MARCA)) or _testo(proprieta.get(MODELLO)))
    )


def righe_della_tabella(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    naming: Naming,
    sigle: dict[str, str],
    sul_foglio: Iterable[str],
    ogni_pezzo: bool = False,
) -> list[RigaDellaTabella]:
    """Le apparecchiature della tavola, una riga per pezzo, in ordine.

    `sigle` sono quelle della lettura dell'impianto (`graph.plant`): la sigla
    che l'ingegnere ha scritto, e per gli altri quella della famiglia — la
    stessa che il disegno scrive accanto al pezzo (D-097, «la sigla è una sola
    per tutto il prodotto»). `sul_foglio` sono i pezzi disegnati su questa
    tavola.

    `ogni_pezzo` e' la tabella **della tavola dell'elettrico** (I-276): ogni pezzo
    disegnato, perche' su quella tavola ogni pezzo ha un cavo ed e' un'apparecchiatura
    dell'elettrico o del comando — tranne gli organi di linea
    (`FUORI_DALLA_TABELLA_DELL_ELETTRICO`); `tabella_della_tavola`. Le sue
    caratteristiche sono quelle elettriche (`dati_elettrici`, I-277), non quelle
    idroniche.

    L'ordine e' quello delle famiglie in `naming/families.json` — prima chi il
    calore lo produce, poi accumuli, separatori, circolatori, scambiatori, vasi
    — e dentro una famiglia quello delle sigle."""
    disegnati = set(sul_foglio)
    scelti: list[tuple[tuple[int, tuple[str, int, str], str], RigaDellaTabella]] = []
    for pezzo in modello.components:
        if pezzo.id not in disegnati:
            continue
        voce = catalogo.get(pezzo.definition_id)
        mestieri = tuple(voce.functions)
        if not entra_in_tabella(mestieri, pezzo.properties, ogni_pezzo):
            continue
        try:
            famiglia = naming.families.index(naming.family_of(mestieri, pezzo.id))
        except NamingError:
            famiglia = len(naming.families)
        dati = (
            dati_elettrici(mestieri, pezzo.properties)
            if ogni_pezzo
            else dati_idronici(mestieri, pezzo.properties)
        )
        codice = sigle.get(pezzo.id, pezzo.tag)
        riga = RigaDellaTabella(
            component_id=pezzo.id,
            codice=codice,
            descrizione=voce.name,
            caratteristiche=SEPARATORE.join(dati) if dati else None,
            marca=_testo(pezzo.properties.get(MARCA)),
            modello=_testo(pezzo.properties.get(MODELLO)),
        )
        scelti.append(((famiglia, _in_ordine_di_sigla(codice), pezzo.id), riga))
    righe = [riga for _, riga in sorted(scelti, key=lambda item: item[0])]

    # «nr 1», «nr 2» quando due apparecchiature hanno lo stesso nome (I-141): e'
    # quale delle due, nell'ordine delle sigle, non quante.
    quante = Counter(riga.descrizione for riga in righe)
    contate: Counter[str] = Counter()
    numerate: list[RigaDellaTabella] = []
    for riga in righe:
        if quante[riga.descrizione] < 2:
            numerate.append(riga)
            continue
        contate[riga.descrizione] += 1
        numerate.append(
            riga.model_copy(
                update={"descrizione": f"{riga.descrizione} nr {contate[riga.descrizione]}"}
            )
        )
    return numerate


def celle(riga: RigaDellaTabella) -> tuple[str, ...]:
    """Le cinque celle di una riga, come si scrivono: il trattino dove manca il dato."""
    return tuple(
        valore if valore else CELLA_VUOTA
        for valore in (riga.codice, riga.descrizione, riga.caratteristiche, riga.marca, riga.modello)
    )


def impagina_la_tabella(
    righe: list[RigaDellaTabella], frame: SheetFrame
) -> TabellaDelleApparecchiature | None:
    """La tabella misurata e messa **nell'angolo in alto a sinistra dell'area
    del disegno**, contro la squadratura e la testata come la legenda sta contro
    la squadratura a destra. `None` se la tavola non ha apparecchiature.

    Ogni colonna e' larga quanto il suo testo piu' lungo — intestazione
    compresa — piu' il rientro dai due lati, e si arrotonda al passo di griglia:
    le linee della tabella cadono sulla griglia del disegno."""
    if not righe:
        return None
    standard = frame.standard
    corpo_pt = standard.text_small_mm / PT_MM
    passo = standard.grid_mm
    colonne: list[float] = []
    for indice, titolo in enumerate(INTESTAZIONE):
        piu_lungo = max(
            [larghezza_mm(titolo, corpo_pt, True)]
            + [larghezza_mm(celle(riga)[indice], corpo_pt, False) for riga in righe]
        )
        colonne.append(-(-(piu_lungo + 2 * RIENTRO_MM) // passo) * passo)
    area = frame.drawing_rect_mm
    return TabellaDelleApparecchiature(
        x_mm=area.x_mm,
        y_mm=area.y_mm,
        colonne_mm=colonne,
        riga_mm=altezza_della_riga_mm(standard.text_small_mm),
        righe=righe,
    )


def tabella_della_tavola(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    cartella_dei_nomi: Path,
    sheet: SheetGeometry,
    frame: SheetFrame,
    vista: str = "tutto",
) -> TabellaDelleApparecchiature | None:
    """La tabella di una tavola: le righe dei pezzi disegnati, impaginate.

    Le sigle vengono dalla lettura dell'impianto (D-097, D-098). Se l'impianto
    non si legge — un pezzo che nessuna sorgente raggiunge — la tabella scrive
    le sigle che l'ingegnere ha dato, e il trattino dove non ce ne sono: la
    tavola esce lo stesso, e la lettura lo dice dove serve.

    **Sulla tavola dell'elettrico** (`vista` «elettrico», I-276) la tabella elenca ogni
    pezzo disegnato: la tavola porta soltanto i pezzi a cui arriva un cavo, e sono le
    apparecchiature dell'elettrico e del comando — la deviatrice e la miscelatrice
    motorizzate, le sonde, il quadro, i relè, i termostati, il comando a filo — oltre
    alle macchine di sempre. Il sezionatore no: e' un organo di linea
    (`FUORI_DALLA_TABELLA_DELL_ELETTRICO`). Il PO, su una commessa reale: nella tabella della tavola
    elettrica «mancano la deviatrice, le sonde e il quadro». Le sigle sono quelle del
    grafo intero, che la vista scrive sui pezzi (`piano.vista`). La tabella della
    tavola idraulica e della tavola unica resta quella di sempre. *Proposta della
    sessione*, da giudicare sulla tavola."""
    naming = Naming.from_directory(cartella_dei_nomi)
    try:
        sigle = read_plant(modello, catalogo, naming).sigle
    except (GraphError, NamingError):
        sigle = {}
    righe = righe_della_tabella(
        modello,
        catalogo,
        naming,
        sigle,
        (item.component_id for item in sheet.symbols),
        ogni_pezzo=vista == "elettrico",
    )
    return impagina_la_tabella(righe, frame)


def fuori_dall_acqua(voce: ComponentDefinition) -> bool:
    """Se una voce non ha **nessun attacco d'acqua**: sta tutta sull'aria, sul
    refrigerante, sulla condensa, sull'elettrico o sul comando (REL-012).

    E' la regola con cui questi pezzi portano la loro sigla sul disegno anche fuori
    dalla tabella: sul canalizzato del collaudo T1 bocchette, termostati, quadro,
    sezionatore, ripresa, sifone e scarico restavano senza, e la pianta e la
    distinta non avevano un nome con cui citarli. **I pezzi dell'idronico restano
    come sono**: una valvola o un filtro la sigla sul disegno non la portano (la
    tavola di consegna porta le sigle delle macchine principali, `layout.addresses`),
    e una regola sui soli pezzi senz'acqua non tocca nessuna tavola idronica."""
    return bool(voce.ports) and all(porta.domain is not Domain.HYDRONIC for porta in voce.ports)


def sigle_sul_disegno(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    sigle: dict[str, str],
    sul_foglio: Iterable[str],
    comandati: Iterable[str] = (),
) -> dict[str, str]:
    """La sigla dei pezzi **fuori dall'acqua** disegnati su questa tavola, che il
    progettista non ha scritto. `sigle` sono quelle della lettura del **grafo intero**
    (D-097, `piano.vista.sigle_del_grafo_intero`): le stesse che la tabella, la
    distinta e la pianta usano, e le stesse sulla tavola idraulica e su quella
    dell'elettrico. Se l'impianto non si legge sono vuote, e valgono quelle scritte,
    come per la tabella.

    **E dei pezzi `comandati`** (collaudo T2 di REL-012, §3.1): quelli che hanno un
    cavo — una valvola motorizzata, una sonda a immersione, un circolatore — portano
    la sigla della famiglia (VMR, VD, SO, CIR) **sulle due tavole**, anche
    sull'idraulica dove il cavo non c'e'. Sulla tavola dell'elettrico due valvole a
    tre vie e due sonde senza nome non dicevano quale cavo va dove. Un grafo senza
    elettrico non ha pezzi comandati, e nessuna tavola idronica cambia."""
    disegnati = set(sul_foglio)
    con_un_cavo = set(comandati)
    return {
        pezzo.id: sigle[pezzo.id]
        for pezzo in modello.components
        if pezzo.id in disegnati
        and pezzo.tag is None
        and pezzo.id in sigle
        and (pezzo.id in con_un_cavo or fuori_dall_acqua(catalogo.get(pezzo.definition_id)))
    }


def pezzi_comandati(modello: ProjectModel) -> frozenset[str]:
    """I pezzi a cui arriva almeno un cavo o un bus nel grafo intero (collaudo T2 di
    REL-012): una tubazione di una rete del dominio del comando li tocca."""
    del_comando = {rete.id for rete in modello.networks if rete.domain is Domain.CONTROL}
    return frozenset(
        ref.component_id
        for item in modello.connections
        if item.network_id in del_comando
        for ref in (item.endpoint_a, item.endpoint_b)
    )


@dataclass(frozen=True)
class TestoDellaTabella:
    testo: str
    x_mm: float
    y_mm: float
    """La linea di base."""
    grassetto: bool


@dataclass(frozen=True)
class TrattiDellaTabella:
    """La tabella come linee e testi: quello che l'SVG e il DXF scrivono."""

    linee: tuple[tuple[float, float, float, float], ...]
    testi: tuple[TestoDellaTabella, ...]
    corpo_mm: float
    spessore_mm: float


def tratti_della_tabella(
    tabella: TabellaDelleApparecchiature, standard: GraphicStandard
) -> TrattiDellaTabella:
    """Le linee — una griglia piena, al tratto sottile della legenda — e i testi:
    l'intestazione in neretto, le righe in chiaro, al corpo dei testi della
    tavola, allineati a sinistra e a meta' riga."""
    sinistra, alto, destra, basso = tabella.riquadro
    linee: list[tuple[float, float, float, float]] = []
    for indice in range(len(tabella.righe) + 2):
        y = round(alto + indice * tabella.riga_mm, 6)
        linee.append((sinistra, y, destra, y))
    x = sinistra
    bordi = [x]
    for larghezza in tabella.colonne_mm:
        x = round(x + larghezza, 6)
        bordi.append(x)
    linee.extend((item, alto, item, basso) for item in bordi)

    corpo = standard.text_small_mm
    testi: list[TestoDellaTabella] = []
    scritte = [INTESTAZIONE, *(celle(riga) for riga in tabella.righe)]
    for fila, valori in enumerate(scritte):
        base = round(
            alto + fila * tabella.riga_mm + tabella.riga_mm / 2 + corpo * MEZZE_MAIUSCOLE_EM, 6
        )
        for colonna, valore in enumerate(valori):
            testi.append(
                TestoDellaTabella(
                    testo=valore,
                    x_mm=round(bordi[colonna] + RIENTRO_MM, 6),
                    y_mm=base,
                    grassetto=fila == 0,
                )
            )
    return TrattiDellaTabella(
        linee=tuple(linee),
        testi=tuple(testi),
        corpo_mm=corpo,
        spessore_mm=standard.line_thin_mm,
    )


def _escape(testo: str) -> str:
    return (
        testo.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_della_tabella(
    tabella: TabellaDelleApparecchiature, standard: GraphicStandard
) -> str:
    """La tabella nell'SVG della tavola: un gruppo, in nero come la legenda."""
    return svg_dei_tratti(tratti_della_tabella(tabella, standard), "tabella-apparecchiature")


def svg_dei_tratti(tratti: TrattiDellaTabella, classe: str) -> str:
    """Linee e testi di una tabella come un gruppo SVG di quella classe: la tabella
    delle apparecchiature e il riquadro delle note di posa (REL-011) si scrivono
    allo stesso modo."""
    parti = [
        f'<g class="{classe}" stroke="black" '
        f'stroke-width="{tratti.spessore_mm:g}" fill="none">'
    ]
    parti.extend(
        f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"/>'
        for x1, y1, x2, y2 in tratti.linee
    )
    for item in tratti.testi:
        peso = ' font-weight="bold"' if item.grassetto else ""
        parti.append(
            f'<text x="{item.x_mm:g}" y="{item.y_mm:g}" font-family="{FAMIGLIA}" '
            f'font-size="{tratti.corpo_mm:g}"{peso} fill="black" stroke="none">'
            f"{_escape(item.testo)}</text>"
        )
    parti.append("</g>")
    return "".join(parti)


__all__ = [
    "CARATTERISTICHE_DI_TESTO",
    "CARATTERISTICHE_ELETTRICHE",
    "CARATTERISTICHE_PER_MESTIERE",
    "CELLA_VUOTA",
    "FUNZIONI_CON_MARCA_O_MODELLO",
    "FUNZIONI_DELLA_TABELLA",
    "FUORI_DALLA_TABELLA_DELL_ELETTRICO",
    "INTESTAZIONE",
    "TestoDellaTabella",
    "TrattiDellaTabella",
    "celle",
    "dati_elettrici",
    "dati_idronici",
    "entra_in_tabella",
    "formatta_il_dato",
    "impagina_la_tabella",
    "righe_della_tabella",
    "svg_dei_tratti",
    "svg_della_tabella",
    "tabella_della_tavola",
    "tratti_della_tabella",
]
