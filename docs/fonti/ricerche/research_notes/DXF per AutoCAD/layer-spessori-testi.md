> **Nota di ricerca della sessione del 26 settembre 2026** (`REL-004`, D-152), riportata com'è stata
> scritta. I file che cita «in questa cartella» — le anteprime delle norme ISO, i PDF dei manuali, l'estratto
> ISO Open Data — sono rimasti nella sessione: il repository è pubblico e le norme non si riproducono.
> Le scelte fatte poi nel programma sono in `../../reports/DXF per AutoCAD.md`.

# Ricerca B — layer, spessori, testi e blocchi per il DXF degli schemi di centrale termica

**Data:** 26 settembre 2026 · **Per:** la sessione di `REL-004` (e, attraverso lei, il PO) · **Stato:** note di ricerca, nessuna decisione.

Legenda dei marcatori, usata in tutto il documento:

- **[V]** verificato: ho letto la fonte (testo o dato) e la cito o la parafraso da vicino;
- **[V2]** verificato solo su fonte secondaria (blog, Wikipedia, riassunto di un motore di ricerca confermato da una seconda fonte);
- **[D]** deduzione mia, non scritta in nessuna fonte;
- **[NV]** non verificato / incerto: la fonte non era leggibile o non l'ho trovata.

Nota di metodo: **iso.org, autodesk.com/support e forums.autodesk.com rispondono 403** (Cloudflare/Akamai) a questo
ambiente. Per lo stato delle norme ISO ho usato il **dataset ufficiale ISO Open Data** (file del 23 settembre 2026),
per i testi le **anteprime gratuite** delle norme (iTeh/SIST: prime pagine fino a metà norma), per Autodesk le pagine
statiche `help.autodesk.com/cloudhelp/...`. I file scaricati sono in questa cartella; l'estratto ISO è
`iso_open_data_estratto.json`.

---

## 0. In breve

