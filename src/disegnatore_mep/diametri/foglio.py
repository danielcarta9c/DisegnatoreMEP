"""Il foglio dei calcoli (REL-007): per ogni tratto i dati, la portata, il DN, la velocita'.

Il PO controlla i numeri oltre al disegno (punto 5 del pacchetto): per ogni tratto
d'acqua dell'impianto una riga, con **da dove viene la portata** — i dati del
progettista che il conto ha usato —, e il DN con la velocita' che ne risulta e
quella massima del suo diametro (D-193). Un tratto senza DN dice perche': una rete
non chiesta o esistente, una portata che i dati non danno.

Le estremita' si nominano con la sigla della lettura dell'impianto (D-097): e'
quella che la tavola scrive, e anche i raccordi ne hanno una.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.model.project import ProjectModel

from .portate import Portate, portate_delle_tratte
from .tratti import TrattoDelDiametro, tratti_del_diametro


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
    dn: int | None
    velocita_m_s: float | None
    velocita_massima_m_s: float | None
    nota: str | None


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
        righe.append(
            RigaDelCalcolo(
                rete=", ".join(reti.get(item, item) for item in tratto.reti),
                da=sigle.get(capo.component_id, capo.component_id),
                a=sigle.get(fine.component_id, fine.component_id),
                dati=_dati(tratto, portate, sigle) if tratto.portata_m3h is not None else "",
                potenza_kw=tratto.potenza_kw,
                salto_termico_k=tratto.salto_termico_k,
                portata_m3h=tratto.portata_m3h,
                dn=None if diametro is None else diametro.dn,
                velocita_m_s=None if diametro is None else diametro.velocita_m_s,
                velocita_massima_m_s=None if diametro is None else diametro.velocita_massima_m_s,
                nota=tratto.perche_senza_dn,
            )
        )
    return tuple(righe)


def foglio_in_markdown(righe: Sequence[RigaDelCalcolo]) -> str:
    """Il foglio come tabella: si legge nel rapporto e nella pull request."""
    trattino = "–"
    testa = (
        "| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | "
        "velocità m/s | massima m/s | note |\n"
        "|---|---|---|---|---:|---:|---:|---|---:|---:|---|\n"
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
                    trattino if riga.dn is None else f"**Øi {riga.dn}**",
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


__all__ = ["RigaDelCalcolo", "foglio_in_markdown", "righe_del_calcolo"]
