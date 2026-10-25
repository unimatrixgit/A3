"""Apply the validated Borg Armada II model and station scale correction."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';m=json.loads((stage/'manifest.json').read_text());v=json.loads((stage/'validation.json').read_text());assert v['status']=='PASS'
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(r.stdout.strip()or'0'):raise SystemExit('Game running: structural refinement staged, not applied.')
changes=[rel for rel,h in m['files'].items()if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=h];backup=Path('D:/Xaramada-Modwork/backups')/('yard-bridges-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False)
for rel in changes:
 target=(root/rel).resolve();assert target.is_relative_to(root.resolve())and not rel.lower().startswith(('maps/','bzn/'));assert hashlib.sha256(target.read_bytes()).hexdigest()==m['sourceHashes'][rel];out=backup/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,out)
try:
 for rel in changes:
  target=root/rel;shutil.copyfile(O/rel,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==m['files'][rel]
except Exception:
 for rel in changes:shutil.copyfile(backup/rel,root/rel)
 raise
for rel,h in m['files'].items():
 assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h;dest=repo/'bajor/overlay'/rel;shutil.copyfile(root/rel,dest)
a=json.loads((stage/'applied.json').read_text());a['borgAndScaleUpdate']={'backup':str(backup),'files':len(changes),'runtimeVerified':False};a['staticChecks']=v['checks'];a['nextPatch']='Conservative unused asset audit; balance changes remain on hold';(stage/'applied.json').write_text(json.dumps(a,indent=2));(repo/'reports/twin-yards-applied.json').write_text(json.dumps(a,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Applied Armada II original Borg Nexus and Assembly Matrix model correction. Production and repair yards 25% larger with footprints; Borg HWP 12.5% smaller with footprint. Static validation passed; gameplay testing pending. Cleanup audit next; maps protected.';s['twinYards']=a;(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Borg Armada II and yard scale correction] '+json.dumps(a['borgAndScaleUpdate'])+'\n')
print(json.dumps(a['borgAndScaleUpdate']))
