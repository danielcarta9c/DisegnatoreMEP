# L'albero dell'impianto

> **Cosa approvi qui.** L'impianto completo — quello che hai descritto piu' tutto
> cio' che le regole degli accessori gli hanno aggiunto — scritto invece che
> disegnato. Serve a vedere **che cosa e' uscito e dove sta**, prima e
> indipendentemente da qualunque tavola.
>
> **Perche' non un disegno.** Un disegno prova l'instradamento e la resa grafica.
> Qui la domanda e' un'altra: il pezzo giusto e' finito nel punto giusto, sul tubo
> giusto? Quella si legge meglio su un elenco che su un segno.

---

## Come si legge

- **Ogni pezzo e' un nodo** con la propria sigla, macchine e accessori allo stesso
  modo. Le sigle gia' scritte da te restano come le hai scritte.
- **Ogni tubazione fra due pezzi e' un arco**, e porta il proprio fluido.
- **Ogni attacco e' un braccio numerato**, come in un incrocio stradale: un volano a
  quattro attacchi e' un nodo solo con quattro bracci. Dove su un braccio convergono
  piu' tubazioni, il braccio lo dice.
- **Non e' un albero, e' un anello.** Un circuito si chiude su se' stesso: dove
  succede, la lettura lo segnala invece di fermarsi.

**Da dove si comincia a contare.** Dalle sorgenti — PDC-01 Pompa di calore aria-acqua e AF-01 Alimentazione acqua fredda — seguendo l'acqua.
La prima valvola che si incontra uscendo dal generatore e' la numero uno della sua
famiglia. **Costo di questa scelta, detto subito:** se domani si aggiunge un pezzo
vicino a una sorgente, i numeri della sua famiglia a valle scalano tutti di uno. E'
normale per un documento che si rigenera a ogni revisione; cio' che non cambia mai
e' che lo stesso impianto dia sempre le stesse sigle.

---

## Le sigle, per famiglia

| Sigla | Famiglia |
|---|---|
| **VOL** | Accumulo inerziale |
| **BOL** | Accumulo di acqua calda sanitaria |
| **CIR** | Circolatore |
| **COL** | Collettore |
| **VD** | Valvola deviatrice |
| **VM** | Valvola miscelatrice |
| **VIB** | Valvola di intercettazione bloccabile aperta |
| **VI** | Valvola di intercettazione |
| **VR** | Valvola di ritegno |
| **VS** | Valvola di sicurezza |
| **VE** | Vaso di espansione |
| **FIL** | Filtro |
| **DEF** | Defangatore |
| **SA** | Separatore d'aria |
| **GR** | Gruppo di riempimento |
| **SC** | Attacco di scarico |
| **MN** | Manometro |
| **TM** | Termometro |
| **ACS** | famiglia nominata da te nel modello |
| **AF** | famiglia nominata da te nel modello |
| **PAV** | famiglia nominata da te nel modello |
| **PDC** | famiglia nominata da te nel modello |
| **RAD** | famiglia nominata da te nel modello |

---

## I nodi

| Sigla | Che cos'e' | Fluidi che tocca | Bracci |
|---|---|---|---|
| **PDC-01** | Pompa di calore aria-acqua | acqua di riscaldamento | braccio 1 (uscita) · braccio 2 (ingresso, vi convergono 2 tubazioni) |
| **VS-01** | Valvola di sicurezza · pende dal tubo | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-02** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **TM-01** | Termometro · pende dal tubo | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **SA-01** | Separatore d'aria | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-03** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VD-01** | Valvola deviatrice a tre vie | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) · braccio 3 (uscita) |
| **VI-04** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-05** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **FIL-01** | Filtro a Y | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-06** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-07** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VOL-01** | Volano termico a quattro attacchi | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) · braccio 3 (uscita) · braccio 4 (ingresso, vi convergono 2 tubazioni) |
| **SC-01** | Attacco di scarico · pende dal tubo | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-01** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **FIL-02** | Filtro a Y | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **DEF-01** | Defangatore | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VIB-01** | Valvola di intercettazione bloccabile aperta | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VE-01** | Vaso di espansione · pende dal tubo | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VIB-02** | Valvola di intercettazione bloccabile aperta | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **GR-01** | Gruppo di riempimento · pende dal tubo | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **MN-01** | Manometro · pende dal tubo | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-08** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-09** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **FIL-03** | Filtro a Y | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **DEF-02** | Defangatore | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-10** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **CIR-02** | Pompa di circolazione | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-11** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-12** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **COL-01** | Collettore di zona | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) · braccio 3 (uscita) |
| **VI-13** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-14** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **RAD-01** | Radiatore | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-15** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-16** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-17** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-18** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **PAV-01** | Pannello radiante | acqua di riscaldamento | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-19** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-20** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VI-21** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **BOL-01** | Bollitore ACS | acqua di riscaldamento, acqua fredda sanitaria, acqua calda sanitaria | braccio 1 (ingresso) · braccio 2 (uscita) · braccio 3 (uscita) · braccio 4 (ingresso) |
| **VI-22** | Valvola di intercettazione | acqua di riscaldamento | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **SC-02** | Attacco di scarico sanitario · pende dal tubo | acqua calda sanitaria | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-23** | Valvola di intercettazione | acqua calda sanitaria | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VM-01** | Valvola miscelatrice termostatica | acqua calda sanitaria | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-24** | Valvola di intercettazione | acqua calda sanitaria | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **ACS-01** | Utenze sanitarie | acqua calda sanitaria | braccio 1 (ingresso) |
| **VS-02** | Valvola di sicurezza sanitaria · pende dal tubo | acqua fredda sanitaria | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-25** | Valvola di intercettazione | acqua fredda sanitaria | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VIB-03** | Valvola di intercettazione bloccabile aperta | acqua fredda sanitaria | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VE-02** | Vaso di espansione sanitario · pende dal tubo | acqua fredda sanitaria | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VIB-04** | Valvola di intercettazione bloccabile aperta | acqua fredda sanitaria | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **VR-01** | Valvola di ritegno sanitaria | acqua fredda sanitaria | braccio 1 (ingresso) · braccio 2 (uscita) |
| **VI-26** | Valvola di intercettazione | acqua fredda sanitaria | braccio 1 (passaggio) · braccio 2 (passaggio) |
| **AF-01** | Alimentazione acqua fredda | acqua fredda sanitaria | braccio 1 (uscita) |

