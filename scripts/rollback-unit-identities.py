from pathlib import Path
import json,shutil,os,hashlib,datetime,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');r=json.loads((repo/'reports/unit-identity-applied.json').read_text());backup=Path(r['backup']);restored=0;removed=0
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game still running'
for rel in r['files']:
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;src=backup/label/rel;assert dst.resolve().is_relative_to(base.resolve()),dst
  if src.exists():
   if dst.exists():os.chmod(dst,0o666)
   shutil.copy2(src,dst);assert dst.read_bytes()==src.read_bytes();restored+=1
  elif dst.exists():dst.unlink();removed+=1
r['rolledBack']=True;r['rolledBackAt']=datetime.datetime.now().astimezone().isoformat();r['rollbackReason']='Crash while loading match after identity/artwork deployment; source diagnosis pending';(repo/'reports/unit-identity-applied.json').write_text(json.dumps(r,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Rolled back entire839-unit icon/name patch after match-loading crash. Restored previous sprite and ODF files, removed added aliases/atlases. Earlier gameplay patches retained. Investigating new dump; identity pack is NOT ready for deployment.';s['updated']=r['rolledBackAt'];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+'\n')
print(json.dumps({'restoredFiles':restored,'removedNewFiles':removed,'backup':str(backup)}))
