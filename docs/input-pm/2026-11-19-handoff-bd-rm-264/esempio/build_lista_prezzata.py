#!/usr/bin/env python3
import os, sys, json, re, tempfile
SKILL_REF='/root/.claude/skills/synced/573b1397-0283-4afc-961c-43c7904e6340_78f9ba77-9f3a-4dc7-8cb9-caece0bf6847/nove-c-report/references'
sys.path.insert(0, SKILL_REF)
from nove_c_report_cover import build_cover_pdf
from nove_c_report_engine import *
import nove_c_report_engine as _eng
from nove_c_report_qa import qa_pdf
TMP=tempfile.mkdtemp(prefix='novec_')
_eng._DOC_HEADER_RIGHT[:]=['noveC — Lista materiali prezzata BD.RM.264','Novembre 2026']
d=json.load(open('/tmp/mep/bd-rm-264/distinta2/interno/costo-minuteria.json'))
def forn(conto):
    f=re.findall(r'\((Tecnomat|Idrosanitaria|Abbattista|riferimento online)',conto)
    f=['Online' if x=='riferimento online' else x for x in f]
    out=[]
    for x in f:
        if x not in out: out.append(x)
    return ' / '.join(out) or '—'
R={r['rif']:r for r in d['righe']}
def row(rif, voce, q, um, fo, pu):
    return dict(rif=rif, voce=voce, q=q, um=um, fo=fo, pu=pu, tot=None if pu is None else round(q*pu,2))
sec={}
sec['Pompa di calore']=[row('P.1','Pompa di calore aria-acqua monoblocco Shenling ThermaX R290 9 kW (HPM-V90W/R3)',1,'n','Shenling',2450.00)]
sec['Apparecchiature']=[
 row('A.1','Bollitore ACS Cordivari Bolly 1 XL WB 200 l, serpentino 2 m²',1,'n','Idrosanitaria',546.00),
 row('A.2','Volano termico Cordivari VB 50 l a 4 attacchi',1,'n','Idrosanitaria',95.00),
 row('A.3','Circolatore DAB Evosta 2 40-70/130 1"',1,'n','Idrosanitaria',93.60),
 row('A.4','Cronotermostato ambiente BPT settimanale wifi',1,'n','Tecnomat',56.56)]
fix={'I.2':('Guaina isolante elastomerica per tubo multistrato MS 20×2',8,'m','Tecnomat',2.355),
     'I.5':None,
     'I.11':('Guaina isolante elastomerica per tubo multistrato MS 26×3',4,'m','Tecnomat',2.79),
     'I.26':('Miscelatore termostatico sanitario ¾" (Giacomini DR156)',1,'n','Tecnomat',46.30)}
idr=[]; el=[]
um={'n':'n','m':'m'}
for r in d['righe']:
    rf=r['rif']
    if rf.startswith('I.'):
        if rf in fix:
            if fix[rf] is None: continue
            v,q,u,fo,pu=fix[rf]; idr.append(row(rf,v,q,u,fo,pu)); continue
        v=re.sub(r'\s*\((riserva|guaina[^)]*)\)','',r['testo']).replace(', a corpo','').replace(' DA DEFINIRE (attacco)','')
        idr.append(row(rf,v,r['quantita'],r['um'],forn(r['conto']),r['unitario_eur']))
    elif rf.startswith('E.'):
        v=r['testo']
        v=re.sub(r'^(Cavo FG16OR16 3G1,5).*',r'\1 (comandi relè e deviatrice, alimentazione circolatore)',v)
        v=re.sub(r'^(Cavo FG16OR16 3G4).*',r'\1 (alimentazione pompa di calore)',v)
        v=re.sub(r'^(Cavo 2×0,75).*',r'\1 (sonde e termostato)',v)
        el.append(row(rf,v,r['quantita'],r['um'],forn(r['conto']),r['unitario_eur']))
# canapa e pasta: due articoli, due fornitori
_n=[]
for x in idr:
    if x['voce'].startswith('Canapa e pasta'):
        _n.append(row(x['rif'],'Canapa per raccordi filettati',1,'n','Tecnomat',3.07))
        _n.append(row(x['rif'],'Pasta sigillante per raccordi filettati',1,'n','Idrosanitaria',2.63))
    else: _n.append(x)
idr=_n
# rinumera
for i,x in enumerate(idr,1): x['rif']=f'I.{i}'
for i,x in enumerate(el,1): x['rif']=f'E.{i}'
sec['Circuito idraulico']=idr
sec['Elettrico']=el
sec['Staffaggi']=[row('S.1','Piedini antivibranti per l\'unità esterna',4,'n','Tecnomat',1.62)]
tot={k:round(sum(x['tot'] or 0 for x in v),2) for k,v in sec.items()}
G=round(sum(tot.values()),2)
json.dump({'sezioni':sec,'totali':tot,'totale':G},open('/home/claude/listino/dati.json','w'),ensure_ascii=False,indent=1)
def e(v): return '—' if v is None else eur(v)
def qfmt(q): return (f'{q:.0f}' if abs(q-round(q))<1e-9 else f'{q:.1f}'.replace('.',','))
W=cols(0.07,0.44,0.06,0.07,0.14,0.10,0.12)
def tab(rows):
    h=['Rif.','Voce','UM','Q.tà','Fornitore','€ unit.','€ totale']
    body=[[x['rif'],x['voce'],x['um'],qfmt(x['q']),x['fo'],P(e(x['pu']),'table_cell_r'),P(e(x['tot']),'table_cell_r')] for x in rows]
    return std_table(h,body,W)
