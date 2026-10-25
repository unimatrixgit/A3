"""Preview compact connected yards without modifying staged or installed assets."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
from types import SimpleNamespace
out=repo/'patches/compact-yard-preview';out.mkdir(exist_ok=True)
for code,title in [('b','Borg'),('f','Federation')]:
 parts=[]
 def add(source,size,pos):
  for p in pieces(source):
   p['data']['vertices']=p['data']['vertices']*size+np.array(pos);parts.append(p)
 add(bases[code],1.65,(0,.08,0))
 for side in [-1,1]:add(yards[code],1.0,(side*.78,-.08,.03))
 frame=truss.Geometry()
 for side in [-1,1]:
  for z in [-.18,.18]:
   frame.beam((0,-.08,z),(side*.9,-.08,z),.12,'hull')
   for step in range(1,7):
    x=side*step*.13
    frame.beam((x,-.15,z-.085),(x,-.01,z+.085),.035,'hull')
 reference=pieces(yards[code])[0]
 for g in frame.parts:
  dat=copy.deepcopy(reference['data']);vv=g['v']
  # Use real hull texture across the connector surfaces instead of sampling
  # one dark texel for every vertex, which produced a featureless black band.
  uv=[[float(v[0]*3)%1,float((v[1]+v[2])*3)%1]for v in vv]
  dat.update(vertices=vv,texture_coordinates=uv,vertex_lighting_groups=[{'lighting_material':reference['data']['vertex_lighting_groups'][0]['lighting_material'],'faces':[[[int(i),int(i)]for i in face]for face in g['f']]}]);parts.append({'data':dat})
 nodes=[{'id':'root','parent':'','type':'NULL_OR_HARDPOINT','local_transform':[[1,0,0],[0,1,0],[0,0,1],[0,0,0]],'data':None}]
 for i,p in enumerate(parts):nodes.append({'id':'mesh'+str(i),'parent':'root','type':'MESH','local_transform':[[1,0,0],[0,1,0],[0,0,1],[0,0,0]],'data':p['data']})
 im=preview(SimpleNamespace(nodes=nodes),900);ImageDraw.Draw(im).text((24,22),title+' — compact connected yard',font=font,fill=(210,230,245));im.save(out/(code+'-compact-yard.png'))
 print(out/(code+'-compact-yard.png'),flush=True)
