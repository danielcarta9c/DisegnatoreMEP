"""Come un rilievo nomina una tratta: con i pezzi che collega, non con il suo id.

**Il collaudo T2 di REL-012, §2.1.5.** I rilievi dicevano «le tratte t11 e t12», e sul
foglio una tratta non porta il suo id: chi legge non aveva modo di trovarle, e il
collaudo ha perso un giro a cercarle. Una tratta si dice coi due pezzi ai suoi capi,
come si dice a voce davanti alla tavola: «la tratta fra COL-01 e VOL-01».

Si legge **dalla tavola**, non dal grafo: il capo di una spezzata sta su una porta,
cioe' sul riquadro di un simbolo posato, e il simbolo porta la sigla che la tavola gli
scrive. Un pezzo senza sigla sul disegno si dice con la sua etichetta, se il foglio la
porta («collettore di distribuzione»), se no — una valvola, un raccordo — col nome della
sua voce in legenda. Una tratta senza spezzata, o i cui capi non toccano niente,
resta detta coi suoi id: e' l'unica cosa che c'e'.
"""

from __future__ import annotations

from disegnatore_mep.layout.geometry import PlacedSymbol, Point, RoutedTrunk, SheetGeometry
from disegnatore_mep.layout.labels import ETICHETTA

TOLLERANZA_MM = 0.05


def _sul_riquadro(punto: Point, pezzo: PlacedSymbol) -> bool:
    x0, y0 = pezzo.origin.x_mm, pezzo.origin.y_mm
    x1, y1 = pezzo.right_mm, pezzo.bottom_mm
    return (
        x0 - TOLLERANZA_MM <= punto.x_mm <= x1 + TOLLERANZA_MM
        and y0 - TOLLERANZA_MM <= punto.y_mm <= y1 + TOLLERANZA_MM
    )


def nome_del_pezzo(sheet: SheetGeometry, pezzo: PlacedSymbol) -> str:
    """La sigla che la tavola scrive sul pezzo, o la sua etichetta scritta sul foglio
    («collettore di distribuzione»), o il nome della sua voce in legenda, o — se
    nemmeno quello c'e' — il suo id."""
    if pezzo.tag:
        return pezzo.tag
    etichetta = next(
        (item.text for item in sheet.labels if item.id == f"{pezzo.component_id}-{ETICHETTA}"), None
    )
    if etichetta:
        return f"«{etichetta}»"
    nome = next((voce.name for voce in sheet.legend if voce.symbol_id == pezzo.symbol_id), None)
    if nome:
        return f"{nome[0].lower()}{nome[1:]}"
    return pezzo.component_id


def _capo(sheet: SheetGeometry, punto: Point) -> PlacedSymbol | None:
    """Il pezzo su cui finisce la spezzata: fra quelli che il punto tocca, il primo
    con una sigla, se no il piu' piccolo — una porta sta sul riquadro del suo pezzo,
    e il riquadro piu' piccolo e' il piu' stretto attorno a lei."""
    toccati = [pezzo for pezzo in sheet.symbols if _sul_riquadro(punto, pezzo)]
    if not toccati:
        return None
    return min(toccati, key=lambda item: (item.tag is None, item.width_mm * item.height_mm))


def nome_della_tratta(sheet: SheetGeometry, route: RoutedTrunk) -> str:
    """«fra COL-01 e VOL-01»: i due pezzi ai capi della spezzata. Senza capi
    riconoscibili, gli id delle tubazioni."""
    disegnati = [segmento for segmento in route.segments if segmento]
    if disegnati:
        capi = [_capo(sheet, disegnati[0][0]), _capo(sheet, disegnati[-1][-1])]
        if capi[0] is not None and capi[1] is not None and capi[0] is not capi[1]:
            return f"fra {nome_del_pezzo(sheet, capi[0])} e {nome_del_pezzo(sheet, capi[1])}"
    return ", ".join(route.connection_ids) if route.connection_ids else route.network_id


def nome_delle_tubazioni(sheet: SheetGeometry, connection_ids: tuple[str, ...] | list[str]) -> str:
    """La tratta della tavola che porta queste tubazioni, detta coi suoi capi; se la
    tavola non ne ha una con queste tubazioni, gli id."""
    cercate = tuple(connection_ids)
    route = next((item for item in sheet.routes if tuple(item.connection_ids) == cercate), None)
    if route is None:
        route = next(
            (item for item in sheet.routes if set(cercate) <= set(item.connection_ids)), None
        )
    if route is None:
        return ", ".join(cercate)
    return nome_della_tratta(sheet, route)


__all__ = ["nome_del_pezzo", "nome_della_tratta", "nome_delle_tubazioni"]
