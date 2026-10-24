from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import shutil,subprocess
props=json.loads((repo/'reports/ferengi-current-properties.json').read_text())
stage=Path('D:/Xaramada-Modwork/ferengi-final-stage');stage.mkdir(parents=True,exist_ok=True)
backup=Path('D:/Xaramada-Modwork/backups')/('ferengi-final-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
pending={};binary={};records=[];abilityids=[];sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
source=Path('D:/Xaramada-Modwork/ferengi-expansion/scavengers/Ferengi Scavengers');alltex={p.stem.lower():p for p in source.parent.rglob('*')if p.suffix.lower()=='.tga'}
def q(x):return '"'+str(x)+'"'
def update(t,values):
 for k,v in values.items():t=put(t,k,v)
 return t

def get(n):return Path(props[n.lower()]['file']).read_text(encoding='latin1')
def imgbytes(im):
 b=io.BytesIO();im.save(b,format='TGA');return b.getvalue()
def stripbanks(t):return re.sub(r'(?mi)^\s*weapon(?:Hardpoints)?\d+\s*=[^\r\n]*','',t)
def icon(n,m,trade=False):
 global sprite
 visible=copy.deepcopy(m);nodes={z['id'].lower():z for z in visible.nodes}
 def hidden(z):
  seen=set()
  while z and z['id'].lower()not in seen:
   key=z['id'].lower();seen.add(key)
   if key in ['borg','damage','shields','shield']:return True
   z=nodes.get(z['parent'].lower())
  return False
 visible.nodes[:]=[z for z in visible.nodes if z['type']!='MESH' or not hidden(z)]
 im=preview(visible,320)
 if trade:
  d=ImageDraw.Draw(im);d.rounded_rectangle((183,8,310,113),12,fill=(12,15,20),outline=(245,195,65),width=5)
  d.line((197,37,291,37),fill=(245,195,65),width=9);d.polygon([(291,37),(272,22),(272,52)],fill=(245,195,65))
  d.line((291,79,197,79),fill=(245,195,65),width=9);d.polygon([(197,79),(216,64),(216,94)],fill=(245,195,65))
  d.rectangle((0,262,319,319),fill=(8,12,18));font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',42);d.text((86,263),'TRADE',font=font,fill=(245,195,65))
 binary['Textures/RGB/gb'+n+'.tga']=imgbytes(im.resize((64,64),Image.Resampling.LANCZOS));binary['Textures/RGB/wf'+n+'.tga']=imgbytes(im.resize((256,256),Image.Resampling.LANCZOS))
 for key in ['b_'+n]+[n+'w'+str(i)for i in range(1,6)]:sprite=re.sub(r'(?mi)^'+key+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' gb'+n+' 0 0 64 64\n@reference=256\n'
 for i in range(1,6):sprite+=n+'w'+str(i)+' wf'+n+' 0 0 256 256\n'

def model(n,src):
 m=load(src)
 for z in m.nodes:
  if z['type']!='MESH':continue
  d=z['data']
  for key in ['texture','borgification']:
   old=d.get(key)
   if not isinstance(old,str)or not old:continue
   tex=alltex.get(old.lower())or texidx.get(old.lower())or (alltex.get('zferengi')or texidx.get('zferengi')if old.lower()=='zeemax'else None);assert tex,('texture',old)
   alias='xfg'+hashlib.sha256(tex.read_bytes()).hexdigest()[:9];binary['Textures/RGB/'+alias+'.tga']=tex.read_bytes();d[key]=alias;texidx[alias]=tex
 out=stage/'SOD'/(n+'.sod');out.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(out))
 binary['SOD/'+n+'.sod']=out.read_bytes();check=load(out);assert len(check.nodes)==len(m.nodes)
 return m

def normal(n,kind,damage,delay):
 directory='Phasers'if kind=='beam'else'Photons';src='cc04phas'if kind=='beam'else'fc1phot';ordsrc='cbphaso'if kind=='beam'else'fc1photo';hit=.75 if kind=='beam'else .65
 t=get(src);t=update(t,{'ordName':q(n+'o'),'wpnName':q('Ferengi Disruptor'if kind=='beam'else'Ferengi Photon Torpedo'),'damageBase':f'{damage:.8f}','hitChance':hit,'shotDelay':delay,'specialEnergyCost':0,'special':0,'range':550})
 o=update(get(ordsrc),{'damageBase':f'{damage:.8f}','damageVariance':0,'specialEnergyCost':0})
 pending['odf/weapons/'+directory+'/'+n+'.odf']=t;pending['odf/weapons/'+directory+'/'+n+'o.odf']=o
 return n

def ability(n,src,slot,name,cost,desc):
 global sprite
 t=update(get(src),{'wpnName':q(name),'tooltip':q(name),'verboseTooltip':q(desc),'buttonSlot':slot,'popupSlot':slot,'hotkeyLabel':q('HOTKEY_F'+str(slot)),'shotDelay':25,'specialEnergyCost':cost,'maxTargets':1})
 t=re.sub(r'(?mi)^\s*assimilatable\s*=[^\r\n]*','',t)
 op=props[src].get('ordname');
 if op:
  o=get(op);o=put(o,'specialEnergyCost',cost);pending['odf/special_weapons/'+n+'o.odf']=o;t=put(t,'ordName',q(n+'o'))
 pending['odf/special_weapons/'+n+'.odf']=t
 iconsrc='gpoleron'if src=='gpolerond'else src
 match=re.search(r'(?mi)^b_'+iconsrc+r'[ \t]+[^\r\n]+',sprite);assert match,iconsrc
 ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:match.start()])[-1]
 sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+','b_'+n,match[0])+'\n';abilityids.append(n)
 return n

