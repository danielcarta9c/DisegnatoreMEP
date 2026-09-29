"""Che cosa ha fatto un agente in camera pulita: i comandi della skill e i file letti (REL-001).

Legge la trascrizione di un agente — il file JSONL che l'ambiente di sviluppo scrive per
ogni agente lanciato in sessione — e ne tira fuori, nell'ordine:

- **ogni comando `mep.py`** che l'agente ha eseguito, con il codice d'uscita e la riga
  finale dell'uscita: e' la prova del criterio 6, che **i controlli sono della skill** —
  li lancia lei, non la sessione (I-166);
- **ogni file che ha aperto** con lo strumento di lettura, e ogni comando che nomina un
  percorso fuori dalla camera: e' la prova che la camera era pulita.

E' uno strumento di sessione. Uso:

    python docs/collaudi/REL-001/comandi_della_camera.py <trascrizione.jsonl> <cartella-della-camera>
"""

import json
import re
import sys
from pathlib import Path


def _testo(contenuto: object) -> str:
    if isinstance(contenuto, str):
        return contenuto
    if isinstance(contenuto, list):
        return "\n".join(
            parte.get("text", "") for parte in contenuto if isinstance(parte, dict) and parte.get("type") == "text"
        )
    return ""


def leggi(trascrizione: Path) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    chiamate: list[dict[str, object]] = []
    risultati: dict[str, dict[str, object]] = {}
    for riga in trascrizione.read_text(encoding="utf-8").splitlines():
        voce = json.loads(riga)
        messaggio = voce.get("message")
        if not isinstance(messaggio, dict) or not isinstance(messaggio.get("content"), list):
            continue
        for parte in messaggio["content"]:
            if not isinstance(parte, dict):
                continue
            if parte.get("type") == "tool_use":
                chiamate.append({"id": parte["id"], "strumento": parte["name"], "ingresso": parte.get("input", {})})
            elif parte.get("type") == "tool_result":
                risultati[parte["tool_use_id"]] = {
                    "testo": _testo(parte.get("content")),
                    "errore": bool(parte.get("is_error")),
                }
    return chiamate, risultati


def main() -> None:
    trascrizione, camera = Path(sys.argv[1]), str(Path(sys.argv[2]).resolve())
    chiamate, risultati = leggi(trascrizione)
    print("## I comandi della skill\n")
    numero = 0
    for chiamata in chiamate:
        ingresso = chiamata["ingresso"]
        comando = ingresso.get("command", "") if isinstance(ingresso, dict) else ""
        if chiamata["strumento"] != "Bash" or "mep.py" not in str(comando):
            continue
        numero += 1
        esito = risultati.get(str(chiamata["id"]), {"testo": "", "errore": False})
        testo = str(esito["testo"]).strip()
        # Gli agenti spesso stampano da se' il codice (`; echo EXIT=$?`): se c'e', vale quello.
        codice = re.search(r"EXIT[=: ]+(\d+)", testo) or re.search(r"Exit code (\d+)", testo)
        uscita = codice.group(1) if codice else ("?" if esito["errore"] else "0")
        righe = [
            r for r in testo.splitlines()
            if r.strip() and not r.startswith("Exit code") and not re.fullmatch(r"\s*EXIT[=: ]+\d+\s*", r)
        ]
        sottocomando = re.search(r"mep\.py\s+(\w+)", str(comando))
        print(
            f"{numero}. `{sottocomando.group(1) if sottocomando else '?'}` — uscita {uscita} — "
            f"{(righe[-1] if righe else '').strip()[:160]}"
        )
    print("\n## I file aperti\n")
    fuori = []
    for chiamata in chiamate:
        ingresso = chiamata["ingresso"] if isinstance(chiamata["ingresso"], dict) else {}
        percorso = ingresso.get("file_path") or ingresso.get("path")
        if chiamata["strumento"] in ("Read", "Glob", "Grep") and percorso:
            print(f"- {chiamata['strumento']}: {percorso}")
            if not str(percorso).startswith(camera):
                fuori.append(str(percorso))
        comando = str(ingresso.get("command", ""))
        for trovato in re.findall(r"(?:^|(?<=[\s\"'=(]))(/[\w./-]+)", comando):
            if trovato.startswith("/") and not trovato.startswith(camera) and not trovato.startswith(
                ("/dev/", "/tmp/mep", "/mnt/user-data")
            ) and len(trovato) > 4:
                fuori.append(f"(nel comando) {trovato}")
    print("\n## Fuori dalla camera\n")
    print("\n".join(f"- {f}" for f in sorted(set(fuori))) or "- niente")


if __name__ == "__main__":
    main()
