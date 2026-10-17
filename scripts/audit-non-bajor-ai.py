from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
tt={m[1].lower():m[0]for m in re.finditer(r'(?mi)^([^\s/]+\.odf)[ \t]+[^\r\n]+',(root/'techtree/tech1.tt').read_text(encoding='latin1'))};producers={}
for n in idx:
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower().removesuffix('.odf')+'.odf',[]).append(n)
profiles=[];issues=[]
for p in(root/'AI/AIPs').glob('*.aip'):
 if p.name.startswith('bajoran_')or not any(p.name.startswith(x+'_')for x in ['federation','borg','klingon','romulan','cardassian','dominion','breen','species8472']):continue
 rows=re.findall(r'(?mi)^[ \t]*"([^"\r\n]+)"[ \t]*,[ \t]*(-?\d+)[ \t]*,[ \t]*(-?\d+)[ \t]*,[ \t]*(-?\d+)[ \t]*,[ \t]*(-?\d+)[ \t]*,',p.read_text(encoding='latin1'))
 if not rows:continue
 for i,row in enumerate(rows):
  n=row[0].lower()+'.odf';errors=[]
  if n not in idx:errors.append('missing definition')
  if n not in tt:errors.append('missing tech1 entry')
  if n not in producers:errors.append('no producer found')
  if errors:issues.append({'profile':p.name,'row':i,'unit':n,'issues':errors})
 profiles.append({'profile':p.name,'rows':len(rows),'within200Rows':len(rows)<=200})
out={'target':str(root),'profiles':profiles,'issues':issues,'runtimeVerified':False,'note':'Reference audit only; does not validate runtime AI decisions or full dependency ordering.'};(repo/'reports/non-bajor-ai-reference-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'profiles':len(profiles),'issues':len(issues),'firstIssues':issues[:8]}))
