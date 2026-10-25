"""Withdraw native collector tiers/yards; retain Ferengi equipment and refit chains."""
from pathlib import Path
import re,json,hashlib,shutil,subprocess,datetime
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=repo/'patches/remove-native-mining-upgrades-20261025';O=stage/'overlay'
pack=json.loads((repo/'patches/mining-yards-20261025/gameplay.json').read_text());idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};pending={};checks=[]
def text(path):
 rel=path.relative_to(root).as_posix();return pending[rel]if rel in pending else path.read_text(encoding='latin1')
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=text(idx[n]);d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):d.update(props(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def ck(ok,label):
 assert ok,label
 checks.append(label)
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+str(v)+'\n'
def save(p,t):pending[p.relative_to(root).as_posix()]=t
native_refits=[r for r in pack['refits']if not r['source'].startswith(('xfg','xbg'))]
ferengi_refits=[r for r in pack['refits']if r['source'].startswith(('xfg','xbg'))]
disabled={r['yard']for r in pack['yards']}|{n for r in pack['yards']for n in r['miners'][1:]}|{r['weapon']for r in native_refits}|{'myfpod1','myfpod2','xsbiolab','xsbio1','xsbio2'}
before={n:props(n)for n in idx};keep=['ffreight','bfreight','kfreight','rfreight','cfreight','dfreight','xdominer','bjfreight','brfreight','8472_collector'];ferengi_hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in(root/'odf').rglob('*.odf')if p.stem.lower().startswith(('xfg','xbg'))}

# Remove native collector refit weapons, never the Ferengi refit abilities.
for p in(root/'odf').rglob('*.odf'):
 n=p.stem.lower()
 if n in disabled:continue
 t=p.read_text(encoding='latin1');d=before[n];changed=False
 banks=sorted((int(k[6:]),v)for k,v in d.items()if re.fullmatch(r'weapon\d+',k))
 if any(v.lower()in disabled for i,v in banks):
  ck(not n.startswith(('xfg','xbg')),'No Ferengi weapon strip')
  t=re.sub(r'(?mi)^[ \t]*(?:weapon\d+|weaponHardpoints\d+)[ \t]*=[^\r\n]*','',t)
  for new,(old,w)in enumerate([(i,w)for i,w in banks if w.lower()not in disabled],1):
   t=put(t,'weapon'+str(new),'"'+w+'"');t=put(t,'weaponHardpoints'+str(new),'"'+d['weaponhardpoints'+str(old)]+'"')
  changed=True
 # Remove yard/lab/tier menu entries and compact the remaining build order.
 items=sorted((int(k[9:]),v)for k,v in d.items()if re.fullmatch(r'builditem\d+',k))
 if any(v.lower()in disabled for i,v in items):
  t=re.sub(r'(?mi)^[ \t]*buildItem\d+[ \t]*=[^\r\n]*','',t)
  for i,(old,v)in enumerate([(i,v)for i,v in items if v.lower()not in disabled]):t=put(t,'buildItem'+str(i),'"'+v+'"')
  changed=True
 if n=='fresear2':
  t=put(t,'podHardpoints',' '.join('"'+hp+'"'for hp in re.findall(r'[A-Za-z0-9_]+',d['podhardpoints'])if hp!='myminingpod'));changed=True
 if changed:save(p,t)

# Disable in every technology mode, including Full Tech. Keep archived definitions
# and their assets in place, avoiding destructive deletion of models or save data.
for file in(root/'techtree').glob('*.tt'):
 t=file.read_text(encoding='latin1');old=t
 for n in disabled:t=re.sub(r'(?mi)^'+re.escape(n)+r'\.odf[ \t]+[^\r\n]*',n+'.odf -1 // Native mining upgrade / yard withdrawn',t)
 if t!=old:save(file,t)
AI=[]
for file in(root/'AI/AIPs').glob('*.aip'):
 t=file.read_text(encoding='latin1');old=t
 t=re.sub(r'(?mi)^[ \t]*"('+'|'.join(re.escape(n)for n in sorted(disabled))+r')"[ \t]*,[^\r\n]*(?:\r?\n|$)','',t)
 if t!=old:save(file,t);AI.append(file.name)

# Validate withdrawal and retained functionality against current source definitions.
for n in keep:
 d=props(n);original=before[n]
 for k,v in original.items():
  if re.fullmatch(r'weapon\d+|weaponhardpoints\d+',k):continue
  ck(d.get(k)==v,n+': preserves '+k)
 oldbanks=[v for k,v in original.items()if re.fullmatch(r'weapon\d+',k)and v.lower()not in disabled];newbanks=[v for k,v in d.items()if re.fullmatch(r'weapon\d+',k)]
 ck(oldbanks==newbanks,n+': keeps original mining/combat/transwarp weapons')
for n in idx:
 if n in disabled:continue
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+|weapon\d+',k):ck(v.lower()not in disabled,n+': no removed mining menu/weapon target '+v)
for r in ferengi_refits:
 source=props(r['source']);ability=props(r['weapon'])
 ck(r['weapon']in source.values(),r['source']+': Ferengi Upgrade button retained')
 ck(ability['fusedclass']==r['target'],r['source']+': correct Ferengi refit target')
 ck(ability['specialenergycost']=='0',r['source']+': zero-energy Ferengi refit retained')
for tree in(root/'techtree').glob('*.tt'):
 t=text(tree)
 for n in disabled:
  for match in re.findall(r'(?mi)^'+re.escape(n)+r'\.odf[ \t]+(-?\d+)',t):ck(match=='-1',tree.name+': disabled '+n)
for file in(root/'AI/AIPs').glob('*.aip'):
 names=re.findall(r'(?m)^[ \t]*"([^"]+)"[ \t]*,',text(file));ck(not set(n.lower()for n in names)&disabled,file.name+': no withdrawn mining order')
ck(pending['odf/ships/ffreight.odf']==pending['odf/other/ffreight.odf'],'Both Federation collector ODFs remain synchronized')
for rel,h in ferengi_hashes.items():ck(hashlib.sha256(text(root/rel).encode('latin1')).hexdigest()==hashlib.sha256((root/rel).read_text(encoding='latin1').encode('latin1')).hexdigest(),'Ferengi ODF untouched '+rel)
files=[]
for rel,t in pending.items():
 out=O/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'file':rel,'sourceHash':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'stagedHash':hashlib.sha256(out.read_bytes()).hexdigest()})
