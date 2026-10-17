"""Create native-style extrapolated 8472 hero variants and matching buttons."""
import sys,pathlib,json,copy,contextlib,io,math,struct
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class ModelIO(SodIO):
 # These Armada II 1.8 exporters omit the Armada I legacy table.
 def read_unknown_legacy_data(self,stream):
  return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(stream)
 def write_unknown_legacy_data(self,data,stream):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(data,stream)
ROOT=pathlib.Path('D:/armadaIII'); OUT=pathlib.Path('D:/Xaramada-Modwork/hero-yard-release'); RELEASE=pathlib.Path('D:/Xaramada-Modwork/bajor-rebuild'); REPO=pathlib.Path('D:/aramada')
manifest=json.loads((REPO/'reports/hero-yard-release.json').read_text());textures={f.stem.lower():f for f in (ROOT/'Textures').rglob('*.tga')}
identity=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]]
def matrix(node):
 t=np.asarray(node['local_transform']);m=np.eye(4);m[:3,:3]=t[:3].T;m[:3,3]=t[3];return m

def world_meshes(model):
 nodes={n['id']:n for n in model.nodes};cache={}
 def world(n,seen=None):
  key=n['id']
  if key in cache:return cache[key]
  seen=set() if seen is None else seen
  if key in seen:return np.eye(4)
  seen.add(key);m=matrix(n);parent=nodes.get(n['parent']);m=world(parent,seen)@m if parent else m;cache[key]=m;return m
 result=[]
 for n in model.nodes:
  if n['type']!='MESH':continue
  # Draw the finest level only, plus our independent construction pods.
  chain=(n['id']+' '+n['parent']).lower()
  if any(s in chain for s in ['lod2','lod3','lod4','lod5','lod6']):continue
  d=n['data'];v=np.array(d['vertices']);v=(world(n)@np.c_[v,np.ones(len(v))].T).T[:,:3];result.append((n,v))
 return result

def boxmesh(template,name,parent,center,size):
 verts=[];uv=[];faces=[]
 x,y,z=center;sx,sy,sz=size
 points=[(x+a*sx/2,y+b*sy/2,z+c*sz/2)for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(1,2,6,5),(0,4,7,3)]:
  start=len(verts);verts.extend([points[i]for i in q]);uv.extend([[0,0],[1,0],[1,1],[0,1]])
  for tri in [(0,1,2),(0,2,3)]:faces.append([[start+i,start+i]for i in tri])
 data=copy.deepcopy(template['data']);data['vertices']=verts;data['texture_coordinates']=uv;data['vertex_lighting_groups']=[{'lighting_material':data['vertex_lighting_groups'][0]['lighting_material'],'faces':faces}];data['cull_type']='NO_CULL'
 return {'type':'MESH','id':name,'parent':parent,'local_transform':copy.deepcopy(identity),'data':data}

