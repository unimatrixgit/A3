"""Stage the next engine probe without replacing files in the running test game."""
from pathlib import Path
import struct,json,shutil
root=Path('D:/ArmadaLab');repo=Path('D:/aramada')
dest=root/'Development/api-probe';(dest/'missions').mkdir(parents=True,exist_ok=True)
mode=repo/'modes/last-man-standing'
parts=[]
for name in ['RescueConfig.lua','NativeDefinitions.lua','NativeAdapter.lua']:
    parts.append('do local loadModule=function()\n'+(mode/name).read_text()+'\nend;loadModule() end\n')
parts.append((mode/'APIProbe.lua').read_text())
(dest/'missions/LMSAPIProbe.lua').write_text('\n'.join(parts))
# Derive from the original snapshot, retaining filename, rules and native menu.
original=root/'Development/source-snapshot/bzn/a2_fed01.bzn'
assert original.exists(),'An unchanged source map snapshot is required'
b=original.read_bytes()
oldMode=b'mission';newMode=b'mp-regular'
record=struct.pack('<IIIII',4,4,len(oldMode),0,len(oldMode))+oldMode
assert b.count(record)==1
b=b.replace(record,struct.pack('<IIIII',4,4,len(newMode),0,len(newMode))+newMode)
o=b.index(b'EmptyMission');first=b.find(struct.pack('<II',2,64),o,o+100);assert first>=0
old=b[first+144+8:first+144+72].split(b'\0')[0];title=b'LMSAPIProbe'
record=struct.pack('<IIIII',4,4,len(old),0,len(old))+old
assert b.count(record)==1
b=b.replace(record,struct.pack('<IIIII',4,4,len(title),0,len(title))+title)
rules=b'a2_fed01R.drl'
record=struct.pack('<IIIII',4,4,len(rules),0,len(rules))+rules
assert b.count(record)==1
b=b.replace(record,struct.pack('<IIIII',4,4,0,0,0))
o=b.index(b'EmptyMission');first=b.find(struct.pack('<II',2,64),o,o+100)
for field,value in [(first,b'mmm_loader.dll'),(first+72,b''),(first+144,title)]:
    b=b[:field+8]+value.ljust(64,b'\0')+b[field+72:]
(dest/'bzn').mkdir(exist_ok=True);(dest/'bzn/a2_fed01.bzn').write_bytes(b)
base=Path('D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm')
for name in ['mmm_holder.odf','mmm_mapper.odf']:
    p=dest/'odf/other'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/'odf/system'/name,p)
assert rules not in b
report=dict(stage=str(dest),applied=False,runtimeVerified=False,nativeRulesRemoved=True,headerMode='mp-regular',localCampaignSlot=True,probe='snapshot, one owned constructor spawn/removal, Save/Load stream round-trip',guard='Do not apply while Armada2 is running')
(repo/'reports/lms-api-probe.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
