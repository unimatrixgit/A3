from pathlib import Path
import sys,contextlib,io,copy,json,re,datetime,shutil
import numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
root=Path('D:/armadaIII');repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('hwp-faction-textures-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
pairs={'fhwp':'xvstock_fbase','bhwp':'xvstock_bbase','khwp':'xvstock_kbase','rhwp':'xvstock_rbase','chwp':'xvstock_cbase','dturret3':'dbase','bjhwp':'fds9','tybrhwp':'brbase','tyfghwp':'xfgmerc','tybghwp':'xfgmerc'}
textures={p.stem.lower()for p in(root/'Textures').rglob('*')if p.is_file()}
def load(p):
 with contextlib.redirect_stdout(io.StringIO()):return IO().read_file(str(p))
def world_vertices(model):
 result={};worlds=[];last={}
 for n in model.nodes:
  t=np.asarray(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];parent=last.get(n['parent'].lower());a=(worlds[parent]if parent is not None else np.eye(4))@a;worlds.append(a);last[n['id'].lower()]=len(worlds)-1
  if n['type']=='MESH':
   v=np.asarray(n['data']['vertices']);result[n['id']]=(a@np.c_[v,np.ones(len(v))].T).T[:,:3]
 return result
for unit,donor in pairs.items():
 odf=root/'odf/stations'/(unit+'.odf');assert odf.exists(),unit
 t=odf.read_text(encoding='latin1');model=re.findall(r'(?mi)^baseName\s*=\s*"([^"]+)"',t)[-1];p=root/'SOD'/(model+'.sod');m=load(p);native=load(root/'SOD'/(donor+'.sod'));nw=world_vertices(native)
 # Use the primary opaque native hull atlas; exclude alternate damage/assimilation effects.
 meshes=[n for n in native.nodes if n['type']=='MESH'and n['data'].get('texture_material')not in ['additive','translucent']and not any(x in n['id'].lower()for x in ['borg','damage','shield'])]
 assert meshes,donor
 reference=max(meshes,key=lambda n:sum(len(g['faces'])for g in n['data']['vertex_lighting_groups']));atlas=reference['data']['texture'];assert atlas.lower()in textures
 points=nw[reference['id']];mid=(points.max(0)+points.min(0))/2;span=max(np.ptp(points,axis=0).max(),1e-8);templates=[]
 for g in reference['data']['vertex_lighting_groups']:
  for face in g['faces']:
   v=points[[vi for vi,ui in face]];normal=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(normal)
   if length<1e-8:continue
   uv=np.asarray([reference['data']['texture_coordinates'][ui]for vi,ui in face]);templates.append(((v.mean(0)-mid)/span,normal/length,uv))
 assert templates
 centers=np.asarray([a for a,b,c in templates]);normals=np.asarray([b for a,b,c in templates]);mw=world_vertices(m);allpoints=np.concatenate(list(mw.values()));center=(allpoints.max(0)+allpoints.min(0))/2;extent=max(np.ptp(allpoints,axis=0).max(),1e-8)
 material=copy.deepcopy(next((mat for mat in native.materials if mat['name'].lower()==str(reference['data']['vertex_lighting_groups'][0]['lighting_material']).lower()),(native.materials[0]if native.materials else m.materials[0])));material['name']='hwp_faction_hull';m.materials[:]=[x for x in m.materials if x['name']!='hwp_faction_hull'];m.materials.append(material)
 before=[(n['id'],copy.deepcopy(n['local_transform']),copy.deepcopy(n['data']['vertices']))for n in m.nodes if n['type']=='MESH'];previous=set()
 for n in m.nodes:
  if n['type']!='MESH':continue
  dat=n['data'];previous.add(dat['texture']);uvs=[]
  for g in dat['vertex_lighting_groups']:
   g['lighting_material']=material['name']
   for face in g['faces']:
    v=mw[n['id']][[vi for vi,ui in face]];normal=np.cross(v[1]-v[0],v[2]-v[0]);normal/=np.linalg.norm(normal)+1e-12;pos=(v.mean(0)-center)/extent
    match=int(np.argmin(np.sum((centers-pos)**2,axis=1)+.65*(1-np.abs(normals@normal))))
    template=templates[match][2]
    for j,pair in enumerate(face):pair[1]=len(uvs);uvs.append(template[j].tolist())
  dat['texture_coordinates']=uvs;dat['texture']=atlas;dat['texture_material']='opaque';dat['borgification']={'texture':atlas}
 b=backup/p.relative_to(root);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);temp=backup/(model+'-checked.sod');writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(temp))
 check=load(temp);after=[n for n in check.nodes if n['type']=='MESH'];assert len(after)==len(before)
 for (name,tr,v),n in zip(before,after):assert n['id']==name and np.allclose(n['local_transform'],tr)and np.allclose(n['data']['vertices'],v)
 assert [(n['id'],n['parent'],n['local_transform'])for n in check.nodes if n['type']!='MESH']==[(n['id'],n['parent'],n['local_transform'])for n in m.nodes if n['type']!='MESH']
 data=temp.read_bytes();p.write_bytes(data);(repo/'bajor/overlay'/p.relative_to(root)).write_bytes(data)
 rows.append({'unit':unit,'model':model,'donor':donor,'oldTextures':sorted(previous),'nativeHullTexture':atlas,'meshCount':len(after)})
(repo/'reports/hwp-faction-textures-20261028.json').write_text(json.dumps({'backup':str(backup),'models':rows,'method':'Reproject original faction station UV face patches onto existing HWP geometry using surface normal and position; original native hull atlas and material reused.','geometryHardpointsOdfPreserved':True,'runtimeVerified':False},indent=2));print(json.dumps(rows))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All 10 HWP variants, including Breen and both Ferengi versions, mapped to original faction station hull textures/materials. Geometry, size, footprint, weapon mounts and ODF stats preserved. SOD round-trip checks passed; visual gameplay check pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
