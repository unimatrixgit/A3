"""Stage the approved framework with independent repair and light production berths."""
from pathlib import Path
script=Path('D:/aramada/scripts/stage-federation-service-v4.py').read_text()
script=script.replace('federation-service-v4-20261026','federation-dual-purpose-dock-20261026')
# The renderer stays the approved V4 framework; only the build berth moves right.
script=script.replace("exec(compile(script,__file__,'exec'))", "script=script.replace(\"for hp in ['tylaunch','tyrepair']:\",\"for hp in ['tylaunch','tyrepair']:\\n   pos=(np.array([1.03 if hp=='tylaunch'else -1.03,.12,0])-center)/span*size\")\nexec(compile(script,__file__,'exec'))")
exec(compile(script,__file__,'exec'))
import hashlib,subprocess
ships=['fscout','fdestroy2','fdestroy'];master=repo/'patches/twin-yards-20261025'
def write(rel,text):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.replace('\r','').replace('\n','\r\n').encode('latin1'))
t=(root/'odf/stations/xyr_f.odf').read_text(encoding='latin1');t=put(t,'builder_ship',1)
for i,n in enumerate(ships):t=put(t,'buildItem'+str(i),'"'+n+'"')
t=put(t,'verboseTooltip','"Starbase 74 Service Dock\\nRepair, recrew, decommission; light ship production\\nStarfleet crews restore and launch light vessels."')
write('odf/stations/xyr_f.odf',t)
for yard in ['fyard','fyard2']:
 t=(root/('odf/stations/'+yard+'.odf')).read_text(encoding='latin1');items=re.findall(r'(?mi)^[ \t]*buildItem\d+[ \t]*=[ \t]*"([^"]+)"',t);items=[n for n in items if n not in ships];t=re.sub(r'(?mi)^[ \t]*buildItem\d+[ \t]*=[^\r\n]*','',t)
 for i,n in enumerate(items):t=put(t,'buildItem'+str(i),'"'+n+'"')
 write('odf/stations/'+yard+'.odf',t)
for path in(root/'techtree').glob('*.tt'):
 if path.name not in ['tech1.tt','fulltech.tt','earlytech.tt','nosci.tt','nospweap.tt','nosuper.tt']:continue
 t=path.read_text(encoding='latin1')
 for n in ships:
  match=re.search(r'(?mi)^'+n+r'\.odf[ \t]+(-?\d+)[^\r\n]*',t)
  if match and int(match[1])>=0:t=t[:match.start()]+n+'.odf '+('0'if path.stem=='fulltech'else'1 xyr_f.odf')+t[match.end():]
 write('techtree/'+path.name,t)
d=json.loads((master/'design.json').read_text());d['attackAssignments'].update({n:'xyr_f'for n in ships});d['extraAiTargets'].setdefault('federation',[]).extend(ships);(stage/'design.json').write_text(json.dumps(d,indent=2))
aiScript=(repo/'scripts/finish-twin-yard-ai.py').read_text().replace("stage=repo/'patches/twin-yards-20261025'","stage=repo/'patches/federation-dual-purpose-dock-20261026'")
exec(compile(aiScript,'dual-purpose-ai','exec'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={p.relative_to(O).as_posix():sha(p)for p in O.rglob('*')if p.is_file()};sourceHashes={r:sha(root/r)for r in files if(root/r).exists()}
patch={'status':'PASS','files':files,'sourceHashes':sourceHashes,'attackAssignments':{n:'xyr_f'for n in ships},'extraAiTargets':{'federation':ships},'description':'Staged Federation dual-purpose dock: repair berth left, Venture/Sabre/Defiant production berth right; no duplicate attack production.'};(stage/'patch.json').write_text(json.dumps(patch,indent=2))
assert P['xyr_f']['repairfacility']=='1'and P['xyr_f']['decommissionfacility']=='1'and P['xyr_f']['builder_ship']=='1'
for n in ships:assert producers[n]==['xyr_f'],(n,producers[n])
report={'status':'PASS','productionRoster':ships,'productionPoint':'tylaunch in right bay','repairPoint':'tyrepair in left bay','duplicateProduction':False,'aiProfiles':len(reports),'runtimeVerified':False,'applied':False};(stage/'dual-purpose-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
