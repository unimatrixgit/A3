from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast
from collections import Counter
stage=repo/'patches/mining-yards-20261025';O=stage/'overlay';pack=json.loads((stage/'gameplay.json').read_text());art=json.loads((stage/'artwork.json').read_text());checks=[]
source=(repo/'scripts/stage-approved-visual-refresh.py').read_text()
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef)and node.name in ['load_model','visible_points']:exec(compile(ast.Module(body=[node],type_ignores=[]),str(repo/'scripts/stage-approved-visual-refresh.py'),'exec'))
native={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};idx=dict(native);idx.update({p.stem.lower():p for p in(O/'odf').rglob('*.odf')})
def props(n,table=idx,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);text=table[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',text):d.update(props(Path(inc).stem.lower(),table,seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',text):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
P={n:props(n)for n in idx}
def ck(ok,label):
 assert ok,label
 checks.append(label)
def number(x):return float(str(x).rstrip('fF;'))
sprite=(O/'Sprites/gui_global.spr').read_text(encoding='latin1');keys={m[1].lower():m[2].split()for m in re.finditer(r'(?mi)^(\S+)[ \t]+([^\r\n]+)',sprite)if not m[1].startswith(('@','#','//'))}
texidx={p.stem.lower():p for p in(root/'Textures').rglob('*.tga')};texidx.update({p.stem.lower():p for p in(O/'Textures').rglob('*.tga')})
for cfg in pack['yards']:
 n=cfg['yard'];d=P[n];menu=[d['builditem'+str(i)]for i in range(3)]
 ck(menu==cfg['miners']and 'builditem3'not in d,n+': exactly Basic / MK II / MK III native miners')
 ck(not any(x.startswith(('xfg','xbg'))for x in menu),n+': no Ferengi miners in native yards')
 for b in cfg['builders']:ck(n in P[b].values(),b+': builds '+n)
 for i,unit in enumerate(cfg['miners']):
  u=P[unit];ck(u['classlabel']=='freighter',unit+': true miner AI class')
  capacity='maxbiomatter'if cfg['race']=='species8472'else'maxdilithium';base=number(P[cfg['miners'][0]][capacity]);ck(number(u[capacity])==round(base*(1+i*.5)),unit+': tier capacity')
  for key in ['crewcost','maximumcrew','maxhealth','shieldrate','physicsfile','scalesod','basename']:
   old=props(unit,native)if unit in native else props(cfg['miners'][0],native)
   ck(u.get(key)==old.get(key),unit+': preserves '+key)
  ck('b_'+unit in keys,unit+': build icon exists')
  for j in range(1,6):ck(unit+'w'+str(j)in keys,unit+': full queue/status portrait '+str(j))
 for i,unit in enumerate(cfg['miners'][1:],1):
  if cfg['race']=='species8472':continue
  old=props(cfg['miners'][0],native);u=P[unit];found=0
  for key,w in old.items():
   if not re.fullmatch(r'weapon\d+',key)or'dilithium'not in w.lower():continue
   oldord=P[w.lower()]['ordname'].lower();neword=P[u[key].lower()]['ordname'].lower()
   ck(abs(number(P[neword]['damagebase'])/number(P[oldord]['damagebase'])-(1+i*.5))<1e-8,unit+': extraction multiplier');found+=1
  ck(found>0,unit+': original dilithium beam upgraded')
for row in pack['refits']:
 s=row['source'];target=row['target'];w=row['weapon'];d=P[s];wd=P[w]
 ck(wd['classlabel']=='fusingweapon'and wd['fusedclass']==target and wd['multireqclass0']==s and wd['multireqmin0']=='1',s+': one-unit NX refit')
 ck(wd['specialenergycost']=='0',s+': refit usable with zero special energy')
 banks=sorted((int(k[6:]),v.lower())for k,v in d.items()if re.fullmatch(r'weapon\d+',k));ck([i for i,v in banks]==list(range(1,len(banks)+1)),s+': contiguous weapon banks')
 ck(sum(P[v].get('classlabel')=='fusingweapon'for i,v in banks)==1,s+': exactly one refit button')
 slots=[P[v].get('buttonslot','0')for i,v in banks if P[v].get('buttonslot','0')!='0'];ck(len(set(slots))==len(slots),s+': no special button collisions')
 ck('b_'+w in keys,w+': upgrade icon')
 # Original beams, ordinary weapons and transwarp remain ahead of the appended refit.
 if s in native:
  old=props(s,native)
  for key,v in old.items():
   if re.fullmatch(r'weapon\d+|weaponhardpoints\d+',key):ck(d.get(key)==v,s+': original '+key)
