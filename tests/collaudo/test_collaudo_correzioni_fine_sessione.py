"""Collaudo indipendente delle due correzioni di fine sessione del 7 agosto 2026.

Scritto a contesto separato da chi non ha scritto ne' il codice ne' la
documentazione che giudica. I criteri sono stati fissati **prima** di leggere
l'implementazione, e sono piu' duri di quelli che l'implementatore si e' dato.

**Correzione 1 — la camminata del ritorno generale che si apre sui rami.**
Il corredo di rete (vaso, riempimento, manometro, defangatore) sta sul ritorno
generale, a monte della prima ripartizione, e il punto si trova camminando
sulla struttura del grafo. La correzione afferma che la camminata ora si apre
sui rami e che nessuno dei cinque impianti ha piu' punti aperti sul tratto
comune.

**Correzione 2 — il regime ricavato dalle potenze dichiarate (D-108).**
Il regime si **legge** sommando le potenze che il progettista ha scritto nel
testo; non si chiede. Senza potenze resta non dichiarato, vale il corredo
minimo, e la mancanza si dice.

**Come si legge questo file.** Le prove marcate `xfail(strict=True)` sono
difetti trovati dal collaudo: falliscono apposta e sono li' per non farli
perdere. Il giorno in cui il difetto e' chiuso il segno va tolto, e la prova
resta come regressione.

Il collaudo e' stato fatto con HEAD a `82b8374`. Le sei prove rosse della
suite completa riguardano un artefatto pubblicato non ancora rigenerato (il
documento del quinto impianto) e non hanno niente a che vedere con queste due
correzioni.
"""

import re
from pathlib import Path

import pytest
from helpers import catalog, comp, load, net, permuted, pipe, project
from helpers import rules as load_rules

from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.context import RuleContext
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.proposal import GapReason

ROOT = Path(__file__).resolve().parents[2]
CAT = catalog()
REG = load_rules()

PROVE = [
    "prova-1-due-pdc-accumulo-combinato.json",
    "prova-2-pdc-deviatrice-acs.json",
    "prova-3-pdc-diretta-pavimento.json",
    "prova-4-ibrido-pdc-caldaia.json",
    "prova-5-cascata-tre-pdc.json",
]

KIT = {
    "expansion-on-closed-circuit",
    "filling-unit-on-return",
    "gauge-where-the-plant-is-charged",
    "dirt-separation-before-what-it-would-ruin",
}

TESTO = ROOT / "examples" / "prova" / "input" / "2026-08-06-impianti-di-prova.txt"
ISTRUZIONI = ROOT / "skill" / "capire" / "ISTRUZIONI.md"
CONFRONTO = ROOT / "docs" / "prodotto" / "grafi-di-prova" / "CONFRONTO-2026-08-07.md"


# ---------------------------------------------------------------------------
# Attrezzi del collaudo — scritti qui, non presi in prestito dalle prove
# esistenti: una prova che riusa gli occhiali di chi ha sbagliato non vede.
# ---------------------------------------------------------------------------


def kit_posato(model: ProjectModel) -> dict[str, tuple[str, str, str]]:
    """Dove ciascuna delle quattro regole del corredo si posa: rete e attacco."""
    found = evaluate(model, CAT, REG)
    return {
        p.rule_id: (p.network_id, p.anchor.component_id, p.anchor.port_id)
        for p in found.proposals
        if p.rule_id in KIT
    }


def kit_aperto(model: ProjectModel) -> dict[str, str]:
    """I punti aperti delle quattro regole del corredo, con la ragione."""
    found = evaluate(model, CAT, REG)
    return {g.rule_id: g.reason.value for g in found.gaps if g.rule_id in KIT}


def generatori(model: ProjectModel) -> list[str]:
    return [
        c.id
        for c in model.components
        if "heat_generation" in CAT.get(c.definition_id).functions
    ]


def tratto_di(model: ProjectModel, component_id: str, port_id: str) -> str | None:
    return RuleContext.build(model, CAT).connection_of_port.get((component_id, port_id))


