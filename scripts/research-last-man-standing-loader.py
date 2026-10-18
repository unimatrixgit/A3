from pathlib import Path
import urllib.request,json,zipfile
out=Path('D:/Xaramada-Modwork/last-man-standing/research');out.mkdir(parents=True,exist_ok=True);results=[]
for name,url in [('mmm.zip','http://guide.fleetops.net/downloads/mmm_1_0_1.zip'),('getting-started.html','http://guide.fleetops.net/guide/modding/units/megadroid-mission-mod/tutorials/gettingstarted')]:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'});b=urllib.request.urlopen(req,timeout=25).read();(out/name).write_bytes(b);results.append(dict(file=name,bytes=len(b),url=url))
 except Exception as e:results.append(dict(file=name,error=str(e),url=url))
print(json.dumps(results));z=out/'mmm.zip'
if z.exists()and zipfile.is_zipfile(z):
 with zipfile.ZipFile(z)as archive:
  names=archive.namelist();print('\n'.join(names[:65]));base=(out/'mmm-extracted').resolve()
  for item in archive.infolist():
   assert (base/item.filename).resolve().is_relative_to(base)
  archive.extractall(base)
(out/'download-report.json').write_text(json.dumps(results,indent=2))

