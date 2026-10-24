from pathlib import Path
# Load established parsers and icon helpers, without executing earlier patches.
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
props=json.loads((repo/'reports/constructor-patch-before.json').read_text())
oldmirror=json.loads((repo/'reports/mirror-ferengi-research.json').read_text())
plan=json.loads((repo/'reports/constructor-tier-plan.json').read_text())
original=json.loads((repo/'reports/mirror-current-properties.json').read_text())
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
stage=Path('D:/Xaramada-Modwork/constructor-mirror-stage');stage.mkdir(parents=True,exist_ok=True)
backup=Path('D:/Xaramada-Modwork/backups')/('constructor-mirror-'+stamp)
pending={};binary={};techdefs={};icons=[];yards=[];research=[];constructors=[];starprices=[];aichanges=[]
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
def save(n,t,folder=None):
 rel=Path(props[n]['file']).relative_to(root).as_posix() if n in props else 'odf/'+(folder or 'ships')+'/'+n+'.odf'
 pending[rel]=t
def menu(t,items):
 assert len(items)<=14 and len(items)==len(set(items)),items
 t=re.sub(r'(?mi)^\s*(?:secondary)?buildItem\d+\s*=[^\r\n]*','',t)
 for i,n in enumerate(items):t=put(t,'buildItem'+str(i),q(n))
 return t
def cropbutton(n):
 key='b_'+n;m=re.search(r'(?mi)^'+re.escape(key)+r'[ \t]+([^\r\n]+)',sprite);assert m,('button',n)
 part=m[1].split();tex=part[0];data=binary.get('Textures/RGB/'+tex+'.tga')
 im=Image.open(io.BytesIO(data)if data else texidx[tex.lower()]).convert('RGB')
 ref=int(re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:m.start()])[-1]);x,y,w,h=[float(v)*im.width/ref for v in part[1:5]]
 return im.crop((round(x),round(y),round(x+w),round(y+h))).resize((128,128))
def badge(n,donor,label,color=(100,210,255)):
 global sprite
 if donor not in index and not any(rel.lower().endswith('/'+donor+'.odf')for rel in pending):
  for suffix in ['button',1,2,3,4,5]:
   sourcekey='b_'+donor if suffix=='button'else donor+'w'+str(suffix);targetkey='b_'+n if suffix=='button'else n+'w'+str(suffix)
   found=re.search(r'(?mi)^'+re.escape(sourcekey)+r'[ \t]+[^\r\n]+',sprite);assert found,sourcekey
   ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:found.start()])[-1];line=re.sub(r'^\S+',targetkey,found[0]);sprite=re.sub(r'(?mi)^'+re.escape(targetkey)+r'[ \t]+[^\r\n]*','',sprite);sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+line+'\n'
 else:aliasgui(n,donor)
 im=cropbutton(n);d=ImageDraw.Draw(im);d.rectangle((0,94,127,127),fill=(7,10,18));font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23);d.text((5,96),label,font=font,fill=color)
 tex='gb'+n;binary['Textures/RGB/'+tex+'.tga']=imgbytes(im.resize((64,64),Image.Resampling.LANCZOS));texidx[tex]=stage/'Textures/RGB'/(tex+'.tga')
 sprite=re.sub(r'(?mi)^b_'+re.escape(n)+r'[ \t]+[^\r\n]*','',sprite);sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+tex+' 0 0 64 64\n';icons.append(n)
def native_model(n):
 modelname=resolve(n).get('basename',n);path=root/'SOD'/(modelname+'.sod')
 try:return load(path)
 except Exception:
  with contextlib.redirect_stdout(io.StringIO()):return SodIO().read_file(str(path))
def appenditem(n,item):
 d=resolve(n);items=[v.lower()for k,v in sorted(d.items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1)if re.fullmatch('builditem[0-9]+',k)]
 if item not in items:items.append(item)
 save(n,menu(text(n),items))
def clear_summon(n):
 d=resolve(n);banks=sorted((int(k[6:]),v)for k,v in d.items()if re.fullmatch('weapon[0-9]+',k));t=stripbanks(text(n))
 for i,(j,w)in enumerate([(j,w)for j,w in banks if not re.fullmatch('mra[0-9]+',w,re.I)],1):
  t=put(t,'weapon'+str(i),q(w));t=put(t,'weaponHardpoints'+str(i),q(d.get('weaponhardpoints'+str(j),'hp01')))
 base=original.get(n)or original.get('xfg'+n[3:]if n.startswith('xbg')else n)
 if base:
  for key in ['maxspecialenergy','specialenergyrate']:
   if key in base:t=put(t,key,base[key])
 save(n,t)
