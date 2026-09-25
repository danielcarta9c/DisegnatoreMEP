"""Genera il modello del cartiglio Nove C dal file che il PO ha dato.

La fonte e' `assets/cartigli/Cartiglio_NoveC_A3.pdf`, la versione del 25 settembre
2026 (I-127): «questo e' il cartiglio che usiamo per i fogli A3». Lo script lo
legge **con la sola libreria standard** — tabella dei riferimenti, oggetti,
flussi, il disegno della pagina interpretato operatore per operatore — e
scrive accanto:

- `Cartiglio_NoveC_A3.json`: il modello, cioe' ogni tratto, campitura, testo
  e segnaposto **nell'ordine in cui il file li dipinge**, in millimetri con
  l'origine in alto a sinistra;
- `Cartiglio_NoveC_A3-logo.jpg`: il logo, **byte per byte** il JPEG che il
  file contiene.

Quello che il file non dice, e lo script aggiunge, sta tutto qui sotto in
chiaro: **quale segnaposto e' quale dato** (`CAMPI`), come si allinea ogni
testo, e il posto dei tre nomi sulle righe delle firme, che il file lascia
vuote. Tutto il resto e' misurato.

Un file che cambia forma fa fallire lo script con un messaggio, non con un
modello sbagliato: un testo nuovo va dichiarato, un segnaposto sparito va
cercato. Rieseguirlo deve dare file bit per bit identici, e
`tests/catalog/test_generated_fixtures.py` lo pretende.
"""

import base64
import hashlib
import json
import math
import re
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from disegnatore_mep.graphics.cartiglio import (
    Campitura,
    Campo,
    Fonte,
    Ingombro,
    Logo,
    ModelloDelCartiglio,
    Testo,
    Tratto,
    Zona,
    larghezza_mm,
)

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "assets" / "cartigli"
SOURCE = FOLDER / "Cartiglio_NoveC_A3.pdf"
MODEL = FOLDER / "Cartiglio_NoveC_A3.json"
LOGO = FOLDER / "Cartiglio_NoveC_A3-logo.jpg"
INPUT = "I-127"

PT = 25.4 / 72
DECIMALS = 3

# --- Quello che il file non dice, e la sessione dichiara --------------------

CAMPI: dict[str, tuple[str, str]] = {
    # segnaposto nel file: (campo, allineamento)
    "NOVE C INGEGNERIA  |  Documento confidenziale  |  MI.223 – Elaborati Grafici": (
        "intestazione",
        "sinistra",
    ),
    "Conto Termico con sconto in fattura": ("dicitura", "destra"),
    "Nome committente": ("committente", "sinistra"),
    "Indirizzo comune e provincia": ("indirizzo", "sinistra"),
    "nome del progetto": ("progetto", "sinistra"),
    "Nome della tavbola": ("titolo_tavola", "sinistra"),
    "—": ("scala", "sinistra"),
    "gg.mm.aaaa": ("data", "sinistra"),
    "Rev. 01": ("revisione", "sinistra"),
    "codice": ("commessa", "sinistra"),
    "T3": ("numero_tavola", "centro"),
}
"""Quale segnaposto e' quale dato. Il file del 25 settembre ha i valori in
segnaposto, tranne la testata, dove restano la commessa e la dicitura di una
commessa vera: si leggono come la commessa e la dicitura da compilare (I-127)."""

COMMESSA_IN_TESTATA = "MI.223"
"""La commessa scritta nella testata del file, che nel modello diventa `{commessa}`."""

ETICHETTE: dict[str, str] = {
    "COMMITTENTE": "sinistra",
    "INDIRIZZO": "sinistra",
    "PROGETTO": "sinistra",
    "TITOLO TAVOLA": "sinistra",
    "SCALA": "sinistra",
    "DATA": "sinistra",
    "REVISIONE": "sinistra",
    "COMMESSA": "sinistra",
    "APPROVATO": "sinistra",
    "VERIFICATO": "sinistra",
    "DISEGNATO": "sinistra",
    "TAVOLA": "centro",
}
"""I testi fissi della fascia, con il loro allineamento: «TAVOLA» e il numero
sono centrati nella casella blu, e lo script lo verifica sul file."""

