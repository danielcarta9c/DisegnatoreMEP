# Il grafo dell'impianto

> **Cosa approvi qui.** L'impianto — Sistema ibrido con pompa di calore e caldaia a condensazione —
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

- **CAL-01** Caldaia a condensazione, sull'acqua di riscaldamento
- **PDC-01** Pompa di calore aria-acqua, sull'acqua di riscaldamento
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
| **ACS** | Allacciamento — sigla che hai scelto tu nel modello |
| **AF** | Allacciamento — sigla che hai scelto tu nel modello |
| **CAL** | Generatore di calore — sigla che hai scelto tu nel modello |
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
| **SCA** | Scambiatore di calore |
| **TM** | Termometro |
| **VD** | Valvola deviatrice |
| **VE** | Vaso di espansione |
| **VI** | Valvola di intercettazione |
| **VIB** | Valvola di intercettazione bloccabile aperta |
| **VOL** | Accumulo inerziale |
| **VS** | Valvola di sicurezza |

---

## I nodi

Nell'ordine in cui la passeggiata li incontra, che e' l'ordine in cui sono stati
numerati.

| Sigla | Che cos'e' | Su quale fluido |
|---|---|---|
| **CAL-01** | Caldaia a condensazione | acqua di riscaldamento |
| **DER-01** | Derivazione a T | acqua di riscaldamento |
| **DER-02** | Derivazione a T | acqua di riscaldamento |
| **VI-01** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-02** | Valvola di intercettazione | acqua di riscaldamento |
| **SA-01** | Separatore d'aria | acqua di riscaldamento |
| **VI-03** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-04** | Valvola di intercettazione | acqua di riscaldamento |
| **VD-01** | Valvola deviatrice a tre vie | acqua di riscaldamento |
| **VI-05** | Valvola di intercettazione | acqua di riscaldamento |
| **RC-01** | Raccordo a T | acqua di riscaldamento |
| **VI-06** | Valvola di intercettazione | acqua di riscaldamento |
| **VOL-01** | Volano termico a quattro attacchi · tiene in serbo acqua di riscaldamento | acqua di riscaldamento |
| **VI-07** | Valvola di intercettazione | acqua di riscaldamento |
| **RC-02** | Ripartizione a T | acqua di riscaldamento |
| **DER-03** | Derivazione a T | acqua di riscaldamento |
| **VI-08** | Valvola di intercettazione | acqua di riscaldamento |
| **FIL-01** | Filtro a Y | acqua di riscaldamento |
| **VI-09** | Valvola di intercettazione | acqua di riscaldamento |
| **DEF-01** | Defangatore | acqua di riscaldamento |
| **VI-10** | Valvola di intercettazione | acqua di riscaldamento |
| **DER-04** | Derivazione a T | acqua di riscaldamento |
| **DER-05** | Derivazione a T | acqua di riscaldamento |
| **VI-11** | Valvola di intercettazione | acqua di riscaldamento |
| **PDC-01** | Pompa di calore aria-acqua | acqua di riscaldamento |
| **DER-06** | Derivazione a T | acqua di riscaldamento |
| **DER-07** | Derivazione a T | acqua di riscaldamento |
| **VI-12** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-13** | Valvola di intercettazione | acqua di riscaldamento |
| **SA-02** | Separatore d'aria | acqua di riscaldamento |
| **VI-14** | Valvola di intercettazione | acqua di riscaldamento |
| **TM-01** | Termometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VS-01** | Valvola di sicurezza · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VI-15** | Valvola di intercettazione | acqua di riscaldamento |
| **MN-01** | Manometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VIB-01** | Valvola di intercettazione bloccabile aperta | acqua di riscaldamento |
| **VE-01** | Vaso di espansione · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VI-16** | Valvola di intercettazione | acqua di riscaldamento |
| **GR-01** | Gruppo di riempimento · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **RC-03** | Raccordo a T | acqua di riscaldamento |
| **FIL-02** | Filtro a Y | acqua di riscaldamento |
| **DEF-02** | Defangatore | acqua di riscaldamento |
| **VI-17** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-18** | Valvola di intercettazione | acqua di riscaldamento |
| **SCA-01** | Scambiatore a piastre | acqua di riscaldamento, acqua fredda sanitaria, acqua calda sanitaria |
| **VI-19** | Valvola di intercettazione | acqua di riscaldamento |
| **DEF-03** | Defangatore | acqua di riscaldamento |
| **FIL-03** | Filtro a Y | acqua di riscaldamento |
| **VI-20** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-21** | Valvola di intercettazione | acqua di riscaldamento |
| **FIL-04** | Filtro a Y | acqua di riscaldamento |
| **DEF-04** | Defangatore | acqua di riscaldamento |
| **VI-22** | Valvola di intercettazione | acqua di riscaldamento |
| **CIR-01** | Pompa di circolazione | acqua di riscaldamento |
| **VI-23** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-24** | Valvola di intercettazione | acqua di riscaldamento |
| **RAD-01** | Radiatore | acqua di riscaldamento |
| **VI-25** | Valvola di intercettazione | acqua di riscaldamento |
| **VI-26** | Valvola di intercettazione | acqua di riscaldamento |
| **SC-01** | Attacco di scarico · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **TM-02** | Termometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **VS-02** | Valvola di sicurezza · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| **AF-01** | Alimentazione acqua fredda | acqua fredda sanitaria |
| **VI-27** | Valvola di intercettazione | acqua fredda sanitaria |
| **VI-28** | Valvola di intercettazione | acqua fredda sanitaria |
| **VI-29** | Valvola di intercettazione | acqua calda sanitaria |
| **VI-30** | Valvola di intercettazione | acqua calda sanitaria |
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

