from pathlib import Path
import json,subprocess,hashlib,datetime,shutil
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/iconian-model-compatibility-stage');m=json.loads((stage/'manifest.json').read_text())
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(r.stdout.strip()or'0'):raise SystemExit('Game is still running; no files applied.')
for rel,h in m['sourceHashes'].items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,('source changed',rel)
for rel,h in m['files'].items():assert hashlib.sha256((stage/'overlay'/rel).read_bytes()).hexdigest()==h,('stage changed',rel)
backup=Path('D:/Xaramada-Modwork/backups')/('iconian-model-compatibility-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False)
new=[]
for rel in m['files']:
 dest=root/rel
 if dest.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,b)
 else:new.append(rel)
(backup/'new-files.json').write_text(json.dumps(new,indent=2))
for rel,h in m['files'].items():
 dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():dest.chmod(0o666)
 shutil.copyfile(stage/'overlay'/rel,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==h
 mirror=repo/'bajor/overlay'/rel;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dest,mirror)
result={**m,'status':'APPLIED - AWAITING GAMEPLAY TEST','backup':str(backup)};(repo/'reports/iconian-model-compatibility-applied.json').write_text(json.dumps(result,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Iconian white-cube model fix applied to all ten arrays: native diffuse-layer flags, 256px textures and small draw meshes. Gameplay fields unchanged. Awaiting in-game confirmation; remaining redesigns still being staged.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Iconian model compatibility] Applied '+str(len(m['files']))+' asset files; backup '+str(backup)+'. Native diffuse-layer flags corrected; gameplay test pending.\n')
print('Applied',len(m['files']),'asset files; backup:',backup)
