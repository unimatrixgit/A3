"""Distinct Bajoran hulls fitted into native animated skeletons; stage only."""
import pathlib,json,re,sys,io,contextlib,copy,math,hashlib
import numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
ROOT=pathlib.Path('D:/armadaIII');OUT=pathlib.Path('D:/Xaramada-Modwork/bajor-redesign-v3');REPO=pathlib.Path('D:/aramada');manifest=json.loads((OUT/'manifest.json').read_text());idx={f.stem.lower():f for f in(ROOT/'odf').rglob('*.odf')};cache={}
def props(n,seen=None):
 if n in cache:return cache[n]
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
 for inc in re.findall(r'^[ \t]*#include[ \t]+"([^"]+)"',t,re.M):v.update(props(inc.lower().removesuffix('.odf'),seen.copy()))
 for k,x in re.findall(r'^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t,re.M):v[k.lower()]=x.split('//')[0].strip().strip('"')
 cache[n]=v;return v
class Shape:
 def __init__(self):self.v=[];self.uv=[];self.faces=[]
 def poly(self,pts,mat=0):
  start=len(self.v);self.v.extend(pts);x=(mat%2)*.5+.025;y=(mat//2)*.5+.025;corners=[(x,y),(x+.45,y),(x+.45,y+.45),(x,y+.45)]
  self.uv.extend(corners[:len(pts)])
  for i in range(1,len(pts)-1):self.faces.append([[start,start],[start+i,start+i],[start+i+1,start+i+1]])
 def box(self,c,size,mat=0):
  x,y,z=c;a,b,d=np.array(size)/2;v=[(x+i*a,y+j*b,z+k*d)for i,j,k in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  for q in[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(1,2,6,5),(0,4,7,3)]:self.poly([v[i]for i in q],mat)
 def loft(self,sections,mat=0):
  # Beveled eight-sided fuselage along Z.
  rings=[[(math.cos(a)*w,y+math.sin(a)*h,z)for a in np.linspace(0,2*math.pi,9)[:-1]]for z,w,h,y in sections]
  for n in range(len(rings)-1):
   for i in range(8):self.poly([rings[n][i],rings[n][(i+1)%8],rings[n+1][(i+1)%8],rings[n+1][i]],1 if i in[1,2]else mat)
  for ring in[rings[0],rings[-1]]:
   center=np.mean(ring,axis=0).tolist()
   for i in range(8):self.poly([center,ring[i],ring[(i+1)%8]],mat)
 def cylinder(self,c,r,h,axis='y',mat=0,segments=12):
  x,y,z=c;rings=[]
  for q in[-h/2,h/2]:rings.append([(x+math.cos(a)*r,y+q,z+math.sin(a)*r)if axis=='y'else(x+math.cos(a)*r,y+math.sin(a)*r,z+q)for a in np.linspace(0,2*math.pi,segments+1)[:-1]])
  for i in range(segments):self.poly([rings[0][i],rings[0][(i+1)%segments],rings[1][(i+1)%segments],rings[1][i]],mat)
  for ring in rings:
   center=np.mean(ring,axis=0).tolist()
   for i in range(segments):self.poly([center,ring[i],ring[(i+1)%segments]],mat)
 def arc(self,r,w,y,h,start=0,end=360,mat=0,segments=24):
  for a,b in zip(np.linspace(math.radians(start),math.radians(end),segments+1)[:-1],np.linspace(math.radians(start),math.radians(end),segments+1)[1:]):
   v=[(math.cos(t)*rr,yy,math.sin(t)*rr)for t,rr,yy in[(a,r-w/2,y-h/2),(b,r-w/2,y-h/2),(b,r+w/2,y-h/2),(a,r+w/2,y-h/2),(a,r-w/2,y+h/2),(b,r-w/2,y+h/2),(b,r+w/2,y+h/2),(a,r+w/2,y+h/2)]]
   for q in[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(1,2,6,5),(0,4,7,3)]:self.poly([v[i]for i in q],mat)
 def pylon(self,a,r=13,h=20):
  # Curved taper rising from an open radial platform.
  last=None
  for f in np.linspace(0,1,7):
   cx=math.cos(a)*(r-5*f*f);cz=math.sin(a)*(r-5*f*f);w=2.8*(1-.72*f);ring=[(cx+dx*w,h*f,cz+dz*w)for dx,dz in[(-1,-1),(1,-1),(1,1),(-1,1)]]
   if last:
    for i in range(4):self.poly([last[i],last[(i+1)%4],ring[(i+1)%4],ring[i]],1 if i==1 else 0)
   last=ring

def make(u):
 s=Shape();role=u.get('role','');name=u['odf'];ship=u['folder']=='ships'
 if ship:
  heavy=role in['battleship','super','cruiser','assault','torpedo'];length=18 if not heavy else 25
  s.loft([(-length*.6,3,2,0),(-length*.3,5,3,0),(0,6,3,0),(length*.5,2.5,1.3,0),(length*.8,.35,.5,0)])
  for sign in[-1,1]:
   # Swept Bajoran side fins, separately faceted ceramic leading panels.
   pts=[(sign*3,0,7),(sign*15,-1,-6),(sign*10,1,-11),(sign*4,2,-5)]
   s.poly(pts,0);s.poly([(x,y+.65,z)for x,y,z in pts],1)
   for i in range(4):j=(i+1)%4;s.poly([pts[i],pts[j],(pts[j][0],pts[j][1]+.65,pts[j][2]),(pts[i][0],pts[i][1]+.65,pts[i][2])])
   s.cylinder((sign*11,0,-8),2.1,8,'z',0);s.cylinder((sign*11,0,-12.1),1.65,.2,'z',2)
   s.poly([(sign*8,1,-7),(sign*8,8,-9),(sign*8,1,-13)],1)
  s.box((0,3.1,4),(3,.35,5),3)
  if heavy:
   s.arc(8,2,1,1.5,190,350,1,12);s.box((0,3,-4),(6,2,9),1)
  if role in['construction','repair','freighter','cargo','colony','transport']:
   for sign in[-1,1]:
    for z in[-7,-2,3]:s.box((sign*6,3,z),(4,4,4),1)
    if role in['construction','repair']:
     s.box((sign*9,-2,6),(2,2,14));s.box((sign*9,-3,12),(3,4,2),2)
  if role in ['torpedo','artillery']:
   for sign in [-1,1]:s.cylinder((sign*5,4,10),1.2,16 if role=='artillery'else 8,'z',1);s.cylinder((sign*5,4,18 if role=='artillery'else 14),.8,.3,'z',2)
  if role=='special':s.arc(7,1,6,1,0,360,1,16)
  if role=='super':
   for sign in [-1,1]:s.box((sign*16,1,-2),(4,3,18),1);s.box((sign*16,1,-11),(3,2,.4),2)
  if role=='hero':s.box((0,5,-2),(3,2,5),1);s.box((0,6.1,-1),(2,.3,3),3)
  if role=='lightship':
   s=Shape();s.loft([(-5,2,1,0),(0,2,1,0),(6,.2,.2,0)])
   for sign in[-1,1]:
    s.box((sign*10,0,0),(20,.4,.5),0)
    s.poly([(sign*3,0,-10),(sign*18,0,-10),(sign*18,0,10),(sign*3,0,10)],3)
 else:
  if role=='pod':
   s.cylinder((0,0,0),4,3,mat=0);s.cylinder((0,2,0),2.6,1.3,mat=1);s.box((0,3,0),(1,2,1),3);return s
  s.cylinder((0,0,0),7,5,mat=0);s.cylinder((0,4,0),4,3,mat=1)
  if role in['yard','yard2','yard3']:
   s.arc(20,4,0,3,35,325,0,28);s.arc(20,1,2,1,35,325,1,28)
   for a in[math.radians(35),math.radians(325)]:s.pylon(a,20,18 if role!='yard3'else 25)
   s.box((0,-3,-18),(30,2,3),1)
   for x in[-9,9]:s.box((x,0,0),(1,1,22),2)
  elif role in['research','research2','upgrade','sensor','superlab']:
   s.arc(15,3,0,2,0,360,0,24)
   for a in[0,2*math.pi/3,4*math.pi/3]:
    s.pylon(a,15,20 if role!='sensor'else 28);s.cylinder((math.cos(a)*11,1,math.sin(a)*11),4,3,mat=1)
   s.cylinder((0,8,0),3,5,mat=3)
   if role in['research2','upgrade','superlab']:s.arc(7,1,11,1,0,360,1,16)
   if role=='sensor':s.arc(4,1,20,1,0,360,2,16)
  elif role in['mining','orbital','trading']:
   for a in[0,2*math.pi/3,4*math.pi/3]:
    s.arc(14,3,1,3,math.degrees(a)-32,math.degrees(a)+32,0,8);s.pylon(a,14,14);s.cylinder((math.cos(a)*10,-2,math.sin(a)*10),4,7,mat=1)
   s.cylinder((0,10,0),3,12,mat=0);s.box((0,6,11),(9,3,12),1);s.box((0,6.1,17),(6,2,.4),2)
   if role=='trading':s.arc(20,2,-3,2,0,360,1,24)
  else:
   for a in[0,2*math.pi/3,4*math.pi/3]:s.pylon(a,7,10)
   s.box((0,9,4),(3,3,14),0);s.box((0,9,11),(2,2,.4),2)
 if ship and role in ['scout','raider','frigate']:
  sx,sz={'scout':(.62,1.2),'raider':(.8,.64),'frigate':(1.2,.8)}[role];s.v=[(x*sx,y,z*sz)for x,y,z in s.v]
 return s

def matrices(model):
 nodes={n['id']:n for n in model.nodes};memo={}
 def world(n,seen=None):
  if n['id']in memo:return memo[n['id']]
  seen=set()if seen is None else seen
  if n['id']in seen:return np.eye(4)
  seen.add(n['id']);t=np.asarray(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];par=nodes.get(n['parent']);a=world(par,seen)@a if par else a;memo[n['id']]=a;return a
 def chain(n):
  out=[];seen=set()
  while n and n['id']not in seen:seen.add(n['id']);out.append(n['id']);n=nodes.get(n['parent'])
  return out
 return world,chain
reports=[]
for u in manifest['units']:
 name=u['odf']
 if name=='bjbase':continue
 v=props(name);sourceModel=v.get('basename',name)
 with contextlib.redirect_stdout(io.StringIO()):model=IO().read_file(str(ROOT/'SOD'/(sourceModel+'.sod')))
 beforeNodes=len(model.nodes);beforeAnims=len(model._animation_transforms);world,chain=matrices(model)
 visible=[n for n in model.nodes if n['type']=='MESH'and not any(x.lower()in['borg','damage','shield']for x in chain(n))]
 if not visible:raise ValueError('No visible native geometry '+name)
 groups={}
 for n in visible:
  lod=next((x for x in chain(n)if re.fullmatch(r'lod\d+',x,re.I)),None);groups.setdefault(lod,[]).append(n)
 selected=[]
 for group,meshes in groups.items():
  if group is None and any(k is not None for k in groups):continue
  selected.append(max(meshes,key=lambda n:sum(len(g['faces'])for g in n['data']['vertex_lighting_groups'])))
 allv=np.concatenate([(world(n)@np.c_[n['data']['vertices'],np.ones(len(n['data']['vertices']))].T).T[:,:3]for n in visible]);lo=allv.min(axis=0);hi=allv.max(axis=0);center=(lo+hi)/2;shape=make(u);verts=np.array(shape.v);scale=np.ptp(allv,axis=0).max()/np.ptp(verts,axis=0).max();newv=(verts-(verts.max(axis=0)+verts.min(axis=0))/2)*scale+center
 for n in model.nodes:
  if n['type']!='MESH':continue
  d=n['data'];d['texture_material']='opaque'if model.version>1.61 else'default';d['texture']='bjrhull_B'if any(x.lower()=='borg'for x in chain(n))else'bjrhull';d['bump_map']=1
  if model.version>1.9101:d['borgification']={'texture':'bjrhull_B'}
  d['texture_coordinates']=[[.025+.45*float(a),.025+.45*float(b)]for a,b in d['texture_coordinates']]
 for n in selected:
  d=n['data'];lighting=max(d['vertex_lighting_groups'],key=lambda g:len(g['faces']))['lighting_material'];inv=np.linalg.inv(world(n));d['vertices']=(inv@np.c_[newv,np.ones(len(newv))].T).T[:,:3].tolist();d['texture_coordinates']=shape.uv;d['vertex_lighting_groups']=[{'lighting_material':lighting,'faces':shape.faces}];d['cull_type']='NO_CULL'
 model.set_nodes(model.nodes);dest=OUT/'SOD'/('br3_'+name+'.sod');dest.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(dest));check=IO().read_file(str(dest))
 assert len(check.nodes)==beforeNodes and len(check._animation_transforms)==beforeAnims
 assert check._animation_transforms==model._animation_transforms and check._animation_tex_refs==model._animation_tex_refs
 rel=pathlib.Path('odf')/u['folder']/(name+'.odf');text=(ROOT/rel).read_text(encoding='latin1');text=re.sub(r'^[ \t]*baseName[ \t]*=[^\r\n]*','baseName = "br3_'+name+'"',text,flags=re.M|re.I)
 if not re.search(r'^[ \t]*baseName[ \t]*=',text,re.M|re.I):text+='\r\nbaseName = "br3_'+name+'"\r\n'
 (OUT/rel).parent.mkdir(parents=True,exist_ok=True);(OUT/rel).write_bytes(text.encode('latin1'));reports.append({'unit':name,'sourceModel':sourceModel,'model':'br3_'+name,'nativeNodesRetained':beforeNodes,'nativeAnimationChannelsRetained':beforeAnims,'textureAnimationReferencesRetained':len(model._animation_tex_refs),'animationRecordsRoundTripIdentical':True,'replacedMeshIds':[n['id']for n in selected],'triangles':len(shape.faces),'runtimeVerified':False})
(REPO/'reports/bajoran-redesign-v3-models.json').write_text(json.dumps(reports,indent=2));print(json.dumps({'models':len(reports),'nativeAnimationChannelsPreserved':sum(r['nativeAnimationChannelsRetained']for r in reports),'allNodeCountsPreserved':True}))



