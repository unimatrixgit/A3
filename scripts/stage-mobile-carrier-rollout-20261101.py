"""Prepare only: native mobile yards, Delta Flyers, and Ancient city fleet."""
from pathlib import Path
import ast, re, json, hashlib, zipfile, struct, sys, contextlib, io
import numpy as np
from PIL import Image

repo=Path('D:/aramada'); root=Path('D:/armadaIII')
source=Path('D:/Xaramada-Modwork/carrier-research-20261101')
stage=repo/'patches/mobile-carrier-rollout-20261101'; out=stage/'overlay'
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
for n in ast.parse((repo/'scripts/stage-armadafiles-yards-20261031.py').read_text()).body:
 if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['IO','load','matrix','world_nodes','bounds']:
  exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
exec((repo/'scripts/twin-yard-render.py').read_text())
idx={p.stem.lower():p for p in (root/'odf').rglob('*') if p.suffix.lower()=='.odf'}
sods={p.stem.lower():p for p in (root/'SOD').glob('*')}
texidx={p.stem.lower():p for p in (root/'Textures/RGB').glob('*') if p.suffix.lower()=='.tga'}
texturecache={}; cache={}; pending={}; models={}; credits=[]; changes=[]
def effective(n):
 if n in cache:return cache[n].copy()
 t=idx[n].read_text(encoding='latin1'); d={}
 for parent in re.findall(r'(?im)^\s*#include\s+"([^"]+)"',t):d.update(effective(Path(parent).stem.lower()))
 for k,v in re.findall(r'(?im)^\s*(\w+)\s*=\s*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 cache[n]=d;return d.copy()
def save(rel,data):pending[rel]=data if isinstance(data,bytes) else data.encode('latin1')
def get(rel):return pending.get(rel,(root/rel).read_bytes()).decode('latin1')
def put(t,k,v):
 pat=r'(?im)^'+re.escape(k)+r'\s*=.*$'
 return re.sub(pat,lambda m:k+' = '+str(v),t) if re.search(pat,t) else t+'\r\n'+k+' = '+str(v)+'\r\n'
def props(t,d):
 for k,v in d.items():t=put(t,k,v)
 return t
def hps(model):return [n['id'] for n in model.nodes if re.fullmatch(r'hp\d+',n['id'],re.I)]
def launch(model):
 w,_=world_nodes(model); candidates=[n for n in model.nodes if n['id'] in hps(model)]
 assert candidates
 return min(candidates,key=lambda n:w[id(n)][2,3])['id']
def mobile(t,craft,model):
 d={'classLabel':'"shipyard"','aiName':'"CraftProcess"','ship':1,'facility':0,'is_starbase':0,
 'builder_ship':1,'alwaysRecomputeRallyPoint':1,'buildItem0':'"'+craft+'"','buildHardpoint':'"'+launch(model)+'"',
 'repairFacility':0,'decommissionFacility':0,'recrewRate':0,'maxCrewGain':0,'officerGain':0,'maximumUpgrades':0}
 return props(t,d)
def import_model(pack,unit,target_span):
 z=zipfile.ZipFile(source/(pack+'.download'))
 entries={Path(n.replace('\\','/')).stem.lower():n for n in z.namelist() if n.lower().endswith('.tga')}
 sn=next(n for n in z.namelist() if n.lower().endswith('.sod'));raw=z.read(sn)
 tmp=source/(pack+'.sod');tmp.write_bytes(raw);m=load(tmp)
 texture_names=set()
 for node in m.nodes:
  if node['type']!='MESH':continue
  d=node['data']; texture_names.add(d['texture'])
  borg=d.get('borgification')
  if isinstance(borg,dict) and borg.get('texture'):texture_names.add(borg['texture'])
 for name in texture_names:
  if not name:continue
  token=struct.pack('<H',len(name))+name.encode('latin1')
  if token not in raw:continue  # Reader synthesizes implicit _B texture references.
  if name.lower() in entries:b=z.read(entries[name.lower()])
  elif name.lower().endswith('_b') and name[:-2].lower() in entries:
   # Pack references absent assimilation maps: retain its original hull texture.
   b=z.read(entries[name[:-2].lower()])
  else:
   assert name.lower() in texidx,(pack,name)
   b=texidx[name.lower()].read_bytes()
  alias='sg26t'+hashlib.sha256(b).hexdigest()[:12]
  raw=raw.replace(token,struct.pack('<H',len(alias))+alias.encode())
  rel='Textures/RGB/'+alias+'.tga';save(rel,b);p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);texidx[alias.lower()]=p
  save('Textures/RGB/'+alias+'_B.tga',b)
 save('SOD/'+unit+'.sod',raw);p=out/'SOD'/(unit+'.sod');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 model=load(p);assert len(m.nodes)==len(model.nodes);lo,hi=bounds(model)
 models[unit]=model
 for n in z.namelist():
  if n.lower().endswith('.txt'):
   rel='docs/third-party/mobile-carriers-20261101/'+pack+'/'+Path(n).name
   p=repo/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n));credits.append(rel)
 return model,target_span/max(hi-lo)