---

## Gli archi

Dal pezzo da cui l'acqua esce a quello in cui entra.

| Da | A | Fluido |
|---|---|---|
| PDC-01, braccio 1 (uscita) | VS-01, braccio 1 (ingresso) | acqua di riscaldamento |
| VS-01, braccio 2 (uscita) | VI-02, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-02, braccio 2 (passaggio) | TM-01, braccio 1 (ingresso) | acqua di riscaldamento |
| TM-01, braccio 2 (uscita) | SA-01, braccio 1 (ingresso) | acqua di riscaldamento |
| SA-01, braccio 2 (uscita) | VI-03, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-03, braccio 2 (passaggio) | VD-01, braccio 1 (ingresso) | acqua di riscaldamento |
| VD-01, braccio 2 (uscita) | VI-04, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-04, braccio 2 (passaggio) | VI-05, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-05, braccio 2 (passaggio) | FIL-01, braccio 1 (passaggio) | acqua di riscaldamento |
| FIL-01, braccio 2 (passaggio) | VI-06, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-06, braccio 2 (passaggio) | VI-07, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-07, braccio 2 (passaggio) | VOL-01, braccio 1 (ingresso) | acqua di riscaldamento |
| VOL-01, braccio 2 (uscita) | SC-01, braccio 1 (ingresso) | acqua di riscaldamento |
| SC-01, braccio 2 (uscita) | VI-01, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-01, braccio 2 (passaggio) | FIL-02, braccio 1 (passaggio) | acqua di riscaldamento |
| FIL-02, braccio 2 (passaggio) | DEF-01, braccio 1 (ingresso) | acqua di riscaldamento |
| DEF-01, braccio 2 (uscita) | VIB-01, braccio 1 (passaggio) | acqua di riscaldamento |
| VIB-01, braccio 2 (passaggio) | VE-01, braccio 1 (ingresso) | acqua di riscaldamento |
| VE-01, braccio 2 (uscita) | VIB-02, braccio 1 (passaggio) | acqua di riscaldamento |
| VIB-02, braccio 2 (passaggio) | GR-01, braccio 1 (ingresso) | acqua di riscaldamento |
| GR-01, braccio 2 (uscita) | MN-01, braccio 1 (ingresso) | acqua di riscaldamento |
| MN-01, braccio 2 (uscita) | VI-08, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-08, braccio 2 (passaggio) | PDC-01, braccio 2 (ingresso, vi convergono 2 tubazioni) | acqua di riscaldamento |
| VD-01, braccio 3 (uscita) | VI-20, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-20, braccio 2 (passaggio) | VI-21, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-21, braccio 2 (passaggio) | BOL-01, braccio 1 (ingresso) | acqua di riscaldamento |
| BOL-01, braccio 2 (uscita) | VI-22, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-22, braccio 2 (passaggio) | PDC-01, braccio 2 (ingresso, vi convergono 2 tubazioni) | acqua di riscaldamento |
| VOL-01, braccio 3 (uscita) | VI-09, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-09, braccio 2 (passaggio) | FIL-03, braccio 1 (passaggio) | acqua di riscaldamento |
| FIL-03, braccio 2 (passaggio) | DEF-02, braccio 1 (ingresso) | acqua di riscaldamento |
| DEF-02, braccio 2 (uscita) | VI-10, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-10, braccio 2 (passaggio) | CIR-02, braccio 1 (ingresso) | acqua di riscaldamento |
| CIR-02, braccio 2 (uscita) | VI-11, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-11, braccio 2 (passaggio) | VI-12, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-12, braccio 2 (passaggio) | COL-01, braccio 1 (ingresso) | acqua di riscaldamento |
| COL-01, braccio 2 (uscita) | VI-13, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-13, braccio 2 (passaggio) | VI-14, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-14, braccio 2 (passaggio) | RAD-01, braccio 1 (ingresso) | acqua di riscaldamento |
| COL-01, braccio 3 (uscita) | VI-17, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-17, braccio 2 (passaggio) | VI-18, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-18, braccio 2 (passaggio) | PAV-01, braccio 1 (ingresso) | acqua di riscaldamento |
| RAD-01, braccio 2 (uscita) | VI-15, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-15, braccio 2 (passaggio) | VI-16, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-16, braccio 2 (passaggio) | VOL-01, braccio 4 (ingresso, vi convergono 2 tubazioni) | acqua di riscaldamento |
| PAV-01, braccio 2 (uscita) | VI-19, braccio 1 (passaggio) | acqua di riscaldamento |
| VI-19, braccio 2 (passaggio) | VOL-01, braccio 4 (ingresso, vi convergono 2 tubazioni) | acqua di riscaldamento |
| AF-01, braccio 1 (uscita) | VI-26, braccio 1 (passaggio) | acqua fredda sanitaria |
| VI-26, braccio 2 (passaggio) | VR-01, braccio 1 (ingresso) | acqua fredda sanitaria |
| VR-01, braccio 2 (uscita) | VIB-04, braccio 1 (passaggio) | acqua fredda sanitaria |
| VIB-04, braccio 2 (passaggio) | VE-02, braccio 1 (ingresso) | acqua fredda sanitaria |
| VE-02, braccio 2 (uscita) | VIB-03, braccio 1 (passaggio) | acqua fredda sanitaria |
| VIB-03, braccio 2 (passaggio) | VI-25, braccio 1 (passaggio) | acqua fredda sanitaria |
| VI-25, braccio 2 (passaggio) | VS-02, braccio 1 (ingresso) | acqua fredda sanitaria |
| VS-02, braccio 2 (uscita) | BOL-01, braccio 4 (ingresso) | acqua fredda sanitaria |
| BOL-01, braccio 3 (uscita) | SC-02, braccio 1 (ingresso) | acqua calda sanitaria |
| SC-02, braccio 2 (uscita) | VI-23, braccio 1 (passaggio) | acqua calda sanitaria |
| VI-23, braccio 2 (passaggio) | VM-01, braccio 1 (ingresso) | acqua calda sanitaria |
| VM-01, braccio 2 (uscita) | VI-24, braccio 1 (passaggio) | acqua calda sanitaria |
| VI-24, braccio 2 (passaggio) | ACS-01, braccio 1 (ingresso) | acqua calda sanitaria |