for row in oldmirror['heroes']:clear_summon(row['hero'])
# Remove obsolete mirror research from every station, retaining other pods.
removedresearch=[]
for n,d in props.items():
 items=sorted((int(k[9:]),v)for k,v in d.items()if re.fullmatch('builditem[0-9]+',k))
 if any(v.lower().startswith('mrp')for _,v in items):
  save(n,menu(text(n),[v for _,v in items if not v.lower().startswith('mrp')]));removedresearch.append(n)

templates={'federation':'fyard3','borg':'byard3','klingon':'kyard2','romulan':'ryard2','cardassian':'cyard3','dominion':'dyard3','breen':'bryard','bajoran':'bjyard3','species8472':'8472_fluidicgate','ferengi':'xfgmerc'}
firstyards={'federation':'fyard','borg':'byard','klingon':'kyard','romulan':'ryard','cardassian':'cyard','dominion':'dyard','breen':'bryard','bajoran':'bjyard','species8472':'8472_fluidicgate','ferengi':'xfgmerc','borg_ferengi':'xbgmerc'}
yard2={'federation':'fyard2','borg':'byard2','klingon':'kyard2','romulan':'ryard2','cardassian':'cyard2','dominion':'dyard2','breen':'bryard2','bajoran':'bjyard2','species8472':'8472_advancedresearch','ferengi':'xfgmerc','borg_ferengi':'xbgmerc'}
yardids={'federation':['mryfeda','mryfedb'],'borg':['mryborg'],'klingon':['mrykling'],'romulan':['mryrom'],'cardassian':['mrycard'],'dominion':['mrydom'],'breen':['mrybreen'],'bajoran':['mrybajor'],'species8472':['mry8472'],'ferengi':['mryfer']}
for race,ids in yardids.items():
 mirrors=[r for r in oldmirror['heroes']if r['faction']==race]
 for j,n in enumerate(ids):
  entries=mirrors[j*12:(j+1)*12];assert entries
  donor=templates[race];d=resolve(donor);modelname=d.get('basename',donor)
  binary['SOD/'+n+'.sod']=(root/'SOD'/(modelname+'.sod')).read_bytes()
  title=race.title()+' Mirror Universe Yard'+(' '+str(j+1)if len(ids)>1 else'')
  cost={'dilithiumCost':600,'metalCost':400,'latinumCost':0,'biomatterCost':0}
  if race=='ferengi':cost.update(dilithiumCost=0,metalCost=0,latinumCost=1000)
  if race=='species8472':cost.update(dilithiumCost=0,metalCost=0,biomatterCost=1000)
  t=menu(text(donor),[r['clone']for r in entries]);t=update(t,dict(cost,baseName=q(n),unitName=q(title),tooltip=q(title),verboseTooltip=q('Builds controllable Mirror Universe counterparts. Double normal weapon damage, 75 percent original durability and 125 percent original size. No summoning research is required.'),buildTime=100,crewCost=150,maximumCrew=max(150,int(num(d.get('maximumcrew',150)))),hotkeyLabel=q('HOTKEY_F'+str(7+j))))
  if race=='species8472':t=update(t,{'crewCost':0,'maximumCrew':0})
  save(n,t,'stations');badge(n,donor,'MIR '+str(j+1),(210,150,255));techdefs[n]=[yard2[race]]
  for i,row in enumerate(entries):
   clone=row['clone'];hd=resolve(row['hero']);t=text(clone)
   oldmodel=resolve(clone).get('basename',clone);binary['SOD/'+clone+'.sod']=(root/'SOD'/(oldmodel+'.sod')).read_bytes();t=put(t,'baseName',q(clone))
   values={k:int(round(num(hd.get(k.lower(),0))*1.25))for k in ['dilithiumCost','metalCost','latinumCost','biomatterCost','buildTime']}
   t=update(t,dict(values,hotkeyLabel=q('HOTKEY_F'+str(i+1)),verboseTooltip=q('Mirror Universe counterpart: double normal weapon damage, 75 percent original durability and 125 percent original size. Built and commanded as a normal player-owned ship.')))
   save(clone,t);techdefs[clone]=[n];badge(clone,clone,'MIR',(210,150,255))
  yards.append({'faction':race,'yard':n,'ships':[r['clone']for r in entries],'template':donor})
 print('Prepared mirror yards:',race,flush=True)

