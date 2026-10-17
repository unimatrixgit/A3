from pathlib import Path
import re,json,shutil,datetime,subprocess,stat
exec(Path('D:/aramada/scripts/audit-all-faction-ai-sequence.py').read_text().split('issues=[];profiles=[]')[0])
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
backup=Path('D:/Xaramada-Modwork/backups')/('all-ai-cleanup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));patches=[];failures=[]
for race in factions:
 for p in(root/'AI/AIPs').glob(race+'_*list.aip'):
  avail={v.lower().removesuffix('.odf')+'.odf'for k,v in props({'federation':'fed','klingon':'kling','romulan':'rom','cardassian':'card'}.get(race,race)).items()if re.fullmatch('standardunits[0-9]+',k)};added=[]
  def ensure(n,trail=None):
   if n in avail:return
   trail=set()if trail is None else set(trail)
   if n in trail or n not in tt:raise ValueError('Unreachable '+n)
   trail.add(n)
   for dep in tt[n]:ensure(dep,trail)
   choices=producers.get(n,[])
   if not any(x in avail for x in choices):
    candidates=[x for x in choices if props(x).get('race','').lower()in [race,{'federation':'fed','klingon':'kling','romulan':'rom','cardassian':'card'}.get(race,race)]]
    if not candidates:raise ValueError('No faction producer '+n)
    success=False
    for producer in candidates:
     before=set(avail);length=len(added)
     try:ensure(producer,trail);success=True;break
     except ValueError:avail.clear();avail.update(before);del added[length:]
    if not success:raise ValueError('Producer cycle '+n)
   avail.add(n);added.append(n)
  t=p.read_text(encoding='latin1');lines=[];inserted=[]
  for line in t.splitlines():
   m=re.match(r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,',line)
   if m:
    n=m[1].lower()+'.odf';added=[]
    try:ensure(n)
    except ValueError as e:failures.append(dict(profile=p.name,unit=n,error=str(e)));break
    for a in added:
     if a!=n:lines.append(f'    "{a[:-4]}", 1, 0, -1, 0, // prerequisite / producer before dependent unit');inserted.append(a)
   lines.append(line)
  else:
   if not inserted:continue
   text='\n'.join(lines)+'\n';text=re.sub(r'int\s+checkTechnologyAvailable\s*=\s*0\s*;', 'int checkTechnologyAvailable = 1;',text)
   rel=p.relative_to(root);dst=Path('D:/Xaramada-Modwork/all-ai-cleanup')/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(text,encoding='latin1');patches.append(dict(file=str(rel),inserted=inserted,stage=str(dst)))
assert not failures,failures
for x in patches:
 p=root/x['file'];b=backup/x['file'];b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.chmod(p.stat().st_mode|stat.S_IWRITE);shutil.copy2(x['stage'],p);o=repo/'overlay'/x['file'];o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o)
(repo/'reports/all-ai-cleanup-patch.json').write_text(json.dumps(dict(patches=patches,failures=failures,backup=str(backup),gameplayVerified=False),indent=2));print('Patched',len(patches),'profiles;',sum(len(x['inserted'])for x in patches),'prerequisite/producer insertions.')