def generatori_che_si_chiudono_senza(
    model: ProjectModel, network_id: str, tratto: str | None
) -> list[str]:
    """I generatori il cui circuito **si chiude ancora** senza quel tratto.

    E' la definizione operativa di «ritorno generale»: se togliendo quel tratto
    un generatore continua a mandare e a ricevere acqua, quel tratto non porta
    la sua acqua, e il corredo posato li' non lo serve. Il grafo si percorre
    attraversando anche le macchine, perche' l'acqua ci passa dentro: fermarsi
    sulle macchine e' comodo per camminare, non e' vero per l'acqua.

    Il defangatore ha questa proprieta' scritta nella propria motivazione —
    «li' passa tutta l'acqua che torna, quindi un pezzo solo protegge ogni
    generatore» — quindi non e' un criterio inventato dal collaudo.
    """
    ctx = RuleContext.build(model, CAT)
    tubi = [
        p
        for p, n in ctx.network_of_connection.items()
        if n == network_id and p in ctx.pipe_ends
    ]
    avanti: dict[str, list[str]] = {p: [] for p in tubi}
    for p in tubi:
        _, entra = ctx.pipe_ends[p]
        avanti[p] = [q for q in ctx.outgoing.get(entra.component_id, ()) if q in avanti]
    colpevoli = []
    for gen in generatori(model):
        partenze = [p for p in tubi if ctx.pipe_ends[p][0].component_id == gen]
        arrivi = {p for p in tubi if ctx.pipe_ends[p][1].component_id == gen}
        if not partenze or not arrivi:
            continue
        visti: set[str] = set()
        pila = [p for p in partenze if p != tratto]
        while pila:
            corrente = pila.pop()
            if corrente in visti:
                continue
            visti.add(corrente)
            pila.extend(q for q in avanti[corrente] if q != tratto and q not in visti)
        if visti & arrivi:
            colpevoli.append(gen)
    return colpevoli


def rinomina_tubazioni(model: ProjectModel, prefisso: str) -> ProjectModel:
    return model.model_copy(
        update={
            "connections": [
                c.model_copy(update={"id": prefisso + c.id}) for c in model.connections
            ]
        }
    )


# ---------------------------------------------------------------------------
# Le topologie ostili, costruite a mano dal collaudo
# ---------------------------------------------------------------------------


def anello_di_ritorno(prima: str = "gen-a", seconda: str = "gen-b") -> ProjectModel:
    """Due macchine su un ritorno ad **anello**: il collettore si richiude.

        volano --t0--> J --t1--> S1 --a--> prima
                                 S1 --t2--> S2 --b--> seconda
                                            S2 --t3--> J   (l'anello si chiude)

    Il tratto che porta tutta l'acqua di ritorno e' `t1`: `t2` ne porta solo
    la parte che la prima macchina non ha preso. I due nomi delle macchine
    sono un parametro apposta: la topologia non cambia di un tubo.
    """
    return project(
        networks=[net("primario", "heating_water"), net("secondario", "heating_water")],
        components=[
            comp(prima, "heat-pump-air-water"),
            comp(seconda, "heat-pump-air-water"),
            comp("volano", "buffer-four-port"),
            comp("mand", "tee-junction"),
            comp("j", "tee-junction"),
            comp("s1", "tee-split"),
            comp("s2", "tee-split"),
            comp("utenza", "fan-coil"),
        ],
        connections=[
            pipe("m1", "primario", (prima, "water_supply"), ("mand", "a")),
            pipe("m2", "primario", (seconda, "water_supply"), ("mand", "c")),
            pipe("m3", "primario", ("mand", "b"), ("volano", "primary_in")),
            pipe("t0", "primario", ("volano", "primary_out"), ("j", "a")),
            pipe("t1", "primario", ("j", "b"), ("s1", "a")),
            pipe("a", "primario", ("s1", "b"), (prima, "water_return")),
            pipe("t2", "primario", ("s1", "c"), ("s2", "a")),
            pipe("b", "primario", ("s2", "b"), (seconda, "water_return")),
            pipe("t3", "primario", ("s2", "c"), ("j", "c")),
            pipe("x1", "secondario", ("volano", "secondary_out"), ("utenza", "in")),
            pipe("x2", "secondario", ("utenza", "out"), ("volano", "secondary_in")),
        ],
    )


