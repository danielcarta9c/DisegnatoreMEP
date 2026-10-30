"""Il documento della distinta per l'installatore: che cosa dice, non come si stampa (REL-015, I-232).

Il PO: «Non foglio Excel meglio documento pdf con copertina e impaginazione generata con la
skill report di nove c (senza kpi di copertina e senza la sezione chi siamo).» Qui c'e' il
**contenuto** del documento — la copertina, i capitoli, le tabelle — come dati, gia'
scritto come testo; lo stampa `impaginazione` col motore dei report Nove C, oppure, se
quel motore non c'e', `documento_in_markdown` in un file Markdown con lo stesso contenuto.

I capitoli sono sette, sempre gli stessi e sempre nello stesso ordine:

1. l'impianto e le avvertenze — a corpo, fisso e invariabile; quantita' indicative;
   sopralluogo obbligatorio; la fornitura, da confermare o confermata; la distinta non
   progetta;
2. le tratte — sezioni, materiali, portate, L stimata e L da quotare —, e la verifica;
3. il computo, una tabella per sezione (A, B, C, D, E, F, X, Z);
4. le attivita' a corpo (G);
5. le varianti a prezzo unitario (V) e le voci che aggiunge l'installatore (H, righe vuote);
6. le voci da definire e le domande;
7. le note e le regole usate, in parole.

**Niente prezzi e niente dati interni**: i pezzi si dicono con le sigle dello schema, le
regole con `fonte_in_parole`; gli id delle regole restano nel JSON e nel foglio dei
calcoli. Dove il cartiglio non ha un dato, «DA DEFINIRE», come la tavola.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from .calcolo import DA_DEFINIRE, Distinta, Voce
from .uscite import data_del_cartiglio, dato_o_da_definire, numero_o_vuoto, tabelle_del_foglio

TITOLO_DEL_DOCUMENTO = "Distinta materiali per l'installatore"

CONTROLLO_DELLA_SCRITTA = "scritta sulla tavola"
"""Il controllo della verifica che confronta la scritta «Ø · L» della tavola con la
distinta (`calcolo._verifica`)."""


@dataclass(frozen=True)
class Tabella:
    """Una tabella: le intestazioni, le righe (testo gia' scritto), il peso di ogni
    colonna (la larghezza relativa) e le colonne allineate a destra. `titolo`, se c'e',
    e' il titoletto che le sta sopra e non se ne separa."""

    intestazioni: tuple[str, ...]
    righe: tuple[tuple[str, ...], ...]
    pesi: tuple[float, ...]
    a_destra: frozenset[int] = frozenset()
    titolo: str = ""

    def __post_init__(self) -> None:
        if len(self.pesi) != len(self.intestazioni):
            raise ValueError(f"{self.titolo or 'tabella'}: {len(self.pesi)} pesi per {len(self.intestazioni)} colonne")
        for riga in self.righe:
            if len(riga) != len(self.intestazioni):
                raise ValueError(f"{self.titolo or 'tabella'}: una riga di {len(riga)} celle su {len(self.intestazioni)}")


@dataclass(frozen=True)
class Chiavi:
    """Una tabella chiave/valore, senza intestazioni: i dati del cartiglio."""

    righe: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Paragrafo:
    """Un paragrafo. `nota`: in piccolo, come una didascalia."""

    testo: str
    nota: bool = False


@dataclass(frozen=True)
class Elenco:
    """Un elenco numerato."""

    voci: tuple[str, ...]
    titolo: str = ""


Blocco = Tabella | Chiavi | Paragrafo | Elenco


@dataclass(frozen=True)
class Capitolo:
    numero: int
    titolo: str
    blocchi: tuple[Blocco, ...]


@dataclass(frozen=True)
class Copertina:
    """I testi della copertina dei report Nove C, senza le card dei KPI (I-232)."""

    titolo: tuple[str, str, str]
    """Le tre righe del titolo: bianca, teal, bianca."""
    sottotitolo: str
    riquadro: tuple[str, str, str]
    """La testa del riquadro centrale e le sue due righe."""
    piede: str
    """A destra nella fascia in basso: commessa e data."""
    riserva: tuple[str, str] = ("", "")
    """La terza riga del titolo e il sottotitolo quando il titolo non ci sta accanto ai
    triangoli: la commessa nel titolo, il nome dell'impianto sotto."""


@dataclass(frozen=True)
class Documento:
    nome: str
    """Il nome del file, senza estensione: parlante dal cartiglio, o «distinta»."""
    titolo: str
    """Il titolo nei metadati del PDF."""
    intestazione: tuple[str, str]
    """Le due righe a destra nella testata delle pagine del corpo."""
    copertina: Copertina
    capitoli: tuple[Capitolo, ...]
    vietate: tuple[str, ...] = field(default=())
    """Le stringhe che nel documento non devono comparire: le passa a `qa_pdf`."""


VIETATE = ("€", "rules/", "lavoro/", ".py", "RAPPORTO", "REVISIONE", "kit AA-01", "corredo/", "fluidi/", "CAPEX", "markup")
"""Niente prezzi e niente dati interni (I-232): il controllo finale dei report le cerca
nel PDF. Le regole si dicono in parole; gli id restano nel JSON e nel foglio dei calcoli."""


def _vuoto(valore: object) -> bool:
    return not valore or str(valore).strip().upper() in ("ND", DA_DEFINIRE)


def nome_del_file(progetto: dict[str, object] | object) -> str:
    """Il nome parlante del documento, dal cartiglio: «AA-01_Distinta_materiali_
    Climatizzazione_canalizzata_Daikin». Senza commessa e senza titolo, «distinta»."""
    commessa = progetto.get("commission_code") if isinstance(progetto, dict) else None
    titolo = progetto.get("project_name") if isinstance(progetto, dict) else None
    parti: list[str] = []
    if not _vuoto(commessa):
        parti.append(re.sub(r"[^\w.-]+", "-", str(commessa).strip()).strip("-"))
    if not parti and _vuoto(titolo):
        return "distinta"
    parti.append("Distinta_materiali")
    if not _vuoto(titolo):
        parole = re.findall(r"\w+", str(titolo))
        scelte: list[str] = []
        for parola in parole:
            if len("_".join([*scelte, parola])) > 40:
                break
            scelte.append(parola)
        while scelte and len(scelte[-1]) <= 3 and scelte[-1].islower():
            scelte.pop()
        if scelte:
            parti.append("_".join(scelte))
    return "_".join(parti)


def _testo(testo: str) -> str:
    """Una cella per chi legge: senza gli accenti gravi del Markdown che le domande usano
    per i campi del grafo («manca `protezione` sul tratto»)."""
    return testo.replace("`", "")


def _quantita(voce: Voce) -> str:
    if voce.quantita is None:
        return "" if voce.sezione == "V" else DA_DEFINIRE
    return numero_o_vuoto(voce.quantita) or DA_DEFINIRE


def _computo(voci: Sequence[Voce], titolo: str) -> Tabella:
    return Tabella(
        intestazioni=("Rif.", "Voce", "UM", "Q.tà", "Fornitura", "Note"),
        righe=tuple((v.rif, _testo(v.testo), v.um, _quantita(v), v.fornitura, _testo(v.note)) for v in voci),
        pesi=(0.55, 4.6, 0.55, 0.6, 1.0, 2.1),
        a_destra=frozenset({3}),
        titolo=titolo,
    )


def _capitolo_1(distinta: Distinta) -> Capitolo:
    progetto = distinta.progetto
    regole = distinta.regole
    tavola = (
        f"{dato_o_da_definire(progetto, 'sheet_number')}, rev. {dato_o_da_definire(progetto, 'revision')} del "
        f"{data_del_cartiglio(progetto)}"
    )
    chiavi = Chiavi(
        righe=(
            ("Commessa", dato_o_da_definire(progetto, "commission_code")),
            ("Impianto", dato_o_da_definire(progetto, "project_name")),
            ("Committente", dato_o_da_definire(progetto, "client")),
            ("Indirizzo", dato_o_da_definire(progetto, "address")),
            ("Schema funzionale", f"tavola {tavola}"),
            ("Contenuto", f"{len(distinta.voci)} voci in {len({v.sezione for v in distinta.voci})} sezioni, "
                          f"{len(distinta.tratte_in_tabella)} tratte"),
        )
    )
    avvertenze = [str(a) for a in regole.distinta.get("intestazione", [])]
    if distinta.fornitura:
        avvertenze.insert(len(avvertenze) - 1 if avvertenze else 0, distinta.fornitura)
    return Capitolo(
        1,
        "L'impianto e le avvertenze",
        (
            chiavi,
            Paragrafo(
                "Questa distinta accompagna lo schema funzionale: è la base comune su cui gli installatori fanno "
                "il prezzo dell'impianto. Le sigle dei pezzi sono quelle dello schema."
            ),
            Elenco(tuple(avvertenze), titolo="Avvertenze per l'offerta"),
        ),
    )


def _capitolo_2(distinta: Distinta) -> Capitolo:
    foglio = tabelle_del_foglio(distinta, ("tratte",))["tabelle"][0]
    righe = tuple(tuple(riga) for riga in foglio["sezioni"][0]["righe"])
    tratte = Tabella(
        intestazioni=("Tratto", "Da - a", "Ø / sezione", "Materiale", "Q m³/h", "v m/s", "L stimata m", "L da quotare m"),
        righe=righe,
        pesi=(0.6, 2.0, 1.25, 2.0, 0.65, 0.6, 0.75, 0.8),
        a_destra=frozenset({4, 5, 6, 7}),
    )
    blocchi: list[Blocco] = [
        Paragrafo(
            "Ogni tratto con la sua sezione, il materiale e la lunghezza: la «L stimata» è quella del progettista, "
            "la «L da quotare» è quella maggiorata su cui si fa l'offerta. Un raccordo diretto (la ripresa sulla "
            "macchina, un cablaggio di fabbrica) non ha lunghezza."
        ),
        tratte,
    ]
    if distinta.note:
        blocchi.append(Paragrafo(distinta.note[0], nota=True))
    # La scritta sulla tavola che concorda con la distinta non dice niente all'installatore:
    # si mostra solo quando non concorda.
    verifica = [e for e in distinta.verifica if e.controllo != CONTROLLO_DELLA_SCRITTA or e.esito != "entro"]
    if verifica:
        blocchi.append(
            Tabella(
                intestazioni=("Dove", "Controllo", "Valore", "Soglia", "Esito"),
                righe=tuple((e.dove, e.controllo, _testo(e.valore), e.soglia, e.esito) for e in verifica),
                pesi=(0.9, 1.6, 3.2, 1.6, 1.0),
                titolo="La verifica dell'aria e delle linee — segnala, non corregge",
            )
        )
    return Capitolo(2, "Le tratte: sezioni e lunghezze", tuple(blocchi))


def _capitolo_3(distinta: Distinta) -> Capitolo:
    regole = distinta.regole
    lettere = [str(lettera) for lettera in regole.distinta.get("sezioni_sul_foglio", [])]
    blocchi: list[Blocco] = [
        Paragrafo(
            "Le quantità per sezione, indicative e già maggiorate. La colonna «Fornitura» dice chi fornisce la voce in "
            "questa offerta: le voci di Nove C e del Committente non si quotano, ma la posa sì dove la voce lo dice."
        )
    ]
    for lettera in lettere:
        voci = distinta.voci_della_sezione(lettera)
        if voci:
            blocchi.append(_computo(voci, f"{lettera}. {regole.titolo(lettera)}"))
    if len(blocchi) == 1:
        blocchi.append(Paragrafo("Nessuna voce."))
    return Capitolo(3, "Il computo per sezioni", tuple(blocchi))


def _capitolo_4(distinta: Distinta) -> Capitolo:
    voci = distinta.voci_della_sezione("G")
    blocchi: list[Blocco] = [
        Paragrafo(
            "Le attività che l'installatore quota a corpo, insieme alle voci del computo: manodopera, mezzi, prove e "
            "documenti per l'impianto finito."
        )
    ]
    if voci:
        blocchi.append(
            Tabella(
                intestazioni=("Rif.", "Attività", "Note"),
                righe=tuple((v.rif, _testo(v.testo), _testo(v.note)) for v in voci),
                pesi=(0.55, 6.9, 2.0),
                titolo=f"G. {distinta.regole.titolo('G')}",
            )
        )
    else:
        blocchi.append(Paragrafo("Nessuna attività."))
    return Capitolo(4, "Le attività a corpo", tuple(blocchi))


def _capitolo_5(distinta: Distinta) -> Capitolo:
    regole = distinta.regole
    varianti = distinta.voci_della_sezione("V")
    blocchi: list[Blocco] = [
        Paragrafo(
            "Le varianti si quotano a prezzo unitario, fuori dal prezzo a corpo: valgono solo se Nove C le ordina per "
            "iscritto. Nelle righe H l'installatore scrive quello che manca per l'impianto finito, dopo il sopralluogo."
        )
    ]
    if varianti:
        blocchi.append(
            Tabella(
                intestazioni=("Rif.", "Voce", "UM", "Note"),
                righe=tuple((v.rif, _testo(v.testo), v.um, _testo(v.note)) for v in varianti),
                pesi=(0.55, 6.0, 0.7, 2.2),
                titolo=f"V. {regole.titolo('V')}",
            )
        )
    righe_h = int(regole.distinta.get("righe_h", 6))
    blocchi.append(
        Tabella(
            intestazioni=("Rif.", "Voce", "UM", "Q.tà", "Note"),
            righe=tuple((f"H.{i}", "", "", "", "") for i in range(1, righe_h + 1)),
            pesi=(0.55, 5.4, 0.7, 0.7, 2.1),
            titolo=f"H. {regole.titolo('H')}",
        )
    )
    chiusura = str(regole.distinta.get("chiusura", "")).rstrip(":").strip()
    if chiusura:
        blocchi.append(Paragrafo(f"Con l'offerta l'installatore indica: {chiusura[:1].lower()}{chiusura[1:]}."))
    return Capitolo(5, "Le varianti e le voci dell'installatore", tuple(blocchi))


def _capitolo_6(distinta: Distinta) -> Capitolo:
    blocchi: list[Blocco] = []
    domande = [_testo(d) for d in distinta.domande]
    if domande:
        rif = ", ".join(v.rif for v in distinta.da_definire)
        blocchi.append(
            Paragrafo(
                f"Le voci DA DEFINIRE ({rif or 'nessuna'}) aspettano un dato del progettista: la distinta non lo "
                "inventa. Finché non c'è, la distinta non si manda agli installatori."
            )
        )
        blocchi.append(Elenco(tuple(domande), titolo="Le domande al progettista"))
    if distinta.da_confermare:
        blocchi.append(Elenco(tuple(_testo(c) for c in distinta.da_confermare), titolo="Da confermare per questa offerta"))
    oltre = [e for e in distinta.verifica if e.esito == "oltre"]
    if oltre:
        blocchi.append(
            Elenco(
                tuple(f"{e.dove}, {e.controllo}: {_testo(e.valore)}, contro {e.soglia}." for e in oltre),
                titolo="Le segnalazioni della verifica (la distinta non corregge)",
            )
        )
    detti = {f"{e.dove}, {e.controllo}: {e.valore}, contro {e.soglia}." for e in oltre}
    avvisi = [_testo(a) for a in distinta.avvisi if a not in detti]
    if avvisi:
        blocchi.append(Elenco(tuple(avvisi), titolo="Le assunzioni della distinta"))
    if not blocchi:
        blocchi.append(Paragrafo("Nessuna voce da definire, niente da confermare e nessuna domanda aperta."))
    return Capitolo(6, "Le voci da definire e le domande", tuple(blocchi))


def _capitolo_7(distinta: Distinta) -> Capitolo:
    per_fonte: dict[str, list[str]] = {}
    for voce in distinta.voci:
        for fonte in (f.strip() for f in voce.fonte.split(";")):
            if fonte:
                per_fonte.setdefault(fonte, [])
                if voce.rif not in per_fonte[fonte]:
                    per_fonte[fonte].append(voce.rif)
    blocchi: list[Blocco] = []
    if distinta.note:
        blocchi.append(Elenco(tuple(_testo(n) for n in distinta.note), titolo="Le note"))
    if per_fonte:
        blocchi.append(
            Tabella(
                intestazioni=("Da dove viene la quantità", "Voci"),
                righe=tuple((fonte[:1].upper() + fonte[1:], ", ".join(rif)) for fonte, rif in per_fonte.items()),
                pesi=(4.2, 5.8),
                titolo="Le regole usate",
            )
        )
    return Capitolo(7, "Le note e le regole usate", tuple(blocchi))


def documento_della_distinta(distinta: Distinta) -> Documento:
    """Il documento della distinta: la copertina e i sette capitoli, gia' scritti."""
    progetto = distinta.progetto
    commessa = dato_o_da_definire(progetto, "commission_code")
    impianto = dato_o_da_definire(progetto, "project_name")
    data = data_del_cartiglio(progetto)
    tavola = progetto.get("sheet_number")
    revisione = dato_o_da_definire(progetto, "revision")
    schema = "Schema funzionale" + ("" if _vuoto(tavola) else f" {tavola}, rev. {revisione}")
    copertina = Copertina(
        titolo=("Distinta materiali", "per l'installatore", impianto),
        sottotitolo=f"{schema}  ·  {data}",
        riquadro=(
            "DISTINTA MATERIALI PER L'INSTALLATORE",
            "A corpo, fisso e invariabile  ·  quantità indicative",
            "Sopralluogo obbligatorio prima dell'offerta",
        ),
        piede=f"Commessa {commessa} — {data}",
        riserva=(f"Commessa {commessa}", impianto),
    )
    return Documento(
        nome=nome_del_file(dict(progetto)),
        titolo=f"{TITOLO_DEL_DOCUMENTO} — {impianto}",
        intestazione=(f"noveC — Distinta materiali, commessa {commessa}", data),
        copertina=copertina,
        capitoli=(
            _capitolo_1(distinta),
            _capitolo_2(distinta),
            _capitolo_3(distinta),
            _capitolo_4(distinta),
            _capitolo_5(distinta),
            _capitolo_6(distinta),
            _capitolo_7(distinta),
        ),
        vietate=VIETATE,
    )


def tutti_i_testi(documento: Documento) -> list[str]:
    """Ogni testo del documento, nell'ordine: la copertina, la testata, i titoli, le
    celle. E' quello che legge l'installatore: ci si cercano i dati interni."""
    copertina = documento.copertina
    testi = [*copertina.titolo, copertina.sottotitolo, *copertina.riquadro, copertina.piede, *documento.intestazione]
    for capitolo in documento.capitoli:
        testi.append(capitolo.titolo)
        for blocco in capitolo.blocchi:
            if isinstance(blocco, Paragrafo):
                testi.append(blocco.testo)
            elif isinstance(blocco, Elenco):
                testi += [blocco.titolo, *blocco.voci]
            elif isinstance(blocco, Chiavi):
                testi += [t for riga in blocco.righe for t in riga]
            else:
                testi += [blocco.titolo, *blocco.intestazioni, *(c for riga in blocco.righe for c in riga)]
    return [t for t in testi if t]


# --- lo stesso contenuto in Markdown -------------------------------------------------


def _cella_md(testo: str) -> str:
    return testo.replace("|", "/").replace("\n", " ")


def _blocco_in_markdown(blocco: Blocco) -> list[str]:
    if isinstance(blocco, Paragrafo):
        return [f"*{blocco.testo}*" if blocco.nota else blocco.testo, ""]
    if isinstance(blocco, Elenco):
        righe = [f"### {blocco.titolo}", ""] if blocco.titolo else []
        return [*righe, *(f"{i}. {v}" for i, v in enumerate(blocco.voci, start=1)), ""]
    if isinstance(blocco, Chiavi):
        return ["| | |", "|---|---|", *(f"| **{_cella_md(k)}** | {_cella_md(v)} |" for k, v in blocco.righe), ""]
    righe = [f"### {blocco.titolo}", ""] if blocco.titolo else []
    allinea = ["---:" if i in blocco.a_destra else "---" for i in range(len(blocco.intestazioni))]
    righe += [
        "| " + " | ".join(_cella_md(i) for i in blocco.intestazioni) + " |",
        "|" + "|".join(allinea) + "|",
        *("| " + " | ".join(_cella_md(c) for c in riga) + " |" for riga in blocco.righe),
        "",
    ]
    return righe


def documento_in_markdown(documento: Documento) -> str:
    """Lo stesso contenuto del PDF, in Markdown: quando il motore dei report non c'e'."""
    copertina = documento.copertina
    righe = [
        f"# {copertina.titolo[0]} {copertina.titolo[1]}",
        "",
        f"**{copertina.sottotitolo}** — {copertina.piede}",
        "",
        f"> **{copertina.riquadro[0]}** — {copertina.riquadro[1]}  ·  {copertina.riquadro[2]}",
        "",
    ]
    for capitolo in documento.capitoli:
        righe += [f"## {capitolo.numero}. {capitolo.titolo}", ""]
        for blocco in capitolo.blocchi:
            righe += _blocco_in_markdown(blocco)
    return "\n".join(righe).rstrip("\n") + "\n"
