"""I controlli misurati della pianta, sulla geometria che la tavola disegna.

Come i rilievi del motore dello schema: un numero e l'elenco di chi lo fa.
Bloccano la consegna le diagonali, le sovrapposizioni, le scritte su una linea
e le tratte non instradate; sormonti e forature sono fatti da guardare — un
sormonto si paga ma si puo' fare, una foratura e' lavoro dell'installatore —, e
la tavola li dice.

Si misurano anche se l'instradatore e' costruito per non produrli: e' il
controllo che lo dimostra sulla tavola finita, non il codice che lo promette.

**I richiami si misurano** (collaudo REL-012, t1: «scritte che toccano una
linea: 0» non li guardava, e i richiami attraversavano la UI, il fascio frigo,
una tramezza e mezzo corridoio). Un richiamo piu' lungo di
`RICHIAMO_MASSIMO_MM`, o che attraversa un muro, un pezzo che non e' il suo,
una scritta o piu' di una linea, ferma la consegna; quello che attraversa una
linea sola si conta e si dice.

**Una linea non passa sopra un pezzo che non e' un suo capo** (ne' un organo in
linea suo, ne' un pezzo dichiarato sovrapposto a un suo capo): ferma la consegna.

**Fermano la consegna anche** (collaudo T3 della 1.6.0, dove la pianta usciva
con 0 e non si consegnava): una tratta che corre fuori dall'edificio fuori
dalle zone esterne dichiarate; due pezzi sovrapposti senza che uno lo dichiari;
un numero di tratta che nella distinta collega pezzi diversi.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from .instrada import Percorso
from .modello import Pianta
from .scritte import (
    LINEE_PER_RICHIAMO,
    RICHIAMO_MASSIMO_MM,
    Rettangolo,
    ScrittaPosata,
    _riquadro_del_segmento,
    _segmento_tocca,
    _sovrapposti,
    esce_di_traverso,
)

EPS = 1e-6

Punto = tuple[float, float]


@dataclass
class Rilievi:
    diagonali: list[str] = field(default_factory=list)
    sormonti: list[str] = field(default_factory=list)
    sovrapposizioni: list[str] = field(default_factory=list)
    scritte_su_linee: list[str] = field(default_factory=list)
    scritte_su_scritte: list[str] = field(default_factory=list)
    fori_fuori_dalle_aperture: list[str] = field(default_factory=list)
    tratte_cedute: list[str] = field(default_factory=list)
    fasci: dict[str, float] = field(default_factory=dict)
    """Per fascio: la parte dei tracciati che corre accanto a un compagno, al
    passo del fascio (1 = tutta)."""
    fuori_dal_controsoffitto_m: dict[str, float] = field(default_factory=dict)
    richiami: list[str] = field(default_factory=list)
    """Tutti i richiami, con la lunghezza sulla carta."""
    richiamo_piu_lungo_mm: float = 0.0
    richiami_lunghi: list[str] = field(default_factory=list)
    richiami_che_attraversano: list[str] = field(default_factory=list)
    """Un muro, un pezzo non suo, una scritta, o piu' di una linea: bloccante."""
    richiami_su_una_linea: list[str] = field(default_factory=list)
    """Una linea sola: ammesso, e contato."""
    scritte_in_legenda: list[str] = field(default_factory=list)
    linee_sui_pezzi: list[str] = field(default_factory=list)
    scritte_nel_dettaglio: list[str] = field(default_factory=list)
    """Le scritte che a 1:50 non stanno e si posano nel riquadro di dettaglio."""
    misure_oltre_la_lunghezza: list[str] = field(default_factory=list)
    """La misura in pianta supera la lunghezza del progettista di oltre lo
    scarto ammesso: non ferma, ma si dice sulla tavola e in console."""
    fuori_dalle_zone_esterne: list[str] = field(default_factory=list)
    """Le tratte che escono dall'edificio fuori dalle zone esterne dichiarate."""
    pezzi_sovrapposti: list[str] = field(default_factory=list)
    """Due pezzi che si sovrappongono in pianta senza che uno lo dichiari."""
    confronto: list[str] = field(default_factory=list)
    """Le discordanze con la distinta e il grafo (`--distinta`, `--grafo`)."""
    confronto_bloccante: list[str] = field(default_factory=list)
    """Le discordanze che fermano: un numero di tratta che collega pezzi diversi."""

    def unisci_le_scritte(self, altri: Rilievi, dove: str) -> None:
        """Le scritte e i richiami di un'altra tavola (il dettaglio), col posto davanti."""
        for nome in ("scritte_su_linee", "scritte_su_scritte", "richiami", "richiami_lunghi",
                     "richiami_che_attraversano", "richiami_su_una_linea", "scritte_in_legenda"):
            getattr(self, nome).extend(f"{dove}: {voce}" for voce in getattr(altri, nome))
        self.richiamo_piu_lungo_mm = max(self.richiamo_piu_lungo_mm, altri.richiamo_piu_lungo_mm)

    @property
    def bloccanti(self) -> list[str]:
        out: list[str] = []
        if self.richiami_lunghi:
            out.append(f"{len(self.richiami_lunghi)} richiami piu' lunghi di {RICHIAMO_MASSIMO_MM:g} mm")
        if self.richiami_che_attraversano:
            out.append(f"{len(self.richiami_che_attraversano)} richiami che attraversano muri, pezzi, "
                       "scritte o piu' di una linea")
        if self.linee_sui_pezzi:
            out.append(f"{len(self.linee_sui_pezzi)} linee sopra un pezzo che non e' un loro capo")
        if self.diagonali:
            out.append(f"{len(self.diagonali)} tratti diagonali")
        if self.sovrapposizioni:
            out.append(f"{len(self.sovrapposizioni)} sovrapposizioni fra tracciati")
        if self.scritte_su_linee:
            out.append(f"{len(self.scritte_su_linee)} scritte che toccano una linea")
        if self.scritte_su_scritte:
            out.append(f"{len(self.scritte_su_scritte)} scritte sopra altre scritte")
        if self.tratte_cedute:
            out.append(f"{len(self.tratte_cedute)} tratte non instradate")
        out += [
            f"la tratta esce dall'edificio fuori dalle zone esterne dichiarate: {voce}"
            for voce in self.fuori_dalle_zone_esterne
        ]
        out += [f"pezzi sovrapposti senza «sovrapposto_a»: {voce}" for voce in self.pezzi_sovrapposti]
        out += self.confronto_bloccante
        return out

    def come_dati(self) -> dict[str, object]:
        return {
            "diagonali": len(self.diagonali),
            "sormonti": len(self.sormonti),
            "sovrapposizioni": len(self.sovrapposizioni),
            "scritte_su_linee": len(self.scritte_su_linee),
            "scritte_su_scritte": len(self.scritte_su_scritte),
            "fori_fuori_dalle_aperture": len(self.fori_fuori_dalle_aperture),
            "tratte_cedute": len(self.tratte_cedute),
            "fasci_in_parallelo": {k: round(v, 3) for k, v in sorted(self.fasci.items())},
            "fuori_dal_controsoffitto_m": dict(sorted(self.fuori_dal_controsoffitto_m.items())),
            "richiami": len(self.richiami),
            "richiamo_piu_lungo_mm": round(self.richiamo_piu_lungo_mm, 1),
            "richiamo_massimo_mm": RICHIAMO_MASSIMO_MM,
            "richiami_lunghi": len(self.richiami_lunghi),
            "richiami_che_attraversano": len(self.richiami_che_attraversano),
            "richiami_su_una_linea": len(self.richiami_su_una_linea),
            "scritte_in_legenda": len(self.scritte_in_legenda),
            "linee_sui_pezzi": len(self.linee_sui_pezzi),
            "misure_oltre_la_lunghezza": len(self.misure_oltre_la_lunghezza),
            "scritte_nel_dettaglio": len(self.scritte_nel_dettaglio),
            "fuori_dalle_zone_esterne": len(self.fuori_dalle_zone_esterne),
            "pezzi_sovrapposti": len(self.pezzi_sovrapposti),
            "discordanze_con_distinta_e_grafo": len(self.confronto) + len(self.confronto_bloccante),
            "bloccanti": self.bloccanti,
            "elenco": {
                "diagonali": self.diagonali,
                "sormonti": self.sormonti,
                "sovrapposizioni": self.sovrapposizioni,
                "scritte_su_linee": self.scritte_su_linee,
                "scritte_su_scritte": self.scritte_su_scritte,
                "fori_fuori_dalle_aperture": self.fori_fuori_dalle_aperture,
                "tratte_cedute": self.tratte_cedute,
                "richiami": self.richiami,
                "richiami_lunghi": self.richiami_lunghi,
                "richiami_che_attraversano": self.richiami_che_attraversano,
                "richiami_su_una_linea": self.richiami_su_una_linea,
                "scritte_in_legenda": self.scritte_in_legenda,
                "linee_sui_pezzi": self.linee_sui_pezzi,
                "misure_oltre_la_lunghezza": self.misure_oltre_la_lunghezza,
                "scritte_nel_dettaglio": self.scritte_nel_dettaglio,
                "fuori_dalle_zone_esterne": self.fuori_dalle_zone_esterne,
                "pezzi_sovrapposti": self.pezzi_sovrapposti,
                "discordanze_con_distinta_e_grafo": [*self.confronto_bloccante, *self.confronto],
            },
        }


