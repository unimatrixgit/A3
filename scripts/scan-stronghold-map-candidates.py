from pathlib import Path
import re,json,collections
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
results=[]
for p in(root/'bzn').glob('a2_*.txt'):
 counts=collections.Counter();ships=collections.Counter();examples=collections.defaultdict(list)
 for model in re.findall(r'//\s*Handle for .*?\(([^)]+)\) object ',p.read_text(encoding='latin1'),re.I):
  a=props(model)
  if not a:continue
  race=a.get('race','unknown');odf=idx.get(model.lower()+'.odf');category=odf.parent.name.lower()if odf else''
  if category=='stations':counts[race]+=1;examples[race].append(model)
  elif category=='ships':ships[race]+=1
 results.append(dict(map=p.stem,stationCounts=dict(counts),shipCounts=dict(ships),stationTypes={k:sorted(set(v))for k,v in examples.items()},ownershipVerified=False))
results.sort(key=lambda x:sum(x['stationCounts'].values()),reverse=True);(repo/'reports/stronghold-campaign-map-scan.json').write_text(json.dumps(dict(maps=results,notes=['Counts from map editor handle declarations matched against installed ODFs.','Race is original unit faction,not team ownership. Player ownership,coordinates and traversability require binary map validation.','Campaign scripting may depend on preplaced named objects;maps must be copied for mode prototypes.']),indent=2));print(json.dumps(results[:4],indent=2))
mode=repo/'modes/last-man-standing';mode.mkdir(parents=True,exist_ok=True);(repo/'modes/game-modes.json').write_text(json.dumps(dict(localOnly=True,totalModes=6,modes=[dict(id='last-man-standing',name='Last Man Standing',rule='Once per AI per match,last constructor lost while structures remain triggers hero+9escorts+constructor at another valid location with rebuilding grant.',status='loader compatibility investigation'),dict(id='stronghold',name='Stronghold',rule='Completed base,all standard facilities,basic fleet;normal expansion and victory.',status='campaign map candidates under review'),dict(id='siege',name='Siege',rule='Defend fortified base against escalating AI attack waves.',status='planned'),dict(id='border-war',name='Border War',rule='Small starting outposts and light fleets;research unlocks capital ships.',status='planned'),dict(id='hero-command',name='Hero Command',rule='One faction hero and escorts;hero survival is a defeat condition.',status='planned'),dict(id='king-of-the-wormhole',name='King of the Wormhole',rule='Control a central objective to accumulate victory points.',status='planned')],notes=['Design manifest only;not installed/playable menu options.','Stronghold means standard structures,not every mutually exclusive or unique special station.']),indent=2));print('Saved exactly6 local game-mode designs.')
