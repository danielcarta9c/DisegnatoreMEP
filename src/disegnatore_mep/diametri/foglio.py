"""Il foglio dei calcoli (REL-007): per ogni tratto i dati, la portata, il tubo, la velocita'.

Il PO controlla i numeri oltre al disegno (punto 5 del pacchetto): per ogni tratto
d'acqua dell'impianto una riga, con **da dove viene la portata** — i dati del
progettista che il conto ha usato —, e il tubo scelto (I-279): l'**Øi minimo** alla
massima del suo pollice, il **tubo** nella notazione del suo materiale, l'**Øi reale**
e la **velocita' reale** con la massima (D-193). L'Øi sta solo qui: sulla tavola c'e'
il tubo da comprare. Dove il progettista ha scritto il suo tubo, la riga porta quello,
con la sua velocita', e la nota dice se supera la massima e che cosa il calcolo
sceglierebbe. Un tratto senza tubo dice perche': una rete non chiesta o esistente, una
portata che i dati non danno.

Le estremita' si nominano con la sigla della lettura dell'impianto (D-097): e'
quella che la tavola scrive, e anche i raccordi ne hanno una.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.model.project import ProjectModel

from .perdite import (
    KPA_AL_METRO,
    MAGGIORAZIONE_CONCENTRATE,
    RUGOSITA_DEL_MATERIALE,
    VISCOSITA_CINEMATICA_M2_S,
    VerificaDellaPrevalenza,
)
from .portate import Portate, portate_delle_tratte
from .tratti import TrattoDelDiametro, tratti_del_diametro
from .tubi import tubo_per


@dataclass(frozen=True)
class RigaDelCalcolo:
    rete: str
    da: str
    a: str
    dati: str
    """I dati del progettista da cui viene la portata, con la sigla del pezzo."""
    potenza_kw: float | None
    salto_termico_k: float | None
    portata_m3h: float | None
    interno_minimo_mm: float | None
    """L'Øi sotto il quale la velocita' supererebbe la massima del pollice del tubo."""
    tubo: str | None
    """Il tubo, come la tavola lo scrive: «MS 32×3»."""
    interno_mm: float | None
    """L'Øi reale del tubo."""
    velocita_m_s: float | None
    velocita_massima_m_s: float | None
    nota: str | None
    del_progettista: bool = False
    """Il tubo e' quello che il progettista ha scritto, non quello del calcolo."""


def _numero(valore: float, cifre: int) -> str:
    testo = f"{valore:.{cifre}f}"
    return testo.replace(".", ",")


def _dati(tratto: TrattoDelDiametro, portate: Portate, sigle: dict[str, str]) -> str:
    parti: list[str] = []
    for component_id in tratto.fonti:
        dato = portate.dati.get(component_id)
        sigla = sigle.get(component_id, component_id)
        if dato is None:
            parti.append(sigla)
        elif dato.potenza_kw is not None and dato.salto_termico_k is not None:
            parti.append(
                f"{sigla} {_numero(dato.potenza_kw, 1).removesuffix(',0')} kW, "
                f"ΔT {_numero(dato.salto_termico_k, 1).removesuffix(',0')} K"
            )
        else:
            parti.append(f"{sigla} {_numero(dato.portata_m3h, 2)} m³/h")
    return " + ".join(parti)


def righe_del_calcolo(
    project: ProjectModel,
    catalog: ComponentRegistry,
    sigle: dict[str, str],
    tratti: Sequence[TrattoDelDiametro] | None = None,
) -> tuple[RigaDelCalcolo, ...]:
    """Una riga per tratto d'acqua, nell'ordine dei tratti."""
    portate = portate_delle_tratte(project, catalog, tratte_del_progetto(project, catalog))
    if tratti is None:
        tratti = tratti_del_diametro(project, catalog, portate=portate)
    reti = {item.id: item.name for item in project.networks}
    righe: list[RigaDelCalcolo] = []
    for tratto in tratti:
        capo, fine = tratto.capi
        diametro = tratto.diametro if tratto.richiesto else None
        tubo = tratto.tubo_del_progettista or (None if diametro is None else diametro.tubo)
        portata = tratto.portata_m3h
        velocita = None if tubo is None or portata is None or portata <= 0 else tubo.velocita_m_s(portata)
        minimo = None
        nota = tratto.perche_senza_dn
        if tubo is not None and portata is not None and portata > 0:
            minimo = (4 * portata / 3600.0 / (3.141592653589793 * tubo.velocita_massima_m_s)) ** 0.5 * 1000
        if tratto.tubo_del_progettista is not None and velocita is not None and tubo is not None:
            calcolo = tubo_per(portata or 0.0, tubo.materiale) if portata else None
            if velocita > tubo.velocita_massima_m_s * (1 + 1e-9):
                nota = "del progettista: oltre la massima" + (
                    f", il calcolo sceglierebbe {calcolo.scritta}" if calcolo is not None else ""
                )
            else:
                nota = "del progettista"
        righe.append(
            RigaDelCalcolo(
                rete=", ".join(reti.get(item, item) for item in tratto.reti),
                da=sigle.get(capo.component_id, capo.component_id),
                a=sigle.get(fine.component_id, fine.component_id),
                dati=_dati(tratto, portate, sigle) if tratto.portata_m3h is not None else "",
                potenza_kw=tratto.potenza_kw,
                salto_termico_k=tratto.salto_termico_k,
                portata_m3h=tratto.portata_m3h,
                interno_minimo_mm=minimo,
                tubo=None if tubo is None else tubo.scritta,
                interno_mm=None if tubo is None else tubo.interno_mm,
                velocita_m_s=velocita,
                velocita_massima_m_s=None if tubo is None else tubo.velocita_massima_m_s,
                nota=nota,
                del_progettista=tratto.tubo_del_progettista is not None,
            )
        )
    return tuple(righe)


