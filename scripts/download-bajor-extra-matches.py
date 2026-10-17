from pathlib import Path
import urllib.request,zipfile,json,hashlib
root=Path('D:/Xaramada-Modwork/armadafiles-bajor');sources=[('raider','http://armadafiles.com/files/armada-2/ships/other/bajoran-raider-with-hps/summary/download'),('station-v1','http://armadafiles.com/files/armada-2/stations/other/bajoran-starbase/summary/download')]
for name,u in sources:
 with urllib.request.urlopen(u,timeout=20)as r:b=r.read()
 p=root/(name+'.zip');p.write_bytes(b);dest=(root/(name+'-extracted')).resolve();dest.mkdir(exist_ok=True)
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():assert(dest/n).resolve().is_relative_to(dest)
  z.extractall(dest)
 print(name,'files',[(x.relative_to(dest).as_posix())for x in dest.rglob('*')if x.is_file()and x.suffix.lower()in['.tga','.sod']])
