from pathlib import Path
exec(Path('D:/aramada/scripts/install-mercenary-ferengi.py').read_text().split('powers={')[0])
import collections
props=json.loads((repo/'reports/mirror-current-properties.json').read_text());stage=Path('D:/Xaramada-Modwork/mirror-ferengi-stage');stage.mkdir(parents=True,exist_ok=True);backup=Path('D:/Xaramada-Modwork/backups')/('mirror-ferengi-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};binary={};sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');techdefs={};rows=[];stationrows=[]
index={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def text(n):
 for rel,t in pending.items():
  if rel.lower().endswith('/'+n.lower()+'.odf'):return t
 return index[n.lower()].read_text(encoding='latin1')
def resolve(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=text(n);d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(resolve(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^\s*([a-z][a-z0-9_]*)\s*=\s*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d

def num(v):return float(str(v).strip().rstrip('fF;'))
def serialize(d):
 out=[]
 for k,v in d.items():
  if k=='file':continue
  value=str(v)
  if not re.fullmatch(r'[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?[fF]?;?',value):value=q(value)
  out.append(k+' = '+value)
 return '\n'.join(out)+'\n'
def aliasgui(n,donor):
 global sprite
 d=resolve(donor);model=d.get('basename',donor)
 for key,tries in [('b_'+n,['b_'+donor,'b_'+model])]+[(n+'w'+str(i),[donor+'w'+str(i),model+'w'+str(i)])for i in range(1,6)]:
  found=None
  for candidate in tries:
   m=re.search(r'(?mi)^'+re.escape(candidate)+r'[ \t]+[^\r\n]+',sprite)
   if m:found=m;break
  if found:
   ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:found.start()])[-1];sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+',key,found[0])+'\n'
  elif key.startswith('b_'):
   try:mm=load(root/'SOD'/(model+'.sod'))
   except Exception:
    with contextlib.redirect_stdout(io.StringIO()):mm=SodIO().read_file(str(root/'SOD'/(model+'.sod')))
   icon(n,mm)

def cardicon(key):
 m=re.search(r'(?mi)^'+key+r'[ \t]+([^\r\n]+)',sprite);assert m,key
 parts=m[1].split();ref=int(re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:m.start()])[-1]);base=Image.open(texidx[parts[0].lower()]).convert('RGB');a=[float(x)*base.width/ref for x in parts[1:5]];x,y,w,h=a;return base.crop((int(x),int(y),int(x+w),int(y+h))).resize((128,128))
# Existing Cardassian artwork, distinct mirror overlay; no external bitmap generation.
for name,key in [('gbmirror','b_gquanteffect'),('gbmirrorpod','b_carpod7')]:
 im=cardicon(key);d=ImageDraw.Draw(im);d.rectangle((0,96,127,127),fill=(8,10,20));font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23);d.text((37,96),'MIR',font=font,fill=(110,210,255));d.line((21,16,104,16),fill=(235,150,245),width=5);d.polygon([(104,16),(91,8),(91,24)],fill=(235,150,245));binary['Textures/RGB/'+name+'.tga']=imgbytes(im.resize((64,64),Image.Resampling.LANCZOS))
def button(n,texture):
 global sprite
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+texture+' 0 0 64 64\n'

def pod(n,race,name,parent,slot,price='native'):
 t='#include "pod.odf"\n';cost={'dilithiumCost':600,'metalCost':300,'latinumCost':200 if race in ['bajoran','breen','cardassian','dominion','klingon','romulan']else 0,'biomatterCost':0}
 if race=='ferengi':cost={'dilithiumCost':0,'metalCost':0,'latinumCost':900,'biomatterCost':0}
 if race=='species8472':cost={'dilithiumCost':0,'metalCost':0,'latinumCost':0,'biomatterCost':900}
 t=update(t,dict(cost,baseName=q('carpod7'),race=q(race),unitName=q(name),tooltip=q(name),verboseTooltip=q('Unlocks the described technology. Mirror Reinforcement creates an owned counterpart with doubled normal damage,75 percent durability and125 percent size.'if 'Mirror'in name else'Unlocks enhanced Ferengi resource equipment; existing units retain their current equipment.'),buildTime=90,crewCost=0,officerCost=1,hotkeyLabel=q('HOTKEY_F'+str(slot+1)),ScaleSOD=.6));pending['odf/stations/'+n+'.odf']=t;button(n,'gbmirrorpod');techdefs[n]=[]if n.startswith('mrp')else[parent]