def tre_macchine_due_ripartizioni() -> ProjectModel:
    """Il ritorno si dirama **due volte**: il tratto comune e' a monte di tutte."""
    return project(
        networks=[net("primario", "heating_water"), net("secondario", "heating_water")],
        components=[
            comp("pdc-1", "heat-pump-air-water"),
            comp("pdc-2", "heat-pump-air-water"),
            comp("pdc-3", "heat-pump-air-water"),
            comp("volano", "buffer-four-port"),
            comp("ma", "tee-junction"),
            comp("mb", "tee-junction"),
            comp("ra", "tee-split"),
            comp("rb", "tee-split"),
            comp("utenza", "fan-coil"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc-1", "water_supply"), ("ma", "a")),
            pipe("m2", "primario", ("pdc-2", "water_supply"), ("ma", "c")),
            pipe("m3", "primario", ("ma", "b"), ("mb", "a")),
            pipe("m4", "primario", ("pdc-3", "water_supply"), ("mb", "c")),
            pipe("m5", "primario", ("mb", "b"), ("volano", "primary_in")),
            pipe("r0", "primario", ("volano", "primary_out"), ("ra", "a")),
            pipe("r1", "primario", ("ra", "b"), ("pdc-1", "water_return")),
            pipe("r2", "primario", ("ra", "c"), ("rb", "a")),
            pipe("r3", "primario", ("rb", "b"), ("pdc-2", "water_return")),
            pipe("r4", "primario", ("rb", "c"), ("pdc-3", "water_return")),
            pipe("x1", "secondario", ("volano", "secondary_out"), ("utenza", "in")),
            pipe("x2", "secondario", ("utenza", "out"), ("volano", "secondary_in")),
        ],
    )


def confluenza_sopra_la_ripartizione() -> ProjectModel:
    """Un ramo rientra **prima** della ripartizione: confluenza e diramazione insieme.

    E' il caso che la correzione dice di aver chiuso: la camminata deve
    superare la confluenza e non fermarsi li'. Il tratto giusto e' `r1`, fra
    la confluenza e la ripartizione."""
    return project(
        networks=[
            net("primario", "heating_water"),
            net("secondario", "heating_water"),
            net("fredda", "cold_water"),
            net("sanitaria", "domestic_hot_water"),
        ],
        components=[
            comp("pdc-1", "heat-pump-air-water"),
            comp("pdc-2", "heat-pump-air-water"),
            comp("volano", "buffer-four-port"),
            comp("bollitore", "dhw-cylinder"),
            comp("dev", "diverting-valve-3way"),
            comp("mand", "tee-junction"),
            comp("conf", "tee-junction"),
            comp("rip", "tee-split"),
            comp("utenza", "fan-coil"),
            comp("acquedotto", "cold-water-inlet"),
            comp("utenze", "dhw-draw-off"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc-1", "water_supply"), ("mand", "a")),
            pipe("m2", "primario", ("pdc-2", "water_supply"), ("mand", "c")),
            pipe("m3", "primario", ("mand", "b"), ("dev", "in")),
            pipe("m4", "primario", ("dev", "out_a"), ("volano", "primary_in")),
            pipe("m5", "primario", ("dev", "out_b"), ("bollitore", "coil_in")),
            pipe("r0", "primario", ("volano", "primary_out"), ("conf", "a")),
            pipe("r0b", "primario", ("bollitore", "coil_out"), ("conf", "c")),
            pipe("r1", "primario", ("conf", "b"), ("rip", "a")),
            pipe("r2", "primario", ("rip", "b"), ("pdc-1", "water_return")),
            pipe("r3", "primario", ("rip", "c"), ("pdc-2", "water_return")),
            pipe("x1", "secondario", ("volano", "secondary_out"), ("utenza", "in")),
            pipe("x2", "secondario", ("utenza", "out"), ("volano", "secondary_in")),
            pipe("w1", "fredda", ("acquedotto", "a"), ("bollitore", "cold_in")),
            pipe("w2", "sanitaria", ("bollitore", "dhw_out"), ("utenze", "a")),
        ],
    )


def due_tratti_comuni_in_fila() -> ProjectModel:
    """Due candidati in serie, separati da un pezzo in linea: si sceglie il piu' vicino."""
    return project(
        networks=[net("primario", "heating_water"), net("secondario", "heating_water")],
        components=[
            comp("pdc-1", "heat-pump-air-water"),
            comp("pdc-2", "heat-pump-air-water"),
            comp("volano", "buffer-four-port"),
            comp("mand", "tee-junction"),
            comp("valvola", "valve-isolation"),
            comp("rip", "tee-split"),
            comp("utenza", "fan-coil"),
        ],
        connections=[
            pipe("m1", "primario", ("pdc-1", "water_supply"), ("mand", "a")),
            pipe("m2", "primario", ("pdc-2", "water_supply"), ("mand", "c")),
            pipe("m3", "primario", ("mand", "b"), ("volano", "primary_in")),
            pipe("r0", "primario", ("volano", "primary_out"), ("valvola", "a")),
            pipe("r1", "primario", ("valvola", "b"), ("rip", "a")),
            pipe("r2", "primario", ("rip", "b"), ("pdc-1", "water_return")),
            pipe("r3", "primario", ("rip", "c"), ("pdc-2", "water_return")),
            pipe("x1", "secondario", ("volano", "secondary_out"), ("utenza", "in")),
            pipe("x2", "secondario", ("utenza", "out"), ("volano", "secondary_in")),
        ],
    )


def due_anelli_separati() -> ProjectModel:
    """Il tratto comune non esiste davvero: due circuiti sulla stessa rete."""
    return project(
        networks=[net("rete", "heating_water")],
        components=[
            comp("gen-a", "heat-pump-air-water"),
            comp("term-a", "radiator"),
            comp("gen-b", "heat-pump-air-water"),
            comp("term-b", "radiator"),
        ],
        connections=[
            pipe("ma", "rete", ("gen-a", "water_supply"), ("term-a", "in")),
            pipe("ra", "rete", ("term-a", "out"), ("gen-a", "water_return")),
            pipe("mb", "rete", ("gen-b", "water_supply"), ("term-b", "in")),
            pipe("rb", "rete", ("term-b", "out"), ("gen-b", "water_return")),
        ],
    )


# ===========================================================================
# CORREZIONE 1 — la camminata del ritorno generale
# ===========================================================================


@pytest.mark.parametrize("nome", PROVE)
def test_nessuno_dei_cinque_ha_punti_aperti_sul_corredo_di_rete(nome: str) -> None:
    """L'affermazione della correzione, presa alla lettera e verificata."""
    assert kit_aperto(load(nome)) == {}


@pytest.mark.parametrize("nome", PROVE)
def test_il_corredo_esce_una_volta_sola_e_tutto_sullo_stesso_attacco(nome: str) -> None:
    """Quattro regole, un attacco solo: se si sparpagliassero, il «tratto
    comune» sarebbe una parola e non un punto."""
    posato = kit_posato(load(nome))
    assert set(posato) == KIT, nome
    assert len(set(posato.values())) == 1, posato


@pytest.mark.parametrize("nome", PROVE)
def test_permutare_pezzi_tubazioni_e_reti_non_muove_il_corredo(nome: str) -> None:
    """Il determinismo, provato piu' a fondo delle tre permutazioni di casa:
    otto rimescolamenti su **tutti** e cinque gli impianti."""
    base = load(nome)
    atteso = kit_posato(base)
    for seme in (2, 3, 5, 8, 13, 21, 34, 55):
        assert kit_posato(permuted(base, seme)) == atteso, (nome, seme)


@pytest.mark.parametrize("nome", PROVE)
def test_rinominare_le_tubazioni_non_muove_il_corredo(nome: str) -> None:
    """Fra rami pari la camminata guarda l'identificativo della tubazione: se
    quell'identificativo decidesse la sostanza, cambiarlo sposterebbe il pezzo."""
    base = load(nome)
    atteso = kit_posato(base)
    for prefisso in ("zz-", "aa-", "m-"):
        rinominato = kit_posato(rinomina_tubazioni(base, prefisso))
        assert {(n, c, p) for n, c, p in rinominato.values()} == {
            (n, c, p) for n, c, p in atteso.values()
        }, (nome, prefisso)


def test_con_tre_macchine_il_corredo_sta_a_monte_di_tutte_e_due_le_ripartizioni() -> None:
    """Il ritorno si apre due volte: il corredo non deve fermarsi alla seconda."""
    model = tre_macchine_due_ripartizioni()
    posato = kit_posato(model)
    assert set(posato) == KIT
    assert set(posato.values()) == {("primario", "ra", "a")}
    assert not generatori_che_si_chiudono_senza(model, "primario", "r0")


def test_la_camminata_supera_la_confluenza_e_arriva_alla_ripartizione() -> None:
    """E' il cuore della correzione: aprirsi sui rami invece di fermarsi
    sulla prima confluenza. Qui il ramo del bollitore rientra a monte della
    ripartizione, e il tratto giusto e' quello fra le due."""
    model = confluenza_sopra_la_ripartizione()
    posato = kit_posato(model)
    assert set(posato.values()) == {("primario", "rip", "a")}
    assert not generatori_che_si_chiudono_senza(model, "primario", "r1")


def test_con_due_tratti_comuni_in_fila_si_prende_quello_vicino_alle_macchine() -> None:
    """«A monte della prima ripartizione», non «il piu' lontano possibile»."""
    posato = kit_posato(due_tratti_comuni_in_fila())
    assert set(posato.values()) == {("primario", "rip", "a")}


def test_un_anello_sul_ritorno_non_manda_la_camminata_in_tondo() -> None:
    """Il grafo con un anello deve terminare e dare una risposta, non girare."""
    posato = kit_posato(anello_di_ritorno())
    assert set(posato) == KIT


def test_dove_il_tratto_comune_non_esiste_resta_un_punto_aperto() -> None:
    """Due circuiti separati sulla stessa rete: nessun ramo scelto in silenzio."""
    model = due_anelli_separati()
    assert kit_posato(model) == {}
    assert kit_aperto(model) == dict.fromkeys(KIT, GapReason.NO_COMMON_RUN.value)
    finito, _, _ = saturate(model, CAT, REG)
    vietate = {"expansion", "filling", "pressure_measurement", "sludge_separation"}
    for c in finito.components:
        assert not set(CAT.get(c.definition_id).functions) & vietate, c.id


@pytest.mark.parametrize(
    "nome",
    [
        PROVE[0],
        PROVE[1],
        PROVE[2],
        pytest.param(
            PROVE[3],
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "DIFETTO 1 del collaudo. Impianto 4, l'ibrido — l'impianto per cui "
                    "la correzione esiste. Il tratto scelto (p5, fra il volume tecnico "
                    "e la ripartizione) NON porta l'acqua che la caldaia rimanda dallo "
                    "scambiatore sanitario: quel ramo rientra a valle, in "
                    "`ritorno-caldaia`, e non passa mai per p5. Togliendo p5 il "
                    "circuito della caldaia si chiude lo stesso. Il corredo — "
                    "defangatore compreso, la cui motivazione scritta e' «li' passa "
                    "tutta l'acqua che torna, quindi un pezzo solo protegge ogni "
                    "generatore» — viene posato lo stesso, senza punto aperto e senza "
                    "una parola. Prima della correzione erano quattro punti aperti."
                ),
            ),
        ),
        PROVE[4],
    ],
)
def test_il_tratto_scelto_porta_davvero_l_acqua_di_tutti_i_generatori(nome: str) -> None:
    """Il criterio duro del collaudo, e non e' inventato: e' la motivazione
    scritta del defangatore. Se togliendo il tratto scelto il circuito di un
    generatore si chiude lo stesso, quel tratto non porta la sua acqua."""
    model = load(nome)
    posato = kit_posato(model)
    assert posato, nome
    rete, componente, attacco = next(iter(posato.values()))
    tratto = tratto_di(model, componente, attacco)
    assert not generatori_che_si_chiudono_senza(model, rete, tratto), (
        f"{nome}: il tratto {tratto} non taglia il circuito di tutti i generatori"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 2 del collaudo. Con un anello sul ritorno, il tratto scelto cambia "
        "col NOME delle macchine, a topologia identica: chiamandole gen-a/gen-b il "
        "corredo va su `s1.a` (giusto: `t1` porta tutta l'acqua), chiamandole "
        "zeta/alfa va su `s2.a` — che sta a VALLE della prima ripartizione e porta "
        "solo la parte di acqua che la prima macchina non ha preso. La camminata "
        "parte dal primo generatore in ordine alfabetico e prende il primo tratto "
        "condiviso che incontra: con un anello, «il primo che incontro» dipende da "
        "chi parte. E' esattamente il difetto che la regola dice di non avere — il "
        "corredo sul ramo di una macchina sola."
    ),
)
def test_su_un_anello_il_corredo_non_dipende_dal_nome_delle_macchine() -> None:
    primo = kit_posato(anello_di_ritorno("gen-a", "gen-b"))
    secondo = kit_posato(anello_di_ritorno("zeta", "alfa"))
    assert {(n, c, p) for n, c, p in primo.values()} == {
        (n, c, p) for n, c, p in secondo.values()
    }


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 2 del collaudo, l'altra faccia: sull'anello con le macchine chiamate "
        "zeta/alfa il tratto scelto (`t2`) non porta l'acqua di `zeta`."
    ),
)
def test_su_un_anello_il_tratto_scelto_porta_l_acqua_di_tutti() -> None:
    model = anello_di_ritorno("zeta", "alfa")
    rete, componente, attacco = next(iter(kit_posato(model).values()))
    tratto = tratto_di(model, componente, attacco)
    assert not generatori_che_si_chiudono_senza(model, rete, tratto)


