from pathlib import Path
import json,shutil,datetime,stat,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII').resolve();p=repo/'reports/last-man-standing-loader-test.json';d=json.loads(p.read_text());backup=Path(d['backup']);q=Path('D:/Xaramada-Modwork/backups')/('loader-test-withdrawn-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
restored=[];withdrawn=[]
for rel in d['files']:
 live=(root/rel).resolve();assert live.is_relative_to(root)and live!=root,live
 old=backup/rel;overlay=(repo/'overlay'/rel).resolve();assert overlay.is_relative_to((repo/'overlay').resolve())
 if old.exists():
  dest=q/'live'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(live,dest);live.chmod(live.stat().st_mode|stat.S_IWRITE);shutil.copy2(old,live);assert old.read_bytes()==live.read_bytes();overlay.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,overlay);restored.append(rel)
 else:
  for source,label in [(live,'live'),(overlay,'overlay')]:
   if source.exists():dest=q/label/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(source),str(dest))
  withdrawn.append(rel)
d.update(installed=False,withdrawnAfterCrash=True,withdrawalBackup=str(q),restored=restored,withdrawn=withdrawn,notes=d['notes']+['Native crash0x547b1b before MMM loader appears in dump and before first Lua log. Test integration withdrawn;25AI patches retained.']);p.write_text(json.dumps(d,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']='Loader-test crash recovery applied:original mission menus restored;4new experimental test files quarantined outside game.25AI improvements and Cardassian mining fix retained.No experimental mission loader active.Gameplay retest pending.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(dict(restored=restored,withdrawn=withdrawn,quarantine=str(q))))
