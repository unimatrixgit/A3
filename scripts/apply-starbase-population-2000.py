from pathlib import Path
import json,re,datetime,shutil,stat,subprocess
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game must be closed'
# Station variants only: leave orbital mines, ships, platforms and research facilities alone.
names=['bbase','bjbase','brbase','cbase','dbase','domabase','dombase','fbase','fbase2','fbaseHQ','kbase','kbase2','kimpbase','kmarbase','rbase','rbase2','ds9','fds9','foutpost','fregula','koutpost','cstation']
b=Path('D:/Xaramada-Modwork/backups')/('starbase-crew2000-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));changes=[]
for n in names:
 p=idx[n.lower()+'.odf'];a=props(n);t=p.read_text(encoding='latin1');old=a.get('maximumcrew');t=re.sub(r'^\s*maximumCrew\s*=.*$','maximumCrew = 2000',t,flags=re.M|re.I)if re.search(r'^\s*maximumCrew\s*=',t,re.M|re.I)else t+'\nmaximumCrew = 2000\n'
 rel=p.relative_to(root);back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,back);p.chmod(p.stat().st_mode|stat.S_IWRITE);p.write_text(t,encoding='latin1');dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);changes.append(dict(unit=n,previousMaximum=old,maximumCrew=2000,startingCrew=a.get('crewcost')))
cache.clear();assert all(props(n).get('maximumcrew')=='2000'for n in names)
d=dict(changes=changes,backup=str(b),installed=True,gameplayVerified=False,notes=['Only maximumCrew changed. Starting crew and resource costs preserved. Species8472 uses biomatter and has no normal crew population. Orbital mines and shipyards untouched.']);(repo/'reports/starbase-population-2000.json').write_text(json.dumps(d,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']='Installed 2000 maximum crew for22 starbase/outpost variants. Starting crew and costs unchanged. Backed up and checked; gameplay pending.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\nInstalled22 starbase crew caps:2000. Backup '+str(b)+'\n');print(json.dumps(dict(installed=len(changes),backup=str(b))))