def foglio_in_markdown(righe: Sequence[RigaDelCalcolo]) -> str:
    """Il foglio come tabella: si legge nel rapporto e nella pull request."""
    trattino = "–"
    testa = (
        "| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | "
        "tubo | Øi reale mm | velocità m/s | massima m/s | note |\n"
        "|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|\n"
    )
    corpo = []
    for riga in righe:
        corpo.append(
            "| "
            + " | ".join(
                [
                    riga.rete,
                    riga.da,
                    riga.a,
                    riga.dati or trattino,
                    trattino if riga.potenza_kw is None else _numero(riga.potenza_kw, 1),
                    trattino if riga.salto_termico_k is None else _numero(riga.salto_termico_k, 1),
                    trattino if riga.portata_m3h is None else _numero(riga.portata_m3h, 3),
                    trattino if riga.interno_minimo_mm is None else _numero(riga.interno_minimo_mm, 1),
                    trattino if riga.tubo is None else f"**{riga.tubo}**",
                    trattino if riga.interno_mm is None else _numero(riga.interno_mm, 1),
                    trattino if riga.velocita_m_s is None else _numero(riga.velocita_m_s, 2),
                    trattino
                    if riga.velocita_massima_m_s is None
                    else _numero(riga.velocita_massima_m_s, 1),
                    riga.nota or "",
                ]
            )
            + " |"
        )
    return testa + "\n".join(corpo) + "\n"


def prevalenza_in_markdown(
    verifiche: Sequence[VerificaDellaPrevalenza], sigle: dict[str, str]
) -> str:
    """La verifica della prevalenza della pompa a bordo (I-270), sotto il foglio.

    Per ogni macchina che ha i dati il giro piu' costoso, tratto per tratto, e il
    confronto con la prevalenza utile. Vuota se nessuna macchina li ha: senza dati
    la verifica non si fa, e non si scrive."""
    if not verifiche:
        return ""
    parti = [
        "\n### Verifica della prevalenza della pompa a bordo\n\n"
        f"Darcy-Weisbach con Swamee-Jain, acqua a 40 °C (ν {_numero(VISCOSITA_CINEMATICA_M2_S * 1e6, 3)}·10⁻⁶ "
        f"m²/s), sul diametro interno reale del tubo e con la scabrezza del suo materiale (multistrato "
        f"{_numero(RUGOSITA_DEL_MATERIALE['multistrato'] * 1000, 3)} mm, acciaio "
        f"{_numero(RUGOSITA_DEL_MATERIALE['acciaio'] * 1000, 3)} mm, rame "
        f"{_numero(RUGOSITA_DEL_MATERIALE['rame'] * 1000, 4)} mm); concentrate il "
        f"{MAGGIORAZIONE_CONCENTRATE:.0%} delle distribuite. Non entrano le perdite proprie di serpentini, "
        "scambiatori e volano.\n"
    ]
    for verifica in verifiche:
        nome = sigle.get(verifica.macchina, verifica.macchina)
        righe = "\n".join(
            f"| {sigle.get(item.da, item.da)} | {sigle.get(item.a, item.a)} | {item.tubo.scritta} "
            f"(Øi {_numero(item.tubo.interno_mm, 1)}) | "
            f"{_numero(item.portata_m3h, 3)} | {_numero(item.velocita_m_s, 2)} | {_numero(item.lunghezza_m, 1)} | "
            f"{_numero(item.perdita_pa_m, 0)} | {_numero(item.perdita_kpa, 2)} |"
            for item in verifica.giro
        )
        esito = "**NON BASTA**" if verifica.supera else "basta"
        parti.append(
            f"\n**{nome}** — il giro piu' costoso di {verifica.giri}:\n\n"
            "| da | a | tubo | portata m³/h | velocità m/s | L m | Pa/m | kPa |\n"
            "|---|---|---|---:|---:|---:|---:|---:|\n"
            f"{righe}\n\n"
            f"Distribuite {_numero(verifica.distribuite_kpa, 2)} kPa + concentrate "
            f"{_numero(verifica.concentrate_kpa, 2)} kPa = **{_numero(verifica.totale_kpa, 2)} kPa**; "
            f"prevalenza utile {_numero(verifica.prevalenza_utile_kpa, 1)} kPa"
            + (
                f" ({_numero(verifica.prevalenza_utile_kpa / KPA_AL_METRO, 0)} m, indicativo del PO; il valore "
                "vero è la curva del manuale alla portata)"
                if verifica.assunta
                else ""
            )
            + f": {esito}.\n"
        )
    return "".join(parti)


__all__ = ["RigaDelCalcolo", "foglio_in_markdown", "prevalenza_in_markdown", "righe_del_calcolo"]
