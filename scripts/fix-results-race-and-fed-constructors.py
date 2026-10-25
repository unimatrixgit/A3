from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import shutil,subprocess,os,hashlib,collections
assert subprocess.run(['powershell','-NoProfile','-Command',"if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}"],capture_output=True).returncode==0,'Game must be closed'
pending={};records=[]
def save(n,t):pending[index[n].relative_to(root).as_posix()]=t
def menu(n,items):
 assert len(items)<=14 and len(items)==len(set(items)),n
 t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',text(n))
 for i,v in enumerate(items):t=put(t,'buildItem'+str(i),q(v))
 save(n,t)
def items(n):return [v for k,v in sorted(resolve(n).items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1)if re.fullmatch('builditem[0-9]+',k)]
# The executable resolves CraftClass+0x1b0 through the race/name table.
# Its results tally dereferences that pointer without checking for null.
raceids=[v for k,v in sorted(resolve('races').items(),key=lambda kv:int(kv[0][4:])if re.fullmatch('race[0-9]+',kv[0])else-1)if re.fullmatch('race[0-9]+',k)]
assert 'breen.odf'not in raceids
assert resolve('breen')['instantactionslot']=='-1'
raceids.insert(raceids.index('norace.odf'),'breen.odf')
t='// Registered gameplay races, including non-selectable subraces.\nnumberOfRaces = '+str(len(raceids))+'\n'
for i,v in enumerate(raceids):t+='race'+str(i)+' = '+q(v)+'\n'
save('races',t)
# Case-sensitive race lookup also requires the native Dominion spelling.
assert resolve('dompod9')['race']=='Dominion';save('dompod9',put(text('dompod9'),'race',q('dominion')))
menu('fconst2',items('fconst2')+['fjupiter']);menu('xfuconst',items('xfuconst')+['fsuperbl'])
removed=[]
for n in index:
 if 'xu3fed2'in items(n):menu(n,[v for v in items(n)if v!='xu3fed2']);removed.append(n)
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';lines=[]
 for line in(root/rel).read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if a and a[0].lower()=='xu3fed2.odf':continue
  if len(a)>2 and 'xu3fed2.odf'in [v.lower()for v in a[2:]]:line=re.sub(r'(?i)\bxu3fed2\.odf\b','xfuconst.odf',line)
  lines.append(line)
 pending[rel]='\n'.join(lines)+'\nxu3fed2.odf -1\n'
ai=[]
for f in(root/'AI/AIPs').glob('*.aip'):
 t=f.read_text(encoding='latin1')
 if not re.search(r'(?m)^\s*"xu3fed2"\s*,',t):continue
 pending[f.relative_to(root).as_posix()]='\n'.join(s for s in t.splitlines()if not re.match(r'^\s*"xu3fed2"\s*,',s))+'\n';ai.append(f.name)
# Validate race names and constructor availability against the pending overlay.
registered={resolve(Path(v).stem)['name']for v in raceids};assert 'breen'in registered and 'ferengi'in registered
produced={v.lower()for n in index for k,v in resolve(n).items()if re.fullmatch('(secondary)?builditem[0-9]+',k)}
invalid=[];native=collections.defaultdict(set)
for n in produced:
 d=resolve(n)
 if d.get('race')and d['race']not in registered:invalid.append((n,d['race']))
 if d.get('classlabel')in ['constructionrig','evolver']and re.search('Constructor|Assembler',d.get('unitname',''))and not d.get('unitname','').startswith('Ferengi'):native[d['race']].add(n)
assert not invalid,invalid
assert all(len(v)<=3 for v in native.values()),native
assert len(native['breen'])==1 and 'xu3fed2'not in produced
assert len(items('xfuconst'))==14 and len(items('fconst2'))==10
# Independently audit every live AI profile with the pending menus and trees.
tt={}
for line in pending['techtree/tech1.tt'].splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):tt[Path(a[0]).stem.lower()]=None if int(a[1])<0 else [Path(x).stem.lower()for x in a[2:2+int(a[1])]]
producers=collections.defaultdict(set)
for n in index:
 for k,v in resolve(n).items():
  if re.fullmatch('(secondary)?builditem[0-9]+',k):producers[v.lower()].add(n)
cfg={'federation':'fed','klingon':'kling','romulan':'rom','cardassian':'card'};profiles=json.loads((repo/'reports/ai-start-recovery.json').read_text())['profiles']
for profile in profiles:
 config=resolve(cfg.get(profile['race'],profile['race']));seen={Path(v).stem.lower()for k,v in config.items()if re.fullmatch('standardunits[0-9]+',k)};rel='AI/AIPs/'+profile['file'];t=pending.get(rel)or(root/rel).read_text(encoding='latin1')
 for n in re.findall(r'(?m)^\s*"([^\"]+)"\s*,',t):
  if n not in seen:
   assert isinstance(tt.get(n),list)and all(v in seen for v in tt[n]),(profile['file'],n,'technology')
   assert producers[n]&seen,(profile['file'],n,'producer')
  seen.add(n)
backup=Path('D:/Xaramada-Modwork/backups')/('results-race-fed-constructors-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));manifest=[]
for rel in pending:
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
for rel,t in pending.items():
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1')
 for base in [root,repo/'bajor/overlay']:
  dst=base/rel;os.chmod(dst,0o666);dst.write_bytes(data);assert dst.read_bytes()==data
 manifest.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
r={'applied':True,'appliedAt':datetime.datetime.now().astimezone().isoformat(),'backup':str(backup),'files':list(pending),'manifest':manifest,'crashDump':'C:/Users/thoma/AppData/Local/CrashDumps/Armada2.exe.23908.dmp','crashOffset':'0x001fedfa','crashStage':'Admirals Log / match results','evidence':['0x5fedfa reads race name from a null race pointer (EDI=0x14)','CraftClass+0x1b0 is populated by race-name lookup at0x48b020','Lookup returns0 for unregistered race names','Breen units use race=breen but races.odf omitted breen.odf'],'raceFix':'Register existing Breen definition with instantActionSlot=-1; correct Dominion pod race capitalization','nativeConstructorCounts':{k:len(v)for k,v in native.items()},'removedFederationSpecialistFrom':removed,'aiPlansAdjusted':ai,'aiPlansValidated':len(profiles),'registeredRaceNames':sorted(registered),'invalidProducedUnitRaces':invalid,'runtimeVerified':False};(repo/'reports/results-race-fed-constructors.json').write_text(json.dumps(r,indent=2))
s=repo/'status.json';d=json.loads(s.read_text(encoding='utf-8-sig'));d['current']='Applied results-crash fix: registered missing hidden Breen subrace and corrected Dominion pod race spelling. Dump dereferenced a null race record while building Admiral\'s Log results. Federation now has3 native constructors: Jupiter moved to Advanced, Temporal Stasis facility to Temporal; Specialist removed from production/AI/tech. All main factions have at most3 native constructor types; Breen/Ferengi remain single.45 AI plans and produced-unit race names checked. Results-screen gameplay retest pending.';d['updated']=r['appliedAt'];s.write_text(json.dumps(d,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as f:f.write('\n['+r['appliedAt']+'] '+d['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'files':len(pending),'registeredRaceNames':sorted(registered),'nativeConstructorCounts':r['nativeConstructorCounts'],'aiPlansValidated':len(profiles),'backup':str(backup)},indent=2))