def segmenti(punti: Sequence[Punto]) -> list[tuple[Punto, Punto]]:
    return [(a, b) for a, b in zip(punti, punti[1:], strict=False) if a != b]


def diagonale(a: Punto, b: Punto) -> bool:
    return abs(a[0] - b[0]) > EPS and abs(a[1] - b[1]) > EPS


def _incrocio(s: tuple[Punto, Punto], t: tuple[Punto, Punto]) -> Punto | None:
    """Il punto in cui un tratto orizzontale e uno verticale si toccano."""
    (a, b), (c, d) = s, t
    s_orizzontale = abs(a[1] - b[1]) < EPS
    t_orizzontale = abs(c[1] - d[1]) < EPS
    if s_orizzontale == t_orizzontale:
        return None
    if not s_orizzontale:
        (a, b), (c, d) = (c, d), (a, b)
    y, x = a[1], c[0]
    if min(a[0], b[0]) - EPS <= x <= max(a[0], b[0]) + EPS and min(c[1], d[1]) - EPS <= y <= max(c[1], d[1]) + EPS:
        return (x, y)
    return None


def _sovrapposizione(s: tuple[Punto, Punto], t: tuple[Punto, Punto]) -> float:
    """Quanto due tratti sulla stessa retta corrono uno sull'altro."""
    (a, b), (c, d) = s, t
    if abs(a[1] - b[1]) < EPS and abs(c[1] - d[1]) < EPS and abs(a[1] - c[1]) < EPS:
        lo, hi = max(min(a[0], b[0]), min(c[0], d[0])), min(max(a[0], b[0]), max(c[0], d[0]))
        return max(0.0, hi - lo)
    if abs(a[0] - b[0]) < EPS and abs(c[0] - d[0]) < EPS and abs(a[0] - c[0]) < EPS:
        lo, hi = max(min(a[1], b[1]), min(c[1], d[1])), min(max(a[1], b[1]), max(c[1], d[1]))
        return max(0.0, hi - lo)
    return 0.0


