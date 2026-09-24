"""L'esecutore del piano, sulle tavole che il pianificatore ha composto da solo.

Sono i documenti agli atti di `docs/collaudi/DRAW-017/prova-camera-pulita-2026-09-24/`:
per ciascuno dei cinque impianti **il grafo completo e il piano composto su di
lui** — quattro ricomposti il 24 settembre 2026 sulla libreria di `DRAW-017`, e
il 4 com'era stato approvato il 23, perche' il suo grafo non e' cambiato. Fino a
`DRAW-017` erano i due piani scritti a mano il 19/20 settembre, che hanno
deciso D-151 (`docs/collaudi/PROVA-PIANO/`): da D-167 quello della cascata non
si instradava piu', e da D-175 nemmeno quello dell'impianto 1 — la miscelatrice
e' diventata un pezzo del piano, e un piano che non la nomina non compone il
grafo di oggi. **I piani a mano erano il bersaglio del pianificatore, non il
prodotto**: le prove leggono quelli che il pianificatore scrive (`DRAW-017` §6).

Quello che si misura qui e' il criterio 5 di DRAW-015 — **zero rilievi
bloccanti e zero tratte cedute** — piu' le tre regole non negoziabili che il
pezzo porta con se':

* **non gira nessuna ricerca**, ne' la fase del tronco ne' il ciclo di
  miglioramento (D-151);
* **la rotazione si deduce solo dove non c'e' scelta** (C2);
* **la mappa delle porte si rifa' solo per i raccordi** (C3, D-004, I-027), ed
  e' il difetto di **contenuto** che il 20 settembre ha mandato l'acqua fredda
  sull'uscita primaria dell'accumulo.
"""
# categoria: difende il motore

import json
import sys
from functools import cache
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout import compose, improve, spine
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano, orienta
from disegnatore_mep.piano.formato import (
    ErroreDelPiano,
    PezzoNelPiano,
    PianoDiComposizione,
    carica_piano,
)

ROOT = Path(__file__).resolve().parents[2]
COLLAUDO = ROOT / "docs" / "collaudi" / "DRAW-017" / "prova-camera-pulita-2026-09-24"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"

LE_TAVOLE = (
    (1, "A3", 23),
    (4, "A3", 25),
)
"""Impianto, formato e tratte della tavola, come le ha misurate la sessione il
24 settembre 2026 (`README.md` della prova)."""

PRIMO, QUARTO = 1, 4
"""L'impianto 1 porta l'accumulo combinato — l'acqua fredda del 20 settembre —;
il piano del 4 porta il gruppo di riempimento girato **dal pianificatore** e il
tee del manometro girato **dalla deduzione**."""


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def completato(impianto: int) -> ProjectModel:
    """Il grafo completo **su cui il piano e' stato composto**, agli atti con lui.

    E' il file che `rules --apply-all --out` ha scritto per il pianificatore, e
    si legge com'e': la posa di partenza e' greedy e legge l'ordine del file
    (`place.py::_file_order`), e un piano vale per il grafo su cui e' nato
    (D-155). Rifarlo dalle regole di oggi misurerebbe le regole, non
    l'esecutore.
    """
    return load_project(COLLAUDO / f"grafo-completo-{impianto}.json")


@cache
def piano_di(impianto: int) -> PianoDiComposizione:
    return carica_piano(COLLAUDO / f"piano-completo-{impianto}.json")


@cache
def esito(impianto: int) -> EsitoDelPiano:
    return esegui_piano(
        completato(impianto), piano_di(impianto), catalogo(), simboli(), NAMING
    )


@cache
def partenza(impianto: int) -> tuple[list[PlacedSymbol], SheetPartition]:
    """La posa di partenza e la partizione, per interrogare `orienta` da solo."""
    modello = completato(impianto)
    inline = inline_component_ids(modello, catalogo())
    partizione = partition_project(modello, build_trunks(modello, inline))[0]
    frame = esito(impianto).frame
    return place_sheet(modello, partizione, catalogo(), frame, inline), partizione


