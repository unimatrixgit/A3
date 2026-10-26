"""Validate native class compatibility, references, complete rosters and economy scope."""
from pathlib import Path
import json,re,hashlib,collections,sys
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';d=json.loads((stage/'design.json').read_text());art=json.loads((stage/'artwork.json').read_text());ai=json.loads((stage/'ai.json').read_text());idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};idx['ffreight']=root/'odf/ships/ffreight.odf';idx.update({p.stem.lower():p for p in(O/'odf').rglob('*.odf')});cache={};errors=[];checks=0
def check(ok,label):
 global checks
 checks+=1
 if not ok:errors.append(label)
def props(n,stack=()):
 if n in cache:return cache[n]
 assert n not in stack,('Inheritance cycle',n)
 t=idx[n].read_text(encoding='latin1');out={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):out.update(props(Path(inc).stem.lower(),stack+(n,)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):out[k.lower()]=v.split('//')[0].strip().strip('"')
 cache[n]=out;return out
def items(p,prefix='builditem'):return[(int(k[len(prefix):]),v.lower())for k,v in p.items()if re.fullmatch(prefix+r'\d+',k)]
P={n:props(n)for n in idx};files={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in O.rglob('*')if p.is_file()};baseline=d['baseline']
installed=json.loads((stage/'manifest.json').read_text())['files']if '--installed'in sys.argv else{}
installedSources=json.loads((stage/'manifest.json').read_text()).get('sourceHashes',{})if '--installed'in sys.argv else{}
for n,row in baseline.items():check(hashlib.sha256((root/row['file']).read_bytes()).hexdigest()in [row['hash'],installed.get(row['file']),installedSources.get(row['file'])],'expected live baseline '+n)
check(not any(r.lower().startswith(('bzn/','maps/','missions/','events/'))for r in files),'maps, missions and events untouched')
check(not any('start'in Path(r).stem.lower()and r.endswith('.odf')for r in files),'no starter fleet edits')
check(not any(Path(r).stem.lower()=='brecycle'for r in files),'Borg Recycler untouched')
for n,p in P.items():
 if not idx[n].is_relative_to(O):continue
 menu=items(p);check(len(menu)<=14 and sorted(i for i,v in menu)==list(range(len(menu))),'ordered 14-slot menu '+n)
 for i,v in menu+items(p,'secondarybuilditem'):check(v in P,'build target '+n+' '+v)
 for k,v in p.items():
  if re.fullmatch('weapon[0-9]+',k):check(v.lower()in P,'weapon ODF '+n+' '+v)
 check(p.get('race')!='species8472','8472 ODF untouched '+n)
 if p.get('classlabel')=='research':
  for i,v in menu+items(p,'secondarybuilditem'):check(P[v].get('classlabel')=='pod','native ResearchStation only builds ResearchPod '+n+' '+v)
for ship,yard in d['attackAssignments'].items():
 producers=[n for n,p in P.items()if n not in d['exemptStructures']and any(v==ship for i,v in items(p))];check(producers==[yard],'one attack producer '+ship+' '+str(producers));check(P[ship]==baseline[ship]['properties'],'ship stats unchanged '+ship)
for n,a in d['assets'].items():
 p=P[n]
 if a['kind']in ['yard','service']:
  check(p.get('classlabel')=='shipyard','native standalone Shipyard '+n);check([p.get('weapon'+str(i))for i in [1,2,3]]and 'weapon4'not in p,'three defensive banks '+n)
  if a['kind']=='yard':check(p.get('repairfacility')=='0'and p.get('decommissionfacility')=='0'and float(p.get('recrewrate',0))==0,'production dock service-free '+n)
  else:check(not items(p)and p.get('repairfacility')=='1'and p.get('decommissionfacility')=='1'and float(p.get('recrewrate',0))>0,'service dock repair/recrew/decommission only '+n)
 if a['kind']=='research':
  allowed={'basename','scalesod','unitname','tooltip','verbosetooltip'};before=baseline[n]['properties'];diff={k for k in set(p)|set(before)if p.get(k)!=before.get(k)};check(diff<=allowed,'research function/cost/anchors preserved '+n+' '+str(diff));check(abs(float(p.get('scalesod','1').rstrip('fF;'))-float(before.get('scalesod','1').rstrip('fF;')))<1e-9,'research pod physical scale preserved '+n)
for n in d['miningSizeChanges']:
 p=P[n];before=baseline[n]['properties'];check(abs(float(p['scalesod'])/float(before.get('scalesod','1'))-1.15)<1e-8,'mining size +15% '+n);allowed={'scalesod','footprintbuffer'}|{k for k in set(p)|set(before)if re.fullmatch('builditem[0-9]+',k)};diff={k for k in set(p)|set(before)if p.get(k)!=before.get(k)};check(diff<=allowed,'mining performance and costs preserved '+n+' '+str(diff))
trees={}
for f in(O/'techtree').glob('*.tt'):
 t={}
 for line in f.read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if len(a)<2 or not a[0].lower().endswith('.odf'):continue
  n=Path(a[0]).stem.lower();count=int(a[1]);deps=[Path(x).stem.lower()for x in a[2:]];check(n not in t,'unique technology rule '+f.stem+' '+n);check(count<0 or count==len(deps),'technology prerequisite count '+f.stem+' '+n);t[n]=(count,deps)
 trees[f.stem]=t;relevant=set(d['assets'])|set(d['attackAssignments'])|set(d['constructorTypes'][c][0]for c in d['constructorTypes'])
 def cycles(n,stack=()):
  if n in stack:return[stack+(n,)]
  if n not in t or t[n][0]<0:return[]
  return [x for dep in t[n][1]for x in cycles(dep,stack+(n,))]
 for n in relevant:
  check(n in t,'technology entry '+f.stem+' '+n)
  if n not in t:continue
  for dep in t[n][1]:check(dep in P and dep in t and t[dep][0]>=0,'available prerequisite '+f.stem+' '+n+' '+dep)
  check(not cycles(n),'no tech cycle '+f.stem+' '+n)
 for n in d['retired']:check(t.get(n,(0,[]))[0]<0,'retired duplicate disabled '+f.stem+' '+n)
# Every AI order is replayed against its technology and available producer graph.
producer=collections.defaultdict(set)
for n,p in P.items():
 for i,v in items(p)+items(p,'secondarybuilditem'):producer[v].add(n)
roots={'federation':['fbase','fconst'],'borg':['bbase','bconst'],'klingon':['kbase','kconst'],'romulan':['rbase','rconst'],'cardassian':['cbase','cconst'],'dominion':['dbase','dconst'],'bajoran':['bjbase','bjconst'],'breen':['brbase','brconst']};pat=re.compile(r'(?m)^[ \t]*"([^"]+)"[ \t]*,')
for f in(O/'AI/AIPs').glob('*.aip'):
 available=set(roots[f.name.split('_')[0]]);rows=pat.findall(f.read_text(encoding='latin1'));check(len(rows)<=200,'native AI array capacity '+f.name)
 for n in rows:
  check(n in trees['tech1']and trees['tech1'][n][0]>=0,'AI enabled technology '+f.name+' '+n);check(all(dep in available for dep in trees['tech1'].get(n,(0,[]))[1]),'AI technology order '+f.name+' '+n);check(n in available or bool(producer[n]&available),'AI reachable producer '+f.name+' '+n);available.add(n)
check(len(ai['profiles'])==40 and not ai['failures']and not any(x['skipped']for x in ai['profiles']),'40 complete AI profiles')
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';d=json.loads((stage/'design.json').read_text());sprite=(O/'Sprites/gui_global.spr').read_text(encoding='latin1');keys={m[1].lower():m[2].split()for m in re.finditer(r'(?mi)^(\S+)[ \t]+([^\r\n]+)',sprite)if not m[1].startswith(('@','#','//'))}
for row in art:
 n=row['unit'];p=P[n]
 if row.get('architecture')=='approved vanilla-derived 20261026':
  check(row['bays']==1,'native assembly opening '+n)
  check(row['centralModel']in {x.stem.lower()for x in(root/'SOD').glob('*.sod')},'native architecture source exists '+n)
 if d.get('compactYardRedesign')and row['kind']=='yard'and row.get('architecture')!='approved vanilla-derived 20261026':
  fit=row.get('fit',{});check(bool(fit),'yard ship-size fit recorded '+n)
  if fit:check(fit['bayDesignWidth']+1e-6>=fit['largestShip']['span']*1.25,'conservative bay clearance '+n)
  check(row['bays']==(1 if row['theme']=='b'else 2),'single Borg bay / twin conventional bays '+n)
 try:model=load(O/'SOD'/(row['model']+'.sod'))
 except Exception:
  with contextlib.redirect_stdout(io.StringIO()):model=SodIO().read_file(str(O/'SOD'/(row['model']+'.sod')))
 nodes={node['id'].lower()for node in model.nodes}
 if row['kind']=='research'and row.get('podFittings'):
  declared=re.findall('[A-Za-z0-9_]+',p.get('podhardpoints',''))
  check(set(declared)==set(row['podFittings']),'physical fitting for every research pod '+n)
  check(max(len(items(p)),len(items(p,'secondarybuilditem')))<=len(declared),'pod capacity covers each research tier '+n)
  podWorld=[];podLast={};actualPods={}
  for node in model.nodes:
   tr=np.asarray(node['local_transform']);local=np.eye(4);local[:3,:3]=tr[:3].T;local[:3,3]=tr[3];parentIndex=podLast.get(node['parent'].lower());world=(podWorld[parentIndex]if parentIndex is not None else np.eye(4))@local;podWorld.append(world);podLast[node['id'].lower()]=len(podWorld)-1
   if node['id'].lower()in row['podFittings']:actualPods[node['id'].lower()]=world[:3,3]
  for hp,pos in row['podFittings'].items():check(hp in actualPods and np.allclose(actualPods[hp],pos,atol=.0001),'pod attachment position preserved '+n+' '+hp)
 if row['theme']=='b':check(row['centralModel'].startswith('xvstock_b')if row['kind']=='research'or row.get('architecture')=='approved vanilla-derived 20261026'else row['centralModel']=='xvstock_bbase','original Armada II Borg architecture reference '+n)
 for node in model.nodes:
  if node['type']!='MESH':continue
  dat=node['data'];v=dat['vertices'];uv=dat['texture_coordinates'];check(np.isfinite(v).all()and np.isfinite(uv).all(),'finite geometry '+n);check(len(v)<=450,'native conservative mesh chunks '+n);check(dat['texture'].lower()in texidx,'native diffuse texture '+n+' '+dat['texture'])
  if model.version>1.9101:check(dat['bump_map']==1,'diffuse layer flag '+n)
  for group in dat['vertex_lighting_groups']:check(all(len(f)==3 and all(0<=vi<len(v)and 0<=ui<len(uv)for vi,ui in f)for f in group['faces']),'valid native face indices '+n)
 for k,value in p.items():
  if re.fullmatch('weaponhardpoints[0-9]+',k)or k in ['podhardpoints','buildhardpoint','repairhardpoint']:
   for hp in re.findall('[A-Za-z0-9_]+',value):check(hp.lower()in nodes,'hardpoint exists '+n+' '+hp)
 for key in ['b_'+n,'b_'+row['model']]+[s+'w'+str(i)for s in[n,row['model']]for i in range(1,6)]:
  check(key in keys,'build/queue/status sprite '+key)
  if key in keys:
   tex=O/'Textures/RGB'/(keys[key][0]+'.tga');check(tex.is_file(),'icon texture '+key)
   if tex.is_file():im=Image.open(tex);check(im.mode=='RGB'and im.size==(64,64),'native full RGB portrait '+key)
manifest={'files':files,'sourceHashes':{rel:hashlib.sha256((root/rel).read_bytes()).hexdigest()for rel in files if(root/rel).is_file()},'models':len(art),'yards':sum(len(x)for x in d['yards'].values()),'serviceDocks':10,'runtimeVerified':False};(stage/'manifest.json').write_text(json.dumps(manifest,indent=2));result={'status':'FAIL'if errors else'PASS','checks':checks,'models':len(art),'files':len(files),'errors':errors,'runtimeVerified':False};(stage/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if errors:sys.exit(1)

