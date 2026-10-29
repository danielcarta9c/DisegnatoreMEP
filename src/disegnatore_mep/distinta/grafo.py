"""Il grafo, letto dal JSON com'e' e senza pretese, e i suoi tratti.

La distinta legge il grafo completo come dizionario: i campi del tratto che servono
— `sezione`, `lunghezza_m`, `scritta` — li cerca **sulla tubazione e, se non ci sono,
nelle sue `properties`**, con gli stessi nomi (il contratto con `REL-012`, che li
porta nel modello). Cosi' la distinta non dipende da quando il modello li avra'.

Un **tratto** e' la catena di tubazioni di una rete che passa per i pezzi
`passante` del corredo — il sezionatore sulla linea dell'unita' esterna, il sifone
sullo scarico —: e' quello che l'installatore posa in un pezzo, e quello che la
tabella delle tratte numera. La sua lunghezza e' la somma delle `lunghezza_m` date
sulle sue tubazioni; **0 su tutte** vuol dire raccordo diretto (il plenum montato
sulla macchina, un cablaggio di fabbrica), e non porta materiale.

I pezzi e le tubazioni `esistente` non entrano: non si forniscono.

**Come si chiama un pezzo** (collaudo REL-012 t1, §2.4.5): con la **sigla dello schema**,
la stessa che la tavola scrive — quella che l'ingegnere ha dato (`tag`), o quella che la
lettura dell'impianto assegna (`graph.plant.read_plant`, D-097: una sigla sola per tutto
il prodotto) —; dove un pezzo non ne ha, con la sua `etichetta`; e in ultimo col nome
della sua voce di catalogo. **Mai con l'id del grafo**: e' un codice interno, e
l'installatore non lo legge. Lo stesso per le reti (il nome, o il nome del fluido) e per
le tubazioni, che si dicono coi pezzi che collegano.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CAMPI_DEL_TRATTO = ("sezione", "lunghezza_m", "scritta")
"""I campi che `REL-012` porta sulla tubazione; finche' non ci sono, stanno in `properties`."""


def numero(valore: object) -> float | None:
    """Un numero dal JSON: 6, 6.5 o «6,5». `None` se non c'e' o non si legge."""
    if isinstance(valore, bool):
        return None
    if isinstance(valore, int | float):
        return float(valore)
    if isinstance(valore, str):
        testo = valore.strip().replace(",", ".")
        if re.fullmatch(r"-?\d+(\.\d+)?", testo):
            return float(testo)
    return None


@dataclass(frozen=True)
class Pezzo:
    id: str
    voce: str
    """L'id della voce di catalogo (`definition_id`)."""
    sigla: str
    """Come lo si nomina: la sigla dello schema, o l'etichetta, o il nome della voce.
    Mai l'id del grafo."""
    proprieta: Mapping[str, Any]


@dataclass(frozen=True)
class Tubazione:
    id: str
    rete: str
    fluido: str
    capo_a: str
    capo_b: str
    dati: Mapping[str, Any]
    """Le `properties` della tubazione, con sopra i campi del tratto se li ha in testa."""


@dataclass(frozen=True)
class Rete:
    id: str
    nome: str
    """Il `name` della rete, o il nome del fluido: mai l'id."""
    fluido: str
    dominio: str


@dataclass
class Tratta:
    rete: Rete
    tubazioni: tuple[Tubazione, ...]
    pezzi: tuple[str, ...]
    """Gli id dei pezzi in fila: il primo e l'ultimo sono i capi, in mezzo i passanti."""
    num: str = ""
    lunghezza_m: float | None = None
    """La lunghezza data dal progettista (somma delle `lunghezza_m`), prima della maggiorazione."""
    senza_lunghezza: tuple[str, ...] = ()
    """Le tubazioni del tratto senza `lunghezza_m`."""
    illeggibili: tuple[str, ...] = ()
    """Le tubazioni con una `lunghezza_m` che non e' un numero."""
    da_quotare_m: float | None = None
    calcolo_della_lunghezza: str = ""
    sezioni: tuple[str, ...] = field(default_factory=tuple)

    @property
    def fluido(self) -> str:
        return self.rete.fluido

    @property
    def capi(self) -> tuple[str, str]:
        return self.pezzi[0], self.pezzi[-1]

    @property
    def diretta(self) -> bool:
        """Raccordo diretto: ogni tubazione ha `lunghezza_m` 0."""
        return (
            not self.senza_lunghezza
            and not self.illeggibili
            and self.lunghezza_m is not None
            and self.lunghezza_m == 0
        )

    @property
    def sezione(self) -> str | None:
        return self.sezioni[0] if len(self.sezioni) == 1 else None

    def dato(self, nome: str) -> Any:
        """Il primo valore del dato sulle tubazioni del tratto, nell'ordine del tratto."""
        for tubazione in self.tubazioni:
            valore = tubazione.dati.get(nome)
            if valore is not None and valore != "":
                return valore
        return None


