from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import shutil,subprocess,os,hashlib,collections
pending={}; before=json.loads((repo/'reports/yard-rebalance-before.json').read_text()); inventory=json.loads((repo/'reports/yard-rebalance-inventory.json').read_text()); yardids={x['id'] for x in inventory}; retired={}; changed={}
def items(n):
 d=resolve(n); return [d[k].lower() for k in sorted((k for k in d if re.fullmatch('builditem[0-9]+',k)),key=lambda k:int(k[9:]))]
def unique(xs):return list(dict.fromkeys(xs))
def save(n,t):pending[index[n].relative_to(root).as_posix()]=t
original={n:items(n) for n in index}
def menu(n,xs):
 xs=unique(xs); assert len(xs)<=14,(n,len(xs)); t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',text(n))
 for i,v in enumerate(xs):t=put(t,'buildItem'+str(i),q(v))
 save(n,t);changed[n]=xs

def retire(n,replacement):retired[n]=replacement
# Consolidate sparse production facilities; keep distinctive utility facilities.
menu('fyard',original['fyard0']+original['fyard'][:8]); menu('fyard2',original['fyard2']+original['fyard'][8:]);retire('fyard0','fyard')
menu('bryard',sum((original[n] for n in ['bryard','bryard2','bryard3','mrybreen']),[]))
for n in ['bryard2','bryard3','mrybreen']:retire(n,'bryard')
menu('bjyard2',original['bjyard2']+original['bjyard3']+original['mrybajor'])
for n in ['bjyard3','mrybajor']:retire(n,'bjyard2')
menu('byard2',original['byard2']+original['byard3'][:3]);menu('byard3',[n for n in original['byard3'] if n not in items('byard2')]+original['mryborg']);retire('mryborg','byard3')
menu('cyard2',original['cyard2']+original['cobyard'][:2]);menu('cyard3',original['cyard3']+original['cobyard'][2:]+original['mrycard'])
menu('cyard2',items('cyard2')+original['domyard'][:6]);menu('cyard3',items('cyard3')+original['domyard'][6:])
for n in ['cobyard','mrycard']:retire(n,'cyard3')
retire('domyard','cyard2')
menu('dyard2',original['dyard2']+['dbattle2','xdcarrier','dsuper']);menu('dyard3',[n for n in original['dyard3'] if n not in items('dyard2')]+original['mrydom'])
menu('dyard',original['dyard']+['dfrigate','dbattle','dspecial','dbattle2','xdcarrier']);menu('dyard3',items('dyard3')+['dweyoun','xdhattack','dsuper'])
for n in ['mrydom','dsuperbl','dyard2']:retire(n,'dyard3')
menu('kyard2',original['kyard2']+original['kimpyard'][:4]);menu('kyard3',original['kyard3']+original['kimpyard'][4:]+original['mrykling'])
for n in ['kimpyard','mrykling']:retire(n,'kyard3')
menu('ryard2',original['ryard2']+original['ryard3'][:5]);menu('ryard3',original['ryard3'][5:]+original['mryrom']);retire('mryrom','ryard3')
menu('xhs_yard3',original['xhs_yard3']+original['mry8472']);retire('mry8472','xhs_yard3')
menu('8472_fluidicgate',original['8472_fluidicgate']+original['714syard']);retire('714syard','8472_fluidicgate')
menu('xfgmerc',original['xfgmerc']+original['mryfer']);menu('xfgserv',[n for n in original['xfgserv'] if n!='xfgconst']);retire('mryfer','xfgmerc')
# Remove retired yards from all constructor and station menus. Compatibility ODFs remain.
for n in index:
 xs=items(n)
 if any(v in retired for v in xs):menu(n,[v for v in xs if v not in retired])
# Preserve dormant compatibility definitions byte-for-byte.
for n in retired:pending.pop(index[n].relative_to(root).as_posix(),None)
# Standardize construction prices/time by role, retaining native durability, crew and repair settings.
basic=['fyard','byard','kyard','ryard','cyard','dyard','bryard','bjyard']
advanced=['fyard2','byard2','kyard2','ryard2','cyard2','bjyard2']
elite=['fyard3','xflegacyyard','s31yard','byard3','kyard3','ryard3','cyard3','dyard3']
prices={}
for tier,ids,dil,metal,secs in [('basic',basic,250,750,45),('advanced',advanced,300,1000,90),('elite',elite,450,1350,120)]:
 for n in ids:
  t=text(n)
  for k,v in [('dilithiumCost',dil),('metalCost',metal),('buildTime',secs)]:t=put(t,k,v)
  save(n,t);prices[n]={'tier':tier,'dilithium':dil,'metal':metal,'seconds':secs}
