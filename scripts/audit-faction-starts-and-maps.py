from pathlib import Path
import re,json
root=Path('D:/armadaIII');repo=Path('D:/aramada');idx={p.name.lower():p for p in(root/'odf').rglob('*.odf')};cache={}
def props(n,seen=None):
 n=n.lower();n=n if n.endswith('.odf')else n+'.odf'
 if n in cache:return cache[n]
 seen=set()if seen is None else seen
 if n in seen or n not in idx:return {}
 seen.add(n);t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',t):d.update(props(inc,set(seen)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 cache[n]=d;return d
results=[]
for race in ['borg','fed','kling','rom','card','species8472','dominion','bajoran','breen']:
 d=props(race);modes={}
 for mode in ['standard','minimal','super']:
  units=[v for k,v in d.items()if re.fullmatch(mode+r'units\d+',k)];heroes=[u for u in units if props(u).get('ishero')=='1'];modes[mode]={'units':units,'heroes':heroes,'heroCount':len(heroes)}
 results.append({'race':race,'starts':modes})
# Historical archive list is only a source list, not proof of current map compatibility.
old=json.loads((repo/'reports/eight-player-maps.json').read_text(encoding='utf-8-sig'));maps=[]
for x in old:
 if x.get('players')==8 and x.get('map'):
  p=root/'bzn'/x['map'];maps.append({'map':x['map'],'present':p.exists(),'bytes':p.stat().st_size if p.exists()else 0,'eightPlayerCountPreviouslyReported':True,'currentHeaderRechecked':False})
out={'target':str(root),'factions':results,'historicalEightPlayerMaps':maps,'runtimeVerified':False}
(repo/'reports/faction-start-and-map-inventory-live.json').write_text(json.dumps(out,indent=2));print(json.dumps({'standardHeroes':{x['race']:x['starts']['standard']['heroes']for x in results},'mapFilesPresent':sum(x['present']for x in maps),'mapFilesListed':len(maps)}))
