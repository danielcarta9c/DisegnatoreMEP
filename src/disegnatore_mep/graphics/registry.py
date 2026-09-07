from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from pydantic import ValidationError

from .errors import SymbolError
from .symbol import SymbolManifest

# SymbolError vive in .errors, ma resta esportato da qui: e' il nome con cui il
# resto del progetto lo importa da quando esisteva un solo modulo a sollevarlo.
__all__ = ["Symbol", "SymbolError", "SymbolRegistry"]


def _local_name(tag: str) -> str:
    """Nome dell'elemento senza il prefisso di namespace `{uri}` di ElementTree."""
    return tag.rpartition("}")[2]


@dataclass(frozen=True)
class Symbol:
    """Un simbolo pubblicato: manifesto geometrico piu' corpo grafico SVG."""

    manifest: SymbolManifest
    body: str
    body_transform: str = ""
    """Trasformazione SVG che porta il corpo nel riquadro ruotato, vuota a 0 gradi."""

    def rotated(self, degrees: int) -> "Symbol":
        """Il simbolo ruotato: manifesto trasformato e corpo avvolto nella
        matrice equivalente.

        Le due trasformazioni devono coincidere, o il disegno si stacca dai
        propri attacchi; `tests/graphics/test_rotation.py` lo verifica angolo
        per angolo su tutta la libreria pubblicata.

        **I glifi dichiarati leggibili non girano** (DRAW-005, I-033): ogni
        gruppo `data-glyph` del corpo riceve la rotazione contraria attorno al
        proprio centro, cosi' che la lettera segua il centro spostato e resti
        dritta rispetto al foglio. Corpo e porte girano come sempre.
        """
        manifest = self.manifest.rotated(degrees)
        if degrees == 0:
            return self
        width, height = self.manifest.width_mm, self.manifest.height_mm
        transform = {
            90: f"translate({height:g} 0) rotate(90)",
            180: f"translate({width:g} {height:g}) rotate(180)",
            270: f"translate(0 {width:g}) rotate(270)",
        }[degrees]
        body = self.body
        for glyph in self.manifest.upright_glyphs:
            body = body.replace(
                f'<g data-glyph="{glyph.id}"',
                f'<g data-glyph="{glyph.id}" '
                f'transform="rotate({-degrees:g} {glyph.x_mm:g} {glyph.y_mm:g})"',
                1,
            )
        return Symbol(
            manifest=manifest,
            body=f'<g transform="{transform}">{body}</g>',
            body_transform=transform,
        )


class SymbolRegistry:
    def __init__(self, symbols: list[Symbol]) -> None:
        self._symbols: dict[str, Symbol] = {}
        for symbol in symbols:
            if symbol.manifest.id in self._symbols:
                raise SymbolError(f"duplicate symbol: {symbol.manifest.id}")
            self._symbols[symbol.manifest.id] = symbol

    @classmethod
    def from_directory(cls, directory: Path) -> "SymbolRegistry":
        if not directory.is_dir():
            raise SymbolError(f"symbol directory not found: {directory}")
        symbols: list[Symbol] = []
        for path in sorted(directory.glob("*.json")):
            try:
                manifest = SymbolManifest.model_validate_json(path.read_text("utf-8"))
            except (OSError, ValidationError, ValueError) as exc:
                raise SymbolError(f"invalid symbol manifest {path}: {exc}") from exc
            if manifest.id != path.stem:
                raise SymbolError(f"file name does not match symbol id: {path}")
            body_path = path.with_suffix(".svg")
            if not body_path.is_file():
                raise SymbolError(f"missing svg body for {manifest.id}")
            body = body_path.read_text("utf-8").strip()
            if not body:
                raise SymbolError(f"empty svg body for {manifest.id}")
            # The body is spliced verbatim into the sheet, so a body that is not
            # well-formed makes the whole sheet unparseable. Parsed here, wrapped
            # in a group exactly as the sheet nests it, so the failure lands on
            # the file that caused it instead of on the rendered deliverable.
            try:
                root = ElementTree.fromstring(f"<g>{body}</g>")
            except ElementTree.ParseError as exc:
                raise SymbolError(f"svg body is not well-formed xml {body_path}: {exc}") from exc
            if any(_local_name(element.tag) == "svg" for element in root.iter()):
                raise SymbolError(f"svg body must not contain an <svg> root: {body_path}")
            # Ogni glifo dichiarato leggibile ha il proprio gruppo nel corpo, e
            # viceversa: un glifo dichiarato e non disegnato resterebbe una
            # promessa, uno disegnato e non dichiarato girerebbe col corpo.
            declared = {item.id for item in manifest.upright_glyphs}
            drawn = [
                element.get("data-glyph", "")
                for element in root.iter()
                if _local_name(element.tag) == "g" and element.get("data-glyph")
            ]
            if len(drawn) != len(set(drawn)) or set(drawn) != declared:
                raise SymbolError(
                    f"upright glyphs of {manifest.id} do not match its body: the "
                    f"manifest declares {sorted(declared)}, the body draws "
                    f"{sorted(drawn)} — each declared glyph is one data-glyph group"
                )
            # La rotazione contraria si scrive nel testo del gruppo, subito
            # dopo `data-glyph`: il gruppo va scritto cosi', e senza una
            # trasformazione propria, o ne avrebbe due.
            for glyph_id in drawn:
                element = next(
                    item
                    for item in root.iter()
                    if _local_name(item.tag) == "g" and item.get("data-glyph") == glyph_id
                )
                if element.get("transform") is not None or f'<g data-glyph="{glyph_id}"' not in body:
                    raise SymbolError(
                        f"the glyph group {glyph_id} of {manifest.id} must open with "
                        f'<g data-glyph="{glyph_id}" and carry no transform of its '
                        f"own: the registry writes the counter-rotation there"
                    )
            symbols.append(Symbol(manifest=manifest, body=body))
        if not symbols:
            raise SymbolError(f"no symbol manifests found in: {directory}")
        return cls(symbols)

    def get(self, symbol_id: str) -> Symbol:
        try:
            return self._symbols[symbol_id]
        except KeyError as exc:
            raise SymbolError(f"unknown symbol: {symbol_id}") from exc

    def contains(self, symbol_id: str) -> bool:
        return symbol_id in self._symbols

    def all(self) -> tuple[Symbol, ...]:
        return tuple(self._symbols[key] for key in sorted(self._symbols))