# Ferengi research facility, retaining Ferengi station art and using Cardassian pod models.
d=resolve('xfgserv');t='#include "research.odf"\n';m=load(root/'SOD/xfgserv.sod');anchors=[z['id']for z in m.nodes if re.fullmatch(r'hp\d+',z['id'],re.I)][:4];assert len(anchors)==4
vals={'baseName':q('xfgserv'),'race':q('ferengi'),'unitName':q('Ferengi Commerce Institute'),'tooltip':q('Ferengi Commerce Institute'),'verboseTooltip':q('Researches improved dilithium, metal and latinum equipment, and Mirror Universe Reinforcement. Research unlocks new equipment versions.'),'maxHealth':1800,'shieldRate':8,'crewCost':100,'maximumCrew':200,'officerCost':5,'buildTime':75,'dilithiumCost':0,'metalCost':0,'latinumCost':500,'biomatterCost':0,'ScaleSOD':d['scalesod'],'podHardpoints':' '.join(q(x)for x in anchors),'hotkeyLabel':q('HOTKEY_F11')}
t=update(t,vals)
for i,n in enumerate(['xfgpdil','xfgpmet','xfgplat','mrpfer']):t=put(t,'buildItem'+str(i),q(n))
pending['odf/stations/xfgresearch.odf']=t;aliasgui('xfgresearch','xfgserv');techdefs['xfgresearch']=[]
for i,(n,title)in enumerate([('xfgpdil','Dilithium Extraction Contracts'),('xfgpmet','Metal Processing Contracts'),('xfgplat','Latinum Prospecting Contracts')]):pod(n,'ferengi',title,'xfgresearch',i)
# Research-unlocked equipment versions. Each costs latinum; base miner is unchanged.
for n,resource,power,parent,slot in [('xfgdil2','dilithium','xfgmineD2','xfgpdil',5),('xfglat2','latinum','xfgmineL2','xfgplat',6)]:
 t=text('xfgmine');t=stripbanks(t);t=update(t,{'unitName':q('Mercenary Ferengi Enhanced '+resource.title()+' Collector'),'tooltip':q('Enhanced '+resource.title()+' Collector'),'verboseTooltip':q('Research-unlocked collector with45 units extracted every1.5 seconds. Latinum resource cost only.'),'resourcesCanHandle':q(resource),'weapon1':q(power),'weaponHardpoints1':q('hp01'),'latinumCost':350,'hotkeyLabel':q('HOTKEY_F'+str(slot+1))});pending['odf/ships/'+n+'.odf']=t;aliasgui(n,'xfgmine');techdefs[n]=['xfgserv',parent]
 w=update(text('gmineDilithium'if resource=='dilithium'else'gmineLatinum'),{'ordName':q(power+'o')});o=put(text('mineDilithium'if resource=='dilithium'else'mineLatinum'),'damageBase',45);pending['odf/special_weapons/'+power+'.odf']=w;pending['odf/special_weapons/'+power+'o.odf']=o;techdefs[power]=[]
 t=text('xfgserv');pending['odf/stations/xfgserv.odf']=put(t,'buildItem'+str(slot),q(n))
