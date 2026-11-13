"""Il comando della pianta: dal JSON alla tavola, ai tracciati e ai rilievi.

    mep.py pianta <pianta.json> --out <cartella> [--distinta distinta.json] [--grafo grafo-completo.json]

Scrive nella cartella, col nome del JSON:

- `<nome>.svg`, `<nome>.pdf`, `<nome>.dxf` (con il logo accanto) e
  `<nome>.png`, l'anteprima;
- `<nome>.tracciati.json`: i percorsi in metri e, per tratta, la lunghezza del
  progettista, quella misurata, quella usata e quella da quotare (col conto),
  i rilievi. Dove il progettista non ha dato la lunghezza, la misura e' li', e
  con `--grafo` il comando la scrive nel grafo dello schema (`nel_grafo.py`,
  REL-026 B-4): la distinta quota lo stesso numero della pianta.

**Le forature sono spente di base** (REL-026, B-3). Con `"forature": true` nella
pianta la tavola le numera e le elenca, e i dati portano per tratta gli
`attraversamenti_di_parete`: le pareti interne che la tratta fora (fuori da
un'apertura che lascia passare la sua quota) piu' il foro del pezzo a parete a un
suo capo (la bocchetta nella tramezza); a parte i fori nel muro perimetrale. Con
`--grafo` vanno sulla tubazione del grafo (`attraversamenti`), e la distinta conta
le forature della pianta invece di assumerle.

Con `--distinta` e `--grafo` la pianta si confronta con le uscite degli altri
comandi (`confronto.py`): sigle, numeri di tratta, capi e lunghezze.

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

from .confronto import Confronto, con_le_lunghezze, confronta
from .controlli import Rilievi, controlla
from .griglia import Griglia, costruisci_la_griglia
from .instrada import Percorso, chiave_della_tratta, instrada_tutto
from .lunghezze import Lunghezza, Regola, la_regola, lunghezze, metri
from .modello import Dettaglio, Foglio, Pianta, Tracciato, carica_pianta
from .nel_grafo import Aggiornamento, aggiorna
from .nel_grafo import Tratta as TrattaNelGrafo
from .scritte import RICHIAMO_MASSIMO_MM
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
    regola: Regola | None = None
    avvisi: list[str] | None = None
    """Gli avvisi della colonna: misure oltre lo scarto, controsoffitto che
    manca, la regola delle lunghezze se non e' quella della distinta."""
    dettagli: list[Tavola] | None = None
    """Le tavole dei riquadri di dettaglio, se ci sono."""
    confronto: Confronto | None = None
    """Il confronto con la distinta e il grafo, se il comando li ha avuti."""
    nel_grafo: Aggiornamento | None = None
    """Le lunghezze che la pianta scrive nel grafo (o scriverebbe), se ha avuto il grafo."""


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


def attraversamenti_per_tratta(
    pianta: Pianta, percorsi: list[Percorso], dei_pezzi: list[tuple[str, str]],
) -> tuple[dict[str, int], dict[str, int]]:
    """Le pareti **interne** che ogni tratta passa con un foro: i muri forati
    dal suo percorso, e il foro del pezzo a parete (una bocchetta nella
    tramezza) che e' un suo capo — quello va alla prima tratta che ci arriva.
    E' il dato `attraversamenti` della tubazione, quello che la distinta conta
    («pareti interne»: il foro nel muro esterno dell'unita' esterna sta gia'
    nella sua posa). A parte, i fori nel muro perimetrale."""
    perimetrali = {m.id for m in pianta.muri if m.tipo == "perimetrale"}
    interni = {t.tratta: 0 for t in pianta.tracciati}
    esterni = {t.tratta: 0 for t in pianta.tracciati}
    for tracciato, percorso in zip(pianta.tracciati, percorsi, strict=True):
        for passaggio in percorso.attraversamenti:
            if passaggio.forato:
                (esterni if passaggio.muro in perimetrali else interni)[tracciato.tratta] += 1
    contati: set[tuple[str, str]] = set()
    for tracciato in pianta.tracciati:
        for sigla, muro in dei_pezzi:
            if (sigla, muro) in contati or sigla not in (tracciato.estremo_da.pezzo, tracciato.estremo_a.pezzo):
                continue
            contati.add((sigla, muro))
            (esterni if muro in perimetrali else interni)[tracciato.tratta] += 1
    return interni, esterni


