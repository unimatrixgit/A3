from pathlib import Path
import re,json,datetime,shutil,hashlib,subprocess,stat
R=Path('D:/aramada');L=Path('D:/armadaIII');S=R/'patches/all-ai-local-economy-20261105';O=S/'overlay';O.mkdir(parents=True,exist_ok=True)
assert 'armada2.exe' not in subprocess.run(['tasklist','/FI','IMAGENAME eq Armada2.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout.lower()
# Import only the read-only ODF resolver and current producer/tech indexes.
exec((R/'scripts/audit-all-faction-ai-sequence.py').read_text().split('issues=[];profiles=[]')[0])
files={};startRows=[];profileRows=[];settings=[]
def save(p,s):files[p]=s.replace('\r\n','\n').replace('\n','\r\n').encode('cp1252')
colony={'fed':'fcolony','borg':'bcolony','kling':'kcolony','rom':'rcolony','card':'ccolony','dominion':'dcolony','breen':'brcolony','bajoran':'bjcolony','fer':'xfgcolony'}
# Exactly one colony ship in every existing default fleet, while leaving other units intact.
for race,ship in colony.items():
 assert ship+'.odf' in idx
 p='odf/other/'+race+'.odf';s=(L/p).read_text(encoding='cp1252')
 for mode in ['standard','minimal','super','ctf']:
  pat=r'(?im)^'+mode+r'Units(\d+)\s*=\s*"([^"\r\n]+)"[^\r\n]*(?:\r?\n)?';ms=list(re.finditer(pat,s))
  if not ms:continue
  units=[m[2] for m in sorted(ms,key=lambda m:int(m[1])) if m[2].lower()!=ship+'.odf']+[ship+'.odf'];s=re.sub(pat,'',s)+'\n'+'\n'.join(mode+'Units'+str(i)+' = "'+u+'"' for i,u in enumerate(units,1))+'\n';startRows.append(dict(raceFile=race,preset=mode,colony=ship))
 save(p,s)
config={
 'federation':dict(prefix='f',raceFile='fed',base='fbase',const='fconst',metal='forbital',mine='fmining',freight='ffreight',yard='fyard',colony='fcolony',trade='ftrading',cargo='fcargo'),
 'borg':dict(prefix='b',raceFile='borg',base='bbase',const='bconst',metal='bbase2',mine='bmining',freight='bfreight',yard='byard',colony='bcolony'),
 'klingon':dict(prefix='k',raceFile='kling',base='kbase',const='kconst',metal='korbital',mine='kmining',freight='kfreight',yard='kyard',colony='kcolony',trade='ktrading',cargo='kcargo'),
 'romulan':dict(prefix='r',raceFile='rom',base='rbase',const='rconst',metal='rorbital',mine='rmining',freight='rfreight',yard='ryard',colony='rcolony',trade='rtrading',cargo='rcargo'),
 'cardassian':dict(prefix='c',raceFile='card',base='cbase',const='cconst',metal='corbital',mine='cmining',freight='cfreight',yard='cyard',colony='ccolony',trade='ctrading',cargo='ccargo'),
 'dominion':dict(prefix='d',raceFile='dominion',base='dbase',const='dconst',metal='dorbital',mine='dmining',freight='dfreight',yard='dyard',colony='dcolony',trade='dtrading',cargo='dcargo'),
 'breen':dict(prefix='br',raceFile='breen',base='brbase',const='brconst',metal='brorbital',mine='brmining',freight='brfreight',yard='bryard',colony='brcolony'),
 'bajoran':dict(prefix='bj',raceFile='bajoran',base='bjbase',const='bjconst',metal='bjorbital',mine='bjmining',freight='bjfreight',yard='bjyard',colony='bjcolony',trade='bjtrading',cargo='bjcargo')}
pattern=r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
for race in list(config)+['species8472']:
 if race=='species8472':
  opening=[('8472_passive',2),('8472_transmuter',1),('8472_active',2),('8472_collector',2),('8472_transmuter',2),('8472_active',4),('8472_collector',4)];raceFile='species8472'
 else:
  c=config[race];raceFile=c['raceFile'];opening=[(c['base'],1),(c['const'],3),(c['mine'],2),(c['freight'],4),(c['metal'],2)]
  if 'trade' in c:opening += [(c['trade'],2),(c['freight'],6),(c['cargo'],2)]
  opening += [(c['yard'],1),(c['colony'],2)]
 for p in (L/'AI/AIPs').glob(race+'_*list.aip'):
  text=p.read_text(encoding='cp1252');rows=[(m[1],int(m[2]),int(m[3]),int(m[4]),int(m[5])) for m in re.finditer(pattern,text,re.M)];assert rows,p
  remaining=list(rows)
  for unit in dict.fromkeys(n for n,count in opening):
   # Replace only its first home-base quota, leaving later expansion/roster choices intact.
   j=next((j for j,row in enumerate(remaining) if row[0]==unit and row[2]==0),None)
   if j is not None:remaining.pop(j)
  first=[(n,count,0,-1,0) for n,count in opening];new=first+remaining;assert len(new)<=200,(p,len(new))
  d=props(raceFile);avail={Path(v).name.lower() for k,v in d.items() if re.fullmatch('standardunits[0-9]+',k)}
  if raceFile in colony:avail.add(colony[raceFile]+'.odf')
  checks=[]
  for n,count,base,cap,tech in first:
   key=n+'.odf';assert key in idx,(p,n);missing=[x for x in tt.get(key,[]) if x not in avail];prod=[x for x in producers.get(key,[]) if x in avail]
   assert key in avail or (key in tt and not missing and prod),(p.name,n,missing,prod)
   checks.append(dict(unit=n,count=count,producerAvailable=bool(prod) or key in avail,missingPrerequisites=missing));avail.add(key)
  # Edit the build array in place, retaining the surrounding native AIP configuration.
  a=re.search(r'(Way_Better_Build_List_Element\s+the_build_list\s*\[[^\]]+\]\s*=\s*\{)(.*?)(\};)',text,re.S);assert a,p
  body='\n// Local economy first: home-base resource quotas and support before attack fleets.\n'+'\n'.join(f'    "{n}", {count}, {base}, {cap}, {tech},' for n,count,base,cap,tech in new)+'\n';text=text[:a.start(2)]+body+text[a.end(2):];save(p.relative_to(L).as_posix(),text)
  profileRows.append(dict(profile=p.name,race=race,rows=len(new),opening=checks,homeBase=0,latinumSupport='trade' in config.get(race,{}),laterRowsPreserved=True))
# Shared instant-action strategies: favor nearby viable resources and continue local expansion.
strategyNames=['newdefault','a2_aggressive','a2_defensive','a2_exploration','a2_hard_aggressive','a2_hard_defensive','a2_hard_exploration','a2_modified_aggressive','a2_modified_defensive','a2_modified_exploration','a2_very_aggressive']
for name in strategyNames:
 p=L/'AI/AIPs'/(name+'.aip');s=p.read_text(encoding='cp1252');changes={}
 for key,value in [('resource_distance_multiplier',200000.0),('resource_enemy_penalty',2000.0),('resource_lack_multiplier',3.0),('resource_dilithium_tendency',3.0),('resource_metal_tendency',3.0),('resource_latinum_tendency',2.5),('resource_biomatter_tendency',3.0),('MAX_EXEC_RESOURCE',6),('MAX_EVAL_RESOURCE',40)]:
  pat=r'(?m)^\s*(int|double)\s+'+key+r'\s*=\s*[^;]+;';m=re.search(pat,s);typ='int' if key.startswith('MAX_') else 'double';line=typ+' '+key+' = '+str(value)+';'
  if m:s=re.sub(pat,lambda m:line,s)
  else:s+='\n'+line+'\n'
  changes[key]=value
 pat=r'(?m)^\s*int\s+resource_priority\s*=\s*([^;]+);';m=re.search(pat,s);value=max(10000,int(m[1].strip())) if m else 10000
 if m:s=re.sub(pat,'\nint resource_priority = '+str(value)+';',s)
 else:s+='\nint resource_priority = '+str(value)+';\n'
 changes['resource_priority']=value;save(p.relative_to(L).as_posix(),s);settings.append(dict(profile=p.name,parameters=changes))
for p,data in files.items():dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
assert len(profileRows)==45
for p,data in files.items():
 if p.startswith('AI/AIPs/'):
  for inc in re.findall(rb'#include\s+"([^"]+)"',data):assert (L/'AI/AIPs'/inc.decode()).exists(),(p,inc)
# Verify each updated starting fleet has one colony ship and no newly introduced heroes.
for row in startRows:
 p='odf/other/'+row['raceFile']+'.odf';s=files[p].decode('cp1252');units=re.findall(r'(?im)^'+row['preset']+r'Units\d+\s*=\s*"([^"]+)"',s);assert units.count(row['colony']+'.odf')==1
 for u in units:assert props(u).get('ishero','0')!='1',(row,u)
report={'installed':False,'runtimeVerified':False,'scope':'All45 existing faction AI lists plus11 generic instant-action strategies;9 colonizer-capable faction start files. Campaign-specific mission AI lists are not rewritten.','openingTargets':{'normalFactions':{'homeConstructors':3,'dilithiumFacilities':2,'metalOrbitals':2,'miningFreighters':4,'withNativeLatinumTrade':{'tradeFacilities':2,'miningFreighters':6,'tradeCargoShips':2},'supportShipyard':1,'colonyShips':2},'species8472':{'transmuters':2,'collectors':4,'activeProducers':4}},'limitations':['Static build lists cannot guarantee that every nearby resource is occupied before any combat production; native resource-site availability and priorities control placement.','Nearby resources favored10x more strongly; this is a preference, not a hard maximum distance.','No ordinary metal/dilithium colonies added to8472; it cannot colonize.','Borg and Breen have no native trading station; their later Ferengi expansion remains intact.','There is no separate Ferengi faction AI build-list set; Ferengi default starts still receive their colony ship.'],'profiles':profileRows,'strategies':settings,'startingColonies':startRows,'files':[dict(path=p,previousSha256=hashlib.sha256((L/p).read_bytes()).hexdigest(),sha256=hashlib.sha256(d).hexdigest()) for p,d in files.items()]}
(S/'manifest.json').write_text(json.dumps(report,indent=2));(R/'reports/all-ai-local-economy-20261105.json').write_text(json.dumps(report,indent=2))
# User has confirmed the game is closed and requested deployment.
B=Path('D:/Xaramada-Modwork/backups')/('all-ai-local-economy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
assert 'armada2.exe' not in subprocess.run(['tasklist','/FI','IMAGENAME eq Armada2.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout.lower()
for row in report['files']:assert hashlib.sha256((L/row['path']).read_bytes()).hexdigest()==row['previousSha256']
for p,data in files.items():
 for root,tag in [(L,'live'),(R/'bajor/overlay','mirror')]:
  target=root/p
  if target.exists():dest=B/tag/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest);target.chmod(target.stat().st_mode|stat.S_IWRITE)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 assert (L/p).read_bytes()==(R/'bajor/overlay'/p).read_bytes()
report.update(installed=True,backup=str(B));(S/'manifest.json').write_text(json.dumps(report,indent=2));(R/'reports/all-ai-local-economy-20261105.json').write_text(json.dumps(report,indent=2))
p=R/'status.json';status=json.loads(p.read_text());status['current']='Installed economy-first update across45 faction AI lists and11 strategies: two home dilithium facilities/two metal orbitals, increased miners, native latinum trade first, stronger nearby-resource preference. Added one colony ship to33 default start presets across9 capable factions;8472 uses4 collectors/2 transmuters. Prefix producer/tech checks passed. Runtime AI/map behavior untested.';p.write_text(json.dumps(status,indent=2)+'\n')
with (R/'build.log').open('a') as f:f.write('\n2026-11-05 Installed all-AI local economy/colony-start update: '+str(len(files))+' files;45 build lists,11 strategies,'+str(len(startRows))+' start presets. All new opening producer/tech checks passed. Backup='+str(B)+'. Runtime AI behavior pending.\n')
print(json.dumps({'installedFiles':len(files),'AILists':len(profileRows),'strategies':len(settings),'startingPresets':len(startRows),'backup':str(B)},indent=2))
