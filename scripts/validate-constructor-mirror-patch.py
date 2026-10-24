from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
report=json.loads((repo/'reports/constructor-mirror-patch.json').read_text());stage=Path(report['stage']);base=json.loads((repo/'reports/constructor-patch-before.json').read_text());old=json.loads((repo/'reports/mirror-ferengi-research.json').read_text());pending={rel:(stage/rel).read_text(encoding='latin1')for rel in report['files']if rel.lower().endswith('.odf')};sprite=(stage/'Sprites/gui_global.spr').read_text(encoding='latin1');errors=[];warnings=[]
def check(condition,message):
 if not condition:errors.append(message)
allunits=set(base)|{Path(rel).stem.lower()for rel in pending};changed={Path(rel).stem.lower():resolve(Path(rel).stem.lower())for rel in pending};models={};modelwarnings=[]
def model(n):
 if n in models:return models[n]
 path=stage/'SOD'/(n+'.sod')
 if not path.exists():path=root/'SOD'/(n+'.sod')
 try:
  try:m=load(path)
  except Exception:
   with contextlib.redirect_stdout(io.StringIO()):m=SodIO().read_file(str(path))
  models[n]=m;return m
 except Exception as e:errors.append('Model '+n+': '+str(e));return None
for n,d in changed.items():
 for k,v in d.items():
  if re.fullmatch('(secondary)?builditem[0-9]+|weapon[0-9]+|ordname',k):check(v.lower()in allunits,n+' missing '+k+' '+v)
 if d.get('classlabel','').lower()in ['constructionrig','evolver','shipyard','starbase','research','freighter','pod','p_mining','craft']or d.get('basename'):
  # Ordnance and weapons do not have a model baseName in this patch.
  if d.get('classlabel','').lower() in ['cannon','toggleweapon','resourceextractionbeam','minebm']:continue
  mn=d.get('basename',n).lower();m=model(mn)
  if m:
   nodes={z['id'].lower()for z in m.nodes}
   for k,v in d.items():
    if re.fullmatch('weaponhardpoints[0-9]+|podhardpoints|buildhardpoint',k):
     for hp in re.findall(r'[^"\s]+',v):
      if hp.lower()not in nodes and n in base and base[n].get(k)==v and base[n].get('basename',n).lower()==mn:warnings.append(n+': unchanged source hardpoint absent: '+hp+' ('+k+')')
      else:check(hp.lower()in nodes,n+' missing model hardpoint '+hp+' ('+k+')')
   for z in m.nodes:
    if z['type']!='MESH':continue
    tex=z['data'].get('texture','').lower()
    if tex and tex not in texidx and not (stage/'Textures/RGB'/(tex+'.tga')).exists():
     if tex=='damagesm':modelwarnings.append(n+': pre-existing damagesm texture reference')
     else:errors.append(n+' missing texture '+tex)
  check(bool(re.search(r'(?mi)^b_'+re.escape(n)+r'[ \t]+',sprite))or bool(re.search(r'(?mi)^b_'+re.escape(mn)+r'[ \t]+',sprite)),n+' missing build button')
for c in report['constructors']:
 n=c['unit'];d=changed[n];items=[v.lower()for k,v in d.items()if re.fullmatch('builditem[0-9]+',k)]
 check(len(items)<=13,n+' constructor menu overflow');check(set(items)==set(c['buildings']),n+' menu mismatch')
 for k,w in d.items():
  if re.fullmatch('weapon[0-9]+',k):check(d.get('race')=='borg'and w.lower()=='xabtrans5',n+' constructor has a combat weapon')
 check(d.get('basename')==n,n+' icon/model alias not unique')
