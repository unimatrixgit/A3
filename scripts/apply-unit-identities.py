from pathlib import Path
import json,datetime,subprocess,hashlib,shutil,os
repo=Path('D:/aramada');root=Path('D:/armadaIII');report=repo/'reports/unit-identity-staged.json';m=json.loads(report.read_text());stage=Path(m['stage']);assert not m['applied'],'Already applied'
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game is running'
assert hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()==m['sourceSpriteSha256'],'Live sprite baseline changed'
for rel,h in {**m['sourceODFHashes'],**m.get('sourceAssetHashes',{})}.items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,('Live baseline changed',rel)
for item in m['manifest']:assert hashlib.sha256((stage/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
backup=Path('D:/Xaramada-Modwork/backups')/('unit-identity-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));operations=[]
for item in m['manifest']:
 rel=item['file']
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel;exists=dst.exists()
  if exists:b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
  operations.append((dst,b,exists,stage/rel,item['sha256']))
written=[]
try:
 for dst,b,exists,src,h in operations:
  dst.parent.mkdir(parents=True,exist_ok=True)
  if exists:os.chmod(dst,0o666)
  written.append((dst,b,exists));shutil.copyfile(src,dst);assert hashlib.sha256(dst.read_bytes()).hexdigest()==h,str(dst)
except Exception:
 for dst,b,exists in reversed(written):
  if exists:shutil.copy2(b,dst)
  elif dst.exists():dst.unlink()
 raise
m['applied']=True;m['appliedAt']=datetime.datetime.now().astimezone().isoformat();m['backup']=str(backup);m['runtimeVerified']=False;m['validation']['applied']=True;report.write_text(json.dumps(m,indent=2));(repo/'reports/unit-identity-applied.json').write_text(json.dumps(m,indent=2))
p=repo/'reports/unit-identity-staged.md';s=p.read_text(encoding='utf-8').replace('# Staged unit names and tooltips','# Applied unit names and tooltips').replace('Live game unchanged.','Applied to D:/armadaIII. Gameplay testing pending.');p.write_text(s,encoding='utf-8')
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='APPLIED:839 faction ship/station icons, unique names and faction tooltips. Role badges and hero faction emblems installed;14 atlases and105 byte-identical model aliases preserve independent buttons.5 legacy models use existing artwork;5 unused missing-asset definitions unchanged. All installed files verified; gameplay testing pending.';s['updated']=m['appliedAt']
for feature in s.get('features',[]):
 if feature.get('title')=='Ship and station identity refresh':feature['note']='Applied839 unit updates; file checks passed; gameplay test pending.'
p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+m['appliedAt']+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'appliedUnits':len(m['units']),'verifiedFiles':len(m['manifest']),'modelAliases':len(m['sharedModelConflictCopies']),'backup':str(backup)}))
