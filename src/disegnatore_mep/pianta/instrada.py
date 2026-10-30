"""L'instradatore della pianta: la stessa pseudoregola del motore dello schema.

Il PO (I-229): «i sormonti fra linee si pagano, si pagano le curve, anche i
tratti diagonali NON si fanno mai + importante seguire le macro linee
architettoniche». Quattro cose, e qui sono quattro meccanismi:

- **mai diagonali** — non e' un costo, e' la griglia: si cammina solo fra nodi
  vicini in orizzontale o in verticale, e i capi si prolungano sul bordo del
  pezzo lungo la direzione d'uscita. Una spezzata di questo modulo non puo'
  avere un tratto obliquo, e il controllo lo misura lo stesso;
- **le curve si pagano** — come in `layout/route.py` (`TURN_COST`): una curva
  costa quanto `curva_m` di tracciato lungo il muro (mezzo metro, di regola);
- **i sormonti si pagano, le sovrapposizioni no** — attraversare un altro
  tracciato costa `sormonto_m`; percorrerne un tratto per il lungo e' vietato,
  come `taken` nel motore dello schema: due linee sovrapposte sono una linea.
  Anche dentro un fascio: i tracciati del fascio corrono **accanto**, a
  `passo_fascio_m`, e quella corsia costa meno di ogni altra;
- **le macro linee architettoniche** — il costo di un passo dipende da dove
  cade: lungo i muri, a `corsia_da_m`–`corsia_a_m` dalla faccia, costa il
  minimo; in mezzo alla stanza costa di piu', al centro molto di piu'; in un
  disimpegno e' tutto corsia. Un muro si passa solo **di traverso**, dentro
  un'apertura che lascia passare quella quota oppure pagando `foratura_m`, e
  allora il foro va in uscita.

**Fuori dall'edificio si passa solo nelle zone esterne dichiarate** (il
terrazzo, il balcone) e accosto ai pezzi che stanno fuori. Altrove un passo
costa `ESTERNO_NON_DICHIARATO`: l'instradatore ci va solo se non c'e' altra
strada, e il controllo lo ferma come bloccante. Collaudo T3 della 1.6.0: il
cavo UI-UE usciva dal muro ovest e faceva il giro dell'edificio, e
l'alimentazione dell'UE usciva dalla porta di casa — con uscita 0.

**Due pezzi sovrapposti** (`sovrapposto_a`: la centrale sopra il plenum) stanno
a quote diverse: le linee di uno partono dal suo ingombro e possono passare
sotto l'ingombro dell'altro, mai sotto quello di un terzo.

**L'ordine e' dichiarato e stabile**: prima i piu' ingombranti — canali, poi
tubi del refrigerante e dell'acqua, condensa, cavi, bus —, e i tracciati di un
fascio uno dopo l'altro. Chi viene dopo trova occupato quello che ha preso chi
e' venuto prima. A parita' di costo vince l'ordine fisso delle direzioni: lo
stesso ingresso da' lo stesso percorso.
"""

from __future__ import annotations

import heapq
import math
import re
from dataclasses import dataclass, field, replace

from .griglia import (
    ATTRAVERSO_IN_ORIZZONTALE,
    ATTRAVERSO_IN_VERTICALE,
    INCROCIO_DI_MURI,
    Griglia,
)
from .modello import Pianta, Quota, Tracciato

PASSO_IN_CORSIA = 10
"""Il costo di un passo lungo il muro: l'unita' di tutti gli altri costi."""

PASSO_VICINO_AL_MURO = 16
"""Troppo addosso alla faccia del muro: sulla carta la linea tocca il muro."""

PASSO_IN_STANZA = 14
"""Lontano dal muro, ma non in mezzo."""

PASSO_AL_CENTRO = 25
"""In mezzo alla stanza: e' la strada che nessun installatore farebbe."""

PASSO_NEL_FASCIO = 7
"""Accanto a un compagno di fascio, al passo del fascio: costa meno di tutto,
cosi' i tracciati del fascio non si separano."""

ACCOSTO = 6
"""Si aggiunge a un passo troppo vicino a un altro tracciato o a un pezzo: come
`HUG_COST` del motore, non deve far girare una rotta, solo farle scegliere la
corsia libera."""

STRETTO_NEL_FASCIO = 40
"""Si aggiunge a un passo piu' vicino a un compagno di fascio del passo del
fascio. Non e' un accosto qualsiasi: un fascio che si stringe a un nodo sulla
carta e' una linea sola, e sul caso di prova il terzo tracciato frigo si
infilava in mezzo agli altri due, a 5 cm, e li incrociava alla prima curva."""

FUORI_DAL_CONTROSOFFITTO = 5
"""Un tracciato in controsoffitto, dove il controsoffitto non c'e', costa il
triplo: si puo' fare, ma l'instradatore lo evita se puo'."""

ESTERNO_NON_DICHIARATO = 2000
"""Un passo fuori dall'edificio e fuori dalle zone esterne dichiarate: un metro
costa quanto duecento lungo il muro, cinquanta forature. Non e' un divieto solo
perche' una tratta che non trova altra strada si vede meglio disegnata e
fermata dal controllo che ceduta."""

TETTO_DI_ESPANSIONI = 3_000_000

ORDINE_DEI_FLUIDI: dict[str, int] = {
    "supply_air": 0,
    "return_air": 0,
    "refrigerant_liquid": 1,
    "refrigerant_gas": 1,
    "heating_water": 1,
    "chilled_water": 1,
    "domestic_hot_water": 1,
    "cold_water": 1,
    "natural_gas": 1,
    "solar_fluid": 1,
    "condensate": 2,
    "power_supply": 3,
    "interconnection": 3,
    "control_bus": 4,
}
"""Prima i piu' ingombranti: canali, tubi, condensa, cavi, bus."""


@dataclass(frozen=True)
class Attraversamento:
    """Un muro passato da un tracciato: dentro un'apertura, o forandolo."""

    tratta: str
    muro: str
    apertura: str | None
    forato: bool
    punto: tuple[float, float]
    quota: Quota


