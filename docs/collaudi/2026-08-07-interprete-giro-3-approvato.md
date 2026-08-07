# Collaudo indipendente del pezzo «Capire» — giro 3

**Data:** 7 agosto 2026 · **Collaudo:** a contesto separato, terzo giro
**Oggetto:** `skill/capire/ISTRUZIONI.md`, misurate sulle consegne in
`skill/capire/prova-2026-08-07/impianto-1..5/`
**Metro:** `examples/prova/prova-*.json` (letture manuali congelate, non toccate)
**Prove:** `tests/collaudo/test_collaudo_interprete.py`

---

## VERDETTO: **APPROVATO**

Nessun difetto che respinge. Su 67 componenti e 82 tubazioni, cinque impianti:
**zero perso, zero inventato**. Tutti e cinque i grafi attraversano il resto della
catena e producono un documento identico carattere per carattere anche rimescolando
l'ordine — compreso il quinto, che al giro 2 rompeva la catena.

Resta **un difetto aperto, minore, che non respinge**: la voce a2 del primo grafo cita
due identificativi interni del JSON in una frase destinata all'ingegnere. È inchiodato
come `xfail(strict=True)`.

---

## 1. Come ho lavorato

Ho scritto i criteri **prima** di aprire le consegne (§2 qui sotto). Poi ho riletto io i
cinque testi frase per frase contro i cinque grafi, **senza usare le tabelle di rilettura
degli agenti** — quelle sono parte di ciò che giudico. Ogni affermazione di questo
verbale è verificata da una prova che gira.

Le letture manuali non sono state toccate.

---

## 2. I criteri

Obbligatori dall'incarico (C1–C7) più i miei (C8–C17).

| | Criterio | Esito |
|---|---|---|
| C1 | Fedeltà ai cinque testi originali, rilettura mia | **passato** |
| C2 | Nessuna invenzione progettuale | **passato** |
| C3 | Nessuna informazione esplicita persa | **passato** |
| C4 | Domande solo quando necessarie (D-108) | **passato** |
| C5 | Regime ricavato dalle potenze, non chiesto | **passato** |
| C6 | Diramazioni a N vie ⇒ N−1 raccordi; i tre circuiti del quinto | **passato** |
| C7 | Determinismo del completatore e del documento finale | **passato** |
| C8 | Il file carica, forma del JSON, liste dei pezzi successivi vuote | **passato** |
| C9 | Coerenza col catalogo: attacchi, verso, un tubo per attacco, stub | **passato** |
| C10 | Nessun mestiere della «ferramenta» fra i componenti | **passato** |
| C11 | Reti: mai cominciate su un raccordo; fluidi coerenti | **passato** |
| C12 | Nessun componente staccato | **passato** |
| C13 | `tag` solo quelli scritti dall'ingegnere | **passato** |
| C14 | `properties`: nessun numero che il testo non scrive | **passato** |
| C15 | Voci dichiarate leggibili, senza identificativi interni | **1 difetto aperto (impianto 1)** |
| C16 | Voci dichiarate veritiere rispetto al grafo consegnato | **passato** |
| C17 | Confronto col metro e classificazione a quattro esiti | **passato** |

---

## 3. Il primo rilievo: l'esclusione dell'impianto 3 — **NON è un difetto**

La prova rossa era:

    test_le_esclusioni_esplicite_sono_dichiarate[3]
    esclusioni del testo non dichiarate ['non collegato idraulicamente']

**È un difetto della prova, non del grafo.** L'agente del giro 3 l'esclusione **l'ha
dichiarata**. Voce a7 del terzo grafo:

> «Il testo dice che la produzione di ACS è completamente separata e **non collegata
> idraulicamente** all'impianto di riscaldamento — e così è rappresentata: il boiler in
> pompa di calore non tocca il circuito di riscaldamento.»

Il testo del committente scrive «un boiler … **non collegato** idraulicamente»
(maschile, il soggetto è il boiler); l'agente scrive «la produzione … **non collegata**
idraulicamente» (femminile, il soggetto è la produzione). Stessa informazione, stesso
avvertimento a chi viene dopo, **una lettera di differenza**. La prova del giro 2
cercava la stringa secca e non l'ha trovata.

**Sul merito.** L'argomento «il grafo la mostra, quindi non serve dichiararla» non
regge, e ho lasciato la prova in piedi: un boiler staccato per distrazione e un boiler
staccato per prescrizione si disegnano **identici**. Solo la voce dichiarata dice al
pezzo che completa di non collegarlo. §4.5 ha ragione a pretenderla.

**Correzione fatta:** `ESCLUSIONI` ora porta espressioni regolari
(`non collegat[ao] idraulicamente`), con la motivazione scritta per esteso nel testo
della costante. La prova resta e resta severa.

