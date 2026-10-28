from pathlib import Path
import sys,re,json,contextlib,io,collections
import numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class R(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/armadaIII');idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def props(n,seen=()):
 n=Path(n.strip('"')).stem.lower()
 if n not in idx or n in seen:return{}
 t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(inc,seen+(n,)))
 for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]+)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
textures={p.stem.lower()for p in(root/'Textures').rglob('*')if p.is_file()};rows=[]
for name,p in idx.items():
 if p.parent.name.lower()!='stations':continue
 d=props(name);items=[v for k,v in d.items()if re.fullmatch('builditem[0-9]+',k)]
 if not any(props(v).get('classlabel','').lower()in ['pod','researchpod']for v in items):continue
 model=d.get('basename',name);path=root/'SOD'/(model+'.sod')
 if not path.exists():continue
 with contextlib.redirect_stdout(io.StringIO()):m=R().read_file(str(path))
 nodes={n['id'].lower():n for n in m.nodes};world={}
 def transform(n,seen=()):
  key=n['id'].lower()
  if key in seen:return np.eye(4)
  a=np.eye(4);t=np.array(n['local_transform']);a[:3,:3]=t[:3].T;a[:3,3]=t[3];parent=nodes.get(n.get('parent','').lower());return transform(parent,seen+(key,))@a if parent else a
 tris=collections.Counter();modes=collections.Counter();refs=set();mesh=0
 for n in m.nodes:
  if n['type']!='MESH':continue
  # Compare visible hull surfaces only, excluding damage/shield/borg and alternate LOD branches.
  branch=[];cur=n
  while cur and cur['id'].lower()not in branch:branch.append(cur['id'].lower());cur=nodes.get(cur.get('parent','').lower())
  if any(x in ['borg','damage','shield','shields']or re.fullmatch('lod[1-9][0-9]*',x)for x in branch):continue
  mesh+=1;dat=n['data'];modes[str(dat.get('texture_material'))]+=1;refs.add(dat['texture']);v=np.asarray(dat['vertices']);v=(transform(n)@np.c_[v,np.ones(len(v))].T).T[:,:3]
  for g in dat['vertex_lighting_groups']:
   for face in g['faces']:
    key=tuple(sorted(tuple(np.round(v[x[0]],4))for x in face));tris[key]+=1
 rows.append({'unit':name,'name':d.get('unitname'),'model':model,'visibleMeshes':mesh,'textures':sorted(refs),'textureModes':dict(modes),'missingTextures':[x for x in refs if x.lower()not in textures],'coincidentTriangles':sum(v-1 for v in tris.values()if v>1),'triangles':sum(tris.values())})
report={'stations':rows,'runtimeVerified':False};Path('D:/aramada/reports/research-visual-audit-20261028.json').write_text(json.dumps(report,indent=2));print(json.dumps(rows))
