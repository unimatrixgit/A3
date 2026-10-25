"""Render proposed connected yard families; never write game files."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
from types import SimpleNamespace
out=repo/'patches/compact-yard-preview';out.mkdir(exist_ok=True)
odfs={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def properties(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen or n not in odfs:return{}
 seen.add(n);t=odfs[n].read_text(encoding='latin1');p={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):p.update(properties(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]*)',t):p[k.lower()]=v.split('//')[0].strip().strip('"')
 return p
roster=[]
for yard in d['yards']['b']:
 p=properties(yard)
 for k,v in p.items():
  if not re.fullmatch('builditem[0-9]+',k):continue
  n=Path(v).stem.lower();s=properties(n);roster.append({'ship':n,'name':s.get('unitname',n),'yard':yard,'hero':n in ['blocutus','xoblocutus','xhbqueen']or n.startswith('mrc'),'cube':any(x in (n+' '+s.get('unitname','')).lower()for x in ['cube','cubus'])})
assert len(roster)==len({r['ship']for r in roster})
report={'currentBorgShips':len(roster),'minimumYardsAt14Slots':math.ceil(len(roster)/14),'roster':roster,'gameFilesChanged':False}
(out/'borg-roster-review.json').write_text(json.dumps(report,indent=2))
names={'b':'Borg','f':'Federation','k':'Klingon','r':'Romulan','c':'Cardassian','d':'Dominion','bj':'Bajoran','br':'Breen','fg':'Ferengi'}
images=[]
for code,title in names.items():
 for tier in ([0,1,2]if code in ['b','f']else[0,2]):
  parts=[];frame=truss.Geometry();ysource=yards[code]
  def add(source,size,pos=(0,0,0),stretch=(1,1,1),yaw=0):
   rot=np.array([[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]])
   for p in pieces(source):p['data']['vertices']=(p['data']['vertices']*np.array(stretch)*size)@rot.T+np.array(pos);parts.append(p)
  central=bases[code];core=1.35+tier*.18
  # Centres retain faction silhouettes, with distinct command superstructures.
  add(central,core,(0,.12,0))
  if tier==2:
   if code=='f':add(central,.82,(0,.9,0),stretch=(1,.55,1))
   elif code=='b':
    for side in [-1,1]:add(central,.38,(side*.32,.45,-.22),stretch=(.7,1,1))
   else:add(central,.48,(0,.58,-.15),yaw=math.pi/3)
  cube=code=='b'
  # Cube yards use one oversized open frame rather than two small bays.
  bays=[(1.3,-.08,0)]if cube else[(-.8,-.08,.06),(.8,-.08,.06)]
  if not cube and tier>0 and ysource+'2'in sods:ysource+='2'
  for pos in bays:add(ysource,1.8+tier*.14 if cube else 1.0+tier*.08,pos,stretch=(1,1,1+tier*.08),yaw=0 if cube else(-.08 if pos[0]<0 else .08)*tier)
  reference=pieces(ysource)[0]
  def pipe(start,end,radius=.035):
   a=np.asarray(start);b=np.asarray(end);axis=b-a;axis=axis/np.linalg.norm(axis);up=np.array([0.,1.,0.]);u=np.cross(axis,up);u/=np.linalg.norm(u);v=np.cross(axis,u);vv=[]
   for center in [a,b]:
    for j in range(10):ang=j*math.tau/10;vv.append((center+radius*(u*math.cos(ang)+v*math.sin(ang))).tolist())
   faces=[]
   for j in range(10):k=(j+1)%10;faces.extend([[j,k,10+j],[k,10+k,10+j]])
   data=copy.deepcopy(reference['data']);data.update(vertices=vv,texture_coordinates=[[j/9,i]for i in [0,1]for j in range(10)],vertex_lighting_groups=[{'lighting_material':reference['data']['vertex_lighting_groups'][0]['lighting_material'],'faces':[[[i,i]for i in f]for f in faces]}]);parts.append({'data':data,'materials':reference['materials']})
  for pos in bays:
   x=pos[0];end=x+(.25 if cube else 0)
   for z in [-.2,.2]:
    frame.beam((0,-.1,z),(end,-.1,z),.11,'hull')
    # Elevated pipes visibly enter the command hull and assembly frame.
    pipe((0,.22,z),(end,.22,z),.045)
    for j in range(1,7):xx=end*j/7;frame.beam((xx,-.16,z-.07),(xx,-.04,z+.07),.025,'hull')
  for g in frame.parts:
   dat=copy.deepcopy(reference['data']);vv=g['v'];dat.update(vertices=vv,texture_coordinates=[[float(v[0]*3)%1,float((v[1]+v[2])*3)%1]for v in vv],vertex_lighting_groups=[{'lighting_material':reference['data']['vertex_lighting_groups'][0]['lighting_material'],'faces':[[[int(i),int(i)]for i in f]for f in g['f']]}]);parts.append({'data':dat,'materials':reference['materials']})
  nodes=[{'id':'root','parent':'','type':'NULL_OR_HARDPOINT','local_transform':[[1,0,0],[0,1,0],[0,0,1],[0,0,0]],'data':None}]
  for i,p in enumerate(parts):nodes.append({'id':'m'+str(i),'parent':'root','type':'MESH','local_transform':[[1,0,0],[0,1,0],[0,0,1],[0,0,0]],'data':p['data']})
  im=preview(SimpleNamespace(nodes=nodes),720);label=title+' '+(['Patrol','Capital','Command'][tier])+(' — single bay'if cube else' — twin bay');ImageDraw.Draw(im).text((15,15),label,font=font,fill=(220,235,245));path=out/(code+'-tier'+str(tier)+'.png');im.save(path);images.append((code,tier,im));print(path,flush=True)
sheet=Image.new('RGB',(1440,360*math.ceil(len(images)/2)),(10,15,22))
for i,(_,_,im)in enumerate(images):sheet.paste(im.resize((720,360)),((i%2)*720,(i//2)*360))
sheet.save(out/'yard-family-contact-sheet.png')
print(json.dumps({'renders':len(images),'borg':report['currentBorgShips'],'minimumBorgYards':report['minimumYardsAt14Slots']}))