def build_document():
    story=[]; n=1
    qe=[[k,P(eur(tot[k]),'table_cell_r'),P(eur(round(tot[k]*0.22,2)),'table_cell_r'),P(eur(round(tot[k]*1.22,2)),'table_cell_r')] for k in sec]
    qe.append([P('<b>Totale</b>','table_bold'),P(f'<b>{eur(G)}</b>','table_bold_r'),P(f'<b>{eur(round(G*0.22,2))}</b>','table_bold_r'),P(f'<b>{eur(round(G*1.22,2))}</b>','table_bold_r')])
    story+=chapter(n,'Quadro economico riepilogativo',[
        kv_table([('Commessa','BD.RM.264 — Sostituzione caldaia con pompa di calore, int. 28'),('Committente','Daniele Gianni'),('Indirizzo','Via di San Giovanni in Laterano 28, Roma (RM)'),('Prezzi','Prezzi netti d\'acquisto Nove C, listino interno rev. 07 del 18/11/2026; ogni articolo dal fornitore più economico')]),
        sp(4), std_table(['Capitolo','Netto €','IVA 22% €','Totale IVA inclusa €'],qe,cols(0.46,0.18,0.16,0.20))])
    k=n+1
    for name in sec:
        story+=chapter(k,name,[tab(sec[name])], keep='first' if len(sec[name])>12 else 'all'); k+=1
    ordini={}
    for v in sec.values():
        for x in v:
            if x['tot'] is None: continue
            o=ordini.setdefault(x['fo'],[0,0.0]); o[0]+=1; o[1]=round(o[1]+x['tot'],2)
    ordine=sorted(ordini.items(), key=lambda kv:-kv[1][1])
    rr=[[f if f!='Online' else 'Online (nessuno dei fornitori lo ha a listino)',str(n),P(eur(t),'table_cell_r'),P(eur(round(t*0.22,2)),'table_cell_r'),P(eur(round(t*1.22,2)),'table_cell_r')] for f,(n,t) in ordine]
    rr.append([P('<b>Totale</b>','table_bold'),str(sum(n for n,_ in ordini.values())),P(f'<b>{eur(G)}</b>','table_bold_r'),P(f'<b>{eur(round(G*0.22,2))}</b>','table_bold_r'),P(f'<b>{eur(round(G*1.22,2))}</b>','table_bold_r')])
    story+=chapter(k,'Recap ordini',[std_table(['Fornitore','Articoli','Netto €','IVA 22% €','Totale IVA inclusa €'],rr,cols(0.38,0.10,0.16,0.16,0.20))])
    return story
def main():
    cvr=os.path.join(TMP,'cover.pdf'); bdy=os.path.join(TMP,'body.pdf')
    out='/mnt/user-data/outputs/mep/BD.RM.264_Lista_materiali_prezzata_rev04.pdf'
    build_cover_pdf(cvr,TITLE_L1='Lista materiali',TITLE_L2='prezzata',TITLE_L3='Commessa BD.RM.264',
        SUBTITLE='PdC Shenling 9 kW  ·  Bollitore 200 l  ·  Volano 50 l',
        BOX_HEAD='USO INTERNO  ·  PREZZI NETTI D\'ACQUISTO',
        BOX_TXT1='Sostituzione caldaia con pompa di calore, int. 28 — Via di San Giovanni in Laterano 28, Roma.',
        BOX_TXT2='Fornitori: Shenling, Idrosanitaria, Tecnomat.',
        KPI_DATA=((eur(G).replace('€','').strip(),'euro netti','Totale materiali','oltre IVA'),
                  ('9 kW','Shenling R290','Pompa di calore','ThermaX'),
                  ('3','fornitori','Ordini','più economico per voce'),
                  (str(sum(len(v) for v in sec.values())),'voci','Lista materiali','quantità nette')),
        FTR_RIGHT='BD.RM.264 — Novembre 2026')
    story=build_document()
    validate_story(story,label='listino')
    doc=make_doc(bdy); doc.build(story); fill_report(doc)
    merge_pdf(out,cvr,bdy,title='BD.RM.264 Lista materiali prezzata')
    rep=qa_pdf(out,offer=False)
    print('ISSUES',rep.get('issues')); print(rep.get('pngs'))
    print('TOT',tot,G)
main()
