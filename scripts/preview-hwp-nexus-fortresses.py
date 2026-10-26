"""Four connected weapon bastions, sixteen visible banks per existing loadout."""
from pathlib import Path
exec(Path('D:/aramada/scripts/preview-vanilla-station-direction.py').read_text().split('rows=[];sources=[]')[0])
out=repo/'patches/hwp-fortress-v2-20261026';rows=json.loads((out/'loadouts.json').read_text());units=['fhwp','bhwp','khwp','rhwp','chwp','dturret3','bjhwp','tybrhwp','tyfghwp'];codes=['f','b','k','r','c','d','bj','br','fg'];images=[];mounts=[]
for code,unit in zip(codes,units):
 title=names[code];g=truss.Geometry();source={'f':'xvstock_fresear','b':'xvstock_bresear','k':'xvstock_kresear','r':'xvstock_rresear','c':'xvstock_cresear','bj':'xvstock_cresear','d':'dresear','br':'brresear','fg':'xfgmerc'}[code]
 segments=8 if code in ['b','k','br']else 48;radius=.53
 if code=='b':
  g.box((0,0,0),(1.0,.24,1.0));g.box((0,.16,0),(.7,.16,.7));g.box((0,.29,0),(.42,.16,.42))
  for x in [-.38,.38]:
   for z in [-.38,.38]:g.box((x,.12,z),(.14,.35,.14))
 else:
  g.cylinder((0,0,0),radius,.18,'hull',n=segments,top=.97)
  g.cylinder((0,.14,0),.51,.2,'hull',n=segments,top=.4)
  g.cylinder((0,.31,0),.18,.18,'hull',n=segments,top=.55)
  g.cylinder((0,.49,0),.052,.23,'dark',n=12,top=.3)
  g.torus((0,-.07,0),.51,.025,'dark',n=segments)
 g.cylinder((0,-.22,0),.21,.28,'dark',n=segments,top=1.3)
 g.cylinder((0,-.4,0),.08,.14,'hull',n=12,top=1.5)
 if code in ['c','bj']:
  g.torus((0,.02,0),.58,.028,'hull',n=36)
  for a in np.linspace(0,math.tau,3,endpoint=False):g.cylinder((.32*math.cos(a),.26,.32*math.sin(a)),.055,.3 if code=='c'else .18,'hull',n=6,top=.1)
 elif code=='r':g.torus((0,.06,0),.56,.04,'hull',n=48,start=.2,end=math.tau-.2,stretch=(1,.6,1))
 elif code=='d':
  for a in np.linspace(0,math.tau,3,endpoint=False):g.box((.32*math.cos(a),.18,.32*math.sin(a)),(.14,.18,.35),'hull',yaw=-a,taper=.2)
 elif code=='br':
  for x in [-.22,.22]:g.cylinder((x,.34,0),.1,.65,'hull',n=4,top=.1)
 elif code=='bj':g.box((0,.3,0),(.22,.12,.3))
 # Windows and native faction reactor conduits.
 for a in np.linspace(0,math.tau,24,endpoint=False):
  g.box((.515*math.cos(a),.015,.515*math.sin(a)),(.025,.035,.025),'light')
 loadout=next(r for r in rows if r['unit']==unit);assert len(loadout['weapons'])==16
 positions=[]
 for i in range(4):
  a=i*math.pi/2;axis=np.array([math.cos(a),0,math.sin(a)]);cross=np.array([-axis[2],0,axis[0]]);pod=axis*.91
  g.beam(axis*.43,pod,.11,'hull')
  for s in [-1,1]:g.beam(axis*.47+cross*s*.05+[0,.07,0],pod+cross*s*.05+[0,.07,0],.016,'light')
  g.box(pod,(.39,.2,.39),'hull',yaw=-a,taper=.75 if code in ['k','b','br']else .9)
  g.cylinder(pod+[0,.14,0],.16,.10,'hull',n=8 if code in ['b','k','br']else 20,top=.8)
  for j in range(4):
   slot=j*4+i+1;w=loadout['weapons'][slot-1];label=w['label']or'';torp=w['ordnanceClass']=='photontorpedo';pulse=w['ordnanceClass']=='pphaser';p=pod+cross*((j-1.5)*.075)+[0,.18 if j%2==0 else .05,0];end=p+axis*(.24 if torp else .18 if pulse else .29)
   g.beam(p,end,.045 if torp else .026,'dark');g.box(end,(.04,.035,.04),'light',yaw=-a)
   if torp:g.box(p+axis*.08,(.065,.065,.065),'hull',yaw=-a)
   positions.append({'slot':slot,'weapon':w['odf'],'type':label,'position':end.tolist(),'module':i+1})
 # Material colours selected from native texture texels, avoiding stretched UV patches.
 ref=max(pieces(source),key=lambda p:len(p['data']['vertices']));dat=ref['data'];tex=Image.open(texidx[dat['texture'].lower()]).convert('RGB');rgb=np.asarray(tex);h,w=rgb.shape[:2]
 hull={'f':(180,185,195),'b':(48,55,48),'k':(100,85,55),'r':(65,110,75),'c':(150,115,65),'bj':(175,130,70),'d':(110,100,135),'br':(125,155,165),'fg':(180,125,55)}[code]
 light={'f':(60,155,245),'b':(30,240,70),'k':(240,80,30),'r':(80,230,90),'c':(240,170,40),'bj':(240,190,75),'d':(210,90,240),'br':(70,235,220),'fg':(250,180,40)}[code];palette={'hull':hull,'dark':(30,35,40),'light':light};uv={}
 for mat,color in palette.items():
  y,x=np.unravel_index(np.sum((rgb.astype(float)-np.array(color))**2,axis=2).argmin(),(h,w));uv[mat]=[(x+.5)/w,(y+.5)/h]
 parts=[]
 for part in g.parts:
  v=part['v'];d2=copy.deepcopy(dat);d2.update(vertices=v,texture_coordinates=[uv[part['mat']]for _ in v],vertex_lighting_groups=[{'lighting_material':dat['vertex_lighting_groups'][0]['lighting_material'],'faces':[[[int(k),int(k)]for k in f]for f in part['f']]}]);parts.append({'data':d2,'materials':ref['materials']})
 im=render(parts,out/(code+'-fortress.png'),title+' HWP - 16 weapon banks');images.append(im);mounts.append({'unit':unit,'source':source,'weaponBanks':positions});print(title+' 16 banks rendered',flush=True)
sheet=Image.new('RGB',(1920,1920),(10,15,22))
for i,im in enumerate(images):sheet.paste(im,((i%3)*640,(i//3)*640))
sheet.save(out/'all-faction-fortresses.png');(out/'weapon-mount-layout.json').write_text(json.dumps(mounts,indent=2));print('Preview only. No installed files changed.')

