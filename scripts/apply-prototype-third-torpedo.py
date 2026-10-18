from pathlib import Path
import re,json,shutil,datetime,stat,subprocess
r=Path('D:/armadaIII');repo=Path('D:/aramada');rel=Path('odf/ships/brenborg.odf');p=r/rel;t=p.read_text(encoding='latin1')
assert 'weapon7 = "xbtpgreen"'in t,'Unexpected prototype loadout'
# Insert normal launcher before specials; move matching hardpoint rows together.
def shift(m):return m[1]+str(int(m[2])+1)+m[3]if int(m[2])>=7 else m[0]
t=re.sub(r'(?mi)^(weapon(?:Hardpoints)?)(\d+)(\s*=.*)$',shift,t)
t=t.replace('weapon8 = "xbtpgreen"','weapon7 = "bm4phot"\nweaponHardpoints7 = "hp14" "hp15"\nweapon8 = "xbtpgreen"');assert sorted(map(int,re.findall(r'^weapon(\d+)\s*=',t,re.M)))==list(range(1,14))
stage=Path('D:/Xaramada-Modwork/transwarp-prototype-third-torpedo')/rel;stage.parent.mkdir(parents=True,exist_ok=True);stage.write_text(t,encoding='latin1');running=subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode!=0
backup=Path('D:/Xaramada-Modwork/backups')/('prototype-third-torpedo-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
if not running:
 b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.chmod(p.stat().st_mode|stat.S_IWRITE);shutil.copy2(stage,p);o=repo/'overlay'/rel;shutil.copy2(p,o);assert p.read_bytes()==stage.read_bytes()
d=dict(installed=not running,weapon='bm4phot',source='bsphere weapon7',shotDelaySeconds=.375,weaponSlot=7,totalWeaponSlots=13,specialEnergyUnchanged='3000 capacity /30 regeneration',backup=str(backup)if not running else None,gameplayVerified=False);(repo/'reports/transwarp-prototype-third-torpedo.json').write_text(json.dumps(d,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']=('Staged'if running else'Installed')+' third rapid-fire torpedo on Transwarp Prototype:large-sphere bm4phot,0.375s refire;special weapon order retained,energy unchanged. Gameplay pending.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(d))
