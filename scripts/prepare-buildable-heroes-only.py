from pathlib import Path
import re,json,hashlib
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
stage=Path('D:/Xaramada-Modwork/buildable-heroes-only');files=[];removed=[];producers={}
for n in idx:
 for k,v in props(n).items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower().removesuffix('.odf')+'.odf',[]).append(n)
for race in ['borg','fed','kling','rom','card','species8472','dominion','bajoran','breen']:
 p=idx[race+'.odf'];old=p.read_text(encoding='latin1');t=old;d=props(race)
 groups={m[1].lower():m[1] for m in re.finditer(r'(?mi)^[ \t]*(\w+Units)(\d+)[ \t]*=',old)}
 for lower,prefix in groups.items():
  entries=sorted([(int(k[len(lower):]),v)for k,v in d.items()if re.fullmatch(re.escape(lower)+r'\d+',k)])
  heroes=[v for i,v in entries if props(v).get('ishero')=='1']
  if not heroes:continue
  for hero in heroes:
   canonical=hero.lower().removesuffix('.odf')+'.odf';assert producers.get(canonical),(race,hero,'not buildable');removed.append({'race':race,'mode':prefix,'unit':hero,'retainedProducers':producers[canonical]})
  keep=[v for i,v in entries if v not in heroes];assert keep
  t=re.sub(r'(?mi)^[ \t]*'+re.escape(prefix)+r'\d+[ \t]*=[^\r\n]*(?:\r?\n)?','',t)
  t+='\n// Hero ships remain buildable; starting fleet contains ordinary units only.\n'+'\n'.join(prefix+str(j)+' = "'+v+'"'for j,v in enumerate(keep,min(i for i,v in entries)))+'\n'
 if t==old:continue
 rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
report={'target':str(root),'stage':str(stage),'files':files,'removedStartingHeroes':removed,'heroDefinitionsAndProductionUnchanged':True,'audioEventsUnchanged':True,'applied':False,'runtimeVerified':False};(repo/'reports/buildable-heroes-only.json').write_text(json.dumps(report,indent=2));print(json.dumps({'raceFiles':len(files),'startingHeroEntriesRemoved':len(removed),'allRemainBuildable':True}))
