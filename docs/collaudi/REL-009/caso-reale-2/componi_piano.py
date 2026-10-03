"""Il piano del caso reale, come lo compone Comporre dopo I-201 … I-205.

    python3 docs/collaudi/REL-009/caso-reale-2/componi_piano.py

Scrive `piano.json` accanto a se'. Le scelte, e da dove vengono:

- **le macchine sulle quote delle autostrade** (D-159): la prima pompa di calore di ciascun
  gruppo e il suo volano allo stesso y, cosi' mandata e ritorno principali sono due rette;
- **i due raccordi del parallelo su due verticali accanto alle macchine** (B3), la mandata
  a sinistra e il ritorno a destra; fra le due verticali lo sfiato di ogni pompa di calore,
  che sale nel vuoto fra una macchina e l'altra e incrocia la sola mandata principale;
- **le pompe di zona parallele, con lo stesso verso** (I-204): la mandata del secondario
  arriva su un collettore verticale corto, e le due pompe stanno su due orizzontali verso
  destra, come nello schizzo del PO; il tratto verticale prima di ciascuna e' piu' corto di
  quanto una valvola chieda, e il motore le posa sull'orizzontale;
- **le dorsali della distribuzione come autostrade** (I-205): i ritorni delle zone tornano
  su una dorsale sotto le pompe; ogni zona ha le sue due colonne affiancate, il ritorno
  dentro e la mandata fuori (B12), cosi' la coppia gira senza incrociarsi;
- **i collettori in colonna e i terminali sotto la loro coppia**, girati con gli attacchi in
  alto (270 gradi e specchio): due linee dritte per terminale (I-205).
"""

import json
from pathlib import Path
from typing import Any

QUI = Path(__file__).resolve().parent

PASSO_PDC = 60.0
"""Fra una pompa di calore e la successiva: 30 di macchina e 30 per la sicurezza e lo sfiato
della seguente, che stanno nel vuoto fra le due."""
X_MANDATA = 95.0
"""La verticale che unisce le mandate del parallelo."""
X_SFIATO = 110.0
"""Lo sfiato di ogni pompa di calore: fra le due verticali, dove la mandata non c'e' piu'."""
X_RITORNO = 140.0
"""La verticale che divide i ritorni del parallelo."""
X_VOLANO = 210.0

PASSO_COLLETTORE = 60.0
"""Collettore (15), discesa con la valvola (20), terminale (20), e 5 di aria."""


def _tee(x: float, quota: float) -> dict[str, float]:
    """Un raccordo centrato in x sulla linea alla quota data."""
    return {"x": x - 2.5, "y": quota - 2.5}