# Two resource tiers unlock equipment variants; existing units are not upgraded.
# Plain research pods occupy separate native anchors, with explicit tier-I prerequisites.
fm=native_model('xfgserv');anchors=[z['id']for z in fm.nodes if re.fullmatch(r'hp\d+',z['id'],re.I)];assert len(anchors)>=6
for prefix,race,resources in [('xfg','ferengi',['dil','met','lat']),('xbg','borg',['dil','met'])]:
 station=prefix+'research';pods=[]
 for level,mult in [(1,1.5),(2,2.0)]:
  for rsrc in resources:
   podid=prefix+'p'+rsrc+('2'if level==2 else'');pods.append(podid);donor=prefix+'p'+rsrc
   title={'dil':'Dilithium','met':'Metal','lat':'Latinum'}[rsrc]+' Contracts '+('I'if level==1 else'II')+' (+'+str(int((mult-1)*100))+'%)'
   cost=900 if level==1 else 1350;v={'unitName':q(title),'tooltip':q(title),'verboseTooltip':q('Unlocks new resource equipment at '+str(int(mult*100))+' percent of the base Ferengi extraction rate. Existing equipment is unchanged.'),'hotkeyLabel':q('HOTKEY_F'+str(len(pods))),'buildTime':90 if level==1 else 135,'latinumCost':cost if prefix=='xfg'else 0,'dilithiumCost':round(cost*.6)if prefix=='xbg'else 0,'metalCost':round(cost*.4)if prefix=='xbg'else 0}
   save(podid,update(text(donor),v),'stations');techdefs[podid]=[station]+([donor]if level==2 else[]);badge(podid,'carpod7',rsrc.upper()+' '+str(level));research.append({'pod':podid,'multiplier':mult,'resource':rsrc,'faction':race})
   if level==1:continue
   n=prefix+('metal3'if rsrc=='met'else rsrc+'3');old=prefix+('metal2'if rsrc=='met'else rsrc+'2');t=text(old)
   t=update(t,{'unitName':q('Mercenary Ferengi '+{'dil':'Dilithium Collector II','met':'Metal Orbital II','lat':'Latinum Collector II'}[rsrc]),'tooltip':q('Ferengi '+rsrc.title()+' Equipment II'),'verboseTooltip':q('Tier-II resource equipment: twice the base Ferengi extraction rate. Research required.'),'latinumCost':500 if prefix=='xfg'else 0,'dilithiumCost':300 if prefix=='xbg'else 0,'metalCost':200 if prefix=='xbg'else 0})
   if rsrc=='met':t=put(t,'miningMultiplier',1.2)
   else:
    wn='xfgmin'+rsrc+'3';on=wn+'o';source='gmineDilithium'if rsrc=='dil'else'gmineLatinum';ordsource='mineDilithium'if rsrc=='dil'else'mineLatinum'
    save(wn,put(text(source),'ordName',q(on)),'special_weapons');save(on,put(text(ordsource),'damageBase',60),'special_weapons');techdefs[wn]=[]
    t=put(t,'weapon1',q(wn))
   save(n,t,'stations'if rsrc=='met'else'ships');badge(n,old,rsrc.upper()+' II');techdefs[n]=[podid]
   if rsrc!='met':appenditem(prefix+'serv',n)
  
 save(station,update(menu(text(station),pods),{'podHardpoints':' '.join(q(a)for a in anchors[:len(pods)]),'verboseTooltip':q('Two tiers of resource equipment contracts: +50 percent and +100 percent extraction. Research unlocks new equipment; existing collectors are unchanged.')}))