def _pixel_dell_immagine(percorso: Path) -> tuple[int, int]:
    from disegnatore_mep.graphics.pdf import misura_dell_immagine

    larghezza, altezza = misura_dell_immagine(percorso.read_bytes())
    return larghezza, altezza


def avvisi_della_tavola(
    pianta: Pianta, percorsi: list[Percorso], lunghe: list[Lunghezza], regola: Regola,
    nel_grafo: Aggiornamento | None = None,
) -> list[str]:
    """Quello che la tavola deve dire, e non ferma la consegna. `nel_grafo` e' quello
    che la pianta scrive nel grafo (B-4): le misure che ci sono non vanno riportate."""
    avvisi: list[str] = []
    soglia = round(pianta.parametri.scarto_della_misura * 100)
    oltre = [
        f"{lu.tratta} {metri(lu.misurata_m)} m su {metri(lu.data_m)} (+{round(lu.scarto * 100)} %)"
        for lu in lunghe if lu.oltre_lo_scarto and lu.data_m is not None and lu.scarto is not None
    ]
    if oltre:
        avvisi.append(
            f"Misura oltre il {soglia} % di L prog.: {'; '.join(oltre)}. Da verificare il percorso o il dato."
        )
    senza = [lu.tratta for lu in lunghe if lu.dalla_misura]
    if senza:
        quali = "tutte le tratte" if len(senza) == len(lunghe) > 1 else ", ".join(senza)
        nel: set[str] = set()
        if nel_grafo is not None:
            nel = set(nel_grafo.allineate) | (set() if nel_grafo.sola_lettura else nel_grafo.nel_grafo)
        dentro = [t for t in senza if t in nel]
        fuori = [t for t in senza if t not in nel]
        coda = []
        if dentro:
            coda.append("Le misure sono nel grafo" + (f" per {', '.join(dentro)}" if fuori else "")
                        + ": schema e distinta, rifatti, le leggono da li'.")
        if fuori:
            coda.append("Da riportare nel grafo, o da chiedere" + (f": {', '.join(fuori)}." if dentro else "."))
        avvisi.append(f"Senza L prog., quotate sulla misura (°): {quali}. {' '.join(coda)}")
    fuori_dalle_zone = [
        f"{p.tratta} {metri(p.fuori_dalle_zone_m, 2)} m" for p in percorsi if p.fuori_dalle_zone_m > 0
    ]
    if fuori_dalle_zone:
        avvisi.append(
            f"Fuori dall'edificio, fuori dalle zone esterne dichiarate (fascia rossa): {'; '.join(fuori_dalle_zone)}. "
            "Ferma la consegna: va dichiarata la zona (terrazzo, balcone) o rivisto il percorso."
        )
    fasci = {t.tratta: t.fascio for t in pianta.tracciati}
    gruppi: dict[str, list[Percorso]] = {}
    for percorso in percorsi:
        if percorso.fuori_dal_controsoffitto_m > 0:
            gruppi.setdefault(fasci.get(percorso.tratta) or percorso.tratta, []).append(percorso)
    if gruppi:
        voci = [
            f"{'-'.join(p.tratta for p in membri)} {metri(max(p.fuori_dal_controsoffitto_m for p in membri), 2)} m"
            for membri in gruppi.values()
        ]
        avvisi.append(
            f"Fuori dal controsoffitto (fascia arancio): {'; '.join(voci)}. Canalina o traccia, da verificare."
        )
    if not regola.della_distinta:
        avvisi.append(f"La regola delle lunghezze e' {regola.origine}: le lunghezze da quotare possono "
                      "non coincidere con la distinta.")
    return avvisi