@dataclass(frozen=True)
class Impianto:
    metadati: Mapping[str, Any]
    pezzi: Mapping[str, Pezzo]
    """Per id, nell'ordine del grafo."""
    tubazioni: tuple[Tubazione, ...]
    reti: Mapping[str, Rete]
    esclusi: tuple[str, ...]
    """I pezzi e le tubazioni esistenti, lasciati fuori, detti per nome."""

    def conta(self, voce: str) -> int:
        return sum(1 for pezzo in self.pezzi.values() if pezzo.voce == voce)

    def nome(self, pezzo: str) -> str:
        """La sigla del pezzo, per chi legge; un pezzo che non c'e' resta col suo id."""
        trovato = self.pezzi.get(pezzo)
        return trovato.sigla if trovato else pezzo

    def tubazione_in_parole(self, tubazione: Tubazione) -> str:
        """Una tubazione detta coi pezzi che collega: «la tubazione SZ-01 - UE-01»."""
        return f"la tubazione {self.nome(tubazione.capo_a)} - {self.nome(tubazione.capo_b)}"


def _testo(valore: object, dove: str) -> str:
    if not isinstance(valore, str) or not valore:
        raise ValueError(f"il grafo non si legge: {dove}")
    return valore


def _nome_del_pezzo(
    pezzo: Mapping[str, Any], ident: str, voce: str, sigle: Mapping[str, str], nomi_del_catalogo: Mapping[str, str]
) -> str:
    """La sigla dello schema; senza, l'etichetta; senza, il nome della voce di catalogo."""
    proprieta = pezzo.get("properties") or {}
    for candidato in (pezzo.get("tag"), sigle.get(ident), proprieta.get("etichetta"), pezzo.get("label")):
        if isinstance(candidato, str) and candidato.strip():
            return candidato.strip()
    return str(nomi_del_catalogo.get(voce) or voce)


def leggi_impianto(
    grafo: Mapping[str, Any],
    sigle: Mapping[str, str] | None = None,
    nomi_del_catalogo: Mapping[str, str] | None = None,
    nomi_dei_fluidi: Mapping[str, str] | None = None,
) -> Impianto:
    """Il grafo completo, dal JSON. Si ferma solo se manca la struttura (id, reti, capi).

    `sigle` sono quelle che la lettura dell'impianto assegna (`sigle_dello_schema`);
    i nomi servono a dire un pezzo senza sigla ne' etichetta, e una rete senza nome."""
    sigle = sigle or {}
    nomi_del_catalogo = nomi_del_catalogo or {}
    nomi_dei_fluidi = nomi_dei_fluidi or {}
    esclusi: list[str] = []
    reti: dict[str, Rete] = {}
    for rete in grafo.get("networks", []):
        ident = _testo(rete.get("id"), "una rete senza id")
        fluido = _testo(rete.get("medium"), f"la rete {ident} senza medium")
        reti[ident] = Rete(
            id=ident,
            nome=str(rete.get("name") or nomi_dei_fluidi.get(fluido) or fluido),
            fluido=fluido,
            dominio=str(rete.get("domain") or ""),
        )
    pezzi: dict[str, Pezzo] = {}
    tutti: dict[str, str] = {}
    pezzi_esistenti: set[str] = set()
    for pezzo in grafo.get("components", []):
        ident = _testo(pezzo.get("id"), "un pezzo senza id")
        voce = _testo(pezzo.get("definition_id"), f"il pezzo {ident} senza definition_id")
        tutti[ident] = _nome_del_pezzo(pezzo, ident, voce, sigle, nomi_del_catalogo)
        if pezzo.get("esistente"):
            esclusi.append(tutti[ident])
            pezzi_esistenti.add(ident)
            continue
        pezzi[ident] = Pezzo(
            id=ident,
            voce=voce,
            sigla=tutti[ident],
            proprieta=dict(pezzo.get("properties") or {}),
        )
    tubazioni: list[Tubazione] = []
    for tubazione in grafo.get("connections", []):
        ident = _testo(tubazione.get("id"), "una tubazione senza id")
        rete = _testo(tubazione.get("network_id"), f"la tubazione {ident} senza rete")
        if rete not in reti:
            raise ValueError(f"il grafo non si legge: la tubazione {ident} nomina la rete {rete}, che non c'e'")
        capo_a = _testo((tubazione.get("endpoint_a") or {}).get("component_id"), f"{ident}: capo a")
        capo_b = _testo((tubazione.get("endpoint_b") or {}).get("component_id"), f"{ident}: capo b")
        if tubazione.get("esistente") or capo_a in pezzi_esistenti or capo_b in pezzi_esistenti:
            esclusi.append(f"la tubazione {tutti.get(capo_a, capo_a)} - {tutti.get(capo_b, capo_b)}")
            continue
        dati = dict(tubazione.get("properties") or {})
        for campo in CAMPI_DEL_TRATTO:
            if tubazione.get(campo) is not None:
                dati[campo] = tubazione[campo]
        tubazioni.append(
            Tubazione(id=ident, rete=rete, fluido=reti[rete].fluido, capo_a=capo_a, capo_b=capo_b, dati=dati)
        )
    return Impianto(
        metadati=dict(grafo.get("metadata") or {}),
        pezzi=pezzi,
        tubazioni=tuple(tubazioni),
        reti=reti,
        esclusi=tuple(esclusi),
    )


