# I cinque grafi, prima e dopo — 7 agosto 2026

> **Cosa c'è qui.** I tuoi cinque impianti, rigenerati con le regole nuove del regime
> della centrale, messi a confronto con i grafi di ieri. Le versioni di ieri restano
> archiviate nella storia del progetto: qui vedi che cosa è cambiato, impianto per
> impianto.

> **Aggiornamento del 7 settembre 2026 (DRAW-005).** I conteggi «a N pezzi» qui sotto
> sono quelli di oggi, dopo la regola dell'isolamento per gruppo (scheda 7 di
> `REGOLE_ACCESSORI.md`, su tua indicazione — I-034): la macchina e il filtro sul suo
> ritorno sono un gruppo che si chiude dall'esterno, un rubinetto per tratto di tubo, e
> i rubinetti in fila sullo stesso volume sono spariti. Le descrizioni impianto per
> impianto restano quelle del 7 agosto e dicono che cosa era cambiato allora; i numeri
> di partenza («da N») sono quelli dei grafi del 6 agosto. Rispetto al 7 agosto:
> impianto 1, 45 pezzi allora e 39 oggi; impianto 2, 54 e 46; impianto 3, 48 e 44;
> impianto 4, 52 e 43; impianto 5, 108 e 98. I grafi rigenerati stanno accanto a questo
> documento; la tavola rifatta è la sola dell'impianto 1 (D-116).

> **Aggiornamento del 9 settembre 2026 (DRAW-005-R1, I-046).** I conteggi «a N pezzi»
> sono quelli di oggi, dopo la tua correzione sulla sicurezza: nella piccola centrale la
> sicurezza è **una per circuito**, sulla mandata dove le mandate sono già una, attaccata
> alla confluenza — non una per generatore e non più sul serbatoio. È la sicurezza del
> 7 settembre spostata, non moltiplicata. Rispetto al 7 settembre: impianto 1, 39 pezzi
> allora e 39 oggi (la sicurezza si è spostata dall'ingresso dell'accumulo alla mandata
> comune); impianto 2, 46 e 46; impianto 3, 44 e 44 (in tutti e due la sicurezza sta
> sulla mandata della macchina sola, che è la mandata comune); impianto 4, 43 e 41 —
> l'ibrido perde la sicurezza sul volume tecnico e non ne riceve una sulla mandata
> comune, perché sulla mandata la camminata si ferma alla deviatrice della caldaia e la
> mandata comune non si trova: sono i suoi tre punti aperti, sotto; impianto 5, 98 e 98 —
> sopra i 35 kW le sicurezze per macchina c'erano già e restano.

> **Aggiornamento del 9 settembre 2026 (DRAW-006).** I conteggi «a N pezzi» qui sotto
> sono quelli di oggi, dopo tre correzioni tue sulla semantica dei componenti (I-048,
> I-049, I-050). **Il manometro** ha il proprio rubinetto portamanometro a tre vie sulla
> presa, al posto della valvola di intercettazione generica: un pezzo al posto di un
> altro, il conto non cambia. **Il gruppo di riempimento** incorpora la propria
> intercettazione e non ne riceve più una esterna: un pezzo in meno per impianto.
> **La deviatrice** dichiara i propri stati idraulici, e la sicurezza si conta per
> dominio di protezione invece che per rete intera. Rispetto al 9 settembre (DRAW-005-R1):
> impianto 1, 39 pezzi allora e 38 oggi; impianto 2, 46 e 45; impianto 3, 44 e 43;
> impianto 4, 41 e 42 — l'ibrido **riceve** la sicurezza di circuito sul dominio che un
> tratto comune ce l'ha, con il suo raccordo di derivazione, e perde la valvola del
> riempimento; impianto 5, 98 e 97. L'elaborato rifatto è la sola tavola 2 (I-050): la
> tavola 1 resta una regressione automatica e non viene riconsegnata.

---

## Perché sono cambiati

Tre correzioni, tutte tue, tutte riscontrate sugli schemi dei costruttori prima di
scrivere le regole:

1. **Il regime della centrale.** Sotto i 35 kW niente separatore d'aria, niente
   termometro aggiunto, niente sicurezza per ogni macchina: sfogo aria e sicurezza
   stanno sul serbatoio, e stop. Il regime lo **leggiamo dalle potenze che hai scritto
   tu**, testo per testo — il conto è in fondo a questa pagina. Quattro impianti stanno
   sotto la soglia, la cascata di tre macchine sopra.
2. **Il ritorno generale.** Vaso, riempimento, manometro e defangatore stanno sul
   tratto comune del ritorno, prima che si divida verso le macchine — non più sul ramo
   della prima macchina. Il defangatore è **uno per circuito**: con due o tre macchine
   in parallelo niente più doppioni. Il filtro a Y resta uno per generatore, sul suo
   ritorno, ed esce dai circolatori.
3. **Lo scarico del bollitore.** Va da dove la riserva si riempie: l'ingresso
   dell'acqua fredda. Prima finiva sull'uscita calda, ed era un difetto trovato dal
   controllo indipendente.

---

## Impianto per impianto