### Si parte da CAL-01, sull'acqua di riscaldamento

**CAL-01** Caldaia a condensazione e' una sorgente: generatore di calore. Da qui l'acqua di riscaldamento entra nell'impianto.

Da **CAL-01** Caldaia a condensazione la lettura prosegue su 2 bracci: braccio 1 e braccio 2.

*Circuito primario*

1. **CAL-01** Caldaia a condensazione · braccio 1 → **DER-01** Derivazione a T · braccio 1
    - da **DER-01** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
2. **DER-01** Derivazione a T · braccio 2 → **DER-02** Derivazione a T · braccio 1
    - da **DER-02** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
3. **DER-02** Derivazione a T · braccio 2 → **VI-01** Valvola di intercettazione · braccio 1
4. **VI-01** Valvola di intercettazione · braccio 2 → **VI-02** Valvola di intercettazione · braccio 1
5. **VI-02** Valvola di intercettazione · braccio 2 → **SA-01** Separatore d'aria · braccio 1
6. **SA-01** Separatore d'aria · braccio 2 → **VI-03** Valvola di intercettazione · braccio 1
7. **VI-03** Valvola di intercettazione · braccio 2 → **VI-04** Valvola di intercettazione · braccio 1
8. **VI-04** Valvola di intercettazione · braccio 2 → **VD-01** Valvola deviatrice a tre vie · braccio 1
    - da **VD-01** Valvola deviatrice a tre vie la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
9. **VD-01** Valvola deviatrice a tre vie · braccio 2 → **VI-05** Valvola di intercettazione · braccio 1
10. **VI-05** Valvola di intercettazione · braccio 2 → **RC-01** Raccordo a T · braccio 2
    - da **RC-01** Raccordo a T la lettura prosegue su altri 2 bracci: braccio 1 e braccio 3
11. **RC-01** Raccordo a T · braccio 3 → **VI-06** Valvola di intercettazione · braccio 1
12. **VI-06** Valvola di intercettazione · braccio 2 → **VOL-01** Volano termico a quattro attacchi · braccio 1
    - da **VOL-01** Volano termico a quattro attacchi la lettura prosegue su altri 4 bracci: braccio 2, braccio 3, braccio 4 e braccio 6
13. **VOL-01** Volano termico a quattro attacchi · braccio 2 → **VI-07** Valvola di intercettazione · braccio 1
14. **VI-07** Valvola di intercettazione · braccio 2 → **RC-02** Ripartizione a T · braccio 1
    - da **RC-02** Ripartizione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
15. **RC-02** Ripartizione a T · braccio 2 → **DER-03** Derivazione a T · braccio 1
    - da **DER-03** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
16. **DER-03** Derivazione a T · braccio 2 → **VI-08** Valvola di intercettazione · braccio 1
17. **VI-08** Valvola di intercettazione · braccio 2 → **FIL-01** Filtro a Y · braccio 1
18. **FIL-01** Filtro a Y · braccio 2 → **VI-09** Valvola di intercettazione · braccio 1
19. **VI-09** Valvola di intercettazione · braccio 2 → **DEF-01** Defangatore · braccio 1
20. **DEF-01** Defangatore · braccio 2 → **VI-10** Valvola di intercettazione · braccio 1
21. **VI-10** Valvola di intercettazione · braccio 2 → **DER-04** Derivazione a T · braccio 1
    - da **DER-04** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
