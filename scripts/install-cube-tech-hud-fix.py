from pathlib import Path
import subprocess,datetime,shutil,json,stat,re
r=Path('D:/armadaIII');repo=Path('D:/aramada');rel=Path('odf/special_weapons/gTechAssimBeam.odf');src=Path('D:/Xaramada-Modwork/cube-tech-button-fix')/rel;dst=r/rel
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game still running'
b=Path('D:/Xaramada-Modwork/backups')/('cube-tech-hud-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))/rel;b.parent.mkdir(parents=True);shutil.copy2(dst,b);dst.chmod(dst.stat().st_mode|stat.S_IWRITE);shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():dest.chmod(dest.stat().st_mode|stat.S_IWRITE)
shutil.copy2(src,dest);t=dst.read_text(encoding='latin1');assert re.search(r'^buttonSlot\s*=\s*7$',t,re.M);assert re.search(r'^popupSlot\s*=\s*7$',t,re.M)
f=repo/'reports/cube-captured-tech-audit.json';d=json.loads(f.read_text());d['hudFixInstalled']=True;d['backup']=str(b);d['fixStaged']='Installed technology beam buttonSlot7/popupSlot7; adaptation remains slot6.';f.write_text(json.dumps(d,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed cube HUD fix: technology-assimilation button/popup slot7, separate from shield adaptation slot6. All16 cube capacities and beam references checked. Captured foreign button collisions and Omega full-capacity display remain gameplay-unverified.';f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled cube Tech Assimilation HUD slot7 fix; backup '+str(b)+'. Existing shield adaptation slot6 retained.\n')
print('Installed and verified technology-assimilation HUD slot7.')
