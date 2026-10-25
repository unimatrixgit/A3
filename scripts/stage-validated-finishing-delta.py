"""Stage validated AI/yard updates and native-format results-screen portraits."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
master=stage;manifest=json.loads((master/'manifest.json').read_text());assert json.loads((master/'validation.json').read_text())['status']=='PASS';stage=repo/'patches/production-hero-ai-finish-20261025';dest=stage/'overlay';sourceHashes={}
for rel,h in manifest['files'].items():
 current=hashlib.sha256((root/rel).read_bytes()).hexdigest()
 if current==h:continue
 assert current==manifest['sourceHashes'][rel];path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((master/'overlay'/rel).read_bytes());sourceHashes[rel]=current
size=Image.open(root/'bitmaps/AdmiralsLog/ShipImages/fgalaxy.bmp').size
hero=Image.open(repo/'patches/tvarek-hero-20261025/tvarek-render.png').convert('RGB').resize(size);fighterSource=yard_unit_properties('xdcfighter',globals()).get('basename','xdcfighter').lower();fighter=preview(native(fighterSource),max(size)).convert('RGB').resize(size)
for n,im in [('xhftvarek',hero),('xdcfighter',fighter),('xdofighter',fighter)]:
 rel='bitmaps/AdmiralsLog/ShipImages/'+n+'.bmp'
 if(root/rel).exists():continue
 path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
report={'status':'PASS','description':'Applied final dependency-ordered AI plans, enlarged Archer Legacy Yard for T\'Varek, and results-screen portraits for the new hero and carrier fighters.','files':{p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},'sourceHashes':sourceHashes,'runtimeVerified':False};(stage/'patch.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':'PASS','files':len(report['files']),'portraitSize':size}))
