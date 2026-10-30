"""Le regole della distinta, come dato (`rules/distinta/`).

Sei file, ciascuno con la sua parte: `distinta` (sezioni, intestazione), `lunghezze`
(la maggiorazione e i minimi), `fluidi` (che cosa costa a metro e a giunzione),
`corredo` (che cosa porta con se' ogni voce di catalogo), `attivita` (attivita' a
corpo, varianti, opere generali), `verifica` (le soglie che si segnalano). Si leggono
da una cartella, o da un file solo nella forma dei fasci della skill
(`{"fascio": "distinta", "file": {"distinta.json": {...}, ...}}`): la skill su claude.ai
porta i suoi dati in un file per cartella (I-188).

**Ogni voce porta `fonte`, `fonte_in_parole` e `perche`**: una regola senza uno dei tre
non si carica, e il caricamento dice quale. `fonte` e' la fonte di sviluppo (il kit, il
rapporto, il rilievo) e resta qui; `fonte_in_parole` e' quella che esce nelle uscite,
scritta per l'installatore o il tecnico che le legge (collaudo REL-012 t1, §2.4.5).

**La fornitura e' una scelta dell'offerta, non un fatto** (§2.4.4): chi fornisce le
apparecchiature, le bocchette e le griglie, le opere edili, e con chi si fa la messa in
servizio stanno in `distinta.json`, `fornitura.scelte`, con il valore predefinito di
Nove C. La distinta li dichiara come assunzione da confermare, finche' il progettista
non li conferma (o li cambia) con `--fornitura`.
"""

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FILE_DELLE_REGOLE = ("distinta", "lunghezze", "fluidi", "corredo", "attivita", "verifica")

CALCOLI_DEI_FLUIDI = frozenset(
    {
        "lunghezza",
        "confezioni",
        "per_tratta",
        "passo",
        "per_metro",
        "metri_arrotondati",
        "fisso",
        "attraversamenti",
        "proprieta",
        "carica_refrigerante",
    }
)
CALCOLI_DEL_CORREDO = frozenset({"per_pezzo", "per_linea", "per_locale"})
CONDIZIONI = frozenset({"sempre", "voci", "fluidi"})


FORNITURA_INSTALLATORE = "installatore"
FORNITURA_COMMITTENTE = "committente"


class ErroreDelleRegole(ValueError):
    """Le regole della distinta non si caricano: il messaggio dice dove e perche'."""


def _chiave(valore: str) -> str:
    """«Nove C», «nove-c», «novec» sono la stessa scelta."""
    return "".join(c for c in valore.casefold() if c.isalnum())


@dataclass(frozen=True)
class Fornitura:
    """Chi fornisce che cosa in questa offerta: le scelte di `distinta.json`, con i
    valori predefiniti o quelli dati con `--fornitura`."""

    scelte: Mapping[str, Mapping[str, Any]]
    """Per id della scelta, come la scrive `distinta.json`."""
    valori: Mapping[str, str]
    """Per id della scelta, il valore di questa offerta."""
    confermata: bool
    """`False`: valgono le regole predefinite, e la distinta lo dichiara da confermare."""
    installatore: str = FORNITURA_INSTALLATORE

    def testo(self, scelta: str) -> str:
        """Come la scelta si scrive in una frase: «fornite da Nove C», «con Nove C»."""
        return str(self.scelte[scelta]["testi"][self.valori[scelta]])

    def sezione_e_chi(self, sezione: str, fornitura: object) -> tuple[str, str]:
        if isinstance(fornitura, str) and fornitura in self.scelte:
            chi = self.valori[fornitura]
            dove = self.scelte[fornitura].get("sezione_se_installatore")
            if chi == self.installatore and isinstance(dove, str):
                return dove, chi
            return sezione, chi
        if fornitura == FORNITURA_COMMITTENTE:
            return sezione, FORNITURA_COMMITTENTE
        return sezione, self.installatore

    def _parti(self) -> str:
        return "; ".join(f"{s['nome']} {self.testo(i)}" for i, s in self.scelte.items())

    def in_parole(self) -> str:
        """La riga delle cose da confermare (il comando, l'Excel, il foglio dei calcoli)."""
        if self.confermata:
            return f"Fornitura per questa offerta: {self._parti()}."
        return f"Fornitura: {self._parti()} — come da regole predefinite di Nove C; confermare per questa offerta."

    def nota(self) -> str:
        """La stessa cosa fra le note, e quindi sul foglio: corta, perche' sta in una riga
        della tabella delle note."""
        gruppi: list[tuple[list[str], str]] = []
        for ident, scelta in self.scelte.items():
            testo = self.testo(ident)
            if gruppi and gruppi[-1][1] == testo:
                gruppi[-1][0].append(str(scelta["nome"]))
            else:
                gruppi.append(([str(scelta["nome"])], testo))
        parti = "; ".join(f"{', '.join(nomi)} {testo}" for nomi, testo in gruppi)
        return f"Fornitura{'' if self.confermata else ' da confermare'}: {parti}."


