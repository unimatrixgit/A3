from pathlib import Path
import urllib.request,zipfile,json
from concurrent.futures import ThreadPoolExecutor
jobs=[('luna','http://armadafiles.com/files/armada-2/ships/federation/tng-ds9-voy-and-future/luna-class-127/summary/download'),('rom-prebird','http://armadafiles.com/files/armada-2/ships/romulan/romulan-pre-bird-of-prey/summary/download'),('daedalus','http://armadafiles.com/files/armada-2/ships/federation/ent-tos-and-tmp/daedalus-class-by-fireball/summary/download')]
def fetch(job):
 key,url=job;p=Path('D:/Xaramada-Modwork/content-expansion')/key;p.mkdir(parents=True,exist_ok=True)
 try:
  b=urllib.request.urlopen(url,timeout=25).read();archive=p/'source.archive';archive.write_bytes(b)
  if zipfile.is_zipfile(archive):
   with zipfile.ZipFile(archive)as z:z.extractall(p/'extracted')
  return {'key':key,'url':url,'bytes':len(b),'magic':b[:4].hex(),'files':[str(x.relative_to(p))for x in p.rglob('*')if x.is_file()][:40]}
 except Exception as e:return {'key':key,'error':str(e)}
results=list(ThreadPoolExecutor(max_workers=3).map(fetch,jobs));Path('D:/aramada/reports/content-expansion-downloads.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