A_CAPO = {"committente", "indirizzo", "progetto", "titolo_tavola"}
"""I campi che possono andare su due righe: le quattro caselle larghe."""

CORPO_MINIMO_PT = 7.0
"""Il corpo sotto il quale un valore non scende: il piu' piccolo che il file
stesso usa per un valore — l'indirizzo e la revisione."""

FIRME = {"APPROVATO": "approvato", "VERIFICATO": "verificato", "DISEGNATO": "disegnato"}
FIRMA_CORPO_PT = 6.0
FIRMA_SOPRA_LA_RIGA_MM = 0.7
"""*Scelta della sessione, non del file*: il nome di chi firma si scrive sulla
riga della firma, 0,7 mm sopra, a 6 punti, nel colore dei valori."""

# --- 1. Il file, letto con la libreria standard ------------------------------


@dataclass(frozen=True)
class Name:
    value: str


@dataclass(frozen=True)
class Ref:
    number: int


@dataclass(frozen=True)
class Keyword:
    value: str


WHITE = b" \t\r\n\x0c\x00"
DELIMITERS = b"()<>[]{}/%"
NUMBER = re.compile(rb"[+-]?(\d+\.?\d*|\.\d+)")


class Lexer:
    def __init__(self, data: bytes, pos: int = 0) -> None:
        self.data = data
        self.pos = pos

    def skip(self) -> None:
        data = self.data
        while self.pos < len(data):
            if data[self.pos] in WHITE:
                self.pos += 1
            elif data[self.pos : self.pos + 1] == b"%":
                while self.pos < len(data) and data[self.pos] not in b"\r\n":
                    self.pos += 1
            else:
                break

    def token(self) -> Any:
        self.skip()
        data = self.data
        if self.pos >= len(data):
            return None
        char = data[self.pos : self.pos + 1]
        if data.startswith(b"<<", self.pos) or data.startswith(b">>", self.pos):
            self.pos += 2
            return data[self.pos - 2 : self.pos].decode()
        if char in (b"[", b"]", b"{", b"}"):
            self.pos += 1
            return char.decode()
        if char == b"/":
            end = self.pos + 1
            while end < len(data) and data[end] not in WHITE and data[end] not in DELIMITERS:
                end += 1
            raw = data[self.pos + 1 : end]
            self.pos = end
            return Name(re.sub(rb"#([0-9A-Fa-f]{2})", lambda m: bytes([int(m[1], 16)]), raw).decode("latin-1"))
        if char == b"(":
            return self.literal()
        if char == b"<":
            end = data.index(b">", self.pos)
            digits = re.sub(rb"\s", b"", data[self.pos + 1 : end])
            self.pos = end + 1
            if len(digits) % 2:
                digits += b"0"
            return bytes.fromhex(digits.decode())
        match = NUMBER.match(data, self.pos)
        if match and (match.end() == len(data) or data[match.end()] in WHITE + DELIMITERS):
            self.pos = match.end()
            text = match.group().decode()
            return float(text) if "." in text else int(text)
        start = end = self.pos
        while end < len(data) and data[end] not in WHITE and data[end] not in DELIMITERS:
            end += 1
        if end == start:
            raise SystemExit(f"carattere inatteso {char!r} alla posizione {start}")
        self.pos = end
        return Keyword(data[start:end].decode("latin-1"))

    def literal(self) -> bytes:
        data, pos, depth = self.data, self.pos + 1, 1
        out = bytearray()
        escapes = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}
        while True:
            byte = data[pos]
            if byte == ord("\\"):
                pos += 1
                nxt = data[pos]
                if nxt in escapes:
                    out.append(escapes[nxt])
                    pos += 1
                elif nxt in b"()\\":
                    out.append(nxt)
                    pos += 1
                elif 48 <= nxt <= 55:
                    digits = re.match(rb"[0-7]{1,3}", data[pos : pos + 3])
                    assert digits is not None
                    out.append(int(digits.group(), 8) & 0xFF)
                    pos += len(digits.group())
                elif nxt in b"\r\n":
                    pos += 2 if data[pos : pos + 2] == b"\r\n" else 1
                else:
                    # Un escape sconosciuto vale il carattere, senza barra
                    # (PDF 1.7, 7.3.4.2): nel file c'e' «Elaborati \Grafici».
                    out.append(nxt)
                    pos += 1
                continue
            if byte == ord("("):
                depth += 1
            elif byte == ord(")"):
                depth -= 1
                if depth == 0:
                    self.pos = pos + 1
                    return bytes(out)
            out.append(byte)
            pos += 1


