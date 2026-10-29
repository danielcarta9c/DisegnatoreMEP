"""Dal grafo completo alla distinta materiali (REL-013, proposta D-213).

La distinta **non progetta**: lunghezze, sezioni, portate, protezioni, marca e modello
sono dati del progettista, scritti nel grafo. La distinta li **maggiora** e ne
**conta il corredo** con le regole di `rules/distinta/`, e ogni quantita' esce con
la regola che l'ha prodotta, la sua fonte, il suo perche' e il conto fatto. Dove un
dato manca la voce esce **DA DEFINIRE**, con la domanda: mai un numero inventato.

L'ordine: le apparecchiature (A); per ogni fluido, le voci a metro e a giunzione sui
suoi tratti; per ogni pezzo, il suo corredo di posa; le voci di catalogo e i fluidi
senza regola (X, DA DEFINIRE); le attivita' a corpo, le opere del committente e le
varianti. Poi la verifica dell'aria, che **segnala e non corregge**.
"""

import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .confezioni import in_confezioni
from .grafo import Impianto, Pezzo, Tratta, leggi_impianto, numero, tratte_dell_impianto
from .lunghezze import Minimo, da_quotare, in_parole, per_eccesso, quante_volte
from .regole import Fornitura, RegoleDellaDistinta, la_fornitura

DA_DEFINIRE = "DA DEFINIRE"

SEGNAPOSTO = re.compile(r"\{([a-z_]+(?:\.[a-z0-9_-]+)?)\}")

CALCOLI_CON_LA_LUNGHEZZA = frozenset(
    {"lunghezza", "confezioni", "passo", "per_metro", "metri_arrotondati", "carica_refrigerante"}
)


@dataclass
class Voce:
    """Una riga della distinta."""

    sezione: str
    testo: str
    um: str
    quantita: float | None
    """`None`: DA DEFINIRE, o una variante che ha solo il prezzo unitario."""
    fornitura: str
    regola: str
    """Da quale regola viene: `fluidi/<fluido>/<voce>`, `corredo/<voce di catalogo>/<voce>`, …"""
    fonte: str
    perche: str
    calcolo: str
    note: str = ""
    da_definire: bool = False
    domande: list[str] = field(default_factory=list)
    rif: str = ""
    contributi: list[tuple[str, float]] = field(default_factory=list, repr=False)


@dataclass(frozen=True)
class EsitoDellaVerifica:
    dove: str
    controllo: str
    valore: str
    soglia: str
    esito: str
    """«entro», «oltre», «da rispettare», «non verificabile»."""
    fonte: str
    misura: float | None = None
    """Il numero misurato (la velocita' in m/s), quando c'e'."""


@dataclass
class Distinta:
    progetto: Mapping[str, Any]
    regole: RegoleDellaDistinta
    voci: list[Voce]
    tratte: list[Tratta]
    sigle: Mapping[str, str]
    nomi_dei_fluidi: Mapping[str, str]
    verifica: list[EsitoDellaVerifica]
    avvisi: list[str]
    note: list[str]
    domande_dei_tratti: list[str]
    da_confermare: list[str] = field(default_factory=list)
    """Le scelte che la distinta prende dalle regole predefinite e che il progettista
    conferma per questa offerta (la fornitura): non sono DA DEFINIRE — le quantita'
    ci sono —, ma non sono fatti."""

    def voci_della_sezione(self, lettera: str) -> list[Voce]:
        return [voce for voce in self.voci if voce.sezione == lettera]

    @property
    def domande(self) -> list[str]:
        tutte: list[str] = []
        for domanda in [*self.domande_dei_tratti, *(d for v in self.voci for d in v.domande)]:
            if domanda not in tutte:
                tutte.append(domanda)
        return tutte

    @property
    def da_definire(self) -> list[Voce]:
        return [voce for voce in self.voci if voce.da_definire]

    @property
    def tratte_in_tabella(self) -> list[Tratta]:
        return [tratta for tratta in self.tratte if tratta.num]

    def da_a(self, tratta: Tratta) -> str:
        return " - ".join(self.sigle.get(p, p) for p in tratta.pezzi)


def riempi(testo: str, valori: Mapping[str, Any]) -> tuple[str, list[str]]:
    """Il testo con i dati al posto dei segnaposto; quelli che mancano diventano
    «DA DEFINIRE (nome)», e tornano nell'elenco."""
    mancanti: list[str] = []

    def sostituisci(trovato: re.Match[str]) -> str:
        nome = trovato.group(1)
        valore = valori.get(nome)
        if valore is None or valore == "":
            mancanti.append(nome)
            return f"{DA_DEFINIRE} ({nome})"
        if isinstance(valore, float):
            return in_parole(valore)
        return str(valore)

    return SEGNAPOSTO.sub(sostituisci, testo), mancanti


def _unici(valori: Iterable[str | None]) -> list[str]:
    visti: list[str] = []
    for valore in valori:
        if valore and valore not in visti:
            visti.append(valore)
    return visti


def _nome_del_tratto(distinta_parziale: "_Lavoro", tratta: Tratta) -> str:
    chi = f"{tratta.num} " if tratta.num else ""
    return f"{chi}({tratta.rete.nome}: {distinta_parziale.da_a(tratta)})"


def _in_parole_le_tubazioni(impianto: Impianto, tratta: Tratta, idents: Sequence[str]) -> str:
    """Le tubazioni di un tratto dette coi loro capi, non coi loro id."""
    return ", ".join(impianto.tubazione_in_parole(t) for t in tratta.tubazioni if t.id in idents)


@dataclass
class _Lavoro:
    """Lo stato mentre la distinta si compone."""

    impianto: Impianto
    regole: RegoleDellaDistinta
    tratte: list[Tratta]
    nomi_del_catalogo: Mapping[str, str]
    nomi_dei_fluidi: Mapping[str, str]
    fornitura: Fornitura
    voci: list[Voce] = field(default_factory=list)
    avvisi: list[str] = field(default_factory=list)
    domande_dei_tratti: list[str] = field(default_factory=list)

    @property
    def sigle(self) -> dict[str, str]:
        return {ident: pezzo.sigla for ident, pezzo in self.impianto.pezzi.items()}

    def da_a(self, tratta: Tratta) -> str:
        sigle = self.sigle
        return " - ".join(sigle.get(p, p) for p in tratta.pezzi)

    def nome_della_voce(self, voce: str) -> str:
        corredo = self.regole.corredo.get(voce, {})
        return str(self.nomi_del_catalogo.get(voce) or corredo.get("nome") or voce)

    def nome_del_fluido(self, fluido: str) -> str:
        return str(self.nomi_dei_fluidi.get(fluido, fluido))

    @property
    def fornitura_installatore(self) -> str:
        return self.fornitura.installatore

    def sezione_e_fornitura(self, voce: Mapping[str, Any]) -> tuple[str, str]:
        """La sezione della voce e chi la fornisce: la `fornitura` della regola e' una
        scelta dell'offerta (`apparecchiature`, `bocchette_e_griglie`, …, in
        `distinta.json`), «committente», o niente (l'installatore). Una voce del
        Committente che l'offerta da' all'installatore passa nella sezione che la
        scelta dice, e si quota."""
        return self.fornitura.sezione_e_chi(str(voce["sezione"]), voce.get("fornitura"))


