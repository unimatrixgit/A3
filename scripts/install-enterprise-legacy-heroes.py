from pathlib import Path
import json,subprocess,datetime,shutil,stat
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/enterprise-legacy-heroes');f=repo/'reports/enterprise-legacy-heroes.json';d=json.loads(f.read_text());assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Close Armada III before installing'
b=Path('D:/Xaramada-Modwork/backups')/('enterprise-legacy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));manifest=[]
for rel in d['files']:
 p=o/rel;dst=r/rel;existed=dst.exists()
 if existed:back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back);dst.chmod(dst.stat().st_mode|stat.S_IWRITE)
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert p.read_bytes()==dst.read_bytes();dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);manifest.append({'path':rel,'existed':existed})
b.mkdir(parents=True,exist_ok=True);(b/'manifest.json').write_text(json.dumps(manifest,indent=2));d.update(installed=True,backup=str(b));f.write_text(json.dumps(d,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed Enterprise Legacy Yard via Federation main constructor:Kirk original/A, Harriman B, Garrett C, Picard D, plus existing Archer NX-01. Direct hero production, native icons/voices/models, no fusion upgrades.14 files backed up and verified; gameplay pending.'
for a in s['features']:
 if a['id']=='enterprise-legacy-heroes':a['steps'][3]['done']=True
s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled Enterprise Legacy Yard batch;5 new directly buildable hero variants, existing Archer,14 files. Gameplay pending.\n')
print('Installed',len(manifest),'files. Backup',b)