sprite=(root/'Sprites/gui_global.spr').read_bytes(); extra='\r\n// Mobile carrier rollout: isolated new unit icons\r\n'
def icons(unit,model):
 global extra
 im=preview(model,128).resize((64,64),Image.Resampling.LANCZOS)
 for prefix in ['gb','wf']:
  b=io.BytesIO();im.save(b,format='TGA');save('Textures/RGB/'+prefix+unit+'.tga',b.getvalue())
 extra+='@reference=64\r\n@tmaterial=default\r\nb_'+unit+' gb'+unit+' 0 0 64 64\r\n'
 for i in range(1,6):extra+=unit+'w'+str(i)+' wf'+unit+' 0 0 64 64\r\n'

# Existing ships keep their combat banks, statistics, voices and research.
for unit,child,why in [
 ('fvoyager','fdeltaflyer','Voyager / Delta Flyer'),('fcruise3','fdeltaflyer','Intrepid hangar refit'),
 ('fintx','fdeltaflyer','Intrepid X-refit hangar'),('mrc018','fdeltaflyer','Mirror Voyager hangar'),
 ('kbattle','kscout','Negh Var hangar refit; gameplay extrapolation inspired by Klingon carrier roles'),
 ('chutet','cscout','Hutet hangar refit; gameplay extrapolation'),
 ('bspecial','bscout','Diamond scout deployment; gameplay extrapolation'),
 ('bjbattle','bjinterceptor','Bajoran battleship interceptor hangar; gameplay extrapolation')]:
 d=effective(unit);assert not any(k.startswith('builditem') for k in d),unit
 model=load(sods[d.get('basename',unit).lower()]);rel='odf/ships/'+unit+'.odf';t=get(rel)
 t=mobile(t,child,model)
 t=put(t,'verboseTooltip','"'+d.get('verbosetooltip',d.get('unitname',unit))+'\\nHangar: build '+effective(child).get('unitname',child)+'. Existing research requirements apply."')
 save(rel,t);changes.append({'unit':unit,'builds':[child],'role':why,'newModel':False})

# Downloaded native models are kept intact except for counted texture strings.
atlantis,ats=import_model('atlantis-20','sg26atlantis',500)
jumper,js=import_model('jumper','sg26jumper',45)
aurora,aus=import_model('aurora','sg26aurora',220)
kryonyx,rs=import_model('kryonyx','xr26carrier',260)