# --- le lunghezze --------------------------------------------------------------


def _ordina_e_numera(lavoro: _Lavoro) -> None:
    ordine = {fluido: indice for indice, fluido in enumerate(lavoro.regole.fluidi)}
    posizione = {id(tratta): indice for indice, tratta in enumerate(lavoro.tratte)}
    lavoro.tratte.sort(key=lambda t: (ordine.get(t.fluido, len(ordine)), posizione[id(t)]))
    numero_del_tratto = 0
    for tratta in lavoro.tratte:
        if not tratta.diretta or tratta.sezioni:
            numero_del_tratto += 1
            tratta.num = f"T{numero_del_tratto:02d}"


def _minimo_della_classe(regole: RegoleDellaDistinta, fluido: str) -> Minimo | None:
    for classe in regole.lunghezze.get("classi", []):
        if fluido in classe.get("fluidi", []) and float(classe.get("minimo_m", 0)) > 0:
            return Minimo(float(classe["minimo_m"]), f"minimo {classe['classe']}")
    return None


def _lunghezze(lavoro: _Lavoro) -> None:
    regola = lavoro.regole.lunghezze["regola"]
    segue = {str(s["fluido"]): s for s in lavoro.regole.lunghezze.get("segue", [])}

    def calcola(tratta: Tratta, altri: Sequence[Minimo]) -> None:
        if tratta.lunghezza_m is None:
            return
        minimi: list[Minimo] = []
        della_classe = _minimo_della_classe(lavoro.regole, tratta.fluido)
        if della_classe:
            minimi.append(della_classe)
        scritto = numero(tratta.dato("lunghezza_minima_m"))
        if scritto:
            minimi.append(Minimo(scritto, "minimo scritto sul tratto"))
        minimi.extend(altri)
        esito = da_quotare(tratta.lunghezza_m, regola, minimi)
        tratta.da_quotare_m = esito.da_quotare
        tratta.calcolo_della_lunghezza = esito.calcolo

    for tratta in lavoro.tratte:
        nome = _nome_del_tratto(lavoro, tratta)
        if tratta.illeggibili:
            lavoro.domande_dei_tratti.append(
                f"{nome}: la lunghezza di {_in_parole_le_tubazioni(lavoro.impianto, tratta, tratta.illeggibili)} "
                "non e' un numero."
            )
        if tratta.diretta:
            continue
        if tratta.lunghezza_m is None:
            lavoro.domande_dei_tratti.append(
                f"{nome}: quanto e' lungo? Serve `lunghezza_m` (la lunghezza stimata) su una sua tubazione, "
                "o 0 se e' un raccordo diretto."
            )
            continue
        if tratta.senza_lunghezza:
            lavoro.avvisi.append(
                f"{nome}: {_in_parole_le_tubazioni(lavoro.impianto, tratta, tratta.senza_lunghezza)} senza "
                "lunghezza; si considera compresa nei "
                f"{in_parole(tratta.lunghezza_m)} m dati sul tratto."
            )
        if tratta.fluido not in segue:
            calcola(tratta, ())
    for tratta in lavoro.tratte:
        if tratta.diretta or tratta.lunghezza_m is None or tratta.fluido not in segue:
            continue
        regola_segue = segue[tratta.fluido]
        seguiti = [
            altra
            for altra in lavoro.tratte
            if altra.fluido in regola_segue["fluidi_seguiti"]
            and set(altra.capi) == set(tratta.capi)
            and altra.da_quotare_m is not None
        ]
        altri = []
        if seguiti:
            lunga = max(seguiti, key=lambda t: t.da_quotare_m or 0)
            in_piu = float(regola_segue["in_piu_m"])
            altri.append(
                Minimo((lunga.da_quotare_m or 0) + in_piu, f"segue {lunga.num} + {in_parole(in_piu)} m:")
            )
        calcola(tratta, altri)


# --- le voci dei fluidi ----------------------------------------------------------


def _gruppi(tratte: Sequence[Tratta], raggruppa: str) -> list[list[Tratta]]:
    if raggruppa == "fluido":
        return [list(tratte)]
    gruppi: dict[str | None, list[Tratta]] = {}
    for tratta in tratte:
        gruppi.setdefault(tratta.sezione, []).append(tratta)
    return list(gruppi.values())


def _elenco(parti: Sequence[tuple[str, float]], unita: str = "") -> str:
    testo = " + ".join(f"{chi} {in_parole(q)}" for chi, q in parti)
    totale = sum(q for _, q in parti)
    return f"{testo} = {in_parole(totale)}{unita}" if len(parti) > 1 else f"{testo}{unita}"


def _pezzo_con(lavoro: _Lavoro, tratta: Tratta, dati: Sequence[str]) -> Pezzo | None:
    for capo in tratta.capi:
        pezzo = lavoro.impianto.pezzi.get(capo)
        if pezzo and any(pezzo.proprieta.get(d) not in (None, "") for d in dati):
            return pezzo
    return None


