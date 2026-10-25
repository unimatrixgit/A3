from pathlib import Path
import json,subprocess,hashlib
repo=Path('D:/aramada');root=Path('D:/armadaIII')
report=json.loads((repo/'reports/mining-yards-applied.json').read_text());tracked=subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines();canonical={s.lower():s for s in tracked}
paths=[]
for row in report['files']:
 rel=row['file'];assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==row['stagedHash'];p='bajor/overlay/'+rel;paths.append(canonical.get(p.lower(),p))
paths += ['scripts/'+x+'.py'for x in ['prepare-mining-yards','build-mining-yard-art','finish-mining-yard-support','validate-mining-yards','apply-mining-yards','commit-mining-yards']]
paths += ['reports/'+x+'.json'for x in ['mining-yard-before','mining-yards-prepared','mining-yards-validation','mining-yards-applied']]
paths += ['patches/mining-yards-20261025/'+x for x in ['README.md','manifest.json','gameplay.json','artwork.json','validation.json']]
paths += ['artwork/mining-yards/v1/concepts.png','artwork/mining-yards/v1/models-preview.png']
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).strip(),'Unexpected pre-staged changes'
for i in range(0,len(paths),40):subprocess.run(['git','add','-f','--']+paths[i:i+40],cwd=repo,check=True)
staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).splitlines();assert not any(x.startswith('lab/')for x in staged)
subprocess.run(['git','-c','core.whitespace=-blank-at-eol,-blank-at-eof','diff','--cached','--check'],cwd=repo,check=True)
subprocess.run(['git','-c','gc.auto=0','commit','-q','-m','Add faction mining yards, researched miner refits and AI production'],cwd=repo,check=True)
print('Verified',len(report['files']),'live files; committed',len(staged),'source and report files.')
