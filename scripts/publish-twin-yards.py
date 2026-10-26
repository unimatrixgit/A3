"""Verify installed copies and stage only this patch, leaving unrelated lab files alone."""
from pathlib import Path
import json,hashlib,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/twin-yards-20261025';m=json.loads((stage/'manifest.json').read_text());a=json.loads((stage/'applied.json').read_text());paths=[]
for rel,h in m['files'].items():
 assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,rel
 assert hashlib.sha256((repo/'bajor/overlay'/rel).read_bytes()).hexdigest()==h,rel
 paths+=['bajor/overlay/'+rel,'patches/twin-yards-20261025/overlay/'+rel]
result={'status':'PASS','installedFiles':len(m['files']),'gameAndSourceHashesMatch':True,'runtimeVerified':False};(stage/'installed-verification.json').write_text(json.dumps(result,indent=2))
for name in ['design.json','artwork.json','ai.json','manifest.json','validation.json','applied.json','installed-verification.json','README.md']:paths.append('patches/twin-yards-20261025/'+name)
for name in ['nexus-common.py','prepare-twin-yards.py','extend-twin-yard-scope.py','build-native-faction-stations.py','twin-yard-render.py','finish-twin-yard-tech.py','finish-twin-yard-ai.py','name-and-document-twin-yards.py','validate-twin-yards.py','apply-twin-yards.py','apply-yard-bridge-update.py','publish-twin-yards.py','finish-borg-yard-size.py']:paths.append('scripts/'+name)
for name in ['twin-yard-building-list.md','twin-yards-applied.json','twin-yard-production-input.json','nexus-node-crash-rollback.json']:paths.append('reports/'+name)
paths+=['status.json','build.log'];head=subprocess.check_output(['git','-C',str(repo),'ls-files'],text=True).splitlines();canonical={x.lower():x for x in head};paths=list(dict.fromkeys(canonical.get(x.lower(),x)for x in paths))
paths+=['scripts/'+n for n in ['compact-yard-layout.py','preview-yard-family.py','preview-compact-yards.py','render-compact-yard-sheet.py','stage-compact-borg-roster.py']]
paths+=['patches/compact-yard-preview/'+n for n in ['borg-roster-review.json','borg-proposed-production.json','staging-report.json','all-staged-yards.png','byard2-staged.png','fyard3-staged.png']]
paths+=['scripts/render-bajoran-cardassian-yards.py','patches/compact-yard-preview/bajor-cardassian-yard-sheet.png']
paths+=['scripts/'+n for n in ['faction-research-layout.py','render-faction-research-sheet.py','verify-research-native-materials.py']]
paths+=['patches/faction-research-preview/'+n for n in ['preview-report.json','material-verification.json','all-research-stations.png','borg-cardassian-bajoran.png','research-variety-preview.png']]
paths+=['scripts/'+n for n in ['audit-production-interiors.py','stage-production-interiors.py','deploy-game-overlay.py','stage-dominion-carrier-fighters.py','stage-tvarek-hero.py','finish-carrier-tvarek-links.py','stage-validated-finishing-delta.py','verify-production-and-hero-install.py']]
for patch in ['production-interiors-20261025','dominion-carrier-launch-20261025','tvarek-hero-20261025','carrier-tvarek-links-20261025','production-hero-ai-finish-20261025']:
 for filename in ['patch.json','applied.json']:
  paths.append('patches/'+patch+'/'+filename)
 paths.extend(p.relative_to(repo).as_posix()for p in(repo/'patches'/patch/'overlay').rglob('*')if p.is_file())
paths+=['patches/production-interiors-20261025/audit.json','patches/production-interiors-20261025/installed-verification.json','patches/production-interiors-20261025/spacedock-doors-fixed.png','patches/tvarek-hero-20261025/tvarek-render.png','reports/production-carrier-tvarek-summary.md']
paths+=['scripts/preview-vanilla-station-direction.py','scripts/stage-vanilla-station-redesign.py']
for folder in ['vanilla-stations-20261026','vanilla-station-direction-20261026']:
 paths.extend(p.relative_to(repo).as_posix()for p in(repo/'patches'/folder).rglob('*')if p.is_file())
existing=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();assert not existing,existing
for i in range(0,len(paths),35):subprocess.run(['git','-C',str(repo),'add','-f','--']+paths[i:i+35],check=True,capture_output=True)
staged=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();assert not any(x.startswith('lab/')for x in staged)
subprocess.run(['git','-C',str(repo),'-c','core.whitespace=-blank-at-eol,-blank-at-eof','diff','--cached','--check'],check=True);print(json.dumps({**result,'stagedFiles':len(staged),'nextPatch':'ON HOLD'}))

