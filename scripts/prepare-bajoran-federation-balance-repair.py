from pathlib import Path
import re,json,hashlib,sys,contextlib,io
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=Path('D:/Xaramada-Modwork/bajor-federation-balance-repair');idx={p.name.lower():p for p in(root/'odf').rglob('*.odf')};cache={};files=[];summary=[]
def props(n,seen=None):
 n=n.lower();n=n if n.endswith('.odf')else n+'.odf'
 if n in cache:return cache[n]
 seen=set()if seen is None else seen
 if n in seen or n not in idx:return {}
 seen.add(n);s=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',s):d.update(props(inc,set(seen)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',s):d[k.lower()]=v.split('//')[0].strip()
 cache[n]=d;return d
def put(t,k,v):
 pat=r'(?mi)^'+re.escape(k)+r'[ \t]*=[^\r\n]*';return re.sub(pat,k+' = '+v,t)if re.search(pat,t)else t+'\n'+k+' = '+v+'\n'
def normalweapons(d):
 return [(int(k[6:]),v)for k,v in d.items()if re.fullmatch(r'weapon\d+',k)and v.strip('"')and props(v.strip('"')).get('special','0').strip('f')not in ['1','1.0']]
keys=set('maxhealth maxshields maxhull maxcrew shieldgeneratorhitpoints engineshitpoints weaponshitpoints lifesupporthitpoints sensorshitpoints shieldrate hullrate repairrate maxspecialenergy specialenergyrate dilithiumcost metalcost latinumcost biomattercost crewcost officercost buildtime sanecrewlossmethod weaponred weaponyellow'.split())
m=json.loads((repo/'bajor/rebuild-manifest.json').read_text(encoding='utf-8-sig'))
for u in m['units']:
 name=u['odf'];src='fente'if name=='bjnerys'else u['parent'];p=idx[name+'.odf'];t=p.read_text(encoding='latin1');fed=props(src);current=props(name);changed=[]
 for k,v in fed.items():
  if k in keys and re.fullmatch(r'[-+\d.eEfF]+',v):
   if current.get(k)!=v:t=put(t,k,v);changed.append(k)
 # Research pods inherit the exact Federation upgrade type, not custom multipliers.
 if name.startswith('bjpod'):
  native=idx[src+'.odf'].read_text(encoding='latin1');includes=re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',native)
  if includes:
   t=re.sub(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"','#include "'+includes[0]+'"',t)
  for k,v in fed.items():
   if any(x in k for x in ['upgrade','modifier','multiplier'])and re.fullmatch(r'[-+\d.eEfF]+',v):t=put(t,k,v);changed.append(k)
 # Normal weapon slots match the Federation counterpart; use current valid hardpoints.
 fw=sorted(normalweapons(fed));cw=sorted(normalweapons(current))
 if fw and cw and name not in ['bjfreight','bjcargo','bjrepair','bjcolony','bjconst']:
  specials=[(int(k[6:]),v)for k,v in current.items()if re.fullmatch(r'weapon\d+',k)and v.strip('"')and props(v.strip('"')).get('special','0').strip('f')in ['1','1.0']]
  if len(fw)+len(specials)>16:raise ValueError(name+' weapon limit')
  hp=[current.get('weaponhardpoints'+str(i),'"hp01"')for i,v in cw]
  # clear all explicit assignments; subsequent complete list overrides inherited slots.
  for i in range(1,max([i for i,v in cw+specials]+[len(fw)+len(specials)])+1):t=re.sub(r'(?mi)^weapon'+str(i)+r'[ \t]*=[^\r\n]*(?:\r?\n)?','',t)
  for j,(i,v)in enumerate(fw,1):t=put(t,'weapon'+str(j),v);t=put(t,'weaponHardpoints'+str(j),hp[(j-1)%len(hp)])
  for j,(i,v)in enumerate(specials,len(fw)+1):t=put(t,'weapon'+str(j),v);t=put(t,'weaponHardpoints'+str(j),current.get('weaponhardpoints'+str(i),hp[0]))
  changed.append('normalWeaponLayout')
 if name in ['bjyard','bjyard2','bjyard3']:
  t=put(t,'repairFacility','1');t=put(t,'repairHardpoint','"repair"');t=t.replace("//Even though we are a shipyard we don't have a repair facility",'// Accept friendly ships at the native repair docking point.');changed.append('repairEnabled')
 if not changed:continue
 rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()});summary.append({'unit':name,'federationEquivalent':src,'properties':changed,'federationNormalWeapons':[v for i,v in fw]})
r={'stage':str(stage),'files':files,'summary':summary,'applied':False,'runtimeVerified':False,'preserved':['Bajor artwork and race','special abilities and their research IDs','Kira Enterprise-E equivalent','custom freighter physics and visual scales']};(repo/'reports/bajoran-federation-balance-repair.json').write_text(json.dumps(r,indent=2));print('Prepared',len(files),'balanced definitions including three repair yards')
