from pathlib import Path
import subprocess,shutil,datetime,json
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
r=Path('D:/armadaIII');repo=Path('D:/aramada');rel=Path('odf/stations/bbase.odf');src=Path('D:/Xaramada-Modwork/borg-nexus-weapons')/rel;dst=r/rel;b=Path('D:/Xaramada-Modwork/backups')/('nexus-weapons-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))/rel;b.parent.mkdir(parents=True);shutil.copy2(dst,b);shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();shutil.copy2(src,repo/'overlay'/rel)
f=repo/'reports/borg-nexus-weapons.json';d=json.loads(f.read_text());d.update(installed=True,backup=str(b));f.write_text(json.dumps(d,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed Nexus defense upgrade: six pulse disruptor banks and two torpedo launchers. One file backed up and verified; damage per bank, hull, shields and costs unchanged. Fresh-match test pending.'
for a in s['features']:
 if a['id']=='borg-nexus-weapons':a['steps'][2]['done']=True
s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nNexus weapon patch installed: 6 pulse banks / 2 launchers; backup '+str(b)+'. Gameplay pending.\n')
print('Installed and verified Nexus weapon patch.')
