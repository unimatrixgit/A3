"""Generate dependency-ordered native AI for consolidated yards and service docks."""
from pathlib import Path
import json,re
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';d=json.loads((stage/'design.json').read_text());idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};idx.update({p.stem.lower():p for p in(O/'odf').rglob('*.odf')});cache={}
def props(n):
 if n in cache:return cache[n]
 t=idx[n].read_text(encoding='latin1');out={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):out.update(props(Path(inc).stem.lower()))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):out[k.lower()]=v.split('//')[0].strip().strip('"')
 cache[n]=out;return out
P={n:props(n)for n in idx};tech={};producers={}
for line in(O/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>=2 and a[0].lower().endswith('.odf'):tech[Path(a[0]).stem.lower()]=(int(a[1]),[Path(x).stem.lower()for x in a[2:2+max(0,int(a[1]))]])
for n,p in P.items():
 for k,v in p.items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower(),[]).append(n)
codes={'federation':'f','borg':'b','klingon':'k','romulan':'r','cardassian':'c','dominion':'d','bajoran':'bj','breen':'br'};base={'f':'fbase','b':'bbase','k':'kbase','r':'rbase','c':'cbase','d':'dbase','bj':'bjbase','br':'brbase'};builder={'f':'fconst','b':'bconst','k':'kconst','r':'rconst','c':'cconst','d':'dconst','bj':'bjconst','br':'brconst'};pat=re.compile(r'(?m)^[ \t]*"([^"]+)"[ \t]*,[ \t]*(-?\d+)[ \t]*,[ \t]*(-?\d+)[ \t]*,[ \t]*(-?\d+)[ \t]*,[ \t]*(-?\d+)[ \t]*,');reports=[];errors=[]
for race,code in codes.items():
 for file in(root/'AI/AIPs').glob(race+'_*list.aip'):
  available={base[code],builder[code]};plan=[];skipped=[]
  class Unreachable(Exception):pass
  def ensure(n,stack=()):
   if n in available:return
   if n in stack:raise Unreachable('dependency cycle '+str(stack+(n,)))
   if n not in tech or tech[n][0]<0:raise Unreachable('disabled/missing technology '+n)
   for dep in tech[n][1]:ensure(dep,stack+(n,))
   candidates=sorted(producers.get(n,[]),key=lambda p:(p not in available,P[p].get('race')!=race,p))
   if not any(p in available for p in candidates):
    solved=False;reasons=[]
    for p in candidates:
     if p in stack or p==n or P[p].get('race')not in [race,'ferengi']:continue
     saved=set(available);length=len(plan)
     try:ensure(p,stack+(n,));solved=True;break
     except Unreachable as e:available.clear();available.update(saved);del plan[length:];reasons.append(str(e))
    if not solved:raise Unreachable('no producer '+n+' '+str(reasons[:2]))
   plan.append((n,1,0,-1,0));available.add(n)
  for match in pat.finditer(file.read_text(encoding='latin1')):
   original=match[1].lower();n=d['retired'].get(original,original);saved=set(available);length=len(plan)
   try:
    existed=n in available;ensure(n)
    if not existed and len(plan)>length and plan[-1][0]==n:plan.pop()
    plan.append((n,*[int(match[i])for i in range(2,6)]));available.add(n)
   except Unreachable as e:available.clear();available.update(saved);del plan[length:];skipped.append({'unit':n,'reason':str(e)})
  owned={code,'bg'if code=='b'else'fg'};wanted=[n for c in owned for n in d['yards'][c]]+['xyr_'+c for c in owned]
  wanted += [n for n,a in d['assets'].items()if a['kind']=='hwp'and a['theme']in owned]
  wanted += d.get('extraAiTargets',{}).get(race,[])
  for n in wanted:
   try:ensure(n)
   except Unreachable as e:errors.append({'file':file.name,'unit':n,'reason':str(e)})
  assert len(plan)<=200,(file.name,len(plan));out=O/file.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);text='// Native dependency-ordered standalone production and service docks.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'+''.join('    "'+r[0]+'", '+', '.join(str(x)for x in r[1:])+',\n'for r in plan)+'};\n';out.write_bytes(text.replace('\n','\r\n').encode('latin1'));reports.append({'file':file.name,'orders':len(plan),'skipped':skipped})
report={'profiles':reports,'failures':errors,'runtimeVerified':False};(stage/'ai.json').write_text(json.dumps(report,indent=2));print(json.dumps({'profiles':len(reports),'requiredFailures':errors,'skipped':sum(len(x['skipped'])for x in reports)}))
if errors or any(x['skipped']for x in reports):raise SystemExit(1)
