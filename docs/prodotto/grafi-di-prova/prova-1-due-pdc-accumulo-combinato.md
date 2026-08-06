# Il grafo dell'impianto

> **Cosa approvi qui.** L'impianto — Due pompe di calore in parallelo con accumulo combinato —
> scritto invece che disegnato: ogni pezzo con la propria sigla, ogni tubazione
> fra due pezzi, e la passeggiata che parte dalle sorgenti e segue l'acqua fino a
> dove il giro si richiude.
>
> **Perche' non un disegno.** Un disegno prova come l'impianto e' stato messo sul
> foglio. Qui la domanda e' un'altra: **il pezzo giusto e' nel punto giusto, sul
> tubo giusto?** Quella si legge, non si guarda. E con una sigla per pezzo puoi
> correggere puntando — «questo qui e' nel posto sbagliato» — invece di
> descrivere a parole dove guardare.

---

## Come si legge

- **Ogni pezzo e' un nodo** con la propria sigla, macchine e accessori allo stesso
  modo. Le sigle che hai gia' scritto tu restano come le hai scritte.
- **Ogni tubazione fra due pezzi e' un arco**, e porta il proprio fluido.
- **Ogni attacco e' un braccio numerato**, come in un incrocio stradale: un volano
  a quattro attacchi e' un nodo solo con quattro bracci, contati nell'ordine in cui
  il pezzo li dichiara.
- **Un braccio su cui convergono piu' tubazioni e' un incrocio**, e le tubazioni che
  ci arrivano si contano.
- **Non e' un albero, e' un anello.** Un circuito si chiude su se' stesso: dove
  succede, la lettura lo dice e non si interrompe.

---

## Da dove si comincia a contare

Non dall'ordine in cui il modello elenca i pezzi, che e' un fatto di come e'
scritto e non dell'impianto: **dalle sorgenti**, seguendo il fluido. La prima
valvola che si incontra uscendo dal generatore e' la numero uno della sua
famiglia. Sono sorgenti chi il calore lo produce e il punto da cui l'acqua entra
nell'edificio; si riconoscono da cio' che ogni pezzo dichiara di saper fare, mai
da un elenco di nomi — un impianto con una caldaia al posto della pompa di calore
comincia esattamente allo stesso modo.

Qui si parte da:

- **PDC-01** Pompa di calore aria-acqua, sull'acqua di riscaldamento
- **PDC-02** Pompa di calore aria-acqua, sull'acqua di riscaldamento
- **AF-01** Alimentazione acqua fredda, sull'acqua fredda sanitaria

**Costo di questa scelta, detto subito:** se domani si aggiunge un pezzo vicino a
una sorgente, i numeri della sua famiglia a valle scalano tutti di uno. E' normale
per un documento che si rigenera a ogni revisione; cio' che non cambia mai e' che
lo stesso impianto dia sempre le stesse sigle, comunque sia scritto il modello che
lo descrive.

---

## Le famiglie delle sigle

La sigla di un pezzo dice a quale famiglia appartiene, e la famiglia si legge dal
mestiere che quel pezzo dichiara di fare — mai dal suo nome. Aggiungere una
famiglia vuol dire aggiungere una riga a una tabella, non toccare il programma.

| Sigla | Famiglia |
|---|---|
| **ACC** | Accumulo inerziale — sigla che hai scelto tu nel modello |
| **ACS** | Allacciamento — sigla che hai scelto tu nel modello |
| **AF** | Allacciamento — sigla che hai scelto tu nel modello |
| **CIR** | Circolatore |
| **DEF** | Defangatore |
| **DER** | Derivazione |
| **FIL** | Filtro |
| **GR** | Gruppo di riempimento |
| **MN** | Manometro |
| **PDC** | Generatore di calore — sigla che hai scelto tu nel modello |
| **RAD** | Terminale di emissione — sigla che hai scelto tu nel modello |
| **RC** | Raccordo |
| **SA** | Separatore d'aria |
| **SC** | Attacco di scarico |
| **TM** | Termometro |
| **VE** | Vaso di espansione |
| **VI** | Valvola di intercettazione |
| **VIB** | Valvola di intercettazione bloccabile aperta |
| **VM** | Valvola miscelatrice |
| **VS** | Valvola di sicurezza |

---

## I nodi

Nell'ordine in cui la passeggiata li incontra, che e' l'ordine in cui sono stati
numerati.

