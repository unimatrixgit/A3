from pathlib import Path
import ast,re,json,hashlib,zipfile,struct,sys,contextlib,io
import numpy as np
from PIL import Image
repo=Path('D:/aramada');root=Path('D:/armadaIII');source=Path('D:/Xaramada-Modwork/unimatrix-hero-20261101')
stage=repo/'patches/unimatrix-hero-20261101';out=stage/'overlay';stage.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
for n in ast.parse((repo/'scripts/stage-armadafiles-yards-20261031.py').read_text()).body:
 if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in ['IO','load','matrix','world_nodes','bounds']:exec(compile(ast.Module(body=[n],type_ignores=[]),'h','exec'))
exec((repo/'scripts/twin-yard-render.py').read_text())
idx={p.stem.lower():p for p in(root/'odf').rglob('*')if p.suffix.lower()=='.odf'};cache={};pending={}
def effective(n):
 if n in cache:return cache[n].copy()
 t=idx[n].read_text(encoding='latin1');d={}
 for p in re.findall(r'(?im)^\s*#include\s+"([^"]+)"',t):d.update(effective(Path(p).stem.lower()))
 for k,v in re.findall(r'(?im)^\s*(\w+)\s*=\s*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 cache[n]=d;return d.copy()
def put(t,k,v):
 pat=r'(?im)^'+re.escape(k)+r'\s*=.*$'
 return re.sub(pat,lambda _:k+' = '+str(v),t)if re.search(pat,t)else t+'\r\n'+k+' = '+str(v)+'\r\n'
def save(rel,b):pending[rel]=b if isinstance(b,bytes)else b.encode('latin1')
def number(v):return float(v.rstrip('fF;'))

# Preserve the downloaded model binary; force the Borg appearance under Federation ownership.
z=zipfile.ZipFile(source/'borg-intrepid.download');raw=z.read('Bintrepid.SOD');token=struct.pack('<H',len('fcruise3'))+b'fcruise3';assert token in raw
texture=(root/'Textures/RGB/Fcruise3_B.tga').read_bytes();alias='xu26hull';raw=raw.replace(token,struct.pack('<H',len(alias))+alias.encode())
save('SOD/xu26unimatrix.sod',raw);save('Textures/RGB/'+alias+'.tga',texture);save('Textures/RGB/'+alias+'_B.tga',texture)
p=out/'SOD/xu26unimatrix.sod';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);model=load(p);hp=sorted(n['id']for n in model.nodes if re.fullmatch(r'hp\d+',n['id'],re.I));assert len(hp)>=14
texidx={p.stem.lower():p for p in(root/'Textures/RGB').glob('*')if p.suffix.lower()=='.tga'};tp=out/'Textures/RGB'/ (alias+'.tga');tp.parent.mkdir(parents=True,exist_ok=True);tp.write_bytes(texture);texidx[alias]=tp;texturecache={}
im=preview(model,320);im.save(stage/'preview.png')
for pre in ['gb','wf']:
 b=io.BytesIO();im.resize((64,64),Image.Resampling.LANCZOS).save(b,format='TGA');save('Textures/RGB/'+pre+'xu26unimatrix.tga',b.getvalue())
credit=repo/'docs/third-party/unimatrix-hero-20261101';credit.mkdir(parents=True,exist_ok=True);(credit/'intrepid readme.txt').write_bytes(z.read('intrepid readme.txt'))

# Isolated weapon/ordinance copies carry the +50% damage without changing existing ships.
banks=[];damage=[]
for tag,weapon in [('beam','fintrepidphas'),('torp','ftype6'),('transphasic','xhtphase')]:
 d=effective(weapon);ordname=Path(d['ordname']).stem.lower();od=effective(ordname);new='xu26'+tag;neword=new+'o'
 t=idx[weapon].read_text(encoding='latin1');t=put(t,'ordName','"'+neword+'"')
 if 'range'in d:t=put(t,'range',f'{number(d["range"])*1.5:.12g}')
 rel=idx[weapon].relative_to(root).parent/(new+'.odf');save(rel.as_posix(),t)
 t=idx[ordname].read_text(encoding='latin1')
 for k in ['damageBase','damageVariance']:
  if k.lower()in od:t=put(t,k,f'{number(od[k.lower()])*1.5:.12g}')
 save((idx[ordname].relative_to(root).parent/(neword+'.odf')).as_posix(),t)
 banks.extend([new]*({'beam':6,'torp':2,'transphasic':1}[tag]));damage.append({'weapon':new,'baseDamage':number(od.get('damagebase','0')),'newDamage':number(od.get('damagebase','0'))*1.5})

