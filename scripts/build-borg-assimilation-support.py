from pathlib import Path
import json,re,copy,contextlib,io,shutil
from PIL import Image
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
R=Path('D:/armadaIII'); O=Path('D:/Xaramada-Modwork/borg-assimilation-stations'); A=Path('D:/aramada/borg/artwork/assimilation-stations')
def put(p,t):
 p=O/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
def override(t,vals):
 for k,v in vals.items():
  t=re.sub(r'^\s*'+re.escape(k)+r'\s*=.*$', '',t,flags=re.M|re.I)
  t+='\n'+k+' = '+str(v)+'\n'
 return t
G=Path('C:/Users/thoma/.codex/generated_images/01a145a1-f38b-7cd1-b2f0-542bd7532033')
for tex,png in [('xbharvtex','exec-0afe84e4-d866-4de7-812a-c2a734d6b080.png'),('xbasstex','exec-7530b78e-775e-40cc-93dc-6bef487ee5c6.png'),('xbdrntex','exec-0bf5e7b8-ab51-40fc-96ad-f53afcd28648.png')]:
 A.mkdir(parents=True,exist_ok=True);shutil.copy2(G/png,A/(tex+'.png'));p=O/'Textures/RGB'/(tex+'.tga');p.parent.mkdir(parents=True,exist_ok=True);Image.open(G/png).convert('RGB').resize((256,256),Image.Resampling.LANCZOS).save(p)
for src,dst,old,new in [('xvstock_bturret','xbharvest','brecx','xbharvtex'),('xvstock_bturret2','xbassimst','brecy','xbasstex'),('fsrepair','xbrepair','OLYMPIC','xbdrntex')]:
 with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(R/'SOD'/(src+'.sod')))
 nodes=copy.deepcopy(m.nodes)
 for n in nodes:
  if n['type']=='MESH':
   d=n['data']
   if d['texture'].lower()==old.lower():
    d['texture']=new
    if d.get('borgification'):d['borgification']['texture']=new
  if dst=='xbrepair':
   if n['id']=='borg':n['id']='assimilation_overlay'
   if n['parent']=='borg':n['parent']='assimilation_overlay'
 if dst=='xbassimst':
  for name,z in [('build',-160),('repair',160)]:
   n=copy.deepcopy(next(n for n in nodes if n['id']=='hp01'));n['id']=name;n['local_transform']=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,float(z)]];nodes.append(n)
 texnames={f.stem.lower()for f in(R/'Textures').rglob('*.tga')}|{f.stem.lower()for f in(O/'Textures').rglob('*.tga')}
 for n in nodes:
  if n['type']=='MESH':
   b=n['data'].get('borgification')
   if b and b['texture'].lower()not in texnames:b['texture']=n['data']['texture']
 m.set_nodes(nodes);p=O/'SOD'/(dst+'.sod');p.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(p));check=IO().read_file(str(p))
 assert len(check.nodes)==len(nodes)
for unit,src,beam,crew,dil,metal,off,time in [('xbharvest','bturret','xbharvbeam',200,150,150,4,30),('xbassimst','bturret2','xbassimbeam',500,300,600,6,60)]:
 t=(R/'odf/stations'/(src+'.odf')).read_text(encoding='latin1')
 name='Harvester Station' if crew==200 else 'Assimilation Station'
 vals={'unitName':json.dumps(name),'tooltip':json.dumps(name),'verboseTooltip':json.dumps(name+' - '+('Blue crew-harvesting beam.' if crew==200 else 'Green boarding beam. Produces Borg Repair Drones.')),'baseName':json.dumps(unit),'weapon1':json.dumps(beam),'crewCost':crew,'maximumCrew':crew,'has_crew':1,'lifeSupportHitPoints':200,'crewHitPercent':13.5,'dilithiumCost':dil,'metalCost':metal,'officerCost':off,'buildTime':time,'maxSpecialEnergy':1500,'specialEnergyRate':10,'hotkeyLabel':json.dumps('HOTKEY_F10' if crew==200 else 'HOTKEY_F11')}
 if crew==500:vals.update({'classLabel':'"shipyard"','builder_ship':1,'buildItem0':'"xbrepair"','buildHardpoint':'"build"','repairHardpoint':'"repair"','repairFacility':1,'decommissionFacility':1,'animation':0,'repairAnimation':0})
 put(Path('odf/stations')/(unit+'.odf'),override(t,vals))
