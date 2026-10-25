"""Apply the validated research artwork revision with original materials."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';m=json.loads((stage/'manifest.json').read_text());v=json.loads((stage/'validation.json').read_text());assert v['status']=='PASS'
r=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],capture_output=True,text=True,check=True)
if int(r.stdout.strip()or'0'):raise SystemExit('Game running: structural refinement staged, not applied.')
changes=[rel for rel,h in m['files'].items()if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=h]
art=json.loads((stage/'artwork.json').read_text());research=[row for row in art if row['kind']=='research'];assert len(research)==27
materials=repo/'patches/faction-research-preview/material-verification.json';assert json.loads(materials.read_text())['status']=='PASS'
allowed={'Sprites/gui_global.spr'.lower()}
design=json.loads((stage/'design.json').read_text())
for row in research:
 allowed.update(x.lower()for x in ['SOD/'+row['model']+'.sod','Textures/RGB/gb'+row['model']+'.tga','Textures/RGB/wf'+row['model']+'.tga',design['baseline'][row['unit']]['file']])
assert all(rel.lower()in allowed for rel in changes),[rel for rel in changes if rel.lower()not in allowed]
backup=Path('D:/Xaramada-Modwork/backups')/('research-materials-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False)
for rel in changes:
 target=(root/rel).resolve();assert target.is_relative_to(root.resolve())and not rel.lower().startswith(('maps/','bzn/'));assert hashlib.sha256(target.read_bytes()).hexdigest()==m['sourceHashes'][rel];out=backup/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,out)
try:
 for rel in changes:
  target=root/rel;shutil.copyfile(O/rel,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==m['files'][rel]
except Exception:
 for rel in changes:shutil.copyfile(backup/rel,root/rel)
 raise
for rel,h in m['files'].items():
 assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h;dest=repo/'bajor/overlay'/rel;shutil.copyfile(root/rel,dest)
a=json.loads((stage/'applied.json').read_text());a['researchArtworkRevision']={'backup':str(backup),'files':len(changes),'stations':27,'originalMaterialsVerified':True,'podPositionsPreserved':True,'yardsUnchanged':True,'runtimeVerified':False};a['staticChecks']=v['checks'];a['nextPatch']='Conservative unused asset audit; balance changes remain on hold';(stage/'applied.json').write_text(json.dumps(a,indent=2));(repo/'reports/twin-yards-applied.json').write_text(json.dumps(a,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Applied 27 cohesive faction research-station designs with original materials, textures and lighting. Pod attachment positions and research capacity verified; original functions/costs preserved. Includes upgrade centres and Federation/Borg Omega labs. Bajor/Cardassia share architecture. Yards, 8472 and Borg tech assimilator unchanged. Static validation passed; gameplay testing pending.';s['twinYards']=a;(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Faction research artwork and original materials] '+json.dumps(a['researchArtworkRevision'])+'\n')
for p in [materials,repo/'patches/faction-research-preview/preview-report.json']:
 r=json.loads(p.read_text());r['applied']=True;r['runtimeVerified']=False;p.write_text(json.dumps(r,indent=2))
print(json.dumps(a['researchArtworkRevision']))