# Voyager hero baseline, not a mass-production Intrepid baseline.
hero=effective('fvoyager');t=idx['fvoyager'].read_text(encoding='latin1')
t=re.sub(r'(?im)^(?:weapon(?:Hardpoints)?\d+|buildItem\d+)\s*=.*$','',t)
values={'unitName':'"Unimatrix Class"','label':'"USS Unimatrix NX-1999"','possibleCraftNames':'"USS Unimatrix NX-1999"',
 'tooltip':'"Hero Ship - USS Unimatrix NX-1999"','baseName':'"xu26unimatrix"','race':'"federation"','isHero':1,
 'verboseTooltip':'"USS Unimatrix NX-1999\\nBorg-enhanced Voyager hero; six beams, two photons and one transphasic launcher\\nAblative battle armour, transwarp, Delta Flyer and Puddle Jumper hangars."'}
stats={}
for k in ['maxHealth','shieldRate','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','shieldGeneratorHitPoints','sensorsHitPoints','rangeScan','damagedScan','maxSpecialEnergy','specialEnergyRate']:
 if k.lower()in hero:
  before=number(hero[k.lower()]);after=before*1.5
  if k.lower().endswith('hitpoints'):after=int(after+.5)
  values[k]=f'{after:.12g}';stats[k]={'baseline':before,'new':after}
for k in ['enginesRepairTime','weaponsRepairTime','lifeSupportRepairTime','shieldGeneratorRepairTime','sensorsRepairTime']:
 if k.lower()in hero:values[k]=f'{number(hero[k.lower()])/1.5:.12g}'
values['maximumCrew']=int(number(hero.get('crewcost','220'))*1.5);values['crewCost']=hero['crewcost']
for key in ['engines','lifeSupport','weapons','shieldGenerator','sensors','hull','critical']:values[key+'TargetHardpoints']=' '.join('"'+p+'"'for p in hp[:6])
physname=Path(hero['physicsfile']).stem.lower();phys=idx[physname].read_text(encoding='latin1');pd=effective(physname)
for k in ['combatSpeed','impulseSpeed','warpSpeed','forwardAccel','turnOmega','turnAlpha','pitchOmega','pitchAlpha']:
 if k.lower()in pd:
  before=number(pd[k.lower()]);phys=put(phys,k,f'{before*1.5:.12g}');stats[k]={'baseline':before,'new':before*1.5}
save('odf/other/xu26phys.odf',phys);values['physicsFile']='"xu26phys.odf"';values['trekPhysicsFile']='"xu26phys.odf"'
lo,hi=bounds(model);oldmodel=load(root/'SOD/fvoyager.SOD');ol,oh=bounds(oldmodel);values['ScaleSOD']=f'{number(hero.get("scalesod","1"))*max(oh-ol)/max(hi-lo):.12g}'
for i,name in enumerate(banks+['xu26armour','xu26transwarp'],1):values['weapon'+str(i)]='"'+name+'"';values['weaponHardpoints'+str(i)]='"'+hp[i-1]+'"'
for k,v in {'classLabel':'"shipyard"','aiName':'"CraftProcess"','ship':1,'facility':0,'is_starbase':0,'builder_ship':1,
 'buildItem0':'"fdeltaflyer"','buildItem1':'"xu26jumper"','buildHardpoint':'"'+hp[-1]+'"','alwaysRecomputeRallyPoint':1,
 'repairFacility':0,'decommissionFacility':0,'recrewRate':0,'maxCrewGain':0,'officerGain':0,'maximumUpgrades':0}.items():values[k]=v
for k,v in values.items():t=put(t,k,v)
save('odf/ships/xu26unimatrix.odf',t)

