# REL-024 — La 2.0: la skill che si consegna ai progettisti

> **Scritto il 6 novembre 2026**, dopo la 1.15.0. Il PO: «per me la 2.0 è consolidamento. Voglio iniziare a
> distribuirla ai miei progettisti. fino adesso l'ho usata solo io» (I-295). La skill non cambia mestiere: cambia
> chi la usa. Fino alla 1.15.0 l'ha usata una persona sola, che conosce ogni decisione; dalla 2.0 la usano
> progettisti che non hanno letto niente di questo repository.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CORSO** — fase 1 avviata il 6 novembre 2026. `REL-023` è sospeso (`docs/plans/pacchetti/REL-023.md`).
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

## Le decisioni che sono del PO (si chiedono, non si prendono)

- **Il repository è pubblico** e porta le fatture dell'installatore della commessa PR.BG.017, il riferimento dei
  1.700 € e i costi del corredo (`skill/distinta/LISTINO-MINUTERIA.md`). Prima di distribuire: resta pubblico, diventa
  privato, o i prezzi escono dal repository e dalla skill?
- **Che cosa vedono i progettisti dei costi**: la distinta con `--costo` (in `interno/`) va a tutti o resta al PO?
- **Come si distribuisce**: sul piano Team di claude.ai il proprietario dell'organizzazione può fornire la skill a tutti
  da Impostazioni dell'organizzazione, ed è attiva per tutti; in alternativa un membro la condivide con persone
  scelte (fonte: centro d'aiuto di claude.ai, «Provision and manage skills for your organization», letto il 6
  novembre 2026; i nomi dei menu sono cambiati di recente e si verificano sul posto).
- **La skill `nove-c-report`**, da cui dipende il PDF della distinta: si distribuisce insieme?
- **Dove arrivano i rilievi dei progettisti** e chi li porta in sessione.

## Fuori

Nessuna capacità nuova: l'anello revisore → pianificatore (`DRAW-016` punti 2 e 3), l'espansione diretta e il VRV, le
famiglie di `docs/DEFERRED.md` §1, il corredo standard di `REL-023` sono delle 2.x.

## Criteri di accettazione, per ogni PR

Le tavole per prime; suite a 0 failed senza skip o xfail nuovi; la CI verde; nessun dato di cliente nuovo nel diff;
`tests/test_le_release.py` verde se c'è una release. Per la 2.0.0: le cinque fasi chiuse, ciascuna con il comando e il
suo output nel rapporto (`docs/collaudi/REL-024/RAPPORTO.md`).
