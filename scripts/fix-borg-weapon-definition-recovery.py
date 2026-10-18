from pathlib import Path
import re,json,shutil,datetime,stat,subprocess,winreg
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
backup=Path('D:/Xaramada-Modwork/backups')/('borg-weapon-definition-recovery-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));changes=[]
def flatten(p,seen=None):
 seen=set()if seen is None else set(seen);assert p.name.lower()not in seen;seen.add(p.name.lower());t=p.read_text(encoding='latin1')
 return re.sub(r'^\s*#include\s+"([^"\r\n]+)"[^\r\n]*',lambda m:flatten(idx[m[1].lower()],seen),t,flags=re.M|re.I)
def parsed(t):return{k.lower():v.split('//')[0].strip().strip('"')for k,v in re.findall(r'^\s*(\w+)\s*=\s*([^\r\n]*)',t,re.M)}
def install(p,t):
 rel=p.relative_to(root);b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.chmod(p.stat().st_mode|stat.S_IWRITE);p.write_text(t,encoding='latin1');o=repo/'overlay'/rel;o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o);changes.append(str(rel))
for p in(root/'odf/special_weapons').glob('*.odf'):
 if not(p.stem.startswith('xy_')or p.stem.startswith('xbtp')):continue
 old=props(p.stem);t=flatten(p);assert parsed(t)==old,(p.name,'effective properties changed');assert 'classlabel'in old
 if old.get('ordname'):assert old['ordname'].lower().removesuffix('.odf')+'.odf'in idx
 install(p,t)
p=idx['bbase.odf'];t=p.read_text(encoding='latin1')
for key,value in [('maxSpecialEnergy',2500),('specialEnergyRate',25)]:
 t=re.sub(r'^\s*'+key+r'\s*=.*$',f'{key} = {value}',t,flags=re.M|re.I)if re.search(r'^\s*'+key+r'\s*=',t,re.M|re.I)else t+f'\n{key} = {value}\n'
install(p,t)
# Per-user,per-executable full crash dumps;separate folder and a bounded count.
dumps=Path('D:/Xaramada-Modwork/diagnostics/full-native-dumps');dumps.mkdir(parents=True,exist_ok=True);keyname=r'Software\Microsoft\Windows\Windows Error Reporting\LocalDumps\Armada2.exe';previous={}
with winreg.CreateKey(winreg.HKEY_CURRENT_USER,keyname)as key:
 for n,v,typ in [('DumpFolder',str(dumps),winreg.REG_EXPAND_SZ),('DumpType',2,winreg.REG_DWORD),('DumpCount',2,winreg.REG_DWORD)]:
  try:previous[n]=winreg.QueryValueEx(key,n)
  except FileNotFoundError:previous[n]=None
  winreg.SetValueEx(key,n,0,typ,v)
report=dict(installed=True,files=changes,backup=str(backup),dump='C:/Users/thoma/AppData/Local/CrashDumps/Armada2.exe.9136.dmp',exceptionAddress='0x0066f250',finding='Weapon update dereferences null weapon definition at+0x14;minidump lacks weapon object heap,exact weapon identity unconfirmed.',nexusFix='2500 special energy /25 regeneration;previously0/0 despite green beam.',aliasFix='37 recent Borg special definitions flattened to standalone files;effective properties compared equal.',fullCrashDumpFolder=str(dumps),priorUserRegistryValues=previous,gameplayVerified=False,causeConfirmed=False);(repo/'reports/borg-weapon-definition-recovery.json').write_text(json.dumps(report,indent=2));cache.clear();assert props('bbase')['maxspecialenergy']=='2500';p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Installed Borg weapon compatibility recovery:37new ability aliases flattened with settings preserved;Nexus energy fixed2500/25.Full per-user Armada2 dumps enabled(count2).Exact crashing weapon not retained in old minidump;gameplay retest required.';p.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print('Installed',len(changes),'files. Backup:',backup)
