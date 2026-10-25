"""Apply the validated Cardassian-derived Bajoran yard revision."""
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
a=json.loads((stage/'applied.json').read_text());a['bajoranYardRevision']={'backup':str(backup),'files':len(changes),'runtimeVerified':False,'centreSource':'cbase','basicBaySource':'cyard','commandBaySource':'xvstock_cyard2','decorativeShips':False};a['staticChecks']=v['checks'];a['nextPatch']='Conservative unused asset audit; balance changes remain on hold';(stage/'applied.json').write_text(json.dumps(a,indent=2));(repo/'reports/twin-yards-applied.json').write_text(json.dumps(a,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Applied Cardassian-derived Bajoran production yards and service dock: swept station pylons, copper hulls, connected bays. Second yard uses a different original Cardassian advanced-yard model; no decorative fighter models. Icons, footprints and launch points refreshed. Static checks passed; gameplay testing pending.';s['twinYards']=a;(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Cardassian-derived Bajoran yard revision] '+json.dumps(a['bajoranYardRevision'])+'\n')
print(json.dumps(a['bajoranYardRevision']))
