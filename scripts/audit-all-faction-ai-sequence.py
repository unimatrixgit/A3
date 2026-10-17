from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
factions=['federation','borg','klingon','romulan','cardassian','dominion','breen','species8472','bajoran'];tt={};producers={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):tt[a[0].lower()]=[x.lower()for x in a[2:2+max(int(a[1]),0)]]
for n in idx:
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower().removesuffix('.odf')+'.odf',[]).append(n)
issues=[];profiles=[]
for race in factions:
 for p in(root/'AI/AIPs').glob(race+'_*list.aip'):
  avail={v.lower().removesuffix('.odf')+'.odf'for k,v in props({'federation':'fed','klingon':'kling','romulan':'rom','cardassian':'card'}.get(race,race)).items()if re.fullmatch('standardunits[0-9]+',k)}
  rows=re.findall(r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,',p.read_text(encoding='latin1'),re.M)
  for i,row in enumerate(rows):
   n=row[0].lower()+'.odf'
   if n not in avail:
    missing=[x for x in tt.get(n,[])if x not in avail];prod=[x for x in producers.get(n,[])if x in avail]
    if missing or not prod or n not in tt:issues.append(dict(profile=p.name,row=i,unit=n,missing=missing,producerAvailable=bool(prod)))
   avail.add(n)
  profiles.append(dict(profile=p.name,rows=len(rows)))
(repo/'reports/all-faction-ai-sequence.json').write_text(json.dumps(dict(profiles=profiles,issues=issues,gameplayVerified=False),indent=2));print(json.dumps(dict(profiles=len(profiles),issues=len(issues),examples=issues[:35])))

