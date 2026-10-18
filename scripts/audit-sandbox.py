"""Read-only audits against the isolated copy, with separate report output."""
from pathlib import Path
import json

repo=Path('D:/aramada')
target=Path('D:/ArmadaLab')
reports=target/'Development/reports'
reports.mkdir(parents=True,exist_ok=True)
assert target.resolve()!=Path('D:/armadaIII').resolve()
def source(name):
    s=(repo/'scripts'/name).read_text()
    s=s.replace("Path('D:/armadaIII')", "Path('D:/ArmadaLab')")
    s=s.replace("Path('D:/aramada/reports/installation-wide-diagnostic.json')",repr_path(reports/'installation-wide-diagnostic.json'))
    s=s.replace("repo/'reports/all-faction-ai-sequence.json'",repr_path(reports/'all-faction-ai-sequence.json'))
    s=s.replace("repo/'reports/non-bajor-ai-reference-audit.json'",repr_path(reports/'non-bajor-ai-reference-audit.json'))
    helper=(repo/'scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0]
    helper=helper.replace("Path('D:/armadaIII')","Path('D:/ArmadaLab')")
    s=s.replace("exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])",helper)
    return s
def repr_path(p):return 'Path('+repr(p.as_posix())+')'
for name in ['audit-installation-references.py','audit-all-faction-ai-sequence.py','audit-non-bajor-ai.py']:
    exec(compile(source(name),name,'exec'),{'__name__':'__main__'})
summary={}
for p in reports.glob('*.json'):
    data=json.loads(p.read_text())
    summary[p.name]=dict(issues=len(data.get('issues',[])),runtimeVerified=False)
(reports/'summary.json').write_text(json.dumps(dict(target=str(target),audits=summary),indent=2))