---

## 4. I due casi che le istruzioni non coprono alla lettera

L'incarico chiede di giudicarli. Per ciascuno mi sono chiesto: **ha prodotto un grafo
sbagliato?**

### 4.1 La valvola deviatrice (segnalata dagli agenti 2, 4 e 5, senza vedersi)

§4.2 dice dove una rete comincia — da una macchina che la alimenta o da un confine, mai
da un raccordo — e che i rami che si staccano da una **ripartizione** restano nella rete
da cui nascono. Una **valvola deviatrice** non è nessuna delle due cose: §5 la mette fra
i pezzi di topologia, ma non alimenta niente. Alla lettera, il caso non è coperto.

**Giudizio: NON è un difetto che respinge. È un'imprecisione delle istruzioni.**

Tutti e tre i grafi che hanno una deviatrice — 2, 4, 5 — hanno tenuto i rami **dentro la
rete della macchina che li alimenta**; tutti e tre l'hanno dichiarato (voci a12, a11,
nessuna necessaria nel 5 perché non c'era dubbio); tutti e tre **combaciano con la
lettura manuale**, che risolve allo stesso modo e in silenzio. Nessun pezzo perso,
nessuno inventato, nessuna catena rotta. Le istruzioni sono imprecise; i grafi sono
giusti, e concordanti fra loro pur essendo scritti da tre agenti isolati.

Ho presidiato la lettura giusta con una prova nuova
(`test_la_valvola_deviatrice_non_apre_una_rete_nuova`), perché un giro futuro non la
cambi in silenzio: **tutte le tubazioni di una deviatrice stanno su una rete sola**.

### 4.2 Il regime quando solo alcune macchine dichiarano la potenza (agente 3)

L'impianto 3 ha **due** macchine che il catalogo classifica generatrici — la pompa di
calore aria-acqua e il boiler in pompa di calore — e il testo dà la potenza **solo della
prima** (8 kW); del boiler dà il volume (200 litri). §4.6 prevede due casi soli: il
testo dà le potenze, oppure non le dà. Questo non è né l'uno né l'altro.

**Giudizio: NON è un difetto. È il caso di mezzo, risolto bene.**

L'agente ha ricavato il regime dagli 8 kW scritti (`up_to_35_kw`) e **ha dichiarato la
lacuna** (voce a8: «Il boiler in pompa di calore produce calore anche lui, ma il testo
non ne dà la potenza … se una potenza va dichiarata anche per quello, il conto va
rifatto»). Le due alternative erano peggiori:

- omettere il campo avrebbe **buttato via** gli 8 kW che l'ingegnere ha scritto;
- chiedere il regime sarebbe stato chiedere un dato ricavabile — D-108 in pieno.

L'esito coincide con la lettura manuale. Ho presidiato la condotta con
`test_il_regime_esce_anche_quando_una_potenza_non_e_scritta`, che pretende tutte e tre
le cose insieme: il regime esce, il conto è scritto, la lacuna è dichiarata.

> **Nota di attribuzione.** Un altro collaudo, sul completatore, tiene lo stesso caso
> aperto come suo «difetto 4» in `test_collaudo_correzioni_fine_sessione.py`. Quel
> collaudo giudicava le **letture manuali**, che non dichiaravano niente; qui la voce
> c'è. Sono due rilievi diversi sullo stesso punto delle istruzioni. Sul giro 3 il
> comportamento è corretto e dichiarato.

---

## 5. La tabella di classificazione, impianto per impianto

Confronto sulle **reti** (dominio e fluido), sui **componenti** (voce di catalogo) e
sulle **tubazioni** (attacco con attacco, su quale rete). Sigle e sottosistemi fuori per
costruzione.

| Impianto | Reti | Componenti | Tubazioni | Differenze dal metro | Esito |
|---|---|---|---|---|---|
| 1 — due PdC + accumulo combinato | 4 = 4 | 9 = 9 | 11 = 11 | **nessuna** | — |
| 2 — PdC con deviatrice ACS | 4 = 4 | 9 = 9 | 11 = 11 | **nessuna** | — |
| 3 — PdC diretta su pavimento | 3 = 3 | 9 = 9 | 9 = 9 | **nessuna** | — |
| 4 — ibrido PdC + caldaia | 4 = 4 | 12 = 12 | 15 = 15 | **nessuna** | — |
| 5 — tre PdC, tre secondari | 4 = 4 | 28 vs 29 | 36 vs 37 | il metro porta una **valvola di ritegno** sul ricircolo sanitario | **assunzione tacita della lettura manuale** (terzo esito) |

