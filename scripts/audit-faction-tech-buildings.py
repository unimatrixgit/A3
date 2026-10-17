from pathlib import Path
import json,re
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
tech={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):
  tech[a[0].lower()]=None if int(a[1])<0 else[x.lower()for x in a[2:2+int(a[1])]]
races=['borg','fed','kling','rom','card','dominion','breen','bajoran','species8472'];out=[]
for racefile in races:
 rd=props(racefile);race=rd.get('name',racefile).lower();start={v.lower()for k,v in rd.items()if re.fullmatch('standardunits[0-9]+',k)};start={x if x.endswith('.odf')else x+'.odf'for x in start};reach=set(start);producers={};overflow=[]
 changed=True
 while changed:
  changed=False
  for n in list(reach):
   d=props(n)
   for k,v in d.items():
    if not re.fullmatch(r'(?:secondary)?builditem\d+',k):continue
    target=v.lower();target=target if target.endswith('.odf')else target+'.odf';td=props(target)
    if td.get('race',race).lower()!=race:continue
    producers.setdefault(target,set()).add(n)
    if k.startswith('builditem')and int(k[9:])>12:overflow.append({'producer':n,'target':target,'slot':k});continue
    req=tech.get(target)
    if req is not None and set(req)<=reach and target not in reach:reach.add(target);changed=True
 candidates=[]
 for n,p in idx.items():
  if p.parent.name.lower()!='stations':continue
  d=props(n)
  if d.get('race','').lower()!=race:continue
  if d.get('classlabel','').lower()not in ['research','techassim']and not re.search(r'(?:resear|upgrade|techass|omegalab)',n,re.I):continue
  if 'pod'in n:continue
  direct=[]
  for pn in idx:
   pd=props(pn)
   if pd.get('race','').lower()!=race:continue
   if any(v.lower().removesuffix('.odf')==n.removesuffix('.odf')for k,v in pd.items()if re.fullmatch(r'(?:secondary)?builditem\d+',k)):direct.append(pn)
  candidates.append({'unit':n,'name':d.get('unitname'),'reachable':n in reach,'producers':direct,'tech':tech.get(n),'missingPrerequisites':[x for x in tech.get(n,[])or[]if x not in reach]})
 out.append({'race':race,'starts':sorted(start),'reachableCount':len(reach),'techBuildings':candidates,'overflow':overflow})
report={'target':str(root),'scope':'Faction-specific research/upgrade/technology-assimilation stations; standard start, tech1 dependencies and first13 menu entries. Does not prove runtime construction.','races':out,'issues':[{'race':r['race'],**c}for r in out for c in r['techBuildings']if not c['reachable']]};(repo/'reports/faction-tech-building-reachability.json').write_text(json.dumps(report,indent=2));print(json.dumps({'buildings':sum(len(x['techBuildings'])for x in out),'issues':report['issues'],'overflows':[{'race':x['race'],'items':x['overflow']}for x in out if x['overflow']]},indent=2))