| Sigla | Che cos'e' | Su quale fluido |
|---|---|---|
| **PDC-01** | Pompa di calore aria-acqua | acqua di riscaldamento |
| **DER-01** | Derivazione a T | acqua di riscaldamento |
| **DER-02** | Derivazione a T | acqua di riscaldamento |
| **VI-01** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-02** | Valvola di intercettazione | acqua di riscaldamento |
| **SA-01** | Separatore d'aria | acqua di riscaldamento |
| **VI-03** | Valvola di intercettazione | acqua di riscaldamento |
| **RC-01** | Raccordo a T | acqua di riscaldamento |
| **VI-04** | Valvola di intercettazione | acqua di riscaldamento |
| **ACC-01** | Accumulo combinato · tiene in serbo acqua di riscaldamento | acqua di riscaldamento, acqua fredda sanitaria, acqua calda sanitaria |
| **VI-05** | Valvola di intercettazione | acqua di riscaldamento |
| **RC-02** | Ripartizione a T | acqua di riscaldamento |
| **DER-03** | Derivazione a T | acqua di riscaldamento |
| **VI-06** | Valvola di intercettazione | acqua di riscaldamento |
| **FIL-01** | Filtro a Y | acqua di riscaldamento |
| **VI-07** | Valvola di intercettazione | acqua di riscaldamento |
| **DEF-01** | Defangatore | acqua di riscaldamento |
| **VI-08** | Valvola di intercettazione | acqua di riscaldamento |
| **DER-04** | Derivazione a T | acqua di riscaldamento |
| **DER-05** | Derivazione a T | acqua di riscaldamento |
| **VI-09** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-10** | Valvola di intercettazione | acqua di riscaldamento |
| **MN-01** | Manometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VIB-01** | Valvola di intercettazione bloccabile aperta | acqua di riscaldamento |
| **VE-01** | Vaso di espansione · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VI-11** | Valvola di intercettazione | acqua di riscaldamento |
| **GR-01** | Gruppo di riempimento · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **FIL-02** | Filtro a Y | acqua di riscaldamento |
| **DEF-02** | Defangatore | acqua di riscaldamento |
| **VI-12** | Valvola di intercettazione | acqua di riscaldamento |
| **PDC-02** | Pompa di calore aria-acqua | acqua di riscaldamento |
| **DER-06** | Derivazione a T | acqua di riscaldamento |
| **DER-07** | Derivazione a T | acqua di riscaldamento |
| **VI-13** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-14** | Valvola di intercettazione | acqua di riscaldamento |
| **SA-02** | Separatore d'aria | acqua di riscaldamento |
| **VI-15** | Valvola di intercettazione | acqua di riscaldamento |
| **TM-01** | Termometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VS-01** | Valvola di sicurezza · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VI-16** | Valvola di intercettazione | acqua di riscaldamento |
| **FIL-03** | Filtro a Y | acqua di riscaldamento |
| **DEF-03** | Defangatore | acqua di riscaldamento |
| **VI-17** | Valvola di intercettazione | acqua di riscaldamento |
| **CIR-01** | Pompa di circolazione | acqua di riscaldamento |
| **VI-18** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-19** | Valvola di intercettazione | acqua di riscaldamento |
| **RAD-01** | Radiatore | acqua di riscaldamento |
| **VI-20** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-21** | Valvola di intercettazione | acqua di riscaldamento |
| **SC-01** | Attacco di scarico · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **TM-02** | Termometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VS-02** | Valvola di sicurezza · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **AF-01** | Alimentazione acqua fredda | acqua fredda sanitaria |
| **VI-22** | Valvola di intercettazione | acqua fredda sanitaria |
| **VI-23** | Valvola di intercettazione | acqua fredda sanitaria |
| **VI-24** | Valvola di intercettazione | acqua calda sanitaria |
| **VM-01** | Valvola miscelatrice termostatica | acqua calda sanitaria |
| **VI-25** | Valvola di intercettazione | acqua calda sanitaria |
| **ACS-01** | Utenze sanitarie | acqua calda sanitaria |

---

## Gli incroci

Nessuno: su questo impianto ogni attacco porta una sola tubazione.

---

## La passeggiata

Si parte da ogni sorgente e si segue il fluido, un pezzo alla volta. Dove
l'impianto si dirama, la lettura dice su quali bracci prosegue. Dove torna su un
pezzo gia' incontrato dice quale delle due cose e' successa — **il giro si
richiude**, perche' un circuito e' un anello, oppure **ci si innesta** un giro che
si era gia' letto — e in nessuno dei due casi si interrompe. Ogni tubazione
dell'impianto compare esattamente una volta.

### Si parte da PDC-01, sull'acqua di riscaldamento

**PDC-01** Pompa di calore aria-acqua e' una sorgente: generatore di calore. Da qui l'acqua di riscaldamento entra nell'impianto.

Da **PDC-01** Pompa di calore aria-acqua la lettura prosegue su 2 bracci: braccio 1 e braccio 2.

*Circuito primario*

1. **PDC-01** Pompa di calore aria-acqua · braccio 1 → **DER-01** Derivazione a T · braccio 1
    - da **DER-01** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
