from pathlib import Path
import json,re,collections,datetime,shutil,os,hashlib
root=Path('D:/armadaIII');repo=Path('D:/aramada');p=json.loads((repo/'reports/ai-recovery-before.json').read_text());idx={n:Path(d['file'])for n,d in p.items()};pending={};profiles=[];failures=[]
cfg={'federation':('fed','fconst','fconst2','fbase','fmining','ffreight','forbital','fyard','fdestroy'),'borg':('borg','bconst','bconst2','bbase','bmining','bfreight','bbase2','byard','bdestroy'),'klingon':('kling','kconst','kconst2','kbase','kmining','kfreight','korbital','kyard','kdestroy'),'romulan':('rom','rconst','rconst2','rbase','rmining','rfreight','rorbital','ryard','rdestroy'),'cardassian':('card','cconst','xcconst2','cbase','cmining','cfreight','corbital','cyard','cdestroy'),'dominion':('dominion','dconst','xdconst2','dbase','dmining','dfreight','dorbital','dyard','ddestroy'),'breen':('breen','brconst',None,'brbase','brmining','brfreight','brorbital','bryard','brdestroy'),'bajoran':('bajoran','bjconst','xbjconst2','bjbase','bjmining','bjfreight','bjorbital','bjyard','bjdestroy'),'species8472':('species8472','8472_passive','714const','8472_mothership','8472_transmuter','8472_collector',None,'8472_fluidicgate','8472_destroy')}
def put(t,k,v):return re.sub(r'(?mi)^\s*'+re.escape(k)+r'\s*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
starts={}
for race,(conf,basic,adv,base,*_)in cfg.items():
 units=[basic,basic]+([adv]if adv else[])+[base]
 if race=='dominion':units+=['brconst']
 if race=='bajoran':units+=['xfgconst']
 assert all(n in p for n in units)
 assert not any(p[n].get('ishero')=='1'for n in units)
 t=idx[conf].read_text(encoding='latin1');t=re.sub(r'(?mi)^\s*standardUnits\d+\s*=[^\r\n]*','',t)
 for i,n in enumerate(units,1):t=put(t,'standardUnits'+str(i),'"'+n+'.odf"')
 pending[idx[conf].relative_to(root).as_posix()]=t;starts[race]=units

# Production was consolidated, so old constructor aliases must not remain as
# mandatory research prerequisites after their production options disappear.
aliases={'domconst':'xcconst2','8472_defender':'714const','f31const':'fconst2','uconst':'xbuconst','xcdconst':'dconst','xcduniv':'xduconst','xbrconst2':'brconst','xbruconst':'brconst','xu3fer2':'xfgconst'}
techchanges=[]
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';lines=[]
 for line in(root/rel).read_text(encoding='latin1').splitlines():
  parts=line.split('//',1);tokens=parts[0].split()
  if len(tokens)>2 and tokens[0].lower().endswith('.odf')and int(tokens[1])>0:
   changed=False
   for i in range(2,len(tokens)):
    n=Path(tokens[i]).stem.lower()
    if n in aliases:tokens[i]=aliases[n]+'.odf';changed=True
   if changed:techchanges.append({'tree':tree,'unit':tokens[0],'requirements':tokens[2:]});line=' '.join(tokens)+(' //'+parts[1]if len(parts)>1 else'')
  lines.append(line)
 pending[rel]='\n'.join(lines)+'\n'
cfg['bajoran']=(*cfg['bajoran'][:-1],'bjinterceptor')

tt={};disabled=set()
for line in pending['techtree/tech1.tt'].splitlines():
 a=line.split('//')[0].split()
 if len(a)<2 or not a[0].lower().endswith('.odf'):continue
 n=Path(a[0]).stem.lower();count=int(a[1])
 if count<0:disabled.add(n);tt.pop(n,None)
 else:disabled.discard(n);tt[n]=[Path(x).stem.lower()for x in a[2:2+count]]
producers=collections.defaultdict(list)
for n,d in p.items():
 for k,v in d.items():
  if re.fullmatch('(secondary)?builditem[0-9]+',k):producers[Path(v).stem.lower()].append(n)
pattern=r'^\s*"([^\"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
eligible={'borg','klingon','romulan','cardassian','dominion','breen','bajoran'}
def allowed(n,race):
 if n in disabled:return False
 d=p.get(n,{});ur=d.get('race','').lower()
 if n in starts[race]:return True
 if ur==race:return True
 if race=='dominion'and ur=='breen':return True
 if ur=='ferengi'and race in eligible and race!='borg':return True
 if n=='xfgtrade'and race in eligible and race!='borg':return True
 return False

for f in(root/'AI/AIPs').glob('*.aip'):
 race=next((r for r in cfg if f.name.lower().startswith(r+'_')),None)
 if not race:continue
 t=f.read_text(encoding='latin1')
 if 'the_build_list'not in t:continue
 lines=t.splitlines();begin=next((i for i,s in enumerate(lines)if re.match(r'^\s*\{',s)),None);end=next((i for i,s in enumerate(lines)if re.match(r'^\s*\};',s)),None)
 if begin is None or end is None:continue
 desired=[(m[1].lower(),*[int(m[i])for i in range(2,6)])for s in lines[begin+1:end]if(m:=re.match(pattern,s))]
 avail=set(starts[race]);initial=collections.Counter(starts[race]);result=[];goals={};insertions=[];visiting=[];removed=[]
 def ensure(n):
  if n in avail:return
  if n in visiting:raise ValueError('cycle '+' -> '.join(visiting+[n]))
  if n not in p:raise ValueError('missing ODF '+n)
  if n not in tt or n in disabled:raise ValueError('disabled/missing technology '+n)
  visiting.append(n)
  try:
   for dep in tt[n]:ensure(dep)
   choices=[v for v in producers.get(n,[])if allowed(v,race)]
   if not any(v in avail for v in choices):
    choices.sort(key=lambda v:(v.startswith('mrc'),p[v].get('classlabel','').lower()in ['pod','evolver'],len(tt.get(v,[])),v))
    reasons=[]
    for producer in choices:
     oldavail=set(avail);oldlen=len(result);oldgoals=dict(goals);oldins=len(insertions)
     try:ensure(producer);break
     except ValueError as e:
      reasons.append(str(e));avail.clear();avail.update(oldavail);del result[oldlen:];goals.clear();goals.update(oldgoals);del insertions[oldins:]
    else:raise ValueError('no reachable producer for '+n+' ('+'; '.join(reasons[:2])+')')
   avail.add(n);result.append((n,1,0,-1,0));goals[(n,0)]=1;insertions.append(n)
  finally:visiting.pop()
 def request(n,count=1,base=0,maxbuild=-1):
  if count<=goals.get((n,base),0):return
  ensure(n)
  # ensure already emitted its first construction goal; only emit growth goals.
  if count>goals.get((n,base),0):result.append((n,count,base,maxbuild,0));goals[(n,base)]=count
 conf,basic,adv,base,mine,miner,orbital,yard,combat=cfg[race]
 bootstrap=[(base,1),(basic,2)]+([(adv,1)]if adv else[])
 if race=='dominion':bootstrap.append(('brconst',1))
 if race=='bajoran':bootstrap.append(('xfgconst',1))
 bootstrap+=[(mine,1),(miner,2)]+([(orbital,1)]if orbital else[])+[(yard,1),(combat,2)]
 try:
  for n,count in bootstrap:request(n,count)
  for n,count,basenum,maxbuild,level in desired:
   if n in disabled:removed.append({'unit':n,'reason':'retired/disabled technology'});continue
   request(n,count,basenum,maxbuild)
  if race=='dominion':
   # The extra starting constructor gets a complete Breen development branch.
   source=(root/'AI/AIPs/breen_instant_action_build_list.aip').read_text(encoding='latin1')
   for match in re.finditer(pattern,source,re.M):
    n=match[1].lower()
    if n not in disabled and p.get(n,{}).get('race')=='breen'and p[n].get('classlabel','').lower()!='constructionrig':request(n,int(match[2]),int(match[3]),int(match[4]))
 except ValueError as e:failures.append({'profile':f.name,'error':str(e),'unit':n});continue
 if len(result)>200:failures.append({'profile':f.name,'error':'AI capacity exceeded','rows':len(result)});continue
 # Independent sequential audit: every non-started goal needs its prerequisites
 # and a currently owned/scheduled producer, including economy and research pods.
 seen=set(starts[race]);audit=[]
 for i,(n,count,basenum,maxbuild,_)in enumerate(result):
  if n not in seen:
   missing=[v for v in tt.get(n,[])if v not in seen];owners=[v for v in producers.get(n,[])if v in seen]
   if missing or not owners or n not in tt:audit.append({'row':i,'unit':n,'missing':missing,'producer':owners})
  seen.add(n)
 if audit:failures.append({'profile':f.name,'error':'sequential dependency audit','details':audit});continue
 body=['    "'+n+'", '+str(count)+', '+str(basenum)+', '+str(maxbuild)+', 0,'for n,count,basenum,maxbuild,_ in result]
 new='\n'.join(lines[:begin+1]+['    // Economy first; every producer and research dependency precedes its unit.']+body+lines[end:])+'\n'
 new=re.sub(r'int\s+checkTechnologyAvailable\s*=\s*0\s*;','int checkTechnologyAvailable = 1;',new)
 pending[f.relative_to(root).as_posix()]=new;profiles.append({'file':f.name,'race':race,'rows':len(result),'opening':result[:16],'insertedPrerequisites':insertions,'removedDisabled':removed,'sequentialAuditErrors':audit})
stage=Path('D:/Xaramada-Modwork/ai-start-recovery-stage')
for rel,t in pending.items():out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
report={'stage':str(stage),'starts':starts,'files':list(pending),'profiles':profiles,'failures':failures,'techChanges':techchanges,'applied':False,'runtimeVerified':False};(repo/'reports/ai-start-recovery.json').write_text(json.dumps(report,indent=2));print(json.dumps({'profiles':len(profiles),'failures':failures,'rows':{x['file']:x['rows']for x in profiles}},indent=2));raise SystemExit(bool(failures))
