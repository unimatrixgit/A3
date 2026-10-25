"""Normalize collectors, synchronize the shadow Federation ODF, enlarge its sensor."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast,datetime,shutil,subprocess
for node in ast.parse((repo/'scripts/stage-approved-visual-refresh.py').read_text()).body:
 if isinstance(node,ast.FunctionDef)and node.name in ['load_model','visible_points']:exec(compile(ast.Module(body=[node],type_ignores=[]),'model-helpers','exec'))
stage=repo/'patches/collector-size-and-duplicate-20261025';O=stage/'overlay';idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};idx['ffreight']=root/'odf/ships/ffreight.odf';pending={};checks=[]
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);p=idx[n];rel=p.relative_to(root).as_posix();t=pending[rel]if rel in pending else p.read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):d.update(props(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def ck(ok,label):
 assert ok,label
 checks.append(label)
def number(x):return float(str(x).rstrip('fF;'))
def replace(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+str(v)+'\n'
P={n:props(n)for n in idx};spans={}
def span(n):
 model=P[n].get('basename',n)
 if model not in spans:spans[model]=float(np.ptp(visible_points(load_model(root/'SOD'/(model+'.sod'))),axis=0).max())
 return spans[model]
target=span('myfminer1')*number(P['myfminer1'].get('scalesod',1))*.5;rows=[]
for n,d in P.items():
 if d.get('classlabel')!='freighter'or'dilithium'not in d.get('resourcescanhandle','').lower():continue
 src=idx[n];rel=src.relative_to(root).as_posix();old=src.read_text(encoding='latin1');newscale=target/span(n);t=replace(old,'ScaleSOD',format(newscale,'.12g'));pending[rel]=t
 after=props(n)
 ck({k:v for k,v in after.items()if k!='scalesod'}=={k:v for k,v in d.items()if k!='scalesod'},n+': only model scale changed')
 ck(abs(span(n)*number(after['scalesod'])-target)<.00001,n+': rendered hull extent matches reference')
 rows.append({'unit':n,'file':rel,'model':d.get('basename',n),'oldScale':number(d.get('scalesod',1)),'newScale':newscale,'worldSpan':target})
ck(len(rows)>=35,'All native, tiered, Ferengi and 8472 dilithium-capable collectors included')
shadow=root/'odf/other/ffreight.odf';ck(shadow.exists(),'Shadow Federation freighter ODF exists')
shadowtext=shadow.read_text(encoding='latin1');ck('myu000'not in shadowtext,'Old shadow copy is missing refit weapon')
pending[shadow.relative_to(root).as_posix()]=pending['odf/ships/ffreight.odf']
ck('weapon4 = "myu000"'in pending[shadow.relative_to(root).as_posix()],'Both Federation ODF copies carry refit ability')
ck('baseName = "dr26_ffreight"'in pending[shadow.relative_to(root).as_posix()],'Both Federation ODF copies use redesigned hull')

# Federation sensor only, following the current Federation-specific request.
n='fsensor';d=P[n];src=idx[n];rel=src.relative_to(root).as_posix();t=src.read_text(encoding='latin1');fields={'ScaleSOD':number(d.get('scalesod',1))*2.5}
for k in ['footprintBuffer','eastBuffer','westBuffer','northBuffer','southBuffer']:
 if k.lower()in d:fields[k]=number(d[k.lower()])*2.5
for k,v in fields.items():t=replace(t,k,format(v,'.12g'))
pending[rel]=t;after=props(n);allowed={k.lower()for k in fields};ck({k:v for k,v in after.items()if k not in allowed}=={k:v for k,v in d.items()if k not in allowed},'Sensor: only size and placement buffers changed')
ck(number(after['scalesod'])==number(d.get('scalesod',1))*2.5,'Sensor: +150 percent means 2.5 times original size')
files=[]
for rel,t in pending.items():
 dest=O/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'file':rel,'sourceHash':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'stagedHash':hashlib.sha256(dest.read_bytes()).hexdigest()})
report={'status':'STAGED','collectors':rows,'targetWorldSpan':target,'reference':'Federation custom MK II collector at half its previous rendered size','duplicateFix':{'canonical':'odf/ships/ffreight.odf','shadow':'odf/other/ffreight.odf','reason':'Shadow ODF contains original model and lacks myu000 refit ability; both paths now have identical canonical contents.','runtimeVerified':False},'sensor':{'unit':'fsensor','sizeMultiplier':2.5,'fields':fields},'files':files,'checks':len(checks),'runtimeVerified':False,'canonicalGameplayStatsUnchanged':True,'legacyShadowReplacedWithCanonical':True}
(stage/'manifest.json').write_text(json.dumps(report,indent=2));(repo/'reports/collector-size-and-duplicate-prepared.json').write_text(json.dumps(report,indent=2))
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-CimInstance Win32_Process -Filter "Name=\'Armada2.exe\' OR Name=\'Armada.exe\'").Count'],capture_output=True,text=True,check=True)
if int(running.stdout.strip()or'0'):
 print(json.dumps({'status':'STAGED - GAME RUNNING','collectors':len(rows),'files':len(files)}));raise SystemExit(0)
backup=Path('D:/Xaramada-Modwork/backups')/('collector-size-and-duplicate-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for r in files:
 rel=r['file'];ck(hashlib.sha256((root/rel).read_bytes()).hexdigest()==r['sourceHash'],'unchanged live baseline '+rel);dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,dest)
changed=[]
try:
 for r in files:
  rel=r['file'];(root/rel).chmod(0o666);shutil.copyfile(O/rel,root/rel);changed.append(rel);assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==r['stagedHash']
except Exception:
 for rel in changed:shutil.copyfile(backup/rel,root/rel)
 raise
ck((root/'odf/ships/ffreight.odf').read_bytes()==shadow.read_bytes(),'Applied Federation duplicates are identical')
for r in files:
 rel=r['file'];dest=repo/'bajor/overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
report.update(status='APPLIED - GAMEPLAY TEST PENDING',backup=str(backup),checks=len(checks));(repo/'reports/collector-size-and-duplicate-applied.json').write_text(json.dumps(report,indent=2))
status=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));status['current']='Collector patch applied: '+str(len(rows))+' dilithium-capable miners matched to half-size Federation reference, preserving proportions. Shadow Federation freighter ODF synchronized to restore its new model and refit ability. Federation sensor +150% with proportional footprint. Gameplay button test pending.';(repo/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as log:log.write('\n[Collector size / duplicate] Applied '+str(len(files))+' verified files. '+str(len(rows))+' miner hulls normalized; fsensor x2.5. Both ffreight.odf copies identical, including refit weapon and custom model. Backup '+str(backup)+'. Runtime refit test pending.\n')
print(json.dumps({'status':report['status'],'collectors':len(rows),'files':len(files),'worldSpan':target,'checks':len(checks),'backup':str(backup)},indent=2))
