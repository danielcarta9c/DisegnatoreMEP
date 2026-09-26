> **Nota di ricerca della sessione del 26 settembre 2026** (`REL-004`, D-152), riportata com'è stata
> scritta. I file di lavoro che cita — `prova/`, `src/`, `venv/`, gli strumenti — sono rimasti nella
> sessione: il repository è pubblico, e delle pagine Autodesk si tengono gli indirizzi, non le copie.
> Le scelte fatte poi nel programma sono in `../../reports/DXF per AutoCAD.md`.

# DXF per AutoCAD / AutoCAD LT: note di ricerca (agente A)

Data: 26 settembre 2026. Solo ricerca: il repository non è stato toccato.

**Legenda**
- **[V]**: verificato su una fonte (URL e citazione breve).
- **[M]**: misurato qui, con comando ed esito (file in `prova/`).
- **[D]**: mia deduzione.
- **[I]**: incerto, da verificare.

**Come ho letto le fonti.** Le pagine di help.autodesk.com le ho scaricate in HTML (percorso `cloudhelp`); le copie sono in `src/`. Gli articoli di supporto su www.autodesk.com rispondono 403 (Akamai) a una lettura diretta: li ho letti tramite il lettore `r.jina.ai`, che scarica lo stesso URL Autodesk. I forum Autodesk sono fonti di comunità, non ufficiali, e sono segnalati come tali. Il sorgente di ezdxf citato è quello della 1.4.4 installata da PyPI (https://pypi.org/project/ezdxf/1.4.4/) in `venv/`.

---

## 0. Prova eseguita: la tavola prima di tutto

- **Esce una tavola.** È `prova/foglio_A3.png`, con la sua versione `prova/foglio_A3.pdf`: la presentazione A3 del DXF di prova `prova/prova_A3.dxf`, resa da ezdxf a foglio intero 420×297 mm, in scala 1:1.
  - Il DXF è scritto da `prova/crea_prova.py`.
  - Contiene: tubazioni in true color; tratteggio ISO; blocchi valvola con l'attributo SIGLA; frecce-blocco; cartiglio in spazio carta con il logo JPEG; finestra 1:1 bloccata.
- **Misure sulla tavola [M].**
  - La cornice disegnata a 10 mm dal bordo cade a 10,00 mm.
  - Il tratteggio di acqua fredda misura 12,0 mm di tratto e 3,0 mm di spazio.
  - I colori sono esatti: #c0392b, #2471a3, #c71585, e #5dade2 per l'acqua fredda (valore scelto da me per la prova: l'azzurro vero non mi è stato dato).
  - Gli spessori sono 0,35 e 0,50 mm.
  - Un tratto di acqua fredda lungo 6 mm (più corto di un motivo) esce **continuo**.
- **Cose che nella tavola non tornano, anche se i numeri vanno bene.**
  - Il testo in stile `isocp.shx` è reso con un font di ripiego (su Linux non ci sono né i file SHX né i TTF equivalenti di Autodesk). Questa tavola **non** prova l'aspetto dei testi in AutoCAD.
  - Il logo ha una doppia cornice: il bordo dell'entità IMAGE si somma a quello del JPEG. In AutoCAD dipende dalla variabile "cornice immagine" (vedi §8).
  - Sul tratto verticale di acqua fredda la freccia copre proprio uno spazio del tratteggio, e lì la linea **sembra piena**. Nel programma vero le frecce vanno messe su un tratto, non su uno spazio [D].
- **Andata e ritorno con ODA File Converter (DXF → DWG 2018 → DXF) [M].**
  - Conversione riuscita, file DWG con intestazione `AC1032`.
  - Entità, layer, colori, spessori, tipo di linea, impostazione di pagina, finestra bloccata, attributi e nome del logo sono invariati.
  - La resa prima e dopo è identica pixel per pixel: 0 pixel diversi su 1653×1169.
- **Limite della prova.** Qui non c'è AutoCAD. Nessuna prova su questa macchina sostituisce l'apertura del file da parte del disegnatore (vedi §9).

### Sorprese trovate (utili al programma)

1. `ezdxf.new()` ha come unità predefinite i **metri** (`units=6`). Per i mm bisogna passare `units=4` [V, §2].
2. `ezdxf.new(setup=True)` crea, in un documento in mm, un tipo DASHED con **1,27 mm di tratto e 0,254 mm di spazio**, e stili di testo OpenSans [M sui valori]. Con uno spessore di 0,5 mm quel tratteggio esce praticamente pieno, e OpenSans su un PC con AutoCAD di norma non c'è [D sugli effetti]. Vedi §3 e §4.
3. `Paperspace.page_setup()` di ezdxf scrive un nome carta non canonico, `ezdxf_(420.00_x_297.00_MM)` [V sorgente, §2].
4. Con un CTB, anche `monochrome.ctb`, **gli oggetti in true color stampano comunque a colori** [V Autodesk, §7].
5. Il DXF Reference descrive `$PSLTSCALE` con i valori 0 e 1 **invertiti** rispetto alla guida della variabile di sistema [V, §3]. A 1:1 la differenza non conta.
6. ODA File Converter **ripara in silenzio**: ha convertito un DXF volutamente difettoso con esito 0 e nessun file `.err` [M, §9].
7. `ezdxf draw` ritaglia la pagina sull'ingombro del contenuto: è uscita di 399,7×276,9 mm, non 420×297. Riusare lo stesso backend PyMuPDF per una seconda uscita produce una scala sbagliata (circa 2,83×) [M, §9].

---

## 1. Versione DXF

**Risposta breve.**
- Scrivere **R2013 (AC1027)**, che è anche il valore predefinito di ezdxf. Si apre in AutoCAD e AutoCAD LT dal 2013 al 2027 [D da V].
- **R2018 (AC1032)** va bene se si sa che il disegnatore ha una versione 2018 o successiva: è il formato nativo di AutoCAD 2018–2027.
- Tutto ciò che serve esiste già in entrambe:
  - spessori di linea dalla R2000;
  - true color e trasparenza dalla R2004;
  - testo UTF-8 dalla R2007;
  - presentazioni e IMAGE dalla R2000.
- R2010 non porta vantaggi concreti. R12 va esclusa.

**Fonti.**
- [V] ezdxf, gestione del documento. Firma `ezdxf.new(dxfversion='AC1027', setup=False, units=6)`. Scrive R12, R2000, R2004, R2007, R2010, R2013 e R2018. "DXF R2007 and later requires an UTF-8 encoding". Nessuna raccomandazione esplicita sulla versione. https://ezdxf.mozman.at/docs/drawing/management.html
- [V] ezdxf, true color: "The support for true color was added to the DXF file format in revision R2004"; "The true color value has higher precedence than the AutoCAD Color Index (ACI)". https://ezdxf.mozman.at/docs/concepts/true_color.html
- [V] ezdxf, spessori: "The lineweight attribute is supported by DXF R2000 and newer." https://ezdxf.mozman.at/docs/concepts/lineweights.html
- [V] ezdxf, spazio carta: "If you need paperspace layouts use DXF version R2000 or newer". https://ezdxf.mozman.at/docs/tutorials/psp_viewports.html
- [V] Autodesk, codici di gruppo comuni. 420: "A 24-bit color value…". 370: "Lineweight enum value". 62: numero di colore ACI, dove 0 è BYBLOCK e 256 è BYLAYER. 48: "Linetype scale (optional)", predefinito 1.0. 430 e 440: nome del colore e trasparenza. https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-3610039E-27D1-4E23-B6D3-7E60B22BB5BD.htm
- [V] Autodesk, variabile `$ACADVER` nell'intestazione: "AC1024 = AutoCAD 2010, AC1027 = AutoCAD 2013, AC1032 = AutoCAD 2018". https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm
- [V] Autodesk, compatibilità dei formati (articolo del 27/05/2026, prodotti AutoCAD e LT). Tabella "AutoCAD 2018 - AutoCAD 2027 → AutoCAD 2018"; "older versions cannot open DWG files of newer DWG format". https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-drawing-file-format.html
- [V] Autodesk, codici di versione: "AC1027 - DWG AutoCAD 2013/2014/2015/2016/2017", "AC1032 - DWG AutoCAD 2018/…/2024". https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/drawing-version-codes-for-autocad.html
- [M] Un DXF R2013 scritto da ezdxf 1.4.4 è stato convertito da ODA File Converter 27.1 in DWG `AC1032` senza errori (§9).

**Incerto.**
- Autodesk non raccomanda, nelle pagine che ho trovato, una versione DXF da *scrivere*. La tabella sopra riguarda i DWG; per i DXF il comportamento è analogo [D].
- Il dato "true color dalla R2004" viene da ezdxf, non da un "what's new" Autodesk. Il codice 420 compare comunque in tutte le versioni candidate.

---

## 2. Unità, spazio modello 1:1 in mm, presentazione A3/A2

**Risposta breve.**

*Unità.*
- `$INSUNITS = 4` (millimetri) e `$MEASUREMENT = 1` (metrico). In ezdxf si fanno entrambe con `ezdxf.new("R2013", units=ezdxf.units.MM)`.
- **Attenzione:** il valore predefinito di ezdxf è `units=6`, cioè metri.

*Modello.*
- Si disegna in **spazio modello in mm di carta, a 1:1**. Conviene far coincidere l'origine del foglio con (0,0) [D].

*Presentazione.*
- Una presentazione "A3" (o "A2") con impostazione di pagina a margini 0, scala 1:1, tipo di stampa "Layout" e dispositivo `DWG To PDF.pc3`.
- Una sola finestra con altezza in carta uguale all'altezza della vista in modello, cioè 1:1, con lo zoom bloccato.
- La finestra sta su un layer dedicato. Autodesk indica di **spegnerlo** per nasconderne il bordo [V]. In alternativa lo si rende non stampabile (290 = 0), così il bordo resta visibile ma non si stampa; non l'ho verificato in AutoCAD [D].
- Il cartiglio va in spazio carta.
- A 1:1 coincidono tutte le "scale": LTSCALE = 1, altezze dei testi in mm, spessori in mm. Il disegnatore può lavorare indifferentemente in modello o in presentazione [D].

*Cosa si può impostare con ezdxf.*
- `Paperspace.page_setup(size, margins, units, offset, rotation, scale, name, device)`.
- `set_plot_type()`: 0–5, dove 5 è "layout information".
- `set_plot_window()`, `set_plot_style()` (file CTB) e i flag di stampa (`print_lineweights`, `use_plot_styles`, `plot_centered`, …).
- Sulla LAYOUT: `dxf.paper_size` (nome canonico della carta) e `dxf.current_style_sheet`.
- `doc.page_setup(name, "ISO A3" | "ISO A2", landscape)` come scorciatoia.
- `doc.layouts.set_active_layout()` e `doc.layouts.delete("Layout1")`.
- Anche il Modello ha le sue impostazioni di stampa: con `set_plot_type(4)` e `set_plot_window()` si può stampare il foglio anche dal Modello [V API, D sull'utilità].

**Fonti.**
- [V] Autodesk, INSUNITS: "Specifies a drawing-units value for automatic scaling of blocks, images, or xrefs"; "4 Millimeters"; valore iniziale "4 (metric)". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-A58A87BB-482B-4042-A00A-EEF55A2B4FD8.htm
- [V] Autodesk, MEASUREMENT: "1 Metric; uses the hatch pattern file and linetype file designated by the ISOHatch and ISOLinetype registry settings". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-1D074C55-0B63-482E-8A37-A52AC0C7C8FE.htm
- [V] ezdxf, unità: "$MEASUREMENT … operates independently from $INSUNITS"; `doc.units = units.CM` è la scorciatoia per `$INSUNITS`; "It is never a good idea to use different measurement system in one project". https://ezdxf.mozman.at/docs/concepts/units.html
- [V] ezdxf, spazio carta:
  - "It's recommended to let this scale at the default value of 1:1 and draw lines and text in paperspace with the same units as you defined the paper size";
  - "Maybe it's preferable to set all margins to zero";
  - "If both values are equal the scaling is 1:1" (altezza della finestra rispetto a `view_height`);
  - "The paperspace layout feature lacks documentation in the DXF reference … most of the information here is assumptions gathered through trail and error".
  - https://ezdxf.mozman.at/docs/tutorials/psp_viewports.html
- [V] ezdxf, riferimento di `page_setup` e dei metodi `set_plot_*`: https://ezdxf.mozman.at/docs/layouts/layouts.html
- [V] Sorgente ezdxf 1.4.4, `layouts/layout.py`. `page_setup(... name="ezdxf", device="DWG to PDF.pc3")` scrive `paper_size = f"{name}_({w:.2f}_x_{h:.2f}_{units})"`, quindi per default `ezdxf_(420.00_x_297.00_MM)`. `Drawing.page_setup()` (in `document.py`) usa il nome predefinito.
- [V] Autodesk DXF, PLOTSETTINGS:
  - 2 = file di configurazione o stampante; 4 = formato carta; 7 = "Current style sheet"; 40–43 margini in mm; 44–45 formato carta in mm; 142/143 scala personalizzata;
  - 70 = flag: 16 UseStandardScale, 32 PlotPlotStyles, 128 PrintLineweights, 512 DrawViewportsFirst;
  - 72 = 1 "Plot in millimeters"; 74 = 5 "Layout information"; 75 = 16 "1:1".
  - https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-1113675E-AB07-4567-801A-310CDE0D56E9.htm
- [V] Autodesk DXF, VIEWPORT: 40/41 larghezza e altezza in unità di spazio carta; 45 "View height (in model space units)"; 90, bit "16384 (0x4000) = Enables viewport zoom locking". https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-2602B0FB-02E4-4B9A-B03C-B1D904753D34.htm
- [V] Autodesk DXF, LAYER: 290 "Plotting flag. If set to 0, do not plot this layer". https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-D94802B0-8BE8-4AC9-8054-17197688AFDB.htm
- [V] Autodesk, Getting Started "Layout": "create all viewport objects on a separate layer and then turn that layer off"; "Turn off the layer on which you created the layout viewport object. This hides the edges of the layout viewport". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-GettingStarted/files/GUID-DF5C5E9A-113E-456E-AFC4-4CEDAEE60A78.htm
- [V] Autodesk, formati "Full Bleed": "Plot using a Full Bleed page size, these have a margin set to 0 (zero)". https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-print-pdf-in-full-layout-in-AutoCAD.html
- [V] Autodesk: il file predefinito `DWG To PDF.pc3` si trova in `C:\Program Files\Autodesk\AutoCAD 20xx\UserDataCache\Plotters`. https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-add-a-new-AutoCAD-DWG-to-PDF-PC3-driver.html
- [M] Presentazione "A3" scritta con:
  - dispositivo `DWG To PDF.pc3`;
  - carta `ISO_full_bleed_A3_(420.00_x_297.00_MM)`;
  - margini 0, 420×297, scala 1/1, flag 672, tipo 5;
  - finestra con flag 16384;
  - presentazione attiva A3, `Layout1` eliminata, `$TILEMODE = 0`.
- [M] Il passaggio da ODA ha conservato tutto questo invariato. La resa 1:1 colloca la cornice esattamente a 10 mm.

**Incerto.**
- **Il nome canonico esatto delle carte A3/A2 di `DWG To PDF.pc3`.** `ISO_full_bleed_A3_(420.00_x_297.00_MM)` segue lo schema dei nomi canonici, ma non l'ho trovato in una pagina Autodesk. Per A2 presumo `ISO_full_bleed_A2_(594.00_x_420.00_MM)` [I].
- Che cosa fa AutoCAD se il nome carta non esiste nel PC3: probabilmente ricade su una carta predefinita e lo segnala nella finestra Imposta pagina [I].
- **Rimedio pratico.** Farsi mandare dal disegnatore un DXF salvato dal *suo* AutoCAD con una presentazione A3 e una A2 già impostate, e copiare i codici 1/2/4/7 della PLOTSETTINGS [D].
- Che `$TILEMODE = 0` apra il file direttamente sulla presentazione [I, da provare].
- Se usare `DWG To PDF.pc3` o il plotter reale del disegnatore: il suo PC3 ha nomi carta diversi [D].

---

## 3. Tipi di linea e scale

**Risposta breve.**

*Definizione.*
- Nella tabella LTYPE: codice 72 = 65 ("A"); 73 = numero di elementi; 40 = lunghezza totale; 49 = elementi. Positivo è tratto, negativo è spazio, 0 è punto.
- Le lunghezze sono in **unità di disegno**, quindi in mm.
- In ezdxf: `doc.linetypes.add("ACAD_ISO02W100", pattern=[15.0, 12.0, -3.0], description="ISO dash …")`.

*Scale.*
- Lunghezza effettiva = motivo × `$LTSCALE` × scala dell'entità (codice 48) [V: "based on both the global scale factor, and the linetype scale property"].
- `CELTSCALE` è solo il valore che ricevono le *nuove* entità.
- `PSLTSCALE`: con 1 le lunghezze in una finestra seguono le unità di carta, con 0 quelle del modello. In una finestra 1:1 le due cose coincidono, quindi PSLTSCALE è indifferente.
- `MSLTSCALE` scala i tipi di linea sul Modello secondo la scala di annotazione; con annotazione 1:1 non ha effetto [V + D].
- Proposta: `$LTSCALE = 1` e `$PSLTSCALE = 1`. La scala dell'entità si usa solo per la regola ISO della larghezza del pennino.

*Tipi ISO di `acadiso.lin`* (i nomi hanno il prefisso `ACAD_`):

| Nome | Descrizione | Definizione |
|---|---|---|
| ACAD_ISO02W100 | ISO dash | A,12,-3 |
| ACAD_ISO03W100 | dash space | A,12,-18 |
| ACAD_ISO04W100 | long-dash dot | A,24,-3,0,-3 |
| ACAD_ISO05W100 | long-dash double-dot | A,24,-3,0,-3,0,-3 |
| ACAD_ISO07W100 | dot | A,0,-3 |
| ACAD_ISO08W100 | long-dash short-dash | A,24,-3,6,-3 |
| ACAD_ISO10W100 | dash dot | A,12,-3,0,-3 |

- "W100" significa motivo definito per un pennino da 1 mm. Per 0,5 mm si usa scala 0,5, cioè 6/1,5 mm.
- Per confronto, in `acadiso.lin` DASHED è A,12.7,-6.35 e HIDDEN è A,6.35,-3.175.

*Come evitare il tratteggio "pieno".*
- Motivi in mm coerenti con `$INSUNITS = 4` e `$MEASUREMENT = 1`.
- **Non usare i tipi di linea di `setup=True` di ezdxf in un documento in mm** [M].
- Polilinee LWPOLYLINE con flag 128 (plinegen), così il motivo prosegue attraverso i vertici.
- Nessun tratto più corto di un motivo: con l'allineamento di tipo A un tratto troppo corto è disegnato continuo [V, M].
- Uno spazio del motivo più grande dello spessore della linea, altrimenti a stampa si chiude [D].
- Frecce e simboli non posati sugli spazi [M, §0].

*Come evitare il tratteggio "invisibile" o anomalo.*
- Il tipo di linea deve esistere nella tabella LTYPE. Un nome non definito viene rimosso da `ezdxf audit`, e anche ODA lo toglie in silenzio: la linea torna DALAYER, e nella prova è diventata continua [M].
- Niente tipi complessi con forme SHX che il disegnatore non ha: la forma sparisce [V].

**Fonti.**
- [V] Autodesk DXF, LTYPE: 72 "Alignment code; value is always 65", 73, 40 "Total pattern length", 49 "Dash, dot or space length", 74/75/340/46/50/44/45/9 per gli elementi complessi. https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-F57A316C-94A2-416C-8280-191E34B182AC.htm
- [V] Autodesk, tipi di linea semplici personalizzati:
  - esempio "a dash 0.5 drawing units long" (le unità sono quelle del disegno);
  - "The program supports only A-type alignment";
  - "If a line is too short to hold even one dash-dot sequence, a continuous line between the endpoints is drawn".
  - https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Customization/files/GUID-EF1DF0A9-2088-487C-8085-16FEE6425405.htm
- [V] Autodesk, tipi di linea personalizzati: "AutoCAD … acad.lin and acadiso.lin"; "AutoCAD LT product - acadlt.lin and acadltiso.lin". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Customization/files/GUID-5A6E6759-8A9A-4A8A-9AEE-EE9DB72F792D.htm
- [V] Autodesk, "About Linetypes":
  - "A line created with CELTSCALE = 2 in a drawing with LTSCALE set to 0.5 would appear the same as … CELTSCALE = 1 … LTSCALE = 1";
  - "If the linetype of an object looks solid even though you assigned a linetype with a pattern, you may need to specify a different linetype scale";
  - "do not mix imperial and metric linetypes";
  - PLINEGEN per il motivo continuo sui vertici.
  - https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-20B4D4B3-1220-426A-847B-5BBE36EC6FDF.htm
- [V] Autodesk, LTSCALE ("global linetype scale factor", iniziale 1): https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-88787AE5-957B-483C-9EEF-51564114181F.htm
- [V] Autodesk, CELTSCALE: https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-ECE175AB-AB7B-4DEC-9CEC-D5D67AF9310B.htm
- [V] Autodesk, PSLTSCALE (anche LT 2026):
  - "0 No special linetype scaling. Linetype dash lengths are based on the drawing units of the space … in which the objects were created";
  - "1 Viewport scaling governs linetype scaling. If TILEMODE is set to 0, dash lengths are based on paper space drawing units, even for objects in model space".
  - https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT/files/GUID-23EA4D64-AE7D-41E5-A8D0-20F060313D62.htm
- [V] Autodesk, MSLTSCALE: "Linetypes displayed on the Model tab are scaled by the annotation scale", iniziale 1. https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-023B046C-56EA-463C-A867-DF713666A69E.htm
- [V] Autodesk, PLINEGEN: "1 Generates linetypes in an uninterrupted pattern through the vertices of the polyline". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-352844E4-FBEA-44E0-B8F3-41C4187AD9C7.htm
- [V] Autodesk DXF, LWPOLYLINE: flag 70 "128 = Plinegen". https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-748FC305-F3F2-4F74-825A-61F04D757A50.htm
- [V] **Discrepanza.** L'intestazione DXF descrive `$PSLTSCALE` come "1 = No special linetype scaling; 0 = Viewport scaling governs linetype scaling", cioè l'opposto della guida della variabile di sistema. https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm
- [V] `acadiso.lin`, copia del file Autodesk ("Copyright 2017 Autodesk", AutoCAD 2018) nel repository netDxf. Contiene le definizioni ISO sopra e la nota "defined for an usage with a pen width of 1 mm … (e.g. pen width 0,5 mm -> ltscale 0.5)". https://github.com/haplokuon/netDxf/blob/master/TestDxfDocument/Support/acadiso.lin (letto dal file grezzo https://raw.githubusercontent.com/haplokuon/netDxf/master/TestDxfDocument/Support/acadiso.lin). È una copia di terzi del file Autodesk, non una pagina Autodesk.
- [V] ezdxf, tipi di linea: il formato `pattern = [total, e1, e2, …]`; "Complex line types with shapes only work if the associated shape file … and the DXF file are in the same directory". https://ezdxf.mozman.at/docs/tutorials/linetypes.html
- [V] ezdxf, scala dei tipi di linea: `$LTSCALE`; la scala per entità è supportata dalla R2000. https://ezdxf.mozman.at/docs/concepts/linetypes.html
- [M] Il sorgente ezdxf 1.4.4 (`tools/standards.py`) usa `ISO_LTYPE_FACTOR = 2.54`. Con `ezdxf.new("R2013", setup=True, units=MM)`, DASHED risulta `[1.524, 1.27, -0.254]`: 10 volte più corto del DASHED di `acadiso.lin`.
- [M] Nella resa 1:1 il tipo `ACAD_ISO02W100` ha dato tratti di 12,0 mm e spazi di 3,0 mm. Il tratto da 6 mm è uscito continuo.

**Incerto.**
- Il contenuto esatto di `acadltiso.lin` (quello di LT): i nomi ISO dovrebbero essere gli stessi, ma non l'ho verificato [I].
- Quanto spazio serve perché, a stampa, il tratteggio non si chiuda con spessori di 0,35–0,5 mm e le estremità arrotondate di AutoCAD [I/D].
- Il motivo del PDF attuale (il dasharray dell'SVG) non l'ho visto. Il DXF deve riprodurlo in mm. Se il motivo va cambiato per adottare quello ISO, è una **convenzione grafica: decide il PO**.

---

## 4. Testi e font

**Risposta breve.**
- Il DXF **non incorpora i font**: nomina solo il file (codice 3 della tabella STYLE, per esempio `arial.ttf` oppure `isocp.shx`).

*Arial TTF.*
- È un font di sistema di Windows: di fatto c'è sempre [D, nessuna fonte Autodesk trovata].
- Somiglia di più al PDF se il PDF usa Arial o Helvetica [D].
- Glifi pieni, accenti e Unicode completi [D].

*Font SHX.*
- `romans.shx`, `simplex.shx`, `isocp.shx`/`isoct.shx` e il TTF `isocpeur` sono nominati nella guida sia di AutoCAD 2026 sia di **AutoCAD LT 2026**. Quindi sono installati con entrambi [V + D].
- Pro: tratto singolo, aspetto "da CAD", si stampano con lo spessore della linea [D].
- Contro: copertura di glifi limitata (il diametro va scritto `%%c`), aspetto diverso dal PDF [D/I].
- Contro per la verifica: ezdxf su Linux non li rende senza i TTF equivalenti di Autodesk [V].

*Font mancante.*
- Un `.ttf` mancante passa dalla tabella di mappatura a "Windows substitutes a similar font".
- Un `.shx` mancante ricade su FONTALT, per default `simplex.shx` [V].

*Definizione.*
- `doc.styles.add("MEP_ARIAL", font="arial.ttf")`. L'altezza va messa in ogni testo, non nello stile (40 = 0 significa altezza non fissa).
- Usare R2007 o successiva per l'UTF-8, per à è ì ò ù e simboli [V §1].
- **Non** usare `setup=True`: imposta `$TEXTSTYLE = OpenSans` e stili OpenSans [M].

**Fonti.**
- [V] Autodesk DXF, STYLE: "3 Primary font file name", "4 Bigfont file name", "40 Fixed text height; 0 if not fixed", "1071 … truetype font's pitch and family…". https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-EF68AF7C-13EF-45A1-8175-ED6CE66C8FC9.htm
- [V] Autodesk, simboli di testo: "These text symbols are available in the following True Type (TTF) and SHX fonts: Simplex, Romans, gdt, amgdt, Isocp, Isocp2, Isocp3, Isoct, Isoct2, Isoct3, Isocpeur (TTF only) …".
  - AutoCAD 2026: https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-518E1A9D-398C-4A8A-AC32-2D85590CDBE1.htm
  - AutoCAD LT 2026, stesso elenco: https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT/files/GUID-518E1A9D-398C-4A8A-AC32-2D85590CDBE1.htm
- [V] Autodesk, font sostitutivi: "By default, the simplex.shx file is used" (FONTALT) e la tabella delle regole di sostituzione. https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-928DF015-1E04-4CC2-AF1B-0037548DFBAE.htm
- [V] ezdxf, stili di testo: "The DXF format does not and can not embed TTF fonts like the PDF format!"; "Do not include the path!"; "It is recommended that you do not rely on the default settings in the Textstyle entity". https://ezdxf.mozman.at/docs/tables/style_table_entry.html
- [V] ezdxf, font: "DXF relies on the infrastructure installed by AutoCAD like the included SHX files or True Type fonts". https://ezdxf.mozman.at/docs/concepts/fonts.html
- [V] ezdxf, FAQ: "only SHX fonts which have corresponding TTF-fonts can be rendered". https://ezdxf.mozman.at/docs/faq.html
- [M] Il sorgente ezdxf 1.4.4 (`fonts/fonts.py`) mappa `ISOCP.SHX` su `isocp.ttf` e `ROMANS.SHX` su `romans__.ttf`. Sono TTF di Autodesk, non distribuiti con ezdxf. Nella resa di prova il testo `isocp.shx` è uscito con un font di ripiego.

**Incerto.**
- Che `isocp.shx` segua ISO 3098 l'ho letto solo su siti non ufficiali [I].
- La copertura di à è ì ò ù e Ø negli SHX Autodesk [I].
- **La scelta Arial o ISOCP cambia l'aspetto della tavola: decide il PO.**

---

## 5. Blocchi

**Risposta breve.**

*Proprietà della geometria.*
- Mettere la geometria dei simboli sul **layer 0**, con colore e spessore **DAPERBLOCCO (BYBLOCK)**, e inserire il blocco sul layer del fluido o dei simboli con proprietà DALAYER. Il simbolo prende così l'aspetto del layer d'inserimento e resta sovrascrivibile sul singolo inserimento.
- In alternativa, layer 0 con DALAYER: eredita soltanto dal layer.
- Per i simboli che non devono diventare tratteggiati (una valvola sulla rete di acqua fredda) il tipo di linea va messo **Continuous esplicito**, non BYBLOCK [D].

*Punto base.*
- Sull'asse della tubazione, al centro o all'attacco del simbolo [D].
- Per la freccia, sulla punta o sul centro, con direzione +X, così la rotazione dell'inserimento è l'angolo del tratto [D].

*Nomi.*
- Prefisso univoco (per esempio `MEP_…`). Con lo stesso nome, AutoCAD usa la definizione già presente nel disegno.
- Niente caratteri `<>/\":;?*=` e backtick.

*Unità del blocco.*
- mm, cioè BLOCK_RECORD 70 = 4, uguale a `$INSUNITS`: nessuna scalatura [D da V].

*Attributi.*
- ATTDEF `SIGLA` nel blocco: tag univoco e senza spazi.
- In ezdxf: `add_blockref()` più `add_auto_attribs()`.
- **Evitare `add_auto_blockref()`**: incapsula in un blocco anonimo `*U…`, scomodo da ritoccare [V + D].

*Blocchi annidati.*
- Ammessi; valgono le stesse regole. I riferimenti circolari non sono permessi.

*Colori espliciti nel blocco.*
- Restano quelli, qualunque sia il layer d'inserimento, e si cambiano solo modificando il blocco.
- Se sono true color, per di più ignorano il CTB (§7).

**Fonti.**
- [V] Autodesk, "Block Object Properties Reference". Tabella: "Retain original properties: Any [layer] but 0 / Any but ByBlock or ByLayer"; "Inherit properties from the current layer: 0 / ByLayer"; "Inherit individual properties first, then layer properties: Any / ByBlock"; "… also affect the components of nested blocks". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-25E9F20C-D146-426C-8815-37DF48D2D33F.htm
- [V] Autodesk 2010, "Control the Color and Linetype Properties in Blocks": "The properties of objects in the block do not change regardless of the current settings… do not use BYBLOCK or BYLAYER…"; per ereditare dal layer "set the current layer to 0, and set the current color, linetype, and lineweight to BYLAYER". http://docs.autodesk.com/ACD/2010/ENU/AutoCAD%202010%20User%20Documentation/files/WS1a9193826455f5ffa23ce210c4a30acaf-6c53.htm
- [V] Autodesk, "About Defining Blocks": "A base point that's used for placing the block"; blocchi annidati; "circular references … are not allowed". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-F81D7F1E-1F0A-45AD-AC7E-891A85A0033A.htm
- [V] Autodesk, "About Organizing Blocks": "If you try to insert a block from another drawing that has the same name … the block definition in the current drawing will be used instead". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-9C9FF3BC-7275-44E8-93D4-00A2F50BC96D.htm
- [V] Autodesk, unità dei blocchi e scala d'inserimento: https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-6C46049D-8636-442D-8BAC-CF4FD515FDC0.htm
- [V] Autodesk DXF, BLOCK_RECORD ("70 Block insertion units", 280/281): https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-A1FD1934-7EF5-4D35-A4B0-F8AE54A9A20A.htm
- [V] Autodesk DXF, ATTDEF: "Tag string (cannot contain spaces)"; flag "1 invisible, 2 constant, 4 verification, 8 preset". https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-F0EA099B-6F88-4BCC-BEC7-247BA64838A4.htm
- [V] Autodesk, attributi: "make sure that attribute tags have unique names". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-67A2DDAD-2217-412F-8AEF-D4495192F45B.htm
- [V] Autodesk, EXTNAMES: "Names can be up to 255 characters … any special characters not used by the operating system and the product". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-8EC065EC-D551-4E02-9C5A-A33D1DB80B05.htm
- [V] Sorgente ezdxf (`lldxf/const.py`): ``INVALID_NAME_CHARACTERS = '<>/\\":;?*=`'`` (compreso il backtick).
- [V] ezdxf, blocchi: `add_attdef`, `add_auto_attribs`; `add_auto_blockref()` "wrapping the block reference and its attributes into an anonymous block". https://ezdxf.mozman.at/docs/tutorials/blocks.html
- [V] Autodesk, CTB monocromatico e colori: "Objects or layers have been assigned a True Color … This may be objects inside a block". Vedi §7.
- [M] Nella prova, le valvole (layer 0, BYBLOCK) inserite su `M-SIMBOLI` sono nere, e le frecce inserite sui layer dei fluidi prendono il colore del fluido. Gli attributi V01–V03 sono rimasti intatti dopo il passaggio da ODA.

---

## 6. Frecce del verso di flusso

**Risposta breve.** Consiglio un **blocco "freccia"** (triangolo pieno) inserito e ruotato sulla tubazione [D]. È il metodo dei software P&ID di Autodesk, dove "Flow Arrow" è un blocco [V].

*Confronto per l'editabilità* [D salvo dove indicato]:

| Metodo | Pro | Contro |
|---|---|---|
| **Blocco inserito e ruotato** (triangolo SOLID o HATCH dentro il blocco) | Si seleziona, sposta, ruota e cancella singolarmente. Si ridefinisce in un colpo solo. Stampa esatta. Resa corretta anche da ezdxf [M]. | Non è associato alla tubazione: se la linea si sposta o si inverte, la freccia va aggiustata a mano. |
| **SOLID o HATCH sciolto** | Semplice. | Nessuna identità di simbolo: centinaia di triangoli da modificare uno a uno. Il riempimento dipende da FILLMODE [V]. |
| **Tipo di linea complesso** (testo come ">" oppure forma da un file `.shx`) | Segue la linea quando si stira. REVERSE ne inverte il verso [V]. | Posizione e numero delle frecce dipendono da motivo e scala, non si scelgono. Problemi di verso sugli archi (serve la generazione continua) [V forum]. La forma richiede un `.shx` da consegnare, altrimenti "the linetype is loaded … but without the embedded shape" [V]. Il testo richiede lo stile di testo già presente [V]. ezdxf non rende né testo né forme nei tipi di linea, quindi la verifica non li vede [V]. |

**Fonti.**
- [V] Autodesk, Plant 3D/P&ID: "Navigate to P&ID Class Definitions > Non-Engineering Items > Flow Arrow. Click on Edit Block…". https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-add-a-P-ID-custom-flow-arrow-symbol-as-a-substitute-to-flow-arrow-in-AutoCAD-Plant-3D.html
- [V] Autodesk, testo nei tipi di linea: il formato `["text",style,S=,R=|U=|A=,X=,Y=]`; "Any text styles associated with a linetype must exist in the drawing before you load the linetype". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Customization/files/GUID-FEDCE7EB-4919-43AE-A54E-F3A293DD60CA.htm
- [V] Autodesk, forme nei tipi di linea: "If the file is not found, the linetype is loaded and can be used but without the embedded shape". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Customization/files/GUID-AF0613E6-5C8B-47F0-800C-8B2524BF2015.htm
- [V] Autodesk, REVERSE: "useful for linetypes with included text". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-EAE8C2C3-B780-4501-9CBD-C06346CC9F2E.htm
- [V] Autodesk, FILLMODE: "Specifies whether hatches and fills, 2D solids, and wide polylines are filled in", iniziale 1. https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-FC385D70-45AA-4B9A-848A-CA3906C36124.htm
- [V, forum non ufficiale] Autodesk Community, tipo di linea a frecce sbagliato sugli archi disegnati in senso orario; soluzione "Change the Linetype generation to enabled". https://forums.autodesk.com/t5/autocad-lt-forum/directional-flow-arrow-linetype/td-p/8503826
- [V] ezdxf drawing add-on: "Text and shapes in linetypes are not supported". https://ezdxf.mozman.at/docs/addons/drawing.html

---

## 7. Colori e stampa (CTB, STB, spessori)

**Risposta breve.**

*ACI contro true color.*
- ACI (codice 62) è un indice da 1 a 255; il true color (codice 420) è l'RGB esatto.
- Se ci sono entrambi, vince il true color.

*Oggetti in true color stampati con un CTB* (fonte Autodesk).
- **Il CTB non li governa.** Un CTB ha 255 stili, uno per ciascun ACI, e non si possono definire stili per colori oltre i 255.
- Autodesk documenta che con `monochrome.ctb` o `grayscale.ctb` gli oggetti in true color **stampano a colori**; causa: "Color assignments in CTB files use AutoCAD Index (256) colors".
- **Non** risulta alcuna mappatura sul pennino dell'ACI più vicino. L'unica frase Autodesk sul "nearest match" riguarda i true color assegnati *dentro* una tabella di stili, non gli oggetti.
- Rimedi indicati da Autodesk: usare colori ACI, oppure convertire il disegno a stili con nome, **STB** (CONVERTCTB e CONVERTPSTYLES). Gli STB possono avere stili per qualsiasi colore.
- **Conseguenza per noi** [D]:
  - true color sui layer dà colori esatti a video e a stampa con qualsiasi CTB, cioè stampa uguale al PDF;
  - il disegnatore però **non** ottiene il bianco e nero scegliendo `monochrome.ctb`;
  - servono le sovrascritture di colore per finestra, oppure STB, oppure layer in ACI.
  - È un compromesso da **decidere col PO**.
- Alternativa: layer in ACI più un CTB su misura che a stampa riassegna l'RGB esatto (un colore di stile può essere true color). Costo: installare il CTB sul PC del disegnatore, cioè preparazione [D da V].

*Nomi dei CTB.*
- Il CTB predefinito è `acad.ctb` in AutoCAD e `acadlt.ctb` in LT; `monochrome.ctb` c'è in entrambi.
- Nel DXF conviene non puntare ad `acad.ctb` [D].

*Spessori.*
- Codice 370 sul layer, entità DALAYER. Valori ammessi in 1/100 mm: 0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120, 140, 158, 200, 211.
- Se l'SVG usa 0,45 mm o 0,6 mm, va mappato su un valore ammesso [D].
- `$LWDISPLAY = 1` li mostra a video. Per default si stampano alla larghezza esatta.
- Nell'impostazione di pagina il flag 128 PrintLineweights (e 32 PlotPlotStyles) è attivo per default in ezdxf [M: flag 672].
- Un CTB o STB può sovrascrivere gli spessori se li definisce [V].

**Fonti.**
- [V] Autodesk, "Black and white (monochrome/grayscale) color-dependent plot style (CTB) plots color in AutoCAD products". Issue: "Objects in drawings plot color when using a black and white (monochrome) or grayscale … (CTB)". Cause: "Objects or layers have been assigned a True Color (RGB) value. Color assignments in CTB files use AutoCAD Index (256) colors. This may be objects inside a block". Soluzione: colori indice oppure CONVERTCTB e CONVERTPSTYLES. https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Plotting-True-Color-objects-in-monochrome.html
- [V] Autodesk, "Objects with color beyond standard 255 do not plot as expected from AutoCAD" (AutoCAD e AutoCAD LT, tutte le versioni):
  - "Color-dependent plot styles (CTB files) have 255 plot styles … Additional plot styles cannot be added…";
  - "there is no way to define a plot style for colors beyond the standard 255 colors using a color-dependent plot style table";
  - "Named plot styles can be created for any color … including true colors".
  - https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Objects-with-color-beyond-standard-255-do-not-plot-as-expected.html
- [V] Autodesk, "To Assign a Plot Style Color": "The default setting for plot style color is Use Object Color"; "If you use a plot style table saved in AutoCAD 2000 or later, the True Color values change to the nearest match in the current version's palette" (riguarda i colori *degli stili*). https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-4AD3C3B4-50A1-4B44-AF4D-BCFEDE4D7CBA.htm
- [V] Autodesk, CTB preinstallati:
  - AutoCAD 2026 ("acad.ctb Default plot style table … monochrome.ctb Plots all colors as black"): https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-F6DF548E-DF71-45F7-8DC5-A1EAD73998B1.htm
  - LT 2026 ("acadlt.ctb Default plot style table"): https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT/files/GUID-BEFF271C-3EDE-49E3-8BF1-EEE8A805ECBB.htm
- [V] Autodesk, "About Plot Style Tables": "There are 256 plot styles in a color-dependent plot style table"; negli STB "Named plot styles can be assigned to objects or layers". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-2FD01085-DDD8-49D2-A910-E63EA45A7FED.htm
- [V] Autodesk DXF, HEADER: `$PSTYLEMODE` "0 = … named plot style tables; 1 = … color-dependent"; `$LWDISPLAY`; `$CELWEIGHT`. https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm
- [V] Autodesk, LWDISPLAY ("0 Lineweights are not displayed", iniziale 0): https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-18CA6E8F-0008-402E-9F6B-2F9ED8A0A7DD.htm
- [V] Autodesk, "About Lineweights": "In a paper space layout, lineweights are displayed using real-world units"; "By default, lineweights are plotted with the exact width of the assigned lineweight value". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-4B33ACD3-F6DD-4CB5-8C55-D6D0D7130905.htm
- [V] ezdxf, spessori (valori ammessi, `$LWDISPLAY`, "can be overridden by CTB or STB files"): https://ezdxf.mozman.at/docs/concepts/lineweights.html
- [V, forum non ufficiale] Autodesk Community: "CTBs ignore 'true-colors', always have, still do"; "If you need to work with 'true colors' you need STB, not CTB"; "No CTB or STB installed with AutoCAD has lineweights assigned in it". https://forums.autodesk.com/t5/autocad-forum/lineweights-for-true-color/td-p/11866498
- [M] In un documento nuovo ezdxf 1.4.4 ha `$PSTYLEMODE = 1` (CTB) e il dizionario `ACAD_PLOTSTYLENAME` con "Normal". Un disegno in modalità STB sembra quindi scrivibile, ma non l'ho provato in AutoCAD [I].

**Incerto.**
- Con quale spessore o retinatura un CTB tratta un oggetto in true color: Autodesk dice solo che non si può definirgli uno stile. "Stampa com'è" è deduzione, sostenuta dal forum [I].
- Che cosa succede se la `current_style_sheet` nomina un CTB assente, per esempio `acad.ctb` in LT [I].

---

## 8. Immagine del logo (IMAGE e IMAGEDEF)

**Risposta breve.**

*Come funziona.*
- IMAGEDEF (codice 1, "File name of image") più IMAGE nel cartiglio. L'immagine **non è incorporata**.
- Scrivere il nome **senza percorso** (`logo.jpg`) e consegnare il JPEG **nella stessa cartella** del DXF. AutoCAD cerca nell'ordine:
  1. il percorso salvato;
  2. **la cartella del disegno**;
  3. i percorsi di progetto;
  4. i percorsi di supporto;
  5. la cartella di avvio.
- JPEG è un formato supportato. Serve R2000 o successiva.

*Se il file manca.*
- Nel pannello Riferimenti esterni compare "Not Found".
- Nel disegno resta solo la cornice, con il testo del percorso.

*Cornice.*
- RASTERVARIABLES 70 ("Display-image-frame flag: 0 = No frame; 1 = Display frame"). In ezdxf si imposta con `doc.set_raster_variables(frame=0, quality=1, units="mm")`.

*Alternative.*
- Incorporare come oggetto OLE: è il metodo Autodesk, Windows con Incolla speciale, ma ezdxf **non** supporta OLE [V].
- **Logo vettorializzato** in un blocco di HATCH e polilinee: non dipende da nessun file esterno [D].
- Pacchetto ZIP con DXF più `logo.jpg` [D].

**Fonti.**
- [V] ezdxf, immagini: "The raster image is NOT embedded in the DXF file!"; "The IMAGE entity requires the DXF R2000 format or later". https://ezdxf.mozman.at/docs/tutorials/image.html
- [V] Autodesk DXF, IMAGEDEF ("1 File name of image", "280 Image-is-loaded flag"): https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-EFE5319F-A71A-4612-9431-42B6C7C3941F.htm
- [V] Autodesk DXF, RASTERVARIABLES: https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-DDCC21A4-822A-469B-9954-1E1EC4F6DF82.htm
- [V] Autodesk, "About Changing the Path to Raster Images": l'ordine di ricerca sopra; "If you open a drawing that contains an image that is not in the saved path location or in any of the defined search paths, the External References palette displays Not Found". https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-327B966B-161E-429C-841F-BAC13E121367.htm
- [V] Autodesk, "Raster images are missing and not displayed…": "Only a boundary frame for the picture with a text pointing to the file path is shown instead"; suggerimento "Embed the image file instead of attaching it". https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Raster-images-are-missing-and-not-displayed-when-opening-a-drawing-in-AutoCAD.html
- [V] Autodesk, logo incorporato: "A raster image can be embedded in a DWG file as an OLE object… One example of this is when using a company logo as part of a title block" (Windows, PASTESPEC). https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Saving-raster-image-in-DWG-file-to-eliminate-need-for-external-image-file.html
- [V] Autodesk, formati raster supportati ("JPEG File Interchange Format .jpg, .jpeg", ".png"); da AutoCAD 2026 le immagini si caricano in background (IMAGEASYNC). https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/GUID-E6EDF33B-052A-4A7C-AF7B-870FC6303598.htm
- [V] ezdxf, FAQ, "Are OLE/OLE2 entities supported? TLDR; NO!": https://ezdxf.mozman.at/docs/faq.html
- [M] ODA ha conservato `logo.jpg` come nome nell'andata e ritorno. ezdxf l'ha reso trovandolo accanto al DXF.

**Incerto.** Che AutoCAD trovi `logo.jpg` senza percorso nella cartella del DXF lo dice l'ordine di ricerca Autodesk, ma non l'ho provato in AutoCAD [I].

---

## 9. Verifica senza AutoCAD

**Risposta breve.**

*1. ezdxf audit.*
- `ezdxf audit file.dxf` (oppure `doc.audit()`) controlla la struttura e ripara. Il modulo `ezdxf.recover` serve per i file rovinati.
- **Ha trovato** l'errore che ho inserito apposta (tipo di linea inesistente) [M].

*2. ODA File Converter.*
- Esiste per Linux: RPM, DEB e AppImage (versione 27.1 in questa data).
- Ha l'interfaccia a riga di comando: `ODAFileConverter "cartella_in" "cartella_out" ACAD2018 DWG 0 1 "*.DXF"` (versione, tipo, ricorsivo, audit, filtro).
- Su Linux serve un display, per esempio con `xvfb-run -a`.
- L'andata e ritorno DXF → DWG → DXF l'ho eseguita: riuscita e senza perdite [M].
- **Ma ripara in silenzio**: sul DXF difettoso ha dato esito 0, nessun `.err` e il tipo di linea rimosso [M]. Dimostra la *leggibilità*, non la correttezza.

*3. Resa con il modulo `drawing` di ezdxf.*
- `ezdxf draw` ha i backend matplotlib, qt, mupdf e custom_svg.
- **Per un confronto a 1:1 col PDF usare l'API**: `Page(420, 297, mm)` più `render_box` uguale al foglio, e un backend nuovo per ogni uscita [M].
- Limiti: niente testo o forme nei tipi di linea; SHX solo con i TTF Autodesk [V]. ezdxf fa partire il motivo dall'inizio della linea [M], mentre AutoCAD applica l'allineamento di tipo A, con un tratto a ciascun estremo [V]. Le posizioni dei tratti quindi differiscono.

*4. Motore Autodesk senza AutoCAD.*
- **DWG TrueView** (gratuito, **solo Windows**, apre DWG e DXF).
- **Autodesk Viewer** online (accetta DXF). Attenzione: carica il disegno nel cloud Autodesk [D].
- Per ezdxf, TrueView è il riferimento di "reliable DXF viewer".
- **La prova vera resta l'apertura e la stampa da parte del disegnatore.**

**Fonti.**
- [V] ezdxf, launcher: `ezdxf audit [-s] FILE`, `ezdxf draw [--backend {matplotlib,qt,mupdf,custom_svg}] [-l LAYOUT] [-o OUT] [--dpi DPI]`. https://ezdxf.mozman.at/docs/launcher.html
- [V] ezdxf, recover: "The read() and readfile() functions will repair as much flaws as possible and run the required audit process". https://ezdxf.mozman.at/docs/drawing/recover.html
- [V] ODA, pagina ufficiale:
  - "RPM DEB AppImage … Ubuntu 20.10 x64 or later. GLIBC version 2.28 or higher";
  - "ODA File Converter application features a graphical interface and a command-line interface, and accepts … Source directory, Target directory, Input file filter …, Output version/type, Recursive flag, Audit flag";
  - "If the audit flag is enabled, an audit/repair operation will be applied".
  - https://www.opendesign.com/guestfiles/oda_file_converter
- [V] ezdxf, add-on odafc: "on Linux you may have to install the xvfb package"; versioni ACAD2013 e ACAD2018; supporto AppImage via `unix_exec_path`. Il sorgente (`addons/odafc.py`) documenta l'ordine: `ODAFileConverter "Input Folder" "Output Folder" version type recurse audit [filter]`. https://ezdxf.mozman.at/docs/addons/odafc.html
- [V] ezdxf, "What is DXF": come applicazioni affidabili "AutoCAD and Trueview", quelle basate su ODA, BricsCAD; "not even ezdxf … is a reliable library in this sense". https://ezdxf.mozman.at/docs/concepts/dxf.html
- [V] ezdxf, drawing add-on (limiti, `PyMuPdfBackend`, `LinePolicy`: "Text and shapes in linetypes are not supported"): https://ezdxf.mozman.at/docs/addons/drawing.html
- [V] Autodesk, viewer: DWG TrueView "File type DWG, DXF … Platform Windows": https://www.autodesk.com/viewers
- [V] Autodesk Viewer, formati supportati (comprende DXF): https://help.autodesk.com/cloudhelp/ENU/ADSKVIEWER-Help/files/ADSKVIEWER_Help_SupportedFileTypes_html.html

**Misure [M]** (script in `prova/`, strumenti in `tools/` e `venv/`).
- `venv/bin/ezdxf audit prova/prova_A3.dxf` restituisce `No errors found.`
- `TMPDIR=… xvfb-run -a tools/squashfs-root/AppRun prova/oda_in prova/oda_dwg ACAD2018 DWG 0 1 prova_A3.dxf` esce con 0; `prova_A3.dwg` inizia con `AC1032`. L'AppImage di ODA è stata estratta con `--appimage-extract`: non serve FUSE.
- Il ritorno DWG → DXF con ODA è stato confrontato con ezdxf:
  - entità: Modello 10 INSERT, 5 LWPOLYLINE e 2 TEXT; carta 2 VIEWPORT, 2 LWPOLYLINE, 1 TEXT e 1 IMAGE;
  - RGB, spessori e tipo di linea dei layer invariati;
  - intestazione invariata;
  - impostazione di pagina, finestra bloccata, `logo.jpg`, attributi e font `arial.ttf` invariati;
  - resa PDF prima e dopo con 0 pixel diversi.
- DXF difettoso (LINE con tipo di linea "NONESISTENTE"):
  - ezdxf audit: `Removed undefined linetype nonesistente … applied 1 fixes`;
  - ODA: esito 0, nessun file `.err`, linea tornata DALAYER.
- `ezdxf draw --backend mupdf -l A3` ha prodotto una pagina di 399,7×276,9 mm, cioè l'ingombro del contenuto e non il foglio.
- Con l'API la pagina esce di 419,81×296,69 mm: arrotondata ai punti interi, 1190×841 pt [D sulla causa]. Tratti misurati 12,0/3,0 mm; cornice a 10,00 mm; colori RGB esatti.
- Stesso `PyMuPdfBackend` usato per una seconda uscita: la cornice finisce a 28,1 mm invece di 10 (circa 2,83×). Con un backend nuovo esce a 9,82 mm, cioè il bordo esterno della linea da 0,35 mm a 10 mm.
- Effetti collaterali:
  - ezdxf scrive una cache dei font in `~/.cache/ezdxf/font_manager_cache.json`, a meno che `XDG_CACHE_HOME` punti altrove;
  - matplotlib crea `~/.config/matplotlib`, a meno che sia impostato `MPLCONFIGDIR`;
  - `xvfb-run` crea `/tmp/.X11-unix`.
  - Li ho creati io in questa sessione e li ho rimossi.

---

## Incertezze da chiudere con il disegnatore (una prova su un file vero)

1. Il nome canonico delle carte A3/A2 di `DWG To PDF.pc3` e il comportamento se non esiste. Meglio farsi mandare un DXF di riferimento dal suo AutoCAD.
2. Che il file si apra sulla presentazione (`$TILEMODE = 0`) e che il logo venga trovato accanto al DXF.
3. La versione di AutoCAD o LT: da questa dipende la scelta R2013 o R2018.
4. L'aspetto dei testi (Arial o ISOCP) e le estremità delle linee spesse a stampa.
5. Come vuole il bianco e nero, visto che i true color ignorano `monochrome.ctb`.

---

## Proposta di impostazione (massimo 10 righe)

1. `ezdxf.new("R2013", setup=False, units=MM)`. Intestazione: `$MEASUREMENT = 1`, `$LTSCALE = 1`, `$PSLTSCALE = 1`, `$CELTSCALE = 1`, `$LWDISPLAY = 1`. Niente tipi e stili di `setup=True`.
2. Modello a 1:1 in mm di carta, con l'origine sul foglio. Presentazione "A3"/"A2": margini 0, `DWG To PDF.pc3`, nome carta canonico (da confermare), una finestra 1:1 bloccata su un layer dedicato (spento, oppure non stampabile), cartiglio in spazio carta, presentazione attiva, niente `Layout1`.
3. Un layer per fluido: true color esatto (420), ACI vicino come ripiego (62), spessore ammesso (370), tipo di linea. Entità DALAYER.
4. Tratteggi: LTYPE in mm uguale al dasharray del PDF (oppure `ACAD_ISO02W100` A,12,-3 con scala del pennino). LWPOLYLINE con flag 128. Frecce mai sugli spazi. Nessun tratto più corto del motivo.
5. Testi: stile `MEP_ARIAL` su `arial.ttf`, altezza in ogni entità. ISOCP solo se il PO lo sceglie.
6. Simboli come blocchi `MEP_*`: layer 0, colore e spessore BYBLOCK, tipo Continuous, unità mm, punto base sull'asse, ATTDEF `SIGLA`. `add_blockref` più `add_auto_attribs`, niente blocchi anonimi.
7. Frecce: blocco `MEP_FRECCIA_FLUSSO` (triangolo SOLID, punta su +X) inserito sul layer del fluido e ruotato secondo il tratto.
8. Logo: IMAGE con `logo.jpg` senza percorso, consegnato nella stessa cartella (ZIP), con `set_raster_variables(frame=0)`. A regime, meglio un logo vettoriale in un blocco.
9. Stampa: nessun CTB oppure `monochrome.ctb`, spiegando che i true color stampano comunque a colori. Il bianco e nero (STB o ACI) lo decide il PO.
10. Verifica a ogni rilascio: `ezdxf audit`, poi andata e ritorno con ODA (xvfb), poi resa ezdxf del foglio 1:1 affiancata al PDF. Il primo invio va aperto e stampato dal disegnatore (AutoCAD o TrueView).