def la_fornitura(regole: "RegoleDellaDistinta", data: str | None = None) -> Fornitura:
    """La fornitura dell'offerta. `data` e' quella dell'opzione `--fornitura`:
    «apparecchiature=installatore,bocchette_e_griglie=installatore», o «confermata» per
    confermare le predefinite. Senza, valgono le predefinite, da confermare. Una scelta
    o un valore che le regole non hanno e' un errore che dice quali ci sono."""
    scelte = {str(s["id"]): s for s in regole.distinta["fornitura"]["scelte"]}
    valori = {i: str(s["predefinita"]) for i, s in scelte.items()}
    if data is None:
        return Fornitura(scelte=scelte, valori=valori, confermata=False)
    for parte in (p.strip() for p in data.split(",")):
        if not parte or _chiave(parte) in ("confermata", "predefinita"):
            continue
        nome, uguale, valore = parte.partition("=")
        nome = nome.strip().replace("-", "_")
        if not uguale or nome not in scelte:
            raise ErroreDelleRegole(
                f"--fornitura: «{parte}» non e' una scelta; le scelte sono "
                + ", ".join(f"{i}=<{'|'.join(s['ammesse'])}>" for i, s in scelte.items())
                + ", oppure «confermata»"
            )
        ammessi = {_chiave(str(a)): str(a) for a in scelte[nome]["ammesse"]}
        if _chiave(valore) not in ammessi:
            raise ErroreDelleRegole(
                f"--fornitura: {nome} vale {', '.join(ammessi.values())}, non «{valore.strip()}»"
            )
        valori[nome] = ammessi[_chiave(valore)]
    return Fornitura(scelte=scelte, valori=valori, confermata=True)


@dataclass(frozen=True)
class RegoleDellaDistinta:
    """Le regole caricate e controllate. I campi sono i JSON come sono scritti."""

    distinta: Mapping[str, Any]
    lunghezze: Mapping[str, Any]
    fluidi: Mapping[str, Mapping[str, Any]]
    """Per fluido (il `medium` della rete), nell'ordine del file."""
    corredo: Mapping[str, Mapping[str, Any]]
    """Per id di voce di catalogo."""
    attivita: tuple[Mapping[str, Any], ...]
    verifica: Mapping[str, Any]
    versioni: Mapping[str, str]
    impronta: str
    """Le prime sedici cifre dello sha256 delle regole lette: dice quali regole hanno
    fatto una distinta."""

    @property
    def lettere(self) -> tuple[str, ...]:
        return tuple(str(s["lettera"]) for s in self.distinta["sezioni"])

    def titolo(self, lettera: str) -> str:
        for sezione in self.distinta["sezioni"]:
            if sezione["lettera"] == lettera:
                return str(sezione["titolo"])
        raise KeyError(lettera)


