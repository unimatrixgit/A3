from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
R=Path('D:/armadaIII');O=Path('D:/Xaramada-Modwork/borg-assimilation-stations');repo=Path('D:/aramada')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
report=json.loads((repo/'reports/borg-assimilation-support.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('borg-assimilation-support-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);old=[]
for item in report['files']:
 rel=Path(item['path']);src=O/rel;dst=R/rel;assert hashlib.sha256(src.read_bytes()).hexdigest()==item['sha256']
 old.append({'path':str(rel),'existed':dst.exists()})
 if dst.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
(backup/'manifest.json').write_text(json.dumps(old,indent=2))
for item in report['files']:
 rel=Path(item['path']);src=O/rel;dst=R/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert hashlib.sha256(dst.read_bytes()).hexdigest()==item['sha256']
 if src.suffix.lower()in['.odf','.tt','.spr']:
  dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
report['installed']=True;report['backup']=str(backup);report['gameplayVerified']=False;(repo/'reports/borg-assimilation-support.json').write_text(json.dumps(report,indent=2))
sfile=repo/'status.json';s=json.loads(sfile.read_text());s['current']='Installed Borg assimilation support in Armada III only. Harvester Station: 200 crew. Assimilation Station: 500 crew, produces Borg Repair Drone. Native Recrew enabled by crewed facility flags. All 36 files hash verified; gameplay test pending.';f=next(f for f in s['features']if f['id']=='borg-assimilation-support');f['steps'][2]['done']=True;s['steps']=[{'label':f['title']+': '+a['label'],'done':a['done']}for f in s['features']for a in f['steps']];sfile.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a')as log:log.write('\nInstalled Borg support: 36 backed-up/hash-verified files to D:/armadaIII only. Runtime test pending.\n')
print('Installed 36 files; backup',backup)
