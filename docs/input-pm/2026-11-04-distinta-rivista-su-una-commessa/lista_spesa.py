"""Distinta [commessa aria-aria] in forma di lista della spesa per l'installatore (indicazione del PO, 04/11/2026).

Stesso calcolo di `mep.py distinta` (stesse regole, stessi numeri); cambia solo il documento:
- copertina e avvertenze senza il linguaggio dell'offerta a corpo;
- capitolo 2: le tratte, senza la verifica dell'aria e delle linee (e' un controllo del progettista);
- capitolo 3: la lista dei materiali da comprare, sezioni A (fornite da Nove C, dichiarate) S B C D E X;
  fuori le assistenze murarie F, le opere del Committente Z e le voci a corpo che non si comprano;
- niente capitoli 4-7 (attivita', varianti, domande, note e regole).
Uso: python3 lista_spesa.py <argomenti di mep.py distinta>
"""
import sys
from pathlib import Path

L = Path(__file__).parent
sys.path.insert(0, str(L / "skill" / "scripts"))

from disegnatore_mep.distinta import comando, documento as D  # noqa: E402

SEZIONI = ("A", "S", "B", "C", "D", "E", "X")


def _cap1(distinta):
    progetto = distinta.progetto
    tavola = (f"{D.dato_o_da_definire(progetto, 'sheet_number')}, rev. {D.dato_o_da_definire(progetto, 'revision')} "
              f"del {D.data_del_cartiglio(progetto)}")
    chiavi = D.Chiavi(righe=(
        ("Commessa", D.dato_o_da_definire(progetto, "commission_code")),
        ("Impianto", D.dato_o_da_definire(progetto, "project_name")),
        ("Committente", D.dato_o_da_definire(progetto, "client")),
        ("Indirizzo", D.dato_o_da_definire(progetto, "address")),
        ("Schema funzionale", f"tavola {tavola}; pianta M.03"),
    ))
    avvertenze = (
        "Le quantità sono indicative e già maggiorate: verificarle in sopralluogo prima di comprare.",
        "Le apparecchiature della sezione A (unità esterna e interna Daikin, comando Madoka, plenum e centrale Airzone, "
        "termostati Airzone) le fornisce Nove C: non si comprano, l'installatore le posa.",
        "Bocchette e griglie e le opere edili (controsoffitti, velette, botole, chiusura delle tracce) sono del "
        "Committente: non sono in questa lista.",
        "Le sigle (UE-01, PLZ-01, DV-01, B1...) sono quelle dello schema M.02 e della pianta M.03.",
    )
    return D.Capitolo(1, "L'impianto", (
        chiavi,
        D.Paragrafo("La lista dei materiali da comprare per realizzare l'impianto dello schema funzionale M.02."),
        D.Elenco(avvertenze, titolo="Da sapere"),
    ))


def _cap2(distinta):
    foglio = D.tabelle_del_foglio(distinta, ("tratte",))["tabelle"][0]
    righe = tuple(tuple(r) for r in foglio["sezioni"][0]["righe"])
    tratte = D.Tabella(
        intestazioni=("Tratto", "Da - a", "Ø / sezione", "Materiale", "Q m³/h", "v m/s", "L stimata m", "L da comprare m"),
        righe=righe, pesi=(0.6, 2.0, 1.25, 2.0, 0.65, 0.6, 0.75, 0.8), a_destra=frozenset({4, 5, 6, 7}))
    blocchi = [D.Paragrafo("Ogni tratto con la sua sezione, il materiale e la lunghezza: la «L stimata» è quella del "
                           "progetto, la «L da comprare» è già maggiorata. Un raccordo diretto (la ripresa sulla "
                           "macchina, un cablaggio di fabbrica) non ha lunghezza."), tratte]
    return D.Capitolo(2, "Le tratte: sezioni e lunghezze", tuple(blocchi))


def _cap3(distinta):
    regole = distinta.regole
    blocchi = [D.Paragrafo("Colonna «Fornitura»: «installatore» = da comprare; «Nove C» = fornito da Nove C, solo da posare.")]
    for lettera in SEZIONI:
        voci = [v for v in distinta.voci_della_sezione(lettera)
                if lettera == "A" or v.um.strip().lower() != "a corpo"]
        if voci:
            titolo = "A. Apparecchiature (fornite da Nove C, da posare)" if lettera == "A" else f"{lettera}. {regole.titolo(lettera)}"
            blocchi.append(D._computo(voci, titolo))
    return D.Capitolo(3, "La lista dei materiali", tuple(blocchi))


def documento_lista(distinta):
    doc = D.documento_della_distinta(distinta)
    progetto = distinta.progetto
    impianto = D.dato_o_da_definire(progetto, "project_name")
    c = doc.copertina
    copertina = D.Copertina(
        titolo=("Lista materiali", "per l'installatore", impianto),
        sottotitolo=c.sottotitolo,
        riquadro=("LISTA MATERIALI PER L'INSTALLATORE", "Quantità indicative, già maggiorate",
                  "Da verificare in sopralluogo prima dell'acquisto"),
        piede=c.piede, riserva=c.riserva)
    return D.Documento(nome=doc.nome, titolo=doc.titolo, intestazione=doc.intestazione, copertina=copertina,
                       capitoli=(_cap1(distinta), _cap2(distinta), _cap3(distinta)), vietate=doc.vietate)


comando.documento_della_distinta = documento_lista

if __name__ == "__main__":
    import runpy
    sys.argv = [str(L / "skill" / "scripts" / "mep.py"), "distinta", *sys.argv[1:]]
    runpy.run_path(sys.argv[0], run_name="__main__")
