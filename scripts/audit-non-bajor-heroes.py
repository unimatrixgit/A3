from pathlib import Path
import re,json,wave,collections
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
events=(root/'events.dat').read_text(encoding='latin1');blocks={m[1].lower():m[2]for m in re.finditer(r'(?ms)^([A-Za-z_][\w]*)[ \t]*\{(.*?)^\}',events)};audio={p.name.lower():p for p in(root/'sounds').rglob('*')if p.is_file()};rows=[];errors=[]
actions=['select','acknowledge','attack','stop','move','repair','redalert','yellowalert','greenalert','transport','selfdestruct','decommission']
for n,p in idx.items():
 if not p.parent.name.lower()=='ships' or n.startswith(('bj','xbj')):continue
 d=props(n)
 if d.get('ishero')!='1':continue
 checks=[]
 for a in actions:
  event=d.get('event'+a,'');block=blocks.get(event.lower(),'');clips=re.findall(r'(?mi)^[ \t]*Sound(?:[ \t]+<[^>]+>)?[ \t]+"([^"\r\n]+)"',block);missing=[x for x in clips if x.lower()not in audio]
  if not event or not block or not clips or missing:errors.append({'unit':n,'action':a,'event':event,'missingClips':missing,'eventPresent':bool(block),'clipCount':len(clips)})
  checks.append({'action':a,'event':event,'clips':clips,'missingClips':missing})
 rows.append({'unit':n,'name':d.get('unitname'),'race':d.get('race'),'commands':checks})
yards=[];tt=(root/'techtree/tech1.tt').read_text(encoding='latin1')
for y in ['fyard3','byard3','kyard3','ryard3','cyard3','dyard3','bryard3','xhs_yard3']:
 d=props(y);producers=[]
 for n in idx:
  if n.startswith(('bj','xbj')):continue
  if any(v.lower()==y for k,v in props(n).items()if re.fullmatch(r'(?:secondary)?builditem\d+',k)):producers.append(n)
 tech=re.findall(r'(?mi)^'+y+r'\.odf[^\r\n]*',tt);builds=[v for k,v in d.items()if re.fullmatch('builditem\d+',k)]
 yards.append({'yard':y,'name':d.get('unitname'),'producers':producers,'technology':tech,'builds':builds})
 if not producers or not tech:errors.append({'yard':y,'missingProducer':not producers,'missingTechnology':not tech})
out={'target':str(root),'scope':'Non-Bajoran hero command audio and hero-yard references; read only.','heroCount':len(rows),'heroes':rows,'yards':yards,'errors':errors,'runtimeVerified':False};(repo/'reports/non-bajor-hero-yard-voice-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'heroes':len(rows),'yards':len(yards),'issues':len(errors),'firstIssues':errors[:12]}))
