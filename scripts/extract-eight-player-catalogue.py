from pathlib import Path,PureWindowsPath
import json,zipfile,re,subprocess,hashlib
root=Path('D:/Xaramada-Modwork/eight-player-completion');r=json.loads((root/'downloads.json').read_text());results=[]
for x in r['downloads']:
 if 'archive'not in x:results.append(x);continue
 p=Path(x['archive']);dest=(root/'extracted'/p.stem).resolve();dest.mkdir(parents=True,exist_ok=True)
 try:
  if zipfile.is_zipfile(p):
   with zipfile.ZipFile(p)as z:
    for n in z.namelist():
     n=n.replace('\\','/');assert (dest/n).resolve().is_relative_to(dest)and not PureWindowsPath(n).drive
    assert sum(i.file_size for i in z.infolist())<500_000_000
    z.extractall(dest)
  else:
   listing=subprocess.run(['C:/Program Files/7-Zip/7z.exe','l','-slt',str(p)],capture_output=True,text=True)
   if listing.returncode:raise ValueError('Unrecognized archive or broken download')
   names=re.findall(r'(?m)^Path = (.*)$',listing.stdout)[1:]
   for n in names:assert (dest/n).resolve().is_relative_to(dest)and not PureWindowsPath(n).drive
   ex=subprocess.run(['C:/Program Files/7-Zip/7z.exe','x','-y','-o'+str(dest),str(p)],capture_output=True,text=True);assert ex.returncode==0
  x['extracted']=str(dest);x['maps']=[str(m)for m in dest.rglob('*')if m.suffix.lower()=='.bzn'];x['extraAssets']=[str(m.relative_to(dest))for m in dest.rglob('*')if m.is_file()and m.suffix.lower()in ['.odf','.sod','.tga','.spr','.dll','.exe']]
 except Exception as e:x['error']=str(e)
 results.append(x)
(root/'extraction.json').write_text(json.dumps(results,indent=2));print(json.dumps({'archives':len(results),'maps':sum(len(x.get('maps',[]))for x in results),'failed':[{'title':x['title'],'error':x['error']}for x in results if 'error'in x],'fleetOps':[x['title']for x in results if x.get('mentionsFleetOps')],'extraAssets':[x['title']for x in results if x.get('extraAssets')]}))
