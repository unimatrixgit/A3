"""Create a game-scale Federation T'Varek hero from the user's orthographic reference."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
stage=repo/'patches/tvarek-hero-20261025';dest=stage/'overlay';dest.mkdir(parents=True,exist_ok=True);sourceHashes={};unit='xhftvarek';source='fentd';model=copy.deepcopy(native(source));g=truss.Geometry()
def prism(poly,thickness):
 count=len(poly);vertices=[[x,-thickness/2,z]for x,z in poly]+[[x,thickness/2,z]for x,z in poly];faces=[]
 for i in range(1,count-1):faces.extend([(0,i+1,i),(count,count+i,count+i+1)])
 for i in range(count):j=(i+1)%count;faces.extend([(i,j,count+j),(i,count+j,count+i)])
 g.add(vertices,faces)
prism([(-.035,-1.1),(.035,-1.1),(.25,-.63),(.42,-.08),(.32,.28),(-.32,.28),(-.42,-.08),(-.25,-.63)],.12)
g.torus((0,-.005,.38),.43,.065,n=40,m=8,stretch=(1,.75,1.35));g.box((0,.025,.04),(.14,.17,1.95),taper=.75);g.box((0,.025,.64),(.98,.1,.12))
g.cylinder((0,.14,-.34),.07,.06,n=20,top=.65)
for side in [-1,1]:
 g.beam((side*.27,.07,-.14),(side*.27,.07,-.64),.075);g.beam((side*.38,-.02,.12),(side*.3,-.02,.72),.06)
 g.beam((side*.13,.071,-.79),(side*.3,.071,-.24),.014,'red');g.beam((side*.041,.12,-.18),(side*.041,.12,.84),.012,'red')
 g.box((side*.21,.02,.8),(.065,.08,.11),'engine')
 # Raised, armoured plates break up the large triangular hull.
 for z in [-.43,-.12,.19]:g.box((side*(.16+(z+.43)*.17),.082,z),(.095,.035,.17),yaw=side*.17,taper=.8)
for part in g.parts:
 part['v'][:,2]*=-1;part['f']=[(f[0],f[2],f[1])for f in part['f']]
parts=research_surface_parts(g,source,globals());targetLength=92;points=np.concatenate([p['data']['vertices']for p in parts]);factor=targetLength/np.ptp(points,axis=0).max()
for node in model.nodes:
 if node['type']=='MESH':node['type']='NULL_OR_HARDPOINT';node['data']=None
parent=next(n for n in model.nodes if not n['parent']);inverse=np.linalg.inv(matrix(parent));chunk=0
for part in parts:
 dat=part['data'];mapping={}
 for material in part['materials']:
  ma=copy.deepcopy(material);old=ma['name'];ma['name']='tvmat'+str(len(model.materials));mapping[old]=ma['name'];model.materials.append(ma)
 for group in dat['vertex_lighting_groups']:
  for start in range(0,len(group['faces']),150):
   vv=[];uv=[];faces=[]
   for face in group['faces'][start:start+150]:
    base=len(vv)
    for vi,ui in face:vv.append((inverse@np.r_[dat['vertices'][vi]*factor,1])[:3].tolist());uv.append(dat['texture_coordinates'][ui])
    faces.append([[base+j,base+j]for j in range(3)])
   mesh=copy.deepcopy(dat);mesh.update(vertices=vv,texture_coordinates=uv,vertex_lighting_groups=[{'lighting_material':mapping[group['lighting_material']],'faces':faces}]);mesh.setdefault('borgification',{'texture':dat['texture']})
   if model.version>1.9101:mesh['bump_map']=1
   model.nodes.append({'id':'tvarmesh'+str(chunk),'parent':parent['id'],'type':'MESH','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':mesh});chunk+=1
def hp(name,pos,aft=False):
 v=np.array([pos[0],pos[1],-pos[2]])*factor;local=(inverse@np.r_[v,1])[:3];rot=np.diag([-1.,1.,-1.])if aft else np.eye(3);localRot=inverse[:3,:3]@rot;model.nodes.append({'id':name,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','data':None,'local_transform':localRot.T.tolist()+[local.tolist()]})
for side,label in [(-1,'1'),(1,'2')]:hp('tvc'+label,(side*.27,.07,-.64))
for i,pos in enumerate([(-.18,.09,-.55),(.18,.09,-.55),(-.33,.09,.14),(.33,.09,.14),(-.18,-.09,-.5),(.18,-.09,-.5),(-.32,-.08,.18),(.32,-.08,.18)],1):hp('tvb'+str(i),pos)
for i,pos in enumerate([(-.085,-.05,-.83),(.085,-.05,-.83),(-.16,-.04,.85),(.16,-.04,.85)],1):hp('tvt'+str(i),pos,i>=3)
hp('tvsystem',(0,.08,-.2));path=dest/'SOD/xhftvarek.sod';path.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=model.version
with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(path))
def emit(rel,t):
 path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
 if(root/rel).is_file():sourceHashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
weapons=[]
for alias,src,damage,delay in [('tvarpulse','ffighterpulse',45,2),('tvarbeam','fgalaxyphas',40,2),('tvartorp','fgalaxyphot',95,3)]:
 w=idx[src].read_text(encoding='latin1');wp=yard_unit_properties(src,globals());ordn=idx[wp['ordname'].lower()].read_text(encoding='latin1');w=re.sub(r'(?mi)^\s*(?:savefire|maxshots|minimumshotinterval)\s*=[^\r\n]*','',w);w=put(w,'ordName','"'+alias+'o"');w=put(w,'shotDelay',delay);ordn=put(ordn,'damageBase',damage);emit('odf/weapons/'+alias+'.odf',w);emit('odf/weapons/'+alias+'o.odf',ordn);weapons.append(alias)
t=(root/'odf/ships/xhfpicardd.odf').read_text(encoding='latin1');t=re.sub(r'(?mi)^\s*(?:weapon\d+|weaponhardpoints\d+|possiblecraftnames)\s*=[^\r\n]*','',t)
values={'unitName':'"U.S.S. T\'Varek"','tooltip':'"U.S.S. T\'Varek - Heavy Cruiser Hero"','verboseTooltip':'"U.S.S. T\'Varek\\nParticle cannons, beams and torpedoes\\nVulcan ingenuity in early Federation service."','possibleCraftNames':'"U.S.S. T\'Varek"','baseName':'"xhftvarek"','race':'"federation"','shipclass':'"cruiser"','ScaleSOD':1,'maxHealth':8000,'shieldRate':80,'crewCost':240,'maximumCrew':240,'officerCost':12,'dilithiumCost':1000,'metalCost':450,'latinumCost':0,'biomatterCost':0,'buildTime':90,'maxSpecialEnergy':2500,'specialEnergyRate':25,'hotkeyLabel':'"HOTKEY_F9"'}
for key in ['shieldGeneratorHitPoints','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','sensorsHitPoints']:values[key]=1200
for key in ['enginesTargetHardpoints','lifeSupportTargetHardpoints','weaponsTargetHardpoints','shieldGeneratorTargetHardpoints','sensorsTargetHardpoints','hullTargetHardpoints','criticalTargetHardpoints']:values[key]='"tvsystem"'
layout=[('tvarpulse','tvc1'),('tvarpulse','tvc2'),('tvarbeam','tvb1 tvb2'),('tvarbeam','tvb3 tvb4'),('tvarbeam','tvb5 tvb6'),('tvarbeam','tvb7 tvb8'),('tvartorp','tvt1 tvt2'),('tvartorp','tvt3 tvt4'),('gcorbom','tvsystem'),('xhtphase','tvt1'),('gselfdes','tvsystem')]
for i,(weapon,points)in enumerate(layout,1):values['weapon'+str(i)]='"'+weapon+'"';values['weaponHardpoints'+str(i)]=' '.join('"'+x+'"'for x in points.split())
values['label']='"U.S.S. T\'Varek"';values['shiptype']='"C"'
for k,v in values.items():t=put(t,k,v)
emit('odf/ships/'+unit+'.odf',t);yard='xflegacyyard';rel='odf/stations/'+yard+'.odf';t=(root/rel).read_text(encoding='latin1');items=re.findall(r'(?mi)^\s*buildItem\d+\s*=\s*"([^"]+)"',t);assert len(items)==8 and unit not in items;t+='\nbuildItem8 = "'+unit+'"\n';emit(rel,t)
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');im=preview(load_model(path),800);im.save(stage/'tvarek-render.png');tex=dest/'Textures/RGB';tex.mkdir(parents=True,exist_ok=True);icon=im.resize((64,64));ImageDraw.Draw(icon).rectangle((0,0,63,63),outline=(90,170,255),width=2);ImageDraw.Draw(icon).text((2,49),'HERO',font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',12),fill=(240,215,90));icon.save(tex/'gbxhftvarek.tga');im.resize((64,64)).save(tex/'wfxhftvarek.tga');sprite+='\n@reference=64\n@tmaterial=default\nb_xhftvarek gbxhftvarek 0 0 64 64\n'
dr=ImageDraw.Draw(icon);dr.ellipse((45,2,61,18),fill=(20,65,120),outline=(235,215,140),width=1);dr.polygon([(53,4),(47,16),(53,12),(58,16)],fill=(235,235,220));icon.save(tex/'gbxhftvarek.tga')
for i in range(1,6):sprite+='xhftvarekw'+str(i)+' wfxhftvarek 0 0 64 64\n'
emit('Sprites/gui_global.spr',sprite)
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 rel='techtree/'+tree+'.tt';t=(root/rel).read_text(encoding='latin1');gate=re.search(r'(?mi)^'+yard+r'\.odf\s+(-?\d+)',t);assert gate;t+='\n'+unit+'.odf '+('-1'if int(gate[1])<0 else'0'if tree=='fulltech'else'1 '+yard+'.odf')+' // Federation T\'Varek hero\n';emit(rel,t)
report={'status':'PASS','description':'U.S.S. T\'Varek Federation hero installed at Archer Legacy Yard with custom reference-inspired annular-warp model and matched heavy-cruiser hero statistics.','files':{p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},'sourceHashes':sourceHashes,'baselineUpdates':[unit],'attackAssignments':{unit:yard},'extraAiTargets':{'federation':[unit]},'unit':unit,'yard':yard,'sourceReference':'User-supplied T\'Varek orthographic sheet','stats':{'health':8000,'shieldRegen':80,'crew':240,'energy':2500,'energyRegen':25,'dilithium':1000,'metal':450,'buildTime':90},'weaponLayout':{'heavyParticleCannons':2,'beamEmitters':8,'torpedoTubes':4,'specials':['Corbomite Reflector','Transphasic Torpedo','Self Destruct']},'estimatedNormalBankDPS':188.33333333333334,'comparisonPicardNormalBankDPS':189.28571428571428,'runtimeVerified':False};(stage/'patch.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':'PASS','files':len(report['files']),'yard':yard,'meshChunks':chunk,'runtimeVerified':False}))
