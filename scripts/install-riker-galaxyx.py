from pathlib import Path
import json,shutil,subprocess,datetime
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/riker-galaxyx')
# Stock menu has no F13 action; use clickable final slot without an invalid shortcut.
p=o/'odf/ships/xhfriker.odf';p.write_text(p.read_text(encoding='latin1').replace('hotkeyLabel = "HOTKEY_F13"','hotkeyLabel = ""'),encoding='latin1')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('riker-galaxyx-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in o.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(o);dst=r/rel
 if dst.exists():back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back)
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert p.read_bytes()==dst.read_bytes();dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);files.append(str(rel))
f=repo/'reports/riker-galaxyx.json';d=json.loads(f.read_text());d.update(installed=True,backup=str(b),files=files);f.write_text(json.dumps(d,indent=2))
f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed Cpt William T Riker Galaxy-X hero at Laforge\'s Shipyard: three-nacelle model, five offensive banks (three more than Galaxy), cloak, matching build icon and tech availability. Existing installed model reused after Armada Files lookup. Nine files backed up/verified; fresh-game test pending.';s['features'].append({'id':'riker-galaxyx','title':'Riker Galaxy-X hero','steps':[{'label':'Check source and model','done':True},{'label':'Weapons, cloak, icons and tech','done':True},{'label':'Install and validate','done':True},{'label':'Gameplay test','done':False}]});s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled Riker Galaxy-X hero: five offensive banks plus cloak; buildable only in fyard3. Nine files backed up and verified. Gameplay pending.\n')
print('Installed',len(files),'files; backup',b)