powers={
'xfgquark':[ability('xfgqholo','gholoemt',1,'Quark\'s Holo-Emitter',700,'Projects deceptive holograms around enemy ships.'),ability('xfgqcloak','grcloak',2,'Quark\'s Cloaking Device',0,'Conceals the ship using a conventional cloaking device.')],
'xfgrom':[ability('xfgrregen','gregen',1,'Rom\'s Emergency Repairs',600,'Regenerates this ship.'),ability('xfgrshield','gshldemt',2,'Rom\'s Shield Service',600,'Restores allied shields in range.'),ability('xfgrenergy','gengyemt',3,'Rom\'s Energy Service',500,'Recharges allied special energy in range.')],
'xfgnagus':[ability('xfgnpol','gpolerond',1,'Systems Embargo',600,'Polaron torpedo randomly disables a target system.'),ability('xfgnshield','gshieldd',2,'Shield Seizure',600,'Temporarily disrupts enemy shields.'),ability('xfgnengine','gwcover',3,'Engine Embargo',600,'Temporarily disables enemy engines.'),ability('xfgncrew','gmicroorgs',4,'Life Support Sanctions',600,'Drains enemy crew. Systems Embargo can separately disable life support.')]}
# Bound the crew-draining control power; preserve its native ordnance class.
p='odf/special_weapons/xfgncrewo.odf';pending[p]=update(pending[p],{'DrainRate':10,'DrainTime':12})
# Cloak is a toggle, so preserve the native zero-delay toggle behavior.
p='odf/special_weapons/xfgqcloak.odf';pending[p]=put(pending[p],'shotDelay',0)
configs=[
('xfgfight','Bronta Fighter','fgscout',300,2,2,0,100,20,20,1,0,0,None),
('xfgfrig','Goront Frigate','fgfrigate',900,4,2,1,240,40,100,3,0,0,None),
('xfgdest','Eemax Destroyer','fgcruise3',1400,6,3,1,320,50,180,5,0,0,None),
('xfgcruis','Tokron Cruiser','fgspecial',2200,9,4,3,500,70,300,8,0,0,None),
('xfgbatt',"D'Kora Battleship",'fgbattle',3200,13,4,3,850,100,600,12,0,0,None),
('xfgquark',"Quark's Battleship",'fgbattle1',4500,18,6,4,1250,130,800,16,2400,24,351.26),
('xfgrom',"Rom's Cruiser",'fgspecial',3600,16,5,3,1100,115,450,12,2600,26,98.7),
('xfgnagus',"Grand Nagus's Frigate",'fgfrigate',3200,14,5,2,1000,110,350,10,2400,24,67.2)]
for slot,c in enumerate(configs,1):
 n,name,donor,hp,regen,nb,nt,lat,time,crew,off,energy,recharge,target=c
 m=model(n,next(p for p in(source/'Sod').iterdir()if p.stem.lower()==donor));hps=[z['id']for z in m.nodes if re.fullmatch(r'hp\d+',z['id'],re.I)];assert hps
 # Assign aggregate hero normal DPS, accounting for every added bank.
 bd,td=(35 if slot==1 else 70 if slot<5 else 100),100
 if target:
  scale=target/(nb*100/1.8*.75+nt*140/2.5*.65);bd=100*scale;td=140*scale
 beam=normal(n+'b','beam',bd,1.8);torp=normal(n+'t','torp',td,2.5)
 t='#include "cruise1.odf"\n';roles=['fighter','frigate','destroyer','cruiser','battleship','battleship','cruiser','frigate']
 vals={'unitName':q('Mercenary Ferengi '+name),'tooltip':q('Mercenary Ferengi '+name),'verboseTooltip':q('Latinum-funded Ferengi contract vessel. '+('Hero abilities are available without research.'if target else'Available from the Mercenary Ferengi Contract Yard.')),'baseName':q(n),'race':q('ferengi'),'classLabel':q('craft'),'aiName':q('CraftProcess'),'shipclass':q(roles[slot-1]),'isHero':int(target is not None),'maxHealth':hp,'shieldRate':regen,'shieldProtection':1,'maxSpecialEnergy':energy,'specialEnergyRate':recharge,'crewCost':crew,'maximumCrew':int(crew*1.25),'officerCost':off,'buildTime':time,'dilithiumCost':0,'metalCost':0,'latinumCost':lat,'biomatterCost':0,'ScaleSOD':1.3,'hotkeyLabel':q('HOTKEY_F'+str(slot)),'possibleCraftNames':q(name)if target else'"Profit Margin" "Golden Rule" "Risk Premium" "Liquid Assets" "Fair Acquisition"'}
 for k in ['shieldGeneratorHitPoints','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','sensorsHitPoints']:vals[k]=int(hp*.2)
 for k in ['engines','lifeSupport','weapons','shieldGenerator','sensors','hull','critical']:vals[k+'TargetHardpoints']=' '.join(q(h)for h in hps[:5])
 t=update(t,vals);banks=[beam]*nb+[torp]*nt+powers.get(n,[])
 for i,w in enumerate(banks,1):t=update(t,{'weapon'+str(i):q(w),'weaponHardpoints'+str(i):q(hps[(i-1)%len(hps)])})
 pending['odf/ships/'+n+'.odf']=t;icon(n,m);records.append({'unit':n,'name':name,'health':hp,'regen':regen,'beams':nb,'torpedoes':nt,'latinum':lat,'energy':energy,'recharge':recharge,'normalDps':nb*bd/1.8*.75+nt*td/2.5*.65,'abilities':powers.get(n,[])})
 print('Prepared',n,flush=True)