# Use the pack's yellow Ancient drone ordinance and sound, not stock phaser art.
z=zipfile.ZipFile(source/'atlantis-20.download')
base=z.read('drone2.odf').decode('latin1');ordbase=z.read('drone3.odf').decode('latin1')
sound=z.read('drone.wav');save('sounds/effects/sg26drone.wav',sound)
for tag,damage,delay,reach in [('jumper',10,.6,400),('aurora',35,.6,700),('city',40,.5,900)]:
 w='sg26drone_'+tag;o=w+'o'
 t=props(base,{'ordName':'"'+o+'"','wpnName':'"Ancient Drones"','shotDelay':delay,'range':reach,'restrictFireArc':0,'fireSound':'"sg26drone.wav"','hitChance':1})
 save('odf/weapons/Pulse/'+w+'.odf',t)
 t=props(ordbase,{'damageBase':damage,'damageVariance':0,'specialEnergyCost':0,'shotSpeed':450,'lifeSpan':4,'Length':10,'Radius':2.5})
 save('odf/weapons/Pulse/'+o+'.odf',t)

def newcraft(unit,model,scale,title,health,crew,dil,metal,officers,seconds,tag,banks):
 hp=hps(model);assert len(hp)>=banks
 t='#include "craft.odf"\r\n'
 t=props(t,{'unitName':'"'+title+'"','label':'"'+title+'"','tooltip':'"'+title+'"',
 'verboseTooltip':'"'+title+'\\nAncient drone weapons\\nBuilt at Atlantis."','baseName':'"'+unit+'"','race':'"federation"',
 'maxHealth':health,'shieldRate':health/100,'crewCost':crew,'officerCost':officers,'dilithiumCost':dil,'metalCost':metal,'buildTime':seconds,
 'ScaleSOD':scale,'physicsFile':'"fbattlephys.odf"','trekPhysicsFile':'"fbattlephys.odf"','maxSpecialEnergy':1000,'specialEnergyRate':10,
 'combat':1,'alert':1,'can_sandd':1,'shipType':'"B"','shipclass':'"battleship"'})
 for system in ['engines','weapons','sensors','lifeSupport','shieldGenerator']:
  t=props(t,{system+'HitPoints':max(100,int(health*.1)),system+'TargetHardpoints':' '.join('"'+p+'"' for p in hp[:4])})
 for i in range(1,banks+1):t=props(t,{'weapon'+str(i):'"sg26drone_'+tag+'"','weaponHardpoints'+str(i):'"'+hp[i-1]+'"'})
 save('odf/ships/'+unit+'.odf',t);icons(unit,model);return t
newcraft('sg26jumper',jumper,js,'Puddle Jumper',650,8,120,40,1,15,'jumper',2)
newcraft('sg26aurora',aurora,aus,'Aurora-class Alteran Battleship',6000,800,1800,800,8,70,'aurora',4)
t=newcraft('sg26atlantis',atlantis,ats,'Atlantis',12000,1200,5000,5000,20,120,'city',6)
t=mobile(t,'sg26jumper',atlantis);t=props(t,{'buildItem1':'"sg26aurora"','verboseTooltip':'"Atlantis\\nAncient city-ship and drone fortress\\nProduces Puddle Jumpers and Aurora-class Alteran battleships."'})
t=props(t,{'weapon7':'"sg26wormhole"','weaponHardpoints7':'"'+hps(atlantis)[0]+'"',
 'weapon8':'"sg26zpm"','weaponHardpoints8':'"'+hps(atlantis)[0]+'"',
 'weapon9':'"sg26cloak"','weaponHardpoints9':'"'+hps(atlantis)[0]+'"',
 'weapon10':'"sg26overdrive"','weaponHardpoints10':'"'+hps(atlantis)[0]+'"',
 'maxSpecialEnergy':4000,'specialEnergyRate':40,
 'verboseTooltip':'"Atlantis\\nDrones, Wormhole Drive, ZPM Improvement, cloak and Naquadaq Overdrive\\nProduces Puddle Jumpers and Aurora-class Alteran battleships."'})
save('odf/ships/sg26atlantis.odf',t)
drive=props((root/'odf/special_weapons/gtwarpd.odf').read_text(encoding='latin1'),
 {'wpnName':'"Wormhole Drive"','tooltip':'"Wormhole Drive"',
 'verboseTooltip':'"Wormhole Drive\\nOpen a subspace corridor to the selected location.\\nUses1000 special energy; replenishes in25 seconds when no other abilities consume energy."',
 'buttonSlot':1,'popupSlot':1,'hotkeyLabel':'"HOTKEY_F1"'})