@pytest.mark.parametrize(("impianto", "formato", "tratte"), LE_TAVOLE)
def test_la_tavola_composta_esce_a_zero(impianto: int, formato: str, tratte: int) -> None:
    """**Criterio 5**: zero rilievi bloccanti e zero tratte cedute.

    E' la misura che ha deciso D-151, e qui si rifa' dal percorso nuovo, su
    tutte e cinque le tavole. Le tratte si contano perche' un conto che cambia
    vuol dire che e' cambiato l'impianto, non il disegno; il formato, perche'
    e' il piano a sceglierlo.
    """
    misura = esito(impianto)
    assert misura.errore is None
    assert misura.disegno is not None
    foglio = misura.disegno.sheets[0]
    assert len(foglio.routes) == tratte
    assert misura.cedute == ()
    assert misura.bloccanti == []
    assert misura.frame.standard.sheet_width_mm == {
        "A4": 297.0,
        "A3": 420.0,
        "A2": 594.0,
        "A1": 841.0,
    }[formato]


@pytest.mark.parametrize(("impianto", "formato", "tratte"), LE_TAVOLE)
def test_la_tavola_composta_ha_simboli_linee_e_legenda(
    impianto: int, formato: str, tratte: int
) -> None:
    """Una tavola che non porta niente non e' una tavola (D-146)."""
    foglio = esito(impianto).disegno
    assert foglio is not None
    sheet = foglio.sheets[0]
    assert sheet.symbols and sheet.routes and sheet.legend and sheet.labels


@pytest.mark.parametrize(("impianto", "formato", "tratte"), LE_TAVOLE)
def test_la_mappa_delle_porte_non_si_rifa_sulle_macchine(
    impianto: int, formato: str, tratte: int
) -> None:
    """**C3**, e il 20 settembre e' il precedente.

    Un T si disegna come un punto e ha tre attacchi uguali: quale porta stia su
    quale attacco e' una scelta della posa. Su una macchina no — `primary_out` e
    `cold_in` di un accumulo sono due bocchettoni **fisici diversi del
    serbatoio** — e rimapparli non e' un ritocco grafico, e' un altro impianto.
    """
    posati, partizione = partenza(impianto)
    prima = {item.component_id: dict(item.port_map) for item in posati}
    girati = orienta(posati, completato(impianto), partizione, catalogo(), frozenset())
    definizioni = {
        item.id: item.definition_id for item in completato(impianto).components
    }

    macchine = 0
    for item in girati:
        if catalogo().resolve(definizioni[item.component_id]).definition.is_a_fitting:
            continue
        macchine += 1
        assert item.port_map == prima[item.component_id], item.component_id
    assert macchine, "nessuna macchina: la prova non misurerebbe niente"


def test_l_acqua_fredda_resta_sull_ingresso_freddo_dell_accumulo() -> None:
    """Il difetto di **contenuto** del 20 settembre, sulla tavola che lo produsse.

    Rimappando anche le macchine, l'acqua fredda dell'impianto 1 finiva sulla
    porta a quota 211 — che e' `primary_out` — invece che su `cold_in` a 228,5:
    il ritorno e l'ingresso sanitario arrivavano allo stesso punto. Il grafo era
    giusto e il disegno era sbagliato, e l'ha visto il PO guardando la tavola,
    non una misura. Adesso c'e' la misura.
    """
    disegno = esito(PRIMO).disegno
    assert disegno is not None
    accumulo = next(
        item for item in disegno.sheets[0].symbols if item.component_id == "accumulo"
    )
    assert accumulo.physical_port("cold_in") == "cold_in"
    assert accumulo.physical_port("primary_out") == "primary_out"


def test_la_rotazione_scritta_nel_piano_non_si_tocca() -> None:
    """Il **buco noto** (§4): due attacchi e non e' una macchina.

    Il gruppo di riempimento non rientra in nessuno dei due casi della
    deduzione, e la sua rotazione la scrive il piano. Dove il piano l'ha
    scritta, l'esecutore non la cambia. Sul piano del 4 l'ha scritta il
    pianificatore, e il PO ha approvato la tavola.
    """
    assert piano_di(QUARTO).pezzi["filling-unit-collettore-ritorno-a"].rotazione == 180
    misura = esito(QUARTO)
    gruppo = next(
        item
        for item in misura.posa
        if item.component_id == "filling-unit-collettore-ritorno-a"
    )
    assert gruppo.rotation_deg == 180
    assert not any(riga.startswith("filling-unit-") for riga in misura.girati)