# ===========================================================================
# CORREZIONE 2 — il regime ricavato dalle potenze dichiarate (D-108)
# ===========================================================================

# Le potenze come il committente le ha scritte, impianto per impianto, e la
# somma che se ne ricava. Riscritte qui dal testo originale, non copiate dai
# commenti di chi ha fatto la correzione.
POTENZE = {
    PROVE[0]: ([12.0, 12.0], "due pompe di calore aria-acqua da 12 kW ciascuna"),
    PROVE[1]: ([15.0], "una pompa di calore aria-acqua reversibile da 15 kW"),
    PROVE[2]: ([8.0], "una pompa di calore aria-acqua da 8 kW"),
    PROVE[3]: ([10.0, 24.0], "una pompa di calore aria-acqua da 10 kW e da una caldaia"),
    PROVE[4]: ([35.0, 35.0, 35.0], "tre pompe di calore aria-acqua reversibili da 35 kW"),
}


@pytest.mark.parametrize("nome", PROVE)
def test_il_regime_dichiarato_e_quello_che_le_potenze_del_testo_danno(nome: str) -> None:
    """Il conto rifatto da zero: si rilegge il testo del committente, si somma,
    si confronta con la soglia e si pretende che il modello dica lo stesso.

    La soglia e' inclusiva — D-106 dice «piccole centrali (fino a 35 kW)» —
    quindi 35 kW esatti sono piccola centrale."""
    potenze, citazione = POTENZE[nome]
    testo = TESTO.read_text(encoding="utf-8")
    assert citazione in testo, f"la citazione non e' piu' nel testo: {citazione}"
    model = load(nome)
    atteso = PlantRegime.OVER_35_KW if sum(potenze) > 35.0 else PlantRegime.UP_TO_35_KW
    assert model.plant_regime is atteso, (nome, sum(potenze))