# Trading ship: stock scavenger appearance, stock cargo ship controller, isolated doubled physics.
n='xfgtrade';m=load(root/'SOD/zferengi.sod');binary['SOD/'+n+'.sod']=(root/'SOD/zferengi.sod').read_bytes();hps=[z['id']for z in m.nodes if re.fullmatch(r'hp\d+',z['id'],re.I)];assert hps
physics=update(get('scargophys'),{'combatSpeed':40,'impulseSpeed':160,'warpSpeed':0});pending['odf/other/xfgtradephys.odf']=physics
beam=normal('xfgtradeb','beam',39,1.8)
t='#include "cargo.odf"\n';t=update(t,{'unitName':q('Mercenary Ferengi Trade Ship'),'tooltip':q('Mercenary Ferengi Trade Ship'),'verboseTooltip':q('Trades 1,500 cargo per shipment. Twice standard cargo-ship combat and impulse speed. Armed with one defensive disruptor beam.'),'baseName':q(n),'race':q('ferengi'),'classLabel':q('cargo_ship'),'aiName':q('CargoShipProcess'),'m_maxResource':1500,'physicsFile':q('xfgtradephys.odf'),'combatSpeed':40,'impulseSpeed':160,'warpSpeed':0,'canAttack':1,'maxHealth':600,'shieldRate':3.5,'maxSpecialEnergy':0,'specialEnergyRate':0,'crewCost':100,'maximumCrew':150,'officerCost':4,'dilithiumCost':0,'metalCost':0,'latinumCost':300,'biomatterCost':0,'buildTime':40,'ScaleSOD':1.3,'weapon1':q(beam),'weaponHardpoints1':q('hp01'),'hotkeyLabel':q('HOTKEY_F9'),'possibleCraftNames':'"Liquid Profits" "No Refunds" "Quark Express" "Tax Exempt"'})
for k in ['engines','lifeSupport','weapons','shieldGenerator','sensors','hull','critical']:t=put(t,k+'TargetHardpoints',' '.join(q(h)for h in hps[:5]))
for k in ['shieldGeneratorHitPoints','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','sensorsHitPoints']:t=put(t,k,100)
pending['odf/ships/'+n+'.odf']=t;icon(n,m,True)
# Shared contract yard, using the selectively imported Scavengers yard.
n='xfgmerc';m=model(n,next(p for p in(source/'Sod').iterdir()if p.stem.lower()=='fgyard'));hps=[z['id']for z in m.nodes if re.fullmatch(r'hp\d+',z['id'],re.I)];assert any(z['id'].lower()=='build'for z in m.nodes)
t=(source/'odf/stations/fgyard.odf').read_text(encoding='latin1');t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',t)
t=update(t,{'unitName':q('Mercenary Ferengi Contract Yard'),'tooltip':q('Mercenary Ferengi Contract Yard'),'verboseTooltip':q('Contracts Ferengi warships, three mercenary heroes and a 1,500-capacity trade ship. Resource costs are latinum only.'),'baseName':q(n),'maxHealth':2400,'shieldRate':10,'crewCost':200,'maximumCrew':400,'officerCost':10,'dilithiumCost':0,'metalCost':0,'latinumCost':650,'biomatterCost':0,'buildTime':90,'repairFacility':1,'repairHardpoint':q('repair'),'hotkeyLabel':q('HOTKEY_F10')})
for i,x in enumerate([c[0]for c in configs]+['xfgtrade']):t=put(t,'buildItem'+str(i),q(x))
pending['odf/stations/'+n+'.odf']=t;icon(n,m)
# Secondary constructors; never add contract yards to Federation/Borg menus.
menus={}
for b in ['xbjuconst','xbruconst','xcuconst','xcduniv','xduconst','kconst2','xkuconst','rconst2','xruconst']:
 t=get(b);items={int(k[9:]):v for k,v in props[b].items()if re.fullmatch(r'builditem\d+',k)};slot=max(items,default=-1)+1;assert slot<13,(b,slot)
 t=put(t,'buildItem'+str(slot),q('xfgmerc'));rel=str(Path(props[b]['file']).relative_to(root)).replace('\\','/');pending[rel]=t;menus[b]=slot