def _accanto(punto: Punto, orizzontale: bool, altro: Sequence[Punto], passo: float) -> bool:
    """Un punto di un tracciato ha un compagno a `passo`, parallelo, di fianco."""
    x, y = punto
    for a, b in segmenti(altro):
        if (
            orizzontale and abs(a[1] - b[1]) < EPS and abs(abs(a[1] - y) - passo) < 1e-3
            and min(a[0], b[0]) - EPS <= x <= max(a[0], b[0]) + EPS
        ):
            return True
        if (
            not orizzontale and abs(a[0] - b[0]) < EPS and abs(abs(a[0] - x) - passo) < 1e-3
            and min(a[1], b[1]) - EPS <= y <= max(a[1], b[1]) + EPS
        ):
            return True
    return False


def parallelismo(membri: Sequence[Sequence[Punto]], passo: float, campione: float) -> float:
    """La parte dei tracciati di un fascio che ha un compagno accanto, al passo."""
    totale = accanto = 0
    for indice, punti in enumerate(membri):
        altri = [m for j, m in enumerate(membri) if j != indice]
        for a, b in segmenti(punti):
            orizzontale = abs(a[1] - b[1]) < EPS
            lunghezza = abs(b[0] - a[0]) + abs(b[1] - a[1])
            passi = max(1, round(lunghezza / campione))
            for k in range(passi):
                t = (k + 0.5) / passi
                p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                totale += 1
                if any(_accanto(p, orizzontale, altro, passo) for altro in altri):
                    accanto += 1
    return accanto / totale if totale else 1.0


