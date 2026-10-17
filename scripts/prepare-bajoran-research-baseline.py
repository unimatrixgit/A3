from pathlib import Path
import re,json,hashlib
exec(Path('D:/aramada/scripts/prepare-bajoran-durability-research.py').read_text().split("for u in m['units']:")[0])
stage=Path('D:/Xaramada-Modwork/bajor-research-baseline');files=[];checks=[];keys=set('maxhealth maxshields maxhull maxcrew shieldgeneratorhitpoints engineshitpoints weaponshitpoints lifesupporthitpoints sensorshitpoints shieldrate hullrate repairrate maxspecialenergy specialenergyrate dilithiumcost metalcost latinumcost biomattercost crewcost officercost buildtime sanecrewlossmethod weaponred weaponyellow'.split())
for u in m['units']:
 name=u['odf'];src='fente'if name=='bjnerys'else u['parent'];fed=props(src);p=idx[name+'.odf'];old=p.read_text(encoding='latin1');t=old
 # Make the native research mechanism explicit, preserving visuals and Bajor race.
 if name.startswith('bjpod'):
  for k in ['isshipupgrade','upgradelevel','upgrademultiplier','upgradesystem']:
   if k in fed:t=put(t,k,fed[k]);checks.append({'unit':name,'setting':k,'value':fed[k]})
 for k,v in fed.items():
  if k in keys and re.fullmatch(r'[-+\d.eEfF]+',v):t=put(t,k,v)
 if t==old:continue
 rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
r={'stage':str(stage),'files':files,'researchSettings':checks,'applied':False,'runtimeVerified':False,'sequence':['Resolve native Federation research settings explicitly','Match base numeric stats to counterpart'],'preserved':['Bajoran visuals and icons','utility weapon slots','repair-enabled yards','freighter custom physics','Kira Enterprise-E baseline']};(repo/'reports/bajoran-research-baseline.json').write_text(json.dumps(r,indent=2));print('Staged',len(files),'files;',len(checks),'explicit native research settings')