1. **ISO 13567** vigente: **ISO 13567-1:2017** e **ISO 13567-2:2017** (2ª edizione, settembre 2017, stato 90.93 «confermata»); la parte 3 (ISO/TR 13567-3:1999) è **ritirata**; una revisione unificata (ISO/PWI 13567) è stata **aperta e abbandonata** (stadio 00.98). In Italia: **UNI EN ISO 13567-1:2017** e **UNI EN ISO 13567-2:2017**, in vigore dal **21 dicembre 2017**.
2. ISO 13567 fissa la **struttura** del nome (3 campi obbligatori a lunghezza fissa + 7 facoltativi, caratteri `A–Z 0–9 - _`) ma **non i codici** degli impianti: agente ed elemento si decidono per progetto o da tabelle nazionali. Per avere codici già scritti per riscaldamento, sanitario e ricircolo la fonte più utile è l'**US National CAD Standard (AIA CAD Layer Guidelines)**: `M-HWTR-SPLY`, `M-HWTR-RETN`, `P-DOMW-CPIP`, `P-DOMW-HPIP`, `P-DOMW-RPIP`.
3. **Spessori**: ISO 128-2:2022 — serie 0,13/0,18/0,25/0,35/0,5/0,7/1/1,4/2 mm, rapporto extra-grossa:grossa:fine **4:2:1**. Per gli **schemi di flusso** la norma più vicina è **ISO 10628-1:2014**: flussi principali 1,0 mm, apparecchi 0,5, valvole e strumenti 0,25, **mai sotto 0,25**; griglia M = 2,5 mm.
4. **Testi**: ISO 3098-1:2015 (serie 1,8/2,5/3,5/5/7/10/14/20 mm, l'altezza nominale è quella delle **maiuscole**), ISO 3098-5 per il CAD (tipo CB verticale preferito, tratto = h/10). ISO 10628-1 chiede 2,5 mm per i testi e 5 mm per le sigle degli apparecchi.
5. **Rilievo misurato** (§4.4): nella tavola approvata «1,8 / 2,5 / 3,5 mm» sono il **corpo** SVG, non l'altezza delle maiuscole. Con Liberation Sans 2.1.5 le maiuscole misurano **1,24 / 1,72 / 2,41 mm**. Se il DXF scrivesse `height = 2,5` con un font SHX, i testi uscirebbero **il 45 % più grandi** della tavola approvata.
6. **Nomi**: AutoCAD accetta fino a 255 caratteri ed esclude `< > / \ " : ; ? * | = , '` e l'accento grave; con `EXTNAMES=0` il limite è 31 caratteri `A–Z 0–9 $ _ -`. Per stare sicuri su ogni versione: solo **ASCII maiuscolo/minuscolo, cifre, `-` e `_`**, niente spazi, accenti, `$`, `|`, `*`.
7. **Colori**: né ISO 13567 né le AIA CLG fissano colori per layer. I colori NCS vengono dalle Tri-Service Plotting Guidelines. In Italia gli enti pubblici fissano colori soprattutto per stato di progetto (rosso nuovo, giallo demolito). Buona pratica documentata: proprietà **DaLayer (ByLayer)**, entità dei blocchi sul layer **0**.
8. **Proposta** (§7): 12 layer nel formato NCS `D-MMMM-mmmm` (11 caratteri), colori e spessori **identici alla tavola approvata**, blocchi `NoveC_<Tipo>` secondo BS 8541-1 (via AEC (UK)).

---

## 1. ISO 13567 — organizzazione e denominazione dei layer CAD

### 1.1 Edizione vigente, stato, revisione

| Documento | Edizione / data | Stadio ISO (Open Data) | Note |
|---|---|---|---|
| ISO 13567-1:2017 *Overview and principles* | 2ª ed., pubbl. 2017-09-20, 4 pp. | **90.93** (norma confermata) | sostituisce la 13567-1:1998 |
| ISO 13567-2:2017 *Concepts, format and codes used in construction documentation* | 2ª ed., pubbl. 2017-09-26, 9 pp. | **90.93** | sostituisce la 13567-2:1998 |
| ISO/TR 13567-3:1999 *Application of ISO 13567-1 and -2* | 1999-10-21 | **95.99** (ritirata) | nessuna sostituzione |
| ISO/PWI 13567 (revisione unica delle parti 1 e 2) | — | **00.98** | lavoro preliminare **abbandonato** |

- [V] Stadi e date: dataset ISO Open Data, record 70181, 70182, 31415, 86874
  (<https://isopublicstorageprod.blob.core.windows.net/opendata/_latest/iso_deliverables_metadata/json/iso_deliverables_metadata.jsonl>,
  `Last-Modified: Wed, 23 Sep 2026`). Il PWI 86874 ha `replaces: [70181, 70182]` e `currentStage: 98`.
- [V] Le due edizioni 2017 sono una **revisione minore** della 1998: «This second edition cancels and replaces the
  first edition (13567-1:1998), of which it constitutes a minor revision to update the Bibliography» (identica frase
  nella parte 2). Anteprime: <https://cdn.standards.iteh.ai/samples/70181/52a7ddcd8c114147a2b459e04dd438a7/ISO-13567-1-2017.pdf>,
  <https://cdn.standards.iteh.ai/samples/70182/dbb9db3dfac342339fcd0b827852f38f/ISO-13567-2-2017.pdf>.
- [V] «The ISO 13567 series consists of two parts … ISO 13567-1 has a general application whereas ISO 13567-2 is
  applicable to construction projects» (Introduzione, parte 1).
- [V2] Significato dei codici di stadio: 90.93 = confermata, 95.99 = ritirata, 00.98 = proposta abbandonata. Pagina ISO
  <https://www.iso.org/stage-codes.html> non leggibile da qui (403); confermato dalla tabella ULC «adapted ISO Guide 69»
  (<https://canada.ul.com/wp-content/uploads/sites/11/2014/06/ULC-PROJECT-STAGES.pdf>: «00.98 Concept for New Work Item abandoned»).
- [NV] **L'anno dell'ultima conferma** (la frase «last reviewed and confirmed in …» delle pagine
  <https://www.iso.org/standard/70181.html> e <https://www.iso.org/standard/70182.html>) non l'ho potuto leggere.

### 1.2 Adozione italiana

- [V] **UNI EN ISO 13567-1:2017** — «Data entrata in vigore: 21 dicembre 2017», stato «IN VIGORE», sommario: «La norma
  stabilisce i principi generali della struttura dei **livelli** nell'ambito dei file CAD…» (<https://store.uni.com/uni-en-iso-13567-1-2017>).
- [V] **UNI EN ISO 13567-2:2017** — in vigore dal 21 dicembre 2017: «La norma riguarda l'organizzazione e l'assegnazione di
  livelli per CAD nei progetti di costruzione…» (<https://store.uni.com/uni-en-iso-13567-2-2017>).
- [V2] Edizione precedente **UNI EN ISO 13567-1:2002**, titolo italiano «Documentazione tecnica di prodotto - Organizzazione e
  denominazione dei livelli (layers) per CAD - Vista di insieme e principi», pubblicata come versione ufficiale **in
  lingua inglese** (<https://ediliziainrete.it/norme/uni-en-iso-13567-12002>).
- [NV] La lingua dell'edizione UNI 2017 (inglese o italiano) non era indicata nella pagina letta.
- Nota: UNI traduce «layer» con **«livello»**.

### 1.3 Struttura del nome

[V] Dalla parte 2 (anteprima 2017 per §4–6.3, anteprima 1998 per i codici di presentazione, testo invariato salvo bibliografia):

- «Layer names are divided into fields. Each field holds one concept. Fields are either mandatory or optional…
  The order of fields … and the number of characters for each field should be maintained as defined in this
  document, unless an alternative is specifically agreed by the project partners and … documented» (§5.1).
- «A format with fixed number of characters is used to allow selection of layers by wildcarding» (§5.1).
- Caratteri: «Alphanumeric characters allowed are the letters A–Z and the digits 0–9 in addition to the hyphen and
  underscore characters» (§5.2). `_` = campo non usato o non deciso; `-` = «tutti i valori possibili» di quella posizione.
  «All fields are left-justified.» «Unused trailing fields in the optional part … can be omitted.»

| Campo | Lunghezza | Obbligatorio | Cosa dice la norma |
|---|---|---|---|
| Agente responsabile | 2 | sì | «considered to be unique to each project, and is thus **not defined** in this document» (§4.1) [V] |
| Elemento | 6 | sì | «National element tables should be used whenever available» (§6.2) [V] |
| Presentazione | 2 | sì | 1° carattere con codici riservati, 2° libero per il progetto (§6.3) [V] |
| Stato | 1 | no | nuovo, esistente, da demolire… [V2] |
| Settore | 4 | no | edificio, piano, zona [V2] |
| Fase | 1 | no | [V2] |
| Proiezione | 1 | no | pianta, prospetto, sezione, 3D [V2] |
| Scala | 1 | no | [V2] |
| Pacchetto di lavoro | 2 | no | [V2] |
| Definito dall'utente | libero | no | [V2] |

Lunghezze dei campi facoltativi: [V2] Wikipedia (<https://en.wikipedia.org/wiki/ISO_13567>) e la figura «Default ISO
Layer Format» dell'Appendice C delle AIA CAD Layer Guidelines (v. §2.1), che scompone un nome d'esempio in agente `A1`,
elemento `B210` più riempimento, presentazione `D_`, stato `N`, settore `B101`, fase `3`, proiezione `1`, scala `F`,
pacchetto `RC` (la stringa intera, estratta dal PDF, ha perso un carattere: non la riporto). Il §7 della norma non è
nell'anteprima.

Codici riservati del 1° carattere di **Presentazione** [V] (ISO 13567-2:1998, §6.3,
<https://cdn.standards.iteh.ai/samples/26766/5c9204ada6ce47d19d0c2af20912a938/ISO-13567-2-1998.pdf>):
`--` intero modello e foglio · `M` modello → `E` grafica degli elementi, `A` annotazioni (`T` testo, `H` tratteggi, `D`
quote, `J` richiami di sezione/dettaglio, `K` revisioni), `G` griglia, `U` utente (`R` redline, `C` linee di costruzione) ·
`P` foglio/carta → `B` bordo (`F` squadratura, `O` altra grafica), `V` testi di foglio (`W` titolo, `N` note), `I`
informazioni tabellari (`L` **legende**, `S` distinte, `Q` tabelle).

### 1.4 Esempi per impianti meccanici

- [V] Nelle parti lette la norma **non ha esempi impiantistici**; gli esempi noti sono architettonici
  (Wikipedia: `A-B374--T-` «Architect, Roof window in SfB, text»).
- [V] Esempio britannico di struttura derivata (BS 1192 / AEC (UK)): `M-Ss_65-M_HVAC-Fwd` «A mechanical engineer's HVAC
  duct in elevation or plan» (AEC (UK) Protocol for Layer Naming v4.1, p. 21, v. §2.2).
- [D] Esempio costruito da me nel formato ISO di default, solo per mostrarne la forma (codici di progetto inventati e da
  documentare): agente `MH` (il codice «Heating» del protocollo AEC (UK)), elemento `HWTRSP` (codice di progetto
  «riscaldamento, mandata»), presentazione `E_` (grafica degli elementi) → **`MHHWTRSPE_`**; lo stesso impianto, testi →
  `MHHWTRSPT_`. È leggibile solo con la tabella dei codici accanto: è il motivo per cui propongo la forma NCS (§7).
- [V] Le AIA CLG (App. C) spiegano come ottenere una **conformità «concettuale»** a ISO 13567 usando i nomi NCS:
  discipline designator ↔ agent responsible, major+minor group ↔ element, ultimo minor group riservato alle annotazioni
  ↔ presentation; «Layer names must all be of the same length, use the same set of mandatory and optional fields in the same order».

---

## 2. Altre convenzioni diffuse

### 2.1 US National CAD Standard — AIA CAD Layer Guidelines (CLG)

**Versione corrente**: [V] **NCS V7**, «Release: September 2025», NIBS product code 92014-7
(<https://nationalcadstandard.org/resources/standards/ncs7/>); a pagamento. [V] Novità V7 rilevanti: «New Major and Minor
Groups definitions added for 'Airports and Plumbing'», «All 1300+ NCS Symbol CAD files replaced and renamed»
(<https://nationalcadstandard.org/ncs7/new.php>). [V2] La pagina NIBS mostra «2024» accanto al codice V7
(<https://nibs.org/projects/united-states-national-cad-standard-ncs/>): discrepanza di date.
**Io ho letto**: l'estratto gratuito V6 del formato
(<https://www.nationalcadstandard.org/ncs6/pdfs/ncs6_clg_lnf.pdf>, © 2014) e le CLG complete della **V5** (90 pp.)
pubblicate dalla Duke University (<https://facilities.duke.edu/sites/default/files/AIA%20CAD%20Layer%20Guidelines.pdf>).
[NV] Le liste V7 per il sanitario possono essere cambiate.

**Formato** [V] (V6): «There are four defined layer name data fields: Discipline Designator, Major Group, two Minor
Groups, and Status. The Discipline Designator and Major Group fields are mandatory… Each data field is separated from
adjacent fields by a dash». Esempio completo `AI-WALL-FULL-DIMS-N`.

- Discipline designator 1–2 caratteri: `M` Mechanical (`MH` HVAC, `MP` Piping, `MI` Instrumentation…), `P` Plumbing,
  `G` General, `E` Electrical…
- Major/minor group: **4 caratteri**; «any Major Group may be combined with any prescribed Discipline Designator,
  provided that the definition of the Major Group remains unchanged»; codici utente ammessi se di «four alphabetic
  and/or numeric characters and/or "~"» e documentati nel «NCS Compliance Disclosure Statement».
- Per la conformità concettuale a ISO 13567: formato e lunghezza uguali per tutti i layer, niente major group `ANNO`.

**Codici utili, testuali dalle CLG V5** (Mechanical Layer List §5.13, Plumbing §5.15, Annotation §3.2) [V]:

| Rete della tavola | Layer NCS prescritto | Descrizione NCS |
|---|---|---|
| riscaldamento mandata | `M-HWTR-SPLY` | Hot water heating system: supply |
| riscaldamento ritorno | `M-HWTR-RETN` | Hot water heating system: return |
| acqua fredda sanitaria | `P-DOMW-CPIP` | Domestic water systems: cold water piping |
| acqua calda sanitaria | `P-DOMW-HPIP` | Domestic water systems: hot water piping |
| ricircolo | `P-DOMW-RPIP` | Domestic water systems: recirculation piping |
| solare | *nessun codice*; affini `M-GLYC-SPLY/RETN` «Glycol systems» | [D] fluido glicolato, ma non ogni solare lo è |
| acqua refrigerata | `M-CWTR-SPLY` / `M-CWTR-RETN` | Chilled water systems |
| gas metano | `M-NGAS-PIPE` | Natural gas systems: piping |
| refrigerante | `M-REFG-SPLY` / `-RETN` / `-DISC` | Refrigeration systems |
| condensa | `M-CWTR-CNDS` | Chilled water systems: condensate piping |
| regolazione | `M-CONT-WIRE` | Controls and instrumentation: wiring (low voltage) |

Gruppi generici [V]: major `EQPM` Equipment, `DIAG` Diagrams, `PIPE` Piping; minor `VALV` Valves, `TANK` Storage
tanks, `SPLY`, `RETN`; annotazioni (usabili su qualunque major group): `IDEN` Identification tags, `LEGN` «Legends,
symbol keys», `TEXT`, `NOTE`, `LABL`, `SYMB` Reference symbols, `TTLB` «Border and title block», `LOGO`, `NPLT`
non-plotting. Prescritti nelle discipline elettrica e telecomunicazioni: `E-DIAG-EQPM` e `T-DIAG-EQPM` «Diagrams: equipment».

**Adozione** [V]: Autodesk implementa NCS 3.1 in AutoCAD Architecture: «Lo stile di chiavi layer AIA v3 include spessori
di linea e tipi di linea conformi agli standard UDS, nonché colori conformi alle linee guida Tri-Services Plotting
Guidelines» (<https://help.autodesk.com/cloudhelp/2026/ITA/AutoCAD-Architecture/files/GUID-741BDF62-0BD4-43B7-84FC-0B8DB8C12562.htm>).
Esempio di committente pubblico: University of Houston, *CAD Standards* (settembre 2020): «Layers shall be based on the
AIA CAD Layer Guidelines», «Purge each drawing of unused layers prior to submittal»
(<https://www.uh.edu/facilities-planning-construction/vendor-resources/cad-standards/cad_standard_manual.pdf>).

### 2.2 BS 1192 e Uniclass (Regno Unito)

- [V] **BS 1192:2007+A2:2016 è ritirata** (2018), sostituita da BS EN ISO 19650-1:2018 e -2:2018
  (<https://www.thenbs.com/publicationindex/documents/details?Pub=BSI&DocId=314028>).
- [V2] Dopo il ritiro, l'annesso nazionale UK della BS EN ISO 19650-2 rimanda per i layer a BS EN ISO 13567-2
  (<https://www.manandmachine.co.uk/the-most-boring-article-about-cad-layer-naming-standard-youll-ever-read/>, che però
  scrive «13568-2:2217», refuso); «The UK Foreword to BS EN ISO 13567-2:2017 … covers guidance on layer naming and
  Uniclass» (S. Hamil, NBS, <https://constructioncode.blogspot.com/2019/02/bs-en-iso-19650-and-uniclass.html>). Il testo
  dell'annesso non l'ho letto [NV].
- [V] **AEC (UK) Protocol for Layer Naming v4.1** (giugno 2018,
  <https://aecuk.wordpress.com/wp-content/uploads/2018/06/aecukprotocolforlayernaming-v4-1.pdf>) — è la forma BS 1192
  resa pratica. Campi: **Role** (1–2 car.: `M` Mechanical engineers, `MH` Heating, `MW` Chilled Water, `P` Public health,
  `PW` Water Services…) – **Classification** (Uniclass 2015: tabelle Ee, Pr, SL, Ss, più Zz per il non fisico) –
  **Presentation** (`D` quote, `H` tratteggi, `M` modello, `P` carta, `T` testo, `X` esistente) `_` **Description**
  (CamelCase, ≤ 40 car.) – **View** facoltativa (`Cut`, `Fwd`, `Hid`, `Rfl`). «it is recommended that the total layer
  name length … is limited to 64 characters». Tabella Zz: `Zz_10_20_85` Title Block, `Zz_20_80_50` Legends,
  `Zz_20_10_85` Tags, `Zz_30_20` Blocks and cells.
- [V] Codici Uniclass per le nostre reti (Systems v1.43, luglio 2026): `Ss_60_40_37_48` Low-temperature hot water
  heating systems, `Ss_60_40_37_81` Solar heating systems (<https://uniclass.thenbs.com/taxon/ss_60_40_37>);
  `Ss_55_70_38_15` Cold water supply systems, `Ss_55_70_38_42` Indirect hot water storage supply systems
  (<https://uniclass.thenbs.com/taxon/ss_55_70_38>). Un layer diventerebbe per esempio
  `M-Ss_60_40_37_48-M_HeatingFlow` [D]: preciso, ma lungo e poco leggibile per un disegnatore italiano.

### 2.3 Pratiche italiane documentate

[V] Non ho trovato un documento pubblico italiano che fissi layer per **schemi di centrale termica**. Ho trovato questi
capitolati e linee guida di enti pubblici che fissano layer, colori, spessori o regole di consegna DWG:

| Ente, documento, data | Cosa fissa | URL |
|---|---|---|
| **Città di Torino**, «Pratiche edilizie on line — Standard grafici per la realizzazione degli elaborati di progetto» (PDF del 26/05/2008) | tabella dei **piani di lavoro con colore**: `TT` testalino bianco, `SQn` squadratura, `TERMICO` «simboli termico» rosso, `SCARICHI`, `ELETTRICO`…; «Il piano 0 deve essere sempre vuoto»; disegno in scala 1:1 (unità cm); modelli **DWT e DXF** con layer, stili di quota, stili di testo e «blocco testalino con attributi» | <https://servizi.torinofacile.it/servizi/filepim/manuale_cad.pdf> |
| **Comune di Genova**, «Modalità di redazione degli elaborati grafici in formato digitale» (PDF del 14/06/2017) | 1 unità = 1 m; cartiglio «possibilmente in basso a destra»; stampa monocromatica; «gli spessori delle penne diversificati in funzione del tipo di linea scelto … (es.: 0.2 mm tramezze – 0.4mm strutture portanti)»; spegnere i layer accessori | <https://www.comune.genova.it/sites/default/files/2023-06/ISTRUZIONI%20PER%20LA%20REDAZIONE%20ELABORATI%20DIGITALI_140617.pdf> |
| **Città di Pomezia**, SUE, «Modalità di redazione degli elaborati in formato digitale» (PDF del 16/03/2018) | stesso impianto di Genova; «il colore di riferimento … è il nero su sfondo bianco»; rosso/giallo per costruzioni/demolizioni | <https://municipium-images-production.s3-eu-west-1.amazonaws.com/s3/5370/allegati/istruzioni-sue/guida-di-redazione-degli-elaborati-in-formato-digitale.pdf> |
| **Autorità di bacino distrettuale del fiume Po**, «Specifica per la consegna degli elaborati», v2.1 del 27/10/2023 | disegno tecnico in **DWG «con il corredo di librerie necessarie alla ricostruzione dell'elaborato»** (font inclusi); «limitare l'utilizzo del colore» (fotocopie); consegnare «un breve commento testuale» su **livelli utilizzati, simbologie, graficismi**; nella cartografia «evitati blocchi annidati e … blocchi utilizzati con funzioni diverse da simboli» | <https://www.adbpo.it/wp-content/uploads/2023/10/SpecificaConsegnaElaborati_20231027.pdf> |
| **Gruppo CAP** (servizio idrico, Lombardia), «Specifiche di restituzione as-built e rilievi» (09/07/2019) | colori per **indice ACI**: opere realizzate rosso (1), dismesse arancione (30), demolite giallo (40), risanate viola (200); spazio modello + layout; cartiglio nello spazio carta; simbologia fornita come DWG | <https://www.gruppocap.it/content/dam/groupcap/assets/documents/documents-web/servizi-per-i-cittadini/specifiche-as-build/specifiche-restituzione-rilievi-e-as-built/_SPECIFICHE%20RESTITUZIONE%20RILIEVI%20E%20AS%20BUILT_20190709.pdf> |
| **Azienda Gardesana Servizi**, «Linee guida per la restituzione degli as built» (prima stesura novembre 2020) | layer con prefisso `R-` (rilevato); impianti in DWG «con gli eventuali Plotstyle (file .ctb di AutoCAD)» | <https://www.ags.vr.it/uploads/editor/files/Ciclo_integrato_-_modulistica/Pareri_preventivi_o_parere_tecnico/Linee_guida_per_la_restituzione_degli_as_built.pdf> |

- [D] Tratto comune: nomi italiani mnemonici e brevi, colori per layer (spesso per ACI), **layer 0 vuoto**, disegno 1:1,
  modello DWT/DXF fornito dall'ente, spessori affidati alla tabella di stampa. Nessuno cita ISO 13567.
- [V] Colori dei **tubi veri** (non dei disegni): **UNI 5634:1997**, «IN VIGORE» dal 31/10/1997, identificazione di
  tubazioni e canalizzazioni per natura del fluido (<https://store.uni.com/uni-5634-1997>). [V2] Codice colori: acqua
  verde, vapore rosso ecc. (sintesi di siti di settore). Non riguarda le tavole: i colori della tavola sono decisioni
  del PO (D-057, D-176, D-187).

---

## 3. Spessori di linea

### 3.1 ISO 128 vigente

- [V] **ISO 128-2:2022** (2ª ed., 2022-10-07, stadio 60.60) ha **assorbito** le vecchie 128-20, -21, -22, -23 (edilizia),
  -24 (meccanica), -25: nel dataset ISO tutte hanno `replacedBy` → ISO 128-2:2020 → 2022. Le altre parti vigenti:
  ISO 128-1:2020, ISO 128-3:2022, ISO 128-100:2020. [V] Per la 128-2 c'è un **PWI di terza edizione allo stadio 00.99**
  (record 90526). [V2] 00.99 è l'esito positivo della fase preliminare (ULC: «Decision to investigate New Work Item»):
  una revisione è agli inizi. [D] Nulla che cambi oggi.
- [V] Italia: **UNI EN ISO 128-2:2023**, «IN VIGORE», dal 26 gennaio 2023 (<https://store.uni.com/uni-en-iso-128-2-2023>).
- [V] ISO 128-2:2022 §5.1 (<https://cdn.standards.iteh.ai/samples/83355/10bb39d36fc34caeb80ecd25347ddb0c/ISO-128-2-2022.pdf>):
  «The width, d, of all types of lines shall be one of the following … based on a common ratio 1:√2 (≈1:1,4).
  0,13 mm; 0,18 mm; 0,25 mm; 0,35 mm; 0,5 mm; 0,7 mm; 1 mm; 1,4 mm; 2 mm. The widths of extra-wide, wide and narrow
  lines are in the ratio **4:2:1**.» §5.3: trattini `12d`, spazi `3d`, trattini corti `6d`, lunghi ≈`24d`.
  §6.1: «The minimum space between parallel lines should not be less than 0,7 mm».
- [V] Le annesse normative per settore: B (costruzioni), D (meccanica), F (navale). Non sono nell'anteprima; ne ho letto
  i testi d'origine:
  - **ISO 128-23:1999 §5 (costruzioni)**: «three line widths, narrow, wide and extra-wide … The proportions … are
    1:2:4. A special line width is used for representation and lettering of **graphical symbols**. This line width is
    situated between the width of the narrow and the wide line». Gruppi: 0,25 → 0,13/0,25/0,5 (simboli 0,18);
    **0,35 → 0,18/0,35/0,7 (simboli 0,25)**; 0,5 → 0,25/0,5/1 (simboli 0,35); 0,7 → 0,35/0,7/1,4 (simboli 0,5);
    1 → 0,5/1/2 (simboli 0,7) (<https://cdn.standards.iteh.ai/samples/22292/a9f6396b7eb94397aa5e41513ebf09b1/ISO-128-23-1999.pdf>).
  - **ISO 128-24:2014 §5 (meccanica)**: «two line widths are normally used. The proportions … should be 1:2», gruppi
    preferiti **0,5** (0,5/0,25) e **0,7** (0,7/0,35)
    (<https://cdn.standards.iteh.ai/samples/57099/67be8e32461446f1a410ce15e3aea7ff/ISO-128-24-2014.pdf>).
  - [NV] Che le tabelle siano passate identiche nelle annesse B e D del 2022 non l'ho letto.
- [V] Lo stesso elenco di spessori è nelle NCS Plotting Guidelines (Extra Fine 0,13 … XXXX Wide 2,00; «Extra Fine
  incorporated to reflect ISO 128-20») (<https://www.nationalcadstandard.org/ncs6/pdfs/ncs6_pg.pdf>).

### 3.2 Per gli schemi funzionali

- [V] **ISO 10628-1:2014** *Diagrams for the chemical and petrochemical industry — Part 1: Specification of diagrams*
  (stadio 90.93; **UNI EN ISO 10628-1:2015**, in vigore dal 12/02/2015, in inglese) è la norma ISO che regola gli
  schemi di flusso con tubazioni. §5.3.1 (<https://cdn.standards.iteh.ai/samples/51840/688f149554ee4443b3396c01f82da2ba/ISO-10628-1-2014.pdf>):
  «Line widths shall be related to the grid module (in accordance with ISO 81714-1) for flow diagrams, **M = 2,5 mm**…
  Lines representing main flows or main piping shall be highlighted»:
  - **1,0 mm** (0,4 M) linee dei flussi principali;
  - **0,5 mm** (0,2 M) simboli di apparecchi e macchine (escluse valvole e accessori), riquadri, flussi secondari,
    linee di vettori energetici e sistemi ausiliari;
  - **0,25 mm** (0,1 M) simboli di valvole, raccordi e accessori, strumenti di misura e regolazione, linee di
    trasmissione, linee di richiamo e altre linee ausiliarie;
  - «Line widths less than 0,25 mm (0,1 M) shall not be used.»
  - §5.3.2 spazio fra linee parallele ≥ 2 volte la più spessa e ≥ 1 mm; «Space between flow lines should be greater
    than 10 mm». §5.3.3 flusso «from left to right and from top to bottom», **frecce inserite nelle linee**. §5.3.4
    incroci senza collegamento: s'interrompe la linea verticale (spessori uguali) o la più sottile. §5.3.5 linee
    ausiliarie tratteggiate.
- [D] ISO 10628-1 è per l'industria chimica: per un impianto termico è un **riferimento per analogia**, non un obbligo.
  Coincide però con la griglia delle tavole (2,5 mm) e con l'impostazione già scelta (frecce sulle linee, flusso da
  sinistra a destra).
- [V] **La tavola approvata** (codice del repository a `f1c8c14`, `graphics/standard.py` e `sheet.py`, letti in sola lettura): tubazioni
  0,35; simboli 0,35 (46 su 47, `stroke_weight: medium`) e 0,50 (1, `thick`); squadratura 0,35; riquadri di
  cartiglio e legenda 0,18. [D] Sono tutti valori della serie ISO 128-2 e lineweight DXF validi. Rispetto a ISO 10628-1
  le tubazioni pesano **quanto** i simboli (non di più) e 0,18 è sotto il minimo di 0,25. È una convenzione grafica
  approvata dal PO: la segnalo, non la cambio.

---

## 4. Testi

### 4.1 ISO 3098 vigente

| Parte | Edizione | Stadio | UNI |
|---|---|---|---|
| ISO 3098-1:2015 *General requirements* | 2ª ed., 2015-02-26; **sostituisce la 3098-0:1997** | 90.93 | UNI EN ISO 3098-1:2015, in vigore dal 26/03/2015, in inglese [V] |
| ISO 3098-2:2000 *Latin alphabet, numerals and marks* | 2000-04-20 | 90.93 | UNI EN ISO 3098-2:2001 [V2] |
| ISO 3098-5:1997 *CAD lettering of the Latin alphabet…* | 1997-12-11 | 90.93 | UNI EN ISO 3098-5:2000, in vigore dal 30/04/2000, **in italiano** [V] |

Fonti: dataset ISO Open Data; <https://store.uni.com/uni-en-iso-3098-1-2015>; <https://store.uni.com/uni-en-iso-3098-5-2000>.

- [V] ISO 3098-1:2015 §5.1: «The nominal size of lettering is defined by the height (h) of the outline contour of the
  **upper-case** letters». §5.3: «1,8 mm; 2,5 mm; 3,5 mm; 5 mm; 7 mm; 10 mm; 14 mm; 20 mm» (progressione √2 come i
  formati ISO 216). §5.5: tipo A e tipo B, verticali o inclinati; **«lettering type B, vertical (V) (preferred
  application)»**; per il CAD tipi CA e CB, **«CB, vertical (V) (preferred application)»**. §4.2: spazio fra
  caratteri pari a due volte lo spessore del tratto
  (<https://cdn.standards.iteh.ai/samples/65679/d6c3a5303d6a48cba4486718d1947b0c/ISO-3098-1-2015.pdf>).
- [V] ISO 3098-5:1997 Tabella 1: tipo **CB**: spessore del tratto **d = h/10** (0,18 · 0,25 · 0,35 · 0,5 · 0,7 · 1 · 1,4 · 2
  per h = 1,8 … 20); tipo CA: d = h/14; minuscole alte 7/10 h
  (<https://cdn.standards.iteh.ai/samples/24793/ecb5d87c00b8447488e7de333c5fd888/ISO-3098-5-1997.pdf>).
- [V] ISO 10628-1:2014 §5.4: «Type B vertical lettering in accordance with ISO 3098-2 is recommended», sigle e legende
  in **maiuscolo**; altezze: **5 mm** per le designazioni di apparecchi e macchine, **2,5 mm** per il resto.
- [V] AEC (UK) BIM Technology Protocol v2.1.1 (giugno 2015) §9.4: altezze ammesse 1,8 («General text … used on A3 & A4
  size drawings»), 2,5, 3,5, 5,0 (titoli, numeri di tavola), 7,0 (titoli principali)
  (<https://aecuk.wordpress.com/wp-content/uploads/2015/06/aecukbimtechnologyprotocol-v2-1-1-201506022.pdf>).
- [V] NCS: i simboli di identificazione sono disegnati con «2.5 mm (3/32") text» (UDS Module 6,
  <https://www.nationalcadstandard.org/ncs6/pdfs/ncs6_uds6.pdf>). University of Houston: testi ≥ 1/8" (3,2 mm) stampati.

### 4.2 Caratteri: che cosa si usa nei DWG consegnati

| Carattere | Dove sta | Fonte |
|---|---|---|
| **isocp.shx / isocpeur.ttf** (e isoct, isocteur) | [D] forniti con AutoCAD: la guida li cita come font disponibili, senza dire «installati» | [V] Autodesk elenca Simplex, Romans, gdt, amgdt, **Isocp, Isocp2, Isocp3, Isoct…, «Isocpeur (TTF only)»** fra i font con i simboli speciali (<https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-518E1A9D-398C-4A8A-AC32-2D85590CDBE1.htm>); [V2] ISOCPEUR è conforme a ISO 3098-5, tratto h/10 (<https://fontsinuse.com/typefaces/201002/isocpeur>) |
| **romans.shx / simplex.shx** | [D] forniti con AutoCAD (simplex è il font di ripiego di default, quindi c'è di sicuro) | [V] stessa pagina Autodesk; **simplex.shx** è il sostituto di default dei font mancanti: «FONTALT … Specifies the alternate font to be used when the specified font file cannot be located … Initial value: simplex.shx» (<https://help.autodesk.com/cloudhelp/2020/ENU/AutoCAD-Core/files/GUID-858A8D84-5104-4A35-9C82-2094DF6F411D.htm>); University of Houston: «requires the use of SIMPLEX.shx … Special fonts which are not packaged with AutoCAD are not allowed» |
| **Arial / Arial Narrow** (TTF) | [D] font di Windows, non installati da Autodesk | [V] AEC (UK) §9.3: «Where no pre-defined text standards exist, the Text Style shall be ARIAL NARROW using font file ARIALN.TTF»; [NV] che Arial Narrow sia sempre installato su Windows |

- [V] Altezza del testo in AutoCAD — **SHX**: il valore `above` del font è «the number of vector lengths above the baseline
  that the uppercase letters extend … used as scale factors for the height specified» (altezza = maiuscole)
  (<https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-MAC-Customization/files/GUID-9BBE5B28-DF02-4EC5-863A-BA04AB6F5EF1.htm>).
  **TrueType**: «the value specified for text height represents the height of a capital letter **plus an ascent area**
  reserved for accent marks … it varies from font to font»
  (<https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-7BC6132F-BF07-4A49-B8A8-4FCB524EB736.htm>).
- [V] Liberation Sans, il carattere su cui il motore misura i testi (`graphics/metriche.py`), è **metricamente
  compatibile con Arial** (larghezze identiche) (<https://en.wikipedia.org/wiki/Liberation_fonts>). [D] Con Arial nel DXF
  i testi occupano in AutoCAD la stessa larghezza che il motore ha misurato; con ISOCPEUR o romans no.

### 4.3 Accenti e codifica (per i testi, non per i nomi)

- [V] «Starting with DXF R2007 (AC1021) the drawing file is UTF-8 encoded»; fino a R2004 vale `$DWGCODEPAGE`
  (default ANSI_1252) e i caratteri fuori codifica si scrivono `\U+nnnn`
  (<https://ezdxf.readthedocs.io/en/stable/dxfinternals/fileencoding.html>). [D] Con DXF ≥ R2007 le lettere accentate
  nei testi della tavola («unità», «è») non sono un problema; nei **nomi** conviene evitarle comunque (§5).

### 4.4 Rilievo misurato: le altezze della tavola, lette in termini ISO 3098

La tavola dichiara testi da 1,8, 2,5 e 3,5 mm (`text_small_mm`, `text_normal_mm`, `text_title_mm`), che sono tre
altezze nominali ISO 3098. Ma nell'SVG quel numero è il **`font-size`**, cioè il corpo (em). ISO 3098 misura invece
l'**altezza delle maiuscole**. Misura sul file del progetto (stesso sha256 registrato in `metriche.py`):

```
$ python3 (fontTools) su /usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf
file sha256 4659bc0c58c5028dd488ec928d41d9265db43d9b669fc14ca8b0832daca7b144
version Version 2.1.5
unitsPerEm 2048
capHeight 1409 0.688
H (168, 0, 1312, 1409) 0.688
```

| Livello della tavola | font-size SVG | Maiuscole reali (× 0,688) | Altezza ISO 3098 corrispondente |
|---|---|---|---|
| piccolo | 1,8 mm | **1,24 mm** | sotto la serie (min. 1,8) |
| normale | 2,5 mm | **1,72 mm** | ≈ 1,8 |
| titolo | 3,5 mm | **2,41 mm** | ≈ 2,5 |

- [D] **Per il DXF**: se lo scrittore copia il `font-size` nell'altezza del TEXT, con un font **SHX** (altezza =
  maiuscole) i testi escono **2,5/1,72 = +45 %** rispetto alla tavola approvata e possono sforare riquadri e legenda. Con
  **Arial TTF** il rapporto dipende da come AutoCAD definisce «maiuscola + ascendente» per quel font: **va misurato
  aprendo un DXF di prova in AutoCAD**.
- [D] Non è un difetto della tavola: il PO l'ha approvata guardandola. Se volesse testi a norma ISO 3098 (maiuscole
  1,8/2,5/3,5), i testi crescerebbero del 45 % e cambierebbero gli ingombri, cioè la **posa**, che è fuori perimetro
  di `REL-004`. È una sua decisione, da prendere a parte.

---

## 5. Nomi dei blocchi (e dei layer)

### 5.1 Limiti di AutoCAD e del DXF [V]

- **EXTNAMES** (vale per blocchi, layer, stili, tipi di linea): `1` (default) «Names can be up to **255** characters …
  can include the letters A to Z, the numerals 0 to 9, spaces, and any special characters not used by the operating
  system and the product for other purposes»; `0` «limit names to **31** characters … letters A to Z, the numerals 0 to 9,
  and the special characters dollar sign ($), underscore (_), and hyphen (-)»
  (<https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-Core/files/GUID-8EC065EC-D551-4E02-9C5A-A33D1DB80B05.htm>).
  Il comando `-BLOCK` rimanda alla stessa regola
  (<https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-Core/files/GUID-816B2D9C-F518-4E8B-971F-08E0E43006E7.htm>).
- **Caratteri vietati nei layer**: «Layer names cannot include the following characters: `< > / \ " : ; ? * | = '`»
  (<https://help.autodesk.com/cloudhelp/2015/ENU/AutoCAD-Core/files/GUID-CE211679-F264-4128-BE00-BF4E0E7DEA8E.htm>).
- **Regola generale delle tabelle** (ObjectARX): «AutoCAD preserves the case of names but does **not** use the case in
  comparisons … Names can be composed of all characters allowed by Windows or Mac OS for filenames, except comma (,),
  backquote (‘), semi-colon (;), and equal sign (=)»
  (<https://help.autodesk.com/cloudhelp/2018/ENU/OARX-DevGuide/files/GUID-83ABF20A-57D4-4AB3-8A49-D91E0F70DBFF.htm>).
  ezdxf rifiuta `<>/\":;?*=` e l'accento grave (`INVALID_NAME_CHARACTERS` in `ezdxf/lldxf/const.py`, 1.4.4).
- **Nomi riservati**: blocchi `*Model_Space`, `*Paper_Space`, `*Paper_Space0`…; blocchi anonimi con `*` (flag 70 = 1,
  «anonymous block generated by hatching, associative dimensioning…»)
  (<https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-66D32572-005A-4E23-8B8B-8726E8C14302.htm>);
  layer `0` e `DEFPOINTS` non si cancellano (Autodesk, pagina sui layer citata sopra) né si rinominano (ezdxf,
  `Layer.rename`). Riferimenti esterni: `|` separa file e nome (`STAIR|STEEL`),
  il BIND lo trasforma in `$0$`
  (<https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-4E9487C1-0821-47F9-8F1B-ECFFE3237FDE.htm>).
- Il blocco DXF ha una **descrizione facoltativa** (codice di gruppo 4, stessa pagina DXF): ci può stare il nome
  italiano del simbolo.

### 5.2 Convenzioni documentate per i nomi dei simboli

- [V] **BS 8541-1:2012**, riportata dall'AEC (UK) BIM Technology Protocol v2.1.1 §8.6 (oggetti di libreria): «Names
  should be composed using characters A to Z, a to z, 0 to 9, and the _ underscore character»; non usare
  ``, . ! " £ $ % ^ & * ( ) { } [ ] + = < > ? | \ / @ ' ~ # ¬`` né l'accento grave; «use the _ underscore character as
  the delimiter and use **CamelCase** … No spaces». Opzione 1: **`Source_Type_Subtype`**, esempio
  `AEC_LightFixture_CeilingPendant`.
  Opzione 2 con classificazione: `Role_Classification_Presentation_Source_Type_Subtype`.
- [V] AEC (UK) §8.3, regole generali: solo `A–Z`, `-`, `_`, `0–9`; campi separati da `-`; niente spazi.
- [V] ISO 13567-1 si applica anche alle librerie: «An important use is also to structure data in component libraries
  produced by third parties»; nella parte 2 chi produce cataloghi usa `__` nel campo agente.
- [V] NCS (UDS Module 6): i file dei simboli si chiamano con numero MasterFormat + estensione di 3 cifre + tipo (`ID`,
  `LINE`, `MATL`, `OBJ`, `REF`, `TEXT`) + descrizione abbreviata, p.es. `010000-001-OBJ COL CIRC`. [NV] Se la
  descrizione contenga davvero spazi o se sia un a capo del PDF; in V7 i file sono stati rinominati.
- [V] Autorità di bacino del Po: evitare blocchi annidati e blocchi usati per scopi diversi dai simboli.

---

## 6. Colori per layer e DaLayer

- [V] **ISO 13567**: nelle parti lette (§1–6.3) i colori non compaiono; la «presentazione» è una categoria del
  contenuto, non uno stile. [NV] Il §7 non l'ho letto.
- [V] **AIA CLG V5**: nessuna occorrenza di «color» nelle 90 pagine (ricerca nel testo estratto). I colori NCS vengono
  dalle **Tri-Service Plotting Guidelines** (pagina Autodesk su NCS in AutoCAD Architecture, §2.1), che le NCS
  Plotting Guidelines riportano come «gray scale, color, and line width tables»
  (<https://www.nationalcadstandard.org/ncs6/content.php>). [NV] La tabella colori non è nell'estratto gratuito.
- [V] **AEC (UK)**: nessun colore prescritto; l'esempio AutoCAD del protocollo crea il layer con colore proprio e porta
  gli oggetti a DaLayer: `-layer;color;yellow … -color bylayer … -linetype set bylayer … -layer;lweight;0.25 … -lweight;bylayer`.
- [NV] **ISO 128-2:2022** ha un §7 «Colours» che non era nell'anteprima.
- [V] **Italia**: colori per layer a Torino (per nome) e Gruppo CAP (per ACI e stato); nero su bianco e rosso/giallo per
  i raffronti a Genova e Pomezia; Po: limitare il colore. Per costruito/demolito prevale **rosso = nuovo, giallo =
  demolito** (Genova, Pomezia, Gruppo CAP, tabella di Torino); il testo del manuale di Torino dice il contrario
  («rossa per le demolizioni e gialla per le nuove costruzioni»): il documento si contraddice.
- [V] **DaLayer** (Autodesk, guida italiana): «Se il colore corrente è impostato su **DaLayer**, gli oggetti vengono
  creati nel colore assegnato al layer corrente. Se il colore corrente è impostato su **DaBlocco**, gli oggetti vengono
  creati con il colore 7 (bianco o nero) fino a quando gli oggetti vengono raggruppati in una definizione di blocco.
  Quando il blocco viene inserito nel disegno, mostra il colore corrente per questi oggetti.» — «Il colore viene inoltre
  utilizzato come metodo per indicare lo spessore di linea nella stampa dipendente dal colore»
  (<https://help.autodesk.com/cloudhelp/2024/ITA/AutoCAD-Core/files/GUID-14BC039D-238D-4D9E-921B-F4015F96CB54.htm>).
- [V] **Blocchi** (Autodesk, AutoCAD 2010, tabella): proprietà **ereditate dal layer d'inserimento** → oggetti creati sul
  layer **0** con **BYLAYER**; «inherit individual properties first, then layer properties» → **BYBLOCK** su qualunque
  layer; proprietà fisse → layer diverso da 0 e niente BYBLOCK/BYLAYER
  (<http://docs.autodesk.com/ACD/2010/ENU/AutoCAD%202010%20User%20Documentation/files/WS1a9193826455f5ffa23ce210c4a30acaf-6c53.htm>).
- [V] **Stampa**: «Color-dependent plot style tables (CTB) use an object's color to determine characteristics such as
  lineweight … There are 256 plot styles in a color-dependent plot style table, one for each color»; le tabelle con
  nome (STB) «can be assigned to objects or layers»
  (<https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-2FD01085-DDD8-49D2-A910-E63EA45A7FED.htm>);
  `monochrome.ctb` «Plots all colors as black»
  (<https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-F6DF548E-DF71-45F7-8DC5-A1EAD73998B1.htm>);
  «If you assign a plot style lineweight, the lineweight **overrides** the object's lineweight when it is plotted»
  (<https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-MAC-Core/files/GUID-2770BBA8-AF39-4278-8B65-C3FF84A66C12.htm>).
- [NV] **True Color e CTB**: esiste un articolo Autodesk intitolato «Black and white (monochrome/grayscale)
  color-dependent plot style (CTB) plots color in AutoCAD products»
  (<https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Plotting-True-Color-objects-in-monochrome.html>,
  403 da qui). Il titolo fa pensare che gli oggetti True Color possano uscire a colori con un CTB monocromatico: **da
  provare in AutoCAD**.
- [V] DXF: colore True Color sul layer «requires DXF R2004»; lineweight in centesimi di mm, validi solo
  `0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120, 140, 158, 200, 211`; `-1` BYLAYER,
  `-2` BYBLOCK, `-3` DEFAULT; `$LWDISPLAY = 1` li mostra a video
  (<https://ezdxf.readthedocs.io/en/stable/tables/layer_table_entry.html>,
  <https://ezdxf.readthedocs.io/en/stable/concepts/lineweights.html>).

---

## 7. Proposta per le nostre tavole

Tutto quello che segue è **[D]**: una proposta costruita sulle fonti sopra, da mostrare al PO nel DXF. Colori, tratteggi
e spessori sono **quelli della tavola approvata**. Non ne propongo di nuovi: sono convenzioni grafiche del PO.

### 7.1 Regole di nome

- Formato **NCS/AIA CLG** `D-MMMM-mmmm` — disciplina, major group, un minor group — **11 caratteri per tutti i layer**.
  Codici prescritti ovunque esistano; un solo codice di progetto, `SOLR`, ammesso dalle NCS se documentato.
- Solo `A–Z` e `-`: dentro l'alfabeto di ISO 13567-2 e dentro le regole più strette di AutoCAD (`EXTNAMES = 0`), quindi
  leggibile da qualunque versione DXF.
- La **descrizione italiana** va nella descrizione del layer. [V] AEC (UK): «Always remember to utilise the layer
  description»; [V] ezdxf la scrive come XDATA `AcAecLayerStandard` (`Layer.description`); [NV] che AutoCAD la mostri
  nella colonna «Descrizione» va visto.
- Conformità: **NCS sì**, ISO 13567 «concettuale» **no**, perché i layer di annotazione usano il major group `ANNO`
  che le CLG escludono per la conformità ISO. [D] Per un solo studio non serve di più.

### 7.2 Schema dei layer (12 + il layer 0)

| # | Layer | Contenuto | Base NCS | Colore (tavola approvata) | ACI più vicino* | Tipo linea | Spessore |
|---|---|---|---|---|---|---|---|
| 1 | `M-HWTR-SPLY` | tubazioni di mandata del riscaldamento (CP, CS), con le **frecce** e gli archetti di scavalcamento | prescritto | `#c0392b` | 22 | Continuous | 0,35 |
| 2 | `M-HWTR-RETN` | ritorno riscaldamento (RP, RS), con le frecce | prescritto | `#2471a3` | 142 | Continuous | 0,35 |
| 3 | `P-DOMW-CPIP` | acqua fredda sanitaria (AF), con le frecce | prescritto | `#5dade2` | 161 | tratteggio della tavola `3 2` (3 mm pieno, 2 mm vuoto) | 0,35 |
| 4 | `P-DOMW-HPIP` | acqua calda sanitaria (ACS), con le frecce | prescritto | `#d68910` | 30 | Continuous | 0,35 |
| 5 | `P-DOMW-RPIP` | ricircolo (ACSR), con le frecce | prescritto | `#58d68d` | 123 | Continuous | 0,35 |
| 6 | `M-SOLR-SPLY` | circuito solare, mandata | `SOLR` di progetto, `SPLY` prescritto | `#c71585` | 222 | Continuous | 0,35 |
| 7 | `M-SOLR-RETN` | circuito solare, ritorno (stesso magenta, D-187) | `SOLR` di progetto, `RETN` prescritto | `#c71585` | 222 | Continuous | 0,35 |
| 8 | `M-DIAG-EQPM` | **blocchi dei simboli**: generatori, accumuli, circolatori, valvole, accessori | `DIAG` + `EQPM` prescritti, come `E-DIAG-EQPM` | 7 (nero/bianco) | 7 | Continuous | 0,35 (il simbolo `thick`: 0,50 sull'inserimento) |
| 9 | `M-ANNO-IDEN` | sigle dei componenti (GT, VOL, P…) e delle linee (CP, RS, ACSR…), con le linee di richiamo | prescritti | 7 | 7 | Continuous | 0,18 |
| 10 | `M-ANNO-TEXT` | altri testi e note (riferimenti di continuità, avvisi) | prescritti | 7 | 7 | Continuous | 0,18 |
| 11 | `M-ANNO-LEGN` | legenda: riquadro, testi, campioni dei simboli e dei fluidi | prescritti | 7 | 7 | Continuous | 0,18 |
| 12 | `G-ANNO-TTLB` | squadratura, cartiglio, logo | prescritti | 7 | 7 | Continuous | 0,18 (squadratura 0,35 sull'oggetto) |
| — | `0` | **vuoto** nel disegno; contiene solo le entità dentro le definizioni di blocco | Autodesk; Torino | — | — | — | — |

\* ACI più vicino in distanza RGB, calcolato da me sulla tavolozza di ezdxf 1.4.4 (appendice A.3): le distanze vanno
da 38 a 53 su 441, **differenze visibili**. [D] Quindi **True Color** sui layer (DXF ≥ R2004), con l'ACI solo come
ripiego se il PO preferisse la stampa a CTB colore→penna.

Regole di proprietà [D, basate sulle fonti del §6]:

- Tutte le entità del disegno **DaLayer** (colore, tipo linea, spessore). Le eccezioni sono tre, dichiarate:
  1. i **campioni dei fluidi** in legenda portano colore, tratteggio e 0,35 (come nella tavola) sull'oggetto, perché
     la legenda resti intera anche se un layer di rete è spento;
  2. la **squadratura** porta 0,35 sull'oggetto;
  3. l'**inserimento** dell'unico simbolo `thick` porta 0,50.
- **Frecce**: un blocco `NoveC_FlowArrow` (un triangolo pieno) inserito sul layer della sua rete, entità interne sul
  layer 0 in **BYBLOCK**. La freccia prende il colore della rete senza colori espliciti, si sposta con la sua linea
  (il PO vuole «frecce già sulle linee») e si seleziona tutta per nome di blocco. Alternativa, se il PO volesse
  spegnere le frecce da sole: un 13° layer `M-ANNO-FLLW` (`FLLW` «Flow» è un minor group NCS), al prezzo di colori
  espliciti su ogni freccia.
- **Simboli**: entità interne sul layer **0** in **BYBLOCK**; l'inserimento sta su `M-DIAG-EQPM` in DaLayer.
  Risultato: nero, 0,35 dal layer; lo spessore del simbolo `thick` si sovrascrive sull'inserimento.
- **Stampa**: gli spessori stanno sui layer. [D] Con `monochrome.ctb` e «usa spessore oggetto», o con una STB, la stampa
  AutoCAD dà gli spessori della tavola. Con un CTB che assegna penne per colore, gli spessori del layer vengono
  sovrascritti (Autodesk) e i True Color potrebbero non essere mappati [NV]. `$LWDISPLAY = 1` perché il DXF si apra già
  con gli spessori visibili.
- **Estensioni** oltre le dodici, quando una tavola le disegna: `M-CWTR-SPLY/RETN` (refrigerata), `M-NGAS-PIPE` (gas),
  `M-REFG-SPLY/RETN` (refrigerante), `M-CWTR-CNDS` (condensa), `M-HVAC-SPLY/RETN` (aria), `M-CONT-WIRE` (regolazione).
  Tutti prescritti nelle CLG V5.

### 7.3 Blocchi

- Nome: **`NoveC_` + tipo in CamelCase** ricavato dall'id della libreria, secondo l'opzione 1 di BS 8541-1
  (`Source_Type`). Esempi: `pump-circulator` → `NoveC_PumpCirculator`, `heat-pump-air-water-large` →
  `NoveC_HeatPumpAirWaterLarge`, `valve-isolation` → `NoveC_ValveIsolation`; più `NoveC_FlowArrow` e il cartiglio
  `NoveC_TitleBlockA3`.
- [V misurato] Sui 47 simboli il nome più lungo è `NoveC_MixingValveThermostatic`, 29 caratteri; tutti in
  `[A-Za-z0-9_]`: validi anche con `EXTNAMES = 0` (≤ 31) e senza caratteri vietati.
- Il **nome italiano** («Pompa di circolazione») va nella descrizione del blocco (codice DXF 4).
- Il prefisso `NoveC_` distingue i blocchi dello studio da quelli dei produttori quando un disegnatore incolla un
  disegno in un altro. Da evitare: spazi, accenti, `$` (bind), `|` (xref), `*` iniziale (anonimi), l'accento grave e
  ``, ; = < > / \ " : ? '``.
- Blocchi **non annidati**, salvo il cartiglio (Autorità di bacino del Po).

### 7.4 Spessori (riassunto)

| Elemento | Tavola approvata | ISO 128-2, gruppo 0,35 (edilizia) | ISO 10628-1 (schemi di flusso) |
|---|---|---|---|
| tubazioni | 0,35 | grossa 0,35 | 1,0 principali · 0,5 secondarie |
| simboli di apparecchi | 0,35 (0,50 uno) | «per simboli» 0,25 | 0,5 |
| valvole e accessori | 0,35 | «per simboli» 0,25 | 0,25 |
| testi, richiami, riquadri di legenda e cartiglio | 0,18 | fine 0,18 | 0,25 (minimo) |
| squadratura | 0,35 | — | — |

Proposta [D]: **le colonne «tavola approvata»**, che sono tutte nella serie ISO 128-2 e tutte lineweight DXF validi.
Le altre due colonne servono solo se il PO vuole spingere il DXF verso una norma.

### 7.5 Testi

- Uno stile di testo, **`NC-ARIAL`** (font `arial.ttf`, altezza 0 nello stile, fattore di larghezza 1). [D] È la scelta
  più fedele alla tavola, perché Liberation Sans e Arial hanno le stesse larghezze. Alternativa ISO 3098-5:
  `isocpeur.ttf`, fornito con AutoCAD, ma con larghezze diverse (rischio di sforare riquadri e cartiglio). Da
  evitare font che non arrivano con AutoCAD o con Windows: al loro posto AutoCAD usa il font alternativo (`FONTALT`,
  di default `simplex.shx`) o chiede quale usare.
- **Altezze**: le tre della tavola (piccolo, normale, titolo), con l'altezza del TEXT **calibrata** perché le maiuscole
  in AutoCAD misurino quanto nella tavola: **1,24 / 1,72 / 2,41 mm** (§4.4). Il fattore fra altezza DXF e maiuscole di
  Arial in AutoCAD va misurato su un DXF di prova.
- [V] ISO 10628-1 vuole legende e designazioni **in maiuscolo**; la legenda della tavola scrive in minuscolo con
  iniziale maiuscola («Acqua di riscaldamento», `MEDIUM_NAMES` in `layout/legend.py`). È una convenzione del PO: la
  segnalo, il DXF riproduce la tavola.

---

## 8. Che cosa resta incerto

1. **Anno di conferma** di ISO 13567 e testo del §7–8 della parte 2 (campi facoltativi, esempi): pagine ISO bloccate,
   anteprima parziale.
2. **Lingua** delle UNI EN ISO 13567-1/-2:2017.
3. **Liste NCS V7** (a pagamento, settembre 2025): i codici che cito sono della V5 (2014). La V7 ha aggiunto gruppi
   per il sanitario: `P-DOMW-*` potrebbe avere nuove varianti.
4. **Annesso nazionale UK** alla BS EN ISO 19650-2 e prefazione UK alla BS EN ISO 13567-2: solo fonti secondarie.
5. **ISO 128-2:2022** annesse B e D: ho letto i testi d'origine (128-23:1999, 128-24:2014), non le annesse;
   **§7 «Colours»** non letto. ISO 14617-1:2025 e ISO 81714-1:2010 (simboli per schemi) non lette.
6. **Arial in AutoCAD**: rapporto fra altezza del TEXT e maiuscole. Si misura aprendo un DXF di prova.
7. **True Color con CTB monocromatico**: se gli oggetti escono neri o a colori. Si prova stampando da AutoCAD.
8. **Descrizione del layer** scritta come XDATA: se AutoCAD la mostra nel Gestore proprietà layer.
9. **Italia**: nessun capitolato pubblico trovato che fissi layer per impianti meccanici. Gli esempi riguardano pratiche
   edilizie e reti idriche. Università e aziende sanitarie cercate, niente di pubblico e leggibile (ASL TO5: 503).
10. **Arial Narrow** (raccomandato da AEC UK) su Windows senza Office: non verificato.

---

## Appendice A — misure eseguite

### A.1 Stato delle norme (ISO Open Data, file del 23/09/2026)

```
ISO 13567-1:2017 2017-09-20 ed 2 stage 9093 replacedBy [86874]
ISO 13567-2:2017 2017-09-26 ed 2 stage 9093 replacedBy [86874]
ISO/TR 13567-3:1999 1999-10-21 ed 1 stage 9599 replacedBy None
ISO/PWI 13567 None ed 1 stage 98 replacedBy None          (replaces [70181, 70182])
ISO 128-2:2022 2022-10-07 ed 2 stage 6060 replacedBy [81892, 90526]
ISO/PWI 128-2 None ed 3 stage 98 / ISO/PWI 128-2 None ed 3 stage 99
ISO 128-23:1999 1999-07-01 ed 1 stage 9599 replacedBy [69129]   (69129 = ISO 128-2:2020)
ISO 128-24:2014 2014-02-11 ed 2 stage 9599 replacedBy [69129]
ISO 3098-1:2015 2015-02-26 ed 2 stage 9093 replacedBy None      (replaces 3098-0:1997)
ISO 3098-5:1997 1997-12-11 ed 1 stage 9093 replacedBy None
ISO 10628-1:2014 2014-09-17 ed 1 stage 9093 replacedBy None
ISO 14617-1:2025 2025-03-14 ed 3 stage 6060 replacedBy None
```

Estratto completo: `iso_open_data_estratto.json` in questa cartella.

### A.2 Altezza delle maiuscole di Liberation Sans

Vedi §4.4 (fontTools su `LiberationSans-Regular.ttf` 2.1.5, sha256 `4659bc0c…`): `capHeight 1409/2048 = 0.688`.

### A.3 ACI più vicino ai colori della tavola (tavolozza di `ezdxf/colors.py` 1.4.4, distanza RGB)

```
M-HWTR-SPLY riscaldamento mandata    #c0392b -> ACI  22 rgb(165, 41, 0) dist=53.2
M-HWTR-RETN riscaldamento ritorno    #2471a3 -> ACI 142 rgb(0, 124, 165) dist=37.7
P-DOMW-CPIP AFS                      #5dade2 -> ACI 161 rgb(127, 159, 255) dist=46.8
P-DOMW-HPIP ACS                      #d68910 -> ACI  30 rgb(255, 127, 0) dist=45.1
P-DOMW-RPIP ricircolo                #58d68d -> ACI 123 rgb(82, 165, 145) dist=49.5
M-SOLR-* solare                      #c71585 -> ACI 222 rgb(165, 0, 124) dist=41.0
```

I colori vengono da `src/disegnatore_mep/layout/legend.py` (`MEDIUM_STYLES`, `SUPPLY_SHIFT`, `RECIRCULATION_COLOUR`)
del repository a `f1c8c14` (ramo `claude/missing-symbols-uuzbhb`, albero pulito), letto senza modificarlo.

### A.4 Simboli della libreria e nomi dei blocchi proposti

```
Counter({'medium': 46, 'thick': 1}) 47
max id len 25 heat-pump-air-water-large
max block name len 29 NoveC_MixingValveThermostatic
all ascii [A-Za-z0-9_]: True
```
