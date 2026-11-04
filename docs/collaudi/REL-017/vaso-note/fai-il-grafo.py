"""La villetta di riferimento (`docs/collaudi/REL-015/pdc-regola/`) **con il vaso sanitario e le
note del progettista** (REL-017, I-271, I-272).

Il PO, da una commessa reale (villetta, PdC Shenling 12 kW, volano a 4 attacchi, ACS su
deviatrice, circolatore secondario verso il pavimento radiante): «Verifica quanto sopra detto.
risolvi.». Due difetti:

- **I-272, il vaso sanitario.** L'acqua calda della villetta non e' centralizzata, e la regola
  del vaso sanitario chiede se il bollitore lo porta dentro. Il «no» del progettista non aveva
  una forma nel grafo, e il vaso si scriveva a mano sull'acqua fredda: un punto fisso, e le
  regole posavano il gruppo di sicurezza — con il non ritorno dentro — fra lui e il bollitore.
  Il vaso sta fra il non ritorno e il bollitore (D-178). Adesso il «no» si scrive sul bollitore,
  `non_a_bordo: ["expansion"]`, e il vaso lo posa la regola, al suo posto;
- **I-271, le note di posa.** Il progettista scrive le sue in `metadata.note_di_posa`: qui un
  isolamento differenziato — tratto interrato, a muro esterno, in centrale —, che prende il
  posto della nota generata sull'isolamento perche' comincia con «Isolamento». Le note escono
  solo nell'esecutivo: il livello e' `esecutivo`.

Il resto e' la villetta com'e' agli atti.

    python3 docs/collaudi/REL-017/vaso-note/fai-il-grafo.py [uscita.json]
"""

import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
uscita = Path(sys.argv[1]) if len(sys.argv) > 1 else QUI / "grafo.json"
grafo = json.loads((RADICE / "docs/collaudi/REL-015/pdc-regola/grafo.json").read_text(encoding="utf-8"))

grafo["metadata"]["project_id"] = "centrale-termica-villetta-vaso-e-note"
grafo["metadata"]["issue_date"] = "2026-11-04"
grafo["metadata"]["livello"] = "esecutivo"
grafo["metadata"]["note_di_posa"] = [
    "Isolamento delle tubazioni a celle chiuse, conduttività massima 0,040 W/mK: nel tratto "
    "interrato in guaina corrugata, spessore 30 mm; a muro esterno spessore pieno 40 mm con "
    "protezione anti-UV; in centrale spessori minimi dell'Allegato B del DPR 412/93.",
]

for pezzo in grafo["components"]:
    if pezzo["id"] == "bollitore":
        # La risposta al punto aperto di completa: il bollitore non porta il vaso dentro.
        pezzo["non_a_bordo"] = ["expansion"]

uscita.write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
