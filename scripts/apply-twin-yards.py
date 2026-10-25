"""Apply only the validated standalone station patch and keep an exact rollback."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/twin-yards-20261025';O=stage/'overlay'
assert not(stage/'applied.json').exists(),'Already applied; inspect transaction before another application.'
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True);assert int(r.stdout.strip()or'0')==0,'Game is running; nothing applied.'
m=json.loads((stage/'manifest.json').read_text());v=json.loads((stage/'validation.json').read_text());assert v['status']=='PASS',v['errors'];backup=Path('D:/Xaramada-Modwork/backups')/('twin-yards-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False);new=[];changed=[]
for rel,h in m['files'].items():
 target=(root/rel).resolve();assert target.is_relative_to(root.resolve())and not rel.lower().startswith(('bzn/','maps/','missions/','events/'));assert hashlib.sha256((O/rel).read_bytes()).hexdigest()==h,rel
 if target.exists():
  assert hashlib.sha256(target.read_bytes()).hexdigest()==m['sourceHashes'][rel],rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,b)
 else:new.append(rel)
(backup/'new-files.json').write_text(json.dumps(new,indent=2));(backup/'transaction.json').write_text(json.dumps(m,indent=2))
try:
 for rel,h in m['files'].items():
  target=root/rel;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():target.chmod(0o666)
  changed.append(rel);shutil.copyfile(O/rel,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==h,rel
except Exception:
 for rel in reversed(changed):
  target=(root/rel).resolve();assert target.is_relative_to(root.resolve());old=backup/rel
  if old.is_file():shutil.copyfile(old,target)
  elif rel in new:target.unlink(missing_ok=True)
 raise
for rel,h in m['files'].items():
 target=repo/'bajor/overlay'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==h,rel
result={'status':'APPLIED - GAMEPLAY TEST PENDING','target':str(root),'backup':str(backup),'files':len(m['files']),'models':m['models'],'staticChecks':v['checks'],'newFiles':new,'runtimeVerified':False,'nextPatch':'ON HOLD as requested','mapsUntouched':True,'borgRecyclerUntouched':True,'appliedAt':datetime.datetime.now().astimezone().isoformat()};(stage/'applied.json').write_text(json.dumps(result,indent=2));(repo/'reports/twin-yards-applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Standalone twin-yard patch installed: 76 faction models/icons, 29 production definitions, 10 repair/recrew/decommission docks, matching research stations and HWP fortresses, 23 mining stations +15% size/footprint. 40 AI profiles updated. Static validation passed; gameplay testing pending. Next patch ON HOLD.';s['twinYards']=result;s['nexusPatch']={'status':'CANCELLED AND ROLLED BACK'};(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Twin yards] '+json.dumps({k:x for k,x in result.items()if k!='newFiles'})+'\n')
print(json.dumps({k:x for k,x in result.items()if k!='newFiles'}))
