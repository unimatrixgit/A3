from pathlib import Path
import json,re
root=Path('D:/armadaIII');stage=Path('D:/aramada/patches/twin-yards-20261025');O=stage/'overlay';d=json.loads((stage/'design.json').read_text());P={n:v['properties']for n,v in d['baseline'].items()};assigned=d['attackAssignments'];retired=d['retired'];exempt=set(d['exemptStructures']);producers={}
for n,p in P.items():
 matches=[v for k,v in p.items()if re.fullmatch('builditem[0-9]+',k)and v in assigned]
 if matches and n not in exempt and n not in assigned.values()and(p.get('classlabel')=='shipyard'or n in retired or n in ['bbattle5','bbattle6','fbyard']):producers[n]=assigned[matches[0]]
for file in(root/'techtree').glob('*.tt'):
 if file.stem not in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:continue
 seen=set();out=[]
 for line in file.read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if len(a)<2 or not a[0].lower().endswith('.odf'):out.append(line);continue
  n=Path(a[0]).stem.lower()
  if n in seen:continue
  seen.add(n);count=int(a[1]);deps=[Path(x).stem.lower()for x in a[2:2+max(0,count)]]
  if n in retired:out.append(n+'.odf -1 // Consolidated production');continue
  if n=='dyard2':count=2;deps=['dyard','dresear']
  if count<0:out.append(line);continue
  deps=[retired.get(x,producers.get(x,x))for x in deps]
  if n in assigned:deps=[assigned[n]]+[x for x in deps if x not in assigned.values()]
  deps=list(dict.fromkeys(x for x in deps if x!=n));out.append(n+'.odf '+('0'if file.stem=='fulltech'else str(len(deps))+(' '+' '.join(x+'.odf'for x in deps)if deps else'')))
 for n in d['newUnits']:
  if n in seen:continue
  a=d['assets'].get(n);dep=d['yards'][a['theme']][0]if a else None;out.append(n+'.odf '+('0'if not dep or file.stem=='fulltech'else'1 '+dep+'.odf'))
 if file.stem!='fulltech':
  rules={}
  for line in out:
   x=line.split('//')[0].split()
   if len(x)>=2 and x[0].lower().endswith('.odf'):rules[Path(x[0]).stem.lower()]=(int(x[1]),[Path(y).stem.lower()for y in x[2:]])
  affected=set(d['assets'])|set(assigned)|set(d['newUnits']);disabled=set();changed=True
  while changed:
   changed=False
   for n in affected:
    if n not in rules or rules[n][0]<0:continue
    if any(rules.get(dep,(-1,[]))[0]<0 for dep in rules[n][1]):rules[n]=(-1,[]);disabled.add(n);changed=True
  final=[]
  for line in out:
   x=line.split('//')[0].split();n=Path(x[0]).stem.lower()if x else''
   final.append(n+'.odf -1 // Unavailable in this technology mode'if n in disabled else line)
  out=final
 (O/file.relative_to(root)).write_bytes(('\r\n'.join(out)+'\r\n').encode('latin1'))
print('Rebuilt six technology trees; native starbase prerequisites preserved.')
