from pathlib import Path
import zipfile
root=Path('D:/Xaramada-Modwork/armadafiles-bajor')
for name in ['ships','station']:
 d=(root/(name+'-extracted')).resolve();d.mkdir(exist_ok=True)
 with zipfile.ZipFile(root/(name+'-download-response'))as z:
  for n in z.namelist():
   p=(d/n).resolve()
   assert p.is_relative_to(d)
  z.extractall(d)
 print(name)
 for p in d.rglob('*'):
  if p.is_file():print(p.relative_to(d))
