from pathlib import Path
import re,json,hashlib
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=Path('D:/Xaramada-Modwork/bajor-durability-research');idx={p.name.lower():p for p in(root/'odf').rglob('*.odf')};m=json.loads((repo/'bajor/rebuild-manifest.json').read_text(encoding='utf-8-sig'));files=[];changes=[]
def props(n,seen=None):
 n=n.lower();n=n if n.endswith('.odf')else n+'.odf';seen=set()if seen is None else seen
 if n in seen or n not in idx:return {}
 seen.add(n);s=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^#include[ \t]+"([^"]+)"',s):d.update(props(inc,set(seen)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',s):d[k.lower()]=v.split('//')[0].strip()
 return d
def put(t,k,v):
 pat=r'(?mi)^'+k+r'[ \t]*=[^\r\n]*';return re.sub(pat,k+' = '+v,t)if re.search(pat,t)else t+'\n'+k+' = '+v+'\n'
for u in m['units']:
 n=u['odf'];p=idx[n+'.odf'];old=p.read_text(encoding='latin1');t=old;d=props(n);notes=[]
 research=n.startswith('bjpod')or n in ['bjresear','bjresear2','bjupgrade']
 if research:
  t=idx[u['parent']+'.odf'].read_text(encoding='latin1')
  # Clone Federation behavior; retain all Bajoran identity, visual and model-anchor properties.
  for k,v in d.items():
   if k in ['race','unitname','tooltip','verbosetooltip','basename','scalesod','possiblecraftnames']or'hardpoint'in k or k.startswith('event'):t=put(t,k,v)
  t=re.sub(r'(?i)\bfedpod(\d+)\b',r'bjpod\1',t)
  notes.append('Federation research definition cloned, Bajor visual identity retained')
 # Scale effective durability from current settings, including inherited values.
 for k,v in d.items():
  if k in ['maxhealth','maxshields','maxhull','shieldgeneratorhitpoints','engineshitpoints','weaponshitpoints','lifesupporthitpoints','sensorshitpoints','shieldrate']:
   try:value=float(v.rstrip('fF'))
   except ValueError:continue
   if value>0:t=put(t,k,format(value*(1.25 if k=='shieldrate'else 1.5),'.8g'));notes.append(k)
 if t==old:continue
 rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()});changes.append({'unit':n,'changes':notes})
(repo/'reports/bajoran-durability-research.json').write_text(json.dumps({'stage':str(stage),'files':files,'changes':changes,'applied':False,'runtimeVerified':False,'weaponDamageChanged':False,'iconsChanged':False},indent=2));print('Staged',len(files),'definitions; no live game changes')
