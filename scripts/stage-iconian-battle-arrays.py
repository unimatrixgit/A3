"""Prepare only: actual SOD models, icons, faction menus and research. Never writes live files."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import importlib.util,shutil
from PIL import ImageFont
spec=importlib.util.spec_from_file_location('geometry',repo/'scripts/approved-station-geometry.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
P=json.loads((repo/'reports/iconian-before.json').read_text())
stage=Path('D:/Xaramada-Modwork/iconian-battle-array-stage');overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True)
pending={};records=[];ability_pods={};source_hashes={};menus=[]
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
art=repo/'artwork/iconian-battle-array/v1'
atlas_source=art/'faction-materials-source.png'
if not atlas_source.exists():
 original=Path('C:/Users/thoma/.codex/generated_images/01a15648-67ee-7c02-ad5c-95c9665332e3/exec-8ee98eb6-d3b6-476b-9421-493445da2b86.png');shutil.copy2(original,atlas_source)
atlas=Image.open(atlas_source).convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
atlaspath=overlay/'Textures/RGB/ia26mat.tga';atlaspath.parent.mkdir(parents=True,exist_ok=True);atlas.save(atlaspath)
texidx['ia26mat']=atlaspath
config=[
 ('federation','fiaarray','fconst2',['fconst','fconst2','xfuconst','ffreight'],[('gcorbom','fedpod1',4)],0),
 ('klingon','kiaarray','kconst2',['kconst','kconst2','xkuconst','kfreight'],[('gplasmac','klipod1',4)],2),
 ('romulan','riaarray','rconst2',['rconst','rconst2','xruconst','rfreight'],[('grcloak',None,5)],3),
 ('cardassian','ciaarray','xcconst2',['cconst','xcconst2','xcuconst','cfreight'],[('gplasmabank','carpod1',4),('gcloak',None,5)],4),
 ('dominion','diaarray','xdconst2',['dconst','xdconst2','xduconst','dfreight'],[('gdcteam','dompod2',4)],5),
 ('bajoran','bjiaarray','xbjconst2',['bjconst','xbjconst2','xbjuconst','bjfreight'],[],6),
 ('species8472','siaarray','714const',['8472_active','8472_passive','714const','xsuconst'],[],9),
 ('breen','briaarray','brconst',['brconst','brfreight'],[],7),
 ('ferengi','fgiaarray','xfgconst',['xfgconst','xfgdil2','xfgdil3'],[],8),
 ('borg','xbtarray',None,['bconst','bconst2','xbuconst','bfreight'],[],1),
]
basepath=Path(P['xbtarray']['file']);basetext=basepath.read_text(encoding='latin1');old=load(root/'SOD/xbtarray.sod')
basepts=np.array([p for t in mesh_triangles(old)for p in t]);oldspan=np.ptp(basepts,axis=0).max();oldcenter=(basepts.max(0)+basepts.min(0))/2

def progress(message):
 print(message,flush=True)
 s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']=message+' Staging only; live game unchanged.'
 (repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
 with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Iconian staging] '+message+'\n')

def text(rel):return pending.get(rel,(root/rel).read_text(encoding='latin1')if(root/rel).exists()else'')
def settext(rel,t):
 if(root/rel).exists():source_hashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
 pending[rel]=t
def quote(v):return '"'+v+'"'
def structure(race):
 g=geo.Geometry()
 organic=race=='species8472'
 # Two interrupted polygonal crescents and a hollow ship assembly bay.
 for level,radius in [(0,1.05),(.12,.92)]:
  for side in [-1,1]:
   angles=np.linspace(.16*math.pi,.85*math.pi,10)
   for a,b in zip(angles[:-1],angles[1:]):
    aa=np.array([side*radius*math.sin(a),level,radius*math.cos(a)]);bb=np.array([side*radius*math.sin(b),level,radius*math.cos(b)])
    g.beam(aa,bb,.16 if level==0 else .065,'hull')
    g.beam(aa+[0,.09,0],bb+[0,.09,0],.018,'glow')
 for side in [-1,1]:
  # Split Iconian central spire, with open portal between the two halves.
  g.box((side*.13,.18,0),(.14,1.35,.32),taper=.25)
  g.beam((side*.12,-.44,-.05),(side*.12,.74,-.05),.026,'glow')
  g.beam((side*.16,-.2,0),(side*.85,0,-.15),.11)
  # Shipyard rails: open centre, overhead rib and an unobstructed exit.
  g.box((side*.36,-.27,.64),(.14,.13,.88),'dark')
  g.box((side*.39,-.11,.4),(.12,.24,.28))
  g.beam((side*.39,.02,.34),(side*.39,.02,.9),.035,'glow')
  g.beam((side*.43,-.25,.12),(side*.43,.18,.12),.06)
 g.beam((-.43,.18,.12),(.43,.18,.12),.075)
 # Side intake module, visibly independent of the construction aperture.
 g.beam((.7,0,-.25),(1.12,-.07,-.3),.16)
 g.cylinder((1.14,-.12,-.3),.22,.32,n=12)
 g.torus((1.14,.06,-.3),.19,.025,'glow',n=12)
 for a in np.linspace(0,math.tau,8,endpoint=False):g.box((1.14+.19*math.cos(a),-.09,-.3+.19*math.sin(a)),(.05,.3,.05),'pipes')
 for side in [-1,1]:
  if race=='borg':
   for z in [-.65,-.3,.05,.4,.7]:
    g.box((side*.8,.12,z),(.25,.22,.22));g.box((side*.81,.25,z),(.16,.035,.12),'glow')
    g.beam((side*.65,-.1,z),(side*.91,.3,z),.035,'dark')
   g.box((side*.3,.48,-.12),(.18,.38,.36))
  elif race=='federation':
   g.box((side*.97,.04,-.13),(.17,.15,.72),taper=.8);g.box((side*.97,.05,-.5),(.14,.09,.08),'glow')
  elif race in ['romulan','klingon']:
   g.box((side*.9,.13,-.3),(.45,.11,.65),yaw=side*.4,taper=.3);g.beam((side*.7,.05,-.7),(side*1.17,.16,.1),.075)
  elif race in ['cardassian','bajoran']:
   for z in [-.5,-.15,.2,.5]:g.box((side*.92,.08,z),(.19,.18,.09),yaw=side*.12)
   g.cylinder((side*.85,.22,-.15),.085,.42,n=4,top=.18)
  elif race=='dominion':
   for z in [-.5,-.05,.4]:g.sphere((side*.88,.12,z),(.21,.17,.27),n=10,m=5)
   g.box((side*.55,.17,-.48),(.15,.2,.5),taper=.2)
  elif race=='ferengi':
   g.sphere((side*.84,.16,-.4),(.27,.16,.3),n=12,m=6);g.cylinder((side*.84,.31,-.4),.09,.04,'glow',n=12)
   g.torus((0,0,-.1),.78,.04,n=18,start=.1*math.pi,end=.9*math.pi)
  elif race=='breen':g.box((side*.92,.05,-.18),(.33,.33,.7),taper=.8);g.box((side*.99,.23,-.4),(.2,.16,.28),'dark')
  elif organic:
   for z in [-.55,-.1,.4]:g.sphere((side*.83,.08,z),(.21,.24,.3),n=10,m=5)
   for y in [-.3,.1,.45]:g.torus((0,y,-.07),.26,.045,n=14,vertical=True,stretch=(1,1,.6))
 return g

def make_model(race,alias,tile):
 g=structure(race);m=copy.deepcopy(old)
 for n in m.nodes:
  if n['type']=='MESH':n['type']='NULL_OR_HARDPOINT';n['data']=None
 parent=next(n for n in m.nodes if not n['parent']);inv=np.linalg.inv(matrix(parent));points=np.concatenate([p['v']for p in g.parts]);center=(points.max(0)+points.min(0))/2;span=np.ptp(points,axis=0).max()
 def location(v):return(inv@np.r_[(np.array(v)-center)/span*oldspan+oldcenter,1])[:3].tolist()
 glow=13 if race in ['borg','romulan']else 14 if race in ['dominion','species8472']else 15 if race in ['klingon','cardassian','bajoran','ferengi']else 12
 # Combine geometry by material to keep the model lightweight.
 for mat in ['hull','dark','pipes','glow']:
  vv=[];uv=[];ff=[];cell={'hull':tile,'dark':10,'pipes':11,'glow':glow}[mat]
  for part in g.parts:
   if part['mat']!=mat:continue
   for face in part['f']:
    tri=part['v'][list(face)];normal=np.abs(np.cross(tri[1]-tri[0],tri[2]-tri[0]));axis=int(normal.argmax());axes=[i for i in range(3)if i!=axis];proj=tri[:,axes];lo=part['v'][:,axes].min(0);delta=np.ptp(part['v'][:,axes],axis=0);delta[delta<1e-6]=1
    mapped=(proj-lo)/delta*.215+.0175;start=len(vv)
    for v,q in zip(tri,mapped):vv.append(location(v));uv.append([(cell%4)*.25+q[0],(cell//4)*.25+q[1]])
    ff.append([[start+j,start+j]for j in range(3)])
  material=copy.deepcopy(old.materials[0]);material['name']='ia_'+mat;material['ambient_color']=[.6,.6,.6];material['diffuse_color']=[1.,1.,1.];material['self_illumination_enabled']=mat=='glow';m.materials.append(material)
  data={'texture_material':'default','bump_map':1,'texture':'ia26mat','borgification':{'texture':'ia26mat'},'vertices':vv,'texture_coordinates':uv,'vertex_lighting_groups':[{'lighting_material':'ia_'+mat,'faces':ff}],'cull_type':0}
  m.nodes.append({'id':'ia_mesh_'+mat,'parent':parent['id'],'type':'MESH','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':data})
 anchors={'iabuild':(0,-.12,.65),'iadock':(1.14,.15,-.3)}
 for i in range(1,13):a=(i-1)*math.tau/12;anchors['iagun'+str(i).zfill(2)]=(.92*math.cos(a),.13,.82*math.sin(a))
 for name,pos in anchors.items():m.nodes.append({'id':name,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],location(pos)],'data':None})
 dest=overlay/'SOD'/(alias+'.sod');dest.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(dest))
 check=load(dest);assert len(check.nodes)==len(m.nodes);assert len(check._animation_transforms)==len(old._animation_transforms)
 for n in check.nodes:
  if n['type']=='MESH':assert np.isfinite(n['data']['vertices']).all()and np.isfinite(n['data']['texture_coordinates']).all()
 return check,sum(len(n['data']['vertex_lighting_groups'][0]['faces'])for n in check.nodes if n['type']=='MESH')

def alias_special(unit,source,pod,slot):
 global sprite
 alias=unit+'s'+str(slot);t=Path(P[source]['file']).read_text(encoding='latin1')
 for k,v in {'buttonSlot':slot,'popupSlot':slot+1,'hotkeyLabel':quote('HOTKEY_F'+str(slot))}.items():t=put(t,k,v)
 if pod:t=put(t,'assimilatable',quote(pod))
 else:t=re.sub(r'(?mi)^\s*assimilatable\s*=[^\r\n]*','',t)
 settext('odf/special_weapons/'+alias+'.odf',t);ability_pods[alias]=pod
 match=re.search(r'(?mi)^b_'+re.escape(source)+r'[ \t]+[^\r\n]+',sprite);assert match,('ability button',source)
 ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:match.start()])[-1]
 sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+','b_'+alias,match[0])+'\n'
 return alias

font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',16)
for race,unit,builder,items,specials,tile in config:
 progress('Building Iconian model and production assets: '+race)
 for n in items:assert n in P,('missing production unit',n)
 modelname='ia26_'+unit;m,faces=make_model(race,modelname,tile)
 t=basetext;t=re.sub(r'(?mi)^[ \t]*(?:weapon(?:Hardpoints)?\d+|buildItem\d+)\s*=[^\r\n]*','',t)
 slot=sum(1 for k in P[builder]if re.fullmatch('builditem[0-9]+',k))+1 if builder else 6
 values={'baseName':quote(modelname),'race':quote(race),'unitName':quote('Borg Tactical Battle Array'if race=='borg'else'Iconian Battle Array'),'tooltip':quote('Borg Tactical Battle Array'if race=='borg'else'Iconian Battle Array'),'possibleCraftNames':quote('Collective Battle Array'if race=='borg'else race.title()+' Iconian Array'),'buildHardpoint':quote('iabuild'),'dockingHardpoint':quote('iadock'),'repairfacility':0,'freighterName':quote(items[-1]if race!='species8472'else'8472_collector'),'resourcesCanHandle':quote('dilithium'if race!='species8472'else'biomatter'),'dilithiumTransferRate':30 if race!='species8472'else 0,'biomatterTransferRate':30 if race=='species8472'else 0,'hotkeyLabel':quote('HOTKEY_F'+str(slot))}
 if race=='species8472':values.update(dilithiumCost=0,metalCost=0,latinumCost=0,biomatterCost=26000,crewCost=0)
 # Required faction-native construction and economy menus, no changes to starting fleets.
 for k,v in values.items():t=put(t,k,v)
 for k in re.findall(r'(?mi)^\s*(\w*TargetHardpoints)\s*=',t):t=put(t,k,' '.join(quote('iagun'+str(i).zfill(2))for i in range(1,7)))
 banks=['bb3phas']*6+['bb3phot']*4
 abilities=[]
 if race=='borg':banks+=['xbarrayhold','xbarraywarp'];abilities=['Green Holding / Assimilation Beam','Transwarp Drive']
 else:
  for source,pod,slot in specials:banks.append(alias_special(unit,source,pod,slot));abilities.append(P[source].get('wpnname',source))
 for i,w in enumerate(banks,1):t+='\nweapon'+str(i)+' = '+quote(w)+'\nweaponHardpoints'+str(i)+' = '+quote('iagun'+str(i).zfill(2))+'\n'
 for i,n in enumerate(items):t+='\nbuildItem'+str(i)+' = '+quote(n)+'\n'
 name='Borg Tactical Battle Array'if race=='borg'else'Iconian Battle Array'
 t=put(t,'verboseTooltip',quote(name+'\\n'+(', '.join(abilities)or'Battle defence, ship construction')+'\\n'+'Ancient architecture reforged for a new empire.'))
 settext('odf/stations/'+unit+'.odf',t)
 # Textured renders from the actual exported SOD model.
 im=preview(m,320);im.save(stage/(unit+'-preview.png'));thumb=im.resize((64,64),Image.Resampling.LANCZOS).convert('RGB')
 dr=ImageDraw.Draw(thumb);dr.rectangle((0,0,63,63),outline=(235,90,65),width=2);dr.rectangle((1,47,62,62),fill=(12,17,24));dr.text((9,47),'ARRAY',font=font,fill=(245,215,125))
 # Two functional badges: battle defence and construction yard.
 dr.line((4,5,17,5,16,14,10,19,5,14,4,5),fill=(255,105,85),width=2);dr.line((47,4,47,19,60,19,60,4),fill=(90,180,255),width=2)
 tex='gb'+modelname;thumb.save(overlay/'Textures/RGB'/(tex+'.tga'));portrait='wf'+modelname;im.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(overlay/'Textures/RGB'/(portrait+'.tga'))
 for key in ['b_'+unit,'b_'+modelname]+[n+'w'+str(i)for n in [unit,modelname]for i in range(1,6)]:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+unit+' '+tex+' 0 0 64 64\nb_'+modelname+' '+tex+' 0 0 64 64\n'
 for n in [unit,modelname]:
  for i in range(1,6):sprite+=n+'w'+str(i)+' '+portrait+' 0 0 64 64\n'
 if builder:
  builders=[builder]+(['8472_defender']if race=='species8472'else['f31const']if race=='federation'else['domconst']if race=='cardassian'else[])
  for b in builders:
   rel=Path(P[b]['file']).relative_to(root).as_posix();bt=text(rel);entries=[v for k,v in sorted(P[b].items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1)if re.fullmatch('builditem[0-9]+',k)]
   if unit not in entries:entries.append(unit)
   assert len(entries)<=14,('constructor menu overflow',b,len(entries))
   bt=re.sub(r'(?mi)^[ \t]*buildItem\d+\s*=[^\r\n]*','',bt)
   for i,n in enumerate(entries):bt+='\nbuildItem'+str(i)+' = '+quote(n)+'\n'
   settext(rel,bt);menus.append({'constructor':b,'items':entries})
 records.append({'unit':unit,'race':race,'model':modelname,'triangles':faces,'production':items,'abilities':abilities,'constructor':builder,'transwarp':race=='borg','energy':200000,'energyRecharge':20000,'health':22000,'crew':0 if race=='species8472'else 5000,'maxCrew':5000,'biomatterException':race=='species8472'})

settext('Sprites/gui_global.spr',sprite)
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 rel='techtree/'+tree+'.tt';t=text(rel)
 for race,unit,builder,items,specials,tile in config:
  if race=='borg':continue
  assert not re.search(r'(?mi)^'+unit+r'\.odf\s',t),('unit exists',unit)
  t+='\n'+unit+'.odf '+('0'if tree=='fulltech'else'1 '+builder+'.odf')+' // Iconian Battle Array\n'
 for alias,pod in ability_pods.items():t+='\n'+alias+'.odf '+('0'if not pod or tree=='fulltech'else'-1'if tree=='nospweap'else'1 '+pod+'.odf')+' // Iconian faction ability\n'
 settext(rel,t)
for rel,t in pending.items():dest=overlay/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
sheet=Image.new('RGB',(1280,5*365+70),(9,16,24));dr=ImageDraw.Draw(sheet);titlefont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',25);dr.text((25,15),'ICONIAN BATTLE ARRAYS — ACTUAL STAGED GAME MODELS',font=titlefont,fill=(225,205,155))
for i,r in enumerate(records):x=(i%2)*640;y=70+(i//2)*365;im=Image.open(stage/(r['unit']+'-preview.png'));sheet.paste(im,(x+150,y));dr.text((x+24,y+320),r['race'].upper()+' | '+(', '.join(r['abilities'])or'Battle array'),font=font,fill=(210,220,230))
sheet.save(stage/'Iconian-actual-models.png')
files={p.relative_to(overlay).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in overlay.rglob('*')if p.is_file()}
report={'status':'STAGED - NOT APPLIED','stage':str(stage),'overlay':str(overlay),'units':records,'menus':menus,'abilityResearch':ability_pods,'sourceHashes':source_hashes,'files':files,'startingFleetsChanged':False,'runtimeVerified':False,'note':'All arrays retain Borg baseline normal weapon stats and appearance. Faction-specific special abilities use native research. 8472 uses combined resource value as biomatter. Borg original retains transwarp and assimilation.'}
(stage/'manifest.json').write_text(json.dumps(report,indent=2));(repo/'reports/iconian-staged.json').write_text(json.dumps(report,indent=2));progress('Iconian arrays staged: ten models, nine faction clones, Borg redesign. Static validation pending.')