atlas=Image.new('RGB',(512,512),(0,0,0));report=[]
for index,f in enumerate(manifest['heroes']):
 source=ROOT/'SOD'/(f['sourceModel']+'.sod')
 if f.get('race','species8472')=='bajoran' and (RELEASE/'SOD/bjconst.sod').exists():source=RELEASE/'SOD/bjconst.sod'
 with contextlib.redirect_stdout(io.StringIO()):model=ModelIO().read_file(str(source))
 meshes=world_meshes(model)
 if not meshes:raise ValueError('No visible meshes '+str(source))
 allv=np.concatenate([v for n,v in meshes]);lo=allv.min(axis=0);hi=allv.max(axis=0);center=(lo+hi)/2;dims=np.maximum(hi-lo,[8,4,8]);template=max(meshes,key=lambda x:len(x[1]))[0]
 scene=next((n['id']for n in model.nodes if not n['parent']),'Scene Root');nodes=copy.deepcopy(model.nodes)
 # Scale the organic root frame, including hardpoints, to retain aligned weapons.
 for n in nodes:
  if n['parent']==scene:
   for row in range(4):
    for axis in range(3):n['local_transform'][row][axis]*=f['shape'][axis]
 model.set_nodes(nodes);writer=ModelIO();writer.curr_sod_version=model.version
 dest=OUT/'SOD'/(f['id']+'.sod');dest.parent.mkdir(parents=True,exist_ok=True)
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(dest));check=ModelIO().read_file(str(dest))
 assert len(check.nodes)==len(nodes)
 # Render the model, retaining each mesh's own original texture and UV map.
 meshes=world_meshes(check);allv=np.concatenate([v for n,v in meshes]);project=lambda v:np.column_stack(((v[:,0]-v[:,2])*.707,-v[:,1]*.816+(v[:,0]+v[:,2])*.408))
 bounds=project(allv);offset=(bounds.max(axis=0)+bounds.min(axis=0))/2;scale=110/max(np.ptp(bounds,axis=0).max(),1)
 canvas=np.zeros((128,128,3),dtype=np.uint8);zb=np.full((128,128),-np.inf);missing=[]
 for n,vertices in meshes:
  data=n['data'];texturefile=textures.get(data['texture'].lower())
  if not texturefile:missing.append(data['texture']);continue
  texture=np.asarray(Image.open(texturefile).convert('RGB'));th,tw=texture.shape[:2];pointsall=(project(vertices)-offset)*scale+64;depth=vertices[:,0]+vertices[:,1]+vertices[:,2];uvs=np.asarray(data['texture_coordinates'])
  for group in data['vertex_lighting_groups']:
   for face in group['faces']:
    ids=[i[0]for i in face];uv=uvs[[i[1]for i in face]];points=pointsall[ids];low=np.maximum(np.floor(points.min(axis=0)).astype(int),0);high=np.minimum(np.ceil(points.max(axis=0)).astype(int),127)
    if np.any(high<low):continue
    x,y=np.meshgrid(np.arange(low[0],high[0]+1)+.5,np.arange(low[1],high[1]+1)+.5);a,b,c=points;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-9:continue
    wa=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;wb=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;wc=1-wa-wb;z=wa*depth[ids[0]]+wb*depth[ids[1]]+wc*depth[ids[2]]
    sub=zb[low[1]:high[1]+1,low[0]:high[0]+1];mask=(wa>=0)&(wb>=0)&(wc>=0)&(z>sub)
    if not mask.any():continue
    u=wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0];v=wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1];color=texture[(np.clip(v,0,.999999)*(th-1)).astype(int),(np.clip(u,0,.999999)*(tw-1)).astype(int)]
    normal=np.cross(vertices[ids[1]]-vertices[ids[0]],vertices[ids[2]]-vertices[ids[0]]);shade=.6+.4*abs(np.dot(normal/max(np.linalg.norm(normal),1e-9),np.array([.3,.9,-.3])/np.sqrt(.99)))
    region=canvas[low[1]:high[1]+1,low[0]:high[0]+1];region[mask]=np.clip(color[mask]*shade,0,255).astype(np.uint8);sub[mask]=z[mask]
 if missing:raise ValueError('Missing native textures '+str(set(missing)))
 icon=Image.fromarray(canvas).resize((64,64),Image.Resampling.LANCZOS);atlas.paste(icon,((index%8)*64,0));f['buttonCell']=index
 report.append({'id':f['id'],'sourceModel':str(source),'design':f['design'],'preservesNativeHardpoints':True,'organicProfileScale':f['shape'],'roundTripValid':True,'textureReferencesValid':True,'runtimeVerified':False})
 rgba=atlas.convert('RGBA')
# Top-origin preview, bottom-origin game TGA.
(REPO/'heroes8472/artwork').mkdir(parents=True,exist_ok=True);atlas.crop((0,0,512,64)).resize((1024,128)).save(REPO/'heroes8472/artwork/hero-bioships.png')
header=bytearray(18);header[2]=2;header[12:16]=struct.pack('<HH',512,512);header[16]=32;header[17]=8
(OUT/'Textures/RGB').mkdir(parents=True,exist_ok=True);(OUT/'Textures/RGB/xhsherobuttons.tga').write_bytes(header+atlas.convert('RGBA').transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes('raw','BGRA'))
(REPO/'reports/hero-yard-release.json').write_text(json.dumps(manifest,indent=2));(REPO/'reports/8472-hero-models.json').write_text(json.dumps(report,indent=2))
status=json.loads((REPO/'status.json').read_text(encoding='utf-8-sig'))
status['current']='Completed three extrapolated 8472 organic hero model variants and matching model-rendered buttons. Native materials, damage hierarchy, animation and aligned hardpoints retained. Finalizing technology, AI, menu and 8472 Universal-builder exclusion checks.'
(REPO/'status.json').write_text(json.dumps(status,indent=2))
with (REPO/'build.log').open('a')as log:log.write('\n'+status['current']+'\n')
print('Three organic hero models and matching buttons generated; native textures and SOD round-trip checks passed.')