# Import Chiletrek's model under unique names: no native station is overwritten.
source=Path('D:/Xaramada-Modwork/8472-resource-research/payload/8472_Stations');alltex={f.stem.lower():f for f in source.rglob('*.tga')}
n='xsbiolab';m=model(n,source/'SOD/8472_BasicResearch.sod');hps=[z['id']for z in m.nodes if re.fullmatch(r'hp\d+',z['id'],re.I)];assert len(hps)>=2
base=text('8472_basicresearch');t=menu(base,['xsbio1','xsbio2']);t=update(t,{'baseName':q(n),'unitName':q('Biomatter Metabolism Institute'),'tooltip':q('Biomatter Metabolism Institute'),'verboseTooltip':q('Researches two tiers of biomatter extraction equipment. No Ferengi technology or other resource upgrades.'),'biomatterCost':750,'dilithiumCost':0,'metalCost':0,'latinumCost':0,'buildTime':100,'podHardpoints':' '.join(q(a)for a in hps[:2]),'ScaleSOD':1,'hotkeyLabel':q('HOTKEY_F9')})
for key in ['engines','lifeSupport','weapons','shieldGenerator','sensors','hull','critical']:t=put(t,key+'TargetHardpoints',' '.join(q(a)for a in hps[2:7]))
save(n,t,'stations');icon(n,m);badge(n,n,'BIO');techdefs[n]=['8472_basicresearch']
for level,mult in [(1,1.5),(2,2)]:
 podid='xsbio'+str(level);podmodel='xsbpod'+str(level);pm=model(podmodel,source/'SOD'/('8472_PodBasic'+str(level-1)+'.sod'));icon(podmodel,pm)
 title='Biomatter Extraction '+('I'if level==1 else'II')+' (+'+str(int((mult-1)*100))+'%)'
 t=update('#include "pod.odf"\n',{'baseName':q(podmodel),'race':q('species8472'),'unitName':q(title),'tooltip':q(title),'verboseTooltip':q('Unlocks an enhanced Collector with '+str(int(mult*100))+' percent of the base biomatter extraction rate. Existing collectors are unchanged.'),'biomatterCost':900 if level==1 else 1350,'dilithiumCost':0,'metalCost':0,'latinumCost':0,'crewCost':0,'officerCost':1,'buildTime':90 if level==1 else 135,'ScaleSOD':.6,'hotkeyLabel':q('HOTKEY_F'+str(level))})
 save(podid,t,'stations');badge(podid,podmodel,'BIO '+str(level));techdefs[podid]=[n]+(['xsbio1']if level==2 else[])
 collector='xsbcol'+str(level);d=resolve('8472_collector');t=text('8472_collector')
 for k,w in d.items():
  if not re.fullmatch('weapon[0-9]+',k):continue
  if w.lower()not in ['gminemetalborg','gresourceextractionbeam']:continue
  wn='xsb'+('orb'if w.lower()=='gminemetalborg'else'ext')+str(level);on=wn+'o';wd=resolve(w);od=resolve(wd['ordname'].lower());o=text(wd['ordname'].lower())
  # minebm damage is resource yield; extraction conversion is biomass per drained HP.
  key='damageBase'if w.lower()=='gminemetalborg'else'conversionRate';o=put(o,key,num(od[key.lower()])*mult)
  save(on,o,'special_weapons');save(wn,put(text(w.lower()),'ordName',q(on)),'special_weapons');techdefs[wn]=[]
  found=re.search(r'(?mi)^b_'+re.escape(w)+r'[ \t]+[^\r\n]+',sprite)
  if found:
   ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:found.start()])[-1];sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+','b_'+wn,found[0])+'\n'
  t=put(t,k,q(wn))
 t=update(t,{'unitName':q('Biomatter Collector '+('I'if level==1 else'II')),'tooltip':q('Biomatter Collector '+str(level)),'verboseTooltip':q('Improved biomatter extraction only: +'+str(int((mult-1)*100))+' percent. Other resource beams and capacity are unchanged.'),'biomatterCost':350 if level==1 else 450,'hotkeyLabel':q('HOTKEY_F'+str(6+level))})
 t=put(t,'baseName',q(d.get('basename','8472_collector')));save(collector,t,'ships');badge(collector,'8472_collector','BIO '+str(level));techdefs[collector]=[podid];appenditem('8472_active',collector);research.append({'pod':podid,'multiplier':mult,'resource':'biomatter','faction':'species8472'})
binary['Credits/8472 Resource Research - Chiletrek.txt']=(source/'Read me.txt').read_bytes()