save('odf/special_weapons/sg26wormhole.odf',drive)
extra+='@reference=64\r\n@tmaterial=default\r\nb_sg26wormhole gbtwarpd00 0 0 64 64\r\n'
zpm=props((root/'odf/special_weapons/gcorbom.odf').read_text(encoding='latin1'),
 {'wpnName':'"ZPM Improvement"','tooltip':'"ZPM Improvement"',
 'verboseTooltip':'"ZPM Improvement\\nAncient shield reinforcement reflects hostile fire using Sovereign Corbomite mechanics.\\nAvailable without research; uses special energy."',
 'buttonSlot':2,'popupSlot':2,'hotkeyLabel':'"HOTKEY_F2"'})
save('odf/special_weapons/sg26zpm.odf',zpm)
cloak='#include "grcloak.odf"\r\n'
cloak=props(cloak,{'wpnName':'"Atlantis Cloak"','tooltip':'"Atlantis Cloak"',
 'verboseTooltip':'"Atlantis Cloak\\nConceal the city using the standard cloaking device.\\nConsumes100 special energy when activated."',
 'buttonSlot':3,'popupSlot':3,'hotkeyLabel':'"HOTKEY_F3"'})
save('odf/special_weapons/sg26cloak.odf',cloak)
extra+='@reference=64\r\n@tmaterial=default\r\nb_sg26zpm gbcorbom00 0 0 64 64\r\nb_sg26cloak gbcloak00 0 0 64 64\r\n'
over=props((root/'odf/special_weapons/gdchant.odf').read_text(encoding='latin1'),
 {'ordName':'"sg26overdriveo"','wpnName':'"Naquadaq Overdrive"','tooltip':'"Naquadaq Overdrive"',
 'verboseTooltip':'"Naquadaq Overdrive\\nRestore original700 damage per Ancient drone for15 seconds.\\nUses1000 special energy;60-second firing cooldown. No research required."',
 'range':1,'shotDelay':60,'buttonSlot':4,'popupSlot':4,'hotkeyLabel':'"HOTKEY_F4"'})
over=re.sub(r'(?im)^assimilatable\s*=.*$','',over)
save('odf/special_weapons/sg26overdrive.odf',over)
overord=props((root/'odf/special_weapons/dchant.odf').read_text(encoding='latin1'),
 {'specialValue':15,'specialEnergyCost':1000,'FireModifier':1,'RepairModifier':1,'TurnModifier':1,
 'DamageModifier':17.5,'SpeedModifier':1,'HitModifier':1,'damageBase':0,'lifeSpan':0})
save('odf/special_weapons/sg26overdriveo.odf',overord)
extra+='@reference=64\r\n@tmaterial=default\r\nb_sg26overdrive gbwenhance00 0 0 64 64\r\n'

# Romulan downloaded carrier: match native warbird stats and preserve research specials.
d=effective('rbattle');t=idx['rbattle'].read_text(encoding='latin1');hp=hps(kryonyx)
t=props(t,{'baseName':'"xr26carrier"','ScaleSOD':rs,'unitName':'"Kryonyx-class Carrier"','tooltip':'"Kryonyx-class Carrier"','verboseTooltip':'"Kryonyx-class Carrier\\nRomulan scout hangar\\nDownloaded design by Bryan; native mobile production."'})
for key in re.findall(r'(?im)^(\w*TargetHardpoints)\s*=',t):t=put(t,key,' '.join('"'+p+'"' for p in hp[:4]))
t=re.sub(r'(?im)^(weaponHardpoints)(\d+)\s*=.*$',lambda m:m[1]+m[2]+' = "'+hp[(int(m[2])-1)%len(hp)]+'"',t)
t=mobile(t,'rscout',kryonyx);save('odf/ships/xr26carrier.odf',t);icons('xr26carrier',kryonyx)
t=get('odf/stations/ryard3.odf');assert not re.search(r'(?im)^buildItem12\s*=',t);t+='\r\nbuildItem12 = "xr26carrier"\r\n';save('odf/stations/ryard3.odf',t)