@dataclass(frozen=True)
class Percorso:
    tratta: str
    punti: tuple[tuple[float, float], ...]
    """I vertici della spezzata, in metri, dal bordo del pezzo di partenza a
    quello di arrivo."""
    ceduto: bool
    nodi: tuple[int, ...] = ()
    attraversamenti: tuple[Attraversamento, ...] = ()
    fuori_dal_controsoffitto_m: float = 0.0
    tronchi: tuple[tuple[tuple[float, float], ...], ...] = ()
    """Una tratta che passa per organi in linea (`passa_per`) e' fatta di
    tronchi, uno per coppia di pezzi: si disegnano e si misurano loro. Allora
    `punti` li unisce passando **dentro** l'organo in linea, in ortogonale."""
    fuori: tuple[tuple[tuple[float, float], ...], ...] = ()
    """Le spezzate, in metri, dei tratti in controsoffitto dove il
    controsoffitto non c'e' (dentro l'edificio): la tavola le disegna."""
    fuori_dalle_zone_m: float = 0.0
    """Quanto corre fuori dall'edificio e fuori dalle zone esterne dichiarate:
    piu' di zero ferma la consegna."""
    fuori_dalle_zone: tuple[tuple[tuple[float, float], ...], ...] = ()
    """Le spezzate di quei tratti, per la tavola."""

    @property
    def linee(self) -> tuple[tuple[tuple[float, float], ...], ...]:
        """Le spezzate da disegnare: i tronchi, o il percorso intero."""
        return self.tronchi or (self.punti,)

    @property
    def lunghezza_m(self) -> float:
        return sum(
            abs(b[0] - a[0]) + abs(b[1] - a[1])
            for linea in self.linee
            for a, b in zip(linea, linea[1:], strict=False)
        )


@dataclass
class _Occupato:
    """Quello che i tracciati gia' instradati tengono."""

    proprietario: list[int]
    fermi: bytearray
    """I vertici e i capi degli altri: non si attraversano."""
    presi: set[int] = field(default_factory=set)
    """I lati gia' percorsi, come `a * n + b` con a < b: vietati."""


def chiave_della_tratta(tratta: str) -> tuple[str, int, str]:
    """T2 prima di T10: il prefisso, il numero, il resto."""
    trovato = re.match(r"^(\D*)(\d+)(.*)$", tratta)
    if trovato is None:
        return (tratta, 0, "")
    return (trovato.group(1), int(trovato.group(2)), trovato.group(3))


def ordine_di_instradamento(tracciati: list[Tracciato]) -> list[Tracciato]:
    """L'ordine dichiarato: per fluido (i piu' ingombranti prima), poi per
    tratta; i tracciati di un fascio di seguito, al posto del primo."""
    gruppi: dict[str, list[Tracciato]] = {}
    for tracciato in tracciati:
        chiave = f"fascio:{tracciato.fascio}" if tracciato.fascio else f"tratta:{tracciato.tratta}"
        gruppi.setdefault(chiave, []).append(tracciato)

    def chiave(t: Tracciato) -> tuple[int, tuple[str, int, str]]:
        return ORDINE_DEI_FLUIDI.get(t.fluido, 2), chiave_della_tratta(t.tratta)

    ordinati = sorted((sorted(g, key=chiave) for g in gruppi.values()), key=lambda g: chiave(g[0]))
    return [t for gruppo in ordinati for t in gruppo]


