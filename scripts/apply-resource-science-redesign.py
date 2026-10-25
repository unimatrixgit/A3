from pathlib import Path
import json,hashlib,subprocess,sys,datetime,shutil
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/resource-science-redesign-stage');overlay=stage/'overlay'
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(r.stdout.strip()or'0'):raise SystemExit('Armada II is still running; no files changed.')
subprocess.run([sys.executable,str(repo/'scripts/validate-resource-science-redesign.py')],check=True)
pack=json.loads((stage/'manifest.json').read_text());validation=json.loads((stage/'validation.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('resource-science-redesign-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False);new=[];changed=[]
for rel in pack['files']:
 dest=root/rel
 if dest.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,b)
 else:new.append(rel)
(backup/'new-files.json').write_text(json.dumps(new,indent=2))
try:
 for rel,h in pack['files'].items():
  dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():dest.chmod(0o666)
  shutil.copyfile(overlay/rel,dest);changed.append(rel);assert hashlib.sha256(dest.read_bytes()).hexdigest()==h,rel
except Exception:
 for rel in changed:
  dest=root/rel;b=backup/rel
  if b.exists():shutil.copyfile(b,dest)
  elif rel in new:dest.unlink(missing_ok=True)
 raise
for rel in pack['files']:
 dest=repo/'bajor/overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
result={**pack,'status':'APPLIED - AWAITING GAMEPLAY TEST','backup':str(backup),'newFiles':new,'validationChecks':validation['checks'],'researchFacilities':validation['researchFacilities'],'researchPodMounts':validation['researchPodMounts'],'runtimeVerified':False};(repo/'reports/resource-science-redesign-applied.json').write_text(json.dumps(result,indent=2));(stage/'applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Resource / science redesign applied: 67 models; all 34 research facilities and 184 pod mounts; upgrade centres, Omega labs, resource freighters / refineries, Borg assimilation structures, Recycler and repair drone. Other orbitals +20%; Borg matches enlarged Federation orbital. Static checks passed; gameplay testing pending.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Resource / science redesign] Applied '+str(len(pack['files']))+' files; '+str(validation['checks'])+' static checks. Backup '+str(backup)+'. Runtime testing pending.\n')
print(json.dumps({'status':result['status'],'models':len(pack['units']),'researchFacilities':validation['researchFacilities'],'podMounts':validation['researchPodMounts'],'orbitalResizes':len(pack.get('orbitalResize',[])),'files':len(pack['files']),'backup':str(backup)}))
