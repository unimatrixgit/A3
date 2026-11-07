from pathlib import Path
import sys,ast,contextlib,io,json,re,struct,hashlib,datetime,shutil,subprocess
import numpy as np
from PIL import Image
R=Path('D:/aramada');L=Path('D:/armadaIII');S=R/'patches/klingon-yard-opacity-20261107';O=S/'overlay';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
for n in ast.parse((R/'scripts/stage-armadafiles-yards-20261031.py').read_text()).body:
 if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['IO','load','matrix','world_nodes','bounds']:exec(compile(ast.Module(body=[n],type_ignores=[]),'h','exec'))
class Trace(IO):
 def read_mesh_node(self,s):
  a=s.tell();d=super().read_mesh_node(s);self.spans.append((a,s.tell()));return d
files={};rows=[];mapping={};textures={p.stem.lower():p for p in (L/'Textures/RGB').glob('*.tga')}
def counted(s):b=s.encode();return struct.pack('<H',len(b))+b
for unit in ['kyard','kyard2','kyard3']:
 rel='SOD/ay31_'+unit+'.sod';raw=(L/rel).read_bytes();tr=Trace();tr.spans=[]
 with contextlib.redirect_stdout(io.StringIO()):m=tr.read_file(str(L/rel))
 used={n['data']['texture'] for n in m.nodes if n['type']=='MESH' and not n['id'].lower().startswith('borg')}
 for t in used:
  if t in mapping:continue
  with Image.open(textures[t.lower()]) as im:
   if im.mode!='RGBA' or np.mean(np.asarray(im.getchannel('A'))==0)<.9:continue
   alias='kl07'+hashlib.sha256(t.encode()).hexdigest()[:10];mapping[t]=alias;buf=io.BytesIO();im.convert('RGB').save(buf,format='TGA');files['Textures/RGB/'+alias+'.tga']=buf.getvalue();rows.append({'source':t,'alias':alias,'zeroAlphaFraction':float(np.mean(np.asarray(im.getchannel('A'))==0)),'rgbPreserved':True})
 new=raw
 for a,b in reversed(tr.spans):
  chunk=raw[a:b]
  for t,alias in mapping.items():chunk=chunk.replace(counted(t),counted(alias),1)
  new=new[:a]+chunk+new[b:]
 files[rel]=new;p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(new);check=load(p)
 assert len(m.nodes)==len(check.nodes) and m.materials==check.materials and m._animation_transforms==check._animation_transforms
 for a,b in zip(m.nodes,check.nodes):
  assert a['id']==b['id'] and a['parent']==b['parent'] and a['local_transform']==b['local_transform']
  if a['type']=='MESH':
   for k in a['data']:
    if k!='texture':assert a['data'][k]==b['data'][k],(unit,k)
def size(unit):
 s=(L/'odf/stations'/f'{unit}.odf').read_text();base=re.findall(r'(?im)^baseName\s*=\s*"([^"]+)"',s)[-1];scale=float(re.findall(r'(?im)^ScaleSOD\s*=\s*([\d.]+)',s)[-1]);lo,hi=bounds(load(L/'SOD'/f'{base}.sod'));return s,scale,float(max(hi-lo)*scale)
s,oldscale,oldspan=size('korbital');_,_,targetspan=size('forbital');newscale=oldscale*targetspan/oldspan
s=re.sub(r'(?im)^ScaleSOD\s*=[^\r\n]*','ScaleSOD = '+format(newscale,'.12g'),s);files['odf/stations/korbital.odf']=s.replace('\r\n','\n').replace('\n','\r\n').encode('cp1252')
assert 'armada2.exe' not in subprocess.run(['tasklist','/FI','IMAGENAME eq Armada2.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout.lower()
B=Path('D:/Xaramada-Modwork/backups')/('klingon-yard-opacity-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for rel,data in files.items():
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 for root,tag in [(L,'live'),(R/'bajor/overlay','mirror')]:
  p=root/rel
  if p.exists():b=B/tag/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assert (L/rel).read_bytes()==(R/'bajor/overlay'/rel).read_bytes()
report={'installed':True,'runtimeVerified':False,'backup':str(B),'finding':'Hull texture alpha zero on 98-100% of pixels. Private RGB copies remove unintended transparency without changing source RGB, meshes, material assignments or animations.','textures':rows,'modelGeometryMaterialsAnimations':'Byte-preserved except counted texture bindings; parsed validation passed','controller':'No per-yard preview/ghost/opacity/fade or alternate completed-model override found in yard ODFs. Engine preview/completion render paths not instrumented.','orbitalMiningSize':{'unit':'korbital','reference':'forbital','oldSpan':oldspan,'newSpan':targetspan,'oldScale':oldscale,'newScale':newscale,'gameplayStatsUnchanged':True},'tests':{'assetChecks':'passed','placement':'pending','constructionProgress':'pending','completion':'pending','saveLoad':'pending','rebuilding':'pending'},'files':[{'path':p,'sha256':hashlib.sha256(d).hexdigest()} for p,d in files.items()]}
(S/'manifest.json').write_text(json.dumps(report,indent=2));(R/'reports/klingon-yard-opacity-20261107.json').write_text(json.dumps(report,indent=2))
p=R/'status.json';v=json.loads(p.read_text());v['current']='Installed Klingon yard opacity fix preserving unique models, geometry, animations and stats. Vorcha/Kahless and primary yard use private opaque hull maps. Klingon orbital mining station scaled to Federation orbital envelope. Gameplay placement/completion/save-load/rebuild tests pending.';p.write_text(json.dumps(v,indent=2)+'\n')
with (R/'build.log').open('a') as f:f.write('\n2026-11-07 Installed Klingon hull alpha correction and orbital mining visual scale match. Source RGB, meshes, materials, animation and gameplay stats retained. Runtime verification pending. Backup='+str(B)+'\n')
print('Installed',len(files),'files. Backup',B,'orbital scale',oldscale,'->',newscale)