armour=idx['garmour'].read_text(encoding='latin1')
for k,v in {'wpnName':'"Voyager Battle Armour"','tooltip':'"Voyager Battle Armour"','verboseTooltip':'"Deploy Voyager ablative battle armour using the existing armour effect. Consumes special energy."',
 'buttonSlot':1,'popupSlot':1,'hotkeyLabel':'"HOTKEY_F1"'}.items():armour=put(armour,k,v)
save('odf/special_weapons/xu26armour.odf',armour)
warp=idx['gtwarpd'].read_text(encoding='latin1')
for k,v in {'wpnName':'"Unimatrix Transwarp"','tooltip':'"Unimatrix Transwarp"','verboseTooltip':'"Open a transwarp passage to the selected destination. Requires the Federation transwarp research facility."',
 'buttonSlot':2,'popupSlot':2,'hotkeyLabel':'"HOTKEY_F2"'}.items():warp=put(warp,k,v)
save('odf/special_weapons/xu26transwarp.odf',warp)

# A carrier-owned Jumper clone avoids requiring Atlantis to produce this hero's shuttle.
jt=idx['sg26jumper'].read_text(encoding='latin1');jt=put(jt,'tooltip','"Unimatrix Puddle Jumper"');save('odf/ships/xu26jumper.odf',jt)
yard=idx['fyard2'].read_text(encoding='latin1');assert not re.search(r'(?im)^buildItem13\s*=',yard);save('odf/stations/fyard2.odf',yard+'\r\nbuildItem13 = "xu26unimatrix"\r\n')
sprite=(root/'Sprites/gui_global.spr').read_bytes();tail='\r\n@reference=64\r\n@tmaterial=default\r\nb_xu26unimatrix gbxu26unimatrix 0 0 64 64\r\n'
for i in range(1,6):tail+='xu26unimatrixw'+str(i)+' wfxu26unimatrix 0 0 64 64\r\n'
tail+='b_xu26armour gbremod00 0 0 64 64\r\nb_xu26transwarp gbtwarpd00 0 0 64 64\r\nb_xu26jumper gbsg26jumper 0 0 64 64\r\n'
for i in range(1,6):tail+='xu26jumperw'+str(i)+' wfsg26jumper 0 0 64 64\r\n'
save('Sprites/gui_global.spr',sprite+tail.encode('latin1'))
for p in(root/'Techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');full=p.name.lower()=='fulltech.tt'
 for name,deps in [('xu26unimatrix',['fyard2','fresear2','fupgrade']),('xu26jumper',['xu26unimatrix']),('xu26armour',[]),('xu26transwarp',['fjupiter'])]:
  assert not re.search(r'(?im)^'+name+r'\.odf\s',t);r=[]if full else deps;t+='\r\n'+name+'.odf '+str(len(r))+(' '+' '.join(x+'.odf'for x in r)if r else'')+'\r\n'
 save('Techtree/'+p.name,t)
files=[]
for rel,data in pending.items():
 p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);live=root/rel;files.append({'path':rel,'previousSha256':hashlib.sha256(live.read_bytes()).hexdigest()if live.exists()else None,'sha256':hashlib.sha256(data).hexdigest()})
report={'installed':False,'runtimeVerified':False,'target':'D:/armadaIII','name':'USS Unimatrix NX-1999','class':'Unimatrix Class','heroBaseline':'fvoyager','strengthMultiplier':1.5,'stats':stats,
 'weapons':banks+['xu26armour','xu26transwarp'],'damageChanges':damage,'yard':'fyard2','yardSlot':13,'production':['fdeltaflyer','xu26jumper'],
 'crew':'Starting staffing/cost remains220; capacity330. Other resource costs and build time retain Voyager hero baseline.',
 'source':'http://armadafiles.com/files/armada-2/ships/federation/tng-ds9-voy-and-future/assimilated-intrepid-class/details',
 'artwork':'Downloaded Assimilated Intrepid model, existing Borg Fcruise3_B hull map forced as normal texture; Federation ownership retained; no starting hero added.',
 'specialEnergy':'Voyager hero +50%:1500 capacity,22.5/sec regeneration; transwarp costs1000, armour retains existing20 cost.',
 'research':'Native Federation transwarp facility requirement; armour follows existing ungated armour ability; unit requires advanced yard/research/upgrade facilities.',
 'files':files}
(stage/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('PREPARED',len(files),'files; live files untouched')
