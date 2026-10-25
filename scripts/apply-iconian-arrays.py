"""Deploy the validated Iconian array overlay to the authorized Armada III installation."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,shutil
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/iconian-battle-array-stage')
running=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(running.stdout.strip()or'0'):raise SystemExit('Game is running; deployment stopped without changing game files.')
subprocess.run([sys.executable,str(repo/'scripts/validate-iconian-arrays.py')],check=True)
manifest=json.loads((stage/'manifest.json').read_text());overlay=Path(manifest['overlay'])
backup=Path('D:/Xaramada-Modwork/backups')/('iconian-arrays-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False)
new=[];changed=[]
for rel in manifest['files']:
 dest=root/rel
 if dest.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,b)
 else:new.append(rel)
(backup/'new-files.json').write_text(json.dumps(new,indent=2))
try:
 for rel in manifest['files']:
  dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():dest.chmod(0o666)
  shutil.copyfile(overlay/rel,dest);changed.append(rel)
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==manifest['files'][rel],rel
except Exception:
 for rel in changed:
  dest=root/rel;b=backup/rel
  if b.exists():shutil.copyfile(b,dest)
  elif rel in new:dest.unlink(missing_ok=True)
 raise
for rel in manifest['files']:
 dest=repo/'bajor/overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
result={**manifest,'status':'APPLIED - AWAITING GAMEPLAY TEST','backup':str(backup),'newFiles':new,'runtimeVerified':False}
(repo/'reports/iconian-applied.json').write_text(json.dumps(result,indent=2));(stage/'applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Iconian Battle Arrays applied: nine faction arrays plus redesigned Borg original, native faction specials and research, freighter menus, icons and docking. 1,019 static checks passed. Ready for gameplay testing; no runtime success claimed.'
(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Iconian arrays] Applied '+str(len(manifest['files']))+' verified files to D:/armadaIII; backup '+str(backup)+'. Awaiting gameplay test.\n')
print(json.dumps({'status':result['status'],'files':len(manifest['files']),'backup':str(backup),'runtimeVerified':False}))
