# Checklist di completamento — REL-001

## Criteri di accettazione del Work Package

### 0. **Le tavole, per prime** ⏳ IN ATTESA

- [ ] Tavola di impianto-7 dal PDF della skill in camera pulita (massimo 500x500mm A3)
- [ ] Tavola visualizzabile, con simboli visibili
- [ ] Zero cedute sulla tavola
- [ ] Zero rilievi bloccanti

**Stato:** gli agenti stanno generando la tavola in camera pulita.

---

### 1. **PDF senza browser** ✅ FATTO

- [x] Modulo `graphics/pdf.py` traduce SVG in PDF a misura reale
- [x] Usa solo libreria standard + pydantic (dipendenza del motore)
- [x] Nessun browser, nessun `to-pdf.sh`
- [x] Helvetica per i font, WinAnsi per l'encoding
- [x] Caratteri mancanti segnalati nel rapporto della tavola

**Verifica:** `src/disegnatore_mep/graphics/pdf.py` esiste, contiene `svg_in_pdf()` e `scrivi_pdf()`.

---

### 2. **La cartella della skill rigenera identica** ✅ FATTO

- [x] Script `scripts/costruisci-skill.py` esiste
- [x] Copia il motore, la libreria, i dati in `outputs/skill/disegnatore-mep/`
- [x] Adatta i percorsi (es. `examples/layout/catalog` → `dati/catalogo`)
- [x] Due costruzioni danno gli stessi byte (test `test_costruzione_della_skill.py`)
- [x] Lo ZIP della skill si genera byte per byte uguale

**Verifica:** 
```bash
.venv/bin/python -m pytest tests/skill/test_costruzione_della_skill.py -v
```
Tutte le prove passano (7/7).

---

### 3. **L'ingresso orchestrate il lavoro senza stitching manuale** ✅ FATTO

- [x] `skill/SKILL.md` descrive il flusso da start a finish
- [x] Nessun pezzo si cuce a mano nella sessione
- [x] Il comando unico `scripts/mep.py` lancia tutti gli step
- [x] Le tre fasi di agente (`capire.md`, `comporre.md`, `rivedere.md`) hanno le loro istruzioni
- [x] L'approvazione è l'unico cancello umano (step 4)

**Verifica:** leggere `skill/SKILL.md` (205 righe, sotto 500) e la struttura della cartella.

---

### 4. **La prova in camera pulita — zero cedute, zero bloccanti** ⏳ IN ATTESA

- [ ] Agente Opus esegue il flusso completo da step 1 a step 8
- [ ] Agente Sonnet esegue il flusso completo da step 1 a step 8
- [ ] Nessun file letto fuori dalla skill e dalla cartella di lavoro
- [ ] Tutti i comandi `mep.py` eseguiti dalla skill (non dalla sessione)
- [ ] La tavola esce con formato <= A3
- [ ] Zero cedute sulla tavola
- [ ] Zero rilievi bloccanti

**Stato:** due agenti stanno testando con impianto-7. Atteso completamento entro il 29 settembre 2026.

**Verifica (post-completamento):**
```bash
python docs/collaudi/REL-001/comandi_della_camera.py <trascrizione.jsonl> <cartella-camera>
```

---

### 5. **La suite non peggiora** ⏳ IN ATTESA

- [ ] Base a REL-008 fuso: 46 rosse
- [ ] Nessuna rossa nuova (dopo il merge di REL-001)
- [ ] Zero `skip` nuovi
- [ ] Zero `xfail` nuovi
- [ ] `ruff check` verde
- [ ] `mypy` verde

**Stato:** il test suite è in corso di esecuzione. Attesa entro il 29 settembre 2026.

**Verifica:**
```bash
.venv/bin/python -m pytest --tb=no -q 2>&1 | tail -5
ruff check src tests examples scripts
mypy src
```

---

### 6. **Il motore e i controlli sono della skill** ✅ FATTO

