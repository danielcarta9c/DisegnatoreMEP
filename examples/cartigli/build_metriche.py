"""Genera le larghezze dei caratteri con cui il cartiglio misura i propri testi.

Il cartiglio Nove C (`assets/cartigli/Cartiglio_NoveC_A3.pdf`) e' scritto in
**Helvetica**, e i valori che il PO ha ritoccato nel suo editor sono in **Arial**,
alle stesse misure. Arial e' costruito con le larghezze di Helvetica, e
**Liberation Sans** con quelle di Arial: e' il carattere che l'ambiente di sviluppo
ha davvero, e da quello si leggono le larghezze. Servono a una cosa sola: sapere
se un committente o un titolo **entra nella sua casella** prima di scriverlo.

La prova `tests/graphics/test_cartiglio.py` le confronta con le larghezze dei due
caratteri Arial incorporati nel file del PO, su ogni carattere che il file usa:
e' il controllo che la catena Helvetica — Arial — Liberation tiene davvero.

Legge i due file TrueType con la sola libreria standard — le tabelle `head`,
`hhea`, `hmtx`, `cmap` e `name` — e scrive `src/disegnatore_mep/graphics/metriche.py`.
**Non fa parte delle prove dei generatori**: i caratteri stanno nel sistema, non
nel repository, e una prova che dipende da cosa e' installato non e' una prova.

Uso: python examples/cartigli/build_metriche.py [cartella-dei-caratteri]
"""

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "src" / "disegnatore_mep" / "graphics" / "metriche.py"
FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
FILES = {"NORMALE": "LiberationSans-Regular.ttf", "GRASSETTO": "LiberationSans-Bold.ttf"}


def characters() -> list[str]:
    """I caratteri stampabili di WinAnsi, la codifica del cartiglio."""
    found: list[str] = []
    for code in range(0x20, 0x100):
        try:
            text = bytes([code]).decode("cp1252")
        except UnicodeDecodeError:
            continue
        if code != 0x7F:
            found.append(text)
    return found


def tables(data: bytes) -> dict[str, bytes]:
    count = struct.unpack(">H", data[4:6])[0]
    found: dict[str, bytes] = {}
    for index in range(count):
        tag, _, offset, length = struct.unpack(">4sIII", data[12 + 16 * index : 28 + 16 * index])
        found[tag.decode("latin-1")] = data[offset : offset + length]
    return found


def cmap_format_4(cmap: bytes) -> dict[int, int]:
    """Da punto di codice a glifo, dalla sottotabella Windows Unicode BMP."""
    count = struct.unpack(">H", cmap[2:4])[0]
    for index in range(count):
        platform, encoding, offset = struct.unpack(">HHI", cmap[4 + 8 * index : 12 + 8 * index])
        if (platform, encoding) != (3, 1):
            continue
        table = cmap[offset:]
        if struct.unpack(">H", table[0:2])[0] != 4:
            continue
        segments = struct.unpack(">H", table[6:8])[0] // 2
        ends = struct.unpack(f">{segments}H", table[14 : 14 + 2 * segments])
        base = 16 + 2 * segments
        starts = struct.unpack(f">{segments}H", table[base : base + 2 * segments])
        deltas = struct.unpack(f">{segments}h", table[base + 2 * segments : base + 4 * segments])
        ranges_at = base + 4 * segments
        ranges = struct.unpack(f">{segments}H", table[ranges_at : ranges_at + 2 * segments])
        glyphs: dict[int, int] = {}
        for segment in range(segments):
            for code in range(starts[segment], ends[segment] + 1):
                if code == 0xFFFF:
                    continue
                if ranges[segment] == 0:
                    glyph = (code + deltas[segment]) & 0xFFFF
                else:
                    at = ranges_at + 2 * segment + ranges[segment] + 2 * (code - starts[segment])
                    glyph = struct.unpack(">H", table[at : at + 2])[0]
                    if glyph:
                        glyph = (glyph + deltas[segment]) & 0xFFFF
                if glyph:
                    glyphs[code] = glyph
        return glyphs
    raise SystemExit("nessuna sottotabella cmap Windows Unicode di formato 4")


def version(name: bytes) -> str:
    count, strings = struct.unpack(">HH", name[2:6])
    for index in range(count):
        platform, _, _, name_id, length, offset = struct.unpack(
            ">6H", name[6 + 12 * index : 18 + 12 * index]
        )
        if platform == 3 and name_id == 5:
            return name[strings + offset : strings + offset + length].decode("utf-16-be")
    return "?"


def widths(path: Path) -> tuple[dict[str, int], str]:
    data = path.read_bytes()
    found = tables(data)
    units = struct.unpack(">H", found["head"][18:20])[0]
    metrics = struct.unpack(">H", found["hhea"][34:36])[0]
    advances = struct.unpack(f">{metrics * 2}H", found["hmtx"][: metrics * 4])[0::2]
    glyphs = cmap_format_4(found["cmap"])
    table: dict[str, int] = {}
    for text in characters():
        glyph = glyphs.get(ord(text))
        if glyph is None:
            raise SystemExit(f"{path.name} non ha il carattere {text!r}")
        advance = advances[min(glyph, metrics - 1)]
        table[text] = round(advance * 1000 / units)
    digest = hashlib.sha256(data).hexdigest()
    return table, f"{path.name} {version(found['name'])}, sha256 {digest}"


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else FONT_DIR
    lines = [
        '"""Le larghezze dei caratteri del cartiglio, in millesimi di em.',
        "",
        "**Generato** da `examples/cartigli/build_metriche.py`: non si modifica a mano.",
        "Il perche' di queste larghezze, e il controllo che le tiene oneste, sta in",
        "testa al generatore.",
        '"""',
        "",
    ]
    sources: list[str] = []
    for constant, name in FILES.items():
        table, source = widths(folder / name)
        sources.append(source)
        lines.append(f"{constant}: dict[str, int] = {{")
        lines.extend(f"    {text!r}: {width}," for text, width in table.items())
        lines.append("}")
        lines.append("")
    lines.insert(7, "FONTI: tuple[str, ...] = (")
    for offset, source in enumerate(sources, start=8):
        lines.insert(offset, f"    {source!r},")
    lines.insert(8 + len(sources), ")")
    lines.insert(9 + len(sources), "")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUTPUT.relative_to(ROOT)}: {len(characters())} caratteri, da {', '.join(sources)}")


if __name__ == "__main__":
    main()