---

## Come si segue l'acqua

Ogni blocco e' una tubazione fra due pezzi, con in mezzo la fila ordinata di cio'
che ci sta sopra, da monte a valle.

### Circuito primario — acqua di riscaldamento

**PDC-01 Pompa di calore aria-acqua**, braccio 1 (uscita) → **VD-01 Valvola deviatrice a tre vie**, braccio 1 (ingresso)
&nbsp;&nbsp;&nbsp;VS-01 Valvola di sicurezza · VI-02 Valvola di intercettazione · TM-01 Termometro · SA-01 Separatore d'aria · VI-03 Valvola di intercettazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ VS-01 non e' un organo di passaggio: pende dal tubo con una propria derivazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ TM-01 non e' un organo di passaggio: pende dal tubo con una propria derivazione

**VOL-01 Volano termico a quattro attacchi**, braccio 2 (uscita) → **PDC-01 Pompa di calore aria-acqua**, braccio 2 (ingresso, vi convergono 2 tubazioni)
&nbsp;&nbsp;&nbsp;SC-01 Attacco di scarico · VI-01 Valvola di intercettazione · FIL-02 Filtro a Y · DEF-01 Defangatore · VIB-01 Valvola di intercettazione bloccabile aperta · VE-01 Vaso di espansione · VIB-02 Valvola di intercettazione bloccabile aperta · GR-01 Gruppo di riempimento · MN-01 Manometro · VI-08 Valvola di intercettazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ SC-01 non e' un organo di passaggio: pende dal tubo con una propria derivazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ VE-01 non e' un organo di passaggio: pende dal tubo con una propria derivazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ GR-01 non e' un organo di passaggio: pende dal tubo con una propria derivazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ MN-01 non e' un organo di passaggio: pende dal tubo con una propria derivazione