report={'status':'STAGED','disabledUnits':sorted(disabled),'removedNativeRefits':native_refits,'retainedFerengiRefits':ferengi_refits,'files':files,'AIprofilesChanged':AI,'checks':len(checks),'runtimeVerified':False,'collectorArtworkSizesAndBaseStatsPreserved':True,'FerengiODFsUnchanged':True}
(stage/'manifest.json').write_text(json.dumps(report,indent=2));(repo/'reports/native-mining-removal-prepared.json').write_text(json.dumps(report,indent=2))
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-CimInstance Win32_Process -Filter "Name=\'Armada2.exe\' OR Name=\'Armada.exe\'").Count'],capture_output=True,text=True,check=True)
if int(running.stdout.strip()or'0'):
 print(json.dumps({'status':'STAGED - GAME RUNNING','files':len(files)}));raise SystemExit(0)
backup=Path('D:/Xaramada-Modwork/backups')/('native-mining-removal-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for r in files:
 rel=r['file'];ck(hashlib.sha256((root/rel).read_bytes()).hexdigest()==r['sourceHash'],'unchanged live baseline '+rel);out=backup/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,out)
changed=[]
try:
 for r in files:
  rel=r['file'];(root/rel).chmod(0o666);shutil.copyfile(O/rel,root/rel);changed.append(rel);assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==r['stagedHash']
except Exception:
 for rel in changed:shutil.copyfile(backup/rel,root/rel)
 raise
for r in files:
 rel=r['file'];out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,out)
report.update(status='APPLIED - GAMEPLAY TEST PENDING',backup=str(backup));(repo/'reports/native-mining-removal-applied.json').write_text(json.dumps(report,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Native mining upgrade rollback applied: nine Mining Yards, non-Ferengi collector MK II/III and native mining research/refit buttons withdrawn from menus, technology and AI. Ferengi research, tiers and all seven Ferengi refit chains preserved. Latest basic collector artwork/size and sensor size retained. Gameplay test pending.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as log:log.write('\n[Native mining removal] Applied '+str(len(files))+' files. Removed native yards, upper collector tiers, mining pods/refits and AI orders; retained Ferengi ODFs and seven refit chains. Backup '+str(backup)+'. Gameplay test pending.\n')
print(json.dumps({'status':report['status'],'files':len(files),'withdrawn':len(disabled),'AIprofiles':len(AI),'FerengiRefitsKept':len(ferengi_refits),'checks':len(checks),'backup':str(backup)},indent=2))
