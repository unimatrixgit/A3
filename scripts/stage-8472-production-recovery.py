from pathlib import Path
exec(Path('D:/aramada/scripts/stage-special-ability-tooltips.py').read_text().split('roster=')[0])
from collections import defaultdict,Counter
stage=Path('D:/Xaramada-Modwork/8472-production-recovery-stage');stage.mkdir(exist_ok=True);pending={};changes=[]
fixes={'xhs_yard3':{'shipIsBuiltByEvolution':0,'shipIsBuiltByShips':1},'8472_mine':{'shipIsBuiltByEvolution':1,'shipIsBuiltByShips':0},'714turr':{'shipIsBuiltByEvolution':0,'shipIsBuiltByShips':1},'8472_sentinel':{'shipIsBuiltByEvolution':0,'shipIsBuiltByShips':1}}
for n,values in fixes.items():
 t=idx[n].read_text(encoding='latin1')
 for k,v in values.items():t=re.sub(r'(?mi)^[ \t]*'+k+r'\s*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
 pending[idx[n].relative_to(root).as_posix()]=t;changes.append({'unit':n,'values':values})
# Overlay staged flags onto immutable live property snapshots.
p={n:dict(props(n))for n in idx}
for n,values in fixes.items():p[n].update({k.lower():str(v)for k,v in values.items()})
tech={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].lower().endswith('.odf'):tech[Path(a[0]).stem.lower()]=None if int(a[1])<0 else [Path(x).stem.lower()for x in a[2:2+int(a[1])]]
producers=defaultdict(set)
for n,d in p.items():
 for k,v in d.items():
  if re.fullmatch('(secondary)?builditem[0-9]+',k):producers[v.lower()].add(n)
starts=[Path(v).stem.lower()for k,v in p['species8472'].items()if re.fullmatch('standardunits[0-9]+',k)]
assert starts==['8472_mothership','8472_active','8472_passive','8472_scout'],starts

def route(n):
 d=p[n];candidates=[x for x in producers[n]if p[x].get('race')=='species8472']
 if d.get('shipisbuiltbyevolution')=='1':return [x for x in candidates if p[x].get('classlabel')=='evolver']
 if d.get('shipisbuiltbyships')=='1':return [x for x in candidates if p[x].get('classlabel')=='constructionrig']
 return [x for x in candidates if p[x].get('classlabel')not in ['evolver','constructionrig']]
profiles=[];pat=r'^\s*"([^\"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
for file in sorted((root/'AI/AIPs').glob('species8472_*.aip')):
 src=file.read_text(encoding='latin1')
 if 'the_build_list'not in src:continue
 desired=[(m[1].lower(),*[int(m[i])for i in range(2,6)])for m in re.finditer(pat,src,re.M)];pop=Counter(starts);result=[];events=[];visiting=set();spent=0
 def ensure(n,count=1,base=0,mx=-1):
  nonlocal_dummy=None
  if pop[n]>=count:return
  assert n not in visiting,('dependency cycle',n)
  assert isinstance(tech.get(n),list),('missing tech',n)
  visiting.add(n)
  for dep in tech[n]:ensure(dep)
  choices=route(n);assert choices,('no compatible producer',n,p[n].get('shipisbuiltbyevolution'),producers[n])
  choices.sort(key=lambda x:(pop[x]==0,len(tech.get(x)or[]),x))
  producer=choices[0];evolves=p[producer].get('classlabel')=='evolver'
  while pop[n]<count:
   # Keep a spare embryo: one evolves, one remains available for the next goal.
   ensure(producer,2 if evolves else 1)
   for dep in tech[n]:
    if pop[dep]<1:ensure(dep)
   goal=pop[n]+1;result.append((n,goal,base,mx,0));events.append({'unit':n,'target':goal,'producer':producer,'consumesProducer':evolves,'producerBefore':pop[producer]});pop[n]+=1
   if evolves:pop[producer]-=1
  visiting.remove(n)
 bootstrap=[('8472_mothership',1),('8472_passive',2),('8472_transmuter',1),('8472_active',2),('8472_collector',2),('8472_fluidicgate',1),('714const',1)]
 for n,count in bootstrap:ensure(n,count)
 for n,count,base,mx,level in desired:ensure(n,count,base,mx)
 assert len(result)<=200,(file.name,len(result))
 # Independent execution simulation: unlike the old graph audit, remove each evolved embryo.
 check=Counter(starts)
 for (n,count,base,mx,level),ev in zip(result,events):
  assert check[n]<count,(n,'redundant goal')
  assert all(check[x]>0 for x in tech[n]),(file.name,n,'technology')
  assert check[ev['producer']]>0 and ev['producer']in route(n),(file.name,n,'producer')
  if ev['consumesProducer']:check[ev['producer']]-=1
  check[n]+=1
 assert check==pop
 lines=src.splitlines();begin=next(i for i,s in enumerate(lines)if re.match(r'^\s*\{',s));end=next(i for i,s in enumerate(lines)if re.match(r'^\s*\};',s));body=['    // Preserve one spare embryo and replace every consumed evolution producer.']+['    "'+n+'", '+', '.join(map(str,(c,b,m,l)))+','for n,c,b,m,l in result];new='\n'.join(lines[:begin+1]+body+lines[end:])+'\n';pending[file.relative_to(root).as_posix()]=new;profiles.append({'file':file.name,'rows':len(result),'opening':result[:18],'evolutionEvents':sum(e['consumesProducer']for e in events),'independentConsumptiveAuditPassed':True,'finalEmbryos':{n:pop[n]for n in ['8472_active','8472_passive']},'events':events})
assert len(profiles)==5,len(profiles)
manifest=[]
for rel,t in pending.items():
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');out.write_bytes(data);manifest.append({'file':rel,'sourceSHA256':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'stagedSHA256':hashlib.sha256(data).hexdigest()})
r={'status':'staged only; not applied','stage':str(stage),'generated':datetime.datetime.now().astimezone().isoformat(),'flagsCorrected':changes,'aiProfiles':profiles,'startsPreserved':starts,'files':list(pending),'manifest':manifest,'runtimeVerified':False,'findings':['Active embryos are consumed by evolution; original AI requested a second collector before producing another active embryo.','The original graph audit retained consumed producers, so it missed evolution deadlocks.','Hatchery uses conventional714const but retained shipIsBuiltByEvolution=1.','Mine on the Passive Embryo lacked evolution routing; conventional Advanced Constructor defenses now have explicit conventional routing.'],'biomatterOnlyCostsPreserved':True,'otherFactionsChanged':False};(repo/'reports/8472-production-recovery-staged.json').write_text(json.dumps(r,indent=2));(stage/'manifest.json').write_text(json.dumps(r,indent=2));lines=['# Species8472 production recovery - staged','','Not applied to the live game. No starting-fleet, cost, artwork or other-faction changes.','','Fixes: replace consumed embryos before the next evolution; correct Advanced Hatchery/conventional defense construction routing; mark the Passive Embryo mine as evolution-built.','','All five AI plans pass a population simulation that consumes embryos, checks compatible producers and technology prerequisites, and retains spare embryos. This does not replace in-game testing.','','| AI plan | Rows | Evolution steps |','|---|---|---|']+['| '+x['file']+' | '+str(x['rows'])+' | '+str(x['evolutionEvents'])+' |'for x in profiles];(repo/'reports/8472-production-recovery-staged.md').write_text('\n'.join(lines),encoding='utf-8')
pf=repo/'status.json';s=json.loads(pf.read_text(encoding='utf-8-sig'));s['current']='STAGED ONLY:8472 production recovery,9 files. All5 AI plans now replenish embryos consumed by evolution and pass a consumptive-producer/tech audit. Corrected Hatchery and defense conventional-construction routing; restored Mine evolution routing. Original starting fleet and biomatter costs preserved. Live game unchanged; runtime test pending.';s['updated']=r['generated'];pf.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+'\n')
print(json.dumps({'stagedFiles':len(pending),'AIProfiles':{x['file']:x['rows']for x in profiles},'liveFilesChanged':False,'stage':str(stage)}))
