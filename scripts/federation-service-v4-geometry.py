"""Reference-proportioned Starfleet service dock, with explicit hull and gantry detail."""
def federation_service_v4(scope):
 import math,copy
 np=scope['np'];g=scope['truss'].Geometry();source='xvstock_fbase'
 g.cylinder((0,-.12,0),.13,.6,'blue',n=24)
 for a in np.linspace(0,math.tau,8,endpoint=False):
  x,z=.22*math.cos(a),.22*math.sin(a);g.beam((x,-.35,z),(x,.1,z),.03,'hull')
 # Swept service hulls and angled open dock frames; retain the approved centre.
 for side in [-1,1]:
  x=side*1.03
  # Slender twin-keel underside and a recessed, segmented maintenance floor.
  for dx in [-.22,.22]:g.box((x+dx,-.06,0),(.12,.12,1.92),'hull',taper=.7)
  for z in [-.72,-.36,0,.36,.72]:
   g.box((x,-.015,z),(.68,.045,.28),'deck',taper=.85)
   g.box((x,.013,z),(.51,.008,.008),'line')
  for edge in [-1,1]:
   xx=x+edge*.36
   g.box((xx,.11,0),(.17,.24,1.82),'hull',taper=.68)
   g.box((xx,.24,0),(.09,.035,1.70),'dark',taper=.85)
   g.beam((xx-edge*.04,.225,-.81),(xx-edge*.04,.225,.81),.014,'blue')
   # Swept end caps replace the blocky square posts.
   for z in [-.86,.86]:g.box((xx,.07,z),(.18,.2,.25),'hull',taper=.45)
   for z in [-.68,-.23,.23,.68]:
    g.box((xx,.15,z),(.19,.12,.18),'dark',taper=.7)
    g.box((xx-edge*.04,.22,z),(.1,.035,.12),'window')
  # Chamfered service arches with braced shoulders, leaving both ends open.
  for z in [-.65,0,.65]:
   for edge in [-1,1]:
    a=(x+edge*.4,.12,z);b=(x+edge*.34,.43,z);c=(x+edge*.23,.53,z)
    g.beam(a,b,.045,'hull');g.beam(b,c,.038,'hull')
    g.beam((x+edge*.36,.18,z-.07),(x+edge*.33,.41,z+.07),.016,'dark')
    g.box((x+edge*.31,.39,z),(.055,.06,.075),'window',taper=.6)
   g.beam((x-.23,.53,z),(x+.23,.53,z),.028,'dark')
   g.box((x,.5,z),(.1,.055,.09),'hull',taper=.7)
  for edge in [-1,1]:
   g.beam((x+edge*.23,.53,-.7),(x+edge*.23,.53,.7),.017,'hull')
  for dx in [-.18,.18]:
   g.box((x+dx,.024,0),(.012,.008,1.72),'blue')
   g.box((x+dx,-.035,.97),(.055,.06,.27),'hull',taper=.7)
   g.box((x+dx,.002,.98),(.012,.008,.26),'blue')
  for z in [-.24,.24]:
   g.beam((side*.22,.12,z),(x-side*.35,.12,z),.095,'hull')
   g.beam((side*.3,.17,z),(x-side*.35,.17,z),.018,'window')
 # Retain native textures/materials but choose clean panel/light texels.
 parts=[];reference=max(scope['pieces'](source),key=lambda p:len(p['data']['vertices']));texture=scope['Image'].open(scope['texidx'][reference['data']['texture'].lower()]).convert('RGB');rgb=np.asarray(texture);h,w=rgb.shape[:2]
 palette={'hull':(190,195,202),'dark':(36,42,48),'deck':(55,65,80),'gold':(170,125,45),'blue':(40,130,250),'window':(245,221,155),'line':(135,146,160),'violet':(130,70,230)}
 coords={}
 for name,color in palette.items():
  distance=np.sum((rgb.astype(float)-np.array(color))**2,axis=2);y,x=np.unravel_index(distance.argmin(),distance.shape);coords[name]=[(x+.5)/w,(y+.5)/h]
 for part in g.parts:
  ref=reference
  if part['mat']=='blue':ref=max(scope['pieces']('xvstock_fyard'),key=lambda p:len(p['data']['vertices']))
  dat=copy.deepcopy(ref['data']);v=part['v'];coord=coords[part['mat']]
  if part['mat']=='blue':
   arr=np.asarray(scope['Image'].open(scope['texidx'][dat['texture'].lower()]).convert('RGB'));hh,ww=arr.shape[:2];yy,xx=np.unravel_index(np.sum((arr.astype(float)-np.array([40,130,250]))**2,axis=2).argmin(),(hh,ww));coord=[(xx+.5)/ww,(yy+.5)/hh]
  dat.update(vertices=v,texture_coordinates=[coord for _ in v],vertex_lighting_groups=[{'lighting_material':ref['data']['vertex_lighting_groups'][0]['lighting_material'],'faces':[[[int(i),int(i)]for i in face]for face in part['f']]}]);parts.append({'data':dat,'materials':ref['materials']})
 
 core=scope['change'](scope['pieces']('xvstock_fbase'),1.5,(0,.22,0),stretch=(1.08,.88,1.08))
 return core+parts,source


