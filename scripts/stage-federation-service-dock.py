"""Federation reference-style saucer with two connected open service decks."""
from pathlib import Path
script=Path('D:/aramada/scripts/stage-vanilla-station-redesign.py').read_text(encoding='utf-8-sig')
script=script.replace("stage=repo/'patches/vanilla-stations-20261026'","stage=repo/'patches/federation-service-dock-20261026'")
script=script.replace("if a['kind']not in ['yard','service','research']:continue","if n!='xyr_f':continue")
geometry='''
 g=truss.Geometry();source='xvstock_fresear'
 # Federation command saucer and engineering spindle, with no biodome.
 g.cylinder((0,.16,0),.35,.11,n=40,top=.82)
 g.cylinder((0,.08,0),.28,.08,n=32,top=1.24)
 g.cylinder((0,-.13,0),.115,.4,n=20,top=1.25)
 g.cylinder((0,-.3,0),.21,.07,n=24,top=1.1)
 g.cylinder((0,.31,0),.075,.24,n=16,top=.58)
 g.cylinder((0,.49,0),.018,.19,n=8,top=.4)
 for side in [-1,1]:
  x=side*.69
  # Twin flat decks with open bow/stern exits and overhead crane bridges.
  g.box((x,-.16,0),(.66,.07,1.57))
  for dx in [-.3,.3]:
   g.box((x+dx,-.04,0),(.065,.24,1.62))
   g.beam((x+dx,.1,-.76),(x+dx,.1,.76),.025)
   for z in [-.66,-.22,.22,.66]:
    g.box((x+dx,.13,z),(.055,.33,.07))
  for z in [-.66,-.22,.22,.66]:g.beam((x-.3,.3,z),(x+.3,.3,z),.035)
  for z in [-.58,.58]:
   g.beam((side*.16,-.02,z*.3),(x,-.08,z),.07)
   g.beam((side*.18,.02,z*.3),(x,.05,z),.022)
  for dx in [-.17,0,.17]:g.box((x+dx,-.1,0),(.025,.025,1.63))
 allparts=research_surface_parts(g,source,globals());central=source
 # Use the original light hull panels rather than the lab's dark underside.
 for part in allparts:
  dat=part['data'];tex=Image.open(texidx[dat['texture'].lower()]).convert('RGB');rgb=np.asarray(tex);h,w=rgb.shape[:2];templates=[]
  for ref in pieces(source):
   rd=ref['data']
   if rd['texture'].lower()!=dat['texture'].lower():continue
   ru=np.asarray(rd['texture_coordinates'])
   for group in rd['vertex_lighting_groups']:
    for face in group['faces']:
     uv=ru[[ui for vi,ui in face]];u,v=uv.mean(0);light=float(rgb[int(v*h)%h,int(u*w)%w].mean());templates.append((light,uv))
  templates.sort(key=lambda x:x[0],reverse=True);templates=templates[:max(1,len(templates)//5)]
  if templates:
   coords=[]
   for group in dat['vertex_lighting_groups']:
    for i,face in enumerate(group['faces']):
     uv=templates[i%len(templates)][1]
     for j,pair in enumerate(face):pair[1]=len(coords);coords.append(uv[j])
   dat['texture_coordinates']=coords
'''
script=script.replace(" points=np.concatenate([p['data']['vertices']for p in allparts]);",geometry+" points=np.concatenate([p['data']['vertices']for p in allparts]);")
script=script.replace("pos=(np.zeros(3)-center)/span*size","pos=(np.array([-.69,-.02,0])-center)/span*size")
script=script.replace("Approved vanilla-derived faction yards and research artwork, with Cardassian-derived Bajoran refits. Stats and technology unchanged.","Federation service dock redesigned with central saucer and two connected open service decks. Existing repair, recrew and decommission behavior preserved.")
exec(compile(script,__file__,'exec'))
