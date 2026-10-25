"""Orthographic textured SOD preview with per-pixel depth, matching intersecting hulls."""
def preview(model,size=400):
 worlds=[];last={};meshes=[];points=[]
 for node in model.nodes:
  parent=last.get(node['parent'].lower());world=(worlds[parent]if parent is not None else np.eye(4))@matrix(node);worlds.append(world);last[node['id'].lower()]=len(worlds)-1
  if node['type']!='MESH':continue
  d=node['data'];v=np.asarray(d['vertices']);v=(world@np.c_[v,np.ones(len(v))].T).T[:,:3];s=np.c_[v[:,0]+v[:,2]*.4,-v[:,1]-v[:,2]*.62,v@np.array([.4,.62,-1])];points.extend(s[:,:2]);meshes.append((v,s,d))
 pts=np.asarray(points);lo=pts.min(0);hi=pts.max(0);center=(lo+hi)/2;scale=(size-40)/max(hi-lo);pixels=np.zeros((size,size,3),dtype=np.uint8);pixels[:]=[10,15,22];depth=np.full((size,size),-np.inf)
 for vertices,screen,data in meshes:
  p=screen.copy();p[:,:2]=(p[:,:2]-center)*scale+size/2;uv=np.asarray(data['texture_coordinates']);tex=data['texture'].lower();texture=texturecache.get(tex)
  if texture is None:texture=Image.open(texidx[tex]).convert('RGB')if tex in texidx else Image.new('RGB',(1,1),(125,130,140));texturecache[tex]=texture
  rgb=np.asarray(texture);th,tw=rgb.shape[:2]
  for group in data['vertex_lighting_groups']:
   for face in group['faces']:
    ids=[x[0]for x in face];t=p[ids];xy=t[:,:2];low=np.maximum(np.floor(xy.min(0)).astype(int),0);high=np.minimum(np.ceil(xy.max(0)).astype(int)+1,size);w,h=high-low
    if w<=0 or h<=0:continue
    den=(xy[1,1]-xy[2,1])*(xy[0,0]-xy[2,0])+(xy[2,0]-xy[1,0])*(xy[0,1]-xy[2,1])
    if abs(den)<1e-6:continue
    yy,xx=np.mgrid[low[1]:high[1],low[0]:high[0]];xx=xx+.5;yy=yy+.5
    a=((xy[1,1]-xy[2,1])*(xx-xy[2,0])+(xy[2,0]-xy[1,0])*(yy-xy[2,1]))/den;b=((xy[2,1]-xy[0,1])*(xx-xy[2,0])+(xy[0,0]-xy[2,0])*(yy-xy[2,1]))/den;c=1-a-b;z=a*t[0,2]+b*t[1,2]+c*t[2,2];region=depth[low[1]:high[1],low[0]:high[0]];mask=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)&(z>region)
    if not mask.any():continue
    coords=uv[[x[1]for x in face]];u=a*coords[0,0]+b*coords[1,0]+c*coords[2,0];v=a*coords[0,1]+b*coords[1,1]+c*coords[2,1];colors=rgb[(v*th).astype(int)%th,(u*tw).astype(int)%tw];vv=vertices[ids];normal=np.cross(vv[1]-vv[0],vv[2]-vv[0]);normal/=np.linalg.norm(normal)+1e-9;light=.5+.5*abs(normal@np.array([.3,.8,-.5]));colors=np.clip(colors*light,0,255).astype(np.uint8);region[mask]=z[mask];out=pixels[low[1]:high[1],low[0]:high[0]];out[mask]=colors[mask]
 return Image.fromarray(pixels)