t=(R/'odf/ships/fsrepair.odf').read_text(encoding='latin1');t=re.sub(r'possibleCraftNames\s*=.*?(?=//\*+)', 'possibleCraftNames = "Repair Drone"\n\n',t,flags=re.S)
put(Path('odf/ships/xbrepair.odf'),override(t,{'unitName':'"Borg Repair Drone"','tooltip':'"Borg Repair Drone"','verboseTooltip':'"Assimilated Olympic repair vessel. Repairs allied ships."','race':'"borg"','baseName':'"xbrepair"','metalCost':75,'maximumCrew':50,'buildTime':18,'hotkeyLabel':'"HOTKEY_F1"','weapon3':'"gtwarpd"','weaponHardpoints3':'"hp16"'}))
for src,dst,label in [('gborgbor','xbharvbeam','Harvest Crew'),('gholdbm','xbassimbeam','Assimilate Target')]:
 t=(R/'odf/special_weapons'/(src+'.odf')).read_text(encoding='latin1')
 put(Path('odf/special_weapons')/(dst+'.odf'),override(t,{'wpnName':json.dumps(label),'tooltip':json.dumps(label),'verboseTooltip':json.dumps(label+' - native Borg beam mechanics.'),'buttonSlot':3,'popupSlot':4,'hotkeyLabel':'"HOTKEY_F4"'}))
for name in ['uconst','xbuconst']:
 t=(R/'odf/ships'/(name+'.odf')).read_text(encoding='latin1')
 assert not re.search(r'buildItem(?:9|10)\s*=',t,re.I)
 put(Path('odf/ships')/(name+'.odf'),t+'\nbuildItem9 = "xbharvest"\nbuildItem10 = "xbassimst"\n')
for p in (R/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');add=[]
 for unit,parent in [('xbharvest','bturret'),('xbassimst','bturret2')]:
  match=re.search(r'^'+parent+r'\.odf\s+([^\r\n]*)',t,re.M|re.I)
  if match:add.append(unit+'.odf '+match.group(1))
 if add:
  free=all(re.match(r'\w+\.odf\s+0(?:\s|$)',x) for x in add)
  add+=['xbrepair.odf '+('0' if free else '1 xbassimst.odf'),'xbharvbeam.odf 0','xbassimbeam.odf 0'];put(Path('techtree')/p.name,t+'\n// Borg assimilation support\n'+'\n'.join(add)+'\n')
notes='Created with builtin imagegen. Edited native brecx atlas into cyan harvesting conduits; edited native brecy atlas retaining grey panels and adding green machinery; edited native Olympic atlas preserving hull islands, adding dark Borg implants and green lights. Unique 256px RGB TGA copies; original atlases unchanged. Native SOD geometry and rig retained, with stationary yard launch/repair anchors added. Runtime verification pending.\n'
(A/'generation-notes.txt').write_text(notes)
status=Path('D:/aramada/status.json');s=json.loads(status.read_text());s['current']='Staging Borg Harvester and Assimilation Stations; Assimilation Station produces Borg Repair Drone. Artwork and definitions prepared; icon and dependency checks in progress. Not installed.';s.setdefault('features',[]).append({'id':'borg-assimilation-support','title':'Borg assimilation support','steps':[{'label':'Artwork and definitions','done':True},{'label':'Icons and validation','done':False},{'label':'Install after game closes','done':False},{'label':'Gameplay test','done':False}]});status.write_text(json.dumps(s,indent=2))
print('Staged',len(list(O.rglob('*.*'))),'files')