22. **DER-04** Derivazione a T · braccio 2 → **DER-05** Derivazione a T · braccio 1
    - da **DER-05** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
23. **DER-05** Derivazione a T · braccio 2 → **VI-11** Valvola di intercettazione · braccio 1
24. **VI-11** Valvola di intercettazione · braccio 2 → **PDC-01** Pompa di calore aria-acqua · braccio 2
25. **PDC-01** Pompa di calore aria-acqua · braccio 1 → **DER-06** Derivazione a T · braccio 1
    - da **DER-06** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
26. **DER-06** Derivazione a T · braccio 2 → **DER-07** Derivazione a T · braccio 1
    - da **DER-07** Derivazione a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
27. **DER-07** Derivazione a T · braccio 2 → **VI-12** Valvola di intercettazione · braccio 1
28. **VI-12** Valvola di intercettazione · braccio 2 → **VI-13** Valvola di intercettazione · braccio 1
29. **VI-13** Valvola di intercettazione · braccio 2 → **SA-02** Separatore d'aria · braccio 1
30. **SA-02** Separatore d'aria · braccio 2 → **VI-14** Valvola di intercettazione · braccio 1
31. **VI-14** Valvola di intercettazione · braccio 2 → **RC-01** Raccordo a T · braccio 1 · **qui il giro si richiude su RC-01**
32. **DER-07** Derivazione a T · braccio 3 → **TM-01** Termometro · braccio 1
33. **DER-06** Derivazione a T · braccio 3 → **VS-01** Valvola di sicurezza · braccio 1
34. **DER-05** Derivazione a T · braccio 3 → **VI-15** Valvola di intercettazione · braccio 1
35. **VI-15** Valvola di intercettazione · braccio 2 → **MN-01** Manometro · braccio 1
36. **DER-04** Derivazione a T · braccio 3 → **VIB-01** Valvola di intercettazione bloccabile aperta · braccio 1
37. **VIB-01** Valvola di intercettazione bloccabile aperta · braccio 2 → **VE-01** Vaso di espansione · braccio 1
38. **DER-03** Derivazione a T · braccio 3 → **VI-16** Valvola di intercettazione · braccio 1
39. **VI-16** Valvola di intercettazione · braccio 2 → **GR-01** Gruppo di riempimento · braccio 1
40. **RC-02** Ripartizione a T · braccio 3 → **RC-03** Raccordo a T · braccio 1
    - da **RC-03** Raccordo a T la lettura prosegue su altri 2 bracci: braccio 2 e braccio 3
41. **RC-03** Raccordo a T · braccio 3 → **FIL-02** Filtro a Y · braccio 1
42. **FIL-02** Filtro a Y · braccio 2 → **DEF-02** Defangatore · braccio 1
43. **DEF-02** Defangatore · braccio 2 → **VI-17** Valvola di intercettazione · braccio 1
44. **VI-17** Valvola di intercettazione · braccio 2 → **CAL-01** Caldaia a condensazione · braccio 2 · **qui il giro si richiude su CAL-01**
45. **RC-03** Raccordo a T · braccio 2 → **VI-18** Valvola di intercettazione · braccio 2
46. **VI-18** Valvola di intercettazione · braccio 1 → **SCA-01** Scambiatore a piastre · braccio 2
47. **SCA-01** Scambiatore a piastre · braccio 1 → **VI-19** Valvola di intercettazione · braccio 2
48. **VI-19** Valvola di intercettazione · braccio 1 → **DEF-03** Defangatore · braccio 2
49. **DEF-03** Defangatore · braccio 1 → **FIL-03** Filtro a Y · braccio 2
50. **FIL-03** Filtro a Y · braccio 1 → **VI-20** Valvola di intercettazione · braccio 2
51. **VI-20** Valvola di intercettazione · braccio 1 → **VD-01** Valvola deviatrice a tre vie · braccio 3 · **qui il giro si richiude su VD-01**

*Circuito secondario*

