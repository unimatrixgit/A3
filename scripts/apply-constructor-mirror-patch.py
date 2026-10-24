from pathlib import Path
import json,datetime,hashlib,shutil,os,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');rp=repo/'reports/constructor-mirror-patch.json';r=json.loads(rp.read_text());v=json.loads((repo/'reports/constructor-mirror-validation.json').read_text());assert not v['errors'];assert v['mirrorShips']==59 and v['mirrorYards']==11
assert not r['applied'],'This manifest has already been applied; preserve its original backup'
running=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process armada2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True);assert running.stdout.strip()=='0','Close Armada II before applying'
stage=Path(r['stage']);backup=Path(r['backup']);files=r['files'];manifest=[];saved=[]
# Complete both live and repository backups before replacing any file.
for rel in files:
 assert '..'not in Path(rel).parts and not Path(rel).is_absolute(),rel
 assert (stage/rel).is_file(),rel
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel
  if dst.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
  saved.append((dst,b,dst.exists()))
try:
 for i,rel in enumerate(files):
  src=stage/rel;data=src.read_bytes()
  for base in [root,repo/'bajor/overlay']:
   dst=base/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   if dst.exists():os.chmod(dst,0o666)
   dst.write_bytes(data);assert dst.read_bytes()==data,rel
  manifest.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
  if(i+1)%100==0:print('Applied',i+1,'/',len(files),flush=True)
except Exception:
 for dst,b,existed in reversed(saved):
  if existed:shutil.copyfile(b,dst)
  elif dst.exists():dst.unlink()
 raise
r.update(applied=True,appliedAt=datetime.datetime.now().astimezone().isoformat(),manifest=manifest,runtimeVerified=False);rp.write_text(json.dumps(r,indent=2))
md='# Applied constructor, mirror yard and resource patch\n\nApplied only to D:/armadaIII. Source files mirrored to D:/aramada/bajor/overlay. File validation passed; gameplay has not been tested.\n\n'
md+='## Constructor roles\n\nT1: mining, standard yards, research and upgrade facilities. T2: defenses, hero/Omega and Mirror Universe yards. T3: all eight main faction starbases, faction special structures and Ferengi facilities. Extra T3 variants preserve overflow. Legacy constructor files remain compatible aliases. Constructors carry no weapons.\n\nStandard constructor prices: T1 125 dilithium/25 metal, T2 200/100, T3 300/200. Starting crew150; build times20/30/40 seconds. Ferengi constructors cost500 latinum; Borg-priced Ferengi constructors cost300 dilithium/200 metal. Species8472 constructors use biomatter. Existing hulls, model proportions and worker-bee systems are preserved.\n\n'
md+='## Starbase prices\n\nAll strategic conventional starbases cost1,500 dilithium +1,500 metal, with150 starting crew and unchanged maximum crew. Other resource costs are zero. Species8472 retains its biomatter economy. Heavy weapons platforms, tactical arrays, special shipyards and ships implemented through the starbase engine class are excluded from this price change.\n\n'
md+='## Mirror Universe\n\n59 counterparts are built through11 normal shipyards, including two Federation yards. Ordinary production gives the building player ownership. The failed summon abilities and mirror-research menus are removed from gameplay; their dormant definitions are disabled in all six technology trees. Native abilities remain. Mirror ships retain double normal damage,75% health and125% model size. Their resource prices and build times are125% of the corresponding original hero. Hugh uses the battle-pack cube; the Queen counterpart retains its sphere model. No starting fleets were changed.\n\n'
md+='## Resource research\n\nTwo tiers unlock new equipment variants: +50% and +100% over the base extraction rate. Existing units do not upgrade retroactively. Normal Ferengi research covers dilithium/metal/latinum; Borg contracts cover dilithium/metal only. Research costs900/1350 latinum, or the same value split60% dilithium and40% metal for Borg contracts.\n\nSpecies8472 has its own Biomatter Metabolism Institute, built by T1. It uses Chiletrek\'s Species8472 Pack07 research station/pod models and textures under unique filenames. Research costs900/1350 biomatter and unlocks enhanced Collectors on the Active Embryo. Biomatter mining yield and extraction conversion improve50%/100%; other mining beams and storage capacities are unchanged. No Ferengi facilities or units were added to8472.\n\n'
md+='## AI and interface\n\n45 faction skirmish/strategy build lists order the correct constructors before their buildings. Eligible factions use the Ferengi contract, service and research facilities; Borg plans use the Borg-priced catalog and omit latinum research/collectors. Every faction builds its mirror yards and a counterpart from each. Icons distinguish constructor tiers, mirror production and resource research tiers.\n\n'
md+='## Applied constructor menus\n\n'
before=json.loads((repo/'reports/constructor-patch-before.json').read_text())
for c in r['constructors']:
 md+='### '+c['race']+' — T'+str(c['tier'])+' (`'+c['unit']+'`)\n\n'
 for n in c['buildings']:md+='- '+before.get(n,{}).get('unitname',n)+' (`'+n+'`)\n'
 md+='\n'
md+='## Validation\n\n'+str(v['changedODFs'])+' ODFs, '+str(v['modelsChecked'])+' models, '+str(v['buttons'])+' build buttons, six technology trees and45 AI plans checked. No new validation errors. Existing source warnings remain:\n\n'
for warning in v['warnings']:md+='- '+warning+'\n'
md+='\nBackup: '+str(backup)+'\n'
(repo/'reports/constructor-mirror-applied.md').write_text(md)
planpath=repo/'reports/constructor-tier-plan.json';plan=json.loads(planpath.read_text());plan.update(status='applied; see constructor-mirror-patch.json for final menus and additions',appliedReport=str(rp));planpath.write_text(json.dumps(plan,indent=2))
oldpath=repo/'reports/mirror-ferengi-research.json';old=json.loads(oldpath.read_text());old.update(supersededBy=str(rp),currentMechanism='Normal Mirror Universe shipyard production; summoning/research disabled');oldpath.write_text(json.dumps(old,indent=2))
s=repo/'status.json';d=json.loads(s.read_text(encoding='utf-8-sig'));d['updated']=r['appliedAt'];d['current']='Applied constructor T1/T2/T3 roles, all strategic starbase prices1500 dilithium/1500 metal/150 starting crew,11 Mirror Universe yards replacing summoning, two-tier Ferengi resource research, and a dedicated8472 biomatter research station using Chiletrek artwork.45 AI plans include constructor roles, eligible Ferengi catalogs and mirrors.130 build icons checked. Backed up and installed to D:/armadaIII only; in-game testing pending.'
d.setdefault('features',[]).append({'id':'constructor-tiers-mirror-yards','title':'Constructor tiers, mirror yards and resource research','steps':[{'label':'Audit construction options and preserve existing buildings','done':True},{'label':'Create tier icons, mirror yards and two-tier resource research','done':True},{'label':'Validate models, technology and45 AI plans','done':True},{'label':'Back up and install patch to armadaIII','done':True},{'label':'Test production, research and AI in a new match','done':False}]});s.write_text(json.dumps(d,indent=2))
with(repo/'build.log').open('a')as log:log.write('\n['+r['appliedAt']+'] '+d['current']+' Backup: '+str(backup)+'\n')
print('APPLIED',len(manifest),'files. Backup:',backup,flush=True)