# Metal research unlocks a Ferengi orbital, using the dedicated Ferengi base art.
t=stripbanks(text('corbital'));t=update(t,{'baseName':q('xfgserv'),'race':q('ferengi'),'unitName':q('Mercenary Ferengi Advanced Metal Orbital'),'tooltip':q('Advanced Ferengi Metal Orbital'),'verboseTooltip':q('Research-unlocked planetary metal processor. Latinum resource cost only.'),'ScaleSOD':d['scalesod'],'dilithiumCost':0,'metalCost':0,'latinumCost':400,'biomatterCost':0,'miningMultiplier':.9,'weapon1':q('gOrbitalBeam'),'weaponHardpoints1':q(anchors[0]),'hotkeyLabel':q('HOTKEY_F12')})
for k in ['engines','lifeSupport','weapons','shieldGenerator','sensors','hull','critical']:t=put(t,k+'TargetHardpoints',' '.join(q(x)for x in anchors))
pending['odf/stations/xfgmetal2.odf']=t;aliasgui('xfgmetal2','xfgserv');techdefs['xfgmetal2']=['xfgpmet']
pending['odf/ships/xfgconst.odf']=update(text('xfgconst'),{'buildItem10':q('xfgresearch'),'buildItem11':q('xfgmetal2')})
# Borg-specific catalog. Cost variants prevent changing the other factions' latinum contracts.
baseunits=['xfgmerc','xfgserv','xfgconst','xfgfight','xfgfrig','xfgdest','xfgcruis','xfgbatt','xfgquark','xfgrom','xfgnagus','xfgdaim','xfgmine','xfgrepair','xfgcolony','xfgresearch','xfgdil2','xfgmetal2','xfgpdil','xfgpmet'];borgmap={n:'xbg'+n[3:]for n in baseunits}
for n,new in borgmap.items():
 rd=resolve(n);t=text(n);price=num(rd.get('latinumcost',0));t=update(t,{'race':q('borg'),'dilithiumCost':int(round(price*.6)),'metalCost':int(round(price*.4)),'latinumCost':0,'biomatterCost':0})
 t=put(t,'verboseTooltip',q('Borg contract paid in dilithium and metal. '+re.sub('latinum','dilithium and metal',rd.get('verbosetooltip',''),flags=re.I)))
 for k,v in rd.items():
  if re.fullmatch(r'builditem\d+',k)and v in borgmap:t=put(t,k,q(borgmap[v]))
 if n=='xfgserv':t=re.sub(r'(?mi)^\s*buildItem6\s*=[^\r\n]*','',t)
 if n=='xfgresearch':
  t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',t)
  for i,unit in enumerate([borgmap['xfgpdil'],borgmap['xfgpmet'],'mrpbor']):t=put(t,'buildItem'+str(i),q(unit))
  t=put(t,'podHardpoints',' '.join(q(x)for x in anchors[:3]));t=put(t,'verboseTooltip',q('Dilithium/metal funded Ferengi research for the Borg. No latinum prospecting research is offered.'))
 if n=='xfgmine':t=put(stripbanks(t),'weapon1',q('xfgminedil'));t=update(t,{'weaponHardpoints1':q('hp01'),'resourcesCanHandle':q('dilithium'),'maxLatinum':0})
 if n=='xfgdil2':t=put(t,'maxLatinum',0)
 if n not in ['xfgmerc','xfgserv','xfgresearch','xfgmetal2','xfgpdil','xfgpmet']:folder='ships'
 else:folder='stations'
 pending['odf/'+folder+'/'+new+'.odf']=t;aliasgui(new,n);deps=techdefs.get(n,['xfgmerc']if n.startswith('xfg')and n not in ['xfgmerc','xfgserv','xfgresearch']else[]);techdefs[new]=[borgmap.get(x,x)for x in deps]
for b in ['uconst','xbuconst','bconst2']:
 rd=resolve(b);slot=max(int(k[9:])for k in rd if re.fullmatch(r'builditem\d+',k))+1;assert slot<13
 pending['odf/ships/'+b+'.odf']=put(text(b),'buildItem'+str(slot),q(borgmap['xfgmerc']))
# The trading freighter is deliberately shared, still latinum priced.
assert resolve('xfgtrade')['latinumcost']=='300'

