from pathlib import Path
import json,re,hashlib,shutil,datetime,subprocess,os
repo=Path('D:/aramada');root=Path('D:/armadaIII');pack=json.loads((repo/'reports/unit-identity-applied.json').read_text());stage=Path(pack['stage']);out=Path('D:/Xaramada-Modwork/icons-only-stage');out.mkdir(exist_ok=True);pending={};changed=[]
assert pack.get('rolledBack'),'Original failed patch must remain rolled back'
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
assert hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()==pack['sourceSpriteSha256']
for rel,h in pack['sourceODFHashes'].items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,rel
# Exact graphics assets and sprite mappings from the failed combined patch.
for item in pack['manifest']:
 rel=item['file']
 if rel.lower().endswith(('.tga','.sod'))or rel=='Sprites/gui_global.spr':
  data=(stage/rel).read_bytes();assert hashlib.sha256(data).hexdigest()==item['sha256'];pending[rel]=data
# Only the model-name selector changes on shared-model units. All names/tooltips remain original.
byunit={x['unit']:x for x in pack['units']}
for alias in pack['sharedModelConflictCopies']:
 unit=alias['unit'];rel=byunit[unit]['odf'];t=(root/rel).read_text(encoding='latin1');new='baseName = "'+alias['iconModelAlias']+'"'
 if re.search(r'(?mi)^\s*baseName\s*=',t):t=re.sub(r'(?mi)^[ \t]*baseName\s*=[^\r\n]*',new,t)
 else:t+='\n'+new+'\n'
 pending[rel]=t.replace('\r','').replace('\n','\r\n').encode('latin1');changed.append(rel)
 def values(s):return{k.lower():v.strip()for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]*)',s)if k.lower()!='basename'}
 assert values(t)==values((root/rel).read_text(encoding='latin1')),unit
 original=root/'SOD'/(alias['originalModel']+'.sod');lookup={p.stem.lower():p for p in(root/'SOD').glob('*')if p.suffix.lower()=='.sod'};original=lookup[alias['originalModel']]
 assert pending['SOD/'+alias['iconModelAlias']+'.sod']==original.read_bytes(),unit
backup=Path('D:/Xaramada-Modwork/backups')/('icons-only-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));ops=[]
for rel,data in pending.items():
 dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel
  if dst.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
  ops.append((dst,b,data,dst.exists()))
written=[]
try:
 for dst,b,data,existed in ops:
  dst.parent.mkdir(parents=True,exist_ok=True)
  if existed:os.chmod(dst,0o666)
  written.append((dst,b,existed));dst.write_bytes(data);assert dst.read_bytes()==data
except Exception:
 for dst,b,existed in reversed(written):
  if existed:shutil.copy2(b,dst)
  elif dst.exists():dst.unlink()
 raise
# All839 units must retain every original gameplay and text property.
for rel in pack['sourceODFHashes']:
 old=Path(pack['backup'])/'live'/rel
 if rel in changed:assert values(old.read_text(encoding='latin1'))==values((root/rel).read_text(encoding='latin1')),rel
 else:assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==pack['sourceODFHashes'][rel],rel
r={'applied':True,'diagnostic':True,'appliedAt':datetime.datetime.now().astimezone().isoformat(),'backup':str(backup),'stage':str(out),'files':list(pending),'manifest':[{'file':f,'sha256':hashlib.sha256(v).hexdigest()}for f,v in pending.items()],'originalNamesAndTooltipsPreserved':839,'modelSelectorsChanged':len(changed),'modelGeometryByteIdentical':True,'spriteAndArtworkIdenticalToCombinedPatch':True,'runtimeVerified':False,'filesNeedingModelSelector':changed,'sourceODFHashes':pack['sourceODFHashes'],'sourceSpriteSha256':pack['sourceSpriteSha256']};(repo/'reports/icons-only-diagnostic.json').write_text(json.dumps(r,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='APPLIED ICONS-ONLY DIAGNOSTIC: same839-unit icon artwork and sprite mappings as withdrawn pack; original names, tooltips, costs, abilities and production unchanged.105 model-name aliases use byte-identical original geometry.225 files verified. Awaiting new-match load test to distinguish graphics/model mapping from text changes.';s['updated']=r['appliedAt'];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'appliedFiles':len(pending),'originalUnitNamesAndDescriptionsVerified':839,'modelSelectors':len(changed),'backup':str(backup)}))
