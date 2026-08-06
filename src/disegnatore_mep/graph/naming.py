"""Come si chiamano le famiglie e i fluidi: due tabelle, e sono **dati**.

La sigla di un pezzo e' fatta di due cose — la famiglia e un numero — e la
famiglia si legge dal **mestiere che il pezzo dichiara**, mai dal suo nome e mai
dalla voce di catalogo con cui e' stato scelto (D-090). Se la tabella delle
famiglie fosse scritta nel programma, aggiungere una famiglia vorrebbe dire
toccare il programma, ed e' esattamente il difetto che il progetto ha gia'
corretto sulle regole: si aggiunge un file, non una riga di codice.

Le due tabelle stanno in `naming/`:

- `families.json` — per ogni mestiere, la sigla di famiglia, come si chiama
  quella famiglia in italiano, e se un pezzo di quella famiglia e' un **punto da
  cui la lettura comincia** (D-098);
- `media.json` — come si chiama in parole cio' che scorre nei tubi.

**L'ordine dell'elenco delle famiglie conta**, ed e' l'unica cosa che il file
non puo' dire due volte: un pezzo che fa piu' mestieri prende la prima famiglia
che combacia, e le sorgenti si leggono nell'ordine in cui le loro famiglie
compaiono — prima chi il calore lo produce, poi il confine da cui il fluido
entra nell'edificio.

Cio' che non si sa dire non si tace: una funzione senza famiglia e un fluido
senza nome fanno fallire, nominando il colpevole. E' la stessa scelta del
catalogo, e per lo stesso motivo — un pezzo senza sigla non si puo' ne' citare
ne' contare.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeVar

from pydantic import Field, ValidationError, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel

FAMILIES_FILE = "families.json"
MEDIA_FILE = "media.json"
LINES_FILE = "lines.json"

Table = TypeVar("Table", bound=StrictModel)


class NamingError(ValueError):
    """Qualcosa che non si sa chiamare per nome."""


class FamilyEntry(StrictModel):
    """Una famiglia di pezzi: il mestiere che la definisce e la sua sigla."""

    function: str = Field(pattern=ID_PATTERN)
    """Il mestiere dichiarato dal catalogo. E' la chiave: mai un nome di pezzo."""

    prefix: str = Field(pattern=r"^[A-Z]{2,4}$")
    """La sigla con cui quella famiglia si scrive da sempre su uno schema."""

    name: str = Field(min_length=1)
    """Come si chiama la famiglia in italiano, per chi legge il documento."""

    starts_the_reading: bool = False
    """Se da un pezzo di questa famiglia la lettura dell'impianto comincia.

    Sono i generatori e i confini da cui il fluido entra (D-098). Un confine
    conta come partenza solo se il fluido **esce** da lui: un prelievo e' un
    confine anche lui, ma e' dove il fluido se ne va.
    """


class FamilyTable(StrictModel):
    note: str = Field(min_length=1)
    families: list[FamilyEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def each_trade_and_each_prefix_appears_once(self) -> "FamilyTable":
        for label, values in (
            ("mestiere", [item.function for item in self.families]),
            ("sigla di famiglia", [item.prefix for item in self.families]),
        ):
            twice = sorted({item for item in values if values.count(item) > 1})
            if twice:
                raise ValueError(
                    f"lo stesso {label} compare due volte: {', '.join(twice)}. "
                    f"Due righe per la stessa cosa vorrebbero dire che la sigla "
                    f"dipende da quale delle due si legge per prima"
                )
        return self


class MediumEntry(StrictModel):
    medium: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)


