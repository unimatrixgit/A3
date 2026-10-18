from pathlib import Path
import shutil,json,hashlib
src=Path('D:/armadaIII');dst=Path('D:/ArmadaLab');dst.mkdir(parents=True,exist_ok=True);folders=['AI','animations','bitmaps','bmp','cursors','misc','missions','objectives','odf','Shaders','SOD','sods','sounds','Sprites','techtree','Textures'];files=[]
for p in src.iterdir():
 if p.is_file()and p.name.lower()not in ['uninstall.exe','gw2_demo.exe']:
  q=dst/p.name
  if not q.exists():shutil.copy2(p,q);files.append(str(p.relative_to(src)))
for folder in folders:
 for p in(src/folder).rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(src);q=dst/rel
  if not q.exists():q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);files.append(str(rel))
for p in(src/'bzn').glob('a2_*'):
 if p.is_file():q=dst/'bzn'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q);files.append(str(p.relative_to(src)))
(dst/'save').mkdir(exist_ok=True)
report=dict(source=str(src),sandbox=str(dst),copiedFiles=len(files),copiedPaths=files,hardlinksUsed=False,liveGameModified=False,note='Private test copy contains installed commercial runtime;do not redistribute this sandbox.Only selected native campaign maps copied.');Path('D:/aramada/reports/last-man-standing-sandbox.json').write_text(json.dumps(report,indent=2));print('Independent sandbox prepared:',len(files),'copied files;live game unchanged.')
