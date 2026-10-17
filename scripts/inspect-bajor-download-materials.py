from pathlib import Path
import json,sys,io,contextlib
from PIL import Image
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
root=Path('D:/Xaramada-Modwork/armadafiles-bajor');report=[]
for p in list((root/'ships-extracted').glob('*.sod'))+list((root/'station-extracted').rglob('bajbase.sod')):
 try:
  with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(p))
  meshes=[n['data']for n in m.nodes if n['type']=='MESH'];report.append({'model':p.name,'textures':sorted(set(x['texture']for x in meshes)),'meshCount':len(meshes),'vertices':sum(len(x['vertices'])for x in meshes)})
 except Exception as e:report.append({'model':p.name,'parseError':str(e)})
print(json.dumps(report,indent=2));(root/'source-materials.json').write_text(json.dumps(report,indent=2))
print('CURRENT');p=Path('D:/armadaIII/SOD/br3_bjassault.sod')
with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(p))
print(sorted({n['data']['texture']for n in m.nodes if n['type']=='MESH'}))
