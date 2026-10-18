from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-all-faction-ai-sequence.py').read_text().split('issues=[];profiles=[]')[0])
stage=Path('D:/Xaramada-Modwork/cardassian-ai-economy');profiles=[];issues=[]
# Resource extraction before expensive research,with an early defensive fleet.
opening=[('cbase',1),('cconst',2),('corbital',1),('cmining',1),('cfreight',2),('cyard',1),('cdestroy',2),('csensor',1),('cturret',2),('cresear',1),('ccolony',1),('xcuconst',1),('cresear2',1),('cturret2',1)]
for p in(root/'AI/AIPs').glob('cardassian_*list.aip'):
 original=p.read_text(encoding='latin1');rows=[(m[1],int(m[2]),int(m[3]),int(m[4]),int(m[5]))for m in re.finditer(r'^\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,',original,re.M)]
 # Preserve all later profile choices,expansion locations and force sizes.
 end=next(i for i,x in enumerate(rows)if x[0]=='ccolony')
 new=[(n,c,0,-1,0)for n,c in opening]+rows[end+1:]
 avail={v.lower().removesuffix('.odf')+'.odf'for k,v in props('card').items()if re.fullmatch('standardunits[0-9]+',k)}
 for i,row in enumerate(new):
  n=row[0].lower()+'.odf'
  if n not in avail:
   missing=[x for x in tt.get(n,[])if x not in avail];producer=[x for x in producers.get(n,[])if x in avail]
   if n not in tt or missing or not producer:issues.append(dict(profile=p.name,row=i,unit=n,missing=missing,producers=producer))
  avail.add(n)
 assert len(new)<=200
 text='// Cardassian economy recovery:metal and dilithium before research;early defense.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'+'\n'.join(f'    "{n}", {c}, {b}, {m}, {tech},'for n,c,b,m,tech in new)+'\n};\n';rel=p.relative_to(root);dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(text,encoding='latin1');profiles.append(dict(profile=p.name,file=str(rel),rows=len(new),oldOpening=[x[0]for x in rows[:end+1]],newOpening=[x[0]for x in new[:len(opening)]]))
assert not issues,issues
report=dict(stage=str(stage),profiles=profiles,issues=issues,installed=False,gameplayVerified=False,notes=['Five skirmish profiles only;campaign files unchanged.','Metal extraction scheduled before research stations.','Two freighters and two basic destroyers before advanced research.','Universal constructor can be replaced;removed finite one-build opening restriction.','All later original unit choices,expansion indices and quantities retained.']);(repo/'reports/cardassian-ai-economy.json').write_text(json.dumps(report,indent=2));sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']='Cardassian AI economy fix ready:5profiles validated;metal,dilithium,2freighters and early destroyers before advanced research. Staged only;waiting until testing ends.';sfile.write_text(json.dumps(s,indent=2));(repo/'build.log').open('a').write('\n'+s['current']+'\n');print(json.dumps(dict(profiles=len(profiles),issues=issues,installed=False)))
