from pathlib import Path
import json,re,shutil,subprocess,datetime
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
seq=[('dbase',1,0),('dconst',2,0),('dorbital',1,1),('dmining',1,1),('dfreight',2,0),('dyard',1,0),('dscout',1,0),('ddestroy',2,0),('dresear',1,0),('dcruise1',2,0),('dcruise2',1,0),('dcolony',1,0),('xduconst',1,0),('dyard2',1,0),('dresear2',1,0),('dupgrade',1,0),('dbattle',2,0),('dompod11',1,0),('dompod12',1,0),('dbattle2',2,0),('dtrading',1,0),('dyard3',1,0),('xhdhero',1,0),('dfreight',4,0),('ddestroy',6,0),('dbattle',4,0),('dbattle2',4,0)]
tech={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):tech[a[0].lower().removesuffix('.odf')]=[x.lower().removesuffix('.odf')for x in a[2:2+max(int(a[1]),0)]]
producers={}
for n in idx:
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower().removesuffix('.odf'),[]).append(n.removesuffix('.odf'))
avail={'dconst'};checks=[]
for n,q,base in seq:
 assert n+'.odf'in idx and n in tech,n
 assert set(tech[n])<=avail,(n,tech[n])
 assert any(p in avail for p in producers.get(n,[])),(n,producers.get(n))
 avail.add(n);checks.append({'unit':n,'prerequisites':tech[n],'producersAvailable':[p for p in producers[n]if p in avail]})
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('dominion-ai-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
text='// Dominion economy-first production recovery.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'+'\n'.join(f'    "{n}", {q}, {base}, -1, 0,'for n,q,base in seq)+'\n};\n'
for p in(root/'AI/AIPs').glob('dominion_*list.aip'):
 rel=p.relative_to(root);back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,back);p.write_text(text,encoding='latin1');assert p.read_text(encoding='latin1')==text;dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);files.append(str(rel))
report={'installed':True,'files':files,'backup':str(b),'findings':['Metal producer was after metal-heavy opening research/fleet expenditure.','Hero shipyard required dtrading which no plan ordered.','Finite lifetime row limits restricted replacement production.'],'dependencyChecks':checks,'gameplayVerified':False};(repo/'reports/dominion-ai-recovery.json').write_text(json.dumps(report,indent=2));p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Installed Dominion AI recovery: early metal/dilithium economy, missing trading prerequisite added, unlimited replacement build limits. Five profiles and 27 ordered dependencies validated; fresh-match AI test pending.';s['features'].append({'id':'dominion-ai-recovery','title':'Dominion AI recovery','steps':[{'label':'Check economy and prerequisites','done':True},{'label':'Install five build plans','done':True},{'label':'Gameplay test','done':False}]});s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled Dominion AI recovery, five profiles, 27 producer/tech checks passed. Runtime pending.\n')
print('Installed',len(files),'profiles;',len(checks),'dependency checks passed.')
