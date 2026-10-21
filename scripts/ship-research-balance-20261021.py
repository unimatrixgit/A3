"""Stage/apply the user's armadaIII-only research, ship-price and platform patch."""
from pathlib import Path
from functools import lru_cache
import contextlib,csv,datetime,hashlib,io,json,math,re,shutil,subprocess,sys

ROOT=Path('D:/armadaIII');REPO=Path('D:/aramada')
PACKAGE=REPO/'patches/20261021-ship-research-balance'
BACKUP=Path('D:/Xaramada-Modwork/backups')/('ship-research-balance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
IDX={p.stem.lower():p for p in(ROOT/'odf').rglob('*.odf')}
FACTIONS={'federation':('f','fresear2','hp10'),'klingon':('k','kresear2','hp10'),
 'romulan':('r','rresear2','hp10'),'cardassian':('c','cresear2','hp01'),
 'dominion':('d','dresear2','hp01'),'borg':('b','bresear2','hp01'),
 'breen':('br','brresear','pod02'),'bajoran':('bj','bjresear2','hp01'),
 'species8472':('s','8472_advancedresearch','hp05')}
UTILITY={'gminedilithium','gminelatinum','gminemetalborg','gminedilithiumborg',
 'gtracbm','gresourceextractionbeam','gcolbeam','fcolonypod','ccolonypod','kcolonypod',
 'rcolonypod','grepairbeam','xbj_grepairbeam'}
HEAVY={'fhwp','khwp','rhwp','chwp','dturret3','bjhwp','bhwp'}
pending={};preimages={}
def text(relative):
    return pending.get(relative,(ROOT/relative).read_text(encoding='latin1'))
def stage(relative,content):
    path=ROOT/relative
    preimages.setdefault(relative,hashlib.sha256(path.read_bytes()).hexdigest()if path.exists()else None)
    pending[relative]=content
def put(content,key,value):
    pattern=r'(?mi)^[ \t]*'+re.escape(key)+r'[ \t]*=[^\r\n]*'
    line=key+' = '+str(value)
    if re.search(pattern,content):
        content=re.sub(pattern,'',content)
    return content.rstrip()+'\n'+line+'\n'
@lru_cache(None)
def rawprops(name,chain=()):
    name=Path(name).stem.lower()
    if name in chain:raise ValueError('Include cycle: '+str(chain+(name,)))
    if name not in IDX:return {}
    content=IDX[name].read_text(encoding='latin1');values={}
    for inc in re.findall(r'(?mi)^[ \t]*#include\s+"([^\"]+)"',content):
        values.update(rawprops(inc,chain+(name,)))
    for key,value in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',content):
        values[key.lower()]=value.split('//')[0].strip()
    return values
def props(name):return {k:v.strip('"')for k,v in rawprops(name).items()}
def number(values,key,default=0):
    try:return float(values.get(key,str(default)).rstrip('fF;'))
    except ValueError:return default
def round5(value):return max(0,int(math.floor(value/5+.5))*5)
def flatten(name):return '\n'.join(k+' = '+v for k,v in rawprops(name).items())+'\n'
def tree(name,seen=()):
    if name in seen:raise ValueError('Tree include cycle')
    result={}
    for line in (ROOT/'techtree'/name).read_text(encoding='latin1').splitlines():
        line=line.split('//')[0].strip()
        if line.startswith('#include'):
            result.update(tree(line.split(None,1)[1].strip('"'),seen+(name,)));continue
        fields=line.split()
        if len(fields)>1 and fields[0].lower().endswith('.odf'):
            count=int(fields[1]);assert count<0 or count==len(fields)-2,(name,line)
            result[Path(fields[0]).stem.lower()]=(count,[Path(x).stem.lower()for x in fields[2:]])
    return result
TECH=tree('tech1.tt');PRODUCERS={}
for name in IDX:
    for key,value in props(name).items():
        if re.fullmatch(r'(?:secondary)?builditem\d+',key):
            PRODUCERS.setdefault(Path(value).stem.lower(),set()).add(name)
def has_own_research(weapon,race):
    queue=list(TECH.get(weapon,(0,[]))[1]);seen=set();found=False
    while queue:
        name=queue.pop()
        if name in seen:continue
        seen.add(name);v=props(name)
        if v.get('classlabel','').lower()in {'pod','researchpod'}:
            if v.get('race','').lower()!=race or not PRODUCERS.get(name):return False
            found=True
        queue.extend(TECH.get(name,(0,[]))[1])
    return found
ships={name:props(name)for name,p in IDX.items()if p.parent.name.lower()=='ships'
       and props(name).get('race','').lower()in FACTIONS and props(name).get('unitname')}
uses={};audit=[]
for name,v in ships.items():
    for key,w in v.items():
        if re.fullmatch(r'weapon\d+',key)and number(props(w),'special')==1:
            w=w.lower();race=v['race'].lower()
            if w in UTILITY:status='basic utility retained'
            elif TECH.get(w,(0,[]))[0]<0:status='already disabled'
            elif has_own_research(w,race):status='existing faction research retained'
            else:status='research required';uses.setdefault((w,race),[]).append((name,key))
            audit.append({'ship':name,'weapon':w,'race':race,'status':status})

sprite_path='Sprites/gui_global.spr';sprite=text(sprite_path);new_sprites=[]
sprite_documents=[sprite]+[p.read_text(encoding='latin1')for p in(ROOT/'Sprites').glob('*.spr')if p.name.lower()!='gui_global.spr']
def copy_button(source,destination):
    for document in sprite_documents:
        matches=list(re.finditer(r'(?mi)^'+re.escape('b_'+source)+r'[ \t]+[^\r\n]+',document))
        if not matches:continue
        m=matches[-1];refs=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',document[:m.start()])
        new_sprites.append('\n@reference='+ (refs[-1]if refs else'64')+'\n@tmaterial=default\n'+re.sub(r'^\S+','b_'+destination,m[0])+'\n')
        return
    if props(source).get('classlabel','').lower()=='detectcloak' and number(props(source),'buttonslot')==0:
        return  # Native passive detector has no manual HUD button.
    raise ValueError('Missing original button '+source)

sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class SodReader(SodIO):
    def read_unknown_legacy_data(self,stream):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(stream)
sods={p.stem.lower():p for p in(ROOT/'SOD').glob('*.sod')}
research={};gates={};aliases=[]
for race in sorted({race for _,race in uses}):
    code,facility,attachment=FACTIONS[race];v=props(facility)
    items=sorted((int(k[9:]),x)for k,x in v.items()if re.fullmatch(r'builditem\d+',k))
    assert [i for i,_ in items]==list(range(len(items))) and len(items)<13
    template=items[0][1]if items else'yabrpolpod';pod='z21'+code+'spec'
    assert pod not in IDX,'Patch already installed'
    model=sods[v.get('basename',facility).lower()]
    with contextlib.redirect_stdout(io.StringIO()):nodes=SodReader().read_file(str(model)).nodes
    assert attachment in {n['id'].lower()for n in nodes}
    hardpoints=re.findall(r'[A-Za-z_]+\d+',v.get('podhardpoints',''))
    assert len(hardpoints)==len(items) and attachment not in hardpoints,(facility,hardpoints)
    content=text(IDX[facility].relative_to(ROOT).as_posix())
    content=put(content,'buildItem'+str(len(items)),'"'+pod+'"')
    content=put(content,'podHardpoints',' '.join('"'+x+'"'for x in hardpoints+[attachment]))
    stage(IDX[facility].relative_to(ROOT).as_posix(),content)
    content=flatten(template)
    title='Special Systems Research'
    values={'baseName':'"'+props(template).get('basename',template)+'"','race':'"'+race+'"',
      'unitName':'"'+title+'"','tooltip':'"'+title+'"',
      'verboseTooltip':'"Unlocks additional faction abilities, including cloak, detection and emergency systems where fitted."',
      'hotkeyLabel':'"HOTKEY_F'+str(len(items)+1)+'"','crewCost':0,'officerCost':1,'buildTime':160,
      'dilithiumCost':0 if race=='species8472'else 400,'metalCost':0 if race=='species8472'else 200,
      'latinumCost':0,'biomatterCost':600 if race=='species8472'else 0}
    for k,value in values.items():content=put(content,k,value)
    stage('odf/stations/'+pod+'.odf',content);copy_button(template,pod)
    gates[pod]='1 '+facility+'.odf'
    research[race]={'pod':pod,'facility':facility,'attachment':attachment,'abilityDefinitions':[]}
for (weapon,race),locations in sorted(uses.items()):
    same_races={v['race'].lower()for v in ships.values()if any(k.startswith('weapon')and x.lower()==weapon for k,x in v.items())}
    alias=weapon
    if len(same_races)>1:
        alias='z21'+FACTIONS[race][0]+hashlib.sha1(weapon.encode()).hexdigest()[:6]
        stage('odf/weapons/Other/'+alias+'.odf',flatten(weapon));copy_button(weapon,alias)
        for name,key in locations:
            rel=IDX[name].relative_to(ROOT).as_posix()
            stage(rel,put(text(rel),key,'"'+alias+'"'))
        aliases.append({'original':weapon,'alias':alias,'race':race})
    gates[alias]='1 '+research[race]['pod']+'.odf'
    research[race]['abilityDefinitions'].append(alias)

for row in audit:
    if row['status']=='existing faction research retained':
        count,requirements=TECH[row['weapon']]
        gates.setdefault(row['weapon'],str(count)+' '+ ' '.join(x+'.odf'for x in requirements))

# Apply normal research rules; the explicit full-tech/free-tech presets stay unlocked.
for name in ['tech1.tt','earlytech.tt','nosci.tt','nosuper.tt','nospweap.tt','fulltech.tt','freetech.tt']:
    rel='techtree/'+name;content=text(rel)
    for item,gate in gates.items():
        actual='0'if name in ['fulltech.tt','freetech.tt']else'-1'if name=='nospweap.tt'else gate
        content=re.sub(r'(?mi)^'+re.escape(item)+r'\.odf\s+[^\r\n]*','',content)
        content+='\n'+item+'.odf '+actual+' // Faction special systems research\n'
    stage(rel,content)
if new_sprites:stage(sprite_path,sprite+''.join(new_sprites))

# Research in each local-game AI profile after its producing facility is scheduled.
ai_changes=[]
for race,info in research.items():
    for path in (ROOT/'AI/AIPs').glob(race+'*.aip'):
        content=path.read_text(encoding='latin1')
        pattern=r'(?mi)^([ \t]*)"'+re.escape(info['facility'])+r'"[^\r\n]*'
        m=re.search(pattern,content)
        if not m:continue
        line='\n'+m[1]+'"'+info['pod']+'", 1, 0, -1, 0, // Additional special ability research'
        content=content[:m.end()]+line+content[m.end():]
        stage(path.relative_to(ROOT).as_posix(),content);ai_changes.append(path.name)

def power(name):
    v=props(name);dps=0;ranges=[];abilities=0
    for key,w in v.items():
        if not re.fullmatch(r'weapon\d+',key):continue
        a=props(w)
        if number(a,'special')==1:
            if w.lower()not in UTILITY:abilities+=1
            continue
        o=props(a.get('ordname',''));damage=number(a,'damagebase',number(o,'damagebase'))
        delay=number(a,'shotdelay');chance=max(.1,min(1,number(a,'hitchance',number(o,'hitchance',1))))
        if damage>0 and delay>0:
            # maxShots is burst length, not simultaneous barrels; count weapon slots.
            dps+=damage/max(delay,.15)*chance;ranges.append(number(a,'range',500))
    return {'durability':max(1,number(v,'maxhealth')+15*number(v,'shieldrate')),
            'dps':dps,'range':sum(ranges)/len(ranges)if ranges else 500,'abilities':abilities}
ref=power('fbattle');assert ref['dps']>0
def combat_score(name):
    v=props(name);p=power(name);role=v.get('shipclass','').lower()
    fallback={'scout':.15,'destroyer':.4,'frigate':.6,'cruiser':.8,'battleship':1,'special':.5,'assault':.65}.get(role,.6)
    dps=p['dps']or ref['dps']*fallback
    score=(p['durability']/ref['durability'])**.55*(dps/ref['dps'])**.45
    score*=max(.9,min(1.15,(p['range']/ref['range'])**.2))
    score*=(1+.04*min(p['abilities'],6))/(1+.04*min(ref['abilities'],6))
    return score,p
borg_score,_=combat_score('bbattle1');prices=[]
for name,v in ships.items():
    role=v.get('shipclass','').lower();race=v['race'].lower();cls=v.get('classlabel','').lower()
    old={k:number(v,k)for k in ['dilithiumcost','metalcost','latinumcost','biomattercost']}
    if name in {'q','zflag'}:continue  # Scripted encounter and victory helper, not fleet purchases.
    if not sum(old.values())and name not in PRODUCERS:continue
    score,power_stats=combat_score(name)
    if role=='construction'or cls in ['constructionrig','evolver']:dil,metal=125,25;category='constructor'
    elif role in ['mining','cargo','colony','repair']:
        dil,metal={'mining':(175,75),'cargo':(200,100),'colony':(250,100),'repair':(250,150)}[role];category=role
    else:
        total=max(75,round5(550*score))
        fraction={'scout':0,'destroyer':.2,'frigate':.25,'cruiser':.25,'battleship':.3,'special':.25,'assault':.25}.get(role,.25)
        if race=='borg':total=max(75,round5(700*score/borg_score));fraction=150/700
        metal=round5(total*fraction);dil=total-metal;category='combat '+(role or'craft')
    new={'dilithiumcost':0 if race=='species8472'else dil,'metalcost':0 if race=='species8472'else metal,
         'latinumcost':0,'biomattercost':dil+metal if race=='species8472'else 0}
    rel=IDX[name].relative_to(ROOT).as_posix();content=text(rel)
    for key,value in new.items():content=put(content,key,value)
    old_crew=int(number(v,'crewcost'))
    if race=='species8472' or old_crew==0:crew=0
    elif role=='construction'or cls in ['constructionrig','evolver']:crew=150 if race=='borg'else 100
    elif role in ['mining','cargo','colony','repair']:crew={'mining':100,'cargo':100,'colony':100,'repair':50}[role]
    elif race=='borg':crew=150 if role=='scout'else max(150,round5(800*math.sqrt(score/borg_score)))
    else:
        complement,expected_power={'scout':(25,.1),'destroyer':(100,.5),'frigate':(180,.65),
          'cruiser':(250,.85),'battleship':(700,1),'special':(150,.6),'assault':(250,.7)}.get(role,(250,.7))
        crew=max(10,round5(complement*math.sqrt(score/expected_power)))
    # Explicit crew capacities remain intact; an omitted maximum follows the native crewCost default.
    if 'maximumcrew'in v:crew=min(crew,int(number(v,'maximumcrew')))
    content=put(content,'crewCost',crew)
    changed=old!=new or old_crew!=crew
    if changed:stage(rel,content)
    prices.append({'ship':name,'name':v['unitname'],'race':race,'category':category,'before':old,'after':new,
      'oldCrewCost':old_crew,'newCrewCost':crew,'changed':changed,'nominalPower':power_stats})
platforms=[]
for name in sorted(HEAVY):
    v=props(name);rel=IDX[name].relative_to(ROOT).as_posix();content=text(rel)
    officers=int(number(v,'officercost'));assert officers>0
    for key,value in {'crewCost':0,'maximumCrew':0,'officerCost':2*officers}.items():content=put(content,key,value)
    stage(rel,content);platforms.append({'unit':name,'oldCrew':number(v,'crewcost'),'oldMaximumCrew':number(v,'maximumcrew'),'oldOfficers':officers,'crew':0,'maximumCrew':0,'officers':2*officers})

manifest=[]
for relative,content in sorted(pending.items()):
    path=PACKAGE/'overlay'/relative;path.parent.mkdir(parents=True,exist_ok=True)
    data=content.replace('\r','').replace('\n','\r\n').encode('latin1');path.write_bytes(data)
    manifest.append({'file':relative,'beforeSha256':preimages[relative],'afterSha256':hashlib.sha256(data).hexdigest()})
report={'target':str(ROOT),'installed':False,'runtimeVerified':False,'shipsAudited':len(ships),
 'specialSlotAudit':audit,'research':research,'weaponAliases':aliases,'aiProfilesUpdated':ai_changes,
 'prices':prices,'platforms':platforms,'files':manifest,'backup':str(BACKUP),
 'rules':'Normal research tech modes gate combat/special systems; basic mining/repair/tractor/colony equipment is exempt. Full/free tech presets remain unlocked. Campaign trees unchanged. Ship prices use nominal durability/DPS/role; maxShots is not multiplied into sustained DPS. Sovereign total550 and crew700, original basic Cube550 dilithium/150 metal and crew800 are anchors. Combat crew follows sqrt relative power; utility roles use fixed complements, Borg scouts150; explicit maximumCrew and crewless biology retained. Ship officer costs/build times unchanged; seven heavy platforms lose crew and double officers.'}
(PACKAGE/'manifest.json').write_text(json.dumps(report,indent=2))
out=io.StringIO();writer=csv.writer(out);writer.writerow(['Ship','Faction','Old dil','Old metal','Old biomatter','New dil','New metal','New biomatter','Old crew','New crew'])
for row in prices:writer.writerow([row['ship'],row['race']]+[row['before'][k]for k in ['dilithiumcost','metalcost','biomattercost']]+[row['after'][k]for k in ['dilithiumcost','metalcost','biomattercost']]+[row['oldCrewCost'],row['newCrewCost']])
(PACKAGE/'ship-prices.csv').write_bytes(out.getvalue().encode('utf-8'))
if '--apply'in sys.argv:
    running=subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True)
    assert int(running.strip())==0,'Game must be closed'
    for row in manifest:
        path=ROOT/row['file'];current=hashlib.sha256(path.read_bytes()).hexdigest()if path.exists()else None
        assert current==row['beforeSha256'],'Changed during staging: '+row['file']
    for row in manifest:
        relative=row['file'];path=ROOT/relative
        if path.exists():
            saved=BACKUP/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved);path.chmod(0o666)
        path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PACKAGE/'overlay'/relative,path)
        mirror=REPO/'bajor/overlay'/relative;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,mirror)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['afterSha256']
    report['installed']=True;(PACKAGE/'manifest.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'target':str(ROOT),'stagedFiles':len(manifest),'shipsAudited':len(ships),'pricesChanged':sum(p['changed']for p in prices),'newResearchPods':len(research),'researchAbilityPairsFixed':len(uses),'heavyPlatforms':len(platforms),'installed':report['installed']}))