def test_quattro_impianti_sotto_e_uno_solo_sopra() -> None:
    """Il conto complessivo che la correzione promette."""
    regimi = [load(n).plant_regime for n in PROVE]
    assert regimi.count(PlantRegime.UP_TO_35_KW) == 4
    assert regimi.count(PlantRegime.OVER_35_KW) == 1
    assert load(PROVE[4]).plant_regime is PlantRegime.OVER_35_KW


def test_le_regole_non_sommano_mai_le_potenze_dei_pezzi() -> None:
    """Il rovescio di D-108: chi **legge** il testo ricava il regime, le regole
    quel campo lo leggono e basta. Si scrivono 900 kW su ogni pezzo, nelle due
    forme che il progetto usa, e non si deve muovere niente."""
    base = load(PROVE[0]).model_copy(update={"plant_regime": None})
    gonfio = base.model_copy(
        update={
            "components": [
                c.model_copy(update={"properties": {"potenza": "900 kW", "power_kw": 900.0}})
                for c in base.components
            ]
        }
    )
    grande = {r.id for r in REG.all() if r.when.plant_regime is PlantRegime.OVER_35_KW}
    _, applicate, _ = saturate(gonfio, CAT, REG)
    _, riferimento, _ = saturate(base, CAT, REG)
    assert not {p.rule_id for p in applicate} & grande
    assert {p.rule_id for p in applicate} == {p.rule_id for p in riferimento}


