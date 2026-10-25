"""One cohesive laboratory per station; no duplicated research-node buildings."""
def research_station_parts(n,code,scope):
 import math,copy
 np=scope['np'];pieces=scope['pieces'];sods=scope['sods'];g=scope['truss'].Geometry();parts=[]
 role=2 if 'upgrade'in n else 1 if n.endswith('2')or n=='xselaresearch'else 0;omega='omega'in n
 families={'f':['xvstock_fresear','xvstock_fresear2','xvstock_fupgrade'],'b':['xvstock_bresear','xvstock_bresear2','xvstock_bupgrade'],'k':['xvstock_kresear','xvstock_kresear2','xvstock_kupgrade'],'r':['xvstock_rresear','xvstock_rresear2','xvstock_rupgrade'],'c':['xvstock_cresear','xvstock_cresear2','xvstock_cupgrade'],'bj':['xvstock_cresear','xvstock_cresear2','xvstock_cupgrade'],'d':['dresear','dresear2','dupgrade'],'br':['brresear']*3,'fg':['xfgresearch']*3,'bg':['xfgresearch']*3}
 source=families[code][role]
 if source not in sods:source=scope['bp'].get('basename',scope['donor'])
 # One native core retains recognisable faction detail inside a fresh hull.
 for p in pieces(source):p['data']['vertices']=p['data']['vertices']*(.68 if not omega else .58);parts.append(p)
 if code=='b':
  if role==0 and not omega:
   g.box((0,-.12,0),(.82,.25,.82));g.box((0,.12,0),(.38,.54,.38))
   for x in [-.32,.32]:
    for z in [-.32,.32]:g.box((x,.09,z),(.17,.45,.17))
    g.beam((x,.32,-.38),(x,.32,.38),.045)
  elif role==1:
   g.box((0,-.2,0),(.82,.22,.65));g.box((0,.1,0),(.42,.35,.36))
   for x in [-.29,.29]:g.box((x,.1,0),(.17,.85,.58))
  else:
   g.box((0,0,0),(.9,.32,.6));g.box((0,-.24,0),(.65,.2,.45))
   for i in range(5):g.box((-.36+i*.18,.22,0),(.065,.3,.66))
  if omega:g.box((0,.48,0),(.3,.3,.3));g.beam((0,-.45,0),(0,.66,0),.12)
 elif code=='f':
  g.cylinder((0,0,0),.46,.17,n=32,top=.82);g.cylinder((0,-.23,0),.14,.5,n=16)
  if role==0:g.box((0,-.02,0),(1.05,.13,.24),taper=.85)
  elif role==1:g.cylinder((0,.28,0),.15,.45,n=16,top=.45);g.torus((0,.3,0),.28,.025,vertical=True)
  else:
   for i in range(4):a=i*math.pi/2;g.beam((0,-.05,0),(.59*math.cos(a),-.05,.59*math.sin(a)),.1)
  if omega:g.torus((0,.22,0),.35,.045,vertical=True);g.cylinder((0,.45,0),.08,.35,n=12)
 elif code=='k':
  g.cylinder((0,0,0),.36,.3,n=6,top=.65)
  for i in range(3):
   a=i*math.tau/3;end=np.array([.55*math.cos(a),.08,.55*math.sin(a)]);g.beam((0,0,0),end,.14);g.box(end,(.34,.18,.15),yaw=-a,taper=.3)
  if role>0:g.cylinder((0,.4,0),.12,.55,n=4,top=.05)
  if role==2:g.torus((0,-.12,0),.4,.055,n=6)
 elif code=='r':
  g.sphere((0,-.05,0),(.48,.16,.33),n=24)
  for side in [-1,1]:g.torus((0,.04,0),.5,.075,n=24,start=side*.1,end=side*.1+math.pi*.8,stretch=(1,.6,1))
  if role==1:g.cylinder((0,.25,-.12),.1,.5,n=8,top=.4)
  if role==2:g.torus((0,.04,0),.32,.07,vertical=True)
  if n=='xselaresearch':g.torus((0,.25,-.16),.22,.045,vertical=True);g.box((0,-.1,.25),(.5,.12,.22),taper=.7)
 elif code in ['c','bj']:
  g.cylinder((0,-.06,0),.39,.24,n=12,top=.7);g.torus((0,-.13,0),.5,.055,n=30)
  for i in range(3):
   a=i*math.tau/3;end=np.array([.52*math.cos(a),.03,.52*math.sin(a)]);g.beam((0,-.05,0),end,.09);g.torus(end,.16,.045,n=14,start=a,end=a+math.pi*1.25,vertical=True)
  if role==1:g.cylinder((0,.27,0),.12,.5 if code=='c'else .35,n=6,top=.2)
  if role==2:g.torus((0,.12,0),.33,.06,n=24,vertical=True)
 elif code=='d':
  g.cylinder((0,0,0),.36,.25,n=6,top=.8)
  for i in range(3):
   a=i*math.tau/3;end=np.array([.48*math.cos(a),-.05,.48*math.sin(a)]);g.beam((0,0,0),end,.16);g.box(end,(.2,.3,.3),yaw=-a,taper=.4)
  if role>0:g.cylinder((0,.4,0),.13,.6,n=6,top=.1)
  if role==2:g.torus((0,-.18,0),.36,.04,n=18)
 elif code=='br':
  g.box((0,0,0),(.35,.4,.85),yaw=.3,taper=.6)
  for side in [-1,1]:g.box((side*.3,side*.12,0),(.15,.45,.65),yaw=side*.25,taper=.65);g.beam((0,0,0),(side*.37,side*.12,0),.08)
 else:
  g.sphere((0,.05,0),(.48,.22,.38),n=24);g.cylinder((0,-.15,0),.4,.15,n=24);g.torus((0,.03,0),.52,.05,n=28,start=.2,end=math.tau-.2)
  for side in [-1,1]:g.cylinder((side*.37,.23,-.06),.1,.4,n=12,top=.65)
 parts+=research_surface_parts(g,source,scope)
 return parts,source

