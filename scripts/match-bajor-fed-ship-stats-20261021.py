from pathlib import Path
import re,json,datetime,shutil
repo=Path('D:/aramada');root=Path('D:/armadaIII');idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def props(n,seen=()):
 n=Path(n.strip('"')).stem.lower()
 if n not in idx or n in seen:return {}
 t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(inc,seen+(n,)))
 for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]+)',t):d[k.lower()]=v.split('//')[0].strip()
 return d
def put(t,k,v):
 pat=r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*'
 return re.sub(pat,lambda m:k+' = '+v,t)if re.search(pat,t)else t+'\n'+k+' = '+v+'\n'
m=json.loads((repo/'bajor/rebuild-manifest.json').read_text(encoding='utf-8-sig'))
pairs={u['odf']:u['parent']for u in m['units']if u['folder']=='ships'}
pairs.update({'bjnerys':'fente','bjsuper':'fbattle','bjraider':'ffighter','bjlightship':'fdestroy','xbjuconst':'xfuconst'})
keys='maxhealth maxshields maxhull shieldrate hullrate repairrate maxspecialenergy specialenergyrate shieldgeneratorhitpoints engineshitpoints weaponshitpoints lifesupporthitpoints sensorshitpoints shieldgeneratorhitpercent engineshitpercent weaponshitpercent lifesupporthitpercent sensorshitpercent crewhitpercent hullhitpercent weaponred weaponyellow sanecrewlossmethod physicsfile rang es can'.split();keys=[k for k in keys if k not in ['rang','es','can']]+['rangescan','damagedscan']
backup=Path('D:/Xaramada-Modwork/backups')/('bajor-fed-stats-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
for unit,ref in pairs.items():
 assert unit in idx and ref in idx,(unit,ref)
 p=idx[unit];a=props(unit);b=props(ref);t=p.read_text(encoding='latin1');before=t;changes={}
 for key in keys:
  if key in b:
   if a.get(key)!=b[key]:changes[key]={'before':a.get(key),'after':b[key]}
   t=put(t,key,b[key])
 # Match normal combat battery to the counterpart, retaining Bajoran specials and utility loadouts.
 def slots(d):return sorted([(int(k[6:]),v)for k,v in d.items()if re.fullmatch(r'weapon\d+',k)])
 def special(w):return props(w).get('special','0').strip('"')=='1'
 normal=[(n,w)for n,w in slots(b)if not special(w)]
 if normal and unit not in ['bjfreight','bjcargo','bjcolony','bjconst','bjrepair','xbjuconst']:
  oldslots=slots(a);hps=[a.get('weaponhardpoints'+str(n),'"hp01"')for n,w in oldslots if not special(w)]
  retained=[(w,a.get('weaponhardpoints'+str(n),'"hp01"'))for n,w in oldslots if special(w)]
  load=[(w,hps[i%len(hps)]if hps else '"hp01"')for i,(n,w)in enumerate(normal)]+retained
  t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*','',t)
  for i,(w,hp)in enumerate(load,1):t=put(t,'weapon'+str(i),w);t=put(t,'weaponHardpoints'+str(i),hp)
  changes['normalWeapons']={'before':[w for n,w in oldslots if not special(w)],'after':[w for n,w in normal]}
 saved=backup/p.relative_to(root);saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.write_bytes(data);out=repo/'bajor/overlay'/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 actual=props(unit)
 for key in keys:
  if key in b:assert actual.get(key)==b[key],(unit,key)
 assert actual.get('basename')==a.get('basename') and actual.get('race')==a.get('race')
 rows.append({'unit':unit,'federationCounterpart':ref,'changes':changes})
(repo/'reports/bajor-fed-ship-stats-20261021.json').write_text(json.dumps({'target':str(root),'backup':str(backup),'ships':rows,'costsCrewArtworkResearchPreserved':True,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']=f'Bajoran ship combat, regeneration, energy, movement and normal batteries matched to Federation counterparts: {len(rows)} ships. Bajoran identity, specials, costs and research preserved. File checks passed; gameplay pending. Eight-player map next.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print('PASS:',len(rows),'Bajoran ships matched; models, identity, specials, costs and research preserved.')
