# PRD — Disegnatore MEP

## Problema

La generazione grafica libera produce schemi termotecnici incoerenti: accessori fuori dalle tubazioni, valvole collocate senza regole, collegamenti simili a diagrammi da presentazione e risultati difficili da verificare o riutilizzare in un progetto esecutivo.

## Obiettivo

Creare una skill che operi come un tecnico CAD esperto di disegno termotecnico. A partire da una configurazione già progettata e dimensionata dall'ingegnere, deve:

1. interpretare e normalizzare l'impianto;
2. verificare la completezza del corredo accessorio;
3. proporre integrazioni motivate;
4. raccogliere l'approvazione dell'ingegnere;
5. produrre uno schema unifilare tecnico-esecutivo vettoriale.

## Utente principale

Ingegnere termotecnico che definisce architettura, potenze, volumi, circuiti e scelte progettuali principali, ma delega alla skill lo sviluppo coerente del dettaglio grafico e degli accessori standard.

## Perimetro funzionale

La skill non è un generatore di schemi tipo. Il nucleo deve rappresentare impianti termici componibili mediante componenti, porte tipizzate, reti e diramazioni.

La libreria iniziale deve essere ampia e comprendere i componenti comuni dei principali domini:

- reti idroniche di riscaldamento, raffrescamento e ACS;
- generatori a pompa di calore, gas e sistemi ibridi;
- centrali termiche, scambiatori e accumuli;
- distribuzioni miste con radiatori, pavimento radiante e ventilconvettori nello stesso impianto;
- impianti aria-aria e aria-acqua canalizzati;
- sistemi a espansione diretta e VRV;
- reti gas, scarico condensa, regolazione e misura pertinenti allo schema termotecnico.

Il primo caso con pompa di calore, ACS, volano a quattro attacchi e due zone è un test di accettazione, non il limite della skill.

## Livello dell'elaborato

Schema tecnico-esecutivo impiantistico comprendente componenti principali, valvole, accessori, strumenti di misura, sonde, dispositivi di sicurezza, tag, diametri e dati tecnici disponibili. Sono escluse, nella prima versione, le annotazioni dettagliate di posa e montaggio.

## Flusso approvato

1. L'ingegnere descrive l'impianto ad alto livello.
2. La skill completa l'analisi secondo l'interpretazione tecnica più comune.
3. La skill presenta, senza disegnare, integrazioni e domande.
4. Le integrazioni sono classificate come necessarie, raccomandate o condizionate.
5. Ogni voce riporta quantità, posizione funzionale, motivazione e regola applicata.
6. L'ingegnere approva o corregge; una risposta come «sì, procedi» approva la proposta completa.
7. Soltanto dopo l'approvazione viene generato lo schema.

## Fuori perimetro iniziale

- dimensionamento automatico;
- selezione autonoma delle apparecchiature principali;
- modifica silenziosa delle scelte dell'ingegnere;
- annotazioni esecutive di posa;
- controllo diretto di AutoCAD o altri CAD come requisito della prima versione.

## Criteri di successo preliminari

- nessun accessorio grafico flottante o scollegato;
- topologia verificabile prima del rendering;
- quantità e posizione degli accessori ricostruibili dalle regole applicate;
- disegno leggibile, allineato e privo di sovrapposizioni;
- supporto di più reti e terminali differenti nello stesso impianto;
- SVG/PDF vettoriali riproducibili a parità di input;
- approvazione esplicita dell'ingegnere prima del disegno.
