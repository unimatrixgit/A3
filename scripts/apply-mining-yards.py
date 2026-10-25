"""Apply the validated mining patch transactionally to the authorized live folder."""
from pathlib import Path
import json,hashlib,shutil,datetime,subprocess,sys
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=repo/'patches/mining-yards-20261025';O=stage/'overlay'
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-CimInstance Win32_Process -Filter "Name=\'Armada2.exe\' OR Name=\'Armada.exe\'").Count'],capture_output=True,text=True,check=True)
if int(running.stdout.strip()or'0'):raise SystemExit('Game running; no changes applied.')
subprocess.run([sys.executable,str(repo/'scripts/validate-mining-yards.py')],check=True)
m=json.loads((stage/'manifest.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('mining-yards-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));new=[]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for r in m['files']:
 rel=r['file'];live=root/rel
 assert digest(O/rel)==r['stagedHash'],('Staged file changed',rel)
 assert(digest(live)if live.exists()else None)==r['sourceHash'],('Live baseline changed',rel)
 if live.exists():
  saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(live,saved)
 else:new.append(rel)
backup.mkdir(parents=True,exist_ok=True);(backup/'new-files.json').write_text(json.dumps(new,indent=2));changed=[]
try:
 for r in m['files']:
  rel=r['file'];live=root/rel;live.parent.mkdir(parents=True,exist_ok=True)
  if live.exists():live.chmod(0o666)
  shutil.copyfile(O/rel,live);changed.append(rel);assert digest(live)==r['stagedHash']
except Exception:
 for rel in changed:
  if(backup/rel).exists():shutil.copyfile(backup/rel,root/rel)
  elif rel in new:(root/rel).unlink(missing_ok=True)
 raise
for r in m['files']:
 rel=r['file'];mirror=repo/'bajor/overlay'/rel;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,mirror)
result={**m,'status':'APPLIED - GAMEPLAY TEST PENDING','backup':str(backup),'runtimeVerified':False}
(repo/'reports/mining-yards-applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Applied nine faction Mining Yards (native collectors MK I-III), 26 research-gated NX-style miner refit buttons, 45 AI plans, tier icons and Ferengi Service Yard redesign. Federation contracts are at its advanced research station; 8472 uses biomatter. Orbital replacement not enabled. Runtime mining/refit test pending.'
(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Mining Yards] Applied '+str(len(m['files']))+' hash-verified files; '+str(m['checks'])+' file checks. Backup '+str(backup)+'. Nine native yards, MK I-III, Ferengi miners stay at Service Yards, all 45 faction AI plans. Gameplay refit/cargo behavior unverified. No orbital fusion or starting-fleet changes.\n')
print(json.dumps({k:v for k,v in result.items()if k!='files'},indent=2))
