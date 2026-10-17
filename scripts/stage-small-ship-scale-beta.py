from pathlib import Path
import re,json,contextlib,io,numpy as np
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
out=Path('D:/Xaramada-Modwork/small-ship-scale-beta');models={p.stem.lower():p for p in(root/'SOD').glob('*')if p.suffix.lower()=='.sod'};sizes={}
def span(model):
 if model in sizes:return sizes[model]
 with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(models[model]))
 nodes={n['id']:n for n in m.nodes};memo={}
 def world(n):
  if n['id']in memo:return memo[n['id']]
  t=np.asarray(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];par=nodes.get(n['parent']);a=world(par)@a if par else a;memo[n['id']]=a;return a
 verts=[]
 for n in m.nodes:
  if n['type']!='MESH':continue
  par=n;chain=[]
  while par:chain.append(par['id'].lower());par=nodes.get(par['parent'])
  if any(x in chain for x in ['borg','damage','shield','lod2','lod3','lod4','lod5','lod6']):continue
  v=np.asarray(n['data']['vertices']);verts.append((world(n)@np.c_[v,np.ones(len(v))].T).T[:,:3])
 if not verts:raise ValueError('No visible mesh')
 sizes[model]=float(np.ptp(np.concatenate(verts),axis=0).max());return sizes[model]
def modelname(n,p):return p.get('basename',n).lower().removesuffix('.sod')
def lineage(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen or n not in idx:return seen
 seen.add(n)
 for inc in re.findall(r'#include\s+"([^"]+)"',idx[n].read_text(encoding='latin1'),re.I):lineage(inc.lower(),seen)
 return seen
import sys,subprocess
if len(sys.argv)>2 and sys.argv[1]=='--measure':
 print(span(sys.argv[2]));raise SystemExit
rawspan=span
def span(model):
 if model not in sizes:
  result=subprocess.run([sys.executable,__file__,'--measure',model],capture_output=True,text=True,timeout=3)
  if result.returncode:raise ValueError('Model could not be measured safely')
  sizes[model]=float(result.stdout.strip())
 return sizes[model]
p=props('fdestroy');baseline=span(modelname('fdestroy',p))*float(p.get('scalesod','1'))*1.35;changes=[];skipped=[]
for path in(root/'odf/ships').glob('*.odf'):
 n=path.stem.lower();anc=lineage(path.name.lower());p=props(n)
 if not any(x in anc for x in ['destroy.odf','scoutbase.odf','scout.odf','colony.odf','freight.odf','repair.odf','const.odf','cargo.odf','construction.odf']):continue
 if any(x in anc for x in ['frigate.odf','battle.odf','cruise.odf','cruise1.odf','cruise2.odf','assault.odf','special.odf']):continue
 try:
  model=modelname(n,p);scale=float(p.get('scalesod','1'));old=span(model)*scale
  if old>=baseline*.995:continue
  assert np.isfinite(old) and old>0,'Invalid model dimensions'
  new=round(scale*baseline/old,6);t=path.read_text(encoding='latin1');t=re.sub(r'^\s*ScaleSOD\s*=.*$',f'ScaleSOD = {new}',t,flags=re.M|re.I)if re.search(r'^\s*ScaleSOD\s*=',t,re.M|re.I)else t+f'\nScaleSOD = {new}\n';dst=out/path.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(t,encoding='latin1');changes.append(dict(unit=n,oldScale=scale,newScale=new,oldSpan=old,newSpan=baseline,file=str(path.relative_to(root))))
 except Exception as e:skipped.append(dict(unit=n,reason=str(e)))
(repo/'reports/small-ship-scale-beta.json').write_text(json.dumps(dict(stage=str(out),baseline='fdestroy Defiant Class',baselineSpan=baseline,changes=changes,skipped=skipped,files=[x['file']for x in changes],installed=False,gameplayVerified=False),indent=2));print(json.dumps(dict(baseline=baseline,changes=len(changes),skipped=skipped)))