# Constructor plan approved by the user. Retain legacy filenames as role aliases.
baseids={'federation':'fbase','borg':'bbase','klingon':'kbase','romulan':'rbase','cardassian':'cbase','dominion':'dbase','breen':'brbase','bajoran':'bjbase','species8472':'8472_mothership','ferengi':'xfgserv','borg_ferengi':'xbgserv'}
canonical={};aliases={};newmenus={};tierof={};raceof={}
for group in plan['factions']:
 race=group['faction'];items=group['proposed']
 if race=='species8472':next(b for b in items if b['tier']==1)['buildings'].append('xsbiolab')
 for b in items:
  n=b['constructor'];tier=b['tier'];buildings=b['buildings'];canonical.setdefault(race,{})[tier]=canonical.setdefault(race,{}).get(tier,n)
  donor=n if n in props else ('714const'if race=='species8472'else group['oldConstructors'][0])
  if race=='cardassian'and n=='xcconst2':donor='cconst'
  if race=='dominion'and n=='xdconst2':donor='dconst'
  if race=='breen'and n=='xbrconst2':donor='brconst'
  if race=='bajoran'and n=='xbjconst2':donor='bjconst'
  if tier==3 and n not in props:donor=canonical[race].get(3,group['oldConstructors'][-1]);donor=donor if donor in props else group['oldConstructors'][-1]
  d=resolve(donor);t=menu(text(donor),buildings);title=race.replace('_',' ').title()+' '+{1:'Constructor I',2:'Constructor II',3:'Universal Constructor III'}[tier]+(' - Specialist'if re.fullmatch('xu3.*',n)else'')
  cost={1:(125,25,150,20),2:(200,100,150,30),3:(300,200,150,40)}[tier];dil,met,crew,time=cost
  values={'unitName':q(title),'tooltip':q(title),'verboseTooltip':q('Tier '+str(tier)+': '+{1:'mining, regular yards, research and upgrade facilities.',2:'defenses and hero, Omega and Mirror Universe yards.',3:'starbases, special installations and Ferengi facilities.'}[tier]),'baseName':q(d.get('basename',donor)),'dilithiumCost':dil,'metalCost':met,'latinumCost':0,'biomatterCost':0,'crewCost':crew,'maximumCrew':max(crew,int(num(d.get('maximumcrew',crew)))),'buildTime':time,'hotkeyLabel':q('HOTKEY_F'+str(tier)),'canAttack':0,'maxSpecialEnergy':0,'specialEnergyRate':0}
  if race in ['ferengi','borg_ferengi']:
   values.update(dilithiumCost=0 if race=='ferengi'else 300,metalCost=0 if race=='ferengi'else 200,latinumCost=500 if race=='ferengi'else 0)
  if race=='species8472':values.update(dilithiumCost=0,metalCost=0,biomatterCost=150 if tier==1 else 300 if tier==2 else 500,crewCost=0,maximumCrew=d.get('maximumcrew',0))
  oldmodel=d.get('basename',donor);binary['SOD/'+n+'.sod']=binary.get('SOD/'+oldmodel+'.sod')or(root/'SOD'/(oldmodel+'.sod')).read_bytes();values['baseName']=q(n)
  t=update(stripbanks(t),values);save(n,t,'ships');badge(n,donor,'T'+str(tier),(255,215,100));techdefs[n]=[]if tier==1 or race in ['ferengi','borg_ferengi']else[firstyards[race]if tier==2 else yard2[race]]
  constructors.append({'unit':n,'race':race,'tier':tier,'buildings':buildings,'costs':values});newmenus[n]=buildings;tierof[n]=tier;raceof[n]=race
 for legacy in group['oldConstructors']:
  if legacy in newmenus:continue
  level=2 if legacy in ['f31const','domconst','8472_defender']else 1 if legacy=='xcdconst'else 3
  target=canonical[race][level];aliases[legacy]=target
  # Preserve the native legacy model and its animation/sound properties.
  d=resolve(legacy);oldmodel=d.get('basename',legacy);binary['SOD/'+legacy+'.sod']=binary.get('SOD/'+oldmodel+'.sod')or(root/'SOD'/(oldmodel+'.sod')).read_bytes();t=menu(stripbanks(text(legacy)),newmenus[target]);td=resolve(target)
  for key in ['unitname','tooltip','verbosetooltip','dilithiumcost','metalcost','latinumcost','biomattercost','crewcost','buildtime','canattack','maxspecialenergy','specialenergyrate']:
   t=put(t,key,q(td[key])if key in ['unitname','tooltip','verbosetooltip']else td[key])
  t=put(t,'baseName',q(legacy));save(legacy,t);badge(legacy,legacy,'T'+str(level),(255,215,100));techdefs[legacy]=techdefs[target]
 # Production menus replace old constructor options while retaining other units.
 owned=set(group['oldConstructors']);options=[b['constructor']for b in items]
 producers=[n for n,d in props.items()if any(v.lower()in owned for k,v in d.items()if re.fullmatch('builditem[0-9]+',k))]
 if baseids[race]not in producers:producers.append(baseids[race])
 for producer in producers:
  rd=resolve(producer);existing=[v.lower()for k,v in sorted(rd.items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1)if re.fullmatch('builditem[0-9]+',k)]
  result=[]
  for u in existing:
   if u in owned:
    if not any(x in result for x in options):result+=options
   elif u not in result:result.append(u)
  if not any(x in result for x in options):result=options+result
  # Some minor outposts have limited existing menus: one complete role set fits.
  save(producer,menu(text(producer),result))
 print('Prepared constructors:',race,flush=True)

