from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-all-faction-ai-sequence.py').read_text().split('issues=[];profiles=[]')[0])
stage=Path('D:/Xaramada-Modwork/all-ai-economy-final');patches=[];issues=[]
specs={'federation':['fbase','fconst','forbital','fmining','ffreight','fyard0','fyard','fdestroy'],'klingon':['kbase','kconst','korbital','kmining','kfreight','kyard','kdestroy'],'romulan':['rbase','rconst','rorbital','rmining','rfreight','ryard','rdestroy'],'breen':['brbase','brconst','brorbital','brmining','brfreight','bryard','brdestroy'],'bajoran':['bjbase','bjconst','bjorbital','bjmining','bjfreight','bjyard','bjinterceptor']}
pattern=r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
for race,opening in specs.items():
 for p in(root/'AI/AIPs').glob(race+'_*list.aip'):
  rows=[(m[1],int(m[2]),int(m[3]),int(m[4]),int(m[5]))for m in re.finditer(pattern,p.read_text(encoding='latin1'),re.M)];remaining=list(rows);first=[]
  for n in opening:
   i=next((i for i,x in enumerate(remaining)if x[0]==n),None)
   if i is None:row=(n,1,0,-1,0)
   else:row=remaining.pop(i)
   count=max(row[1],2)if n in [opening[1],opening[4],opening[-1]]else row[1];first.append((n,count,0,-1,row[4]if n==opening[0]else 0))
  new=first+[(n,c,b,-1 if n.startswith('x')and n.endswith('uconst')else m,tech)for n,c,b,m,tech in remaining]
  avail={v.lower().removesuffix('.odf')+'.odf'for k,v in props({'federation':'fed','klingon':'kling','romulan':'rom'}.get(race,race)).items()if re.fullmatch('standardunits[0-9]+',k)}
  for i,row in enumerate(new):
   n=row[0].lower()+'.odf'
   if n not in avail:
    missing=[x for x in tt.get(n,[])if x not in avail];producer=[x for x in producers.get(n,[])if x in avail]
    if n not in tt or missing or not producer:issues.append(dict(profile=p.name,row=i,unit=n,missing=missing,producer=producer))
   avail.add(n)
  assert len(new)<=200
  text='// Economy-first opening;original later force choices and tech phases retained.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'+'\n'.join(f'    "{n}", {c}, {b}, {m}, {tech},'for n,c,b,m,tech in new)+'\n};\n';rel=p.relative_to(root);dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(text,encoding='latin1');patches.append(dict(file=str(rel),rows=len(new),opening=first))
assert not issues,issues
# Read-only scan of all live AI include links,including campaign scripts.
ai=root/'AI/AIPs';lookup={p.name.lower()for p in ai.iterdir()if p.is_file()};includeIssues=[]
for p in ai.glob('*'):
 if not p.is_file():continue
 for target in re.findall(r'#include\s+"([^"]+)"',p.read_text(encoding='latin1')):
  if target.lower()not in lookup and not (p.parent/target).exists():includeIssues.append(dict(file=p.name,missing=target))
report=dict(stage=str(stage),patches=patches,issues=issues,includeIssues=includeIssues,installed=False,gameplayVerified=False,notes=['All45 faction profiles reviewed;25 economy openings corrected across5 factions.','Borg,Cardassian,Dominion,8472 profiles preserved.','Existing advanced unit roster,expansion rows and tech phase markers retained.','Initial resource facilities placed at home base0 before optional fleets.','Constructor and freighter opening quantities at least2;universal builder replacement no longer lifetime-limited.','Campaign scripts scanned for missing includes only,not altered.']);(repo/'reports/all-ai-economy-final.json').write_text(json.dumps(report,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']=f'All-faction AI deeper review complete:25 economy-first profiles staged;45profiles reviewed,zero staged producer/prerequisite errors. AI include-link issues:{len(includeIssues)}. Waiting for game closure;not installed.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(dict(stagedProfiles=len(patches),issues=issues,includeIssues=includeIssues)))

