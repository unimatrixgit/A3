from pathlib import Path
import json,datetime,shutil,os,hashlib,re,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');rp=repo/'reports/ai-start-recovery.json';r=json.loads(rp.read_text());assert not r['failures']and len(r['profiles'])==45 and not r['applied']
game=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process armada2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True);assert game.stdout.strip()=='0','Game must be closed'
stage=Path(r['stage']);backup=Path('D:/Xaramada-Modwork/backups')/('ai-start-recovery-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));saved=[]
for rel in r['files']:
 assert (stage/rel).is_file()
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);saved.append((dst,b))
manifest=[]
try:
 for rel in r['files']:
  data=(stage/rel).read_bytes()
  for base in [root,repo/'bajor/overlay']:
   dst=base/rel;os.chmod(dst,0o666);dst.write_bytes(data);assert dst.read_bytes()==data
  manifest.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
except Exception:
 for dst,b in saved:shutil.copyfile(b,dst)
 raise
for profile in r['profiles']:
 if profile['race']!='dominion':continue
 t=(root/'AI/AIPs'/profile['file']).read_text(encoding='latin1');seq=re.findall(r'(?m)^\s*"([^"]+)"\s*,',t)
 assert {'brconst','brbase','bryard','bryard2','bryard3','mrybreen'}<=set(seq),profile['file']
r.update(applied=True,appliedAt=datetime.datetime.now().astimezone().isoformat(),backup=str(backup),manifest=manifest,dominionBreenBranchVerified=True);rp.write_text(json.dumps(r,indent=2))
md='# AI build-order recovery and standard starts\n\nApplied to D:/armadaIII only. Backups and source copies saved; gameplay is not yet verified.\n\nThe previous constructor rewrite inserted advanced yards/Temporal Constructors ahead of the basic yards and research required to obtain them, including before the already-owned starting starbase goal. This patch seeds each plan from the actual starting fleet, opens with economy and basic production, and recursively schedules each missing research prerequisite and a reachable producer before its target. Retired constructor names in technology requirements are redirected to their currently produced equivalents.\n\nAll45 faction skirmish/strategy plans passed a separate sequential dependency audit and remain below the200-entry limit. Existing duplicate goals are compacted. Legacy tech-level phase fields are normalized to0; explicit technology-tree prerequisites govern progression. This is a static reachability check, not a demonstration of live AI behavior or resource affordability.\n\nFerengi and mirror branches remain present. Dominion additionally develops a complete Breen branch using its free starting Breen constructor, including all three Breen yards and its mirror yard.\n\n## Standard starting fleets\n\n| Faction | Fleet |\n|---|---|\n'
for race,units in r['starts'].items():md+='| '+race+' | '+', '.join(units)+' |\n'
md+='\nAll main factions except Breen start with2 Basic Constructors,1 Advanced Constructor and1 starbase. Dominion additionally receives1 Breen constructor. Bajor additionally receives1 free Ferengi Temporal Constructor; purchase costs remain unchanged. Breen retains its single constructor type and starts with2 copies plus its starbase. Species8472 uses its existing biological constructor equivalents. Scouts are no longer included in standard starts. Minimal/Super definitions are unchanged. No heroes were added to any starts; icons and ship stats were not edited.\n\n## AI plan sizes\n\n'
for x in r['profiles']:md+='- '+x['file']+': '+str(x['rows'])+' rows, no dependency-order failures.\n'
md+='\nBackup: '+str(backup)+'\n';(repo/'reports/ai-start-recovery.md').write_text(md)
s=repo/'status.json';d=json.loads(s.read_text());d['updated']=r['appliedAt'];d['current']='Applied45 AI build-order repairs using actual start units, economy-first progression and full producer/research chains; corrected retired constructor technology requirements. Standard starts:2 Basic +1 Advanced +starbase (Breen:2 native builders +base); Dominion adds a Breen constructor and develops the Breen branch; Bajor adds a free Ferengi Temporal Constructor. Ferengi/mirror branches retained. File checks passed; new-match testing pending.';d.setdefault('features',[]).append({'id':'ai-start-recovery','title':'AI build-order recovery and standard starts','steps':[{'label':'Find early advanced-yard and retired-constructor dependency blocks','done':True},{'label':'Rebuild45 faction AI plans with valid producer/research ordering','done':True},{'label':'Apply standard starts and Dominion/Bajor bonus constructors','done':True},{'label':'Verify live AI economy and progression in a new match','done':False}]});s.write_text(json.dumps(d,indent=2))
with(repo/'build.log').open('a')as f:f.write('\n['+r['appliedAt']+'] '+d['current']+' Backup:'+str(backup)+'\n')
print('Applied',len(r['files']),'files;45 AI plans;9 standard fleets;',len(r['techChanges']),'technology requirement corrections. Backup:',backup)
