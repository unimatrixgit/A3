"""Install the prepared API diagnostic only into ArmadaLab, with a closed-game guard."""
from pathlib import Path
import subprocess,json,shutil,hashlib,datetime
root=Path('D:/ArmadaLab').resolve()
assert str(root).lower()=='d:\\armadalab'
running=subprocess.run(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command',
    "@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
if int(running.stdout.strip()):raise SystemExit('No files applied: close the running game before installing this probe.')
stage=root/'Development/api-probe'
files=[Path(x) for x in ['missions/LMSAPIProbe.lua','bzn/a2_fed01.bzn','odf/other/mmm_holder.odf','odf/other/mmm_mapper.odf']]
assert all((stage/p).is_file() for p in files)
backup=root/'Development/backups'/('api-probe-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
manifest=[]
for rel in files:
    src=stage/rel;dst=root/rel
    assert dst.resolve().is_relative_to(root)
    existed=dst.exists()
    if existed:
        saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,saved)
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    manifest.append(dict(file=rel.as_posix(),existed=existed,sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
backup.mkdir(parents=True,exist_ok=True)
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
report=Path('D:/aramada/reports/lms-api-probe.json');r=json.loads(report.read_text());r.update(applied=True,backup=str(backup));report.write_text(json.dumps(r,indent=2))
print('Applied API probe to D:/ArmadaLab only.')
