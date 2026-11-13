"""Il controllo a vista della base (REL-026, C-3): `mep.py base`.

Con la planimetria, la pagina con la griglia in pixel; con la pianta, la base trascritta sopra la
planimetria d'origine, alla stessa scala, e i controlli della taratura. Il caso e' quello anonimo
(`examples/pianta/casi/base-anonima`): una planimetria inventata, disegnata come la disegna un
architetto, e la sua base."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.graphics.pdf import leggi_il_png, misura_dell_immagine
from disegnatore_mep.pianta import sovrapposizione
from disegnatore_mep.pianta.modello import Pianta, carica_pianta
from disegnatore_mep.pianta.sovrapposizione import (
    ErroreDellaBase,
    Foglio,
    base_sopra,
    controlla_a_vista,
    controlli_della_taratura,
    guarda_la_planimetria,
    immagine_dell_origine,
)
from disegnatore_mep.pianta.tavola import Area
from disegnatore_mep.skill import cartelle_del_repository
from disegnatore_mep.skill import main as skill

from .conftest import CASI, RADICE

ANONIMA = CASI["base-anonima"]
ORIGINE = ANONIMA.parent / "base-anonima" / "planimetria.pdf"


def test_la_planimetria_inventata_si_rifa_uguale(tmp_path: Path) -> None:
    """Lo script disegna sempre la stessa planimetria: il PDF del repository e' il suo."""
    script = ANONIMA.parent / "base-anonima" / "disegna_la_planimetria.py"
    copia = tmp_path / "base-anonima"
    copia.mkdir()
    (copia / script.name).write_text(
        script.read_text(encoding="utf-8").replace(
            'sys.path.insert(0, str(QUI.parents[3] / "src"))', f"sys.path.insert(0, {str(RADICE / 'src')!r})"
        ),
        encoding="utf-8",
    )
    subprocess.run([sys.executable, str(copia / script.name)], check=True, capture_output=True)
    assert (copia / "planimetria.pdf").read_bytes() == ORIGINE.read_bytes()


def test_la_pagina_con_la_griglia_in_pixel(tmp_path: Path) -> None:
    esito = guarda_la_planimetria(ORIGINE, tmp_path, dpi=100)
    immagine, pdf, png = esito.file
    w, h = misura_dell_immagine(immagine.read_bytes())
    assert abs(w - 1654) <= 1 and abs(h - 1169) <= 1  # un A3 orizzontale a 100 dpi
    assert pdf.suffix == ".pdf" and png.exists()
    w2, h2 = misura_dell_immagine(png.read_bytes())
    assert abs(w2 - w) <= 1 and abs(h2 - h) <= 1  # la griglia ha i pixel della pagina
    assert any("1:50 78.74 px" in riga for riga in esito.righe)
    # La zona ingrandita: in pixel della pagina, e resa piu' fitta.
    zoom = guarda_la_planimetria(ORIGINE, tmp_path, dpi=100, zona_px=(200, 250, 600, 550))
    larghezza, altezza = misura_dell_immagine(zoom.file[-1].read_bytes())
    assert larghezza > 1000 and abs(larghezza / altezza - 400 / 300) < 0.02


def test_la_sovrapposizione_mette_la_base_dove_la_taratura_dice(tmp_path: Path) -> None:
    pianta = carica_pianta(ANONIMA)
    assert pianta.sfondo is not None
    immagine = immagine_dell_origine(ANONIMA.parent / pianta.sfondo.file, tmp_path)
    foglio = Foglio(immagine)
    base_sopra(foglio, pianta)
    (muri, *_) = [p for p in foglio.primitive if isinstance(p, Area)]
    k = immagine.mm_per_px
    # lo spigolo esterno in alto a sinistra dell'edificio: (0, 1,5) m nella pianta
    px, py = pianta.sfondo.in_pixel(0.0, 1.5)
    assert (round(px * k, 2), round(py * k, 2)) in [(round(x, 2), round(y, 2)) for x, y in muri.punti]
    # e sulla carta della planimetria inventata e' il punto (60, 70) mm
    assert px * k == pytest.approx(60.0, abs=0.01) and py * k == pytest.approx(70.0, abs=0.01)


def test_il_controllo_a_vista_del_caso_anonimo(tmp_path: Path) -> None:
    esito = controlla_a_vista(ANONIMA, tmp_path)
    nomi = {p.name for p in esito.file}
    assert {"base-anonima-sovrapposizione.pdf", "base-anonima-sovrapposizione.png"} <= nomi
    testo = "\n".join(esito.righe)
    assert "Base: 8 muri, 0 sagome, 10 aperture, 5 stanze, 1 balconi" in testo
    assert "luce mediana 0.80 m" in testo and "DA GUARDARE" not in testo
    assert "totale netto 68.0 m²" in testo


