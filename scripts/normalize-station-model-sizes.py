from pathlib import Path
import re,json,datetime,sys,contextlib,io,math
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class R(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('equal-station-sizes-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending=[];records=[]
heavy=['fhwp','khwp','rhwp','chwp','dturret3','bjhwp','bhwp']
bases=['bbase','bjbase','brbase','cbase','cstation','dbase','domabase','dombase','ds9','fbase','fbase2','fbaseHQ','fds9','foutpost','kbase','kbase2','kimpbase','kmarbase','koutpost','rbase','rbase2','8472_mother','8472_mothership']
cache={}
def span(f):
 if str(f)in cache:return cache[str(f)]
 with contextlib.redirect_stdout(io.StringIO()):model=R().read_file(str(f))
 nodes={n['id'].lower():n for n in model.nodes};mins=[math.inf]*3;maxs=[-math.inf]*3;count=0
 for node in model.nodes:
  if node['type']!='MESH':continue
  chain=[];n=node;seen=set()
  while n:
   key=n['id'].lower();assert key not in seen,('node cycle',f,key);seen.add(key);chain.append(n['local_transform']);n=nodes.get(n.get('parent','').lower())
  for vertex in node['data']['vertices']:
   v=list(vertex)
   for tr in chain:v=[sum(v[i]*tr[i][j]for i in range(3))+tr[3][j]for j in range(3)]
   for j in range(3):mins[j]=min(mins[j],v[j]);maxs[j]=max(maxs[j],v[j])
   count+=1
 assert count
 dimensions=[maxs[j]-mins[j]for j in range(3)];result={'dimensions':dimensions,'span':max(dimensions)};assert result['span']>0;cache[str(f)]=result;return result
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={f.stem.lower():f for f in(root/'odf').rglob('*.odf')};sods={f.stem.lower():f for f in(root/'SOD').iterdir()if f.suffix.lower()=='.sod'}
 def props(name,seen=None):
  seen=set()if seen is None else seen
  if name in seen:return {}
  seen.add(name);t=idx[name].read_text(encoding='latin1');v={}
  for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):v.update(props(Path(inc).stem.lower(),seen))
  for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
  return v
 fv=props('fhwp');fmodel=fv.get('basename','fhwp').lower();targetHeavy=span(sods[fmodel])['span']*float(fv.get('scalesod','1').rstrip('fF'))
 targetBase=span(sods['xvstock_bbase'])['span'] # Preserved vanilla Borg Nexus geometry, native scale 1.
 for category,names,target in [('heavy',heavy,targetHeavy),('starbase',bases,targetBase)]:
  for name in names:
   n=name.lower();f=idx[n];v=props(n);model=v.get('basename',f.stem).lower();size=span(sods[model]);old=float(v.get('scalesod','1').rstrip('fF'));new=target/size['span'];assert math.isfinite(new)and 0<new<100
   t=f.read_text(encoding='latin1');t=re.sub(r'(?mi)^[ \t]*ScaleSOD[ \t]*=[^\r\n]*','',t)+'\n// Equal visual span: '+('Federation Cyclone'if category=='heavy'else'vanilla Borg Nexus')+' reference.\nScaleSOD = '+format(new,'.9g')+'\n'
   pending.append((root,f.relative_to(root),t));records.append({'root':str(root),'category':category,'unit':f.name,'model':model,'oldScale':old,'newScale':new,'unscaledDimensions':size['dimensions'],'targetSpan':target,'resultSpan':size['span']*new})
for root,rel,t in pending:
 f=root/rel;b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
(repo/'reports/equal-station-sizes.json').write_text(json.dumps({'backup':str(backup),'measurement':'Longest world-space mesh bounding-box dimension, including node hierarchy transforms; shape proportions preserved','heavyReference':'fhwp current visible span','starbaseReference':'xvstock_bbase preserved vanilla Borg Nexus geometry at scale1','units':records,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Station sizes normalized in armadaIII and ArmadaLab: all 7 heavy platforms match Federation Cyclone measured visible span; 23 starbase/command-base variants including Species8472 Mothers match preserved vanilla Borg Nexus span. Per-model scales calculated from transformed geometry, preserving proportions. Stats/menus/weapons unchanged. Backed up; visual gameplay confirmation pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'files':len(pending),'backup':str(backup),'live':[{'unit':x['unit'],'scale':round(x['newScale'],5),'span':round(x['targetSpan'],3)}for x in records if x['root'].lower().endswith('armadaiii')]}))
