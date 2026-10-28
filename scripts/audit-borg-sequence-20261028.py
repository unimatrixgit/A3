from pathlib import Path
import re,json
root=Path('D:/armadaIII');repo=Path('D:/aramada');idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def props(n,seen=()):
 n=Path(n.strip('"')).stem.lower()
 if n not in idx or n in seen:return{}
 t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):d.update(props(inc,seen+(n,)))
 for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
cache={n:props(n)for n in idx};tech={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):tech[Path(a[0]).stem.lower()]=(int(a[1]),[Path(x).stem.lower()for x in a[2:2+max(0,int(a[1]))]])
starts={Path(v).stem.lower()for k,v in cache['borg'].items()if re.fullmatch('standardunits[0-9]+',k)};print('STARTS',starts)
producers={}
for name,d in cache.items():
 for k,v in d.items():
  if re.fullmatch('(secondary)?builditem[0-9]+',k):producers.setdefault(Path(v).stem.lower(),set()).add(name)
reports=[]
for p in sorted((root/'AI/AIPs').glob('borg_*list.aip')):
 rows=re.findall(r'(?m)^\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,?',p.read_text(encoding='latin1'));avail=set(starts);issues=[]
 for i,row in enumerate(rows):
  name=row[0].lower()
  if name not in avail:
   gate,deps=tech.get(name,(0,[]));missing=[x for x in deps if x not in avail];prod=sorted(producers.get(name,set())&avail)
   if name not in idx or gate<0 or missing or not prod:issues.append({'step':i+1,'unit':name,'missingDependencies':missing,'availableProducers':prod,'allProducers':sorted(producers.get(name,set())),'disabled':gate<0})
  avail.add(name)
 reports.append({'profile':p.name,'steps':len(rows),'issues':issues})
(repo/'reports/borg-ai-sequence-audit-20261028.json').write_text(json.dumps({'startingUnits':sorted(starts),'profiles':reports},indent=2));print(json.dumps(reports))
