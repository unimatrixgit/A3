from pathlib import Path
import re,json,hashlib
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
spr=root/'Sprites/gui_global.spr';text=spr.read_text(encoding='latin1');reference='256';material='default';records={}
for l in text.splitlines():
 s=l.strip()
 if s.lower().startswith('@reference='):reference=s.split('=',1)[1]
 elif s.lower().startswith('@tmaterial='):material=s.split('=',1)[1]
 else:
  a=s.split()
  if len(a)>=6 and not s.startswith(('#','//','@')):
   try:[int(v)for v in a[2:6]]
   except ValueError:continue
   records[a[0].lower()]={'row':a,'reference':reference,'material':material}
active=set()
for n in idx:
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):active.add(v.lower().removesuffix('.odf'))
added=[];unresolved=[]
for n in sorted(active):
 if n.startswith(('bj','xbj')):continue
 d=props(n);base=d.get('basename',n);base=base.lower();target='b_'+base
 source=next((x for x in ['b_'+n,'b_'+base.removeprefix('xvstock_')]if x in records),None)
 if target not in records:
  if source:
   r=records[source];row=[target]+r['row'][1:];text+='\n@skip=off\n@reference='+r['reference']+'\n@tmaterial='+r['material']+'\n'+' '.join(row)+'\n';records[target]={**r,'row':row};added.append({'unit':n,'alias':target,'source':source})
  else:unresolved.append({'unit':n,'baseName':base,'missingBuildIcon':True})
 for i in range(1,6):
  target=base+'w'+str(i);source=n+'w'+str(i)
  if target not in records and source in records:
   r=records[source];row=[target]+r['row'][1:];text+='\n@reference='+r['reference']+'\n@tmaterial='+r['material']+'\n'+' '.join(row)+'\n';records[target]={**r,'row':row};added.append({'unit':n,'alias':target,'source':source})
stage=Path('D:/Xaramada-Modwork/non-bajor-gui-aliases');stage.mkdir(exist_ok=True);p=stage/'gui_global.spr';p.write_bytes(text.replace('\r','').replace('\n','\r\n').encode('latin1'));r={'target':str(spr),'stage':str(p),'sourceSha256':hashlib.sha256(spr.read_bytes()).hexdigest(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'activeBuildTargets':len(active),'added':added,'unresolved':unresolved,'applied':False,'runtimeVerified':False};(repo/'reports/non-bajor-gui-aliases.json').write_text(json.dumps(r,indent=2));print(json.dumps({'activeTargets':len(active),'aliasesAdded':len(added),'unresolved':unresolved[:20],'unresolvedTotal':len(unresolved)}))