2. **DER-01** Derivazione a T · braccio 2 → **DER-02** Derivazione a T · braccio 1
    - da **DER-02** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
3. **DER-02** Derivazione a T · braccio 2 → **VI-01** Valvola di intercettazione · braccio 1
4. **VI-01** Valvola di intercettazione · braccio 2 → **VI-02** Valvola di intercettazione · braccio 1
5. **VI-02** Valvola di intercettazione · braccio 2 → **SA-01** Separatore d'aria · braccio 1
6. **SA-01** Separatore d'aria · braccio 2 → **VI-03** Valvola di intercettazione · braccio 1
7. **VI-03** Valvola di intercettazione · braccio 2 → **RC-01** Raccordo a T · braccio 1
    - da **RC-01** Raccordo a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
8. **RC-01** Raccordo a T · braccio 3 → **VI-04** Valvola di intercettazione · braccio 1
9. **VI-04** Valvola di intercettazione · braccio 2 → **ACC-01** Accumulo combinato · braccio 1
    - da **ACC-01** Accumulo combinato la lettura prosegue su altri 4 bracci: braccio 2, braccio 3, braccio 4 e braccio 8
10. **ACC-01** Accumulo combinato · braccio 2 → **VI-05** Valvola di intercettazione · braccio 1
11. **VI-05** Valvola di intercettazione · braccio 2 → **RC-02** Ripartizione a T · braccio 1
    - da **RC-02** Ripartizione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
12. **RC-02** Ripartizione a T · braccio 2 → **DER-03** Derivazione a T · braccio 1
    - da **DER-03** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
13. **DER-03** Derivazione a T · braccio 2 → **VI-06** Valvola di intercettazione · braccio 1
14. **VI-06** Valvola di intercettazione · braccio 2 → **FIL-01** Filtro a Y · braccio 1
15. **FIL-01** Filtro a Y · braccio 2 → **VI-07** Valvola di intercettazione · braccio 1
16. **VI-07** Valvola di intercettazione · braccio 2 → **DEF-01** Defangatore · braccio 1
17. **DEF-01** Defangatore · braccio 2 → **VI-08** Valvola di intercettazione · braccio 1
18. **VI-08** Valvola di intercettazione · braccio 2 → **DER-04** Derivazione a T · braccio 1
    - da **DER-04** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
19. **DER-04** Derivazione a T · braccio 2 → **DER-05** Derivazione a T · braccio 1
    - da **DER-05** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
20. **DER-05** Derivazione a T · braccio 2 → **VI-09** Valvola di intercettazione · braccio 1
21. **VI-09** Valvola di intercettazione · braccio 2 → **PDC-01** Pompa di calore aria-acqua · braccio 2 · **qui il giro si richiude su PDC-01**
22. **DER-05** Derivazione a T · braccio 3 → **VI-10** Valvola di intercettazione · braccio 1
23. **VI-10** Valvola di intercettazione · braccio 2 → **MN-01** Manometro · braccio 1
24. **DER-04** Derivazione a T · braccio 3 → **VIB-01** Valvola di intercettazione bloccabile aperta · braccio 1
25. **VIB-01** Valvola di intercettazione bloccabile aperta · braccio 2 → **VE-01** Vaso di espansione · braccio 1
26. **DER-03** Derivazione a T · braccio 3 → **VI-11** Valvola di intercettazione · braccio 1
27. **VI-11** Valvola di intercettazione · braccio 2 → **GR-01** Gruppo di riempimento · braccio 1
28. **RC-02** Ripartizione a T · braccio 3 → **FIL-02** Filtro a Y · braccio 1
29. **FIL-02** Filtro a Y · braccio 2 → **DEF-02** Defangatore · braccio 1
30. **DEF-02** Defangatore · braccio 2 → **VI-12** Valvola di intercettazione · braccio 1
31. **VI-12** Valvola di intercettazione · braccio 2 → **PDC-02** Pompa di calore aria-acqua · braccio 2
32. **PDC-02** Pompa di calore aria-acqua · braccio 1 → **DER-06** Derivazione a T · braccio 1
    - da **DER-06** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
33. **DER-06** Derivazione a T · braccio 2 → **DER-07** Derivazione a T · braccio 1
    - da **DER-07** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
34. **DER-07** Derivazione a T · braccio 2 → **VI-13** Valvola di intercettazione · braccio 1
35. **VI-13** Valvola di intercettazione · braccio 2 → **VI-14** Valvola di intercettazione · braccio 1
36. **VI-14** Valvola di intercettazione · braccio 2 → **SA-02** Separatore d'aria · braccio 1
37. **SA-02** Separatore d'aria · braccio 2 → **VI-15** Valvola di intercettazione · braccio 1
38. **VI-15** Valvola di intercettazione · braccio 2 → **RC-01** Raccordo a T · braccio 2 · **qui il giro si richiude su RC-01**
39. **DER-07** Derivazione a T · braccio 3 → **TM-01** Termometro · braccio 1
40. **DER-06** Derivazione a T · braccio 3 → **VS-01** Valvola di sicurezza · braccio 1