def componi() -> dict[str, Any]:
    pezzi: dict[str, dict[str, Any]] = {}

    def gruppo(generatori: list[str], y0: float, volano: str, unioni: list[str], divisioni: list[str], riempimento: str) -> None:
        """Un parallelo di pompe di calore col suo volano; la prima macchina e' quella della
        linea principale."""
        for indice, pdc in enumerate(generatori):
            y = y0 + indice * PASSO_PDC
            n = pdc.removeprefix("pdc-")
            pezzi[pdc] = {"x": 0, "y": y}
            pezzi[f"tee-valve-safety-{pdc}-water-supply"] = _tee(50, y + 5)
            pezzi[f"valve-safety-{pdc}-water-supply"] = {"x": 47.5, "y": y - 17.5}
            pezzi[f"tee-sfiato-{n}"] = _tee(X_SFIATO, y + 20)
            pezzi[f"sfiato-{n}"] = {"x": X_SFIATO - 2.5, "y": y - 15}
        # Le unioni della mandata e le divisioni del ritorno, dalla prima macchina in giu'.
        for indice, tee in enumerate(unioni):
            pezzi[tee] = _tee(X_MANDATA, y0 + 5 + indice * PASSO_PDC)
        for indice, tee in enumerate(divisioni):
            pezzi[tee] = _tee(X_RITORNO, y0 + 20 + indice * PASSO_PDC)
        pezzi[volano] = {"x": X_VOLANO, "y": y0, "regola": "D-159 — sulle quote della prima pompa di calore"}
        pezzi[f"sfiato-{volano}"] = {"x": X_VOLANO + 10, "y": y0 - 30}
        pezzi[f"tee-filling-unit-{riempimento}-b"] = _tee(152.5, y0 + 20)
        pezzi[f"filling-unit-{riempimento}"] = {"x": 150, "y": y0 + 32.5, "rotazione": 180}
        pezzi[f"inlet-filling-unit-{riempimento}"] = {"x": 150, "y": y0 + 52.5}

    gruppo(
        ["pdc-r1", "pdc-r2", "pdc-r3", "pdc-r4"], 0, "volano-risc",
        ["tj-pr-3", "tj-pr-2", "tj-pr-1"], ["ts-pr-3", "ts-pr-2", "ts-pr-1"], "ts-pr-3-a",
    )
    pezzi["drain-connection-volano-risc-primary-in"] = {"x": X_VOLANO + 10, "y": 55}

    # Il secondario del riscaldamento: ritorno con vaso e manometro, poi giu' sulla dorsale.
    pezzi["tee-pressure-gauge-tj-mz-b"] = _tee(255, 20)
    pezzi["pressure-gauge-tj-mz-b"] = {"x": 252.5, "y": 40, "rotazione": 180}
    pezzi["tee-expansion-connection-tj-mz-b"] = _tee(267.5, 20)
    pezzi["expansion-connection-tj-mz-b"] = {"x": 265, "y": 40}
    # La mandata e il ritorno del secondario restano sulle quote del volano fino alla
    # zona lontana: sono la sua coppia, dritta. La zona vicina prende la mandata da un
    # raccordo e scende sotto il ritorno, con la sua pompa su un orizzontale.
    pezzi["ts-mz"] = _tee(290, 5)
    zone = {
        # zona: (x della colonna interna, x di quella esterna, collettori, la colonna interna e' la mandata?)
        1: (345.0, 355.0, 3, True),
        2: (445.0, 455.0, 5, False),
    }
    for numero, (interna, esterna, collettori, mandata_dentro) in zone.items():
        mandata, ritorno = (interna, esterna) if mandata_dentro else (esterna, interna)
        x_collettore = esterna + 30
        for k in range(1, collettori + 1):
            y = 50 + (k - 1) * PASSO_COLLETTORE
            pezzi[f"coll-mz{numero}-{k}"] = {"x": x_collettore, "y": y}
            pezzi[f"fc-mz{numero}-{k}"] = {"x": x_collettore + 5, "y": y + 35, "rotazione": 270, "specchio": True}
            pezzi[f"rad-mz{numero}-{k}"] = {"x": x_collettore + 25, "y": y + 35, "rotazione": 270, "specchio": True}
            if k < collettori:
                pezzi[f"ts-mz{numero}-{k}"] = _tee(mandata, y + 2.5)
                pezzi[f"tj-mz{numero}-{k}"] = _tee(ritorno, y + 12.5)
    # Il ritorno della zona vicina entra nella dorsale dove la sua colonna la incontra.
    pezzi["tj-mz"] = _tee(zone[1][1], 20)
    # La coppia della zona lontana scende in colonna: il primo raccordo di ciascuna
    # colonna si gira a mano (C2), perche' il vicino da cui arriva — il raccordo delle
    # pompe — sta a sinistra, e dedotto il raccordo prenderebbe la coppia di lato.
    pezzi["ts-mz2-1"] |= {"rotazione": 90}
    pezzi["tj-mz2-1"] |= {"rotazione": 90, "specchio": True}

    # Il gruppo dell'acqua calda sanitaria, sotto.
    y_acs = 400.0
    gruppo(["pdc-a1", "pdc-a2"], y_acs, "volano-acs", ["tj-pa"], ["ts-pa"], "ts-pa-a")
    pezzi["drain-connection-volano-acs-aux-in"] = {"x": X_VOLANO + 10, "y": y_acs + 55}
    pezzi["solare-mandata"] = {"x": 245, "y": y_acs + 25}
    pezzi["solare-ritorno"] = {"x": 245, "y": y_acs + 35}
    pezzi["tee-expansion-connection-volano-acs-secondary-in"] = _tee(292.5, y_acs + 20)
    pezzi["expansion-connection-volano-acs-secondary-in"] = {"x": 290, "y": y_acs + 40}
    pezzi["tee-pressure-gauge-volano-acs-secondary-in"] = _tee(305, y_acs + 20)
    pezzi["pressure-gauge-volano-acs-secondary-in"] = {"x": 302.5, "y": y_acs + 40, "rotazione": 180}
    pezzi["bollitore"] = {"x": 420, "y": y_acs - 2.5, "regola": "la serpentina sulla quota del secondario"}
    pezzi["acquedotto"] = {"x": 315, "y": y_acs + 32.5}
    pezzi["tee-drain-connection-cold-bollitore-cold-in"] = _tee(357.5, y_acs + 35)
    pezzi["drain-connection-cold-bollitore-cold-in"] = {"x": 355, "y": y_acs + 50}
    pezzi["tee-expansion-connection-dhw-bollitore-cold-in"] = _tee(402.5, y_acs + 35)
    pezzi["expansion-connection-dhw-bollitore-cold-in"] = {"x": 400, "y": y_acs + 57.5}
    pezzi["mixing-valve-thermostatic-bollitore-dhw-out"] = {"x": 422.5, "y": y_acs - 40, "rotazione": 270}
    pezzi["inlet-mixing-valve-thermostatic-bollitore-dhw-out"] = {"x": 450, "y": y_acs - 40}
    pezzi["utenze-acs"] = {"x": 425, "y": y_acs - 70}
    pezzi["ricircolo-utenze"] = {"x": 500, "y": y_acs + 7.5}

    return {
        "formato": "A1",
        "note": [
            "Il caso reale ricostruito (caso-reale-2), composto dopo I-201 … I-205: autostrade "
            "prima, pompe di zona parallele, dorsali della distribuzione come autostrade, "
            "collettori con i terminali sotto la loro coppia.",
        ],
        "pezzi": pezzi,
    }


if __name__ == "__main__":
    uscita = QUI / "piano.json"
    uscita.write_text(json.dumps(componi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(uscita)