# Select existing research stations with free physical anchors; add one anchor only when necessary.
stationcfg={'federation':'fresear2','borg':'bresear2','klingon':'kresear2','romulan':'xselaresearch','cardassian':'cresear2','dominion':'dresear2','breen':'brresear2','bajoran':'bjresear2','species8472':'8472_advancedresearch','ferengi':'xfgresearch'}
podids={'federation':'mrpfed','borg':'mrpbor','klingon':'mrpkli','romulan':'mrprom','cardassian':'mrpcar','dominion':'mrpdom','breen':'mrpbre','bajoran':'mrpbaj','species8472':'mrpspe','ferengi':'mrpfer'}
for race,station in stationcfg.items():
 rd=resolve(station);items={int(k[9:]):v for k,v in rd.items()if re.fullmatch(r'builditem\d+',k)}
 if race=='ferengi':slot=3
 else:
  slot=max(items,default=-1)+1;t=text(station);modelname=rd.get('basename',station)
  try:m=load(root/'SOD'/(modelname+'.sod'))
  except Exception:
   with contextlib.redirect_stdout(io.StringIO()):m=SodIO().read_file(str(root/'SOD'/(modelname+'.sod')))
  hp=rd.get('podhardpoints','').replace('"','').split()
  if len(hp)<=slot:
   parent=next(z for z in m.nodes if not z['parent']);verts=np.array([v for tr in mesh_triangles(m)for v in tr]);pos=[float((verts[:,0].max()+verts[:,0].min())/2),float(verts[:,1].max()+8),float((verts[:,2].max()+verts[:,2].min())/2)];a=np.linalg.inv(matrix(parent))@np.array(pos+[1]);anchor='mirrorpod';m.nodes.append({'type':'NULL_OR_HARDPOINT','id':anchor,'parent':parent['id'],'local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],a[:3].tolist()],'data':None});hp.append(anchor);alias='mrst_'+race[:3];out=stage/'SOD'/(alias+'.sod');out.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
   with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(out))
   binary['SOD/'+alias+'.sod']=out.read_bytes();aliasgui(alias,station);t=put(t,'baseName',q(alias))
  assert len(hp)>slot,(race,slot,hp)
  t=update(t,{'podHardpoints':' '.join(q(x)for x in hp),'buildItem'+str(slot):q(podids[race])});pending['odf/stations/'+station+'.odf']=t
 pod(podids[race],race,'Mirror Universe Reinforcement Research',station,slot);stationrows.append({'faction':race,'station':station,'slot':slot,'pod':podids[race]})
# Catalog of military hero definitions, including Borg-paid Ferengi variants.
allnames=set(index)|{Path(rel).stem.lower()for rel in pending if rel.endswith('.odf')};heroes=[]
for n in sorted(allnames):
 rd=resolve(n)
 if rd.get('ishero')=='1'and n not in ['q','momega']and (n in props and '/ships/'in props[n]['file'].replace('\\','/').lower()or n in [borgmap[x]for x in ['xfgquark','xfgrom','xfgnagus']]):heroes.append(n)
weaponcache={}
def double_values(v):
 parts=re.split(r'("[^"]*")',v)
 for i in range(0,len(parts),2):parts[i]=re.sub(r'(?<![a-zA-Z_])[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?',lambda m:format(float(m[0])*2,'.10g'),parts[i])
 return ''.join(parts)
def mirrored_weapon(n):
 if n in weaponcache:return weaponcache[n]
 rd=resolve(n);ordn=rd.get('ordname');od=resolve(ordn.lower())if ordn else{}
 if rd.get('special')=='1'or not ordn:return n
 if not any(num(x)>0 for x in [rd.get('damagebase','0'),od.get('damagebase','0')]if re.fullmatch(r'[\d.eE+-]+[fF]?',x)):return n
 alias='mrw'+str(len(weaponcache)).zfill(3);oa=alias+'o';directory='Phasers'if od.get('classlabel','').lower()=='phaser'else'Pulse'if od.get('classlabel','').lower()=='pphaser'else'Photons'if od.get('classlabel','').lower()in ['photontorpedo','artillery']else'Other'
 wt=text(n);ot=text(ordn)
 for key in ['damagebase','damagevariance']:
  if key in rd:wt=put(wt,key,double_values(rd[key]))
  if key in od:ot=put(ot,key,double_values(od[key]))
 wt=put(wt,'ordName',q(oa));pending['odf/weapons/'+directory+'/'+alias+'.odf']=wt;pending['odf/weapons/'+directory+'/'+oa+'.odf']=ot;weaponcache[n]=alias;return alias
snapshots={n:resolve(n)for n in heroes}
for i,n in enumerate(heroes):
 rd=snapshots[n];race=rd.get('race');assert race in podids,(n,race);clone='mrc'+str(i).zfill(3);ability='mra'+str(i).zfill(3);ordn=ability+'o';banks=sorted((int(k[6:]),v)for k,v in rd.items()if re.fullmatch(r'weapon\d+',k));usedslots=set();usedkeys=set()
 for j,w in banks:
  wd=resolve(w.lower())
  if wd.get('special')=='1':
   if wd.get('buttonslot'):usedslots.add(int(num(wd['buttonslot'])))
   usedkeys.add(wd.get('hotkeylabel',''))
 slot=next(x for x in range(1,10)if x not in usedslots);hotkey=next('HOTKEY_F'+str(x)for x in range(1,13)if'HOTKEY_F'+str(x)not in usedkeys);nextbank=max(j for j,w in banks)+1;assert nextbank<=16
 summonname="Hugh's Cube"if n in ['blocutus','xoblocutus']else'Mirror '+rd.get('unitname',n)
 copyprops=dict(rd);copyprops.update({'unitname':summonname,'tooltip':summonname,'verbosetooltip':'Mirror Universe counterpart: double normal-weapon damage,75 percent original durability,125 percent original size. No Mirror Reinforcement ability.','possiblecraftnames':summonname,'basename':rd.get('basename',n),'maxhealth':format(num(rd['maxhealth'])*.75,'.10g'),'scalesod':format(num(rd.get('scalesod','1'))*1.25,'.10g'),'ishero':'0','dilithiumcost':'0','metalcost':'0','latinumcost':'0','biomattercost':'0'})
 for j,w in banks:copyprops['weapon'+str(j)]=mirrored_weapon(w.lower())
 if n in ['blocutus','xoblocutus']:
  for key,v in resolve('bbattle').items():
   if key.startswith('event'):copyprops[key]=v
 pending['odf/ships/'+clone+'.odf']=serialize(copyprops);aliasgui(clone,n);techdefs[clone]=[]
 # Generic native object spawner inherits the casting projectile's owner/team flags.
 w=update(text('gholod'),{'ordName':q(ordn),'wpnName':q('Summon Hugh\'s Cube'if n in ['blocutus','xoblocutus']else'Mirror Universe Reinforcement'),'tooltip':q('Summon Hugh\'s Cube'if n in ['blocutus','xoblocutus']else'Mirror Universe Reinforcement'),'verboseTooltip':q('After faction research, click open space to summon '+summonname+'. Double normal damage,25 percent less durability,25 percent larger. Costs1500 energy;120-second cooldown. Player-owned reinforcement.'),'buttonSlot':slot,'popupSlot':slot,'hotkeyLabel':q(hotkey),'shotDelay':120,'range':800,'special':1,'targetLocation':1,'needTarget':1,'switchToAttack':0})
 w=re.sub(r'(?mi)^\s*assimilatable\s*=[^\r\n]*','',w);o=update(text('holod'),{'objectName':q(clone),'specialEnergyCost':1500,'damageBase':0,'damageVariance':0,'lifeSpan':4,'shotSpeed':400});pending['odf/special_weapons/'+ability+'.odf']=w;pending['odf/special_weapons/'+ordn+'.odf']=o;button(ability,'gbmirror');techdefs[ability]=[podids[race]]
 t=serialize(rd);t=update(t,{'weapon'+str(nextbank):q(ability),'weaponHardpoints'+str(nextbank):q(rd.get('weaponhardpoints1','hp01').replace('"','').split()[0]),'maxSpecialEnergy':max(1500,num(rd.get('maxspecialenergy',0))),'specialEnergyRate':max(15,num(rd.get('specialenergyrate',0)))})
 pending['odf/ships/'+n+'.odf']=t;rows.append({'hero':n,'faction':race,'clone':clone,'cloneName':summonname,'ability':ability,'normalDamageMultiplier':2,'oldHealth':num(rd['maxhealth']),'cloneHealth':num(copyprops['maxhealth']),'oldScale':num(rd.get('scalesod','1')),'cloneScale':num(copyprops['scalesod']),'research':podids[race],'buttonSlot':slot,'hotkey':hotkey,'weaponBank':nextbank})
 print('Prepared mirror',n,flush=True)
for name in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+name+'.tt';t=(root/rel).read_text(encoding='latin1')
 for n,dep in techdefs.items():
  t=re.sub(r'(?mi)^\s*'+re.escape(n)+r'\.odf\s+[^\r\n]*','',t)
  deps=[]if name=='fulltech'else dep
  if name=='nospweap'and n.startswith('mra'):t+='\n'+n+'.odf -1\n'
  else:t+='\n'+n+'.odf '+str(len(deps))+''.join(' '+x+'.odf'for x in deps)+'\n'
 pending[rel]=t
pending['Sprites/gui_global.spr']=sprite
for rel,t in pending.items():out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for rel,b in binary.items():out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
r={'stage':str(stage),'backup':str(backup),'applied':False,'runtimeVerified':False,'files':list(pending)+list(binary),'heroes':rows,'researchStations':stationrows,'mirroredWeapons':weaponcache,'borgCatalog':borgmap,'tradingFreighterChanged':False,'hughVoice':'No verified Hugh voice pack found; generic Borg command events replace Locutus events on Hugh clones.','spawnMechanism':'Native ionstorm_tp object creation; projectile owner/team masks copied to spawned object at0x57b557-0x57b56a and0x57b60a-0x57b61d. In-game selection/control still needs testing.'};(repo/'reports/mirror-ferengi-research.json').write_text(json.dumps(r,indent=2));print('STAGED',len(r['files']),'files;',len(rows),'hero mirrors')



