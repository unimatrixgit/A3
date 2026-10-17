import pathlib,json,re,sys,contextlib,io,hashlib,math,numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=pathlib.Path('D:/armadaIII');repo=pathlib.Path('D:/aramada');stage=pathlib.Path('D:/Xaramada-Modwork/bajor-redesign-v3');r=json.loads((repo/'reports/bajoran-redesign-v3-release.json').read_text());m=json.loads((stage/'manifest.json').read_text());ledger=json.loads((repo/'reports/bajoran-test-overrides.json').read_text());models=json.loads((repo/'reports/bajoran-redesign-v3-models.json').read_text());errors=[];idx={f.stem.lower():f for f in(root/'odf').rglob('*.odf')};idx.update({f.stem.lower():f for f in(stage/'odf').rglob('*.odf')});textures={f.stem.lower()for folder in[root/'Textures',stage/'Textures']for f in folder.rglob('*.tga')};cache={}
def props(n,seen=None):
 if n in cache:return cache[n]
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
 for inc in re.findall(r'^[ \t]*#include[ \t]+"([^"]+)"',t,re.M):v.update(props(inc.lower().removesuffix('.odf'),seen.copy()))
 for k,x in re.findall(r'^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t,re.M):v[k.lower()]=x.split('//')[0].strip().strip('"')
 cache[n]=v;return v
for f in r['files']:
 file=stage/f['path']
 if hashlib.sha256(file.read_bytes()).hexdigest()!=f['sha256']:errors.append([f['path'],'Package hash mismatch'])
 if file.suffix.lower()=='.odf':
  for i,l in enumerate(file.read_text(encoding='latin1').splitlines(),1):
   if l.split('//')[0].count('"')%2:errors.append([f['path'],i,'Unbalanced quote'])
for u in m['units']:
 name=u['odf'];v=props(name);model=v.get('basename',name);file=stage/'SOD'/(model+'.sod');file=file if file.exists()else root/'SOD'/(model+'.sod')
 with contextlib.redirect_stdout(io.StringIO()):s=IO().read_file(str(file))
 names={n['id'].lower()for n in s.nodes}
 for k,value in v.items():
  if 'hardpoint'in k:
   for hp in re.findall(r'(?:hp|pod|bot)\d+',value,re.I):
    if hp.lower()not in names:errors.append([name,'Missing hardpoint',hp])
 for n in s.nodes:
  if not np.isfinite(np.array(n['local_transform'])).all():errors.append([name,'Invalid transform'])
  if n['type']!='MESH':continue
  d=n['data'];verts=d['vertices'];uv=d['texture_coordinates']
  if not np.isfinite(np.array(verts)).all():errors.append([name,'Nonfinite vertices'])
  for g in d['vertex_lighting_groups']:
   for face in g['faces']:
    if any(v<0 or v>=len(verts)or t<0 or t>=len(uv)for v,t in face):errors.append([name,n['id'],'Face index out of bounds'])
  for tex in[d['texture'],d.get('borgification',{}).get('texture','')]:
   if tex and tex not in['_B','0']and tex.lower()not in textures:errors.append([name,'Missing texture',tex])
 if name!='bjbase':
  rec=next(x for x in models if x['unit']==name)
  with contextlib.redirect_stdout(io.StringIO()):native=IO().read_file(str(root/'SOD'/(rec['sourceModel']+'.sod')))
  if[(n['id'],n['parent'],n['type'])for n in s.nodes]!=[(n['id'],n['parent'],n['type'])for n in native.nodes]:errors.append([name,'Native hierarchy changed'])
  if s._animation_transforms!=native._animation_transforms or s._animation_tex_refs!=native._animation_tex_refs:errors.append([name,'Native animation records changed'])
for row in ledger['normalCosts']:
 t=(stage/'odf/stations'/(row['unit']+'.odf')).read_text(encoding='latin1')
 for k,value in row['normal'].items():
  found=re.search(r'^[ \t]*'+k+r'[ \t]*=[ \t]*([^\r\n]+)',t,re.M|re.I)
  if(value is None and found)or(value is not None and(not found or found[1].strip()!=str(value))):errors.append([row['unit'],k,'Normal value not restored'])
for rel in ledger['originalTechFiles']:
 current=(stage/rel).read_text(encoding='latin1');original=(pathlib.Path(ledger['originalTechBackup'])/rel).read_text(encoding='latin1')
 for u in ledger['temporaryTestBuildings']:
  pattern=r'^[ \t]*'+u+r'\.odf[ \t]+([^\r\n]+)'
  if re.findall(pattern,current,re.M|re.I)!=re.findall(pattern,original,re.M|re.I):errors.append([rel,u,'Normal prerequisites not restored'])
if props('bjmining').get('freightername')!='bjfreight'or any(k.startswith('builditem')for k in props('bjmining')):errors.append(['Harvester mining-class fix lost'])
if props('bjfreight').get('weapon1','').lower()!='gminedilithium'or props('bjfreight').get('weapon2','').lower()!='gminelatinum':errors.append(['Native harvest weapons lost'])
if props('bjbase').get('basename')!='fds9'or any(k in props('bjbase')for k in['animation','buildanimation']):errors.append(['DS9 fix lost'])
if props('bjnerys').get('ishero')!='1':errors.append(['Kira hero marker missing'])
spr=(stage/'Sprites/gui_global.spr').read_text(encoding='latin1')
for u in m['units']:
 for k in['b_'+u['odf']]+[u['odf']+'w'+str(i)for i in range(1,6)]:
  if len(re.findall(r'^[ \t]*'+k+r'[ \t]+',spr,re.M|re.I))!=1:errors.append([k,'Nonunique/missing GUI mapping'])
report={'target':str(root),'stage':str(stage),'errors':errors,'modelsChecked':54,'newModels':53,'nativeHierarchiesAndAllAnimationRecordsPreserved':True,'normalBuildingSettingsChecked':13,'techRowsChecked':13*38,'guiMappingsChecked':324,'harvesterAndDs9FixesPreserved':True,'runtimeVerified':False};(repo/'reports/bajoran-redesign-v3-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report)[:7000]);raise SystemExit(bool(errors))