def parse(lexer: Lexer, first: Any = None) -> Any:
    token = lexer.token() if first is None else first
    if token == "<<":
        found: dict[str, Any] = {}
        while True:
            key = lexer.token()
            if key == ">>":
                return found
            if not isinstance(key, Name):
                raise SystemExit(f"chiave di dizionario inattesa: {key!r}")
            found[key.value] = parse(lexer)
    if token == "[":
        items: list[Any] = []
        while True:
            item = lexer.token()
            if item == "]":
                return items
            items.append(parse(lexer, item))
    if isinstance(token, int):
        saved = lexer.pos
        second, third = lexer.token(), lexer.token()
        if isinstance(second, int) and third == Keyword("R"):
            return Ref(token)
        lexer.pos = saved
    return token


class Pdf:
    """Il file: la catena delle tabelle dei riferimenti, e gli oggetti per numero.

    Il file del PO e' un salvataggio **incrementale** — ReportLab, poi un editor
    — e la definizione piu' recente di un oggetto vince sulle precedenti."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offsets: dict[int, int] = {}
        found = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
        if found is None:
            raise SystemExit("startxref non trovato")
        offset: int | None = int(found.group(1))
        trailer: dict[str, Any] | None = None
        while offset is not None:
            if not data.startswith(b"xref", offset):
                raise SystemExit(
                    "il file usa una tabella dei riferimenti a flusso: questo lettore "
                    "legge solo quelle classiche. Va salvato di nuovo senza compressione "
                    "degli oggetti, o il lettore va esteso"
                )
            lexer = Lexer(data, offset + 4)
            while True:
                head = lexer.token()
                if head == Keyword("trailer"):
                    break
                start, count = head, lexer.token()
                for number in range(start, start + count):
                    where, _, kind = lexer.token(), lexer.token(), lexer.token()
                    if kind == Keyword("n"):
                        self.offsets.setdefault(number, where)
            current = parse(lexer)
            trailer = trailer or current
            offset = current.get("Prev")
        assert trailer is not None
        self.trailer = trailer

    def resolve(self, value: Any) -> Any:
        while isinstance(value, Ref):
            value = self.object(value.number)[0]
        return value

    def object(self, number: int) -> tuple[Any, bytes | None]:
        lexer = Lexer(self.data, self.offsets[number])
        if lexer.token() != number:
            raise SystemExit(f"l'oggetto {number} non sta dove la tabella dice")
        lexer.token()
        if lexer.token() != Keyword("obj"):
            raise SystemExit(f"l'oggetto {number} non comincia con «obj»")
        value = parse(lexer)
        lexer.skip()
        if not self.data.startswith(b"stream", lexer.pos):
            return value, None
        start = lexer.pos + len(b"stream")
        if self.data.startswith(b"\r\n", start):
            start += 2
        elif self.data[start : start + 1] in (b"\n", b"\r"):
            start += 1
        length = self.resolve(value["Length"])
        return value, self.data[start : start + length]

    def stream(self, number: int, stop_at: str | None = None) -> bytes:
        """Il flusso decodificato; con `stop_at` si ferma prima di quel filtro."""
        value, raw = self.object(number)
        if raw is None:
            raise SystemExit(f"l'oggetto {number} non ha un flusso")
        filters = value.get("Filter", [])
        for item in filters if isinstance(filters, list) else [filters]:
            if item.value == stop_at:
                break
            if item.value == "ASCII85Decode":
                raw = raw.strip()
                raw = base64.a85decode(raw[:-2] if raw.endswith(b"~>") else raw, ignorechars=WHITE)
            elif item.value == "FlateDecode":
                raw = zlib.decompress(raw)
            else:
                raise SystemExit(f"filtro {item.value} non gestito nell'oggetto {number}")
        return raw


# --- 2. Il disegno della pagina, operatore per operatore ----------------------

Matrix = tuple[float, float, float, float, float, float]
IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def times(m: Matrix, n: Matrix) -> Matrix:
    """m poi n, nella convenzione PDF (vettori riga)."""
    a, b, c, d, e, f = m
    p, q, r, s, t, u = n
    return (a * p + b * r, a * q + b * s, c * p + d * r, c * q + d * s, e * p + f * r + t, e * q + f * s + u)


def apply(m: Matrix, x: float, y: float) -> tuple[float, float]:
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


@dataclass
class State:
    ctm: Matrix = IDENTITY
    stroke: tuple[float, float, float] = (0.0, 0.0, 0.0)
    fill: tuple[float, float, float] = (0.0, 0.0, 0.0)
    width: float = 1.0
    fill_alpha: float = 1.0


@dataclass
class Font:
    name: str
    bold: bool
    decode: Any
    cap_height: float | None
    widths: dict[str, int]


def colour(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(channel * 255):02x}" for channel in rgb)


def fonts(pdf: Pdf, resources: dict[str, Any]) -> dict[str, Font]:
    found: dict[str, Font] = {}
    for key, ref in pdf.resolve(resources.get("Font", {})).items():
        font = pdf.resolve(ref)
        base = font["BaseFont"].value.split("+")[-1]
        bold = "Bold" in base
        if font["Subtype"].value == "Type1":
            if font.get("Encoding") != Name("WinAnsiEncoding"):
                raise SystemExit(f"{base}: codifica non WinAnsi")
            found[key] = Font(base, bold, lambda raw: raw.decode("cp1252"), None, {})
            continue
        if font["Subtype"].value != "Type0" or font.get("Encoding") != Name("Identity-H"):
            raise SystemExit(f"{base}: carattere non gestito")
        cmap = pdf.stream(font["ToUnicode"].number).decode("latin-1")
        table: dict[int, str] = {}
        for block in re.findall(r"beginbfchar(.*?)endbfchar", cmap, re.S):
            for code, text in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
                table[int(code, 16)] = bytes.fromhex(text).decode("utf-16-be")
        for block in re.findall(r"beginbfrange(.*?)endbfrange", cmap, re.S):
            for low, high, text in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
                first = int(text, 16)
                for code in range(int(low, 16), int(high, 16) + 1):
                    table[code] = chr(first + code - int(low, 16))
        child = pdf.resolve(pdf.resolve(font["DescendantFonts"])[0])
        descriptor = pdf.resolve(child["FontDescriptor"])
        widths: dict[str, int] = {}
        items = pdf.resolve(child.get("W", []))
        index = 0
        while index < len(items):
            start = items[index]
            if isinstance(items[index + 1], list):
                for offset, width in enumerate(items[index + 1]):
                    if start + offset in table:
                        widths[table[start + offset]] = round(width)
                index += 2
            else:
                for code in range(start, items[index + 1] + 1):
                    if code in table:
                        widths[table[code]] = round(items[index + 2])
                index += 3

        def decode(raw: bytes, table: dict[int, str] = table) -> str:
            return "".join(table[int.from_bytes(raw[i : i + 2], "big")] for i in range(0, len(raw), 2))

        found[key] = Font(base, bold, decode, descriptor["CapHeight"] / 1000, widths)
    return found


@dataclass
class Painted:
    kind: str
    data: dict[str, Any]


def interpret(pdf: Pdf, page: dict[str, Any]) -> tuple[list[Painted], dict[str, Font], float]:
    resources = pdf.resolve(page["Resources"])
    font_table = fonts(pdf, resources)
    states = pdf.resolve(resources.get("ExtGState", {}))
    images = pdf.resolve(resources.get("XObject", {}))
    height = float(pdf.resolve(page["MediaBox"])[3])
    contents = pdf.resolve(page["Contents"])
    numbers = [item.number for item in (contents if isinstance(contents, list) else [page["Contents"]])]
    stream = b"\n".join(pdf.stream(number) for number in numbers)

    def mm(x: float, y: float) -> tuple[float, float]:
        return (round(x * PT, DECIMALS), round((height - y) * PT, DECIMALS))

    painted: list[Painted] = []
    state, stack = State(), []
    path: list[tuple[str, list[tuple[float, float]]]] = []
    text_line: Matrix = IDENTITY
    font: Font | None = None
    size = 0.0
    shown_since_move = False
    operands: list[Any] = []
    lexer = Lexer(stream)
    while True:
        token = lexer.token()
        if token is None:
            break
        if not isinstance(token, Keyword):
            operands.append(parse(lexer, token) if token in ("[", "<<") else token)
            continue
        op, args, operands = token.value, operands, []
        if op == "q":
            stack.append(State(state.ctm, state.stroke, state.fill, state.width, state.fill_alpha))
        elif op == "Q":
            state = stack.pop()
        elif op == "cm":
            state.ctm = times(tuple(float(v) for v in args), state.ctm)  # type: ignore[arg-type]
        elif op == "w":
            state.width = float(args[0])
        elif op == "RG":
            state.stroke = (float(args[0]), float(args[1]), float(args[2]))
        elif op == "rg":
            state.fill = (float(args[0]), float(args[1]), float(args[2]))
        elif op == "gs":
            state.fill_alpha = float(pdf.resolve(states[args[0].value]).get("ca", 1.0))
        elif op == "m":
            path.append(("line", [apply(state.ctm, float(args[0]), float(args[1]))]))
        elif op == "l":
            path[-1][1].append(apply(state.ctm, float(args[0]), float(args[1])))
        elif op == "re":
            x, y, w, h = (float(v) for v in args)
            path.append(("rect", [apply(state.ctm, x, y), apply(state.ctm, x + w, y + h)]))
        elif op in ("S", "f", "f*", "F", "n"):
            scale = math.sqrt(abs(state.ctm[0] * state.ctm[3] - state.ctm[1] * state.ctm[2]))
            for kind, points in path:
                if op == "n":
                    continue
                corners = [mm(*point) for point in points]
                if op == "S":
                    if kind == "line" and len(corners) != 2:
                        raise SystemExit("una spezzata di piu' tratti: il lettore non la gestisce")
                    painted.append(
                        Painted(
                            "stroke",
                            {
                                "forma": "rettangolo" if kind == "rect" else "linea",
                                "points": corners,
                                "colore": colour(state.stroke),
                                "spessore_mm": round(state.width * scale * PT, DECIMALS),
                            },
                        )
                    )
                else:
                    if kind != "rect":
                        raise SystemExit("una campitura che non e' un rettangolo")
                    painted.append(
                        Painted(
                            "fill",
                            {"points": corners, "colore": colour(state.fill), "opacita": state.fill_alpha},
                        )
                    )
            path = []
        elif op == "Do":
            box = [mm(*apply(state.ctm, x, y)) for x, y in ((0, 1), (1, 0))]
            painted.append(Painted("image", {"points": box, "ref": images[args[0].value]}))
        elif op == "BT":
            text_line = IDENTITY
            shown_since_move = False
        elif op == "Tf":
            font, size = font_table[args[0].value], float(args[1])
        elif op in ("Td", "TD"):
            text_line = times((1, 0, 0, 1, float(args[0]), float(args[1])), text_line)
            shown_since_move = False
        elif op == "Tm":
            text_line = tuple(float(v) for v in args)  # type: ignore[assignment]
            shown_since_move = False
        elif op in ("Tj", "TJ"):
            if shown_since_move:
                raise SystemExit("due testi di fila senza spostamento: il lettore non misura l'avanzamento")
            assert font is not None
            raw = args[0] if op == "Tj" else b"".join(item for item in args[0] if isinstance(item, bytes))
            full = times(text_line, state.ctm)
            if abs(full[1]) > 1e-9 or abs(full[2]) > 1e-9:
                raise SystemExit("un testo ruotato: il lettore non lo gestisce")
            painted.append(
                Painted(
                    "text",
                    {
                        "testo": font.decode(raw),
                        "at": mm(full[4], full[5]),
                        "corpo_pt": round(size * full[3], DECIMALS),
                        "font": font,
                        "colore": colour(state.fill),
                        "opacita": state.fill_alpha,
                    },
                )
            )
            shown_since_move = True
        elif op in ("ET", "MP", "DP", "BMC", "BDC", "EMC", "Tc", "Tw", "Tz", "TL", "Ts", "Tr"):
            if op in ("Tc", "Tw", "Ts") and float(args[0]) != 0:
                raise SystemExit(f"{op} diverso da zero: il lettore non lo gestisce")
        else:
            raise SystemExit(f"operatore {op} non gestito")
    return painted, font_table, height


# --- 3. Dal disegno al modello -----------------------------------------------


def rounded(value: float) -> float:
    return round(value, DECIMALS) + 0.0


def text_width(text: str, item: Painted) -> float:
    font: Font = item.data["font"]
    return larghezza_mm(text, item.data["corpo_pt"], font.bold)


def main() -> None:
    data = SOURCE.read_bytes()
    pdf = Pdf(data)
    root = pdf.resolve(pdf.trailer["Root"])
    pages = pdf.resolve(pdf.resolve(root["Pages"])["Kids"])
    if len(pages) != 1:
        raise SystemExit(f"il cartiglio deve avere una pagina, ne ha {len(pages)}")
    page = pdf.resolve(pages[0])
    painted, font_table, height = interpret(pdf, page)
    width = float(pdf.resolve(page["MediaBox"])[2])

    # La squadratura e' il rettangolo piu' grande; la fascia sta sotto la riga
    # turchese, la testata sopra il proprio filetto.
    strokes = [item for item in painted if item.kind == "stroke" and item.data["forma"] == "rettangolo"]
    border = max(
        strokes,
        key=lambda item: abs(item.data["points"][1][0] - item.data["points"][0][0])
        * abs(item.data["points"][1][1] - item.data["points"][0][1]),
    )
    (bx1, by1), (bx2, by2) = border.data["points"]
    left, right, top, bottom = min(bx1, bx2), max(bx1, bx2), min(by1, by2), max(by1, by2)
    fills = [item for item in painted if item.kind == "fill"]
    band_top = min(min(point[1] for point in item.data["points"]) for item in fills)

    def ys(item: Painted) -> list[float]:
        if item.kind == "text":
            return [item.data["at"][1]]
        return [point[1] for point in item.data["points"]]

    header = [item for item in painted if item is not border and max(ys(item)) <= (top + band_top) / 2 and max(ys(item)) < 30]
    band = [item for item in painted if min(ys(item)) >= band_top - 1e-6]
    stray = [item for item in painted if item is not border and item not in header and item not in band]
    if stray:
        raise SystemExit(f"elementi fuori da testata e fascia: {[item.kind for item in stray]}")

    # Le caselle: i montanti della fascia, scuri e chiari.
    verticals = sorted(
        {
            item.data["points"][0][0]
            for item in band
            if item.kind == "stroke"
            and item.data["forma"] == "linea"
            and item.data["points"][0][0] == item.data["points"][1][0]
        }
        | {left, right}
    )

    def span(item: Painted, x: float, y: float) -> tuple[float, float]:
        """La casella che contiene il punto: i montanti a sinistra e a destra che
        passano alla sua altezza."""
        bars = [left, right]
        for other in band:
            if other.kind != "stroke" or other.data["forma"] != "linea":
                continue
            (x1, y1), (x2, y2) = other.data["points"]
            if x1 == x2 and min(y1, y2) - 1.5 <= y <= max(y1, y2) + 1.5:
                bars.append(x1)
        return max(bar for bar in bars if bar <= x + 1e-6), min(bar for bar in bars if bar > x + 1e-6)

    padding = {rounded(item.data["at"][0] - span(item, *item.data["at"])[0]) for item in band if item.kind == "text" and item.data["testo"] in CAMPI and CAMPI[item.data["testo"]][1] == "sinistra"}
    if len(padding) != 1:
        raise SystemExit(f"i valori non rientrano tutti allo stesso modo dal montante: {sorted(padding)}")
    indent = padding.pop()

    values_colour = next(item.data["colore"] for item in band if item.kind == "text" and item.data["testo"] == "Nome committente")
    cap_heights = {font.cap_height for font in font_table.values() if font.cap_height is not None}
    if len(cap_heights) != 1:
        raise SystemExit(f"altezze delle maiuscole diverse fra i caratteri incorporati: {cap_heights}")

    labels = {item.data["testo"]: item for item in band if item.kind == "text" and item.data["testo"] in ETICHETTE}
    header_left = [
        item for item in header
        if item.kind == "text" and item.data["testo"] in CAMPI and CAMPI[item.data["testo"]][1] == "sinistra"
    ]
    if len(header_left) != 1:
        raise SystemExit("la testata deve avere una scritta a sinistra")
    header_indent = rounded(header_left[0].data["at"][0] - left)

    def zone(items: list[Painted], anchored: bool) -> list[Any]:
        elements: list[Any] = []
        for item in items:
            if item.kind == "stroke":
                (x1, y1), (x2, y2) = item.data["points"]
                stretch = "entrambe" if anchored and x1 != x2 and abs(x2 - x1) > (right - left) / 2 else "sinistra"
                elements.append(
                    Tratto(
                        forma=item.data["forma"], x1_mm=x1, y1_mm=y1, x2_mm=x2, y2_mm=y2,
                        colore=item.data["colore"], spessore_mm=item.data["spessore_mm"], ancora=stretch,
                    )
                )
                if not anchored and item.data["forma"] == "linea" and y1 == y2:
                    for label, name in FIRME.items():
                        above = labels.get(label)
                        if above is None or above.data["at"][0] != x1:
                            continue
                        if 0 < y1 - above.data["at"][1] < 6:
                            elements.append(
                                Campo(
                                    campo=name, x_mm=x1, y_mm=rounded(y1 - FIRMA_SOPRA_LA_RIGA_MM),
                                    corpo_pt=FIRMA_CORPO_PT, corpo_minimo_pt=FIRMA_CORPO_PT,
                                    grassetto=False, colore=values_colour,
                                    larghezza_mm=rounded(x2 - x1), segnaposto="", origine="sessione",
                                )
                            )
            elif item.kind == "fill":
                (x1, y1), (x2, y2) = item.data["points"]
                elements.append(
                    Campitura(
                        x_mm=min(x1, x2), y_mm=min(y1, y2), larghezza_mm=rounded(abs(x2 - x1)),
                        altezza_mm=rounded(abs(y2 - y1)), colore=item.data["colore"], opacita=item.data["opacita"],
                    )
                )
            elif item.kind == "image":
                (x1, y1), (x2, y2) = item.data["points"]
                value = pdf.resolve(item.data["ref"])
                jpeg = pdf.stream(item.data["ref"].number, stop_at="DCTDecode")
                LOGO.write_bytes(jpeg)
                elements.append(
                    Logo(
                        file=LOGO.name, sha256=hashlib.sha256(jpeg).hexdigest(),
                        x_mm=min(x1, x2), y_mm=min(y1, y2), larghezza_mm=rounded(abs(x2 - x1)),
                        altezza_mm=rounded(abs(y2 - y1)), pixel_larghezza=value["Width"], pixel_altezza=value["Height"],
                    )
                )
            else:
                text, (x, y) = item.data["testo"], item.data["at"]
                if text in CAMPI:
                    name, alignment = CAMPI[text]
                elif text in ETICHETTE:
                    name, alignment = "", ETICHETTE[text]
                else:
                    raise SystemExit(f"testo non dichiarato nel generatore: {text!r}")
                cell = span(item, x, y) if not anchored else (left, right)
                width = text_width(text, item)
                if alignment == "centro":
                    x = rounded((cell[0] + cell[1]) / 2)
                    if abs(item.data["at"][0] + width / 2 - x) > 0.1:
                        raise SystemExit(f"{text!r} non e' centrato nella sua casella")
                elif alignment == "destra":
                    # In testata la scritta di destra rientra dal bordo quanto
                    # quella di sinistra; nella fascia, quanto i valori.
                    x = rounded(right - header_indent if anchored else cell[1] - indent)
                    if abs(item.data["at"][0] + width - x) > 0.1:
                        raise SystemExit(f"{text!r} non finisce dove il rientro dice")
                font: Font = item.data["font"]
                common = {
                    "x_mm": x, "y_mm": y, "corpo_pt": item.data["corpo_pt"], "grassetto": font.bold,
                    "colore": item.data["colore"], "opacita": item.data["opacita"], "allineamento": alignment,
                }
                if anchored:
                    common["ancora"] = "destra" if alignment == "destra" else "sinistra"
                if not name:
                    elements.append(Testo(testo=text, **common))
                    continue
                room = None if anchored else rounded(cell[1] - cell[0] - 2 * indent)
                label_y = None
                if name in A_CAPO:
                    above = [
                        other.data["at"][1] for other in band
                        if other.kind == "text" and other.data["testo"] in ETICHETTE
                        and other.data["at"][0] == item.data["at"][0] and other.data["at"][1] < y
                    ]
                    label_y = max(above)
                template = None
                if name == "intestazione":
                    if text.count(COMMESSA_IN_TESTATA) != 1:
                        raise SystemExit(f"la testata non contiene una volta {COMMESSA_IN_TESTATA}")
                    template = text.replace(COMMESSA_IN_TESTATA, "{commessa}")
                elements.append(
                    Campo(
                        campo=name, larghezza_mm=room, corpo_minimo_pt=min(CORPO_MINIMO_PT, item.data["corpo_pt"]) if not anchored else item.data["corpo_pt"],
                        a_capo=name in A_CAPO, etichetta_y_mm=label_y, segnaposto=text, origine="file", modello=template,
                        **common,
                    )
                )
        return elements

    header_box = Ingombro(x_mm=left, y_mm=top, larghezza_mm=rounded(right - left), altezza_mm=rounded(max(max(ys(item)) for item in header) - top))
    band_box = Ingombro(x_mm=left, y_mm=band_top, larghezza_mm=rounded(right - left), altezza_mm=rounded(bottom - band_top))
    widths = {font.name: dict(sorted(font.widths.items())) for font in font_table.values() if font.widths}
    model = ModelloDelCartiglio(
        fonte=Fonte(
            file=SOURCE.name,
            sha256=hashlib.sha256(data).hexdigest(),
            input=INPUT,
            generatore=str(Path(__file__).resolve().relative_to(ROOT)),
        ),
        foglio_larghezza_mm=rounded(width * PT),
        foglio_altezza_mm=rounded(height * PT),
        squadratura=Tratto(
            forma="rettangolo", x1_mm=left, y1_mm=top, x2_mm=right, y2_mm=bottom,
            colore=border.data["colore"], spessore_mm=border.data["spessore_mm"],
        ),
        testata=Zona(ingombro=header_box, elementi=zone(header, anchored=True)),
        fascia=Zona(ingombro=band_box, elementi=zone(band, anchored=False)),
        altezza_maiuscole_em=cap_heights.pop(),
        larghezze_nel_file=dict(sorted(widths.items())),
    )
    found = {item.campo for item in model.campi()}
    missing = sorted({name for name, _ in CAMPI.values()} - found)
    if missing:
        raise SystemExit(f"segnaposti dichiarati e non trovati nel file: {missing}")
    MODEL.write_text(
        json.dumps(model.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{MODEL.relative_to(ROOT)}: {len(model.testata.elementi)} elementi in testata, "
          f"{len(model.fascia.elementi)} nella fascia; {LOGO.name}: {len(LOGO.read_bytes())} byte")


if __name__ == "__main__":
    main()