# Rewrite all trees, expanding the prerequisites of a removed facility so research progression survives.
techreports={}
newowner={u:n for n,xs in changed.items() if n in yardids and n not in retired for u in xs}
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';source=(root/rel).read_text(encoding='latin1');defs={}
 for line in source.splitlines():
  a=line.split('//')[0].split()
  if len(a)>1 and a[0].lower().endswith('.odf'):defs[Path(a[0]).stem.lower()]=(int(a[1]),[Path(x).stem.lower() for x in a[2:2+max(0,int(a[1]))]])
 def expand(n,seen=()):
  if n not in retired:return [n]
  assert n not in seen,('retired dependency cycle',n)
  return unique([x for d in defs.get(n,(0,[]))[1] for x in expand(d,seen+(n,))])
 out=[];edits=[]
 for line in source.splitlines():
  a=line.split('//')[0].split()
  if len(a)>1 and a[0].lower().endswith('.odf'):
   n=Path(a[0]).stem.lower();count=int(a[1]);old=[Path(x).stem.lower() for x in a[2:2+max(0,count)]]
   if n in retired:continue
   if count>=0:
    deps=unique([x for d in old for x in expand(d) if x!=n])
    # The actual producing yard is also required, except technology-free modes.
    if n in newowner and count>0 and newowner[n]!=n and resolve(n).get('classlabel') not in ['constructionrig','evolver']:deps=unique(deps+[newowner[n]])
    if deps!=old:line=n+'.odf '+str(len(deps))+(' '+' '.join(x+'.odf' for x in deps) if deps else '');edits.append(n)
  out.append(line)
 out+=['','// Retired redundant yards; ships reassigned to retained facilities.']+[n+'.odf -1' for n in retired]
 pending[rel]='\n'.join(out)+'\n';techreports[tree]=edits
# AI: replace retired goals and recursively insert available producers/research in order.
tt={}
for line in pending['techtree/tech1.tt'].splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].endswith('.odf'):tt[Path(a[0]).stem.lower()]=None if int(a[1])<0 else [Path(v).stem.lower() for v in a[2:2+int(a[1])]]
producers=collections.defaultdict(list)
for n in index:
 if n in retired:continue
 for v in items(n):producers[v.lower()].append(n)
 for k,v in resolve(n).items():
  if re.fullmatch('secondarybuilditem[0-9]+',k):producers[v.lower()].append(n)
profiles=json.loads((repo/'reports/ai-start-recovery.json').read_text())['profiles'];cfg={'federation':'fed','klingon':'kling','romulan':'rom','cardassian':'card'};aiprofiles=[]
for profile in profiles:
 race=profile['race'];conf=resolve(cfg.get(race,race));starts={Path(v).stem.lower() for k,v in conf.items() if re.fullmatch('standardunits[0-9]+',k)};seen=set(starts);visiting=set();rows=[];goals={};rel='AI/AIPs/'+profile['file'];src=(root/rel).read_text(encoding='latin1')
 def allowed(n):
  r=resolve(n).get('race','').lower()
  return r==race or (race=='dominion' and r=='breen') or (r=='ferengi' and race in ['klingon','romulan','cardassian','dominion','breen','bajoran'])
 def ensure(n):
  if n in seen:return
  assert n not in visiting,('AI cycle',profile['file'],n,visiting)
  assert isinstance(tt.get(n),list),('missing/disabled tech',n)
  visiting.add(n)
  for dep in tt[n]:ensure(dep)
  choices=sorted((x for x in producers[n] if allowed(x)),key=lambda x:(x not in seen,len(tt.get(x)or[]),x))
  if not any(x in seen for x in choices):
   errors=[]
   for x in choices:
    snap=(set(seen),list(rows),dict(goals),set(visiting))
    try:ensure(x);break
    except AssertionError as e:errors.append(str(e));seen.clear();seen.update(snap[0]);rows[:]=snap[1];goals.clear();goals.update(snap[2]);visiting.clear();visiting.update(snap[3])
   else:raise AssertionError(('no producer',profile['file'],n,errors))
  visiting.remove(n);seen.add(n);rows.append((n,1,0,-1,0));goals[(n,0)]=1
 pat=r'(?m)^\s*"([^\"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,'
 for m in re.finditer(pat,src):
  n=m[1];n=retired.get(n,n);count,base,mx,level=[int(m[i]) for i in range(2,6)]
  ensure(n)
  if count>goals.get((n,base),0):rows.append((n,count,base,mx,level));goals[(n,base)]=count
 assert len(rows)<=200,(profile['file'],len(rows))
 lines=src.splitlines();begin=next(i for i,s in enumerate(lines) if re.match(r'^\s*\{',s));end=next(i for i,s in enumerate(lines) if re.match(r'^\s*\};',s))
 pending[rel]='\n'.join(lines[:begin+1]+['    // Consolidated yards; prerequisites and producers precede every unit.']+['    "'+n+'", '+', '.join(map(str,(c,b,m,l)))+',' for n,c,b,m,l in rows]+lines[end:])+'\n'
 audit=set(starts)
 for n,*_ in rows:
  if n not in audit:assert all(x in audit for x in tt[n]) and any(x in audit for x in producers[n]),(profile['file'],n)
  audit.add(n)
 aiprofiles.append({'file':profile['file'],'race':race,'rows':len(rows)})
