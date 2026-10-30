# REL-016 — I tre rilievi del collaudo della 1.7.0

> **▶ Il pacchetto attivo, per l'ordine del PO** — «si fondi e procedi con REL-016» (I-237), dopo la spiegazione dei
> rilievi D1, D3, D4 del collaudo indipendente della 1.7.0 e la proposta di farli prima di `REL-011`. Scritto il 30
> ottobre 2026, sulla 1.7.1.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **COSTRUITA SUL RAMO, AL PO** — la 1.8.0 aspetta il suo sì sulle tavole.
**Base:** `main` dopo la PR #82 (la 1.7.1).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147).
**Dopo:** `REL-011` (`docs/plans/pacchetti/REL-011.md`).

---

## Perché

Il collaudo indipendente della 1.7.0 (`docs/collaudi/REL-015/collaudo-1.7.0/RAPPORTO.md`) ha usato solo lo ZIP su due
impianti inventati. Tre rilievi si incontrano appena la skill lavora su offerte vere; i casi del collaudo sono in
`docs/collaudi/REL-016/casi-del-collaudo/`.

## Le cose da fare

### 1. Una tavola aggrovigliata non si consegna (D1)

Con i raccordi posati nell'ordine inverso a quello della tratta e il gruppo di riempimento non girato, la villetta del
collaudo esce col ritorno che scavalca sé stesso e il defangatore su una piega — e `disegna` dice «rilievi bloccanti
0» (`villetta-piano-groviglio.json`).

- **Il controllo**: quello che la tavola aggrovigliata mostra a occhio diventa un rilievo bloccante, misurato. Prima
  di tutto la tratta che scavalca sé stessa; poi, se reggono sul banco, l'organo in linea su una piega e gli altri che
  il collaudo ha visto. Un controllo nuovo bloccante **non deve fermare nessuna tavola già approvata**: si misura sul
  banco delle 24 tavole idroniche e sulle tavole di riferimento dell'aria.
- **Comporre**: `pezzi` dice in che ordine i pezzi stanno lungo ciascuna tratta, e `comporre.md` chiede di posarli in
  quell'ordine.

### 2. Il collettore di zona a più vie (D3)

Il collettore di zona a coppia (`zone-manifold-pair`) ha due vie; un collettore a pavimento a 6 vie oggi non si
disegna. Il collettore con N vie (da 2 a 12, una mandata e un ritorno per via), come il plenum da 2 a 6 uscite: catalogo,
simbolo, `capire.md`. **Il simbolo è una convenzione grafica del PO**: si propone sulla tavola.

### 3. Le domande della distinta al passo 2 (D4)

Quando il progettista vuole la distinta, le domande che le servono — marca e modello, refrigerante e precarica,
bocchette, attacco della condensa, protezioni, portate, lunghezze e sezioni dei cavi — si fanno **nello stesso giro**
delle domande del disegno, non dopo il primo lancio. La prova: sul trilocale del collaudo, con le risposte date al
passo 2, la distinta esce senza voci «DA DEFINIRE» salvo quelle che il progettista lascia aperte di proposito.

### 4. La release

**1.8.0**, con `scripts/costruisci-skill.py` e `tests/test_le_release.py` verde (D-200).

## Perimetro

**Dentro:** `src/**`, `assets/symbols/**`, `examples/**`, `rules/**`, `skill/**`, `tests/**`, `schemas/**`,
`scripts/costruisci-skill.py`, `docs/collaudi/REL-016/`, `releases/`, il registro, il registro delle decisioni (come
proposte), `HANDOFF.md`, questo file.

**Fuori:** un contenuto MEP o una convenzione grafica decisi dalla sessione; i dati del cliente, in qualunque file.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole per prime**, al PO: la villetta aggrovigliata che ora si ferma, il collettore a più vie.
1. **La suite**: `0 failed`; nessuno `skip` e nessuno `xfail` nuovi; `ruff check src tests` verde.
2. **La regressione**: il banco `docs/collaudi/REL-011/banco.py` fra `main` e il ramo; nessuna tavola approvata con un
   bloccante nuovo; ogni tavola cambiata spiegata.
3. **Ogni correzione ha la sua prova**, rossa sul commit di partenza.
4. **Gli input del PO nel registro** il giorno in cui arrivano.
5. **Nessun dato di cliente nel diff**.
6. **La release**: `tests/test_le_release.py` verde.
