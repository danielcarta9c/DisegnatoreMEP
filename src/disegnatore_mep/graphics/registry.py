from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .symbol import SymbolManifest


class SymbolError(ValueError):
    pass


@dataclass(frozen=True)
class Symbol:
    """Un simbolo pubblicato: manifesto geometrico piu' corpo grafico SVG."""

    manifest: SymbolManifest
    body: str


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
            if "<svg" in body:
                raise SymbolError(
                    f"svg body must not contain an <svg> root: {body_path}"
                )
            symbols.append(Symbol(manifest=manifest, body=body))
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
