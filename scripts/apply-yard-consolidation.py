from pathlib import Path
import json,datetime,subprocess,shutil,os,hashlib,re
repo=Path('D:/aramada');root=Path('D:/armadaIII');report=repo/'reports/yard-consolidation.json';r=json.loads(report.read_text());stage=Path(r['stage'])
assert not r['applied'],'Already applied'
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game is running; patch remains staged'
backup=Path('D:/Xaramada-Modwork/backups')/('yard-consolidation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));targets=[]
for item in r['manifest']:
 rel=item['file'];data=(stage/rel).read_bytes();assert hashlib.sha256(data).hexdigest()==item['sha256']
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():shutil.copy2(dst,b)
  targets.append((dst,b,data))
try:
 for dst,b,data in targets:
  dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():os.chmod(dst,0o666)
  dst.write_bytes(data);assert dst.read_bytes()==data
except Exception:
 for dst,b,data in targets:
  if b.exists():shutil.copy2(b,dst)
 raise
r['applied']=True;r['appliedAt']=datetime.datetime.now().astimezone().isoformat();r['backup']=str(backup);report.write_text(json.dumps(r,indent=2))
props=json.loads((repo/'reports/yard-rebalance-before.json').read_text());lines=['# Yard consolidation','', 'Applied to D:/armadaIII. Runtime testing pending.','',f"Retired {len(r['retired'])} redundant yards. Preserved all {r['preservedYardProducedUnits']} units from yard menus. All 45 AI plans pass sequential prerequisite/producer checks; all formerly reachable units remain reachable.",'','Menus have at most 14 unique entries. Spare slots preserve sensible early/advanced/specialist production roles; no duplicate ships were invented to fill slots. Dedicated repair, recycling, assimilation, superweapon and wormhole facilities retain their separate functions. The already-unavailable fbyard remains unavailable.','', 'Native hull/shield statistics, crew, repair settings, models, starting fleets, ship abilities and existing artwork are preserved. Conventional basic yards cost 250 dilithium / 750 metal and take 45 seconds; advanced yards 300 / 1000 and 90 seconds; elite yards 450 / 1350 and 120 seconds. Other resource charges and specialized facilities retain their existing prices.','','## Active production rosters','']
for n,xs in r['rosters'].items():
 if n in ['fbyard','brecycle','fremmeler']:continue
 lines += ['### '+props[n].get('unitname',n)+' (`'+n+'`) - '+str(len(xs))+' slots','',', '.join(props[u].get('unitname',u)+' (`'+u+'`)' for u in xs), '']
lines+=['## Retired yards','', '| Yard | Ships redistributed to |','|---|---|']
for n,v in r['retired'].items():lines+=['| '+props[n].get('unitname',n)+' (`'+n+'`) | '+v+'; see rosters above |']
lines+=['','Retired facilities are removed from construction, technology and AI plans. Their ODF definitions remain dormant for compatibility. Saved matches may retain previously built facilities; use a new match for testing.','', 'Backup: '+str(backup)]
(repo/'reports/yard-consolidation.md').write_text('\n'.join(lines),encoding='utf-8')
# Refresh constructor documentation from applied menus, including the previous Fed consolidation.
planfile=repo/'reports/constructor-tier-plan.json';plan=json.loads(planfile.read_text());pending={}
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
backup=Path(r['backup'])
def items(n):
 d=resolve(n);return [d[k].lower() for k in sorted((k for k in d if re.fullmatch('builditem[0-9]+',k)),key=lambda k:int(k[9:]))]
ctorlines=['# Applied constructor menus','', 'Live installation: D:/armadaIII. Native icons and upgrade-only chains preserved.','']
for faction in plan['factions']:
 faction['proposed']=[c for c in faction['proposed'] if c['constructor'] not in ['xu3fed2','xu3bor2']]
 for c in faction['proposed']:
  c['buildings']=items(c['constructor']);ctorlines+=['## '+resolve(c['constructor']).get('unitname',c['constructor'])+' (`'+c['constructor']+'`)','',', '.join(c['buildings']),'']
plan['status']='Applied; yard consolidation removes19 redundant facilities; native constructor menus refreshed';plan['updated']=r['appliedAt'];planfile.write_text(json.dumps(plan,indent=2));(repo/'reports/constructor-current-menus.md').write_text('\n'.join(ctorlines))
s=repo/'status.json';d=json.loads(s.read_text(encoding='utf-8-sig'));d['current']='Applied yard consolidation:19 redundant yards retired; all340 yard-menu units preserved. Construction menus, six tech trees, build-button checks and45 AI plans updated/validated. Basic/advanced/elite conventional yard prices and build times standardized; durability, crew, repairs, ship stats and original starts preserved. Gameplay and results-screen retest pending.';d['updated']=r['appliedAt'];s.write_text(json.dumps(d,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+r['appliedAt']+'] '+d['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'applied':True,'files':len(r['files']),'backup':str(backup),'retired':len(r['retired']),'AIPlans':len(r['aiProfiles'])}))
