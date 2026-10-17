from pathlib import Path
import re,json,subprocess,datetime,shutil,stat
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
out=Path('D:/Xaramada-Modwork/borg-green-heavy');changes=[];checked=[]
for p in list((root/'odf/ships').glob('*.odf'))+[idx['bbase.odf']]:
 a=props(p.stem)
 def num(v):
  try:return float(str(v).rstrip('f'))
  except:return 0
 if p.stem!='bbase'and(a.get('race','').lower()!='borg'or max(num(a.get('crewcost',0)),num(a.get('maximumcrew',0)))<=1500):continue
 weapons={int(k[6:]):v for k,v in a.items()if re.fullmatch('weapon[0-9]+',k)};checked.append(p.stem)
 if any(v.lower() in ['xacgreen','xbassimbeam','xbassimmanual']for v in weapons.values()):continue
 assert sorted(weapons)==list(range(1,max(weapons)+1)),p.stem
 slot=max(weapons)+1;assert slot<=16,(p.stem,slot)
 hp=a.get('weaponhardpoints1','hp01').split('"')[0].strip();assert hp
 t=p.read_text(encoding='latin1')+f'\n// Green assimilation beam for heavy Borg crew capacity / Nexus.\nweapon{slot} = "xacgreen"\nweaponHardpoints{slot} = "{hp}"\n';rel=p.relative_to(root);dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(t,encoding='latin1');changes.append(dict(unit=p.stem,file=str(rel),weaponSlot=slot,hardpoint=hp))
running=subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode!=0
backup=Path('D:/Xaramada-Modwork/backups')/('borg-green-heavy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
if not running:
 for x in changes:
  p=root/x['file'];b=backup/x['file'];b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.chmod(p.stat().st_mode|stat.S_IWRITE);shutil.copy2(out/x['file'],p);o=repo/'overlay'/x['file'];o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o)
d=dict(checked=checked,changes=changes,stage=str(out),installed=not running,backup=str(backup)if not running else None,gameplayVerified=False);(repo/'reports/borg-green-heavy.json').write_text(json.dumps(d,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']=('Staged'if running else'Installed')+f' green assimilation beam audit: {len(checked)} heavy Borg vessels/Nexus checked;{len(changes)} missing beams added. Existing weapon order preserved. Gameplay pending.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(d))