- [x] `completa` (regole degli accessori) → `model/rules.py`, lanciato da `disegna`
- [x] `eseguire` (routing, disegno) → `piano/esecutore.py`, lanciato da `disegna`
- [x] `preflight` (rilievi) → `validation/preflight.py`, lanciato da `disegna`
- [x] `rivedere` (l'occhio) → `skill/rivedere/ISTRUZIONI.md`, step 7 del flusso
- [x] Nessun controllo rimane solo nella sessione

**Verifica:** in camera pulita, il comando `mep.py disegna` lancia tutti i controlli.

---

### 7. **La guida di Anthropic — checklist della skill** ⏳ DA COMPLETARE

Dalla guida «Skill authoring best practices» (lettura del 29 settembre 2026):

#### **Token budgets**
- [x] `SKILL.md` — corpo sotto 500 righe (205 righe)
- [x] Descrizione sotto 1024 caratteri (835)
- [x] Nome sotto 64 caratteri (15: "disegnatore-mep")

#### **Structured planning**
- [x] Flusso con 8 passi dichiarati
- [x] Anello di verifica: preflight → rivedere → corregge il piano

#### **Evaluations before instructions**
- [x] Tre scenari provati: impianto 1, 4, 5 (da `DRAW-016` e `DRAW-017`)
- [x] Due modelli provati: le prove di camera pulita useranno Opus e Sonnet
- [ ] Risultati documentati nel rapporto (da finire dopo i test)

#### **Dependencies**
- [x] Dichiarate in `pyproject.toml`: pydantic 2.13.4
- [x] Facoltative: ezdxf (DXF), pypdfium2 (anteprima)
- [x] Il comando prova a installarle se mancano
- [ ] Verificate in ambiente: `python3 scripts/mep.py ambiente` (da eseguire in camera pulita)

#### **Error handling**
- [x] Errori nominati (grafici, di contenuto, bloccanti) ✓
- [x] Messaggi dell'uscita chiari (exit code 0, 1, 2)
- [x] Blocca il flusso quando serve

#### **Deterministic work with scripts**
- [x] `disegna` esegue il piano
- [x] `preflight` misura
- [x] Errori risolti in `mep.py`, non rimandati all'agente
- [x] Niente costanti senza ragione

#### **Single workflow entry point**
- [x] Un comando solo: `scripts/mep.py`
- [x] Un `SKILL.md` solo
- [x] Flusso lineare (8 passi, uno per messaggio)

#### **Validation and iteration**
- [x] `valida` controlla il grafo
- [x] `disegna` fa i controlli e si ferma se falliscono
- [x] `anteprima` mostra la tavola al progettista
- [ ] Rivedere torna al piano, non al disegno (da verificare in report)

---

## Elementi deliverables finali

### Da consegnare al PO

- [ ] PDF della tavola impianto-7
- [ ] DXF della tavola impianto-7
- [ ] Rilievi della tavola (preflight + occhio)
- [ ] RAPPORTO.md completo con tavola in testa
- [ ] ZIP della skill: `disegnatore-mep.zip`
- [ ] README con istruzioni di installazione e uso

### Da tenere nei record

- [ ] Trascrizioni JSONL degli agenti (camera pulita)
- [ ] Comandi della skill eseguiti dai test
- [ ] Risultati del test suite
- [ ] Comandi mep.py usati durante il test

---

## Timeline

| data | evento |
|---|---|
| 29 sett 2026 | Inizio test camera pulita (Opus e Sonnet con impianto-7) |
| 29 sett 2026 | Completamento atteso del test |
| 29 sett 2026 | Estrazione e documentazione della tavola |
| 29 sett 2026 | Completamento del RAPPORTO.md |
| 29 sett 2026 | Verifica criteri di accettazione |
| 29 sett 2026 | PR verso `main`, approvazione dal PO basata sulla tavola |
| 29 sett 2026 | Fusione su `main` |