def controlla(
    pianta: Pianta,
    percorsi: Sequence[Percorso],
    forature: Sequence[str],
    scritte: Sequence[tuple[str, ScrittaPosata]],
    linee_sulla_carta: Sequence[tuple[str, tuple[float, float, float, float, float]]],
    rettangoli_sulla_carta: Sequence[tuple[str, Rettangolo]],
    ammessi: dict[str, set[str]] | None = None,
) -> Rilievi:
    """`scritte` sono (di chi, scritta posata); `linee_sulla_carta` i segmenti
    disegnati, col mezzo spessore e di chi sono; `rettangoli_sulla_carta` muri e
    pezzi. Le scritte si misurano sulla carta, i tracciati in metri."""
    rilievi = Rilievi()
    for percorso in percorsi:
        if percorso.ceduto:
            rilievi.tratte_cedute.append(f"{percorso.tratta}: nessun percorso ortogonale libero")
        for a, b in (t for linea in percorso.linee for t in segmenti(linea)):
            if diagonale(a, b):
                rilievi.diagonali.append(f"{percorso.tratta}: da {a} a {b}")
        if percorso.fuori_dal_controsoffitto_m > 0:
            rilievi.fuori_dal_controsoffitto_m[percorso.tratta] = percorso.fuori_dal_controsoffitto_m
        if percorso.fuori_dalle_zone_m > 0:
            rilievi.fuori_dalle_zone_esterne.append(
                f"{percorso.tratta} per {percorso.fuori_dalle_zone_m:.2f} m".replace(".", ",")
            )
    rilievi.pezzi_sovrapposti = pezzi_sovrapposti(pianta)
    for chi, (x0, y0, x1, y1, _) in linee_sulla_carta:
        if diagonale((x0, y0), (x1, y1)) and chi.startswith("richiamo"):
            rilievi.diagonali.append(f"{chi}: richiamo obliquo")

    instradati = [p for p in percorsi if not p.ceduto]
    for i, p in enumerate(instradati):
        for q in instradati[i + 1:]:
            for s in (x for linea in p.linee for x in segmenti(linea)):
                for t in (y for linea in q.linee for y in segmenti(linea)):
                    lungo = _sovrapposizione(s, t)
                    if lungo > EPS:
                        rilievi.sovrapposizioni.append(f"{p.tratta} e {q.tratta}: {lungo:.2f} m")
                    punto = _incrocio(s, t)
                    if punto is not None:
                        rilievi.sormonti.append(
                            f"{p.tratta} × {q.tratta} a ({punto[0]:.2f}; {punto[1]:.2f})"
                        )

    passo = pianta.parametri.passo_fascio_m
    fasci: dict[str, list[Percorso]] = {}
    per_tratta = {p.tratta: p for p in percorsi}
    for tracciato in pianta.tracciati:
        if tracciato.fascio and not per_tratta[tracciato.tratta].ceduto:
            fasci.setdefault(tracciato.fascio, []).append(per_tratta[tracciato.tratta])
    for nome, membri in fasci.items():
        if len(membri) > 1:
            rilievi.fasci[nome] = parallelismo(
                [m.punti for m in membri], passo, pianta.parametri.passo_m
            )

    rilievi.fori_fuori_dalle_aperture.extend(forature)
    _i_richiami(rilievi, pianta, scritte, linee_sulla_carta, rettangoli_sulla_carta, ammessi or {})
    _le_linee_sui_pezzi(rilievi, pianta, linee_sulla_carta, rettangoli_sulla_carta)

    for indice, (chi, scritta) in enumerate(scritte):
        r = scritta.riquadro
        toccate = [
            di for di, s in linee_sulla_carta
            if di != f"richiamo:{chi}" and _segmento_tocca(s, r)
        ]
        suoi = (ammessi or {}).get(chi, set())
        toccate += [di for di, q in rettangoli_sulla_carta if di != chi and di not in suoi and _sovrapposti(q, r)]
        if toccate:
            rilievi.scritte_su_linee.append(
                f"«{scritta.testo}» ({chi}) tocca: {', '.join(sorted(set(toccate)))}"
            )
        for altro_chi, altra in scritte[indice + 1:]:
            if _sovrapposti(altra.riquadro, r):
                rilievi.scritte_su_scritte.append(f"«{scritta.testo}» ({chi}) e «{altra.testo}» ({altro_chi})")
    return rilievi


def pezzi_sovrapposti(pianta: Pianta) -> list[str]:
    """Le coppie di pezzi che si sovrappongono in pianta senza dichiararlo."""
    dichiarati = pianta.sovrapposti()
    out: list[str] = []
    for i, p in enumerate(pianta.pezzi):
        for q in pianta.pezzi[i + 1:]:
            a, b = p.rettangolo, q.rettangolo
            si_toccano = min(a[2], b[2]) - max(a[0], b[0]) > EPS and min(a[3], b[3]) - max(a[1], b[1]) > EPS
            if si_toccano and q.sigla not in dichiarati.get(p.sigla, set()):
                out.append(f"{p.sigla} e {q.sigla}")
    return out