def test_i_controlli_vedono_la_scala_sbagliata() -> None:
    """Con la taratura alla meta' tutto raddoppia: le porte di 1,6 m lo dicono."""
    dati = json.loads(ANONIMA.read_text(encoding="utf-8"))

    def doppio(v: Any) -> Any:
        return [doppio(x) for x in v] if isinstance(v, list) else v * 2

    for muro in dati["muri"]:
        muro.update(da=doppio(muro["da"]), a=doppio(muro["a"]), spessore=muro["spessore"] * 2)
    for apertura in dati["aperture"]:
        apertura.update(centro=doppio(apertura["centro"]), larghezza=apertura["larghezza"] * 2)
    for stanza in dati["stanze"]:
        stanza["poligono"] = doppio(stanza["poligono"])
    dati.update(pezzi=[], tracciati=[], zone_esterne=[], balconi=[])
    righe = controlli_della_taratura(Pianta.model_validate(dati))
    assert any("la taratura e' sbagliata" in r for r in righe)
    assert any("porte fuori da" in r for r in righe)


def test_senza_sfondo_la_sovrapposizione_lo_dice(tmp_path: Path) -> None:
    with pytest.raises(ErroreDellaBase, match="sfondo"):
        controlla_a_vista(CASI["sagome"], tmp_path)


def test_senza_un_lettore_di_pdf_il_comando_lo_dice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vera = importlib.import_module

    def senza(nome: str, *args: Any, **kwargs: Any) -> Any:
        if nome in ("fitz", "pypdfium2"):
            raise ImportError(nome)
        return vera(nome, *args, **kwargs)

    monkeypatch.setattr(sovrapposizione.importlib, "import_module", senza)
    monkeypatch.setattr(sovrapposizione.shutil, "which", lambda _nome: None)
    with pytest.raises(ErroreDellaBase, match="pypdfium2"):
        immagine_dell_origine(ORIGINE, tmp_path)


def test_un_png_con_la_trasparenza_si_rifa_pieno(tmp_path: Path) -> None:
    """Un PNG RGBA (una schermata) si rifa' pieno su fondo bianco, coi filtri del PNG letti."""
    larghezza, altezza = 6, 4
    righe = b""
    for y in range(altezza):
        riga = bytes(v for x in range(larghezza) for v in (200, 10 * x, 50, 255 if x < 3 else 0))
        if y % 2:  # filtro Sub sulle righe dispari
            filtrata = bytes((riga[i] - (riga[i - 4] if i >= 4 else 0)) & 0xFF for i in range(len(riga)))
            righe += b"\x01" + filtrata
        else:
            righe += b"\x00" + riga

    def blocco(tipo: bytes, dati: bytes) -> bytes:
        return len(dati).to_bytes(4, "big") + tipo + dati + zlib.crc32(tipo + dati).to_bytes(4, "big")

    png = (b"\x89PNG\r\n\x1a\n" + blocco(b"IHDR", larghezza.to_bytes(4, "big") + altezza.to_bytes(4, "big")
                                         + bytes([8, 6, 0, 0, 0]))
           + blocco(b"IDAT", zlib.compress(righe)) + blocco(b"IEND", b""))
    (tmp_path / "foto.png").write_bytes(png)
    immagine = immagine_dell_origine(tmp_path / "foto.png", tmp_path / "out")
    pieno = leggi_il_png(immagine.file.read_bytes())
    assert (pieno.colore, pieno.larghezza, pieno.altezza) == (2, 6, 4)
    grezzo = zlib.decompress(pieno.compressi)
    riga1 = grezzo[1 + 18 + 1 : 1 + 18 + 1 + 18]  # la seconda riga, quella col filtro Sub
    assert riga1[:3] == bytes((200, 0, 50)) and riga1[-3:] == bytes((255, 255, 255))


def test_il_comando_della_skill(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cartelle = cartelle_del_repository(RADICE)
    assert skill(["base", str(ANONIMA), "--out", str(tmp_path / "a"), "--zona", "3,5,8,9"], cartelle) == 0
    uscita = capsys.readouterr().out
    assert "Sovrapposizione:" in uscita and "Zona guardata, in metri: 3.00, 5.00, 8.00, 9.00" in uscita
    assert skill(["base", str(ORIGINE), "--out", str(tmp_path / "b"), "--dpi", "72"], cartelle) == 0
    assert "Griglia in pixel:" in capsys.readouterr().out
    assert skill(["base", str(tmp_path / "manca.pdf"), "--out", str(tmp_path / "c")], cartelle) == 1
