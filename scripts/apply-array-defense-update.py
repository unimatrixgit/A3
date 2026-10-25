from pathlib import Path
import json,sys,subprocess,datetime,shutil,hashlib
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/array-defense-update-20261025';overlay=stage/'overlay'
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(r.stdout.strip()or'0'):raise SystemExit('Game is running; no files changed.')
subprocess.run([sys.executable,str(repo/'scripts/validate-array-defense-update.py')],check=True)
m=json.loads((stage/'manifest.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('array-defense-update-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False);new=[];changed=[]
for row in m['files']:
 rel=row['file'];dest=root/rel
 if dest.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,b)
 else:new.append(rel)
(backup/'new-files.json').write_text(json.dumps(new,indent=2))
try:
 for row in m['files']:
  rel=row['file'];dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():dest.chmod(0o666)
  shutil.copyfile(overlay/rel,dest);changed.append(rel);assert hashlib.sha256(dest.read_bytes()).hexdigest()==row['stagedHash']
except Exception:
 for rel in changed:
  if(backup/rel).exists():shutil.copyfile(backup/rel,root/rel)
  elif rel in new:(root/rel).unlink(missing_ok=True)
 raise
for row in m['files']:
 rel=row['file'];out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,out)
result={**m,'status':'APPLIED - AWAITING GAMEPLAY TEST','backup':str(backup),'runtimeVerified':False};(repo/'reports/array-defense-update-applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='All 11 Battle Arrays patched: gun range 600 to 750, matching acquisition range and explicit attack settings, built-in cloak detection, faction scouts and light craft. Damage / reload / original abilities unchanged. Auto-fire correction awaits in-game confirmation.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Battle Array defence] Applied '+str(len(m['files']))+' files; backup '+str(backup)+'. Range +25%, detector and production additions. In-game auto-fire validation pending.\n')
print(json.dumps({'status':result['status'],'arrays':len(m['arrays']),'files':len(m['files']),'backup':str(backup)}))
