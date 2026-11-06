# REL-024 — La 2.0: la skill che si consegna ai progettisti

> **Scritto il 6 novembre 2026**, dopo la 1.15.0. Il PO: «per me la 2.0 è consolidamento. Voglio iniziare a
> distribuirla ai miei progettisti. fino adesso l'ho usata solo io» (I-295). La skill non cambia mestiere: cambia
> chi la usa. Fino alla 1.15.0 l'ha usata una persona sola, che conosce ogni decisione; dalla 2.0 la usano
> progettisti che non hanno letto niente di questo repository.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CORSO** — **fase 1 chiusa** sul ramo della PR della 1.15.2: la CI e mypy (1.15.1, PR #92), il banco come prova e la skill senza rete (`docs/collaudi/REL-024/RAPPORTO.md`). Il prossimo: la fase 2.
**Base:** `main` dopo la 1.15.0 (PR #91).
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147), a ogni PR.
**Il numero:** le PR intermedie restano 1.x; la **2.0.0** esce solo dalla fase 5, dopo la prova del PO con i progettisti.

## Il punto di partenza (misurato il 6 novembre 2026 su `main`, la 1.15.0)

| controllo | esito |
|---|---|
| `pytest` | 2889 passed, 15 skipped, 11 xfailed |
| `ruff check src tests` | verde; `ruff check .` 59 errori negli script di `docs/collaudi/`; 258 file non formattati |
| `mypy` (strict, `pyproject.toml`) | **fermo sugli stub di numpy** prima di controllare; con `--python-version 3.13` **50 errori in 13 file** |
| CI | **assente**: in `.github/` c'è solo il modello della PR |
| build della skill | riproducibile: lo ZIP ricostruito ha lo sha256 di `releases/latest` (`56514abd…`), 150 file su 200 |
| tag git | nessuno |
| prova di fumo | lo ZIP della 1.15.0 in una cartella pulita, Python con il solo pydantic: T1 di `REL-023` dal grafo al PDF, A3, 0 cedute, 0 bloccanti; ezdxf **installato da PyPI al volo** |
| valutazioni della skill | le tre di `skill/evals/`, da `REL-001` (settembre): mai rifatte sulle release dopo |
| banco delle tavole | `docs/collaudi/REL-011/banco.py`: uno strumento di sessione, non una prova |
| `skill/SKILL.md` | 459 righe su 500 |

## Le cinque fasi

### Fase 1 — La messa in sicurezza (nessuna tavola cambia)

1. **La CI** su GitHub Actions, a ogni PR e su `main`: `pytest`, `ruff check src tests`, `mypy`, la costruzione della
   skill con `tests/test_le_release.py`. Una PR rossa non si fonde.
2. **`mypy` verde davvero**: la configurazione che non si ferma sugli stub di terzi, e i 50 errori corretti nel codice,
   non silenziati.
3. **Il banco diventa una prova**: le tavole di riferimento (i cinque impianti, la villetta, il T1) rifatte a ogni
   PR e confrontate con quelle registrate; una differenza non voluta è rossa, una voluta si registra con la tavola nella
   PR.
4. **La prova senza rete**: che cosa succede alla skill in un ambiente senza PyPI. O le dipendenze viaggiano nello ZIP
   dentro il limite dei 200 file, o la skill lo dice al progettista con un messaggio chiaro, prima di cominciare.

### Fase 2 — La prova dell'agente, che resta agli atti

5. **Sei impianti tipo in camera pulita**, con Opus e Sonnet, dal testo del progettista alla tavola: PdC piccola con
   volano e bollitore, cascata, ibrido caldaia + PdC, aria-aria, l'elettrico, il costruito. Testi scritti **come li
   scriverebbe un progettista che non conosce la skill**. Gli esiti — tavole, domande fatte, tempi — diventano il
   riferimento con cui si giudica ogni release successiva (`skill/evals/`).

### Fase 3 — Il debito di decisioni, chiuso col PO

6. Una per una, con la domanda e la proposta: D-225 (sospesa), D-236 (proposta fusa, da confermare), il contenuto di
   D-231; il glicole e il materiale sopra i 35 kW; le voci del canalizzato DA PREZZARE; il ritegno sul ricircolo; il
   gruppo di riempimento nei soli riscaldamento. Quello che il PO non decide va in «limiti noti», non resta muto.

### Fase 4 — La skill per chi non l'ha scritta

7. **La guida del progettista**: una pagina sola — che cosa chiedere, che cosa la skill domanda, che cosa consegna, che
   cosa non fa mai, i modelli che funzionano (non Haiku).
8. **I limiti noti** e le **note di release leggibili** (che cosa cambia per chi disegna, senza I- e D-).
9. **I documenti interni riallineati**: `PROJECT_STATE.md` (fermo alla 1.5), `docs/ARCHITETTURA-DEL-PIANO.md` (il pezzo
   3 dato per inesistente), `HANDOFF.md` accorciato davvero.
10. **`skill/SKILL.md`** sotto le 400 righe, con il dettaglio nei riferimenti, per lasciare spazio alle 2.x.

### Fase 5 — La release candidate

11. **2.0.0-rc1** consegnata dal PO a due o tre progettisti su commesse vere; i loro rilievi raccolti in un posto solo;
    le correzioni; la **2.0.0** con il tag git, la release su GitHub, `releases/latest/`. Poi la potatura dei rami
    vecchi (una quarantina, già fusi).

### Un difetto della distinta, dal progetto reale (I-297)

12. **FATTO** (1.15.2) — **`compreso_in` vale per ogni pezzo, non solo per le macchine.** Oggi toglie soltanto la riga della sezione A
    (`src/disegnatore_mep/distinta/calcolo.py`, `_apparecchiature`): un accessorio dichiarato compreso nella pompa di
    calore — il filtro a Y, i pozzetti — resta in distinta con il suo corredo. È un'uscita sbagliata su un dato che il
    progettista ha già dato: rientra nel consolidamento. Il resto di I-297 è la 2.1 (`docs/plans/pacchetti/REL-025.md`).

## Le decisioni del PO sulla distribuzione (I-296, 6 novembre 2026)

- **Il repository resta pubblico**, con i prezzi e le fatture della commessa PR.BG.017 («no problem»).
- **I progettisti vedono i costi** della distinta (`distinta --costo`).
- **La distribuzione, la skill `nove-c-report` e il canale dei rilievi dei progettisti li cura il PO**: la skill dei
  report l'hanno già tutti. Per la fase 5 resta da sapere, al momento della rc, chi la prova e dove arrivano i rilievi.

## Fuori

Nessuna capacità nuova (quelle di I-297 sono la 2.1, `REL-025`): l'anello revisore → pianificatore (`DRAW-016` punti 2 e 3), l'espansione diretta e il VRV, le
famiglie di `docs/DEFERRED.md` §1, il corredo standard di `REL-023` sono delle 2.x.

## Criteri di accettazione, per ogni PR

Le tavole per prime; suite a 0 failed senza skip o xfail nuovi; la CI verde; nessun dato di cliente nuovo nel diff;
`tests/test_le_release.py` verde se c'è una release. Per la 2.0.0: le cinque fasi chiuse, ciascuna con il comando e il
suo output nel rapporto (`docs/collaudi/REL-024/RAPPORTO.md`).
