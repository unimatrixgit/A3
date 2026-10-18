"""Prepare a private runtime test; never touches the installed mod or release overlay."""
from pathlib import Path
import struct, shutil, json

repo=Path('D:/aramada')
live=Path('D:/armadaIII')
sandbox=Path('D:/ArmadaLab')
assert sandbox.resolve()!=live.resolve() and (sandbox/'Armada2.exe').exists()
original=(live/'bzn/a2_fed01.bzn').read_bytes()
b=original
title=b'LMSProbe'
# Keep the original filename, native rules module and campaign menu layout.
old=b'MISSION_FED_1_MAIN_TITLE'
record=struct.pack('<IIIII',4,4,len(old),0,len(old))+old
assert b.count(record)==1
b=b.replace(record,struct.pack('<IIIII',4,4,len(title),0,len(title))+title)
o=b.index(b'EmptyMission')
first=b.find(struct.pack('<II',2,64),o,o+100)
assert first>=0
for field,value in [(first,b'mmm_loader.dll'),(first+144,title)]:
    assert struct.unpack_from('<I',b,field+4)[0]==64
    b=b[:field+8]+value.ljust(64,b'\0')+b[field+72:]
assert b'a2_fed01R.drl' in b
(sandbox/'bzn/a2_fed01.bzn').write_bytes(b)
shutil.copy2(live/'mshell.set',sandbox/'mshell.set')
shutil.copy2(live/'label.map',sandbox/'label.map')
loader=Path('D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm/missions/mmm_loader.dll')
shutil.copy2(loader,sandbox/'missions/mmm_loader.dll')
(sandbox/'missions/LMSProbe.lua').write_text("""class 'LMSProbe'
local function log(s)
 print(s)
 if io and io.open then
  local f=io.open('LMSProbe.log','a')
  if f then f:write(s..'\\n');f:close() end
 end
end
function LMSProbe:__init() self.checked=false end
function LMSProbe:setup() log('SETUP: Lua mission entry reached') end
function LMSProbe:update()
 if not self.checked then
  self.checked=true
  log('UPDATE: Lua mission tick reached')
 end
end
MMM.register(LMSProbe())
""")
report=dict(sandbox=str(sandbox),installedInLiveGame=False,gameplayVerified=False,
    selection='Federation campaign first mission in sandbox only',
    preservesNativeRules=True,preservesMissionMenu=True,
    purpose='Isolate loader initialization from added menu entries and blank rules links',
    evidence='LMSProbe.log must contain SETUP and UPDATE before success is claimed')
(repo/'reports/isolated-loader-test.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
