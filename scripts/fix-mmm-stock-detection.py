"""Correct MMM 1.0.1 GetModuleHandleW null detection in the private test copy."""
from pathlib import Path
import struct,hashlib,json,datetime,shutil,subprocess
root=Path('D:/ArmadaLab')
count=subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command',"@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count"],text=True)
assert int(count.strip())==0,'Close Armada2 first'
p=root/'missions/mmm_loader.dll';b=p.read_bytes();before=hashlib.sha256(b).hexdigest()
nt=struct.unpack_from('<I',b,60)[0];sec=nt+24+struct.unpack_from('<H',b,nt+20)[0]
offset=None
for i in range(struct.unpack_from('<H',b,nt+6)[0]):
    size,va,rawsize,raw=struct.unpack_from('<IIII',b,sec+40*i+8)
    if va<=0x21ac<va+max(size,rawsize):offset=raw+0x21ac-va
assert offset is not None
assert b[offset:offset+6] in [bytes.fromhex('83f8ff0f95c0'),bytes.fromhex('83f8000f95c0')],'Unexpected loader build: refusing patch'
if b[offset+2]==0:
    print('Stock detection already corrected');raise SystemExit(0)
backup=root/'Development/backups'/('mmm-stock-check-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True);shutil.copy2(p,backup/p.name)
patched=b[:offset+2]+b'\0'+b[offset+3:];p.write_bytes(patched)
report=dict(target=str(p),backup=str(backup),beforeSha256=before,afterSha256=hashlib.sha256(patched).hexdigest(),fileOffset=hex(offset+2),original='cmp eax,-1; setne al',corrected='cmp eax,0; setne al',reason='GetModuleHandleW returns NULL when FleetOpsHook.dll is absent, not INVALID_HANDLE_VALUE; original comparison enables incompatible extended interface calls',crashEvidence='Armada2.exe.16356.dmp: invalid call at MMM RVA0x287e through ScriptInterface offset0x5cc',runtimeVerified=False,sources=['https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlew','https://www.fleetops.net/news/item/204-megadroids-mission-mod-101'],redistribution='Private test patch only; no loader binary added to Git')
Path('D:/aramada/reports/mmm-stock-detection-fix.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