**1 — Due pompe di calore e accumulo combinato: da 59 a 39 pezzi.**
Escono i due separatori d'aria, i due termometri e una delle due sicurezze; il
defangatore passa da tre a uno, sul ritorno generale prima della ripartizione verso le
due macchine; i filtri a Y restano due, uno per macchina, e il circolatore perde il suo;
entra lo sfogo aria sull'attacco dedicato dell'accumulo, e la sicurezza superstite sta
sull'accumulo. Vaso, riempimento e manometro stanno adesso sul tratto comune, non più
sul ramo della prima macchina.

**2 — Pompa di calore con deviatrice e bollitore: da 58 a 41 pezzi.**
Escono separatore, termometro e il defangatore doppio; entra lo sfogo sul volano; la
sicurezza sta sul volano. Lo scarico del bollitore si sposta dall'uscita calda
all'ingresso dell'acqua fredda.

**3 — Pompa di calore diretta su pavimento: da 55 a 39 pezzi.**
Stesse uscite del regime piccolo (separatore, termometro), sfogo e sicurezza sul volano
in linea, e lo scarico del boiler sull'ingresso freddo.

**4 — Ibrido pompa di calore e caldaia: da 68 a 43 pezzi.**
Il ritorno generale è il tratto fra il volume tecnico e il punto in cui il ritorno si
divide verso le due macchine: lì stanno vaso, riempimento, manometro e l'unico
defangatore. Ogni generatore tiene il suo filtro a Y; sfogo e sicurezza sul volano;
escono i due separatori, i due termometri e una sicurezza. **Sul circuito sanitario non
c'è filtro**, come è giusto in un impianto domestico.

**5 — Cascata di tre pompe di calore: da 105 a 93 pezzi.**
È l'unico dei cinque **sopra i 35 kW** — tre macchine da 35, e non è una centrale
domestica — quindi tiene il corredo da grande centrale: sicurezza e termometro per ogni
macchina, e il separatore d'aria sulla mandata generale. I cinque defangatori diventano
uno solo sul ritorno generale della cascata, un filtro a Y per macchina, e lo scarico del
bollitore passa sull'ingresso freddo.

**Ma la correzione grossa di questo impianto è un'altra, ed è una nostra lettura
sbagliata rimessa a posto.** Il tuo testo dice che dal volume tecnico partono **tre**
circuiti secondari — batterie delle UTA, fan-coil, e un circuito miscelato per il
pavimento radiante — e non nomina nessun collettore. Noi ne avevamo disegnati **due**,
perché avevamo supposto un collettore, e quel collettore aveva due sole uscite: il
circuito del pavimento radiante era rimasto fuori, e ti era stata portata come domanda
una cosa che il tuo testo non aveva mai detto. **Il circuito del pavimento adesso c'è**,
con la sua valvola miscelatrice e il suo circolatore, e il collettore non c'è più: dove
tre tubi si incontrano mettiamo due raccordi, che è la regola generale e non richiede di
supporre un pezzo che non hai nominato. Di qui i pezzi in più rispetto a ieri, non da un
irrigidimento delle regole.

**Ogni punto aperto è una domanda su un dato che non abbiamo, mai un pezzo perso.**
Uno solo dei cinque non ne ha nessuno; gli altri quattro ne hanno **uno a testa**, e
ciascuno chiede una cosa sola.

L'ibrido (impianto 4) chiede della **sicurezza**. Dal 9 settembre 2026 (DRAW-006) la
deviatrice dichiara i propri stati idraulici: l'ingresso va su un ramo oppure sull'altro,
mai su tutti e due. La pompa di calore, che alla mandata comune ci arriva comunque stia la
deviatrice, **riceve** la sicurezza di circuito del proprio dominio; la caldaia, che in
uno degli stati ammessi la deviatrice manda allo scambiatore sanitario, è un dominio a sé,
e per lei il catalogo non dice se la sicurezza sta dentro il mantello.

Gli impianti 2, 3 e 5 chiedono del **vaso di espansione sanitario**. Dal 10 settembre 2026
(DRAW-006-R1) non lo aggiungiamo al buio: molti accumuli sanitari lo portano già dentro il
mantello, e il catalogo del tuo può tacere. Dove tace, la domanda è per te — una riga, e
il vaso si posa o si lascia stare.

---

## Il regime: letto dai testi, non chiesto a te

I tuoi testi dichiarano le potenze, e la soglia è quella che hai dato: 35 kW. Sommare e
confrontare non è dimensionare — il dato è tuo, la soglia è tua, il conto è aritmetica.
Quindi il regime lo leggiamo, e lo scriviamo dove tu lo possa vedere e correggere:

| | Cosa dice il testo | Regime |
|---|---|---|
| 1 | due pompe di calore da 12 kW | 24 kW — sotto |
| 2 | una pompa di calore da 15 kW | sotto |
| 3 | una pompa di calore da 8 kW | sotto |
| 4 | pompa di calore 10 kW + caldaia 24 kW | 34 kW — sotto |
| 5 | tre pompe di calore da 35 kW | 105 kW — **sopra** |

Se un testo le potenze non le desse, allora sì che sarebbe una domanda per te: il regime
resterebbe non dichiarato e l'impianto prenderebbe il corredo minimo.
