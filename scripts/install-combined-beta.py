from pathlib import Path
import json,datetime,subprocess,shutil,stat,re,hashlib
repo=Path('D:/aramada');root=Path('D:/armadaIII');names=['screen-ships-beta','borg-ai-beta','small-ship-scale-beta','borg-final-adjustments']
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running; installation deferred'
backup=Path('D:/Xaramada-Modwork/backups')/('combined-beta-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));manifest=[]
for name in names:
 report=repo/'reports'/(name+'.json');d=json.loads(report.read_text());stage=Path(d['stage'])
 for rel in d['files']:
  src=stage/rel;dst=root/rel;assert src.is_file();existed=dst.exists();b=backup/rel
  if existed and not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
  if existed:dst.chmod(dst.stat().st_mode|stat.S_IWRITE)
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();o=repo/'overlay'/rel;o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,o);manifest.append(dict(path=rel,existed=existed,sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
 d.update(installed=True,backup=str(backup),gameplayVerified=False);report.write_text(json.dumps(d,indent=2))
backup.mkdir(parents=True,exist_ok=True);(backup/'manifest.json').write_text(json.dumps(manifest,indent=2));p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Installed beta patch: six command ships, five Borg AI profiles,14 small-ship size increases using Defiant +35% minimum,Scout Cube crew150,orbital beam and torpedo banks. Backed up and file-verified; gameplay testing pending.';s.setdefault('features',[]).append(dict(id='combined-beta',title='Combined beta patch',steps=[dict(label='Six command ships and icons',done=True),dict(label='Borg AI producer and prerequisite audit',done=True),dict(label='Small-ship scales and Borg adjustments installed',done=True),dict(label='In-game beta testing',done=False)]));s['steps']=[dict(label=f['title']+': '+x['label'],done=x['done'])for f in s['features']for x in f['steps']];p.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\nCombined beta installed; backed up; gameplay testing pending.\n');print('Installed',len(manifest),'files. Backup:',backup)
