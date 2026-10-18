"""Install a local Instant Action probe in ArmadaLab; restore its campaign baseline."""
from pathlib import Path
import struct,uuid,shutil,json,subprocess,datetime
repo=Path('D:/aramada');root=Path('D:/ArmadaLab');source=Path('D:/armadaIII/bzn/+quad+.bzn')
result=subprocess.run(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command',"@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
assert int(result.stdout.strip())==0,'Close Armada2 before applying a test'
backup=root/'Development/backups'/('instant-action-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
shutil.copy2(root/'bzn/a2_fed01.bzn',backup/'a2_fed01.bzn')
shutil.copy2(root/'Development/source-snapshot/bzn/a2_fed01.bzn',root/'bzn/a2_fed01.bzn')
b=source.read_bytes();title=b'LMS API Probe';filename=b'lmsprobe.bzn'
o=b.index(b'EmptyMission');f=b.find(struct.pack('<II',2,64),o,o+100);assert f>=0
oldtitle=b[f+152:f+208].split(b'\0')[0]
changes=[]
for i in range(len(b)-20):
    if b[i:i+8]!=struct.pack('<II',4,4):continue
    n,res,n2=struct.unpack_from('<III',b,i+8)
    if n!=n2 or res!=0 or n>256:continue
    value=b[i+20:i+20+n];replacement=None
    if value==oldtitle:replacement=title
    elif value.lower()==source.name.lower().encode():replacement=filename
    elif value.rstrip(b'\0').startswith(b'{') and value.rstrip(b'\0').endswith(b'}') and len(value.rstrip(b'\0'))==38:
        replacement=('{'+str(uuid.uuid4())+'}').encode()+(b'\0' if value.endswith(b'\0') else b'')
    if replacement is not None:changes.append((i,i+20+n,struct.pack('<IIIII',4,4,len(replacement),0,len(replacement))+replacement))
assert len(changes)>=4
for start,end,new in reversed(changes):b=b[:start]+new+b[end:]
o=b.index(b'EmptyMission');f=b.find(struct.pack('<II',2,64),o,o+100)
for field,value in [(f,b'mmm_loader.dll'),(f+72,b''),(f+144,title)]:
    assert struct.unpack_from('<I',b,field+4)[0]==64
    b=b[:field+8]+value.ljust(64,b'\0')+b[field+72:]
(root/'bzn/lmsprobe.bzn').write_bytes(b)
shutil.copy2(source.with_suffix('.bmp'),root/'bzn/lmsprobe.bmp')
shutil.copy2(root/'missions/LMSAPIProbe.lua',root/'missions/LMS API Probe.lua')
report=dict(target=str(root),campaignRestored=True,map='lmsprobe.bzn',selection='Instant Action > LMS API Probe',loader='mmm_loader.dll',runtimeVerified=False,source=str(source),sourceCredit='Existing Quad map by TornMorbid; private test derivative only',backup=str(backup))
(repo/'reports/lms-instant-action-probe.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