# Every previously yard-produced ship remains offered, with no invisible slots or duplicate entries.
beforeunits={u for n in yardids for u in original[n]};afterunits={u for n in yardids-retired.keys() for u in items(n)};assert beforeunits<=afterunits,sorted(beforeunits-afterunits)
assert all(not any(v in retired for v in items(n)) for n in index)
buttons=[]
for n in changed:
 if n in retired:continue
 for u in items(n):
  d=resolve(u);model=d.get('basename',u)
  if not re.search(r'(?mi)^b_'+re.escape(u)+r'\s',sprite) and not re.search(r'(?mi)^b_'+re.escape(model)+r'\s',sprite):buttons.append((n,u,model))
assert not buttons,('missing button aliases',buttons)
# Reachability comparison catches tech cycles outside the AI's selected rosters.
def parse_tree(t):
 d={}
 for line in t.splitlines():
  a=line.split('//')[0].split()
  if len(a)>1 and a[0].lower().endswith('.odf'):d[Path(a[0]).stem.lower()]=None if int(a[1])<0 else [Path(x).stem.lower() for x in a[2:2+int(a[1])]]
 return d
def reachable(tree,menus):
 seen={Path(v).stem.lower() for conf in ['fed','borg','kling','rom','card','dominion','breen','bajoran','species8472'] for k,v in resolve(conf).items() if re.fullmatch('standardunits[0-9]+',k)}
 while True:
  add={u for n in seen for u in menus.get(n,[]) if isinstance(tree.get(u),list) and all(d in seen for d in tree[u])}
  if add<=seen:return seen
  seen.update(add)
oldmenus={n:unique(original[n]+[v.lower() for k,v in before[n].items() if re.fullmatch('secondarybuilditem[0-9]+',k)]) for n in index}
newmenus={n:unique(items(n)+[v.lower() for k,v in resolve(n).items() if re.fullmatch('secondarybuilditem[0-9]+',k)]) for n in index if n not in retired}
oldreachable=reachable(parse_tree((root/'techtree/tech1.tt').read_text(encoding='latin1')),oldmenus);newreachable=reachable(tt,newmenus)
lost=oldreachable-newreachable-set(retired)
assert not lost,('lost reachable units',sorted(lost))
# Stage first; applying requires a closed game and preserves backup copies.
stage=Path('D:/Xaramada-Modwork/yard-consolidation-stage');manifest=[]
for rel,t in pending.items():
 dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');dst.write_bytes(data);manifest.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
report={'applied':False,'stage':str(stage),'retired':retired,'rosters':{n:items(n) for n in sorted(yardids-retired.keys())},'changedMenus':changed,'prices':prices,'techChanges':techreports,'aiProfiles':aiprofiles,'preservedYardProducedUnits':len(beforeunits),'previouslyReachableUnits':len(oldreachable),'nowReachableUnits':len(newreachable),'lostReachableUnits':sorted(lost),'files':list(pending),'manifest':manifest,'runtimeVerified':False}
(repo/'reports/yard-consolidation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'retiredYards':len(retired),'preservedUnits':len(beforeunits),'files':len(pending),'AIProfiles':len(aiprofiles),'retainedRosters':{n:len(items(n)) for n in sorted(yardids-retired.keys())}},indent=2))