def _voce_del_fluido(
    lavoro: _Lavoro,
    fluido: str,
    regola_del_fluido: Mapping[str, Any],
    voce: Mapping[str, Any],
    gruppo: list[Tratta],
) -> list[Voce]:
    calcolo = voce["calcolo"]
    tipo = str(calcolo["tipo"])
    ident = f"fluidi/{fluido}/{voce['id']}"
    nomi = [t.num for t in gruppo]
    sezioni = [t.sezione for t in gruppo]
    valori: dict[str, Any] = {
        "sezione": ", ".join(_unici(sezioni)) if all(sezioni) else None,
        "materiale": ", ".join(
            _unici(str(t.dato("materiale") or regola_del_fluido.get("materiale") or "") for t in gruppo)
        )
        or None,
        "rete": ", ".join(_unici(t.rete.nome for t in gruppo)),
    }

    def una_voce(quantita: float | None, conto: str, note: str = "", extra: Mapping[str, Any] | None = None) -> Voce:
        testo, mancanti = riempi(str(voce["testo"]), {**valori, **(extra or {})})
        domande = []
        for mancante in mancanti:
            if mancante == "sezione":
                senza = [t.num for t in gruppo if not t.sezione]
                domande.append(
                    f"{', '.join(senza)} ({lavoro.nome_del_fluido(fluido)}): che sezione hanno? "
                    "Serve `sezione` sul tratto (es. «Ø200», «3G2,5»)."
                )
            else:
                domande.append(f"{', '.join(nomi)}: manca il dato «{mancante}» per «{testo}».")
        sezione, fornitura = lavoro.sezione_e_fornitura(voce)
        return Voce(
            sezione=sezione,
            testo=testo,
            um=str(voce["um"]),
            quantita=quantita,
            fornitura=fornitura,
            regola=ident,
            fonte=str(voce["fonte_in_parole"]),
            perche=str(voce["perche"]),
            calcolo=conto,
            note=note,
            da_definire=quantita is None or bool(mancanti),
            domande=domande,
        )

    senza_lunghezza = [t for t in gruppo if t.da_quotare_m is None]
    if tipo in CALCOLI_CON_LA_LUNGHEZZA and senza_lunghezza:
        quali = ", ".join(t.num for t in senza_lunghezza)
        if len(senza_lunghezza) == len(gruppo):
            return [una_voce(None, f"manca la lunghezza di {quali}", f"lunghezza di {quali} {DA_DEFINIRE}")]
        # Collaudo REL-012 t1, §2.4.1: una lunghezza che manca non cancella quelle date.
        # La parte nota si conta, e quella che manca e' una riga sua, DA DEFINIRE.
        noti = [t for t in gruppo if t.da_quotare_m is not None]
        mancante = _voce_del_fluido(lavoro, fluido, regola_del_fluido, voce, senza_lunghezza)
        for riga in mancante:
            riga.calcolo += f"; la parte nota ({', '.join(t.num for t in noti)}) e' nella riga sopra"
        return [*_voce_del_fluido(lavoro, fluido, regola_del_fluido, voce, noti), *mancante]
    lunghe = [(t.num, t.da_quotare_m or 0.0) for t in gruppo]
    totale = sum(q for _, q in lunghe)

    if tipo == "lunghezza":
        note = "; ".join(
            f"{t.num} stimati {in_parole(t.lunghezza_m or 0)} m" for t in gruppo
        )
        return [una_voce(totale, _elenco(lunghe, " m"), note)]
    if tipo == "confezioni":
        esito = in_confezioni(
            [q for _, q in lunghe], float(calcolo["confezione_m"]), float(calcolo["sfrido_m"]), float(calcolo["riserva"])
        )
        note = (
            f"{in_parole(totale)} m in {len(lunghe)} tratti interi: "
            + " + ".join(in_parole(q) for _, q in lunghe)
            + " m"
        )
        voci = [una_voce(float(esito.numero), esito.calcolo, note)]
        if esito.giunte:
            sezione, fornitura = lavoro.sezione_e_fornitura(voce)
            voci.append(
                Voce(
                    sezione=sezione,
                    testo=riempi("Manicotto di giunzione {sezione} per i tratti piu' lunghi di una confezione", valori)[0],
                    um="n",
                    quantita=float(esito.giunte),
                    fornitura=fornitura,
                    regola=ident,
                    fonte=str(voce["fonte_in_parole"]),
                    perche="Un tratto piu' lungo della parte utile di una confezione si giunta: una giunta, un manicotto.",
                    calcolo=f"{esito.giunte} giunte",
                )
            )
            lavoro.avvisi.append(
                f"{', '.join(nomi)}: un tratto e' piu' lungo di una confezione, {esito.giunte} giunte."
            )
        return voci
    if tipo == "per_tratta":
        n = float(calcolo["n"])
        tratti = "tratto" if len(gruppo) == 1 else "tratti"
        return [una_voce(n * len(gruppo), f"{len(gruppo)} {tratti} × {in_parole(n)} = {in_parole(n * len(gruppo))}")]
    if tipo == "passo":
        passo, in_piu = float(calcolo["passo_m"]), int(calcolo.get("in_piu", 0))
        parti = [(chi, float(max(0, quante_volte(q, passo) + in_piu))) for chi, q in lunghe]
        quantita = sum(q for _, q in parti)
        if not quantita:
            return []
        regola = f"(L / {in_parole(passo)} m per eccesso{f' {in_piu:+d}' if in_piu else ''} per tratto)"
        return [una_voce(quantita, f"{_elenco(parti)} {regola}")]
    if tipo == "per_metro":
        ogni, minimo = float(calcolo["ogni_m"]), int(calcolo.get("minimo", 0))
        quantita = float(max(minimo, quante_volte(totale, ogni)))
        return [una_voce(quantita, f"{in_parole(totale)} m / {in_parole(ogni)} m per eccesso, almeno {minimo} = {in_parole(quantita)}")]
    if tipo == "metri_arrotondati":
        fattore, passo = float(calcolo.get("fattore", 1.0)), float(calcolo["passo_m"])
        quantita = per_eccesso(totale * fattore, passo)
        return [
            una_voce(
                quantita,
                f"{_elenco(lunghe, ' m')} × {in_parole(fattore)}, per eccesso a {in_parole(passo)} m = {in_parole(quantita)} m",
            )
        ]
    if tipo == "fisso":
        n = float(calcolo["n"])
        return [una_voce(n, f"{in_parole(n)} per {'fluido' if calcolo.get('raggruppa') == 'fluido' else 'sezione'}")]
    if tipo == "attraversamenti":
        parti, assunti = [], []
        for tratta in gruppo:
            dato = numero(tratta.dato("attraversamenti"))
            if dato is None:
                dato = float(regola_del_fluido.get("attraversamenti_se_mancano", 0))
                if dato:
                    assunti.append(tratta.num)
            if dato:
                parti.append((tratta.num, dato))
        if not parti:
            return []
        note = (
            f"assunt{'o' if len(assunti) == 1 else 'i'} {in_parole(float(regola_del_fluido.get('attraversamenti_se_mancano', 0)))} "
            f"per {', '.join(assunti)} (attraversamenti non dati)"
            if assunti
            else ""
        )
        if assunti:
            lavoro.avvisi.append(
                f"{', '.join(assunti)} ({lavoro.nome_del_fluido(fluido)}): attraversamenti di parete non dati, "
                f"assunti {in_parole(float(regola_del_fluido.get('attraversamenti_se_mancano', 0)))} per tratto "
                f"({regola_del_fluido.get('fonte_attraversamenti_in_parole')})."
            )
        return [una_voce(sum(q for _, q in parti), _elenco(parti), note)]
    if tipo == "proprieta":
        nome = str(calcolo["proprieta"])
        per_valore: dict[str | None, list[Tratta]] = {}
        for tratta in gruppo:
            valore = tratta.dato(nome)
            per_valore.setdefault(str(valore) if valore not in (None, "") else None, []).append(tratta)
        voci = []
        for valore, tratte_del_valore in per_valore.items():
            rete = ", ".join(_unici(t.rete.nome for t in tratte_del_valore))
            voce_del_valore = una_voce(
                float(len(tratte_del_valore)),
                f"una per tratto: {', '.join(t.num for t in tratte_del_valore)}",
                extra={nome: valore, "rete": rete},
            )
            if valore is None:
                voce_del_valore.domande = [
                    f"{t.num} ({t.rete.nome}): manca `{nome}` sul tratto." for t in tratte_del_valore
                ]
            voci.append(voce_del_valore)
        return voci
    if tipo == "carica_refrigerante":
        minimo_kg = float(calcolo.get("minimo_kg", 0))
        dati = ("precarica_fino_a_m", "carica_aggiuntiva_g_m", "refrigerante")
        voci = []
        for tratta in gruppo:
            macchina = _pezzo_con(lavoro, tratta, dati)
            proprieta = macchina.proprieta if macchina else {}
            precarica = numero(proprieta.get("precarica_fino_a_m"))
            grammi = numero(proprieta.get("carica_aggiuntiva_g_m"))
            refrigerante = proprieta.get("refrigerante")
            if precarica is None or grammi is None:
                chi = macchina.sigla if macchina else " o ".join(lavoro.sigle.get(c, c) for c in tratta.capi)
                voce_mancante = una_voce(
                    None, "mancano i dati di macchina", extra={"refrigerante": refrigerante}
                )
                # Collaudo REL-012 t1, §2.4.3: si chiede solo quello che manca. Il
                # refrigerante dato (la voce lo scrive gia', «R32») non si richiede.
                mancano = [
                    f"`{d}`" for d in dati if proprieta.get(d) in (None, "") or (d != "refrigerante" and numero(proprieta.get(d)) is None)
                ]
                elenco = mancano[0] if len(mancano) == 1 else f"{', '.join(mancano[:-1])} e {mancano[-1]}"
                verbo = "serve" if len(mancano) == 1 else "servono"
                voce_mancante.domande.append(
                    f"{tratta.num}: su {chi} {verbo} {elenco} (dati di macchina del progettista) per la riserva "
                    "di refrigerante."
                )
                voci.append(voce_mancante)
                continue
            oltre = max(0.0, (tratta.da_quotare_m or 0) - precarica)
            grezza = oltre * grammi / 1000
            quantita = max(minimo_kg, per_eccesso(grezza, 0.05))
            voci.append(
                una_voce(
                    quantita,
                    f"{tratta.num}: ({in_parole(tratta.da_quotare_m or 0)} - {in_parole(precarica)} m) × "
                    f"{in_parole(grammi)} g/m = {in_parole(grezza, 3)} kg, almeno {in_parole(minimo_kg)} kg → "
                    f"{in_parole(quantita)} kg",
                    f"precarica fino a {in_parole(precarica)} m; oltre, {in_parole(grammi)} g/m",
                    extra={"refrigerante": refrigerante},
                )
            )
        return voci
    raise ValueError(f"{ident}: calcolo {tipo!r} sconosciuto")


