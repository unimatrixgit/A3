"""Fix native SOD diffuse-layer flags; prepare only while the user tests."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import copy
stage=Path('D:/Xaramada-Modwork/iconian-model-compatibility-stage');overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True)
pack=json.loads((repo/'reports/iconian-applied.json').read_text());atlas=Image.open(root/'Textures/RGB/ia26mat.tga').convert('RGB');records=[];sourcehashes={}
for r in pack['units']:
 model=r['model'];src=root/'SOD'/(model+'.sod');m=load(src);sourcehashes[src.relative_to(root).as_posix()]=hashlib.sha256(src.read_bytes()).hexdigest();added=[]
 for n in m.nodes:
  if n['type']!='MESH':continue
  d=n['data'];uv=np.array(d['texture_coordinates']);cellx=int(np.floor(uv[:,0].min()*4));celly=int(np.floor(uv[:,1].min()*4));cell=celly*4+cellx;tex='ia26tile'+str(cell).zfill(2)
  dest=overlay/'Textures/RGB'/(tex+'.tga');dest.parent.mkdir(parents=True,exist_ok=True);atlas.crop((cellx*256,celly*256,(cellx+1)*256,(celly+1)*256)).convert('RGB').save(dest)
  d['texture']=tex;d['borgification']={'texture':tex};d['bump_map']=1;d['texture_coordinates']=((uv-np.array([cellx,celly])*.25)*4).tolist()
  # Limit each draw mesh to 450 vertices, keeping all original triangles and UVs.
  faces=[(g['lighting_material'],f)for g in d['vertex_lighting_groups']for f in g['faces']]
  for start in range(0,len(faces),150):
   node=copy.deepcopy(n);node['id']=n['id']+'_'+str(start//150);part=node['data'];part['vertices']=[];part['texture_coordinates']=[];groups={}
   for material,face in faces[start:start+150]:
    ff=[]
    for vi,ui in face:j=len(part['vertices']);part['vertices'].append(d['vertices'][vi]);part['texture_coordinates'].append(d['texture_coordinates'][ui]);ff.append([j,j])
    groups.setdefault(material,[]).append(ff)
   part['vertex_lighting_groups']=[{'lighting_material':k,'faces':v}for k,v in groups.items()];added.append(node)
  n['type']='NULL_OR_HARDPOINT';n['data']=None
 m.nodes.extend(added);out=overlay/'SOD'/src.name;out.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(out))
 check=load(out);meshes=[n for n in check.nodes if n['type']=='MESH'];assert all(n['data']['bump_map']==1 and len(n['data']['vertices'])<=450 for n in meshes)
 assert sum(len(g['faces'])for n in meshes for g in n['data']['vertex_lighting_groups'])==r['triangles']
 assert {n['id']for n in load(src).nodes}.issubset({n['id']for n in check.nodes})
 records.append({'unit':r['unit'],'model':model,'meshCount':len(meshes),'triangles':r['triangles'],'nativeDiffuseLayerFlag':1,'textureSize':256,'hardpointsPreserved':True})
files={p.relative_to(overlay).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in overlay.rglob('*')if p.is_file()}
result={'status':'STAGED - NOT APPLIED','stage':str(stage),'files':files,'sourceHashes':sourcehashes,'models':records,'gameplayFieldsChanged':False,'runtimeVerified':False,'diagnosis':'Native SOD texture-layer field (called bump_map by the reader) was 0; working original uses 1 for diffuse textured meshes.'}
(stage/'manifest.json').write_text(json.dumps(result,indent=2));(repo/'reports/iconian-model-compatibility-staged.json').write_text(json.dumps(result,indent=2));print('STAGED compatibility fix:',len(records),'models;',len(files),'files; gameplay unchanged.')
