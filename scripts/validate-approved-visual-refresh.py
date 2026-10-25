from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
from collections import Counter
stage=Path('D:/Xaramada-Modwork/approved-visual-refresh-stage');overlay=stage/'overlay';pack=json.loads((stage/'manifest.json').read_text());P=json.loads((repo/'reports/visual-refresh-before.json').read_text());checks=[]
idx={p.stem.lower():p for p in(root/'odf').rglob('*')if p.suffix.lower()=='.odf'};idx.update({p.stem.lower():p for p in(overlay/'odf').rglob('*.odf')})
def props(path,seen=None):
 seen=set()if seen is None else seen
 if path in seen:return{}
 seen.add(path);t=path.read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(idx[Path(inc).stem.lower()],seen))
 for k,v in re.findall(r'(?mi)^[ \t]*([a-z][a-z0-9_]*)[ \t]*=[ \t]*(.*?)[ \t]*(?://.*)?$',t):d[k.lower()]=v.strip().strip('"')
 return d
def check(ok,label):
 assert ok,label
 checks.append(label)
sprite=(overlay/'Sprites/gui_global.spr').read_text(encoding='latin1')
spritekeys={m[1]:m[2].split()for m in re.finditer(r'(?mi)^(\S+)[ \t]+([^\r\n]+)',sprite)if not m[1].startswith(('@','#','//'))}
def modelread(p):
 try:return load(p)
 except Exception:
  with contextlib.redirect_stdout(io.StringIO()):return SodIO().read_file(str(p))