# Keep constructor menus within the existing fourteen-entry limit.
t=get('odf/ships/xfuconst.odf');assert re.search(r'(?im)^buildItem12\s*=\s*"fmidas"',t)
t=put(t,'buildItem12','"sg26atlantis"');save('odf/ships/xfuconst.odf',t)
t=get('odf/ships/fconst2.odf');assert not re.search(r'(?im)^buildItem12\s*=',t);t+='\r\nbuildItem12 = "fmidas"\r\n';save('odf/ships/fconst2.odf',t)

# Technology: no starting fleets, broad research generation or utility gates.
for p in (root/'Techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');full=p.name.lower()=='fulltech.tt'
 for unit,req in [('sg26atlantis',['fbase2','fresear2','fupgrade']),('sg26jumper',['sg26atlantis']),('sg26aurora',['sg26atlantis']),('sg26wormhole',[]),('sg26zpm',[]),('sg26cloak',[]),('sg26overdrive',[]),('xr26carrier',['ryard3','rresear2'])]:
  assert not re.search(r'(?im)^'+unit+r'\.odf\s',t)
  needs=[] if full else req;t+='\r\n'+unit+'.odf '+str(len(needs))+(' '+' '.join(n+'.odf' for n in needs) if needs else '')+'\r\n'
 save('Techtree/'+p.name,t)
save('Sprites/gui_global.spr',sprite+extra.encode('latin1'))
assert pending['Sprites/gui_global.spr'].startswith(sprite)
files=[]
for rel,data in pending.items():
 p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);live=root/rel
 files.append({'path':rel,'previousSha256':hashlib.sha256(live.read_bytes()).hexdigest() if live.exists() else None,'sha256':hashlib.sha256(data).hexdigest()})
manifest={'target':str(root),'installed':False,'runtimeVerified':False,'dependency':'Dominion carrier move/build/combat test must pass first',
 'existingShipConversions':changes,'newUnits':['sg26atlantis','sg26jumper','sg26aurora','xr26carrier'],
 'excludedFactions':['breen','ferengi'],'species8472':'Existing native mobile mothership retained, no extra ship',
 'constructorMove':'Midas moves from MKIII slot12 to MKII slot12; Atlantis uses MKIII slot12. No removed build access or menu overflow.',
 'sourceCredits':credits,'files':files,'wormholeDrive':'Native transwarp named Wormhole Drive;1000 energy/jump,4000 capacity,40 regeneration/sec;25 seconds per jump replenishment without other consumption',
 'citySpecials':{'ZPM Improvement':'Sovereign Corbomite Reflector, unchanged80 energy cost, no research','Cloak':'Native cloak,100 energy cost',
 'Naquadaq Overdrive':'DeathChant TimedHyper effect:15 seconds, DamageModifier17.5 restores40 base damage to original700; all other modifiers1; self-range1;1000 energy;60-second cooldown. Runtime self-target/timing test required.',
 'nativeDamageEvidence':'Ordnance::mApplyDamage0x58f3c0 resolves shooter at+0x5c, gets TimedHyper via0x4d4ea0, multiplies outgoing damage by+0xc0 at0x58f3f7. DeathChant maps DamageModifier to+0xc0 and specialValue to duration.',
 'energyBudget':'4 special abilities *1000 capacity and *10/sec recharge =4000/40; combined listed activation costs2180; full recharge100 seconds','buttons':'Wormhole1, ZPM2, Cloak3, Overdrive4; reused icons, no overlap','research':'All four zero prerequisites, no research/resource unlock cost; special energy retained'},
 'droneBalance':{'jumper':'2 banks,10 damage/.6sec,400 range','aurora':'4 banks,35 damage/.6sec,700 range','atlantis':'6 banks,40 damage/.5sec,900 range'}}
(stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PREPARED',len(files),'files; live game files untouched')
