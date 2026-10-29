"""Il comando della pianta: dal JSON alla tavola, ai tracciati e ai rilievi.

    mep.py pianta <pianta.json> --out <cartella>

Scrive nella cartella, col nome del JSON:

- `<nome>.svg`, `<nome>.pdf`, `<nome>.dxf` (con il logo accanto) e
  `<nome>.png`, l'anteprima;
- `<nome>.tracciati.json`: i percorsi in metri, le lunghezze misurate e da
  quotare per tratta, le forature, i rilievi — quello che serve alla distinta
  materiali (`REL-013`).

Codici di uscita come il resto della skill: `0` fatto, `2` fatto ma c'e' un
rilievo che ferma la consegna, `1` non si e' potuto fare.
"""

from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

from disegnatore_mep.graphics.cartiglio import Cartiglio

from .controlli import Rilievi, controlla
from .griglia import Griglia, costruisci_la_griglia
from .instrada import Percorso, instrada_tutto
from .lunghezze import Lunghezza, lunghezze, metri
from .modello import Pianta, carica_pianta
from .tavola import Foratura, Tavola, componi, scrivi_dxf, scrivi_svg

VICINE_M = 0.5
"""Due forature dello stesso fascio sullo stesso muro, piu' vicine di cosi',
sono un foro solo."""


@dataclass
class Esito:
    pianta: Pianta
    percorsi: list[Percorso]
    lunghezze: list[Lunghezza]
    forature: list[Foratura]
    fori_dei_pezzi: list[tuple[str, str]]
    tavola: Tavola
    rilievi: Rilievi
    file: list[Path]


def forature(pianta: Pianta, percorsi: list[Percorso]) -> list[Foratura]:
    """I muri passati fuori da un'apertura che lascia passare quella quota.
    Le tratte di uno stesso fascio che forano lo stesso muro vicino fanno un
    foro solo."""
    fasci = {t.tratta: t.fascio for t in pianta.tracciati}
    tipi = {m.id: m.tipo for m in pianta.muri}
    gruppi: list[dict[str, object]] = []
    for percorso in percorsi:
        for passaggio in percorso.attraversamenti:
            if not passaggio.forato:
                continue
            fascio = fasci.get(passaggio.tratta)
            for gruppo in gruppi:
                if (
                    fascio is not None
                    and gruppo["fascio"] == fascio
                    and gruppo["muro"] == passaggio.muro
                    and math.dist(gruppo["punto"], passaggio.punto) <= VICINE_M  # type: ignore[arg-type]
                ):
                    gruppo["tratte"].append(passaggio.tratta)  # type: ignore[attr-defined]
                    gruppo["punti"].append(passaggio.punto)  # type: ignore[attr-defined]
                    break
            else:
                gruppi.append({
                    "fascio": fascio, "muro": passaggio.muro, "punto": passaggio.punto,
                    "tratte": [passaggio.tratta], "punti": [passaggio.punto], "quota": passaggio.quota,
                })
    out: list[Foratura] = []
    for numero, gruppo in enumerate(gruppi, start=1):
        punti: list[tuple[float, float]] = gruppo["punti"]  # type: ignore[assignment]
        centro = (
            round(sum(p[0] for p in punti) / len(punti), 4),
            round(sum(p[1] for p in punti) / len(punti), 4),
        )
        out.append(
            Foratura(
                numero=f"F{numero}", muro=str(gruppo["muro"]), tipo_del_muro=tipi[str(gruppo["muro"])],
                tratte=tuple(gruppo["tratte"]),  # type: ignore[arg-type]
                quota=str(gruppo["quota"]), punto=centro,
            )
        )
    return out


