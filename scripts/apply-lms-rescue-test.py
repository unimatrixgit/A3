"""Install only the four reviewed prototype files into the closed lab game."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess

repo=Path('D:/aramada');root=Path('D:/ArmadaLab')
report_path=repo/'reports/lms-rescue-test-stage.json'
report=json.loads(report_path.read_text());stage=Path(report['stage'])
assert stage==root/'Development/next-rescue-test'
running=subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True)
assert int(running.strip())==0,'User must close the game before installation'
allowed={'bzn/lmstest.bzn','bzn/lmstest.bmp','missions/Last Man Standing Test.lua','objectives/LastManStandingObjectives.txt'}
assert {row['file']for row in report['files']}==allowed
for row in report['files']:
    assert hashlib.sha256((stage/row['file']).read_bytes()).hexdigest()==row['sha256'],row['file']
assert hashlib.sha256((root/'missions/mmm_loader.dll').read_bytes()).hexdigest()=='89ab2bd3782384fca5ea315f8d60b2ec50089ae0553bf048831708adc611ac69','Unexpected loader; do not reinstall diagnostic experiments'
assert (root/'odf/other/mmm_holder.odf').exists() and (root/'odf/other/mmm_mapper.odf').exists()
backup=root/'Development/backups'/('rescue-test-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
previous=[]
for row in report['files']:
    relative=row['file'];destination=root/relative
    if destination.exists():
        saved=backup/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(destination,saved)
        previous.append(relative)
for row in report['files']:
    relative=row['file'];destination=root/relative;destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(stage/relative,destination)
    assert hashlib.sha256(destination.read_bytes()).hexdigest()==row['sha256']
report.update(installed=True,backup=str(backup),previouslyPresent=previous)
report_path.write_text(json.dumps(report,indent=2))
print(json.dumps({'installedFiles':len(allowed),'target':str(root),'runtimeVerified':False}))