**Nessuna differenza cade nel primo esito (detto dal testo e perso).**
**Nessuna differenza cade nel secondo esito (inventato).**

La sola differenza, sul quinto impianto, è a carico del metro: `valve-check-dhw-hot` è
ferramenta (`non_return`), il testo non la nomina, e §5 la vieta alla prima stesura.
Il contratto §2 vieta di correggere il metro: la differenza si registra e basta.

Tolto il ritegno, i due grafi del quinto impianto **coincidono arco per arco, e sulle
reti con la loro molteplicità** — il confronto più stretto che il contratto ammette. Al
giro 2 il quinto grafo combaciava solo confrontando i fluidi, perché il lato secondario
era tagliato in quattro reti. Il §4.2 corretto ha chiuso anche quella.

### Il terzo esito, dalla parte opposta

Le **cinque letture manuali non portano nemmeno una `properties`**: potenze, volumi e
nome commerciale che l'ingegnere ha scritto, a mano si erano persi. I cinque grafi della
camera pulita li trascrivono tutti, come vuole §4.5. Non è una differenza da
classificare: è il pezzo 1 che lavora meglio della lettura a mano. Registrato con
`test_i_dati_dell_ingegnere_stanno_nel_grafo_e_non_nel_metro`.

Stesso discorso per le domande: 55 voci dichiarate in camera pulita contro 12 del metro.

---

## 6. Verifiche puntuali sui criteri più duri

**Regime (C5).** Ricavato in tutti e cinque, mai chiesto. 12+12=24 → sotto;
15 → sotto; 8 → sotto; 10+24=**34** → sotto, a un kW dalla soglia, e l'agente 4 lo
segnala; 3×35=105 → sopra. Tutti e cinque coincidono col metro.

**Raccordi N−1 (C6).** 2, 1, 1, 3, 12. Nessuno di troppo, nessuno di meno. Nessun
attacco porta due tubazioni in nessuno dei cinque grafi.

**I tre circuiti del quinto (C6).** Ci sono tutti e tre: batterie UTA (`ahu-coil`),
fan-coil (`fan-coil`), pavimento radiante miscelato (`underfloor-panel` +
`mixing-valve-3way`). Nessun collettore a due uscite. Tre circolatori, uno per circuito,
più quello del ricircolo sanitario. Il bypass che alimenta l'ingresso freddo della
miscelatrice è dichiarato (voce a8) ed è quello che fa anche il metro.

**Domande (C4).** Ho letto una per una tutte le 22 frasi interrogative delle 55 voci.
**Nessuna** chiede una potenza, un volume, una taglia, un diametro o una marca.
Nessuna chiede il regime. Tutte riguardano cose che il testo davvero non dice: con che
pezzo si fa il parallelo, su quale ramo sta il circolatore, quanti sono i terminali,
dove rientra un ritorno, se il primario ha circolatori esterni.
La domanda dell'agente 4 sul circolatore della caldaia è legittima: `gas-boiler` non
dichiara `carries_on_board`, quindi non è ricavabile né dal testo né dal catalogo.

**Invenzioni (C2, C14).** Ogni componente che non è un raccordo o un confine risale a
una parola del testo. Nessun valore numerico delle `properties` è assente dal testo del
proprio impianto. Nessun `tag` inventato: tutti `null` in tutti e cinque.

**Catena (C7, C12).** Nessun componente staccato. Nessuna rete dichiarata e mai usata.
Nessuna rete comincia su un raccordo. Il completatore non lascia punti aperti su nessuno
dei cinque, e il documento finale è invariante su 20 rimescolamenti — **compreso il
quinto**, che il collaudo del giro 2 aveva dovuto escludere.

**Consegna (contratto §1).** Tutte e cinque le tabelle di rilettura sono complete:
ogni componente, ogni tubazione e ogni voce dichiarata vi compare.

---

## 7. Il difetto aperto

### D — Identificativi interni in una voce destinata all'ingegnere (impianto 1)

`CONSEGNA.md` §1 punto 2 vuole l'elenco delle domande in «italiano piano, **niente
identificativi interni**, ogni voce comprensibile da sola». La voce a2 del primo grafo
finisce così:

> «… nel grafo le due macchine non sono distinte fra loro **(pdc-1 e pdc-2 sono
> intercambiabili)**.»

`pdc-1` e `pdc-2` sono gli `id` di due componenti del JSON: nomi che l'ingegnere non ha
mai visto. Gli altri quattro grafi sono puliti.

**Perché non respinge.** Non è un pezzo perso né inventato: la classificazione del
contratto §2 non lo tocca. E la frase resta comprensibile anche senza la parentesi, che
ripete quello che la frase ha appena detto. È una regola scritta e violata, di forma.