# Strategic starbases only: omit heavy platforms and ships using class starbase.
excluded=set('bhwp bjhwp chwp dturret3 fhwp khwp rhwp fbyard cquantum xbtarray xhs_yard3'.split())
for n,d in props.items():
 if d.get('classlabel','').lower()!='starbase'or n in excluded:continue
 if '/stations/'not in d.get('file','').replace('\\','/').lower():continue
 if d.get('race')=='species8472':starprices.append({'unit':n,'biomatterRetained':True});continue
 t=update(text(n),{'dilithiumCost':1500,'metalCost':1500,'latinumCost':0,'biomatterCost':0,'crewCost':150});save(n,t);starprices.append({'unit':n,'dilithium':1500,'metal':1500,'crew':150,'maxCrewUnchanged':d.get('maximumcrew')})

# Disable removed summon definitions in every tree, and add all new producer gates.
obsolete={r['ability']for r in oldmirror['heroes']}|{r['ability']+'o'for r in oldmirror['heroes']}|{r['research']for r in oldmirror['heroes']}
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';t=(root/rel).read_text(encoding='latin1')
 for n in obsolete|set(techdefs):t=re.sub(r'(?mi)^\s*'+re.escape(n)+r'\.odf\s+[^\r\n]*','',t)
 for n in sorted(obsolete):t+='\n'+n+'.odf -1\n'
 for n,deps in techdefs.items():
  deps=[]if tree=='fulltech'else deps;t+='\n'+n+'.odf '+str(len(deps))+''.join(' '+v+'.odf'for v in deps)+'\n'
 pending[rel]=t

# Rewrite constructor ordering in every faction skirmish build-list variant.
allbuilders=set(tierof)|set(aliases);buildowner={}
for c in constructors:
 for n in c['buildings']:buildowner.setdefault(c['race'],{})[n]=c['unit']