def research_surface_parts(g,source,scope,worldSpace=False):
 """Map original textured hull faces and materials onto the new surfaces."""
 import copy
 np=scope['np'];reference=max(scope['pieces'](source),key=lambda p:sum(len(x['faces'])for x in p['data']['vertex_lighting_groups']));d=reference['data'];uv=np.asarray(d['texture_coordinates']);native=[]
 for group in d['vertex_lighting_groups']:
  for face in group['faces']:
   v=np.asarray(d['vertices'])[[x[0]for x in face]];normal=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(normal)
   if length<1e-10:continue
   native.append((v.mean(axis=0),normal/length,uv[[x[1]for x in face]],group['lighting_material']))
 assert native,source
 centers=np.asarray([x[0]for x in native]);normals=np.asarray([x[1]for x in native])
 out=[]
 for part in g.parts:
  vv=[];coords=[];groups={};points=part['v'];extent=np.ptp(points,axis=0);mid=(points.max(0)+points.min(0))/2
  for face in part['f']:
   triangle=points[list(face)];normal=np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0]);normal/=np.linalg.norm(normal)+1e-12;position=(triangle.mean(axis=0)-mid)/max(float(max(extent)),1e-12)
   match=int(np.argmin(np.sum((centers-position)**2,axis=1)+(.5*(1-np.abs(normals@normal)))))
   _,_,template,material=native[match];start=len(vv);vv.extend(triangle);coords.extend(template);groups.setdefault(material,[]).append([[start+i,start+i]for i in range(3)])
  dat=copy.deepcopy(d);dat.update(vertices=np.asarray(vv),texture_coordinates=np.asarray(coords),vertex_lighting_groups=[{'lighting_material':material,'faces':faces}for material,faces in groups.items()]);out.append({'data':dat,'materials':reference['materials'],'worldSpace':worldSpace})
 return out

def research_pod_fittings(model,bp,source,scope,rawSpan):
 """Place physical collars exactly at the station's original pod hardpoints."""
 import re,copy
 np=scope['np'];g=scope['truss'].Geometry();names=re.findall('[A-Za-z0-9_]+',bp.get('podhardpoints',''));worlds=[];last={};positions={}
 for node in model.nodes:
  parent=last.get(node['parent'].lower());world=(worlds[parent]if parent is not None else np.eye(4))@scope['matrix'](node);worlds.append(world);last[node['id'].lower()]=len(worlds)-1
  if node['id'].lower()in names:positions[node['id'].lower()]=world[:3,3]
 assert set(names)==set(positions),('Missing pod fitting positions',set(names)-set(positions))
 for name,pos in positions.items():
  if np.linalg.norm(pos)>rawSpan*.05:g.beam((0,0,0),pos,rawSpan*.025)
  g.cylinder(pos+[0,-rawSpan*.008,0],rawSpan*.035,rawSpan*.016,n=12)
 parts=research_surface_parts(g,source,scope,True)
 return parts,{name:pos.tolist()for name,pos in positions.items()}
