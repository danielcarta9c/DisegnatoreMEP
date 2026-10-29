import re
from collections.abc import Iterable
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

    def rotated(self, degrees: int, mirrored: bool = False) -> "Symbol":
        """Il simbolo nella giacitura chiesta: manifesto trasformato e corpo
        avvolto nella matrice equivalente.

        Le due trasformazioni devono coincidere, o il disegno si stacca dai
        propri attacchi; `tests/graphics/test_rotation.py` lo verifica giacitura
        per giacitura su tutta la libreria pubblicata.

        **Le giaciture sono otto** (**D-169**): le quattro rotazioni ammesse,
        per diritto o **specchiato**. Lo specchio si applica **prima** della
        rotazione, attorno all'asse verticale del riquadro, ed e' la stessa
        convenzione del manifesto — se le due divergono, il corpo si stacca
        dalle porte.

        **I glifi dichiarati leggibili non girano** (DRAW-005, I-033): ogni
        gruppo `data-glyph` del corpo riceve la trasformazione **contraria**
        attorno al proprio centro, cosi' che la lettera segua il centro spostato
        e resti dritta rispetto al foglio. Con lo specchio la contraria e' uno
        specchio piu' una rotazione: **una lettera non si legge allo specchio**.
        Corpo e porte girano come sempre.
        """
        manifest = self.manifest.rotated(degrees, mirrored)
        if degrees == 0 and not mirrored:
            return self
        width, height = self.manifest.width_mm, self.manifest.height_mm
        giro = {
            0: "",
            90: f"translate({height:g} 0) rotate(90)",
            180: f"translate({width:g} {height:g}) rotate(180)",
            270: f"translate(0 {width:g}) rotate(270)",
        }[degrees]
        # SVG applica le trasformazioni **da destra a sinistra**: lo specchio
        # scritto per ultimo e' quello che agisce per primo, che e' la
        # convenzione del manifesto.
        specchio = f"translate({width:g} 0) scale(-1 1)" if mirrored else ""
        transform = " ".join(part for part in (giro, specchio) if part)
        body = self.body
        for glyph in self.manifest.upright_glyphs:
            contraria = f"rotate({-degrees:g} {glyph.x_mm:g} {glyph.y_mm:g})"
            if mirrored:
                # Prima si disfa la rotazione attorno al centro del glifo, poi
                # lo specchio attorno alla verticale che ci passa: la
                # composizione delle due con la trasformazione esterna e' una
                # traslazione pura, e il glifo resta dritto e leggibile.
                contraria = f"translate({2 * glyph.x_mm:g} 0) scale(-1 1) {contraria}"
            body = body.replace(
                f'<g data-glyph="{glyph.id}"',
                f'<g data-glyph="{glyph.id}" transform="{contraria}"',
                1,
            )
        return Symbol(
            manifest=manifest,
            body=f'<g transform="{transform}">{body}</g>',
            body_transform=transform,
        )

    @property
    def porte_col_moncone(self) -> frozenset[str]:
        """Le porte che il corpo disegna in un gruppo `data-port` suo."""
        return frozenset(re.findall(r'<g data-port="([^"]+)">', self.body))

    def senza_le_porte(self, porte: Iterable[str]) -> "Symbol":
        """Il simbolo senza il moncone delle `porte` (collaudo T1 di REL-012, §3).

        Una porta che la tavola non collega non disegna niente: il suo gruppo
        `data-port` si toglie dal corpo. I simboli che non hanno gruppi — tutti gli
        idronici — restano quelli che sono, byte per byte. Si chiama **prima** di
        `rotated`: il manifesto non cambia, cambia solo il disegno."""
        body = self.body
        for porta in sorted(set(porte)):
            body = re.sub(rf'<g data-port="{re.escape(porta)}">.*?</g>', "", body, count=1)
        if body == self.body:
            return self
        return Symbol(manifest=self.manifest, body=body, body_transform=self.body_transform)


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
            # Un moncone in un gruppo `data-port` (collaudo T1 di REL-012): il gruppo
            # nomina una porta del manifesto, una volta sola, senza trasformazione e
            # senza gruppi dentro — il motore lo toglie per testo, quando la porta
            # non e' collegata, e un gruppo annidato si chiuderebbe al posto sbagliato.
            monconi = [
                element
                for element in root.iter()
                if _local_name(element.tag) == "g" and element.get("data-port") is not None
            ]
            nominate = [element.get("data-port", "") for element in monconi]
            for element, porta in zip(monconi, nominate, strict=True):
                if (
                    porta not in manifest.port_ids
                    or nominate.count(porta) > 1
                    or element.get("transform") is not None
                    or any(_local_name(figlio.tag) == "g" for figlio in element.iter() if figlio is not element)
                    or f'<g data-port="{porta}">' not in body
                ):
                    raise SymbolError(
                        f"the port group {porta!r} of {manifest.id} must name one port of "
                        f'the manifest, once, open with <g data-port="{porta}">, and carry '
                        f"no transform and no nested group"
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