def test_senza_dichiarazione_vale_il_corredo_minimo_e_non_un_terzo_regime() -> None:
    """«Se le potenze non ci sono, il regime resta non dichiarato e vale il
    corredo minimo»: allora un impianto senza dichiarazione deve uscire
    identico a uno dichiarato piccolo, su tutti e cinque."""
    grande = {r.id for r in REG.all() if r.when.plant_regime is PlantRegime.OVER_35_KW}
    for nome in PROVE:
        nudo = load(nome).model_copy(update={"plant_regime": None})
        piccolo = nudo.model_copy(update={"plant_regime": PlantRegime.UP_TO_35_KW})
        senza = saturate(nudo, CAT, REG)
        con = saturate(piccolo, CAT, REG)
        assert not {p.rule_id for p in senza[1]} & grande, nome
        assert {p.rule_id for p in senza[1]} == {p.rule_id for p in con[1]}, nome
        assert {g.key for g in senza[2]} == {g.key for g in con[2]}, nome


def test_le_istruzioni_dicono_di_ricavare_il_regime_e_di_non_chiederlo() -> None:
    """La correzione vive nelle istruzioni dell'interprete: si verifica che ci
    siano davvero le tre cose che promette — si ricava, la soglia e' inclusiva,
    e senza potenze si omette il campo e si scrive la domanda."""
    testo = ISTRUZIONI.read_text(encoding="utf-8")
    assert "Si ricava, non si chiede" in testo
    assert "somma ≤ 35 kW" in testo and "up_to_35_kw" in testo
    assert "somma > 35 kW" in testo and "over_35_kw" in testo
    assert "il testo non dà le potenze" in testo and "ometti il campo" in testo
    assert "qualunque cosa il testo abbia già scritto — a partire dalle potenze" in testo