def test_il_tee_del_manometro_si_gira_verso_il_manometro() -> None:
    """La misura del 20 settembre che ha fatto nascere `orienta`.

    Il tee del manometro restava a `rot=0` — lo stacco in su — mentre il piano
    aveva messo il manometro **sotto**: la linea usciva in alto, girava a
    destra, scendeva per sessanta millimetri, tornava indietro e risaliva. E'
    il rettangolo che il PO ha cerchiato chiedendo «perche' non sei andato
    dritto?». Sul piano del 4 il pianificatore mette il manometro sotto il
    ritorno e non scrive la rotazione del tee: la deduce l'esecutore.
    """
    assert piano_di(QUARTO).pezzi["tee-pressure-gauge-collettore-ritorno-a"].rotazione is None
    girati = esito(QUARTO).girati
    assert "tee-pressure-gauge-collettore-ritorno-a 0->180" in girati
    assert "pressure-gauge-collettore-ritorno-a 0->180" in girati


def _vieta(monkeypatch: pytest.MonkeyPatch, nome: str) -> int:
    """Fa esplodere `nome` ovunque il pacchetto lo tenga in mano."""

    def urla(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"{nome} e' stata chiamata: qui non si cerca (D-151)")

    trovate = 0
    for modulo in list(sys.modules.values()):
        if not isinstance(modulo, ModuleType):
            continue
        if not getattr(modulo, "__name__", "").startswith("disegnatore_mep"):
            continue
        if hasattr(modulo, nome):
            monkeypatch.setattr(modulo, nome, urla)
            trovate += 1
    return trovate


def test_l_esecutore_non_gira_nessuna_ricerca(monkeypatch: pytest.MonkeyPatch) -> None:
    """**Non gira nessuna ricerca**: ne' `lay_the_spine` ne' `improve_sheet`.

    E' il punto di D-151, e una regola che nessuno misura e' un'intenzione. Le
    due funzioni si fanno esplodere in **ogni** modulo che le tiene in mano —
    `spine`, `improve` e `compose`, che le importa per nome — e poi si esegue il
    piano: se una delle due parte, la prova e' rossa.
    """
    assert improve.improve_sheet is not None and spine.lay_the_spine is not None
    # **`compose` non le tiene piu' nemmeno in mano** (DRAW-015 §4): dal 20
    # settembre non le importa affatto, che e' una garanzia piu' forte di
    # «non le chiama». Qui si asserisce proprio quello, e le due funzioni si
    # fanno esplodere dove ancora vivono — `improve` e `spine`.
    assert not hasattr(compose, "improve_sheet")
    assert not hasattr(compose, "lay_the_spine")
    assert _vieta(monkeypatch, "improve_sheet") >= 1
    assert _vieta(monkeypatch, "lay_the_spine") >= 1

    misura = esegui_piano(
        completato(PRIMO), piano_di(PRIMO), catalogo(), simboli(), NAMING
    )
    assert misura.disegno is not None
    assert misura.bloccanti == []


def test_un_piano_che_nomina_pezzi_inesistenti_li_elenca() -> None:
    """Un difetto del piano si dice prima di posare qualunque cosa."""
    piano = PianoDiComposizione(
        formato="A2",
        pezzi={
            "pdc-master": PezzoNelPiano(x=35, y=115),
            "caldaia-fantasma": PezzoNelPiano(x=10, y=10),
            "pompa-che-non-c-e": PezzoNelPiano(x=20, y=20),
        },
    )
    with pytest.raises(ErroreDelPiano) as errore:
        esegui_piano(
            completato(PRIMO), piano, catalogo(), simboli(), NAMING
        )
    detto = str(errore.value)
    assert "non esistono nel modello" in detto
    assert "caldaia-fantasma" in detto
    assert "pompa-che-non-c-e" in detto
    assert "pdc-master" not in detto


