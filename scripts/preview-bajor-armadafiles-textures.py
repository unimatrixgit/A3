import pathlib,json,sys,contextlib,io,math
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
ROOT=pathlib.Path('D:/armadaIII');OUT=pathlib.Path('D:/Xaramada-Modwork/bajor-armadafiles-textures');REPO=pathlib.Path('D:/aramada');m=json.loads(pathlib.Path('D:/Xaramada-Modwork/bajor-redesign-v3/manifest.json').read_text());textures={f.stem.lower():f for f in (ROOT/'Textures').rglob('*.tga')};textures.update({f.stem.lower():f for f in (OUT/'Textures').rglob('*.tga')});images={};atlas=Image.new('RGB',(512,512));sheet=Image.new('RGB',(1024,1024),(13,17,22));draw=ImageDraw.Draw(sheet);reports=[]
for index,u in enumerate(m['units']):
 name=u['odf'];file=ROOT/'SOD'/('br3_'+name+'.sod')if name!='bjbase'else ROOT/'SOD/fds9.sod'
 with contextlib.redirect_stdout(io.StringIO()):model=IO().read_file(str(file))
 nodes={n['id']:n for n in model.nodes};memo={}
 def chain(n):
  seen=set();out=[]
  while n and n['id']not in seen:seen.add(n['id']);out.append(n['id']);n=nodes.get(n['parent'])
  return out
 def world(n,seen=None):
  if n['id']in memo:return memo[n['id']]
  seen=set()if seen is None else seen
  if n['id']in seen:return np.eye(4)
  seen.add(n['id']);t=np.asarray(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];par=nodes.get(n['parent']);a=world(par,seen)@a if par else a;memo[n['id']]=a;return a
 visible=[n for n in model.nodes if n['type']=='MESH'and not any(x.lower()in['borg','damage','shield']for x in chain(n))];lod0=any(any(x.lower()=='lod0'for x in chain(n))for n in visible);visible=[n for n in visible if not any(x.lower()in(['lod1','lod2','lod3','lod4','lod5','lod6']if lod0 else['lod2','lod3','lod4','lod5','lod6'])for x in chain(n))];meshes=[(n,(world(n)@np.c_[n['data']['vertices'],np.ones(len(n['data']['vertices']))].T).T[:,:3])for n in visible];allv=np.concatenate([v for n,v in meshes]);project=lambda v:np.column_stack(((v[:,0]-v[:,2])*.707,-v[:,1]*.816+(v[:,0]+v[:,2])*.408));bounds=project(allv);offset=(bounds.max(axis=0)+bounds.min(axis=0))/2;scale=108/max(np.ptp(bounds,axis=0).max(),1);canvas=np.zeros((128,128,3),dtype=np.uint8);zb=np.full((128,128),-np.inf)
 for n,vtx in meshes:
  d=n['data'];key=d['texture'].lower()
  if key not in images:images[key]=np.asarray(Image.open(textures[key]).convert('RGB'))if key in textures else np.full((4,4,3),170,dtype=np.uint8)
  texture=images[key];th,tw=texture.shape[:2];xy=(project(vtx)-offset)*scale+64;depth=vtx[:,0]+vtx[:,1]+vtx[:,2];uvs=np.asarray(d['texture_coordinates'])
  for g in d['vertex_lighting_groups']:
   for face in g['faces']:
    ids=[q[0]for q in face];uv=uvs[[q[1]for q in face]];points=xy[ids];lo=np.maximum(np.floor(points.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(points.max(axis=0)).astype(int),127)
    if np.any(hi<lo):continue
    x,y=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5);a,b,c=points;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-9:continue
    wa=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;wb=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;wc=1-wa-wb;z=wa*depth[ids[0]]+wb*depth[ids[1]]+wc*depth[ids[2]];sub=zb[lo[1]:hi[1]+1,lo[0]:hi[0]+1];mask=(wa>=0)&(wb>=0)&(wc>=0)&(z>sub)
    if not mask.any():continue
    u=wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0];v=wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1];color=texture[(np.clip(v,0,.999999)*(th-1)).astype(int),(np.clip(u,0,.999999)*(tw-1)).astype(int)];norm=np.cross(vtx[ids[1]]-vtx[ids[0]],vtx[ids[2]]-vtx[ids[0]]);shade=.6+.4*abs(np.dot(norm/max(np.linalg.norm(norm),1e-9),np.array([.3,.9,-.3])/np.sqrt(.99)));region=canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1];region[mask]=np.clip(color[mask]*shade,0,255).astype(np.uint8);sub[mask]=z[mask]
 image=Image.fromarray(canvas);atlas.paste(image.resize((64,64),Image.Resampling.LANCZOS),((index%8)*64,(index//8)*64));sheet.paste(image.resize((120,108),Image.Resampling.LANCZOS),((index%8)*128+4,(index//8)*140));draw.text(((index%8)*128+5,(index//8)*140+111),name,fill=(220,215,190));reports.append({'unit':name,'buttonCell':index,'renderedFromModel':str(file),'visiblePixelCount':int(np.count_nonzero(canvas.max(axis=2)))})
(REPO/'bajor/artwork/armadafiles-adaptation/model-preview.png').parent.mkdir(parents=True,exist_ok=True);sheet.save(REPO/'bajor/artwork/armadafiles-adaptation/model-preview.png');atlas.save(OUT/'Textures/RGB/bjrbuttons.tga');(REPO/'reports/bajoran-armadafiles-texture-preview.json').write_text(json.dumps(reports,indent=2));print('Rendered',len(reports),'matching model icons and review sheet.')