def test_nessun_documento_dice_piu_che_il_regime_non_si_ricava_dalle_potenze() -> None:
    """La contraddizione che aveva fermato la prova in camera pulita: il kit
    non deve piu' contenere da nessuna parte la frase vecchia di D-106.
    Restano fuori il registro delle decisioni, che conserva la storia, e gli
    atti del giro interrotto, che sono la prova del difetto."""
    vecchia = re.compile(r"nemmeno sommando le potenze", re.IGNORECASE)
    esclusi = {"docs/DECISION_LOG.md"}
    colpevoli = []
    for cartella in ("docs", "src", "skill", "schemas", "examples", "rules"):
        for percorso in (ROOT / cartella).rglob("*"):
            if not percorso.is_file() or percorso.suffix not in {".md", ".py", ".json"}:
                continue
            relativo = percorso.relative_to(ROOT).as_posix()
            if relativo in esclusi or "giro-interrotto" in relativo:
                continue
            if vecchia.search(percorso.read_text(encoding="utf-8")):
                colpevoli.append(relativo)
    assert colpevoli == [], colpevoli


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 3 del collaudo. Le istruzioni dell'interprete ordinano di trascrivere "
        "la potenza in `properties` (§4.5) e il loro esempio lo dice a parole: «la "
        "potenza detta dal testo compare in DUE posti: trascritta in `properties`, e "
        "usata per ricavare `plant_regime`». Nei cinque grafi di prova compare in un "
        "posto solo: `plant_regime` c'e', le potenze no, e ogni componente ha "
        "`properties` vuote. Il conto che giustifica il regime vive in un commento "
        "Python del generatore delle fixture. Non e' un dettaglio: quei cinque grafi "
        "sono il METRO congelato con cui si giudichera' l'interprete quando esistera' "
        "(`examples/prova/input/README.md`), e un interprete che seguisse le istruzioni "
        "produrrebbe un grafo diverso dal metro che lo misura. E' la stessa specie di "
        "contraddizione dentro il kit che ha fatto fermare la prova in camera pulita "
        "del 7 agosto. Chi apre il modello vede la conclusione e non vede il dato da "
        "cui e' stata tratta."
    ),
)
@pytest.mark.parametrize("nome", PROVE)
def test_le_potenze_da_cui_il_regime_e_stato_letto_stanno_nel_modello(nome: str) -> None:
    model = load(nome)
    con_potenza = [
        c.id
        for c in model.components
        if c.id in generatori(model)
        and any("potenz" in str(k).lower() or "power" in str(k).lower() for k in c.properties)
    ]
    assert con_potenza == generatori(model), (
        f"{nome}: il regime e' dichiarato ma le potenze non sono nel modello"
    )


