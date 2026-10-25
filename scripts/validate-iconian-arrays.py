from pathlib import Path
import re,json,hashlib,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/iconian-battle-array-stage');overlay=stage/'overlay';report=json.loads((stage/'manifest.json').read_text());checks=[]
index={p.stem.lower():p for p in(root/'odf').rglob('*')if p.suffix.lower()=='.odf'}
index.update({p.stem.lower():p for p in(overlay/'odf').rglob('*.odf')})
def props(path,seen=None):
 seen=set()if seen is None else seen
 if path in seen:return{}
 seen.add(path);t=path.read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):
  n=Path(inc).stem.lower();assert n in index,('missing include',path,inc);d.update(props(index[n],seen))
 for k,v in re.findall(r'(?mi)^\s*([a-z][a-z0-9_]*)\s*=\s*(.*?)\s*(?://.*)?$',t):d[k.lower()]=v.strip().strip('"')
 return d
def check(ok,label):
 assert ok,label
 checks.append(label)
sprite=(overlay/'Sprites/gui_global.spr').read_text(encoding='latin1')
base=props(root/'odf/stations/xbtarray.odf')
numeric=['maxhealth','shieldrate','shieldprotection','shielddelay','maxspecialenergy','specialenergyrate','maximumcrew','maxcrewgain','officercost','officergain','buildtime','shieldgeneratorhitpoints','engineshitpoints','weaponshitpoints','lifesupporthitpoints','sensorshitpoints','rangescan','footprintbuffer']
for row in report['units']:
 unit=row['unit'];d=props(index[unit]);model=overlay/'SOD'/(d['basename']+'.sod')
 with contextlib.redirect_stdout(io.StringIO()):m=Reader().read_file(str(model))
 nodes={n['id'].lower():n for n in m.nodes}
 check(all(d.get(k)==base.get(k)for k in numeric),unit+': baseline combat/system stats retained')
 check(d['race']==row['race'],unit+': valid faction')
 banks={int(k[6:]):v for k,v in d.items()if re.fullmatch('weapon[0-9]+',k)}
 check(sorted(banks)==list(range(1,len(banks)+1)),unit+': contiguous weapon slots')
 check([banks[i]for i in range(1,11)]==['bb3phas']*6+['bb3phot']*4,unit+': six beams and four torpedoes, exact baseline damage')
 check(('xbarraywarp'in banks.values())==(row['race']=='borg'),unit+': transwarp restricted to Borg')
 check(('xbarrayhold'in banks.values())==(row['race']=='borg'),unit+': Borg assimilation restricted to original')
 for i,w in banks.items():
  check(w in index,unit+': weapon '+str(i)+' resolves')
  for hp in re.findall(r'[A-Za-z0-9_]+',d['weaponhardpoints'+str(i)]):check(hp.lower()in nodes,unit+': weapon hardpoint '+hp)
  wd=props(index[w])
  if 'ordname'in wd:check(Path(wd['ordname']).stem.lower()in index,w+': ordnance resolves')
  if wd.get('special')=='1':check(bool(re.search(r'(?mi)^b_'+re.escape(w)+r'\s',sprite)),w+': special button exists')
 for k in ['buildhardpoint','dockinghardpoint']:check(d[k].lower()in nodes,unit+': '+k+' exists')
 check(all(n in index for n in row['production']),unit+': all production targets resolve')
 check(bool(re.search(r'(?mi)^b_'+unit+r'\s',sprite)),unit+': construction button exists')
 for n in [unit,d['basename']]:
  for i in range(1,6):check(bool(re.search(r'(?mi)^'+n+'w'+str(i)+r'\s',sprite)),n+': full-image portrait '+str(i))
 for n in m.nodes:
  if n['type']=='MESH':
   data=n['data'];check((overlay/'Textures/RGB'/(data['texture']+'.tga')).is_file(),unit+': mesh texture resolves')
   for g in data['vertex_lighting_groups']:
    check(all(len(f)==3 and all(0<=v<len(data['vertices'])and 0<=u<len(data['texture_coordinates'])for v,u in f)for f in g['faces']),unit+': face and UV indices valid')
 if row['race']=='species8472':check(d['crewcost']=='0'and d['dilithiumcost']=='0'and d['metalcost']=='0'and d['biomattercost']=='26000',unit+': native biomatter economy')
 else:check(d['dilithiumcost']==base['dilithiumcost']and d['metalcost']==base['metalcost']and d['crewcost']==base['crewcost'],unit+': baseline resource/crew cost')
for menu in report['menus']:
 d=props(index[menu['constructor']]);items={int(k[9:]):v for k,v in d.items()if re.fullmatch('builditem[0-9]+',k)}
 check(len(items)<=14 and sorted(items)==list(range(len(items))),menu['constructor']+': menu capacity and order valid')
 check(all(v in index for v in items.values()),menu['constructor']+': menu targets resolve')
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 t=(overlay/'techtree'/(tree+'.tt')).read_text(encoding='latin1')
 for n in [r['unit']for r in report['units']]+list(report['abilityResearch']):
  lines=re.findall(r'(?mi)^'+re.escape(n)+r'\.odf\s+([^\r\n/]+)',t)
  check(len(lines)==1,tree+': unique tech rule '+n)
  rule=lines[0].split();count=int(rule[0]);check(count<0 or len(rule[1:])==count,tree+': prerequisite count '+n)
  for dep in rule[1:]:check(Path(dep).stem.lower()in index,tree+': prerequisite resolves '+dep)
 for a,pod in report['abilityResearch'].items():
  rule=re.search(r'(?mi)^'+a+r'\.odf\s+([^\r\n/]+)',t)[1].split()
  expected=['0']if tree=='fulltech'or not pod else['-1']if tree=='nospweap'else['1',pod+'.odf']
  check(rule==expected,tree+': intended ability research gate '+a)
for rel,sha in report['files'].items():check(hashlib.sha256((overlay/rel).read_bytes()).hexdigest()==sha,'staged integrity '+rel)
for rel,sha in report['sourceHashes'].items():check(hashlib.sha256((root/rel).read_bytes()).hexdigest()==sha,'live baseline unchanged '+rel)
check(not any('start'in rel.lower()and rel.lower().endswith('.odf')for rel in report['files']),'starting fleets untouched')
result={'status':'PASS','checks':len(checks),'models':len(report['units']),'newArrays':9,'borgRedesigned':True,'runtimeVerified':False,'details':checks}
(stage/'validation.json').write_text(json.dumps(result,indent=2));Path('D:/aramada/reports/iconian-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='details'}))