def _proprie(chi: str) -> set[str]:
    """Le linee di chi ha la scritta: «tratta T03», «fascio T06 T07 T11»."""
    tipo, _, resto = chi.partition(" ")
    if tipo == "tratta":
        return {f"tratta {resto}"}
    if tipo == "fascio":
        return {f"tratta {t}" for t in resto.split()}
    return set()


def _i_richiami(
    rilievi: Rilievi, pianta: Pianta, scritte: Sequence[tuple[str, ScrittaPosata]],
    linee: Sequence[tuple[str, tuple[float, float, float, float, float]]],
    rettangoli: Sequence[tuple[str, Rettangolo]], ammessi: dict[str, set[str]],
) -> None:
    del pianta
    riquadri_delle_scritte = [(chi, s.riquadro) for chi, s in scritte]
    for chi, posata in scritte:
        if posata.numero is not None:
            rilievi.scritte_in_legenda.append(f"{posata.numero}: «{posata.in_legenda}» ({chi})")
        if posata.richiamo is None:
            continue
        x0, y0, x1, y1 = posata.richiamo
        segmento = (x0, y0, x1, y1, 0.09)
        lungo = abs(x1 - x0) + abs(y1 - y0)
        rilievi.richiamo_piu_lungo_mm = max(rilievi.richiamo_piu_lungo_mm, lungo)
        nome = f"«{posata.testo}» ({chi})"
        rilievi.richiami.append(f"{nome}: {lungo:.1f} mm")
        if lungo > RICHIAMO_MASSIMO_MM + 1e-6:
            rilievi.richiami_lunghi.append(f"{nome}: {lungo:.1f} mm")
        riquadro = _riquadro_del_segmento(segmento)
        ostacoli = sorted({
            di for di, r in rettangoli
            if di != chi and di not in ammessi.get(chi, set()) and _sovrapposti(riquadro, r)
            and not (di.startswith("muro ") and esce_di_traverso(segmento, r))
        })
        ostacoli += sorted({
            f"scritta {di}" for di, r in riquadri_delle_scritte if di != chi and _sovrapposti(riquadro, r)
        })
        proprie = _proprie(chi)
        attraversate = sorted({
            di for di, s in linee
            if di != f"richiamo:{chi}" and di not in proprie and _segmento_tocca(s, riquadro)
        })
        if ostacoli or len(attraversate) > LINEE_PER_RICHIAMO:
            rilievi.richiami_che_attraversano.append(f"{nome} attraversa: {', '.join(ostacoli + attraversate)}")
        elif attraversate:
            rilievi.richiami_su_una_linea.append(f"{nome} attraversa: {attraversate[0]}")


def _le_linee_sui_pezzi(
    rilievi: Rilievi, pianta: Pianta,
    linee: Sequence[tuple[str, tuple[float, float, float, float, float]]],
    rettangoli: Sequence[tuple[str, Rettangolo]],
) -> None:
    """Un tratto di tracciato che entra nel rettangolo di un pezzo che non e' un
    suo capo ne' un suo organo in linea."""
    sovrapposti = pianta.sovrapposti()
    capi: dict[str, set[str]] = {}
    for t in pianta.tracciati:
        suoi = {t.estremo_da.pezzo, t.estremo_a.pezzo, *t.passa_per}
        capi[t.tratta] = suoi | {c for s in suoi for c in sovrapposti.get(s, set())}
    pezzi = [(di[len("pezzo "):], r) for di, r in rettangoli if di.startswith("pezzo ")]
    visti: set[str] = set()
    for di, (x0, y0, x1, y1, _) in linee:
        if not di.startswith("tratta "):
            continue
        tratta = di[len("tratta "):]
        for sigla, r in pezzi:
            if sigla in capi.get(tratta, set()):
                continue
            dentro = (
                min(x0, x1) < r[2] - EPS and max(x0, x1) > r[0] + EPS
                and min(y0, y1) < r[3] - EPS and max(y0, y1) > r[1] + EPS
            ) if (x0 != x1 and y0 != y1) else (
                (r[0] + EPS < x0 < r[2] - EPS and min(y0, y1) < r[3] - EPS and max(y0, y1) > r[1] + EPS)
                if x0 == x1 else
                (r[1] + EPS < y0 < r[3] - EPS and min(x0, x1) < r[2] - EPS and max(x0, x1) > r[0] + EPS)
            )
            voce = f"{tratta} sopra {sigla}"
            if dentro and voce not in visti:
                visti.add(voce)
                rilievi.linee_sui_pezzi.append(voce)
