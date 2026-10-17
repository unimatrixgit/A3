from pathlib import Path
import re,json
root=Path('D:/armadaIII');paths=list((root/'odf').rglob('*.odf'));idx={p.name.lower():p for p in paths};issues=[];includes=0;weapons=0
for p in paths:
 t=p.read_text(encoding='latin1')
 for n in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',t):
  includes+=1
  if n.lower()not in idx:issues.append({'file':p.relative_to(root).as_posix(),'missingInclude':n})
 for slot,n in re.findall(r'(?mi)^[ \t]*(weapon\d+)[ \t]*=[ \t]*"([^"\r\n]*)"',t):
  weapons+=1
  if not n or n.lower()+'.odf'not in idx:issues.append({'file':p.relative_to(root).as_posix(),'slot':slot,'missingOrEmptyWeapon':n})
report={'target':str(root),'odfFiles':len(paths),'includesChecked':includes,'explicitWeaponSlotsChecked':weapons,'issues':issues,'runtimeVerified':False,'note':'Static installation-wide references. Unused legacy files may appear; do not treat every finding as an active crash cause.'};Path('D:/aramada/reports/installation-wide-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps({'odfFiles':len(paths),'includes':includes,'weapons':weapons,'issues':len(issues),'firstIssues':issues[:5]}))
