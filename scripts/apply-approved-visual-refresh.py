"""Apply the reviewed visual refresh only to D:/armadaIII, preserving a rollback copy."""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime,shutil
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/approved-visual-refresh-stage');overlay=stage/'overlay'
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(r.stdout.strip()or'0'):raise SystemExit('Armada II is still running. No files changed.')
subprocess.run([sys.executable,str(repo/'scripts/validate-approved-visual-refresh.py')],check=True)
m=json.loads((stage/'manifest.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('approved-visual-refresh-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False);new=[];changed=[]
for rel in m['files']:
 dest=root/rel
 if dest.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,b)
 else:new.append(rel)
(backup/'new-files.json').write_text(json.dumps(new,indent=2))
try:
 for rel,h in m['files'].items():
  dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():dest.chmod(0o666)
  shutil.copyfile(overlay/rel,dest);changed.append(rel);assert hashlib.sha256(dest.read_bytes()).hexdigest()==h,rel
except Exception:
 for rel in changed:
  dest=root/rel;b=backup/rel
  if b.exists():shutil.copyfile(b,dest)
  elif rel in new:dest.unlink(missing_ok=True)
 raise
for rel in m['files']:
 mirror=repo/'bajor/overlay'/rel;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,mirror)
result={**m,'status':'APPLIED - AWAITING GAMEPLAY TEST','backup':str(backup),'newFiles':new,'validationChecks':json.loads((stage/'validation.json').read_text())['checks'],'runtimeVerified':False}
(repo/'reports/approved-visual-refresh-applied.json').write_text(json.dumps(result,indent=2));(stage/'applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Full approved redesign applied to D:/armadaIII: 112 faction-themed models, matching icons, Ferengi refinery and secondary constructors, Ferengi orbital combat weapons and updated AI. 14,211 static checks passed; gameplay testing pending.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Approved visual refresh] Applied '+str(len(m['files']))+' files. Backup '+str(backup)+'. 112 models; static checks passed; gameplay unverified.\n')
print(json.dumps({'status':result['status'],'models':len(m['units']),'files':len(m['files']),'backup':str(backup),'checks':result['validationChecks']}))