def disegna_la_pianta(
    sorgente: Path, cartella: Path, cartiglio: Cartiglio | None,
    dxf: bool = True, png: bool = True, regole: Path | None = None,
    distinta: Path | None = None, grafo: Path | None = None,
    catalogo: Path | None = None, nomi: Path | None = None,
    aggiorna_il_grafo: bool = False,
) -> Esito:
    """`regole` sono le regole della distinta (una cartella o il fascio della
    skill); se mancano si cercano accanto al motore. `distinta` e `grafo` sono
    i file con cui confrontare sigle, numeri di tratta e lunghezze;
    `catalogo` e `nomi` servono a leggere dal grafo le sigle dello schema.

    Con `grafo`, la pianta calcola sempre che cosa cambierebbe nel grafo (`nel_grafo.py`);
    lo scrive, dopo le tavole, solo con `aggiorna_il_grafo` — il comando lo fa di base, e
    `--grafo-in-sola-lettura` lo spegne."""
    pianta = carica_pianta(sorgente)
    dichiarate = {t.tratta: t.lunghezza_m for t in pianta.tracciati}
    confronto = confronta(pianta, distinta, grafo, catalogo, nomi)
    pianta = con_le_lunghezze(pianta, confronto)
    griglia = costruisci_la_griglia(pianta)
    percorsi = instrada_tutto(pianta, griglia)
    regola = la_regola(pianta.maggiorazione, regole)
    lunghe = lunghezze(list(pianta.tracciati), percorsi, regola, pianta.parametri.scarto_della_misura)
    fori = forature(pianta, percorsi)
    dei_pezzi = fori_dei_pezzi(pianta, griglia)
    nel_grafo = None if grafo is None else aggiorna(
        grafo, tratte_per_il_grafo(pianta, percorsi, lunghe, confronto, dichiarate, dei_pezzi),
        sola_lettura=not aggiorna_il_grafo,
    )
    avvisi = avvisi_della_tavola(pianta, percorsi, lunghe, regola, nel_grafo)
    if confronto.lunghezze:
        per_fonte: dict[str, list[str]] = {}
        for tratta, (_, fonte) in sorted(confronto.lunghezze.items(), key=lambda v: chiave_della_tratta(v[0])):
            per_fonte.setdefault(fonte, []).append(tratta)
        avvisi.append(
            "L prog. non scritta nella pianta, presa "
            + "; ".join(f"dal{'la' if fonte == 'distinta' else ''} {fonte} per {', '.join(tratte)}"
                        for fonte, tratte in per_fonte.items())
            + "."
        )
    # Le discordanze, riassunte: l'elenco intero sta nei dati e in console (REL-026, B-5).
    avvisi += confronto.per_la_tavola(f"{sorgente.stem}.tracciati.json")
    # Le forature sono spente di base (REL-026, B-3): si contano, ma la tavola, i
    # rilievi e i dati non le scrivono, se la pianta non le accende.
    fori_scritti = fori if pianta.forature else []
    dei_pezzi_scritti = dei_pezzi if pianta.forature else []
    pixel = None
    cartella.mkdir(parents=True, exist_ok=True)
    scritti: list[Path] = []
    # Lo sfondo va sulla tavola solo se il progettista lo chiede, o se non c'e' altra base
    # (REL-026, C-3): se no la planimetria d'origine serve al controllo a vista (`base`).
    if pianta.sfondo is not None and pianta.sfondo_sulla_tavola:
        immagine = sorgente.parent / pianta.sfondo.file
        if immagine.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            raise ValueError(
                f"lo sfondo {immagine.name} va sulla tavola, e non e' un JPEG o un PNG: il PDF del motore "
                "incorpora solo quelli (l'immagine della pagina la scrive mep.py base)"
            )
        if pianta.sfondo.rotazione:
            raise ValueError(
                f"lo sfondo {immagine.name} e' ruotato di {pianta.sfondo.rotazione:g} gradi: sulla tavola si stampa "
                "solo diritto. Serve al controllo a vista (mep.py base), non alla tavola"
            )
        pixel = _pixel_dell_immagine(immagine)
        copia = cartella / immagine.name
        if copia.resolve() != immagine.resolve():
            shutil.copyfile(immagine, copia)
        scritti.append(copia)
    nome = sorgente.stem
    tavola, dettagli, rimandate = _la_tavola_e_i_dettagli(
        pianta, percorsi, lunghe, fori_scritti, dei_pezzi_scritti, cartiglio, pixel, regola, avvisi, nome,
        confronto.nota,
    )
    rilievi = controlla(
        pianta, percorsi,
        [f"{f.numero}: {' '.join(f.tratte)} nel muro {f.muro}" for f in fori_scritti],
        tavola.scritte, tavola.linee, tavola.rettangoli, tavola.ammessi,
    )
    rilievi.misure_oltre_la_lunghezza = [
        f"{lu.tratta}: {metri(lu.misurata_m)} m misurati contro {metri(lu.data_m or 0)} m dati"
        for lu in lunghe if lu.oltre_lo_scarto
    ]
    rilievi.scritte_nel_dettaglio = sorted(f"{chi} (dettaglio {lettera})" for chi, lettera in rimandate.items())
    rilievi.confronto = list(confronto.avvisi)
    rilievi.confronto_bloccante = list(confronto.bloccanti)
    tavole_dei_dettagli: list[tuple[Dettaglio, Tavola]] = []
    for dettaglio in dettagli:
        tavola_del_dettaglio = componi(
            _pianta_del_dettaglio(pianta, dettaglio), percorsi, lunghe, fori_scritti, dei_pezzi_scritti, cartiglio,
            pixel,
            regola, avvisi, zona=dettaglio.rettangolo, ridotta=nome,
            nel_dettaglio=frozenset(c for c, i in rimandate.items() if i == dettaglio.id),
            controllo_delle_sigle=confronto.nota,
        )
        del_dettaglio = controlla(pianta, percorsi, [], tavola_del_dettaglio.scritte, tavola_del_dettaglio.linee,
                                  tavola_del_dettaglio.rettangoli, tavola_del_dettaglio.ammessi)
        rilievi.unisci_le_scritte(del_dettaglio, f"dettaglio {dettaglio.id}")
        tavole_dei_dettagli.append((dettaglio, tavola_del_dettaglio))

    scritti += _scrivi_la_tavola(tavola, cartella / f"{nome}.svg", pianta, dxf, png)
    for dettaglio, tavola_del_dettaglio in tavole_dei_dettagli:
        scritti += _scrivi_la_tavola(tavola_del_dettaglio, cartella / f"{nome}-dettaglio-{dettaglio.id}.svg",
                                     _pianta_del_dettaglio(pianta, dettaglio), dxf, png)
    # Le lunghezze nel grafo, dopo le tavole (B-4): se il disegno non esce, il grafo resta com'era.
    if nel_grafo is not None and grafo is not None:
        nel_grafo.scrivi(grafo)
    dati = cartella / f"{nome}.tracciati.json"
    contenuto = _dati(pianta, percorsi, lunghe, fori_scritti, dei_pezzi_scritti, tavola, rilievi, regola, avvisi,
                      confronto)
    contenuto["grafo"] = None if nel_grafo is None else nel_grafo.come_dati()
    contenuto["dettagli"] = [
        {"id": d.id, "rettangolo_m": list(d.rettangolo), "scala": f"1:{d.scala}",
         "tavola": f"{nome}-dettaglio-{d.id}"}
        for d, _ in tavole_dei_dettagli
    ]
    dati.write_text(json.dumps(contenuto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scritti.append(dati)
    return Esito(pianta, percorsi, lunghe, fori, dei_pezzi, tavola, rilievi, scritti, regola, avvisi,
                 [t for _, t in tavole_dei_dettagli], confronto, nel_grafo)


def tratte_per_il_grafo(
    pianta: Pianta, percorsi: list[Percorso], lunghe: list[Lunghezza], confronto: Confronto,
    dichiarate: dict[str, float | None], dei_pezzi: list[tuple[str, str]],
) -> list[TrattaNelGrafo]:
    """Quello che la pianta sa di ogni tratta, per scriverlo nel grafo: le tubazioni che il
    confronto le ha trovato, la misura della tratta, la lunghezza che la pianta dichiara
    (del progettista) e, a forature accese, le pareti interne forate."""
    per_tratta = {lu.tratta: lu for lu in lunghe}
    pareti = attraversamenti_per_tratta(pianta, percorsi, dei_pezzi)[0] if pianta.forature else {}
    coppie = sorted(zip(pianta.tracciati, percorsi, strict=True), key=lambda c: chiave_della_tratta(c[0].tratta))
    return [
        TrattaNelGrafo(
            tratta=t.tratta,
            tubazioni=tuple(confronto.tubazioni.get(t.tratta, ())),
            misurata_m=per_tratta[t.tratta].misurata_m,
            data_nella_pianta_m=dichiarate.get(t.tratta),
            instradata=not p.ceduto,
            attraversamenti=pareti.get(t.tratta) if pianta.forature else None,
        )
        for t, p in coppie
    ]


GIRI_DEI_DETTAGLI = 4


def _pianta_del_dettaglio(pianta: Pianta, dettaglio: Dettaglio) -> Pianta:
    numero = pianta.cartiglio.get("numero_tavola")
    cartiglio = {**pianta.cartiglio, **({"numero_tavola": f"{numero}.{dettaglio.id}"} if numero else {})}
    return pianta.model_copy(update={
        "titolo": f"{pianta.titolo} - dettaglio {dettaglio.id}",
        "foglio": Foglio(scala=dettaglio.scala),
        "cartiglio": cartiglio,
    })


def _la_tavola_e_i_dettagli(
    pianta: Pianta, percorsi: list[Percorso], lunghe: list[Lunghezza], fori: list[Foratura],
    dei_pezzi: list[tuple[str, str]], cartiglio: Cartiglio | None, pixel: tuple[int, int] | None,
    regola: Regola, avvisi: list[str], nome: str, controllo_delle_sigle: str = "",
) -> tuple[Tavola, list[Dettaglio], dict[str, str]]:
    """La tavola intera e i riquadri di dettaglio **che la pianta chiede**.

    Una scritta che a 1:50 non trova posto — ne' accanto, ne' con un richiamo
    corto, ne' come numero in legenda — va fuori dalla pianta, col suo richiamo
    (`fuori_pianta.py`). Se il suo oggetto cade in un riquadro di dettaglio che il
    progettista ha dichiarato in `dettagli`, si posa invece nel dettaglio, come
    prima. **I riquadri non nascono piu' da soli** (REL-026, C-1; LEGGIMI M2 di
    BD.RM.260: il dettaglio B della commessa era un A3 con due tubi e le parole
    mandata e ritorno): senza `dettagli`, o con `[]`, non ce n'e' nessuno."""
    dettagli = list(pianta.dettagli or [])
    rimandate: dict[str, str] = {}

    def nota() -> list[str]:
        if not dettagli:
            return []
        elenco = ", ".join(f"{d.id} 1:{d.scala}" for d in dettagli)
        return [f"Dettagli {elenco} (zone incorniciate): tavole {nome}-dettaglio-<lettera>."]

    def componi_la_tavola() -> Tavola:
        return componi(pianta, percorsi, lunghe, fori, dei_pezzi, cartiglio, pixel, regola, [*avvisi, *nota()],
                       rimandate=frozenset(rimandate),
                       riquadri=[(d.id, d.rettangolo, d.scala) for d in dettagli],
                       controllo_delle_sigle=controllo_delle_sigle)

    tavola = componi_la_tavola()
    for _ in range(GIRI_DEI_DETTAGLI if dettagli else 0):
        cambiato = False
        for chi, posata in tavola.scritte:
            if chi in rimandate or (posata.libera and posata.richiamo_fuori is None):
                continue
            # Dove sta l'oggetto: il punto d'attacco del richiamo fuori; per una scritta
            # rimasta senza posto, il posto provato, accanto all'oggetto.
            if posata.richiamo_fuori is not None:
                px, py = posata.richiamo_fuori[0]
                x0, y0, _, _ = tavola.in_metri((px, py, px, py))
                centro = (x0, y0)
            else:
                x0, y0, x1, y1 = tavola.in_metri(posata.riquadro)
                centro = ((x0 + x1) / 2, (y0 + y1) / 2)
            dentro = [
                d for d in dettagli
                if d.rettangolo[0] <= centro[0] <= d.rettangolo[2] and d.rettangolo[1] <= centro[1] <= d.rettangolo[3]
            ]
            if dentro:
                rimandate[chi] = dentro[0].id
                cambiato = True
        if not cambiato:
            break
        tavola = componi_la_tavola()
    return tavola, dettagli, rimandate


def _scrivi_la_tavola(tavola: Tavola, svg: Path, pianta: Pianta, dxf: bool, png: bool) -> list[Path]:
    from disegnatore_mep.graphics.pdf import scrivi_pdf

    scritti: list[Path] = []
    svg.write_text(scrivi_svg(tavola), encoding="utf-8")
    scritti.append(svg)
    scrivi_pdf(svg, titolo=f"{pianta.cartiglio.get('numero_tavola', '')} {pianta.titolo}".strip())
    scritti.append(svg.with_suffix(".pdf"))
    if dxf:
        scritti += scrivi_dxf(tavola, svg.with_suffix(".dxf"), pianta.titolo)
    if png:
        from disegnatore_mep.skill import anteprima

        immagine_png = svg.with_suffix(".png")
        if anteprima(svg.with_suffix(".pdf"), immagine_png, 110) is not None:
            scritti.append(immagine_png)
    return scritti


def _dati(
    pianta: Pianta, percorsi: list[Percorso], lunghe: list[Lunghezza], fori: list[Foratura],
    dei_pezzi: list[tuple[str, str]], tavola: Tavola, rilievi: Rilievi, regola: Regola, avvisi: list[str],
    confronto: Confronto | None = None,
) -> dict[str, object]:
    per_tratta = {lu.tratta: lu for lu in lunghe}
    pareti, perimetro = attraversamenti_per_tratta(pianta, percorsi, dei_pezzi)
    prese = confronto.lunghezze if confronto is not None else {}
    accese = pianta.forature

    def data_da(t: Tracciato) -> str | None:
        if t.tratta in prese:
            return prese[t.tratta][1]
        return "pianta" if t.lunghezza_m is not None else None

    def fori_della_tratta(t: Tracciato) -> dict[str, int]:
        """Le pareti forate dalla tratta, per la distinta: solo a forature accese."""
        if not accese:
            return {}
        return {"attraversamenti_di_parete": pareti[t.tratta], "fori_nel_perimetrale": perimetro[t.tratta]}

    per_il_grafo: dict[str, object] = {
        "per_il_grafo": {
            "nota": "Le pareti interne forate da ogni tratta: da riportare nel grafo, fra le properties di una "
                    "tubazione della tratta (attraversamenti), perche' la distinta conti le forature della pianta.",
            "attraversamenti": {t.tratta: pareti[t.tratta] for t in pianta.tracciati},
        },
    } if accese else {}

    return {
        "tavola": {"formato": tavola.formato, "scala": f"1:{tavola.scala}", "avvisi": tavola.avvisi},
        "forature_accese": accese,
        "avvisi": avvisi,
        "regola_delle_lunghezze": {
            "origine": regola.origine,
            "della_distinta": regola.della_distinta,
            "regola": {k: regola.regola[k] for k in ("aggiunta_m", "fattore", "passo_m")},
            "scarto_della_misura": pianta.parametri.scarto_della_misura,
        },
        "tratte": [
            {
                "tratta": t.tratta,
                "fluido": t.fluido,
                "da": t.estremo_da.pezzo,
                "a": t.estremo_a.pezzo,
                "passa_per": list(t.passa_per),
                "dimensione": t.dimensione,
                "quota": t.quota,
                "fascio": t.fascio,
                "instradata": not p.ceduto,
                "lunghezza_data_m": per_tratta[t.tratta].data_m,
                "lunghezza_data_da": data_da(t),
                "lunghezza_misurata_m": per_tratta[t.tratta].misurata_m,
                "lunghezza_usata_m": per_tratta[t.tratta].usata_m,
                "lunghezza_usata_da": "misura" if per_tratta[t.tratta].dalla_misura else "progettista",
                "scarto_della_misura": per_tratta[t.tratta].scarto,
                "misura_oltre_lo_scarto": per_tratta[t.tratta].oltre_lo_scarto,
                "lunghezza_da_quotare_m": per_tratta[t.tratta].da_quotare_m,
                "calcolo": per_tratta[t.tratta].calcolo,
                "deciso_dal_minimo": per_tratta[t.tratta].minimo_m is not None,
                "curve": sum(max(0, len(linea) - 2) for linea in p.linee),
                "fuori_dal_controsoffitto_m": p.fuori_dal_controsoffitto_m,
                "fuori_dalle_zone_esterne_m": p.fuori_dalle_zone_m,
                **fori_della_tratta(t),
                "punti_m": [list(q) for q in p.punti],
                "tronchi_m": [[list(q) for q in linea] for linea in p.linee] if p.tronchi else None,
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
        **per_il_grafo,
        "confronto": None if confronto is None else {
            "con": confronto.fonti, "bloccanti": confronto.bloccanti, "avvisi": confronto.avvisi,
            "avvisi_per_tipo": {tipo: len(elenco) for tipo, elenco in confronto.per_tipo.items()},
            "lunghezze_prese": {t: {"m": m, "da": da} for t, (m, da) in sorted(confronto.lunghezze.items())},
        },
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
        f"Richiami: {len(r.richiami)} (il piu' lungo {r.richiamo_piu_lungo_mm:.1f} mm, soglia "
        f"{RICHIAMO_MASSIMO_MM:g} mm); lunghi: {len(r.richiami_lunghi)}; che attraversano muri, pezzi, "
        f"scritte o piu' linee: {len(r.richiami_che_attraversano)}; su una linea: {len(r.richiami_su_una_linea)}",
        f"Scritte in legenda (numerate): {len(r.scritte_in_legenda)}",
        f"Scritte fuori dalla pianta, col richiamo: {len(r.scritte_fuori_pianta)}"
        + (f" (il richiamo piu' lungo {r.richiamo_fuori_piu_lungo_mm:.1f} mm); richiami che si incrociano: "
           f"{len(r.richiami_che_si_incrociano)}; sopra scritte o pezzi: {len(r.richiami_fuori_sopra)}"
           if r.scritte_fuori_pianta else ""),
        f"Linee sopra un pezzo non loro: {len(r.linee_sui_pezzi)}",
        f"Tratte fuori dall'edificio, fuori dalle zone esterne dichiarate: {len(r.fuori_dalle_zone_esterne)}",
        f"Pezzi sovrapposti senza dichiararlo: {len(r.pezzi_sovrapposti)}",
        f"Riquadri di dettaglio: {len(esito.dettagli or [])}"
        + (f" (scritte rimandate al dettaglio: {', '.join(r.scritte_nel_dettaglio)})" if r.scritte_nel_dettaglio else ""),
        f"Regola delle lunghezze: {esito.regola.origine if esito.regola else '?'}",
        f"Forature fuori dalle aperture: {len(r.fori_fuori_dalle_aperture)}"
        + (f" (e {len(esito.fori_dei_pezzi)} fori per i pezzi a parete)" if esito.fori_dei_pezzi else "")
        if esito.pianta.forature else
        "Forature: spente, come di base (le accende \"forature\": true nella pianta)",
    ]
    for fascio, quota in sorted(r.fasci.items()):
        righe.append(f"Fascio «{fascio}»: {round(quota * 100)}% del percorso accanto a un compagno")
    if esito.confronto is not None and esito.confronto.fonti:
        righe.append(
            f"Confronto con {' e '.join(esito.confronto.fonti)}: {len(r.confronto_bloccante)} bloccanti, "
            f"{len(r.confronto)} avvisi"
        )
        # Per esteso qui e nei dati: sulla tavola sono riassunte (REL-026, B-5). I
        # bloccanti escono in fondo, con gli altri.
        righe += [f"  - {voce}" for voce in r.confronto]
    if esito.nel_grafo is not None:
        righe += esito.nel_grafo.righe()
    righe += [f"Avviso: {a}" for a in [*esito.tavola.avvisi, *(esito.avvisi or [])]]
    for elenco in (r.diagonali, r.sovrapposizioni, r.scritte_su_linee, r.scritte_su_scritte, r.tratte_cedute,
                   r.richiami_lunghi, r.richiami_che_attraversano, r.richiami_su_una_linea,
                   r.scritte_in_legenda, r.scritte_fuori_pianta, r.richiami_che_si_incrociano,
                   r.richiami_fuori_sopra, r.linee_sui_pezzi):
        righe += [f"  - {voce}" for voce in elenco]
    righe += [f"BLOCCANTE: {b}" for b in r.bloccanti]
    return righe


def esegui(sorgente: Path, cartella: Path, cartiglio: Path | None, dxf: bool = True,
           regole: Path | None = None, distinta: Path | None = None, grafo: Path | None = None,
           catalogo: Path | None = None, nomi: Path | None = None, grafo_in_sola_lettura: bool = False) -> int:
    """Il sottocomando `pianta`, uguale nella CLI del repository e in quella della
    skill: scrive, dice che cosa ha scritto e che cosa ha misurato. Con `grafo` scrive
    nel grafo le lunghezze misurate (REL-026, B-4), salvo `grafo_in_sola_lettura`."""
    modello = Cartiglio.da_file(cartiglio) if cartiglio is not None and cartiglio.exists() else None
    if dxf:
        try:
            import ezdxf  # noqa: F401
        except ImportError:
            print("Manca ezdxf: la pianta esce in PDF, SVG e PNG, senza DXF.")
            dxf = False
    esito = disegna_la_pianta(sorgente, cartella, modello, dxf=dxf, regole=regole, distinta=distinta, grafo=grafo,
                              catalogo=catalogo, nomi=nomi, aggiorna_il_grafo=not grafo_in_sola_lettura)
    for percorso in esito.file:
        print(f"Scritto: {percorso}")
    if modello is None:
        print("Senza cartiglio: la tavola ha la sola squadratura.")
    for riga in riassunto(esito):
        print(riga)
    return 2 if esito.rilievi.bloccanti else 0
