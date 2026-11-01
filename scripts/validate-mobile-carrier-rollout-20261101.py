from pathlib import Path
import json,re,hashlib,ast,sys,contextlib,io,wave
import numpy as np
from PIL import Image
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/mobile-carrier-rollout-20261101';out=stage/'overlay'
m=json.loads((stage/'manifest.json').read_text());errors=[]
idx={p.stem.lower():p for p in(root/'odf').rglob('*')if p.suffix.lower()=='.odf'}
idx.update({p.stem.lower():p for p in(out/'odf').rglob('*')if p.suffix.lower()=='.odf'});cache={}
def props(n,seen=None):
 if n in cache:return cache[n]
 seen=set()if seen is None else seen
 assert n not in seen,('include cycle',n);seen.add(n);p=idx[n];t=p.read_text(encoding='latin1');d={}
 for parent in re.findall(r'(?im)^\s*#include\s+"([^"]+)"',t):d.update(props(Path(parent).stem.lower(),seen.copy()))
 for k,v in re.findall(r'(?im)^\s*(\w+)\s*=\s*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 cache[n]=d;return d
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
for n in ast.parse((repo/'scripts/stage-armadafiles-yards-20261031.py').read_text()).body:
 if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in ['IO','load']:exec(compile(ast.Module(body=[n],type_ignores=[]),'h','exec'))
sods={p.stem.lower():p for p in(root/'SOD').glob('*')};sods.update({p.stem.lower():p for p in(out/'SOD').glob('*')})
textures={p.stem.lower():p for p in(root/'Textures').rglob('*')if p.suffix.lower()in['.tga','.bmp']};textures.update({p.stem.lower():p for p in(out/'Textures').rglob('*')if p.suffix.lower()in['.tga','.bmp']})
sprite=(out/'Sprites/gui_global.spr').read_text(encoding='latin1');keys=set(re.findall(r'(?m)^(\w+)[ \t]+\w+',sprite));weapons=(root/'Sprites/weapon.spr')
weaponSprites='\n'.join(p.read_text(encoding='latin1')for p in(root/'Sprites').glob('*.spr'))
sound={p.name.lower():p for p in(root/'sounds').rglob('*')if p.is_file()};sound.update({p.name.lower():p for p in(out/'sounds').rglob('*')if p.is_file()})
checked=[]
for rec in m['files']:
 p=out/rec['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],rec['path']
 if rec['previousSha256']:assert hashlib.sha256((root/rec['path']).read_bytes()).hexdigest()==rec['previousSha256'],('stale live source',rec['path'])
 if p.suffix.lower()!='.odf':continue
 name=p.stem.lower();d=props(name)
 for k,v in d.items():
  if re.fullmatch(r'weapon\d+|builditem\d+|ordname|physicsfile|trekphysicsfile',k):assert Path(v).stem.lower()in idx,(name,k,v)
  if k=='firesound':assert v.lower()in sound,(name,k,v)
 if p.parent.name.lower()=='ships':
  b=d.get('basename',name).lower();assert b in sods,(name,b);model=load(sods[b]);nodes={n['id'].lower()for n in model.nodes}
  for k,v in d.items():
   if re.fullmatch(r'weaponhardpoints\d+|buildhardpoint|repairhardpoint',k):
    for hp in re.findall(r'\w+',v):assert hp.lower()in nodes,(name,k,hp)
  builds=sorted(int(k[9:])for k in d if re.fullmatch(r'builditem\d+',k));assert not builds or builds==list(range(max(builds)+1)),(name,builds);assert len(builds)<=14,(name,builds)
  if name in m['newUnits']:
   for key in ['b_'+name]+[name+'w'+str(i)for i in range(1,6)]:assert key in keys,key
   for n in model.nodes:
    if n['type']=='MESH':
     tex=n['data']['texture']
     if tex:assert tex.lower()in textures,(name,tex)
  checked.append({'unit':name,'model':b,'buildItems':builds})
for p in(out/'Textures').rglob('*'):
 if p.is_file():
  with Image.open(p)as im:im.load()
with wave.open(str(out/'sounds/effects/sg26drone.wav'),'rb')as w:assert w.getnframes()>0
for p in(out/'Techtree').glob('*.tt'):
 for name in m['newUnits']+['sg26wormhole','sg26zpm','sg26cloak','sg26overdrive']:
  rows=re.findall(r'(?im)^'+name+r'\.odf\s+([^\r\n]+)',p.read_text(encoding='latin1'));assert len(rows)==1,(p.name,name)
  parts=rows[0].split('//')[0].split();assert int(parts[0])==len(parts)-1,(p.name,name,parts)
  for dep in parts[1:]:assert Path(dep).stem.lower()in idx,(p.name,name,dep)
  if name in ['sg26wormhole','sg26zpm','sg26cloak','sg26overdrive']:assert parts==['0'],(p.name,name,parts)
assert(out/'Sprites/gui_global.spr').read_bytes().startswith((root/'Sprites/gui_global.spr').read_bytes())
assert props('sg26atlantis')['weapon7']=='sg26wormhole'
assert props('sg26wormhole')['wpnname']=='Wormhole Drive'
assert props('sg26wormhole')['ordname']=='twarpd'
assert 'b_sg26wormhole'in keys
slots=[]
for name in ['sg26wormhole','sg26zpm','sg26cloak','sg26overdrive']:
 d=props(name);slots.append(int(d['buttonslot']));assert 'b_'+name in keys
assert slots==[1,2,3,4]
assert props('sg26overdriveo')['specialvalue']=='15'
assert float(props('sg26overdriveo')['damagemodifier'])*float(props('sg26drone_cityo')['damagebase'])==700
assert props('sg26atlantis')['maxspecialenergy']=='4000'
assert props('sg26atlantis')['specialenergyrate']=='40'
assert all(props(u)['classlabel']=='shipyard'and props(u)['ainame']=='CraftProcess'for u in [x['unit']for x in m['existingShipConversions']]+['sg26atlantis','xr26carrier'])
r={'fileCount':len(m['files']),'shipsAndBuildersChecked':checked,'errors':errors,'runtimeVerified':False,
 'checks':['source/stage hashes','ODF includes and weapons/ordinance','physics','sound file and WAV decoding','texture decoding','native launch/weapon hardpoints','new unit build/group aliases','tech entries and prerequisites','14-entry producer menu limit','GUI original prefix preserved','Wormhole Drive label/icon/ordinance']}
(stage/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'files':len(m['files']),'unitsChecked':len(checked),'errors':errors}))