for f in(root/'AI/AIPs').glob('*.aip'):
 race=next((r for r in canonical if f.name.lower().startswith(r+'_')),None)
 if not race or race in ['ferengi','borg_ferengi']:continue
 t=f.read_text(encoding='latin1')
 if 'the_build_list'not in t:continue
 lines=t.splitlines();start=next((i for i,s in enumerate(lines)if re.match(r'^\s*\{',s)),None);end=next((i for i,s in enumerate(lines)if re.match(r'^\s*\};',s)),None)
 if start is None or end is None:continue
 rows=lines[start+1:end];out=[];built=set();inserted=[]
 def add(n,count=1):
  if n in built:return
  # Explicit tech prerequisites for this patch are built before use.
  for dep in techdefs.get(n,[]):
   if dep not in built and dep!=n:add(dep)
  owner=buildowner.get(race,{}).get(n)
  if owner and owner not in built and owner!=n:add(owner)
  out.append('    "'+n+'", '+str(count)+', 0, -1, 0, // A3 tier, resource and mirror integration');built.add(n);inserted.append(n)
 for line in rows:
  mt=re.match(r'^\s*"([^\"]+)"\s*,',line)
  if not mt:out.append(line);continue
  n=mt[1].lower()
  if n in allbuilders:
   target=aliases.get(n,n)
   if raceof.get(target,race)!=race:out.append(line);built.add(n);continue
   if target not in built:add(target,2 if tierof.get(target)==1 else 1)
   continue
  owner=buildowner.get(race,{}).get(n)
  if owner and owner not in built:add(owner)
  out.append(line);built.add(n)
 # Every role, faction mirror yard and one mirror unit per yard.
 for c in constructors:
  if c['race']==race:add(c['unit'])
 for y in yards:
  if y['faction']==race:add(y['yard']);add(y['ships'][0])
 # Ferengi apply only to the factions already offered their contracts.
 if race in ['borg','klingon','romulan','cardassian','dominion','breen','bajoran']:
  pre='xbg'if race=='borg'else'xfg'
  for n in [pre+'merc',pre+'const',pre+'serv',pre+'research']+(['xu3fer2']if race!='borg'else[])+[pre+'pdil',pre+'pmet',pre+'pdil2',pre+'pmet2',pre+'dil3',pre+'metal3',pre+'fight',pre+'cruis',pre+'quark']:add(n)
  if race!='borg':
   for n in ['xfgplat','xfgplat2','xfglat3','xfgtrade','mryfer']:add(n)
   add(next(y['ships'][0]for y in yards if y['faction']=='ferengi'))
 if race=='species8472':
  for n in ['xsbiolab','xsbio1','xsbio2','xsbcol2']:add(n)
 result='\n'.join(lines[:start+1]+out+lines[end:])+'\n';count=len(re.findall(r'(?m)^\s*"[^\"]+"\s*,',result));assert count<=200,(f.name,count)
 pending[f.relative_to(root).as_posix()]=result;aichanges.append({'file':f.name,'entries':count,'inserted':inserted})
# Give new resource equipment/pods unique model aliases so baseName lookup cannot
# substitute another unit's build button. Preserve bytes and physical scales.
for rr in research:
 n=rr['pod'];d=resolve(n);old=d.get('basename',n)
 if old!=n:
  binary['SOD/'+n+'.sod']=binary.get('SOD/'+old+'.sod')or(root/'SOD'/(old+'.sod')).read_bytes();save(n,put(text(n),'baseName',q(n)))
for n in ['xfgdil3','xfglat3','xfgmetal3','xbgdil3','xbgmetal3','xsbcol1','xsbcol2']:
 d=resolve(n);old=d.get('basename',n);binary['SOD/'+n+'.sod']=binary.get('SOD/'+old+'.sod')or(root/'SOD'/(old+'.sod')).read_bytes();save(n,put(text(n),'baseName',q(n)))
for n in ['8472_heromother','kbekta']:
 if not re.search(r'(?mi)^b_'+re.escape(n)+r'[ \t]+',sprite):icon(n,native_model(n));icons.append(n)
# Transwarp is a non-combat utility and must survive constructor disarmament.
for rel in list(pending):
 if not rel.lower().endswith('.odf'):continue
 n=Path(rel).stem.lower();d=resolve(n)
 if d.get('race')=='borg'and d.get('classlabel','').lower()=='constructionrig':
  save(n,update(text(n),{'weapon1':q('xabtrans5'),'weaponHardpoints1':q('hp10'if n=='xbgconst'else'hp01'),'maxSpecialEnergy':1000,'specialEnergyRate':10}))
pending['Sprites/gui_global.spr']=sprite
for rel,t in pending.items():
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for rel,b in binary.items():
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
r={'stage':str(stage),'backup':str(backup),'files':list(dict.fromkeys(list(pending)+list(binary))),'constructors':constructors,'legacyAliases':aliases,'mirrorYards':yards,'mirrorShips':len(oldmirror['heroes']),'removedResearchStations':removedresearch,'resourceResearch':research,'starbasePrices':starprices,'aiChanges':aichanges,'icons':list(dict.fromkeys(icons)),'techDefinitions':techdefs,'obsoleteDefinitions':sorted(obsolete),'applied':False,'runtimeVerified':False,'biomatterModelSource':'http://armadafiles.com/files/armada-2/stations/species-8472/species-8472-pack-07-research-stations-and-fluidic-gate-10/details','biomatterModelAuthor':'Chiletrek'}
(repo/'reports/constructor-mirror-patch.json').write_text(json.dumps(r,indent=2));print('STAGED',len(r['files']),'files;',len(constructors),'constructors;',len(aichanges),'AI plans',flush=True)
