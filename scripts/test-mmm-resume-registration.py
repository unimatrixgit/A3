"""Private experiment: initialize the loader at interface binding on stock saves.

Does not distribute or patch the main game. --undo restores the known stock-check
loader from this experiment's backup. Gameplay verification is still required.
"""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import sys

target = Path('D:/ArmadaLab/missions/mmm_loader.dll')
repo = Path('D:/aramada')
report_path = repo / 'reports/mmm-resume-registration-experiment.json'
shell = 'C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
running = subprocess.check_output([shell, '-NoProfile', '-Command', '@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'], text=True)
assert int(running.strip()) == 0, 'Close the game before replacing its loader'
expected = '89ab2bd3782384fca5ea315f8d60b2ec50089ae0553bf048831708adc611ac69'
if '--undo' in sys.argv:
    report = json.loads(report_path.read_text())
    backup = Path(report['backup'])
    assert hashlib.sha256(backup.read_bytes()).hexdigest() == expected
    assert hashlib.sha256(target.read_bytes()).hexdigest() == report['afterSha256']
    shutil.copy2(backup, target)
    report['reverted'] = True
else:
    data = bytearray(target.read_bytes())
    assert hashlib.sha256(data).hexdigest() == expected, 'Unexpected loader version'
    # RVA 0x20d0 is file offset 0x14d0. Preserve the existing profile guard,
    # interface store and ABI. Call ScriptInit before returning interface v0x33.
    assert data[0x14e4:0x14e6] == bytes.fromhex('75 09')
    assert data[0x14ef:0x14fb] == bytes.fromhex('5d c3 cc cc cc cc cc cc cc cc cc cc')
    data[0x14e5] = 0x0e
    data[0x14ef:0x14fb] = bytes.fromhex('e8 0c 00 00 00 b8 33 00 00 00 5d c3')
    backup_dir = target.parent.parent / 'Development/backups' / ('resume-registration-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup_dir.mkdir(parents=True)
    backup = backup_dir / target.name
    shutil.copy2(target, backup)
    target.write_bytes(data)
    report = {'target': str(target), 'backup': str(backup),
              'beforeSha256': expected, 'afterSha256': hashlib.sha256(data).hexdigest(),
              'experimental': True, 'runtimeVerified': False, 'reverted': False,
              'reason': 'Stock saved loads bind the interface but skip AiMission ScriptInit'}
report_path.write_text(json.dumps(report, indent=2))
print(json.dumps(report))