def _voci_dei_fluidi(lavoro: _Lavoro) -> None:
    for fluido, regola_del_fluido in lavoro.regole.fluidi.items():
        tratte = [t for t in lavoro.tratte if t.fluido == fluido and not t.diretta]
        if not tratte:
            continue
        for voce in regola_del_fluido.get("voci", []):
            raggruppa = str(voce["calcolo"].get("raggruppa", "sezione"))
            for gruppo in _gruppi(tratte, raggruppa):
                lavoro.voci.extend(_voce_del_fluido(lavoro, fluido, regola_del_fluido, voce, gruppo))
    senza_regola: dict[str, list[Tratta]] = {}
    for tratta in lavoro.tratte:
        if tratta.fluido not in lavoro.regole.fluidi and not tratta.diretta:
            senza_regola.setdefault(tratta.fluido, []).append(tratta)
    for fluido, tratte in senza_regola.items():
        for gruppo in _gruppi(tratte, "sezione"):
            sezione = gruppo[0].sezione or f"{DA_DEFINIRE} (sezione)"
            noti = [t for t in gruppo if t.da_quotare_m is not None]
            ignoti = [t for t in gruppo if t.da_quotare_m is None]
            for parte, quantita in ((noti, sum(t.da_quotare_m or 0 for t in noti)), (ignoti, None)):
                if not parte:
                    continue
                lavoro.voci.append(
                    Voce(
                        sezione="X",
                        testo=f"Linea di {lavoro.nome_del_fluido(fluido)} {sezione}: materiale, corredo e accessori {DA_DEFINIRE}",
                        um="m",
                        quantita=quantita,
                        fornitura=DA_DEFINIRE,
                        regola=f"fluidi/{fluido} (manca)",
                        fonte="nessuna: la distinta non ha regole per questo fluido",
                        perche="Senza regola la distinta non inventa materiale e accessori: quota la lunghezza, se c'e', e chiede.",
                        calcolo=_elenco([(t.num, t.da_quotare_m or 0) for t in parte], " m")
                        if quantita is not None
                        else f"manca la lunghezza di {', '.join(t.num for t in parte)}",
                        note=", ".join(t.num for t in parte),
                        da_definire=True,
                        domande=[
                            f"Il fluido «{lavoro.nome_del_fluido(fluido)}» non ha regole di distinta: materiale, "
                            "corredo e accessori a metro sono da scrivere nelle regole della distinta (fluidi)."
                        ],
                    )
                )


# --- il corredo dei pezzi --------------------------------------------------------


def _sezione_al_pezzo(lavoro: _Lavoro, pezzo: str) -> str | None:
    for tratta in lavoro.tratte:
        if pezzo in tratta.pezzi and tratta.sezione:
            return tratta.sezione
    return None


@dataclass
class _Locale:
    """Un locale servito dalle bocchette: quello che conta per le griglie di transito."""

    nome: str
    pezzi: list[Pezzo]
    varco: bool
    """Il progettista ha dichiarato un varco aperto verso la ripresa: niente griglia."""
    dall_etichetta: bool
    """Il nome viene dall'etichetta della bocchetta, non dal dato `locale`."""