class Instradatore:
    def __init__(self, pianta: Pianta, griglia: Griglia) -> None:
        self.pianta = pianta
        self.g = griglia
        parametri = pianta.parametri
        passo = griglia.passo
        unita = PASSO_IN_CORSIA / passo
        self.curva = round(unita * parametri.curva_m)
        self.sormonto = round(unita * parametri.sormonto_m)
        self.foratura = round(unita * parametri.foratura_m)
        self.passi_fascio = max(1, round(parametri.passo_fascio_m / passo))
        self.passi_distacco = max(0, round(parametri.distacco_m / passo))
        n = griglia.colonne * griglia.righe
        self.n = n
        self.occupato = _Occupato(proprietario=[0] * n, fermi=bytearray(n))
        self.percorsi: list[tuple[Tracciato, list[int]]] = []
        self._basi: dict[Quota, list[int]] = {}
        self._alone = self._alone_dei_pezzi()
        self.ammesse = [()] + [pianta.quote_ammesse(a) for a in pianta.aperture]
        self.indice_dei_pezzi = {p.sigla: i for i, p in enumerate(pianta.pezzi)}
        self.fatti: dict[str, Percorso] = {}
        self.in_blocco: set[str] = set()
        """Le tratte instradate come un fascio solo: il ripasso non le tocca."""
        sigle = self.indice_dei_pezzi
        self.compagni: dict[int, frozenset[int]] = {
            sigle[sigla] + 1: frozenset(sigle[c] + 1 for c in altri)
            for sigla, altri in pianta.sovrapposti().items()
        }
        """Per pezzo (indice da 1), i pezzi sovrapposti dichiarati."""
        self._attraversabili: dict[tuple[int, int], frozenset[int]] = {}
        self.zone_costo = [1.0] + [z.costo for z in pianta.zone_esterne]
        self._accosti: dict[int, frozenset[int]] = {}
        self._lontano_dal_fascio: set[int] = set()
        """Durante la prova di un fascio: dove la guida non deve passare, perche'
        li' una parallela si e' gia' rotta."""

    # -- i costi fissi --

    def base(self, quota: Quota) -> list[int]:
        if quota in self._basi:
            return self._basi[quota]
        g, parametri = self.g, self.pianta.parametri
        da = parametri.corsia_da_m / g.passo - 1e-6
        a = parametri.corsia_a_m / g.passo + 1e-6
        centro = parametri.centro_da_m / g.passo + 1e-6
        disimpegni = {i for i, s in enumerate(self.pianta.stanze, start=1) if s.disimpegno}
        costi = [PASSO_IN_CORSIA] * self.n
        for k in range(self.n):
            if g.muro[k] or g.pezzo[k]:
                continue
            d = g.distanza[k]
            if d < da:
                costo = PASSO_VICINO_AL_MURO
            elif d <= a or g.stanza[k] in disimpegni:
                costo = PASSO_IN_CORSIA
            elif d > centro:
                costo = PASSO_AL_CENTRO
            else:
                costo = PASSO_IN_STANZA
            if quota == "controsoffitto" and not g.controsoffitto[k] and not g.esterno[k]:
                costo *= FUORI_DAL_CONTROSOFFITTO
            if g.esterno[k]:
                zona = g.zona[k]
                if zona > 0:
                    costo = round(costo * self.zone_costo[zona])
                elif not zona:
                    costo = ESTERNO_NON_DICHIARATO
            costi[k] = costo
        self._basi[quota] = costi
        return costi

    def _alone_dei_pezzi(self) -> list[int]:
        g = self.g
        alone = [0] * self.n
        for indice, (i_min, j_min, i_max, j_max) in enumerate(g.ingombri, start=1):
            for j in range(j_min - 1, j_max + 2):
                for i in range(i_min - 1, i_max + 2):
                    if g.dentro(i, j) and not g.pezzo[g.nodo(i, j)]:
                        alone[g.nodo(i, j)] = indice
        return alone

    def attraversabili(self, i_da: int, i_a: int) -> frozenset[int]:
        """I nodi dei pezzi sovrapposti ai due capi (indici da 0), dove la linea
        puo' passare: sotto l'ingombro del compagno, mai sotto un capo o un terzo."""
        chiave = (i_da, i_a)
        if chiave in self._attraversabili:
            return self._attraversabili[chiave]
        g = self.g
        compagni = self.compagni.get(i_da + 1, frozenset()) | self.compagni.get(i_a + 1, frozenset())
        compagni -= {i_da + 1, i_a + 1}
        nodi: set[int] = set()
        for indice in compagni:
            i_min, j_min, i_max, j_max = g.ingombri[indice - 1]
            for j in range(max(0, j_min), min(g.righe - 1, j_max) + 1):
                for i in range(max(0, i_min), min(g.colonne - 1, i_max) + 1):
                    k = g.nodo(i, j)
                    if set(g.pezzi_del_nodo(k)) <= compagni:
                        nodi.add(k)
        self._attraversabili[chiave] = frozenset(nodi)
        return self._attraversabili[chiave]

    def _accosto_all_esterno(self, raggio: int) -> frozenset[int]:
        """I nodi a non piu' di `raggio` passi da un nodo esterno fuori dalle zone,
        o dall'incrocio di due muri, che non lo sono loro stessi: li' la guida
        di un fascio porterebbe una parallela fuori, o dentro l'incrocio — e il
        fascio si farebbe a tracciati singoli (collaudo T3: il fascio frigo
        passava la tramezza accanto all'incrocio, e stava insieme per il 58 %)."""
        if raggio in self._accosti:
            return self._accosti[raggio]
        g, cols = self.g, self.g.colonne
        out: set[int] = set()
        for k in range(self.n):
            if not g.fuori_dalle_zone(k) and g.giacitura[k] != INCROCIO_DI_MURI:
                continue
            i, j = k % cols, k // cols
            for dj in range(-raggio, raggio + 1):
                for di in range(-raggio, raggio + 1):
                    if g.dentro(i + di, j + dj):
                        vicino = k + dj * cols + di
                        if not g.fuori_dalle_zone(vicino) and g.giacitura[vicino] != INCROCIO_DI_MURI:
                            out.add(vicino)
        self._accosti[raggio] = frozenset(out)
        return self._accosti[raggio]

    # -- i costi di chi e' gia' passato --

    def _penalita(
        self, tracciato: Tracciato, mezza_larghezza: int = 0
    ) -> tuple[dict[int, int], set[int]]:
        g, cols = self.g, self.g.colonne
        penalita: dict[int, int] = {}
        corsia_del_fascio: set[int] = set()
        r = self.passi_distacco + mezza_larghezza
        kf = self.passi_fascio
        for altro, nodi in self.percorsi:
            compagno = tracciato.fascio is not None and altro.fascio == tracciato.fascio
            if not compagno:
                for k in nodi:
                    i, j = k % cols, k // cols
                    for dj in range(-r, r + 1):
                        for di in range(-r, r + 1):
                            if g.dentro(i + di, j + dj):
                                vicino = k + dj * cols + di
                                # Per un fascio, entro la sua mezza larghezza
                                # ci correrebbe sopra una parallela: caro.
                                stretto = mezza_larghezza and max(abs(di), abs(dj)) <= mezza_larghezza
                                costo = STRETTO_NEL_FASCIO if stretto else ACCOSTO
                                penalita[vicino] = max(penalita.get(vicino, 0), costo)
                continue
            for a, b in zip(nodi, nodi[1:], strict=False):
                orizzontale = abs(b - a) == 1
                for k in (a, b):
                    i, j = k % cols, k // cols
                    for passi in range(1, kf + 1):
                        for verso in (-1, 1):
                            di, dj = (0, verso * passi) if orizzontale else (verso * passi, 0)
                            if not g.dentro(i + di, j + dj):
                                continue
                            vicino = k + dj * cols + di
                            if passi == kf:
                                corsia_del_fascio.add(vicino)
                            else:
                                penalita[vicino] = max(penalita.get(vicino, 0), STRETTO_NEL_FASCIO)
        corsia_del_fascio -= set(penalita)
        return penalita, corsia_del_fascio

    # -- la ricerca --

    def _trova(self, tracciato: Tracciato, mezza_larghezza: int = 0) -> list[int] | None:
        g = self.g
        da, a = tracciato.estremo_da, tracciato.estremo_a
        i_da = self.indice_dei_pezzi[da.pezzo]
        i_a = self.indice_dei_pezzi[a.pezzo]
        occ = self.occupato
        sotto = self.attraversabili(i_da, i_a)
        sorgenti = [
            (k, d) for k, d in g.bordo_del_pezzo(i_da, da.lato, sotto)
            if not occ.proprietario[k] and not occ.fermi[k]
        ]
        mete = {
            k: (d + 2) % 4 for k, d in g.bordo_del_pezzo(i_a, a.lato, sotto)
            if not occ.proprietario[k] and not occ.fermi[k]
        }
        if not (sorgenti and mete):
            return None
        if not mezza_larghezza:
            return self._cerca(tracciato, sorgenti, mete, {i_da + 1, i_a + 1}, attraversabili=sotto)
        # Un fascio vuole spazio ai capi: il capo della guida sta ad almeno
        # mezza larghezza dagli spigoli del lato, e i primi e gli ultimi passi
        # sono dritti, perche' le parallele interne non si annullino.
        g, m = self.g, mezza_larghezza
        delta = (1, g.colonne, -1, -g.colonne)
        lati_da = {(k, d) for k, d in sorgenti}
        lati_a = {(k, (d + 2) % 4) for k, d in mete.items()}

        def dritti(k: int, d: int) -> list[int] | None:
            out = []
            for passi in range(1, m + 2):
                i, j = k % g.colonne + (1, 0, -1, 0)[d] * passi, k // g.colonne + (0, 1, 0, -1)[d] * passi
                if not g.dentro(i, j):
                    return None
                nodo = g.nodo(i, j)
                if (g.pezzo[nodo] and nodo not in sotto) or self.occupato.fermi[nodo]:
                    return None
                gv = g.giacitura[nodo]
                if gv == INCROCIO_DI_MURI or (gv == ATTRAVERSO_IN_VERTICALE and d in (0, 2)) or (
                    gv == ATTRAVERSO_IN_ORIZZONTALE and d in (1, 3)
                ):
                    return None
                out.append(nodo)
            return out

        def largo(k: int, d: int, lati: set[tuple[int, int]]) -> bool:
            laterale = delta[(d + 1) % 4]
            return all((k + s * laterale, d) in lati for s in (-m, m))

        prefissi: dict[int, list[int]] = {}
        partenze = []
        for k, d in sorgenti:
            passi = dritti(k, d) if largo(k, d, lati_da) else None
            if passi is not None:
                prefissi[passi[-1]] = [k, *passi[:-1]]
                partenze.append((passi[-1], d))
        suffissi: dict[int, list[int]] = {}
        arrivi: dict[int, int] = {}
        for k, dentro in mete.items():
            fuori = (dentro + 2) % 4
            passi = dritti(k, fuori) if largo(k, fuori, lati_a) else None
            if passi is not None:
                suffissi[passi[-1]] = [*reversed(passi[:-1]), k]
                arrivi[passi[-1]] = dentro
        if not (partenze and arrivi):
            return None
        nodi = self._cerca(tracciato, partenze, arrivi, {i_da + 1, i_a + 1}, m, sotto)
        if nodi is None:
            return None
        return [*prefissi[nodi[0]], *nodi, *suffissi[nodi[-1]]]

    def instrada(self, tracciato: Tracciato) -> Percorso:
        nodi = self._trova(tracciato)
        if nodi is None:
            percorso = self._ceduto(tracciato)
        else:
            self._occupa(tracciato, nodi)
            percorso = self._registra(tracciato, nodi)
        self.fatti[tracciato.tratta] = percorso
        return percorso

    def instrada_il_fascio(self, membri: list[Tracciato]) -> None:
        """Un fascio fra gli stessi due pezzi si instrada **come uno**: il primo
        trova la strada larga quanto il fascio, gli altri ne sono le parallele
        a passo fisso, una per parte. Le curve si annidano da sole — la
        parallela interna gira prima, l'esterna dopo — e il fascio non si
        incrocia mai su se stesso. Se una parallela non passa (un pezzo, un
        incrocio di muri, un tratto gia' preso), i tracciati del fascio si
        instradano uno per uno, con la corsia del fascio che li tiene vicini.

        Se la prima guida non basta, il fascio si instrada uno per uno **e** si
        riprova intero allontanando la guida dai punti dove una parallela si
        rompe (`_prova_il_fascio`): vince il fascio intero, se non costa piu' di
        `PREMIO_DEL_FASCIO` oltre i tracciati singoli, con i pesi della ricerca
        (`_punteggio`)."""
        if self._prova_il_fascio(membri, giri=1):
            return
        nomi = {t.tratta for t in membri}
        for t in membri:
            self.instrada(t)
        singoli = [(t, nodi) for t, nodi in self.percorsi if t.tratta in nomi]
        self.percorsi = [(t, nodi) for t, nodi in self.percorsi if t.tratta not in nomi]
        self._ricostruisci()
        if len(singoli) == len(membri):
            per_tratta = {t.tratta: nodi for t, nodi in singoli}
            punteggio = self._punteggio([per_tratta[t.tratta] for t in membri], membri)
        else:
            punteggio = None  # un tracciato non si e' instradato: il fascio intero e' meglio di niente
        if self._prova_il_fascio(membri, tetto=punteggio, alla_pari=True):
            return
        for t, nodi in singoli:
            self._occupa(t, nodi)

    def _punteggio(self, percorsi: list[list[int]], membri: list[Tracciato]) -> int:
        """Quanto costa un fascio, con i pesi della ricerca: i passi (lungo il
        muro, in mezzo alla stanza, fuori dal controsoffitto, fuori dalle zone
        esterne), le curve, i sormonti con gli altri e fra loro, e le forature —
        una per muro, perche' lo stesso muro a meno di mezzo metro e' un foro
        solo, come in uscita."""
        g = self.g
        fori: set[tuple[str, int, int]] = set()
        costo = 0
        for t, nodi in zip(membri, percorsi, strict=True):
            base = self.base(t.quota)
            costo += sum(PASSO_IN_CORSIA if g.giacitura[k] else base[k] for k in nodi[1:])
            costo += self.curva * max(0, len(_vertici(nodi)) - 2)
            for passaggio in self._attraversamenti(t, nodi):
                if passaggio.forato:
                    fori.add((passaggio.muro, round(passaggio.punto[0] / 0.5), round(passaggio.punto[1] / 0.5)))
        sormonti = sum(self._sormonti(nodi) for nodi in percorsi) + _incroci_fra(percorsi)
        return costo + self.foratura * len(fori) + self.sormonto * sormonti

    def _prova_il_fascio(
        self, membri: list[Tracciato], tetto: int | None = None, giri: int | None = None,
        alla_pari: bool = False,
    ) -> bool:
        """Il fascio intero, se passa; con `tetto`, solo se non costa piu' di
        `tetto` maggiorato di `PREMIO_DEL_FASCIO` (a pari, solo `alla_pari`): il
        costo e' `_punteggio`.

        La guida si cerca larga quanto il fascio, ma la ricerca non sa dove una
        parallela si annulla in una curva stretta o finisce in un incrocio di
        muri. Se una parallela non passa, si riprova la guida tenendola lontana
        da quel punto, fino a `GIRI_DEL_FASCIO` volte (collaudo T3: l'unita'
        interna a 23 cm dalla tramezza, il fascio girava nel corridoio, la
        parallela esterna finiva nel muro e il fascio si faceva a pezzi)."""
        self._lontano_dal_fascio = set()
        try:
            for _ in range(giri or GIRI_DEL_FASCIO):
                guasto: list[int] = []
                validi = self._il_fascio(membri, guasto)
                if validi is not None:
                    break
                if not guasto or not self._allontana_la_guida(membri[0], guasto[0]):
                    return False
            else:
                return False
        finally:
            self._lontano_dal_fascio = set()
        if tetto is not None:
            punteggio = self._punteggio(validi, membri)
            soglia = tetto * (1 + PREMIO_DEL_FASCIO)
            if punteggio > soglia or (punteggio == soglia and not alla_pari):
                return False
        for t, parallela in zip(membri, validi, strict=True):
            self._occupa(t, parallela)
            self._registra(t, parallela)
            self.in_blocco.add(t.tratta)
        return True

    def _il_fascio(self, membri: list[Tracciato], guasto: list[int]) -> list[list[int]] | None:
        """La guida e le sue parallele; se una non passa, `guasto` dice dove."""
        kf = self.passi_fascio
        scarti = [0]
        for indice in range(1, len(membri)):
            scarti.append(kf * ((indice + 1) // 2) * (1 if indice % 2 else -1))
        guida = self._trova(membri[0], max(abs(s) for s in scarti))
        if guida is None:
            return None
        validi: list[list[int]] = []
        usati: set[int] = set()
        for t, scarto in zip(membri, scarti, strict=True):
            parallela = self._parallela(guida, scarto, guasto)
            if parallela is None or not self._percorribile(t, parallela, guasto):
                return None
            if usati & set(parallela):
                guasto.append(min(usati & set(parallela)))
                return None
            usati |= set(parallela)
            validi.append(parallela)
        return validi

    def _allontana_la_guida(self, tracciato: Tracciato, nodo: int) -> bool:
        """Fa pagare alla guida i nodi attorno a quello dove una parallela si e'
        rotta: e' un costo, non un divieto, e vicino a un capo la guida ci passa
        lo stesso se non ha altra strada. Falso se non cambia niente."""
        del tracciato
        g, cols = self.g, self.g.colonne
        raggio = max(1, round(RAGGIO_DEL_GUASTO_M / g.passo))
        i, j = nodo % cols, nodo // cols
        nuovi = {
            g.nodo(i + di, j + dj)
            for dj in range(-raggio, raggio + 1) for di in range(-raggio, raggio + 1)
            if g.dentro(i + di, j + dj)
        }
        if nuovi <= self._lontano_dal_fascio:
            return False
        self._lontano_dal_fascio |= nuovi
        return True

    def ripassa_il_fascio(self, membri: list[Tracciato]) -> bool:
        """Il fascio che al primo giro si e' dovuto instradare a pezzi si
        riprova intero, con gli altri al posto del ripasso: resta se non costa
        piu' dei suoi tracciati presi uno per uno, col premio del fascio."""
        if any(t.tratta in self.in_blocco for t in membri):
            return False
        nomi = {t.tratta for t in membri}
        vecchi = [(t, nodi) for t, nodi in self.percorsi if t.tratta in nomi]
        if len(vecchi) != len(membri):
            return False
        self.percorsi = [(t, nodi) for t, nodi in self.percorsi if t.tratta not in nomi]
        self._ricostruisci()
        per_tratta = {t.tratta: nodi for t, nodi in vecchi}
        prima = self._punteggio([per_tratta[t.tratta] for t in membri], membri)
        if self._prova_il_fascio(membri, tetto=prima):
            return True
        for t, nodi in vecchi:
            self._occupa(t, nodi)
        return False

    def _parallela(self, nodi: list[int], scarto: int, guasto: list[int] | None = None) -> list[int] | None:
        """La spezzata spostata di `scarto` nodi alla sinistra del verso di
        percorrenza (a destra se negativo), con gli spigoli annidati. Se si
        annulla, `guasto` riceve il vertice della guida dove succede."""
        if scarto == 0:
            return list(nodi)
        cols = self.g.colonne
        vertici = [(k % cols, k // cols) for k in _vertici(nodi)]
        if len(vertici) < 2:
            return None
        versi = []
        for (i0, j0), (i1, j1) in zip(vertici, vertici[1:], strict=False):
            di, dj = (i1 > i0) - (i1 < i0), (j1 > j0) - (j1 < j0)
            versi.append((dj, -di))  # la sinistra di (di, dj), con la y in basso
        nuovi = [(vertici[0][0] + versi[0][0] * scarto, vertici[0][1] + versi[0][1] * scarto)]
        for indice in range(1, len(vertici) - 1):
            a, b = versi[indice - 1], versi[indice]
            nuovi.append((vertici[indice][0] + (a[0] + b[0]) * scarto,
                          vertici[indice][1] + (a[1] + b[1]) * scarto))
        nuovi.append((vertici[-1][0] + versi[-1][0] * scarto, vertici[-1][1] + versi[-1][1] * scarto))
        if not self.g.dentro(*nuovi[0]):
            return None
        out: list[int] = [self.g.nodo(*nuovi[0])]
        for indice, ((i0, j0), (i1, j1), verso) in enumerate(zip(nuovi, nuovi[1:], versi, strict=False)):
            di, dj = (i1 > i0) - (i1 < i0), (j1 > j0) - (j1 < j0)
            if (di, dj) != (-verso[1], verso[0]):
                # il tratto interno si e' annullato o rovesciato
                if guasto is not None:
                    guasto.append(self.g.nodo(*vertici[indice + 1]))
                return None
            for p in range(1, abs(i1 - i0) + abs(j1 - j0) + 1):
                if not self.g.dentro(i0 + di * p, j0 + dj * p):
                    return None
                out.append(self.g.nodo(i0 + di * p, j0 + dj * p))
        return out

    def _percorribile(self, tracciato: Tracciato, nodi: list[int], guasto: list[int] | None = None) -> bool:
        """Le stesse regole della ricerca, controllate su un percorso dato. Se non
        passa, `guasto` riceve il nodo dove si ferma."""
        g, n = self.g, self.n
        occ = self.occupato
        da, a = tracciato.estremo_da, tracciato.estremo_a
        i_da, i_a = self.indice_dei_pezzi[da.pezzo], self.indice_dei_pezzi[a.pezzo]
        sotto = self.attraversabili(i_da, i_a)
        partenze = dict(g.bordo_del_pezzo(i_da, da.lato, sotto))
        arrivi = dict(g.bordo_del_pezzo(i_a, a.lato, sotto))
        if len(nodi) < 2 or nodi[0] not in partenze or nodi[-1] not in arrivi:
            return False
        delta = {1: 0, g.colonne: 1, -1: 2, -g.colonne: 3}
        verso = partenze[nodi[0]]
        for k in (nodi[0], nodi[-1]):
            if occ.proprietario[k] or occ.fermi[k]:
                return False
        for prima, dopo in zip(nodi, nodi[1:], strict=False):
            nuovo = delta.get(dopo - prima)
            gv = g.giacitura[dopo]
            rotto = (
                nuovo is None or nuovo == (verso + 2) % 4
                or ((g.giacitura[prima] or occ.proprietario[prima]) and nuovo != verso)
                or (g.pezzo[dopo] and dopo not in sotto) or occ.fermi[dopo]
                # La parallela di un fascio esce dalle zone esterne dove la
                # guida ci sta dentro.
                or g.fuori_dalle_zone(dopo)
                or (prima * n + dopo if prima < dopo else dopo * n + prima) in occ.presi
                or gv == INCROCIO_DI_MURI
                or (gv == ATTRAVERSO_IN_VERTICALE and nuovo in (0, 2))
                or (gv == ATTRAVERSO_IN_ORIZZONTALE and nuovo in (1, 3))
            )
            if rotto:
                if guasto is not None:
                    guasto.append(dopo)
                return False
            verso = nuovo
        return (verso + 2) % 4 == arrivi[nodi[-1]]

    def _registra(self, tracciato: Tracciato, nodi: list[int]) -> Percorso:
        i_da = self.indice_dei_pezzi[tracciato.estremo_da.pezzo]
        i_a = self.indice_dei_pezzi[tracciato.estremo_a.pezzo]
        percorso = self._percorso(tracciato, nodi, i_da, i_a)
        self.fatti[tracciato.tratta] = percorso
        return percorso

    def _sormonti(self, nodi: list[int]) -> int:
        """I nodi in cui il percorso attraversa un tracciato gia' posato."""
        return sum(1 for k in nodi if self.occupato.proprietario[k])

    def _ricostruisci(self) -> None:
        tenuti = self.percorsi
        self.occupato = _Occupato(proprietario=[0] * self.n, fermi=bytearray(self.n))
        self.percorsi = []
        for tracciato, nodi in tenuti:
            self._occupa(tracciato, nodi)

    def ripassa(self, tracciato: Tracciato) -> bool:
        """Toglie il tracciato, lo rifa' con tutti gli altri al loro posto, e
        tiene il nuovo percorso se sormonta meno (a parita', se e' piu' corto o
        ha meno curve). Torna vero se e' cambiato."""
        presenti = [i for i, (t, _) in enumerate(self.percorsi) if t.tratta == tracciato.tratta]
        if not presenti or tracciato.tratta in self.in_blocco:
            return False
        _, vecchi = self.percorsi.pop(presenti[0])
        self._ricostruisci()
        prima = self._sormonti(vecchi)
        if prima == 0:
            self._occupa(tracciato, vecchi)
            return False
        nuovi = self._trova(tracciato)

        def misura(nodi: list[int]) -> tuple[int, int, int]:
            return (self._sormonti(nodi), len(_vertici(nodi)), len(nodi))

        if nuovi is None or misura(nuovi) >= misura(vecchi):
            self._occupa(tracciato, vecchi)
            return False
        self._occupa(tracciato, nuovi)
        self._registra(tracciato, nuovi)
        return True

    def _cerca(
        self, tracciato: Tracciato, sorgenti: list[tuple[int, int]], mete: dict[int, int],
        pezzi_suoi: set[int], mezza_larghezza: int = 0, attraversabili: frozenset[int] = frozenset(),
    ) -> list[int] | None:
        """L'A* su (nodo, direzione). Con `mezza_larghezza` cerca la strada di
        un fascio intero: chi gli passa accanto, i pezzi e i muri lungo cui corre
        devono stare piu' lontani, perche' ai lati del percorso ci sono gli
        altri tracciati del fascio."""
        g, n, cols = self.g, self.n, self.g.colonne
        base = self.base(tracciato.quota)
        penalita, corsia_del_fascio = self._penalita(tracciato, mezza_larghezza)
        if mezza_larghezza:
            distanza = g.distanza
            for indice, (i_min, j_min, i_max, j_max) in enumerate(g.ingombri, start=1):
                if indice in pezzi_suoi:
                    continue
                r = mezza_larghezza + 1
                for j in range(j_min - r, j_max + r + 1):
                    for i in range(i_min - r, i_max + r + 1):
                        if g.dentro(i, j):
                            k = g.nodo(i, j)
                            penalita[k] = max(penalita.get(k, 0), STRETTO_NEL_FASCIO)
            for k in range(n):
                if not g.muro[k] and distanza[k] <= mezza_larghezza:
                    penalita[k] = penalita.get(k, 0) + 3 * ACCOSTO
            # Le parallele non escono dalle zone esterne: la guida ne sta
            # lontana quanto il fascio e' largo.
            for k in self._accosto_all_esterno(mezza_larghezza):
                penalita[k] = penalita.get(k, 0) + ESTERNO_NON_DICHIARATO
            for k in self._lontano_dal_fascio:
                penalita[k] = penalita.get(k, 0) + ESTERNO_NON_DICHIARATO
        alone = self._alone
        pezzo, giacitura, apertura = g.pezzo, g.giacitura, g.apertura
        proprietario, fermi, presi = self.occupato.proprietario, self.occupato.fermi, self.occupato.presi
        ammesse = self.ammesse
        quota = tracciato.quota
        curva, sormonto, foratura = self.curva, self.sormonto, self.foratura
        passo_minimo = PASSO_NEL_FASCIO if tracciato.fascio else PASSO_IN_CORSIA
        delta = (1, cols, -1, -cols)

        colonne_mete = [k % cols for k in mete]
        righe_mete = [k // cols for k in mete]
        gi0, gi1 = min(colonne_mete), max(colonne_mete)
        gj0, gj1 = min(righe_mete), max(righe_mete)

        def stima(k: int) -> int:
            i, j = k % cols, k // cols
            dx = gi0 - i if i < gi0 else (i - gi1 if i > gi1 else 0)
            dy = gj0 - j if j < gj0 else (j - gj1 if j > gj1 else 0)
            return (dx + dy) * passo_minimo

        infinito = 1 << 60
        migliore: dict[int, int] = {}
        venuto: dict[int, int] = {}
        coda: list[tuple[int, int, int]] = []
        for k, d in sorgenti:
            stato = k * 4 + d
            migliore[stato] = 0
            heapq.heappush(coda, (stima(k), 0, stato))
            if k in mete:
                finale = 0 if d == mete[k] else curva
                heapq.heappush(coda, (finale, finale, -stato - 1))
        espansioni = 0
        while coda:
            _, costo, stato = heapq.heappop(coda)
            if stato < 0:
                stato = -stato - 1
                nodi = [stato // 4]
                while stato in venuto:
                    stato = venuto[stato]
                    nodi.append(stato // 4)
                nodi.reverse()
                return nodi
            if costo > migliore.get(stato, infinito):
                continue
            espansioni += 1
            if espansioni > TETTO_DI_ESPANSIONI:
                return None
            k, d = divmod(stato, 4)
            i = k % cols
            nel_muro = giacitura[k] != 0
            su_un_altro = proprietario[k] != 0
            for nd in range(4):
                if nd == (d + 2) % 4:
                    continue
                if (nel_muro or su_un_altro) and nd != d:
                    continue
                if (nd == 0 and i + 1 >= cols) or (nd == 2 and i == 0):
                    continue
                vicino = k + delta[nd]
                if vicino < 0 or vicino >= n or fermi[vicino] or (pezzo[vicino] and vicino not in attraversabili):
                    continue
                lato = k * n + vicino if k < vicino else vicino * n + k
                if lato in presi:
                    continue
                gv = giacitura[vicino]
                if gv:
                    if gv == INCROCIO_DI_MURI:
                        continue
                    if gv == ATTRAVERSO_IN_VERTICALE and nd in (0, 2):
                        continue
                    if gv == ATTRAVERSO_IN_ORIZZONTALE and nd in (1, 3):
                        continue
                    passo = PASSO_IN_CORSIA
                    if not nel_muro:
                        varco = apertura[vicino]
                        if not (varco and quota in ammesse[varco]):
                            passo += foratura
                else:
                    passo = base[vicino]
                    if vicino in corsia_del_fascio and passo > PASSO_NEL_FASCIO:
                        passo = PASSO_NEL_FASCIO
                    passo += penalita.get(vicino, 0)
                    if alone[vicino] and alone[vicino] not in pezzi_suoi:
                        passo += ACCOSTO
                if nd != d:
                    passo += curva
                if proprietario[vicino]:
                    passo += sormonto
                nuovo = costo + passo
                prossimo = vicino * 4 + nd
                if nuovo < migliore.get(prossimo, infinito):
                    migliore[prossimo] = nuovo
                    venuto[prossimo] = stato
                    heapq.heappush(coda, (nuovo + stima(vicino), nuovo, prossimo))
                    if vicino in mete:
                        finale = nuovo + (0 if nd == mete[vicino] else curva)
                        heapq.heappush(coda, (finale, finale, -prossimo - 1))
        return None

    # -- dopo la ricerca --

    def _occupa(self, tracciato: Tracciato, nodi: list[int]) -> None:
        occ, n = self.occupato, self.n
        numero = len(self.percorsi) + 1
        for k in nodi:
            if not occ.proprietario[k]:
                occ.proprietario[k] = numero
        for a, b in zip(nodi, nodi[1:], strict=False):
            occ.presi.add(a * n + b if a < b else b * n + a)
        for k in _vertici(nodi):
            occ.fermi[k] = 1
        self.percorsi.append((tracciato, nodi))

    def _percorso(self, tracciato: Tracciato, nodi: list[int], i_da: int, i_a: int) -> Percorso:
        g = self.g
        vertici = _vertici(nodi)
        punti = [g.punto(k) for k in vertici]
        punti.insert(0, _sul_bordo(self.pianta.pezzi[i_da].rettangolo, g.punto(nodi[0]),
                                   g.punto(nodi[1]) if len(nodi) > 1 else None))
        punti.append(_sul_bordo(self.pianta.pezzi[i_a].rettangolo, g.punto(nodi[-1]),
                                g.punto(nodi[-2]) if len(nodi) > 1 else None))
        punti = _senza_ripetizioni(punti)
        fuori = 0.0
        tratti_fuori: list[tuple[tuple[float, float], ...]] = []
        if tracciato.quota == "controsoffitto":

            def scoperto(k: int) -> bool:
                return not (g.controsoffitto[k] or g.muro[k] or g.esterno[k])

            corsa: list[int] = []
            for a, b in zip(nodi, nodi[1:], strict=False):
                if scoperto(a) and scoperto(b):
                    fuori += g.passo
                    if not corsa:
                        corsa = [a]
                    corsa.append(b)
                    continue
                if corsa:
                    tratti_fuori.append(tuple(g.punto(k) for k in _vertici(corsa)))
                    corsa = []
            if corsa:
                tratti_fuori.append(tuple(g.punto(k) for k in _vertici(corsa)))
        esterno = 0.0
        tratti_esterni: list[tuple[tuple[float, float], ...]] = []
        corsa = []
        for a, b in zip(nodi, nodi[1:], strict=False):
            if g.fuori_dalle_zone(a) and g.fuori_dalle_zone(b):
                esterno += g.passo
                if not corsa:
                    corsa = [a]
                corsa.append(b)
                continue
            if corsa:
                tratti_esterni.append(tuple(g.punto(k) for k in _vertici(corsa)))
                corsa = []
        if corsa:
            tratti_esterni.append(tuple(g.punto(k) for k in _vertici(corsa)))
        return Percorso(
            tratta=tracciato.tratta, punti=tuple(punti), ceduto=False, nodi=tuple(nodi),
            attraversamenti=self._attraversamenti(tracciato, nodi),
            fuori_dal_controsoffitto_m=round(fuori, 3), fuori=tuple(tratti_fuori),
            fuori_dalle_zone_m=round(esterno, 3), fuori_dalle_zone=tuple(tratti_esterni),
        )

    def _attraversamenti(self, tracciato: Tracciato, nodi: list[int]) -> tuple[Attraversamento, ...]:
        g, pianta = self.g, self.pianta
        out: list[Attraversamento] = []
        corsa: list[int] = []
        for k in [*nodi, -1]:
            if k >= 0 and g.muro[k] and not g.pezzo[k]:
                corsa.append(k)
                continue
            if corsa:
                muri = sorted({g.muro[c] for c in corsa})
                varchi = sorted({g.apertura[c] for c in corsa if g.apertura[c]})
                varco = varchi[0] if varchi else 0
                ammesso = bool(varco) and tracciato.quota in self.ammesse[varco]
                mezzo = g.punto(corsa[len(corsa) // 2])
                out.append(
                    Attraversamento(
                        tratta=tracciato.tratta,
                        muro=pianta.muri[muri[0] - 1].id,
                        apertura=pianta.aperture[varco - 1].id if varco else None,
                        forato=not ammesso,
                        punto=mezzo,
                        quota=tracciato.quota,
                    )
                )
                corsa = []
        return tuple(out)

    def _ceduto(self, tracciato: Tracciato) -> Percorso:
        """La tratta che non si instrada: una L fra i centri dei due pezzi,
        tratteggiata. Non evita niente — e' il segno che dice *qui manca una
        tratta* (D-150) — e non e' obliqua nemmeno lei."""
        da = self.pianta.pezzi[self.indice_dei_pezzi[tracciato.estremo_da.pezzo]]
        a = self.pianta.pezzi[self.indice_dei_pezzi[tracciato.estremo_a.pezzo]]
        punti = _senza_ripetizioni([(da.x, da.y), (a.x, da.y), (a.x, a.y)])
        return Percorso(tratta=tracciato.tratta, punti=tuple(punti), ceduto=True)


def _incroci_fra(percorsi: list[list[int]]) -> int:
    """I nodi che due percorsi hanno in comune: i loro sormonti reciproci."""
    visti: set[int] = set()
    comuni = 0
    for nodi in percorsi:
        propri = set(nodi)
        comuni += len(propri & visti)
        visti |= propri
    return comuni


def _vertici(nodi: list[int]) -> list[int]:
    if len(nodi) < 3:
        return list(nodi)
    out = [nodi[0]]
    for prima, qui, dopo in zip(nodi, nodi[1:], nodi[2:], strict=False):
        if qui - prima != dopo - qui:
            out.append(qui)
    out.append(nodi[-1])
    return out


def _sul_bordo(
    rettangolo: tuple[float, float, float, float], fuori: tuple[float, float],
    verso: tuple[float, float] | None,
) -> tuple[float, float]:
    """Il punto del bordo del pezzo davanti al nodo esterno, lungo la retta che
    unisce il pezzo al nodo: il capo si prolunga senza piegare."""
    x0, y0, x1, y1 = rettangolo
    x, y = fuori
    if x < x0 - 1e-9:
        return (x0, y)
    if x > x1 + 1e-9:
        return (x1, y)
    if y < y0 - 1e-9:
        return (x, y0)
    if y > y1 + 1e-9:
        return (x, y1)
    del verso
    return (x, y)


def _senza_ripetizioni(punti: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for p in punti:
        p = (round(p[0], 6), round(p[1], 6))
        if not out or math.dist(p, out[-1]) > 1e-9:
            out.append(p)
    # Tre punti in fila: il vertice di mezzo non e' un vertice.
    pulito: list[tuple[float, float]] = []
    for p in out:
        if len(pulito) >= 2:
            a, b = pulito[-2], pulito[-1]
            if (abs(a[0] - b[0]) < 1e-9 and abs(b[0] - p[0]) < 1e-9) or (
                abs(a[1] - b[1]) < 1e-9 and abs(b[1] - p[1]) < 1e-9
            ):
                pulito[-1] = p
                continue
        pulito.append(p)
    return pulito


def fasci_in_blocco(tracciati: list[Tracciato]) -> dict[str, list[Tracciato]]:
    """I fasci i cui tracciati vanno tutti fra gli stessi due pezzi, con gli
    stessi lati: si instradano come uno. Dal primo tracciato del fascio
    nell'ordine di instradamento, i membri in quell'ordine."""
    gruppi: dict[tuple[object, ...], list[Tracciato]] = {}
    for t in ordine_di_instradamento(tracciati):
        if t.fascio is None:
            continue
        da, a = t.estremo_da, t.estremo_a
        gruppi.setdefault((t.fascio, da.pezzo, da.lato, a.pezzo, a.lato), []).append(t)
    per_fascio: dict[str, int] = {}
    for chiave in gruppi:
        per_fascio[str(chiave[0])] = per_fascio.get(str(chiave[0]), 0) + 1
    return {
        membri[0].tratta: membri
        for chiave, membri in gruppi.items()
        if len(membri) > 1 and per_fascio[str(chiave[0])] == 1
    }


PREMIO_DEL_FASCIO = 0.5
"""Un fascio intero resta anche se costa fino al 50 % in piu' dei suoi tracciati
presi uno per uno: tre linee frigo che si separano sono tre tracce e una tavola
che non si legge (collaudo T3: il fascio stava insieme per il 58 %, e il gas
passava dall'ingresso mentre il liquido e il cavo attraversavano il
soggiorno). Misurato (`_punteggio`): T3 +45 % e T1 +6 %, il fascio resta
intero; l'esempio +65 % al primo giro (si fa a tracciati singoli), poi al
ripasso il fascio intero costa l'1 % in meno e resta lui. Un parametro da
tarare sulle tavole, non una costante di natura."""

RAGGIO_DEL_GUASTO_M = 0.25
"""Quanto attorno al punto dove una parallela si e' rotta la guida paga per passare."""

GIRI_DEL_FASCIO = 6
"""Quante guide si provano per un fascio prima di farlo a tracciati singoli."""

GIRI_DI_RIPASSO = 2
"""Quante volte si ripassano i tracciati che sormontano (vedi `instrada_tutto`)."""


def instrada_tutto(pianta: Pianta, griglia: Griglia) -> list[Percorso]:
    """Tutti i tracciati, nell'ordine dichiarato; poi il **ripasso**.

    Chi viene prima prende la strada migliore e chi viene dopo paga: sul caso di
    prova il primo ramo del plenum prendeva la corsia alta e il secondo, che
    andava alla bocchetta subito sopra, lo doveva sormontare. Un sormonto
    evitabile. Il ripasso toglie, uno alla volta e nello stesso ordine, ogni
    tracciato che sormonta un altro, e lo rifa' con tutti gli altri gia' al
    loro posto; il nuovo percorso resta se sormonta meno, a parita' se costa
    meno. Deterministico come il primo giro, e con un tetto di giri dichiarato.

    Una tratta con organi in linea (`passa_per`) si instrada a tronchi, uno per
    coppia di pezzi, e torna **una**: un numero, una scritta, una lunghezza.

    Torna i percorsi nell'ordine in cui la pianta li elenca."""
    instradatore = Instradatore(pianta, griglia)
    da_fare, tronchi = tronchi_da_instradare(pianta)
    ordine = ordine_di_instradamento(da_fare)
    blocchi = fasci_in_blocco(da_fare)
    fatti: set[str] = set()
    for tracciato in ordine:
        if tracciato.tratta in fatti:
            continue
        membri = blocchi.get(tracciato.tratta)
        if membri:
            instradatore.instrada_il_fascio(membri)
            fatti |= {m.tratta for m in membri}
        else:
            instradatore.instrada(tracciato)
    for _ in range(GIRI_DI_RIPASSO):
        cambiato = False
        for tracciato in ordine:
            if tracciato.tratta in blocchi:
                cambiato |= instradatore.ripassa_il_fascio(blocchi[tracciato.tratta])
            cambiato |= instradatore.ripassa(tracciato)
        if not cambiato:
            break
    out: list[Percorso] = []
    for tracciato in pianta.tracciati:
        if tracciato.tratta in tronchi:
            out.append(unisci_i_tronchi(tracciato.tratta, [instradatore.fatti[n] for n in tronchi[tracciato.tratta]]))
        else:
            out.append(instradatore.fatti[tracciato.tratta])
    return out


SEPARATORE_DEI_TRONCHI = "/"
"""Il nome interno di un tronco: «T10/1», «T10/2». Non esce dall'instradatore."""


def tronchi_da_instradare(pianta: Pianta) -> tuple[list[Tracciato], dict[str, list[str]]]:
    """I tracciati da cercare: quelli con organi in linea, spezzati in tronchi."""
    out: list[Tracciato] = []
    tronchi: dict[str, list[str]] = {}
    for tracciato in pianta.tracciati:
        if not tracciato.passa_per:
            out.append(tracciato)
            continue
        nomi: list[str] = []
        for indice, (da, a) in enumerate(pianta.tronchi(tracciato), start=1):
            nome = f"{tracciato.tratta}{SEPARATORE_DEI_TRONCHI}{indice}"
            out.append(tracciato.model_copy(update={"tratta": nome, "da": da, "a": a, "passa_per": []}))
            nomi.append(nome)
        tronchi[tracciato.tratta] = nomi
    return out, tronchi


def unisci_i_tronchi(tratta: str, parti: list[Percorso]) -> Percorso:
    """I tronchi in un percorso solo. Fra un tronco e il successivo la spezzata
    passa dentro l'organo in linea con un gomito ortogonale: sta sotto il pezzo,
    non si vede e non si misura, ma tiene la regola dei diagonali."""
    punti: list[tuple[float, float]] = []
    for parte in parti:
        if punti:
            fine, inizio = punti[-1], parte.punti[0]
            if abs(fine[0] - inizio[0]) > 1e-9 and abs(fine[1] - inizio[1]) > 1e-9:
                punti.append((inizio[0], fine[1]))
        punti.extend(parte.punti)
    return Percorso(
        tratta=tratta,
        punti=tuple(_senza_ripetizioni(punti)),
        ceduto=any(p.ceduto for p in parti),
        nodi=tuple(k for p in parti for k in p.nodi),
        attraversamenti=tuple(replace(a, tratta=tratta) for p in parti for a in p.attraversamenti),
        fuori_dal_controsoffitto_m=round(sum(p.fuori_dal_controsoffitto_m for p in parti), 3),
        tronchi=tuple(p.punti for p in parti),
        fuori=tuple(f for p in parti for f in p.fuori),
        fuori_dalle_zone_m=round(sum(p.fuori_dalle_zone_m for p in parti), 3),
        fuori_dalle_zone=tuple(f for p in parti for f in p.fuori_dalle_zone),
    )