# Cardassian detector uses its own research, preserving Federation/Klingon tech.
pending['odf/special_weapons/gdetectc.odf']=get('gdetectf');pending['odf/stations/csensor.odf']=put(get('csensor'),'weapon1',q('gdetectc'))
for name in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+name+'.tt';t=(root/rel).read_text(encoding='latin1')
 lines={'xfgmerc':[],'brconst':[],'xbruconst':[],'gdetectc':[]if name=='fulltech'else['carpod5']}
 for c in configs:lines[c[0]]=[]if name=='fulltech'else['xfgmerc']
 lines['xfgtrade']=[]if name=='fulltech'else['xfgmerc']
 for a in abilityids:lines[a]=[]
 for unit,req in lines.items():t=re.sub(r'(?mi)^\s*'+re.escape(unit)+r'\.odf\s+[^\r\n]*','',t);t+='\n'+unit+'.odf '+str(len(req))+''.join(' '+r+'.odf'for r in req)+'\n'
 pending[rel]=t
# Additional trade commodities retain existing goods. Native numbered cargo entries.
goods=[('CLOAKING','Cloaking Devices',1.5),('QUANTUM','Quantum Cores',1.5),('TRANSPHASIC','Transphasic Torpedoes',1.9),('CONTRABAND','Contraband',1.2),('QUARK','Quark\'s Delivery',1.0),('TRIBBLE_INSURANCE','Tribbles (Some Assembly Required)',.8),('BLOODWINE','Bloodwine: Definitely Not Decaf',1.1),('EARPLUGS','Klingon Opera Earplugs',1.0),('SELF_SEALING','Self-Sealing Stem Bolts (Probably)',1.1),('HOLO_COUPONS','Expired Holodeck Coupons',.5),('RULES','Rules of Acquisition: Fine Print Edition',1.0)]
goods += [('GEL','Biomimetic Gel',1.8),('PERIDAXON','Peridaxon',1.6),('WHITE','Ketracel-White',1.8),('DEUTERIUM','Deuterium',1.0),('ANTIMATTER','Antimatter',1.5)]
loc=(root/'Dynamic_Localized_Strings.h').read_text(encoding='latin1');anchor='"GUI_SD_CARGO_RAKTAJINO"' # insert beside existing cargo strings, inside native table
match=re.search(r'(?m)^.*"GUI_SD_RAKTAJINO"[^\r\n]*',loc);assert match
addition='\n'+''.join('\t"GUI_SD_XFG_'+key+'", "'+label+'",\n'for key,label,val in goods);loc=loc[:match.end()]+addition+loc[match.end():];pending['Dynamic_Localized_Strings.h']=loc
for rel in ['odf/stations/TradingStation.odf','odf/stations/ds9.odf']:
 t=(root/rel).read_text(encoding='latin1')
 for i,(key,label,val)in enumerate(goods,13):t+='\ncargoKey'+str(i)+' = "GUI_SD_XFG_'+key+'"\ncargoValue'+str(i)+' = '+str(val)+'\n'
 pending[rel]=t
credits=next(source.parent.glob('*Install.txt'));binary['Credits/Mercenary Ferengi - original credits.txt']=credits.read_bytes()
pending['Sprites/gui_global.spr']=sprite
for rel,t in pending.items():
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for rel,b in binary.items():out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
report={'staged':True,'applied':False,'runtimeVerified':False,'backup':str(backup),'ships':records,'trade':{'capacity':1500,'combatSpeed':40,'impulseSpeed':160,'beams':1,'stockModel':'zferengi'},'menus':menus,'commodities':[x[1]for x in goods],'files':list(pending)+list(binary)}
(repo/'reports/mercenary-ferengi-install.json').write_text(json.dumps(report,indent=2));print('STAGED',len(report['files']),'files',flush=True)



