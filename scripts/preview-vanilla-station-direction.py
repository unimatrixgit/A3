"""Isolated artwork previews; never modifies installation or approved overlay."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
from types import SimpleNamespace
out=repo/'patches/vanilla-station-direction-20261026';out.mkdir(exist_ok=True)
names={'f':'Federation','b':'Borg','k':'Klingon','r':'Romulan','c':'Cardassian','bj':'Bajoran','d':'Dominion','br':'Breen','fg':'Ferengi'}
identity=[[1,0,0],[0,1,0],[0,0,1],[0,0,0]]
def render(parts,path,title):
 nodes=[{'id':'root','parent':'','type':'NULL_OR_HARDPOINT','local_transform':identity,'data':None}]
 for i,p in enumerate(parts):nodes.append({'id':'mesh'+str(i),'parent':'root','type':'MESH','local_transform':identity,'data':p['data']})
 im=preview(SimpleNamespace(nodes=nodes),640)
 ImageDraw.Draw(im).text((14,12),title,font=font,fill=(230,238,250));im.save(path);return im
def change(parts,scale=1,pos=(0,0,0),stretch=(1,1,1)):
 p=copy.deepcopy(parts)
 for x in p:x['data']['vertices']=x['data']['vertices']*np.array(stretch)*scale+np.array(pos)
 return p
rows=[];sources=[]
research={'f':'xvstock_fresear','b':'xvstock_bresear','k':'xvstock_kresear','r':'xvstock_rresear','c':'xvstock_cresear','bj':'xvstock_cresear','d':'dresear','br':'brresear','fg':'xfgresearch'}
for code,title in names.items():
 source='xvstock_cyard'if code=='bj'else 'xvstock_'+yards[code]if 'xvstock_'+yards[code]in sods else yards[code]
 p=change(pieces(source));g=truss.Geometry()
 if code=='f':
  # Open-ended longitudinal drydock cage; no command-starbase centre.
  p=change(p,.78,(0,-.12,0),stretch=(1,1,1.25))
  for z in np.linspace(-.66,.66,7):
   ring=[(.49*math.cos(a),.32*math.sin(a),z)for a in np.linspace(0,math.tau,9)]
   for i in range(8):g.beam(ring[i],ring[i+1],.025)
  for a in np.linspace(0,math.tau,8,endpoint=False):
   x,y=.49*math.cos(a),.32*math.sin(a);g.beam((x,y,-.69),(x,y,.69),.024)
  g.box((0,.34,0),(.16,.09,1.45));g.box((.55,-.12,0),(.12,.15,.6))
 elif code=='bj':
  p=change(p,1,(0,0,0),stretch=(1.05,.82,1.12))
  # Refit the Cardassian framework with paired militia control blocks.
  for side in [-1,1]:
   g.box((side*.39,.14,-.13),(.13,.18,.27),yaw=side*.22,taper=.7)
   g.beam((side*.33,.1,-.35),(side*.33,.1,.35),.035)
 elif code=='b':
  for side in [-1,1]:
   g.beam((side*.35,-.2,-.4),(side*.35,-.2,.4),.045)
   for z in [-.32,0,.32]:g.box((side*.39,.04,z),(.1,.24,.12))
 else:
  # Small integrated gantries preserve the original faction silhouette.
  for side in [-1,1]:g.beam((side*.28,-.18,-.35),(side*.28,-.18,.35),.035)
 p+=research_surface_parts(g,source,globals())
 yard=render(p,out/(code+'-yard.png'),title+' drydock - native model base')
 rs=research[code];rs=rs if rs in sods else research['d'];rp=change(pieces(rs));g=truss.Geometry()
 if code=='bj':
  rp=change(rp,1,stretch=(1.08,.82,1.08))
  for side in [-1,1]:g.box((side*.31,.03,0),(.12,.14,.23),yaw=side*.25,taper=.65)
 else:
  g.cylinder((0,-.26,0),.17,.12,n=8 if code=='b'else 16)
 rp+=research_surface_parts(g,rs,globals())
 lab=render(rp,out/(code+'-research.png'),title+' laboratory - native model base')
 rows.append((yard,lab));sources.append({'faction':code,'yardSource':source,'researchSource':rs,'previewOnly':True})
 print(title+' previews saved',flush=True)
sheet=Image.new('RGB',(1280,640*len(rows)),(10,15,22))
for i,(a,b)in enumerate(rows):sheet.paste(a,(0,i*640));sheet.paste(b,(640,i*640))
sheet.save(out/'all-factions.png')
sheet.crop((0,0,1280,1280)).save(out/'federation-borg.png')
sheet.crop((0,4*640,1280,6*640)).save(out/'cardassian-bajoran.png')
(out/'sources.json').write_text(json.dumps(sources,indent=2))
print('PREVIEW ONLY - no live files changed')