def test_un_piano_che_posa_un_organo_in_linea_lo_dice_per_nome() -> None:
    """Un organo in linea c'e' nel modello, e lo posa il motore sulla sua tratta.

    Fino al 23 settembre 2026 il messaggio lo metteva fra i pezzi «che non
    esistono nel modello»: falso, e chi componeva il primo grafo completo ci
    avrebbe perso il giro cercando un pezzo che il grafo porta.
    """
    piano = PianoDiComposizione(
        formato="A2",
        pezzi={
            "pdc-master": PezzoNelPiano(x=35, y=115),
            "valve-isolation-accumulo-primary-in": PezzoNelPiano(x=100, y=100),
        },
    )
    with pytest.raises(ErroreDelPiano) as errore:
        esegui_piano(
            completato(PRIMO), piano, catalogo(), simboli(), NAMING
        )
    detto = str(errore.value)
    assert "non esistono nel modello" not in detto
    assert "organi in linea" in detto
    assert "valve-isolation-accumulo-primary-in" in detto


def test_un_piano_che_non_si_instrada_porta_comunque_la_posa() -> None:
    """**La diagnostica utile e' dove sono finiti i pezzi**, non il messaggio.

    Chi compone deve poter vedere che cosa ha lasciato in mezzo e correggere il
    piano invece di indovinare. Qui il piano ammucchia tutti i pezzi
    dell'impianto 1 nello stesso punto: non si instrada, e l'esito porta lo
    stesso la posa applicata e il motivo.
    """
    scritto = piano_di(PRIMO)
    ammucchiato = PianoDiComposizione(
        formato=scritto.formato,
        note=["ammucchiati apposta: questo piano non si deve instradare"],
        pezzi={nome: PezzoNelPiano(x=60, y=60) for nome in scritto.pezzi},
    )
    misura = esegui_piano(
        completato(PRIMO), ammucchiato, catalogo(), simboli(), NAMING
    )
    assert misura.disegno is None
    assert misura.rilievi == []
    assert misura.cedute == ()
    assert misura.errore is not None and "cannot be routed" in misura.errore
    assert len(misura.posa) == len(scritto.pezzi)
    assert {item.component_id for item in misura.posa} == set(scritto.pezzi)


def test_il_piano_puo_chiedere_lo_specchio_e_la_valvola_gira_davvero(
    tmp_path: Path,
) -> None:
    """**D-169 dal piano alla tavola**, sul caso che l'ha prodotta.

    Il PO, il 22 settembre 2026, guardando la tavola 4: la commutatrice va dove
    le sue tre linee si incontrano — ingresso dall'alto, terza via a destra,
    uscita in basso. Fra le quattro rotazioni quella giacitura **non esiste**;
    con lo specchio e' la **270**.

    **Misurato sullo scheletro dell'impianto 4**: il piano che la chiede passa
    da 4 spezzate piegate a **3**, da 5 pieghe a **4** e da 3 sormonti a **2**.
    Qui si sorveglia che `specchio` arrivi **fino alla geometria**: senza, la
    valvola resta girata come prima e la linea che le arriva da destra deve
    girarle intorno con quattro pieghe.
    """
    cartella = ROOT / "docs" / "collaudi" / "DRAW-016" / "prova-camera-pulita-2026-09-21"
    scheletro, sorgente = cartella / "scheletro-4.json", cartella / "piano-4.json"
    if not (scheletro.exists() and sorgente.exists()):
        pytest.skip("il collaudo in camera pulita non c'e' piu'")

    piano = json.loads(sorgente.read_text(encoding="utf-8"))
    piano["pezzi"]["commutatrice-ritorno"] = {
        "x": 102.5,
        "y": 125,
        "rotazione": 270,
        "specchio": True,
        "regola": "D-169 — la commutatrice dove le sue tre linee si incontrano",
    }
    scritto = tmp_path / "piano-specchio.json"
    scritto.write_text(json.dumps(piano, ensure_ascii=False), encoding="utf-8")

    esecuzione = esegui_piano(
        load_project(scheletro), carica_piano(scritto), catalogo(), simboli(), NAMING
    )
    assert esecuzione.errore is None
    assert esecuzione.disegno is not None
    valvola = next(
        item for item in esecuzione.posa if item.component_id == "commutatrice-ritorno"
    )
    assert valvola.specchiato is True
    assert valvola.rotation_deg == 270

    # E le facce sono quelle che il PO ha disegnato.
    manifesto = (
        catalogo()
        .resolve("switching-valve-3way")
        .symbol.manifest.rotated(valvola.rotation_deg, valvola.specchiato)
    )
    assert {port.id: port.face.value for port in manifesto.ports} == {
        "in_a": "top",
        "out": "bottom",
        "in_b": "right",
    }
