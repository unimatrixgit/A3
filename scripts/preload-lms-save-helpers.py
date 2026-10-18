"""Register the MMM save helpers for the separate test copy only."""
from pathlib import Path
import json,shutil,datetime,subprocess
root=Path('D:/ArmadaLab')
count=subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command',"@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count"],text=True)
assert int(count.strip())==0,'Close Armada2 first'
backup=root/'Development/backups'/('save-helpers-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
changed=[]
source=Path('D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm/odf/system')
for name in ['mmm_holder.odf','mmm_mapper.odf']:
    # Stock Armada II uses odf/other; odf/system is the Fleet Operations layout.
    target=root/'odf/other'/name
    if target.exists():shutil.copy2(target,backup/name)
    shutil.copy2(source/name,target)
    old=root/'odf/system'/name
    if old.exists():
        archived=backup/'system';archived.mkdir(exist_ok=True);shutil.move(str(old),str(archived/name))
for name in ['tech1.tt','freetech.tt','fulltech.tt']:
    p=root/'techtree'/name
    if not p.exists():continue
    text=p.read_text(encoding='latin1');new=text
    for odf in ['mmm_holder.odf','mmm_mapper.odf']:
        assert (root/'odf/other'/odf).is_file()
        if not any(line.split('//')[0].split()[:1]==[odf] for line in text.splitlines()):new+='\n'+odf+' 0\n'
    if new!=text:
        shutil.copy2(p,backup/name);p.write_text(new,encoding='latin1');changed.append(name)
print(json.dumps(dict(target=str(root),changed=changed,backup=str(backup),runtimeVerified=False)))
