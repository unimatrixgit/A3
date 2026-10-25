from pathlib import Path
import json,hashlib,datetime,subprocess,shutil,os
repo=Path('D:/aramada');root=Path('D:/armadaIII');report=repo/'reports/8472-production-recovery-staged.json';r=json.loads(report.read_text());stage=Path(r['stage']);assert r['status']=='staged only; not applied'
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
for x in r['manifest']:
 assert hashlib.sha256((root/x['file']).read_bytes()).hexdigest()==x['sourceSHA256'],('Live file changed',x['file'])
 assert hashlib.sha256((stage/x['file']).read_bytes()).hexdigest()==x['stagedSHA256'],('Staged file changed',x['file'])
backup=Path('D:/Xaramada-Modwork/backups')/('8472-production-recovery-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));written=[]
try:
 for x in r['manifest']:
  rel=x['file'];data=(stage/rel).read_bytes()
  for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
   dst=base/rel;b=backup/label/rel;exists=dst.exists()
   if exists:b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);os.chmod(dst,0o666)
   dst.parent.mkdir(parents=True,exist_ok=True);written.append((dst,b,exists));dst.write_bytes(data);assert hashlib.sha256(dst.read_bytes()).hexdigest()==x['stagedSHA256']
except Exception:
 for dst,b,exists in reversed(written):
  if exists:shutil.copy2(b,dst)
  elif dst.exists():dst.unlink()
 raise
r['status']='applied; awaiting in-game AI production test';r['applied']=True;r['appliedAt']=datetime.datetime.now().astimezone().isoformat();r['backup']=str(backup);report.write_text(json.dumps(r,indent=2));(repo/'reports/8472-production-recovery-applied.json').write_text(json.dumps(r,indent=2))
p=repo/'reports/8472-production-recovery-staged.md';s=p.read_text(encoding='utf-8').replace('Species8472 production recovery - staged','Species8472 production recovery - applied').replace('Not applied to the live game.','Applied to D:/armadaIII; in-game AI test pending.');p.write_text(s,encoding='utf-8')
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='APPLIED8472 production recovery:9 files verified. All5 AI plans replenish consumed embryos; fixed Advanced Hatchery/conventional defence construction flags and Mine evolution routing. Original starting fleet, biomatter costs, icons and other factions preserved. Static consumptive-production audit passed; new-match AI test pending.';s['updated']=r['appliedAt'];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'applied':True,'verifiedFiles':len(r['files']),'backup':str(backup)}))
