"""Deploy an explicitly manifested game patch and keep source mirrors in sync."""
from pathlib import Path
import argparse,json,hashlib,datetime,subprocess,shutil,re
args=argparse.ArgumentParser();args.add_argument('stage');a=args.parse_args();stage=Path(a.stage).resolve();repo=Path('D:/aramada');root=Path('D:/armadaIII');O=stage/'overlay';p=json.loads((stage/'patch.json').read_text());assert p['status']=='PASS'
running=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(running.stdout.strip()or'0'):raise SystemExit('Game is running; patch remains staged.')
backup=Path('D:/Xaramada-Modwork/backups')/(stage.name+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False);existed={}
for rel,h in p['files'].items():
 target=(root/rel).resolve();assert target.is_relative_to(root.resolve())and not any(x.lower()in ['maps','bzn','missions','events']for x in Path(rel).parts);assert hashlib.sha256((O/rel).read_bytes()).hexdigest()==h;existed[rel]=target.exists()
 if target.exists():
  assert hashlib.sha256(target.read_bytes()).hexdigest()==p['sourceHashes'][rel],rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,b)
try:
 for rel,h in p['files'].items():
  target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(O/rel,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==h
except Exception:
 for rel,old in existed.items():
  if old:shutil.copyfile(backup/rel,root/rel)
  elif(root/rel).is_file():(root/rel).unlink()
 raise
master=repo/'patches/twin-yards-20261025';manifest=json.loads((master/'manifest.json').read_text());design=json.loads((master/'design.json').read_text())
for rel,h in p['files'].items():
 for folder in [repo/'bajor/overlay',master/'overlay']:
  target=folder/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,target)
 manifest['files'][rel]=h;manifest.setdefault('sourceHashes',{})[rel]=h
if p.get('baselineUpdates'):
 idx={x.stem.lower():x for x in(root/'odf').rglob('*.odf')}
 def props(n,seen=None):
  seen=set()if seen is None else seen;assert n not in seen;seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
  for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):v.update(props(Path(inc).stem.lower(),set(seen)))
  for k,x in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):v[k.lower()]=x.split('//')[0].strip().strip('"')
  return v
 for n in p['baselineUpdates']:design['baseline'][n]={'file':idx[n].relative_to(root).as_posix(),'hash':hashlib.sha256(idx[n].read_bytes()).hexdigest(),'properties':props(n)}
design['attackAssignments'].update(p.get('attackAssignments',{}))
for race,units in p.get('extraAiTargets',{}).items():design.setdefault('extraAiTargets',{}).setdefault(race,[]);design['extraAiTargets'][race]=list(dict.fromkeys(design['extraAiTargets'][race]+units))
(master/'design.json').write_text(json.dumps(design,indent=2));(master/'manifest.json').write_text(json.dumps(manifest,indent=2))
result={'status':'APPLIED','backup':str(backup),'files':len(p['files']),'runtimeVerified':False,'description':p.get('description',stage.name)};(stage/'applied.json').write_text(json.dumps(result,indent=2));status=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));status['current']=result['description']+' Applied and file hashes verified; gameplay testing pending.';status.setdefault('patches',{})[stage.name]=result;(repo/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as log:log.write('\n['+stage.name+'] '+json.dumps(result)+'\n')
print(json.dumps(result))
