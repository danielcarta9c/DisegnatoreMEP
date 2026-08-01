# ADR 0001 - Nucleo universale con pacchetti di dominio

**Stato:** accettato - agosto 2026

## Contesto

Il prodotto deve rappresentare impianti termici misti senza trasformarsi in un catalogo di schemi tipo. Acqua, aria, refrigerante e gas condividono concetti topologici, ma non regole e convenzioni identiche.

## Decisione

Usare un nucleo universale per componenti, porte, reti e connessioni, affiancato da pacchetti di dominio indipendenti per vocabolario, regole, simbologia e validazione.

## Motivazione

Un catalogo di template non gestirebbe combinazioni nuove. Un motore completamente uniforme mescolerebbe regole incompatibili. La separazione proposta riusa la grammatica comune mantenendo competenza specifica per dominio.

## Conseguenze

È possibile aggiungere nuovi domini o componenti senza modificare il nucleo. Ogni pacchetto richiede però una propria copertura di test e una gestione esplicita delle interfacce con gli altri domini.

## Quando rivedere

Se due domini richiedessero modelli topologici realmente incompatibili o se il nucleo iniziasse a contenere eccezioni specifiche di dominio.
