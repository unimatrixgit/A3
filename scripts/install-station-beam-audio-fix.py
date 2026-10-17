from pathlib import Path
import subprocess,shutil,datetime,json
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/station-beam-audio-fix');assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game still running'
b=Path('D:/Xaramada-Modwork/backups')/('station-beam-audio-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in o.rglob('*.odf'):
 rel=p.relative_to(o);dst=r/rel;back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back);shutil.copy2(p,dst);assert dst.read_bytes()==p.read_bytes();shutil.copy2(p,repo/'overlay'/rel);files.append(str(rel))
assert len(files)==4
f=repo/'reports/station-beam-audio-fix.json';d=json.loads(f.read_text());d.update(installed=True,backup=str(b));f.write_text(json.dumps(d,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed station-only audio hotfix: silenced beam fireSound on four automatic/manual station weapons. Ships unchanged; autofire and HUD controls retained. Four files backed up and verified. Gameplay confirmation pending.';f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled four-file station beam audio hotfix; backup '+str(b)+'. Runtime confirmation pending.\n')
print('Installed and verified four files. Backup:',b)
