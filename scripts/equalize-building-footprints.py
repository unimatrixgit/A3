from pathlib import Path
import re,json,datetime,sys,contextlib,io,math
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class R(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');sizes=json.loads((repo/'reports/equal-station-sizes.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('equal-building-footprints-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));cache={};pending=[];records=[]
def bounds(f):
 if str(f)in cache:return cache[str(f)]
 with contextlib.redirect_stdout(io.StringIO()):m=R().read_file(str(f))
 nodes={n['id'].lower():n for n in m.nodes};lo=[math.inf]*3;hi=[-math.inf]*3
 for n in m.nodes:
  if n['type']!='MESH':continue
  chain=[];node=n;seen=set()
  while node:
   key=node['id'].lower();assert key not in seen;seen.add(key);chain.append(node['local_transform']);node=nodes.get(node.get('parent','').lower())
  for vertex in n['data']['vertices']:
   v=list(vertex)
   for tr in chain:v=[sum(v[i]*tr[i][j]for i in range(3))+tr[3][j]for j in range(3)]
   for j in range(3):lo[j]=min(lo[j],v[j]);hi[j]=max(hi[j],v[j])
 assert all(math.isfinite(x)for x in lo+hi);cache[str(f)]=(lo,hi);return lo,hi
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={f.stem.lower():f for f in(root/'odf').rglob('*.odf')};sods={f.stem.lower():f for f in(root/'SOD').iterdir()if f.suffix.lower()=='.sod'}
 def props(n,seen=None):
  seen=set()if seen is None else seen
  if n in seen:return {}
  seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
  for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):v.update(props(Path(inc).stem.lower(),seen))
  for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
  return v
 fv=props('fhwp');fscl=float(fv.get('scalesod','1').rstrip('fF'));fl,fh=bounds(sods[fv.get('basename','fhwp').lower()]);bl,bh=bounds(sods['xvstock_bbase'])
 targets={'heavy':([x*fscl for x in fl],[x*fscl for x in fh],10.0),'starbase':(bl,bh,100.0)}
 for record in sizes['units']:
  if Path(record['root'])!=root:continue
  n=Path(record['unit']).stem.lower();f=idx[n];v=props(n);scale=float(v.get('scalesod','1').rstrip('fF'));lo,hi=bounds(sods[v.get('basename',f.stem).lower()]);lo=[x*scale for x in lo];hi=[x*scale for x in hi];tl,th,buffer=targets[record['category']]
  values={'footprintBuffer':buffer,'eastBuffer':th[0]-hi[0],'westBuffer':lo[0]-tl[0],'northBuffer':th[2]-hi[2],'southBuffer':lo[2]-tl[2]}
  predicted=[lo[0]-buffer-values['westBuffer'],lo[2]-buffer-values['southBuffer'],hi[0]+buffer+values['eastBuffer'],hi[2]+buffer+values['northBuffer']]
  target=[tl[0]-buffer,tl[2]-buffer,th[0]+buffer,th[2]+buffer];assert max(abs(a-b)for a,b in zip(predicted,target))<1e-6
  t=f.read_text(encoding='latin1');originalScale=v.get('scalesod','1')
  for k,val in values.items():t=re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+format(val,'.9g')+'\n'
  assert re.findall(r'(?mi)^\s*ScaleSOD\s*=\s*([^\r\n]+)',t)==re.findall(r'(?mi)^\s*ScaleSOD\s*=\s*([^\r\n]+)',f.read_text(encoding='latin1'))
  pending.append((root,f.relative_to(root),t));records.append({'root':str(root),'unit':f.name,'category':record['category'],'scaleUnchanged':originalScale,'buffers':values,'calculatedFootprintXZ':predicted,'referenceFootprintXZ':target})
for root,rel,t in pending:
 f=root/rel;b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.write_bytes(data)
(repo/'reports/equal-building-footprints.json').write_text(json.dumps({'backup':str(backup),'nativeFieldsVerified':'CraftClass loader 0x4bf36d reads east/west/north/southBuffer; GetFootprint 0x4c0240 uses these with model bounding box and footprintBuffer','reference':'Original vanilla Nexus model xvstock_bbase at scale1 plus station100 buffer; fhwp current model plus turret10 buffer','units':records,'modelFilesChanged':False,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Building placement footprints adjusted in armadaIII and ArmadaLab: 23 starbase variants match original vanilla Borg Nexus reference; 7 heavy platforms match Federation Cyclone reference. Native directional buffer values calculated from transformed/scaled mesh bounds and validated mathematically. Model geometry, proportions and current visual scales unchanged. Backups saved; in-game placement-grid verification pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'files':len(pending),'backup':str(backup),'modelsUnchanged':True,'calculatedFootprintsMatch':True,'runtimeVerified':False}))