def fori_dei_pezzi(pianta: Pianta, griglia: Griglia) -> list[tuple[str, str]]:
    """I pezzi dichiarati a cavallo di un muro — una bocchetta, una griglia: il
    foro e' il pezzo stesso, e va detto."""
    del griglia
    out: list[tuple[str, str]] = []
    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        for muro in pianta.muri:
            h = muro.spessore / 2
            (ax, ay), (bx, by) = muro.da, muro.a
            if abs(ay - by) < 1e-9:
                attraversa = y0 < ay - h + 1e-6 and y1 > ay + h - 1e-6
                dentro = min(ax, bx) - h < (x0 + x1) / 2 < max(ax, bx) + h
            elif abs(ax - bx) < 1e-9:
                attraversa = x0 < ax - h + 1e-6 and x1 > ax + h - 1e-6
                dentro = min(ay, by) - h < (y0 + y1) / 2 < max(ay, by) + h
            else:
                continue
            if attraversa and dentro:
                out.append((pezzo.sigla, muro.id))
    return out


def _pixel_del_jpeg(percorso: Path) -> tuple[int, int]:
    from disegnatore_mep.graphics.pdf import _jpeg

    larghezza, altezza, _ = _jpeg(percorso.read_bytes())
    return larghezza, altezza


def disegna_la_pianta(
    sorgente: Path, cartella: Path, cartiglio: Cartiglio | None,
    dxf: bool = True, png: bool = True,
) -> Esito:
    pianta = carica_pianta(sorgente)
    griglia = costruisci_la_griglia(pianta)
    percorsi = instrada_tutto(pianta, griglia)
    lunghe = lunghezze(list(pianta.tracciati), percorsi, pianta.maggiorazione)
    fori = forature(pianta, percorsi)
    dei_pezzi = fori_dei_pezzi(pianta, griglia)
    pixel = None
    cartella.mkdir(parents=True, exist_ok=True)
    scritti: list[Path] = []
    if pianta.sfondo is not None:
        immagine = sorgente.parent / pianta.sfondo.file
        if immagine.suffix.lower() not in (".jpg", ".jpeg"):
            raise ValueError(f"lo sfondo {immagine.name} non e' un JPEG: il PDF del motore incorpora solo JPEG")
        pixel = _pixel_del_jpeg(immagine)
        copia = cartella / immagine.name
        if copia.resolve() != immagine.resolve():
            shutil.copyfile(immagine, copia)
        scritti.append(copia)
    tavola = componi(pianta, percorsi, lunghe, fori, dei_pezzi, cartiglio, pixel)
    rilievi = controlla(
        pianta, percorsi,
        [f"{f.numero}: {' '.join(f.tratte)} nel muro {f.muro}" for f in fori],
        tavola.scritte, tavola.linee, tavola.rettangoli,
    )
    nome = sorgente.stem
    svg = cartella / f"{nome}.svg"
    svg.write_text(scrivi_svg(tavola), encoding="utf-8")
    scritti.append(svg)

    from disegnatore_mep.graphics.pdf import scrivi_pdf

    scrivi_pdf(svg, titolo=f"{pianta.cartiglio.get('numero_tavola', '')} {pianta.titolo}".strip())
    scritti.append(svg.with_suffix(".pdf"))
    if dxf:
        scritti += scrivi_dxf(tavola, svg.with_suffix(".dxf"), pianta.titolo)
    if png:
        from disegnatore_mep.skill import anteprima

        immagine_png = svg.with_suffix(".png")
        if anteprima(svg.with_suffix(".pdf"), immagine_png, 110) is not None:
            scritti.append(immagine_png)
    dati = cartella / f"{nome}.tracciati.json"
    dati.write_text(
        json.dumps(_dati(pianta, percorsi, lunghe, fori, dei_pezzi, tavola, rilievi),
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    scritti.append(dati)
    return Esito(pianta, percorsi, lunghe, fori, dei_pezzi, tavola, rilievi, scritti)


def _dati(
    pianta: Pianta, percorsi: list[Percorso], lunghe: list[Lunghezza], fori: list[Foratura],
    dei_pezzi: list[tuple[str, str]], tavola: Tavola, rilievi: Rilievi,
) -> dict[str, object]:
    per_tratta = {lu.tratta: lu for lu in lunghe}
    return {
        "tavola": {"formato": tavola.formato, "scala": f"1:{tavola.scala}", "avvisi": tavola.avvisi},
        "maggiorazione": pianta.maggiorazione.model_dump(),
        "tratte": [
            {
                "tratta": t.tratta,
                "fluido": t.fluido,
                "da": t.estremo_da.pezzo,
                "a": t.estremo_a.pezzo,
                "dimensione": t.dimensione,
                "quota": t.quota,
                "fascio": t.fascio,
                "instradata": not p.ceduto,
                "lunghezza_misurata_m": per_tratta[t.tratta].misurata_m,
                "lunghezza_da_quotare_m": per_tratta[t.tratta].da_quotare_m,
                "deciso_dal_minimo": per_tratta[t.tratta].minimo_m is not None,
                "curve": max(0, len(p.punti) - 2),
                "fuori_dal_controsoffitto_m": p.fuori_dal_controsoffitto_m,
                "punti_m": [list(q) for q in p.punti],
                "attraversamenti": [
                    {"muro": a.muro, "apertura": a.apertura, "forato": a.forato, "punto_m": list(a.punto)}
                    for a in p.attraversamenti
                ],
            }
            for t, p in zip(pianta.tracciati, percorsi, strict=True)
        ],
        "forature": [
            {"numero": f.numero, "muro": f.muro, "tipo_del_muro": f.tipo_del_muro,
             "tratte": list(f.tratte), "quota": f.quota, "punto_m": list(f.punto)}
            for f in fori
        ],
        "fori_dei_pezzi": [{"pezzo": s, "muro": m} for s, m in dei_pezzi],
        "rilievi": rilievi.come_dati(),
    }


def riassunto(esito: Esito) -> list[str]:
    r = esito.rilievi
    righe = [
        f"Tavola: {esito.tavola.formato} a 1:{esito.tavola.scala}",
        f"Tratte: {len(esito.percorsi)} ({len(r.tratte_cedute)} non instradate)",
        f"Diagonali: {len(r.diagonali)}",
        f"Sormonti: {len(r.sormonti)}",
        f"Sovrapposizioni: {len(r.sovrapposizioni)}",
        f"Scritte che toccano una linea: {len(r.scritte_su_linee)}; sopra altre scritte: "
        f"{len(r.scritte_su_scritte)}",
        f"Forature fuori dalle aperture: {len(r.fori_fuori_dalle_aperture)}"
        + (f" (e {len(esito.fori_dei_pezzi)} fori per i pezzi a parete)" if esito.fori_dei_pezzi else ""),
    ]
    for fascio, quota in sorted(r.fasci.items()):
        righe.append(f"Fascio «{fascio}»: {round(quota * 100)}% del percorso accanto a un compagno")
    for tratta, fuori in sorted(r.fuori_dal_controsoffitto_m.items()):
        righe.append(f"{tratta}: {metri(fuori, 2)} m in controsoffitto dove il controsoffitto non c'e'")
    righe += [f"Avviso: {a}" for a in esito.tavola.avvisi]
    for elenco in (r.diagonali, r.sovrapposizioni, r.scritte_su_linee, r.scritte_su_scritte, r.tratte_cedute):
        righe += [f"  - {voce}" for voce in elenco]
    righe += [f"BLOCCANTE: {b}" for b in r.bloccanti]
    return righe


def esegui(sorgente: Path, cartella: Path, cartiglio: Path | None, dxf: bool = True) -> int:
    """Il sottocomando `pianta`, uguale nella CLI del repository e in quella della
    skill: scrive, dice che cosa ha scritto e che cosa ha misurato."""
    modello = Cartiglio.da_file(cartiglio) if cartiglio is not None and cartiglio.exists() else None
    if dxf:
        try:
            import ezdxf  # noqa: F401
        except ImportError:
            print("Manca ezdxf: la pianta esce in PDF, SVG e PNG, senza DXF.")
            dxf = False
    esito = disegna_la_pianta(sorgente, cartella, modello, dxf=dxf)
    for percorso in esito.file:
        print(f"Scritto: {percorso}")
    if modello is None:
        print("Senza cartiglio: la tavola ha la sola squadratura.")
    for riga in riassunto(esito):
        print(riga)
    return 2 if esito.rilievi.bloccanti else 0
