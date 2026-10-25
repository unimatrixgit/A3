"""Stage faction mining yards, research-gated miner refits and consistent tier names."""
from pathlib import Path
import json,re,hashlib,math,datetime

root=Path('D:/armadaIII');repo=Path('D:/aramada')
stage=repo/'patches/mining-yards-20261025';overlay=stage/'overlay'
idx={p.stem.lower():p for p in (root/'odf').rglob('*.odf')}
pending={};gates={};records=[];refits=[];renames=[]
def raw(n):
 p=idx[n.lower()];rel=p.relative_to(root).as_posix();return pending[rel]if rel in pending else p.read_text(encoding='latin1')
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=raw(n);d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):d.update(props(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
P={n:props(n)for n in idx}
def q(s):return '"'+str(s)+'"'
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+str(v)+'\n'
def update(t,d):
 for k,v in d.items():t=put(t,k,v)
 return t
def emit(n,t,folder='ships'):
 rel=idx[n].relative_to(root).as_posix()if n in idx else 'odf/'+folder+'/'+n+'.odf'
 pending[rel]=t
 if n not in idx:idx[n]=root/rel
 return rel
def num(x):return float(str(x).rstrip('fF;'))
def menu(t,items):
 assert len(items)<=14
 t=re.sub(r'(?mi)^[ \t]*buildItem\d+[ \t]*=[^\r\n]*','',t)
 for i,n in enumerate(items):t=put(t,'buildItem'+str(i),q(n))
 return t
def items(d):return[v for k,v in sorted(d.items(),key=lambda kv:int(kv[0][9:])if re.fullmatch(r'builditem\d+',kv[0])else-1)if re.fullmatch(r'builditem\d+',k)]
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
def alias(new,old):
 global sprite
 for a,b in [('b_'+new,'b_'+old)]+[(new+'w'+str(i),old+'w'+str(i))for i in range(1,6)]:
  m=re.search(r'(?mi)^'+re.escape(b)+r'[ \t]+[^\r\n]+',sprite);assert m,(new,old,b)
  ref=re.findall(r'(?mi)^@reference[ \t]*=[ \t]*(\d+)',sprite[:m.start()])[-1]
  sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+',a,m[0])+'\n'

spec=[('federation','f','ffreight','fconst','fyard'),('borg','b','bfreight','bconst','byard'),('klingon','k','kfreight','kconst','kyard'),('romulan','r','rfreight','rconst','ryard'),('cardassian','c','cfreight','cconst','cyard'),('dominion','d','dfreight','dconst','dyard'),('bajoran','bj','bjfreight','bjconst','bjyard'),('breen','br','brfreight','brconst','bryard'),('species8472','s','8472_collector','8472_passive','714syard')]
# Federation has no native Ferengi contract-yard construction route. Reuse the
# verified free fifth research socket rather than making Federation pay Latinum.
assert len(items(P['fresear2']))==4 and len(re.findall(r'[A-Za-z0-9_]+',P['fresear2']['podhardpoints']))>=5
for level,donor in [(1,'xbgpdil'),(2,'xbgpdil2')]:
 n='myfpod'+str(level);title='Dilithium Contracts '+('I (+50%)'if level==1 else'II (+100%)')
 emit(n,update(raw(donor),{'race':q('federation'),'unitName':q(title),'tooltip':q(title),'verboseTooltip':q(title+'\\nUnlocks researched collectors and refit buttons\\nStarfleet industry sustains exploration.')}),'stations');alias(n,donor)
 gates[n]=['fresear2']+(['myfpod1']if level==2 else[])
emit('fresear2',update(raw('fresear2'),{'buildItem4':q('myfpod1'),'buildItem5':q('myfpod2'),'podHardpoints':' '.join(q(hp)for hp in re.findall(r'[A-Za-z0-9_]+',P['fresear2']['podhardpoints'])+['myminingpod'])}),'stations')
bankcache={}
def enhanced_beam(w,tier):
 key=(w,tier)
 if key in bankcache:return bankcache[key]
 d=P[w];o=d['ordname'].lower();od=P[o];name='myw'+str(len(bankcache)).zfill(3);ordn=name+'o'
 assert od.get('classlabel','').lower()=='minebm',(w,o)
 mult=1.5 if tier==1 else 2
 emit(ordn,put(raw(o),'damageBase',format(num(od['damagebase'])*mult,'.8g')),'special_weapons')
 emit(name,put(raw(w),'ordName',q(ordn)),'special_weapons');gates[name]=[];bankcache[key]=name
 return name

def upgrade(source,target,deps):
 d=props(source);banks=sorted((int(k[6:]),v.lower())for k,v in d.items()if re.fullmatch(r'weapon\d+',k))
 assert banks and max(i for i,w in banks)<16,source
 slots={int(num(props(w).get('buttonslot',0)))for i,w in banks};slot=next(i for i in range(1,10)if i not in slots)
 hotkeys={props(w).get('hotkeylabel','')for i,w in banks};hotkey=next('HOTKEY_F'+str(i)for i in range(1,13)if'HOTKEY_F'+str(i)not in hotkeys)
 n='myu'+str(len(refits)).zfill(3);t=raw('fnxenttoent')
 t=update(t,{'wpnName':q('Upgrade Mining Equipment'),'tooltip':q('Upgrade Mining Equipment'),'verboseTooltip':q('Upgrade to '+props(target)['unitname']+'. Research required. Unload cargo before refitting.'),'fusedClass':q(target),'multiReqClass0':q(source),'multiReqMin0':1,'buttonSlot':slot,'hotkeyLabel':q(hotkey),'specialEnergyCost':0,'fusingMetalCost':0})
 emit(n,t,'special_weapons');gates[n]=deps
 bank=max(i for i,w in banks)+1;hp=d.get('weaponhardpoints'+str(banks[0][0]),'hp01')
 emit(source,update(raw(source),{'weapon'+str(bank):q(n),'weaponHardpoints'+str(bank):q(hp)}))
 # An individual special-weapon sprite; do not replace any native command icon.
 global sprite
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' gbmyupgrade 0 0 64 64\n'
 refits.append({'source':source,'target':target,'weapon':n,'research':deps,'buttonSlot':slot,'energyCost':0,'cargoPreservationVerified':False})

for race,code,base,builder,donor in spec:
 yard='my'+code+'yard';d=P[base]
 if race=='species8472':tiers=['xsbcol1','xsbcol2'];pods=['xsbio1','xsbio2']
 else:
  tiers=['my'+code+'miner1','my'+code+'miner2'];pods=['myfpod1','myfpod2']if race=='federation'else['xbgpdil','xbgpdil2']if race=='borg'else['xfgpdil','xfgpdil2']
 for level,n in enumerate([base]+tiers):
  title=('Biomatter Collector'if race=='species8472'else'Dilithium Collector')+' MK '+['I','II','III'][level]
  t=raw(n)if n in idx else raw(base)
  t=update(t,{'unitName':q(title),'tooltip':q(title),'verboseTooltip':q(title+'\\n'+('Biomatter extraction'if race=='species8472'else'Dilithium extraction')+(' +'+str(level*50)+'% capacity and rate'if level else'')+'\\nResources sustain the fleet.')})
  if level:
   if race=='species8472':t=put(t,'maxBiomatter',round(num(d['maxbiomatter'])*(1+level*.5)))
   else:
    t=put(t,'maxDilithium',round(num(d['maxdilithium'])*(1+level*.5)))
    for k,w in d.items():
     if re.fullmatch(r'weapon\d+',k)and w.lower()in P:
      wd=P[w.lower()];od=P.get(wd.get('ordname','').lower(),{})
      if od.get('classlabel','').lower()=='minebm'and'dilithium'in w.lower():t=put(t,k,q(enhanced_beam(w.lower(),level)))
    # Reuse all model/voice/physics/weapon hardpoint settings; prices scale modestly.
    t=put(t,'dilithiumCost',round(num(d.get('dilithiumcost',0))*(1+level*.25)))
   gates[n]=[yard,pods[level-1]]
  emit(n,t);alias(n,base)if n not in P else None
 upgrade(base,tiers[0],[pods[0]]);upgrade(tiers[0],tiers[1],[pods[1]])
 # Dominion outpost uses a separate miner alias; give it an identical upgrade path.
 if race=='dominion':
  emit('xdominer',update(raw('xdominer'),{'unitName':q('Dilithium Collector MK I'),'tooltip':q('Dilithium Collector MK I')}));upgrade('xdominer',tiers[0],[pods[0]])
 t=raw(donor)
 t=re.sub(r'(?mi)^[ \t]*(?:weapon\d+|weaponHardpoints\d+)[ \t]*=[^\r\n]*','',t)
 cost={'dilithiumCost':200,'metalCost':400,'latinumCost':0,'biomatterCost':0,'crewCost':100,'maximumCrew':250}
 if race=='species8472':cost.update(dilithiumCost=0,metalCost=0,biomatterCost=600,crewCost=0,maximumCrew=0)
 t=update(menu(t,[base]+tiers),dict(cost,unitName=q(('Species 8472'if race=='species8472'else race.title())+' Mining Yard'),tooltip=q('Mining Yard'),verboseTooltip=q('Mining Yard\\nCollectors MK I, II and III; repairs\\nIndustrial docks keep the fleet supplied.'),race=q(race),classLabel=q('shipyard'),maxHealth=1400,shieldRate=8,repairFacility=1,buildTime=45,officerCost=5,hotkeyLabel=q('HOTKEY_F13')))
 emit(yard,t,'stations');gates[yard]=[]
 # Each yard is available on the native basic constructor; Species 8472 also has a rig.
 builders=[builder]+(['714const','8472_defender']if race=='species8472'else[])
 for b in builders:
  bi=items(props(b));assert yard not in bi and len(bi)<14,(b,bi);emit(b,menu(raw(b),bi+[yard]))
 records.append({'race':race,'yard':yard,'donor':donor,'builders':builders,'miners':[base]+tiers,'pods':pods,'cost':cost,'researchBonus':'1.0 / 1.5 / 2.0 cargo and extraction; native latinum and metal equipment unchanged'})

# Ferengi miners stay at their Ferengi Service Yards, including the Borg-priced versions.
for prefix in ['xfg','xbg']:
 base=prefix+'mine';d=P[base];tiers=[prefix+'mnr1',prefix+'mnr2'];pods=[prefix+'pdil',prefix+'pdil2'];latpods=['xfgplat','xfgplat2']if prefix=='xfg'else[]
 for level,n in enumerate(tiers,1):
  title='Dilithium Collector MK '+['II','III'][level-1]
  t=update(raw(base),{'unitName':q(title),'tooltip':q(title),'verboseTooltip':q(title+'\\nImproved mining equipment\\nA full hold is a profitable hold.'),'maxDilithium':round(num(d['maxdilithium'])*(1+level*.5))})
  if latpods:t=put(t,'maxLatinum',round(num(d['maxlatinum'])*(1+level*.5)))
  for k,w in d.items():
   if re.fullmatch(r'weapon\d+',k)and P.get(w.lower(),{}).get('ordname','').lower()in P:t=put(t,k,q(enhanced_beam(w.lower(),level)))
  t=put(t,'latinumCost',round(num(d.get('latinumcost',0))*(1+level*.25)))
  if prefix=='xbg':
   for key in ['dilithiumcost','metalcost']:t=put(t,key,round(num(d.get(key,0))*(1+level*.25)))
  emit(n,t);alias(n,base);gates[n]=[prefix+'serv',pods[level-1]]+([latpods[level-1]]if latpods else[])
 upgrade(base,tiers[0],[pods[0]]+latpods[:1]);upgrade(tiers[0],tiers[1],[pods[1]]+latpods[1:])
 serv=prefix+'serv';emit(serv,menu(raw(serv),items(props(serv))+tiers))
 # Existing dedicated dil/lat collectors keep their role and can refit to the next tier.
 for resource,pod in [('dil','pdil')]+([('lat','plat')]if prefix=='xfg'else[]):
  upgrade(prefix+resource+'2',prefix+resource+'3',[prefix+pod+'2'])
 for pod in pods+latpods:
  title=props(pod)['unitname'];emit(pod,put(raw(pod),'verboseTooltip',q(title+'\\nUnlocks researched collectors and refit buttons\\nResearch equips the fleet for profitable extraction.')),'stations')

# Consistent display names only: no ODF filenames or production references are renamed.
for n,d in P.items():
 title=None;race=d.get('race','');old=d.get('unitname','')
 if d.get('classlabel')=='constructionrig'or n=='8472_passive':
  tier=3 if any(x in old.lower()for x in ['temporal','universal'])else 2 if'advanced'in old.lower()or'omega'in old.lower()else 1
  title='Assemblers MK '+['I','II','III'][tier-1]
 if n in ['forbital','bbase2','borbital','korbital','rorbital','corbital','dorbital','bjorbital','brorbital','xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:
  tier=3 if n.endswith('metal3')else 2 if n.endswith('metal2')else 1;title='Orbital Mining Station MK '+['I','II','III'][tier-1]
 if n in ['xfgmine','xbgmine','xfgdil2','xbgdil2','xfgdil3','xbgdil3','xfglat2','xfglat3']:
  tier=3 if n.endswith('3')else 2 if n.endswith('2')else 1;title=('Latinum Collector'if'lat'in n else'Dilithium Collector')+' MK '+['I','II','III'][tier-1]
 if title:
  desc=props(n).get('verbosetooltip','').split('\\n');desc[0]=title
  emit(n,update(raw(n),{'unitName':q(title),'tooltip':q(title),'verboseTooltip':q('\\n'.join(desc))}));renames.append({'unit':n,'name':title})

# Native research gates and button entries in every technology mode.
for file in (root/'techtree').glob('*.tt'):
 text=file.read_text(encoding='latin1')
 for n,deps in gates.items():
  line=n+'.odf '+('0'if file.stem.lower()=='fulltech'else str(len(deps))+(' '+' '.join(x+'.odf'for x in deps)if deps else''))
  pattern=r'(?mi)^'+re.escape(n)+r'\.odf[ \t]+[^\r\n]*'
  text=re.sub(pattern,line,text)if re.search(pattern,text)else text.rstrip()+'\n'+line+'\n'
 pending[file.relative_to(root).as_posix()]=text

# Add each yard before the first normal miner row; place upgrade production only after
# its required research already exists in that plan. Do not alter campaign scripts.
ai=[]
rowpat=re.compile(r'(?m)^[ \t]*"([^"]+)"[ \t]*,[^\r\n]*')
for cfg in records:
 for f in (root/'AI/AIPs').glob(cfg['race']+'_*list.aip'):
  text=f.read_text(encoding='latin1');rows=list(rowpat.finditer(text));assert rows,f
  names=[m[1].lower()for m in rows];base=cfg['miners'][0];pos=next((i for i,n in enumerate(names)if n==base),None)
  if pos is None:pos=next((i+1 for i,n in enumerate(names)if n in cfg['builders']),None)
  assert pos is not None,(f,cfg)
  insert=rows[min(pos,len(rows)-1)].start();line='    "'+cfg['yard']+'", 1, 0, -1, 0, // native mining production\n'
  text=text[:insert]+line+text[insert:]
  added=[]
  for tier,pod in enumerate(cfg['pods'],1):
   match=re.search(r'(?m)^[ \t]*"'+pod+r'"[ \t]*,[^\r\n]*',text)
   if match:
    line='\n    "'+cfg['miners'][tier]+'", 2, 0, -1, 0, // researched native collector'
    text=text[:match.end()]+line+text[match.end():];added.append(cfg['miners'][tier])
  pending[f.relative_to(root).as_posix()]=text;ai.append({'file':f.name,'yard':cfg['yard'],'tieredMiners':added})

pending['Sprites/gui_global.spr']=sprite
for rel,t in pending.items():
 dest=overlay/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
report={'status':'STAGED','yards':records,'refits':refits,'renames':renames,'ai':ai,'gates':gates,'runtimeVerified':False,'orbitalRefitsImplemented':False,'note':'Refits use the existing one-unit NX fusion pattern. Cargo/planet attachment behavior must be tested; no orbital fusion added. New construction offers three explicit MK options; it does not automatically select the highest tier.'}
(stage/'gameplay.json').write_text(json.dumps(report,indent=2));(repo/'reports/mining-yards-prepared.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'yards':len(records),'refits':len(refits),'AIplans':len(ai),'files':len(pending),'stage':str(stage)}))
