"""Private causality test, NOT a release patch: retain script callback on load.

Pair with the loader interface-binding experiment. Always revert after testing:
skipping the stock callback reset globally is unsuitable for mixed missions.
"""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import struct
import subprocess
import sys

target = Path('D:/ArmadaLab/Armada2.exe')
report_path = Path('D:/aramada/reports/native-callback-reset-experiment.json')
running = subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', '-NoProfile', '-Command', '@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'], text=True)
assert int(running.strip()) == 0, 'Game must be closed'
expected = 'f9e283deb68506a779feceecac144d1c035f6e4fe79c636e5207437780fecb28'
if '--undo' in sys.argv:
    report = json.loads(report_path.read_text())
    backup = Path(report['backup'])
    assert hashlib.sha256(backup.read_bytes()).hexdigest() == expected
    assert hashlib.sha256(target.read_bytes()).hexdigest() == report['afterSha256']
    shutil.copy2(backup, target)
    report['reverted'] = True
else:
    data = bytearray(target.read_bytes())
    assert hashlib.sha256(data).hexdigest() == expected
    u16 = lambda o: struct.unpack_from('<H', data, o)[0]
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    nt = u32(60); optional = nt+24; base = u32(optional+28)
    table = optional+u16(nt+20); address = 0x45844e; offset = None
    for i in range(u16(nt+6)):
        s = table+40*i; va=u32(s+12); size=u32(s+16); raw=u32(s+20)
        if va <= address-base < va+size:
            offset=raw+address-base-va
    assert offset is not None
    assert data[offset:offset+10] == bytes.fromhex('6a 00 8b 01 ff 90 28 04 00 00')
    backup_dir=target.parent/'Development/backups'/('callback-reset-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup_dir.mkdir(parents=True);backup=backup_dir/target.name
    shutil.copy2(target,backup)
    data[offset:offset+10]=b'\x90'*10
    target.write_bytes(data)
    report={'target':str(target),'backup':str(backup),'beforeSha256':expected,
            'afterSha256':hashlib.sha256(data).hexdigest(),'experimental':True,
            'releaseSuitable':False,'runtimeVerified':False,'reverted':False}
report_path.write_text(json.dumps(report,indent=2))
print(json.dumps(report))