NON_E_UN_VARCO = frozenset({"", "no", "false", "0", "falso"})


def _ha_un_varco(pezzo: Pezzo) -> bool:
    valore = pezzo.proprieta.get("varco")
    if valore is None or valore is False:
        return False
    return str(valore).strip().casefold() not in NON_E_UN_VARCO


def _locale_della_bocchetta(pezzo: Pezzo) -> tuple[str, bool] | None:
    """Il locale che la bocchetta serve: il dato `locale`, o la sua etichetta senza le
    parentesi e senza la sua sigla in testa («B4 · Soggiorno-cucina» → «Soggiorno-cucina»,
    «Z3 Soggiorno (veletta)» → «Z3 Soggiorno»). `None` se non c'e' ne' l'uno ne' l'altra."""
    locale = pezzo.proprieta.get("locale")
    if isinstance(locale, str) and locale.strip():
        return " ".join(locale.split()), False
    etichetta = pezzo.proprieta.get("etichetta")
    if not isinstance(etichetta, str) or not etichetta.strip():
        return None
    testo = re.sub(r"\([^)]*\)", " ", etichetta)
    senza_sigla = re.sub(rf"^\s*{re.escape(pezzo.sigla)}\s*[·:\-–]\s*", "", testo)
    if senza_sigla.strip() and senza_sigla != testo:
        testo = senza_sigla
    testo = " ".join(testo.split()).strip(" ,;·-–")
    return (testo, True) if testo else None


def _locali_serviti(lavoro: _Lavoro, voce: str) -> tuple[list[_Locale], list[Pezzo]]:
    """I locali serviti dai pezzi di una voce di catalogo (le bocchette), nell'ordine del
    grafo: due bocchette dello stesso locale sono un locale (collaudo REL-012 t1, §2.4.2).
    Restituisce anche le bocchette di cui non si sa il locale."""
    locali: dict[str, _Locale] = {}
    senza: list[Pezzo] = []
    for pezzo in lavoro.impianto.pezzi.values():
        if pezzo.voce != voce:
            continue
        trovato = _locale_della_bocchetta(pezzo)
        if trovato is None:
            senza.append(pezzo)
            continue
        nome, dall_etichetta = trovato
        locale = locali.setdefault(nome.casefold(), _Locale(nome, [], False, dall_etichetta))
        locale.pezzi.append(pezzo)
        locale.varco = locale.varco or _ha_un_varco(pezzo)
    return list(locali.values()), senza


def _apparecchiature(lavoro: _Lavoro) -> None:
    compresi: dict[str, list[Pezzo]] = {}
    per_sigla = {p.sigla: p.id for p in lavoro.impianto.pezzi.values()}
    for pezzo in lavoro.impianto.pezzi.values():
        dentro = pezzo.proprieta.get("compreso_in")
        if dentro:
            bersaglio = str(dentro) if str(dentro) in lavoro.impianto.pezzi else per_sigla.get(str(dentro))
            if bersaglio is None:
                lavoro.avvisi.append(f"{pezzo.sigla}: «compreso_in» nomina {dentro}, che non c'e' nel grafo.")
            else:
                compresi.setdefault(bersaglio, []).append(pezzo)
    gruppi: dict[tuple[str, str, str], list[Pezzo]] = {}
    for pezzo in lavoro.impianto.pezzi.values():
        corredo = lavoro.regole.corredo.get(pezzo.voce)
        if not corredo or not corredo.get("apparecchiatura") or pezzo.proprieta.get("compreso_in"):
            continue
        chiave = (pezzo.voce, str(pezzo.proprieta.get("marca") or ""), str(pezzo.proprieta.get("modello") or ""))
        gruppi.setdefault(chiave, []).append(pezzo)
    for (voce, marca, modello), pezzi in gruppi.items():
        corredo = lavoro.regole.corredo[voce]
        nome = lavoro.nome_della_voce(voce)
        sigle = ", ".join(p.sigla for p in pezzi)
        note: list[str] = []
        primo = pezzi[0].proprieta
        if numero(primo.get("power_kw")) is not None:
            note.append(f"{in_parole(numero(primo.get('power_kw')) or 0)} kW")
        if numero(primo.get("flow_rate_m3h")) is not None:
            note.append(f"{in_parole(numero(primo.get('flow_rate_m3h')) or 0)} m³/h")
        for nota in _unici(str(p.proprieta.get("nota") or "") for p in pezzi):
            note.append(nota)
        for pezzo in pezzi:
            for compreso in compresi.get(pezzo.id, []):
                note.append(f"comprende {compreso.sigla} ({lavoro.nome_della_voce(compreso.voce)})")
        senza = not marca and not modello
        lavoro.voci.append(
            Voce(
                sezione="A",
                testo=f"{nome}: {f'{marca} {modello}'.strip()}" if not senza else f"{nome}: marca e modello {DA_DEFINIRE}",
                um="n",
                quantita=float(len(pezzi)),
                fornitura=lavoro.fornitura.valori["apparecchiature"],
                regola=f"corredo/{voce}/apparecchiatura",
                fonte=str(corredo["fonte_in_parole"]),
                perche=str(corredo["perche"]),
                calcolo=f"{len(pezzi)} nello schema ({sigle})",
                note="; ".join([sigle, *note]),
                da_definire=senza,
                domande=[f"{sigle} ({nome}): marca e modello li da' il progettista (D-190)."] if senza else [],
            )
        )