special_changes={'xfgconst','xbgconst','xfgserv','xbgserv','xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3'}
new=set(pack['newUnits']);newmodels={}
for row in pack['units']:
 n=row['unit'];d=props(idx[n]);m=modelread(overlay/'SOD'/(row['model']+'.sod'));newmodels[n]=m;nodes={z['id'].lower()for z in m.nodes};source=P[row['sourceUnit']];old=modelread(root/'SOD'/(source.get('basename',row['sourceUnit'])+'.sod'))
 check({z['id']for z in old.nodes}.issubset({z['id']for z in m.nodes}),n+': skeleton and hardpoint names retained')
 check(len(old.animation_transforms)==len(m.animation_transforms),n+': animation channels retained')
 if n not in new:
  allowed={'basename'}
  if n in ['xfgconst','xbgconst']:allowed|={'unitname','tooltip','verbosetooltip'};allowed|={k for k in set(P[n])|set(d)if re.fullmatch('builditem[0-9]+',k)}
  if n in ['xfgserv','xbgserv']:allowed|={k for k in set(P[n])|set(d)if re.fullmatch('builditem[0-9]+',k)}
  if n in ['xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:allowed|={'weapon'+str(i)for i in [2,3,4]}|{'weaponhardpoints'+str(i)for i in [2,3,4]}
  previous=props(Path(P[n]['file']))
  diffs={k:(previous.get(k),d.get(k))for k in set(previous)|set(d)if k not in allowed and previous.get(k)!=d.get(k)}
  check(not diffs,n+': gameplay preserved '+str(diffs))
 for node in m.nodes:
  if node['type']!='MESH':continue
  data=node['data'];v=data['vertices'];uv=data['texture_coordinates'];check(np.isfinite(v).all()and np.isfinite(uv).all(),n+': finite geometry / UVs')
  texture=overlay/'Textures/RGB'/(data['texture']+'.tga');check(texture.is_file(),n+': texture exists '+data['texture'])
  im=Image.open(texture);check(im.size==(256,256)and im.mode=='RGB',n+': native 256px RGB texture')
  if m.version>1.9101:check(data['bump_map']==1,n+': native diffuse texture layer flag')
  if row['kind']!='reskin':check(len(v)<=450,n+': conservative mesh size')
  for group in data['vertex_lighting_groups']:check(all(len(f)==3 and all(0<=vi<len(v)and 0<=ui<len(uv)for vi,ui in f)for f in group['faces']),n+': valid triangle indices')
 for k,value in d.items():
  if re.fullmatch('weapon[0-9]+',k):check(value.lower()in idx,n+': weapon exists '+value)
  if re.fullmatch('weaponhardpoints[0-9]+',k)or k.endswith('targethardpoints')or k in ['buildhardpoint','dockinghardpoint','repairhardpoint']:
   for hp in re.findall('[A-Za-z0-9_]+',value):check(hp.lower()in nodes,n+': referenced hardpoint '+hp)
 items={int(k[9:]):value for k,value in d.items()if re.fullmatch('builditem[0-9]+',k)}
 if items:check(len(items)<=14 and sorted(items)==list(range(len(items))),n+': ordered build menu within capacity')
 for item in items.values():check(item.lower()in idx,n+': build target '+item)
 for key in ['b_'+n,'b_'+row['model']]+[p+'w'+str(i)for p in [n,row['model']]for i in range(1,6)]:
  check(key in spritekeys,n+': GUI sprite '+key);tex=spritekeys[key][0];path=overlay/'Textures/RGB'/(tex+'.tga');check(path.is_file(),n+': GUI texture exists '+tex)
for n in ['xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:
 d=props(idx[n]);check(d['weapon1']==P[n]['weapon1']and d['weaponhardpoints1']==P[n]['weaponhardpoints1'],n+': mining beam and its hardpoint unchanged')
 check([d['weapon'+str(i)]for i in [2,3,4]]==['xfgcruisb','xfgcruisb','xfgcruist'],n+': two beams and one photon added')
for prefix in ['xfg','xbg']:
 primary=props(idx[prefix+'const']);secondary=props(idx[prefix+'const2']);service=props(idx[prefix+'serv']);ref=props(idx[prefix+'dref'])
 check(any(v==prefix+'const2'for k,v in service.items()if k.startswith('builditem')),prefix+': secondary constructor buildable')
 check(ref['classlabel']=='mining'and ref['resourcescanhandle']=='dilithium',prefix+': actual DIL refinery function')
 check(ref['freightername']==prefix+'dil2',prefix+': correct miner faction / price variant')
 check(any(v==prefix+'dref'for k,v in primary.items()if k.startswith('builditem')),prefix+': refinery on primary constructor')
 if prefix=='xbg':check(secondary['latinumcost']=='0'and ref['latinumcost']=='0',prefix+': Borg never pays Latinum')
 else:check(secondary['dilithiumcost']=='0'and secondary['metalcost']=='0'and ref['dilithiumcost']=='0'and ref['metalcost']=='0',prefix+': Latinum-only Ferengi resource prices')
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 t=(overlay/'techtree'/(tree+'.tt')).read_text(encoding='latin1')
 for unit in pack['newUnits']:
  lines=re.findall(r'(?mi)^'+unit+r'\.odf\s+([^\r\n/]+)',t);check(len(lines)==1,tree+': single technology entry '+unit);rule=lines[0].split();check(int(rule[0])==len(rule)-1,tree+': valid prerequisite count '+unit)
  for dep in rule[1:]:check(Path(dep).stem.lower()in idx,tree+': prerequisite exists '+dep)
for aip in(overlay/'AI/AIPs').glob('*.aip'):
 t=aip.read_text(encoding='latin1')
 for prefix in ['xfg','xbg']:
  if '"'+prefix+'serv"'in t:check('"'+prefix+'const2"'in t and '"'+prefix+'dref"'in t,aip.name+': secondary constructor and refinery included')
for rel,h in pack['files'].items():check(hashlib.sha256((overlay/rel).read_bytes()).hexdigest()==h,'staged hash '+rel)
for rel,h in pack['sourceHashes'].items():check(hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,'live baseline unchanged '+rel)
check(not any('start'in Path(rel).stem.lower()and rel.lower().endswith('.odf')for rel in pack['files']),'no starting-fleet changes')
result={'status':'PASS','checks':len(checks),'models':len(pack['units']),'files':len(pack['files']),'kinds':dict(Counter(r['kind']for r in pack['units'])),'runtimeVerified':False,'details':checks};(stage/'validation.json').write_text(json.dumps(result,indent=2));(repo/'reports/approved-visual-refresh-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='details'}))
