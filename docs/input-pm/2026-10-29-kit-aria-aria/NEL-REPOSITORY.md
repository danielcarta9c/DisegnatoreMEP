# Il kit nel repository: che cosa è rimasto fuori

Il kit è l'input del PO del 29 ottobre 2026 (I-224 … I-229), copiato qui com'è arrivato, con quattro esclusioni. Il
repository è pubblico, e il perimetro esclude i dati del cliente in qualunque file.

| escluso | perché |
|---|---|
| `lavoro/pt_crop.png` | è il ritaglio della planimetria catastale di una casa reale |
| `tavole/AA-01_M.03_*` (PDF e anteprima) | la M.03 ha come sfondo quella planimetria |
| `lavoro/riferimento_carichi_estivi.py` | porta la latitudine del sito; il calcolo dei carichi resta fuori dalla skill |
| `lavoro/skill-orig/` | la skill 1.4.1, che è già nella storia del repository e in `releases/` |

Gli originali restano nello ZIP del PO. Per questo `rifai.sh` e `pianta.py` non girano da qui: la M.03 si rifà nel suo
pacchetto, su una planimetria che non sia di un cliente (I-229). I file non sono stati toccati: i rimandi a `skill-orig`,
a `pt_crop.png` e alla M.03 nel `RAPPORTO.md`, nel `LEGGIMI.md` e negli script sono quelli originali.