**Riproducibile con:**

    .venv/bin/python -m pytest "tests/collaudo/test_collaudo_interprete.py::test_le_voci_dichiarate_non_portano_identificativi_interni" -q -rx

Inchiodato come `xfail(strict=True)` col motivo per esteso: quando il grafo si corregge,
la prova diventa rossa e va tolto il marcatore.

---

## 8. Osservazioni che non respingono

Segnalate perché tornino utili, non perché siano difetti.

1. **Due voci chiedono conferma di una lettura che il testo dà.** L'impianto 1 chiede
   «È la lettura giusta dell'ECOcombi?» e l'impianto 5 «Confermate la lettura [di "a
   quattro tubi"]?». In tutti e due i casi la lettura è quella giusta e il testo la dice.
   Non è una violazione di D-108 — non si chiede un **dato**, si chiede conferma di
   un'interpretazione che tocca una delle quattro cose del §9 — ma è il limite superiore
   di quanto si può chiedere.
2. **Una qualifica trascritta in un grafo e non nell'altro.** «L'impianto **esistente** a
   radiatori» compare in tutti e due i testi 1 e 4; l'agente 1 l'ha messa in
   `properties` (`stato: esistente`), l'agente 4 no. Non è nel confronto del contratto e
   non cambia il disegno.
3. **Le chiavi delle `properties` non hanno un vocabolario.** Fra i cinque grafi
   compaiono `potenza, volume, tipo, configurazione, modello, funzione, funzionamento,
   gestione, impiego, produzione, produzione_acs, stato`. Quattro agenti su cinque lo
   segnalano da soli. Finché nessuno a valle legge le `properties` **per chiave**, non
   fa danno.
4. **La derivazione a T è inutilizzabile.** §4.4 prescrive le derivazioni «dove il testo
   descrive qualcosa che si stacca da un tubo», ma nel catalogo tutte le voci
   `tee-branch*` hanno l'attacco `branch` marcato `stub: true`, e §4.3 vieta di
   collegarci qualsiasi cosa. Tre agenti l'hanno notato. Nessuno ne è stato danneggiato —
   dove serviva uno stacco hanno usato `tee-split`, che è corretto — ma la
   contraddizione fra istruzioni e catalogo è reale.
5. **`carries_on_board` non è mai nominato dalle istruzioni.** Due agenti hanno dedotto
   da soli che significa «il circolatore è dentro la macchina, non si disegna» e l'hanno
   dichiarato. Hanno dedotto giusto.

Nessuna di queste ha prodotto un grafo sbagliato. Non respingono.

---

## 9. Cosa lascio

`tests/collaudo/test_collaudo_interprete.py`, esteso e adottato come regressione.
**Girano verdi**: 147 passate, 1 `xfail(strict=True)`. `ruff check` pulito,
`mypy --strict` pulito.

**Una prova corretta:** `test_le_esclusioni_esplicite_sono_dichiarate` — confronto sulla
sostanza invece che sul carattere, motivo scritto nella costante `ESCLUSIONI`.

**Due prove strette:**
`test_quinto_impianto_topologia_identica_a_meno_del_ritegno` (ora confronta le reti con
la loro molteplicità, non più i soli fluidi) e `test_il_documento_finale_e_deterministico`
(ora su tutti e cinque gli impianti, non più sui primi quattro).

**Undici prove nuove**, sezione 6 del file: pezzi staccati, numeri inventati, fluidi
fuori tabella, reti vuote, la valvola deviatrice, il regime col dato parziale, il regime
contro il metro, le domande vietate da D-108, la tabella di classificazione scritta come
prova, i dati dell'ingegnere che il metro non ha, gli identificativi interni.

---

## 10. Attribuzione delle altre prove rosse della suite

Sulla suite intera: **7 rosse, 1027 verdi, 22 saltate, 12 `xfail`**. Nessuna delle rosse
riguarda l'interprete, e nessuna è causata da questo collaudo — che ha toccato un file
solo.

- 6 rosse (`test_p4_indirizzo_dei_nodi.py` ×4, `test_p5_regime_e_tratto_comune.py` ×2):
  l'artefatto pubblicato del quinto impianto, non ancora rigenerato.
- 1 rossa (`test_collaudo_correzioni_fine_sessione.py::test_nessun_documento_dice_piu_che_il_regime_non_si_ricava_dalle_potenze`):
  la frase vecchia di D-106 sopravvive in `docs/plans/2026-08-06-piano-costruzione-skill.md`.
- 11 `xfail` in `test_collaudo_correzioni_fine_sessione.py`: i difetti dell'altro
  collaudo, sul completatore.
- 1 `xfail` in `test_collaudo_interprete.py`: il difetto D di questo verbale.
