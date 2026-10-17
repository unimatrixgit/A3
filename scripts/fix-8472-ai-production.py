from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
O=Path('D:/Xaramada-Modwork/8472-ai-recovery');O.mkdir(exist_ok=True)
p=root/'odf/ships/8472_mothership.odf';t=p.read_text(encoding='latin1');assert not re.search(r'buildItem2\s*=',t,re.I);t+='\n// Break constructor/yard bootstrap cycle; Species 8472 constructor only.\nbuildItem2 = "714const"\n';dest=O/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t,encoding='latin1')
tech={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):
  count=int(a[1]);tech[a[0].lower().removesuffix('.odf')]=[x.lower().removesuffix('.odf')for x in a[2:2+max(count,0)]]
producers={}
for n in idx:
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower().removesuffix('.odf'),[]).append(n.removesuffix('.odf'))
producers.setdefault('714const',[]).insert(0,'8472_mothership')
# Explicit economy-first evolution chain, followed by all required research and fleet types.
sequence=[('8472_mothership',1),('8472_active',2),('8472_passive',2),('8472_transmuter',1),('8472_collector',2),('714const',1),('8472_scout',2),('8472fig',2),('8472_destroy',2),('8472_basicresearch',1),('8472_cruise1',2),('8472_advancedresearch',1),('8472_cruise2',2),('8472_shipupgraderesearch',1),('8472_fluidicgate',1),('714syard',1),('714turr',2),('8472_defender',1),('8472_sentinel',2),('8472_frigate',2),('8472_battle',2),('8472_behemoth',1),('714rnode',1),('714skate',2),('714orca',1),('714hydra',1),('714tmat',1),('8472_mine',1),('xhs_yard3',1),('xhs_vanguard',1),('xhs_sentinel',1),('xhs_leviathan',1),('8472_podshipresearch1',1),('8472_podshipresearch2',1),('8472_podshipresearch3',1),('8472_podshipresearch4',1),('8472_podshipresearch21',1),('8472_podshipresearch22',1),('8472_podshipresearch23',1),('8472_podshipresearch24',1)]
available={'8472_mothership'};checks=[]
for n,qty in sequence:
 assert n+'.odf'in idx,n
 assert n in tech,n
 assert set(tech[n])<=available,(n,tech[n],available)
 ps=producers.get(n,[]);assert n in available or any(v in available for v in ps),(n,ps)
 available.add(n);checks.append({'unit':n,'quantity':qty,'prerequisites':tech[n],'availableProducers':[v for v in ps if v in available]})
for p in(root/'AI/AIPs').glob('species8472_*list.aip'):
 rows=[]
 for n,q in sequence:
  # Evolvers are consumed while constructing; maintain a small replacement supply.
  if n in ['8472_active','8472_passive']:q=3
  rows.append(f'    "{n}", {q}, 0, -1, 0,')
 text='// Species 8472 economy-first dependency-ordered recovery.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'+'\n'.join(rows)+'\n};\n';d=O/p.relative_to(root);d.parent.mkdir(parents=True,exist_ok=True);d.write_text(text,encoding='latin1')
files=[str(p.relative_to(O))for p in O.rglob('*')if p.is_file()];out={'target':str(root),'stage':str(O),'cause':['Constructor 714const and its only producer 714syard formed an unreachable cycle.','Cruisers were ordered before basic/advanced research and economy.'],'fix':['Mothership builds 714const; no universal assembler added.','Five AI profiles reordered economy first, then research, yards and fleet; technology checks enabled.'],'dependencyChecks':checks,'files':files,'gameplayVerified':False}
(repo/'reports/8472-ai-recovery.json').write_text(json.dumps(out,indent=2))
sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding="utf-8-sig"));s['current']='Species 8472 AI recovery staged: fixed constructor/yard bootstrap loop and dependency-ordered all five AI plans. Six files validated; waiting for game closure before install.';s['features'].append({'id':'8472-ai-recovery','title':'Species 8472 AI recovery','steps':[{'label':'Find production blockers','done':True},{'label':'Validate five build plans','done':True},{'label':'Install','done':False},{'label':'Gameplay test','done':False}]});s['steps']=[{'label':f['title']+': '+a['label'],'done':a['done']}for f in s['features']for a in f['steps']];sfile.write_text(json.dumps(s,indent=2),encoding="utf-8");print('Validated',len(files),'files and',len(checks),'ordered production dependencies.')


