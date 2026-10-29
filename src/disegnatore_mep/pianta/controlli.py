"""I controlli misurati della pianta, sulla geometria che la tavola disegna.

Come i rilievi del motore dello schema: un numero e l'elenco di chi lo fa.
Bloccano la consegna le diagonali, le sovrapposizioni, le scritte su una linea
e le tratte non instradate; sormonti e forature sono fatti da guardare — un
sormonto si paga ma si puo' fare, una foratura e' lavoro dell'installatore —, e
la tavola li dice.

Si misurano anche se l'instradatore e' costruito per non produrli: e' il
controllo che lo dimostra sulla tavola finita, non il codice che lo promette.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from .instrada import Percorso
from .modello import Pianta
from .scritte import Rettangolo, ScrittaPosata, _segmento_tocca, _sovrapposti

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

    @property
    def bloccanti(self) -> list[str]:
        out: list[str] = []
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
            "bloccanti": self.bloccanti,
            "elenco": {
                "diagonali": self.diagonali,
                "sormonti": self.sormonti,
                "sovrapposizioni": self.sovrapposizioni,
                "scritte_su_linee": self.scritte_su_linee,
                "scritte_su_scritte": self.scritte_su_scritte,
                "fori_fuori_dalle_aperture": self.fori_fuori_dalle_aperture,
                "tratte_cedute": self.tratte_cedute,
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
) -> Rilievi:
    """`scritte` sono (di chi, scritta posata); `linee_sulla_carta` i segmenti
    disegnati, col mezzo spessore e di chi sono; `rettangoli_sulla_carta` muri e
    pezzi. Le scritte si misurano sulla carta, i tracciati in metri."""
    rilievi = Rilievi()
    for percorso in percorsi:
        if percorso.ceduto:
            rilievi.tratte_cedute.append(f"{percorso.tratta}: nessun percorso ortogonale libero")
        for a, b in segmenti(percorso.punti):
            if diagonale(a, b):
                rilievi.diagonali.append(f"{percorso.tratta}: da {a} a {b}")
        if percorso.fuori_dal_controsoffitto_m > 0:
            rilievi.fuori_dal_controsoffitto_m[percorso.tratta] = percorso.fuori_dal_controsoffitto_m
    for chi, (x0, y0, x1, y1, _) in linee_sulla_carta:
        if diagonale((x0, y0), (x1, y1)) and chi.startswith("richiamo"):
            rilievi.diagonali.append(f"{chi}: richiamo obliquo")

    instradati = [p for p in percorsi if not p.ceduto]
    for i, p in enumerate(instradati):
        for q in instradati[i + 1:]:
            for s in segmenti(p.punti):
                for t in segmenti(q.punti):
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

    for indice, (chi, scritta) in enumerate(scritte):
        r = scritta.riquadro
        toccate = [
            di for di, s in linee_sulla_carta
            if di != f"richiamo:{chi}" and _segmento_tocca(s, r)
        ]
        toccate += [di for di, q in rettangoli_sulla_carta if _sovrapposti(q, r)]
        if toccate:
            rilievi.scritte_su_linee.append(
                f"«{scritta.testo}» ({chi}) tocca: {', '.join(sorted(set(toccate)))}"
            )
        for altro_chi, altra in scritte[indice + 1:]:
            if _sovrapposti(altra.riquadro, r):
                rilievi.scritte_su_scritte.append(f"«{scritta.testo}» ({chi}) e «{altra.testo}» ({altro_chi})")
    return rilievi