**BOL-01 Bollitore ACS**, braccio 2 (uscita) → **PDC-01 Pompa di calore aria-acqua**, braccio 2 (ingresso, vi convergono 2 tubazioni)
&nbsp;&nbsp;&nbsp;VI-22 Valvola di intercettazione

**VD-01 Valvola deviatrice a tre vie**, braccio 2 (uscita) → **VOL-01 Volano termico a quattro attacchi**, braccio 1 (ingresso) · **qui il giro si richiude su VOL-01**
&nbsp;&nbsp;&nbsp;VI-04 Valvola di intercettazione · VI-05 Valvola di intercettazione · FIL-01 Filtro a Y · VI-06 Valvola di intercettazione · VI-07 Valvola di intercettazione

**VD-01 Valvola deviatrice a tre vie**, braccio 3 (uscita) → **BOL-01 Bollitore ACS**, braccio 1 (ingresso) · **qui il giro si richiude su BOL-01**
&nbsp;&nbsp;&nbsp;VI-20 Valvola di intercettazione · VI-21 Valvola di intercettazione

### Circuito secondario — acqua di riscaldamento

**VOL-01 Volano termico a quattro attacchi**, braccio 3 (uscita) → **COL-01 Collettore di zona**, braccio 1 (ingresso)
&nbsp;&nbsp;&nbsp;VI-09 Valvola di intercettazione · FIL-03 Filtro a Y · DEF-02 Defangatore · VI-10 Valvola di intercettazione · CIR-02 Pompa di circolazione · VI-11 Valvola di intercettazione · VI-12 Valvola di intercettazione

**RAD-01 Radiatore**, braccio 2 (uscita) → **VOL-01 Volano termico a quattro attacchi**, braccio 4 (ingresso, vi convergono 2 tubazioni)
&nbsp;&nbsp;&nbsp;VI-15 Valvola di intercettazione · VI-16 Valvola di intercettazione

**PAV-01 Pannello radiante**, braccio 2 (uscita) → **VOL-01 Volano termico a quattro attacchi**, braccio 4 (ingresso, vi convergono 2 tubazioni)
&nbsp;&nbsp;&nbsp;VI-19 Valvola di intercettazione

**COL-01 Collettore di zona**, braccio 2 (uscita) → **RAD-01 Radiatore**, braccio 1 (ingresso) · **qui il giro si richiude su RAD-01**
&nbsp;&nbsp;&nbsp;VI-13 Valvola di intercettazione · VI-14 Valvola di intercettazione

**COL-01 Collettore di zona**, braccio 3 (uscita) → **PAV-01 Pannello radiante**, braccio 1 (ingresso) · **qui il giro si richiude su PAV-01**
&nbsp;&nbsp;&nbsp;VI-17 Valvola di intercettazione · VI-18 Valvola di intercettazione

### Acqua calda sanitaria

**BOL-01 Bollitore ACS**, braccio 3 (uscita) → **ACS-01 Utenze sanitarie**, braccio 1 (ingresso)
&nbsp;&nbsp;&nbsp;SC-02 Attacco di scarico sanitario · VI-23 Valvola di intercettazione · VM-01 Valvola miscelatrice termostatica · VI-24 Valvola di intercettazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ SC-02 non e' un organo di passaggio: pende dal tubo con una propria derivazione

### Acqua fredda sanitaria

**AF-01 Alimentazione acqua fredda**, braccio 1 (uscita) → **BOL-01 Bollitore ACS**, braccio 4 (ingresso)
&nbsp;&nbsp;&nbsp;VI-26 Valvola di intercettazione · VR-01 Valvola di ritegno sanitaria · VIB-04 Valvola di intercettazione bloccabile aperta · VE-02 Vaso di espansione sanitario · VIB-03 Valvola di intercettazione bloccabile aperta · VI-25 Valvola di intercettazione · VS-02 Valvola di sicurezza sanitaria
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ VE-02 non e' un organo di passaggio: pende dal tubo con una propria derivazione
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ VS-02 non e' un organo di passaggio: pende dal tubo con una propria derivazione

---

## Punti aperti

Nessuno: per ogni accessorio che le regole hanno chiesto, il catalogo aveva il
pezzo adatto al fluido di quella tubazione.

---

## Cosa ti stiamo chiedendo

Di scorrere la lettura dell'acqua e dirci, per ogni pezzo: **e' quello giusto, ed
e' nel punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito
sbagliato si vede da qui, senza aprire nient'altro.