class MediumTable(StrictModel):
    note: str = Field(min_length=1)
    media: list[MediumEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def each_fluid_appears_once(self) -> "MediumTable":
        names = [item.medium for item in self.media]
        twice = sorted({item for item in names if names.count(item) > 1})
        if twice:
            raise ValueError(f"lo stesso fluido compare due volte: {', '.join(twice)}")
        return self


class LineFamilyEntry(StrictModel):
    """Una famiglia di linee idrauliche: che acqua porta e da che parte va (D-105).

    La riga si legge dal **fluido della rete**, dal **mestiere della sorgente**
    da cui la rete parte e dal **verso**. I campi facoltativi valgono «qualunque»:
    l'acqua fredda sanitaria e' `AF` comunque la si percorra.
    """

    medium: str = Field(pattern=ID_PATTERN)
    fed_by: Literal["generator", "store", "boundary", "other"] | None = None
    """Chi da' origine alla rete: un generatore fa un circuito primario, una
    riserva un secondario. Vuoto = qualunque origine."""

    direction: Literal["supply", "return"] | None = None
    """Mandata o ritorno. Vuoto = la famiglia non distingue il verso."""

    prefix: str = Field(pattern=r"^[A-Z]{2,4}$")
    name: str = Field(min_length=1)
    """Come si chiama in italiano: «mandata primaria», «acqua fredda sanitaria»."""


class LineFamilyTable(StrictModel):
    note: str = Field(min_length=1)
    families: list[LineFamilyEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def each_case_appears_once(self) -> "LineFamilyTable":
        keys = [(item.medium, item.fed_by, item.direction) for item in self.families]
        twice = sorted({str(item) for item in keys if keys.count(item) > 1})
        if twice:
            raise ValueError(
                f"lo stesso caso compare due volte: {', '.join(twice)}. "
                f"Due righe per lo stesso caso vorrebbero dire che la sigla della "
                f"linea dipende da quale delle due si legge per prima"
            )
        prefixes = [item.prefix for item in self.families]
        repeated = sorted({item for item in prefixes if prefixes.count(item) > 1})
        if repeated:
            raise ValueError(
                f"la stessa sigla di linea compare due volte: {', '.join(repeated)}"
            )
        return self


@dataclass(frozen=True)
class LineNaming:
    """La tabella delle famiglie di linea, pronta da interrogare (D-105)."""

    families: tuple[LineFamilyEntry, ...]

    @classmethod
    def from_directory(cls, directory: Path) -> "LineNaming":
        table = Naming._read(directory / LINES_FILE, LineFamilyTable)
        return cls(families=tuple(table.families))

    def family_for(self, medium: str, fed_by: str, direction: str) -> LineFamilyEntry:
        """La famiglia di una linea, dalla prima riga che combacia."""
        for entry in self.families:
            if entry.medium != medium:
                continue
            if entry.fed_by is not None and entry.fed_by != fed_by:
                continue
            if entry.direction is not None and entry.direction != direction:
                continue
            return entry
        raise NamingError(
            f"nessuna famiglia di linea per il fluido {medium!r} che parte da "
            f"{fed_by!r} in verso {direction!r}: aggiungerne una all'elenco delle "
            f"famiglie di linea invece di lasciare la linea senza sigla"
        )


@dataclass(frozen=True)
class Naming:
    """Le due tabelle caricate, pronte da interrogare."""

    families: tuple[FamilyEntry, ...]
    media: tuple[MediumEntry, ...]

    @classmethod
    def from_directory(cls, directory: Path) -> "Naming":
        return cls(
            families=tuple(cls._read(directory / FAMILIES_FILE, FamilyTable).families),
            media=tuple(cls._read(directory / MEDIA_FILE, MediumTable).media),
        )

    @staticmethod
    def _read(path: Path, shape: type[Table]) -> Table:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise NamingError(f"non trovo la tabella {path.name}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise NamingError(f"la tabella {path.name} non e' JSON valido: {exc}") from exc
        try:
            return shape.model_validate(payload)
        except ValidationError as exc:
            raise NamingError(f"la tabella {path.name} non e' valida: {exc}") from exc

    # --- cio' che si puo' chiedere -------------------------------------------

    def family_of(self, functions: tuple[str, ...], because: str) -> FamilyEntry:
        """La famiglia di un pezzo, dal primo mestiere che combacia.

        `because` serve solo alla diagnostica: dice di chi si stava parlando
        quando la tabella non ha saputo rispondere.
        """
        declared = set(functions)
        for entry in self.families:
            if entry.function in declared:
                return entry
        raise NamingError(
            f"nessuna famiglia per un pezzo che fa {', '.join(sorted(declared))} "
            f"({because}): aggiungerne una all'elenco delle famiglie invece di "
            f"lasciare il pezzo senza sigla"
        )

    def order_of(self, entry: FamilyEntry) -> int:
        """La posizione della famiglia nell'elenco: e' l'ordine delle sorgenti."""
        return self.families.index(entry)

    def name_of_medium(self, medium: str) -> str:
        for entry in self.media:
            if entry.medium == medium:
                return entry.name
        raise NamingError(
            f"non so come chiamare in parole il fluido {medium!r}: aggiungerlo "
            f"all'elenco dei fluidi invece di lasciarlo comparire com'e' davanti "
            f"a chi legge"
        )


__all__ = [
    "FAMILIES_FILE",
    "LINES_FILE",
    "MEDIA_FILE",
    "FamilyEntry",
    "FamilyTable",
    "LineFamilyEntry",
    "LineFamilyTable",
    "LineNaming",
    "MediumEntry",
    "MediumTable",
    "Naming",
    "NamingError",
]
