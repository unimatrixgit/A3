from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');keys=set(re.findall(r'^([^\s/@][^\s]*)\s+\S+\s+\d+\s+\d+\s+\d+\s+\d+',sprite,re.M));keys={k.lower()for k in keys};models={p.stem.lower()for p in(root/'SOD').glob('*')if p.is_file()};rows=[];issues=[]
for n in idx:
 d=props(n)
 for k,v in d.items():
  if not re.fullmatch(r'(?:secondary)?builditem\d+',k):continue
  target=v.lower().removesuffix('.odf');td=props(target)
  if not td:issues.append({'producer':n,'target':target,'issue':'Missing target'});continue
  model=td.get('basename',target).lower().removesuffix('.sod');icon=next((x for x in ['b_'+target,'b_'+model]if x in keys),None)
  row={'producer':n,'target':target,'model':model,'modelPresent':model in models,'icon':icon};rows.append(row)
  if not icon:issues.append({**row,'issue':'Missing build icon'})
  if model not in models and target!='shield':issues.append({**row,'issue':'Missing model'})
report={'targetsChecked':len(rows),'uniqueTargets':len(set(x['target']for x in rows)),'issues':issues,'note':'All definition menus including unused legacy content; Planetary shield upgrade is a native effect without a separate model.','rows':rows};(repo/'reports/final-production-assets.json').write_text(json.dumps(report,indent=2));print(json.dumps({'targets':len(rows),'uniqueTargets':report['uniqueTargets'],'issues':issues[:20],'issueCount':len(issues)}))
