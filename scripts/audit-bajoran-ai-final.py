from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
tt={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].endswith('.odf'):tt[a[0].lower()]=[x.lower()for x in a[2:2+max(int(a[1]),0)]]
profiles=[];issues=[]
for p in(root/'AI/AIPs').glob('bajoran_*list.aip'):
 avail={v.lower()for k,v in props('bajoran').items()if re.fullmatch('standardunits[0-9]+',k)};rows=re.findall(r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,',p.read_text(encoding='latin1'),re.M)
 for i,row in enumerate(rows):
  n=row[0].lower()+'.odf'
  if n in avail:continue
  missing=[x for x in tt.get(n,[])if x not in avail];prod=[x for x in avail if any(v.lower().removesuffix('.odf')+'.odf'==n for k,v in props(x).items()if re.fullmatch(r'(?:secondary)?builditem\d+',k))]
  if n not in tt or missing or not prod:issues.append({'profile':p.name,'row':i,'unit':n,'missingPrerequisites':missing,'producerAvailable':bool(prod)})
  avail.add(n)
 profiles.append({'profile':p.name,'rows':len(rows)})
(repo/'reports/bajoran-ai-final-cleanup.json').write_text(json.dumps({'profiles':profiles,'issues':issues,'gameplayVerified':False},indent=2));print(json.dumps({'profiles':len(profiles),'issues':issues[:8],'issueCount':len(issues)}))
