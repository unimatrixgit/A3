"""Render game-model geometry into matching build buttons (software rasterizer)."""
import json, math, pathlib, struct
import numpy as np
from PIL import Image
ROOT=pathlib.Path('D:/Xaramada-Modwork/bajor-completion-v2')
manifest=json.loads(pathlib.Path('D:/Xaramada-Modwork/bajor-completion-v2/manifest.json').read_text())
texture=np.asarray(Image.open('D:/Xaramada-Modwork/bajor-completion-v2/Textures/RGB/xbjv2hull.tga').convert('RGB'),dtype=np.float32)
atlas=Image.new('RGB',(512,512),(0,0,0))
for index,unit in enumerate(manifest['units']):
 data=json.loads((ROOT/'SOD'/(unit['odf']+'.geometry.json')).read_text())
 vertices=np.asarray(data['vertices'],dtype=float)
 # Mirrored top-quarter view, consistent across the entire faction.
 projected=np.column_stack(((vertices[:,0]-vertices[:,2])*.707,-vertices[:,1]*.816+(vertices[:,0]+vertices[:,2])*.408))
 projected-=((projected.max(axis=0)+projected.min(axis=0))/2)
 projected*=82/max(np.ptp(projected,axis=0).max(),1)
 projected+=48
 depth=vertices[:,0]+vertices[:,1]+vertices[:,2]
 canvas=np.zeros((96,96,3),dtype=np.uint8);zbuffer=np.full((96,96),-np.inf)
 light=np.array([.3,.9,-.3]);light/=np.linalg.norm(light)
 for face in data['faces']:
  ids=[v[0] for v in face];points=projected[ids]
  lo=np.maximum(np.floor(points.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(points.max(axis=0)).astype(int),95)
  if np.any(hi<lo):continue
  x,y=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
  a,b,c=points;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-8:continue
  wa=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
  wb=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;wc=1-wa-wb
  z=wa*depth[ids[0]]+wb*depth[ids[1]]+wc*depth[ids[2]]
  sub=zbuffer[lo[1]:hi[1]+1,lo[0]:hi[0]+1];mask=(wa>=0)&(wb>=0)&(wc>=0)&(z>sub)
  if not mask.any():continue
  # Geometry exporter emits per-face UV corners; sample the hull consistently.
  uv=np.array([[0,0],[1,0],[1,1]])
  u=(wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0]);v=(wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1])
  color=texture[(v*255).astype(int)%256,(u*255).astype(int)%256]
  normal=np.cross(vertices[ids[1]]-vertices[ids[0]],vertices[ids[2]]-vertices[ids[0]])
  norm=np.linalg.norm(normal);shade=.55+.45*abs(np.dot(normal/max(norm,1e-6),light))
  dest=canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1];dest[mask]=np.clip(color[mask]*shade,0,255).astype(np.uint8);sub[mask]=z[mask]
 icon=Image.fromarray(canvas).resize((64,64),Image.Resampling.LANCZOS)
 atlas.paste(icon,((index%8)*64,(index//8)*64))
 unit['buttonCell']=index
folder=pathlib.Path('D:/aramada/bajor/artwork');atlas.save(folder/'completion-model-buttons.png')
rgba=atlas.convert('RGBA');header=bytearray(18);header[2]=2;header[12:16]=struct.pack('<HH',512,512);header[16]=32;header[17]=8
(ROOT/'Textures/RGB').mkdir(parents=True,exist_ok=True)
(ROOT/'Textures/RGB/xbjv2buttons.tga').write_bytes(header+rgba.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes('raw','BGRA'))
pathlib.Path('D:/Xaramada-Modwork/bajor-completion-v2/manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'{len(manifest["units"])} matching model-rendered buttons generated.')