*Circuito secondario*

41. **ACC-01** Accumulo combinato · braccio 3 → **VI-16** Valvola di intercettazione · braccio 1
42. **VI-16** Valvola di intercettazione · braccio 2 → **FIL-03** Filtro a Y · braccio 1
43. **FIL-03** Filtro a Y · braccio 2 → **DEF-03** Defangatore · braccio 1
44. **DEF-03** Defangatore · braccio 2 → **VI-17** Valvola di intercettazione · braccio 1
45. **VI-17** Valvola di intercettazione · braccio 2 → **CIR-01** Pompa di circolazione · braccio 1
46. **CIR-01** Pompa di circolazione · braccio 2 → **VI-18** Valvola di intercettazione · braccio 1
47. **VI-18** Valvola di intercettazione · braccio 2 → **VI-19** Valvola di intercettazione · braccio 1
48. **VI-19** Valvola di intercettazione · braccio 2 → **RAD-01** Radiatore · braccio 1
49. **RAD-01** Radiatore · braccio 2 → **VI-20** Valvola di intercettazione · braccio 1
50. **VI-20** Valvola di intercettazione · braccio 2 → **VI-21** Valvola di intercettazione · braccio 1
51. **VI-21** Valvola di intercettazione · braccio 2 → **ACC-01** Accumulo combinato · braccio 4 · **qui il giro si richiude su ACC-01**

*Circuito primario*

52. **ACC-01** Accumulo combinato · braccio 8 → **SC-01** Attacco di scarico · braccio 1
53. **DER-02** Derivazione a T · braccio 3 → **TM-02** Termometro · braccio 1
54. **DER-01** Derivazione a T · braccio 3 → **VS-02** Valvola di sicurezza · braccio 1

### Si parte da PDC-02, sull'acqua di riscaldamento

**PDC-02** Pompa di calore aria-acqua e' una sorgente: generatore di calore. Da qui l'acqua di riscaldamento entra nell'impianto.

Da **PDC-02** Pompa di calore aria-acqua la lettura prosegue su 2 bracci: braccio 1 e braccio 2.

Da qui non riparte niente che non sia gia' stato letto: il suo giro compare piu' su.


### Si parte da AF-01, sull'acqua fredda sanitaria

**AF-01** Alimentazione acqua fredda e' una sorgente: allacciamento. Da qui l'acqua fredda sanitaria entra nell'impianto.

*Acqua fredda sanitaria*

1. **AF-01** Alimentazione acqua fredda · braccio 1 → **VI-22** Valvola di intercettazione · braccio 1
2. **VI-22** Valvola di intercettazione · braccio 2 → **VI-23** Valvola di intercettazione · braccio 1
3. **VI-23** Valvola di intercettazione · braccio 2 → **ACC-01** Accumulo combinato · braccio 5 · **qui ci si innesta su ACC-01**, che si e' gia' letto

### Si riparte da ACC-01, sull'acqua calda sanitaria

Attraversando **ACC-01** Accumulo combinato il fluido cambia nome: quello che esce di qui e' acqua calda sanitaria, e il suo giro si legge a parte.

*Acqua calda sanitaria*

1. **ACC-01** Accumulo combinato · braccio 6 → **VI-24** Valvola di intercettazione · braccio 1
2. **VI-24** Valvola di intercettazione · braccio 2 → **VM-01** Valvola miscelatrice termostatica · braccio 1
3. **VM-01** Valvola miscelatrice termostatica · braccio 2 → **VI-25** Valvola di intercettazione · braccio 1
4. **VI-25** Valvola di intercettazione · braccio 2 → **ACS-01** Utenze sanitarie · braccio 1

---

## Quello che il grafo non tace

Le cose che un elenco muto lascerebbe scoprire in cantiere.

**Attacchi liberi:** nessuno. Ogni attacco di ogni pezzo porta la sua
tubazione.

**Pezzi che nessuna sorgente raggiunge:** nessuno. Partendo dalle sorgenti si
arriva a ogni pezzo dell'impianto.

**Tubazioni non lette:** nessuna. Ogni tubazione compare nella passeggiata.

**Punti aperti:** nessuno. Per ogni accessorio che le regole hanno chiesto, il
catalogo aveva il pezzo adatto al fluido di quella tubazione.

---

## Cosa ti stiamo chiedendo

Di scorrere la passeggiata e dirci, per ogni pezzo: **e' quello giusto, ed e' nel
punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito sbagliato
si vede da qui, senza aprire nient'altro — e per segnalarcelo basta la sigla.
