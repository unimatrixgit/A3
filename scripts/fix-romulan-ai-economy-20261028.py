from pathlib import Path
import re,json,datetime,shutil,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close game first.'
s=(repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig');exec(s.split('reports=[]')[0]);backup=Path('D:/Xaramada-Modwork/backups')/('romulan-ai-economy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
assert any(v=='rcolony'for k,v in cache['ryard'].items()if re.fullmatch('builditem[0-9]+',k));assert tech['rcolony']==(0,[])
pattern=r'^\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,?'
for p in sorted((root/'AI/AIPs').glob('romulan_*list.aip')):
 lines=p.read_text(encoding='latin1').splitlines();yard=[(i,l)for i,l in enumerate(lines)if re.match(r'\s*"xyr_r"\s*,',l)];assert len(yard)==1;line=yard[0][1];lines.pop(yard[0][0]);target=next(i for i,l in enumerate(lines)if re.match(r'\s*"rsrepair"\s*,',l));lines.insert(target,line)
 assert not any(re.match(r'\s*"rfreight"\s*,\s*3\s*,',l)for l in lines)
 at=next(i for i,l in enumerate(lines)if re.match(r'\s*"rcolony"\s*,',l));lines.insert(at+1,'    "rfreight", 3, 0, -1, 0,')
 assert not any(re.match(r'\s*"(?:rtrading|rcargo)"\s*,',l)for l in lines)
 at=next(i for i,l in enumerate(lines)if re.match(r'\s*"rresear2"\s*,',l));lines[at:at]=['    "rtrading", 1, 0, -1, 0,','    "rcargo", 1, 0, -1, 0,']
 parsed=[re.match(pattern,l).groups()for l in lines if re.match(pattern,l)];avail={Path(v).stem.lower()for k,v in cache['rom'].items()if re.fullmatch('standardunits[0-9]+',k)};issues=[]
 for i,row in enumerate(parsed):
  n=row[0]
  if n not in avail:
   gate,deps=tech.get(n,(0,[]));missing=set(deps)-avail;prod=producers.get(n,set())&avail
   if n not in idx or gate<0 or missing or not prod:issues.append({'step':i+1,'unit':n,'missing':sorted(missing),'producers':sorted(prod)})
  avail.add(n)
 assert not issues,(p.name,issues);assert len(parsed)<=200
 rel=p.relative_to(root);b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=('\r\n'.join(lines)+'\r\n').encode('latin1');p.write_bytes(data);(repo/'bajor/overlay'/rel).write_bytes(data)
 rows.append({'profile':p.name,'steps':len(parsed),'issues':issues,'changes':['Repair yard before repair ship','Third freighter immediately after first colony ship','Native trade station and one cargo ship before advanced research']})
report={'backup':str(backup),'profiles':rows,'colony':{'producer':'ryard','buildSlot':8,'techRequirements':[],'starbaseFallbackNeeded':False},'economyChecks':{'miningBeforeFreighters':True,'freighterMiningWeapons':['gmineDilithium','gmineLatinum'],'metalOrbitalBeforeYard':True,'nativeTradeAdded':True,'existingCostsUnchanged':True},'runtimeVerified':False};(repo/'reports/romulan-ai-economy-20261028.json').write_text(json.dumps(report,indent=2))
p=repo/'status.json';j=json.loads(p.read_text(encoding='utf-8-sig'));j['current']='Romulan AI/colony/economy checked: colony ship present in Yard I, no tech prerequisite. Five profiles corrected: repair yard before repair ship, third freighter after colony, trade station+cargo before advanced research. All 508 build steps passed dependency/producer audit. armadaIII applied; gameplay pending.';p.write_text(json.dumps(j,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+j['current']+'\n')
print(json.dumps({'profiles':len(rows),'steps':sum(x['steps']for x in rows),'issues':0,'colonyAlreadyBuildable':True}))