fedmodel=load_model(O/'SOD/my26_fresear2.sod');fednodes={n['id'].lower()for n in fedmodel.nodes};fedpods=re.findall(r'[A-Za-z0-9_]+',P['fresear2']['podhardpoints'])
ck(len(fedpods)==6 and len(set(fedpods))==6,'Federation research: six separate persistent pod sockets')
for hp in fedpods:ck(hp.lower()in fednodes,'Federation research: pod anchor '+hp)
ck(P['fresear2']['builditem4']=='myfpod1'and P['fresear2']['builditem5']=='myfpod2','Federation: two independent mining research pods')
for row in art:
 n=row['unit'];d=P[n];model=load_model(O/'SOD'/(row['model']+'.sod'));nodes={z['id'].lower()for z in model.nodes}
 for key in ['buildhardpoint','repairhardpoint']:
  ck(d.get(key,'').lower()in nodes,n+': '+key+' exists')
 for node in model.nodes:
  if node['type']!='MESH':continue
  data=node['data'];ck(len(data['vertices'])<=450,n+': native mesh size');ck(np.isfinite(data['vertices']).all(),n+': finite hull coordinates')
  ck(data['texture'].lower()in texidx,n+': texture '+data['texture'])
  im=Image.open(texidx[data['texture'].lower()]);ck(im.size==(256,256)and im.mode=='RGB',n+': compatible diffuse texture')
  if model.version>1.9101:ck(data['bump_map']==1,n+': native texture-layer flag')
  for group in data['vertex_lighting_groups']:ck(all(all(0<=v<len(data['vertices'])and 0<=u<len(data['texture_coordinates'])for v,u in face)for face in group['faces']),n+': triangle indices')
 for key in ['b_'+n,'b_'+row['model']]+[p+'w'+str(i)for p in [n,row['model']]for i in range(1,6)]:
  ck(key in keys,n+': sprite '+key);tex=keys[key][0].lower();ck(tex in texidx,n+': sprite texture');im=Image.open(texidx[tex]);ck(im.size==(64,64)and im.mode=='RGB',n+': full RGB portrait / icon')
 if row['serviceStarbase']:
  old=props(n,native)
  for key in ['dilithiumcost','metalcost','latinumcost','crewcost','maximumcrew','maxhealth','shieldrate','scalesod']:
   ck(d.get(key)==old.get(key),n+': starbase-like artwork preserves '+key)
  oldmenu={v for k,v in old.items()if re.fullmatch(r'builditem\d+',k)};newmenu={v for k,v in d.items()if re.fullmatch(r'builditem\d+',k)};ck(oldmenu<=newmenu,n+': all prior Service Yard functions retained')
for file in(O/'techtree').glob('*.tt'):
 text=file.read_text(encoding='latin1');rules={}
 for n in pack['gates']:
  matches=re.findall(r'(?mi)^'+re.escape(n)+r'\.odf[ \t]+([^\r\n/]+)',text);ck(len(matches)==1,file.name+': unique '+n);a=matches[0].split();ck(int(a[0])==len(a)-1,file.name+': prerequisite count '+n)
  for dep in a[1:]:ck(Path(dep).stem.lower()in idx,file.name+': prerequisite exists '+dep)
  rules[n]=[Path(x).stem.lower()for x in a[1:]]
 for row in pack['refits']:ck(rules[row['weapon']]==([]if file.stem=='fulltech'else row['research']),file.name+': refit research gate '+row['weapon'])
for row in pack['ai']:
 text=(O/'AI/AIPs'/row['file']).read_text(encoding='latin1');names=[m[1].lower()for m in re.finditer(r'(?m)^[ \t]*"([^"]+)"[ \t]*,',text)]
 cfg=next(r for r in pack['yards']if r['yard']==row['yard']);ck(row['yard']in names,row['file']+': native yard ordered')
 for i,n in enumerate(cfg['miners']):
  ck(n in names and names.index(row['yard'])<names.index(n),row['file']+': yard precedes '+n)
  if i:ck(cfg['pods'][i-1]in names[:names.index(n)],row['file']+': research precedes '+n)
 # New support rows must also have a real producer and all technology dependencies earlier.
 tech={}
 for line in(O/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if len(a)>=2 and a[0].lower().endswith('.odf'):tech[Path(a[0]).stem.lower()]=[Path(x).stem.lower()for x in a[2:2+max(0,int(a[1]))]]
 for n in row.get('addedSupport',[]):
  earlier=set(names[:names.index(n)]);ck(set(tech[n])<=earlier,row['file']+': support prerequisites '+n)
  producers=[p for p,d in P.items()if any(re.fullmatch(r'(?:secondary)?builditem\d+',k)and v.lower()==n for k,v in d.items())];ck(bool(earlier.intersection(producers)),row['file']+': support producer '+n)
ck(len(pack['ai'])==45,'all 45 faction AI plans updated')
ck(not pack['orbitalRefitsImplemented'],'planet-bound orbital replacement not introduced')
for n in ['forbital','bbase2','borbital','korbital','rorbital','corbital','dorbital','bjorbital','brorbital','xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:
 d=P[n];old=props(n,native)
 for key in set(old)|set(d):
  if key not in ['unitname','tooltip','verbosetooltip']:ck(d.get(key)==old.get(key),n+': orbital gameplay preserved '+key)
files=[]
for path in sorted(O.rglob('*')):
 if not path.is_file():continue
 rel=path.relative_to(O).as_posix();live=root/rel
 files.append({'file':rel,'sourceHash':hashlib.sha256(live.read_bytes()).hexdigest()if live.exists()else None,'stagedHash':hashlib.sha256(path.read_bytes()).hexdigest()})
manifest={'status':'VALIDATED - NOT APPLIED','files':files,'checks':len(checks),'runtimeVerified':False,'yards':len(pack['yards']),'models':len(art),'refitButtons':len(pack['refits']),'AIplans':len(pack['ai'])}
(stage/'manifest.json').write_text(json.dumps(manifest,indent=2));(stage/'validation.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'runtimeVerified':False,'details':checks},indent=2));(repo/'reports/mining-yards-validation.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items()if k!='files'}))
