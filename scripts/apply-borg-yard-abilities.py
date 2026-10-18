from pathlib import Path
import re,json,datetime,shutil,stat,subprocess
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
stage=Path('D:/Xaramada-Modwork/borg-yard-abilities');files=[];rows=[]
def put(rel,t):
 p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1');files.append(str(rel))
ships=sorted({v for yard in ['byard','byard2','byard3']for k,v in props(yard).items()if re.fullmatch('builditem[0-9]+',k)})
for n in ships:
 a=props(n);p=idx[n.lower()+'.odf'];t=p.read_text(encoding='latin1');weapons=[v for k,v in sorted(a.items(),key=lambda x:int(x[0][6:])if re.fullmatch('weapon[0-9]+',x[0])else 999)if re.fullmatch('weapon[0-9]+',k)];before=list(weapons)
 cube='cube'in a.get('unitname','').lower()or n in ['bmama','blocutus','xoblocutus'];used=set()
 for w in weapons:
  d=props(w)
  if d.get('special')=='1':
   for k in ['buttonslot','popupslot']:
    if d.get(k,'').isdigit():used.add(int(d[k]))
 hp=a.get('weaponhardpoints1','hp01').split('"')[0].strip();added=[]
 warp=any(props(w).get('ordname','').lower()=='twarpd'or w.lower()in ['gtwarpd','xactwarp','xabtrans5','xbtpwarp']for w in weapons)
 blue=any(w.lower()in ['gborgbor','xacassim','xbtpblue']for w in weapons);green=any(w.lower()in ['xacgreen','xbtpgreen']for w in weapons)
 def add(base):
  slot=next((s for s in range(1,10)if s not in used),None);assert slot is not None,(n,'no free HUD slot');used.add(slot);name='xy_'+n+'_'+base.lower();put(Path('odf/special_weapons')/(name+'.odf'),f'#include "{base}.odf"\nbuttonSlot = {slot}\npopupSlot = {slot}\nhotkeyLabel = "HOTKEY_F{slot}"\n');weapons.append(name);added.append(dict(weapon=base,buttonSlot=slot));return name
 if not warp:add('gtwarpd')
 if cube and not green:add('xacgreen')
 if not cube and not blue:add('gborgbor')
 # A distinct active ability beyond travel/assimilation,excluding self destruct and passive detection.
 other=any(props(w).get('special')=='1'and w.lower()not in ['gselfdes','gtwarpd','xactwarp','xabtrans5','xbtpwarp','xacgreen','xbtpgreen','gborgbor','xacassim','xbtpblue','gtechassimbeam']and props(w).get('classlabel','').lower()!='detectcloak'for w in before)
 if not other:add('gregen')
 for i,w in enumerate(weapons[len(before):],len(before)+1):t+=f'\nweapon{i} = "{w}"\nweaponHardpoints{i} = "{hp}"\n'
 assert len(weapons)<=16,(n,len(weapons))
 if added:
  cap=int(float(a.get('maxextraweapons','0')));energy=max(float(a.get('maxspecialenergy','0')),500*(4+cap));regen=max(float(a.get('specialenergyrate','0')),5*(4+cap))
  for key,value in [('maxSpecialEnergy',int(energy)),('specialEnergyRate',int(regen))]:
   t=re.sub(r'^\s*'+key+r'\s*=.*$',f'{key} = {value}',t,flags=re.M|re.I)if re.search(r'^\s*'+key+r'\s*=',t,re.M|re.I)else t+f'\n{key} = {value}\n'
  put(p.relative_to(root),t)
 rows.append(dict(ship=n,cube=cube,added=added,weaponCount=len(weapons)))
running=subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode!=0;backup=Path('D:/Xaramada-Modwork/backups')/('borg-yard-abilities-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
if not running:
 for rel in files:
  p=root/rel
  if p.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.chmod(p.stat().st_mode|stat.S_IWRITE)
  p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stage/rel,p);o=repo/'overlay'/rel;o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o)
report=dict(installed=not running,stage=str(stage),backup=str(backup)if not running else None,ships=rows,files=files,gameplayVerified=False,notes=['Existing green beam on non-cubes preserved;blue added alongside it.','No blue beams added to cubes.','Distinct extra ability ensured;regeneration used when absent.','No ship costs or combat stats changed;energy minima use cube formula.']);(repo/'reports/borg-yard-abilities.json').write_text(json.dumps(report,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']=('Staged'if running else'Installed')+f' Borg three-yard ability pass:{len(ships)} ships checked;{sum(bool(x["added"])for x in rows)} updated with transwarp,correct-color beam and distinct special ability. Gameplay pending.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(dict(installed=not running,ships=len(ships),updated=[x for x in rows if x['added']])))