for row in old['heroes']:
 d=changed[row['hero']];check(not any(re.fullmatch('mra[0-9]+',v,re.I)for k,v in d.items()if re.fullmatch('weapon[0-9]+',k)),row['hero']+' still summons')
 clone=changed[row['clone']];check(num(clone['maxhealth'])==num(base[row['clone']]['maxhealth']),row['clone']+' health changed');check(num(clone['scalesod'])==num(base[row['clone']]['scalesod']),row['clone']+' scale changed')
 check(all(clone.get(k)==v for k,v in base[row['clone']].items()if re.fullmatch('weapon[0-9]+',k)),row['clone']+' weapons changed')
for row in report['starbasePrices']:
 if row.get('biomatterRetained'):continue
 d=changed[row['unit']];check([num(d[k])for k in ['dilithiumcost','metalcost','crewcost']]==[1500,1500,150],row['unit']+' price mismatch');check(d.get('maximumcrew')==base[row['unit']].get('maximumcrew'),row['unit']+' max crew changed')
for rel in report['files']:
 if not rel.endswith('.tt'):continue
 t=(stage/rel).read_text(encoding='latin1');defs={};dupes=[]
 for line in t.splitlines():
  s=line.split('//')[0].strip().split()
  if len(s)<2 or not s[0].lower().endswith('.odf'):continue
  n=Path(s[0]).stem.lower()
  if n in defs:dupes.append(n)
  defs[n]=s[1:]
 for n,deps in report['techDefinitions'].items():
  expected=[]if Path(rel).stem=='fulltech'else deps;check(n in defs,rel+' missing '+n)
  if n in defs:check(defs[n]==[str(len(expected))]+[x+'.odf'for x in expected],rel+' wrong requirements '+n)
 for n in report['obsoleteDefinitions']:check(defs.get(n)==['-1'],rel+' obsolete node active '+n)
 check(not(set(dupes)&set(report['techDefinitions'])),rel+' duplicate changed tech definitions')
 # Explicit new dependencies must not cycle back to their own unit.
 def visit(n,path):
  if n in path:errors.append(rel+' technology cycle: '+' -> '.join(path+[n]));return
  parts=defs.get(n,[])
  if not parts or parts[0]=='-1':return
  for dep in parts[1:]:visit(Path(dep).stem.lower(),path+[n])
 for n in report['techDefinitions']:visit(n,[])
for ai in report['aiChanges']:
 t=(stage/'AI/AIPs'/ai['file']).read_text(encoding='latin1');seq=re.findall(r'(?m)^\s*"([^\"]+)"\s*,',t);seq=[s.lower()for s in seq]
 check(len(seq)<=200,ai['file']+' AI capacity')
 for n in ai['inserted']:
  check(n in allunits,ai['file']+' missing unit '+n)
  for dep in report['techDefinitions'].get(n,[]):check(dep in seq and seq.index(dep)<seq.index(n),ai['file']+' orders '+n+' before '+dep)
 if ai['file'].startswith('species8472_'):check(not any(n.startswith(('xfg','xbg'))or n=='mryfer'for n in seq),ai['file']+' Ferengi leak')
 if ai['file'].startswith('borg_'):check(not any(n.startswith('xfglat')or n.startswith('xfgplat')for n in seq),ai['file']+' Borg latinum research leak')
for n in report['icons']:
 matches=list(re.finditer(r'(?mi)^b_'+re.escape(n)+r'[ \t]+([^\r\n]+)',sprite));check(len(matches)==1,n+' duplicate/missing build icon')
 if matches:
  tex=matches[0][1].split()[0];check((stage/'Textures/RGB'/(tex+'.tga')).exists()or tex.lower()in texidx,n+' icon texture missing')
r={'errors':list(dict.fromkeys(errors)),'warnings':sorted(set(modelwarnings+warnings)),'changedODFs':len(changed),'modelsChecked':len(models),'mirrorShips':report['mirrorShips'],'mirrorYards':len(report['mirrorYards']),'constructors':len(report['constructors']),'aiPlans':len(report['aiChanges']),'buttons':len(report['icons']),'runtimeVerified':False}
(repo/'reports/constructor-mirror-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));raise SystemExit(bool(errors))