DIFETTO_4 = (
    "DIFETTO 4 del collaudo. La regola di §4.6 ha due soli rami: «somma le potenze» e "
    "«il testo non da' le potenze». Manca il caso di mezzo, che e' il piu' insidioso: "
    "il testo da' la potenza di una macchina e NON quella di un'altra. Sommando le sole "
    "dichiarate si ottiene un totale sottostimato e si scrive il regime in silenzio, "
    "senza nessuna domanda. E non e' teorico: e' successo. L'impianto 3 ha DUE macchine "
    "che il catalogo classifica generatrici di calore — la pompa di calore aria-acqua e "
    "lo scaldacqua in pompa di calore, che dichiara `heat_generation` — e il testo da' "
    "la potenza solo della prima (8 kW); dello scaldacqua da' il volume (200 litri), non "
    "la potenza. La somma e' stata fatta su una macchina sola, il regime e' stato scritto "
    "lo stesso, e la mancanza non e' stata detta da nessuna parte. Qui l'esito non cambia "
    "perche' il margine e' larghissimo; su un impianto vicino alla soglia — il 4 sta a "
    "34 kW su 35 — lo stesso silenzio ribalterebbe il corredo. E' anche la stessa "
    "classificazione di catalogo che il collaudo precedente aveva gia' trovato "
    "insidiosa sullo scaldacqua."
)


@pytest.mark.xfail(strict=True, reason=DIFETTO_4)
def test_le_istruzioni_coprono_la_potenza_dichiarata_solo_su_alcune_macchine() -> None:
    testo = ISTRUZIONI.read_text(encoding="utf-8")
    inizio = testo.index("### 4.6")
    sezione = testo[inizio : testo.index("---", inizio)]
    parziale = ("solo alcune", "una sola", "non tutte", "parziale", "solo di alcune")
    assert any(chiave in sezione for chiave in parziale), (
        "§4.6 non dice cosa fare quando una macchina dichiara la potenza e un'altra no"
    )


@pytest.mark.parametrize(
    "nome",
    [
        PROVE[0],
        PROVE[1],
        pytest.param(PROVE[2], marks=pytest.mark.xfail(strict=True, reason=DIFETTO_4)),
        PROVE[3],
        PROVE[4],
    ],
)
def test_ogni_macchina_che_genera_calore_porta_una_potenza_nel_conto(nome: str) -> None:
    """Il conto del regime deve contare tutte le macchine che generano calore.

    Se il grafo ne ha piu' di quante il testo ne dichiara con la potenza, la
    somma e' parziale: o si dice, o il regime scritto non e' fondato."""
    potenze, _ = POTENZE[nome]
    macchine = generatori(load(nome))
    assert len(macchine) == len(potenze), (
        f"{nome}: {len(macchine)} macchine generatrici nel grafo {macchine}, "
        f"{len(potenze)} potenze nel testo — la somma del regime e' parziale"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 5 del collaudo. Il documento che il committente legge si contraddice "
        "dentro se stesso: al punto 1 dice ancora «Nessuno dei cinque testi dichiara il "
        "regime, e senza dichiarazione vale il corredo minimo — quello della piccola "
        "centrale», che era vero prima della correzione; piu' sotto, la sezione «Il "
        "regime: letto dai testi, non chiesto a te» porta la tabella delle potenze e "
        "dichiara il quinto impianto SOPRA i 35 kW, con il corredo da grande centrale. "
        "La correzione ha riscritto la sezione nuova e ha lasciato in piedi la frase "
        "vecchia, nella stessa pagina."
    ),
)
def test_il_confronto_per_il_committente_non_si_contraddice_sul_regime() -> None:
    testo = CONFRONTO.read_text(encoding="utf-8")
    dice_letto = "letto dai testi" in testo or "letto dal testo" in testo
    dice_non_dichiarato = "Nessuno dei cinque testi dichiara il regime" in testo
    assert not (dice_letto and dice_non_dichiarato), (
        "lo stesso documento dice che il regime e' letto dai testi e che nessun testo lo dichiara"
    )