def _corredo(lavoro: _Lavoro) -> None:
    righe: dict[tuple[str, str, str, str], Voce] = {}
    per_locale: dict[int, tuple[list[_Locale], list[Pezzo]]] = {}
    """Le righe contate per locale, con i locali e le bocchette senza locale."""
    senza_corredo: dict[str, list[Pezzo]] = {}
    for pezzo in lavoro.impianto.pezzi.values():
        corredo = lavoro.regole.corredo.get(pezzo.voce)
        if corredo is None:
            senza_corredo.setdefault(pezzo.voce, []).append(pezzo)
            continue
        valori: dict[str, Any] = {k: v for k, v in pezzo.proprieta.items() if v not in (None, "")}
        valori["sigla"] = pezzo.sigla
        valori.setdefault("sezione", _sezione_al_pezzo(lavoro, pezzo.id))
        for voce in corredo.get("voci", []):
            calcolo = voce["calcolo"]
            n = float(calcolo["n"])
            chi = pezzo.sigla
            senza_locale = False
            if calcolo["tipo"] == "per_linea":
                linee = [
                    t for t in lavoro.tratte if t.fluido == calcolo["fluido"] and not t.diretta and pezzo.id in t.capi
                ]
                quantita = n * len(linee)
            elif calcolo["tipo"] == "per_locale":
                locali, _ = _locali_serviti(lavoro, pezzo.voce)
                suo = next((locale for locale in locali if pezzo in locale.pezzi), None)
                if suo is None:
                    quantita, senza_locale = n, True
                elif suo.pezzi[0] is pezzo and not suo.varco:
                    quantita, chi = n, suo.nome
                else:
                    quantita = 0.0
            else:
                quantita = n
            if not quantita:
                continue
            testo, mancanti = riempi(str(voce["testo"]), valori)
            sezione, fornitura = lavoro.sezione_e_fornitura(voce)
            chiave = (sezione, testo, str(voce["um"]), fornitura)
            riga = righe.get(chiave)
            if riga is None:
                riga = Voce(
                    sezione=chiave[0],
                    testo=testo,
                    um=chiave[2],
                    quantita=0.0,
                    fornitura=chiave[3],
                    regola=f"corredo/{pezzo.voce}/{voce['id']}",
                    fonte=str(voce["fonte_in_parole"]),
                    perche=str(voce["perche"]),
                    calcolo="",
                    da_definire=bool(mancanti),
                )
                righe[chiave] = riga
                lavoro.voci.append(riga)
            elif f"corredo/{pezzo.voce}/{voce['id']}" not in riga.regola.split(" + "):
                riga.regola += f" + corredo/{pezzo.voce}/{voce['id']}"
                if str(voce["fonte_in_parole"]) not in riga.fonte:
                    riga.fonte += f"; {voce['fonte_in_parole']}"
            if calcolo["tipo"] == "per_locale":
                per_locale[id(riga)] = _locali_serviti(lavoro, pezzo.voce)
            riga.quantita = (riga.quantita or 0) + quantita
            riga.contributi.append((chi, quantita))
            for mancante in mancanti:
                domanda = f"{pezzo.sigla} ({lavoro.nome_della_voce(pezzo.voce)}): manca il dato «{mancante}» per «{testo}»."
                riga.domande.append(domanda)
            if senza_locale:
                riga.da_definire = True
                riga.domande.append(
                    f"{pezzo.sigla} ({lavoro.nome_della_voce(pezzo.voce)}): che locale serve? Serve `locale` sulla "
                    "bocchetta (o un'etichetta col nome del locale): le griglie di transito si contano per locale, "
                    "e intanto questa bocchetta ne conta una sua."
                )
    for riga in righe.values():
        if id(riga) in per_locale:
            locali, senza = per_locale[id(riga)]
            contati = [locale for locale in locali if not locale.varco]
            parti_del_conto = [f"{len(contati)} locali serviti ({', '.join(locale.nome for locale in contati)})"]
            if senza:
                parti_del_conto.append(
                    f"{len(senza)} bocchette senza locale, una ciascuna ({', '.join(p.sigla for p in senza)})"
                )
            con_varco = [locale.nome for locale in locali if locale.varco]
            if con_varco:
                parti_del_conto.append(f"nessuna dove il locale ha un varco: {', '.join(con_varco)}")
            if any(locale.dall_etichetta for locale in locali):
                parti_del_conto.append("il locale e' letto dall'etichetta della bocchetta")
            riga.calcolo = f"{in_parole(riga.quantita or 0)}: " + "; ".join(parti_del_conto)
            riga.note = ", ".join(s for s, _ in riga.contributi)
            continue
        parti = riga.contributi
        distinte = {q for _, q in parti}
        sigle = ", ".join(s for s, _ in parti)
        if len(distinte) == 1 and len(parti) > 1:
            q = next(iter(distinte))
            riga.calcolo = f"{len(parti)} pezzi × {in_parole(q)} = {in_parole(riga.quantita or 0)} ({sigle})"
            riga.note = sigle
        elif len(parti) == 1:
            riga.calcolo = f"{parti[0][0]}: {in_parole(parti[0][1])}"
            riga.note = parti[0][0]
        else:
            riga.calcolo = _elenco(parti)
            riga.note = ", ".join(f"{s} {in_parole(q)}" for s, q in parti)
    for voce, pezzi in senza_corredo.items():
        nome = lavoro.nome_della_voce(voce)
        sigle = ", ".join(p.sigla for p in pezzi)
        lavoro.voci.append(
            Voce(
                sezione="X",
                testo=f"{nome}: fornitura e corredo di posa {DA_DEFINIRE}",
                um="n",
                quantita=float(len(pezzi)),
                fornitura=DA_DEFINIRE,
                regola=f"corredo/{voce} (manca)",
                fonte="nessuna: la distinta non ha il corredo di questo pezzo",
                perche="Senza regola la distinta non inventa il corredo: conta i pezzi del grafo e chiede.",
                calcolo=f"{len(pezzi)} nello schema ({sigle})",
                note=sigle,
                da_definire=True,
                domande=[
                    f"«{nome}» ({sigle}) non ha corredo di posa nelle regole della distinta: chi lo fornisce e che "
                    "cosa porta con se'? Si scrive nelle regole della distinta (corredo)."
                ],
            )
        )


# --- attivita', opere e varianti -------------------------------------------------


def _attivita(lavoro: _Lavoro) -> None:
    fluidi_presenti = {t.fluido for t in lavoro.tratte}
    valori: dict[str, Any] = {f"fornitura.{s}": lavoro.fornitura.testo(s) for s in lavoro.fornitura.scelte}
    for pezzo in lavoro.impianto.pezzi.values():
        valori[f"conta.{pezzo.voce}"] = str(lavoro.impianto.conta(pezzo.voce))
    for fluido in fluidi_presenti:
        valori[f"tratte.{fluido}"] = str(sum(1 for t in lavoro.tratte if t.fluido == fluido and not t.diretta))
    for voce in lavoro.regole.attivita:
        se = voce["se"]
        if "voci" in se:
            presenti = [v for v in se["voci"] if lavoro.impianto.conta(v)]
            vera = bool(presenti)
            perche_vera = f"nell'impianto: {', '.join(lavoro.nome_della_voce(v) for v in presenti)}"
        elif "fluidi" in se:
            presenti = [f for f in se["fluidi"] if f in fluidi_presenti]
            vera = bool(presenti)
            perche_vera = f"nell'impianto: {', '.join(lavoro.nome_del_fluido(f) for f in presenti)}"
        else:
            vera, perche_vera = bool(se["sempre"]), "sempre"
        if not vera:
            continue
        testo, mancanti = riempi(str(voce["testo"]), valori)
        variante = voce["sezione"] == "V"
        sezione, fornitura = lavoro.sezione_e_fornitura(voce)
        lavoro.voci.append(
            Voce(
                sezione=sezione,
                testo=testo,
                um=str(voce["um"]),
                quantita=None if variante else 1.0,
                fornitura=fornitura,
                regola=f"attivita/{voce['id']}",
                fonte=str(voce["fonte_in_parole"]),
                perche=str(voce["perche"]),
                calcolo=perche_vera + ("; solo prezzo unitario" if variante else ""),
                da_definire=bool(mancanti),
                domande=[f"manca il dato «{m}» per «{testo}»" for m in mancanti],
            )
        )


