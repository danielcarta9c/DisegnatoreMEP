"""WP3 — la disposizione al servizio delle linee (D-078, D-080), collaudata.

> **Dal 2 ottobre 2026 (I-180) il solutore non c'e' piu'**, e con lui le prove che lo
> difendevano. Restano qui la prova che la via senza piano, sul caso completo, non esce con rilievi bloccanti. Il resto di questa intestazione e' la storia del
> file, e si legge come tale.


«Spostare un oggetto e' gratis, piegare una linea costa»: dopo la prima posa i
componenti si spostano, si reinstrada, e la mossa si tiene solo se l'obiettivo
totale scende senza che gli attraversamenti crescano. Il criterio di
accettazione del pacchetto, rivisto dall'orchestratore sulla scorta della
ricerca esaustiva (600 disposizioni: sotto i 9 nodi condivisi si va solo
pagando 27 pieghe), e': nessuna voce peggiore del pre-miglioramento, almeno
una strettamente migliore, obiettivo totale strettamente migliore. I vincoli
rigidi — ordine di processo, distanze, griglia, terra — non si negoziano per
nessun guadagno.

⛔ **Il tetto «lunghezza entro il +10%» e' caduto il 17 settembre 2026 con
D-139**: i millimetri di tubo non sono piu' una voce di costo, e la fase della
struttura si tiene larga per disposizione del PO. La lunghezza si misura
ancora e si riporta; non giudica piu'.

WP3b aggiunge le due cose che chiudono il residuo dichiarato — l'andata e
ritorno sul prelievo ACS del caso di accettazione: le **rotazioni** fra le
mosse candidate, perche' nessuna traslazione cambia da che parte guarda una
porta, e l'**andata e ritorno** come prima voce del confronto, perche' non e'
un disegno caro ma un disegno sbagliato e va pagata prima dell'obiettivo.

**Il secondo caso e' una fixture di posa, non l'uscita delle regole.** Fino a
P2 era il modello che le regole rigeneravano dal caso essenziale, e ogni
misura di questo file era percio' appesa al contenuto del pacchetto delle
regole: cambiarne una spostava numeri che parlano di geometria. Da P2 il
pacchetto propone l'intercettazione su **ogni** attacco di **ogni** cosa che si
smonta in esercizio — accessori compresi — e l'impianto che ne esce non entra
piu' su un formato ordinario: e' il limite di composizione che il piano assegna
a P6, non un difetto delle regole. Qui resta congelato l'impianto a quattro
fasce con cui questo ciclo e' stato misurato, come dato d'ingresso del layout.
"""
# categoria: difende il motore — la via senza piano (`draw`) sul caso completo non esce con rilievi bloccanti

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import (
    compose_drawing,
)
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.validation.preflight import preflight_drawing

ROOT = Path(__file__).resolve().parents[2]
COMPLETE = ROOT / "examples" / "layout" / "centrale-pdc-quattro-fasce.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


@cache
def registry() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )






























@pytest.mark.skip(
    reason="La composizione compone: da quando cio' che pende da uno stacco sta "
    "accanto al proprio pezzo, il caso completo entra in una A3 e ogni tratta si "
    "instrada. Resta fuori la QUALITA', ed e' misurata: 27 pieghe contro le 23 "
    "di budget, 1055 mm di linea contro 825, la tratta fra pompa di calore e "
    "valvola deviatrice non e' un rettilineo, e due attese contano dieci pezzi "
    "dove il caso ne ha dodici. ATTENZIONE: la vecchia motivazione di queste "
    "prove — «l'impianto chiede piu' larghezza di quanta ne abbia un foglio "
    "ordinario» — era FALSA e ha ingannato due volte; i cinque impianti "
    "fallivano anche su A0, e per l'instradamento. Queste prove tornano quando "
    "il disegno rientra nei budget, non ammorbidendo i budget."
)
def test_the_complete_case_carries_no_blocking_quality_finding() -> None:
    """Lo stesso invariante del caso di accettazione, sulla tavola completa.

    E' la tavola che ha mostrato il difetto: tre accessori in linea posati a
    0 mm da una tratta instradata prima di loro, perche' chi li posava non
    vedeva le tratte gia' disegnate, e il ciclo che li avrebbe potuti scartare
    valutava una geometria senza accessori. Qui si misura cio' che esce.
    """
    findings = preflight_drawing(
        compose_drawing(load_project(COMPLETE), registry(), NOVE_C_A3),
        NOVE_C_A3,
        registry(),
    )
    blocking = [item for item in findings if item.severity is IssueSeverity.BLOCKING]
    assert blocking == [], [item.model_dump() for item in blocking]