def tratte_dell_impianto(impianto: Impianto, voci_passanti: Iterable[str]) -> list[Tratta]:
    """I tratti, nell'ordine in cui il grafo nomina la loro prima tubazione."""
    passanti = set(voci_passanti)
    per_capo: dict[tuple[str, str], list[Tubazione]] = {}
    for tubazione in impianto.tubazioni:
        for capo in (tubazione.capo_a, tubazione.capo_b):
            per_capo.setdefault((tubazione.rete, capo), []).append(tubazione)

    def attraversa(pezzo: str, rete: str) -> bool:
        voce = impianto.pezzi[pezzo].voce if pezzo in impianto.pezzi else ""
        return voce in passanti and len(per_capo.get((rete, pezzo), [])) == 2

    def altro_capo(tubazione: Tubazione, capo: str) -> str:
        return tubazione.capo_b if tubazione.capo_a == capo else tubazione.capo_a

    viste: set[str] = set()
    tratte: list[Tratta] = []
    for prima in impianto.tubazioni:
        if prima.id in viste:
            continue
        viste.add(prima.id)
        catena = [prima]
        pezzi = [prima.capo_a, prima.capo_b]
        for verso in (1, -1):
            while True:
                capo = pezzi[-1] if verso == 1 else pezzi[0]
                if not attraversa(capo, prima.rete):
                    break
                seguenti = [t for t in per_capo[(prima.rete, capo)] if t.id not in viste]
                if not seguenti:
                    break
                seguente = seguenti[0]
                viste.add(seguente.id)
                if verso == 1:
                    catena.append(seguente)
                    pezzi.append(altro_capo(seguente, capo))
                else:
                    catena.insert(0, seguente)
                    pezzi.insert(0, altro_capo(seguente, capo))
        tratta = Tratta(rete=impianto.reti[prima.rete], tubazioni=tuple(catena), pezzi=tuple(pezzi))
        lunghezze = [(t.id, t.dati.get("lunghezza_m")) for t in catena]
        tratta.senza_lunghezza = tuple(i for i, v in lunghezze if v is None or v == "")
        tratta.illeggibili = tuple(i for i, v in lunghezze if v not in (None, "") and numero(v) is None)
        date = [numero(v) for _, v in lunghezze if numero(v) is not None]
        tratta.lunghezza_m = sum(x for x in date if x is not None) if date else None
        sezioni: list[str] = []
        for tubazione in catena:
            sezione = tubazione.dati.get("sezione")
            if isinstance(sezione, str) and sezione.strip() and sezione.strip() not in sezioni:
                sezioni.append(sezione.strip())
        tratta.sezioni = tuple(sezioni)
        tratte.append(tratta)
    return tratte


def sigle_dello_schema(grafo: Mapping[str, Any], cartella_del_catalogo: Path, cartella_dei_nomi: Path) -> dict[str, str]:
    """Le sigle che lo schema scrive, dalla **stessa** lettura dell'impianto che le da'
    alla tavola (`graph.plant.read_plant`): la distinta non ne inventa di sue.

    Se il grafo non si lascia leggere — un pezzo che il catalogo non ha, una tubazione
    al contrario — nessuna sigla calcolata: valgono quelle scritte dall'ingegnere, e
    dove non ce ne sono l'etichetta (`leggi_impianto`). La distinta esce lo stesso."""
    from pydantic import ValidationError

    from disegnatore_mep.catalog.errors import CatalogError
    from disegnatore_mep.catalog.registry import ComponentRegistry
    from disegnatore_mep.graph.naming import Naming, NamingError
    from disegnatore_mep.graph.plant import GraphError, read_plant
    from disegnatore_mep.model.project import ProjectModel

    try:
        modello = ProjectModel.model_validate(dict(grafo))
        catalogo = ComponentRegistry.from_directory(cartella_del_catalogo).per_il_progetto(modello)
        return dict(read_plant(modello, catalogo, Naming.from_directory(cartella_dei_nomi)).sigle)
    except (ValidationError, CatalogError, GraphError, NamingError, ValueError, OSError):
        return {}