52. **VOL-01** Volano termico a quattro attacchi · braccio 3 → **VI-21** Valvola di intercettazione · braccio 1
53. **VI-21** Valvola di intercettazione · braccio 2 → **FIL-04** Filtro a Y · braccio 1
54. **FIL-04** Filtro a Y · braccio 2 → **DEF-04** Defangatore · braccio 1
55. **DEF-04** Defangatore · braccio 2 → **VI-22** Valvola di intercettazione · braccio 1
56. **VI-22** Valvola di intercettazione · braccio 2 → **CIR-01** Pompa di circolazione · braccio 1
57. **CIR-01** Pompa di circolazione · braccio 2 → **VI-23** Valvola di intercettazione · braccio 1
58. **VI-23** Valvola di intercettazione · braccio 2 → **VI-24** Valvola di intercettazione · braccio 1
59. **VI-24** Valvola di intercettazione · braccio 2 → **RAD-01** Radiatore · braccio 1
60. **RAD-01** Radiatore · braccio 2 → **VI-25** Valvola di intercettazione · braccio 1
61. **VI-25** Valvola di intercettazione · braccio 2 → **VI-26** Valvola di intercettazione · braccio 1
62. **VI-26** Valvola di intercettazione · braccio 2 → **VOL-01** Volano termico a quattro attacchi · braccio 4 · **qui il giro si richiude su VOL-01**

*Circuito primario*

63. **VOL-01** Volano termico a quattro attacchi · braccio 6 → **SC-01** Attacco di scarico · braccio 1
64. **DER-02** Derivazione a T · braccio 3 → **TM-02** Termometro · braccio 1
65. **DER-01** Derivazione a T · braccio 3 → **VS-02** Valvola di sicurezza · braccio 1

### Si parte da PDC-01, sull'acqua di riscaldamento

**PDC-01** Pompa di calore aria-acqua e' una sorgente: generatore di calore. Da qui l'acqua di riscaldamento entra nell'impianto.

Da **PDC-01** Pompa di calore aria-acqua la lettura prosegue su 2 bracci: braccio 1 e braccio 2.

Da qui non riparte niente che non sia gia' stato letto: il suo giro compare piu' su.


### Si parte da AF-01, sull'acqua fredda sanitaria

**AF-01** Alimentazione acqua fredda e' una sorgente: allacciamento. Da qui l'acqua fredda sanitaria entra nell'impianto.

*Acqua fredda sanitaria*

1. **AF-01** Alimentazione acqua fredda · braccio 1 → **VI-27** Valvola di intercettazione · braccio 1
2. **VI-27** Valvola di intercettazione · braccio 2 → **VI-28** Valvola di intercettazione · braccio 1
3. **VI-28** Valvola di intercettazione · braccio 2 → **SCA-01** Scambiatore a piastre · braccio 3 · **qui ci si innesta su SCA-01**, che si e' gia' letto

### Si riparte da SCA-01, sull'acqua calda sanitaria

Attraversando **SCA-01** Scambiatore a piastre il fluido cambia nome: quello che esce di qui e' acqua calda sanitaria, e il suo giro si legge a parte.

*Acqua calda sanitaria*

1. **SCA-01** Scambiatore a piastre · braccio 4 → **VI-29** Valvola di intercettazione · braccio 1
2. **VI-29** Valvola di intercettazione · braccio 2 → **VI-30** Valvola di intercettazione · braccio 1
3. **VI-30** Valvola di intercettazione · braccio 2 → **ACS-01** Utenze sanitarie · braccio 1

---

## Quello che il grafo non tace

Le cose che un elenco muto lascerebbe scoprire in cantiere.

**Attacchi liberi:** nessuno. Ogni attacco di ogni pezzo porta la sua
tubazione.

**Pezzi che nessuna sorgente raggiunge:** nessuno. Partendo dalle sorgenti si
arriva a ogni pezzo dell'impianto.

**Tubazioni non lette:** nessuna. Ogni tubazione compare nella passeggiata.

**Punti aperti: qui una regola si applicava e il catalogo non aveva niente da
offrire.** Non e' una dimenticanza del disegno: e' una scelta che torna al
progettista.

- **manca defangatore** su **SCA-01** Scambiatore a piastre: servirebbe, e in catalogo non c'e' nessun pezzo che lo faccia sull'acqua fredda sanitaria. Va deciso dal progettista.

---

## Cosa ti stiamo chiedendo

Di scorrere la passeggiata e dirci, per ogni pezzo: **e' quello giusto, ed e' nel
punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito sbagliato
si vede da qui, senza aprire nient'altro — e per segnalarcelo basta la sigla.
