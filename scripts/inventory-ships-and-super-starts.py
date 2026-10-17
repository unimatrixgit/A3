from pathlib import Path
import re,json,hashlib,csv
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
rows=[]
for name,p in idx.items():
 if p.parent.name.lower()!='ships':continue
 d=props(name);base=d.get('basename',p.stem);model=root/'SOD'/(base+'.sod');producers=[]
 for n in idx:
  if any(v.lower().removesuffix('.odf')==p.stem.lower()for k,v in props(n).items()if re.fullmatch(r'(?:secondary)?builditem\d+',k)):producers.append(n)
 rows.append({'unit':p.stem,'name':d.get('unitname',''),'race':d.get('race',''),'hero':d.get('ishero')=='1','class':d.get('shipclass',d.get('classlabel','')),'model':base,'modelPresent':model.exists(),'producers':'; '.join(producers),'shieldCapacity':d.get('maxhealth',''),'shieldRecharge':d.get('shieldrate','')})
p=repo/'reports/installed-ship-roster.csv'
with p.open('w',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
missing=[x for x in rows if x['producers']and not x['modelPresent']];(repo/'reports/installed-ship-roster-summary.json').write_text(json.dumps({'shipsInventoried':len(rows),'buildableShipDefinitions':sum(bool(x['producers'])for x in rows),'missingBuildableModels':missing,'scope':'Current installed ship definitions, not an exhaustive every-film/episode canon inventory.','runtimeVerified':False},indent=2));print(json.dumps({'ships':len(rows),'buildable':sum(bool(x['producers'])for x in rows),'missingModels':len(missing)}))
# Starting-hero generation disabled: user now requires buildable heroes only.
raise SystemExit(0)
# Historical implementation below retained only for reference.
stage=Path('D:/Xaramada-Modwork/super-start-heroes');files=[]
for race in ['borg','fed','kling','rom','card','species8472','dominion','breen']:
 d=props(race);standard=[v for k,v in d.items()if re.fullmatch(r'standardunits\d+',k)];heroes=[n for n in standard if props(n).get('ishero')=='1'];assert len(heroes)==1
 current=[v for k,v in d.items()if re.fullmatch(r'superunits\d+',k)];assert not any(props(n).get('ishero')=='1'for n in current)
 number=max([int(k[10:])for k in d if re.fullmatch(r'superunits\d+',k)]+[-1])+1;p=idx[race+'.odf'];t=p.read_text(encoding='latin1')+'\n// Faction hero also accompanies the alternate super starting fleet.\nsuperUnits'+str(number)+' = "'+heroes[0]+'"\n';rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'hero':heroes[0]})
(repo/'reports/super-start-heroes.json').write_text(json.dumps({'stage':str(stage),'target':str(root),'files':files,'applied':False,'runtimeVerified':False,'existingStartingUnitsPreserved':True},indent=2));print('Prepared eight alternate starting fleets with their own hero; Bajor already correct')
