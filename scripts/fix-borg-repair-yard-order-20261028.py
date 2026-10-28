from pathlib import Path
import re,json,datetime,shutil,subprocess
root=Path('D:/armadaIII');repo=Path('D:/aramada');assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close Armada III before patching.'
backup=Path('D:/Xaramada-Modwork/backups')/('borg-ai-repair-order-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rows=[]
for p in sorted((root/'AI/AIPs').glob('borg_*list.aip')):
 t=p.read_text(encoding='latin1');lines=t.splitlines();before=list(lines);yard=[(i,line)for i,line in enumerate(lines)if re.match(r'\s*"xyr_b"\s*,',line)];drone=[i for i,line in enumerate(lines)if re.match(r'\s*"xbrepair"\s*,',line)];assert len(yard)==1 and len(drone)==1
 old=yard[0][0];line=yard[0][1];lines.pop(old);new=next(i for i,l in enumerate(lines)if re.match(r'\s*"xbrepair"\s*,',l));lines.insert(new,line)
 assert sorted(before)==sorted(lines)
 rel=p.relative_to(root);b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=('\r\n'.join(lines)+'\r\n').encode('latin1');p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 rows.append({'profile':p.name,'moved':'xyr_b','previousLine':old+1,'newLine':new+1,'before':'xbrepair','allOtherEntriesPreserved':True})
(repo/'reports/borg-ai-sequence-fix-20261028.json').write_text(json.dumps({'backup':str(backup),'changes':rows,'reason':'Repair-drone tech now requires repair yard; yard was listed near the end of each build plan.','runtimeVerified':False},indent=2));print('Updated',len(rows),'Borg profiles.')
