"""Stage a fresh-match rescue test without changing a running game."""
from pathlib import Path
import hashlib
import json
import math
import re
import shutil
import struct
import uuid

repo=Path('D:/aramada');root=Path('D:/ArmadaLab')
stage=root/'Development/next-rescue-test'
mode=repo/'modes/last-man-standing'
source=root/'bzn/lmsprobe.bzn';data=source.read_bytes()
idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
objects=[]
for match in re.finditer(rb'[a-zA-Z_][a-zA-Z_0-9]{2,40}\x00',data):
    name=match.group()[:-1].decode().lower()
    if name not in idx:continue
    at=data.find(struct.pack('<II',9,12),match.end(),match.end()+100)
    if at<0:continue
    position=struct.unpack_from('<fff',data,at+8)
    if all(math.isfinite(f) and abs(f)<100000 for f in position):
        objects.append({'odf':name,'position':position})
assert len([o for o in objects if o['odf']=='mdmoon'])==9
sites=[]
for x,z in [(3000,800),(6000,800),(3000,8200),(6000,8200)]:
    distances={}
    for item in objects:
        name=item['odf'];p=item['position'];distance=math.hypot(x-p[0],z-p[2])
        distances[name]=min(distances.get(name,float('inf')),distance)
    assert 400<=x<=8600 and 400<=z<=8600
    assert 650<distances['mdmoon']<1800
    assert min(distances[n] for n in ['pb_clssm','pb_clssd','mafield2'])>1200
    sites.append({'x':x,'y':0,'z':z,'validated':True,'resourcesNearby':True,
                  'staticClearances':{n:round(d) for n,d in distances.items()}})

def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+json.dumps(str(k))+']='+lua(v)for k,v in value.items())+'}'
    if isinstance(value,list):return '{'+','.join(lua(v)for v in value)+'}'
    if isinstance(value,str):return json.dumps(value)
    if isinstance(value,bool):return 'true' if value else 'false'
    return str(value)

scenario={'mapId':'lmstest.bzn','ready':True,'discoverOrigins':True,'origins':{},
          'sites':[{k:v for k,v in s.items()if k!='staticClearances'}for s in sites]}
assembled='-- Private fresh-match rescue prototype. Save/reload is not verified.\n'
for name in ['RescueCore.lua','RescueConfig.lua','NativeAdapter.lua','NativeDefinitions.lua']:
    assembled+='\n(function()\n'+(mode/name).read_text()+'\nend)();\n'
assembled+='\nLMSScenario='+lua(scenario)+'\n'
entry=(mode/'Last Man Standing.lua').read_text()
entry=re.sub(r"(?m)^include\('[^']+'\)\r?\n",'',entry)
assembled+=entry
title=b'Last Man Standing Test';filename=b'lmstest.bzn';oldtitle=b'LMS API Probe'
changes=[]
for i in range(len(data)-20):
    if data[i:i+8]!=struct.pack('<II',4,4):continue
    n,res,n2=struct.unpack_from('<III',data,i+8)
    if n!=n2 or res or n>256:continue
    value=data[i+20:i+20+n];replacement=None
    if value==oldtitle:replacement=title
    elif value.lower()==b'lmsprobe.bzn':replacement=filename
    elif value.rstrip(b'\0').startswith(b'{') and len(value.rstrip(b'\0'))==38:
        replacement=('{'+str(uuid.uuid4())+'}').encode()+(b'\0'if value.endswith(b'\0')else b'')
    if replacement is not None:
        changes.append((i,i+20+n,struct.pack('<IIIII',4,4,len(replacement),0,len(replacement))+replacement))
assert len(changes)>=4
for start,end,new in reversed(changes):data=data[:start]+new+data[end:]
at=data.index(b'EmptyMission');field=data.find(struct.pack('<II',2,64),at,at+100)
assert field>=0
for f,value in [(field,b'mmm_loader.dll'),(field+72,b''),(field+144,title)]:
    assert struct.unpack_from('<I',data,f+4)[0]==64
    data=data[:f+8]+value.ljust(64,b'\0')+data[f+72:]
files={'bzn/lmstest.bzn':data,'missions/Last Man Standing Test.lua':assembled.encode(),
       'objectives/LastManStandingObjectives.txt':b'LAST MAN STANDING - PRIVATE TEST\n\nEvery AI has one reserve task force. Destroy its last constructor while leaving at least one structure alive. A hero, nine escorts and a constructor should appear at another resource site.\n\nFirst test: one Easy Federation opponent, normal starting forces, no random placement. Keep fog off to observe the reserve fleet. Do not save/reload this prototype.\n\nA scattered fleet carries the last hope of rebuilding. Break its logistics, and its reserves must choose a new home.\n'}
for relative,content in files.items():
    p=stage/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
shutil.copy2(root/'bzn/lmsprobe.bmp',stage/'bzn/lmstest.bmp')
manifest=[]
for p in sorted(stage.rglob('*')):
    if p.is_file():manifest.append({'file':p.relative_to(stage).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'stage':str(stage),'target':str(root),'selection':'Instant Action > Last Man Standing Test',
        'installed':False,'runtimeVerified':False,'freshMatchesOnly':True,
        'firstTest':'One Easy Federation AI; leave its starbase intact, destroy every constructor',
        'staticSites':sites,'siteReview':'Quad preview and parsed object centers; formation/flight clearance still requires runtime observation',
        'sourceMapCredit':'Private derivative of Quad by TornMorbid, from existing user installation; not a redistribution license',
        'files':manifest}
(repo/'reports/lms-rescue-test-stage.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'stagedFiles':len(manifest),'sites':len(sites),'installed':False,'stage':str(stage)}))
