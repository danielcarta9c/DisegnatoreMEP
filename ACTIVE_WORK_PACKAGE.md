# REL-015 — La distinta in un documento a parte, la tavola in A3, l'elettrico dopo l'idraulica

> **▶ Il pacchetto attivo, per l'ordine del PO** — «si fondi la 1.6.0 e procedi con la 1.7.0» (I-234), sulle sue
> osservazioni alla 1.6.0 (I-230 … I-233). Scritto il 30 ottobre 2026, sulla 1.6.0.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **COSTRUITA SUL RAMO, AL PO** — la 1.7.0 aspetta il suo sì sulle tavole e sul PDF della distinta.
**Base:** `main` dopo la PR #80 (la 1.6.0).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole e il PDF della distinta (D-146, D-147).
**Dopo:** `REL-011` (le tre proposte sul manuale Shenling e il dubbio sul vaso, `docs/plans/pacchetti/REL-011.md`).

---

## Perché

Il PO ha guardato le tavole della 1.6.0: «In generale va tutto bene» (I-230), con quattro osservazioni.

1. **La centrale va alimentata tutta, con le sonde della pompa di calore** (I-230): «anche la pdc va alimentata
   ovviamente poi ci sono le sonde della psc che vanno nei bollitori e volano ecc. comunque nel manuale Shenling c'è
   tutto».
2. **Prima l'idronico e l'aeraulico, poi l'elettrico e il comando** (I-231): «Non vorrei che le linee elettriche
   facciano spostare le linee idrauliche. Un collettore aveva una forma strana le tubazioni.»
3. **La distinta in un PDF a parte** (I-232): «Non foglio Excel meglio documento pdf con copertina e impaginazione
   generata con la skill report di nove c (senza kpi di copertina e senza la sezione chi siamo).»
4. **Sulla tavola solo la tabella delle apparecchiature e la legenda** (I-233), così i disegni «stanno in a3 più
   facilmente».

## Le cose da fare

### 1. La tavola: apparecchiature e legenda, nient'altro (I-233)

- Tabella delle tratte, note e computo escono dal foglio: vanno nel PDF della distinta. Il flusso della skill non
  riserva più le zone (`zone_tabelle`) e non passa `--tabelle`; il motore le tiene come capacità, non usata dal flusso.
- La M.02 di riferimento e il canalizzato del collaudo T3 rifatti: devono uscire in **A3** (o dire perché no).
- `SKILL.md`, `comporre.md`, `distinta.md` allineati.

### 2. La distinta in PDF con la skill dei report Nove C (I-232)

- Il documento: copertina senza KPI (`KPI_DATA` vuoto, verificato sul codice della skill `nove-c-report` rev9), senza
  «Chi siamo»; capitoli: l'impianto e le avvertenze (a corpo, quantità indicative, sopralluogo obbligatorio, fornitura
  da confermare), le tratte con diametri e lunghezze, il computo per sezioni, le attività a corpo, le varianti, le
  opere del committente, le voci da definire e le domande; niente dati interni, niente prezzi.
- **Niente Excel.**
- **Come**: la Disegnatore MEP prepara il contenuto; il PDF lo costruisce il motore della skill `nove-c-report`,
  installata accanto, importato dal suo percorso — **non si copia nel repository**, che è pubblico (assunzione detta al
  PO il 30 ottobre, non contraddetta). Se la skill dei report non c'è, la distinta lo dice e scrive il contenuto in
  Markdown.
- Il controllo finale della skill dei report (`fill_report`, `qa_pdf`, la verifica a vista delle pagine) si fa sempre.

### 3. Prima l'idraulica, poi l'elettrico (I-231)

- **La prova**: su una tavola unica, la parte idronica e aeraulica — tubazioni, pezzi **e sigle** — è identica alla
  stessa tavola nella vista `idraulica`. Oggi le tubazioni lo sono già; le sigle no (VMR-01, CIR-01, la sonda si
  spostano). Le sigle si posano con l'acqua, i cavi e le loro scritte dopo, nello spazio che resta.
- **Il collettore con il ritorno a barrette** (`zone-manifold-pair`), visto dal PO e dal collaudo T2: si disegna come un
  collettore, con il ritorno continuo. Cambia le tavole idroniche che lo usano: al PO, prima e dopo.

### 4. La pompa di calore alimentata, con le sue sonde (I-230)

- Dal **manuale Shenling ThermaX R290 6–15 kW** (OneDrive del PO, connettore Microsoft 365; non entra nel repository):
  che cosa alimenta e che cosa comanda la scheda della macchina — le sonde del bollitore e del volano, la valvola a tre
  vie, i circolatori, il bus — con la pagina. Il contenuto MEP è del PO: si mostra, si propone.
- Le porte di comando della pompa di calore che servono (sonde, uscite), facoltative come le altre; la tavola
  dell'elettrico di una centrale con le sonde della macchina.

### 5. La release

**1.7.0**, con `scripts/costruisci-skill.py` e `tests/test_le_release.py` verde (D-200); un collaudo indipendente sullo
ZIP prima della PR.

## Perimetro

**Dentro:** `src/**`, `assets/symbols/**`, `examples/**`, `naming/**`, `rules/**`, `skill/**`, `tests/**`, `schemas/**`,
`scripts/costruisci-skill.py`, `docs/collaudi/REL-015/`, `releases/`, il registro, il registro delle decisioni (come
proposte), `HANDOFF.md`, questo file.

**Fuori:** il motore della skill `nove-c-report` (si usa, non si copia); i manuali dei costruttori e la specifica
tecnica Nove C (si citano con la pagina); i dati del cliente, in qualunque file; un contenuto MEP o una convenzione
grafica decisi dalla sessione.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole e il PDF della distinta, per primi**, al PO.
1. **La suite**: `0 failed`; nessuno `skip` e nessuno `xfail` nuovi; `ruff check src tests` verde.
2. **La regressione**: il banco `docs/collaudi/REL-011/banco.py` fra `main` e il ramo; ogni tavola cambiata spiegata
   (il collettore cambia apposta).
3. **Ogni correzione ha la sua prova**, rossa sul commit di partenza.
4. **Gli input del PO nel registro** il giorno in cui arrivano.
5. **Nessun dato di cliente nel diff**, e nessuna pagina dei manuali.
6. **La release**: `tests/test_le_release.py` verde — la skill si carica (D-200).