# --- la verifica -----------------------------------------------------------------


def area_della_sezione(sezione: str | None) -> float | None:
    """L'area lorda in m² di «Ø200» (diametro in mm) o «1000×250» (lati in mm)."""
    if not sezione:
        return None
    rettangolo = re.search(r"(\d+(?:[.,]\d+)?)\s*[×xX]\s*(\d+(?:[.,]\d+)?)", sezione)
    if rettangolo:
        a, b = (float(g.replace(",", ".")) / 1000 for g in rettangolo.groups())
        return a * b
    tondo = re.search(r"Ø\s*(\d+(?:[.,]\d+)?)", sezione)
    if tondo:
        d = float(tondo.group(1).replace(",", ".")) / 1000
        return math.pi * d * d / 4
    return None


def _verifica(lavoro: _Lavoro) -> tuple[list[EsitoDellaVerifica], dict[str, str]]:
    regole = lavoro.regole.verifica
    esiti: list[EsitoDellaVerifica] = []
    soglie = {str(s["fluido"]): s for s in regole.get("velocita", [])}
    for tratta in lavoro.tratte:
        soglia = soglie.get(tratta.fluido)
        if soglia is None or not tratta.num:
            continue
        portata = numero(tratta.dato("portata_m3h"))
        area = area_della_sezione(tratta.sezione)
        massima = float(soglia["massima_m_s"])
        if portata is None or area is None:
            manca = "la portata (`portata_m3h`)" if portata is None else "una sezione che si legge (Ø o lati)"
            esiti.append(
                EsitoDellaVerifica(tratta.num, "velocità", f"manca {manca}", f"≤ {in_parole(massima)} m/s", "non verificabile", str(soglia["fonte_in_parole"]))
            )
            continue
        velocita = portata / 3600 / area
        esiti.append(
            EsitoDellaVerifica(
                tratta.num,
                "velocità",
                f"{in_parole(portata)} m³/h su {tratta.sezione}: {in_parole(velocita)} m/s",
                f"≤ {in_parole(massima)} m/s",
                "entro" if velocita <= massima + 1e-9 else "oltre",
                str(soglia["fonte_in_parole"]),
                misura=velocita,
            )
        )
    aree_di_transito: dict[str, str] = {}
    transito = regole.get("transito", {})
    if transito.get("velocita_m_s"):
        v_transito = float(transito["velocita_m_s"])

        def portata_della_bocchetta(pezzo: Pezzo) -> float | None:
            tratte = [t for t in lavoro.tratte if pezzo.id in t.capi and numero(t.dato("portata_m3h")) is not None]
            return numero(tratte[0].dato("portata_m3h")) if tratte else None

        # Per locale servito, con la portata di tutte le sue bocchette (§2.4.2); una
        # bocchetta di cui non si sa il locale fa locale da se'.
        locali, senza = _locali_serviti(lavoro, "air-supply-terminal")
        gruppi = [(locale.nome, locale.pezzi, locale.varco) for locale in locali]
        gruppi += [(pezzo.sigla, [pezzo], False) for pezzo in senza]
        for nome, pezzi, varco in gruppi:
            portate = [q for q in (portata_della_bocchetta(p) for p in pezzi) if q is not None]
            if not portate:
                continue
            portata = sum(portate)
            area = math.ceil(portata / 3600 / v_transito * 1000 - 1e-9) / 1000
            aree_di_transito[nome] = f"{in_parole(area, 3)} m²"
            esiti.append(
                EsitoDellaVerifica(
                    nome,
                    "varco verso la ripresa" if varco else "griglia di transito",
                    f"{in_parole(portata)} m³/h a {in_parole(v_transito)} m/s",
                    f"Aeff ≥ {in_parole(area, 3)} m²",
                    "da rispettare",
                    str(transito["fonte_in_parole"]),
                )
            )
    for tratta in lavoro.tratte:
        if not tratta.fluido.startswith("refrigerant") or tratta.da_quotare_m is None:
            continue
        macchina = _pezzo_con(lavoro, tratta, ("lunghezza_max_m",))
        massima_m = numero(macchina.proprieta.get("lunghezza_max_m")) if macchina else None
        if macchina is None or massima_m is None:
            continue
        esiti.append(
            EsitoDellaVerifica(
                tratta.num,
                "lunghezza della linea frigorifera",
                f"{in_parole(tratta.da_quotare_m)} m da quotare",
                f"≤ {in_parole(massima_m)} m ({macchina.sigla})",
                "entro" if tratta.da_quotare_m <= massima_m else "oltre",
                str(regole["linea_frigorifera"]["fonte_in_parole"]),
            )
        )
    for tratta in lavoro.tratte:
        scritta = tratta.dato("scritta")
        trovata = re.search(r"L\s*(\d+(?:[.,]\d+)?)\s*m\b", str(scritta or ""))
        if not trovata or tratta.da_quotare_m is None:
            continue
        sulla_tavola = float(trovata.group(1).replace(",", "."))
        uguale = abs(sulla_tavola - tratta.da_quotare_m) < 0.01
        esiti.append(
            EsitoDellaVerifica(
                tratta.num,
                "scritta sulla tavola",
                f"«{scritta}»",
                f"L {in_parole(tratta.da_quotare_m)} m da quotare",
                "entro" if uguale else "oltre",
                str(regole["scritta"]["fonte_in_parole"]),
            )
        )
    for esito in esiti:
        if esito.esito == "oltre":
            lavoro.avvisi.append(f"{esito.dove}, {esito.controllo}: {esito.valore}, contro {esito.soglia}.")
    return esiti, aree_di_transito


# --- le note ---------------------------------------------------------------------


