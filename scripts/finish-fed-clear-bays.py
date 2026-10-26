"""Merge Federation-only model corrections and dual-purpose dock changes."""
from pathlib import Path
import json,hashlib,shutil
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/fed-clear-bays-20261026';O=stage/'overlay';stage.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for folder in ['federation-dual-purpose-dock-20261026','fed-clear-production-bays-20261026']:
 source=repo/'patches'/folder;records.extend(json.loads((source/'artwork.json').read_text()))
 for p in(source/'overlay').rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(source/'overlay');target=O/rel
  if(root/rel).exists()and sha(p)==sha(root/rel):continue
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
ships=['fscout','fdestroy2','fdestroy'];checks=json.loads((repo/'patches/federation-dual-purpose-dock-20261026/dual-purpose-validation.json').read_text());assert checks['status']=='PASS'
files={p.relative_to(O).as_posix():sha(p)for p in O.rglob('*')if p.is_file()};assert not any(any(s in r.lower()for s in ['maps/','bzn/','8472'])for r in files)
assert all(r.startswith(('SOD/ty26_f','SOD/ty26_s31','SOD/ty26_mryfed','SOD/ty26_xyr_f','SOD/ty26_xflegacy','Textures/','odf/stations/fyard','odf/stations/xyr_f','techtree/','AI/AIPs/federation_'))for r in files),list(files)
patch={'status':'PASS','files':files,'sourceHashes':{r:sha(root/r)for r in files if(root/r).exists()},'attackAssignments':{n:'xyr_f'for n in ships},'extraAiTargets':{'federation':ships},'description':'Removed nested yard geometry from seven Federation production yards and the revised service dock. Left repair berth; right Venture, Sabre and Defiant berth. Updated technology and AI.'}
(stage/'patch.json').write_text(json.dumps(patch,indent=2));(stage/'artwork.json').write_text(json.dumps(records,indent=2));(stage/'validation.json').write_text(json.dumps({**checks,'modelCount':len(records),'files':len(files),'otherFactionsUnchanged':True},indent=2));shutil.copyfile(repo/'patches/federation-dual-purpose-dock-20261026/ai.json',stage/'ai.json');print(json.dumps({'status':'PASS','models':len(records),'changedFiles':len(files)}))
