from pathlib import Path
import sys,json,contextlib,io,math,re,datetime,shutil
import numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
root=Path('D:/armadaIII');repo=Path('D:/aramada');art=json.loads((repo/'patches/twin-yards-20261025/artwork.json').read_text());audit=json.loads((repo/'reports/research-visual-audit-20261028.json').read_text());active={x['unit']:x['model']for x in audit['stations']};backup=Path('D:/Xaramada-Modwork/backups')/('research-remove-old-core-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[];pending=[]
def load(p):
 with contextlib.redirect_stdout(io.StringIO()):return IO().read_file(str(p))
for row in art:
 if row['kind']!='research'or active.get(row['unit'])!=row['model']:continue
 p=root/'SOD'/(row['model']+'.sod');source=root/'SOD'/(row['centralModel']+'.sod');m=load(p);original=load(source);last={};parts=[]
 for node in original.nodes:
  chain=last.get(node['parent'].lower(),[])+[node['id'].lower()];last[node['id'].lower()]=chain
  if node['type']=='MESH'and not any(x in ['borg','damage','shield','shields']for x in chain):parts.append((node['data'],chain))
 lods={x for dat,c in parts for x in c if re.fullmatch('lod[0-9]+',x)}
 if lods:
  best=min(lods,key=lambda x:int(x[3:]));parts=[(dat,c)for dat,c in parts if best in c or not any(x in lods for x in c)]
 expected=[]
 for dat,c in parts:
  for g in dat['vertex_lighting_groups']:
   for start in range(0,len(g['faces']),150):expected.append(np.asarray([dat['texture_coordinates'][ui]for face in g['faces'][start:start+150]for vi,ui in face]))
 meshes=[n for n in m.nodes if n['type']=='MESH'];core=meshes[:len(expected)]
 if not expected or len(meshes)<=len(expected)or any(np.asarray(n['data']['texture_coordinates']).shape!=uv.shape or not np.allclose(n['data']['texture_coordinates'],uv,atol=1e-6)for n,uv in zip(core,expected)):
  rows.append({'unit':row['unit'],'status':'SKIPPED: source core could not be verified'});continue
 ids={id(n)for n in core};m.nodes[:]=[n for n in m.nodes if id(n)not in ids]
 pending.append((p,m,len(core)));rows.append({'unit':row['unit'],'model':row['model'],'removedOldCoreMeshes':len(core),'retainedNewHullMeshes':len(meshes)-len(core),'status':'verified by original core UV chunks'})
for p,m,count in pending:
 b=backup/p.relative_to(root);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);temp=backup/(p.stem+'-checked.sod');writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(temp))
 test=load(temp);assert len(test.nodes)==len(m.nodes)
 assert [(n['id'],n['parent'])for n in test.nodes if n['type']!='MESH']==[(n['id'],n['parent'])for n in m.nodes if n['type']!='MESH']
 data=temp.read_bytes();p.write_bytes(data);out=repo/'bajor/overlay'/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
(repo/'reports/research-old-core-removal-20261028.json').write_text(json.dumps({'backup':str(backup),'stations':rows,'appliedModels':len(pending),'runtimeVerified':False,'preserved':'New hulls, hardpoints, research attachment nodes, ODFs, stats and research definitions'},indent=2));print(json.dumps({'appliedModels':len(pending),'stations':rows}))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']=f'Research visual overlap corrected on {len(pending)} redesigned models: verified embedded stock cores removed, new hulls and attachment hardpoints retained. All 30 research-capable stations audited for missing textures and overlap. File checks passed; gameplay pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')