def _note(lavoro: _Lavoro, esiti: Sequence[EsitoDellaVerifica]) -> list[str]:
    regola = lavoro.regole.lunghezze["regola"]
    minimi = [
        f"{', '.join(lavoro.nome_del_fluido(f) for f in c['fluidi'])} {in_parole(float(c['minimo_m']))} m"
        for c in lavoro.regole.lunghezze.get("classi", [])
        if float(c.get("minimo_m", 0)) > 0
    ]
    note = [
        f"«L da quotare» = (L stimata + {in_parole(float(regola['aggiunta_m']))} m) × {in_parole(float(regola['fattore']))}, "
        f"per eccesso a {in_parole(float(regola['passo_m']))} m; minimi: {'; '.join(minimi)}. La L stimata è un dato "
        "del progettista, scritta su ogni tratto.",
        "Quantità indicative per un prezzo a corpo, fisso e invariabile: l'installatore le verifica nel sopralluogo "
        "obbligatorio prima dell'offerta; le varianti hanno solo il prezzo unitario.",
    ]
    for fluido in lavoro.regole.fluidi:
        velocita = [
            e.misura
            for e in esiti
            if e.misura is not None and any(t.num == e.dove and t.fluido == fluido for t in lavoro.tratte)
        ]
        if velocita:
            campo = (
                f"da {in_parole(min(velocita), 1)} a {in_parole(max(velocita), 1)}"
                if min(velocita) != max(velocita)
                else in_parole(velocita[0], 1)
            )
            note.append(
                f"Velocità nei tratti di {lavoro.nome_del_fluido(fluido)} {campo} m/s, sulla sezione lorda, dalle "
                "portate e dalle sezioni del progettista (verifica: segnala, non corregge)."
            )
    note.append(lavoro.fornitura.nota())
    note.append(
        "La distinta non progetta: lunghezze, sezioni, portate, protezioni, marca e modello sono dati del "
        "progettista; la distinta li maggiora e ne conta il corredo con regole scritte, ciascuna con la sua fonte "
        f"(regole {lavoro.regole.impronta})."
    )
    return note


# --- tutto insieme ---------------------------------------------------------------


NON_DATO = "ND"
"""Come «Capire» scrive un dato del cartiglio che il progettista non ha dato: per la
distinta, come per il cartiglio della tavola, e' un dato che manca."""

CAMPI_DEL_PROGETTO = (
    "client",
    "address",
    "project_name",
    "commission_code",
    "revision",
    "issue_date",
    "sheet_number",
    "sheet_title",
)


def _dato_del_cartiglio(valore: object) -> str | None:
    """Il valore come lo legge il cartiglio della tavola: vuoto o «ND» non e' un dato."""
    if valore is None or isinstance(valore, bool):
        return None
    testo = str(valore).strip()
    return None if not testo or testo.upper() == NON_DATO else testo


def _progetto(grafo: Mapping[str, Any], metadati: Mapping[str, Any]) -> dict[str, str]:
    progetto = {c: v for c in CAMPI_DEL_PROGETTO if (v := _dato_del_cartiglio(metadati.get(c))) is not None}
    if "sheet_number" not in progetto:
        numeri = [
            n
            for tavola in grafo.get("sheets") or []
            if isinstance(tavola, Mapping) and (n := _dato_del_cartiglio(tavola.get("number"))) is not None
        ]
        if numeri:
            progetto["sheet_number"] = ", ".join(numeri)
    return progetto


def componi_la_distinta(
    grafo: Mapping[str, Any],
    regole: RegoleDellaDistinta,
    nomi_del_catalogo: Mapping[str, str] | None = None,
    nomi_dei_fluidi: Mapping[str, str] | None = None,
    sigle: Mapping[str, str] | None = None,
    fornitura: Fornitura | None = None,
) -> Distinta:
    """La distinta del grafo completo. `nomi_del_catalogo` e `nomi_dei_fluidi` danno i
    nomi in parole; senza, valgono quelli del corredo e gli id dei fluidi. `sigle` sono
    quelle dello schema (`grafo.sigle_dello_schema`): senza, valgono quelle scritte
    dall'ingegnere e poi le etichette. `fornitura` e' la scelta dell'offerta: senza,
    le predefinite delle regole, dichiarate da confermare."""
    impianto = leggi_impianto(grafo, sigle, nomi_del_catalogo, nomi_dei_fluidi)
    passanti = [voce for voce, corredo in regole.corredo.items() if corredo.get("passante")]
    lavoro = _Lavoro(
        impianto=impianto,
        regole=regole,
        tratte=tratte_dell_impianto(impianto, passanti),
        nomi_del_catalogo=nomi_del_catalogo or {},
        nomi_dei_fluidi=nomi_dei_fluidi or {},
        fornitura=fornitura or la_fornitura(regole),
    )
    if impianto.esclusi:
        lavoro.avvisi.append(f"Esistenti, fuori dalla distinta: {', '.join(impianto.esclusi)}.")
    _ordina_e_numera(lavoro)
    _lunghezze(lavoro)
    _apparecchiature(lavoro)
    _voci_dei_fluidi(lavoro)
    _corredo(lavoro)
    _attivita(lavoro)
    esiti, aree_di_transito = _verifica(lavoro)
    for voce in lavoro.voci:
        if voce.regola.endswith("/griglia-di-transito") and aree_di_transito:
            locali = [chi for chi, _ in voce.contributi]
            voce.note = "Aeff min.: " + ", ".join(
                f"{s} {aree_di_transito[s]}" for s in locali if s in aree_di_transito
            )
    ordine = {lettera: indice for indice, lettera in enumerate(regole.lettere)}
    posizione = {id(voce): indice for indice, voce in enumerate(lavoro.voci)}
    lavoro.voci.sort(key=lambda v: (ordine.get(v.sezione, len(ordine)), posizione[id(v)]))
    contatori: dict[str, int] = {}
    for voce in lavoro.voci:
        contatori[voce.sezione] = contatori.get(voce.sezione, 0) + 1
        voce.rif = f"{voce.sezione}.{contatori[voce.sezione]}"
    progetto = _progetto(grafo, impianto.metadati)
    return Distinta(
        progetto=progetto,
        regole=regole,
        voci=lavoro.voci,
        tratte=lavoro.tratte,
        sigle=lavoro.sigle,
        nomi_dei_fluidi=dict(nomi_dei_fluidi or {}),
        verifica=esiti,
        avvisi=lavoro.avvisi,
        note=_note(lavoro, esiti),
        domande_dei_tratti=lavoro.domande_dei_tratti,
        da_confermare=[] if lavoro.fornitura.confermata else [lavoro.fornitura.in_parole()],
    )

