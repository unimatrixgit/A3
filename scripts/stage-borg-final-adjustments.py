from pathlib import Path
import re,json
r=Path('D:/armadaIII');o=Path('D:/Xaramada-Modwork/borg-final-adjustments');files=[]
for rel in ['odf/ships/bscout.odf','odf/stations/bbase2.odf']:
 p=r/rel;t=p.read_text(encoding='latin1')
 if p.stem=='bscout':
  for k in ['crewCost','maximumCrew']:
   t=re.sub(r'^\s*'+k+r'\s*=.*$',k+' = 150',t,flags=re.M|re.I)if re.search(r'^\s*'+k+r'\s*=',t,re.M|re.I)else t+'\n'+k+' = 150\n'
 else:
  assert max(map(int,re.findall(r'^weapon(\d+)\s*=',t,re.M|re.I)))==7
  t+='\n// Additional orbital defense banks.\nweapon8 = "bb3phas"\nweaponHardpoints8 = "pod01" "pod02" "pod03" "pod04" "pod05"\nweapon9 = "bfphot"\nweaponHardpoints9 = "pod01" "pod02" "pod03" "pod04" "pod05"\n'
 dst=o/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(t,encoding='latin1');files.append(rel)
Path('D:/aramada/reports/borg-final-adjustments.json').write_text(json.dumps(dict(stage=str(o),files=files,installed=False,gameplayVerified=False),indent=2))
print('Staged Scout crew 150 and orbital beam/torpedo banks 8–9.')
