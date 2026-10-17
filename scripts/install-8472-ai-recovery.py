from pathlib import Path
import subprocess,shutil,datetime,json,hashlib
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/8472-ai-recovery')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Close Armada III before installing'
b=Path('D:/Xaramada-Modwork/backups')/('8472-ai-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in o.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(o);dest=r/rel;back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,back);shutil.copy2(p,dest);assert p.read_bytes()==dest.read_bytes();mirror=repo/'overlay'/rel;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,mirror);files.append({'path':str(rel),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
f=repo/'reports/8472-ai-recovery.json';d=json.loads(f.read_text());d.update(installed=True,backup=str(b),installedFiles=files);f.write_text(json.dumps(d,indent=2))
f=repo/'status.json';d=json.loads(f.read_text(encoding='utf-8-sig'));d['current']='Installed Species 8472 AI recovery: mothership constructor access and five economy/research-first AI plans. Six files backed up and hash verified. Fresh-match AI production test pending.'
for feature in d['features']:
 if feature['id']=='8472-ai-recovery':feature['steps'][2]['done']=True
d['steps']=[{'label':a['title']+': '+s['label'],'done':s['done']}for a in d['features']for s in a['steps']];f.write_text(json.dumps(d,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled six-file 8472 AI recovery; backup '+str(b)+'. Gameplay pending.\n')
print('Installed',len(files),'files. Backup',b)
