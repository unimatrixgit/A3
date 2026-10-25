"""Reorder all 34 existing Borg yard entries into the minimum three yards."""
from pathlib import Path
import re,json
repo=Path('D:/aramada');stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';d=json.loads((stage/'design.json').read_text())
def edit_menu(t,ships):
 assert len(ships)<=14 and len(ships)==len(set(ships))
 t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',t).rstrip()
 return t+'\n'+''.join('buildItem'+str(i)+' = "'+n+'"\n'for i,n in enumerate(ships))
menus={}
for y in d['yards']['b']:
 p=O/d['baseline'][y]['file'];t=p.read_text(encoding='latin1');menus[y]=re.findall(r'(?mi)^\s*buildItem\d+\s*=\s*"([^"]+)"',t)
original={n:y for y,ships in menus.items()for n in ships};assert len(original)==34
moves={n:'byard'for n in ['bfrigate','btacpyr','bspecial','bsphere','bpentra']};moves.update(bhentrag='byard2',blocutus='byard3')
result={y:[n for n in ships if moves.get(n,y)==y]for y,ships in menus.items()}
for n,y in moves.items():
 if n not in result[y]:result[y].append(n)
assert sorted(n for ships in result.values()for n in ships)==sorted(original)
for y,ships in result.items():
 p=O/d['baseline'][y]['file'];p.write_bytes(edit_menu(p.read_text(encoding='latin1'),ships).replace('\r','').replace('\n','\r\n').encode('latin1'))
 for ship in ships:
  if ship in d['attackAssignments']:d['attackAssignments'][ship]=y
for p in(O/'techtree').glob('*.tt'):
 out=[]
 for line in p.read_text(encoding='latin1').splitlines():
  tokens=line.split('//')[0].split();n=Path(tokens[0]).stem.lower()if tokens else''
  if n in moves and len(tokens)>1 and int(tokens[1])>=0:
   count=int(tokens[1]);deps=[Path(x).stem.lower()for x in tokens[2:2+count]];deps=[x for x in deps if x not in menus];deps=([moves[n]]+deps)if p.stem!='fulltech'else[];deps=list(dict.fromkeys(deps));line=n+'.odf '+str(len(deps))+(' '+' '.join(x+'.odf'for x in deps)if deps else'')
  if n=='byard3'and p.stem=='nosuper':
   # The yard now houses ordinary Locutus too. Keep the yard available in
   # No Superweapons; existing forbidden Omega ship entries stay disabled.
   line='byard3.odf 3 bbase.odf byard2.odf bresear2.odf'
  out.append(line)
 p.write_bytes(('\r\n'.join(out)+'\r\n').encode('latin1'))
d['compactYardRedesign']={'borgMinimumYards':3,'borgRosterCount':34,'borgMenus':result,'movedShips':moves,'allFactionsExcept8472':True,'singleBorgBay':True,'status':'STAGED'}
(stage/'design.json').write_text(json.dumps(d,indent=2));(repo/'patches/compact-yard-preview/borg-proposed-production.json').write_text(json.dumps(result,indent=2));print(json.dumps({y:len(v)for y,v in result.items()}))