def _leggi_i_file(percorso: Path) -> dict[str, Any]:
    if percorso.is_dir():
        letti: dict[str, Any] = {}
        for nome in FILE_DELLE_REGOLE:
            file = percorso / f"{nome}.json"
            if not file.is_file():
                raise ErroreDelleRegole(f"{percorso}: manca {nome}.json")
            try:
                letti[nome] = json.loads(file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as errore:
                raise ErroreDelleRegole(f"{file}: non e' JSON valido ({errore})") from errore
        return letti
    if percorso.is_file():
        try:
            fascio = json.loads(percorso.read_text(encoding="utf-8"))
        except json.JSONDecodeError as errore:
            raise ErroreDelleRegole(f"{percorso}: non e' JSON valido ({errore})") from errore
        file_del_fascio = fascio.get("file") if isinstance(fascio, dict) else None
        if not isinstance(file_del_fascio, dict):
            raise ErroreDelleRegole(f"{percorso}: non e' un fascio di regole (manca «file»)")
        letti = {}
        for nome in FILE_DELLE_REGOLE:
            if f"{nome}.json" not in file_del_fascio:
                raise ErroreDelleRegole(f"{percorso}: il fascio non ha {nome}.json")
            letti[nome] = file_del_fascio[f"{nome}.json"]
        return letti
    raise ErroreDelleRegole(f"{percorso}: le regole della distinta non ci sono")


def _ha_fonte_e_perche(voce: Mapping[str, Any], dove: str, difetti: list[str]) -> None:
    for chiave in ("fonte", "fonte_in_parole", "perche"):
        valore = voce.get(chiave)
        if not isinstance(valore, str) or not valore.strip():
            difetti.append(f"{dove}: manca «{chiave}»")


def _controlla_la_voce(
    voce: Mapping[str, Any],
    dove: str,
    lettere: set[str],
    calcoli: frozenset[str],
    difetti: list[str],
    scelte: frozenset[str] = frozenset(),
) -> None:
    _ha_fonte_e_perche(voce, dove, difetti)
    fornitura = voce.get("fornitura")
    if fornitura is not None and fornitura not in {FORNITURA_COMMITTENTE, FORNITURA_INSTALLATORE, *scelte}:
        difetti.append(f"{dove}: la fornitura {fornitura!r} non e' «committente» ne' una scelta di distinta.json")
    for chiave in ("id", "testo", "um", "sezione"):
        if not isinstance(voce.get(chiave), str) or not voce[chiave]:
            difetti.append(f"{dove}: manca «{chiave}»")
    if voce.get("sezione") not in lettere:
        difetti.append(f"{dove}: la sezione {voce.get('sezione')!r} non e' fra quelle di distinta.json")
    calcolo = voce.get("calcolo")
    if calcoli and (not isinstance(calcolo, dict) or calcolo.get("tipo") not in calcoli):
        tipo = calcolo.get("tipo") if isinstance(calcolo, dict) else calcolo
        difetti.append(f"{dove}: calcolo {tipo!r} sconosciuto (ammessi: {', '.join(sorted(calcoli))})")


def controlla(letti: Mapping[str, Any]) -> list[str]:
    """I difetti delle regole, uno per riga; nessuno se si caricano."""
    difetti: list[str] = []
    distinta = letti["distinta"]
    _ha_fonte_e_perche(distinta, "distinta.json", difetti)
    lettere = {str(s.get("lettera")) for s in distinta.get("sezioni", [])}
    for lettera in ("A", "G", "H", "V", "X"):
        if lettera not in lettere:
            difetti.append(f"distinta.json: manca la sezione {lettera}")
    fornitura = distinta.get("fornitura")
    scelte: set[str] = set()
    if not isinstance(fornitura, dict) or not isinstance(fornitura.get("scelte"), list):
        difetti.append("distinta.json: manca «fornitura» con le sue «scelte»")
    else:
        _ha_fonte_e_perche(fornitura, "distinta.json, fornitura", difetti)
        for scelta in fornitura["scelte"]:
            ident = scelta.get("id")
            dove = f"distinta.json, fornitura {ident}"
            ammesse = scelta.get("ammesse")
            testi = scelta.get("testi")
            if not isinstance(ident, str) or not isinstance(scelta.get("nome"), str):
                difetti.append(f"{dove}: manca «id» o «nome»")
                continue
            scelte.add(ident)
            if not isinstance(ammesse, list) or scelta.get("predefinita") not in ammesse:
                difetti.append(f"{dove}: la «predefinita» non e' fra le «ammesse»")
            elif not isinstance(testi, dict) or set(testi) != set(ammesse):
                difetti.append(f"{dove}: ogni valore ammesso vuole il suo testo in «testi»")
            dove_va = scelta.get("sezione_se_installatore")
            if dove_va is not None and dove_va not in lettere:
                difetti.append(f"{dove}: la sezione {dove_va!r} non e' fra quelle di distinta.json")
    fisse = frozenset(scelte)

    lunghezze = letti["lunghezze"]
    _ha_fonte_e_perche(lunghezze.get("regola", {}), "lunghezze.json, regola", difetti)
    for chiave in ("aggiunta_m", "fattore", "passo_m"):
        if not isinstance(lunghezze.get("regola", {}).get(chiave), int | float):
            difetti.append(f"lunghezze.json, regola: manca il numero «{chiave}»")
    for classe in lunghezze.get("classi", []):
        _ha_fonte_e_perche(classe, f"lunghezze.json, classe {classe.get('classe')}", difetti)
    for segue in lunghezze.get("segue", []):
        _ha_fonte_e_perche(segue, f"lunghezze.json, segue {segue.get('fluido')}", difetti)

    for fluido in letti["fluidi"].get("fluidi", []):
        nome = fluido.get("fluido")
        for chiave in ("fonte_attraversamenti", "fonte_attraversamenti_in_parole"):
            if not isinstance(fluido.get(chiave), str):
                difetti.append(f"fluidi.json, {nome}: manca «{chiave}»")
        for voce in fluido.get("voci", []):
            _controlla_la_voce(
                voce, f"fluidi.json, {nome}/{voce.get('id')}", lettere, CALCOLI_DEI_FLUIDI, difetti, fisse
            )

    for ident, voce_di_catalogo in letti["corredo"].get("voci", {}).items():
        _ha_fonte_e_perche(voce_di_catalogo, f"corredo.json, {ident}", difetti)
        if not isinstance(voce_di_catalogo.get("nome"), str):
            difetti.append(f"corredo.json, {ident}: manca «nome»")
        for voce in voce_di_catalogo.get("voci", []):
            _controlla_la_voce(
                voce, f"corredo.json, {ident}/{voce.get('id')}", lettere, CALCOLI_DEL_CORREDO, difetti, fisse
            )

    for voce in letti["attivita"].get("voci", []):
        dove = f"attivita.json, {voce.get('id')}"
        _controlla_la_voce(voce, dove, lettere, frozenset(), difetti, fisse)
        se = voce.get("se")
        if not isinstance(se, dict) or len(se) != 1 or not set(se) <= CONDIZIONI:
            difetti.append(f"{dove}: la condizione «se» vuole una chiave fra {', '.join(sorted(CONDIZIONI))}")

    verifica = letti["verifica"]
    for soglia in verifica.get("velocita", []):
        _ha_fonte_e_perche(soglia, f"verifica.json, velocita {soglia.get('fluido')}", difetti)
    for chiave in ("transito", "linea_frigorifera", "scritta"):
        _ha_fonte_e_perche(verifica.get(chiave, {}), f"verifica.json, {chiave}", difetti)
    return difetti


def carica_regole(percorso: Path) -> RegoleDellaDistinta:
    """Le regole da una cartella (`rules/distinta/`) o da un fascio in un file solo."""
    letti = _leggi_i_file(percorso)
    difetti = controlla(letti)
    if difetti:
        raise ErroreDelleRegole(f"{percorso}: le regole non si caricano:\n  - " + "\n  - ".join(difetti))
    impronta = hashlib.sha256(
        json.dumps([letti[n] for n in FILE_DELLE_REGOLE], ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()[:16]
    return RegoleDellaDistinta(
        distinta=letti["distinta"],
        lunghezze=letti["lunghezze"],
        fluidi={str(f["fluido"]): f for f in letti["fluidi"]["fluidi"]},
        corredo=dict(letti["corredo"]["voci"]),
        attivita=tuple(letti["attivita"]["voci"]),
        verifica=letti["verifica"],
        versioni={n: str(letti[n].get("versione", "?")) for n in FILE_DELLE_REGOLE},
        impronta=impronta,
    )


def regole_predefinite(cartella_delle_regole_degli_accessori: Path, cartella_dei_nomi: Path) -> Path | None:
    """Dove stanno le regole della distinta, se nessuno le indica.

    Nel repository accanto alle regole degli accessori (`rules/distinta/` accanto a
    `rules/hydronic/`); nella skill, quando la costruzione le portera', in un fascio
    accanto ai nomi (`dati/distinta.json`)."""
    for candidato in (
        cartella_delle_regole_degli_accessori.parent / "distinta",
        cartella_dei_nomi.parent / "distinta.json",
    ):
        if candidato.exists():
            return candidato
    return None
